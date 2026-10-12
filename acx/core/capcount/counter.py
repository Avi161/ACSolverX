"""``CapCount``: the plain Python counter of what one relator cap dropped."""
from heapq import heappop, heappush

from .records import fields

# A dropped state waiting for a later pop is the plain tuple ``(key, arrival, longest, payload)`` (a tuple, not
# a NamedTuple, because ``drop`` runs once per move): it orders by ``key``, then ``arrival`` (the tie-break, so
# equal keys never compare their payloads); ``longest`` is the longest relator of the dropped state.
KEY, LONGEST, PAYLOAD = 0, 2, 3


class CapCount:
    """The counter of one cap. A search tells it three things:

    * ``drop(key, total, longest, ident)``: the cap dropped a child (one call per move). ``key`` is the full heap
      key the active priority would have pushed the child under, e.g. ``(priority, depth, state_bytes)``; ``ident``
      names the state, so each state is judged once, under the key of its first drop (a search dedups on
      discovery, so a state is pushed at most once, by its first discoverer).
    * ``pop(bar)``: the search popped an entry with key ``bar``; call it BEFORE expanding, the solving pop
      included. Every pending dropped key sorting strictly before ``bar`` is a state the search would have popped
      first with a larger cap.
    * ``end(ran_dry, left)``: the search stopped. ``ran_dry``: the queue emptied unsolved with ``left > 0`` pops
      of budget left, so the pending dropped states would have popped next (up to ``left``). A search that solved or
      spent its budget passes ``ran_dry=False``.

    Keys are any totally ordered values. ``record(prefix)`` returns the six ``FIELDS`` (``cap`` renamed ``prefix``),
    which ``docs/CAP.md`` defines.

    For a best-first search with a strict total order on keys, ``cap_would_pop == 0`` holds exactly when every
    larger cap pops the same states in the same order with the same path, and a cap below ``cap_needed`` gives
    the same search while one at or above it does not.

    ``known``: idents already discovered (the start), so a dropped child equal to one counts in ``cap_dropped``
    only. ``accept(payload)``: optional pop-time dedup for a search that dedups when it pops; a drained entry
    counts only if it returns True.
    """

    __slots__ = ("cap", "accept", "dropped", "would_pop", "pops", "min_total", "first_bind", "needed",
                 "_pending", "_seen", "_arrivals")

    def __init__(self, cap, accept=None, known=()):
        self.cap = cap
        self.accept = accept
        self.dropped = 0
        self.would_pop = 0
        self.pops = 0
        self.min_total = None
        self.first_bind = None
        self.needed = None
        self._pending = []              # heap of (key, arrival, longest, payload)
        self._seen = set(known)         # idents already dropped or discovered
        self._arrivals = 0

    def drop(self, key, total, longest, ident=None, payload=None):
        """The cap dropped a child (one call per move); ``ident`` None means no dedup."""
        self._count_drop(total)
        if ident is not None:
            if ident in self._seen:
                return
            self._seen.add(ident)
        self._arrivals += 1
        heappush(self._pending, (key, self._arrivals, longest, payload))

    def drop_now(self, total, longest):
        """A dropped child the search would have acted on at once (a beam slot, a finishing gate)."""
        self._count_drop(total)
        self._would_have_popped(longest, at_pop=self.pops)

    def pop(self, bar):
        """One pop, before it expands. ``bar`` None only advances the pop number."""
        self.pops += 1
        if bar is None:
            return
        while self._pending and self._pending[0][KEY] < bar:
            entry = heappop(self._pending)
            if self.accept is None or self.accept(entry[PAYLOAD]):
                self._would_have_popped(entry[LONGEST], at_pop=self.pops)

    def end(self, ran_dry, left):
        """The search stopped; ``ran_dry``: the queue emptied unsolved with ``left > 0`` budget."""
        if ran_dry and self._pending and left > 0:
            in_pop_order = sorted(self._pending)
            if self.accept is not None:
                in_pop_order = [entry for entry in in_pop_order if self.accept(entry[PAYLOAD])]
            for rank, entry in enumerate(in_pop_order):
                # Every pending state bounds ``needed``; only the first ``left`` would fit in the budget.
                self._would_have_popped(entry[LONGEST], at_pop=self.pops + 1, counts=rank < left)
        self._pending = []
        self._seen = set()

    @property
    def pending(self):
        """Number of dropped states still waiting for a later pop."""
        return len(self._pending)

    def record(self, prefix="cap"):
        """The counter's ``FIELDS`` as a dict."""
        values = (self.cap, self.dropped, self.min_total, self.would_pop, self.first_bind, self.needed)
        return dict(zip(fields(prefix), values))

    def _count_drop(self, total):
        self.dropped += 1
        if self.min_total is None or total < self.min_total:
            self.min_total = total

    def _would_have_popped(self, longest, at_pop, counts=True):
        """A dropped state would have popped at pop number ``at_pop`` (it counts in ``would_pop`` if ``counts``)."""
        if counts:
            self.would_pop += 1
        if self.first_bind is None:
            self.first_bind = at_pop
        if self.needed is None or longest < self.needed:
            self.needed = longest
