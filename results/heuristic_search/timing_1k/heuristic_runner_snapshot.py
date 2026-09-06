"""Small exploratory arms; no changes to the production ordering or engine."""
from __future__ import annotations

import argparse
import heapq
import json
import os
from pathlib import Path
import time

import numpy as np
from numba import njit

from experiments.equivalence_classes.lib.autcanon import peak_reduce, check, is_automorphism
from experiments.equivalence_classes.lib.words import apply_pair, canon_pair, cyc_reduce
from experiments.heuristic_search.core.hcompact import greedy_search_hcompact
from experiments.heuristic_search.core.hexpand import expand_and_score_h
from experiments.heuristic_search.core.hfast import _arrs, _feats_nj, compile_config
from experiments.search.greedy_baseline import moves_to_states, str_to_move
from experiments.search.heuristics import BASELINE_CONFIG, S20_MK2, N_FEAT

ROOT = Path(__file__).resolve().parents[2]
NIELSEN = ({'x': 'xy', 'y': 'y'}, {'x': 'xY', 'y': 'y'},
           {'x': 'x', 'y': 'yx'}, {'x': 'x', 'y': 'yX'})
CODE = {'X': 1, 'Y': 2, 'x': 3, 'y': 4}
CHARS = '\0XYxy'
ARMS = ('greedy', 's20', 'whitehead2', 'aut_start', 'aut_edges', 'minK2')


def pack(pair):
    return bytes(CODE[c] for c in pair[0]) + b'\0' + bytes(CODE[c] for c in pair[1])


def unpack(key):
    a, b = key.split(b'\0')
    return ''.join(CHARS[c] for c in a), ''.join(CHARS[c] for c in b)


@njit(cache=True)
def response(codes):
    nx, ny = 0, 0
    edges = np.zeros((5, 5), dtype=np.int64)
    start = 0
    for end in range(len(codes) + 1):
        if end == len(codes) or codes[end] == 0:
            for j in range(start, end):
                a = codes[j]
                b = codes[start if j + 1 == end else j + 1]
                edges[a, b] += 1
                if a == 1 or a == 3:
                    nx += 1
                else:
                    ny += 1
            start = end + 1
    return (nx - 2 * (edges[3, 2] + edges[4, 1]),
            nx - 2 * (edges[3, 4] + edges[2, 1]),
            ny - 2 * (edges[4, 1] + edges[3, 2]),
            ny - 2 * (edges[4, 3] + edges[1, 2]))


@njit(cache=True)
def adjust_scores(blob, offsets, lengths, scores):
    for i in range(len(scores)):
        o = offsets[i]
        scores[i] += 2.0 * min(response(blob[o:o + lengths[i]]))


@njit(cache=True)
def score_key(codes, whitehead):
    sep = 0
    for i in range(len(codes)):
        if codes[i] == 0:
            sep = i
            break
    word_codes = np.empty(len(codes) - 1, dtype=np.uint8)
    word_codes[:sep] = codes[:sep]
    word_codes[sep:] = codes[sep + 1:]
    f = np.empty(N_FEAT, dtype=np.float64)
    _feats_nj(word_codes, 0, sep, len(codes) - sep - 1,
              np.empty(len(codes), dtype=np.bool_),
              np.empty(len(codes), dtype=np.int64), f)
    score = f[0] + 2.0 * f[5] + 20.0 * f[7]
    if whitehead:
        score += 2.0 * min(response(codes))
    return score


def mixed_search(pair, arm, budget=1000, cap=48):
    root = pack(canon_pair(*pair))
    whitehead = arm == 'whitehead2'
    priority = float(len(root) - 1) if arm == 'greedy' else score_key(
        np.frombuffer(root, dtype=np.uint8), whitehead)
    heap = [(priority, 0, root)]
    parent = {root: None}
    upto, weights, _ = compile_config(BASELINE_CONFIG if arm == 'greedy' else S20_MK2)
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
                        steps=steps[::-1], basis_evaluations=basis_evaluations)
        a, b = _arrs(key)
        blob, offsets, lengths, segs, scores, _, _, moves, count = expand_and_score_h(
            a, b, cap, True, upto, weights, True, True)
        if whitehead:
            adjust_scores(blob, offsets[:count], lengths, scores)
        raw = blob.tobytes()
        for i in range(count):
            o = int(offsets[i])
            child = raw[o:o + int(lengths[i])]
            if child in parent:
                continue
            parent[child] = key, {'kind': 'substitution', 'move': '_'.join(str(int(x)) for x in moves[i])}
            heapq.heappush(heap, (float(scores[i]), depth + 1, child))
        if arm == 'aut_edges':
            for transform in NIELSEN:
                basis_evaluations += 1
                nxt = apply_pair(state, transform)
                if max(map(len, nxt)) > cap:
                    continue
                child = pack(nxt)
                if child not in parent:
                    parent[child] = key, {'kind': 'automorphism', 'images': transform}
                    score = score_key(np.frombuffer(child, dtype=np.uint8), False)
                    heapq.heappush(heap, (score, depth + 1, child))
    return dict(solved=False, nodes_explored=nodes, states=[], steps=[],
                basis_evaluations=basis_evaluations)


def run(pair, arm, budget=1000, cap=48):
    if not 1 <= budget <= 1000:
        raise ValueError('This exploratory runner requires a budget in 1..1000')
    if not 1 <= cap <= 128:
        raise ValueError('Certificate experiments require a cap in 1..128')
    if max(map(len, canon_pair(*pair))) > cap:
        raise ValueError('Reduced input exceeds the relator cap')
    if arm in ('greedy', 's20', 'whitehead2', 'aut_edges'):
        return mixed_search(pair, arm, budget, cap)
    start = pair
    witness = None
    preprocessing = 0.0
    config = S20_MK2
    if arm == 'aut_start':
        t = time.perf_counter()
        _, start, witness = peak_reduce(pair)
        start = canon_pair(*start)
        assert check(pair, start, witness) and is_automorphism(witness)
        preprocessing = time.perf_counter() - t
    elif arm == 'minK2':
        config = {'segments': [{'upto': None, 'w': {'L': 1.0, 'S': 20.0, 'MK': 2.0, 'mK': 2.0}}]}
    else:
        raise ValueError(arm)
    st = greedy_search_hcompact(*start, node_budget=budget, max_relator_length=cap,
                                config=config, track_path=True)
    return dict(solved=st['solved'], nodes_explored=st['nodes_explored'],
                states=st['path'], steps=[{'kind': 'substitution', 'move': m} for m in st['path_moves']],
                initial_images=witness, preprocessing_seconds=preprocessing,
                basis_evaluations=None if witness else 0)


def verify(pair, record):
    if not record['solved']:
        return False
    state = canon_pair(*pair)
    if record.get('initial_images'):
        images = record['initial_images']
        if not is_automorphism(images):
            raise AssertionError('invalid initial basis change')
        state = apply_pair(state, images)
    if list(state) != record['states'][0]:
        raise AssertionError('certificate does not start at the transformed input')
    for step, expected in zip(record['steps'], record['states'][1:], strict=True):
        if step['kind'] == 'automorphism':
            if step['images'] not in NIELSEN:
                raise AssertionError('unknown generator change')
            state = apply_pair(state, step['images'])
        else:
            state = tuple(moves_to_states(*state, [str_to_move(step['move'])])[-1])
        if list(state) != expected:
            raise AssertionError('certificate step differs')
    if not (len(state[0]) == len(state[1]) == 1 and state[0].lower() != state[1].lower()):
        raise AssertionError('certificate is not terminal')
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--arm', choices=ARMS, required=True)
    ap.add_argument('--ids', help='comma-separated presentation IDs; omitted means subset60')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--cap', type=int, default=48)
    ap.add_argument('--cooldown', type=float, default=0.5)
    args = ap.parse_args()
    try:
        os.nice(10)
    except OSError:
        pass
    rows = json.loads((ROOT / 'benchmark/subsets/benchmark_subset_60.json').read_text())['subset']
    if args.ids:
        wanted = set(map(int, args.ids.split(',')))
        rows = [r for r in rows if r['pres_id'] in wanted]
        if len(rows) != len(wanted):
            raise ValueError('unknown presentation ID')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    previous = [json.loads(line) for line in args.out.read_text().splitlines()] if args.out.exists() else []
    if any((r['arm'], r['cap'], r['budget']) != (args.arm, args.cap, 1000) for r in previous):
        raise ValueError('Output file contains another experiment configuration')
    done = {r['pres_id'] for r in previous}
    t = time.perf_counter()
    run(('xyX', 'yyx'), args.arm, 5, args.cap)
    print(f'warmup_seconds={time.perf_counter()-t:.3f}', flush=True)
    for row in rows:
        if row['pres_id'] in done:
            continue
        t = time.perf_counter()
        rec = run((row['r1'], row['r2']), args.arm, cap=args.cap)
        seconds = time.perf_counter() - t
        rec.update(pres_id=row['pres_id'], bin=row['bin'], r1=row['r1'], r2=row['r2'],
                   arm=args.arm, budget=1000, cap=args.cap, seconds=seconds)
        rec['certificate_verified'] = verify((row['r1'], row['r2']), rec) if rec['solved'] else None
        with args.out.open('a') as f:
            f.write(json.dumps(rec) + '\n')
        print(f"{args.arm} {row['pres_id']:3d} solved={rec['solved']} nodes={rec['nodes_explored']} seconds={seconds:.3f}", flush=True)
        time.sleep(max(args.cooldown, seconds))


if __name__ == '__main__':
    main()
