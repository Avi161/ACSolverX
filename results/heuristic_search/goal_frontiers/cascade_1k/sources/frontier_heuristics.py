"""Budgeted beam and basis-normalized searches for exploratory screening."""
from __future__ import annotations

import heapq
import math

import numpy as np

from experiments.equivalence_classes.lib.words import (
    SIGNED_PERMS, apply_pair, canon_pair, replay_move,
)
from experiments.heuristic_search.core.hfast import _arrs, compile_config
from experiments.heuristic_search.core.hexpand import expand_and_score_h
from experiments.search.basis_moves import apply_nielsen_key, reduce_basis_key
from experiments.search.heuristic_1k import NIELSEN, adjust_scores, pack, score_key, unpack


def search(pair, *, budget=1000, cap=48, s=20.0, mk=2.0, w=0.0,
           generators=False, normalization='none', beam=0, deep_ties=False):
    if not 1 <= budget <= 10000 or not 1 <= cap <= 128:
        raise ValueError('Budget must be1..10000 and cap1..128')
    if normalization not in ('none', 'root', 'pop', 'children'):
        raise ValueError('unknown normalization mode')
    if beam < 0 or any(not math.isfinite(x) or x < 0 for x in (s, mk, w)):
        raise ValueError('Invalid width or weights')
    s, mk, w = float(s), float(mk), float(w)
    root = pack(canon_pair(*pair))
    if max(map(len, unpack(root))) > cap:
        raise ValueError('Reduced input exceeds cap')
    parent = {root: None}
    closed = set()
    count = dict(nodes_explored=0, expanded_states=0, generator_evaluations=0,
                 normalization_calls=0, normalization_steps=0, generated_children=0,
                 normalization_response_values=0, normalization_image_applications=0,
                 duplicate_children=0, max_frontier=1, maximum_depth=0)
    best_length = len(root) - 1
    snapshots = []
    cfg = {'segments': [{'upto': None, 'w': {'L': 1.0, 'S': s, 'MK': mk}}]}
    upto, weights, _ = compile_config(cfg)

    def score(key):
        return float(score_key(np.frombuffer(key, dtype=np.uint8), w != 0, w, s, mk))

    def normalize(key):
        count['normalization_calls'] += 1
        out, trace = reduce_basis_key(key)
        count['normalization_steps'] += len(trace)
        descents = sum(step['images'] in NIELSEN for step in trace)
        count['normalization_response_values'] += 4 * (descents + 1)
        count['normalization_image_applications'] += descents + 8
        chain = [(pack(step['state']), {k: v for k, v in step.items() if k != 'state'})
                 for step in trace]
        if any(max(map(len, step['state'])) > cap for step in trace):
            return key, []
        return out, chain

    start = root
    if normalization != 'none':
        start, chain = normalize(root)
        if start != root:
            parent[start] = root, chain
    depth = {start: 0}
    frontier = [(score(start), 0, start)]
    next_layer = {}

    def finish(key=None):
        states, steps = [], []
        if key is not None:
            segments = []
            while parent[key] is not None:
                key, chain = parent[key]
                segments.append(chain)
            states = [list(unpack(key))]
            for chain in reversed(segments):
                for child, step in chain:
                    states.append(list(unpack(child)))
                    steps.append(step)
        return dict(count, solved=key is not None, states=states, steps=steps,
                    minimum_popped_length=best_length, snapshots=snapshots)

    def offer(child, src, chain, priority=None):
        count['generated_children'] += 1
        if child in closed or child in parent:
            count['duplicate_children'] += 1
            return
        if normalization == 'children':
            normalized, tail = normalize(child)
            if normalized in closed or normalized in parent:
                count['duplicate_children'] += 1
                return
            child, chain, priority = normalized, chain + tail, None
        if max(map(len, unpack(child))) > cap:
            return
        parent[child] = src, chain
        d = depth[src] + 1
        depth[child] = d
        entry = (score(child) if priority is None else priority, -d if deep_ties else d, child)
        if beam:
            next_layer[child] = entry
        else:
            heapq.heappush(frontier, entry)

    while frontier and count['nodes_explored'] < budget:
        _, _, key = heapq.heappop(frontier)
        count['nodes_explored'] += 1
        closed.add(key)
        d = depth[key]
        count['maximum_depth'] = max(d, count['maximum_depth'])
        best_length = min(best_length, len(key) - 1)
        state = unpack(key)
        if len(state[0]) == len(state[1]) == 1 and state[0].lower() != state[1].lower():
            return finish(key)
        redirected = False
        if normalization == 'pop':
            normalized, chain = normalize(key)
            if normalized != key:
                offer(normalized, key, chain)
                redirected = True
        if not redirected:
            count['expanded_states'] += 1
            a, b = _arrs(key)
            blob, offsets, lengths, _, scores, _, _, moves, n = expand_and_score_h(
                a, b, cap, True, upto, weights, True, True)
            if w:
                adjust_scores(blob, offsets[:n], lengths, scores, w)
            raw = blob.tobytes()
            for i in range(n):
                off = int(offsets[i])
                child = raw[off:off + int(lengths[i])]
                if child in parent or child in closed:
                    count['generated_children'] += 1
                    count['duplicate_children'] += 1
                    continue
                step = {'kind': 'substitution', 'move': '_'.join(str(int(x)) for x in moves[i])}
                offer(child, key, [(child, step)], float(scores[i]))
            if generators:
                for i, images in enumerate(NIELSEN):
                    count['generator_evaluations'] += 1
                    child = apply_nielsen_key(key, i)
                    offer(child, key, [(child, {'kind': 'automorphism', 'images': images})])
        if beam and not frontier:
            entries = heapq.nsmallest(beam, next_layer.values())
            kept = {entry[2] for entry in entries}
            for dropped in next_layer.keys() - kept:
                # A discarded beam node has never expanded, so no retained path uses it.
                del parent[dropped]
                del depth[dropped]
            frontier = entries
            heapq.heapify(frontier)
            next_layer.clear()
        count['max_frontier'] = max(count['max_frontier'], len(frontier) + len(next_layer))
        if count['nodes_explored'] in (100, 400, 1000, 3000, 10000):
            snapshots.append(dict(pops=count['nodes_explored'], depth=d, total_length=len(key)-1,
                                  minimum_length=best_length, frontier=len(frontier)))
    return finish()


def verify(pair, result):
    if not result['solved']:
        return False
    state = canon_pair(*pair)
    assert list(state) == result['states'][0]
    allowed = list(NIELSEN) + [images for _, images in SIGNED_PERMS]
    for step, expected in zip(result['steps'], result['states'][1:], strict=True):
        if step['kind'] == 'automorphism':
            assert step['images'] in allowed
            state = apply_pair(state, step['images'])
        else:
            state = replay_move(state, tuple(map(int, step['move'].split('_'))))
        assert list(state) == expected
    assert len(state[0]) == len(state[1]) == 1 and state[0].lower() != state[1].lower()
    return True
