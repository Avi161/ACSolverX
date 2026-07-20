"""``experiments/analysis/combined_benchmark.py`` -- the merged ladder+reach benchmark.

Reads the real ``results/benchmark/subsets/`` and ``results/benchmark/reach/`` fixtures
(committed data, not stubbed) and writes to ``tmp_path`` so the test suite never touches
``results/benchmark/combined/``.
"""

import csv
import json

import pytest

from experiments.analysis.combined_benchmark import PAIRING, build_combined, load_combined


def test_pairing_map_is_exact():
    assert PAIRING == {11: (10, 1), 22: (20, 2), 44: (40, 4), 66: (60, 6)}


def test_combined_11_is_10_ladder_plus_1_reach(tmp_path):
    _, _, doc = build_combined(11, out_dir=str(tmp_path))
    assert doc["n_ladder"] == 10 and doc["n_reach"] == 1
    assert doc["size"] == 11 and len(doc["rows"]) == 11
    for k in ("combined_id", "size", "n_ladder", "n_reach", "ladder_source",
              "reach_source", "comparison_budget", "pairing", "purpose", "rows"):
        assert k in doc
    assert doc["combined_id"] == 11
    assert doc["comparison_budget"] == 50_000


def test_ladder_rows_carry_r1_r2_and_baseline_at_50k_fields(tmp_path):
    _, _, doc = build_combined(11, out_dir=str(tmp_path))
    ladder = [r for r in doc["rows"] if r["source"] == "ladder"]
    assert len(ladder) == 10
    for r in ladder:
        assert r["r1"] and r["r2"]
        for k in ("baseline_solved_at_50k", "baseline_nodes_at_50k",
                  "baseline_path_at_50k", "baseline_min_relator_length_at_50k",
                  "baseline_progress_at_50k"):
            assert k in r
        assert r["name"] == f"ms{r['pres_id']}"


def test_reach_row_ak3_carries_bar_to_beat_and_aut_min_rep(tmp_path):
    _, _, doc = build_combined(11, out_dir=str(tmp_path))
    reach = [r for r in doc["rows"] if r["source"] == "reach"]
    assert len(reach) == 1
    ak3 = reach[0]
    assert ak3["name"] == "AK(3)"
    assert ak3["bar_to_beat"] == "min_relator_length < 13"
    assert ak3["aut_min_rep_r1"] and ak3["aut_min_rep_r2"]
    assert "aut_min_rep_total_length" in ak3
    assert "note" in ak3
    assert "members" not in ak3            # AK(3) has no members list


def test_reach_row_with_members_at_size_22(tmp_path):
    _, _, doc = build_combined(22, out_dir=str(tmp_path))
    reach = [r for r in doc["rows"] if r["source"] == "reach"]
    assert len(reach) == 2
    named = next(r for r in reach if r["name"] != "AK(3)")
    assert "members" in named
    assert "note" not in named            # only the AK(3) row carries a note


def test_every_row_has_the_common_keys(tmp_path):
    _, _, doc = build_combined(44, out_dir=str(tmp_path))
    assert len(doc["rows"]) == 44
    for r in doc["rows"]:
        for k in ("name", "source", "r1", "r2", "base_total_length"):
            assert k in r and r[k] not in (None, "")
        assert r["source"] in ("ladder", "reach")


def test_base_total_length_equals_len_r1_plus_len_r2(tmp_path):
    _, _, doc = build_combined(66, out_dir=str(tmp_path))
    for r in doc["rows"]:
        assert r["base_total_length"] == len(r["r1"]) + len(r["r2"])


def test_json_and_csv_both_written_with_matching_row_counts(tmp_path):
    json_path, csv_path, doc = build_combined(11, out_dir=str(tmp_path))
    assert json_path.endswith("benchmark_combined_11.json")
    assert csv_path.endswith("benchmark_combined_11.csv")
    with open(json_path) as f:
        reloaded = json.load(f)
    assert reloaded == doc
    with open(csv_path, newline="") as f:
        csv_rows = list(csv.DictReader(f))
    assert len(csv_rows) == len(doc["rows"]) == 11


def test_load_combined_reads_back_the_written_doc(tmp_path):
    _, _, doc = build_combined(22, out_dir=str(tmp_path))
    assert load_combined(22, out_dir=str(tmp_path)) == doc


def test_all_four_sizes_build_with_the_expected_counts(tmp_path):
    for combined_id, (n_ladder, n_reach) in PAIRING.items():
        _, _, doc = build_combined(combined_id, out_dir=str(tmp_path))
        assert (doc["n_ladder"], doc["n_reach"]) == (n_ladder, n_reach)
        assert doc["size"] == n_ladder + n_reach


def test_unknown_combined_id_raises():
    with pytest.raises(ValueError):
        build_combined(99)
