"""run.py / acx.runner: every method end to end on a few rows, the path and fields options, per-row errors, resume,
config errors, record and cap helpers."""
import importlib
import importlib.util
import json
import os
import shutil
import statistics
import time

import pytest
from conftest import ROOT

import run
from acx import runner

HAS_TORCH = importlib.util.find_spec("torch") is not None
needs_torch = pytest.mark.skipif(not HAS_TORCH, reason="the rl method needs PyTorch")


def cfg(name, *overrides):
    return runner.load_config(os.path.join(ROOT, "configs", f"{name}.toml"), list(overrides))


def records(out, name):
    with open(os.path.join(out, name, "paths.jsonl")) as f:
        return [json.loads(line) for line in f]


def by_id(out, name):
    return {r["id"]: r for r in records(out, name)}


def summary_of(out, name):
    with open(os.path.join(out, name, "summary.json")) as f:
        return json.load(f)


ALL = ("ac_path", "aut_assisted", "stable_cert")

# (config, overrides, kinds of its solves): each method on a few rows
METHOD_CASES = [
    ("smoke", ['rows="0:20"'], {"ac_path"}),
    ("cov", ['rows="0,496,521,609,538"'], {"ac_path", "stable_cert"}),             # bench60 ids
    ("aut", ['rows="0:12"'], {"aut_assisted"}),
    ("hybrid", ['benchmark="ladder60"', 'rows="ac19_11987,ms_000,ac19_54765"'], set(ALL)),
    ("ngen_sac", ['benchmark="ms640"', 'rows="0:12"'], {"stable_cert"}),
    pytest.param("rl", ['rows="0:3"', "rl.width=64", "rl.steps=60"], {"ac_path"}, marks=needs_torch)]


@pytest.mark.parametrize("name,overrides,kinds", METHOD_CASES)
def test_methods(tmp_path, name, overrides, kinds):
    from acx.runner.output import RECORD_KEYS
    s = runner.run(cfg(name, *overrides), str(tmp_path), log=lambda *a: None)
    assert s["solved"] == s["ac_path"] + s["aut_assisted"] + s["stable_cert"] > 0
    assert {k for k in ALL if s[k]} == kinds
    for kind, lengths in s["path_length"].items():
        assert lengths["sub_moves"]["n"] == s[kind]
        if kind != "stable_cert" or name != "cov":           # a CoV transform has no elementary path
            assert lengths["elem_moves"]["sum"] >= lengths["sub_moves"]["sum"]
    recs = records(tmp_path, s["name"])
    assert len(recs) == s["rows"]
    assert all(r["verified"] == r["solved"] and r["cpu_seconds"] >= 0 for r in recs)     # every solve is replayed
    assert set().union(*recs) <= RECORD_KEYS                                              # what ``fields`` may name


def test_resume_and_config_guard(tmp_path):
    out = str(tmp_path)
    runner.run(cfg("smoke", 'rows="0:5"'), out, log=lambda *a: None)
    s = runner.run(cfg("smoke", 'rows="0:8"'), out, log=lambda *a: None)
    assert s["rows"] == 8 and len(records(out, "smoke")) == 8          # only rows 5-7 were searched
    for other in ("search.budget=50", "path=false", 'fields=["cost"]'):      # path and fields are part of the config
        with pytest.raises(SystemExit):
            runner.run(cfg("smoke", other), out, log=lambda *a: None)
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
    ("cov", ["cov.cap_headroom=-1"]),
    ("smoke", ["path=1"]),                        # path is true or false
    ("smoke", ['path="no"']),
    ("smoke", ["decode=no"]),                     # decode is true or false
    ("smoke", ["decode=1"]),
    ("smoke", ["workers=two"]),                   # workers is an int >= 1
    ("smoke", ["workers=0"]),
    ("smoke", ["workers=true"]),
    ("smoke", ["workers=1.5"]),
    ("smoke", ['fields="cost"']),                 # fields is a list of record keys ...
    ("smoke", ["fields=[1]"]),
    ("smoke", ['fields=["cots"]']),               # ... that a record can hold
    ("rank3_bf", ["path=false"]),                 # rankn writes its own row files, in its own format
    ("rank3_bf", ['fields=["id"]'])])
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
    """A re-check of fewer rows must not shrink summary.json below what paths.jsonl holds, nor leave a ``rows`` (or
    ``workers``) in its embedded config that says otherwise; the settings stay."""
    quiet(cfg("smoke", 'rows="0:6"'), tmp_path)
    quiet(cfg("smoke", 'rows="0:2"', "workers=2"), tmp_path)
    s = summary_of(tmp_path, "smoke")
    assert s["rows"] == len(records(tmp_path, "smoke")) == 6
    assert "rows" not in s["config"] and "workers" not in s["config"] and s["config"]["search"]["budget"] == 1000


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
    assert not any(r["verified"] for r in recs.values() if r.get("error")) and recs["2"]["verified"]
    assert all(r["cpu_seconds"] >= 0 for r in recs.values())


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
                         "verified", "rank"]
    assert rec["path"] is None and rec["elementary"] is None and rec["cost"] == 3 and rec["verified"] is False


def test_record_caps_copies_only_the_counters_a_search_kept():
    from acx.core.capcount import blank
    from acx.runner.caps import record_caps
    assert record_caps(None) == {} and record_caps({"pops": 5}) == {}
    stats = {**blank("dyn_cap"), "cap_legs_bound": 2, "pops": 5}
    assert set(record_caps(stats)) == set(blank("dyn_cap")) | {"cap_legs_bound"}


# ---- the path option: no certificate, no replay ------------------------------------------------------------------

@pytest.mark.parametrize("name,overrides,kinds", METHOD_CASES)
def test_path_false_is_the_same_search_without_the_certificate(tmp_path, name, overrides, kinds):
    """``path = false`` skips the certificate and its replay, not the search: solves, costs, counters and the S-move
    length are those of ``path = true``. ``path`` and ``elementary`` are null, ``verified`` false and ``steps`` gone;
    the elementary length survives only where the method has it without the path, and is then the true one."""
    quiet(cfg(name, *overrides, "name=full"), tmp_path)
    quiet(cfg(name, *overrides, "name=lite", "path=false"), tmp_path)
    full, lite = by_id(tmp_path, "full"), by_id(tmp_path, "lite")
    assert lite.keys() == full.keys() and any(r["solved"] for r in lite.values())
    for id_, rec in lite.items():
        assert rec["path"] is None and rec["elementary"] is None and rec["verified"] is False
        assert set(full[id_]) - set(rec) <= {"steps"}
        for key, value in rec.items():
            if key == "elem_moves":
                assert value in (None, full[id_][key])
            elif key not in ("path", "elementary", "verified", "seconds", "cpu_seconds"):
                assert value == full[id_][key]
        assert rec["solved"] == (rec["sub_moves"] is not None)


GREEDY_AUT_NGEN = [case[:2] for case in METHOD_CASES if case[0] in ("smoke", "aut", "ngen_sac")]


@pytest.mark.parametrize("name,overrides", GREEDY_AUT_NGEN)
def test_path_false_keeps_sub_moves_and_nulls_elem_moves(tmp_path, name, overrides):
    """Greedy, aut and ngen know the length of a solve without its path (the solved state's depth); the elementary
    length needs the path, so it is null, in the records and in the summary's ``path_length``."""
    s = quiet(cfg(name, *overrides, "path=false"), tmp_path)
    solved = [r for r in records(tmp_path, s["name"]) if r["solved"]]
    assert len(solved) == s["solved"] > 0
    assert all(r["sub_moves"] > 0 and r["elem_moves"] is None for r in solved)
    for kind, lengths in s["path_length"].items():
        assert lengths["sub_moves"]["n"] == s[kind] and lengths["elem_moves"] is None


def test_path_option_sets_each_methods_own_switch():
    """The one top-level ``path`` is the search's ``capture_path``, the hybrid's ``certify`` and ngen's ``lift``."""
    assert runner.method_config(cfg("smoke")).capture_path is True
    assert runner.method_config(cfg("smoke", "path=false")).capture_path is False
    assert runner.method_config(cfg("aut", "path=false")).capture_path is False
    assert runner.method_config(cfg("cov", "path=false")).search.capture_path is False
    assert runner.method_config(cfg("hybrid")).certify is True
    assert runner.method_config(cfg("hybrid", "path=false")).certify is False
    ngen = runner.method_config(cfg("ngen_sac", "path=false"))
    assert (ngen.search.capture_path, ngen.lift) == (False, False)
    assert runner.method_config(cfg("ngen_sac")).lift is True


# (config, overrides, the one check of each method's certificate): the search, CoV, the hybrid's certify and rl
# replay inside; the runner replays only aut's carried-back path and ngen's lift
CHECK_CASES = [
    ("smoke", ['rows="0:2"'], "acx.search.engine.replay"),
    ("aut", ['rows="0:2"'], "acx.runner.methods.replay"),
    ("cov", ['rows="0,496"'], "acx.cov.run.verify"),
    ("hybrid", ['benchmark="ladder60"', 'rows="ac19_11987,ms_000"'], "acx.hybrid.certify.replay"),
    ("ngen_sac", ['rows="0:2"'], "acx.ngen.verify"),
    pytest.param("rl", ['rows="0:2"', "rl.width=64", "rl.steps=60"], "acx.rl.solve.replay", marks=needs_torch)]


@pytest.fixture
def no_warm_up(monkeypatch):
    """Leave out the run's warm-up solve, for tests that count the solves of the rows."""
    from acx.runner import execute
    monkeypatch.setattr(execute, "warm_up", lambda cfg: None)


def module_and_name(check):
    """``"acx.hybrid.certify.replay"`` -> the module ``acx.hybrid.certify`` and ``"replay"``; imported, as a package
    may export a function under its submodule's name (``acx.hybrid.certify``, ``acx.search``)."""
    module, name = check.rsplit(".", 1)
    return importlib.import_module(module), name


@pytest.mark.parametrize("name,overrides,check", CHECK_CASES)
def test_a_certificate_that_fails_its_check_is_an_error_never_a_verified_solve(tmp_path, monkeypatch, name,
                                                                               overrides, check):
    """With ``path = true`` the check stands between a method and its record: when it fails the row is unsolved."""
    from acx.verify import ReplayError

    def fails(*args, **kwargs):
        raise ReplayError("the path does not end trivial")

    monkeypatch.setattr(*module_and_name(check), fails)
    s = quiet(cfg(name, *overrides), tmp_path)
    recs = records(tmp_path, s["name"])
    assert s["solved"] == 0 and s["errors"] >= 1 and not any(r["verified"] for r in recs)
    assert all(r["error"] == "ReplayError: the path does not end trivial" for r in recs if r.get("error"))


def count_calls(monkeypatch, module, name):
    """Wrap ``module.name`` so that every call is counted; the list returned gets one entry per call."""
    real, calls = getattr(module, name), []

    def counted(*args, **kwargs):
        calls.append(name)
        return real(*args, **kwargs)

    monkeypatch.setattr(module, name, counted)
    return calls


@pytest.mark.parametrize("name,overrides,check", CHECK_CASES)
def test_every_solve_is_checked_exactly_once(tmp_path, monkeypatch, no_warm_up, name, overrides, check):
    """With ``path = true`` each solved row passes its method's check once; the runner adds a second replay only
    where it is the one check (aut's carried-back path; ngen's lift is checked by ``acx.ngen.verify``)."""
    from acx.runner import methods
    checks = count_calls(monkeypatch, *module_and_name(check))
    runner_checks = [count_calls(monkeypatch, methods, "replay"),
                     count_calls(monkeypatch, importlib.import_module("acx.cov"), "verify")]   # the runner's own
    s = quiet(cfg(name, *overrides), tmp_path)
    assert s["solved"] > 0 and len(checks) == s["solved"]
    assert sum(map(len, runner_checks)) == (s["solved"] if name == "aut" else 0)


def test_path_false_does_no_replay_and_no_decode(tmp_path, monkeypatch):
    """The speed-up is work skipped: the search is not asked for a path, and nothing replays or decodes one."""
    from acx.runner import methods
    engine = importlib.import_module("acx.search.engine")
    calls = [count_calls(monkeypatch, engine, "replay"), count_calls(monkeypatch, methods, "decode_and_replay")]
    quiet(cfg("smoke", 'rows="0:4"', "name=lite", "path=false"), tmp_path)
    assert not any(calls)
    quiet(cfg("smoke", 'rows="0:4"', "name=full"), tmp_path)
    assert all(calls)


# ---- the fields option --------------------------------------------------------------------------------------------

@pytest.mark.parametrize("name,override,message", [
    ("smoke", "path=1", "path must be true or false"),
    ("smoke", "decode=no", "decode must be true or false, got 'no'"),
    ("smoke", "workers=two", "workers must be an int >= 1, got 'two'"),
    ("smoke", 'fields="cost"', "fields must be a list"),
    ("smoke", 'fields=["cots"]', r"unknown record keys in fields: \['cots'\]"),
    ("smoke", "search.capture_path=false", "search.capture_path follows the top-level path"),    # path drives these
    ("hybrid", "hybrid.certify=false", "hybrid.certify follows the top-level path"),
    ("ngen_sac", "ngen.lift=false", "ngen.lift follows the top-level path"),
    ("rank3_bf", "path=false", "rankn writes its own row files"),
    ("rank3_bf", 'fields=["id"]', "rankn writes its own row files")])
def test_path_and_fields_errors_say_what_is_wrong(name, override, message):
    with pytest.raises(ValueError, match=message):
        cfg(name, override)


def test_fields_keeps_the_listed_keys_through_a_resume(tmp_path):
    """Records hold ``id``, ``solved`` and the listed keys only; the summary is built from the records as stored."""
    slim = 'fields=["cost", "sub_moves"]'
    quiet(cfg("smoke", 'rows="0:4"', slim), tmp_path)
    s = quiet(cfg("smoke", 'rows="0:8"', slim), tmp_path)                          # resumed: rows 4-7 are new
    recs = records(tmp_path, "smoke")
    assert len(recs) == s["rows"] == 8 and all(set(r) == {"id", "pres", "solved", "cost", "sub_moves"} for r in recs)
    assert s["solved"] == sum(r["solved"] for r in recs) > 0
    assert s["cost"]["total"] == sum(r["cost"] for r in recs) and s["cost_unit"] == "pops"
    assert s["config"]["fields"] == ["cost", "sub_moves"]


def test_fields_never_hides_an_error(tmp_path):
    csv = tmp_path / "rows.csv"
    csv.write_text("r1,r2\nX,x\nxxY,Yx\n")                   # det 0, a good row
    s = quiet(cfg("smoke", f'benchmark="{csv}"', "rows=", "name=bad", 'fields=["cost"]'), tmp_path)
    recs = by_id(tmp_path, "bad")
    assert set(recs["0"]) == {"id", "pres", "solved", "cost", "error"}
    assert set(recs["1"]) == {"id", "pres", "solved", "cost"}
    assert s["errors"] == 1


# ---- cost and CPU ------------------------------------------------------------------------------------------------

def test_summary_has_the_cost_and_cpu_numbers(tmp_path):
    s = quiet(cfg("smoke", 'rows="0:12"'), tmp_path)
    recs = records(tmp_path, "smoke")
    cost, cpu = [r["cost"] for r in recs], sum(r["cpu_seconds"] for r in recs)
    assert s["cost_unit"] == s["cost"]["unit"] == "pops" and cpu > 0
    assert s["cost_mean"] == pytest.approx(statistics.fmean(cost), abs=0.01)
    assert s["cost_median"] == statistics.median(cost)
    assert s["cpu_seconds"] == pytest.approx(cpu, abs=0.001)
    assert s["us_per_cost"] == pytest.approx(1e6 * cpu / sum(cost), rel=1e-3)


def test_cpu_seconds_is_cpu_time_not_waiting(tmp_path, monkeypatch):
    from acx.runner.methods import SOLVERS, record

    def sleepy(pres, cfg):
        time.sleep(0.3)
        return record(False)

    monkeypatch.setitem(SOLVERS, "greedy", sleepy)
    quiet(cfg("smoke", 'rows="0:1"'), tmp_path)
    rec = records(tmp_path, "smoke")[0]
    assert rec["seconds"] >= 0.3 and rec["cpu_seconds"] < 0.15


def test_resuming_a_run_whose_records_predate_cpu_seconds_still_summarizes(tmp_path):
    """Older result folders have no ``cpu_seconds``, ``verified`` or ``pres`` in their records: their rows count as
    done, so a shipped run still resumes."""
    quiet(cfg("smoke", 'rows="0:3"'), tmp_path)
    file = tmp_path / "smoke" / "paths.jsonl"
    old = [{k: v for k, v in rec.items() if k not in ("verified", "cpu_seconds", "pres")}
           for rec in records(tmp_path, "smoke")]
    file.write_text("".join(json.dumps(rec) + "\n" for rec in old))
    s = quiet(cfg("smoke", 'rows="0:5"'), tmp_path)
    recs = records(tmp_path, "smoke")
    assert s["rows"] == len(recs) == 5 and sum("cpu_seconds" in rec for rec in recs) == 2
    assert sum("pres" in rec for rec in recs) == 2
    assert s["cost"]["total"] == sum(rec["cost"] for rec in recs) and s["cpu_seconds"] > 0


def test_summary_of_a_run_with_no_cost_has_no_cost_per_cost(tmp_path):
    """Rows no search ran on (here: det 0) add no cost, so there is no mean to divide by and no price per pop."""
    csv = tmp_path / "rows.csv"
    csv.write_text("r1,r2\nX,x\n")
    s = quiet(cfg("smoke", f'benchmark="{csv}"', "rows=", "name=none"), tmp_path)
    assert s["cost"]["total"] == 0 and s["cost_mean"] == 0 and s["us_per_cost"] is None


def test_two_workers_write_the_same_records_as_one(tmp_path):
    quiet(cfg("smoke", 'rows="0:8"', "name=one"), tmp_path)
    quiet(cfg("smoke", 'rows="0:8"', "name=two", "workers=2"), tmp_path)

    def untimed(name):
        return {i: {k: v for k, v in r.items() if k not in ("seconds", "cpu_seconds")}
                for i, r in by_id(tmp_path, name).items()}

    assert untimed("one") == untimed("two") and len(untimed("one")) == 8


# ---- a row that raises ---------------------------------------------------------------------------------------------

@pytest.mark.parametrize("error", [RuntimeError("boom"), ValueError("bad row"), AssertionError("unreduced")])
def test_a_row_that_raises_is_an_error_record_and_the_run_goes_on(tmp_path, monkeypatch, no_warm_up, error):
    """One bad row (a method that raises, a certificate that does not replay) is recorded as unsolved with its
    ``error`` (type: message) and counted in the summary; the other rows still run."""
    from acx.runner.methods import SOLVERS
    real, calls = SOLVERS["greedy"], []

    def second_row_raises(pres, cfg):
        calls.append(pres)
        if len(calls) == 2:
            raise error
        return real(pres, cfg)

    monkeypatch.setitem(SOLVERS, "greedy", second_row_raises)
    s = quiet(cfg("smoke", 'rows="0:4"'), tmp_path)
    recs = records(tmp_path, "smoke")
    assert len(calls) == 4 and len(recs) == s["rows"] == 4 and s["errors"] == 1
    bad = recs[1]
    assert bad["solved"] is False and bad["verified"] is False and bad["error"] == f"{type(error).__name__}: {error}"
    assert not any(r.get("error") for r in recs[:1] + recs[2:])


AK2 = "xxYYY, xyxYXY"                  # Akbulut-Kirby n = 2: every method solves it
THREE_GENERATORS = "xy, yz, z"         # trivial, but the two-generator methods cannot take it


def run_py(out, name, *args):
    """``run.py --config configs/<name>.toml --out <out> ...``, the way a user types it."""
    run.main(["--config", os.path.join(ROOT, "configs", f"{name}.toml"), "--out", str(out), *args])


def test_run_py_goes_on_after_a_presentation_its_search_cannot_take(tmp_path, capsys):
    """The smoke config's S20_MK2 priority is for two generators only: the search raises on the second ``--pres``,
    which becomes that row's error record while the first row is solved, and the command ends normally."""
    run_py(tmp_path, "smoke", "--set", "name=x", "--pres", AK2, "--pres", THREE_GENERATORS)
    first, second = records(tmp_path, "x")
    assert first["solved"] and first["verified"] and not first.get("error")
    assert (second["solved"], second["verified"]) == (False, False)
    assert second["error"].startswith("ValueError: ") and "two generators" in second["error"]
    s = summary_of(tmp_path, "x")
    assert (s["rows"], s["solved"], s["errors"]) == (2, 1, 1)
    assert f"error={second['error']}" in capsys.readouterr().out                    # the row's line names the error


@pytest.mark.parametrize("name", ["smoke", "aut", "cov", "hybrid"])
def test_a_three_generator_row_is_an_error_for_every_two_generator_method(tmp_path, name):
    """smoke (S20_MK2), aut (Whitehead on F2), cov and the hybrid raise ``ValueError`` on it: an error record each."""
    run_py(tmp_path, name, "--pres", AK2, "--pres", THREE_GENERATORS)
    first, second = records(tmp_path, f"{name}_pres")
    assert first["solved"] and not first.get("error")
    assert not second["solved"] and second["error"].startswith("ValueError: ") and "generator" in second["error"]


def test_the_hybrid_on_an_unreduced_relator_does_not_stop_the_run(tmp_path):
    """``xXx`` made the hybrid's cascade raise ``AssertionError`` (as the whole run). Whatever the hybrid decides
    about the row, the row after it is still run."""
    run_py(tmp_path, "hybrid", "--pres", "xXx, y", "--pres", AK2)
    unreduced, after = records(tmp_path, "hybrid_pres")
    assert after["solved"] and after["verified"]
    assert not unreduced.get("error") or unreduced["error"].startswith("AssertionError: ")


# ---- per-method counters, decode switches, row selection (coverage audit T04, T19, T24) --------------------------

# (config, overrides, counters in summary["caps"], cost unit): unsolved rows 600 and 639 of MS640 at a tiny budget
CAP_CASES = [
    ("smoke", ["search.budget=3", "search.cap=16"], ["cap"], "pops"),
    ("aut", ["search.budget=3", "search.cap=16"], ["cap"], "pops"),
    ("cov", ["search.budget=3", "search.cap=16"], ["cap"], "pops"),
    ("hybrid", ["hybrid.budget=3"], ["cap", "dyn_cap", "slack"], "units"),
    ("ngen_sac", ["search.budget=3", "search.cap=16"], ["cap"], "pops"),
    pytest.param("rl", ["rl.width=2", "rl.steps=2", "rl.cap=8"], ["cap"], "evaluations", marks=needs_torch)]


@pytest.mark.parametrize("name,overrides,counters,unit", CAP_CASES)
def test_every_method_records_and_sums_its_cap_counters(tmp_path, name, overrides, counters, unit):
    """Unsolved rows still carry their counters (a skipped rl row a blank one); one ``caps`` block per counter."""
    from acx.core.capcount import fields
    s = quiet(cfg(name, 'benchmark="ms640"', 'rows="600,639"', *overrides), tmp_path)
    recs = records(tmp_path, s["name"])
    assert len(recs) == 2 and not any(r["solved"] for r in recs)
    assert all(set(fields(prefix)) <= set(r) for r in recs for prefix in counters)
    assert list(s["caps"]) == counters and all(block["rows"] == len(recs) for block in s["caps"].values())
    assert s["cost"]["unit"] == s["cost_unit"] == unit
    if name == "cov":
        assert all("cap_legs_bound" in r for r in recs) and "cap_legs_bound" in s["caps"]["cap"]
    if name == "rl":                                            # rows with a relator over the cap are skipped
        assert s["skipped"] == 2 and s["caps"]["cap"]["cap"] == 8 and s["caps"]["cap"]["dropped"] == 0


@pytest.mark.parametrize("option", ["search.cyclic=false", "decode=false"])
def test_cyclic_false_and_decode_false_store_no_elementary_length(tmp_path, option):
    """The S-move path is kept and replayed, but nothing decodes it: ``elem_moves`` is null, the S-move lengths
    stay in the summary."""
    s = quiet(cfg("smoke", 'rows="0:8"', option), tmp_path)
    solved = [r for r in records(tmp_path, "smoke") if r["solved"]]
    assert len(solved) == s["solved"] > 0
    assert all(r["elem_moves"] is None and r["elementary"] is None and r["path"] and r["verified"] for r in solved)
    lengths = s["path_length"]["ac_path"]
    assert lengths["elem_moves"] is None and lengths["sub_moves"]["n"] == len(solved)


@pytest.mark.parametrize("name,overrides", [("aut", ['rows="0:4"']),
                                            ("hybrid", ['benchmark="ladder60"', 'rows="ac19_11987,ms_000"'])])
def test_decode_false_keeps_the_length_of_an_elementary_certificate(tmp_path, name, overrides):
    """The hybrid's and aut's certificates are elementary moves: ``decode = false`` does not take ``elem_moves``."""
    s = quiet(cfg(name, *overrides, "decode=false"), tmp_path)
    solved = [r for r in records(tmp_path, s["name"]) if r["solved"]]
    assert len(solved) == s["solved"] > 0 and all(r["elem_moves"] >= r["sub_moves"] > 0 for r in solved)


def test_rows_selection_forms_and_unknown_ids():
    from acx import data
    rows = data.rows("bench60")
    ids = [r.id for r in rows]
    assert len(runner.select(rows, None)) == len(runner.select(rows, "")) == 60
    assert runner.select(rows, "5:") == rows[5:] and runner.select(rows, ":3") == rows[:3]
    assert runner.select(rows, "::20") == rows[::20] and len(rows[::20]) == 3
    assert [r.id for r in runner.select(rows, f"{ids[3]},{ids[1]}")] == [ids[3], ids[1]]       # ids keep their order
    for spec, missing in (("nope", ["nope"]), (f"{ids[0]},nope,{ids[1]}", ["nope"]), ("nope,nada", ["nope", "nada"])):
        with pytest.raises(KeyError) as error:
            runner.select(rows, spec)
        assert error.value.args[0] == f"rows not in the benchmark: {missing}"


def test_the_library_raises_where_run_py_exits(tmp_path):
    """``runner.run`` raises on a row id or a file that is wrong, before it writes anything; only run.py exits."""
    bad = tmp_path / "bad.txt"
    bad.write_text("xxYYY, xyxYXY\nxy1\n")
    for override, error in (('rows="nope"', KeyError), ('rows="x:3"', KeyError), ('rows="0:3:0"', ValueError),
                            (f'benchmark="{bad}"', ValueError)):
        with pytest.raises(error):
            quiet(cfg("smoke", override), tmp_path / "out")
    assert not (tmp_path / "out").exists()


# ---- resume checks the presentation of each row ------------------------------------------------------------------

AK3 = "xxxYYYY, xyxYXY"                # n = 3: the smoke search does not solve it within its budget


def own_rows(tmp_path, *lines):
    """A config running the smoke search on a file of ``lines``, run name ``m``; each call rewrites the file."""
    mine = tmp_path / "mine.txt"
    mine.write_text("".join(line + "\n" for line in lines))
    return cfg("smoke", f'benchmark="{mine}"', "rows=", "name=m", "search.budget=200")


def outcomes(out):
    return [(r["id"], r["pres"], r["solved"]) for r in records(out, "m")]


def test_resume_solves_again_a_row_whose_presentation_changed(tmp_path):
    """Swapping two lines of an input file changes both rows: neither keeps the record of the other presentation,
    in paths.jsonl or in the summary."""
    quiet(own_rows(tmp_path, AK2, AK3), tmp_path)
    assert outcomes(tmp_path) == [("0", AK2, True), ("1", AK3, False)]
    log = []
    s = runner.run(own_rows(tmp_path, AK3, AK2), str(tmp_path), log=log.append)
    assert "2 rows (0 done)" in log[0]
    assert outcomes(tmp_path) == [("0", AK3, False), ("1", AK2, True)] and (s["rows"], s["solved"]) == (2, 1)


def test_resume_keeps_the_rows_whose_presentation_is_unchanged(tmp_path):
    quiet(own_rows(tmp_path, AK2, AK3), tmp_path)
    log = []
    s = runner.run(own_rows(tmp_path, AK2, "xy, y"), str(tmp_path), log=log.append)
    assert "2 rows (1 done)" in log[0]
    assert outcomes(tmp_path) == [("0", AK2, True), ("1", "xy, y", True)] and (s["rows"], s["solved"]) == (2, 2)


# ---- the run's search backend ------------------------------------------------------------------------------------

@pytest.mark.parametrize("method", ["greedy", "aut", "cov", "ngen", "rankn", "hybrid"])
def test_a_config_without_backend_runs_the_fast_backend(tmp_path, method):
    """``SearchConfig`` keeps ``spec`` as its default, but a run defaults to ``fast`` (the same steps, 27x faster)."""
    from acx.core.config import SearchConfig
    bare = tmp_path / "bare.toml"
    bare.write_text(f'method = "{method}"\nbenchmark = "ms640"\n')
    settings = runner.method_config(runner.load_config(str(bare)))
    assert getattr(settings, "search", settings).backend == "fast"
    assert SearchConfig().backend == "spec"


def test_a_config_that_names_the_spec_backend_keeps_it():
    assert runner.method_config(cfg("baseline_spec")).backend == "spec"
    assert runner.method_config(cfg("smoke", "search.backend=spec")).backend == "spec"
    assert runner.method_config(cfg("hybrid", "hybrid.backend=spec")).backend == "spec"


# ---- the warm-up solve -------------------------------------------------------------------------------------------

def watch_solves(monkeypatch, log_file):
    """Wrap the greedy solver so that each presentation it is given is appended to ``log_file`` (also from workers)."""
    from acx.runner.methods import SOLVERS
    real = SOLVERS["greedy"]

    def watched(pres, cfg):
        with open(log_file, "a") as f:
            f.write(", ".join(pres.strs) + "\n")
        return real(pres, cfg)

    monkeypatch.setitem(SOLVERS, "greedy", watched)


def test_the_warm_up_solve_comes_before_the_rows_and_is_not_recorded(tmp_path, monkeypatch):
    """Compiling the numba kernels must not land in row 0's ``cpu_seconds``: one unrecorded solve runs first."""
    from acx.runner.execute import WARM_UP
    log_file = tmp_path / "solves.txt"
    watch_solves(monkeypatch, log_file)
    quiet(cfg("smoke", 'rows="0:2"'), tmp_path / "out")
    solves = log_file.read_text().splitlines()
    assert len(solves) == 3 and solves[0] == ", ".join(WARM_UP.strs)
    assert [r["id"] for r in records(tmp_path / "out", "smoke")] == ["0", "1"]
    log_file.unlink()
    quiet(cfg("smoke", 'rows="0:2"'), tmp_path / "out")                    # nothing left to solve: no warm-up either
    assert not log_file.exists()


def test_each_worker_warms_up_once_as_it_starts(tmp_path, monkeypatch):
    from acx.runner.execute import WARM_UP
    log_file = tmp_path / "solves.txt"
    watch_solves(monkeypatch, log_file)
    quiet(cfg("smoke", 'rows="0:4"', "workers=2"), tmp_path / "out")
    solves = log_file.read_text().splitlines()
    assert len(solves) == 6 and solves.count(", ".join(WARM_UP.strs)) == 2
    assert len(records(tmp_path / "out", "smoke")) == 4


def test_a_warm_up_that_raises_does_not_stop_the_run(tmp_path, monkeypatch):
    """The rows record their own errors; a warm-up the method cannot take (three generators here) is skipped."""
    from acx.data import parse_presentation
    from acx.runner import execute
    monkeypatch.setattr(execute, "WARM_UP", parse_presentation("xy, yz, z"))
    assert quiet(cfg("smoke", 'rows="0:2"'), tmp_path)["solved"] == 2


# ---- a damaged paths.jsonl, a summary without CPU times, a published folder --------------------------------------

def test_a_bad_line_before_the_last_stops_the_resume_and_names_it(tmp_path):
    """Only a cut-off last line is an interrupted write; a bad line with records after it is not dropped silently."""
    quiet(cfg("smoke", 'rows="0:3"'), tmp_path)
    f = tmp_path / "smoke" / "paths.jsonl"
    first, second, third = f.read_text().splitlines(keepends=True)
    for bad in ("garbage\n", second[:30] + "\n"):
        f.write_text(first + bad + third)
        with pytest.raises(ValueError, match=r"paths\.jsonl:2: "):
            quiet(cfg("smoke", 'rows="0:5"'), tmp_path)
        assert f.read_text() == first + bad + third                    # nothing truncated


def test_without_cpu_seconds_in_fields_the_summary_has_no_cpu_numbers(tmp_path):
    s = quiet(cfg("smoke", 'rows="0:3"', 'fields=["cost"]'), tmp_path)
    assert s["cost"]["total"] > 0 and s["cpu_seconds"] is None and s["us_per_cost"] is None


def published(tmp_path):
    """A copy of the shipped ``results/smoke`` (summary.json and config.json, no paths.jsonl) under ``tmp_path``."""
    folder = tmp_path / "smoke"
    folder.mkdir()
    for name in ("summary.json", "config.json"):
        shutil.copy(os.path.join(ROOT, "results", "smoke", name), folder)
    return folder


def test_a_subset_run_never_replaces_a_published_summary(tmp_path):
    folder = published(tmp_path)
    shipped = (folder / "summary.json").read_text()
    with pytest.raises(SystemExit, match="published"):
        quiet(cfg("smoke", 'rows="0:2"'), tmp_path)
    assert (folder / "summary.json").read_text() == shipped
    assert sorted(os.listdir(folder)) == ["config.json", "summary.json"]
    assert quiet(cfg("smoke", 'rows="0:2"'), tmp_path, fresh=True)["rows"] == 2


def test_a_full_rerun_of_a_published_folder_reproduces_it(tmp_path):
    """The config's own 20 rows: the run is the published one again, so it may rewrite the summary."""
    folder = published(tmp_path)
    shipped = json.loads((folder / "summary.json").read_text())
    s = quiet(cfg("smoke"), tmp_path)
    assert s["rows"] == s["solved"] == shipped["solved"] == 20 and s["cost"] == shipped["cost"]


# ---- --rows: ids with spaces or colons ---------------------------------------------------------------------------

def test_rows_ids_may_carry_spaces_and_colons():
    rows = [type("R", (), {"id": i})() for i in ("0", "1", "2", "ms:1", "a")]

    def ids(spec):
        return [r.id for r in runner.select(rows, spec)]

    assert ids("0, 2") == ids(" 0 ,2 ") == ["0", "2"]
    assert ids("ms:1") == ["ms:1"] and ids("a, ms:1") == ["a", "ms:1"]
    assert ids("-2:") == ["ms:1", "a"] and ids(" 1:3 ") == ["1", "2"] and ids("::2") == ["0", "2", "a"]
    for spec in ("a:b", "1:2:3:4", "0:1.5"):
        with pytest.raises(KeyError) as error:
            runner.select(rows, spec)
        assert error.value.args[0] == f"rows not in the benchmark: [{spec!r}]"
    for spec in ("0:5:0", "::0"):
        with pytest.raises(ValueError, match=f"^bad rows slice {spec!r}"):
            runner.select(rows, spec)


# ---- the rl numbers are checked when the config loads ------------------------------------------------------------

@pytest.mark.parametrize("override, message", [
    ("rl.width=0", "rl.width must be an int >= 1, got 0"),
    ('rl.width="a"', "rl.width must be an int >= 1, got 'a'"),
    ("rl.width=1.5", "rl.width must be an int >= 1, got 1.5"),
    ("rl.width=true", "rl.width must be an int >= 1, got True"),
    ("rl.steps=0", "rl.steps must be an int >= 1, got 0"),
    ('rl.alpha="x"', "rl.alpha must be a number, got 'x'"),
    ("rl.alpha=true", "rl.alpha must be a number, got True")])
def test_rl_numbers_are_checked_when_the_config_loads(tmp_path, override, message):
    """A bad ``rl.width``, ``steps`` or ``alpha`` raised once per row (IndexError, TypeError); now once, at load."""
    path = tmp_path / "rl.toml"
    path.write_text('method = "rl"\nbenchmark = "bench60"\n')
    with pytest.raises(ValueError) as error:
        runner.load_config(str(path), [override])
    assert str(error.value) == message


def test_rl_numbers_in_range_are_kept():
    keywords = runner.method_config(cfg("rl", "rl.width=1", "rl.steps=1", "rl.alpha=1"))
    assert (keywords["width"], keywords["steps"], keywords["alpha"]) == (1, 1, 1)
    assert runner.method_config(cfg("rl", "rl.alpha=0.5"))["alpha"] == 0.5


# ---- resume keeps only the records of rows the input still holds, under their own config -------------------------

THREE_ROWS = "xxYYY, xyxYXY\nYYXyx, Yx\nYYXyx, YX\n"          # all three solved by the length search below


def three_rows(tmp_path, name):
    """A length search over ``mine.txt`` (written with ``THREE_ROWS``), every row, run name ``name``."""
    mine = tmp_path / "mine.txt"
    mine.write_text(THREE_ROWS)
    return mine, cfg("smoke", f'benchmark="{mine}"', 'rows=""', f"name={name}", "search.priority=length")


def test_rows_removed_from_the_input_leave_the_summary(tmp_path):
    mine, c = three_rows(tmp_path, "shrink")
    assert quiet(c, tmp_path)["rows"] == 3
    mine.write_text("xx, yyy\n")                                  # one row now, |det| = 6
    s = quiet(c, tmp_path)
    assert (s["rows"], s["solved"]) == (1, 0)                     # was (3, 2): ids 1 and 2 stayed, solved
    assert [(r["id"], r["pres"]) for r in records(tmp_path, "shrink")] == [("0", "xx, yyy")]


def test_a_changed_row_outside_the_selection_is_not_summarized_as_solved(tmp_path):
    mine, c = three_rows(tmp_path, "edit")
    assert quiet(c, tmp_path)["solved"] == 3
    mine.write_text("xxYYY, xyxYXY\nYYXyx, Yx\nxx, yyy\n")        # row 2 is now not AC-trivial
    s = quiet({**c, "rows": "0:1"}, tmp_path)
    assert [r["id"] for r in records(tmp_path, "edit")] == ["0", "1"]      # row 2's old record is gone
    assert (s["rows"], s["solved"]) == (2, 2)                     # was (3, 3)


def test_a_record_without_pres_is_kept_while_its_row_is_in_the_input(tmp_path):
    """Records written before ``pres`` was stored resume as they are; one whose id left the input does not."""
    mine, c = three_rows(tmp_path, "old")
    quiet(c, tmp_path)
    paths = tmp_path / "old" / "paths.jsonl"
    old = [{k: v for k, v in r.items() if k != "pres"} for r in records(tmp_path, "old")]
    paths.write_text("".join(json.dumps(r) + "\n" for r in old))
    mine.write_text("xxYYY, xyxYXY\nYYXyx, Yx\n")
    s = quiet(c, tmp_path)
    assert [r["id"] for r in records(tmp_path, "old")] == ["0", "1"] and (s["rows"], s["solved"]) == (2, 2)
    assert all("pres" not in r for r in records(tmp_path, "old"))          # kept, not solved again


def test_records_without_their_config_json_are_not_resumed(tmp_path):
    """A branch switch removes the tracked config.json and keeps the ignored paths.jsonl; budget-3 records were then
    summarized as a budget-1000 run."""
    quiet(cfg("smoke", 'rows="0:5"', "name=nocfg", "search.budget=3"), tmp_path)
    folder = tmp_path / "nocfg"
    (folder / "config.json").unlink()
    kept = (folder / "paths.jsonl").read_text()
    with pytest.raises(SystemExit, match="paths.jsonl without its config.json"):
        quiet(cfg("smoke", 'rows="0:5"', "name=nocfg", "search.budget=1000"), tmp_path)
    assert (folder / "paths.jsonl").read_text() == kept and not (folder / "config.json").exists()
    assert quiet(cfg("smoke", 'rows="0:5"', "name=nocfg", "search.budget=1000"), tmp_path, fresh=True)["rows"] == 5
