"""The hybrid solver (``acx.hybrid``): the source's numbers, backend parity, replayable certificates.

Reference numbers are the source's own runs (``origin/claude/vigilant-babbage-nnbuj0:
research/ac_hashfree_cascade_20260914/records/``, budget 1,000, penalty 5, dyn_ratio 0.5):
MS640 640/640 with 25,064 units (stage B 98, C 328, H 214 rows), and the AC19 Aut-minimal
census 72,779/72,779 with 2,489,726 units, 188 certificates using higher rank. The full census
(about 190 s on 4 workers, certification included) is not run here; its first 2,000 rows are.
"""
import heapq
import random
import time
from types import SimpleNamespace

import pytest

from acx import data
from acx.aut.whitehead import AUTOS
from acx.core.words import Presentation, canonical_rels, parse
from acx.hybrid import HybridConfig, certify, decode_steps, encode_steps, solve
from acx.hybrid.cascade import NIELSEN
from acx.core.capcount import blank, fields
from acx.hybrid import solver as hybrid_solver
from acx.hybrid.cascade import gate_precheck_key
from acx.hybrid.frontier import backend, pack, pair_precheck, spec_dropped, unpack
from acx.verify import is_valid, replay

FAST = HybridConfig(certify=False)


def test_nielsen_indices():
    assert [AUTOS[k] for k in NIELSEN] == [tuple(map(parse, p)) for p in (("xy", "y"), ("xY", "y"),
                                                                          ("x", "yx"), ("x", "yX"))]


@pytest.mark.slow
def test_frontier_backends_agree(ms640):
    (sx, st), (fx, ft) = backend("spec"), backend("fast")
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
    old = hybrid_solver.heapq
    hybrid_solver.heapq = SimpleNamespace(heappush=heapq.heappush, heappop=pop)
    try:
        return solve(pres, HybridConfig(certify=False, **kw)), log
    finally:
        hybrid_solver.heapq = old


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


def test_spec_dropped_lists_every_rejected_move_of_both_backends(ms640):
    (sx, _), (fx, _) = backend("spec"), backend("fast")
    seen = 0
    for pres in ms640[::16]:
        key = pack(pres.reduced().canonical().rels)
        for cap in (None, len(key) - 1, 8, 6, 3):
            lost = spec_dropped(key, cap)
            kept, rejected = sx(key, cap)
            assert len(lost) == rejected == fx(key, cap)[1]
            orders = [(mv.i, -mv.s, mv.k1, mv.k2) for _, mv in kept]
            assert orders == sorted(orders) and [o for o, *_ in lost] == sorted(o for o, *_ in lost)
            assert not set(orders) & {o for o, *_ in lost}
            assert cap is None or all(longest > cap for *_, longest in lost)
            assert cap is None or all(max(map(len, k.split(b"\0"))) <= cap for k, _ in kept)
            for _, pair, total, longest in lost:
                assert total == sum(map(len, pair)) and longest == max(map(len, pair))
                assert canonical_rels(pair) == canonical_rels(unpack(pack(canonical_rels(pair))))
            seen += len(lost)
    assert seen > 500


def test_pair_precheck_is_the_free_gate_test_without_packing(ms640):
    rng = random.Random(5)
    n = 0
    for pres in ms640[::5]:
        for _ in range(20):
            pair = tuple(tuple(rng.choice((1, -1, 2, -2)) for _ in range(rng.randint(1, 9))) for _ in range(2))
            assert pair_precheck(pair) == gate_precheck_key(pack(pair))
            n += pair_precheck(pair)
        assert pair_precheck(pres.rels) == gate_precheck_key(pack(pres.rels))
    assert 0 < n < 128 * 20


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
