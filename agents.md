# Agent Guidelines

Rules for every change to this repository.

## Commit messages

Use Conventional Commits format for every commit subject:

```
<type>(<scope>): <short summary>
```

Common types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.

Include a body that explains **why** the change was made, what problem it solves,
and any non-obvious decisions. Reference the improvement or bug number when applicable.

## Version bump

Bump `my_lastfm_player/version.py` (`__version__`) with every commit that changes
user-facing behaviour:

- `PATCH` for bug fixes and small improvements
- `MINOR` for new features
- `MAJOR` for breaking changes

Update `README.md` (`Current version: \`x.y.z\``) in the same commit.
Update the version assertion in `tests/test_app_smoke.py` in the same commit.

## Pipeline

Run `./localPipeline.sh --noRun` before every commit and ensure **all mandatory
stages pass**. A red pipeline means no commit.

Stages that must be green: Ruff lint, Docs check, Sphinx, Tests + Coverage (≥90%).

## Translations

After adding or changing any user-visible string wrapped in `self.tr()` or
`translate(...)`, run:

```bash
tools/update_translations.sh
tools/compile_translations.sh
```

Include the updated `.ts` and `.qm` files in the same commit.

## Quality checklist (before every commit)

1. `./localPipeline.sh --noRun` — all mandatory stages green
2. New modules added to `docs/api.rst`
3. Version bumped in `version.py` and `README.md`
4. Translations regenerated if user-visible strings changed
5. Improvement or bug entry in `documents/05_IMPROVEMENTS.md` marked `fixed:`
