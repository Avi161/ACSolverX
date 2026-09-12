"""Bounded continuation of the C19 pair ⟨D, BS(n,n+1)⟩.

Asks whether ordinary AC1–AC3 of bounded depth can create a valid
Britton pinch on D, a one-occurrence row, or a further cyclic-length
drop. Not a U124 solve. Incoming C16 remains non-effective.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.words import (  # noqa: E402
    canon_pair,
    cyc_reduce,
    free_reduce,
    inv,
)

CODE = Path(__file__).resolve().parent
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

import c16_escape_scan as esc  # noqa: E402
import theory_wave1_replay as tw  # noqa: E402
from elementary_ac2_scan import children  # noqa: E402

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"

D = "XuuuXUU"


def c19_pair(n: int) -> tuple[str, str]:
    rec = esc.c19_identity(n)
    return rec["donor"], rec["product"]


def conjugate(word: str, g: str, k: int) -> str:
    return cyc_reduce(tw.pw(g, -k) + word + tw.pw(g, k))


def pinch_report(word: str, n: int) -> dict:
    pinches = esc.split_stable_pinches(word, "u")
    return {
        "word": word,
        "cyc_len": len(cyc_reduce(word)),
        "pinches": pinches,
        "valid": any(esc.associated_bs_pinch(p["k"], p["left"], p["right"], n) for p in pinches),
        "exponents": sorted({p["k"] for p in pinches}),
        "one_occ": esc.one_occ(word),
    }


def interesting(base_len: int, base_valid: bool, r1: str, r2: str, n: int) -> dict | None:
    feat1 = pinch_report(r1, n)
    feat2 = pinch_report(r2, n)
    new_len = feat1["cyc_len"] + feat2["cyc_len"]
    dropped = new_len < base_len
    new_pinch = (feat1["valid"] or feat2["valid"]) and not base_valid
    new_one = (feat1["one_occ"] or feat2["one_occ"]) and not (
        pinch_report(D, n)["one_occ"]
    )
    if not (dropped or new_pinch or new_one):
        return None
    return {
        "new_r1": r1,
        "new_r2": r2,
        "new_len": new_len,
        "drop": base_len - new_len,
        "new_valid_pinch": new_pinch,
        "new_one_occ": new_one,
        "r1_exponents": feat1["exponents"],
        "r2_exponents": feat2["exponents"],
    }


def scan_n(n: int) -> dict:
    r1, r2 = c19_pair(n)
    base_len = len(cyc_reduce(r1)) + len(cyc_reduce(r2))
    base = pinch_report(r1, n)
    conjugates = []
    for gen in "ux":
        for k in range(-n - 2, n + 3):
            w = conjugate(r1, gen, k)
            info = pinch_report(w, n)
            rec = {
                "by": gen,
                "k": k,
                "word": w,
                "exponents": info["exponents"],
                "valid": info["valid"],
                "one_occ": info["one_occ"],
                "len": info["cyc_len"],
            }
            if info["valid"] or info["one_occ"] or set(info["exponents"]) - {-1}:
                conjugates.append(rec)
    ac2_hits = []
    n_children = 0
    seen = set()
    for a, b, move in children(r1, r2):
        n_children += 1
        key = canon_pair(a, b)
        if key in seen:
            continue
        seen.add(key)
        rec = interesting(base_len, base["valid"], a, b, n)
        if rec is not None:
            rec["move"] = move
            ac2_hits.append(rec)
    return {
        "n": n,
        "pair": [r1, r2],
        "base_len": base_len,
        "base_D_pinches": base,
        "n_ac2_raw": n_children,
        "n_ac2_unique": len(seen),
        "ac2_hits": ac2_hits[:20],
        "n_ac2_hits": len(ac2_hits),
        "conjugate_hits": conjugates,
        "n_conjugate_hits": len(conjugates),
    }


def displayed_multiply_identities() -> dict:
    """Literal D · B^{±1} and B · D^{±1} for n=2..7, no extra rotations."""
    rows = []
    for n in range(2, 8):
        r1, r2 = c19_pair(n)
        rows.append(
            {
                "n": n,
                "D_times_B": pinch_report(cyc_reduce(r1 + r2), n),
                "D_times_Binv": pinch_report(cyc_reduce(r1 + inv(r2)), n),
                "B_times_D": pinch_report(cyc_reduce(r2 + r1), n),
                "B_times_Dinv": pinch_report(cyc_reduce(r2 + inv(r1)), n),
            }
        )
    return rows


def main() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    scans = [scan_n(n) for n in range(2, 8)]
    displayed = displayed_multiply_identities()
    summary = {
        "n_checked": len(scans),
        "any_ac2_length_drop": any(r["n_ac2_hits"] and any(h["drop"] > 0 for h in r["ac2_hits"]) for r in scans),
        "any_ac2_valid_pinch": any(any(h["new_valid_pinch"] for h in r["ac2_hits"]) for r in scans),
        "any_ac2_one_occ": any(any(h["new_one_occ"] for h in r["ac2_hits"]) for r in scans),
        "ac2_hit_counts": {r["n"]: r["n_ac2_hits"] for r in scans},
        "any_conjugate_valid_pinch": any(any(c["valid"] for c in r["conjugate_hits"]) for r in scans),
        "any_conjugate_new_exponent": any(
            any(set(c["exponents"]) - {-1} for c in r["conjugate_hits"]) for r in scans
        ),
        "displayed_any_valid_pinch": any(
            any(row[k]["valid"] for k in ("D_times_B", "D_times_Binv", "B_times_D", "B_times_Dinv"))
            for row in displayed
        ),
        "solved_u124": 0,
    }
    report = {
        "summary": summary,
        "scans": scans,
        "displayed_multiplies": displayed,
        "notes": [
            "Depth-1 AC2 plus AC3 by u^k and x^k on D, k in [-(n+2), n+2].",
            "A miss is not an obstruction to longer products.",
            "C19 pair is not a stored U124 spelling; C16 incoming is non-effective.",
            "any_ac2_valid_pinch is not C5 progress: C20 shows those pinches are round trips.",
            "No U124 row is solved.",
        ],
    }
    path = OUT / "c19_continuation.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c19 continuation")
    print(json.dumps(summary, indent=2))
    print(f"wrote {path}")
    return report


if __name__ == "__main__":
    main()
