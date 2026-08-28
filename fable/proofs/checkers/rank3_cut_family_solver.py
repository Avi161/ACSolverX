"""W6c: the CUT family — a certified rank-general Neuwirth solver for support in
which one parallel bundle's complement splits into two pieces that each touch
both endpoints (the rank-three `K4-e` shape).

This is the family `W6B_TPUB_DECISION.md` §8 named as the next decisive step.
It extends `rank3_shift_family_solver` (imported, never forked: the link
dictionary, the constraint/propagation/replay kernel, the macro enumeration,
the BOOK and SPLIT_ENDPOINT paths and their fixtures all come from there) with
the one scheme parameter those families do not have — a *cut*.

WHAT IS PROVEN AND WHAT IS ENUMERATED
=====================================

Setting is W6b's verbatim.  `G` is the occurrence link multigraph
(`rank3_link_graph.build_link`), `H` its simple support, a *bundle*
`beta = {u,v}` a parallel class of multiplicity `m_beta`, and `pieces(beta)`
the connected components of `H - {u,v}`.

    Family CUT.  `G` is connected and loopless, every generator occurs,
    exactly one bundle `beta = {u,v}` with `m_beta = m >= 2` has
    `|pieces(beta)| = 2` with BOTH pieces meeting BOTH of `u` and `v`, and
    every other bundle of multiplicity >= 2 has `|pieces| = 1` (i.e. is BOOK
    in the sense of W6b Lemma B).

Lemma A (bundle regions) — PROVEN in W6b, reused verbatim.
    The `m` arcs of a bundle cut `S^2` into exactly `m` regions and each
    component of `G - {u,v}` lies in the closure of exactly one of them.

Lemma G (piece contraction) — PROVEN.  *This is what changes with two pieces.*
    Let `G` be embedded in `S^2` and let `beta = {u,v}` be any bundle.  Write
    `P_1, ..., P_k` for the pieces.  Contracting each `P_i` to a single vertex
    `p_i` is a sequence of contractions of non-loop edges of an embedded
    graph, so it preserves the genus and preserves the cyclic order of the
    darts at `u` and at `v`.  The contracted graph `G/P` is the multigraph on
    `{u, v, p_1, ..., p_k}` with `m` parallel `u-v` edges and, for each `i`,
    `a_i >= 0` edges `u-p_i` and `b_i >= 0` edges `v-p_i`, and no `p_i-p_j`
    edge (distinct pieces are non-adjacent in `H - {u,v}`).
    In `G/P` the bundle `{u, p_i}` has `(G/P) - {u, p_i}` connected whenever
    some other piece or `v` remains attached, so W6b Lemma B applies to it:
    **the darts from `u` into `P_i` are consecutive in the rotation at `u`**,
    and likewise at `v`.  (Contraction preserved that cyclic order, so the
    statement is about `G` itself.)

Lemma H (cut decoupling) — PROVEN.  *The completeness lemma of this family.*
    Assume family CUT, with pieces `P_1, P_2` both meeting both endpoints.
    In EVERY spherical rotation system of `G`:
      (i)   every bundle other than `beta` is book, exactly as in W6b Lemma B,
            so deleting `m_gamma - 1` edges from each of them is deletion of
            non-bridges, preserves sphericity, and the `G`-rotation is
            recovered from the reduced rotation by re-inserting each such
            bundle as one contiguous block;
      (ii)  at `u` the darts into `P_1` form one contiguous block `D_1` and
            the darts into `P_2` a contiguous block `D_2` (Lemma G), and the
            `m` arcs of `beta` occupy the two remaining gaps, in runs of
            sizes `s` and `m - s` for some `s in {0,...,m}`; likewise at `v`;
      (iii) deleting all but one arc of `beta` as well leaves a spherical
            rotation system of `H`, whose rotation at `u` is
            `(D_1, arc, D_2)` or `(D_1, D_2, arc)` — in either case its
            *arc-deleted* cyclic order at `u` is `(D_1, D_2)` with the same
            internal orders, and the same at `v`.
    Hence every spherical rotation system of `G` is obtained from some
    spherical rotation system `rho` of `H` (a *macro rotation*, enumerated
    exactly as in W6b) by: blowing up every non-`beta` bundle as one block in
    `rho`-order; reading `rho`'s arc-deleted order at `u` and at `v` as
    `(D_1, D_2)`; and inserting the `m` arcs of `beta` into the two gaps at
    each endpoint.  The insertion is described by a *cut* parameter and the
    order of the arcs inside each run — a finite set, enumerated in full
    below.  The freedom Lemma B removed at a book bundle is exactly this cut;
    the freedom Lemma C (endpoint split) gave back was a single offset
    `t in Z_m` because one of `D_1`, `D_2` is empty at each end there, so the
    two gaps merge into one.  **With two pieces touching both endpoints, both
    gaps are real at both ends, and the cut is the parameter.**

    NOTE what Lemma H does *not* claim: it does not claim that every
    (macro, cut) combination is spherical.  It claims the converse inclusion —
    that every spherical rotation system appears in the enumerated set.  A
    generated shape that is not spherical can never carry a witness (the
    replay recomputes the Euler characteristic and rejects), so the solver
    discards it up front; that discard is lossless because the Euler
    characteristic of a scheme is invariant under the rank assignment
    (permuting ranks inside a parallel class relabels edges at both endpoints
    simultaneously, an isomorphism of the embedded graph).

Lemma F (bare-row splitting) — PROVEN; W6 Lemma W6.1 stated for a general
generator instead of `z`.
    Let `P = <g_1..g_n | r_1..r_n>` and suppose some generator `g` occurs in
    exactly one relator, that relator being the one-letter word `g` or `g^-1`.
    Then the link graph of `P` is the disjoint union of the link graph of the
    presentation with `g` and that relator removed, and a single edge
    `g^+ - g^-`; `m_g = 1` so the compatible orderings biject; the extra
    component has `|C| = 2, |A| = 1, |AC| = 1, L = 1`, hence Euler
    characteristic 2 and genus 0; and genus is additive over components.  So
    `gamma_N(P) = gamma_N(P minus that row)` exactly.

Lemma D (gauge) and Lemma E (reflection) are W6b's, unchanged and reused.

ENUMERATED (not proven — finite, closed, counted):
    * the macro rotations (W6b's closure over all rotation systems of `H`);
    * the cut `s in {0,...,m}` and, at `v`, which run neighbours `D_1` and in
      which direction the arcs run inside a run — four sign variants, kept
      deliberately redundant so that no orientation convention has to be
      argued (the repo's certified `_k4_minus_edge_scheme` picks one of the
      four; this solver enumerates all four and lets the Euler filter decide);
    * the phase tuples and the rank assignments — identical machinery to W6b,
      calling `neuwirth_rank_solver._propagate_component` verbatim.

Lemma I (book contraction) — PROVEN, and strictly more general than Lemma H.
    Contract ONLY the book bundles (W6b Lemma B licenses that: they are book in
    every spherical rotation system, deleting `m-1` parallel edges is deletion
    of non-bridges, and re-inserting them side by side adds `m-1` edges and
    `m-1` faces so the Euler characteristic is unchanged).  The spherical
    rotation systems of `G` are then in bijection with (spherical rotation
    systems of the reduced multigraph `Hhat`) x (a labelling of each book
    bundle's `m` edges by its `m` block positions).  NOTHING is assumed about
    the non-book bundles -- they are carried at full multiplicity and their
    placement is enumerated, not constructed.  This is the general fallback
    (route `HHAT`); it decides MIXED, three-piece and multi-split supports
    whenever `prod_w (deg_Hhat(w) - 1)!` fits the declared budget.  See the
    full statement at `reduced_multigraph`.

FAIL CLOSED.  Anything outside BOOK / SPLIT_ENDPOINT (delegated to W6b) /
CUT / a bare-row reduction / a reduced-multigraph closure within budget
returns `UNSUPPORTED`.  A negative is returned only after the whole finite
case set is consumed; a truncated enumeration raises, and a `Hhat` closure
above the budget returns `UNSUPPORTED` rather than a verdict.

DOCTRINE.  `NOT_SPHERICAL` is a certificate for the exact spelling tested
(necessity half of `AK3_NEUWIRTH.md` Theorem 2, which does not use
connectivity).  A spherical verdict is `SPHERICAL_REQUIRES_REGINA` and is
QUARANTINED: Pipeline B (Regina `isBall` on an independently built `N(K)`)
does not exist in this repo, so a positive is a suspected Pipeline-A bug
first and a result never.  No AK(3), AC, or stable-AC claim is made here.

Run (every mode fits the guard's 60 s slice):

    python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- \\
        python3 fable/proofs/checkers/rank3_cut_family_solver.py controls
    python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- \\
        python3 fable/proofs/checkers/rank3_cut_family_solver.py crosscheck
    python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- \\
        python3 fable/proofs/checkers/rank3_cut_family_solver.py shape-completeness
    python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- \\
        python3 fable/proofs/checkers/rank3_cut_family_solver.py repo-agreement
    python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- \\
        python3 fable/proofs/checkers/rank3_cut_family_solver.py reduced
    python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- \\
        python3 fable/proofs/checkers/rank3_cut_family_solver.py targets
    python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- \\
        python3 fable/proofs/checkers/rank3_cut_family_solver.py coverage-report
    python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- \\
        python3 fable/proofs/checkers/rank3_cut_family_solver.py ball-coverage \\
        --ceiling 20
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

import rank3_link_graph as rlg  # noqa: E402
import rank3_shift_family_solver as sf  # noqa: E402
from experiments.stable_ac.thickenable import (  # noqa: E402
    neuwirth_rank_solver as base,
)

ClassKey = tuple[int, int]

MAX_MACRO_ENUMERATION = sf.MAX_MACRO_ENUMERATION
MAX_DFS_NODES = sf.MAX_DFS_NODES

# Lemma H's redundant sign variants at `v`.  Production enumerates all four;
# the corruption controls switch subsets off and watch verdicts move.
V_VARIANTS = ((False, False), (False, True), (True, False), (True, True))

# W6b Lemma B(iii): a bundle's arcs run in opposite cyclic senses at its two
# endpoints.  This flag exists ONLY so a corruption control can switch the
# reversal off and watch verdicts move; production code never touches it.
REVERSE_BLOCKS = True

FAILS: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> bool:
    print(f"{'PASS' if cond else 'FAIL'}  {name}" + (f"   {detail}" if detail else ""))
    if not cond:
        FAILS.append(name)
    return bool(cond)


# ---------------------------------------------------------------------------
# family classification
# ---------------------------------------------------------------------------


def bundle_shape(
    verts: list[int], simple: frozenset[ClassKey], u: int, v: int, m: int
) -> tuple[str, tuple[frozenset[int], ...]]:
    """Classify one bundle by Lemma A's region index set."""
    if m < 2:
        return "SINGLE", ()
    pieces = sf.pieces_of(verts, simple, u, v)
    if len(pieces) == 1:
        return "BOOK", pieces
    if len(pieces) != 2:
        return f"PIECES{len(pieces)}", pieces
    touch = []
    for piece in pieces:
        tu = any(tuple(sorted((u, w))) in simple for w in piece)
        tv = any(tuple(sorted((v, w))) in simple for w in piece)
        touch.append((tu, tv))
    ordered = sorted(touch)
    if ordered == [(False, True), (True, False)]:
        return "SPLIT_ENDPOINT", pieces
    if ordered == [(True, True), (True, True)]:
        return "CUT", pieces
    return "MIXED", pieces


@dataclass(frozen=True)
class CutFamily:
    kind: str                      # BOOK | SPLIT_ENDPOINT | CUT | BARE_ROW | UNSUPPORTED
    reason: str | None
    data: base.LinkData | None
    gens: str
    n_germs: int
    simple_edges: frozenset[ClassKey] = frozenset()
    macro: tuple[dict[int, tuple[int, ...]], ...] = ()
    cut_bundle: ClassKey | None = None
    cut_multiplicity: int = 0
    piece_label: dict[int, int] = field(default_factory=dict)
    bundle_report: tuple[dict[str, object], ...] = ()
    reduced: tuple[tuple[str, ...], str] | None = None


def bare_row_reduction(
    words: tuple[str, ...], gens: str
) -> tuple[tuple[str, ...], str] | None:
    """Lemma F: drop a generator occurring once, as its own one-letter row."""
    for index, word in enumerate(words):
        if len(word) != 1:
            continue
        letter = word.lower()
        if letter not in gens:
            continue
        occurrences = sum(
            other.lower().count(letter) for j, other in enumerate(words) if j != index
        )
        if occurrences:
            continue
        rest = tuple(w for j, w in enumerate(words) if j != index)
        new_gens = "".join(g for g in gens if g != letter)
        if not new_gens or len(rest) != len(new_gens):
            continue
        return rest, new_gens
    return None


def classify_cut_family(words: tuple[str, ...], gens: str) -> CutFamily:
    try:
        link = rlg.build_link(tuple(words), gens)
    except ValueError as exc:
        return CutFamily("UNSUPPORTED", f"link graph rejected the words: {exc}",
                         None, gens, 2 * len(gens))
    simple_set, loops = rlg.simple_support(link)
    simple = frozenset(simple_set)
    data = sf.link_data(link)
    n_germs = link.n_germs
    verts = sorted(rlg.active_germs(link))
    if loops:
        return CutFamily("UNSUPPORTED", "A-link contains a loop", data, gens, n_germs)
    if len(verts) != n_germs:
        return CutFamily("UNSUPPORTED", "some generator does not occur",
                         data, gens, n_germs)
    if len(rlg.components(link)) != 1:
        reduced = bare_row_reduction(tuple(words), gens)
        if reduced is not None:
            return CutFamily("BARE_ROW",
                             "A-link is disconnected; Lemma F reduction available",
                             data, gens, n_germs, simple, (), None, 0, {}, (),
                             reduced)
        return CutFamily("UNSUPPORTED", "A-link is disconnected", data, gens,
                         n_germs)

    mult = {key: len(edges) for key, edges in data.class_edges.items()}
    report: list[dict[str, object]] = []
    cut_bundle: ClassKey | None = None
    cut_pieces: tuple[frozenset[int], ...] = ()
    kind = "BOOK"
    reason: str | None = None
    split_endpoint = 0
    for key in sorted(mult):
        u, v = key
        m = mult[key]
        shape, pieces = bundle_shape(verts, simple, u, v, m)
        report.append({"bundle": f"{u}-{v}", "multiplicity": m,
                       "pieces": len(pieces), "class": shape})
        if shape in ("SINGLE", "BOOK"):
            continue
        if shape == "SPLIT_ENDPOINT":
            split_endpoint += 1
            continue
        if shape == "CUT":
            if cut_bundle is not None:
                kind = "UNSUPPORTED"
                reason = "more than one CUT bundle"
            else:
                cut_bundle, cut_pieces = key, pieces
            continue
        kind = "UNSUPPORTED"
        reason = f"bundle {u}-{v} is {shape}"

    if kind != "UNSUPPORTED":
        if cut_bundle is not None and split_endpoint:
            kind, reason = "UNSUPPORTED", "a CUT bundle and a SPLIT_ENDPOINT bundle"
        elif split_endpoint > 1:
            kind, reason = "UNSUPPORTED", "more than one split bundle"
        elif split_endpoint == 1:
            kind = "SPLIT_ENDPOINT"
        elif cut_bundle is not None:
            kind = "CUT"

    if kind == "UNSUPPORTED":
        return CutFamily("UNSUPPORTED", reason, data, gens, n_germs, simple, (),
                         None, 0, {}, tuple(report))
    if kind != "CUT":
        # BOOK / SPLIT_ENDPOINT are W6b's; the decision is delegated there so
        # that this solver reproduces W6b exactly on the states it already did.
        return CutFamily(kind, None, data, gens, n_germs, simple, (), None, 0,
                         {}, tuple(report))

    try:
        macro = sf.macro_rotations(verts, simple)
    except AssertionError as exc:
        return CutFamily("UNSUPPORTED", str(exc), data, gens, n_germs, simple, (),
                         None, 0, {}, tuple(report))
    if not macro:
        return CutFamily("UNSUPPORTED", "simple support is not planar", data, gens,
                         n_germs, simple, (), None, 0, {}, tuple(report))
    ordered_pieces = sorted(cut_pieces, key=sorted)
    label = {w: index for index, piece in enumerate(ordered_pieces) for w in piece}
    assert cut_bundle is not None
    return CutFamily("CUT", None, data, gens, n_germs, simple, macro, cut_bundle,
                     mult[cut_bundle], label, tuple(report))


# ---------------------------------------------------------------------------
# the cut scheme (Lemma H's enumeration)
# ---------------------------------------------------------------------------


def split_runs(
    seq: tuple[int, ...], label: dict[int, int]
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Cut a cyclic neighbour sequence into its piece-0 run and piece-1 run.

    Lemma G says the two runs are cyclically contiguous in any spherical
    rotation; a sequence that is not raises rather than being silently
    dropped.
    """
    labels = [label[w] for w in seq]
    if not labels:
        return (), ()
    if len(set(labels)) == 1:
        return (tuple(seq), ()) if labels[0] == 0 else ((), tuple(seq))
    n = len(seq)
    starts = [i for i in range(n) if labels[i] == 0 and labels[i - 1] == 1]
    if len(starts) != 1:
        raise AssertionError("piece darts are not contiguous in a macro rotation")
    start = starts[0]
    rotated = tuple(seq[(start + i) % n] for i in range(n))
    rotated_labels = [label[w] for w in rotated]
    first = rotated_labels.count(0)
    if rotated_labels[:first] != [0] * first or set(rotated_labels[first:]) != {1}:
        raise AssertionError("piece darts are not contiguous in a macro rotation")
    return rotated[:first], rotated[first:]


def cut_scheme(
    data: base.LinkData,
    rotation: dict[int, tuple[int, ...]],
    bundle: ClassKey,
    label: dict[int, int],
    cut: int,
    swap_v: bool,
    reverse_v: bool,
    n_germs: int,
    name: str,
) -> base.Scheme | None:
    """Blow the macro rotation up with the cut bundle placed in TWO runs.

    At `u` the arcs of ranks `0..cut-1` fill the gap that follows the `P_1`
    block and ranks `cut..m-1` the gap that follows the `P_2` block.  At `v`
    the run adjacent to the `P_1` block is `cut..m-1` in reverse order (the
    convention of the repo's certified `_k4_minus_edge_scheme`); `swap_v` and
    `reverse_v` enumerate the other three sign conventions so that no
    orientation argument is load-bearing.
    """
    u, v = bundle
    m = len(data.class_edges[bundle])
    slots = base._empty_slots(data)
    for vertex in range(n_germs):
        if vertex in (u, v):
            continue
        start = 0
        for neighbor in rotation[vertex]:
            key = tuple(sorted((vertex, neighbor)))
            base._set_class_block(data, slots, key, vertex, start,
                                  reverse=(vertex != key[0]) if REVERSE_BLOCKS
                                  else False)
            start += len(data.class_edges[key])

    for endpoint, other in ((u, v), (v, u)):
        seq = tuple(w for w in rotation[endpoint] if w != other)
        block_one, block_two = split_runs(seq, label)
        if endpoint == u:
            first_ranks: list[int] = list(range(cut))
            second_ranks: list[int] = list(range(cut, m))
        else:
            first_ranks = list(range(m - 1, cut - 1, -1))
            second_ranks = list(range(cut - 1, -1, -1))
            if swap_v:
                first_ranks, second_ranks = second_ranks, first_ranks
            if reverse_v:
                first_ranks = first_ranks[::-1]
                second_ranks = second_ranks[::-1]
        position = 0
        vector = [-1] * m
        for neighbor in block_one:
            key = tuple(sorted((endpoint, neighbor)))
            base._set_class_block(data, slots, key, endpoint, position,
                                  reverse=(endpoint != key[0]) if REVERSE_BLOCKS
                                  else False)
            position += len(data.class_edges[key])
        for rank in first_ranks:
            vector[rank] = position
            position += 1
        for neighbor in block_two:
            key = tuple(sorted((endpoint, neighbor)))
            base._set_class_block(data, slots, key, endpoint, position,
                                  reverse=(endpoint != key[0]) if REVERSE_BLOCKS
                                  else False)
            position += len(data.class_edges[key])
        for rank in second_ranks:
            vector[rank] = position
            position += 1
        if position != len(data.vertex_darts[endpoint]) or min(vector) < 0:
            raise AssertionError("cut scheme did not fill the rotation at an endpoint")
        for edge in data.class_edges[bundle]:
            dart = base._dart_for_edge_at(data, edge, endpoint)
            slots[dart][:] = list(vector)

    if not sf.verify_slot_partition(data, slots, n_germs):
        raise AssertionError("cut scheme produced an invalid slot partition")
    return base.Scheme(name, "CUT", cut, tuple(map(tuple, slots)), True)


def cut_schemes(
    family: CutFamily,
    cut_offsets: bool = True,
    macro_limit: int | None = None,
    v_variants: tuple[tuple[bool, bool], ...] = V_VARIANTS,
) -> tuple[tuple[base.Scheme, ...], dict[str, int]]:
    """All cut schemes, deduplicated and filtered to spherical shapes.

    The Euler filter is LOSSLESS: permuting ranks inside a parallel class
    relabels the same edges at both endpoints, an isomorphism of the embedded
    graph, so a scheme's Euler characteristic does not depend on the rank
    assignment.  A non-spherical shape can therefore never carry a witness.
    """
    assert family.data is not None and family.cut_bundle is not None
    data = family.data
    m = family.cut_multiplicity
    ranks = sf.identity_ranks(data)
    seen: set[tuple[tuple[int, ...], ...]] = set()
    kept: list[base.Scheme] = []
    stats = {"generated": 0, "duplicate": 0, "non_spherical": 0, "kept": 0}
    cuts = range(m + 1) if cut_offsets else range(1)
    for index, rotation in enumerate(family.macro):
        if macro_limit is not None and index >= macro_limit:
            continue
        for cut in cuts:
            for swap_v, reverse_v in v_variants:
                stats["generated"] += 1
                scheme = cut_scheme(
                    data, rotation, family.cut_bundle, family.piece_label, cut,
                    swap_v, reverse_v, family.n_germs,
                    f"macro{index}-cut{cut}-s{int(swap_v)}r{int(reverse_v)}",
                )
                assert scheme is not None
                if scheme.slots in seen:
                    stats["duplicate"] += 1
                    continue
                seen.add(scheme.slots)
                if sf.scheme_euler(data, scheme, ranks, family.n_germs) != 2:
                    stats["non_spherical"] += 1
                    continue
                stats["kept"] += 1
                kept.append(scheme)
    return tuple(kept), stats


# ---------------------------------------------------------------------------
# the reduced multigraph `Hhat` (Lemma I) — the general fallback
# ---------------------------------------------------------------------------


def reduced_multigraph(
    data: base.LinkData, verts: list[int], simple: frozenset[ClassKey]
) -> tuple[tuple[ClassKey, ...], dict[ClassKey, int], dict[int, list[int]]]:
    """`Hhat`: every BOOK bundle contracted to one edge, the rest kept in full.

    Lemma I (book contraction) — PROVEN, from W6b Lemma B.
        Let `B` be the set of bundles with `|pieces| = 1` and `m >= 2`.  By
        Lemma B every such bundle is book in every spherical rotation system
        of `G`, so deleting `m - 1` of its edges (deletion of non-bridges)
        preserves sphericity, and re-inserting them as one contiguous block
        preserves it back (drawing `m` parallel arcs side by side adds `m-1`
        edges and `m-1` faces, leaving the Euler characteristic fixed).
        Hence the spherical rotation systems of `G` are in bijection with
        (spherical rotation systems of `Hhat`) x (a labelling of each book
        bundle's `m` edges by its `m` block positions), where `Hhat` is `G`
        with exactly the book bundles contracted.  NOTHING is assumed about
        the non-book bundles: they are carried at full multiplicity and their
        placement is enumerated, not constructed.
    """
    order: list[ClassKey] = []
    keep: dict[ClassKey, int] = {}
    incidence: dict[int, list[int]] = {w: [] for w in verts}
    for key in sorted(data.class_edges):
        m = len(data.class_edges[key])
        shape, _ = bundle_shape(verts, simple, key[0], key[1], m)
        keep[key] = 1 if shape in ("SINGLE", "BOOK") else m
        order.append(key)
    edge_id = 0
    edges: list[tuple[ClassKey, int]] = []
    for key in order:
        for index in range(keep[key]):
            edges.append((key, index))
            incidence[key[0]].append(edge_id)
            incidence[key[1]].append(edge_id)
            edge_id += 1
    return tuple(order), keep, {"edges": edges, **incidence}  # type: ignore[return-value]


def reduced_rotation_budget(
    data: base.LinkData, verts: list[int], simple: frozenset[ClassKey]
) -> int:
    _, keep, inc = reduced_multigraph(data, verts, simple)
    total = 1
    for w in verts:
        total *= math.factorial(max(0, len(inc[w]) - 1))
    return total


def spherical_reduced_rotations(
    data: base.LinkData, verts: list[int], simple: frozenset[ClassKey], budget: int
) -> tuple[tuple[dict[int, tuple[int, ...]], ...], dict[ClassKey, int], int] | None:
    """Every spherical rotation system of `Hhat` (a complete finite closure).

    Returns `None` (fail closed, never truncate) when the closure exceeds
    `budget`.
    """
    _, keep, inc = reduced_multigraph(data, verts, simple)
    edges: list[tuple[ClassKey, int]] = inc["edges"]  # type: ignore[assignment]
    # Lemma I and the `V - E + F = 2` test below are for a CONNECTED link;
    # a disconnected one has Euler characteristic `2L` and is Lemma F's or
    # W6 Lemma W6.3's business, never this route's.
    adjacency: dict[int, set[int]] = {w: set() for w in verts}
    for key in keep:
        adjacency[key[0]].add(key[1])
        adjacency[key[1]].add(key[0])
    reached = {verts[0]}
    frontier = [verts[0]]
    while frontier:
        current = frontier.pop()
        fresh = adjacency[current] - reached
        reached |= fresh
        frontier.extend(fresh)
    if reached != set(verts):
        raise AssertionError("reduced-rotation closure needs a connected link")
    total = 1
    for w in verts:
        total *= math.factorial(max(0, len(inc[w]) - 1))
    if total > budget:
        return None
    # darts of Hhat: (edge_id, endpoint)
    per_vertex = []
    for w in verts:
        darts = [(e, w) for e in inc[w]]
        head, *tail = darts
        per_vertex.append([(head, *p) for p in itertools.permutations(tail)])
    n_edges = len(edges)
    out = []
    for combo in itertools.product(*per_vertex):
        nxt: dict[tuple[int, int], tuple[int, int]] = {}
        for rotation in combo:
            for index, dart in enumerate(rotation):
                nxt[dart] = rotation[(index + 1) % len(rotation)]
        seen: set[tuple[int, int]] = set()
        faces = 0
        for start in nxt:
            if start in seen:
                continue
            faces += 1
            dart = start
            while dart not in seen:
                seen.add(dart)
                edge, at = dart
                key = edges[edge][0]
                other = key[1] if at == key[0] else key[0]
                dart = nxt[(edge, other)]
        if len(verts) - n_edges + faces == 2:
            out.append({w: tuple(e for e, _ in rotation)
                        for w, rotation in zip(verts, combo)})
    return tuple(out), keep, total


def reduced_scheme(
    data: base.LinkData,
    rotation: dict[int, tuple[int, ...]],
    keep: dict[ClassKey, int],
    edges: list[tuple[ClassKey, int]],
    n_germs: int,
    name: str,
) -> base.Scheme:
    """Turn one `Hhat` rotation system into a slot scheme on `G`."""
    slots = base._empty_slots(data)
    for vertex in range(n_germs):
        position = 0
        pending: dict[ClassKey, list[int]] = {}
        for edge_id in rotation[vertex]:
            key, index = edges[edge_id]
            if keep[key] == 1 and len(data.class_edges[key]) > 1:
                base._set_class_block(data, slots, key, vertex, position,
                                      reverse=(vertex != key[0]) if REVERSE_BLOCKS
                                      else False)
                position += len(data.class_edges[key])
                continue
            if keep[key] == 1:
                base._set_class_block(data, slots, key, vertex, position,
                                      reverse=False)
                position += 1
                continue
            vector = pending.setdefault(key, [-1] * len(data.class_edges[key]))
            vector[index] = position
            position += 1
        for key, vector in pending.items():
            if min(vector) < 0:
                raise AssertionError("reduced scheme lost a parallel arc")
            for edge in data.class_edges[key]:
                dart = base._dart_for_edge_at(data, edge, vertex)
                slots[dart][:] = list(vector)
        if position != len(data.vertex_darts[vertex]):
            raise AssertionError("reduced scheme did not fill a rotation")
    if not sf.verify_slot_partition(data, slots, n_germs):
        raise AssertionError("reduced scheme produced an invalid slot partition")
    return base.Scheme(name, "REDUCED", None, tuple(map(tuple, slots)), True)


def reduced_schemes(
    family: CutFamily, budget: int
) -> tuple[tuple[base.Scheme, ...], dict[str, int]] | None:
    assert family.data is not None
    data = family.data
    verts = sorted(range(family.n_germs))
    found = spherical_reduced_rotations(data, verts, family.simple_edges, budget)
    if found is None:
        return None
    rotations, keep, total = found
    _, _, inc = reduced_multigraph(data, verts, family.simple_edges)
    edges: list[tuple[ClassKey, int]] = inc["edges"]  # type: ignore[assignment]
    seen: set[tuple[tuple[int, ...], ...]] = set()
    kept: list[base.Scheme] = []
    for index, rotation in enumerate(rotations):
        scheme = reduced_scheme(data, rotation, keep, edges, family.n_germs,
                                f"hhat{index}")
        if scheme.slots in seen:
            continue
        seen.add(scheme.slots)
        kept.append(scheme)
    return tuple(kept), {"reduced_rotation_closure": total,
                         "spherical_reduced_rotations": len(rotations),
                         "distinct_schemes": len(kept)}


# ---------------------------------------------------------------------------
# the decision
# ---------------------------------------------------------------------------


@dataclass
class CutDecision:
    words: tuple[str, ...]
    gens: str
    verdict: str
    spherical: bool | None
    family: str
    reason: str | None
    witness: sf.ShiftWitness | None
    counters: sf.Counters
    bundle_report: tuple[dict[str, object], ...] = ()
    macro_rotation_count: int = 0
    scheme_stats: dict = field(default_factory=dict)
    route: str = "CUT"
    extras: dict = field(default_factory=dict)


def _from_shift(decision: sf.ShiftDecision, route: str) -> CutDecision:
    return CutDecision(decision.words, decision.gens, decision.verdict,
                       decision.spherical, decision.family, decision.reason,
                       decision.witness, decision.counters,
                       decision.bundle_report, decision.macro_rotation_count,
                       {}, route)


DEFAULT_REDUCED_BUDGET = 300_000


def _run_schemes(
    data: base.LinkData,
    gens: str,
    schemes: tuple[base.Scheme, ...],
    n_germs: int,
) -> tuple[sf.ShiftWitness | None, sf.Counters]:
    """The W6b phase / rank machinery, verbatim, over a given scheme list."""
    counters = sf.Counters()
    constraints = sf.constraints_of(data, len(gens))
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
            witness = sf._combine(data, scheme, constraints, per_component, phases,
                                  n_germs, counters)
            if witness is not None:
                counters.exhaustive = False
                return witness, counters
    counters.exhaustive = (
        counters.schemes_considered == counters.scheme_budget
        and counters.phase_tuples_considered == counters.phase_tuple_budget
        and counters.component_seed_attempts == counters.component_seed_budget
    )
    if not counters.exhaustive:
        raise AssertionError("negative search did not exhaust its budget")
    return None, counters


def solve_cut(
    words: tuple[str, ...],
    gens: str,
    cut_offsets: bool = True,
    macro_limit: int | None = None,
    v_variants: tuple[tuple[bool, bool], ...] = V_VARIANTS,
    allow_bare_row: bool = True,
    reduced_budget: int = DEFAULT_REDUCED_BUDGET,
) -> CutDecision:
    """Decide compatible sphericity on BOOK / SPLIT_ENDPOINT / CUT support.

    `cut_offsets=False`, `macro_limit` and `v_variants` exist ONLY for the
    corruption controls: each deliberately breaks a completeness lemma.
    """
    words = tuple(words)
    family = classify_cut_family(words, gens)

    if family.kind in ("BOOK", "SPLIT_ENDPOINT"):
        return _from_shift(sf.solve_shift_family(words, gens), "W6b_DELEGATED")

    if family.kind == "BARE_ROW":
        if not allow_bare_row or family.reduced is None:
            return CutDecision(words, gens, "UNSUPPORTED", None, "UNSUPPORTED",
                               "A-link is disconnected", None, sf.Counters(),
                               family.bundle_report, 0, {}, "NONE")
        rest, new_gens = family.reduced
        inner = solve_cut(rest, new_gens, cut_offsets, macro_limit, v_variants,
                          allow_bare_row, reduced_budget)
        if inner.spherical is None:
            return CutDecision(words, gens, "UNSUPPORTED", None, "BARE_ROW",
                               f"Lemma F reduction to {rest} is {inner.reason}",
                               None, inner.counters, family.bundle_report, 0,
                               inner.scheme_stats, "LEMMA_F_" + inner.route,
                               {"reduced_words": list(rest),
                                "reduced_gens": new_gens,
                                "reduced_family": inner.family})
        return CutDecision(words, gens, inner.verdict, inner.spherical,
                           "BARE_ROW", None, inner.witness, inner.counters,
                           family.bundle_report, inner.macro_rotation_count,
                           inner.scheme_stats, "LEMMA_F_" + inner.route,
                           {"reduced_words": list(rest),
                            "reduced_gens": new_gens,
                            "reduced_family": inner.family,
                            "reduced_verdict": inner.verdict})

    counters = sf.Counters()
    if family.kind == "UNSUPPORTED" or family.data is None:
        # `simple_edges` is populated only once the link has been checked
        # connected, loopless, and with every generator occurring -- exactly
        # the setting Lemma I needs.
        if family.data is not None and family.simple_edges and reduced_budget > 0:
            built = reduced_schemes(family, reduced_budget)
            if built is not None:
                schemes, stats = built
                witness, counters = _run_schemes(family.data, gens, schemes,
                                                 family.n_germs)
                verdict = ("SPHERICAL_REQUIRES_REGINA" if witness is not None
                           else "NOT_SPHERICAL")
                return CutDecision(words, gens, verdict, witness is not None,
                                   "REDUCED", None, witness, counters,
                                   family.bundle_report, 0, stats, "HHAT")
            return CutDecision(
                words, gens, "UNSUPPORTED", None, family.kind,
                f"{family.reason}; reduced rotation closure exceeds the budget "
                f"({reduced_budget})", None, counters, family.bundle_report,
                len(family.macro), {}, "NONE")
        return CutDecision(words, gens, "UNSUPPORTED", None, family.kind,
                           family.reason, None, counters, family.bundle_report,
                           len(family.macro), {}, "NONE")

    data = family.data
    schemes, stats = cut_schemes(family, cut_offsets, macro_limit, v_variants)
    constraints = sf.constraints_of(data, len(gens))
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
            witness = sf._combine(data, scheme, constraints, per_component, phases,
                                  family.n_germs, counters)
            if witness is not None:
                counters.exhaustive = False
                return CutDecision(words, gens, "SPHERICAL_REQUIRES_REGINA", True,
                                   "CUT", None, witness, counters,
                                   family.bundle_report, len(family.macro), stats,
                                   "CUT")

    counters.exhaustive = (
        counters.schemes_considered == counters.scheme_budget
        and counters.phase_tuples_considered == counters.phase_tuple_budget
        and counters.component_seed_attempts == counters.component_seed_budget
    )
    if not counters.exhaustive:
        raise AssertionError("negative cut-family search did not exhaust its budget")
    return CutDecision(words, gens, "NOT_SPHERICAL", False, "CUT", None, None,
                       counters, family.bundle_report, len(family.macro), stats,
                       "CUT")


# ---------------------------------------------------------------------------
# independent oracles
# ---------------------------------------------------------------------------


def all_spherical_rotation_shapes(
    words: tuple[str, ...], gens: str, budget: int
) -> set[tuple[tuple[int, ...], ...]] | None:
    """Every spherical rotation system of `G`, as canonical dart cycles.

    A rotation system is recorded as, for each germ, the cyclic sequence of
    its darts normalised to start at its smallest dart.  This is the set the
    scheme enumeration must CONTAIN (Lemma H's completeness claim), and it is
    checked directly rather than by a count.
    """
    link = rlg.build_link(tuple(words), gens)
    data = sf.link_data(link)
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
    out = set()
    for combo in itertools.product(*per_vertex):
        sigma = [-1] * len(data.A)
        for rotation in combo:
            for index, dart in enumerate(rotation):
                sigma[dart] = rotation[(index + 1) % len(rotation)]
        if sf.faces_and_euler(data, sigma, n_germs)[1] == 2:
            out.add(tuple(normalise_cycle(rotation) for rotation in combo))
    return out


def normalise_cycle(rotation: tuple[int, ...]) -> tuple[int, ...]:
    start = rotation.index(min(rotation))
    return tuple(rotation[(start + i) % len(rotation)] for i in range(len(rotation)))


def shapes_from_schemes(
    family: CutFamily, schemes: tuple[base.Scheme, ...]
) -> set[tuple[tuple[int, ...], ...]]:
    """Every rotation system generated by (scheme, rank assignment)."""
    assert family.data is not None
    data = family.data
    classes = list(data.class_edges.items())
    domains = [list(itertools.permutations(range(len(edges))))
               for _, edges in classes]
    out = set()
    for scheme in schemes:
        for combo in itertools.product(*domains):
            ranks = [0] * len(data.edge_darts)
            for (key, edges), perm in zip(classes, combo):
                for edge, rank in zip(edges, perm):
                    ranks[edge] = rank
            rotations = []
            for vertex in range(family.n_germs):
                rotation = tuple(sorted(
                    data.vertex_darts[vertex],
                    key=lambda d: scheme.slots[d][ranks[data.edge_of_dart[d]]],
                ))
                rotations.append(normalise_cycle(rotation))
            out.add(tuple(rotations))
    return out




# ---------------------------------------------------------------------------
# pinned fixtures
# ---------------------------------------------------------------------------

# Every fixture below was found by a seeded random scan over short cyclically
# reduced words and is pinned here so runs are reproducible.  `gamma` is the
# EXACT gamma_N from a complete enumeration of all compatible orderings; the
# solver must agree with it (spherical iff gamma == 0).  All are family CUT.
CROSSCHECK: tuple[tuple[tuple[str, ...], str, int], ...] = (
    # CUT, rank 2 (this is the K4-e support; see `repo-agreement`)
    (("Xyy", "yyyx"), "xy", 0),
    (("YxYY", "yx"), "xy", 0),
    (("XYxy", "yxyxxx"), "xy", 1),
    (("XXXYXX", "xxY"), "xy", 0),
    (("yXYX", "YYYX"), "xy", 1),
    (("YY", "xyyXY"), "xy", 1),
    (("XYXYY", "YxYYx"), "xy", 0),
    (("x", "xxxYXy"), "xy", 1),
    (("XXyX", "xyxy"), "xy", 1),
    (("Yxyyyx", "YxYx"), "xy", 0),
    # CUT, rank 3
    (("YXZ", "xYZxY", "yX"), "xyz", 1),
    (("zxzy", "zyXzz", "Y"), "xyz", 0),
    (("Yzx", "YZXX", "XZX"), "xyz", 0),
    (("zXz", "Xy", "ZZYZ"), "xyz", 0),
    (("Xz", "YY", "zzzzYx"), "xyz", 1),
    (("Y", "ZZZxY", "ZXZ"), "xyz", 0),
    (("yyX", "yyxyy", "xz"), "xyz", 0),
    (("ZXXZx", "X", "Zxxzy"), "xyz", 1),
    (("zzxx", "XYYXz", "xx"), "xyz", 1),
    (("xxYZ", "yyyZ", "ZXyxY"), "xyz", 1),
    (("YxzY", "xyyZY", "ZyX"), "xyz", 1),
    (("xzyx", "ZxZZ", "zXZxYX"), "xyz", 1),
)

# Fixtures whose verdict FLIPS when a completeness lemma is broken.  Each
# corruption control asserts the flip, so a control that stops firing is a
# failure, not a pass.
FLIP_NO_CUT: tuple[tuple[tuple[str, ...], str], ...] = (
    (("XXyxxy", "xY"), "xy"),
    (("YX", "yyXYYX"), "xy"),
    (("Yxx", "YXX"), "xy"),
    (("XYXXYX", "YXyX"), "xy"),
    (("xxYx", "yxyxx"), "xy"),
    (("XXYX", "yXXX"), "xy"),
)
FLIP_ONE_MACRO: tuple[tuple[tuple[str, ...], str], ...] = (
    (("Z", "yXZyyz", "Yzx"), "xyz"),
    (("zY", "zxzY", "Zxxx"), "xyz"),
    (("xzz", "zXYX", "zzz"), "xyz"),
    (("zXy", "yXz", "ZZXZ"), "xyz"),
    (("yZYXX", "XYX", "yX"), "xyz"),
    (("z", "YzyzYX", "ZZX"), "xyz"),
)

# Small enough for a COMPLETE enumeration of every rotation system of the
# multigraph `G`, so Lemma H's completeness can be checked as a set identity
# rather than a count.
SHAPE_FIXTURES: tuple[tuple[tuple[str, ...], str], ...] = (
    (("YxYY", "yx"), "xy"),
    (("Xyy", "yyyx"), "xy"),
    (("yXYX", "YYYX"), "xy"),
    (("XXyX", "xyxy"), "xy"),
    (("YY", "xyyXY"), "xy"),
    (("YXZ", "xYZxY", "yX"), "xyz"),
    (("zxzy", "zyXzz", "Y"), "xyz"),
    (("Yzx", "YZXX", "XZX"), "xyz"),
    (("zXz", "Xy", "ZZYZ"), "xyz"),
    (("Y", "ZZZxY", "ZXZ"), "xyz"),
    (("Z", "ZyZ", "ZXyX"), "xyz"),
    (("Z", "yXzx", "zzY"), "xyz"),
)

# Lemma F (bare-row splitting): `gamma_N(r1, r2, Z) == gamma_N(r1, r2)`.
BARE_ROW_FIXTURES: tuple[tuple[tuple[str, ...], str, int], ...] = (
    (("xyx", "XXXy", "Z"), "xyz", 0),
    (("xx", "xyXY", "Z"), "xyz", 1),
    (("yy", "XYxY", "Z"), "xyz", 1),
    (("yXyy", "yxYXy", "Z"), "xyz", 1),
    (("xYXyXY", "YY", "Z"), "xyz", 1),
    (("YXyXY", "Y", "Z"), "xyz", 1),
    (("XXyxxy", "xY", "Z"), "xyz", 0),
    (("XX", "YXyXX", "Z"), "xyz", 1),
)

# Instances OUTSIDE the CUT family that the Lemma I reduced route decides:
# MIXED bundles (one piece meets both endpoints, the other only one), bundles
# with three or four pieces, and several split bundles at once.  `gamma` is
# again the exact value from a complete enumeration of compatible orderings.
HHAT_CROSSCHECK: tuple[tuple[tuple[str, ...], str, int], ...] = (
    (("xzYY", "ZY", "zYYz"), "xyz", 0),
    (("ZZ", "zyZyx", "Y"), "xyz", 1),
    (("yZX", "yZXZ", "ZZ"), "xyz", 1),
    (("yZ", "zXzY", "xZyz"), "xyz", 0),
    (("zxz", "z", "YZX"), "xyz", 0),
    (("xy", "Y", "yzy"), "xyz", 0),
    (("xx", "yX", "ZXyX"), "xyz", 0),
    (("ZY", "yyy", "xYXXy"), "xyz", 2),
    (("yyXYz", "yZ", "Y"), "xyz", 0),
    (("zzx", "YZZ", "y"), "xyz", 0),
    (("ZY", "ZZ", "yXyy"), "xyz", 1),
    (("yXX", "XZX", "x"), "xyz", 0),
    (("ZZZX", "xzx", "Xy"), "xyz", 0),
    (("X", "ZXYX", "YZXX"), "xyz", 0),
    (("XXZ", "zx", "zyzx"), "xyz", 0),
    (("yxz", "zXXzz", "z"), "xyz", 1),
    (("X", "zXYxYX", "xzYx"), "xyz", 1),
)

HHAT_FLIP_ONE_SCHEME: tuple[tuple[tuple[str, ...], str], ...] = (
    (("xzYY", "ZY", "zYYz"), "xyz"),
    (("yyXYz", "yZ", "Y"), "xyz"),
    (("zzx", "YZZ", "y"), "xyz"),
    (("yXX", "XZX", "x"), "xyz"),
    (("xYY", "X", "zYY"), "xyz"),
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

CEILINGS = (16, 18, 20, 22)


def decision_row(name: str, decision: CutDecision) -> dict:
    return {
        "name": name,
        "words": list(decision.words),
        "gens": decision.gens,
        "verdict": decision.verdict,
        "spherical": decision.spherical,
        "family": decision.family,
        "route": decision.route,
        "reason": decision.reason,
        "macro_rotations": decision.macro_rotation_count,
        "scheme_stats": decision.scheme_stats,
        "bundles": [dict(r) for r in decision.bundle_report],
        "counters": vars(decision.counters),
        "witness": (
            None if decision.witness is None else {
                "scheme": decision.witness.scheme,
                "cut": decision.witness.shift,
                "phases": list(decision.witness.phases),
                "face_count": decision.witness.face_count,
                "euler_characteristic": decision.witness.euler_characteristic,
                "genus": decision.witness.genus,
            }
        ),
        **decision.extras,
    }


def blocker_bucket(words: tuple[str, ...], gens: str) -> str:
    """What SHAPE blocks a state — the residual profile's index."""
    try:
        link = rlg.build_link(tuple(words), gens)
    except ValueError:
        return "REJECTED"
    simple_set, loops = rlg.simple_support(link)
    if loops:
        return "LOOP"
    verts = sorted(rlg.active_germs(link))
    if len(verts) != link.n_germs:
        return "MISSING_GENERATOR"
    if len(rlg.components(link)) != 1:
        return ("DISCONNECTED_BARE_ROW"
                if bare_row_reduction(tuple(words), gens) else "DISCONNECTED_OTHER")
    data = sf.link_data(link)
    simple = frozenset(simple_set)
    tally: dict[str, int] = {}
    for key, edges in data.class_edges.items():
        shape, _ = bundle_shape(verts, simple, key[0], key[1], len(edges))
        tally[shape] = tally.get(shape, 0) + 1
    hard = {k: v for k, v in tally.items() if k not in ("SINGLE", "BOOK")}
    if not hard:
        return "BOOK"
    if hard == {"CUT": 1}:
        return "CUT_1"
    if hard == {"SPLIT_ENDPOINT": 1}:
        return "SPLIT_ENDPOINT_1"
    if set(hard) == {"CUT"}:
        return f"CUT_{hard['CUT']}"
    return "MIXED:" + ",".join(f"{k}x{v}" for k, v in sorted(hard.items()))


# ---------------------------------------------------------------------------
# modes
# ---------------------------------------------------------------------------


def run_controls() -> dict:
    global REVERSE_BLOCKS
    record: dict = {}

    # (1) fail closed / route table on the six targets
    rows = []
    for name, words, gens in TARGETS:
        decision = solve_cut(words, gens)
        rows.append({"name": name, "family": decision.family,
                     "route": decision.route, "verdict": decision.verdict,
                     "reason": decision.reason})
    for name, expected_family in (("Tpub", "BOOK"), ("Txy_certified_AC_trivial", "BOOK"),
                                  ("ak3_rank2", "BOOK"), ("Q_rank2", "CUT"),
                                  ("ak3_stabilized", "BARE_ROW"),
                                  ("Q_stabilized", "BARE_ROW")):
        row = next(r for r in rows if r["name"] == name)
        check(f"route table: {name} is {expected_family}",
              row["family"] == expected_family, f"{row['family']} / {row['reason']}")
    record["route_table"] = rows

    # (2) every kept scheme traces a sphere, and the filter is not vacuous
    rows = []
    for words, gens, _gamma in CROSSCHECK:
        family = classify_cut_family(words, gens)
        assert family.data is not None
        schemes, stats = cut_schemes(family)
        ranks = sf.identity_ranks(family.data)
        eulers = {sf.scheme_euler(family.data, s, ranks, family.n_germs)
                  for s in schemes}
        ok = eulers == {2} and stats["kept"] > 0
        check(f"kept cut schemes trace a sphere {words}", ok,
              f"eulers={sorted(eulers)} stats={stats}")
        rows.append({"words": list(words), "gens": gens,
                     "macro_rotations": len(family.macro),
                     "cut_multiplicity": family.cut_multiplicity, **stats})
    check("the Euler filter actually discards shapes (not a vacuous filter)",
          all(r["non_spherical"] > 0 for r in rows))
    record["scheme_sphericity"] = rows

    # (3) Lemma D (gauge): a cyclic re-gauge of one germ's slots is inert
    rows = []
    for words, gens, gamma in CROSSCHECK[:8]:
        family = classify_cut_family(words, gens)
        data = family.data
        assert data is not None
        constraints = sf.constraints_of(data, len(gens))
        components = base._constraint_components(len(data.edge_darts), constraints)
        phase_ranges = [range(len(data.vertex_darts[2 * k])) for k in range(len(gens))]
        schemes, _ = cut_schemes(family)
        hits = []
        for gauge in (0, 1):
            hit = False
            for scheme in schemes:
                slots = [list(row) for row in scheme.slots]
                if gauge:
                    degree = len(data.vertex_darts[0])
                    for dart in data.vertex_darts[0]:
                        slots[dart][:] = [(s + 1) % degree for s in slots[dart]]
                gauged = base.Scheme(scheme.name, scheme.support_kind, scheme.cut,
                                     tuple(map(tuple, slots)), True)
                for phases in itertools.product(*phase_ranges):
                    per = []
                    for component in components:
                        domain = len(data.class_edges[
                            data.edge_class[component[0][0]]])
                        sols = []
                        for seed in range(domain):
                            sol, within = base._propagate_component(
                                data, gauged, constraints, component, phases, seed)
                            if sol is not None and not within:
                                sols.append(sol)
                        per.append(tuple(sols))
                    if any(not s for s in per):
                        continue
                    if sf._combine(data, gauged, constraints, per, phases,
                                   family.n_germs, sf.Counters()) is not None:
                        hit = True
                        break
                if hit:
                    break
            hits.append(hit)
        ok = hits[0] == hits[1] == (gamma == 0)
        check(f"Lemma D gauge invariance {words}", ok,
              f"base={hits[0]} gauged={hits[1]} gamma={gamma}")
        rows.append({"words": list(words), "base": hits[0], "regauged": hits[1],
                     "gamma_N": gamma})
    record["lemma_d_gauge"] = rows

    # (4) corruption: truncate the cut set to {0} (= treat the cut bundle as a
    # BOOK block; this is exactly what breaks Lemma H)
    rows = []
    flipped = 0
    for words, gens in FLIP_NO_CUT:
        full = solve_cut(words, gens)
        broken = solve_cut(words, gens, cut_offsets=False)
        flip = full.spherical is True and broken.spherical is not True
        flipped += bool(flip)
        rows.append({"words": list(words), "gens": gens, "full": full.verdict,
                     "cut_0_only": broken.verdict, "flipped": flip})
    check("broken cut-completeness flips a verdict", flipped == len(FLIP_NO_CUT),
          f"{flipped}/{len(FLIP_NO_CUT)}")
    record["corruption_cut_completeness"] = rows

    # (5) corruption: truncate the macro set to one rotation
    rows = []
    flipped = 0
    for words, gens in FLIP_ONE_MACRO:
        full = solve_cut(words, gens)
        broken = solve_cut(words, gens, macro_limit=1)
        flip = full.spherical is True and broken.spherical is not True
        flipped += bool(flip)
        rows.append({"words": list(words), "gens": gens, "full": full.verdict,
                     "one_macro_only": broken.verdict, "flipped": flip})
    check("broken macro-completeness flips a verdict", flipped == len(FLIP_ONE_MACRO),
          f"{flipped}/{len(FLIP_ONE_MACRO)}")
    record["corruption_macro_completeness"] = rows

    # (6) corruption: drop the block reversal (W6b Lemma B(iii)'s analogue)
    moved = []
    REVERSE_BLOCKS = False
    try:
        for words, gens, gamma in CROSSCHECK:
            broken = solve_cut(words, gens)
            if (broken.spherical is True) != (gamma == 0):
                moved.append({"words": list(words), "gens": gens,
                              "true_gamma_N": gamma, "broken": broken.verdict})
    finally:
        REVERSE_BLOCKS = True
    check("dropping the block reversal moves verdicts", len(moved) > 0,
          f"{len(moved)} of {len(CROSSCHECK)} fixtures move")
    record["corruption_block_reversal"] = {"moved": moved}

    # (7) corruption: corrupt the Euler characteristic itself
    honest = sf.faces_and_euler
    positive = next(((w, g) for w, g, gamma in CROSSCHECK if gamma == 0), None)
    assert positive is not None
    before = solve_cut(*positive)

    def off_by_one(data, sigma, n_germs):
        faces, euler = honest(data, sigma, n_germs)
        return faces, euler + 1

    sf.faces_and_euler = off_by_one
    try:
        after = solve_cut(*positive)
    finally:
        sf.faces_and_euler = honest
    check("corrupted Euler characteristic flips a positive to NOT_SPHERICAL",
          before.spherical is True and after.spherical is False,
          f"{before.verdict} -> {after.verdict}")
    record["corruption_genus"] = {"instance": [list(positive[0]), positive[1]],
                                  "before": before.verdict, "after": after.verdict}

    # (8) MEASURED, not a control: are the three extra sign variants at `v`
    # ever needed?  Restricting to the repo's `_k4_minus_edge_scheme`
    # convention alone and recording whether any verdict moves.
    moved_variant = []
    for words, gens, gamma in CROSSCHECK:
        one = solve_cut(words, gens, v_variants=((False, False),))
        if (one.spherical is True) != (gamma == 0):
            moved_variant.append({"words": list(words), "gens": gens,
                                  "true_gamma_N": gamma, "restricted": one.verdict})
    print(f"  measured: restricting to the repo v-convention moves "
          f"{len(moved_variant)} of {len(CROSSCHECK)} verdicts")
    record["v_variant_redundancy"] = {
        "note": "measured, not asserted: the four sign variants at v are carried "
                "so that no orientation convention is load-bearing",
        "verdicts_moved_when_restricted_to_repo_convention": moved_variant,
    }

    # (9) Lemma F (bare-row splitting), numerically
    rows = []
    for words, gens, gamma in BARE_ROW_FIXTURES:
        reduced = bare_row_reduction(words, gens)
        assert reduced is not None
        rest, new_gens = reduced
        full = rlg.neuwirth_min_genus(rlg.build_link(words, gens), budget=200_000,
                                      stop_at_zero=False)
        small = rlg.neuwirth_min_genus(rlg.build_link(rest, new_gens),
                                       budget=200_000, stop_at_zero=False)
        decision = solve_cut(words, gens)
        ok = (full.get("gamma_N") == small.get("gamma_N") == gamma
              and (decision.spherical is True) == (gamma == 0))
        check(f"Lemma F: gamma_N({words}) == gamma_N({rest}) == {gamma}", ok,
              f"{full.get('gamma_N')} / {small.get('gamma_N')} / {decision.verdict}")
        rows.append({"words": list(words), "reduced": list(rest),
                     "gamma_full": full.get("gamma_N"),
                     "gamma_reduced": small.get("gamma_N"),
                     "verdict": decision.verdict, "route": decision.route})
    record["lemma_f_bare_row"] = rows

    # (10) delegation: on BOOK / SPLIT_ENDPOINT states this solver must return
    # W6b's answer unchanged, so W6c can never silently move a W6b decision
    rows = []
    mismatches = []
    checked = 0
    for ceiling in CEILINGS:
        path = OUT / f"w6b_ball_coverage_c{ceiling}.jsonl"
        if not path.exists():
            continue
        for line in path.read_text().splitlines()[:400]:
            if not line.strip():
                continue
            row = json.loads(line)
            if row["family"] not in ("BOOK", "SPLIT_ENDPOINT"):
                continue
            state = tuple(row["state"])
            mine = solve_cut(state, "xyz")
            checked += 1
            if mine.verdict != row["verdict"] or mine.family != row["family"]:
                mismatches.append({"state": row["state"], "w6b": row["verdict"],
                                   "w6c": mine.verdict})
    check(f"W6b delegation is verdict-identical on {checked} BOOK states",
          not mismatches and checked > 0, f"{len(mismatches)} mismatches")
    record["w6b_delegation"] = {"checked": checked, "mismatches": mismatches}
    return record


def run_crosscheck(genus_budget: int, sweep: int, seed: int) -> dict:
    rows = []
    seen_gamma = set()
    for words, gens, gamma in CROSSCHECK:
        decision = solve_cut(words, gens)
        brute = rlg.neuwirth_min_genus(rlg.build_link(words, gens),
                                       budget=genus_budget, stop_at_zero=False)
        check(f"pinned gamma_N {words}", brute.get("gamma_N") == gamma,
              f"{brute.get('gamma_N')} vs {gamma}")
        check(f"pinned instance is family CUT {words}", decision.family == "CUT",
              decision.family)
        agrees = (decision.spherical is True) == (brute.get("gamma_N") == 0)
        check(f"solver == brute force {words}", agrees,
              f"{decision.verdict} vs gamma_N={brute.get('gamma_N')}")
        if decision.spherical is False:
            check(f"negative is exhaustive {words}", decision.counters.exhaustive)
        seen_gamma.add(gamma == 0)
        rows.append({"words": list(words), "gens": gens, "pinned_gamma_N": gamma,
                     "brute_gamma_N": brute.get("gamma_N"),
                     "compatible_orderings": brute.get("cases"),
                     "verdict": decision.verdict,
                     "cut_multiplicity": next(
                         (b["multiplicity"] for b in decision.bundle_report
                          if b["class"] == "CUT"), None),
                     "scheme_stats": decision.scheme_stats,
                     "agrees": agrees,
                     "exhaustive": decision.counters.exhaustive})
    check("pinned cross-check carries BOTH verdicts (not a one-sided null)",
          seen_gamma == {True, False}, str(seen_gamma))

    import random

    rng = random.Random(seed)
    alphabet = {"xy": "xXyY", "xyz": "xXyYzZ"}
    tested = 0
    attempts = 0
    disagreements = []
    tally = {"gamma_0": 0, "gamma_positive": 0, "rank2": 0, "rank3": 0}
    while tested < sweep and attempts < 400 * sweep:
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
        family = classify_cut_family(words, gens)
        if family.kind != "CUT":
            continue
        link = rlg.build_link(words, gens)
        cases = rlg.compatible_case_count(link)
        if not 4 <= cases <= 20_000:
            continue
        brute = rlg.neuwirth_min_genus(link, budget=20_000, stop_at_zero=False)
        decision = solve_cut(words, gens)
        tested += 1
        tally["rank2" if gens == "xy" else "rank3"] += 1
        tally["gamma_0" if brute["gamma_N"] == 0 else "gamma_positive"] += 1
        if (decision.spherical is True) != (brute["gamma_N"] == 0):
            disagreements.append({"words": list(words), "gens": gens,
                                  "verdict": decision.verdict,
                                  "gamma_N": brute["gamma_N"]})
    check(f"seeded CUT sweep: {tested} instances, solver == brute force everywhere",
          not disagreements and tested >= sweep, f"{tally} bad={disagreements[:3]}")
    check("seeded CUT sweep saw BOTH verdicts",
          tally["gamma_0"] > 0 and tally["gamma_positive"] > 0, str(tally))
    return {"pinned": rows,
            "sweep": {"seed": seed, "tested": tested, "tally": tally,
                      "disagreements": disagreements}}


def run_shape_completeness(budget: int, sweep: int, seed: int) -> dict:
    """Lemma H, checked as a SET IDENTITY against complete enumeration.

    For each instance, every spherical rotation system of the link multigraph
    `G` is enumerated directly and compared with the set generated by
    (kept cut scheme) x (rank assignment).  Completeness is `truth <= built`;
    equality additionally says the scheme set is not over-general in shape.
    """
    rows = []
    scored = 0
    for words, gens in SHAPE_FIXTURES:
        family = classify_cut_family(words, gens)
        check(f"shape fixture is family CUT {words}", family.kind == "CUT",
              family.kind)
        truth = all_spherical_rotation_shapes(words, gens, budget)
        if truth is None:
            rows.append({"words": list(words), "gens": gens,
                         "skipped": "rotation-system closure exceeds the budget"})
            continue
        schemes, stats = cut_schemes(family)
        built = shapes_from_schemes(family, schemes)
        complete = truth <= built
        equal = truth == built
        scored += 1
        check(f"Lemma H completeness: every spherical rotation is built {words}",
              complete, f"missing={len(truth - built)} of {len(truth)}")
        check(f"Lemma H exactness: built set == spherical set {words}", equal,
              f"extra={len(built - truth)}")
        rows.append({"words": list(words), "gens": gens,
                     "spherical_rotation_systems": len(truth),
                     "built_by_schemes": len(built), "complete": complete,
                     "exact": equal, "scheme_stats": stats,
                     "macro_rotations": len(family.macro),
                     "cut_multiplicity": family.cut_multiplicity})
    check("shape-completeness control is not vacuous", scored >= 6, f"{scored} scored")

    import random

    rng = random.Random(seed)
    alphabet = {"xy": "xXyY", "xyz": "xXyYzZ"}
    tested = 0
    attempts = 0
    incomplete = []
    inexact = []
    while tested < sweep and attempts < 400 * sweep:
        attempts += 1
        gens = "xy" if attempts % 2 else "xyz"
        words = []
        for _ in range(len(gens)):
            word = rlg.cyclic_reduce(
                "".join(rng.choice(alphabet[gens]) for _ in range(rng.randint(1, 5)))
            )
            if not word:
                break
            words.append(word)
        if len(words) != len(gens):
            continue
        words = tuple(words)
        family = classify_cut_family(words, gens)
        if family.kind != "CUT":
            continue
        truth = all_spherical_rotation_shapes(words, gens, budget)
        if truth is None or not truth:
            continue
        schemes, _ = cut_schemes(family)
        built = shapes_from_schemes(family, schemes)
        tested += 1
        if not truth <= built:
            incomplete.append({"words": list(words), "gens": gens,
                               "missing": len(truth - built)})
        if truth != built:
            inexact.append({"words": list(words), "gens": gens,
                            "extra": len(built - truth)})
    check(f"seeded shape sweep: {tested} instances, Lemma H complete everywhere",
          not incomplete and tested >= 20, f"bad={incomplete[:3]}")
    check(f"seeded shape sweep: built set is exactly the spherical set",
          not inexact, f"bad={inexact[:3]}")
    return {"pinned": rows,
            "sweep": {"seed": seed, "tested": tested, "incomplete": incomplete,
                      "inexact": inexact}}


def run_repo_agreement(sweep: int) -> dict:
    """The rank-2 K4-e family is the DEGENERATE case of CUT — checked twice.

    (a) verdict agreement with the repo's certified `neuwirth_rank_solver`;
    (b) the stronger statement: the scheme set this solver builds generates
        EXACTLY the same set of rotation systems as the repo's proven
        `_k4_minus_edge_scheme` family.  Rank 2 is the degenerate case in the
        precise sense that each piece of `H - {u,v}` is a single vertex, so
        Lemma G's contraction is the identity map.
    """
    from experiments.stable_ac.thickenable.neuwirth_p4_solver import (
        solve_four_germ_spherical,
    )
    from experiments.stable_ac.thickenable.neuwirth_rank_solver import (
        embedding_schemes, solve_spherical,
    )

    import random

    rng = random.Random(31337)
    rows = []
    disagreements = []
    shape_mismatches = []
    single_vertex_pieces = 0
    attempts = 0
    while len(rows) < sweep and attempts < 200_000:
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
        family = classify_cut_family(words, "xy")
        if family.kind != "CUT":
            continue
        repo = solve_spherical(words)
        if repo.spherical is None:
            continue
        mine = solve_cut(words, "xy")
        assert family.data is not None
        mine_schemes, _ = cut_schemes(family)
        repo_schemes = embedding_schemes(family.data)
        mine_shapes = shapes_from_schemes(family, mine_schemes)
        repo_shapes = shapes_from_schemes(family, repo_schemes)
        agrees = (mine.spherical is True) == bool(repo.spherical)
        pieces = sf.pieces_of(sorted(rlg.active_germs(rlg.build_link(words, "xy"))),
                              family.simple_edges, *family.cut_bundle)
        if all(len(p) == 1 for p in pieces):
            single_vertex_pieces += 1
        row = {"words": list(words), "repo_support": repo.support.kind,
               "repo_spherical": repo.spherical, "my_spherical": mine.spherical,
               "agrees": agrees, "repo_schemes": len(repo_schemes),
               "my_schemes": len(mine_schemes),
               "scheme_shape_sets_identical": mine_shapes == repo_shapes}
        rows.append(row)
        if not agrees:
            disagreements.append(row)
        if mine_shapes != repo_shapes:
            shape_mismatches.append(row)
    supports: dict[str, int] = {}
    for row in rows:
        supports[row["repo_support"]] = supports.get(row["repo_support"], 0) + 1
    check(f"rank-2 CUT agrees with the certified solver on {len(rows)} instances",
          not disagreements and len(rows) >= 30, f"supports={supports}")
    check("every rank-2 CUT instance has K4-e support (the degenerate case)",
          set(supports) == {"K4-e"}, str(supports))
    check("rank-2 CUT pieces are single vertices (Lemma G contraction is trivial)",
          single_vertex_pieces == len(rows), f"{single_vertex_pieces}/{len(rows)}")
    check("cut schemes generate EXACTLY the repo's certified K4-e scheme set",
          not shape_mismatches, f"{len(shape_mismatches)} mismatches")

    # the repo's two pinned P4 decisions still reproduce (via W6b delegation)
    pinned = []
    for words in sf.REPO_P4_CASES:
        repo = solve_four_germ_spherical(words)
        mine = solve_cut(words, "xy")
        agrees = (mine.spherical is True) == bool(repo.spherical)
        check(f"repo P4 decision reproduced {words}", agrees,
              f"mine={mine.verdict} route={mine.route}")
        pinned.append({"words": list(words), "repo_support": repo.support.kind,
                       "repo_spherical": repo.spherical, "my_verdict": mine.verdict,
                       "route": mine.route, "agrees": agrees})

    # Q_rank2 is the repo's own K4-e target: now decided by the CUT family
    q = solve_cut(rlg.Q, "xy")
    repo_q = solve_spherical(tuple(rlg.Q))
    agrees_q = (q.spherical is True) == bool(repo_q.spherical)
    check("Q_rank2 (repo K4-e target) agrees with the certified solver", agrees_q,
          f"mine={q.verdict} repo={repo_q.spherical}")
    return {"sweep": {"tested": len(rows), "repo_supports": supports,
                      "disagreements": disagreements,
                      "scheme_shape_mismatches": shape_mismatches,
                      "single_vertex_pieces": single_vertex_pieces},
            "pinned_p4": pinned,
            "Q_rank2": {"my_verdict": q.verdict, "repo_spherical": repo_q.spherical,
                        "agrees": agrees_q},
            "rows": rows[:40]}


def run_ball_coverage(ceiling: int, slice_seconds: float,
                      reduced_budget: int = DEFAULT_REDUCED_BUDGET) -> dict:
    """How much of W6's closed rank-three AC ball does the CUT family decide?

    Sliced and resumable: rows append to `out/w6c_ball_coverage_c{N}.jsonl`
    keyed by the state, and a rerun skips states already done, so a guard kill
    is a pause, not a restart.
    """
    import time

    source = OUT / f"w6_ac_ball_c{ceiling}.json"
    if not source.exists():
        raise SystemExit(f"missing {source}; run rank3_link_graph.py ball first")
    ball = json.loads(source.read_text())
    states = [tuple(row["state"]) for row in ball["states"] if "state" in row]
    path = OUT / f"w6c_ball_coverage_c{ceiling}.jsonl"
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
            decision = solve_cut(state, "xyz",
                                 reduced_budget=reduced_budget)
            row = {"state": list(state),
                   "total_length": sum(map(len, state)),
                   "family": decision.family,
                   "route": decision.route,
                   "verdict": decision.verdict,
                   "reason": decision.reason,
                   "blocker": blocker_bucket(state, "xyz"),
                   "scheme_stats": decision.scheme_stats,
                   "macro_rotations": decision.macro_rotation_count,
                   "exhaustive": decision.counters.exhaustive}
            handle.write(json.dumps(row, sort_keys=True) + "\n")
            handle.flush()
            done[state] = row
            appended += 1
    families: dict[str, int] = {}
    verdicts: dict[str, int] = {}
    routes: dict[str, int] = {}
    blockers: dict[str, int] = {}
    for row in done.values():
        families[row["family"]] = families.get(row["family"], 0) + 1
        verdicts[row["verdict"]] = verdicts.get(row["verdict"], 0) + 1
        routes[row["route"]] = routes.get(row["route"], 0) + 1
        if row["verdict"] == "UNSUPPORTED":
            blockers[row["blocker"]] = blockers.get(row["blocker"], 0) + 1
    positives = [r["state"] for r in done.values()
                 if r["verdict"].startswith("SPHERICAL")]
    decided = sum(v for k, v in verdicts.items() if k != "UNSUPPORTED")
    print(f"  ceiling {ceiling}: {len(done)}/{len(states)} classified, "
          f"appended {appended} this slice")
    print(f"  families={families}")
    print(f"  verdicts={verdicts}")
    print(f"  routes={routes}")
    print(f"  residual blockers={blockers}")
    if positives:
        print("  *** SPHERICAL_REQUIRES_REGINA / quarantined-suspected-bug on "
              f"{len(positives)} ball states ***")
    for row in done.values():
        if row["verdict"] == "NOT_SPHERICAL" and not row["exhaustive"]:
            raise AssertionError(f"non-exhaustive negative on {row['state']}")
    return {"ceiling": ceiling, "ball_states": len(states),
            "classified": len(done), "complete": len(done) == len(states),
            "family_counts": families, "verdict_counts": verdicts,
            "route_counts": routes, "residual_blockers": blockers,
            "decided": decided, "quarantined_positive_states": positives,
            "jsonl": str(path)}


def run_coverage_report() -> dict:
    """Combined W6b + W6c coverage per ceiling, and the residual profile."""
    report = {}
    for ceiling in CEILINGS:
        source = OUT / f"w6_ac_ball_c{ceiling}.json"
        if not source.exists():
            continue
        ball = json.loads(source.read_text())
        states = [tuple(row["state"]) for row in ball["states"] if "state" in row]
        w6b: dict[tuple[str, ...], dict] = {}
        w6c: dict[tuple[str, ...], dict] = {}
        for store, name in ((w6b, "w6b"), (w6c, "w6c")):
            path = OUT / f"{name}_ball_coverage_c{ceiling}.jsonl"
            if not path.exists():
                continue
            for line in path.read_text().splitlines():
                if line.strip():
                    row = json.loads(line)
                    store[tuple(row["state"])] = row
        b_decided = {s for s, r in w6b.items() if r["verdict"] != "UNSUPPORTED"}
        c_decided = {s for s, r in w6c.items() if r["verdict"] != "UNSUPPORTED"}
        regressions = sorted(b_decided - c_decided)
        positives = [list(s) for s, r in w6c.items()
                     if r["verdict"].startswith("SPHERICAL")]
        residual: dict[str, int] = {}
        for state in states:
            if state in c_decided:
                continue
            bucket = w6c.get(state, {}).get("blocker") or blocker_bucket(state, "xyz")
            residual[bucket] = residual.get(bucket, 0) + 1
        check(f"c{ceiling}: W6c classified every ball state",
              len(w6c) == len(states), f"{len(w6c)}/{len(states)}")
        check(f"c{ceiling}: W6c decides everything W6b decided",
              not regressions, f"{len(regressions)} regressions")
        check(f"c{ceiling}: no quarantined positive on a ball state",
              not positives, f"{len(positives)} positives")
        report[str(ceiling)] = {
            "ball_states": len(states),
            "w6b_decided": len(b_decided),
            "w6c_decided": len(c_decided),
            "newly_decided_by_w6c": len(c_decided - b_decided),
            "undecided": len(states) - len(c_decided),
            "complete": len(c_decided) == len(states),
            "all_negative": all(r["verdict"] == "NOT_SPHERICAL"
                                for r in w6c.values()
                                if r["verdict"] != "UNSUPPORTED"),
            "residual_profile": dict(sorted(residual.items(),
                                            key=lambda kv: -kv[1])),
            "quarantined_positive_states": positives,
            "w6b_decisions_lost": [list(s) for s in regressions],
        }
        row = report[str(ceiling)]
        print(f"  ceiling {ceiling:2d}: {row['w6c_decided']}/{row['ball_states']} "
              f"decided (W6b {row['w6b_decided']}, +{row['newly_decided_by_w6c']}), "
              f"complete={row['complete']}, residual={row['residual_profile']}")
    return report


def run_reduced(budget: int, sweep: int, seed: int) -> dict:
    """Validate the Lemma I reduced (`Hhat`) route — the general fallback.

    It assumes nothing about the non-book bundles: they are carried at full
    multiplicity and every rotation system of `Hhat` is enumerated.  So the
    only things to check are (a) that Lemma I's bijection really is onto —
    checked as a set identity against complete enumeration; (b) that the
    verdicts match brute force; (c) that it agrees with the independently
    constructed CUT schemes wherever both apply; (d) corruption controls.
    """
    global REVERSE_BLOCKS
    rows = []
    seen_gamma = set()
    for words, gens, gamma in HHAT_CROSSCHECK:
        decision = solve_cut(words, gens, reduced_budget=budget)
        brute = rlg.neuwirth_min_genus(rlg.build_link(words, gens), budget=200_000,
                                       stop_at_zero=False)
        check(f"Hhat route taken {words}", decision.route == "HHAT", decision.route)
        check(f"pinned gamma_N {words}", brute.get("gamma_N") == gamma,
              f"{brute.get('gamma_N')} vs {gamma}")
        agrees = (decision.spherical is True) == (gamma == 0)
        check(f"Hhat == brute force {words}", agrees, decision.verdict)
        if decision.spherical is False:
            check(f"Hhat negative is exhaustive {words}",
                  decision.counters.exhaustive)
        seen_gamma.add(gamma == 0)
        rows.append({"words": list(words), "gens": gens, "gamma_N": gamma,
                     "blocked_by": classify_cut_family(words, gens).reason,
                     "verdict": decision.verdict, "scheme_stats": decision.scheme_stats,
                     "agrees": agrees})
    check("Hhat pinned set carries BOTH verdicts", seen_gamma == {True, False},
          str(seen_gamma))

    # (a) Lemma I as a SET IDENTITY against complete enumeration
    shape_rows = []
    scored = 0
    for words, gens, _gamma in HHAT_CROSSCHECK:
        family = classify_cut_family(words, gens)
        truth = all_spherical_rotation_shapes(words, gens, 300_000)
        built_pair = reduced_schemes(family, budget)
        if truth is None or built_pair is None:
            continue
        schemes, stats = built_pair
        built = shapes_from_schemes(family, schemes)
        scored += 1
        check(f"Lemma I completeness: every spherical rotation is built {words}",
              truth <= built, f"missing={len(truth - built)} of {len(truth)}")
        check(f"Lemma I exactness: built == spherical {words}", truth == built,
              f"extra={len(built - truth)}")
        shape_rows.append({"words": list(words), "gens": gens,
                           "spherical_rotation_systems": len(truth),
                           "built": len(built), "stats": stats})
    check("Lemma I shape control is not vacuous", scored >= 8, f"{scored} scored")

    # (b) corruption: one Hhat scheme only
    flip_rows = []
    flipped = 0
    for words, gens in HHAT_FLIP_ONE_SCHEME:
        family = classify_cut_family(words, gens)
        built_pair = reduced_schemes(family, budget)
        assert built_pair is not None and family.data is not None
        schemes, _ = built_pair
        full, _ = _run_schemes(family.data, gens, schemes, family.n_germs)
        broken, _ = _run_schemes(family.data, gens, schemes[:1], family.n_germs)
        flip = full is not None and broken is None
        flipped += bool(flip)
        flip_rows.append({"words": list(words), "gens": gens,
                          "full": full is not None, "one_scheme": broken is not None,
                          "flipped": flip})
    check("truncating the Hhat scheme set flips a verdict",
          flipped == len(HHAT_FLIP_ONE_SCHEME), f"{flipped}/{len(HHAT_FLIP_ONE_SCHEME)}")

    # (c) corruption: drop the book-block reversal
    moved = []
    REVERSE_BLOCKS = False
    try:
        for words, gens, gamma in HHAT_CROSSCHECK:
            broken = solve_cut(words, gens, reduced_budget=budget)
            if (broken.spherical is True) != (gamma == 0):
                moved.append({"words": list(words), "true_gamma_N": gamma,
                              "broken": broken.verdict})
    finally:
        REVERSE_BLOCKS = True
    check("dropping the book-block reversal moves Hhat verdicts", len(moved) > 0,
          f"{len(moved)} of {len(HHAT_CROSSCHECK)} move")

    # (d) fail closed: a budget of 1 must yield UNSUPPORTED, never a verdict
    starved = [solve_cut(w, g, reduced_budget=1).verdict
               for w, g, _ in HHAT_CROSSCHECK]
    check("a starved budget fails closed (UNSUPPORTED, never a verdict)",
          set(starved) == {"UNSUPPORTED"}, str(sorted(set(starved))))

    # (e) seeded sweep: brute force, shape identity, and CUT/Hhat cross-route
    import random

    rng = random.Random(seed)
    alphabet = {"xy": "xXyY", "xyz": "xXyYzZ"}
    tested = 0
    attempts = 0
    disagreements, inexact, cross = [], [], []
    tally = {"gamma_0": 0, "gamma_positive": 0, "cut_cross_checked": 0}
    families: dict[str, int] = {}
    while tested < sweep and attempts < 500 * sweep:
        attempts += 1
        gens = "xy" if attempts % 2 else "xyz"
        words = []
        for _ in range(len(gens)):
            word = rlg.cyclic_reduce(
                "".join(rng.choice(alphabet[gens]) for _ in range(rng.randint(1, 5)))
            )
            if not word:
                break
            words.append(word)
        if len(words) != len(gens):
            continue
        words = tuple(words)
        family = classify_cut_family(words, gens)
        if family.data is None or not family.simple_edges:
            continue
        link = rlg.build_link(words, gens)
        cases = rlg.compatible_case_count(link)
        if not 4 <= cases <= 20_000:
            continue
        built_pair = reduced_schemes(family, budget)
        if built_pair is None:
            continue
        schemes, _ = built_pair
        witness, _counters = _run_schemes(family.data, gens, schemes, family.n_germs)
        brute = rlg.neuwirth_min_genus(link, budget=20_000, stop_at_zero=False)
        tested += 1
        families[family.kind] = families.get(family.kind, 0) + 1
        tally["gamma_0" if brute["gamma_N"] == 0 else "gamma_positive"] += 1
        if (witness is not None) != (brute["gamma_N"] == 0):
            disagreements.append({"words": list(words), "gens": gens,
                                  "family": family.kind,
                                  "hhat_spherical": witness is not None,
                                  "gamma_N": brute["gamma_N"]})
        truth = all_spherical_rotation_shapes(words, gens, 200_000)
        if truth:
            if truth != shapes_from_schemes(family, schemes):
                inexact.append({"words": list(words), "gens": gens})
        if family.kind == "CUT":
            tally["cut_cross_checked"] += 1
            cut = solve_cut(words, gens)
            if (cut.spherical is True) != (witness is not None):
                cross.append({"words": list(words), "cut": cut.verdict,
                              "hhat": witness is not None})
    check(f"Hhat sweep: {tested} instances, == brute force everywhere",
          not disagreements and tested >= sweep, f"{families} bad={disagreements[:3]}")
    check("Hhat sweep: Lemma I set identity holds everywhere", not inexact,
          f"bad={inexact[:3]}")
    check("Hhat sweep saw BOTH verdicts", tally["gamma_0"] > 0
          and tally["gamma_positive"] > 0, str(tally))
    # a dedicated CUT-targeted cross-route loop: the constructed CUT schemes
    # (Lemma H) and the enumerated Hhat schemes (Lemma I) are two independent
    # derivations of the same scheme set, so they must decide identically.
    attempts = 0
    while tally["cut_cross_checked"] < 40 and attempts < 200_000:
        attempts += 1
        gens = "xy" if attempts % 2 else "xyz"
        words = []
        for _ in range(len(gens)):
            word = rlg.cyclic_reduce(
                "".join(rng.choice(alphabet[gens]) for _ in range(rng.randint(1, 5)))
            )
            if not word:
                break
            words.append(word)
        if len(words) != len(gens):
            continue
        words = tuple(words)
        family = classify_cut_family(words, gens)
        if family.kind != "CUT":
            continue
        built_pair = reduced_schemes(family, budget)
        if built_pair is None:
            continue
        assert family.data is not None
        witness, _c = _run_schemes(family.data, gens, built_pair[0], family.n_germs)
        cut = solve_cut(words, gens)
        tally["cut_cross_checked"] += 1
        if (cut.spherical is True) != (witness is not None):
            cross.append({"words": list(words), "gens": gens, "cut": cut.verdict,
                          "hhat": witness is not None})
    check(f"CUT and Hhat agree on all {tally['cut_cross_checked']} shared instances",
          not cross and tally["cut_cross_checked"] >= 40, f"bad={cross[:3]}")
    return {"pinned": rows, "shape_identity": shape_rows,
            "corruption_one_scheme": flip_rows,
            "corruption_block_reversal": {"moved": moved},
            "starved_budget_verdicts": sorted(set(starved)),
            "sweep": {"seed": seed, "tested": tested, "families": families,
                      "tally": tally, "disagreements": disagreements,
                      "inexact": inexact, "cut_vs_hhat": cross}}


def run_targets(genus_budget: int) -> dict:
    rows = []
    for name, words, gens in TARGETS:
        decision = solve_cut(words, gens)
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
            row["link_connected"] = len(rlg.components(link)) == 1
            row["claim"] = "NOT THICKENABLE for this exact spelling (gamma_N > 0)."
            if not decision.counters.exhaustive:
                raise AssertionError(f"non-exhaustive negative on {name}")
        elif decision.spherical is True:
            row["claim"] = ("SPHERICAL_REQUIRES_REGINA / quarantined-suspected-bug: "
                            "Pipeline B (Regina isBall) is absent; NOT a result")
        else:
            row["claim"] = "UNSUPPORTED by this family; no claim"
        if brute.get("decided") and decision.spherical is not None:
            agrees = (decision.spherical is True) == (brute["gamma_N"] == 0)
            check(f"target {name}: solver == brute force", agrees)
            row["agrees_with_brute_force"] = agrees
        rows.append(row)
        print(f"  {name:26s} family={decision.family:14s} route={decision.route:16s}"
              f" schemes={decision.counters.scheme_budget:4d} -> {decision.verdict}")
    quarantined = [r["name"] for r in rows if r["spherical"] is True]
    if quarantined:
        print("  *** SPHERICAL_REQUIRES_REGINA / quarantined-suspected-bug: "
              f"{quarantined} ***")
    return {"targets": rows, "quarantined_positives": quarantined}


def main() -> int:
    parser = argparse.ArgumentParser(description="W6c cut-family solver")
    parser.add_argument("mode", choices=("controls", "crosscheck",
                                         "shape-completeness", "repo-agreement",
                                         "ball-coverage", "targets",
                                         "reduced", "coverage-report"))
    parser.add_argument("--genus-budget", type=int, default=100_000)
    parser.add_argument("--sweep", type=int, default=120)
    parser.add_argument("--shape-budget", type=int, default=200_000)
    parser.add_argument("--seed", type=int, default=6161)
    parser.add_argument("--ceiling", type=int, default=20)
    parser.add_argument("--slice-seconds", type=float, default=42.0)
    parser.add_argument("--reduced-budget", type=int,
                        default=DEFAULT_REDUCED_BUDGET)
    parser.add_argument("--out", type=str, default=None)
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.mode == "controls":
        data, path = run_controls(), OUT / "w6c_controls.json"
    elif args.mode == "crosscheck":
        data = run_crosscheck(args.genus_budget, args.sweep, args.seed)
        path = OUT / "w6c_bruteforce_crosscheck.json"
    elif args.mode == "shape-completeness":
        data = run_shape_completeness(args.shape_budget, args.sweep, args.seed)
        path = OUT / "w6c_shape_completeness.json"
    elif args.mode == "repo-agreement":
        data, path = run_repo_agreement(args.sweep), OUT / "w6c_repo_agreement.json"
    elif args.mode == "reduced":
        data = run_reduced(args.reduced_budget, args.sweep, args.seed)
        path = OUT / "w6c_reduced_route.json"
    elif args.mode == "ball-coverage":
        data = run_ball_coverage(args.ceiling, args.slice_seconds,
                                 args.reduced_budget)
        path = OUT / f"w6c_ball_coverage_c{args.ceiling}.json"
    elif args.mode == "coverage-report":
        data, path = run_coverage_report(), OUT / "w6c_coverage_report.json"
    else:
        data, path = run_targets(args.genus_budget), OUT / "w6c_targets.json"
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
