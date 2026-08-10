"""Scout: sign-channel lag (FFT-equivalent) heap term on AC1M-hard Aut split.

Mentor: map X/Y → Fourier for knots. Advisor: use *sign* channel + short lags
(not generator-bipolar ≈ K); select on train 120; evaluate on fresh holdout 60
(+ report spent holdout 60 as second-read confirmatory).

Budget 1000, cap 48. Controls: length, L+20S, L+20S+2MK.
FFT arms: those + wF · Fsign for a short wF grid (selected on train).

    PYTHONPATH=. .venv/bin/python3 -m experiments.heuristic_search.runners.scout_fft_signlag
"""
from __future__ import annotations

import csv
import json
import os
import sys
import time
from datetime import datetime, timezone

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.heuristic_search.core.search_signlag import search_signlag  # noqa: E402
from experiments.heuristic_search.core.signlag_feats import (  # noqa: E402
    pair_fft_scalars, pair_sign_lag,
)
from experiments.heuristic_search.core.hlab import FEATURES, phi  # noqa: E402
from experiments.search.greedy_baseline import (  # noqa: E402
    str_to_arr, reduce_relator_nj, canonical_pair_nj, pack_key,
)
import numpy as np  # noqa: E402

ROOT = _d
SPLIT = os.path.join(ROOT, "results", "heuristic_search", "splits",
                     "splits_ac1m_hard_aut.json")
FRESH = os.path.join(ROOT, "results", "heuristic_search", "splits",
                     "splits_fft_fresh_holdout60.json")
OUT_DIR = os.path.join(ROOT, "results", "heuristic_search", "fft_signlag")
JSONL = os.path.join(OUT_DIR, "runs.jsonl")
RESULTS = os.path.join(OUT_DIR, "RESULTS.md")
BUDGET = 1000
CAP = 48

# wF grid — keep small (anti-overfit)
WF_GRID = (0.0, 2.0, 4.0, 8.0, 16.0)


def _cfg_LS(**w):
    return {"segments": [{"upto": None, "w": dict(w)}]}


CONTROLS = [
    ("length", _cfg_LS(L=1.0), 0.0),
    ("s20", _cfg_LS(L=1.0, S=20.0), 0.0),
    ("s20_mk2", _cfg_LS(L=1.0, S=20.0, MK=2.0), 0.0),
]


def _arms_for_select():
    """Controls + s20 + wF grid (select among these on train)."""
    arms = list(CONTROLS)
    for wF in WF_GRID:
        if wF == 0.0:
            continue  # already have s20
        arms.append((f"s20_F{wF:g}", _cfg_LS(L=1.0, S=20.0), float(wF)))
        arms.append((f"s20_mk2_F{wF:g}",
                     _cfg_LS(L=1.0, S=20.0, MK=2.0), float(wF)))
        arms.append((f"length_F{wF:g}", _cfg_LS(L=1.0), float(wF)))
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
    for arm, cfg, wF in arms:
        for rec in rows:
            key = (half_name, arm, rec["idx"])
            if key in done:
                continue
            res = search_signlag(rec["r1"], rec["r2"], BUDGET, cfg, CAP, wF=wF)
            row = {
                "half": half_name, "arm": arm, "wF": wF,
                "idx": rec["idx"], "L": rec.get("L"),
                "budget": BUDGET, "cap": CAP,
                "solved": bool(res["solved"]),
                "nodes": int(res["nodes_explored"]),
                "solved_at": (int(res["nodes_explored"]) if res["solved"]
                              else None),
                "ts": datetime.now(timezone.utc).isoformat(),
            }
            _append(row)
            n_ok += 1
            if n_ok % 20 == 0:
                print(f"  [{half_name}] {n_ok} new rows  "
                      f"{(time.perf_counter()-t0)/60:.1f} min", flush=True)
    return n_ok


def _rank(half_name):
    by = {}
    for line in open(JSONL):
        r = json.loads(line)
        if r.get("half") != half_name:
            continue
        by.setdefault(r["arm"], []).append(r)
    ranked = []
    for arm, rs in by.items():
        n = len(rs)
        s = sum(1 for r in rs if r["solved"])
        nodes = [r["nodes"] for r in rs if r["solved"]]
        mean_n = (sum(nodes) / len(nodes)) if nodes else None
        ranked.append({
            "arm": arm, "solved": s, "n": n,
            "mean_nodes": mean_n,
            "wF": rs[0].get("wF"),
        })
    ranked.sort(key=lambda r: (-r["solved"],
                               r["mean_nodes"] if r["mean_nodes"] is not None
                               else 1e18))
    return ranked


def _redundancy_report(train_rows):
    """Partial description: correlate Fsign / FFT scalars vs 17 feats on starts."""
    from numpy.linalg import lstsq
    Xs = []
    y_lag = []
    y_fft = []
    for rec in train_rows:
        r1, r2 = rec["r1"], rec["r2"]
        Xs.append(list(phi(r1, r2)))
        # pack for lag
        a1 = reduce_relator_nj(str_to_arr(r1), True)
        a2 = reduce_relator_nj(str_to_arr(r2), True)
        ca, cb = canonical_pair_nj(a1, a2)
        key = pack_key(ca, cb)
        sep = key.index(0)
        codes = np.frombuffer(key[:sep] + key[sep + 1:], dtype=np.uint8)
        y_lag.append(pair_sign_lag(codes, 0, sep, sep, len(key) - sep - 1))
        ff = pair_fft_scalars(r1, r2, channel="sign")
        y_fft.append(ff["FspecK"])
    X = np.asarray(Xs, float)
    # add intercept
    X1 = np.concatenate([X, np.ones((len(X), 1))], axis=1)
    def r2(y):
        y = np.asarray(y, float)
        coef, _, _, _ = lstsq(X1, y, rcond=None)
        pred = X1 @ coef
        ss_res = float(np.sum((y - pred) ** 2))
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        return 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return {
        "R2_signlag_vs_17": r2(y_lag),
        "R2_FspecK_sign_vs_17": r2(y_fft),
        "mean_signlag": float(np.mean(y_lag)),
        "mean_FspecK_sign": float(np.mean(y_fft)),
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    if not os.path.exists(FRESH):
        from experiments.heuristic_search.splits.freeze_fft_fresh_holdout import (
            main as freeze_main)
        freeze_main()

    sp = json.load(open(SPLIT))
    train = sp["train_rows"]
    spent_hold = sp["holdout_rows"]
    fresh = json.load(open(FRESH))["holdout_rows"]

    print("redundancy on train starts…", flush=True)
    red = _redundancy_report(train)
    print(" ", red, flush=True)
    with open(os.path.join(OUT_DIR, "redundancy.json"), "w") as f:
        json.dump(red, f, indent=2)
        f.write("\n")

    arms = _arms_for_select()
    print(f"arms={len(arms)}  train={len(train)}  "
          f"fresh_hold={len(fresh)}  spent_hold={len(spent_hold)}", flush=True)
    # warm
    search_signlag("X", "Y", 20, _cfg_LS(L=1.0), 32, wF=0.0)

    done = _done()
    print("=== TRAIN (select) ===", flush=True)
    _run_half("train", train, arms, done)
    done = _done()
    train_rank = _rank("train")
    print("train top:", train_rank[:8], flush=True)

    # pick best non-control with wF>0 if it beats s20; else best overall among fft
    best_ctrl = max(
        (r for r in train_rank if r["arm"] in ("length", "s20", "s20_mk2")),
        key=lambda r: (r["solved"],
                       -(r["mean_nodes"] or 1e18)))
    fft_cands = [r for r in train_rank if r["arm"] not in
                 ("length", "s20", "s20_mk2")]
    winner = train_rank[0]
    # promote best fft if ≥ best control
    if fft_cands and fft_cands[0]["solved"] >= best_ctrl["solved"]:
        winner = fft_cands[0]
    else:
        # still evaluate top fft cand for honesty
        winner = fft_cands[0] if fft_cands else best_ctrl

    # holdout arms: controls + winner + top fft if different
    hold_names = {"length", "s20", "s20_mk2", winner["arm"]}
    if fft_cands:
        hold_names.add(fft_cands[0]["arm"])
    hold_arms = [a for a in arms if a[0] in hold_names]

    print(f"=== FRESH HOLDOUT (primary) winner_train={winner['arm']} ===",
          flush=True)
    done = _done()
    _run_half("fresh_holdout", fresh, hold_arms, done)

    print("=== SPENT HOLDOUT (second read, confirmatory) ===", flush=True)
    done = _done()
    _run_half("spent_holdout", spent_hold, hold_arms, done)

    fresh_rank = _rank("fresh_holdout")
    spent_rank = _rank("spent_holdout")

    lines = [
        "# FFT / sign-lag scout — AC1M-hard Aut",
        "",
        f"Updated `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "Mentor: map X/Y → Fourier for knots. "
        "Advisor REVISE: **sign channel** + short-lag autocorrelations "
        "(FFT band-energy equivalent; generator-bipolar ≈ K / xyimb).",
        "",
        f"Budget {BUDGET}, cap {CAP}. Engine: `search_signlag` (hfast expand + Fsign).",
        "",
        f"**selected_on** = ac1m_hard_aut train ({len(train)})  ",
        f"**evaluated_on (primary)** = fft fresh holdout ({len(fresh)})  ",
        f"**evaluated_on (confirmatory, 2nd read)** = spent holdout ({len(spent_hold)})",
        "",
        "## Redundancy (train starts vs 17-dim φ)",
        "",
        f"- R²(sign-lag F vs 17 feats) = **{red['R2_signlag_vs_17']:.3f}**",
        f"- R²(FFT FspecK sign vs 17) = **{red['R2_FspecK_sign_vs_17']:.3f}**",
        "",
        "## Train ranking (selection)",
        "",
        "| rank | arm | solved | mean nodes |",
        "|---:|---|---:|---:|",
    ]
    for i, r in enumerate(train_rank[:15], 1):
        mn = f"{r['mean_nodes']:.0f}" if r["mean_nodes"] is not None else "—"
        lines.append(f"| {i} | `{r['arm']}` | {r['solved']}/{r['n']} | {mn} |")
    lines += [
        "",
        f"Promoted for holdout read: `{winner['arm']}` "
        f"(best control on train: `{best_ctrl['arm']}` "
        f"{best_ctrl['solved']}/{best_ctrl['n']}).",
        "",
        "## Fresh holdout (primary)",
        "",
        "| arm | solved | mean nodes |",
        "|---|---:|---:|",
    ]
    for r in fresh_rank:
        mn = f"{r['mean_nodes']:.0f}" if r["mean_nodes"] is not None else "—"
        lines.append(f"| `{r['arm']}` | {r['solved']}/{r['n']} | {mn} |")
    lines += [
        "",
        "## Spent holdout (confirmatory — already used for S+K+MK tune)",
        "",
        "| arm | solved | mean nodes |",
        "|---|---:|---:|",
    ]
    for r in spent_rank:
        mn = f"{r['mean_nodes']:.0f}" if r["mean_nodes"] is not None else "—"
        lines.append(f"| `{r['arm']}` | {r['solved']}/{r['n']} | {mn} |")
    lines += [
        "",
        "## Notes",
        "",
        "- Headline against **s20_mk2 / s20**, not length (length is 0 on this pool).",
        "- Fsign is not invariant under generator-inversion relabel (x↔X); "
          "rotation and r→r⁻¹ are fine.",
        "- Unsolved = unsolved within budget 1000.",
        "",
    ]
    with open(RESULTS, "w") as f:
        f.write("\n".join(lines))
    print("\n".join(lines))
    # csvs
    for name, ranked in (("train", train_rank), ("fresh_holdout", fresh_rank),
                         ("spent_holdout", spent_rank)):
        path = os.path.join(OUT_DIR, f"ranking_{name}.csv")
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["rank", "arm", "solved", "n",
                                              "mean_nodes", "wF"])
            w.writeheader()
            for i, r in enumerate(ranked, 1):
                w.writerow({"rank": i, **r})


if __name__ == "__main__":
    main()
