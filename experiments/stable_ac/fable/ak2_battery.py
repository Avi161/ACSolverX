"""Battery (b) of the R3' falsification program: the AK(2) control artifacts.

This is the implementation of item 4 ("BATTERY (b) REBUILT AS PRE-CONDITION") of the
revised R3' arc plan in ``results/stable_ac/theory/fable/R3PRIME_DIGON_EXCESS.md``.  It
regenerates, as committed artifacts, the two things every future candidate functional
must be evaluated against BEFORE any proof attempt:

1. **The AK(2) member set** (``results/stable_ac/fable/ak2_members.jsonl``).  A
   best-first harvest of exactly :data:`HARVEST_POPS` pops from
   AK(2) = ``("xxYYY", "xyxYXY")`` -- a provably AC-trivializable class -- at per-relator
   length cap :data:`CAP`, with the seen-set keyed on cyclically-REDUCED canonical forms
   (``ac_words.canon_pair``) per the lesson
   ``experiments/lessons/harvest-dedup-on-reduced-forms.md``, exact realizations kept
   only as provenance.  Because a canonical seen-set makes every plain conjugation child
   a duplicate (R1_COLAB_RUNNER_SPEC.md, round-1 fact 2), the expansion operator adds
   the explicit relator-rotation freedom: a popped canonical class is expanded through
   every concatenation h-move applied to every pair of cyclic rotations of its two
   (cyclically reduced) relators.  Each such child is reachable from the parent class by
   an exact h-move composite -- single-letter conjugations (h5-h12) realize any rotation
   of a cyclic word, one concatenation move (h1-h4) forms the product, and the final
   canonicalization is an AC composite by Lemma P of R1E_DISCONNECTED_LINK.md (rotation
   = AC3, relator inversion = AC1, relator swap = the explicit 6-move composite).  So
   every row is a genuine member of AK(2)'s classical AC class.

   Every distinct member is decided through ``disconnected_split.decide_pair`` -- the
   round-2 decision stack with budgets pinned VERBATIM (scheme 200,000 / branch
   2,000,000 / census cap 2,000,000): R1c-v2 cut-scheme solver first
   (``rank3_round2.decide_state`` with generators ``("x", "y")``), exact factorial
   census ``gamma_N_factorial_n`` second where the family fits the 2,000,000 cap,
   ``UNDECIDED_BUDGET`` otherwise -- never a verdict beyond the cap.  Disconnected-link
   members (the standard pair ``("x", "y")`` has link components {x+,x-} and {y+,y-})
   are decided by the census under **Theorem D** of R1E_DISCONNECTED_LINK.md: with the
   general defect ``|A| - |C| + 2L - |AC|`` (the 2L term is what
   ``gamma_N_factorial_n`` computes), ``minimum_defect == 0`` is decisive SPHERICAL
   (orientably thickenable) even when ``link_components > 1``.

   SPHERICAL members are EXPECTED here and are the point of the control: AK(2)'s class
   is AC-trivial, so its short/degenerate tail contains guaranteed-thickenable states.
   No mathematical claim is attached to any row; this file is calibration data.

2. **An explicit trivialization path** (``results/stable_ac/fable/
   ak2_trivialization_path.json``).  An AC-move path AK(2) -> standard in the exact
   twelve-move convention h1-h12 of ``ac_words`` (free reduction is part of
   ``apply_move``), found by a best-first search of STRICTLY at most
   :data:`PATH_POP_BUDGET` node pops.  The search runs at the class level on
   rotation-reduced keys (min-rotation of the cyclic reduction of each relator, NO
   inversion and NO swap, so that every class edge is realizable by pure h-moves), and
   the recorded move list is the deterministic expansion of the class path: conjugation
   moves to rotate each relator into the realization the edge used, then the one
   concatenation move.  **Arrival convention: canon.**  The twelve moves contain no
   relator-inversion and no swap move, so the search cannot target the ordered pair
   ``("x", "y")`` byte-exactly; the replay ends byte-identically at the recorded
   ``final_state`` (a length-1/length-1 pair), and
   ``canon_pair(final_state) == canon_pair(("x", "y")) == ("Y", "X")`` closes the
   remaining gap by Lemma P (inversion AC1 + swap composite), exactly as stated in the
   file.

   The **tail evaluation track** runs ``gamma_N_factorial_n`` (cap 2,000,000) on EVERY
   state of the path -- including the freely-but-not-cyclically-reduced intermediates
   (A-loop links; the census is loop- and short-relator-tolerant) and the short tail
   with 1- and 2-letter relators -- and records the FULL defect histogram,
   ``minimum_defect`` and ``link_components`` per state.  States whose compatible
   family exceeds the cap are recorded with status ``UNKNOWN_SIZE`` and are NOT
   decided.  The first path index whose census reaches ``minimum_defect == 0`` is
   recorded; the endpoint ``("x", "y")``-class state must be 0 with L = 2, interpreted
   SPHERICAL via Theorem D.

Budget rules implemented here (hard session rules): the harvest performs EXACTLY 1,000
pops, the path search STRICTLY at most 1,000 pops in aggregate; both numbers are
recorded in the artifacts and asserted by the tests.

New-files-only contract: this module IMPORTS the existing stack (``ac_words``,
``neuwirth_rank_n``, ``disconnected_split``/``rank3_round2``) and modifies nothing.
Plain python3, CPU only.
"""

from __future__ import annotations

import argparse
import heapq
import json
import os
import time

from experiments.stable_ac.fable import ac_words as W
from experiments.stable_ac.fable import neuwirth_rank_n as RN
from experiments.stable_ac.fable.disconnected_split import decide_pair
from experiments.stable_ac.fable.rank3_round2 import (
    BRANCH_BUDGET,
    FALLBACK_CAP,
    SCHEME_BUDGET,
    UNDECIDED_BUDGET,
)

__all__ = [
    "AK2",
    "STANDARD",
    "CAP",
    "HARVEST_POPS",
    "PATH_POP_BUDGET",
    "GENERATORS",
    "PathVerificationError",
    "rotations",
    "canon_class_children",
    "harvest_members",
    "decide_members",
    "rot_key",
    "rot_class_children",
    "class_path_search",
    "conjugation_moves_to",
    "reconstruct_exact_path",
    "build_trivialization_path",
    "tail_track",
    "verify_path_document",
    "census_summary",
    "run_battery",
]

AK2 = ("xxYYY", "xyxYXY")
STANDARD = ("x", "y")
GENERATORS = ("x", "y")
CAP = 15
HARVEST_POPS = 1_000
PATH_POP_BUDGET = 1_000

DEFAULT_MEMBERS = "results/stable_ac/fable/ak2_members.jsonl"
DEFAULT_PATH = "results/stable_ac/fable/ak2_trivialization_path.json"
DEFAULT_SUMMARY = "results/stable_ac/fable/ak2_battery_summary.json"

# conjugation move h-number for (relator index, payload p), acting as r -> p r p^-1
CONJUGATION_MOVE = {
    (0, "x"): 8, (0, "X"): 12, (0, "y"): 10, (0, "Y"): 6,
    (1, "x"): 9, (1, "X"): 5, (1, "y"): 11, (1, "Y"): 7,
}
# concatenation move h-number for (target relator index, sign of the other relator)
CONCAT_MOVE = {(1, +1): 1, (1, -1): 3, (0, +1): 4, (0, -1): 2}

STANDARD_CANON = W.canon_pair(*STANDARD)          # ("Y", "X")


class PathVerificationError(AssertionError):
    """The recorded trivialization path failed its byte-exact replay check."""


# --------------------------------------------------------------------------------------
# shared small pieces
# --------------------------------------------------------------------------------------


def rotations(w: str):
    """The distinct cyclic rotations of ``w``, sorted (deterministic expansion order)."""
    return sorted({w[i:] + w[:i] for i in range(len(w))})


def _concat_products(k1: str, k2: str, cap: int):
    """Every concatenation h-move applied to every rotation realization of the class.

    Yields ``(realization (a, b), (target, sign), exact result pair)`` for the four
    concatenation moves h1/h3 (r2 -> r2 r1^{+-1}) and h4/h2 (r1 -> r1 r2^{+-1}) over
    all cyclic rotations ``a`` of ``k1`` and ``b`` of ``k2``.  Inverted-relator
    realizations need no extra loop: the piece already carries both signs, and a child
    with an inverted TARGET is canon-equal to the opposite-sign child (``canon_rel``
    quotients by inversion).  Results that free-reduce to empty or exceed ``cap`` are
    dropped, mirroring the no-op rule of ``ac_words.apply_move``.
    """
    for a in rotations(k1):
        ia = W.inverse(a)
        for b in rotations(k2):
            ib = W.inverse(b)
            for target, sign in ((1, +1), (1, -1), (0, +1), (0, -1)):
                if target == 1:
                    new = W.free_reduce(b + (a if sign > 0 else ia))
                    exact = (a, new)
                else:
                    new = W.free_reduce(a + (b if sign > 0 else ib))
                    exact = (new, b)
                if not new or len(new) > cap:
                    continue
                yield (a, b), (target, sign), exact


# --------------------------------------------------------------------------------------
# 1. the member harvest (canonical seen-set, rotation-expanded children)
# --------------------------------------------------------------------------------------


def canon_class_children(key, cap: int = CAP):
    """Distinct canonical children of the canonical class ``key``; first exact wins.

    Deterministic: the rotation grid is iterated in sorted order and the first exact
    realization producing a canonical form is kept as its provenance.
    """
    out = {}
    for _real, _cc, exact in _concat_products(key[0], key[1], cap):
        ck = W.canon_pair(*exact)
        if ck not in out:
            out[ck] = exact
    return out


def harvest_members(root=AK2, pops: int = HARVEST_POPS, cap: int = CAP) -> dict:
    """Best-first canonical harvest: EXACTLY ``pops`` pops (asserted), cap ``cap``.

    Priority is total canonical length, ties by insertion order (deterministic).  The
    returned record maps canonical pair -> ``{order, first_seen_pop, first_exact,
    encounters}`` where ``order`` is the discovery index (0 = root) and
    ``first_seen_pop`` the 1-based pop during whose expansion the member first
    appeared (0 for the root).  A truncated run with ``pops = P`` discovers exactly
    the rows with ``first_seen_pop <= P``, in the same order -- the determinism
    contract asserted by the tests.
    """
    root = tuple(root)
    root_key = W.canon_pair(*root)
    found = {root_key: {"order": 0, "first_seen_pop": 0, "first_exact": root,
                        "encounters": 1}}
    heap = [(len(root_key[0]) + len(root_key[1]), 0, root_key)]
    tie = 1
    popped = 0
    children_generated = 0
    while heap and popped < pops:
        _priority, _tie, key = heapq.heappop(heap)
        popped += 1
        for ck, exact in sorted(canon_class_children(key, cap).items()):
            children_generated += 1
            record = found.get(ck)
            if record is not None:
                record["encounters"] += 1
                continue
            found[ck] = {"order": len(found), "first_seen_pop": popped,
                         "first_exact": exact, "encounters": 1}
            heapq.heappush(heap, (len(ck[0]) + len(ck[1]), tie, ck))
            tie += 1
    if popped != pops:
        raise AssertionError(
            f"harvest queue exhausted after {popped} pops; the {pops}-pop contract "
            "is broken"
        )
    return {
        "root": root,
        "root_key": root_key,
        "pops": popped,
        "pop_budget": pops,
        "relator_cap": cap,
        "children_generated": children_generated,
        "distinct_members": len(found),
        "queue_remaining": len(heap),
        "members": found,
    }


def census_summary(census: dict) -> dict:
    """The compact, JSON-stable slice of a ``gamma_N_factorial_n`` result."""
    return {
        "status": census["status"],
        "expected_cases": census["expected_cases"],
        "cap_rotations": census["cap_rotations"],
        "enumerated_cases": census.get("enumerated_cases"),
        "minimum_defect": census.get("minimum_defect"),
        "minimum_genus": census.get("minimum_genus"),
        "link_components": census["link_components"],
        "degrees": dict(census["degrees"]),
        "defect_histogram": {str(k): v for k, v in
                             sorted(census.get("defect_histogram", {}).items())},
    }


def _compact_counters(verdict) -> dict | None:
    """A small counter slice for r1c_v2 rows (full counters live in round-2 rows)."""
    decision = verdict.decision
    if decision is None or getattr(decision, "counters", None) is None:
        return None
    c = decision.counters.as_dict() if hasattr(decision.counters, "as_dict") \
        else dict(decision.counters.__dict__)
    keep = ("schemes_considered", "phase_tuples_considered", "exhaustive",
            "scheme_budget", "branch_budget")
    return {k: c[k] for k in keep if k in c}


def decide_members(members: dict, progress_every: int = 2_000):
    """Decide every distinct member through the pinned round-2 stack.

    ``disconnected_split.decide_pair`` = R1c-v2 cut-scheme solver first (exact for
    in-scope states), factorial census second where the family fits the 2,000,000-cap,
    with the census interpreted through Theorem D (R1E_DISCONNECTED_LINK.md): the
    general 2L defect makes ``minimum_defect == 0`` decisive SPHERICAL even for
    disconnected links such as the standard pair.  Budget exhaustion stays
    ``UNDECIDED_BUDGET``.  Returns a list of JSON rows in discovery order.
    """
    rows = []
    t0 = time.time()
    ordered = sorted(members.items(), key=lambda kv: kv[1]["order"])
    for i, (key, rec) in enumerate(ordered):
        try:
            data = RN.build_link_n(key, GENERATORS)
            family = RN.census_size(data, GENERATORS)
            structural_L = data.link_components
        except RN.NeuwirthInputError as exc:      # pragma: no cover - not expected
            family, structural_L = None, None
        verdict, support = decide_pair(key)
        row = {
            "record": "ak2_member",
            "canonical": list(key),
            "total_length": len(key[0]) + len(key[1]),
            "order": rec["order"],
            "first_seen_pop": rec["first_seen_pop"],
            "provenance": {"first_exact": list(rec["first_exact"]),
                           "encounters": rec["encounters"]},
            "census_family_size": family,
            "structural_link_components": structural_L,
            "support_kind": support.kind if support is not None else None,
            "verdict": verdict.verdict,
            "method": verdict.method,
            "reason": verdict.reason,
            "counters": _compact_counters(verdict),
            "census": census_summary(verdict.census) if verdict.census else None,
        }
        rows.append(row)
        if progress_every and (i + 1) % progress_every == 0:
            print(f"  decided {i + 1}/{len(ordered)} members "
                  f"({time.time() - t0:.0f}s)", flush=True)
    return rows


# --------------------------------------------------------------------------------------
# 2. the trivialization path (rotation-class search + exact h-move expansion)
# --------------------------------------------------------------------------------------


def _rot_min(w: str) -> str:
    w = W.cyclic_reduce(w)
    if not w:
        return w
    return min(w[i:] + w[:i] for i in range(len(w)))


def rot_key(state):
    """Ordered rotation-class key: min-rotation of each relator's cyclic reduction.

    Unlike ``canon_pair`` this quotients ONLY by conjugacy (AC3 + free reduction),
    never by inversion or swap, so any two exact states with the same key are
    connected by pure single-letter conjugation h-moves -- the property the path
    reconstruction relies on.
    """
    return (_rot_min(state[0]), _rot_min(state[1]))


def rot_class_children(key, cap: int = CAP):
    """``(child rot-key, realization, (target, sign), exact result)`` per child."""
    out = {}
    for real, cc, exact in _concat_products(key[0], key[1], cap):
        ck = rot_key(exact)
        if ck not in out:
            out[ck] = (real, cc, exact)
    return out


def _is_goal(key) -> bool:
    return len(key[0]) == 1 and len(key[1]) == 1


def class_path_search(root=AK2, pop_budget: int = PATH_POP_BUDGET, cap: int = CAP):
    """Best-first rotation-class search for a length-1/length-1 pair.

    STRICTLY at most ``pop_budget`` pops (the hard session rule); priority is total
    key length with insertion-order ties.  Returns ``(popped, goal_key_or_None,
    parents, children_generated)`` where ``parents`` maps each discovered key to its
    ``(parent key, realization, concat move, exact result)`` edge.
    """
    root = tuple(root)
    root_key = rot_key(root)
    parents = {root_key: None}
    heap = [(len(root_key[0]) + len(root_key[1]), 0, root_key)]
    tie = 1
    popped = 0
    children_generated = 0
    goal = None
    while heap and popped < pop_budget and goal is None:
        _priority, _tie, key = heapq.heappop(heap)
        popped += 1
        if _is_goal(key):
            goal = key
            break
        for ck, (real, cc, exact) in sorted(rot_class_children(key, cap).items()):
            children_generated += 1
            if ck in parents:
                continue
            parents[ck] = (key, real, cc, exact)
            if _is_goal(ck):
                goal = ck
                break
            heapq.heappush(heap, (len(ck[0]) + len(ck[1]), tie, ck))
            tie += 1
    return popped, goal, parents, children_generated


def conjugation_moves_to(state, idx: int, target_word: str, cap: int = CAP):
    """Conjugation h-moves carrying relator ``idx`` of ``state`` to ``target_word``.

    ``target_word`` must be a rotation of the cyclic reduction of ``state[idx]``.
    First strips conjugate pairs (payload = inverse of the leading letter removes one
    ``c ... c^-1`` shell per move), then rotates in the cheaper direction.  Every
    intermediate stays within ``cap`` (conjugation here never grows the relator).
    Returns ``(moves, state_after)``.
    """
    moves = []
    cur = tuple(state)
    while not W.is_cyclically_reduced(cur[idx]):
        payload = W.inverse_letter(cur[idx][0])
        move = CONJUGATION_MOVE[(idx, payload)]
        nxt = W.apply_move(cur, move, cap)
        if nxt == cur:
            raise AssertionError(f"reduction conjugation h{move} was a no-op on {cur}")
        moves.append(move)
        cur = nxt
    w = cur[idx]
    if len(w) != len(target_word) or (w and target_word not in w + w):
        raise AssertionError(f"{target_word!r} is not a rotation of {w!r}")
    if w != target_word:
        n = len(w)
        k = (w + w).index(target_word)
        steps = k if k <= n - k else n - k
        left = k <= n - k
        for _ in range(steps):
            payload = (W.inverse_letter(cur[idx][0]) if left else cur[idx][-1])
            move = CONJUGATION_MOVE[(idx, payload)]
            nxt = W.apply_move(cur, move, cap)
            if nxt == cur:
                raise AssertionError(f"rotation conjugation h{move} was a no-op on {cur}")
            moves.append(move)
            cur = nxt
        if cur[idx] != target_word:
            raise AssertionError("rotation bookkeeping failed")
    return moves, cur


def reconstruct_exact_path(root, goal, parents, cap: int = CAP):
    """Expand the class path into an explicit h-move list, replay-verified.

    Each class edge becomes: conjugation moves rotating r1 to the edge's realization
    ``a``, conjugation moves rotating r2 to ``b``, then the edge's concatenation move;
    the result is asserted byte-equal to the edge's recorded exact pair.  A final
    conjugation block reduces both relators to their 1-letter rotation-class
    representatives.  Returns ``(moves, final_state)``.
    """
    chain = []
    key = goal
    while parents[key] is not None:
        chain.append(parents[key])
        key = parents[key][0]
    chain.reverse()

    moves = []
    cur = tuple(root)
    for _parent, (a, b), (target, sign), exact in chain:
        ms, cur = conjugation_moves_to(cur, 0, a, cap)
        moves += ms
        ms, cur = conjugation_moves_to(cur, 1, b, cap)
        moves += ms
        concat = CONCAT_MOVE[(target, sign)]
        nxt = W.apply_move(cur, concat, cap)
        if nxt == cur:
            raise AssertionError(f"concatenation h{concat} was a no-op on {cur}")
        moves.append(concat)
        cur = nxt
        if cur != exact:
            raise AssertionError(f"edge replay mismatch: {cur} != {exact}")
    ms, cur = conjugation_moves_to(cur, 0, _rot_min(cur[0]), cap)
    moves += ms
    ms, cur = conjugation_moves_to(cur, 1, _rot_min(cur[1]), cap)
    moves += ms
    return moves, cur


def tail_track(states, cap_rotations: int = FALLBACK_CAP):
    """The battery track: the full exact census of EVERY state on the path.

    ``gamma_N_factorial_n`` is loop- and short-relator-tolerant and computes the
    general defect with the 2L term, so the freely-but-not-cyclically-reduced
    intermediates (A-loop links) and the 1-/2-letter tail are all in scope.  Theorem D
    (R1E_DISCONNECTED_LINK.md) makes ``minimum_defect == 0`` decisive SPHERICAL at any
    number of link components -- the reading recorded for the standard tail.  States
    over the rotation cap keep status ``UNKNOWN_SIZE`` and are not decided.
    """
    track = []
    for i, state in enumerate(states):
        data = RN.build_link_n(state, GENERATORS)
        census = RN.gamma_N_factorial_n(state, GENERATORS,
                                        cap_rotations=cap_rotations,
                                        keep_accepting=False)
        track.append({
            "index": i,
            "state": list(state),
            "total_length": W.total_length(state),
            "cyclically_reduced": (W.is_cyclically_reduced(state[0])
                                   and W.is_cyclically_reduced(state[1])),
            "has_A_loop": data.has_loop,
            "structural_link_components": data.link_components,
            "census": census_summary(census),
        })
    return track


def build_trivialization_path(root=AK2, pop_budget: int = PATH_POP_BUDGET,
                              cap: int = CAP, cap_rotations: int = FALLBACK_CAP):
    """Search, reconstruct, replay-verify and census-track the AK(2) -> standard path."""
    root = tuple(root)
    popped, goal, parents, children = class_path_search(root, pop_budget, cap)
    if goal is None:
        return {
            "record": "ak2_trivialization_path",
            "root": list(root),
            "relator_cap": cap,
            "search": {"algorithm": "best-first over rotation-class keys",
                       "pops": popped, "pop_budget": pop_budget,
                       "children_generated": children, "goal_found": False},
            "failure": f"no length-1/length-1 class within {pop_budget} pops",
        }
    moves, final_state = reconstruct_exact_path(root, goal, parents, cap)
    states = [root] + W.replay(root, moves, cap)
    if tuple(states[-1]) != tuple(final_state):
        raise PathVerificationError("reconstruction and replay disagree")
    if W.canon_pair(*final_state) != STANDARD_CANON:
        raise PathVerificationError(
            f"final state {final_state} is not the standard class {STANDARD_CANON}"
        )
    track = tail_track(states, cap_rotations)
    zero_indices = [t["index"] for t in track
                    if t["census"]["status"] == "OK"
                    and t["census"]["minimum_defect"] == 0]
    first_zero = zero_indices[0] if zero_indices else None
    doc = {
        "record": "ak2_trivialization_path",
        "root": list(root),
        "relator_cap": cap,
        "move_convention": ("h1-h12 of ac_words.py (app/ac_paths.tex numbering); "
                            "free reduction is part of apply_move"),
        "arrival_convention": (
            "canon: the replay from root must arrive byte-identically at final_state; "
            "final_state is the standard pair up to relator inversion and order, i.e. "
            "canon_pair(final_state) == canon_pair(('x','y')) == ('Y','X').  The "
            "twelve moves contain no inversion/swap move, so this is the exact "
            "arrival the h-calculus can express; inversion+swap are AC composites by "
            "Lemma P of R1E_DISCONNECTED_LINK.md."),
        "search": {
            "algorithm": ("best-first (total reduced length, insertion-order ties) "
                          "over rotation-class keys; class edges expanded to exact "
                          "h-moves deterministically afterwards"),
            "pops": popped,
            "pop_budget": pop_budget,
            "children_generated": children,
            "goal_found": True,
            "goal_key": list(goal),
            "class_edges": sum(1 for k in _walk_chain_length(goal, parents)),
        },
        "moves": list(moves),
        "move_count": len(moves),
        "states": [list(s) for s in states],
        "final_state": list(final_state),
        "replay_verified": True,
        "length_profile": [W.total_length(s) for s in states],
        "max_total_length": max(W.total_length(s) for s in states),
        "tail_track": track,
        "census_cap_rotations": cap_rotations,
        "zero_defect_indices": zero_indices,
        "first_zero_defect_index": first_zero,
        "first_zero_defect_state": (list(states[first_zero])
                                    if first_zero is not None else None),
        "endpoint_censuses": {
            "ak2": census_summary(RN.gamma_N_factorial_n(
                root, GENERATORS, cap_rotations=cap_rotations,
                keep_accepting=False)),
            "standard_xy": census_summary(RN.gamma_N_factorial_n(
                STANDARD, GENERATORS, cap_rotations=cap_rotations,
                keep_accepting=False)),
        },
    }
    return doc


def _walk_chain_length(goal, parents):
    key = goal
    while parents[key] is not None:
        yield 1
        key = parents[key][0]


def verify_path_document(doc: dict) -> bool:
    """Byte-exact replay verification of a recorded path document.

    Re-applies ``doc['moves']`` from ``doc['root']`` at ``doc['relator_cap']`` and
    demands: every recorded intermediate state matches the replay byte-identically,
    the arrival equals ``doc['final_state']``, and the arrival's canonical form is the
    standard class ``('Y', 'X')``.  Raises :class:`PathVerificationError` on any
    mismatch; returns ``True`` otherwise.
    """
    root = tuple(doc["root"])
    cap = doc["relator_cap"]
    moves = list(doc["moves"])
    states = [tuple(s) for s in doc["states"]]
    if not states or states[0] != root:
        raise PathVerificationError("states[0] is not the root")
    if len(states) != len(moves) + 1:
        raise PathVerificationError("state count != move count + 1")
    replayed = W.replay(root, moves, cap)
    for i, (got, recorded) in enumerate(zip(replayed, states[1:]), start=1):
        if tuple(got) != recorded:
            raise PathVerificationError(
                f"replay diverges at state {i}: {got} != {recorded}"
            )
    if tuple(doc["final_state"]) != states[-1]:
        raise PathVerificationError("final_state does not match states[-1]")
    if W.canon_pair(*states[-1]) != STANDARD_CANON:
        raise PathVerificationError("arrival is not the standard class")
    return True


# --------------------------------------------------------------------------------------
# 3. the runner
# --------------------------------------------------------------------------------------


def _verdict_histogram(rows):
    out = {}
    for row in rows:
        key = f"{row['verdict']}/{row['method']}"
        out[key] = out.get(key, 0) + 1
    return dict(sorted(out.items()))


def run_battery(members_out: str = DEFAULT_MEMBERS, path_out: str = DEFAULT_PATH,
                summary_out: str = DEFAULT_SUMMARY, pops: int = HARVEST_POPS,
                path_budget: int = PATH_POP_BUDGET, cap: int = CAP) -> dict:
    t0 = time.time()
    print(f"[1/3] harvesting AK(2) member set ({pops} pops, cap {cap}) ...", flush=True)
    harvest = harvest_members(AK2, pops, cap)
    print(f"      {harvest['distinct_members']} distinct members "
          f"({harvest['children_generated']} children generated)", flush=True)

    print("[2/3] deciding every member through the pinned round-2 stack ...",
          flush=True)
    rows = decide_members(harvest["members"])
    for directory in {os.path.dirname(members_out), os.path.dirname(path_out),
                      os.path.dirname(summary_out)}:
        if directory:
            os.makedirs(directory, exist_ok=True)
    with open(members_out, "w") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    print(f"      wrote {len(rows)} rows -> {members_out}", flush=True)

    print(f"[3/3] trivialization path (<= {path_budget} pops) + tail track ...",
          flush=True)
    path_doc = build_trivialization_path(AK2, path_budget, cap)
    if path_doc.get("failure") is None:
        verify_path_document(path_doc)
    with open(path_out, "w") as fh:
        json.dump(path_doc, fh, indent=1)
    print(f"      wrote path ({path_doc.get('move_count')} moves) -> {path_out}",
          flush=True)

    summary = {
        "record": "ak2_battery_summary",
        "root": list(AK2),
        "budgets": {
            "harvest_pops": harvest["pops"],
            "harvest_pop_budget": harvest["pop_budget"],
            "path_search_pops": path_doc["search"]["pops"],
            "path_search_pop_budget": path_doc["search"]["pop_budget"],
            "relator_cap": cap,
            "scheme_budget": SCHEME_BUDGET,
            "branch_budget": BRANCH_BUDGET,
            "census_cap": FALLBACK_CAP,
        },
        "harvest": {k: harvest[k] for k in
                    ("root_key", "pops", "pop_budget", "relator_cap",
                     "children_generated", "distinct_members", "queue_remaining")},
        "member_verdicts": _verdict_histogram(rows),
        "undecided_budget_rows": sum(1 for r in rows
                                     if r["verdict"] == UNDECIDED_BUDGET),
        "spherical_rows": sum(1 for r in rows if r["verdict"] == "SPHERICAL"),
        "path": {
            "goal_found": path_doc["search"]["goal_found"],
            "move_count": path_doc.get("move_count"),
            "final_state": path_doc.get("final_state"),
            "length_profile": path_doc.get("length_profile"),
            "max_total_length": path_doc.get("max_total_length"),
            "first_zero_defect_index": path_doc.get("first_zero_defect_index"),
            "zero_defect_indices": path_doc.get("zero_defect_indices"),
            "over_cap_states": [t["index"] for t in path_doc.get("tail_track", ())
                                if t["census"]["status"] != "OK"],
        },
        "elapsed_seconds": round(time.time() - t0, 1),
        "outputs": {"members": members_out, "path": path_out,
                    "summary": summary_out},
    }
    summary["harvest"]["root_key"] = list(summary["harvest"]["root_key"])
    with open(summary_out, "w") as fh:
        json.dump(summary, fh, indent=1)
    print(f"done in {summary['elapsed_seconds']}s; verdict histogram: "
          f"{summary['member_verdicts']}", flush=True)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--members-out", default=DEFAULT_MEMBERS)
    parser.add_argument("--path-out", default=DEFAULT_PATH)
    parser.add_argument("--summary-out", default=DEFAULT_SUMMARY)
    parser.add_argument("--pops", type=int, default=HARVEST_POPS)
    parser.add_argument("--path-budget", type=int, default=PATH_POP_BUDGET)
    parser.add_argument("--cap", type=int, default=CAP)
    args = parser.parse_args(argv)
    run_battery(args.members_out, args.path_out, args.summary_out,
                args.pops, args.path_budget, args.cap)


if __name__ == "__main__":
    main()
