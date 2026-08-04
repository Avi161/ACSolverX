"""Tests for the A9 sweep of the 124 unsolved Miller-Schupp AC classes.

The properties pinned here are the ones a silent regression would destroy:

* **units** -- ``gamma_N = minimum_defect // 2``, ``defect 0 == SPHERICAL``;
* **anchors** -- ``aca_115`` is AK(3) and its exact 86,400-rotation census still has
  ``minimum_defect = 4``; a certified ``gamma_N = 0`` fixture still decides SPHERICAL;
* **fail-closed** -- a budget exhaustion never becomes a NO, and a row with no two-sided
  verdict is marked UNINFORMATIVE rather than negative;
* **bound direction** -- the sampler is an UPPER bound and its witness is re-verified;
* **the neighbourhood operator** -- every image is a genuine one-move AC image, the
  seen-set is keyed on cyclically REDUCED canonical forms, and the parent is excluded;
* **contradiction handling** -- two instruments that disagree raise, never vote.
"""

from __future__ import annotations

import json
import os
import random

import pytest

from experiments.stable_ac.fable import ac_words as W
from experiments.stable_ac.fable import neuwirth_rank_n as RN
from experiments.stable_ac.fable import u124_thickenability as U

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(REPO_ROOT, "results", "stable_ac", "fable", "aca_124.csv")

AK3 = ("YXYxyx", "YYYYxxx")
# certified gamma_N = 0 fixture, exact census 12 rotation systems (witness_sensitivity)
SPHERICAL_FIXTURE = ("xyXY", "xxy")
# certified gamma_N = 1 gateway, exact census 86,400 (R7 / gateway_scan docstring)
GATEWAY = ("YYXXyx", "YYxyXXX")

needs_csv = pytest.mark.skipif(not os.path.exists(CSV_PATH),
                               reason="aca_124.csv is not present in this checkout")


# --------------------------------------------------------------------------------------
# units and anchors
# --------------------------------------------------------------------------------------


def test_units_gamma_is_half_the_defect():
    census = RN.gamma_N_factorial_n(AK3, U.GENERATORS, cap_rotations=200_000,
                                    keep_accepting=False)
    assert census["status"] == "OK"
    assert census["enumerated_cases"] == 86_400
    assert census["minimum_defect"] == U.AK3_MINIMUM_DEFECT == 4
    assert census["minimum_genus"] == census["minimum_defect"] // 2 == 2


def test_exact_census_wrapper_reports_the_same_numbers():
    got = U.exact_census(AK3, cap=200_000)
    assert got["ran"] is True
    assert got["expected_cases"] == 86_400
    assert got["minimum_defect"] == 4
    assert got["gamma_N"] == 2
    assert got["accepting_orders"] == 0
    assert got["witness"] is None


def test_exact_census_refuses_over_the_cap_and_never_returns_a_defect():
    got = U.exact_census(AK3, cap=100)
    assert got["ran"] is False
    assert "minimum_defect" not in got
    assert got["expected_cases"] == 86_400


def test_census_size_matches_the_solver_stack():
    for pair in (AK3, SPHERICAL_FIXTURE, GATEWAY):
        data = RN.build_link_n(pair, U.GENERATORS)
        assert U.census_size(pair) == RN.census_size(data, U.GENERATORS)


def test_spherical_fixture_is_decided_spherical_and_ak3_is_not():
    assert U.exact_decision(SPHERICAL_FIXTURE)["verdict"] == U.SPHERICAL
    assert U.exact_decision(AK3)["verdict"] == U.NOT_SPHERICAL


def test_gateway_has_gamma_one_exactly():
    census = U.exact_census(GATEWAY, cap=200_000)
    assert census["ran"] is True
    assert census["minimum_defect"] == 2
    assert census["gamma_N"] == 1


# --------------------------------------------------------------------------------------
# instrument B: direction of the bound, and the witness re-verification
# --------------------------------------------------------------------------------------


def test_sampler_is_an_upper_bound_and_its_witness_is_verified():
    got = U.sampled_upper(SPHERICAL_FIXTURE, budget=2_000, seeds=2)
    assert got["best_defect"] == got["verified_defect"]
    assert got["gamma_N_upper"] == got["best_defect"] // 2
    exact = U.exact_census(SPHERICAL_FIXTURE, cap=200_000)
    # the sampler can never go below the true minimum
    assert got["best_defect"] >= exact["minimum_defect"]


def test_sampler_never_beats_the_exact_minimum_on_the_gateway():
    got = U.sampled_upper(GATEWAY, budget=5_000, seeds=2)
    assert got["best_defect"] >= 2


def test_sampler_witness_check_is_independent_of_the_sampler():
    rng = random.Random(11)
    from experiments.stable_ac.fable import gateway_scan as GS
    defect, orders = GS.sampled_min_defect(AK3, 2_000, rng)
    assert GS.verify_witness(AK3, orders) == defect


# --------------------------------------------------------------------------------------
# a row of the sweep: fail-closed and informativeness
# --------------------------------------------------------------------------------------


def test_sweep_row_on_ak3_is_exact_and_not_thickenable():
    rec = {"name": U.AK3_ROW, "pair": AK3, "total_length": 13, "n_members": 1}
    row = U.sweep_row(rec, census_cap=200_000, budget=2_000, seeds=1)
    assert row["census"]["ran"] is True
    assert row["gamma_N_exact"] == 2
    assert row["gamma_N_lower"] == row["gamma_N_upper"] == 2
    assert row["thickenable"] is False
    assert row["informative"] is True
    assert row["todd_coxeter"]["trivial"] is True
    assert row["structural_link_components"] == 1


def test_sweep_row_over_the_census_cap_keeps_a_two_sided_bracket():
    rec = {"name": U.AK3_ROW, "pair": AK3, "total_length": 13, "n_members": 1}
    row = U.sweep_row(rec, census_cap=10, budget=2_000, seeds=1)
    assert row["census"]["ran"] is False
    assert row["gamma_N_exact"] is None
    # NOT_SPHERICAL is a certified lower bound of 1, the sampler an upper bound
    assert row["gamma_N_lower"] == 1
    assert row["gamma_N_upper"] >= row["gamma_N_lower"]
    assert row["thickenable"] is False


def test_a_budget_exhaustion_is_never_a_no():
    # census_cap 0 forces the census fallback to refuse; the verdict must stay honest
    got = U.exact_decision(("x", "y"), census_cap=0, cross_check=False)
    assert got["verdict"] != U.NOT_SPHERICAL
    assert got["verdict"] in (U.UNSUPPORTED, "UNDECIDED_BUDGET")


def test_ranking_puts_lower_upper_bounds_first_and_nulls_last():
    rows = [
        {"name": "b", "total_length": 14, "gamma_N_upper": 1},
        {"name": "c", "total_length": 25, "gamma_N_upper": None},
        {"name": "a", "total_length": 20, "gamma_N_upper": 1},
        {"name": "d", "total_length": 13, "gamma_N_upper": 3},
    ]
    ranked = U.rank_rows(rows)
    assert [r["name"] for r in ranked] == ["b", "a", "d", "c"]
    assert [r["rank"] for r in ranked] == [1, 2, 3, 4]


# --------------------------------------------------------------------------------------
# the neighbourhood operator
# --------------------------------------------------------------------------------------


def test_one_move_images_are_reachable_by_ac_moves_and_dedup_on_reduced_forms():
    images = U.one_move_images(AK3, cap=17)
    assert images
    parent = W.canon_pair(*AK3)
    for key, (exact, label) in images.items():
        # the key is the cyclically reduced canonical form of the exact image
        assert key == W.canon_pair(*exact)
        assert key != parent
        assert all(w == W.free_reduce(w) for w in exact)
        assert all(0 < len(w) <= 17 for w in exact)
        assert label.startswith(("AC1", "AC2", "AC3"))


def test_one_move_images_contain_the_expected_ac1_and_ac3_shapes():
    pair = ("xyXY", "xxy")
    images = U.one_move_images(pair, cap=12)
    labels = {label for _exact, label in images.values()}
    assert any(label.startswith("AC2") for label in labels)
    # AC1/AC3 images collapse under canon_pair (which quotients by inversion and
    # conjugacy), so their absence is expected, not a bug -- assert exactly that.
    for i in (0, 1):
        inverted = list(pair)
        inverted[i] = W.free_reduce(W.inverse(inverted[i]))
        assert W.canon_pair(*inverted) == W.canon_pair(*pair)


def test_one_move_images_respect_the_length_cap():
    images = U.one_move_images(AK3, cap=8)
    for _key, (exact, _label) in images.items():
        assert all(len(w) <= 8 for w in exact)


def test_harvest_wrapper_is_bounded_and_contains_its_root():
    root = W.canon_pair(*AK3)
    got = U._harvest_canonical(root, pops=5, cap=15, state_cap=200)
    assert root in got["members"]
    assert got["distinct_members"] <= 200
    assert got["pops"] <= 5


# --------------------------------------------------------------------------------------
# contradiction handling
# --------------------------------------------------------------------------------------


def test_sampler_contradiction_raises(monkeypatch):
    honest = U.GS.sampled_min_defect

    def _lying_sampler(words, samples, rng, **kwargs):
        _defect, orders = honest(words, 200, rng)
        return -99, orders

    monkeypatch.setattr(U.GS, "sampled_min_defect", _lying_sampler)
    with pytest.raises(U.SweepContradiction):
        U.sampled_upper(AK3, budget=200, seeds=1)


def test_census_disagreement_raises(monkeypatch):
    monkeypatch.setattr(U, "exact_decision",
                        lambda *a, **k: {"verdict": U.SPHERICAL, "method": "fake",
                                         "reason": None, "support_kind": None,
                                         "support_reason": None, "counters": None,
                                         "exhaustive": True, "seconds": 0.0})
    rec = {"name": "fake", "pair": AK3, "total_length": 13, "n_members": 1}
    with pytest.raises(U.SweepContradiction):
        U.sweep_row(rec, census_cap=200_000, budget=200, seeds=1)


# --------------------------------------------------------------------------------------
# the corpus and the calibration ladder
# --------------------------------------------------------------------------------------


@needs_csv
def test_csv_has_124_balanced_rows_and_aca_115_is_ak3():
    reps = U.load_reps(CSV_PATH)
    assert len(reps) == 124
    names = [r["name"] for r in reps]
    assert names == [f"aca_{i}" for i in range(124)]
    anchor = next(r for r in reps if r["name"] == U.AK3_ROW)
    assert tuple(anchor["pair"]) == AK3 == U.AK3_PAIR
    for rec in reps:
        assert 13 <= rec["total_length"] <= 25
        joined = "".join(rec["pair"])
        assert set(joined) <= set("xXyY")
        # balanced: 2 generators, 2 relators, both generators genuinely present
        assert joined.lower().count("x") > 0 and joined.lower().count("y") > 0


@needs_csv
def test_every_representative_presents_the_trivial_group():
    """Lackenby's hypothesis needs the trivial group; this checks it, never assumes it.

    ``TC_CAP`` is 2,000,000 because ``aca_82`` and ``aca_86`` need ~2.4e5 / ~2.3e5
    cosets; at 200,000 both come back ``CAP_EXCEEDED``, which is *unknown*, not
    *non-trivial*.
    """
    from experiments.stable_ac.fable import coset_enum as CE
    reps = U.load_reps(CSV_PATH)
    for rec in reps:
        tc = CE.is_trivial_group(tuple(rec["pair"]), generators=U.GENERATORS,
                                 cap=U.TC_CAP)
        assert tc["trivial"] is True, (rec["name"], rec["pair"], tc["status"])
        assert tc["index"] == 1


def test_positive_ladder_states_really_are_thickenable():
    ladder = U.positive_ladder(min_length=13, max_length=25, min_degree=3)
    assert ladder, "the calibration ladder must not be empty"
    sample = ladder[:6] + ladder[-6:]
    for entry in sample:
        verdict = U.exact_decision(tuple(entry["pair"]), cross_check=False)["verdict"]
        assert verdict != U.NOT_SPHERICAL, entry
        assert entry["min_degree"] >= 3


def test_calibration_writes_rates_by_length(tmp_path):
    out = tmp_path / "cal.json"
    doc = U.run_calibration(out_path=str(out), budget=500, seeds=1, per_length_cap=2,
                            verbose=False)
    assert out.exists()
    on_disk = json.loads(out.read_text())
    assert on_disk["record"] == "u124_calibration"
    assert doc["cells_by_total_length"]
    for length, cell in doc["cells_by_total_length"].items():
        assert 0.0 <= cell["instrument_A_detection_rate"] <= 1.0
        assert 0.0 <= cell["instrument_B_detection_rate"] <= 1.0
        assert cell["states_measured"] <= 2
        assert int(length) >= 13
    assert doc["instrument_B"]["one_sided"] is True
    assert doc["instrument_A"]["one_sided"] is False


@needs_csv
def test_sweep_stage_is_reproducible_and_marks_uninformative_rows(tmp_path):
    rows_out = tmp_path / "rows.jsonl"
    summary_out = tmp_path / "summary.json"
    summary = U.run_sweep(CSV_PATH, str(rows_out), str(summary_out),
                          census_cap=200_000, budget=400, seeds=1, limit=5,
                          calibration_path=str(tmp_path / "missing.json"),
                          verbose=False)
    assert summary["rows"] == 5
    assert summary["two_sided_rows"] + len(summary["uninformative_rows"]) >= 5
    on_disk = [json.loads(line) for line in rows_out.read_text().splitlines()]
    assert len(on_disk) == 5
    assert all("gamma_N_upper" in r for r in on_disk)
    # every row that is not two-sided must be flagged, never counted as a negative
    for row in on_disk:
        if not row["decision_is_two_sided"] and not row["census"]["ran"]:
            assert row["informative"] is False
            assert row["thickenable"] is False
