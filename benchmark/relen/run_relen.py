"""Longest relator along each solution path of LENGTH and S20_MK2 (Section 1 runs), for the paper's relator-length table.

Each task reruns one row with the numba backend at its recorded cap and with budget = its recorded pop count (the
search is deterministic, so it reproduces the recorded solve pop for pop; a mismatch is reported). The S-move path (``path``: acx.core.moves.Move tuples
i, j, s, k1, k2) is stored and replayed on the row (acx.verify.replay) and the longest relator and largest total length over its states are stored.

    python benchmark/relen/run_relen.py --bench ladder --method length --out results/relen/ladder_length.jsonl \
        [--min-pops N] [--max-pops N] [--workers W] [--caps 48,64,24] [--mem-gb G] [--gb-per-mpop 13]
"""
import argparse, csv, json, os, sys, time
import multiprocessing as mp
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from acx.data import rows as load_rows  # noqa: E402
from acx.search.engine import search  # noqa: E402
from acx.core.config import SearchConfig  # noqa: E402
from acx.verify.replay import replay  # noqa: E402


def tasks(bench, method, lo, hi, caps):
    out = []
    if bench == "ladder":
        meta = {r["name"]: r for r in csv.DictReader(open(ROOT / "benchmark/ladder/ladder_default.csv"))}
        for row in load_rows("ladder"):
            m = meta[row.id]
            if method == "length":
                if m["greedy_solved"] != "1":
                    continue
                n, cl = int(m["greedy_nodes"]), [int(m["greedy_cap"])]
            else:
                if m["s20_solved"] != "1":
                    continue
                n, cl = int(m["s20_nodes"]), caps
            if lo <= n <= hi:
                out.append((row.id, row.pres.rels, n, cl))
    else:  # ms640: every row, budget = the Section 1 budget, cap 24; the expected pop count is unknown
        budget = 1_000_000 if method == "length" else 100_000
        for row in load_rows("ms640"):
            out.append((row.id, row.pres.rels, budget, [24]))
    return out


def work(args):
    rid, rels, n, caps, method, exact = args
    from acx.core.words import Presentation
    pres = Presentation(2, tuple(tuple(r) for r in rels))
    tried, first = [], None
    for cap in caps:
        t0 = time.time()
        res = search(pres, SearchConfig(priority="length" if method == "length" else "s20_mk2", cap=cap, budget=n,
                                        backend="fast", capture_path=True))
        tried.append((cap, res.solved, res.pops))
        if res.solved:
            states = replay(pres, res.path, cyclic=True, cap=cap)
            rec = dict(id=rid, solved=True, pops=res.pops, expected=n if exact else None, cap=cap,
                       path_length=len(res.path), start_max_rel=max(map(len, states[0].rels)),
                       max_rel=max(max(map(len, s.rels)) for s in states),
                       max_total=max(sum(map(len, s.rels)) for s in states), seconds=round(time.time() - t0, 1),
                       path=[list(m) for m in res.path])
            if not exact or res.pops == n:
                return rec
            first = first or dict(rec, mismatch=True, tried=tried)   # solved, but not the recorded run
    return first or dict(id=rid, solved=False, expected=n if exact else None, tried=tried)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bench", required=True); ap.add_argument("--method", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--min-pops", type=int, default=0); ap.add_argument("--max-pops", type=int, default=10**9)
    ap.add_argument("--caps", default="48,64,24")
    ap.add_argument("--mem-gb", type=float, default=1e9, help="memory budget for all workers together")
    ap.add_argument("--gb-per-mpop", type=float, default=13.0, help="estimated GB per million pops")
    a = ap.parse_args()
    caps = [int(c) for c in a.caps.split(",")]
    T = tasks(a.bench, a.method, a.min_pops, a.max_pops, caps)
    done = set()
    if os.path.exists(a.out):
        done = {json.loads(l)["id"] for l in open(a.out)}
    exact = a.bench == "ladder"
    T = [t + (a.method, exact) for t in T if t[0] not in done]
    T.sort(key=lambda t: -t[2])
    print(f"{len(T)} tasks", flush=True)
    # Memory-aware scheduling: a search holds about gb_per_mpop GB per million pops, so start the largest task that
    # fits in what is left of mem_gb, up to `workers` at once (one process per task, so its memory is returned).
    need = {t[0]: 1 + a.gb_per_mpop * t[2] / 1e6 for t in T}
    ctx = mp.get_context("spawn")
    with ProcessPoolExecutor(a.workers, mp_context=ctx, max_tasks_per_child=1) as ex, open(a.out, "a") as f:
        running, used = {}, 0.0
        while T or running:
            while T and len(running) < a.workers:
                fit = next((t for t in T if used + need[t[0]] <= a.mem_gb), None)
                if fit is None and not running:
                    fit = T[0]                       # too big for the budget: run it alone
                if fit is None:
                    break
                T.remove(fit); used += need[fit[0]]
                running[ex.submit(work, fit)] = fit[0]
            done_f, _ = wait(running, return_when=FIRST_COMPLETED)
            for fu in done_f:
                rid = running.pop(fu); used -= need[rid]
                try:
                    rec = fu.result()
                except Exception as e:               # e.g. a worker killed for memory: record it, keep going
                    rec = dict(id=rid, solved=False, error=repr(e)[:200])
                f.write(json.dumps(rec) + "\n"); f.flush()
                print(rec["id"], rec.get("pops"), rec.get("max_rel"), rec.get("seconds"), rec.get("error", ""),
                      flush=True)

if __name__ == "__main__":
    main()
