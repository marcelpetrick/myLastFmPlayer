# GitHub Actions and Releases

The repository has two product workflows and CodeQL analysis:

- **Local Pipeline** runs for pushes to `master`, `main`, and `mpe/**`, for pull
  requests, and on manual dispatch. It executes the same `localPipeline.sh --noRun`
  gate used before local commits and uploads packages, coverage, and Sphinx HTML.
- **Manual Release** accepts an explicit version, rebuilds and verifies every artifact,
  and can publish the matching tag and GitHub Release.
- **CodeQL** performs GitHub's security-oriented Python analysis on its configured
  events.

## Release Preconditions

Before dispatching a release:

1. Update `my_lastfm_player/version.py`.
2. Update the exact version checks in `tests/test_app_smoke.py`.
3. Update the README current version.
4. Run the complete local pipeline successfully.
5. Commit with the matching `(vX.Y.Z)` suffix and push the commit.
6. Confirm that tag `vX.Y.Z` does not already exist.

The requested workflow version must exactly match the package version checked out from
the selected branch. When publishing is enabled, an existing tag makes validation fail
instead of replacing a release.

## Run from the GitHub Interface

1. Open the repository's **Actions** page.
2. Select **Manual Release**.
3. Choose **Run workflow** and select the branch containing the release commit.
4. Enter the version without a leading `v`, for example `0.0.170`.
5. Enable **publish_release**.
6. Choose whether the release is a draft or prerelease.
7. Start the workflow and wait for both build and publish jobs to succeed.

The workflow defaults are intentionally conservative: publishing is off and a
published release would be created as a draft unless the caller changes those inputs.

## Run with the GitHub CLI

To publish a normal, non-draft release:

```sh
gh workflow run "Manual Release" \
  --ref master \
  -f version=0.0.170 \
  -f publish_release=true \
  -f draft=false \
  -f prerelease=false
```

Inspect and follow the dispatched run:

```sh
gh run list --workflow "Manual Release" --limit 5
gh run watch RUN_ID --exit-status
```

Verify the finished release and its assets:

```sh
gh release view v0.0.170
```

## Published Assets

A successful published release contains nine independently downloadable assets:

| Asset | Purpose |
| --- | --- |
| Python wheel | Direct installation |
| Source distribution | Standard Python source package |
| Packages ZIP | Wheel and source distribution together |
| Sphinx documentation ZIP | Browsable generated product/API documentation |
| C4 architecture ZIP | Architecture source, rendered page, and diagrams |
| Test-results ZIP | Pytest trace and JUnit XML |
| Coverage ZIP | HTML and XML coverage reports |
| Static-analysis ZIP | Ruff and Pylint reports |
| Pipeline-trace ZIP | Stage logs, summary, environment, and import verification |

Every generated ZIP includes a `README.txt` describing its contents and build
provenance. The workflow targets the dispatched commit SHA so the tag, packages, and
reports all refer to the same source revision.
