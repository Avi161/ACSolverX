"""Check the ported engine against the original: the auto-CoV dual (and the triple with its CoV queue switched off,
which pops by the same rule) must give the committed nodes and path of every row.

    python -m benchmark.elliot.fullcov.check_port results/elliot_100k [--limit N] [--workers 4]
"""
import argparse
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from .engine import from_xy, run_dual, run_triple
from .expanders import auto_cov

MAX_TOTAL = 65


def _empty(state):
    return [], 0, 0


def check(rec):
    start = (from_xy(rec["r1"]), from_xy(rec["r2"]))
    budget = rec["budget"]
    out = {}
    for name, res in (("dual", run_dual(start, auto_cov(MAX_TOTAL), budget, MAX_TOTAL)),
                      ("triple", run_triple(start, auto_cov(MAX_TOTAL), _empty, budget, MAX_TOTAL, seed_cov=False,
                                            charge_empty_cov_pops=False))):
        path = [[from_xy(a), from_xy(b)] for a, b in rec["path"]] if rec["solved"] else None
        out[name] = (res["solved"] == rec["solved"] and res["nodes"] == rec["nodes"]
                     and (not rec["solved"] or [list(s) for s in res["path"]] == path))
    return rec["bench"], rec["id"], rec["nodes"], out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    recs, seen = [], set()
    for f in sorted(Path(a.folder).glob("*__auto_dual.jsonl")):
        for r in map(json.loads, f.read_text().splitlines()):
            if (r["r1"], r["r2"]) not in seen:
                seen.add((r["r1"], r["r2"]))
                recs.append(r)
    recs.sort(key=lambda r: r["nodes"])
    recs = recs[:a.limit]
    bad = []
    with ProcessPoolExecutor(a.workers) as ex:
        for bench, pid, nodes, out in ex.map(check, recs, chunksize=4):
            if not all(out.values()):
                bad.append((bench, pid, nodes, out))
    print(json.dumps({"rows": len(recs), "max_nodes": recs[-1]["nodes"], "mismatches": len(bad), "first": bad[:10]}))


if __name__ == "__main__":
    main()
