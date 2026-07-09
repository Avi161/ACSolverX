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
