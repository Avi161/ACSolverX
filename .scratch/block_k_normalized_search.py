"""Normalize short AC-trivial image tuples before applying them to ACA124."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import deque
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from block_k_ac_ball_search import successors
from experiments.stable_ac.supermoves.search_coordinate_descents import substitute_pair


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--checker-root", type=Path, required=True)
    parser.add_argument("--depth", type=int, default=5)
    parser.add_argument("--max-image-total", type=int, default=12)
    parser.add_argument("--whitehead-margin", type=int, default=6)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    import experiments
    import experiments.stable_ac

    package_path = str(args.checker_root / "experiments")
    stable_path = str(args.checker_root / "experiments/stable_ac")
    if package_path not in experiments.__path__:
        experiments.__path__.append(package_path)
    if stable_path not in experiments.stable_ac.__path__:
        experiments.stable_ac.__path__.append(stable_path)
    from experiments.equivalence_classes.lib.autcanon import (
        aut_canon,
        aut_min_len,
        peak_reduce,
    )
    from experiments.equivalence_classes.lib.words import apply_hom, free_reduce
    from experiments.stable_ac.rank3_compression.primitive_bases import nielsen_reduce

    with args.data.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    sources = []
    for row in rows:
        source = (row["r1"], row["r2"])
        floor, rep, _ = aut_canon(source)
        sources.append((row["name"], source, floor, rep))

    start = ("x", "y")
    queue = deque([(start, 0)])
    certificates = {start: []}
    normalized: dict[tuple[str, str], dict[str, object]] = {}
    proper_states = 0
    raw_descents = 0
    minimum_raw_delta = None
    whitehead_checks = 0
    records = []

    while queue:
        image_pair, depth = queue.popleft()
        if depth == args.depth:
            continue
        for child, move in successors(image_pair):
            if sum(map(len, child)) > args.max_image_total or child in certificates:
                continue
            certificate = certificates[image_pair] + [move]
            certificates[child] = certificate
            child_depth = depth + 1
            queue.append((child, child_depth))
            if nielsen_reduce(child) is not None:
                continue
            proper_states += 1
            image_floor, image_descent_rep, image_witness = peak_reduce(child)
            # Keep only the simultaneous ambient automorphism here.  The
            # relator-level swaps/inversions/rotations used by ``image_rep``
            # would precompose the endomorphism and can change its action on
            # a source tuple.  In contrast, applying ``image_witness`` to both
            # component images is postcomposition, so it preserves the exact
            # Aut-orbit (and Whitehead floor) of every resulting target.
            normalized_exact = tuple(
                free_reduce(apply_hom(word, image_witness)) for word in child
            )
            if normalized_exact in normalized:
                continue
            normalized[normalized_exact] = {
                "raw_image_tuple": list(child),
                "raw_quotient_ac_certificate": certificate,
                "raw_certificate_depth": child_depth,
                "image_floor": image_floor,
                "image_descent_representative": list(image_descent_rep),
                "image_whitehead_witness": image_witness,
            }

    for image_rep, provenance in normalized.items():
        for name, source, source_floor, source_rep in sources:
            target = tuple(
                substitute_pair(relator, image_rep[0], image_rep[1])
                for relator in source
            )
            raw_total = sum(map(len, target))
            raw_delta = raw_total - source_floor
            if minimum_raw_delta is None or raw_delta < minimum_raw_delta:
                minimum_raw_delta = raw_delta
            if raw_total < source_floor:
                raw_descents += 1
            if raw_total > source_floor + args.whitehead_margin:
                continue
            whitehead_checks += 1
            target_floor = aut_min_len(target)
            if target_floor >= source_floor:
                continue
            exact_floor, target_rep, target_witness = aut_canon(target)
            if exact_floor != target_floor or target_rep == source_rep:
                continue
            records.append(
                {
                    "name": name,
                    "source": list(source),
                    "source_floor": source_floor,
                    "source_representative": list(source_rep),
                    "image_tuple": list(image_rep),
                    **provenance,
                    "target": list(target),
                    "target_raw_total": raw_total,
                    "target_floor": target_floor,
                    "target_representative": list(target_rep),
                    "target_whitehead_witness": target_witness,
                    "floor_delta": target_floor - source_floor,
                }
            )

    payload = {
        "depth": args.depth,
        "max_image_total": args.max_image_total,
        "whitehead_margin": args.whitehead_margin,
        "ac_ball_states": len(certificates),
        "proper_states": proper_states,
        "distinct_normalized_proper_image_tuples": len(normalized),
        "normalized_raw_descents": raw_descents,
        "minimum_normalized_raw_delta": minimum_raw_delta,
        "target_whitehead_checks": whitehead_checks,
        "strict_nonautomorphic_floor_descents": len(records),
        "records": sorted(
            records,
            key=lambda row: (row["floor_delta"], row["name"], row["image_tuple"]),
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in payload.items() if key != "records"}))
    for record in payload["records"][:20]:
        print(json.dumps(record, sort_keys=True))


if __name__ == "__main__":
    main()
