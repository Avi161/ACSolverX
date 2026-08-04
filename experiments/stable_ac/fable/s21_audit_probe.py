"""S21 adversarial audit probe — structural contrast between AK(3) and the S21 controls.

NEW FILE (audit).  Does not modify or import-and-mutate anything under experiments/.
It only READS the repo's own deciders (`s12_hunt.decide`, `neuwirth_rank_n`) and the
solved Miller-Schupp ladder, and reports:

  (a) the rank-2 AND rank-3 exact-census defect of AK(3) and of the five S21 controls
      (S21 read the defect off the rank-3 STABILIZED form only; the rank-2 number is
      what "matched on minimum_defect" has to mean, and it is not in S21);
  (b) structural invariants that differ systematically between AK(3) and the controls
      (relator-length shape, abelianised matrix rows, x-letter counts, link census size);
  (c) a scan of the whole solved ladder for defect-4 members, keyed by first relator and
      by shape, to find controls that do NOT share `YYXyx` and/or are 6+7 like AK(3).

Usage:
    python3 -m experiments.stable_ac.fable.s21_audit_probe --mode defects
    python3 -m experiments.stable_ac.fable.s21_audit_probe --mode scan --lo 11 --hi 18
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from experiments.stable_ac.fable.s12_hunt import decide, load_ladder, ALPHA
from experiments.stable_ac.fable.neuwirth_rank_n import (
    build_link_n, census_size, gamma_N_factorial_n)

REPO = Path(__file__).resolve().parents[3]

AK3 = ("xyxYXY", "xxxYYYY")
S21_CONTROLS = [
    ("YYXyx", "YYxxxyXX"),
    ("YYXyx", "YYxxyXXX"),
    ("YYXyx", "YXYXXyxx"),
    ("YYXyx", "YXXYxxx"),
    ("YYXyx", "YXXXYxx"),
]


def gens_of(words):
    return tuple(sorted(set("".join(words).lower())))


def stab(words, k=1):
    g = list(gens_of(words))
    out = list(words)
    for _ in range(k):
        z = next(c for c in ALPHA if c not in g)
        g.append(z)
        out.append(z)
    return tuple(out)


def abelian_row(w, gens):
    return [sum((1 if c == g else -1 if c == g.upper() else 0) for c in w) for g in gens]


def letter_counts(w, gens):
    return {g: sum(1 for c in w if c.lower() == g) for g in gens}


def exact_defect(words, cap=2_000_000):
    """Exact census defect; returns (defect, census_size) or (None, size) if over cap."""
    g = gens_of(words)
    try:
        size = census_size(build_link_n(words, g), g)
    except Exception as exc:
        return None, f"link_exc:{type(exc).__name__}"
    if size > cap:
        return None, size
    try:
        c = gamma_N_factorial_n(words, g, cap_rotations=cap, keep_accepting=False)
    except Exception as exc:
        return None, f"census_exc:{type(exc).__name__}"
    if c["status"] != "OK":
        return None, size
    return c["minimum_defect"], size


def profile(words):
    g = gens_of(words)
    rows = [abelian_row(w, g) for w in words]
    det = (rows[0][0] * rows[1][1] - rows[0][1] * rows[1][0]) if len(rows) == 2 else None
    return {
        "words": list(words),
        "gens": list(g),
        "shape": sorted(len(w) for w in words),
        "total": sum(len(w) for w in words),
        "abelian_rows": rows,
        "abelian_det": det,
        "unit_row": any(sorted(map(abs, r)) == [0, 1] for r in rows),
        "letters": [letter_counts(w, g) for w in words],
    }


def cmd_defects(args):
    out = {"record": "s21_audit_defects", "rows": []}
    targets = [("AK3", AK3)] + [(f"ctl{i}", w) for i, w in enumerate(S21_CONTROLS)]
    for name, w in targets:
        row = {"name": name, **profile(w)}
        d2, s2 = exact_defect(w, args.cap)
        row["rank2_defect"], row["rank2_census"] = d2, s2
        row["rank2_decide"] = decide(w, 200_000)
        w3 = stab(w, 1)
        d3, s3 = exact_defect(w3, args.cap)
        row["rank3_defect"], row["rank3_census"] = d3, s3
        if args.rank4:
            w4 = stab(w, 2)
            d4, s4 = exact_defect(w4, args.cap)
            row["rank4_defect"], row["rank4_census"] = d4, s4
        out["rows"].append(row)
        print(f"{name:5s} {str(w):34s} shape={row['shape']} ab={row['abelian_rows']} "
              f"det={row['abelian_det']} unit_row={row['unit_row']} "
              f"r2def={d2} (cen {s2})  r3def={d3} (cen {s3})"
              + (f"  r4def={row.get('rank4_defect')}" if args.rank4 else ""))
    Path(REPO / args.out).write_text(json.dumps(out, indent=1))
    print("wrote", args.out)


def cmd_scan(args):
    """Scan the solved ladder for defect-4 members; group by first relator and shape."""
    rng = random.Random(args.seed)
    lad = load_ladder(args.n, rng, lo=args.lo, hi=args.hi)
    rows = []
    for w in lad:
        w3 = stab(w, 1)
        d3, s3 = exact_defect(w3, args.cap)
        d2, s2 = (None, None)
        if d3 == 4 or args.all_rank2:
            d2, s2 = exact_defect(w, args.cap)
        rows.append({"words": list(w), "shape": sorted(len(x) for x in w),
                     "total": sum(len(x) for x in w), "r3def": d3, "r3census": s3,
                     "r2def": d2, "r2census": s2,
                     "first": w[0], "profile": profile(w)})
        if d3 == 4:
            print(f"  DEFECT4 {str(w):36s} shape={sorted(len(x) for x in w)} "
                  f"r2def={d2} first={w[0]}")
    d4 = [r for r in rows if r["r3def"] == 4]
    print(f"\nscanned {len(rows)}   with a rank-3 defect number: "
          f"{sum(1 for r in rows if r['r3def'] is not None)}   defect4: {len(d4)}")
    from collections import Counter
    print("defect-4 first relators:", Counter(r["first"] for r in d4))
    print("defect-4 shapes:", Counter(tuple(r["shape"]) for r in d4))
    print("ALL-member first-relator census:", Counter(r["first"] for r in rows).most_common(12))
    print("ALL-member shape census:", Counter(tuple(r["shape"]) for r in rows).most_common(12))
    Path(REPO / args.out).write_text(json.dumps(
        {"record": "s21_audit_scan", "args": vars(args), "rows": rows}, indent=1))
    print("wrote", args.out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["defects", "scan"], default="defects")
    ap.add_argument("--cap", type=int, default=2_000_000)
    ap.add_argument("--rank4", action="store_true")
    ap.add_argument("--n", type=int, default=240)
    ap.add_argument("--lo", type=int, default=11)
    ap.add_argument("--hi", type=int, default=18)
    ap.add_argument("--seed", type=int, default=20260804)
    ap.add_argument("--all-rank2", action="store_true")
    ap.add_argument("--out", default="results/stable_ac/fable/s21_audit_defects.json")
    args = ap.parse_args()
    (cmd_defects if args.mode == "defects" else cmd_scan)(args)


if __name__ == "__main__":
    main()
