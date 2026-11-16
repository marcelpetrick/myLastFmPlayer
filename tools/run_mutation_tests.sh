#!/usr/bin/env bash
# Mutation-testing gate: run mutmut over my_lastfm_player/ and fail unless the
# mutation score reaches MUTATION_SCORE_MIN percent (default 99).
#
# A mutant counts as detected when a test fails (killed), when mypy rejects it
# (caught by type check), when it hangs past mutmut's timeout, or when it crashes
# the test process. Survivors, untested and suspicious mutants count against the
# score. The summary is also written to mutants/mutation-score.json.
#
# Usage: tools/run_mutation_tests.sh [--report-only] [mutmut run arguments...]
#   --report-only  print the summary of the previous run without running mutmut
# Extra arguments go to `mutmut run`, e.g. a mutant glob such as
# "my_lastfm_player.storage*" to re-check one module after adding tests.
set -u
set -o pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MUTMUT="${ROOT_DIR}/.venv/bin/mutmut"
PYTHON="${ROOT_DIR}/.venv/bin/python"
REPORT_ONLY=false
MUTATION_SCORE_MIN="${MUTATION_SCORE_MIN:-99}"

if [[ "${1:-}" == "--report-only" ]]; then
    REPORT_ONLY=true
    shift
fi

if [[ ! -x "${MUTMUT}" ]]; then
    printf '[ERROR] %s not found. Run ./localPipeline.sh --noRun --noOpen first.\n' "${MUTMUT}" >&2
    exit 2
fi

cd "${ROOT_DIR}" || exit 2
export QT_QPA_PLATFORM=offscreen
# The type-check pre-filter (type_check_command in pyproject.toml) calls `mypy`.
export PATH="${ROOT_DIR}/.venv/bin:${PATH}"

if [[ "${REPORT_ONLY}" == false ]]; then
    max_children="$(nproc 2>/dev/null || echo 4)"
    "${MUTMUT}" run --max-children "${max_children}" "$@" || exit $?
fi

exec "${PYTHON}" "${ROOT_DIR}/tools/mutation_score.py" "${MUTATION_SCORE_MIN}"
