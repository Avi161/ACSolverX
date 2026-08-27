"""Scout solved-presentation composition targets against the 124 classes."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--solver-root", type=Path, required=True)
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--name")
    parser.add_argument("--budget", type=int, default=100)
    parser.add_argument("--cap", type=int, default=48)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    import experiments

    package_path = str(args.solver_root / "experiments")
    if package_path not in experiments.__path__:
        experiments.__path__.append(package_path)
    from experiments.equivalence_classes.lib.words import apply_hom, canon_pair
    from experiments.search.greedy_baseline import greedy_search

    with args.data.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if args.name is not None:
        rows = [row for row in rows if row["name"] == args.name]
        if not rows:
            raise ValueError(f"unknown source name: {args.name}")
    with args.images.open(newline="") as handle:
        images = list(csv.DictReader(handle))

    records = []
    for index, row in enumerate(rows, start=1):
        source = (row["r1"], row["r2"])
        baseline = greedy_search(*source, args.budget, args.cap, True, True)
        candidates = []
        for image_row in images:
            mapping = {"x": image_row["rep_r1"], "y": image_row["rep_r2"]}
            target = canon_pair(
                apply_hom(source[0], mapping),
                apply_hom(source[1], mapping),
            )
            if max(map(len, target)) > args.cap:
                continue
            candidates.append(
                (sum(map(len, target)), image_row["aut_id"], mapping, target)
            )
        improvements = []
        for _, aut_id, mapping, target in sorted(candidates)[: args.top]:
            stats = greedy_search(*target, args.budget, args.cap, True, True)
            if stats["solved"] or stats["min_relator_length"] < baseline["min_relator_length"]:
                improvements.append(
                    {
                        "image_id": aut_id,
                        "images": mapping,
                        "target": list(target),
                        "solved": stats["solved"],
                        "nodes": stats["nodes_explored"],
                        "min_total": stats["min_relator_length"],
                    }
                )
        if improvements:
            records.append(
                {
                    "name": row["name"],
                    "source": list(source),
                    "baseline": {
                        "solved": baseline["solved"],
                        "nodes": baseline["nodes_explored"],
                        "min_total": baseline["min_relator_length"],
                    },
                    "improvements": improvements,
                }
            )
            print(f"improvement {records[-1]}", flush=True)
        print(f"{index}/{len(rows)}", flush=True)

    payload = {
        "top_per_source": args.top,
        "budget": args.budget,
        "cap": args.cap,
        "sources": len(rows),
        "image_presentations": len(images),
        "improved_sources": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
