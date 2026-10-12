"""``CapArrays``: the numba twin of ``CapCount``, owning the arrays the ``cc_*`` kernels work on."""
import numpy as np

from .kernels import (C_DROPPED, C_FIRST, C_MINTOT, C_NEED, C_NENT, C_NHEAP, C_POOL, C_POPS, C_WOULD, SLOT_DEPTH,
                      SLOT_HEAP, SLOT_LONGEST, SLOT_NBYTES, SLOT_OFFSET, SLOT_POOL, SLOT_PRIO, SLOT_STATE, cc_drop,
                      cc_free, cc_known, cc_pop, rehash)
from .records import fields

STATE_SIZE = 9                                  # the C_* slots

# The arrays holding one value per entry (copied as they are when the arrays grow).
_PER_ENTRY = (SLOT_PRIO, SLOT_DEPTH, SLOT_OFFSET, SLOT_NBYTES, SLOT_LONGEST)


def _allocate(state, entries, nbytes):
    """The ``cc`` tuple for room for ``entries`` entries and ``nbytes`` key bytes, sharing ``state``."""
    table_size = 1 << (2 * entries - 1).bit_length()        # a power of two, at least twice the entries
    return (state,
            np.empty(entries, np.float64),                  # SLOT_PRIO
            np.empty(entries, np.int64),                    # SLOT_DEPTH
            np.empty(entries, np.int64),                    # SLOT_OFFSET
            np.empty(entries, np.int32),                    # SLOT_NBYTES
            np.empty(entries, np.int32),                    # SLOT_LONGEST
            np.empty(entries, np.int32),                    # SLOT_HEAP
            np.zeros(table_size, np.int32),                 # SLOT_TABLE
            np.empty(nbytes, np.uint8))                     # SLOT_POOL


class CapArrays:
    """The twin of ``CapCount`` on flat arrays.

    ``cap`` is the cap watched, ``cc`` the state tuple the ``cc_*`` kernels take, and ``drop`` / ``known`` /
    ``pop`` / ``end`` / ``record`` mirror ``CapCount``'s. The arrays grow by doubling what is short (``grow``).
    """

    def __init__(self, cap, entries=1 << 12, nbytes=1 << 16):
        self.cap = cap
        state = np.zeros(STATE_SIZE, dtype=np.int64)
        state[C_FIRST] = state[C_NEED] = state[C_MINTOT] = -1
        self.cc = _allocate(state, entries, nbytes)

    def grow(self, entries, nbytes):
        """Make room for ``entries`` more entries and ``nbytes`` more key bytes."""
        old = self.cc
        state = old[SLOT_STATE]
        used_entries, used_bytes = int(state[C_NENT]), int(state[C_POOL])
        new_entries, new_bytes = len(old[SLOT_PRIO]), len(old[SLOT_POOL])
        while used_entries + entries > new_entries:
            new_entries *= 2
        while used_bytes + nbytes > new_bytes:
            new_bytes *= 2
        if new_entries == len(old[SLOT_PRIO]) and new_bytes == len(old[SLOT_POOL]):
            return
        new = _allocate(state, new_entries, new_bytes)
        for slot in _PER_ENTRY:
            new[slot][:used_entries] = old[slot][:used_entries]
        heap_size = state[C_NHEAP]
        new[SLOT_HEAP][:heap_size] = old[SLOT_HEAP][:heap_size]
        new[SLOT_POOL][:used_bytes] = old[SLOT_POOL][:used_bytes]
        rehash(new, used_entries)
        self.cc = new

    def free(self, entries, nbytes):
        """``cc_free`` on the current arrays."""
        return cc_free(self.cc, entries, nbytes)

    def tail(self):
        """The pool from the free offset: where the next key bytes are written."""
        return self.cc[SLOT_POOL][self.cc[SLOT_STATE][C_POOL]:]

    def drop(self, prio, depth, key, total, longest):
        """Python entry (tests, small searches): copy ``key`` bytes in, then ``cc_drop``."""
        self._write_key(key)
        cc_drop(self.cc, float(prio), int(depth), len(key), int(total), int(longest))

    def known(self, key):
        """Seed ``key`` as already discovered."""
        self._write_key(key)
        cc_known(self.cc, len(key))

    def pop(self, prio, depth, key):
        """``CapCount.pop`` with the bar ``(prio, depth, key)``."""
        bar = np.frombuffer(bytes(key), np.uint8)
        cc_pop(self.cc, float(prio), int(depth), bar, len(bar))

    def end(self, ran_dry, left):
        """``CapCount.end``: count what a dry queue would pop next, then drop the pending entries."""
        state = self.cc[SLOT_STATE]
        pending = int(state[C_NHEAP])
        if ran_dry and pending > 0 and left > 0:
            state[C_WOULD] += min(pending, left)
            if state[C_FIRST] < 0:
                state[C_FIRST] = state[C_POPS] + 1
            pending_ids = self.cc[SLOT_HEAP][:pending]
            least_longest = int(self.cc[SLOT_LONGEST][pending_ids].min())
            if state[C_NEED] < 0 or least_longest < state[C_NEED]:
                state[C_NEED] = least_longest
        state[C_NHEAP] = 0

    def record(self, prefix="cap"):
        """The counter's ``FIELDS`` as a dict (a slot still at -1 is None)."""
        state = [int(x) for x in self.cc[SLOT_STATE]]

        def unset_as_none(value):
            return None if value < 0 else value

        values = (self.cap, state[C_DROPPED], unset_as_none(state[C_MINTOT]), state[C_WOULD],
                  unset_as_none(state[C_FIRST]), unset_as_none(state[C_NEED]))
        return dict(zip(fields(prefix), values))

    def _write_key(self, key):
        """Write the key bytes at the free offset, growing the arrays first if they are full."""
        if not self.free(1, len(key)):
            self.grow(1, len(key))
        self.tail()[:len(key)] = np.frombuffer(bytes(key), np.uint8)
