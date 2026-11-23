# Contributing

Thanks for helping! The easiest ways in:

- **Test on macOS or Linux** and report what `resolve-autopilot check` prints.
- Pick an issue labelled `good first issue` (see `docs/good-first-issues.md` for ideas).
- Add a recipe in `skills/resolve-autopilot/recipes/` for a video type you edit often.

## Ground rules

- Never modify or delete source media. New work goes in a duplicate timeline or a new file.
- Anything that talks to Resolve lives behind a function that takes names/paths, so it can be tested.
  Logic that does not need Resolve (planning, parsing) must have an offline test in `tests/`.
- No media, music, sound effects or project files in the repo.

## Dev setup

```bash
pip install -e ".[dev,ffmpeg]"
pytest
```

CI runs the offline tests only; Resolve itself cannot run in CI.
