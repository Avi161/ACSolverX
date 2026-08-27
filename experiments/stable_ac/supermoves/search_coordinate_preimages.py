"""Search the 124 classes for shortening reverse coordinate actions."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from experiments.stable_ac.supermoves.certified_acm import (
    cyclic_key,
    cyclic_orientations,
)
from experiments.stable_ac.supermoves.quotient_isolator import (
    exponent_sum,
    substitute_generator,
)
from experiments.stable_ac.supermoves.search_coordinate_descents import reduced_words


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--checker-root", type=Path, required=True)
    parser.add_argument("--max-image-length", type=int, default=7)
    parser.add_argument("--max-preimage-length", type=int, default=8)
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
    source_keys = {
        cyclic_key(row[relator])
        for row in rows
        for relator in ("r1", "r2")
    }
    orientation_to_key = {
        orientation: cyclic_key(row[relator])
        for row in rows
        for relator in ("r1", "r2")
        for orientation in cyclic_orientations(row[relator])
    }
    required = {
        row["name"]: (cyclic_key(row["r1"]), cyclic_key(row["r2"]))
        for row in rows
    }
    preimage_words = tuple(reduced_words(args.max_preimage_length))
    records = []
    candidate_count = 0
    for generator in ("x", "y"):
        fixed = "y" if generator == "x" else "x"
        for image in reduced_words(args.max_image_length):
            if exponent_sum(image, generator) not in (-1, 1):
                continue
            basis = (image, fixed) if generator == "x" else (fixed, image)
            if nielsen_reduce(basis) is not None:
                continue
            candidate_count += 1
            found = {}
            for preimage in preimage_words:
                if not preimage:
                    continue
                image_word = substitute_generator(preimage, generator, image)
                image_key = orientation_to_key.get(image_word)
                if image_key in source_keys and image_key not in found:
                    found[image_key] = preimage
            for row in rows:
                left_key, right_key = required[row["name"]]
                if left_key not in found or right_key not in found:
                    continue
                preimage_pair = (found[left_key], found[right_key])
                source_pair = (row["r1"], row["r2"])
                source_floor, source_rep, _ = aut_canon(source_pair)
                preimage_floor, preimage_rep, _ = aut_canon(preimage_pair)
                records.append(
                    {
                        "name": row["name"],
                        "generator": generator,
                        "image": image,
                        "source": list(source_pair),
                        "preimage": list(preimage_pair),
                        "source_floor": source_floor,
                        "preimage_floor": preimage_floor,
                        "floor_delta": preimage_floor - source_floor,
                        "nonautomorphic": source_rep != preimage_rep,
                    }
                )
        print(f"finished generator {generator}: {candidate_count} candidates", flush=True)

    payload = {
        "max_image_length": args.max_image_length,
        "max_preimage_length": args.max_preimage_length,
        "proper_coordinate_candidates": candidate_count,
        "matches": sorted(
            records,
            key=lambda row: (
                row["floor_delta"], row["name"], row["generator"], row["image"]
            ),
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"matches={len(records)}", flush=True)


if __name__ == "__main__":
    main()
