"""C42 identity checks. New file: does not edit test_campaign.py."""

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
CODE = ROOT / "research" / "u124_stable_20260912" / "code"


def test_c42_yyxxxyxx_y_eq_cinv_identities():
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(CODE))
    import c22_gate_witness as c22  # type: ignore
    import c35_yxxx_family as c35  # type: ignore
    import c40_yyxxxyxx_x_eq_c as c40  # type: ignore
    import c42_yyxxxyxx_y_eq_cinv as c42  # type: ignore
    from experiments.equivalence_classes.lib.words import free_reduce  # type: ignore

    assert c22.exp_on(c42.DONOR, "xy") == (-1, -1)
    assert c42.y_combo_from_listed_c_exp(0, -1) == (0, -1, 1)
    try:
        c42.y_combo_from_listed_c_exp(-1, 0)
        assert False, "combo must stay restricted to listed C_ab=(0,-1)"
    except ValueError:
        pass
    try:
        c42.y_combo_from_listed_c_exp(1, 0)
        assert False, "combo must not accept C40 C_ab=(1,0)"
    except ValueError:
        pass
    assert c42.ORIENTATION == c35.C31_ORIENTATION
    assert c42.ORIENTATION != c35.C35_ORIENTATION
    assert c42.ORIENTATION != c40.C40_ORIENTATION
    best = c42.load_best()
    row = best["aca_38"]
    donor, companion = c42.split_pair(row["r1"], row["r2"])
    assert donor == c42.DONOR
    assert companion == "YYYYYXyyyyx"
    ab = c42.abelian_row("aca_38", companion)
    assert ab["y_L1"] == 1
    assert ab["y_combo"]["a"] == 0 and ab["y_combo"]["b"] == -1
    assert ab["C_exp"] == [0, -1]
    assert ab["pair_det"] == 1
    assert ab["C_cyc_len"] == 11
    assert ab["y_equiv_Cinv_in_abelianization"]
    assert ab["not_free_equality_y_equals_Cinv"]
    assert ab["x_L1"] == 2
    assert ab["x_combo"]["a"] == -1 and ab["x_combo"]["b"] == 1
    assert ab["companion_bs_mm1"]
    assert ab["companion_bs_m"] == 4
    rec = c42.three_factor_row("aca_38", companion)
    assert rec["n_products"] == 183924
    assert rec["n_products_equals_typed"]
    assert rec["min_len"] == 11
    assert not rec["found"]
    assert rec["orientation"] == c35.C31_ORIENTATION
    assert rec["hit_replay_outside_scanner"] is None
    planted = c42.planted()
    assert planted["ok"]
    assert planted["orientation"] == c35.C31_ORIENTATION
    assert planted["independent_checker"] is False
    witness = planted["hit"]
    assert witness["word"] == "y"
    assert planted["hit_replay_outside_scanner"]["ok"]
    assert free_reduce("".join(witness["factors"])) == "y"
    json_path = ROOT / "research/u124_stable_20260912/tables/c42_yyxxxyxx_y_eq_cinv.json"
    artifact = json.loads(json_path.read_text())
    summary = artifact["summary"]
    assert summary["n_rows"] == 1
    assert summary["all_y_combo_zero_minus_one"]
    assert summary["all_y_equiv_Cinv_in_abelianization"]
    assert summary["combo_restricted_to_listed_C_ab"]
    assert summary["not_six_row_yyxxxyxx_census"]
    assert summary["not_lumped_with_c40_or_c41"]
    assert summary["C_cyc_lens"] == [11]
    assert summary["all_k1_blocked_by_C_cyc_len_11"]
    assert summary["all_companion_bs_mm1_m4"]
    assert summary["bs_is_classification_not_a_c15_or_c31_rerun"]
    assert summary["three_all_orientation_c31"]
    assert summary["three_none_orientation_c35_or_c40"]
    assert summary["disjointness_relative_to_prior_typed_donor_family_censuses"]
    assert summary["c28_touched_rows_under_different_predicate"]
    assert summary["equal_typed_sizes_do_not_identify_censuses"]
    assert summary["completeness_is_all_typed_tuples_in_this_bounded_pool"]
    assert summary["hit_replay_outside_scanner_capability"] is True
    assert not summary["three_any_hit"]
    assert summary["three_n_products"] == 183924
    assert summary["three_n_typed_tuples"] == c42.EXPECTED_TYPED_TOTAL
    assert summary["three_products_equal_typed"]
    assert summary["three_min_len"] == 11
    assert summary["three_min_lens"] == [11]
    assert summary["independent_checker"] is False
    assert summary["solved_u124"] == 0
    per_row = {row["id"]: row["n_products"] for row in artifact["three_factor"]}
    assert per_row == c42.EXPECTED_TYPED
    abelian_ids = [row["id"] for row in artifact["abelian"]]
    assert abelian_ids == ["aca_38"]
    assert artifact["three_factor"][0]["hit_replay_outside_scanner"] is None


if __name__ == "__main__":
    test_c42_yyxxxyxx_y_eq_cinv_identities()
    print("test_c42_yyxxxyxx_y_eq_cinv_identities ok")
