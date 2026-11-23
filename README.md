# Resolve Autopilot

Automate **DaVinci Resolve Studio** from Python and [Claude Code](https://claude.com/claude-code):
build a timeline from a folder of takes, give it a consistent look, pre-mix the audio
(treated voice, music that ducks under speech, sound effects on the cuts), and render.

Leave it running, review the result in the morning. The original media is never modified or deleted.

▶️ **[Watch the 37-second demo](https://github.com/costagonzaga/resolve-autopilot/releases/tag/v0.1.0)** (video attached to the release)

🇧🇷 [Leia em português](README.pt-BR.md)

## What is this, in plain words

People who edit in DaVinci Resolve repeat the same chores: putting takes in order, adding zoom and
colour, levelling voice and music, adding sound effects and animated titles. Resolve Autopilot does
those chores from commands, and works with Claude Code (an AI that programs): you describe what you
want, it builds a **copy** of your edit, and you review it in the morning. Your original files are
never changed.

## Want to help? It takes 30 seconds

The project is new and **needs real people using and commenting**. You do not need to code:

1. ⭐ **Star it.** Click **Star** at the top right of this page (needs a free GitHub account).
2. 💬 **Say hi.** Open the ["Say hi" issue](https://github.com/costagonzaga/resolve-autopilot/issues/4),
   write one sentence (for example: "I edit in Resolve and want to try this") and click **Comment**.
3. 🧪 **Test it on macOS or Linux:** issues
   [#1](https://github.com/costagonzaga/resolve-autopilot/issues/1) and
   [#2](https://github.com/costagonzaga/resolve-autopilot/issues/2) explain the steps.
4. 📤 **Send the link** to someone who edits video in Resolve.

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

## Motion graphics: Resolve + Remotion

Resolve edits, [Remotion](https://www.remotion.dev) draws the animated graphics (it is much better at
text and shapes), and `resolve-autopilot` is the bridge. It renders a **transparent ProRes 4444** clip at
your timeline's exact size and frame rate, then places it on a new video track above V1 of a *duplicate*
timeline. Your takes are never touched.

```bash
cd motion && npm install && cd ..        # once; needs Node.js 20+
resolve-autopilot motion "My reel v2" "My reel v3" \
    --lead "the secret is" --word "CONSISTENCY" --at 3.5 --duration 2.5
```

The bundled template (`motion/src/TitleHighlight.tsx`) is a small white lead line plus one big yellow
Poppins word that springs in and fades out. Copy it to make your own templates: any Remotion
composition can be rendered and placed the same way. Tested on Windows with Resolve Studio 21.

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
