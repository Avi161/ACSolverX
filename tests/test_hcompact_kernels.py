"""Direct pins on the ``hcompact`` dedup hash that the search-level gates
cannot see through.

The engine-vs-oracle and engine-vs-baseline gates prove the SEARCH is
unchanged, and by Lemma B (the hash only selects slots) they would pass for
ANY hash. What they cannot check is the invariant the rehash relies on:
``_hash_row`` over a packed arena row must equal ``_hash_codes`` over the
same state's unpacked candidate codes, for every length 0..2w including a
relator that exactly fills its region. A mismatch would make a state
inserted by ``_rehash_h`` after a grow invisible to later lookups -- a
duplicate would be re-inserted and the search would silently diverge from
the grow-free one. These tests pin that agreement on thousands of random
states at every row width and on real rows, and additionally pin the values
to the frozen baseline's hash (the change here is indexing only).
"""
import os
import sys

import numpy as np
import pytest
from numba import njit

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from experiments.heuristic_search.core import hcompact as H            # noqa: E402
from experiments.heuristic_search.core.perf_lab import hcompact_baseline as B  # noqa: E402
from experiments.search.greedy_compact import _set_nib_at              # noqa: E402


# ---------------------------------------------------------------------------
# helpers: build arena rows and candidate blobs exactly as each engine does.
# The live engine packs symbols at 2 bits (4 per byte, regions of w bytes);
# the frozen baseline packs nibbles (2 per byte). The hash is over codes and
# lengths, so both rows of the same state must hash identically.
# ---------------------------------------------------------------------------
def _pack_rows_nib(states, w):
    """Nibble rows at width w (the frozen baseline's layout): regions hold
    2w symbols. Returns (arena, len1, len2)."""
    rw = 2 * w
    nb2 = 2 * w
    n = len(states)
    arena = np.zeros(n * rw, dtype=np.uint8)
    len1 = np.zeros(n, dtype=np.uint8)
    len2 = np.zeros(n, dtype=np.uint8)
    for sid, (c1, c2) in enumerate(states):
        assert len(c1) <= nb2 and len(c2) <= nb2
        off = sid * rw
        for t, c in enumerate(c1):
            _set_nib_at(arena, off, t, int(c))
        for t, c in enumerate(c2):
            _set_nib_at(arena, off, nb2 + t, int(c))
        len1[sid] = len(c1)
        len2[sid] = len(c2)
    return arena, len1, len2


def _pack_rows_2bit(states, w):
    """2-bit rows at width w (the live engine's layout): regions hold 4w
    symbols. Returns (arena, len1, len2)."""
    rw = 2 * w
    sym2 = 4 * w
    n = len(states)
    arena = np.zeros(n * rw, dtype=np.uint8)
    len1 = np.zeros(n, dtype=np.uint8)
    len2 = np.zeros(n, dtype=np.uint8)
    for sid, (c1, c2) in enumerate(states):
        assert len(c1) <= sym2 and len(c2) <= sym2
        off = sid * rw
        for t, c in enumerate(c1):
            H._set_sym2_at(arena, off, t, int(c))
        for t, c in enumerate(c2):
            H._set_sym2_at(arena, off, sym2 + t, int(c))
        len1[sid] = len(c1)
        len2[sid] = len(c2)
    return arena, len1, len2


def _blob_of(cands):
    """``cands`` = list of (codes1, codes2) -> (blob, offs, la, lb) in the
    ``expand_and_score_nj`` layout: codes1, 0x00, codes2, back to back."""
    parts, offs, las, lbs = [], [], [], []
    pos = 0
    for c1, c2 in cands:
        offs.append(pos)
        las.append(len(c1))
        lbs.append(len(c2))
        parts.append(bytes(int(c) for c in c1) + b"\x00" + bytes(int(c) for c in c2))
        pos += len(c1) + 1 + len(c2)
    blob = np.frombuffer(b"".join(parts) or b"\x00", dtype=np.uint8).copy()
    return blob, np.array(offs, dtype=np.int64), np.array(las, dtype=np.int64), \
        np.array(lbs, dtype=np.int64)


def _rand_word(rng, n):
    return rng.integers(1, 5, size=n, dtype=np.uint8)


# ---------------------------------------------------------------------------
# 2. the candidate hash == the row hash == the frozen baseline's hash
# ---------------------------------------------------------------------------
@njit(cache=True)
def _h_codes_new(blob, o, la, lb):
    return H._hash_codes(blob, o, la, lb)


@njit(cache=True)
def _h_codes_base(blob, o, la, lb):
    return B._hash_codes(blob, o, la, lb)


@njit(cache=True)
def _h_row_new(arena, sid, len1, len2, sym2, rw):
    return H._hash_row(arena, sid, len1, len2, sym2, rw)


@njit(cache=True)
def _h_row_base(arena, sid, len1, len2, nb2, rw):
    return B._hash_row(arena, sid, len1, len2, nb2, rw)


@pytest.mark.parametrize("w", [1, 2, 4, 12, 24, 32])
def test_hash_of_codes_equals_hash_of_row_and_the_baselines(w):
    """The dedup invariant: a state inserted by the rehash (hashed from its
    packed row) must be found by a later candidate lookup (hashed from the
    unpacked codes). Thousands of random states at every row width, every
    length 0..2w including the full region, and the values must also equal
    the frozen baseline's on both sides (the change is indexing only)."""
    rng = np.random.default_rng(2000 + w)
    nb2 = 2 * w                    # symbols per region in the nibble layout
    rw = 2 * w
    # the 2-bit layout holding the same symbol counts: regions of w2 bytes
    # (4 symbols each), exactly full when 2w is a multiple of 4
    w2 = (nb2 + 3) // 4
    sym2, rw2 = 4 * w2, 2 * w2
    states = [(_rand_word(rng, int(rng.integers(0, nb2 + 1))),
               _rand_word(rng, int(rng.integers(0, nb2 + 1)))) for _ in range(3000)]
    states += [(_rand_word(rng, nb2), _rand_word(rng, nb2)),
               (np.zeros(0, np.uint8), np.zeros(0, np.uint8)),
               (_rand_word(rng, nb2), np.zeros(0, np.uint8)),
               (np.zeros(0, np.uint8), _rand_word(rng, nb2))]
    if nb2 % 4:
        # ... and states that exactly fill the 2-bit regions too
        states += [(_rand_word(rng, sym2), _rand_word(rng, sym2))]
    arena_n, len1, len2 = _pack_rows_nib([s for s in states if len(s[0]) <= nb2
                                          and len(s[1]) <= nb2], w)
    arena_2, len1_2, len2_2 = _pack_rows_2bit(states, w2)
    blob, offs, las, lbs = _blob_of(states)
    n_nib = len(len1)
    for sid in range(len(states)):
        hc = _h_codes_new(blob, offs[sid], las[sid], lbs[sid])
        assert hc == _h_row_new(arena_2, sid, len1_2, len2_2, sym2, rw2), sid
        assert hc == _h_codes_base(blob, offs[sid], las[sid], lbs[sid]), sid
        if sid < n_nib:
            assert hc == _h_row_base(arena_n, sid, len1, len2, nb2, rw), sid


def test_hash_agreement_on_real_rows():
    """Same three-way agreement on every state a real S20_MK2 search stores."""
    from experiments.search.run_leftovers_1m import S20_MK2
    from experiments.heuristic_search.core.perf_lab.bench import load_rows

    for name in ("aca_0", "aca_5"):
        (_, r1, r2), = load_rows([name])
        s = H.HCompactSolver(r1, r2, max_nodes=800, max_relator_length=64,
                             config=S20_MK2, track_path=False)
        s.solve()
        n = s.n_discovered
        sym2, rw = 4 * s.w, s.rw
        rows = s.arena[:n * rw].reshape(n, rw)
        # unpack the 2-bit fields (most-significant first) back to codes 1..4
        syms = np.empty((n, 4 * rw), dtype=np.uint8)
        for k in range(4):
            syms[:, k::4] = ((rows >> (6 - 2 * k)) & 3) + 1
        cands = [(syms[sid, :int(s.len1[sid])].copy(),
                  syms[sid, sym2:sym2 + int(s.len2[sid])].copy()) for sid in range(n)]
        blob, offs, las, lbs = _blob_of(cands)
        # the same states as nibble rows, for the frozen baseline's row hash
        arena_n, len1_n, len2_n = _pack_rows_nib(cands, 32)
        for sid in range(n):
            hc = _h_codes_new(blob, offs[sid], las[sid], lbs[sid])
            assert hc == _h_row_new(s.arena, sid, s.len1, s.len2, sym2, rw)
            assert hc == _h_codes_base(blob, offs[sid], las[sid], lbs[sid])
            assert hc == _h_row_base(arena_n, sid, len1_n, len2_n, 64, 64)
