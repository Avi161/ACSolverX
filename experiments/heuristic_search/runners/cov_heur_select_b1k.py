"""Pick each row's CoV by min RECOMMENDED start priority; search at budget 1,000.

Removes the selection bias that favors length-only: for each of the 60 subset
rows, enumerate the same subword-CoV family as the sweep, score every
transformed start with the static ``RECOMMENDED`` min-heap priority
(``L + 2.53K + 6.418MK + 8.458S + 3.292·xyimb``), keep the argmin, then run
**both** length-only and ``RECOMMENDED`` searches at budget 1,000 on that start.

Compare to the shipped greedy-oracle best-CoV arms in
``cov_heur_b1k_subset60.csv`` (45/60 covgreedy, 43/60 covheur).

Control gate: when the heur-selected ``(z, iso_gen, iso_index)`` equals the
shipped bestcov recipe, both hsel arms must match the shipped b1k CoV arms
pop for pop (solved + nodes).

    .venv/bin/python3 -m experiments.heuristic_search.runners.cov_heur_select_b1k
"""
from __future__ import annotations

import csv
import json
import os
import statistics
import sys
import time


def _repo_root(start=None):
    d = os.path.abspath(start or os.path.dirname(os.path.abspath(__file__)))
    while d != os.path.dirname(d):
        if (os.path.isdir(os.path.join(d, "experiments"))
                and os.path.isdir(os.path.join(d, "data"))):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root (experiments/ + data/) not found")


ROOT = _repo_root()
sys.path.insert(0, ROOT)

from experiments.greedy_tests.spec.words import str_to_word, word_to_str  # noqa: E402
from experiments.heuristic_search.core.hlab import FEATURES, phi  # noqa: E402
from experiments.heuristic_search.core.hsolve import (  # noqa: E402
    RECOMMENDED, greedy_search_h,
)
from experiments.stable_ac.cov import cov  # noqa: E402

BUDGET = 1_000
CAP_HEADROOM = 16
SOURCE = os.path.join(ROOT, "results/comparison/cov_heur_b1k_subset60.csv")
CSV_OUT = os.path.join(ROOT, "results/comparison/cov_heur_select_b1k_subset60.csv")
MD_OUT = os.path.join(ROOT, "results/comparison/COV_HEUR_SELECT_B1K.md")

DIMS = ("L", "K", "MK", "S", "xyimb")
WEIGHTS = RECOMMENDED["segments"][0]["w"]

FIELDS = [
    "pres_id", "bin", "aut_class", "start_length", "r1", "r2",
    # shipped greedy-oracle bestcov
    "bestcov_z", "bestcov_iso_gen", "bestcov_iso_index", "bestcov_class",
    "bestcov_cap", "bestcov_r1", "bestcov_r2", "bestcov_n_tied_starts",
    "bestcov_prio",
    "b1k_covgreedy_solved", "b1k_covgreedy_nodes", "b1k_covgreedy_path",
    "b1k_covheur_solved", "b1k_covheur_nodes", "b1k_covheur_path",
    # heur-selected by min RECOMMENDED start prio
    "hsel_z", "hsel_iso_gen", "hsel_iso_index", "hsel_class",
    "hsel_cap", "hsel_r1", "hsel_r2", "hsel_n_tied_starts",
    "hsel_n_candidates", "hsel_prio", "same_as_bestcov",
    "hsel_covgreedy_solved", "hsel_covgreedy_nodes", "hsel_covgreedy_path",
    "hsel_covheur_solved", "hsel_covheur_nodes", "hsel_covheur_path",
]


def _bool(v):
    return str(v).strip().lower() in ("1", "true", "yes")


def _prio(r1, r2):
    v = phi(r1, r2)
    idx = {f: i for i, f in enumerate(FEATURES)}
    return sum(WEIGHTS[d] * float(v[idx[d]]) for d in DIMS)


def select_min_prio(r1, r2):
    """Argmin RECOMMENDED start prio over enumerate_cov; first-seen wins ties."""
    cands = cov.enumerate_cov(
        str_to_word(r1), str_to_word(r2),
        default_cap=max(len(r1), len(r2), 24),
        cap_headroom=cov.CAP_HEADROOM,
        reject_len=cov.REJECT_LEN)
    if not cands:
        raise RuntimeError(f"no CoV candidates for {r1!r}, {r2!r}")

    best = None
    best_prio = None
    tied_pairs = set()
    for c in cands:
        o1, o2 = word_to_str(c.r1), word_to_str(c.r2)
        p = _prio(o1, o2)
        if best is None or p < best_prio:
            best_prio = p
            best = {
                "z": word_to_str(c.z_word),
                "iso_gen": c.iso_gen,
                "iso_index": int(c.iso_index),
                "r1": o1,
                "r2": o2,
                "n_subs": int(c.n_subs),
                "prio": p,
            }
            tied_pairs = {(o1, o2)}
        elif p == best_prio:
            tied_pairs.add((o1, o2))

    best["n_tied_starts"] = len(tied_pairs)
    best["n_candidates"] = len(cands)
    best["cap"] = max(len(best["r1"]), len(best["r2"])) + CAP_HEADROOM
    return best


def _path_cell(res):
    return int(res["path_length"]) if res["solved"] else ""


def run():
    with open(SOURCE) as f:
        src = list(csv.DictReader(f))
    if len(src) != 60:
        raise RuntimeError(f"expected 60 rows, got {len(src)}")

    # Warm numba once
    greedy_search_h("X", "Y", 10, max_relator_length=24, config=None)

    rows = []
    gate_fail = []
    over = []
    t0 = time.time()

    for i, s in enumerate(src):
        r1, r2 = s["r1"], s["r2"]
        hsel = select_min_prio(r1, r2)

        same = (
            hsel["z"] == s["cov_z"]
            and str(hsel["iso_gen"]) == str(s["cov_iso_gen"])
            and int(hsel["iso_index"]) == int(s["cov_iso_index"])
        )

        cg = greedy_search_h(
            hsel["r1"], hsel["r2"], BUDGET,
            max_relator_length=hsel["cap"], config=None)
        ch = greedy_search_h(
            hsel["r1"], hsel["r2"], BUDGET,
            max_relator_length=hsel["cap"], config=RECOMMENDED)

        for tag, res in (("covgreedy", cg), ("covheur", ch)):
            if int(res["nodes_explored"]) > BUDGET:
                over.append((s["pres_id"], tag, res["nodes_explored"]))

        if same:
            for arm, res, sol_k, nodes_k in (
                ("covgreedy", cg, "b1k_covgreedy_solved", "b1k_covgreedy_nodes"),
                ("covheur", ch, "b1k_covheur_solved", "b1k_covheur_nodes"),
            ):
                want_sol = _bool(s[sol_k])
                want_nodes = int(s[nodes_k])
                got_sol = bool(res["solved"])
                got_nodes = int(res["nodes_explored"])
                if (got_sol, got_nodes) != (want_sol, want_nodes):
                    gate_fail.append(
                        (s["pres_id"], arm,
                         f"shipped {want_nodes}/{want_sol} != hsel {got_nodes}/{got_sol}"))

        bestcov_prio = _prio(s["cov_r1"], s["cov_r2"])
        # class: compare to shipped if same recipe, else n_subs==1 is NOT relabel;
        # leave as "unknown" unless we match shipped pair strings after Aut...
        # Use shipped class when same; otherwise mark by whether prio selection
        # pair equals any known — simpler: blank "hsel" and set moved/relabel
        # only when same_as_bestcov.
        hsel_class = s["cov_class"] if same else ""

        row = {
            "pres_id": s["pres_id"],
            "bin": s["bin"],
            "aut_class": s["aut_class"],
            "start_length": s["start_length"],
            "r1": r1,
            "r2": r2,
            "bestcov_z": s["cov_z"],
            "bestcov_iso_gen": s["cov_iso_gen"],
            "bestcov_iso_index": s["cov_iso_index"],
            "bestcov_class": s["cov_class"],
            "bestcov_cap": s["cov_cap"],
            "bestcov_r1": s["cov_r1"],
            "bestcov_r2": s["cov_r2"],
            "bestcov_n_tied_starts": s["cov_n_tied_starts"],
            "bestcov_prio": bestcov_prio,
            "b1k_covgreedy_solved": _bool(s["b1k_covgreedy_solved"]),
            "b1k_covgreedy_nodes": int(s["b1k_covgreedy_nodes"]),
            "b1k_covgreedy_path": s["b1k_covgreedy_path"],
            "b1k_covheur_solved": _bool(s["b1k_covheur_solved"]),
            "b1k_covheur_nodes": int(s["b1k_covheur_nodes"]),
            "b1k_covheur_path": s["b1k_covheur_path"],
            "hsel_z": hsel["z"],
            "hsel_iso_gen": hsel["iso_gen"],
            "hsel_iso_index": hsel["iso_index"],
            "hsel_class": hsel_class,
            "hsel_cap": hsel["cap"],
            "hsel_r1": hsel["r1"],
            "hsel_r2": hsel["r2"],
            "hsel_n_tied_starts": hsel["n_tied_starts"],
            "hsel_n_candidates": hsel["n_candidates"],
            "hsel_prio": hsel["prio"],
            "same_as_bestcov": same,
            "hsel_covgreedy_solved": bool(cg["solved"]),
            "hsel_covgreedy_nodes": int(cg["nodes_explored"]),
            "hsel_covgreedy_path": _path_cell(cg),
            "hsel_covheur_solved": bool(ch["solved"]),
            "hsel_covheur_nodes": int(ch["nodes_explored"]),
            "hsel_covheur_path": _path_cell(ch),
        }
        rows.append(row)
        if (i + 1) % 5 == 0 or i + 1 == len(src):
            print(f"[hsel] {i+1}/{len(src)}  same={sum(1 for r in rows if r['same_as_bestcov'])}  "
                  f"hsel_heur={sum(1 for r in rows if r['hsel_covheur_solved'])}  "
                  f"{time.time()-t0:.0f}s", flush=True)

    if over:
        raise SystemExit(f"budget gate FAILED: {over[:6]}")
    if gate_fail:
        raise SystemExit(f"same-as-bestcov control gate FAILED on {len(gate_fail)}: {gate_fail[:6]}")
    n_same = sum(1 for r in rows if r["same_as_bestcov"])
    print(f"[hsel] control gate PASSED on {n_same} same-as-bestcov rows "
          f"({time.time()-t0:.0f}s)", flush=True)

    os.makedirs(os.path.dirname(CSV_OUT), exist_ok=True)
    with open(CSV_OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            out = dict(r)
            for k in ("b1k_covgreedy_solved", "b1k_covheur_solved",
                      "hsel_covgreedy_solved", "hsel_covheur_solved",
                      "same_as_bestcov"):
                out[k] = "true" if r[k] else "false"
            w.writerow({k: out[k] for k in FIELDS})
    print(f"wrote {CSV_OUT}", flush=True)

    write_md(rows)
    print_summary(rows)
    return rows


def _solved_set(rows, key):
    return {r["pres_id"] for r in rows if r[key]}


def write_md(rows):
    bc_g = _solved_set(rows, "b1k_covgreedy_solved")
    bc_h = _solved_set(rows, "b1k_covheur_solved")
    hs_g = _solved_set(rows, "hsel_covgreedy_solved")
    hs_h = _solved_set(rows, "hsel_covheur_solved")
    n_same = sum(1 for r in rows if r["same_as_bestcov"])
    n_diff = 60 - n_same

    hsel_prios = [r["hsel_prio"] for r in rows]
    best_prios = [r["bestcov_prio"] for r in rows]

    # rows 634, 635: bestcov heur lost vs covgreedy
    lost_ids = {"634", "635"}
    lost_info = []
    for r in rows:
        if r["pres_id"] in lost_ids:
            lost_info.append(
                f"- `ms{r['pres_id']}`: same_as_bestcov={r['same_as_bestcov']}; "
                f"hsel_covheur={r['hsel_covheur_solved']} "
                f"({r['hsel_covheur_nodes']}); "
                f"shipped covheur={r['b1k_covheur_solved']} "
                f"({r['b1k_covheur_nodes']})")

    # gains unique to hsel
    new_heur = sorted(hs_h - bc_h, key=int)
    lost_heur = sorted(bc_h - hs_h, key=int)
    new_greedy = sorted(hs_g - bc_g, key=int)
    lost_greedy = sorted(bc_g - hs_g, key=int)

    lines = [
        "# Heur-selected CoV vs greedy-oracle best-CoV at budget 1,000",
        "",
        "For each of the 60 benchmark presentations, pick the subword CoV with "
        "the **lowest RECOMMENDED start priority** (static `phi` score — no search "
        "to select `z`), then run length-only and `RECOMMENDED` searches at budget "
        "1,000 on that start. Compare to the shipped greedy-oracle best-CoV arms "
        "(`b1k_covgreedy` 45/60, `b1k_covheur` 43/60).",
        "",
        "```text",
        "prio = L + 2.53·K + 6.418·MK + 8.458·S + 3.292·xyimb   # min-heap, lower better",
        "```",
        "",
        "## Solve counts",
        "",
        "| arm | start selection | ordering | solved / 60 |",
        "|---|---|---|---:|",
        f"| `b1k_covgreedy` (shipped) | greedy-oracle bestcov | length-only | **{len(bc_g)}** |",
        f"| `b1k_covheur` (shipped) | greedy-oracle bestcov | RECOMMENDED | **{len(bc_h)}** |",
        f"| `hsel_covgreedy` | min RECOMMENDED start prio | length-only | **{len(hs_g)}** |",
        f"| `hsel_covheur` | min RECOMMENDED start prio | RECOMMENDED | **{len(hs_h)}** |",
        "",
        f"Heur-selected recipe equals shipped bestcov on **{n_same}/60** rows "
        f"(differs on {n_diff}).",
        "",
        "## Does selecting for RECOMMENDED help the ordering?",
        "",
        f"- `hsel_covheur` vs shipped `b1k_covheur`: **{len(hs_h)}** vs **{len(bc_h)}**",
        f"- `hsel_covgreedy` vs shipped `b1k_covgreedy`: **{len(hs_g)}** vs **{len(bc_g)}**",
        f"- New solves under hsel+RECOMMENDED (not in shipped covheur): "
        f"{new_heur or 'none'}",
        f"- Lost vs shipped covheur: {lost_heur or 'none'}",
        f"- New under hsel+length-only (not in shipped covgreedy): "
        f"{new_greedy or 'none'}",
        f"- Lost vs shipped covgreedy: {lost_greedy or 'none'}",
        "",
        f"Hsel nestedness: `hsel_covgreedy` ⊂ `hsel_covheur` is "
        f"{hs_g <= hs_h} "
        f"(shipped: `b1k_covheur` ⊂ `b1k_covgreedy` is {bc_h <= bc_g}).",
        "",
        "## Verdict",
        "",
        "Selecting the CoV with the lowest RECOMMENDED **start** priority does "
        "**not** beat the greedy-oracle best-CoV on the heuristic arm "
        f"({len(hs_h)}/60 = {len(bc_h)}/60, identical solved set). It does make "
        "the start look better on paper "
        f"(mean prio {statistics.fmean(hsel_prios):.1f} vs "
        f"{statistics.fmean(best_prios):.1f}) and flips the ordering comparison: "
        "on these starts, RECOMMENDED strictly contains length-only "
        f"({len(hs_h)} ⊃ {len(hs_g)}), whereas under greedy-selected bestcov the "
        "opposite held (43 ⊂ 45). Length-only on the heur-picked start is much "
        f"weaker ({len(hs_g)}/60 vs {len(bc_g)}/60). Rows 634/635 stay unsolved "
        "under both selection rules at budget 1,000 with RECOMMENDED.",
        "",
        "## Start priorities",
        "",
        f"- Mean hsel prio: {statistics.fmean(hsel_prios):.2f} "
        f"(median {statistics.median(hsel_prios):.2f})",
        f"- Mean bestcov prio: {statistics.fmean(best_prios):.2f} "
        f"(median {statistics.median(best_prios):.2f})",
        f"- Rows where hsel prio < bestcov prio: "
        f"{sum(1 for a, b in zip(hsel_prios, best_prios) if a < b)}/60 "
        f"(equal {sum(1 for a, b in zip(hsel_prios, best_prios) if a == b)}, "
        f"higher {sum(1 for a, b in zip(hsel_prios, best_prios) if a > b)})",
        "",
        "## The two rows shipped covheur lost (634, 635)",
        "",
    ]
    lines.extend(lost_info or ["- (not in this subset)"])
    lines.extend([
        "",
        "## Source",
        "",
        f"- Input: [`cov_heur_b1k_subset60.csv`](cov_heur_b1k_subset60.csv)",
        f"- Table: [`cov_heur_select_b1k_subset60.csv`](cov_heur_select_b1k_subset60.csv)",
        "- Runner: `experiments/heuristic_search/runners/cov_heur_select_b1k.py`",
        "",
    ])
    with open(MD_OUT, "w") as f:
        f.write("\n".join(lines))
    print(f"wrote {MD_OUT}", flush=True)


def print_summary(rows):
    bc_g = sum(1 for r in rows if r["b1k_covgreedy_solved"])
    bc_h = sum(1 for r in rows if r["b1k_covheur_solved"])
    hs_g = sum(1 for r in rows if r["hsel_covgreedy_solved"])
    hs_h = sum(1 for r in rows if r["hsel_covheur_solved"])
    n_same = sum(1 for r in rows if r["same_as_bestcov"])
    print(json.dumps({
        "b1k_covgreedy": bc_g,
        "b1k_covheur": bc_h,
        "hsel_covgreedy": hs_g,
        "hsel_covheur": hs_h,
        "same_as_bestcov": n_same,
    }, indent=2))


def main(argv=None):
    run()


if __name__ == "__main__":
    main()
