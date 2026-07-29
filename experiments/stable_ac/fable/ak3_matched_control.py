"""The MATCHED-OPERATOR AK(3) control: the falsifiable contrast experiment.

This is the implementation of item 2 of the "CALIBRATION UPDATE" section of
``results/stable_ac/theory/fable/R3PRIME_DIGON_EXCESS.md``: harvest the classical AC
class of AK(3) = ``("xxxYYYY", "xyxYXY")`` -- AC-triviality OPEN, the minimal open case
of the AC conjecture -- with the IDENTICAL search operator that the AK(2) battery
(``experiments/stable_ac/fable/ak2_battery.py``) used on AK(2)'s provably-AC-trivial
class, and compare SPHERICAL rates at matched exploration.

Everything emitted here is DATA, not a mathematical claim.  Both outcomes are recorded
symmetrically: any SPHERICAL member goes through the full hit protocol (independent
L-general witness check, Todd-Coxeter triviality certificate, full move-chain replay
from the AK(3) root) and is flagged loudly WITHOUT interpretation (the
Corollary 3 / D3 / Lackenby-Thm-1.3 chain is flagged UNVERIFIED in the theory notes);
zero hits at matched exploration where AK(2) shows ~3% is exactly the class-level
contrast the R3' program needs, and is likewise only recorded, not interpreted.

The matched operator (all pieces imported from ``ak2_battery``, never copied where an
import suffices):

* **Seen-set** keyed on cyclically-REDUCED canonical forms (``ac_words.canon_pair``),
  per the lesson ``experiments/lessons/harvest-dedup-on-reduced-forms.md``.
* **Expansion** through ``ak2_battery._concat_products``: every concatenation h-move
  (h1-h4) applied to every pair of cyclic rotations of the two canonical relators.
  Each child is reachable from the parent class by an exact h-move composite
  (single-letter conjugations h5-h12 realize the rotations, one concatenation move
  forms the product); the final canonicalization is an AC composite by Lemma P of
  ``R1E_DISCONNECTED_LINK.md`` (rotation = AC3, inversion = AC1, swap = the explicit
  six-move composite).  So every row is a genuine member of AK(3)'s CLASSICAL AC class.
* **Priority**: best-first on total canonical length, insertion-order ties.
* **Budget**: EXACTLY :data:`HARVEST_POPS` = 1,000 pops -- hard session rule, asserted.
* **Operator-identity check**: the provenance-carrying harvest below is re-run against
  ``ak2_battery.harvest_members`` on the SAME root/pops/cap and the two member streams
  are asserted identical (keys, discovery order, first_seen_pop, first exact
  realizations, encounter counts); the result is recorded in the summary.

Length cap (recorded for the doc):

* **Rule**: per-relator cap = total root length + 4.  AK(2) ran at 15 = 11 + 4; AK(3)
  runs at :data:`CAP` = 17 = 13 + 4.
* **Relative-headroom reasoning** (the choice made): both runs give the operator the
  same additive slack above their root's scale -- any single relator may grow to
  (root total length) + 4 letters -- so the per-pop expansion geometry is comparable
  and the matched quantities are the operator + the 1,000-pop budget.
* **Absolute-cap argument** (the alternative, recorded for the doc): matching the cap
  ABSOLUTELY (15 for both) would leave AK(3) only 2 letters of headroom above its
  13-letter root versus AK(2)'s 4, mechanically suppressing child generation and
  biasing the control toward zero hits.  With cap 17 the AK(3) run explores a strictly
  LARGER absolute box (per-relator <= 17 vs <= 15), the conservative direction: a
  zero-hit outcome cannot be attributed to a smaller search space.

Provenance for replay: every non-root member row stores its parent's canonical pair
(``parent_key``), that same pair as the exact state replay starts from
(``parent_exact`` -- a canonical pair of cyclically reduced words IS an exact state in
the class), the rotation realization the expansion used, the concatenation h-move, and
the full h-move composite (``move_composite``: conjugations rotating relator 1 to
``realization[0]``, conjugations rotating relator 2 to ``realization[1]``, then the
concatenation move) whose byte-exact replay from ``parent_exact`` arrives at
``first_exact`` with ``canon_pair(first_exact) == canonical``.  Every single-step
composite is replay-verified at build time; full root-to-member CHAIN replays are
verified on a seeded 100-member sample and on EVERY SPHERICAL member.  The chain's
root row carries ``first_exact`` = the AK(3) root itself; the step from each child's
exact state to its canonical key (and from the root to the root key) is the Lemma P
canonicalization composite noted above.

Decisions: the pinned round-2 stack, identical to the AK(2) battery --
``disconnected_split.decide_pair`` = R1c-v2 cut-scheme solver first
(scheme budget 200,000 / branch budget 2,000,000), exact factorial census
``gamma_N_factorial_n`` second where the family fits the 2,000,000 cap, honest
``UNDECIDED_BUDGET`` otherwise (never a verdict beyond the cap).  Disconnected-link
members are decided by the census under **Theorem D** of ``R1E_DISCONNECTED_LINK.md``
(general defect ``|A| - |C| + 2L - |AC|``; ``minimum_defect == 0`` is decisive
SPHERICAL at any number of link components).  The decision loop itself is
``ak2_battery.decide_members``, imported -- the rows are then annotated in place, so
the two batteries share the code path byte for byte.

New-files-only contract: this module IMPORTS ``ak2_battery`` (including its
module-private ``_concat_products`` generator -- refactor-by-import, no copy) and the
existing stack; it modifies nothing.  Plain python3, CPU only.
"""

from __future__ import annotations

import argparse
import heapq
import json
import os
import random
import time
from collections import Counter

from experiments.stable_ac.fable import ac_words as W
from experiments.stable_ac.fable import ak2_battery as AB
from experiments.stable_ac.fable.disconnected_split import (
    TC_HIT_CAP,
    decide_pair,
    spherical_hit_protocol,
)
from experiments.stable_ac.fable.rank3_round2 import (
    BRANCH_BUDGET,
    FALLBACK_CAP,
    SCHEME_BUDGET,
    UNDECIDED_BUDGET,
)

__all__ = [
    "AK3",
    "CAP",
    "HARVEST_POPS",
    "REPLAY_SAMPLE_SIZE",
    "REPLAY_SEED",
    "ReplayVerificationError",
    "canon_class_children_prov",
    "harvest_members_prov",
    "operator_identity_report",
    "step_composite",
    "attach_and_verify_composites",
    "verify_step",
    "replay_chain",
    "annotate_rows",
    "spherical_stats",
    "ak2_side_of_comparison",
    "run_control",
]

AK3 = ("xxxYYYY", "xyxYXY")
CAP = 17                       # per-relator cap = total root length 13 + 4 (see docstring)
HARVEST_POPS = 1_000           # hard session rule: EXACTLY this many pops, asserted
REPLAY_SAMPLE_SIZE = 100
REPLAY_SEED = 20260729         # fixed so the 100-member chain sample is deterministic

DEFAULT_MEMBERS = "results/stable_ac/fable/ak3_matched_members.jsonl"
DEFAULT_SUMMARY = "results/stable_ac/fable/ak3_matched_summary.json"
AK2_SUMMARY_PATH = "results/stable_ac/fable/ak2_battery_summary.json"
AK2_MEMBERS_PATH = "results/stable_ac/fable/ak2_members.jsonl"

LOUD_ALERT = (
    "SPHERICAL MEMBER(S) IN AK(3)'S CLASSICAL CLASS.  This is DATA ONLY -- no "
    "mathematical claim is made here.  The interpretation chain (thickenable + "
    "trivial group + balanced => AC-trivial via Lackenby Thm 1.3) is FLAGGED "
    "UNVERIFIED in the theory notes; every hit below carries the full protocol "
    "artifacts (independent L-general witness check, Todd-Coxeter certificate, full "
    "move-chain replay from the AK(3) root) and requires an independent adversarial "
    "audit before any claim."
)


class ReplayVerificationError(AssertionError):
    """A stored provenance step or chain failed its byte-exact replay check."""


# --------------------------------------------------------------------------------------
# 1. the provenance-carrying harvest (operator identical to ak2_battery)
# --------------------------------------------------------------------------------------


def canon_class_children_prov(key, cap: int = CAP):
    """``ak2_battery.canon_class_children`` keeping full per-child provenance.

    Attribution: the iteration order and the first-exact-wins rule are byte-identical
    to ``ak2_battery.canon_class_children`` -- the shared generator
    ``ak2_battery._concat_products`` is IMPORTED, not copied; the only difference is
    that the winning child also keeps the ``(rotation realization, (target, sign))``
    that produced it.  The child key sets and first exact realizations therefore agree
    with the AK(2) battery's operator by construction (and are asserted to, by
    :func:`operator_identity_report`).
    """
    out = {}
    for real, cc, exact in AB._concat_products(key[0], key[1], cap):
        ck = W.canon_pair(*exact)
        if ck not in out:
            out[ck] = (exact, real, cc)
    return out


def harvest_members_prov(root=AK3, pops: int = HARVEST_POPS, cap: int = CAP) -> dict:
    """``ak2_battery.harvest_members`` with per-member replay provenance.

    Attribution: the traversal (priority = total canonical length, insertion-order
    ties; seen-set on canonical pairs; ``sorted`` child iteration; the exactly-``pops``
    assertion) is a line-for-line mirror of ``ak2_battery.harvest_members`` -- copied
    only because that function does not expose the parent/realization of each first
    encounter, which the replay contract of this control requires.  Identity of the
    two operators is asserted by :func:`operator_identity_report`, not assumed.

    Per member the record adds ``parent_key`` (the popped canonical class it was first
    generated from; ``None`` for the root), ``realization`` (the rotation pair the
    concatenation acted on) and ``concat_move`` (the h-move number).
    """
    root = tuple(root)
    root_key = W.canon_pair(*root)
    found = {root_key: {"order": 0, "first_seen_pop": 0, "first_exact": root,
                        "encounters": 1, "parent_key": None, "realization": None,
                        "concat_move": None}}
    heap = [(len(root_key[0]) + len(root_key[1]), 0, root_key)]
    tie = 1
    popped = 0
    children_generated = 0
    while heap and popped < pops:
        _priority, _tie, key = heapq.heappop(heap)
        popped += 1
        for ck, (exact, real, cc) in sorted(canon_class_children_prov(key, cap).items()):
            children_generated += 1
            record = found.get(ck)
            if record is not None:
                record["encounters"] += 1
                continue
            found[ck] = {"order": len(found), "first_seen_pop": popped,
                         "first_exact": exact, "encounters": 1,
                         "parent_key": key, "realization": real,
                         "concat_move": AB.CONCAT_MOVE[cc]}
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


def operator_identity_report(harvest: dict) -> dict:
    """Assert the provenance harvest IS the ak2_battery operator on this root.

    Re-runs ``ak2_battery.harvest_members`` verbatim with the same root/pops/cap and
    compares member keys, discovery orders, ``first_seen_pop``, first exact
    realizations and encounter counts.  Any mismatch raises -- the whole control is
    meaningless if the operator is not byte-identical.
    """
    ref = AB.harvest_members(harvest["root"], harvest["pop_budget"],
                             harvest["relator_cap"])
    mine, theirs = harvest["members"], ref["members"]
    if set(mine) != set(theirs):
        raise AssertionError(
            f"operator mismatch: {len(mine)} vs {len(theirs)} members, symmetric "
            f"difference size {len(set(mine) ^ set(theirs))}"
        )
    for key, rec in mine.items():
        other = theirs[key]
        for field in ("order", "first_seen_pop", "first_exact", "encounters"):
            if rec[field] != other[field]:
                raise AssertionError(
                    f"operator mismatch on {key}: {field} {rec[field]} != "
                    f"{other[field]}"
                )
    if (harvest["children_generated"] != ref["children_generated"]
            or harvest["queue_remaining"] != ref["queue_remaining"]):
        raise AssertionError("operator mismatch: traversal counters differ")
    return {
        "checked_against": "ak2_battery.harvest_members (verbatim import, same "
                           "root/pops/cap)",
        "pops": ref["pops"],
        "relator_cap": ref["relator_cap"],
        "members_compared": len(mine),
        "children_generated_equal": True,
        "identical": True,
    }


# --------------------------------------------------------------------------------------
# 2. exact h-move composites + replay verification
# --------------------------------------------------------------------------------------


def step_composite(parent_key, realization, concat_move: int, cap: int = CAP):
    """The exact h-move list realizing one expansion step, and its arrival state.

    Starts from the parent's canonical pair AS AN EXACT STATE (cyclically reduced
    words are legal exact relators), rotates relator 1 to ``realization[0]`` and
    relator 2 to ``realization[1]`` via ``ak2_battery.conjugation_moves_to``
    (conjugation h-moves only), then applies the concatenation h-move.  The caller
    verifies the arrival byte-exactly against the recorded ``first_exact``.
    """
    state = (parent_key[0], parent_key[1])
    a, b = realization
    moves, state = AB.conjugation_moves_to(state, 0, a, cap)
    more, state = AB.conjugation_moves_to(state, 1, b, cap)
    moves = moves + more + [concat_move]
    nxt = W.apply_move(state, concat_move, cap)
    if nxt == state:
        raise ReplayVerificationError(
            f"concatenation h{concat_move} was a no-op on {state}"
        )
    return moves, nxt


def verify_step(parent_exact, moves, expected_exact, expected_canonical=None,
                cap: int = CAP) -> bool:
    """Byte-exact replay of ONE stored composite through ``ac_words.replay`` alone.

    Deliberately independent of :func:`step_composite`: this function trusts nothing
    but the stored ``(parent_exact, moves, expected_exact)`` triple and the twelve-move
    calculus.  Raises :class:`ReplayVerificationError` on any mismatch.
    """
    parent_exact = tuple(parent_exact)
    states = W.replay(parent_exact, list(moves), cap)
    arrival = tuple(states[-1]) if states else parent_exact
    if arrival != tuple(expected_exact):
        raise ReplayVerificationError(
            f"step replay mismatch: {arrival} != {tuple(expected_exact)} "
            f"(from {parent_exact} via {list(moves)})"
        )
    if expected_canonical is not None \
            and W.canon_pair(*arrival) != tuple(expected_canonical):
        raise ReplayVerificationError(
            f"canonicalization mismatch: canon{arrival} != {tuple(expected_canonical)}"
        )
    return True


def attach_and_verify_composites(harvest: dict) -> dict:
    """Compute ``move_composite`` for EVERY non-root member and replay-verify each.

    Verification is done through :func:`verify_step` (the independent replayer), not
    by trusting :func:`step_composite`'s own arrival.  Returns counters for the
    summary.
    """
    cap = harvest["relator_cap"]
    verified = 0
    for key, rec in harvest["members"].items():
        if rec["parent_key"] is None:
            rec["move_composite"] = None
            continue
        moves, _arrival = step_composite(rec["parent_key"], rec["realization"],
                                         rec["concat_move"], cap)
        verify_step(rec["parent_key"], moves, rec["first_exact"],
                    expected_canonical=key, cap=cap)
        rec["move_composite"] = moves
        verified += 1
    return {"single_step_composites_verified": verified,
            "members_total": len(harvest["members"])}


def replay_chain(key, index, root=AK3, cap: int = CAP) -> dict:
    """Full byte-exact replay of the chain root -> member from stored provenance.

    ``index`` maps canonical-pair tuples to member rows (as written to the artifact:
    provenance carries ``parent_key`` / ``parent_exact`` / ``move_composite`` /
    ``first_exact``).  Walks parent links up to the root key, then verifies every
    step downward with :func:`verify_step`, checks ``parent_exact == parent_key``
    (the recorded replay start must be the parent's canonical pair), parent-order
    monotonicity, and that the root row's exact realization is the AK(3) root itself.
    """
    root = tuple(root)
    root_key = W.canon_pair(*root)
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
                f"pair {parent_key}"
            )
        parent_row = index.get(parent_key)
        if parent_row is None:
            raise ReplayVerificationError(f"chain broken: parent {parent_key} missing")
        if parent_row["order"] >= row["order"]:
            raise ReplayVerificationError(
                f"parent order {parent_row['order']} not before child {row['order']}"
            )
        verify_step(prov["parent_exact"], prov["move_composite"],
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
            f"is not the AK(3) root {root}"
        )
    steps.reverse()
    return {"verified": True, "chain_steps": len(steps),
            "h_moves_total": sum(steps), "h_moves_per_step": steps}


# --------------------------------------------------------------------------------------
# 3. decisions (ak2_battery.decide_members imported verbatim) + row annotation
# --------------------------------------------------------------------------------------


def annotate_rows(rows, harvest: dict):
    """Patch the ``ak2_battery.decide_members`` rows into ak3 control rows, in place.

    The decision loop itself is shared byte-for-byte with the AK(2) battery; only the
    record tag, degeneracy bookkeeping and the replay provenance are added here.
    """
    ordered = sorted(harvest["members"].items(), key=lambda kv: kv[1]["order"])
    if len(rows) != len(ordered):
        raise AssertionError("row / member count mismatch")
    for row, (key, rec) in zip(rows, ordered):
        if row["canonical"] != list(key):
            raise AssertionError(f"row order mismatch at {row['canonical']} vs {key}")
        row["record"] = "ak3_member"
        row["relator_lengths"] = [len(key[0]), len(key[1])]
        row["non_degenerate"] = len(key[0]) >= 3 and len(key[1]) >= 3
        prov = row["provenance"]
        if rec["parent_key"] is None:
            prov.update(parent_key=None, parent_exact=None, realization=None,
                        concat_move=None, move_composite=None)
        else:
            prov.update(parent_key=list(rec["parent_key"]),
                        parent_exact=list(rec["parent_key"]),
                        realization=list(rec["realization"]),
                        concat_move=rec["concat_move"],
                        move_composite=list(rec["move_composite"]))
    return rows


def spherical_stats(rows) -> dict:
    """The comparison bookkeeping slice for one battery's member rows."""
    spherical = [r for r in rows if r["verdict"] == "SPHERICAL"]
    non_deg = [r for r in spherical
               if all(len(w) >= 3 for w in r["canonical"])]
    return {
        "distinct_members": len(rows),
        "verdict_method_histogram": AB._verdict_histogram(rows),
        "verdict_histogram": dict(sorted(Counter(r["verdict"]
                                                 for r in rows).items())),
        "spherical_rows": len(spherical),
        "spherical_rate": (len(spherical) / len(rows)) if rows else None,
        "spherical_by_total_length": {
            str(k): v for k, v in
            sorted(Counter(r["total_length"] for r in spherical).items())},
        "non_degenerate_spherical_rows": len(non_deg),
        "undecided_budget_rows": sum(1 for r in rows
                                     if r["verdict"] == UNDECIDED_BUDGET),
        "member_total_length_histogram": {
            str(k): v for k, v in
            sorted(Counter(r["total_length"] for r in rows).items())},
    }


def ak2_side_of_comparison(summary_path: str = AK2_SUMMARY_PATH,
                           members_path: str = AK2_MEMBERS_PATH) -> dict:
    """The AK(2) numbers, re-quoted from the COMMITTED battery artifacts (read-only)."""
    with open(summary_path, encoding="utf-8") as fh:
        committed = json.load(fh)
    rows = []
    with open(members_path, encoding="utf-8") as fh:
        for line in fh:
            rows.append(json.loads(line))
    stats = spherical_stats(rows)
    if stats["distinct_members"] != committed["harvest"]["distinct_members"]:
        raise AssertionError("ak2 members file does not match the ak2 summary")
    if stats["spherical_rows"] != committed["spherical_rows"]:
        raise AssertionError("ak2 spherical count does not match the ak2 summary")
    stats.update(
        root=committed["root"],
        relator_cap=committed["budgets"]["relator_cap"],
        harvest_pops=committed["budgets"]["harvest_pops"],
        children_generated=committed["harvest"]["children_generated"],
        quoted_from=[summary_path, members_path],
        committed_verdict_method_histogram=committed["member_verdicts"],
    )
    return stats


# --------------------------------------------------------------------------------------
# 4. the runner
# --------------------------------------------------------------------------------------


def run_control(members_out: str = DEFAULT_MEMBERS,
                summary_out: str = DEFAULT_SUMMARY,
                pops: int = HARVEST_POPS, cap: int = CAP) -> dict:
    if pops != HARVEST_POPS:
        raise AssertionError(
            f"the control's budget is EXACTLY {HARVEST_POPS} pops (hard session "
            f"rule); got {pops}.  Small harvests are available via "
            "harvest_members_prov for tests, but no artifact is written off-budget."
        )
    t0 = time.time()
    print(f"[1/6] harvesting AK(3) member set ({pops} pops, cap {cap}) ...",
          flush=True)
    harvest = harvest_members_prov(AK3, pops, cap)
    print(f"      {harvest['distinct_members']} distinct members "
          f"({harvest['children_generated']} children generated)", flush=True)
    print("      operator-identity check vs ak2_battery.harvest_members ...",
          flush=True)
    identity = operator_identity_report(harvest)

    print("[2/6] computing + replay-verifying every single-step h-move composite ...",
          flush=True)
    step_report = attach_and_verify_composites(harvest)
    print(f"      {step_report['single_step_composites_verified']} composites "
          "verified byte-exactly", flush=True)

    print("[3/6] deciding every member through the pinned round-2 stack "
          "(ak2_battery.decide_members, imported) ...", flush=True)
    rows = AB.decide_members(harvest["members"])
    annotate_rows(rows, harvest)

    print("[4/6] chain replays: seeded 100-member sample + every SPHERICAL member; "
          "hit protocol on any SPHERICAL ...", flush=True)
    index = {tuple(r["canonical"]): r for r in rows}
    non_root = [tuple(r["canonical"]) for r in rows if r["order"] > 0]
    rng = random.Random(REPLAY_SEED)
    sample_keys = rng.sample(non_root, min(REPLAY_SAMPLE_SIZE, len(non_root)))
    sample_chains = []
    for key in sample_keys:
        chain = replay_chain(key, index, AK3, cap)
        sample_chains.append({"canonical": list(key),
                              "chain_steps": chain["chain_steps"],
                              "h_moves_total": chain["h_moves_total"]})
    spherical_rows = [r for r in rows if r["verdict"] == "SPHERICAL"]
    hits = []
    for row in spherical_rows:
        key = tuple(row["canonical"])
        chain = replay_chain(key, index, AK3, cap)
        row["chain_replay"] = chain
        verdict, _support = decide_pair(key)
        row["re_decision"] = {"verdict": verdict.verdict, "method": verdict.method,
                              "agrees": verdict.verdict == row["verdict"]}
        protocol = spherical_hit_protocol(key, verdict, tc_cap=TC_HIT_CAP)
        row["hit_protocol"] = protocol
        hits.append({
            "canonical": row["canonical"],
            "total_length": row["total_length"],
            "relator_lengths": row["relator_lengths"],
            "non_degenerate": row["non_degenerate"],
            "order": row["order"],
            "first_seen_pop": row["first_seen_pop"],
            "verdict": row["verdict"],
            "method": row["method"],
            "re_decision": row["re_decision"],
            "chain_replay": {k: chain[k] for k in
                             ("verified", "chain_steps", "h_moves_total")},
            "hit_protocol": protocol,
        })
    print(f"      {len(sample_chains)} sampled chains verified; "
          f"{len(spherical_rows)} SPHERICAL member(s)", flush=True)

    print("[5/6] AK(2) comparison from the committed battery artifacts ...",
          flush=True)
    ak3_stats = spherical_stats(rows)
    ak3_stats.update(root=list(AK3), relator_cap=cap, harvest_pops=harvest["pops"],
                     children_generated=harvest["children_generated"])
    ak2_stats = ak2_side_of_comparison()

    print("[6/6] writing artifacts ...", flush=True)
    for directory in {os.path.dirname(members_out), os.path.dirname(summary_out)}:
        if directory:
            os.makedirs(directory, exist_ok=True)
    with open(members_out, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    print(f"      wrote {len(rows)} rows -> {members_out}", flush=True)

    summary = {
        "record": "ak3_matched_control_summary",
        "purpose": ("Matched-operator control of the CALIBRATION UPDATE in "
                    "results/stable_ac/theory/fable/R3PRIME_DIGON_EXCESS.md: AK(3)'s "
                    "classical class (AC-triviality OPEN) harvested with the "
                    "IDENTICAL operator the AK(2) battery ran on a provably "
                    "AC-trivial class.  DATA ONLY -- no mathematical claim."),
        "root": list(AK3),
        "root_key": list(harvest["root_key"]),
        "design": {
            "operator": {
                "seen_set": "cyclically-reduced canonical pairs (ac_words.canon_pair)",
                "expansion": ("every concatenation h-move (h1-h4) on every pair of "
                              "cyclic rotations of the two canonical relators "
                              "(ak2_battery._concat_products, imported)"),
                "priority": "best-first on total canonical length, insertion-order "
                            "ties",
                "identical_to": "experiments/stable_ac/fable/ak2_battery.py "
                                "harvest_members",
                "identity_check": identity,
            },
            "length_cap": {
                "value": cap,
                "rule": "per-relator cap = total root length + 4",
                "ak2_value": AB.CAP,
                "relative_headroom_reasoning": (
                    "AK(2) ran at 15 = 11 + 4; AK(3) runs at 17 = 13 + 4.  Both runs "
                    "give the operator the same additive slack above their root's "
                    "scale (any relator may grow to root-total + 4 letters), keeping "
                    "the per-pop expansion geometry comparable; the matched "
                    "quantities are the operator and the 1,000-pop budget."),
                "absolute_cap_argument": (
                    "An ABSOLUTE match (cap 15 for both) would leave AK(3) only 2 "
                    "letters of headroom above its 13-letter root versus AK(2)'s 4, "
                    "mechanically suppressing child generation and biasing the "
                    "control toward zero hits.  Cap 17 makes the AK(3) box strictly "
                    "LARGER (per-relator <= 17 vs <= 15) -- the conservative "
                    "direction: a zero-hit outcome cannot be attributed to a smaller "
                    "search space."),
            },
            "decision_stack": (
                "disconnected_split.decide_pair, identical to the AK(2) battery: "
                "R1c-v2 cut-scheme solver first, exact factorial census fallback "
                "where the family fits the cap, honest UNDECIDED_BUDGET otherwise; "
                "disconnected members decided by the census under Theorem D of "
                "R1E_DISCONNECTED_LINK.md (general 2L defect; minimum_defect == 0 "
                "decisive SPHERICAL at any L).  Decision loop = "
                "ak2_battery.decide_members, imported verbatim."),
            "provenance_semantics": (
                "Each non-root row stores parent_key (the popped canonical class), "
                "parent_exact (== parent_key: a canonical pair of cyclically reduced "
                "words is itself an exact state), realization (the rotation pair the "
                "concatenation acted on), concat_move, and move_composite -- the "
                "exact h1-h12 list whose replay from parent_exact arrives "
                "byte-identically at first_exact with canon_pair(first_exact) == "
                "canonical.  The child-exact -> child-canonical step (and root -> "
                "root_key) is the Lemma P AC composite of R1E_DISCONNECTED_LINK.md "
                "(rotation = AC3 conjugations, inversion = AC1, swap = the explicit "
                "six-move composite), exactly as in the AK(2) battery's provenance "
                "convention; so every row is a member of AK(3)'s CLASSICAL class "
                "with a fully replayable route from the root."),
            "hit_protocol": (
                "For every SPHERICAL row: independent L-general witness check "
                "(disconnected_split.check_witness_l_general via "
                "spherical_hit_protocol), Todd-Coxeter triviality certificate "
                f"(coset_enum, cap {TC_HIT_CAP}), full move-chain replay from the "
                "AK(3) root, re-decision agreement, and the loud summary field "
                "SPHERICAL_HITS below."),
        },
        "budgets": {
            "harvest_pops": harvest["pops"],
            "harvest_pop_budget": harvest["pop_budget"],
            "relator_cap": cap,
            "scheme_budget": SCHEME_BUDGET,
            "branch_budget": BRANCH_BUDGET,
            "census_cap": FALLBACK_CAP,
            "tc_hit_cap": TC_HIT_CAP,
            "pinned_from": "rank3_round2 (round-2 values, imported verbatim; "
                           "identical to the AK(2) battery)",
        },
        "harvest": {k: harvest[k] for k in
                    ("pops", "pop_budget", "relator_cap", "children_generated",
                     "distinct_members", "queue_remaining")},
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
            "spherical_chains_verified": len(spherical_rows),
        },
        "member_verdicts": AB._verdict_histogram(rows),
        "undecided_budget_rows": ak3_stats["undecided_budget_rows"],
        "spherical_rows": ak3_stats["spherical_rows"],
        "LOUD_SPHERICAL_ALERT": bool(hits),
        "SPHERICAL_HITS": hits if hits else [],
        "SPHERICAL_HITS_NOTE": (LOUD_ALERT if hits else
                                "zero SPHERICAL members at matched exploration; see "
                                "the comparison block -- data only, no claim"),
        "comparison": {
            "matched": ["seen-set", "expansion operator", "priority",
                        "pop budget (exactly 1,000)",
                        "relative length-cap headroom (root total + 4)",
                        "decision stack + budgets"],
            "not_matched": ["absolute per-relator cap (17 vs 15; AK(3)'s box is "
                            "strictly larger -- see design.length_cap)"],
            "ak3": ak3_stats,
            "ak2": ak2_stats,
        },
        "elapsed_seconds": round(time.time() - t0, 1),
        "outputs": {"members": members_out, "summary": summary_out},
    }
    with open(summary_out, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1)
        fh.write("\n")
    print(f"done in {summary['elapsed_seconds']}s; verdicts: "
          f"{summary['member_verdicts']}; spherical: "
          f"{summary['spherical_rows']}", flush=True)
    if hits:
        print("!" * 78, flush=True)
        print(LOUD_ALERT, flush=True)
        for hit in hits:
            print(f"  {tuple(hit['canonical'])} (len {hit['total_length']}, "
                  f"non_degenerate={hit['non_degenerate']})", flush=True)
        print("!" * 78, flush=True)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--members-out", default=DEFAULT_MEMBERS)
    parser.add_argument("--summary-out", default=DEFAULT_SUMMARY)
    args = parser.parse_args(argv)
    run_control(args.members_out, args.summary_out)


if __name__ == "__main__":
    main()
