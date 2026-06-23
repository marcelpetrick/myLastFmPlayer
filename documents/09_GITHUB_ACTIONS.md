# tl;dr

```

• In GitHub:

  1. Open the repo: marcelpetrick/myLastFmPlayer
  2. Go to Actions
  3. In the left sidebar, click Manual Release
  4. Click Run workflow
  5. Fill the fields:
      - version: 0.0.68
      - publish_release: checked / true
      - draft: checked / true
      - prerelease: unchecked / false
  6. Click the green Run workflow button.

  Those fields come from .github/workflows/manual-release.yml. Specifically, they are defined under:

  on:
    workflow_dispatch:
      inputs:

  After the workflow succeeds, GitHub creates a draft release under Releases. You can inspect it there and manually publish it when ready.
```

# GitHub Actions and Releases

This document describes the repository automation added for CI builds and manual
GitHub Releases.

## What Is Implemented as Code

GitHub Actions workflows are repository code. They live in `.github/workflows/`
and become active after they are pushed to GitHub. This repository provides:

- `.github/workflows/local-pipeline.yml`: CI replica of the mandatory local
  pipeline.
- `.github/workflows/manual-release.yml`: manually triggered release build and
  optional GitHub Release publisher.

GitHub documents workflow files under `.github/workflows/`, `workflow_dispatch`
for manual triggers, workflow artifacts for build outputs, and `permissions`
for the `GITHUB_TOKEN` scopes:

- <https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax>
- <https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow>
- <https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts>

## CI Workflow

`Local Pipeline` runs on:

- pushes to `main`, `master`, and `mpe/**`
- pull requests
- manual `workflow_dispatch` runs from the GitHub Actions tab

The workflow runs `./localPipeline.sh --noRun` on `ubuntu-latest` with Python
3.12. It installs the system packages needed by the current headless pipeline,
sets Qt to offscreen mode, suppresses report opening through a no-op report
browser command, and uploads these artifacts when they exist:

- `python-packages`: files from `dist/`
- `coverage-html`: the generated coverage report
- `sphinx-html`: the generated Sphinx documentation

This intentionally mirrors the local mandatory gates instead of inventing a
separate CI-only quality definition.

The Ubuntu package list is deliberately small but includes the native libraries
needed by the current pipeline:

- `graphviz`: required by Sphinx inheritance diagrams.
- `libegl1`, `libxcb-cursor0`, and `libxkbcommon-x11-0`: required by PyQt6 in
  headless Linux runners.
- `libpulse0`: required when importing `PyQt6.QtMultimedia` for playback tests
  and autodoc imports.

## Manual Release Workflow

`Manual Release` is triggered only by a human from the GitHub Actions tab. It has
four inputs:

- `version`: required version without the leading `v`, for example `0.0.68`.
  This must match `my_lastfm_player/version.py`.
- `publish_release`: safety flag. `false` builds and uploads artifacts only.
  `true` also creates the `v<version>` tag and GitHub Release.
- `draft`: when publishing, create the release as a draft. This defaults to
  `true` so artifacts can be reviewed before public publication.
- `prerelease`: when publishing, mark the release as a prerelease.

The build job runs the same no-GUI local pipeline with a persistent report
directory. It keeps the wheel and source distribution as direct release assets
and also creates these ZIP archives:

- `packages`: wheel and source distribution.
- `sphinx-docs`: complete browsable Sphinx HTML documentation.
- `c4-architecture`: architecture source, rendered page, and C4/Graphviz
  diagrams.
- `test-results`: pytest console trace and JUnit XML.
- `coverage`: browsable HTML coverage and machine-readable coverage XML.
- `static-analysis`: Ruff and Pylint reports.
- `pipeline-trace`: stage logs, translation and documentation checks, pipeline
  summary, package/import verification, and environment metadata.

Every ZIP contains a `README.txt` describing its contents and recording the
application version, commit, workflow run ID, and generation time. The GitHub
Release notes contain the same short artifact inventory, and the release assets
use descriptive display labels.

The publish job runs only when `publish_release` is true and uses the repository
`GITHUB_TOKEN` with job-scoped `contents: write` permission to create the tag
and GitHub Release.

## Recommended Release Flow

1. Make and commit the release change locally. The version must already be
   bumped in `my_lastfm_player/version.py`, `README.md`, and
   `tests/test_app_smoke.py`.
2. Run `./localPipeline.sh --noRun` locally.
3. Push the branch and merge it to the default branch after review.
4. Confirm `Local Pipeline` passes on the default branch.
5. Open GitHub, go to **Actions** > **Manual Release** > **Run workflow**.
6. Enter the exact version, for example `0.0.68`.
7. First run with `publish_release=false` if you want a dry-run package build.
8. Run again with `publish_release=true` when ready.
9. Leave `draft=true` for normal releases, inspect the generated draft release,
   then publish it from GitHub's release UI.

This is the safer default for manual releases: the irreversible tag/release step
is guarded by an explicit publish flag, and the public release can still be held
as a draft for final review.

## Operational Notes

- The workflow file must be present on the default branch before the manual
  **Run workflow** button appears.
- The release tag is `v<version>`, for example `v0.0.68`.
- If the requested version does not match package metadata, the release build
  fails before packaging.
- If `publish_release=true` and the tag already exists, the release build fails
  before packaging.
- No PyPI publishing is configured. The release workflow creates GitHub Release
  assets only.
- GitHub Actions workflow artifacts are temporary transport between the build
  and publish jobs. Published GitHub Release assets preserve the reports with
  the release.
- No custom secrets are required for GitHub Releases. The workflow uses the
  built-in `GITHUB_TOKEN`.
