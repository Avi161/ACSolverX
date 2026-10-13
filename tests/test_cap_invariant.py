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
            invariant(pres, cap, 200 if backend == "fast" else 100, backend=backend, cyclic=cyclic)


@pytest.mark.parametrize("backend, budget, kinds", [
    ("spec", 60, {"binds at a pop", "dropped, never binds"}),
    ("fast", 150, {"binds at a pop", "solved with drops"}),
])
def test_invariant_s20_mk2_linear(ms640, backend, budget, kinds):
    """S20_MK2 without cyclic reduction, which the three-generator rows above cannot test (S20_MK2 needs two)."""
    got = {invariant(ms640[pid], 12, budget, priority="s20_mk2", cyclic=False, backend=backend)
           for pid in (144, 322, 435)}
    assert got == kinds


def counters(r):
    """``(solved, pops, dropped, min_total, would_pop, first_bind, needed)`` of a result, as ``PLANTED`` lists them."""
    s = r.stats
    return (r.solved, r.pops, s["cap_dropped"], s["cap_dropped_min_total"], s["cap_would_pop"],
            s["cap_first_bind"], s["cap_needed"])


# Planted binds, keyed (priority, MS640 row, cap, budget). Row 620 starts over cap 16, so its only pop drops
# everything and the queue runs dry; the other rows bind at a pop, or never (500 solves with drops, S20_MK2 551
# drops without binding). The two priorities rank the children differently: S20_MK2's numbers are not LENGTH's.
PLANTED = {
    ("length", 500, 16, 2000): (True, 6, 8, 23, 0, None, None),
    ("length", 600, 16, 2000): (False, 2000, 300694, 22, 17657, 195, 17),
    ("length", 620, 16, 2000): (False, 1, 102, 23, 90, 2, 17),
    ("length", 635, 16, 2000): (False, 2000, 194260, 25, 282, 1905, 17),
    ("length", 639, 16, 2000): (False, 10, 2113, 25, 1252, 4, 17),
    ("length", 435, 12, 150): (True, 113, 4732, 19, 134, 12, 13),
    ("s20_mk2", 500, 16, 300): (True, 6, 8, 23, 0, None, None),
    ("s20_mk2", 551, 16, 300): (False, 300, 6222, 23, 0, None, None),
    ("s20_mk2", 466, 16, 300): (False, 300, 21522, 22, 62, 30, 17),
    ("s20_mk2", 600, 16, 300): (False, 300, 34966, 23, 221, 9, 17),
    ("s20_mk2", 620, 16, 2000): (False, 1, 102, 23, 90, 2, 17),
    ("s20_mk2", 639, 16, 300): (False, 10, 2113, 25, 400, 3, 17),
    ("s20_mk2", 144, 12, 150): (True, 105, 2272, 18, 2, 27, 13),
    ("s20_mk2", 435, 12, 150): (True, 65, 2808, 20, 3, 27, 13),
}


@pytest.mark.parametrize("key", PLANTED, ids=lambda key: "-".join(map(str, key)))
def test_planted_binds(ms640, key):
    priority, pid, cap, budget = key
    backends = ("fast",) if PLANTED[key][1] > 150 else ("spec", "fast")         # spec is too slow for long runs
    for backend in backends:
        r = search(ms640[pid], SearchConfig(priority=priority, cap=cap, budget=budget, backend=backend))
        assert counters(r) == PLANTED[key]


@pytest.mark.parametrize("backend", ["spec", "fast"])
@pytest.mark.parametrize("priority", ["length", "s20_mk2"])
@pytest.mark.parametrize("budget, counted", [(1, (0, None, None)), (2, (1, 2, 17)), (3, (2, 2, 17)),
                                             (5, (4, 2, 17)), (91, (90, 2, 17))])
def test_dry_queue_boundary_counts_only_what_the_budget_would_pop(ms640, backend, priority, budget, counted):
    """Row 620 at cap 16 starts over the cap: its one pop drops all 102 children (90 distinct states) and the queue
    runs dry. A budget of 1 is spent by that pop, so nothing more would pop; a budget of ``b`` would pop ``b - 1``
    of the 90, the first at pop 2 and the least longest relator of them all (17) being the cap needed."""
    r = search(ms640[620], SearchConfig(priority=priority, cap=16, budget=budget, backend=backend))
    s = r.stats
    assert (r.solved, r.pops, s["cap_dropped"], s["cap_dropped_min_total"]) == (False, 1, 102, 23)
    assert (s["cap_would_pop"], s["cap_first_bind"], s["cap_needed"]) == counted


@pytest.mark.parametrize("priority, pid, pops", [
    ("s20_mk2", 144, {12: 105, 13: 107, None: 107}),
    ("s20_mk2", 435, {12: 65, 13: 68, None: 68}),
    ("length", 435, {12: 113, 13: 142, None: None}),              # None: unsolved within the budget
])
def test_cap_needed_is_the_cap_that_changes_a_solved_row(ms640, priority, pid, pops):
    """At cap 12 the counter says 13 is the cap that changes the search: it solves the row in other pops, and so
    does no cap at all (LENGTH row 435 then stops solving it within 150 pops)."""
    runs = {cap: search(ms640[pid], SearchConfig(priority=priority, cap=cap, budget=150, backend="fast"))
            for cap in pops}
    assert runs[12].stats["cap_needed"] == 13
    assert {cap: (r.pops if r.solved else None) for cap, r in runs.items()} == pops


# A dropped child that ties a later pop on (priority, depth) sorts before it by the state bytes alone. A bar without
# the bytes would count 351 would-pop states on the first run, bind at pop 9 on the second and count 38 on the third.
@pytest.mark.parametrize("priority, pid, cap, counted", [("length", 635, 12, (385, 12)), ("s20_mk2", 144, 10, (70, 8)),
                                                         ("s20_mk2", 466, 16, (62, 30))])
def test_ties_on_priority_and_depth_are_ordered_by_the_state_bytes(ms640, priority, pid, cap, counted):
    for backend in ("spec", "fast"):
        s = search(ms640[pid], SearchConfig(priority=priority, cap=cap, budget=150, backend=backend)).stats
        assert (s["cap_would_pop"], s["cap_first_bind"]) == counted


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


# Published MS640 runs (fast, cap 24, budget 10,000): solved rows and the counters' golden counts. On
# S20_MK2 a cap of 25 would change the pop sequence of 20 rows (6 of them solved: 527, 529, 628, 629, 630,
# 633); on LENGTH the cap never mattered.
GOLDEN = {"length": dict(solved=606, rows_dropped=26, rows_would_pop=0),
          "s20_mk2": dict(solved=626, rows_dropped=74, rows_would_pop=20)}


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
