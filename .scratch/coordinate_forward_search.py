"""Exhaustive forward proper-coordinate shortening search on ACA124."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from experiments.stable_ac.supermoves.quotient_isolator import (
    coordinate_endomorphism_move,
    exponent_sum,
)
from experiments.stable_ac.supermoves.search_coordinate_descents import reduced_words


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--checker-root", type=Path, required=True)
    parser.add_argument("--max-image-length", type=int, default=8)
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
    sources = []
    for row in rows:
        pair = (row["r1"], row["r2"])
        floor, rep, _ = aut_canon(pair)
        sources.append((row["name"], pair, floor, rep))

    candidates = 0
    evaluations = 0
    records = []
    for generator in ("x", "y"):
        fixed = "y" if generator == "x" else "x"
        for image in reduced_words(args.max_image_length):
            if exponent_sum(image, generator) not in (-1, 1):
                continue
            image_pair = (image, fixed) if generator == "x" else (fixed, image)
            if nielsen_reduce(image_pair) is not None:
                continue
            candidates += 1
            for name, source, source_floor, source_rep in sources:
                evaluations += 1
                target = coordinate_endomorphism_move(source, generator, image).target
                raw_total = sum(map(len, target))
                if raw_total >= source_floor:
                    continue
                target_floor, target_rep, target_witness = aut_canon(target)
                if target_floor >= source_floor or target_rep == source_rep:
                    raise AssertionError("raw descent failed the exact orbit check")
                records.append(
                    {
                        "name": name,
                        "source": list(source),
                        "source_floor": source_floor,
                        "source_representative": list(source_rep),
                        "generator": generator,
                        "coordinate_image": image,
                        "target": list(target),
                        "target_raw_total": raw_total,
                        "target_floor": target_floor,
                        "target_representative": list(target_rep),
                        "target_whitehead_witness": target_witness,
                        "floor_delta": target_floor - source_floor,
                    }
                )
    payload = {
        "max_image_length": args.max_image_length,
        "proper_coordinate_candidates": candidates,
        "source_map_evaluations": evaluations,
        "strict_raw_and_whitehead_floor_descents": len(records),
        "records": sorted(
            records,
            key=lambda row: (
                row["floor_delta"], row["name"], row["generator"], row["coordinate_image"]
            ),
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in payload.items() if key != "records"}))
    for record in payload["records"][:20]:
        print(json.dumps(record, sort_keys=True))


if __name__ == "__main__":
    main()
