"""Gate-style tests for Phase 0 (no pytest; matches the scripts/validate_canon.py idiom).

Run from the repo root:
    python scripts/test_phase0.py

Prints each check; exits non-zero with 'PHASE0 TESTS FAILED' on any failure, else prints
'PHASE0 TESTS PASS'. Pure-function checks touch no files; the end-to-end check runs main()
into a project-relative scratch dir (never /tmp) and removes it afterward.

The hard-pinned counts (37,496 / 4,954) and percentiles (48 / 150 ...) intentionally
regression-pin the *current* data/dot_archive.jsonl -- if the archive is rebuilt these are
expected to be revisited together with 4-§4.
"""
import os
import sys
import json
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dot_config as cfg     # noqa: E402
import dot_dataset           # noqa: E402
import phase0_baseline as p0  # noqa: E402


def run_tests():
    failures = []

    def check(name, cond, detail=""):
        if cond:
            print(f"  ok   {name}")
        else:
            print(f"  FAIL {name}  {detail}")
            failures.append(name)

    # ---- group 1: config (pure, no data) ----
    print("[config]")
    check("target shares sum to 1", abs(sum(cfg.TARGET_SHARES.values()) - 1.0) < 1e-9,
          f"sum={sum(cfg.TARGET_SHARES.values())}")
    lo, hi = cfg.WEIGHT_CLIP
    check("weight clip ordered & positive", 0 < lo < hi, f"{cfg.WEIGHT_CLIP}")
    check("AK range valid", cfg.AK_MIN < cfg.AK_MAX and cfg.AK_MIN >= 1,
          f"{cfg.AK_MIN}..{cfg.AK_MAX}")
    check("AK headroom 2*AK_MAX+1 <= L", 2 * cfg.AK_MAX + 1 <= cfg.L,
          f"2*{cfg.AK_MAX}+1={2 * cfg.AK_MAX + 1} L={cfg.L}")
    check("tail mult in (0,1)", 0 < cfg.TAIL_MULT < 1, f"{cfg.TAIL_MULT}")
    check("short-hard mult >= 1", cfg.SHORT_HARD_MULT >= 1, f"{cfg.SHORT_HARD_MULT}")
    check("diversity stride >= 1", cfg.DIVERSITY_STRIDE >= 1, f"{cfg.DIVERSITY_STRIDE}")
    check("per-path cap >= 1", cfg.PER_PATH_CAP >= 1, f"{cfg.PER_PATH_CAP}")
    check("B_soft < B_hard expected", cfg.B_SOFT_EXPECTED < cfg.B_HARD_EXPECTED)

    for d, want in [(0, "easy"), (10, "easy"), (11, "valley"), (50, "valley"),
                    (51, "hard_solved"), (349, "hard_solved")]:
        check(f"band_of({d})=={want}", cfg.band_of(d) == want, f"got {cfg.band_of(d)}")
    e = cfg.BAND_EDGES
    check("bands contiguous & open-ended",
          e["easy"][1] + 1 == e["valley"][0]
          and e["valley"][1] + 1 == e["hard_solved"][0]
          and e["hard_solved"][1] is None)

    # ---- group 2: data (real archive, pure functions, no writes) ----
    print("[data]")
    problems = p0.check_inputs()
    check("check_inputs() clean", problems == [], f"{problems}")

    labelled, censored = dot_dataset.load_archive(cfg.ARCHIVE)
    check("n_labelled == 37496", len(labelled) == 37496, f"got {len(labelled)}")
    check("n_censored == 4954", len(censored) == 4954, f"got {len(censored)}")
    check("n_total == 42450", len(labelled) + len(censored) == 42450)

    pcts = p0.compute_percentiles([r["min_dot"] for r in labelled])
    check("p50 == 11", pcts["p50"] == 11, f"{pcts['p50']}")
    check("p75 == 20", pcts["p75"] == 20, f"{pcts['p75']}")
    check("round(p90) == 48", round(pcts["p90"]) == 48, f"{pcts['p90']}")
    check("p95 == 81", pcts["p95"] == 81, f"{pcts['p95']}")
    check("round(p99) == 150", round(pcts["p99"]) == 150, f"{pcts['p99']}")
    check("max == 349", pcts["max"] == 349, f"{pcts['max']}")

    b_soft, b_hard = p0.derive_bounds(pcts)
    check("derive_bounds == (48,150)", (b_soft, b_hard) == (48, 150), f"{(b_soft, b_hard)}")
    check("bounds within tol of expected",
          abs(b_soft - cfg.B_SOFT_EXPECTED) <= cfg.B_TOL
          and abs(b_hard - cfg.B_HARD_EXPECTED) <= cfg.B_TOL)

    base = p0.baseline_distribution(labelled, censored)
    bc = base["band_counts"]
    check("bands reconcile to labelled",
          bc["easy"] + bc["valley"] + bc["hard_solved"] == len(labelled), f"{bc}")
    check("hard_unsolved == n_censored", bc["hard_unsolved"] == len(censored))
    fr = {row["total_len"]: row["censored_frac"] for row in base["length_hardness"]}
    check("censored_frac@17 > @13", fr.get(17, 0) > fr.get(13, 0),
          f"13={fr.get(13)} 17={fr.get(17)}")
    check("censored_frac@13 < 0.01", fr.get(13, 1) < 0.01, f"{fr.get(13)}")
    check("n_censored_le13 == 8", base["n_censored_le13"] == 8, f"{base['n_censored_le13']}")
    check("baseline deterministic", base == p0.baseline_distribution(labelled, censored))

    # ---- group 3: main() end-to-end via scratch dir (exercises the writer seam) ----
    print("[main e2e]")
    scratch = os.path.join(".scratch", "phase0_test")
    try:
        os.makedirs(scratch, exist_ok=True)
        pj = os.path.join(scratch, "percentiles.json")
        bj = os.path.join(scratch, "baseline_distribution.json")
        p0.main(archive=cfg.ARCHIVE, percentiles_json=pj, baseline_json=bj)
        with open(pj) as f:
            pobj = json.load(f)
        with open(bj) as f:
            bobj = json.load(f)
        check("percentiles.json B_soft == 48", pobj["B_soft"] == 48, f"{pobj.get('B_soft')}")
        check("percentiles.json B_hard == 150", pobj["B_hard"] == 150, f"{pobj.get('B_hard')}")
        check("baseline.json reconciles",
              bobj["band_counts"]["easy"] + bobj["band_counts"]["valley"]
              + bobj["band_counts"]["hard_solved"] == bobj["n_labelled"])
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    print()
    if failures:
        print(f"  {len(failures)} check(s) failed: {failures}")
        raise SystemExit("PHASE0 TESTS FAILED")
    print("PHASE0 TESTS PASS")


if __name__ == "__main__":
    run_tests()
