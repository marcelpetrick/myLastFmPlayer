#!/usr/bin/env bash
# Mutation-testing gate: run mutmut over my_lastfm_player/ and fail unless every
# generated mutant is detected by the test suite. A mutant counts as detected when
# a test fails (killed), when it hangs past mutmut's timeout, or when it crashes
# the test process; survivors, untested and suspicious mutants fail the gate.
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
STATS_FILE="${ROOT_DIR}/mutants/mutmut-cicd-stats.json"
REPORT_ONLY=false

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

if [[ "${REPORT_ONLY}" == false ]]; then
    max_children="$(nproc 2>/dev/null || echo 4)"
    "${MUTMUT}" run --max-children "${max_children}" "$@" || exit $?
fi

"${MUTMUT}" export-cicd-stats >/dev/null || exit $?

"${PYTHON}" - "${STATS_FILE}" <<'EOF'
import json
import sys

stats = json.load(open(sys.argv[1], encoding="utf-8"))
total = stats["total"]
detected = stats["killed"] + stats.get("timeout", 0) + stats.get("segfault", 0)
undetected = {
    key: stats[key] for key in ("survived", "no_tests", "suspicious", "skipped") if stats.get(key)
}
score = 100.0 * detected / total if total else 100.0
print(
    f"Mutation score: {score:.2f}% ({detected}/{total} detected: "
    f"{stats['killed']} killed, {stats.get('timeout', 0)} timeout, "
    f"{stats.get('segfault', 0)} crashed)"
)
for key, value in undetected.items():
    print(f"  {key}: {value}")
if undetected:
    print("Mutation gate: FAIL (list survivors with `.venv/bin/mutmut results`)")
    sys.exit(1)
print("Mutation gate: PASS")
EOF
