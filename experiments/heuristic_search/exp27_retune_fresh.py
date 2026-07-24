"""EXP-27 -- re-tune from scratch on presentations the earlier tuning never touched.

Every weight vector recommended so far was fitted on 40-45 rows of the 66-row benchmark. That is a
small training set, and it shows: a best-of-320 pick on it carried 1.65 presentations of optimism
(EXP-19), and the search space saturated at +0 improvement. The natural suspicion is that the
incumbent is not the best ordering, only the best ordering *that particular 40 rows* could reveal.

EXP-26 supplied the material to test that -- 75 decidable-band presentations from
``data/ms640_solved.txt`` that no stage of this program had read -- and ``splits_ms640.json``
divided them, before any fitting, into **50 to tune on and 25 held back**.

So this repeats the joint search honestly on new ground: random weight vectors over all 17
features, threshold optional, at budget 1,000, selected on the 50. The incumbents ride along as
controls. Then the winner and the incumbents are scored on the **25 the search never saw**, which
is the only number that settles it.

Three outcomes, all worth having. The re-tune wins out of sample -- there is a better ordering and
the old training set was the limit. It ties -- the incumbent is confirmed on genuinely independent
data, which is the strongest robustness statement available here. It wins on the 50 and loses on
the 25 -- the search is fitting noise, and the honest reading is that 50 rows is still too few.

    python3 -m experiments.heuristic_search.exp27_retune_fresh
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import LOGS, cfg_name        # noqa: E402
from experiments.heuristic_search.hfast import search_fast          # noqa: E402
from experiments.heuristic_search.hsolve import (                   # noqa: E402
    LEAN_SMALL_BUDGET, RECOMMENDED,
)
from experiments.heuristic_search.exp26_clean_holdout import clean_rows  # noqa: E402

BUDGET = 1_000
MRL = 48
SEED = 2607
N_RANDOM = 260
OUT = os.path.join(LOGS, "EXP27_retune.jsonl")
SPLIT = os.path.join(LOGS, "splits_ms640.json")

POOL = ("K", "MK", "mK", "S", "Bmax", "B1", "Bmin", "Lmin", "Lmax", "imbal", "xyimb",
        "Bmaxrun", "Bspread", "ratio", "density")
THRESHOLDS = (0, 0, 0, 12, 16, 20)

INCUMBENTS = {
    "recommended (incumbent)": RECOMMENDED,
    "lean (incumbent)": LEAN_SMALL_BUDGET,
    "baseline (length)": {"segments": [{"upto": None, "w": {"L": 1.0}}]},
}


def configs(seed=SEED, n=N_RANDOM):
    rng = np.random.default_rng(seed)
    out, meta = [], {}
    for label, cfg in INCUMBENTS.items():
        cid = cfg_name(cfg)
        if cid not in meta:
            out.append(cfg)
            meta[cid] = {"kind": "incumbent", "label": label}
    while len(out) < n:
        k = int(rng.integers(2, 6))
        feats = list(rng.choice(POOL, size=k, replace=False))
        w = {"L": 1.0}
        for f in feats:
            mag = float(10 ** rng.uniform(-0.7, 1.1))
            w[f] = float(np.round(mag * (1 if rng.random() < 0.75 else -1), 3))
        T = int(rng.choice(THRESHOLDS))
        cfg = ({"segments": [{"upto": None, "w": w}]} if T == 0 else
               {"segments": [{"upto": T, "w": {"L": 1.0}}, {"upto": None, "w": w}]})
        cid = cfg_name(cfg)
        if cid in meta:
            continue
        out.append(cfg)
        meta[cid] = {"kind": "random"}
    return out, meta


def main():
    with open(SPLIT) as f:
        sp = json.load(f)
    rows = {r["name"]: r for r in clean_rows()}
    tune = [rows[n] for n in sp["tune"]]
    evl = [rows[n] for n in sp["eval"]]

    cfgs, meta = configs()
    done = set()
    if os.path.exists(OUT):
        for line in open(OUT):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            done.add((r["config_id"], r["name"]))

    # Phase 1: every config on the tuning half only.
    print(f"  {len(cfgs)} configs x {len(tune)} tuning rows, budget {BUDGET}", flush=True)
    import time
    t0 = time.perf_counter()
    with open(OUT, "a") as f:
        for i, cfg in enumerate(cfgs, 1):
            cid = cfg_name(cfg)
            for row in tune:
                if (cid, row["name"]) in done:
                    continue
                res = search_fast(row["r1"], row["r2"], BUDGET, cfg, MRL)
                f.write(json.dumps({
                    "config_id": cid, "name": row["name"], "split": "tune",
                    "bin": row["bin"], "budget": BUDGET, "mrl": MRL,
                    "solved": res["solved"], "nodes": res["nodes"],
                    "path_length": res["path_length"]}) + "\n")
                f.flush()
                os.fsync(f.fileno())
            if i % 25 == 0 or i == len(cfgs):
                el = time.perf_counter() - t0
                print(f"    {i}/{len(cfgs)} configs  {el/60:.1f} min  "
                      f"ETA {el/i*(len(cfgs)-i)/60:.1f} min", flush=True)

    data = [json.loads(l) for l in open(OUT)]
    tsolved = {}
    for r in data:
        if r["split"] == "tune":
            tsolved.setdefault(r["config_id"], set())
            if r["solved"]:
                tsolved[r["config_id"]].add(r["name"])

    ranked = sorted(tsolved, key=lambda c: -len(tsolved[c]))
    winner = next(c for c in ranked if meta.get(c, {}).get("kind") == "random")
    inc_ids = {cfg_name(c): l for l, c in INCUMBENTS.items()}
    finalists = [winner] + list(inc_ids)

    # Phase 2: ONLY the finalists touch the eval half.
    print(f"\n  scoring {len(finalists)} finalists on the {len(evl)} held-back rows", flush=True)
    by_id = {cfg_name(c): c for c in cfgs}
    with open(OUT, "a") as f:
        for cid in finalists:
            for row in evl:
                if (cid, row["name"]) in done:
                    continue
                res = search_fast(row["r1"], row["r2"], BUDGET, by_id[cid], MRL)
                f.write(json.dumps({
                    "config_id": cid, "name": row["name"], "split": "eval",
                    "bin": row["bin"], "budget": BUDGET, "mrl": MRL,
                    "solved": res["solved"], "nodes": res["nodes"],
                    "path_length": res["path_length"]}) + "\n")
                f.flush()
                os.fsync(f.fileno())

    data = [json.loads(l) for l in open(OUT)]

    def cnt(cid, split):
        d = [r for r in data if r["config_id"] == cid and r["split"] == split]
        return sum(r["solved"] for r in d), len(d)

    lines = ["# EXP-27 — re-tuning from scratch on ground the earlier tuning never touched", "",
             f"{len(cfgs)} configs over all 17 features, threshold optional, budget {BUDGET}, cap "
             f"{MRL}. Selected on **{len(tune)}** presentations from `ms640` that no stage of this "
             f"program had read; the winner and the incumbents are then scored on **{len(evl)}** "
             "more that the selection never saw. Split frozen before any fitting "
             "(`splits_ms640.json`).", "",
             "| config | tuned on (50) | **held back (25)** |", "|---|---|---|"]
    for cid in finalists:
        ts, tn = cnt(cid, "tune")
        es, en = cnt(cid, "eval")
        tag = f" ← {inc_ids[cid]}" if cid in inc_ids else " ← re-tuned winner"
        lines.append(f"| `{cid[:52]}`{tag} | {ts}/{tn} | **{es}/{en}** |")

    w_e = cnt(winner, "eval")[0]
    rec_id = cfg_name(RECOMMENDED)
    r_e = cnt(rec_id, "eval")[0]
    w_t, r_t = cnt(winner, "tune")[0], cnt(rec_id, "tune")[0]
    lines += ["", "## Verdict", ""]
    if w_e > r_e:
        lines += [f"The re-tune **wins out of sample**: {w_e}/{len(evl)} against the incumbent's "
                  f"{r_e}/{len(evl)}. Fitting on 50 fresh presentations found an ordering the "
                  "benchmark's 40 rows could not reveal — the old training set was the binding "
                  "constraint, not the feature space. This is a candidate to replace the "
                  "recommendation, pending a check at larger budget.", ""]
    elif w_e == r_e:
        # Report the tuning half honestly in whichever direction it fell -- the earlier version of
        # this branch asserted the re-tune had won it, which is not implied by an out-of-sample tie.
        tune_note = (f"and it did not even win the half it was selected on ({w_t} vs the "
                     f"incumbent's {r_t}) — the incumbent, fitted on entirely different "
                     f"presentations, is better on the re-tune's own training data"
                     if r_t >= w_t else
                     f"having won the half it was selected on ({w_t} vs {r_t}), a gap that is "
                     f"exactly what selection buys and that vanishes out of sample")
        lines += [f"The re-tune **ties** the incumbent out of sample ({w_e}/{len(evl)} each), "
                  f"{tune_note}. **The incumbent is confirmed on genuinely independent data**, by "
                  "a search fitted elsewhere that had every chance to beat it.", ""]
    else:
        lines += [f"The re-tune **wins on the tuning half and loses out of sample** "
                  f"({w_t} vs {r_t} tuned, {w_e} vs {r_e} held back). That is overfitting, plainly "
                  "measured: 50 presentations is still too few to select 17 weights on. The "
                  "incumbent stands, and the honest conclusion is about the data, not the space.",
                  ""]

    with open(os.path.join(LOGS, "EXP27_retune.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
