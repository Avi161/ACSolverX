"""Scout: abelianization-Gram heap term on AC1M-hard Aut 120 / holdouts.

Advisor:
  * Mob/L² BLOCKED (R²≈0.92 vs shipped 17) — kept as a train-only negative control.
  * "Sign asymmetry" = |⟨ab(r1),ab(r2)⟩|/T — this *is* IDEAS.md idea 8.
  * Split A_norm (=num/T) from A_raw (=num/L); T alone is R²≈0.985 redundant.
  * Select on train 120; primary evaluate on virgin asym holdout 60.
  * FFT-fresh 60 = second read; spent Aut 60 = third read.
  * Promote only if same-sign McNemar lift vs s20_mk2 on virgin (and confirmatory).

    PYTHONPATH=. .venv/bin/python3 -m experiments.heuristic_search.runners.scout_asym
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.heuristic_search.core.search_asym import search_asym  # noqa: E402
from experiments.heuristic_search.core.abel_gram_feats import (  # noqa: E402
    pair_abel_gram_words,
)
from experiments.heuristic_search.core.hlab import FEATURES, phi  # noqa: E402

ROOT = _d
SPLIT = os.path.join(ROOT, "results", "heuristic_search", "splits",
                     "splits_ac1m_hard_aut.json")
FRESH_FFT = os.path.join(ROOT, "results", "heuristic_search", "splits",
                         "splits_fft_fresh_holdout60.json")
VIRGIN = os.path.join(ROOT, "results", "heuristic_search", "splits",
                      "splits_asym_virgin_holdout60.json")
OUT_DIR = os.path.join(ROOT, "results", "heuristic_search", "asym_scout")
JSONL = os.path.join(OUT_DIR, "runs.jsonl")
RESULTS = os.path.join(OUT_DIR, "ASYM.md")
BUDGET = 1000
CAP = 48

# advisor: shrink to 5 values incl 0; both signs
WA_GRID = (0.0, -8.0, -3.0, 3.0, 8.0)
MODES = ("norm", "raw")  # + mob negative control separately


def _cfg_LS(**w):
    return {"segments": [{"upto": None, "w": dict(w)}]}


CONTROLS = [
    ("length", _cfg_LS(L=1.0), 0.0, "norm"),
    ("s20", _cfg_LS(L=1.0, S=20.0), 0.0, "norm"),
    ("s20_mk2", _cfg_LS(L=1.0, S=20.0, MK=2.0), 0.0, "norm"),
]


def _tag(base, mode, wA):
    if wA == 0.0:
        return base
    sign = "m" if wA < 0 else "p"
    return f"{base}_A{mode}{sign}{abs(wA):g}"


def _arms_for_select():
    """Controls + base×mode×nonzero weights + Mob/L² negative controls (train)."""
    arms = list(CONTROLS)
    bases = [
        ("length", _cfg_LS(L=1.0)),
        ("s20", _cfg_LS(L=1.0, S=20.0)),
        ("s20_mk2", _cfg_LS(L=1.0, S=20.0, MK=2.0)),
    ]
    for base, cfg in bases:
        for mode in MODES:
            for wA in WA_GRID:
                if wA == 0.0:
                    continue
                arms.append((_tag(base, mode, wA), cfg, float(wA), mode))
    # Mob/L² negative control only (BLOCKED) — train evidence, not for promotion
    for base, cfg in bases:
        for wA in (-8.0, 8.0):
            arms.append((_tag(base, "mob", wA), cfg, float(wA), "mob"))
    return arms


def _append(row):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(JSONL, "a") as f:
        f.write(json.dumps(row) + "\n")
        f.flush()
        os.fsync(f.fileno())


def _done():
    s = set()
    if not os.path.exists(JSONL):
        return s
    for line in open(JSONL):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        s.add((r.get("half"), r.get("arm"), r.get("idx")))
    return s


def _run_half(half_name, rows, arms, done):
    n_ok = 0
    t0 = time.perf_counter()
    for arm, cfg, wA, mode in arms:
        for rec in rows:
            key = (half_name, arm, rec["idx"])
            if key in done:
                continue
            res = search_asym(rec["r1"], rec["r2"], BUDGET, cfg, CAP,
                              wA=wA, mode=mode)
            row = {
                "half": half_name, "arm": arm,
                "wA": wA, "mode": mode,
                "idx": rec["idx"], "L": rec.get("L"),
                "budget": BUDGET, "cap": CAP,
                "solved": bool(res["solved"]),
                "nodes": int(res["nodes_explored"]),
                "solved_at": (int(res["nodes_explored"]) if res["solved"]
                              else None),
                "min_L": int(res["min_relator_length"]),
                "goal_hidden": bool(res["goal_hidden"]),
                "ts": datetime.now(timezone.utc).isoformat(),
            }
            _append(row)
            n_ok += 1
            if n_ok % 20 == 0:
                print(f"  [{half_name}] {n_ok} new rows  "
                      f"{(time.perf_counter()-t0)/60:.1f} min", flush=True)
    return n_ok


def _load_rows(path, side):
    d = json.load(open(path))
    if side in d:
        rows = d[side]
    elif "holdout_rows" in d:
        rows = d["holdout_rows"]
    else:
        raise KeyError(side)
    # ensure idx
    out = []
    for i, r in enumerate(rows):
        rr = dict(r)
        if "idx" not in rr:
            rr["idx"] = i
        out.append(rr)
    return out


def _by_arm(half):
    by = defaultdict(dict)  # arm -> idx -> row
    if not os.path.exists(JSONL):
        return by
    for line in open(JSONL):
        r = json.loads(line)
        if r.get("half") != half:
            continue
        by[r["arm"]][r["idx"]] = r
    return by


def _score(by_arm):
    out = []
    for arm, mp in by_arm.items():
        rs = list(mp.values())
        sol = [r for r in rs if r["solved"]]
        gh = sum(1 for r in rs if r.get("goal_hidden"))
        mean_n = (sum(r["nodes"] for r in sol) / len(sol)) if sol else None
        sample = rs[0]
        out.append({
            "arm": arm,
            "wA": sample.get("wA", 0.0),
            "mode": sample.get("mode", "norm"),
            "n": len(rs),
            "solved": len(sol),
            "goal_hidden": gh,
            "mean_nodes": mean_n,
        })
    out.sort(key=lambda r: (-r["solved"],
                            r["mean_nodes"] if r["mean_nodes"] is not None
                            else 1e18))
    return out


def _mcnemar(a_map, b_map):
    """Return (b_only, c_only, n_both, delta, exact_binom_p) for A vs B.

    b = A solves, B fails; c = B solves, A fails. delta = b - c.
    Two-sided exact binomial on discordants.
    """
    idxs = set(a_map) & set(b_map)
    b = c = both = 0
    for i in idxs:
        sa = bool(a_map[i]["solved"])
        sb = bool(b_map[i]["solved"])
        if sa and sb:
            both += 1
        elif sa and not sb:
            b += 1
        elif sb and not sa:
            c += 1
    n = b + c
    if n == 0:
        p = 1.0
    else:
        # two-sided exact binomial under p=0.5
        k = min(b, c)
        # P(X<=k) + P(X>=n-k) with X~Bin(n,0.5); for k < n/2 that's 2*cdf
        cdf = sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
        p = min(1.0, 2.0 * cdf)
    return b, c, both, b - c, p


def _decidable(maps):
    """Rows where at least two arms disagree on solved."""
    idxs = set()
    for m in maps.values():
        idxs |= set(m)
    dec = []
    for i in idxs:
        vals = {bool(m[i]["solved"]) for m in maps.values() if i in m}
        if len(vals) > 1:
            dec.append(i)
    return dec


def _r2_report(train_rows):
    """R² of asym / num / T / Mob_L2 vs the 17 shipped features on train starts."""
    X = []
    ys = {"asym": [], "num": [], "T": [], "Mob_L2": [], "num_L": []}
    for r in train_rows:
        feats = phi(r["r1"], r["r2"])  # tuple ordered like FEATURES
        X.append(list(feats))
        g = pair_abel_gram_words(r["r1"], r["r2"])
        for k in ys:
            ys[k].append(g[k] if k != "Mob_L2" else g["Mob_L2"])
    X = np.asarray(X, dtype=np.float64)
    # add intercept
    A = np.concatenate([np.ones((len(X), 1)), X], axis=1)
    out = {}
    for k, y in ys.items():
        y = np.asarray(y, dtype=np.float64)
        # least squares
        coef, _, _, _ = np.linalg.lstsq(A, y, rcond=None)
        pred = A @ coef
        ss_res = float(np.sum((y - pred) ** 2))
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        out[k] = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return out


def _half_split_optimism(by_arm, seed=0):
    """Measured best-of-N optimism: disagree rate of winners across half-splits."""
    rng = np.random.default_rng(seed)
    arms = [a for a in by_arm if a not in ()]
    if not arms:
        return None
    idxs = sorted(set().union(*(set(by_arm[a]) for a in arms)))
    if len(idxs) < 4:
        return None
    winners = []
    for _ in range(7):
        rng.shuffle(idxs)
        half = idxs[: len(idxs) // 2]
        best, best_n = None, -1
        for a in arms:
            n = sum(1 for i in half if by_arm[a].get(i, {}).get("solved"))
            if n > best_n:
                best, best_n = a, n
        winners.append(best)
    return {
        "n_splits": 7,
        "n_distinct_winners": len(set(winners)),
        "winners": winners,
    }


def write_results(train_rows):
    halves = {
        "train": _by_arm("train"),
        "virgin": _by_arm("virgin"),
        "fft": _by_arm("fft"),
        "spent": _by_arm("spent"),
    }
    scores = {h: _score(m) for h, m in halves.items()}
    r2 = _r2_report(train_rows)
    opt = _half_split_optimism(halves["train"])

    # select winner among non-mob asym arms on train (exclude pure controls' mob)
    cand = [r for r in scores["train"]
            if r["mode"] in ("norm", "raw") and r["wA"] != 0.0]
    # also allow wA=0 controls as the null selection
    cand += [r for r in scores["train"] if r["arm"] in ("length", "s20", "s20_mk2")]
    cand.sort(key=lambda r: (-r["solved"],
                             r["mean_nodes"] if r["mean_nodes"] is not None
                             else 1e18))
    winner = cand[0] if cand else None
    base = next((r for r in scores["train"] if r["arm"] == "s20_mk2"), None)

    lines = [
        "# Abelianization-Gram / asym scout",
        "",
        f"Updated `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "**selected_on** = `splits_ac1m_hard_aut` train 120",
        "**evaluated_on (primary, first read)** = `splits_asym_virgin_holdout60`",
        "**evaluated_on (second read)** = `splits_fft_fresh_holdout60`",
        "**evaluated_on (third read)** = `splits_ac1m_hard_aut` holdout 60",
        "",
        "Budget 1000 / cap 48. Heap term = shipped base + `wA · feat`.",
        "",
        "## Verdict framing",
        "",
        "- **Mob/L² is BLOCKED** as an ordering feature "
        f"(R² vs 17 shipped = {r2.get('Mob_L2', float('nan')):.3f}). "
        "Train-only negative-control arms are reported below; do not promote.",
        "- **asym = |⟨ab(r1),ab(r2)⟩|/T is IDEAS.md idea 8** (abelianized-distance "
        "priority), not a new sign-channel mechanism. Prior kill-first on solved "
        "paths: length↑∧abel↓ in 0.4% of steps. This scout re-tests the *same-length "
        "ordering* escape hatch.",
        f"- R² on train starts: asym={r2['asym']:.3f}, num={r2['num']:.3f}, "
        f"num/L={r2['num_L']:.3f}, T={r2['T']:.3f}, Mob/L²={r2['Mob_L2']:.3f}.",
        "",
    ]
    if opt:
        lines += [
            f"- Best-of-N optimism (7 half-splits on train): "
            f"{opt['n_distinct_winners']} distinct winners "
            f"`{opt['winners']}`.",
            "",
        ]
    if winner and base:
        lines += [
            f"## Train selection winner: `{winner['arm']}`",
            "",
            f"mode={winner['mode']}, wA={winner['wA']:g} → "
            f"**{winner['solved']}/{winner['n']}** "
            f"(goal_hidden={winner['goal_hidden']})"
            + (f", mean nodes {winner['mean_nodes']:.0f}"
               if winner["mean_nodes"] is not None else ""),
            f"Control `s20_mk2`: **{base['solved']}/{base['n']}** "
            f"(goal_hidden={base['goal_hidden']}).",
            "",
        ]

    # holdout tables
    for half, label in (("virgin", "Primary virgin 60"),
                        ("fft", "Second-read FFT-fresh 60"),
                        ("spent", "Third-read spent Aut 60")):
        sc = scores[half]
        if not sc:
            lines += [f"## {label}", "", "(not run yet)", ""]
            continue
        lines += [
            f"## {label}",
            "",
            "| arm | mode | wA | solved | Δ vs s20_mk2 | goal_hidden | mean nodes |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
        base_n = next((r["solved"] for r in sc if r["arm"] == "s20_mk2"), 0)
        for r in sc:
            delta = r["solved"] - base_n
            mn = (f"{r['mean_nodes']:.0f}" if r["mean_nodes"] is not None
                  else "—")
            lines.append(
                f"| `{r['arm']}` | {r['mode']} | {r['wA']:g} | "
                f"**{r['solved']}/{r['n']}** | {delta:+d} | "
                f"{r['goal_hidden']} | {mn} |"
            )
        # McNemar vs s20_mk2 for top non-control
        amap = halves[half]
        if "s20_mk2" in amap and winner and winner["arm"] in amap:
            b, c, both, delta, p = _mcnemar(amap[winner["arm"]],
                                            amap["s20_mk2"])
            lines += [
                "",
                f"McNemar `{winner['arm']}` vs `s20_mk2`: "
                f"b(win-only)={b}, c(base-only)={c}, both={both}, "
                f"Δ={delta:+d}, exact two-sided p={p:.4f}.",
            ]
        # decidable subset
        if winner and winner["arm"] in amap and "s20_mk2" in amap:
            dec = _decidable({winner["arm"]: amap[winner["arm"]],
                              "s20_mk2": amap["s20_mk2"]})
            if dec:
                w_dec = sum(1 for i in dec if amap[winner["arm"]][i]["solved"])
                b_dec = sum(1 for i in dec if amap["s20_mk2"][i]["solved"])
                lines.append(
                    f"Decidable subset (disagree rows): "
                    f"`{winner['arm']}` {w_dec}/{len(dec)} vs "
                    f"`s20_mk2` {b_dec}/{len(dec)}."
                )
        lines.append("")

    # train full table (compact)
    lines += [
        "## Train 120 ranking (all arms)",
        "",
        "| rank | arm | mode | wA | solved | goal_hidden | mean nodes |",
        "|---:|---|---|---:|---:|---:|---:|",
    ]
    for i, r in enumerate(scores["train"], 1):
        mn = (f"{r['mean_nodes']:.0f}" if r["mean_nodes"] is not None else "—")
        lines.append(
            f"| {i} | `{r['arm']}` | {r['mode']} | {r['wA']:g} | "
            f"{r['solved']}/{r['n']} | {r['goal_hidden']} | {mn} |"
        )
    lines += [
        "",
        "## Promotion bar",
        "",
        "Promote only if: same-sign Δ vs `s20_mk2` on virgin **and** at least "
        "one confirmatory read; McNemar exact p suggests real lift (target "
        "ballpark ≥ +6/60 discordant net, but report b,c,p not a hard cutoff); "
        "no systematic `goal_hidden` inflation; and a mechanism story for the "
        "**sign of wA** (wA>0 = idea-8 as written; wA<0 = opposite).",
        "",
        "Do **not** promote Mob/L² from this file.",
        "",
    ]
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(RESULTS, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[write] {RESULTS}", flush=True)
    return winner


def main():
    if not os.path.exists(VIRGIN):
        print("[freeze] virgin holdout missing — freezing now", flush=True)
        from experiments.heuristic_search.splits.freeze_asym_virgin_holdout import (
            main as freeze_main,
        )
        freeze_main()

    sp = json.load(open(SPLIT))
    train = _load_rows(SPLIT, "train_rows")
    spent = _load_rows(SPLIT, "holdout_rows")
    fft = _load_rows(FRESH_FFT, "holdout_rows")
    virgin = _load_rows(VIRGIN, "holdout_rows")

    arms = _arms_for_select()
    print(f"[scout] {len(arms)} arms × train {len(train)} "
          f"(+ holdouts after selection)", flush=True)
    # warm one search
    search_asym(train[0]["r1"], train[0]["r2"], 50,
                _cfg_LS(L=1.0), CAP, wA=0.0, mode="norm")

    done = _done()
    n = _run_half("train", train, arms, done)
    print(f"[train] +{n} rows", flush=True)
    write_results(train)

    # freeze selection: top train arm among norm/raw (incl controls)
    ranked = _score(_by_arm("train"))
    cand = [r for r in ranked
            if r["mode"] in ("norm", "raw")]
    winner_arm = cand[0]["arm"] if cand else "s20_mk2"
    # evaluate winner + controls + winner's mode siblings at same |wA|? keep small:
    # fixed: controls + train winner + best mob neg-control (for honesty on train only)
    eval_names = {"length", "s20", "s20_mk2", winner_arm}
    # also include best opposite-sign sibling of winner if exists
    wrow = next(r for r in ranked if r["arm"] == winner_arm)
    if wrow["wA"] != 0.0:
        # include wA=0 already; include ± of both modes at same |w| on s20_mk2 base
        for mode in MODES:
            for s in (-1.0, 1.0):
                eval_names.add(_tag("s20_mk2", mode, s * abs(wrow["wA"])))
                eval_names.add(_tag("s20", mode, s * abs(wrow["wA"])))
    eval_arms = [a for a in arms if a[0] in eval_names]
    # ensure winner present
    if not any(a[0] == winner_arm for a in eval_arms):
        eval_arms.append(next(a for a in arms if a[0] == winner_arm))

    print(f"[holdout] evaluating {len(eval_arms)} arms: "
          f"{[a[0] for a in eval_arms]}", flush=True)
    done = _done()
    for half, rows in (("virgin", virgin), ("fft", fft), ("spent", spent)):
        n = _run_half(half, rows, eval_arms, done)
        print(f"[{half}] +{n} rows", flush=True)
        done = _done()
    winner = write_results(train)
    print(f"[done] train winner={winner['arm'] if winner else None}", flush=True)


if __name__ == "__main__":
    main()
