"""Fold the budget-20,000 escalation into the cross-arm comparison tables.

Writes two files and runs no search:

* ``results/comparison/greedy_vs_bestcov_subset60_nodes_path.csv`` — new. Greedy
  against best CoV over all 60, on **both** axes (nodes explored and path length).
* ``results/comparison/nodes_comparison_subset60.csv`` — patched in place. The
  eight rows that were blank/False in every best-CoV column are filled from the
  escalation; the b10k-scoped columns (``*_bestcov_b10k``) are left exactly as
  they were, because they are a correct record of that run.

**Why best CoV at budget 20,000 is defined for all 60 with no new search.** A
search at budget ``B`` is exactly the first ``B`` pops of any longer search. So
for a presentation whose best CoV solved in ``n <= 10,000``: that same start
still solves in ``n`` at 20,000, and any start that newly solves must cost more
than 10,000 — hence more than ``n``. The minimum is unchanged. Only the eight
that had *no* solving start at 10,000 can move, and those come from the
escalation file. ``_assert_invariance`` checks this rather than trusting it.

Three things this table does NOT claim, each visible as a column:

* **The caps differ by construction.** The greedy runs at cap 24; a CoV winner
  runs at the cap its transform needs (33–39 here). A CoV lengthens relators, so
  this is not a confound that was closed — it is inherent, and both caps are
  carried per row.
* **The two path lengths are not comparable.** A CoV path is measured from the
  *transformed* pair and is not a certificate for the original. No path-ratio
  column is emitted.
* **Best CoV is an oracle**, the cheapest of ~80–174 searches. ``best_technique``
  already ranked it against single-search arms before this change, so the new
  ``best_technique_is_oracle`` column marks every row where it wins — 35 of them
  predate this run.

    .venv/bin/python3 -m experiments.stable_ac.cov.figures.rebuild_comparison_tables
"""

import csv
import json
import os

SWEEP_B10K = ("results/stable_ac/cov/"
              "covsweep_10000_66_subnc2pxysb_mrl24_cyc_s60r6_07_20_26.jsonl")
ESCALATION = "results/stable_ac/cov/allcov_escape/allcov_b20000_8rows_subnc2pxysb.jsonl"
GREEDY_1M = "results/greedy_baseline/greedy_1000000_640_mrl24_cyc_all_07_11_26.jsonl"
BASE_CSV = "results/stable_ac/cov/greedy_vs_bestcov_subset60_b10000.csv"
NODES_CSV = "results/comparison/nodes_comparison_subset60.csv"
OUT_CSV = "results/comparison/greedy_vs_bestcov_subset60_nodes_path.csv"

ESCALATION_BUDGET = 20_000
ORACLE_ARMS = {"bestcov_b10k", "bestcov_b20k", "stdcov_b1M", "dualcov_b1M"}


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


def best_cov_b20k():
    """pres_id -> the cheapest CoV start solving within 20,000 nodes."""
    best = {}
    for d in _jsonl(SWEEP_B10K):
        if not d["solved"] or d.get("n_cov", 0) == 0:
            continue  # n_cov == 0 is the control row: the ORIGINAL pair, not a CoV
        cur = best.get(d["pres_id"])
        if cur is None or d["nodes_explored"] < cur["nodes"]:
            best[d["pres_id"]] = {
                "nodes": d["nodes_explored"], "path": d["path_length"],
                "cap": d["max_relator_length_cap"], "z": d["z_word"],
                "klass": ("relabel" if d["aut_canon_orig"] == d["aut_canon_cov"] else "moved"),
                "found_at": 10_000,
            }

    from experiments.stable_ac.cov.escape import allcov_escalate as ae
    from experiments.stable_ac.cov.ladder.autcanon_fast import aut_min
    tasks, _unsolved = ae.build_tasks()
    prov_of = {(a, b): p for (a, b, _c, p) in tasks}
    # relabel vs moved has to be derived here, not defaulted: 4 of the 8 escaping
    # winners DO leave the input orbit, so assuming "relabel" mislabels half of them
    orig_orbit = {int(r["pres_id"]): aut_min((r["r1"], r["r2"]))[1]
                  for r in csv.DictReader(open(os.path.join(ROOT, BASE_CSV)))}
    for d in _jsonl(ESCALATION):
        if not d["solved"]:
            continue
        # same tie-break as allcov_escape_report: a pair can carry several
        # provenances, and both files must name the same witness
        for pr in sorted(prov_of[(d["r1"], d["r2"])],
                         key=lambda p: (p["z_word"], p["iso_gen"], p["iso_index"])):
            pid = pr["pres_id"]
            cur = best.get(pid)
            # a b10k winner is cheaper than anything that needed >10k, by
            # construction -- so this can only fill an empty slot
            if cur is not None and cur["found_at"] == 10_000:
                continue
            if cur is None or (d["nodes_explored"], d["r1"], d["r2"]) < (
                    cur["nodes"], cur.get("r1", ""), cur.get("r2", "")):
                best[pid] = {
                    "nodes": d["nodes_explored"], "path": d["path_length"],
                    "cap": d["cap"], "z": pr["z_word"],
                    "r1": d["r1"], "r2": d["r2"],
                    "klass": ("relabel" if aut_min((d["r1"], d["r2"]))[1] == orig_orbit[pid]
                              else "moved"),
                    "found_at": ESCALATION_BUDGET,
                }
    return best


def _assert_invariance(best, base_rows):
    """Every row the b10k table already solved must keep its exact b10k value."""
    n = 0
    for r in base_rows:
        if r["cov_solved"] != "True":
            continue
        pid = int(r["pres_id"])
        assert best[pid]["found_at"] == 10_000, f"{pid}: b10k winner displaced"
        assert best[pid]["nodes"] == int(r["cov_nodes"]), (
            f"{pid}: best CoV nodes moved {r['cov_nodes']} -> {best[pid]['nodes']} "
            f"— a larger budget cannot lower the minimum")
        assert best[pid]["path"] == int(r["cov_path"]), f"{pid}: best CoV path moved"
        n += 1
    print(f"[tables] invariance: {n} rows keep their exact b10k best-CoV nodes and path")


def build_new_csv(best):
    base = list(csv.DictReader(open(os.path.join(ROOT, BASE_CSV))))
    greedy = {d["pres_id"]: d for d in _jsonl(GREEDY_1M)}
    _assert_invariance(best, base)

    fields = ["pres_id", "bin", "aut_class", "start_length", "r1", "r2",
              "greedy_budget", "greedy_cap", "greedy_solved", "greedy_nodes", "greedy_path",
              "bestcov_budget", "bestcov_cap", "bestcov_solved", "bestcov_nodes",
              "bestcov_path", "bestcov_z", "bestcov_class", "bestcov_found_at_budget",
              "bestcov_n_tried", "nodes_greedy_over_bestcov"]
    out = []
    for r in base:
        pid = int(r["pres_id"])
        g, b = greedy[pid], best.get(pid)
        row = {
            "pres_id": pid, "bin": r["bin"], "aut_class": r["aut_class"],
            "start_length": r["start_length"], "r1": r["r1"], "r2": r["r2"],
            "greedy_budget": g["node_budget"], "greedy_cap": g["max_relator_length_cap"],
            "greedy_solved": bool(g["solved"]), "greedy_nodes": g["nodes_explored"],
            "greedy_path": g["path_length"] if g["solved"] else "",
            "bestcov_budget": ESCALATION_BUDGET,
            "bestcov_n_tried": r["n_cov_tried"],
        }
        if b:
            row.update(bestcov_cap=b["cap"], bestcov_solved=True, bestcov_nodes=b["nodes"],
                       bestcov_path=b["path"], bestcov_z=b["z"], bestcov_class=b["klass"],
                       bestcov_found_at_budget=b["found_at"])
            if g["solved"]:
                row["nodes_greedy_over_bestcov"] = round(g["nodes_explored"] / b["nodes"], 2)
        else:
            row.update(bestcov_solved=False, bestcov_cap="", bestcov_nodes="",
                       bestcov_path="", bestcov_z="", bestcov_class="",
                       bestcov_found_at_budget="")
        out.append(row)

    dest = os.path.join(ROOT, OUT_CSV)
    with open(dest, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(out)
    ns = sum(r["greedy_solved"] for r in out)
    bs = sum(r["bestcov_solved"] for r in out)
    print(f"[tables] wrote {OUT_CSV}: {len(out)} rows, greedy {ns}/60, best CoV {bs}/60")
    return out


# -- patching the existing nodes table ----------------------------------------

_ARMS = [("bestcov_b10k", 10_000), ("greedy_b1M", 1_000_000), ("stdcov_b1M", 1_000_000),
         ("dualcov_b1M", 1_000_000), ("hsearch_base_b100k", 100_000),
         ("hsearch_reco_b100k", 100_000), ("greedy_b10k", 10_000),
         ("bestcov_b20k", ESCALATION_BUDGET)]


def _median(v):
    v = sorted(v)
    n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2


def patch_nodes_csv(best):
    path = os.path.join(ROOT, NODES_CSV)
    rows = list(csv.DictReader(open(path)))
    fields = list(rows[0].keys())
    data = [r for r in rows if r["pres_id"].isdigit()]

    for new in ("nodes_bestcov_b20k", "solved_bestcov_b20k", "best_technique_is_oracle"):
        if new not in fields:
            fields.insert(fields.index("best_technique"), new)

    changed = 0
    for r in data:
        pid = int(r["pres_id"])
        b = best.get(pid)
        r["nodes_bestcov_b20k"] = b["nodes"] if b else ""
        r["solved_bestcov_b20k"] = "True" if b else "False"
        if b and not r["nodes_bestcov_b10k"]:
            # this row was blank in every best-CoV column; fill from the escalation
            r["best_z"], r["best_cov_class"] = b["z"], b["klass"]
            for arm, _bud in _ARMS:
                if arm in ("bestcov_b10k", "bestcov_b20k"):
                    continue
                key = f"x_bestcov_{arm}"
                if key in r and r[f"solved_{arm}"] == "True" and r[f"nodes_{arm}"]:
                    r[key] = round(int(r[f"nodes_{arm}"]) / b["nodes"], 2)
            changed += 1
        # Rank every arm this row solved. Best CoV enters once, under the budget
        # that actually found it -- a row whose winner solved at 10,000 keeps the
        # name bestcov_b10k, because relabelling it b20k would imply it needed a
        # budget it never used.
        cand = []
        for arm, _bud in _ARMS:
            if arm in ("bestcov_b10k", "bestcov_b20k"):
                continue
            if r.get(f"solved_{arm}") == "True" and r.get(f"nodes_{arm}"):
                cand.append((int(r[f"nodes_{arm}"]), arm))
        if b:
            cand.append((b["nodes"],
                         "bestcov_b10k" if b["found_at"] == 10_000 else "bestcov_b20k"))
        if cand:
            n, arm = min(cand)
            r["best_technique"], r["best_nodes"] = arm, n
            r["best_technique_is_oracle"] = str(arm in ORACLE_ARMS)

    # trailer aggregates, recomputed -- censored substitutes the arm's own budget
    tr = {r["pres_id"]: r for r in rows if not r["pres_id"].isdigit()}
    for arm, budget in _ARMS:
        nk, sk = f"nodes_{arm}", f"solved_{arm}"
        if nk not in fields:
            continue
        solved = [int(r[nk]) for r in data if r.get(sk) == "True" and r[nk]]
        cens = [int(r[nk]) if r.get(sk) == "True" and r[nk] else budget for r in data]
        if "SOLVED_COUNT" in tr:
            tr["SOLVED_COUNT"][nk] = f"{len(solved)}/{len(data)}"
        if "MEAN_all60_censored" in tr:
            tr["MEAN_all60_censored"][nk] = f"{sum(cens) / len(cens):.1f}"
        if "MEDIAN_all60_censored" in tr:
            tr["MEDIAN_all60_censored"][nk] = f"{_median(cens):.1f}"
        if solved:
            if "MEAN_solved_only" in tr:
                tr["MEAN_solved_only"][nk] = f"{sum(solved) / len(solved):.1f}"
            if "MEDIAN_solved_only" in tr:
                tr["MEDIAN_solved_only"][nk] = f"{_median(solved):.1f}"

    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})
    print(f"[tables] patched {NODES_CSV}: {changed} rows filled from the escalation, "
          f"3 columns added, 5 aggregate rows recomputed")


def main():
    best = best_cov_b20k()
    build_new_csv(best)
    patch_nodes_csv(best)


if __name__ == "__main__":
    main()
