"""The binary min-heap of state ids, ordered by ``(prio, depth, key)``.

``key`` compares relators in turn by ``key_code``, a proper prefix first: exactly spec's ``state_key`` tuples. The
symbols are read out of the packed arena (``packing``). Keys are unique (dedup before push), so the order is strict
and the pop sequence does not depend on the heap layout.
"""
from numba import njit

from .kernels import key_code
from .packing import symbol


@njit(inline="always")
def less(a, b, prio, depth, arena, lens, n_gen, bits):
    """Whether state ``a`` pops before state ``b``."""
    if prio[a] != prio[b]:
        return prio[a] < prio[b]
    if depth[a] != depth[b]:
        return depth[a] < depth[b]
    for r in range(lens.shape[1]):
        la, lb = lens[a, r], lens[b, r]
        n = min(la, lb)
        k = 0                                       # equal whole bytes hold equal symbols
        while k < (n * bits) >> 3 and arena[a, r, k] == arena[b, r, k]:
            k += 1
        for t in range((k << 3) // bits, n):
            x, y = symbol(arena[a, r], t, bits), symbol(arena[b, r], t, bits)
            if x != y:
                return key_code(x, n_gen) < key_code(y, n_gen)
        if la != lb:
            return la < lb
    return False


@njit(inline="always")
def heap_pop(heap, heap_len, prio, depth, arena, lens, n_gen, bits):
    """Remove the root of ``heap[:heap_len]`` (the caller has read ``heap[0]``); returns the new length."""
    heap_len -= 1
    if heap_len > 0:
        moved = heap[heap_len]                      # the last entry sifts down from the root
        i = 0
        while True:
            child = 2 * i + 1
            if child >= heap_len:
                break
            if child + 1 < heap_len and less(heap[child + 1], heap[child], prio, depth, arena, lens, n_gen, bits):
                child += 1
            if not less(heap[child], moved, prio, depth, arena, lens, n_gen, bits):
                break
            heap[i] = heap[child]
            i = child
        heap[i] = moved
    return heap_len


@njit(inline="always")
def heap_push(heap, heap_len, sid, prio, depth, arena, lens, n_gen, bits):
    """Add state ``sid`` to ``heap[:heap_len]``; returns the new length."""
    i = heap_len
    while i > 0:
        parent = (i - 1) >> 1
        if not less(sid, heap[parent], prio, depth, arena, lens, n_gen, bits):
            break
        heap[i] = heap[parent]
        i = parent
    heap[i] = sid
    return heap_len + 1
