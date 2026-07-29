"""Rank-n Neuwirth sphericity decision for 3-connected planar simple supports.

This is the implementation of ``results/stable_ac/theory/fable/R1C_RANK_N_THREECONNECTED.md``
(Theorem R and Theorem P with the audited repairs [R1]-[R5]).  It decides, for a
presentation ``P = <g_1..g_n | w_1..w_m>`` whose exact word-realized link ``G_A`` is
connected and loopless and whose *simple* support ``S`` is 3-connected and planar,
whether some Neuwirth-compatible rotation system is spherical (``gamma_N = 0``).

Layout of the decision, mirroring the theorem:

* **support extraction** (``build_link_n``) for an arbitrary generator alphabet: germs
  ``g+ = 2k`` and ``g- = 2k + 1`` for the ``k``-th generator, ``tau = (d -> d ^ 1)``, the
  occurrence dictionary ``D, A, B`` exactly as in ``lit_AK3_NEUWIRTH.md`` (no free or
  cyclic reduction, no identification of repeated occurrences).  The ``LinkData``
  container and every *rank-generic* primitive are imported from ``neuwirth_core`` /
  ``neuwirth_rank``; only the pieces those modules hard-code at rank 2 (the four germ
  names, the ``range(4)`` loops, the two-generator phase pair) are re-derived here.
* **(H2) 3-connectivity** by explicit vertex-pair deletion, **(H3) planarity** by the
  macro-rotation enumeration itself.
* **macro-rotation** (Theorem R.2): every rotation system of the simple graph ``S`` is
  enumerated (``prod_v (deg_S(v) - 1)!``, tiny for ``2n <= 8``), the genus-0 ones are
  kept, and for a 3-connected planar ``S`` there must be EXACTLY 2 of them and they must
  be mutual vertex-wise reversals (Whitney).  A different count is a bug or a violated
  hypothesis and raises ``WhitneyViolation`` -- it is never converted into a verdict.
  One reflection is then fixed; Theorem P says this loses no compatible solution.
* **blocks and slots** (Theorem R.1/R.3 + [R3]): at each germ the *cyclic* macro order is
  cut at an arbitrary place (here: at the first neighbour of the enumerated order) and
  the parallel classes are laid out as consecutive blocks of slots.  Changing the cut
  shifts every slot at that germ by one constant, which is absorbed by the enumerated
  phase of that generator, so the arbitrary cut costs nothing.
* **phases** (Lemma 4.1, one per generator), **``H_{A,B}`` relator-cycle propagation**
  (Lemma 4.2 / Theorem 4.3) and **cross-cycle combination** with the global per-class
  all-different and union-cardinality checks (4.4) [R2].

Fail-closed boundary.  ``UNSUPPORTED`` -- never ``NO`` -- is returned for: a malformed
word, a relator shorter than three letters, a generator that does not occur, an
``A``-loop, a disconnected link, fewer than four germs, a simple germ degree below 3, a
2-cut in ``S``, and a support whose planarity could not be settled inside the macro
budget.  ``NOT_SPHERICAL`` is returned for a *certified* non-planar ``S`` (planarity of
``G_A`` implies planarity of its subgraph ``S``, so a non-planar ``S`` kills every
rotation system; the certificate is either the Euler sparsity bound ``|E| > 3|V| - 6``
resp. ``|E| > 2|V| - 4`` for bipartite ``S``, or an exhaustive enumeration of every
rotation system of ``S`` showing none has genus 0), and otherwise only after the full
product of phase tuples x seeds x cross-cycle combinations has been exhausted.  Every
accepted solution is replayed through ``euler_data`` / ``is_compatible`` before it is
returned; a replay failure raises rather than being reported.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations, product
from math import factorial

from experiments.stable_ac.fable.neuwirth_core import (
    LinkData,
    NeuwirthInputError,
    euler_data,
    is_compatible,
    rotation_from_orders,
)
from experiments.stable_ac.fable.neuwirth_rank import (
    MIN_RELATOR_LENGTH,
    NOT_SPHERICAL,
    SPHERICAL,
    UNSUPPORTED,
    WitnessReplayError,
    _adjacency,
    _blocks_to_slots,
    _build_rotations,
    _components,
    _Constraint,
    _propagate,
    _Slots,
    Scheme,
)

__all__ = [
    "SPHERICAL",
    "NOT_SPHERICAL",
    "UNSUPPORTED",
    "MIN_RELATOR_LENGTH",
    "DEFAULT_MACRO_BUDGET",
    "DEFAULT_CENSUS_CAP",
    "WhitneyViolation",
    "WitnessReplayError",
    "NeuwirthInputError",
    "generators_of",
    "germ_names",
    "build_link_n",
    "simple_support",
    "is_three_connected",
    "macro_rotations",
    "classify_support_n",
    "solve_spherical_n",
    "compatible_orders_n",
    "gamma_N_factorial_n",
    "SupportN",
    "MacroResult",
    "CountersN",
    "RankNWitness",
    "RankNDecision",
]

DEFAULT_MACRO_BUDGET = 2_000_000
DEFAULT_CENSUS_CAP = 2_000_000

PLANAR = "PLANAR"
NONPLANAR = "NONPLANAR"
UNDETERMINED = "UNDETERMINED"


class WhitneyViolation(RuntimeError):
    """A 3-connected planar simple support did not have exactly two reflections."""


# --------------------------------------------------------------------------------------
# rank-n occurrence dictionary
# --------------------------------------------------------------------------------------


def generators_of(words) -> tuple:
    """The sorted unsigned generator alphabet implied by ``words``."""
    letters = set()
    for w in words:
        letters.update(w)
    gens = set()
    for c in letters:
        if len(c) != 1 or not c.isalpha():
            raise NeuwirthInputError(f"bad letter {c!r}")
        gens.add(c.lower())
    return tuple(sorted(gens))


def germ_names(generators) -> tuple:
    """``('x+', 'x-', 'y+', 'y-', ...)`` -- germ ``2k`` / ``2k + 1`` of generator ``k``."""
    out = []
    for g in generators:
        out.append(f"{g}+")
        out.append(f"{g}-")
    return tuple(out)


def _letter_germ_table(generators) -> dict:
    """``letter -> (nu(d_i), nu(h_i))`` for every signed letter of the alphabet."""
    table = {}
    for k, g in enumerate(generators):
        pos, neg = 2 * k, 2 * k + 1
        table[g] = (pos, neg)
        table[g.upper()] = (neg, pos)
    return table


def build_link_n(words, generators=None) -> LinkData:
    """The exact ``D/A/B`` dictionary of the word-realized complex at arbitrary rank.

    Structurally identical to ``neuwirth_core.build_link`` but over ``2 * len(generators)``
    germs instead of the four hard-coded ones; the returned container is the very same
    ``LinkData``, so every rank-generic consumer in ``neuwirth_core`` /
    ``neuwirth_rank`` (``rotation_from_orders``, ``euler_data``, ``is_compatible``,
    ``_build_rotations``, ``_components``, ``_adjacency``, ``_propagate``) applies
    unchanged.  ``LinkData.positive_end_orders_size`` is the one rank-2 method on the
    container and is replaced here by ``census_size``.
    """
    words = tuple(words)
    if not words:
        raise NeuwirthInputError("no relators")
    if generators is None:
        generators = generators_of(words)
    generators = tuple(generators)
    if len(set(generators)) != len(generators):
        raise NeuwirthInputError("duplicate generator")
    for g in generators:
        if len(g) != 1 or not g.islower() or not g.isalpha():
            raise NeuwirthInputError(f"generator {g!r} must be a single lowercase letter")
    table = _letter_germ_table(generators)
    n_germs = 2 * len(generators)

    letters: list = []
    relator_of: list = []
    starts: list = []
    for j, w in enumerate(words):
        if not w:
            raise NeuwirthInputError("empty relator")
        starts.append(len(letters))
        for c in w:
            if c not in table:
                raise NeuwirthInputError(f"letter {c!r} is not over {generators}")
            letters.append(c)
        relator_of.extend([j] * len(w))
    n = len(letters)
    n_darts = 2 * n

    B = [0] * n_darts
    for i in range(n):
        B[2 * i] = 2 * i + 1
        B[2 * i + 1] = 2 * i

    A = [-1] * n_darts
    for j, w in enumerate(words):
        base = starts[j]
        m = len(w)
        for k in range(m):
            i = base + k
            nxt = base + (k + 1) % m
            A[2 * i + 1] = 2 * nxt
            A[2 * nxt] = 2 * i + 1
    if any(a < 0 for a in A):
        raise NeuwirthInputError("corner involution incomplete")

    germ = [0] * n_darts
    for i, c in enumerate(letters):
        gd, gh = table[c]
        germ[2 * i] = gd
        germ[2 * i + 1] = gh

    buckets = [[] for _ in range(n_germs)]
    for d in range(n_darts):
        buckets[germ[d]].append(d)
    vertex_darts = tuple(tuple(b) for b in buckets)

    edge_darts: list = []
    edge_of_dart = [-1] * n_darts
    for d in range(n_darts):
        if edge_of_dart[d] >= 0:
            continue
        e = len(edge_darts)
        edge_darts.append((d, A[d]))
        edge_of_dart[d] = e
        edge_of_dart[A[d]] = e
    edge_class = tuple(tuple(sorted((germ[a], germ[b]))) for a, b in edge_darts)
    class_edges: dict = {}
    for e, key in enumerate(edge_class):
        class_edges.setdefault(key, []).append(e)
    class_edges = {k: tuple(v) for k, v in class_edges.items()}

    loop_edges = tuple(e for e, key in enumerate(edge_class) if key[0] == key[1])
    present = tuple(v for v in range(n_germs) if vertex_darts[v])

    parent = list(range(n_germs))

    def find(a: int) -> int:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for u, v in edge_class:
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
    components = len({find(v) for v in present}) if present else 0

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


def census_size(data: LinkData, generators) -> int:
    """``prod_g (n_{g+} - 1)!`` -- the size of the compatible-rotation family."""
    total = 1
    for k in range(len(generators)):
        deg = data.degree(2 * k)
        if deg:
            total *= factorial(deg - 1)
    return total


# --------------------------------------------------------------------------------------
# the simple support S and its combinatorics
# --------------------------------------------------------------------------------------


def simple_support(data: LinkData):
    """``(vertices, edges, adjacency)`` of the SIMPLE support of the link multigraph."""
    vertices = tuple(data.present_germs)
    edges = tuple(sorted(k for k in data.class_edges if k[0] != k[1]))
    adj = {v: set() for v in vertices}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    adj = {v: tuple(sorted(s)) for v, s in adj.items()}
    return vertices, edges, adj


def _connected(vertices, adj, removed=()) -> bool:
    live = [v for v in vertices if v not in removed]
    if not live:
        return False
    seen = {live[0]}
    stack = [live[0]]
    while stack:
        v = stack.pop()
        for w in adj[v]:
            if w in removed or w in seen:
                continue
            seen.add(w)
            stack.append(w)
    return len(seen) == len(live)


def is_three_connected(vertices, adj):
    """Explicit 0-, 1- and 2-cut search.  Returns ``(bool, reason_or_None)``."""
    n = len(vertices)
    if n < 4:
        return False, f"only {n} vertices; 3-connectivity needs at least 4"
    if not _connected(vertices, adj):
        return False, "simple support is disconnected"
    for v in vertices:
        if not _connected(vertices, adj, removed=(v,)):
            return False, f"cut vertex {v}"
    for i, u in enumerate(vertices):
        for v in vertices[i + 1:]:
            if not _connected(vertices, adj, removed=(u, v)):
                return False, f"2-cut {{{u}, {v}}}"
    return True, None


def _is_bipartite(vertices, adj) -> bool:
    colour = {}
    for start in vertices:
        if start in colour:
            continue
        colour[start] = 0
        stack = [start]
        while stack:
            v = stack.pop()
            for w in adj[v]:
                if w not in colour:
                    colour[w] = 1 - colour[v]
                    stack.append(w)
                elif colour[w] == colour[v]:
                    return False
    return True


def sparsity_nonplanarity_certificate(vertices, edges, adj):
    """A certified non-planarity reason from Euler's bounds, or ``None``."""
    v_count, e_count = len(vertices), len(edges)
    if v_count >= 3 and e_count > 3 * v_count - 6:
        return (f"|E| = {e_count} > 3|V| - 6 = {3 * v_count - 6} "
                "(Euler bound for simple planar graphs)")
    if v_count >= 3 and _is_bipartite(vertices, adj) and e_count > 2 * v_count - 4:
        return (f"S is bipartite with |E| = {e_count} > 2|V| - 4 = {2 * v_count - 4} "
                "(Euler bound for simple bipartite planar graphs)")
    return None


@dataclass(frozen=True)
class MacroResult:
    """The outcome of the rotation-system enumeration of the simple support."""

    status: str                       # PLANAR / NONPLANAR / UNDETERMINED
    rotations: tuple = ()             # tuple of {germ: neighbour tuple} (genus 0 only)
    genus0_count: int = 0
    enumerated: int = 0
    family_size: int = 0
    budget: int = 0
    reflections_verified: bool = False
    certificate: str | None = None


_MACRO_CACHE: dict = {}
MACRO_CACHE_LIMIT = 4096


def macro_rotations(vertices, edges, adj, budget: int = DEFAULT_MACRO_BUDGET,
                    keep: int = 4) -> MacroResult:
    """Enumerate every rotation system of the simple graph and keep the genus-0 ones.

    The graph is assumed simple and connected.  ``keep`` bounds how many genus-0
    systems are stored (four is enough to detect "more than the Whitney two"); the
    *count* is always exact because the whole family is enumerated.

    Results are memoised on ``(vertices, edges, budget)``: a harvest visits thousands of
    presentations but only a handful of distinct simple supports, and the enumeration is
    a pure function of the graph.
    """
    cache_key = (tuple(vertices), tuple(edges), budget, keep)
    hit = _MACRO_CACHE.get(cache_key)
    if hit is not None:
        return hit
    result = _macro_rotations_uncached(vertices, edges, adj, budget, keep)
    if len(_MACRO_CACHE) < MACRO_CACHE_LIMIT:
        _MACRO_CACHE[cache_key] = result
    return result


def _macro_rotations_uncached(vertices, edges, adj, budget, keep) -> MacroResult:
    v_count, e_count = len(vertices), len(edges)
    family = 1
    for v in vertices:
        family *= factorial(max(len(adj[v]) - 1, 0))
    if family > budget:
        return MacroResult(UNDETERMINED, (), 0, 0, family, budget,
                           certificate=f"family {family} exceeds macro budget {budget}")

    cert = sparsity_nonplanarity_certificate(vertices, edges, adj)
    if cert is not None:
        return MacroResult(NONPLANAR, (), 0, 0, family, budget, certificate=cert)

    # darts: edge i owns dart 2i (u -> v) and 2i + 1 (v -> u); alpha(d) = d ^ 1
    index = {e: i for i, e in enumerate(edges)}
    darts_at = {v: [] for v in vertices}
    head = [0] * (2 * e_count)
    for (u, v), i in index.items():
        darts_at[u].append(2 * i)
        darts_at[v].append(2 * i + 1)
        head[2 * i] = v
        head[2 * i + 1] = u

    order_pools = []
    order_vertices = []
    for v in vertices:
        ds = tuple(sorted(darts_at[v]))
        if not ds:
            return MacroResult(UNDETERMINED, (), 0, 0, family, budget,
                               certificate=f"germ {v} is isolated in the simple support")
        pool = [(ds[0],) + p for p in permutations(ds[1:])]
        order_pools.append(pool)
        order_vertices.append(v)

    target_faces = e_count - v_count + 2
    n_darts = 2 * e_count
    found = []
    genus0 = 0
    enumerated = 0
    nxt = [0] * n_darts
    for combo in product(*order_pools):
        enumerated += 1
        for seq in combo:
            m = len(seq)
            for k in range(m):
                nxt[seq[k]] = seq[(k + 1) % m]
        seen = bytearray(n_darts)
        faces = 0
        for start in range(n_darts):
            if seen[start]:
                continue
            faces += 1
            cur = start
            while not seen[cur]:
                seen[cur] = 1
                cur = nxt[cur ^ 1]
        if faces == target_faces:
            genus0 += 1
            if len(found) < keep:
                found.append(tuple(
                    (order_vertices[i], tuple(head[d] for d in combo[i]))
                    for i in range(len(order_vertices))
                ))
    if enumerated != family:
        raise NeuwirthInputError(
            f"macro enumeration size {enumerated} != predicted family {family}"
        )
    if genus0 == 0:
        return MacroResult(
            NONPLANAR, (), 0, enumerated, family, budget,
            certificate=(f"exhaustive enumeration of all {enumerated} rotation systems "
                         f"of S found none of genus 0 (target faces {target_faces})"),
        )
    rotations = tuple({v: nb for v, nb in rot} for rot in found)
    verified = False
    if genus0 == 2:
        verified = _are_mutual_reflections(rotations[0], rotations[1])
    return MacroResult(PLANAR, rotations, genus0, enumerated, family, budget,
                       reflections_verified=verified)


def _are_mutual_reflections(rot_a, rot_b) -> bool:
    """``rot_b`` is the vertex-wise reversal of ``rot_a`` (as cyclic orders)."""
    if set(rot_a) != set(rot_b):
        return False
    for v, seq in rot_a.items():
        other = rot_b[v]
        if len(other) != len(seq):
            return False
        rev = tuple(reversed(seq))
        m = len(rev)
        if not any(rev[i:] + rev[:i] == other for i in range(m)):
            return False
    return True


# --------------------------------------------------------------------------------------
# support classification (the fail-closed gate)
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class SupportN:
    kind: str                             # "3CONN_PLANAR" / "NONPLANAR" / "UNSUPPORTED"
    data: LinkData | None
    generators: tuple = ()
    germ_names: tuple = ()
    vertices: tuple = ()
    edges: tuple = ()
    class_keys: tuple = ()
    multiplicities: tuple = ()
    simple_degrees: tuple = ()
    three_connected: bool | None = None
    planar: bool | None = None
    macro: MacroResult | None = None
    reason: str | None = None
    diagnostics: tuple = ()

    def multiplicity_map(self) -> dict:
        return {k: m for k, m in self.multiplicities}


def classify_support_n(words, generators=None,
                       macro_budget: int = DEFAULT_MACRO_BUDGET) -> SupportN:
    """Run every hypothesis gate of R1c in order and report the outcome."""
    words = tuple(words)
    try:
        if generators is None:
            generators = generators_of(words)
        generators = tuple(generators)
        data = build_link_n(words, generators)
    except NeuwirthInputError as exc:
        return SupportN("UNSUPPORTED", None, reason=f"malformed input: {exc}")

    names = germ_names(generators)
    base = dict(data=data, generators=generators, germ_names=names)

    short = [len(w) for w in words if len(w) < MIN_RELATOR_LENGTH]
    if short:
        return SupportN("UNSUPPORTED", **base,
                        reason=f"degenerate relator of length {min(short)} "
                               f"< {MIN_RELATOR_LENGTH}")
    missing = [names[v] for v in range(2 * len(generators)) if not data.vertex_darts[v]]
    if missing:
        return SupportN("UNSUPPORTED", **base,
                        reason=f"germ(s) {missing} do not occur; the link is not connected")
    if data.has_loop:
        return SupportN("UNSUPPORTED", **base,
                        reason=f"A-link has {len(data.loop_edges)} loop edge(s)")
    if data.link_components != 1:
        return SupportN("UNSUPPORTED", **base,
                        reason=f"link has {data.link_components} components; (H1) fails")

    vertices, edges, adj = simple_support(data)
    keys = tuple(sorted(data.class_edges))
    mult = tuple((k, len(data.class_edges[k])) for k in keys)
    degrees = tuple((names[v], len(adj[v])) for v in vertices)
    base.update(vertices=vertices, edges=edges, class_keys=keys, multiplicities=mult,
                simple_degrees=degrees)

    macro = macro_rotations(vertices, edges, adj, budget=macro_budget)
    diagnostics = []
    if macro.status == NONPLANAR:
        # planarity of G_A implies planarity of its subgraph S, so a certified
        # non-planar S rules out EVERY spherical rotation system.  This does not use
        # (H2) and is therefore reported even when S is not 3-connected.
        return SupportN("NONPLANAR", **base, three_connected=None, planar=False,
                        macro=macro,
                        reason=f"S is non-planar: {macro.certificate}")
    if macro.status == UNDETERMINED:
        return SupportN("UNSUPPORTED", **base, macro=macro,
                        reason=f"planarity of S undetermined: {macro.certificate}")

    if len(vertices) < 4:
        diagnostics.append(f"only {len(vertices)} germs; four are required")
    low = [names[v] for v in vertices if len(adj[v]) < 3]
    if low:
        diagnostics.append(f"simple degree < 3 at germ(s) {low}")
    ok, why = is_three_connected(vertices, adj)
    if not ok:
        diagnostics.append(f"(H2) fails: {why}")
    if diagnostics:
        return SupportN("UNSUPPORTED", **base, three_connected=ok, planar=True,
                        macro=macro, reason="; ".join(diagnostics),
                        diagnostics=tuple(diagnostics))

    if macro.genus0_count != 2:
        raise WhitneyViolation(
            f"S is 3-connected and planar but has {macro.genus0_count} genus-0 rotation "
            f"systems, not 2 (words={words}, |V|={len(vertices)}, |E|={len(edges)})"
        )
    if not macro.reflections_verified:
        raise WhitneyViolation(
            f"the two genus-0 rotation systems of S are not mutual vertex-wise "
            f"reversals (words={words})"
        )
    return SupportN("3CONN_PLANAR", **base, three_connected=True, planar=True,
                    macro=macro)


# --------------------------------------------------------------------------------------
# slot scheme from the fixed macro reflection ([R3]: arbitrary linear cut)
# --------------------------------------------------------------------------------------


class _SlotsN(_Slots):
    """``neuwirth_rank._Slots`` with the rank-2 ``range(4)`` germ loop generalised.

    Everything else (``_local``, ``slot``, ``rank_at_slot`` -- i.e. the whole slot
    arithmetic of (4.2), including the endpoint reversal of Theorem R.3) is inherited
    verbatim.
    """

    __slots__ = ()

    def __init__(self, data: LinkData, scheme: Scheme):
        self.data = data
        self.scheme = scheme
        self.reference = scheme.reference_map()
        self.class_size = {k: len(v) for k, v in data.class_edges.items()}
        inverse = []
        for v in range(len(scheme.slots)):
            table = {}
            for key, positions in scheme.slots[v].items():
                for t, slot in enumerate(positions):
                    if slot in table:
                        raise NeuwirthInputError("slot scheme is not injective")
                    table[slot] = (key, t)
            inverse.append(table)
        self.inverse = inverse


def _verify_partition_n(data: LinkData, slots) -> bool:
    for v in data.present_germs:
        seen = []
        for key, positions in slots[v].items():
            if len(positions) != len(data.class_edges[key]):
                return False
            seen.extend(positions)
        if sorted(seen) != list(range(data.degree(v))):
            return False
    return True


def macro_scheme(support: SupportN, macro_index: int = 0) -> Scheme:
    """Blocks laid out along one macro reflection, cut at its first neighbour."""
    data = support.data
    mult = support.multiplicity_map()
    rotation = support.macro.rotations[macro_index]
    n_germs = 2 * len(support.generators)
    slots = []
    for v in range(n_germs):
        if v not in rotation:
            slots.append({})
            continue
        order = [tuple(sorted((v, w))) for w in rotation[v]]
        block, width = _blocks_to_slots(order, mult)
        if width != data.degree(v):
            raise NeuwirthInputError(
                f"block widths {width} do not fill germ {support.germ_names[v]} "
                f"(degree {data.degree(v)})"
            )
        slots.append(block)
    slots = tuple(slots)
    reference = tuple((k, min(k)) for k in support.class_keys)
    name = "macro[%d]cut(%s)" % (
        macro_index,
        ",".join(f"{support.germ_names[v]}:{support.germ_names[rotation[v][0]]}"
                 for v in sorted(rotation)),
    )
    return Scheme(name, None, slots, reference, _verify_partition_n(data, slots))


def _constraints_n(data: LinkData, n_generators: int):
    """One modular equation per ``B``-transposition, i.e. per occurrence (Lemma 4.1)."""
    out = []
    for i in range(data.n_occurrences):
        da, db = 2 * i, 2 * i + 1
        va, vb = data.germ[da], data.germ[db]
        if vb != (va ^ 1):
            raise NeuwirthInputError("germ map violates nu(Bd) = tau(nu(d))")
        generator = va // 2
        if generator >= n_generators:
            raise NeuwirthInputError("germ index outside the generator alphabet")
        modulus = data.degree(va)
        if modulus != data.degree(vb):
            raise NeuwirthInputError("n_v != n_{tau v}")
        out.append(_Constraint(da, db, data.edge_of_dart[da], data.edge_of_dart[db],
                               generator, modulus))
    return tuple(out)


# --------------------------------------------------------------------------------------
# verdict containers
# --------------------------------------------------------------------------------------


@dataclass
class CountersN:
    macro_family_size: int = 0
    macro_rotations_enumerated: int = 0
    macro_genus0_found: int = 0
    macro_reflections_used: int = 0
    phase_tuples_considered: int = 0
    phase_tuple_budget: int = 0
    component_seed_attempts: int = 0
    component_seed_budget: int = 0
    closed_component_assignments: int = 0
    within_cycle_collision_rejections: int = 0
    propagation_dead_ends: int = 0
    component_combinations_considered: int = 0
    cross_cycle_collision_rejections: int = 0
    union_cardinality_checks: int = 0
    union_cardinality_rejections: int = 0
    witness_replay_failures: int = 0
    exhaustive: bool = False

    def as_dict(self) -> dict:
        return dict(self.__dict__)


@dataclass(frozen=True)
class RankNWitness:
    scheme: str
    macro_index: int
    macro_rotation: tuple             # ((germ name, neighbour name tuple), ...)
    phases: tuple                     # ((generator, s_g), ...)
    ranks: tuple
    rotations: tuple                  # ((germ name, dart tuple), ...) -- the witness C
    rotation_by_index: tuple          # ((germ index, dart tuple), ...)
    permutation: tuple
    cycles_C: int
    cycles_A: int
    cycles_AC: int
    link_components: int
    euler_characteristic: int
    defect: int
    genus: int
    compatibility_verified: bool

    def rotation_map(self) -> dict:
        return {name: darts for name, darts in self.rotations}

    def rotation_index_map(self) -> dict:
        return {v: darts for v, darts in self.rotation_by_index}


@dataclass(frozen=True)
class RankNDecision:
    words: tuple
    generators: tuple
    verdict: str
    spherical: bool | None
    support: SupportN
    witness: RankNWitness | None
    counters: CountersN
    reason: str | None = None


# --------------------------------------------------------------------------------------
# the solver
# --------------------------------------------------------------------------------------


def solve_spherical_n(words, generators=None,
                      macro_budget: int = DEFAULT_MACRO_BUDGET,
                      macro_index: int = 0,
                      support: SupportN | None = None) -> RankNDecision:
    """Decide Neuwirth-compatible sphericity at arbitrary rank (Theorems R and P).

    ``macro_index`` selects which of the two Whitney reflections is fixed.  By
    Theorem P the verdict does not depend on it; the tests exercise both.
    """
    words = tuple(words)
    if generators is None:
        generators = generators_of(words) if support is None else support.generators
    generators = tuple(generators)
    if support is None:
        support = classify_support_n(words, generators, macro_budget=macro_budget)
    counters = CountersN()
    if support.macro is not None:
        counters.macro_family_size = support.macro.family_size
        counters.macro_rotations_enumerated = support.macro.enumerated
        counters.macro_genus0_found = support.macro.genus0_count
    if support.kind == "UNSUPPORTED":
        return RankNDecision(words, generators, UNSUPPORTED, None, support, None,
                             counters, reason=support.reason)
    if support.kind == "NONPLANAR":
        counters.exhaustive = True
        return RankNDecision(words, generators, NOT_SPHERICAL, False, support, None,
                             counters, reason=support.reason)

    data = support.data
    counters.macro_reflections_used = 1
    scheme = macro_scheme(support, macro_index)
    if not scheme.partition_verified:
        return RankNDecision(words, generators, UNSUPPORTED, None, support, None,
                             counters,
                             reason=f"scheme {scheme.name} does not partition the slots")

    constraints = _constraints_n(data, len(generators))
    n_edges = len(data.edge_darts)
    components = _components(n_edges, constraints)
    adjacency = _adjacency(n_edges, constraints)
    if sum(len(c[1]) for c in components) != len(constraints):
        raise NeuwirthInputError("constraint partition lost an equation")
    if len(components) != len(words):
        raise NeuwirthInputError(
            f"H_(A,B) has {len(components)} components but there are {len(words)} "
            "relators (Lemma 4.2)"
        )

    moduli = tuple(data.degree(2 * k) for k in range(len(generators)))
    class_size = {k: len(v) for k, v in data.class_edges.items()}
    seeds_per_phase = sum(
        class_size[data.edge_class[edges[0]]] for edges, _ in components
    )
    phase_budget = 1
    for m in moduli:
        phase_budget *= m
    counters.phase_tuple_budget = phase_budget
    counters.component_seed_budget = phase_budget * seeds_per_phase

    slots = _SlotsN(data, scheme)
    for phases in product(*(range(m) for m in moduli)):
        counters.phase_tuples_considered += 1
        per_component = []
        for edges, _cons in components:
            seed = edges[0]
            seed_class = data.edge_class[seed]
            solutions = []
            for seed_rank in range(class_size[seed_class]):
                counters.component_seed_attempts += 1
                assign = _propagate(slots, adjacency, seed, seed_rank, phases)
                if assign is None:
                    counters.propagation_dead_ends += 1
                    continue
                if len(assign) != len(edges):
                    raise NeuwirthInputError("component propagation left holes")
                counters.closed_component_assignments += 1
                used = {}
                clash = False
                for e in edges:
                    key = data.edge_class[e]
                    bucket = used.setdefault(key, set())
                    if assign[e] in bucket:
                        clash = True
                        break
                    bucket.add(assign[e])
                if clash:
                    counters.within_cycle_collision_rejections += 1
                    continue
                solutions.append((assign, {k: frozenset(v) for k, v in used.items()}))
            per_component.append(solutions)
        if any(not s for s in per_component):
            continue
        witness = _combine_n(data, slots, scheme, phases, per_component, class_size,
                             counters, support, macro_index)
        if witness is not None:
            return RankNDecision(words, generators, SPHERICAL, True, support, witness,
                                 counters)

    counters.exhaustive = True
    return RankNDecision(words, generators, NOT_SPHERICAL, False, support, None,
                         counters,
                         reason="every phase tuple, seed and cross-cycle combination "
                                "was exhausted for the fixed macro reflection")


def _combine_n(data, slots, scheme, phases, per_component, class_size, counters,
               support, macro_index):
    """Cross-cycle combination with the (4.4) union-cardinality check."""
    n = len(per_component)
    chosen = [None] * n

    def rec(k: int, used: dict):
        if k == n:
            counters.component_combinations_considered += 1
            counters.union_cardinality_checks += 1
            for key, size in class_size.items():
                if len(used.get(key, ())) != size:
                    counters.union_cardinality_rejections += 1
                    return None
            ranks = {}
            for assign, _ in chosen:
                ranks.update(assign)
            return _finalise_n(data, slots, scheme, phases, ranks, counters, support,
                               macro_index)
        for assign, marks in per_component[k]:
            merged = dict(used)
            clash = False
            for key, bucket in marks.items():
                prev = merged.get(key)
                if prev is None:
                    merged[key] = set(bucket)
                elif prev & bucket:
                    clash = True
                    break
                else:
                    merged[key] = prev | bucket
            if clash:
                counters.cross_cycle_collision_rejections += 1
                continue
            chosen[k] = (assign, marks)
            got = rec(k + 1, merged)
            if got is not None:
                return got
            chosen[k] = None
        return None

    return rec(0, {})


def _finalise_n(data, slots, scheme, phases, ranks, counters, support, macro_index):
    """Rebuild the rotation, replay (2.1) and Euler; a failure is a bug, not a NO."""
    ranks_tuple = tuple(ranks[e] for e in range(len(data.edge_darts)))
    orders = _build_rotations(data, slots, ranks_tuple)
    C = rotation_from_orders(data, orders)
    compatible = is_compatible(data, C)
    numbers = euler_data(data, C)
    if not compatible or numbers["defect"] != 0 or numbers["link_components"] != 1:
        counters.witness_replay_failures += 1
        raise WitnessReplayError(
            f"accepted rank-n solution failed replay: compatible={compatible}, "
            f"numbers={numbers}, scheme={scheme.name}, phases={phases}"
        )
    names = support.germ_names
    rotation = support.macro.rotations[macro_index]
    return RankNWitness(
        scheme=scheme.name,
        macro_index=macro_index,
        macro_rotation=tuple(
            (names[v], tuple(names[w] for w in rotation[v])) for v in sorted(rotation)
        ),
        phases=tuple((support.generators[k], s) for k, s in enumerate(phases)),
        ranks=ranks_tuple,
        rotations=tuple((names[v], orders[v]) for v in sorted(orders)),
        rotation_by_index=tuple((v, orders[v]) for v in sorted(orders)),
        permutation=C,
        cycles_C=numbers["cycles_C"],
        cycles_A=numbers["cycles_A"],
        cycles_AC=numbers["cycles_AC"],
        link_components=numbers["link_components"],
        euler_characteristic=numbers["euler_characteristic"],
        defect=numbers["defect"],
        genus=numbers["genus"],
        compatibility_verified=True,
    )


# --------------------------------------------------------------------------------------
# rank-n factorial ground truth (the fallback oracle)
# --------------------------------------------------------------------------------------


def compatible_orders_n(data: LinkData, generators):
    """Every compatible rotation system as ``{germ: dart tuple}``.

    The rank-2 ``neuwirth_core.compatible_orders`` pins the positive germs to the pair
    ``(x+, y+)``; this is the same construction over ``n`` positive germs.
    """
    B = data.B
    pos = [2 * k for k in range(len(generators)) if data.vertex_darts[2 * k]]
    pools = []
    for g in pos:
        darts = data.vertex_darts[g]
        head, tail = darts[0], darts[1:]
        pools.append([(head,) + p for p in permutations(tail)])

    def rec(k: int, acc: dict):
        if k == len(pos):
            yield dict(acc)
            return
        g = pos[k]
        for order in pools[k]:
            acc[g] = order
            acc[g ^ 1] = tuple(B[p] for p in reversed(order))
            yield from rec(k + 1, acc)
            del acc[g]
            del acc[g ^ 1]

    yield from rec(0, {})


def gamma_N_factorial_n(words, generators=None, cap_rotations: int = DEFAULT_CENSUS_CAP,
                        keep_accepting: bool = True) -> dict:
    """Exact minimum of the Neuwirth genus potential over the whole compatible family."""
    words = tuple(words)
    if generators is None:
        generators = generators_of(words)
    generators = tuple(generators)
    data = build_link_n(words, generators)
    names = germ_names(generators)
    size = census_size(data, generators)
    base = {
        "words": words,
        "generators": generators,
        "expected_cases": size,
        "cap_rotations": cap_rotations,
        "link_components": data.link_components,
        "degrees": {g: data.degree(2 * k) for k, g in enumerate(generators)},
    }
    if size > cap_rotations:
        base.update(status="UNKNOWN_SIZE", enumerated_cases=0, defect_histogram={},
                    minimum_defect=None, minimum_genus=None, accepting_orders=[])
        return base

    nA = data.n_occurrences
    nC = len(data.present_germs)
    L = data.link_components
    A = data.A
    n_darts = data.n_darts

    histogram: dict = {}
    accepting = []
    enumerated = 0
    minimum = None
    C = [0] * n_darts
    for orders in compatible_orders_n(data, generators):
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
            accepting.append({names[v]: seq for v, seq in orders.items()})

    base.update(
        status="OK",
        enumerated_cases=enumerated,
        defect_histogram=histogram,
        minimum_defect=minimum,
        minimum_genus=None if minimum is None else minimum // 2,
        accepting_orders=accepting,
    )
    return base
