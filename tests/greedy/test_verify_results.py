"""Tests for the certificate verifier (experiments/stable_ac/verify_results).

Two duties. First, the committed evidence files must verify — that is the
standing proof the pipelines produce genuine solutions. Second, and more
important, the verifier must FAIL on tampered certificates: every tamper test
here is a mutation of a real, passing certificate, so a verifier that stops
checking something goes red here immediately (the suite is its own
mutation audit).

The verifier's independence rule (spec-only replay, never solvern) is what
makes these tests meaningful — see the module docstring there.
"""

import json
import os
import shutil

import pytest

from experiments.greedy_tests.spec.moves import Move
from experiments.stable_ac.verify_results import (
    CertificateError, check_budget_invariance, main, parse_move, verify_file,
)


def _root():
    d = os.path.dirname(os.path.abspath(__file__))
    while not (os.path.isdir(os.path.join(d, "experiments"))
               and os.path.isdir(os.path.join(d, "data"))):
        parent = os.path.dirname(d)
        assert parent != d, "no repo root above the test file"
        d = parent
    return d


ROOT = _root()
NOCOV_DIR = os.path.join(ROOT, "results", "stable_ac", "nocov")
COV_DIR = os.path.join(ROOT, "results", "stable_ac", "cov")
A1_100 = os.path.join(NOCOV_DIR,
                      "nocov_combined_11_A1_100_mrl64_cyc_07_13_26.jsonl")
COV_100 = os.path.join(COV_DIR, "cov_100_11_zf1_mrl24_cyc_s10r1_07_13_26.jsonl")


def _rows(path):
    with open(path) as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def _write(path, rows):
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def _copy_pair(dst_dir):
    """The committed A1@100 evidence (results + paths) copied for tampering."""
    res = os.path.join(dst_dir, os.path.basename(A1_100))
    shutil.copy(A1_100, res)
    shutil.copy(A1_100[:-len(".jsonl")] + "_paths.jsonl",
                res[:-len(".jsonl")] + "_paths.jsonl")
    return res


# -- the committed evidence is the standing positive case ---------------------


def test_committed_nocov_evidence_verifies():
    assert os.path.exists(A1_100), "committed evidence file is gone"
    n_rows, n_solved, failures = verify_file(A1_100)
    assert (n_rows, n_solved, failures) == (176, 26, [])


def test_committed_cov_evidence_verifies():
    assert os.path.exists(COV_100), "committed evidence file is gone"
    n_rows, n_solved, failures = verify_file(COV_100)
    assert (n_rows, n_solved, failures) == (11, 4, [])


def test_main_verifies_everything_committed_including_invariance():
    # exercises the full CLI path: all files, all certificates, and the real
    # cross-budget pairs (A1 100 vs 1000, cov/covbase 100 vs 1000)
    assert main([os.path.join(ROOT, "results", "stable_ac")]) == 0


# -- tampered certificates must FAIL ------------------------------------------


def test_corrupted_move_fails(tmp_path):
    res = _copy_pair(tmp_path)
    ppath = res[:-len(".jsonl")] + "_paths.jsonl"
    prows = _rows(ppath)
    mv = prows[0]["path_moves"][0].split("_")
    mv[3] = str(int(mv[3]) + 1)              # nudge one rotation
    prows[0]["path_moves"][0] = "_".join(mv)
    _write(ppath, prows)
    _, _, failures = verify_file(res)
    assert failures, "a corrupted move verified"


def test_truncated_path_fails(tmp_path):
    res = _copy_pair(tmp_path)
    ppath = res[:-len(".jsonl")] + "_paths.jsonl"
    prows = _rows(ppath)
    prows[0]["path_moves"] = prows[0]["path_moves"][:-1]
    _write(ppath, prows)
    _, _, failures = verify_file(res)
    assert failures                           # path_length mismatch at least
    # even with path_length "fixed" to match, the endpoint is not trivial
    key = (prows[0]["name"], prows[0]["z_word"])
    rrows = _rows(res)
    for r in rrows:
        if (r["name"], r["z_word"]) == key:
            r["path_length"] = len(prows[0]["path_moves"])
    _write(res, rrows)
    _, _, failures = verify_file(res)
    assert any("trivial" in f[2] for f in failures)


def test_missing_paths_row_fails(tmp_path):
    res = _copy_pair(tmp_path)
    ppath = res[:-len(".jsonl")] + "_paths.jsonl"
    _write(ppath, _rows(ppath)[1:])           # drop the first solved job's path
    _, _, failures = verify_file(res)
    assert any("no paths row" in f[2] for f in failures)


def test_fake_solved_flag_fails(tmp_path):
    res = _copy_pair(tmp_path)
    rrows = _rows(res)
    fake = next(r for r in rrows if not r["solved"])
    fake["solved"], fake["path_length"] = True, 7
    _write(res, rrows)
    _, _, failures = verify_file(res)
    assert failures, "an unsolved row flipped to solved verified"


def test_relabelled_z_word_fails(tmp_path):
    # verifier-audit finding: a VALID certificate relabeled under a different
    # z_word (consistently, in both files, z_relator untouched) must not
    # verify -- the certificate must be bound to the row's identity
    res = _copy_pair(tmp_path)
    ppath = res[:-len(".jsonl")] + "_paths.jsonl"
    rrows, prows = _rows(res), _rows(ppath)
    solved = next(r for r in rrows if r["solved"])
    key = (solved["name"], solved["z_word"])
    fake = "XXXXXXX"
    assert fake != solved["z_word"]
    solved["z_word"] = fake
    for p in prows:
        if (p["name"], p["z_word"]) == key:
            p["z_word"] = fake
    _write(res, rrows)
    _write(ppath, prows)
    _, _, failures = verify_file(res)
    assert any("does not encode" in f[2] for f in failures)


def test_malformed_row_fails_cleanly(tmp_path):
    res = _copy_pair(tmp_path)
    rrows = _rows(res)
    solved = next(r for r in rrows if r["solved"])
    del solved["mode"]                        # nocov row masquerading as cov
    _write(res, rrows)
    _, _, failures = verify_file(res)         # must report, not crash
    assert failures


def test_orphan_paths_row_fails(tmp_path):
    res = _copy_pair(tmp_path)
    ppath = res[:-len(".jsonl")] + "_paths.jsonl"
    prows = _rows(ppath)
    orphan = dict(prows[0])
    orphan["z_word"] = "xyxyxyx"              # no solved results row has this
    _write(ppath, prows + [orphan])
    _, _, failures = verify_file(res)
    assert any("without a solved results row" in f[2] for f in failures)


# -- budget invariance ---------------------------------------------------------


def test_budget_invariance_catches_a_lie(tmp_path):
    res = _copy_pair(tmp_path)                # genuine solved rows at budget 100
    rrows = _rows(res)
    solved = next(r for r in rrows if r["solved"])
    liar = dict(solved)                       # same job, bigger budget, "unsolved"
    liar.update(node_budget=1000, solved=False, path_length=None,
                nodes_explored=1000)
    lie_file = str(tmp_path / "nocov_combined_11_A1_1000_mrl64_cyc_lie.jsonl")
    _write(lie_file, [liar])
    assert main([res, lie_file]) == 1

    honest = dict(solved)                     # same stats at the bigger budget
    honest["node_budget"] = 1000
    _write(lie_file, [honest])
    ppath = lie_file[:-len(".jsonl")] + "_paths.jsonl"
    porig = _rows(res[:-len(".jsonl")] + "_paths.jsonl")
    key = (solved["name"], solved["z_word"])
    _write(ppath, [p for p in porig if (p["name"], p["z_word"]) == key])
    assert main([res, lie_file]) == 0


# -- plumbing -------------------------------------------------------------------


def test_move_parser_both_formats():
    assert parse_move("2_1_-1_0_0") == Move(2, 1, -1, 0, 0)
    assert parse_move("2_-1_3_4") == Move(1, 0, -1, 3, 4)   # legacy, 1-based tgt
    assert parse_move("1_1_0_0") == Move(0, 1, 1, 0, 0)
    with pytest.raises(CertificateError):
        parse_move("1_2_3")


def test_torn_trailing_line_tolerated_interior_fails(tmp_path):
    res = _copy_pair(tmp_path)
    with open(res, "a") as f:
        f.write('{"name": "torn')             # crash mid-append: tolerated
    n_rows, n_solved, failures = verify_file(res)
    assert (n_rows, n_solved, failures) == (176, 26, [])

    lines = open(res).read().splitlines()
    lines[3] = '{"name": "torn'               # interior corruption: not tolerated
    with open(res, "w") as f:
        f.write("\n".join(lines) + "\n")
    with pytest.raises(CertificateError):
        verify_file(res)
