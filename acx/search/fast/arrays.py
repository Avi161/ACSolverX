"""The fast engine's state arrays, grown by doubling or re-laid at a wider row."""
import numpy as np

from .dedup import rehash
from .packing import packed_width, unpack_state


class Arrays:
    """Room for ``n`` states of ``R`` relators of up to ``W`` symbols, stored ``bits`` a symbol (``packing``).

    State ``sid`` is ``arena[sid]`` (``(R, packed_width(W, bits))`` uint8) with ``lens[sid]``, ``depth``, ``prio``
    (float64), and, when ``track`` is set, ``parent`` and ``pmove`` (``(i, j, s, k1, k2)`` as int32, so path capture
    has no limit on the cap). ``heap`` holds state ids; ``table`` is the dedup table.
    """

    def __init__(self, n, R, W, track, bits):
        self.track, self.width, self.bits = track, W, bits
        self.arena = np.empty((n, R, packed_width(W, bits)), dtype=np.uint8)
        self.lens = np.empty((n, R), dtype=np.int32)
        self.depth = np.empty(n, dtype=np.int32)
        self.prio = np.empty(n, dtype=np.float64)
        self.heap = np.empty(n, dtype=np.int32)
        self.parent = np.empty(n if track else 1, dtype=np.int32)
        self.pmove = np.empty((n if track else 1, 5), dtype=np.int32)
        self.table = np.zeros(1 << (2 * n - 1).bit_length(), dtype=np.int32)

    @property
    def capacity(self):
        return len(self.depth)

    def symbols(self, sid):
        """State ``sid`` unpacked: ``(R, W)`` Booth symbols."""
        out = np.zeros((self.lens.shape[1], self.width), dtype=np.uint8)
        unpack_state(self.arena[sid], self.lens[sid], self.bits, out)
        return out

    def grow(self, n_states, W, n_disc, heap_len):
        """A copy with room for ``n_states`` rows of up to ``W`` symbols, holding the first ``n_disc`` states."""
        new = Arrays(n_states, self.lens.shape[1], W, self.track, self.bits)
        new.arena[:n_disc, :, :self.arena.shape[2]] = self.arena[:n_disc]      # a wider row only adds bytes
        per_state = ("lens", "depth", "prio") + (("parent", "pmove") if self.track else ())
        for name in per_state:
            getattr(new, name)[:n_disc] = getattr(self, name)[:n_disc]
        new.heap[:heap_len] = self.heap[:heap_len]
        rehash(new.table, new.arena, new.lens, n_disc, self.bits)
        return new
