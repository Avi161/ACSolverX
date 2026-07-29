"""The exact Neuwirth occurrence dictionary (D, A, B), the germ map, the support
multigraph, and the factorial ground-truth enumerator for the genus potential.

Everything here is built from the *exact word-realized* presentation complex: no free
reduction, no cyclic reduction, no identification of repeated occurrences.

Conventions (fixed once, everywhere in this package):

* permutations act on the left, products evaluate right-to-left, ``(PQ)(e) = P(Q(e))``;
* ``|Q|`` is the number of cycles of ``Q`` including one-cycles;
* occurrence ``i`` (a position in a relator) owns two darts, ``d_i = 2i`` and
  ``h_i = 2i + 1``: the endpoint the oriented relator boundary departs from, and the
  endpoint it arrives at;
* ``B = prod_i (d_i h_i)`` (the generator tube);
* for every cyclic corner ``a_i a_{i+1}`` of one relator, ``A(h_i) = d_{i+1}`` and
  ``A(d_{i+1}) = h_i``.

Germ map ``nu : D -> {x+, x-, y+, y-}`` (Section "The exact D,A,B dictionary"):

======  ==========  ==========
a_i     nu(d_i)     nu(h_i)
======  ==========  ==========
x       x+          x-
X       x-          x+
y       y+          y-
Y       y-          y+
======  ==========  ==========

so ``nu(B d) = tau(nu(d))`` with ``tau = (x+ x-)(y+ y-)``.

Euler dictionary (Lemma 1).  For a compatible rotation ``C``, the induced cell
structure on the rotation surface has ``|C|`` vertices, ``|A|`` edges and ``|AC|``
faces, and the sum of the component genera is

    defect(C) = |A| - |C| + 2 L(C) - |AC|,   L(C) = #Orb<A, C>,

which is always a nonnegative *even* integer, and the sum of the component genera is
``defect(C) / 2``.  The Neuwirth genus potential is ``gamma_N = min_C defect(C) / 2``.

Because ``A`` is a fixed-point-free involution on the ``2N`` darts, ``|A| = N`` equals
the total word length.  Because each ``C_v`` is a *single* cycle on all darts at germ
``v``, the orbits of ``<A, C>`` are exactly the connected components of the support
multigraph, so ``L(C)`` does not depend on ``C``; ``link_components`` records it and
``euler_data`` recomputes it directly for auditing.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations
from math import factorial

GERM_NAMES = ("x+", "x-", "y+", "y-")
X_POS, X_NEG, Y_POS, Y_NEG = 0, 1, 2, 3
TAU = (X_NEG, X_POS, Y_NEG, Y_POS)

# nu(d_i), nu(h_i) per letter.
_LETTER_GERMS = {
    "x": (X_POS, X_NEG),
    "X": (X_NEG, X_POS),
    "y": (Y_POS, Y_NEG),
    "Y": (Y_NEG, Y_POS),
}

UNKNOWN_SIZE = "UNKNOWN_SIZE"


class NeuwirthInputError(ValueError):
    """Raised when the input is not a legal exact word-realized presentation."""


@dataclass(frozen=True)
class LinkData:
    """The complete exact dictionary of one word-realized presentation complex."""

    words: tuple[str, ...]
    letters: tuple[str, ...]           # letter of each occurrence
    relator_of: tuple[int, ...]        # relator index of each occurrence
    n_occurrences: int
    n_darts: int
    A: tuple[int, ...]
    B: tuple[int, ...]
    germ: tuple[int, ...]              # dart -> germ index
    vertex_darts: tuple[tuple[int, ...], ...]      # germ -> darts at that germ
    edge_darts: tuple[tuple[int, int], ...]        # A-orbit -> its two darts
    edge_of_dart: tuple[int, ...]                  # dart -> A-orbit index
    edge_class: tuple[tuple[int, int], ...]        # A-orbit -> sorted germ pair
    class_edges: dict                              # germ pair -> tuple of A-orbits
    has_loop: bool
    loop_edges: tuple[int, ...]
    link_components: int
    present_germs: tuple[int, ...]

    # -- convenience ---------------------------------------------------------------
    @property
    def n_relators(self) -> int:
        return len(self.words)

    def degree(self, germ: int) -> int:
        return len(self.vertex_darts[germ])

    def positive_end_orders_size(self) -> int:
        """The number of compatible rotation systems, ``prod_g (n_{g+} - 1)!``."""
        total = 1
        for germ in (X_POS, Y_POS):
            n = self.degree(germ)
            if n:
                total *= factorial(n - 1)
        return total


def build_link(words) -> LinkData:
    """Build the exact D/A/B dictionary of the word-realized complex of ``words``."""
    words = tuple(words)
    if not words:
        raise NeuwirthInputError("no relators")
    for w in words:
        if not w:
            raise NeuwirthInputError("empty relator")
        for c in w:
            if c not in _LETTER_GERMS:
                raise NeuwirthInputError(f"bad letter {c!r}")

    letters: list[str] = []
    relator_of: list[int] = []
    starts: list[int] = []
    for j, w in enumerate(words):
        starts.append(len(letters))
        letters.extend(w)
        relator_of.extend([j] * len(w))
    n = len(letters)
    n_darts = 2 * n

    # B: the tube involution.
    B = [0] * n_darts
    for i in range(n):
        B[2 * i] = 2 * i + 1
        B[2 * i + 1] = 2 * i

    # A: the corner involution, cyclic inside each relator.
    A = [-1] * n_darts
    for j, w in enumerate(words):
        base = starts[j]
        m = len(w)
        for k in range(m):
            i = base + k
            nxt = base + (k + 1) % m
            A[2 * i + 1] = 2 * nxt      # A(h_i) = d_{i+1}
            A[2 * nxt] = 2 * i + 1      # A(d_{i+1}) = h_i
    if any(a < 0 for a in A):
        raise NeuwirthInputError("corner involution incomplete")

    germ = [0] * n_darts
    for i, c in enumerate(letters):
        gd, gh = _LETTER_GERMS[c]
        germ[2 * i] = gd
        germ[2 * i + 1] = gh

    vertex_darts = tuple(
        tuple(d for d in range(n_darts) if germ[d] == v) for v in range(4)
    )

    # A-orbits, ordered by their smallest dart.
    edge_darts: list[tuple[int, int]] = []
    edge_of_dart = [-1] * n_darts
    for d in range(n_darts):
        if edge_of_dart[d] >= 0:
            continue
        e = len(edge_darts)
        edge_darts.append((d, A[d]))
        edge_of_dart[d] = e
        edge_of_dart[A[d]] = e
    edge_class = tuple(
        tuple(sorted((germ[a], germ[b]))) for a, b in edge_darts
    )
    class_edges: dict = {}
    for e, key in enumerate(edge_class):
        class_edges.setdefault(key, []).append(e)
    class_edges = {k: tuple(v) for k, v in class_edges.items()}

    loop_edges = tuple(e for e, key in enumerate(edge_class) if key[0] == key[1])
    present = tuple(v for v in range(4) if vertex_darts[v])

    # connected components of the support multigraph on the present germs
    parent = list(range(4))

    def find(a: int) -> int:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for u, v in edge_class:
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
    components = len({find(v) for v in present})

    return LinkData(
        words=words,
        letters=tuple(letters),
        relator_of=tuple(relator_of),
        n_occurrences=n,
        n_darts=n_darts,
        A=tuple(A),
        B=tuple(B),
        germ=tuple(germ),
        vertex_darts=vertex_darts,
        edge_darts=tuple(edge_darts),
        edge_of_dart=tuple(edge_of_dart),
        edge_class=edge_class,
        class_edges=class_edges,
        has_loop=bool(loop_edges),
        loop_edges=loop_edges,
        link_components=components,
        present_germs=present,
    )


# --------------------------------------------------------------------------------------
# permutation arithmetic
# --------------------------------------------------------------------------------------


def cycle_count(perm) -> int:
    """Number of cycles of ``perm`` (given as an image list), one-cycles included."""
    n = len(perm)
    seen = bytearray(n)
    count = 0
    for start in range(n):
        if seen[start]:
            continue
        count += 1
        cur = start
        while not seen[cur]:
            seen[cur] = 1
            cur = perm[cur]
    return count


def compose(p, q):
    """The right-to-left product ``(p q)(e) = p(q(e))``."""
    return tuple(p[q[e]] for e in range(len(q)))


def orbit_count(perms, size: int) -> int:
    """Number of orbits of the group generated by ``perms`` acting on ``range(size)``."""
    seen = bytearray(size)
    count = 0
    for start in range(size):
        if seen[start]:
            continue
        count += 1
        stack = [start]
        seen[start] = 1
        while stack:
            e = stack.pop()
            for p in perms:
                f = p[e]
                if not seen[f]:
                    seen[f] = 1
                    stack.append(f)
    return count


def rotation_from_orders(data: LinkData, orders) -> tuple[int, ...]:
    """Assemble the permutation ``C`` from a per-germ cyclic dart order.

    ``orders`` maps each present germ index to a tuple listing every dart at that germ
    exactly once; ``C`` sends each dart to its successor in that cyclic order.
    """
    C = [-1] * data.n_darts
    for v, seq in orders.items():
        m = len(seq)
        for k in range(m):
            C[seq[k]] = seq[(k + 1) % m]
    if any(c < 0 for c in C):
        raise NeuwirthInputError("rotation does not cover every dart")
    return tuple(C)


def euler_data(data: LinkData, C) -> dict:
    """Lemma 1 numbers for a rotation ``C``: ``|C|``, ``|A|``, ``|AC|``, ``L`` and defect."""
    A = data.A
    AC = tuple(A[C[e]] for e in range(data.n_darts))
    nC = cycle_count(C)
    nA = cycle_count(A)
    nAC = cycle_count(AC)
    L = orbit_count((A, C), data.n_darts)
    defect = nA - nC + 2 * L - nAC
    if defect < 0 or defect % 2:
        raise NeuwirthInputError(f"illegal Euler defect {defect}")
    return {
        "cycles_C": nC,
        "cycles_A": nA,
        "cycles_AC": nAC,
        "link_components": L,
        "defect": defect,
        "genus": defect // 2,
        "euler_characteristic": nC - nA + nAC,
    }


def is_compatible(data: LinkData, C) -> bool:
    """Check Neuwirth compatibility ``C_{tau v} = B C_v^{-1} B`` (globally ``B C B = C^-1``)."""
    B = data.B
    n = data.n_darts
    Cinv = [0] * n
    for e in range(n):
        Cinv[C[e]] = e
    return all(B[C[B[e]]] == Cinv[e] for e in range(n))


# --------------------------------------------------------------------------------------
# factorial ground truth
# --------------------------------------------------------------------------------------


def compatible_orders(data: LinkData):
    """Enumerate every compatible rotation system as a dict ``germ -> dart tuple``.

    One cyclic order is chosen at the positive end of each unsigned generator; the
    first element is pinned to kill the rotation freedom, so the family has exactly
    ``prod_g (n_{g+} - 1)!`` members.  The negative end is the reversed ``B``-image.
    """
    B = data.B
    pos_germs = [g for g in (X_POS, Y_POS) if data.vertex_darts[g]]
    pools = []
    for g in pos_germs:
        darts = data.vertex_darts[g]
        head, tail = darts[0], darts[1:]
        pools.append([(head,) + p for p in permutations(tail)])

    def rec(k: int, acc: dict):
        if k == len(pos_germs):
            yield dict(acc)
            return
        g = pos_germs[k]
        for order in pools[k]:
            acc[g] = order
            acc[TAU[g]] = tuple(B[p] for p in reversed(order))
            yield from rec(k + 1, acc)
            del acc[g]
            del acc[TAU[g]]

    yield from rec(0, {})


def gamma_N_factorial(words, cap_rotations: int = 5_000_000, keep_accepting: bool = True):
    """Exact minimum of the Neuwirth genus potential over every compatible ``C``.

    Returns a dict with the full defect histogram, the minimum, the accepting orders
    (defect 0) and the enumeration size.  If the family is larger than
    ``cap_rotations`` the enumeration is refused and ``status`` is ``UNKNOWN_SIZE``.
    """
    data = build_link(words)
    size = data.positive_end_orders_size()
    if size > cap_rotations:
        return {
            "status": UNKNOWN_SIZE,
            "words": tuple(words),
            "expected_cases": size,
            "cap_rotations": cap_rotations,
            "enumerated_cases": 0,
            "defect_histogram": {},
            "minimum_defect": None,
            "minimum_genus": None,
            "accepting_orders": [],
            "link_components": data.link_components,
        }

    # |A| and L(C) are constant over the family (see the module docstring), so the only
    # per-rotation work is the cycle count of A C.
    nA = data.n_occurrences
    nC = len(data.present_germs)
    L = data.link_components
    A = data.A
    n_darts = data.n_darts

    histogram: dict = {}
    accepting = []
    enumerated = 0
    minimum = None
    for orders in compatible_orders(data):
        C = [0] * n_darts
        for v, seq in orders.items():
            m = len(seq)
            for k in range(m):
                C[seq[k]] = seq[(k + 1) % m]
        seen = bytearray(n_darts)
        nAC = 0
        for start in range(n_darts):
            if seen[start]:
                continue
            nAC += 1
            cur = start
            while not seen[cur]:
                seen[cur] = 1
                cur = A[C[cur]]
        defect = nA - nC + 2 * L - nAC
        histogram[defect] = histogram.get(defect, 0) + 1
        enumerated += 1
        if minimum is None or defect < minimum:
            minimum = defect
        if defect == 0 and keep_accepting:
            accepting.append({GERM_NAMES[v]: seq for v, seq in orders.items()})

    return {
        "status": "OK",
        "words": tuple(words),
        "expected_cases": size,
        "enumerated_cases": enumerated,
        "defect_histogram": histogram,
        "minimum_defect": minimum,
        "minimum_genus": None if minimum is None else minimum // 2,
        "accepting_orders": accepting,
        "link_components": L,
        "degrees": {
            "x": data.degree(X_POS),
            "y": data.degree(Y_POS),
        },
    }
