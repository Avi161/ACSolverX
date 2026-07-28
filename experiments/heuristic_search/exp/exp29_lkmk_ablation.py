"""Assemble EXP-29 and report L/K/MK against baseline and full RECOMMENDED at budget 1,000.

The L/K/MK rows are measured directly by ``run_lkmk_ablation``. Baseline and RECOMMENDED come from
the exact 1,000-pop prefix of the existing cap-48 EXP-28 runs, read through each row's ``solved_at``.
No search is launched here.

    .venv/bin/python3 -m experiments.heuristic_search.exp.exp29_lkmk_ablation
"""
import csv
import json
import os
import statistics
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, part)) for part in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.heuristic_search.core.hlab import LOGS, bench66  # noqa: E402

BUDGET = 1_000
MRL = 48
ARMS = ("baseline", "recommended", "lkmk")
LABELS = {
    "baseline": "Greedy baseline",
    "recommended": "Full RECOMMENDED",
    "lkmk": "L + 2.53K + 6.418MK",
}
LKMK_CONFIG = "L=1; K=2.53; MK=6.418"
RAW_LKMK = os.path.join(LOGS, "EXP29_lkmk_bench66_b1000_mrl48.jsonl")
EXP28 = os.path.join(LOGS, "EXP28_colab_scale.jsonl")
OUT_CSV = os.path.join(LOGS, "EXP29_lkmk_ablation.csv")
OUT_MD = os.path.join(LOGS, "EXP29_lkmk_ablation.md")

FIELDS = (
    "order", "pres_id", "name", "bin", "start_length", "arm", "arm_label", "config",
    "budget", "mrl", "solved", "nodes_explored", "path_length", "derived", "source",
    "source_budget", "in_all_three_solved",
)


def _jsonl(path):
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def _validate_one_per_name(rows, expected, label):
    names = [r["name"] for r in rows]
    if len(rows) != len(expected) or set(names) != set(expected) or len(names) != len(set(names)):
        missing = sorted(set(expected) - set(names))
        extra = sorted(set(names) - set(expected))
        raise SystemExit(f"{label}: expected one row for each of {len(expected)} names; "
                         f"got {len(rows)}, missing={missing[:8]}, extra={extra[:8]}")


def _native_lkmk(expected):
    rows = list(_jsonl(RAW_LKMK))
    _validate_one_per_name(rows, expected, "EXP-29 raw L/K/MK")
    bad = [r["name"] for r in rows if r.get("arm") != "lkmk" or r.get("dataset") != "bench66"
           or r.get("budget") != BUDGET or r.get("mrl") != MRL]
    if bad:
        raise SystemExit(f"EXP-29 raw rows have wrong identity: {bad[:8]}")
    return {r["name"]: r for r in rows}


def _derived_exp28(expected):
    source = [r for r in _jsonl(EXP28)
              if r.get("arm") in ("baseline", "recommended") and r.get("name") in expected]
    out = {}
    for arm in ("baseline", "recommended"):
        rows = [r for r in source if r["arm"] == arm]
        _validate_one_per_name(rows, expected, f"EXP-28 {arm}")
        for r in rows:
            solved = r["solved_at"] is not None and int(r["solved_at"]) <= BUDGET
            if solved and r.get("path_length") is None:
                raise SystemExit(f"EXP-28 {arm}/{r['name']} solves by 1,000 but has no path length")
            out[(arm, r["name"])] = {
                "solved": solved,
                "nodes_explored": int(r["solved_at"]) if solved else BUDGET,
                "path_length": int(r["path_length"]) if solved else None,
                "source_budget": int(r["budget"]),
            }
    return out


def _mean(values):
    return statistics.fmean(values) if values else None


def _median(values):
    return statistics.median(values) if values else None


def _stats(rows):
    solved = [r for r in rows if r["solved"]]
    return {
        "n": len(solved),
        "nodes_mean": _mean([r["nodes_explored"] for r in solved]),
        "nodes_median": _median([r["nodes_explored"] for r in solved]),
        "path_mean": _mean([r["path_length"] for r in solved]),
        "path_median": _median([r["path_length"] for r in solved]),
    }


def _fmt(value, digits=1):
    if value is None:
        return "—"
    if float(value).is_integer():
        return f"{int(value):,}"
    return f"{value:,.{digits}f}"


def _write_csv(rows):
    with open(OUT_CSV, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: "" if row[k] is None else row[k] for k in FIELDS})


def _write_report(rows, bench):
    own = {arm: _stats([r for r in rows if r["arm"] == arm]) for arm in ARMS}
    shared_names = {r["name"] for r in rows if r["in_all_three_solved"]}
    shared = {arm: _stats([r for r in rows
                           if r["arm"] == arm and r["name"] in shared_names]) for arm in ARMS}
    by_bin = {arm: [] for arm in ARMS}
    for arm in ARMS:
        for b in range(10):
            d = [r for r in rows if r["arm"] == arm and r["bin"] == b]
            by_bin[arm].append(sum(r["solved"] for r in d))

    frontier = [r["name"] for r in rows if r["arm"] == "lkmk" and not r["solved"]
                and r["nodes_explored"] != BUDGET]
    lines = [
        "# EXP-29 — how much of RECOMMENDED is already in L, K and MK?",
        "",
        f"A controlled ablation on the frozen 60-row benchmark: one `hcompact` search per presentation at budget {BUDGET:,}, cap {MRL}. The ablation keeps the shipped coefficients `L + 2.53K + 6.418MK` and removes only `S` and `xyimb`; it is not re-tuned. Baseline and full RECOMMENDED are exact budget-{BUDGET:,} checkpoints derived from `EXP28_colab_scale.jsonl` by `solved_at`, not new searches.",
        "",
        "## Solve count",
        "",
        "| arm | solved | bins 0–3 | bin 4 | bin 5 | bin 6 | bin 7 | bins 8–9 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for arm in ARMS:
        bins = by_bin[arm]
        lines.append(f"| {LABELS[arm]} | **{own[arm]['n']}/60** | {sum(bins[:4])}/24 | "
                     f"{bins[4]}/6 | {bins[5]}/6 | {bins[6]}/6 | {bins[7]}/6 | "
                     f"{sum(bins[8:])}/12 |")

    lines += [
        "",
        "## Descriptive cost on each arm's own solved rows",
        "",
        "These denominators differ and therefore describe each arm separately; they are not a head-to-head cost comparison. Unsolved rows are excluded because their `nodes_explored = 1,000` is censoring, not solution cost.",
        "",
        "| arm | denominator | nodes mean | nodes median | path mean | path median |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for arm in ARMS:
        s = own[arm]
        lines.append(f"| {LABELS[arm]} | {s['n']} solved | {_fmt(s['nodes_mean'])} | "
                     f"{_fmt(s['nodes_median'])} | {_fmt(s['path_mean'])} | "
                     f"{_fmt(s['path_median'])} |")

    lines += [
        "",
        "## Matched cost on the rows all three solve",
        "",
        f"All values below use the same **{len(shared_names)} presentations**. This is the apples-to-apples comparison used in the figure.",
        "",
        "| arm | denominator | nodes mean | nodes median | path mean | path median |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for arm in ARMS:
        s = shared[arm]
        lines.append(f"| {LABELS[arm]} | {s['n']} shared solves | {_fmt(s['nodes_mean'])} | "
                     f"{_fmt(s['nodes_median'])} | {_fmt(s['path_mean'])} | "
                     f"{_fmt(s['path_median'])} |")

    lines += [
        "",
        "## Provenance and checks",
        "",
        f"- New search: `EXP29_lkmk_bench66_b1000_mrl48.jsonl`, `hcompact`, `{LKMK_CONFIG}`, {len(bench)} rows.",
        "- Reused searches: `EXP28_colab_scale.jsonl`, arms `baseline` and `recommended`, source budget 100,000/cap 48; the deterministic prefix property makes `solved_at <= 1,000` the exact budget-1,000 result.",
        f"- L/K/MK unsolved rows that exhausted the frontier before node {BUDGET:,}: "
        + (", ".join(frontier) if frontier else "none") + ".",
        "- Raw row-level comparison: `EXP29_lkmk_ablation.csv`; figure: `EXP29_lkmk_ablation.png`.",
        "",
    ]
    with open(OUT_MD, "w") as fh:
        fh.write("\n".join(lines))
    print("\n".join(lines))


def main():
    bench = bench66()[:60]
    expected = [r["name"] for r in bench]
    meta = {r["name"]: r for r in bench}
    native = _native_lkmk(expected)
    derived = _derived_exp28(set(expected))

    solved_by_name = {}
    for name in expected:
        solved_by_name[name] = {
            "baseline": derived[("baseline", name)]["solved"],
            "recommended": derived[("recommended", name)]["solved"],
            "lkmk": bool(native[name]["solved"]),
        }
    shared = {name for name, flags in solved_by_name.items() if all(flags.values())}

    rows = []
    for order, name in enumerate(expected):
        m = meta[name]
        for arm in ARMS:
            if arm == "lkmk":
                src = native[name]
                result = {
                    "solved": bool(src["solved"]),
                    "nodes_explored": int(src["nodes_explored"]),
                    "path_length": int(src["path_length"]) if src["solved"] else None,
                    "derived": False,
                    "source": "EXP29_lkmk_bench66_b1000_mrl48.jsonl",
                    "source_budget": BUDGET,
                    "config": LKMK_CONFIG,
                }
            else:
                src = derived[(arm, name)]
                result = {
                    **src,
                    "derived": True,
                    "source": "EXP28_colab_scale.jsonl",
                    "config": "L" if arm == "baseline" else
                              "L=1; K=2.53; MK=6.418; S=8.458; xyimb=3.292",
                }
            rows.append({
                "order": order,
                "pres_id": m["pres_id"],
                "name": name,
                "bin": m["bin"],
                "start_length": m["start_length"],
                "arm": arm,
                "arm_label": LABELS[arm],
                "budget": BUDGET,
                "mrl": MRL,
                "in_all_three_solved": name in shared,
                **result,
            })

    _write_csv(rows)
    _write_report(rows, bench)
    print(f"\nwrote {OUT_CSV}")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
