"""Higher-rank moves of the hybrid solver: products, digram definitions, eliminations, transvections.

A dynamic-rank state is a balanced presentation ``(R_1, .., R_n)`` on generators
``1..n`` in this module's own normal form: each relator cyclically reduced and
replaced by the least of its rotations and those of its inverse in INT order
(``-2 < -1 < 1 < 2``, not the Booth order of ``acx.core.words``), the tuple
sorted. The search's tie-breaks depend on this order, so it is kept as the
source had it. Moves, each returned as ``(normalized child, event)``:

``product``    ``R_i <- R_i[k1:] R_i[:k1] . B[k2:] B[:k2]`` with ``B = R_j^sign``
               (left rotations), the result at most ``cap`` letters: an AC move.
``define``     a cyclic digram ``d = (a, b)`` occurring at least ``min_uses``
               times: add generator ``h = n + 1`` with relator ``h^-1 a b`` and
               rewrite every relator, ``d -> h`` and ``d^-1 -> h^-1`` (shortest
               tokenisation over its rotations). A stabilisation, the
               automorphism ``h -> h^-1 a b`` and AC moves.
``eliminate``  a generator ``g`` occurring once in ``R_i = g^e u``: substitute
               ``g -> image`` (``u^-1`` or ``u``) in the other relators, drop
               ``R_i``, renumber the generators above ``g``. AC moves, the
               automorphism ``g -> g u`` and a destabilisation.
``nielsen``    the transvection ``x_i -> x_i x_j^sign`` on every relator (an
               automorphism of the free group).

``relabel_canonical`` quotients states by permutations of the generators
(individualisation-refinement); the chosen permutation is part of the step so
the certificate can be replayed. ``acx.hybrid.certify`` turns every event into
elementary and stable moves (``define`` and ``eliminate`` are written out, not
assumed), so a certificate that uses them is a replayable stable AC path.

Port of ``origin/claude/vigilant-babbage-nnbuj0:research/ac_dynamic_rank_20260913/
dynrank.py`` (moves, relabelling; ``tokenize`` is ``acx.ngen.sac``'s) and
``research/ac_hashfree_cascade_20260914/hfunified.py`` (``nielsen_children``),
commit 5ae1bd8e; the drivers (``best_first``, ``closure``) and ``triangulate``
(``acx.ngen.sac``) are not ported.
"""
from collections import Counter

from ..core.priority import length
from ..core.words import inverse, reduce
from ..ngen.sac import tokenize


def dcanon(w):
    """Cyclically reduce, then the least rotation of ``w`` or ``w^-1`` in int order."""
    w = reduce(w)
    if not w:
        return ()
    return min(v[k:] + v[:k] for v in (w, inverse(w)) for k in range(len(v)))


def normalize(words):
    return tuple(sorted(dcanon(w) for w in words))


# ---------------------------------------------------------------- generator relabelling
def apply_relabel(words, perm, signs):
    """``x_g -> x_perm[g] ** signs[g]`` (1-based dicts), then normalized."""
    return normalize(tuple(perm[abs(x)] * signs[abs(x)] * (1 if x > 0 else -1) for x in w) for w in words)


def _refine(words, n, colour):
    """Colour refinement of the generators by sign-blind cyclic adjacency."""
    while True:
        nbr = {g: [] for g in range(1, n + 1)}
        for w in words:
            m = len(w)
            if m < 2:
                continue
            for k in range(m):
                a, b = abs(w[k]), abs(w[(k + 1) % m])
                nbr[a].append(colour[b])
                nbr[b].append(colour[a])
        sig = {g: (colour[g], tuple(sorted(nbr[g]))) for g in range(1, n + 1)}
        index = {v: i for i, v in enumerate(sorted(set(sig.values())))}
        new = {g: index[sig[g]] for g in range(1, n + 1)}
        if len(index) == len(set(colour.values())):
            return new
        colour = new


def _initial_colour(words, n):
    base = {}
    for g in range(1, n + 1):
        rows = tuple(sorted((len(w), sum(abs(x) == g for x in w)) for w in words if any(abs(x) == g for x in w)))
        base[g] = (sum(abs(x) == g for w in words for x in w), rows)
    index = {v: i for i, v in enumerate(sorted(set(base.values())))}
    return {g: index[base[g]] for g in range(1, n + 1)}


def relabel_canonical(words, limit=20000):
    """``(least normalize over generator permutations, perm, signs)``; signs are all +1."""
    n = len(words)
    if any(abs(x) > n or x == 0 for w in words for x in w):
        raise ValueError("letters must lie in 1..rank")
    signs = {g: 1 for g in range(1, n + 1)}
    best = [None, None, 0]

    def search(colour):
        colour = _refine(words, n, colour)
        classes = {}
        for g, c in colour.items():
            classes.setdefault(c, []).append(g)
        multi = [c for c in sorted(classes) if len(classes[c]) > 1]
        if not multi:
            perm = {g: colour[g] + 1 for g in colour}
            cand = apply_relabel(words, perm, signs)
            best[2] += 1
            if best[2] > limit:
                raise RuntimeError("relabel_canonical leaf limit exceeded")
            if best[0] is None or cand < best[0]:
                best[0], best[1] = cand, perm
            return
        c = multi[0]
        for g in classes[c]:
            search({h: 2 * ch + (1 if (ch == c and h != g) else 0) for h, ch in colour.items()})

    search(_initial_colour(words, n))
    return best[0], best[1], dict(signs)


def make_key(words):
    canon, perm, signs = relabel_canonical(words)
    return canon, {"perm": perm, "signs": signs}


# ---------------------------------------------------------------- moves
def products(words, cap):
    """``(children, cut)``: every rotation product with a result of at most ``cap`` letters (first move per child), and
    for each longer one ``(total, needed, rank, (i, product))``: the child's total length, the cap that would admit it,
    its rank and what it takes to build the child (``(i, product)`` replaces relator ``i``)."""
    n, total = len(words), sum(map(len, words))
    seen, cut = {}, []
    for i in range(n):
        target = words[i]
        if not target:
            continue
        for j in range(n):
            if i == j or not words[j]:
                continue
            for sign in (1, -1):
                base = words[j] if sign == 1 else inverse(words[j])
                for k1 in range(len(target)):
                    left = target[k1:] + target[:k1]
                    for k2 in range(len(base)):
                        product = dcanon(left + base[k2:] + base[:k2])
                        if not product or product == target:
                            continue
                        if cap is not None and len(product) > cap:
                            cut.append((total - len(target) + len(product), len(product), n, (i, product)))
                            continue
                        key = normalize(words[:i] + (product,) + words[i + 1:])
                        if key not in seen:
                            seen[key] = {"kind": "product", "i": i, "j": j, "sign": sign,
                                         "k1": k1, "k2": k2, "result": product}
    return list(seen.items()), cut


def digram_counts(words):
    counts = Counter()
    for w in words:
        m = len(w)
        if m < 2:
            continue
        for k in range(m):
            d = (w[k], w[(k + 1) % m])
            counts[min(d, inverse(d))] += 1
    return counts


def define(words, d):
    """Add generator ``h = n + 1`` with relator ``h^-1 d``; every relator rewritten (its template)."""
    h = len(words) + 1
    templates = tuple(w if len(w) < 2 else min((tokenize(w[k:] + w[:k], d, h) for k in range(len(w))),
                                               key=lambda t: (len(t), t)) for w in words)
    uses = sum(abs(x) == h for t in templates for x in t)
    return ((-h,) + d,) + templates, {"kind": "define", "digram": d, "h": h, "uses": uses, "templates": templates}


def defines(words, min_uses=2):
    out = []
    for d, count in digram_counts(words).items():
        if count < min_uses:
            continue
        raw, event = define(words, d)
        if event["uses"] >= min_uses:
            out.append((normalize(raw), event))
    return out


def substitute(word, g, image):
    out = []
    for x in word:
        out.extend(image if x == g else inverse(image) if x == -g else (x,))
    return reduce(tuple(out), cyclic=False)


def renumber(word, g):
    return tuple((abs(x) - 1 if abs(x) > g else abs(x)) * (1 if x > 0 else -1) for x in word)


def eliminate(words, i, g):
    """Eliminate generator ``g`` with relator ``i``, in which it occurs exactly once."""
    r = words[i]
    k = next(k for k, x in enumerate(r) if abs(x) == g)
    rot = r[k:] + r[:k]                          # g^e u
    image = inverse(rot[1:]) if rot[0] > 0 else rot[1:]
    raw = tuple(renumber(substitute(w, g, image), g) for idx, w in enumerate(words) if idx != i)
    return raw, {"kind": "eliminate", "i": i, "g": g, "image": image}


def eliminations(words):
    out = []
    for i, r in enumerate(words):
        for g, c in Counter(abs(x) for x in r).items():
            if c == 1:
                raw, event = eliminate(words, i, g)
                out.append((normalize(raw), event))
    return out


def transvection(word, i, j, sign):
    """``x_i -> x_i x_j^sign`` on one word, then ``dcanon``."""
    out = []
    for x in word:
        out.extend((i, sign * j) if x == i else (-sign * j, -i) if x == -i else (x,))
    return dcanon(tuple(out))


def nielsen_children(words):
    n = len(words)
    return [(normalize(transvection(w, i, j, s) for w in words), {"kind": "nielsen", "i": i, "j": j, "sign": s})
            for i in range(1, n + 1) for j in range(1, n + 1) if i != j for s in (1, -1)]


def children(words, cap, ceiling, min_uses=2):
    """``(kept, cut, over)``: every admissible child ``(normalized child, event)`` within the total-length ``ceiling``,
    and the children the cap (``cut``) or the ceiling (``over``) rejected, each ``(total, needed, rank, payload)`` as in
    ``products`` (``payload`` the normalized child, or ``(i, product)``), ``needed`` the cap, or for ``over`` the ceiling,
    that would admit it.

    ``cap`` bounds the relators a product or an elimination creates (``None``: no bound); a definition never lengthens
    a relator. Relators inherited unchanged may exceed ``cap``.
    """
    prods, cut = products(words, cap)
    kept = []
    for k, e in eliminations(words):
        longest = max(map(len, k), default=0)
        if cap is None or longest <= cap:
            kept.append((k, e))
        else:
            cut.append((length(k), longest, len(k), k))
    out, over = [], []
    for k, e in prods + defines(words, min_uses) + kept + nielsen_children(words):
        total = length(k)
        if total <= ceiling:
            out.append((k, e))
        else:
            over.append((total, total, len(k), k))
    return out, cut, over
