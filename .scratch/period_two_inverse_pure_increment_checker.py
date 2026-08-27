#!/usr/bin/env python3
"""All-power direct-Q certificate for the inverse pure increment.

Source bindings:

* ``period_two_raw_stream_manifest_generator.build_w_rows`` supplies the
  authoritative negative-oriented Q provenance and integral incidences;
* ``period_two_inverse_q_companion_checker`` supplies only the reviewed
  quotient normalizer primitives;
* ``period_two_residual_augmented_defect_raw_checker.raw_observable`` supplies
  the reviewed literal raw-mirror evaluator; and
* ``period_two_seven_family_covariance_checker`` supplies an independent
  direct semantic replay at the base point of every exhaustive cell.

The production path below has its own ``(e,n)`` affine schemas and templates.
It does not substitute parameters into the positive-chamber ``(a,n)``
templates.  Generation records computed values and fail-closed diagnostics;
the target value is imposed only by ``verification_failures``.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
INVERSE_PATH = ROOT / ".scratch/period_two_inverse_q_companion_checker.py"
RAW_PATH = ROOT / ".scratch/period_two_residual_augmented_defect_raw_checker.py"
DIRECT_PATH = ROOT / ".scratch/period_two_seven_family_covariance_checker.py"
GENERATOR_PATH = ROOT / ".scratch/period_two_raw_stream_manifest_generator.py"
PROOF_PATH = ROOT / "literature/proofs/AK3_OLD_NEW_INVERSE_Q_CONNECTORS.md"
MANIFEST_PATH = ROOT / ".scratch/period_two_inverse_pure_increment_manifest.json"
Word = tuple[int, ...]


@dataclass(frozen=True)
class AffineENSchema:
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
    q_offset: int
    p_offset: int


@dataclass(frozen=True)
class ENCell:
    cell_id: str
    e_value: int | None
    n_value: int | None
    base_e: int
    base_n: int


@dataclass(frozen=True)
class ENPumpedTemplate:
    schema_id: str
    cell_id: str
    blocks: tuple[tuple[str, Word, tuple[int, int, int] | None], ...]
    base_word: Word
    insertion_splits: tuple[tuple[str, int], ...]
    pumping_witnesses: tuple[tuple[str, int, int, int], ...]
    terminal_c: bool
    length_affine_en: tuple[int, int, int]


CELLS = tuple(
    ENCell(
        f"e{e_id}_n{n_id}",
        e_value,
        n_value,
        2 if e_value is None else e_value,
        3 if n_value is None else n_value,
    )
    for e_id, e_value in (("0", 0), ("1", 1), ("ge2", None))
    for n_id, n_value in (("0", 0), ("1", 1), ("2", 2), ("ge3", None))
)

OCCURRENCES_BY_SLOT = {2: (1, 6), 3: (9, 14), 4: (15, 16)}
SLOT_ZERO_OCCURRENCES = (3, 4, 7, 8, 11, 12)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def canonical_line(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def cell_contains(cell: ENCell, e: int, n: int) -> bool:
    return (
        e >= 0
        and n >= 0
        and (e == cell.e_value if cell.e_value is not None else e >= cell.base_e)
        and (n == cell.n_value if cell.n_value is not None else n >= cell.base_n)
    )


def matching_cells(e: int, n: int) -> tuple[ENCell, ...]:
    return tuple(cell for cell in CELLS if cell_contains(cell, e, n))


def raw_parser_guard(generator: Any) -> dict[str, str]:
    raw_p = generator.parse_raw("tc")
    return {
        "raw_p": generator.lit(raw_p),
        "raw_p_inverse": generator.lit(generator.lift.quotient_inverse(raw_p)),
        "module_parser_p": generator.lit(generator.lift.parse_quotient("tc")),
    }


def affine_en_schema(
    inverse: Any,
    generator: Any,
    schema_id: str,
    left: Word,
    q_word: Word,
    middle: Word,
    p_word: Word,
    right: Word,
    q_offset: int,
    p_offset: int,
    q_reference: Word,
    p_reference: Word,
) -> AffineENSchema:
    q_left, q_core, q_multiplier, q_right = inverse.reference_primitive_decomposition(
        generator, q_word, q_reference
    )
    p_left, p_core, p_multiplier, p_right = inverse.reference_primitive_decomposition(
        generator, p_word, p_reference
    )
    return AffineENSchema(
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
        q_offset=q_offset,
        p_offset=p_offset,
    )


def tagged_quotient_word_en(
    generator: Any,
    schema: AffineENSchema,
    e: int,
    n: int,
) -> list[tuple[int, tuple[Any, ...]]]:
    q_exponent = schema.q_multiplier * (e + schema.q_offset)
    p_exponent = schema.p_multiplier * (n + schema.p_offset)
    if e < 0 or n < 0 or q_exponent < 0 or p_exponent < 0:
        raise ValueError((schema.schema_id, e, n, q_exponent, p_exponent))
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
        letter = generator.lift.C if abs(raw_letter) == generator.lift.C else raw_letter
        inverse_letter = (
            generator.lift.C
            if abs(letter) == generator.lift.C
            else -letter
        )
        if reduced and reduced[-1][0] == inverse_letter:
            reduced.pop()
        else:
            reduced.append((letter, tag))
    return reduced


def tagged_c_vertex_en(
    generator: Any,
    schema: AffineENSchema,
    e: int,
    n: int,
) -> list[tuple[int, tuple[Any, ...]]]:
    reduced = tagged_quotient_word_en(generator, schema, e, n)
    if reduced and abs(reduced[-1][0]) == generator.lift.C:
        return reduced[:-1]
    return reduced


def direct_schema_vertex(
    generator: Any,
    schema: AffineENSchema,
    e: int,
    n: int,
) -> Word:
    q_power = generator.quotient_power(schema.source_q, e + schema.q_offset)
    p_power = generator.quotient_power(schema.source_p, n + schema.p_offset)
    return generator.lift.c_vertex(
        generator.lift.quotient_reduce(
            (
                *schema.source_left,
                *q_power,
                *schema.source_middle,
                *p_power,
                *schema.source_right,
            )
        )
    )


def build_template_en(
    inverse: Any,
    generator: Any,
    schema: AffineENSchema,
    cell: ENCell,
) -> ENPumpedTemplate:
    tagged = tagged_c_vertex_en(generator, schema, cell.base_e, cell.base_n)
    base_word = tuple(letter for letter, _ in tagged)
    insertions: list[tuple[str, int, Word, tuple[int, int, int], int, int]] = []
    if cell.e_value is None:
        boundary = inverse.intact_boundary(tagged, "q", len(schema.q_core))
        if boundary is None:
            raise AssertionError((schema.schema_id, cell.cell_id, "missing_q_boundary"))
        insertions.append(
            (
                "q",
                boundary["split"],
                schema.q_core,
                (
                    schema.q_multiplier,
                    0,
                    0,
                ),
                boundary["left_copy"],
                boundary["right_copy"],
            )
        )
    if cell.n_value is None:
        boundary = inverse.intact_boundary(tagged, "p", len(schema.p_core))
        if boundary is None:
            raise AssertionError((schema.schema_id, cell.cell_id, "missing_p_boundary"))
        insertions.append(
            (
                "p",
                boundary["split"],
                schema.p_core,
                (
                    0,
                    schema.p_multiplier,
                    0,
                ),
                boundary["left_copy"],
                boundary["right_copy"],
            )
        )
    insertions.sort(key=lambda item: item[1])
    if len({item[1] for item in insertions}) != len(insertions):
        raise AssertionError((schema.schema_id, cell.cell_id, "coincident_insertions"))
    blocks: list[tuple[str, Word, tuple[int, int, int] | None]] = []
    cursor = 0
    for name, split, core, affine, _, _ in insertions:
        if base_word[cursor:split]:
            blocks.append(("fixed", base_word[cursor:split], None))
        constant = -affine[0] * cell.base_e - affine[1] * cell.base_n
        blocks.append((name, core, (affine[0], affine[1], constant)))
        cursor = split
    if base_word[cursor:]:
        blocks.append(("fixed", base_word[cursor:], None))
    e_coefficient = sum(
        len(word) * affine[0]
        for kind, word, affine in blocks
        if kind != "fixed" and affine is not None
    )
    n_coefficient = sum(
        len(word) * affine[1]
        for kind, word, affine in blocks
        if kind != "fixed" and affine is not None
    )
    constant = len(base_word) - e_coefficient * cell.base_e - n_coefficient * cell.base_n
    full = tagged_quotient_word_en(generator, schema, cell.base_e, cell.base_n)
    return ENPumpedTemplate(
        schema_id=schema.schema_id,
        cell_id=cell.cell_id,
        blocks=tuple(blocks) if blocks else (("fixed", (), None),),
        base_word=base_word,
        insertion_splits=tuple((name, split) for name, split, _, _, _, _ in insertions),
        pumping_witnesses=tuple(
            (name, split, left_copy, right_copy)
            for name, split, _, _, left_copy, right_copy in insertions
        ),
        terminal_c=bool(full and abs(full[-1][0]) == generator.lift.C),
        length_affine_en=(e_coefficient, n_coefficient, constant),
    )


def expand_template_en(template: ENPumpedTemplate, e: int, n: int) -> Word:
    output: list[int] = []
    for kind, word, affine in template.blocks:
        if kind == "fixed":
            output.extend(word)
            continue
        if affine is None:
            raise AssertionError((template.schema_id, template.cell_id, kind))
        copies = affine[0] * e + affine[1] * n + affine[2]
        if copies < 0:
            raise AssertionError((template.schema_id, template.cell_id, kind, copies))
        output.extend(word * copies)
    return tuple(output)


def canonical_blocks(inverse: Any, template: ENPumpedTemplate) -> tuple[Any, ...]:
    return inverse.normalize_blocks(template.blocks)


def fixed_mismatch_witness_en(
    inverse: Any,
    template: ENPumpedTemplate,
    e: int,
    n: int,
    position: int,
) -> tuple[tuple[Any, ...], tuple[int, int, int], int] | None:
    try:
        return inverse.fixed_mismatch_witness(template, e, n, position)
    except AssertionError:
        return None


def compare_templates_en(
    inverse: Any,
    generator: Any,
    left: ENPumpedTemplate,
    right: ENPumpedTemplate,
) -> dict[str, Any]:
    if left.cell_id != right.cell_id:
        return {"order": None, "method": "fail_closed_cell_mismatch"}
    left_e, left_n, left_constant = left.length_affine_en
    right_e, right_n, right_constant = right.length_affine_en
    length_record = {
        "left_affine_en": [left_e, left_n, left_constant],
        "right_affine_en": [right_e, right_n, right_constant],
    }
    if (left_e, left_n) != (right_e, right_n):
        return {
            "order": None,
            "method": "fail_closed_unequal_affine_slopes",
            "length": length_record,
        }
    difference = left_constant - right_constant
    if difference:
        return {
            "order": -1 if difference < 0 else 1,
            "method": "affine_length",
            "length": {**length_record, "difference": difference},
        }
    mismatch = inverse.first_mismatch(left.base_word, right.base_word)
    if mismatch is None:
        if canonical_blocks(inverse, left) != canonical_blocks(inverse, right):
            return {
                "order": None,
                "method": "fail_closed_equal_base_noncanonical",
                "length": length_record,
            }
        return {
            "order": 0,
            "method": "canonical_pumped_word_equality",
            "length": {**length_record, "difference": 0},
        }
    position, left_letter, right_letter = mismatch
    cell = next(item for item in CELLS if item.cell_id == left.cell_id)
    left_witness = fixed_mismatch_witness_en(
        inverse, left, cell.base_e, cell.base_n, position
    )
    right_witness = fixed_mismatch_witness_en(
        inverse, right, cell.base_e, cell.base_n, position
    )
    if left_witness is None or right_witness is None:
        return {
            "order": None,
            "method": "fail_closed_unwitnessed_pumped_mismatch",
            "length": length_record,
            "base_position": position,
        }
    left_prefix, left_position, witnessed_left = left_witness
    right_prefix, right_position, witnessed_right = right_witness
    if (
        left_prefix != right_prefix
        or left_position != right_position
        or (witnessed_left, witnessed_right) != (left_letter, right_letter)
    ):
        return {
            "order": None,
            "method": "fail_closed_nonuniform_first_mismatch",
            "length": length_record,
            "base_position": position,
        }
    return {
        "order": -1 if left_letter < right_letter else 1,
        "method": (
            "fixed_prefix_first_mismatch"
            if left_position[:2] == (0, 0)
            else "affine_pumped_first_mismatch"
        ),
        "length": {**length_record, "difference": 0},
        "first_mismatch": {
            "position_affine_en": list(left_position),
            "left_letter": generator.lit((left_letter,)),
            "right_letter": generator.lit((right_letter,)),
        },
    }


def parse_factor_word(generator: Any, factor: dict[str, Any]) -> Word:
    return generator.parse_raw(factor["word"])


def inverse_provenance_rows(generator: Any) -> list[dict[str, Any]]:
    _, source_rows = generator.build_w_rows()
    rows = [
        row
        for row in source_rows
        if row["family"] == "W"
        and row["key"]["block"] == "Q"
        and row["key"]["orientation"] == -1
    ]
    rows.sort(key=lambda row: (row["key"]["nu"], row["key"]["position"]))
    return rows


def build_schemas(
    inverse: Any,
    generator: Any,
    provenance: list[dict[str, Any]],
    actions: dict[int, Word],
) -> tuple[dict[str, AffineENSchema], list[dict[str, Any]], list[str]]:
    failures: list[str] = []
    if not provenance:
        return {}, [], ["no_inverse_provenance"]
    first_factors = provenance[0]["module_vertex"]["factors"]
    q_word = parse_factor_word(generator, first_factors[2])
    p_word = parse_factor_word(generator, first_factors[4])
    _, q_reference, _, _ = inverse.reference_primitive_decomposition(
        generator, q_word, inverse.primitive_power(q_word)[0]
    )
    _, p_reference, _, _ = inverse.reference_primitive_decomposition(
        generator, p_word, inverse.primitive_power(p_word)[0]
    )
    schemas: dict[str, AffineENSchema] = {}
    rows: list[dict[str, Any]] = []
    expected_exponents = (
        {"op": "const", "value": 1},
        {"op": "const", "value": 1},
        {"op": "var", "name": "h"},
        {"op": "const", "value": 1},
        {"op": "var", "name": "i"},
        {"op": "const", "value": 1},
    )
    for source in provenance:
        factors = source["module_vertex"]["factors"]
        source_id = source["id"]
        if len(factors) != 6 or tuple(item["exponent"] for item in factors) != expected_exponents:
            failures.append(f"source_factor_shape:{source_id}")
            continue
        words = tuple(parse_factor_word(generator, item) for item in factors)
        module_id = f"inverse:path:{source_id}:module"
        module_schema = affine_en_schema(
            inverse,
            generator,
            module_id,
            (*words[0], *words[1]),
            words[2],
            words[3],
            words[4],
            words[5],
            0,
            0,
            q_reference,
            p_reference,
        )
        schemas[module_id] = module_schema
        action_ids: dict[str, str] = {}
        slot = source["key"]["slot"]
        for occurrence in OCCURRENCES_BY_SLOT[slot]:
            action_id = f"inverse:path:{source_id}:label:o{occurrence}"
            schemas[action_id] = affine_en_schema(
                inverse,
                generator,
                action_id,
                (*actions[occurrence], *module_schema.source_left),
                module_schema.source_q,
                module_schema.source_middle,
                module_schema.source_p,
                module_schema.source_right,
                0,
                0,
                q_reference,
                p_reference,
            )
            action_ids[str(occurrence)] = action_id
        rows.append(
            {
                "id": source_id,
                "nu": source["key"]["nu"],
                "position": source["key"]["position"],
                "traversal_position": source["traversal_position"],
                "stored_letter": source["stored_letter"],
                "actual_letter": source["actual_letter"],
                "slot": slot,
                "source_scale": source["source_scale"],
                "incidence_sign": source["incidence_sign"],
                "integral_coefficient": source["coefficient"],
                "module_schema": module_id,
                "label_schemas": action_ids,
                "source_binding": "build_w_rows:negative_Q:h=e:i=n",
            }
        )

    gamma = generator.eval_path(generator.BLOCKS[0][2])
    gamma_inverse = generator.lift.quotient_inverse(gamma)
    for delta in (0, 1):
        module_id = f"inverse:slot0:delta{delta}:module"
        schemas[module_id] = affine_en_schema(
            inverse,
            generator,
            module_id,
            generator.parse_raw("cT"),
            gamma_inverse,
            generator.parse_raw("c"),
            gamma_inverse,
            generator.parse_raw("t"),
            delta,
            1,
            q_reference,
            p_reference,
        )
        for occurrence in SLOT_ZERO_OCCURRENCES:
            action_id = f"inverse:slot0:delta{delta}:label:o{occurrence}"
            module = schemas[module_id]
            schemas[action_id] = affine_en_schema(
                inverse,
                generator,
                action_id,
                (*actions[occurrence], *module.source_left),
                module.source_q,
                module.source_middle,
                module.source_p,
                module.source_right,
                delta,
                1,
                q_reference,
                p_reference,
            )
    return schemas, rows, failures


def schema_record(generator: Any, schema: AffineENSchema) -> dict[str, Any]:
    return {
        "id": schema.schema_id,
        "source": {
            "left": generator.lit(schema.source_left),
            "q": generator.lit(schema.source_q),
            "q_exponent": [1, 0, schema.q_offset],
            "middle": generator.lit(schema.source_middle),
            "p": generator.lit(schema.source_p),
            "p_exponent": [0, 1, schema.p_offset],
            "right": generator.lit(schema.source_right),
        },
        "normal_form": {
            "fixed_0": generator.lit(schema.fixed_0),
            "q_core": generator.lit(schema.q_core),
            "q_multiplier": schema.q_multiplier,
            "fixed_1": generator.lit(schema.fixed_1),
            "p_core": generator.lit(schema.p_core),
            "p_multiplier": schema.p_multiplier,
            "fixed_2": generator.lit(schema.fixed_2),
        },
    }


def template_digest(generator: Any, templates: dict[tuple[str, str], ENPumpedTemplate]) -> str:
    digest = hashlib.sha256()
    for key, template in sorted(templates.items()):
        digest.update(
            canonical_line(
                {
                    "schema": key[0],
                    "cell": key[1],
                    "blocks": [
                        [kind, generator.lit(word), affine]
                        for kind, word, affine in template.blocks
                    ],
                    "base": generator.lit(template.base_word),
                    "length_affine_en": template.length_affine_en,
                    "pumping_witnesses": template.pumping_witnesses,
                }
            )
        )
    return digest.hexdigest()


def build_templates(
    inverse: Any,
    generator: Any,
    schemas: dict[str, AffineENSchema],
) -> tuple[dict[tuple[str, str], ENPumpedTemplate], list[str]]:
    templates: dict[tuple[str, str], ENPumpedTemplate] = {}
    failures: list[str] = []
    for schema_id, schema in sorted(schemas.items()):
        for cell in CELLS:
            try:
                template = build_template_en(inverse, generator, schema, cell)
                direct = direct_schema_vertex(generator, schema, cell.base_e, cell.base_n)
                if template.base_word != direct:
                    failures.append(f"base_normal_form:{schema_id}:{cell.cell_id}")
                if expand_template_en(template, cell.base_e, cell.base_n) != direct:
                    failures.append(f"base_expansion:{schema_id}:{cell.cell_id}")
                templates[(schema_id, cell.cell_id)] = template
            except Exception as exc:
                failures.append(f"template:{schema_id}:{cell.cell_id}:{type(exc).__name__}:{exc}")
    return templates, failures


def cell_fibers(
    inverse: Any,
    generator: Any,
    cell: ENCell,
    provenance: list[dict[str, Any]],
    templates: dict[tuple[str, str], ENPumpedTemplate],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str], dict[str, int]]:
    failures: list[str] = []
    methods: Counter[str] = Counter()
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for row in provenance:
        template = templates[(row["module_schema"], cell.cell_id)]
        key = (row["slot"], canonical_blocks(inverse, template))
        grouped.setdefault(key, []).append(row)
    equality_checks = 0
    for left_index, left in enumerate(provenance):
        for right in provenance[left_index + 1 :]:
            if left["slot"] != right["slot"]:
                continue
            comparison = compare_templates_en(
                inverse,
                generator,
                templates[(left["module_schema"], cell.cell_id)],
                templates[(right["module_schema"], cell.cell_id)],
            )
            equality_checks += 1
            methods[comparison["method"]] += 1
            same = canonical_blocks(
                inverse, templates[(left["module_schema"], cell.cell_id)]
            ) == canonical_blocks(
                inverse, templates[(right["module_schema"], cell.cell_id)]
            )
            if comparison["order"] is None:
                failures.append(f"collision_compare:{left['id']}:{right['id']}:{comparison['method']}")
            elif (comparison["order"] == 0) != same:
                failures.append(f"collision_equivalence:{left['id']}:{right['id']}")
    runtime: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    sorted_groups = sorted(
        grouped.values(), key=lambda members: (members[0]["slot"], sorted(item["id"] for item in members))
    )
    for index, members in enumerate(sorted_groups):
        members = sorted(members, key=lambda item: item["id"])
        representative = members[0]
        coefficient_sum = sum(item["integral_coefficient"] for item in members)
        action_schemas: dict[str, str] = {}
        for occurrence in OCCURRENCES_BY_SLOT[representative["slot"]]:
            representative_action = representative["label_schemas"][str(occurrence)]
            for member in members[1:]:
                member_action = member["label_schemas"][str(occurrence)]
                comparison = compare_templates_en(
                    inverse,
                    generator,
                    templates[(representative_action, cell.cell_id)],
                    templates[(member_action, cell.cell_id)],
                )
                if comparison["order"] != 0:
                    failures.append(
                        f"collision_label:{representative['id']}:{member['id']}:o{occurrence}:{comparison['method']}"
                    )
            action_schemas[str(occurrence)] = representative_action
        fiber_id = f"{cell.cell_id}:f{index:03d}"
        item = {
            "fiber_id": fiber_id,
            "slot": representative["slot"],
            "members": [member["id"] for member in members],
            "integral_coefficient_sum": coefficient_sum,
            "activity_parity": coefficient_sum % 2,
            "module_schema": representative["module_schema"],
            "label_schemas": action_schemas,
        }
        records.append(item)
        runtime.append(item)
    return runtime, records, failures, {
        "same_slot_pair_checks": equality_checks,
        **dict(sorted(methods.items())),
    }


def build_tokens(
    inverse: Any,
    cell: ENCell,
    fibers: list[dict[str, Any]],
    templates: dict[tuple[str, str], ENPumpedTemplate],
    occurrences: dict[int, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    tokens: list[dict[str, Any]] = []
    for delta in (0, 1):
        module_id = f"inverse:slot0:delta{delta}:module"
        coordinate_id = f"slot0:delta{delta}"
        for occurrence in SLOT_ZERO_OCCURRENCES:
            tokens.append(
                {
                    "id": f"{cell.cell_id}:{coordinate_id}:o{occurrence}",
                    "coordinate_id": coordinate_id,
                    "source": "slot0",
                    "occurrence": occurrence,
                    "polarity": occurrences[occurrence]["polarity"],
                    "module_schema": module_id,
                    "module_template": templates[(module_id, cell.cell_id)],
                    "label_schema": f"inverse:slot0:delta{delta}:label:o{occurrence}",
                    "label_template": templates[
                        (f"inverse:slot0:delta{delta}:label:o{occurrence}", cell.cell_id)
                    ],
                }
            )
    for fiber in fibers:
        if not fiber["activity_parity"]:
            continue
        for occurrence in OCCURRENCES_BY_SLOT[fiber["slot"]]:
            label_id = fiber["label_schemas"][str(occurrence)]
            tokens.append(
                {
                    "id": f"{fiber['fiber_id']}:o{occurrence}",
                    "coordinate_id": fiber["fiber_id"],
                    "source": "inverse_Q_path",
                    "occurrence": occurrence,
                    "polarity": occurrences[occurrence]["polarity"],
                    "module_schema": fiber["module_schema"],
                    "module_template": templates[(fiber["module_schema"], cell.cell_id)],
                    "label_schema": label_id,
                    "label_template": templates[(label_id, cell.cell_id)],
                }
            )
    tokens.sort(key=lambda item: item["id"])
    failures: list[str] = []
    coordinate_keys = [
        (token["occurrence"], canonical_blocks(inverse, token["module_template"]))
        for token in tokens
    ]
    if len(coordinate_keys) != len(set(coordinate_keys)):
        failures.append("duplicate_decorated_coordinate")
    records = [
        {
            "id": token["id"],
            "coordinate_id": token["coordinate_id"],
            "source": token["source"],
            "occurrence": token["occurrence"],
            "polarity": token["polarity"],
            "module_schema": token["module_schema"],
            "label_schema": token["label_schema"],
        }
        for token in tokens
    ]
    return tokens, records, failures


def observable_record(generator: Any, observable: tuple[Any, ...]) -> dict[str, Any]:
    first_labels, equalities, rho, central = observable
    return {
        "first_half_labels": [generator.lit(label) for label in first_labels],
        "equalities": list(equalities),
        "rho": rho,
        "central_label": generator.lit(central),
        "central_length": len(central),
        "max_first_half_length": max((len(label) for label in first_labels), default=-1),
    }


def raw_records(
    residual: Any,
    generator: Any,
    cell: ENCell,
    tokens: list[dict[str, Any]],
    schemas: dict[str, AffineENSchema],
    actions: dict[int, Word],
) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    failures: list[str] = []
    for token in tokens:
        if token["source"] == "slot0":
            continue
        schema = schemas[token["module_schema"]]
        template = token["module_template"]
        action = actions[token["occurrence"]]
        vertex = direct_schema_vertex(generator, schema, cell.base_e, cell.base_n)
        base = residual.raw_observable(generator, action, vertex)
        base_record = observable_record(generator, base)
        locality = {
            "all_first_half_noncentral": not any(base[1]),
            "central_strictly_longer": (
                not base[0] or len(base[3]) > max(len(label) for label in base[0])
            ),
            "action_horizon": len(action) + 1,
        }
        pumps = []
        for variable, is_free, coefficient_index in (
            ("e", cell.e_value is None, 0),
            ("n", cell.n_value is None, 1),
        ):
            if not is_free:
                continue
            candidates = [
                (kind, core, affine)
                for kind, core, affine in template.blocks
                if affine is not None and affine[coefficient_index] > 0
            ]
            if len(candidates) != 1:
                failures.append(f"raw_pump_block:{token['id']}:{variable}:{len(candidates)}")
                continue
            kind, core, affine = candidates[0]
            split = dict(template.insertion_splits).get(kind)
            if split is None:
                failures.append(f"raw_pump_split:{token['id']}:{variable}")
                continue
            next_e = cell.base_e + (1 if variable == "e" else 0)
            next_n = cell.base_n + (1 if variable == "n" else 0)
            next_vertex = direct_schema_vertex(generator, schema, next_e, next_n)
            next_observable = residual.raw_observable(generator, action, next_vertex)
            stable_signature = base[:3] == next_observable[:3]
            affine_increment = affine[coefficient_index]
            saturated_boundary = split + affine_increment * len(core)
            horizon_saturated = saturated_boundary > locality["action_horizon"]
            central_length_slope = len(next_observable[3]) - len(base[3])
            pump = {
                "variable": variable,
                "block": kind,
                "core": generator.lit(core),
                "core_length": len(core),
                "insertion_split": split,
                "affine_increment": affine_increment,
                "action_horizon": locality["action_horizon"],
                "saturated_boundary": saturated_boundary,
                "horizon_saturated": horizon_saturated,
                "base_next_raw_signature_equal": stable_signature,
                "central_length_slope": central_length_slope,
                "one_step": observable_record(generator, next_observable),
            }
            pumps.append(pump)
            if not horizon_saturated or not stable_signature or central_length_slope <= 0:
                failures.append(f"raw_pump:{token['id']}:{variable}")
        if pumps and (
            not locality["all_first_half_noncentral"]
            or not locality["central_strictly_longer"]
        ):
            failures.append(f"raw_locality:{token['id']}")
        records.append(
            {
                "id": f"raw:{token['id']}",
                "token_id": token["id"],
                "coordinate_id": token["coordinate_id"],
                "occurrence": token["occurrence"],
                "action": generator.lit(action),
                "module_schema": token["module_schema"],
                "base": base_record,
                "locality": locality,
                "pumps": pumps,
                "source_binding": "raw_observable + one-increment horizon-saturation lemma",
            }
        )
    return records, failures


def pair_record(
    inverse: Any,
    generator: Any,
    left: dict[str, Any],
    right: dict[str, Any],
) -> tuple[dict[str, Any], str | None]:
    label = compare_templates_en(
        inverse, generator, left["label_template"], right["label_template"]
    )
    failure = None
    if label["order"] is None:
        failure = f"label_compare:{left['id']}:{right['id']}:{label['method']}"
    module = None
    if left["occurrence"] != right["occurrence"]:
        chronological_order = -1 if left["occurrence"] < right["occurrence"] else 1
        bit = None if label["order"] is None else int(label["order"] == chronological_order)
        chronology = "literal_occurrence_order"
    else:
        module = compare_templates_en(
            inverse, generator, left["module_template"], right["module_template"]
        )
        if module["order"] in (None, 0):
            failure = (
                f"module_compare:{left['id']}:{right['id']}:{module['method']}"
            )
            bit = None
        elif label["order"] is None:
            bit = None
        else:
            bit = int(label["order"] == left["polarity"] * module["order"])
        chronology = (
            "same_occurrence_increasing"
            if left["polarity"] == 1
            else "same_occurrence_decreasing"
        )
    return (
        {
            "id": f"pair:{left['id']}|{right['id']}",
            "left": left["id"],
            "right": right["id"],
            "occurrences": [left["occurrence"], right["occurrence"]],
            "polarity": left["polarity"] if left["occurrence"] == right["occurrence"] else None,
            "chronology": chronology,
            "label_method": label["method"],
            "label_order": label["order"],
            "module_method": None if module is None else module["method"],
            "module_order": None if module is None else module["order"],
            "bit": bit,
        },
        failure,
    )


def pair_records(
    inverse: Any,
    generator: Any,
    tokens: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str], dict[str, Any]]:
    records: list[dict[str, Any]] = []
    failures: list[str] = []
    methods: Counter[str] = Counter()
    chronology: Counter[str] = Counter()
    digest = hashlib.sha256()
    for left_index, left in enumerate(tokens):
        for right in tokens[left_index + 1 :]:
            record, failure = pair_record(inverse, generator, left, right)
            records.append(record)
            digest.update(canonical_line(record))
            methods[record["label_method"]] += 1
            if record["module_method"] is not None:
                methods[f"module:{record['module_method']}"] += 1
            chronology[record["chronology"]] += 1
            if failure is not None:
                failures.append(failure)
    bits = [record["bit"] for record in records]
    return records, failures, {
        "pair_count": len(records),
        "one_count": None if any(bit is None for bit in bits) else sum(bits),
        "Q": None if any(bit is None for bit in bits) else sum(bits) % 2,
        "ordered_pair_digest_sha256": digest.hexdigest(),
        "comparison_method_counts": dict(sorted(methods.items())),
        "chronology_counts": dict(sorted(chronology.items())),
    }


def slot_zero_raw_value(cell: ENCell) -> int:
    return int(cell.e_value == 0)


def direct_base_replay(
    direct: Any,
    generator: Any,
    cell: ENCell,
    tokens: list[dict[str, Any]],
    token_records: list[dict[str, Any]],
    raw: list[dict[str, Any]],
    pairs: list[dict[str, Any]],
    computed: dict[str, Any],
    schemas: dict[str, AffineENSchema],
) -> dict[str, Any]:
    left = direct.anchored_direction(cell.base_n, cell.base_n + cell.base_e)
    right = direct.anchored_direction(cell.base_n, cell.base_n + cell.base_e + 1)
    increment = direct.add_directions(right, direct.negate(left))
    replay_tokens = direct.correction_tokens(
        increment, f"inverse_replay:{cell.cell_id}", compute_raw=True
    )
    replay_by_key = {
        (token.occurrence, token.module_vertex): token for token in replay_tokens
    }
    production_by_id = {record["id"]: record for record in token_records}
    production_key_by_id: dict[str, tuple[int, Word]] = {}
    coordinate_failures = []
    label_failures = []
    for token in tokens:
        schema = schemas[token["module_schema"]]
        module = direct_schema_vertex(generator, schema, cell.base_e, cell.base_n)
        label_schema = schemas[token["label_schema"]]
        label = direct_schema_vertex(generator, label_schema, cell.base_e, cell.base_n)
        key = (token["occurrence"], module)
        production_key_by_id[token["id"]] = key
        replay_token = replay_by_key.get(key)
        if replay_token is None:
            coordinate_failures.append(token["id"])
        elif replay_token.label != label or replay_token.polarity != token["polarity"]:
            label_failures.append(token["id"])
    extra_coordinates = sorted(
        f"o{occurrence}:{generator.lit(module or ())}"
        for occurrence, module in set(replay_by_key) - set(production_key_by_id.values())
    )
    raw_failures = []
    for record in raw:
        replay_token = replay_by_key.get(production_key_by_id[record["token_id"]])
        if replay_token is None or replay_token.raw_weight != record["base"]["rho"]:
            raw_failures.append(record["token_id"])
    slot_zero_replay = sum(
        token.raw_weight
        for token in replay_tokens
        if token.occurrence in SLOT_ZERO_OCCURRENCES
    ) % 2
    pair_failures = []
    for record in pairs:
        left_token = replay_by_key.get(production_key_by_id[record["left"]])
        right_token = replay_by_key.get(production_key_by_id[record["right"]])
        replay_bit = (
            None
            if left_token is None or right_token is None
            else direct.kernel(left_token, right_token)
        )
        if replay_bit != record["bit"]:
            pair_failures.append(record["id"])
    direct_l = direct.raw_linear(replay_tokens)
    direct_q = direct.quadratic(replay_tokens)
    totals_match = {
        "L": direct_l == computed["L"],
        "Q": direct_q == computed["Q"],
        "Phi": (direct_l ^ direct_q) == computed["Phi"],
    }
    return {
        "base_point": {"e": cell.base_e, "n": cell.base_n},
        "token_count": len(replay_tokens),
        "production_token_count": len(production_by_id),
        "coordinate_failures": coordinate_failures,
        "extra_coordinates": extra_coordinates,
        "label_failures": label_failures,
        "raw_failures": raw_failures,
        "slot_zero_raw": slot_zero_replay,
        "slot_zero_formula_matches": slot_zero_replay == computed["L_slot_zero"],
        "pair_failures": pair_failures,
        "direct": {"L": direct_l, "Q": direct_q, "Phi": direct_l ^ direct_q},
        "totals_match": totals_match,
    }


def build_cell_result(
    inverse: Any,
    residual: Any,
    direct: Any,
    generator: Any,
    cell: ENCell,
    provenance: list[dict[str, Any]],
    schemas: dict[str, AffineENSchema],
    templates: dict[tuple[str, str], ENPumpedTemplate],
    occurrences: dict[int, dict[str, Any]],
    actions: dict[int, Word],
) -> dict[str, Any]:
    fibers, fiber_records, collision_failures, collision_methods = cell_fibers(
        inverse, generator, cell, provenance, templates
    )
    tokens, token_records, token_failures = build_tokens(
        inverse, cell, fibers, templates, occurrences
    )
    raw, raw_failures = raw_records(
        residual, generator, cell, tokens, schemas, actions
    )
    pairs, pair_failures, q_record = pair_records(inverse, generator, tokens)
    raw_bits = [record["base"]["rho"] for record in raw]
    l_nonzero = sum(raw_bits) % 2
    l_slot_zero = slot_zero_raw_value(cell)
    q_value = q_record["Q"]
    computed = {
        "L_slot_zero": l_slot_zero,
        "L_nonzero": l_nonzero,
        "L": l_slot_zero ^ l_nonzero,
        "Q": q_value,
        "Phi": None if q_value is None else l_slot_zero ^ l_nonzero ^ q_value,
        "remaining_scalar": None if q_value is None else l_nonzero ^ q_value,
    }
    replay = direct_base_replay(
        direct,
        generator,
        cell,
        tokens,
        token_records,
        raw,
        pairs,
        computed,
        schemas,
    )
    failures = [
        *collision_failures,
        *token_failures,
        *raw_failures,
        *pair_failures,
    ]
    return {
        "cell": {
            "id": cell.cell_id,
            "e": "ge2" if cell.e_value is None else cell.e_value,
            "n": "ge3" if cell.n_value is None else cell.n_value,
            "base_e": cell.base_e,
            "base_n": cell.base_n,
        },
        "collision": {
            "fibers": fiber_records,
            "fiber_count": len(fiber_records),
            "active_fiber_count": sum(item["activity_parity"] for item in fiber_records),
            "active_slot_profile": {
                str(slot): sum(
                    item["activity_parity"]
                    for item in fiber_records
                    if item["slot"] == slot
                )
                for slot in (2, 3, 4)
            },
            "comparison_counts": collision_methods,
        },
        "coordinate_count": 2 + sum(item["activity_parity"] for item in fiber_records),
        "tokens": token_records,
        "raw_records": raw,
        "quadratic": {**q_record, "pairs": pairs},
        "computed": computed,
        "direct_base_semantic_replay": replay,
        "generation_failures": failures,
    }


def build_manifest() -> dict[str, Any]:
    inverse = load_module("inverse_pure_increment_normalizer", INVERSE_PATH)
    residual = load_module("inverse_pure_increment_raw", RAW_PATH)
    direct = load_module("inverse_pure_increment_direct", DIRECT_PATH)
    generator = inverse.load_raw_generator()
    occurrences = {item["order"]: item for item in generator.trace_ast()[1]}
    actions = {
        order: generator.parse_raw(item["quotient_prefix"])
        for order, item in occurrences.items()
    }
    source_rows = inverse_provenance_rows(generator)
    schemas, provenance, schema_failures = build_schemas(
        inverse, generator, source_rows, actions
    )
    templates, template_failures = build_templates(inverse, generator, schemas)
    cells = [
        build_cell_result(
            inverse,
            residual,
            direct,
            generator,
            cell,
            provenance,
            schemas,
            templates,
            occurrences,
            actions,
        )
        for cell in CELLS
    ]
    all_failures = [
        *schema_failures,
        *template_failures,
        *(failure for cell in cells for failure in cell["generation_failures"]),
    ]
    return {
        "format": "period-two-inverse-pure-increment-direct-q-v4",
        "scope": {
            "parameters": "e=j-i>=0, n=i>=0",
            "increment": "b^-_(n,e)=A^-_(n,e)+A^-_(n,e+1)",
            "computed_target": "Phi(b^-)=L(b^-)+Q(b^-)",
            "nonclaim": (
                "Generator does not assert Phi=1. Verification tests that value only; "
                "no diagonal, lift, AK3, stable-AC, or AC conclusion is made."
            ),
        },
        "source_bindings": {
            "negative_provenance": {
                "path": str(GENERATOR_PATH.relative_to(ROOT)),
                "function": "build_w_rows",
                "selection": "family=W, block=Q, orientation=-1, active increment layer h=e, i=n",
                "sha256": sha256_path(GENERATOR_PATH),
            },
            "normalizer": {
                "path": str(INVERSE_PATH.relative_to(ROOT)),
                "functions": [
                    "reference_primitive_decomposition",
                    "intact_boundary",
                    "normalize_blocks",
                    "fixed_mismatch_witness",
                ],
                "sha256": sha256_path(INVERSE_PATH),
            },
            "raw": {
                "path": str(RAW_PATH.relative_to(ROOT)),
                "function": "raw_observable",
                "sha256": sha256_path(RAW_PATH),
                "locality_lemma": (
                    "For A R^(k t) B, if one inserted affine increment moves the "
                    "right edge past the finite action horizon, the exact base and "
                    "next raw signatures agree, and the central length has positive "
                    "slope, then later insertions cannot alter the horizon prefix."
                ),
                "certificate_fields": [
                    "insertion_split",
                    "affine_increment",
                    "core_length",
                    "action_horizon",
                    "saturated_boundary",
                    "base_next_raw_signature_equal",
                    "central_length_slope",
                ],
            },
            "direct_replay": {
                "path": str(DIRECT_PATH.relative_to(ROOT)),
                "functions": ["anchored_direction", "correction_tokens", "kernel"],
                "sha256": sha256_path(DIRECT_PATH),
            },
            "theory": {
                "path": str(PROOF_PATH.relative_to(ROOT)),
                "sections": ["1.12", "7.3", "7.4", "7.5"],
                "sha256": sha256_path(PROOF_PATH),
            },
        },
        "raw_parser_guard": raw_parser_guard(generator),
        "cells": [
            {
                "id": cell.cell_id,
                "e": "ge2" if cell.e_value is None else cell.e_value,
                "n": "ge3" if cell.n_value is None else cell.n_value,
                "base_e": cell.base_e,
                "base_n": cell.base_n,
            }
            for cell in CELLS
        ],
        "provenance": provenance,
        "schemas": [schema_record(generator, schema) for schema in schemas.values()],
        "template_digest_sha256": template_digest(generator, templates),
        "cell_results": cells,
        "generation_failures": all_failures,
    }


def recompute_pair_bit(record: dict[str, Any]) -> int | None:
    if record["label_order"] is None:
        return None
    left_occurrence, right_occurrence = record["occurrences"]
    if left_occurrence != right_occurrence:
        chronology = -1 if left_occurrence < right_occurrence else 1
        return int(record["label_order"] == chronology)
    if record["module_order"] in (None, 0) or record["polarity"] not in (-1, 1):
        return None
    return int(record["label_order"] == record["polarity"] * record["module_order"])


def verification_failures(manifest: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    try:
        if manifest["raw_parser_guard"] != {
            "raw_p": "tc",
            "raw_p_inverse": "cT",
            "module_parser_p": "t",
        }:
            failures.append("raw_parser_guard")
        if manifest["generation_failures"]:
            failures.append("generation_failures")
        cell_ids = [cell["id"] for cell in manifest["cells"]]
        if cell_ids != [cell.cell_id for cell in CELLS]:
            failures.append("cell_catalog")
        if any(len(matching_cells(e, n)) != 1 for e in range(7) for n in range(7)):
            failures.append("cell_coverage")
        provenance = manifest["provenance"]
        provenance_by_id = {row["id"]: row for row in provenance}
        if len(provenance) != 92 or len(provenance_by_id) != 92:
            failures.append("provenance_count")
        for result in manifest["cell_results"]:
            cell_id = result["cell"]["id"]
            fibers = result["collision"]["fibers"]
            members = [member for fiber in fibers for member in fiber["members"]]
            if sorted(members) != sorted(provenance_by_id):
                failures.append(f"collision_partition:{cell_id}")
            for fiber in fibers:
                coefficient_sum = sum(
                    provenance_by_id[member]["integral_coefficient"]
                    for member in fiber["members"]
                )
                if coefficient_sum != fiber["integral_coefficient_sum"]:
                    failures.append(f"collision_coefficient:{cell_id}:{fiber['fiber_id']}")
                if coefficient_sum % 2 != fiber["activity_parity"]:
                    failures.append(f"collision_parity:{cell_id}:{fiber['fiber_id']}")
            if result["collision"]["active_fiber_count"] != 36:
                failures.append(f"active_fiber_count:{cell_id}")
            if result["collision"]["active_slot_profile"] != {"2": 8, "3": 14, "4": 14}:
                failures.append(f"active_slot_profile:{cell_id}")
            if result["coordinate_count"] != 38:
                failures.append(f"coordinate_count:{cell_id}")
            tokens = result["tokens"]
            token_ids = [token["id"] for token in tokens]
            token_by_id = {token["id"]: token for token in tokens}
            if len(tokens) != 84 or len(set(token_ids)) != 84:
                failures.append(f"token_count:{cell_id}")
            active_fiber_ids = {
                fiber["fiber_id"] for fiber in fibers if fiber["activity_parity"]
            }
            slot_zero_tokens = [token for token in tokens if token["source"] == "slot0"]
            path_tokens = [token for token in tokens if token["source"] == "inverse_Q_path"]
            if len(slot_zero_tokens) != 12 or len(path_tokens) != 72:
                failures.append(f"token_source_profile:{cell_id}")
            if {token["coordinate_id"] for token in path_tokens} != active_fiber_ids:
                failures.append(f"token_fiber_coverage:{cell_id}")
            raw = result["raw_records"]
            if len(raw) != 72 or len({record["token_id"] for record in raw}) != 72:
                failures.append(f"raw_count:{cell_id}")
            for record in raw:
                token = token_by_id.get(record["token_id"])
                if (
                    token is None
                    or token["source"] != "inverse_Q_path"
                    or token["occurrence"] != record["occurrence"]
                    or token["coordinate_id"] != record["coordinate_id"]
                ):
                    failures.append(f"raw_token_binding:{cell_id}:{record['id']}")
                expected_rho = sum(not value for value in record["base"]["equalities"]) % 2
                if expected_rho != record["base"]["rho"]:
                    failures.append(f"raw_recompute:{cell_id}:{record['id']}")
                if record["pumps"] and not record["locality"]["all_first_half_noncentral"]:
                    failures.append(f"raw_noncentral:{cell_id}:{record['id']}")
                if record["pumps"] and not record["locality"]["central_strictly_longer"]:
                    failures.append(f"raw_length:{cell_id}:{record['id']}")
                for pump in record["pumps"]:
                    expected_boundary = (
                        pump["insertion_split"]
                        + pump["affine_increment"] * pump["core_length"]
                    )
                    expected_saturation = expected_boundary > pump["action_horizon"]
                    expected_signature_equal = all(
                        record["base"][field] == pump["one_step"][field]
                        for field in ("first_half_labels", "equalities", "rho")
                    )
                    expected_central_slope = (
                        pump["one_step"]["central_length"]
                        - record["base"]["central_length"]
                    )
                    if (
                        pump["core_length"] != len(pump["core"])
                        or pump["affine_increment"] != 3
                        or pump["action_horizon"] != record["locality"]["action_horizon"]
                        or pump["saturated_boundary"] != expected_boundary
                        or pump["horizon_saturated"] != expected_saturation
                        or not expected_saturation
                        or pump["base_next_raw_signature_equal"] != expected_signature_equal
                        or not expected_signature_equal
                        or pump["central_length_slope"] != expected_central_slope
                        or expected_central_slope <= 0
                    ):
                        failures.append(f"raw_pump:{cell_id}:{record['id']}:{pump['variable']}")
            pairs = result["quadratic"]["pairs"]
            expected_pair_ids = {
                f"pair:{left}|{right}"
                for index, left in enumerate(token_ids)
                for right in token_ids[index + 1 :]
            }
            if len(pairs) != 3486 or {pair["id"] for pair in pairs} != expected_pair_ids:
                failures.append(f"pair_completeness:{cell_id}")
            pair_bits = []
            for pair in pairs:
                left_token = token_by_id.get(pair["left"])
                right_token = token_by_id.get(pair["right"])
                if (
                    left_token is None
                    or right_token is None
                    or pair["occurrences"]
                    != [left_token["occurrence"], right_token["occurrence"]]
                    or (
                        left_token["occurrence"] == right_token["occurrence"]
                        and pair["polarity"] != left_token["polarity"]
                    )
                ):
                    failures.append(f"pair_token_binding:{cell_id}:{pair['id']}")
                bit = recompute_pair_bit(pair)
                pair_bits.append(bit)
                if bit != pair["bit"]:
                    failures.append(f"pair_recompute:{cell_id}:{pair['id']}")
            q_value = None if any(bit is None for bit in pair_bits) else sum(pair_bits) % 2
            if q_value != result["computed"]["Q"] or q_value != result["quadratic"]["Q"]:
                failures.append(f"Q_recompute:{cell_id}")
            l_nonzero = sum(record["base"]["rho"] for record in raw) % 2
            l_slot_zero = int(result["cell"]["e"] == 0)
            l_value = l_nonzero ^ l_slot_zero
            phi = None if q_value is None else l_value ^ q_value
            computed = result["computed"]
            if (
                computed["L_nonzero"] != l_nonzero
                or computed["L_slot_zero"] != l_slot_zero
                or computed["L"] != l_value
                or computed["Phi"] != phi
            ):
                failures.append(f"totals_recompute:{cell_id}")
            if phi != 1:
                failures.append(f"target_phi:{cell_id}:{phi}")
            expected_remaining = int(result["cell"]["e"] != 0)
            if computed["remaining_scalar"] != expected_remaining:
                failures.append(f"remaining_scalar:{cell_id}")
            replay = result["direct_base_semantic_replay"]
            if (
                replay["token_count"] != 84
                or replay["production_token_count"] != 84
                or replay["coordinate_failures"]
                or replay["extra_coordinates"]
                or replay["label_failures"]
                or replay["raw_failures"]
                or replay["pair_failures"]
                or not replay["slot_zero_formula_matches"]
                or not all(replay["totals_match"].values())
            ):
                failures.append(f"direct_replay:{cell_id}")
    except Exception as exc:
        failures.append(f"manifest_shape:{type(exc).__name__}:{exc}")
    return failures


def verify_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    failures = verification_failures(manifest)
    if failures:
        raise AssertionError(failures[:20])
    return manifest


def write_manifest() -> dict[str, Any]:
    manifest = verify_manifest(build_manifest())
    MANIFEST_PATH.write_bytes(canonical_json(manifest))
    return manifest


def check_manifest() -> dict[str, Any]:
    manifest = verify_manifest(build_manifest())
    expected = canonical_json(manifest)
    if MANIFEST_PATH.read_bytes() != expected:
        raise AssertionError("manifest differs; regenerate with --write")
    return manifest


def argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    return parser


def summary(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "format": manifest["format"],
        "generation_failures": len(manifest["generation_failures"]),
        "cells": [
            {
                "id": result["cell"]["id"],
                **result["computed"],
                "cell_failures": len(result["generation_failures"]),
            }
            for result in manifest["cell_results"]
        ],
    }


def main() -> None:
    args = argument_parser().parse_args()
    if args.write:
        manifest = write_manifest()
    elif args.check:
        manifest = check_manifest()
    else:
        manifest = build_manifest()
    print(json.dumps(summary(manifest), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
