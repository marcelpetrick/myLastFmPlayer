# Agentic AI contribution rules

Practices that apply whenever an AI agent contributes to this repository.

## Commits

- Follow Conventional Commits: `<type>(<scope>): <subject> (vX.X.XXX)`
- Every commit on a branch carries its own version bump:
  - `my_lastfm_player/version.py` — `__version__`
  - `tests/test_app_smoke.py` — four version string assertions
  - `README.md` — current version reference
- Sequential commits on the same branch get sequential version numbers.
- No AI attribution. No `Co-Authored-By` lines. No mention of AI tools in commit messages or source files.

## Pipeline

- Run `./localPipeline.sh` before every commit. All stages must be green:
  - Ruff — 0 violations
  - Pylint — 10.00/10
  - Translations — 0 untranslated strings across all locales
  - Docs — no trailing whitespace, required files present
  - Tests + Coverage — 99 % minimum
- Never commit on a red pipeline. Fix the failure first.

## Code changes

- Do not add features, refactors, or abstractions beyond what the task requires.
- Do not add comments that explain *what* code does — only *why* when non-obvious.
- Verify behavior before changing it; the app is production-usable.
- Write tests for every new code path. Aim to keep or improve the coverage gate.

## Dependency updates

- Runtime deps: `pylast`, `PyQt6`, `requests` — bump the `>=` floor in `pyproject.toml` to the latest stable release.
- Dev deps: `pytest`, `pylint`, `ruff`, `sphinx`, `build`, `pytest-cov` — same rule.
- Check PyPI with `pip index versions <package>` before claiming a version is current.
- Run the full pipeline after any dependency change.
