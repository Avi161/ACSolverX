"""One record per presentation of MS640 (640 rows, bench60 marked) and ladder100 (100 rows), holding every method's
result on it, so the paper's per-row numbers never have to be gathered or rerun again.

Per method: solved, units (the paper's unit for that method), path_length and max_rel (the longest relator on the
solution path). The paths themselves go to paths/<bench>.jsonl.gz, one line per row, keyed by method, each with its
format (see the README). Sources are listed in table.py.

    python benchmark/relen/build_rows.py --out results/benchmark_rows
"""
import argparse
import csv
import gzip
import json
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from table import BENCH60, LADDER, R, ROOT, by_id, elliot, jl, ryan_load, stored  # noqa: E402

sys.path.insert(0, str(ROOT))
from acx.data import rows as load_rows  # noqa: E402
from acx.core.words import fmt  # noqa: E402

METHODS = ["LENGTH", "S20_MK2", "hybrid", "CoV gate", "dual, single CoV", "dual, auto CoV", "triple"]
UNITS = {"LENGTH": "pops", "S20_MK2": "pops", "hybrid": "S-moves and Nielsen maps",
         "CoV gate": "pops plus gate openings", "dual, single CoV": "pops", "dual, auto CoV": "pops", "triple": "pops"}


def rec(solved, units=None, path_length=None, max_rel=None):
    return dict(solved=bool(solved), units=units, path_length=path_length, max_rel=max_rel) if solved else \
        dict(solved=False)


def greedy_ladder(tag, col):
    rr = {k: v for k, v in by_id(jl(R / f"relen/ladder_{tag}.jsonl")).items() if v.get("solved")}
    stp = {h["name"]: h for h in jl(R / "relen/stored_paths_all_branches.jsonl")}
    keep = stored("greedy" if tag == "length" else "s20", col)
    out = {}
    for name, m in LADDER.items():
        if m[col + "_solved"] != "1":
            out[name] = rec(False)
            continue
        n = int(m[col + "_nodes"])
        r = rr.get(name)
        if r and r["pops"] == n:
            out[name] = rec(True, n, r["path_length"], r["max_rel"])
        elif name in keep:
            h = [x for x in jl(R / "relen/stored_paths_all_branches.jsonl")
                 if x["name"] == name and x["nodes"] == n and (x["arm"] or "").startswith(tag[:1] if tag == "smk" else "greedy")]
            h = h[0] if h else None
            out[name] = rec(True, n, h["plen"] if h else None, keep[name]["max_rel"])
        else:
            out[name] = dict(solved=True, units=n, path_length=None, max_rel=None, missing="no path yet")
    return out


def paths_for(bench, key):
    """{method: {id: {"format": ..., ...}}} from every source that stores a path."""
    P = {m: {} for m in METHODS}
    gmeth = {"length": "LENGTH", "smk": "S20_MK2"}
    for tag, meth in gmeth.items():
        for r in jl(R / f"relen/{key}_{tag}.jsonl"):
            if r.get("solved") and r.get("path") is not None and not r.get("mismatch"):
                P[meth][r["id"]] = dict(format="smoves", cap=r["cap"], path=r["path"])
    if key == "ms640":   # the S20_MK2 MS640 rerun keeps its paths in its run folder
        for r in jl(R / "relen_ms640_smk/paths.jsonl"):
            if r["solved"]:
                P["S20_MK2"].setdefault(r["id"], dict(format="smoves", cap=r["cap"], path=r["path"]))
    else:
        for h in jl(R / "relen/stored_paths_ladder.jsonl"):
            meth = "LENGTH" if h["arm"] == "greedy" else "S20_MK2"
            P[meth].setdefault(h["id"], dict(format="states", cap=h["cap"], path=h["path_states"], source=h["source"]))
    for r in jl(R / f"relen_{key}_hybrid/paths.jsonl"):
        if r["solved"]:
            P["hybrid"][r["id"]] = dict(format="hybrid", certificate=r["steps"], elementary=r["elementary"])
    for r in ryan_load([R / "ryan_cov_full_1e5", R / "ryan_cov_full_1e6"], key if key == "ms640" else bench):
        if r["solved"]:
            P["CoV gate"][r["id"]] = dict(format="cov_gate", kind=r["kind"], path=r["path"])
    for meth, algo in (("dual, single CoV", "dual_single_cov"), ("dual, auto CoV", "dual_auto_cov"),
                       ("triple", "triple")):
        for r in elliot("MS640" if bench == "ms640" else bench, algo):
            if r["solved"]:
                P[meth][r["id"]] = dict(format="elliot", kind=r["kind"], path=r["path"], cov_used=r.get("cov_used"),
                                        moves=r.get("moves"))
    return P


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/benchmark_rows")
    a = ap.parse_args()
    outdir = ROOT / a.out
    outdir.mkdir(parents=True, exist_ok=True)
    b60 = set(BENCH60)
    for bench in ("ms640", "ladder100"):
        key = "ms640" if bench == "ms640" else "ladder"
        rows = load_rows(key)
        M = {}
        if bench == "ms640":
            for tag, meth in (("length", "LENGTH"), ("smk", "S20_MK2")):
                rr = by_id(jl(R / f"relen/ms640_{tag}.jsonl"))
                M[meth] = {i: rec(r.get("solved"), r.get("pops"), r.get("path_length"), r.get("max_rel"))
                           for i, r in rr.items()}
        else:
            M["LENGTH"] = greedy_ladder("length", "greedy")
            M["S20_MK2"] = greedy_ladder("smk", "s20")
        M["hybrid"] = {i: dict(rec(r["solved"], r.get("units"), r.get("steps"), r.get("max_rel_cyclic")),
                               **({"max_rel_search": r["max_rel_search"]} if r["solved"] else {}))
                       for i, r in by_id(jl(R / f"relen/{key}_hybrid.jsonl")).items()}
        M["CoV gate"] = {r["id"]: rec(r["solved"], r.get("units"), r.get("path_length"), r.get("max_relator_len"))
                         for r in ryan_load([R / "ryan_cov_full_1e5", R / "ryan_cov_full_1e6"], key if key == "ms640" else bench)}
        for meth, algo in (("dual, single CoV", "dual_single_cov"), ("dual, auto CoV", "dual_auto_cov"),
                           ("triple", "triple")):
            M[meth] = {r["id"]: rec(r["solved"], r.get("units"), r.get("path_length"), r.get("max_relator_len"))
                       for r in elliot("MS640" if bench == "ms640" else bench, algo)}
        lines = []
        for row in rows:
            d = dict(id=row.id, pres=[fmt(w) for w in row.pres.rels],
                     start_max_rel=max(len(w) for w in row.pres.rels))
            if bench == "ms640":
                d["bench60"] = row.id in b60
            else:
                d["level"] = int(LADDER[row.id]["level"])
            d["methods"] = {m: M[m].get(row.id, dict(solved=None, missing="no record")) for m in METHODS}
            lines.append(d)
        (outdir / f"{bench}.jsonl").write_text("".join(json.dumps(x) + "\n" for x in lines))
        P = paths_for(bench, key)
        (outdir / "paths").mkdir(exist_ok=True)
        with gzip.open(outdir / "paths" / f"{bench}.jsonl.gz", "wt") as g:
            for row in rows:
                g.write(json.dumps(dict(id=row.id, paths={m: P[m][row.id] for m in METHODS if row.id in P[m]})) + "\n")
        nopath = sum(1 for x in lines for m, v in x["methods"].items() if v.get("solved") and x["id"] not in P[m])
        print(bench, nopath, "solved method entries without a path", flush=True)
        miss = sum(1 for x in lines for v in x["methods"].values() if v.get("missing"))
        print(bench, len(lines), "rows;", miss, "method entries still missing", flush=True)
    # Summary over the solved rows, per benchmark (bench60 read off MS640).
    md = ["| benchmark | method | solved | units mean / median / max | path mean / median / max | longest relator mean / median / max |",
          "|---|---|---:|---|---|---|"]
    def s3(v, d=1):
        return f"{st.mean(v):,.{d}f} / {st.median(v):,g} / {max(v):,}" if v else "-"
    for bench, f, keep in (("MS640", "ms640", None), ("bench60", "ms640", b60), ("ladder100", "ladder100", None)):
        recs = jl(outdir / f"{f}.jsonl")
        recs = [r for r in recs if keep is None or r["id"] in keep]
        for m in METHODS:
            sol = [r["methods"][m] for r in recs if r["methods"][m].get("solved")]
            g = lambda k: [x[k] for x in sol if x.get(k) is not None]
            md.append(f"| {bench} | {m} | {len(sol)} / {len(recs)} | {s3(g('units'), 0)} | {s3(g('path_length'))} "
                      f"| {s3(g('max_rel'))} |")
    (outdir / "SUMMARY.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
