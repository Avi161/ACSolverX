"""Wholly independent brute-force AC-with-cap neighbour generator.

Different formulation from the module under test:
  * words are python strings over 'xXyY';
  * NO rotations / no connector bound: for a state (r_i, r_j) we enumerate ALL
    freely reduced conjugators u with |u| <= L and form the *literal* group
    element  r_i * (u r_j^e u^-1),  free-reduce it, then cyclically reduce.
    (Rotations of r_i and of r_j^e are absorbed into u, which is why none are
    enumerated here -- see saturation test.)
  * canonical form uses a DIFFERENT letter order (y < Y < x < X) so that the
    module's canonicalisation is not trusted; a state set produced by the
    module is compared after re-canonicalising every relator with this code.
"""
INV = {'x': 'X', 'X': 'x', 'y': 'Y', 'Y': 'y'}
ORD = {'y': 0, 'Y': 1, 'x': 2, 'X': 3}          # deliberately NOT the module's order


def inv(w):
    return "".join(INV[c] for c in reversed(w))


def fr(w):
    out = []
    for c in w:
        if out and out[-1] == INV[c]:
            out.pop()
        else:
            out.append(c)
    return "".join(out)


def cr(w):
    w = fr(w)
    while len(w) >= 2 and w[0] == INV[w[-1]]:
        w = w[1:-1]
    return w


def key(w):
    return tuple(ORD[c] for c in w)


def canon(w):
    w = cr(w)
    if not w:
        raise ValueError("empty relator")
    best = None
    for v in (w, inv(w)):
        for k in range(len(v)):
            r = v[k:] + v[:k]
            if best is None or key(r) < key(best):
                best = r
    return best


def cpair(a, b):
    a, b = canon(a), canon(b)
    if (len(a), key(a)) > (len(b), key(b)):
        a, b = b, a
    return (a, b)


def freely_reduced_words(L):
    """All freely reduced words of length <= L over xXyY."""
    cur = [""]
    out = [""]
    for _ in range(L):
        nxt = []
        for u in cur:
            for c in "xXyY":
                if u and u[-1] == INV[c]:
                    continue
                nxt.append(u + c)
        out.extend(nxt)
        cur = nxt
    return out


def brute_neighbours(state, cap, L, _cache={}):
    """{canonical child}: r_i <- r_i * u r_j^e u^-1 over all |u| <= L."""
    us = _cache.get(L)
    if us is None:
        us = _cache[L] = freely_reduced_words(L)
    r = (canon(state[0]), canon(state[1]))
    out = set()
    for i in (0, 1):
        ri, rj = r[i], r[1 - i]
        for e in (1, -1):
            oj = rj if e == 1 else inv(rj)
            for u in us:
                R = cr(ri + u + oj + inv(u))
                if 1 <= len(R) <= cap:
                    out.add(cpair(R, rj))
    return out


def brute_bfs(r1, r2, cap, L, max_states=2_000_000):
    start = cpair(r1, r2)
    seen = {start}
    frontier = [start]
    while frontier:
        nxt = []
        for st in frontier:
            for ch in brute_neighbours(st, cap, L):
                if ch not in seen:
                    seen.add(ch)
                    nxt.append(ch)
                    if len(seen) > max_states:
                        raise RuntimeError("budget")
        frontier = nxt
    return seen


def recanon_set(pairs_of_strings):
    """Map ['r1','r2'] pairs (any representative) into this module's canon."""
    return {cpair(a, b) for a, b in pairs_of_strings}
