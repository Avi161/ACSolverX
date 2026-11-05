"""Summarise run_full.py output beside Ryan's CoV-gate row (results/ryan_full_1e6, gate no_short_sub).

Budgets are in units: one per pop plus one per gate opening (``units``); the pops-only count (``nodes_visited``, as in
Ryan's code and the paper's CoV gate row) is shown too. Ryan's own row is recounted in both.

Two tags per solve:
  orbit   every CoV step's child is in its parent's Aut(F2) orbit (checked; verify_full.py rechecks it) -> AC path;
  one-z   every CoV step's isolating relator holds exactly one z. Then g = s z^{+-1} t is an automorphism of
          F(other, z), and each substitution w -> z in the other relator changes it by a conjugate of the isolating
          relator (an AC move), so the step is AC as well (argument from the Elliot full-CoV thread; not replayed).

  python benchmark/ryan/summarize_full.py results/ryan_cov_full_1e5 [results/ryan_cov_full_1e6] [--md OUT.md]
"""
import argparse
import csv
import json
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUDGETS = (10**3, 10**4, 10**5, 10**6)


def load(folders, bench):
    """Records by id; a later folder (a rerun of the unsolved rows at a larger budget) replaces an unsolved row."""
    name = "ms640" if bench == "bench60" else bench
    recs = {}
    for folder in folders:
        f = Path(folder) / f"{name}__no_short_sub.jsonl"
        if not f.exists():
            continue
        for r in map(json.loads, f.read_text().splitlines()):
            if r["id"] not in recs or not recs[r["id"]]["solved"]:
                recs[r["id"]] = r
    if bench == "bench60":
        ids = [r["pres_id"] for r in csv.DictReader((ROOT / "benchmark/subsets/benchmark_subset_60.csv").open())]
        return [recs[i] for i in ids if i in recs]
    return list(recs.values())


def z_count(step):
    """Letters z (3) in the isolating relator of an image step, cyclically reduced."""
    from acx.core.words import reduce
    steps = step["cov"]["steps"]
    rel = steps[1]["rels"][steps[2]["target"] - 1]
    return sum(abs(a) == 3 for a in reduce(tuple(rel)))


def one_z(r):
    return all(z_count(s) == 1 for s in r["path"][1:] if s["kind"] == "img")


def stats(xs, d=0):
    if not xs:
        return "-"
    return f"{st.mean(xs):,.{d}f} / {st.median(xs):,.0f} / {max(xs):,}"


def row(label, recs, unit_key, ryan=False):
    sol = [r for r in recs if r["solved"]]
    u = [r[unit_key] for r in sol]
    at = " / ".join(str(sum(x <= b for x in u)) for b in BUDGETS)
    if ryan:
        kinds = f"{len(sol)} / 0 / -"
        cov = [r["path_cov_moves"] for r in sol]
    else:
        orbit = sum(r["kind"] == "ac_path" for r in sol)
        oz = sum(one_z(r) for r in sol)
        kinds = f"{orbit} / {len(sol) - orbit} / {oz}"
        cov = [r["path_img_moves"] for r in sol]
    return (f"| {label} | {len(recs)} | {at} | {kinds} | {stats(u)} | {stats([r['path_length'] for r in sol], 1)} "
            f"| {stats(cov, 2)} | {stats([r['max_relator_len'] for r in sol], 1)} "
            f"| {max((r.get('max_relator_len_generated') or 0) for r in recs)} |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folders", nargs="+")
    ap.add_argument("--md")
    a = ap.parse_args()
    import sys
    sys.path.insert(0, str(ROOT))
    ryan_dir = ROOT / "results/ryan_full_1e6"
    lines = ["| benchmark / search | rows | solved @ 1e3 / 1e4 / 1e5 / 1e6 | AC path (orbit) / stable cert (orbit) / "
             "AC by one-z | units to solve mean / median / max | path mean / median / max | CoV moves on path "
             "mean / median / max | longest relator on path mean / median / max | longest relator generated |",
             "|---|---:|---|---|---|---|---|---|---:|"]
    for bench in ("ms640", "bench60", "ladder100"):
        ryan = load([ryan_dir], bench)
        for r in ryan:
            if r["solved"]:
                r["units"] = r["nodes_visited"] + r["gate_openings"]
        full = load(a.folders, bench)
        lines.append(row(f"{bench}: Ryan CoV, pops", ryan, "nodes_visited", True))
        lines.append(row(f"{bench}: Ryan CoV, units", ryan, "units", True))
        lines.append(row(f"{bench}: full CoV, pops", full, "nodes_visited"))
        lines.append(row(f"{bench}: full CoV, units", full, "units"))
    text = "\n".join(lines)
    print(text)
    if a.md:
        Path(a.md).write_text(text + "\n")


if __name__ == "__main__":
    main()
