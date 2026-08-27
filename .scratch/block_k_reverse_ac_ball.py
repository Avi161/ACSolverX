"""Search reverse images under short proper AC-trivial quotient tuples."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import deque
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from block_k_ac_ball_search import successors
from stallings_coordinate_preimages import StallingsRewriter
from experiments.stable_ac.supermoves.certified_acm import (
    cyclic_orientations,
    cyclic_reduce,
)
from experiments.stable_ac.supermoves.search_coordinate_descents import substitute_pair


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--checker-root", type=Path, required=True)
    parser.add_argument("--depth", type=int, default=4)
    parser.add_argument("--max-image-total", type=int, default=10)
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
    from experiments.equivalence_classes.lib.autcanon import aut_canon
    from experiments.stable_ac.rank3_compression.primitive_bases import (
        apply_nielsen,
        nielsen_reduce,
    )

    with args.data.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    sources = []
    for row in rows:
        pair = (row["r1"], row["r2"])
        floor, rep, _ = aut_canon(pair)
        sources.append(
            (
                row["name"],
                pair,
                tuple(cyclic_orientations(pair[0])),
                tuple(cyclic_orientations(pair[1])),
                floor,
                rep,
            )
        )

    start = ("x", "y")
    queue = deque([(start, 0)])
    certificates = {start: []}
    depth_counts = [1]
    proper_count = 0
    membership_pairs = 0
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
            while len(depth_counts) <= child_depth:
                depth_counts.append(0)
            depth_counts[child_depth] += 1
            queue.append((child, child_depth))
            if nielsen_reduce(child) is not None:
                continue
            proper_count += 1
            rewriter = StallingsRewriter(
                child[0], child[1], nielsen_reduce, apply_nielsen
            )
            for name, source, left_orientations, right_orientations, source_floor, source_rep in sources:
                preimages = []
                exact_images = []
                for orientations in (left_orientations, right_orientations):
                    choices = []
                    for orientation in orientations:
                        preimage = rewriter.preimage(orientation)
                        if preimage is None:
                            continue
                        mapped = substitute_pair(preimage, child[0], child[1])
                        if cyclic_reduce(mapped) != cyclic_reduce(orientation):
                            raise AssertionError("preimage replay failed")
                        choices.append((len(cyclic_reduce(preimage)), preimage, orientation))
                    if not choices:
                        break
                    _, preimage, orientation = min(choices)
                    preimages.append(cyclic_reduce(preimage))
                    exact_images.append(orientation)
                if len(preimages) != 2:
                    continue
                membership_pairs += 1
                preimage_pair = tuple(preimages)
                pre_floor, pre_rep, witness = aut_canon(preimage_pair)
                if pre_floor >= source_floor or pre_rep == source_rep:
                    continue
                records.append(
                    {
                        "name": name,
                        "source": list(source),
                        "source_floor": source_floor,
                        "source_representative": list(source_rep),
                        "image_tuple": list(child),
                        "quotient_ac_certificate": certificate,
                        "certificate_depth": child_depth,
                        "exact_oriented_images": exact_images,
                        "preimage": list(preimage_pair),
                        "preimage_floor": pre_floor,
                        "preimage_representative": list(pre_rep),
                        "floor_delta": pre_floor - source_floor,
                        "preimage_whitehead_witness": witness,
                    }
                )

    payload = {
        "depth": args.depth,
        "max_image_total": args.max_image_total,
        "states": len(certificates),
        "states_by_first_seen_depth": depth_counts,
        "proper_states_processed": proper_count,
        "source_pairs_in_images": membership_pairs,
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
