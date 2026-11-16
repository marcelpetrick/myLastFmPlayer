# Mutation Testing Plan

## Question

When this plan was written, the suite (613 tests, 99% line+branch coverage) showed
that nearly every line *runs* under test. It did not show that the tests would *notice* if a line were
wrong. Mutation testing answers that: it makes small faults in the source
(`<` → `<=`, `True` → `False`, a string altered, a call argument dropped) and
re-runs the tests. A mutant that no test kills shows behaviour the suite does
not check.

Before this work the repository had no mutation testing, so how strong the tests
were was unknown.

## Tool Choice

| Tool | State (2026-11) | Verdict |
| --- | --- | --- |
| **mutmut** 3.8.1 | Active, pytest-native, `pyproject.toml` config, runs only the tests that cover each mutated function, incremental cache, fork-based parallel workers | **Chosen** |
| cosmic-ray 8.9.0 | Active, session database, distributed execution | Heavier setup; built for large/distributed runs |
| poodle 1.4.0 | Small project | Smaller community, fewer operators |
| mutatest 3.1.0 | Unmaintained | Rejected |

mutmut fits the existing pytest + `pyproject.toml` setup without a new runner. It
works with the offscreen Qt platform the suite already uses.

## Plan

1. **Configure** `[tool.mutmut]` in `pyproject.toml`: mutate `my_lastfm_player/`,
   run pytest with `--no-cov`, and copy the non-Python files the tests read
   (README, docs, tools, workflows) into mutmut's `mutants/` sandbox.
2. **Baseline**: run `mutmut run` and record killed / survived / timeout counts.
3. **Kill survivors** module by module, starting with pure logic (models, storage,
   settings, lastfm, scrobbling, download, youtube) and finishing with the
   controller. Each survivor is resolved in one of three ways:
   - strengthen or add a test so the mutant fails (the default);
   - mark a *provably equivalent* mutant (same observable behaviour, e.g. a log
     message text or a default that is always overridden) with
     `# pragma: no mutate` and a short reason;
   - exclude non-logic code wholesale only where mutation cannot be observed
     (e.g. log calls), listed in `do_not_mutate_patterns` with a justification.
4. **Gate**: add `tools/run_mutation_tests.sh`, which runs mutmut and fails when
   the mutation score is below 99% (timeouts and crashes count as detected, and so
   do mutants that mypy rejects since it became mutmut's type-check pre-filter;
   survivors, suspicious and untested mutants do not). It is an opt-in pipeline
   stage (`--mutation`) because a full run takes minutes rather than seconds.
5. **Keep coverage ≥ 99%**: the existing `--cov-fail-under=99` gate stays
   unchanged and must remain green with the new tests.
6. **Document** the workflow in `07_AGENT_GUIDELINES.md` and the README.

## Definition of Done

- Mutation score **≥ 99%** (`tools/run_mutation_tests.sh`, `MUTATION_SCORE_MIN`).
- Every `# pragma: no mutate` carries a reason.
- `./localPipeline.sh --noRun --noOpen` is green with coverage ≥ 99%.

## Setup Findings

- **Qt slots behind the trampoline.** mutmut replaces every method with a
  `trampoline(*args, **kwargs)`. PyQt normally drops a signal argument a slot does
  not accept (e.g. `clicked(bool)` → `slot(self)`), but it cannot see through
  `*args`, so the slot raised `TypeError` and Qt aborted the process. The eight
  affected connections now go through `lambda _checked=False: self.slot()`.
  `@pyqtSlot()` would also work, but mutmut does not mutate decorated functions.
- **Slot exceptions abort pytest.** `tests/conftest.py` installs a per-test
  `sys.excepthook`, so an exception inside a Qt slot fails that one test instead of
  killing the whole run.
- **Qt is not fork-safe.** With mutmut's default `fork` isolation, workers are
  forked from a process that already ran the GUI tests; about a thousand mutants
  died with SIGABRT and were reported as *suspicious*, masking survivors.
  `process_isolation = "forkserver"` forks from a clean process instead.

## Results

| Run | Mutants | Detected | Survived | Suspicious | Score |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baseline (`fork`, slot fix) | 10,926 | 7,137 | 2,753 | 1,036 | 65.3% |
| Baseline (`forkserver`) | 10,926 | 7,096 | 3,798 | 32 | 64.95% |
| Catalog check, golden images, log exclusion (v0.0.205) | 10,274 | 8,283 | 1,969 | 22 | 80.62% |
| Contract tests for scrobbling, playback, download, YouTube, Last.fm (v0.0.206) | 10,274 | 8,653 | 1,599 | 22 | 84.22% |
| mypy as pre-filter, controller wiring tests (v0.0.208) | 10,281 | 9,257 | 1,016 | 8 | 90.04% |

The full write-up is in [`../docs/followup_mutation_testing.md`](../docs/followup_mutation_testing.md).
