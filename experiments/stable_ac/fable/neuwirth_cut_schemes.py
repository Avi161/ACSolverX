"""R1c-v2 -- synchronized planarity for NON-3-connected supports at arbitrary rank.

Implementation of ``results/stable_ac/theory/fable/R1C_V2_CUT_SCHEMES.md`` (AUDITED,
with its four normative errata E1-E4, which override the body where they touch it).

What this module decides.  For a presentation ``P = <g_1..g_n | w_1..w_r>`` whose exact
word-realized Neuwirth link ``G = G_A`` is connected and loopless and whose simple
support ``S`` is planar -- *with no connectivity hypothesis on* ``S`` -- it decides
whether some Neuwirth-compatible rotation system is spherical.  It subsumes
``neuwirth_rank`` (``K4``, ``K4-e``, ``C4``) and ``neuwirth_rank_n`` (Theorem R, the
3-connected case, recovered as Corollary 6.R).

The pipeline, section by section of the note:

* **block-first decomposition** (Sec. 5, TRAP 1).  Blocks (biconnected components) of the
  *multigraph* ``G`` are computed first; only then is each block decomposed at split
  pairs (Sec. 3).  Doing it the other way round drops the ``P_4`` shifts and produces
  false negatives -- the two recorded witnesses ``<x,y|xY,yy>`` and ``<x,y|xxx,xxy>``.
* **split-pair (P-node) composition** (Thm 3.5, (3.2)).  At a split pair ``{a,b}`` with
  ``m`` trivial and ``c`` nontrivial bridges the enumerated shape is a cyclic order of
  the distinguishable bridges times a composition of ``m`` into the resulting arcs; the
  linear order of the ``m`` central edges is *never* enumerated -- it is carried by the
  all-different ranks.  Per erratum **E2** the factor list and ``c`` are pinned to the
  canonical decomposition actually performed (only the *value* of the product is
  decomposition-independent).
* **cut vertices** (Sec. 5, Thm 5.3, (5.1)).  At a cut vertex with ``t`` blocks the merge
  patterns are the labelled **non-crossing partitions** of ``Z/N`` (Kreweras) together
  with one rotation offset per block, taken up to the free global rotation:
  ``A(d_1..d_t) = (prod d_i) (N-1)!/(N-t+1)!``.  The interval lemma is *false* for
  ``t >= 3`` (TRAP 2) and is not used; non-crossing is.
* **rank normalisation** (Lemma 7.4 + erratum **E4**).  Every class carries ``m!`` rank
  assignments, so the scheme space is ``|Sigma| = N(G)/prod m_uv!``.  The
  fractional-looking ``1/m`` of a bundle (dipole) block is realised concretely as the
  **anchor consumption** of E4: the block's rotation offset at one incident cut vertex --
  its *anchor pole* -- is pinned to zero, because rotating it is exactly a cyclic shift
  of the ranks.  Everything else is enumerated.
* **composed piecewise slot maps** (Sec. 7.2).  A scheme is materialised as one *layout*
  per germ: a linear list of tokens ``("C", class key, rank)``.  The class's positions
  are then in general a union of arcs -- split by its own P-node composition *and* by
  cut-vertex insertions -- i.e. the piecewise signed-affine slot map of Sec. 7.2.  The
  slot arithmetic itself (``_Slots``/``_SlotsN``), the per-generator phases (Lemma 4.1),
  the relator-cycle propagation (Lemma 4.2 / Thm 4.3) and the cross-cycle all-different
  combination (4.4) are **imported unchanged** from ``neuwirth_rank`` /
  ``neuwirth_rank_n``: nothing in that layer is support-specific.

Fail-closed boundary (Sec. 8.2).  ``UNSUPPORTED`` -- never ``NO`` -- for: a malformed
word, an ``A``-loop, a disconnected link, a germ that does not occur, ``2n < 4``, a
scheme space or branch budget that does not fit, an R-node whose planarity could not be
settled inside the macro budget, or a slot scheme that fails the Lemma 7.3 partition
re-check.  ``NOT_SPHERICAL`` is returned for a **certified** non-planar R-node skeleton
(Sec. 11.9: a non-planar graph always exhibits itself that way, since S- and P-nodes are
planar and Thms 3.5/5.3 are bijections) and otherwise only after the entire product
schemes x phases x seeds x cross-cycle combinations has been exhausted.  A decomposition
that stalls is an **audit contradiction** (Lemma 6.2 says it cannot happen), never an
``UNSUPPORTED``.  Every YES is replayed through ``is_compatible`` / ``euler_data`` before
it is returned, and is designed to pass the independent ``witness_check_n``.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from fractions import Fraction
from math import comb, factorial

from experiments.stable_ac.fable.neuwirth_core import (
    LinkData,
    NeuwirthInputError,
    euler_data,
    is_compatible,
    rotation_from_orders,
)
from experiments.stable_ac.fable.neuwirth_rank import (
    NOT_SPHERICAL,
    SPHERICAL,
    UNSUPPORTED,
    Scheme,
    WitnessReplayError,
    _adjacency,
    _build_rotations,
    _components,
    _propagate,
)
from experiments.stable_ac.fable.neuwirth_rank_n import (
    DEFAULT_MACRO_BUDGET,
    NONPLANAR,
    PLANAR,
    UNDETERMINED,
    WhitneyViolation,
    _SlotsN,
    _constraints_n,
    _verify_partition_n,
    build_link_n,
    census_size,
    generators_of,
    germ_names,
    is_three_connected,
    macro_rotations,
)

__all__ = [
    "SPHERICAL",
    "NOT_SPHERICAL",
    "UNSUPPORTED",
    "AuditContradiction",
    "WhitneyViolation",
    "WitnessReplayError",
    "DEFAULT_SCHEME_BUDGET",
    "DEFAULT_BRANCH_BUDGET",
    "MultiGraph",
    "multigraph_from_edges",
    "multigraph_from_link",
    "Decomposition",
    "decompose",
    "scheme_count",
    "iter_schemes",
    "iter_scheme_rotations",
    "nc_partitions",
    "nc_rotation_classes",
    "merge_pattern_count",
    "CutCounters",
    "CutWitness",
    "CutDecision",
    "classify_cut_support",
    "decomposition_profile",
    "solve_cut_schemes",
    "solve_with_scheme_indices",
]

DEFAULT_SCHEME_BUDGET = 1_000_000
DEFAULT_BRANCH_BUDGET = 50_000_000


class AuditContradiction(RuntimeError):
    """A situation the audited theorem proves cannot occur -- an implementation bug."""


# =======================================================================================
# 0.  the multigraph container
# =======================================================================================


@dataclass(frozen=True)
class MultiGraph:
    """A loopless multigraph: vertices, plus one ``(u, v)`` record per edge id."""

    vertices: tuple
    edge_ends: tuple                      # eid -> (u, v) with u < v

    @property
    def n_edges(self) -> int:
        return len(self.edge_ends)

    def class_key(self, eid: int) -> tuple:
        return self.edge_ends[eid]

    def classes(self) -> dict:
        out: dict = {}
        for eid, key in enumerate(self.edge_ends):
            out.setdefault(key, []).append(eid)
        return {k: tuple(v) for k, v in out.items()}

    def degree(self, v: int) -> int:
        return sum(1 for u, w in self.edge_ends if u == v or w == v)

    def product_of_class_factorials(self) -> int:
        total = 1
        for eids in self.classes().values():
            total *= factorial(len(eids))
        return total


def multigraph_from_edges(pairs) -> MultiGraph:
    """Build a :class:`MultiGraph` from an iterable of unordered vertex pairs."""
    ends = []
    verts = set()
    for u, v in pairs:
        if u == v:
            raise NeuwirthInputError(f"loop at {u}: R1c-v2 excludes loops (H4)")
        ends.append((min(u, v), max(u, v)))
        verts.add(u)
        verts.add(v)
    return MultiGraph(tuple(sorted(verts)), tuple(ends))


def multigraph_from_link(data: LinkData) -> MultiGraph:
    """The link multigraph ``G_A``: one edge per ``A``-orbit, keyed by its germ pair."""
    return MultiGraph(tuple(data.present_germs), tuple(data.edge_class))


# =======================================================================================
# 1.  graph primitives (blocks, components, cuts)
# =======================================================================================


def _incidence(vertices, edges):
    """``vertex -> list of (eid, other endpoint)`` for ``edges = [(eid, u, v), ...]``."""
    inc = {v: [] for v in vertices}
    for eid, u, v in edges:
        inc[u].append((eid, v))
        inc[v].append((eid, u))
    return inc


def _connected_vertices(vertices, edges, banned=()):
    """Components of the induced subgraph on ``vertices - banned``."""
    banned = set(banned)
    live = [v for v in vertices if v not in banned]
    inc = {v: [] for v in live}
    for eid, u, v in edges:
        if u in banned or v in banned:
            continue
        inc[u].append(v)
        inc[v].append(u)
    seen = set()
    comps = []
    for start in live:
        if start in seen:
            continue
        comp = [start]
        seen.add(start)
        stack = [start]
        while stack:
            x = stack.pop()
            for y in inc[x]:
                if y not in seen:
                    seen.add(y)
                    comp.append(y)
                    stack.append(y)
        comps.append(tuple(sorted(comp)))
    return tuple(comps)


def biconnected_components(vertices, edges):
    """Blocks of a loopless multigraph as tuples of edge ids (Hopcroft-Tarjan).

    Parallel edges are distinguished by their id, so a parallel class of size ``m >= 2``
    comes out as a single block, exactly as the theorem's "bundle block" requires.
    """
    inc = _incidence(vertices, edges)
    disc: dict = {}
    low: dict = {}
    stack: list = []
    comps: list = []
    timer = [0]

    def dfs(root):
        # explicit stack: (vertex, parent edge id, iterator over incidences)
        frames = [(root, None, iter(inc[root]))]
        disc[root] = low[root] = timer[0]
        timer[0] += 1
        while frames:
            u, pe, it = frames[-1]
            advanced = False
            for eid, w in it:
                if eid == pe:
                    continue
                if w not in disc:
                    stack.append(eid)
                    disc[w] = low[w] = timer[0]
                    timer[0] += 1
                    frames.append((w, eid, iter(inc[w])))
                    advanced = True
                    break
                if disc[w] < disc[u]:
                    stack.append(eid)
                    if disc[w] < low[u]:
                        low[u] = disc[w]
            if advanced:
                continue
            frames.pop()
            if frames:
                p, _ppe, _pit = frames[-1]
                if low[u] < low[p]:
                    low[p] = low[u]
                if low[u] >= disc[p]:
                    comp = []
                    while True:
                        e = stack.pop()
                        comp.append(e)
                        if e == pe:
                            break
                    comps.append(tuple(sorted(comp)))

    for v in vertices:
        if v not in disc:
            dfs(v)
    if stack:
        raise AuditContradiction("biconnected decomposition left edges on the stack")
    return tuple(comps)


def _block_vertices(edges, eids):
    ends = {}
    for eid, u, v in edges:
        ends[eid] = (u, v)
    verts = set()
    for e in eids:
        verts.update(ends[e])
    return tuple(sorted(verts))


def _find_two_cut(vertices, edges):
    """The lexicographically first 2-cut of a simple 2-connected graph, or ``None``."""
    vs = tuple(vertices)
    for i, a in enumerate(vs):
        for b in vs[i + 1:]:
            if len(_connected_vertices(vs, edges, banned=(a, b))) >= 2:
                return (a, b)
    return None


# =======================================================================================
# 2.  Kreweras layer -- labelled non-crossing partitions of a cycle  (5.1)
# =======================================================================================


def _distribute(labels, capacities):
    """Every way of assigning whole labelled parts to gaps with exact capacities."""
    if not capacities:
        if not labels:
            yield []
        return
    cap = capacities[0]
    n = len(labels)
    for r in range(n + 1):
        for sub in itertools.combinations(range(n), r):
            if sum(labels[i][1] for i in sub) != cap:
                continue
            chosen = [labels[i] for i in sub]
            picked = set(sub)
            rest = [labels[i] for i in range(n) if i not in picked]
            for tail in _distribute(rest, capacities[1:]):
                yield [chosen] + tail


def _nc_linear(positions, labels):
    """Linear non-crossing partitions of ``positions`` into the labelled ``labels``.

    ``labels`` is a list of ``(label, size)``.  Yields ``{position: label}`` dicts.
    A partition of a *cycle* is non-crossing iff its linearisation (cut anywhere) is,
    so this doubles as the cyclic generator.
    """
    if not positions:
        if not labels:
            yield {}
        return
    if not labels:
        return
    span = len(positions)
    for idx in range(len(labels)):
        label, size = labels[idx]
        if size > span:
            continue
        rest = labels[:idx] + labels[idx + 1:]
        for combo in itertools.combinations(range(1, span), size - 1):
            chosen = (0,) + combo
            gaps = []
            for a, b in zip(chosen, chosen[1:] + (span,)):
                gaps.append(positions[a + 1:b])
            caps = [len(g) for g in gaps]
            for dist in _distribute(rest, caps):
                pieces = []
                ok = True
                for gap, sub in zip(gaps, dist):
                    piece = list(_nc_linear(gap, sub))
                    if not piece:
                        ok = False
                        break
                    pieces.append(piece)
                if not ok:
                    continue
                base = {positions[c]: label for c in chosen}
                for combo_pieces in itertools.product(*pieces) if pieces else [()]:
                    out = dict(base)
                    for part in combo_pieces:
                        out.update(part)
                    yield out


def nc_partitions(n: int, sizes):
    """Every labelled non-crossing partition of ``Z/n`` with the prescribed sizes.

    Yields tuples ``labels`` of length ``n`` with ``labels[p]`` the index of the part
    holding position ``p``.  The total is Kreweras' ``n!/(n-t+1)!`` (fact **(K)**), which
    the caller re-checks.
    """
    sizes = tuple(sizes)
    if sum(sizes) != n:
        raise AuditContradiction(f"part sizes {sizes} do not sum to {n}")
    labels = [(i, d) for i, d in enumerate(sizes)]
    for assign in _nc_linear(tuple(range(n)), labels):
        yield tuple(assign[p] for p in range(n))


def _kreweras_total(n: int, t: int) -> int:
    """``n!/(n-t+1)!`` -- fact (K), the labelled non-crossing partition count."""
    return factorial(n) // factorial(n - t + 1)


def nc_rotation_classes(n: int, sizes):
    """One representative per rotation orbit of :func:`nc_partitions`.

    The global rotation of a germ's cyclic order is an arbitrary linear cut, absorbed by
    the generator phase ([R3], Sec. 7.3), so exactly the ``(n-1)!/(n-t+1)!`` orbits are
    genuine scheme parameters.
    """
    sizes = tuple(sizes)
    t = len(sizes)
    seen: dict = {}
    total = 0
    for labelling in nc_partitions(n, sizes):
        total += 1
        canon = min(labelling[i:] + labelling[:i] for i in range(n))
        if canon not in seen:
            seen[canon] = labelling
    if total != _kreweras_total(n, t):
        raise AuditContradiction(
            f"non-crossing enumeration produced {total} partitions for n={n}, "
            f"sizes={sizes}; Kreweras (K) predicts {_kreweras_total(n, t)}"
        )
    expected = factorial(n - 1) // factorial(n - t + 1)
    out = tuple(seen[k] for k in sorted(seen))
    if len(out) != expected:
        raise AuditContradiction(
            f"rotation classes {len(out)} != (n-1)!/(n-t+1)! = {expected} "
            f"(n={n}, sizes={sizes}); the rotation action was expected to be free"
        )
    return out


def merge_pattern_count(sizes) -> int:
    """``A(d_1..d_t) = (prod d_i)(N-1)!/(N-t+1)!`` -- equation (5.1)."""
    sizes = tuple(sizes)
    n = sum(sizes)
    t = len(sizes)
    prod = 1
    for d in sizes:
        prod *= d
    return prod * factorial(n - 1) // factorial(n - t + 1)


# =======================================================================================
# 3.  the decomposition: blocks first (TRAP 1), then split pairs inside each block
# =======================================================================================
#
# Tokens.  A layout entry is either
#     ("C", class key, rank)   -- the rank-``z`` member of a real parallel class, or
#     ("V", virtual id)        -- a virtual edge, deleted by the parent that created it.
# The rank is carried explicitly (never "position in the list"), so a layout may be
# cyclically re-cut -- which is exactly what Lemma 3.4 does at a bridge pole and what a
# cut-vertex rotation offset does -- without disturbing the class's rank bookkeeping.
#
# Invariant (Lemma 2.2 / Lemma 3.3).  For every class of size ``m`` the ranks occur in
# cyclic order ``0, 1, ..., m-1`` at one pole and ``m-1, ..., 0`` at the other.


def _token_real(key, rank):
    return ("C", key, rank)


def _token_virtual(vid):
    return ("V", vid)


class _Context:
    """Shared state of one decomposition: class sizes, virtual ids, R-node registry."""

    def __init__(self, graph: MultiGraph, macro_budget: int):
        self.graph = graph
        self.class_size = {k: len(v) for k, v in graph.classes().items()}
        self.macro_budget = macro_budget
        self._next_virtual = -1
        self.r_nodes: list = []
        self.p_nodes: list = []
        self.s_nodes = 0
        self.dipole_blocks = 0
        self.nonplanar_certificate = None
        self.undetermined_certificate = None
        self.macro_family_total = 0
        self.macro_enumerated_total = 0

    def new_virtual(self) -> int:
        vid = self._next_virtual
        self._next_virtual -= 1
        return vid

    def token(self, eid: int):
        """The token of a piece edge that is *not* consumed by a P-node or a dipole."""
        if eid < 0:
            return _token_virtual(eid)
        key = self.graph.class_key(eid)
        size = self.class_size[key]
        if size != 1:
            raise AuditContradiction(
                f"edge {eid} of class {key} (size {size}) reached a leaf without being "
                "stripped into a P-node; Lemma 6.2's first branch was expected to fire"
            )
        return _token_real(key, 0)


def _rotate_to_front(seq, token):
    """Cut a cyclic layout at ``token`` and drop it (Lemma 3.4: the virtual dart cut)."""
    try:
        i = seq.index(token)
    except ValueError:
        raise AuditContradiction(f"virtual token {token} missing from layout {seq}")
    rotated = seq[i:] + seq[:i]
    return rotated[1:]


class _CycleNode:
    """S-node: every vertex has degree two, the cyclic order is unique (Sec. 4.2)."""

    kind = "S"

    def __init__(self, verts, edges, ctx: _Context):
        self.verts = tuple(verts)
        self.edges = tuple(edges)
        self.ctx = ctx
        self.count = 1
        ctx.s_nodes += 1

    def effective_count(self) -> int:
        return 1

    def iter_layouts(self):
        inc = {v: [] for v in self.verts}
        for eid, u, v in self.edges:
            inc[u].append(eid)
            inc[v].append(eid)
        layout = {}
        for v in self.verts:
            if len(inc[v]) != 2:
                raise AuditContradiction(f"S-node vertex {v} has degree {len(inc[v])}")
            layout[v] = tuple(self.ctx.token(e) for e in inc[v])
        yield ("S", layout)


class _DipoleNode:
    """P-leaf / bundle block: ``m`` parallel edges between two vertices (Sec. 4.1).

    Its own scheme datum is empty; the ``1/m`` of (7.1) is realised by pinning the
    block's rotation offset at its *anchor pole* (erratum E4), which the block-cut layer
    does.
    """

    kind = "DIPOLE"

    def __init__(self, u, v, eids, ctx: _Context):
        self.u, self.v = u, v
        self.eids = tuple(eids)
        self.key = (min(u, v), max(u, v))
        self.m = len(self.eids)
        self.ctx = ctx
        self.count = 1
        if any(e < 0 for e in self.eids):
            raise AuditContradiction("a dipole block carries a virtual edge")
        if ctx.class_size[self.key] != self.m:
            raise AuditContradiction(
                f"dipole block on {self.key} holds {self.m} of "
                f"{ctx.class_size[self.key]} class members"
            )
        ctx.dipole_blocks += 1

    def effective_count(self) -> int:
        return 1

    def iter_layouts(self):
        up = tuple(_token_real(self.key, z) for z in range(self.m))
        down = tuple(_token_real(self.key, z) for z in reversed(range(self.m)))
        yield ("P0", {self.u: up, self.v: down})


class _RNode:
    """R-node: a simple 3-connected skeleton, two Whitney reflections (Sec. 4.3).

    Planarity is *certified* here and nowhere else -- the enumeration of every rotation
    system of the skeleton is ``neuwirth_rank_n.macro_rotations``, reused verbatim.
    """

    kind = "R"

    def __init__(self, verts, edges, ctx: _Context):
        self.verts = tuple(verts)
        self.edges = tuple(edges)
        self.ctx = ctx
        self.fixed_bit = False
        pairs = {}
        for eid, u, v in edges:
            key = (min(u, v), max(u, v))
            if key in pairs:
                raise AuditContradiction("R-node skeleton carries a parallel class")
            pairs[key] = eid
        self.edge_of_pair = pairs
        simple_edges = tuple(sorted(pairs))
        adj = {v: set() for v in self.verts}
        for u, v in simple_edges:
            adj[u].add(v)
            adj[v].add(u)
        adj = {v: tuple(sorted(s)) for v, s in adj.items()}
        macro = macro_rotations(self.verts, simple_edges, adj, budget=ctx.macro_budget)
        self.macro = macro
        ctx.macro_family_total += macro.family_size
        ctx.macro_enumerated_total += macro.enumerated
        if macro.status == NONPLANAR:
            self.count = 0
            ctx.nonplanar_certificate = (
                f"R-node skeleton on {self.verts} is non-planar: {macro.certificate}"
            )
            self.rotations = ()
            return
        if macro.status == UNDETERMINED:
            self.count = 0
            ctx.undetermined_certificate = (
                f"R-node skeleton on {self.verts}: {macro.certificate}"
            )
            self.rotations = ()
            return
        if macro.genus0_count != 2:
            raise WhitneyViolation(
                f"3-connected planar skeleton on {self.verts} has "
                f"{macro.genus0_count} genus-0 rotation systems, not 2"
            )
        if not macro.reflections_verified:
            raise WhitneyViolation(
                f"the two genus-0 systems of the skeleton on {self.verts} are not "
                "mutual vertex-wise reversals"
            )
        self.rotations = macro.rotations
        self.count = 2
        ctx.r_nodes.append(self)

    def effective_count(self) -> int:
        return 1 if self.fixed_bit else self.count

    def iter_layouts(self):
        indices = (0,) if self.fixed_bit else tuple(range(len(self.rotations)))
        for i in indices:
            rot = self.rotations[i]
            layout = {}
            for v in self.verts:
                layout[v] = tuple(
                    self.ctx.token(self.edge_of_pair[(min(v, w), max(v, w))])
                    for w in rot[v]
                )
            yield (f"R{i}", layout)


class _PNode:
    """Split-pair composition (Thm 3.5) with the shape parameter (3.2).

    ``m_real`` trivial bridges are the real members of the class ``P_ab``; their linear
    order ``L`` is *never* enumerated (it is the ranks).  The distinguishable items are
    the ``c`` nontrivial bridges plus, if present, the piece's inherited virtual
    ``ab``-edge.  Per erratum **E2** the factor list is pinned to this canonical
    decomposition.
    """

    kind = "P"

    def __init__(self, a, b, trivial_real, trivial_virtual, bridges, ctx: _Context):
        self.a, self.b = a, b
        self.key = (min(a, b), max(a, b))
        self.trivial_real = tuple(trivial_real)
        self.trivial_virtual = tuple(trivial_virtual)
        self.bridges = tuple(bridges)          # (node, virtual id)
        self.ctx = ctx
        self.m_real = len(self.trivial_real)
        self.c = len(self.bridges)
        # distinguishable items: bridges first, then the inherited virtual ab-edge
        self.items = tuple(
            [("B", i) for i in range(self.c)] + [("T", e) for e in self.trivial_virtual]
        )
        self.c_prime = len(self.items)
        if self.c_prime == 0:
            raise AuditContradiction(
                f"split pair {{{a},{b}}} has no distinguishable bridge (Lemma 6.2)"
            )
        if self.m_real and ctx.class_size[self.key] != self.m_real:
            raise AuditContradiction(
                f"P-node on {self.key} consumed {self.m_real} of "
                f"{ctx.class_size[self.key]} class members"
            )
        self.k = self.m_real + self.c_prime
        self.shape = (factorial(self.c_prime - 1)
                      * comb(self.m_real + self.c_prime - 1, self.c_prime - 1))
        if self.shape * factorial(self.m_real) != factorial(self.k - 1):
            raise AuditContradiction("P-node shape count contradicts (k-1)!/m!")
        self.count = self.shape
        for node, _vid in self.bridges:
            self.count *= node.count
        ctx.p_nodes.append(self)

    def effective_count(self) -> int:
        out = self.shape
        for node, _vid in self.bridges:
            out *= node.effective_count()
        return out

    def _compositions(self):
        """Compositions ``m_real = i_1 + ... + i_{c'}`` with ``i_j >= 0``."""
        parts = self.c_prime
        m = self.m_real
        if parts == 1:
            yield (m,)
            return
        for cuts in itertools.combinations(range(m + parts - 1), parts - 1):
            prev = -1
            out = []
            for cpos in cuts:
                out.append(cpos - prev - 1)
                prev = cpos
            out.append(m + parts - 2 - prev)
            yield tuple(out)

    def iter_layouts(self):
        a, b = self.a, self.b
        origin = self.items[0]
        others = self.items[1:]
        bridge_pools = [list(node.iter_layouts()) for node, _vid in self.bridges]
        for perm in itertools.permutations(others):
            order = (origin,) + perm
            for comp in self._compositions():
                for choice in itertools.product(*bridge_pools) if bridge_pools else [()]:
                    layout: dict = {}
                    seg_a, seg_b = {}, {}
                    for item in order:
                        if item[0] == "T":
                            seg_a[item] = (_token_virtual(item[1]),)
                            seg_b[item] = (_token_virtual(item[1]),)
                        else:
                            idx = item[1]
                            _label, sub = choice[idx]
                            vid = self.bridges[idx][1]
                            vtok = _token_virtual(vid)
                            seg_a[item] = _rotate_to_front(sub[a], vtok)
                            seg_b[item] = _rotate_to_front(sub[b], vtok)
                            for v, seq in sub.items():
                                if v in (a, b):
                                    continue
                                if v in layout:
                                    raise AuditContradiction(
                                        f"vertex {v} appears in two bridges"
                                    )
                                layout[v] = seq
                    # ranks 0..m-1 laid consecutively along the arcs at a
                    arcs = []
                    base = 0
                    for width in comp:
                        arcs.append(tuple(range(base, base + width)))
                        base += width
                    at_a: list = []
                    for j, item in enumerate(order):
                        at_a.extend(seg_a[item])
                        at_a.extend(_token_real(self.key, z) for z in arcs[j])
                    # at b: reversed bridge order, each arc internally reversed
                    at_b: list = list(seg_b[order[0]])
                    for j in range(self.c_prime - 1, 0, -1):
                        at_b.extend(_token_real(self.key, z) for z in reversed(arcs[j]))
                        at_b.extend(seg_b[order[j]])
                    at_b.extend(_token_real(self.key, z) for z in reversed(arcs[0]))
                    layout[a] = tuple(at_a)
                    layout[b] = tuple(at_b)
                    label = "P(%d,%d)[%s|%s|%s]" % (
                        a, b,
                        ",".join(f"{i[0]}{i[1]}" for i in order),
                        ",".join(str(x) for x in comp),
                        ",".join(lab for lab, _ in choice),
                    )
                    yield (label, layout)


def _piece_adjacency(verts, edges):
    adj = {v: set() for v in verts}
    for _eid, u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return {v: tuple(sorted(s)) for v, s in adj.items()}


def _split_piece(verts, edges, a, b, ctx: _Context):
    """Decompose a 2-connected piece at the split pair ``{a, b}`` (Definition 3.1)."""
    pair = (min(a, b), max(a, b))
    trivial = [e for e in edges if (min(e[1], e[2]), max(e[1], e[2])) == pair]
    others = [e for e in edges if (min(e[1], e[2]), max(e[1], e[2])) != pair]
    trivial_real = tuple(sorted(e[0] for e in trivial if e[0] >= 0))
    trivial_virtual = tuple(sorted((e[0] for e in trivial if e[0] < 0), reverse=True))
    comps = _connected_vertices(verts, others, banned=(a, b))
    bridges = []
    for comp in comps:
        cset = set(comp)
        bedges = [e for e in others if e[1] in cset or e[2] in cset]
        vid = ctx.new_virtual()
        bverts = tuple(sorted(cset | {a, b}))
        node = _build_piece(bverts, tuple(bedges) + ((vid, a, b),), ctx)
        bridges.append((node, vid))
    return _PNode(a, b, trivial_real, trivial_virtual, bridges, ctx)


def _build_piece(verts, edges, ctx: _Context):
    """The recursion of Sec. 6: dipole / cycle / parallel class / R-node / 2-cut."""
    verts = tuple(sorted(verts))
    edges = tuple(edges)
    if len(verts) < 2:
        raise AuditContradiction(f"piece with {len(verts)} vertices")
    if len(verts) == 2:
        u, v = verts
        return _DipoleNode(u, v, [e[0] for e in edges], ctx)
    deg = {v: 0 for v in verts}
    for _eid, u, v in edges:
        deg[u] += 1
        deg[v] += 1
    if all(d == 2 for d in deg.values()):
        return _CycleNode(verts, edges, ctx)
    buckets: dict = {}
    for eid, u, v in edges:
        buckets.setdefault((min(u, v), max(u, v)), []).append(eid)
    parallel = sorted(k for k, es in buckets.items() if len(es) >= 2)
    if parallel:
        a, b = parallel[0]
        return _split_piece(verts, edges, a, b, ctx)
    adj = _piece_adjacency(verts, edges)
    ok, _why = is_three_connected(verts, adj)
    if ok:
        return _RNode(verts, edges, ctx)
    cut = _find_two_cut(verts, edges)
    if cut is None:
        raise AuditContradiction(
            f"piece on {verts} with {len(edges)} edges is neither a dipole, a cycle, "
            "nor 3-connected simple, and has no 2-cut -- Lemma 6.2 forbids this"
        )
    return _split_piece(verts, edges, cut[0], cut[1], ctx)


# =======================================================================================
# 4.  block-cut assembly (Theorem 5.3) and the scheme space
# =======================================================================================


@dataclass
class CutVertexPlan:
    """The enumerated datum at one cut vertex: (5.1) merge patterns."""

    vertex: int
    block_indices: tuple
    sizes: tuple
    total: int
    partitions: tuple                    # rotation classes of labelled NC partitions
    pinned: tuple                        # per block: offset pinned to 0 (erratum E4)

    def offset_domains(self):
        return tuple(1 if p else d for d, p in zip(self.sizes, self.pinned))

    def factor(self) -> int:
        out = len(self.partitions)
        for d in self.offset_domains():
            out *= d
        return out

    def unpinned_factor(self) -> int:
        return merge_pattern_count(self.sizes)


@dataclass
class Decomposition:
    graph: MultiGraph
    status: str
    reason: str | None
    ctx: _Context | None = None
    block_nodes: tuple = ()
    block_edges: tuple = ()
    block_vertices: tuple = ()
    cut_plans: tuple = ()
    blocks_at: dict = field(default_factory=dict)
    scheme_space: int = 0
    unquotiented_scheme_space: int = 0
    reflection_quotient: bool = False

    def summary(self) -> dict:
        ctx = self.ctx
        return {
            "status": self.status,
            "reason": self.reason,
            "blocks": len(self.block_nodes),
            "cut_vertices": len(self.cut_plans),
            "max_blocks_at_a_cut_vertex": max(
                (len(p.block_indices) for p in self.cut_plans), default=0),
            "r_nodes": len(ctx.r_nodes) if ctx else 0,
            "p_nodes": len(ctx.p_nodes) if ctx else 0,
            "s_nodes": ctx.s_nodes if ctx else 0,
            "dipole_blocks": ctx.dipole_blocks if ctx else 0,
            "scheme_space": self.scheme_space,
            "unquotiented_scheme_space": self.unquotiented_scheme_space,
            "reflection_quotient": self.reflection_quotient,
        }


def decompose(graph: MultiGraph, macro_budget: int = DEFAULT_MACRO_BUDGET,
              quotient: bool = True) -> Decomposition:
    """Block-first decomposition of a connected loopless multigraph (TRAP 1)."""
    edges = tuple((eid, u, v) for eid, (u, v) in enumerate(graph.edge_ends))
    if len(_connected_vertices(graph.vertices, edges)) != 1:
        return Decomposition(graph, "UNSUPPORTED", "the multigraph is disconnected (H1)")
    ctx = _Context(graph, macro_budget)
    blocks = biconnected_components(graph.vertices, edges)
    if not blocks:
        return Decomposition(graph, "UNSUPPORTED", "no edges")
    by_id = {eid: (u, v) for eid, u, v in edges}
    block_vertices = tuple(_block_vertices(edges, b) for b in blocks)
    blocks_at: dict = {}
    for i, verts in enumerate(block_vertices):
        for v in verts:
            blocks_at.setdefault(v, []).append(i)
    blocks_at = {v: tuple(bs) for v, bs in blocks_at.items()}

    nodes = []
    for eids, verts in zip(blocks, block_vertices):
        piece = tuple((e, by_id[e][0], by_id[e][1]) for e in eids)
        nodes.append(_build_piece(verts, piece, ctx))
    if ctx.nonplanar_certificate is not None:
        return Decomposition(graph, NONPLANAR, ctx.nonplanar_certificate, ctx)
    if ctx.undetermined_certificate is not None:
        return Decomposition(graph, "UNSUPPORTED", ctx.undetermined_certificate, ctx)

    if quotient and ctx.r_nodes:
        ctx.r_nodes[0].fixed_bit = True

    # erratum E4: each bundle (dipole) block consumes exactly one rotation-offset factor
    # at its anchor pole, which is where its class's linear order is anchored.
    anchor: dict = {}
    for i, node in enumerate(nodes):
        if not isinstance(node, _DipoleNode) or node.m < 2:
            continue
        poles = [p for p in (node.u, node.v) if len(blocks_at[p]) >= 2]
        if not poles:
            return Decomposition(
                graph, "UNSUPPORTED",
                f"bundle block {node.key} has no cut-vertex pole; G is a single dipole "
                "and Lemma 7.4's rank normalisation degenerates (Sec. 8.2, n = 1)",
                ctx)
        anchor[i] = min(poles)

    cut_plans = []
    for v in sorted(blocks_at):
        bs = blocks_at[v]
        if len(bs) < 2:
            continue
        sizes = []
        for i in bs:
            eids = blocks[i]
            sizes.append(sum(1 for e in eids if v in by_id[e]))
        sizes = tuple(sizes)
        total = sum(sizes)
        if total != graph.degree(v):
            raise AuditContradiction(
                f"block degrees {sizes} at cut vertex {v} do not sum to "
                f"{graph.degree(v)}"
            )
        parts = nc_rotation_classes(total, sizes)
        pinned = tuple(anchor.get(i) == v for i in bs)
        cut_plans.append(CutVertexPlan(v, bs, sizes, total, parts, pinned))

    space = Fraction(1)
    raw = Fraction(1)
    for node in nodes:
        space *= node.effective_count()
        raw *= node.count
    for plan in cut_plans:
        space *= plan.factor()
        raw *= plan.unpinned_factor()
    # sanity: the unpinned product is N(G) / prod (m! of non-bundle classes) ...
    if space.denominator != 1:
        raise AuditContradiction(f"scheme space {space} is not an integer (Lemma 7.4)")
    decomp = Decomposition(
        graph, "OK", None, ctx,
        tuple(nodes), tuple(blocks), block_vertices, tuple(cut_plans), blocks_at,
        int(space), int(space) * (2 if (quotient and ctx.r_nodes) else 1),
        bool(quotient and ctx.r_nodes),
    )
    return decomp


def scheme_count(graph: MultiGraph, macro_budget: int = DEFAULT_MACRO_BUDGET,
                 quotient: bool = False):
    """``|Sigma| = N(G) / prod m_uv!`` -- (7.1).  ``None`` if the graph is out of scope."""
    decomp = decompose(graph, macro_budget=macro_budget, quotient=quotient)
    if decomp.status == NONPLANAR:
        return 0
    if decomp.status != "OK":
        return None
    return decomp.scheme_space


# =======================================================================================
# 5.  materialising a scheme: layouts, and (for audit) rotation systems
# =======================================================================================


def _iter_choices(pools, k=0, acc=None):
    """Lazy cartesian product over generators that can be restarted."""
    if acc is None:
        acc = []
    if k == len(pools):
        yield tuple(acc)
        return
    for item in pools[k]():
        acc.append(item)
        yield from _iter_choices(pools, k + 1, acc)
        acc.pop()


def _merge_at_cut(plan: CutVertexPlan, block_layouts):
    """Every merge pattern at one cut vertex: (NC partition class, offsets) -> layout.

    ``block_layouts[i]`` is block ``plan.block_indices[i]``'s linear token list at the
    cut vertex.  Offsets rotate a block's *cyclic* sequence onto its part positions; the
    tokens carry their own ranks, so an offset never disturbs a class's bookkeeping --
    except for a bundle block, where it *is* the class's cyclic shift, which is why the
    anchor pole's offset is pinned (erratum E4).
    """
    total = plan.total
    domains = plan.offset_domains()
    for labelling in plan.partitions:
        parts = [[] for _ in plan.sizes]
        for p, lab in enumerate(labelling):
            parts[lab].append(p)
        for offsets in itertools.product(*(range(d) for d in domains)):
            slot = [None] * total
            for i, positions in enumerate(parts):
                seq = block_layouts[i]
                d = len(positions)
                if d != len(seq):
                    raise AuditContradiction(
                        f"cut vertex {plan.vertex}: part size {d} != block sequence "
                        f"length {len(seq)}"
                    )
                for j, token in enumerate(seq):
                    slot[positions[(j + offsets[i]) % d]] = token
            if any(s is None for s in slot):
                raise AuditContradiction("merge pattern left a hole")
            yield (labelling, offsets), tuple(slot)


def iter_schemes(decomp: Decomposition):
    """Every scheme of ``Sigma`` as ``(label, {vertex: token tuple})``.

    The number of items is exactly :attr:`Decomposition.scheme_space`, which the callers
    re-check; each item is a complete set of germ layouts with every virtual token
    already consumed.
    """
    if decomp.status != "OK":
        raise NeuwirthInputError(f"decomposition status {decomp.status}: {decomp.reason}")
    nodes = decomp.block_nodes
    plans = decomp.cut_plans
    block_pools = [(lambda n=n: n.iter_layouts()) for n in nodes]
    for block_choice in _iter_choices(block_pools):
        block_layouts = [lay for _lab, lay in block_choice]
        cut_pools = []
        for plan in plans:
            seqs = tuple(block_layouts[i][plan.vertex] for i in plan.block_indices)
            cut_pools.append((lambda p=plan, s=seqs: _merge_at_cut(p, s)))
        for merge_choice in _iter_choices(cut_pools):
            layout: dict = {}
            for i, lay in enumerate(block_layouts):
                for v, seq in lay.items():
                    if len(decomp.blocks_at[v]) == 1:
                        layout[v] = seq
            for plan, (_param, seq) in zip(plans, merge_choice):
                layout[plan.vertex] = seq
            label = "|".join(
                [",".join(lab for lab, _ in block_choice)]
                + [f"@{p.vertex}:{param[0]}/{param[1]}"
                   for p, (param, _s) in zip(plans, merge_choice)]
            )
            yield label, layout


def _rank_assignments(classes):
    """Every all-different assignment ``(class key, rank) -> edge id`` (the ``m!``)."""
    keys = sorted(classes)
    pools = [list(itertools.permutations(classes[k])) for k in keys]
    for combo in itertools.product(*pools):
        out = {}
        for key, perm in zip(keys, combo):
            for z, eid in enumerate(perm):
                out[(key, z)] = eid
        yield out


def iter_scheme_rotations(decomp: Decomposition):
    """``(scheme, ranks) -> rotation system`` of Lemma 7.4, as ``{vertex: edge tuple}``.

    This materialises the claimed bijection so a test can compare it, as a *set*, with a
    brute-force enumeration of the spherical rotation systems.
    """
    classes = decomp.graph.classes()
    for label, layout in iter_schemes(decomp):
        for assign in _rank_assignments(classes):
            rot = {}
            for v, seq in layout.items():
                out = []
                for token in seq:
                    if token[0] != "C":
                        raise AuditContradiction(f"unconsumed virtual token {token}")
                    out.append(assign[(token[1], token[2])])
                rot[v] = tuple(out)
            yield label, rot


# =======================================================================================
# 6.  the decision procedure (Theorem 7.5)
# =======================================================================================


IN_SCOPE = "IN_SCOPE"


@dataclass(frozen=True)
class CutSupport:
    """The outcome of the fail-closed gate of Sec. 8.1/8.2."""

    kind: str                              # IN_SCOPE / NONPLANAR / UNSUPPORTED
    data: LinkData | None = None
    generators: tuple = ()
    germ_names: tuple = ()
    graph: MultiGraph | None = None
    decomposition: Decomposition | None = None
    multiplicities: tuple = ()
    simple_degrees: tuple = ()
    reason: str | None = None

    def multiplicity_map(self) -> dict:
        return {k: m for k, m in self.multiplicities}


@dataclass
class CutCounters:
    blocks: int = 0
    cut_vertices: int = 0
    max_blocks_at_cut_vertex: int = 0
    r_nodes: int = 0
    p_nodes: int = 0
    s_nodes: int = 0
    dipole_blocks: int = 0
    macro_family_total: int = 0
    macro_rotations_enumerated: int = 0
    reflection_quotient: bool = False
    scheme_space: int = 0
    scheme_budget: int = 0
    schemes_considered: int = 0
    phase_tuples_considered: int = 0
    phase_tuple_budget: int = 0
    branch_budget: int = 0
    top_level_branches: int = 0
    component_seed_attempts: int = 0
    component_seed_budget: int = 0
    closed_component_assignments: int = 0
    within_cycle_collision_rejections: int = 0
    propagation_dead_ends: int = 0
    component_combinations_considered: int = 0
    cross_cycle_collision_rejections: int = 0
    union_cardinality_checks: int = 0
    union_cardinality_rejections: int = 0
    partition_recheck_failures: int = 0
    witness_replay_failures: int = 0
    exhaustive: bool = False

    def as_dict(self) -> dict:
        return dict(self.__dict__)


@dataclass(frozen=True)
class CutWitness:
    scheme: str
    phases: tuple
    ranks: tuple
    rotations: tuple                       # ((germ name, dart tuple), ...)
    rotation_by_index: tuple
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
class CutDecision:
    words: tuple
    generators: tuple
    verdict: str
    spherical: bool | None
    support: CutSupport
    witness: CutWitness | None
    counters: CutCounters
    reason: str | None = None


def classify_cut_support(words, generators=None,
                         macro_budget: int = DEFAULT_MACRO_BUDGET,
                         quotient: bool = True) -> CutSupport:
    """Run the R1c-v2 hypotheses (H1)-(H5) and the decomposition, in order."""
    words = tuple(words)
    try:
        if generators is None:
            generators = generators_of(words)
        generators = tuple(generators)
        data = build_link_n(words, generators)
    except NeuwirthInputError as exc:
        return CutSupport(UNSUPPORTED, reason=f"malformed input: {exc}")

    names = germ_names(generators)
    base = dict(data=data, generators=generators, germ_names=names)

    if 2 * len(generators) < 4:
        return CutSupport(UNSUPPORTED, **base,
                          reason=f"2n = {2 * len(generators)} < 4; (H5) fails "
                                 "(a single dipole, Sec. 8.2)")
    missing = [names[v] for v in range(2 * len(generators)) if not data.vertex_darts[v]]
    if missing:
        return CutSupport(UNSUPPORTED, **base,
                          reason=f"germ(s) {missing} do not occur; the link is not "
                                 "connected (H1)")
    if data.has_loop:
        return CutSupport(UNSUPPORTED, **base,
                          reason=f"A-link has {len(data.loop_edges)} loop edge(s); "
                                 "(H4) fails and every lemma of Sec. 3/5 assumes "
                                 "nu(d) != nu(A d) (Sec. 8.2)")
    if data.link_components != 1:
        return CutSupport(UNSUPPORTED, **base,
                          reason=f"link has {data.link_components} components; (H1) "
                                 "fails (Sec. 8.2)")

    graph = multigraph_from_link(data)
    keys = tuple(sorted(data.class_edges))
    mult = tuple((k, len(data.class_edges[k])) for k in keys)
    simple_deg: dict = {v: 0 for v in data.present_germs}
    for u, v in keys:
        simple_deg[u] += 1
        simple_deg[v] += 1
    degrees = tuple((names[v], simple_deg[v]) for v in sorted(simple_deg))
    base.update(graph=graph, multiplicities=mult, simple_degrees=degrees)

    try:
        decomp = decompose(graph, macro_budget=macro_budget, quotient=quotient)
    except WhitneyViolation:
        raise
    except NeuwirthInputError as exc:
        return CutSupport(UNSUPPORTED, **base, reason=f"decomposition failed: {exc}")
    if decomp.status == NONPLANAR:
        return CutSupport(NONPLANAR, **base, decomposition=decomp,
                          reason=f"S is non-planar: {decomp.reason}")
    if decomp.status != "OK":
        return CutSupport(UNSUPPORTED, **base, decomposition=decomp,
                          reason=decomp.reason)
    return CutSupport(IN_SCOPE, **base, decomposition=decomp)


def _scheme_from_layout(data: LinkData, n_germs: int, label: str, layout: dict,
                        class_size: dict, reference: dict) -> Scheme:
    """Turn one layout into the ``Scheme`` the imported slot arithmetic consumes.

    ``layout[v][p]`` is the token at slot ``p``; ``slots[v][key][t]`` must be the slot of
    the class member with *local* index ``t``, where local = rank at the reference pole
    and ``m - 1 - rank`` at the other (``_Slots._local``).  That is exactly Lemma 2.2's
    reversal, so the two poles' entries are mirror images of one another.
    """
    slots: list = []
    for v in range(n_germs):
        seq = layout.get(v)
        if seq is None:
            slots.append({})
            continue
        by_rank: dict = {}
        for p, token in enumerate(seq):
            if token[0] != "C":
                raise AuditContradiction(f"unconsumed virtual token {token} at germ {v}")
            bucket = by_rank.setdefault(token[1], {})
            if token[2] in bucket:
                raise AuditContradiction(f"rank {token[2]} of {token[1]} placed twice")
            bucket[token[2]] = p
        table: dict = {}
        for key, mapping in by_rank.items():
            m = class_size[key]
            if sorted(mapping) != list(range(m)):
                raise AuditContradiction(
                    f"class {key} at germ {v} carries ranks {sorted(mapping)}, not "
                    f"0..{m - 1}"
                )
            positions = tuple(mapping[z] for z in range(m))
            if reference[key] == v:
                table[key] = positions
            else:
                table[key] = tuple(positions[m - 1 - t] for t in range(m))
        slots.append(table)
    slots = tuple(slots)
    return Scheme(label, None, slots, tuple(sorted(reference.items())),
                  _verify_partition_n(data, slots))


def solve_cut_schemes(words, generators=None,
                      macro_budget: int = DEFAULT_MACRO_BUDGET,
                      scheme_budget: int = DEFAULT_SCHEME_BUDGET,
                      branch_budget: int = DEFAULT_BRANCH_BUDGET,
                      quotient: bool = True,
                      support: CutSupport | None = None) -> CutDecision:
    """Decide Neuwirth-compatible sphericity by the R1c-v2 cut-scheme enumeration."""
    words = tuple(words)
    if generators is None:
        generators = generators_of(words) if support is None else support.generators
    generators = tuple(generators)
    if support is None:
        support = classify_cut_support(words, generators, macro_budget=macro_budget,
                                       quotient=quotient)
    counters = CutCounters(scheme_budget=scheme_budget, branch_budget=branch_budget)
    decomp = support.decomposition
    if decomp is not None and decomp.ctx is not None:
        s = decomp.summary()
        counters.blocks = s["blocks"]
        counters.cut_vertices = s["cut_vertices"]
        counters.max_blocks_at_cut_vertex = s["max_blocks_at_a_cut_vertex"]
        counters.r_nodes = s["r_nodes"]
        counters.p_nodes = s["p_nodes"]
        counters.s_nodes = s["s_nodes"]
        counters.dipole_blocks = s["dipole_blocks"]
        counters.reflection_quotient = s["reflection_quotient"]
        counters.scheme_space = s["scheme_space"]
        counters.macro_family_total = decomp.ctx.macro_family_total
        counters.macro_rotations_enumerated = decomp.ctx.macro_enumerated_total

    if support.kind == UNSUPPORTED:
        return CutDecision(words, generators, UNSUPPORTED, None, support, None,
                           counters, reason=support.reason)
    if support.kind == NONPLANAR:
        counters.exhaustive = True
        return CutDecision(words, generators, NOT_SPHERICAL, False, support, None,
                           counters, reason=support.reason)

    data = support.data
    n_germs = 2 * len(generators)
    class_size = {k: len(v) for k, v in data.class_edges.items()}
    reference = {k: min(k) for k in class_size}

    if decomp.scheme_space > scheme_budget:
        return CutDecision(words, generators, UNSUPPORTED, None, support, None, counters,
                           reason=f"scheme space |Sigma| = {decomp.scheme_space} exceeds "
                                  f"the budget {scheme_budget}")
    moduli = tuple(data.degree(2 * k) for k in range(len(generators)))
    phase_budget = 1
    for m in moduli:
        phase_budget *= m
    counters.phase_tuple_budget = phase_budget
    counters.top_level_branches = decomp.scheme_space * phase_budget
    if counters.top_level_branches > branch_budget:
        return CutDecision(words, generators, UNSUPPORTED, None, support, None, counters,
                           reason=f"|Sigma| x phases = {counters.top_level_branches} "
                                  f"exceeds the branch budget {branch_budget}")

    constraints = _constraints_n(data, len(generators))
    n_edges = len(data.edge_darts)
    components = _components(n_edges, constraints)
    adjacency = _adjacency(n_edges, constraints)
    if sum(len(c[1]) for c in components) != len(constraints):
        raise AuditContradiction("constraint partition lost an equation")
    if len(components) != len(words):
        raise AuditContradiction(
            f"H_(A,B) has {len(components)} components but there are {len(words)} "
            "relators (Lemma 4.2)"
        )
    seeds_per_phase = sum(
        class_size[data.edge_class[edges[0]]] for edges, _ in components
    )
    counters.component_seed_budget = (
        decomp.scheme_space * phase_budget * seeds_per_phase)

    for label, layout in iter_schemes(decomp):
        counters.schemes_considered += 1
        scheme = _scheme_from_layout(data, n_germs, label, layout, class_size, reference)
        if not scheme.partition_verified:
            counters.partition_recheck_failures += 1
            return CutDecision(words, generators, UNSUPPORTED, None, support, None,
                               counters,
                               reason=f"scheme {label} fails the Lemma 7.3 partition "
                                      "re-check")
        slots = _SlotsN(data, scheme)
        for phases in itertools.product(*(range(m) for m in moduli)):
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
                        raise AuditContradiction("component propagation left holes")
                    counters.closed_component_assignments += 1
                    used: dict = {}
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
                    solutions.append(
                        (assign, {k: frozenset(v) for k, v in used.items()}))
                per_component.append(solutions)
            if any(not s for s in per_component):
                continue
            witness = _combine(data, slots, scheme, phases, per_component, class_size,
                               counters, support)
            if witness is not None:
                return CutDecision(words, generators, SPHERICAL, True, support, witness,
                                   counters)

    if counters.schemes_considered != decomp.scheme_space:
        raise AuditContradiction(
            f"enumerated {counters.schemes_considered} schemes but |Sigma| = "
            f"{decomp.scheme_space} (Lemma 7.4)"
        )
    counters.exhaustive = True
    return CutDecision(words, generators, NOT_SPHERICAL, False, support, None, counters,
                       reason="every scheme, phase tuple, seed and cross-cycle "
                              "combination of (7.3) was exhausted")


def _combine(data, slots, scheme, phases, per_component, class_size, counters, support):
    """Cross-cycle combination under the global all-different and (4.4)."""
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
            ranks: dict = {}
            for assign, _ in chosen:
                ranks.update(assign)
            return _finalise(data, slots, scheme, phases, ranks, counters, support)
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


def _finalise(data, slots, scheme, phases, ranks, counters, support):
    """Rebuild the rotation, replay (2.1) and Euler; a failure is a bug, not a NO."""
    ranks_tuple = tuple(ranks[e] for e in range(len(data.edge_darts)))
    orders = _build_rotations(data, slots, ranks_tuple)
    C = rotation_from_orders(data, orders)
    compatible = is_compatible(data, C)
    numbers = euler_data(data, C)
    if not compatible or numbers["defect"] != 0 or numbers["link_components"] != 1:
        counters.witness_replay_failures += 1
        raise WitnessReplayError(
            f"accepted R1c-v2 solution failed replay: compatible={compatible}, "
            f"numbers={numbers}, scheme={scheme.name}, phases={phases}"
        )
    names = support.germ_names
    return CutWitness(
        scheme=scheme.name,
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


# =======================================================================================
# 7.  structural profile (audit / test surface)
# =======================================================================================


def _node_profile(node, depth: int, acc: dict) -> None:
    kind = node.kind
    acc["nodes"][kind] = acc["nodes"].get(kind, 0) + 1
    if kind == "P":
        acc["p_node_depth"] = max(acc["p_node_depth"], depth + 1)
        acc["p_node_shapes"].append((node.m_real, node.c, node.c_prime, node.k))
        for child, _vid in node.bridges:
            _node_profile(child, depth + 1, acc)


def decomposition_profile(decomp: Decomposition) -> dict:
    """Structural profile of a decomposition (nesting depth, cut-vertex arities, ...)."""
    acc = {"nodes": {}, "p_node_depth": 0, "p_node_shapes": []}
    for node in decomp.block_nodes:
        _node_profile(node, 0, acc)
    arities = tuple(len(p.block_indices) for p in decomp.cut_plans)
    acc["cut_vertex_arities"] = arities
    acc["max_cut_vertex_arity"] = max(arities, default=0)
    acc["blocks"] = len(decomp.block_nodes)
    acc["scheme_space"] = decomp.scheme_space
    acc["p_node_shapes"] = tuple(acc["p_node_shapes"])
    return acc


def solve_with_scheme_indices(words, support: CutSupport, indices,
                              generators=None) -> str:
    """AUDIT KNOB: run the phase/rank layer for a *subfamily* of ``Sigma`` only.

    A ``NOT_SPHERICAL`` produced here is a statement about the listed schemes only, never
    about the presentation.  It exists so a test can read off *which* schemes carry a
    solution -- e.g. the ``P_4`` shift set of Theorem 6.S case 2, which is exactly what
    the two recorded false-negative witnesses of TRAP 1 turn on.
    """
    if support.kind != IN_SCOPE:
        return UNSUPPORTED
    words = tuple(words)
    generators = tuple(generators or support.generators)
    data = support.data
    decomp = support.decomposition
    wanted = set(indices)
    n_germs = 2 * len(generators)
    class_size = {k: len(v) for k, v in data.class_edges.items()}
    reference = {k: min(k) for k in class_size}
    constraints = _constraints_n(data, len(generators))
    n_edges = len(data.edge_darts)
    components = _components(n_edges, constraints)
    adjacency = _adjacency(n_edges, constraints)
    moduli = tuple(data.degree(2 * k) for k in range(len(generators)))
    counters = CutCounters()
    for index, (label, layout) in enumerate(iter_schemes(decomp)):
        if index not in wanted:
            continue
        scheme = _scheme_from_layout(data, n_germs, label, layout, class_size, reference)
        if not scheme.partition_verified:
            return UNSUPPORTED
        slots = _SlotsN(data, scheme)
        for phases in itertools.product(*(range(m) for m in moduli)):
            per_component = []
            for edges, _cons in components:
                seed = edges[0]
                seed_class = data.edge_class[seed]
                solutions = []
                for seed_rank in range(class_size[seed_class]):
                    assign = _propagate(slots, adjacency, seed, seed_rank, phases)
                    if assign is None:
                        continue
                    used: dict = {}
                    clash = False
                    for e in edges:
                        key = data.edge_class[e]
                        bucket = used.setdefault(key, set())
                        if assign[e] in bucket:
                            clash = True
                            break
                        bucket.add(assign[e])
                    if clash:
                        continue
                    solutions.append(
                        (assign, {k: frozenset(v) for k, v in used.items()}))
                per_component.append(solutions)
            if any(not s for s in per_component):
                continue
            if _combine(data, slots, scheme, phases, per_component, class_size,
                        counters, support) is not None:
                return SPHERICAL
    return NOT_SPHERICAL
