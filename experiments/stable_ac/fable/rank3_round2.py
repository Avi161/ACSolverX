"""Round 2 of the direct rank-3 STABLE-move harvest, run through the R1c-v2 solver.

Round 1 (``rank3_stable_harvest.py``) found 3,104 distinct canonical states and could
decide only 25 of them: the R1c gate (3-connected planar simple support) rejected
**100 %** of the corridor, and the factorial census fitted the 2,000,000-rotation cap in
25 cases, leaving **3,079** in the ``UNDECIDED_BUDGET`` bucket.  R1c-v2
(``neuwirth_cut_schemes.py``) removes the connectivity hypothesis on the simple support,
so the 628 two-cut states, the 1,444 low-simple-degree states and the 1,032 short-relator
states of round 1 are all in scope now.  This module re-runs the corridor with that
solver in front of the census.

Four amendments to the round-1 search (the Colab spec for this round):

1. **per-relator cap 26 for the ``P25`` root** (15 for ``AK3``).  Round 1 used 15
   everywhere and the ``P25`` component froze after 93 states with an exhausted queue --
   the cap, not the budget, was the binding constraint.
2. **exact-word frontier, canonical dedup for counting only.**  The seen-set that gates
   *expansion* is keyed on the exact word tuple, so children are expanded from every new
   exact realization; the canonical (cyclically reduced, lex-min over rotation x
   inversion, relator multiset sorted) form is used only to count distinct states and to
   pick the representative that gets decided.  Round 1 deduplicated the frontier itself,
   which pruned exact realizations whose *children* are not canonical duplicates.
3. **z-entangling bias.**  A child whose total ``z``/``Z`` occurrence count strictly
   exceeds its parent's gets a priority bonus of :data:`Z_BONUS`, i.e. it is popped as if
   it were ``Z_BONUS`` letters shorter.  The stabilizing generator only matters once it
   is entangled with ``x`` and ``y``; a pure length priority keeps ``z`` at multiplicity
   one for a long time.
4. **1,000 pops per root, one round** -- unchanged from round 1, so the two rounds are
   comparable.

Deciding a state (the canonical representative, which is what the harvest counts):

1. :func:`neuwirth_cut_schemes.solve_cut_schemes` -- the R1c-v2 decision procedure.  Its
   ``NOT_SPHERICAL`` is exhaustive over schemes x phases x seeds x cross-cycle
   combinations, and a certified non-planar R-node skeleton is a real ``NO``.
2. Anything it fails closed on (an ``A``-loop, a disconnected link, a germ that does not
   occur, a scheme/branch budget) falls through to the exact factorial census
   ``gamma_N_factorial_n`` with the round-1 per-state cap of 2,000,000 rotation systems
   and a global work budget, smallest family first.
3. Whatever is still open is bucketed as ``UNDECIDED_BUDGET`` or ``UNSUPPORTED`` and
   counted separately -- never folded into "all NO".

Any ``SPHERICAL`` verdict is re-verified by ``witness_check_n`` (permutation-only, shares
no scheme code), re-run through the exact census when that fits, given a Todd-Coxeter
triviality attempt over ``("x","y","z")``, and **flagged loudly**: a stable-class member
with ``gamma_N = 0`` and ``pi_1 = 1`` would say the target is stably AC-trivial.
"""

from __future__ import annotations

import argparse
import heapq
import json
import os
import time
from dataclasses import dataclass

from experiments.stable_ac.fable import coset_enum as CE
from experiments.stable_ac.fable import neuwirth_cut_schemes as CS
from experiments.stable_ac.fable import neuwirth_rank_n as RN
from experiments.stable_ac.fable import witness_check_n as WCN
from experiments.stable_ac.fable.rank3_stable_harvest import (
    AK3,
    P25,
    canon_state,
    letter_order,
    moves,
)

GENERATORS = ("x", "y", "z")
POPS_PER_ROOT = 1_000
Z_BONUS = 2

# amendment 1: a per-root relator cap
ROOTS = (
    ("AK3+z", tuple(AK3) + ("z",), 15),
    ("P25+z", tuple(P25) + ("z",), 26),
)

DEFAULT_OUTPUT = "results/stable_ac/fable/rank3_harvest_round2.jsonl"

FALLBACK_CAP = 2_000_000
FALLBACK_TOTAL_BUDGET = 50_000_000
SCHEME_BUDGET = 200_000
BRANCH_BUDGET = 4_000_000

UNDECIDED_BUDGET = "UNDECIDED_BUDGET"


def z_occurrences(state) -> int:
    """Total number of ``z``/``Z`` letters in a state (amendment 3's bias signal)."""
    return sum(w.count("z") + w.count("Z") for w in state)


# --------------------------------------------------------------------------------------
# the search (amendments 1-4)
# --------------------------------------------------------------------------------------


@dataclass
class Found:
    root: str
    canonical: tuple
    exact: tuple
    depth: int
    order_found: int
    move: str | None
    parent_canonical: tuple | None
    exact_realizations: int = 1
    max_z: int = 0

    def total_length(self) -> int:
        return sum(len(w) for w in self.exact)

    def canonical_length(self) -> int:
        return sum(len(w) for w in self.canonical)


def harvest_root(root_name: str, root_state, cap: int, pops: int = POPS_PER_ROOT,
                 generators=GENERATORS, z_bonus: int = Z_BONUS) -> dict:
    """Best-first expansion over the **exact** frontier, counted on canonical forms."""
    order = letter_order(generators)
    root_state = tuple(root_state)
    root_key = canon_state(root_state, order)

    found: dict = {root_key: Found(root_name, root_key, root_state, 0, 0, None, None,
                                   1, z_occurrences(root_state))}
    seen_exact = {root_state}
    heap = [(sum(len(w) for w in root_state), 0, root_state, 0)]
    tie = 1
    popped = generated = duplicate_exact = new_canonical = 0
    z_boosted = 0
    while heap and popped < pops:
        _priority, _tie, state, depth = heapq.heappop(heap)
        popped += 1
        parent_key = canon_state(state, order)
        parent_z = z_occurrences(state)
        for label, child in moves(state, generators, cap):
            generated += 1
            if child in seen_exact:
                duplicate_exact += 1
                continue
            seen_exact.add(child)
            child_z = z_occurrences(child)
            bonus = z_bonus if child_z > parent_z else 0
            if bonus:
                z_boosted += 1
            child_key = canon_state(child, order)
            record = found.get(child_key)
            if record is None:
                found[child_key] = Found(root_name, child_key, child, depth + 1,
                                         len(found), label, parent_key, 1, child_z)
                new_canonical += 1
            else:
                record.exact_realizations += 1
                record.max_z = max(record.max_z, child_z)
            heapq.heappush(
                heap,
                (sum(len(w) for w in child) - bonus, tie, child, depth + 1))
            tie += 1
    return {
        "root": root_name,
        "root_state": root_state,
        "root_key": root_key,
        "relator_cap": cap,
        "z_bonus": z_bonus,
        "pops": popped,
        "pop_budget": pops,
        "queue_remaining": len(heap),
        "queue_exhausted": not heap,
        "children_generated": generated,
        "duplicate_exact_children": duplicate_exact,
        "distinct_exact_states": len(seen_exact),
        "distinct_states": len(found),
        "z_boosted_children": z_boosted,
        "max_z_occurrences": max(r.max_z for r in found.values()),
        "states": found,
    }


# --------------------------------------------------------------------------------------
# deciding a state
# --------------------------------------------------------------------------------------


@dataclass
class Verdict:
    verdict: str
    method: str
    reason: str | None = None
    census: dict | None = None
    decision: object | None = None


V2_GATES = (
    "IN SCOPE (R1c-v2)",
    "certified non-planar S",
    "A-loop",
    "disconnected link",
    "germ absent from every relator",
    "2n < 4",
    "scheme/branch budget",
    "malformed",
)


def v2_gate(support) -> str:
    """Which R1c-v2 hypothesis, if any, stopped this state (Sec. 8.2 of the note)."""
    if support.kind == CS.IN_SCOPE:
        return "IN SCOPE (R1c-v2)"
    if support.kind == CS.NONPLANAR:
        return "certified non-planar S"
    reason = support.reason or ""
    if "malformed" in reason:
        return "malformed"
    if "do not occur" in reason:
        return "germ absent from every relator"
    if "loop" in reason:
        return "A-loop"
    if "components" in reason:
        return "disconnected link"
    if "2n =" in reason:
        return "2n < 4"
    return "scheme/branch budget"


def decide_state(words, generators=GENERATORS, scheme_budget: int = SCHEME_BUDGET,
                 branch_budget: int = BRANCH_BUDGET):
    """R1c-v2 first; returns ``(verdict, support)`` with the support kept for reporting."""
    support = CS.classify_cut_support(words, generators)
    if support.kind == CS.UNSUPPORTED:
        return Verdict(CS.UNSUPPORTED, "r1c_v2_gate", support.reason), support
    decision = CS.solve_cut_schemes(words, generators, scheme_budget=scheme_budget,
                                    branch_budget=branch_budget, support=support)
    return Verdict(decision.verdict,
                   "r1c_v2_nonplanar" if support.kind == CS.NONPLANAR
                   else "r1c_v2_solver",
                   decision.reason, decision=decision), support


def decide_by_census(words, generators=GENERATORS, cap: int = FALLBACK_CAP) -> Verdict:
    census = RN.gamma_N_factorial_n(words, generators, cap_rotations=cap,
                                    keep_accepting=True)
    if census["status"] != "OK":
        return Verdict(UNDECIDED_BUDGET, "none",
                       f"census family {census['expected_cases']} exceeds the per-state "
                       f"cap {cap}", census=census)
    if census["link_components"] != 1:
        return Verdict(CS.UNSUPPORTED, "factorial_census",
                       f"link has {census['link_components']} components; Theorem 2 "
                       "needs a connected link", census=census)
    verdict = CS.SPHERICAL if census["minimum_defect"] == 0 else CS.NOT_SPHERICAL
    return Verdict(verdict, "factorial_census", None, census=census)


def census_family_size(words, generators=GENERATORS):
    try:
        data = RN.build_link_n(words, generators)
    except RN.NeuwirthInputError:
        return None
    return RN.census_size(data, generators)


def audit_spherical(words, verdict: Verdict, generators=GENERATORS,
                    tc_cap: int = 50_000) -> dict:
    """Independent re-verification of a YES plus a Todd-Coxeter triviality attempt."""
    report = {"words": list(words)}
    rotation = None
    if verdict.decision is not None and verdict.decision.witness is not None:
        rotation = verdict.decision.witness.rotation_map()
    elif verdict.census is not None and verdict.census.get("accepting_orders"):
        rotation = verdict.census["accepting_orders"][0]
    if rotation is None:
        report["witness"] = None
        report["witness_error"] = "no rotation system available to verify"
    else:
        report["witness"] = {k: list(v) for k, v in rotation.items()}
        try:
            check = WCN.check_witness_n(words, rotation, generators=generators,
                                        trivial_group=False)
            check["words"] = list(words)
            check["generators"] = list(generators)
            check["germs"] = list(check["germs"])
            report["witness_check"] = check
        except Exception as exc:                       # noqa: BLE001 -- audit surface
            report["witness_error"] = f"{type(exc).__name__}: {exc}"
    census = verdict.census
    if census is None:
        census = RN.gamma_N_factorial_n(words, generators, cap_rotations=FALLBACK_CAP,
                                        keep_accepting=False)
    report["census_status"] = census["status"]
    report["census_minimum_defect"] = census.get("minimum_defect")
    report["census_expected_cases"] = census.get("expected_cases")
    tc = CE.is_trivial_group(words, generators=generators, cap=tc_cap)
    report["todd_coxeter"] = {
        "status": tc["status"], "index": tc["index"], "trivial": tc["trivial"],
        "cosets_defined": tc["cosets_defined"], "cap": tc["cap"],
    }
    return report


def _support_signature(support) -> dict:
    if support.data is None:
        return {"kind": support.kind, "reason": support.reason}
    names = support.germ_names
    out = {
        "kind": support.kind,
        "reason": support.reason,
        "multiplicities": [[f"{names[k[0]]}-{names[k[1]]}", m]
                           for k, m in support.multiplicities],
        "simple_degrees": [list(d) for d in support.simple_degrees],
        "has_loop": support.data.has_loop,
        "link_components": support.data.link_components,
        "degrees": {g: support.data.degree(2 * k)
                    for k, g in enumerate(support.generators)},
    }
    if support.decomposition is not None and support.decomposition.status == "OK":
        profile = CS.decomposition_profile(support.decomposition)
        out["decomposition"] = {
            "blocks": profile["blocks"],
            "nodes": profile["nodes"],
            "p_node_depth": profile["p_node_depth"],
            "cut_vertex_arities": list(profile["cut_vertex_arities"]),
            "scheme_space": profile["scheme_space"],
        }
    return out


# --------------------------------------------------------------------------------------
# the round
# --------------------------------------------------------------------------------------


def run_round(pops: int = POPS_PER_ROOT, roots=ROOTS, output: str = DEFAULT_OUTPUT,
              fallback_cap: int = FALLBACK_CAP,
              fallback_total_budget: int = FALLBACK_TOTAL_BUDGET,
              generators=GENERATORS, verbose: bool = True) -> dict:
    started = time.time()
    searches = []
    states: dict = {}
    for name, root, cap in roots:
        result = harvest_root(name, root, cap, pops=pops, generators=generators)
        searches.append({k: v for k, v in result.items() if k != "states"})
        for key, rec in result["states"].items():
            if key not in states:
                states[key] = rec
        if verbose:
            print(f"[search] {name}: cap {cap}, pops {result['pops']}/"
                  f"{result['pop_budget']}, children {result['children_generated']}, "
                  f"duplicate exact {result['duplicate_exact_children']}, "
                  f"distinct exact {result['distinct_exact_states']}, "
                  f"distinct canonical {result['distinct_states']}, "
                  f"z-boosted {result['z_boosted_children']}, "
                  f"queue left {result['queue_remaining']}")

    keys = sorted(states, key=lambda k: (sum(len(w) for w in k), k))
    if verbose:
        print(f"[search] distinct canonical states across roots: {len(keys)}")

    records: dict = {}
    deferred = []
    t_decide = time.time()
    for index, key in enumerate(keys):
        rec = states[key]
        verdict, support = decide_state(key, generators)
        row = {
            "root": rec.root,
            "canonical": list(key),
            "exact_realization": list(rec.exact),
            "exact_realizations_seen": rec.exact_realizations,
            "depth": rec.depth,
            "discovery_order": rec.order_found,
            "move": rec.move,
            "z_occurrences": z_occurrences(key),
            "total_length_exact": rec.total_length(),
            "total_length_canonical": rec.canonical_length(),
            "support": _support_signature(support),
            "gate": v2_gate(support),
        }
        if verdict.decision is not None:
            row["counters"] = verdict.decision.counters.as_dict()
        if verdict.verdict == CS.UNSUPPORTED:
            gate = row["gate"]
            if gate in ("disconnected link", "germ absent from every relator"):
                # the census is the ground truth but cannot produce a YES here:
                # Theorem 2 of lit_AK3_NEUWIRTH.md needs a connected link, so a census
                # of this family would be enumerated only to be rejected.  Bucket it
                # directly instead of spending the fallback budget on a foregone answer.
                row["verdict"] = CS.UNSUPPORTED
                row["method"] = "r1c_v2_gate"
                row["reason"] = verdict.reason
                records[key] = (row, verdict)
                continue
            size = census_family_size(key, generators)
            row["census_family_size"] = size
            deferred.append((size if size is not None else -1, key, row, verdict))
            continue
        row["verdict"] = verdict.verdict
        row["method"] = verdict.method
        row["reason"] = verdict.reason
        records[key] = (row, verdict)
        if verbose and (index + 1) % 2000 == 0:
            print(f"[decide] {index + 1}/{len(keys)} "
                  f"({round(time.time() - t_decide, 1)}s)")

    deferred.sort(key=lambda t: (t[0] if t[0] >= 0 else 1 << 60, t[1]))
    spent = 0
    for size, key, row, gate_verdict in deferred:
        if size is None or size < 0:
            row["verdict"] = CS.UNSUPPORTED
            row["method"] = "none"
            row["reason"] = gate_verdict.reason or "malformed input"
            records[key] = (row, gate_verdict)
            continue
        if size > fallback_cap or spent + size > fallback_total_budget:
            row["verdict"] = UNDECIDED_BUDGET
            row["method"] = "none"
            row["reason"] = (
                f"R1c-v2 fail-closed ({gate_verdict.reason}); census family {size} "
                + (f"exceeds the per-state cap {fallback_cap}" if size > fallback_cap
                   else f"does not fit the remaining global fallback budget "
                        f"({fallback_total_budget - spent} left)"))
            records[key] = (row, Verdict(UNDECIDED_BUDGET, "none", row["reason"]))
            continue
        verdict = decide_by_census(key, generators, cap=fallback_cap)
        spent += size
        row["verdict"] = verdict.verdict
        row["method"] = verdict.method
        row["reason"] = verdict.reason or gate_verdict.reason
        if verdict.census is not None:
            row["census"] = {
                "status": verdict.census["status"],
                "expected_cases": verdict.census["expected_cases"],
                "enumerated_cases": verdict.census.get("enumerated_cases"),
                "minimum_defect": verdict.census.get("minimum_defect"),
                "minimum_genus": verdict.census.get("minimum_genus"),
                "link_components": verdict.census.get("link_components"),
            }
        records[key] = (row, verdict)

    spherical = []
    for key in keys:
        row, verdict = records[key]
        if verdict.verdict != CS.SPHERICAL:
            continue
        row["SPHERICAL_AUDIT"] = audit_spherical(key, verdict, generators)
        spherical.append((key, row))

    rows = [records[key][0] for key in keys]
    gate_hist: dict = {}
    verdict_hist: dict = {}
    method_hist: dict = {}
    reason_hist: dict = {}
    scheme_spaces = []
    for row in rows:
        gate_hist[row["gate"]] = gate_hist.get(row["gate"], 0) + 1
        verdict_hist[row["verdict"]] = verdict_hist.get(row["verdict"], 0) + 1
        method_hist[row["method"]] = method_hist.get(row["method"], 0) + 1
        if row["verdict"] in (CS.UNSUPPORTED, UNDECIDED_BUDGET):
            reason_hist[row["reason"]] = reason_hist.get(row["reason"], 0) + 1
        counters = row.get("counters")
        if counters and counters.get("scheme_space"):
            scheme_spaces.append(counters["scheme_space"])

    decided = verdict_hist.get(CS.SPHERICAL, 0) + verdict_hist.get(CS.NOT_SPHERICAL, 0)
    undecided = (verdict_hist.get(UNDECIDED_BUDGET, 0)
                 + verdict_hist.get(CS.UNSUPPORTED, 0))
    summary = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "round": 2,
        "solver": "R1c-v2 cut schemes (neuwirth_cut_schemes)",
        "roots": [{"name": n, "state": list(s), "relator_cap": c} for n, s, c in roots],
        "generators": list(generators),
        "pops_per_root": pops,
        "z_bonus": Z_BONUS,
        "searches": [
            {k: (list(v) if isinstance(v, tuple) else v) for k, v in s.items()}
            for s in searches
        ],
        "distinct_states": len(rows),
        "decided": decided,
        "undecided": undecided,
        "gate_histogram": {g: gate_hist[g] for g in V2_GATES if g in gate_hist},
        "verdict_histogram": dict(sorted(verdict_hist.items())),
        "method_histogram": dict(sorted(method_hist.items())),
        "unsupported_reasons": dict(sorted(reason_hist.items(),
                                           key=lambda kv: -kv[1])[:20]),
        "scheme_space_max": max(scheme_spaces, default=0),
        "scheme_space_total": sum(scheme_spaces),
        "fallback_cap": fallback_cap,
        "fallback_total_budget": fallback_total_budget,
        "fallback_spent": spent,
        "spherical_states": [list(k) for k, _ in spherical],
        "elapsed_seconds": round(time.time() - started, 2),
    }

    if output:
        directory = os.path.dirname(output)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(output, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"record": "summary", **summary}) + "\n")
            for row in rows:
                fh.write(json.dumps({"record": "state", **row}) + "\n")
    return {"summary": summary, "rows": rows, "spherical": spherical}


def print_summary(result: dict, output: str = DEFAULT_OUTPUT) -> None:
    s = result["summary"]
    print("=" * 78)
    print("RANK-3 STABLE-MOVE HARVEST, ROUND 2  (R1c-v2 cut schemes)")
    print("=" * 78)
    print(f"generators           : {' '.join(s['generators'])}")
    print(f"pops per root        : {s['pops_per_root']}   z-bonus {s['z_bonus']}")
    for root, search in zip(s["roots"], s["searches"]):
        print(f"root {root['name']:<7}      : {tuple(root['state'])}  "
              f"cap {root['relator_cap']}")
        print(f"    pops {search['pops']}/{search['pop_budget']}   "
              f"children {search['children_generated']}   "
              f"duplicate exact {search['duplicate_exact_children']}   "
              f"distinct exact {search['distinct_exact_states']}   "
              f"distinct canonical {search['distinct_states']}   "
              f"z-boosted {search['z_boosted_children']}   "
              f"max z {search['max_z_occurrences']}   "
              f"queue left {search['queue_remaining']}")
    print(f"distinct states      : {s['distinct_states']}")
    print(f"DECIDED              : {s['decided']}")
    print(f"UNDECIDED            : {s['undecided']}")
    print("R1c-v2 gate          :")
    for gate, count in s["gate_histogram"].items():
        print(f"    {count:6d}  {gate}")
    print(f"verdict histogram    : {s['verdict_histogram']}")
    print(f"decision method      : {s['method_histogram']}")
    print(f"scheme space         : max {s['scheme_space_max']}, "
          f"total {s['scheme_space_total']}")
    print(f"fallback budget      : spent {s['fallback_spent']} of "
          f"{s['fallback_total_budget']} rotation systems "
          f"(per-state cap {s['fallback_cap']})")
    if s["unsupported_reasons"]:
        print("undecided/unsupported reasons (top 12):")
        for reason, count in list(s["unsupported_reasons"].items())[:12]:
            print(f"    {count:6d}  {reason}")
    print(f"elapsed              : {s['elapsed_seconds']}s")
    print(f"output               : {output}")
    if s["spherical_states"]:
        print()
        print("!" * 78)
        print("!!! SPHERICAL RANK-3 STATE(S) FOUND -- gamma_N = 0 IN A STABLE CLASS !!!")
        print("!!! a spherical stable-class member with pi_1 = 1 says the target is  !!!")
        print("!!! STABLY AC-TRIVIAL -- verify and report immediately.               !!!")
        print("!" * 78)
        for key, row in result["spherical"]:
            print(f"  state  : {tuple(key)}")
            print(f"  root   : {row['root']}  depth {row['depth']}  "
                  f"method {row['method']}")
            audit = row.get("SPHERICAL_AUDIT", {})
            check = audit.get("witness_check")
            if check:
                print(f"  witness: defect {check['defect']}, L {check['link_components']}"
                      f", {check['euler_line']}, <AC,BC> orbits "
                      f"{check['ac_bc_orbits']}")
            else:
                print(f"  witness: FAILED -- {audit.get('witness_error')}")
            tc = audit.get("todd_coxeter", {})
            print(f"  pi_1   : Todd-Coxeter {tc.get('status')} index {tc.get('index')} "
                  f"trivial={tc.get('trivial')}")
        print("!" * 78)
    else:
        print()
        print("no SPHERICAL state in this round.")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--pops", type=int, default=POPS_PER_ROOT)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--fallback-cap", type=int, default=FALLBACK_CAP)
    parser.add_argument("--fallback-total-budget", type=int,
                        default=FALLBACK_TOTAL_BUDGET)
    args = parser.parse_args(argv)
    result = run_round(pops=args.pops, output=args.output,
                       fallback_cap=args.fallback_cap,
                       fallback_total_budget=args.fallback_total_budget)
    print_summary(result, output=args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
