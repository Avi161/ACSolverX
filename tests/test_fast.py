"""acx.search.fast: step-for-step parity with the spec backend, the cap, the kernels, the speed.

Parity means the same ``solved``, ``pops``, ``path``, ``end``, ``depth``, popped-state
``trace`` and ``PARITY_STATS``. ``PARITY_ROWS`` are 40 MS640 rows at budget
10,000 under both presets (about 70 s, nearly all of it spec; the four heavy
rows are marked ``slow``); the ``slow`` set adds every 16th MS640 row (35 rows,
about 56,000 spec pops, a few minutes).
"""
import random
import time

import numpy as np
import pytest

from acx.core.config import SearchConfig
from acx.core.moves import Move, enumerate_moves, source_word, step
from acx.core.priority import get as get_priority
from acx.core.words import Presentation, canonical_word, reduce, rotate, sort_rels, state_bytes, state_key
from acx.search import PARITY_STATS, search
from acx.search.fast import best_first, children, decode, encode
from acx.search.fast.arrays import Arrays
from acx.search.fast.dedup import find_slot, hash_state, rehash
from acx.search.fast.heap import heap_pop, heap_push
from acx.search.fast.kernels import PRIORITY_IDS, canon_buf, decode_word, reduce_buf, rel_less, score, tie_bytes

# 36 rows spread over the 566 MS640 rows whose spec cost (length + s20_mk2 pops at budget 10,000)
# is at most 2,500, plus four rows costing 3,000-7,600 pops: about 22,000 spec pops in all.
PARITY_ROWS = [0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180, 195, 210, 225, 240, 255,
               270, 285, 300, 315, 330, 345, 360, 375, 390, 405, 420, 435, 450, 467, 482, 497, 512,
               528] + [pytest.param(p, marks=pytest.mark.slow) for p in (464, 547, 565, 577)]
FULL_ROWS = [p for p in range(0, 640, 16) if p not in (0, 240, 464, 512, 528)]     # those run in PARITY_ROWS


def parity(pres, **kw):
    cfg = SearchConfig(trace=True, **kw)
    a, b = search(pres, cfg), search(pres, cfg.replace(backend="fast"))
    assert (a.solved, a.pops, a.path, a.end, a.depth) == (b.solved, b.pops, b.path, b.end, b.depth)
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


def test_a_cap_does_not_size_the_counter_arrays_by_the_budget():
    """The cap counters' per-pop arrays grow with the pops: sized by this budget they would need 30 GiB."""
    start = ("xxYYY", "xyxYXY")
    fast = search(start, SearchConfig(backend="fast", cap=24, budget=4 * 10**9))
    assert (fast.solved, fast.pops) == (True, 22)
    assert fast.pops == search(start, SearchConfig(backend="spec", cap=24, budget=4 * 10**9)).pops


@pytest.mark.parametrize("pid, priority, cap, budget", [(322, "length", 12, 400), (559, "length", 14, 300),
                                                        (630, "s20_mk2", 20, 1_000)])
def test_cap_counter_arrays_double_when_the_pops_outgrow_them(ms640, monkeypatch, pid, priority, cap, budget):
    """Sized for 64 pops at first, the per-pop arrays double on the way, and the result is still spec's. The rows
    are one solved and two out of budget."""
    monkeypatch.setattr(best_first, "FIRST_POPS", 64)
    r = parity(ms640[pid], priority=priority, cap=cap, budget=budget)
    assert r.pops > 2 * 64 and r.stats["cap_dropped"] > 0 and r.stats["cap_would_pop"] > 0


@pytest.mark.slow
def test_cap_counters_past_65536_pops(ms640):
    """MS640 row 639 at cap 18 runs dry after 174,192 pops, so the per-pop arrays double twice from their first size;
    these are the counters it gave when they were sized by the budget."""
    r = search(ms640[639], SearchConfig(backend="fast", priority="length", cap=18, budget=200_000))
    assert not r.solved and r.pops == 174_192
    assert (r.stats["cap_dropped"], r.stats["cap_would_pop"]) == (35_902_544, 2_280_795)


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


def spec_expand(rels, cap):
    """Spec's children of one state, as (move, canonical sorted child) in enumeration order: ``(kept, dropped)``."""
    kept, dropped = [], []
    for m in enumerate_moves(rels):
        new = reduce(rotate(rels[m.i], m.k1) + rotate(source_word(rels, m), m.k2))
        child = sort_rels(rels[:m.i] + (canonical_word(new),) + rels[m.i + 1:])
        over = cap is not None and (len(new) > cap or any(len(r) > cap for k, r in enumerate(rels) if k != m.i))
        (dropped if over else kept).append((m, child))
    return kept, dropped


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
        want = spec_expand(rels, 16)[0]
        assert set(got) <= set(want)
        assert list(dict.fromkeys(c for _, c in got)) == list(dict.fromkeys(c for _, c in want))
        assert list(scores) == [prio(c) for _, c in got]
        assert rejected == len(list(enumerate_moves(rels))) - len(want)
        kept, total, rejected_all = kept + len(got), total + len(want), rejected_all + rejected
    assert kept < total and rejected_all > 0


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
        want = [c for _, c in spec_expand(rels, cap)[1]]
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


def test_decode_word_reads_one_encoded_relator_back():
    for n_gen in (2, 3, 27, 127):
        rels = ((1, -2, n_gen, -n_gen), (2, -1), ())
        syms, lens = encode(rels, n_gen)
        assert tuple(decode_word(syms[r, :lens[r]], n_gen) for r in range(3)) == rels == decode(syms, lens, n_gen)


def test_more_generators_than_the_byte_encoding_holds_is_refused():
    with pytest.raises(ValueError, match="127"):
        encode(((1,), (2,)), 128)
    assert encode(((1,), (2,)), 127)[0].dtype.itemsize == 1


# ---- the kernels, one by one, against the plain-Python words and priorities ----

def random_words(n_gen, count=300, seed=0):
    rng = random.Random(seed)
    letters = [g for k in range(1, n_gen + 1) for g in (k, -k)]
    return [tuple(rng.choice(letters) for _ in range(rng.randint(1, 14))) for _ in range(count)]


@pytest.mark.parametrize("n_gen", [2, 3])
@pytest.mark.parametrize("cyclic", [True, False])
def test_reduce_and_canon_kernels_match_core_words(n_gen, cyclic):
    for w in random_words(n_gen):
        syms, lens = encode((w,), n_gen)
        buf = syms[0].copy()
        lo, m = reduce_buf(buf, lens[0], cyclic)
        reduced = decode(buf[lo:lo + m].reshape(1, -1), [m], n_gen)[0]
        assert reduced == reduce(w, cyclic)
        out = np.zeros_like(buf)
        canon_buf(buf, lo, m, out)
        assert decode(out.reshape(1, -1), [m], n_gen)[0] == canonical_word(reduced)


def test_rel_less_is_the_sort_rels_order():
    words = random_words(2, count=60)
    for a, b in zip(words, words[1:]):
        (sa, la), (sb, lb) = encode((a,), 2), encode((b,), 2)
        before = sort_rels((a, b))[0] == a and a != b
        assert rel_less(sa[0], la[0], sb[0], lb[0]) == before


@pytest.mark.parametrize("priority", ["length", "s20_mk2"])
def test_score_kernel_matches_core_priority(priority):
    """Includes pure powers and a generator that is absent, the cases with special branches."""
    prio = get_priority(priority)
    cases = [((1, 1, 1), (2,)), ((1, 2), (1, -2)), ((1, 1, 2, 2, 1), (2, 2, -1)), ((2, 2), (2, 2, 2))]
    cases += [tuple(random_words(2, count=2, seed=s)) for s in range(40)]
    for rels in cases:
        syms, lens = encode(rels, 2)
        assert score(syms, lens, 2, PRIORITY_IDS[priority]) == prio(rels)


@pytest.mark.parametrize("n_gen", [2, 3])
def test_tie_bytes_kernel_writes_state_bytes(n_gen):
    for w in random_words(n_gen, count=40):
        rels = (w, w[::-1])
        syms, lens = encode(rels, n_gen)
        buf = np.zeros(sum(lens) + len(lens), dtype=np.uint8)
        assert tie_bytes(syms, lens, n_gen, buf, 0) == len(buf)
        assert bytes(buf) == state_bytes(rels, n_gen)


@pytest.mark.parametrize("n_gen", [2, 3])
def test_state_bytes_sort_like_state_key(n_gen):
    """The cap counters compare ``state_bytes`` where the heap compares ``state_key``: one order, a prefix first."""
    words = random_words(n_gen, count=200, seed=1)
    states = {(a, b) for a, b in zip(words, words[1:])}
    states |= {(w[:2], v) for w, v in zip(words, words[2:])}                # a relator that is a prefix of another
    states |= {(w, v) for w, v in zip(words, words[2:])}
    by_key = sorted(states, key=lambda rels: state_key(rels, n_gen))
    assert by_key == sorted(states, key=lambda rels: state_bytes(rels, n_gen))
    assert len(by_key) > 300


# ---- the engine parts: heap order, dedup table, array growth ----

def test_heap_pops_in_priority_depth_order():
    """Ties in (prio, depth) are broken by the symbols, so give each state a distinct 4-symbol word."""
    rng = random.Random(1)
    n = 200
    prio = np.array([rng.randint(0, 5) for _ in range(n)], dtype=np.float64)
    depth = np.array([rng.randint(0, 5) for _ in range(n)], dtype=np.int32)
    arena = np.array([[[(sid >> (2 * t)) & 3 for t in range(4)]] for sid in range(n)], dtype=np.uint8)
    lens = np.full((n, 1), 4, dtype=np.int32)
    heap, size = np.zeros(n, dtype=np.int32), 0
    for sid in range(n):
        size = heap_push(heap, size, sid, prio, depth, arena, lens, 2)
    popped = []
    while size:
        popped.append(int(heap[0]))
        size = heap_pop(heap, size, prio, depth, arena, lens, 2)
    assert sorted(popped) == list(range(n))
    assert [(prio[s], depth[s]) for s in popped] == sorted((prio[s], depth[s]) for s in range(n))


def test_arrays_grow_keeps_states_and_lookups():
    syms, lens = encode(((1, 2, -1, -2), (1, 1, 2)), 2)
    a = Arrays(8, 2, syms.shape[1], track=True)
    a.arena[0], a.lens[0] = syms, lens
    rehash(a.table, a.arena, a.lens, 1)
    b = a.grow(32, syms.shape[1] + 3, 1, 0)
    assert b.capacity == 32 and b.arena.shape == (32, 2, syms.shape[1] + 3)
    row, rlen = b.arena[0], b.lens[0]
    slot = find_slot(b.table, b.arena, b.lens, row, rlen, hash_state(row, rlen))
    assert b.table[slot] == 1
    assert decode(b.arena[0], b.lens[0], 2) == ((1, 2, -1, -2), (1, 1, 2))
