"""The dedup table of the fast engine: open addressing, linear probing, int32 slots.

Slot ``h`` holds ``sid + 1`` for the state ``arena[sid]`` stored there, or 0 when empty. States hash by FNV-1a over
their lengths and symbols.
"""
import numpy as np
from numba import njit


@njit(inline="always")
def hash_state(row, rlen):
    h = np.uint64(1469598103934665603)
    prime = np.uint64(1099511628211)
    for r in range(len(rlen)):
        h = (h ^ np.uint64(rlen[r] + 256)) * prime
        for t in range(rlen[r]):
            h = (h ^ np.uint64(row[r, t])) * prime
    return h ^ (h >> np.uint64(29))


@njit(inline="always")
def _same_state(arena, lens, sid, row, rlen):
    for r in range(len(rlen)):
        if lens[sid, r] != rlen[r]:
            return False
    for r in range(len(rlen)):
        for t in range(rlen[r]):
            if arena[sid, r, t] != row[r, t]:
                return False
    return True


@njit(inline="always")
def find_slot(table, arena, lens, row, rlen, h):
    """Slot holding the state equal to ``row``, or the empty slot where it goes."""
    mask = len(table) - 1
    slot = np.int64(h & np.uint64(mask))
    while table[slot] != 0 and not _same_state(arena, lens, table[slot] - 1, row, rlen):
        slot = (slot + 1) & mask
    return slot


@njit(cache=True)
def rehash(table, arena, lens, n_states):
    """Rebuild the table from the first ``n_states`` states."""
    table[:] = 0
    for sid in range(n_states):
        slot = find_slot(table, arena, lens, arena[sid], lens[sid], hash_state(arena[sid], lens[sid]))
        table[slot] = sid + 1
