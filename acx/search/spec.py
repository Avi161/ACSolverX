"""The reference backend, pure Python: ``acx.search.fast`` must reproduce its ``Result`` exactly (no numba).

The search, in words::

    push the start with key (priority, depth 0, state key)
    repeat until the budget is spent:
        pop the least key; that is one pop
        stop, solved, if every relator has length 1
        for each move of the popped state, in enumeration order:
            build the child
            if a relator is over the cap: hand it to the cap counter, do not push it
            else if it was discovered before: skip it
            else: remember its parent and move, and push it at depth + 1

A child replaces ``r_i`` by ``rot(r_i, k1) * rot(r_j ** s, k2)`` (the move), reduces it, and puts every relator in
canonical form with the relators sorted. Untouched relators are reduced and canonicalised too (a no-op when
``cyclic``).

The cap is a filter on reduced lengths applied when a child is generated, before dedup. A dropped child is handed to
a ``CapCount`` under the key it would have had, and each pop hands it the popped key before expanding (see
``acx.core.capcount`` for the stats).
"""
from heapq import heappop, heappush

from ..core.capcount import CapCount
from ..core.moves import enumerate_moves, source_word
from ..core.priority import get as get_priority, length
from ..core.words import Presentation, canonical_word, fmt, reduce, rotate, sort_rels, state_bytes, state_key
from .engine import Result


def _strs(rels):
    return tuple(map(fmt, rels))


def _is_trivial(rels):
    return all(len(r) == 1 for r in rels)


def _children(rels, cfg):
    """Every move of the state as ``(move, child, over_cap)``, in enumeration order."""
    cap, cyclic = cfg.cap, cfg.cyclic
    untouched = tuple(canonical_word(reduce(r, cyclic)) for r in rels)
    lengths = [len(r) for r in untouched]
    for move in enumerate_moves(rels):
        i = move.i
        new = reduce(rotate(rels[i], move.k1) + rotate(source_word(rels, move), move.k2), cyclic)
        child = sort_rels(untouched[:i] + (canonical_word(new),) + untouched[i + 1:])
        over_cap = cap is not None and (len(new) > cap or any(n > cap for k, n in enumerate(lengths) if k != i))
        yield move, child, over_cap


def _path_to(key, parent):
    """The moves from the start to ``key``, following ``parent`` links back."""
    moves = []
    while parent[key] is not None:
        key, move = parent[key]
        moves.append(move)
    return tuple(reversed(moves))


def run(start, cfg):
    """Best-first search from ``start`` (a normal form) under ``cfg``; returns a ``Result``."""
    priority = get_priority(cfg.priority)
    n_gen = start.n_gen
    root_key = state_key(start.rels, n_gen)
    states = {root_key: start.rels}     # key -> relators
    parent = {root_key: None}           # key -> (parent key, move); also the set of discovered keys
    heap = [(priority(start.rels), 0, root_key)]
    # A dropped child equal to the start is no new state.
    cap_count = CapCount(cfg.cap, known=(state_bytes(start.rels, n_gen),))

    min_total = max_total = max_expanded_total = length(start.rels)
    max_expanded = start.rels
    pops = 0
    trace = [] if cfg.trace else None
    solved_key = solved_depth = None

    while heap and pops < cfg.budget:
        prio, depth, key = heappop(heap)
        pops += 1
        rels = states[key]
        cap_count.pop((prio, depth, state_bytes(rels, n_gen)))    # the bar: before this pop's own drops
        if length(rels) > max_expanded_total:                     # strict: the first such pop wins
            max_expanded_total, max_expanded = length(rels), rels
        if trace is not None:
            trace.append(_strs(rels))
        if _is_trivial(rels):
            solved_key, solved_depth = key, depth
            break

        for move, child, over_cap in _children(rels, cfg):
            if over_cap:
                child_bytes = state_bytes(child, n_gen)
                cap_count.drop((priority(child), depth + 1, child_bytes), length(child), max(map(len, child)),
                               ident=child_bytes)
                continue
            child_key = state_key(child, n_gen)
            if child_key in parent:
                continue
            parent[child_key] = (key, move)
            states[child_key] = child
            min_total = min(min_total, length(child))
            max_total = max(max_total, length(child))
            heappush(heap, (priority(child), depth + 1, child_key))

    queue_ran_dry = solved_key is None and not heap and pops < cfg.budget
    cap_count.end(queue_ran_dry, cfg.budget - pops)

    path = end = None
    if solved_key is not None:
        end = Presentation(n_gen, states[solved_key])
        if cfg.capture_path:
            path = _path_to(solved_key, parent)
    stats = {"discovered": len(parent), **cap_count.record(), "min_total": min_total, "max_total": max_total,
             "max_total_expanded": max_expanded_total, "max_expanded": _strs(max_expanded)}
    return Result(solved_key is not None, pops, path, start, end, stats,
                  tuple(trace) if trace is not None else None, solved_depth)
