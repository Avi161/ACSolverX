"""Replay witnessed-ACM actions over a CSV of rank-two presentations."""

from __future__ import annotations

import argparse
import csv
import json
from hashlib import sha256
from pathlib import Path
from typing import Callable, Iterable

from experiments.stable_ac.supermoves.certified_acm import (
    ACMSuccessor,
    bounded_acm_successors,
    expand_atomic_moves,
    replay_atomic_moves,
)


OrbitKey = Callable[[tuple[str, str]], tuple[int, tuple[str, str]]]


def census_rows(
    rows: Iterable[dict[str, str]],
    orbit_key: OrbitKey,
    *,
    max_width: int = 3,
    max_conjugator_length: int = 1,
    beam_size: int = 96,
    relator_cap: int = 80,
) -> dict[str, object]:
    records: list[dict[str, object]] = []
    total_actions = 0
    for row in rows:
        source = (row["r1"], row["r2"])
        source_floor, source_rep = orbit_key(source)
        actions: dict[tuple[str, ...], ACMSuccessor] = {}
        for target_index in range(2):
            for successor in bounded_acm_successors(
                source,
                target_index=target_index,
                max_width=max_width,
                max_conjugator_length=max_conjugator_length,
                beam_size=beam_size,
                relator_cap=relator_cap,
            ):
                actions.setdefault(successor.relators, successor)

        first_nonautomorphic = None
        for successor in sorted(actions.values(), key=_action_score):
            moves = expand_atomic_moves(source, successor.certificate)
            if replay_atomic_moves(source, moves) != successor.relators:
                raise AssertionError(f"atomic replay failed for {row['name']}")
            if first_nonautomorphic is None:
                target_floor, target_rep = orbit_key(successor.relators)
                if target_rep != source_rep:
                    first_nonautomorphic = {
                        "target": list(successor.relators),
                        "target_floor": target_floor,
                        "target_representative": list(target_rep),
                        "atomic_bound": successor.atomic_bound,
                        "certificate": {
                            "target_index": successor.certificate.target_index,
                            "source_exponent": successor.certificate.source_exponent,
                            "source_conjugator": successor.certificate.source_conjugator,
                            "factors": [
                                {
                                    "relator_index": factor.relator_index,
                                    "exponent": factor.exponent,
                                    "conjugator": factor.conjugator,
                                }
                                for factor in successor.certificate.factors
                            ],
                        },
                    }
        total_actions += len(actions)
        records.append(
            {
                "name": row["name"],
                "source": list(source),
                "source_floor": source_floor,
                "source_representative": list(source_rep),
                "action_count": len(actions),
                "all_actions_replayed": True,
                "first_nonautomorphic": first_nonautomorphic,
            }
        )

    payload: dict[str, object] = {
        "schema": "aca124-witnessed-acm-v1",
        "bounds": {
            "max_width": max_width,
            "max_conjugator_length": max_conjugator_length,
            "beam_size": beam_size,
            "relator_cap": relator_cap,
        },
        "summary": {
            "class_count": len(records),
            "classes_with_actions": sum(
                record["action_count"] > 0 for record in records
            ),
            "classes_with_nonautomorphic_action": sum(
                record["first_nonautomorphic"] is not None
                for record in records
            ),
            "total_distinct_actions": total_actions,
            "replay_failures": 0,
        },
        "records": records,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["payload_sha256"] = sha256(encoded.encode("utf-8")).hexdigest()
    return payload


def _action_score(successor: ACMSuccessor):
    return (
        sum(len(word) for word in successor.relators),
        successor.atomic_bound,
        successor.relators,
    )


def _load_orbit_key(checker_root: Path) -> OrbitKey:
    import experiments

    package_path = str(checker_root / "experiments")
    if package_path not in experiments.__path__:
        experiments.__path__.append(package_path)
    from experiments.equivalence_classes.lib.autcanon import aut_canon

    def checked(pair: tuple[str, str]):
        floor, representative, _witness = aut_canon(pair)
        return floor, representative

    return checked


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--checker-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--max-width", type=int, default=3)
    parser.add_argument("--max-conjugator-length", type=int, default=1)
    parser.add_argument("--beam-size", type=int, default=96)
    parser.add_argument("--relator-cap", type=int, default=80)
    args = parser.parse_args()

    with args.data.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    payload = census_rows(
        rows,
        _load_orbit_key(args.checker_root),
        max_width=args.max_width,
        max_conjugator_length=args.max_conjugator_length,
        beam_size=args.beam_size,
        relator_cap=args.relator_cap,
    )
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)


if __name__ == "__main__":
    main()
