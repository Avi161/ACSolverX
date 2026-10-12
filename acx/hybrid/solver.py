"""The hybrid "solve everything" solver: stages A-C, then one best-first search over every rank.

``solve(pres, cfg)`` runs the cascade (``acx.hybrid.cascade``) and, with what is
left of the budget, a best-first search with two frontiers:

* **rank two**: packed keys (``acx.hybrid.frontier``) expanded by the S-moves
  (a child relator may not be longer than the parent's total length, unless
  ``r2_cap`` sets a fixed cap, or ``None`` removes it) plus the four Nielsen maps; a popped state is
  first replaced by its least image under the eight signed permutations (the
  permutation joins its step). Every generated child that passes the free key
  precheck goes through the finishing gates (``cascade.run_gates``).
* **higher rank** (``acx.hybrid.dynrank``): a popped rank-two state also offers
  its ``define`` children, generated lazily: one placeholder with the priority
  the best of them could have waits in this frontier and is expanded only if
  the frontier is served at that priority. A higher-rank state is expanded by
  capped products (``dyn_cap``), definitions, eliminations and transvections
  within a total-length ceiling (the search root's total plus ``slack``); a
  child that returns to rank two re-enters the rank-two frontier.

Priorities: total length at rank two; total length plus ``penalty`` per
generator above two at higher rank. The higher-rank frontier is served when its
best priority is no worse and its pops are at most ``dyn_ratio`` times the
rank-two pops plus 20 (and fewer than ``dyn_max``, if set). Ties: depth, then
insertion order. Each frontier has a visited set checked at pop time. One work
unit per popped state of either rank, plus the cascade's charges and the gates'.
A placeholder's lower bound is ``total - (most uses of one digram) + 3 + penalty``.
``stats`` of a search: ``pops``, ``dyn_pops``, ``max_rank``, ``dyn_rejected`` (higher-rank moves over
``dyn_cap`` or the ceiling) and the cap counters of the three limits (``acx.hybrid.capwatch``):
``cap_*`` (rank-two moves over ``r2_cap``; zero by construction under ``"parent"``), ``dyn_cap_*``
and ``slack_*``, each with the children dropped and whether a dropped state would have been popped,
so a cap never decides the run silently.

Outputs are typed: a certificate with no higher-rank step is an ``ac_path``
(AC moves and automorphisms of F2); one with higher-rank steps is a
``stable_cert``. Either way ``acx.hybrid.certify`` writes it out as elementary
(and, for a ``stable_cert``, stabilisation) moves on the presentation itself and
``acx.verify.replay`` must accept them before ``solve`` returns a solve.

Port of ``origin/claude/vigilant-babbage-nnbuj0:research/ac_hashfree_cascade_20260914/
hfhybrid.py`` (``search``, ``solve``; commit 5ae1bd8e). Changes: the visited sets are
Python sets (the source kept block-sorted arrays to avoid hashing; the pop order
is the same), the rank-two kernel is ``acx.search.fast.kernels.expand`` (or the
pure-Python ``spec`` expansion), and certificates replay through ``acx.verify``.
Defaults are the source's final setting (budget 1,000 units, penalty 5,
dyn_ratio 0.5, cap 8, slack 8): MS640 640/640, AC19 aut-min 72,779/72,779.
"""
import heapq
import time
from operator import itemgetter
from dataclasses import dataclass, field, replace

import numpy as np

from ..core.config import parse_cap
from ..core.moves import Move
from ..core.priority import length
from ..core.words import Presentation, canonical_rels
from . import dynrank as D
from .capwatch import DYNPOOL, Watch, blank_records, lazy_entries
from .cascade import NIELSEN, Aut, Budget, Run, cascade, gate_applicable, gate_precheck_key, is_terminal, run_gates
from .certify import certify
from .frontier import BACKENDS, backend, orbit, over_cap, pack, unpack

R2, DYN, DEFS = 0, 1, 2


@dataclass(frozen=True)
class HybridConfig:
    budget: int = 1000                # work units
    penalty: int = 5                  # priority letters per generator above two
    dyn_ratio: float = 0.5            # higher-rank pops <= dyn_ratio * rank-two pops + 20
    dyn_cap: int | None = 8           # longest relator a higher-rank product or elimination may create; None = uncapped
    slack: int = 8                    # higher-rank total-length ceiling above the search root
    min_uses: int = 2                 # a defined digram must occur this often
    r2_cap: int | str | None = "parent"   # rank-two relator cap: "parent" (the parent's total length, the source's rule), an int, or None (uncapped)
    backend: str = "fast"             # rank-two expansion: "spec" (pure Python) | "fast" (numba)
    certify: bool = True              # write out and replay the elementary path

    def __post_init__(self):
        if self.backend not in BACKENDS:
            raise ValueError(f"backend {self.backend!r} not in {BACKENDS}")
        object.__setattr__(self, "r2_cap", parse_cap(self.r2_cap, "r2_cap", keep=("parent",)))
        object.__setattr__(self, "dyn_cap", parse_cap(self.dyn_cap, "dyn_cap"))

    def replace(self, **kw):
        return replace(self, **kw)


@dataclass(frozen=True)
class HybridResult:
    solved: bool
    stage: str | None                 # "terminal", "B", "C" (cascade) or "H" (search)
    units: int
    steps: tuple                      # the certificate from the canonical start: Move / Aut / dyn dicts
    kind: str | None                  # "ac_path" or "stable_cert"
    path: tuple | None = None         # elementary moves on the presentation, replayed (cfg.certify)
    stats: dict = field(default_factory=dict)


def _dedup_sorted(items):
    """``(state, event)`` pairs sorted by state, the first of equal states kept."""
    out = []
    for state, event in sorted(items, key=lambda t: t[0]):
        if not out or out[-1][0] != state:
            out.append((state, event))
    return out


class _Done(Exception):
    pass


class _Search:
    """The best-first search from ``run.state`` with a budget of ``budget`` units; ``go()`` runs it."""

    def __init__(self, run, cfg, budget):
        self.cfg, self.budget, self.clock, self.result = cfg, budget, 0, []
        self.expand, self.full, self.transform = backend(cfg.backend)
        self.base = sum(map(len, run.state))              # the root's total length
        self.ceiling = self.base + cfg.slack
        root = pack(run.state)
        images = orbit(root, self.transform)
        root = min(images)
        self.prefix = (Aut(images.index(root)),) if root != images[0] else ()
        self.heap = [(float(len(root) - 1), 0, 0, (root, None, (), R2))]
        self.dheap, self.seen_r2, self.seen_dyn = [], set(), set()
        self.st = dict(pops=0, dyn_pops=0, max_rank=2, dyn_rejected=0)
        self.watch = Watch({"cap": cfg.r2_cap, "dyn_cap": cfg.dyn_cap, "slack": cfg.slack}, self.seen_r2, self.seen_dyn)

    def tick(self, n=1):
        """The first of ``n`` new insertion numbers, the last tie-break of the heaps (only compared, so a dropped child
        may take one: it is the place it would have had)."""
        self.clock += n
        return self.clock - n + 1

    def can_dyn(self):
        """May the higher-rank heap be served (its pops are at most ``dyn_ratio`` times the rank-two pops plus 20)?"""
        return self.st["dyn_pops"] <= self.cfg.dyn_ratio * (self.st["pops"] - self.st["dyn_pops"]) + 20

    def chain(self, node):
        out = []
        while node[1] is not None:
            out.append(node[2])
            node = node[1]
        return self.prefix + sum(reversed(out), ())

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
        """Offer every child of the rank-two state ``rep`` (S-moves, then the four Nielsen maps), and park its defines."""
        cfg, watch = self.cfg, self.watch
        cap = len(rep) - 1 if cfg.r2_cap == "parent" else cfg.r2_cap
        children, rejected = self.expand(rep, cap)
        drops = over_cap(self.full(rep), cap) if rejected and watch.has("cap") else None   # never under "parent"
        base = self.tick(len(children) + (len(drops.pos) if drops else 0))
        hits, shift = [], ()
        if drops:
            watch.moved("cap", rejected, int(drops.total.min()))
            hits = watch.drop_children("cap", depth, base, drops)
            shift = np.searchsorted(drops.before, np.arange(len(children)), side="right").tolist()
        for j, (child, move) in enumerate(children):
            while hits and hits[0][0] <= j:
                watch.drop_now("cap", *hits.pop(0)[1:], self.st["pops"] + 1)
            self.offer((child, node, (move,), R2), depth, base + j + (shift[j] if shift else 0))
        for k in NIELSEN:
            self.offer((self.transform(rep, k), node, (Aut(k),), R2), depth, self.tick())
        lower = float(len(rep) - 1 - max(D.digram_counts(state).values(), default=0) + 3 + cfg.penalty)
        heapq.heappush(self.dheap, (lower, depth, self.tick(), (None, node, state, DEFS)))

    def offer_children(self, words, kept, drops, parent, depth):
        """Offer the higher-rank children ``kept`` of ``words`` (``(state, event)``, sorted and deduplicated here) and hand
        ``drops`` (``(name, offset, items)``: what the limit ``name`` rejected, see ``dynrank.children``) to the counters.
        A dropped child that is an elimination back to rank two goes through the gates, in its place among the offers."""
        watch, pen = self.watch, self.cfg.penalty
        lazy, short = [], []
        for name, offset, items in drops:
            if items:
                watch.moved(name, len(items), min(map(itemgetter(0), items)))
                lazy.append((name, offset, [t for t in items if t[2] > 2]))
                short += [(t[3], (name, t[1] - offset)) for t in items if t[2] == 2]
        offered = _dedup_sorted(kept + short)
        base = self.tick(len(offered) + 1)
        states = [state for state, _ in offered]
        for name, offset, items in lazy:
            if items:
                watch.block(name, DYNPOOL, lazy_entries(depth, base, pen, offset, words, states, items))
        for j, (state, event) in enumerate(offered, base + 1):
            if event.__class__ is tuple:                # an elimination to rank two that a limit rejected
                key = pack(canonical_rels(D.make_key(state)[0]))
                watch.drop_child(event[0], depth, j, key, event[1], self.st["pops"] + 1)
            else:
                self.offer_dyn(*D.make_key(state), parent, event, depth, j)

    def expand_dyn(self, rep, node, depth):
        """Offer every child of the higher-rank state ``rep``."""
        cfg, st = self.cfg, self.st
        st["dyn_pops"] += 1
        kept, cut, over = D.children(rep, cfg.dyn_cap, self.ceiling, cfg.min_uses)
        st["dyn_rejected"] += len(cut) + len(over)
        self.offer_children(rep, kept, (("dyn_cap", 0, cut), ("slack", self.base, over)), node, depth)

    def expand_defs(self, state, parent, depth):
        """The deferred define children of a rank-two state (no charge)."""
        kept, over = [], []
        for cw, event in _dedup_sorted(D.defines(D.normalize(state), self.cfg.min_uses)):
            if length(cw) <= self.ceiling:
                kept.append((cw, event))
            else:
                over.append((length(cw), length(cw), len(cw), cw))
        self.st["dyn_rejected"] += len(over)
        self.offer_children(state, kept, (("slack", self.base, over),), parent, depth)

    def go(self):
        """Run the search; ``(solved, steps, stats)``."""
        st, watch, heap, dheap = self.st, self.watch, self.heap, self.dheap
        try:
            while (heap or dheap) and st["pops"] < self.budget:
                dyn_ok = self.can_dyn()
                served = dheap if dyn_ok and dheap and (not heap or dheap[0][0] <= heap[0][0]) else heap
                if not served:
                    break                               # only deferred higher-rank states remain
                if watch.armed:
                    watch.step(heap[0] if served is heap else None, dheap[0] if served is dheap else None,
                               dyn_ok and bool(dheap or watch.armed), st["pops"] + 1)
                _, depth, _, node = heapq.heappop(served)
                rep, parent, steps, kind = node
                if kind == DEFS:                        # a placeholder carries its parent's pair in ``steps``
                    self.expand_defs(steps, parent, depth)
                    continue
                seen = self.seen_r2 if kind == R2 else self.seen_dyn
                if rep in seen:
                    continue
                if kind == R2:                          # seen is closed under the signed permutations
                    images = orbit(rep, self.transform)
                    seen.update(images)
                    best = min(images)
                    if best != rep:
                        rep, node = best, (best, parent, steps + (Aut(images.index(best)),), R2)
                else:
                    seen.add(rep)
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
        return bool(self.result), (self.result[0] if self.result else ()), st


def search(run, cfg, budget):
    """The best-first hybrid search from ``run.state``; ``(solved, steps, stats)``."""
    return _Search(run, cfg, budget).go()


def solve(pres, cfg=None, **overrides):
    """Solve ``pres`` (a ``Presentation`` or two relator strings); see the module docstring."""
    cfg = (cfg or HybridConfig()).replace(**overrides)
    if not isinstance(pres, Presentation):
        pres = Presentation.parse(*pres)
    if pres.n_gen != 2 or len(pres.rels) != 2:
        raise ValueError("the hybrid solves balanced two-generator presentations")
    t0 = time.perf_counter()
    run = Run(pres.rels, cfg.budget)
    stats = blank_records(cfg)                           # the cascade has no caps; a search replaces these
    try:
        stage = cascade(run)
    except Budget:
        return HybridResult(False, None, cfg.budget, (), None, stats=dict(seconds=time.perf_counter() - t0, **blank_records(cfg)))
    if stage is not None:
        solved, steps, units = True, tuple(run.steps), 1 if stage == "terminal" else run.units
    else:
        solved, steps, stats = search(run, cfg, cfg.budget - run.units)
        steps, units, stage = tuple(run.steps) + steps, min(run.units + stats["pops"], cfg.budget), "H"
    stats["seconds"] = time.perf_counter() - t0
    if not solved:
        return HybridResult(False, None, units, (), None, stats=stats)
    kind = "stable_cert" if any(isinstance(s, dict) for s in steps) else "ac_path"
    path = None
    if cfg.certify:
        path = tuple(certify(pres, steps))
    return HybridResult(True, stage, units, steps, kind, path, stats)


def encode_steps(steps):
    """JSON form of a certificate: ``[i, j, s, k1, k2]``, ``{"aut": k}`` or the dyn dict (lists for tuples)."""
    def js(x):
        if isinstance(x, dict):
            return {str(k): js(v) for k, v in x.items()}
        return [js(v) for v in x] if isinstance(x, (tuple, list)) else x
    return [{"aut": s.k} if isinstance(s, Aut) else js(s) if isinstance(s, dict) else list(s) for s in steps]


def decode_steps(items):
    """Inverse of ``encode_steps``."""
    def tup(x):
        return tuple(map(tup, x)) if isinstance(x, list) else x

    def dyn(d):
        ev = {k: tup(v) for k, v in d["event"].items()}
        rl = d["relabel"] and {k: {int(g): v for g, v in m.items()} for k, m in d["relabel"].items()}
        return {"op": "dyn", "event": ev, "relabel": rl, "after": tup(d["after"])}
    return tuple(Move(*s) if isinstance(s, list) else Aut(s["aut"]) if "aut" in s else dyn(s) for s in items)
