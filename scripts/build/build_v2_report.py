#!/usr/bin/env python3
"""Phase 8 -- acceptance report for the v2 data-crafting build (4.0.DETAILED_STEPS §8).

`build_report()` is a PURE, testable function: it reads the shipping artifacts (the committed
`dot_archive_v2.jsonl` + `dot_splits_v2.npz`), the Phase-0 baseline, the percentiles, and the
trap-set; computes every headline number; runs all §8 acceptance assertions (raises SystemExit
on failure); and writes `data/derived/dot/v2_report.json`. The `5.0.v2_acceptance_report.ipynb`
notebook is a thin presentation layer that calls this and renders matplotlib panels -- so the
numbers and the green/red gates are unit-testable without running a notebook.

Run from the repo root:
    ../.venv/bin/python scripts/build/build_v2_report.py

Honesty framing baked into the report (Field-Advisor warm-pre, c.1/c.2/d.2 + Q3 caveats):
  * `counterexample_eval` (8 named) is ALL-HARD with no ground-truth d-o-t -> NO MAE. A constant
    model passes it. It is a length-stratified SEPARATION/RANKING metric: P(eval) >> P(short-easy),
    reported as a contrast, never a bare value, never length-aggregated. 5/6 AK(n) are len>=15
    (passable by the long=>hard shortcut); the real short-hard probe is {AK(3), Length-14 x2} (n=3).
  * The HEADLINE band loss-mass is the TRAIN-fold cut ("what actually trains"); the whole-archive
    .256/.358/.128/.257 is the Phase-5 invariant to reproduce. Freezing hard_test + the x0.5 tail
    discount doubly-deplete train's hard_solved mass below .128.
  * Hardness eval leads with Spearman on `hard_test` (1,671 real labels); the named set is the anchor.
  * bound_B (48/150) is a HEURISTIC floor, never a lower bound; B_hard=150 for AK(3) can err in BOTH
    directions (solved p99, no group-theory backing). AK(n) are POTENTIAL counterexamples, never
    "non-trivializable". hard_test membership is itself upper-bound-contaminated + heteroscedastic.
"""
import os
import sys
import json

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # repo root
from scripts.lib import canon              # noqa: E402
from scripts.lib import dot_config as cfg  # noqa: E402
from scripts.lib import dot_dataset as dd  # noqa: E402
from scripts.build import build_training_archive as bt  # noqa: E402

REPORT_JSON = "data/derived/dot/v2_report.json"
AK3_KEY = "YXYxyx|YYYYxxx"
LOOKALIKE_KEY = "YXyxYx|YYYYxxx"
BAND_MASS_TOL = 0.03            # Phase 5.5 tolerance (the x0.5/x3 multipliers perturb exact targets)
SHORT_EASY_LENS = (13, 14)     # length-matched contrast for the n=3 short-hard probe (FA c.1)


def _native(o):
    """Recursively convert numpy scalars/arrays/bools to JSON-native python types."""
    if isinstance(o, dict):
        return {k: _native(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_native(v) for v in o]
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return _native(o.tolist())
    return o


def _region(r):
    """easy/valley/hard_solved for labelled rows; hard_unsolved for censored+named."""
    return "hard_unsolved" if r["censored"] else cfg.band_of(r["min_dot"])


def _band_mass(rows, idx, weights):
    """Per-region share of total weight over the rows at `idx`."""
    regions = cfg.TARGET_SHARES.keys()
    tot = float(sum(weights[i] for i in idx)) or 1.0
    out = {b: 0.0 for b in regions}
    for i in idx:
        out[_region(rows[i])] += weights[i]
    return {b: out[b] / tot for b in regions}


def build_report(archive_v2=None, splits_npz=None, baseline_json=None, percentiles_json=None,
                 trap_set_json=None, out=REPORT_JSON, write=True, rederive=True):
    archive_v2 = archive_v2 or cfg.ARCHIVE_V2
    splits_npz = splits_npz or cfg.SPLIT_NPZ_V2
    baseline_json = baseline_json or cfg.BASELINE_JSON
    percentiles_json = percentiles_json or cfg.PERCENTILES_JSON
    trap_set_json = trap_set_json or cfg.TRAP_SET_JSON

    rows = dd._load_rows_in_order(archive_v2)
    n = len(rows)
    keys = [f"{r['r1']}|{r['r2']}" for r in rows]
    weights = np.array([r["weight"] for r in rows], dtype=np.float64)
    baseline = json.load(open(baseline_json))
    perc = json.load(open(percentiles_json))
    trap = json.load(open(trap_set_json))
    named_label_of = {v: k for k, v in trap["groups"]["named"].items()}

    z = np.load(splits_npz, allow_pickle=False)
    folds = ("train", "val", "test", "hard_test", "counterexample_eval")
    fold_idx = {f: z[f].tolist() for f in folds}
    key_in = {f: {keys[i] for i in fold_idx[f]} for f in folds}

    # ---- distribution: whole-archive vs train-fold band loss-mass (FA: headline the train cut) ----
    all_idx = list(range(n))
    band_mass_archive = _band_mass(rows, all_idx, weights)
    band_mass_train = _band_mass(rows, fold_idx["train"], weights)
    target = dict(cfg.TARGET_SHARES)

    # ---- d-o-t histogram raw (count) vs weighted, labelled only ----
    lab = [i for i in all_idx if not rows[i]["censored"]]
    dots = np.array([rows[i]["min_dot"] for i in lab], dtype=float)
    wlab = weights[lab]
    hist_edges = [0, 6, 11, 21, 31, 51, 76, 101, 151, 400]
    raw_hist, _ = np.histogram(dots, bins=hist_edges)
    wt_hist, _ = np.histogram(dots, bins=hist_edges, weights=wlab)
    dot_hist = {"edges": hist_edges,
                "raw": raw_hist.astype(int).tolist(),
                "weighted": np.round(wt_hist, 2).tolist()}

    # ---- length x hardness 2-D: v2 vs baseline; hard (censored+named) length spread ----
    by_len = {}
    for i, r in enumerate(rows):
        L = r["total_len"]
        d = by_len.setdefault(L, {"n_solved": 0, "solved_dots": [], "n_hard": 0})
        if r["censored"]:
            d["n_hard"] += 1
        else:
            d["n_solved"] += 1
            d["solved_dots"].append(r["min_dot"])
    length_hardness_v2 = []
    for L in sorted(by_len):
        d = by_len[L]
        tot = d["n_solved"] + d["n_hard"]
        length_hardness_v2.append({
            "total_len": L, "n_solved": d["n_solved"], "n_hard": d["n_hard"],
            "solved_median_dot": float(np.median(d["solved_dots"])) if d["solved_dots"] else None,
            "hard_frac": d["n_hard"] / tot if tot else 0.0})
    # the "spread" headline: hard mass by length, baseline (censored only) vs v2 (censored+named)
    hard_len_v2 = {str(d["total_len"]): d["n_hard"] for d in length_hardness_v2 if d["n_hard"]}
    hard_len_baseline = {str(k): v for k, v in baseline["censored_len_dist"].items()}

    # ---- provenance: source mix per band ----
    # NB: only the 8 named anchors are "anchor"; generic censored rows merely have empty `sources`
    # (search found no path) -- do NOT fold them into "anchor" (4,954 != 8).
    src_by_band = {b: {} for b in target}
    for r in rows:
        b = _region(r)
        if r["tier"] == "named":
            s = "anchor"
        elif r["sources"]:
            s = "+".join(sorted(r["sources"]))
        else:
            s = "censored (no source recorded)"
        src_by_band[b][s] = src_by_band[b].get(s, 0) + 1

    # ---- per-fold counts + per-fold band loss-mass ----
    fold_counts = {}
    for f in folds:
        idx = fold_idx[f]
        cens = sum(1 for i in idx if rows[i]["censored"])
        fold_counts[f] = {"n": len(idx), "labelled": len(idx) - cens, "censored": cens,
                          "band_mass": _band_mass(rows, idx, weights)}

    # ---- eval reframing (FA c.1/d.2 + post §2.A/§2.B, corrected) ----
    # The eval metric is SEPARATION of the anchor's predicted d-o-t vs a short-easy baseline; there is
    # NO ground truth on the anchors (so B_hard=150 is irrelevant to this read) -> NO MAE. A length-
    # exploiting REGRESSION head predicts ~ E[d-o-t | length] = solved_median_dot(L), which rises
    # MONOTONICALLY with length (13->6 ... 23->23). Against v1's single len-13-14 baseline (median ~6)
    # that buys a *spurious* separation that GROWS with length: AK(6/7/8)@19/21/23 are the MOST length-
    # gameable anchors (+9/+12/+17), not the least. The len<=14 anchors are length-matched to the
    # baseline (~0 spurious sep); their residual confound is r1-cousin leakage (AK(3)). Constructive
    # fix (model plan): PER-LENGTH-matched baselines P(AK(n)@L) >> P(solved@L) -- removes the length
    # confound from ALL 8 anchors. Do NOT call the long anchors "clean" under the current single baseline.
    LH = {d["total_len"]: d for d in length_hardness_v2}
    short_easy_idx = [i for i in lab if rows[i]["total_len"] in SHORT_EASY_LENS]
    se_dots = [rows[i]["min_dot"] for i in short_easy_idx]
    baseline_median = float(np.median(se_dots)) if se_dots else 6.0
    train_r1 = {}                                      # canonical-r1 -> count of TRAIN rows (leakage)
    for i in fold_idx["train"]:
        r1 = keys[i].split("|")[0]
        train_r1[r1] = train_r1.get(r1, 0) + 1
    eval_instances = []
    for i in fold_idx["counterexample_eval"]:
        L = rows[i]["total_len"]
        smd = LH.get(L, {}).get("solved_median_dot")
        r1 = keys[i].split("|")[0]
        length_sep = (smd - baseline_median) if smd is not None else None  # spurious sep a length head buys
        eval_instances.append({
            "label": named_label_of.get(keys[i], "?"), "key": keys[i], "total_len": L,
            "group": rows[i]["group"], "in_dist_solved_median_dot": smd,
            "length_baseline_separation": round(length_sep, 2) if length_sep is not None else None,
            "r1_cousins_in_train": train_r1.get(r1, 0),
            "v1_stratum": ("length_matched_to_v1_baseline(len<=14)" if L <= 14
                           else "needs_per_length_baseline(len>=15)"),
            "dominant_confound_under_v1": ("r1_cousin_leakage" if L <= 13 and train_r1.get(r1, 0) > 1
                                           else "length_baseline_separation" if L >= 15
                                           else "length_matched(residual: structure)")})
    eval_instances.sort(key=lambda e: e["total_len"])
    v1_length_matched = [e for e in eval_instances if e["total_len"] <= 14]      # n=3 (AK(3)+L14x2)
    needs_per_length = [e for e in eval_instances if e["total_len"] >= 15]       # n=5 (AK(4..8))
    anchor_lens = sorted({e["total_len"] for e in eval_instances})
    per_length_solved = {str(L): sum(1 for i in lab if rows[i]["total_len"] == L) for L in anchor_lens}
    contrast = {
        "note": ("hardness claim is P(anchor@L) >> P(solved@SAME L); reported as gap/AUC/Spearman at "
                 "MODEL time. NO ground-truth d-o-t on anchors -> NO MAE; a constant-output model passes "
                 "it. v1's single len-13-14 baseline length-matches only n=3 anchors; the model plan must "
                 "use PER-LENGTH-matched baselines (per_length_solved below) to make all 8 usable and to "
                 "subtract the monotone solved_median_dot(L) length confound."),
        "baseline_median_dot_len13_14": baseline_median,
        "counterexample_eval": {"n": len(eval_instances), "len_range": [min(anchor_lens), max(anchor_lens)],
                                "max_length_baseline_separation": max(
                                    (e["length_baseline_separation"] for e in eval_instances
                                     if e["length_baseline_separation"] is not None), default=None)},
        "short_easy_len13_14": {"n": len(short_easy_idx), "median_dot": baseline_median},
        "per_length_solved_baseline": per_length_solved,
        "hard_test": {"n": len(fold_idx["hard_test"]),
                      "median_dot": float(np.median([rows[i]["min_dot"] for i in fold_idx["hard_test"]]))},
    }
    ak3_vs_lookalike = {
        "ak3_key": AK3_KEY, "ak3_fold": [f for f in folds if AK3_KEY in key_in[f]],
        "lookalike_key": LOOKALIKE_KEY, "lookalike_fold": [f for f in folds if LOOKALIKE_KEY in key_in[f]],
        "n": 1,
        "note": ("n=1 illustrative probe (differ only in r1). AK(3) is LENGTH-MATCHED to the baseline, so "
                 "length buys it ~0 separation -> its dominant confound is r1-cousin leakage: AK(3) can be "
                 "passed by matching r1='YXYxyx', seen labelled-hard in its train cousins (Havas-Ramsay "
                 "len<=13 => plausibly the same AC-problem); a pass shows r1-substring leverage, NOT clean "
                 "de-novo recognition. (Long anchors AK(6/7/8) flip: their dominant confound is length.)"),
    }

    # ---- Phase-3 drop (build-time-only stat): reuse build_v2_rows; cross-check band-mass ----
    drop = {"n_dropped": baseline["n_labelled"] - len(lab),
            "drop_n_paths_hist": None, "single_path_frac": None, "note": "rederive=False -> hist unavailable"}
    rederived_ok = None
    if rederive:
        _surv, st = bt.build_v2_rows()
        p3, p5 = st["p3"], st["p5"]
        h = p3["drop_n_paths_hist"]
        drop = {"n_dropped": p3["n_dropped"], "drop_n_paths_hist": h,
                "single_path_frac": round(h.get(1, 0) / max(sum(h.values()), 1), 3),
                "note": ("anti-diverse: drops skew to rare single-path classes; reweighting (info-"
                         "preserving) would suffice. Do NOT claim 'decorrelation worked' off this alone.")}
        # consistency: the re-derived Phase-5 band-mass must match the committed archive's
        rederived_ok = all(abs(p5["band_mass"][b] - band_mass_archive[b]) < 1e-6 for b in target)
        sh_named_share = p5["short_hard_named_mass_share"]
        nn = {"mean": p3["nn_mean"], "max": p3["nn_max"]}
    else:
        sh_named_share = sum(weights[i] for i, r in enumerate(rows)
                             if r["group"] in ("short_hard", "named")) / weights.sum()
        nn = None

    # ================= acceptance assertions (all must be green) =================
    A = {}
    A["AK3_in_counterexample_eval_only"] = ak3_vs_lookalike["ak3_fold"] == ["counterexample_eval"]
    A["AK3_tier_named"] = all(rows[i]["tier"] == "named" for i in fold_idx["counterexample_eval"]
                              if keys[i] == AK3_KEY)
    A["AK3_not_in_train"] = AK3_KEY not in key_in["train"]
    A["8_cousins_present_and_in_train"] = (set(trap["groups"]["short_hard"]) <= key_in["train"])
    A["lookalike_in_train"] = ak3_vs_lookalike["lookalike_fold"] == ["train"]
    A["lookalike_absent_from_trapset"] = LOOKALIKE_KEY not in set(trap["keys"])   # Finding-2 guard
    import itertools
    A["no_key_in_two_folds"] = not any(key_in[a] & key_in[b]
                                       for a, b in itertools.combinations(folds, 2))
    A["mean_weight_~1"] = abs(weights.mean() - 1.0) < 0.01
    A["archive_band_mass_within_tol"] = all(abs(band_mass_archive[b] - target[b]) <= BAND_MASS_TOL
                                            for b in target)
    # FA post §2.A (corrected): len<=14 (n=3) are length-matched to v1's single baseline; len>=15 (n=5)
    # need a per-length baseline (a length regression head buys spurious separation that GROWS with
    # length -- AK(8)@23 the most). solved_median_dot(L) must rise monotonically over the anchor lengths.
    A["eval_v1_length_matched_n3"] = len(v1_length_matched) == 3
    A["eval_needs_per_length_n5"] = len(needs_per_length) == 5
    smds = [e["in_dist_solved_median_dot"] for e in eval_instances]
    A["eval_length_separation_monotone"] = all(
        a <= b for a, b in zip(smds, smds[1:]) if a is not None and b is not None)
    A["eval_AK8_most_length_gameable"] = (
        eval_instances[-1]["label"] == "AK(8)"
        and eval_instances[-1]["length_baseline_separation"] == max(
            e["length_baseline_separation"] for e in eval_instances
            if e["length_baseline_separation"] is not None))
    if rederive:
        A["rederived_band_mass_matches_committed"] = rederived_ok
    # Phase-9 env->canon_key round-trip on AK(3): env-int8 literal -> strs -> canon_key
    lit = canon.strs_to_presentation_literal("xyxYXY", "xxxYYYY", max_length=cfg.L)
    r1s, r2s = canon.env_state_to_strs(lit, max_length=cfg.L)
    A["env_to_canonkey_roundtrip_AK3"] = canon.canon_key(r1s, r2s)[0] == AK3_KEY

    failed = [k for k, v in A.items() if not v]

    report = {
        "schema_version": 1,
        "inputs": {"archive_v2": archive_v2, "splits": splits_npz, "baseline": baseline_json,
                   "percentiles": percentiles_json, "trap_set": trap_set_json},
        "n_rows": n, "n_labelled": len(lab),
        "n_censored_generic": sum(1 for r in rows if r["censored"] and r["tier"] != "named"),
        "n_named": sum(1 for r in rows if r["tier"] == "named"),
        "bands": {
            "target_shares": target,
            "band_mass_archive": {k: round(v, 4) for k, v in band_mass_archive.items()},
            "band_mass_train_HEADLINE": {k: round(v, 4) for k, v in band_mass_train.items()},
            "tolerance": BAND_MASS_TOL,
            "note": ("HEADLINE = train cut (what actually trains); archive cut reproduces Phase-5. "
                     "hard_solved is doubly-depleted in train (hard_test frozen + x0.5 tail discount)."),
        },
        "mean_weight": round(float(weights.mean()), 5),
        "dot_histogram_labelled": dot_hist,
        "length_hardness_v2": length_hardness_v2,
        "hard_length_spread": {"baseline_censored": hard_len_baseline, "v2_censored_plus_named": hard_len_v2,
                               "note": "anchors add hard mass at len 19/21/23 absent from baseline (small)."},
        "source_mix_by_band": src_by_band,
        "fold_counts": fold_counts,
        "eval_reframed": {"per_instance": eval_instances,
                          "v1_length_matched_len<=14": v1_length_matched,
                          "needs_per_length_baseline_len>=15": needs_per_length,
                          "contrast_populations": contrast,
                          "ak3_vs_lookalike": ak3_vs_lookalike},
        "diversity_drop": drop,
        "near_neighbour_proxy": nn,
        "hinge_bounds": {"B_soft": perc["B_soft"], "B_hard": perc["B_hard"],
                         "short_hard_named_loss_mass_share": round(float(sh_named_share), 4),
                         "note": ("HEURISTIC floors, NOT lower bounds. B_hard=150 for AK(n) rests on solved "
                                  "p99, no group-theory backing, can err BOTH directions. flat B_soft=48 "
                                  "understates len-17 unsolved (B_soft(L) deferred). 16 short_hard+named rows "
                                  "~0.21% loss mass -> the x3 is near-inert (real fix = automorphic data).")},
        "caveats": [
            "counterexample_eval is all-hard, no ground-truth d-o-t -> NO MAE; report as separation/ranking.",
            "DOMINANT confound for AK(3): r1-cousin leakage -- AK(3) is length-matched to the baseline so "
            "length buys ~0 separation; it is passable by matching r1='YXYxyx', seen labelled-hard in its "
            "train cousins -> NOT clean de-novo recognition (per-anchor, not a global ordering).",
            "Length confound (mechanism): solved_median_dot(L) -- what a length regression head predicts -- "
            "RISES monotonically with length, so anchors longer than the len-13-14 baseline gain SPURIOUS "
            "separation that grows with length (AK(8)@23 the most, not the least). Fix = per-length-matched "
            "baselines P(AK(n)@L) >> P(solved@L); only then are AK(4)-AK(8) usable structural probes.",
            "HEADLINE band loss-mass is the TRAIN cut; archive cut is the Phase-5 reproduction.",
            "weight balances per-band WEIGHT mass, not loss/gradient mass (hinge vs regression scales differ).",
            "Phase-3 drop is anti-diverse (single-path-skewed); reweighting alone would suffice.",
            "hard_test membership is upper-bound-contaminated + heteroscedastic -> lead with Spearman, not MAE.",
            "bound_B is a heuristic floor, never a lower bound; B_hard=150 rests on solved p99 (no group-"
            "theory backing) and can err BOTH ways. ALL 8 named anchors -- the 6 AK(n) AND the 2 Length-14 "
            "(which fall OUTSIDE the Havas-Ramsay len<=13 dichotomy) -- are believed-hard / POTENTIAL "
            "counterexamples, never proven non-trivializable.",
            "band-boundary mis-binning of loose (50,100] labels (tail x0.5 only fires >100); model-side fix.",
            "d-o-t treated as a class invariant under rotation/inverse/swap, length-capped action (Phase-3.1 evidence).",
            "statistical-power limit: the conjecture-relevant eval is n=8, zero PROVEN-hard, one dominant "
            "family; hard_test (powered) measures regression on the SOLVABLE tail, not open-case recognition "
            "-- 'we built a structure-not-length dataset' must NOT read as 'we showed structure-not-length'.",
        ],
        "assertions": A,
    }

    if failed:
        if write:
            json.dump(_native(report), open(out, "w"), indent=2)   # persist the red report for debugging
        raise SystemExit(f"V2 REPORT acceptance FAILED: {failed}")
    if write:
        json.dump(_native(report), open(out, "w"), indent=2)
        print(f"wrote {out}")
    return _native(report)


def _print_headline(rep):
    b = rep["bands"]
    print("PHASE 8 v2 acceptance report")
    print(f"  rows={rep['n_rows']}  labelled={rep['n_labelled']}  censored={rep['n_censored_generic']}  "
          f"named={rep['n_named']}  mean(weight)={rep['mean_weight']}")
    print(f"  band loss-mass ARCHIVE (Phase-5 repro): "
          + "  ".join(f"{k}={v}" for k, v in b["band_mass_archive"].items()))
    print(f"  band loss-mass TRAIN (headline):        "
          + "  ".join(f"{k}={v}" for k, v in b["band_mass_train_HEADLINE"].items()))
    d = rep["diversity_drop"]
    print(f"  Phase-3 drop: n_dropped={d['n_dropped']}  single-path-frac={d['single_path_frac']}  "
          f"hist={d['drop_n_paths_hist']}")
    print(f"  short_hard+named loss-mass share = {rep['hinge_bounds']['short_hard_named_loss_mass_share']*100:.2f}%  (near-inert)")
    e = rep["eval_reframed"]
    print(f"  eval: {len(e['v1_length_matched_len<=14'])} length-matched(len<=14) + "
          f"{len(e['needs_per_length_baseline_len>=15'])} needs-per-length-baseline(len>=15)")
    print(f"  assertions: {sum(rep['assertions'].values())}/{len(rep['assertions'])} green")


if __name__ == "__main__":
    rep = build_report()
    _print_headline(rep)
