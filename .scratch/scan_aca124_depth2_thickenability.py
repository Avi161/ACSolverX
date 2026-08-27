#!/usr/bin/env python3
"""Reconstruct and exactly scan every stored aca124 depth-2 mu state."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import multiprocessing as mp
import sys
from collections import Counter
from dataclasses import asdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROOF_ROOT = ROOT / ".claude/worktrees/codex-proofs"
sys.path[:0] = [str(ROOT / ".scratch"), str(PROOF_ROOT)]

from experiments.stable_ac.cov.mu_descent_scan import hop_outputs, orbit  # noqa: E402
from experiments.stable_ac.thickenable.neuwirth_one_loop_solver import (  # noqa: E402
    classify_one_loop_support,
)
from experiments.stable_ac.thickenable.neuwirth_p4_solver import (  # noqa: E402
    classify_four_germ_support,
    solve_four_germ_spherical,
)
from experiments.stable_ac.thickenable.neuwirth_paw_one_loop_solver import (  # noqa: E402
    classify_paw_one_loop_support,
    solve_paw_one_loop_spherical,
)
from experiments.stable_ac.thickenable.neuwirth_rank_solver import (  # noqa: E402
    G_X_POS,
    G_Y_POS,
    GERMS,
    classify_support,
    solve_spherical,
)
from fast_one_loop import solve_one_loop_spherical_fast  # noqa: E402


SCHEMA = "aca124-depth2-supported-neuwirth-v1"
DATA = PROOF_ROOT / "data/ms_unsolved_reps/aca_124.csv"
SUMMARY = (
    PROOF_ROOT
    / "results/stable_ac/mu_scan/mu_scan_aca124_d2_k10_mrl24.jsonl"
)
MU_SCAN = PROOF_ROOT / "experiments/stable_ac/cov/mu_descent_scan.py"
COV = PROOF_ROOT / "experiments/stable_ac/cov/cov.py"
SOLVER_FILES = {
    "base_solver": PROOF_ROOT / "experiments/stable_ac/thickenable/neuwirth_rank_solver.py",
    "p4_solver": PROOF_ROOT / "experiments/stable_ac/thickenable/neuwirth_p4_solver.py",
    "one_loop_solver": PROOF_ROOT / "experiments/stable_ac/thickenable/neuwirth_one_loop_solver.py",
    "paw_loop_solver": PROOF_ROOT / "experiments/stable_ac/thickenable/neuwirth_paw_one_loop_solver.py",
    "fast_one_loop_engine": ROOT / ".scratch/fast_one_loop.py",
}
DEFAULT_OUT = ROOT / ".scratch/aca124_depth2_neuwirth_scan.json"
DEFAULT_CHECKPOINT = ROOT / ".scratch/aca124_depth2_neuwirth_scan.records.jsonl"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reconstruct(cap: int = 24, keep: int = 10):
    expected = {
        row["pres_id"]: row
        for row in map(json.loads, SUMMARY.read_text().splitlines())
    }
    states = []
    for source in csv.DictReader(DATA.open()):
        pres_id = source["name"]
        source_pair = (source["r1"], source["r2"])
        _, source_rep = orbit(source_pair)
        first = hop_outputs(*source_pair, cap)
        first_paths = {}
        for rep1, (mu1, pair1, z1) in first.items():
            first_paths[rep1] = {
                "pres_id": pres_id,
                "source_words": list(source_pair),
                "hops": 1,
                "z_path": [z1],
                "via_words": None,
                "words": list(pair1),
                "orbit_rep": list(rep1),
                "mu": mu1,
            }
        states.extend(first_paths.values())

        seen = set(first)
        kept = sorted(first.items(), key=lambda item: item[1][0])[:keep]
        second_count = len(seen)
        for rep1, (_, pair1, z1) in kept:
            for rep2, (mu2, pair2, z2) in hop_outputs(*pair1, cap).items():
                if rep2 == source_rep or rep2 in seen:
                    continue
                seen.add(rep2)
                second_count += 1
                states.append({
                    "pres_id": pres_id,
                    "source_words": list(source_pair),
                    "hops": 2,
                    "z_path": [z1, z2],
                    "via_words": list(pair1),
                    "words": list(pair2),
                    "orbit_rep": list(rep2),
                    "mu": mu2,
                })
        row = expected[pres_id]
        if len(first) != row["n_orbits1"] or second_count != row["n_orbits2"]:
            raise AssertionError(
                f"{pres_id}: reconstructed {len(first)}/{second_count}, "
                f"stored {row['n_orbits1']}/{row['n_orbits2']}"
            )
    if len(states) != sum(row["n_orbits2"] for row in expected.values()):
        raise AssertionError("unexpected aggregate reconstructed state count")
    for index, state in enumerate(states):
        state["state_index"] = index
    return states


def cost(state):
    index = state["state_index"]
    words = tuple(state["words"])
    length = sum(map(len, words))
    support = classify_support(words)
    if support.kind != "UNSUPPORTED":
        return 0, length, index
    support = classify_four_germ_support(words)
    if support.kind != "UNSUPPORTED":
        return 1, length, index
    support = classify_one_loop_support(words)
    if support.kind != "UNSUPPORTED":
        data = support.data
        loop_vertex = support.loop_class[0]
        core_degree = len(data.vertex_darts[loop_vertex]) - 2
        if support.kind == "K4+1loop":
            schemes = 2 * core_degree
        else:
            c, d = support.missing_edge
            poles = tuple(vertex for vertex in GERMS if vertex not in (c, d))
            central = tuple(sorted(poles))
            schemes = 2 * core_degree * (len(data.class_edges[central]) + 1)
        phases = len(data.vertex_darts[G_X_POS]) * len(data.vertex_darts[G_Y_POS])
        return 2, schemes * phases, index
    support = classify_paw_one_loop_support(words)
    if support.kind != "UNSUPPORTED":
        return 3, length, index
    return -1, length, index


def decide(state):
    words = tuple(state["words"])
    decision = solve_spherical(words)
    solver = "base"
    if decision.spherical is None:
        decision = solve_four_germ_spherical(words)
        solver = "p4"
    if decision.spherical is None:
        decision = solve_one_loop_spherical_fast(words)
        solver = "one_loop"
    if decision.spherical is None:
        decision = solve_paw_one_loop_spherical(words)
        solver = "paw_one_loop"
    if decision.spherical is None:
        verdict = "UNSUPPORTED"
    elif decision.spherical:
        verdict = "SPHERICAL_REQUIRES_INDEPENDENT_VALIDATION"
    else:
        verdict = "NOT_SPHERICAL"
    if decision.spherical is False and not decision.counters.exhaustive:
        raise AssertionError(f"non-exhaustive negative state {state['state_index']}")
    if decision.spherical is True and decision.witness is None:
        raise AssertionError(f"positive without witness state {state['state_index']}")
    return {
        "checkpoint_schema": SCHEMA,
        "state": state,
        "solver": solver,
        "support": decision.support.kind,
        "simple_edges": [list(edge) for edge in sorted(decision.support.simple_edges)],
        "verdict": verdict,
        "reason": decision.reason,
        "counters": json.loads(json.dumps(asdict(decision.counters))),
        "witness": (
            json.loads(json.dumps(asdict(decision.witness)))
            if decision.witness is not None
            else None
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=max(1, mp.cpu_count() - 1))
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    args = parser.parse_args()

    states = reconstruct()
    done = {}
    if args.checkpoint.exists():
        for line in args.checkpoint.read_text().splitlines():
            record = json.loads(line)
            if record.get("checkpoint_schema") != SCHEMA:
                raise AssertionError("checkpoint schema mismatch")
            done[record["state"]["state_index"]] = record
    pending = [state for state in states if state["state_index"] not in done]
    pending.sort(key=cost)
    print(
        f"reconstructed {len(states)} exact states; {len(pending)} pending",
        flush=True,
    )
    args.checkpoint.parent.mkdir(parents=True, exist_ok=True)
    with args.checkpoint.open("a") as output:
        if args.workers == 1:
            iterator = map(decide, pending)
            pool = None
        else:
            pool = mp.Pool(args.workers)
            iterator = pool.imap_unordered(decide, pending, chunksize=1)
        try:
            for count, record in enumerate(iterator, 1):
                done[record["state"]["state_index"]] = record
                output.write(json.dumps(record, sort_keys=True) + "\n")
                if count % 50 == 0:
                    output.flush()
                    print(f"  {count}/{len(pending)}", flush=True)
        finally:
            if pool is not None:
                pool.close()
                pool.join()

    records = [done[index] for index in range(len(states))]
    verdicts = Counter(record["verdict"] for record in records)
    supports = Counter(record["support"] for record in records)
    positives = [r for r in records if r["verdict"].startswith("SPHERICAL")]
    unsupported = [r for r in records if r["verdict"] == "UNSUPPORTED"]
    source_hashes = {
        "aca124": sha256(DATA),
        "stored_summary": sha256(SUMMARY),
        "mu_scan": sha256(MU_SCAN),
        "cov": sha256(COV),
        "driver": sha256(Path(__file__)),
        **{name: sha256(path) for name, path in SOLVER_FILES.items()},
    }
    certificate = {
        "schema": SCHEMA,
        "scope": (
            "Exact reconstruction of every orbit-moving state counted by "
            "the stored aca124 depth-2 cap-24 keep-10 mu scan: all hop-1 "
            "orbits and every new hop-2 orbit from the ten lowest-mu hop-1 states."
        ),
        "source_hashes": source_hashes,
        "state_count": len(states),
        "hop_counts": dict(sorted(Counter(s["hops"] for s in states).items())),
        "source_class_count": len({s["pres_id"] for s in states}),
        "verdict_counts": dict(sorted(verdicts.items())),
        "support_counts": dict(sorted(supports.items())),
        "positive_records": positives,
        "unsupported_records": unsupported,
        "records": records,
    }
    args.out.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "out": str(args.out),
        "state_count": len(states),
        "hop_counts": certificate["hop_counts"],
        "verdict_counts": certificate["verdict_counts"],
        "support_counts": certificate["support_counts"],
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
