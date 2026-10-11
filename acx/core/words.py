"""Words, relators and presentations: the one encoding every acx module shares.

A word is a tuple of nonzero ints: ``abs(g)`` names the generator (1 = x, 2 = y,
3 = z, ...) and the sign is the exponent. A presentation carries ``n_gen``
explicitly, because a substitution can remove the last occurrence of a
generator and AC4 adds a generator that occurs in one relator only.

Two symbol orders exist and must never be mixed up:

* Booth order ``Y < y < X < x`` (generally ``... < Y < y < X < x``):
  canonicalisation minimises over it. It only picks WHICH representative of a
  rotation/inversion orbit is stored. Same as ``is_less_than`` in main's
  ``greedy_baseline.py``.
* ASCII (key) order ``X < Y < x < y`` (inverses first, then by generator): the
  heap tie-break compares state keys in this order. ``state_key`` uses the
  order-preserving codes ``X=1, Y=2, x=3, y=4`` that main's packed keys and the
  fast engine (``hcompact``'s ``_code_of``) use.

Sources: ``origin/test/greedy-test-suite:experiments/greedy_tests/spec/
{words,presentation}.py`` (general-n spec), ``origin/main:experiments/search/
greedy_baseline.py`` (reduction tail, canonical pair order, encodings).
"""
from dataclasses import dataclass

Word = tuple

GEN_CHARS = "xyzabcdefghijklmnopqrstuvw"


def to_char(g):
    c = GEN_CHARS[abs(g) - 1]
    return c if g > 0 else c.upper()


def parse(s):
    """``'xYy'`` -> ``(1, -2, 2)``. Not reduced."""
    return tuple((GEN_CHARS.index(c.lower()) + 1) * (1 if c.islower() else -1) for c in s)


def fmt(w):
    return "".join(map(to_char, w))


def inverse(w):
    return tuple(-g for g in reversed(w))


def rotate(w, k):
    """``np.roll(arr, 2 * k)`` on main's ``(n, 2)`` encoding: element ``m`` is ``w[m - k]``."""
    n = len(w)
    if n == 0:
        return w
    k %= n
    return w[n - k:] + w[:n - k]


def reduce(w, cyclic=True):
    """Free reduction; with ``cyclic`` also cancel across the wrap-around.

    The cyclic tail mirrors main's ``reduce_relator_nj`` exactly, including the
    strict ``i < length / 2`` bound (so it never empties a free-reduced word).
    """
    st = []
    for g in w:
        if st and st[-1] == -g:
            st.pop()
        else:
            st.append(g)
    n = len(st)
    if cyclic and n > 1 and st[0] == -st[-1]:
        i = 1
        while i < n / 2 and st[i] == -st[-1 - i]:
            i += 1
        st = st[i:-i]
    return tuple(st)


def free(w):
    """Free reduction only (no cyclic cancellation)."""
    return reduce(w, cyclic=False)


def conjugators(w, t):
    """Every ``(sign, c)`` with ``free(c^-1 w^sign c) == free(t)``: two per rotation of the cyclic core of
    ``w^sign`` that is ``t``'s, the first ``a . C[:k] . b^-1`` (``w = a C a^-1``, ``t = b D b^-1``)."""
    w, t = free(w), free(t)
    cw, ct = reduce(w), reduce(t)
    a, b = w[:(len(w) - len(cw)) // 2], t[:(len(t) - len(ct)) // 2]
    for sign, cs in ((1, cw), (-1, inverse(cw))):
        for k in range(max(len(cs), 1)):
            if cs[k:] + cs[:k] == ct:
                yield sign, free(a + cs[:k] + inverse(b))
                yield sign, free(a + inverse(cs[k:]) + inverse(b))


def is_cyclically_reduced(w):
    return all(a != -b for a, b in zip(w, w[1:])) and (len(w) < 2 or w[0] != -w[-1])


# Booth order as single characters, so that min() over str slices is Booth's least rotation:
# chr(0x1000 - 2|g| + (g > 0)) gives ... < Y < y < X < x.
class _Table(dict):
    def __init__(self, f):
        super().__init__()
        self.f = f

    def __missing__(self, k):
        v = self[k] = self.f(k)
        return v


def _sym(c):
    v = 0x1000 - ord(c)                   # 2|g| - (g > 0)
    return (v + 1) // 2 if v % 2 else -(v // 2)


_BCHAR = _Table(lambda g: chr(0x1000 - 2 * abs(g) + (g > 0)))
_BSYM = _Table(_sym)


def booth_str(w):
    return "".join([_BCHAR[g] for g in w])


def _from_bstr(s):
    return tuple([_BSYM[c] for c in s])


def canonical_word(w):
    """Least element of the orbit of ``w`` under rotation and inversion (Booth order)."""
    n = len(w)
    if n == 0:
        return w
    s = booth_str(w) * 2
    t = booth_str(inverse(w)) * 2
    return _from_bstr(min(min(s[i:i + n] for i in range(n)), min(t[i:i + n] for i in range(n))))


def sort_rels(rels):
    """Relators sorted by ``(length, Booth order)``: main's pair order."""
    return tuple(sorted(rels, key=lambda r: (len(r), booth_str(r))))


def canonical_rels(rels):
    """Each relator canonical, then sorted (``canonical_pair_nj``)."""
    return sort_rels([canonical_word(r) for r in rels])


def state_key(rels, n_gen=2):
    """The heap tie-break key: per relator the codes (inverses ``1..n_gen``, then generators
    ``n_gen+1..2n_gen``), compared as tuples.

    At ``n_gen = 2`` this sorts exactly like main's ``(r1_str, r2_str)``.
    """
    return tuple(tuple(n_gen + g if g > 0 else -g for g in r) for r in rels)


@dataclass(frozen=True)
class Presentation:
    """A balanced-or-not presentation ``<x_1..x_n_gen | rels>``; words as int tuples."""
    n_gen: int
    rels: tuple

    def __post_init__(self):
        object.__setattr__(self, "rels", tuple(tuple(int(g) for g in r) for r in self.rels))
        if any(g == 0 or abs(g) > self.n_gen for r in self.rels for g in r):
            raise ValueError(f"symbol outside 1..{self.n_gen}: {self.rels}")

    @classmethod
    def parse(cls, *strs, n_gen=None):
        rels = tuple(parse(s) for s in strs)
        if n_gen is None:
            n_gen = max([2] + [abs(g) for r in rels for g in r])
        return cls(n_gen, rels)

    @classmethod
    def from_flat(cls, ints, n_rel=2, n_gen=2):
        """The dataset layout ``[r1 | r2 | ...]``, each slot zero padded."""
        ints = list(ints)
        if len(ints) % n_rel:
            raise ValueError(f"{len(ints)} ints do not split into {n_rel} slots")
        k = len(ints) // n_rel
        return cls(n_gen, tuple(tuple(g for g in ints[i * k:(i + 1) * k] if g) for i in range(n_rel)))

    @property
    def strs(self):
        return tuple(fmt(r) for r in self.rels)

    @property
    def total(self):
        return sum(map(len, self.rels))

    def reduced(self, cyclic=True):
        return Presentation(self.n_gen, tuple(reduce(r, cyclic) for r in self.rels))

    def canonical(self):
        return Presentation(self.n_gen, canonical_rels(self.rels))

    def is_trivial(self):
        """``<x_1..x_n | x_1..x_n>`` up to cyclic reduction, signs and order."""
        rs = [reduce(r) for r in self.rels]
        return (len(rs) == self.n_gen and all(len(r) == 1 for r in rs)
                and {abs(r[0]) for r in rs} == set(range(1, self.n_gen + 1)))

    def __str__(self):
        return "<" + ", ".join(GEN_CHARS[:self.n_gen]) + " | " + ", ".join(self.strs) + ">"
