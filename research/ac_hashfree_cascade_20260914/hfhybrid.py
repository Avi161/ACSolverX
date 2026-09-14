"""Hybrid hash-free search: the rank-two fast engine plus dynamic-rank moves, one frontier.

Rank-two states are packed keys expanded by the compiled kernel exactly as in
`hfcascade.stage_fast` (seam-cancelling products, four Nielsen maps, canonical under the
eight signed permutations, finishing gates at pop).  In addition every popped rank-two
state offers `define` children (a new generator for a repeated cyclic digram) and every
higher-rank state is expanded with the dynamic-rank moves of
research/ac_dynamic_rank_20260913 (capped products, define, eliminate) plus Nielsen
transvections.  A higher-rank child that returns to rank two re-enters the fast path.
The frontier is one heap ordered by total length plus `penalty` per generator above
two; the closed sets are block-sorted arrays (comparison only).  One unit per popped
state, whatever its rank.

Certificate steps: rank-two steps as in hfcascade ('substitution', 'automorphism');
dynamic steps as {'kind': 'dyn', 'event', 'relabel', 'after'} in the int-word format of
dynrank.  `verify_hybrid` replays both kinds with the two independent verifiers.
Certificate scope: a certificate without 'dyn' steps is an ordinary rank-two AC
certificate (with automorphism transport); one with 'dyn' steps proves stable
AC-triviality of a trivial-group presentation (define/eliminate are Lemma-11
composites, unexpanded).
"""
from __future__ import annotations

import heapq
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.ac_dynamic_rank_20260913 import dynrank as D  # noqa: E402
from research.ac_dynamic_rank_20260913 import verify as DV  # noqa: E402
from research.ac_hashfree_cascade_20260914 import hfcascade as H  # noqa: E402
from research.ac_hashfree_cascade_20260914 import verify as SV  # noqa: E402
from research.ac_hashfree_cascade_20260914.hfunified import nielsen_children  # noqa: E402

_LETTER = {'x': 1, 'y': 2}


def pair_to_words(pair):
    return D.normalize(tuple(D.parse(w) for w in pair))


def words_to_pair(words):
    if len(words) != 2:
        raise ValueError('not rank two')
    return H.canon_pair(D.render(words[0]), D.render(words[1]))


def _dedup_sorted(items):
    """Deduplicate (state, event) pairs by sorting on the state (no hashing)."""
    items = sorted(items, key=lambda t: t[0])
    out = []
    prev = None
    for state, event in items:
        if state == prev:
            continue
        prev = state
        out.append((state, event))
    return out


def search(run, *, budget, penalty=2, cap=8, slack=8, relabel=True, nielsen=True, perms=True,
           allow_define=True, allow_eliminate=True, min_uses=2, gates=True):
    """Best-first hybrid search from run.state; returns (solved, steps, info)."""
    F = H._fast_setup()
    np, expand, arrs, transform, pack, unpack = (F['np'], F['expand'], F['arrs'], F['transform'],
                                                  F['pack'], F['unpack'])
    upto, weights, _ = F['cfgs']['length']
    root_pair = run.state
    ceiling = H.total_length(root_pair) + slack
    root_key = pack(root_pair)
    prefix = []
    if perms:
        best, img = H._perm_key(root_key, transform, np)
        if best != root_key:
            prefix.append({'kind': 'automorphism', 'images': H._IMAGES_FAST[img]})
            root_pair = H.canon_pair(H.apply_hom(root_pair[0], H._IMAGES_FAST[img]),
                                     H.apply_hom(root_pair[1], H._IMAGES_FAST[img]))
            root_key = pack(root_pair)
    # node = (repr, parent, step, kind)
    root = (root_key, None, None, 'r2')
    heap = [(float(len(root_key) - 1), 0, 0, root)]
    counter = 0
    seen_r2 = H.SortedBlocks(b'')
    seen_dyn = H.SortedBlocks(((),))
    pops = 0
    max_rank = 2
    dyn_pops = 0
    push = heapq.heappush

    def chain_steps(node):
        out = []                       # built backwards; each node's steps reversed too
        while node[1] is not None:
            repr_, parent, step, kind = node
            mine = []
            if kind == 'r2':
                if isinstance(step, tuple) and len(step) == 3 and step[0] == 'dyn':
                    _, ev, perm = step
                    mine.append(ev)
                    if perm is not None:
                        mine.append({'kind': 'automorphism', 'images': perm})
                else:
                    perm = None
                    if isinstance(step, tuple) and len(step) == 2 and isinstance(step[1], (dict, type(None))):
                        step, perm = step
                    if isinstance(step, dict):
                        mine.append({'kind': 'automorphism', 'images': dict(step)})
                    else:
                        mine.append({'kind': 'substitution', 'move': '_'.join(map(str, step))})
                    if perm is not None:
                        mine.append({'kind': 'automorphism', 'images': perm})
            else:
                mine.append(step)
            out.extend(reversed(mine))
            node = parent
        out.reverse()
        return prefix + out

    while heap and pops < budget:
        _, depth, _, node = heapq.heappop(heap)
        repr_, parent, step, kind = node
        if kind == 'r2':
            if not seen_r2.add(repr_):
                continue
        else:
            if not seen_dyn.add(repr_):
                continue
        pops += 1
        depth += 1
        if kind == 'r2':
            key = repr_
            state = unpack(key)
            if H.is_terminal(state):
                return True, chain_steps(node), dict(pops=pops, max_rank=max_rank, dyn_pops=dyn_pops)
            if gates and parent is not None and H.gate_applicable(state):
                gate_run = H.Run(state, budget - pops)
                try:
                    if H.run_gates(gate_run):
                        pops += gate_run.units
                        return True, chain_steps(node) + gate_run.steps, dict(pops=pops, max_rank=max_rank, dyn_pops=dyn_pops)
                    pops += gate_run.units
                except H.Budget:
                    pops = budget
                    break
            a, b = arrs(key)
            blob, offs, lens, _, scores, _, _, moves, count = expand(a, b, len(key) - 1, True, upto, weights, True, True)
            raw = blob.tobytes()
            offs = offs.tolist()
            lens = lens.tolist()
            scores = scores.tolist()
            moves = moves.tolist()
            for i in range(count):
                o = offs[i]
                child = raw[o:o + lens[i]]
                cstep = tuple(moves[i])
                if perms:
                    child, img = H._perm_key(child, transform, np)
                    cstep = (cstep, None if img == 4 else H._IMAGES_FAST[img])
                counter += 1
                push(heap, (scores[i], depth, counter, (child, node, cstep, 'r2')))
            if nielsen:
                codes = np.frombuffer(key, dtype=np.uint8)
                for t in range(4):
                    child = transform(codes, t).tobytes()
                    cstep = H.NIELSEN[t]
                    if perms:
                        child, img = H._perm_key(child, transform, np)
                        cstep = (cstep, None if img == 4 else H._IMAGES_FAST[img])
                    counter += 1
                    push(heap, (float(len(child) - 1), depth, counter, (child, node, cstep, 'r2')))
            if allow_define:
                words = pair_to_words(state)
                for cw, event in _dedup_sorted(D.defines(words, min_uses)):
                    if D.total_length(cw) > ceiling:
                        continue
                    ckey, rl = D.make_key(cw, relabel)
                    cstep = {'kind': 'dyn', 'event': event, 'relabel': rl, 'after': ckey}
                    counter += 1
                    max_rank = max(max_rank, len(ckey))
                    push(heap, (float(D.total_length(ckey) + penalty * (len(ckey) - 2)), depth, counter,
                                (ckey, node, cstep, 'dyn')))
        else:
            words = repr_
            dyn_pops += 1
            edges = D.children(words, cap=cap, ceiling=ceiling, allow_define=allow_define,
                               allow_eliminate=allow_eliminate, min_uses=min_uses)
            if nielsen:
                edges = edges + [(c, e) for c, e in nielsen_children(words) if D.total_length(c) <= ceiling]
            for cw, event in _dedup_sorted(edges):
                ckey, rl = D.make_key(cw, relabel)
                cstep = {'kind': 'dyn', 'event': event, 'relabel': rl, 'after': ckey}
                counter += 1
                if len(ckey) == 2:
                    pair = words_to_pair(ckey)
                    k2 = pack(pair)
                    perm = None
                    if perms:
                        k2, img = H._perm_key(k2, transform, np)
                        perm = None if img == 4 else H._IMAGES_FAST[img]
                    push(heap, (float(len(k2) - 1), depth, counter, (k2, node, ('dyn', cstep, perm), 'r2')))
                elif len(ckey) < 2:
                    raise AssertionError('rank fell below two')
                else:
                    max_rank = max(max_rank, len(ckey))
                    push(heap, (float(D.total_length(ckey) + penalty * (len(ckey) - 2)), depth, counter,
                                (ckey, node, cstep, 'dyn')))
    return False, [], dict(pops=min(pops, budget), max_rank=max_rank, dyn_pops=dyn_pops)


def solve(pair, budget=1000, **kw):
    """Stages A-C of hfcascade, then the hybrid search with the remaining budget."""
    run = H.Run(pair, budget)
    try:
        if H.is_terminal(run.state):
            return dict(solved=True, stage='terminal', units=1, steps=[], explicit_rank2=True)
        H.stage_pair_descent(run)
        for index in range(2):
            if H.stage_primitive(run, index):
                return dict(solved=True, stage='B', units=run.units, steps=run.steps, explicit_rank2=True)
        if H.try_pinch_gates(run):
            return dict(solved=True, stage='C', units=run.units, steps=run.steps, explicit_rank2=True)
    except H.Budget:
        return dict(solved=False, stage=None, units=budget, steps=[], explicit_rank2=None)
    solved, steps, info = search(run, budget=budget - run.units, **kw)
    units = run.units + info['pops']
    all_steps = run.steps + steps
    return dict(solved=solved, stage='H' if solved else None, units=min(units, budget), steps=all_steps if solved else [],
                explicit_rank2=(not any(s['kind'] == 'dyn' for s in all_steps)) if solved else None,
                max_rank=info['max_rank'], dyn_pops=info['dyn_pops'],
                path_length=len(all_steps) if solved else None)


def verify_hybrid(pair, steps, min_uses=2):
    """Replay a hybrid certificate with the two independent verifiers; returns the final
    string pair.  Raises SV.Failure / DV.Failure on any discrepancy."""
    cur = SV.canon_pair(*pair)          # string world
    words = None                        # int world (when not None it is authoritative)
    for i, step in enumerate(steps):
        if step['kind'] == 'dyn':
            if words is None:
                words = DV.norm(tuple(D.parse(w) for w in cur))
            ev = step['event']
            kind = ev['kind']
            if kind == 'product':
                child = DV.replay_product(words, ev)
            elif kind == 'define':
                child = DV.replay_define(words, ev, min_uses)
            elif kind == 'eliminate':
                child = DV.replay_eliminate(words, ev)
            elif kind == 'nielsen':
                child = DV.replay_nielsen(words, ev)
            else:
                raise DV.Failure('unknown dyn event')
            child = DV.apply_relabel(child, step.get('relabel'))
            if child != DV.norm(tuple(tuple(w) for w in step['after'])):
                raise DV.Failure('hybrid step %d: replayed state differs from stored state' % i)
            words = child
            if len(words) == 2:
                cur = SV.canon_pair(D.render(words[0]), D.render(words[1]))
                words = None
        else:
            if words is not None:
                raise SV.Failure('string step at rank %d' % len(words))
            cur = SV.replay(cur, [step], None)  if False else _replay_one(cur, step, i)
    if words is not None or not SV.terminal(cur):
        raise SV.Failure('final state is not terminal: %r' % (cur if words is None else words,))
    return cur


def _replay_one(cur, step, i):
    if step['kind'] == 'automorphism':
        img = step['images']
        signed_perm = (set(img) == {'x', 'y'} and all(v in ('x', 'X', 'y', 'Y') for v in img.values())
                       and img['x'].lower() != img['y'].lower())
        if not (signed_perm or any(img == dict(n) for n in SV.NIELSEN)):
            raise SV.Failure('step %d: images are neither a Nielsen map nor a signed permutation' % i)
        return SV.canon_pair(SV.apply_map(cur[0], img), SV.apply_map(cur[1], img))
    if step['kind'] == 'substitution':
        target, jsign, k1, k2 = map(int, step['move'].split('_'))
        ri, rj = (cur[0], cur[1]) if target == 1 else (cur[1], cur[0])
        oj = rj if jsign == 1 else SV.inverse(rj)
        piece = SV.rotate_right(ri, k1) + SV.rotate_right(oj, k2)
        return SV.canon_pair(piece, cur[1]) if target == 1 else SV.canon_pair(cur[0], piece)
    raise SV.Failure('step %d: unknown kind' % i)
