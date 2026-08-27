"""Beam search over quotient AC certificates, scored by ACA124 shortening."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from block_k_ac_ball_search import successors
from experiments.stable_ac.supermoves.search_coordinate_descents import substitute_pair


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--depth", type=int, default=16)
    parser.add_argument("--beam", type=int, default=2000)
    parser.add_argument("--max-image-total", type=int, default=40)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with args.data.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    sources = [
        (row["name"], (row["r1"], row["r2"]), len(row["r1"]) + len(row["r2"]))
        for row in rows
    ]

    def evaluate(image_pair):
        best = None
        for name, source, source_floor in sources:
            target = tuple(
                substitute_pair(relator, image_pair[0], image_pair[1])
                for relator in source
            )
            total = sum(map(len, target))
            candidate = (total - source_floor, total, name, source, source_floor, target)
            if best is None or candidate < best:
                best = candidate
        return best

    start = ("x", "y")
    frontier = [(start, [])]
    seen = {start}
    depth_stats = []
    records = []
    for depth in range(1, args.depth + 1):
        children = []
        for state, certificate in frontier:
            for child, move in successors(state):
                if (
                    child == state
                    or child in seen
                    or sum(map(len, child)) > args.max_image_total
                ):
                    continue
                seen.add(child)
                score = evaluate(child)
                child_certificate = certificate + [move]
                children.append((score, sum(map(len, child)), child, child_certificate))
                if score[0] < 0:
                    _, target_total, name, source, source_floor, target = score
                    records.append(
                        {
                            "name": name,
                            "source": list(source),
                            "source_floor": source_floor,
                            "image_tuple": list(child),
                            "quotient_ac_certificate": child_certificate,
                            "certificate_depth": depth,
                            "target": list(target),
                            "target_raw_total": target_total,
                            "raw_delta": target_total - source_floor,
                        }
                    )
        children.sort(key=lambda item: (item[0], item[1], item[2]))
        frontier = [(child, certificate) for _, _, child, certificate in children[: args.beam]]
        depth_stats.append(
            {
                "depth": depth,
                "generated": len(children),
                "retained": len(frontier),
                "best_delta": children[0][0][0] if children else None,
                "best_image_total": children[0][1] if children else None,
            }
        )
        print(json.dumps(depth_stats[-1]), flush=True)
        if records or not frontier:
            break

    payload = {
        "depth_limit": args.depth,
        "beam": args.beam,
        "max_image_total": args.max_image_total,
        "distinct_states": len(seen),
        "depth_stats": depth_stats,
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
