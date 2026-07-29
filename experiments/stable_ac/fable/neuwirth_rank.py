"""Polynomial decision of Neuwirth-compatible sphericity for the three proved supports.

Implements the specialized criterion of ``lit_AK3_SYNCHRONIZED_PLANARITY.md``:

* **Theorem 3.1** — a rotation system of a loopless multigraph whose simple support is
  ``K_4`` is spherical iff every parallel class is one cyclic block at both endpoints,
  the contracted macro-rotation is the tetrahedral one (3.1) or its global reversal, and
  the block order at one endpoint is the reverse of the block order at the other.  The
  reversal ``C_{tau v} = B C_v^{-1} B`` of (2.1) survives a global reflection, so one
  macro-orientation is fixed and no solution is lost.
* **Theorem 5.2** — for ``K_4 - e`` with poles ``a, b`` (the simple-degree-3 germs) and
  ``c, d`` (the simple-degree-2 germs), every spherical bridge order at ``a`` is
  uniquely ``C, L[:i], D, L[i:]`` for a cut ``0 <= i <= m_ab`` and a linear order ``L``
  of the central class; the bridge order at ``b`` is its reverse.  The central class
  need not be a block, which is why the cut is enumerated.
* **Theorem 6.1** — for ``C_4`` every parallel class is one block with reversed endpoint
  orders and there is no macro-rotation choice, so a single scheme suffices.
* **Lemma 4.1** — the reversal (2.1) holds iff there is a single phase ``s_g`` per
  unsigned generator with ``P_d + P_{Bd} + s_g = 0 (mod n_{g+})`` for every
  ``B``-transposition.
* **Lemma 4.2** — contracting each ``A``-orbit and drawing one constraint edge per
  ``B``-transposition gives a 2-regular multigraph ``H_{A,B}`` whose components are the
  relator cycles.
* **Theorem 4.3** — for fixed phases and scheme, seeding one rank per component and
  propagating by inverse slot lookup finds every solution; the remaining coupling
  between components is the per-class all-different condition, enforced as within-cycle
  distinctness, cross-cycle disjointness, and the union-cardinality check (4.4).

Fail-closed boundary (the nine points of the note).  ``UNSUPPORTED`` — never ``NO`` — is
returned for an ``A``-loop, fewer than four germs, any relator shorter than three
letters, a disconnected support, or any support outside the three proved types.  Every
slot scheme is verified to partition each germ's slots before it is used, every
``B``-transposition contributes exactly one equation, constraint loops and 2-cycles are
checked rather than simplified away, and ``NOT_SPHERICAL`` is returned only after the
full product of schemes x phase pairs x seeds x component combinations is exhausted
(the counters in the verdict report both what was tried and what the budget was).
"""

from __future__ import annotations

from dataclasses import dataclass

from experiments.stable_ac.fable.neuwirth_core import (
    GERM_NAMES,
    TAU,
    X_POS,
    Y_POS,
    LinkData,
    NeuwirthInputError,
    build_link,
    euler_data,
    is_compatible,
    rotation_from_orders,
)

SPHERICAL = "SPHERICAL"
NOT_SPHERICAL = "NOT_SPHERICAL"
UNSUPPORTED = "UNSUPPORTED"

MIN_RELATOR_LENGTH = 3

# One tetrahedral macro-rotation of the simple K_4 on labels 0,1,2,3 -- equation (3.1).
# The germ indices x+, x-, y+, y- are used as the labels; every relabelling of (3.1)
# is (3.1) itself or its simultaneous reversal, and the reversal is the global
# reflection that (2.1) is invariant under, so this fixed choice is complete.
_K4_MACRO = {
    0: (1, 2, 3),
    1: (0, 3, 2),
    2: (0, 1, 3),
    3: (0, 2, 1),
}


class WitnessReplayError(RuntimeError):
    """An accepted rank solution failed its own replay -- an implementation bug."""


@dataclass(frozen=True)
class SupportClass:
    kind: str
    data: LinkData | None
    class_keys: tuple = ()
    multiplicities: tuple = ()          # ((key, m), ...) sorted by key
    missing_key: tuple | None = None
    poles: tuple | None = None          # (a, b, c, d) for K4-e
    reason: str | None = None

    def multiplicity_map(self) -> dict:
        return {k: m for k, m in self.multiplicities}


@dataclass(frozen=True)
class Scheme:
    name: str
    cut: int | None
    slots: tuple                        # germ -> {class key: tuple of slots by local index}
    reference: tuple                    # ((key, germ), ...) sorted by key
    partition_verified: bool

    def reference_map(self) -> dict:
        return dict(self.reference)


@dataclass
class Counters:
    schemes_considered: int = 0
    scheme_budget: int = 0
    phase_pairs_considered: int = 0
    phase_pair_budget: int = 0
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
class RankWitness:
    scheme: str
    cut: int | None
    phases: tuple
    ranks: tuple                        # A-edge index -> rank in its parallel class
    rotations: tuple                    # ((germ name, dart tuple), ...) -- the witness C
    permutation: tuple                  # C as an image list on the darts
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


@dataclass(frozen=True)
class RankDecision:
    words: tuple
    verdict: str
    spherical: bool | None
    support: SupportClass
    witness: RankWitness | None
    counters: Counters
    reason: str | None = None


# --------------------------------------------------------------------------------------
# support classification (fail-closed gate)
# --------------------------------------------------------------------------------------


def classify_support(words) -> SupportClass:
    """Classify the support of the exact link, or explain why it is out of scope."""
    words = tuple(words)
    try:
        data = build_link(words)
    except NeuwirthInputError as exc:
        return SupportClass("UNSUPPORTED", None, reason=f"malformed input: {exc}")

    short = [len(w) for w in words if len(w) < MIN_RELATOR_LENGTH]
    if short:
        return SupportClass(
            "UNSUPPORTED", data,
            reason=f"degenerate relator of length {min(short)} < {MIN_RELATOR_LENGTH}",
        )
    if len(data.present_germs) < 4:
        return SupportClass(
            "UNSUPPORTED", data,
            reason=f"only {len(data.present_germs)} germs occur; four are required",
        )
    if data.has_loop:
        return SupportClass(
            "UNSUPPORTED", data,
            reason=f"A-link has {len(data.loop_edges)} loop edge(s)",
        )
    if data.link_components != 1:
        return SupportClass(
            "UNSUPPORTED", data,
            reason=f"support has {data.link_components} components; only connected supports are proved",
        )

    keys = tuple(sorted(data.class_edges))
    mult = tuple((k, len(data.class_edges[k])) for k in keys)
    simple_degree = {v: 0 for v in range(4)}
    for u, v in keys:
        simple_degree[u] += 1
        simple_degree[v] += 1

    if len(keys) == 6:
        return SupportClass("K4", data, keys, mult)
    if len(keys) == 5:
        all_pairs = {(u, v) for u in range(4) for v in range(u + 1, 4)}
        missing = sorted(all_pairs - set(keys))
        if len(missing) != 1:
            return SupportClass("UNSUPPORTED", data, keys, mult,
                                reason="five classes but not K4 minus one edge")
        miss = missing[0]
        poles_ab = tuple(sorted(v for v in range(4) if simple_degree[v] == 3))
        poles_cd = tuple(sorted(miss))
        if len(poles_ab) != 2 or set(poles_ab) | set(poles_cd) != {0, 1, 2, 3}:
            return SupportClass("UNSUPPORTED", data, keys, mult,
                                reason="K4-e pole detection failed")
        return SupportClass("K4-e", data, keys, mult, missing_key=miss,
                            poles=(poles_ab[0], poles_ab[1], poles_cd[0], poles_cd[1]))
    if len(keys) == 4 and all(simple_degree[v] == 2 for v in range(4)):
        return SupportClass("C4", data, keys, mult)
    return SupportClass(
        "UNSUPPORTED", data, keys, mult,
        reason=f"simple support has {len(keys)} classes with degrees "
               f"{tuple(simple_degree[v] for v in range(4))}; outside K4 / K4-e / C4",
    )


# --------------------------------------------------------------------------------------
# slot schemes
# --------------------------------------------------------------------------------------


def _blocks_to_slots(order, mult):
    """Lay consecutive blocks out; returns {key: tuple of slots} and the total width."""
    out = {}
    base = 0
    for key in order:
        m = mult[key]
        out[key] = tuple(range(base, base + m))
        base += m
    return out, base


def _verify_partition(data: LinkData, slots) -> bool:
    for v in range(4):
        n = data.degree(v)
        seen = []
        for key, positions in slots[v].items():
            if len(positions) != len(data.class_edges[key]):
                return False
            seen.extend(positions)
        if sorted(seen) != list(range(n)):
            return False
    return True


def _k4_schemes(support: SupportClass):
    data = support.data
    mult = support.multiplicity_map()
    slots = []
    for v in range(4):
        order = [tuple(sorted((v, w))) for w in _K4_MACRO[v]]
        block, width = _blocks_to_slots(order, mult)
        if width != data.degree(v):
            raise NeuwirthInputError("K4 block widths do not fill the germ")
        slots.append(block)
    reference = tuple((k, min(k)) for k in support.class_keys)
    scheme = Scheme("K4", None, tuple(slots), reference,
                    _verify_partition(data, slots))
    return (scheme,)


def _c4_schemes(support: SupportClass):
    data = support.data
    mult = support.multiplicity_map()
    slots = []
    for v in range(4):
        order = sorted(k for k in support.class_keys if v in k)
        block, width = _blocks_to_slots(order, mult)
        if width != data.degree(v):
            raise NeuwirthInputError("C4 block widths do not fill the germ")
        slots.append(block)
    reference = tuple((k, min(k)) for k in support.class_keys)
    scheme = Scheme("C4", None, tuple(slots), reference,
                    _verify_partition(data, slots))
    return (scheme,)


def _k4_minus_e_schemes(support: SupportClass):
    """One scheme per cut ``i = 0 .. m_ab`` of Theorem 5.2."""
    data = support.data
    mult = support.multiplicity_map()
    a, b, c, d = support.poles
    k_ab = tuple(sorted((a, b)))
    k_ac = tuple(sorted((a, c)))
    k_bc = tuple(sorted((b, c)))
    k_ad = tuple(sorted((a, d)))
    k_bd = tuple(sorted((b, d)))
    m = mult[k_ab]
    m_ac, m_bc, m_ad, m_bd = mult[k_ac], mult[k_bc], mult[k_ad], mult[k_bd]

    # Reference endpoints: the central class is read at a; each leg at its pole.
    reference = ((k_ab, a), (k_ac, a), (k_bc, b), (k_ad, a), (k_bd, b))
    reference = tuple(sorted(reference))

    schemes = []
    for i in range(m + 1):
        slots = [dict() for _ in range(4)]
        # a: P_ac, L[:i], P_ad, L[i:]
        slots[a][k_ac] = tuple(range(0, m_ac))
        slots[a][k_ab] = tuple(
            (m_ac + t) if t < i else (m_ac + i + m_ad + (t - i)) for t in range(m)
        )
        slots[a][k_ad] = tuple(range(m_ac + i, m_ac + i + m_ad))
        # b: P_bc, rev(L[i:]), P_bd, rev(L[:i]); local index t = m-1-z at b
        slots[b][k_bc] = tuple(range(0, m_bc))
        slots[b][k_ab] = tuple(
            (m_bc + t) if t < m - i else (m_bc + (m - i) + m_bd + (t - (m - i)))
            for t in range(m)
        )
        slots[b][k_bd] = tuple(range(m_bc + (m - i), m_bc + (m - i) + m_bd))
        # c: the two reversed leg blocks concatenate (a 2-block cyclic order is unique)
        slots[c][k_ac] = tuple(range(0, m_ac))
        slots[c][k_bc] = tuple(range(m_ac, m_ac + m_bc))
        # d: likewise
        slots[d][k_ad] = tuple(range(0, m_ad))
        slots[d][k_bd] = tuple(range(m_ad, m_ad + m_bd))
        slots = tuple(slots)
        schemes.append(
            Scheme(f"K4-e[cut={i}]", i, slots, reference, _verify_partition(data, slots))
        )
    return tuple(schemes)


def embedding_schemes(support: SupportClass):
    if support.kind == "K4":
        return _k4_schemes(support)
    if support.kind == "C4":
        return _c4_schemes(support)
    if support.kind == "K4-e":
        return _k4_minus_e_schemes(support)
    raise NeuwirthInputError(f"no scheme for support {support.kind}")


# --------------------------------------------------------------------------------------
# constraints and their components
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class _Constraint:
    dart_a: int
    dart_b: int
    edge_a: int
    edge_b: int
    generator: int          # 0 = x, 1 = y
    modulus: int


def _constraints(data: LinkData):
    """Exactly one modular equation per ``B``-transposition, i.e. per occurrence."""
    out = []
    for i in range(data.n_occurrences):
        da, db = 2 * i, 2 * i + 1
        va = data.germ[da]
        if data.germ[db] != TAU[va]:
            raise NeuwirthInputError("germ map violates nu(Bd) = tau(nu(d))")
        generator = 0 if va in (X_POS, TAU[X_POS]) else 1
        modulus = data.degree(va)
        if modulus != data.degree(data.germ[db]):
            raise NeuwirthInputError("n_v != n_{tau v}")
        out.append(_Constraint(da, db, data.edge_of_dart[da], data.edge_of_dart[db],
                               generator, modulus))
    return tuple(out)


def _components(n_edges: int, constraints):
    """Connected components of ``H_{A,B}`` (Lemma 4.2: the relator cycles)."""
    parent = list(range(n_edges))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for c in constraints:
        ra, rb = find(c.edge_a), find(c.edge_b)
        if ra != rb:
            parent[ra] = rb
    buckets = {}
    for e in range(n_edges):
        buckets.setdefault(find(e), []).append(e)
    comps = []
    for root in sorted(buckets):
        edges = tuple(buckets[root])
        cons = tuple(c for c in constraints if find(c.edge_a) == root)
        comps.append((edges, cons))
    return tuple(comps)


# --------------------------------------------------------------------------------------
# the solver
# --------------------------------------------------------------------------------------


class _Slots:
    """Slot arithmetic for one scheme (equation (4.2) and its ``K_4-e`` refinement)."""

    __slots__ = ("data", "scheme", "reference", "class_size", "inverse")

    def __init__(self, data: LinkData, scheme: Scheme):
        self.data = data
        self.scheme = scheme
        self.reference = scheme.reference_map()
        self.class_size = {k: len(v) for k, v in data.class_edges.items()}
        self.inverse = []
        for v in range(4):
            table = {}
            for key, positions in scheme.slots[v].items():
                for t, slot in enumerate(positions):
                    if slot in table:
                        raise NeuwirthInputError("slot scheme is not injective")
                    table[slot] = (key, t)
            self.inverse.append(table)

    def _local(self, dart: int, rank: int) -> int:
        key = self.data.edge_class[self.data.edge_of_dart[dart]]
        if self.reference[key] == self.data.germ[dart]:
            return rank
        return self.class_size[key] - 1 - rank

    def slot(self, dart: int, rank: int) -> int:
        v = self.data.germ[dart]
        key = self.data.edge_class[self.data.edge_of_dart[dart]]
        return self.scheme.slots[v][key][self._local(dart, rank)]

    def rank_at_slot(self, dart: int, slot: int):
        """The unique rank of ``dart``'s edge that puts it in ``slot``, or ``None``."""
        v = self.data.germ[dart]
        entry = self.inverse[v].get(slot)
        if entry is None:
            return None
        key, t = entry
        if key != self.data.edge_class[self.data.edge_of_dart[dart]]:
            return None
        if self.reference[key] == v:
            return t
        return self.class_size[key] - 1 - t


def _propagate(slots: _Slots, adjacency, seed_edge: int, seed_rank: int, phases):
    """Theorem 4.3 propagation around one component of ``H_{A,B}``.

    Every constraint of the component is traversed from *both* of its ends, so loops
    and 2-cycles are tested rather than simplified away, and the closing equation is
    checked rather than assumed.
    """
    assign = {seed_edge: seed_rank}
    stack = [seed_edge]
    while stack:
        edge = stack.pop()
        rank = assign[edge]
        for constraint, here, other, other_edge in adjacency[edge]:
            slot_here = slots.slot(here, rank)
            needed = (-phases[constraint.generator] - slot_here) % constraint.modulus
            other_rank = slots.rank_at_slot(other, needed)
            if other_rank is None:
                return None
            known = assign.get(other_edge)
            if known is None:
                assign[other_edge] = other_rank
                stack.append(other_edge)
            elif known != other_rank:
                return None
    return assign


def _adjacency(n_edges: int, constraints):
    adj = [[] for _ in range(n_edges)]
    for c in constraints:
        adj[c.edge_a].append((c, c.dart_a, c.dart_b, c.edge_b))
        adj[c.edge_b].append((c, c.dart_b, c.dart_a, c.edge_a))
    return adj


def _build_rotations(data: LinkData, slots: _Slots, ranks):
    orders = {}
    for v in data.present_germs:
        placed = {}
        for dart in data.vertex_darts[v]:
            slot = slots.slot(dart, ranks[data.edge_of_dart[dart]])
            if slot in placed:
                raise NeuwirthInputError("two darts in one slot")
            placed[slot] = dart
        if sorted(placed) != list(range(data.degree(v))):
            raise NeuwirthInputError("slots at a germ are not a bijection")
        orders[v] = tuple(placed[s] for s in range(data.degree(v)))
    return orders


def solve_spherical(words) -> RankDecision:
    """Decide Neuwirth-compatible sphericity of the exact word-realized complex.

    A ``NOT_SPHERICAL`` from this entry point is exhaustive over the whole proved
    family of schemes.
    """
    return solve_with_schemes(words, None)


def solve_with_schemes(words, schemes=None) -> RankDecision:
    """The search restricted to ``schemes`` (``None`` = the complete proved family).

    Audit-only knob.  A ``NOT_SPHERICAL`` produced from a *proper* subfamily is a
    statement about that subfamily only; it is used in the tests to show that some
    ``K_4 - e`` instances are spherical only for a split cut ``0 < i < m``.
    """
    words = tuple(words)
    support = classify_support(words)
    counters = Counters()
    if support.kind == "UNSUPPORTED":
        return RankDecision(words, UNSUPPORTED, None, support, None, counters,
                            reason=support.reason)

    data = support.data
    if schemes is None:
        schemes = embedding_schemes(support)
    schemes = tuple(schemes)
    for scheme in schemes:
        if not scheme.partition_verified:
            return RankDecision(
                words, UNSUPPORTED, None, support, None, counters,
                reason=f"scheme {scheme.name} does not partition the germ slots",
            )

    constraints = _constraints(data)
    n_edges = len(data.edge_darts)
    components = _components(n_edges, constraints)
    adjacency = _adjacency(n_edges, constraints)
    if sum(len(c[1]) for c in components) != len(constraints):
        raise NeuwirthInputError("constraint partition lost an equation")

    n_x = data.degree(X_POS)
    n_y = data.degree(Y_POS)
    class_size = {k: len(v) for k, v in data.class_edges.items()}
    seeds_per_phase = sum(
        class_size[data.edge_class[edges[0]]] for edges, _ in components
    )

    counters.scheme_budget = len(schemes)
    counters.phase_pair_budget = len(schemes) * n_x * n_y
    counters.component_seed_budget = counters.phase_pair_budget * seeds_per_phase

    for scheme in schemes:
        counters.schemes_considered += 1
        slots = _Slots(data, scheme)
        for s_x in range(n_x):
            for s_y in range(n_y):
                counters.phase_pairs_considered += 1
                phases = (s_x, s_y)
                per_component = []
                # Every component's every seed is tried even once one component is
                # known infeasible, so the reported attempt counts always equal the
                # budget and the exhaustiveness claim is auditable from the counters.
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
                witness = _combine(data, slots, scheme, phases, per_component,
                                   class_size, counters, words, support)
                if witness is not None:
                    counters.exhaustive = False
                    return RankDecision(words, SPHERICAL, True, support, witness,
                                        counters)

    counters.exhaustive = True
    return RankDecision(words, NOT_SPHERICAL, False, support, None, counters,
                        reason="every scheme, phase pair, seed and component "
                               "combination was exhausted")


def _combine(data, slots, scheme, phases, per_component, class_size, counters,
             words, support):
    """Cross-component combination with (4.4); returns a verified witness or ``None``."""
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
            return _finalise(data, slots, scheme, phases, ranks, counters)
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


def _finalise(data, slots, scheme, phases, ranks, counters):
    """Rebuild the rotations, replay (2.1) and Euler; a failure is a bug, not a NO."""
    ranks_tuple = tuple(ranks[e] for e in range(len(data.edge_darts)))
    orders = _build_rotations(data, slots, ranks_tuple)
    C = rotation_from_orders(data, orders)
    compatible = is_compatible(data, C)
    numbers = euler_data(data, C)
    if not compatible or numbers["defect"] != 0 or numbers["link_components"] != 1:
        counters.witness_replay_failures += 1
        raise WitnessReplayError(
            f"accepted rank solution failed replay: compatible={compatible}, "
            f"numbers={numbers}, scheme={scheme.name}, phases={phases}"
        )
    return RankWitness(
        scheme=scheme.name,
        cut=scheme.cut,
        phases=tuple(phases),
        ranks=ranks_tuple,
        rotations=tuple((GERM_NAMES[v], orders[v]) for v in sorted(orders)),
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
