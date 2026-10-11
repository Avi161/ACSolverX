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
     child, reduce the changed relator, and REJECT it (counting
     ``cap_rejected``) if any relator is longer than ``cfg.cap``; otherwise
     canonicalise; skip it if already discovered; else record its parent and
     move, update min/max discovered totals, and push it at depth + 1.
     Untouched relators are reduced and canonicalised too (a no-op when
     ``cyclic``; with ``cyclic=False`` main's canonical words can be
     non-reduced rotations, and main reduces both relators of every child).

The cap is a generation-time filter on reduced lengths, applied before
canonicalisation and dedup, so a rejected child is never seen and the count
does not depend on discovery order. ``cap=None`` disables it.
"""
from heapq import heappop, heappush

from ..core.moves import enumerate_moves, source_word
from ..core.priority import get as get_priority
from ..core.words import Presentation, canonical_word, fmt, reduce, rotate, sort_rels, state_key
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
    pops = cap_rejected = 0
    trace = [] if cfg.trace else None
    solved = None

    while heap and pops < cfg.budget:
        _, depth, key = heappop(heap)
        pops += 1
        rels = states[key]
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
                cap_rejected += 1
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

    path = end = None
    if solved is not None:
        end = Presentation(n, states[solved])
        if cfg.capture_path:
            path, k = [], solved
            while parent[k] is not None:
                k, mv = parent[k]
                path.append(mv)
            path = tuple(reversed(path))
    stats = {"discovered": len(parent), "cap_rejected": cap_rejected, "min_total": min_total,
             "max_total": max_total, "max_total_expanded": max_exp_total,
             "max_expanded": _strs(max_exp)}
    return Result(solved is not None, pops, path, start, end, stats,
                  tuple(trace) if trace is not None else None)
