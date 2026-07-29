"""Tests for ``experiments/stable_ac/fable/witness_sensitivity.py``.

Load-bearing checks:

* the fixture ``("xyXY","xxy")`` really is gamma_N = 0 with exactly 2 of 12
  compatible rotation systems at defect 0 (pins the census wiring and the UNHALVED
  defect convention);
* ``witness_probe`` returns a hit ONLY after ``verify_witness`` independently
  recomputes defect 0, and never fabricates a hit on a state with gamma_N = 1;
* spike children really are single spikes (length + 2, same free reduction);
* ``grow_chain`` produces a rung certified by census AND witness at small length, and
  the recorded witness re-verifies in isolation;
* the even-parity seed is a census-certified gamma-0 graft image at total length 10;
* detection accounting: hits <= runs, rate == hits / runs, perfect detection on the
  tiny fixture;
* ``summarize`` finds the 40k half-crossing and persistent-zero lengths on synthetic
  tables, and the artifact carries the bound-direction / null-reading statements
  (the trap of experiments/lessons/parallel-runs-and-bound-direction.md);
* a zero deadline yields a truncated but valid, parseable artifact.
"""

from __future__ import annotations

import json
import random
import time

from experiments.stable_ac.fable import gateway_scan as GS
from experiments.stable_ac.fable import witness_sensitivity as ws
from experiments.stable_ac.fable.ac_words import free_reduce
from experiments.stable_ac.fable.neuwirth_rank_n import gamma_N_factorial_n

FIXTURE = ("xyXY", "xxy")
SPIKED_GAMMA1 = ("xyXY", "yYxxy")        # gamma_N = 1 (recorded fixture)


# --------------------------------------------------------------------------------------
# fixture and primitives
# --------------------------------------------------------------------------------------


def test_fixture_is_gamma0_with_two_accepting_systems():
    census = gamma_N_factorial_n(FIXTURE, cap_rotations=1_000, keep_accepting=False)
    assert census["status"] == "OK"
    assert census["enumerated_cases"] == 12
    assert census["minimum_defect"] == 0                      # UNHALVED convention
    assert census["defect_histogram"][0] == 2
    assert ws.predicted_census_size(FIXTURE) == 12


def test_witness_probe_hit_is_independently_verified():
    best, orders, anomaly = ws.witness_probe(FIXTURE, 2_000, random.Random(11))
    assert anomaly is None
    assert best == 0
    assert orders is not None
    # re-verify OUTSIDE the probe, straight through gateway_scan
    assert GS.verify_witness(FIXTURE, orders) == 0


def test_witness_probe_never_fabricates_a_hit_on_gamma1():
    # census ground truth: minimum defect 2 (gamma_N = 1), so no defect-0 exists
    census = gamma_N_factorial_n(SPIKED_GAMMA1, cap_rotations=10_000,
                                 keep_accepting=False)
    assert census["status"] == "OK" and census["minimum_defect"] == 2
    best, orders, anomaly = ws.witness_probe(SPIKED_GAMMA1, 3_000, random.Random(7))
    assert anomaly is None
    assert best >= 2                     # an UPPER bound: certifies gamma_N <= best/2
    assert orders is None                # no defect-0 witness, so no hit


def test_spike_children_are_single_spikes():
    children = ws.spike_children(FIXTURE)
    assert len(children) == len(set(children))
    base_reduced = tuple(free_reduce(w) for w in FIXTURE)
    for child in children:
        assert sum(len(w) for w in child) == 9
        assert tuple(free_reduce(w) for w in child) == base_reduced


# --------------------------------------------------------------------------------------
# ladder construction
# --------------------------------------------------------------------------------------


def test_grow_chain_produces_a_census_and_witness_certified_rung():
    rung, stall = ws.grow_chain(FIXTURE, 9, master_seed=1,
                                deadline=time.time() + 120,
                                probe_tiers=(500, 2_000, 8_000),
                                census_cap=20_000)
    assert stall is None
    assert rung["total_length"] == 9
    assert rung["certified_by"] == "census+witness"
    assert rung["census"]["zero_systems"] > 0
    assert rung["witness_verified_defect"] == 0
    # the stored witness re-verifies in isolation
    orders = {int(k): v for k, v in rung["witness_orders"].items()}
    assert GS.verify_witness(tuple(rung["words"]), orders) == 0
    # and the rung really is a spike child of the tip
    assert tuple(rung["words"]) in set(ws.spike_children(FIXTURE))


def test_grow_chain_deadline_stall_proves_nothing_and_says_so():
    rung, stall = ws.grow_chain(FIXTURE, 9, master_seed=1,
                                deadline=time.time() - 1.0,
                                probe_tiers=(500,), census_cap=1_000)
    assert rung is None
    assert stall["reason"] == "deadline"


def test_even_seed_is_a_length10_census_certified_graft_image():
    rung, scan = ws.select_even_seed(master_seed=5, census_cap=100_000,
                                     deadline=time.time() + 120)
    assert scan["gamma0_images"] > 0
    assert rung is not None
    assert rung["total_length"] == 10
    assert rung["certified_by"] == "census+witness"
    assert rung["census"]["zero_systems"] > 0
    orders = {int(k): v for k, v in rung["witness_orders"].items()}
    assert GS.verify_witness(tuple(rung["words"]), orders) == 0


# --------------------------------------------------------------------------------------
# detection measurement
# --------------------------------------------------------------------------------------


def test_measure_rung_detects_the_fixture_and_accounts_cleanly():
    record = ws.measure_rung(FIXTURE, 7, master_seed=3, seeds_per_cell=5,
                             production_samples=(300,),
                             deadline=time.time() + 120,
                             certified_by="census+witness")
    cell = record["cells"]["300"]
    assert cell["runs"] == 5
    assert cell["hits"] == 5             # 2/12 accepting systems: trivial at 300 evals
    assert cell["rate"] == 1.0
    assert cell["complete"] is True
    assert all(d == 0 for d in cell["run_best_defects"])


def test_measure_rung_rate_is_hits_over_runs_on_a_gamma1_state():
    record = ws.measure_rung(SPIKED_GAMMA1, 9, master_seed=3, seeds_per_cell=3,
                             production_samples=(400,),
                             deadline=time.time() + 120, certified_by="census")
    cell = record["cells"]["400"]
    assert cell["hits"] == 0             # no defect-0 system exists to detect
    assert cell["rate"] == 0.0
    assert all(d >= 2 for d in cell["run_best_defects"])


# --------------------------------------------------------------------------------------
# summary logic
# --------------------------------------------------------------------------------------


def _entry(length, r10, r40, r200):
    return {"words": ["w", "v"], "total_length": length, "certified_by": "witness",
            "cells": {"10000": {"samples": 10_000, "runs": 10, "hits": int(10 * r10),
                                "rate": r10},
                      "40000": {"samples": 40_000, "runs": 10, "hits": int(10 * r40),
                                "rate": r40},
                      "200000": {"samples": 200_000, "runs": 10,
                                 "hits": int(10 * r200), "rate": r200}}}


def test_summarize_finds_the_40k_crossings():
    detection = {"13": _entry(13, 1.0, 1.0, 1.0),
                 "15": _entry(15, 0.2, 0.4, 1.0),
                 "17": _entry(17, 0.0, 0.0, 0.1),
                 "19": _entry(19, 0.0, 0.0, 0.0)}
    summary = ws.summarize(detection, [], (10_000, 40_000, 200_000), 19)
    assert summary["first_length_below_half_at_40k"] == 15
    assert summary["first_length_zero_at_40k"] == 17
    assert [row["total_length"] for row in summary["table"]] == [13, 15, 17, 19]
    rec = summary["recommendation_at_max_length"]
    assert rec["status"] == "VACUOUS_AT_ALL_MEASURED_BUDGETS"
    assert isinstance(rec, dict)


def test_summarize_handles_full_detection_and_scaled_budgets():
    detection = {"13": _entry(13, 1.0, 1.0, 1.0)}
    summary = ws.summarize(detection, [], (10_000, 40_000, 200_000), 13)
    assert summary["first_length_below_half_at_40k"] is None
    assert summary["first_length_zero_at_40k"] is None
    assert summary["recommendation_at_max_length"]["recommended_samples"] == 10_000

    detection = {"24": _entry(24, 0.0, 0.0, 0.3)}
    summary = ws.summarize(detection, [], (10_000, 40_000, 200_000), 24)
    rec = summary["recommendation_at_max_length"]
    assert rec["status"] == "MEASURED"
    assert rec["recommended_samples"] >= 200_000    # scaled up from the 30% rate

    summary = ws.summarize({}, [{"target_length": 20, "reason": "x"}],
                           (10_000, 40_000, 200_000), 24)
    assert summary["recommendation_at_max_length"]["status"] == "NO_CALIBRATION_STATE"


# --------------------------------------------------------------------------------------
# artifact honesty and truncation
# --------------------------------------------------------------------------------------


def test_zero_deadline_yields_truncated_valid_artifact(tmp_path):
    out = tmp_path / "sens.json"
    report = ws.run(out_path=str(out), deadline_seconds=0.0)
    assert report["truncated"] is True
    on_disk = json.loads(out.read_text())
    assert on_disk["record"] == "witness_sensitivity"
    assert on_disk["truncated"] is True
    # the side-of-bound and null-reading statements must be in the artifact itself
    assert "ABOVE" in on_disk["bound_direction"]
    assert "never proves gamma_N > 0" in on_disk["null_reading"]
    assert "selection_bias" in on_disk


def test_tiny_end_to_end_run_measures_certified_rungs(tmp_path):
    out = tmp_path / "sens_tiny.json"
    report = ws.run(out_path=str(out), master_seed=2, seeds_per_cell=3,
                    production_samples=(400,), max_length=10,
                    deadline_seconds=240.0, probe_tiers=(500, 2_000, 8_000),
                    census_cap=20_000, measure_from=9)
    assert report["truncated"] is False
    lengths = sorted(r["total_length"] for r in report["ladder"])
    assert lengths[:2] == [7, 9] and 10 in lengths
    for rung in report["ladder"]:
        orders = {int(k): v for k, v in rung["witness_orders"].items()}
        assert GS.verify_witness(tuple(rung["words"]), orders) == 0
    assert "9" in report["detection"] and "10" in report["detection"]
    for entry in report["detection"].values():
        for cell in entry["cells"].values():
            assert cell["hits"] <= cell["runs"]
            assert cell["rate"] == cell["hits"] / cell["runs"]
    assert report["summary"] is not None
    assert not report["anomalies"]
    on_disk = json.loads(out.read_text())
    assert on_disk["summary"]["table"]
