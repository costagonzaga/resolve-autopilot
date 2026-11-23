"""Read-only report of the timelines in the open project (useful context for an AI assistant)."""
from __future__ import annotations

import json
import statistics

from .connect import find_timeline, get_project

PROPERTIES = ["Pan", "Tilt", "ZoomX", "ZoomY", "Opacity", "RotationAngle", "Volume",
              "CompositeMode", "RetimeProcess", "Speed"]


def _safe(call, default=None):
    try:
        value = call()
        return default if value is None else value
    except Exception:
        return default


def describe_timeline(timeline) -> dict:
    fps = float(_safe(lambda: timeline.GetSetting("timelineFrameRate"), 0) or 0)
    start = _safe(timeline.GetStartFrame, 0)
    clips = []
    for item in _safe(lambda: timeline.GetItemListInTrack("video", 1), []):
        duration = _safe(item.GetDuration, 0)
        clips.append({
            "name": _safe(item.GetName, ""),
            "start_s": round((_safe(item.GetStart, 0) - start) / fps, 3) if fps else None,
            "duration_s": round(duration / fps, 3) if fps else None,
            "properties": {p: v for p in PROPERTIES
                           if (v := _safe(lambda p=p: item.GetProperty(p))) is not None},
        })
    durations = [c["duration_s"] for c in clips if c["duration_s"]]
    return {
        "name": timeline.GetName(),
        "fps": fps,
        "video_tracks": timeline.GetTrackCount("video"),
        "audio_tracks": timeline.GetTrackCount("audio"),
        "markers": _safe(timeline.GetMarkers, {}),
        "clips": clips,
        "rhythm": {
            "clip_count": len(durations),
            "mean_clip_s": round(statistics.mean(durations), 2) if durations else None,
            "median_clip_s": round(statistics.median(durations), 2) if durations else None,
            "shortest_s": min(durations) if durations else None,
            "longest_s": max(durations) if durations else None,
        },
    }


def inspect_project(names: list[str] | None = None) -> dict:
    """Describe the named timelines, or all of them."""
    project = get_project()
    if names:
        timelines = [find_timeline(project, n) for n in names]
        timelines = [t for t in timelines if t is not None]
    else:
        timelines = [project.GetTimelineByIndex(i) for i in range(1, project.GetTimelineCount() + 1)]
    return {"project": project.GetName(), "timelines": [describe_timeline(t) for t in timelines]}


def main(names: list[str] | None = None) -> None:
    print(json.dumps(inspect_project(names), indent=2, ensure_ascii=False))
