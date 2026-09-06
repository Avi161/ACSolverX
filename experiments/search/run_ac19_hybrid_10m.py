"""Cloud runner and certificate recovery for the three-row hybrid campaign."""
from __future__ import annotations

import argparse
import json
import os

from experiments.search.greedy_baseline import moves_to_states, str_to_move
from experiments.search.run_leftovers_5m import (
    _floor_for, _run_row_isolated, load_rows_5m, out_path_5m, plan_memory,
    read_rows, report_5m, resolve_campaign, run_arm_5m,
)

ARM = "hybrid_10m"
CAMPAIGN = "ac19_hybrid_10m"
BUDGET = 10_000_000
CAP = 255
STATES_PER_NODE = 214
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_OUT = os.path.join(ROOT, "results", "heuristic_search", CAMPAIGN)


def run(out_dir=DEFAULT_OUT, *, workers="auto", limit=None, resume=True,
        log=print):
    return run_arm_5m(
        ARM, out_dir, chunks=1, chunk_index=1, budget=BUDGET, mrl=CAP,
        n_workers=workers, resume=resume, campaign=CAMPAIGN, limit=limit,
        log=log)


def report(out_dir=DEFAULT_OUT, *, log=print):
    return report_5m(
        ARM, out_dir, chunks=1, chunk_index=None, budget=BUDGET, mrl=CAP,
        campaign=CAMPAIGN, log=log)


def certify(out_dir=DEFAULT_OUT, *, log=print):
    source = out_path_5m(ARM, out_dir, 1, 1, BUDGET, CAP, campaign=CAMPAIGN)
    records = {r["name"]: r for r in read_rows(source)
               if r.get("solved") and not r.get("error")}
    rows = {r["name"]: r for r in load_rows_5m(ARM, campaign=CAMPAIGN)[0]}
    target = os.path.join(out_dir, "ac19_hybrid_10m_certificates.jsonl")
    os.makedirs(out_dir, exist_ok=True)
    completed = {r["name"] for r in read_rows(target)
                 if r.get("certified") and not r.get("error")}
    with open(target, "a") as fh:
        _, campaign = resolve_campaign(CAMPAIGN)
        states_per_node = _floor_for(campaign, log)
        for name in sorted(records):
            if name in completed:
                continue
            expected = records[name]
            node_budget = int(expected["nodes_explored"])
            mem_limit, reserve = plan_memory(
                node_budget, CAP, states_per_node=states_per_node,
                track_path=True, log=log)
            rec = _run_row_isolated(
                ARM, rows[name], node_budget, CAP, 60, mem_limit, reserve,
                None, log, track_path=True)
            if rec.get("error"):
                raise RuntimeError(f"certificate rerun failed for {name}: {rec['error']}")
            if not rec.get("solved") or int(rec["nodes_explored"]) != node_budget:
                raise RuntimeError(
                    f"deterministic rerun mismatch for {name}: "
                    f"solved={rec.get('solved')} nodes={rec.get('nodes_explored')} "
                    f"expected={node_budget}")
            moves = [str_to_move(m) for m in rec["path_moves"]]
            states = moves_to_states(rows[name]["r1"], rows[name]["r2"], moves)
            if states != rec["path"]:
                raise RuntimeError(f"stored path does not match move replay for {name}")
            last = states[-1]
            if not (len(last[0]) == len(last[1]) == 1
                    and last[0].lower() != last[1].lower()):
                raise RuntimeError(f"replayed path is not terminal for {name}: {last}")
            rec["certified"] = True
            rec["discovery_record"] = expected
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
            log(f"certified {name}: {node_budget:,} nodes, {len(moves)} moves")
    return target


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", choices=("plan", "smoke", "run", "report", "certify"))
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--workers", default="auto")
    args = ap.parse_args(argv)
    if args.command == "plan":
        _, campaign = resolve_campaign(CAMPAIGN)
        mem, reserve = plan_memory(
            BUDGET, CAP, states_per_node=_floor_for(campaign), track_path=False)
        print(json.dumps({"budget": BUDGET, "cap": CAP,
                          "reserve_states": reserve, "mem_limit_bytes": mem},
                         indent=2))
    elif args.command == "smoke":
        run_arm_5m(
            ARM, args.out_dir + "_smoke", chunks=1, chunk_index=1,
            budget=2_000, mrl=CAP, n_workers=1, resume=False,
            campaign=CAMPAIGN, limit=1)
    elif args.command == "run":
        run(args.out_dir, workers=args.workers)
        report(args.out_dir)
        print(certify(args.out_dir))
    elif args.command == "report":
        report(args.out_dir)
    else:
        print(certify(args.out_dir))


if __name__ == "__main__":
    main()
