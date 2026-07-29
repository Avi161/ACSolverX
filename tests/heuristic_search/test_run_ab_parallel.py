"""The multi-worker path of ``run_ab`` claims to be result-neutral: same rows as a serial
run (order in the file aside), same resume contract, same file identity. These tests pin
that, plus the four operational guarantees the Colab campaign leans on — heartbeats reach
the parent from workers (a pool worker cannot print in a notebook), a flock-claimed stage
refuses a second run (an interrupted cell's orphans must not double-compute), Drive mode
never appends to the mount (local stage + whole-file mirror), and a fresh VM seeds its
stage back from the mirror.

Budgets stay at the repo ceiling. One structural note: the heartbeat test uses the hsolve
engine deliberately — hcompact calls ``progress`` only every ``_HB_CHECK_EVERY = 1024``
pops, which no budget-legal test can reach (see
``experiments/lessons/budget-capped-tests-miss-structural-thresholds.md``); the queue
plumbing under test is engine-independent.
"""
import fcntl
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.abspath(__file__))
while ROOT != os.path.dirname(ROOT) and not all(
        os.path.isdir(os.path.join(ROOT, _s)) for _s in ("experiments", "data")):
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, ROOT)

import experiments.heuristic_search.runners.run_ab as ra                     # noqa: E402


def _rows(path):
    out = {}
    for line in open(path):
        r = json.loads(line)
        r.pop("secs")
        out[(r["arm"], r["name"])] = r
    return out


def _cfg(**kw):
    cfg = dict(DATASET="bench66", SUBSET=8, ARMS=["recommended"], NODE_BUDGET=500,
               CHECKPOINTS=[500], MAX_RELATOR_LENGTH=48, RESUME=True,
               OUT_STEM="t", ENGINE="hcompact")
    cfg.update(kw)
    return cfg


FNAME = "t_bench66_b500_mrl48.jsonl"


def test_parallel_rows_identical_to_serial_and_resume_across_modes(tmp_path, capsys):
    ra.run_ab(_cfg(N_WORKERS=1), out_dir=str(tmp_path / "ser"), progress_secs=10**6)
    ra.run_ab(_cfg(N_WORKERS=4), out_dir=str(tmp_path / "par"), progress_secs=10**6)
    a = _rows(tmp_path / "ser" / FNAME)
    b = _rows(tmp_path / "par" / FNAME)
    assert a == b
    assert any(r["solved"] and r["path_moves"] for r in a.values()), \
        "no solved row carried a certificate -- recovery went unexercised"

    # A file written serially resumes under the pool, finishing only the missing rows.
    d = tmp_path / "resume"
    d.mkdir()
    lines = open(tmp_path / "ser" / FNAME).readlines()
    (d / FNAME).write_text("".join(lines[:5]))
    capsys.readouterr()
    ra.run_ab(_cfg(N_WORKERS=4), out_dir=str(d), progress_secs=10**6)
    assert "5 rows resumed; 3 to run" in capsys.readouterr().out
    assert _rows(d / FNAME) == a


def test_worker_heartbeats_reach_the_parent(tmp_path, capsys):
    cfg = _cfg(DATASET="unsolved124", SUBSET=2, NODE_BUDGET=1000, CHECKPOINTS=[1000],
               ENGINE="hsolve", N_WORKERS=2, OUT_STEM="hb")
    ra.run_ab(cfg, out_dir=str(tmp_path), heartbeat_secs=0.05, progress_secs=10**6)
    out = capsys.readouterr().out
    assert any("nodes/s" in l and "[recommended/" in l for l in out.splitlines())


def test_flock_claimed_stage_refuses_a_second_run(tmp_path):
    out = tmp_path / FNAME
    fd = os.open(str(out) + ".lock", os.O_CREAT | os.O_RDWR)
    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        with pytest.raises(RuntimeError, match="flock-claimed"):
            ra.run_ab(_cfg(N_WORKERS=2), out_dir=str(tmp_path), progress_secs=10**6)
    finally:
        os.close(fd)


def test_drive_mode_stages_mirrors_and_seeds_back(tmp_path, monkeypatch, capsys):
    fake_drive = tmp_path / "drive" / "MyDrive" / "hsearch"
    monkeypatch.setattr(ra, "_REMOTE_PREFIX", str(tmp_path / "drive"))
    cfg = _cfg(N_WORKERS=3, STAGE_DIR=str(tmp_path / "stage1"))
    ra.run_ab(cfg, out_dir=str(fake_drive), progress_secs=10**6)
    assert _rows(fake_drive / FNAME) == _rows(tmp_path / "stage1" / FNAME)

    # "Fresh VM": a new, empty stage dir. The mirror must seed it and resume everything.
    cfg["STAGE_DIR"] = str(tmp_path / "stage2")
    capsys.readouterr()
    ra.run_ab(cfg, out_dir=str(fake_drive), progress_secs=10**6)
    assert "8 rows resumed; 0 to run" in capsys.readouterr().out
