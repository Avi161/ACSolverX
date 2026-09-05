#!/usr/bin/env python3
"""Evaluate the three coordinate-four local seams from the frozen raw manifest."""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.stable_ac import depth4_period_two_five_direction_obstruction_certificate as five
from experiments.stable_ac import depth4_period_two_remote_syzygy_certificate as remote


MANIFEST = ROOT / ".scratch/period_two_diagonal_pure_p_raw_manifest.json"
EXPECTED_SHA256 = "6f83559c4edfb27575beac7df28a774732a92dd81738656036278da00ddde9ef"
THEORY = ROOT / "literature/proofs/AK3_DEPTH4_PERIOD_TWO_FULL_LIFT_BOUNDARY.md"
THEORY_START = b"### 5.7 Coordinate-four new--new covariance\n"
THEORY_END = b"#### Lemma 5.4 (equal-label chord polarization)\n"
EXPECTED_THEORY_LENGTH = 4618
EXPECTED_THEORY_SHA256 = "749ab9456dc3fb2adce711baaa757151c3dddd5f37f9ca29246f0615f792ff8c"
EXPECTED_CELLS = ("e0_n0", "e0_n1", "e0_n2", "e0_nge3")
EXPECTED_OCCURRENCES = (1, 6, 9, 14, 15, 16)
EXPECTED_OCCURRENCE_COUNTS = {1: 9, 6: 9, 9: 15, 14: 15, 15: 18, 16: 18}
EXPECTED_SLOT_PROFILE = {2: 9, 3: 15, 4: 18}
EXPECTED_OCCURRENCES_BY_SLOT = {2: {1, 6}, 3: {9, 14}, 4: {15, 16}}

C = (0, 2, 1)
T = (1, 0, 2)
LETTER_ACTION = {"c": C, "t": T, "T": T}
ALPHABET = {"c": five.lift.C, "t": five.lift.T, "T": -five.lift.T}


def exact_theory_section() -> bytes:
    data = THEORY.read_bytes()
    assert data.count(THEORY_START) == 1
    assert data.count(THEORY_END) == 1
    start = data.index(THEORY_START) + len(THEORY_START)
    end = data.index(THEORY_END)
    assert start <= end
    return data[start:end]


def point(word: str, start: int = 0) -> int:
    assert set(word) <= set(ALPHABET)
    value = start
    for letter in reversed(word):
        value = LETTER_ACTION[letter][value]
    parsed = tuple(ALPHABET[letter] for letter in word)
    assert value == remote.point_image(parsed, start, C, T)
    return value


def observable_weight(observable: dict[str, object]) -> int:
    central = observable["central_label"]
    first_half = observable["first_half_labels"]
    assert isinstance(central, str)
    assert isinstance(first_half, list)
    central_point = point(central)
    return sum(point(label) != central_point for label in first_half) % 2


def local_weight(record: dict[str, object]) -> int:
    base = record["base"]
    assert isinstance(base, dict)
    return observable_weight(base)


def main() -> None:
    assert five.NEW_THREE_POINT_ACTION == (C, T)
    theory_section = exact_theory_section()
    assert len(theory_section) == EXPECTED_THEORY_LENGTH
    theory_digest = hashlib.sha256(theory_section).hexdigest()
    assert theory_digest == EXPECTED_THEORY_SHA256

    digest = hashlib.sha256(MANIFEST.read_bytes()).hexdigest()
    assert digest == EXPECTED_SHA256, (digest, EXPECTED_SHA256)
    data = json.loads(MANIFEST.read_text())
    assert data["generation_failures"] == []
    cells = data["cell_results"]
    assert tuple(cell["cell"]["id"] for cell in cells) == EXPECTED_CELLS

    identity_word = "cTctttcT" * 3
    assert tuple(point(identity_word, start) for start in range(3)) == (0, 1, 2)

    output_cells: list[dict[str, object]] = []
    totals: list[int] = []
    for cell in cells:
        assert cell["generation_failures"] == []
        records = cell["raw_records"]
        assert len(records) == 84
        assert len({record["id"] for record in records}) == 84
        occurrence_counts = Counter(record["occurrence"] for record in records)
        assert dict(sorted(occurrence_counts.items())) == EXPECTED_OCCURRENCE_COUNTS
        assert set(occurrence_counts) == set(EXPECTED_OCCURRENCES)

        slot_coordinates = Counter()
        coordinate_slots: dict[str, int] = {}
        coordinate_occurrences: defaultdict[str, set[int]] = defaultdict(set)
        for record in records:
            coordinate = record["coordinate_id"]
            slot = record["slot"]
            previous = coordinate_slots.setdefault(coordinate, slot)
            assert previous == slot
            coordinate_occurrences[coordinate].add(record["occurrence"])
        slot_coordinates.update(coordinate_slots.values())
        assert dict(sorted(slot_coordinates.items())) == EXPECTED_SLOT_PROFILE
        assert all(
            coordinate_occurrences[coordinate] == EXPECTED_OCCURRENCES_BY_SLOT[slot]
            for coordinate, slot in coordinate_slots.items()
        )

        if cell["cell"]["id"] == "e0_nge3":
            for record in records:
                pumps = record["pumps"]
                assert isinstance(pumps, list) and len(pumps) == 1
                pump = pumps[0]
                assert pump["horizon_saturated"] is True
                assert pump["base_next_observable_signature_equal"] is True
                assert pump["stable_schema_equality"] is True
                base = record["base"]
                one_step = pump["one_step"]
                assert isinstance(base, dict) and isinstance(one_step, dict)
                assert base["first_half_labels"] == one_step["first_half_labels"]
                assert point(base["central_label"]) == point(one_step["central_label"])
                assert observable_weight(base) == observable_weight(one_step)
        else:
            assert all(record["pumps"] == [] for record in records)

        total = 0
        by_slot: defaultdict[int, int] = defaultdict(int)
        by_occurrence: defaultdict[int, int] = defaultdict(int)
        by_family: defaultdict[str, int] = defaultdict(int)
        active_ids: list[str] = []
        for record in records:
            weight = local_weight(record)
            total ^= weight
            by_slot[record["slot"]] ^= weight
            by_occurrence[record["occurrence"]] ^= weight
            by_family[record["family"]] ^= weight
            if weight:
                active_ids.append(record["id"])

        totals.append(total)
        output_cells.append(
            {
                "cell": cell["cell"]["id"],
                "base_i": cell["cell"]["base_i"],
                "local_nonzero_slot_bit": total,
                "by_slot": dict(sorted(by_slot.items())),
                "by_occurrence": dict(sorted(by_occurrence.items())),
                "by_family": dict(sorted(by_family.items())),
                "active_record_count": len(active_ids),
                "active_record_ids": active_ids,
            }
        )

    result = {
        "source_manifest_sha256": digest,
        "source_theory_section_sha256": theory_digest,
        "rho4": {"c": [0, 2, 1], "t": [1, 0, 2]},
        "cells": output_cells,
        "cell_bits": totals,
        "seam_bits": [totals[index] ^ totals[index + 1] for index in range(3)],
        "computed_target": "coordinate-four nonzero-slot local bit in four exhaustive cells and its three lower seams",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
