"""Derive the rows that failed the 10k screen and were never escalated.

WHAT THESE ROWS ARE
-------------------
The 2026-07-31 Colab wave judged 71,556 of the 72,779 orbits on greedy and
71,582 on s20_mk2. Every rung above it -- 100k, 1M, 5M, 10M -- ran a list built
from what that wave saw, so an orbit it never judged could not appear on any of
them. `ac19_autmin_10k` then re-ran both arms over ALL 72,779, and a handful of
those previously unjudged rows failed at 10,000 nodes with nothing above them.

    greedy   12 rows      s20_mk2   1 row

That is the entire residue of the coverage gap. Every other row in the campaign
either has a measured cost or is censored at a stated budget; these 13 are the
only ones the deck can say nothing about except "unmeasured", which is why they
get their own list and their own rung rather than a footnote.

The single s20_mk2 row is not a random one. `ac19_33435` is the orbit
`run_leftovers_1m.COMMON_DENOMINATOR_EXCLUDED` names -- the one row outside the
70,723 both arms searched at 10k -- so it is the coverage gap's own documented
example, arriving here from the other end.

NONE OF THE 13 IS A HARD PRESENTATION
-------------------------------------
They are one arm's blind spots, not the campaign's residue. The cascade settles
all 13 (54 to 23,393 nodes, eleven of them under 700), and s20_mk2 settles 11 of
greedy's 12 inside 10,000 nodes. So a 100,000-node rung should close most of
them, and a row that survives it is interesting rather than expected.

    PYTHONPATH=. python3 -m experiments.search.make_ac19_unescalated_lists
    PYTHONPATH=. python3 -m experiments.search.make_ac19_unescalated_lists --check
    PYTHONPATH=. python3 -m experiments.search.make_ac19_unescalated_lists --write
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

RES = os.path.join(ROOT, "results", "heuristic_search")
SCREEN_DIR = os.path.join(RES, "ac19_autmin_screen")
ORBITS_CSV = os.path.join(SCREEN_DIR, "ac19_autmin_orbits.csv")

# The ladder, cheapest rung first. Rung 0 is where a row FAILS; rungs 1.. are
# where it would have been escalated to. A row absent from all of 1.. is one no
# later rung ever ran -- which is the definition being derived here, so it is
# read off the files rather than off any stored list.
RUNGS = {
    "greedy": [
        "ac19_autmin_10k/ac19_autmin_10k_greedy_b10000_mrl48.jsonl",
        "hsearch_ac19_hard100k/ac19_unsolved10k_baseline_b100000_mrl48.jsonl",
        "leftovers_1m/leftovers_1m_greedy_b1000000_mrl48.jsonl",
        "leftovers_5m/leftovers_5m_greedy_b5000000_mrl64.jsonl",
        "ac19_10m/ac19_10m_greedy_b10000000_mrl64.jsonl",
    ],
    "s20_mk2": [
        "ac19_autmin_10k/ac19_autmin_10k_s20_mk2_b10000_mrl48.jsonl",
        "hsearch_ac19_hard100k/ac19_unsolved10k_s20_mk2_b100000_mrl48.jsonl",
        "leftovers_1m/leftovers_1m_s20_mk2_b1000000_mrl48.jsonl",
        "leftovers_5m/leftovers_5m_s20_mk2_b5000000_mrl64.jsonl",
        "ac19_10m/ac19_10m_s20_mk2_b10000000_mrl64.jsonl",
    ],
}
OUT_CSV = {"greedy": "unescalated_10k_baseline.csv",
           "s20_mk2": "unescalated_10k_s20_mk2.csv"}
# `run_leftovers_1m.load_rows` reads exactly these; min_relator_length is
# optional there and is carried because the 10k run measured it.
FIELDS = ["name", "r1", "r2", "nodes_explored", "min_relator_length"]

EXPECTED = {"greedy": 12, "s20_mk2": 1}


def _records(rel):
    path = os.path.join(RES, rel)
    if not os.path.exists(path):
        raise SystemExit(f"missing rung file: {path}")
    out = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def load_orbits(path=ORBITS_CSV):
    with open(path, newline="") as fh:
        return {r["name"]: r for r in csv.DictReader(fh)}


def derive(arm, orbits=None):
    """The arm's never-escalated rows, sorted by name."""
    rungs = RUNGS[arm]
    orbits = orbits or load_orbits()
    failed, cost = [], {}
    for rec in _records(rungs[0]):
        if rec.get("solved"):
            continue
        failed.append(rec["name"])
        cost[rec["name"]] = rec
    above = set()
    for rel in rungs[1:]:
        above.update(r["name"] for r in _records(rel))
    rows = []
    for name in sorted(set(failed) - above):
        rec = cost[name]
        rows.append({"name": name, "r1": rec["r1"], "r2": rec["r2"],
                     "nodes_explored": rec["nodes_explored"],
                     "min_relator_length": rec["min_relator_length"]})
    return rows


def build():
    orbits = load_orbits()
    return {arm: derive(arm, orbits) for arm in RUNGS}


def render(rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=FIELDS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def check(derived=None):
    """``[]`` when the committed lists match the derivation. Problems otherwise."""
    derived = derived or build()
    problems = []
    for arm, rows in sorted(derived.items()):
        if len(rows) != EXPECTED[arm]:
            problems.append(
                f"{arm}: derived {len(rows)} rows, expected {EXPECTED[arm]} -- "
                "the ladder changed under this list; re-derive deliberately "
                "rather than editing the constant")
        path = os.path.join(SCREEN_DIR, OUT_CSV[arm])
        if not os.path.exists(path):
            problems.append(f"{arm}: {OUT_CSV[arm]} not written yet")
            continue
        want = render(rows)
        got = open(path).read()
        if got != want:
            problems.append(f"{arm}: {OUT_CSV[arm]} differs from the derivation")
    return problems


def write(derived=None):
    derived = derived or build()
    written = []
    for arm, rows in sorted(derived.items()):
        path = os.path.join(SCREEN_DIR, OUT_CSV[arm])
        with open(path, "w") as fh:
            fh.write(render(rows))
        written.append(path)
        print(f"  {arm:<8} {len(rows):>2} row(s) -> {os.path.relpath(path, ROOT)}")
    return written


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="re-derive and diff against the committed lists")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args(argv)
    derived = build()
    if a.check:
        problems = check(derived)
        for p in problems:
            print("  !!", p)
        print("  OK: lists match the derivation" if not problems
              else f"  {len(problems)} problem(s)")
        return 1 if problems else 0
    if a.write:
        write(derived)
        return 0
    for arm, rows in sorted(derived.items()):
        print(f"{arm}: {len(rows)} never-escalated")
        for r in rows:
            print(f"    {r['name']:<12} {r['r1']:<12} {r['r2']:<16} "
                  f"failed at {r['nodes_explored']:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
