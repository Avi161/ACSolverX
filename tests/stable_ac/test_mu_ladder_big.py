"""Harness tests for the chunked, provenance-complete mu-ladder
(``experiments/stable_ac/cov/mu_ladder_big.py`` + its verifier).

The load-bearing pin is ``test_climb_matches_mu_ladder``: with both budgets
unlimited, ``climb_one_big`` must reproduce ``mu_ladder.climb_one``'s row
bit-for-bit on every shared field — the scaled pipeline is the SAME nb2
semantics, only chunked, budgeted and provenance-complete. Zero search nodes
anywhere (pure enumeration + Whitehead canonicalisation), so no node-budget
rules apply here.
"""

import json
import os

import pytest

from experiments.stable_ac.cov import mu_ladder_big as big
from experiments.stable_ac.cov.mu_descent_scan import hop_outputs
from experiments.stable_ac.cov.mu_ladder import climb_one
from experiments.stable_ac.cov.verify_mu_ladder import (
    verify_class,
    verify_files,
)

# aca_115 (= AK(3)'s class, mu_in 13) and aca_1's rep: small pairs, small
# CoV fan-out, so real climbs stay sub-second.
P115 = ("YXYxyx", "YYYYxxx")
P1 = ("YYXXyxx", "YYYxyXyX")

UNLIMITED = dict(rungs=2, beam=3, cap=24, stop_mu=0,
                 time_per_class_s=0, max_orbits=0)


def _task(pres_id, pair, **over):
    return {"pres_id": pres_id, "r1": pair[0], "r2": pair[1],
            **UNLIMITED, **over}


def _roundtrip(row, orbits):
    return (json.loads(json.dumps(row)),
            [json.loads(json.dumps(o)) for o in orbits])


# --------------------------------------------------------------------------
# partition + identity

def test_stride_partition_is_equal_and_covers():
    rows = list(range(124))
    slices = [big._chunk_rows(rows, 5, i) for i in range(1, 6)]
    assert sorted(len(s) for s in slices) == [24, 25, 25, 25, 25]
    assert sorted(x for s in slices for x in s) == rows
    assert big._chunk_rows(rows, 5, 1) == rows[0::5]   # stride, not blocks


def test_filename_identity_encodes_result_knobs():
    c = dict(big.DEFAULTS)
    base = big._run_prefix(c, 124)
    assert base == "mu_ladder_big_aca124_n124_r256_b64_s12_t14400_o150000"
    for knob in ("rungs", "beam", "stop_mu", "time_per_class_s",
                 "max_orbits"):
        assert big._run_prefix({**c, knob: 7}, 124) != base, knob
    # cap is result-inert in the ladder path (nothing reads CoVResult.cap),
    # so it must stay OUT of the identity
    assert big._run_prefix({**c, "cap": 30}, 124) == base
    root = "/r"
    sp, op = big._chunk_paths(c, 124, root, 2)
    assert sp.endswith(base + "_c2of5.jsonl")
    assert op.endswith(base + "_c2of5_orbits.jsonl")
    ms, mo = big._merged_paths(c, 124, root)
    assert ms.endswith(base + ".jsonl") and mo.endswith(base + "_orbits.jsonl")
    assert big._CHUNK_MARK.search(os.path.basename(sp))
    assert not big._CHUNK_MARK.search(os.path.basename(ms))


def test_stop_mu_default_is_12_not_13():
    # lesson: stop-threshold-at-the-boundary-skips-the-boundary-case —
    # mu=13 starters (aca_115) must climb, not stop at rung 0
    assert big.DEFAULTS["stop_mu"] == 12


# --------------------------------------------------------------------------
# hop + climb parity with nb2

def test_hop_outputs_full_matches_hop_outputs():
    for pair in (P115, P1):
        full = big.hop_outputs_full(*pair, 24, memo={})
        base = hop_outputs(*pair, 24)
        assert set(full) == set(base)
        for rep in base:
            assert full[rep][:3] == base[rep]
        for rep, (_, _, _, iso_gen, iso_index, n_subs) in full.items():
            assert iso_gen in ("x", "y") and iso_index in (0, 1)
            assert n_subs >= 1


def test_climb_matches_mu_ladder():
    for pid, pair in (("aca_115", P115), ("aca_1", P1)):
        row, orbits = big.climb_one_big(_task(pid, pair))
        ref = climb_one((pid, pair[0], pair[1], UNLIMITED["rungs"],
                         UNLIMITED["beam"], UNLIMITED["cap"],
                         UNLIMITED["stop_mu"]))
        for k in ref:
            assert row[k] == ref[k], (pid, k)
        assert not row["timed_out"] and not row["orbit_capped"]
        assert len(orbits) == row["n_orbits_seen"]


def test_boundary_class_actually_climbs_at_default_stop_mu():
    row, _ = big.climb_one_big(_task("aca_115", P115, stop_mu=12))
    assert not row["hits_stop"]
    assert row["n_orbits_seen"] > 1   # explored, not skipped at rung 0


# --------------------------------------------------------------------------
# provenance

def test_provenance_replays_and_tampering_is_caught():
    row, orbits = _roundtrip(*big.climb_one_big(_task("aca_115", P115,
                                                      rungs=3, beam=4)))
    assert verify_class(row, orbits, level="full") == []
    bad = [dict(o) for o in orbits]
    bad[2]["mu"] += 1
    assert verify_class(row, bad, level="full")
    bad = [dict(o) for o in orbits]
    bad[1]["z"] = "xyxy"
    assert verify_class(row, bad, level="replay")
    bad = [dict(o) for o in orbits]
    bad[1]["pair"] = [bad[1]["pair"][1], bad[1]["pair"][0]]
    assert verify_class(row, bad, level="replay")
    assert verify_class({**row, "best_mu": row["best_mu"] - 1}, orbits,
                        level="replay")
    assert verify_class({**row, "n_orbits_seen": 999}, orbits,
                        level="replay")


def test_time_budget_flags_and_still_writes_a_valid_row():
    row, orbits = big.climb_one_big(_task("aca_115", P115,
                                          time_per_class_s=1e-9))
    assert row["timed_out"] and not row["orbit_capped"]
    assert not row["hits_stop"]
    row, orbits = _roundtrip(row, orbits)
    assert verify_class(row, orbits, level="full") == []


def test_max_orbits_flags_and_still_writes_a_valid_row():
    row, orbits = big.climb_one_big(_task("aca_115", P115, rungs=5, beam=4,
                                          max_orbits=3))
    assert row["orbit_capped"]
    row, orbits = _roundtrip(row, orbits)
    assert verify_class(row, orbits, level="full") == []


def test_lead_tag_ak3_tripwire():
    lead = {"pres_id": "aca_115", "hits_stop": True, "best_mu": 12,
            "mu_in": 13, "is_ak3_orbit": False}
    assert "PRESUMED BUG" in big._lead_tag(lead)
    lead2 = {"pres_id": "aca_7", "hits_stop": True, "best_mu": 12,
             "mu_in": 16, "is_ak3_orbit": True}
    assert "PRESUMED BUG" in big._lead_tag(lead2)
    desc = {"pres_id": "aca_7", "hits_stop": False, "best_mu": 15,
            "mu_in": 16}
    assert "DESC 16->15" in big._lead_tag(desc)
    assert big._lead_tag({"pres_id": "aca_7", "hits_stop": False,
                          "best_mu": 16, "mu_in": 16}) == ""


# --------------------------------------------------------------------------
# chunk runner: resume, repair, merge

@pytest.fixture
def tiny_setup(tmp_path):
    csv_path = tmp_path / "tiny.csv"
    csv_path.write_text("name,r1,r2\n"
                        f"t_a,{P115[0]},{P115[1]}\n"
                        f"t_b,{P1[0]},{P1[1]}\n")
    out_dir = tmp_path / "out"
    return dict(big.DEFAULTS, data=str(csv_path), out_dir=str(out_dir),
                rungs=1, beam=2, stop_mu=0, time_per_class_s=0,
                max_orbits=0, chunks=2, use_chunks=True)


def test_chunk_resume_skips_done_and_repairs_orphans(tiny_setup):
    c = tiny_setup
    sp, op = big.run_chunk(c, 1)          # slice = [t_a]
    first = open(sp).read()
    assert json.loads(first)["pres_id"] == "t_a"
    orig_orbits = open(op).read()
    # crash artifacts: a torn summary tail + orbit rows of an uncommitted class
    with open(sp, "a") as f:
        f.write('{"pres_id": "torn')
    with open(op, "a") as f:
        f.write(json.dumps({"pres_id": "t_crashed", "rung": 0}) + "\n")
    sp2, op2 = big.run_chunk(c, 1)
    assert (sp2, op2) == (sp, op)
    assert open(sp).read() == first       # repaired AND t_a not re-run
    assert open(op).read() == orig_orbits  # orphan rows dropped
    hb = json.load(open(sp + ".hb"))
    assert hb["done"] == 1 and hb["total"] == 1


def test_merge_refuses_incomplete_then_merges(tiny_setup):
    c = tiny_setup
    kw = {k: c[k] for k in ("data", "out_dir", "rungs", "beam", "stop_mu",
                            "time_per_class_s", "max_orbits", "chunks")}
    big.run_chunk(c, 1)
    with pytest.raises(RuntimeError, match="incomplete"):
        big.merge_chunks(**kw)
    big.run_chunk(c, 2)
    ms, mo = big.merge_chunks(**kw)
    rows = [json.loads(ln) for ln in open(ms)]
    assert [r["pres_id"] for r in rows] == ["t_a", "t_b"]   # CSV order
    n, errs = verify_files(ms, level="full")
    assert (n, errs) == (2, [])
    with pytest.raises(RuntimeError, match="target exists"):
        big.merge_chunks(**kw)


def test_merge_refuses_orbit_row_mismatch(tiny_setup):
    c = tiny_setup
    kw = {k: c[k] for k in ("data", "out_dir", "rungs", "beam", "stop_mu",
                            "time_per_class_s", "max_orbits", "chunks")}
    big.run_chunk(c, 1)
    big.run_chunk(c, 2)
    _, op = big._chunk_paths(c, 2, "/", 1)
    op = os.path.join(c["out_dir"],
                      os.path.basename(op))
    with open(op, "a") as f:     # an extra orbit row the summary never saw
        f.write(json.dumps({"pres_id": "t_a", "rung": 9}) + "\n")
    with pytest.raises(RuntimeError, match="orbit rows"):
        big.merge_chunks(**kw)


def test_heartbeat_beat_carries_instantaneous_rate(tmp_path):
    # the mandatory heartbeat rule: the 60s beat shows an instantaneous rate
    # (orbits/s here), and a frozen sidecar shows its age, never silence
    import time as _t
    sp = str(tmp_path / "mu_ladder_big_x_c1of2.jsonl")
    open(sp, "w").close()
    hb = big._LadderHeartbeat([sp], total=2, now=0.0)
    now_wall = _t.time()
    json.dump({"pres_id": "t_a", "mu_in": 16, "rung": 1, "n_orbits": 100,
               "best_mu": 16, "done": 0, "total": 2, "ts": now_wall - 60},
              open(sp + ".hb", "w"))
    first = hb.maybe_beat(now=61.0)
    assert first and "orb/s n/a" in first          # first sample of the class
    json.dump({"pres_id": "t_a", "mu_in": 16, "rung": 3, "n_orbits": 700,
               "best_mu": 15, "done": 0, "total": 2, "ts": now_wall},
              open(sp + ".hb", "w"))
    second = hb.maybe_beat(now=122.0)
    assert second and "10.0 orb/s" in second       # (700-100)/60s
    third = hb.maybe_beat(now=183.0)               # sidecar frozen
    assert third and "no update for" in third


def test_high_speedup_toggle_is_result_neutral(tiny_setup, tmp_path):
    # HIGH_SPEEDUP off => pure-Python aut_canon, byte-identical rows in a
    # file with the SAME identity (result-neutral knobs stay out of the name)
    c_fast = dict(tiny_setup, out_dir=str(tmp_path / "fast"))
    c_slow = dict(tiny_setup, out_dir=str(tmp_path / "slow"),
                  high_speedup=False)
    try:
        sp_f, op_f = big.run_chunk(c_fast, 1)
        assert big.FAST_CANON is True
        sp_s, op_s = big.run_chunk(c_slow, 1)
        assert big.FAST_CANON is False
    finally:
        big._apply_high_speedup({})            # restore the module default
    assert os.path.basename(sp_f) == os.path.basename(sp_s)
    strip = ("elapsed_s", "git_commit")
    rows_f = [json.loads(ln) for ln in open(sp_f)]
    rows_s = [json.loads(ln) for ln in open(sp_s)]
    assert [{k: v for k, v in r.items() if k not in strip} for r in rows_f] \
        == [{k: v for k, v in r.items() if k not in strip} for r in rows_s]
    assert open(op_f).read() == open(op_s).read()


def test_end_to_end_spawned_chunks_then_merge_and_verify(tiny_setup):
    c = tiny_setup
    kw = {k: c[k] for k in ("data", "out_dir", "rungs", "beam", "stop_mu",
                            "time_per_class_s", "max_orbits", "chunks")}
    paths = big.run(**kw, chunk_index=None)
    assert len(paths) == 2
    for sp, op in paths:
        assert os.path.exists(sp) and os.path.exists(op)
    ms, _ = big.merge_chunks(**kw)
    n, errs = verify_files(ms, level="full")
    assert (n, errs) == (2, [])
