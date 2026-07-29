"""Round 1 of the first direct STABLE-move-space search on this line (rank 3).

Everything before this module searched the rank-2 (classical) AC move space.  Here the
two targets are stabilized by one extra generator/relator pair -- the trivial
stabilization ``(r1, r2) -> (r1, r2, z)`` over ``<x, y, z>`` -- and the search then runs
entirely inside rank 3.  A ``gamma_N = 0`` state found here would be a *stably*
thickenable representative of the target's stable class; combined with a
``pi_1 = 1`` certificate and Corollary 3 / Lackenby's Theorem 1.3 that would say the
target is stably AC-trivial.  Nothing of the sort is expected at this budget; the point
of round 1 is to build and calibrate the corridor.

Roots
-----
``AK3  = ("xxxYYYY", "xyxYXY")``  and  ``P25 = ("XYxYXyxYYxyXy", "YXyyXYxyxYYx")``,
each stabilized to ``(r1, r2, "z")`` over the alphabet ``("x", "y", "z")``.

Move set (rank 3, per-relator cap 15)
-------------------------------------
* AC1 concatenation ``r_i <- free_reduce(r_i . r_j^{+-1})`` for every ordered ``i != j``
  (12 moves): free reduction happens only at the seam, since both factors are already
  freely reduced;
* AC3 conjugation ``r_i <- free_reduce(g^{+-1} r_i g^{-+1})`` for ``g`` in ``x, y, z``
  (18 moves).

A move whose rewritten relator would exceed the cap, or would be empty, is dropped (the
same convention as ``ac_words.apply_move``).

De-duplication
--------------
The seen-set is keyed on the CYCLICALLY-REDUCED canonical form -- per-relator lex-min
over rotation x inversion, then the relator multiset sorted -- i.e. the proved symmetry
quotient of ``experiments/lessons/harvest-dedup-on-reduced-forms.md``, extended from two
relators to ``m``.  Exact realizations are kept only as provenance.  Rank-2
specialisation of ``canon_relator``/``canon_state`` reproduces
``ac_words.canon_rel``/``canon_pair`` exactly (asserted in the tests).

Deciding a state
----------------
The canonical (cyclically reduced) form is the tested representative -- cyclic reduction
is AC3 + free reduction, hence class-preserving, and it is what the harvest de-duplicates
on.  Each is routed as:

1. ``neuwirth_rank_n.classify_support_n`` with the explicit alphabet ``("x","y","z")``
   (so a state in which ``z`` has disappeared is caught as a disconnected link, not
   silently re-read as a rank-2 state);
2. support ``3CONN_PLANAR``  -> the R1c polynomial decision procedure;
   support ``NONPLANAR``     -> ``NOT_SPHERICAL`` on the certified non-planarity of S;
3. otherwise the exact factorial census ``gamma_N_factorial_n`` (the ground truth, valid
   for loopy / short / low-degree supports too) whenever its family
   ``prod_g (n_g - 1)!`` fits the per-state cap AND the run's remaining global budget;
   a census with a disconnected link never yields a YES (Theorem 2 needs ``L = 1``) and
   is bucketed ``UNSUPPORTED``;
4. anything still undecided is bucketed and counted separately -- never folded into
   "all NO".

Any SPHERICAL verdict is re-verified immediately by ``witness_check_n`` (an independent
permutation-only verifier) and by the exact census, a Todd-Coxeter triviality attempt is
run over ``("x","y","z")``, and the state is flagged loudly in the summary and in the
JSONL.
"""

from __future__ import annotations

import argparse
import heapq
import json
import os
import time
from dataclasses import dataclass, field

from experiments.stable_ac.fable import coset_enum as CE
from experiments.stable_ac.fable import neuwirth_rank_n as RN
from experiments.stable_ac.fable import witness_check_n as WCN
from experiments.stable_ac.fable.ac_words import (
    free_reduce,
    inverse,
    inverse_letter,
    cyclic_reduce,
)

GENERATORS = ("x", "y", "z")
RELATOR_CAP = 15
POPS_PER_ROOT = 1_000

AK3 = ("xxxYYYY", "xyxYXY")
P25 = ("XYxYXyxYYxyXy", "YXyyXYxyxYYx")

ROOTS = (
    ("AK3+z", tuple(AK3) + ("z",)),
    ("P25+z", tuple(P25) + ("z",)),
)

DEFAULT_OUTPUT = "results/stable_ac/fable/rank3_harvest_round1.jsonl"

# per-state cap on the factorial fallback family, as specified for this round
FALLBACK_CAP = 2_000_000
# global ceiling on the total number of rotation systems the fallback may enumerate in
# one run; states are served smallest-family-first, and whatever is left over is
# reported in its own bucket instead of being guessed.
FALLBACK_TOTAL_BUDGET = 50_000_000

UNDECIDED_BUDGET = "UNDECIDED_BUDGET"


# --------------------------------------------------------------------------------------
# canonical forms (the proved symmetry quotient, at rank n and m relators)
# --------------------------------------------------------------------------------------


def letter_order(generators) -> dict:
    """The solver's ``Y < y < X < x`` ordering, extended to ``n`` generators.

    Generator ``k`` (0-based in the given order) gets ranks ``2(n-1-k)`` for its inverse
    and ``2(n-1-k)+1`` for itself, so at rank 2 over ``("x","y")`` this is exactly
    ``ac_words._ORDER`` = ``{Y: 0, y: 1, X: 2, x: 3}``.
    """
    generators = tuple(generators)
    n = len(generators)
    order = {}
    for k, g in enumerate(generators):
        order[g.upper()] = 2 * (n - 1 - k)
        order[g] = 2 * (n - 1 - k) + 1
    return order


def _key(word: str, order: dict) -> tuple:
    return tuple(order[c] for c in word)


def canon_relator(word: str, order: dict) -> str:
    """Lex-min over every rotation of ``cyclic_reduce(word)`` and of its inverse."""
    word = cyclic_reduce(word)
    if not word:
        return ""
    best = None
    for w in (word, inverse(word)):
        doubled = w + w
        n = len(w)
        for i in range(n):
            cand = doubled[i:i + n]
            k = _key(cand, order)
            if best is None or k < best[0]:
                best = (k, cand)
    return best[1]


def canon_state(words, order: dict) -> tuple:
    """Canonical form: each relator canonicalised, then the multiset sorted."""
    canon = [canon_relator(w, order) for w in words]
    canon.sort(key=lambda w: (len(w), _key(w, order)))
    return tuple(canon)


# --------------------------------------------------------------------------------------
# the rank-3 move generator
# --------------------------------------------------------------------------------------


def moves(state, generators=GENERATORS, cap: int = RELATOR_CAP):
    """Every AC1 concatenation and AC3 conjugation child of ``state``.

    Yields ``(label, child_state)``.  Children equal to the parent, children with an
    empty relator and children breaching the per-relator cap are dropped.
    """
    state = tuple(state)
    n = len(state)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            for sign in (1, -1):
                piece = state[j] if sign == 1 else inverse(state[j])
                new = free_reduce(state[i] + piece)
                if not new or len(new) > cap:
                    continue
                child = state[:i] + (new,) + state[i + 1:]
                if child != state:
                    yield (f"AC1 r{i + 1}<-r{i + 1}.r{j + 1}"
                           f"{'' if sign == 1 else '^-1'}", child)
    for i in range(n):
        for g in generators:
            for c in (g, g.upper()):
                new = free_reduce(c + state[i] + inverse_letter(c))
                if not new or len(new) > cap:
                    continue
                child = state[:i] + (new,) + state[i + 1:]
                if child != state:
                    yield (f"AC3 r{i + 1}<-{c} r{i + 1} {inverse_letter(c)}", child)


# --------------------------------------------------------------------------------------
# best-first harvest
# --------------------------------------------------------------------------------------


@dataclass
class Found:
    root: str
    canonical: tuple
    exact: tuple
    depth: int
    order_found: int
    move: str | None
    parent: tuple | None

    def total_length(self) -> int:
        return sum(len(w) for w in self.exact)

    def canonical_length(self) -> int:
        return sum(len(w) for w in self.canonical)


def harvest_root(root_name: str, root_state, pops: int = POPS_PER_ROOT,
                 generators=GENERATORS, cap: int = RELATOR_CAP) -> dict:
    """Best-first (total length) expansion of one root, de-duped on canonical forms."""
    order = letter_order(generators)
    root_state = tuple(root_state)
    root_key = canon_state(root_state, order)

    found: dict = {}
    found[root_key] = Found(root_name, root_key, root_state, 0, 0, None, None)
    heap = [(sum(len(w) for w in root_state), root_key, 0, root_state, 0)]
    tie = 1
    popped = 0
    generated = 0
    duplicates = 0
    while heap and popped < pops:
        _length, key, _tie, state, depth = heapq.heappop(heap)
        popped += 1
        for label, child in moves(state, generators, cap):
            generated += 1
            child_key = canon_state(child, order)
            if child_key in found:
                duplicates += 1
                continue
            found[child_key] = Found(root_name, child_key, child, depth + 1,
                                     len(found), label, key)
            heapq.heappush(heap, (sum(len(w) for w in child), child_key, tie,
                                  child, depth + 1))
            tie += 1
    return {
        "root": root_name,
        "root_state": root_state,
        "root_key": root_key,
        "pops": popped,
        "pop_budget": pops,
        "queue_remaining": len(heap),
        "queue_exhausted": not heap,
        "children_generated": generated,
        "duplicate_children": duplicates,
        "distinct_states": len(found),
        "states": found,
    }


# --------------------------------------------------------------------------------------
# deciding the harvested states
# --------------------------------------------------------------------------------------


@dataclass
class Verdict:
    verdict: str
    method: str
    support_kind: str
    support_reason: str | None = None
    census: dict | None = None
    decision: object | None = None
    detail: dict = field(default_factory=dict)


def classify_only(words, generators=GENERATORS):
    return RN.classify_support_n(words, generators)


def decide_in_scope(words, support, generators=GENERATORS) -> Verdict:
    """Route a state whose support the R1c theorem covers (or certifies non-planar)."""
    if support.kind == "NONPLANAR":
        return Verdict(RN.NOT_SPHERICAL, "nonplanar_support", support.kind,
                       support.reason)
    decision = RN.solve_spherical_n(words, generators, support=support)
    return Verdict(decision.verdict, "rank_n_solver", support.kind, decision.reason,
                   decision=decision,
                   detail={"counters": decision.counters.as_dict()})


def decide_by_census(words, support, generators=GENERATORS,
                     cap: int = FALLBACK_CAP) -> Verdict:
    """Exact factorial ground truth for an out-of-scope support."""
    census = RN.gamma_N_factorial_n(words, generators, cap_rotations=cap,
                                    keep_accepting=True)
    if census["status"] != "OK":
        return Verdict(RN.UNSUPPORTED, "factorial_census", support.kind,
                       f"census family {census['expected_cases']} exceeds cap {cap}",
                       census=census)
    if census["link_components"] != 1:
        return Verdict(RN.UNSUPPORTED, "factorial_census", support.kind,
                       f"link has {census['link_components']} components; Theorem 2 "
                       "needs a connected link", census=census)
    verdict = RN.SPHERICAL if census["minimum_defect"] == 0 else RN.NOT_SPHERICAL
    return Verdict(verdict, "factorial_census", support.kind, support.reason,
                   census=census)


def census_family_size(words, generators=GENERATORS) -> int | None:
    try:
        data = RN.build_link_n(words, generators)
    except RN.NeuwirthInputError:
        return None
    return RN.census_size(data, generators)


def audit_spherical(words, verdict: Verdict, generators=GENERATORS,
                    tc_cap: int = 50_000) -> dict:
    """Independent re-verification of a YES, plus a Todd-Coxeter triviality attempt."""
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
            report["witness_check"] = WCN.check_witness_n(
                words, rotation, generators=generators, trivial_group=False)
            report["witness_check"]["words"] = list(words)
            report["witness_check"]["generators"] = list(generators)
            report["witness_check"]["germs"] = list(report["witness_check"]["germs"])
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


# --------------------------------------------------------------------------------------
# the round
# --------------------------------------------------------------------------------------


GATE_ORDER = (
    "IN SCOPE (3-connected planar)",
    "certified non-planar S",
    "relator shorter than 3",
    "generator absent from every relator",
    "A-loop",
    "disconnected link",
    "simple degree < 3",
    "2-cut in S (not 3-connected)",
    "planarity undetermined",
    "malformed",
)


def gate_category(words, support) -> str:
    """Which R1c hypothesis first stopped this state (for the round's accounting)."""
    if support.data is None:
        return "malformed"
    if any(len(w) < MIN_RELATOR_LENGTH for w in words):
        return "relator shorter than 3"
    if len(support.data.present_germs) != 2 * len(support.generators):
        return "generator absent from every relator"
    if support.data.has_loop:
        return "A-loop"
    if support.data.link_components != 1:
        return "disconnected link"
    if support.kind == "NONPLANAR":
        return "certified non-planar S"
    if support.kind == "3CONN_PLANAR":
        return "IN SCOPE (3-connected planar)"
    if support.macro is not None and support.macro.status == RN.UNDETERMINED:
        return "planarity undetermined"
    if any(d < 3 for _name, d in support.simple_degrees):
        return "simple degree < 3"
    if support.three_connected is False:
        return "2-cut in S (not 3-connected)"
    return "malformed"


MIN_RELATOR_LENGTH = RN.MIN_RELATOR_LENGTH


def _support_signature(support) -> dict:
    if support.data is None:
        return {"kind": support.kind, "reason": support.reason}
    names = support.germ_names
    return {
        "kind": support.kind,
        "reason": support.reason,
        "germs": list(names),
        "simple_vertices": [names[v] for v in support.vertices],
        "simple_edges": [[names[u], names[v]] for u, v in support.edges],
        "simple_degrees": [list(d) for d in support.simple_degrees],
        "multiplicities": [[f"{names[k[0]]}-{names[k[1]]}", m]
                           for k, m in support.multiplicities],
        "three_connected": support.three_connected,
        "planar": support.planar,
        "has_loop": support.data.has_loop,
        "link_components": support.data.link_components,
        "degrees": {g: support.data.degree(2 * k)
                    for k, g in enumerate(support.generators)},
    }


def run_round(pops: int = POPS_PER_ROOT, roots=ROOTS, output: str = DEFAULT_OUTPUT,
              fallback_cap: int = FALLBACK_CAP,
              fallback_total_budget: int = FALLBACK_TOTAL_BUDGET,
              generators=GENERATORS, verbose: bool = True) -> dict:
    started = time.time()
    searches = []
    states: dict = {}
    for name, root in roots:
        result = harvest_root(name, root, pops=pops, generators=generators)
        searches.append({k: v for k, v in result.items() if k != "states"})
        for key, rec in result["states"].items():
            if key not in states:
                states[key] = rec
        if verbose:
            print(f"[search] {name}: pops {result['pops']}/{result['pop_budget']}, "
                  f"children {result['children_generated']}, "
                  f"duplicates {result['duplicate_children']}, "
                  f"distinct {result['distinct_states']}, "
                  f"queue left {result['queue_remaining']}")

    keys = sorted(states, key=lambda k: (sum(len(w) for w in k), k))
    if verbose:
        print(f"[search] distinct states across roots: {len(keys)}")

    # phase 1: classify + decide everything the theorem covers
    records: dict = {}
    deferred = []
    for key in keys:
        rec = states[key]
        support = classify_only(key, generators)
        row = {
            "root": rec.root,
            "canonical": list(key),
            "exact_realization": list(rec.exact),
            "depth": rec.depth,
            "discovery_order": rec.order_found,
            "move": rec.move,
            "total_length_exact": rec.total_length(),
            "total_length_canonical": rec.canonical_length(),
            "support": _support_signature(support),
            "gate": gate_category(key, support),
        }
        if support.kind in ("3CONN_PLANAR", "NONPLANAR"):
            verdict = decide_in_scope(key, support, generators)
            row["verdict"] = verdict.verdict
            row["method"] = verdict.method
            row["reason"] = verdict.support_reason
            if verdict.decision is not None:
                row["counters"] = verdict.decision.counters.as_dict()
            records[key] = (row, verdict)
        else:
            size = census_family_size(key, generators)
            deferred.append((size if size is not None else -1, key, row, support))

    # phase 2: factorial fallback, smallest family first, under a global work budget
    deferred.sort(key=lambda t: (t[0] if t[0] >= 0 else 1 << 60, t[1]))
    spent = 0
    for size, key, row, support in deferred:
        if size < 0:
            row["verdict"] = RN.UNSUPPORTED
            row["method"] = "none"
            row["reason"] = support.reason or "malformed input"
            records[key] = (row, Verdict(RN.UNSUPPORTED, "none", support.kind,
                                         row["reason"]))
            continue
        row["census_family_size"] = size
        if size > fallback_cap or spent + size > fallback_total_budget:
            row["verdict"] = UNDECIDED_BUDGET
            row["method"] = "none"
            row["reason"] = (f"census family {size} exceeds the per-state cap "
                             f"{fallback_cap}" if size > fallback_cap else
                             f"census family {size} does not fit the remaining global "
                             f"fallback budget ({fallback_total_budget - spent} left)")
            records[key] = (row, Verdict(UNDECIDED_BUDGET, "none", support.kind,
                                         row["reason"]))
            continue
        verdict = decide_by_census(key, support, generators, cap=fallback_cap)
        spent += size
        row["verdict"] = verdict.verdict
        row["method"] = verdict.method
        row["reason"] = verdict.support_reason
        if verdict.census is not None:
            row["census"] = {
                "status": verdict.census["status"],
                "expected_cases": verdict.census["expected_cases"],
                "enumerated_cases": verdict.census.get("enumerated_cases"),
                "minimum_defect": verdict.census.get("minimum_defect"),
                "minimum_genus": verdict.census.get("minimum_genus"),
                "link_components": verdict.census.get("link_components"),
                "defect_histogram": {str(k): v for k, v in
                                     sorted((verdict.census.get("defect_histogram")
                                             or {}).items())},
            }
        records[key] = (row, verdict)

    # phase 3: audit every YES
    spherical = []
    for key in keys:
        row, verdict = records[key]
        if verdict.verdict != RN.SPHERICAL:
            continue
        audit = audit_spherical(key, verdict, generators)
        row["SPHERICAL_AUDIT"] = audit
        spherical.append((key, row))

    rows = [records[key][0] for key in keys]
    support_hist: dict = {}
    gate_hist: dict = {}
    verdict_hist: dict = {}
    method_hist: dict = {}
    reason_hist: dict = {}
    for row in rows:
        support_hist[row["support"]["kind"]] = support_hist.get(
            row["support"]["kind"], 0) + 1
        gate_hist[row["gate"]] = gate_hist.get(row["gate"], 0) + 1
        verdict_hist[row["verdict"]] = verdict_hist.get(row["verdict"], 0) + 1
        method_hist[row["method"]] = method_hist.get(row["method"], 0) + 1
        if row["verdict"] in (RN.UNSUPPORTED, UNDECIDED_BUDGET):
            reason_hist[row["reason"]] = reason_hist.get(row["reason"], 0) + 1

    summary = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "roots": [{"name": n, "state": list(s)} for n, s in roots],
        "generators": list(generators),
        "relator_cap": RELATOR_CAP,
        "pops_per_root": pops,
        "searches": [
            {k: (list(v) if isinstance(v, tuple) else v) for k, v in s.items()}
            for s in searches
        ],
        "distinct_states": len(rows),
        "support_histogram": dict(sorted(support_hist.items())),
        "gate_histogram": {g: gate_hist[g] for g in GATE_ORDER if g in gate_hist},
        "verdict_histogram": dict(sorted(verdict_hist.items())),
        "method_histogram": dict(sorted(method_hist.items())),
        "unsupported_reasons": dict(sorted(reason_hist.items(),
                                           key=lambda kv: -kv[1])),
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
            fh.write(json.dumps({"record": "summary", **summary},
                                sort_keys=False) + "\n")
            for row in rows:
                fh.write(json.dumps({"record": "state", **row},
                                    sort_keys=False) + "\n")
    return {"summary": summary, "rows": rows, "spherical": spherical}


def print_summary(result: dict, output: str = DEFAULT_OUTPUT) -> None:
    s = result["summary"]
    print("=" * 78)
    print("RANK-3 STABLE-MOVE HARVEST, ROUND 1")
    print("=" * 78)
    print(f"generators           : {' '.join(s['generators'])}")
    print(f"relator cap          : {s['relator_cap']}")
    print(f"pops per root        : {s['pops_per_root']}")
    for root, search in zip(s["roots"], s["searches"]):
        print(f"root {root['name']:<7}      : {tuple(root['state'])}")
        print(f"    pops {search['pops']}/{search['pop_budget']}   "
              f"children {search['children_generated']}   "
              f"duplicate children {search['duplicate_children']}   "
              f"distinct {search['distinct_states']}   "
              f"queue left {search['queue_remaining']}")
    print(f"distinct states      : {s['distinct_states']}")
    print(f"support histogram    : {s['support_histogram']}")
    print("R1c hypothesis gate  :")
    for gate, count in s["gate_histogram"].items():
        print(f"    {count:6d}  {gate}")
    print(f"verdict histogram    : {s['verdict_histogram']}")
    print(f"decision method      : {s['method_histogram']}")
    print(f"fallback budget      : spent {s['fallback_spent']} of "
          f"{s['fallback_total_budget']} rotation systems "
          f"(per-state cap {s['fallback_cap']})")
    print("undecided/unsupported reasons (top 12):")
    for reason, count in list(s["unsupported_reasons"].items())[:12]:
        print(f"    {count:6d}  {reason}")
    print(f"elapsed              : {s['elapsed_seconds']}s")
    print(f"output               : {output}")
    if s["spherical_states"]:
        print()
        print("!" * 78)
        print("!!! SPHERICAL RANK-3 STATE(S) FOUND -- gamma_N = 0 IN A STABLE CLASS !!!")
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
        print("no SPHERICAL state in this round (expected at this budget).")


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
