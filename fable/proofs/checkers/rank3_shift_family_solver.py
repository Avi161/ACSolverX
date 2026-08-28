"""W6b: a certified rank-general Neuwirth solver for BOOK and SPLIT_ENDPOINT support.

This is the family `W6_RANK3_FEASIBILITY.md` §2.5 said was missing: a
`P4`-style relative-shift analysis over *several* macro embeddings of a
2-connected six-germ support, in place of the `K6 - E(P5)` Whitney-pair
rigidity argument.  It decides `Tpub = (A, B, Xyz)`.

WHAT IS PROVEN AND WHAT IS ENUMERATED
=====================================

Setting.  `G` is the occurrence link multigraph of `AK3_NEUWIRTH.md` (built by
`rank3_link_graph.build_link`, imported, never re-derived here).  `H` is its
simple support; a *bundle* is a parallel class of `G`, of multiplicity
`m_beta`.  A compatible ordering is a rotation at every germ `g+` with the
rotation at `g-` forced to the reversed `B`-image.  `gamma_N = 0` iff some
compatible ordering is a *spherical* rotation system of `G` (Euler
characteristic `2` for a connected link).

Lemma A (bundle regions) — PROVEN.
    Let `beta = {u,v}` have `m >= 2` and let `G` be embedded in `S^2`.  The
    `m` arcs of `beta` meet only at `u` and `v`, so they cut `S^2` into
    exactly `m` regions.  Every connected component of `G - {u,v}` is a
    connected set disjoint from those arcs, hence lies in the closure of a
    single region; every edge of `G` that is not in `beta` joins `u` or `v`
    to (or lies inside) one such component, hence lies in that component's
    region.  So the *occupied* regions are indexed by the components of
    `G - {u,v}` (each component occupies exactly one).

Lemma B (book decoupling) — PROVEN, and this is the decoupling lemma the task
asked for.
    If `G - {u,v}` is connected for every bundle `beta = {u,v}` with
    `m_beta >= 2`, then in EVERY spherical rotation system of `G`:
      (i)  each bundle occupies one region only (Lemma A with one component),
           so its `m` darts are consecutive in the rotation at `u` and at `v`
           ("book form");
      (ii) deleting `m_beta - 1` edges from every bundle is deletion of
           non-bridges, so it preserves sphericity and yields a spherical
           rotation system of `H`; and by (i) the `G`-rotation is recovered
           from the `H`-rotation by re-inserting each bundle as one block;
      (iii) the cyclic order of a bundle's arcs at `v` is the reverse of the
           order at `u` (the `m` arcs bound `m` regions in a cyclic sequence
           whose orientation reverses between the two endpoints), and the
           *alignment* of that reversal is pinned: the unique occupied region
           is bounded by the same ordered pair of arcs seen from `u` and from
           `v`.  Hence there is NO relative-shift freedom in a book bundle.
    Therefore the spherical rotation systems of `G` are in bijection with
    (spherical rotation systems of `H`) x (a labelling of each bundle's `m`
    edges by its `m` block positions).  The first factor is the *macro
    rotation*; the second is the *rank* assignment.

Lemma C (endpoint split) — PROVEN; this is `neuwirth_p4_solver`'s central-gap
mechanism lifted off the 4-vertex path.
    Suppose exactly one bundle `beta = {u,v}` with `m >= 2` has `G - {u,v}`
    disconnected, with exactly two components `P1, P2`, `P1` meeting only `u`
    and `P2` meeting only `v` (all other `m >= 2` bundles satisfy Lemma B).
    Then at `u` only `P1` is present, so exactly one region is occupied as
    seen from `u` and the bundle is book at `u`; likewise at `v`.  The
    alignment of the reversal is now NOT pinned — the region occupied at `u`
    and the region occupied at `v` may differ — and the two occupied regions
    differ by an offset `t in Z_m`.  So the schemes are (macro rotations)
    x (`m` relative shifts), and `m` is a complete shift set.

Lemma D (gauge) — PROVEN, and checked by a control.
    A scheme fixes an absolute slot `0..deg(v)-1` per dart, i.e. a linear
    representative of a cyclic order.  Replacing the slots at any germ vertex
    by a cyclic shift changes every phase equation
    `slot(p) + slot(n) + phase = 0 (mod m_g)` by a constant, which the phase
    parameter (quantified over all of `Z_{m_g}`) absorbs.  So fixing one
    linear representative per vertex loses no compatible ordering.

Lemma E (reflection) — PROVEN, not used to shrink anything here.
    Reversing every rotation maps compatible orderings to compatible
    orderings and preserves the face count, so spherical compatible orderings
    come in reflection pairs.  The macro rotation set is closed under
    reflection; this solver enumerates all of them anyway (it does not halve
    the work), so a completeness bug cannot hide behind this lemma.

ENUMERATED (not proven — finite, closed, and counted):
    * the macro rotations: every rotation system of `H` is generated and kept
      iff `V - E + F = 2` (a complete finite closure over `prod (deg-1)!`);
    * the shift offsets `t in Z_m` in the SPLIT_ENDPOINT case;
    * the phase tuples `prod_g Z_{m_g}`;
    * the rank assignments, by seeded propagation around the 2-regular
      constraint graph (shared verbatim with the repo's certified solver:
      `neuwirth_rank_solver._propagate_component`), then a depth-first
      combination of per-component solutions with per-class rank masks.

FAIL CLOSED.  Any support outside BOOK / SPLIT_ENDPOINT (a loop, a
disconnected link, a missing generator, two or more split bundles, a split
bundle with three or more pieces, a split bundle whose pieces touch both
endpoints — the `K4-e` shape, which the repo's certified rank-2 solver
already decides) returns `UNSUPPORTED`.  A negative is returned only after
the whole finite case set above has been consumed; a truncated search raises.

DOCTRINE.  `NOT_SPHERICAL` is a certificate (necessity half of Theorem 2 of
`literature/proofs/AK3_NEUWIRTH.md`, which does not use connectivity) for the
exact spelling tested.  A `gamma_N = 0` / spherical verdict is reported as
`SPHERICAL_REQUIRES_REGINA` and is QUARANTINED: Pipeline B (Regina `isBall`
on an independently built `N(K)`) does not exist in this repo, so a positive
is a suspected Pipeline-A bug first and a result never.  No AK(3), AC, or
stable-AC claim is made anywhere in this file.

Run (every mode fits the guard's 60 s slice):

    python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- \\
        python3 fable/proofs/checkers/rank3_shift_family_solver.py controls
    python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- \\
        python3 fable/proofs/checkers/rank3_shift_family_solver.py crosscheck
    python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- \\
        python3 fable/proofs/checkers/rank3_shift_family_solver.py repo-agreement
    python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- \\
        python3 fable/proofs/checkers/rank3_shift_family_solver.py targets
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
REPO = HERE.parents[2]

if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import rank3_link_graph as rlg  # noqa: E402  (the W6 builder, imported not forked)
from experiments.stable_ac.thickenable import (  # noqa: E402
    neuwirth_rank_solver as base,
)

ClassKey = tuple[int, int]

# Hard caps.  Nothing here is a budgeted search: these are closure guards that
# RAISE rather than silently truncate, so a negative can never come from a cut
# short enumeration.
MAX_MACRO_ENUMERATION = 4_000_000
MAX_DFS_NODES = 2_000_000

# Lemma B(iii): a bundle's arcs run in opposite cyclic senses at its two
# endpoints.  This flag exists ONLY so a corruption control can switch the
# reversal off and watch a verdict move; production code never touches it.
REVERSE_BUNDLE_BLOCKS = True


FAILS: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> bool:
    print(f"{'PASS' if cond else 'FAIL'}  {name}" + (f"   {detail}" if detail else ""))
    if not cond:
        FAILS.append(name)
    return bool(cond)


# ---------------------------------------------------------------------------
# link data adapter: rank3_link_graph.Link -> the repo's LinkData
# ---------------------------------------------------------------------------


def link_data(link: rlg.Link) -> base.LinkData:
    """Index the W6 link graph the way the certified rank solver expects.

    The dart dictionary (`A`, `B`, `germ`) is taken verbatim from
    `rank3_link_graph.build_link`; only derived indices (edge ids, parallel
    classes, vertex incidence) are computed here.
    """
    n = len(link.A)
    edge_of_dart = [-1] * n
    edge_darts: list[tuple[int, int]] = []
    edge_class: list[ClassKey] = []
    class_edges: dict[ClassKey, list[int]] = {}
    for dart, mate in enumerate(link.A):
        if dart > mate:
            continue
        edge = len(edge_darts)
        edge_darts.append((dart, mate))
        edge_of_dart[dart] = edge
        edge_of_dart[mate] = edge
        key = tuple(sorted((link.germ[dart], link.germ[mate])))
        edge_class.append(key)  # type: ignore[arg-type]
        class_edges.setdefault(key, []).append(edge)  # type: ignore[arg-type]
    if min(edge_of_dart) < 0:
        raise AssertionError("dart without an A-edge")
    return base.LinkData(
        words=link.words,
        A=link.A,
        B=link.B,
        germ=link.germ,
        edge_of_dart=tuple(edge_of_dart),
        edge_darts=tuple(edge_darts),
        edge_class=tuple(edge_class),
        class_edges={k: tuple(v) for k, v in sorted(class_edges.items())},
        vertex_darts={
            v: tuple(d for d in range(n) if link.germ[d] == v)
            for v in range(link.n_germs)
        },
    )


# ---------------------------------------------------------------------------
# support analysis: pieces, macro rotations, family classification
# ---------------------------------------------------------------------------


def pieces_of(
    verts: list[int], simple: frozenset[ClassKey], u: int, v: int
) -> tuple[frozenset[int], ...]:
    """Connected components of H - {u, v} (Lemma A's region index set)."""
    rest = [w for w in verts if w not in (u, v)]
    adj: dict[int, set[int]] = {w: set() for w in rest}
    for a, b in simple:
        if a in adj and b in adj:
            adj[a].add(b)
            adj[b].add(a)
    seen: set[int] = set()
    out = []
    for w in rest:
        if w in seen:
            continue
        comp = {w}
        seen.add(w)
        stack = [w]
        while stack:
            t = stack.pop()
            for s in adj[t] - seen:
                seen.add(s)
                comp.add(s)
                stack.append(s)
        out.append(frozenset(comp))
    return tuple(sorted(out, key=sorted))


def face_count(
    rotation: dict[int, tuple[int, ...]], simple: frozenset[ClassKey]
) -> int:
    directed = {(u, v) for u, v in simple} | {(v, u) for u, v in simple}
    seen: set[tuple[int, int]] = set()
    faces = 0
    for start in sorted(directed):
        if start in seen:
            continue
        faces += 1
        dart = start
        while dart not in seen:
            seen.add(dart)
            a, b = dart
            order = rotation[b]
            dart = (b, order[(order.index(a) + 1) % len(order)])
    if seen != directed:
        raise AssertionError("simple face trace missed a directed edge")
    return faces


def macro_rotations(
    verts: list[int], simple: frozenset[ClassKey]
) -> tuple[dict[int, tuple[int, ...]], ...]:
    """Every spherical rotation system of the SIMPLE support (a closure)."""
    adj: dict[int, set[int]] = {v: set() for v in verts}
    for u, v in simple:
        adj[u].add(v)
        adj[v].add(u)
    total = 1
    for v in verts:
        total *= math.factorial(max(0, len(adj[v]) - 1))
    if total > MAX_MACRO_ENUMERATION:
        raise AssertionError(
            f"macro rotation closure too large ({total}); refusing to truncate"
        )
    per_vertex = []
    for v in verts:
        neighbors = sorted(adj[v])
        if not neighbors:
            raise AssertionError("isolated germ vertex in a connected support")
        head, *tail = neighbors
        per_vertex.append([(head, *p) for p in itertools.permutations(tail)])
    out = []
    for combo in itertools.product(*per_vertex):
        rot = dict(zip(verts, combo))
        if len(verts) - len(simple) + face_count(rot, simple) == 2:
            out.append(rot)
    return tuple(out)


@dataclass(frozen=True)
class Family:
    kind: str                       # BOOK | SPLIT_ENDPOINT | UNSUPPORTED
    reason: str | None
    data: base.LinkData | None
    gens: str
    n_germs: int
    simple_edges: frozenset[ClassKey] = frozenset()
    macro: tuple[dict[int, tuple[int, ...]], ...] = ()
    split_bundle: ClassKey | None = None
    split_multiplicity: int = 0
    bundle_report: tuple[dict[str, object], ...] = ()


def classify_family(words: tuple[str, ...], gens: str) -> Family:
    try:
        link = rlg.build_link(tuple(words), gens)
    except ValueError as exc:
        return Family("UNSUPPORTED", f"link graph rejected the words: {exc}",
                      None, gens, 2 * len(gens))
    simple, loops = rlg.simple_support(link)
    data = link_data(link)
    n_germs = link.n_germs
    verts = sorted(rlg.active_germs(link))
    if loops:
        return Family("UNSUPPORTED", "A-link contains a loop", data, gens, n_germs)
    if len(verts) != n_germs:
        return Family("UNSUPPORTED", "some generator does not occur",
                      data, gens, n_germs)
    if len(rlg.components(link)) != 1:
        return Family("UNSUPPORTED", "A-link is disconnected", data, gens, n_germs)

    mult = {key: len(edges) for key, edges in data.class_edges.items()}
    report = []
    split: ClassKey | None = None
    kind = "BOOK"
    reason = None
    for key in sorted(mult):
        u, v = key
        m = mult[key]
        ps = pieces_of(verts, simple, u, v)
        row: dict[str, object] = {
            "bundle": f"{u}-{v}", "multiplicity": m, "pieces": len(ps)
        }
        if m < 2:
            row["class"] = "SINGLE_EDGE (no bundle freedom)"
            report.append(row)
            continue
        if len(ps) == 1:
            row["class"] = "BOOK"
            report.append(row)
            continue
        if len(ps) != 2:
            row["class"] = f"SPLIT_k{len(ps)}"
            report.append(row)
            kind = "UNSUPPORTED"
            reason = f"bundle {u}-{v} has {len(ps)} pieces (>2)"
            continue
        touch = []
        for piece in ps:
            tu = any(tuple(sorted((u, w))) in simple for w in piece)
            tv = any(tuple(sorted((v, w))) in simple for w in piece)
            touch.append((tu, tv))
        if sorted(touch) == [(False, True), (True, False)]:
            row["class"] = "SPLIT_ENDPOINT"
            report.append(row)
            if split is not None:
                kind = "UNSUPPORTED"
                reason = "more than one split bundle"
            elif kind == "BOOK":
                kind = "SPLIT_ENDPOINT"
                split = key
        else:
            row["class"] = "SPLIT_BOTH_ENDS (K4-e shape; not in this family)"
            report.append(row)
            kind = "UNSUPPORTED"
            reason = f"bundle {u}-{v} has two pieces touching both endpoints"

    if kind == "UNSUPPORTED":
        return Family("UNSUPPORTED", reason, data, gens, n_germs,
                      frozenset(simple), (), None, 0, tuple(report))
    try:
        macro = macro_rotations(verts, frozenset(simple))
    except AssertionError as exc:
        # too dense to close the macro enumeration: make NO claim rather than
        # decide from a truncated scheme set
        return Family("UNSUPPORTED", str(exc), data, gens, n_germs,
                      frozenset(simple), (), None, 0, tuple(report))
    if not macro:
        return Family("UNSUPPORTED", "simple support is not planar",
                      data, gens, n_germs, frozenset(simple), (), None, 0,
                      tuple(report))
    return Family(kind, None, data, gens, n_germs, frozenset(simple), macro,
                  split, mult[split] if split else 0, tuple(report))


# ---------------------------------------------------------------------------
# schemes
# ---------------------------------------------------------------------------


def verify_slot_partition(data: base.LinkData, slots, n_germs: int) -> bool:
    for vertex in range(n_germs):
        images: list[int] = []
        for key in data.class_edges:
            if vertex not in key:
                continue
            edge = data.class_edges[key][0]
            dart = base._dart_for_edge_at(data, edge, vertex)
            image = slots[dart]
            if len(set(image)) != len(image):
                return False
            images.extend(image)
        if sorted(images) != list(range(len(data.vertex_darts[vertex]))):
            return False
    return all(all(slot >= 0 for slot in image) for image in slots)


def book_scheme(
    data: base.LinkData,
    rotation: dict[int, tuple[int, ...]],
    n_germs: int,
    name: str,
) -> base.Scheme:
    """Blow every bundle up as one contiguous block, in macro-rotation order.

    Block order at a vertex = the macro rotation; within a block the ranks run
    forward at the class key's smaller germ and backward at the larger one
    (Lemma B(iii): the arcs reverse between the endpoints, and relabelling
    ranks `r -> m-1-r` turns one convention into the other, so the choice is
    without loss of generality).
    """
    slots = base._empty_slots(data)
    for vertex in range(n_germs):
        start = 0
        for neighbor in rotation[vertex]:
            key = tuple(sorted((vertex, neighbor)))
            base._set_class_block(
                data, slots, key, vertex, start,
                reverse=(vertex != key[0]) if REVERSE_BUNDLE_BLOCKS else False,
            )
            start += len(data.class_edges[key])
    if not verify_slot_partition(data, slots, n_germs):
        raise AssertionError("book scheme produced an invalid slot partition")
    return base.Scheme(name, "BOOK", None, tuple(map(tuple, slots)), True)


def shifted_scheme(
    data: base.LinkData,
    unshifted: base.Scheme,
    bundle: ClassKey,
    shift: int,
    n_germs: int,
    name: str,
) -> base.Scheme:
    """Rotate the split bundle's block at its larger germ by `shift` (Lemma C)."""
    m = len(data.class_edges[bundle])
    vertex = bundle[1]
    slots = [list(row) for row in unshifted.slots]
    for edge in data.class_edges[bundle]:
        dart = base._dart_for_edge_at(data, edge, vertex)
        start = min(slots[dart])
        slots[dart][:] = [
            start + ((slot - start + shift) % m) for slot in slots[dart]
        ]
    if not verify_slot_partition(data, slots, n_germs):
        raise AssertionError("shifted scheme produced an invalid slot partition")
    return base.Scheme(name, "SPLIT_ENDPOINT", shift,
                       tuple(map(tuple, slots)), True)


def schemes_for(family: Family, shift_offsets: bool = True) -> tuple[base.Scheme, ...]:
    if family.kind == "UNSUPPORTED" or family.data is None:
        return ()
    data = family.data
    out: list[base.Scheme] = []
    for index, rotation in enumerate(family.macro):
        book = book_scheme(data, rotation, family.n_germs, f"macro{index}")
        if family.kind == "BOOK":
            out.append(book)
            continue
        assert family.split_bundle is not None
        m = family.split_multiplicity
        offsets = range(m) if shift_offsets else range(1)
        for t in offsets:
            out.append(
                shifted_scheme(data, book, family.split_bundle, t,
                               family.n_germs, f"macro{index}-shift{t}")
            )
    return tuple(out)


# ---------------------------------------------------------------------------
# constraints, replay, search
# ---------------------------------------------------------------------------


def constraints_of(data: base.LinkData, n_gens: int) -> tuple[base._Constraint, ...]:
    positive_germs = tuple(2 * k for k in range(n_gens))
    out = []
    for departure in range(0, len(data.B), 2):
        arrival = data.B[departure]
        if data.germ[departure] in positive_germs:
            positive, negative = departure, arrival
        else:
            positive, negative = arrival, departure
        positive_germ = data.germ[positive]
        if positive_germ not in positive_germs:
            raise AssertionError("occurrence without a positive generator germ")
        out.append(
            base._Constraint(
                edge_positive=data.edge_of_dart[positive],
                edge_negative=data.edge_of_dart[negative],
                dart_positive=positive,
                dart_negative=negative,
                phase_index=positive_germ // 2,
                modulus=len(data.vertex_darts[positive_germ]),
            )
        )
    degree = [0] * len(data.edge_darts)
    for constraint in out:
        degree[constraint.edge_positive] += 1
        degree[constraint.edge_negative] += 1
    if any(value != 2 for value in degree):
        raise AssertionError("A-contracted B-constraint graph is not 2-regular")
    return tuple(out)


def faces_and_euler(
    data: base.LinkData, sigma: list[int], n_germs: int
) -> tuple[tuple[tuple[int, ...], ...], int]:
    phi = tuple(sigma[data.A[dart]] for dart in range(len(data.A)))
    faces = base._permutation_cycles(phi)
    euler = n_germs - len(data.edge_darts) + len(faces)
    return faces, euler


@dataclass(frozen=True)
class ShiftWitness:
    scheme: str
    shift: int | None
    phases: tuple[int, ...]
    ranks: tuple[int, ...]
    rotations: tuple[tuple[int, ...], ...]
    face_count: int
    euler_characteristic: int
    genus: int
    b_reversal_verified: bool
    rank_partition_verified: bool
    phase_equations_verified: bool


def replay_witness(
    data: base.LinkData,
    scheme: base.Scheme,
    constraints: tuple[base._Constraint, ...],
    phases: tuple[int, ...],
    ranks: tuple[int, ...],
    n_germs: int,
) -> ShiftWitness | None:
    """Independent re-derivation of the embedding from (scheme, phases, ranks).

    Nothing about the search is trusted here: the rotations are rebuilt from
    the slot maps, `B`-reversal and the phase equations are re-checked, and
    the Euler characteristic is recomputed by tracing faces.
    """
    rank_partition_verified = all(
        {ranks[edge] for edge in edges} == set(range(len(edges)))
        for edges in data.class_edges.values()
    )
    if not rank_partition_verified:
        return None
    rotations = []
    sigma = [-1] * len(data.A)
    for vertex in range(n_germs):
        rotation = tuple(
            sorted(
                data.vertex_darts[vertex],
                key=lambda dart: scheme.slots[dart][ranks[data.edge_of_dart[dart]]],
            )
        )
        if {
            scheme.slots[dart][ranks[data.edge_of_dart[dart]]] for dart in rotation
        } != set(range(len(rotation))):
            return None
        rotations.append(rotation)
        for index, dart in enumerate(rotation):
            sigma[dart] = rotation[(index + 1) % len(rotation)]
    b_reversal_verified = all(
        base._cyclically_equal(
            tuple(data.B[dart] for dart in reversed(rotations[2 * k])),
            rotations[2 * k + 1],
        )
        for k in range(n_germs // 2)
    )
    phase_equations_verified = all(
        (
            scheme.slots[c.dart_positive][ranks[c.edge_positive]]
            + scheme.slots[c.dart_negative][ranks[c.edge_negative]]
            + phases[c.phase_index]
        ) % c.modulus == 0
        for c in constraints
    )
    faces, euler = faces_and_euler(data, sigma, n_germs)
    if euler != 2 or not b_reversal_verified or not phase_equations_verified:
        return None
    return ShiftWitness(
        scheme=scheme.name,
        shift=scheme.cut,
        phases=phases,
        ranks=ranks,
        rotations=tuple(rotations),
        face_count=len(faces),
        euler_characteristic=euler,
        genus=0,
        b_reversal_verified=True,
        rank_partition_verified=True,
        phase_equations_verified=True,
    )


@dataclass
class Counters:
    scheme_budget: int = 0
    schemes_considered: int = 0
    phase_tuple_budget: int = 0
    phase_tuples_considered: int = 0
    component_seed_budget: int = 0
    component_seed_attempts: int = 0
    closed_component_assignments: int = 0
    within_cycle_collision_rejections: int = 0
    dfs_nodes: int = 0
    dfs_prunes: int = 0
    full_assignments_considered: int = 0
    union_cardinality_rejections: int = 0
    witness_replay_failures: int = 0
    exhaustive: bool = False


@dataclass
class ShiftDecision:
    words: tuple[str, ...]
    gens: str
    verdict: str
    spherical: bool | None
    family: str
    reason: str | None
    witness: ShiftWitness | None
    counters: Counters
    bundle_report: tuple[dict[str, object], ...] = ()
    macro_rotation_count: int = 0
    extras: dict = field(default_factory=dict)


def _combine(
    data: base.LinkData,
    scheme: base.Scheme,
    constraints: tuple[base._Constraint, ...],
    per_component: list[tuple[base._ComponentSolution, ...]],
    phases: tuple[int, ...],
    n_germs: int,
    counters: Counters,
) -> ShiftWitness | None:
    """Depth-first exact cover over per-component solutions.

    Complete: every combination is either visited or pruned by a rank
    collision inside a parallel class, which no extension could repair.
    """
    n_edges = len(data.edge_darts)
    assignments: dict[int, int] = {}
    masks: dict[ClassKey, int] = {}
    stack_result: list[ShiftWitness] = []

    def rec(index: int) -> bool:
        counters.dfs_nodes += 1
        if counters.dfs_nodes > MAX_DFS_NODES:
            raise AssertionError("combination closure exceeded its node cap")
        if index == len(per_component):
            counters.full_assignments_considered += 1
            if len(assignments) != n_edges or any(
                masks.get(key, 0).bit_count() != len(edges)
                for key, edges in data.class_edges.items()
            ):
                counters.union_cardinality_rejections += 1
                return False
            ranks = tuple(assignments[edge] for edge in range(n_edges))
            witness = replay_witness(data, scheme, constraints, phases, ranks,
                                     n_germs)
            if witness is None:
                counters.witness_replay_failures += 1
                return False
            stack_result.append(witness)
            return True
        for solution in per_component[index]:
            collision = False
            for key, mask in solution.class_masks:
                if masks.get(key, 0) & mask:
                    collision = True
                    break
            if collision:
                counters.dfs_prunes += 1
                continue
            for key, mask in solution.class_masks:
                masks[key] = masks.get(key, 0) | mask
            for edge, rank in solution.assignments:
                if edge in assignments:
                    raise AssertionError("constraint components share an A-edge")
                assignments[edge] = rank
            found = rec(index + 1)
            for edge, _ in solution.assignments:
                del assignments[edge]
            for key, mask in solution.class_masks:
                masks[key] ^= mask
            if found:
                return True
        return False

    if rec(0):
        return stack_result[0]
    return None


def solve_shift_family(
    words: tuple[str, ...],
    gens: str,
    shift_offsets: bool = True,
    macro_limit: int | None = None,
) -> ShiftDecision:
    """Decide compatible sphericity on BOOK / SPLIT_ENDPOINT support.

    `shift_offsets=False` and `macro_limit` exist ONLY for the corruption
    controls: they deliberately break Lemma C / Lemma B completeness.
    """
    words = tuple(words)
    family = classify_family(words, gens)
    counters = Counters()
    if family.kind == "UNSUPPORTED" or family.data is None:
        return ShiftDecision(words, gens, "UNSUPPORTED", None, family.kind,
                             family.reason, None, counters,
                             family.bundle_report, len(family.macro))
    data = family.data
    schemes = schemes_for(family, shift_offsets=shift_offsets)
    if macro_limit is not None:
        keep = {f"macro{i}" for i in range(macro_limit)}
        schemes = tuple(s for s in schemes if s.name.split("-")[0] in keep)
    constraints = constraints_of(data, len(gens))
    components = base._constraint_components(len(data.edge_darts), constraints)
    phase_ranges = [range(len(data.vertex_darts[2 * k])) for k in range(len(gens))]
    phase_budget = math.prod(len(r) for r in phase_ranges)
    seed_budget_per_phase = sum(
        len(data.class_edges[data.edge_class[component[0][0]]])
        for component in components
    )
    counters.scheme_budget = len(schemes)
    counters.phase_tuple_budget = len(schemes) * phase_budget
    counters.component_seed_budget = counters.phase_tuple_budget * seed_budget_per_phase

    for scheme in schemes:
        counters.schemes_considered += 1
        for phases in itertools.product(*phase_ranges):
            counters.phase_tuples_considered += 1
            per_component: list[tuple[base._ComponentSolution, ...]] = []
            for component in components:
                seed_edge = component[0][0]
                seed_domain = len(data.class_edges[data.edge_class[seed_edge]])
                solutions = []
                for seed_rank in range(seed_domain):
                    counters.component_seed_attempts += 1
                    solution, within = base._propagate_component(
                        data, scheme, constraints, component, phases, seed_rank
                    )
                    if within:
                        counters.within_cycle_collision_rejections += 1
                    elif solution is not None:
                        counters.closed_component_assignments += 1
                        solutions.append(solution)
                per_component.append(tuple(solutions))
            if any(not s for s in per_component):
                continue
            witness = _combine(data, scheme, constraints, per_component, phases,
                               family.n_germs, counters)
            if witness is not None:
                counters.exhaustive = False
                return ShiftDecision(
                    words, gens, "SPHERICAL_REQUIRES_REGINA", True, family.kind,
                    None, witness, counters, family.bundle_report,
                    len(family.macro),
                )

    counters.exhaustive = (
        counters.schemes_considered == counters.scheme_budget
        and counters.phase_tuples_considered == counters.phase_tuple_budget
        and counters.component_seed_attempts == counters.component_seed_budget
    )
    if not counters.exhaustive:
        raise AssertionError("negative shift-family search did not exhaust its budget")
    return ShiftDecision(words, gens, "NOT_SPHERICAL", False, family.kind, None,
                         None, counters, family.bundle_report, len(family.macro))


# ---------------------------------------------------------------------------
# brute force (independent oracle): all compatible orderings, exact genus
# ---------------------------------------------------------------------------


def brute_force_gamma(words: tuple[str, ...], gens: str, budget: int) -> dict:
    """Exhaustive gamma_N over every compatible ordering (a finite closure)."""
    link = rlg.build_link(tuple(words), gens)
    return rlg.neuwirth_min_genus(link, budget=budget, stop_at_zero=False)


def brute_force_all_spherical_rotations(
    words: tuple[str, ...], gens: str, budget: int
) -> int | None:
    """Count EVERY spherical rotation system of the link multigraph.

    No compatibility constraint: this is the count Lemma B predicts equals
    (#macro rotations) x prod_beta m_beta!.  Returns None past `budget`.
    """
    link = rlg.build_link(tuple(words), gens)
    data = link_data(link)
    n_germs = link.n_germs
    total = 1
    for vertex in range(n_germs):
        total *= math.factorial(max(0, len(data.vertex_darts[vertex]) - 1))
    if total > budget:
        return None
    per_vertex = []
    for vertex in range(n_germs):
        darts = list(data.vertex_darts[vertex])
        head, *tail = darts
        per_vertex.append([(head, *p) for p in itertools.permutations(tail)])
    count = 0
    for combo in itertools.product(*per_vertex):
        sigma = [-1] * len(data.A)
        for rotation in combo:
            for index, dart in enumerate(rotation):
                sigma[dart] = rotation[(index + 1) % len(rotation)]
        _, euler = faces_and_euler(data, sigma, n_germs)
        if euler == 2:
            count += 1
    return count


# ---------------------------------------------------------------------------
# pinned fixtures
# ---------------------------------------------------------------------------

# Every fixture below was found by a seeded random scan over short cyclically
# reduced words (seed 4242) and is pinned here so runs are reproducible.
# `gamma` is the EXACT gamma_N from a complete enumeration of all compatible
# orderings; the solver must agree with it (spherical iff gamma == 0).
CROSSCHECK: tuple[tuple[tuple[str, ...], str, int], ...] = (
    # BOOK, rank 2
    (("YYxYYx", "XyxxYX"), "xy", 1),
    (("yyyyx", "XXYxyy"), "xy", 1),
    (("yXXXXy", "XyXY"), "xy", 0),
    (("yyyx", "YxxxxY"), "xy", 0),
    (("YXyX", "XYYXX"), "xy", 0),
    # BOOK, rank 3
    (("YZyxZY", "Yxxyyx", "xYZ"), "xyz", 1),
    (("ZZXzY", "YYYY", "yyyxz"), "xyz", 1),
    (("zyxz", "ZYZxzy", "xZY"), "xyz", 0),
    (("yzYxZX", "YX", "Zxxy"), "xyz", 0),
    (("ZZxZ", "yx", "yxxzXy"), "xyz", 0),
    # SPLIT_ENDPOINT, rank 2
    (("yxyxxx", "xxxxx"), "xy", 1),
    (("xyxx", "yxyx"), "xy", 1),
    (("YXYX", "XYYYXY"), "xy", 0),
    (("XXXX", "xxyx"), "xy", 0),
    # SPLIT_ENDPOINT, rank 3
    (("Y", "zYYYY", "xzYYx"), "xyz", 1),
    (("xxx", "XX", "ZxYY"), "xyz", 1),
    (("zzyx", "yyyx", "YY"), "xyz", 0),
    (("Yxzx", "xY", "zzzz"), "xyz", 0),
    (("xzYzxz", "YX", "YY"), "xyz", 0),
    # the repo's own pinned calibrations (two_hop_cov_thickenability_certificate)
    (("yx", "yxXX"), "xy", 0),
    (("XYyyX", "X"), "xy", 1),
    (("x", "xxyxYy"), "xy", 0),
    # AK(3) itself: K4 support, 86,400 compatible orderings, gamma_N = 2
    (rlg.AK3, "xy", 2),
)

# Fixtures whose verdict FLIPS when a completeness lemma is broken.  Each
# corruption control asserts the flip, so a control that stops firing is a
# failure, not a pass.
FLIP_NO_SHIFT = (
    (("XXXX", "xxyx"), "xy"),
    (("zzyx", "yyyx", "YY"), "xyz"),
    (("Yxzx", "xY", "zzzz"), "xyz"),
)
FLIP_ONE_MACRO = (
    (("yzYxZX", "YX", "Zxxy"), "xyz"),
    (("ZZxZ", "yx", "yxxzXy"), "xyz"),
    (("xzYzxz", "YX", "YY"), "xyz"),
)

# Small enough for a complete enumeration of ALL rotation systems of the
# multigraph (Lemma B's bijection count).
LEMMA_B_FIXTURES = (
    (("YXyX", "XYYXX"), "xy"),
    (("yzYxZX", "YX", "Zxxy"), "xyz"),
    (("ZZxZ", "yx", "yxxzXy"), "xyz"),
    (("zzyx", "yyyx", "YY"), "xyz"),
    (("Yxzx", "xY", "zzzz"), "xyz"),
    (("xzYzxz", "YX", "YY"), "xyz"),
)

# The repo's two pinned P4 decisions (tests/stable_ac/test_neuwirth_p4_solver.py
# ::test_p4_positive_and_negative_match_factorial_replay).
REPO_P4_CASES = (("X", "XY"), ("X", "XXXYXY"))

# Tpub's own simple support, as a germ-labelled edge set, and Txy's.
TPUB_SIMPLE_SUPPORT = frozenset(
    {(0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (1, 5), (3, 4), (3, 5)}
)
TXY_SIMPLE_SUPPORT = frozenset(
    {(0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (1, 5), (3, 5)}
)

# TRUNCATED instances: the same macro structure as Tpub / Txy (identical or
# isomorphic simple support, hence the same four macro rotations and the same
# all-book bundle classification) but with bundle multiplicities small enough
# that EVERY compatible ordering can be enumerated directly.  `EXACT` carries
# Tpub's literal 9-edge support on the same germ ids.
TRUNCATED = (
    # tag, words, expected gamma_N
    ("exact_Tpub_support", ("YxyZ", "XYxz", "YxZx"), 1),
    ("iso_Tpub_support", ("zX", "yxzxxy", "XZyyxz"), 0),
    ("iso_Tpub_support", ("XZxyZY", "XZXX", "XYY"), 0),
    ("iso_Tpub_support", ("zyyy", "Xyzz", "xyzxZ"), 0),
    ("iso_Tpub_support", ("zYYzx", "yZxzyZ", "yXZZ"), 1),
    ("iso_Tpub_support", ("xzYXyy", "zYXyzy", "XXY"), 2),
    ("iso_Tpub_support", ("XXXZ", "zxYYY", "xYxxzy"), 1),
    ("iso_Txy_support", ("ZyxYX", "yxZX", "ZXyx"), 0),
    ("iso_Txy_support", ("ZxZYZX", "zYX", "zYX"), 0),
    ("iso_Txy_support", ("XZYzxY", "xyZY", "YxYX"), 1),
    ("iso_Txy_support", ("YzyX", "zzyyX", "YYZX"), 1),
)

A_WORD, B_WORD = rlg.A_WORD, rlg.B_WORD
TARGETS = (
    ("Txy_certified_AC_trivial", (A_WORD, B_WORD, rlg.K_XY), "xyz"),
    ("Tpub", (A_WORD, B_WORD, rlg.K_PUB), "xyz"),
    ("ak3_stabilized", (rlg.AK3[0], rlg.AK3[1], "z"), "xyz"),
    ("Q_stabilized", (rlg.Q[0], rlg.Q[1], "z"), "xyz"),
    ("ak3_rank2", rlg.AK3, "xy"),
    ("Q_rank2", rlg.Q, "xy"),
)


def decision_row(name: str, decision: ShiftDecision) -> dict:
    return {
        "name": name,
        "words": list(decision.words),
        "gens": decision.gens,
        "verdict": decision.verdict,
        "spherical": decision.spherical,
        "family": decision.family,
        "reason": decision.reason,
        "macro_rotations": decision.macro_rotation_count,
        "bundles": [dict(r) for r in decision.bundle_report],
        "counters": vars(decision.counters),
        "witness": (
            None if decision.witness is None else {
                "scheme": decision.witness.scheme,
                "shift": decision.witness.shift,
                "phases": list(decision.witness.phases),
                "face_count": decision.witness.face_count,
                "euler_characteristic": decision.witness.euler_characteristic,
                "genus": decision.witness.genus,
            }
        ),
        **decision.extras,
    }


# ---------------------------------------------------------------------------
# modes
# ---------------------------------------------------------------------------


def scheme_euler(
    data: base.LinkData, scheme: base.Scheme, ranks: tuple[int, ...], n_germs: int
) -> int:
    sigma = [-1] * len(data.A)
    for vertex in range(n_germs):
        rotation = tuple(
            sorted(
                data.vertex_darts[vertex],
                key=lambda dart: scheme.slots[dart][ranks[data.edge_of_dart[dart]]],
            )
        )
        for index, dart in enumerate(rotation):
            sigma[dart] = rotation[(index + 1) % len(rotation)]
    return faces_and_euler(data, sigma, n_germs)[1]


def independent_genus(
    link: rlg.Link, rotations: tuple[tuple[int, ...], ...]
) -> tuple[int, bool]:
    """Re-score a witness with `rank3_link_graph`'s own genus formula.

    Only the rotations at the POSITIVE germs are read; the negative germs'
    rotations are re-derived as the reversed `B`-image (the compatibility
    condition) and compared with what the witness claims.  Returns
    `(genus, b_reversal_recomputed)`.
    """
    n = len(link.A)
    C = [-1] * n
    compatible = True
    for k in range(len(link.gens)):
        order = rotations[2 * k]
        m = len(order)
        for i, dart in enumerate(order):
            C[dart] = order[(i + 1) % m]
        reversed_image = [link.B[dart] for dart in reversed(order)]
        for i, dart in enumerate(reversed_image):
            C[dart] = reversed_image[(i + 1) % m]
        if not base._cyclically_equal(tuple(reversed_image), rotations[2 * k + 1]):
            compatible = False
    if min(C) < 0:
        raise AssertionError("witness rotations do not cover every dart")
    AC = [link.A[C[dart]] for dart in range(n)]
    genus_twice = (
        n // 2 - 2 * len(link.gens) + 2 * len(rlg.components(link))
        - rlg._cycle_count(AC)
    )
    if genus_twice < 0 or genus_twice % 2:
        raise AssertionError("genus defect must be an even non-negative number")
    return genus_twice // 2, compatible


def identity_ranks(data: base.LinkData) -> tuple[int, ...]:
    ranks = [0] * len(data.edge_darts)
    for edges in data.class_edges.values():
        for rank, edge in enumerate(edges):
            ranks[edge] = rank
    return tuple(ranks)


def run_controls() -> dict:
    record: dict = {}

    # (1) dictionary agreement with the repo's certified rank-2 builder
    rows = []
    for words in (rlg.AK3, rlg.Q, ("yx", "yxXX"), ("XYyyX", "X"), ("x", "xxyxYy")):
        mine = link_data(rlg.build_link(words, "xy"))
        theirs = base._build_link_data(tuple(words))
        same = (
            mine.A == theirs.A and mine.B == theirs.B and mine.germ == theirs.germ
            and mine.edge_of_dart == theirs.edge_of_dart
            and mine.edge_darts == theirs.edge_darts
            and mine.edge_class == theirs.edge_class
            and dict(mine.class_edges) == dict(theirs.class_edges)
            and {k: v for k, v in mine.vertex_darts.items() if k < 4}
            == dict(theirs.vertex_darts)
        )
        check(f"link data matches the repo builder {words}", same)
        rows.append({"words": list(words), "identical": same})
    record["dictionary_agreement"] = rows

    # (1b) the RANK-THREE dictionary, against the repo's independent rank-3
    # builder (neuwirth_rank3_rigid_solver, alphabet x,z,t -> the same germ
    # ids).  Without this the rank-3 dart dictionary would only ever be
    # checked against itself, and the brute-force oracle shares it.
    from experiments.stable_ac.thickenable import (
        neuwirth_rank3_rigid_solver as rigid,
    )

    table = str.maketrans("xyzXYZ", "xztXZT")
    rows = []
    for name, words, gens in TARGETS:
        if gens != "xyz":
            continue
        mine = link_data(rlg.build_link(words, gens))
        theirs = rigid._build_link_data(tuple(w.translate(table) for w in words))
        same = (
            mine.A == theirs.A and mine.B == theirs.B and mine.germ == theirs.germ
            and mine.edge_of_dart == theirs.edge_of_dart
            and mine.edge_darts == theirs.edge_darts
            and mine.edge_class == theirs.edge_class
            and dict(mine.class_edges) == dict(theirs.class_edges)
            and dict(mine.vertex_darts) == dict(theirs.vertex_darts)
        )
        check(f"rank-3 link data matches the repo rigid builder: {name}", same)
        rows.append({"name": name, "identical": same})
    record["rank3_dictionary_agreement"] = rows

    # (2) Lemma B: #spherical rotation systems of G == #macro x prod m!
    rows = []
    for words, gens in LEMMA_B_FIXTURES:
        family = classify_family(words, gens)
        data = family.data
        assert data is not None
        predicted = len(family.macro)
        for edges in data.class_edges.values():
            predicted *= math.factorial(len(edges))
        counted = brute_force_all_spherical_rotations(words, gens, 3_000_000)
        ok = counted is not None and counted == predicted and family.kind == "BOOK"
        if family.kind != "BOOK":
            # Lemma B is stated for book support only; SPLIT_ENDPOINT gets
            # m extra shifts, so the predicted count is multiplied by m.
            predicted_split = predicted * family.split_multiplicity
            ok = counted is not None and counted == predicted_split
            predicted = predicted_split
        check(
            f"Lemma B blow-up count {words} ({family.kind})", bool(ok),
            f"counted={counted} predicted={predicted}",
        )
        rows.append({"words": list(words), "gens": gens, "family": family.kind,
                     "macro_rotations": len(family.macro),
                     "counted_spherical_rotation_systems": counted,
                     "predicted": predicted, "agrees": bool(ok)})
    record["lemma_b_bijection"] = rows

    # (3) every scheme really is a spherical shape (Euler characteristic 2)
    rows = []
    for name, words, gens in TARGETS:
        family = classify_family(words, gens)
        if family.kind == "UNSUPPORTED" or family.data is None:
            continue
        ranks = identity_ranks(family.data)
        eulers = [
            scheme_euler(family.data, scheme, ranks, family.n_germs)
            for scheme in schemes_for(family)
        ]
        ok = all(value == 2 for value in eulers)
        check(f"every scheme of {name} traces a sphere", ok, f"eulers={set(eulers)}")
        rows.append({"name": name, "schemes": len(eulers),
                     "euler_characteristics": sorted(set(eulers))})
    record["scheme_sphericity"] = rows

    # (4) Lemma D (gauge): a cyclic re-gauge of one germ's slots is inert
    rows = []
    for words, gens, gamma in CROSSCHECK[:8]:
        family = classify_family(words, gens)
        data = family.data
        assert data is not None
        constraints = constraints_of(data, len(gens))
        components = base._constraint_components(len(data.edge_darts), constraints)
        phase_ranges = [range(len(data.vertex_darts[2 * k])) for k in range(len(gens))]
        base_hit = None
        gauged_hit = None
        for gauge in (0, 1):
            hit = False
            for scheme in schemes_for(family):
                slots = [list(row) for row in scheme.slots]
                if gauge:
                    vertex = 0
                    degree = len(data.vertex_darts[vertex])
                    for dart in data.vertex_darts[vertex]:
                        slots[dart][:] = [(s + 1) % degree for s in slots[dart]]
                shifted = base.Scheme(scheme.name, scheme.support_kind, scheme.cut,
                                      tuple(map(tuple, slots)), True)
                for phases in itertools.product(*phase_ranges):
                    per = []
                    for component in components:
                        seed_edge = component[0][0]
                        domain = len(data.class_edges[data.edge_class[seed_edge]])
                        sols = []
                        for seed in range(domain):
                            sol, within = base._propagate_component(
                                data, shifted, constraints, component, phases, seed)
                            if sol is not None and not within:
                                sols.append(sol)
                        per.append(tuple(sols))
                    if any(not s for s in per):
                        continue
                    counters = Counters()
                    if _combine(data, shifted, constraints, per, phases,
                                family.n_germs, counters) is not None:
                        hit = True
                        break
                if hit:
                    break
            if gauge:
                gauged_hit = hit
            else:
                base_hit = hit
        ok = base_hit == gauged_hit and base_hit == (gamma == 0)
        check(f"Lemma D gauge invariance {words}", ok,
              f"base={base_hit} gauged={gauged_hit} gamma={gamma}")
        rows.append({"words": list(words), "base": base_hit, "regauged": gauged_hit,
                     "gamma_N": gamma})
    record["lemma_d_gauge"] = rows

    # (5) corruption control: break Lemma C's shift completeness
    rows = []
    flipped = 0
    for words, gens in FLIP_NO_SHIFT:
        full = solve_shift_family(words, gens)
        broken = solve_shift_family(words, gens, shift_offsets=False)
        flip = full.spherical is True and broken.spherical is not True
        flipped += bool(flip)
        rows.append({"words": list(words), "full": full.verdict,
                     "shift_0_only": broken.verdict, "flipped": flip})
    check("broken shift-completeness flips a verdict", flipped == len(FLIP_NO_SHIFT),
          f"{flipped}/{len(FLIP_NO_SHIFT)}")
    record["corruption_shift_completeness"] = rows

    # (6) corruption control: break Lemma B's macro completeness
    rows = []
    flipped = 0
    for words, gens in FLIP_ONE_MACRO:
        full = solve_shift_family(words, gens)
        broken = solve_shift_family(words, gens, macro_limit=1)
        flip = full.spherical is True and broken.spherical is not True
        flipped += bool(flip)
        rows.append({"words": list(words), "full": full.verdict,
                     "one_macro_only": broken.verdict, "flipped": flip})
    check("broken macro-completeness flips a verdict", flipped == len(FLIP_ONE_MACRO),
          f"{flipped}/{len(FLIP_ONE_MACRO)}")
    record["corruption_macro_completeness"] = rows

    # (7) corruption control: corrupt the genus computation itself
    global faces_and_euler
    honest = faces_and_euler
    positive = (("zyxz", "ZYZxzy", "xZY"), "xyz")
    before = solve_shift_family(*positive)

    def off_by_one(data, sigma, n_germs):
        faces, euler = honest(data, sigma, n_germs)
        return faces, euler + 1

    faces_and_euler = off_by_one
    try:
        after = solve_shift_family(*positive)
    finally:
        faces_and_euler = honest
    check("corrupted Euler characteristic flips a positive to NOT_SPHERICAL",
          before.spherical is True and after.spherical is False,
          f"{before.verdict} -> {after.verdict}")

    # Measured, and worth recording: on this family a NEGATIVE never reaches
    # the replay stage -- the phase propagation closes every (scheme, phase)
    # case first -- so an "accept every trace" corruption is INERT on
    # negatives and cannot be used as a control there.  The genus computation
    # is load-bearing on positives (the off-by-one control above) and is
    # cross-checked against rank3_link_graph's independent formula below.
    replay_reached = {
        "negatives_examined": 0, "negatives_reaching_a_full_assignment": 0
    }
    for words, gens, gamma in CROSSCHECK:
        if gamma == 0:
            continue
        decision = solve_shift_family(words, gens)
        replay_reached["negatives_examined"] += 1
        if decision.counters.full_assignments_considered > 0:
            replay_reached["negatives_reaching_a_full_assignment"] += 1
    record["corruption_genus"] = {
        "positive_instance": [list(positive[0]), positive[1]],
        "verdict_before": before.verdict, "verdict_after_offset": after.verdict,
        "replay_reachability_on_negatives": replay_reached,
    }

    # (7b) corruption control: break Lemma B(iii), the bundle reversal
    global REVERSE_BUNDLE_BLOCKS
    flips = []
    REVERSE_BUNDLE_BLOCKS = False
    try:
        for words, gens, gamma in CROSSCHECK:
            broken = solve_shift_family(words, gens)
            if (broken.spherical is True) != (gamma == 0):
                flips.append({"words": list(words), "gens": gens,
                              "true_gamma_N": gamma, "broken": broken.verdict})
    finally:
        REVERSE_BUNDLE_BLOCKS = True
    check("dropping the bundle reversal (Lemma B(iii)) moves verdicts",
          len(flips) > 0, f"{len(flips)} of {len(CROSSCHECK)} fixtures move")
    record["corruption_bundle_reversal"] = {"moved": flips}

    # (7c) every positive witness is re-scored by rank3_link_graph's own
    # genus formula -- a different code path, on the rotations alone
    rows = []
    scored = 0
    for words, gens, gamma in CROSSCHECK:
        if gamma != 0:
            continue
        decision = solve_shift_family(words, gens)
        if decision.spherical is None:
            # outside the family (the repo calibrations carry link loops):
            # failing closed is the correct behaviour, nothing to re-score
            rows.append({"words": list(words), "gens": gens,
                         "skipped": decision.reason})
            continue
        if decision.witness is None:
            check(f"positive fixture produced a witness {words}", False)
            continue
        link = rlg.build_link(words, gens)
        genus, compatible = independent_genus(link, decision.witness.rotations)
        scored += 1
        ok = genus == 0 and compatible
        check(f"witness re-scored by rank3_link_graph {words}", ok,
              f"genus={genus} compatible={compatible}")
        rows.append({"words": list(words), "gens": gens,
                     "independent_genus": genus,
                     "b_reversal_recomputed": compatible})
    check("witness re-scoring control is not vacuous", scored > 0, f"{scored} scored")
    record["independent_witness_rescoring"] = rows

    # (8) fail closed outside the family
    rows = []
    for name, words, gens in TARGETS:
        decision = solve_shift_family(words, gens)
        rows.append({"name": name, "family": decision.family,
                     "verdict": decision.verdict, "reason": decision.reason})
    for name, expected in (("ak3_stabilized", "UNSUPPORTED"),
                           ("Q_stabilized", "UNSUPPORTED"),
                           ("Q_rank2", "UNSUPPORTED")):
        row = next(r for r in rows if r["name"] == name)
        check(f"fails closed on {name}", row["verdict"] == expected,
              str(row["reason"]))
    record["fail_closed"] = rows
    return record


def run_crosscheck(genus_budget: int, sweep: int, seed: int) -> dict:
    rows = []
    for words, gens, gamma in CROSSCHECK:
        decision = solve_shift_family(words, gens)
        brute = brute_force_gamma(words, gens, genus_budget)
        pinned_ok = brute.get("gamma_N") == gamma
        check(f"pinned gamma_N {words}", pinned_ok,
              f"{brute.get('gamma_N')} vs {gamma}")
        agrees: bool | None = None
        if decision.spherical is None:
            # the three repo calibrations carry link loops and are outside
            # the family by construction; fail-closed is the right answer and
            # there is nothing to agree or disagree with
            check(f"fails closed with a reason {words}",
                  bool(decision.reason), str(decision.reason))
        else:
            agrees = (decision.spherical is True) == (brute.get("gamma_N") == 0)
            check(f"solver == brute force {words}", agrees,
                  f"{decision.verdict} vs gamma_N={brute.get('gamma_N')}")
            if decision.spherical is False:
                check(f"negative is exhaustive {words}",
                      decision.counters.exhaustive)
        rows.append({"words": list(words), "gens": gens,
                     "pinned_gamma_N": gamma, "brute_gamma_N": brute.get("gamma_N"),
                     "compatible_orderings": brute.get("cases"),
                     "verdict": decision.verdict, "reason": decision.reason,
                     "agrees": agrees,
                     "exhaustive": decision.counters.exhaustive})

    # a seeded random sweep: many more chances for the solver to disagree
    import random

    rng = random.Random(seed)
    alphabet = {"xy": "xXyY", "xyz": "xXyYzZ"}
    tested = 0
    disagreements = []
    kinds: dict[str, int] = {}
    attempts = 0
    while tested < sweep and attempts < 200 * sweep:
        attempts += 1
        gens = "xy" if attempts % 2 else "xyz"
        words = []
        for _ in range(len(gens)):
            word = rlg.cyclic_reduce(
                "".join(rng.choice(alphabet[gens]) for _ in range(rng.randint(1, 6)))
            )
            if not word:
                break
            words.append(word)
        if len(words) != len(gens):
            continue
        words = tuple(words)
        family = classify_family(words, gens)
        if family.kind == "UNSUPPORTED":
            continue
        link = rlg.build_link(words, gens)
        cases = rlg.compatible_case_count(link)
        if cases > 20_000 or cases < 4:
            continue
        brute = rlg.neuwirth_min_genus(link, budget=20_000, stop_at_zero=False)
        decision = solve_shift_family(words, gens)
        tested += 1
        kinds[family.kind] = kinds.get(family.kind, 0) + 1
        if (decision.spherical is True) != (brute["gamma_N"] == 0):
            disagreements.append(
                {"words": list(words), "gens": gens, "family": family.kind,
                 "verdict": decision.verdict, "gamma_N": brute["gamma_N"]}
            )
    check(f"seeded sweep: {tested} instances, solver == brute force everywhere",
          not disagreements, f"kinds={kinds} disagreements={disagreements[:3]}")
    return {"pinned": rows, "sweep": {"seed": seed, "tested": tested,
                                      "family_counts": kinds,
                                      "disagreements": disagreements}}


def run_repo_agreement() -> dict:
    from experiments.stable_ac.thickenable.neuwirth_p4_solver import (
        solve_four_germ_spherical,
    )
    from experiments.stable_ac.thickenable.neuwirth_permutation_certificate import (
        enumerate_trace,
    )
    from experiments.stable_ac.thickenable.neuwirth_rank_solver import solve_spherical

    rows = []
    for words in REPO_P4_CASES:
        repo = solve_four_germ_spherical(words)
        factorial = enumerate_trace(words)
        mine = solve_shift_family(words, "xy")
        repo_verdict = (
            "UNSUPPORTED" if repo.spherical is None
            else ("SPHERICAL_REQUIRES_REGINA" if repo.spherical else "NOT_SPHERICAL")
        )
        agrees = (mine.spherical is True) == bool(repo.spherical)
        check(f"repo P4 decision reproduced {words}", agrees,
              f"mine={mine.verdict} repo={repo_verdict} "
              f"factorial={bool(factorial.accepting_orders)}")
        check(f"repo P4 factorial replay agrees {words}",
              bool(repo.spherical) == bool(factorial.accepting_orders))
        rows.append({"words": list(words), "repo_support": repo.support.kind,
                     "repo_verdict": repo_verdict, "my_family": mine.family,
                     "my_verdict": mine.verdict,
                     "factorial_accepting": len(factorial.accepting_orders),
                     "agrees": agrees})

    # a broader agreement sweep against whichever certified rank-2 solver applies
    import random

    rng = random.Random(90210)
    sweep = []
    disagreements = []
    attempts = 0
    while len(sweep) < 120 and attempts < 40_000:
        attempts += 1
        words = []
        for _ in range(2):
            word = rlg.cyclic_reduce(
                "".join(rng.choice("xXyY") for _ in range(rng.randint(1, 6)))
            )
            if not word:
                break
            words.append(word)
        if len(words) != 2:
            continue
        words = tuple(words)
        mine = solve_shift_family(words, "xy")
        if mine.spherical is None:
            continue
        repo = solve_spherical(words)
        if repo.spherical is None:
            repo = solve_four_germ_spherical(words)
        if repo.spherical is None:
            continue
        agrees = (mine.spherical is True) == bool(repo.spherical)
        row = {"words": list(words), "repo_support": repo.support.kind,
               "repo_spherical": repo.spherical, "my_family": mine.family,
               "my_spherical": mine.spherical, "agrees": agrees}
        sweep.append(row)
        if not agrees:
            disagreements.append(row)
    supports: dict[str, int] = {}
    for row in sweep:
        supports[row["repo_support"]] = supports.get(row["repo_support"], 0) + 1
    check(f"certified rank-2 ladder agreement on {len(sweep)} instances",
          not disagreements, f"supports={supports} bad={disagreements[:3]}")
    return {"pinned_p4": rows,
            "sweep": {"tested": len(sweep), "repo_supports": supports,
                      "disagreements": disagreements}}


def support_isomorphic(
    simple: frozenset[ClassKey], target: frozenset[ClassKey]
) -> bool:
    if len(simple) != len(target):
        return False
    for perm in itertools.permutations(range(6)):
        relabelled = frozenset(
            tuple(sorted((perm[a], perm[b]))) for a, b in simple
        )
        if relabelled == target:
            return True
    return False


def run_truncated(genus_budget: int, sweep: int, seed: int) -> dict:
    """Brute-force cross-check restricted to Tpub's / Txy's macro structure.

    Tpub itself has 2.09e16 compatible orderings, so it cannot be brute
    forced.  These instances have the SAME simple support (identically
    labelled for `exact_Tpub_support`, isomorphic otherwise), hence the same
    four macro rotations and the same all-book bundle classification, with
    multiplicities small enough for a complete enumeration.
    """
    rows = []
    for tag, words, gamma in TRUNCATED:
        words = tuple(words)
        link = rlg.build_link(words, "xyz")
        simple, _ = rlg.simple_support(link)
        if tag == "exact_Tpub_support":
            check(f"{tag} really carries Tpub's simple support {words}",
                  frozenset(simple) == TPUB_SIMPLE_SUPPORT)
        elif tag == "iso_Tpub_support":
            check(f"{tag} is isomorphic to Tpub's simple support {words}",
                  support_isomorphic(frozenset(simple), TPUB_SIMPLE_SUPPORT))
        else:
            check(f"{tag} is isomorphic to Txy's simple support {words}",
                  support_isomorphic(frozenset(simple), TXY_SIMPLE_SUPPORT))
        decision = solve_shift_family(words, "xyz")
        brute = rlg.neuwirth_min_genus(link, budget=genus_budget,
                                       stop_at_zero=False)
        check(f"{tag} pinned gamma_N {words}", brute.get("gamma_N") == gamma,
              f"{brute.get('gamma_N')} vs {gamma}")
        agrees = (decision.spherical is True) == (brute.get("gamma_N") == 0)
        check(f"{tag} solver == brute force {words}", agrees,
              f"{decision.verdict} vs gamma_N={brute.get('gamma_N')}")
        check(f"{tag} same family as Tpub (BOOK, four macro rotations) {words}",
              decision.family == "BOOK" and decision.macro_rotation_count == 4,
              f"{decision.family}, macro={decision.macro_rotation_count}")
        rows.append({"tag": tag, "words": list(words),
                     "compatible_orderings": brute.get("cases"),
                     "brute_gamma_N": brute.get("gamma_N"),
                     "verdict": decision.verdict, "family": decision.family,
                     "macro_rotations": decision.macro_rotation_count,
                     "agrees": agrees})

    import random

    rng = random.Random(seed)
    tested = 0
    attempts = 0
    disagreements = []
    tally = {"iso_Tpub": 0, "iso_Txy": 0, "gamma_0": 0, "gamma_positive": 0}
    while tested < sweep and attempts < 400_000:
        attempts += 1
        words = []
        for _ in range(3):
            word = rlg.cyclic_reduce(
                "".join(rng.choice("xXyYzZ") for _ in range(rng.randint(2, 6)))
            )
            if not word:
                break
            words.append(word)
        if len(words) != 3:
            continue
        words = tuple(words)
        try:
            link = rlg.build_link(words, "xyz")
        except ValueError:
            continue
        simple, loops = rlg.simple_support(link)
        if loops or len(rlg.components(link)) != 1:
            continue
        if len(rlg.active_germs(link)) != 6:
            continue
        cases = rlg.compatible_case_count(link)
        if not 24 <= cases <= 6_000:
            continue
        is_tpub = support_isomorphic(frozenset(simple), TPUB_SIMPLE_SUPPORT)
        is_txy = support_isomorphic(frozenset(simple), TXY_SIMPLE_SUPPORT)
        if not (is_tpub or is_txy):
            continue
        decision = solve_shift_family(words, "xyz")
        if decision.spherical is None:
            continue
        brute = rlg.neuwirth_min_genus(link, budget=6_000, stop_at_zero=False)
        tested += 1
        tally["iso_Tpub" if is_tpub else "iso_Txy"] += 1
        tally["gamma_0" if brute["gamma_N"] == 0 else "gamma_positive"] += 1
        if (decision.spherical is True) != (brute["gamma_N"] == 0):
            disagreements.append({"words": list(words),
                                  "verdict": decision.verdict,
                                  "gamma_N": brute["gamma_N"]})
    check(f"Tpub-support sweep: {tested} instances, solver == brute force",
          not disagreements and tested >= 20,
          f"{tally} disagreements={disagreements[:3]}")
    check("Tpub-support sweep saw BOTH verdicts (not a one-sided null)",
          tally["gamma_0"] > 0 and tally["gamma_positive"] > 0, str(tally))
    return {"pinned": rows,
            "sweep": {"seed": seed, "tested": tested, "tally": tally,
                      "disagreements": disagreements}}


def run_ball_coverage(ceiling: int, slice_seconds: float) -> dict:
    """How much of W6's closed rank-three AC ball does this family decide?

    Reads the state list from `out/w6_ac_ball_c{ceiling}.json` (produced by
    `rank3_link_graph.py ball`, under the 1,000-pop law) and classifies every
    state.  Sliced and resumable: rows append to
    `out/w6b_ball_coverage_c{ceiling}.jsonl` keyed by the state, and a rerun
    skips states already done, so a guard kill is a pause, not a restart.
    """
    import time

    source = OUT / f"w6_ac_ball_c{ceiling}.json"
    if not source.exists():
        raise SystemExit(f"missing {source}; run rank3_link_graph.py ball first")
    ball = json.loads(source.read_text())
    states = [tuple(row["state"]) for row in ball["states"] if "state" in row]
    path = OUT / f"w6b_ball_coverage_c{ceiling}.jsonl"
    done: dict[tuple[str, ...], dict] = {}
    if path.exists():
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            done[tuple(row["state"])] = row
    started = time.monotonic()
    appended = 0
    with path.open("a") as handle:
        for state in states:
            if state in done:
                continue
            if time.monotonic() - started > slice_seconds:
                break
            decision = solve_shift_family(state, "xyz")
            row = {"state": list(state),
                   "total_length": sum(map(len, state)),
                   "family": decision.family,
                   "verdict": decision.verdict,
                   "reason": decision.reason,
                   "macro_rotations": decision.macro_rotation_count,
                   "exhaustive": decision.counters.exhaustive}
            handle.write(json.dumps(row, sort_keys=True) + "\n")
            handle.flush()
            done[state] = row
            appended += 1
    families: dict[str, int] = {}
    verdicts: dict[str, int] = {}
    reasons: dict[str, int] = {}
    for row in done.values():
        families[row["family"]] = families.get(row["family"], 0) + 1
        verdicts[row["verdict"]] = verdicts.get(row["verdict"], 0) + 1
        if row["reason"]:
            reasons[row["reason"]] = reasons.get(row["reason"], 0) + 1
    positives = [r["state"] for r in done.values()
                 if r["verdict"].startswith("SPHERICAL")]
    decided = sum(v for k, v in verdicts.items() if k != "UNSUPPORTED")
    print(f"  ceiling {ceiling}: {len(done)}/{len(states)} states classified, "
          f"appended {appended} this slice")
    print(f"  families={families}")
    print(f"  verdicts={verdicts}")
    print(f"  unsupported reasons={reasons}")
    if positives:
        print("  *** SPHERICAL_REQUIRES_REGINA / quarantined-suspected-bug on "
              f"{len(positives)} ball states ***")
    for row in done.values():
        if row["verdict"] == "NOT_SPHERICAL" and not row["exhaustive"]:
            raise AssertionError(f"non-exhaustive negative on {row['state']}")
    return {"ceiling": ceiling, "ball_states": len(states),
            "classified": len(done), "complete": len(done) == len(states),
            "family_counts": families, "verdict_counts": verdicts,
            "unsupported_reasons": reasons,
            "decided": decided,
            "quarantined_positive_states": positives,
            "jsonl": str(path)}


def run_targets(genus_budget: int) -> dict:
    rows = []
    for name, words, gens in TARGETS:
        decision = solve_shift_family(words, gens)
        row = decision_row(name, decision)
        link = rlg.build_link(words, gens)
        try:
            row["compatible_orderings"] = rlg.compatible_case_count(link)
        except ValueError as exc:
            row["compatible_orderings"] = f"undefined: {exc}"
        brute = rlg.neuwirth_min_genus(link, budget=genus_budget, stop_at_zero=False)
        row["brute_force_gamma_N"] = brute.get("gamma_N")
        row["brute_force_decided"] = brute.get("decided")
        if decision.spherical is False:
            connected = len(rlg.components(link)) == 1
            row["link_connected"] = connected
            row["claim"] = (
                "NOT THICKENABLE for this exact spelling (gamma_N > 0). "
                + ("The link graph is CONNECTED, so AK3_NEUWIRTH Theorem 2 "
                   "applies as an equivalence (thickenable iff gamma_N = 0); "
                   "the negative does not rest on the necessity half alone."
                   if connected else
                   "The link graph is disconnected, so only the necessity "
                   "half (W6 Lemma W6.3) is available -- which is all a "
                   "negative needs.")
            )
            if not decision.counters.exhaustive:
                raise AssertionError(f"non-exhaustive negative on {name}")
        elif decision.spherical is True:
            row["claim"] = (
                "SPHERICAL_REQUIRES_REGINA / quarantined-suspected-bug: "
                "Pipeline B (Regina isBall) is absent; NOT a result"
            )
        else:
            row["claim"] = "UNSUPPORTED by this family; no claim"
        if brute.get("decided") and decision.spherical is not None:
            agrees = (decision.spherical is True) == (brute["gamma_N"] == 0)
            check(f"target {name}: solver == brute force", agrees)
            row["agrees_with_brute_force"] = agrees
        rows.append(row)
        print(f"  {name:26s} family={decision.family:15s} "
              f"macro={decision.macro_rotation_count} "
              f"schemes={decision.counters.scheme_budget} "
              f"phases={decision.counters.phase_tuple_budget} "
              f"-> {decision.verdict}")
    quarantined = [r["name"] for r in rows if r["spherical"] is True]
    if quarantined:
        print("  *** SPHERICAL_REQUIRES_REGINA / quarantined-suspected-bug: "
              f"{quarantined} ***")
    return {"targets": rows, "quarantined_positives": quarantined}


def main() -> int:
    parser = argparse.ArgumentParser(description="W6b shift-family solver")
    parser.add_argument("mode", choices=("controls", "crosscheck",
                                         "repo-agreement", "truncated",
                                         "ball-coverage", "targets"))
    parser.add_argument("--genus-budget", type=int, default=100_000)
    parser.add_argument("--sweep", type=int, default=250)
    parser.add_argument("--seed", type=int, default=4242)
    parser.add_argument("--ceiling", type=int, default=20)
    parser.add_argument("--slice-seconds", type=float, default=42.0)
    parser.add_argument("--out", type=str, default=None)
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.mode == "controls":
        data = run_controls()
        path = OUT / "w6b_controls.json"
    elif args.mode == "crosscheck":
        data = run_crosscheck(args.genus_budget, args.sweep, args.seed)
        path = OUT / "w6b_bruteforce_crosscheck.json"
    elif args.mode == "repo-agreement":
        data = run_repo_agreement()
        path = OUT / "w6b_repo_agreement.json"
    elif args.mode == "ball-coverage":
        data = run_ball_coverage(args.ceiling, args.slice_seconds)
        path = OUT / f"w6b_ball_coverage_c{args.ceiling}.json"
    elif args.mode == "truncated":
        data = run_truncated(args.genus_budget, args.sweep, args.seed)
        path = OUT / "w6b_truncated_tpub_support.json"
    else:
        data = run_targets(args.genus_budget)
        path = OUT / "w6b_targets.json"
    if args.out:
        path = Path(args.out)
    data["_fails"] = FAILS
    path.write_text(json.dumps(data, indent=2, sort_keys=True, default=str) + "\n")
    print(f"wrote {path}")
    if FAILS:
        print(f"FAILURES: {FAILS}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
