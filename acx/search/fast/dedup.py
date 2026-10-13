"""The dedup table of the fast engine: open addressing, linear probing, int32 slots.

Slot ``h`` holds ``sid + 1`` for the state ``arena[sid]`` stored there, or 0 when empty. States hash by FNV-1a over
their lengths and packed bytes (``packing``, which hashes a child as it packs it), and compare by the same.
"""
import numpy as np
from numba import njit

from .packing import FNV_OFFSET, fnv, fnv_end, used_bytes


@njit(inline="always")
def hash_state(prow, rlen, bits):
    """The hash of a packed state, the one ``packing.pack_state`` returns."""
    h = FNV_OFFSET
    for r in range(len(rlen)):
        h = fnv(h, rlen[r] + 256)
        for k in range(used_bytes(rlen[r], bits)):
            h = fnv(h, prow[r, k])
    return fnv_end(h)


@njit(inline="always")
def _same_state(arena, lens, sid, prow, rlen, bits):
    for r in range(len(rlen)):
        if lens[sid, r] != rlen[r]:
            return False
    for r in range(len(rlen)):
        for k in range(used_bytes(rlen[r], bits)):
            if arena[sid, r, k] != prow[r, k]:
                return False
    return True


@njit(inline="always")
def find_slot(table, arena, lens, prow, rlen, h, bits):
    """Slot holding the state equal to the packed ``prow``, or the empty slot where it goes."""
    mask = len(table) - 1
    slot = np.int64(h & np.uint64(mask))
    while table[slot] != 0 and not _same_state(arena, lens, table[slot] - 1, prow, rlen, bits):
        slot = (slot + 1) & mask
    return slot


@njit(cache=True)
def rehash(table, arena, lens, n_states, bits):
    """Rebuild the table from the first ``n_states`` states."""
    table[:] = 0
    for sid in range(n_states):
        h = hash_state(arena[sid], lens[sid], bits)
        table[find_slot(table, arena, lens, arena[sid], lens[sid], h, bits)] = sid + 1
