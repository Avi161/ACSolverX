"""Gate-style tests for Phase 8 (acceptance report) + Phase 9 (handoff) of the data-crafting
pipeline. No pytest; matches the test_build_training_archive.py / test_phase1.py idiom.

Run from the repo root:
    ../.venv/bin/python tests/data_crafting/test_acceptance_v2.py

Prints each check; exits non-zero with 'ACCEPTANCE-V2 TESTS FAILED' on any failure, else prints
'ACCEPTANCE-V2 TESTS PASS'. Calls build_v2_report.build_report() (the pure function the notebook
wraps) and re-derives the headline numbers independently from the committed v2 archive + splits;
asserts the Field-Advisor eval-reframing (length-stratified n=3 short-hard probe, no MAE), the
whole-archive Phase-5 invariants, and the Phase-9 trap-set seam (env->canon_key round-trip on
AK(3), look-alike absent from the trap-set, 16 keys <-> v2 tiers).
"""
import os
import sys
import json

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # repo root
from scripts.lib import canon              # noqa: E402
from scripts.lib import dot_config as cfg  # noqa: E402
from scripts.lib import dot_dataset as dd  # noqa: E402
from scripts.build import build_v2_report as rpt  # noqa: E402

AK3_KEY = "YXYxyx|YYYYxxx"
LOOKALIKE_KEY = "YXyxYx|YYYYxxx"
TARGET_BAND_MASS = {"easy": 0.256, "valley": 0.358, "hard_solved": 0.128, "hard_unsolved": 0.257}

failures = []


def check(name, cond, extra=""):
    ok = bool(cond)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"   -- {extra}" if extra else ""))
    if not ok:
        failures.append(name)


def run_tests():
    print("== Phase 8/9: build_v2_report + trap-set handoff ==")

    # build_report runs all its own §8 assertions; if any are red it raises SystemExit, so a
    # clean return already means all internal gates were green. We then re-derive independently.
    rep = rpt.build_report(write=False)

    # ---------- Phase 8: every internal assertion is green ----------
    A = rep["assertions"]
    check("build_report ran ALL §8 assertions and all are green",
          all(A.values()), str([k for k, v in A.items() if not v]))
    # spot-check the load-bearing ones are actually present (not silently dropped)
    for must in ("AK3_in_counterexample_eval_only", "lookalike_in_train",
                 "lookalike_absent_from_trapset", "no_key_in_two_folds",
                 "archive_band_mass_within_tol", "env_to_canonkey_roundtrip_AK3",
                 "eval_v1_length_matched_n3", "eval_needs_per_length_n5",
                 "eval_length_separation_monotone", "eval_AK8_most_length_gameable",
                 "rederived_band_mass_matches_committed"):
        check(f"assertion present: {must}", must in A)

    # ---------- whole-archive Phase-5 invariants (NOT the train cut) ----------
    bm = rep["bands"]["band_mass_archive"]
    check("archive band loss-mass ~ documented .256/.358/.128/.257 (Phase-5 repro)",
          all(abs(bm[b] - TARGET_BAND_MASS[b]) <= 0.005 for b in TARGET_BAND_MASS), str(bm))
    check("mean(weight) ~ 1.0 (full-archive invariant)", abs(rep["mean_weight"] - 1.0) < 0.01,
          str(rep["mean_weight"]))
    # the TRAIN headline must be the depleted cut (hard_solved BELOW the archive value)
    tr = rep["bands"]["band_mass_train_HEADLINE"]
    check("train-fold hard_solved is doubly-depleted below the archive value (FA headline)",
          tr["hard_solved"] < bm["hard_solved"], f"train={tr['hard_solved']} archive={bm['hard_solved']}")

    # ---------- independent re-derivation of the archive band-mass ----------
    rows = dd._load_rows_in_order(cfg.ARCHIVE_V2)
    w = np.array([r["weight"] for r in rows], dtype=np.float64)

    def region(r):
        return "hard_unsolved" if r["censored"] else cfg.band_of(r["min_dot"])
    mass = {b: 0.0 for b in TARGET_BAND_MASS}
    for i, r in enumerate(rows):
        mass[region(r)] += w[i]
    mass = {b: round(mass[b] / w.sum(), 4) for b in mass}   # report rounds to 4dp
    check("independent band-mass recompute matches the report",
          all(abs(mass[b] - bm[b]) < 1e-9 for b in mass), str(mass))

    # ---------- eval reframing (FA post §2.A/§2.B, corrected) ----------
    e = rep["eval_reframed"]
    lm = e["v1_length_matched_len<=14"]
    npl = e["needs_per_length_baseline_len>=15"]
    check("eval per-instance has 8 named anchors", len(e["per_instance"]) == 8)
    check("exactly 3 length-matched-to-v1-baseline anchors (len<=14): AK(3)+Length-14 x2",
          len(lm) == 3, str([x["label"] for x in lm]))
    check("exactly 5 needs-per-length-baseline anchors (len>=15): AK(4)..AK(8)",
          len(npl) == 5, str([x["label"] for x in npl]))
    # corrected mechanism: solved_median_dot(L) rises -> length separation GROWS with length
    smds = [x["in_dist_solved_median_dot"] for x in e["per_instance"]]
    check("solved_median_dot(L) rises monotonically over anchor lengths (length confound mechanism)",
          all(a <= b for a, b in zip(smds, smds[1:])), str(smds))
    ak8 = e["per_instance"][-1]
    check("AK(8)@23 is the MOST length-gameable (largest spurious separation), NOT the least",
          ak8["label"] == "AK(8)" and ak8["length_baseline_separation"] == max(
              x["length_baseline_separation"] for x in e["per_instance"]))
    ak3 = next(x for x in e["per_instance"] if x["label"] == "AK(3)")
    check("AK(3) is length-matched (separation ~0) -> dominant confound = r1_cousin_leakage",
          ak3["length_baseline_separation"] == 0.0
          and ak3["dominant_confound_under_v1"] == "r1_cousin_leakage")
    av = e["ak3_vs_lookalike"]
    check("ak3-vs-lookalike probe is labelled n=1 and flags r1-cousin leakage as AK(3)'s confound",
          av["n"] == 1 and "r1" in av["note"].lower())
    check("contrast populations present (eval / short_easy / per-length baseline / hard_test)",
          all(k in e["contrast_populations"] for k in
              ("counterexample_eval", "short_easy_len13_14", "per_length_solved_baseline", "hard_test")))
    check("report states counterexample_eval has NO MAE",
          "no mae" in e["contrast_populations"]["note"].lower().replace("-", " "))
    check("per-length-matched baseline data present for all anchor lengths (the constructive fix)",
          len(e["contrast_populations"]["per_length_solved_baseline"]) >= 7)

    # ---------- provenance honesty: 'anchor' in the source mix == the 8 named ONLY ----------
    smix = rep["source_mix_by_band"]
    anchor_in_mix = sum(b.get("anchor", 0) for b in smix.values())
    check("source-mix 'anchor' count == n_named == 8 (NOT all 4,954 censored)",
          anchor_in_mix == rep["n_named"] == 8, f"anchor_in_mix={anchor_in_mix}")
    check("generic censored shown as 'censored (no source recorded)', not 'anchor'",
          smix["hard_unsolved"].get("censored (no source recorded)", 0) == 4954,
          str(smix["hard_unsolved"]))

    # ---------- diversity drop honesty (anti-diverse, single-path-skewed) ----------
    d = rep["diversity_drop"]
    check("Phase-3 drop reported: n_dropped == 4074", d["n_dropped"] == 4074, str(d["n_dropped"]))
    check("drop is single-path-skewed (single_path_frac > 0.5, honest decorrelation caveat)",
          d["single_path_frac"] > 0.5, str(d["single_path_frac"]))
    check("short_hard+named loss-mass share reported as near-inert (< 1%)",
          rep["hinge_bounds"]["short_hard_named_loss_mass_share"] < 0.01,
          str(rep["hinge_bounds"]["short_hard_named_loss_mass_share"]))

    # ---------- caveats present (the honesty guards) ----------
    cav = " ".join(rep["caveats"]).lower()
    check(">= 11 caveats carried forward", len(rep["caveats"]) >= 11, str(len(rep["caveats"])))
    for token in ("no mae", "r1-cousin leakage", "per-length-matched", "heuristic floor",
                  "heteroscedastic", "potential", "length-14"):
        check(f"caveat mentions '{token}'", token in cav, token)

    # ---------- v2_report.json schema: writes + round-trips, all values finite/native ----------
    print("[v2_report.json write + schema]")
    os.makedirs(".scratch", exist_ok=True)
    out = os.path.join(".scratch", "v2_report.json")
    try:
        rep2 = rpt.build_report(out=out, write=True)
        loaded = json.load(open(out))   # must be valid JSON (native types only)
        for key in ("bands", "dot_histogram_labelled", "length_hardness_v2", "fold_counts",
                    "eval_reframed", "diversity_drop", "hinge_bounds", "caveats", "assertions",
                    "source_mix_by_band", "hard_length_spread"):
            check(f"v2_report.json has top-level key '{key}'", key in loaded)
        check("all assertions in the written json are True", all(loaded["assertions"].values()))
        # fold counts reconcile to 38,384
        fc = loaded["fold_counts"]
        check("fold_counts sum to 38,384",
              sum(fc[f]["n"] for f in fc) == 38384, str({f: fc[f]["n"] for f in fc}))
        # committed v2_report.json (if present) matches a fresh build
        if os.path.exists(rpt.REPORT_JSON):
            committed = json.load(open(rpt.REPORT_JSON))
            check("committed v2_report.json band_mass matches a fresh build",
                  committed["bands"]["band_mass_archive"] == loaded["bands"]["band_mass_archive"])
    finally:
        import shutil
        shutil.rmtree(".scratch", ignore_errors=True)

    # =================== Phase 9: trap-set handoff is consumable ===================
    print("[Phase 9: ak_trap_set.json handoff]")
    trap = json.load(open(cfg.TRAP_SET_JSON))
    named = trap["groups"]["named"]      # {label: key}
    short = trap["groups"]["short_hard"]  # [key]
    all_keys = set(trap["keys"])
    check("16 distinct trap keys", trap["n_keys"] == 16 and len(all_keys) == 16)
    check("groups.named is a {label:key} dict of 8", isinstance(named, dict) and len(named) == 8)
    check("groups.short_hard is a list of 8", isinstance(short, list) and len(short) == 8)
    check("trap keys == named values ∪ short_hard", all_keys == set(named.values()) | set(short))

    # the 16 keys map to the right v2-archive tiers (closed-world membership is well-typed)
    by_key = {f"{r['r1']}|{r['r2']}": r for r in rows}
    named_ok = all(by_key.get(k, {}).get("tier") == "named" for k in named.values())
    short_ok = all(by_key.get(k, {}).get("censored") and by_key.get(k, {}).get("group") == "short_hard"
                   for k in short)
    check("8 named keys -> tier=='named' in v2 archive", named_ok)
    check("8 short_hard keys -> censored & group=='short_hard' in v2 archive", short_ok)

    # (a) env-int8 -> canon_key round-trip on AK(3) -- the search monitor's only real failure point
    lit = canon.strs_to_presentation_literal("xyxYXY", "xxxYYYY", max_length=cfg.L)
    r1s, r2s = canon.env_state_to_strs(lit, max_length=cfg.L)
    rt_key = canon.canon_key(r1s, r2s)[0]
    check("env-int8(AK(3)) -> canon_key round-trips to YXYxyx|YYYYxxx (Booth!=canon seam closed)",
          rt_key == AK3_KEY, f"got {rt_key}")
    # also from the canonical form's own literal (idempotence of the bridge)
    lit2 = canon.strs_to_presentation_literal("YXYxyx", "YYYYxxx", max_length=cfg.L)
    check("env-int8(canonical AK(3)) -> canon_key is idempotent == YXYxyx|YYYYxxx",
          canon.canon_key(*canon.env_state_to_strs(lit2, max_length=cfg.L))[0] == AK3_KEY)

    # (b) look-alike absent from the trap-set (else the EASY look-alike is flagged as a hard basin)
    check("look-alike YXyxYx|YYYYxxx is ABSENT from the trap-set (Finding-2 guard)",
          LOOKALIKE_KEY not in all_keys)
    check("AK(3) != look-alike (differ only in r1) yet both are valid distinct canon keys",
          AK3_KEY != LOOKALIKE_KEY and AK3_KEY in all_keys)

    print()
    if failures:
        print(f"  {len(failures)} check(s) failed: {failures}")
        raise SystemExit("ACCEPTANCE-V2 TESTS FAILED")
    print("ACCEPTANCE-V2 TESTS PASS")


if __name__ == "__main__":
    run_tests()
