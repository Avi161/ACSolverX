"""Regression tests for the U124 campaign census and MS identities."""

from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
CODE = ROOT / "research" / "u124_stable_20260912" / "code"


def test_ms_template_identities_n3_both_signs():
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(CODE))
    import ms_template_identities as m  # type: ignore

    for delta in (-1, 1):
        p = m.parametric_p(3, delta)
        h1 = m.apply_cov(p, "xy", iso_gen="x")
        assert len(h1) == 1 and h1[0]["n_subs"] == 2
        h2 = m.apply_cov(h1[0]["pair"], "xxx", iso_gen="x")
        q = m.claimed_q(3, delta)
        assert any(row["pair"] == q and row["n_subs"] == 4 for row in h2)


def test_census_hashes_and_counts():
    cmd = [sys.executable, str(CODE / "u124_census.py")]
    subprocess.check_call(cmd, cwd=ROOT)
    summary = json.loads(
        (ROOT / "research/u124_stable_20260912/tables/census_summary.json").read_text()
    )
    assert summary["n_rows"] == 124
    assert summary["initial_total_length"] == 2446
    assert summary["best_total_length"] == 2356
    assert summary["n_mu_floor_best"] == 36
    assert summary["solved"] == 0
    assert summary["feature_counts_on_best"]["unimodular_best"] == 124
    assert summary["feature_counts_on_best"]["ms_floor_shape_best"] == 10
    assert (
        summary["hashes"]["aca_124_initial.csv"]["sha256"]
        == summary["hashes"]["aca_124.csv"]["sha256"]
    )


def test_q_peel_identities_and_commutator_factor():
    sys.path.insert(0, str(CODE))
    import q_peel as peel  # type: ignore

    q_rows = peel.check_q_identities()
    assert len(q_rows) == 14
    assert all(row["peel_matches_claimed"] for row in q_rows)
    assert all(row["peel_is_u_xpow_v_commutator"] for row in q_rows)
    assert peel.free_reduce(peel.inv(peel.G)) == peel.free_reduce(peel.V + peel.COMM)
    # Unconjugated second peel is not a descent on n and does not restore R2.
    assert all(not row["second_peel_equals_original_r2"] for row in q_rows)
    a_rows = peel.check_family_a_prefix()
    assert len(a_rows) == 6
    assert all(row["matches_conjugate"] for row in a_rows)


def test_primitive_controls_and_ms_donors_not_primitive():
    sys.path.insert(0, str(ROOT))
    from experiments.stable_ac.rank3_compression.rank3_whitehead import (
        check_word_reduction,
        is_primitive_word,
        reduce_word,
    )

    def red(word: str):
        result = reduce_word(word, generators=("x", "y"))
        check_word_reduction(word, result)
        return result

    assert is_primitive_word(red("x"))
    assert is_primitive_word(red("xyX"))
    assert not is_primitive_word(red("xyXY"))
    assert not is_primitive_word(red("xxxYYYY"))
    assert not is_primitive_word(red("YXXyxYx"))
    assert not is_primitive_word(red("YXyXYxx"))
    assert red("YXyXYxx").minimum_total == 5
    assert red("YXXyxYx").minimum_total == 6


def test_c12_generator_deletion_signs_and_unimodular_finish():
    sys.path.insert(0, str(CODE))
    import c12_generator_deletion as d  # type: ignore

    yx = d.delete_all_x("yx")
    assert yx["leftover"] == "y" and yx["terminal_is_y_pm1"]
    xy = d.delete_all_x("xy")
    assert xy["leftover"] == "y"
    inv_first = d.delete_all_x("Yx")
    assert inv_first["leftover"] == "Y"
    mixed = d.delete_all_x("xyXYy")
    assert mixed["leftover"] in ("y", "Y") and abs(mixed["det_if_paired_with_x"]) == 1
    commutator = d.delete_all_x("xyXY")
    assert commutator["leftover"] == ""
    assert commutator["det_if_paired_with_x"] == 0


def test_c15_leading_y_conjugate_keeps_interior_runs():
    sys.path.insert(0, str(CODE))
    import c15_divisibility_scan as c15  # type: ignore

    word = c15.conjugate_by_ypower(c15.DONOR, 2)
    assert word == "YYYXXXyxYxyy"
    assert c15.y_run_lengths(word) == [3, 1, 1, 2]
    assert not c15.all_divisible(word, 3)


def test_c16_c17_c18_identities_fast():
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(CODE))
    import theory_wave1_replay as tw  # type: ignore

    q = tw.check_q_to_q_prime()
    assert q["all_freely_equal"]
    c16 = tw.check_c16_u124_instance()
    assert c16["all_H2_H3"] and c16["all_faithful"] and c16["all_c_free"]
    assert c16["all_plus_loops"]
    assert c16["all_minus_rotation_absent"]
    assert c16["minus_row1_x_exponent"] == [-2]
    c17 = tw.check_c17()
    assert c17["orbit_u124_flank_never_drops"]
    assert c17["S_plus_is_BS32_and_E"]
    assert c17["S_minus_not_BS"]
    assert c17["S_plus_H3_fails"]
    c18 = tw.check_c18()
    assert c18["euclid_ok"]
    assert c18["h1_raw_rotations_matching_inventor"] == {"tested": 1764, "hits": 0}
    rec = tw.check_u124_c16_recognizer()
    best = rec["tables"]["aca_124_best.csv"]
    assert best["pairs_firing_C16"] == 5
    assert best["all_hits_instance_ok"]
    assert {h["name"] for h in best["hits"]} == {"aca_16", "aca_43", "aca_67", "aca_87", "aca_90"}
    assert all(not h["verified"]["C16_1_rho_legal"] for h in best["hits"])
