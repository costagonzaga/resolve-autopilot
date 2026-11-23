---
name: resolve-autopilot
description: Edit videos in DaVinci Resolve Studio through the resolve-autopilot CLI: build a timeline from numbered takes, apply a look, pre-mix voice/music/SFX, and render. Use when asked to assemble or edit a video in Resolve.
---

# Resolve Autopilot

## Safety rules
- Never modify or delete source media. Work on a duplicate timeline; the original stays.
- Back up the project (`.drp`) before changing anything.
- Do not render or publish unless the user asked for it; leave the timeline ready for review.
- If something is ambiguous or outside the API, write the question in the log and take the safest option.

## Workflow
1. `resolve-autopilot check` (Resolve Studio must be open with a project).
2. `resolve-autopilot inspect` to read existing timelines and learn the rhythm (clip length, zoom, markers).
3. `resolve-autopilot build <takes_folder> <name>`: takes are ordered by file name (01, 02, ...).
4. Trim pauses and mistakes inside takes. Keep take order.
5. `resolve-autopilot look <name> <name v2>`.
6. `resolve-autopilot mix <name v2> <music> <audio_dir> --sfx ...` then `add-audio`.
7. Verify: re-run `inspect`, check the mix report (`mix_info.json`: final LUFS and peak).
8. Render only on request: `resolve-autopilot render ...`.

## Known limits
- The API cannot set clip volume or keyframes: audio is pre-mixed with ffmpeg and added as stems.
- Text+/caption templates and plugin scripts need the user to be signed in; never type passwords for them.

See `recipes/` for per-video-type settings.
