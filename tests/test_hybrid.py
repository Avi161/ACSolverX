"""The hybrid solver (``acx.hybrid``): the source's numbers, backend parity, replayable certificates.

Reference numbers are the source's own runs (``origin/claude/vigilant-babbage-nnbuj0:
research/ac_hashfree_cascade_20260914/records/``, budget 1,000, penalty 5, dyn_ratio 0.5):
MS640 640/640 with 25,064 units (stage B 98, C 328, H 214 rows), and the AC19 Aut-minimal
census 72,779/72,779 with 2,489,726 units, 188 certificates using higher rank. The full census
(about 190 s on 4 workers, certification included) is not run here; its first 2,000 rows are.
"""
import heapq
import random
import sys
import time
from bisect import bisect_left
from types import SimpleNamespace

import numpy as np
import pytest

from acx import data
from acx.aut.whitehead import AUTOS
from acx.core.capcount import blank, fields
from acx.core.words import Presentation, parse
from acx.hybrid import HybridConfig, capwatch, certify, decode_steps, dynrank, encode_steps, solve
from acx.hybrid import search as hybrid_search
from acx.hybrid.cascade import NIELSEN, Budget, Run, cascade, gate_applicable, gate_precheck_key, run_gates
from acx.hybrid.frontier import backend, orbit, over_cap, pack, unpack
from acx.hybrid.pinch import conjugation_forms, from_syllables, syllables
from acx.verify import is_valid, replay

FAST = HybridConfig(certify=False)


def test_nielsen_indices():
    assert [AUTOS[k] for k in NIELSEN] == [tuple(map(parse, p)) for p in (("xy", "y"), ("xY", "y"),
                                                                          ("x", "yx"), ("x", "yX"))]


@pytest.mark.slow
def test_frontier_backends_agree(ms640):
    (sx, _, st), (fx, _, ft) = backend("spec"), backend("fast")
    for pres in ms640[::16]:
        key = pack(pres.reduced().canonical().rels)
        for cap in (None, len(key) - 1, 6, 3):
            assert sx(key, cap) == fx(key, cap)
        for k in range(len(AUTOS)):
            assert st(key, k) == ft(key, k)


def test_ms640(ms640):
    solve(ms640[176], FAST)                                  # compile the kernels
    t = time.perf_counter()
    res = [solve(p, FAST) for p in ms640]
    seconds = time.perf_counter() - t
    print(f"MS640 hybrid: {sum(r.solved for r in res)}/640 in {seconds:.2f} s (source: 2.22-2.4 s)")
    assert all(r.solved and r.kind == "ac_path" for r in res)
    assert sum(r.units for r in res) == 25_064 and max(r.units for r in res) == 283
    assert [sum(r.stage == s for r in res) for s in "BCH"] == [98, 328, 214]
    paths = [certify(p, r.steps) for p, r in zip(ms640, res)]  # each replayed by acx.verify inside
    assert all(is_valid(p, path, normalize=False) for p, path in list(zip(ms640, paths))[::10])


def test_spec_backend_matches_fast(ms640):
    rows = [p for p in ms640 if solve(p, FAST).stage == "H"][::9]
    ac19 = {r.id: r.pres for r in data.load_csv("data/AC19_extended_aut_min.csv")[:1300]}
    rows += [ac19[i] for i in ("ac19_239", "ac19_714", "ac19_1286")]      # higher rank used
    assert len(rows) >= 25
    for p in rows:
        a, b = solve(p, FAST), solve(p, FAST, backend="spec")
        assert (a.units, a.steps) == (b.units, b.steps)


def test_rank_two_cap_is_counted_and_backends_agree(ms640):
    rows = [p for p in ms640 if solve(p, FAST).stage == "H"][::70]
    for cap, budget in ((6, 1000), (14, 1000), (None, 60)):
        for p in rows:
            a, b = (solve(p, FAST, r2_cap=cap, budget=budget, backend=be) for be in ("fast", "spec"))
            assert (a.solved, a.units, a.steps, a.stats["cap_dropped"]) == (b.solved, b.units, b.steps, b.stats["cap_dropped"])
        assert (sum(solve(p, FAST, r2_cap=cap, budget=budget).stats["cap_dropped"] for p in rows) > 0) == (cap is not None)
    with pytest.raises(ValueError):
        HybridConfig(r2_cap="24")


@pytest.mark.slow
def test_ac19_aut_min_sample():
    rows = data.load_csv("data/AC19_extended_aut_min.csv")[:2000]
    res = [solve(r.pres) for r in rows]                      # certify=True: every path replayed
    assert all(r.solved and r.path is not None for r in res)
    assert sum(r.units for r in res) == 67_889
    assert [sum(r.stage == s for r in res) for s in ("terminal", "B", "C", "H")] == [1, 185, 581, 1233]
    stable = [(row, r) for row, r in zip(rows, res) if r.kind == "stable_cert"]
    assert len(stable) == 3
    row, r = stable[0]
    ops = [m["op"] for m in r.path]
    assert "stabilize" in ops and ops.count("stabilize") == ops.count("destabilize")
    assert replay(row.pres, r.path, normalize=False)[-1] == Presentation(2, ((1,), (2,)))
    assert certify(row.pres, decode_steps(encode_steps(r.steps))) == list(r.path)


def test_tampered_certificate_fails(ms640):
    p = ms640[300]
    steps = solve(p, FAST).steps
    with pytest.raises((ValueError, AssertionError)):
        certify(p, steps[:-1])
    with pytest.raises((ValueError, AssertionError)):
        certify(p, steps[1:])


def test_budget_is_respected(ms640):
    res = solve(ms640[636], FAST, budget=30)
    assert not res.solved and res.units <= 30 and res.path is None


# ------------------------------------------------------------------ cap counters (acx.hybrid.capwatch)
PREFIXES = ("cap", "dyn_cap", "slack")
LIMITS = dict(zip(PREFIXES, ("r2_cap", "dyn_cap", "slack")))
TIGHT = [dict(r2_cap=14, dyn_cap=7, slack=4, budget=200), dict(r2_cap=10, dyn_cap=6, slack=3, budget=150),
         dict(r2_cap=8, dyn_cap=4, slack=3, budget=150)]


def counters(res):
    return {p: tuple(res.stats[f] for f in fields(p)) for p in PREFIXES}


def run_with_pops(pres, **kw):
    """``(result, the heap pops in order)``: every ``(priority, depth, kind, state)`` either heap served."""
    log = []

    def pop(h):
        e = heapq.heappop(h)
        log.append((e[0], e[1], e[3][3], e[3][0]))
        return e
    old = hybrid_search.heapq
    hybrid_search.heapq = SimpleNamespace(heappush=heapq.heappush, heappop=pop)
    try:
        return solve(pres, HybridConfig(certify=False, **kw)), log
    finally:
        hybrid_search.heapq = old


def ac19_row(rid):
    return next(r.pres for r in data.load_csv("data/AC19_extended_aut_min.csv")[:1300] if r.id == rid)


def test_every_hybrid_result_carries_the_three_counters(ms640):
    """Cascade-solved rows and budget-less ones too (nothing was cut there)."""
    for pres in ms640[::20]:
        res = solve(pres, FAST)
        assert [res.stats[f] for f in fields("cap")][0] == "parent"
        assert [res.stats[f] for f in fields("dyn_cap")][0] == 8 and [res.stats[f] for f in fields("slack")][0] == 8
        assert res.stats["cap_dropped"] == res.stats["cap_would_pop"] == 0                 # "parent" cannot reject
        assert res.stats["cap_first_bind"] is None and res.stats["cap_needed"] is None
        assert res.stage != "H" or res.stats["dyn_cap_dropped"] + res.stats["slack_dropped"] == res.stats["dyn_rejected"]
    res = solve(ms640[176], FAST, r2_cap=None, dyn_cap=None)
    assert res.stats["cap"] is None and res.stats["dyn_cap"] is None and res.stats["cap_dropped"] == res.stats["dyn_cap_dropped"] == 0
    out = solve(ms640[636], FAST, budget=1)                                               # out of budget in the cascade
    assert not out.solved and counters(out) == {p: tuple(blank(p, c).values()) for p, c in zip(PREFIXES, ("parent", 8, 8))}


def test_parent_cap_rejects_nothing_on_all_of_ms640(ms640):
    """The ``"parent"`` rule (a child relator may not exceed the parent's total) cannot bind: a product is at
    most ``l_i + l_j - 2`` letters, so the rank-two counters are 0 / None by construction (and measured). All
    the default hybrid cuts on MS640 are ``dyn_cap`` and the ceiling (766 moves), none of which would pop."""
    res = [solve(p, FAST) for p in ms640]
    assert sum(r.stats["cap_dropped"] for r in res) == 0 and sum(r.units for r in res) == 25_064
    assert sum(r.stats["dyn_cap_dropped"] + r.stats["slack_dropped"] for r in res) == 766
    assert sum(r.stats["dyn_cap_would_pop"] + r.stats["slack_would_pop"] for r in res) == 0


def sample_keys(ms640, stride=16):
    return [pack(p.reduced().canonical().rels) for p in ms640[::stride]]


@pytest.mark.parametrize("name", ["spec", "fast"])
def test_full_children_are_the_kept_children_plus_the_over_cap_ones(ms640, name):
    """``full`` lists every child; the children a cap keeps are those of ``full`` that ``over_cap`` does not pick,
    in the same order, and each picked one carries its total, its longest relator and the free gate test."""
    expand, full, _ = backend(name)
    picked = 0
    for key in sample_keys(ms640):
        raw, offs, first = full(key)
        everything = expand(key, None)[0]
        assert [raw[a:b] for a, b in zip(offs[:-1], offs[1:])] == [k for k, _ in everything]
        for cap in (len(key) - 1, 8, 6, 3):
            kept, rejected = expand(key, cap)
            d = over_cap((raw, offs, first), cap)
            keep = np.setdiff1d(np.arange(len(everything)), d.pos)
            assert [everything[i] for i in keep] == kept
            assert len(d.pos) <= rejected and (len(d.pos) == 0) == (rejected == 0)
            assert (d.before == [int(np.searchsorted(keep, p)) for p in d.pos]).all()
            for i, pos in enumerate(d.pos.tolist()):
                child = d.raw[d.start[i]:d.end[i]]
                assert child == everything[pos][0]
                assert d.total[i] == len(child) - 1 == sum(map(len, unpack(child)))
                assert d.longest[i] == max(map(len, unpack(child))) > cap
                assert d.flag[i] == gate_precheck_key(child)
            picked += len(d.pos)
    assert picked > 500


def test_backends_list_the_same_children(ms640):
    (_, spec_full, _), (_, fast_full, _) = backend("spec"), backend("fast")
    for key in sample_keys(ms640, 8):
        (r1, o1, f1), (r2, o2, f2) = spec_full(key), fast_full(key)
        assert r1 == r2 and (np.asarray(o1) == np.asarray(o2)).all() and (f1 == f2).all()


def test_the_visited_set_of_rank_two_is_closed_under_the_signed_permutations(ms640):
    transform = backend("fast")[2]
    rows = [p for p in ms640 if solve(p, FAST).stage == "H"][::25]
    for p in rows:
        run = Run(p.rels, 1000)
        assert cascade(run) is None
        search = hybrid_search.BestFirst(run, FAST, 100)
        search.go()
        assert len(search.seen_r2) > 8
        assert all(set(orbit(key, transform)) <= search.seen_r2 for key in search.seen_r2)


def test_gates_act_does_not_depend_on_the_budget(ms640):
    """``capwatch.gates_act``: would the gates solve the pair or spend units? A budget too small to finish also
    shows as acting (``Budget`` or units spent), so the answer is the same at every budget."""
    states = []
    for key in sample_keys(ms640, 4):
        d = over_cap(backend("fast")[1](key), 6)
        states += [unpack(d.raw[d.start[i]:d.end[i]]) for i in np.flatnonzero(d.flag)[:6]]
    acts, idle = [], 0
    for state in states:
        if not gate_applicable(state):
            assert not capwatch.gates_act(pack(state))
            idle += 1
            continue
        for budget in (1, 3, 1000):
            run = Run(state, budget)
            try:
                acted = run_gates(run) or run.units > 0
            except Budget:
                acted = True
            assert acted == capwatch.gates_act(pack(state)), (state, budget)
        acts.append(capwatch.gates_act(pack(state)))
    assert any(acts) and idle > 0


def test_syllables_read_a_cyclic_word_and_conjugation_forms_find_the_pinch_shape():
    rng = random.Random(3)
    for _ in range(200):
        w = [rng.choice((1, -1, 2, -2)) for _ in range(rng.randint(1, 12))]
        w = tuple(x for i, x in enumerate(w) if i == 0 or x != -w[i - 1])
        while len(w) > 1 and w[0] == -w[-1]:
            w = w[1:-1]
        back = from_syllables(syllables(w))
        assert len(back) == len(w) and (not w or any(back == w[k:] + w[:k] for k in range(len(w))))
    word = (1, 1, 2, 2, 2, -1, -1, -2)                       # x^2 y^3 x^-2 y^-1
    assert (1, 2, 2, 3, -1) in conjugation_forms(word)
    assert conjugation_forms((1, 2, 1, 2, 1)) == ()


def test_lazy_entries_come_in_key_order_and_equal_the_eager_list(ms640):
    """The generator behind the dyn pool: every dropped state not offered, once per priority group, in key order,
    each placed between the offered neighbours it would have been pushed between."""
    p = next(p for p in ms640 if solve(p, FAST).stage == "H")
    words = dynrank.normalize(dynrank.defines(dynrank.normalize(Run(p.rels, 9).state))[0][0])
    kept, cut, _ = dynrank.children(words, 3, 99, 2)
    items = [t for t in cut if t[2] > 2]
    assert items and kept
    offered = sorted(state for state, _ in kept)
    penalty, depth, base = 5, 4, 100
    entries = list(capwatch.lazy_entries(depth, base, penalty, 0, words, offered, items))
    states = [e for e in entries if e[3] is not None]
    markers = [e for e in entries if e[3] is None]
    assert markers and [e[0] for e in states] == sorted(e[0] for e in states)
    eager = set()
    for total, _, rank, (i, product) in items:
        state = tuple(sorted(words[:i] + (product,) + words[i + 1:]))
        if state not in offered:
            eager.add((float(total + penalty * (rank - 2)), state))
    assert {(e[0][0], e[3]) for e in states} == eager and len(states) == len(eager)
    for key, _, _, state in states:
        at = base + bisect_left(offered, state)
        assert at < key[2] < at + 1 and key[1] == depth
    for marker in markers:                                    # a marker bounds its group from below
        later = [e for e in entries[entries.index(marker) + 1:] if e[0][0] == marker[0][0]]
        assert all(marker[0] <= e[0] for e in later)


def backends_agree_on_counters(ms640, configs, stride):
    rows = [p for p in ms640 if solve(p, FAST).stage == "H"][::stride]
    bound = 0
    for kw in configs:
        for p in rows:
            a, b = (solve(p, FAST, backend=be, **kw) for be in ("fast", "spec"))
            assert (a.solved, a.units, a.steps) == (b.solved, b.units, b.steps) and counters(a) == counters(b)
            bound += any(a.stats[f"{q}_would_pop"] for q in PREFIXES)
    return bound


def test_counters_agree_between_the_backends(ms640):
    assert backends_agree_on_counters(ms640, TIGHT[:1], 35) >= 1


@pytest.mark.slow
def test_counters_agree_between_the_backends_on_many_rows(ms640):
    assert backends_agree_on_counters(ms640, TIGHT, 17) >= 10


def test_counters_leave_the_search_alone(ms640):
    """They only observe: a tightly capped run spends the same units as it did before the counters (golden)."""
    res = [solve(p, FAST, r2_cap=10, dyn_cap=6, slack=3, budget=150) for p in ms640[176::48]]
    assert (sum(r.units for r in res), sum(r.solved for r in res)) == (547, 9)


def zero_means_same(ms640, configs, stride):
    """``(rows with all counters 0, rows nonzero, zero rows that did drop, nonzero rows whose pop order moves)``.

    With all three counters at 0, raising every limit pops the same states in the same order (the results are
    equal); this is asserted. A nonzero count only says the run may change: raising each binding limit to its
    ``_needed`` is counted if it moves the pop order."""
    rows = [p for p in ms640 if solve(p, FAST).stage == "H"][::stride]
    zero = nonzero = dropped_zero = moved = 0
    for kw in configs:
        for p in rows:
            a, la = run_with_pops(p, **kw)
            if not any(a.stats[f"{q}_would_pop"] for q in PREFIXES):
                b, lb = run_with_pops(p, **dict(kw, r2_cap=None, dyn_cap=None, slack=40))
                zero += 1
                dropped_zero += any(a.stats[f"{q}_dropped"] for q in PREFIXES)
                assert (a.solved, a.units, a.steps) == (b.solved, b.units, b.steps) and la == lb[:len(la)]
                continue
            nonzero += 1
            for q in PREFIXES:
                if a.stats[f"{q}_would_pop"]:
                    c, lc = run_with_pops(p, **dict(kw, **{LIMITS[q]: a.stats[f"{q}_needed"]}))
                    n = min(len(la), len(lc))
                    moved += la[:n] != lc[:n]
    return zero, nonzero, dropped_zero, moved


def test_zero_would_pop_means_the_run_does_not_change(ms640):
    zero, nonzero, dropped_zero, moved = zero_means_same(ms640, TIGHT[:1], 6)
    assert zero > 25 and nonzero >= 1 and dropped_zero > 10 and moved >= 1


@pytest.mark.slow
def test_zero_would_pop_means_the_run_does_not_change_on_tight_limits(ms640):
    """Limits tight enough that many rows bind (about 4 minutes): no false zero among 108 runs."""
    zero, nonzero, dropped_zero, moved = zero_means_same(ms640, TIGHT, 6)
    assert zero > 40 and nonzero > 20 and moved > 15


def test_dyn_cap_binds_on_ac19_rows_and_needed_is_the_smallest_cap_that_changes_the_run():
    """The default ``dyn_cap`` 8 drops states that would be popped on higher-rank rows; below ``dyn_cap_needed``
    the run is the same, at it the run changes (units and certificate). Defaults, so the published numbers stand."""
    for rid, bind, needed, units in (("ac19_239", 110, 11, (150, 153)), ("ac19_714", 35, 11, (59, 63))):
        pres = ac19_row(rid)
        base = solve(pres, FAST)
        assert (base.stats["dyn_cap_would_pop"] > 0, base.stats["dyn_cap_first_bind"], base.stats["dyn_cap_needed"]) == (True, bind, needed)
        assert base.stats["cap_would_pop"] == base.stats["slack_would_pop"] == 0 and base.units == units[0]
        below, at = solve(pres, FAST, dyn_cap=needed - 1), solve(pres, FAST, dyn_cap=needed)
        assert (below.units, below.steps) == (base.units, base.steps)
        assert at.units == units[1] and at.steps != base.steps


def test_ceiling_counter_counts_a_dropped_state_that_would_pop():
    pres = ac19_row("ac19_1286")
    tight, loose = solve(pres, FAST, dyn_cap=None, slack=0), solve(pres, FAST, dyn_cap=None)
    assert tight.stats["slack_dropped"] > 1000 and (tight.stats["slack_would_pop"], tight.stats["slack_first_bind"],
                                                    tight.stats["slack_needed"]) == (1, 24, 1)
    assert tight.stats["slack_dropped_min_total"] > 0 and counters(loose)["slack"][3] == 0
    assert solve(pres, FAST, dyn_cap=None, slack=1).stats["slack_would_pop"] == 0


# ------------------------------------------------------------------ cost of the rank-two counter
def calls_and_seconds(pres, watch_cap, **kw):
    """Python-level calls and CPU seconds of one solve, with the ``r2_cap`` counter on or off."""
    old = capwatch.Watch.has
    capwatch.Watch.has = lambda self, name: (name != "cap" or watch_cap) and old(self, name)
    n = 0

    def prof(frame, event, arg):
        nonlocal n
        n += event in ("call", "c_call")
    try:
        t = time.process_time()
        solve(pres, FAST, **kw)
        seconds = time.process_time() - t
        sys.setprofile(prof)
        solve(pres, FAST, **kw)
    finally:
        sys.setprofile(None)
        capwatch.Watch.has = old
    return n, seconds


def test_integer_r2_cap_counters_cost_under_ten_percent(ms640):
    """A tight integer ``r2_cap`` drops hundreds of moves per pop; counting them must stay cheap (the first
    version was 5x slower). Python calls are the deterministic measure (within 10%), CPU time the sanity check
    (within 60%, loose because the machine is shared; about 20% is measured at ``r2_cap`` 8)."""
    solve(ms640[380], FAST)
    kw = dict(r2_cap=8, budget=150)
    for i in (380, 602):
        on, t_on = calls_and_seconds(ms640[i], True, **kw)
        off, t_off = calls_and_seconds(ms640[i], False, **kw)
        assert solve(ms640[i], FAST, **kw).stats["cap_dropped"] > 10_000
        assert on <= 1.10 * off, (i, on, off)
        assert t_on <= 1.60 * t_off, (i, t_on, t_off)
