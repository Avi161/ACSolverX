"""Per-presentation best-known cost for each technique, joined onto every benchmark subset.

The subset files say what the *problems* are. This says what each technique currently *costs* on
them -- nodes explored and the path length that came with those nodes -- so a new technique can be
priced against the field without re-deriving the field.

Writes ``benchmark/subsets/benchmark_subset_60_arms.{csv,json}`` plus
``benchmark/subsets/ARMS.md``. It never touches the frozen ``benchmark_subset_{N}.{csv,json}``:
those regenerate from the baseline jsonl alone and are checked by a zero-diff regeneration, and
folding a scoreboard into them would make the problem set depend on the results measured on it.

**Subset-60 only.** The four subsets are not nested, and both campaigns ran against subset-60's row
list, so 10/20/40 have arm data for only 4/10, 18/20 and 25/40 of their rows.

Two blocks of columns, and they answer different questions.

**Best-known** (``greedy_*``, ``bestcov_*``, ``heur_*``) -- the cheapest solve anyone has recorded,
each arm at its own budget and its own relator cap. This is what "how expensive is this row" means
in practice, and it is what the user asked for. It is **not** a controlled comparison: the arms ran
at 1,000,000 / <=20,000 / 100,000 nodes and at cap 24 / 24 / 48. Never read a ratio across them.

**Matched** (``m10k_*``) -- all three arms at budget 10,000 and cap 24, from
``results/comparison/three_way_b10k_subset60.csv``, whose builder refuses to write unless its
length-only control reproduces the plain greedy pop for pop on all 60 rows. This is the block a
head-to-head claim belongs in.

Run::

    .venv/bin/python3 -m experiments.analysis.benchmark_arms
"""
import csv
import json
import os
import sys


def _repo_root():
    d = os.path.dirname(os.path.abspath(__file__))
    while d != os.path.dirname(d):
        if (os.path.isdir(os.path.join(d, "experiments"))
                and os.path.isdir(os.path.join(d, "data"))):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root not found")


REPO = _repo_root()
sys.path.insert(0, REPO)

SUBSETS_DIR = os.path.join(REPO, "benchmark", "subsets")
COMPARISON = os.path.join(REPO, "results", "comparison")
BESTCOV_CSV = os.path.join(COMPARISON, "greedy_vs_bestcov_subset60_nodes_path.csv")
THREEWAY_CSV = os.path.join(COMPARISON, "three_way_b10k_subset60.csv")
EXP28_JSONL = os.path.join(REPO, "results", "heuristic_search", "runs",
                           "EXP28_colab_scale.jsonl")

# Subset-60 only. The four subsets are **not** nested (`nested: false` in each file), and both the
# CoV sweep and the heuristic campaign were run against subset-60's row list -- so 10/20/40 each
# contain rows nothing has been measured on (4/10, 18/20 and 25/40 have arm data). Emitting those
# would ship mostly-blank tables; subset-60 is the set that was actually carried out, 60/60.
SIZES = (60,)

# The recommended heap ordering, as shipped in experiments/heuristic_search/hsolve.py:RECOMMENDED.
# Mirrored here as data so this file can state the formula without importing the solver; the
# weights are asserted against RECOMMENDED at run time, so the two cannot drift apart silently.
HEUR_WEIGHTS = {"L": 1.0, "K": 2.53, "MK": 6.418, "S": 8.458, "xyimb": 3.292}
HEUR_FORMULA = ("priority(r1, r2) = L + 2.53*K + 6.418*MK + 8.458*S + 3.292*xyimb   "
                "(one segment, no length threshold)")
HEUR_TERMS = {
    "L": "total length |r1| + |r2| -- the baseline greedy's entire ordering",
    "K": "knot sum knots(r1) + knots(r2), where knots(w) = 0 for a pure power, "
         "else max(#x-blocks, #y-blocks) read cyclically",
    "MK": "max knots over the two relators",
    "S": "smaller mean block -- the mean run length of the thinner generator",
    "xyimb": "generator imbalance |#x - #y| / L, scale-free",
}

# Every arm's provenance, so a column can never be read without its budget and cap.
ARMS = {
    "greedy": {"what": "baseline greedy, best known", "budget": 1_000_000, "cap": 24,
               "source": "benchmark/subsets/benchmark_subset_60.json (nodes_1M / path_1M)"},
    "bestcov": {"what": "best change of variables over the whole subword family", "budget": 20_000,
                "cap": 24, "source": "results/comparison/greedy_vs_bestcov_subset60_nodes_path.csv"},
    "heur": {"what": "recommended heap ordering (formula above)", "budget": 100_000, "cap": 48,
             "source": "results/heuristic_search/runs/EXP28_colab_scale.jsonl, arm=recommended"},
    "m10k": {"what": "all three arms at a matched budget and cap", "budget": 10_000, "cap": 24,
             "source": "results/comparison/three_way_b10k_subset60.csv"},
}

FIELDS = [
    "pres_id", "bin", "aut_class", "start_length", "r1", "r2",
    # best known, each arm at its own budget/cap -- see ARMS
    "greedy_solved", "greedy_nodes", "greedy_path",
    "bestcov_solved", "bestcov_nodes", "bestcov_path",
    "bestcov_z", "bestcov_class", "bestcov_found_at_budget",
    "heur_solved", "heur_nodes", "heur_path",
    # matched budget 10,000 / cap 24 -- the controlled head-to-head
    "m10k_greedy_solved", "m10k_greedy_nodes", "m10k_greedy_path",
    "m10k_bestcov_solved", "m10k_bestcov_nodes", "m10k_bestcov_path",
    "m10k_heur_solved", "m10k_heur_nodes", "m10k_heur_path",
]


def _int(v):
    return None if v in ("", None) else int(v)


def _bool(v):
    return v in (True, "True", "true", 1, "1")


def load_bestcov():
    """pres_id -> the best CoV's cost, with the z it was found under."""
    out = {}
    with open(BESTCOV_CSV) as f:
        for r in csv.DictReader(f):
            out[int(r["pres_id"])] = {
                "bestcov_solved": _bool(r["bestcov_solved"]),
                "bestcov_nodes": _int(r["bestcov_nodes"]),
                "bestcov_path": _int(r["bestcov_path"]),
                "bestcov_z": r["bestcov_z"],
                "bestcov_class": r["bestcov_class"],
                "bestcov_found_at_budget": _int(r["bestcov_found_at_budget"]),
            }
    return out


def load_heuristic():
    """pres_id -> the recommended ordering's cost at 100,000 nodes, cap 48 (EXP-28)."""
    out = {}
    with open(EXP28_JSONL) as f:
        for line in f:
            row = json.loads(line)
            if row.get("arm") != "recommended":
                continue
            name = row.get("name", "")
            if not name.startswith("ms") or not name[2:].isdigit():
                continue          # the six reach rows carry a non-numeric suffix
            out[int(name[2:])] = {
                "heur_solved": bool(row["solved"]),
                "heur_nodes": row.get("nodes_explored"),
                "heur_path": row.get("path_length"),
            }
    return out


def load_matched():
    """pres_id -> all three arms at budget 10,000, cap 24."""
    out = {}
    with open(THREEWAY_CSV) as f:
        for r in csv.DictReader(f):
            out[int(r["pres_id"])] = {
                "m10k_greedy_solved": _bool(r["greedy_solved"]),
                "m10k_greedy_nodes": _int(r["greedy_nodes"]),
                "m10k_greedy_path": _int(r["greedy_path"]),
                "m10k_bestcov_solved": _bool(r["bestcov_solved"]),
                "m10k_bestcov_nodes": _int(r["bestcov_nodes"]),
                "m10k_bestcov_path": _int(r["bestcov_path"]),
                "m10k_heur_solved": _bool(r["heur_solved"]),
                "m10k_heur_nodes": _int(r["heur_nodes"]),
                "m10k_heur_path": _int(r["heur_path"]),
            }
    return out


def build_rows(size, bestcov, heur, matched):
    with open(os.path.join(SUBSETS_DIR, f"benchmark_subset_{size}.json")) as f:
        subset = json.load(f)["subset"]
    missing = [s["pres_id"] for s in subset
               if not (s["pres_id"] in bestcov and s["pres_id"] in heur
                       and s["pres_id"] in matched)]
    assert not missing, (
        f"subset_{size} has {len(missing)} rows no arm was measured on: {missing}. "
        "Emitting them blank would read as 'no technique solves it' -- rerun the arms on "
        "these rows, or restrict SIZES to the subset that was actually carried out.")
    rows = []
    for s in subset:
        pid = s["pres_id"]
        row = {
            "pres_id": pid,
            "bin": s["bin"],
            "aut_class": s.get("aut_class"),
            "start_length": s.get("start_length"),
            "r1": s["r1"],
            "r2": s["r2"],
            # The baseline's 10^6-node run is the subset's own ground truth: all 640 solve there.
            "greedy_solved": True,
            "greedy_nodes": s["nodes_1M"],
            "greedy_path": s["path_1M"],
        }
        row.update(bestcov[pid])
        row.update(heur[pid])
        row.update(matched[pid])
        rows.append(row)
    return rows


def summarize(rows):
    """Means over the rows every listed arm solves -- the only set a cross-arm mean is honest on."""
    both = [r for r in rows
            if r["greedy_solved"] and r["bestcov_solved"] and r["heur_solved"]]
    out = {"n_rows": len(rows), "n_all_three_solved": len(both)}
    for arm in ("greedy", "bestcov", "heur"):
        out[f"{arm}_solved"] = sum(1 for r in rows if r[f"{arm}_solved"])
        if both:
            out[f"{arm}_mean_nodes"] = round(
                sum(r[f"{arm}_nodes"] for r in both) / len(both), 2)
            out[f"{arm}_mean_path"] = round(
                sum(r[f"{arm}_path"] for r in both) / len(both), 2)
    for arm in ("m10k_greedy", "m10k_bestcov", "m10k_heur"):
        out[f"{arm}_solved"] = sum(1 for r in rows if r[f"{arm}_solved"])
    return out


def main():
    # Fail loudly rather than shipping a stale formula if RECOMMENDED ever changes.
    from experiments.heuristic_search.hsolve import RECOMMENDED
    shipped = RECOMMENDED["segments"]
    assert len(shipped) == 1 and shipped[0]["upto"] is None, \
        f"RECOMMENDED is no longer a single unthresholded segment: {RECOMMENDED}"
    assert shipped[0]["w"] == HEUR_WEIGHTS, \
        f"HEUR_WEIGHTS drifted from hsolve.RECOMMENDED: {shipped[0]['w']} != {HEUR_WEIGHTS}"

    bestcov, heur, matched = load_bestcov(), load_heuristic(), load_matched()

    for size in SIZES:
        rows = build_rows(size, bestcov, heur, matched)
        csv_path = os.path.join(SUBSETS_DIR, f"benchmark_subset_{size}_arms.csv")
        with open(csv_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(rows)
        json_path = os.path.join(SUBSETS_DIR, f"benchmark_subset_{size}_arms.json")
        with open(json_path, "w") as f:
            json.dump({
                "size": size,
                "heuristic_formula": HEUR_FORMULA,
                "heuristic_weights": HEUR_WEIGHTS,
                "heuristic_terms": HEUR_TERMS,
                "arms": ARMS,
                "summary": summarize(rows),
                "rows": rows,
            }, f, indent=1)
        s = summarize(rows)
        print(f"subset_{size:<3} n={s['n_rows']:<3} "
              f"solved greedy {s['greedy_solved']}, cov {s['bestcov_solved']}, "
              f"heur {s['heur_solved']}  |  on the {s['n_all_three_solved']} all three solve: "
              f"nodes {s['greedy_mean_nodes']} / {s['bestcov_mean_nodes']} / {s['heur_mean_nodes']}"
              f"   path {s['greedy_mean_path']} / {s['bestcov_mean_path']} / {s['heur_mean_path']}")

    write_doc(bestcov, heur, matched)
    print("\nwrote -> benchmark/subsets/benchmark_subset_60_arms.{csv,json}"
          f" + ARMS.md")


def write_doc(bestcov, heur, matched):
    lines = [
        "# Best-known cost per presentation, per technique",
        "",
        "`benchmark_subset_60_arms.{csv,json}` give one row per presentation: what each technique costs to solve it, in **nodes explored** and the **path length** that came with those nodes. Produced by `experiments/analysis/benchmark_arms.py`; the frozen `benchmark_subset_{N}.{csv,json}` are untouched.",
        "",
        "**Subset-60 only.** The four subsets are *not* nested (`nested: false` in each file), and both the CoV sweep and the heuristic campaign were run against subset-60's row list — so subset-10/20/40 have arm data for only 4/10, 18/20 and 25/40 of their rows. Subset-60 is the one that was actually carried out, and it is complete at 60/60.",
        "",
        "## The heuristic",
        "",
        "The recommended heap ordering — the baseline greedy with **only** the priority expression replaced, so any difference is attributable to the ordering and nothing else:",
        "",
        "```",
        HEUR_FORMULA,
        "```",
        "",
        "| term | weight | what it measures |",
        "|---|---|---|",
    ]
    for k, desc in HEUR_TERMS.items():
        # A bare "|" ends the cell in GFM, even inside a code span -- these descriptions carry
        # |r1| + |r2| and |#x - #y| / L, so escape before rendering, not in the data.
        lines.append(f"| `{k}` | {HEUR_WEIGHTS[k]} | {desc.replace('|', chr(92) + '|')} |")
    lines += [
        "",
        "Lower is popped first. Every term is a pure function of the state and rotation-invariant — a priority reading `depth` or the parent would make pop order depend on discovery order and stop being reproducible. It is a **single segment with no length threshold**: the earlier phased form is unnecessary here, because `S` and `MK` both fall as a pair approaches the trivial state, so the climb self-regulates.",
        "",
        "Shipped as `RECOMMENDED` in `experiments/heuristic_search/hsolve.py`; the producer asserts these weights against it, so the two cannot drift apart.",
        "",
        "## Columns",
        "",
        "**Best known** — each arm at its own budget and cap. This is what a row costs in practice.",
        "",
        "| prefix | technique | budget | cap | source |",
        "|---|---|---|---|---|",
    ]
    for k in ("greedy", "bestcov", "heur"):
        a = ARMS[k]
        lines.append(f"| `{k}_*` | {a['what']} | {a['budget']:,} | {a['cap']} | `{a['source']}` |")
    lines += [
        "",
        "> ⚠ **The three ran at different budgets and different relator caps.** Never read a ratio across them — a CoV row compared against a control at a different `max_relator_length` is not a comparison. Use the matched block for that.",
        "",
        "**Matched** — `m10k_*`, all three arms at budget 10,000 and cap 24, from "
        "`results/comparison/three_way_b10k_subset60.csv`, whose builder refuses to write unless its length-only control reproduces the plain greedy pop for pop on all 60 rows. A head-to-head claim belongs here.",
        "",
        "`bestcov_z` is the change of variables that produced the win and `bestcov_class` how it acts (`relabel` = a pure renaming, which is most of them — a rename is not a no-op, because the greedy reads strings, not orbits).",
        "",
        "## What the numbers say",
        "",
    ]
    rows60 = build_rows(60, bestcov, heur, matched)
    s = summarize(rows60)
    lab = {"greedy": "greedy @ 1,000,000, cap 24",
           "bestcov": "best CoV @ ≤20,000, cap 24",
           "heur": "heuristic @ 100,000, cap 48"}
    lines += [
        f"On subset-60 all three arms solve **{s['n_all_three_solved']}/60**, so every row below is a like-for-like row. **Read the median, not the mean** — both are given because the mean is dominated by a handful of second-hump rows (greedy: mean 45,244 against a median of 1,310, a 35× skew).",
        "",
        "| arm | solved | median nodes | mean nodes | median path | mean path |",
        "|---|---|---|---|---|---|",
    ]
    for k in ("greedy", "bestcov", "heur"):
        n = sorted(r[f"{k}_nodes"] for r in rows60)
        p = sorted(r[f"{k}_path"] for r in rows60)
        med = lambda v: (v[len(v) // 2 - 1] + v[len(v) // 2]) / 2 if len(v) % 2 == 0 else v[len(v) // 2]
        lines.append(f"| {lab[k]} | {s[f'{k}_solved']}/60 | {med(n):,.0f} | "
                     f"{s[f'{k}_mean_nodes']:,.0f} | {med(p):,.0f} | {s[f'{k}_mean_path']} |")
    lines += [
        "",
        "Both transformed arms cost **less** than the untransformed greedy on the same rows, and return **shorter** derivations — path length is not being traded for reach.",
        "",
        f"At the matched budget of 10,000 and cap 24, the solve counts are greedy **{s['m10k_greedy_solved']}/60**, best CoV **{s['m10k_bestcov_solved']}/60**, heuristic **{s['m10k_heur_solved']}/60**. That is the controlled comparison; the table above is best-known cost, where each arm ran at a different budget.",
        "",
        "> The best-CoV column is an **oracle**: 2,383 median nodes is what the winning `z` costs *once you know which `z` wins*, and finding it cost ~2.2M nodes per presentation of sweeping. It is a lower bound on a transformed route, not a runnable procedure ([why that distinction matters](../../experiments/lessons/price-the-untransformed-route.md)). The heuristic column has no such caveat — it is one search, with one fixed ordering.",
        "",
    ]
    with open(os.path.join(SUBSETS_DIR, "ARMS.md"), "w") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
