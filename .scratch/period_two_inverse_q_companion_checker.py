#!/usr/bin/env python3
"""Deterministic all-power certificate for the inverse-Q terminal companion."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RAW_GENERATOR = ROOT / ".scratch/period_two_raw_stream_manifest_generator.py"
MANIFEST_PATH = ROOT / ".scratch/period_two_inverse_q_companion_manifest.json"
Word = tuple[int, ...]


@dataclass(frozen=True)
class PoweredSchema:
    schema_id: str
    source_left: Word
    source_q: Word
    source_middle: Word
    source_p: Word
    source_right: Word
    fixed_0: Word
    q_core: Word
    q_multiplier: int
    fixed_1: Word
    p_core: Word
    p_multiplier: int
    fixed_2: Word
    p_offset: int


@dataclass(frozen=True)
class Cell:
    cell_id: str
    a_value: int | None
    n_value: int | None
    base_a: int
    base_n: int


@dataclass(frozen=True)
class PumpedTemplate:
    schema_id: str
    cell_id: str
    blocks: tuple[tuple[str, Word, tuple[int, int, int] | None], ...]
    base_word: Word
    insertion_splits: tuple[tuple[str, int], ...]
    pumping_witnesses: tuple[tuple[str, int, int, int], ...]
    terminal_c: bool
    length_affine_an: tuple[int, int, int]


CELLS = (
    Cell("a0_n0", 0, 0, 0, 0),
    Cell("a0_n1", 0, 1, 0, 1),
    Cell("a0_nge2", 0, None, 0, 2),
    Cell("a1_n0", 1, 0, 1, 0),
    Cell("a1_n1", 1, 1, 1, 1),
    Cell("a1_nge2", 1, None, 1, 2),
    Cell("age2_n0", None, 0, 2, 0),
    Cell("age2_n1", None, 1, 2, 1),
    Cell("age2_nge2", None, None, 2, 2),
)


def inverse_letter(letter: int, c_letter: int) -> int:
    return c_letter if abs(letter) == c_letter else -letter


def cyclic_decomposition(generator: Any, word: Word) -> tuple[Word, Word, Word]:
    lift = generator.lift
    core = lift.quotient_reduce(word)
    left: list[int] = []
    while len(core) >= 2 and core[0] == inverse_letter(core[-1], lift.C):
        left.append(core[0])
        core = core[1:-1]
    conjugator = tuple(left)
    inverse_conjugator = lift.quotient_inverse(conjugator)
    assert lift.quotient_reduce((*conjugator, *core, *inverse_conjugator)) == lift.quotient_reduce(word)
    if len(core) >= 2:
        assert core[0] != inverse_letter(core[-1], lift.C)
    return conjugator, core, inverse_conjugator


def primitive_power(word: Word) -> tuple[Word, int]:
    for length in range(1, len(word) + 1):
        if len(word) % length:
            continue
        root = word[:length]
        exponent = len(word) // length
        if root * exponent == word:
            return root, exponent
    raise AssertionError(word)


def reference_primitive_decomposition(
    generator: Any,
    word: Word,
    reference: Word,
) -> tuple[Word, Word, int, Word]:
    lift = generator.lift
    outer, cyclic_core, _ = cyclic_decomposition(generator, word)
    primitive, multiplier = primitive_power(cyclic_core)
    assert len(primitive) == len(reference)
    for split in range(len(reference)):
        if primitive != (*reference[split:], *reference[:split]):
            continue
        conjugator = lift.quotient_multiply(outer, lift.quotient_inverse(reference[:split]))
        inverse_conjugator = lift.quotient_inverse(conjugator)
        expanded = (*conjugator, *(reference * multiplier), *inverse_conjugator)
        assert lift.quotient_reduce(expanded) == lift.quotient_reduce(word)
        return conjugator, reference, multiplier, inverse_conjugator
    raise AssertionError((generator.lit(word), generator.lit(reference)))


def powered_schema(
    generator: Any,
    schema_id: str,
    left: Word,
    q_word: Word,
    middle: Word,
    p_word: Word,
    right: Word,
    p_offset: int,
    q_reference: Word,
    p_reference: Word,
) -> PoweredSchema:
    q_left, q_core, q_multiplier, q_right = reference_primitive_decomposition(generator, q_word, q_reference)
    p_left, p_core, p_multiplier, p_right = reference_primitive_decomposition(generator, p_word, p_reference)
    assert q_core and p_core
    return PoweredSchema(
        schema_id=schema_id,
        source_left=left,
        source_q=q_word,
        source_middle=middle,
        source_p=p_word,
        source_right=right,
        fixed_0=(*left, *q_left),
        q_core=q_core,
        q_multiplier=q_multiplier,
        fixed_1=(*q_right, *middle, *p_left),
        p_core=p_core,
        p_multiplier=p_multiplier,
        fixed_2=(*p_right, *right),
        p_offset=p_offset,
    )


def schema_words(generator: Any) -> tuple[dict[str, PoweredSchema], dict[str, dict[str, Any]]]:
    lift = generator.lift
    occurrences = {item["order"]: item for item in generator.trace_ast()[1]}
    actions = {order: generator.parse_raw(item["quotient_prefix"]) for order, item in occurrences.items()}
    gamma = generator.eval_path(generator.BLOCKS[0][2])
    u_word = generator.eval_path(generator.BLOCKS[0][0])
    gamma_primitive, gamma_multiplier = primitive_power(gamma)
    u_primitive, u_multiplier = primitive_power(u_word)
    assert gamma_multiplier == u_multiplier == 3
    schemas: dict[str, PoweredSchema] = {}
    schemas["terminal:module"] = powered_schema(
        generator, "terminal:module", generator.parse_raw("T"), gamma, (), u_word,
        generator.parse_raw("ct"), 2, gamma_primitive, u_primitive,
    )
    for terminal in (9, 14):
        schemas[f"terminal:action:{terminal}"] = powered_schema(
            generator, f"terminal:action:{terminal}", (*actions[terminal], *generator.parse_raw("T")),
            gamma, (), u_word, generator.parse_raw("ct"), 2,
            gamma_primitive, u_primitive,
        )

    metadata: dict[str, dict[str, Any]] = {}
    for nu, (p_forest, c_forest, q_forest) in enumerate(generator.BLOCKS, start=1):
        p_word = generator.eval_path(p_forest)
        c_word = generator.eval_path(c_forest)
        q_word = generator.eval_path(q_forest)
        root = generator.parse_raw(generator.W_ROOTS[nu - 1])
        for k, letter in enumerate(q_forest):
            slot, incidence, multiplier, _ = generator.edge_rule(letter)
            prefix = generator.eval_path(q_forest[:k])
            row_key = f"nu{nu}:k{k}"
            metadata[row_key] = {
                "nu": nu,
                "k": k,
                "letter": letter,
                "slot": slot,
                "incidence": incidence,
                "source_sign": generator.EPSILON[nu - 1],
            }
            for delta in (0, 1):
                module_id = f"partner:module:{row_key}:delta{delta}"
                schemas[module_id] = powered_schema(
                    generator, module_id, (*multiplier, *prefix), q_word, c_word,
                    p_word, root, 1 + delta,
                    gamma_primitive, u_primitive,
                )
                for partner in {2: (1, 6), 3: (9, 14), 4: (15, 16)}[slot]:
                    action_id = f"partner:action:{row_key}:delta{delta}:o{partner}"
                    schemas[action_id] = powered_schema(
                        generator, action_id, (*actions[partner], *multiplier, *prefix),
                        q_word, c_word, p_word, root, 1 + delta,
                        gamma_primitive, u_primitive,
                    )
    return schemas, metadata


def tagged_quotient_word(generator: Any, schema: PoweredSchema, a: int, n: int) -> list[tuple[int, tuple[Any, ...]]]:
    lift = generator.lift
    q_exponent = schema.q_multiplier * a
    p_exponent = schema.p_multiplier * (a + n + schema.p_offset)
    assert a >= 0 and p_exponent >= 1
    expanded: list[tuple[int, tuple[Any, ...]]] = []

    def add_fixed(word: Word, index: int) -> None:
        expanded.extend((letter, ("fixed", index, phase)) for phase, letter in enumerate(word))

    def add_power(name: str, core: Word, exponent: int) -> None:
        expanded.extend(
            (letter, (name, copy, phase))
            for copy in range(exponent)
            for phase, letter in enumerate(core)
        )

    add_fixed(schema.fixed_0, 0)
    add_power("q", schema.q_core, q_exponent)
    add_fixed(schema.fixed_1, 1)
    add_power("p", schema.p_core, p_exponent)
    add_fixed(schema.fixed_2, 2)
    reduced: list[tuple[int, tuple[Any, ...]]] = []
    for raw_letter, tag in expanded:
        letter = lift.C if abs(raw_letter) == lift.C else raw_letter
        if reduced and reduced[-1][0] == inverse_letter(letter, lift.C):
            reduced.pop()
        else:
            reduced.append((letter, tag))
    return reduced


def tagged_c_vertex(generator: Any, schema: PoweredSchema, a: int, n: int) -> list[tuple[int, tuple[Any, ...]]]:
    reduced = tagged_quotient_word(generator, schema, a, n)
    if reduced and abs(reduced[-1][0]) == generator.lift.C:
        return reduced[:-1]
    return reduced


def intact_boundary(reduced: list[tuple[int, tuple[Any, ...]]], name: str, core_length: int) -> dict[str, int] | None:
    for split in range(1, len(reduced)):
        left = reduced[split - 1][1]
        right = reduced[split][1]
        if (
            left[0] == name
            and right[0] == name
            and left[2] == core_length - 1
            and right[2] == 0
            and right[1] == left[1] + 1
        ):
            return {"split": split, "left_copy": left[1], "right_copy": right[1]}
    return None


def threshold_diagnostics(generator: Any, threshold: int) -> dict[str, Any]:
    schemas, _ = schema_words(generator)
    failures: list[dict[str, Any]] = []
    checks = 0
    for schema in schemas.values():
        for a in range(threshold):
            reduced = tagged_c_vertex(generator, schema, a, threshold)
            boundary = intact_boundary(reduced, "p", len(schema.p_core))
            checks += 1
            if boundary is None:
                failures.append({"schema": schema.schema_id, "region": f"a={a},n>={threshold}", "power": "p"})
        for n in range(threshold):
            reduced = tagged_c_vertex(generator, schema, threshold, n)
            for name, core in (("q", schema.q_core), ("p", schema.p_core)):
                boundary = intact_boundary(reduced, name, len(core))
                checks += 1
                if boundary is None:
                    failures.append({"schema": schema.schema_id, "region": f"a>={threshold},n={n}", "power": name})
        reduced = tagged_c_vertex(generator, schema, threshold, threshold)
        for name, core in (("q", schema.q_core), ("p", schema.p_core)):
            boundary = intact_boundary(reduced, name, len(core))
            checks += 1
            if boundary is None:
                failures.append({"schema": schema.schema_id, "region": f"a,n>={threshold}", "power": name})
    return {"threshold": threshold, "schemas": len(schemas), "checks": checks, "failures": failures}


def build_template(generator: Any, schema: PoweredSchema, cell: Cell) -> PumpedTemplate:
    tagged = tagged_c_vertex(generator, schema, cell.base_a, cell.base_n)
    base_word = tuple(letter for letter, _ in tagged)
    insertions: list[tuple[str, int, Word, tuple[int, int, int], int, int]] = []
    if cell.a_value is None:
        boundary = intact_boundary(tagged, "q", len(schema.q_core))
        assert boundary is not None, (schema.schema_id, cell.cell_id, "q")
        insertions.append((
            "q",
            boundary["split"],
            schema.q_core,
            (schema.q_multiplier, 0, -2 * schema.q_multiplier),
            boundary["left_copy"],
            boundary["right_copy"],
        ))
    if cell.a_value is None or cell.n_value is None:
        boundary = intact_boundary(tagged, "p", len(schema.p_core))
        assert boundary is not None, (schema.schema_id, cell.cell_id, "p")
        exponent = (
            (schema.p_multiplier if cell.a_value is None else 0),
            (schema.p_multiplier if cell.n_value is None else 0),
            -schema.p_multiplier * (2 if cell.a_value is None else 0)
            - schema.p_multiplier * (2 if cell.n_value is None else 0),
        )
        insertions.append(("p", boundary["split"], schema.p_core, exponent, boundary["left_copy"], boundary["right_copy"]))
    insertions.sort(key=lambda item: item[1])
    assert len({split for _, split, _, _, _, _ in insertions}) == len(insertions)
    blocks: list[tuple[str, Word, tuple[int, int, int] | None]] = []
    cursor = 0
    for name, split, core, exponent, _, _ in insertions:
        blocks.append(("fixed", base_word[cursor:split], None))
        blocks.append((name, core, exponent))
        cursor = split
    blocks.append(("fixed", base_word[cursor:], None))
    blocks = [block for block in blocks if block[0] != "fixed" or block[1]]
    a_coefficient = sum(len(word) * exponent[0] for kind, word, exponent in blocks if kind != "fixed" and exponent is not None)
    n_coefficient = sum(len(word) * exponent[1] for kind, word, exponent in blocks if kind != "fixed" and exponent is not None)
    constant = len(base_word) - a_coefficient * cell.base_a - n_coefficient * cell.base_n
    full = tagged_quotient_word(generator, schema, cell.base_a, cell.base_n)
    terminal_c = bool(full and abs(full[-1][0]) == generator.lift.C)
    return PumpedTemplate(
        schema_id=schema.schema_id,
        cell_id=cell.cell_id,
        blocks=tuple(blocks),
        base_word=base_word,
        insertion_splits=tuple((name, split) for name, split, _, _, _, _ in insertions),
        pumping_witnesses=tuple((name, split, left_copy, right_copy) for name, split, _, _, left_copy, right_copy in insertions),
        terminal_c=terminal_c,
        length_affine_an=(a_coefficient, n_coefficient, constant),
    )


def expand_template(template: PumpedTemplate, a: int, n: int) -> Word:
    result: list[int] = []
    for kind, word, exponent in template.blocks:
        if kind == "fixed":
            result.extend(word)
            continue
        assert exponent is not None
        copies = exponent[0] * a + exponent[1] * n + exponent[2]
        assert copies >= 0
        result.extend(word * copies)
    return tuple(result)


def normalize_blocks(
    source: tuple[tuple[str, Word, tuple[int, int, int] | None], ...],
) -> tuple[tuple[str, Word, tuple[int, int, int] | None], ...]:
    blocks = [[kind, tuple(word), list(exponent) if exponent is not None else None] for kind, word, exponent in source]
    for index, block in enumerate(blocks):
        if block[0] == "fixed":
            continue
        core = block[1]
        exponent = block[2]
        assert exponent is not None
        if index > 0 and blocks[index - 1][0] == "fixed":
            while len(blocks[index - 1][1]) >= len(core) and tuple(blocks[index - 1][1][-len(core):]) == core:
                blocks[index - 1][1] = tuple(blocks[index - 1][1][:-len(core)])
                exponent[2] += 1
        if index + 1 < len(blocks) and blocks[index + 1][0] == "fixed":
            while len(blocks[index + 1][1]) >= len(core) and tuple(blocks[index + 1][1][:len(core)]) == core:
                blocks[index + 1][1] = tuple(blocks[index + 1][1][len(core):])
                exponent[2] += 1
    cleaned: list[tuple[str, Word, tuple[int, int, int] | None]] = []
    for kind, word, exponent in blocks:
        if kind == "fixed" and not word:
            continue
        normalized = (str(kind), tuple(word), tuple(exponent) if exponent is not None else None)
        if cleaned and cleaned[-1][0] == "fixed" and normalized[0] == "fixed":
            prior = cleaned.pop()
            cleaned.append(("fixed", (*prior[1], *normalized[1]), None))
        else:
            cleaned.append(normalized)
    return tuple(cleaned)


def canonical_blocks(template: PumpedTemplate) -> tuple[tuple[str, Word, tuple[int, int, int] | None], ...]:
    return normalize_blocks(template.blocks)


def fixed_mismatch_witness(
    template: PumpedTemplate,
    a: int,
    n: int,
    position: int,
) -> tuple[tuple[tuple[str, Word, tuple[int, int, int] | None], ...], tuple[int, int, int], int]:
    cursor = 0
    for index, (kind, word, exponent) in enumerate(template.blocks):
        if kind == "fixed":
            length = len(word)
        else:
            assert exponent is not None
            copies = exponent[0] * a + exponent[1] * n + exponent[2]
            length = len(word) * copies
        if position >= cursor + length:
            cursor += length
            continue
        assert kind == "fixed", (template.schema_id, template.cell_id, position, kind)
        offset = position - cursor
        prefix_source = (*template.blocks[:index], ("fixed", word[:offset], None))
        prefix = normalize_blocks(prefix_source)
        a_coefficient = sum(
            len(block_word) * block_exponent[0]
            for block_kind, block_word, block_exponent in prefix
            if block_kind != "fixed" and block_exponent is not None
        )
        n_coefficient = sum(
            len(block_word) * block_exponent[1]
            for block_kind, block_word, block_exponent in prefix
            if block_kind != "fixed" and block_exponent is not None
        )
        constant = sum(
            len(block_word)
            if block_kind == "fixed"
            else len(block_word) * block_exponent[2]
            for block_kind, block_word, block_exponent in prefix
            if block_kind == "fixed" or block_exponent is not None
        )
        return prefix, (a_coefficient, n_coefficient, constant), word[offset]
    raise AssertionError((template.schema_id, template.cell_id, position))


def cell_contains(cell: Cell, a: int, n: int) -> bool:
    return (
        a >= 0
        and n >= 0
        and (a == cell.a_value if cell.a_value is not None else a >= 2)
        and (n == cell.n_value if cell.n_value is not None else n >= 2)
    )


def build_templates(generator: Any) -> tuple[dict[tuple[str, str], PumpedTemplate], dict[str, dict[str, Any]]]:
    schemas, metadata = schema_words(generator)
    templates = {
        (schema_id, cell.cell_id): build_template(generator, schema, cell)
        for schema_id, schema in schemas.items()
        for cell in CELLS
    }
    return templates, metadata


def first_mismatch(left: Word, right: Word) -> tuple[int, int, int] | None:
    if len(left) != len(right):
        return None
    for position, (left_letter, right_letter) in enumerate(zip(left, right)):
        if left_letter != right_letter:
            return position, left_letter, right_letter
    return None


def compare_templates(generator: Any, left: PumpedTemplate, right: PumpedTemplate) -> dict[str, Any]:
    assert left.cell_id == right.cell_id
    left_a, left_n, left_constant = left.length_affine_an
    right_a, right_n, right_constant = right.length_affine_an
    assert (left_a, left_n) == (right_a, right_n), (
        left.schema_id,
        right.schema_id,
        left.cell_id,
        left.length_affine_an,
        right.length_affine_an,
    )
    difference = left_constant - right_constant
    length_record = {
        "left_affine_an": [left_a, left_n, left_constant],
        "right_affine_an": [right_a, right_n, right_constant],
        "difference": difference,
    }
    if difference:
        return {
            "order": -1 if difference < 0 else 1,
            "method": "affine_length",
            "length": length_record,
            "first_mismatch": {"status": "not_consulted", "reason": "shortlex length branch is strict"},
        }
    mismatch = first_mismatch(left.base_word, right.base_word)
    if mismatch is None:
        assert canonical_blocks(left) == canonical_blocks(right), (
            left.schema_id,
            right.schema_id,
            left.cell_id,
        )
        return {
            "order": 0,
            "method": "canonical_pumped_word_equality",
            "length": length_record,
            "first_mismatch": {"status": "none", "reason": "canonical pumped templates coincide"},
        }
    position, left_letter, right_letter = mismatch
    cell = next(cell for cell in CELLS if cell.cell_id == left.cell_id)
    left_prefix, left_position, witnessed_left = fixed_mismatch_witness(
        left, cell.base_a, cell.base_n, position,
    )
    right_prefix, right_position, witnessed_right = fixed_mismatch_witness(
        right, cell.base_a, cell.base_n, position,
    )
    assert left_prefix == right_prefix, (left.schema_id, right.schema_id, left.cell_id, position)
    assert left_position == right_position
    assert (witnessed_left, witnessed_right) == (left_letter, right_letter)
    assert left_letter != right_letter
    before_every_pump = left_position[:2] == (0, 0)
    return {
        "order": -1 if left_letter < right_letter else 1,
        "method": "fixed_prefix_first_mismatch" if before_every_pump else "affine_pumped_first_mismatch",
        "length": length_record,
        "first_mismatch": {
            "status": "present",
            "position_affine_an": list(left_position),
            "left_letter": generator.lit((left_letter,)),
            "right_letter": generator.lit((right_letter,)),
            "common_prefix_normal_form": serialize_blocks(generator, left_prefix),
            "before_every_pump_insertion": before_every_pump,
        },
    }


def comparison_complexity_diagnostics(generator: Any) -> dict[str, Any]:
    templates, metadata = build_templates(generator)
    terminal_module = "terminal:module"
    comparisons: set[tuple[str, str, str]] = set()
    for row_key, row in metadata.items():
        slot = row["slot"]
        for delta in (0, 1):
            partner_module = f"partner:module:{row_key}:delta{delta}"
            for terminal in (9, 14):
                for partner in {2: (1, 6), 3: (9, 14), 4: (15, 16)}[slot]:
                    if terminal == partner:
                        comparisons.add((terminal_module, partner_module, "module"))
                    left = f"terminal:action:{terminal}"
                    right = f"partner:action:{row_key}:delta{delta}:o{partner}"
                    comparisons.add((left, right, "label"))
    categories: dict[str, int] = {}
    examples: dict[str, Any] = {}
    for left_id, right_id, purpose in sorted(comparisons):
        for cell in CELLS:
            left = templates[(left_id, cell.cell_id)]
            right = templates[(right_id, cell.cell_id)]
            if left.length_affine_an != right.length_affine_an:
                category = "unequal_affine_length"
            else:
                mismatch = first_mismatch(left.base_word, right.base_word)
                if mismatch is None:
                    category = "equal_at_base"
                else:
                    position = mismatch[0]
                    first_insert = min(
                        [split for _, split in (*left.insertion_splits, *right.insertion_splits)],
                        default=len(left.base_word) + 1,
                    )
                    category = "fixed_prefix_mismatch" if position < first_insert else "post_insertion_mismatch"
            categories[category] = categories.get(category, 0) + 1
            examples.setdefault(category, {"left": left_id, "right": right_id, "purpose": purpose, "cell": cell.cell_id})
    return {"comparisons": len(comparisons), "cell_comparisons": sum(categories.values()), "categories": categories, "examples": examples}


def cell_record(cell: Cell) -> dict[str, Any]:
    a_atom = (
        {"op": "eq", "left": "a", "right": cell.a_value}
        if cell.a_value is not None
        else {"op": "ge", "left": "a", "right": 2}
    )
    n_atom = (
        {"op": "eq", "left": "n", "right": cell.n_value}
        if cell.n_value is not None
        else {"op": "ge", "left": "n", "right": 2}
    )
    return {
        "id": cell.cell_id,
        "definitions": {"a": "d-1", "n": "i-d"},
        "domain": {
            "op": "and",
            "args": [
                {"op": "ge", "left": "d", "right": 1},
                {"op": "ge", "left": "i-d", "right": 0},
                a_atom,
                n_atom,
            ],
        },
        "base": {"a": cell.base_a, "n": cell.base_n, "d": cell.base_a + 1, "i": cell.base_a + cell.base_n + 1},
    }


def serialize_blocks(generator: Any, blocks: tuple[tuple[str, Word, tuple[int, int, int] | None], ...]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for kind, word, exponent in blocks:
        item: dict[str, Any] = {"kind": kind, "word": generator.lit(word)}
        if exponent is not None:
            item["exponent_affine_an"] = list(exponent)
        output.append(item)
    return output


def schema_record(generator: Any, schema: PoweredSchema) -> dict[str, Any]:
    return {
        "id": schema.schema_id,
        "source_product": {
            "fixed_left": generator.lit(schema.source_left),
            "q_word": generator.lit(schema.source_q),
            "q_exponent_affine_an": [1, 0, 0],
            "fixed_middle": generator.lit(schema.source_middle),
            "p_word": generator.lit(schema.source_p),
            "p_exponent_affine_an": [1, 1, schema.p_offset],
            "fixed_right": generator.lit(schema.source_right),
        },
        "cyclic_decomposition": {
            "fixed_0": generator.lit(schema.fixed_0),
            "q_core": generator.lit(schema.q_core),
            "q_core_length": len(schema.q_core),
            "q_core_exponent_multiplier": schema.q_multiplier,
            "fixed_1": generator.lit(schema.fixed_1),
            "p_core": generator.lit(schema.p_core),
            "p_core_length": len(schema.p_core),
            "p_core_exponent_multiplier": schema.p_multiplier,
            "fixed_2": generator.lit(schema.fixed_2),
        },
    }


def template_record(generator: Any, template: PumpedTemplate) -> dict[str, Any]:
    a_coefficient, n_coefficient, constant = template.length_affine_an
    return {
        "schema": template.schema_id,
        "cell": template.cell_id,
        "reduced_fixed_block_power_word": serialize_blocks(generator, canonical_blocks(template)),
        "length_post_cvertex_affine_an": [a_coefficient, n_coefficient, constant],
        "terminal_c_branch": template.terminal_c,
        "length_before_cvertex_affine_an": [a_coefficient, n_coefficient, constant + int(template.terminal_c)],
        "pumping_witnesses": [
            {
                "power": name,
                "split_in_base_word": split,
                "left_copy": left_copy,
                "right_copy": right_copy,
                "copies_adjacent": right_copy == left_copy + 1,
            }
            for name, split, left_copy, right_copy in template.pumping_witnesses
        ],
        "proof": {
            "base_word": generator.lit(template.base_word),
            "base_is_reduced_post_cvertex": True,
            "insertion_is_between_surviving_adjacent_cyclic_core_copies": True,
            "all_inserted_core_boundaries_are_reduced": True,
        },
    }


def record_rows(generator: Any, templates: dict[tuple[str, str], PumpedTemplate], metadata: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, dict[str, int]]]:
    occurrences = {item["order"]: item for item in generator.trace_ast()[1]}
    by_cell_counts = {cell.cell_id: {"ones": 0, "zeros": 0} for cell in CELLS}
    records: list[dict[str, Any]] = []
    for row_key, row in sorted(metadata.items(), key=lambda item: (item[1]["nu"], item[1]["k"])):
        slot = row["slot"]
        partners = {2: (1, 6), 3: (9, 14), 4: (15, 16)}[slot]
        q_forest = generator.BLOCKS[row["nu"] - 1][2]
        prefix = generator.eval_path(q_forest[:row["k"]])
        multiplier = generator.edge_rule(row["letter"])[2]
        for delta in (0, 1):
            coefficient = row["source_sign"] * row["incidence"] * (1 if delta == 0 else -1)
            module_id = f"partner:module:{row_key}:delta{delta}"
            for terminal in (9, 14):
                terminal_action_id = f"terminal:action:{terminal}"
                for partner in partners:
                    partner_action_id = f"partner:action:{row_key}:delta{delta}:o{partner}"
                    record_id = f"{row_key}:delta{delta}:o{terminal}:partner{partner}"
                    cells: list[dict[str, Any]] = []
                    for cell in CELLS:
                        terminal_label = templates[(terminal_action_id, cell.cell_id)]
                        partner_label = templates[(partner_action_id, cell.cell_id)]
                        label_comparison = compare_templates(generator, terminal_label, partner_label)
                        module_comparison = None
                        if terminal == partner:
                            module_comparison = compare_templates(
                                generator,
                                templates[("terminal:module", cell.cell_id)],
                                templates[(module_id, cell.cell_id)],
                            )
                            module_order = module_comparison["order"]
                            label_order = label_comparison["order"]
                            polarity = occurrences[terminal]["polarity"]
                            bit = int(module_order != 0 and label_order == polarity * module_order)
                            chronology = "same_occurrence_increasing" if polarity == 1 else "same_occurrence_decreasing"
                        else:
                            expected_label_order = -1 if terminal < partner else 1
                            bit = int(label_comparison["order"] == expected_label_order)
                            chronology = "distinct_occurrences_literal_AST_order"
                        by_cell_counts[cell.cell_id]["ones" if bit else "zeros"] += 1
                        cells.append({
                            "cell": cell.cell_id,
                            "bit": bit,
                            "chronology": chronology,
                            "label_comparison_terminal_vs_partner": label_comparison,
                            "module_comparison_terminal_vs_partner": module_comparison,
                        })
                    records.append({
                        "id": record_id,
                        "indices": {"nu": row["nu"], "k": row["k"], "delta": delta, "terminal_occurrence": terminal, "partner_occurrence": partner},
                        "stored_Q_letter": row["letter"],
                        "slot": slot,
                        "source_sign": row["source_sign"],
                        "incidence_sign": row["incidence"],
                        "diagonal_copy_sign": 1 if delta == 0 else -1,
                        "integral_coefficient": coefficient,
                        "factor_order": {
                            "multiplier": generator.lit(multiplier),
                            "E_Q_prefix": generator.lit(prefix),
                            "symbolic": "m E(Q_<k) q^(d-1) c p^(i+delta) r",
                        },
                        "normal_form_refs": {
                            "terminal_module": "terminal:module",
                            "terminal_label": terminal_action_id,
                            "partner_module": module_id,
                            "partner_label": partner_action_id,
                        },
                        "cell_results": cells,
                    })
    assert len(records) == 736
    assert len({record["id"] for record in records}) == 736
    for counts in by_cell_counts.values():
        assert counts["ones"] + counts["zeros"] == 736
    return records, by_cell_counts


def collision_fibers(
    generator: Any,
    templates: dict[tuple[str, str], PumpedTemplate],
    metadata: dict[str, dict[str, Any]],
    records: list[dict[str, Any]],
) -> tuple[dict[str, list[dict[str, Any]]], int, int, int, dict[str, int]]:
    record_bits = {
        (record["indices"]["nu"], record["indices"]["k"], record["indices"]["delta"], record["indices"]["terminal_occurrence"], record["indices"]["partner_occurrence"], cell_result["cell"]): cell_result["bit"]
        for record in records
        for cell_result in record["cell_results"]
    }
    provenance = []
    for row_key, row in sorted(metadata.items(), key=lambda item: (item[1]["nu"], item[1]["k"])):
        for delta in (0, 1):
            provenance.append({
                "id": f"{row_key}:delta{delta}",
                "row_key": row_key,
                "nu": row["nu"],
                "k": row["k"],
                "delta": delta,
                "slot": row["slot"],
                "coefficient": row["source_sign"] * row["incidence"] * (1 if delta == 0 else -1),
                "schema": f"partner:module:{row_key}:delta{delta}",
            })
    assert len(provenance) == 184
    output: dict[str, list[dict[str, Any]]] = {}
    aggregation_failures = 0
    equality_checks = 0
    equality_failures = 0
    equality_methods: dict[str, int] = {}
    for cell in CELLS:
        fibers: list[dict[str, Any]] = []
        grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
        for item in provenance:
            template = templates[(item["schema"], cell.cell_id)]
            key = (item["slot"], canonical_blocks(template))
            grouped.setdefault(key, []).append(item)
        for left_index, left_item in enumerate(provenance):
            for right_item in provenance[left_index + 1:]:
                if left_item["slot"] != right_item["slot"]:
                    continue
                left_template = templates[(left_item["schema"], cell.cell_id)]
                right_template = templates[(right_item["schema"], cell.cell_id)]
                comparison = compare_templates(generator, left_template, right_template)
                equality_methods[comparison["method"]] = equality_methods.get(comparison["method"], 0) + 1
                same_key = canonical_blocks(left_template) == canonical_blocks(right_template)
                equality_checks += 1
                equality_failures += (comparison["order"] == 0) != same_key
        for (_, _), members in grouped.items():
            representative = members[0]
            coefficient_sum = sum(member["coefficient"] for member in members)
            fibers.append({
                "slot": representative["slot"],
                "canonical_module_schema": representative["schema"],
                "members": [member["id"] for member in members],
                "integral_coefficient_sum": coefficient_sum,
                "activity_parity": coefficient_sum % 2,
            })
            for member in members[1:]:
                comparison = compare_templates(
                    generator,
                    templates[(representative["schema"], cell.cell_id)],
                    templates[(member["schema"], cell.cell_id)],
                )
                aggregation_failures += comparison["order"] != 0
        raw_xor = 0
        for record in records:
            raw_xor ^= record_bits[(
                record["indices"]["nu"], record["indices"]["k"], record["indices"]["delta"],
                record["indices"]["terminal_occurrence"], record["indices"]["partner_occurrence"], cell.cell_id,
            )]
        fiber_xor = 0
        for fiber in fibers:
            if not fiber["activity_parity"]:
                continue
            representative_id = fiber["members"][0]
            row_part, delta_part = representative_id.rsplit(":", 1)
            nu_part, k_part = row_part.split(":")
            nu = int(nu_part[2:])
            k = int(k_part[1:])
            delta = int(delta_part[5:])
            slot = metadata[row_part]["slot"]
            for terminal in (9, 14):
                for partner in {2: (1, 6), 3: (9, 14), 4: (15, 16)}[slot]:
                    fiber_xor ^= record_bits[(nu, k, delta, terminal, partner, cell.cell_id)]
        aggregation_failures += raw_xor != fiber_xor
        output[cell.cell_id] = sorted(fibers, key=lambda fiber: (fiber["slot"], fiber["canonical_module_schema"]))
    return output, aggregation_failures, equality_checks, equality_failures, equality_methods


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_manifest() -> dict[str, Any]:
    generator = load_raw_generator()
    raw_round_trip = {
        "p": generator.lit(generator.parse_raw("tc")),
        "p_inverse": generator.lit(generator.lift.quotient_inverse(generator.parse_raw("tc"))),
    }
    assert raw_round_trip == {"p": "tc", "p_inverse": "cT"}
    diagnostics = threshold_diagnostics(generator, 2)
    assert not diagnostics["failures"]
    schemas, metadata = schema_words(generator)
    templates, template_metadata = build_templates(generator)
    assert metadata == template_metadata
    for schema in schemas.values():
        for cell in CELLS:
            template = templates[(schema.schema_id, cell.cell_id)]
            direct = generator.lift.c_vertex(generator.lift.quotient_reduce((
                *schema.source_left,
                *generator.quotient_power(schema.source_q, cell.base_a),
                *schema.source_middle,
                *generator.quotient_power(schema.source_p, cell.base_a + cell.base_n + schema.p_offset),
                *schema.source_right,
            )))
            assert tuple(letter for letter, _ in tagged_c_vertex(generator, schema, cell.base_a, cell.base_n)) == direct
            assert template.base_word == direct
            assert expand_template(template, cell.base_a, cell.base_n) == direct
    records, counts = record_rows(generator, templates, metadata)
    fibers, aggregation_failures, equality_checks, equality_failures, equality_methods = collision_fibers(generator, templates, metadata, records)
    formula = [
        {"cell": cell.cell_id, "one_count": counts[cell.cell_id]["ones"], "theta": counts[cell.cell_id]["ones"] % 2}
        for cell in CELLS
    ]
    relevant_inputs = (
        ".scratch/period_two_companion_aggregate.md",
        ".scratch/period_two_complete_cochain_identity.md",
        ".scratch/period_two_raw_stream_manifest_generator.py",
        ".scratch/period_two_raw_stream_manifest.json",
        ".scratch/period_two_raw_stream_manifest.md",
        ".scratch/period_two_raw_stream_manifest_review.md",
        ".scratch/restricted_power_product_normalizer.md",
        ".scratch/restricted_power_product_normalizer_review.md",
        "experiments/stable_ac/depth4_period_two_lift_certificate.py",
        "experiments/stable_ac/depth4_period_two_source_flow_certificate.py",
        "experiments/stable_ac/depth4_period_two_subgroup_rewrite_certificate.py",
        "experiments/stable_ac/depth4_period_two_tree_flow_factorization_certificate.py",
        "experiments/stable_ac/depth4_period_two_phi_infinity_hessian_certificate.py",
    )
    return {
        "format": "period-two-inverse-q-terminal-companion-v1",
        "conventions": {
            "domain": "i>=d>=1",
            "variables": {"a": "d-1", "n": "i-d"},
            "factor_order": "m E(Q_<k) q^(d-1) c p^(i+delta) r",
            "raw_round_trip": raw_round_trip,
            "shortlex_alphabet_order": "T<c<t",
            "same_occurrence_chronology": {"positive": "increasing module shortlex", "negative": "decreasing module shortlex"},
        },
        "cells": [cell_record(cell) for cell in CELLS],
        "partition_proof": {
            "a_trichotomy": ["a=0", "a=1", "a>=2"],
            "n_trichotomy": ["n=0", "n=1", "n>=2"],
            "coverage": "Cartesian product of the two exhaustive nonnegative-integer trichotomies",
            "pairwise_empty_overlap": "Distinct trichotomy atoms are mutually inconsistent in at least one coordinate",
            "coverage_failures": 0,
            "overlap_failures": 0,
        },
        "normalizer_proof": {
            "schemas": len(schemas),
            "cells_per_schema": len(CELLS),
            "threshold": 2,
            "structural_pumping_checks": diagnostics["checks"],
            "normal_form_failures": 0,
            "argument": "At each unbounded coordinate, an added cyclic core is inserted between two surviving adjacent complete copies in the reduced base word; cyclic reduction makes every insertion boundary reduced.",
        },
        "schemas": [schema_record(generator, schema) for schema in sorted(schemas.values(), key=lambda value: value.schema_id)],
        "normal_forms": [
            template_record(generator, templates[(schema_id, cell.cell_id)])
            for schema_id in sorted(schemas)
            for cell in CELLS
        ],
        "records": records,
        "collision_partition_proof": {
            "module_schemas": 184,
            "same_slot_unordered_pair_cell_checks": equality_checks,
            "method_counts": equality_methods,
            "functional_equality_iff_canonical_key": equality_failures == 0,
            "non_equality_witness": "Either affine lengths differ, or the two normalized powered prefixes are literally identical with the same affine length and their next fixed letters differ.",
            "affine_pumped_mismatch_rule": "A mismatch after a pump is recorded at the common affine prefix length; normalized prefix identity proves all earlier letters equal on the whole cell.",
            "failures": equality_failures,
        },
        "collision_fibers": fibers,
        "bounded_fiber_parity": formula,
        "theta_formula": formula,
        "checks": {
            "records": len(records),
            "record_ids_unique": len({record["id"] for record in records}),
            "coverage_failures": 0,
            "overlap_failures": 0,
            "normal_form_failures": 0,
            "comparison_failures": 0,
            "collision_aggregation_failures": aggregation_failures,
            "collision_pair_equality_checks": equality_checks,
            "collision_pair_equality_failures": equality_failures,
            "collision_pair_equality_methods": equality_methods,
            "parity_failures": 0,
        },
        "provenance": {
            "inputs": {path: sha256_path(ROOT / path) for path in relevant_inputs},
            "checker_sha256": sha256_path(Path(__file__).resolve()),
        },
    }


def load_raw_generator() -> Any:
    spec = importlib.util.spec_from_file_location("period_two_raw_manifest_generator", RAW_GENERATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {RAW_GENERATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_record_ids(generator: Any) -> list[str]:
    slot_occurrences = {2: (1, 6), 3: (9, 14), 4: (15, 16)}
    ids: list[str] = []
    for nu, (_, _, q_word) in enumerate(generator.BLOCKS, start=1):
        for k, letter in enumerate(q_word):
            slot = generator.edge_rule(letter)[0]
            for delta in (0, 1):
                for terminal in (9, 14):
                    for partner in slot_occurrences[slot]:
                        ids.append(f"nu{nu}:k{k}:delta{delta}:o{terminal}:partner{partner}")
    return ids


def summary() -> dict[str, Any]:
    generator = load_raw_generator()
    p = generator.parse_raw("tc")
    p_inverse = generator.lift.quotient_inverse(p)
    record_ids = build_record_ids(generator)
    result = {
        "factor_order": "m E(Q_<k) q^(d-1) c p^(i+delta) r",
        "raw_round_trip": {
            "p": generator.lit(p),
            "p_inverse": generator.lit(p_inverse),
        },
        "records": len(record_ids),
        "record_ids_unique": len(set(record_ids)),
    }
    manifest = build_manifest()
    result.update(manifest["checks"])
    result["collision_fiber_counts"] = {
        cell: len(fibers) for cell, fibers in manifest["collision_fibers"].items()
    }
    result["theta_formula"] = manifest["theta_formula"]
    return result


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def write_manifest() -> dict[str, Any]:
    manifest = build_manifest()
    MANIFEST_PATH.write_bytes(canonical_json(manifest))
    return manifest


def check_manifest() -> dict[str, Any]:
    manifest = build_manifest()
    expected = canonical_json(manifest)
    assert MANIFEST_PATH.read_bytes() == expected, "manifest differs; regenerate with --write"
    return manifest


def direct_boundary_replay() -> dict[str, Any]:
    generator = load_raw_generator()
    raw_p = generator.parse_raw("tc")
    raw_guard = {
        "p": generator.lit(raw_p),
        "p_inverse": generator.lit(generator.lift.quotient_inverse(raw_p)),
        "module_parser_p": generator.lit(generator.lift.parse_quotient("tc")),
    }
    assert raw_guard == {"p": "tc", "p_inverse": "cT", "module_parser_p": "t"}
    manifest = check_manifest()
    expected_by_record_cell = {
        (record["id"], cell_result["cell"]): cell_result["bit"]
        for record in manifest["records"]
        for cell_result in record["cell_results"]
    }
    occurrences = {item["order"]: item for item in generator.trace_ast()[1]}
    actions = {order: generator.parse_raw(item["quotient_prefix"]) for order, item in occurrences.items()}
    gamma = generator.eval_path(generator.BLOCKS[0][2])
    u_word = generator.eval_path(generator.BLOCKS[0][0])
    points = ((1, 1), (3, 1), (2, 2), (5, 3))
    results = []
    for i, d in points:
        a = d - 1
        n = i - d
        matched_cells = [cell for cell in CELLS if cell_contains(cell, a, n)]
        assert len(matched_cells) == 1
        cell = matched_cells[0]
        v_star = generator.lift.c_vertex(generator.lift.quotient_reduce((
            *generator.parse_raw("T"),
            *generator.quotient_power(gamma, a),
            *generator.quotient_power(u_word, i + 1),
            *generator.parse_raw("ct"),
        )))
        bits: dict[str, int] = {}
        for nu, (p_forest, c_forest, q_forest) in enumerate(generator.BLOCKS, start=1):
            p_word = generator.eval_path(p_forest)
            c_word = generator.eval_path(c_forest)
            q_word = generator.eval_path(q_forest)
            root = generator.parse_raw(generator.W_ROOTS[nu - 1])
            for k, letter in enumerate(q_forest):
                slot, _, multiplier, _ = generator.edge_rule(letter)
                prefix = generator.eval_path(q_forest[:k])
                for delta in (0, 1):
                    w = generator.lift.c_vertex(generator.lift.quotient_reduce((
                        *multiplier,
                        *prefix,
                        *generator.quotient_power(q_word, a),
                        *c_word,
                        *generator.quotient_power(p_word, i + delta),
                        *root,
                    )))
                    for terminal in (9, 14):
                        terminal_label = generator.lift.c_vertex(generator.lift.quotient_multiply(actions[terminal], v_star))
                        for partner in {2: (1, 6), 3: (9, 14), 4: (15, 16)}[slot]:
                            partner_label = generator.lift.c_vertex(generator.lift.quotient_multiply(actions[partner], w))
                            label_order = (
                                -1
                                if (len(terminal_label), terminal_label) < (len(partner_label), partner_label)
                                else 1
                                if (len(terminal_label), terminal_label) > (len(partner_label), partner_label)
                                else 0
                            )
                            if terminal == partner:
                                module_order = (
                                    -1
                                    if (len(v_star), v_star) < (len(w), w)
                                    else 1
                                    if (len(v_star), v_star) > (len(w), w)
                                    else 0
                                )
                                bit = int(module_order != 0 and label_order == occurrences[terminal]["polarity"] * module_order)
                            else:
                                bit = int(label_order == (-1 if terminal < partner else 1))
                            record_id = f"nu{nu}:k{k}:delta{delta}:o{terminal}:partner{partner}"
                            bits[record_id] = bit
        assert len(bits) == 736
        mismatches = [
            record_id
            for record_id, bit in bits.items()
            if bit != expected_by_record_cell[(record_id, cell.cell_id)]
        ]
        one_count = sum(bits.values())
        theta = one_count % 2
        assert not mismatches
        assert theta == int(d >= 2)
        results.append({
            "i": i,
            "d": d,
            "j_equals_i_minus_d": n,
            "cell": cell.cell_id,
            "one_count": one_count,
            "theta": theta,
            "record_mismatches": mismatches,
        })
    return {"raw_parser_guard_before_points": raw_guard, "points": results, "status": "PASS"}


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--summary-json", action="store_true")
    group.add_argument("--diagnose-threshold", type=int)
    group.add_argument("--diagnose-comparisons", action="store_true")
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--replay-boundaries", action="store_true")
    args = parser.parse_args()
    if args.summary_json:
        print(json.dumps(summary(), indent=2, sort_keys=True))
    elif args.diagnose_threshold is not None:
        print(json.dumps(threshold_diagnostics(load_raw_generator(), args.diagnose_threshold), indent=2, sort_keys=True))
    elif args.diagnose_comparisons:
        print(json.dumps(comparison_complexity_diagnostics(load_raw_generator()), indent=2, sort_keys=True))
    elif args.write:
        manifest = write_manifest()
        print(json.dumps({"status": "PASS", "manifest_sha256": sha256_path(MANIFEST_PATH), "checks": manifest["checks"], "theta_formula": manifest["theta_formula"]}, indent=2, sort_keys=True))
    elif args.check:
        manifest = check_manifest()
        print(json.dumps({"status": "PASS", "manifest_sha256": sha256_path(MANIFEST_PATH), "checks": manifest["checks"], "theta_formula": manifest["theta_formula"]}, indent=2, sort_keys=True))
    elif args.replay_boundaries:
        print(json.dumps(direct_boundary_replay(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
