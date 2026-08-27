"""Census hidden-cancellation rank-three corridors on the 124 classes."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--checker-root", type=Path, required=True)
    parser.add_argument("--max-word-length", type=int, default=3)
    parser.add_argument("--max-template-length", type=int, default=5)
    parser.add_argument("--name")
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
    from experiments.equivalence_classes.lib.acmoves import canon
    from experiments.equivalence_classes.lib.autcanon import aut_canon
    from experiments.stable_ac.rank3_compression.corridors import (
        enumerate_short_corridors,
    )

    with args.data.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if args.name is not None:
        selected = set(args.name.split(","))
        rows = [row for row in rows if row["name"] in selected]
        if not rows:
            raise ValueError(f"unknown source names: {args.name}")
    records = []
    for index, row in enumerate(rows, start=1):
        source = (row["r1"], row["r2"])
        source_floor, source_rep, _ = aut_canon(source)
        census = enumerate_short_corridors(
            source,
            max_word_length=args.max_word_length,
            max_template_length=args.max_template_length,
        )
        accepted_by_output = {}
        for accepted in census.accepted:
            accepted_by_output.setdefault(canon(*accepted.output), accepted)
        best = None
        if census.aut_records:
            aut_record = min(
                census.aut_records,
                key=lambda item: (item.minimum_total, item.representative),
            )
            witness = accepted_by_output[aut_record.output]
            best = {
                "source_index": witness.source_index,
                "source_orientation": witness.source_orientation,
                "eliminated": witness.eliminated,
                "defining_word": witness.word,
                "isolator_template": witness.template,
                "expression": witness.expression,
                "output": list(aut_record.output),
                "output_floor": aut_record.minimum_total,
                "output_representative": list(aut_record.representative),
                "floor_delta": aut_record.minimum_total - source_floor,
                "nonautomorphic": aut_record.representative != source_rep,
            }
        records.append(
            {
                "name": row["name"],
                "source": list(source),
                "source_floor": source_floor,
                "source_representative": list(source_rep),
                "accepted_count": census.accepted_count,
                "trace_sha256": census.trace_sha256,
                "best": best,
            }
        )
        print(
            f"{index}/{len(rows)} {row['name']} accepted={census.accepted_count} "
            f"best={None if best is None else best['output_floor']}",
            flush=True,
        )

    payload = {
        "schema": "aca124-rank3-hidden-cancellation-v1",
        "bounds": {
            "max_word_length": args.max_word_length,
            "max_template_length": args.max_template_length,
            "minimum_z_occurrences": 2,
        },
        "summary": {
            "class_count": len(records),
            "classes_with_corridors": sum(row["best"] is not None for row in records),
            "classes_with_floor_descent": sum(
                row["best"] is not None and row["best"]["floor_delta"] < 0
                for row in records
            ),
            "classes_with_nonautomorphic_output": sum(
                row["best"] is not None and row["best"]["nonautomorphic"]
                for row in records
            ),
        },
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
