"""acx.ngen.sweep: the rank-3 / rank-n brute-force sweep (word pool, starts, rows, resume, summary, verifier)."""
import json
import os
import shutil
import sys

import numpy as np
import pytest

from acx import data
from acx.core.config import SearchConfig
from acx.core.words import fmt
from acx.ngen import sweep
from acx.ngen.sweep import SweepConfig, SweepError, combos, pool, reduced_words, start
from acx.search import search
from acx.verify.replay import abs_det

ROW_IDS = ["0", "100", "330"]


def cfg(extra=1, min_len=1, max_len=2, rows="0:3", name="t", budget=300, backend="fast", **rankn):
    return {"name": name, "method": "rankn", "benchmark": "ms640", "rows": rows, "workers": 1,
            "search": {"budget": budget, "cap": 24, "backend": backend},
            "rankn": {"extra": extra, "min_len": min_len, "max_len": max_len, **rankn}}


def quiet(c, out, **kw):
    return sweep.run(c, str(out), log=lambda *a: None, **kw)


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
    {"rankn": {"extra": 4}}, {"rankn": {"extra": 0}},
    {"rankn": {"min_len": 3, "max_len": 2}}, {"rankn": {"bogus": 1}}, {"rankn": {"sample": 2}},
])
def test_config_errors(bad):
    c = cfg()
    for k, v in bad.items():
        c[k] = {**c[k], **v}
    with pytest.raises(ValueError):
        SweepConfig.from_cfg(c)


def test_uncapped_is_allowed():
    sc = SweepConfig.from_cfg({"search": {"cap": "none", "budget": 100}, "rankn": {"max_len": 6}})
    assert sc.search.cap is None


def test_shipped_configs_load():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for name, extra, max_len in (("rank3_bf", 1, 4), ("rank4_bf", 2, 3), ("rank5_bf", 3, 2)):
        c = sweep.load_config(os.path.join(root, "configs", f"{name}.toml"))
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
        sweep._task((str(d), "0", data.rows("ms640")[0].pres, sc))
    s = quiet(cfg(rows="0:2", budget=200), tmp_path, fresh=True)
    assert s["rows"] == 2 and sorted(os.listdir(d / "rows")) == ["0.npz", "1.npz"]


def test_summary_matches_the_arrays(tmp_path):
    s = quiet(cfg(max_len=2, rows="0:12", budget=400), tmp_path)
    d = str(tmp_path / "t")
    rows = [sweep.load_row(sweep.row_path(d, str(i))) for i in range(12)]
    wl = sweep.lengths(SweepConfig.from_cfg(cfg(max_len=2)))
    assert s["control_solved"] == sum(bool(r["control"]["solved"]) for r in rows)
    for n in (1, 2):
        t = s["buckets"][f"L{n}"]
        some = [bool(((r["path_len"] >= 0) & (wl <= n)).any()) for r in rows]
        assert t["oracle"]["solved_by_some"] == sum(some)
        assert t["oracle"]["gained_over_control"] == sum(a and not r["control"]["solved"] for a, r in zip(some, rows))
        rate = np.mean([(r["path_len"][wl == n] >= 0).mean() for r in rows])
        assert t["solved"] == round(float(rate), 4)
        assert round(t["fewer"] + t["same"] + t["more"] + t["unsolved"], 3) == 1.0
    assert s["buckets"]["L2"]["oracle"]["solved_by_some"] >= s["buckets"]["L1"]["oracle"]["solved_by_some"]
    assert os.path.exists(os.path.join(d, "summary.md")) and os.path.exists(os.path.join(d, "summary.json"))


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
    put()
    assert quiet_v(recheck=30) == []
    with open(os.path.join(d, "config.json")) as f:
        key = json.load(f)
    key["sweep"]["search"]["budget"] = 301                      # a renamed budget: the row files no longer match
    with open(os.path.join(d, "config.json"), "w") as f:
        json.dump(key, f)
    assert any("ident differs" in m for m in quiet_v())


def test_counter_consistency_rules():
    sc = SweepConfig.from_cfg(cfg(budget=100))
    fails = []
    base = {"cap_dropped": [0, 5, 5], "cap_dropped_min_total": [-1, 30, 30], "cap_first_bind": [-1, -1, 7],
            "cap_would_pop": [0, 0, 2], "cap_needed": [-1, -1, 26]}

    def check(**kw):
        r = {k: np.array(v) for k, v in {**base, **kw}.items()}
        fails.clear()
        sweep._check_counters(r, np.array([True, True, False]), np.array([5, 40, 100]), 100, sc, fails.append)
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
    r = {"cap_dropped": np.array([5]), "cap_dropped_min_total": np.array([30]), "cap_first_bind": np.array([-1])}
    fails.clear()
    sweep._check_counters(r, np.array([False]), np.array([40]), 100, sc, fails.append)
    assert fails


@pytest.mark.skipif("cap_first_bind" not in sweep.counter_fields(SearchConfig(cap=24, budget=10)),
                    reason="the search reports no bind counter")
def test_rank3_counters_prove_the_cap_irrelevant(tmp_path):
    """Cells whose cap never binds are the same search at any larger cap; cells that bind exist at a tight cap."""
    ids = ["635", "300", "450", "600"]        # at cap 12: drops without a bind (3 rows), binds (600)
    quiet({**cfg(max_len=2, rows=",".join(ids), budget=300), "search": {"budget": 300, "cap": 12, "backend": "fast"}}, tmp_path)
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
def test_cli_entry_point(tmp_path, monkeypatch):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sweep.main(["--config", os.path.join(root, "configs", "rank3_bf.toml"), "--rows", "0:3", "--set", "rankn.max_len=2",
                "--set", "workers=1", "--set", "search.budget=300", "--out", str(tmp_path), "--verify", "5"])
    assert os.path.exists(tmp_path / "rank3_bf" / "summary.json")


@pytest.mark.skipif("rankn" not in __import__("acx.runner", fromlist=["x"]).METHODS, reason="runner method not wired yet")
def test_run_py_entry_point(tmp_path):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, root)
    import run as run_py
    run_py.main(["--config", os.path.join(root, "configs", "rank3_bf.toml"), "--rows", "0:3",
                 "--set", "rankn.max_len=2", "--set", "workers=1", "--set", "search.budget=300", "--out", str(tmp_path)])
    assert os.path.exists(tmp_path / "rank3_bf" / "summary.json")


@pytest.mark.slow
def test_ms640_lengths_1_and_2_reproduce_the_baseline(tmp_path):
    """Budget 1,000, cap 24, MS640: control 554; solved by some word of length 1: 403, up to length 2: 472."""
    s = quiet(cfg(max_len=2, rows=None, budget=1000), tmp_path)
    assert s["control_solved"] == 554
    assert s["buckets"]["L1"]["oracle"]["solved_by_some"] == 403
    assert s["buckets"]["L2"]["oracle"]["solved_by_some"] == 472
    assert (round(s["buckets"]["L1"]["solved"], 3), round(s["buckets"]["L2"]["solved"], 3)) == (0.601, 0.684)
    assert sweep.verify(str(tmp_path / "t"), recheck=40, log=lambda *a: None) == []
    shutil.rmtree(tmp_path)
