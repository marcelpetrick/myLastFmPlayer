# Agentic AI Contribution Rules

Practices that apply whenever an AI agent contributes to this repository.

## Commits

- Follow Conventional Commits: `<type>(<scope>): <subject> (vX.X.XXX)`
- Every commit on a branch carries its own version bump:
  - `my_lastfm_player/version.py` — `__version__`
  - `tests/test_app_smoke.py` — exact package/display version assertions
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

## Code Changes

- Do not add features, refactors, or abstractions beyond what the task requires.
- Do not add comments that explain *what* code does — only *why* when non-obvious.
- Verify behavior before changing it; the app is production-usable.
- Write tests for every new code path. Aim to keep or improve the coverage gate.

## Dependency Updates

- Runtime dependencies (`pylast`, `PyQt6`, and `requests`) are pinned to exact versions
  in `pyproject.toml`; review and update each pin deliberately.
- Development dependencies (`pytest`, `pylint`, `ruff`, `sphinx`, `build`, and
  `pytest-cov`) follow the same exact-pin policy.
- Check PyPI with `pip index versions <package>` before claiming a version is current.
- Run the full pipeline after any dependency change.
