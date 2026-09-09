"""Derive the AC19 10M-stage row lists from the two 5M jsonls -- never by hand.

THE LADDER
----------
Every AC19 stage's row list is what the previous stage left unsolved, read
off that stage's jsonl and re-derived by a test rather than trusted:

    unsolved_10k_*   -> unsolved_100k_*  -> unsolved_1m_*  -> unsolved_5m_*
    (the screen)        (100k, cap 48)      (1M, cap 48)      (5M, cap 64)

This module writes the last rung: ``unsolved_5m_baseline.csv`` (every row
the greedy arm failed at 5M) and ``unsolved_5m_s20_mk2.csv`` (every row the
s20_mk2 arm failed at 5M), same schema as every earlier list, plus the
``.txt`` name lists and ``UNSOLVED_AFTER_5M.md`` with the accounting.
``CAMPAIGNS["ac19_10m"]`` in ``run_leftovers_5m`` runs them at 10M.

THE ACCOUNTING
--------------
The greedy list is NOT the residual set. s20_mk2's 5M list was, by
construction, its own 1M failures (14 rows), so a greedy 5M failure that
s20_mk2 "did not search at 5M" is a row s20_mk2 had already solved at an
earlier rung -- at 1M, at 100k, or at the 10k screen -- and a solved
presentation stays solved. The residue unsolved by every arm at every
budget is the s20_mk2 list. ``derive()`` names the rung at which s20_mk2
solved each of the others, and refuses to write anything if a greedy
failure cannot be accounted for (the one row s20_mk2 never searched,
``ac19_33435`` of ``COMMON_DENOMINATOR_EXCLUDED``, would show up here as
``never searched`` -- it does not, because greedy solved it at 5M).

    PYTHONPATH=. python3 -m experiments.search.make_ac19_10m_lists          # write
    PYTHONPATH=. python3 -m experiments.search.make_ac19_10m_lists --check  # drift?
"""
from __future__ import annotations

import argparse
import csv
import io
import os

from experiments.search.run_leftovers_1m import (
    ARMS, COMMON_DENOMINATOR_EXCLUDED, HARD100K_DIR, SCREEN_DIR, read_rows,
)

RESULTS_5M_DIR = os.path.join(os.path.dirname(SCREEN_DIR), "leftovers_5m")
RESULTS_1M_DIR = os.path.join(os.path.dirname(SCREEN_DIR), "leftovers_1m")

JSONL_5M = {"greedy": "leftovers_5m_greedy_b5000000_mrl64.jsonl",
            "s20_mk2": "leftovers_5m_s20_mk2_b5000000_mrl64.jsonl"}
JSONL_1M = {"greedy": "leftovers_1m_greedy_b1000000_mrl48.jsonl",
            "s20_mk2": "leftovers_1m_s20_mk2_b1000000_mrl48.jsonl"}
LIST_1M = {"greedy": "unsolved_1m_baseline.csv",
           "s20_mk2": "unsolved_1m_s20_mk2.csv"}
LIST_10K = {"greedy": "unsolved_10k_baseline.csv",
            "s20_mk2": "unsolved_10k_s20_mk2.csv"}
OUT_CSV = {"greedy": "unsolved_5m_baseline.csv",
           "s20_mk2": "unsolved_5m_s20_mk2.csv"}
OUT_MD = "UNSOLVED_AFTER_5M.md"

# the schema every rung of the ladder has used
FIELDS = ["name", "r1", "r2", "n_members", "members", "nodes_explored",
          "min_relator_length"]

BUDGET_5M = 5_000_000
NODES_EXPLORED_KEY = "nodes_explored"


def latest_by_name(records):
    """One record per name: a finished record beats an error record, and
    among finished records the later one wins (a retried row's second
    completion, if there ever were one, would be the same search)."""
    best = {}
    for r in records:
        n = r.get("name")
        if n is None:
            continue
        prev = best.get(n)
        if prev is None or (prev.get("error") and not r.get("error")):
            best[n] = r
        elif not prev.get("error") and not r.get("error"):
            best[n] = r
    return best


def _csv_rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _need(path):
    rows = read_rows(path)
    if not rows:
        raise FileNotFoundError(f"missing or empty: {path}")
    return rows


def derive(results_5m_dir=RESULTS_5M_DIR, results_1m_dir=RESULTS_1M_DIR,
           screen_dir=SCREEN_DIR, hard100k_dir=HARD100K_DIR):
    """``{"rows": {arm: [csv rows]}, "accounting": [...], "counts": {...}}``.

    Pure: reads the jsonls and lists, writes nothing. Raises if the 5M
    stage is not settled (an outstanding error record) or a greedy failure
    cannot be placed on the ladder."""
    five = {arm: latest_by_name(_need(os.path.join(results_5m_dir, f)))
            for arm, f in JSONL_5M.items()}
    for arm, recs in five.items():
        bad = sorted(n for n, r in recs.items() if r.get("error"))
        if bad:
            raise RuntimeError(f"{arm} 5M stage not settled; error records "
                               f"outstanding for {bad}")
        wrong = sorted(n for n, r in recs.items()
                       if not r.get("solved")
                       and int(r.get(NODES_EXPLORED_KEY, 0)) != BUDGET_5M)
        if wrong:
            raise RuntimeError(f"{arm}: unsolved rows that did not run the "
                               f"full {BUDGET_5M:,}: {wrong}")
    one = {arm: latest_by_name(_need(os.path.join(results_1m_dir, f)))
           for arm, f in JSONL_1M.items()}
    s20_100k = latest_by_name(_need(os.path.join(hard100k_dir,
                                                 ARMS["s20_mk2"]["jsonl"])))
    s20_10k_unsolved = {r["name"] for r in
                        _csv_rows(os.path.join(screen_dir, LIST_10K["s20_mk2"]))}
    never = set(COMMON_DENOMINATOR_EXCLUDED.get("greedy", ()))

    # orbit columns come from the 1M lists (every 5M row is on one of them)
    orbit = {}
    for arm, f in LIST_1M.items():
        for r in _csv_rows(os.path.join(screen_dir, f)):
            orbit.setdefault(r["name"], r)

    rows, unsolved = {}, {}
    for arm in ("greedy", "s20_mk2"):
        names = sorted(n for n, r in five[arm].items() if not r.get("solved"))
        unsolved[arm] = set(names)
        out = []
        for n in names:
            r = five[arm][n]
            o = orbit.get(n)
            if o is None:
                raise RuntimeError(f"{n} is on no 1M list; the 5M jsonl and "
                                   f"the ladder disagree")
            if (o["r1"], o["r2"]) != (r["r1"], r["r2"]):
                raise RuntimeError(f"{n}: relators differ between the 1M "
                                   f"list and the 5M record")
            out.append({"name": n, "r1": r["r1"], "r2": r["r2"],
                        "n_members": o["n_members"], "members": o["members"],
                        "nodes_explored": int(r[NODES_EXPLORED_KEY]),
                        "min_relator_length": r.get("min_relator_length",
                                                    o["min_relator_length"])})
        rows[arm] = out
    if not unsolved["s20_mk2"] <= unsolved["greedy"]:
        raise RuntimeError("an s20_mk2 5M failure is not a greedy 5M failure: "
                           f"{sorted(unsolved['s20_mk2'] - unsolved['greedy'])}")

    # where on the ladder s20_mk2 settled each greedy 5M failure
    accounting = []
    for n in sorted(unsolved["greedy"]):
        r5 = five["s20_mk2"].get(n)
        r1 = one["s20_mk2"].get(n)
        rh = s20_100k.get(n)
        if r5 is not None and not r5.get("solved"):
            st = ("unsolved", None, None, None)
        elif r5 is not None:
            st = ("solved", "5M", 64, int(r5[NODES_EXPLORED_KEY]))
        elif r1 is not None and r1.get("solved"):
            st = ("solved", "1M", 48, int(r1[NODES_EXPLORED_KEY]))
        elif rh is not None and rh.get("solved"):
            st = ("solved", "100k", 48, int(rh[NODES_EXPLORED_KEY]))
        elif n in never:
            st = ("never searched", None, None, None)
        elif n not in s20_10k_unsolved and r1 is None and rh is None:
            # searched at 10k (the screen's common denominator: exactly the
            # rows in ``never`` were not) and absent from every failure list
            st = ("solved", "10k", 48, None)
        else:
            raise RuntimeError(f"{n}: cannot place s20_mk2's result on the "
                               f"ladder")
        status, rung, cap, nodes = st
        accounting.append({"name": n, "status": status, "rung": rung,
                           "cap": cap, "nodes": nodes})
    if any(a["status"] == "never searched" for a in accounting):
        raise RuntimeError("a greedy 5M failure was never searched by "
                           "s20_mk2; the residual set is larger than the "
                           "s20_mk2 list and needs a decision, not a script")
    counts = {"greedy_rows": len(five["greedy"]),
              "greedy_solved": sum(1 for r in five["greedy"].values()
                                   if r.get("solved")),
              "greedy_unsolved": len(unsolved["greedy"]),
              "s20_rows": len(five["s20_mk2"]),
              "s20_solved": sum(1 for r in five["s20_mk2"].values()
                                if r.get("solved")),
              "s20_unsolved": len(unsolved["s20_mk2"]),
              "by_rung": {k: sum(1 for a in accounting if a["rung"] == k)
                          for k in ("5M", "1M", "100k", "10k")}}
    return {"rows": rows, "accounting": accounting, "counts": counts}


def render_csv(rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=FIELDS, lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({k: r[k] for k in FIELDS})
    return buf.getvalue()


def render_txt(rows):
    return "".join(r["name"] + "\n" for r in rows)


def render_md(d):
    c = d["counts"]
    by = c["by_rung"]
    L = []
    L.append("# What is still unsolved after budget 5,000,000 (cap 64) -- "
             "the 10M run list\n")
    L.append("Generated by `experiments/search/make_ac19_10m_lists.py` from "
             "the two 5M jsonls under\n`../leftovers_5m/`; "
             "`tests/test_leftovers_5m.py` re-derives it. Do not edit by hand.\n")
    L.append("## The two lists\n")
    L.append("| arm | 5M rows | solved | still unsolved @5M | run list |\n"
             "|---|---:|---:|---:|---|")
    L.append(f"| greedy (`baseline`) | {c['greedy_rows']} | {c['greedy_solved']} "
             f"| **{c['greedy_unsolved']}** | [`{OUT_CSV['greedy']}`]"
             f"({OUT_CSV['greedy']}) |")
    L.append(f"| `s20_mk2` (L + 20*S + 2*MK) | {c['s20_rows']} | {c['s20_solved']} "
             f"| **{c['s20_unsolved']}** | [`{OUT_CSV['s20_mk2']}`]"
             f"({OUT_CSV['s20_mk2']}) |\n")
    L.append("`CAMPAIGN=ac19_10m` runs both lists at 10,000,000 nodes, cap 64, "
             "each arm against its own\n(greedy first), the way the 1M and 5M "
             "stages ran: the comparison only means something at\nequal "
             "budget. The s20_mk2 list is the residue unsolved by every arm at "
             "every budget. The\ngreedy list is every greedy 5M failure; the "
             "rows on it that are not on the s20_mk2 list are\nrows s20_mk2 "
             "already solved, at the rung named below "
             f"(5M: {by['5M']}, 1M: {by['1M']}, 100k: {by['100k']}, "
             f"10k screen: {by['10k']}).\nA solved presentation stays solved. "
             "The 9 are a subset of the 31 as presentations, so the two\narms "
             "meet head-to-head on them.\n")
    L.append("## Every greedy 5M failure, and where s20_mk2 settled it\n")
    L.append("| row | s20_mk2 | rung | cap | nodes |\n|---|---|---|---:|---:|")
    for a in d["accounting"]:
        L.append(f"| `{a['name']}` | {a['status']} | {a['rung'] or ''} | "
                 f"{a['cap'] or ''} | "
                 f"{'' if a['nodes'] is None else format(a['nodes'], ',')} |")
    L.append("")
    L.append("## The residue (both arms, every budget)\n")
    L.append("| row | r1 | r2 | min total length reached at 5M |\n|---|---|---|---:|")
    for r in d["rows"]["s20_mk2"]:
        L.append(f"| `{r['name']}` | `{r['r1']}` | `{r['r2']}` | "
                 f"{r['min_relator_length']} |")
    L.append("")
    return "\n".join(L)


def outputs(d, screen_dir=SCREEN_DIR):
    """``{path: content}`` for everything this module writes."""
    out = {}
    for arm, rows in d["rows"].items():
        p = os.path.join(screen_dir, OUT_CSV[arm])
        out[p] = render_csv(rows)
        out[p[:-4] + ".txt"] = render_txt(rows)
    out[os.path.join(screen_dir, OUT_MD)] = render_md(d)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="compare the shipped files with what would be "
                         "written; exit 1 on drift, write nothing")
    ap.add_argument("--screen-dir", default=SCREEN_DIR)
    a = ap.parse_args(argv)
    d = derive(screen_dir=a.screen_dir)
    c = d["counts"]
    print(f"greedy : {c['greedy_rows']} rows, {c['greedy_solved']} solved, "
          f"{c['greedy_unsolved']} unsolved at 5M")
    print(f"s20_mk2: {c['s20_rows']} rows, {c['s20_solved']} solved, "
          f"{c['s20_unsolved']} unsolved at 5M  (the residue)")
    print(f"greedy failures s20_mk2 solved earlier: {c['by_rung']}")
    drift = 0
    for p, content in outputs(d, a.screen_dir).items():
        if a.check:
            have = open(p).read() if os.path.exists(p) else None
            if have != content:
                drift += 1
                print(f"DRIFT: {p}")
            continue
        with open(p, "w") as f:
            f.write(content)
        print(f"wrote {p}")
    if a.check:
        print("check: " + ("PASS" if not drift else f"FAIL ({drift} file(s))"))
        return 1 if drift else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
