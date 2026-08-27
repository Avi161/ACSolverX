"""Reproducible random search for raw-shortening AC-trivial image tuples."""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from block_k_ac_ball_search import successors
from experiments.stable_ac.supermoves.search_coordinate_descents import substitute_pair


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--walks", type=int, default=10_000)
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--max-image-total", type=int, default=30)
    parser.add_argument("--seed", type=int, default=260816)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    with args.data.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    sources = [
        (row["name"], (row["r1"], row["r2"]), len(row["r1"]) + len(row["r2"]))
        for row in rows
    ]
    rng = random.Random(args.seed)
    seen = {("x", "y")}
    evaluations = 0
    records = []
    for _ in range(args.walks):
        state = ("x", "y")
        certificate = []
        for depth in range(1, args.steps + 1):
            options = [
                option
                for option in successors(state)
                if option[0] != state
                and sum(map(len, option[0])) <= args.max_image_total
            ]
            if not options:
                break
            state, move = rng.choice(options)
            certificate.append(move)
            if state in seen:
                continue
            seen.add(state)
            for name, source, source_floor in sources:
                evaluations += 1
                target = tuple(
                    substitute_pair(relator, state[0], state[1])
                    for relator in source
                )
                target_total = sum(map(len, target))
                if target_total >= source_floor:
                    continue
                records.append(
                    {
                        "name": name,
                        "source": list(source),
                        "source_floor": source_floor,
                        "image_tuple": list(state),
                        "quotient_ac_certificate": list(certificate),
                        "certificate_depth": depth,
                        "target": list(target),
                        "target_raw_total": target_total,
                        "raw_delta": target_total - source_floor,
                    }
                )
    payload = {
        "walks": args.walks,
        "steps": args.steps,
        "max_image_total": args.max_image_total,
        "seed": args.seed,
        "distinct_image_tuples": len(seen),
        "source_map_evaluations": evaluations,
        "raw_descents": len(records),
        "records": sorted(
            records,
            key=lambda row: (row["raw_delta"], row["name"], row["image_tuple"]),
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in payload.items() if key != "records"}))
    for record in payload["records"][:20]:
        print(json.dumps(record, sort_keys=True))


if __name__ == "__main__":
    main()
