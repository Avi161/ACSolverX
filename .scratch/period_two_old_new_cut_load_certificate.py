from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import tempfile
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


def _template_record_body(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in record.items()
        if key not in {"schema_id", "cell_id"}
    }


def _template_body_digest(body: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(body).encode("ascii")).hexdigest()


def _template_catalog_digest(
    mapping: Mapping[str, str], records: Mapping[str, Mapping[str, Any]]
) -> str:
    payload = canonical_json({"mapping": mapping, "records": records})
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def build_task4_schema_catalog(context: SourceContext) -> Task4SchemaCatalog:
    b_tokens, _ = build_b_catalog(context)
    b_identity_table = _b_identity_table(b_tokens)
    old_tokens, _ = build_old_rows(context)
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
    template_mapping: dict[str, str] = {}
    template_records: dict[str, Mapping[str, Any]] = {}
    family_comparisons = 0
    family_occurrence_loads = 0
    for cell in item.cells:
        templates = {
            schema_id: build_template(schema, cell)
            for schema_id, schema in item.schemas.items()
        }
        for schema_id, template in templates.items():
            identity = f"{schema_id}|{cell.cell_id}"
            if identity in template_mapping:
                raise CertificateFailure(
                    f"duplicate template identity: {item.family}, {identity}"
                )
            body = _template_record_body(template.to_record())
            body_digest = _template_body_digest(body)
            prior = template_records.setdefault(body_digest, body)
            if canonical_json(prior) != canonical_json(body):
                raise CertificateFailure(
                    f"template body digest collision: {body_digest}"
                )
            template_mapping[identity] = body_digest
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
        "template_catalog": {
            "template_count": len(template_mapping),
            "record_count": len(template_records),
            "mapping": template_mapping,
            "records": template_records,
            "digest": _template_catalog_digest(
                template_mapping, template_records
            ),
        },
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
    manifest = {
        "format": "period-two-old-new-cut-load-v1",
        "domain": "a=d-1>=0, n>=0; positive chamber d>=1",
        "status": "unverified",
        "summary": summary,
        "dependency_digests": dict(catalog.dependency_digests),
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


if __name__ == "__main__":
    raise SystemExit(main())
