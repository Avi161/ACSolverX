import random

import numpy as np
import pytest

from experiments.equivalence_classes.lib.words import (
    SIGNED_PERMS, apply_pair, canon_pair, relabel_key,
)
from experiments.search.basis_moves import (
    _apply_transform_nj, apply_nielsen_key, reduce_basis_key,
)
from experiments.search.heuristic_1k import NIELSEN, pack, response, unpack


def _pairs():
    rng = random.Random(931)
    pairs = [('', ''), ('x', 'y'), ('xX', 'yyY'), ('YXyxYx', 'YYYYxxx'),
             ('YXYxyx', 'YYYYxxx'), ('xy' * 32, 'x' * 65), ('x' * 128, 'y' * 129)]
    pairs.extend(('x' * n, 'y') for n in (15, 16, 17, 31, 32, 33))
    for n in (1, 8, 31, 32, 33, 48, 63, 64, 65, 96):
        pairs.extend(tuple(''.join(rng.choices('XYxy', k=n)) for _ in range(2))
                     for _ in range(8))
    return pairs


def test_nielsen_images_match_independent_word_oracle():
    for pair in _pairs():
        for index, images in enumerate(NIELSEN):
            assert unpack(apply_nielsen_key(pack(pair), index)) == apply_pair(pair, images)


def test_signed_permutation_kernel_matches_word_oracle():
    for pair in _pairs():
        codes = np.frombuffer(pack(pair), dtype=np.uint8)
        for index, (_, images) in enumerate(SIGNED_PERMS, start=4):
            assert unpack(_apply_transform_nj(codes, index).tobytes()) == apply_pair(pair, images)


@pytest.mark.parametrize('signed_perms', [False, True])
def test_descent_certificates_and_terminal_responses(signed_perms):
    for pair in _pairs():
        current = canon_pair(*pair)
        initial_length = sum(map(len, current))
        key, steps = reduce_basis_key(pack(pair), signed_perms=signed_perms)
        for i, step in enumerate(steps):
            previous = current
            current = apply_pair(current, step['images'])
            assert list(current) == step['state']
            if step['images'] in NIELSEN:
                changes = response(np.frombuffer(pack(previous), dtype=np.uint8))
                assert NIELSEN.index(step['images']) == min(range(4), key=lambda j: changes[j])
                assert sum(map(len, current)) < sum(map(len, previous))
            else:
                assert signed_perms and i == len(steps) - 1
                assert sum(map(len, current)) == sum(map(len, previous))
        assert current == unpack(key)
        assert len(key) - 1 <= initial_length
        assert min(response(np.frombuffer(key, dtype=np.uint8))) >= 0
        if signed_perms:
            assert current == relabel_key(current)
        assert reduce_basis_key(key, signed_perms=signed_perms) == (key, [])


def test_reduction_records_multiple_strict_steps():
    pair = ('xy', 'xyy')
    key, steps = reduce_basis_key(pack(pair), signed_perms=False)
    assert len(steps) >= 2
    assert len(key) < len(pack(pair))


@pytest.mark.parametrize('key', [b'', b'\1', b'\0\0', b'\5\0\1'])
def test_invalid_encoded_keys_are_rejected(key):
    with pytest.raises(ValueError):
        apply_nielsen_key(key, 0)
    with pytest.raises(ValueError):
        reduce_basis_key(key)


@pytest.mark.parametrize('index', [-1, 4])
def test_invalid_nielsen_index_is_rejected(index):
    with pytest.raises(ValueError, match='0..3'):
        apply_nielsen_key(b'\1\0\2', index)


def test_non_bytes_key_is_rejected():
    with pytest.raises(TypeError, match='bytes'):
        apply_nielsen_key([1, 0, 2], 0)
