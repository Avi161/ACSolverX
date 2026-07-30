from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import importlib.util
import io
import json
import os
import re
import sys
import tempfile
import time
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from itertools import product
from pathlib import Path
from typing import Any

TOKEN_COUNT = 84
THRESHOLD_STATES = (0, 1, 2, None)
HISTOGRAM_KEY_FIELDS = (
    "old_occurrence",
    "old_leaf",
    "b_source_class",
    "b_coordinate",
    "equality_exclusion",
    "old_polarity",
    "module_method",
    "module_order",
    "chronology",
    "chronology_order",
    "label_method",
    "label_order",
    "contribution_bit",
)
ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SOURCE_DIGESTS = {
    ".scratch/period_two_raw_stream_manifest_generator.py": "edd1f21fda1665b092447143b30d25e65f8c9a9cf2753a56ceb5da16db150bb1",
    ".scratch/period_two_raw_stream_manifest.json": "824d17adc0bc9b553d722eb627ee60f363451673237e366f6eb869acc6e058dd",
    ".scratch/period_two_inverse_q_companion_checker.py": "37bfcd326951848f2a721e3dabbaa6d65220b5b1109fafb21e4aa403db94d980",
    ".scratch/period_two_inverse_q_companion_manifest.json": "616c7eaa570f0be87a42c1dae17d0301cbe0b0280f52777f926c6504172225d3",
    ".scratch/period_two_new_new_aggregate_checker.py": "e1f8b9f748ca5a6cfeed9f7db7243892bc888a92ab0e096e754fb0d06b9ec650",
    ".scratch/period_two_new_new_aggregate_manifest.json": "39183f77a56915b6f1e135b23b26d1067c1b56f0a4af8b6c09057d9fc477d640",
    ".scratch/period_two_seven_family_covariance_checker.py": "e8946bfef79b4f4c267c20bcd0f82a4776fff56e1087df4854f74cbf5004d164",
    ".scratch/period_two_seven_family_covariance_manifest.json": "a044e99d93ed43e10721c7f3925f0d750f23944f07d4f385f41fe810f1b62894",
    ".scratch/period_two_old_new_cut_selector_theory.md": "8c5cb9898068e34b34ac2871f6ab82fb9db7bad5da4c5df2cacc2c24fd14baa0",
    ".scratch/period_two_old_new_cut_endpoint_potential.md": "856fba47ee4d4dece0698e10a27a916db533c8a119f3ab3f510a74cc143b6911",
    ".scratch/period_two_intact_boundary_pumping_lemma.md": "7833a0d68b8d088a355db0e4cf659291325d05b0ddbac81cb6d410106f361f94",
}
SOURCE_PATHS = tuple(EXPECTED_SOURCE_DIGESTS)
INVERSE_CELL_IDS = (
    "a0_n0",
    "a0_n1",
    "a0_nge2",
    "a1_n0",
    "a1_n1",
    "a1_nge2",
    "age2_n0",
    "age2_n1",
    "age2_nge2",
)


class CertificateFailure(RuntimeError):
    pass


@dataclass(frozen=True)
class Cell:
    cell_id: str
    names: tuple[str, ...]
    states: tuple[int | None, ...]
    base_values: tuple[int, ...]


@dataclass(frozen=True)
class HistogramBucket:
    key: tuple[Any, ...]
    count: int
    mask: int


@dataclass(frozen=True)
class SourceContext:
    root: Path
    source_digests: Mapping[str, str]
    manifests: Mapping[str, Mapping[str, Any]]
    modules: Mapping[str, Any]
    raw_rows: tuple[Mapping[str, Any], ...]
    raw_validation: Mapping[str, Any]
    occurrences: Mapping[int, Mapping[str, Any]]


@dataclass(frozen=True)
class TokenRef:
    token_id: str
    family: str
    coefficient: int
    slot: int | None
    occurrence: int | None
    polarity: int | None
    module_schema: str
    label_schema: str
    domain: Mapping[str, Any]
    current_equality: Mapping[str, Any]
    source_members: tuple[str, ...] = ()
    token_index: int | None = None


@dataclass(frozen=True)
class Schema:
    schema_id: str
    variables: tuple[str, ...]
    blocks: tuple[
        tuple[str, tuple[int, ...], tuple[int, ...] | None], ...
    ]


@dataclass(frozen=True)
class PumpingWitness:
    block_name: str
    block_index: int
    core: tuple[int, ...]
    base_copies: int
    slopes: tuple[int, ...]
    split_position: int
    left_copy_id: int
    right_copy_id: int
    left_core_offset: int
    right_core_offset: int

    def to_record(self) -> dict[str, Any]:
        return {
            "block_name": self.block_name,
            "block_index": self.block_index,
            "core": list(self.core),
            "base_copies": self.base_copies,
            "slopes": list(self.slopes),
            "split_position": self.split_position,
            "left_copy_id": self.left_copy_id,
            "right_copy_id": self.right_copy_id,
            "left_core_offset": self.left_core_offset,
            "right_core_offset": self.right_core_offset,
        }


@dataclass(frozen=True)
class ComparisonWitness:
    method: str
    order: int
    difference: tuple[int, ...] = ()
    normalized_blocks: tuple[
        tuple[str, tuple[int, ...], tuple[int, ...] | None], ...
    ] = ()
    prefix_length: tuple[int, ...] = ()
    mismatch_letters: tuple[int, int] = ()

    def to_record(self) -> dict[str, Any]:
        if self.method == "strict_affine_length":
            return {
                "method": self.method,
                "order": self.order,
                "difference": list(self.difference),
            }
        if self.method == "identical_pumped_blocks":
            return {
                "method": self.method,
                "order": self.order,
                "normalized_blocks": _serialize_blocks(
                    self.normalized_blocks
                ),
            }
        if self.method == "fixed_mismatch_after_pumped_prefix":
            return {
                "method": self.method,
                "order": self.order,
                "prefix_length": list(self.prefix_length),
                "mismatch_letters": list(self.mismatch_letters),
            }
        raise ValueError(f"unknown comparison witness method: {self.method}")


@dataclass(frozen=True)
class Template:
    schema_id: str
    canonical_key: Any
    cell_id: str | None = None
    variables: tuple[str, ...] = ()
    blocks: tuple[
        tuple[str, tuple[int, ...], tuple[int, ...] | None], ...
    ] = ()
    tagged_base_word: tuple[tuple[int, tuple[Any, ...]], ...] = ()
    base_word: tuple[int, ...] = ()
    length_affine: tuple[int, ...] = ()
    pumping_witnesses: tuple[PumpingWitness, ...] = ()
    terminal_full_letter: int | None = None
    terminal_c_deleted: bool = False

    def to_record(self) -> dict[str, Any]:
        return {
            "schema_id": self.schema_id,
            "cell_id": self.cell_id,
            "variables": list(self.variables),
            "tagged_base_word": [
                {"letter": letter, "tag": list(tag)}
                for letter, tag in self.tagged_base_word
            ],
            "base_word": list(self.base_word),
            "normalized_blocks": _serialize_blocks(
                _normalize_blocks(self.blocks)
            ),
            "terminal_full_letter": self.terminal_full_letter,
            "terminal_c_deleted": self.terminal_c_deleted,
            "pumping_witnesses": [
                witness.to_record()
                for witness in self.pumping_witnesses
            ],
        }


@dataclass(frozen=True)
class DecoratedSchemaRef:
    module_schema: str | None
    label_schemas: tuple[tuple[int | None, str], ...]


@dataclass(frozen=True)
class Task4FamilyCatalog:
    family: str
    variables: tuple[str, ...]
    cells: tuple[Cell, ...]
    schemas: Mapping[str, Schema]
    old_tokens: tuple[TokenRef, ...]
    b_tokens: tuple[TokenRef, ...]
    old_schema_refs: Mapping[str, DecoratedSchemaRef]
    b_schema_refs: Mapping[str, DecoratedSchemaRef]
    old_footprint_bindings: Mapping[
        str, tuple[Mapping[str, Any], ...]
    ]


@dataclass(frozen=True)
class Task4SchemaCatalog:
    families: Mapping[str, Task4FamilyCatalog]
    dependency_digests: Mapping[str, str]
    old_source_proof: Mapping[str, Any]
    b_source_proof: Mapping[str, Any]
    occurrence_leafs: Mapping[int, int]
    occurrence_polarities: Mapping[int, int]
    occurrence_slots: Mapping[int, int]
    fixed_metadata: Mapping[str, Mapping[str, Any]]
    chronology_digest: str
    b_identity_table: tuple[Mapping[str, Any], ...]
    b_identity_digest: str


@dataclass(frozen=True)
class CollisionFiber:
    collision_key: Any
    member_ids: tuple[str, ...]
    coefficients: tuple[int, ...]
    integral_sum: int
    parity: int
    label_equality_witness: Mapping[str, Any]
    active: bool


def _eval_affine(affine: tuple[int, ...], point: tuple[int, ...]) -> int:
    if len(affine) != len(point) + 1:
        raise ValueError("affine dimension differs from its point")
    return sum(
        coefficient * value
        for coefficient, value in zip(affine[:-1], point)
    ) + affine[-1]


def _inverse_letter(letter: int, c_letter: int) -> int:
    return c_letter if abs(letter) == c_letter else -letter


def _validate_core(core: tuple[int, ...], c_letter: int) -> None:
    if not core:
        raise ValueError("powered core must be nonempty")
    normalized = tuple(c_letter if abs(letter) == c_letter else letter for letter in core)
    if normalized != core:
        raise ValueError("powered core must use the normalized order-two letter")
    cyclic_pairs = zip(core, (*core[1:], core[:1]))
    if any(right == _inverse_letter(left, c_letter) for left, right in cyclic_pairs):
        raise ValueError("powered core must be reduced and cyclically reduced")


def _merge_fixed_blocks(
    blocks: Sequence[
        tuple[str, tuple[int, ...], tuple[int, ...] | None]
    ],
) -> tuple[tuple[str, tuple[int, ...], tuple[int, ...] | None], ...]:
    merged: list[tuple[str, tuple[int, ...], tuple[int, ...] | None]] = []
    for block_name, word, affine in blocks:
        if affine is None and not word:
            continue
        if merged and affine is None and merged[-1][2] is None:
            prior_name, prior_word, _ = merged.pop()
            merged.append((prior_name, (*prior_word, *word), None))
        else:
            merged.append((block_name, tuple(word), affine))
    return tuple(merged)


def _normalize_blocks(
    source: Sequence[
        tuple[str, tuple[int, ...], tuple[int, ...] | None]
    ],
) -> tuple[tuple[str, tuple[int, ...], tuple[int, ...] | None], ...]:
    blocks: list[list[Any]] = [
        [name, tuple(word), list(affine) if affine is not None else None]
        for name, word, affine in source
    ]
    for index, block in enumerate(blocks):
        if block[2] is None:
            continue
        core = block[1]
        affine = block[2]
        if index > 0 and blocks[index - 1][2] is None:
            while (
                len(blocks[index - 1][1]) >= len(core)
                and tuple(blocks[index - 1][1][-len(core) :]) == core
            ):
                blocks[index - 1][1] = tuple(
                    blocks[index - 1][1][: -len(core)]
                )
                affine[-1] += 1
        if index + 1 < len(blocks) and blocks[index + 1][2] is None:
            while (
                len(blocks[index + 1][1]) >= len(core)
                and tuple(blocks[index + 1][1][: len(core)]) == core
            ):
                blocks[index + 1][1] = tuple(
                    blocks[index + 1][1][len(core) :]
                )
                affine[-1] += 1
    return _merge_fixed_blocks(
        (
            str(name),
            tuple(word),
            tuple(affine) if affine is not None else None,
        )
        for name, word, affine in blocks
    )


def _serialize_blocks(
    blocks: Sequence[
        tuple[str, tuple[int, ...], tuple[int, ...] | None]
    ],
) -> list[dict[str, Any]]:
    return [
        {
            "block_name": block_name,
            "word": list(word),
            "affine": list(affine) if affine is not None else None,
        }
        for block_name, word, affine in blocks
    ]


def schema_from_powered(
    powered: Any,
    *,
    variables: Sequence[str],
    q_exponent: Sequence[int],
    p_exponent: Sequence[int],
) -> Schema:
    variable_names = tuple(variables)
    q_affine = tuple(powered.q_multiplier * value for value in q_exponent)
    p_affine = tuple(powered.p_multiplier * value for value in p_exponent)
    if len(q_affine) != len(variable_names) + 1:
        raise ValueError("q exponent has the wrong affine dimension")
    if len(p_affine) != len(variable_names) + 1:
        raise ValueError("p exponent has the wrong affine dimension")
    return Schema(
        schema_id=powered.schema_id,
        variables=variable_names,
        blocks=_merge_fixed_blocks(
            (
                ("fixed", tuple(powered.fixed_0), None),
                ("q", tuple(powered.q_core), q_affine),
                ("fixed", tuple(powered.fixed_1), None),
                ("p", tuple(powered.p_core), p_affine),
                ("fixed", tuple(powered.fixed_2), None),
            )
        ),
    )


def _tagged_reduced_word(
    schema: Schema,
    point: tuple[int, ...],
    c_letter: int,
) -> tuple[tuple[int, tuple[Any, ...]], ...]:
    expanded: list[tuple[int, tuple[Any, ...]]] = []
    for block_index, (block_name, word, affine) in enumerate(schema.blocks):
        if affine is None:
            expanded.extend(
                (letter, ("fixed", block_index, offset))
                for offset, letter in enumerate(word)
            )
            continue
        _validate_core(word, c_letter)
        if len(affine) != len(schema.variables) + 1:
            raise ValueError("powered affine has the wrong dimension")
        if any(coefficient < 0 for coefficient in affine[:-1]):
            raise ValueError("powered affine slopes must be nonnegative")
        copies = _eval_affine(affine, point)
        if copies < 0:
            raise ValueError("powered exponent is negative at the cell base")
        expanded.extend(
            (
                letter,
                (block_name, block_index, copy_index, core_offset),
            )
            for copy_index in range(copies)
            for core_offset, letter in enumerate(word)
        )

    reduced: list[tuple[int, tuple[Any, ...]]] = []
    for raw_letter, tag in expanded:
        letter = c_letter if abs(raw_letter) == c_letter else raw_letter
        if reduced and reduced[-1][0] == _inverse_letter(letter, c_letter):
            reduced.pop()
        else:
            reduced.append((letter, tag))
    return tuple(reduced)


def _retained_word(
    tagged_full: tuple[tuple[int, tuple[Any, ...]], ...],
    c_letter: int,
) -> tuple[tuple[tuple[int, tuple[Any, ...]], ...], int | None, bool]:
    terminal = tagged_full[-1][0] if tagged_full else None
    deleted = terminal == c_letter
    retained = tagged_full[:-1] if deleted else tagged_full
    return retained, terminal, deleted


def _changing_slopes(
    affine: tuple[int, ...], cell: Cell
) -> tuple[int, ...]:
    return tuple(
        coefficient if state is None else 0
        for coefficient, state in zip(affine[:-1], cell.states)
    )


def _find_intact_boundary(
    tagged: Sequence[tuple[int, tuple[Any, ...]]],
    block_name: str,
    block_index: int,
    core_length: int,
) -> tuple[int, int, int] | None:
    for split in range(1, len(tagged)):
        left = tagged[split - 1][1]
        right = tagged[split][1]
        if (
            len(left) == 4
            and len(right) == 4
            and left[0] == right[0] == block_name
            and left[1] == right[1] == block_index
            and left[3] == core_length - 1
            and right[3] == 0
            and right[2] == left[2] + 1
        ):
            return split, int(left[2]), int(right[2])
    return None


def build_template(
    schema: Schema,
    cell: Cell,
    *,
    c_letter: int = 1,
) -> Template:
    if schema.variables != cell.names:
        raise ValueError("schema variables differ from cell variables")
    tagged_full = _tagged_reduced_word(schema, cell.base_values, c_letter)
    tagged_base, terminal, terminal_c_deleted = _retained_word(
        tagged_full, c_letter
    )
    base_word = tuple(letter for letter, _ in tagged_base)
    insertions: list[
        tuple[PumpingWitness, tuple[int, ...]]
    ] = []
    for block_index, (block_name, core, affine) in enumerate(schema.blocks):
        if affine is None:
            continue
        slopes = _changing_slopes(affine, cell)
        if not any(slopes):
            continue
        boundary = _find_intact_boundary(
            tagged_base, block_name, block_index, len(core)
        )
        if boundary is None:
            raise ValueError(
                "missing intact boundary: "
                f"{schema.schema_id}, {cell.cell_id}, {block_name}"
            )
        split, left_copy, right_copy = boundary
        witness = PumpingWitness(
            block_name=block_name,
            block_index=block_index,
            core=core,
            base_copies=_eval_affine(affine, cell.base_values),
            slopes=slopes,
            split_position=split,
            left_copy_id=left_copy,
            right_copy_id=right_copy,
            left_core_offset=len(core) - 1,
            right_core_offset=0,
        )
        delta_affine = (
            *slopes,
            -sum(
                coefficient * value
                for coefficient, value in zip(slopes, cell.base_values)
            ),
        )
        insertions.append((witness, delta_affine))
    insertions.sort(key=lambda item: item[0].split_position)
    splits = [item[0].split_position for item in insertions]
    if len(set(splits)) != len(splits):
        raise ValueError("coincident intact boundaries")

    pumped_blocks: list[
        tuple[str, tuple[int, ...], tuple[int, ...] | None]
    ] = []
    cursor = 0
    for witness, delta_affine in insertions:
        pumped_blocks.append(
            ("fixed", base_word[cursor : witness.split_position], None)
        )
        pumped_blocks.append(
            (witness.block_name, witness.core, delta_affine)
        )
        cursor = witness.split_position
    pumped_blocks.append(("fixed", base_word[cursor:], None))
    blocks = _merge_fixed_blocks(pumped_blocks)
    coefficients = tuple(
        sum(
            len(word) * affine[axis]
            for _, word, affine in blocks
            if affine is not None
        )
        for axis in range(len(schema.variables))
    )
    length_affine = (
        *coefficients,
        len(base_word)
        - sum(
            coefficient * value
            for coefficient, value in zip(coefficients, cell.base_values)
        ),
    )
    normalized = _normalize_blocks(blocks)
    template = Template(
        schema_id=schema.schema_id,
        canonical_key=normalized,
        cell_id=cell.cell_id,
        variables=schema.variables,
        blocks=blocks,
        tagged_base_word=tagged_base,
        base_word=base_word,
        length_affine=length_affine,
        pumping_witnesses=tuple(item[0] for item in insertions),
        terminal_full_letter=terminal,
        terminal_c_deleted=terminal_c_deleted,
    )
    verify_intact_boundaries(schema, cell, template, c_letter=c_letter)
    return template


def verify_template_record(
    schema: Schema,
    cell: Cell,
    record: Mapping[str, Any],
    *,
    c_letter: int = 1,
) -> Template:
    template = build_template(schema, cell, c_letter=c_letter)
    if canonical_json(record) != canonical_json(template.to_record()):
        raise ValueError(
            f"template proof record differs: {schema.schema_id}, {cell.cell_id}"
        )
    return template


def expand_template(template: Template, point: tuple[int, ...]) -> tuple[int, ...]:
    if len(point) != len(template.variables):
        raise ValueError("template point has the wrong dimension")
    output: list[int] = []
    for _, word, affine in template.blocks:
        if affine is None:
            output.extend(word)
            continue
        copies = _eval_affine(affine, point)
        if copies < 0:
            raise ValueError("template expansion has a negative copy count")
        output.extend(word * copies)
    return tuple(output)


def verify_intact_boundaries(
    schema: Schema,
    cell: Cell,
    template: Template,
    *,
    c_letter: int = 1,
) -> tuple[PumpingWitness, ...]:
    splits = [
        witness.split_position for witness in template.pumping_witnesses
    ]
    if len(set(splits)) != len(splits):
        raise ValueError("coincident intact boundaries")
    tagged_full = _tagged_reduced_word(schema, cell.base_values, c_letter)
    tagged_base, terminal, terminal_c_deleted = _retained_word(
        tagged_full, c_letter
    )
    if (
        terminal != template.terminal_full_letter
        or terminal_c_deleted != template.terminal_c_deleted
    ):
        raise ValueError("terminal-c branch changed")
    if tagged_base != template.tagged_base_word:
        raise ValueError("tagged fully reduced base word changed")
    if tuple(letter for letter, _ in tagged_base) != template.base_word:
        raise ValueError("fully reduced base word changed")

    changing_blocks = []
    for block_index, (block_name, core, affine) in enumerate(schema.blocks):
        if affine is None:
            continue
        slopes = _changing_slopes(affine, cell)
        if any(slopes):
            changing_blocks.append((block_index, block_name, core, affine, slopes))
    if len(changing_blocks) != len(template.pumping_witnesses):
        raise ValueError("missing intact boundary witness")

    witnesses_by_block = {
        witness.block_index: witness
        for witness in template.pumping_witnesses
    }
    for block_index, block_name, core, affine, slopes in changing_blocks:
        witness = witnesses_by_block.get(block_index)
        if witness is None:
            raise ValueError("missing intact boundary witness")
        if not 0 < witness.split_position < len(tagged_base):
            raise ValueError("pumping insertion is not internal to retained word")
        left = tagged_base[witness.split_position - 1][1]
        right = tagged_base[witness.split_position][1]
        expected = PumpingWitness(
            block_name=block_name,
            block_index=block_index,
            core=core,
            base_copies=_eval_affine(affine, cell.base_values),
            slopes=slopes,
            split_position=witness.split_position,
            left_copy_id=int(left[2]) if len(left) == 4 else -1,
            right_copy_id=int(right[2]) if len(right) == 4 else -1,
            left_core_offset=len(core) - 1,
            right_core_offset=0,
        )
        if witness != expected or _find_intact_boundary(
            tagged_base,
            block_name,
            block_index,
            len(core),
        ) != (
            witness.split_position,
            witness.left_copy_id,
            witness.right_copy_id,
        ):
            raise ValueError("invalid intact boundary witness")

    if expand_template(template, cell.base_values) != template.base_word:
        raise ValueError("base template expansion differs from reduction")
    for axis, state in enumerate(cell.states):
        if state is not None:
            continue
        point = list(cell.base_values)
        point[axis] += 1
        point_tuple = tuple(point)
        incremented_full = _tagged_reduced_word(schema, point_tuple, c_letter)
        incremented, incremented_terminal, incremented_deleted = _retained_word(
            incremented_full, c_letter
        )
        if (
            incremented_terminal != terminal
            or incremented_deleted != terminal_c_deleted
        ):
            raise ValueError("terminal-c branch changed after pumping")
        if expand_template(template, point_tuple) != tuple(
            letter for letter, _ in incremented
        ):
            raise ValueError("one-copy pumping differs from direct reduction")
    return template.pumping_witnesses


def _prefix_witness(
    template: Template,
    point: tuple[int, ...],
    position: int,
) -> tuple[
    tuple[tuple[str, tuple[int, ...], tuple[int, ...] | None], ...],
    tuple[int, ...],
    int,
]:
    cursor = 0
    for index, (block_name, word, affine) in enumerate(template.blocks):
        length = len(word) if affine is None else len(word) * _eval_affine(
            affine, point
        )
        if position >= cursor + length:
            cursor += length
            continue
        if affine is not None:
            raise ValueError("mismatch lies inside powered block")
        offset = position - cursor
        prefix = _normalize_blocks(
            (*template.blocks[:index], ("fixed", word[:offset], None))
        )
        coefficients = tuple(
            sum(
                len(prefix_word) * prefix_affine[axis]
                for _, prefix_word, prefix_affine in prefix
                if prefix_affine is not None
            )
            for axis in range(len(template.variables))
        )
        constant = sum(
            len(prefix_word)
            if prefix_affine is None
            else len(prefix_word) * prefix_affine[-1]
            for _, prefix_word, prefix_affine in prefix
        )
        return prefix, (*coefficients, constant), word[offset]
    raise ValueError("first mismatch is outside the template")


def _affine_sign_on_cell(
    difference: tuple[int, ...], cell: Cell
) -> int | None:
    base_value = _eval_affine(difference, cell.base_values)
    changing = tuple(
        coefficient
        for coefficient, state in zip(difference[:-1], cell.states)
        if state is None
    )
    if all(coefficient == 0 for coefficient in changing):
        return -1 if base_value < 0 else 1 if base_value > 0 else 0
    if base_value > 0 and all(coefficient >= 0 for coefficient in changing):
        return 1
    if base_value < 0 and all(coefficient <= 0 for coefficient in changing):
        return -1
    return None


def compare_templates(
    left: Template,
    right: Template,
    cell: Cell,
) -> dict[str, Any]:
    if left.cell_id != cell.cell_id or right.cell_id != cell.cell_id:
        raise ValueError("comparison templates differ from the cell")
    if left.variables != cell.names or right.variables != cell.names:
        raise ValueError("comparison variables differ from the cell")
    if len(left.length_affine) != len(right.length_affine):
        raise ValueError("comparison affine dimensions differ")
    difference = tuple(
        left_value - right_value
        for left_value, right_value in zip(
            left.length_affine, right.length_affine
        )
    )
    sign = _affine_sign_on_cell(difference, cell)
    if sign is None:
        raise ValueError("affine length difference has no fixed strict sign")
    if sign:
        return ComparisonWitness(
            method="strict_affine_length",
            order=sign,
            difference=difference,
        ).to_record()

    left_normalized = _normalize_blocks(left.blocks)
    right_normalized = _normalize_blocks(right.blocks)
    if left_normalized == right_normalized:
        return ComparisonWitness(
            method="identical_pumped_blocks",
            order=0,
            normalized_blocks=left_normalized,
        ).to_record()

    mismatch = next(
        (
            (position, left_letter, right_letter)
            for position, (left_letter, right_letter) in enumerate(
                zip(left.base_word, right.base_word)
            )
            if left_letter != right_letter
        ),
        None,
    )
    if mismatch is None:
        raise ValueError("equal base words have different normalized pumps")
    position, left_letter, right_letter = mismatch
    left_prefix, left_length, witnessed_left = _prefix_witness(
        left, cell.base_values, position
    )
    right_prefix, right_length, witnessed_right = _prefix_witness(
        right, cell.base_values, position
    )
    if left_prefix != right_prefix or left_length != right_length:
        raise ValueError("pumped prefixes before fixed mismatch differ")
    if (witnessed_left, witnessed_right) != (left_letter, right_letter):
        raise ValueError("fixed mismatch letters changed")
    return ComparisonWitness(
        method="fixed_mismatch_after_pumped_prefix",
        order=-1 if left_letter < right_letter else 1,
        prefix_length=left_length,
        mismatch_letters=(left_letter, right_letter),
    ).to_record()


def comparison_record(
    old: Mapping[str, Any],
    new: Mapping[str, Any],
    templates: Mapping[str, Template],
    cell: Cell,
    *,
    comparison_cache: dict[tuple[str, str, str], Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    def compare(left_schema: str, right_schema: str) -> Mapping[str, Any]:
        key = (left_schema, right_schema, cell.cell_id)
        if comparison_cache is not None and key in comparison_cache:
            return comparison_cache[key]
        result = compare_templates(
            templates[left_schema], templates[right_schema], cell
        )
        if comparison_cache is not None:
            comparison_cache[key] = result
        return result

    label_comparison = compare(old["label_schema"], new["label_schema"])
    module_comparison = None
    equality_exclusion = False
    if old["occurrence"] is None:
        chronology_order = -1 if old["leaf"] < new["leaf"] else 1
        chronology = "fixed_vs_correction_literal_leaf_order"
    elif old["occurrence"] != new["occurrence"]:
        chronology_order = -1 if old["leaf"] < new["leaf"] else 1
        chronology = "distinct_occurrences_literal_AST_order"
    else:
        if old["module_schema"] is None or new["module_schema"] is None:
            raise ValueError("same-occurrence correction lacks module schema")
        module_comparison = compare(
            old["module_schema"], new["module_schema"]
        )
        if module_comparison["order"] == 0:
            equality_exclusion = True
            chronology_order = 0
            chronology = "equal_coordinate_excluded"
        else:
            if old["polarity"] != new["polarity"]:
                raise ValueError("same occurrence has inconsistent polarity")
            chronology_order = old["polarity"] * module_comparison["order"]
            chronology = (
                "same_occurrence_increasing"
                if old["polarity"] == 1
                else "same_occurrence_decreasing"
            )
    return {
        "token_index": new["token_index"],
        "old_occurrence": old["occurrence"],
        "old_leaf": old["leaf"],
        "b_source_class": new["source_class"],
        "b_coordinate": new["coordinate"],
        "equality_exclusion": equality_exclusion,
        "old_polarity": old["polarity"],
        "module_method": (
            None if module_comparison is None else module_comparison["method"]
        ),
        "module_order": (
            None if module_comparison is None else module_comparison["order"]
        ),
        "chronology": chronology,
        "chronology_order": chronology_order,
        "label_method": label_comparison["method"],
        "label_order": label_comparison["order"],
        "contribution_bit": int(
            not equality_exclusion
            and label_comparison["order"] == chronology_order
        ),
    }


def _hashable_histogram_key(value: Any) -> Any:
    if isinstance(value, Mapping):
        return tuple(
            (key, _hashable_histogram_key(item))
            for key, item in sorted(value.items())
        )
    if isinstance(value, (list, tuple)):
        return tuple(_hashable_histogram_key(item) for item in value)
    return value


def _sortable_histogram_key(value: Any) -> Any:
    if value is None:
        return (0, "")
    if isinstance(value, bool):
        return (1, int(value))
    if isinstance(value, int):
        return (2, value)
    if isinstance(value, str):
        return (3, value)
    if isinstance(value, (list, tuple)):
        return (4, tuple(_sortable_histogram_key(item) for item in value))
    if isinstance(value, Mapping):
        return (
            5,
            tuple(
                (key, _sortable_histogram_key(item))
                for key, item in sorted(value.items())
            ),
        )
    raise ValueError(f"unsupported histogram key value: {type(value).__name__}")


def validate_histogram(histogram: Mapping[str, Any]) -> Mapping[str, Any]:
    buckets = histogram["buckets"]
    union = 0
    decoded = []
    for bucket in buckets:
        mask_hex = bucket["mask"]
        if (
            not isinstance(mask_hex, str)
            or len(mask_hex) != 21
            or any(letter not in "0123456789abcdef" for letter in mask_hex)
        ):
            raise CertificateFailure("histogram mask is not 21 lowercase hex digits")
        mask = int(mask_hex, 16)
        if union & mask:
            raise CertificateFailure("histogram masks overlap")
        union |= mask
        decoded.append((bucket, mask))
        key = bucket["key"]
        if key["old_occurrence"] != histogram["old_occurrence"]:
            raise CertificateFailure("histogram old occurrence differs from key")
        if key["old_leaf"] != histogram["old_leaf"]:
            raise CertificateFailure("histogram old leaf differs from key")
        if key["old_polarity"] != histogram["old_polarity"]:
            raise CertificateFailure("histogram old polarity differs from key")
    if union != (1 << TOKEN_COUNT) - 1:
        raise CertificateFailure("histogram masks do not cover all 84 tokens")
    if histogram["comparison_count"] != TOKEN_COUNT:
        raise CertificateFailure("histogram comparison count differs from 84")
    if sum(bucket["count"] for bucket, _ in decoded) != TOKEN_COUNT:
        raise CertificateFailure("histogram bucket counts do not sum to 84")
    if any(
        bucket["count"]
        != bin(mask).count("1")  # noqa: FURB161 - Python 3.9
        for bucket, mask in decoded
    ):
        raise CertificateFailure("histogram count differs from mask population")
    one_count = sum(
        bucket["count"] * bucket["key"]["contribution_bit"]
        for bucket, _ in decoded
    )
    if histogram["one_count"] != one_count:
        raise CertificateFailure("histogram one count differs from buckets")
    if histogram["value"] != one_count % 2:
        raise CertificateFailure("histogram value differs from one-count parity")
    return histogram


def histogram_for_load(
    old: Mapping[str, Any],
    new_tokens: Sequence[Mapping[str, Any]],
    templates: Mapping[str, Template],
    cell: Cell,
    *,
    comparison_cache: dict[tuple[str, str, str], Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    records = tuple(
        comparison_record(
            old,
            new,
            templates,
            cell,
            comparison_cache=comparison_cache,
        )
        for new in new_tokens
    )
    grouped: dict[Any, list[Any]] = {}
    seen_indices = set()
    for record in records:
        token_index = record["token_index"]
        if token_index in seen_indices:
            raise ValueError(f"duplicate token_index: {token_index}")
        if not 0 <= token_index < TOKEN_COUNT:
            raise ValueError("token_index must be in 0..83")
        seen_indices.add(token_index)
        key = tuple(record[field] for field in HISTOGRAM_KEY_FIELDS)
        hashable_key = _hashable_histogram_key(key)
        if hashable_key not in grouped:
            grouped[hashable_key] = [key, 0, 0]
        grouped[hashable_key][1] += 1
        grouped[hashable_key][2] |= 1 << token_index
    if seen_indices != set(range(TOKEN_COUNT)):
        raise ValueError("token indices must cover 0..83 exactly")
    buckets = tuple(
        HistogramBucket(key=key, count=count, mask=mask)
        for key, count, mask in sorted(
            grouped.values(), key=lambda row: _sortable_histogram_key(row[0])
        )
    )
    one_count = sum(record["contribution_bit"] for record in records)
    histogram = {
        "old_occurrence": old["occurrence"],
        "old_leaf": old["leaf"],
        "old_polarity": old["polarity"],
        "comparison_count": len(records),
        "one_count": one_count,
        "value": one_count % 2,
        "buckets": [
            {
                "key": dict(zip(HISTOGRAM_KEY_FIELDS, bucket.key)),
                "count": bucket.count,
                "mask": f"{bucket.mask:021x}",
            }
            for bucket in buckets
        ],
    }
    return dict(validate_histogram(histogram))


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True)


def _canonical_bytes(value: Any) -> bytes:
    return (canonical_json(value) + "\n").encode("ascii")


def _project_local_path(path: Path) -> Path:
    resolved = path.resolve()
    root = ROOT.resolve()
    if resolved != root and root not in resolved.parents:
        raise CertificateFailure(f"manifest path is outside the project: {path}")
    return resolved


def _atomic_write(path: Path, payload: bytes) -> None:
    target = _project_local_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=target.parent,
            prefix=f".{target.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(payload)
            handle.flush()
        temporary.replace(target)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the grouped old--new cut load certificate."
    )
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", type=Path, metavar="PATH")
    action.add_argument("--check", type=Path, metavar="PATH")
    action.add_argument("--summary", action="store_true")
    arguments = parser.parse_args(argv)

    manifest = build_manifest()
    payload = _canonical_bytes(manifest)
    if arguments.write is not None:
        _atomic_write(arguments.write, payload)
    elif arguments.check is not None:
        target = _project_local_path(arguments.check)
        if not target.is_file() or target.read_bytes() != payload:
            raise CertificateFailure(f"canonical manifest differs: {target}")
    else:
        print(
            canonical_json(
                {"status": manifest["status"], "summary": manifest["summary"]}
            )
        )
    return 0


def _sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load source module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _validate_raw_rows(
    raw: Any, source_schema: Mapping[str, Any]
) -> tuple[tuple[Mapping[str, Any], ...], dict[str, Any]]:
    _, live_v_rows = raw.build_v_rows()
    _, live_w_rows = raw.build_w_rows()
    _, live_anchor_rows = raw.build_anchor_rows()
    groups = {
        "V": (live_v_rows, source_schema["V_rows"], 167),
        "W": (live_w_rows, source_schema["W_rows"], 397),
        "A": (live_anchor_rows, source_schema["anchor_rows"], 21),
    }
    for family, (live_rows, bound_rows, expected_count) in groups.items():
        if len(live_rows) != expected_count or len(bound_rows) != expected_count:
            raise ValueError(f"{family} row count differs from approved source")
        if canonical_json(live_rows) != canonical_json(bound_rows):
            raise ValueError(f"live {family} rows differ from bound raw manifest")

    raw_rows = tuple(
        row
        for family in ("V", "W", "A")
        for row in groups[family][1]
    )
    row_ids = [row["id"] for row in raw_rows]
    if len(set(row_ids)) != len(row_ids):
        raise ValueError("duplicate raw row IDs")
    for row in raw_rows:
        coefficient = row.get("coefficient")
        if isinstance(coefficient, bool) or not isinstance(coefficient, int):
            raise ValueError(  # noqa: TRY004 - uniform source-validation failure
                f"raw row has non-integer coefficient: {row.get('id')}"
            )
        if not row.get("domain") or not row.get("current_equality"):
            raise ValueError(f"raw row lacks typed provenance: {row.get('id')}")
    family_counts = {
        family: sum(row["family"] == family for row in raw_rows)
        for family in ("V", "W", "A")
    }
    expected_counts = {"V": 167, "W": 397, "A": 21}
    if family_counts != expected_counts:
        raise ValueError(f"raw row family counts differ: {family_counts}")
    return raw_rows, {
        "family_counts": family_counts,
        "ids_unique": True,
        "rows": len(raw_rows),
    }


def load_source_context() -> SourceContext:
    source_digests: dict[str, str] = {}
    for relative_path in SOURCE_PATHS:
        path = ROOT / relative_path
        if not path.is_file():
            raise FileNotFoundError(path)
        digest = _sha256_path(path)
        if digest != EXPECTED_SOURCE_DIGESTS[relative_path]:
            raise ValueError(f"approved source digest mismatch: {relative_path}")
        source_digests[relative_path] = digest

    manifest_paths = {
        "raw": ".scratch/period_two_raw_stream_manifest.json",
        "inverse": ".scratch/period_two_inverse_q_companion_manifest.json",
        "aggregate": ".scratch/period_two_new_new_aggregate_manifest.json",
        "seven": ".scratch/period_two_seven_family_covariance_manifest.json",
    }
    manifests = {
        name: json.loads((ROOT / relative_path).read_text())
        for name, relative_path in manifest_paths.items()
    }
    if manifests["raw"]["verdict"]["bridge_A_to_C"] != "proved":
        raise ValueError("raw source bridge is not proved")
    if manifests["inverse"]["collision_partition_proof"]["failures"] != 0:
        raise ValueError("inverse-Q collision partition has failures")
    for name in ("aggregate", "seven"):
        checks = manifests[name]["checks"]
        failure_counts = [value for key, value in checks.items() if key.endswith("failures")]
        if any(failure_counts):
            raise ValueError(f"{name} source contains failed checks")

    modules = {
        "raw": _load_module(
            "old_new_bound_raw_generator",
            ROOT / ".scratch/period_two_raw_stream_manifest_generator.py",
        ),
        "inverse": _load_module(
            "old_new_bound_inverse_checker",
            ROOT / ".scratch/period_two_inverse_q_companion_checker.py",
        ),
        "aggregate": _load_module(
            "old_new_bound_aggregate_checker",
            ROOT / ".scratch/period_two_new_new_aggregate_checker.py",
        ),
        "seven": _load_module(
            "old_new_bound_seven_checker",
            ROOT / ".scratch/period_two_seven_family_covariance_checker.py",
        ),
    }
    source_schema = manifests["raw"]["source_schema_manifest"]
    raw_rows, raw_validation = _validate_raw_rows(modules["raw"], source_schema)
    occurrence_rows = manifests["raw"]["typed_ast_query_manifest"]["occurrences"]
    occurrences = {row["order"]: row for row in occurrence_rows}
    if set(occurrences) != set(range(1, 17)):
        raise ValueError("raw occurrence order must cover 1..16")
    return SourceContext(
        root=ROOT,
        source_digests=dict(sorted(source_digests.items())),
        manifests=manifests,
        modules=modules,
        raw_rows=raw_rows,
        raw_validation=raw_validation,
        occurrences=occurrences,
    )


def aggregate_integral_fibers(
    rows: Sequence[TokenRef],
    templates: Mapping[tuple[str, str], Template],
    cell: Cell,
) -> tuple[CollisionFiber, ...]:
    grouped: dict[str, tuple[Any, list[tuple[TokenRef, Any]]]] = {}
    for row in rows:
        module_template = templates[(row.module_schema, cell.cell_id)]
        label_template = templates[(row.label_schema, cell.cell_id)]
        collision_key = (row.slot, module_template.canonical_key)
        serialized_key = canonical_json(collision_key)
        if serialized_key not in grouped:
            grouped[serialized_key] = (collision_key, [])
        grouped[serialized_key][1].append((row, label_template.canonical_key))

    fibers = []
    for serialized_key in sorted(grouped):
        collision_key, entries = grouped[serialized_key]
        entries.sort(key=lambda item: item[0].token_id)
        representative_label = canonical_json(entries[0][1])
        label_members = []
        for row, label_key in entries:
            serialized_label = canonical_json(label_key)
            label_members.append(
                {"member": row.token_id, "label_key": serialized_label}
            )
            if serialized_label != representative_label:
                raise ValueError(
                    "equal canonical module keys have unequal transported labels: "
                    f"{entries[0][0].token_id}, {row.token_id}"
                )
        member_ids = tuple(row.token_id for row, _ in entries)
        coefficients = tuple(row.coefficient for row, _ in entries)
        integral_sum = sum(coefficients)
        parity = integral_sum % 2
        fibers.append(
            CollisionFiber(
                collision_key=collision_key,
                member_ids=member_ids,
                coefficients=coefficients,
                integral_sum=integral_sum,
                parity=parity,
                label_equality_witness={
                    "equal": True,
                    "representative_label_key": representative_label,
                    "members": label_members,
                },
                active=parity != 0,
            )
        )
    return tuple(fibers)


def build_b_catalog(
    context: SourceContext,
) -> tuple[tuple[TokenRef, ...], dict[str, Any]]:
    inverse_manifest = context.manifests["inverse"]
    source_cell = "a0_n0"
    collision_cells = inverse_manifest["collision_fibers"]
    if set(collision_cells) != set(INVERSE_CELL_IDS):
        raise ValueError(
            "exact inverse-Q cell IDs required: "
            f"expected {list(INVERSE_CELL_IDS)}, got {sorted(collision_cells)}"
        )
    coefficient_copies: dict[str, set[int]] = {}
    for record in inverse_manifest["records"]:
        indices = record["indices"]
        member_id = (
            f"nu{indices['nu']}:k{indices['k']}:delta{indices['delta']}"
        )
        coefficient_copies.setdefault(member_id, set()).add(
            record["integral_coefficient"]
        )
    inconsistent_members = [
        member_id
        for member_id, coefficients in coefficient_copies.items()
        if len(coefficients) != 1
    ]
    if inconsistent_members:
        raise ValueError(
            f"occurrence copies disagree on coefficient: {inconsistent_members}"
        )
    record_coefficients = {
        member_id: next(iter(coefficients))
        for member_id, coefficients in coefficient_copies.items()
    }

    def integer_fiber_values(
        fiber: Mapping[str, Any],
    ) -> tuple[tuple[int, ...], int, int]:
        members = tuple(sorted(fiber["members"]))
        coefficients = tuple(record_coefficients[member] for member in members)
        integral_sum = sum(coefficients)
        if integral_sum != fiber["integral_coefficient_sum"]:
            raise ValueError(f"integer-first B sum mismatch: {fiber['members']}")
        parity = integral_sum % 2
        if parity != fiber["activity_parity"]:
            raise ValueError(f"integer-first B parity mismatch: {fiber['members']}")
        return coefficients, integral_sum, parity

    def delta_zero_fibers(fibers: Sequence[Mapping[str, Any]]) -> list[Any]:
        return [
            fiber
            for fiber in fibers
            if all(member.endswith(":delta0") for member in fiber["members"])
        ]

    delta_fibers = delta_zero_fibers(collision_cells[source_cell])
    stable_signature = canonical_json(
        [
            {
                "members": sorted(fiber["members"]),
                "integral_sum": integer_fiber_values(fiber)[1],
                "parity": integer_fiber_values(fiber)[2],
                "canonical_module_schema": fiber["canonical_module_schema"],
                "slot": fiber["slot"],
            }
            for fiber in delta_fibers
        ]
    )
    unstable_cells = [
        cell_id
        for cell_id in INVERSE_CELL_IDS
        for fibers in (collision_cells[cell_id],)
        if canonical_json(
            [
                {
                    "members": sorted(fiber["members"]),
                    "integral_sum": integer_fiber_values(fiber)[1],
                    "parity": integer_fiber_values(fiber)[2],
                    "canonical_module_schema": fiber["canonical_module_schema"],
                    "slot": fiber["slot"],
                }
                for fiber in delta_zero_fibers(fibers)
            ]
        )
        != stable_signature
    ]
    if unstable_cells:
        raise ValueError(f"B collision catalog changes across cells: {unstable_cells}")
    if len(delta_fibers) != 53:
        raise ValueError("bound inverse-Q source does not contain 53 delta0 fibers")
    active_fibers = [
        fiber for fiber in delta_fibers if integer_fiber_values(fiber)[2]
    ]
    if len(active_fibers) != 36:
        raise ValueError("bound inverse-Q source does not contain 36 active fibers")

    tokens = []
    true_domain = {"op": "true"}
    inverse = context.modules["inverse"]
    label_templates, label_metadata = inverse.build_templates(context.modules["raw"])
    if set(label_metadata) != {
        member_id.rsplit(":", 1)[0]
        for member_id in record_coefficients
        if member_id.endswith(":delta0")
    }:
        raise ValueError("B label metadata does not cover the delta0 source rows")
    slot_zero_occurrences = (3, 4, 7, 8, 11, 12)
    for corner in ("00", "01"):
        for occurrence in slot_zero_occurrences:
            occurrence_row = context.occurrences[occurrence]
            tokens.append(
                TokenRef(
                    token_id=f"b0:g0:{corner}:o{occurrence}",
                    family="b_slot_zero",
                    coefficient=1,
                    slot=occurrence_row["slot"],
                    occurrence=occurrence,
                    polarity=occurrence_row["polarity"],
                    module_schema=f"g0:{corner}:module",
                    label_schema=f"g0:{corner}:action:o{occurrence}",
                    domain=true_domain,
                    current_equality={
                        "op": "bound_g_zero_schema",
                        "corner": corner,
                    },
                    source_members=(f"g0:{corner}",),
                )
            )

    occurrences_by_slot = {2: (1, 6), 3: (9, 14), 4: (15, 16)}

    def member_label_witness(
        fiber: Mapping[str, Any], members: tuple[str, ...]
    ) -> dict[str, Any]:
        checks = []
        for occurrence in occurrences_by_slot[fiber["slot"]]:
            for cell_id in INVERSE_CELL_IDS:
                member_labels = []
                for member_id in members:
                    row_key = member_id.removesuffix(":delta0")
                    label_schema = (
                        f"partner:action:{row_key}:delta0:o{occurrence}"
                    )
                    template_key = (label_schema, cell_id)
                    if template_key not in label_templates:
                        raise ValueError(f"missing B member label: {template_key}")
                    label_key = canonical_json(
                        inverse.canonical_blocks(label_templates[template_key])
                    )
                    member_labels.append(
                        {
                            "member": member_id,
                            "label_schema": label_schema,
                            "label_key": label_key,
                        }
                    )
                if len({item["label_key"] for item in member_labels}) != 1:
                    raise ValueError(
                        "equal canonical module keys have unequal transported labels: "
                        f"{members}, occurrence {occurrence}, cell {cell_id}"
                    )
                checks.append(
                    {
                        "occurrence": occurrence,
                        "cell": cell_id,
                        "members": member_labels,
                    }
                )
        return {
            "equal": True,
            "method": "canonical_member_action_blocks_all_inverse_cells",
            "checks": checks,
        }

    collision_records = []
    for fiber_index, fiber in enumerate(delta_fibers):
        members = tuple(sorted(fiber["members"]))
        coefficients, integral_sum, parity = integer_fiber_values(fiber)
        label_equality_witness = member_label_witness(fiber, members)
        collision_records.append(
            {
                "members": list(members),
                "coefficients": list(coefficients),
                "member_coefficients": [
                    [member, coefficient]
                    for member, coefficient in zip(members, coefficients)
                ],
                "integral_sum": integral_sum,
                "parity": parity,
                "active": parity != 0,
                "canonical_module_schema": fiber["canonical_module_schema"],
                "slot": fiber["slot"],
                "label_equality_witness": label_equality_witness,
            }
        )
        if not parity:
            continue
        representative = members[0]
        row_key = representative.removesuffix(":delta0")
        for occurrence in occurrences_by_slot[fiber["slot"]]:
            occurrence_row = context.occurrences[occurrence]
            tokens.append(
                TokenRef(
                    token_id=f"b0:path:f{fiber_index:03d}:o{occurrence}",
                    family="b_path",
                    coefficient=integral_sum,
                    slot=fiber["slot"],
                    occurrence=occurrence,
                    polarity=occurrence_row["polarity"],
                    module_schema=fiber["canonical_module_schema"],
                    label_schema=(
                        f"partner:action:{row_key}:delta0:o{occurrence}"
                    ),
                    domain=true_domain,
                    current_equality={
                        "op": "bound_collision_fiber",
                        "source_cell": source_cell,
                        "members": list(members),
                    },
                    source_members=members,
                )
            )

    tokens.sort(key=lambda token: token.token_id)
    indexed_tokens = tuple(
        replace(token, token_index=index) for index, token in enumerate(tokens)
    )
    if len(indexed_tokens) != TOKEN_COUNT:
        raise ValueError(f"expected 84 B tokens, got {len(indexed_tokens)}")
    if {token.token_index for token in indexed_tokens} != set(range(TOKEN_COUNT)):
        raise ValueError("B token indices do not cover 0..83")
    return indexed_tokens, {
        "occurrences": len(context.occurrences),
        "path_fibers": len(delta_fibers),
        "active_path_fibers": len(active_fibers),
        "slot_zero_tokens": 2 * len(slot_zero_occurrences),
        "bound_cells": len(INVERSE_CELL_IDS),
        "collision_fibers": collision_records,
        "source_digests": dict(context.source_digests),
    }


def _source_collision_fibers(
    rows: Sequence[Mapping[str, Any]], family: str
) -> tuple[tuple[TokenRef, ...], list[dict[str, Any]]]:
    grouped: dict[str, list[Mapping[str, Any]]] = {}
    collision_keys: dict[str, Any] = {}
    for row in rows:
        collision_key = (row["key"]["slot"], row["module_vertex"])
        serialized_key = canonical_json(collision_key)
        grouped.setdefault(serialized_key, []).append(row)
        collision_keys[serialized_key] = collision_key

    active_rows = []
    fiber_records = []
    for fiber_index, serialized_key in enumerate(sorted(grouped)):
        members = sorted(grouped[serialized_key], key=lambda row: row["id"])
        coefficients = tuple(row["coefficient"] for row in members)
        integral_sum = sum(coefficients)
        parity = integral_sum % 2
        member_ids = tuple(row["id"] for row in members)
        representative = members[0]
        fiber_records.append(
            {
                "collision_key": collision_keys[serialized_key],
                "member_ids": list(member_ids),
                "coefficients": list(coefficients),
                "members": [
                    {
                        "id": row["id"],
                        "coefficient": row["coefficient"],
                        "domain": row["domain"],
                        "current_equality": row["current_equality"],
                    }
                    for row in members
                ],
                "integral_sum": integral_sum,
                "parity": parity,
                "active": parity != 0,
                "label_equality_witness": {
                    "equal": True,
                    "method": "identical_typed_module_expression_then_same_slot_action",
                },
            }
        )
        if not parity:
            continue
        active_rows.append(
            TokenRef(
                token_id=f"old:{family}:f{fiber_index:03d}",
                family=family,
                coefficient=integral_sum,
                slot=representative["key"]["slot"],
                occurrence=None,
                polarity=None,
                module_schema=f"old:{family}:f{fiber_index:03d}:module",
                label_schema=f"old:{family}:f{fiber_index:03d}:action",
                domain=representative["domain"],
                current_equality={
                    "op": "integral_collision_fiber",
                    "rows": [row["current_equality"] for row in members],
                },
                source_members=member_ids,
            )
        )
    return tuple(active_rows), fiber_records


def _base_collision_fibers(
    rows: Sequence[Mapping[str, Any]],
) -> tuple[tuple[TokenRef, ...], list[dict[str, Any]]]:
    active_rows = []
    fiber_records = []
    for fiber_index, row in enumerate(sorted(rows, key=lambda item: item["id"])):
        coefficient = row["coefficient"]
        parity = coefficient % 2
        fiber_records.append(
            {
                "collision_key": (row["slot"], row["module_vertex"]),
                "member_ids": [row["id"]],
                "coefficients": [coefficient],
                "members": [
                    {
                        "id": row["id"],
                        "coefficient": coefficient,
                        "domain": row["domain"],
                        "current_equality": {
                            "op": "literal_hessian_base_variable",
                            "source": row["id"],
                        },
                    }
                ],
                "integral_sum": coefficient,
                "parity": parity,
                "active": parity != 0,
                "label_equality_witness": {"equal": True, "method": "singleton"},
            }
        )
        if parity:
            active_rows.append(
                TokenRef(
                    token_id=f"old:base:f{fiber_index:03d}",
                    family="base",
                    coefficient=coefficient,
                    slot=row["slot"],
                    occurrence=None,
                    polarity=None,
                    module_schema=f"base:{fiber_index}:module",
                    label_schema=f"base:{fiber_index}:action",
                    domain=row["domain"],
                    current_equality={
                        "op": "literal_hessian_base_variable",
                        "source": row["id"],
                    },
                    source_members=(row["id"],),
                )
            )
    return tuple(active_rows), fiber_records


def build_old_rows(
    context: SourceContext,
) -> tuple[tuple[TokenRef, ...], dict[str, Any]]:
    raw = context.modules["raw"]
    source_schema = context.manifests["raw"]["source_schema_manifest"]
    _, raw_validation = _validate_raw_rows(raw, source_schema)
    _, live_w_rows = raw.build_w_rows()
    if canonical_json(live_w_rows) != canonical_json(source_schema["W_rows"]):
        raise ValueError("live W rows differ from bound raw manifest")
    _, live_anchor_rows = raw.build_anchor_rows()
    if canonical_json(live_anchor_rows) != canonical_json(source_schema["anchor_rows"]):
        raise ValueError("live anchor rows differ from bound raw manifest")
    live_atoms = raw.singleton_and_base_atoms()
    if canonical_json(live_atoms["base_correction_atoms"]) != canonical_json(
        source_schema["base_correction_atoms"]
    ):
        raise ValueError("live Hessian base atoms differ from bound raw manifest")

    fixed_rows = tuple(
        TokenRef(
            token_id=f"old:{token.token_id}",
            family="fixed",
            coefficient=1,
            slot=None,
            occurrence=None,
            polarity=None,
            module_schema=f"fixed:module:{token.token_id}",
            label_schema=f"fixed:label:{token.token_id}",
            domain={"op": "true"},
            current_equality={
                "op": "fixed_literal_token",
                "coordinate": list(token.coordinate),
            },
            source_members=(token.token_id,),
        )
        for token in context.modules["seven"].fixed_tokens()
    )
    if len(fixed_rows) != 70:
        raise ValueError(f"expected 70 fixed rows, got {len(fixed_rows)}")

    base_rows, base_fibers = _base_collision_fibers(
        source_schema["base_correction_atoms"]
    )
    singleton_rows = (
        TokenRef(
            token_id="old:singleton:g0:00",
            family="singleton",
            coefficient=1,
            slot=0,
            occurrence=None,
            polarity=None,
            module_schema="g0:00:module",
            label_schema="g0:00:module",
            domain={"op": "and", "args": [{"op": "ge", "name": "a", "value": 0}, {"op": "ge", "name": "n", "value": 0}]},
            current_equality={
                "op": "bound_g_zero_slot_zero_footprint",
                "source": "g0:00",
            },
            source_members=("g0:00",),
        ),
    )

    family_sources = {
        "P": [row for row in live_w_rows if row["key"]["block"] == "P"],
        "C": [row for row in live_w_rows if row["key"]["block"] == "C"],
        "Q": [
            row
            for row in live_w_rows
            if row["key"]["block"] == "Q" and row["key"]["orientation"] == 1
        ],
    }
    family_rows = {}
    family_fibers = {}
    for family, rows in family_sources.items():
        family_rows[family], family_fibers[family] = _source_collision_fibers(
            rows, family
        )

    missing_provenance = [
        row["id"]
        for row in tuple(source_schema["V_rows"])
        + tuple(source_schema["W_rows"])
        + tuple(source_schema["anchor_rows"])
        if not row.get("domain") or not row.get("current_equality")
    ]
    old_rows = (
        *fixed_rows,
        *base_rows,
        *singleton_rows,
        *family_rows["P"],
        *family_rows["C"],
        *family_rows["Q"],
    )

    def one_member_source_record(token: TokenRef) -> dict[str, Any]:
        if len(token.source_members) != 1:
            raise ValueError(
                f"one-member source has wrong member count: {token.token_id}"
            )
        return {
            "identity": token.token_id,
            "member_id": token.source_members[0],
            "coefficient": token.coefficient,
            "domain": token.domain,
            "current_equality": token.current_equality,
        }

    proof = {
        "raw_family_rows": {
            family: len(rows) for family, rows in family_sources.items()
        },
        "active_family_fibers": {
            "fixed": len(fixed_rows),
            "base": len(base_rows),
            "singleton": len(singleton_rows),
            "P": len(family_rows["P"]),
            "C": len(family_rows["C"]),
            "Q": len(family_rows["Q"]),
        },
        "integral_fibers": {
            "base": base_fibers,
            "P": family_fibers["P"],
            "C": family_fibers["C"],
            "Q": family_fibers["Q"],
        },
        "one_member_sources": {
            "fixed": [
                one_member_source_record(token) for token in fixed_rows
            ],
            "singleton": [
                one_member_source_record(token) for token in singleton_rows
            ],
        },
        "anchor_rows": len(live_anchor_rows),
        "anchor_integral_sum": sum(
            row["coefficient"] for row in live_anchor_rows
        ),
        "anchor_provenance": [
            {"id": row["id"], "coefficient": row["coefficient"]}
            for row in live_anchor_rows
        ],
        "missing_raw_provenance": missing_provenance,
        "raw_provenance_counts": raw_validation["family_counts"],
        "raw_ids_unique": raw_validation["ids_unique"],
        "source_digests": dict(context.source_digests),
    }
    return tuple(old_rows), proof


def _fixed_schema(
    schema_id: str,
    variables: tuple[str, ...],
    word: Sequence[int],
) -> Schema:
    return Schema(
        schema_id=schema_id,
        variables=variables,
        blocks=(("fixed", tuple(word), None),),
    )


def _prepend_action(
    schema: Schema,
    schema_id: str,
    action: Sequence[int],
) -> Schema:
    blocks = list(schema.blocks)
    if blocks and blocks[0][2] is None:
        block_name, word, _ = blocks[0]
        blocks[0] = (block_name, (*tuple(action), *word), None)
    else:
        blocks.insert(0, ("fixed", tuple(action), None))
    return Schema(schema_id, schema.variables, _merge_fixed_blocks(blocks))


def _one_power_schema(
    inverse: Any,
    raw: Any,
    schema_id: str,
    variables: tuple[str, ...],
    left: Sequence[int],
    power_word: tuple[int, ...],
    right: Sequence[int],
    exponent: tuple[int, ...],
    reference: tuple[int, ...],
) -> Schema:
    power_left, core, multiplier, power_right = (
        inverse.reference_primitive_decomposition(
            raw, power_word, reference
        )
    )
    return Schema(
        schema_id=schema_id,
        variables=variables,
        blocks=_merge_fixed_blocks(
            (
                ("fixed", (*tuple(left), *power_left), None),
                (
                    "p",
                    core,
                    tuple(multiplier * value for value in exponent),
                ),
                ("fixed", (*power_right, *tuple(right)), None),
            )
        ),
    )


def _two_power_schema(
    inverse: Any,
    raw: Any,
    schema_id: str,
    variables: tuple[str, ...],
    left: Sequence[int],
    q_word: tuple[int, ...],
    middle: Sequence[int],
    p_word: tuple[int, ...],
    right: Sequence[int],
    q_exponent: tuple[int, ...],
    p_exponent: tuple[int, ...],
    q_reference: tuple[int, ...],
    p_reference: tuple[int, ...],
) -> Schema:
    q_left, q_core, q_multiplier, q_right = (
        inverse.reference_primitive_decomposition(
            raw, q_word, q_reference
        )
    )
    p_left, p_core, p_multiplier, p_right = (
        inverse.reference_primitive_decomposition(
            raw, p_word, p_reference
        )
    )
    return Schema(
        schema_id=schema_id,
        variables=variables,
        blocks=_merge_fixed_blocks(
            (
                ("fixed", (*tuple(left), *q_left), None),
                (
                    "q",
                    q_core,
                    tuple(q_multiplier * value for value in q_exponent),
                ),
                ("fixed", (*q_right, *tuple(middle), *p_left), None),
                (
                    "p",
                    p_core,
                    tuple(p_multiplier * value for value in p_exponent),
                ),
                ("fixed", (*p_right, *tuple(right)), None),
            )
        ),
    )


def _powered_substitution(
    variables: tuple[str, ...], p_offset: int
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    if variables == ("a", "n"):
        return (1, 0, 0), (1, 1, p_offset)
    if variables == ("a", "h", "r"):
        return (1, 0, 0, 0), (0, 1, 1, p_offset)
    if variables == ("h", "k", "n"):
        return (1, 1, 0, 0), (1, 1, 1, p_offset)
    raise ValueError(f"unsupported Task 4 variable basis: {variables}")


def _occurrences_for_slot(
    context: SourceContext, slot: int
) -> tuple[int, ...]:
    return tuple(
        order
        for order, occurrence in sorted(context.occurrences.items())
        if occurrence["slot"] == slot
    )


def _old_path_schema(
    context: SourceContext,
    inverse: Any,
    family: str,
    variables: tuple[str, ...],
    source_row: Mapping[str, Any],
    schema_id: str,
    action: tuple[int, ...],
) -> Schema:
    raw = context.modules["raw"]
    key = source_row["key"]
    nu = key["nu"]
    position = key["position"]
    p_forest, c_forest, q_forest = raw.BLOCKS[nu - 1]
    p_word = raw.eval_path(p_forest)
    c_word = raw.eval_path(c_forest)
    q_word = raw.eval_path(q_forest)
    root = raw.parse_raw(raw.W_ROOTS[nu - 1])
    multiplier = raw.edge_rule(source_row["actual_letter"])[2]
    gamma = raw.eval_path(raw.BLOCKS[0][2])
    common_p = raw.eval_path(raw.BLOCKS[0][0])
    gamma_reference, gamma_multiplier = inverse.primitive_power(gamma)
    p_reference, p_multiplier = inverse.primitive_power(common_p)
    if gamma_multiplier != 3 or p_multiplier != 3:
        raise ValueError("approved primitive multiplier changed")

    if family == "P":
        return _one_power_schema(
            inverse,
            raw,
            schema_id,
            variables,
            (*action, *multiplier, *raw.eval_path(p_forest[:position])),
            p_word,
            root,
            (0, 1, 0, 0),
            p_reference,
        )
    if family == "C":
        return _one_power_schema(
            inverse,
            raw,
            schema_id,
            variables,
            (*action, *multiplier, *raw.eval_path(c_forest[:position])),
            p_word,
            root,
            (1, 1, 1),
            p_reference,
        )
    if family == "Q":
        return _two_power_schema(
            inverse,
            raw,
            schema_id,
            variables,
            (*action, *multiplier, *raw.eval_path(q_forest[:position])),
            q_word,
            c_word,
            p_word,
            root,
            (1, 0, 0, 0),
            (1, 1, 1, 1),
            gamma_reference,
            p_reference,
        )
    raise ValueError(f"not a path family: {family}")


def _build_old_family_schemas(
    context: SourceContext,
    family: str,
    variables: tuple[str, ...],
    tokens: tuple[TokenRef, ...],
    powered_sources: Mapping[str, Any],
) -> tuple[dict[str, Schema], dict[str, DecoratedSchemaRef]]:
    raw = context.modules["raw"]
    inverse = context.modules["inverse"]
    seven = context.modules["seven"]
    source_rows = {row["id"]: row for row in context.raw_rows}
    base_rows = {
        row["id"]: row
        for row in context.manifests["raw"]["source_schema_manifest"][
            "base_correction_atoms"
        ]
    }
    fixed_tokens = {token.token_id: token for token in seven.fixed_tokens()}
    schemas: dict[str, Schema] = {}
    references: dict[str, DecoratedSchemaRef] = {}
    for token in tokens:
        if family == "fixed":
            source_id = token.source_members[0]
            schema_id = f"{family}:old:{token.token_id}:label"
            schemas[schema_id] = _fixed_schema(
                schema_id, variables, fixed_tokens[source_id].label
            )
            references[token.token_id] = DecoratedSchemaRef(
                module_schema=None,
                label_schemas=((None, schema_id),),
            )
            continue

        module_id = f"{family}:old:{token.token_id}:module"
        label_ids = []
        if token.slot is None:
            raise ValueError(f"old token lacks slot: {token.token_id}")
        occurrences = _occurrences_for_slot(context, token.slot)
        if not occurrences:
            raise ValueError(
                f"old token slot lacks occurrences: {token.token_id}"
            )

        if family == "base":
            source = base_rows[token.source_members[0]]
            word = raw.parse_raw(source["module_vertex"])
            schemas[module_id] = _fixed_schema(module_id, variables, word)
            for occurrence in occurrences:
                label_id = f"{family}:old:{token.token_id}:label:o{occurrence}"
                action = raw.parse_raw(
                    context.occurrences[occurrence]["quotient_prefix"]
                )
                schemas[label_id] = _fixed_schema(
                    label_id, variables, (*action, *word)
                )
                label_ids.append((occurrence, label_id))
        elif family == "singleton":
            source = powered_sources["g0:00:module"]
            q_exponent, p_exponent = _powered_substitution(
                variables, source.p_offset
            )
            base_schema = replace(
                schema_from_powered(
                    source,
                    variables=variables,
                    q_exponent=q_exponent,
                    p_exponent=p_exponent,
                ),
                schema_id=module_id,
            )
            schemas[module_id] = base_schema
            for occurrence in occurrences:
                label_id = f"{family}:old:{token.token_id}:label:o{occurrence}"
                action = raw.parse_raw(
                    context.occurrences[occurrence]["quotient_prefix"]
                )
                schemas[label_id] = _prepend_action(
                    base_schema, label_id, action
                )
                label_ids.append((occurrence, label_id))
        else:
            representative = source_rows[token.source_members[0]]
            schemas[module_id] = _old_path_schema(
                context,
                inverse,
                family,
                variables,
                representative,
                module_id,
                (),
            )
            for occurrence in occurrences:
                label_id = f"{family}:old:{token.token_id}:label:o{occurrence}"
                action = raw.parse_raw(
                    context.occurrences[occurrence]["quotient_prefix"]
                )
                schemas[label_id] = _old_path_schema(
                    context,
                    inverse,
                    family,
                    variables,
                    representative,
                    label_id,
                    action,
                )
                label_ids.append((occurrence, label_id))
        references[token.token_id] = DecoratedSchemaRef(
            module_schema=module_id,
            label_schemas=tuple(label_ids),
        )
    return schemas, references


def _build_b_family_schemas(
    family: str,
    variables: tuple[str, ...],
    tokens: tuple[TokenRef, ...],
    powered_sources: Mapping[str, Any],
) -> tuple[dict[str, Schema], dict[str, DecoratedSchemaRef]]:
    schemas: dict[str, Schema] = {}
    references: dict[str, DecoratedSchemaRef] = {}
    for token in tokens:
        if token.occurrence is None:
            raise ValueError(f"B token lacks occurrence: {token.token_id}")
        resolved = []
        for role, source_id in (
            ("module", token.module_schema),
            ("label", token.label_schema),
        ):
            source = powered_sources[source_id]
            schema_id = f"{family}:b:{source_id}"
            q_exponent, p_exponent = _powered_substitution(
                variables, source.p_offset
            )
            schema = replace(
                schema_from_powered(
                    source,
                    variables=variables,
                    q_exponent=q_exponent,
                    p_exponent=p_exponent,
                ),
                schema_id=schema_id,
            )
            prior = schemas.setdefault(schema_id, schema)
            if prior != schema:
                raise ValueError(f"inconsistent B {role} schema: {schema_id}")
            resolved.append(schema_id)
        references[token.token_id] = DecoratedSchemaRef(
            module_schema=resolved[0],
            label_schemas=((token.occurrence, resolved[1]),),
        )
    return schemas, references


def _task4_chronology_metadata(
    context: SourceContext,
) -> tuple[
    dict[int, int],
    dict[int, int],
    dict[int, int],
    dict[str, dict[str, Any]],
]:
    seven = context.modules["seven"]
    occurrence_leafs = {}
    occurrence = 0
    for leaf_index, leaf in enumerate(
        seven.hessian._expand(seven.hessian._residual_ast()), start=1
    ):
        if leaf.literal is not None:
            continue
        occurrence += 1
        occurrence_leafs[occurrence] = leaf_index
    if set(occurrence_leafs) != set(context.occurrences):
        raise ValueError("AST occurrence leaves do not cover 1..16")
    occurrence_polarities = {
        order: row["polarity"] for order, row in context.occurrences.items()
    }
    occurrence_slots = {
        order: row["slot"] for order, row in context.occurrences.items()
    }
    fixed_metadata = {
        f"old:{token.token_id}": {
            "leaf": token.leaf,
            "coordinate": list(token.coordinate),
        }
        for token in seven.fixed_tokens()
    }
    if len(fixed_metadata) != 70:
        raise ValueError("fixed chronology metadata does not contain 70 tokens")
    return (
        occurrence_leafs,
        occurrence_polarities,
        occurrence_slots,
        fixed_metadata,
    )


def _old_footprint_bindings(
    context: SourceContext,
    tokens: Sequence[TokenRef],
    references: Mapping[str, DecoratedSchemaRef],
    occurrence_leafs: Mapping[int, int],
    occurrence_polarities: Mapping[int, int],
    fixed_metadata: Mapping[str, Mapping[str, Any]],
) -> dict[str, tuple[dict[str, Any], ...]]:
    bindings = {}
    for token in tokens:
        reference = references[token.token_id]
        entries = []
        for occurrence, label_schema in reference.label_schemas:
            if occurrence is None:
                metadata = fixed_metadata.get(token.token_id)
                if metadata is None or token.slot is not None:
                    raise CertificateFailure(
                        f"invalid fixed footprint source: {token.token_id}"
                    )
                occurrence_slot = None
                polarity = None
                leaf = metadata["leaf"]
            else:
                occurrence_row = context.occurrences.get(occurrence)
                if occurrence_row is None or occurrence_row["slot"] != token.slot:
                    raise CertificateFailure(
                        f"old footprint occurrence has wrong slot: {token.token_id}"
                    )
                occurrence_slot = occurrence_row["slot"]
                polarity = occurrence_polarities[occurrence]
                leaf = occurrence_leafs[occurrence]
            entries.append(
                {
                    "token_id": token.token_id,
                    "source_slot": token.slot,
                    "source_members": list(token.source_members),
                    "module_schema": reference.module_schema,
                    "occurrence": occurrence,
                    "occurrence_slot": occurrence_slot,
                    "polarity": polarity,
                    "leaf": leaf,
                    "label_schema": label_schema,
                }
            )
        bindings[token.token_id] = tuple(entries)
    return bindings


def _chronology_digest(
    occurrence_leafs: Mapping[int, int],
    occurrence_polarities: Mapping[int, int],
    occurrence_slots: Mapping[int, int],
    fixed_metadata: Mapping[str, Mapping[str, Any]],
) -> str:
    payload = canonical_json(
        {
            "occurrence_leafs": dict(occurrence_leafs),
            "occurrence_polarities": dict(occurrence_polarities),
            "occurrence_slots": dict(occurrence_slots),
            "fixed_metadata": dict(fixed_metadata),
        }
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def _b_identity_table(
    tokens: Sequence[TokenRef],
) -> tuple[dict[str, Any], ...]:
    if len(tokens) != TOKEN_COUNT:
        raise CertificateFailure(f"expected 84 B tokens, got {len(tokens)}")
    token_ids = [token.token_id for token in tokens]
    if len(set(token_ids)) != TOKEN_COUNT:
        raise CertificateFailure("duplicate B token ID")
    token_indices = [token.token_index for token in tokens]
    if set(token_indices) != set(range(TOKEN_COUNT)):
        raise CertificateFailure("B token indices do not cover 0..83 exactly")
    return tuple(
        {
            "token_index": token.token_index,
            "token_id": token.token_id,
            "source_class": token.family,
            "coefficient": token.coefficient,
            "slot": token.slot,
            "occurrence": token.occurrence,
            "polarity": token.polarity,
            "module_schema": token.module_schema,
            "label_schema": token.label_schema,
            "source_members": list(token.source_members),
        }
        for token in sorted(tokens, key=lambda item: item.token_index)
    )


def _identity_digest(table: Sequence[Mapping[str, Any]]) -> str:
    return hashlib.sha256(canonical_json(table).encode("ascii")).hexdigest()


SOURCE_BINDINGS_FORMAT = "task4-source-bindings-v1"
SOURCE_BINDING_FIELDS = {"format", "old", "b", "sha256"}
OLD_SOURCE_PROOF_FIELDS = {
    "raw_family_rows",
    "active_family_fibers",
    "integral_fibers",
    "one_member_sources",
    "anchor_rows",
    "anchor_integral_sum",
    "anchor_provenance",
    "missing_raw_provenance",
    "raw_provenance_counts",
    "raw_ids_unique",
    "source_digests",
}
B_SOURCE_PROOF_FIELDS = {
    "occurrences",
    "path_fibers",
    "active_path_fibers",
    "slot_zero_tokens",
    "bound_cells",
    "collision_fibers",
    "source_digests",
}
OLD_FIBER_FIELDS = {
    "collision_key",
    "member_ids",
    "coefficients",
    "members",
    "integral_sum",
    "parity",
    "active",
    "label_equality_witness",
}
B_FIBER_FIELDS = {
    "members",
    "coefficients",
    "member_coefficients",
    "integral_sum",
    "parity",
    "active",
    "canonical_module_schema",
    "slot",
    "label_equality_witness",
}
SOURCE_MEMBER_FIELDS = {
    "id",
    "coefficient",
    "domain",
    "current_equality",
}
ONE_MEMBER_SOURCE_FIELDS = {
    "identity",
    "member_id",
    "coefficient",
    "domain",
    "current_equality",
}


def _is_exact_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_source_member(member: Mapping[str, Any]) -> None:
    if set(member) != SOURCE_MEMBER_FIELDS:
        raise CertificateFailure("old source member fields differ")
    if not isinstance(member["id"], str) or not member["id"]:
        raise CertificateFailure("old source member identity is invalid")
    if not _is_exact_integer(member["coefficient"]):
        raise CertificateFailure("old source member coefficient is not integer")
    if not isinstance(member["domain"], Mapping) or not member["domain"]:
        raise CertificateFailure("old source member domain is missing")
    if (
        not isinstance(member["current_equality"], Mapping)
        or not member["current_equality"]
    ):
        raise CertificateFailure("old source member equality is missing")


def _validate_old_source_proof(proof: Mapping[str, Any]) -> None:
    if set(proof) != OLD_SOURCE_PROOF_FIELDS:
        raise CertificateFailure("old source proof fields differ")
    fibers_by_family = proof["integral_fibers"]
    if set(fibers_by_family) != {"base", "P", "C", "Q"}:
        raise CertificateFailure("old integral-fiber families differ")
    for fibers in fibers_by_family.values():
        for fiber in fibers:
            if set(fiber) != OLD_FIBER_FIELDS:
                raise CertificateFailure("old integral-fiber fields differ")
            members = fiber["members"]
            for member in members:
                _validate_source_member(member)
            member_ids = [member["id"] for member in members]
            coefficients = [member["coefficient"] for member in members]
            if fiber["member_ids"] != member_ids:
                raise CertificateFailure("old member identity alignment differs")
            if fiber["coefficients"] != coefficients:
                raise CertificateFailure("old member coefficient alignment differs")
            if not coefficients or not all(
                _is_exact_integer(coefficient) for coefficient in coefficients
            ):
                raise CertificateFailure("old fiber coefficients are invalid")
            if fiber["integral_sum"] != sum(coefficients):
                raise CertificateFailure("old integral fiber sum differs")
            if fiber["parity"] != fiber["integral_sum"] % 2:
                raise CertificateFailure("old integral fiber parity differs")
            if fiber["active"] is not bool(fiber["parity"]):
                raise CertificateFailure("old integral fiber activity differs")
            if fiber["label_equality_witness"].get("equal") is not True:
                raise CertificateFailure("old fiber label equality is missing")
    one_member_sources = proof["one_member_sources"]
    if set(one_member_sources) != {"fixed", "singleton"}:
        raise CertificateFailure("one-member source families differ")
    expected_counts = {"fixed": 70, "singleton": 1}
    for family, records in one_member_sources.items():
        if len(records) != expected_counts[family]:
            raise CertificateFailure("one-member source count differs")
        identities = []
        for record in records:
            if set(record) != ONE_MEMBER_SOURCE_FIELDS:
                raise CertificateFailure("one-member source fields differ")
            identities.append(record["identity"])
            if not record["identity"] or not record["member_id"]:
                raise CertificateFailure("one-member source identity is invalid")
            if not _is_exact_integer(record["coefficient"]):
                raise CertificateFailure("one-member coefficient is invalid")
            if not record["domain"] or not record["current_equality"]:
                raise CertificateFailure("one-member provenance is missing")
        if len(set(identities)) != len(identities):
            raise CertificateFailure("one-member source identities repeat")
    anchor_rows = proof["anchor_provenance"]
    if proof["anchor_rows"] != 21 or len(anchor_rows) != 21:
        raise CertificateFailure("anchor provenance count differs")
    if any(set(row) != {"id", "coefficient"} for row in anchor_rows):
        raise CertificateFailure("anchor provenance fields differ")
    if any(
        not row["id"] or not _is_exact_integer(row["coefficient"])
        for row in anchor_rows
    ):
        raise CertificateFailure("anchor provenance row is invalid")
    if len({row["id"] for row in anchor_rows}) != len(anchor_rows):
        raise CertificateFailure("anchor provenance identities repeat")
    if proof["anchor_integral_sum"] != sum(
        row["coefficient"] for row in anchor_rows
    ):
        raise CertificateFailure("anchor integral sum differs")
    if proof["raw_provenance_counts"] != {"V": 167, "W": 397, "A": 21}:
        raise CertificateFailure("raw provenance counts differ")
    if proof["raw_ids_unique"] is not True:
        raise CertificateFailure("raw provenance identities are not unique")
    if proof["missing_raw_provenance"] != []:
        raise CertificateFailure("raw provenance is missing")


def _validate_b_source_proof(proof: Mapping[str, Any]) -> None:
    if set(proof) != B_SOURCE_PROOF_FIELDS:
        raise CertificateFailure("B source proof fields differ")
    fibers = proof["collision_fibers"]
    if proof["path_fibers"] != 53 or len(fibers) != 53:
        raise CertificateFailure("B collision-fiber count differs")
    for fiber in fibers:
        if set(fiber) != B_FIBER_FIELDS:
            raise CertificateFailure("B collision-fiber fields differ")
        members = fiber["members"]
        coefficients = fiber["coefficients"]
        if members != sorted(members) or not members:
            raise CertificateFailure("B collision members are noncanonical")
        if not all(
            _is_exact_integer(coefficient) for coefficient in coefficients
        ):
            raise CertificateFailure("B collision coefficients are invalid")
        if fiber["member_coefficients"] != [
            [member, coefficient]
            for member, coefficient in zip(members, coefficients)
        ]:
            raise CertificateFailure("B member coefficient alignment differs")
        if len(members) != len(coefficients):
            raise CertificateFailure("B member coefficient lengths differ")
        if fiber["integral_sum"] != sum(coefficients):
            raise CertificateFailure("B integral fiber sum differs")
        if fiber["parity"] != fiber["integral_sum"] % 2:
            raise CertificateFailure("B integral fiber parity differs")
        if fiber["active"] is not bool(fiber["parity"]):
            raise CertificateFailure("B integral fiber activity differs")
        if not _is_exact_integer(fiber["slot"]):
            raise CertificateFailure("B collision slot is invalid")
        if not fiber["canonical_module_schema"]:
            raise CertificateFailure("B module schema is missing")
        if fiber["label_equality_witness"].get("equal") is not True:
            raise CertificateFailure("B label equality witness is missing")


def build_source_bindings(catalog: Task4SchemaCatalog) -> dict[str, Any]:
    payload = copy.deepcopy(
        {
            "format": SOURCE_BINDINGS_FORMAT,
            "old": catalog.old_source_proof,
            "b": catalog.b_source_proof,
        }
    )
    payload["sha256"] = hashlib.sha256(
        canonical_json(payload).encode("ascii")
    ).hexdigest()
    return payload


def validate_source_bindings(
    source_bindings: Mapping[str, Any], catalog: Task4SchemaCatalog
) -> Mapping[str, Any]:
    if set(source_bindings) != SOURCE_BINDING_FIELDS:
        raise CertificateFailure("source-binding fields differ")
    if source_bindings["format"] != SOURCE_BINDINGS_FORMAT:
        raise CertificateFailure("source-binding format differs")
    _validate_old_source_proof(source_bindings["old"])
    _validate_b_source_proof(source_bindings["b"])
    if canonical_json(source_bindings["old"]["source_digests"]) != canonical_json(
        catalog.dependency_digests
    ):
        raise CertificateFailure("old source digests differ")
    if canonical_json(source_bindings["b"]["source_digests"]) != canonical_json(
        catalog.dependency_digests
    ):
        raise CertificateFailure("B source digests differ")
    payload = {
        key: value for key, value in source_bindings.items() if key != "sha256"
    }
    digest = hashlib.sha256(canonical_json(payload).encode("ascii")).hexdigest()
    if source_bindings["sha256"] != digest:
        raise CertificateFailure("source-binding digest differs")
    expected = build_source_bindings(catalog)
    if canonical_json(source_bindings) != canonical_json(expected):
        raise CertificateFailure("source bindings differ from bound source proofs")
    return source_bindings


TEMPLATE_CATALOG_FORMAT = "task4-template-catalog-v2"
TEMPLATE_TYPED_ENCODING = "task4-typed-sha256-v1"
TEMPLATE_FIELD_ORDERS = {
    "schema": ["schema_id", "variables", "blocks"],
    "block": ["block_name", "word", "affine"],
    "cell": ["cell_id", "names", "states", "base_values"],
    "witness": [
        "terminal_full_letter",
        "terminal_c_deleted",
        "pumps",
    ],
    "pump": [
        "block_index",
        "base_copies",
        "slopes",
        "split_position",
        "left_copy_id",
        "right_copy_id",
        "left_core_offset",
        "right_core_offset",
    ],
}
TEMPLATE_CATALOG_FIELDS = {
    "format",
    "typed_encoding",
    "family",
    "field_orders",
    "identity_order",
    "schema_count",
    "cell_count",
    "template_count",
    "witness_count",
    "schema_table",
    "cell_table",
    "witness_table",
    "identity_witness_ids",
    "identity_sha256",
    "replay_sha256",
    "catalog_sha256",
}


def _typed_encode_into(update: Any, value: Any) -> None:
    if value is None:
        update(b"N")
        return
    if isinstance(value, bool):
        update(b"B\x01" if value else b"B\x00")
        return
    if isinstance(value, int):
        payload = str(value).encode("ascii")
        update(b"I" + len(payload).to_bytes(4, "big") + payload)
        return
    if isinstance(value, str):
        payload = value.encode("utf-8")
        update(b"S" + len(payload).to_bytes(4, "big") + payload)
        return
    if isinstance(value, (list, tuple)):
        update(b"L" + len(value).to_bytes(4, "big"))
        for item in value:
            _typed_encode_into(update, item)
        return
    if isinstance(value, Mapping):
        if not all(isinstance(key, str) for key in value):
            raise TypeError("typed mappings require string keys")
        keys = sorted(value, key=lambda key: key.encode("utf-8"))
        update(b"M" + len(keys).to_bytes(4, "big"))
        for key in keys:
            _typed_encode_into(update, key)
            _typed_encode_into(update, value[key])
        return
    raise TypeError(f"unsupported typed hash value: {type(value).__name__}")


def typed_encode(value: Any) -> bytes:
    payload = bytearray()
    _typed_encode_into(payload.extend, value)
    return bytes(payload)


def typed_sha256(value: Any) -> str:
    hasher = hashlib.sha256()
    _typed_encode_into(hasher.update, value)
    return hasher.hexdigest()


def _typed_hash_update(hasher: Any, value: Any) -> None:
    _typed_encode_into(hasher.update, value)


def _compact_template_witness(template: Template) -> tuple[Any, ...]:
    return (
        template.terminal_full_letter,
        template.terminal_c_deleted,
        tuple(
            (
                witness.block_index,
                witness.base_copies,
                witness.slopes,
                witness.split_position,
                witness.left_copy_id,
                witness.right_copy_id,
                witness.left_core_offset,
                witness.right_core_offset,
            )
            for witness in template.pumping_witnesses
        ),
    )


def _jsonable_compact(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_jsonable_compact(item) for item in value]
    return value


def _compact_rolling_hashes(catalog: Mapping[str, Any]) -> tuple[str, str]:
    identity_hasher = hashlib.sha256()
    replay_hasher = hashlib.sha256()
    shared = (
        catalog["format"],
        catalog["typed_encoding"],
        catalog["family"],
        catalog["field_orders"],
        catalog["identity_order"],
        catalog["schema_count"],
        catalog["cell_count"],
        catalog["template_count"],
        catalog["witness_count"],
        catalog["schema_table"],
        catalog["cell_table"],
        catalog["witness_table"],
    )
    for value in shared:
        _typed_hash_update(identity_hasher, value)
        _typed_hash_update(replay_hasher, value)
    cell_count = len(catalog["cell_table"])
    for identity_index, witness_id in enumerate(
        catalog["identity_witness_ids"]
    ):
        schema_index, cell_index = divmod(identity_index, cell_count)
        _typed_hash_update(
            identity_hasher, [schema_index, cell_index, witness_id]
        )
        _typed_hash_update(
            replay_hasher,
            [schema_index, cell_index, witness_id],
        )
        _typed_hash_update(
            replay_hasher, catalog["witness_table"][witness_id]
        )
    return identity_hasher.hexdigest(), replay_hasher.hexdigest()


def _recompute_compact_rolling_hashes(catalog: dict[str, Any]) -> None:
    identity_digest, replay_digest = _compact_rolling_hashes(catalog)
    catalog["identity_sha256"] = identity_digest
    catalog["replay_sha256"] = replay_digest


def _seal_compact_template_catalog(
    catalog: Mapping[str, Any],
) -> tuple[dict[str, Any], int]:
    payload = canonical_json(catalog).encode("ascii")
    digest = hashlib.sha256(payload).hexdigest()
    sealed = {**catalog, "catalog_sha256": digest}
    emitted_bytes = len(payload) + len(',"catalog_sha256":""') + len(digest)
    return sealed, emitted_bytes


def _extract_compact_template_catalog(
    family: str,
    schemas: Mapping[str, Schema],
    cells: Sequence[Cell],
    templates: Mapping[tuple[str, str], Template | tuple[Any, ...]],
) -> dict[str, Any]:
    schema_ids = tuple(sorted(schemas))
    sorted_cells = tuple(sorted(cells, key=lambda cell: cell.cell_id))
    schema_table = [
        [
            schema_id,
            list(schemas[schema_id].variables),
            [
                [
                    block_name,
                    list(word),
                    None if affine is None else list(affine),
                ]
                for block_name, word, affine in schemas[schema_id].blocks
            ],
        ]
        for schema_id in schema_ids
    ]
    cell_table = [
        [
            cell.cell_id,
            list(cell.names),
            list(cell.states),
            list(cell.base_values),
        ]
        for cell in sorted_cells
    ]
    witnesses: list[Any] = []
    witness_ids: dict[tuple[Any, ...], int] = {}
    identity_witness_ids = []
    for schema_id in schema_ids:
        for cell in sorted_cells:
            source = templates[(schema_id, cell.cell_id)]
            witness = (
                _compact_template_witness(source)
                if isinstance(source, Template)
                else source
            )
            witness_id = witness_ids.get(witness)
            if witness_id is None:
                witness_id = len(witnesses)
                witness_ids[witness] = witness_id
                witnesses.append(_jsonable_compact(witness))
            identity_witness_ids.append(witness_id)
    extracted = {
        "format": TEMPLATE_CATALOG_FORMAT,
        "typed_encoding": TEMPLATE_TYPED_ENCODING,
        "family": family,
        "field_orders": copy.deepcopy(TEMPLATE_FIELD_ORDERS),
        "identity_order": "schema-major-cell-minor",
        "schema_count": len(schema_table),
        "cell_count": len(cell_table),
        "template_count": len(identity_witness_ids),
        "witness_count": len(witnesses),
        "schema_table": schema_table,
        "cell_table": cell_table,
        "witness_table": witnesses,
        "identity_witness_ids": identity_witness_ids,
    }
    _recompute_compact_rolling_hashes(extracted)
    return extracted


def _validate_compact_schema_rows(schema_table: Sequence[Any]) -> None:
    for row in schema_table:
        if not isinstance(row, list) or len(row) != 3:
            raise CertificateFailure("compact schema row shape differs")
        _, variables, blocks = row
        if not isinstance(variables, list) or not all(
            isinstance(variable, str) for variable in variables
        ):
            raise CertificateFailure("compact schema variables are invalid")
        if not isinstance(blocks, list):
            raise CertificateFailure("compact schema blocks are invalid")
        for block in blocks:
            if not isinstance(block, list) or len(block) != 3:
                raise CertificateFailure("compact block row shape differs")
            block_name, word, affine = block
            if not isinstance(block_name, str):
                raise CertificateFailure("compact block name is invalid")
            if not isinstance(word, list) or not all(
                _is_exact_integer(letter) for letter in word
            ):
                raise CertificateFailure("compact block word is invalid")
            if affine is not None and (
                not isinstance(affine, list)
                or not all(_is_exact_integer(value) for value in affine)
            ):
                raise CertificateFailure("compact block affine is invalid")
            if affine is not None and len(affine) != len(variables) + 1:
                raise CertificateFailure("compact block affine width differs")


def _validate_compact_cell_rows(cell_table: Sequence[Any]) -> None:
    for row in cell_table:
        if not isinstance(row, list) or len(row) != 4:
            raise CertificateFailure("compact cell row shape differs")
        _, names, states, base_values = row
        if not isinstance(names, list) or not all(
            isinstance(name, str) for name in names
        ):
            raise CertificateFailure("compact cell names are invalid")
        if not isinstance(states, list) or not all(
            state is None or _is_exact_integer(state) for state in states
        ):
            raise CertificateFailure("compact cell states are invalid")
        if not isinstance(base_values, list) or not all(
            _is_exact_integer(value) for value in base_values
        ):
            raise CertificateFailure("compact cell base values are invalid")
        if not (len(names) == len(states) == len(base_values)):
            raise CertificateFailure("compact cell coordinate widths differ")
        if any(state not in THRESHOLD_STATES for state in states):
            raise CertificateFailure("compact cell state is outside threshold")
        if any(
            base != (3 if state is None else state)
            for state, base in zip(states, base_values)
        ):
            raise CertificateFailure("compact cell base value differs")


def _validate_compact_witness_rows(witness_table: Sequence[Any]) -> None:
    integer_fields = (0, 1, 3, 4, 5, 6, 7)
    for witness in witness_table:
        if not isinstance(witness, list) or len(witness) != 3:
            raise CertificateFailure("compact witness row shape differs")
        terminal, terminal_deleted, pumps = witness
        if terminal is not None and not _is_exact_integer(terminal):
            raise CertificateFailure("compact witness terminal is invalid")
        if not isinstance(terminal_deleted, bool):
            raise CertificateFailure("compact terminal-deletion flag is invalid")
        if terminal_deleted != (terminal == 1):
            raise CertificateFailure("compact terminal-deletion branch differs")
        if not isinstance(pumps, list):
            raise CertificateFailure("compact witness pumps are invalid")
        for pump in pumps:
            if not isinstance(pump, list) or len(pump) != 8:
                raise CertificateFailure("compact pump row shape differs")
            if any(not _is_exact_integer(pump[index]) for index in integer_fields):
                raise CertificateFailure("compact pump integer field is invalid")
            if not isinstance(pump[2], list) or not all(
                _is_exact_integer(slope) for slope in pump[2]
            ):
                raise CertificateFailure("compact pump slopes are invalid")
            if any(pump[index] < 0 for index in integer_fields):
                raise CertificateFailure("compact pump index is negative")
            if pump[3] == 0:
                raise CertificateFailure("compact pump split is not internal")
            if pump[5] != pump[4] + 1:
                raise CertificateFailure("compact pump copy IDs are not consecutive")


def _validate_compact_identity_relationships(
    schema_table: Sequence[Any],
    cell_table: Sequence[Any],
    witness_table: Sequence[Any],
    identity_witness_ids: Sequence[int],
) -> None:
    cell_count = len(cell_table)
    for identity_index, witness_id in enumerate(identity_witness_ids):
        schema_index, cell_index = divmod(identity_index, cell_count)
        schema_id, variables, blocks = schema_table[schema_index]
        _, names, states, base_values = cell_table[cell_index]
        if variables != names:
            raise CertificateFailure("compact schema/cell variables differ")
        witness = witness_table[witness_id]
        schema = Schema(
            schema_id=schema_id,
            variables=tuple(variables),
            blocks=tuple(
                (
                    block_name,
                    tuple(word),
                    None if affine is None else tuple(affine),
                )
                for block_name, word, affine in blocks
            ),
        )
        _, expected_terminal, expected_deleted = _retained_word(
            _tagged_reduced_word(schema, tuple(base_values), 1), 1
        )
        if (
            witness[0] != expected_terminal
            or witness[1] is not expected_deleted
        ):
            raise CertificateFailure("compact witness terminal differs")
        pumps = witness[2]
        expected_pumps = {}
        for block_index, (_, _, affine) in enumerate(blocks):
            if affine is None:
                continue
            slopes = [
                coefficient if state is None else 0
                for coefficient, state in zip(affine[:-1], states)
            ]
            if any(slopes):
                expected_pumps[block_index] = (
                    slopes,
                    sum(
                        coefficient * value
                        for coefficient, value in zip(
                            affine[:-1], base_values
                        )
                    )
                    + affine[-1],
                )
        pump_indices = [pump[0] for pump in pumps]
        if len(set(pump_indices)) != len(pump_indices):
            raise CertificateFailure("compact pump block index repeats")
        if set(pump_indices) != set(expected_pumps):
            raise CertificateFailure("compact pump block coverage differs")
        split_positions = [pump[3] for pump in pumps]
        if len(set(split_positions)) != len(split_positions):
            raise CertificateFailure("compact pump split position repeats")
        if split_positions != sorted(split_positions):
            raise CertificateFailure("compact pump splits are not ordered")
        for pump in pumps:
            block_index = pump[0]
            if block_index >= len(blocks):
                raise CertificateFailure("compact pump block index is out of range")
            _, word, _ = blocks[block_index]
            slopes, base_copies = expected_pumps[block_index]
            if pump[1] != base_copies or pump[2] != slopes:
                raise CertificateFailure("compact pump affine data differs")
            if any(slope < 0 for slope in pump[2]):
                raise CertificateFailure("compact pump slope is negative")
            if pump[5] >= pump[1]:
                raise CertificateFailure("compact pump copy ID is out of range")
            if not word or pump[6] != len(word) - 1 or pump[7] != 0:
                raise CertificateFailure("compact pump core offsets differ")


def validate_compact_template_catalog(
    catalog: Mapping[str, Any],
) -> Mapping[str, Any]:
    if set(catalog) != TEMPLATE_CATALOG_FIELDS:
        raise CertificateFailure("compact template catalog fields differ")
    if catalog["format"] != TEMPLATE_CATALOG_FORMAT:
        raise CertificateFailure("compact template catalog format differs")
    if catalog["typed_encoding"] != TEMPLATE_TYPED_ENCODING:
        raise CertificateFailure("compact typed encoding differs")
    family = catalog["family"]
    if not isinstance(family, str) or not family or not family.isascii():
        raise CertificateFailure("compact catalog family is not ASCII")
    if catalog["field_orders"] != TEMPLATE_FIELD_ORDERS:
        raise CertificateFailure("compact catalog field orders differ")
    if catalog["identity_order"] != "schema-major-cell-minor":
        raise CertificateFailure("compact catalog identity order differs")

    count_names = (
        "schema_count",
        "cell_count",
        "template_count",
        "witness_count",
    )
    if any(
        not _is_exact_integer(catalog[name]) or catalog[name] < 0
        for name in count_names
    ):
        raise CertificateFailure("compact catalog count is invalid")
    schema_table = catalog["schema_table"]
    cell_table = catalog["cell_table"]
    witness_table = catalog["witness_table"]
    identity_witness_ids = catalog["identity_witness_ids"]
    if catalog["schema_count"] != len(schema_table) or not schema_table:
        raise CertificateFailure("compact schema count differs")
    if catalog["cell_count"] != len(cell_table) or not cell_table:
        raise CertificateFailure("compact cell count differs")
    if catalog["witness_count"] != len(witness_table) or not witness_table:
        raise CertificateFailure("compact witness count differs")
    expected_template_count = len(schema_table) * len(cell_table)
    if (
        catalog["template_count"] != expected_template_count
        or len(identity_witness_ids) != expected_template_count
    ):
        raise CertificateFailure("compact template count differs")

    _validate_compact_schema_rows(schema_table)
    schema_ids = [row[0] for row in schema_table]
    if any(
        not isinstance(schema_id, str)
        or not schema_id
        or not schema_id.isascii()
        for schema_id in schema_ids
    ):
        raise CertificateFailure("compact schema IDs must be ASCII")
    if schema_ids != sorted(schema_ids) or len(set(schema_ids)) != len(schema_ids):
        raise CertificateFailure("compact schema table is not strictly sorted")

    _validate_compact_cell_rows(cell_table)
    cell_ids = [row[0] for row in cell_table]
    if any(
        not isinstance(cell_id, str) or not cell_id or not cell_id.isascii()
        for cell_id in cell_ids
    ):
        raise CertificateFailure("compact cell IDs must be ASCII")
    if cell_ids != sorted(cell_ids) or len(set(cell_ids)) != len(cell_ids):
        raise CertificateFailure("compact cell table is not strictly sorted")

    if any(
        not _is_exact_integer(witness_id)
        or witness_id < 0
        or witness_id >= len(witness_table)
        for witness_id in identity_witness_ids
    ):
        raise CertificateFailure("compact witness mapping is out of range")
    if set(identity_witness_ids) != set(range(len(witness_table))):
        raise CertificateFailure("compact catalog contains an unused witness")
    _validate_compact_witness_rows(witness_table)
    _validate_compact_identity_relationships(
        schema_table,
        cell_table,
        witness_table,
        identity_witness_ids,
    )
    first_seen: dict[bytes, int] = {}
    for witness_id in identity_witness_ids:
        witness_key = typed_encode(witness_table[witness_id])
        prior_id = first_seen.get(witness_key)
        if prior_id is None:
            expected_id = len(first_seen)
            if witness_id != expected_id:
                raise CertificateFailure(
                    "compact witness table is not first-seen canonical"
                )
            first_seen[witness_key] = witness_id
        elif witness_id != prior_id:
            raise CertificateFailure("compact witness table repeats a witness")
    if len(first_seen) != len(witness_table):
        raise CertificateFailure("compact witness table is noncanonical")

    identity_digest, replay_digest = _compact_rolling_hashes(catalog)
    if catalog["identity_sha256"] != identity_digest:
        raise CertificateFailure("compact identity digest differs")
    if catalog["replay_sha256"] != replay_digest:
        raise CertificateFailure("compact replay digest differs")
    payload = {
        key: value
        for key, value in catalog.items()
        if key != "catalog_sha256"
    }
    catalog_digest = hashlib.sha256(
        canonical_json(payload).encode("ascii")
    ).hexdigest()
    if catalog["catalog_sha256"] != catalog_digest:
        raise CertificateFailure("compact catalog digest differs")
    return catalog


def build_compact_template_catalog(
    family: str,
    schemas: Mapping[str, Schema],
    cells: Sequence[Cell],
    templates: Mapping[tuple[str, str], Template | tuple[Any, ...]],
) -> dict[str, Any]:
    extracted = _extract_compact_template_catalog(
        family, schemas, cells, templates
    )
    sealed = _seal_compact_template_catalog(extracted)[0]
    validate_compact_template_catalog(sealed)
    return sealed


def _schema_pump_capacity(schema: Schema, cells: Sequence[Cell]) -> int:
    return max(
        sum(
            affine is not None and any(_changing_slopes(affine, cell))
            for _, _, affine in schema.blocks
        )
        for cell in cells
    )


def measure_compact_catalog_slice(
    catalog: Task4SchemaCatalog,
) -> dict[str, Any]:
    family_metrics = {}
    extraction_total = 0.0
    serialization_total = 0.0
    projected_total = 0.0
    total_schema_count = 0
    total_identity_count = 0
    sample_identity_count = 0
    sample_catalog_bytes = 0
    for family in sorted(catalog.families):
        item = catalog.families[family]
        schema_ids = tuple(sorted(item.schemas))
        pump_counts = {
            schema_id: _schema_pump_capacity(
                item.schemas[schema_id], item.cells
            )
            for schema_id in schema_ids
        }
        highest_count = max(pump_counts.values())
        highest_schema_ids = tuple(
            schema_id
            for schema_id in schema_ids
            if pump_counts[schema_id] == highest_count
        )
        selected_ids = tuple(
            sorted({*schema_ids[::8], *highest_schema_ids})
        )
        selected_schemas = {
            schema_id: item.schemas[schema_id]
            for schema_id in selected_ids
        }
        sample_templates = {
            (schema_id, cell.cell_id): build_template(schema, cell)
            for schema_id, schema in selected_schemas.items()
            for cell in item.cells
        }

        extraction_start = time.perf_counter()
        extracted = _extract_compact_template_catalog(
            family, selected_schemas, item.cells, sample_templates
        )
        extraction_seconds = time.perf_counter() - extraction_start
        serialization_start = time.perf_counter()
        _, emitted_bytes = _seal_compact_template_catalog(extracted)
        serialization_seconds = time.perf_counter() - serialization_start

        ratio_numerator = len(schema_ids)
        ratio_denominator = len(selected_ids)
        schema_ratio = ratio_numerator / ratio_denominator
        projected_bytes = (
            emitted_bytes * ratio_numerator + ratio_denominator - 1
        ) // ratio_denominator
        projected_extraction = extraction_seconds * schema_ratio
        projected_serialization = serialization_seconds * (
            projected_bytes / emitted_bytes
        )
        projected_overhead = projected_extraction + projected_serialization
        identities = len(schema_ids) * len(item.cells)
        sample_identities = len(selected_ids) * len(item.cells)
        family_metrics[family] = {
            "sample_schema_ids": list(selected_ids),
            "highest_pump_count": highest_count,
            "highest_pump_schema_ids": list(highest_schema_ids),
            "total_schema_count": len(schema_ids),
            "sample_schema_count": len(selected_ids),
            "schema_ratio_numerator": ratio_numerator,
            "schema_ratio_denominator": ratio_denominator,
            "total_identity_count": identities,
            "sample_identity_count": sample_identities,
            "sample_catalog_bytes": emitted_bytes,
            "projected_catalog_bytes": projected_bytes,
            "extraction_intern_seconds": extraction_seconds,
            "canonical_serialization_seconds": serialization_seconds,
            "projected_extraction_seconds": projected_extraction,
            "projected_serialization_seconds": projected_serialization,
            "projected_overhead_seconds": projected_overhead,
        }
        total_schema_count += len(schema_ids)
        total_identity_count += identities
        sample_identity_count += sample_identities
        sample_catalog_bytes += emitted_bytes
        extraction_total += extraction_seconds
        serialization_total += serialization_seconds
        projected_total += projected_overhead
    return {
        "selection": (
            "every-eighth-ascii-schema-plus-all-maximum-pump-schemas"
        ),
        "families": family_metrics,
        "total_schema_count": total_schema_count,
        "total_identity_count": total_identity_count,
        "sample_identity_count": sample_identity_count,
        "sample_catalog_bytes": sample_catalog_bytes,
        "extraction_intern_seconds": extraction_total,
        "canonical_serialization_seconds": serialization_total,
        "projected_full_overhead_seconds": projected_total,
        "doubled_projected_full_overhead_seconds": 2 * projected_total,
    }


def build_task4_schema_catalog(context: SourceContext) -> Task4SchemaCatalog:
    b_tokens, b_source_proof = build_b_catalog(context)
    b_identity_table = _b_identity_table(b_tokens)
    old_tokens, old_source_proof = build_old_rows(context)
    occurrence_leafs, occurrence_polarities, occurrence_slots, fixed_metadata = (
        _task4_chronology_metadata(context)
    )
    inverse_sources, _ = context.modules["inverse"].schema_words(
        context.modules["raw"]
    )
    zero_sources = context.modules["aggregate"].g_zero_schemas(
        context.modules["inverse"], context.modules["raw"]
    )
    powered_sources = {**inverse_sources, **zero_sources}
    configurations = {
        "fixed": ("a", "n"),
        "base": ("a", "n"),
        "singleton": ("a", "n"),
        "P": ("a", "h", "r"),
        "C": ("a", "n"),
        "Q": ("h", "k", "n"),
    }
    families = {}
    for family, variables in configurations.items():
        cells = make_cells(variables)
        if family == "P":
            cells = tuple(cell for cell in cells if p_domain_nonempty(cell))
        family_old_tokens = tuple(
            token for token in old_tokens if token.family == family
        )
        old_schemas, old_references = _build_old_family_schemas(
            context,
            family,
            variables,
            family_old_tokens,
            powered_sources,
        )
        b_schemas, b_references = _build_b_family_schemas(
            family, variables, b_tokens, powered_sources
        )
        overlap = set(old_schemas) & set(b_schemas)
        if overlap:
            raise ValueError(f"old/B schema ID collision: {sorted(overlap)}")
        families[family] = Task4FamilyCatalog(
            family=family,
            variables=variables,
            cells=cells,
            schemas={**old_schemas, **b_schemas},
            old_tokens=family_old_tokens,
            b_tokens=b_tokens,
            old_schema_refs=old_references,
            b_schema_refs=b_references,
            old_footprint_bindings=_old_footprint_bindings(
                context,
                family_old_tokens,
                old_references,
                occurrence_leafs,
                occurrence_polarities,
                fixed_metadata,
            ),
        )
    return Task4SchemaCatalog(
        families=families,
        dependency_digests=dict(context.source_digests),
        old_source_proof=old_source_proof,
        b_source_proof=b_source_proof,
        occurrence_leafs=occurrence_leafs,
        occurrence_polarities=occurrence_polarities,
        occurrence_slots=occurrence_slots,
        fixed_metadata=fixed_metadata,
        chronology_digest=_chronology_digest(
            occurrence_leafs,
            occurrence_polarities,
            occurrence_slots,
            fixed_metadata,
        ),
        b_identity_table=b_identity_table,
        b_identity_digest=_identity_digest(b_identity_table),
    )


def build_task4_template_records(
    catalog: Task4SchemaCatalog,
) -> dict[str, dict[str, dict[str, Any]]]:
    return {
        family: {
            f"{schema_id}|{cell.cell_id}": build_template(
                schema, cell
            ).to_record()
            for schema_id, schema in item.schemas.items()
            for cell in item.cells
        }
        for family, item in catalog.families.items()
    }


def _b_occurrence_records(
    item: Task4FamilyCatalog,
    catalog: Task4SchemaCatalog,
) -> tuple[dict[str, Any], ...]:
    live_identity_table = _b_identity_table(item.b_tokens)
    if canonical_json(live_identity_table) != canonical_json(
        catalog.b_identity_table
    ):
        raise CertificateFailure(
            f"B token-index identity binding mismatch: {item.family}"
        )
    records = []
    for token in item.b_tokens:
        reference = item.b_schema_refs[token.token_id]
        if token.token_index is None or token.occurrence is None:
            raise CertificateFailure(f"incomplete B token: {token.token_id}")
        if reference.module_schema is None or len(reference.label_schemas) != 1:
            raise CertificateFailure(
                f"incomplete B schema reference: {token.token_id}"
            )
        label_occurrence, label_schema = reference.label_schemas[0]
        if label_occurrence != token.occurrence:
            raise CertificateFailure(
                f"B label occurrence differs: {token.token_id}"
            )
        records.append(
            {
                "token_id": token.token_id,
                "token_index": token.token_index,
                "source_class": token.family,
                "coordinate": [token.slot, *token.source_members],
                "leaf": catalog.occurrence_leafs[token.occurrence],
                "occurrence": token.occurrence,
                "polarity": token.polarity,
                "module_schema": reference.module_schema,
                "label_schema": label_schema,
            }
        )
    if len(records) != TOKEN_COUNT:
        raise CertificateFailure(
            f"family {item.family} has {len(records)} B tokens"
        )
    return tuple(records)


def _old_occurrence_records(
    token: TokenRef,
    reference: DecoratedSchemaRef,
    catalog: Task4SchemaCatalog,
) -> tuple[dict[str, Any], ...]:
    records = []
    bindings = []
    for occurrence, label_schema in reference.label_schemas:
        if occurrence is None:
            metadata = catalog.fixed_metadata.get(token.token_id)
            if metadata is None or reference.module_schema is not None:
                raise CertificateFailure(
                    f"incomplete fixed chronology metadata: {token.token_id}"
                )
            leaf = metadata["leaf"]
            polarity = None
            coordinate = metadata["coordinate"]
            occurrence_slot = None
        else:
            if reference.module_schema is None:
                raise CertificateFailure(
                    f"correction lacks module schema: {token.token_id}"
                )
            leaf = catalog.occurrence_leafs[occurrence]
            polarity = catalog.occurrence_polarities[occurrence]
            occurrence_slot = catalog.occurrence_slots[occurrence]
            coordinate = [token.slot, *token.source_members]
        bindings.append(
            {
                "token_id": token.token_id,
                "source_slot": token.slot,
                "source_members": list(token.source_members),
                "module_schema": reference.module_schema,
                "occurrence": occurrence,
                "occurrence_slot": occurrence_slot,
                "polarity": polarity,
                "leaf": leaf,
                "label_schema": label_schema,
            }
        )
        records.append(
            {
                "token_id": token.token_id,
                "source_class": token.family,
                "coordinate": coordinate,
                "leaf": leaf,
                "occurrence": occurrence,
                "polarity": polarity,
                "module_schema": reference.module_schema,
                "label_schema": label_schema,
            }
        )
    family = catalog.families[token.family]
    expected_bindings = family.old_footprint_bindings.get(token.token_id)
    if expected_bindings is None or canonical_json(bindings) != canonical_json(
        expected_bindings
    ):
        raise CertificateFailure(
            f"old footprint binding mismatch: {token.token_id}"
        )
    if not records:
        raise CertificateFailure(f"empty old footprint: {token.token_id}")
    return tuple(records)


def _expected_family_value(family: str, cell: Cell) -> int:
    if family == "singleton":
        return 1
    if family == "C":
        return int(cell.states[cell.names.index("a")] == 0)
    if family in {"fixed", "base", "P", "Q"}:
        return 0
    raise CertificateFailure(f"unknown Task 4 family: {family}")


def family_ledger(
    item: Task4FamilyCatalog,
    catalog: Task4SchemaCatalog,
) -> dict[str, Any]:
    old_token_ids = [token.token_id for token in item.old_tokens]
    if len(set(old_token_ids)) != len(old_token_ids):
        raise CertificateFailure(f"duplicate old token ID: {item.family}")
    grouped_load_ids = [
        f"{item.family}|{cell.cell_id}|{token_id}"
        for cell in item.cells
        for token_id in old_token_ids
    ]
    if len(set(grouped_load_ids)) != len(grouped_load_ids):
        raise CertificateFailure(
            f"duplicate grouped load ID: {item.family}"
        )
    b_records = _b_occurrence_records(item, catalog)
    cell_records = []
    template_witnesses: dict[tuple[str, str], tuple[Any, ...]] = {}
    family_comparisons = 0
    family_occurrence_loads = 0
    for cell in item.cells:
        templates = {
            schema_id: build_template(schema, cell)
            for schema_id, schema in item.schemas.items()
        }
        for schema_id, template in templates.items():
            identity = (schema_id, cell.cell_id)
            if identity in template_witnesses:
                raise CertificateFailure(
                    f"duplicate template identity: {item.family}, {identity}"
                )
            template_witnesses[identity] = _compact_template_witness(template)
        comparison_cache: dict[
            tuple[str, str, str], Mapping[str, Any]
        ] = {}
        loads = []
        odd_load_ids = []
        cell_value = 0
        cell_comparisons = 0
        cell_occurrence_loads = 0
        for token in item.old_tokens:
            if token.coefficient % 2 != 1:
                raise CertificateFailure(
                    f"inactive old fiber reached Task 4: {token.token_id}"
                )
            reference = item.old_schema_refs[token.token_id]
            occurrence_records = _old_occurrence_records(
                token, reference, catalog
            )
            histograms = [
                histogram_for_load(
                    old,
                    b_records,
                    templates,
                    cell,
                    comparison_cache=comparison_cache,
                )
                for old in occurrence_records
            ]
            load_value = sum(
                histogram["value"] for histogram in histograms
            ) % 2
            load_id = f"{item.family}|{cell.cell_id}|{token.token_id}"
            if load_value:
                odd_load_ids.append(load_id)
            cell_value ^= load_value
            occurrence_count = len(histograms)
            comparison_count = sum(
                histogram["comparison_count"] for histogram in histograms
            )
            cell_occurrence_loads += occurrence_count
            cell_comparisons += comparison_count
            loads.append(
                {
                    "load_id": load_id,
                    "old_token_id": token.token_id,
                    "coefficient": token.coefficient,
                    "source_members": list(token.source_members),
                    "occurrence_footprint": occurrence_count,
                    "footprint_bindings": [
                        dict(binding)
                        for binding in item.old_footprint_bindings[
                            token.token_id
                        ]
                    ],
                    "histograms": histograms,
                    "value": load_value,
                }
            )
        expected = _expected_family_value(item.family, cell)
        if cell_value != expected:
            raise CertificateFailure(
                "family parity mismatch: "
                f"family={item.family}, cell={cell.cell_id}, "
                f"expected={expected}, actual={cell_value}, "
                f"first_odd_load_ids={odd_load_ids[:8]}"
            )
        if len(loads) != len(item.old_tokens):
            raise CertificateFailure(
                f"source load count mismatch: {item.family}, {cell.cell_id}"
            )
        if cell_comparisons != cell_occurrence_loads * TOKEN_COUNT:
            raise CertificateFailure(
                f"comparison count mismatch: {item.family}, {cell.cell_id}"
            )
        family_occurrence_loads += cell_occurrence_loads
        family_comparisons += cell_comparisons
        cell_records.append(
            {
                "cell_id": cell.cell_id,
                "load_count": len(loads),
                "occurrence_load_count": cell_occurrence_loads,
                "comparison_count": cell_comparisons,
                "odd_load_ids": odd_load_ids,
                "value": cell_value,
                "loads": loads,
            }
        )
    return {
        "family": item.family,
        "cells": cell_records,
        "template_catalog": build_compact_template_catalog(
            item.family, item.schemas, item.cells, template_witnesses
        ),
        "summary": {
            "load_rows": len(item.old_tokens) * len(item.cells),
            "occurrence_loads": family_occurrence_loads,
            "comparisons": family_comparisons,
        },
    }


def _catalog_summary(catalog: Task4SchemaCatalog) -> dict[str, Any]:
    load_rows = {}
    footprint_sizes = {}
    occurrence_loads = {}
    comparisons = {}
    template_counts = {}
    for family, item in catalog.families.items():
        footprints = [
            len(item.old_schema_refs[token.token_id].label_schemas)
            for token in item.old_tokens
        ]
        distribution = {
            str(size): footprints.count(size) for size in sorted(set(footprints))
        }
        load_rows[family] = len(item.old_tokens) * len(item.cells)
        footprint_sizes[family] = distribution
        occurrence_loads[family] = sum(footprints) * len(item.cells)
        comparisons[family] = occurrence_loads[family] * len(item.b_tokens)
        template_counts[family] = len(item.schemas) * len(item.cells)
    return {
        "load_rows": load_rows,
        "total_load_rows": sum(load_rows.values()),
        "footprint_sizes": footprint_sizes,
        "occurrence_loads": occurrence_loads,
        "total_occurrence_loads": sum(occurrence_loads.values()),
        "b_tokens_per_occurrence": TOKEN_COUNT,
        "active_comparisons": sum(comparisons.values()),
        "template_counts": template_counts,
        "total_templates": sum(template_counts.values()),
    }


def _validate_catalog_summary(summary: Mapping[str, Any]) -> None:
    expected_loads = {
        "fixed": 1120,
        "base": 32,
        "singleton": 16,
        "P": 1728,
        "C": 624,
        "Q": 5888,
    }
    expected_footprints = {
        "fixed": {"1": 70},
        "base": {"2": 2},
        "singleton": {"6": 1},
        "P": {"2": 32},
        "C": {"2": 39},
        "Q": {"2": 92},
    }
    expected_occurrence_loads = {
        "fixed": 1120,
        "base": 64,
        "singleton": 96,
        "P": 3456,
        "C": 1248,
        "Q": 11776,
    }
    expected_template_counts = {
        "fixed": 3072,
        "base": 2048,
        "singleton": 2064,
        "P": 11772,
        "C": 3824,
        "Q": 25472,
    }
    if summary["load_rows"] != expected_loads:
        raise CertificateFailure(
            f"source load census mismatch: {summary['load_rows']}"
        )
    if summary["total_load_rows"] != 9408:
        raise CertificateFailure(
            f"total source load census mismatch: {summary['total_load_rows']}"
        )
    if summary["footprint_sizes"] != expected_footprints:
        raise CertificateFailure(
            f"occurrence footprint mismatch: {summary['footprint_sizes']}"
        )
    if summary["occurrence_loads"] != expected_occurrence_loads:
        raise CertificateFailure(
            f"occurrence load census mismatch: {summary['occurrence_loads']}"
        )
    if summary["total_occurrence_loads"] != 17760:
        raise CertificateFailure(
            "total occurrence load census mismatch: "
            f"{summary['total_occurrence_loads']}"
        )
    if summary["b_tokens_per_occurrence"] != TOKEN_COUNT:
        raise CertificateFailure("B token count differs from 84")
    if summary["active_comparisons"] != 1491840:
        raise CertificateFailure(
            f"active comparison census mismatch: {summary['active_comparisons']}"
        )
    if summary["template_counts"] != expected_template_counts:
        raise CertificateFailure(
            f"template census mismatch: {summary['template_counts']}"
        )
    if summary["total_templates"] != 48252:
        raise CertificateFailure(
            f"total template census mismatch: {summary['total_templates']}"
        )


def build_manifest(
    *, catalog: Task4SchemaCatalog | None = None
) -> dict[str, Any]:
    if catalog is None:
        catalog = build_task4_schema_catalog(load_source_context())
    live_chronology_digest = _chronology_digest(
        catalog.occurrence_leafs,
        catalog.occurrence_polarities,
        catalog.occurrence_slots,
        catalog.fixed_metadata,
    )
    if live_chronology_digest != catalog.chronology_digest:
        raise CertificateFailure("chronology metadata digest mismatch")
    if _identity_digest(catalog.b_identity_table) != catalog.b_identity_digest:
        raise CertificateFailure("B identity table digest mismatch")
    summary = _catalog_summary(catalog)
    _validate_catalog_summary(summary)
    source_bindings = build_source_bindings(catalog)
    validate_source_bindings(source_bindings, catalog)
    manifest = {
        "format": "period-two-old-new-cut-load-v1",
        "domain": "a=d-1>=0, n>=0; positive chamber d>=1",
        "status": "unverified",
        "summary": summary,
        "dependency_digests": dict(catalog.dependency_digests),
        "source_bindings": source_bindings,
        "b_identity_table": [dict(row) for row in catalog.b_identity_table],
        "b_identity_digest": catalog.b_identity_digest,
        "family_ledgers": {},
    }
    ledgers = {
        family: family_ledger(item, catalog)
        for family, item in catalog.families.items()
    }
    derived_comparisons = sum(
        ledger["summary"]["comparisons"] for ledger in ledgers.values()
    )
    if derived_comparisons != summary["active_comparisons"]:
        raise CertificateFailure(
            "ledger comparison census differs from catalog summary: "
            f"{derived_comparisons}"
        )
    derived_templates = {
        family: ledger["template_catalog"]["template_count"]
        for family, ledger in ledgers.items()
    }
    if derived_templates != summary["template_counts"]:
        raise CertificateFailure(
            f"ledger template census differs: {derived_templates}"
        )
    manifest["family_ledgers"] = ledgers
    manifest["status"] = "generated-awaiting-independent-replay"
    return manifest


def _state_label(name: str, state: int | None) -> str:
    if name == "a" and state is None:
        return "3"
    return "ge3" if state is None else str(state)


def _name_label(name: str) -> str:
    return "age" if name == "a" else name


def make_cells(names: Sequence[str]) -> tuple[Cell, ...]:
    field_names = tuple(names)
    cells = []
    for states in product(THRESHOLD_STATES, repeat=len(field_names)):
        cells.append(
            Cell(
                cell_id="_".join(
                    f"{_name_label(name)}{_state_label(name, state)}"
                    for name, state in zip(field_names, states)
                ),
                names=field_names,
                states=states,
                base_values=tuple(3 if state is None else state for state in states),
            )
        )
    return tuple(cells)


def p_domain_nonempty(cell: Cell) -> bool:
    a, h, r = cell.states
    if a is None:
        if h is None or r is None:
            return True
        return h + r >= 3
    if h is None or r is None:
        return True
    return h + r >= a


def bucketize_records(
    records: Iterable[Mapping[str, Any]], *, key_fields: Sequence[str]
) -> tuple[HistogramBucket, ...]:
    grouped: dict[str, tuple[tuple[Any, ...], int, int]] = {}
    seen_indices: set[int] = set()
    for record in records:
        token_index = record["token_index"]
        if isinstance(token_index, bool) or not isinstance(token_index, int):
            raise ValueError(  # noqa: TRY004 - preserve the Task 1 validation API
                "token_index must be an integer"
            )
        if not 0 <= token_index < TOKEN_COUNT:
            raise ValueError("token_index must be in 0..83")
        if token_index in seen_indices:
            raise ValueError(f"duplicate token_index: {token_index}")
        seen_indices.add(token_index)

        key = tuple(record[field] for field in key_fields)
        serialized_key = canonical_json(key)
        previous = grouped.get(serialized_key)
        if previous is None:
            grouped[serialized_key] = (key, 1, 1 << token_index)
        else:
            previous_key, count, mask = previous
            grouped[serialized_key] = (previous_key, count + 1, mask | (1 << token_index))

    if seen_indices != set(range(TOKEN_COUNT)):
        raise ValueError("token indices must cover 0..83 exactly")

    buckets = tuple(
        HistogramBucket(key=key, count=count, mask=mask)
        for _, (key, count, mask) in sorted(grouped.items())
    )
    union = 0
    for bucket in buckets:
        assert union & bucket.mask == 0
        union |= bucket.mask
    assert union == (1 << TOKEN_COUNT) - 1
    return buckets


PACKAGE_V2_FORMAT = "period-two-old-new-cut-package-v2"
LOGICAL_V1_FORMAT = "period-two-old-new-cut-load-v1"
CANONICAL_LINE_ENCODING = "canonical-json-ascii-lines-v1"
MASK_ENCODING = "uint84-be11-base64url-nopad-v1"
FAMILY_ORDER = ("fixed", "base", "singleton", "P", "C", "Q")
SHARD_ORDER = ("shared",) + FAMILY_ORDER
PACKAGE_BYTE_CAP = 100_000_000
MAX_CANONICAL_LINE_BYTES = 16_777_216
PRODUCTION_SCOPE = "production-full"
PREFLIGHT_SCOPE = "preflight-sample"
PRODUCTION_STATUS = "generated-awaiting-independent-replay"
PREFLIGHT_STATUS = "preflight-sample-not-a-certificate"
SOURCE_CELL_ORDER = "product-order-with-P-domain-filter"
IDENTITY_CHUNK_SIZE = 4096
ROOT_INDEX_FIELDS = (
    "format",
    "scope",
    "logical_v1_format",
    "canonical_encoding",
    "mask_encoding",
    "domain",
    "status",
    "shard_order",
    "shards",
    "shard_bytes_total",
    "emitted_summary",
    "full_summary",
    "source_bindings_sha256",
    "b_identity_digest",
    "template_catalogs",
    "root_sha256",
)
SHARD_DESCRIPTOR_FIELDS = (
    "role",
    "family",
    "path",
    "sha256",
    "total_bytes",
    "record_count",
    "record_counts",
)
SHARED_RECORD_FIELDS = {
    "shared_header": (
        "tag",
        "format",
        "scope",
        "logical_v1_format",
        "canonical_encoding",
        "mask_encoding",
        "domain",
        "status",
        "shard_order",
    ),
    "dependency": ("tag", "path", "sha256"),
    "source_bindings": ("tag", "value"),
    "b_identity": (
        "tag",
        "token_index",
        "token_id",
        "source_class",
        "coefficient",
        "slot",
        "occurrence",
        "polarity",
        "module_schema",
        "label_schema",
        "source_members",
    ),
    "b_coordinate": (
        "tag",
        "token_index",
        "source_class",
        "coordinate",
    ),
    "shared_footer": (
        "tag",
        "coordinate_count",
        "records_before_footer",
        "bytes_before_footer",
    ),
}
FAMILY_RECORD_FIELDS = {
    "family_header": (
        "tag",
        "family",
        "variables",
        "source_cell_count",
        "selected_old_indices",
        "old_load_count",
        "footprint_count",
        "bucket_class_count",
        "b_token_count",
        "comparison_methods",
        "chronologies",
        "histogram_key_fields",
        "template_field_orders",
        "source_cell_order",
    ),
    "old_load": (
        "tag",
        "old_index",
        "old_token_id",
        "coefficient",
        "source_members",
        "source_slot",
        "footprint_start",
        "footprint_count",
    ),
    "footprint": (
        "tag",
        "footprint_index",
        "old_index",
        "occurrence",
        "occurrence_slot",
        "polarity",
        "leaf",
        "module_schema",
        "label_schema",
    ),
    "bucket_class": (
        "tag",
        "b_source_class",
        "b_coordinate",
        "equality_exclusion",
        "module_method",
        "module_order",
        "chronology",
        "chronology_order",
        "label_method",
        "label_order",
        "contribution_bit",
    ),
    "load": (
        "tag",
        "old_index",
        "footprint_index",
        "bucket_class_index",
        "mask",
    ),
    "cell_footer": (
        "tag",
        "source_cell_index",
        "compact_cell_index",
        "cell_id",
        "odd_old_indices",
        "value",
        "load_record_count",
    ),
    "template_header": (
        "tag",
        "format",
        "typed_encoding",
        "family",
        "field_orders",
        "identity_order",
        "schema_count",
        "cell_count",
        "template_count",
        "witness_count",
    ),
    "template_schema": (
        "tag",
        "schema_index",
        "schema_id",
        "variables",
        "blocks",
    ),
    "template_cell": (
        "tag",
        "compact_cell_index",
        "cell_id",
        "names",
        "states",
        "base_values",
    ),
    "template_witness": (
        "tag",
        "witness_id",
        "terminal_full_letter",
        "terminal_c_deleted",
        "pumps",
    ),
    "template_identity_chunk": (
        "tag",
        "start_identity_index",
        "witness_id_list",
    ),
    "template_footer": (
        "tag",
        "identity_sha256",
        "replay_sha256",
        "catalog_sha256",
    ),
    "family_footer": (
        "tag",
        "source_cell_count",
        "old_load_count",
        "load_rows",
        "occurrence_loads",
        "comparisons",
        "records_before_footer",
        "bytes_before_footer",
    ),
}
COMPARISON_METHODS = (
    None,
    "strict_affine_length",
    "identical_pumped_blocks",
    "fixed_mismatch_after_pumped_prefix",
)
CHRONOLOGIES = (
    "fixed_vs_correction_literal_leaf_order",
    "distinct_occurrences_literal_AST_order",
    "equal_coordinate_excluded",
    "same_occurrence_increasing",
    "same_occurrence_decreasing",
)
METRIC_STAGES = (
    "encode_shared",
    "encode_family",
    "write_objects",
    "publish_index",
    "verify_package",
)
METRIC_TAGS = (
    *SHARED_RECORD_FIELDS,
    *FAMILY_RECORD_FIELDS,
    "root_index",
)
PACKAGE_V2_TEMPLATE_SUMMARY_FIELDS = (
    "format",
    "typed_encoding",
    "identity_order",
    "schema_count",
    "cell_count",
    "template_count",
    "witness_count",
    "identity_sha256",
    "replay_sha256",
    "catalog_sha256",
)
_HASH_PATTERN = re.compile(r"[0-9a-f]{64}")
_MASK_PATTERN = re.compile(r"[A-Za-z0-9_-]{15}")


class WireFormatError(ValueError):
    pass


class PublicationFailure(RuntimeError):
    def __init__(self, state: str, stage: str, cause: BaseException) -> None:
        self.state = state
        self.stage = stage
        self.cause = cause
        super().__init__(f"{state} publication failure at {stage}: {cause}")


@dataclass(frozen=True)
class EncodedV2Package:
    index: Mapping[str, Any]
    index_bytes: bytes
    objects: Mapping[str, bytes]
    shard_records: Mapping[str, tuple[tuple[Any, ...], ...]]


@dataclass(frozen=True)
class PublicationResult:
    state: str
    index_sha256: str
    root_sha256: str
    package_bytes: int
    created_objects: tuple[str, ...]
    reused_objects: tuple[str, ...]


class PhaseMetrics:
    def __init__(self, *, enabled: bool = False) -> None:
        self.enabled = enabled
        self._stages = {stage: 0.0 for stage in METRIC_STAGES}
        self._record_counts = {tag: 0 for tag in METRIC_TAGS}
        self._byte_counts = {tag: 0 for tag in METRIC_TAGS}

    def add_stage(self, stage: str, elapsed: float) -> None:
        if stage not in self._stages:
            raise ValueError(f"unknown metrics stage: {stage}")
        if self.enabled:
            self._stages[stage] += elapsed

    def record(self, tag: str, byte_count: int) -> None:
        if tag not in self._record_counts:
            raise ValueError(f"unknown metrics tag: {tag}")
        if self.enabled:
            self._record_counts[tag] += 1
            self._byte_counts[tag] += byte_count

    def snapshot(self) -> dict[str, Any]:
        return {
            "format": "period-two-old-new-cut-phase-metrics-v1",
            "stages": dict(self._stages),
            "record_counts": dict(self._record_counts),
            "byte_counts": dict(self._byte_counts),
        }


def _exact_int(value: Any, name: str, *, minimum: int | None = None) -> int:
    if type(value) is not int:
        raise WireFormatError(f"{name} is not an exact integer")
    if minimum is not None and value < minimum:
        raise WireFormatError(f"{name} is below {minimum}")
    return value


def _exact_hash(value: Any, name: str) -> str:
    if not isinstance(value, str) or _HASH_PATTERN.fullmatch(value) is None:
        raise WireFormatError(f"{name} is not a lowercase SHA-256")
    return value


def canonical_json_line(value: Any) -> bytes:
    try:
        payload = json.dumps(
            value,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
    except (TypeError, UnicodeError, ValueError) as error:
        raise WireFormatError("value is not canonical JSON") from error
    return payload + b"\n"


def _reject_json_float(token: str) -> Any:
    raise WireFormatError(f"floating JSON number is forbidden: {token}")


def _parse_json_int(token: str) -> int:
    if token == "-0":
        raise WireFormatError("negative zero is forbidden")
    return int(token)


def _reject_json_constant(token: str) -> Any:
    raise WireFormatError(f"JSON constant is forbidden: {token}")


def _object_without_duplicate_keys(
    pairs: Sequence[tuple[str, Any]],
) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise WireFormatError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _decode_canonical_line(line: bytes) -> Any:
    if b"\r" in line:
        raise WireFormatError("carriage return is forbidden")
    if line == b"\n":
        raise WireFormatError("blank canonical line is forbidden")
    if not line.endswith(b"\n"):
        raise WireFormatError("canonical line is missing final LF")
    try:
        text = line[:-1].decode("ascii")
    except UnicodeDecodeError as error:
        raise WireFormatError("canonical line is not ASCII") from error
    try:
        value = json.loads(
            text,
            parse_int=_parse_json_int,
            parse_float=_reject_json_float,
            parse_constant=_reject_json_constant,
            object_pairs_hook=_object_without_duplicate_keys,
        )
    except WireFormatError:
        raise
    except (json.JSONDecodeError, ValueError) as error:
        raise WireFormatError("canonical line is invalid JSON") from error
    if canonical_json_line(value) != line:
        raise WireFormatError("JSON line is not canonical")
    return value


def iter_canonical_json_lines(
    stream: Any, *, max_line_bytes: int = MAX_CANONICAL_LINE_BYTES
) -> Iterable[Any]:
    if type(max_line_bytes) is not int or not 1 <= max_line_bytes <= (
        MAX_CANONICAL_LINE_BYTES
    ):
        raise WireFormatError("invalid canonical line cap")
    while True:
        line = stream.readline(max_line_bytes + 1)
        if line == b"":
            return
        if not isinstance(line, bytes):
            raise WireFormatError("canonical stream must be binary")
        if len(line) > max_line_bytes:
            raise WireFormatError("canonical line exceeds byte cap")
        yield _decode_canonical_line(line)


def pack_mask(mask: int) -> str:
    _exact_int(mask, "mask", minimum=0)
    if mask >= 1 << TOKEN_COUNT:
        raise WireFormatError("mask is outside uint84")
    token = base64.b64encode(
        mask.to_bytes(11, "big"), altchars=b"-_"
    ).rstrip(b"=")
    return token.decode("ascii")


def unpack_mask(token: str) -> int:
    if not isinstance(token, str) or _MASK_PATTERN.fullmatch(token) is None:
        raise WireFormatError("mask token is not 15-character base64url")
    try:
        raw = base64.b64decode(
            (token + "=").encode("ascii"),
            altchars=b"-_",
            validate=True,
        )
    except (ValueError, UnicodeError) as error:
        raise WireFormatError("mask token has invalid base64url") from error
    if len(raw) != 11 or raw[0] & 0xF0:
        raise WireFormatError("mask token is outside uint84")
    value = int.from_bytes(raw, "big")
    if pack_mask(value) != token:
        raise WireFormatError("mask token is not canonical")
    return value


def validate_mask_partition(tokens: Sequence[str]) -> int:
    union = 0
    for token in tokens:
        mask = unpack_mask(token)
        if mask == 0:
            raise WireFormatError("histogram masks must be nonzero")
        if union & mask:
            raise WireFormatError("histogram masks overlap")
        union |= mask
    if union != (1 << TOKEN_COUNT) - 1:
        raise WireFormatError("histogram masks do not cover uint84")
    return union


def _source_stream(source: Any) -> tuple[Any, bool]:
    if isinstance(source, (bytes, bytearray)):
        return io.BytesIO(bytes(source)), True
    if hasattr(source, "readline"):
        return source, False
    raise WireFormatError("canonical source must be bytes or a binary stream")


def _tagged_records(source: Any) -> tuple[list[Any], ...]:
    stream, owned = _source_stream(source)
    try:
        records = tuple(iter_canonical_json_lines(stream))
    finally:
        if owned:
            stream.close()
    for record in records:
        if (
            not isinstance(record, list)
            or not record
            or not isinstance(record[0], str)
        ):
            raise WireFormatError("tagged record is not a nonempty array")
    return records


def _require_tag_width(
    record: Sequence[Any],
    tag: str,
    declarations: Mapping[str, Sequence[str]],
) -> None:
    if record[0] != tag:
        raise WireFormatError(f"expected {tag}, got {record[0]}")
    fields = declarations.get(tag)
    if fields is None or len(record) != len(fields):
        raise WireFormatError(f"{tag} width differs")


def _root_without_hash(root: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in root.items() if key != "root_sha256"}


def decode_root_index(source: Any) -> dict[str, Any]:
    stream, owned = _source_stream(source)
    try:
        values = tuple(iter_canonical_json_lines(stream))
    finally:
        if owned:
            stream.close()
    if len(values) != 1 or not isinstance(values[0], Mapping):
        raise WireFormatError("root index must contain exactly one object line")
    root = dict(values[0])
    if set(root) != set(ROOT_INDEX_FIELDS):
        raise WireFormatError("root index fields differ")
    if root["format"] != PACKAGE_V2_FORMAT:
        raise WireFormatError("root package format differs")
    if root["logical_v1_format"] != LOGICAL_V1_FORMAT:
        raise WireFormatError("root logical-v1 format differs")
    if root["canonical_encoding"] != CANONICAL_LINE_ENCODING:
        raise WireFormatError("root canonical encoding differs")
    if root["mask_encoding"] != MASK_ENCODING:
        raise WireFormatError("root mask encoding differs")
    scope = root["scope"]
    expected_status = {
        PRODUCTION_SCOPE: PRODUCTION_STATUS,
        PREFLIGHT_SCOPE: PREFLIGHT_STATUS,
    }.get(scope)
    if expected_status is None or root["status"] != expected_status:
        raise WireFormatError("root scope/status pair differs")
    if not isinstance(root["domain"], str) or not root["domain"]:
        raise WireFormatError("root domain is invalid")
    if root["shard_order"] != list(SHARD_ORDER):
        raise WireFormatError("root shard order differs")
    shards = root["shards"]
    if not isinstance(shards, list) or len(shards) != len(SHARD_ORDER):
        raise WireFormatError("root shard descriptor count differs")
    expected_families = (None,) + FAMILY_ORDER
    for position, (descriptor, family) in enumerate(
        zip(shards, expected_families)
    ):
        if not isinstance(descriptor, Mapping) or set(descriptor) != set(
            SHARD_DESCRIPTOR_FIELDS
        ):
            raise WireFormatError("shard descriptor fields differ")
        expected_role = "shared" if family is None else "family"
        if (
            descriptor["role"] != expected_role
            or descriptor["family"] != family
        ):
            raise WireFormatError(f"shard descriptor role differs at {position}")
        digest = _exact_hash(descriptor["sha256"], "descriptor sha256")
        if descriptor["path"] != f"objects/{digest}.jsonl":
            raise WireFormatError("descriptor path is not content addressed")
        _exact_int(descriptor["total_bytes"], "descriptor bytes", minimum=1)
        record_count = _exact_int(
            descriptor["record_count"], "descriptor record count", minimum=1
        )
        expected_tags = (
            SHARED_RECORD_FIELDS if family is None else FAMILY_RECORD_FIELDS
        )
        counts = descriptor["record_counts"]
        if not isinstance(counts, Mapping) or set(counts) != set(expected_tags):
            raise WireFormatError("descriptor record-count tags differ")
        if any(
            _exact_int(value, f"{tag} count", minimum=0) < 0
            for tag, value in counts.items()
        ):
            raise WireFormatError("descriptor record count is negative")
        if sum(counts.values()) != record_count:
            raise WireFormatError("descriptor record counts do not sum")
    shard_bytes_total = _exact_int(
        root["shard_bytes_total"], "root shard bytes", minimum=1
    )
    if shard_bytes_total != sum(
        descriptor["total_bytes"] for descriptor in shards
    ):
        raise WireFormatError("root shard byte total differs")
    _exact_hash(root["source_bindings_sha256"], "source bindings sha256")
    _exact_hash(root["b_identity_digest"], "B identity digest")
    template_catalogs = root["template_catalogs"]
    if not isinstance(template_catalogs, Mapping) or set(
        template_catalogs
    ) != set(FAMILY_ORDER):
        raise WireFormatError("root template catalog families differ")
    for family, summary in template_catalogs.items():
        if not isinstance(summary, Mapping) or set(summary) != set(
            PACKAGE_V2_TEMPLATE_SUMMARY_FIELDS
        ):
            raise WireFormatError(
                f"root template summary fields differ: {family}"
            )
    if scope == PRODUCTION_SCOPE and (
        root["emitted_summary"] != root["full_summary"]
    ):
        raise WireFormatError("production emitted/full summaries differ")
    expected_root_hash = hashlib.sha256(
        canonical_json_line(_root_without_hash(root))
    ).hexdigest()
    if (
        _exact_hash(root["root_sha256"], "root sha256")
        != expected_root_hash
    ):
        raise WireFormatError("root hash differs")
    return root


def decode_shared_records(source: Any) -> dict[str, Any]:
    records = _tagged_records(source)
    if len(records) < 3:
        raise WireFormatError("shared shard is incomplete")
    _require_tag_width(records[0], "shared_header", SHARED_RECORD_FIELDS)
    header = records[0]
    if header[1:] != [
        PACKAGE_V2_FORMAT,
        header[2],
        LOGICAL_V1_FORMAT,
        CANONICAL_LINE_ENCODING,
        MASK_ENCODING,
        header[6],
        header[7],
        list(SHARD_ORDER),
    ]:
        raise WireFormatError("shared header payload differs")
    expected_status = {
        PRODUCTION_SCOPE: PRODUCTION_STATUS,
        PREFLIGHT_SCOPE: PREFLIGHT_STATUS,
    }.get(header[2])
    if expected_status is None or header[7] != expected_status:
        raise WireFormatError("shared scope/status pair differs")
    cursor = 1
    dependencies = {}
    dependency_paths = []
    while cursor < len(records) and records[cursor][0] == "dependency":
        row = records[cursor]
        _require_tag_width(row, "dependency", SHARED_RECORD_FIELDS)
        path, digest = row[1:]
        if not isinstance(path, str) or not path or not path.isascii():
            raise WireFormatError("dependency path is invalid")
        if path in dependencies:
            raise WireFormatError("dependency path repeats")
        dependencies[path] = _exact_hash(digest, "dependency sha256")
        dependency_paths.append(path)
        cursor += 1
    if dependency_paths != sorted(dependency_paths):
        raise WireFormatError("dependencies are not in ASCII order")
    if cursor >= len(records):
        raise WireFormatError("shared source binding is missing")
    source_row = records[cursor]
    _require_tag_width(source_row, "source_bindings", SHARED_RECORD_FIELDS)
    source_bindings = source_row[1]
    if not isinstance(source_bindings, Mapping):
        raise WireFormatError("source bindings are not an object")
    required_source_fields = {"format", "old", "b", "sha256"}
    if set(source_bindings) != required_source_fields:
        raise WireFormatError("source-binding fields differ")
    source_payload = {
        key: value
        for key, value in source_bindings.items()
        if key != "sha256"
    }
    source_digest = hashlib.sha256(
        canonical_json(source_payload).encode("ascii")
    ).hexdigest()
    if source_bindings["sha256"] != source_digest:
        raise WireFormatError("source-binding digest differs")
    cursor += 1
    identities = []
    while cursor < len(records) and records[cursor][0] == "b_identity":
        row = records[cursor]
        _require_tag_width(row, "b_identity", SHARED_RECORD_FIELDS)
        token_index = _exact_int(
            row[1], "B token index", minimum=0
        )
        if token_index != len(identities):
            raise WireFormatError("B identity indices are not consecutive")
        if not isinstance(row[2], str) or not row[2]:
            raise WireFormatError("B token ID is invalid")
        if not isinstance(row[3], str) or not row[3]:
            raise WireFormatError("B source class is invalid")
        _exact_int(row[4], "B coefficient")
        for name, value in (
            ("B slot", row[5]),
            ("B occurrence", row[6]),
            ("B polarity", row[7]),
        ):
            if value is not None:
                _exact_int(value, name)
        if not isinstance(row[8], str) or not isinstance(row[9], str):
            raise WireFormatError("B schema reference is invalid")
        if not isinstance(row[10], list) or not all(
            isinstance(item, str) for item in row[10]
        ):
            raise WireFormatError("B source members are invalid")
        identities.append(row)
        cursor += 1
    coordinates = []
    while cursor < len(records) and records[cursor][0] == "b_coordinate":
        row = records[cursor]
        _require_tag_width(row, "b_coordinate", SHARED_RECORD_FIELDS)
        token_index = _exact_int(
            row[1], "B coordinate token index", minimum=0
        )
        if token_index != len(coordinates):
            raise WireFormatError("B coordinate indices are not consecutive")
        if token_index >= len(identities) or row[2] != identities[token_index][3]:
            raise WireFormatError("B coordinate identity reference differs")
        if not isinstance(row[3], list):
            raise WireFormatError("B coordinate is not an array")
        coordinates.append(row)
        cursor += 1
    if len(coordinates) != len(identities):
        raise WireFormatError("B identity/coordinate counts differ")
    if cursor != len(records) - 1:
        raise WireFormatError("shared records are out of order")
    footer = records[cursor]
    _require_tag_width(footer, "shared_footer", SHARED_RECORD_FIELDS)
    if _exact_int(footer[1], "coordinate count", minimum=0) != len(
        coordinates
    ):
        raise WireFormatError("shared coordinate count differs")
    if _exact_int(footer[2], "shared prefix records", minimum=0) != len(
        records
    ) - 1:
        raise WireFormatError("shared prefix record count differs")
    prefix_bytes = sum(len(canonical_json_line(row)) for row in records[:-1])
    if _exact_int(footer[3], "shared prefix bytes", minimum=0) != prefix_bytes:
        raise WireFormatError("shared prefix byte count differs")
    return {
        "records": tuple(tuple(record) for record in records),
        "header": tuple(header),
        "dependencies": dependencies,
        "source_bindings": dict(source_bindings),
        "identities": tuple(tuple(row) for row in identities),
        "coordinates": tuple(tuple(row) for row in coordinates),
    }


def _template_catalog_from_tagged_rows(
    template_header: Sequence[Any],
    schema_rows: Sequence[Sequence[Any]],
    cell_rows: Sequence[Sequence[Any]],
    witness_rows: Sequence[Sequence[Any]],
    identity_rows: Sequence[Sequence[Any]],
    template_footer: Sequence[Any],
) -> dict[str, Any]:
    identity_witness_ids = [
        witness_id
        for row in identity_rows
        for witness_id in row[2]
    ]
    catalog = {
        "format": template_header[1],
        "typed_encoding": template_header[2],
        "family": template_header[3],
        "field_orders": template_header[4],
        "identity_order": template_header[5],
        "schema_count": template_header[6],
        "cell_count": template_header[7],
        "template_count": template_header[8],
        "witness_count": template_header[9],
        "schema_table": [
            [row[2], row[3], row[4]] for row in schema_rows
        ],
        "cell_table": [
            [row[2], row[3], row[4], row[5]] for row in cell_rows
        ],
        "witness_table": [
            [row[2], row[3], row[4]] for row in witness_rows
        ],
        "identity_witness_ids": identity_witness_ids,
        "identity_sha256": template_footer[1],
        "replay_sha256": template_footer[2],
        "catalog_sha256": template_footer[3],
    }
    return catalog


def _validate_v2_template_catalog(catalog: Mapping[str, Any]) -> None:
    count_names = (
        "schema_count",
        "cell_count",
        "template_count",
        "witness_count",
    )
    for name in count_names:
        _exact_int(catalog[name], f"template {name}", minimum=0)
    if catalog["format"] != TEMPLATE_CATALOG_FORMAT:
        raise WireFormatError("template catalog format differs")
    if catalog["typed_encoding"] != TEMPLATE_TYPED_ENCODING:
        raise WireFormatError("template typed encoding differs")
    if catalog["field_orders"] != TEMPLATE_FIELD_ORDERS:
        raise WireFormatError("template field orders differ")
    if catalog["identity_order"] != "schema-major-cell-minor":
        raise WireFormatError("template identity order differs")
    if catalog["schema_count"] != len(catalog["schema_table"]):
        raise WireFormatError("template schema count differs")
    if catalog["cell_count"] != len(catalog["cell_table"]):
        raise WireFormatError("template cell count differs")
    if catalog["witness_count"] != len(catalog["witness_table"]):
        raise WireFormatError("template witness count differs")
    expected_templates = catalog["schema_count"] * catalog["cell_count"]
    if (
        catalog["template_count"] != expected_templates
        or len(catalog["identity_witness_ids"]) != expected_templates
    ):
        raise WireFormatError("template identity count differs")
    identity_digest, replay_digest = _compact_rolling_hashes(catalog)
    if catalog["identity_sha256"] != identity_digest:
        raise WireFormatError("template identity digest differs")
    if catalog["replay_sha256"] != replay_digest:
        raise WireFormatError("template replay digest differs")
    payload = {
        key: value
        for key, value in catalog.items()
        if key != "catalog_sha256"
    }
    catalog_digest = hashlib.sha256(
        canonical_json(payload).encode("ascii")
    ).hexdigest()
    if catalog["catalog_sha256"] != catalog_digest:
        raise WireFormatError("template catalog digest differs")
    if expected_templates == 0:
        if any(
            catalog[name]
            for name in (
                "schema_table",
                "cell_table",
                "witness_table",
                "identity_witness_ids",
            )
        ):
            raise WireFormatError("empty template catalog has table rows")
        return
    try:
        validate_compact_template_catalog(catalog)
    except (CertificateFailure, TypeError, ValueError) as error:
        raise WireFormatError("compact template catalog is invalid") from error


def _bucket_key_from_rows(
    footprint: Sequence[Any], bucket_class: Sequence[Any]
) -> dict[str, Any]:
    return {
        "old_occurrence": footprint[3],
        "old_leaf": footprint[6],
        "b_source_class": bucket_class[1],
        "b_coordinate": bucket_class[2],
        "equality_exclusion": bucket_class[3],
        "old_polarity": footprint[5],
        "module_method": bucket_class[4],
        "module_order": bucket_class[5],
        "chronology": bucket_class[6],
        "chronology_order": bucket_class[7],
        "label_method": bucket_class[8],
        "label_order": bucket_class[9],
        "contribution_bit": bucket_class[10],
    }


def _validate_family_header(header: Sequence[Any], family: str) -> None:
    _require_tag_width(header, "family_header", FAMILY_RECORD_FIELDS)
    if header[1] != family:
        raise WireFormatError("family header name differs")
    if not isinstance(header[2], list) or not all(
        isinstance(name, str) for name in header[2]
    ):
        raise WireFormatError("family variables are invalid")
    for index, name in (
        (3, "source cell count"),
        (5, "old load count"),
        (6, "footprint count"),
        (7, "bucket class count"),
        (8, "B token count"),
    ):
        _exact_int(header[index], name, minimum=0)
    selected = header[4]
    if (
        not isinstance(selected, list)
        or any(type(index) is not int or index < 0 for index in selected)
        or selected != sorted(set(selected))
    ):
        raise WireFormatError("selected old indices are invalid")
    if any(index >= header[5] for index in selected):
        raise WireFormatError("selected old index is out of range")
    if header[9] != list(COMPARISON_METHODS):
        raise WireFormatError("comparison method declaration differs")
    if header[10] != list(CHRONOLOGIES):
        raise WireFormatError("chronology declaration differs")
    if header[11] != list(HISTOGRAM_KEY_FIELDS):
        raise WireFormatError("histogram field declaration differs")
    if header[12] != TEMPLATE_FIELD_ORDERS:
        raise WireFormatError("template field declaration differs")
    if header[13] != SOURCE_CELL_ORDER:
        raise WireFormatError("source-cell order declaration differs")


def decode_family_records(
    source: Any, *, expected_family: str, scope: str
) -> dict[str, Any]:
    if expected_family not in FAMILY_ORDER:
        raise WireFormatError("unknown family shard")
    if scope not in {PREFLIGHT_SCOPE, PRODUCTION_SCOPE}:
        raise WireFormatError("unknown package scope")
    records = _tagged_records(source)
    if len(records) < 4:
        raise WireFormatError("family shard is incomplete")
    header = records[0]
    _validate_family_header(header, expected_family)
    selected_old_indices = header[4]
    selected_old_set = set(selected_old_indices)
    if (
        scope == PRODUCTION_SCOPE
        and selected_old_indices != list(range(header[5]))
    ):
        raise WireFormatError("production old indices are not complete")
    cursor = 1

    old_rows = []
    for old_index in range(header[5]):
        if cursor >= len(records):
            raise WireFormatError("old-load table is truncated")
        row = records[cursor]
        _require_tag_width(row, "old_load", FAMILY_RECORD_FIELDS)
        if _exact_int(row[1], "old index", minimum=0) != old_index:
            raise WireFormatError("old-load indices are not consecutive")
        if not isinstance(row[2], str) or not row[2]:
            raise WireFormatError("old token ID is invalid")
        _exact_int(row[3], "old coefficient")
        if not isinstance(row[4], list) or not all(
            isinstance(member, str) for member in row[4]
        ):
            raise WireFormatError("old source members are invalid")
        if expected_family == "fixed":
            if row[5] is not None:
                raise WireFormatError("fixed old source slot is not null")
        else:
            _exact_int(row[5], "old source slot")
        _exact_int(row[6], "footprint start", minimum=0)
        _exact_int(row[7], "old footprint count", minimum=1)
        old_rows.append(row)
        cursor += 1

    footprint_rows = []
    for footprint_index in range(header[6]):
        if cursor >= len(records):
            raise WireFormatError("footprint table is truncated")
        row = records[cursor]
        _require_tag_width(row, "footprint", FAMILY_RECORD_FIELDS)
        if _exact_int(
            row[1], "footprint index", minimum=0
        ) != footprint_index:
            raise WireFormatError("footprint indices are not consecutive")
        old_index = _exact_int(row[2], "footprint old index", minimum=0)
        if old_index >= len(old_rows):
            raise WireFormatError("footprint old reference is out of range")
        fixed_nulls = (row[3], row[4], row[5], row[7])
        if expected_family == "fixed":
            if fixed_nulls != (None, None, None, None):
                raise WireFormatError("fixed footprint null domain differs")
        else:
            for name, value in zip(
                (
                    "footprint occurrence",
                    "footprint occurrence slot",
                    "footprint polarity",
                ),
                fixed_nulls[:3],
            ):
                _exact_int(value, name)
            if not isinstance(row[7], str):
                raise WireFormatError("footprint module schema is invalid")
        _exact_int(row[6], "footprint leaf", minimum=0)
        if not isinstance(row[8], str) or not row[8]:
            raise WireFormatError("footprint label schema is invalid")
        footprint_rows.append(row)
        cursor += 1
    expected_footprint = 0
    for old_index, old_row in enumerate(old_rows):
        if old_row[6] != expected_footprint:
            raise WireFormatError("footprint intervals are not contiguous")
        stop = old_row[6] + old_row[7]
        if any(
            footprint_rows[index][2] != old_index
            for index in range(old_row[6], stop)
        ):
            raise WireFormatError("footprint interval owner differs")
        expected_footprint = stop
    if expected_footprint != len(footprint_rows):
        raise WireFormatError("footprint intervals do not cover the table")

    bucket_rows = []
    for _ in range(header[7]):
        if cursor >= len(records):
            raise WireFormatError("bucket-class table is truncated")
        row = records[cursor]
        _require_tag_width(row, "bucket_class", FAMILY_RECORD_FIELDS)
        if not isinstance(row[1], str) or not isinstance(row[2], list):
            raise WireFormatError("bucket B coordinate is invalid")
        if not isinstance(row[3], bool):
            raise WireFormatError("bucket equality exclusion is invalid")
        for method, order, label in (
            (row[4], row[5], "module"),
            (row[8], row[9], "label"),
        ):
            if method not in COMPARISON_METHODS:
                raise WireFormatError(f"bucket {label} method differs")
            if method is None:
                if order is not None:
                    raise WireFormatError(f"bucket {label} null order differs")
            else:
                _exact_int(order, f"bucket {label} order")
        if row[6] not in CHRONOLOGIES:
            raise WireFormatError("bucket chronology differs")
        _exact_int(row[7], "bucket chronology order")
        if row[10] not in (0, 1) or type(row[10]) is not int:
            raise WireFormatError("bucket contribution bit differs")
        bucket_rows.append(row)
        cursor += 1
    bucket_keys = [canonical_json(row[1:]) for row in bucket_rows]
    if bucket_keys != sorted(set(bucket_keys)):
        raise WireFormatError("bucket classes are not canonical")

    cell_groups = []
    for source_cell_index in range(header[3]):
        load_rows = []
        while cursor < len(records) and records[cursor][0] == "load":
            row = records[cursor]
            _require_tag_width(row, "load", FAMILY_RECORD_FIELDS)
            old_index = _exact_int(row[1], "load old index", minimum=0)
            footprint_index = _exact_int(
                row[2], "load footprint index", minimum=0
            )
            bucket_index = _exact_int(
                row[3], "load bucket-class index", minimum=0
            )
            if old_index >= len(old_rows):
                raise WireFormatError("load old reference is out of range")
            if old_index not in selected_old_set:
                raise WireFormatError("load references an unselected old index")
            if footprint_index >= len(footprint_rows):
                raise WireFormatError("load footprint reference is out of range")
            if footprint_rows[footprint_index][2] != old_index:
                raise WireFormatError("load footprint owner differs")
            if bucket_index >= len(bucket_rows):
                raise WireFormatError("load bucket reference is out of range")
            if unpack_mask(row[4]) == 0:
                raise WireFormatError("load mask is zero")
            load_rows.append(row)
            cursor += 1
        if cursor >= len(records):
            raise WireFormatError("cell footer is missing")
        footer = records[cursor]
        _require_tag_width(footer, "cell_footer", FAMILY_RECORD_FIELDS)
        if _exact_int(
            footer[1], "source cell index", minimum=0
        ) != source_cell_index:
            raise WireFormatError("source cell indices are not consecutive")
        _exact_int(footer[2], "compact cell index", minimum=0)
        if not isinstance(footer[3], str) or not footer[3]:
            raise WireFormatError("cell ID is invalid")
        if (
            not isinstance(footer[4], list)
            or any(type(index) is not int for index in footer[4])
            or footer[4] != sorted(set(footer[4]))
        ):
            raise WireFormatError("odd old indices are invalid")
        if footer[5] not in (0, 1) or type(footer[5]) is not int:
            raise WireFormatError("cell value is invalid")
        if _exact_int(
            footer[6], "cell load-record count", minimum=0
        ) != len(load_rows):
            raise WireFormatError("cell load-record count differs")
        cell_groups.append((load_rows, footer))
        cursor += 1

    if cursor >= len(records):
        raise WireFormatError("template header is missing")
    template_header = records[cursor]
    _require_tag_width(
        template_header, "template_header", FAMILY_RECORD_FIELDS
    )
    if (
        template_header[1] != TEMPLATE_CATALOG_FORMAT
        or template_header[2] != TEMPLATE_TYPED_ENCODING
        or template_header[3] != expected_family
        or template_header[4] != TEMPLATE_FIELD_ORDERS
        or template_header[5] != "schema-major-cell-minor"
    ):
        raise WireFormatError("template header declarations differ")
    for index, name in (
        (6, "template schema count"),
        (7, "template cell count"),
        (8, "template identity count"),
        (9, "template witness count"),
    ):
        _exact_int(template_header[index], name, minimum=0)
    cursor += 1

    schema_rows = []
    for schema_index in range(template_header[6]):
        row = records[cursor]
        _require_tag_width(row, "template_schema", FAMILY_RECORD_FIELDS)
        if _exact_int(row[1], "schema index", minimum=0) != schema_index:
            raise WireFormatError("schema indices are not consecutive")
        schema_rows.append(row)
        cursor += 1
    cell_rows = []
    for compact_cell_index in range(template_header[7]):
        row = records[cursor]
        _require_tag_width(row, "template_cell", FAMILY_RECORD_FIELDS)
        if _exact_int(
            row[1], "template compact cell index", minimum=0
        ) != compact_cell_index:
            raise WireFormatError("compact cell indices are not consecutive")
        cell_rows.append(row)
        cursor += 1
    witness_rows = []
    for witness_index in range(template_header[9]):
        row = records[cursor]
        _require_tag_width(row, "template_witness", FAMILY_RECORD_FIELDS)
        if _exact_int(row[1], "witness index", minimum=0) != witness_index:
            raise WireFormatError("witness indices are not consecutive")
        witness_rows.append(row)
        cursor += 1
    identity_rows = []
    next_identity = 0
    while (
        cursor < len(records)
        and records[cursor][0] == "template_identity_chunk"
    ):
        row = records[cursor]
        _require_tag_width(
            row, "template_identity_chunk", FAMILY_RECORD_FIELDS
        )
        if _exact_int(
            row[1], "identity chunk start", minimum=0
        ) != next_identity:
            raise WireFormatError("identity chunks are not consecutive")
        if not isinstance(row[2], list) or not row[2]:
            raise WireFormatError("identity chunk is empty")
        if len(row[2]) > IDENTITY_CHUNK_SIZE:
            raise WireFormatError("identity chunk is too wide")
        next_identity += len(row[2])
        identity_rows.append(row)
        cursor += 1
    if identity_rows and any(
        len(row[2]) != IDENTITY_CHUNK_SIZE for row in identity_rows[:-1]
    ):
        raise WireFormatError("nonfinal identity chunk is not full")
    if next_identity != template_header[8]:
        raise WireFormatError("identity chunks do not cover the catalog")
    template_footer = records[cursor]
    _require_tag_width(
        template_footer, "template_footer", FAMILY_RECORD_FIELDS
    )
    for value in template_footer[1:]:
        _exact_hash(value, "template footer digest")
    cursor += 1
    if cursor != len(records) - 1:
        raise WireFormatError("family records are out of order")
    family_footer = records[cursor]
    _require_tag_width(
        family_footer, "family_footer", FAMILY_RECORD_FIELDS
    )
    for index, name in (
        (1, "footer source cell count"),
        (2, "footer old load count"),
        (3, "footer load rows"),
        (4, "footer occurrence loads"),
        (5, "footer comparisons"),
        (6, "family prefix records"),
        (7, "family prefix bytes"),
    ):
        _exact_int(family_footer[index], name, minimum=0)
    if family_footer[1] != len(cell_groups):
        raise WireFormatError("family footer cell count differs")
    if family_footer[2] != len(old_rows):
        raise WireFormatError("family footer old count differs")
    if family_footer[6] != len(records) - 1:
        raise WireFormatError("family prefix record count differs")
    prefix_bytes = sum(len(canonical_json_line(row)) for row in records[:-1])
    if family_footer[7] != prefix_bytes:
        raise WireFormatError("family prefix byte count differs")

    catalog = _template_catalog_from_tagged_rows(
        template_header,
        schema_rows,
        cell_rows,
        witness_rows,
        identity_rows,
        template_footer,
    )
    _validate_v2_template_catalog(catalog)
    compact_cells = {
        row[1]: row[2] for row in cell_rows
    }
    if len(compact_cells) != len(cell_rows):
        raise WireFormatError("compact cell index repeats")
    for _, footer in cell_groups:
        if compact_cells.get(footer[2]) != footer[3]:
            raise WireFormatError("source/compact cell bijection differs")
    if len({footer[3] for _, footer in cell_groups}) != len(cell_groups):
        raise WireFormatError("source cell ID repeats")
    if {footer[3] for _, footer in cell_groups} != set(
        compact_cells.values()
    ):
        raise WireFormatError("source/compact cell domains differ")

    logical_cells = []
    total_occurrences = 0
    total_comparisons = 0
    for load_records, footer in cell_groups:
        by_footprint: dict[tuple[int, int], list[Sequence[Any]]] = {}
        for row in load_records:
            by_footprint.setdefault((row[1], row[2]), []).append(row)
        logical_loads = []
        derived_odd = []
        cell_value = 0
        for old_index in selected_old_indices:
            old_row = old_rows[old_index]
            histograms = []
            load_value = 0
            footprint_bindings = []
            for footprint_index in range(
                old_row[6], old_row[6] + old_row[7]
            ):
                footprint = footprint_rows[footprint_index]
                rows = by_footprint.get((old_index, footprint_index), [])
                masks = [row[4] for row in rows]
                validate_mask_partition(masks)
                logical_buckets = []
                one_count = 0
                for row in rows:
                    mask = unpack_mask(row[4])
                    bucket_class = bucket_rows[row[3]]
                    count = bin(mask).count("1")  # noqa: FURB161
                    one_count += count * bucket_class[10]
                    logical_buckets.append(
                        {
                            "key": _bucket_key_from_rows(
                                footprint, bucket_class
                            ),
                            "count": count,
                            "mask": f"{mask:021x}",
                        }
                    )
                histogram_value = one_count % 2
                load_value ^= histogram_value
                histograms.append(
                    {
                        "old_occurrence": footprint[3],
                        "old_leaf": footprint[6],
                        "old_polarity": footprint[5],
                        "comparison_count": TOKEN_COUNT,
                        "one_count": one_count,
                        "value": histogram_value,
                        "buckets": logical_buckets,
                    }
                )
                footprint_bindings.append(
                    {
                        "token_id": old_row[2],
                        "source_slot": old_row[5],
                        "source_members": old_row[4],
                        "module_schema": footprint[7],
                        "occurrence": footprint[3],
                        "occurrence_slot": footprint[4],
                        "polarity": footprint[5],
                        "leaf": footprint[6],
                        "label_schema": footprint[8],
                    }
                )
            load_id = f"{expected_family}|{footer[3]}|{old_row[2]}"
            if load_value:
                derived_odd.append(old_index)
            cell_value ^= load_value
            logical_loads.append(
                {
                    "load_id": load_id,
                    "old_token_id": old_row[2],
                    "coefficient": old_row[3],
                    "source_members": old_row[4],
                    "occurrence_footprint": old_row[7],
                    "footprint_bindings": footprint_bindings,
                    "histograms": histograms,
                    "value": load_value,
                }
            )
        if footer[4] != derived_odd or footer[5] != cell_value:
            raise WireFormatError("cell parity footer differs")
        occurrence_count = sum(
            old_rows[index][7] for index in selected_old_indices
        )
        comparison_count = occurrence_count * TOKEN_COUNT
        if len(load_records) != sum(
            len(histogram["buckets"])
            for load in logical_loads
            for histogram in load["histograms"]
        ):
            raise WireFormatError("cell load records are not reconstructible")
        total_occurrences += occurrence_count
        total_comparisons += comparison_count
        logical_cells.append(
            {
                "cell_id": footer[3],
                "load_count": len(selected_old_indices),
                "occurrence_load_count": occurrence_count,
                "comparison_count": comparison_count,
                "odd_load_ids": [
                    f"{expected_family}|{footer[3]}|{old_rows[index][2]}"
                    for index in derived_odd
                ],
                "value": cell_value,
                "loads": logical_loads,
            }
        )
    derived_load_rows = len(selected_old_indices) * len(cell_groups)
    if family_footer[3:6] != [
        derived_load_rows,
        total_occurrences,
        total_comparisons,
    ]:
        raise WireFormatError("family footer summary differs")
    ledger = {
        "family": expected_family,
        "cells": logical_cells,
        "template_catalog": catalog,
        "summary": {
            "load_rows": family_footer[3],
            "occurrence_loads": family_footer[4],
            "comparisons": family_footer[5],
        },
    }
    return {
        "records": tuple(tuple(record) for record in records),
        "header": tuple(header),
        "ledger": ledger,
        "template_catalog": catalog,
    }


_FAMILY_VARIABLES = {
    "fixed": ("a", "n"),
    "base": ("a", "n"),
    "singleton": ("a", "n"),
    "P": ("a", "h", "r"),
    "C": ("a", "n"),
    "Q": ("h", "k", "n"),
}


def _logical_hex_mask(value: Any) -> int:
    if (
        not isinstance(value, str)
        or len(value) != 21
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise WireFormatError("logical-v1 mask is not 21 lowercase hex digits")
    mask = int(value, 16)
    if mask == 0 or mask >= 1 << TOKEN_COUNT:
        raise WireFormatError("logical-v1 mask is outside nonzero uint84")
    return mask


def _logical_b_coordinates(
    logical_v1: Mapping[str, Any],
) -> tuple[tuple[str, Any], ...]:
    identities = logical_v1["b_identity_table"]
    coordinates: dict[int, tuple[str, Any]] = {}
    for family in FAMILY_ORDER:
        ledger = logical_v1["family_ledgers"][family]
        for cell in ledger["cells"]:
            for load in cell["loads"]:
                for histogram in load["histograms"]:
                    for bucket in histogram["buckets"]:
                        key = bucket["key"]
                        mask = _logical_hex_mask(bucket["mask"])
                        coordinate = (
                            key["b_source_class"],
                            key["b_coordinate"],
                        )
                        for token_index in range(TOKEN_COUNT):
                            if not mask & (1 << token_index):
                                continue
                            prior = coordinates.get(token_index)
                            if prior is not None and prior != coordinate:
                                raise WireFormatError(
                                    "B token has conflicting coordinates"
                                )
                            coordinates[token_index] = coordinate
    if set(coordinates) != set(range(len(identities))):
        raise WireFormatError("B coordinate table is incomplete")
    return tuple(coordinates[index] for index in range(len(identities)))


def _encode_shared_records(
    logical_v1: Mapping[str, Any],
    *,
    scope: str,
    metrics: PhaseMetrics,
) -> tuple[tuple[Any, ...], ...]:
    started = time.perf_counter()
    records: list[list[Any]] = [
        [
            "shared_header",
            PACKAGE_V2_FORMAT,
            scope,
            LOGICAL_V1_FORMAT,
            CANONICAL_LINE_ENCODING,
            MASK_ENCODING,
            logical_v1["domain"],
            logical_v1["status"],
            list(SHARD_ORDER),
        ]
    ]
    for path in sorted(logical_v1["dependency_digests"]):
        records.append(
            [
                "dependency",
                path,
                logical_v1["dependency_digests"][path],
            ]
        )
    records.append(["source_bindings", logical_v1["source_bindings"]])
    identity_fields = SHARED_RECORD_FIELDS["b_identity"][1:]
    for expected_index, identity in enumerate(
        logical_v1["b_identity_table"]
    ):
        if set(identity) != set(identity_fields):
            raise WireFormatError("logical B identity fields differ")
        if identity["token_index"] != expected_index:
            raise WireFormatError("logical B identity order differs")
        records.append(
            ["b_identity", *(identity[field] for field in identity_fields)]
        )
    for token_index, (source_class, coordinate) in enumerate(
        _logical_b_coordinates(logical_v1)
    ):
        records.append(
            ["b_coordinate", token_index, source_class, coordinate]
        )
    prefix_bytes = sum(len(canonical_json_line(row)) for row in records)
    records.append(
        [
            "shared_footer",
            len(logical_v1["b_identity_table"]),
            len(records),
            prefix_bytes,
        ]
    )
    for row in records:
        metrics.record(row[0], len(canonical_json_line(row)))
    metrics.add_stage("encode_shared", time.perf_counter() - started)
    return tuple(tuple(row) for row in records)


def _bucket_class_values(key: Mapping[str, Any]) -> list[Any]:
    if set(key) != set(HISTOGRAM_KEY_FIELDS):
        raise WireFormatError("logical histogram key fields differ")
    return [
        key["b_source_class"],
        key["b_coordinate"],
        key["equality_exclusion"],
        key["module_method"],
        key["module_order"],
        key["chronology"],
        key["chronology_order"],
        key["label_method"],
        key["label_order"],
        key["contribution_bit"],
    ]


def _catalog_summary(catalog: Mapping[str, Any]) -> dict[str, Any]:
    return {
        field: catalog[field]
        for field in PACKAGE_V2_TEMPLATE_SUMMARY_FIELDS
    }


def _encode_family_records(
    family: str,
    ledger: Mapping[str, Any],
    *,
    b_token_count: int,
    metrics: PhaseMetrics,
) -> tuple[tuple[Any, ...], ...]:
    started = time.perf_counter()
    if set(ledger) != {"family", "cells", "template_catalog", "summary"}:
        raise WireFormatError("logical family ledger fields differ")
    if ledger["family"] != family:
        raise WireFormatError("logical family ledger name differs")
    cells = ledger["cells"]
    catalog = ledger["template_catalog"]
    _validate_v2_template_catalog(catalog)
    if catalog["family"] != family:
        raise WireFormatError("logical template family differs")
    compact_cell_indices = {
        row[0]: index for index, row in enumerate(catalog["cell_table"])
    }
    if set(compact_cell_indices) != {cell["cell_id"] for cell in cells}:
        raise WireFormatError("logical source/compact cell IDs differ")

    first_loads = cells[0]["loads"] if cells else []
    old_rows = []
    footprint_rows = []
    footprint_cursor = 0
    for old_index, load in enumerate(first_loads):
        bindings = load["footprint_bindings"]
        if load["occurrence_footprint"] != len(bindings) or not bindings:
            raise WireFormatError("logical footprint count differs")
        source_slot = bindings[0]["source_slot"]
        if any(binding["source_slot"] != source_slot for binding in bindings):
            raise WireFormatError("logical source slot differs inside load")
        old_rows.append(
            [
                "old_load",
                old_index,
                load["old_token_id"],
                load["coefficient"],
                load["source_members"],
                source_slot,
                footprint_cursor,
                len(bindings),
            ]
        )
        for binding in bindings:
            if (
                binding["token_id"] != load["old_token_id"]
                or binding["source_members"] != load["source_members"]
            ):
                raise WireFormatError("logical footprint binding differs")
            footprint_rows.append(
                [
                    "footprint",
                    footprint_cursor,
                    old_index,
                    binding["occurrence"],
                    binding["occurrence_slot"],
                    binding["polarity"],
                    binding["leaf"],
                    binding["module_schema"],
                    binding["label_schema"],
                ]
            )
            footprint_cursor += 1
    for cell in cells[1:]:
        comparable = [
            (
                load["old_token_id"],
                load["coefficient"],
                load["source_members"],
                load["footprint_bindings"],
            )
            for load in cell["loads"]
        ]
        baseline = [
            (
                load["old_token_id"],
                load["coefficient"],
                load["source_members"],
                load["footprint_bindings"],
            )
            for load in first_loads
        ]
        if comparable != baseline:
            raise WireFormatError("logical old-load table changes by cell")

    class_values: dict[str, list[Any]] = {}
    for cell in cells:
        for load in cell["loads"]:
            for histogram in load["histograms"]:
                for bucket in histogram["buckets"]:
                    values = _bucket_class_values(bucket["key"])
                    class_values.setdefault(canonical_json(values), values)
    bucket_rows = [
        ["bucket_class", *class_values[key]]
        for key in sorted(class_values)
    ]
    bucket_indices = {
        canonical_json(row[1:]): index for index, row in enumerate(bucket_rows)
    }
    variables = (
        catalog["schema_table"][0][1]
        if catalog["schema_table"]
        else list(_FAMILY_VARIABLES[family])
    )
    records: list[list[Any]] = [
        [
            "family_header",
            family,
            variables,
            len(cells),
            list(range(len(old_rows))),
            len(old_rows),
            len(footprint_rows),
            len(bucket_rows),
            b_token_count,
            list(COMPARISON_METHODS),
            list(CHRONOLOGIES),
            list(HISTOGRAM_KEY_FIELDS),
            TEMPLATE_FIELD_ORDERS,
            SOURCE_CELL_ORDER,
        ],
        *old_rows,
        *footprint_rows,
        *bucket_rows,
    ]
    for source_cell_index, cell in enumerate(cells):
        cell_load_records = []
        derived_odd = []
        derived_cell_value = 0
        for old_index, load in enumerate(cell["loads"]):
            if load["old_token_id"] != old_rows[old_index][2]:
                raise WireFormatError("logical cell old-load order differs")
            derived_load_value = 0
            for local_footprint, histogram in enumerate(load["histograms"]):
                footprint_index = old_rows[old_index][6] + local_footprint
                masks = []
                one_count = 0
                for bucket in histogram["buckets"]:
                    mask = _logical_hex_mask(bucket["mask"])
                    if bucket["count"] != bin(mask).count("1"):  # noqa: FURB161
                        raise WireFormatError("logical bucket count differs")
                    bucket_index = bucket_indices[
                        canonical_json(_bucket_class_values(bucket["key"]))
                    ]
                    wire_mask = pack_mask(mask)
                    masks.append(wire_mask)
                    one_count += (
                        bucket["count"]
                        * bucket["key"]["contribution_bit"]
                    )
                    cell_load_records.append(
                        [
                            "load",
                            old_index,
                            footprint_index,
                            bucket_index,
                            wire_mask,
                        ]
                    )
                validate_mask_partition(masks)
                histogram_value = one_count % 2
                if (
                    histogram["comparison_count"] != TOKEN_COUNT
                    or histogram["one_count"] != one_count
                    or histogram["value"] != histogram_value
                ):
                    raise WireFormatError("logical histogram summary differs")
                derived_load_value ^= histogram_value
            if load["value"] != derived_load_value:
                raise WireFormatError("logical load value differs")
            if derived_load_value:
                derived_odd.append(old_index)
            derived_cell_value ^= derived_load_value
        cell_load_records.sort(key=lambda row: (row[1], row[2], row[3]))
        records.extend(cell_load_records)
        expected_odd_ids = [
            f"{family}|{cell['cell_id']}|{old_rows[index][2]}"
            for index in derived_odd
        ]
        if (
            cell["odd_load_ids"] != expected_odd_ids
            or cell["value"] != derived_cell_value
        ):
            raise WireFormatError("logical cell parity differs")
        records.append(
            [
                "cell_footer",
                source_cell_index,
                compact_cell_indices[cell["cell_id"]],
                cell["cell_id"],
                derived_odd,
                derived_cell_value,
                len(cell_load_records),
            ]
        )

    records.append(
        [
            "template_header",
            catalog["format"],
            catalog["typed_encoding"],
            family,
            catalog["field_orders"],
            catalog["identity_order"],
            catalog["schema_count"],
            catalog["cell_count"],
            catalog["template_count"],
            catalog["witness_count"],
        ]
    )
    records.extend(
        [
            "template_schema",
            schema_index,
            schema_id,
            variables_row,
            blocks,
        ]
        for schema_index, (schema_id, variables_row, blocks) in enumerate(
            catalog["schema_table"]
        )
    )
    records.extend(
        [
            "template_cell",
            cell_index,
            cell_id,
            names,
            states,
            base_values,
        ]
        for cell_index, (
            cell_id,
            names,
            states,
            base_values,
        ) in enumerate(catalog["cell_table"])
    )
    records.extend(
        [
            "template_witness",
            witness_id,
            terminal,
            terminal_deleted,
            pumps,
        ]
        for witness_id, (
            terminal,
            terminal_deleted,
            pumps,
        ) in enumerate(catalog["witness_table"])
    )
    identities = catalog["identity_witness_ids"]
    for start in range(0, len(identities), IDENTITY_CHUNK_SIZE):
        records.append(
            [
                "template_identity_chunk",
                start,
                identities[start : start + IDENTITY_CHUNK_SIZE],
            ]
        )
    records.append(
        [
            "template_footer",
            catalog["identity_sha256"],
            catalog["replay_sha256"],
            catalog["catalog_sha256"],
        ]
    )
    expected_summary = {
        "load_rows": len(cells) * len(old_rows),
        "occurrence_loads": len(cells) * len(footprint_rows),
        "comparisons": len(cells) * len(footprint_rows) * TOKEN_COUNT,
    }
    if ledger["summary"] != expected_summary:
        raise WireFormatError("logical family summary differs")
    prefix_bytes = sum(len(canonical_json_line(row)) for row in records)
    records.append(
        [
            "family_footer",
            len(cells),
            len(old_rows),
            expected_summary["load_rows"],
            expected_summary["occurrence_loads"],
            expected_summary["comparisons"],
            len(records),
            prefix_bytes,
        ]
    )
    for row in records:
        metrics.record(row[0], len(canonical_json_line(row)))
    metrics.add_stage("encode_family", time.perf_counter() - started)
    return tuple(tuple(row) for row in records)


def _record_count_map(
    records: Sequence[Sequence[Any]],
    declarations: Mapping[str, Sequence[str]],
) -> dict[str, int]:
    counts = {tag: 0 for tag in declarations}
    for record in records:
        if record[0] not in counts:
            raise WireFormatError(f"unknown record tag: {record[0]}")
        counts[record[0]] += 1
    return counts


def encode_tiny_v2_package(
    logical_v1: Mapping[str, Any],
    *,
    scope: str = PREFLIGHT_SCOPE,
    metrics: PhaseMetrics | None = None,
) -> EncodedV2Package:
    active_metrics = metrics if metrics is not None else PhaseMetrics()
    expected_status = {
        PREFLIGHT_SCOPE: PREFLIGHT_STATUS,
        PRODUCTION_SCOPE: PRODUCTION_STATUS,
    }.get(scope)
    if expected_status is None:
        raise WireFormatError("unknown package scope")
    expected_top_fields = {
        "format",
        "domain",
        "status",
        "summary",
        "dependency_digests",
        "source_bindings",
        "b_identity_table",
        "b_identity_digest",
        "family_ledgers",
    }
    if set(logical_v1) != expected_top_fields:
        raise WireFormatError("logical-v1 top-level fields differ")
    if (
        logical_v1["format"] != LOGICAL_V1_FORMAT
        or logical_v1["status"] != expected_status
    ):
        raise WireFormatError("logical-v1 format/status differs")
    if set(logical_v1["family_ledgers"]) != set(FAMILY_ORDER):
        raise WireFormatError("logical-v1 family ledgers differ")
    source_digest = logical_v1["source_bindings"].get("sha256")
    _exact_hash(source_digest, "source-binding digest")
    b_identity_digest = hashlib.sha256(
        canonical_json(logical_v1["b_identity_table"]).encode("ascii")
    ).hexdigest()
    if logical_v1["b_identity_digest"] != b_identity_digest:
        raise WireFormatError("logical-v1 B identity digest differs")

    shard_records = {
        "shared": _encode_shared_records(
            logical_v1, scope=scope, metrics=active_metrics
        )
    }
    for family in FAMILY_ORDER:
        shard_records[family] = _encode_family_records(
            family,
            logical_v1["family_ledgers"][family],
            b_token_count=len(logical_v1["b_identity_table"]),
            metrics=active_metrics,
        )
    objects = {}
    descriptors = []
    for role in SHARD_ORDER:
        records = shard_records[role]
        payload = b"".join(canonical_json_line(record) for record in records)
        digest = hashlib.sha256(payload).hexdigest()
        path = f"objects/{digest}.jsonl"
        objects[path] = payload
        family = None if role == "shared" else role
        declarations = (
            SHARED_RECORD_FIELDS if family is None else FAMILY_RECORD_FIELDS
        )
        descriptors.append(
            {
                "role": "shared" if family is None else "family",
                "family": family,
                "path": path,
                "sha256": digest,
                "total_bytes": len(payload),
                "record_count": len(records),
                "record_counts": _record_count_map(records, declarations),
            }
        )
    template_catalogs = {
        family: _catalog_summary(
            logical_v1["family_ledgers"][family]["template_catalog"]
        )
        for family in FAMILY_ORDER
    }
    root_without_hash = {
        "format": PACKAGE_V2_FORMAT,
        "scope": scope,
        "logical_v1_format": LOGICAL_V1_FORMAT,
        "canonical_encoding": CANONICAL_LINE_ENCODING,
        "mask_encoding": MASK_ENCODING,
        "domain": logical_v1["domain"],
        "status": logical_v1["status"],
        "shard_order": list(SHARD_ORDER),
        "shards": descriptors,
        "shard_bytes_total": sum(
            descriptor["total_bytes"] for descriptor in descriptors
        ),
        "emitted_summary": logical_v1["summary"],
        "full_summary": logical_v1["summary"],
        "source_bindings_sha256": source_digest,
        "b_identity_digest": logical_v1["b_identity_digest"],
        "template_catalogs": template_catalogs,
    }
    root_hash = hashlib.sha256(
        canonical_json_line(root_without_hash)
    ).hexdigest()
    root = {**root_without_hash, "root_sha256": root_hash}
    index_bytes = canonical_json_line(root)
    active_metrics.record("root_index", len(index_bytes))
    return EncodedV2Package(
        index=root,
        index_bytes=index_bytes,
        objects=objects,
        shard_records=shard_records,
    )


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    descriptor = os.open(str(path), flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _file_sha256(path: Path, *, chunk_size: int = 1 << 20) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def _bounded_files_equal(
    left: Path, right: Path, *, chunk_size: int = 1 << 20
) -> bool:
    if left.stat().st_size != right.stat().st_size:
        return False
    with left.open("rb") as left_handle, right.open("rb") as right_handle:
        while True:
            left_chunk = left_handle.read(chunk_size)
            right_chunk = right_handle.read(chunk_size)
            if left_chunk != right_chunk:
                return False
            if not left_chunk:
                return True


def _inject_publication_failure(
    injector: Any, stage: str, detail: str
) -> None:
    if injector is not None:
        injector(stage, detail)


def publish_v2_package(
    encoded: EncodedV2Package,
    index_path: Path,
    *,
    package_cap: int = PACKAGE_BYTE_CAP,
    failure_injector: Any = None,
    metrics: PhaseMetrics | None = None,
) -> PublicationResult:
    active_metrics = metrics if metrics is not None else PhaseMetrics()
    target = _project_local_path(Path(index_path))
    _exact_int(package_cap, "package cap", minimum=1)
    target.parent.mkdir(parents=True, exist_ok=True)
    objects_dir = target.parent / "objects"
    objects_dir.mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    reused: list[str] = []
    temporary_paths: list[Path] = []
    state = "PREPARED"
    stage = "object_temp_fsynced"
    write_started = time.perf_counter()
    try:
        for descriptor in encoded.index["shards"]:
            relative_path = descriptor["path"]
            payload = encoded.objects[relative_path]
            destination = target.parent / relative_path
            if destination.parent != objects_dir:
                raise WireFormatError("object path escapes the object directory")
            with tempfile.NamedTemporaryFile(
                dir=objects_dir,
                prefix=".object.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                temporary = Path(handle.name)
                temporary_paths.append(temporary)
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            stage = "object_temp_fsynced"
            _inject_publication_failure(
                failure_injector, stage, relative_path
            )
            if destination.exists():
                stage = "object_reuse_check"
                if (
                    _file_sha256(destination) != descriptor["sha256"]
                    or not _bounded_files_equal(destination, temporary)
                ):
                    raise WireFormatError(
                        f"reused content-addressed object differs: {relative_path}"
                    )
                temporary.unlink()
                temporary_paths.remove(temporary)
                reused.append(relative_path)
                continue
            os.replace(temporary, destination)
            temporary_paths.remove(temporary)
            created.append(relative_path)
            stage = "object_replaced"
            _inject_publication_failure(
                failure_injector, stage, relative_path
            )
            _fsync_directory(objects_dir)
            stage = "objects_dir_fsynced"
            _inject_publication_failure(
                failure_injector, stage, relative_path
            )
        active_metrics.add_stage(
            "write_objects", time.perf_counter() - write_started
        )

        publish_started = time.perf_counter()
        with tempfile.NamedTemporaryFile(
            dir=target.parent,
            prefix=f".{target.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            index_temporary = Path(handle.name)
            temporary_paths.append(index_temporary)
            handle.write(encoded.index_bytes)
            handle.flush()
            os.fsync(handle.fileno())
        stage = "index_temp_fsynced"
        _inject_publication_failure(
            failure_injector, stage, target.name
        )
        package_bytes = (
            encoded.index["shard_bytes_total"] + len(encoded.index_bytes)
        )
        stage = "before_index_replace"
        if (
            encoded.index["scope"] == PRODUCTION_SCOPE
            and package_bytes > package_cap
        ):
            raise WireFormatError(
                f"production package exceeds byte cap: {package_bytes}"
            )
        _inject_publication_failure(
            failure_injector, stage, target.name
        )
        os.replace(index_temporary, target)
        temporary_paths.remove(index_temporary)
        state = "COMMITTED"
        stage = "index_replaced"
        _inject_publication_failure(
            failure_injector, stage, target.name
        )
        _fsync_directory(target.parent)
        stage = "index_dir_fsynced"
        _inject_publication_failure(
            failure_injector, stage, target.name
        )
        active_metrics.add_stage(
            "publish_index", time.perf_counter() - publish_started
        )
        return PublicationResult(
            state=state,
            index_sha256=hashlib.sha256(encoded.index_bytes).hexdigest(),
            root_sha256=encoded.index["root_sha256"],
            package_bytes=package_bytes,
            created_objects=tuple(created),
            reused_objects=tuple(reused),
        )
    except BaseException as cause:
        for temporary in tuple(temporary_paths):
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
        if state == "PREPARED":
            changed_objects = False
            for relative_path in reversed(created):
                destination = target.parent / relative_path
                if destination.exists():
                    destination.unlink()
                    changed_objects = True
            if changed_objects:
                _fsync_directory(objects_dir)
            _fsync_directory(target.parent)
        raise PublicationFailure(state, stage, cause) from cause


if __name__ == "__main__":
    raise SystemExit(main())
