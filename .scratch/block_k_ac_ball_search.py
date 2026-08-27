"""Search short AC-trivial quotient tuples for Whitehead-floor descents."""

from __future__ import annotations

import argparse
import csv
import json
from collections import deque
from pathlib import Path

from experiments.stable_ac.supermoves.certified_acm import free_reduce, inverse
from experiments.stable_ac.supermoves.search_coordinate_descents import substitute_pair


LETTERS = "xXyY"


def successors(pair: tuple[str, str]):
    for target in (0, 1):
        child = list(pair)
        child[target] = inverse(child[target])
        yield tuple(child), {"kind": "invert", "target": target}

        other = 1 - target
        child = list(pair)
        child[target] = free_reduce(child[target] + child[other])
        yield tuple(child), {
            "kind": "multiply",
            "target": target,
            "other": other,
        }

        for letter in LETTERS:
            child = list(pair)
            child[target] = free_reduce(
                letter.swapcase() + child[target] + letter
            )
            yield tuple(child), {
                "kind": "conjugate",
                "target": target,
                "letter": letter,
            }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--checker-root", type=Path, required=True)
    parser.add_argument("--depth", type=int, default=6)
    parser.add_argument("--max-image-total", type=int, default=14)
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
    from experiments.stable_ac.rank3_compression.primitive_bases import nielsen_reduce

    with args.data.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    source_data = []
    for row in rows:
        pair = (row["r1"], row["r2"])
        floor, rep, _ = aut_canon(pair)
        source_data.append((row["name"], pair, floor, rep))

    start = ("x", "y")
    queue = deque([(start, 0)])
    certificates: dict[tuple[str, str], list[dict[str, object]]] = {start: []}
    depth_counts = [1]
    proper_count = 0
    raw_descents = 0
    records = []

    while queue:
        image_pair, depth = queue.popleft()
        if depth == args.depth:
            continue
        for child, move in successors(image_pair):
            if sum(map(len, child)) > args.max_image_total:
                continue
            if child in certificates:
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
            for name, source, source_floor, source_rep in source_data:
                target = tuple(
                    substitute_pair(relator, child[0], child[1])
                    for relator in source
                )
                target_raw = sum(map(len, target))
                if target_raw >= source_floor:
                    continue
                raw_descents += 1
                target_floor, target_rep, witness = aut_canon(target)
                if target_floor >= source_floor or target_rep == source_rep:
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
                        "target": list(target),
                        "target_raw_total": target_raw,
                        "target_floor": target_floor,
                        "target_representative": list(target_rep),
                        "floor_delta": target_floor - source_floor,
                        "target_whitehead_witness": witness,
                    }
                )

    payload = {
        "depth": args.depth,
        "max_image_total": args.max_image_total,
        "states": len(certificates),
        "states_by_first_seen_depth": depth_counts,
        "proper_states_processed": proper_count,
        "raw_descents_checked": raw_descents,
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
