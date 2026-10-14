"""Words (tuples of nonzero ints: ``abs(g)`` the generator, the sign its exponent), relators and presentations.

Booth order ``... < Y < y < X < x`` picks the canonical representative of a rotation/inversion orbit; the heap
tie-break uses the key order ``X < Y < x < y`` (``state_key``). The two must not be mixed up.
"""
import re
from dataclasses import dataclass
from functools import lru_cache
from numbers import Integral

GEN_CHARS = "xyzabcdefghijklmnopqrstuvw"
_NAME = re.compile(r"[gG][1-9]\d*|.", re.DOTALL)        # a long name such as g27, else a single letter


def to_char(g):
    """The letter of ``g`` (``x y z a b ...``, upper case for a negative exponent); ``g27`` / ``G27`` past the 26th."""
    n = abs(g)
    c = GEN_CHARS[n - 1] if n <= len(GEN_CHARS) else f"g{n}"
    return c if g > 0 else c.upper()


@lru_cache(maxsize=None)
def _signed_generator(name):
    """The signed generator of one name from ``to_char``: a letter, or ``g27`` from the 27th on; a capital inverts."""
    n = int(name[1:]) if len(name) > 1 else GEN_CHARS.index(name.lower()) + 1
    if len(name) > 1 and n <= len(GEN_CHARS):
        raise ValueError(f"{name!r} is not a name: generator {n} is written {to_char(n)!r}")
    return n if name.islower() else -n


def parse(s):
    """``'xYy'`` -> ``(1, -2, 2)``; ``'g27'`` is generator 27, the name ``fmt`` gives past the 26th. Not reduced."""
    return tuple(map(_signed_generator, _NAME.findall(s)))


def fmt(w):
    """``(1, -2)`` -> ``'xY'``."""
    return "".join(map(to_char, w))


def inverse(w):
    """The inverse word."""
    return tuple(-g for g in reversed(w))


def rotate(w, k):
    """``w`` rotated right by ``k`` (``np.roll`` convention): element ``m`` of the result is ``w[m - k]``."""
    n = len(w)
    if n == 0:
        return w
    k %= n
    return w[n - k:] + w[:n - k]


def rotate_left(w, k):
    """``w`` rotated left by ``k`` (``0 <= k < len(w)``): it starts at ``w[k]``; ``rotate(w, -k)``."""
    return w[k:] + w[:k]


def reduce(w, cyclic=True):
    """Free reduction; with ``cyclic`` also cancel across the wrap-around, fewer than half the length
    (the baseline's rule), so a freely reduced word never empties."""
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


def conjugate(w, c):
    """``c^-1 w c``, freely reduced."""
    return free(inverse(c) + w + c)


def substitute_generator(w, g, image):
    """``w`` with every ``g`` replaced by ``image`` (``g^-1`` by its inverse), freely reduced."""
    back, out = inverse(image), []
    for x in w:
        out.extend(image if x == g else back if x == -g else (x,))
    return free(out)


def renumber(w, g):
    """``w``, which has no ``g``, with the generators above ``g`` shifted down by one."""
    return tuple((abs(x) - 1 if abs(x) > g else abs(x)) * (1 if x > 0 else -1) for x in w)


def conjugators(w, t):
    """Every ``(sign, c)`` with ``free(c^-1 w^sign c) == free(t)``: two per rotation of the cyclic core of
    ``w^sign`` that is ``t``'s, the first ``a . C[:k] . b^-1`` (``w = a C a^-1``, ``t = b D b^-1``)."""
    w, t = free(w), free(t)
    cw, ct = reduce(w), reduce(t)
    a, b = w[:(len(w) - len(cw)) // 2], t[:(len(t) - len(ct)) // 2]
    for sign, cs in ((1, cw), (-1, inverse(cw))):
        for k in range(max(len(cs), 1)):
            if rotate_left(cs, k) == ct:
                yield sign, free(a + cs[:k] + inverse(b))
                yield sign, free(a + inverse(cs[k:]) + inverse(b))


class _Table(dict):
    """A lookup table computing missing entries with ``compute`` (the Booth characters of the generators in use)."""

    def __init__(self, compute):
        super().__init__()
        self.compute = compute

    def __missing__(self, key):
        value = self[key] = self.compute(key)
        return value


def _booth_char(g):
    """The character of generator symbol ``g`` in Booth order ``... < Y < y < X < x``."""
    return chr(0x1000 - 2 * abs(g) + (g > 0))


def _booth_symbol(char):
    """Inverse of ``_booth_char``."""
    code = 0x1000 - ord(char)             # 2|g| - (g > 0)
    return (code + 1) // 2 if code % 2 else -(code // 2)


_BCHAR = _Table(_booth_char)
_BSYM = _Table(_booth_symbol)


def booth_str(w):
    """``w`` as a string whose character order is Booth order, so that ``min`` over rotations is the least one."""
    return "".join([_BCHAR[g] for g in w])      # a list is faster than a generator here (hot path)


def canonical_word(w):
    """Least element of the orbit of ``w`` under rotation and inversion (Booth order)."""
    n = len(w)
    if n == 0:
        return w
    doubled = booth_str(w) * 2                  # every rotation of w is a length-n window of it
    doubled_inverse = booth_str(inverse(w)) * 2
    least_rotation = min(doubled[i:i + n] for i in range(n))
    least_inverse_rotation = min(doubled_inverse[i:i + n] for i in range(n))
    return tuple([_BSYM[c] for c in min(least_rotation, least_inverse_rotation)])    # list: faster (hot path)


def sort_rels(rels):
    """Relators sorted by ``(length, Booth order)``."""
    return tuple(sorted(rels, key=lambda r: (len(r), booth_str(r))))


def canonical_rels(rels):
    """Each relator canonical, then the relators sorted."""
    return sort_rels([canonical_word(r) for r in rels])


def state_key(rels, n_gen=2):
    """The heap tie-break key: per relator the codes (inverses ``1..n_gen``, then generators
    ``n_gen+1..2n_gen``), compared as tuples. At ``n_gen = 2`` it sorts like the string pair ``(r1, r2)``
    in ASCII order (``X < Y < x < y``)."""
    return tuple(tuple(n_gen + g if g > 0 else -g for g in r) for r in rels)


def state_bytes(rels, n_gen=2):
    """``state_key`` packed as bytes: each relator's codes followed by a 0. Codes are ``>= 1``, so bytes
    order is ``state_key``'s tuple order (a relator that is a proper prefix sorts first); the fast
    engine's ``kernels.tie_bytes`` writes the same bytes. Used for compact keys (cap counters)."""
    return bytes(c for r in state_key(rels, n_gen) for c in (*r, 0))


def _is_integer(value):
    """An int or a NumPy integer scalar, not a bool."""
    return type(value) is int or (isinstance(value, Integral) and not isinstance(value, bool))


@dataclass(frozen=True)
class Presentation:
    """``<x_1..x_n_gen | rels>`` with relators as int tuples (balanced or not; ``n_gen`` is explicit because a
    substitution can remove the last occurrence of a generator and AC4 adds one)."""
    n_gen: int
    rels: tuple

    def __post_init__(self):
        if not _is_integer(self.n_gen) or self.n_gen < 0:
            raise ValueError(f"n_gen must be a nonnegative integer, got {self.n_gen!r}")
        n = int(self.n_gen)
        rels = tuple(map(tuple, self.rels))
        # Plain ints in range, the case of every search and replay step, skip the slower ``Integral`` check.
        if not all(type(g) is int and 0 < abs(g) <= n for r in rels for g in r):
            if not all(_is_integer(g) for r in rels for g in r):
                raise ValueError("generator symbols must be integers (not bools, floats or strings)")
            rels = tuple(tuple(int(g) for g in r) for r in rels)
            if any(g == 0 or abs(g) > n for r in rels for g in r):
                raise ValueError(f"symbol outside 1..{n}: {rels}")
        object.__setattr__(self, "n_gen", n)
        object.__setattr__(self, "rels", rels)

    @classmethod
    def parse(cls, *strs, n_gen=None):
        """``Presentation.parse("xxYXY", "xyyXY")``; ``n_gen`` defaults to the largest generator used (at least 2)."""
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
        """The relators as strings."""
        return tuple(fmt(r) for r in self.rels)

    def reduced(self, cyclic=True):
        """Every relator reduced (``reduce``)."""
        return Presentation(self.n_gen, tuple(reduce(r, cyclic) for r in self.rels))

    def canonical(self):
        """Every relator canonical, then sorted (``canonical_rels``)."""
        return Presentation(self.n_gen, canonical_rels(self.rels))

    def normal(self, cyclic=True):
        """The state a search starts from and a replay normalises to: ``reduced(cyclic).canonical()`` repeated
        until it stops changing. Cyclic reduction is stable after one pass; free reduction alone is not, since
        a canonical rotation of a word need not be freely reduced."""
        p = self.reduced(cyclic).canonical()
        if cyclic:
            # Rotations/inverses of a cyclically reduced word are already cyclically reduced.
            return p
        while (q := p.reduced(cyclic).canonical()) != p:
            p = q
        return p

    def is_trivial(self):
        """``<x_1..x_n | x_1..x_n>`` up to cyclic reduction, signs and order."""
        rs = [reduce(r) for r in self.rels]
        return (len(rs) == self.n_gen and all(len(r) == 1 for r in rs)
                and {abs(r[0]) for r in rs} == set(range(1, self.n_gen + 1)))

    def __str__(self):
        return "<" + ", ".join(map(to_char, range(1, self.n_gen + 1))) + " | " + ", ".join(self.strs) + ">"


def as_presentation(pres):
    """``pres`` as a ``Presentation``: relator strings (``("xxYXY", "xyyXY")``) are parsed."""
    if isinstance(pres, Presentation):
        return pres
    return Presentation.parse(*pres)
