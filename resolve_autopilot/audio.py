"""Pre-mix audio stems with ffmpeg: treated voice, music with ducking, SFX on the cuts.

Resolve's scripting API cannot set clip volume or keyframes, so the mix is built outside
and brought back as three stems (voice.wav, music.wav, sfx.wav, 48 kHz stereo).
The timeline is only read; source media is never modified.

ffmpeg is found via the FFMPEG environment variable, then PATH, then the optional
`imageio-ffmpeg` package.
"""
from __future__ import annotations

import array
import json
import math
import os
import shutil
import subprocess

from .connect import get_project, require_timeline


def find_ffmpeg() -> str:
    path = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if path:
        return path
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        raise SystemExit("ffmpeg not found. Install it, or set FFMPEG, or `pip install imageio-ffmpeg`.")


def run_ffmpeg(args: list[str]) -> None:
    result = subprocess.run([find_ffmpeg(), "-hide_banner", "-loglevel", "error", "-y"] + args,
                            capture_output=True)
    if result.returncode != 0:
        raise SystemExit("ffmpeg failed: " + " ".join(args)[:300] + "\n"
                         + (result.stderr or b"").decode("utf-8", "ignore"))


def measure(path: str) -> tuple[float, float]:
    """Return (integrated LUFS, true peak dBFS) of a file."""
    result = subprocess.run([find_ffmpeg(), "-hide_banner", "-nostats", "-i", path,
                             "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True)
    text = result.stderr.decode("utf-8", "ignore")
    i = text.rfind("I:")
    p = text.rfind("Peak:")
    return float(text[i + 2:].split("LUFS")[0]), float(text[p + 5:].split("dBFS")[0])


def peak_info(path: str, max_seconds: float = 8.0) -> tuple[float, float]:
    """(time of loudest sample in s, its level in dBFS) within the first `max_seconds`."""
    result = subprocess.run([find_ffmpeg(), "-hide_banner", "-loglevel", "error", "-i", path,
                             "-t", str(max_seconds), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                            capture_output=True)
    samples = array.array("f")
    samples.frombytes(result.stdout[: len(result.stdout) // 4 * 4])
    if not samples:
        return 0.0, -60.0
    loudest = max(range(len(samples)), key=lambda k: abs(samples[k]))
    return loudest / 16000.0, 20 * math.log10(max(abs(samples[loudest]), 1e-6))


# ---------------------------------------------------------------- reading the timeline

def read_segments(timeline_name: str) -> tuple[list[dict], float, float]:
    """Read video track 1 (read-only). Returns (segments, total seconds, fps)."""
    project = get_project()
    timeline = require_timeline(project, timeline_name)
    fps = float(timeline.GetSetting("timelineFrameRate"))
    start = timeline.GetStartFrame()
    audio_starts = set()
    for track in range(1, timeline.GetTrackCount("audio") + 1):
        for item in timeline.GetItemListInTrack("audio", track) or []:
            audio_starts.add(item.GetStart())
    segments = []
    for item in timeline.GetItemListInTrack("video", 1):
        media = item.GetMediaPoolItem()
        clip_fps = float(media.GetClipProperty("FPS"))
        segments.append({
            "file": media.GetClipProperty("File Path"),
            "source_start_s": item.GetSourceStartFrame() / clip_fps,
            "duration_s": item.GetDuration() / fps,
            "timeline_start_s": (item.GetStart() - start) / fps,
            "has_audio": item.GetStart() in audio_starts,
        })
    total = (timeline.GetEndFrame() - start + 1) / fps
    return segments, total, fps


# ---------------------------------------------------------------- stems

def build_voice(segments: list[dict], total_s: float, out_dir: str) -> str:
    """Rebuild the dialogue from the original files, then clean and level it."""
    parts = []
    for k, seg in enumerate(segments):
        part = os.path.join(out_dir, f"_seg{k:02d}.wav")
        if seg["has_audio"]:
            fade = min(0.01, seg["duration_s"] / 4)
            run_ffmpeg(["-ss", f"{seg['source_start_s']:.4f}", "-t", f"{seg['duration_s']:.4f}",
                        "-i", seg["file"], "-vn", "-af",
                        f"aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d={fade},"
                        f"afade=t=out:st={seg['duration_s'] - fade:.4f}:d={fade}", part])
        else:
            run_ffmpeg(["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                        "-t", f"{seg['duration_s']:.4f}", part])
        parts.append(part)
    concat_list = os.path.join(out_dir, "_list.txt")
    with open(concat_list, "w", encoding="utf-8") as handle:
        for part in parts:
            handle.write("file '" + part.replace("\\", "/") + "'\n")
    raw = os.path.join(out_dir, "_voice_raw.wav")
    run_ffmpeg(["-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", raw])
    voice = os.path.join(out_dir, "voice.wav")
    run_ffmpeg(["-i", raw, "-af",
                "highpass=f=75,afftdn=nr=10:nf=-32,equalizer=f=3000:t=q:w=1:g=2,"
                "acompressor=threshold=-21dB:ratio=3:attack=8:release=140:makeup=3,"
                f"loudnorm=I=-16:TP=-2:LRA=8,apad,atrim=0:{total_s:.4f}",
                "-ar", "48000", "-ac", "2", voice])
    return voice


def build_music(music: str, voice: str, total_s: float, out_dir: str) -> str:
    """Fit the music to the video and duck it under the voice (side-chain compression)."""
    fade_start = max(0.0, total_s - 1.5)
    out = os.path.join(out_dir, "music.wav")
    run_ffmpeg(["-i", music, "-i", voice, "-filter_complex",
                f"[0:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{total_s:.4f},"
                f"loudnorm=I=-21:TP=-3:LRA=11,afade=t=in:d=0.4,afade=t=out:st={fade_start:.4f}:d=1.5[m];"
                "[m][1:a]sidechaincompress=threshold=0.02:ratio=9:attack=15:release=450:makeup=1[d];"
                f"[d]apad,atrim=0:{total_s:.4f}[out]",
                "-map", "[out]", "-ar", "48000", "-ac", "2", out])
    return out


def plan_sfx(cut_times: list[float], segment_durations: list[float], sfx_files: list[str],
             min_segment_s: float = 1.0, level_db: float = -18.0,
             length_s: float = 0.9) -> list[tuple[str, float, float, float]]:
    """Decide where SFX go: one per cut, alternating `sfx_files`.

    `segment_durations[k]` is the duration of the clip that starts at `cut_times[k]`.
    Very short clips (flash cuts) get no effect. Returns (file, time_s, peak_dbfs, length_s).
    """
    if not sfx_files:
        return []
    events = []
    for n, (when, duration) in enumerate(zip(cut_times, segment_durations)):
        if duration < min_segment_s:
            continue
        events.append((sfx_files[len(events) % len(sfx_files)], when, level_db, length_s))
    return events


def build_sfx(events: list[tuple[str, float, float, float]], total_s: float, out_dir: str) -> str:
    """Mix the SFX so each sound's loudest moment lands exactly on its cut."""
    out = os.path.join(out_dir, "sfx.wav")
    if not events:
        run_ffmpeg(["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{total_s:.4f}", out])
        return out
    inputs, filters, labels = [], [], []
    for n, (path, when, target_peak, length) in enumerate(events):
        peak_t, peak_db = peak_info(path)
        gain = target_peak - peak_db
        start = max(0.0, peak_t - min(peak_t, length * 0.6))
        delay_ms = max(0, int((when - (peak_t - start)) * 1000))
        inputs += ["-ss", f"{start:.3f}", "-t", f"{length:.3f}", "-i", path]
        filters.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,volume={gain:.2f}dB,"
                       f"afade=t=in:d=0.02,afade=t=out:st={max(0.05, length - 0.25):.3f}:d=0.25,"
                       f"adelay={delay_ms}|{delay_ms}[s{n}]")
        labels.append(f"[s{n}]")
    mix = "".join(labels) + (f"amix=inputs={len(labels)}:normalize=0:duration=longest,"
                             f"apad,atrim=0:{total_s:.4f}[out]")
    run_ffmpeg(inputs + ["-filter_complex", ";".join(filters) + ";" + mix, "-map", "[out]",
                         "-ar", "48000", "-ac", "2", out])
    return out


def sum_stems(stems: list[str], out: str) -> None:
    inputs = []
    for stem in stems:
        inputs += ["-i", stem]
    run_ffmpeg(inputs + ["-filter_complex",
                         f"amix=inputs={len(stems)}:normalize=0:duration=longest", out])


def apply_gain(stem: str, gain_db: float) -> None:
    tmp = stem + ".tmp.wav"
    run_ffmpeg(["-i", stem, "-af", f"volume={gain_db:.2f}dB,alimiter=limit=0.89:level=disabled",
                "-ar", "48000", tmp])
    os.replace(tmp, stem)


def mix_timeline(timeline_name: str, music: str, out_dir: str, sfx_files: list[str] | None = None,
                 target_lufs: float = -14.0) -> dict:
    """Build voice.wav, music.wav and sfx.wav for a timeline and level the sum to `target_lufs`."""
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    segments, total_s, fps = read_segments(timeline_name)
    cuts = [s["timeline_start_s"] for s in segments[1:]]
    durations = [s["duration_s"] for s in segments[1:]]
    print(f"{len(segments)} segments, {total_s:.2f} s, {fps} fps; cuts at {[round(c, 2) for c in cuts]}")

    voice = build_voice(segments, total_s, out_dir)
    music_stem = build_music(music, voice, total_s, out_dir)
    events = plan_sfx(cuts, durations, sfx_files or [])
    sfx = build_sfx(events, total_s, out_dir)

    total = os.path.join(out_dir, "_sum.wav")
    stems = [voice, music_stem, sfx]
    sum_stems(stems, total)
    before, _ = measure(total)
    gain = max(-8.0, min(8.0, target_lufs - before))
    for stem in stems:
        apply_gain(stem, gain)
    sum_stems(stems, total)
    lufs, peak = measure(total)
    info = {"timeline": timeline_name, "music": music, "final_lufs": lufs, "final_peak_dbfs": peak,
            "cuts_s": cuts, "sfx": events, "total_s": total_s}
    with open(os.path.join(out_dir, "mix_info.json"), "w", encoding="utf-8") as handle:
        json.dump(info, handle, indent=1)
    print(f"Final mix: {lufs:.1f} LUFS, peak {peak:.1f} dBFS (target {target_lufs})")
    return info
