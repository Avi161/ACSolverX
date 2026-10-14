"""The hybrid's cap counters: what its three limits (``r2_cap``, ``dyn_cap``, ``slack``) dropped, and whether it would have popped.

Each limit has a rank-two pool and a higher-rank pool of ``acx.core.capcount.CapCount``; the fields are ``FIELDS`` under the
prefixes ``cap``, ``dyn_cap`` and ``slack``. ``Watch`` has the rules and the cost.
"""
from bisect import bisect_left
from functools import lru_cache, partial
from itertools import groupby
from operator import itemgetter

import numpy as np

from ..core.capcount import PREFIXES, CapCount, blank, fields
from . import dynrank as D
from .cascade import gate_applicable, run_gates
from .frontier import orbit, unpack
from .steps import Run

INF = float("inf")
R2POOL, DYNPOOL = 0, 1


@lru_cache(maxsize=1 << 16)
def gates_act(key):
    """Would the finishing gates solve the canonical pair ``key`` or spend units on it? Whatever the budget: a
    budget too small to finish makes them act as well."""
    state = unpack(key)
    if not gate_applicable(state):
        return False
    run = Run(state, 1 << 60)
    return run_gates(run) or run.units > 0


def lazy_entries(depth, base, penalty, offset, words, offered, items, dcanon=D.dcanon):
    """The pool entries ``(key, total, needed, state)`` of the higher-rank children one pop's limit rejected (``items``, as
    ``dynrank.children`` returns them), in key order, built only as far as a bar reaches. Ahead of each priority group stands
    a marker (state None) whose key bounds the group's from below, so a group of hundreds costs nothing until a bar passes
    it. ``offered``: the sorted states the pop did offer, the ``j``-th with the tick ``base + 1 + j``; a dropped state
    takes a tick between its neighbours, and one equal to an offered state is not new. ``needed - offset`` is the value
    the counter reports. ``dcanon``: the backend's (``dynrank.backend``)."""
    prio = lambda t: t[0] + penalty * (t[2] - 2)
    last = min(map(itemgetter(0), items)) + penalty            # no rank-two child is here, so no priority is lower
    yield (float(last), depth, base), 0, 0, None
    items.sort(key=prio)
    for p, group in groupby(items, prio):
        if p != last:
            yield (float(p), depth, base), 0, 0, None
            last = p
        found = {}
        for total, needed, _, payload in group:
            if payload[0].__class__ is int:                    # (i, product): relator i replaced
                payload = tuple(sorted(words[:payload[0]] + (dcanon(payload[1]),) + words[payload[0] + 1:]))
            at = bisect_left(offered, payload)
            if payload not in found and not (at < len(offered) and offered[at] == payload):
                found[payload] = (total, needed - offset)
        for r, state in enumerate(sorted(found)):
            yield (float(p), depth, base + bisect_left(offered, state) + (r + 1) / (len(found) + 1)), *found[state], state


def lazy_cut_entries(depth, base, penalty, offset, words, offered, cuts, dcanon=D.dcanon):
    """``lazy_entries`` of ``cuts`` (a ``highspeedup.dynkernels.Cuts`` of items of rank above two, the list it stands
    for): the same entries, in the same order, an item built only when a bar reaches its priority group."""
    last = cuts.min_total() + penalty
    yield (float(last), depth, base), 0, 0, None
    prios = np.concatenate((cuts.total + penalty * (cuts.rank - 2),
                            np.array([t[0] + penalty * (t[2] - 2) for t in cuts.elims], dtype=np.int64)))
    order = np.argsort(prios, kind="stable")                  # ``items.sort(key=prio)``: stable
    sorted_prios = prios[order]
    starts = [0, *(np.flatnonzero(sorted_prios[1:] != sorted_prios[:-1]) + 1).tolist(), len(order)]
    order, sorted_prios = order.tolist(), sorted_prios.tolist()
    for a, b in zip(starts, starts[1:]):
        p = sorted_prios[a]
        if p != last:
            yield (float(p), depth, base), 0, 0, None
            last = p
        found = {}
        for k in order[a:b]:
            total, needed, _, payload = cuts.item(k)
            if payload[0].__class__ is int:                    # (i, product): relator i replaced
                payload = tuple(sorted(words[:payload[0]] + (dcanon(payload[1]),) + words[payload[0] + 1:]))
            at = bisect_left(offered, payload)
            if payload not in found and not (at < len(offered) and offered[at] == payload):
                found[payload] = (total, needed - offset)
        for r, state in enumerate(sorted(found)):
            yield (float(p), depth, base + bisect_left(offered, state) + (r + 1) / (len(found) + 1)), *found[state], state


def blank_records(cfg):
    """The three records of a run that never reached the search (the cascade solved it): nothing was cut."""
    return {k: v for name, limit in zip(PREFIXES, (cfg.r2_cap, cfg.dyn_cap, cfg.slack))
            for k, v in blank(name, cap=limit).items()}


class Watch:
    """The counters of the three limits (a limit that is ``None`` has none).

    ============  =========================================  ==================================================
    prefix        limit                                      ``<prefix>_needed`` is the least value that admits
    ============  =========================================  ==================================================
    ``cap``       ``r2_cap`` (``"parent"`` never rejects)    the child's longest relator
    ``dyn_cap``   higher-rank products and eliminations      the child's longest relator
    ``slack``     total length above the search root         the child's total length minus the root's
    ============  =========================================  ==================================================

    ``<prefix>_dropped`` counts rejected moves, ``_would_pop`` distinct states, ``_first_bind`` is a work unit of the
    search (the cascade's units are not counted), ``_dropped_min_total`` an absolute total length.

    The search is not one queue, so a dropped child waits in a pool under the key ``(priority, depth, tick)`` it would
    have been pushed with (``tick`` is the insertion order, only compared) and every pop that serves an entry gives
    each pool a bar: when the higher-rank heap is served (top ``d``) the rank-two bar is ``(d.priority, -inf)`` and the
    higher-rank bar ``d``; when the rank-two heap is served (top ``h``) the rank-two bar is ``h`` and the higher-rank bar
    ``(h.priority, +inf)``, or none if the ratio rule would not have served the higher-rank heap. A pooled key that sorts
    before a bar is drained: it counts if the search has not popped that state (``seen``) and no earlier drain counted
    it, both up to signed permutation at rank two (the search visits a state's whole orbit at once). A dropped rank-two
    child on which the finishing gates would act (solve it or spend units) counts at once. On a dry queue the pending
    states count too. The counts are first order: a dropped state is judged against the run that happened, so zero in
    all three means a larger limit pops the same states in the same order, and a nonzero count says only that the run
    may change.

    Cost: the children one rank-two pop drops arrive as arrays (``frontier.over_cap``) and wait as one lazy block, so a
    dropped child costs Python time only when a bar passes it; the exception is the exact gate test (``gates_act``) of
    the children that pass the free precheck, which is the larger part of what a tight ``r2_cap`` adds.
    """

    def __init__(self, limits, seen_r2, seen_dyn, transform, dyn=D.SPEC, orbit_of=None):
        self.armed = False                        # set by the first drop: until then no pop has anything to compare
        self.make_key = dyn.make_key              # the higher-rank moves of the search's backend (``dynrank.backend``)
        self.orbit = orbit_of or partial(orbit, transform=transform)    # ``frontier.orbit`` of a key
        self.seen_r2, self.seen_dyn, self.transform, self.live = seen_r2, seen_dyn, transform, []
        self.moves, self.mintot, self.pools = {}, {}, {}
        for name in PREFIXES:
            if limits[name] is not None:
                r2, dyn = CapCount(limits[name]), CapCount(limits[name])
                r2.accept = partial(self._accept_r2, r2, set())
                dyn.accept = partial(self._accept_dyn, dyn, set())
                self.pools[name] = (r2, dyn)
                self.moves[name], self.mintot[name] = 0, None

    def has(self, name):
        """Does the limit ``name`` have a counter?"""
        return name in self.pools

    def moved(self, name, n, total):
        """``n`` moves rejected by ``name``, the least leading to a child of ``total`` letters."""
        self.moves[name] += n
        if self.mintot[name] is None or total < self.mintot[name]:
            self.mintot[name] = total

    def block(self, name, pool, entries):
        """Pool ``pool`` of ``name`` takes the dropped children that ``entries`` yields in key order, as they are needed."""
        self.armed = True
        cc = self.pools[name][pool]
        self.live.append((cc, entries))
        self._push(cc, entries)

    def drop_now(self, name, total, needed, units):
        """A rank-two child the finishing gates would have acted on at pop ``units``."""
        self.armed = True
        cc = self.pools[name][R2POOL]
        first = cc.first_bind
        cc.drop_now(total, needed)
        if first is None:
            cc.first_bind = units

    def drop_children(self, name, depth, base, d):
        """The rank-two children ``d`` (``frontier.over_cap``) that ``name`` rejected at one pop; child ``i`` takes
        the tick ``base + d.pos[i]``. The pool gets all but those the finishing gates would act on; those come back as
        ``(kept children before it, total, longest)`` for the search to count (``drop_now``) at their place."""
        self.armed = True
        acting = [i for i in np.flatnonzero(d.flag).tolist() if gates_act(d.raw[d.start[i]:d.end[i]])]
        idx = np.lexsort((d.pos, d.total))
        idx = np.delete(idx, np.flatnonzero(np.isin(idx, acting)))
        entries = (((float(t), depth, base + p), t, n, d.raw[a:b]) for t, p, n, a, b in zip(
            d.total[idx].tolist(), d.pos[idx].tolist(), d.longest[idx].tolist(), d.start[idx].tolist(),
            d.end[idx].tolist()))
        self.block(name, R2POOL, entries)
        return [(int(d.before[i]), int(d.total[i]), int(d.longest[i])) for i in acting]

    def drop_child(self, name, depth, tick, key, needed, units):
        """One canonical rank-two child (``key``) that ``name`` rejected at pop ``units`` (a higher-rank elimination)."""
        total = len(key) - 1
        if gates_act(key):
            self.drop_now(name, total, needed, units)
            return
        self.block(name, R2POOL, iter([((float(total), depth, tick), total, needed, key)]))

    @staticmethod
    def _push(cc, entries):
        e = next(entries, None)
        if e is not None:
            cc.drop(e[0], e[1], e[2], payload=(e[3], entries))

    def _accept_r2(self, cc, drained, payload):
        key, entries = payload
        self._push(cc, entries)                   # the next of the block takes this one's place in the pool
        if key in self.seen_r2 or key in drained:
            return False
        drained.update(self.orbit(key))           # its signed permutations are the same state
        return True

    def _accept_dyn(self, cc, drained, payload):
        words, entries = payload
        self._push(cc, entries)
        if words is None:                         # a marker: the group behind it is built now
            return False
        ident = self.make_key(words)[0]
        if ident in self.seen_dyn or ident in drained:
            return False
        drained.add(ident)
        return True

    def step(self, h, d, ok, units):
        """One popped entry. ``h``/``d``: the tops of the rank-two / higher-rank heap as they were before the
        pop, ``d`` is None when the rank-two heap is served; ``ok``: the ratio rule allows the higher-rank heap;
        ``units``: the unit number of this pop."""
        if d is not None:
            bars = ((d[0], -INF), d[:3])
        else:
            bars = (h[:3], (h[0], INF) if ok else None)
        for pair in self.pools.values():
            for cc, bar in zip(pair, bars):
                if cc.pending:
                    first = cc.first_bind
                    cc.pop(bar)
                    if first is None and cc.first_bind is not None:
                        cc.first_bind = units

    def end(self, dry, ok, left, units):
        """The loop ended: ``dry`` it ran out of entries unsolved with ``left`` units of budget; ``ok`` whether the
        higher-rank heap would have been served."""
        for cc, entries in self.live if dry else ():
            for e in entries:
                cc.drop(e[0], e[1], e[2], payload=(e[3], iter(())))
        for pair in self.pools.values():
            for cc, ran_dry in zip(pair, (dry, dry and ok)):
                first = cc.first_bind
                cc.end(ran_dry, left)
                if first is None and cc.first_bind is not None:
                    cc.first_bind = units + 1

    def close(self):
        """The search is over: drop the lazy blocks and the pools' callbacks (a reference cycle through ``self``), so
        reference counting frees them at once (``solver.solve`` runs the search with the cyclic collector paused)."""
        self.live = []
        for pair in self.pools.values():
            for cc in pair:
                cc.accept = None

    def record(self, name):
        """The six fields of one limit, its two pools merged."""
        if name not in self.pools:
            return blank(name)
        f = fields(name)
        a, b = (cc.record(name) for cc in self.pools[name])
        out = dict(a)
        out[f[1]], out[f[2]] = self.moves[name], self.mintot[name]
        out[f[3]] = a[f[3]] + b[f[3]]
        for i in (4, 5):
            xs = [r[f[i]] for r in (a, b) if r[f[i]] is not None]
            out[f[i]] = min(xs) if xs else None
        return out

    def records(self):
        """All 18 fields."""
        return {k: v for name in PREFIXES for k, v in self.record(name).items()}
