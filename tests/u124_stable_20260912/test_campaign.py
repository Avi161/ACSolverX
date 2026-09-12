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


def test_c25_alt_words_identities_and_n2():
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(CODE))
    import c25_alt_words as c25  # type: ignore

    yclass = c25.y_class_free_targets()
    assert yclass["class_covers_one_letter"]
    assert yclass["positive_exp_01"] == ["Xyx", "xyX", "y"]
    x = c25.q_prime_x_l1(2, -1)
    assert x["same_abelian_class_as_xi"]
    assert x["L1"] == 1
    assert c25.y_l1_closed(2, -1) == 1
    assert c25.y_l1_closed(2, 1) == 5
    assert c25.y_l1_closed(3, -1) == 2
    y_exc = c25.q_prime_y_l1(2, -1)
    assert y_exc["k1_abelian_legal"]
    assert y_exc["S_cyc_len"] == 7
    assert y_exc["k1_len_obstruction"]
    y_else = c25.q_prime_y_l1(3, -1)
    assert y_else["L1"] == 2
    assert not y_else["k1_abelian_legal"]
    y = c25.q_prime_y_l1(4, -1)
    assert y["matches_closed"]
    assert y["L1"] == 3
    assert not y["k1_abelian_legal"]
    rec_x = c25.q_prime_x_three_factor(2, -1)
    assert not rec_x["found"]
    assert rec_x["min_len"] >= 7
    assert rec_x["pool"] == "nine_signed_type_configs_per_type_dedup"
    assert rec_x["n_configs"] == 9
    prow = c25.c15_p_row2_status()
    assert prow["five_match_P_plus_row2"]
    assert prow["n_equals_P_plus_row2"] == 5
    assert [row["id"] for row in prow["rows"] if row["equals_P_plus_row2"]] == [
        "aca_20",
        "aca_42",
        "aca_65",
        "aca_91",
        "aca_104",
    ]
    invc = c25.inversion_closure()
    assert invc["nine_configs_closed"]
    assert invc["negative_targets_hit_iff_positive_inverse_factors"]
    c15_ab = c25.c15_row_abelian("aca_18", "YYYYxyyyX", 3)
    assert c15_ab["B_len_is_2m3"]
    assert c15_ab["y_same_class_as_Xyx"]
    assert c15_ab["y_L1"] == 1
    rec15 = c25.c15_three_factor("aca_18", "YYYYxyyyX", 3)
    assert not rec15["found"]
    assert rec15["min_len"] >= 7
    assert rec15["pool"] == "nine_signed_type_configs_per_type_dedup"
    artifact = json.loads(
        (ROOT / "research/u124_stable_20260912/tables/c25_alt_words.json").read_text()
    )
    summary = artifact["summary"]
    assert summary["x_same_class_as_xi_all_Q"]
    assert not summary["x_three_any_hit"]
    assert summary["x_three_n_products"] == 1_529_400
    assert summary["x_three_all_min_len_ge_7"]
    assert summary["y_L1_closed_n_le_20"]
    assert summary["y_k1_abelian_only_2_minus"]
    assert summary["c15_five_match_P_plus_row2"]
    assert summary["c15_p_row2_match_ids"] == [
        "aca_20",
        "aca_42",
        "aca_65",
        "aca_91",
        "aca_104",
    ]
    assert summary["c22_6_is_row1_identity_only"]
    assert summary["c12_requires_ac_reachable_primitive"]
    assert summary["counts_are_nine_config_cartesian"]
    assert summary["negative_targets_via_inversion"]
    assert summary["independent_checker"] is False
    assert summary["c15_n_rows"] == 10
    assert summary["c15_B_len_always_2m3"]
    assert summary["c15_y_Xyx_same_class"]
    assert not summary["c15_three_any_hit"]
    assert summary["c15_three_n_checked"] == 10
    assert summary["c15_three_n_products"] == 2_884_950
    assert summary["c15_three_all_min_len_ge_7"]
    assert summary["solved_u124"] == 0
    assert artifact["inversion_closure"]["negative_targets_hit_iff_positive_inverse_factors"]
    assert artifact["c15_p_row2"]["five_match_P_plus_row2"]
    assert artifact["q_prime_x_three_factor"][0]["pool"] == (
        "nine_signed_type_configs_per_type_dedup"
    )


def test_c26_exact_l1_identities_and_n3():
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(CODE))
    import c26_y_exact_l1 as c26  # type: ignore

    cells = c26.window()
    assert (3, -1, 2) in cells
    assert (2, 1, 5) in cells
    assert (4, 1, 7) in cells
    assert (2, -1, 1) not in cells
    assert all(2 <= l1 <= 7 for _, _, l1 in cells)
    assert c26.y_combo(3, -1) == (1, -1, 2)
    assert c26.y_combo(2, 1) == (4, -1, 5)
    assert c26.y_combo(4, 1) == (6, -1, 7)
    controls = c26.planted_controls()
    assert controls["ok"]
    assert controls["independent_checker"] is False
    assert controls["mitm5_hit_found"]
    assert controls["mitm6_end_hit_found"]
    assert controls["mitm6_mid_hit_found"]
    assert controls["cancel_empty_fold_hit_found"]
    assert controls["cartesian_mitm_agree_tiny_m2"]
    rec = c26.scan_exact_l1(3, -1)
    assert not rec["found"]
    assert rec["method"] == "typed_cartesian"
    assert rec["min_len"] == 11
    assert rec["L1"] == 2
    assert rec["combo_a"] == 1
    assert rec["combo_b"] == -1
    assert rec["n_typed_tuples"] == rec["k"] * rec["n_A"] ** rec["m_R"] * rec["n_B"]
    assert rec["counts_are_typed_cartesian"]
    invc = c26.inversion_closure()
    assert invc["negative_targets_hit_iff_positive_inverse_factors"]
    json_path = ROOT / "research/u124_stable_20260912/tables/c26_y_exact_l1.json"
    if json_path.exists():
        artifact = json.loads(json_path.read_text())
        summary = artifact["summary"]
        assert not summary["any_hit"]
        assert summary["n_cells"] == 8
        assert summary["controls_ok"]
        assert summary["independent_checker"] is False
        assert summary["solved_u124"] == 0
        assert summary["counts_are_typed_cartesian"]
        assert summary["skipped_l1_1"]["n"] == 2
        assert [row["n"] for row in summary["skipped_l1_ge_8"]] == [5, 6, 7]
        assert summary["n_cartesian_cells"] == 2
        assert summary["n_mitm_cells"] == 6
        assert summary["cartesian_min_lens"] == [11, 13]
        assert summary["cartesian_observed_min_len"] == 11
        assert summary["cartesian_all_min_len_ge_11"]
        assert summary["n_cartesian_products_enumerated"] == 38_940
        assert summary["n_typed_tuples_cartesian"] == 38_940
        assert summary["n_typed_tuples_mitm"] == 33_815_591_648
        assert summary["n_typed_tuples_total"] == 33_815_630_588
        assert summary["mitm_counts_are_search_space_not_enumerated_products"]
        assert artifact["controls"]["mitm5_hit_found"]
        assert artifact["controls"]["mitm6_mid_hit_found"]
        assert artifact["controls"]["cancel_empty_fold_hit_found"]
        assert artifact["controls"]["cartesian_mitm_agree_tiny_m2"]
        assert artifact["controls"]["independent_checker"] is False


def test_c27_archival_k4_identities():
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(CODE))
    import c27_archival_k4 as c27  # type: ignore
    import ms_template_identities as ms  # type: ignore

    assert c27.c26.y_combo(3, -1) == (1, -1, 2)
    seqs = c27.type_sequences({"Rp": 2, "Rm": 1, "Sm": 1})
    assert len(seqs) == 12
    assert c27.ac2_planted()["ok"]
    assert c27.k4_planted()["ok"]
    rec = c27.scan_ac2_pair("P[2,-1]", *ms.parametric_p(2, -1))
    assert rec["drop"] == 0
    assert not rec["found"]
    json_path = ROOT / "research/u124_stable_20260912/tables/c27_archival_k4.json"
    if json_path.exists():
        artifact = json.loads(json_path.read_text())
        summary = artifact["summary"]
        assert summary["ac2_planted_ok"]
        assert not summary["parametric_any_hit"]
        assert not summary["initial_any_hit"]
        assert summary["initial_n_rows"] == 124
        assert summary["initial_n_changed_from_best"] == 36
        assert not summary["k4_found"]
        assert summary["k4_products_equal_typed"]
        assert summary["k4_n_typed_tuples"] == 5_128_200
        assert summary["k4_n_products"] == 5_128_200
        assert summary["k4_min_len"] == 11
        assert summary["independent_checker"] is False
        assert summary["solved_u124"] == 0


def test_c28_depth2_ac2_identities():
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(CODE))
    import c28_depth2_ac2 as c28  # type: ignore
    import ms_template_identities as ms  # type: ignore
    from experiments.equivalence_classes.lib.words import cyc_reduce, inv, rot
    from u124_census import one_occurrence_cyclic, two_block_shape

    for a, b in (("x", "Yxx"), ("xyxy", "YX"), ("YXXXYxx", "YYYYXyyyx")):
        aa, bb = rot(a, 1), rot(inv(b), 2)
        assert c28.concat_cyc(aa, bb) == cyc_reduce(aa + bb)
        assert c28.one_occ_reduced(cyc_reduce(a)) == one_occurrence_cyclic(a)
        assert c28.two_block_reduced(cyc_reduce(a)) == two_block_shape(a)
    assert c28.children_agree("x", "xy")
    assert c28.children_agree(*ms.parametric_p(2, -1))
    ctrl = c28.planted()
    assert ctrl["ok"]
    assert ctrl["hit"]["depth"] == 1
    assert ctrl["hit"]["drop"] > 0
    assert ctrl["miss_drop"] == 0
    rec = c28.scan_depth2("P[2,-1]", *ms.parametric_p(2, -1))
    assert rec["n_d1_unique"] > 0
    assert rec["n_d1_drop_unique"] == 0
    json_path = ROOT / "research/u124_stable_20260912/tables/c28_depth2_ac2.json"
    if json_path.exists():
        artifact = json.loads(json_path.read_text())
        summary = artifact["summary"]
        assert summary["planted_ok"]
        assert summary["children_fast_agrees"]
        assert summary["parametric_n"] == 36
        assert summary["initial_n_rows"] == 124
        if summary.get("census_complete"):
            assert summary["initial_n_changed_from_best"] == 36
            assert not summary["initial_any_hit"]
            assert not summary["initial_any_length_drop"]
            assert not summary["parametric_any_hit"]
            assert not summary["parametric_any_drop"]
            assert summary["initial_n_d1_drop_unique_total"] == 0
            assert summary["initial_n_drop_unique_total"] == 0
            assert summary["initial_n_d2_raw"] == 30_630_336
            assert summary["initial_n_d1_unique_sum"] == 36_312
            assert summary["initial_n_d2_unique_sum"] == 19_066_394
            assert summary["parametric_n_d2_unique_sum"] == 7_166_262
            assert summary["independent_checker"] is False
            assert summary["solved_u124"] == 0
            assert summary["d2_counts_are_row_local_exact_spellings"]
            assert summary["d2_raw_is_enumerated_edges"]
            assert (
                summary["replay_kind"]
                == "single_resumed_census_plus_sampled_same_implementation_checks"
            )


def test_c29_yxx_family_identities():
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(CODE))
    import c29_yxx_family as c29  # type: ignore
    import c22_gate_witness as c22  # type: ignore

    assert c29.DONOR == "YXXyxYx"
    assert c22.exp_on(c29.DONOR, "xy") == (0, -1)
    assert c29.typed_nine_size(1, 1, 1, 1) == 9
    assert c29.planted()["ok"]
    bridge = c29.free_bridge()
    assert bridge["product_is_YXXyxx"]
    assert bridge["not_an_ac2"]
    ab = c29.abelian_row("aca_120", "YYYXyyxx")
    assert ab["y_L1"] == 1
    assert ab["y_combo"]["a"] == -1 and ab["y_combo"]["b"] == 0
    assert ab["Xyx_same_as_y"] and ab["xyX_same_as_y"]
    assert ab["k1_len_obstruction"] and ab["even_k_forbidden"]
    assert ab["is_p_floor_companion"]
    assert ab["x_L1"] == 2
    json_path = ROOT / "research/u124_stable_20260912/tables/c29_yxx_family.json"
    artifact = json.loads(json_path.read_text())
    summary = artifact["summary"]
    assert summary["n_rows"] == 11
    assert summary["all_y_L1_1"]
    assert summary["all_y_combo_minus_one_zero"]
    assert summary["planted_ok"]
    assert summary["independent_checker"] is False
    assert summary["solved_u124"] == 0
    assert not summary["three_any_hit"]
    assert summary["three_products_equal_typed"]
    assert summary["three_all_min_len_ge_7"]
    assert summary["three_min_len"] == 7
    assert summary["three_n_products"] == 1_650_843
    assert summary["three_n_typed_tuples"] == 1_650_843
    assert summary["n_p_floor_companions"] == 5
    assert summary["counts_are_nine_config_cartesian"]
    per_row = {row["id"]: row["n_products"] for row in artifact["three_factor"]}
    assert per_row == {
        "aca_0": 181917,
        "aca_3": 152361,
        "aca_34": 126225,
        "aca_36": 126225,
        "aca_53": 181917,
        "aca_58": 152361,
        "aca_81": 181917,
        "aca_97": 215109,
        "aca_118": 103293,
        "aca_119": 126225,
        "aca_120": 103293,
    }


def test_c30_x_exact_l1_identities():
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(CODE))
    import c26_y_exact_l1 as c26  # type: ignore
    import c29_yxx_family as c29  # type: ignore
    import c30_x_exact_l1 as c30  # type: ignore
    import theory_wave1_replay as tw  # type: ignore

    xclass = c30.x_class_exponents()
    assert xclass["all_exp_one_zero"]
    assert xclass["inverse_all_exp_minus_one_zero"]
    assert c30.POSITIVE_X[1] == tw.XI
    rec = c30.scan_row("aca_120", "YYYXyyxx")
    assert rec["L1"] == 2
    assert rec["combo_a"] == -1 and rec["combo_b"] == 1
    assert rec["method"] == "typed_cartesian"
    assert rec["n_typed_tuples"] == 1012
    assert rec["n_products"] == 1012
    assert rec["n_products_equals_typed"]
    assert rec["min_len"] == 11
    assert not rec["found"]
    rec3 = c30.scan_row("aca_34", "YYYYXyyxx")
    assert rec3["L1"] == 3
    assert rec3["n_typed_tuples"] == 43125
    assert rec3["method"] == "typed_cartesian"
    assert not rec3["found"]
    assert rec3["min_len"] == 15
    controls = c26.planted_controls()
    assert controls["ok"]
    json_path = ROOT / "research/u124_stable_20260912/tables/c30_x_exact_l1.json"
    if json_path.exists():
        artifact = json.loads(json_path.read_text())
        summary = artifact["summary"]
        assert summary["n_rows"] == 11
        assert summary["all_abs_b_1"]
        assert summary["all_k_equals_L1"]
        assert summary["independent_checker"] is False
        assert summary["solved_u124"] == 0
        assert not summary["any_hit"]
        assert summary["n_cartesian_cells"] == 3
        assert summary["n_mitm_cells"] == 8
        assert summary["n_cartesian_products_enumerated"] == 107212
        assert summary["n_typed_tuples_cartesian"] == 107212
        assert summary["n_typed_tuples_mitm"] == 43_999_380_138
        assert summary["n_typed_tuples_total"] == 43_999_487_350
        assert summary["cartesian_products_equal_typed"]
        assert summary["cartesian_all_min_len_ge_7"]
        assert summary["cartesian_observed_min_len"] == 11
        assert summary["cartesian_min_lens"] == [15, 15, 11]
        assert summary["cartesian_ids"] == ["aca_34", "aca_53", "aca_120"]
        assert summary["mitm_counts_are_search_space_not_enumerated_products"]
        assert summary["n_p_floor_companions"] == 5

