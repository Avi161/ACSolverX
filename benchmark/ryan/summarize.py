"""Summarise run_all.py output: per benchmark and gate, solved at each budget and the path / length metrics.

bench60 is read off the MS640 records (its ids are MS640 rows).
  python benchmark/ryan/summarize.py results/ryan_1e5 [--md results/ryan_1e5/SUMMARY_TABLE.md]
"""
import argparse
import csv
import json
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GATES = ("no_short_sub", "short_relator", "unbalanced", "long_presentation", "plateau100", "periodic10")


def load(folder, bench, gate):
    if bench == "bench60":
        ids = [r["pres_id"] for r in csv.DictReader((ROOT / "benchmark/subsets/benchmark_subset_60.csv").open())]
        if not (folder / f"ms640__{gate}.jsonl").exists():
            return []
        recs = {r["id"]: r for r in map(json.loads, (folder / f"ms640__{gate}.jsonl").read_text().splitlines())}
        return [recs[i] for i in ids if i in recs]
    f = folder / f"{bench}__{gate}.jsonl"
    return [json.loads(l) for l in f.read_text().splitlines()] if f.exists() else []


def fmt(xs, d=0):
    if not xs:
        return "-"
    return f"{st.mean(xs):,.{1 if d else 0}f} / {st.median(xs):,.0f} / {max(xs):,}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--md")
    a = ap.parse_args()
    folder = Path(a.folder)
    top = max(json.loads(l)["max_nodes"] for f in folder.glob("*.jsonl") for l in f.read_text().splitlines())
    budgets = [b for b in (10**3, 10**4, 10**5, 10**6, 10**7) if b <= top]
    head = " / ".join(f"1e{len(str(b)) - 1}" for b in budgets)
    lines = [f"| benchmark | gate | rows | solved @{head} | nodes mean / median / max (solved) "
             "| path mean / median / max | CoV moves mean / max | longest relator on path mean / max "
             "| longest relator generated (max) |",
             "|---|---|---:|---|---|---|---|---|---:|"]
    for bench in ("ms640", "bench60", "ladder100"):
        for gate in GATES:
            recs = load(folder, bench, gate)
            if not recs:
                continue
            sol = [r for r in recs if r["solved"]]
            n = [r["nodes_visited"] for r in sol]
            at = " / ".join(str(sum(x <= b for x in n)) for b in budgets)
            cov = [r["path_cov_moves"] for r in sol]
            mr = [r["max_relator_len"] for r in sol]
            gen = max(r.get("max_relator_len_generated", 0) for r in recs)
            lines.append(
                f"| {bench} | {gate} | {len(recs)} | {at} | {fmt(n)} | {fmt([r['path_length'] for r in sol], 1)} "
                f"| {(f'{st.mean(cov):.2f} / {max(cov)}') if cov else '-'} "
                f"| {(f'{st.mean(mr):.1f} / {max(mr)}') if mr else '-'} | {gen} |")
    text = "\n".join(lines)
    print(text)
    if a.md:
        Path(a.md).write_text(text + "\n")


if __name__ == "__main__":
    main()
