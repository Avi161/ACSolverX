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


def test_c19_minus_endpoint_becomes_bs():
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(CODE))
    import c16_escape_scan as esc  # type: ignore

    for n in (2, 3, 7):
        rec = esc.c19_identity(n)
        assert rec["equals_claimed"]
        assert rec["cyclically_bs_n_n1"]
        assert rec["drop"] == 3
        assert rec["bs_m"] == n
        assert rec["donor_u_exp"] == 1
        assert rec["donor_split_pinches"]
        assert all(p["k"] == -1 for p in rec["donor_split_pinches"])
        assert not rec["donor_valid_bs_pinch"]
    fact = esc.factorization_identities()
    assert fact["equals_inner_xinv2"] and fact["equals_xinv2_conjugate"]


def test_c20_pinch_is_round_trip():
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(CODE))
    import c20_roundtrip as c20  # type: ignore

    for n in (2, 3, 7):
        rec = c20.round_trip_row(n)
        assert rec["round_trip"], rec
        assert rec["D*B"]["equals_D"]
        assert rec["B*D"]["equals_D"]
        assert rec["D*Binv"]["cyclic_of_D"]
        assert rec["B*Dinv"]["cyclic_of_Dinv"]
    depth = c20.depth1_pinch_roundtrips(2)
    counts = depth["counts"]
    assert counts["all_rewrites_allowed"]
    assert counts["other"] == 0
    assert counts["empty_on_D_slot"] == 0
    assert counts["n_no_pinch"] == 10
    assert counts["no_pinch_all_keep_D"]
    assert counts["no_pinch_min_len"] > 14
    assert len(depth["no_pinch_children"]) == 10
    assert all(row["keeps_D"] for row in depth["no_pinch_children"])
    donor = c20.serialize_whitehead(c20.D)
    assert not donor["primitive"]
    assert not donor["first_kind_primitive"]
    assert donor["minimum_total"] == 7


def test_c21_no_pinch_family_and_gate2():
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(CODE))
    import c21_depth2 as c21  # type: ignore

    destab = c21.gate2_destab_probe()
    assert not destab["any_bare_ac5"]
    for n in (2, 3, 7):
        kids = c21.no_pinch_children(n)
        offsets = sorted(row["r2_len"] - 2 * n for row in kids)
        assert offsets == [6, 6, 6, 6, 8, 8, 8, 8, 8, 8], (n, offsets)
    scan = c21.scan_n(2)
    assert not scan["any_drop_vs_c19"]
    assert not scan["any_one_occ"]
    assert not scan["any_two_block"]
    assert not scan["any_other_shorter_than_D"]
    assert scan["n_return_to_c19_length"] == 1
    assert scan["n_return_to_DB_edges"] == 10
    assert scan["n_parent_drop_edges"] == 12
    assert scan["min_other_after_len"] >= 7


def test_c22_gate1_abelian_and_c15_bridge():
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(CODE))
    import c22_gate_witness as c22  # type: ignore

    bridge = c22.c15_bridge_identities()
    assert bridge["donor_times_Xyx_equals_P1"]
    assert bridge["P1_times_xyX_equals_donor"]
    for delta in (-1, 1):
        rec = c22.gate1_abelian(2, delta)
        assert rec["combo"]["ok"]
        assert rec["combo"]["a"] == delta
        assert rec["combo"]["b"] == 0
        assert rec["D_len"] == 4
        assert rec["D_len"] not in (rec["depth1_restore_len_R"], rec["depth1_restore_len_S"])
        c6 = c22.c16_as_c6(2, delta)
        assert c6["hypotheses_ok"]
        assert not c6["canon_match_S"]
    artifact = json.loads(
        (ROOT / "research/u124_stable_20260912/tables/c22_gate_witness.json").read_text()
    )
    summary = artifact["summary"]
    assert summary["gate1_S_coeff_always_0"]
    assert summary["gate1_R_coeff_equals_delta"]
    assert summary["gate1_depth1_restore_impossible"]
    assert not summary["c16_as_c6_same_as_c16"]
    assert not summary["c15_depth1_reaches_P"]
    assert not summary["gate1_search_any_hit"]
    assert len(artifact["gate1_search"]) == 4
    assert {(row["n"], row["delta"]) for row in artifact["gate1_search"]} == {
        (2, -1),
        (2, 1),
        (3, -1),
        (3, 1),
    }
    assert summary["solved_u124"] == 0


def test_c23_three_factor_shapes_and_n2():
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(CODE))
    import c23_three_factor as c23  # type: ignore

    shapes = c23.abelian_three_factor_shapes()
    assert shapes["all_only_A_or_B"]
    for delta in (-1, 1):
        rec = c23.scan_three_factor(2, delta)
        assert not rec["found"]
        assert rec["min_len"] == 7
        assert rec["W_len"] == 10
        assert rec["xi_len"] == 3
    artifact = json.loads(
        (ROOT / "research/u124_stable_20260912/tables/c23_three_factor.json").read_text()
    )
    summary = artifact["summary"]
    assert summary["abelian_only_shapes_A_and_B"]
    assert not summary["three_factor_any_hit"]
    assert summary["three_factor_all_min_len_ge_7"]
    assert summary["three_factor_n_checked"] == 12
    assert summary["three_factor_n_products"] == 1_529_400
    assert not summary["f3_any_hit"]
    assert summary["f3_n_checked"] == 12
    assert summary["f3_all_min_len_non_gen_ge_8"]
    assert summary["D_len"] == 4
    assert summary["solved_u124"] == 0


def test_c24_even_k_and_n2_five_factor():
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(CODE))
    import c24_even_k as c24  # type: ignore

    family = c24.infinite_family_check(20)
    assert family["gate1_hypotheses_hold"]
    assert family["gate2_L1_always_even"]
    ktable = c24.abelian_k_table(6)
    assert ktable["even_k_all_zero"]
    assert ktable["uniform_gate1_counts"]
    assert ktable["closed_matches_enumeration"]
    assert ktable["k5_always_100"]
    assert c24.signed_type_count_closed(1) == 1
    assert c24.signed_type_count_closed(3) == 9
    assert c24.signed_type_count_closed(5) == 100
    assert c24.signed_type_count_closed(2) == 0
    rot = c24.xi_rotation_free_targets()
    assert rot["equals_xi_xiinv_x_xinv"]
    assert set(rot["extra_beyond_xi"]) == {"x", "X"}
    controls = c24.mitm_controls()
    assert controls["ok"]
    assert controls["same_code_as_census"]
    assert not controls["independent_checker"]
    g2 = c24.gate2_parity_row(2, 1)
    assert g2["combo_matches_closed_form"]
    assert g2["L1"] == 6
    assert g2["odd_k_forbidden"]
    assert not g2["k4_abelian_legal"]
    g2m = c24.gate2_parity_row(2, -1)
    assert g2m["L1"] == 2
    assert g2m["k4_abelian_legal"]
    for delta in (-1, 1):
        rec = c24.gate1_five_factor(2, delta)
        assert not rec["found"]
        assert not rec["rotation_found"]
        assert rec["xi_len"] == 3
        assert rec["n_factors"] == 80
        assert rec["n_k_tuples"] == 80 ** 5
    four = c24.gate2_four_factor(2, -1)
    assert not four["found"]
    stored_search = c24.stored_small_k_search()
    searched = {row["id"]: row for row in stored_search if row["searched"]}
    assert set(searched) == {"aca_16", "aca_43", "aca_90"}
    assert searched["aca_16"]["k"] == 5
    assert searched["aca_43"]["k"] == 4
    assert searched["aca_43"]["reason"] and "C22.4" in searched["aca_43"]["reason"]
    assert searched["aca_90"]["k"] == 3
    assert all(not row["found"] for row in stored_search)
    artifact = json.loads(
        (ROOT / "research/u124_stable_20260912/tables/c24_even_k.json").read_text()
    )
    summary = artifact["summary"]
    assert summary["gate1_hypotheses_n_le_20"]
    assert summary["gate2_L1_always_even_n_le_20"]
    assert summary["even_k_all_zero"]
    assert summary["closed_matches_enumeration"]
    assert summary["mitm_control_ok"]
    assert summary["same_code_replay"]
    assert not summary["independent_checker"]
    assert summary["xi_rotation_equals_xi_xiinv_x_xinv"]
    assert not summary["five_factor_any_hit"]
    assert not summary["five_factor_rotation_any_hit"]
    assert summary["five_factor_n_checked"] == 12
    assert summary["gate2_odd_k_all_forbidden"]
    assert summary["gate2_four_n_checked"] == 4
    assert not summary["gate2_four_any_hit"]
    assert summary["stored_small_k_n_searched"] == 3
    assert not summary["stored_small_k_any_hit"]
    assert summary["solved_u124"] == 0
