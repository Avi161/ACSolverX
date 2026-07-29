"""Independent re-implementation of the Neuwirth dictionary + spike calculus, written
from the DEFINITIONS in R7_SPELLING_SPACE.md sections 0-3 only, for the purpose of an
adversarial audit of that note.  Deliberately shares NO code with
``neuwirth_rank_n.py``; the two are cross-checked against each other in
``audit_r7_checks.py``.

Conventions (R7 section 0):
  * letters: lowercase = generator, uppercase = its inverse.
  * germs: generator k has germ ids 2k (``g+``) and 2k+1 (``g-``).
  * dep(g) = g+, arr(g) = g-, dep(G) = g-, arr(G) = g+.
  * occurrence i carries darts d_i = 2i at dep(a_i) and h_i = 2i+1 at arr(a_i);
    B swaps them; A pairs h_i with d_{i+1} cyclically inside each relator.
  * UNHALVED defect(C) = |A| - |C| + 2L - |AC|, gamma_N = min_C defect(C) / 2.
"""

from __future__ import annotations

from itertools import permutations
from math import factorial


# ----------------------------------------------------------------------------------
# dictionary
# ----------------------------------------------------------------------------------


def gens_of(words):
    return tuple(sorted({c.lower() for w in words for c in w}))


def dep_arr(letter, gidx):
    k = gidx[letter.lower()]
    if letter.islower():
        return 2 * k, 2 * k + 1
    return 2 * k + 1, 2 * k


class Dict0:
    """The exact occurrence dictionary of a word-realized complex."""

    def __init__(self, words, generators=None):
        self.words = tuple(words)
        self.generators = tuple(generators) if generators else gens_of(words)
        gidx = {g: i for i, g in enumerate(self.generators)}
        self.n_germs = 2 * len(self.generators)
        letters, rel_of, starts = [], [], []
        for j, w in enumerate(self.words):
            if not w:
                raise ValueError("empty relator")
            starts.append(len(letters))
            for c in w:
                if c.lower() not in gidx:
                    raise ValueError(f"letter {c} outside generators")
                letters.append(c)
                rel_of.append(j)
        self.letters = tuple(letters)
        self.relator_of = tuple(rel_of)
        self.n_occ = len(letters)
        self.n_darts = 2 * self.n_occ
        # B
        self.B = tuple((i ^ 1) for i in range(self.n_darts))
        # germ of each dart
        germ = [0] * self.n_darts
        for i, c in enumerate(letters):
            d, h = dep_arr(c, gidx)
            germ[2 * i] = d
            germ[2 * i + 1] = h
        self.germ = tuple(germ)
        # A: h_i ~ d_{i+1} cyclically inside each relator
        A = [-1] * self.n_darts
        for j, w in enumerate(self.words):
            base, m = starts[j], len(w)
            for k in range(m):
                i, nxt = base + k, base + (k + 1) % m
                A[2 * i + 1] = 2 * nxt
                A[2 * nxt] = 2 * i + 1
        assert all(a >= 0 for a in A)
        self.A = tuple(A)
        self.starts = tuple(starts)
        # corners = A-edges, one per occurrence
        corners = []
        seen = [False] * self.n_darts
        for d in range(self.n_darts):
            if seen[d]:
                continue
            seen[d] = seen[A[d]] = True
            corners.append((d, A[d]))
        self.corners = tuple(corners)
        assert len(self.corners) == self.n_occ
        # germ buckets
        buckets = [[] for _ in range(self.n_germs)]
        for d in range(self.n_darts):
            buckets[germ[d]].append(d)
        self.germ_darts = tuple(tuple(b) for b in buckets)
        self.present = tuple(v for v in range(self.n_germs) if buckets[v])
        # link components (union-find over present germs, one edge per corner)
        par = list(range(self.n_germs))

        def find(a):
            while par[a] != a:
                par[a] = par[par[a]]
                a = par[a]
            return a

        for a, b in self.corners:
            ra, rb = find(germ[a]), find(germ[b])
            if ra != rb:
                par[ra] = rb
        self.comp_of = {v: find(v) for v in self.present}
        self.L = len({self.comp_of[v] for v in self.present})
        self.loops = tuple(
            (a, b) for a, b in self.corners if germ[a] == germ[b]
        )

    def degree(self, g):
        return len(self.germ_darts[g])

    def census_size(self):
        tot = 1
        for k in range(len(self.generators)):
            d = self.degree(2 * k)
            if d:
                tot *= factorial(d - 1)
        return tot

    # ---- rotation systems -------------------------------------------------------

    def compatible_orders(self):
        """Yield every compatible rotation system as {germ: cyclic tuple of darts}."""
        pos = [2 * k for k in range(len(self.generators)) if self.germ_darts[2 * k]]
        pools = []
        for g in pos:
            darts = self.germ_darts[g]
            head, tail = darts[0], darts[1:]
            pools.append([(head,) + p for p in permutations(tail)])

        def rec(k, acc):
            if k == len(pos):
                yield dict(acc)
                return
            g = pos[k]
            for order in pools[k]:
                acc[g] = order
                acc[g ^ 1] = tuple(self.B[p] for p in reversed(order))
                yield from rec(k + 1, acc)
                del acc[g]
                del acc[g ^ 1]

        yield from rec(0, {})

    def is_compatible(self, orders):
        """Check the B-reversal law and the germ-fibre condition explicitly."""
        if set(orders) != set(self.present):
            return False
        for v in self.present:
            if sorted(orders[v]) != sorted(self.germ_darts[v]):
                return False
        for k in range(len(self.generators)):
            gp, gm = 2 * k, 2 * k + 1
            if gp not in orders:
                continue
            fwd = orders[gp]
            rev = tuple(self.B[p] for p in reversed(fwd))
            got = orders[gm]
            # cyclic equality
            if len(got) != len(rev):
                return False
            if not any(got == rev[i:] + rev[:i] for i in range(len(rev))):
                return False
        return True

    def defect(self, orders):
        C = {}
        for v, seq in orders.items():
            m = len(seq)
            for i in range(m):
                C[seq[i]] = seq[(i + 1) % m]
        seen = set()
        nAC = 0
        for start in range(self.n_darts):
            if start in seen:
                continue
            nAC += 1
            cur = start
            while cur not in seen:
                seen.add(cur)
                cur = self.A[C[cur]]
        return self.n_occ - len(self.present) + 2 * self.L - nAC

    def histogram(self):
        h = {}
        for o in self.compatible_orders():
            v = self.defect(o)
            h[v] = h.get(v, 0) + 1
        return h

    def gamma_N(self):
        return min(self.histogram()) // 2


# ----------------------------------------------------------------------------------
# generic ribbon graph, for the interpolation of R7 section 1.4
# ----------------------------------------------------------------------------------


def ribbon_def(orders, edges):
    """def(R) = e - v + 2c - f for the ribbon graph with the given germ rotations.

    ``orders``: {germ: cyclic tuple of darts present at that germ} (empty germs absent).
    ``edges``: iterable of unordered dart pairs; every dart of ``orders`` must appear
    in exactly one edge.
    """
    edges = [tuple(e) for e in edges]
    darts = set()
    for v, seq in orders.items():
        for d in seq:
            darts.add(d)
    A = {}
    for a, b in edges:
        A[a] = b
        A[b] = a
    assert set(A) == darts, (sorted(set(A) ^ darts))
    C = {}
    for v, seq in orders.items():
        m = len(seq)
        for i in range(m):
            C[seq[i]] = seq[(i + 1) % m]
    germ_of = {}
    for v, seq in orders.items():
        for d in seq:
            germ_of[d] = v
    verts = [v for v, seq in orders.items() if seq]
    e = len(edges)
    v = len(verts)
    # components
    par = {x: x for x in verts}

    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a

    for a, b in edges:
        ra, rb = find(germ_of[a]), find(germ_of[b])
        if ra != rb:
            par[ra] = rb
    c = len({find(x) for x in verts})
    # faces
    seen = set()
    f = 0
    for start in darts:
        if start in seen:
            continue
        f += 1
        cur = start
        while cur not in seen:
            seen.add(cur)
            cur = A[C[cur]]
    return e - v + 2 * c - f, dict(e=e, v=v, c=c, f=f)


# ----------------------------------------------------------------------------------
# spikes
# ----------------------------------------------------------------------------------


def spike_words(words, j, k, u):
    """SPIKE(P; j, k, u): insert u u^-1 between positions k-1 and k of relator j."""
    w = words[j]
    N = len(w)
    k = k % N
    inv = u.swapcase()
    new = w[:k] + u + inv + w[k:]
    return tuple(words[:j]) + (new,) + tuple(words[j + 1:])


def spike_layout(words, j, k, u):
    """Global occurrence indices for the spiked presentation and the dart names of
    R7 section 1.1, computed independently of the Dict0 constructor.

    Returns a dict with the pre-indices (in P) and post-indices (in P'), and the
    four spike darts plus the germs X, Y, s, t.
    """
    words = tuple(words)
    N = len(words[j])
    k = k % N
    pre_start = sum(len(words[i]) for i in range(j))
    post_start = pre_start
    gidx = {g: i for i, g in enumerate(gens_of(words))}
    # occurrence indices inside relator j: pre position m maps to
    #   m            if m < k
    #   m + 2        if m >= k
    def pre2post(m):
        return m if m < k else m + 2

    p = post_start + k        # the u occurrence
    q = post_start + k + 1    # the u^-1 occurrence
    km1 = (k - 1) % N
    pre_km1 = pre_start + km1
    pre_k = pre_start + k % N
    post_km1 = post_start + pre2post(km1)
    post_k = post_start + pre2post(k % N)
    s, t = dep_arr(u, gidx)
    Xg = dep_arr(words[j][km1], gidx)[1]      # arr(a_{k-1})
    Yg = dep_arr(words[j][k % N], gidx)[0]    # dep(a_k)
    return dict(
        k=k, N=N, p=p, q=q,
        pre_km1=pre_km1, pre_k=pre_k, post_km1=post_km1, post_k=post_k,
        d_p=2 * p, h_p=2 * p + 1, d_q=2 * q, h_q=2 * q + 1,
        pre_h_km1=2 * pre_km1 + 1, pre_d_k=2 * pre_k,
        post_h_km1=2 * post_km1 + 1, post_d_k=2 * post_k,
        s=s, t=t, X=Xg, Y=Yg,
        pre2post=pre2post, pre_start=pre_start,
    )


def dart_pre2post(words, j, k, u):
    """Injection E -> E' of R7 section 1.2 (the identification under which rho deletes
    exactly the four spike darts)."""
    lay = spike_layout(words, j, k, u)
    pre_start = lay["pre_start"]
    N = lay["N"]
    out = {}
    off = 0
    for i, w in enumerate(words):
        for m in range(len(w)):
            pre_occ = off + m
            if i == j:
                post_occ = pre_start + lay["pre2post"](m)
            elif i < j:
                post_occ = pre_occ
            else:
                post_occ = pre_occ + 2
            out[2 * pre_occ] = 2 * post_occ
            out[2 * pre_occ + 1] = 2 * post_occ + 1
        off += len(w)
    return out


def restrict(orders_post, words, j, k, u):
    """rho: delete the four spike darts from each germ cycle and pull back to E."""
    m = dart_pre2post(words, j, k, u)
    back = {v: kk for kk, v in m.items()}
    out = {}
    for v, seq in orders_post.items():
        kept = tuple(back[d] for d in seq if d in back)
        if kept:
            out[v] = kept
    return out


def all_spikes(words, generators=None):
    """Every (j, k, u) with u a letter of the alphabet (hypothesis (H) automatic)."""
    gens = tuple(generators) if generators else gens_of(words)
    alpha = [g for g in gens] + [g.upper() for g in gens]
    for j, w in enumerate(words):
        for k in range(len(w)):
            for u in alpha:
                yield j, k, u
