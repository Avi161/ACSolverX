"""run.py / acx.runner: every method end to end on a few rows, resume, config errors, record and cap helpers."""
import json
import os

import pytest

from acx import runner

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cfg(name, *overrides):
    return runner.load_config(os.path.join(ROOT, "configs", f"{name}.toml"), list(overrides))


def records(out, name):
    with open(os.path.join(out, name, "paths.jsonl")) as f:
        return [json.loads(line) for line in f]


ALL = ("ac_path", "aut_assisted", "stable_cert")


@pytest.mark.parametrize("name,overrides,kinds", [
    ("smoke", ['rows="0:20"'], {"ac_path"}),
    ("cov", ['rows="0,496,521,609,538"'], {"ac_path", "stable_cert"}),             # bench60 ids
    ("aut", ['rows="0:12"'], {"aut_assisted"}),
    ("hybrid", ['benchmark="ladder60"', 'rows="ac19_11987,ms_000,ac19_54765"'], set(ALL)),
    ("ngen_sac", ['rows="0:12"'], {"stable_cert"})])
def test_methods(tmp_path, name, overrides, kinds):
    s = runner.run(cfg(name, *overrides), str(tmp_path), log=lambda *a: None)
    assert s["solved"] == s["ac_path"] + s["aut_assisted"] + s["stable_cert"] > 0
    assert {k for k in ALL if s[k]} == kinds
    for kind, lengths in s["path_length"].items():
        assert lengths["sub_moves"]["n"] == s[kind]
        if kind != "stable_cert" or name != "cov":           # a CoV transform has no elementary path
            assert lengths["elem_moves"]["sum"] >= lengths["sub_moves"]["sum"]
    assert len(records(tmp_path, s["name"])) == s["rows"]


def test_resume_and_config_guard(tmp_path):
    out = str(tmp_path)
    runner.run(cfg("smoke", 'rows="0:5"'), out, log=lambda *a: None)
    s = runner.run(cfg("smoke", 'rows="0:8"'), out, log=lambda *a: None)
    assert s["rows"] == 8 and len(records(out, "smoke")) == 8          # only rows 5-7 were searched
    with pytest.raises(SystemExit):
        runner.run(cfg("smoke", "search.budget=50"), out, log=lambda *a: None)
    assert runner.run(cfg("smoke", "search.budget=50", 'rows="0:3"'), out, fresh=True, log=print)["rows"] == 3


@pytest.mark.parametrize("name,overrides", [
    ("smoke", ["budget=5"]),                      # belongs under [search]
    ("smoke", ["search.bogus=1"]),
    ("smoke", ["method=beam"]),
    ("smoke", ["hybrid.budget=5"]),               # greedy does not read [hybrid]
    ("hybrid", ["search.cap=5"]),                 # the hybrid's caps are hybrid.r2_cap and hybrid.dyn_cap
    ("rl", ["search.cap=8"]),
    ("rl", ["rl.cap=48"]),                        # wider than the policy's observation
    ("rl", ["rl.beam=4"]),
    ("smoke", ["search.cap=0"]),
    ("hybrid", ["hybrid.r2_cap=true"]),
    ("cov", ["cov.max_len=0"]),
    ("cov", ["cov.cap_headroom=-1"])])
def test_config_errors_raise_at_load(name, overrides):
    """Every bad key or value fails in ``load_config``, before ``run`` writes anything."""
    with pytest.raises(ValueError):
        cfg(name, *overrides)


@pytest.mark.parametrize("name,override,field,value", [
    ("smoke", "search.cap=none", "cap", None),
    ("hybrid", "hybrid.r2_cap=none", "r2_cap", None),
    ("hybrid", "hybrid.r2_cap=24", "r2_cap", 24),
    ("hybrid", "hybrid.dyn_cap=none", "dyn_cap", None),
    ("cov", "cov.max_len=none", "max_len", None),
    ("cov", "cov.cap_headroom=none", "cap_headroom", None)])
def test_uncapped_reaches_every_cap_from_the_cli(name, override, field, value):
    assert getattr(runner.method_config(cfg(name, override)), field) == value


def test_rows_selection():
    rows = list(range(10))
    assert runner.select(rows, "2:8:3") == [2, 5]
    assert runner.select(rows, None) == rows


def test_rl_method(tmp_path):
    pytest.importorskip("torch")
    s = runner.run(cfg("rl", 'rows="0:3"', "rl.width=64", "rl.steps=60"), str(tmp_path), log=lambda *a: None)
    assert s["solved"] == s["ac_path"] == 3


def test_cap_counters_in_records_and_summary(tmp_path):
    """Every record carries the search's cap counters; summary.json sums them under ``caps``."""
    from acx.core.capcount import FIELDS
    s = runner.run(cfg("smoke", 'rows="7,500,620,639"', "search.cap=16", "search.priority=length"), str(tmp_path),
                   log=lambda *a: None)
    recs = records(tmp_path, s["name"])
    assert all(set(FIELDS) <= set(r) and r["cap"] == 16 for r in recs)
    c = s["caps"]["cap"]
    assert c["cap"] == 16 and c["rows"] == 4
    assert c["rows_dropped"] == sum(1 for r in recs if r["cap_dropped"]) >= 3
    assert c["raise_ids"] == [r["id"] for r in recs if r["cap_would_pop"]] and {"620", "639"} <= set(c["raise_ids"])
    assert c["rows_would_pop"] == len(c["raise_ids"]) and c["needed_min"] == 17
    assert c["would_pop"] == sum(r["cap_would_pop"] for r in recs)
    free = runner.run(cfg("smoke", 'rows="620"', "search.cap=none"), str(tmp_path / "free"), log=lambda *a: None)
    assert free["caps"]["cap"]["dropped"] == 0 and free["caps"]["cap"]["cap"] is None


def quiet(c, out, **kw):
    return runner.run(c, str(out), log=lambda *a: None, **kw)


@pytest.mark.parametrize("cut", [50, 1])
def test_resume_survives_a_truncated_last_line(tmp_path, cut):
    """An interrupted run leaves half a record (or one without its newline): resume drops it, redoes that row and
    keeps the file clean."""
    quiet(cfg("smoke", 'rows="0:3"'), tmp_path)
    f = tmp_path / "smoke" / "paths.jsonl"
    f.write_bytes(f.read_bytes()[:-cut])
    s = quiet(cfg("smoke", 'rows="0:5"'), tmp_path)
    recs = records(tmp_path, "smoke")
    assert [r["id"] for r in recs] == ["0", "1", "2", "3", "4"] and s["rows"] == 5


def test_rows_with_repeated_ids_run_once(tmp_path):
    rows = [type("R", (), {"id": str(i)})() for i in range(4)]
    assert [r.id for r in runner.select(rows, "1,1,2,1")] == ["1", "2"]
    s = quiet(cfg("smoke", 'rows="1,1,2"'), tmp_path)
    assert s["rows"] == 2 and [r["id"] for r in records(tmp_path, "smoke")] == ["1", "2"]


def test_summary_covers_every_record_of_the_run(tmp_path):
    """A re-check of fewer rows must not shrink summary.json below what paths.jsonl holds."""
    quiet(cfg("smoke", 'rows="0:6"'), tmp_path)
    quiet(cfg("smoke", 'rows="0:2"'), tmp_path)
    with open(tmp_path / "smoke" / "summary.json") as f:
        assert json.load(f)["rows"] == len(records(tmp_path, "smoke")) == 6


def test_ngen_sac_needs_the_length_priority_at_load():
    with pytest.raises(ValueError, match="length"):
        cfg("ngen_sac", "search.priority=s20_mk2")
    free = runner.method_config(cfg("ngen_sac", "ngen.sac=false", "search.priority=s20_mk2"))
    assert free.search.priority == "s20_mk2"


def test_rows_with_det_not_one_are_recorded_as_errors(tmp_path):
    """No search can solve them: an unsolved record with an ``error``, counted in the summary, no exception."""
    csv = tmp_path / "rows.csv"
    csv.write_text("r1,r2\nX,x\nY,XyYx\nxxY,Yx\n")           # det 0, an empty relator, a good row
    s = quiet(cfg("smoke", f'benchmark="{csv}"', "rows=", "name=bad"), tmp_path)
    recs = {r["id"]: r for r in records(tmp_path, "bad")}
    assert [bool(recs[i].get("error")) for i in "012"] == [True, True, False] and not recs["0"]["solved"]
    assert s["errors"] == 2 and s["rows"] == 3


def test_aut_row_that_is_its_own_representative_stores_the_decoded_path(tmp_path):
    """Not ``aut_assisted``: the elementary path is the decoded S-move path, not the long transported one."""
    from acx import data
    from acx.core.moves import decode_path
    from acx.verify.decode import decode_and_replay
    quiet(cfg("aut", 'benchmark="ms640"', 'rows="7,177"', "name=autself"), tmp_path)
    by_id = {r.id: r.pres for r in data.rows("ms640")}
    for r in records(tmp_path, "autself"):
        assert not r["aut_assisted"]
        want = decode_and_replay(by_id[r["id"]].reduced(False), decode_path(r["path"]))[0]
        assert r["elem_moves"] == len(r["elementary"]) == len(want) < 58 + 1 and len(want) in (13, 47)


def test_cov_with_free_reduction_replays_its_images(tmp_path):
    """Images whose normal form is unstable under free reduction (bench60 ids 579, 380) used to hit ReplayError."""
    s = quiet(cfg("cov", 'rows="579,380"', "search.cyclic=false", "search.budget=300", "name=covlin"), tmp_path)
    assert s["rows"] == 2 and s["errors"] == 0


def test_every_method_but_rankn_has_a_solver():
    from acx.runner.config import METHODS
    from acx.runner.methods import SOLVERS
    assert set(SOLVERS) == set(METHODS) - {"rankn"}


def test_record_has_the_common_fields_first_then_the_extras():
    from acx.runner.methods import record
    rec = record(False, cost=3, rank=2)
    assert list(rec) == ["solved", "kind", "aut_assisted", "cost", "sub_moves", "elem_moves", "path", "elementary",
                         "rank"]
    assert rec["path"] is None and rec["elementary"] is None and rec["cost"] == 3


def test_record_caps_copies_only_the_counters_a_search_kept():
    from acx.core.capcount import blank
    from acx.runner.caps import record_caps
    assert record_caps(None) == {} and record_caps({"pops": 5}) == {}
    stats = {**blank("dyn_cap"), "cap_legs_bound": 2, "pops": 5}
    assert set(record_caps(stats)) == set(blank("dyn_cap")) | {"cap_legs_bound"}
