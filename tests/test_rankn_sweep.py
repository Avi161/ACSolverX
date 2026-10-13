"""acx.ngen.sweep: the rank-3 / rank-n brute-force sweep (word pool, starts, rows, resume, summary, verifier)."""
import hashlib
import json
import os
import shutil
import sys

import numpy as np
import pytest
from conftest import ROOT

from acx import data
from acx.runner import load_config
from acx.core.config import SearchConfig
from acx.core.words import fmt
from acx.ngen import sweep
from acx.ngen.sweep import SweepConfig, SweepError, combos, pool, reduced_words, start
from acx.ngen.sweep.summary import Bucket, BucketTally, _fraction, _percent
from acx.search import search
from acx.verify.replay import abs_det

ROW_IDS = ["0", "100", "330"]
COUNTER_NAMES = ("cap_dropped", "cap_dropped_min_total", "cap_would_pop", "cap_first_bind", "cap_needed")


def cfg(extra=1, min_len=1, max_len=2, rows="0:3", name="t", budget=300, backend="fast", benchmark="ms640", cap=24,
        **rankn):
    return {"name": name, "method": "rankn", "benchmark": benchmark, "rows": rows, "workers": 1,
            "search": {"budget": budget, "cap": cap, "backend": backend},
            "rankn": {"extra": extra, "min_len": min_len, "max_len": max_len, **rankn}}


def quiet(c, out, **kw):
    return sweep.run(c, str(out), log=lambda *a: None, **kw)


def spy_on_backends(monkeypatch, module):
    """The list that collects the backend of every ``search`` call ``module`` makes from now on."""
    used = []
    real = module.search

    def spy(pres, search_config):
        used.append(search_config.backend)
        return real(pres, search_config)

    monkeypatch.setattr(module, "search", spy)
    return used


# ------------------------------------------------------------------------------------------------- words
def test_reduced_words():
    assert [len(reduced_words(n)) for n in range(1, 8)] == [2 * 3 ** (n - 1) for n in range(1, 8)]
    for n in range(1, 6):
        ws = reduced_words(n)
        assert len(set(ws)) == len(ws) and all(len(w) == n for w in ws)
        assert all(a != -b for w in ws for a, b in zip(w, w[1:])), "freely reduced"
        inv = {tuple(-g for g in reversed(w)) for w in ws}
        assert not inv & set(ws), "one of each pair {w, w^-1}"
        assert len(inv | set(ws)) == 4 * 3 ** (n - 1), "every reduced word is covered"
    assert sum(len(reduced_words(n)) for n in range(1, 5)) == 3 ** 4 - 1
    # the fixed order of the stored baseline (rank3_bf_ms640_b1000_cap24_L3.npz)
    assert [fmt(w) for w in reduced_words(3)][:5] == ["xxx", "xxy", "xyx", "xyy", "xyX"]
    assert [fmt(w) for w in reduced_words(2)] == ["xx", "xy", "yx", "yy", "yX", "Xy"]


def test_pools_and_multisets():
    assert len(pool(1, 3, False)) == 26 and len(combos(26, 2)) == 351     # rank 4
    assert len(pool(1, 2, False)) == 8 and len(combos(8, 3)) == 120       # rank 5
    assert combos(8, 1) == tuple((i,) for i in range(8))
    assert pool(1, 2, True)[0] == (-1,) and pool(1, 2, True)[4] == tuple(-g for g in reversed(pool(1, 2, False)[4]))


@pytest.mark.parametrize("lengths, inverted, md5", [
    ((1, 4), False, "726644f813d80b8f503f953b0569113b"), ((1, 3), False, "5316b757386dd443642462e185252375"),
    ((1, 2), False, "23690e3328000be86d384ce8381f5e72"), ((1, 3), True, "d64ee88ee2e8b6a494dd3bed3853449e")])
def test_pool_order_is_pinned(lengths, inverted, md5):
    """T16: the stored baseline lists its cells in this order. A reorder keeps every count and breaks the comparison."""
    assert hashlib.md5(",".join(map(fmt, pool(*lengths, inverted))).encode()).hexdigest() == md5


def test_start_shape(ms640):
    for pres in ms640[::97]:
        for ws in ([(1, 2)], [(), ()], [(1,), (-2, 1)], [(2,), (1, 1), (-1, -2)]):
            s = start(*pres.rels, ws)
            assert s.n_gen == 2 + len(ws) == len(s.rels)
            assert s.rels[2:] == tuple((-(3 + i),) + tuple(w) for i, w in enumerate(ws))
            assert abs_det(s) == 1


# ----------------------------------------------------------------------------------------------- searches
@pytest.mark.parametrize("extra", [1, 2, 3])
def test_null_stabilisation_is_the_control(ms640, extra):
    scfg = SearchConfig(cap=24, budget=400, backend="fast")
    for pres in ms640[:: 80][:8]:
        c = search(pres, scfg)
        n = search(start(*pres.rels, [()] * extra), scfg)
        assert (c.solved, c.pops, c.path_length) == (n.solved, n.pops, n.path_length)


def test_budget_prefix_and_end_state(ms640):
    for pres in ms640[::64]:
        s = start(*pres.rels, [(1, 2)])
        big = search(s, SearchConfig(cap=24, budget=1000, backend="fast"))
        small = search(s, SearchConfig(cap=24, budget=100, backend="fast"))
        assert small.solved == (big.solved and big.pops <= 100)
        assert small.pops == min(big.pops, 100)
        if big.solved:
            assert len(big.end.rels) == 3 and all(len(r) == 1 for r in big.end.rels)


def test_sweep_row_against_direct_searches(ms640):
    for backend in ("spec", "fast"):
        sc = SweepConfig.from_cfg(cfg(budget=200, backend=backend, sample=1.0))
        ws = sweep.words_of(sc)
        for rid in ROW_IDS:
            pres = ms640[int(rid)]
            out = sweep.sweep_row(rid, pres, sc)
            for i, w in enumerate(ws):
                res = search(start(*pres.rels, [w]), sc.search)
                assert int(out["nodes"][i]) == res.pops
                assert int(out["path_len"][i]) == (res.path_length if res.solved else -1)
                assert int(out["min_total"][i]) == res.stats["min_total"]
                for k in COUNTER_NAMES:
                    assert int(out[k][i]) == (-1 if res.stats[k] is None else res.stats[k]), k
            paths = json.loads(str(out["paths"]))
            assert [p["index"] for p in paths] == [i for i in range(len(ws)) if out["path_len"][i] >= 0]


def test_sample_is_deterministic():
    hits = [sweep.sampled("5", w, 0.25) for w in ("x", "y", "xy", "yx", "xxy", "xyX", "Xy", "yX")]
    assert hits == [sweep.sampled("5", w, 0.25) for w in ("x", "y", "xy", "yx", "xxy", "xyX", "Xy", "yX")]
    assert sweep.sampled("5", "x", 0) is False and sweep.sampled("5", "x", 1) is True


# --------------------------------------------------------------------------------------------- the config
@pytest.mark.parametrize("bad", [
    {"search": {"priority": "s20_mk2"}},                 # defined for two generators only
    {"search": {"cap": 2}},                              # below the start relator Z.w
    {"search": {"budget": 70_000}},                      # pops are stored as uint16
    {"rankn": {"extra": 4}}, {"rankn": {"extra": 0}}, {"rankn": {"search": {"budget": 5}}},
    {"rankn": {"min_len": 3, "max_len": 2}}, {"rankn": {"bogus": 1}}, {"rankn": {"sample": 2}},
])
def test_config_errors(bad):
    c = cfg()
    for k, v in bad.items():
        c[k] = {**c[k], **v}
    with pytest.raises(ValueError):
        SweepConfig.from_cfg(c)


def test_uncapped_rows_drop_nothing(tmp_path):
    """Without a cap the counters report nothing: no drop, no bind, the same searches as capped rows solved."""
    c = cfg(rows="0:4", budget=200, max_len=2)
    c["search"]["cap"] = "none"
    s = quiet(c, tmp_path)
    assert s["cap_counters"]["dropped"] == 0 and s["cap_counters"]["could_bind"] == 0
    for rid in range(4):
        r = sweep.load_row(sweep.row_path(str(tmp_path / "t"), str(rid)))
        assert (r["cap_dropped"] == 0).all() and (r["cap_first_bind"] == -1).all()
        assert (r["cap_would_pop"] == 0).all() and (r["cap_needed"] == -1).all()
        assert (r["cap_dropped_min_total"] == -1).all()


def test_every_config_has_one_comment_line():
    """Configs are short: one comment line saying what the config runs, then the TOML (usage is in docs). The
    annotated template is the exception: it documents every key."""
    for name in sorted(set(os.listdir(os.path.join(ROOT, "configs"))) - {"template.toml"}):
        with open(os.path.join(ROOT, "configs", name)) as f:
            lines = f.read().splitlines()
        assert sum(1 for x in lines if x.lstrip().startswith("#")) == 1 and lines[0].startswith("#"), name


def test_shipped_configs_load():
    for name, extra, max_len in (("rank3_bf", 1, 4), ("rank4_bf", 2, 3), ("rank5_bf", 3, 2)):
        c = load_config(os.path.join(ROOT, "configs", f"{name}.toml"))
        sc = SweepConfig.from_cfg(c)
        assert (sc.extra, sc.max_len, sc.search.budget, sc.search.cap) == (extra, max_len, 1000, 24)


# --------------------------------------------------------------------------------- run, resume, summary
def test_run_resume_and_refusals(tmp_path):
    c = cfg(rows="0:4")
    s = quiet(c, tmp_path)
    d = tmp_path / "t"
    files = sorted(os.listdir(d / "rows"))
    assert files == ["0.npz", "1.npz", "2.npz", "3.npz"] and s["rows"] == 4
    mt = {f: os.path.getmtime(d / "rows" / f) for f in files}
    os.remove(d / "rows" / "2.npz")
    quiet(c, tmp_path)                                    # only row 2 is searched again
    assert sorted(os.listdir(d / "rows")) == files
    assert all(os.path.getmtime(d / "rows" / f) == mt[f] for f in files if f != "2.npz")
    with pytest.raises(SystemExit):                       # another budget in the same directory
        quiet(cfg(rows="0:4", budget=200), tmp_path)
    sc = SweepConfig.from_cfg(cfg(rows="0:4", budget=200))
    with pytest.raises(SweepError):                       # a row file from another budget is never merged
        sweep.sweep_row_file((str(d), "0", data.rows("ms640")[0].pres, sc))
    s = quiet(cfg(rows="0:2", budget=200), tmp_path, fresh=True)
    assert s["rows"] == 2 and sorted(os.listdir(d / "rows")) == ["0.npz", "1.npz"]


def test_run_rejects_a_changed_word_range(tmp_path):
    """T16: another word range in a used directory is another run, refused like another budget."""
    quiet(cfg(rows="0:2"), tmp_path)
    with pytest.raises(SystemExit):
        quiet(cfg(rows="0:2", max_len=3), tmp_path)


def test_sweep_summary_covers_every_row_file(tmp_path):
    """T06 (B5 again): a re-run on fewer rows must not shrink ``summary.json`` to those rows."""
    quiet(cfg(rows="0:3"), tmp_path)
    assert quiet(cfg(rows="0:1"), tmp_path)["rows"] == 3
    with open(tmp_path / "t" / "summary.json") as f:
        assert json.load(f)["rows"] == 3


def test_verify_and_summary_ignore_stray_temp_files(tmp_path):
    """T06: an interrupted atomic write leaves ``rows/<id>.npz.tmp<pid>.npz``; it is not a row file."""
    quiet(cfg(rows="0:3"), tmp_path)
    d = tmp_path / "t"
    shutil.copy(d / "rows" / "0.npz", d / "rows" / "0.npz.tmp999.npz")
    assert sweep.verify(str(d), log=lambda *a: None) == []
    assert sweep.summarize(str(d))["rows"] == 3


@pytest.mark.parametrize("rels, cap", [(("yxY", "xxyXY"), 4), (("Y", "XXyxxy"), 5), (("XX", "YXYxyXy"), 4)])
def test_a_start_over_the_cap_passes_the_verifier(tmp_path, rels, cap):
    """F4: a start with a relator over the cap can be the only child the cap drops, and the counters rightly leave it
    out (it is no new state). Such a search runs dry with drops and no bind, which ``verify`` must accept."""
    rows = tmp_path / "rows.csv"
    rows.write_text("name,r1,r2\nrow," + ",".join(rels) + "\n")
    quiet(cfg(rows=None, budget=200, backend="spec", max_len=cap - 1, benchmark=str(rows), cap=cap), tmp_path)
    assert sweep.verify(str(tmp_path / "t"), recheck=20, log=lambda *a: None) == []


def test_summary_matches_the_arrays(tmp_path):
    s = quiet(cfg(max_len=2, rows="0:12", budget=400), tmp_path)
    d = str(tmp_path / "t")
    rows = [sweep.load_row(sweep.row_path(d, str(i))) for i in range(12)]
    wl = np.array([len(w) for w in sweep.pool(1, 2, False)])
    assert s["control_solved"] == sum(bool(r["control"]["solved"]) for r in rows)
    for n in (1, 2):
        t = s["buckets"][f"L{n}"]
        some = [bool(((r["path_len"] >= 0) & (wl <= n)).any()) for r in rows]
        assert t["oracle"]["solved_by_some"] == sum(some)
        assert t["oracle"]["gained_over_control"] == sum(a and not r["control"]["solved"] for a, r in zip(some, rows))
        rate = np.mean([(r["path_len"][wl == n] >= 0).mean() for r in rows])
        assert t["solved"] == round(float(rate), 6)
        assert round(t["fewer"] + t["same"] + t["more"] + t["lost"], 3) == 1.0
    assert s["buckets"]["L2"]["oracle"]["solved_by_some"] >= s["buckets"]["L1"]["oracle"]["solved_by_some"]
    assert os.path.exists(os.path.join(d, "summary.json"))
    with open(os.path.join(d, "summary.md")) as f:
        assert "shares of the control-solved presentations" in f.read()               # the legend under the table


def test_summary_columns_are_the_baselines():
    """fewer/same/more/lost are over the control-solved rows; a start that solves a control-unsolved row is a gain,
    not "some faster" (the definitions of the baseline's published tables)."""
    every = np.ones(4, bool)
    bucket = Bucket("L1", every, every)
    t = BucketTally()
    # the control solves row 1 in 10 pops: the four starts need 5 (fewer), 10 (same), 20 (more) and do not solve (lost)
    t.add_row(bucket, np.array([True, True, True, False]), np.array([5, 10, 20, 40]), control_solved=True,
              control_pops=10)
    t.add_row(bucket, np.array([True, True, True, True]), np.array([3, 7, 9, 9]), control_solved=False, control_pops=40)
    s = t.table(bucket, n_rows=2, n_control_solved=1)
    assert (s["fewer"], s["same"], s["more"], s["lost"]) == (0.25, 0.25, 0.25, 0.25)
    assert s["oracle"] == {"solved_by_some": 2, "gained_over_control": 1, "control_solved_lost_by_every": 0,
                           "some_faster_than_control": 1}


def test_summary_percent_is_rounded_once():
    """0.806458 prints as 80.6% (the baseline's L3 cell at budget 1,000), not 80.7% via 0.8065."""
    assert _percent(_fraction(0.8064580826313679)) == "80.6%"


def test_a_sweep_over_no_row_writes_an_empty_summary(tmp_path):
    """A selector that matches nothing is no crash: no row, no searches, and every share is undefined (null, "-")."""
    s = quiet(cfg(rows="5:5"), tmp_path)
    assert (s["rows"], s["searches"], s["control_solved"]) == (0, 0, 0)
    assert all(t["solved"] is None and t["fewer"] is None and t["lost"] is None for t in s["buckets"].values())
    markdown = (tmp_path / "t" / "summary.md").read_text()
    assert "| L1 | 2 | - | - |" in markdown
    assert s["best_single"] is None and "Best single start" not in markdown      # no start is the best of nothing
    assert sweep.verify(str(tmp_path / "t"), log=lambda *a: None) == []


@pytest.mark.parametrize("extra,max_len", [(2, 1), (3, 1)])
def test_rank_4_and_5_run(tmp_path, extra, max_len):
    s = quiet(cfg(extra=extra, max_len=max_len, rows="0:3", budget=200), tmp_path)
    n = len(combos(len(pool(1, max_len, False)), extra))
    assert s["starts_per_row"] == n and s["extra"] == extra and s["searches"] == 3 * n
    assert sweep.verify(str(tmp_path / "t"), recheck=10, log=lambda *a: None) == []


# ------------------------------------------------------------------------------------------- the verifier
def test_verify_passes_and_rejects_tampering(tmp_path):
    c = cfg(rows="0:3", sample=1.0)
    quiet(c, tmp_path)
    d = str(tmp_path / "t")
    quiet_v = lambda **kw: sweep.verify(d, log=lambda *a: None, **kw)
    assert quiet_v(recheck=30) == []
    path = sweep.row_path(d, "1")
    good = dict(np.load(path))

    def put(**changes):
        np.savez_compressed(path, **{**good, **changes})

    r = sweep.load_row(path)
    i = int(np.flatnonzero(r["path_len"] >= 0)[0])
    nodes = good["nodes"].copy()
    nodes[i] += 1                                               # another pop count than the search gives
    put(nodes=nodes)
    assert quiet_v(recheck=200)
    put(nodes=np.full_like(good["nodes"], 999))                 # above the budget
    assert any("pops outside" in m for m in quiet_v())
    put(nodes=good["nodes"][:-1])
    assert any("wrong shape" in m for m in quiet_v())
    put(**{"null": np.array(json.dumps({**r["null"], "pops": r["null"]["pops"] + 1}))})
    assert any("control != null" in m for m in quiet_v())
    paths = json.loads(str(good["paths"]))
    paths[0]["path"] = paths[0]["path"][:-1]                    # a path that stops short of the trivial presentation
    put(paths=np.array(json.dumps(paths)))
    assert any("replay" in m for m in quiet_v())
    dropped = good["cap_dropped"]
    j = int(np.flatnonzero(dropped == 0)[0]) if (dropped == 0).any() else 0
    would = good["cap_would_pop"].copy()
    would[j] = int(dropped[j]) + 1                              # more would-pop states than dropped children
    put(cap_would_pop=would)
    assert any("cap_would_pop above" in m for m in quiet_v())
    put()
    assert quiet_v(recheck=30) == []
    with open(os.path.join(d, "config.json")) as f:
        key = json.load(f)
    key["sweep"]["search"]["budget"] = 301                      # a renamed budget: the row files no longer match
    with open(os.path.join(d, "config.json"), "w") as f:
        json.dump(key, f)
    assert any("ident differs" in m for m in quiet_v())


def test_recheck_runs_every_cell_on_both_backends(tmp_path, monkeypatch):
    """The stored config does not say which backend wrote the rows, so each cell runs on both: one is the other."""
    quiet(cfg(rows="0:3"), tmp_path)
    used = spy_on_backends(monkeypatch, sweep.check)
    assert sweep.verify(str(tmp_path / "t"), recheck=6, log=lambda *a: None) == []
    assert sorted(used) == ["fast"] * 6 + ["spec"] * 6


def test_verify_names_the_row_each_failure_belongs_to(tmp_path):
    quiet(cfg(rows="0:3"), tmp_path)
    d = str(tmp_path / "t")
    for row_id in ("0", "2"):
        path = sweep.row_path(d, row_id)
        good = dict(np.load(path))
        np.savez_compressed(path, **{**good, "nodes": np.full_like(good["nodes"], 999)})      # above the budget
    failures = sweep.verify(d, log=lambda *a: None)
    assert sorted({f.split(":")[0] for f in failures}) == ["row 0", "row 2"]


def test_counter_consistency_rules():
    sc = SweepConfig.from_cfg(cfg(budget=100))
    fails = []
    base = {"cap_dropped": [0, 5, 5], "cap_dropped_min_total": [-1, 30, 30], "cap_first_bind": [-1, -1, 7],
            "cap_would_pop": [0, 0, 2], "cap_needed": [-1, -1, 26]}

    def check(**kw):
        r = {k: np.array(v) for k, v in {**base, **kw}.items()}
        fails.clear()
        sweep.check_counters(r, np.array([True, True, False]), np.array([5, 40, 100]), 100, sc, fails.append)
        return list(fails)

    assert check() == []
    assert check(cap_dropped_min_total=[-1, -1, 30])                    # a drop without a smallest score
    assert check(cap_dropped_min_total=[-1, 24, 30])                    # a dropped child within the cap
    assert check(cap_first_bind=[3, -1, 7], cap_would_pop=[1, 0, 2], cap_needed=[25, -1, 26])   # a bind without a drop
    assert check(cap_first_bind=[-1, -1, 1])                            # the start cannot bind
    assert check(cap_first_bind=[-1, -1, 101])                          # beyond pops + 1
    assert check(cap_would_pop=[0, 0, 0])                               # a bind with nothing that would pop
    assert check(cap_would_pop=[0, 0, 9])                               # more would-pop states than drops
    assert check(cap_needed=[-1, -1, -1])                               # would-pop without a needed cap
    assert check(cap_needed=[-1, -1, 24])                               # the needed cap is above the cap
    # an unsolved search that stopped below the budget with drops must have a bind (when nothing else is reported)
    r = {"cap_dropped": np.array([5]), "cap_dropped_min_total": np.array([30]), "cap_first_bind": np.array([-1]),
         "cap_would_pop": np.array([0]), "cap_needed": np.array([-1])}
    fails.clear()
    sweep.check_counters(r, np.array([False]), np.array([40]), 100, sc, fails.append)
    assert fails
    fails.clear()          # ... unless the start is over the cap: then the only drops may be the start itself (F4)
    sweep.check_counters(r, np.array([False]), np.array([40]), 100, sc, fails.append, start_over_cap=True)
    assert not fails


def test_rank3_counters_prove_the_cap_irrelevant(tmp_path):
    """Cells whose cap never binds are the same search at any larger cap; cells that bind exist at a tight cap."""
    ids = ["635", "300", "450", "600"]        # at cap 12: drops without a bind (3 rows), binds (600)
    tight = {"budget": 300, "cap": 12, "backend": "fast"}
    quiet({**cfg(max_len=2, rows=",".join(ids), budget=300), "search": tight}, tmp_path)
    d = str(tmp_path / "t")
    sc = SweepConfig.from_cfg({"search": {"budget": 300, "cap": 12, "backend": "fast"}, "rankn": {"max_len": 2}})
    ws = sweep.words_of(sc)
    big = sc.search.replace(cap=64)
    free = sc.search.replace(cap=None)
    seen = {"no_bind_dropped": 0, "bind": 0}
    for rid in ids:
        r = sweep.load_row(sweep.row_path(d, rid))
        for i, w in enumerate(ws):
            s = start(*data.rows("ms640")[int(rid)].pres.rels, [w])
            a = search(s, sc.search)
            if r["cap_first_bind"][i] < 0:
                for other in (big, free):
                    b = search(s, other)
                    assert (a.solved, a.pops, a.path) == (b.solved, b.pops, b.path)
                seen["no_bind_dropped"] += r["cap_dropped"][i] > 0
            else:
                seen["bind"] += 1
                assert a.stats["cap_needed"] > 12 and a.stats["cap_first_bind"] == r["cap_first_bind"][i]
    assert seen["no_bind_dropped"] > 0 and seen["bind"] > 0, seen
    assert sweep.verify(d, recheck=40, log=lambda *a: None) == []


# --------------------------------------------------------------------------------------------- entry points
def test_cli_entry_point(tmp_path):
    sweep.main(["--config", os.path.join(ROOT, "configs", "rank3_bf.toml"), "--rows", "0:3", "--set", "rankn.max_len=2",
                "--set", "workers=1", "--set", "search.budget=300", "--out", str(tmp_path), "--verify", "5"])
    assert os.path.exists(tmp_path / "rank3_bf" / "summary.json")


def test_run_py_entry_point(tmp_path):
    """``run.py`` runs the shipped rank-3 config (the runner delegates method ``rankn`` to the sweep)."""
    sys.path.insert(0, ROOT)
    import run as run_py
    run_py.main(["--config", os.path.join(ROOT, "configs", "rank3_bf.toml"), "--rows", "0:2", "--out", str(tmp_path)])
    s = json.load(open(tmp_path / "rank3_bf" / "summary.json"))
    assert s["rows"] == 2 and s["extra"] == 1 and s["cap_counters"]["fields"] == list(sweep.COUNTERS)


def test_runner_refuses_rankn_s20_mk2_at_load(tmp_path):
    """The runner's config load (run.py, before anything is written) refuses rank-n with S20_MK2 and bad rankn keys."""
    from acx.runner import load_config
    path = os.path.join(ROOT, "configs", "rank3_bf.toml")
    with pytest.raises(ValueError, match="length"):
        load_config(path, ["search.priority=s20_mk2"])
    with pytest.raises(ValueError, match="rankn"):
        load_config(path, ["rankn.bogus=1"])
    assert not (tmp_path / "rank3_bf").exists()


@pytest.mark.slow
def test_ms640_lengths_1_and_2_reproduce_the_baseline(tmp_path):
    """Budget 1,000, cap 24, MS640: control 554; solved by some word of length 1: 403, up to length 2: 472."""
    s = quiet(cfg(max_len=2, rows=None, budget=1000), tmp_path)
    assert s["control_solved"] == 554
    assert s["buckets"]["L1"]["oracle"]["solved_by_some"] == 403
    assert s["buckets"]["L2"]["oracle"]["solved_by_some"] == 472
    assert (round(s["buckets"]["L1"]["solved"], 3), round(s["buckets"]["L2"]["solved"], 3)) == (0.601, 0.684)
    published = {"L1": (0.0, 0.0, 69.4, 30.6, 0), "L2": (1.3, 0.1, 77.7, 21.0, 35)}     # faster, same, slower, lost
    for name, cells in published.items():
        t = s["buckets"][name]
        got = tuple(round(100 * t[k], 1) for k in ("fewer", "same", "more", "lost"))
        assert got + (t["oracle"]["some_faster_than_control"],) == cells
    assert sweep.verify(str(tmp_path / "t"), recheck=40, log=lambda *a: None) == []
    shutil.rmtree(tmp_path)


def test_rows_that_are_not_two_generator_two_relator_are_refused(tmp_path):
    """The control and every start assume two generators and two relators; name the rows that break it."""
    path = tmp_path / "rows.csv"
    path.write_text("id,r1,r2,r3\nok,xxYYY,xyxYXY,\nthree,xx,yy,zz\n")
    all_rows = data.rows(str(path))
    sweep.rows.check_two_relators(all_rows[:1])
    with pytest.raises(ValueError, match=r"two-generator, two-relator.*\['three'\]"):
        sweep.rows.check_two_relators(all_rows)


def test_a_config_without_a_backend_runs_on_fast(tmp_path, monkeypatch):
    """Every other method defaults to the numba backend; ``SearchConfig`` alone would say ``spec``."""
    c = cfg(rows="0:2", max_len=1, budget=50)
    del c["search"]["backend"]
    used = spy_on_backends(monkeypatch, sweep.rows)
    quiet(c, tmp_path)
    assert set(used) == {"fast"}


def test_help_names_the_module(capsys):
    """R8: ``python -m acx.ngen.sweep --help`` printed ``usage: __main__.py``."""
    with pytest.raises(SystemExit):
        sweep.main(["--help"])
    assert "usage: python -m acx.ngen.sweep" in capsys.readouterr().out


# ------------------------------------------------------------------- the driver refuses before it writes anything
def test_sweep_refuses_a_row_that_is_not_two_generators_two_relators(tmp_path):
    rows = tmp_path / "rows.csv"
    rows.write_text("id,r1,r2,r3\nok,xxYYY,xyxYXY,\nthree,xx,yy,zz\n")
    with pytest.raises(ValueError, match="two-generator, two-relator"):
        quiet(cfg(rows=None, benchmark=str(rows)), tmp_path / "out", fresh=True)
    assert not (tmp_path / "out" / "t").exists()


def published_sweep(tmp_path, rows):
    """A sweep folder as git ships it: config.json and summary.*, no ``rows/``; its summary claims ``rows`` rows."""
    quiet(cfg(rows="0:3", max_len=1, budget=50), tmp_path)
    folder = tmp_path / "t"
    shutil.rmtree(folder / "rows")
    summary = json.loads((folder / "summary.json").read_text())
    summary["rows"] = rows
    (folder / "summary.json").write_text(json.dumps(summary))
    return folder


def test_a_smoke_run_does_not_replace_a_published_summary(tmp_path):
    folder = published_sweep(tmp_path, 640)
    shipped = {name: (folder / name).read_text() for name in ("summary.json", "summary.md", "config.json")}
    with pytest.raises(SystemExit, match="published summary"):
        quiet(cfg(rows="0:1", max_len=1, budget=50), tmp_path)
    assert json.loads((folder / "summary.json").read_text())["rows"] == 640
    assert {name: (folder / name).read_text() for name in shipped} == shipped and not (folder / "rows").exists()
    assert quiet(cfg(rows="0:1", max_len=1, budget=50), tmp_path, fresh=True)["rows"] == 1


def test_a_run_of_every_published_row_may_rewrite_the_summary(tmp_path):
    """The rows held plus the rows asked for cover the published count: that run is the published one again."""
    published_sweep(tmp_path, 3)
    assert quiet(cfg(rows="0:3", max_len=1, budget=50), tmp_path)["rows"] == 3
    assert quiet(cfg(rows="0:1", max_len=1, budget=50), tmp_path)["rows"] == 3      # rows/ now holds all three


@pytest.mark.parametrize("damage", ["", '{"rows": 2, "ext'])
def test_a_cut_off_summary_does_not_stop_a_resume(tmp_path, damage):
    """A sweep stopped while writing summary.json leaves it empty or cut off; the resume rebuilds it from rows/."""
    quiet(cfg(rows="0:2", max_len=1, budget=50), tmp_path)
    (tmp_path / "t" / "summary.json").write_text(damage)
    assert quiet(cfg(rows="0:2", max_len=1, budget=50), tmp_path)["rows"] == 2
    assert json.loads((tmp_path / "t" / "summary.json").read_text())["rows"] == 2


def test_cli_exits_with_one_line_for_a_bad_config_or_row(tmp_path):
    """As ``run.py``: a ValueError or KeyError of the library ends ``python -m acx.ngen.sweep`` with its message."""
    rank3 = os.path.join(ROOT, "configs", "rank3_bf.toml")
    three = tmp_path / "rows.csv"
    three.write_text("id,r1,r2,r3\nthree,xx,yy,zz\n")
    for extra, message in ((["--set", "rankn.bogus=1"], "unknown rankn keys ['bogus']"),
                           (["--rows", "nope"], "rows not in the benchmark: ['nope']"),
                           (["--set", f'benchmark="{three}"', "--set", 'rows=""'],
                            "rankn takes two-generator, two-relator rows; not ['three']")):
        with pytest.raises(SystemExit) as error:
            sweep.main(["--config", rank3, "--out", str(tmp_path / "out"), *extra])
        assert error.value.code == message
    assert not (tmp_path / "out").exists()
