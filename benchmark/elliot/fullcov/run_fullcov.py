"""Elliot Steffen's three searches with the full CoV family in place of their CoV steps, on our benchmarks.

    python -m benchmark.elliot.fullcov.run_fullcov --budget 100000 --out results/elliot_fullcov_1e5 --workers 190
    python -m benchmark.elliot.fullcov.run_fullcov --budget 10000000 --from results/elliot_fullcov_1e5 --out ...

The searches (ported engines, ``engine.py``; same parameters as the paper config of ACSolverES, no length bound):

    dual_single_cov   sub queue + one CoV queue: every CoV image (was: single CoV)
    dual_auto_cov     sub queue + one CoV queue: the 24 auto-CoV maps, then every CoV image (was: the 24 maps)
    triple            sub queue + auto queue (24 maps) + CoV queue: every CoV image (was: complete CoV, behind a
                      composite-count filter); every pop is charged, including a CoV pop with no image

One unit is one pop of any queue. The search is deterministic and the budget only stops it, so a row solved in u
units is solved at every budget >= u; ``--from`` carries those rows. Writes ``<out>/<bench>__<algo>.jsonl``.
"""
import argparse
import json
import os
import resource
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

os.environ.setdefault("NUMBA_NUM_THREADS", "1")
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from benchmark.elliot.run_elliot import load_bench  # noqa: E402
from benchmark.elliot.fullcov.engine import from_xy, run_dual, run_triple, to_xy  # noqa: E402
from benchmark.elliot.fullcov.expanders import auto_cov, full_cov, union  # noqa: E402

ALGOS = ("dual_single_cov", "dual_auto_cov", "triple")
PARAMS = dict(threshold=2, seed=True, min_gap=0)


def images_fn():
    """The shared function ``acx.cov.states.cov_states``: every CoV image of a state, 2 <= |w| <= |r| - 1, one per
    class (relator order, rotation, inversion, the 8 signed relabellings), no length limit."""
    from acx.cov.states import cov_states
    return lambda pres: cov_states(*pres.rels)


def search(algo, start, budget):
    cov = full_cov(images_fn())
    if algo == "dual_single_cov":
        return run_dual(start, cov, budget, None, **PARAMS)
    if algo == "dual_auto_cov":
        return run_dual(start, union(auto_cov(), cov), budget, None, **PARAMS)
    return run_triple(start, auto_cov(), cov, budget, None, seed_auto=True, seed_cov=True, cov_prefilter=None,
                      charge_empty_cov_pops=True)


def _move_record(move, frm, to):
    out = {"from": [to_xy(w) for w in frm], "to": [to_xy(w) for w in to], "move_type": move["move_type"]}
    if move["move_type"] == "full_cov":
        out.update({k: move[k] for k in ("w", "gen", "iso_index", "expr", "substituted", "n_subs", "aut")})
        out["w"] = to_xy(out["w"])
    elif move["move_type"] == "auto_cov":
        out["automorphism"] = move["automorphism"]
    return out


def run_one(algo, budget, pid, r1, r2):
    rec = {"algo": algo, "id": pid, "r1": r1, "r2": r2, "budget": budget}
    try:
        t0 = time.perf_counter()
        res = search(algo, (from_xy(r1), from_xy(r2)), budget)
        rec["seconds"] = round(time.perf_counter() - t0, 3)
        rec.update({k: res[k] for k in ("solved", "nodes", "sub_pops", "cov_pops", "cc_pops", "cc_empty_pops",
                                        "cov_generated", "cov_enqueued", "seen", "max_seen_total")})
        rec["units"] = res["nodes"]
        if res["solved"]:
            states, moves = res["path"], res["moves"]
            kinds = {}
            for m in moves:
                k = m["move_type"] if m["move_type"] != "full_cov" else ("full_cov_aut" if m["aut"] else "full_cov_stable")
                kinds[k] = kinds.get(k, 0) + 1
            rec.update(
                path_length=len(moves),
                sub_moves=kinds.get("standard_substitution", 0),
                cov_moves=len(moves) - kinds.get("standard_substitution", 0),
                move_kinds=kinds,
                kind="stable_cert" if kinds.get("full_cov_stable") else "ac_path",
                max_relator_len=max(max(len(a), len(b)) for a, b in states),
                max_total_len=max(len(a) + len(b) for a, b in states),
                path=[[to_xy(a), to_xy(b)] for a, b in states],
                cov_used=[_move_record(m, states[i], states[i + 1]) for i, m in enumerate(moves)
                          if m["move_type"] != "standard_substitution"],
                moves=[m["move_type"] for m in moves],
            )
    except MemoryError:
        rec["error"] = "MemoryError"
    except Exception:
        rec["error"] = traceback.format_exc()
    rec["peak_rss_mb"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024
    return rec


def read_jsonl(path):
    """The records of a results file; a line cut short by a kill (the last one) is skipped and rerun."""
    if not path.exists():
        return []
    out = []
    for line in path.read_text().splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return out


def _init(mem_gb):
    if mem_gb:
        lim = int(mem_gb * 2**30)
        resource.setrlimit(resource.RLIMIT_AS, (lim, lim))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--benches", default="ms640,bench60,ladder100")
    ap.add_argument("--algos", default=",".join(ALGOS))
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--mem-gb", type=float, default=0, help="address-space limit per worker (0: none)")
    ap.add_argument("--from", dest="base", default=None)
    ap.add_argument("--ids", default=None, help="comma-separated row ids to run (default all)")
    a = ap.parse_args()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    only = set(a.ids.split(",")) if a.ids else None
    carried, jobs = [], []
    for bench in a.benches.split(","):
        rows = load_bench(bench)
        for algo in a.algos.split(","):
            f = out / f"{bench}__{algo}.jsonl"
            done = {r["id"] for r in read_jsonl(f)}
            base = {}
            if a.base:
                base = {r["id"]: r for r in read_jsonl(Path(a.base) / f"{bench}__{algo}.jsonl") if "error" not in r}
            for pid, r1, r2 in rows:
                if pid in done or (only and pid not in only):
                    continue
                prev = base.get(pid)
                if prev is not None and prev["solved"] and prev["units"] <= a.budget:
                    carried.append((bench, algo, dict(prev, budget=a.budget, carried_from=str(a.base))))
                else:
                    jobs.append((bench, algo, pid, r1, r2))

    handles = {}

    def write(bench, algo, rec):
        rec["bench"] = bench
        if (bench, algo) not in handles:
            f = out / f"{bench}__{algo}.jsonl"
            handles[bench, algo] = f.open("a")
            if f.stat().st_size and not f.read_bytes().endswith(b"\n"):
                handles[bench, algo].write("\n")
        handles[bench, algo].write(json.dumps(rec) + "\n")
        handles[bench, algo].flush()

    for bench, algo, rec in carried:
        write(bench, algo, rec)
    unique = {}
    for bench, algo, pid, r1, r2 in jobs:
        unique.setdefault((algo, r1, r2), []).append((bench, pid))
    print(f"{len(carried)} rows carried, {len(jobs)} rows to search, {len(unique)} distinct searches", flush=True)
    # the longest searches first, so the pool does not end on one straggler
    order = sorted(unique.items(), key=lambda kv: -(len(kv[0][1]) + len(kv[0][2])))
    with ProcessPoolExecutor(a.workers, initializer=_init, initargs=(a.mem_gb,)) as ex:
        futs = {ex.submit(run_one, algo, a.budget, uses[0][1], r1, r2): (algo, uses) for (algo, r1, r2), uses in order}
        for n, fut in enumerate(as_completed(futs), 1):
            algo, uses = futs[fut]
            rec = fut.result()
            for bench, pid in uses:
                write(bench, algo, dict(rec, id=pid))
            print(n, algo, [u[1] for u in uses], rec.get("solved"), rec.get("units"), rec.get("seconds"),
                  rec.get("peak_rss_mb"), (rec.get("error") or "")[-200:], flush=True)
    for h in handles.values():
        h.close()


if __name__ == "__main__":
    main()
