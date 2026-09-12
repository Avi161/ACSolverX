"""C43 identity checks. New file: does not edit test_campaign.py."""

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
CODE = ROOT / "research" / "u124_stable_20260912" / "code"


def test_c43_yyxxyxx_x_eq_cinv_identities():
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(CODE))
    import c22_gate_witness as c22  # type: ignore
    import c35_yxxx_family as c35  # type: ignore
    import c40_yyxxxyxx_x_eq_c as c40  # type: ignore
    import c43_yyxxyxx_x_eq_cinv as c43  # type: ignore
    from experiments.equivalence_classes.lib.words import free_reduce  # type: ignore

    assert c22.exp_on(c43.DONOR, "xy") == (0, -1)
    assert c43.x_combo_from_listed_c_exp(-1, 0) == (0, -1, 1)
    try:
        c43.x_combo_from_listed_c_exp(1, 0)
        assert False, "combo must stay restricted to listed C_ab=(-1,0)"
    except ValueError:
        pass
    try:
        c43.x_combo_from_listed_c_exp(0, -1)
        assert False, "combo must not accept C42-style C_ab=(0,-1)"
    except ValueError:
        pass
    assert c43.ORIENTATION == c35.C31_ORIENTATION
    assert c43.ORIENTATION != c35.C35_ORIENTATION
    assert c43.ORIENTATION != c40.C40_ORIENTATION
    best = c43.load_best()
    row = best["aca_43"]
    donor, companion = c43.split_pair(row["r1"], row["r2"])
    assert donor == c43.DONOR
    assert companion == "YYxyXYxyXyX"
    ab = c43.abelian_row("aca_43", companion)
    assert ab["x_L1"] == 1
    assert ab["x_combo"]["a"] == 0 and ab["x_combo"]["b"] == -1
    assert ab["C_exp"] == [-1, 0]
    assert ab["D_exp"] == [0, -1]
    assert ab["pair_det"] == -1
    assert ab["D_cyc_len"] == 7
    assert ab["C_cyc_len"] == 11
    assert ab["x_equiv_Cinv_in_abelianization"]
    assert ab["not_free_equality_x_equals_Cinv"]
    assert ab["y_L1"] == 1
    assert ab["y_combo"]["a"] == -1 and ab["y_combo"]["b"] == 0
    assert ab["y_k3_was_c33_not_part_of_c43"]
    assert ab["do_not_rerun_c33"]
    assert ab["c16_escape_is_disclosure_not_a_solve"]
    assert ab["family_a_floor_is_classification_not_a_c16_rerun"]
    rec = c43.three_factor_row("aca_43", companion)
    assert rec["n_products"] == 154368
    assert rec["n_products_equals_typed"]
    assert (rec["n_Rplus"], rec["n_Rminus"], rec["n_Splus"], rec["n_Sminus"]) == (
        24,
        24,
        28,
        28,
    )
    assert not rec["found"]
    assert rec["orientation"] == c35.C31_ORIENTATION
    assert rec["hit_replay_outside_scanner"] is None
    planted = c43.planted()
    assert planted["ok"]
    assert planted["orientation"] == c35.C31_ORIENTATION
    assert planted["independent_checker"] is False
    witness = planted["hit"]
    assert witness["word"] == "x"
    assert planted["hit_replay_outside_scanner"]["ok"]
    assert free_reduce("".join(witness["factors"])) == "x"
    json_path = ROOT / "research/u124_stable_20260912/tables/c43_yyxxyxx_x_eq_cinv.json"
    artifact = json.loads(json_path.read_text())
    summary = artifact["summary"]
    assert summary["n_rows"] == 1
    assert summary["all_x_combo_zero_minus_one"]
    assert summary["all_x_equiv_Cinv_in_abelianization"]
    assert summary["combo_restricted_to_listed_C_ab"]
    assert summary["not_six_row_yyxxyxx_census"]
    assert summary["not_lumped_with_c33_or_other_l1_1_leftovers"]
    assert summary["do_not_rerun_c33"]
    assert summary["C_cyc_lens"] == [11]
    assert summary["D_cyc_lens"] == [7]
    assert summary["all_k1_blocked_by_C_cyc_len_11"]
    assert summary["three_all_orientation_c31"]
    assert summary["three_none_orientation_c35_or_c40"]
    assert summary["disjointness_relative_to_prior_typed_donor_family_censuses"]
    assert summary["c28_touched_rows_under_different_predicate"]
    assert summary["c33_used_c35_orientation_on_this_row_for_y"]
    assert summary["equal_typed_sizes_do_not_identify_censuses"]
    assert summary["c16_escape_is_disclosure_not_a_solve"]
    assert summary["family_a_floor_is_classification_not_a_c16_rerun"]
    assert summary["completeness_is_all_typed_tuples_in_this_bounded_pool"]
    assert summary["hit_replay_outside_scanner_capability"] is True
    assert not summary["three_any_hit"]
    assert summary["three_n_products"] == 154368
    assert summary["three_n_typed_tuples"] == c43.EXPECTED_TYPED_TOTAL
    assert summary["three_products_equal_typed"]
    assert summary["independent_checker"] is False
    assert summary["solved_u124"] == 0
    per_row = {row["id"]: row["n_products"] for row in artifact["three_factor"]}
    assert per_row == c43.EXPECTED_TYPED
    abelian_ids = [row["id"] for row in artifact["abelian"]]
    assert abelian_ids == ["aca_43"]
    assert artifact["three_factor"][0]["hit_replay_outside_scanner"] is None


if __name__ == "__main__":
    test_c43_yyxxyxx_x_eq_cinv_identities()
    print("test_c43_yyxxyxx_x_eq_cinv_identities ok")
