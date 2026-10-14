"""The hybrid's best-first search: one rank-two heap and one higher-rank heap, served by priority.

Rank two works on packed keys (``frontier``); higher ranks on ``dynrank`` states. The cap counters
(``capwatch``) watch what the three limits (``r2_cap``, ``dyn_cap``, ``slack``) drop.
"""
import heapq
from operator import itemgetter

import numpy as np

from ..core.moves import Move
from ..core.priority import length
from ..core.words import canonical_rels
from . import dynrank as D
from .capwatch import DYNPOOL, Watch, lazy_cut_entries, lazy_entries
from .cascade import gate_applicable, gate_precheck_key, run_gates
from .frontier import backend, grouped, orbits, over_cap, pack, unpack
from .steps import NIELSEN, Aut, Budget, Run, is_terminal

R2, DYN, DEFS = 0, 1, 2           # the kind of a heap entry: rank two, higher rank, deferred defines


def _dedup_sorted(items):
    """``(state, event)`` pairs sorted by state, the first of equal states kept."""
    out = []
    for state, event in sorted(items, key=lambda t: t[0]):
        if not out or out[-1][0] != state:
            out.append((state, event))
    return out


class _Done(Exception):
    """Raised inside the search when a solution is found or the budget is spent."""


class BestFirst:
    """The best-first search from ``run.state`` with a budget of ``budget`` units; ``go()`` runs it."""

    def __init__(self, run, cfg, budget):
        self.cfg, self.budget, self.clock, self.result = cfg, budget, 0, []
        self.expand, self.full, self.transform = backend(cfg.backend)
        self.expand_groups = grouped(cfg.backend)         # ``expand`` in the layout ``expand_r2`` pushes
        self.orbit = orbits(cfg.backend)                  # ``frontier.orbit`` of a key
        self.dyn = D.backend(cfg.backend)                 # the higher-rank moves, on the same backend
        self.base = sum(map(len, run.state))              # the root's total length
        self.ceiling = float("inf") if cfg.slack is None else self.base + cfg.slack
        root = pack(run.state)
        images = self.orbit(root)
        root = min(images)
        self.prefix = (Aut(images.index(root)),) if root != images[0] else ()
        self.heap = [(float(len(root) - 1), 0, 0, (root, None, (), R2))]
        self.dheap, self.seen_r2, self.seen_dyn = [], set(), set()
        self.st = dict(pops=0, dyn_pops=0, max_rank=2, dyn_rejected=0)
        limits = {"cap": cfg.r2_cap, "dyn_cap": cfg.dyn_cap, "slack": cfg.slack}
        self.watch = Watch(limits, self.seen_r2, self.seen_dyn, self.transform, self.dyn, self.orbit)

    def tick(self, n=1):
        """The first of ``n`` new insertion numbers, the last tie-break of the heaps (only compared, so a dropped child
        may take one: it is the place it would have had)."""
        self.clock += n
        return self.clock - n + 1

    def can_dyn(self):
        """May the higher-rank heap be served (its pops are at most ``dyn_ratio`` times the rank-two pops plus 20)?"""
        return self.st["dyn_pops"] <= self.cfg.dyn_ratio * (self.st["pops"] - self.st["dyn_pops"]) + 20

    def chain(self, node):
        """The steps from the root to ``node``. A node is ``(key, parent node, steps, kind)``."""
        parts = []
        while node[1] is not None:
            parts.append(node[2])
            node = node[1]
        return self.prefix + sum(reversed(parts), ())

    def try_finish(self, node, state):
        """Stop if ``state`` is trivial or the finishing gates (``cascade.run_gates``) solve it."""
        if is_terminal(state):
            self.result.append(self.chain(node))
            raise _Done()
        if not gate_applicable(state):
            return
        gate = Run(state, self.budget - self.st["pops"])
        try:
            ok = run_gates(gate)
        except Budget:
            self.st["pops"] = self.budget
            raise _Done()
        self.st["pops"] += gate.units
        if ok:
            self.result.append(self.chain(node) + tuple(gate.steps))
            raise _Done()

    def offer(self, cnode, depth, tick):
        """A rank-two child: the gates first, then the rank-two heap."""
        if gate_precheck_key(cnode[0]):
            self.try_finish(cnode, unpack(cnode[0]))
        heapq.heappush(self.heap, (float(len(cnode[0]) - 1), depth, tick, cnode))

    def offer_dyn(self, ckey, rl, parent, event, depth, tick):
        """A higher-rank child ``ckey`` (relabelled by ``rl``); a rank-two one goes to the rank-two heap."""
        cstep = ({"op": "dyn", "event": event, "relabel": rl, "after": ckey},)
        if len(ckey) == 2:
            self.offer((pack(canonical_rels(ckey)), parent, cstep, R2), depth, tick)
            return
        self.st["max_rank"] = max(self.st["max_rank"], len(ckey))
        prio = float(length(ckey) + self.cfg.penalty * (len(ckey) - 2))
        heapq.heappush(self.dheap, (prio, depth, tick, (ckey, parent, cstep, DYN)))

    def expand_r2(self, rep, state, node, depth):
        """Offer every child of the rank-two state ``rep`` (S-moves, then the four Nielsen maps), and park its defines.

        The S-move children are offered as ``offer`` would, one by one: the gates of those that pass the free test in
        their order (a counted cap drop in its place among them), then the heap. They go to the heap in groups of one
        key length, each group one entry, the head (``member``): its children share the priority and depth and have
        consecutive ticks no other entry has, so the heap pops them in the order it would pop them one by one, and
        the next one replaces the head when it pops (``_go``)."""
        cfg, watch = self.cfg, self.watch
        cap = len(rep) - 1 if cfg.r2_cap == "parent" else cfg.r2_cap
        raw, offs, moves, flagged, groups, rejected = self.expand_groups(rep, cap)
        count = len(offs) - 1
        drops = over_cap(self.full(rep), cap) if rejected and watch.has("cap") else None   # never under "parent"
        base = self.tick(count + (len(drops.pos) if drops else 0))
        hits, ticks = [], range(base, base + count)
        if drops:
            watch.moved("cap", rejected, int(drops.total.min()))
            hits = watch.drop_children("cap", depth, base, drops)
            shift = np.searchsorted(drops.before, np.arange(count), side="right").tolist()
            ticks = [t + s for t, s in zip(ticks, shift)]
        batch = (raw, offs, moves, ticks, node, depth)
        for j in flagged:
            while hits and hits[0][0] <= j:
                watch.drop_now("cap", *hits.pop(0)[1:], self.st["pops"] + 1)
            self.try_finish(self.member(batch, j, None), unpack(raw[offs[j]:offs[j + 1]]))
        while hits and hits[0][0] < count:
            watch.drop_now("cap", *hits.pop(0)[1:], self.st["pops"] + 1)
        for group in groups:
            j = group[0]
            heapq.heappush(self.heap, (float(offs[j + 1] - offs[j] - 1), depth, ticks[j],
                                       self.member(batch, j, (group[:0:-1], batch))))
        for k in NIELSEN:
            self.offer((self.transform(rep, k), node, (Aut(k),), R2), depth, self.tick())
        lower = float(len(rep) - 1 - self.dyn.most_uses(state) + 3 + cfg.penalty)
        heapq.heappush(self.dheap, (lower, depth, self.tick(), (None, node, state, DEFS)))

    @staticmethod
    def member(batch, j, group):
        """The node of child ``j`` of an ``expand_r2`` batch; with ``group`` (the members still to come, last first, and
        the batch) it is a group's head and has it as a fifth field."""
        raw, offs, moves, _, parent, _ = batch
        node = (raw[offs[j]:offs[j + 1]], parent, (Move(*moves[j].tolist()),), R2)
        return node if group is None else node + (group,)

    def next_member(self, head):
        """A group's head popped: push the next member as the head, and return the popped node as a plain node."""
        rest, batch = head[4]
        if rest:
            j = rest.pop()
            raw, offs, _, ticks, _, depth = batch
            heapq.heappush(self.heap, (float(offs[j + 1] - offs[j] - 1), depth, ticks[j], self.member(batch, j, head[4])))
        return head[:4]

    def offer_children(self, words, kept, drops, parent, depth):
        """Offer the higher-rank children ``kept`` of ``words`` (``(state, event)``, sorted and deduplicated here) and hand
        ``drops`` (``(name, offset, items)``: what the limit ``name`` rejected, see ``dynrank.children``) to the counters.
        A dropped child that is an elimination back to rank two goes through the gates, in its place among the offers."""
        watch, pen, make_key = self.watch, self.cfg.penalty, self.dyn.make_key
        lazy, short = [], []
        for name, offset, items in drops:
            if not items:
                continue
            if items.__class__ is list:
                watch.moved(name, len(items), min(map(itemgetter(0), items)))
                lazy.append((name, offset, [t for t in items if t[2] > 2]))
                short += [(t[3], (name, t[1] - offset)) for t in items if t[2] == 2]
            else:                                       # ``highspeedup.dynkernels.Cuts``: the same items, the products as arrays
                watch.moved(name, len(items), items.min_total())
                lazy.append((name, offset, items.above(2)))
                short += [(t[3], (name, t[1] - offset)) for t in items.elims if t[2] == 2]
        offered = _dedup_sorted(kept + short)
        base = self.tick(len(offered) + 1)
        states = [state for state, _ in offered]
        for name, offset, items in lazy:
            if items:
                entries = lazy_entries if items.__class__ is list else lazy_cut_entries
                watch.block(name, DYNPOOL, entries(depth, base, pen, offset, words, states, items, self.dyn.dcanon))
        for j, ((state, event), mk) in enumerate(zip(offered, self.dyn.make_keys(states)), base + 1):
            mk = mk or make_key(state)                  # one by one where the batch did not (spec, or it raises)
            if event.__class__ is tuple:                # an elimination to rank two that a limit rejected
                key = pack(canonical_rels(mk[0]))
                watch.drop_child(event[0], depth, j, key, event[1], self.st["pops"] + 1)
            else:
                self.offer_dyn(*mk, parent, event, depth, j)

    def expand_dyn(self, rep, node, depth):
        """Offer every child of the higher-rank state ``rep``."""
        cfg, st = self.cfg, self.st
        st["dyn_pops"] += 1
        kept, cut, over = self.dyn.children_lazy(rep, cfg.dyn_cap, self.ceiling, cfg.min_uses)
        st["dyn_rejected"] += len(cut) + len(over)
        self.offer_children(rep, kept, (("dyn_cap", 0, cut), ("slack", self.base, over)), node, depth)

    def expand_defs(self, state, parent, depth):
        """The deferred define children of a rank-two state (no charge)."""
        kept, over = [], []
        for cw, event in _dedup_sorted(self.dyn.defines(self.dyn.normalize(state), self.cfg.min_uses)):
            if length(cw) <= self.ceiling:
                kept.append((cw, event))
            else:
                over.append((length(cw), length(cw), len(cw), cw))
        self.st["dyn_rejected"] += len(over)
        self.offer_children(state, kept, (("slack", self.base, over),), parent, depth)

    def served_heap(self, dyn_ok):
        """The heap to pop: the higher-rank one when it is allowed and its top is no worse, else the rank-two one."""
        heap, dheap = self.heap, self.dheap
        return dheap if dyn_ok and dheap and (not heap or dheap[0][0] <= heap[0][0]) else heap

    def visit(self, rep, node, kind):
        """Mark ``rep`` visited. ``(rep, node)``, or None if it was visited before. At rank two the visited set is
        closed under the signed permutations and the entry becomes the least image (the permutation joins its steps)."""
        seen = self.seen_r2 if kind == R2 else self.seen_dyn
        if rep in seen:
            return None
        if kind != R2:
            seen.add(rep)
            return rep, node
        images = self.orbit(rep)
        seen.update(images)
        best = min(images)
        if best != rep:
            _, parent, steps, _ = node
            rep, node = best, (best, parent, steps + (Aut(images.index(best)),), R2)
        return rep, node

    def go(self):
        """Run the search; ``(solved, steps, stats)``. ``solver.solve`` pauses the cyclic garbage collector around it."""
        st, watch, heap, dheap = self.st, self.watch, self.heap, self.dheap
        try:
            while (heap or dheap) and st["pops"] < self.budget:
                dyn_ok = self.can_dyn()
                served = self.served_heap(dyn_ok)
                if not served:
                    break                               # only deferred higher-rank states remain
                if watch.armed:
                    watch.step(heap[0] if served is heap else None, dheap[0] if served is dheap else None,
                               dyn_ok and bool(dheap or watch.armed), st["pops"] + 1)
                _, depth, _, node = heapq.heappop(served)
                if len(node) == 5:                      # the head of a group of rank-two children (``expand_r2``)
                    node = self.next_member(node)
                rep, parent, steps, kind = node
                if kind == DEFS:                        # a placeholder carries its parent's pair in ``steps``
                    self.expand_defs(steps, parent, depth)
                    continue
                visited = self.visit(rep, node, kind)
                if visited is None:
                    continue
                rep, node = visited
                st["pops"] += 1
                if kind == DYN:
                    self.expand_dyn(rep, node, depth + 1)
                elif is_terminal(state := unpack(rep)):
                    self.result.append(self.chain(node))
                    raise _Done()
                else:
                    self.expand_r2(rep, state, node, depth + 1)
        except _Done:
            pass
        st["pops"] = min(st["pops"], self.budget)
        watch.end(not self.result and st["pops"] < self.budget, self.can_dyn(), self.budget - st["pops"], st["pops"])
        st.update(watch.records())
        watch.close()
        return bool(self.result), (self.result[0] if self.result else ()), st
