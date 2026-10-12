"""run.py / acx.runner: every method end to end on a few rows, resume, config errors."""
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
