"""The numba kernels of the cap counter: the same logic as ``CapCount`` on flat arrays.

State is a tuple ``cc`` indexed by the ``SLOT_*`` constants:

* per dropped entry ``e``: its key (``prio[e]`` f64, ``depth[e]`` i64, the bytes ``pool[offset[e]:][:nbytes[e]]``)
  and ``longest[e]``, the longest relator of the dropped state;
* ``heap``: an int32 min-heap of the entry ids still pending, ordered by that key;
* ``table``: an open-addressing int32 set of entry id + 1 keyed by the bytes (first-drop dedup; drained entries
  stay in it);
* ``state``: an int64 array of counters and cursors, indexed by the ``C_*`` constants.

A caller writes a dropped child's key bytes at ``pool[state[C_POOL]:]`` (``cc_free`` checks the room) and calls
``cc_drop``; at each pop it calls ``cc_pop`` with the bar's key. Bytes compare lexicographically, a proper
prefix first. ``tests/test_capcount.py`` pins these kernels to ``CapCount``. Without numba they run as plain
Python.
"""
import numpy as np

try:
    from numba import njit
except ModuleNotFoundError:                     # the kernels then run as plain Python
    def njit(*args, **kwargs):
        return args[0] if args and callable(args[0]) else (lambda function: function)

# Slots of the ``cc`` tuple.
SLOT_STATE, SLOT_PRIO, SLOT_DEPTH, SLOT_OFFSET, SLOT_NBYTES, SLOT_LONGEST, SLOT_HEAP, SLOT_TABLE, SLOT_POOL = range(9)

# Slots of the int64 ``state`` array. The "first" and "need" and "min total" slots hold -1 until they are set.
STATE_SIZE = 9
C_DROPPED, C_WOULD, C_FIRST, C_NEED, C_MINTOT, C_POPS, C_NENT, C_NHEAP, C_POOL = range(STATE_SIZE)


# --- key order -------------------------------------------------------------------------------------

@njit(inline="always")
def _bytes_less(pool_a, offset_a, n_a, pool_b, offset_b, n_b):
    """Lexicographic order of two byte strings, a proper prefix first."""
    for t in range(min(n_a, n_b)):
        x, y = pool_a[offset_a + t], pool_b[offset_b + t]
        if x != y:
            return x < y
    return n_a < n_b


@njit(inline="always")
def _entry_less(cc, a, b):
    """Entry ``a`` sorts before entry ``b``: by ``prio``, then ``depth``, then key bytes."""
    prio, depth = cc[SLOT_PRIO], cc[SLOT_DEPTH]
    offset, nbytes, pool = cc[SLOT_OFFSET], cc[SLOT_NBYTES], cc[SLOT_POOL]
    if prio[a] != prio[b]:
        return prio[a] < prio[b]
    if depth[a] != depth[b]:
        return depth[a] < depth[b]
    return _bytes_less(pool, offset[a], nbytes[a], pool, offset[b], nbytes[b])


@njit(inline="always")
def _entry_before_bar(cc, e, bar_prio, bar_depth, bar, n):
    """Entry ``e`` sorts strictly before the bar key ``(bar_prio, bar_depth, bar[:n])``."""
    prio, depth = cc[SLOT_PRIO], cc[SLOT_DEPTH]
    if prio[e] != bar_prio:
        return prio[e] < bar_prio
    if depth[e] != bar_depth:
        return depth[e] < bar_depth
    return _bytes_less(cc[SLOT_POOL], cc[SLOT_OFFSET][e], cc[SLOT_NBYTES][e], bar, 0, n)


# --- the dedup table -------------------------------------------------------------------------------

@njit(inline="always")
def _hash_bytes(pool, offset, n):
    """FNV-1a over ``pool[offset:offset + n]``, with a final fold of the high bits."""
    h = np.uint64(1469598103934665603)
    prime = np.uint64(1099511628211)
    for t in range(n):
        h = (h ^ np.uint64(pool[offset + t])) * prime
    return h ^ (h >> np.uint64(29))


@njit(inline="always")
def _find(cc, offset, n):
    """Slot of the entry whose bytes equal ``pool[offset:offset + n]``, or the empty slot where it goes."""
    entry_offset, nbytes = cc[SLOT_OFFSET], cc[SLOT_NBYTES]
    table, pool = cc[SLOT_TABLE], cc[SLOT_POOL]
    mask = len(table) - 1
    slot = np.int64(_hash_bytes(pool, offset, n) & np.uint64(mask))
    while table[slot] != 0:
        e = table[slot] - 1
        if nbytes[e] == n:
            same = True
            for t in range(n):
                if pool[entry_offset[e] + t] != pool[offset + t]:
                    same = False
                    break
            if same:
                return slot
        slot = (slot + 1) & mask
    return slot


@njit(cache=True)
def rehash(cc, n_entries):
    """Rebuild the dedup table from the first ``n_entries`` entries (after the arrays grew)."""
    table = cc[SLOT_TABLE]
    table[:] = 0
    for e in range(n_entries):
        table[_find(cc, cc[SLOT_OFFSET][e], cc[SLOT_NBYTES][e])] = e + 1


# --- the pending heap ------------------------------------------------------------------------------

@njit(inline="always")
def _heap_push(cc, e):
    """Add entry ``e`` to the pending heap."""
    state, heap = cc[SLOT_STATE], cc[SLOT_HEAP]
    i = state[C_NHEAP]
    state[C_NHEAP] = i + 1
    while i > 0:
        parent = (i - 1) >> 1
        if not _entry_less(cc, e, heap[parent]):
            break
        heap[i] = heap[parent]
        i = parent
    heap[i] = e


@njit(inline="always")
def _heap_pop(cc):
    """Remove the top (least) entry of the pending heap."""
    state, heap = cc[SLOT_STATE], cc[SLOT_HEAP]
    size = state[C_NHEAP] - 1
    state[C_NHEAP] = size
    if size == 0:
        return
    last = heap[size]
    i = 0
    while True:
        child = 2 * i + 1
        if child >= size:
            break
        if child + 1 < size and _entry_less(cc, heap[child + 1], heap[child]):
            child += 1
        if not _entry_less(cc, heap[child], last):
            break
        heap[i] = heap[child]
        i = child
    heap[i] = last


# --- the public kernels ----------------------------------------------------------------------------

@njit(cache=True)
def cc_free(cc, entries, nbytes):
    """True when ``entries`` more entries holding ``nbytes`` more key bytes fit without growing."""
    state = cc[SLOT_STATE]
    n_entries = state[C_NENT] + entries
    return (n_entries <= len(cc[SLOT_PRIO]) and 2 * n_entries <= len(cc[SLOT_TABLE])
            and state[C_POOL] + nbytes <= len(cc[SLOT_POOL]))


@njit(inline="always")
def _add_entry(cc, slot, n, prio, depth, longest):
    """Store the key bytes at ``pool[state[C_POOL]:][:n]`` as a new entry, registered at table ``slot``."""
    state = cc[SLOT_STATE]
    e = state[C_NENT]
    offset = state[C_POOL]
    cc[SLOT_PRIO][e] = prio
    cc[SLOT_DEPTH][e] = depth
    cc[SLOT_OFFSET][e] = offset
    cc[SLOT_NBYTES][e] = n
    cc[SLOT_LONGEST][e] = longest
    cc[SLOT_TABLE][slot] = e + 1
    state[C_NENT] = e + 1
    state[C_POOL] = offset + n
    return e


@njit(cache=True)
def cc_known(cc, n):
    """Seed an ident (the bytes at ``pool[state[C_POOL]:][:n]``) as already discovered: never pending."""
    slot = _find(cc, cc[SLOT_STATE][C_POOL], n)
    if cc[SLOT_TABLE][slot] == 0:
        _add_entry(cc, slot, n, np.inf, 0, 0)


@njit(cache=True)
def cc_drop(cc, prio, depth, n, total, longest):
    """The cap dropped a child whose key is ``(prio, depth, pool[state[C_POOL]:][:n])``."""
    state = cc[SLOT_STATE]
    state[C_DROPPED] += 1
    if state[C_MINTOT] < 0 or total < state[C_MINTOT]:
        state[C_MINTOT] = total
    slot = _find(cc, state[C_POOL], n)
    if cc[SLOT_TABLE][slot] != 0:               # this state was already dropped or discovered
        return
    e = _add_entry(cc, slot, n, prio, depth, longest)
    _heap_push(cc, e)


@njit(cache=True)
def cc_pop(cc, prio, depth, bar, n):
    """One pop with bar key ``(prio, depth, bar[:n])``, before it expands."""
    state, heap, longest = cc[SLOT_STATE], cc[SLOT_HEAP], cc[SLOT_LONGEST]
    state[C_POPS] += 1
    while state[C_NHEAP] > 0 and _entry_before_bar(cc, heap[0], prio, depth, bar, n):
        e = heap[0]                             # it would have popped first
        _heap_pop(cc)
        state[C_WOULD] += 1
        if state[C_FIRST] < 0:
            state[C_FIRST] = state[C_POPS]
        if state[C_NEED] < 0 or longest[e] < state[C_NEED]:
            state[C_NEED] = longest[e]
