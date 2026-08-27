"""Equal-budget baseline/QIE start-state solver ablation."""

from __future__ import annotations

import argparse
import json
from hashlib import sha256
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--census", type=Path, required=True)
    parser.add_argument("--solver-root", type=Path, required=True)
    parser.add_argument("--budget", type=int, default=1_000)
    parser.add_argument("--cap", type=int, default=48)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    import experiments

    package_path = str(args.solver_root / "experiments")
    if package_path not in experiments.__path__:
        experiments.__path__.append(package_path)
    from experiments.search.greedy_baseline import greedy_search

    census = json.loads(args.census.read_text())
    records = []
    for index, row in enumerate(census["records"], start=1):
        source = greedy_search(
            *row["source"], args.budget, args.cap, True, True
        )
        target = greedy_search(
            *row["target"], args.budget, args.cap, True, True
        )
        record = {
            "name": row["name"],
            "source": {
                "solved": source["solved"],
                "nodes": source["nodes_explored"],
                "min_total": source["min_relator_length"],
            },
            "target": {
                "solved": target["solved"],
                "nodes": target["nodes_explored"],
                "min_total": target["min_relator_length"],
            },
        }
        records.append(record)
        print(
            f"{index}/{len(census['records'])} {row['name']} "
            f"source={source['solved']}/{source['min_relator_length']} "
            f"target={target['solved']}/{target['min_relator_length']}",
            flush=True,
        )

    payload = {
        "schema": "aca124-coordinate-solver-ablation-v1",
        "budget": args.budget,
        "max_relator_length": args.cap,
        "summary": {
            "class_count": len(records),
            "source_solved": sum(row["source"]["solved"] for row in records),
            "target_solved": sum(row["target"]["solved"] for row in records),
            "target_only_solved": sum(
                row["target"]["solved"] and not row["source"]["solved"]
                for row in records
            ),
            "target_lower_minimum": sum(
                row["target"]["min_total"] < row["source"]["min_total"]
                for row in records
            ),
        },
        "records": records,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["payload_sha256"] = sha256(encoded.encode()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
