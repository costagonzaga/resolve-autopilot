"""Build and restyle timelines. Source media is never modified or deleted."""
from __future__ import annotations

import os
from dataclasses import dataclass, field

from .connect import find_timeline, get_project

MEDIA_EXTENSIONS = {".mp4", ".mov", ".mxf", ".mkv", ".wav", ".mp3", ".jpg", ".png"}


def list_media(folder: str) -> list[str]:
    """Media files in `folder`, sorted by name (name your takes 01, 02, 03... to set the order)."""
    folder = os.path.abspath(folder)  # Resolve rejects paths that mix / and \
    return sorted(
        os.path.join(folder, name) for name in os.listdir(folder)
        if os.path.splitext(name)[1].lower() in MEDIA_EXTENSIONS
    )


def build_timeline(folder: str, name: str):
    """Import every media file in `folder` and create a timeline with the clips in name order."""
    project = get_project()
    if find_timeline(project, name):
        raise SystemExit(f"A timeline called '{name}' already exists. Pick another name.")
    files = list_media(folder)
    if not files:
        raise SystemExit(f"No media found in {folder}")
    pool = project.GetMediaPool()
    clips = pool.ImportMedia(files)
    if not clips:
        raise SystemExit("Resolve refused to import the files.")
    timeline = pool.CreateTimelineFromClips(name, clips)
    if timeline is None:
        raise SystemExit("Could not create the timeline.")
    return timeline


@dataclass
class Look:
    """A simple, repeatable look: alternating punch-in zoom plus a CDL colour grade."""
    zoom: float = 1.12
    slope: str = "1.05 1.01 0.96"
    offset: str = "-0.005 -0.005 -0.012"
    power: str = "1.04 1.04 1.04"
    saturation: str = "1.10"
    marker_cuts: bool = True
    log: dict = field(default_factory=dict)

    def cdl(self) -> dict:
        return {"NodeIndex": "1", "Slope": self.slope, "Offset": self.offset,
                "Power": self.power, "Saturation": self.saturation}


def apply_look(source_name: str, new_name: str, look: Look | None = None):
    """Duplicate `source_name` as `new_name` and apply the look on video track 1.

    The original timeline is left untouched. Every second clip gets a punch-in zoom,
    all clips get the CDL grade, and each cut gets a marker so you can see what changed.
    """
    look = look or Look()
    project = get_project()
    source = find_timeline(project, source_name)
    if source is None:
        raise SystemExit(f"Timeline '{source_name}' does not exist.")
    if find_timeline(project, new_name):
        raise SystemExit(f"A timeline called '{new_name}' already exists.")
    project.SetCurrentTimeline(source)
    timeline = source.DuplicateTimeline(new_name)
    if timeline is None:
        raise SystemExit("Could not duplicate the timeline.")
    project.SetCurrentTimeline(timeline)
    start = timeline.GetStartFrame()
    items = timeline.GetItemListInTrack("video", 1)
    report = []
    for index, item in enumerate(items):
        zoom = look.zoom if index % 2 else 1.0
        item.SetProperty("ZoomX", zoom)
        item.SetProperty("ZoomY", zoom)
        graded = bool(item.SetCDL(look.cdl()))
        report.append({"clip": item.GetName(), "zoom": zoom, "graded": graded})
        if look.marker_cuts:
            timeline.AddMarker(item.GetStart() - start, "Blue" if index % 2 == 0 else "Yellow",
                               f"cut {index + 1}", f"zoom {zoom:.2f}", 1)
    look.log = {"timeline": new_name, "source": source_name, "clips": report}
    return timeline, look.log


def add_audio_stems(timeline_name: str, folder: str, stems=("voice.wav", "music.wav", "sfx.wav"),
                    mute_original: bool = True):
    """Put pre-mixed stems on new audio tracks and (optionally) mute the original audio track.

    Nothing is deleted: the original track is only disabled and renamed.
    """
    project = get_project()
    timeline = find_timeline(project, timeline_name)
    if timeline is None:
        raise SystemExit(f"Timeline '{timeline_name}' does not exist.")
    paths = [os.path.join(folder, stem) for stem in stems]
    missing = [p for p in paths if not os.path.exists(p)]
    if missing:
        raise SystemExit("Missing stems: " + ", ".join(missing))
    pool = project.GetMediaPool()
    imported = pool.ImportMedia(paths)
    if not imported or len(imported) < len(stems):
        raise SystemExit("Importing the audio stems failed.")
    by_name = {item.GetName(): item for item in imported}
    start = timeline.GetStartFrame()
    total = timeline.GetEndFrame() - start + 1
    first_new = timeline.GetTrackCount("audio") + 1
    for _ in stems:
        timeline.AddTrack("audio", "stereo")
    for offset, stem in enumerate(stems):
        track = first_new + offset
        pool.AppendToTimeline([{
            "mediaPoolItem": by_name[stem], "mediaType": 2, "trackIndex": track,
            "recordFrame": start, "startFrame": 0, "endFrame": total - 1,
        }])
        timeline.SetTrackName("audio", track, os.path.splitext(stem)[0])
    if mute_original:
        timeline.SetTrackName("audio", 1, "Original (muted)")
        timeline.SetTrackEnable("audio", 1, False)
    return timeline
