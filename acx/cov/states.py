"""Every CoV state of a state: the ``suballpxyb8`` images, one per class, as a function a search can call per state.

``cov_states(r1, r2)`` returns the same images, in the same order and with the same representatives, as
``iter_images(Presentation(2, (r1, r2)), None, "suballpxyb8")``, with no length limit. Only the class key is computed
faster: the minimum over the 8 signed permutations of x, y of the pair of cyclic words, each taken up to rotation and
inversion and the pair up to order. Two images whose relators differ by a signed relabelling (x <-> y, x -> x^-1,
...) are one move: they have the same lengths and the same search below them, so only the first is kept, and so is
any image in the class of the state itself.
"""
from .family import proper_subwords
from .images import branches, substitutions
from .substitution import X, Y

# Words are compared as strings over a, b, c, d (x, x^-1, y, y^-1), so rotations and minima run in C.
_CHAR = {1: "a", -1: "b", 2: "c", -2: "d"}
_INVERT = str.maketrans("abcd", "badc")
# The 8 signed permutations of {x, y} (x -> x^+-1 or y^+-1, y -> the other generator^+-1) as string translations.
_SIGNED = tuple(str.maketrans("abcd", t) for t in ("abcd", "abdc", "bacd", "badc", "cdab", "cdba", "dcab", "dcba"))


def _cyclic_reduce(w):
    """Free then cyclic reduction (may give the empty word)."""
    st = []
    for c in w:
        if st and st[-1] == -c:
            st.pop()
        else:
            st.append(c)
    i, j = 0, len(st)
    while j - i > 1 and st[i] == -st[j - 1]:
        i, j = i + 1, j - 1
    return tuple(st[i:j])


def _cyclic_class(s):
    """The least rotation of the string word ``s`` or of its inverse."""
    n = len(s)
    if n == 0:
        return s
    d, e = s + s, (s[::-1].translate(_INVERT)) * 2
    return min(min(d[i:i + n] for i in range(n)), min(e[i:i + n] for i in range(n)))


def class_key(r1, r2):
    """The class of ``<x, y | r1, r2>`` up to relator order, rotation, inversion, cyclic reduction and the 8 signed
    permutations: equal keys exactly when ``acx.cov.images.class_key`` gives equal keys."""
    a = "".join([_CHAR[c] for c in _cyclic_reduce(r1)])
    b = "".join([_CHAR[c] for c in _cyclic_reduce(r2)])
    best = None
    for t in _SIGNED:
        p, q = _cyclic_class(a.translate(t)), _cyclic_class(b.translate(t))
        k = (p, q) if (len(p), p) <= (len(q), q) else (q, p)
        if best is None or k < best:
            best = k
    return best


def cov_states(r1, r2):
    """Every CoV image of ``<x, y | r1, r2>`` in family ``suballpxyb8`` with no length limit, one per class (see the
    module docstring), as ``acx.cov.CoVImage`` (``.pres`` is the new state, ``.steps`` its certificate)."""
    r1, r2 = _cyclic_reduce(r1), _cyclic_reduce(r2)
    if not r1 or not r2:
        return []
    seen, out = {class_key(r1, r2)}, []
    for w in proper_subwords(r1, r2):
        for r1_sub, r2_sub, n_subs in substitutions(r1, r2, w, True):
            for gen in (X, Y):
                for image in branches(r1_sub, r2_sub, n_subs, w, gen, None):
                    key = class_key(*image.pres.rels)
                    if key not in seen:
                        seen.add(key)
                        out.append(image)
    return out
