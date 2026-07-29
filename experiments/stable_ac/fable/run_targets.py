"""Run the fable Neuwirth stack on the R1 targets and write the results row file.

What ``main()`` does, in order:

1. **Re-derives the 53-move AC path** from ``P25`` with the twelve ``h`` moves of
   ``app/ac_paths.tex`` at relator cap 15, asserting (a) the endpoint is exactly
   AK(3) ``("xxxYYYY", "xyxYXY")``, (b) the 54 states are byte-identical to
   ``results/stable_ac/theory/fable/p25_path_states.json``, (c) the published
   ``(move, total_length)`` trace of the commented block in ``ac_paths.tex``, and
   (d) every transition is one of the twelve recomputed children of its predecessor.
2. **Evaluates gamma_N** with the rank solver on ``P25``, on ``Q``, and on every one of
   the 54 path states, in both the exact and the cyclically reduced realization,
   recording which states are not cyclically reduced (their exact realizations carry
   ``A``-loops, hence ``UNSUPPORTED``, never ``NO``).
3. **Certifies pi_1 = 1** by independent Todd-Coxeter on ``P25``, ``Q``, AK(3) and five
   deterministically sampled intermediates.
4. **De-duplicates** the path states against the 1,000-state height-17 component census
   using the canonical form that census stores.
5. Writes ``results/stable_ac/fable/gamma_n_targets.jsonl`` and prints a summary.

``--quick`` skips the factorial cross-checks (step 2 keeps the rank verdicts).
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from experiments.stable_ac.fable import ac_words as W
from experiments.stable_ac.fable import coset_enum as CE
from experiments.stable_ac.fable import neuwirth_core as NC
from experiments.stable_ac.fable import neuwirth_rank as NR
from experiments.stable_ac.fable import witness_check as WC

P25 = ("XYxYXyxYYxyXy", "YXyyXYxyxYYx")
AK3 = ("xxxYYYY", "xyxYXY")
Q = ("xxxxyXXYxyXXY", "YxxyXXYxxyXXYxxyXXY")

PATH_MOVES = (
    9, 7, 4, 8, 11, 5, 11, 9, 3, 10, 12, 7, 7, 9, 11, 5, 3, 5, 4, 3, 12, 5, 7,
    7, 1, 9, 11, 8, 3, 5, 10, 2, 6, 12, 9, 7, 5, 11, 10, 3, 8, 11, 9, 2, 10,
    12, 5, 7, 9, 11, 1, 9, 8,
)

# The commented (move, total_length) checksum block of app/ac_paths.tex.
PUBLISHED_TRACE = (
    (9, 25), (7, 25), (4, 17), (8, 17), (11, 17), (5, 17), (11, 17), (9, 17),
    (3, 16), (10, 16), (12, 16), (7, 16), (7, 16), (9, 16), (11, 16), (5, 16),
    (3, 15), (5, 15), (4, 19), (3, 14), (12, 14), (5, 14), (7, 16), (7, 18),
    (1, 19), (9, 19), (11, 19), (8, 19), (3, 18), (5, 18), (10, 18), (2, 15),
    (6, 15), (12, 15), (9, 15), (7, 15), (5, 15), (11, 15), (10, 15), (3, 15),
    (8, 15), (11, 15), (9, 15), (2, 16), (10, 16), (12, 16), (5, 16), (7, 16),
    (9, 16), (11, 16), (1, 13), (9, 13), (8, 13),
)

PATH_CAP = 15
EXPECTED_NON_CYCLIC_INDICES = (23, 24)

DEFAULT_FIXTURE = "results/stable_ac/theory/fable/p25_path_states.json"
DEFAULT_OUTPUT = "results/stable_ac/fable/gamma_n_targets.jsonl"
DEFAULT_COMPONENT_JSON = (
    "/tmp/claude-0/-home-user-ACSolverX/cff13624-d3f2-4044-bd4f-d64680bb928b/"
    "scratchpad/codex_solver/ak3_component_thickenability.json"
)
# The factorial family has prod_g (n_{g+} - 1)! members and this enumerator runs at
# roughly 1.7e5 rotation systems per second, so anything past ~1e6 turns a routine run
# into minutes.  Instances above the cap are recorded as UNKNOWN_SIZE, never guessed;
# raise --factorial-cap to widen the cross-check.
DEFAULT_FACTORIAL_CAP = 1_000_000


def repo_root() -> str:
    return os.path.dirname(  # .../ACSolverX
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )


# --------------------------------------------------------------------------------------
# step 1: path re-derivation
# --------------------------------------------------------------------------------------


def derive_path(fixture_path: str | None = None) -> dict:
    """Replay the 53 moves and assert every published checksum."""
    states = [P25] + W.replay(P25, PATH_MOVES, PATH_CAP)
    trace = tuple(W.replay_trace(P25, PATH_MOVES, PATH_CAP))

    assert len(PATH_MOVES) == 53, len(PATH_MOVES)
    assert len(states) == 54, len(states)
    assert states[-1] == AK3, f"endpoint {states[-1]} != {AK3}"
    assert trace == PUBLISHED_TRACE, "published (move, total_length) trace mismatch"

    for i, (prev, nxt) in enumerate(zip(states, states[1:])):
        kids = W.children(prev, PATH_CAP)
        assert nxt in kids, f"transition {i} -> {i + 1} is not among the 12 children"

    blob = json.dumps(
        {
            "path": [list(s) for s in states],
            "unique": [list(s) for s in sorted(set(states))],
        },
        indent=0,
    )
    fixture_match = None
    if fixture_path and os.path.exists(fixture_path):
        with open(fixture_path, encoding="utf-8") as fh:
            raw = fh.read()
        fixture_match = raw == blob
        assert fixture_match, "regenerated path states are not byte-identical to the fixture"

    non_cyclic = tuple(
        i for i, s in enumerate(states)
        if not all(W.is_cyclically_reduced(w) for w in s)
    )
    assert non_cyclic == EXPECTED_NON_CYCLIC_INDICES, non_cyclic
    return {
        "states": states,
        "trace": trace,
        "fixture_byte_identical": fixture_match,
        "non_cyclically_reduced_indices": non_cyclic,
        "endpoint": states[-1],
    }


# --------------------------------------------------------------------------------------
# step 2: gamma_N
# --------------------------------------------------------------------------------------


def _class_name(key) -> str:
    return f"{NC.GERM_NAMES[key[0]]}~{NC.GERM_NAMES[key[1]]}"


def _support_payload(support) -> dict:
    return {
        "kind": support.kind,
        "multiplicities": {_class_name(k): m for k, m in support.multiplicities},
        "missing_class": _class_name(support.missing_key) if support.missing_key else None,
        "poles": [NC.GERM_NAMES[v] for v in support.poles] if support.poles else None,
        "reason": support.reason,
    }


def evaluate(words, factorial_cap: int | None) -> dict:
    """Rank verdict (+ witness check, + factorial cross-check when affordable)."""
    words = tuple(words)
    decision = NR.solve_spherical(words)
    row = {
        "words": list(words),
        "total_length": sum(len(w) for w in words),
        "support": _support_payload(decision.support),
        "verdict": decision.verdict,
        "reason": decision.reason,
        "counters": decision.counters.as_dict(),
        "witness": None,
        "witness_check": None,
        "factorial": None,
    }
    if decision.witness is not None:
        row["witness"] = {
            "scheme": decision.witness.scheme,
            "cut": decision.witness.cut,
            "phases": list(decision.witness.phases),
            "ranks": list(decision.witness.ranks),
            "rotations": {name: list(darts) for name, darts in decision.witness.rotations},
            "cycles_C": decision.witness.cycles_C,
            "cycles_A": decision.witness.cycles_A,
            "cycles_AC": decision.witness.cycles_AC,
            "euler_characteristic": decision.witness.euler_characteristic,
            "defect": decision.witness.defect,
            "genus": decision.witness.genus,
        }
        report = WC.check_rank_witness(decision)
        report["words"] = list(report["words"])
        row["witness_check"] = report
    if factorial_cap is not None:
        census = NC.gamma_N_factorial(words, cap_rotations=factorial_cap,
                                      keep_accepting=False)
        row["factorial"] = {
            "status": census["status"],
            "expected_cases": census["expected_cases"],
            "enumerated_cases": census["enumerated_cases"],
            "defect_histogram": {str(k): v for k, v in sorted(census["defect_histogram"].items())},
            "minimum_defect": census["minimum_defect"],
            "minimum_genus": census["minimum_genus"],
            "link_components": census["link_components"],
        }
        if census["status"] == "OK" and decision.verdict != NR.UNSUPPORTED:
            agree = (census["minimum_defect"] == 0) == (decision.verdict == NR.SPHERICAL)
            row["factorial"]["agrees_with_rank"] = agree
            assert agree, (
                f"rank/factorial disagreement on {words}: rank={decision.verdict}, "
                f"factorial minimum defect={census['minimum_defect']}"
            )
    return row


# --------------------------------------------------------------------------------------
# step 4: de-duplication against the component census
# --------------------------------------------------------------------------------------


def load_component_states(path: str):
    if not path or not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        blob = json.load(fh)
    return {tuple(state["words"]) for state in blob["states"]}


# --------------------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------------------


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--quick", action="store_true",
                        help="skip the factorial cross-checks")
    parser.add_argument("--output", default=None)
    parser.add_argument("--fixture", default=None)
    parser.add_argument("--component-json", default=DEFAULT_COMPONENT_JSON)
    parser.add_argument("--factorial-cap", type=int, default=DEFAULT_FACTORIAL_CAP)
    parser.add_argument("--coset-cap", type=int, default=200_000)
    args = parser.parse_args(argv)

    root = repo_root()
    fixture = args.fixture or os.path.join(root, DEFAULT_FIXTURE)
    output = args.output or os.path.join(root, DEFAULT_OUTPUT)
    factorial_cap = None if args.quick else args.factorial_cap

    path = derive_path(fixture)
    states = path["states"]

    rows = []

    p25_row = evaluate(P25, factorial_cap)
    p25_row.update({"target": "P25", "role": "exact", "path_index": 0})
    rows.append(p25_row)

    q_row = evaluate(Q, factorial_cap)
    q_row.update({"target": "Q", "role": "exact", "path_index": None})
    rows.append(q_row)

    path_rows = []
    for i, state in enumerate(states):
        reduced = tuple(W.cyclic_reduce(w) for w in state)
        exact_row = evaluate(state, factorial_cap)
        exact_row.update({"target": f"path[{i}]", "role": "exact", "path_index": i,
                          "cyclically_reduced_input": reduced == state})
        rows.append(exact_row)
        path_rows.append(exact_row)
        if reduced != state:
            red_row = evaluate(reduced, factorial_cap)
            red_row.update({"target": f"path[{i}]", "role": "cyclically_reduced",
                            "path_index": i, "cyclically_reduced_input": True,
                            "exact_words": list(state)})
            rows.append(red_row)
            path_rows.append(red_row)

    # the two non-cyclically-reduced states: exact form must be UNSUPPORTED (A-loops)
    non_cyclic_report = {}
    for i in path["non_cyclically_reduced_indices"]:
        exact = states[i]
        reduced = tuple(W.cyclic_reduce(w) for w in exact)
        link = NC.build_link(exact)
        exact_decision = NR.solve_spherical(exact)
        reduced_decision = NR.solve_spherical(reduced)
        assert link.has_loop, f"state {i} was expected to carry A-loops"
        assert exact_decision.verdict == NR.UNSUPPORTED, exact_decision.verdict
        assert reduced_decision.verdict in (NR.SPHERICAL, NR.NOT_SPHERICAL), \
            reduced_decision.verdict
        non_cyclic_report[i] = {
            "exact_words": list(exact),
            "reduced_words": list(reduced),
            "a_loops": len(link.loop_edges),
            "exact_verdict": exact_decision.verdict,
            "exact_reason": exact_decision.reason,
            "reduced_verdict": reduced_decision.verdict,
        }

    # step 3: Todd-Coxeter
    SAMPLED_INTERMEDIATES = (7, 17, 27, 37, 47)
    assert len(SAMPLED_INTERMEDIATES) == 5
    tc_targets = [("P25", P25), ("Q", Q), ("AK3", AK3)]
    tc_targets += [(f"path[{i}]", states[i]) for i in SAMPLED_INTERMEDIATES]
    tc_results = {}
    for name, words in tc_targets:
        result = CE.is_trivial_group(words, cap=args.coset_cap)
        tc_results[name] = {
            "words": list(words),
            "status": result["status"],
            "index": result["index"],
            "cosets_defined": result["cosets_defined"],
            "trivial": result["trivial"],
        }
        assert result["trivial"] is True, f"{name} did not enumerate to index 1"

    for row in rows:
        key = row["target"]
        if key in tc_results and row["role"] == "exact":
            row["todd_coxeter"] = tc_results[key]
        else:
            row.setdefault("todd_coxeter", None)

    # step 4: de-duplication
    component = load_component_states(args.component_json)
    dedup = {"source": args.component_json, "available": component is not None}
    if component is not None:
        canon = [W.canon_pair(*s) for s in states]
        seen = [c in component for c in canon]
        dedup.update({
            "component_states": len(component),
            "path_states": len(states),
            "distinct_canonical_path_states": len(set(canon)),
            "duplicated": sum(1 for c in set(canon) if c in component),
            "novel": sum(1 for c in set(canon) if c not in component),
            "novel_states": sorted(c for c in set(canon) if c not in component),
            # only a novel state inside the census ceiling (height-17 component,
            # total length <= 17) is evidence of anything the census could have held
            "novel_within_census_ceiling": sorted(
                c for c in set(canon)
                if c not in component and len(c[0]) + len(c[1]) <= 17
            ),
        })
        by_index = {}
        for i, (c, hit) in enumerate(zip(canon, seen)):
            by_index[i] = {"canonical": list(c), "in_component_census": hit}
        for row in rows:
            if row["target"].startswith("path[") and row["role"] == "exact":
                row["dedup"] = by_index[row["path_index"]]
    for row in rows:
        row.setdefault("dedup", None)

    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, sort_keys=True) + "\n")

    verdict_counts = {}
    for row in rows:
        verdict_counts[row["verdict"]] = verdict_counts.get(row["verdict"], 0) + 1
    path_exact = [r for r in rows if r["role"] == "exact" and r["target"].startswith("path[")]
    path_reduced = [r for r in rows if r["role"] == "cyclically_reduced"]

    summary = {
        "path": {
            "moves": len(PATH_MOVES),
            "states": len(states),
            "endpoint": list(path["endpoint"]),
            "endpoint_is_AK3": path["endpoint"] == AK3,
            "published_trace_match": True,
            "fixture_byte_identical": path["fixture_byte_identical"],
            "non_cyclically_reduced_indices": list(path["non_cyclically_reduced_indices"]),
            "non_cyclically_reduced_detail": non_cyclic_report,
        },
        "rows_written": len(rows),
        "output": output,
        "quick": args.quick,
        "verdict_counts": verdict_counts,
        "targets": {
            "P25": {"support": p25_row["support"]["kind"], "verdict": p25_row["verdict"]},
            "Q": {"support": q_row["support"]["kind"], "verdict": q_row["verdict"]},
        },
        "path_exact_verdicts": _tally(path_exact),
        "path_reduced_verdicts": _tally(path_reduced),
        "todd_coxeter": tc_results,
        "dedup": dedup,
        "spherical_targets": [r["target"] for r in rows if r["verdict"] == NR.SPHERICAL],
    }

    print(json.dumps(summary, indent=2, sort_keys=True))
    print()
    print("verdict table")
    print(f"{'target':<12} {'role':<20} {'support':<12} {'verdict':<16} total_len")
    for row in [p25_row, q_row] + path_rows:
        print(f"{row['target']:<12} {row['role']:<20} {row['support']['kind']:<12} "
              f"{row['verdict']:<16} {row['total_length']}")
    return 0


def _tally(rows) -> dict:
    out = {}
    for row in rows:
        out[row["verdict"]] = out.get(row["verdict"], 0) + 1
    return out


if __name__ == "__main__":
    sys.exit(main())
