"""Connection to the DaVinci Resolve scripting API (Windows, macOS, Linux).

The Resolve scripting module is not on PyPI: it ships with Resolve itself. This module
points Python at it at run time (it never touches your system settings) and exposes
small helpers used by everything else.

Override the defaults with the environment variables RESOLVE_SCRIPT_API and
RESOLVE_SCRIPT_LIB if Resolve is installed somewhere unusual.
"""
from __future__ import annotations

import os
import sys


def default_paths() -> tuple[str, str]:
    """Return (script_api_dir, fusionscript_lib) for the current OS."""
    if sys.platform.startswith("win"):
        program_data = os.environ.get("PROGRAMDATA", r"C:\ProgramData")
        program_files = os.environ.get("PROGRAMFILES", r"C:\Program Files")
        api = os.path.join(program_data, "Blackmagic Design", "DaVinci Resolve",
                           "Support", "Developer", "Scripting")
        lib = os.path.join(program_files, "Blackmagic Design", "DaVinci Resolve", "fusionscript.dll")
    elif sys.platform == "darwin":
        api = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
        lib = ("/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/"
               "Fusion/fusionscript.so")
    else:
        api = "/opt/resolve/Developer/Scripting"
        lib = "/opt/resolve/libs/Fusion/fusionscript.so"
    return api, lib


def get_resolve():
    """Return the live Resolve application object, or exit with a helpful message."""
    api, lib = default_paths()
    api = os.environ.get("RESOLVE_SCRIPT_API", api)
    lib = os.environ.get("RESOLVE_SCRIPT_LIB", lib)
    os.environ["RESOLVE_SCRIPT_API"] = api
    os.environ["RESOLVE_SCRIPT_LIB"] = lib
    modules = os.path.join(api, "Modules")
    if modules not in sys.path:
        sys.path.append(modules)
    try:
        import DaVinciResolveScript as dvr  # provided by Resolve
    except ImportError as exc:
        raise SystemExit(f"Could not import DaVinciResolveScript from {modules}: {exc}")
    resolve = dvr.scriptapp("Resolve")
    if resolve is None:
        raise SystemExit(
            "Resolve did not answer. Check that: 1) DaVinci Resolve *Studio* is open with a "
            "project loaded; 2) Preferences > System > General > 'External scripting using' "
            "is set to Local; 3) your Python version is supported by fusionscript."
        )
    return resolve


def get_project(resolve=None):
    """Return the current project (exits if none is open)."""
    resolve = resolve or get_resolve()
    project = resolve.GetProjectManager().GetCurrentProject()
    if project is None:
        raise SystemExit("No project is open in Resolve.")
    return project


def find_timeline(project, name: str):
    """Return the timeline called `name`, or None."""
    for i in range(1, project.GetTimelineCount() + 1):
        timeline = project.GetTimelineByIndex(i)
        if timeline.GetName() == name:
            return timeline
    return None


def require_timeline(project, name: str):
    timeline = find_timeline(project, name)
    if timeline is None:
        raise SystemExit(f"Timeline '{name}' does not exist.")
    return timeline


def check() -> None:
    """Print a short connection report (used by `resolve-autopilot check`)."""
    print(f"Python {sys.version.split()[0]} on {sys.platform}")
    resolve = get_resolve()
    print("Resolve:", resolve.GetProductName(), resolve.GetVersionString())
    project = resolve.GetProjectManager().GetCurrentProject()
    if project is None:
        print("No project is open.")
        return
    print("Project:", project.GetName())
    count = project.GetTimelineCount()
    print("Timelines:", count)
    for i in range(1, count + 1):
        print(f"  {i}. {project.GetTimelineByIndex(i).GetName()}")
    clips = project.GetMediaPool().GetRootFolder().GetClipList()
    print("Clips in the Media Pool root:", len(clips))
