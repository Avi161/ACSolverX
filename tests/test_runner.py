"""run.py / acx.runner: every method end to end on a few rows, the path and fields options, per-row errors, resume,
config errors, record and cap helpers."""
import importlib.util
import json
import os
import statistics
import time

import pytest

import run
from acx import runner

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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

LENGTH_WITHOUT_PATH = {"cov", "hybrid", "rl"}          # these methods count the S-moves whether or not a path is kept


@pytest.mark.parametrize("name,overrides,kinds", METHOD_CASES)
def test_path_false_is_the_same_search_without_the_certificate(tmp_path, name, overrides, kinds):
    """``path = false`` skips the certificate and its replay, not the search: solves, costs and counters are those of
    ``path = true``. ``path`` and ``elementary`` are null, ``verified`` false and ``steps`` gone; a length survives
    only where the method has it without the path, and is then the true one."""
    quiet(cfg(name, *overrides, "name=full"), tmp_path)
    quiet(cfg(name, *overrides, "name=lite", "path=false"), tmp_path)
    full, lite = by_id(tmp_path, "full"), by_id(tmp_path, "lite")
    assert lite.keys() == full.keys() and any(r["solved"] for r in lite.values())
    for id_, rec in lite.items():
        assert rec["path"] is None and rec["elementary"] is None and rec["verified"] is False
        assert set(full[id_]) - set(rec) <= {"steps"}
        for key, value in rec.items():
            if key in ("sub_moves", "elem_moves"):
                assert value in (None, full[id_][key])
            elif key not in ("path", "elementary", "verified", "seconds", "cpu_seconds"):
                assert value == full[id_][key]
        if rec["solved"] and name in LENGTH_WITHOUT_PATH:
            assert rec["sub_moves"] is not None and rec["sub_moves"] == full[id_]["sub_moves"]


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


# (config, overrides, the check each method runs on its certificate): the first rows of every method
CHECK_CASES = [
    ("smoke", ['rows="0:2"'], "acx.runner.methods.replay"),
    ("aut", ['rows="0:2"'], "acx.runner.methods.replay"),
    ("cov", ['rows="0,496"'], "acx.cov.verify"),
    ("hybrid", ['benchmark="ladder60"', 'rows="ac19_11987,ms_000"'], "acx.runner.methods.replay"),
    ("ngen_sac", ['rows="0:2"'], "acx.ngen.verify"),
    pytest.param("rl", ['rows="0:2"', "rl.width=64", "rl.steps=60"], "acx.runner.methods.replay", marks=needs_torch)]


@pytest.mark.parametrize("name,overrides,check", CHECK_CASES)
def test_a_certificate_that_fails_its_check_is_an_error_never_a_verified_solve(tmp_path, monkeypatch, name,
                                                                               overrides, check):
    """With ``path = true`` the check stands between a method and its record: when it fails the row is unsolved."""
    from acx.verify import ReplayError

    def fails(*args, **kwargs):
        raise ReplayError("the path does not end trivial")

    monkeypatch.setattr(check, fails)
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


def test_path_false_does_no_replay_and_no_decode(tmp_path, monkeypatch):
    """The speed-up is work skipped: the search is not asked for a path, and nothing replays or decodes one."""
    import importlib
    from acx.runner import methods
    search_replay = importlib.import_module("acx.verify.replay")      # the name ``acx.verify.replay`` is the function
    calls = [count_calls(monkeypatch, methods, "replay"), count_calls(monkeypatch, methods, "decode_and_replay"),
             count_calls(monkeypatch, search_replay, "replay")]
    quiet(cfg("smoke", 'rows="0:4"', "name=lite", "path=false"), tmp_path)
    assert not any(calls)
    quiet(cfg("smoke", 'rows="0:4"', "name=full"), tmp_path)
    assert all(calls)


# ---- the fields option --------------------------------------------------------------------------------------------

@pytest.mark.parametrize("name,override,message", [
    ("smoke", "path=1", "path must be true or false"),
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
    assert len(recs) == s["rows"] == 8 and all(set(r) == {"id", "solved", "cost", "sub_moves"} for r in recs)
    assert s["solved"] == sum(r["solved"] for r in recs) > 0
    assert s["cost"]["total"] == sum(r["cost"] for r in recs) and s["cost_unit"] == "pops"
    assert s["config"]["fields"] == ["cost", "sub_moves"]


def test_fields_never_hides_an_error(tmp_path):
    csv = tmp_path / "rows.csv"
    csv.write_text("r1,r2\nX,x\nxxY,Yx\n")                   # det 0, a good row
    s = quiet(cfg("smoke", f'benchmark="{csv}"', "rows=", "name=bad", 'fields=["cost"]'), tmp_path)
    recs = by_id(tmp_path, "bad")
    assert set(recs["0"]) == {"id", "solved", "cost", "error"} and set(recs["1"]) == {"id", "solved", "cost"}
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
    """Older result folders have no ``cpu_seconds`` or ``verified`` in their records."""
    quiet(cfg("smoke", 'rows="0:3"'), tmp_path)
    file = tmp_path / "smoke" / "paths.jsonl"
    old = [{k: v for k, v in rec.items() if k not in ("verified", "cpu_seconds")} for rec in records(tmp_path, "smoke")]
    file.write_text("".join(json.dumps(rec) + "\n" for rec in old))
    s = quiet(cfg("smoke", 'rows="0:5"'), tmp_path)
    recs = records(tmp_path, "smoke")
    assert s["rows"] == len(recs) == 5 and sum("cpu_seconds" in rec for rec in recs) == 2
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
def test_a_row_that_raises_is_an_error_record_and_the_run_goes_on(tmp_path, monkeypatch, error):
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
    first, second = records(tmp_path, name)
    assert first["solved"] and not first.get("error")
    assert not second["solved"] and second["error"].startswith("ValueError: ") and "generator" in second["error"]


def test_the_hybrid_on_an_unreduced_relator_does_not_stop_the_run(tmp_path):
    """``xXx`` made the hybrid's cascade raise ``AssertionError`` (as the whole run). Whatever the hybrid decides
    about the row, the row after it is still run."""
    run_py(tmp_path, "hybrid", "--pres", "xXx, y", "--pres", AK2)
    unreduced, after = records(tmp_path, "hybrid")
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
