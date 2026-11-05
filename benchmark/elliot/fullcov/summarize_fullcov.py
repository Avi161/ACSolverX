"""Tables of a full-CoV run: solved by budget, units and path length, longest relator, the CoV moves used.

    python -m benchmark.elliot.fullcov.summarize_fullcov <stage folder> ... [--md out.md]

Stage folders go from the smallest budget up (b10000 b100000 ...). A row's record is the one of the last stage that
has it without an error; the search is deterministic, so it is solved at budget B when its units are at most B. A
budget above the largest stage is reported only if every row is solved by then.
"""
import argparse
import json
import statistics as st
from collections import Counter
from pathlib import Path

from .run_fullcov import read_jsonl

BENCHES = (("ms640", "MS640", 640), ("bench60", "bench60", 60), ("ladder100", "ladder100", 100))
ALGOS = (("dual_single_cov", "dual, single CoV"), ("dual_auto_cov", "dual, auto CoV"), ("triple", "triple"))
BUDGETS = (10**3, 10**4, 10**5, 10**6, 10**7)


def load(stages, bench, algo):
    rows, top = {}, 0
    for d in stages:
        recs = read_jsonl(Path(d) / f"{bench}__{algo}.jsonl")
        for r in recs:
            if "error" not in r:
                rows[r["id"]] = r
                top = max(top, r["budget"])
    return rows, top


def fmt(x):
    return f"{x:,.0f}" if x >= 100 else (f"{x:.1f}" if isinstance(x, float) and x != int(x) else f"{x:,.0f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stages", nargs="+")
    ap.add_argument("--md", default=None)
    a = ap.parse_args()
    lines = ["| benchmark | method | " + " | ".join(f"10^{len(str(b)) - 1}" for b in BUDGETS) + " |",
             "|---|---|" + "---:|" * len(BUDGETS)]
    detail = ["| benchmark | method | solved | AC path | stable cert | units mean | median | max | path mean | "
              "median | max | longest relator | CoV moves (aut / stable / 24-map) |", "|---|---|" + "---:|" * 11 + "---|"]
    moves = []
    for bench, bname, n in BENCHES:
        for algo, aname in ALGOS:
            rows, top = load(a.stages, bench, algo)
            solved = [r for r in rows.values() if r["solved"]]
            cells = []
            for b in BUDGETS:
                k = sum(r["units"] <= b for r in solved)
                cells.append(str(k) if b <= top or k == n else "-")
            lines.append(f"| {bname} (of {n}) | {aname} | " + " | ".join(cells) + f" |")
            if not solved:
                continue
            u = [r["units"] for r in solved]
            p = [r["path_length"] for r in solved]
            kinds = Counter()
            for r in solved:
                kinds.update(r["move_kinds"])
            stable = sum(r["kind"] == "stable_cert" for r in solved)
            detail.append(
                f"| {bname} | {aname} | {len(solved)} | {len(solved) - stable} | {stable} | {st.mean(u):,.0f} | "
                f"{st.median(u):,.0f} | {max(u):,} | {st.mean(p):.1f} | {st.median(p):g} | {max(p)} | "
                f"{max(r['max_relator_len'] for r in solved)} | {kinds['full_cov_aut']} / {kinds['full_cov_stable']}"
                f" / {kinds['auto_cov']} |")
            for r in solved:
                for m in r.get("cov_used") or []:
                    if m["move_type"] == "full_cov":
                        moves.append((len(m["w"]), m["n_subs"], m["aut"]))
    by_w = Counter((w, aut) for w, _, aut in moves)
    by_n = Counter((k, aut) for _, k, aut in moves)
    text = "\n".join(["## Solved by budget (units)", "", *lines, "", "## Solves", "", *detail, "",
                      "## Full-CoV moves on the solution paths (all rows, all methods)", "",
                      "|w| (automorphism / stable): " + ", ".join(
                          f"{w}: {by_w[w, True]} / {by_w[w, False]}" for w in sorted({w for w, _ in by_w})),
                      "", "occurrences substituted (automorphism / stable): " + ", ".join(
                          f"{k}: {by_n[k, True]} / {by_n[k, False]}" for k in sorted({k for k, _ in by_n})), ""])
    print(text)
    if a.md:
        Path(a.md).write_text(text)


if __name__ == "__main__":
    main()
