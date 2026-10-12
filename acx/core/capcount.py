"""Cap counters: what a relator cap dropped, and whether a dropped state would have been popped.

The module knows no heuristic. A search tells a counter three things:

* ``drop(key, total, longest, ident)``: the cap dropped a child (one call per move). ``key`` is the
  full heap key the active priority would have pushed the child under, e.g. ``(priority, depth,
  state_bytes)``; ``ident`` names the state, so that each state is judged once, under the key of
  its FIRST drop (the search dedups on discovery, so a state is pushed at most once, by its
  first discoverer).
* ``pop(bar)``: the search popped an entry with key ``bar`` (call it BEFORE expanding that entry,
  the solving pop included). Every pending dropped key that sorts strictly before the bar is a
  state the search would have popped first had the cap been larger: ``cap_would_pop``.
* ``end(ran_dry, left)``: the search stopped. ``ran_dry``: the queue emptied unsolved with
  ``left > 0`` pops of budget left, so the pending dropped states would have popped next (up to
  ``left`` of them). A search that solved or spent its budget passes ``ran_dry=False``.

Keys are any totally ordered values; the counter only compares them. Fields (``FIELDS``, one
counter = one cap; ``record(prefix)`` renames ``cap`` to ``prefix``):

==========================  ==========================================================================
``cap``                     the cap this counter watches (None = uncapped)
``cap_dropped``             children not pushed because a relator is over the cap, one per move
``cap_dropped_min_total``   least total relator length of a dropped child; None iff nothing dropped
``cap_would_pop``           distinct dropped states whose first-drop key sorts before a later bar,
                            plus, when the queue ran dry, the pending ones the budget would pop
``cap_first_bind``          pop number (1 = the start) of the first such pop; ``pops + 1`` when the
                            queue ran dry with dropped states pending; None iff ``cap_would_pop == 0``
``cap_needed``              least longest relator over the would-pop states (and, on a dry queue,
                            over every pending state): the smallest cap at which the search changes;
                            None iff ``cap_would_pop == 0``
==========================  ==========================================================================

For a best-first search whose heap key is a strict total order (``acx.search``): ``cap_would_pop
== 0`` holds exactly when the search at every larger cap pops the same states in the same order
with the same path, and a cap ``C' < cap_needed`` gives the same search while ``C' >=
cap_needed`` does not. Uncapped searches keep no counter and report ``blank()``.

The numba twin (``CapArrays`` and the ``cc_*`` kernels) keeps the same state in flat arrays for
the fast engine: keys are ``(float64 prio, int64 depth, uint8 bytes)``, bytes compared
lexicographically with a proper prefix first. ``tests/test_capcount.py`` pins it to ``CapCount``.
Without numba the kernels run as plain Python.
"""
from heapq import heappop, heappush

import numpy as np

try:
    from numba import njit
except ModuleNotFoundError:                     # the twin then runs as plain Python
    def njit(*args, **kw):
        return args[0] if args and callable(args[0]) else (lambda f: f)

FIELDS = ("cap", "cap_dropped", "cap_dropped_min_total", "cap_would_pop", "cap_first_bind", "cap_needed")


def fields(prefix="cap"):
    """``FIELDS`` under another counter prefix (``"dyn_cap"`` -> ``dyn_cap``, ``dyn_cap_dropped``, ...)."""
    return tuple(f.replace("cap", prefix, 1) for f in FIELDS)


def blank(prefix="cap", cap=None):
    """The record of a search that kept no counter (uncapped): ``cap: None, dropped 0, ...``."""
    return dict(zip(fields(prefix), (cap, 0, None, 0, None, None)))


class CapCount:
    """One counter per cap (module docstring). ``known``: idents already discovered (the start),
    so a dropped child equal to one counts in ``cap_dropped`` only. ``accept(payload)``: optional
    pop-time dedup (a search that dedups when it pops); a drained entry counts only if it returns
    True."""

    __slots__ = ("cap", "accept", "dropped", "would_pop", "pops", "min_total", "first_bind", "needed",
                 "_pending", "_first", "_seq")

    def __init__(self, cap, accept=None, known=()):
        self.cap, self.accept = cap, accept
        self.dropped = self.would_pop = self.pops = 0
        self.min_total = self.first_bind = self.needed = None
        self._pending, self._first, self._seq = [], set(known), 0

    def drop(self, key, total, longest, ident=None, payload=None):
        """The cap dropped a child (one call per move); ``ident`` None means no dedup."""
        self.dropped += 1
        if self.min_total is None or total < self.min_total:
            self.min_total = total
        if ident is not None:
            if ident in self._first:
                return
            self._first.add(ident)
        self._seq += 1                                   # equal keys never compare their payloads
        heappush(self._pending, (key, self._seq, longest, payload))

    def drop_now(self, total, longest):
        """A dropped child the search would have acted on at once (a beam slot, a finishing gate)."""
        self.dropped += 1
        if self.min_total is None or total < self.min_total:
            self.min_total = total
        self._hit(longest, self.pops)

    def pop(self, bar):
        """One pop, before it expands. ``bar`` None only advances the pop number."""
        self.pops += 1
        p = self._pending
        while bar is not None and p and p[0][0] < bar:
            e = heappop(p)
            if self.accept is None or self.accept(e[3]):
                self._hit(e[2], self.pops)

    def end(self, ran_dry, left):
        """The search stopped; ``ran_dry``: the queue emptied unsolved with ``left > 0`` budget."""
        if ran_dry and self._pending and left > 0:
            p = sorted(self._pending)
            if self.accept is not None:
                p = [e for e in p if self.accept(e[3])]
            for k, e in enumerate(p):
                self._hit(e[2], self.pops + 1, k < left)     # every pending state bounds cap_needed
        self._pending, self._first = [], set()

    def _hit(self, longest, at, count=True):
        self.would_pop += count
        if self.first_bind is None:
            self.first_bind = at
        if self.needed is None or longest < self.needed:
            self.needed = longest

    @property
    def pending(self):
        return len(self._pending)

    def record(self, prefix="cap"):
        return dict(zip(fields(prefix), (self.cap, self.dropped, self.min_total, self.would_pop,
                                         self.first_bind, self.needed)))


def combine(parts, prefix="cap"):
    """One record from several searches run one after another on a shared budget (e.g. CoV legs).

    ``parts``: ``(record, pops_before)`` pairs in run order, ``pops_before`` the pops spent before that
    search started. Sums ``dropped`` and ``would_pop``; ``first_bind`` is ``pops_before`` plus the first
    binding search's ``first_bind``; ``min_total`` and ``needed`` are minima; ``cap`` is the first
    record's.
    """
    f = fields(prefix)
    out = blank(prefix)
    for k, (rec, before) in enumerate(parts):
        if k == 0:
            out[f[0]] = rec[f[0]]
        out[f[1]] += rec[f[1]]
        out[f[3]] += rec[f[3]]
        for i in (2, 5):
            if rec[f[i]] is not None and (out[f[i]] is None or rec[f[i]] < out[f[i]]):
                out[f[i]] = rec[f[i]]
        if out[f[4]] is None and rec[f[4]] is not None:
            out[f[4]] = before + rec[f[4]]
    return out


def summarize(records, prefix="cap", ids=None, keep=100):
    """The ``summary.json`` block of one counter over a run's row records (rows lacking it skipped)."""
    f = fields(prefix)
    rows = [(i, r) for i, r in zip(ids or [r.get("id") for r in records], records) if f[1] in r]
    if not rows:
        return None
    caps = sorted({r[f[0]] for _, r in rows}, key=lambda c: (c is None, c))
    raise_ids = [i for i, r in rows if r[f[3]]]

    def low(k, fn=min):
        xs = [r[f[k]] for _, r in rows if r[f[k]] is not None]
        return fn(xs) if xs else None

    return {f[0]: caps[0] if len(caps) == 1 else caps, "rows": len(rows),
            "rows_dropped": sum(1 for _, r in rows if r[f[1]]), "rows_would_pop": len(raise_ids),
            "raise_ids": raise_ids[:keep], "dropped": sum(r[f[1]] for _, r in rows),
            "would_pop": sum(r[f[3]] for _, r in rows), "dropped_min_total": low(2),
            "first_bind_min": low(4), "needed_min": low(5), "needed_max": low(5, max)}


# ---------------------------------------------------------------------------------------------------
# The numba twin. State is a tuple ``cc = (st, prio, depth, off, nb, longest, heap, table, pool)``:
# per entry its key (``prio`` f64, ``depth`` i64, the bytes ``pool[off:off + nb]``) and ``longest``;
# ``heap`` an int32 min-heap of pending entry ids; ``table`` an open-addressing int32 set of entry
# ids + 1 keyed by the bytes (first-drop dedup; drained entries stay in it). ``st`` slots below.
# A caller writes a dropped child's key bytes at ``pool[st[C_POOL]:]`` (``cc_free`` gives the room
# check) and calls ``cc_drop``; it calls ``cc_pop`` at each pop with the bar's key.

C_DROPPED, C_WOULD, C_FIRST, C_NEED, C_MINTOT, C_POPS, C_NENT, C_NHEAP, C_POOL = range(9)


@njit(inline="always")
def _bytes_less(pool, oa, na, ob, nb_):
    for t in range(min(na, nb_)):
        x, y = pool[oa + t], pool[ob + t]
        if x != y:
            return x < y
    return na < nb_


@njit(inline="always")
def _entry_less(cc, a, b):
    prio, depth, off, nb = cc[1], cc[2], cc[3], cc[4]
    if prio[a] != prio[b]:
        return prio[a] < prio[b]
    if depth[a] != depth[b]:
        return depth[a] < depth[b]
    return _bytes_less(cc[8], off[a], nb[a], off[b], nb[b])


@njit(inline="always")
def _hash_bytes(pool, o, n):
    h = np.uint64(1469598103934665603)
    p = np.uint64(1099511628211)
    for t in range(n):
        h = (h ^ np.uint64(pool[o + t])) * p
    return h ^ (h >> np.uint64(29))


@njit(inline="always")
def _find(cc, o, n):
    """Slot of the entry whose bytes equal ``pool[o:o+n]``, or the empty slot where it goes."""
    off, nb, table, pool = cc[3], cc[4], cc[7], cc[8]
    mask = len(table) - 1
    i = np.int64(_hash_bytes(pool, o, n) & np.uint64(mask))
    while table[i] != 0:
        e = table[i] - 1
        if nb[e] == n:
            same = True
            for t in range(n):
                if pool[off[e] + t] != pool[o + t]:
                    same = False
                    break
            if same:
                return i
        i = (i + 1) & mask
    return i


@njit(cache=True)
def cc_free(cc, entries, nbytes):
    """True when ``entries`` more entries holding ``nbytes`` more key bytes fit without growing."""
    st = cc[0]
    return (st[C_NENT] + entries <= len(cc[1]) and 2 * (st[C_NENT] + entries) <= len(cc[7])
            and st[C_POOL] + nbytes <= len(cc[8]))


@njit(cache=True)
def cc_known(cc, n):
    """Seed an ident (bytes at ``pool[st[C_POOL]:][:n]``) as already discovered: never pending."""
    st, off, nb, table = cc[0], cc[3], cc[4], cc[7]
    o = st[C_POOL]
    s = _find(cc, o, n)
    if table[s] == 0:
        e = st[C_NENT]
        off[e], nb[e] = o, n
        cc[1][e], cc[2][e], cc[5][e] = np.inf, 0, 0
        table[s] = e + 1
        st[C_NENT] = e + 1
        st[C_POOL] = o + n


@njit(cache=True)
def cc_drop(cc, prio, depth, n, total, longest):
    """The cap dropped a child whose key is ``(prio, depth, pool[st[C_POOL]:][:n])``."""
    st, off, nb, heap, table = cc[0], cc[3], cc[4], cc[6], cc[7]
    st[C_DROPPED] += 1
    if st[C_MINTOT] < 0 or total < st[C_MINTOT]:
        st[C_MINTOT] = total
    o = st[C_POOL]
    s = _find(cc, o, n)
    if table[s] != 0:
        return
    e = st[C_NENT]
    cc[1][e], cc[2][e], off[e], nb[e], cc[5][e] = prio, depth, o, n, longest
    table[s] = e + 1
    st[C_NENT] = e + 1
    st[C_POOL] = o + n
    i = st[C_NHEAP]
    st[C_NHEAP] = i + 1
    while i > 0:
        p = (i - 1) >> 1
        if _entry_less(cc, e, heap[p]):
            heap[i] = heap[p]
            i = p
        else:
            break
    heap[i] = e


@njit(cache=True)
def cc_pop(cc, prio, depth, bar, n):
    """One pop with bar key ``(prio, depth, bar[:n])``, before it expands."""
    st, eprio, edepth, off, nb, longest, heap, pool = cc[0], cc[1], cc[2], cc[3], cc[4], cc[5], cc[6], cc[8]
    st[C_POPS] += 1
    while st[C_NHEAP] > 0:
        e = heap[0]
        if eprio[e] != prio:
            if eprio[e] > prio:
                break
        elif edepth[e] != depth:
            if edepth[e] > depth:
                break
        else:
            o, m = off[e], nb[e]
            less = m < n
            for t in range(min(m, n)):
                if pool[o + t] != bar[t]:
                    less = pool[o + t] < bar[t]
                    break
            if not less:
                break
        hl = st[C_NHEAP] - 1                             # pop the pending top: it would have popped first
        st[C_NHEAP] = hl
        if hl > 0:
            v = heap[hl]
            i = 0
            while True:
                c = 2 * i + 1
                if c >= hl:
                    break
                if c + 1 < hl and _entry_less(cc, heap[c + 1], heap[c]):
                    c += 1
                if _entry_less(cc, heap[c], v):
                    heap[i] = heap[c]
                    i = c
                else:
                    break
            heap[i] = v
        st[C_WOULD] += 1
        if st[C_FIRST] < 0:
            st[C_FIRST] = st[C_POPS]
        if st[C_NEED] < 0 or longest[e] < st[C_NEED]:
            st[C_NEED] = longest[e]


class CapArrays:
    """The twin's arrays (``cc`` tuple), grown by doubling what is short (``grow``)."""

    def __init__(self, cap, entries=1 << 12, nbytes=1 << 16):
        self.cap = cap
        st = np.zeros(9, dtype=np.int64)
        st[C_FIRST] = st[C_NEED] = st[C_MINTOT] = -1
        self.cc = self._alloc(st, entries, nbytes)

    @staticmethod
    def _alloc(st, n, nbytes):
        return (st, np.empty(n, np.float64), np.empty(n, np.int64), np.empty(n, np.int64),
                np.empty(n, np.int32), np.empty(n, np.int32), np.empty(n, np.int32),
                np.zeros(1 << (2 * n - 1).bit_length(), np.int32), np.empty(nbytes, np.uint8))

    def grow(self, entries, nbytes):
        """Make room for ``entries`` more entries and ``nbytes`` more key bytes."""
        old = self.cc
        st = old[0]
        k, used = int(st[C_NENT]), int(st[C_POOL])
        n, pb = len(old[1]), len(old[8])
        while k + entries > n:
            n *= 2
        while used + nbytes > pb:
            pb *= 2
        if n == len(old[1]) and pb == len(old[8]):
            return
        new = self._alloc(st, n, pb)
        for a in (1, 2, 3, 4, 5):
            new[a][:k] = old[a][:k]
        new[6][:st[C_NHEAP]] = old[6][:st[C_NHEAP]]
        new[8][:used] = old[8][:used]
        _rehash(new, k)
        self.cc = new

    def free(self, entries, nbytes):
        return cc_free(self.cc, entries, nbytes)

    def tail(self):
        """The pool from the free offset: where the next key bytes are written."""
        return self.cc[8][self.cc[0][C_POOL]:]

    def drop(self, prio, depth, key, total, longest):
        """Python entry (tests, small searches): copy ``key`` bytes in, then ``cc_drop``."""
        if not self.free(1, len(key)):
            self.grow(1, len(key))
        self.tail()[:len(key)] = np.frombuffer(bytes(key), np.uint8)
        cc_drop(self.cc, float(prio), int(depth), len(key), int(total), int(longest))

    def known(self, key):
        if not self.free(1, len(key)):
            self.grow(1, len(key))
        self.tail()[:len(key)] = np.frombuffer(bytes(key), np.uint8)
        cc_known(self.cc, len(key))

    def pop(self, prio, depth, key):
        b = np.frombuffer(bytes(key), np.uint8)
        cc_pop(self.cc, float(prio), int(depth), b, len(b))

    def end(self, ran_dry, left):
        """``CapCount.end``: count what a dry queue would pop next, then drop the pending entries."""
        st = self.cc[0]
        h = int(st[C_NHEAP])
        if ran_dry and h > 0 and left > 0:
            st[C_WOULD] += min(h, left)
            if st[C_FIRST] < 0:
                st[C_FIRST] = st[C_POPS] + 1
            m = int(self.cc[5][self.cc[6][:h]].min())
            if st[C_NEED] < 0 or m < st[C_NEED]:
                st[C_NEED] = m
        st[C_NHEAP] = 0

    def record(self, prefix="cap"):
        st = [int(x) for x in self.cc[0]]
        neg = lambda x: None if x < 0 else x         # noqa: E731
        return dict(zip(fields(prefix), (self.cap, st[C_DROPPED], neg(st[C_MINTOT]), st[C_WOULD],
                                         neg(st[C_FIRST]), neg(st[C_NEED]))))


@njit(cache=True)
def _rehash(cc, k):
    table = cc[7]
    table[:] = 0
    for e in range(k):
        table[_find(cc, cc[3][e], cc[4][e])] = e + 1
