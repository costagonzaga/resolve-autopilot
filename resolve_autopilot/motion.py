"""Bridge to Remotion: render a transparent motion clip and place it on a Resolve timeline.

Division of labour: Resolve does the editing; Remotion draws the animated graphics
(it is far better at text and shapes); this module renders the graphic with the
timeline's own size and frame rate (ProRes 4444 with alpha) and lays it on a new
video track above V1. The original timeline is duplicated, never modified.

Requires Node.js 20+ and `npm install` inside the repository's `motion/` folder.
Set RESOLVE_AUTOPILOT_MOTION to use a different Remotion project.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile

from .connect import find_timeline, get_project

DEFAULT_MOTION_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "motion")


def motion_dir() -> str:
    path = os.environ.get("RESOLVE_AUTOPILOT_MOTION", DEFAULT_MOTION_DIR)
    if not os.path.isdir(os.path.join(path, "node_modules")):
        raise SystemExit(f"Remotion project not ready in {path}. Run `npm install` there (Node 20+ needed).")
    return path


def render_title(lead: str, highlight: str, duration_s: float, fps: float, width: int, height: int,
                 out_path: str) -> str:
    """Render the TitleHighlight template as a transparent ProRes 4444 .mov."""
    npx = shutil.which("npx")
    if not npx:
        raise SystemExit("npx not found. Install Node.js 20+.")
    props = {"lead": lead, "highlight": highlight, "durationSeconds": duration_s,
             "fps": fps, "width": width, "height": height}
    with tempfile.TemporaryDirectory() as tmp:
        props_file = os.path.join(tmp, "props.json")
        with open(props_file, "w", encoding="utf-8") as handle:
            json.dump(props, handle)
        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        result = subprocess.run(
            [npx, "remotion", "render", "src/index.ts", "TitleHighlight", os.path.abspath(out_path),
             "--codec=prores", "--prores-profile=4444", "--image-format=png",
             "--pixel-format=yuva444p10le", f"--props={props_file}", "--overwrite"],
            cwd=motion_dir(), capture_output=True, text=True)
    if result.returncode != 0 or not os.path.exists(out_path):
        raise SystemExit("Remotion render failed:\n" + (result.stderr or result.stdout)[-1500:])
    return out_path


def add_title(source_name: str, new_name: str, lead: str, highlight: str, at_s: float,
              duration_s: float, out_dir: str):
    """Duplicate `source_name` as `new_name` and place an animated title at `at_s` seconds."""
    project = get_project()
    source = find_timeline(project, source_name)
    if source is None:
        raise SystemExit(f"Timeline '{source_name}' does not exist.")
    if find_timeline(project, new_name):
        raise SystemExit(f"A timeline called '{new_name}' already exists.")
    fps = float(source.GetSetting("timelineFrameRate"))
    width = int(source.GetSetting("timelineResolutionWidth"))
    height = int(source.GetSetting("timelineResolutionHeight"))

    clip_path = os.path.join(os.path.abspath(out_dir), f"title_{highlight.lower()[:20]}.mov".replace(" ", "_"))
    render_title(lead, highlight, duration_s, fps, width, height, clip_path)

    project.SetCurrentTimeline(source)
    timeline = source.DuplicateTimeline(new_name)
    if timeline is None:
        raise SystemExit("Could not duplicate the timeline.")
    project.SetCurrentTimeline(timeline)

    pool = project.GetMediaPool()
    imported = pool.ImportMedia([clip_path])
    if not imported:
        raise SystemExit("Resolve refused to import the motion clip.")
    timeline.AddTrack("video")
    track = timeline.GetTrackCount("video")
    frames = int(round(duration_s * fps))
    record = timeline.GetStartFrame() + int(round(at_s * fps))
    placed = pool.AppendToTimeline([{
        "mediaPoolItem": imported[0], "mediaType": 1, "trackIndex": track,
        "recordFrame": record, "startFrame": 0, "endFrame": frames - 1,
    }])
    if not placed:
        raise SystemExit("Resolve did not place the motion clip on the timeline.")
    timeline.SetTrackName("video", track, "Motion (Remotion)")
    return timeline, {"clip": clip_path, "track": track, "record_frame": record, "frames": frames}
