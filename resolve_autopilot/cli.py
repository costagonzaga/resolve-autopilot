"""Command line: `resolve-autopilot <command>` (or `python -m resolve_autopilot <command>`)."""
from __future__ import annotations

import argparse
import json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="resolve-autopilot",
                                     description="Automate DaVinci Resolve Studio from Python.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("check", help="Test the connection to Resolve and list the project.")

    p = sub.add_parser("build", help="Import a folder of takes and create a timeline.")
    p.add_argument("folder")
    p.add_argument("name", help="Name of the new timeline.")

    p = sub.add_parser("look", help="Duplicate a timeline and apply zoom + colour grade.")
    p.add_argument("source")
    p.add_argument("new_name")
    p.add_argument("--zoom", type=float, default=1.12)

    p = sub.add_parser("mix", help="Pre-mix voice, music (ducked) and SFX stems with ffmpeg.")
    p.add_argument("timeline")
    p.add_argument("music", help="Music file (wav/mp3).")
    p.add_argument("out_dir")
    p.add_argument("--sfx", nargs="*", default=[], help="SFX files placed on the cuts.")
    p.add_argument("--lufs", type=float, default=-14.0, help="Target loudness (default -14).")

    p = sub.add_parser("add-audio", help="Put the mixed stems on new audio tracks.")
    p.add_argument("timeline")
    p.add_argument("stems_dir")
    p.add_argument("--keep-original", action="store_true", help="Do not mute the original audio.")

    p = sub.add_parser("render", help="Render a timeline to H.264 MP4 and wait.")
    p.add_argument("timeline")
    p.add_argument("out_dir")
    p.add_argument("file_name")
    p.add_argument("--size", nargs=2, type=int, metavar=("W", "H"), help="e.g. --size 1080 1920")

    p = sub.add_parser("inspect", help="Read-only JSON report of the timelines.")
    p.add_argument("names", nargs="*")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    # Imported lazily so `--help` works even where Resolve is not installed.
    if args.command == "check":
        from .connect import check
        check()
    elif args.command == "build":
        from .timeline import build_timeline
        print("Timeline created:", build_timeline(args.folder, args.name).GetName())
    elif args.command == "look":
        from .timeline import Look, apply_look
        _, log = apply_look(args.source, args.new_name, Look(zoom=args.zoom))
        print(json.dumps(log, indent=1))
    elif args.command == "mix":
        from .audio import mix_timeline
        mix_timeline(args.timeline, args.music, args.out_dir, args.sfx, args.lufs)
    elif args.command == "add-audio":
        from .timeline import add_audio_stems
        add_audio_stems(args.timeline, args.stems_dir, mute_original=not args.keep_original)
        print("Stems added.")
    elif args.command == "render":
        from .render import render_timeline
        width, height = args.size if args.size else (None, None)
        print("Final:", render_timeline(args.timeline, args.out_dir, args.file_name, width, height))
    elif args.command == "inspect":
        from .inspect_project import main as inspect_main
        inspect_main(args.names or None)


if __name__ == "__main__":
    main()
