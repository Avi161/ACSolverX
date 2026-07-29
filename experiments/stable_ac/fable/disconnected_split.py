"""R1e disconnected-split decision pipeline for the round-2 "disconnected link" bucket.

This is the implementation of the contract in
``results/stable_ac/theory/fable/R1E_DISCONNECTED_LINK.md`` (Theorem D, Lemma S,
Corollary Z -- DRAFT v2, pending adversarial audit).  Every verdict emitted here is
**data for the orchestrator**, not a claimed mathematical result: the theorems backing
the split are still under audit, and any SPHERICAL row additionally requires the
explicit replay protocol of that note before any claim is made.

What the pipeline does, mirroring the note's implementation contract:

1. **Independent structural verification** per state: a private union-find over the germ
   vertices, built from the corner edges of the exact words alone (deliberately NOT
   ``build_link_n``, so the two component counts can disagree if either is wrong).  A
   bucket state must have exactly 2 link components, no straddling generator, ``z``
   occurring exactly once, and one relator exactly ``z`` or ``Z``.  Anything else is
   fail-closed into the ``VERIFY_FAIL`` bucket and never split.
2. **Projection** (Lemma S + Corollary Z): drop the ``z``-relator, canonicalise the
   remaining pair with ``ac_words.canon_pair``, and de-duplicate across states keeping
   the full provenance list.
3. **Decision** per distinct pair, in the round-2 stack order: the R1c-v2 cut-scheme
   solver first (``rank3_round2.decide_state`` with the budgets pinned VERBATIM to
   round 2), then the exact factorial census ``gamma_N_factorial_n`` -- called
   DIRECTLY, because ``rank3_round2.decide_by_census`` refuses ``L != 1`` (that refusal
   is Theorem-2-era and must not gate the L-general defect).  ``minimum_defect == 0``
   is SPHERICAL, ``> 0`` is NOT_SPHERICAL, and a census that does not fit the cap is
   UNDECIDED_BUDGET -- never NOT_SPHERICAL.
4. **Joint cross-validation** (Corollary Z's histogram identity): wherever the JOINT
   rank-3 census fits the round-2 cap, the triple census over ``("x", "y", "z")`` and
   the pair census over ``("x", "y")`` must have IDENTICAL full defect histograms (the
   unhalved defect ``|A| - |C| + 2L - |AC|`` keys).  A mismatch raises
   ``SplitAuditError`` -- it would falsify Corollary Z and must never be folded into a
   verdict.  (Histogram keys are ints in memory; a JSON round trip stringifies them, so
   comparisons happen here, before serialisation.)
5. **L-general witness check** for any SPHERICAL outcome: compatibility of the claimed
   rotation plus the general defect recomputed independently, per component (every
   component of the rotation surface must be a sphere); the ``<AC, BC>`` transitivity
   audit is RESCOPED to ``L == 1`` exactly as the note's boundary remark requires --
   ``witness_check_n.check_witness_n`` refuses ``L != 1`` and is deliberately not
   reused for the check itself (its building blocks are imported so the dictionaries
   agree by construction).  A hit is then Todd-Coxeter-certified and flagged with the
   replay-protocol banner; no move-list reconstruction is attempted here.

Budgets are pinned VERBATIM to round 2 by importing them from ``rank3_round2``:
``scheme_budget = 200_000``, ``branch_budget = 2_000_000``, census cap ``2_000_000``.
All knobs are recorded in the output summary.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from fractions import Fraction
from math import factorial

from experiments.stable_ac.fable import coset_enum as CE
from experiments.stable_ac.fable import neuwirth_cut_schemes as CS
from experiments.stable_ac.fable import neuwirth_rank_n as RN
from experiments.stable_ac.fable.ac_words import canon_pair, cyclic_reduce
from experiments.stable_ac.fable.rank3_round2 import (
    BRANCH_BUDGET,
    FALLBACK_CAP,
    SCHEME_BUDGET,
    UNDECIDED_BUDGET,
    Verdict,
    decide_state,
)
from experiments.stable_ac.fable.witness_check import (  # rank-generic primitives only
    AuditContradiction,
    WitnessError,
    _cycles,
    _orbits,
)
from experiments.stable_ac.fable.witness_check_n import (  # shared dictionary builders
    _build,
    _normalise_rotation,
    germ_names,
)

__all__ = [
    "VERIFY_FAIL",
    "SplitAuditError",
    "StructuralReport",
    "structural_report",
    "verify_bucket_shape",
    "project_pair",
    "decide_pair",
    "census_verdict",
    "joint_cross_check",
    "check_witness_l_general",
    "spherical_hit_protocol",
    "support_class_and_E",
    "decide_split_state",
    "load_bucket",
    "load_corpus_verdicts",
    "run_pipeline",
]

GENERATORS = ("x", "y", "z")
PAIR_GENERATORS = ("x", "y")
Z_RELATORS = ("z", "Z")

VERIFY_FAIL = "VERIFY_FAIL"

# budgets: SCHEME_BUDGET / BRANCH_BUDGET / FALLBACK_CAP imported verbatim from round 2.
TC_HIT_CAP = 50_000        # Todd-Coxeter cap for the hit protocol (round-2 audit value)
TC_SAMPLE_CAP = 20_000     # Todd-Coxeter cap for the sampled non-hit group checks
TC_SAMPLE = 5

HARVEST_PATH = "results/stable_ac/fable/rank3_harvest_round2.jsonl"
TARGETS_PATH = "results/stable_ac/fable/gamma_n_targets.jsonl"
DEFAULT_OUTPUT = "results/stable_ac/fable/disconnected_split_verdicts.jsonl"
DEFAULT_SUMMARY = "results/stable_ac/fable/disconnected_split_summary.json"

HIT_BANNER = (
    "SPHERICAL pair in AK(3)'s stable class -- DO NOT report as a result yet.  The "
    "R1E_DISCONNECTED_LINK.md hit protocol REQUIRES an explicitly reconstructed "
    "AC1-AC5 move list from AK(3) to this pair plus a full replay (the harvest "
    "parent/move fields are NOT a replayable chain) and a Todd-Coxeter index-1 "
    "certificate, before any claim.  No move-list reconstruction is attempted here."
)


class SplitAuditError(RuntimeError):
    """A must-not-happen event: Corollary Z's histogram identity or an internal
    consistency check failed.  Raised, never converted into a verdict."""


# --------------------------------------------------------------------------------------
# 1. independent structural verification (own union-find, NOT build_link_n)
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class StructuralReport:
    """The independently recomputed link-component structure of an exact state."""

    words: tuple
    generators: tuple
    present: tuple                # germ names carrying at least one dart
    link_components: int
    component_of: tuple           # ((germ name, component id), ...) for present germs
    straddling: tuple             # generators with g+ and g- in different components
    z_occurrences: int
    z_relator_indices: tuple      # indices j with words[j] exactly "z" or "Z"
    clean: bool                   # matches the R1e bucket shape (u(x,y), v(x,y), z^{+-1})
    reasons: tuple                # why not clean (empty iff clean)

    def component_map(self) -> dict:
        return {name: c for name, c in self.component_of}


def _germ_tables(generators):
    """``letter -> (nu(d), nu(h))`` germ indices; same convention as the solver stack."""
    table = {}
    for k, g in enumerate(generators):
        pos, neg = 2 * k, 2 * k + 1
        table[g] = (pos, neg)
        table[g.upper()] = (neg, pos)
    return table


def structural_report(words, generators=GENERATORS) -> StructuralReport:
    """Recompute components / straddle / shape with a private union-find.

    The corner edge of occurrence ``i`` joins ``nu(h_i)`` to ``nu(d_{i+1})`` (cyclically
    within each relator); the germ classes under those edges are exactly the components
    of the link graph Lambda(P) (Lemma L0 of the R1e note).  ``build_link_n`` is
    deliberately not called so this count is an independent opinion.
    """
    words = tuple(words)
    generators = tuple(generators)
    table = _germ_tables(generators)
    names = germ_names(generators)
    n_germs = 2 * len(generators)

    parent = list(range(n_germs))

    def find(a: int) -> int:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    present = set()
    for w in words:
        if not w:
            continue
        m = len(w)
        for i in range(m):
            c = w[i]
            if c not in table:
                raise WitnessError(f"letter {c!r} is not over {generators}")
            d_germ, h_germ = table[c]
            present.add(d_germ)
            present.add(h_germ)
            nxt = w[(i + 1) % m]
            union(h_germ, table[nxt][0])       # corner e_i: nu(h_i) -- nu(d_{i+1})

    roots = sorted({find(v) for v in present})
    root_id = {r: i for i, r in enumerate(roots)}
    component_of = tuple((names[v], root_id[find(v)]) for v in sorted(present))
    straddling = tuple(
        g for k, g in enumerate(generators)
        if 2 * k in present and 2 * k + 1 in present
        and find(2 * k) != find(2 * k + 1)
    )
    z_occurrences = sum(w.count("z") + w.count("Z") for w in words)
    z_relator_indices = tuple(j for j, w in enumerate(words) if w in Z_RELATORS)

    reasons = []
    if generators != GENERATORS:
        reasons.append(f"generators {generators} != {GENERATORS}; the R1e bucket shape "
                       "is defined over (x, y, z)")
    if len(words) != 3:
        reasons.append(f"{len(words)} relators; the bucket shape (u, v, z^{{+-1}}) "
                       "has exactly 3")
    if any(not w for w in words):
        reasons.append("empty relator")
    if len(z_relator_indices) != 1:
        reasons.append(f"{len(z_relator_indices)} relators are exactly z or Z; "
                       "the shape has exactly 1")
    if z_occurrences != 1:
        reasons.append(f"z occurs {z_occurrences} times, not once")
    missing = [names[v] for v in range(n_germs) if v not in present]
    if missing:
        reasons.append(f"germ(s) {missing} do not occur")
    n_components = len(roots)
    if n_components != 2:
        reasons.append(f"link has {n_components} components, not 2")
    if straddling:
        reasons.append(f"straddling generator(s) {list(straddling)}; Lemma S needs "
                       "no-straddle")
    if not reasons and generators == GENERATORS:
        # belt-and-braces: the z-component must be exactly {z+, z-}
        z_root = find(2 * len(generators) - 2)
        others = [names[v] for v in sorted(present)
                  if find(v) == z_root and v < 2 * len(generators) - 2]
        if others:
            reasons.append(f"z-component also contains {others}")

    return StructuralReport(
        words=words,
        generators=generators,
        present=tuple(names[v] for v in sorted(present)),
        link_components=n_components,
        component_of=component_of,
        straddling=straddling,
        z_occurrences=z_occurrences,
        z_relator_indices=z_relator_indices,
        clean=not reasons,
        reasons=tuple(reasons),
    )


def verify_bucket_shape(words, generators=GENERATORS) -> StructuralReport:
    """Alias with the fail-closed reading spelled out: ``clean`` gates the split."""
    return structural_report(words, generators)


def _structural_dict(report: StructuralReport) -> dict:
    return {
        "link_components": report.link_components,
        "component_of": [list(t) for t in report.component_of],
        "straddling": list(report.straddling),
        "z_occurrences": report.z_occurrences,
        "z_relator_indices": list(report.z_relator_indices),
        "clean": report.clean,
        "reasons": list(report.reasons),
    }


# --------------------------------------------------------------------------------------
# 2. projection (Lemma S + Corollary Z shadow)
# --------------------------------------------------------------------------------------


def project_pair(words) -> tuple:
    """Drop the unique ``z``-relator and canonicalise the remaining rank-2 pair."""
    rest = [w for w in words if w not in Z_RELATORS]
    if len(rest) != 2:
        raise SplitAuditError(f"projection of {tuple(words)} left {len(rest)} relators; "
                              "verify_bucket_shape must gate before projecting")
    return canon_pair(rest[0], rest[1])


# --------------------------------------------------------------------------------------
# 3. decision (round-2 stack order, budgets pinned verbatim)
# --------------------------------------------------------------------------------------


def census_verdict(words, generators, cap: int = FALLBACK_CAP,
                   keep_accepting: bool = True):
    """``gamma_N_factorial_n`` called DIRECTLY, interpreted with the L-general defect.

    ``rank3_round2.decide_by_census`` is NOT reused: its ``L != 1`` refusal predates
    Theorem D and would spuriously refuse every disconnected joint census.  The census
    itself is already L-general (``defect = nA - nC + 2L - nAC``,
    ``neuwirth_rank_n.py:1038``), so ``minimum_defect == 0`` decides SPHERICAL at any
    ``L``.  Budget exhaustion is UNDECIDED_BUDGET, never NOT_SPHERICAL.
    """
    census = RN.gamma_N_factorial_n(words, generators, cap_rotations=cap,
                                    keep_accepting=keep_accepting)
    if census["status"] != "OK":
        return Verdict(UNDECIDED_BUDGET, "none",
                       f"census family {census['expected_cases']} exceeds the "
                       f"per-state cap {cap}", census=census)
    verdict = CS.SPHERICAL if census["minimum_defect"] == 0 else CS.NOT_SPHERICAL
    return Verdict(verdict, "factorial_census", None, census=census)


def decide_pair(pair, scheme_budget: int = SCHEME_BUDGET,
                branch_budget: int = BRANCH_BUDGET, census_cap: int = FALLBACK_CAP):
    """R1c-v2 first, exact census fallback second; returns ``(Verdict, CutSupport)``."""
    pair = tuple(pair)
    verdict, support = decide_state(pair, generators=PAIR_GENERATORS,
                                    scheme_budget=scheme_budget,
                                    branch_budget=branch_budget)
    if verdict.verdict in (CS.SPHERICAL, CS.NOT_SPHERICAL):
        return verdict, support
    gate_reason = verdict.reason
    fallback = census_verdict(pair, PAIR_GENERATORS, cap=census_cap)
    if fallback.reason is None:
        fallback.reason = f"R1c-v2 fail-closed ({gate_reason}); decided by census"
    else:
        fallback.reason = f"R1c-v2 fail-closed ({gate_reason}); {fallback.reason}"
    return fallback, support


def _census_summary(census: dict) -> dict:
    return {
        "status": census["status"],
        "expected_cases": census["expected_cases"],
        "enumerated_cases": census.get("enumerated_cases"),
        "minimum_defect": census.get("minimum_defect"),
        "minimum_genus": census.get("minimum_genus"),
        "link_components": census.get("link_components"),
        "defect_histogram": {str(k): v
                             for k, v in sorted(census.get("defect_histogram",
                                                           {}).items())},
    }


# --------------------------------------------------------------------------------------
# 4. joint cross-validation (Corollary Z's exact defect-HISTOGRAM identity)
# --------------------------------------------------------------------------------------


def joint_cross_check(triple, pair, cap: int = FALLBACK_CAP, pair_verdict=None,
                      pair_census: dict | None = None) -> dict:
    """Compare the joint rank-3 census of ``triple`` with the rank-2 census of ``pair``.

    Corollary Z predicts bin-by-bin equality of the two unhalved-defect histograms and
    ``L_joint == L_pair + 1``.  The joint size is COMPUTED (never assumed equal to the
    pair size, even though the z-germs' degree-1 factor ``(1-1)! = 1`` makes them equal
    on the bucket shape).  Any violation raises ``SplitAuditError``.
    """
    triple = tuple(triple)
    pair = tuple(pair)
    joint_data = RN.build_link_n(triple, GENERATORS)
    joint_size = RN.census_size(joint_data, GENERATORS)
    pair_data = RN.build_link_n(pair, PAIR_GENERATORS)
    pair_size = RN.census_size(pair_data, PAIR_GENERATORS)
    out = {
        "triple": list(triple),
        "pair": list(pair),
        "joint_census_size": joint_size,
        "pair_census_size": pair_size,
        "sizes_equal": joint_size == pair_size,
        "cap": cap,
        "ran": False,
    }
    if joint_size > cap or pair_size > cap:
        out["reason"] = (f"joint size {joint_size} / pair size {pair_size} exceeds "
                         f"the cap {cap}")
        return out

    joint = RN.gamma_N_factorial_n(triple, GENERATORS, cap_rotations=cap,
                                   keep_accepting=True)
    if pair_census is None:
        pair_census = RN.gamma_N_factorial_n(pair, PAIR_GENERATORS, cap_rotations=cap,
                                             keep_accepting=True)
    if joint["status"] != "OK" or pair_census["status"] != "OK":
        raise SplitAuditError(
            f"cross-check census under the cap did not complete: joint "
            f"{joint['status']}, pair {pair_census['status']} ({triple})"
        )
    # int-keyed in memory; compare BEFORE any JSON round trip stringifies the keys
    equal = joint["defect_histogram"] == pair_census["defect_histogram"]
    out.update(
        ran=True,
        histograms_equal=equal,
        joint_minimum_defect=joint["minimum_defect"],
        pair_minimum_defect=pair_census["minimum_defect"],
        joint_link_components=joint["link_components"],
        pair_link_components=pair_census["link_components"],
        joint_enumerated=joint["enumerated_cases"],
        pair_enumerated=pair_census["enumerated_cases"],
        defect_histogram={str(k): v
                          for k, v in sorted(joint["defect_histogram"].items())},
    )
    if not equal:
        raise SplitAuditError(
            "COROLLARY-Z VIOLATION: joint and pair defect histograms differ for "
            f"{triple}: joint={joint['defect_histogram']} "
            f"pair={pair_census['defect_histogram']}"
        )
    if joint["link_components"] != pair_census["link_components"] + 1:
        raise SplitAuditError(
            f"L_joint = {joint['link_components']} != L_pair + 1 = "
            f"{pair_census['link_components'] + 1} for {triple}"
        )
    if pair_verdict is not None and pair_verdict in (CS.SPHERICAL, CS.NOT_SPHERICAL):
        census_says = (CS.SPHERICAL if pair_census["minimum_defect"] == 0
                       else CS.NOT_SPHERICAL)
        out["pair_verdict_agrees_with_census"] = census_says == pair_verdict
        if census_says != pair_verdict:
            raise SplitAuditError(
                f"pair verdict {pair_verdict} contradicts the exact census minimum "
                f"defect {pair_census['minimum_defect']} for {pair}"
            )
    if joint["minimum_defect"] == 0 and joint["accepting_orders"]:
        out["joint_accepting_rotation"] = {
            k: list(v) for k, v in joint["accepting_orders"][0].items()
        }
    return out


# --------------------------------------------------------------------------------------
# 5. L-general witness checker (transitivity audit rescoped to L == 1)
# --------------------------------------------------------------------------------------


def check_witness_l_general(words, rotation, generators=None,
                            trivial_group: bool = False,
                            require_spherical: bool = True) -> dict:
    """Verify a claimed compatible rotation with the GENERAL (2L-term) defect.

    ``witness_check_n.check_witness_n`` hard-refuses ``L != 1`` (Theorem-2-era) and
    would spuriously quarantine every legitimate ``L >= 2`` positive, so this checker
    exists per the R1e implementation contract.  It reuses the dictionary builders of
    ``witness_check_n`` by import (so the two modules agree on ``D/A/B`` by
    construction) and then does only permutation arithmetic:

    1. the rotation is a valid rotation system (exact dart set per germ);
    2. Neuwirth compatibility per germ and globally (``B C B = C^-1``);
    3. the general defect ``|A| - |C| + 2L - |AC|`` AND the per-component Euler
       numbers: every ``<A, C>``-orbit must satisfy ``defect_l = nA_l - nC_l + 2 -
       nAC_l`` and, when ``require_spherical``, ``defect_l == 0`` (every component of
       the rotation surface a sphere -- Theorem D);
    4. the ``<AC, BC>`` transitivity audit runs ONLY when ``L == 1`` and
       ``trivial_group`` is certified (the note's boundary remark: for no-straddle
       ``L >= 2`` transitivity is impossible, so it would be a false alarm there).

    The report also carries ``naive_connected_defect = |A| - |C| + 2 - |AC|`` (the
    ILLEGAL connected-case formula), so tests can pin that the 2L term is load-bearing.
    """
    words = tuple(words)
    if generators is None:
        generators = RN.generators_of(words)
    generators = tuple(generators)
    names = germ_names(generators)
    A, B, germ, size = _build(words, generators)
    orders = _normalise_rotation(rotation, names)

    # (1) valid rotation system
    present = sorted({germ[d] for d in range(size)})
    if sorted(orders) != present:
        raise WitnessError(
            f"rotation covers germs {[names[v] for v in sorted(orders)]}, "
            f"expected {[names[v] for v in present]}"
        )
    for v, seq in orders.items():
        want = sorted(d for d in range(size) if germ[d] == v)
        if sorted(seq) != want:
            raise WitnessError(f"germ {names[v]}: dart set {sorted(seq)} != {want}")

    C = [None] * size
    for v, seq in orders.items():
        m = len(seq)
        for k in range(m):
            C[seq[k]] = seq[(k + 1) % m]
    if any(c is None for c in C):
        raise WitnessError("rotation does not cover every dart")
    C = tuple(C)

    # (2) compatibility
    Cinv = [0] * size
    for e in range(size):
        Cinv[C[e]] = e
    for v, seq in orders.items():
        tv = v ^ 1
        if tv not in orders:
            raise WitnessError(f"germ {names[tv]} missing while {names[v]} present")
        for d in seq:
            if B[C[B[d]]] != Cinv[d]:
                raise WitnessError(
                    f"compatibility C_[{names[tv]}] = B C_[{names[v]}]^-1 B fails "
                    f"at dart {d}"
                )
    if any(B[C[B[e]]] != Cinv[e] for e in range(size)):
        raise WitnessError("global compatibility B C B = C^-1 fails")

    # (3) general defect and per-component Euler
    AC = tuple(A[C[e]] for e in range(size))
    BC = tuple(B[C[e]] for e in range(size))
    n_C, n_A, n_AC = _cycles(C), _cycles(A), _cycles(AC)
    L = _orbits((A, C), size)

    orbit_of = [-1] * size
    n_orbits = 0
    for start in range(size):
        if orbit_of[start] >= 0:
            continue
        stack = [start]
        orbit_of[start] = n_orbits
        while stack:
            d = stack.pop()
            for image in (A[d], C[d]):
                if orbit_of[image] < 0:
                    orbit_of[image] = n_orbits
                    stack.append(image)
        n_orbits += 1
    if n_orbits != L:
        raise SplitAuditError(f"orbit count {n_orbits} != _orbits result {L}")

    def _per_component_cycles(perm):
        counts = [0] * L
        seen = bytearray(size)
        for start in range(size):
            if seen[start]:
                continue
            counts[orbit_of[start]] += 1
            cur = start
            while not seen[cur]:
                seen[cur] = 1
                cur = perm[cur]
        return counts

    comp_A = _per_component_cycles(A)
    comp_C = _per_component_cycles(C)
    comp_AC = _per_component_cycles(AC)
    per_component = []
    for comp in range(L):
        d_l = comp_A[comp] - comp_C[comp] + 2 - comp_AC[comp]
        per_component.append({
            "darts": orbit_of.count(comp),
            "cycles_A": comp_A[comp],
            "cycles_C": comp_C[comp],
            "cycles_AC": comp_AC[comp],
            "defect": d_l,
        })
    defect = n_A - n_C + 2 * L - n_AC
    if defect != sum(c["defect"] for c in per_component):
        raise SplitAuditError("general defect is not the sum of per-component defects")

    report = {
        "words": words,
        "generators": generators,
        "germs": names,
        "darts": size,
        "cycles_C": n_C,
        "cycles_A": n_A,
        "cycles_AC": n_AC,
        "link_components": L,
        "defect": defect,
        "genus": defect // 2 if defect % 2 == 0 else None,
        "naive_connected_defect": n_A - n_C + 2 - n_AC,
        "per_component": per_component,
        "euler_characteristic": n_C - n_A + n_AC,
        "ac_bc_orbits": _orbits((AC, BC), size),
        "compatible": True,
        "trivial_group_assumed": bool(trivial_group),
    }
    if defect % 2:
        raise WitnessError(f"odd defect {defect}")
    if require_spherical:
        bad = [c for c in per_component if c["defect"] != 0]
        if bad:
            raise WitnessError(
                f"{len(bad)} component(s) with nonzero defect: {bad}; the rotation "
                "surface is not a disjoint union of spheres"
            )
    # (4) transitivity audit, RESCOPED to L == 1 per the R1e boundary remark
    report["ac_bc_transitive"] = report["ac_bc_orbits"] == 1 if L == 1 else None
    if L == 1 and trivial_group and report["ac_bc_orbits"] != 1:
        raise AuditContradiction(
            f"Euler passes (defect 0, L = 1) but <AC, BC> has "
            f"{report['ac_bc_orbits']} orbits; Corollary 3 proves this cannot happen "
            f"(words={words}, generators={generators})"
        )
    return report


# --------------------------------------------------------------------------------------
# 6. SPHERICAL hit protocol (no move-list reconstruction here)
# --------------------------------------------------------------------------------------


def spherical_hit_protocol(pair, verdict, cross_check: dict | None = None,
                           tc_cap: int = TC_HIT_CAP) -> dict:
    """Independent verification for a SPHERICAL pair; flags the replay protocol."""
    pair = tuple(pair)
    report = {"hit": True, "HIT_REPLAY_PROTOCOL_REQUIRED": HIT_BANNER}
    rotation = None
    if verdict.decision is not None and verdict.decision.witness is not None:
        rotation = verdict.decision.witness.rotation_map()
    elif verdict.census is not None and verdict.census.get("accepting_orders"):
        rotation = verdict.census["accepting_orders"][0]
    if rotation is None:
        report["pair_witness_error"] = "no rotation system available to verify"
    else:
        try:
            check = check_witness_l_general(pair, rotation,
                                            generators=PAIR_GENERATORS,
                                            trivial_group=False)
            check["words"] = list(check["words"])
            check["generators"] = list(check["generators"])
            check["germs"] = list(check["germs"])
            report["pair_witness_check"] = check
        except Exception as exc:                      # noqa: BLE001 -- audit surface
            report["pair_witness_error"] = f"{type(exc).__name__}: {exc}"
    tc = CE.is_trivial_group(pair, generators=PAIR_GENERATORS, cap=tc_cap)
    report["todd_coxeter"] = {
        "status": tc["status"], "index": tc["index"], "trivial": tc["trivial"],
        "cosets_defined": tc["cosets_defined"], "cap": tc["cap"],
    }
    if (tc["trivial"] is True and rotation is not None
            and "pair_witness_check" in report
            and report["pair_witness_check"]["link_components"] == 1):
        # group certified trivial: the Corollary-3 transitivity audit now applies
        audit = check_witness_l_general(pair, rotation, generators=PAIR_GENERATORS,
                                        trivial_group=True)
        report["transitivity_audit"] = {
            "ac_bc_orbits": audit["ac_bc_orbits"],
            "ac_bc_transitive": audit["ac_bc_transitive"],
        }
    if cross_check is not None and cross_check.get("joint_accepting_rotation"):
        triple = tuple(cross_check["triple"])
        joint_check = check_witness_l_general(
            triple, cross_check["joint_accepting_rotation"],
            generators=GENERATORS, trivial_group=False)
        report["joint_witness_check"] = {
            "link_components": joint_check["link_components"],
            "defect": joint_check["defect"],
            "per_component": joint_check["per_component"],
        }
    return report


# --------------------------------------------------------------------------------------
# 7. E-yield bookkeeping (K4 / K4-e / C4 supports only)
# --------------------------------------------------------------------------------------

# The support classifier and the E-yield formulas below are ported (with attribution)
# from the validated R1d harvest collector, scratchpad ``harvest/collect.py``
# (``support_multigraph`` / ``classify`` / ``e_yield``).  Those formulas were anchored
# against two independent E computations before use (see the lessons index entry
# ``harvest-dedup-on-reduced-forms``); only the K4 / K4-e / C4 closed forms are
# validated, so every other support returns ``None``.

_E_END = {"x": "x-", "X": "x+", "y": "y-", "Y": "y+"}
_E_START = {"x": "x+", "X": "x-", "y": "y+", "Y": "y-"}
_E_VERTS = ("x+", "x-", "y+", "y-")


def _support_multigraph(words) -> dict:
    edges: dict = {}
    for w in words:
        n = len(w)
        for i in range(n):
            u, v = w[i], w[(i + 1) % n]
            key = tuple(sorted((_E_END[u], _E_START[v])))
            edges[key] = edges.get(key, 0) + 1
    return edges


def _classify_support(edges) -> str:
    simple = set(edges)
    if any(a == b for a, b in simple):
        return "has-loops"
    deg: dict = {v: 0 for v in _E_VERTS}
    for a, b in simple:
        deg[a] += 1
        deg[b] += 1
    if any(deg[v] == 0 for v in _E_VERTS):
        return "disconnected"
    adj: dict = {v: set() for v in _E_VERTS}
    for a, b in simple:
        adj[a].add(b)
        adj[b].add(a)
    seen = {"x+"}
    stack = ["x+"]
    while stack:
        v = stack.pop()
        for w in adj[v]:
            if w not in seen:
                seen.add(w)
                stack.append(w)
    if len(seen) != 4:
        return "disconnected"
    m = len(simple)
    if m == 6:
        return "K4"
    if m == 5:
        return "K4-e"
    if m == 4:
        return "C4" if all(deg[v] == 2 for v in _E_VERTS) else "other"
    if m == 3:
        degs = sorted(deg[v] for v in _E_VERTS)
        return "P4" if degs == [1, 1, 2, 2] else "tree"
    return "other"


def _e_yield(cls: str, edges: dict, nx: int, ny: int):
    """The validated closed forms; ``None`` for any other support class."""
    if nx < 1 or ny < 1:
        return None
    den = factorial(nx - 1) * factorial(ny - 1)
    if cls == "K4":
        num = 2
        for m in edges.values():
            num *= factorial(m)
        return Fraction(num, den)
    if cls == "K4-e":
        deg: dict = {v: 0 for v in _E_VERTS}
        for a, b in edges:
            deg[a] += 1
            deg[b] += 1
        hubs = sorted(v for v in _E_VERTS if deg[v] == 3)
        central = tuple(sorted(hubs))
        num = factorial(edges[central] + 1)
        for e, m in edges.items():
            if e != central:
                num *= factorial(m)
        return Fraction(num, den)
    if cls == "C4":
        num = 1
        for m in edges.values():
            num *= factorial(m)
        return Fraction(num, den)
    return None


def support_class_and_E(pair):
    """``(support class, E as Fraction or None)`` for a rank-2 pair."""
    reduced = [cyclic_reduce(w) for w in pair]
    reduced = [w for w in reduced if w]
    if not reduced:
        return "empty", None
    edges = _support_multigraph(reduced)
    cls = _classify_support(edges)
    joined = "".join(reduced).lower()
    e = _e_yield(cls, edges, joined.count("x"), joined.count("y"))
    return cls, e


# --------------------------------------------------------------------------------------
# 8. the per-state pipeline and the 382-bucket runner
# --------------------------------------------------------------------------------------


def decide_split_state(words, census_cap: int = FALLBACK_CAP, cross_check: bool = True,
                       tc_cap: int = TC_HIT_CAP) -> dict:
    """The full pipeline on ONE exact state (structural gate -> split -> decide)."""
    words = tuple(words)
    report = verify_bucket_shape(words)
    row = {"state": list(words), "structural": _structural_dict(report)}
    if not report.clean:
        row.update(verdict=VERIFY_FAIL, method="structural_verification",
                   reason="; ".join(report.reasons))
        return row
    pair = project_pair(words)
    row["pair"] = list(pair)
    verdict, support = decide_pair(pair, census_cap=census_cap)
    row.update(verdict=verdict.verdict, method=verdict.method, reason=verdict.reason,
               support={"kind": support.kind, "reason": support.reason})
    if verdict.decision is not None:
        row["counters"] = verdict.decision.counters.as_dict()
    if verdict.census is not None:
        row["census"] = _census_summary(verdict.census)
    if cross_check:
        row["cross_check"] = joint_cross_check(words, pair, cap=census_cap,
                                               pair_verdict=verdict.verdict,
                                               pair_census=verdict.census)
    if verdict.verdict == CS.SPHERICAL:
        row.update(spherical_hit_protocol(pair, verdict,
                                          cross_check=row.get("cross_check"),
                                          tc_cap=tc_cap))
    else:
        row["hit"] = False
    return row


def load_bucket(harvest_path: str = HARVEST_PATH) -> list:
    """The round-2 rows gated ``disconnected link``, in file order."""
    out = []
    with open(harvest_path, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if r.get("record") == "state" and r.get("gate") == "disconnected link":
                out.append(r)
    return out


def load_corpus_verdicts(targets_path: str = TARGETS_PATH) -> dict:
    """``canon_pair -> stored verdict`` over the 2-word rows of the gamma_N corpus."""
    out = {}
    with open(targets_path, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            w = r.get("words")
            if isinstance(w, list) and len(w) == 2:
                out[canon_pair(w[0], w[1])] = r["verdict"]
    return out


CODEX_LENGTH14_PAIR = ("YXXYx", "YYYYXyyyx")   # AK3_RANK3_COMPRESSION.md, 2026-07-24


def run_pipeline(harvest_path: str = HARVEST_PATH, targets_path: str = TARGETS_PATH,
                 output: str = DEFAULT_OUTPUT, summary_path: str = DEFAULT_SUMMARY,
                 census_cap: int = FALLBACK_CAP, scheme_budget: int = SCHEME_BUDGET,
                 branch_budget: int = BRANCH_BUDGET, tc_sample: int = TC_SAMPLE,
                 verbose: bool = False) -> dict:
    """Decide the whole disconnected bucket through its rank-2 pairs."""
    started = time.time()
    bucket = load_bucket(harvest_path)
    corpus = load_corpus_verdicts(targets_path)

    # -- 1. structural verification + projection ---------------------------------------
    verify_fail = []
    provenance: dict = {}
    state_pair: dict = {}
    for index, state in enumerate(bucket):
        words = tuple(state["canonical"])
        report = verify_bucket_shape(words)
        if not report.clean:
            verify_fail.append({
                "canonical": list(words),
                "root": state["root"],
                "reasons": list(report.reasons),
            })
            state_pair[index] = None
            continue
        pair = project_pair(words)
        state_pair[index] = pair
        prov = provenance.setdefault(pair, {
            "states": [], "roots": {}, "exact_realizations_seen": 0,
        })
        prov["states"].append({
            "canonical": list(words),
            "exact_realization": list(state.get("exact_realization", ())),
            "root": state["root"],
            "depth": state.get("depth"),
            "structural_link_components": report.link_components,
        })
        prov["roots"][state["root"]] = prov["roots"].get(state["root"], 0) + 1
        prov["exact_realizations_seen"] += state.get("exact_realizations_seen", 0)

    pairs = sorted(provenance, key=lambda p: (len(p[0]) + len(p[1]), p))

    # -- 2. decide each distinct pair --------------------------------------------------
    rows = []
    sigma_e = Fraction(0)
    e_known = 0
    cross_ran = 0
    cross_eligible = 0
    cross_all_equal = True
    tc_sampled = 0
    verdict_hist: dict = {}
    method_hist: dict = {}
    class_hist: dict = {}
    pair_row: dict = {}
    for count, pair in enumerate(pairs, 1):
        verdict, support = decide_pair(pair, scheme_budget=scheme_budget,
                                       branch_budget=branch_budget,
                                       census_cap=census_cap)
        cls, e = support_class_and_E(pair)
        prov = provenance[pair]
        row = {
            "record": "pair",
            "pair": list(pair),
            "provenance": {
                "state_count": len(prov["states"]),
                "roots": dict(sorted(prov["roots"].items())),
                "exact_realizations_seen": prov["exact_realizations_seen"],
                "states": prov["states"],
            },
            "support": {"kind": support.kind, "reason": support.reason},
            "verdict": verdict.verdict,
            "method": verdict.method,
            "reason": verdict.reason,
            "support_class": cls,
            "E": float(e) if e is not None else None,
            "E_exact": f"{e.numerator}/{e.denominator}" if e is not None else None,
        }
        if verdict.decision is not None:
            row["counters"] = verdict.decision.counters.as_dict()
        if verdict.census is not None:
            row["census"] = _census_summary(verdict.census)

        # Corollary-Z joint cross-validation for every AFFORDABLE contributing state
        checks = []
        for st in prov["states"]:
            triple = tuple(st["canonical"])
            joint_size = RN.census_size(RN.build_link_n(triple, GENERATORS),
                                        GENERATORS)
            if joint_size > census_cap:
                checks.append({"triple": list(triple),
                               "joint_census_size": joint_size, "ran": False,
                               "reason": f"joint size {joint_size} exceeds the cap "
                                         f"{census_cap}"})
                continue
            cross_eligible += 1
            check = joint_cross_check(triple, pair, cap=census_cap,
                                      pair_verdict=verdict.verdict,
                                      pair_census=verdict.census)
            if check["ran"]:
                cross_ran += 1
                cross_all_equal = cross_all_equal and check["histograms_equal"]
            checks.append(check)
        row["cross_check"] = checks

        overlap = pair in corpus
        row["corpus_overlap"] = overlap
        row["corpus_verdict"] = corpus.get(pair)
        row["corpus_agrees"] = (corpus[pair] == verdict.verdict) if overlap else None

        if verdict.verdict == CS.SPHERICAL:
            cross0 = next((c for c in checks if c.get("ran")), None)
            row.update(spherical_hit_protocol(pair, verdict, cross_check=cross0))
        else:
            row["hit"] = False
            if tc_sampled < tc_sample:
                tc = CE.is_trivial_group(pair, generators=PAIR_GENERATORS,
                                         cap=TC_SAMPLE_CAP)
                row["todd_coxeter"] = {
                    "status": tc["status"], "index": tc["index"],
                    "trivial": tc["trivial"],
                    "cosets_defined": tc["cosets_defined"], "cap": tc["cap"],
                }
                tc_sampled += 1

        if e is not None:
            sigma_e += e
            e_known += 1
        verdict_hist[verdict.verdict] = verdict_hist.get(verdict.verdict, 0) + 1
        method_hist[verdict.method] = method_hist.get(verdict.method, 0) + 1
        class_hist[cls] = class_hist.get(cls, 0) + 1
        rows.append(row)
        pair_row[pair] = row
        if verbose and count % 50 == 0:
            print(f"[decide] {count}/{len(pairs)} pairs "
                  f"({round(time.time() - started, 1)}s)")

    # -- 3. mirror the pair verdicts back onto the 382 states --------------------------
    per_state = []
    state_verdict_hist: dict = {}
    for index, state in enumerate(bucket):
        pair = state_pair[index]
        if pair is None:
            entry = {"canonical": state["canonical"], "root": state["root"],
                     "pair": None, "verdict": VERIFY_FAIL,
                     "method": "structural_verification"}
        else:
            row = pair_row[pair]
            entry = {"canonical": state["canonical"], "root": state["root"],
                     "pair": list(pair), "verdict": row["verdict"],
                     "method": row["method"]}
        state_verdict_hist[entry["verdict"]] = (
            state_verdict_hist.get(entry["verdict"], 0) + 1)
        per_state.append(entry)

    # -- 4. the codex length-14 extra row (recorded, not asserted: the codex note
    #        AK3_RANK3_COMPRESSION.md certifies the stable equivalence and the Aut
    #        floor but states no per-pair Neuwirth verdict to assert against) ----------
    codex_verdict, codex_support = decide_pair(CODEX_LENGTH14_PAIR,
                                               scheme_budget=scheme_budget,
                                               branch_budget=branch_budget,
                                               census_cap=census_cap)
    codex_row = {
        "pair": list(CODEX_LENGTH14_PAIR),
        "source": "AK3_RANK3_COMPRESSION.md (codex, 2026-07-24): certified rank-2 "
                  "stable-class member of AK(3), Aut-floor 14; no Neuwirth verdict "
                  "is stated there, so this row is recorded without assertion",
        "verdict": codex_verdict.verdict,
        "method": codex_verdict.method,
        "support": {"kind": codex_support.kind, "reason": codex_support.reason},
        "in_bucket_pairs": CODEX_LENGTH14_PAIR in provenance,
    }

    spherical_rows = [r for r in rows if r["verdict"] == CS.SPHERICAL]
    undecided_rows = [r for r in rows
                      if r["verdict"] not in (CS.SPHERICAL, CS.NOT_SPHERICAL)]
    overlap_rows = [r for r in rows if r["corpus_overlap"]]

    summary = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "pipeline": "R1e disconnected split (disconnected_split.py)",
        "theory": "results/stable_ac/theory/fable/R1E_DISCONNECTED_LINK.md "
                  "(DRAFT v2, pending adversarial audit -- verdicts are data, "
                  "not results)",
        "harvest_path": harvest_path,
        "targets_path": targets_path,
        "budgets": {
            "scheme_budget": scheme_budget,
            "branch_budget": branch_budget,
            "census_cap": census_cap,
            "macro_budget": RN.DEFAULT_MACRO_BUDGET,
            "tc_hit_cap": TC_HIT_CAP,
            "tc_sample_cap": TC_SAMPLE_CAP,
            "tc_sample": tc_sample,
            "pinned_from": "rank3_round2 (round-2 values, imported verbatim)",
        },
        "bucket_states": len(bucket),
        "verify_fail_states": len(verify_fail),
        "clean_states": len(bucket) - len(verify_fail),
        "distinct_pairs": len(pairs),
        "verdict_histogram": dict(sorted(verdict_hist.items())),
        "method_histogram": dict(sorted(method_hist.items())),
        "per_state_verdict_histogram": dict(sorted(state_verdict_hist.items())),
        "support_class_histogram": dict(sorted(class_hist.items())),
        "cross_check": {
            "eligible_states": cross_eligible,
            "joint_censuses_ran": cross_ran,
            "all_histograms_equal": cross_all_equal,
        },
        "corpus_overlap": {
            "pairs": len(overlap_rows),
            "agreements": sum(1 for r in overlap_rows if r["corpus_agrees"]),
            "disagreements": [
                {"pair": r["pair"], "verdict": r["verdict"],
                 "corpus_verdict": r["corpus_verdict"]}
                for r in overlap_rows if not r["corpus_agrees"]
            ],
        },
        "sigma_E": {
            "rows_with_E": e_known,
            "float": float(sigma_e),
            "exact": f"{sigma_e.numerator}/{sigma_e.denominator}",
        },
        "spherical_pairs": [r["pair"] for r in spherical_rows],
        "undecided_pairs": [
            {"pair": r["pair"], "verdict": r["verdict"], "reason": r["reason"]}
            for r in undecided_rows
        ],
        "verify_fail_states_list": verify_fail,
        "codex_length14_extra": codex_row,
        "per_state": per_state,
        "elapsed_seconds": round(time.time() - started, 2),
    }

    if output:
        directory = os.path.dirname(output)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(output, "w", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps(row) + "\n")
    if summary_path:
        directory = os.path.dirname(summary_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(summary_path, "w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=1)
            fh.write("\n")
    return {"summary": summary, "rows": rows, "spherical": spherical_rows}


def _print_summary(result: dict, output: str, summary_path: str) -> None:
    s = result["summary"]
    print("=" * 78)
    print("R1e DISCONNECTED-SPLIT PIPELINE  (Theorem D / Lemma S / Corollary Z)")
    print("=" * 78)
    print(f"bucket states        : {s['bucket_states']}  "
          f"(clean {s['clean_states']}, VERIFY_FAIL {s['verify_fail_states']})")
    print(f"distinct pairs       : {s['distinct_pairs']}")
    print(f"verdicts (pairs)     : {s['verdict_histogram']}")
    print(f"verdicts (states)    : {s['per_state_verdict_histogram']}")
    print(f"methods              : {s['method_histogram']}")
    print(f"support classes      : {s['support_class_histogram']}")
    cc = s["cross_check"]
    print(f"Corollary-Z checks   : {cc['joint_censuses_ran']} joint censuses ran "
          f"(of {cc['eligible_states']} affordable), all histograms equal: "
          f"{cc['all_histograms_equal']}")
    co = s["corpus_overlap"]
    print(f"corpus overlap       : {co['pairs']} pairs, {co['agreements']} agree, "
          f"disagreements: {co['disagreements']}")
    print(f"Sigma-E              : {s['sigma_E']['float']:.6g} over "
          f"{s['sigma_E']['rows_with_E']} rows  "
          f"(exact {s['sigma_E']['exact']})")
    print(f"codex length-14 pair : {s['codex_length14_extra']['pair']} -> "
          f"{s['codex_length14_extra']['verdict']} "
          f"({s['codex_length14_extra']['method']}; recorded, not asserted)")
    print(f"budgets              : {s['budgets']}")
    print(f"elapsed              : {s['elapsed_seconds']}s")
    print(f"output               : {output}")
    print(f"summary              : {summary_path}")
    if s["spherical_pairs"]:
        print("!" * 78)
        print("!!! SPHERICAL PAIR(S) IN THE STABLE CLASS -- REPLAY PROTOCOL "
              "REQUIRED !!!")
        for pair in s["spherical_pairs"]:
            print(f"  {tuple(pair)}")
        print("!" * 78)
    else:
        print("no SPHERICAL pair in the bucket.")
    if s["undecided_pairs"]:
        print(f"UNDECIDED rows       : {s['undecided_pairs']}")


def main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--harvest", default=HARVEST_PATH)
    parser.add_argument("--targets", default=TARGETS_PATH)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", default=DEFAULT_SUMMARY)
    parser.add_argument("--census-cap", type=int, default=FALLBACK_CAP)
    args = parser.parse_args(argv)
    result = run_pipeline(harvest_path=args.harvest, targets_path=args.targets,
                          output=args.output, summary_path=args.summary,
                          census_cap=args.census_cap, verbose=True)
    _print_summary(result, args.output, args.summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
