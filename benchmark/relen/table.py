"""The longest relator on each solution path: mean / median / max over the solved rows, per method and benchmark.

Sources (all in results/):
  LENGTH, S20_MK2   relen/{ms640,ladder}_{length,smk}.jsonl (reruns, run_relen.py) and, for the ladder rows too large
                    to rerun here, relen/stored_paths_all_branches.jsonl (the paths stored by the 5M and 10M runs on
                    branch claude/ac19-leftover-solver-notebook-6yan6d, taken only when their node count equals the
                    row's recorded grading count)
  hybrid            relen/{ms640,ladder}_hybrid.jsonl (hybrid_relen.py: the AC path rewritten from the certificate;
                    each relator cyclically reduced, as on the S-move searches' states)
  CoV gate          ryan_cov_full_1e5 + ryan_cov_full_1e6 (max_relator_len)
  Elliot's three    elliot_fullcov (max_relator_len)
bench60 is read off MS640.

    python benchmark/relen/table.py [--json results/relen/table.json]
"""
import argparse
import csv
import json
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
R = ROOT / "results"
BENCH60 = [r["pres_id"] for r in csv.DictReader((ROOT / "benchmark/subsets/benchmark_subset_60.csv").open())]
LADDER = {m["name"]: m for m in csv.DictReader((ROOT / "benchmark/ladder/ladder_default.csv").open())}


def ryan_load(folders, bench):
    """CoV-gate records by id (as benchmark/ryan/summarize_full.py): a later folder replaces an unsolved row."""
    recs = {}
    for folder in folders:
        f = Path(folder) / f"{'ms640' if bench == 'bench60' else bench}__no_short_sub.jsonl"
        for r in jl(f):
            if r["id"] not in recs or not recs[r["id"]]["solved"]:
                recs[r["id"]] = r
    return [recs[i] for i in BENCH60 if i in recs] if bench == "bench60" else list(recs.values())


def jl(p):
    p = Path(p)
    return [json.loads(l) for l in p.read_text().splitlines()] if p.exists() else []


def by_id(recs, key="id"):
    return {r[key]: r for r in recs}


def stored(arm, col):
    """Stored ladder paths whose node count equals the row's recorded count (greedy or S20_MK2)."""
    out = {}
    for h in jl(R / "relen/stored_paths_all_branches.jsonl"):
        m = LADDER.get(h["name"])
        ok = arm in (h["arm"] or "") and m and m[col + "_solved"] == "1" and h["nodes"] == int(m[col + "_nodes"])
        if ok:
            out[h["name"]] = dict(id=h["name"], solved=True, max_rel=h["max_rel"])
    return out


def greedy(bench, method):
    tag = "length" if method == "LENGTH" else "smk"
    if bench == "ladder100":
        recs = by_id(jl(R / f"relen/ladder_{tag}.jsonl"))
        st_ = stored("greedy" if tag == "length" else "s20", "greedy" if tag == "length" else "s20")
        recs = {k: v for k, v in recs.items() if v.get("solved") and not v.get("mismatch")}
        for k, v in st_.items():
            recs.setdefault(k, v)
        return list(recs.values())
    recs = by_id(jl(R / f"relen/ms640_{tag}.jsonl"))
    return [recs[i] for i in BENCH60 if i in recs] if bench == "bench60" else list(recs.values())


def hybrid(bench):
    recs = {r["id"]: dict(r, max_rel=r["max_rel_cyclic"]) if r.get("solved") else r
            for r in jl(R / f"relen/{'ladder' if bench == 'ladder100' else 'ms640'}_hybrid.jsonl")}
    return [recs[i] for i in BENCH60 if i in recs] if bench == "bench60" else list(recs.values())


def cov_gate(bench):
    b = "ms640" if bench == "MS640" else bench
    return [dict(r, max_rel=r["max_relator_len"]) for r in ryan_load([R / "ryan_cov_full_1e5", R / "ryan_cov_full_1e6"], b)]


def elliot(bench, algo):
    name = {"MS640": "ms640"}.get(bench, bench)
    return [dict(r, max_rel=r["max_relator_len"]) for r in jl(R / f"elliot_fullcov/{name}__{algo}.jsonl")]


METHODS = [("LENGTH", lambda b: greedy(b, "LENGTH")), ("S20_MK2", lambda b: greedy(b, "S20_MK2")),
           ("hybrid", hybrid), ("CoV gate", cov_gate), ("dual, single CoV", lambda b: elliot(b, "dual_single_cov")),
           ("dual, auto CoV", lambda b: elliot(b, "dual_auto_cov")), ("triple", lambda b: elliot(b, "triple"))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    a = ap.parse_args()
    out = []
    for bench in ("MS640", "bench60", "ladder100"):
        for name, f in METHODS:
            v = [r["max_rel"] for r in f(bench) if r.get("solved")]
            row = dict(bench=bench, method=name, n=len(v), mean=round(st.mean(v), 1) if v else None, min=min(v) if v else None,
                       median=st.median(v) if v else None, max=max(v) if v else None)
            out.append(row)
            print(f"{bench:10s} {name:18s} n={row['n']:4d}  {row["mean"]} / {row["median"]} / {row["min"]} / {row["max"]}")
    if a.json:
        Path(a.json).write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
