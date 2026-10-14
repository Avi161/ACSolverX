"""Higher-rank moves of the hybrid: products, digram definitions, eliminations, transvections.

A state is a balanced presentation ``(R_1, .., R_n)`` on generators ``1..n``: each relator cyclically reduced and
the least of its rotations and those of its inverse in int order (``-2 < -1 < 1 < 2``, not the Booth order of
``acx.core.words``), the tuple sorted. The search's tie-breaks depend on this order. Every move returns
``(normalized child, event)``; ``acx.hybrid.certify`` writes each event out as elementary and stable AC moves.

``product``    ``R_i <- R_i[k1:] R_i[:k1] . B[k2:] B[:k2]`` with ``B = R_j^sign``, at most ``cap`` letters.
``define``     a digram ``d`` used at least ``min_uses`` times gets a new generator ``h`` with relator ``h^-1 d``.
``eliminate``  a generator occurring once in ``R_i`` is substituted away and ``R_i`` dropped.
``nielsen``    the transvection ``x_i -> x_i x_j^sign`` on every relator.

``relabel_canonical`` quotients states by permutations of the generators; the permutation is part of the step.

This module is the reference (backend ``"spec"``); ``acx.hybrid_highspeedup.dynkernels`` compiles the same moves with
numba (backend ``"fast"``), same output bit for bit. ``backend(name)`` gives the moves the search calls.
"""
from collections import Counter, namedtuple

from ..core.config import BACKENDS
from ..core.digrams import digram_counts, tokenize
from ..core.priority import length
from ..core.words import inverse, reduce, renumber, substitute_generator


def dcanon(w):
    """Cyclically reduce, then the least rotation of ``w`` or ``w^-1`` in int order."""
    w = reduce(w)
    return _least_rotation(w) if w else ()


def _least_rotation(w):
    """The least rotation of the reduced ``w`` or ``w^-1``: it starts with their least letter, so only those starts
    are compared."""
    v = inverse(w)
    m = min(w) if min(w) < min(v) else min(v)
    return min(u[k:] + u[:k] for u in (w, v) for k in range(len(u)) if u[k] == m)


def normalize(words):
    """The state: every relator in ``dcanon`` form, sorted."""
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
    """``(canonical relabelling of words, {perm, signs})``: the state up to permuting the generators."""
    canon, perm, signs = relabel_canonical(words)
    return canon, {"perm": perm, "signs": signs}


# ---------------------------------------------------------------- moves
def products(words, cap):
    """``(children, cut)``: every rotation product with a result of at most ``cap`` letters (first move per child), and
    for each longer one ``(total, needed, rank, (i, product))``: the child's total length, the cap that would admit it,
    its rank and what it takes to build the child (``(i, product)`` replaces relator ``i``; ``product`` is reduced but
    not yet ``dcanon``, which only the counters need). ``words`` is a normalized state."""
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
                        product = reduce(left + base[k2:] + base[:k2])
                        if not product:
                            continue
                        size = len(product)
                        if cap is not None and size > cap:      # left reduced, not canonical: lazy_entries does that
                            if size != len(target) or _least_rotation(product) != target:
                                cut.append((total - len(target) + size, size, n, (i, product)))
                            continue
                        product = _least_rotation(product)
                        if product == target:
                            continue
                        key = tuple(sorted(words[:i] + (product,) + words[i + 1:]))   # words are normalized
                        if key not in seen:
                            seen[key] = {"kind": "product", "i": i, "j": j, "sign": sign,
                                         "k1": k1, "k2": k2, "result": product}
    return list(seen.items()), cut


def define(words, d):
    """Add generator ``h = n + 1`` with relator ``h^-1 d``; every relator rewritten (its template)."""
    h = len(words) + 1
    templates = tuple(w if len(w) < 2 else min((tokenize(w[k:] + w[:k], d, h) for k in range(len(w))),
                                               key=lambda t: (len(t), t)) for w in words)
    uses = sum(abs(x) == h for t in templates for x in t)
    return ((-h,) + d,) + templates, {"kind": "define", "digram": d, "h": h, "uses": uses, "templates": templates}


def defines(words, min_uses=2):
    """Every ``define`` child ``(normalized state, event)`` of a digram used at least ``min_uses`` times."""
    out = []
    for d, count in digram_counts(words).items():
        if count < min_uses:
            continue
        raw, event = define(words, d)
        if event["uses"] >= min_uses:
            out.append((normalize(raw), event))
    return out


def eliminate(words, i, g):
    """Eliminate generator ``g`` with relator ``i``, in which it occurs exactly once."""
    r = words[i]
    k = next(k for k, x in enumerate(r) if abs(x) == g)
    rot = r[k:] + r[:k]                          # g^e u
    image = inverse(rot[1:]) if rot[0] > 0 else rot[1:]
    raw = tuple(renumber(substitute_generator(w, g, image), g) for idx, w in enumerate(words) if idx != i)
    return raw, {"kind": "eliminate", "i": i, "g": g, "image": image}


def eliminations(words):
    """Every ``eliminate`` child ``(normalized state, event)``: each generator that occurs once in a relator."""
    out = []
    for i, r in enumerate(words):
        for g, c in Counter(abs(x) for x in r).items():
            if c == 1:
                raw, event = eliminate(words, i, g)
                out.append((normalize(raw), event))
    return out


def transvection(word, i, j, sign):
    """``x_i -> x_i x_j^sign`` on one word, then ``dcanon``."""
    return dcanon(substitute_generator(word, i, (i, sign * j)))


def nielsen_children(words):
    """Every transvection ``x_i -> x_i x_j^s`` child ``(normalized state, event)``."""
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


def make_keys(states):
    """``make_key`` of each state, or None where the caller is to call it itself: here all of them, one by one."""
    return [None] * len(states)


def most_uses(words):
    """The count of the most frequent cyclic digram of ``words`` (0 if none): the most a define can save."""
    return max(digram_counts(words).values(), default=0)


Moves = namedtuple("Moves", "children defines normalize make_key dcanon make_keys children_lazy most_uses")
SPEC = Moves(children, defines, normalize, make_key, dcanon, make_keys, children, most_uses)


def backend(name):
    """The higher-rank moves the search calls, ``Moves``: ``spec`` this module, ``fast`` (numba, ``dynkernels``) the
    same functions compiled; ``fast`` is imported only when asked for, and its kernels are loaded on the first ask
    (``dynkernels.warm``: the runner's warm-up solve asks, so no timed row pays for it). ``make_keys`` and
    ``children_lazy`` are the search's batched forms (``make_key`` of many states; ``children`` with the cut products
    left as arrays)."""
    if name == "spec":
        return SPEC
    if name != "fast":
        raise ValueError(f"backend {name!r} not in {BACKENDS}")
    from ..hybrid_highspeedup import dynkernels as K
    K.warm()
    return Moves(K.children, K.defines, K.normalize, K.make_key, K.dcanon, K.make_keys, K.children_lazy, K.most_uses)
