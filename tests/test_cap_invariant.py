"""Cap counters on ``acx.search`` (spec and fast): the counter's zero means "the cap never mattered".

The invariant, for a run at cap ``C`` and any larger cap ``C'`` (None included): the two runs pop the
same states in the same order, with the same outcome and path, exactly when ``cap_needed`` is None or
``C' < cap_needed``. The planted cases (a start over the cap, binds at a pop, a published S20_MK2 solve
whose pop count the cap changes) must be caught with their exact counts.
"""
import pytest

from acx.core.config import SearchConfig
from acx.core.words import Presentation
from acx.search import CAP_FIELDS, search

ROWS = [7, 120, 200, 322, 380, 466, 500, 551, 600, 620, 627, 635, 639]          # MS640 ids
THREE = [Presentation.parse("xyxYXY", "xxyXYY", "zxZyy"), Presentation.parse("xY", "yZ", "zyX")]


def outcome(r):
    return r.trace, r.solved, r.pops, r.path


def check_record(r):
    s = r.stats
    assert set(CAP_FIELDS) <= set(s)
    assert 0 <= s["cap_would_pop"] <= s["cap_dropped"]
    assert (s["cap_would_pop"] == 0) == (s["cap_first_bind"] is None) == (s["cap_needed"] is None)
    assert (s["cap_dropped"] == 0) == (s["cap_dropped_min_total"] is None)
    if s["cap_needed"] is not None:
        assert s["cap_needed"] > s["cap"] and 1 < s["cap_first_bind"] <= r.pops + 1


def kind(r):
    s = r.stats
    if not s["cap_dropped"]:
        return "no drops"
    if s["cap_first_bind"] is None:
        return "solved with drops" if r.solved else "dropped, never binds"
    return "binds: queue ran dry" if s["cap_first_bind"] == r.pops + 1 else "binds at a pop"


def invariant(pres, cap, budget, **kw):
    """Run at ``cap``, rerun at larger caps, assert the invariant; return the run's kind."""
    cfg = SearchConfig(cap=cap, budget=budget, trace=True, **kw)
    r = search(pres, cfg)
    check_record(r)
    need = r.stats["cap_needed"]
    larger = {cap + 1, cap + 3, cap + 6, 40} | ({need - 1, need} if need else set())
    for c2 in sorted(c for c in larger if c > cap) + [None]:
        same = outcome(search(pres, cfg.replace(cap=c2))) == outcome(r)
        assert same == (need is None or (c2 is not None and c2 < need)), (cap, c2, need)
    return kind(r)


@pytest.mark.parametrize("priority", ["length", "s20_mk2"])
def test_invariant_fast(ms640, priority):
    kinds = {invariant(ms640[pid], cap, 300, priority=priority, backend="fast")
             for pid in ROWS for cap in (10, 13, 16)}
    assert kinds == {"no drops", "solved with drops", "dropped, never binds", "binds at a pop",
                     "binds: queue ran dry"}


@pytest.mark.parametrize("priority", ["length", "s20_mk2"])
@pytest.mark.parametrize("pid", [322, 500, 620, 639])
def test_invariant_spec(ms640, pid, priority):
    invariant(ms640[pid], 13, 120, priority=priority)


@pytest.mark.parametrize("backend", ["spec", "fast"])
@pytest.mark.parametrize("cyclic", [True, False])
def test_invariant_three_generators_and_linear(backend, cyclic):
    for pres in THREE:
        for cap in (5, 6, 8):
            invariant(pres, cap, 200, backend=backend, cyclic=cyclic)


# Planted binds: MS640 at cap 16, budget 2,000, LENGTH (row 620: the start is over the cap, so its only pop
# drops everything and the queue runs dry; the rest bind at a pop or never).
PLANTED = {500: (True, 6, 8, 23, 0, None, None), 600: (False, 2000, 300694, 22, 17657, 195, 17),
           620: (False, 1, 102, 23, 90, 2, 17), 635: (False, 2000, 194260, 25, 282, 1905, 17),
           639: (False, 10, 2113, 25, 1252, 4, 17)}


@pytest.mark.parametrize("pid", sorted(PLANTED))
def test_planted_binds(ms640, pid):
    backends = ("fast",) if PLANTED[pid][1] > 100 else ("spec", "fast")
    for backend in backends:
        r = search(ms640[pid], SearchConfig(cap=16, budget=2000, backend=backend))
        s = r.stats
        got = (r.solved, r.pops, s["cap_dropped"], s["cap_dropped_min_total"], s["cap_would_pop"],
               s["cap_first_bind"], s["cap_needed"])
        assert got == PLANTED[pid]


@pytest.mark.slow
def test_s20_mk2_row_527_cap_changes_a_published_solve(ms640):
    """S20_MK2 at cap 24 solves row 527 in 7,458 pops; the counter says a cap of 25 changes the search,
    and caps 25 and up (and none) solve it in 7,479."""
    cfg = SearchConfig(priority="s20_mk2", backend="fast", budget=10_000, cap=24)
    r = search(ms640[527], cfg)
    s = r.stats
    assert (r.solved, r.pops, s["cap_would_pop"], s["cap_first_bind"], s["cap_needed"]) == (True, 7458, 21, 1653, 25)
    for c2 in (25, 32, None):
        r2 = search(ms640[527], cfg.replace(cap=c2))
        assert (r2.solved, r2.pops, r2.path_length) == (True, 7479, r.path_length)


# Published MS640 runs (fast, cap 24, budget 10,000): solved rows and the counters' golden counts.
GOLDEN = {"length": dict(solved=606, rows_dropped=26, rows_would_pop=0),
          "s20_mk2": dict(solved=626, rows_dropped=74, rows_would_pop=S20_WOULD_POP)}


@pytest.mark.slow
@pytest.mark.parametrize("priority", ["length", "s20_mk2"])
def test_ms640_golden_counters(ms640, priority):
    """The counters only observe: the published solved counts hold, and the cap binds where pinned."""
    from acx.core.capcount import summarize
    recs = []
    for pid, pres in enumerate(ms640):
        r = search(pres, SearchConfig(priority=priority, backend="fast", budget=10_000, cap=24))
        check_record(r)
        recs.append({"id": str(pid), "solved": r.solved, **{k: r.stats[k] for k in CAP_FIELDS}})
    s = summarize(recs)
    got = dict(solved=sum(r["solved"] for r in recs), rows_dropped=s["rows_dropped"], rows_would_pop=s["rows_would_pop"])
    assert got == GOLDEN[priority]
