"""Search proper coordinate actions for equal-budget solver improvements."""

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
    parser.add_argument("--solver-root", type=Path, required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--max-image-length", type=int, default=7)
    parser.add_argument("--budget", type=int, default=100)
    parser.add_argument("--cap", type=int, default=48)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    import experiments
    import experiments.stable_ac

    package_path = str(args.solver_root / "experiments")
    stable_path = str(args.solver_root / "experiments/stable_ac")
    if package_path not in experiments.__path__:
        experiments.__path__.append(package_path)
    if stable_path not in experiments.stable_ac.__path__:
        experiments.stable_ac.__path__.append(stable_path)
    from experiments.search.greedy_baseline import greedy_search
    from experiments.stable_ac.rank3_compression.primitive_bases import nielsen_reduce

    with args.data.open(newline="") as handle:
        row = next(row for row in csv.DictReader(handle) if row["name"] == args.name)
    source = (row["r1"], row["r2"])
    baseline = greedy_search(*source, args.budget, args.cap, True, True)

    candidates = []
    seen_targets = set()
    for generator in ("x", "y"):
        fixed = "y" if generator == "x" else "x"
        ordered_basis = ("x", "y")
        for image in reduced_words(args.max_image_length):
            if exponent_sum(image, generator) not in (-1, 1):
                continue
            basis = (
                (image, fixed) if generator == "x" else (fixed, image)
            )
            if nielsen_reduce(basis) is not None:
                continue
            move = coordinate_endomorphism_move(source, generator, image)
            if move.target in seen_targets:
                continue
            seen_targets.add(move.target)
            if max(map(len, move.target)) > args.cap:
                continue
            candidates.append(
                (
                    sum(map(len, move.target)),
                    generator,
                    image,
                    move.target,
                    ordered_basis,
                )
            )

    results = []
    for index, (_, generator, image, target, _) in enumerate(
        sorted(candidates), start=1
    ):
        stats = greedy_search(*target, args.budget, args.cap, True, True)
        if stats["solved"] or stats["min_relator_length"] < baseline["min_relator_length"]:
            result = {
                "generator": generator,
                "image": image,
                "target": list(target),
                "solved": stats["solved"],
                "nodes": stats["nodes_explored"],
                "min_total": stats["min_relator_length"],
            }
            results.append(result)
            print(f"improvement {result}", flush=True)
        if index % 100 == 0:
            print(f"{index}/{len(candidates)}", flush=True)

    payload = {
        "name": args.name,
        "source": list(source),
        "max_image_length": args.max_image_length,
        "budget": args.budget,
        "cap": args.cap,
        "baseline": {
            "solved": baseline["solved"],
            "nodes": baseline["nodes_explored"],
            "min_total": baseline["min_relator_length"],
        },
        "proper_distinct_targets": len(candidates),
        "improvements": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
