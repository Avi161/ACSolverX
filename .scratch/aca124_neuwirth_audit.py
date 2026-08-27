from __future__ import annotations

import csv
import dataclasses
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROOF_WORKTREE = ROOT / ".claude/worktrees/codex-proofs"
DATA = PROOF_WORKTREE / "data/ms_unsolved_reps/aca_124.csv"
OUTPUT = ROOT / ".scratch/aca124_neuwirth_audit.json"
sys.path.insert(0, str(PROOF_WORKTREE))

from experiments.stable_ac.thickenable.ak3_aut_frontier_certificate import (  # noqa: E402
    dispatch_frontier_support,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    rows = list(csv.DictReader(DATA.open(encoding="utf-8")))
    results = []
    for row in rows:
        words = (row["r1"], row["r2"])
        decision = dispatch_frontier_support(None, words)
        results.append(
            {
                "name": row["name"],
                "relators": list(words),
                "category": decision.category,
                "support": decision.support.kind,
                "spherical": decision.spherical,
                "solver_verdict": decision.solver_verdict,
                "counters": dataclasses.asdict(decision.counters),
            }
        )

    payload = {
        "schema": "aca124-neuwirth-audit-v1",
        "claim_limit": (
            "Exact literal stored representatives only. A negative does not obstruct "
            "a later stable-AC state from becoming thickenable."
        ),
        "input": {"path": str(DATA.relative_to(ROOT)), "sha256": sha256(DATA)},
        "solver_sources": [
            {
                "path": str(path.relative_to(ROOT)),
                "sha256": sha256(path),
            }
            for path in (
                PROOF_WORKTREE
                / "experiments/stable_ac/thickenable/ak3_aut_frontier_certificate.py",
                PROOF_WORKTREE
                / "experiments/stable_ac/thickenable/neuwirth_rank_solver.py",
            )
        ],
        "summary": {
            "rows": len(results),
            "support_histogram": dict(Counter(row["support"] for row in results)),
            "category_histogram": dict(Counter(row["category"] for row in results)),
            "exhaustive_rows": sum(row["counters"]["exhaustive"] for row in results),
        },
        "results": results,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(OUTPUT)


if __name__ == "__main__":
    main()
