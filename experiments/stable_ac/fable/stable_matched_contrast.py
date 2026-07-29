"""The STABLE-CLASS MATCHED CONTRAST: the rank-3 analogue of the classical contrast.

The classical matched contrast (``ak2_battery.py`` -> ``ak3_matched_control.py``;
"CONTRAST RESULT" in ``results/stable_ac/theory/fable/R3PRIME_DIGON_EXCESS.md``) ran one
operator on two rank-2 roots and compared SPHERICAL rates: AK(2)'s provably AC-trivial
class showed 397/13,040 thickenable members, AK(3)'s open classical class 0/124,296.
That tested AK(3)'s CLASSICAL class.  The stable AC conjecture concerns the STABLE
class, so this module runs the IDENTICAL matched design one level up, in the rank-3
stable-move space:

* root ``AK3+z = ("xxxYYYY", "xyxYXY", "z")`` -- AK(3) plus one plain stabilization;
  every harvested member is a member of AK(3)'s STABLE class (rank-3 AC moves +
  Lemma P canonicalization; the AC4 stabilization step is the root's definition).
  Whether this class contains a thickenable member is OPEN -- the target.
* root ``AK2+z = ("xxYYY", "xyxYXY", "z")`` -- AK(2) plus one stabilization.  AK(2) is
  provably AC-trivializable (committed trivialization path,
  ``ak2_trivialization_path.json``), so AK2+z's class is provably trivializable:
  the POSITIVE control.  SPHERICAL members here are EXPECTED and validate the pipeline.

A SPHERICAL member of the AK3+z harvest would be a thickenable member of AK(3)'s STABLE
class, and via the Corollary D3 chain (R1E_DISCONNECTED_LINK.md; final step Lackenby
arXiv:2606.06122 Thm 1.3, FLAGGED [unverified this session]) plus the full replay
protocol, AK(3) stably AC-trivial -- the session goal's headline.  Matched zeros extend
the classical null-model tension to the stable class.  EVERYTHING EMITTED HERE IS DATA,
NOT A MATHEMATICAL CLAIM; both outcomes are recorded symmetrically.

The matched operator (the rank-3 generalization of the ak2_battery rotation-expanded
operator, applied IDENTICALLY to both roots)
--------------------------------------------------------------------------------------

* **Seen-set** keyed on ``rank3_stable_harvest.canon_state``: per-relator lex-min over
  rotations x inversion (cyclically reduced), then the relator multiset sorted -- i.e.
  relator permutations x rotations x inversions, the proved symmetry quotient of
  ``experiments/lessons/harvest-dedup-on-reduced-forms.md`` at rank 3.
* **Expansion**: every rank-3 AC concatenation ``r_i <- free_reduce(r_i . r_j^{+-1})``
  over every ordered pair ``i != j`` and every pair of cyclic rotations of the two
  involved canonical relators (``ak2_battery.rotations``, imported), both signs.  The
  third relator is untouched by the move and stays at its canonical rotation -- its
  rotation freedom cannot change the product and is already quotiented by the seen-set,
  so iterating it would only duplicate canonical children (the rank-3 analogue of the
  ak2_battery note that inverted-TARGET realizations need no extra loop: the canonical
  key quotients by per-relator inversion, and the source's inversion is the sign).
* **Priority**: best-first on total canonical length, insertion-order ties -- verbatim
  the ak2_battery traversal.
* **Budget**: EXACTLY :data:`HARVEST_POPS` = 1,000 pops PER ROOT (two searches, each
  within the hard 1,000-pop limit; both asserted).
* **z stays a live generator**: moves may entangle it -- that IS the stable-move
  space.  No z-inertness bias of any kind (no priority bonus, no filtering);
  ``z_occurrences`` is recorded per member instead.
* **Membership**: each child is reachable from its parent class by an exact composite
  of legal rank-3 AC moves -- single-letter AC3 conjugations realize the rotations, one
  AC2 concatenation forms the product (the move space of
  ``rank3_stable_harvest.moves``, anchored by the tests) -- and the final
  canonicalization is an AC composite by Lemma P of ``R1E_DISCONNECTED_LINK.md``
  (rotation = AC3, inversion = AC1, relator swap = the explicit 6-move composite).  So
  every AK3+z row is a genuine member of AK(3)'s stable class, and every AK2+z row of
  AK2+z's (provably trivializable) class.

Length caps (recorded for the doc)
----------------------------------

* **Rule**: per-relator cap = total root length + 4, the SAME relative-headroom rule
  the classical contrast used (AK(2) ran at 15 = 11 + 4, AK(3) at 17 = 13 + 4).  Here
  AK3+z (total 7 + 6 + 1 = 14) runs at :data:`CAP_AK3Z` = 18, AK2+z (total
  5 + 6 + 1 = 12) at :data:`CAP_AK2Z` = 16.
* **Relative-headroom reasoning** (the choice made): both runs give the operator the
  same additive slack above their root's scale, so the per-pop expansion geometry is
  comparable and the matched quantities are the operator + the 1,000-pop budget.
* **Absolute-cap argument** (the alternative, recorded): an absolute match (16 for
  both) would leave AK3+z only 2 letters of headroom above its 14-letter root versus
  AK2+z's 4, mechanically suppressing child generation and biasing the open-target run
  toward zero hits.  With cap 18 the AK3+z box is strictly LARGER -- the conservative
  direction: a zero-hit outcome cannot be attributed to a smaller search space.

Decisions (same stack and budgets as the audited R1e/round-2 corpus)
--------------------------------------------------------------------

Per distinct canonical member, with all knobs pinned VERBATIM to round 2
(``scheme_budget`` 200,000 / ``branch_budget`` 2,000,000 / census cap 2,000,000):

1. **Clean disconnected shape** (the R1e bucket shape, independently re-verified by
   ``disconnected_split.structural_report``: exactly one relator ``z``/``Z``, z occurs
   once, 2 link components, no straddling generator, all germs present): decided via
   ``disconnected_split.decide_split_state`` -- Theorem D + Lemma S, the AUDITED route
   -- through the projected rank-2 pair (R1c-v2 solver first, L-general census
   fallback).  These are the ``destabilizable`` members (z-inert clean shape; AC1 + AC5
   destabilization reaches their rank-2 projection, per the R1e provenance chain).
2. **Everything else**: ``rank3_round2.decide_state`` with generators
   ``("x", "y", "z")`` (R1c-v2 cut-scheme solver; certified-non-planar NO included).
   Where it fails closed (disconnected-but-not-clean, straddling shapes, budgets):
   the exact L-general factorial census ``disconnected_split.census_verdict`` with the
   GENERAL defect ``|A| - |C| + 2L - |AC|`` -- ``minimum_defect == 0`` is decisive
   SPHERICAL at any L per Theorem D -- whenever the family fits the 2,000,000 cap,
   honest ``UNDECIDED_BUDGET`` otherwise.  A state in which some generator occurs in
   NO relator is fail-closed ``UNSUPPORTED`` (Theorem D requires every generator to
   occur; a census over the occurring generators would silently decide the wrong
   complex).
3. Method recorded per row; UNDECIDED/UNSUPPORTED rows are named and counted, never
   folded into "all NO".

Bookkeeping per member: canonical triple, ``z_occurrences``, ``destabilizable`` flag,
the rank-2 projection + its canon pair when destabilizable, verdict, method.  Shadow-ΣE
accounting runs ``disconnected_split.support_class_and_E`` on the destabilizable
members' rank-2 projections ONLY (the validated E formulas are rank-2-only:
K4 / K4-e / C4 supports); E-unknown rows are counted honestly.

Provenance for replay: every non-root member stores its parent's canonical triple
(``parent_key`` -- a canonical triple of cyclically reduced words IS an exact state in
the class), the realization ``(i, j, a, b, sign)`` the expansion used, and the full
move composite (``move_composite``: AC3 conjugations rotating relator ``i`` to ``a``
and relator ``j`` to ``b``, then the AC2 concatenation) whose byte-exact replay from
``parent_exact`` arrives at ``first_exact`` with ``canon_state(first_exact) ==
canonical``.  Every single-step composite is replay-verified at build time by the
independent replayer; full root-to-member chains are verified on a seeded 100-member
sample per root and on EVERY SPHERICAL member.

Hit protocol (mandatory for any SPHERICAL, either root): L-general witness check
(``disconnected_split.check_witness_l_general``; for clean rows the pair-level protocol
of ``decide_split_state`` plus the joint Corollary-Z cross-check where sampled and
affordable), Todd-Coxeter triviality certificate on the TRIPLE (``coset_enum``, cap
50,000), full move-chain replay from the root, re-decision agreement, loud summary
fields.  AK2+z hits are EXPECTED (positive control); AK3+z hits are the headline and
carry everything, in full.

New-files-only contract: this module IMPORTS the existing stack (``ac_words``,
``ak2_battery``, ``rank3_stable_harvest``, ``rank3_round2``, ``disconnected_split``,
``coset_enum``, ``neuwirth_rank_n``) and modifies nothing.  Plain python3, CPU only,
no JAX.
"""

from __future__ import annotations

import argparse
import gzip
import heapq
import json
import os
import random
import time
from collections import Counter
from fractions import Fraction

from experiments.stable_ac.fable import ac_words as W
from experiments.stable_ac.fable import ak2_battery as AB
from experiments.stable_ac.fable import coset_enum as CE
from experiments.stable_ac.fable import neuwirth_cut_schemes as CS
from experiments.stable_ac.fable import neuwirth_rank_n as RN
from experiments.stable_ac.fable.disconnected_split import (
    TC_HIT_CAP,
    census_verdict,
    check_witness_l_general,
    decide_split_state,
    joint_cross_check,
    structural_report,
    support_class_and_E,
)
from experiments.stable_ac.fable.rank3_round2 import (
    BRANCH_BUDGET,
    FALLBACK_CAP,
    SCHEME_BUDGET,
    UNDECIDED_BUDGET,
    decide_state,
)
from experiments.stable_ac.fable.rank3_stable_harvest import (
    AK3,
    canon_state,
    letter_order,
)

__all__ = [
    "GENERATORS",
    "AK3Z",
    "AK2Z",
    "ROOTS",
    "CAP_AK3Z",
    "CAP_AK2Z",
    "HARVEST_POPS",
    "REPLAY_SAMPLE_SIZE",
    "REPLAY_SEED",
    "OPERATOR_DESCRIPTOR",
    "ReplayVerificationError",
    "OperatorMismatchError",
    "cap_for_root",
    "total_length3",
    "apply_stable_move",
    "replay_stable",
    "stable_move_children",
    "concat_products_rank3",
    "canon_children_rank3",
    "harvest_root_prov",
    "conjugation_moves_to3",
    "step_composite3",
    "verify_step3",
    "attach_and_verify_composites",
    "replay_chain3",
    "verify_recorded_edges",
    "operator_identity_report",
    "decide_member",
    "hit_protocol_rank3",
    "run_root",
    "classical_contrast_requote",
    "run_contrast",
]

GENERATORS = ("x", "y", "z")
ORDER3 = letter_order(GENERATORS)

AK2 = AB.AK2                                  # ("xxYYY", "xyxYXY") -- imported, not copied
AK3Z = tuple(AK3) + ("z",)                    # ("xxxYYYY", "xyxYXY", "z"), total 14
AK2Z = tuple(AK2) + ("z",)                    # ("xxYYY", "xyxYXY", "z"),   total 12

HARVEST_POPS = 1_000          # hard session rule: EXACTLY this many pops PER ROOT
CAP_RULE_SLACK = 4            # per-relator cap = total root length + 4 (classical rule)
CAP_AK3Z = 18                 # 14 + 4
CAP_AK2Z = 16                 # 12 + 4

ROOTS = (
    ("AK2+z", AK2Z, CAP_AK2Z),      # positive control first (fast, expected hits)
    ("AK3+z", AK3Z, CAP_AK3Z),      # the open target
)

REPLAY_SAMPLE_SIZE = 100
REPLAY_SEED = 20260729        # same fixed seed convention as the classical control
OPERATOR_SAMPLE_SIZE = 25     # popped keys per root re-verified by the identity check
CROSS_CHECK_SAMPLE = 3        # AK2+z clean-spherical rows that get the joint Z-check
AK2Z_HIT_BRIEFS = 10          # AK2+z hit briefs kept in the summary (count is exact)

DEFAULT_AK3Z_MEMBERS = "results/stable_ac/fable/stable_contrast_ak3z_members.jsonl.gz"
DEFAULT_AK2Z_MEMBERS = "results/stable_ac/fable/stable_contrast_ak2z_members.jsonl.gz"
DEFAULT_SUMMARY = "results/stable_ac/fable/stable_contrast_summary.json"
CLASSICAL_AK2_SUMMARY = "results/stable_ac/fable/ak2_battery_summary.json"
CLASSICAL_AK3_SUMMARY = "results/stable_ac/fable/ak3_matched_summary.json"

OPERATOR_DESCRIPTOR = (
    "rank-3 rotation-expanded canonical harvest: seen-set on canon_state (relator "
    "permutations x rotations x inversions, cyclically reduced); children = every AC "
    "concatenation r_i <- r_i . r_j^{+-1} (ordered i != j, both signs) over every pair "
    "of cyclic rotations of the two involved canonical relators, third relator "
    "untouched; priority = total canonical length, insertion-order ties; first exact "
    "realization wins"
)

LOUD_ALERT_AK3Z = (
    "SPHERICAL MEMBER(S) IN AK3+z'S HARVEST -- thickenable member(s) of AK(3)'s "
    "STABLE class.  This is DATA ONLY -- no mathematical claim is made here.  The "
    "interpretation chain (thickenable + trivial group + balanced => AC-trivial via "
    "Corollary D3, final step Lackenby Thm 1.3) is FLAGGED UNVERIFIED in the theory "
    "notes; every hit below carries the full protocol artifacts (L-general witness "
    "check, Todd-Coxeter certificate on the triple, full move-chain replay from the "
    "AK3+z root) and requires an independent adversarial audit before any claim."
)


class ReplayVerificationError(AssertionError):
    """A stored provenance step or chain failed its byte-exact replay check."""


class OperatorMismatchError(AssertionError):
    """The recorded harvest edges disagree with the shared expansion operator."""


# --------------------------------------------------------------------------------------
# 0. small pieces: caps, the rank-3 move calculus, replay
# --------------------------------------------------------------------------------------


def total_length3(state) -> int:
    return sum(len(w) for w in state)


def cap_for_root(root) -> int:
    """The classical contrast's relative-headroom rule: total root length + 4."""
    return total_length3(root) + CAP_RULE_SLACK


def apply_stable_move(state, move, cap: int):
    """Apply one legal rank-3 AC move; a no-op returns an equal tuple.

    Move vocabulary (JSON-able lists/tuples; project convention AC1 = invert,
    AC2 = multiply, AC3 = conjugate -- inversion never appears in a composite,
    it lives only inside the Lemma P canonicalization step):

    * ``("conj", i, c)``  -- AC3:  ``r_i <- free_reduce(c . r_i . c^-1)``;
    * ``("mult", i, j, s)`` -- AC2:  ``r_i <- free_reduce(r_i . r_j^s)``, ``s = +-1``.

    Semantics mirror ``rank3_stable_harvest.moves`` /  ``ac_words.apply_move``: a
    rewrite that would be empty or exceed the per-relator ``cap`` is a no-op (the
    tests anchor this move space against ``rank3_stable_harvest.moves`` directly).
    """
    state = tuple(state)
    kind = move[0]
    if kind == "conj":
        _, i, c = move
        new = W.free_reduce(c + state[i] + W.inverse_letter(c))
    elif kind == "mult":
        _, i, j, sign = move
        if i == j:
            raise ValueError(f"mult needs i != j, got {move}")
        piece = state[j] if sign == 1 else W.inverse(state[j])
        new = W.free_reduce(state[i] + piece)
    else:
        raise ValueError(f"unknown stable move {move!r}")
    if not new or len(new) > cap:
        return state
    return state[:i] + (new,) + state[i + 1:]


def replay_stable(state, moves, cap: int):
    """Replay a stable-move list; returns the list of states after each move."""
    out = []
    cur = tuple(state)
    for move in moves:
        cur = apply_stable_move(cur, move, cap)
        out.append(cur)
    return out


def stable_move_children(state, cap: int):
    """Every distinct non-no-op child over the FULL move vocabulary (test anchor)."""
    state = tuple(state)
    n = len(state)
    children = set()
    for i in range(n):
        for j in range(n):
            if i != j:
                for sign in (1, -1):
                    child = apply_stable_move(state, ("mult", i, j, sign), cap)
                    if child != state:
                        children.add(child)
        for g in GENERATORS:
            for c in (g, g.upper()):
                child = apply_stable_move(state, ("conj", i, c), cap)
                if child != state:
                    children.add(child)
    return children


# --------------------------------------------------------------------------------------
# 1. the matched operator (one shared implementation for both roots)
# --------------------------------------------------------------------------------------


def concat_products_rank3(key, cap: int):
    """Every rank-3 AC concatenation over the rotation grid, deterministically.

    Yields ``((i, j, a, b, sign), exact)``: target relator ``i`` at rotation ``a``,
    source relator ``j`` at rotation ``b``, ``r_i <- free_reduce(a . b^sign)``; the
    exact child keeps the source at ``b`` and the third relator at its canonical
    rotation (the exact-state convention of ``ak2_battery._concat_products``, one
    level up).  Children that free-reduce to empty or exceed ``cap`` are dropped,
    mirroring the no-op rule of the move calculus.
    """
    key = tuple(key)
    n = len(key)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            for a in AB.rotations(key[i]):
                for b in AB.rotations(key[j]):
                    ib = W.inverse(b)
                    for sign in (+1, -1):
                        new = W.free_reduce(a + (b if sign > 0 else ib))
                        if not new or len(new) > cap:
                            continue
                        exact = key[:i] + (new,) + key[i + 1:]
                        exact = exact[:j] + (b,) + exact[j + 1:]
                        yield (i, j, a, b, sign), exact


def canon_children_rank3(key, cap: int):
    """Distinct canonical children of the canonical class ``key``; first exact wins.

    Deterministic: ``concat_products_rank3`` iterates the ordered-pair / rotation /
    sign grid in a fixed sorted order and the first exact realization producing a
    canonical form is kept as its provenance.  This single function IS the matched
    operator: both roots' harvests call it and nothing else.
    """
    out = {}
    for prov, exact in concat_products_rank3(key, cap):
        ck = canon_state(exact, ORDER3)
        if ck not in out:
            out[ck] = (exact, prov)
    return out


def harvest_root_prov(root_name: str, root, pops: int = HARVEST_POPS,
                      cap: int | None = None) -> dict:
    """Best-first canonical harvest of one root: EXACTLY ``pops`` pops (asserted).

    A line-for-line rank-3 mirror of ``ak2_battery.harvest_members`` /
    ``ak3_matched_control.harvest_members_prov``: priority is total canonical length
    with insertion-order ties, the seen-set is the canonical triple, children are
    iterated in sorted canonical order, and a truncated run with ``pops = P``
    discovers exactly the rows with ``first_seen_pop <= P`` in the same order (the
    determinism contract asserted by the tests).  Per member the record keeps
    ``parent_key`` (popped canonical class of first encounter; ``None`` for the
    root), ``realization`` ``(i, j, a, b, sign)`` and ``encounters``.
    """
    if cap is None:
        cap = cap_for_root(root)
    root = tuple(root)
    root_key = canon_state(root, ORDER3)
    found = {root_key: {"order": 0, "first_seen_pop": 0, "first_exact": root,
                        "encounters": 1, "parent_key": None, "realization": None}}
    heap = [(total_length3(root_key), 0, root_key)]
    tie = 1
    popped = 0
    children_generated = 0
    popped_keys = []
    while heap and popped < pops:
        _priority, _tie, key = heapq.heappop(heap)
        popped += 1
        popped_keys.append(key)
        for ck, (exact, prov) in sorted(canon_children_rank3(key, cap).items()):
            children_generated += 1
            record = found.get(ck)
            if record is not None:
                record["encounters"] += 1
                continue
            found[ck] = {"order": len(found), "first_seen_pop": popped,
                         "first_exact": exact, "encounters": 1,
                         "parent_key": key, "realization": prov}
            heapq.heappush(heap, (total_length3(ck), tie, ck))
            tie += 1
    if popped != pops:
        raise AssertionError(
            f"{root_name}: harvest queue exhausted after {popped} pops; the "
            f"{pops}-pop contract is broken"
        )
    return {
        "root_name": root_name,
        "root": root,
        "root_key": root_key,
        "pops": popped,
        "pop_budget": pops,
        "relator_cap": cap,
        "operator": OPERATOR_DESCRIPTOR,
        "children_generated": children_generated,
        "distinct_members": len(found),
        "queue_remaining": len(heap),
        "popped_keys": popped_keys,
        "members": found,
    }


# --------------------------------------------------------------------------------------
# 2. exact move composites + independent replay verification
# --------------------------------------------------------------------------------------


def conjugation_moves_to3(state, idx: int, target_word: str, cap: int):
    """AC3 conjugation moves carrying relator ``idx`` of ``state`` to ``target_word``.

    The rank-3 mirror of ``ak2_battery.conjugation_moves_to``: strip conjugate shells
    first (none arise from canonical parents, kept for safety), then rotate in the
    cheaper direction.  Conjugation never grows a cyclically reduced relator, so every
    intermediate stays within ``cap``.  Returns ``(moves, state_after)``.
    """
    moves = []
    cur = tuple(state)
    while not W.is_cyclically_reduced(cur[idx]):
        payload = W.inverse_letter(cur[idx][0])
        move = ("conj", idx, payload)
        nxt = apply_stable_move(cur, move, cap)
        if nxt == cur:
            raise ReplayVerificationError(f"reduction {move} was a no-op on {cur}")
        moves.append(move)
        cur = nxt
    w = cur[idx]
    if len(w) != len(target_word) or (w and target_word not in w + w):
        raise ReplayVerificationError(f"{target_word!r} is not a rotation of {w!r}")
    if w != target_word:
        n = len(w)
        k = (w + w).index(target_word)
        steps = k if k <= n - k else n - k
        left = k <= n - k
        for _ in range(steps):
            payload = (W.inverse_letter(cur[idx][0]) if left else cur[idx][-1])
            move = ("conj", idx, payload)
            nxt = apply_stable_move(cur, move, cap)
            if nxt == cur:
                raise ReplayVerificationError(f"rotation {move} was a no-op on {cur}")
            moves.append(move)
            cur = nxt
        if cur[idx] != target_word:
            raise ReplayVerificationError("rotation bookkeeping failed")
    return moves, cur


def step_composite3(parent_key, realization, cap: int):
    """The exact stable-move list realizing one expansion step, and its arrival.

    Starts from the parent's canonical triple AS AN EXACT STATE (cyclically reduced
    words are legal exact relators), rotates relator ``i`` to ``a`` and relator ``j``
    to ``b`` via AC3 conjugations, then applies the AC2 concatenation
    ``("mult", i, j, sign)``.  The caller verifies the arrival byte-exactly.
    """
    i, j, a, b, sign = realization
    state = tuple(parent_key)
    moves, state = conjugation_moves_to3(state, i, a, cap)
    more, state = conjugation_moves_to3(state, j, b, cap)
    concat = ("mult", i, j, sign)
    nxt = apply_stable_move(state, concat, cap)
    if nxt == state:
        raise ReplayVerificationError(f"concatenation {concat} was a no-op on {state}")
    return moves + more + [concat], nxt


def verify_step3(parent_exact, moves, expected_exact, expected_canonical=None,
                 cap: int = CAP_AK3Z) -> bool:
    """Byte-exact replay of ONE stored composite through ``replay_stable`` alone.

    Deliberately independent of :func:`step_composite3`: trusts nothing but the stored
    ``(parent_exact, moves, expected_exact)`` triple and the move calculus.  Raises
    :class:`ReplayVerificationError` on any mismatch.
    """
    parent_exact = tuple(parent_exact)
    states = replay_stable(parent_exact, [tuple(m) for m in moves], cap)
    arrival = tuple(states[-1]) if states else parent_exact
    if arrival != tuple(expected_exact):
        raise ReplayVerificationError(
            f"step replay mismatch: {arrival} != {tuple(expected_exact)} "
            f"(from {parent_exact} via {list(moves)})"
        )
    if expected_canonical is not None \
            and canon_state(arrival, ORDER3) != tuple(expected_canonical):
        raise ReplayVerificationError(
            f"canonicalization mismatch: canon{arrival} != "
            f"{tuple(expected_canonical)}"
        )
    return True


def attach_and_verify_composites(harvest: dict) -> dict:
    """Compute ``move_composite`` for EVERY non-root member and replay-verify each."""
    cap = harvest["relator_cap"]
    verified = 0
    for key, rec in harvest["members"].items():
        if rec["parent_key"] is None:
            rec["move_composite"] = None
            continue
        moves, _arrival = step_composite3(rec["parent_key"], rec["realization"], cap)
        verify_step3(rec["parent_key"], moves, rec["first_exact"],
                     expected_canonical=key, cap=cap)
        rec["move_composite"] = moves
        verified += 1
    return {"single_step_composites_verified": verified,
            "members_total": len(harvest["members"])}


def replay_chain3(key, index, root, cap: int) -> dict:
    """Full byte-exact replay of the chain root -> member from stored provenance.

    ``index`` maps canonical-triple tuples to rows carrying ``order`` and
    ``provenance`` (``parent_key`` / ``parent_exact`` / ``move_composite`` /
    ``first_exact``), exactly as written to the artifacts.  Walks parent links up to
    the root key, verifies every step with :func:`verify_step3`, checks
    ``parent_exact == parent_key``, parent-order monotonicity, and that the root
    row's exact realization is the root itself.
    """
    root = tuple(root)
    root_key = canon_state(root, ORDER3)
    k = tuple(key)
    steps = []
    guard = 0
    while k != root_key:
        row = index.get(k)
        if row is None:
            raise ReplayVerificationError(f"chain broken: {k} has no stored row")
        prov = row["provenance"]
        if prov["parent_key"] is None:
            raise ReplayVerificationError(f"non-root member {k} has no parent")
        parent_key = tuple(prov["parent_key"])
        if tuple(prov["parent_exact"]) != parent_key:
            raise ReplayVerificationError(
                f"parent_exact {prov['parent_exact']} is not the parent's canonical "
                f"triple {parent_key}"
            )
        parent_row = index.get(parent_key)
        if parent_row is None:
            raise ReplayVerificationError(f"chain broken: parent {parent_key} missing")
        if parent_row["order"] >= row["order"]:
            raise ReplayVerificationError(
                f"parent order {parent_row['order']} not before child {row['order']}"
            )
        verify_step3(prov["parent_exact"], prov["move_composite"],
                     prov["first_exact"], expected_canonical=k, cap=cap)
        steps.append(len(prov["move_composite"]))
        k = parent_key
        guard += 1
        if guard > 100_000:
            raise ReplayVerificationError("chain longer than 100,000 steps (cycle?)")
    root_row = index.get(root_key)
    if root_row is None:
        raise ReplayVerificationError("root row missing from the index")
    if tuple(root_row["provenance"]["first_exact"]) != root:
        raise ReplayVerificationError(
            f"root row's exact realization {root_row['provenance']['first_exact']} "
            f"is not the root {root}"
        )
    steps.reverse()
    return {"verified": True, "chain_steps": len(steps),
            "h_moves_total": sum(steps), "h_moves_per_step": steps}


# --------------------------------------------------------------------------------------
# 3. the operator-identity check between the two roots
# --------------------------------------------------------------------------------------


def verify_recorded_edges(members: dict, key, cap: int) -> int:
    """Re-derive ``canon_children_rank3(key, cap)`` and check every recorded edge.

    For every recomputed child whose stored first encounter names ``key`` as parent,
    the stored ``first_exact`` and ``realization`` must equal the recomputation
    byte-for-byte.  Returns the number of edges verified (0 is legal for a
    late-popped key all of whose children were first encountered elsewhere); raises
    :class:`OperatorMismatchError` on any disagreement.
    """
    key = tuple(key)
    recomputed = canon_children_rank3(key, cap)
    verified = 0
    for ck, (exact, prov) in recomputed.items():
        rec = members.get(ck)
        if rec is None or rec["parent_key"] is None \
                or tuple(rec["parent_key"]) != key:
            continue                    # first encountered elsewhere (or never stored)
        if tuple(rec["first_exact"]) != exact \
                or tuple(rec["realization"]) != tuple(prov):
            raise OperatorMismatchError(
                f"recorded edge {key} -> {ck} disagrees with the operator: stored "
                f"({rec['first_exact']}, {rec['realization']}) != recomputed "
                f"({exact}, {prov})"
            )
        verified += 1
    return verified


def operator_identity_report(harvests, sample_size: int = OPERATOR_SAMPLE_SIZE,
                             seed: int = REPLAY_SEED) -> dict:
    """Assert both roots' harvests consulted the IDENTICAL expansion operator.

    Checks, per root: (1) the recorded operator descriptor is the shared constant and
    the pop budget is exactly 1,000; (2) the cap follows the classical relative-
    headroom rule (total root length + 4); (3) the full first pop re-derives -- the
    recomputed children of the root key are exactly the stored ``first_seen_pop == 1``
    rows; (4) a seeded sample of popped keys re-derives edge-by-edge through
    :func:`verify_recorded_edges` (the SAME single function serves both roots -- there
    is no per-root operator code path anywhere in this module).
    """
    report = {"identical": True, "roots": {}}
    for harvest in harvests:
        name = harvest["root_name"]
        members = harvest["members"]
        cap = harvest["relator_cap"]
        if harvest["operator"] != OPERATOR_DESCRIPTOR:
            raise OperatorMismatchError(f"{name}: operator descriptor differs")
        if harvest["pop_budget"] != HARVEST_POPS or harvest["pops"] != HARVEST_POPS:
            raise OperatorMismatchError(
                f"{name}: pops {harvest['pops']}/{harvest['pop_budget']} != "
                f"{HARVEST_POPS}"
            )
        if cap != cap_for_root(harvest["root"]):
            raise OperatorMismatchError(
                f"{name}: cap {cap} breaks the root-total+{CAP_RULE_SLACK} rule"
            )
        root_key = harvest["root_key"]
        if root_key != canon_state(harvest["root"], ORDER3):
            raise OperatorMismatchError(f"{name}: root_key is not canon of the root")
        root_rec = members[root_key]
        if tuple(root_rec["first_exact"]) != tuple(harvest["root"]) \
                or root_rec["order"] != 0 or root_rec["parent_key"] is not None:
            raise OperatorMismatchError(f"{name}: root row is malformed")
        recomputed_first = set(canon_children_rank3(root_key, cap)) - {root_key}
        stored_first = {k for k, rec in members.items()
                        if rec["first_seen_pop"] == 1}
        if recomputed_first != stored_first:
            raise OperatorMismatchError(
                f"{name}: first pop differs from the operator "
                f"(symmetric difference {len(recomputed_first ^ stored_first)})"
            )
        rng = random.Random(seed)
        sample = rng.sample(harvest["popped_keys"],
                            min(sample_size, len(harvest["popped_keys"])))
        edges = 0
        for key in sample:
            edges += verify_recorded_edges(members, key, cap)
        if edges == 0:
            raise OperatorMismatchError(
                f"{name}: the sampled-edge check verified nothing; vacuous sample"
            )
        report["roots"][name] = {
            "relator_cap": cap,
            "cap_rule": f"total root length + {CAP_RULE_SLACK}",
            "first_pop_children_verified": len(recomputed_first),
            "sampled_popped_keys": len(sample),
            "sampled_edges_verified": edges,
        }
    report["shared_operator"] = OPERATOR_DESCRIPTOR
    report["note"] = ("both harvests call the single implementation "
                      "canon_children_rank3/harvest_root_prov; the only per-root "
                      "inputs are the root state and its rule-derived cap")
    return report


# --------------------------------------------------------------------------------------
# 4. decisions (audited stack, budgets pinned verbatim)
# --------------------------------------------------------------------------------------


def _split_slice(srow: dict) -> dict:
    """The JSON slice of a ``decide_split_state`` row kept in a member row."""
    return {k: v for k, v in srow.items() if k not in ("state", "structural")}


def decide_member(key, scheme_budget: int = SCHEME_BUDGET,
                  branch_budget: int = BRANCH_BUDGET,
                  census_cap: int = FALLBACK_CAP) -> dict:
    """Decide one canonical triple through the audited stack; returns a result dict.

    Route (see the module docstring): clean R1e shape -> ``decide_split_state``
    (Theorem D + Lemma S through the rank-2 pair); otherwise ``decide_state``
    (R1c-v2); fail-closed -> L-general census under Theorem D when every generator
    occurs and the family fits the cap; else honest UNSUPPORTED / UNDECIDED_BUDGET.
    """
    key = tuple(key)
    report = structural_report(key, GENERATORS)
    out = {
        "structural": {
            "link_components": report.link_components,
            "straddling": list(report.straddling),
            "z_occurrences": report.z_occurrences,
            "clean": report.clean,
        },
        "destabilizable": report.clean,
        "pair": None,
        "split": None,
        "support_kind": None,
        "counters": None,
        "census": None,
        "verdict_obj": None,
    }
    if report.clean:
        srow = decide_split_state(key, census_cap=census_cap, cross_check=False)
        out.update(
            verdict=srow["verdict"],
            method="split/" + srow["method"],
            reason=srow.get("reason"),
            pair=srow["pair"],
            split=_split_slice(srow),
            support_kind=(srow.get("support") or {}).get("kind"),
            counters=srow.get("counters"),
            census=srow.get("census"),
        )
        return out
    verdict, support = decide_state(key, generators=GENERATORS,
                                    scheme_budget=scheme_budget,
                                    branch_budget=branch_budget)
    out["support_kind"] = support.kind
    if verdict.verdict in (CS.SPHERICAL, CS.NOT_SPHERICAL):
        out.update(verdict=verdict.verdict, method=verdict.method,
                   reason=verdict.reason, verdict_obj=verdict,
                   counters=AB._compact_counters(verdict))
        return out
    gate_reason = verdict.reason
    missing = 2 * len(GENERATORS) - len(report.present)
    if missing:
        out.update(
            verdict=CS.UNSUPPORTED, method="structural_gate",
            reason=(f"R1c-v2 fail-closed ({gate_reason}); {missing} germ(s) absent -- "
                    "Theorem D requires every generator to occur, and a census over "
                    "the occurring generators would decide the wrong complex"),
        )
        return out
    fallback = census_verdict(key, GENERATORS, cap=census_cap)
    reason = f"R1c-v2 fail-closed ({gate_reason})"
    out.update(
        verdict=fallback.verdict,
        method=("factorial_census" if fallback.verdict in (CS.SPHERICAL,
                                                           CS.NOT_SPHERICAL)
                else "none"),
        reason=(f"{reason}; decided by the L-general census under Theorem D"
                if fallback.reason is None else f"{reason}; {fallback.reason}"),
        verdict_obj=fallback,
        census=AB.census_summary(fallback.census) if fallback.census else None,
    )
    return out


# --------------------------------------------------------------------------------------
# 5. the hit protocol (mandatory for any SPHERICAL, either root)
# --------------------------------------------------------------------------------------


def _witness_rotation(verdict) -> dict | None:
    if verdict is None:
        return None
    if verdict.decision is not None and verdict.decision.witness is not None:
        return verdict.decision.witness.rotation_map()
    if verdict.census is not None and verdict.census.get("accepting_orders"):
        return verdict.census["accepting_orders"][0]
    return None


def hit_protocol_rank3(key, decided: dict, index, root, cap: int,
                       do_cross_check: bool, tc_cap: int = TC_HIT_CAP) -> dict:
    """The full protocol for one SPHERICAL member (triple level).

    * full move-chain replay from the root (byte-exact, independent replayer);
    * re-decision through the same stack, agreement asserted into the record;
    * Todd-Coxeter triviality certificate on the TRIPLE over ``(x, y, z)``;
    * L-general witness check: for clean rows the pair-level protocol is already in
      ``decided['split']`` (pair witness + pair TC), and the joint Corollary-Z
      cross-check runs here when ``do_cross_check`` and affordable; for non-clean
      rows the triple rotation witness is checked directly, with the transitivity
      audit exactly when ``L == 1`` and the group is TC-certified trivial.
    """
    key = tuple(key)
    protocol = {"hit": True}
    chain = replay_chain3(key, index, root, cap)
    protocol["chain_replay"] = {k: chain[k] for k in
                                ("verified", "chain_steps", "h_moves_total")}
    re_decided = decide_member(key)
    protocol["re_decision"] = {
        "verdict": re_decided["verdict"],
        "method": re_decided["method"],
        "agrees": (re_decided["verdict"] == decided["verdict"]
                   and re_decided["method"] == decided["method"]),
    }
    tc = CE.is_trivial_group(key, generators=GENERATORS, cap=tc_cap)
    protocol["todd_coxeter_triple"] = {
        "status": tc["status"], "index": tc["index"], "trivial": tc["trivial"],
        "cosets_defined": tc["cosets_defined"], "cap": tc["cap"],
    }
    if decided["destabilizable"]:
        protocol["witness_route"] = "pair (Theorem D + Lemma S; see split row)"
        if do_cross_check and decided["pair"] is not None:
            try:
                check = joint_cross_check(key, tuple(decided["pair"]),
                                          cap=FALLBACK_CAP)
                check.pop("defect_histogram", None)
                check.pop("joint_accepting_rotation", None)
                protocol["corollary_z_cross_check"] = check
            except Exception as exc:              # noqa: BLE001 -- audit surface
                protocol["corollary_z_cross_check_error"] = \
                    f"{type(exc).__name__}: {exc}"
    else:
        rotation = _witness_rotation(decided.get("verdict_obj"))
        if rotation is None:
            protocol["witness_error"] = "no rotation system available to verify"
        else:
            try:
                check = check_witness_l_general(key, rotation,
                                                generators=GENERATORS,
                                                trivial_group=False)
                check["words"] = list(check["words"])
                check["generators"] = list(check["generators"])
                check["germs"] = list(check["germs"])
                protocol["triple_witness_check"] = check
                if tc["trivial"] is True and check["link_components"] == 1:
                    audit = check_witness_l_general(key, rotation,
                                                    generators=GENERATORS,
                                                    trivial_group=True)
                    protocol["transitivity_audit"] = {
                        "ac_bc_orbits": audit["ac_bc_orbits"],
                        "ac_bc_transitive": audit["ac_bc_transitive"],
                    }
            except Exception as exc:              # noqa: BLE001 -- audit surface
                protocol["witness_error"] = f"{type(exc).__name__}: {exc}"
    protocol["protocol_clean"] = (
        chain["verified"] and protocol["re_decision"]["agrees"]
        and "witness_error" not in protocol
        and "corollary_z_cross_check_error" not in protocol
        and tc["trivial"] is not False
    )
    return protocol


# --------------------------------------------------------------------------------------
# 6. per-root runner (streaming decisions -> gzip JSONL)
# --------------------------------------------------------------------------------------


def _open_out(path: str):
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    if path.endswith(".gz"):
        return gzip.open(path, "wt", encoding="utf-8")
    return open(path, "w", encoding="utf-8")


def _prov_index(harvest: dict) -> dict:
    """The replay index (order + provenance per member), straight from the harvest."""
    index = {}
    for key, rec in harvest["members"].items():
        index[key] = {
            "order": rec["order"],
            "provenance": {
                "parent_key": rec["parent_key"],
                "parent_exact": rec["parent_key"],
                "move_composite": rec["move_composite"],
                "first_exact": rec["first_exact"],
            },
        }
    return index


def run_root(root_name: str, root, cap: int, members_out: str,
             pops: int = HARVEST_POPS, progress_every: int = 10_000,
             keep_all_hits: bool = False) -> dict:
    """Harvest, verify, decide and stream one root's member file; returns the stats.

    ``keep_all_hits`` keeps every SPHERICAL row in memory in full (the AK3+z
    headline setting); otherwise full rows are kept for the first
    :data:`AK2Z_HIT_BRIEFS` hits and the rest contribute briefs/counters only --
    every hit's full protocol is in the members file either way.
    """
    t0 = time.time()
    print(f"[{root_name}] harvesting ({pops} pops, cap {cap}) ...", flush=True)
    harvest = harvest_root_prov(root_name, root, pops, cap)
    print(f"[{root_name}]   {harvest['distinct_members']} distinct members "
          f"({harvest['children_generated']} children generated)", flush=True)

    print(f"[{root_name}] verifying every single-step move composite ...", flush=True)
    step_report = attach_and_verify_composites(harvest)
    print(f"[{root_name}]   {step_report['single_step_composites_verified']} "
          "composites verified byte-exactly", flush=True)

    index = _prov_index(harvest)
    rng = random.Random(REPLAY_SEED)
    non_root = [k for k, rec in harvest["members"].items() if rec["order"] > 0]
    non_root.sort(key=lambda k: harvest["members"][k]["order"])
    sample_keys = rng.sample(non_root, min(REPLAY_SAMPLE_SIZE, len(non_root)))
    sample_chains = []
    for key in sample_keys:
        chain = replay_chain3(key, index, root, cap)
        sample_chains.append({"canonical": list(key),
                              "chain_steps": chain["chain_steps"],
                              "h_moves_total": chain["h_moves_total"]})
    print(f"[{root_name}]   {len(sample_chains)} sampled chains replay-verified",
          flush=True)

    print(f"[{root_name}] deciding every member (audited stack, pinned budgets) ...",
          flush=True)
    ordered = sorted(harvest["members"].items(), key=lambda kv: kv[1]["order"])
    verdict_method_hist: Counter = Counter()
    verdict_hist: Counter = Counter()
    z_hist: Counter = Counter()
    length_hist: Counter = Counter()
    spherical_by_length: Counter = Counter()
    spherical_rows = 0
    destab_rows = 0
    destab_spherical = 0
    undecided_rows = 0
    unsupported_rows = 0
    sigma_e = Fraction(0)
    e_known = 0
    e_unknown = 0
    support_class_hist: Counter = Counter()
    hits_full = []
    hit_briefs = []
    protocol_failures = 0
    cross_checked = 0
    spherical_chains_verified = 0

    with _open_out(members_out) as fh:
        for count, (key, rec) in enumerate(ordered, 1):
            decided = decide_member(key)
            struct = decided["structural"]
            row = {
                "record": "stable_member",
                "root": root_name,
                "canonical": list(key),
                "relator_lengths": [len(w) for w in key],
                "total_length": total_length3(key),
                "order": rec["order"],
                "first_seen_pop": rec["first_seen_pop"],
                "z_occurrences": struct["z_occurrences"],
                "link_components": struct["link_components"],
                "straddling": struct["straddling"],
                "destabilizable": decided["destabilizable"],
                "pair": decided["pair"],
                "verdict": decided["verdict"],
                "method": decided["method"],
                "reason": decided["reason"],
                "support_kind": decided["support_kind"],
                "counters": decided["counters"],
                "census": decided["census"],
                "split": decided["split"],
                "provenance": {
                    "parent_key": (list(rec["parent_key"])
                                   if rec["parent_key"] is not None else None),
                    "parent_exact": (list(rec["parent_key"])
                                     if rec["parent_key"] is not None else None),
                    "realization": (list(rec["realization"])
                                    if rec["realization"] is not None else None),
                    "move_composite": ([list(m) for m in rec["move_composite"]]
                                       if rec["move_composite"] is not None else None),
                    "first_exact": list(rec["first_exact"]),
                    "encounters": rec["encounters"],
                },
            }
            if decided["destabilizable"]:
                destab_rows += 1
                cls, e = support_class_and_E(tuple(decided["pair"]))
                support_class_hist[cls] += 1
                row["pair_support_class"] = cls
                row["pair_E"] = float(e) if e is not None else None
                row["pair_E_exact"] = (f"{e.numerator}/{e.denominator}"
                                       if e is not None else None)
                if e is not None:
                    sigma_e += e
                    e_known += 1
                else:
                    e_unknown += 1
            verdict_method_hist[f"{decided['verdict']}/{decided['method']}"] += 1
            verdict_hist[decided["verdict"]] += 1
            z_hist[struct["z_occurrences"]] += 1
            length_hist[row["total_length"]] += 1
            if decided["verdict"] == UNDECIDED_BUDGET:
                undecided_rows += 1
            if decided["verdict"] == CS.UNSUPPORTED:
                unsupported_rows += 1

            if decided["verdict"] == CS.SPHERICAL:
                spherical_rows += 1
                spherical_by_length[row["total_length"]] += 1
                if decided["destabilizable"]:
                    destab_spherical += 1
                do_cc = keep_all_hits or (decided["destabilizable"]
                                          and cross_checked < CROSS_CHECK_SAMPLE)
                protocol = hit_protocol_rank3(key, decided, index, root, cap,
                                              do_cross_check=do_cc)
                if "corollary_z_cross_check" in protocol:
                    cross_checked += 1
                if protocol["chain_replay"]["verified"]:
                    spherical_chains_verified += 1
                if not protocol["protocol_clean"]:
                    protocol_failures += 1
                row["chain_replay"] = protocol["chain_replay"]
                row["re_decision"] = protocol["re_decision"]
                row["hit_protocol"] = {k: v for k, v in protocol.items()
                                       if k not in ("chain_replay", "re_decision")}
                brief = {
                    "canonical": row["canonical"],
                    "total_length": row["total_length"],
                    "relator_lengths": row["relator_lengths"],
                    "order": row["order"],
                    "first_seen_pop": row["first_seen_pop"],
                    "z_occurrences": row["z_occurrences"],
                    "destabilizable": row["destabilizable"],
                    "pair": row["pair"],
                    "verdict": row["verdict"],
                    "method": row["method"],
                    "tc_triple": protocol["todd_coxeter_triple"],
                    "chain_steps": protocol["chain_replay"]["chain_steps"],
                    "re_decision_agrees": protocol["re_decision"]["agrees"],
                    "protocol_clean": protocol["protocol_clean"],
                }
                if keep_all_hits or len(hits_full) < AK2Z_HIT_BRIEFS:
                    full = dict(row)
                    hits_full.append(full)
                hit_briefs.append(brief)
            fh.write(json.dumps(row) + "\n")
            if progress_every and count % progress_every == 0:
                print(f"[{root_name}]   decided {count}/{len(ordered)} "
                      f"({time.time() - t0:.0f}s; spherical so far "
                      f"{spherical_rows})", flush=True)

    stats = {
        "root": list(root),
        "root_key": list(harvest["root_key"]),
        "relator_cap": cap,
        "harvest": {k: harvest[k] for k in
                    ("pops", "pop_budget", "relator_cap", "children_generated",
                     "distinct_members", "queue_remaining")},
        "verdict_method_histogram": dict(sorted(verdict_method_hist.items())),
        "verdict_histogram": dict(sorted(verdict_hist.items())),
        "spherical_rows": spherical_rows,
        "spherical_rate": (spherical_rows / len(ordered)) if ordered else None,
        "spherical_by_total_length": {str(k): v for k, v in
                                      sorted(spherical_by_length.items())},
        "destabilizable_rows": destab_rows,
        "destabilizable_spherical_rows": destab_spherical,
        "z_occurrence_histogram": {str(k): v for k, v in sorted(z_hist.items())},
        "member_total_length_histogram": {str(k): v for k, v in
                                          sorted(length_hist.items())},
        "undecided_budget_rows": undecided_rows,
        "unsupported_rows": unsupported_rows,
        "shadow_sigma_E": {
            "scope": "destabilizable members' rank-2 projections only (E is "
                     "rank-2-only; validated K4/K4-e/C4 closed forms)",
            "rows_with_E": e_known,
            "rows_E_unknown": e_unknown,
            "float": float(sigma_e),
            "exact": f"{sigma_e.numerator}/{sigma_e.denominator}",
            "pair_support_class_histogram": dict(sorted(
                support_class_hist.items())),
        },
        "replay_verification": {
            "single_steps": step_report,
            "chain_sample": {
                "seed": REPLAY_SEED,
                "requested": REPLAY_SAMPLE_SIZE,
                "verified": len(sample_chains),
                "max_chain_steps": max((c["chain_steps"] for c in sample_chains),
                                       default=0),
                "max_h_moves_total": max((c["h_moves_total"] for c in sample_chains),
                                         default=0),
                "chains": sample_chains,
            },
            "spherical_chains_verified": spherical_chains_verified,
        },
        "hit_protocol": {
            "spherical_rows": spherical_rows,
            "protocol_failures": protocol_failures,
            "corollary_z_cross_checks_ran": cross_checked,
            "re_decisions_all_agree": all(b["re_decision_agrees"]
                                          for b in hit_briefs),
        },
        "elapsed_seconds": round(time.time() - t0, 1),
        "members_out": members_out,
    }
    return {"stats": stats, "harvest": harvest, "hits_full": hits_full,
            "hit_briefs": hit_briefs}


# --------------------------------------------------------------------------------------
# 7. the contrast runner
# --------------------------------------------------------------------------------------


def classical_contrast_requote(ak2_summary_path: str = CLASSICAL_AK2_SUMMARY,
                               ak3_summary_path: str = CLASSICAL_AK3_SUMMARY) -> dict:
    """The classical (rank-2) contrast numbers, re-quoted from committed artifacts."""
    with open(ak2_summary_path, encoding="utf-8") as fh:
        ak2 = json.load(fh)
    with open(ak3_summary_path, encoding="utf-8") as fh:
        ak3 = json.load(fh)
    return {
        "quoted_from": [ak2_summary_path, ak3_summary_path],
        "ak2_classical": {
            "root": ak2["root"],
            "distinct_members": ak2["harvest"]["distinct_members"],
            "spherical_rows": ak2["spherical_rows"],
            "relator_cap": ak2["budgets"]["relator_cap"],
            "harvest_pops": ak2["budgets"]["harvest_pops"],
        },
        "ak3_classical": {
            "root": ak3["root"],
            "distinct_members": ak3["harvest"]["distinct_members"],
            "spherical_rows": ak3["spherical_rows"],
            "relator_cap": ak3["budgets"]["relator_cap"],
            "harvest_pops": ak3["budgets"]["harvest_pops"],
        },
    }


def _comparison_row(name: str, stats: dict) -> dict:
    return {
        "root": stats["root"],
        "relator_cap": stats["relator_cap"],
        "harvest_pops": stats["harvest"]["pops"],
        "distinct_members": stats["harvest"]["distinct_members"],
        "verdict_histogram": stats["verdict_histogram"],
        "spherical_rows": stats["spherical_rows"],
        "spherical_rate": stats["spherical_rate"],
        "destabilizable_rows": stats["destabilizable_rows"],
        "destabilizable_spherical_rows": stats["destabilizable_spherical_rows"],
        "undecided_budget_rows": stats["undecided_budget_rows"],
        "unsupported_rows": stats["unsupported_rows"],
        "shadow_sigma_E": {k: stats["shadow_sigma_E"][k]
                           for k in ("rows_with_E", "rows_E_unknown", "float",
                                     "exact")},
    }


def run_contrast(ak3z_members_out: str = DEFAULT_AK3Z_MEMBERS,
                 ak2z_members_out: str = DEFAULT_AK2Z_MEMBERS,
                 summary_out: str = DEFAULT_SUMMARY,
                 pops: int = HARVEST_POPS) -> dict:
    if pops != HARVEST_POPS:
        raise AssertionError(
            f"the contrast's budget is EXACTLY {HARVEST_POPS} pops per root (hard "
            f"session rule); got {pops}.  Small harvests are available via "
            "harvest_root_prov for tests, but no artifact is written off-budget."
        )
    t0 = time.time()
    outputs = {"AK3+z": ak3z_members_out, "AK2+z": ak2z_members_out}
    results = {}
    for name, root, cap in ROOTS:
        results[name] = run_root(name, root, cap, outputs[name], pops=pops,
                                 keep_all_hits=(name == "AK3+z"))

    print("[contrast] operator-identity check between the two roots ...", flush=True)
    identity = operator_identity_report([results[name]["harvest"]
                                         for name, _root, _cap in ROOTS])

    ak3z_keys = set(results["AK3+z"]["harvest"]["members"])
    ak2z_keys = set(results["AK2+z"]["harvest"]["members"])
    overlap = sorted(ak3z_keys & ak2z_keys)
    overlap_block = {
        "count": len(overlap),
        "keys_sample": [list(k) for k in overlap[:10]],
        "note": ("a nonzero overlap would place a common canonical member in BOTH "
                 "classes, i.e. AK3+z's class would equal AK2+z's provably "
                 "trivializable class -- headline-grade; recorded as data only"),
    }
    if overlap:
        overlap_block["LOUD_OVERLAP_ALERT"] = True

    ak3z_stats = results["AK3+z"]["stats"]
    ak2z_stats = results["AK2+z"]["stats"]
    ak3z_hits = results["AK3+z"]["hits_full"]
    ak2z_briefs = results["AK2+z"]["hit_briefs"]

    summary = {
        "record": "stable_matched_contrast_summary",
        "purpose": (
            "STABLE-CLASS MATCHED CONTRAST: the rank-3 analogue of the classical "
            "matched contrast (R3PRIME_DIGON_EXCESS.md 'CONTRAST RESULT').  One "
            "operator, two stabilized roots: AK2+z (class provably trivializable -- "
            "positive control) vs AK3+z (AK(3)'s stable class -- open target).  "
            "DATA ONLY -- no mathematical claim."
        ),
        "design": {
            "operator": {
                "descriptor": OPERATOR_DESCRIPTOR,
                "seen_set": "canon_state: relator permutations x rotations x "
                            "inversions on cyclically reduced relators",
                "z_policy": ("z is a live generator: moves may entangle it (that is "
                             "the stable-move space); NO z-inertness bias of any "
                             "kind -- z_occurrences recorded per member instead"),
                "identity_check": identity,
            },
            "length_caps": {
                "rule": f"per-relator cap = total root length + {CAP_RULE_SLACK} "
                        "(the classical contrast's relative-headroom rule)",
                "AK3+z": {"root_total": total_length3(AK3Z), "cap": CAP_AK3Z},
                "AK2+z": {"root_total": total_length3(AK2Z), "cap": CAP_AK2Z},
                "relative_headroom_reasoning": (
                    "both runs give the operator the same additive slack above "
                    "their root's scale, keeping the per-pop expansion geometry "
                    "comparable; the matched quantities are the operator and the "
                    "1,000-pop-per-root budget -- exactly the classical design "
                    "(AK(2) 15 = 11 + 4, AK(3) 17 = 13 + 4; here 16 = 12 + 4, "
                    "18 = 14 + 4)"),
                "absolute_cap_argument": (
                    "an absolute match (16 for both) would leave AK3+z only 2 "
                    "letters of headroom above its 14-letter root versus AK2+z's 4, "
                    "mechanically suppressing child generation and biasing the "
                    "open-target run toward zero hits; cap 18 makes the AK3+z box "
                    "strictly larger -- the conservative direction: a zero-hit "
                    "outcome cannot be attributed to a smaller search space"),
            },
            "decision_stack": (
                "clean R1e shape (z-inert: one relator z^{+-1}, z once, 2 "
                "components, no straddle) -> disconnected_split.decide_split_state "
                "(Theorem D + Lemma S, audited route, through the rank-2 pair); "
                "otherwise rank3_round2.decide_state over (x, y, z) (R1c-v2); "
                "fail-closed -> L-general factorial census with the general defect "
                "|A| - |C| + 2L - |AC| (minimum_defect == 0 decisive SPHERICAL at "
                "any L per Theorem D) within the 2,000,000 cap; absent-generator "
                "states fail-closed UNSUPPORTED; budget exhaustion "
                "UNDECIDED_BUDGET, never folded into NO"),
            "provenance_semantics": (
                "each non-root row stores parent_key (== parent_exact: a canonical "
                "triple of cyclically reduced words is itself an exact state), the "
                "realization (i, j, a, b, sign), and move_composite -- AC3 "
                "conjugations rotating relator i to a and relator j to b, then the "
                "AC2 concatenation -- whose replay from parent_exact arrives "
                "byte-identically at first_exact with canon_state(first_exact) == "
                "canonical.  The exact -> canonical step is the Lemma P AC "
                "composite (rotation = AC3, inversion = AC1, swap = the 6-move "
                "composite).  So every AK3+z row is a member of AK(3)'s STABLE "
                "class, every AK2+z row of AK2+z's provably trivializable class."),
            "hit_protocol": (
                "for every SPHERICAL row (either root): full move-chain replay from "
                "the root, re-decision agreement, Todd-Coxeter certificate on the "
                f"triple (cap {TC_HIT_CAP}), L-general witness check (pair-level "
                "protocol inside the split row for clean rows; triple rotation "
                "witness otherwise, transitivity audit when L == 1 and TC-trivial); "
                "joint Corollary-Z cross-check for every AK3+z hit and a "
                f"{CROSS_CHECK_SAMPLE}-row sample of AK2+z clean hits, when the "
                "joint family fits the census cap"),
        },
        "budgets": {
            "harvest_pops_per_root": HARVEST_POPS,
            "relator_caps": {"AK3+z": CAP_AK3Z, "AK2+z": CAP_AK2Z},
            "scheme_budget": SCHEME_BUDGET,
            "branch_budget": BRANCH_BUDGET,
            "census_cap": FALLBACK_CAP,
            "tc_hit_cap": TC_HIT_CAP,
            "pinned_from": "rank3_round2 (round-2 values, imported verbatim; "
                           "identical to the audited R1e/battery runs)",
        },
        "roots": {name: results[name]["stats"] for name, _root, _cap in ROOTS},
        "AK3Z_LOUD_SPHERICAL_ALERT": bool(ak3z_hits),
        "SPHERICAL_HITS_AK3Z": ak3z_hits,
        "SPHERICAL_HITS_AK3Z_NOTE": (
            LOUD_ALERT_AK3Z if ak3z_hits else
            "zero SPHERICAL members in the AK3+z harvest at matched exploration; "
            "see the comparison table -- data only, no claim"),
        "SPHERICAL_HITS_AK2Z": {
            "count": ak2z_stats["spherical_rows"],
            "note": ("EXPECTED: AK2+z's class is provably trivializable; these hits "
                     "are the positive control validating the pipeline end-to-end"),
            "by_total_length": ak2z_stats["spherical_by_total_length"],
            "clean_spherical_rows": ak2z_stats["destabilizable_spherical_rows"],
            "protocol_failures": ak2z_stats["hit_protocol"]["protocol_failures"],
            "first_briefs": ak2z_briefs[:AK2Z_HIT_BRIEFS],
        },
        "cross_root_overlap": overlap_block,
        "classical_contrast_requote": classical_contrast_requote(),
        "comparison_table": {
            "matched": ["operator (single shared implementation)",
                        "seen-set (canon_state)",
                        "priority (total canonical length, insertion ties)",
                        "pop budget (exactly 1,000 per root)",
                        "relative length-cap headroom (root total + 4)",
                        "decision stack + budgets (audited round-2 values)"],
            "not_matched": ["absolute per-relator cap (18 vs 16; AK3+z's box is "
                            "strictly larger -- see design.length_caps)"],
            "stable_AK3z": _comparison_row("AK3+z", ak3z_stats),
            "stable_AK2z": _comparison_row("AK2+z", ak2z_stats),
            "classical": classical_contrast_requote(),
        },
        "elapsed_seconds": round(time.time() - t0, 1),
        "outputs": {"ak3z_members": ak3z_members_out,
                    "ak2z_members": ak2z_members_out,
                    "summary": summary_out},
    }
    directory = os.path.dirname(summary_out)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(summary_out, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1)
        fh.write("\n")

    print(f"[contrast] done in {summary['elapsed_seconds']}s", flush=True)
    for name in ("AK3+z", "AK2+z"):
        s = results[name]["stats"]
        print(f"[contrast] {name}: members {s['harvest']['distinct_members']}, "
              f"verdicts {s['verdict_histogram']}, spherical {s['spherical_rows']}, "
              f"destabilizable {s['destabilizable_rows']}", flush=True)
    if ak3z_hits:
        print("!" * 78, flush=True)
        print(LOUD_ALERT_AK3Z, flush=True)
        for hit in ak3z_hits:
            print(f"  {tuple(hit['canonical'])} (len {hit['total_length']}, "
                  f"method {hit['method']})", flush=True)
        print("!" * 78, flush=True)
    if overlap:
        print("!" * 78, flush=True)
        print(f"CROSS-ROOT OVERLAP: {len(overlap)} shared canonical member(s) -- "
              "see cross_root_overlap in the summary (data only)", flush=True)
        print("!" * 78, flush=True)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ak3z-members-out", default=DEFAULT_AK3Z_MEMBERS)
    parser.add_argument("--ak2z-members-out", default=DEFAULT_AK2Z_MEMBERS)
    parser.add_argument("--summary-out", default=DEFAULT_SUMMARY)
    args = parser.parse_args(argv)
    run_contrast(args.ak3z_members_out, args.ak2z_members_out, args.summary_out)


if __name__ == "__main__":
    main()
