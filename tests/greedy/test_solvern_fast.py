"""``search_n_fast`` — full-result parity with ``search_n``, paths included.

The fast solver's contract is stronger than the 2-gen HIGH_SPEEDUP pair's:
``search_n`` tracks min/max by deterministic first-crossing (no set
tie-breaks), and the fast twin keeps parent/move pointers, so EVERY field of
the return dict must be equal — solved, nodes, all length stats, the min/max
relator *strings*, and the full path. These tests assert whole-dict equality,
never a field subset.

The kernel-level tests pin the two traps the design review called out:
the relator sort must be length-first (``_sort_key`` = ``(len, booth-lex)``;
booth-lex alone misorders e.g. ``x`` vs ``ZZ``), and unpacking must promote
the uint8 byte to a signed int before negating.

All budgets are <= 1000 (the local hard ceiling); production runs on Colab.
"""

import random

import numpy as np
import pytest

from experiments.greedy_tests.fixtures.presentations import ak, ms640
from experiments.greedy_tests.spec import search as spec_search
from experiments.greedy_tests.spec.invariants import abs_det
from experiments.greedy_tests.spec.presentation import Presentation, trivial
from experiments.stable_ac import solvern
from experiments.stable_ac.solvern_fast import (
    _pack_key,
    _pack_state_nj,
    _solved,
    _unpack_key,
    _unpack_state_nj,
    expand_node_packed_nj,
    search_n_fast,
)

#: Branch-A no-CoV targets <x,y,z | r1, r2, Z.w> — several w, same shape the
#: production sweep searches.
def _nocov(idx, w):
    return Presentation.from_strs(*ms640([idx])[0].to_strs(), "Z" + w, n_gen=3)


NOCOV_CASES = [
    (_nocov(0, "xy"), "nocov-ms640.0-xy"),
    (_nocov(0, "x"), "nocov-ms640.0-x"),
    (_nocov(165, "xyy"), "nocov-ms640.165-xyy"),
    (_nocov(7, "yX"), "nocov-ms640.7-yX"),
]

#: a state whose expansion produces an EMPTY child relator (r2 = r1^-1, so a
#: seam-cancelling concatenation reduces to the empty word).
EMPTY_CHILD = Presentation(3, ((1, 2), (-2, -1), (3, 1)))

#: three genuinely-interacting relators (source index j is load-bearing).
THREE_REL = Presentation(3, ((1, 2), (-2, 3), (-3, -1)))

#: start relator lengths 4/5/8: caps 5/6/7 straddle the cap boundary, the one
#: regime where the hoisted over-cap guard bites (same corpus as test_solvern).
OVER_CAP_START = Presentation.from_strs(
    *ms640([165])[0].to_strs(), "Z" + "xyy", n_gen=3)


def _assert_identical(pres, budget, cap=64, cyclic=True):
    a = solvern.search_n(pres, budget, cap=cap, cyclic=cyclic)
    b = search_n_fast(pres, budget, cap=cap, cyclic=cyclic)
    assert a == b, {k: (a[k], b[k]) for k in a if a[k] != b[k]}
    return a


# -- whole-dict parity, n_gen = 2 through 5 ----------------------------------


@pytest.mark.parametrize("idx", range(10))
def test_parity_at_two_generators(idx):
    _assert_identical(ms640([idx])[0], 1000, cap=24)


@pytest.mark.parametrize(
    "pres", [c[0] for c in NOCOV_CASES], ids=[c[1] for c in NOCOV_CASES])
def test_parity_at_three_generators_nocov(pres):
    _assert_identical(pres, 1000, cap=64)


def test_parity_on_stabilized_ak3():
    _assert_identical(ak(3).stabilize(), 1000, cap=64)


def test_parity_at_three_interacting_relators():
    _assert_identical(THREE_REL, 500, cap=24)


def test_parity_at_four_generators():
    _assert_identical(ms640([0])[0].stabilize().stabilize(), 800, cap=64)


def test_parity_at_five_generators():
    p = ms640([0])[0].stabilize().stabilize().stabilize()
    _assert_identical(p, 500, cap=64)


def test_parity_without_cyclic_reduction():
    _assert_identical(_nocov(0, "xy"), 800, cap=64, cyclic=False)
    _assert_identical(ms640([3])[0], 800, cap=24, cyclic=False)


@pytest.mark.parametrize("cap", [5, 6, 7])
def test_parity_when_the_start_carries_an_over_cap_relator(cap):
    _assert_identical(OVER_CAP_START, 800, cap=cap)


def test_parity_when_a_child_relator_reduces_to_empty():
    r = _assert_identical(EMPTY_CHILD, 300, cap=24)
    # non-vacuous: r2 = r1^-1, so a seam-cancelling concatenation empties a
    # relator and the min state must actually carry an empty rendered word.
    assert "" in r["min_relator"]


@pytest.mark.parametrize("budget", [1, 50, 200, 1000])
def test_parity_across_budgets(budget):
    _assert_identical(_nocov(7, "yX"), budget, cap=64)


def test_parity_on_an_already_trivial_start():
    for n in (2, 3, 4):
        r = _assert_identical(trivial(n), 10, cap=24)
        assert r["solved"] and r["nodes_explored"] == 1 and r["path"] != []


def test_the_min_and_max_stats_are_pinned_non_vacuously():
    """The parity corpus must exercise all three stat trackers: a case where
    min moves below the start, max moves above it, and the max popped state
    (max_expanded) stays strictly below the max discovered state."""
    r = solvern.search_n(_nocov(7, "yX"), 1000, cap=64)
    start_total = sum(len(w) for w in _nocov(7, "yX").canonical().relators)
    assert r["min_relator_length"] < start_total
    assert r["max_relator_length"] > start_total
    assert r["max_relator_length_expanded"] < r["max_relator_length"]


# -- trace equality against the pure-Python spec (independent oracle) --------


@pytest.mark.parametrize("pres, budget", [
    (ms640([0])[0], 500),
    (_nocov(0, "xy"), 500),
    (ak(3).stabilize(), 500),
])
def test_trace_equality_vs_spec(pres, budget):
    sp = spec_search.search(pres, budget, cap=24, cyclic=True)
    me = search_n_fast(pres, budget, cap=24, cyclic=True)
    for f in ("solved", "nodes_explored", "path_length", "min_relator_length",
              "max_relator_length", "max_relator_length_expanded",
              "min_relator", "max_relator", "max_relator_expanded"):
        assert sp[f] == me[f], f
    assert [tuple(mv) for mv in sp["path_moves"]] == [
        solvern.str_to_move(m) for m in me["path_moves"]]


# -- the packed-state codec ---------------------------------------------------


def _random_state(rng, n_gen, n_rel, allow_empty=True):
    words = []
    for _ in range(n_rel):
        lo = 0 if allow_empty else 1
        length = rng.randint(lo, 12)
        words.append(tuple(
            rng.choice([-1, 1]) * rng.randint(1, n_gen) for _ in range(length)))
    return tuple(words)


def _to_arrays(key):
    n_rel = len(key)
    width = max((len(w) for w in key), default=0)
    words = np.zeros((n_rel, max(width, 1)), dtype=np.int8)
    lens = np.zeros(n_rel, dtype=np.int64)
    for r, w in enumerate(key):
        lens[r] = len(w)
        for t, g in enumerate(w):
            words[r, t] = g
    return words, lens, n_rel


def test_pack_kernel_matches_tiebreak_on_a_fuzz_corpus():
    """_pack_state_nj must equal solvern._tiebreak byte-for-byte — the packed
    key doubles as the heap tie-break, so a drift changes the pop order."""
    rng = random.Random(20260714)
    for _ in range(400):
        n_gen = rng.choice([2, 3, 4, 8, 26])
        n_rel = rng.randint(2, 5)
        key = _random_state(rng, n_gen, n_rel)
        words, lens, nr = _to_arrays(key)
        packed = bytes(_pack_state_nj(words, lens, nr))
        assert packed == solvern._tiebreak(key), key


def test_pack_unpack_round_trips_including_empty_and_identical_relators():
    rng = random.Random(99)
    corpus = [_random_state(rng, rng.choice([2, 3, 5, 26]), rng.randint(2, 5))
              for _ in range(300)]
    corpus += [
        ((), (1, 2), (-2,)),                      # leading empty segment
        ((1,), (), ()),                           # adjacent empty segments
        ((1, 2), (1, 2), (1, 2)),                 # identical relators
        ((-26, 26), (26,)),                       # extreme generator index
    ]
    for key in corpus:
        packed = _pack_key(key)
        assert _unpack_key(packed) == key
        words, lens = _unpack_state_nj(
            np.frombuffer(packed, dtype=np.uint8), len(key))
        rebuilt = tuple(tuple(int(g) for g in words[r, :lens[r]])
                        for r in range(len(key)))
        assert rebuilt == key


def test_unpack_negates_inverse_symbols_with_a_signed_cast():
    # b=5 encodes -5; a uint8 negation would wrap to 251 / crash the codec.
    key = ((-5,), (-26, 26, -1))
    words, lens = _unpack_state_nj(
        np.frombuffer(_pack_key(key), dtype=np.uint8), 2)
    assert int(words[0, 0]) == -5
    assert [int(g) for g in words[1, :3]] == [-26, 26, -1]


def test_solved_predicate_matches_all_relators_length_one():
    assert _solved(_pack_key(((1,), (2,), (3,))), 3)
    assert not _solved(_pack_key(((1, 2), (3,))), 2)
    # total == n_rel but one relator empty: NOT solved (lens 0/1/2).
    assert not _solved(_pack_key(((), (1,), (2, 3))), 3)
    assert not _solved(_pack_key(((1,), (2,))), 3)


# -- the fused expansion kernel ----------------------------------------------


def _children_via_search_n_logic(key, cap, cyclic):
    """search_n's inner loop, verbatim, as an emission-order oracle."""
    n_rel = len(key)
    arrs = [np.array([int(g) for g in r], dtype=np.int8) for r in key]
    over = [len(r) > cap for r in key]
    n_over = sum(over)
    out = []
    for i in range(n_rel):
        if len(key[i]) == 0 or n_over - over[i] > 0:
            continue
        for j in range(n_rel):
            if j == i or len(key[j]) == 0:
                continue
            for s in (1, -1):
                oj = arrs[j] if s == 1 else solvern.inverse_nj(arrs[j])
                words, lens, k1s, k2s, count = solvern.expand_pair_nj(
                    arrs[i], oj, cap, cyclic)
                for c in range(count):
                    canon_i = solvern.canonical_word_nj(
                        words[c, :lens[c]].copy())
                    child = list(key)
                    child[i] = tuple(int(x) for x in canon_i)
                    child.sort(key=solvern._sort_key)
                    out.append((solvern._tiebreak(tuple(child)),
                                sum(len(r) for r in child),
                                (i, j, s, int(k1s[c]), int(k2s[c]))))
    return out


#: kernel corpus: fixtures + states crafted so the child sort must order
#: relators whose LENGTH order contradicts their booth-lex order (x vs ZZ:
#: booth-lex alone puts ZZ first, _sort_key puts x first).
KERNEL_CORPUS = [
    ms640([0])[0].canonical().relators,
    ms640([165])[0].canonical().relators,
    _nocov(0, "xy").canonical().relators,
    ak(3).stabilize().canonical().relators,
    THREE_REL.canonical().relators,
    EMPTY_CHILD.canonical().relators,
    ms640([0])[0].stabilize().stabilize().canonical().relators,
    ((1,), (-3, -3), (2, 3)),          # inherits x alongside ZZ
    ((-3, -3), (1, 3), (2,)),          # same trap, different target slots
    ((1, 2), (1, 2), (3, 1)),          # identical relators in one state
]


@pytest.mark.parametrize("cap", [5, 24, 64])
@pytest.mark.parametrize("key", KERNEL_CORPUS,
                         ids=[f"state{n}" for n in range(len(KERNEL_CORPUS))])
def test_kernel_children_match_search_n_logic_exactly(key, cap):
    """Same children, same packed bytes, same totals, same moves, SAME ORDER —
    the emission order drives the visited-set evolution and min/max crossings."""
    words, lens, n_rel = _to_arrays(key)
    rows, row_lens, totals, moves, count = expand_node_packed_nj(
        words, lens, n_rel, cap, True)
    kernel = [(rows[c, :row_lens[c]].tobytes(), int(totals[c]),
               tuple(int(v) for v in moves[c])) for c in range(count)]
    assert kernel == _children_via_search_n_logic(key, cap, True)


def test_kernel_corpus_actually_contains_the_length_first_trap():
    """Vacuity guard: at least one corpus state must carry a relator pair
    whose booth-lex-only order contradicts the length-first order."""
    def contradicts(key):
        for a in key:
            for b in key:
                if len(a) < len(b) and a and b and abs(a[0]) < abs(b[0]):
                    return True
        return False
    assert any(contradicts(k) for k in KERNEL_CORPUS)


def test_the_kernel_expander_preserves_abs_det():
    """The independent oracle the contract suite applies to every solver,
    wired directly to the fused expander (children decoded from its bytes)."""
    for key in KERNEL_CORPUS:
        n_gen = max((abs(g) for r in key for g in r), default=1)
        parent = Presentation(n_gen, key)
        d = abs_det(parent)
        words, lens, n_rel = _to_arrays(key)
        rows, row_lens, totals, moves, count = expand_node_packed_nj(
            words, lens, n_rel, 64, True)
        assert count > 0
        for c in range(count):
            child_key = _unpack_key(rows[c, :row_lens[c]].tobytes())
            assert abs_det(Presentation(n_gen, child_key)) == d, key


# -- misc contract properties --------------------------------------------------


def test_determinism_across_runs():
    p = _nocov(165, "xyy")
    assert search_n_fast(p, 800, cap=64) == search_n_fast(p, 800, cap=64)


def test_budget_is_respected():
    r = search_n_fast(ak(3).stabilize(), 300, cap=64)
    assert 1 <= r["nodes_explored"] <= 300


def test_the_progress_callback_is_result_neutral():
    p = ak(3).stabilize()
    quiet = search_n_fast(p, 1000, cap=64)
    seen = []
    loud = search_n_fast(p, 1000, cap=64, progress=seen.append)
    assert quiet == loud
    assert all(n % 1024 == 0 for n in seen)


def test_solved_paths_replay_to_trivial_through_solvern():
    """The fast path certifies through the same replay decoder the verifier
    family uses — moves only, never stored states."""
    p = _nocov(0, "xy")
    r = search_n_fast(p, 500, cap=64)
    assert r["solved"]
    states = solvern.moves_to_states(p.relators, r["path_moves"])
    assert states == r["path_words"]
    assert all(len(w) == 1 for w in states[-1])
