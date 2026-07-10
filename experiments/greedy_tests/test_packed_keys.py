"""The packed-bytes state key.

``GreedyHeavySolver`` keys states by ``bytes``; ``GreedyBaselineSolver`` keys them
by ``(str, str)``. The heap orders on ``(priority, depth, key)``, so the two
solvers pop in the same order **only if the two key types sort identically**.
That single invariant is what makes ``nodes_explored`` comparable between them,
and it is the property tested here -- exhaustively, and at ``n_gen = 3`` via the
spec's code table so the stable extension inherits the coverage.
"""

import itertools

import numpy as np
import pytest

from experiments.search.greedy_baseline import (
    _CODE_TABLE, _CODE_TO_CHAR, _KEY_SEP, key_lengths, pack_key, str_to_arr,
    unpack_arrays, unpack_key,
)
from experiments.search.greedy_compact import (
    _CHAR_TO_CODE, GreedyCompactSolver, pack_row, row_width,
)
from experiments.greedy_tests.fixtures.presentations import all_words
from experiments.greedy_tests.spec import keys as spec_keys
from experiments.greedy_tests.spec.words import str_to_word, symbol_to_char, word_to_str

WORDS_3 = [word_to_str(w) for w in all_words(2, 3)]     # 85 words, includes ''


def test_code_table_matches_the_spec_at_n_gen_2():
    table = spec_keys.code_table(2)
    assert {symbol_to_char(g): c for g, c in table.items()} == \
        {ch: c for c, ch in _CODE_TO_CHAR.items()}
    # _CODE_TABLE is indexed by 2*gen_bit + sign_bit -> Y=0, y=1, X=2, x=3
    assert list(_CODE_TABLE) == [table[-2], table[2], table[-1], table[1]]


def test_separator_sorts_below_every_symbol_code():
    for n_gen in (2, 3):
        assert 0 not in spec_keys.code_table(n_gen).values()
        assert min(spec_keys.code_table(n_gen).values()) > _KEY_SEP[0]


def test_pack_unpack_round_trip():
    for a, b in itertools.islice(itertools.product(WORDS_3, repeat=2), 0, None, 7):
        key = pack_key(str_to_arr(a), str_to_arr(b))
        assert unpack_key(key) == (a, b)


def test_key_lengths_reads_lengths_without_decoding():
    for a, b in itertools.islice(itertools.product(WORDS_3, repeat=2), 0, None, 11):
        key = pack_key(str_to_arr(a), str_to_arr(b))
        assert key_lengths(key) == (len(a), len(b))


def test_unpack_arrays_agrees_with_str_to_arr():
    for a, b in itertools.islice(itertools.product(WORDS_3, repeat=2), 0, None, 13):
        k1, k2 = unpack_arrays(pack_key(str_to_arr(a), str_to_arr(b)))
        assert np.array_equal(k1, str_to_arr(a))
        assert np.array_equal(k2, str_to_arr(b))


def test_packed_keys_sort_exactly_like_string_tuples():
    """The load-bearing invariant. 85*85 = 7225 pairs, including empty relators."""
    pairs = list(itertools.product(WORDS_3, repeat=2))
    packed = {pack_key(str_to_arr(a), str_to_arr(b)): (a, b) for a, b in pairs}
    assert len(packed) == len(pairs), "packing must be injective"

    by_bytes = [packed[k] for k in sorted(packed)]
    by_tuple = sorted(pairs)
    assert by_bytes == by_tuple


@pytest.mark.parametrize("n_gen", [2, 3])
@pytest.mark.stable
def test_spec_pack_sorts_like_string_tuples_for_any_n_gen(n_gen):
    """The same invariant, stated generally: the stable solver must preserve it."""
    words = all_words(n_gen, 2)
    rels = list(itertools.product(words, repeat=2))
    packed = {spec_keys.pack(r, n_gen): r for r in rels}
    assert len(packed) == len(rels)

    by_bytes = [packed[k] for k in sorted(packed)]
    by_str = sorted(rels, key=lambda r: tuple(word_to_str(w) for w in r))
    assert by_bytes == by_str


@pytest.mark.stable
def test_spec_pack_matches_pack_key_at_n_gen_2():
    for a, b in itertools.islice(itertools.product(WORDS_3, repeat=2), 0, None, 17):
        rel = (str_to_word(a), str_to_word(b))
        assert spec_keys.pack(rel, 2) == pack_key(str_to_arr(a), str_to_arr(b))


@pytest.mark.stable
def test_spec_key_supports_three_relators():
    """A 3-relator key needs two separators; ``key.index(0)`` would find only the first."""
    rel = ((1, 2), (-1,), (3,))
    key = spec_keys.pack(rel, 3)
    assert key.count(0) == 2
    assert spec_keys.unpack(key, 3, 3) == rel
    assert spec_keys.key_lengths(key, 3) == (2, 1, 1)
    with pytest.raises(ValueError):
        spec_keys.unpack(key, 3, 2)


# ---------------------------------------------------------------------------
# The compact solver's nibble row. Same invariant, third encoding.
#
# ``GreedyCompactSolver`` drops the bytes key entirely: a state is a fixed-width,
# zero-padded row of 4-bit codes, r1's region then r2's, each byte-aligned. The
# heap tie-break is a memcmp over that row, so it must sort exactly like the
# packed bytes key -- and therefore like ``(r1_str, r2_str)``.
# ---------------------------------------------------------------------------

CAPS = [4, 24, 25, 48]      # 25 is odd: its region carries a trailing pad nibble


def _deep_corpus(cap, seed=20260709):
    """Cap-length words, their proper prefixes, and case-differing tails.

    The shallow 7225 pairs above never exercise a full-width row, a pad nibble,
    or a difference in the final symbol -- which is exactly where a fixed-width
    encoding breaks. ``ms_reps_unsolved`` rows 15 and 16 differ only in the case
    of r1's last letter (``YYYXyyX`` vs ``YYYXyyx``); that specimen is included.
    """
    rng = np.random.default_rng(seed)
    alphabet = "XYxy"
    words = ["", "X", "Y", "x", "y", "YYYXyyX", "YYYXyyx"]
    for _ in range(24):
        w = "".join(rng.choice(list(alphabet), size=cap))
        words += [w, w[:-1], w[:-1] + ("x" if w[-1] == "X" else "X")]
        words += [w[: cap // 2], w[: cap // 2] + "y"]
    return sorted({w for w in words if len(w) <= cap})


@pytest.mark.parametrize("cap", CAPS)
def test_the_nibble_row_is_injective(cap):
    words = _deep_corpus(cap)
    pairs = list(itertools.product(words[:40], repeat=2))
    rows = {pack_row(a, b, cap): (a, b) for a, b in pairs}
    assert len(rows) == len(pairs), "two states packed to the same row"


@pytest.mark.parametrize("cap", CAPS)
def test_nibble_rows_sort_exactly_like_string_tuples(cap):
    """THE load-bearing invariant for the compact solver's heap tie-break."""
    words = _deep_corpus(cap)
    pairs = list(itertools.product(words[:40], repeat=2))
    rows = {pack_row(a, b, cap): (a, b) for a, b in pairs}
    assert [rows[k] for k in sorted(rows)] == sorted(pairs)


@pytest.mark.parametrize("cap", CAPS)
def test_nibble_rows_sort_exactly_like_the_packed_bytes_key(cap):
    """Transitively: compact pops in the same order as heavy, not merely a valid one."""
    words = _deep_corpus(cap)
    pairs = list(itertools.product(words[:40], repeat=2))
    by_row = sorted(pairs, key=lambda p: pack_row(p[0], p[1], cap))
    by_key = sorted(pairs, key=lambda p: pack_key(str_to_arr(p[0]), str_to_arr(p[1])))
    assert by_row == by_key


def test_the_shallow_corpus_also_sorts_identically():
    """The original 7225 pairs, now through the nibble row."""
    pairs = list(itertools.product(WORDS_3, repeat=2))
    rows = {pack_row(a, b, 24): (a, b) for a, b in pairs}
    assert len(rows) == len(pairs)
    assert [rows[k] for k in sorted(rows)] == sorted(pairs)


def test_a_pad_nibble_sorts_below_every_symbol_code():
    """Why shorter-prefix-is-smaller survives fixed-width zero padding."""
    assert min(_CHAR_TO_CODE.values()) > 0
    assert pack_row("X", "", 4) < pack_row("Xx", "", 4)        # prefix is smaller
    assert pack_row("X", "", 4) < pack_row("Y", "", 4)         # X < Y
    assert pack_row("Xx", "", 4) > pack_row("X", "y", 4)       # r1 dominates r2


def test_r2_is_byte_aligned_so_a_short_r1_cannot_shift_it():
    """The reason each region gets ``(cap+1)//2`` bytes rather than being packed
    back-to-back: an odd-length r1 would otherwise push r2 half a byte over."""
    for cap in CAPS:
        w = (cap + 1) // 2
        assert row_width(cap) == 2 * w
        # r2 = "X" always lands in the same nibble regardless of len(r1)
        for r1 in ("", "X", "Xy", "XyY"):
            if len(r1) > cap:
                continue
            row = pack_row(r1, "X", cap)
            assert row[w] >> 4 == _CHAR_TO_CODE["X"]


@pytest.mark.parametrize("cap", CAPS)
def test_the_solver_decodes_its_own_rows(cap):
    """``relators()`` inverts the packer -- min/max stats are read back this way."""
    words = _deep_corpus(cap)[:12]
    for a, b in itertools.islice(itertools.product(words, repeat=2), 0, None, 3):
        if not a or not b:
            continue     # a search never holds an empty relator
        s = GreedyCompactSolver(a, b, max_nodes=1, max_relator_length=cap)
        s.arena[: s.rw] = np.frombuffer(pack_row(a, b, cap), dtype=np.uint8)
        s.len1[0], s.len2[0] = len(a), len(b)
        assert s.relators(0) == (a, b)


def test_pack_row_rejects_a_relator_over_the_cap():
    with pytest.raises(ValueError):
        pack_row("XXXXX", "Y", 4)
