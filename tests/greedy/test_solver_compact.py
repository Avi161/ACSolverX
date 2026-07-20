"""Failure modes that only ``GreedyCompactSolver`` has.

Parity with heavy is asserted in ``test_solver_parity``; the sort invariant its
heap depends on is in ``test_packed_keys``. What is left is everything that
exists *because* the containers are numpy: the reservation, the growth path, the
open-addressing table, and the chunked kernel that lets a Python ``progress``
callback (and hence the memory guard) run inside an ``@njit`` loop.

A caveat this file cannot escape, and does not pretend to: the repo caps every
test at ``MAX_BUDGET = 1_000`` nodes, so nothing here reaches the 64M-state scale
where int32 overflow or a table ceiling would bite. Those are argued
analytically, not asserted -- see the module docstring of ``greedy_compact`` and
the notes on each test below.
"""

import numpy as np
import pytest

import experiments.run_baseline as rb
from experiments.search.greedy_baseline import GreedyHeavySolver, greedy_search
from experiments.search.greedy_compact import (
    GreedyCompactSolver, _next_pow2, est_states, greedy_search_compact, row_width,
)
from experiments.greedy_tests.fixtures.presentations import ms640, ms_unsolved
from experiments.greedy_tests.tools.regen_golden import MAX_BUDGET

DEEP = ms_unsolved([0])[0]      # never solves, so it spends the whole budget
EASY = ms640([0])[0]            # solves in a handful of nodes


def _strs(p):
    return p.to_strs()


# --- the reservation ------------------------------------------------------

def test_the_reservation_is_never_exceeded_on_a_real_search():
    """`_grow` copies the arena. At 1M x 4 workers a copy is a 30 GB spike, so
    the projection must hold in practice, not merely be recoverable."""
    s = GreedyCompactSolver(*_strs(DEEP), max_nodes=MAX_BUDGET,
                            max_relator_length=48)
    s.solve()
    assert s.grew == 0, "the discovery projection under-reserved"
    assert s.n_discovered <= s.states_cap


def test_est_states_dominates_what_a_real_search_discovers():
    """The 82.9*b^0.981 fit, checked against an actual count at the test budget.

    Guards the sizing model itself: if the fit drifted low, every worker would
    grow mid-search and the memory guard would trip on the copy.
    """
    s = GreedyCompactSolver(*_strs(DEEP), max_nodes=MAX_BUDGET,
                            max_relator_length=48)
    s.solve()
    assert s.n_discovered <= est_states(MAX_BUDGET) * 1.5


def test_bytes_reserved_is_exact_arithmetic_not_a_measurement():
    """Never calibrate on macOS ru_maxrss -- it reports bytes/state FALLING as
    states grow. With numpy arrays the number is simply known."""
    s = GreedyCompactSolver(*_strs(EASY), max_nodes=1000, max_relator_length=48)
    n, rw = s.states_cap, s.rw
    expected = n * rw + n + n + 4 * n + 4 * n + s.tcap * 4
    assert s.bytes_reserved() == expected
    assert s.bytes_per_state() == pytest.approx(expected / n)


def test_a_bigger_cap_costs_exactly_the_wider_row():
    """Per-state cost is set by the cap, not by how long the relators happen to
    be -- the opposite of the heavy solver, whose bytes key grows with depth."""
    kw = dict(max_nodes=1000, reserve_states=10_000)
    a = GreedyCompactSolver(*_strs(EASY), max_relator_length=24, **kw)
    b = GreedyCompactSolver(*_strs(EASY), max_relator_length=48, **kw)
    for s, cap in ((a, 24), (b, 48)):
        assert s.bytes_reserved() == \
            s.states_cap * (row_width(cap) + 10) + s.tcap * 4


def test_row_width_is_byte_aligned_per_relator():
    for cap in (1, 2, 23, 24, 25, 48):
        assert row_width(cap) == 2 * ((cap + 1) // 2)
        assert row_width(cap) * 2 >= 2 * cap      # nibble slots must fit both


# --- the growth path (must work, even though it should never fire) --------

def test_growth_preserves_the_result_exactly():
    """Force a reservation far too small. The rehash-and-copy must be invisible."""
    r1, r2 = _strs(DEEP)
    kw = dict(max_relator_length=48, cyclic_reduce=True)
    ref = greedy_search_compact(r1, r2, 400, **kw)

    s = GreedyCompactSolver(r1, r2, max_nodes=400, reserve_states=1, **kw)
    solved, nodes = s.solve()
    assert s.grew >= 1, "reserve_states=1 should have forced a grow"
    assert (solved, nodes) == (ref["solved"], ref["nodes_explored"])
    assert s.min_total == ref["min_relator_length"]
    assert s.max_total == ref["max_relator_length"]
    assert s.max_expanded_total == ref["max_relator_length_expanded"]
    assert list(s.relators(s.min_id)) == ref["min_relator"]
    assert list(s.relators(s.max_id)) == ref["max_relator"]


def test_growth_rehashes_the_visited_table():
    """A copied arena with a stale table would re-discover states it already had,
    inflating nodes_explored. Same n_discovered proves the rehash landed."""
    r1, r2 = _strs(DEEP)
    big = GreedyCompactSolver(r1, r2, max_nodes=400, max_relator_length=48)
    big.solve()
    small = GreedyCompactSolver(r1, r2, max_nodes=400, max_relator_length=48,
                                reserve_states=1)
    small.solve()
    assert small.grew >= 1 and big.grew == 0
    assert small.n_discovered == big.n_discovered


# --- the visited table ----------------------------------------------------

def test_the_table_never_passes_half_full():
    """Linear probing needs a free slot; the kernel's pre-pop headroom check is
    what guarantees one. If load could reach 1.0, `_lookup` would spin forever."""
    s = GreedyCompactSolver(*_strs(DEEP), max_nodes=MAX_BUDGET,
                            max_relator_length=48)
    s.solve()
    assert s.n_discovered * 2 <= s.tcap
    assert s.tcap == _next_pow2(2 * s.states_cap)
    assert int(np.count_nonzero(s.table)) == s.n_discovered


def test_every_discovered_state_is_in_the_table_exactly_once():
    s = GreedyCompactSolver(*_strs(DEEP), max_nodes=500, max_relator_length=48)
    s.solve()
    ids = sorted(int(v) - 1 for v in s.table[s.table != 0])
    assert ids == list(range(s.n_discovered))


def test_n_discovered_matches_the_heavy_solver():
    """The strongest single check that dedup is identical: one extra or one
    missing collision would move this number, and nodes_explored with it."""
    for cap in (24, 48):
        h = GreedyHeavySolver(*_strs(DEEP), max_nodes=500, max_relator_length=cap)
        h.solve()
        c = GreedyCompactSolver(*_strs(DEEP), max_nodes=500, max_relator_length=cap)
        c.solve()
        assert c.n_discovered == h.n_discovered


# --- the chunked kernel ---------------------------------------------------

@pytest.fixture
def tick(monkeypatch):
    """Shrink the progress tick to 100 nodes in BOTH solvers.

    The real tick is 1024, and MAX_BUDGET is 1000, so a search that reaches even
    one tick would break the budget ceiling. Shrinking it exercises the identical
    code path -- the kernel still returns to Python on the boundary -- at a legal
    budget. (`_HB_CHECK_EVERY` is read from module globals inside `solve()`.)
    """
    import experiments.search.greedy_baseline as gb
    import experiments.search.greedy_compact as gc
    monkeypatch.setattr(gb, "_HB_CHECK_EVERY", 100)
    monkeypatch.setattr(gc, "_HB_CHECK_EVERY", 100)
    return 100


def test_progress_fires_on_exactly_the_same_ticks_as_the_heavy_solver(tick):
    """An @njit loop cannot call Python, so the kernel returns every tick and the
    callback runs in between. The memory guard rides it; a broken cadence would
    silently disarm the guard."""
    heavy, compact = [], []
    greedy_search(*_strs(DEEP), 550, max_relator_length=48, high_speedup=True,
                  progress=heavy.append)
    greedy_search_compact(*_strs(DEEP), 550, max_relator_length=48,
                          progress=compact.append)
    assert heavy == [100, 200, 300, 400, 500]
    assert compact == heavy


def test_no_tick_fires_before_the_first_boundary(tick):
    seen = []
    greedy_search_compact(*_strs(DEEP), 60, max_relator_length=48,
                          progress=seen.append)
    assert seen == []


def test_the_real_tick_never_fires_under_the_test_budget_ceiling():
    """_HB_CHECK_EVERY is 1024 and MAX_BUDGET is 1000 -- documents why the
    `tick` fixture above has to exist, and pins the two constants' relation."""
    seen = []
    greedy_search_compact(*_strs(DEEP), MAX_BUDGET, max_relator_length=48,
                          progress=seen.append)
    assert seen == []


def test_a_progress_callback_that_raises_unwinds_cleanly(tick):
    """This is exactly how `_MemGuard` stops a search: it raises out of the
    callback. All state is already written back to the arrays at that point."""
    class Stop(Exception):
        pass

    with pytest.raises(Stop) as e:
        greedy_search_compact(*_strs(DEEP), 550, max_relator_length=48,
                              progress=lambda n: (_ for _ in ()).throw(Stop(n)))
    assert e.value.args[0] == 100


def test_a_budget_straddling_a_chunk_boundary_gives_the_same_answer(tick):
    """The kernel returns to Python every tick. Budgets just below, on, and just
    above a boundary must all agree with the heavy solver."""
    r1, r2 = _strs(DEEP)
    for budget in (99, 100, 101, 999, 1000):
        c = greedy_search_compact(r1, r2, budget, max_relator_length=48)
        h = greedy_search(r1, r2, budget, max_relator_length=48, high_speedup=True)
        assert c["nodes_explored"] == h["nodes_explored"] == budget
        assert c["max_relator_length_expanded"] == h["max_relator_length_expanded"]
        assert c["min_relator"] == h["min_relator"]


def test_an_immediately_trivial_presentation_is_solved_without_expanding():
    s = greedy_search_compact("x", "y", 100)
    assert s["solved"] and s["nodes_explored"] == 1


def test_an_exhausted_search_space_stops_before_the_budget():
    """cap=1 admits almost no states, so the heap empties long before 1000 pops."""
    s = greedy_search_compact("xY", "Xy", MAX_BUDGET, max_relator_length=1)
    assert not s["solved"]
    assert s["nodes_explored"] < MAX_BUDGET


# --- scale safety, argued not asserted ------------------------------------

def test_int32_ids_have_headroom_for_the_largest_projected_search():
    """A 1M-node search discovers ~63.7M states. Every id, depth and heap slot is
    int32. This cannot be exercised under MAX_BUDGET=1000, so assert the margin."""
    projected = est_states(1_000_000)
    assert projected < 2 ** 31 - 1
    assert projected * 1.5 * 2 < 2 ** 31 - 1, "tcap must also fit an int32 index"
    s = GreedyCompactSolver(*_strs(EASY), max_nodes=1000)
    assert s.depth.dtype == np.int32 and s.heap.dtype == np.int32
    assert s.table.dtype == np.int32
    assert s.len1.dtype == np.uint8 and s.len2.dtype == np.uint8


def test_a_relator_length_fits_a_uint8():
    """len1/len2 are uint8, so the cap may never exceed 255."""
    assert row_width(255) == 256
    with pytest.raises(ValueError):
        GreedyCompactSolver("x", "y", max_nodes=10, max_relator_length=256)
    with pytest.raises(ValueError):
        GreedyCompactSolver("x", "y", max_nodes=10, max_relator_length=0)


def test_numba_widens_a_uint8_sum_so_the_heap_total_cannot_wrap():
    """`_less` computes `len1[a] + len2[a]` on two uint8s. A *numpy* scalar sum
    wraps there (200+200 = 144) and the heap order would silently invert for any
    cap above 127. numba widens to int64 instead -- which is the only reason the
    1..255 bound is sound. Nothing else in the suite would notice if a numba
    release changed this, so pin it.
    """
    from numba import njit

    @njit
    def _sum(a, b):
        return a[0] + b[0]

    big = np.array([200], dtype=np.uint8)
    assert _sum(big, big) == 400, "numba wrapped a uint8 sum; cap must drop to 127"
    with np.errstate(over="ignore"):               # the wrap is the point
        assert np.uint8(200) + np.uint8(200) == 144    # what numpy would have done


# --- runner wiring (the SOLVER knob) --------------------------------------

def test_the_runner_dispatches_high_speedup_to_the_named_solver():
    """`run_baseline.greedy_search` is the single seam every search goes through
    -- the pool, the serial memory retry, and the path-recovery re-solve."""
    r1, r2 = _strs(DEEP)
    kw = dict(max_relator_length=48, cyclic_reduce=True)
    compact = rb.greedy_search(r1, r2, 500, high_speedup=True, solver="compact", **kw)
    heavy = rb.greedy_search(r1, r2, 500, high_speedup=True, solver="heavy", **kw)
    ref = greedy_search_compact(r1, r2, 500, **kw)
    assert compact == ref
    for f in ("solved", "nodes_explored", "max_relator_length_expanded"):
        assert compact[f] == heavy[f]


def test_solver_is_ignored_when_high_speedup_is_off():
    """Only the normal solver reconstructs a path, so it must still be reachable."""
    r1, r2 = _strs(EASY)
    for solver in ("compact", "heavy"):
        s = rb.greedy_search(r1, r2, 500, high_speedup=False, solver=solver)
        assert s["solved"] and s["path_moves"], "the normal solver lost its path"


def test_an_unknown_solver_is_rejected_before_a_run_starts():
    with pytest.raises(ValueError, match="compact.*heavy"):
        rb._solver_mode({"SOLVER": "fast"})
    assert rb._solver_mode({}) == "compact"           # the default
    assert rb._solver_mode({"SOLVER": None}) == "compact"
    assert rb._solver_mode({"SOLVER": "HEAVY"}) == "heavy"


def test_the_memory_estimate_follows_the_solver():
    cfg = dict(rb.DEFAULT_CONFIG)
    heavy = rb._est_gb_per_pres({**cfg, "SOLVER": "heavy"}, 1_000_000)
    compact = rb._est_gb_per_pres({**cfg, "SOLVER": "compact"}, 1_000_000)
    assert compact < heavy
    assert heavy / compact == pytest.approx(220 / 80, rel=0.15)
    # an explicit pin still overrides both
    pinned = {**cfg, "SOLVER": "compact", "GB_PER_PRES": 9.0}
    assert rb._est_gb_per_pres(pinned, 1_000_000) == 9.0


def test_the_compact_estimate_is_not_below_what_the_arithmetic_says():
    """Under-provisioning is what made the guard trip on every presentation."""
    n = est_states(1_000_000)
    exact_per_state = (row_width(48) + 10) + (_next_pow2(
        2 * (max(1024, int(n * 1.5)) + 4 * 49 ** 2)) * 4) / n
    assert rb._BYTES_PER_STATE_COMPACT >= exact_per_state


def test_the_compact_solver_is_what_lets_four_workers_fit(monkeypatch):
    """The whole point. 53 GB / 8 cores is a Colab high-RAM runtime."""
    monkeypatch.setattr(rb, "_avail_ram_gb", lambda: 53.0)
    monkeypatch.setattr(rb, "_usable_cores", lambda: 8)
    cfg = {**rb.DEFAULT_CONFIG, "N_WORKERS": 0}
    heavy = rb._auto_workers({**cfg, "SOLVER": "heavy"}, 1_000_000)
    compact = rb._auto_workers({**cfg, "SOLVER": "compact"}, 1_000_000)
    assert heavy == 3, "the status quo that trips the guard"
    assert compact >= 4
    assert compact == 8, "RAM should stop binding; cores become the limit"
