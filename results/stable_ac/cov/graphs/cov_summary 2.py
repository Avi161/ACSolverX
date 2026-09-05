"""Aggregate one budget's CoV sweep into per-presentation records + headline stats.

Library for the week-5 website figures AND a CLI. Per budget B found in ../covsweep_{B}_66_subnc2pxysb_*.jsonl (chunk files excluded), the CLI writes into graphs/:

    per_presentation_b{B}.csv   one row per presentation, sorted by baseline 1M difficulty
    SUMMARY_b{B}.md             headline tables (landscape / lottery / best-z / aut split)

Run from ACSolverX/:
    .venv/bin/python3 results/stable_ac/cov/graphs/cov_summary.py             # all budgets found
    .venv/bin/python3 results/stable_ac/cov/graphs/cov_summary.py --budget 1000

Baseline = the sweep's own control row (z_word null). "best z" = the solved CoV row with the fewest nodes (ties: shortest path, then z_word). Class split: relabel = aut_canon_orig == aut_canon_cov (same Aut(F2)-orbit, a rename), moved = different orbit (a genuinely different problem).
"""
import argparse
import collections
import csv
import glob
import json
import os
import re
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
COV_DIR = os.path.normpath(os.path.join(HERE, ".."))
ACS = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
COMBINED = os.path.join(ACS, "results", "benchmark", "combined", "benchmark_combined_66.csv")
_CHUNK = re.compile(r"_c\d+of\d+_")


def available_budgets():
    """{budget: newest matching 66-presentation sweep file}, chunk files excluded."""
    out = {}
    for p in glob.glob(os.path.join(COV_DIR, "covsweep_*_66_subnc2pxysb_*.jsonl")):
        name = os.path.basename(p)
        if _CHUNK.search(name):
            continue
        b = int(name.split("_")[1])
        if b not in out or os.path.getmtime(p) > os.path.getmtime(out[b]):
            out[b] = p
    return dict(sorted(out.items()))


def load_rows(path):
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def cov_class(r):
    a, b = r.get("aut_canon_orig"), r.get("aut_canon_cov")
    if a is None or b is None:
        return None
    return "relabel" if a == b else "moved"


def _nodes_1m():
    if not os.path.exists(COMBINED):
        return {}
    with open(COMBINED) as f:
        return {r["pres_id"]: int(r["nodes_1M"]) for r in csv.DictReader(f)
                if r["source"] == "ladder" and r["nodes_1M"]}


def order_by_difficulty(per):
    n1m = _nodes_1m()
    ladder = sorted((p for p in per if p["kind"] == "ladder"),
                    key=lambda p: n1m.get(p["pres_id"], 10**9))
    reach = sorted((p for p in per if p["kind"] == "reach"), key=lambda p: p["pres_id"])
    for p in ladder:
        p["nodes_1M"] = n1m.get(p["pres_id"])
    for p in reach:
        p["nodes_1M"] = None
    return ladder + reach


def aggregate(rows):
    by = {}
    for r in rows:
        d = by.setdefault(str(r["pres_id"]), {"ctrl": None, "cov": [], "source": r.get("source", "")})
        if r["z_word"] is None:
            d["ctrl"] = r
        else:
            d["cov"].append(r)

    per = []
    for pid, d in by.items():
        ctrl, cov = d["ctrl"], d["cov"]
        solved = [r for r in cov if r["solved"]]
        base_s = bool(ctrl and ctrl["solved"])
        base_n = ctrl["nodes_explored"] if base_s else None
        base_p = ctrl["path_length"] if base_s else None
        best = min(solved, key=lambda r: (r["nodes_explored"], r["path_length"],
                                          r["z_word"], str(r.get("iso_gen")), str(r.get("iso_index")))) if solved else None
        rec = dict(
            pres_id=pid, source=d["source"],
            kind="reach" if "reach" in d["source"] else "ladder",
            n_cov=len(cov), n_cov_solved=len(solved),
            base_solved=base_s, base_nodes=base_n, base_path=base_p,
            best_nodes=best["nodes_explored"] if best else None,
            best_path=best["path_length"] if best else None,
            best_z=best["z_word"] if best else None,
            best_class=cov_class(best) if best else None,
            min_path=min((r["path_length"] for r in solved), default=None),
            n_relabel=sum(1 for r in cov if cov_class(r) == "relabel"),
            n_moved=sum(1 for r in cov if cov_class(r) == "moved"),
            relabel_solved=sum(1 for r in solved if cov_class(r) == "relabel"),
            moved_solved=sum(1 for r in solved if cov_class(r) == "moved"),
            fewer=None, equal=None, more=None, cov_unsolved=None,
        )
        if base_s:
            rec["fewer"] = sum(1 for r in solved if r["nodes_explored"] < base_n)
            rec["equal"] = sum(1 for r in solved if r["nodes_explored"] == base_n)
            rec["more"] = sum(1 for r in solved if r["nodes_explored"] > base_n)
            rec["cov_unsolved"] = len(cov) - len(solved)
        rec["klass"] = "baseline_solved" if base_s else ("flip" if solved else "never")
        per.append(rec)

    per = order_by_difficulty(per)
    return {"per_pres": per, "totals": _totals(per, rows), "by": by}


def _med(v):
    return round(statistics.median(v), 1) if v else None


def _totals(per, rows):
    cov = [r for r in rows if r["z_word"] is not None]
    t = dict(budget=rows[0]["node_budget"], n_pres=len(per), n_cov_rows=len(cov),
             complete=len(per) == 66)
    t["base_solved"] = sum(p["base_solved"] for p in per)
    t["best_solved"] = sum(1 for p in per if p["best_nodes"] is not None)
    t["flips"] = sum(1 for p in per if p["klass"] == "flip")
    t["never"] = sum(1 for p in per if p["klass"] == "never")

    both = [p for p in per if p["base_solved"] and p["best_nodes"] is not None]
    t["n_both"] = len(both)
    if both:
        ratios = [p["base_nodes"] / p["best_nodes"] for p in both]
        t["ratio_mean"] = round(sum(ratios) / len(ratios), 2)
        t["ratio_median"] = round(statistics.median(ratios), 2)
        t["total_base_nodes"] = sum(p["base_nodes"] for p in both)
        t["total_best_nodes"] = sum(p["best_nodes"] for p in both)
        t["path_shorter"] = sum(1 for p in both if p["best_path"] < p["base_path"])
        t["path_equal"] = sum(1 for p in both if p["best_path"] == p["base_path"])
        t["path_longer"] = sum(1 for p in both if p["best_path"] > p["base_path"])
        t["q_fewer_shorter"] = sum(1 for p in both
                                   if p["best_nodes"] < p["base_nodes"] and p["best_path"] < p["base_path"])
        t["q_fewer_only"] = sum(1 for p in both
                                if p["best_nodes"] < p["base_nodes"] and p["best_path"] >= p["base_path"])
        t["q_shorter_only"] = sum(1 for p in both
                                  if p["best_nodes"] >= p["base_nodes"] and p["best_path"] < p["base_path"])
        t["q_neither"] = sum(1 for p in both
                             if p["best_nodes"] >= p["base_nodes"] and p["best_path"] >= p["base_path"])

    bs = [p for p in per if p["base_solved"]]
    t["lot_fewer"] = sum(p["fewer"] for p in bs)
    t["lot_equal"] = sum(p["equal"] for p in bs)
    t["lot_more"] = sum(p["more"] for p in bs)
    t["lot_unsolved"] = sum(p["cov_unsolved"] for p in bs)
    t["lot_total"] = sum(p["n_cov"] for p in bs)

    rel = [r for r in cov if cov_class(r) == "relabel"]
    mov = [r for r in cov if cov_class(r) == "moved"]
    rel_s = [r for r in rel if r["solved"]]
    mov_s = [r for r in mov if r["solved"]]
    t["n_relabel"], t["n_moved"] = len(rel), len(mov)
    t["relabel_solved"], t["moved_solved"] = len(rel_s), len(mov_s)
    t["relabel_med_nodes"] = _med([r["nodes_explored"] for r in rel_s])
    t["moved_med_nodes"] = _med([r["nodes_explored"] for r in mov_s])
    t["relabel_med_path"] = _med([r["path_length"] for r in rel_s])
    t["moved_med_path"] = _med([r["path_length"] for r in mov_s])
    # robustness: same numbers restricted to rows at the control's cap (24) — cap is part of the method
    t["relabel_med_nodes_cap24"] = _med([r["nodes_explored"] for r in rel_s if r["max_relator_length_cap"] == 24])
    t["moved_med_nodes_cap24"] = _med([r["nodes_explored"] for r in mov_s if r["max_relator_length_cap"] == 24])
    t["n_relabel_cap24"] = sum(1 for r in rel if r["max_relator_length_cap"] == 24)
    t["n_moved_cap24"] = sum(1 for r in mov if r["max_relator_length_cap"] == 24)

    wc = collections.Counter(p["best_class"] for p in per if p["best_nodes"] is not None)
    t["win_relabel"], t["win_moved"] = wc.get("relabel", 0), wc.get("moved", 0)
    fc = collections.Counter()
    for p in per:
        if p["klass"] != "flip":
            continue
        if p["relabel_solved"] and p["moved_solved"]:
            fc["both"] += 1
        elif p["relabel_solved"]:
            fc["relabel_only"] += 1
        elif p["moved_solved"]:
            fc["moved_only"] += 1
    t["flip_relabel_only"] = fc["relabel_only"]
    t["flip_moved_only"] = fc["moved_only"]
    t["flip_both"] = fc["both"]
    # per-presentation solve chance by class, over presentations that have both kinds
    havb = [p for p in per if p["n_relabel"] and p["n_moved"]]
    t["n_pres_both_classes"] = len(havb)
    return t


def write_csv(agg, path):
    cols = ["pres_id", "kind", "nodes_1M", "klass", "n_cov", "n_relabel", "n_moved",
            "base_solved", "base_nodes", "base_path",
            "n_cov_solved", "relabel_solved", "moved_solved",
            "fewer", "equal", "more", "cov_unsolved",
            "best_z", "best_class", "best_nodes", "best_path", "min_path",
            "node_cut", "path_cut"]
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for p in agg["per_pres"]:
            cut = round(p["base_nodes"] / p["best_nodes"], 2) if p["base_solved"] and p["best_nodes"] else None
            pcut = round(p["base_path"] / p["best_path"], 2) if p["base_solved"] and p["best_path"] else None
            w.writerow([p.get(c) if c not in ("node_cut", "path_cut") else (cut if c == "node_cut" else pcut)
                        for c in cols])


def write_md(agg, path, src_name):
    t = agg["totals"]
    B = t["budget"]
    lt = t["lot_total"] or 1

    def pct(x, d=lt):
        return f"{100 * x / d:.0f}%" if d else "—"

    lines = [
        f"# CoV sweep @ budget {B:,} — summary",
        "",
        f"Source: `{src_name}` ({t['n_pres']} presentations, {t['n_cov_rows']:,} CoV rows + {t['n_pres']} controls). Baseline = the sweep's own control row (no CoV). Best z = solved CoV row with fewest nodes. Generated by `cov_summary.py`; per-presentation detail in `per_presentation_b{B}.csv`.",
        "",
        "## Solve landscape",
        "",
        "| | count |",
        "|---|---:|",
        f"| baseline (greedy, no CoV) solves | **{t['base_solved']}/{t['n_pres']}** |",
        f"| flips — baseline fails, some CoV solves | **{t['flips']}** |",
        f"| solved by best CoV | **{t['best_solved']}/{t['n_pres']}** |",
        f"| never solved by anything | {t['never']} |",
        "",
        f"## A random CoV vs its baseline ({t['base_solved']} baseline-solved presentations, {t['lot_total']:,} CoV rows)",
        "",
        "| outcome | count | share |",
        "|---|---:|---:|",
        f"| solved, fewer nodes (better) | {t['lot_fewer']:,} | {pct(t['lot_fewer'])} |",
        f"| solved, equal nodes | {t['lot_equal']:,} | {pct(t['lot_equal'])} |",
        f"| solved, more nodes (worse) | {t['lot_more']:,} | {pct(t['lot_more'])} |",
        f"| did not solve within {B:,} nodes | {t['lot_unsolved']:,} | {pct(t['lot_unsolved'])} |",
        "",
    ]
    if t.get("n_both"):
        lines += [
            f"## Best CoV vs baseline ({t['n_both']} presentations solved by both)",
            "",
            "| metric | value |",
            "|---|---:|",
            f"| node cut base/best — mean | {t['ratio_mean']}× |",
            f"| node cut base/best — median | {t['ratio_median']}× |",
            f"| total nodes, baseline vs best | {t['total_base_nodes']:,} vs {t['total_best_nodes']:,} ({t['total_base_nodes'] / t['total_best_nodes']:.2f}×) |",
            f"| path shorter / equal / longer | {t['path_shorter']} / {t['path_equal']} / {t['path_longer']} |",
            f"| fewer nodes AND shorter path | {t['q_fewer_shorter']}/{t['n_both']} |",
            f"| fewer nodes only | {t['q_fewer_only']} |",
            f"| shorter path only | {t['q_shorter_only']} |",
            f"| neither | {t['q_neither']} |",
            "",
        ]
    if t["n_relabel"] or t["n_moved"]:
        rs = t["relabel_solved"] / t["n_relabel"] if t["n_relabel"] else 0
        ms = t["moved_solved"] / t["n_moved"] if t["n_moved"] else 0
        lines += [
            "## Automorphic (relabel) vs non-automorphic (moved orbit)",
            "",
            "relabel = `aut_canon_orig == aut_canon_cov` (same Aut(F₂)-orbit — the same problem renamed); moved = a genuinely different orbit.",
            "",
            "| | relabel | moved |",
            "|---|---:|---:|",
            f"| CoV rows | {t['n_relabel']:,} ({100 * t['n_relabel'] / (t['n_cov_rows'] or 1):.0f}%) | {t['n_moved']:,} ({100 * t['n_moved'] / (t['n_cov_rows'] or 1):.0f}%) |",
            f"| solved | {t['relabel_solved']:,} ({100 * rs:.0f}%) | {t['moved_solved']:,} ({100 * ms:.0f}%) |",
            f"| median nodes (solved) | {t['relabel_med_nodes']} | {t['moved_med_nodes']} |",
            f"| median path (solved) | {t['relabel_med_path']} | {t['moved_med_path']} |",
            f"| median nodes, cap-24 rows only | {t['relabel_med_nodes_cap24']} (n={t['n_relabel_cap24']:,}) | {t['moved_med_nodes_cap24']} (n={t['n_moved_cap24']:,}) |",
            f"| best-z winners | {t['win_relabel']} | {t['win_moved']} |",
            f"| flips solvable only by this class | {t['flip_relabel_only']} | {t['flip_moved_only']} |",
            "",
            f"Flips solvable by both classes: {t['flip_both']}.",
            "",
        ]
    with open(path, "w") as f:
        f.write("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=None)
    args = ap.parse_args()
    files = available_budgets()
    if args.budget is not None:
        files = {args.budget: files[args.budget]}
    for b, path in files.items():
        agg = aggregate(load_rows(path))
        t = agg["totals"]
        write_csv(agg, os.path.join(HERE, f"per_presentation_b{b}.csv"))
        write_md(agg, os.path.join(HERE, f"SUMMARY_b{b}.md"), os.path.basename(path))
        print(f"budget {b}: {t['n_pres']} pres ({'complete' if t['complete'] else 'PARTIAL'}), "
              f"baseline {t['base_solved']}, best-z {t['best_solved']}, flips {t['flips']}, "
              f"never {t['never']}  ->  per_presentation_b{b}.csv, SUMMARY_b{b}.md")


if __name__ == "__main__":
    main()
