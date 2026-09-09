"""Behavior-preserving plain-search copy with deferred path formatting."""
import heapq

import numpy as np

from experiments.equivalence_classes.lib.words import apply_pair, canon_pair
from experiments.heuristic_search.core.hexpand import expand_and_score_h
from experiments.heuristic_search.core.hfast import _arrs, compile_config
from experiments.search.heuristic_1k import NIELSEN, adjust_scores, pack, score_key, unpack
from experiments.search.heuristics import BASELINE_CONFIG


def _substitution_step(move):
    return {'kind': 'substitution', 'move': '_'.join(map(str, move))}


def mixed_search(pair, arm, budget=1000, cap=48, w_weight=None,
                 s_weight=20.0, mk_weight=2.0):
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
    while heap and nodes < budget:
        _, depth, key = heapq.heappop(heap)
        nodes += 1
        state = unpack(key)
        if len(state[0]) == len(state[1]) == 1 and state[0].lower() != state[1].lower():
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
            return dict(solved=True, nodes_explored=nodes, states=states[::-1],
                        steps=steps[::-1], basis_evaluations=basis_evaluations,
                        best_state=list(unpack(best)), min_total_length_seen=best_total,
                        min_max_relator_length_seen=best_max,
                        max_relator_length_seen=max_seen)
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
                    score = score_key(np.frombuffer(child, dtype=np.uint8), whitehead,
                                      w_weight, s_weight, mk_weight)
                    heapq.heappush(heap, (score, depth + 1, child))
    return dict(solved=False, nodes_explored=nodes, states=[], steps=[],
                basis_evaluations=basis_evaluations, best_state=list(unpack(best)),
                min_total_length_seen=best_total,
                min_max_relator_length_seen=best_max,
                max_relator_length_seen=max_seen)
