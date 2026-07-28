"""Best change of variables **and** the tuned heap ordering, together, at one node budget.

The 2x2. Every arm is a single search at the same budget (default 1,000); the two factors are
whether the start is transformed (the best CoV) and whether the heap ordering is the recommended one:

|                | length-only ordering | recommended ordering |
|----------------|----------------------|----------------------|
| original pair  | ``b1k_greedy_*``     | ``b1k_heur_*``       |
| best-CoV pair  | ``b1k_covgreedy_*``  | ``b1k_covheur_*``    |

``b1k_covheur_*`` is the new arm: singly destabilise with the winning ``z``, then search the
transformed pair with ``RECOMMENDED``. Its control is ``b1k_covgreedy_*`` -- **same** start, **same**
per-row cap, ordering the only difference. The two original-pair arms are references, and they carry
a cap confound: a CoV lengthens relators, so a transformed row runs at ``cap = longest + 16`` (24-46
on these 60) while an untransformed one runs at 24. The cap is carried per row as ``cov_cap``.

**The z is an oracle, and it was chosen for the other ordering.** ``bestcov_z`` is the cheapest of
~80-174 subword CoVs, ranked by what *plain greedy* cost at <=20,000 nodes (~2.2M nodes of sweeping
per presentation to find). So ``b1k_covheur_*`` runs the recommended ordering from a start selected
to suit length-only ordering. That makes it a lower bound on a transformed route, not a runnable
procedure, and not a clean measurement of the ordering.

Where the winner comes from -- reproducing ``rebuild_comparison_tables.best_cov_b20k`` exactly, but
keeping the transformed pair it discards:

* 52 rows: the strict-min-nodes CoV row of ``covsweep_10000_66_*.jsonl`` (first seen wins ties).
* 8 rows: the budget-20,000 escalation, whose winner is named by the ``(z_word, iso_gen, iso_index)``
  tie-break on that row's ``provenance`` list.

Four gates, all fatal -- the run refuses to write:

1. the re-derived ``(z, nodes, path, cap, found_at_budget)`` equals the shipped
   ``greedy_vs_bestcov_subset60_nodes_path.csv`` on all 60 rows, and ``iso_gen`` equals
   ``best_iso_gen`` in ``greedy_vs_bestcov_subset60_b10000.csv`` on the 52 b10k rows;
2. ``b1k_greedy_*`` reproduces the ``n_cov = 0`` control row of ``covsweep_1000_66_*.jsonl``
   pop for pop;
3. ``b1k_covgreedy_*`` reproduces that file's row for the winning
   ``(pres_id, z_word, iso_gen, iso_index)`` pop for pop -- which is what proves the right winner
   row was identified: a wrong ``(z, iso_gen, iso_index)`` gives a different transformed pair and a
   different node count;
4. every arm's node count is <= the budget.

``--budget`` moves all four arms together and **renames the output** (``cov_heur_b1k_``,
``cov_heur_b10k_``, ...): the budget changes the result, so it belongs in the filename, never only
in a column. Gates 2 and 3 need a plain-greedy sweep at the same budget; only 1,000 and 10,000 have
one, and any other budget refuses to run unless ``--no-control-gate`` says so out loud.

    .venv/bin/python3 -m experiments.heuristic_search.runners.cov_heur_b1k
    .venv/bin/python3 -m experiments.heuristic_search.runners.cov_heur_b1k --budget 10000
"""

import argparse
import csv
import json
import os
import time

from experiments.heuristic_search.core.hsolve import RECOMMENDED, greedy_search_h

DEFAULT_BUDGET = 1_000
ORIG_CAP = 24            # the ms640 layout's cap, what every untransformed arm runs at

SWEEP_B10K = ("results/stable_ac/cov/"
              "covsweep_10000_66_subnc2pxysb_mrl24_cyc_s60r6_07_20_26.jsonl")
SWEEP_B1K = ("results/stable_ac/cov/"
             "covsweep_1000_66_subnc2pxysb_mrl24_cyc_s60r6_07_20_26.jsonl")
ESCALATION = "results/stable_ac/cov/allcov_escape/allcov_b20000_8rows_subnc2pxysb.jsonl"
BASE_CSV = "results/stable_ac/cov/greedy_vs_bestcov_subset60_b10000.csv"
SHIPPED_CSV = "results/comparison/greedy_vs_bestcov_subset60_nodes_path.csv"
OUT = "results/comparison/cov_heur_{stem}_subset60.csv"

# The plain-greedy control sweeps: same family, same per-row caps, one budget each. Without one at
# the run's budget there is no way to check the winner row was identified correctly.
CONTROL_SWEEP = {1_000: SWEEP_B1K, 10_000: SWEEP_B10K}

ESCALATION_BUDGET = 20_000

FIELDS = [
    "pres_id", "bin", "aut_class", "start_length", "r1", "r2",
    # the CoV that was applied, and everything needed to reapply it
    "cov_z", "cov_iso_gen", "cov_iso_index", "cov_class", "cov_cap",
    "cov_found_at_budget", "cov_r1", "cov_r2", "cov_n_tied_starts",
    # the 2x2, every arm a single search at the run's budget (which is in the FILENAME, not here --
    # the column names keep the b1k_ prefix so a joiner does not have to know the budget to read them)
    "b1k_greedy_solved", "b1k_greedy_nodes", "b1k_greedy_path",
    "b1k_heur_solved", "b1k_heur_nodes", "b1k_heur_path",
    "b1k_covgreedy_solved", "b1k_covgreedy_nodes", "b1k_covgreedy_path",
    "b1k_covheur_solved", "b1k_covheur_nodes", "b1k_covheur_path",
]


def _repo_root():
    d = os.path.abspath(os.path.dirname(__file__))
    while d != "/":
        if os.path.isdir(os.path.join(d, "experiments")) and os.path.isdir(os.path.join(d, "data")):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root not found")


ROOT = _repo_root()


def _jsonl(path):
    with open(os.path.join(ROOT, path)) as fh:
        for ln in fh:
            ln = ln.strip()
            if ln:
                yield json.loads(ln)


def best_cov_winners():
    """pres_id -> the winning CoV row, **with the transformed pair** it produced.

    Identical selection to ``rebuild_comparison_tables.best_cov_b20k`` -- strict ``<`` on nodes so
    the first row seen wins a tie, then the escalation fills only the slots the b10k sweep left
    empty. That function returns the ``z`` and drops the pair; this one keeps the pair, the
    isolation branch and the cap, because re-running the CoV start needs all three.
    """
    best, ties = {}, {}
    for d in _jsonl(SWEEP_B10K):
        if not d["solved"] or d.get("n_cov", 0) == 0:
            continue          # n_cov == 0 is the control row: the ORIGINAL pair, not a CoV
        pid = d["pres_id"]
        cur = best.get(pid)
        if cur is None or d["nodes_explored"] < cur["nodes"]:
            best[pid] = {
                "nodes": d["nodes_explored"], "path": d["path_length"],
                "cap": d["max_relator_length_cap"], "z": d["z_word"],
                "iso_gen": d["iso_gen"], "iso_index": d["iso_index"],
                "r1": d["r1"], "r2": d["r2"],
                "klass": ("relabel" if d["aut_canon_orig"] == d["aut_canon_cov"] else "moved"),
                "found_at": 10_000,
            }
            ties[pid] = set()
        if best[pid]["nodes"] == d["nodes_explored"]:
            # how many distinct transformed starts are equally cheap: a first-seen tie-break is
            # arbitrary among them, so the count is carried rather than hidden
            ties[pid].add((d["r1"], d["r2"]))

    esc = list(_jsonl(ESCALATION))
    for d in esc:
        if not d["solved"]:
            continue
        for pr in sorted(d["provenance"],
                         key=lambda p: (p["z_word"], p["iso_gen"], p["iso_index"])):
            pid = pr["pres_id"]
            cur = best.get(pid)
            # a b10k winner is cheaper than anything that needed >10k, by construction
            if cur is not None and cur["found_at"] == 10_000:
                continue
            if cur is None or (d["nodes_explored"], d["r1"], d["r2"]) < (
                    cur["nodes"], cur.get("r1", ""), cur.get("r2", "")):
                best[pid] = {
                    "nodes": d["nodes_explored"], "path": d["path_length"],
                    "cap": d["cap"], "z": pr["z_word"],
                    "iso_gen": pr["iso_gen"], "iso_index": pr["iso_index"],
                    "r1": d["r1"], "r2": d["r2"],
                    "klass": None,          # filled from the shipped table -- 4 of the 8 moved orbit
                    "found_at": ESCALATION_BUDGET,
                }
                ties[pid] = {(d["r1"], d["r2"])}
    for pid in best:
        best[pid]["n_tied_starts"] = len(ties[pid])
    return best


def gate_winners(best):
    """Gate 1 -- the re-derived winner must be the shipped one, column for column."""
    shipped = {int(r["pres_id"]): r for r in csv.DictReader(open(os.path.join(ROOT, SHIPPED_CSV)))}
    base = {int(r["pres_id"]): r for r in csv.DictReader(open(os.path.join(ROOT, BASE_CSV)))}
    bad = []
    for pid, s in shipped.items():
        w = best.get(pid)
        if w is None:
            bad.append((pid, "no winner derived"))
            continue
        for got, want, what in ((w["z"], s["bestcov_z"], "z"),
                                (str(w["nodes"]), s["bestcov_nodes"], "nodes"),
                                (str(w["path"]), s["bestcov_path"], "path"),
                                (str(w["cap"]), s["bestcov_cap"], "cap"),
                                (str(w["found_at"]), s["bestcov_found_at_budget"], "found_at")):
            if got != want:
                bad.append((pid, f"{what}: derived {got} != shipped {want}"))
        if w["found_at"] == 10_000 and w["iso_gen"] != base[pid]["best_iso_gen"]:
            bad.append((pid, f"iso_gen: derived {w['iso_gen']} != shipped {base[pid]['best_iso_gen']}"))
        if w["klass"] is None:
            w["klass"] = s["bestcov_class"]
        elif w["klass"] != s["bestcov_class"]:
            bad.append((pid, f"class: derived {w['klass']} != shipped {s['bestcov_class']}"))
    if bad:
        raise SystemExit(f"winner gate FAILED on {len(bad)} rows: {bad[:6]}")
    print(f"[covheur] winner gate PASSED: all {len(shipped)} winners match the shipped best-CoV "
          f"columns (z, iso_gen, nodes, path, cap, found_at)")
    return shipped


def _stem(budget):
    """b1k / b10k / b1500 -- the budget as it appears in the output filename."""
    return f"b{budget // 1000}k" if budget % 1000 == 0 else f"b{budget}"


def sweep_control_index(path):
    """The same family run by plain greedy at this budget -- what the length-only arms must match."""
    orig, cov = {}, {}
    for d in _jsonl(path):
        if d.get("n_cov", 0) == 0:
            orig[d["pres_id"]] = d
        else:
            cov[(d["pres_id"], d["z_word"], d["iso_gen"], d["iso_index"])] = d
    return orig, cov


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--budget", type=int, default=DEFAULT_BUDGET,
                    help="node budget for all four arms (default 1000); it renames the output")
    ap.add_argument("--no-control-gate", action="store_true",
                    help="run at a budget with no plain-greedy sweep, skipping gates 2 and 3")
    args = ap.parse_args()
    budget = args.budget

    sweep = CONTROL_SWEEP.get(budget)
    if sweep is None and not args.no_control_gate:
        raise SystemExit(f"no plain-greedy sweep at budget {budget:,} (have "
                         f"{sorted(CONTROL_SWEEP)}), so the winner row cannot be checked. "
                         f"Re-run with --no-control-gate if you accept that.")
    if sweep is None:
        print(f"[covheur] WARNING: no control sweep at budget {budget:,} -- gates 2 and 3 SKIPPED, "
              f"the winner row is unverified")

    best = best_cov_winners()
    shipped = gate_winners(best)
    ctrl_orig, ctrl_cov = sweep_control_index(sweep) if sweep else ({}, {})

    out, drift, over = [], [], []
    t0 = time.time()
    for i, pid in enumerate(sorted(shipped, key=lambda p: int(p))):
        s, w = shipped[pid], best[pid]
        r1, r2, c1, c2, cap = s["r1"], s["r2"], w["r1"], w["r2"], w["cap"]

        g = greedy_search_h(r1, r2, budget, max_relator_length=ORIG_CAP, config=None)
        h = greedy_search_h(r1, r2, budget, max_relator_length=ORIG_CAP, config=RECOMMENDED)
        cg = greedy_search_h(c1, c2, budget, max_relator_length=cap, config=None)
        ch = greedy_search_h(c1, c2, budget, max_relator_length=cap, config=RECOMMENDED)

        # gate 2 -- untransformed length-only must reproduce the sweep's own control row
        ref = ctrl_orig.get(pid) if sweep else None
        if sweep and ref is None:
            drift.append((pid, "orig", "no control row in the sweep"))
        elif ref and (int(ref["nodes_explored"]), bool(ref["solved"])) != (
                int(g["nodes_explored"]), bool(g["solved"])):
            drift.append((pid, "orig", f"{ref['nodes_explored']}/{ref['solved']} != "
                                       f"{g['nodes_explored']}/{g['solved']}"))
        # gate 3 -- the CoV start, length-only, must reproduce the sweep row for THIS winner
        key = (pid, w["z"], w["iso_gen"], w["iso_index"])
        cref = ctrl_cov.get(key) if sweep else None
        if sweep and cref is None:
            drift.append((pid, "cov", f"no sweep row for {key}"))
        elif cref:
            if (cref["r1"], cref["r2"], cref["max_relator_length_cap"]) != (c1, c2, cap):
                drift.append((pid, "cov", f"start/cap mismatch {cref['r1']},{cref['r2']},"
                                          f"{cref['max_relator_length_cap']} != {c1},{c2},{cap}"))
            if (int(cref["nodes_explored"]), bool(cref["solved"])) != (
                    int(cg["nodes_explored"]), bool(cg["solved"])):
                drift.append((pid, "cov", f"{cref['nodes_explored']}/{cref['solved']} != "
                                          f"{cg['nodes_explored']}/{cg['solved']}"))
        # gate 4 -- nothing may exceed the budget
        for tag, res in (("greedy", g), ("heur", h), ("covgreedy", cg), ("covheur", ch)):
            if int(res["nodes_explored"]) > budget:
                over.append((pid, tag, res["nodes_explored"]))

        row = {
            "pres_id": pid, "bin": int(s["bin"]), "aut_class": int(s["aut_class"]),
            "start_length": int(s["start_length"]), "r1": r1, "r2": r2,
            "cov_z": w["z"], "cov_iso_gen": w["iso_gen"], "cov_iso_index": w["iso_index"],
            "cov_class": w["klass"], "cov_cap": cap, "cov_found_at_budget": w["found_at"],
            "cov_r1": c1, "cov_r2": c2, "cov_n_tied_starts": w["n_tied_starts"],
        }
        for tag, res in (("greedy", g), ("heur", h), ("covgreedy", cg), ("covheur", ch)):
            row[f"b1k_{tag}_solved"] = bool(res["solved"])
            row[f"b1k_{tag}_nodes"] = int(res["nodes_explored"])
            row[f"b1k_{tag}_path"] = int(res["path_length"]) if res["solved"] else ""
        out.append(row)
        if (i + 1) % 10 == 0:
            print(f"[covheur] {i+1}/{len(shipped)}  {time.time()-t0:.0f}s", flush=True)

    if drift:
        raise SystemExit(f"control gate FAILED on {len(drift)} checks: {drift[:6]}")
    if over:
        raise SystemExit(f"budget gate FAILED -- {len(over)} searches exceeded {budget}: {over[:6]}")
    if sweep:
        print(f"[covheur] control gate PASSED: both length-only arms reproduce the b"
              f"{budget // 1000}k sweep on all {len(out)} rows")

    dest = os.path.join(ROOT, OUT.format(stem=_stem(budget)))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(out)
    print(f"[covheur] wrote {dest} in {time.time()-t0:.0f}s")

    def med(v):
        v = sorted(v)
        if not v:
            return None
        return (v[len(v) // 2 - 1] + v[len(v) // 2]) / 2 if len(v) % 2 == 0 else v[len(v) // 2]

    summary = {}
    for tag in ("greedy", "heur", "covgreedy", "covheur"):
        sol = [r for r in out if r[f"b1k_{tag}_solved"]]   # column names keep the b1k_ prefix
        # nodes over SOLVED rows only: an unsolved row's node count is the budget, and folding
        # 1,000 into a median would report the ceiling as a cost
        summary[tag] = {"solved": len(sol),
                        "median_nodes_solved": med([r[f"b1k_{tag}_nodes"] for r in sol]),
                        "median_path_solved": med([r[f"b1k_{tag}_path"] for r in sol])}
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
