"""Summarise run_elliot.py output: one table row per (benchmark, algorithm).

Solved at budget B counts rows with nodes <= B (searches are deterministic and
nothing depends on the budget except where they stop, and no frontier pruning).

Usage: python benchmark/elliot/summarize.py results/elliot_10k [--md out.md]
"""
from __future__ import annotations

import argparse
import json
import statistics as st
from pathlib import Path

BENCHES = ("ms640", "bench60", "ladder100")
ALGOS = ("single_auto_cov_dual", "auto_dual", "auto_nonauto_cov_triple")
LABEL = {
    "single_auto_cov_dual": "Dual (sub + single CoV)",
    "auto_dual": "Dual (sub + auto CoV)",
    "auto_nonauto_cov_triple": "Triple (sub + auto + complete CoV)",
}


def stats(xs):
    if not xs:
        return "-", "-", "-"
    return f"{st.mean(xs):,.1f}", f"{st.median(xs):,.0f}", f"{max(xs):,}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--md")
    a = ap.parse_args()
    folder = Path(a.folder)
    lines = []
    budgets = sorted({json.loads(f.read_text().splitlines()[0])["budget"] for f in folder.glob("*.jsonl")})
    top = budgets[-1] if budgets else 10_000
    marks = [b for b in (10**3, 10**4, 10**5, 10**6, 10**7) if b <= top]
    solved_cols = " | ".join(f"solved @1e{len(str(b)) - 1}" for b in marks)
    head = ("| benchmark | method | rows | " + solved_cols + " | stable_cert | nodes mean / median / max (solved) "
            "| nodes total (fail = budget) | path mean / median / max | S-moves mean | CoV moves mean / max "
            "| max relator len mean / max | max total len max | pruned | errors |")
    lines += [head, "|" + "---|" * (head.count("|") - 1)]
    for bench in BENCHES:
        for algo in ALGOS:
            f = folder / f"{bench}__{algo}.jsonl"
            if not f.exists():
                continue
            recs = [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
            budget = recs[0]["budget"]
            ok = [r for r in recs if "error" not in r]
            sol = [r for r in ok if r["solved"]]
            n_err = len(recs) - len(ok)
            solved_at = " | ".join(str(sum(1 for r in sol if r["nodes"] <= b)) for b in marks)
            stable = sum(1 for r in sol if r["kind"] == "stable_cert")
            total = sum(r["nodes"] if r["solved"] else budget for r in ok)
            nm, nmed, nmax = stats([r["nodes"] for r in sol])
            pm, pmed, pmax = stats([r["path_length"] for r in sol])
            sub = f"{st.mean(r['sub_moves'] for r in sol):.1f}" if sol else "-"
            cov = f"{st.mean(r['cov_moves'] for r in sol):.2f} / {max(r['cov_moves'] for r in sol)}" if sol else "-"
            mr = f"{st.mean(r['max_relator_len'] for r in sol):.1f} / {max(r['max_relator_len'] for r in sol)}" if sol else "-"
            mt = max((r["max_total_len"] for r in sol), default="-")
            pruned = sum(r.get("frontier_prune_count") or 0 for r in ok)
            lines.append(
                f"| {bench} | {LABEL[algo]} | {len(recs)} | {solved_at} | {stable} | {nm} / {nmed} / {nmax} "
                f"| {total:,} | {pm} / {pmed} / {pmax} | {sub} | {cov} | {mr} | {mt} | {pruned} | {n_err} |"
            )
    text = "\n".join(lines)
    print(text)
    if a.md:
        Path(a.md).write_text(text + "\n")


if __name__ == "__main__":
    main()
