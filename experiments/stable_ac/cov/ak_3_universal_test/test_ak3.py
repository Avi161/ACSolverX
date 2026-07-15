"""Colocated checks for the AK(3) universal-CoV experiment.

The 390 sweep rows are all UNSOLVED, so the sweep alone never exercised the
solved branch of ``sweep._search`` (fast solve → slow re-solve for the path).
``test_solved_branch`` covers it on a presentation the difficulty bins show
solving in single-digit nodes. The certificate tests re-verify both shipped
JSONs from disk — they are the experiment's actual claims.

Run from the repo root:
    PYTHONHASHSEED=0 .venv/bin/python3 -m pytest \
        experiments/stable_ac/cov/ak_3_universal_test/test_ak3.py -q
"""

import pytest

from experiments.stable_ac.cov.ak_3_universal_test import ball, census
from experiments.stable_ac.cov.ak_3_universal_test import certify
from experiments.stable_ac.cov.ak_3_universal_test import certify_classical
from experiments.stable_ac.cov.ak_3_universal_test import sweep as S

MAX_BUDGET = 1_000   # repo hard rule


def test_budgets_capped():
    assert S.BUDGET <= MAX_BUDGET
    assert ball.POP_CAP <= MAX_BUDGET
    assert certify.POP_CAP <= MAX_BUDGET
    assert certify_classical.POP_CAP <= MAX_BUDGET


def test_canon_key_invariances():
    k = S.canon_key("xyxYXY", "xxxYYYY")
    assert k == S.canon_key("xxxYYYY", "xyxYXY")          # pair order
    assert k == S.canon_key("xYXYxy", "xxxYYYY")          # rotation
    assert k == S.canon_key("yxyXYX", "xxxYYYY")          # inversion


def test_example_c_matches_worked_example():
    assert S.example_c() == ("yXXyXXyXXXXXX", "yXyXYX")


def test_solved_branch_returns_path():
    # difficulty_bins.csv: (XXYxy, XXYYxy) solves in single-digit nodes
    stats = S._search("XXYxy", "XXYYxy", cap=24)
    assert stats["solved"]
    assert stats["path_moves"], "slow re-solve must recover the move path"
    assert stats["nodes_explored"] <= MAX_BUDGET


def test_orbit2_certificate_verifies():
    certify.verify()          # raises SystemExit(1) on failure


def test_classical_certificate_verifies():
    certify_classical.verify()


def test_census_floor_orbit_helper():
    rows = [{"min_total": 13, "min_pair": list(S.AK3)},
            {"min_total": 14, "min_pair": ["xy", "yx"]}]
    orbs = census.floor_orbits(rows, {})
    assert len(orbs) == 1     # the 14-row is ignored, AK3 maps to one orbit


def test_no_row_beat_the_bar():
    rows = S.load_rows()
    assert rows, "sweep_results.jsonl missing"
    assert all(not r["solved"] and r["min_total"] >= 13 for r in rows)
    assert all(r["node_budget"] <= MAX_BUDGET for r in rows)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
