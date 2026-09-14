"""Frozen mixed-search function with failed-best prefix capture only.

Source: parent checkout experiments/search/heuristic_1k.py.
The expansion, ordering, caps and visited policy are unchanged.
"""
import heapq
import numpy as np
from experiments.search.heuristic_1k import (
    pack, unpack, canon_pair, score_key, compile_config, BASELINE_CONFIG,
    expand_and_score_h, adjust_scores, NIELSEN, apply_pair, _arrs,
)

SOURCE_SHA256 = '4a5f3e29db87e4612c82fdd7bef7baeeef687c7d23be2d985d99b93743959c53'

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
    best_max = max(map(len, unpack(root)))
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
                prev = parent[cur]
                if prev is None:
                    break
                cur, step = prev
                steps.append(step)
            return dict(solved=True, nodes_explored=nodes, states=states[::-1],
                        steps=steps[::-1], basis_evaluations=basis_evaluations,
                        best_state=list(unpack(best)), min_total_length_seen=best_total,
                        min_max_relator_length_seen=best_max,
                        max_relator_length_seen=max_seen)
        a, b = _arrs(key)
        expansion_cap = cap if cap is not None else len(state[0]) + len(state[1])
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
            parent[child] = key, {'kind': 'substitution', 'move': '_'.join(str(int(x)) for x in moves[i])}
            child_state = unpack(child)
            child_total = sum(map(len, child_state))
            child_max = max(map(len, child_state))
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
                    parent[child] = key, {'kind': 'automorphism', 'images': transform}
                    child_total = sum(map(len, nxt))
                    child_max = max(map(len, nxt))
                    max_seen = max(max_seen, child_max)
                    if (child_total, child_max, child) < (best_total, best_max, best):
                        best, best_total, best_max = child, child_total, child_max
                    score = score_key(np.frombuffer(child, dtype=np.uint8), whitehead,
                                      w_weight, s_weight, mk_weight)
                    heapq.heappush(heap, (score, depth + 1, child))
    best_steps, best_states = [], []
    cur = best
    while cur is not None:
        best_states.append(list(unpack(cur)))
        prev = parent[cur]
        if prev is None:
            break
        cur, step = prev
        best_steps.append(step)
    return dict(solved=False, nodes_explored=nodes, states=[], steps=[],
                best_states=best_states[::-1], best_steps=best_steps[::-1],
                basis_evaluations=basis_evaluations, best_state=list(unpack(best)),
                min_total_length_seen=best_total,
                min_max_relator_length_seen=best_max,
                max_relator_length_seen=max_seen)
