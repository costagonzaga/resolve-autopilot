"""Tests that run without DaVinci Resolve installed."""
import os

from resolve_autopilot import audio, cli, connect, timeline


def test_default_paths_are_strings():
    api, lib = connect.default_paths()
    assert "Scripting" in api and lib


def test_list_media_sorted_and_filtered(tmp_path):
    for name in ["02.mp4", "01.mov", "notes.txt", "03.WAV"]:
        (tmp_path / name).write_bytes(b"")
    names = [os.path.basename(p) for p in timeline.list_media(str(tmp_path))]
    assert names == ["01.mov", "02.mp4", "03.WAV"]


def test_plan_sfx_skips_flash_cuts_and_alternates():
    events = audio.plan_sfx([2.0, 4.0, 4.5, 6.0], [2.0, 0.5, 1.5, 1.2], ["a.wav", "b.wav"])
    assert [e[0] for e in events] == ["a.wav", "b.wav", "a.wav"]
    assert [e[1] for e in events] == [2.0, 4.5, 6.0]


def test_plan_sfx_without_files_is_empty():
    assert audio.plan_sfx([1.0], [2.0], []) == []


def test_look_cdl_keys():
    cdl = timeline.Look().cdl()
    assert set(cdl) == {"NodeIndex", "Slope", "Offset", "Power", "Saturation"}


def test_cli_parser_knows_all_commands():
    parser = cli.build_parser()
    for command in ["check", "build f n", "look a b", "mix t m o", "add-audio t d", "render t o f", "motion a b --word X", "inspect"]:
        assert parser.parse_args(command.split()).command == command.split()[0]
