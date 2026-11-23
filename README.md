# Resolve Autopilot

Automate **DaVinci Resolve Studio** from Python and [Claude Code](https://claude.com/claude-code):
build a timeline from a folder of takes, give it a consistent look, pre-mix the audio
(treated voice, music that ducks under speech, sound effects on the cuts), and render.

Leave it running, review the result in the morning. The original media is never modified or deleted.

🇧🇷 [Leia em português](README.pt-BR.md)

## Why

Resolve's scripting API is powerful but awkward: the module is not on PyPI, setup differs per OS,
and it cannot set clip volume or keyframes. This project packages the parts that are painful to
rediscover:

- **Connection** that works on Windows, macOS and Linux, with a clear message when Resolve does not answer.
- **Timeline builder** from a folder of numbered takes.
- **Look**: alternating punch-in zoom and a CDL grade on a *duplicate* timeline, with a marker on every cut.
- **Audio pre-mix with ffmpeg** (the API cannot do volume): dialogue rebuilt from the originals and cleaned,
  music ducked with side-chain compression, SFX aligned so their loudest moment hits the cut,
  everything levelled to a target LUFS.
- **Render** through Resolve's queue, applying settings one by one so a refused value cannot silently drop the picture.
- **Read-only inspector** that prints timelines as JSON, so an AI assistant can see what you edited.
- A **Claude Code skill** (`skills/resolve-autopilot`) that teaches Claude the workflow.

## Requirements

- DaVinci Resolve **Studio** (external scripting is a Studio feature) with a project open.
- Resolve: *Preferences > System > General > External scripting using: Local*.
- Python 3.9+ and [ffmpeg](https://ffmpeg.org/) (or `pip install imageio-ffmpeg`).

## Install

```bash
pip install "resolve-autopilot[ffmpeg] @ git+https://github.com/costagonzaga/resolve-autopilot"
resolve-autopilot check
```

To hack on it instead:

```bash
git clone https://github.com/costagonzaga/resolve-autopilot
cd resolve-autopilot
pip install -e ".[dev,ffmpeg]"
```

## Usage

```bash
# 1. Takes named 01.mp4, 02.mp4... -> timeline in that order
resolve-autopilot build ./takes "My reel"

# 2. Duplicate with zoom + colour grade (original stays untouched)
resolve-autopilot look "My reel" "My reel v2"

# 3. Pre-mix voice / music / sfx, levelled to -14 LUFS
resolve-autopilot mix "My reel v2" music.wav ./audio --sfx whoosh1.wav whoosh2.wav

# 4. Bring the stems back; the original audio track is muted, not deleted
resolve-autopilot add-audio "My reel v2" ./audio

# 5. Render
resolve-autopilot render "My reel v2" ./out reel --size 1080 1920

# Anything: read-only report
resolve-autopilot inspect
```

Use it as a library too: `from resolve_autopilot.timeline import apply_look, Look`.

## Using it with Claude Code

Copy `skills/resolve-autopilot` into your project's `.claude/skills/` and ask
*"edit the takes in `entrada/video-01` as a reel"*. The skill describes the safe workflow
(always work on a copy, never touch originals, log every round).

## Status

Early (v0.1). Developed and tested on Windows with Resolve Studio 21. macOS and Linux paths follow
Blackmagic's documentation but are **untested**: reports and fixes are very welcome.
See [CONTRIBUTING.md](CONTRIBUTING.md) and the issues labelled `good first issue`.

## Not included

Captions are not generated here: Resolve's own Auto Captions or a Text+ template can be driven
through the same API (an open issue). No media, music or sound effects are shipped.

## License

MIT. DaVinci Resolve is a trademark of Blackmagic Design; this project is not affiliated with them.
