"""Search AC1+AC3 reorientations that restore a peelable common suffix.

After one displayed Q-peel the right context becomes v[y^{-1},x^{-1}].
Cyclic permutation is AC3 by a prefix of the same relator. This script
asks whether some orientation pair of (R1^{±1}, R2'^{±1}) again shares a
suffix of length at least 2, and whether peeling that pair strictly
decreases the isolated x-power that the Q family cares about, reaches a
one-occurrence relator, or returns to the previous pair.

Not a heap search. Not a U124 solve by itself.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.words import (  # noqa: E402
    cyc_reduce,
    free_reduce,
    inv,
)

CODE = Path(__file__).resolve().parent
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))
from q_peel import (  # noqa: E402
    COMM,
    G,
    U,
    V,
    peel_suffix,
    power_block_length,
    q_pair,
)
from u124_census import one_occurrence_cyclic, two_block_shape  # noqa: E402

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"


def orientations(word: str) -> list[tuple[str, str]]:
    reduced = cyc_reduce(word)
    out = []
    seen = set()
    for base, tag in ((reduced, "id"), (inv(reduced), "inv")):
        n = len(base)
        for k in range(n or 1):
            rot = base[k:] + base[:k] if n else ""
            if rot in seen:
                continue
            seen.add(rot)
            out.append((rot, f"{tag}:{k}"))
    return out


def common_suffix_len(a: str, b: str) -> int:
    k = 0
    m = min(len(a), len(b))
    while k < m and a[-(k + 1)] == b[-(k + 1)]:
        k += 1
    return k


def search_restored_peels(r1: str, r2: str, min_suffix: int = 2) -> list[dict]:
    hits = []
    base_x = power_block_length(r2, "x")
    base_len = len(cyc_reduce(r1)) + len(cyc_reduce(r2))
    for a, ta in orientations(r1):
        for b, tb in orientations(r2):
            suf = common_suffix_len(a, b)
            if suf < min_suffix:
                continue
            peeled = peel_suffix(a, b)
            if peeled in (b, inv(b), a, inv(a)):
                kind = "round_trip_or_swap"
            else:
                kind = "new"
            rec = {
                "r1_orientation": a,
                "r2_orientation": b,
                "tags": f"{ta}|{tb}",
                "suffix_len": suf,
                "suffix": a[-suf:] if suf else "",
                "peeled": peeled,
                "peeled_len": len(peeled),
                "pair_length": len(a) + len(peeled),
                "length_drop": (len(a) + len(peeled)) < base_len,
                "peeled_x_run": power_block_length(peeled, "x"),
                "base_x_run": base_x,
                "x_run_drop": power_block_length(peeled, "x") < base_x,
                "one_occurrence": one_occurrence_cyclic(peeled)
                or one_occurrence_cyclic(a),
                "two_block_peeled": two_block_shape(peeled),
                "kind": kind,
            }
            hits.append(rec)
    return hits


def interesting(hit: dict) -> bool:
    return bool(
        hit["length_drop"]
        or hit["x_run_drop"]
        or hit["one_occurrence"]
        or hit["two_block_peeled"]
        or hit["peeled_len"] <= 1
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    reports = []
    for delta in (-1, 1):
        for n in range(2, 8):
            r1, r2 = q_pair(n, delta)
            displayed = peel_suffix(r1, r2)
            # After the displayed peel, keep R1 and replace R2.
            restored = search_restored_peels(r1, displayed, min_suffix=2)
            interesting_hits = [h for h in restored if interesting(h)]
            # Also search peels of the original pair under all orientations
            # (the displayed suffix is one of them).
            original = search_restored_peels(r1, r2, min_suffix=2)
            orig_interesting = [h for h in original if interesting(h)]
            reports.append(
                {
                    "n": n,
                    "delta": delta,
                    "r1": r1,
                    "r2": r2,
                    "displayed_peel": displayed,
                    "g_inv": inv(G),
                    "commutator": COMM,
                    "u": U,
                    "v": V,
                    "original_orientation_peels": len(original),
                    "original_interesting": orig_interesting[:12],
                    "n_original_interesting": len(orig_interesting),
                    "after_peel_orientation_peels": len(restored),
                    "after_peel_interesting": interesting_hits[:12],
                    "n_after_peel_interesting": len(interesting_hits),
                    "after_peel_x_run_drops": sum(1 for h in restored if h["x_run_drop"]),
                    "after_peel_length_drops": sum(1 for h in restored if h["length_drop"]),
                }
            )
    summary = {
        "cases": len(reports),
        "any_original_interesting": any(r["n_original_interesting"] for r in reports),
        "any_after_peel_interesting": any(r["n_after_peel_interesting"] for r in reports),
        "any_after_peel_x_run_drop": any(r["after_peel_x_run_drops"] for r in reports),
        "rows": reports,
        "status": "orientation_search_not_a_solve",
        "note": (
            "Interesting means length drop, x-run drop, one-occurrence, "
            "two-block, or peeled length <= 1. Cyclic AC1/AC3 only."
        ),
    }
    path = OUT / "q_peel_orientations.json"
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "cases": summary["cases"],
                "any_original_interesting": summary["any_original_interesting"],
                "any_after_peel_interesting": summary["any_after_peel_interesting"],
                "any_after_peel_x_run_drop": summary["any_after_peel_x_run_drop"],
                "sample_original_n2p": reports[6]["n_original_interesting"]
                if len(reports) > 6
                else None,
                "sample_after_n2p": reports[6]["n_after_peel_interesting"]
                if len(reports) > 6
                else None,
                "status": summary["status"],
            },
            indent=2,
        )
    )
    print("wrote", path)


if __name__ == "__main__":
    main()
