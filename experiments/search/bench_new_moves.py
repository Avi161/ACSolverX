"""Score the macro move set against the greedy baseline and s20_mk2 on subset-60.

Six arms, one 1,000-node run each per presentation (a budget-B search is the
first B pops of any longer one, so ``solved_at`` yields the whole 100..1000
curve from a single run):

    greedy             baseline substitution greedy, priority = total length
    s20_mk2            same move set, priority = L + 20*S + 2*MK
    recommended        same move set, the shipped RECOMMENDED ordering
    macro_L            substitution + conjugate-donor moves, priority = length
    macro_s20_mk2      substitution + donor, s20_mk2 ordering
    macro_recommended  substitution + donor, RECOMMENDED ordering

The 2x3 grid separates the two effects: a macro-vs-plain column difference at a
fixed ordering is attributable to the MOVE SET; a row difference at a fixed move
set is attributable to the ORDERING. All arms run at the benchmark's cap
(max_relator_length 24, cyclic reduction on).

Honesty rules:

  * every solved macro path is verified by the independent string verifier
    (``certify.verify_solution``) before it is counted — an unverified solve is
    recorded and REPORTED as failed verification, never silently kept;
  * every solved plain-arm path is replayed via ``moves_to_states`` and checked
    to end in a trivial pair;
  * node budgets are pop counts, and macro arms do more work per pop — per-arm
    wall-clock totals and nodes/s are reported next to the solve counts, so the
    equal-nodes and equal-time readings can both be made.

Usage:  python -m experiments.search.bench_new_moves [--budget 1000] [--jobs 4]
Writes: results/new_moves/bench60_newmoves.jsonl (one row per arm x presentation)
        results/new_moves/bench60_newmoves_summary.csv
        results/new_moves/SUMMARY.md
"""
import argparse
import csv
import json
import multiprocessing as mp
import os
import statistics
import time

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUBSET_CSV = os.path.join(_ROOT, "benchmark", "subsets", "benchmark_subset_60.csv")
OUT_DIR = os.path.join(_ROOT, "results", "new_moves")

BUDGET = 1000
CHECKPOINTS = (100, 250, 500, 1000)
MRL = 24

ARMS = (
    "greedy", "s20_mk2", "recommended",
    "macro_L", "macro_s20_mk2", "macro_recommended",
)


def load_rows():
    with open(SUBSET_CSV) as f:
        rows = list(csv.DictReader(f))
    return [{"pres_id": int(r["pres_id"]), "bin": int(r["bin"]),
             "r1": r["r1"], "r2": r["r2"]} for r in rows]


def _run_one(job):
    """(arm, row, budget, goal_smax, subw) -> one jsonl row. Deterministic."""
    arm, row, budget, goal_smax, subw = job
    # imports inside the worker: numba compiles per process, cache=True amortises
    from experiments.search.greedy_baseline import greedy_search, moves_to_states, str_to_move
    from experiments.search.heuristics import RECOMMENDED, S20_MK2, greedy_search_h
    from experiments.search.macro_moves import macro_greedy_search
    from experiments.search.certify import verify_solution

    r1, r2 = row["r1"], row["r2"]
    t0 = time.perf_counter()
    if arm == "greedy":
        res = greedy_search(r1, r2, budget, MRL)
    elif arm == "s20_mk2":
        res = greedy_search_h(r1, r2, budget, MRL, config=S20_MK2)
    elif arm == "recommended":
        res = greedy_search_h(r1, r2, budget, MRL, config=RECOMMENDED)
    elif arm == "macro_L":
        res = macro_greedy_search(r1, r2, budget, MRL, config=None,
                                  goal_smax=goal_smax, donor_subw=subw)
    elif arm == "macro_s20_mk2":
        res = macro_greedy_search(r1, r2, budget, MRL, config=S20_MK2,
                                  goal_smax=goal_smax, donor_subw=subw)
    elif arm == "macro_recommended":
        res = macro_greedy_search(r1, r2, budget, MRL, config=RECOMMENDED,
                                  goal_smax=goal_smax, donor_subw=subw)
    else:
        raise ValueError(arm)
    wall = time.perf_counter() - t0

    out = {
        "arm": arm,
        "pres_id": row["pres_id"],
        "bin": row["bin"],
        "solved": res["solved"],
        "solved_at": res["nodes_explored"] if res["solved"] else None,
        "nodes_explored": res["nodes_explored"],
        "path_length": res["path_length"],
        "wall_s": round(wall, 4),
        "verified": None,
        "verify_reason": None,
        "macro_cost": res.get("macro_cost"),
        "elementary_cost": res.get("elementary_cost"),
        "n_donor_edges": res.get("n_donor_edges"),
    }
    if res["solved"]:
        if arm.startswith("macro_"):
            report = verify_solution(
                r1, r2, [tuple(s) for s in res["path"]],
                [tuple(c) for c in res["path_certs"]])
            out["verified"] = report["ok"]
            out["verify_reason"] = report["reason"]
            out["n_primitives"] = report["n_primitives"]
        else:
            states = moves_to_states(r1, r2, [str_to_move(m) for m in res["path_moves"]])
            last = states[-1]
            out["verified"] = (states == res["path"]
                              and len(last[0]) == 1 and len(last[1]) == 1
                              and last[0].lower() != last[1].lower())
            out["verify_reason"] = None if out["verified"] else "replay mismatch"
    return out


def summarise(rows, budget, checkpoints):
    """Per-arm summary dicts + the markdown table lines."""
    per_arm = {}
    for arm in ARMS:
        sub = [r for r in rows if r["arm"] == arm]
        assert len(sub) == 60, (arm, len(sub))
        solved = [r for r in sub if r["solved"] and r["verified"]]
        unverified = [r for r in sub if r["solved"] and not r["verified"]]
        wall = sum(r["wall_s"] or 0 for r in sub)
        entry = {
            "arm": arm,
            "solved_at_checkpoint": {
                b: sum(1 for r in solved if r["solved_at"] <= b) for b in checkpoints},
            "unverified_solves": len(unverified),
            "lost_jobs": sum(1 for r in sub if r.get("lost")),
            "median_nodes_solved": (statistics.median(r["solved_at"] for r in solved)
                                    if solved else None),
            "median_path": (statistics.median(r["path_length"] for r in solved)
                            if solved else None),
            "total_wall_s": round(wall, 1),
            "nodes_per_s": round(sum(r["nodes_explored"] or 0 for r in sub)
                                 / max(wall, 1e-9)),
        }
        donor_rows = [r for r in solved if (r.get("n_donor_edges") or 0) > 0]
        entry["solves_using_donor_edges"] = len(donor_rows) if arm.startswith("macro_") else None
        per_arm[arm] = entry
    return per_arm


def write_outputs(rows, per_arm, budget, checkpoints, wall_total):
    os.makedirs(OUT_DIR, exist_ok=True)
    jsonl = os.path.join(OUT_DIR, "bench60_newmoves.jsonl")
    with open(jsonl, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    csv_path = os.path.join(OUT_DIR, "bench60_newmoves_summary.csv")
    cols = ["arm"] + [f"solved_at_{b}" for b in checkpoints] + [
        "unverified_solves", "median_nodes_solved", "median_path",
        "solves_using_donor_edges", "total_wall_s", "nodes_per_s"]
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for arm in ARMS:
            e = per_arm[arm]
            w.writerow([arm] + [e["solved_at_checkpoint"][b] for b in checkpoints] + [
                e["unverified_solves"], e["median_nodes_solved"], e["median_path"],
                e["solves_using_donor_edges"], e["total_wall_s"], e["nodes_per_s"]])

    md = os.path.join(OUT_DIR, "SUMMARY.md")
    lines = [
        "# New moves on subset-60 at tiny budgets",
        "",
        f"One {budget:,}-node run per arm per presentation "
        "(`solved_at` gives every smaller budget); cap 24, cyclic reduction on. "
        "Solve counts include ONLY independently verified paths "
        "(`certify.verify_solution` for macro arms, `moves_to_states` replay for "
        "plain arms); unverified solves are listed separately and count as failures.",
        "",
        "| arm | moves | ordering | " +
        " | ".join(f"@{b}" for b in checkpoints) +
        " | median nodes | median path | donor-edge solves | wall s | nodes/s |",
        "|---|---|---|" + "---:|" * (len(checkpoints) + 5),
    ]
    meta = {
        "greedy": ("sub", "L"),
        "s20_mk2": ("sub", "s20_mk2"),
        "recommended": ("sub", "RECOMMENDED"),
        "macro_L": ("sub+donor", "L"),
        "macro_s20_mk2": ("sub+donor", "s20_mk2"),
        "macro_recommended": ("sub+donor", "RECOMMENDED"),
    }
    for arm in ARMS:
        e = per_arm[arm]
        mv, ordr = meta[arm]
        cp = e["solved_at_checkpoint"]
        lines.append(
            f"| {arm} | {mv} | {ordr} | " +
            " | ".join(str(cp[b]) for b in checkpoints) +
            f" | {e['median_nodes_solved']} | {e['median_path']} | "
            f"{'-' if e['solves_using_donor_edges'] is None else e['solves_using_donor_edges']} | "
            f"{e['total_wall_s']} | {e['nodes_per_s']:,} |")
    lines += [
        "",
        f"Total wall time for the whole grid: {wall_total:.0f} s. "
        "Node budgets are pop counts; the macro arms pay more wall time per pop "
        "(see nodes/s), so read the table twice — once at equal nodes, once at "
        "equal time via the nodes/s column.",
        "",
        "Regenerate: `python -m experiments.search.bench_new_moves`.",
    ]
    with open(md, "w") as f:
        f.write("\n".join(lines) + "\n")
    return jsonl, csv_path, md


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=BUDGET)
    # 3 workers, not 4: a saturated macro search peaks over 1 GB of visited
    # states, and the first 4-worker run had one worker OOM-killed.
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--goal-smax", type=int, default=2,
                    help="goal-directed proposer cap for the macro arms; "
                         "0 disables it")
    ap.add_argument("--subw", type=int, nargs=2, default=None, metavar=("LO", "HI"),
                    help="enable the blind cyclic-subword conjugator family "
                         "(the breadth ablation), e.g. --subw 3 4")
    ap.add_argument("--job-timeout", type=int, default=900,
                    help="seconds before one search is recorded as lost")
    args = ap.parse_args()
    checkpoints = tuple(b for b in CHECKPOINTS if b <= args.budget)

    rows = load_rows()
    subw = tuple(args.subw) if args.subw else None
    jobs = [(arm, row, args.budget, args.goal_smax, subw)
            for arm in ARMS for row in rows]
    t0 = time.perf_counter()
    if args.jobs > 1:
        # apply_async + per-future timeout instead of imap: if a worker is
        # OOM-killed, its job is recorded as lost and every other row still
        # lands (an imap chunk on a dead worker hangs the whole run).
        ctx = mp.get_context("spawn")
        with ctx.Pool(args.jobs) as pool:
            futures = [(j, pool.apply_async(_run_one, (j,))) for j in jobs]
            results = []
            for i, (job, fut) in enumerate(futures):
                try:
                    results.append(fut.get(timeout=args.job_timeout))
                except mp.TimeoutError:
                    arm, row = job[0], job[1]
                    print(f"  LOST (timeout): {arm} pres {row['pres_id']}", flush=True)
                    results.append({"arm": arm, "pres_id": row["pres_id"],
                                    "bin": row["bin"], "solved": False,
                                    "solved_at": None, "nodes_explored": None,
                                    "path_length": None, "wall_s": None,
                                    "verified": None, "verify_reason": "job lost",
                                    "macro_cost": None, "elementary_cost": None,
                                    "n_donor_edges": None, "lost": True})
                if (i + 1) % 30 == 0:
                    print(f"  {i + 1}/{len(jobs)} searches done "
                          f"({time.perf_counter() - t0:.0f}s)", flush=True)
    else:
        results = [_run_one(j) for j in jobs]
    wall_total = time.perf_counter() - t0

    results.sort(key=lambda r: (ARMS.index(r["arm"]), r["pres_id"]))
    per_arm = summarise(results, args.budget, checkpoints)
    paths = write_outputs(results, per_arm, args.budget, checkpoints, wall_total)
    for arm in ARMS:
        e = per_arm[arm]
        print(f"{arm:18s} " +
              " ".join(f"@{b}={e['solved_at_checkpoint'][b]}" for b in checkpoints) +
              f"  unverified={e['unverified_solves']}  lost={e['lost_jobs']}"
              f"  wall={e['total_wall_s']}s")
    print("wrote:", *paths, sep="\n  ")


if __name__ == "__main__":
    main()
