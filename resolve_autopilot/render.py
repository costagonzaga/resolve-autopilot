"""Render a timeline through Resolve's render queue and wait for it to finish."""
from __future__ import annotations

import os
import time

from .connect import get_project, require_timeline


def render_timeline(timeline_name: str, out_dir: str, file_name: str,
                    width: int | None = None, height: int | None = None) -> dict:
    """Render `timeline_name` as H.264 MP4 into `out_dir`. Does not change the timeline."""
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    project = get_project()
    timeline = require_timeline(project, timeline_name)
    project.SetCurrentTimeline(timeline)
    project.SetCurrentRenderFormatAndCodec("mp4", "H264")
    settings = {"SelectAllFrames": True, "TargetDir": out_dir, "CustomName": file_name,
                "ExportVideo": True, "ExportAudio": True, "AudioCodec": "aac", "AudioBitDepth": 16}
    if width and height:
        settings.update({"FormatWidth": int(width), "FormatHeight": int(height)})
    # One at a time: a single refused value must not silently drop the rest
    # (a refused ExportVideo once produced a render with no picture).
    for key, value in settings.items():
        if not project.SetRenderSettings({key: value}):
            print(f"[!] Resolve refused render setting {key}={value}")
    job = project.AddRenderJob()
    if not job:
        raise SystemExit("Could not add the render job.")
    project.StartRendering(job)
    while project.IsRenderingInProgress():
        status = project.GetRenderJobStatus(job)
        print(f"  {status.get('JobStatus')} {status.get('CompletionPercentage')}%", flush=True)
        time.sleep(3)
    final = project.GetRenderJobStatus(job)
    project.DeleteRenderJob(job)
    return final
