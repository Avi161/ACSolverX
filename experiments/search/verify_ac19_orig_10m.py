"""Re-derive every number in ``ac19_orig_10m/RESULTS.md`` from the records.

Nothing here trusts a reported figure. Row lists come from
``make_ac19_orig_10m_lists``, aggregates from ``nodes_explored``, and the
denominator from the ``ac19_10m`` control jsonls.

THE COUNT THAT KEEPS DRIFTING
-----------------------------
The 18 ``s20_mk2`` originals are a strict SUBSET of the 40 ``greedy``
originals, and the 9 ``s20_mk2`` orbits sit inside the 28 ``greedy`` orbits.
So the target set is **28 distinct orbits and 40 distinct originals**. 58 is
the number of (arm x original) CELLS -- 18 originals carry a run from both
arms. Adding 40 and 18 double-counts those 18 presentations.

This has now been got wrong in a commit message and in an external document,
in both cases by people who had the subset written down elsewhere, so
``check_subset`` asserts it and every report prints the three counts side by
side rather than one total.

A FIELD THAT IS NOT A MEASUREMENT
---------------------------------
``max_relator_length`` in these records is the CONFIGURED CAP echoed back --
it reads 64 on every row including rows that solved. The measurements are
``max_relator_length_expanded`` and ``max_relator_length_discovered``. The
cascade records use a third name again, ``max_relator_length_seen``. Read the
wrong one and you conclude the cap bound when it did not.

    PYTHONPATH=. python3 -m experiments.search.verify_ac19_orig_10m
"""
from __future__ import annotations

import json
import os
import statistics
import sys

from experiments.search import make_ac19_orig_10m_lists as mk
from experiments.search.run_leftovers_1m import SCREEN_DIR, read_rows

RESULTS_DIR = os.path.dirname(SCREEN_DIR)
OUT_DIR = os.path.join(RESULTS_DIR, "ac19_orig_10m")
JSONL = {"greedy": "ac19_orig_10m_greedy_b10000000_mrl64.jsonl",
         "s20_mk2": "ac19_orig_10m_s20_mk2_b10000000_mrl64.jsonl"}
CAP = 64
BUDGET = 10_000_000
# Not a measurement -- the configured cap, echoed into every record.
CONFIG_ECHO = "max_relator_length"
MEASURED = ("max_relator_length_expanded", "max_relator_length_discovered")


def check_subset(derived):
    """The 18 are inside the 40, and the 9 orbits inside the 28. Assert it."""
    g = {r["name"] for r in derived["greedy"]}
    s = {r["name"] for r in derived["s20_mk2"]}
    go = {r["orbit"] for r in derived["greedy"]}
    so = {r["orbit"] for r in derived["s20_mk2"]}
    if s - g:
        raise AssertionError(f"s20_mk2 originals outside greedy's: {sorted(s - g)}")
    if so - go:
        raise AssertionError(f"s20_mk2 orbits outside greedy's: {sorted(so - go)}")
    return {"distinct_orbits": len(go | so), "distinct_originals": len(g | s),
            "row_runs": len(g) + len(s), "both_arms": len(g & s),
            "greedy_originals": len(g), "s20_mk2_originals": len(s),
            "greedy_orbits": len(go), "s20_mk2_orbits": len(so)}


def counts_banner(c, log=print):
    log("=== the three counts, never added together ===")
    log(f"  distinct orbits            {c['distinct_orbits']:>4}"
        f"   (greedy {c['greedy_orbits']}, s20_mk2 {c['s20_mk2_orbits']} SUBSET)")
    log(f"  distinct originals         {c['distinct_originals']:>4}"
        f"   (greedy {c['greedy_originals']}, s20_mk2 {c['s20_mk2_originals']} SUBSET)")
    log(f"  (arm x original) row-runs  {c['row_runs']:>4}"
        f"   ({c['both_arms']} originals ran on BOTH arms)")
    log(f"  40 + 18 = 58 is row-runs, NOT presentations. Distinct is "
        f"{c['distinct_originals']}.")


def control(arm):
    """That arm's own 10M records on the representatives -- the denominator."""
    recs = read_rows(mk.JSONL_10M[arm])
    return {r["name"]: r for r in recs}


def verify_arm(arm, derived, log=print):
    path = os.path.join(OUT_DIR, JSONL[arm])
    if not os.path.exists(path):
        log(f"  {arm}: MISSING {JSONL[arm]} -- cannot verify")
        return None
    recs = read_rows(path)
    want = {r["name"]: r for r in derived[arm]}
    names = {r["name"] for r in recs}
    problems = []
    if len(recs) != len(want):
        problems.append(f"{len(recs)} records, expected {len(want)}")
    if names - set(want):
        problems.append(f"extra rows: {sorted(names - set(want))}")
    if set(want) - names:
        problems.append(f"missing rows: {sorted(set(want) - names)}")
    for r in recs:
        row = want.get(r["name"])
        if row and (r["r1"], r["r2"]) != (row["r1"], row["r2"]):
            problems.append(f"{r['name']}: words differ from the derived list")
        if r.get("budget") != BUDGET:
            problems.append(f"{r['name']}: budget {r.get('budget')} != {BUDGET}")
        if r.get(CONFIG_ECHO) != CAP:
            problems.append(f"{r['name']}: cap {r.get(CONFIG_ECHO)} != {CAP}")

    solved = [r for r in recs if r["solved"]]
    nodes = sorted(r["nodes_explored"] for r in solved)
    ctl = control(arm)
    orbits = {want[r["name"]]["orbit"] for r in recs if r["name"] in want}
    bad_ctl = [o for o in orbits
               if o not in ctl or ctl[o]["solved"]
               or ctl[o]["nodes_explored"] != BUDGET
               or ctl[o].get(CONFIG_ECHO) != CAP]
    measured = [r[f] for r in recs for f in MEASURED if f in r]

    log(f"  {arm}:")
    log(f"    records {len(recs)}  solved {len(solved)}  "
        f"orbits behind them {len(orbits)}")
    if nodes:
        log(f"    nodes  min {nodes[0]:,}  p50 {int(statistics.median(nodes)):,}"
            f"  p90 {nodes[int(len(nodes) * 0.9)]:,}  max {nodes[-1]:,}"
            f"  sum {sum(nodes):,}")
    log(f"    control: {len(orbits)} representatives, all exhausted at "
        f"{BUDGET:,} cap {CAP}: {'YES' if not bad_ctl else 'NO ' + str(bad_ctl)}")
    if measured:
        log(f"    measured relator length {min(measured)}-{max(measured)} "
            f"vs cap {CAP}: cap bound on {sum(1 for m in measured if m >= CAP)} rows")
    for p in problems:
        log(f"    PROBLEM {p}")
    return problems


def main(argv=None):
    derived = mk.build()
    counts = check_subset(derived)
    counts_banner(counts)
    print()
    print("=== per-arm re-derivation from the records ===")
    problems, seen = [], 0
    for arm in ("greedy", "s20_mk2"):
        got = verify_arm(arm, derived)
        if got is None:
            continue
        seen += 1
        problems += got
    print()
    if not seen:
        print("  no jsonl present; counts checked, records not")
        return 2
    print(f"  {len(problems)} problem(s)" if problems else "  all checks pass")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
