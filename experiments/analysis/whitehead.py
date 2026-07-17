"""Whitehead's algorithm for F2: Aut(F2)-equivalence of presentations (pairs of cyclic words).

Two presentations related by phi in Aut(F2) are the SAME problem for AC-triviality:
AC moves commute with phi, and phi(trivial) = (phi(x), phi(y)) is a basis, hence
Nielsen- (= AC-) equivalent to (x, y). So P is AC-trivial iff phi(P) is.

Relators are cyclic words up to inversion, and the pair is unordered (all AC moves),
so the state is the canonical pair.
"""

def inv(w):
    return w[::-1].swapcase()

def free_reduce(w):
    out = []
    for c in w:
        if out and out[-1] == c.swapcase():
            out.pop()
        else:
            out.append(c)
    return "".join(out)

def cyc_reduce(w):
    w = free_reduce(w)
    while len(w) >= 2 and w[0] == w[-1].swapcase():
        w = w[1:-1]
        w = free_reduce(w)
    return w

def canon_rel(w):
    """lex-min over rotations of w and w^-1 -- rotation+inversion invariant."""
    w = cyc_reduce(w)
    if not w:
        return ""
    cands = []
    for u in (w, inv(w)):
        for i in range(len(u)):
            cands.append(u[i:] + u[:i])
    return min(cands)

def canon_pair(r1, r2):
    a, b = canon_rel(r1), canon_rel(r2)
    return (a, b) if (len(a), a) <= (len(b), b) else (b, a)

def _apply(w, img):
    out = []
    for c in w:
        out.append(img[c] if c.islower() else inv(img[c.lower()]))
    return "".join(out)

def apply_auto(pair, img):
    return canon_pair(_apply(pair[0], img), _apply(pair[1], img))

def _build_autos():
    autos = []
    # --- first kind: the 8 signed permutations of {x, y} ---
    for fx in ("x", "X", "y", "Y"):
        for fy in ("x", "X", "y", "Y"):
            if fx.lower() == fy.lower():
                continue
            autos.append((f"x->{fx},y->{fy}", {"x": fx, "y": fy}))
    # --- second kind: Whitehead automorphisms (A, a), A = {a} u S, S subset of other letters ---
    # a = x : y -> y x | X y | X y x      (and the a = X, y, Y analogues)
    second = [
        ("W(x): y->yx",  {"x": "x", "y": "yx"}),
        ("W(x): y->Xy",  {"x": "x", "y": "Xy"}),
        ("W(x): y->Xyx", {"x": "x", "y": "Xyx"}),   # inner (conjugation) -- harmless on cyclic words
        ("W(X): y->yX",  {"x": "x", "y": "yX"}),
        ("W(X): y->xy",  {"x": "x", "y": "xy"}),
        ("W(X): y->xyX", {"x": "x", "y": "xyX"}),
        ("W(y): x->xy",  {"y": "y", "x": "xy"}),
        ("W(y): x->Yx",  {"y": "y", "x": "Yx"}),
        ("W(y): x->Yxy", {"y": "y", "x": "Yxy"}),
        ("W(Y): x->xY",  {"y": "y", "x": "xY"}),
        ("W(Y): x->yx",  {"y": "y", "x": "yx"}),
        ("W(Y): x->yxY", {"y": "y", "x": "yxY"}),
    ]
    autos.extend(second)
    return autos

AUTOS = _build_autos()

def total(p):
    return len(p[0]) + len(p[1])

def peak_reduce(pair):
    """Greedy strict descent. Peak reduction: if ANY automorphism shortens the tuple,
    some Whitehead automorphism does -- so this lands on the orbit minimum length."""
    cur = canon_pair(*pair)
    while True:
        best = None
        for _, img in AUTOS:
            nxt = apply_auto(cur, img)
            if total(nxt) < total(cur) and (best is None or total(nxt) < total(best)):
                best = nxt
        if best is None:
            return cur
        cur = best

def orbit_component(pair, cap=200_000):
    """All minimal-length representatives reachable from `pair` through minimal-length states.
    Peak reduction => this is exactly the orbit's minimal level set, and it is connected."""
    start = peak_reduce(pair)
    t = total(start)
    seen = {start}
    stack = [start]
    while stack:
        if len(seen) > cap:
            return seen, t, True
        cur = stack.pop()
        for _, img in AUTOS:
            nxt = apply_auto(cur, img)
            if total(nxt) == t and nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return seen, t, False

def canonical_form(pair):
    """Aut(F2) invariant: (minimal total length, lex-min minimal representative).
    Two presentations are Aut(F2)-equivalent IFF their canonical forms are equal."""
    comp, t, capped = orbit_component(pair)
    return (t, min(comp)), len(comp), capped
