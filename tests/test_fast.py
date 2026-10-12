"""acx.search.fast: step-for-step parity with the spec backend, the cap, the kernels, the speed.

Parity means the same ``solved``, ``pops``, ``path``, ``end``, popped-state
``trace`` and ``PARITY_STATS``. ``PARITY_ROWS`` are 40 MS640 rows at budget
10,000 under both presets (about 70 s, nearly all of it spec; the four heavy
rows are marked ``slow``); the ``slow`` set adds every 16th MS640 row (40 rows,
about 56,000 spec pops, a few minutes).
"""
import time

import pytest

from acx.core.config import SearchConfig
from acx.core.moves import Move, enumerate_moves, source_word, step
from acx.core.priority import get as get_priority
from acx.core.words import Presentation, canonical_word, reduce, rotate, sort_rels
from acx.search import PARITY_STATS, search
from acx.search.fast import children, decode

# 36 rows spread over the 566 MS640 rows whose spec cost (length + s20_mk2 pops at budget 10,000)
# is at most 2,500, plus four rows costing 3,000-7,600 pops: about 22,000 spec pops in all.
PARITY_ROWS = [0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180, 195, 210, 225, 240, 255,
               270, 285, 300, 315, 330, 345, 360, 375, 390, 405, 420, 435, 450, 467, 482, 497, 512,
               528] + [pytest.param(p, marks=pytest.mark.slow) for p in (464, 547, 565, 577)]
FULL_ROWS = list(range(0, 640, 16))


def parity(pres, **kw):
    cfg = SearchConfig(trace=True, **kw)
    a, b = search(pres, cfg), search(pres, cfg.replace(backend="fast"))
    assert (a.solved, a.pops, a.path, a.end) == (b.solved, b.pops, b.path, b.end)
    assert a.trace == b.trace
    assert {k: a.stats[k] for k in PARITY_STATS} == {k: b.stats[k] for k in PARITY_STATS}
    return b


@pytest.mark.parametrize("priority", ["length", "s20_mk2"])
@pytest.mark.parametrize("pid", PARITY_ROWS)
def test_ms640_parity_budget_10k(ms640, pid, priority):
    parity(ms640[pid], priority=priority, budget=10_000)


@pytest.mark.slow
@pytest.mark.parametrize("priority", ["length", "s20_mk2"])
@pytest.mark.parametrize("pid", FULL_ROWS)
def test_ms640_parity_full(ms640, pid, priority):
    parity(ms640[pid], priority=priority, budget=10_000)


@pytest.mark.parametrize("priority", ["length", "s20_mk2"])
@pytest.mark.parametrize("cap", [12, 16, None])
@pytest.mark.parametrize("pid", [120, 322, 600])
def test_caps(ms640, pid, cap, priority):
    r = parity(ms640[pid], priority=priority, cap=cap, budget=400)
    if cap is None:
        assert r.stats["cap_dropped"] == 0


@pytest.mark.parametrize("priority", ["length", "s20_mk2"])
@pytest.mark.parametrize("pid", [5, 120, 322])
def test_linear_reduction(ms640, pid, priority):
    parity(ms640[pid], priority=priority, cyclic=False, cap=12, budget=300)


@pytest.mark.parametrize("kw", [{"cap": 8}, {"cap": None}, {"cyclic": False}])
def test_three_generators(kw):
    parity(Presentation.parse("xyxYXY", "xxyXYY", "zxZyy"), budget=300, **kw)
    r = parity(Presentation.parse("xY", "yZ", "zyX"), budget=200, **kw)
    assert r.solved and r.end.n_gen == 3


def test_s20_mk2_needs_two_generators():
    p = Presentation.parse("xY", "yZ", "zyX")
    for call in (lambda: search(p, priority="s20_mk2", backend="fast"), lambda: children(p.rels, 3, priority="s20_mk2")):
        with pytest.raises(ValueError, match="two generators"):
            call()


def test_start_over_the_cap():
    r = parity(Presentation.parse("xxxxxxyXYXYX", "xyXyXY"), cap=8, budget=10)
    assert r.pops == 1 and r.stats["cap_dropped"] == len(list(enumerate_moves(r.start.rels)))


def test_uncapped_rows_widen():
    """Uncapped rows start at the longest start relator and are re-laid wider on demand."""
    r = parity(Presentation.parse("xyxYXY", "xxyXYYXyyyx"), cap=None, budget=2000)
    assert r.stats["row_width"] > 11 and r.stats["max_total"] > 24


def test_rotations_above_128():
    """Moves are int32 throughout (hcompact's int8 cut positions needed a decode above 127)."""
    p = Presentation.parse("Y" * 130 + "X", "Y").canonical()
    syms, lens, moves, _, _ = children(p.rels, cap=None)
    big = [(m, decode(s, n, 2)) for s, n, m in zip(syms, lens, moves) if max(m[3], m[4]) >= 128]
    assert big and all(step(p, Move(*map(int, m))).rels == c for m, c in big)
    r = search(p, SearchConfig(backend="fast", cap=None, budget=300))
    assert r.solved and r.path_length == 130


def spec_children(rels, cap):
    """Spec's children of one state, as (move, child) in enumeration order."""
    out = []
    for m in enumerate_moves(rels):
        new = reduce(rotate(rels[m.i], m.k1) + rotate(source_word(rels, m), m.k2))
        if cap is None or (len(new) <= cap and all(len(r) <= cap for k, r in enumerate(rels) if k != m.i)):
            out.append((m, sort_rels(rels[:m.i] + (canonical_word(new),) + rels[m.i + 1:])))
    return out


@pytest.mark.parametrize("priority", ["length", "s20_mk2"])
def test_children_kernel(ms640, priority):
    """Every kernel child is spec's child of that move, scored by acx.core.priority; the first
    occurrences agree in order, and the dropped ones are cut-shift repeats."""
    prio = get_priority(priority)
    kept = total = rejected_all = 0
    for pid in (7, 120, 466, 600):
        rels = ms640[pid].canonical().rels
        syms, lens, moves, scores, rejected = children(rels, cap=16, priority=priority)
        got = [(tuple(m), decode(s, n, 2)) for s, n, m in zip(syms, lens, moves)]
        want = spec_children(rels, 16)
        assert set(got) <= set(want)
        assert list(dict.fromkeys(c for _, c in got)) == list(dict.fromkeys(c for _, c in want))
        assert list(scores) == [prio(c) for _, c in got]
        assert rejected == len(list(enumerate_moves(rels))) - len(want)
        kept, total, rejected_all = kept + len(got), total + len(want), rejected_all + rejected
    assert kept < total and rejected_all > 0


def spec_dropped(rels, cap):
    """Spec's over-cap children of one state (canonical, sorted), one per move, in enumeration order."""
    out = []
    for m in enumerate_moves(rels):
        new = reduce(rotate(rels[m.i], m.k1) + rotate(source_word(rels, m), m.k2))
        if len(new) > cap or any(len(r) > cap for k, r in enumerate(rels) if k != m.i):
            out.append(sort_rels(rels[:m.i] + (canonical_word(new),) + rels[m.i + 1:]))
    return out


@pytest.mark.parametrize("priority", ["length", "s20_mk2"])
@pytest.mark.parametrize("cap", [12, 16, 20])
def test_dropped_children_kernel(ms640, priority, cap):
    """``children(drops=True)``: every distinct over-cap child, in first-occurrence order, scored (from the
    reduced relator, before canonicalisation) exactly as acx.core.priority scores the child."""
    prio = get_priority(priority)
    for pid in (7, 120, 466, 600, 620):
        rels = ms640[pid].canonical().rels
        *_, rejected, dsyms, dlens, dscores = children(rels, cap=cap, priority=priority, drops=True)
        got = [decode(s, n, 2) for s, n in zip(dsyms, dlens)]
        want = spec_dropped(rels, cap)
        assert rejected == len(want) >= len(got)
        assert list(dict.fromkeys(got)) == list(dict.fromkeys(want))
        assert list(dscores) == [prio(c) for c in got]


@pytest.mark.slow
def test_speed(ms640, capsys):
    """Report pops/s of both backends on the same rows; fast must be several times faster."""
    rate = {}
    for backend in ("spec", "fast"):
        search(ms640[0], backend=backend)                     # warm (numba compile or cache load)
        pops, t0 = 0, time.perf_counter()
        for pid in (322, 466):
            for priority in ("length", "s20_mk2"):
                pops += search(ms640[pid], priority=priority, budget=2_000, backend=backend).pops
        rate[backend] = pops / (time.perf_counter() - t0)
    with capsys.disabled():
        print(f"\n  pops/s spec {rate['spec']:,.0f}  fast {rate['fast']:,.0f}  "
              f"({rate['fast'] / rate['spec']:.0f}x)")
    assert rate["fast"] > 5 * rate["spec"]
