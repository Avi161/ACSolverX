#!/usr/bin/env python3
"""Exact supported-class Neuwirth scan of the shipped aca124 CoV sweep."""

from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import sys
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROOF_ROOT = ROOT / ".claude/worktrees/codex-proofs"
sys.path.insert(0, str(PROOF_ROOT))
sys.path.insert(0, str(ROOT / ".scratch"))

from experiments.stable_ac.thickenable.neuwirth_one_loop_solver import (  # noqa: E402
    classify_one_loop_support,
    solve_one_loop_spherical,
)
from experiments.stable_ac.thickenable import neuwirth_rank_solver as rank_base  # noqa: E402
from experiments.stable_ac.thickenable.neuwirth_p4_solver import (  # noqa: E402
    classify_four_germ_support,
    solve_four_germ_spherical,
)
from experiments.stable_ac.thickenable.neuwirth_paw_one_loop_solver import (  # noqa: E402
    classify_paw_one_loop_support,
    solve_paw_one_loop_spherical,
)
from experiments.stable_ac.thickenable.neuwirth_rank_solver import (  # noqa: E402
    classify_support,
    solve_spherical,
)
from fast_one_loop import solve_one_loop_spherical_fast  # noqa: E402


SWEEP = (
    PROOF_ROOT
    / "results/stable_ac/cov/"
    "covsweep_50000_124_subnc2pxysb_mrl24_cyc_aca124_07_21_26.jsonl"
)
DATA = PROOF_ROOT / "data/ms_unsolved_reps/aca_124.csv"
BASE_SOLVER = (
    PROOF_ROOT
    / "experiments/stable_ac/thickenable/neuwirth_rank_solver.py"
)
ONE_LOOP_SOLVER = (
    PROOF_ROOT
    / "experiments/stable_ac/thickenable/neuwirth_one_loop_solver.py"
)
P4_SOLVER = (
    PROOF_ROOT / "experiments/stable_ac/thickenable/neuwirth_p4_solver.py"
)
PAW_LOOP_SOLVER = (
    PROOF_ROOT
    / "experiments/stable_ac/thickenable/neuwirth_paw_one_loop_solver.py"
)
FAST_ONE_LOOP_SOLVER = ROOT / ".scratch/fast_one_loop.py"
DEFAULT_OUT = ROOT / ".scratch/aca124_cov_neuwirth_scan.json"
CHECKPOINT_SCHEMA = "aca124-cov-neuwirth-full-cascade-fast-v1"
DEFAULT_CHECKPOINT = (
    ROOT / ".scratch/aca124_cov_neuwirth_scan.v2.records.jsonl"
)


_INVERSE_SLOT_CACHE: dict[tuple[int, int], dict[int, int]] = {}
_SCHEME_REFS: dict[int, object] = {}
_PROPAGATION_CACHE: dict[tuple[int, object], dict[int, tuple[int, ...]]] = {}
_CONSTRAINT_REFS: dict[int, object] = {}


def fast_inverse_slot(scheme, dart: int, required_slot: int) -> int | None:
    """Exact inverse of an injective slot map, cached once per scheme/dart."""
    scheme_id = id(scheme)
    key = (scheme_id, dart)
    inverse = _INVERSE_SLOT_CACHE.get(key)
    if inverse is None:
        image = scheme.slots[dart]
        inverse = {slot: rank for rank, slot in enumerate(image)}
        if len(inverse) != len(image):
            raise AssertionError("slot map is not injective")
        _INVERSE_SLOT_CACHE[key] = inverse
        _SCHEME_REFS[scheme_id] = scheme
    return inverse.get(required_slot)


rank_base._inverse_slot = fast_inverse_slot


def fast_propagate_component(
    data,
    scheme,
    constraints,
    component,
    phases,
    seed_rank,
):
    """Queue propagation equivalent to the solver's repeated full scans."""
    edges, constraint_indices = component
    constraints_id = id(constraints)
    cache_key = (constraints_id, component)
    incident = _PROPAGATION_CACHE.get(cache_key)
    if incident is None:
        mutable = {edge: [] for edge in edges}
        for index in constraint_indices:
            constraint = constraints[index]
            mutable[constraint.edge_positive].append(index)
            if constraint.edge_negative != constraint.edge_positive:
                mutable[constraint.edge_negative].append(index)
        incident = {
            edge: tuple(indices) for edge, indices in mutable.items()
        }
        _PROPAGATION_CACHE[cache_key] = incident
        _CONSTRAINT_REFS[constraints_id] = constraints

    seed_edge = edges[0]
    assignments = {seed_edge: seed_rank}
    queue = [seed_edge]
    while queue:
        edge = queue.pop()
        for index in incident[edge]:
            constraint = constraints[index]
            left = constraint.edge_positive
            right = constraint.edge_negative
            phase = phases[constraint.phase_index]
            modulus = constraint.modulus
            if left in assignments and right not in assignments:
                required = (
                    -phase
                    - scheme.slots[constraint.dart_positive][assignments[left]]
                ) % modulus
                rank = fast_inverse_slot(
                    scheme, constraint.dart_negative, required
                )
                if rank is None:
                    return None, False
                assignments[right] = rank
                queue.append(right)
            elif right in assignments and left not in assignments:
                required = (
                    -phase
                    - scheme.slots[constraint.dart_negative][assignments[right]]
                ) % modulus
                rank = fast_inverse_slot(
                    scheme, constraint.dart_positive, required
                )
                if rank is None:
                    return None, False
                assignments[left] = rank
                queue.append(left)

    if set(assignments) != set(edges):
        raise AssertionError("seed propagation did not cover its component")
    for index in constraint_indices:
        constraint = constraints[index]
        if (
            scheme.slots[constraint.dart_positive][
                assignments[constraint.edge_positive]
            ]
            + scheme.slots[constraint.dart_negative][
                assignments[constraint.edge_negative]
            ]
            + phases[constraint.phase_index]
        ) % constraint.modulus:
            return None, False

    used = {}
    for edge, rank in assignments.items():
        key = data.edge_class[edge]
        previous = used.setdefault(key, {}).get(rank)
        if previous is not None and previous != edge:
            return None, True
        used[key][rank] = edge
    masks = tuple(
        (key, sum(1 << rank for rank in ranks))
        for key, ranks in sorted(used.items())
    )
    return (
        rank_base._ComponentSolution(tuple(sorted(assignments.items())), masks),
        False,
    )


rank_base._propagate_component = fast_propagate_component


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jsonable(value: object) -> object:
    return json.loads(json.dumps(value, ensure_ascii=True))


def decide(item: tuple[int, dict[str, object]]) -> dict[str, object]:
    _INVERSE_SLOT_CACHE.clear()
    _SCHEME_REFS.clear()
    _PROPAGATION_CACHE.clear()
    _CONSTRAINT_REFS.clear()
    index, row = item
    words = (str(row["r1"]), str(row["r2"]))
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
        raise AssertionError(f"non-exhaustive negative at sweep row {index}")
    if decision.spherical is True and decision.witness is None:
        raise AssertionError(f"positive lacks a witness at sweep row {index}")

    provenance_keys = (
        "pres_id",
        "r1_orig",
        "r2_orig",
        "r1",
        "r2",
        "z_word",
        "iso_gen",
        "iso_index",
        "n_subs",
        "family_tag",
        "max_relator_length_cap",
        "cyclic_reduce",
        "git_commit",
        "aut_canon_orig",
        "aut_canon_cov",
        "start_total_length_orig",
        "start_total_length_cov",
    )
    return {
        "checkpoint_schema": CHECKPOINT_SCHEMA,
        "sweep_row": index,
        "provenance": {key: row.get(key) for key in provenance_keys},
        "solver": solver,
        "support": decision.support.kind,
        "simple_edges": [
            list(edge) for edge in sorted(decision.support.simple_edges)
        ],
        "verdict": verdict,
        "reason": decision.reason,
        "counters": jsonable(asdict(decision.counters)),
        "witness": (
            jsonable(asdict(decision.witness))
            if decision.witness is not None
            else None
        ),
    }


def load_candidates() -> list[tuple[int, dict[str, object]]]:
    candidates = []
    seen = set()
    with SWEEP.open() as handle:
        for index, line in enumerate(handle):
            row = json.loads(line)
            if row.get("n_cov") != 1 or row.get("cov_applicable") is not True:
                continue
            pair = (row["r1"], row["r2"])
            if pair in seen:
                raise AssertionError(f"duplicate exact CoV endpoint {pair!r}")
            seen.add(pair)
            candidates.append((index, row))
    if len(candidates) != 11246:
        raise AssertionError(f"expected 11246 CoV rows, got {len(candidates)}")
    if len({row["pres_id"] for _, row in candidates}) != 124:
        raise AssertionError("CoV sweep does not cover all 124 source classes")
    return candidates


def estimated_cost(item: tuple[int, dict[str, object]]) -> tuple[int, int, int]:
    """Cheap ordering only; it never changes the exact solver or verdict."""
    index, row = item
    words = (str(row["r1"]), str(row["r2"]))
    total_length = sum(map(len, words))
    support = classify_support(words)
    if support.kind != "UNSUPPORTED":
        return (0, total_length, index)
    p4_support = classify_four_germ_support(words)
    if p4_support.kind != "UNSUPPORTED":
        return (1, total_length, index)
    loop_support = classify_one_loop_support(words)
    if loop_support.kind != "UNSUPPORTED":
        data = loop_support.data
        loop_vertex = loop_support.loop_class[0]
        core_degree = len(data.vertex_darts[loop_vertex]) - 2
        if loop_support.kind == "K4+1loop":
            schemes = 2 * core_degree
        else:
            c, d = loop_support.missing_edge
            poles = tuple(v for v in rank_base.GERMS if v not in (c, d))
            central = tuple(sorted(poles))
            schemes = 2 * core_degree * (
                len(data.class_edges[central]) + 1
            )
        phase_pairs = (
            len(data.vertex_darts[rank_base.G_X_POS])
            * len(data.vertex_darts[rank_base.G_Y_POS])
        )
        return (2, schemes * phase_pairs, index)
    paw_support = classify_paw_one_loop_support(words)
    if paw_support.kind != "UNSUPPORTED":
        return (3, total_length, index)
    return (-1, total_length, index)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=max(1, mp.cpu_count() - 1))
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    args = parser.parse_args()

    candidates = load_candidates()
    print(
        f"scanning {len(candidates)} distinct CoV endpoints with "
        f"{args.workers} workers",
        flush=True,
    )
    records_by_index = {}
    if args.checkpoint.exists():
        with args.checkpoint.open() as handle:
            for line in handle:
                record = json.loads(line)
                if record.get("checkpoint_schema") != CHECKPOINT_SCHEMA:
                    raise AssertionError("checkpoint schema mismatch")
                records_by_index[int(record["sweep_row"])] = record
    pending = [
        item for item in candidates if item[0] not in records_by_index
    ]
    pending.sort(key=estimated_cost)
    if records_by_index:
        print(
            f"resuming from {len(records_by_index)} checkpointed records; "
            f"{len(pending)} remain",
            flush=True,
        )
    args.checkpoint.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = args.checkpoint.open("a")
    if args.workers == 1:
        iterator = map(decide, pending)
        for count, record in enumerate(iterator, 1):
            records_by_index[int(record["sweep_row"])] = record
            checkpoint.write(json.dumps(record, sort_keys=True) + "\n")
            if count % 50 == 0:
                checkpoint.flush()
                print(f"  {count}/{len(pending)} new", flush=True)
    else:
        with mp.Pool(args.workers) as pool:
            iterator = pool.imap_unordered(decide, pending, chunksize=1)
            for count, record in enumerate(iterator, 1):
                records_by_index[int(record["sweep_row"])] = record
                checkpoint.write(json.dumps(record, sort_keys=True) + "\n")
                if count % 50 == 0:
                    checkpoint.flush()
                    print(f"  {count}/{len(pending)} new", flush=True)
    checkpoint.flush()
    checkpoint.close()

    records = sorted(
        records_by_index.values(), key=lambda item: int(item["sweep_row"])
    )
    if len(records) != len(candidates):
        raise AssertionError(
            f"expected {len(candidates)} decisions, got {len(records)}"
        )
    verdict_counts = Counter(record["verdict"] for record in records)
    support_counts = Counter(record["support"] for record in records)
    solver_counts = Counter(record["solver"] for record in records)
    by_source: dict[str, Counter[str]] = defaultdict(Counter)
    for record in records:
        source = str(record["provenance"]["pres_id"])
        by_source[source][str(record["verdict"])] += 1

    positives = [
        record
        for record in records
        if record["verdict"] == "SPHERICAL_REQUIRES_INDEPENDENT_VALIDATION"
    ]
    unsupported = [record for record in records if record["verdict"] == "UNSUPPORTED"]
    certificate = {
        "schema": "aca124-cov-supported-neuwirth-scan-v1",
        "scope": (
            "Every distinct applicable one-hop output in the shipped "
            "aca124 no-collapse subword-CoV sweep; exact base solver followed "
            "by exact one-loop solver on unsupported base supports."
        ),
        "source_hashes": {
            "sweep": sha256(SWEEP),
            "aca124": sha256(DATA),
            "base_solver": sha256(BASE_SOLVER),
            "one_loop_solver": sha256(ONE_LOOP_SOLVER),
            "p4_solver": sha256(P4_SOLVER),
            "paw_one_loop_solver": sha256(PAW_LOOP_SOLVER),
            "fast_one_loop_engine": sha256(FAST_ONE_LOOP_SOLVER),
            "driver": sha256(Path(__file__)),
        },
        "candidate_count": len(candidates),
        "source_class_count": len(by_source),
        "verdict_counts": dict(sorted(verdict_counts.items())),
        "support_counts": dict(sorted(support_counts.items())),
        "solver_counts": dict(sorted(solver_counts.items())),
        "positive_count": len(positives),
        "unsupported_count": len(unsupported),
        "positive_records": positives,
        "unsupported_records": unsupported,
        "by_source_verdict_counts": {
            source: dict(sorted(counts.items()))
            for source, counts in sorted(by_source.items())
        },
        "records": records,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "out": str(args.out),
        "verdict_counts": certificate["verdict_counts"],
        "support_counts": certificate["support_counts"],
        "positive_count": len(positives),
        "unsupported_count": len(unsupported),
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
