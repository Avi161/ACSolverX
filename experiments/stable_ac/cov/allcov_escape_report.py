"""Report on the escalated CoV sweep: which of the eight escape, and at what cost.

Reads only what the escalation run wrote. Every number is a join against the
b10k sweep's raw rows, so the budget is the ONLY thing that differs between the
two verdicts — the per-pair cap and ``cyclic_reduce`` are asserted equal before
anything is counted. Certificates are replayed through ``greedy_tests/spec``,
never through a solver.

    .venv/bin/python3 -m experiments.stable_ac.cov.allcov_escape_report --budget 20000
"""

import argparse
import csv
import json
import os

CSV_B10K = "results/stable_ac/cov/greedy_vs_bestcov_subset60_b10000.csv"
SWEEP_B10K = ("results/stable_ac/cov/"
              "covsweep_10000_66_subnc2pxysb_mrl24_cyc_s60r6_07_20_26.jsonl")
CSV_B1M = "results/comparison/nodes_comparison_subset60.csv"
OUT_DIR = "results/stable_ac/cov/allcov_escape"


def _repo_root():
    d = os.path.abspath(os.path.dirname(__file__))
    while d != "/":
        if os.path.isdir(os.path.join(d, "experiments")) and os.path.isdir(os.path.join(d, "data")):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root not found")


ROOT = _repo_root()


def load_jsonl(path):
    rows = []
    with open(path) as fh:
        for ln in fh:
            ln = ln.strip()
            if ln:
                rows.append(json.loads(ln))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=20000)
    args = ap.parse_args()

    from experiments.stable_ac.cov import allcov_escalate as ae
    from experiments.stable_ac.cov.autcanon_fast import aut_min
    from experiments.stable_ac import verify_results as vr

    tasks, unsolved = ae.build_tasks()
    pres_ids = sorted(int(r["pres_id"]) for r in unsolved)

    # -- gate 1: the resume/provenance key must not collide --------------------
    assert len({(a, b) for (a, b, _c, _p) in tasks}) == len(tasks), \
        "two caps share one (r1,r2): provenance and resume are both unsafe"

    path = os.path.join(ROOT, OUT_DIR,
                        f"allcov_b{args.budget}_8rows_subnc2pxysb.jsonl")
    rows = load_jsonl(path)
    by_pair = {(r["r1"], r["r2"]): r for r in rows}
    assert len(by_pair) == len(rows), "duplicate pair in the escalation jsonl"
    print(f"[report] {len(rows)} pairs at budget {args.budget} "
          f"({len(tasks)} in the family)")
    if len(rows) != len(tasks):
        print(f"[report] WARNING: run incomplete — {len(tasks) - len(rows)} pairs missing")

    # -- gate 2: same pair, same cap, unsolved at 10k --------------------------
    sweep = {}
    for d in load_jsonl(os.path.join(ROOT, SWEEP_B10K)):
        if d["pres_id"] in set(pres_ids):
            sweep[(d["r1"], d["r2"])] = d
    joined = miss = 0
    for k, r in by_pair.items():
        s = sweep.get(k)
        if s is None:
            miss += 1
            continue
        assert s["max_relator_length_cap"] == r["cap"], f"cap differs on {k}"
        assert s["cyclic_reduce"] is True, f"cyclic_reduce differs on {k}"
        assert not s["solved"] and s["nodes_explored"] == 10000, f"{k} solved at 10k"
        joined += 1
    print(f"[report] b10k join: {joined} pairs identical in cap+reduce and "
          f"unsolved at exactly 10,000 nodes ({miss} not in the sweep file)")

    # -- gate 3: every certificate replays through the spec --------------------
    solved = [r for r in rows if r["solved"]]
    for r in solved:
        vr.verify_solved_row(
            {"r1": r["r1"], "r2": r["r2"], "path_length": r["path_length"],
             "max_relator_length_cap": r["cap"], "cyclic_reduce": True},
            r["path_moves"])
    print(f"[report] {len(solved)} certificates replay to the trivial "
          f"presentation through greedy_tests/spec")

    # -- per presentation ------------------------------------------------------
    prov_of = {(a, b): p for (a, b, _c, p) in tasks}
    owned = {p: [] for p in pres_ids}
    for k, r in by_pair.items():
        for pr in prov_of[k]:
            owned[pr["pres_id"]].append((r, pr))

    out_csv = os.path.join(ROOT, OUT_DIR, f"escape_b{args.budget}_summary.csv")
    # a failed start costs exactly the budget, which is what makes the blind
    # restart expectation below a closed form rather than a simulation
    for r in rows:
        assert r["solved"] or r["nodes_explored"] == args.budget, \
            f"unsolved row explored {r['nodes_explored']} != budget"
    # the file carries trailing aggregate rows whose pres_id is a label, not an id
    _b1m = [r for r in csv.DictReader(open(os.path.join(ROOT, CSV_B1M)))
            if r["pres_id"].isdigit()]
    greedy_1m = {int(r["pres_id"]): (r["solved_greedy_b1M"] == "True",
                                     int(r["nodes_greedy_b1M"]) if r["nodes_greedy_b1M"] else None)
                 for r in _b1m}
    heur_100k = {int(r["pres_id"]): int(r["nodes_hsearch_reco_b100k"])
                 for r in _b1m
                 if r["solved_hsearch_reco_b100k"] == "True" and r["nodes_hsearch_reco_b100k"]}

    fields = ["pres_id", "n_cov_tried", "n_cov_solved", "escaped", "best_nodes",
              "best_path", "best_z", "best_iso_gen", "best_iso_index",
              "best_cap", "best_r1", "best_r2", "best_left_orbit",
              "blind_restart_expected_nodes", "greedy_b1M_nodes", "blind_vs_greedy",
              "heur_b100k_nodes"]
    orig = {int(r["pres_id"]): (r["r1"], r["r2"])
            for r in csv.DictReader(open(os.path.join(ROOT, CSV_B10K)))
            if int(r["pres_id"]) in set(pres_ids)}
    orig_orbit = {p: aut_min(orig[p])[1] for p in pres_ids}
    summary = []
    for p in pres_ids:
        got = owned[p]
        sol = [(r, pr) for r, pr in got if r["solved"]]
        best = min(sol, key=lambda t: (t[0]["nodes_explored"], t[0]["r1"], t[0]["r2"])) if sol else None
        row = {"pres_id": p, "n_cov_tried": len(got), "n_cov_solved": len(sol),
               "escaped": bool(sol)}
        if best:
            r, pr = best
            row.update(best_nodes=r["nodes_explored"], best_path=r["path_length"],
                       best_z=pr["z_word"], best_iso_gen=pr["iso_gen"],
                       best_iso_index=pr["iso_index"], best_cap=r["cap"],
                       best_r1=r["r1"], best_r2=r["r2"],
                       best_left_orbit=aut_min((r["r1"], r["r2"]))[1] != orig_orbit[p])
            # Draw this presentation's starts in a uniformly random order and stop
            # at the first that solves. The first success sits at expected position
            # (n+1)/(k+1); every earlier draw costs the full budget.
            n, k = len(got), len(sol)
            trials = (n + 1) / (k + 1)
            mean_solved = sum(r_["nodes_explored"] for r_, _ in sol) / k
            exp_nodes = (trials - 1) * args.budget + mean_solved
            row["blind_restart_expected_nodes"] = round(exp_nodes)
            g_solved, g_nodes = greedy_1m.get(p, (False, None))
            if g_solved and g_nodes:
                row["greedy_b1M_nodes"] = g_nodes
                row["blind_vs_greedy"] = round(g_nodes / exp_nodes, 2)
            if p in heur_100k:
                row["heur_b100k_nodes"] = heur_100k[p]
        summary.append(row)
    with open(out_csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for row in summary:
            w.writerow(row)
    print(f"[report] wrote {out_csv}")

    # -- orbit split of the solving pairs (a relabel is not a no-op) -----------
    orbits_all, orbits_sol = {}, {}
    in_orbit_sol = 0
    for k, r in by_pair.items():
        o = aut_min(k)[1]
        orbits_all[o] = orbits_all.get(o, 0) + 1
        if r["solved"]:
            orbits_sol[o] = orbits_sol.get(o, 0) + 1
            if o in set(orig_orbit.values()):
                in_orbit_sol += 1
    n_in_orbit_all = sum(c for o, c in orbits_all.items() if o in set(orig_orbit.values()))

    print()
    print("  pres    tried solved   best nodes  path   blind restart  greedy b1M   speedup   heur b100k")
    for row in summary:
        if not row["escaped"]:
            print(f"  ms{row['pres_id']}  {row['n_cov_tried']:5d} {row['n_cov_solved']:6d}   no escape")
            continue
        print(f"  ms{row['pres_id']}  {row['n_cov_tried']:5d} {row['n_cov_solved']:6d}   "
              f"{row['best_nodes']:10,}  {row['best_path']:4}   "
              f"{row['blind_restart_expected_nodes']:13,}  "
              f"{row.get('greedy_b1M_nodes', 0):10,}   {row.get('blind_vs_greedy', 0):6.2f}x   "
              f"{row.get('heur_b100k_nodes', 0):10,}")
    print()
    print(f"  pairs             : {len(by_pair)}   solved {len(solved)} "
          f"({100 * len(solved) / len(by_pair):.1f}%)")
    print(f"  distinct orbits   : {len(orbits_all)}   among the solvers {len(orbits_sol)}")
    print(f"  input orbit       : {n_in_orbit_all} pairs "
          f"({100 * n_in_orbit_all / len(by_pair):.1f}%), "
          f"{in_orbit_sol} of the {len(solved)} solves "
          f"({100 * in_orbit_sol / max(len(solved), 1):.1f}%)")
    print(f"  orbits of the 8   : {len(set(orig_orbit.values()))} "
          f"(the eight presentations are one Aut class iff this is 1)")
    nodes = sorted(r["nodes_explored"] for r in solved)
    assert nodes[0] > 10000, "a solve at <=10k contradicts the b10k join"
    print(f"  solve cost, nodes : min {nodes[0]}  median {nodes[len(nodes) // 2]}  max {nodes[-1]}")
    total_nodes = sum(r["nodes_explored"] for r in rows)
    print(f"  total search      : {len(rows)} searches, {total_nodes:,} nodes")


if __name__ == "__main__":
    main()
