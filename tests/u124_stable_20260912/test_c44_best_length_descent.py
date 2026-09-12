"""C44 identity checks. New file: does not edit test_campaign.py."""

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
CODE = ROOT / "research" / "u124_stable_20260912" / "code"


def test_c44_best_length_descent_identities():
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(CODE))
    import c44_best_length_descent as c44  # type: ignore
    import c28_depth2_ac2 as c28  # type: ignore
    from experiments.equivalence_classes.lib.words import canon_pair

    c44.assert_inputs()
    assert len(c44.LISTED_IDS) == 47
    assert len(c44.SHORT_IDS) == 13
    assert len(c44.FLOOR_IDS) == 36
    assert set(c44.SHORT_IDS) | set(c44.FLOOR_IDS) == set(c44.LISTED_IDS)
    assert c44.LISTED_IDS == tuple(
        sorted(c44.LISTED_IDS, key=lambda s: int(s.split("_")[1]))
    )
    assert "aca_115" in c44.SHORT_IDS
    assert "aca_111" in c44.FLOOR_IDS
    assert c44.file_sha256(c44.DATA_BEST) == c44.BEST_SHA256
    assert c44.file_sha256(c44.DATA_INITIAL) == c44.INITIAL_SHA256
    assert "children_fast" not in c44.apply_macro_spec.__code__.co_names

    assert c28.children_agree("x", "xy")
    assert c28.children_agree(*c44.CORRIDOR_POS)
    ctrl = c44.planted()
    assert ctrl["ok"]
    assert ctrl["children_fast_agrees"]
    assert ctrl["spec_replay_agrees_on_sample"]
    assert ctrl["corridor_pos_ok"]
    assert ctrl["positive_witness_uses_spec_replay"]
    assert ctrl["hit_depth"] == 1
    assert ctrl["miss_drop"] == 0

    best, initial = c44.load_tables()
    meta_115 = c44.provenance_of("aca_115", best, initial)
    assert meta_115["best_equals_initial"]
    assert meta_115["provenance"] == "ordinary_displayed_initial"
    meta_111 = c44.provenance_of("aca_111", best, initial)
    assert not meta_111["best_equals_initial"]
    assert meta_111["provenance"] == "mu_floor_best_relative"
    meta_120 = c44.provenance_of("aca_120", best, initial)
    assert meta_120["in_c44_1"] and meta_120["in_short"]

    kids = c28.unique_children("x", "xy")
    assert kids
    spec = c44.apply_macro_spec("x", "xy", kids[0][2])
    assert canon_pair(*spec) == canon_pair(kids[0][0], kids[0][1])

    json_path = ROOT / "research/u124_stable_20260912/tables/c44_best_length_descent.json"
    if json_path.exists():
        artifact = json.loads(json_path.read_text())
        summary = artifact["summary"]
        assert summary["listed_ids"] == list(c44.LISTED_IDS)
        assert summary["best_sha256"] == c44.BEST_SHA256
        assert summary["not_full_depth_3"]
        assert summary["depth_counts_ac2_macro_steps"]
        assert summary["c43_is_aca43_ncl_not_this_census"]
        assert summary["independent_checker"] is False
        assert summary["solved_u124"] == 0
        assert not summary["c10_finish"]
        if summary.get("census_complete"):
            assert summary["c44_1_complete"]
            assert summary["c44_2_complete"]
            assert summary["n_done"] == 47
            assert summary["n_d2_unique_sum"] == 5_521_175
            assert summary["n_d3_unique_from_eq_sum"] == 116_608
            assert summary["n_d2_eq_total"] == 819
            assert summary["n_d1_drop_total"] == 0
            assert summary["n_d2_drop_total"] == 0
            assert summary["n_d3_drop_total"] == 0
            assert summary["n_rows_with_replayed_drop"] == 0
            assert summary["any_leq_12"] is False
            rows = {row["id"]: row for row in artifact["listed"]["rows"]}
            assert rows["aca_115"]["n_d2_eq_unique"] == 12
            assert rows["aca_115"]["n_d3_unique_from_eq"] == 819
            assert rows["aca_111"]["provenance"] == "mu_floor_best_relative"


if __name__ == "__main__":
    test_c44_best_length_descent_identities()
    print("test_c44_best_length_descent_identities ok")
