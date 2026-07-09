"""A general-n best-first search, written from the same description as the solver.

This exists so the contract tests have something to run at ``n_gen = 3`` today,
and so the future stable-AC solver has a reference to be compared against.

It reproduces the solver's ordering exactly at ``n_gen = 2``: the heap holds
``(total_length, depth, key)``, the key is the tuple of rendered relator strings,
and children are enumerated ``i -> j -> s -> k1 -> k2``. Because the key is
unique per state and the closed set admits each state once, that triple is a
*strict total order* -- pop order does not depend on push order, so
``nodes_explored`` is fully determined by the neighbour relation and the key
order.

That parity is a bonus check on the 2-generator solvers, not a contract. A
correct stable-AC solver is free to explore in a different order; tests must
never demand that it match this trace.
"""

import heapq

from .moves import enumerate_moves, apply_move
from .presentation import Presentation
from .words import reduce_word, word_to_str

_HB_CHECK_EVERY = 1024


def state_key(pres):
    return tuple(word_to_str(r) for r in pres.relators)


def _total(key):
    return sum(len(s) for s in key)


def search(pres, budget, cap=24, cyclic=True, progress=None):
    """Best-first search over canonical presentations.

    Returns a dict with the same shape as ``greedy_search``'s stats, plus the
    move list as :class:`~..spec.moves.Move` tuples.
    """
    start = pres.reduced(cyclic).canonical()
    init_key = state_key(start)
    init_total = _total(init_key)

    visited = {init_key: None}
    move_in = {init_key: None}
    states = {init_key: start}
    pq = [(init_total, 0, init_key)]

    min_key = max_key = max_expanded_key = init_key
    min_total = max_total = max_expanded_total = init_total

    nodes = 0
    solved_key = None
    while pq and nodes < budget:
        total, depth, key = heapq.heappop(pq)
        nodes += 1
        if progress is not None and nodes % _HB_CHECK_EVERY == 0:
            progress(nodes)
        if total > max_expanded_total:
            max_expanded_key, max_expanded_total = key, total

        cur = states[key]
        if cur.all_relators_are_single_letters():
            solved_key = key
            break

        for mv in enumerate_moves(cur):
            raw = apply_move(cur.relators, mv)
            red = tuple(reduce_word(r, cyclic) for r in raw)
            if any(len(r) > cap for r in red):
                continue
            child = Presentation(cur.n_gen, red).canonical()
            ckey = state_key(child)
            if ckey in visited:
                continue
            visited[ckey] = key
            move_in[ckey] = mv
            states[ckey] = child
            ctotal = _total(ckey)
            if ctotal < min_total:
                min_key, min_total = ckey, ctotal
            elif ctotal > max_total:
                max_key, max_total = ckey, ctotal
            heapq.heappush(pq, (ctotal, depth + 1, ckey))

    path_states, path_moves = [], []
    if solved_key is not None:
        k = solved_key
        while k is not None:
            path_states.append(states[k])
            if move_in[k] is not None:
                path_moves.append(move_in[k])
            k = visited[k]
        path_states.reverse()
        path_moves.reverse()

    return {
        "solved": solved_key is not None,
        "nodes_explored": nodes,
        "path_length": len(path_moves) if solved_key is not None else None,
        "min_relator_length": min_total,
        "min_relator": list(min_key),
        "max_relator_length": max_total,
        "max_relator": list(max_key),
        "max_relator_length_expanded": max_expanded_total,
        "max_relator_expanded": list(max_expanded_key),
        "path": [list(state_key(s)) for s in path_states],
        "path_moves": path_moves,
        "path_states": path_states,
    }


def replay(pres, moves, cyclic=True):
    """Apply a move list to a start presentation, canonicalising each step.

    The stored move is relative to the *canonical parent*, so decoding is replay,
    never a diff of the stored states.
    """
    cur = pres.reduced(cyclic).canonical()
    out = [cur]
    for mv in moves:
        raw = apply_move(cur.relators, mv)
        red = tuple(reduce_word(r, cyclic) for r in raw)
        cur = Presentation(cur.n_gen, red).canonical()
        out.append(cur)
    return out
