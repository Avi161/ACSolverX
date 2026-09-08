"""s40_gen on the 124 u124 rows at a campaign budget, via `mixed_search`.

Why this runner exists. u124 has two zeros against it and they are different
zeros: `s20_mk2` at 10,000,000 nodes (the `u124_10m` campaign) and `s40_gen`
at 10,000 (the cascade's starter ceiling). The second is not a fair test of
`s40_gen` -- it is one ten-thousandth of the first -- and no run has ever sat
between them. This runner does.

It cannot use `cascade_heuristics.search`: that validator refuses a budget
past 100,000. It calls `mixed_search` directly with the `s40_gen` weights,
which has no budget ceiling.

Two things make a campaign budget affordable here:

  capture off  `mixed_search` stores ~95 children per POPPED node, so the
               parent map -- not the search -- is the cost: 50.6 KB per node
               with path capture, 20.0 KB without. Off by default here. A
               solve is re-run once with capture on to recover the
               certificate; the search is deterministic, so it retraces the
               same nodes and stops in the same place.

  cap 255      Memory on this path does not scale with the cap. States are
               Python `bytes`, variable length; nothing is sized at the cap.
               Measured on one row at four caps: 1.061 GiB and 47.11 KB/node
               identical at 48, 64, 128 and 255. Cap 255 costs about 7% wall
               clock (the maxc = 4*(cap+1)^2 scratch buffer is per pop, but
               it amortises over a long search) and nothing in memory. So
               there is no reason to run this narrow, and a filtered child
               leaves no trace -- a cap that binds would hide a solve
               silently.

Every row records `max_relator_length_seen` and `max_popped_total_seen`, so
afterwards the cap question has an answer instead of a shrug. At 10M under
`s20_mk2` five rows reached or crossed the cap of 64 and their verdicts were
undetermined; that must not happen again.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import time

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMBA_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import multiprocessing as mp
import resource

# Recovering a certificate costs KB_PER_NODE_CAPTURE per node of the SOLVE,
# not of the budget, so a row that solves early is free to re-run inline. A
# row that solves late is not: at 2,000,000 nodes capture-on wants ~96 GiB,
# which is larger than any sane lane ceiling and would take the lane down
# after a successful search. Above this the record keeps `nodes_explored` and
# the re-run is deferred to a single-row pass with the whole box to itself.
RECOVER_INLINE_GIB = 8.0

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROWS_CSV = os.path.join(ROOT, "results", "stable_ac", "fable", "aca_124.csv")
S40 = dict(arm="aut_edges", s_weight=40.0, mk_weight=0.0, w_weight=0.0)

# Measured, not assumed. 20.0 KB per popped node with capture off (one u124
# row, 100,000 nodes, fresh process); 50.6 KB with it on. The 0.16 GiB is the
# warm interpreter with numba loaded.
KB_PER_NODE_NOCAPTURE = 20.0
KB_PER_NODE_CAPTURE = 50.6
BASE_GIB = 0.16


def lane_gib(budget, capture=False):
    kb = KB_PER_NODE_CAPTURE if capture else KB_PER_NODE_NOCAPTURE
    return BASE_GIB + budget * kb / 1048576.0


def load_rows(path=None):
    with open(path or ROWS_CSV) as fh:
        return [(r["name"], r["r1"], r["r2"]) for r in csv.DictReader(fh)]


def work(args):
    name, r1, r2, budget, cap = args
    from experiments.search.heuristic_1k import mixed_search
    started = time.time()
    try:
        got = mixed_search((r1, r2), budget=budget, cap=cap, capture=False, **S40)
    except Exception as exc:
        return {"name": name, "r1": r1, "r2": r2, "budget": budget, "cap": cap,
                "error": f"{type(exc).__name__}: {exc}",
                "seconds": round(time.time() - started, 1)}
    record = {
        "name": name, "r1": r1, "r2": r2, "budget": budget, "cap": cap,
        "arm": "s40_gen", "capture": False,
        "solved": bool(got["solved"]),
        "nodes_explored": got["nodes_explored"],
        "start_total": len(r1) + len(r2),
        "min_total_length_seen": got["min_total_length_seen"],
        "max_relator_length_seen": got["max_relator_length_seen"],
        "max_popped_total_seen": got["max_popped_total_seen"],
        "basis_evaluations": got["basis_evaluations"],
        "seconds": round(time.time() - started, 1),
        "peak_rss_gb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                             / 1048576.0, 3),
    }
    # A cap that filtered a child leaves no trace in the record, so say
    # plainly whether anything came close to it rather than implying it.
    record["cap_headroom"] = cap - got["max_relator_length_seen"]
    if not got["solved"]:
        return record
    # The search is deterministic -- no dict or set is ever iterated, and heap
    # ties break on (score, depth, bytes key), which compares lexicographically
    # rather than by hash -- so a capture-on pass retraces the same nodes and
    # stops in the same place. Verified across PYTHONHASHSEED 0/1/12345/99999:
    # identical nodes_explored, solved, min_total, max_relator, max_popped and
    # basis_evaluations. Nothing needs pinning on the box.
    want_gib = got["nodes_explored"] * KB_PER_NODE_CAPTURE / 1048576.0
    record["recover_gib_estimate"] = round(want_gib, 2)
    if want_gib > RECOVER_INLINE_GIB:
        # Solved late. Re-running with capture here would blow the lane
        # ceiling AFTER the row already succeeded, which is the one failure
        # that would cost us the result rather than a row.
        record["path_deferred"] = True
        record["recover_command"] = (
            f"python -m experiments.search.run_u124_s40 recover "
            f"--name {name} --nodes {got['nodes_explored']} --cap {cap}")
        return record
    again = mixed_search((r1, r2), budget=budget, cap=cap, capture=True, **S40)
    record["path_deferred"] = False
    record["recovered_nodes"] = again["nodes_explored"]
    record["path_matches"] = (again["nodes_explored"] == got["nodes_explored"])
    record["steps"] = [dict(step) for step in again["steps"]]
    record["states"] = [list(state) for state in again["states"]]
    record["certificate_moves"] = len(again["steps"])
    record["aut_assisted"] = any(step.get("kind") == "automorphism"
                                 for step in again["steps"])
    return record


def _init_lane(rlimit_bytes):
    """Cap a lane's ADDRESS SPACE so a runaway row dies alone.

    There is no memory governor on this path -- `plan_memory` and the
    states-per-node floor are hcompact concepts and none of them apply to a
    Python heap. This is the only guard, and it fails closed: a lane that
    exceeds it raises MemoryError inside `work`, which records an `error` row
    and lets the wave continue, instead of the box's OOM killer choosing a
    victim for us.
    """
    if rlimit_bytes:
        resource.setrlimit(resource.RLIMIT_AS, (rlimit_bytes, rlimit_bytes))


def plan(budget, lanes, capture=False, rows_csv=None, log=print):
    rows = load_rows(rows_csv)
    per = lane_gib(budget, capture)
    waves = (len(rows) + lanes - 1) // lanes
    info = {"rows": len(rows), "budget_per_row": budget, "cap_default": 255,
            "capture": capture, "lanes": lanes,
            "gib_per_lane_measured": round(per, 2),
            "gib_resident_all_lanes": round(per * lanes, 1),
            "waves": waves,
            "kb_per_node_measured": (KB_PER_NODE_CAPTURE if capture
                                     else KB_PER_NODE_NOCAPTURE)}
    for rate in (900, 1300, 2000):
        info[f"wall_hours_at_{rate}_nodes_per_s"] = round(
            waves * budget / rate / 3600, 2)
    log(json.dumps(info, indent=2))
    log("\n  Rates bracket the measurement: 930-1,012 nodes/s on a 2.10 GHz")
    log("  Xeon at cap 255, and the campaign box measured 792-870 pops/s per")
    log("  lane on hcompact at campaign length. The perf lab's 3,385 pops/s")
    log("  is hcompact on aca_47 at 300k pops on a faster box -- do not size")
    log("  on it. A worst-case row runs the full budget; most stop earlier.")
    return info


def lane_rlimit_gb(budget, lanes, box_gib=None):
    """Per-lane address-space ceiling: generous against the measurement, but
    small enough that every lane hitting it at once still fits the box."""
    measured = lane_gib(budget)
    if box_gib:
        return max(measured * 1.2, min(measured * 3.0, 0.92 * box_gib / lanes))
    return measured * 3.0


def run(out_path, budget, lanes, cap=255, rows_csv=None, resume=True,
        rlimit_gb=None, box_gib=None, log=print):
    rows = load_rows(rows_csv)
    done = set()
    if resume and os.path.exists(out_path):
        with open(out_path) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    got = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not got.get("error"):
                    done.add(got["name"])
    todo = [(n, a, b, budget, cap) for n, a, b in rows if n not in done]
    log(f"  rows    : {len(rows)}, {len(done)} done, {len(todo)} to run")
    log(f"  budget  : {budget:,} nodes/row at cap {cap}, capture off")
    cap_gb = rlimit_gb or lane_rlimit_gb(budget, lanes, box_gib)
    log(f"  lanes   : {lanes} x {lane_gib(budget):.1f} GiB measured = "
        f"{lane_gib(budget) * lanes:.0f} GiB resident")
    log(f"  guard   : {cap_gb:.1f} GiB address space per lane "
        f"({cap_gb * lanes:.0f} GiB if every lane hit it at once)")
    log(f"  out     : {out_path}")
    if not todo:
        log("  nothing to do")
        return out_path
    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    started, n, solved = time.time(), 0, 0
    with open(out_path, "a") as fh, mp.get_context("fork").Pool(
            lanes, initializer=_init_lane,
            initargs=(int(cap_gb * 2 ** 30),)) as pool:
        for record in pool.imap_unordered(work, todo, chunksize=1):
            fh.write(json.dumps(record) + "\n")
            fh.flush()
            n += 1
            mark = ""
            if record.get("solved"):
                solved += 1
                mark = "   *** SOLVED ***"
            log(f"  [{n}/{len(todo)}] {record['name']:<10} "
                f"start={record.get('start_total')} "
                f"best={record.get('min_total_length_seen')} "
                f"nodes={record.get('nodes_explored', 0):,} "
                f"maxrel={record.get('max_relator_length_seen')} "
                f"maxpop={record.get('max_popped_total_seen')} "
                f"{record.get('seconds')}s{mark}")
    log(f"\n  {solved}/{len(todo)} solved in "
        f"{(time.time() - started) / 60:.1f} min")
    return out_path


def recover(name, nodes, cap=255, rows_csv=None):
    """The certificate for one solved row, re-derived with capture on.

    Deterministic, so running to the recorded node count retraces the same
    search. Given the whole box to itself this is affordable at any budget the
    search actually reached; inside a capped lane it is not, which is why the
    run defers it above `RECOVER_INLINE_GIB`.
    """
    from experiments.search.heuristic_1k import mixed_search
    rows = {n: (a, b) for n, a, b in load_rows(rows_csv)}
    if name not in rows:
        raise SystemExit(f"unknown row {name!r}")
    r1, r2 = rows[name]
    got = mixed_search((r1, r2), budget=nodes, cap=cap, capture=True, **S40)
    if not got["solved"]:
        raise SystemExit(
            f"{name} did not solve inside {nodes:,} nodes on the capture-on "
            "pass; the two runs disagree and that must be understood before "
            "the certificate is trusted")
    return {"name": name, "r1": r1, "r2": r2, "nodes_explored": nodes,
            "reproduced_at": got["nodes_explored"],
            "matches": got["nodes_explored"] == nodes,
            "certificate_moves": len(got["steps"]),
            "aut_assisted": any(s.get("kind") == "automorphism"
                                for s in got["steps"]),
            "states": [list(s) for s in got["states"]],
            "steps": [dict(s) for s in got["steps"]]}


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=("plan", "run", "recover"))
    ap.add_argument("--budget", type=int, default=2_000_000)
    ap.add_argument("--cap", type=int, default=255,
                    help="per-relator insertion cap. Memory does not scale "
                         "with it on this path; 255 is the largest value the "
                         "sibling hcompact validator accepts and above it the "
                         "kernel is untested.")
    ap.add_argument("--lanes", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument("--out", default="u124_s40_campaign.jsonl")
    ap.add_argument("--rows-csv", default=None)
    ap.add_argument("--no-resume", action="store_true")
    ap.add_argument("--lane-rlimit-gb", type=float, default=None,
                    help="per-lane address-space ceiling; default is 3x the "
                         "measured need, clipped so every lane hitting it at "
                         "once still fits --box-gib")
    ap.add_argument("--box-gib", type=float, default=None,
                    help="usable RAM, used only to clip the lane ceiling")
    ap.add_argument("--name", default=None, help="recover: which row")
    ap.add_argument("--nodes", type=int, default=None,
                    help="recover: the solve's recorded nodes_explored")
    args = ap.parse_args(argv)
    if args.cap > 255:
        raise SystemExit(
            f"cap {args.cap} above 255: `mixed_search` accepts it but the "
            "kernel's length fields are uint8-shaped and nothing has ever "
            "pushed a word past 255 on this path. Gate it before using it.")
    if args.command == "plan":
        plan(args.budget, args.lanes, rows_csv=args.rows_csv)
    elif args.command == "recover":
        if not (args.name and args.nodes):
            raise SystemExit("recover needs --name and --nodes")
        print(json.dumps(recover(args.name, args.nodes, cap=args.cap,
                                 rows_csv=args.rows_csv), indent=1))
    else:
        run(args.out, args.budget, args.lanes, cap=args.cap,
            rows_csv=args.rows_csv, resume=not args.no_resume,
            rlimit_gb=args.lane_rlimit_gb, box_gib=args.box_gib)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
