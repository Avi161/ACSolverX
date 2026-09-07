"""Compiled Nielsen images and descending basis changes for experimental searches.

The final eight-permutation normalization is not full Aut(F2) canonicalization:
length-preserving Nielsen plateaus are not enumerated.
"""
from __future__ import annotations

import operator

import numpy as np
from numba import njit

from experiments.equivalence_classes.lib.words import SIGNED_PERMS, inv
from experiments.heuristic_search.core.hexpand import (
    _canon_packed, _encode_bools, _encode_packed,
)
from experiments.search.greedy_baseline import canonical_relator_nj
from experiments.search.heuristic_1k import NIELSEN, response

_CODE = {'X': 1, 'Y': 2, 'x': 3, 'y': 4}
_CHARS = '\0XYxy'
_IMAGES = tuple(dict(img) for img in NIELSEN) + tuple(
    dict(img) for _, img in SIGNED_PERMS)
_TABLE = np.zeros((len(_IMAGES), 5, 2), dtype=np.uint8)
_LENGTHS = np.zeros((len(_IMAGES), 5), dtype=np.int64)
for _i, _img in enumerate(_IMAGES):
    for _char, _code in _CODE.items():
        _word = _img[_char] if _char.islower() else inv(_img[_char.lower()])
        _LENGTHS[_i, _code] = len(_word)
        for _j, _out in enumerate(_word):
            _TABLE[_i, _code, _j] = _CODE[_out]


@njit(inline='always')
def _split(codes):
    sep = -1
    for i in range(len(codes)):
        if codes[i] == 0:
            if sep != -1:
                raise ValueError('A key must have exactly one zero separator')
            sep = i
        elif codes[i] > 4:
            raise ValueError('A key contains an invalid symbol code')
    if sep == -1:
        raise ValueError('A key must have exactly one zero separator')
    return sep


@njit(inline='always')
def _order(code):
    return 2 * (code & 1) + (1 if code >= 3 else 0)


@njit(cache=True)
def _apply_transform_nj(codes, transform):
    sep = _split(codes)
    width = 2 * max(sep, len(codes) - sep - 1)
    stack = np.empty((width, 2), dtype=np.bool_)
    canonical = np.empty((2, width), dtype=np.uint8)
    sizes = np.empty(2, dtype=np.int64)
    doubled = np.empty(5, dtype=np.uint64)
    doubled_inverse = np.empty(5, dtype=np.uint64)
    for word in range(2):
        start = 0 if word == 0 else sep + 1
        end = sep if word == 0 else len(codes)
        n = 0
        for i in range(start, end):
            code = codes[i]
            for j in range(_LENGTHS[transform, code]):
                out = _TABLE[transform, code, j]
                generator = (out & 1) == 1
                sign = out >= 3
                if n and stack[n - 1, 0] == generator and stack[n - 1, 1] != sign:
                    n -= 1
                else:
                    stack[n, 0] = generator
                    stack[n, 1] = sign
                    n += 1
        lo = 0
        while n - lo >= 2 and stack[lo, 0] == stack[n - 1, 0] and stack[lo, 1] != stack[n - 1, 1]:
            lo += 1
            n -= 1
        size = n - lo
        sizes[word] = size
        if size <= 64:
            hi, low = _canon_packed(stack, lo, size, doubled, doubled_inverse)
            _encode_packed(hi, low, size, canonical[word], 0)
        else:
            reduced = canonical_relator_nj(stack[lo:n])
            _encode_bools(reduced, size, canonical[word], 0)
    first = 0
    if sizes[0] > sizes[1]:
        first = 1
    elif sizes[0] == sizes[1]:
        for j in range(sizes[0]):
            a, b = _order(canonical[0, j]), _order(canonical[1, j])
            if a != b:
                first = 0 if a < b else 1
                break
    other = 1 - first
    out = np.empty(sizes[0] + sizes[1] + 1, dtype=np.uint8)
    out[:sizes[first]] = canonical[first, :sizes[first]]
    out[sizes[first]] = 0
    out[sizes[first] + 1:] = canonical[other, :sizes[other]]
    return out


@njit(inline='always')
def _bytes_less(a, b):
    for i in range(min(len(a), len(b))):
        if a[i] != b[i]:
            return a[i] < b[i]
    return len(a) < len(b)


@njit(cache=True)
def _reduce_basis_nj(codes, signed_perms):
    cur = _apply_transform_nj(codes, 4)
    states = [cur]
    transforms = []
    while True:
        changes = response(cur)
        best, delta = -1, 0
        for i in range(4):
            if changes[i] < delta:
                best, delta = i, changes[i]
        if best < 0:
            break
        child = _apply_transform_nj(cur, best)
        if len(child) - len(cur) != delta:
            raise AssertionError('Nielsen response differs from transformed length')
        cur = child
        states.append(cur)
        transforms.append(best)
    if signed_perms:
        best_key = cur
        best = -1
        for i in range(5, 12):
            candidate = _apply_transform_nj(cur, i)
            if _bytes_less(candidate, best_key):
                best_key, best = candidate, i
        if best >= 0:
            cur = best_key
            states.append(cur)
            transforms.append(best)
    return cur, states, transforms


def _codes(key):
    if not isinstance(key, bytes):
        raise TypeError('A search key must be bytes')
    return np.frombuffer(key, dtype=np.uint8)


def _state(codes):
    first, second = codes.tobytes().split(b'\0')
    return [''.join(_CHARS[c] for c in first), ''.join(_CHARS[c] for c in second)]


def apply_nielsen_key(key: bytes, index: int) -> bytes:
    """Apply one of heuristic_1k.NIELSEN's four images, then exact canon_pair."""
    index = operator.index(index)
    if not 0 <= index < 4:
        raise ValueError('Nielsen index must be in 0..3')
    return _apply_transform_nj(_codes(key), index).tobytes()


def reduce_basis_key(key: bytes, signed_perms: bool = True) -> tuple[bytes, list[dict]]:
    """Strictly decrease length using the most-negative Nielsen response.

    Equal responses use the first Nielsen index. The initial key is cyclically
    reduced and canon_pair-normalized; each returned step applies to that pair.
    An optional final signed permutation uses words.relabel_key's ordering.
    Every step records its images and resulting canonical state for replay.
    """
    reduced, states, transforms = _reduce_basis_nj(_codes(key), signed_perms)
    steps = [dict(kind='automorphism', images=dict(_IMAGES[index]), state=_state(states[i + 1]))
             for i, index in enumerate(transforms)]
    return reduced.tobytes(), steps
