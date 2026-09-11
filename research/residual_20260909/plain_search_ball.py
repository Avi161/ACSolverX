"""``plain_search_fast`` plus a backward-ball terminal, and nothing else.

This is a copy of ``research/supermoves_20260908/plain_search_fast.py`` -- the
frozen module is left untouched so it stays the comparison implementation --
with one addition: a hash lookup of every newly created state in the exact
backward ball ``B(cap)`` built by ``backward_table.build``.

WHY THE BALL TERMINAL CAN ONLY HELP (the dominance argument)
===========================================================
Run this search and the frozen one side by side on the same row with the same
budget.  Nothing about the ordering changes: the heap, the priorities, the
expansion cap, the ``parent`` de-duplication and the ``nodes`` charging are the
frozen code verbatim, and a ball lookup neither charges a unit nor pushes,
pops, or reorders anything.  So the two runs are in lockstep until this one
reports a ball hit.

* If no lookup ever hits, the two runs are identical -- same solved flag, same
  ``nodes_explored``, same certificate.
* The trivial pair is ``canon_pair('x', 'y') == ('Y', 'X')``, and it is the
  only canonical state the frozen terminal test accepts.  It is in the table at
  depth 0.  The frozen code recognises it when it is POPPED; this code
  recognises it when it is GENERATED, which is strictly earlier in the same
  execution.  So every solve the frozen search finds, this one finds at a point
  no later, and ``nodes`` is nondecreasing along the execution, hence
  ``nodes_ball <= nodes_frozen``.
* Any other hit is an even earlier stop, and it is a genuine solve: every
  stored edge was forward-verified against this same kernel when the table was
  built, and re-checked by pure-Python replay, so the spliced tail is a real
  path of engine moves ending at ``('Y', 'X')``.

Hence: for every row the frozen search solves at N units, this one solves at
<= N units; and it may additionally solve rows the frozen search does not.

ACCOUNTING
==========
``nodes_explored`` keeps its frozen meaning exactly (pops, and, in the mid
search, the same macro charges).  Ball lookups are free: they are reported
separately as ``ball_lookups``, with ``ball_hit`` and ``ball_depth``.
"""
import heapq

import numpy as np

from experiments.equivalence_classes.lib.words import apply_pair, canon_pair
from experiments.heuristic_search.core.hexpand import expand_and_score_h
from experiments.heuristic_search.core.hfast import _arrs, compile_config
from experiments.search.heuristic_1k import NIELSEN, adjust_scores, pack, score_key, unpack
from experiments.search.heuristics import BASELINE_CONFIG
from research.residual_20260909.backward_table import tail as ball_tail

_UNSET = object()
_TABLE = None


def set_table(table):
    """Install the module-level backward ball used when no ``table=`` is passed."""
    global _TABLE
    _TABLE = table


def get_table():
    return _TABLE


def _resolve(table):
    return _TABLE if table is _UNSET else table


def _substitution_step(move):
    return {'kind': 'substitution', 'move': '_'.join(map(str, move))}


def mixed_search(pair, arm, budget=1000, cap=48, w_weight=None,
                 s_weight=20.0, mk_weight=2.0, table=_UNSET):
    table = _resolve(table)
    if w_weight is None:
        w_weight = 2.0 if arm == 'whitehead2' else 0.0
    root = pack(canon_pair(*pair))
    whitehead = w_weight != 0.0
    priority = float(len(root) - 1) if arm == 'greedy' else score_key(
        np.frombuffer(root, dtype=np.uint8), whitehead, w_weight, s_weight, mk_weight)
    heap = [(priority, 0, root)]
    parent = {root: None}
    best = root
    best_total = len(root) - 1
    separator = root.index(0)
    best_max = max(separator, len(root) - separator - 1)
    max_seen = best_max
    config = {'segments': [{'upto': None, 'w': {'L': 1.0, 'S': s_weight, 'MK': mk_weight}}]}
    upto, weights, _ = compile_config(BASELINE_CONFIG if arm == 'greedy' else config)
    nodes = 0
    basis_evaluations = 0
    ball_lookups = 0

    def finish(key, ball_depth=None):
        steps, states = [], []
        cur = key
        while cur is not None:
            states.append(list(unpack(cur)))
            previous = parent[cur]
            if previous is None:
                break
            cur, kind, payload = previous
            steps.append(_substitution_step(payload) if kind == 0 else
                         {'kind': 'automorphism', 'images': payload})
        states.reverse()
        steps.reverse()
        if ball_depth is not None:
            tail_states, tail_steps = ball_tail(table, key)
            states += tail_states[1:]
            steps += tail_steps
        return dict(solved=True, nodes_explored=nodes, states=states,
                    steps=steps, basis_evaluations=basis_evaluations,
                    best_state=list(unpack(best)), min_total_length_seen=best_total,
                    min_max_relator_length_seen=best_max,
                    max_relator_length_seen=max_seen,
                    ball_lookups=ball_lookups, ball_hit=ball_depth is not None,
                    ball_depth=ball_depth or 0)

    if table is not None:
        ball_lookups += 1
        if root in table:
            return finish(root, table[root][0])
    while heap and nodes < budget:
        _, depth, key = heapq.heappop(heap)
        nodes += 1
        state = unpack(key)
        if len(state[0]) == len(state[1]) == 1 and state[0].lower() != state[1].lower():
            return finish(key)
        a, b = _arrs(key)
        expansion_cap = cap if cap is not None else len(key) - 1
        blob, offsets, lengths, segs, scores, _, _, moves, count = expand_and_score_h(
            a, b, expansion_cap, True, upto, weights, True, True)
        if whitehead:
            adjust_scores(blob, offsets[:count], lengths, scores, w_weight)
        raw = blob.tobytes()
        for i in range(count):
            o = int(offsets[i])
            child = raw[o:o + int(lengths[i])]
            if child in parent:
                continue
            parent[child] = key, 0, tuple(int(value) for value in moves[i])
            child_total = len(child) - 1
            separator = child.index(0)
            child_max = max(separator, len(child) - separator - 1)
            max_seen = max(max_seen, child_max)
            if (child_total, child_max, child) < (best_total, best_max, best):
                best, best_total, best_max = child, child_total, child_max
            if table is not None:
                ball_lookups += 1
                if child in table:
                    return finish(child, table[child][0])
            heapq.heappush(heap, (float(scores[i]), depth + 1, child))
        if arm == 'aut_edges':
            for transform in NIELSEN:
                basis_evaluations += 1
                nxt = apply_pair(state, transform)
                if cap is not None and max(map(len, nxt)) > cap:
                    continue
                child = pack(nxt)
                if child not in parent:
                    parent[child] = key, 1, transform
                    child_total = len(child) - 1
                    separator = child.index(0)
                    child_max = max(separator, len(child) - separator - 1)
                    max_seen = max(max_seen, child_max)
                    if (child_total, child_max, child) < (best_total, best_max, best):
                        best, best_total, best_max = child, child_total, child_max
                    if table is not None:
                        ball_lookups += 1
                        if child in table:
                            return finish(child, table[child][0])
                    score = score_key(np.frombuffer(child, dtype=np.uint8), whitehead,
                                      w_weight, s_weight, mk_weight)
                    heapq.heappush(heap, (score, depth + 1, child))
    return dict(solved=False, nodes_explored=nodes, states=[], steps=[],
                basis_evaluations=basis_evaluations, best_state=list(unpack(best)),
                min_total_length_seen=best_total,
                min_max_relator_length_seen=best_max,
                max_relator_length_seen=max_seen,
                ball_lookups=ball_lookups, ball_hit=False, ball_depth=0)
