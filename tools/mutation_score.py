"""Summarise the last mutmut run and enforce the minimum mutation score.

Reads ``mutants/**/*.meta`` and classifies every mutant with mutmut's own exit-code
mapping, because ``mutmut export-cicd-stats`` omits mutants caught by the type
checker. Writes ``mutants/mutation-score.json`` for the README badge.

Usage: python tools/mutation_score.py [MINIMUM_PERCENT]
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from mutmut.stats import status_by_exit_code

DETECTED = ("killed", "caught by type check", "timeout", "segfault")
MUTANTS_DIR = Path("mutants")


def collect_statuses(mutants_dir: Path = MUTANTS_DIR) -> Counter[str]:
    """Count mutants per mutmut status."""

    statuses: Counter[str] = Counter()
    for meta in mutants_dir.rglob("*.meta"):
        results = json.loads(meta.read_text(encoding="utf-8"))["exit_code_by_key"]
        for exit_code in results.values():
            statuses[status_by_exit_code[exit_code]] += 1
    return statuses


def main(argv: list[str]) -> int:
    minimum = float(argv[1]) if len(argv) > 1 else 99.0
    statuses = collect_statuses()
    if not statuses:
        print('No mutation results found. Run "tools/run_mutation_tests.sh" first.')
        return 2

    total = sum(statuses.values())
    detected = sum(statuses[status] for status in DETECTED)
    score = 100.0 * detected / total
    print(
        f"Mutation score: {score:.2f}% ({detected}/{total} detected: "
        f"{statuses['killed']} killed, {statuses['caught by type check']} caught by mypy, "
        f"{statuses['timeout']} timeout, {statuses['segfault']} crashed)"
    )
    for status, count in sorted(statuses.items()):
        if status not in DETECTED:
            print(f"  {status}: {count}")
    (MUTANTS_DIR / "mutation-score.json").write_text(
        json.dumps({"score": round(score, 2), "detected": detected, "total": total}) + "\n",
        encoding="utf-8",
    )
    if score < minimum:
        print(
            f"Mutation gate: FAIL ({score:.2f}% < {minimum:.2f}%; "
            "list survivors with `.venv/bin/mutmut results`)"
        )
        return 1
    print(f"Mutation gate: PASS ({score:.2f}% >= {minimum:.2f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
