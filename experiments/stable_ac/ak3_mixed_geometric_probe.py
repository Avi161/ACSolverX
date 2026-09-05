"""Bounded reproducible mixed-AC probe of exact cyclic presentation complexes."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import random

from experiments.stable_ac.thickenable.ak3_aut_frontier_manifest import free_reduce, formal_inverse
from experiments.stable_ac.thickenable.neuwirth_rank_solver import classify_support, solve_spherical

SOURCE = ("xxxYYYY", "xyxYXY")
SEED = 20260905
MAX_ATTEMPTS = 1000
MAX_SOLVER_CALLS = 64
MAX_FREE_LENGTH = 32
RESTART_INTERVAL = 32
MIN_CYCLIC_LENGTH = 18
OPERATIONS = (
    (("invert", 0), ("invert", 1), ("swap",))
    + tuple(("multiply", row, sign) for row in (0, 1) for sign in (1, -1))
    + tuple(("conjugate", row, letter) for row in (0, 1) for letter in "xXyY")
)


def apply_move(pair, operation):
    rows = list(pair)
    kind = operation[0]
    if kind == "swap":
        rows.reverse()
    elif kind == "invert":
        rows[operation[1]] = formal_inverse(rows[operation[1]])
    elif kind == "multiply":
        _, recipient, sign = operation
        donor = rows[1 - recipient]
        rows[recipient] += donor if sign == 1 else formal_inverse(donor)
    else:
        _, recipient, letter = operation
        rows[recipient] = letter + rows[recipient] + formal_inverse(letter)
    return tuple(free_reduce(row) for row in rows)


def peel_row(word):
    prefix, core = "", word
    while len(core) > 1 and core[0] == core[-1].swapcase():
        prefix += core[0]
        core = core[1:-1]
    if free_reduce(prefix + core + formal_inverse(prefix)) != word:
        raise AssertionError("the cyclic peel failed its literal reconstruction")
    return core, prefix


def cyclic_pair_key(cores):
    return tuple(sorted(min(oriented[index:] + oriented[:index]
                            for oriented in (core, formal_inverse(core))
                            for index in range(len(core))) for core in cores))


def run_probe(output: Path):
    rng = random.Random(SEED)
    counts = dict(attempted_moves=0, accepted_moves=0, rejected_moves=0,
                  restarts=0, below_length=0, duplicates=0, unsupported=0,
                  solver_calls=0, completed_solver_calls=0)
    artifact = {
        "schema": "acsolverx.ak3.mixed-geometric-probe.v1",
        "source": SOURCE,
        "config": {"seed": SEED, "max_attempts": MAX_ATTEMPTS,
                   "max_solver_calls": MAX_SOLVER_CALLS, "max_free_length": MAX_FREE_LENGTH,
                   "restart_interval": RESTART_INTERVAL, "min_cyclic_length": MIN_CYCLIC_LENGTH,
                   "operations": OPERATIONS},
        "summary": counts,
        "status": "running",
        "controls": [],
        "candidates": [],
        "positive_found": False,
        "attempt_budget_reached": False,
        "solver_budget_reached": False,
        "ac_obstruction_claimed": False,
        "positive_validation_required": "independent neighborhood and 3-ball validation before any thickenability or AK3 claim",
    }
    output.parent.mkdir(parents=True, exist_ok=True)

    def checkpoint():
        output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    checkpoint()
    for words, expected in ((("X", "XYXy"), True), (SOURCE, False)):
        control = {"words": words, "expected_spherical": expected, "status": "PENDING"}
        artifact["controls"].append(control)
        checkpoint()
        decision = solve_spherical(words)
        control.update(status="PASSED" if decision.spherical is expected else "FAILED",
                       spherical=decision.spherical, verdict=decision.verdict, support=decision.support.kind)
        if decision.spherical is not expected:
            artifact["status"] = "CONTROL_FAILED"
            checkpoint()
            raise AssertionError("the pinned spherical solver control failed")
        checkpoint()
    pair, trail, seen = SOURCE, [], set()
    for attempt in range(MAX_ATTEMPTS):
        if counts["solver_calls"] >= MAX_SOLVER_CALLS:
            break
        if attempt % RESTART_INTERVAL == 0:
            pair, trail = SOURCE, []
            counts["restarts"] += 1
        counts["attempted_moves"] += 1
        operation = rng.choice(OPERATIONS)
        proposed = apply_move(pair, operation)
        if any(not row for row in proposed) or sum(map(len, proposed)) > MAX_FREE_LENGTH:
            counts["rejected_moves"] += 1
            continue
        pair = proposed
        counts["accepted_moves"] += 1
        trail.append({"attempt": attempt + 1, "operation": operation, "resulting_pair": pair})
        peeled = tuple(peel_row(row) for row in pair)
        cores = tuple(core for core, _ in peeled)
        prefixes = tuple(prefix for _, prefix in peeled)
        if sum(map(len, cores)) < MIN_CYCLIC_LENGTH:
            counts["below_length"] += 1
            continue
        key = cyclic_pair_key(cores)
        if key in seen:
            counts["duplicates"] += 1
            continue
        seen.add(key)
        support = classify_support(cores)
        candidate = {
            "attempt": attempt + 1,
            "freely_reduced_pair": pair,
            "cores": cores,
            "from_root_trail": list(trail),
            "peel_prefixes": prefixes,
            "final_conjugators": tuple(formal_inverse(prefix) for prefix in prefixes),
            "decision": {"verdict": "PENDING", "spherical": None, "support": support.kind},
        }
        artifact["candidates"].append(candidate)
        if support.kind not in ("K4", "K4-e", "C4"):
            counts["unsupported"] += 1
            candidate["decision"].update(verdict="SKIPPED_UNSUPPORTED", reason=support.reason)
            checkpoint()
            continue
        counts["solver_calls"] += 1
        checkpoint()
        decision = solve_spherical(cores)
        counts["completed_solver_calls"] += 1
        candidate["decision"] = {
            "verdict": decision.verdict, "spherical": decision.spherical,
            "support": decision.support.kind, "reason": decision.reason,
            "counters": asdict(decision.counters),
        }
        if decision.spherical:
            if decision.witness is None:
                raise AssertionError("a spherical decision lacks its witness")
            candidate["witness"] = asdict(decision.witness)
            candidate["status"] = "QUARANTINED_SPHERICAL"
            artifact["positive_found"] = True
        checkpoint()
        if artifact["positive_found"]:
            break
    artifact["attempt_budget_reached"] = counts["attempted_moves"] >= MAX_ATTEMPTS
    artifact["solver_budget_reached"] = counts["solver_calls"] >= MAX_SOLVER_CALLS
    artifact["status"] = "QUARANTINED_SPHERICAL" if artifact["positive_found"] else "bounded_probe_completed"
    checkpoint()
    return {**counts, "status": artifact["status"], "positive_found": artifact["positive_found"],
            "attempt_budget_reached": artifact["attempt_budget_reached"],
            "solver_budget_reached": artifact["solver_budget_reached"], "output": str(output)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    print(json.dumps(run_probe(arguments.output), sort_keys=True))


if __name__ == "__main__":
    main()
