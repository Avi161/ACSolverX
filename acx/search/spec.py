"""The reference backend: pure-Python best-first substitution search (no numba).

A rewrite of main's length-only greedy (``origin/main:experiments/search/
greedy_baseline.py``, ``GreedyBaselineSolver``) on int-tuple words, generalised
to any number of relators and to the two priorities. On ``length`` it
reproduces main's solves, ``nodes_explored``, path lengths and min/max
statistics (pinned by ``tests/data/greedy_golden.json``, from
``origin/test/greedy-test-suite``).

One pop:
  1. pop the least ``(priority, depth, key)`` entry; count it;
  2. record max-total-expanded (strict ``>``, so the first such pop wins);
  3. stop as solved if every relator has length 1;
  4. for each seam-cancelling move in ``enumerate_moves`` order: build the
     child, reduce the changed relator, and DROP it if any relator is longer
     than ``cfg.cap``; otherwise canonicalise; skip it if already discovered;
     else record its parent and move, update min/max discovered totals, and
     push it at depth + 1. Untouched relators are reduced and canonicalised too
     (a no-op when ``cyclic``; with ``cyclic=False`` main's canonical words can
     be non-reduced rotations, and main reduces both relators of every child).

The cap is a generation-time filter on reduced lengths, applied before dedup,
so a dropped child is never pushed. It never decides silently: every dropped
child goes to a ``acx.core.capcount.CapCount`` with the key it would have been
pushed under, ``(priority, depth + 1, state_bytes)``, and each pop hands the
counter its key (the bar) BEFORE expanding. The stats carry the counter's
``FIELDS`` (``cap_dropped`` per move; ``cap_would_pop``, ``cap_first_bind``,
``cap_needed``: whether a larger cap would change this search, and from which
cap). ``cap=None`` disables the cap and the counter.
"""
from heapq import heappop, heappush

from ..core.capcount import CapCount, blank
from ..core.moves import enumerate_moves, source_word
from ..core.priority import get as get_priority
from ..core.words import Presentation, canonical_word, fmt, reduce, rotate, sort_rels, state_bytes, state_key
from .engine import Result


def _strs(rels):
    return tuple(map(fmt, rels))


def run(start, cfg):
    """Search from ``start`` (already reduced and canonical) under ``cfg``."""
    prio = get_priority(cfg.priority)
    cap, cyclic, n = cfg.cap, cfg.cyclic, start.n_gen
    root = start.rels
    rkey = state_key(root, n)
    parent = {rkey: None}          # key -> (parent key, move)
    states = {rkey: root}
    heap = [(prio(root), 0, rkey)]
    tot0 = sum(map(len, root))
    min_total = max_total = max_exp_total = tot0
    max_exp = root
    pops = 0
    trace = [] if cfg.trace else None
    solved = None
    # a dropped child equal to the start (only possible when the start is over the cap) is no new state
    cc = None if cap is None else CapCount(cap, known=(state_bytes(root, n),))

    while heap and pops < cfg.budget:
        p, depth, key = heappop(heap)
        pops += 1
        rels = states[key]
        if cc is not None:
            cc.pop((p, depth, state_bytes(rels, n)))          # the bar: before this pop's own drops
        tot = sum(map(len, rels))
        if tot > max_exp_total:
            max_exp_total, max_exp = tot, rels
        if trace is not None:
            trace.append(_strs(rels))
        if all(len(r) == 1 for r in rels):
            solved = key
            break
        # untouched relators: reduced (a no-op on canonical states when cyclic) and canonical
        can = tuple(canonical_word(reduce(r, cyclic)) for r in rels)
        lens = [len(r) for r in can]
        rest = sum(lens)
        for mv in enumerate_moves(rels):
            i = mv.i
            new = reduce(rotate(rels[i], mv.k1) + rotate(source_word(rels, mv), mv.k2), cyclic)
            if cap is not None and (len(new) > cap or any(L > cap for k, L in enumerate(lens) if k != i)):
                child = sort_rels(can[:i] + (canonical_word(new),) + can[i + 1:])
                b = state_bytes(child, n)
                cc.drop((prio(child), depth + 1, b), rest - lens[i] + len(new), max(map(len, child)), ident=b)
                continue
            child = sort_rels(can[:i] + (canonical_word(new),) + can[i + 1:])
            ckey = state_key(child, n)
            if ckey in parent:
                continue
            parent[ckey] = (key, mv)
            states[ckey] = child
            ct = rest - lens[i] + len(new)
            min_total = min(min_total, ct)
            max_total = max(max_total, ct)
            heappush(heap, (prio(child), depth + 1, ckey))

    if cc is not None:
        cc.end(solved is None and not heap and pops < cfg.budget, cfg.budget - pops)
    path = end = None
    if solved is not None:
        end = Presentation(n, states[solved])
        if cfg.capture_path:
            path, k = [], solved
            while parent[k] is not None:
                k, mv = parent[k]
                path.append(mv)
            path = tuple(reversed(path))
    caps = cc.record() if cc is not None else blank()
    stats = {"discovered": len(parent), **caps, "cap_rejected": caps["cap_dropped"], "min_total": min_total,
             "max_total": max_total, "max_total_expanded": max_exp_total,
             "max_expanded": _strs(max_exp)}
    return Result(solved is not None, pops, path, start, end, stats,
                  tuple(trace) if trace is not None else None)
