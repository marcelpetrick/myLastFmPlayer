# Release Announcement: myLastFmPlayer

> **Publication draft:** This is announcement copy. Current capabilities and
> installation instructions are in [`../README.md`](../README.md).

Weeks ago, I finally implemented an idea that had been on my mind for years: a desktop
player for favorite tracks from Last.fm.

Enter a Last.fm username and the app imports that account's loved tracks, resolves them
through YouTube, downloads the best available audio stream for each match, and stores the
files locally. The result is a fully functional Linux desktop product that I have used in
practice, rather than a proof of concept.

The complete workflow runs from one PyQt6 interface. Tracks appear while Last.fm pages
are still loading, YouTube checks and downloads overlap, failed tracks remain independent,
and completed work survives restarts. You can sort and filter the library, prioritize a
track for playback, stop and resume YouTube work, use optional Last.fm scrobbling, and
choose from four themes and five interface languages.

I built the project with the engineering practices I expect from a maintained product:

- a repeatable local pipeline and matching GitHub Actions workflow;
- a 99% test-coverage gate;
- Ruff and Pylint static analysis;
- complete Qt translation catalogs;
- Sphinx API documentation and C4 architecture diagrams;
- installable wheel and source packages;
- reproducible GitHub Releases with test, coverage, and analysis reports.

`myLastFmPlayer` is licensed under GPLv3 or later, so you can inspect it, adapt it, and
share your changes.

Repository: <https://github.com/marcelpetrick/myLastFmPlayer>

Feedback, issues, and ideas are welcome.
