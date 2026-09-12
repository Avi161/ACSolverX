"""C45 identity checks. New file: does not edit test_campaign.py."""

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
CODE = ROOT / "research" / "u124_stable_20260912" / "code"


def test_c45_yxxx_y_eq_cinv_identities():
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(CODE))
    import c22_gate_witness as c22  # type: ignore
    import c35_yxxx_family as c35  # type: ignore
    import c40_yyxxxyxx_x_eq_c as c40  # type: ignore
    import c45_yxxx_y_eq_cinv as c45  # type: ignore
    from experiments.equivalence_classes.lib.words import free_reduce  # type: ignore

    assert c22.exp_on(c45.DONOR, "xy") == (-1, 0)
    assert c45.y_combo_from_listed_c_exp(0, -1) == (0, -1, 1)
    try:
        c45.y_combo_from_listed_c_exp(-1, 0)
        assert False, "combo must stay restricted to listed C_ab=(0,-1)"
    except ValueError:
        pass
    try:
        c45.y_combo_from_listed_c_exp(1, 0)
        assert False, "combo must not accept C40 C_ab=(1,0)"
    except ValueError:
        pass
    assert c45.ORIENTATION == c35.C31_ORIENTATION
    assert c45.ORIENTATION != c35.C35_ORIENTATION
    assert c45.ORIENTATION != c40.C40_ORIENTATION
    best = c45.load_best()
    row = best["aca_117"]
    donor, companion = c45.split_pair(row["r1"], row["r2"])
    assert donor == c45.DONOR
    assert companion == "YYYXyyx"
    assert {row["r1"], row["r2"]} == {"YYYXyyx", "YXXXyxx"}
    ab = c45.abelian_row("aca_117", companion)
    assert ab["y_L1"] == 1
    assert ab["y_combo"]["a"] == 0 and ab["y_combo"]["b"] == -1
    assert ab["C_exp"] == [0, -1]
    assert ab["D_exp"] == [-1, 0]
    assert ab["pair_det"] == 1
    assert ab["D_cyc_len"] == 7
    assert ab["C_cyc_len"] == 7
    assert ab["y_equiv_Cinv_in_abelianization"]
    assert ab["not_free_equality_y_equals_Cinv"]
    assert ab["k1_blocked_by_C_cyc_len_7"]
    assert ab["x_L1"] == 1
    assert ab["x_combo"]["a"] == -1 and ab["x_combo"]["b"] == 0
    assert ab["x_k3_was_c35_not_part_of_c45"]
    assert ab["do_not_rerun_c35"]
    rec = c45.three_factor_row("aca_117", companion)
    assert rec["n_products"] == 83349
    assert rec["n_products_equals_typed"]
    assert (rec["n_Rplus"], rec["n_Rminus"], rec["n_Splus"], rec["n_Sminus"]) == (
        21,
        21,
        21,
        21,
    )
    assert rec["equal_typed_size_does_not_identify_c35_aca117"]
    assert not rec["found"]
    assert rec["orientation"] == c35.C31_ORIENTATION
    assert rec["hit_replay_outside_scanner"] is None
    planted = c45.planted()
    assert planted["ok"]
    assert planted["orientation"] == c35.C31_ORIENTATION
    witness = planted["hit"]
    assert witness["word"] == "y"
    assert planted["hit_replay_outside_scanner"]["ok"]
    assert free_reduce("".join(witness["factors"])) == "y"
    json_path = ROOT / "research/u124_stable_20260912/tables/c45_yxxx_y_eq_cinv.json"
    if json_path.exists():
        artifact = json.loads(json_path.read_text())
        summary = artifact["summary"]
        assert summary["n_rows"] == 1
        assert summary["all_y_combo_zero_minus_one"]
        assert summary["all_y_equiv_Cinv_in_abelianization"]
        assert summary["combo_restricted_to_listed_C_ab"]
        assert summary["not_six_row_yxxx_census"]
        assert summary["do_not_rerun_c35"]
        assert summary["C_cyc_lens"] == [7]
        assert summary["D_cyc_lens"] == [7]
        assert summary["all_k1_blocked_by_C_cyc_len_7"]
        assert summary["three_all_orientation_c31"]
        assert summary["three_none_orientation_c35_or_c40"]
        assert summary["equal_typed_size_83349_does_not_identify_c35_aca117"]
        assert summary["three_min_len_is_product_word_not_pair_total"]
        assert summary["hit_replay_outside_scanner_capability"] is True
        assert not summary["three_any_hit"]
        assert summary["three_n_products"] == 83349
        assert summary["three_n_typed_tuples"] == c45.EXPECTED_TYPED_TOTAL
        assert summary["independent_checker"] is False
        assert summary["solved_u124"] == 0
        per_row = {row["id"]: row["n_products"] for row in artifact["three_factor"]}
        assert per_row == c45.EXPECTED_TYPED
        abelian_ids = [row["id"] for row in artifact["abelian"]]
        assert abelian_ids == ["aca_117"]
        assert artifact["three_factor"][0]["hit_replay_outside_scanner"] is None


if __name__ == "__main__":
    test_c45_yxxx_y_eq_cinv_identities()
    print("test_c45_yxxx_y_eq_cinv_identities ok")
