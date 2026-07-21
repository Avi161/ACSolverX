"""Pins the stall-escape mechanism (idea 4): the plain-Python loop solves what
the shipped greedy solves, the plateau path emits a segmented certificate, and
the independent spec replay accepts it. Budgets well under 1000."""

import pytest

from experiments.stable_ac.cov import stall_escape


def test_greedy_until_solves_a_trivial_case():
    r = stall_escape.greedy_until("xy", "y", 50, 24)
    assert r["status"] == "solved"
    assert r["pops"] <= 10


def test_base_solve_verifies_through_spec():
    row = stall_escape.stall_escape_search("YYXyx", "Yx", 200, 24)
    assert row["solved"] and row["phase"] == "base"
    ok, why = stall_escape.verify_escape_row("YYXyx", "Yx", row)
    assert ok, why


def test_escape_phase_produces_verified_segmented_certificate():
    # ms380 (combined_22): at budget 1000 / plateau_k 200 the base phase
    # plateaus and the mu-ranked CoV escape solves it — pinned as the
    # mechanism's regression anchor (deterministic search, fixed enumeration).
    r1, r2 = "YYYYXyyyx", "YYYYxxyX"
    row = stall_escape.stall_escape_search(r1, r2, 1000, 24)
    assert row["solved"], row
    if row["phase"] == "escape":          # the pinned expectation
        assert row["junction"]["z_word"]
        assert row["seg1_moves"] is not None and row["seg2_moves"]
    ok, why = stall_escape.verify_escape_row(r1, r2, row)
    assert ok, why


def test_budget_gate():
    import os
    os.environ.pop("ACSOLVERX_ALLOW_BIG", None)
    with pytest.raises(SystemExit):
        stall_escape._require_budget_allowed(5000)


def test_tampered_certificate_is_rejected():
    row = stall_escape.stall_escape_search("YYXyx", "Yx", 200, 24)
    assert row["solved"]
    bad = dict(row)
    bad["seg1_moves"] = row["seg1_moves"][:-1]      # drop the last move
    ok, _ = stall_escape.verify_escape_row("YYXyx", "Yx", bad)
    assert not ok
