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
from dataclasses import dataclass, field, replace

from ..core.config import parse_cap
from ..core.moves import Move
from ..core.priority import length
from ..core.words import Presentation, canonical_rels
from . import dynrank as D
from .cascade import NIELSEN, Aut, Budget, Run, cascade, gate_applicable, gate_precheck_key, is_terminal, run_gates
from .capwatch import DYNPOOL, R2POOL, Watch, blank_records
from .certify import certify
from .frontier import BACKENDS, backend, pack, perm_min, spec_dropped, unpack

R2, DYN, DEFS = 0, 1, 2


@dataclass(frozen=True)
class HybridConfig:
    budget: int = 1000                # work units
    penalty: int = 5                  # priority letters per generator above two
    dyn_ratio: float | None = 0.5     # higher-rank pops <= dyn_ratio * rank-two pops + 20
    dyn_max: int | None = None        # at most this many higher-rank pops
    dyn_cap: int | None = 8           # longest relator a higher-rank product or elimination may create; None = uncapped
    slack: int = 8                    # higher-rank total-length ceiling above the search root
    min_uses: int = 2                 # a defined digram must occur this often
    r2_cap: int | str | None = "parent"   # rank-two relator cap: "parent" (the parent's total length, the source's rule), an int, or None (uncapped)
    nielsen: bool = True              # Nielsen-map edges at rank two
    perms: bool = True                # signed-permutation canonical form at rank two
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


def _order(move):
    """The position of a rank-two move in the search order (``i -> j -> s -> k1 -> k2``, ``s = 1`` first)."""
    return (move.i, -move.s, move.k1, move.k2)


def search(run, cfg, budget):
    """The best-first hybrid search from ``run.state``; ``(solved, steps, stats)``."""
    expand, transform = backend(cfg.backend)
    ceiling = sum(map(len, run.state)) + cfg.slack
    root_key, prefix = pack(run.state), ()
    if cfg.perms:
        best, k = perm_min(root_key, transform)
        if k:
            root_key, prefix = best, (Aut(k),)
    heap = [(float(len(root_key) - 1), 0, 0, (root_key, None, (), R2))]
    dheap, seen_r2, seen_dyn = [], set(), set()
    st = dict(pops=0, dyn_pops=0, max_rank=2, dyn_rejected=0)
    ticks = [0]                                         # insertion order, the last tie-break

    def tick():
        ticks[0] += 1
        return ticks[0]

    push, pop = heapq.heappush, heapq.heappop
    result = []
    base = ceiling - cfg.slack                          # the root's total length
    watch = Watch({"cap": cfg.r2_cap, "dyn_cap": cfg.dyn_cap, "slack": cfg.slack},
                  (lambda key: perm_min(key, transform)[0]) if cfg.perms else (lambda key: key),
                  lambda words: D.make_key(words)[0], seen_r2, seen_dyn)
    units_left = lambda: budget - st["pops"]            # noqa: E731

    def can_dyn():
        dyn_pops = st["dyn_pops"]
        return (cfg.dyn_max is None or dyn_pops < cfg.dyn_max) and (
            cfg.dyn_ratio is None or dyn_pops <= cfg.dyn_ratio * (st["pops"] - dyn_pops) + 20)

    def drop_r2(ckey, total, needed, depth):
        """A rank-two child the cap rejected: pending in the rank-two pool, or counted now if it would have
        gone straight to the finishing gates."""
        if gate_precheck_key(ckey):
            watch.drop_now("cap", total, needed, st["pops"] + 1)
        else:
            watch.drop("cap", R2POOL, (float(total), depth, ticks[0] + 0.5), total, needed, ckey)

    def drop_dyn(reason, state, needed, depth):
        """A higher-rank move the dyn_cap (reason "cap") or the ceiling (reason "slack") rejected."""
        name, total, n = ("dyn_cap" if reason == "cap" else "slack"), length(state), len(state)
        if name == "slack":
            needed -= base
        if n == 2:                                      # an elimination back to rank two: offer() would run the gates
            ckey = pack(canonical_rels(D.make_key(state)[0]))
            if gate_precheck_key(ckey):
                watch.drop_now(name, total, needed, st["pops"] + 1)
            else:
                watch.drop(name, R2POOL, (float(total), depth, ticks[0] + 0.5), total, needed, ckey)
        else:
            watch.drop(name, DYNPOOL, (float(total + cfg.penalty * (n - 2)), depth, ticks[0] + 0.5), total, needed, state)

    def chain(node):
        out = []
        while node[1] is not None:
            out.append(node[2])
            node = node[1]
        return prefix + sum(reversed(out), ())

    def try_finish(node, state):
        if is_terminal(state):
            result.append(chain(node))
            raise _Done()
        if not gate_applicable(state):
            return
        gate = Run(state, budget - st["pops"])
        try:
            ok = run_gates(gate)
        except Budget:
            st["pops"] = budget
            raise _Done()
        st["pops"] += gate.units
        if ok:
            result.append(chain(node) + tuple(gate.steps))
            raise _Done()

    def offer(cnode, depth):
        if gate_precheck_key(cnode[0]):
            try_finish(cnode, unpack(cnode[0]))
        push(heap, (float(len(cnode[0]) - 1), depth, tick(), cnode))

    def offer_dyn(ckey, rl, parent, event, depth):
        cstep = ({"op": "dyn", "event": event, "relabel": rl, "after": ckey},)
        if len(ckey) == 2:
            offer((pack(canonical_rels(ckey)), parent, cstep, R2), depth)
            return
        st["max_rank"] = max(st["max_rank"], len(ckey))
        prio = float(length(ckey) + cfg.penalty * (len(ckey) - 2))
        push(dheap, (prio, depth, tick(), (ckey, parent, cstep, DYN)))

    try:
        while (heap or dheap) and st["pops"] < budget:
            ok = can_dyn()
            allowed = bool(dheap) and ok
            if allowed and (not heap or dheap[0][0] <= heap[0][0]):
                if watch.armed:
                    watch.step(None, dheap[0], ok, st["pops"] + 1)
                _, depth, _, node = pop(dheap)
            elif heap:
                if watch.armed:
                    watch.step(heap[0], None, ok, st["pops"] + 1)
                _, depth, _, node = pop(heap)
            else:
                break                                   # only deferred higher-rank states remain
            rep, parent, steps, kind = node
            if kind == R2 and cfg.perms and parent is not None:
                canon, k = perm_min(rep, transform)
                if k:
                    rep, node = canon, (canon, parent, steps + (Aut(k),), R2)
            if kind == DEFS:                            # the deferred define children (no charge)
                state = steps                           # a placeholder carries its parent's pair here
                for cw, event in _dedup_sorted(D.defines(D.normalize(state), cfg.min_uses)):
                    if length(cw) > ceiling:
                        st["dyn_rejected"] += 1
                        drop_dyn("slack", cw, length(cw), depth)
                    else:
                        offer_dyn(*D.make_key(cw), parent, event, depth)
                continue
            seen = seen_r2 if kind == R2 else seen_dyn
            if rep in seen:
                continue
            seen.add(rep)
            st["pops"] += 1
            depth += 1
            if kind == R2:
                state = unpack(rep)
                if is_terminal(state):
                    result.append(chain(node))
                    raise _Done()
                rcap = len(rep) - 1 if cfg.r2_cap == "parent" else cfg.r2_cap
                children, rejected = expand(rep, rcap)
                if rejected and watch.has("cap"):       # never under "parent": its children are shorter than the parent
                    lost = spec_dropped(rep, rcap)
                    assert len(lost) == rejected
                    for entry in sorted([(_order(mv), 0, child, mv) for child, mv in children]
                                        + [(_order(mv), 1, ckey, total, needed) for ckey, mv, total, needed in lost]):
                        if entry[1]:
                            drop_r2(entry[2], entry[3], entry[4], depth)
                        else:
                            offer((entry[2], node, (entry[3],), R2), depth)
                else:
                    for child, move in children:
                        offer((child, node, (move,), R2), depth)
                for k in NIELSEN if cfg.nielsen else ():
                    offer((transform(rep, k), node, (Aut(k),), R2), depth)
                lower = float(len(rep) - 1 - max(D.digram_counts(state).values(), default=0) + 3 + cfg.penalty)
                push(dheap, (lower, depth, tick(), (None, node, state, DEFS)))
            else:
                st["dyn_pops"] += 1
                lost = []
                edges, rejected = D.children(rep, cfg.dyn_cap, ceiling, cfg.min_uses, cfg.nielsen, lost)
                st["dyn_rejected"] += rejected
                for cw, event in _dedup_sorted(edges + [(state, (reason, needed)) for reason, state, needed in lost]):
                    if event.__class__ is tuple:
                        drop_dyn(event[0], cw, event[1], depth)
                    else:
                        offer_dyn(*D.make_key(cw), node, event, depth)
    except _Done:
        pass
    st["pops"] = min(st["pops"], budget)
    watch.end(not result and st["pops"] < budget, can_dyn(), units_left(), st["pops"])
    st.update(watch.records())
    return bool(result), (result[0] if result else ()), st


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
