"""The reference backend, pure Python: ``acx.search.fast`` must reproduce its ``Result`` exactly (no numba)."""
from heapq import heappop, heappush

from ..core.capcount import CapCount
from ..core.moves import enumerate_moves, source_word
from ..core.priority import get as get_priority
from ..core.words import Presentation, canonical_word, fmt, reduce, rotate, sort_rels, state_bytes, state_key
from .engine import Result


def _strs(rels):
    return tuple(map(fmt, rels))


def run(start, cfg):
    """Best-first search from ``start`` (a normal form) under ``cfg``; returns a ``Result``.

    Per pop: take the least ``(priority, depth, state_key)`` entry; stop as solved if every relator has length 1;
    otherwise for each seam-cancelling move (``enumerate_moves`` order) build the child, reduce the changed
    relator, canonicalise it and sort the relators; skip it if already discovered, else record its parent and
    move and push it at depth + 1. Untouched relators are reduced and canonicalised too (a no-op when ``cyclic``).

    The cap is a filter on reduced lengths applied when a child is generated, before dedup: a child with a
    relator over ``cfg.cap`` is never pushed but is handed to a ``CapCount`` under the key it would have had,
    and each pop hands it the popped key before expanding (see ``acx.core.capcount`` for the stats).
    """
    prio = get_priority(cfg.priority)
    cap, cyclic, n = cfg.cap, cfg.cyclic, start.n_gen
    root = start.rels
    rkey = state_key(root, n)
    parent = {rkey: None}          # key -> (parent key, move)
    states = {rkey: root}
    heap = [(prio(root), 0, rkey)]
    min_total = max_total = max_exp_total = sum(map(len, root))
    max_exp = root
    pops = 0
    trace = [] if cfg.trace else None
    solved = None
    cc = CapCount(cap, known=(state_bytes(root, n),))     # a dropped child equal to the start is no new state

    while heap and pops < cfg.budget:
        p, depth, key = heappop(heap)
        pops += 1
        rels = states[key]
        cc.pop((p, depth, state_bytes(rels, n)))          # the bar: before this pop's own drops
        tot = sum(map(len, rels))
        if tot > max_exp_total:
            max_exp_total, max_exp = tot, rels
        if trace is not None:
            trace.append(_strs(rels))
        if all(len(r) == 1 for r in rels):
            solved = key
            break
        can = tuple(canonical_word(reduce(r, cyclic)) for r in rels)
        lens = [len(r) for r in can]
        rest = sum(lens)
        for mv in enumerate_moves(rels):
            i = mv.i
            new = reduce(rotate(rels[i], mv.k1) + rotate(source_word(rels, mv), mv.k2), cyclic)
            child = sort_rels(can[:i] + (canonical_word(new),) + can[i + 1:])
            ct = rest - lens[i] + len(new)
            if cap is not None and (len(new) > cap or any(L > cap for k, L in enumerate(lens) if k != i)):
                b = state_bytes(child, n)
                cc.drop((prio(child), depth + 1, b), ct, max(map(len, child)), ident=b)
                continue
            ckey = state_key(child, n)
            if ckey in parent:
                continue
            parent[ckey] = (key, mv)
            states[ckey] = child
            min_total = min(min_total, ct)
            max_total = max(max_total, ct)
            heappush(heap, (prio(child), depth + 1, ckey))

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
    stats = {"discovered": len(parent), **cc.record(), "min_total": min_total, "max_total": max_total,
             "max_total_expanded": max_exp_total, "max_expanded": _strs(max_exp)}
    return Result(solved is not None, pops, path, start, end, stats, tuple(trace) if trace is not None else None)
