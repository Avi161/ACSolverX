"""Independent replay of hfcascade certificates.

Shares no code with the solver: its own inverse, free and cyclic reduction, its own
canonical form (minimum over rotations of a word and of its inverse, then the pair sorted),
and its own move semantics.  A step of kind 'automorphism' must carry one of the four
Nielsen maps (x->xy, x->xY, y->yx, y->yX with the other generator fixed); a step of kind
'substitution' carries 'target_jsign_k1_k2' and replaces relator `target` by
rot_k1(r_target) . rot_k2(r_other^jsign), rotation meaning "rotate right by k".  The
recorded state after each step must be the replayed state up to canonical equivalence and
the last state must be two distinct single generators.
"""
from __future__ import annotations

import json
import sys

NIELSEN = ({'x': 'xy', 'y': 'y'}, {'x': 'xY', 'y': 'y'},
           {'x': 'x', 'y': 'yx'}, {'x': 'x', 'y': 'yX'})
_RANK = {'Y': 0, 'y': 1, 'X': 2, 'x': 3}


class Failure(Exception):
    pass


def inverse(w):
    return w[::-1].swapcase()


def reduce(w):
    out = []
    for c in w:
        if c not in 'xXyY':
            raise Failure('bad letter %r' % c)
        if out and out[-1] == c.swapcase():
            out.pop()
        else:
            out.append(c)
    return ''.join(out)


def cyclic(w):
    w = reduce(w)
    while len(w) >= 2 and w[0] == w[-1].swapcase():
        w = w[1:-1]
    return w


def canon_word(w):
    w = cyclic(w)
    if not w:
        return ''
    best = None
    for u in (w, inverse(w)):
        for k in range(len(u)):
            r = u[k:] + u[:k]
            key = (len(r), [_RANK[c] for c in r])
            if best is None or key < best[0]:
                best = (key, r)
    return best[1]


def canon_pair(a, b):
    a, b = canon_word(a), canon_word(b)
    ka, kb = (len(a), [_RANK[c] for c in a]), (len(b), [_RANK[c] for c in b])
    return (a, b) if ka <= kb else (b, a)


def rotate_right(w, k):
    if not w:
        return w
    k %= len(w)
    return w[-k:] + w[:-k] if k else w


def apply_map(w, img):
    return reduce(''.join(img[c] if c.islower() else inverse(img[c.lower()]) for c in w))


def terminal(pair):
    a, b = pair
    return len(a) == 1 and len(b) == 1 and a.lower() != b.lower()


def replay(pair, steps, states=None):
    """Replay `steps` from `pair`; returns the final canonical pair or raises Failure.
    When `states` is given, every recorded state must match the replay canonically."""
    cur = canon_pair(*pair)
    if states is not None:
        if len(states) != len(steps) + 1:
            raise Failure('states/steps length mismatch')
        if canon_pair(*states[0]) != cur:
            raise Failure('recorded root differs from the input')
        cur = tuple(states[0])          # replay moves on the recorded spelling
    for i, step in enumerate(steps):
        if step['kind'] == 'automorphism':
            img = step['images']
            if not any(img == dict(n) for n in NIELSEN):
                raise Failure('step %d: images are not a Nielsen map' % i)
            nxt = canon_pair(apply_map(cur[0], img), apply_map(cur[1], img))
        elif step['kind'] == 'substitution':
            target, jsign, k1, k2 = map(int, step['move'].split('_'))
            if target not in (1, 2) or jsign not in (1, -1) or k1 < 0 or k2 < 0:
                raise Failure('step %d: bad move' % i)
            ri, rj = (cur[0], cur[1]) if target == 1 else (cur[1], cur[0])
            oj = rj if jsign == 1 else inverse(rj)
            piece = rotate_right(ri, k1) + rotate_right(oj, k2)
            nxt = canon_pair(piece, cur[1]) if target == 1 else canon_pair(cur[0], piece)
        else:
            raise Failure('step %d: unknown kind' % i)
        if states is not None:
            rec = tuple(states[i + 1])
            if canon_pair(*rec) != nxt:
                raise Failure('step %d: recorded state differs from the replay' % i)
            cur = rec
        else:
            cur = nxt
    if not terminal(cur):
        raise Failure('final state is not terminal: %r' % (cur,))
    return cur


def main(argv):
    total = ok = 0
    for path in argv:
        with open(path) as f:
            for line in f:
                rec = json.loads(line)
                if not rec.get('solved'):
                    continue
                total += 1
                try:
                    replay((rec['r1'], rec['r2']), rec['steps'], rec.get('states'))
                    ok += 1
                except Failure as exc:
                    print('FAIL', rec.get('name'), exc)
    print('verified %d/%d' % (ok, total))
    return 0 if ok == total else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
