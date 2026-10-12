"""The hybrid's cap counters: what each of its three limits dropped, and whether a drop would have popped.

The hybrid cuts children in three places, each its own counter (``acx.core.capcount``; the field names are
``FIELDS`` under the prefix):

==========  ============================================  =============================================
prefix      limit                                         ``<prefix>_needed`` is
==========  ============================================  =============================================
``cap``     ``r2_cap`` (rank-two S-moves; ``"parent"``    the least ``r2_cap`` that admits the child
            never rejects: a child relator is at most     (its longest relator)
            ``l_i + l_j - 2``, below the parent's total)
``dyn_cap`` ``dyn_cap`` (higher-rank products and         the least ``dyn_cap`` that admits it
            eliminations)
``slack``   ``slack`` (the total-length ceiling above     the least ``slack`` that admits it (the
            the search root)                              child's total length minus the root's)
==========  ============================================  =============================================

``<prefix>_dropped_min_total`` is always an absolute total length. ``<prefix>_first_bind`` is a work
unit of the search (the unit number of the pop that would have been preceded by a dropped state; the
cascade's units before the search are not counted).

**The search is not a plain best-first queue**, so the comparison is made per pop against what the
loop actually served. A dropped child waits in a pool with the key ``(priority, depth, tick - 0.5)``
the child would have been pushed under (``tick`` the last insertion number used), bound for the
rank-two heap (pool 0) or the higher-rank heap (pool 1). Every loop iteration that pops an entry
(placeholders and entries skipped as seen included) gives each pool a bar:

* the higher-rank heap was served (top ``d``): rank-two pool bar ``(d.priority, -inf)`` (a rank-two
  entry wins only with a strictly smaller priority: ties go to the higher-rank heap), higher-rank pool
  bar ``d``;
* the rank-two heap was served (top ``h``): rank-two pool bar ``h``, higher-rank pool bar
  ``(h.priority, +inf)`` (a higher-rank entry would have been served at ``priority <= h.priority``) when
  the ratio and ``dyn_max`` rules would have allowed the higher-rank heap, none otherwise.

The hybrid dedups when it pops (the ``seen`` sets), so a drained entry counts only if its popped
identity is not seen yet and was not drained before (``accept``); a dropped rank-two child that would
have gone straight to the finishing gates (``gate_precheck_key``) counts at once. When the search ends
with both heaps empty (or only deferred higher-rank entries that are not served) the pending entries
would have popped next. The counts are first order: a dropped state is judged against the run that
happened, not against the run it would have changed. So a zero in all three counters guarantees that a
larger ``r2_cap``, ``dyn_cap`` or ``slack`` runs the same units and the same certificate, and a nonzero
count says the run may change.
"""
from ..core.capcount import CapCount, blank, fields

INF = float("inf")
NAMES = ("cap", "dyn_cap", "slack")
R2POOL, DYNPOOL = 0, 1


def blank_records(cfg):
    """The three records of a run that never reached the search (the cascade solved it): nothing was cut."""
    return {k: v for name, limit in zip(NAMES, (cfg.r2_cap, cfg.dyn_cap, cfg.slack))
            for k, v in blank(name, cap=limit).items()}


class Watch:
    """The three counters (a limit that is ``None`` has none) and their pools; see the module docstring."""

    def __init__(self, limits, ident_r2, ident_dyn, seen_r2, seen_dyn):
        self.limits = limits                      # {"cap": r2_cap, "dyn_cap": dyn_cap, "slack": slack}
        self.pools = {}
        for name in NAMES:
            if limits[name] is not None:
                self.pools[name] = (CapCount(limits[name], accept=self._accept(seen_r2, ident_r2)),
                                    CapCount(limits[name], accept=self._accept(seen_dyn, ident_dyn)))
        self.armed = False                        # set by the first drop: until then no pop has anything to compare

    @staticmethod
    def _accept(seen, ident):
        drained = set()

        def accept(payload):
            i = ident(payload)
            if i in seen or i in drained:
                return False
            drained.add(i)
            return True
        return accept

    def has(self, name):
        return name in self.pools

    def drop(self, name, pool, key, total, needed, payload):
        self.armed = True
        self.pools[name][pool].drop(key, total, needed, payload=payload)

    def drop_now(self, name, total, needed, units):
        self.armed = True
        cc = self.pools[name][R2POOL]
        first = cc.first_bind
        cc.drop_now(total, needed)
        if first is None:
            cc.first_bind = units

    def step(self, h, d, ok, units):
        """One popped entry. ``h``/``d``: the tops of the rank-two / higher-rank heap as they were before the
        pop, ``d`` is None when the rank-two heap is served; ``ok``: the ratio and ``dyn_max`` rules allow
        the higher-rank heap; ``units``: the unit number of this pop."""
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
        """The loop ended: ``dry`` it ran out of entries unsolved with ``left`` units of budget; ``ok``
        whether the higher-rank heap would have been served."""
        for pair in self.pools.values():
            for cc, ran_dry in zip(pair, (dry, dry and ok)):
                first = cc.first_bind
                cc.end(ran_dry, left)
                if first is None and cc.first_bind is not None:
                    cc.first_bind = units + 1

    def record(self, name):
        """The six fields of one limit, its two pools merged."""
        if name not in self.pools:
            return blank(name)
        f = fields(name)
        a, b = (cc.record(name) for cc in self.pools[name])
        out = dict(a)
        out[f[1]] = a[f[1]] + b[f[1]]
        out[f[3]] = a[f[3]] + b[f[3]]
        for i in (2, 4, 5):
            xs = [r[f[i]] for r in (a, b) if r[f[i]] is not None]
            out[f[i]] = min(xs) if xs else None
        return out

    def records(self):
        out = {}
        for name in NAMES:
            out.update(self.record(name))
        return out
