"""Independent replayer for dynamic-rank certificates.

Uses its own word routines (deliberately not imported from ``dynrank``).  For
every step it rebuilds the child from the parent's stored words and the event's
parameters, checks the algebraic identity behind the move, applies the recorded
renaming, and compares with the stored ``after``.  A certificate is accepted only
if the last state is the empty presentation.

Usage: ``python3 verify.py records.jsonl [...]`` prints a summary and exits
non-zero on any failure.
"""
from __future__ import annotations

import json
import sys
from collections import Counter


def inv(w):
    return tuple(-x for x in w[::-1])


def free_reduce(w):
    stack = []
    for x in w:
        if stack and stack[-1] + x == 0:
            stack.pop()
        else:
            stack.append(x)
    return tuple(stack)


def cyc_canon(w):
    w = free_reduce(w)
    while len(w) >= 2 and w[0] + w[-1] == 0:
        w = w[1:-1]
    if not w:
        return ()
    cands = []
    for v in (w, inv(w)):
        for k in range(len(v)):
            cands.append(v[k:] + v[:k])
    return min(cands)


def norm(ws):
    return tuple(sorted(cyc_canon(tuple(w)) for w in ws))


def conj_equal(a, b):
    """cyclic words equal up to conjugation and inversion"""
    return cyc_canon(a) == cyc_canon(b)


class Failure(Exception):
    pass


def replay_product(parent, ev):
    i, j, sign, k1, k2 = ev['i'], ev['j'], ev['sign'], ev['k1'], ev['k2']
    if i == j:
        raise Failure('product with itself')
    target, donor = parent[i], parent[j]
    base = donor if sign == 1 else inv(donor)
    left = target[k1:] + target[:k1]
    right = base[k2:] + base[:k2]
    result = cyc_canon(left + right)
    if result != tuple(ev['result']):
        raise Failure('product result mismatch')
    # the AC identity: left*right is conjugate to target * c * donor^sign * c^-1
    # with c = right_prefix * left_prefix^-1; check it explicitly
    left_prefix, right_prefix = target[:k1], base[:k2]
    c = free_reduce(right_prefix + inv(left_prefix))
    replacement = free_reduce(target + inv(c) + base + c)
    if not conj_equal(replacement, left + right):
        raise Failure('AC identity failed')
    raw = list(parent)
    raw[i] = result
    return norm(raw)


def replay_define(parent, ev, min_uses=None):
    d = tuple(ev['digram'])
    h = ev['h']
    n = len(parent)
    if h != n + 1 or len(d) != 2 or any(abs(x) > n or x == 0 for x in d):
        raise Failure('bad definition')
    templates = [tuple(t) for t in ev['templates']]
    if len(templates) != n:
        raise Failure('template count')
    uses = 0
    for w, t in zip(parent, templates):
        expanded = []
        for x in t:
            if x == h:
                expanded.extend(d)
            elif x == -h:
                expanded.extend(inv(d))
            else:
                expanded.append(x)
        uses += sum(abs(x) == h for x in t)
        if not conj_equal(tuple(expanded), w):
            raise Failure('template does not expand to the relator')
        if len(t) > len(w):
            raise Failure('template longer than relator')
    if uses < 1 or uses != ev['uses']:
        raise Failure('use count')       # min_uses is a search policy, not a soundness condition
    raw = [(-h,) + d] + templates
    return norm(raw)


def replay_eliminate(parent, ev):
    i, g, image = ev['i'], ev['g'], tuple(ev['image'])
    r = parent[i]
    if sum(abs(x) == g for x in r) != 1:
        raise Failure('generator does not occur exactly once')
    if any(abs(x) == g for x in image):
        raise Failure('image contains the eliminated generator')
    # the relator says g^e u = 1 (cyclically); verify substituting the image kills it
    check = []
    for x in r:
        if x == g:
            check.extend(image)
        elif x == -g:
            check.extend(inv(image))
        else:
            check.append(x)
    if cyc_canon(tuple(check)) != ():
        raise Failure('image is not the solution of the relator')
    out = []
    for idx, w in enumerate(parent):
        if idx == i:
            continue
        sub = []
        for x in w:
            if x == g:
                sub.extend(image)
            elif x == -g:
                sub.extend(inv(image))
            else:
                sub.append(x)
        sub = free_reduce(tuple(sub))
        if any(abs(x) == g for x in sub):
            raise Failure('generator survives')
        renum = tuple((abs(x) - (1 if abs(x) > g else 0)) * (1 if x > 0 else -1) for x in sub)
        out.append(renum)
    return norm(out)


def apply_relabel(ws, rl):
    if rl is None:
        return ws
    n = len(ws)
    perm = {int(k): v for k, v in rl['perm'].items()}
    signs = {int(k): v for k, v in rl['signs'].items()}
    if sorted(perm) != list(range(1, n + 1)) or sorted(perm.values()) != list(range(1, n + 1)):
        raise Failure('relabel is not a permutation of 1..n')
    if any(signs.get(g) not in (1, -1) for g in range(1, n + 1)):
        raise Failure('relabel signs')
    out = []
    for w in ws:
        out.append(tuple(perm[abs(x)] * signs[abs(x)] * (1 if x > 0 else -1) for x in w))
    return norm(out)


def replay(root, path, min_uses=2, root_relabel=None):
    """Replay a certificate; raises ``Failure``.  ``root`` is a list of words,
    ``root_relabel`` the renaming applied to the root before the first step."""
    state = apply_relabel(norm(tuple(tuple(w) for w in root)), root_relabel)
    n_def = n_elim = n_prod = 0
    max_rank = len(state)
    for step_no, step in enumerate(path):
        ev = step['event']
        kind = ev['kind']
        if kind == 'product':
            child = replay_product(state, ev)
            n_prod += 1
        elif kind == 'define':
            child = replay_define(state, ev, min_uses)
            n_def += 1
        elif kind == 'eliminate':
            child = replay_eliminate(state, ev)
            n_elim += 1
        elif kind == 'rename':
            child = state                      # a pure renaming, carried by step['relabel']
        else:
            raise Failure('unknown event kind ' + str(kind))
        child = apply_relabel(child, step.get('relabel'))
        stored = norm(tuple(tuple(w) for w in step['after']))
        if child != stored:
            raise Failure(f'step {step_no} ({kind}): replayed state differs from stored state')
        state = child
        max_rank = max(max_rank, len(state))
    if state != ():
        raise Failure('path does not end at the empty presentation')
    return {'steps': len(path), 'products': n_prod, 'defines': n_def, 'eliminates': n_elim,
            'max_rank': max_rank}


def main(argv):
    ok = bad = skipped = 0
    for fn in argv:
        with open(fn) as f:
            for line in f:
                rec = json.loads(line)
                if not rec.get('solved'):
                    skipped += 1
                    continue
                try:
                    info = replay(rec['root'], rec['path'], rec.get('params', {}).get('min_uses', 2),
                                  rec.get('root_relabel'))
                    ok += 1
                except Failure as e:
                    bad += 1
                    print('FAIL', fn, rec.get('name'), rec.get('arm'), e)
    print(f'replayed {ok} certificates ok, {bad} failed, {skipped} unsolved records skipped')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
