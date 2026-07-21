"""run_mitm_aut (T5) harness tests.

Most tests monkeypatch the search seam
(``experiments.stable_ac.cov.run_mitm_aut.aut_multi_search``) with canned
``(dsu, merges, stats, roots_of)`` tuples, so no real Aut-quotient search runs;
run_mitm only ever sees what the stub returns. They pin the load-bearing logic:

  * ``merged`` is decided from the union-find (target in TRIVIAL's component),
    NOT from "some merge happened";
  * a TRIVIAL-connecting merge is replayed through BOTH verifier stacks and a
    failure suppresses all solve language (advisor item 1);
  * resume skips done targets, the filename is a date-less identity, and the
    nodes_per_source guard refuses a big budget locally.

Plus ONE real end-to-end micro-run: a tiny trivial-group presentation whose
Aut-class merges with TRIVIAL through a real non-empty ACA path, asserting
merged and verify_ok both true.
"""

import json
import os
import re

import pytest

import experiments.stable_ac.cov.run_mitm_aut as R


# --------------------------------------------------------------------------
# stub scaffolding
# --------------------------------------------------------------------------
class _FakeDSU:
    """find(0)==find(1) iff the two sources are merged."""

    def __init__(self, merged):
        self._merged = merged

    def find(self, i):
        return 0 if self._merged else i


def _stats(states=5, capped=False, timed_out=False, components=1):
    return {"popped": 3, "states": states, "capped": capped,
            "timed_out": timed_out, "seconds": 0.0, "components": components}


# ('xy', 'y') and ('x', 'y') both have Aut-canonical rep ('Y', 'X'); an aut merge
# claiming that rep with empty paths verifies against BOTH replay stacks.
_REP = ("Y", "X")
_ROOTS = {0: (None, _REP, None), 1: (None, _REP, None)}


def _fake_search(merged, merges, stats=None, roots_of=None):
    def fake(sources, **kw):
        return (_FakeDSU(merged), merges, stats or _stats(),
                roots_of if roots_of is not None else _ROOTS)
    return fake


def _row(out_path):
    with open(out_path) as f:
        rows = [json.loads(ln) for ln in f if ln.strip()]
    assert len(rows) == 1
    return rows[0]


# --------------------------------------------------------------------------
# merged means TRIVIAL's component, not "any merge happened"
# --------------------------------------------------------------------------
def test_merged_keys_off_dsu_not_merge_count(tmp_path, monkeypatch):
    """A non-empty merges list with a dsu that keeps the two sources apart must
    NOT report merged — merged is read from the union-find."""
    bogus = [{"kind": "aca", "a": "P", "b": "Q", "at": ["Y", "X"],
              "path_a": [], "path_b": []}]
    monkeypatch.setattr(R, "aut_multi_search", _fake_search(False, bogus))
    out = R.run_mitm([("T", "xy", "y")], 12, 100, out_dir=str(tmp_path))
    row = _row(out)
    assert row["merged"] is False
    assert row["verify_ok"] is None
    assert "merge" not in row
    assert row["n_merges"] == 1          # a merge existed; it just isn't T<->TRIVIAL


def test_merged_true_stores_and_verifies_the_merge(tmp_path, monkeypatch):
    merge = {"kind": "aut", "a": "EASY", "b": "TRIVIAL", "at": ["Y", "X"],
             "path_a": [], "path_b": []}
    monkeypatch.setattr(R, "aut_multi_search", _fake_search(True, [merge]))
    out = R.run_mitm([("EASY", "xy", "y")], 12, 100, out_dir=str(tmp_path))
    row = _row(out)
    assert row["merged"] is True
    assert row["verify_ok"] is True
    assert row["merge"]["kind"] == "aut"
    assert row["n_merges"] == 1


def test_row_carries_the_full_schema(tmp_path, monkeypatch):
    merge = {"kind": "aut", "a": "EASY", "b": "TRIVIAL", "at": ["Y", "X"],
             "path_a": [], "path_b": []}
    monkeypatch.setattr(R, "aut_multi_search",
                        _fake_search(True, [merge], stats=_stats(states=9)))
    out = R.run_mitm([("EASY", "xy", "y")], 26, 1000, out_dir=str(tmp_path))
    row = _row(out)
    base = {"name", "r1", "r2", "ceiling", "nodes_per_source", "merged",
            "n_merges", "states", "popped", "capped", "timed_out",
            "components", "seconds", "verify_ok", "git_commit", "wall_seconds"}
    assert base <= set(row), base - set(row)
    assert (row["ceiling"], row["nodes_per_source"]) == (26, 1000)
    assert row["states"] == 9
    assert row["git_commit"] is None or (
        len(row["git_commit"]) == 40
        and all(c in "0123456789abcdef" for c in row["git_commit"]))


# --------------------------------------------------------------------------
# verification gate: an unverified merge is never announced as a solve
# --------------------------------------------------------------------------
def test_unverified_merge_suppresses_solve_language(tmp_path, monkeypatch, capsys):
    """A merge claiming a meeting class its (empty) paths do not reach must fail
    BOTH replay stacks -> verify_ok False, and no solve language is printed."""
    merge = {"kind": "aut", "a": "EASY", "b": "TRIVIAL", "at": ["x", "x"],
             "path_a": [], "path_b": []}
    monkeypatch.setattr(R, "aut_multi_search", _fake_search(True, [merge]))
    out = R.run_mitm([("EASY", "xy", "y")], 12, 100, out_dir=str(tmp_path))
    row = _row(out)
    assert row["merged"] is True
    assert row["verify_ok"] is False
    text = capsys.readouterr().out
    assert "stable-AC-trivial" not in text
    assert "VERIFIED" not in text or "UNVERIFIED" in text
    assert "UNVERIFIED" in text


def test_dsu_merge_without_naming_evidence_is_unverifiable(tmp_path, monkeypatch):
    """merged True from dsu but no merge names {target, TRIVIAL} -> not verifiable,
    so verify_ok is False (never silently True)."""
    unrelated = [{"kind": "aca", "a": "P", "b": "Q", "at": ["Y", "X"],
                  "path_a": [], "path_b": []}]
    monkeypatch.setattr(R, "aut_multi_search", _fake_search(True, unrelated))
    out = R.run_mitm([("EASY", "xy", "y")], 12, 100, out_dir=str(tmp_path))
    row = _row(out)
    assert row["merged"] is True
    assert row["verify_ok"] is False
    assert row["merge"] is None


# --------------------------------------------------------------------------
# resume
# --------------------------------------------------------------------------
def test_resume_skips_done_targets(tmp_path, monkeypatch):
    merge = {"kind": "aut", "a": "EASY", "b": "TRIVIAL", "at": ["Y", "X"],
             "path_a": [], "path_b": []}
    calls = []

    def fake(sources, **kw):
        calls.append(sources[0][0])
        return _FakeDSU(True), [merge], _stats(), _ROOTS

    monkeypatch.setattr(R, "aut_multi_search", fake)
    targets = [("EASY", "xy", "y")]
    out1 = R.run_mitm(targets, 12, 100, out_dir=str(tmp_path))
    out2 = R.run_mitm(targets, 12, 100, out_dir=str(tmp_path))
    assert out1 == out2, "must resume into the same file"
    assert calls == ["EASY"], "the second run must search nothing"
    with open(out1) as f:
        assert sum(1 for ln in f if ln.strip()) == 1


def test_torn_final_line_is_repaired_before_append(tmp_path, monkeypatch):
    merge = {"kind": "aut", "a": "EASY", "b": "TRIVIAL", "at": ["Y", "X"],
             "path_a": [], "path_b": []}
    monkeypatch.setattr(R, "aut_multi_search", _fake_search(True, [merge]))
    out = R.run_mitm([("EASY", "xy", "y")], 12, 100, out_dir=str(tmp_path))
    with open(out) as f:
        line = f.readline()
    with open(out, "w") as f:            # crash mid-write: half a row, no newline
        f.write(line.strip()[: len(line) // 2])
    R.run_mitm([("EASY", "xy", "y")], 12, 100, out_dir=str(tmp_path))
    row = _row(out)                       # raises if the torn line was left in place
    assert row["name"] == "EASY"


# --------------------------------------------------------------------------
# filename identity
# --------------------------------------------------------------------------
def test_filename_is_identity_without_a_date():
    assert R._run_filename(26, 1000) == "mitm_aut_ceil26_nps1000.jsonl"
    assert R._run_filename(28, 1000) != R._run_filename(26, 1000)
    assert R._run_filename(26, 500) != R._run_filename(26, 1000)
    assert not re.search(r"\d\d_\d\d_\d\d", R._run_filename(26, 1000))


# --------------------------------------------------------------------------
# nodes_per_source guard
# --------------------------------------------------------------------------
def test_nps_guard(monkeypatch):
    monkeypatch.delenv("ACSOLVERX_ALLOW_BIG", raising=False)
    R._require_nps_allowed(1000)                 # must not raise
    with pytest.raises(SystemExit):
        R._require_nps_allowed(1001)
    monkeypatch.setenv("ACSOLVERX_ALLOW_BIG", "1")
    R._require_nps_allowed(5000)                  # confirmed production run


def test_run_mitm_refuses_a_big_nps(tmp_path, monkeypatch):
    monkeypatch.delenv("ACSOLVERX_ALLOW_BIG", raising=False)

    def explode(*a, **k):
        raise AssertionError("no search may start under a refused budget")

    monkeypatch.setattr(R, "aut_multi_search", explode)
    with pytest.raises(SystemExit):
        R.run_mitm([("EASY", "xy", "y")], 12, 2000, out_dir=str(tmp_path))


# --------------------------------------------------------------------------
# target loading
# --------------------------------------------------------------------------
def test_load_targets_shortest_prepends_ak3():
    ts = R.load_targets(shortest=5)
    assert ts[0] == R.AK3
    assert len(ts) == 6
    # aca_115 (YXYxyx / YYYYxxx, total length 13) is the shortest aca_124 rep
    assert "aca_115" in {t[0] for t in ts[1:]}


def test_load_targets_by_name_can_drop_ak3():
    ts = R.load_targets(names=["aca_115"], include_ak3=False)
    assert [t[0] for t in ts] == ["aca_115"]
    assert len(ts[0][1]) > 0 and len(ts[0][2]) > 0


# --------------------------------------------------------------------------
# the one real end-to-end micro-run
# --------------------------------------------------------------------------
def test_real_micro_run_merges_and_verifies(tmp_path):
    """No monkeypatch. T2 was found (by trying a few tiny |det|=1 presentations)
    to be a trivial-group presentation whose Aut-class merges with TRIVIAL in a
    handful of pops via a real non-empty ACA path — so this exercises
    replay_path (both stacks) end to end at nps<=200, ceiling 12."""
    T2 = ("T2", "xyxYXY", "xxYYY")
    out = R.run_mitm([T2], ceiling=12, nps=200, out_dir=str(tmp_path))
    row = _row(out)
    assert row["merged"] is True
    assert row["verify_ok"] is True
    assert row["merge"]["kind"] == "aca"
    assert len(row["merge"]["path_a"]) + len(row["merge"]["path_b"]) >= 1
