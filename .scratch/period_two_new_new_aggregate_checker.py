"""Deterministic all-power certificate for the complete new-new curvature."""

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
INVERSE_CHECKER_PATH = ROOT / ".scratch/period_two_inverse_q_companion_checker.py"
MANIFEST_PATH = ROOT / ".scratch/period_two_new_new_aggregate_manifest.json"


@dataclass(frozen=True)
class Cell:
    cell_id: str
    a_value: int | None
    n_value: int | None
    base_a: int
    base_n: int


CELLS = tuple(
    Cell(
        f"a{a_id}_n{n_id}",
        a_value,
        n_value,
        3 if a_value is None else a_value,
        3 if n_value is None else n_value,
    )
    for a_id, a_value in (("0", 0), ("1", 1), ("2", 2), ("ge3", None))
    for n_id, n_value in (("0", 0), ("1", 1), ("2", 2), ("ge3", None))
)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def g_zero_schemas(inverse: Any, generator: Any) -> dict[str, Any]:
    occurrences = {item["order"]: item for item in generator.trace_ast()[1]}
    actions = {
        order: generator.parse_raw(item["quotient_prefix"])
        for order, item in occurrences.items()
    }
    gamma = generator.eval_path(generator.BLOCKS[0][2])
    gamma_inverse = generator.lift.quotient_inverse(gamma)
    gamma_primitive, gamma_multiplier = inverse.primitive_power(gamma)
    common_p = generator.eval_path(generator.BLOCKS[0][0])
    common_p_primitive, common_p_multiplier = inverse.primitive_power(common_p)
    _, inverse_multiplier = inverse.primitive_power(gamma_inverse)
    assert gamma_multiplier == common_p_multiplier == inverse_multiplier == 3
    p_inverse = generator.lift.quotient_inverse(generator.parse_raw("tc"))
    corner_parameters = {
        "00": (1, 2),
        "01": (0, 2),
        "11": (1, 3),
        "12": (0, 3),
    }
    schemas = {}
    for corner, (q_offset, p_offset) in corner_parameters.items():
        for occurrence in (None, 3, 4, 7, 8, 11, 12):
            prefix = () if occurrence is None else actions[occurrence]
            kind = "module" if occurrence is None else f"action:o{occurrence}"
            schema_id = f"g0:{corner}:{kind}"
            schemas[schema_id] = inverse.powered_schema(
                generator,
                schema_id,
                (*prefix, *p_inverse, *generator.quotient_power(gamma, q_offset)),
                gamma,
                generator.parse_raw("c"),
                gamma_inverse,
                generator.parse_raw("t"),
                p_offset,
                gamma_primitive,
                common_p_primitive,
            )
    assert len(schemas) == 28
    return schemas


def build_template(inverse: Any, generator: Any, schema: Any, cell: Cell) -> Any:
    tagged = inverse.tagged_c_vertex(generator, schema, cell.base_a, cell.base_n)
    base_word = tuple(letter for letter, _ in tagged)
    insertions = []
    if cell.a_value is None:
        boundary = inverse.intact_boundary(tagged, "q", len(schema.q_core))
        assert boundary is not None, (schema.schema_id, cell.cell_id, "q")
        insertions.append(
            (
                "q",
                boundary["split"],
                schema.q_core,
                (schema.q_multiplier, 0, -cell.base_a * schema.q_multiplier),
                boundary["left_copy"],
                boundary["right_copy"],
            )
        )
    if cell.a_value is None or cell.n_value is None:
        boundary = inverse.intact_boundary(tagged, "p", len(schema.p_core))
        assert boundary is not None, (schema.schema_id, cell.cell_id, "p")
        exponent = (
            schema.p_multiplier if cell.a_value is None else 0,
            schema.p_multiplier if cell.n_value is None else 0,
            -schema.p_multiplier
            * (cell.base_a if cell.a_value is None else 0)
            - schema.p_multiplier
            * (cell.base_n if cell.n_value is None else 0),
        )
        insertions.append(
            (
                "p",
                boundary["split"],
                schema.p_core,
                exponent,
                boundary["left_copy"],
                boundary["right_copy"],
            )
        )
    insertions.sort(key=lambda item: item[1])
    assert len({item[1] for item in insertions}) == len(insertions)
    blocks = []
    cursor = 0
    for name, split, core, exponent, _, _ in insertions:
        blocks.append(("fixed", base_word[cursor:split], None))
        blocks.append((name, core, exponent))
        cursor = split
    blocks.append(("fixed", base_word[cursor:], None))
    blocks = [block for block in blocks if block[0] != "fixed" or block[1]]
    a_coefficient = sum(
        len(word) * exponent[0]
        for kind, word, exponent in blocks
        if kind != "fixed" and exponent is not None
    )
    n_coefficient = sum(
        len(word) * exponent[1]
        for kind, word, exponent in blocks
        if kind != "fixed" and exponent is not None
    )
    constant = (
        len(base_word)
        - a_coefficient * cell.base_a
        - n_coefficient * cell.base_n
    )
    full = inverse.tagged_quotient_word(
        generator, schema, cell.base_a, cell.base_n
    )
    terminal_c = bool(full and abs(full[-1][0]) == generator.lift.C)
    return inverse.PumpedTemplate(
        schema_id=schema.schema_id,
        cell_id=cell.cell_id,
        blocks=tuple(blocks),
        base_word=base_word,
        insertion_splits=tuple(
            (name, split) for name, split, _, _, _, _ in insertions
        ),
        pumping_witnesses=tuple(
            (name, split, left_copy, right_copy)
            for name, split, _, _, left_copy, right_copy in insertions
        ),
        terminal_c=terminal_c,
        length_affine_an=(a_coefficient, n_coefficient, constant),
    )


def build_templates(
    inverse: Any,
    generator: Any,
    schemas: dict[str, Any],
) -> dict[tuple[str, str], Any]:
    templates = {
        (schema_id, cell.cell_id): build_template(inverse, generator, schema, cell)
        for schema_id, schema in schemas.items()
        for cell in CELLS
    }
    assert len(templates) == len(schemas) * len(CELLS)
    for (schema_id, cell_id), template in templates.items():
        schema = schemas[schema_id]
        cell = next(item for item in CELLS if item.cell_id == cell_id)
        direct = tuple(
            letter
            for letter, _ in inverse.tagged_c_vertex(
                generator, schema, cell.base_a, cell.base_n
            )
        )
        assert direct == template.base_word
        assert inverse.expand_template(template, cell.base_a, cell.base_n) == direct
    return templates


def compare_templates(
    inverse: Any,
    generator: Any,
    left: Any,
    right: Any,
) -> dict[str, Any]:
    assert left.cell_id == right.cell_id
    cell = next(item for item in CELLS if item.cell_id == left.cell_id)
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
    if difference:
        return {"order": -1 if difference < 0 else 1, "method": "affine_length"}
    mismatch = inverse.first_mismatch(left.base_word, right.base_word)
    if mismatch is None:
        assert inverse.canonical_blocks(left) == inverse.canonical_blocks(right), (
            left.schema_id,
            right.schema_id,
            left.cell_id,
        )
        return {"order": 0, "method": "canonical_pumped_word_equality"}
    position, left_letter, right_letter = mismatch
    left_prefix, left_position, witnessed_left = inverse.fixed_mismatch_witness(
        left, cell.base_a, cell.base_n, position
    )
    right_prefix, right_position, witnessed_right = inverse.fixed_mismatch_witness(
        right, cell.base_a, cell.base_n, position
    )
    assert left_prefix == right_prefix, (
        left.schema_id,
        right.schema_id,
        left.cell_id,
        position,
    )
    assert left_position == right_position
    assert (witnessed_left, witnessed_right) == (left_letter, right_letter)
    method = (
        "fixed_prefix_first_mismatch"
        if left_position[:2] == (0, 0)
        else "affine_pumped_first_mismatch"
    )
    return {
        "order": -1 if left_letter < right_letter else 1,
        "method": method,
        "first_mismatch_position_affine_an": list(left_position),
    }


def provenance_rows(metadata: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for row_key, row in sorted(
        metadata.items(), key=lambda item: (item[1]["nu"], item[1]["k"])
    ):
        for delta in (0, 1):
            rows.append(
                {
                    "id": f"{row_key}:delta{delta}",
                    "row_key": row_key,
                    "delta": delta,
                    "slot": row["slot"],
                    "coefficient": row["source_sign"]
                    * row["incidence"]
                    * (1 if delta == 0 else -1),
                    "module_schema": f"partner:module:{row_key}:delta{delta}",
                }
            )
    assert len(rows) == 184
    return rows


def cell_fibers(
    inverse: Any,
    generator: Any,
    templates: dict[tuple[str, str], Any],
    metadata: dict[str, dict[str, Any]],
    cell: Any,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    rows = provenance_rows(metadata)
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    equality_methods: Counter[str] = Counter()
    equality_checks = 0
    for left_index, left in enumerate(rows):
        left_template = templates[(left["module_schema"], cell.cell_id)]
        key = (left["slot"], inverse.canonical_blocks(left_template))
        grouped.setdefault(key, []).append(left)
        for right in rows[left_index + 1 :]:
            if left["slot"] != right["slot"]:
                continue
            comparison = compare_templates(
                inverse,
                generator,
                left_template,
                templates[(right["module_schema"], cell.cell_id)],
            )
            equality_checks += 1
            equality_methods[comparison["method"]] += 1
            same_key = key == (
                right["slot"],
                inverse.canonical_blocks(
                    templates[(right["module_schema"], cell.cell_id)]
                ),
            )
            assert (comparison["order"] == 0) == same_key
    assert equality_checks == 5684

    occurrences_by_slot = {2: (1, 6), 3: (9, 14), 4: (15, 16)}
    fibers = []
    for members in grouped.values():
        members = sorted(members, key=lambda item: item["id"])
        representative = members[0]
        coefficient_sum = sum(item["coefficient"] for item in members)
        action_schemas = {}
        for occurrence in occurrences_by_slot[representative["slot"]]:
            representative_action = (
                f"partner:action:{representative['row_key']}:"
                f"delta{representative['delta']}:o{occurrence}"
            )
            for member in members[1:]:
                member_action = (
                    f"partner:action:{member['row_key']}:"
                    f"delta{member['delta']}:o{occurrence}"
                )
                comparison = compare_templates(
                    inverse,
                    generator,
                    templates[(representative_action, cell.cell_id)],
                    templates[(member_action, cell.cell_id)],
                )
                assert comparison["order"] == 0
            action_schemas[str(occurrence)] = representative_action
        fibers.append(
            {
                "slot": representative["slot"],
                "members": [item["id"] for item in members],
                "integral_coefficient_sum": coefficient_sum,
                "activity_parity": coefficient_sum % 2,
                "module_schema": representative["module_schema"],
                "action_schemas": action_schemas,
            }
        )
    fibers.sort(key=lambda item: (item["slot"], item["members"]))
    assert len(fibers) == 106
    assert sum(item["activity_parity"] for item in fibers) == 72
    methods = dict(sorted(equality_methods.items()))
    return fibers, methods


def token_rows(
    cell: Any,
    g_zero_templates: dict[tuple[str, str], Any],
    g_q_templates: dict[tuple[str, str], Any],
    fibers: list[dict[str, Any]],
    occurrences: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    tokens = []
    for corner in ("00", "01", "11", "12"):
        module_schema = f"g0:{corner}:module"
        for occurrence in (3, 4, 7, 8, 11, 12):
            tokens.append(
                {
                    "id": f"g0:{corner}:o{occurrence}",
                    "source": "g0",
                    "occurrence": occurrence,
                    "polarity": occurrences[occurrence]["polarity"],
                    "module_schema": module_schema,
                    "module_template": g_zero_templates[
                        (module_schema, cell.cell_id)
                    ],
                    "label_schema": f"g0:{corner}:action:o{occurrence}",
                    "label_template": g_zero_templates[
                        (f"g0:{corner}:action:o{occurrence}", cell.cell_id)
                    ],
                }
            )
    for fiber_index, fiber in enumerate(fibers):
        if not fiber["activity_parity"]:
            continue
        for occurrence, action_schema in sorted(
            fiber["action_schemas"].items(), key=lambda item: int(item[0])
        ):
            occurrence_number = int(occurrence)
            token_id = f"gq:f{fiber_index:03d}:o{occurrence_number}"
            tokens.append(
                {
                    "id": token_id,
                    "source": "gQ",
                    "occurrence": occurrence_number,
                    "polarity": occurrences[occurrence_number]["polarity"],
                    "module_schema": fiber["module_schema"],
                    "module_template": g_q_templates[
                        (fiber["module_schema"], cell.cell_id)
                    ],
                    "label_schema": action_schema,
                    "label_template": g_q_templates[
                        (action_schema, cell.cell_id)
                    ],
                }
            )
    tokens.sort(key=lambda item: item["id"])
    assert len(tokens) == 24 + 2 * 72 == 168
    assert len({item["id"] for item in tokens}) == 168
    return tokens


def pair_record(
    inverse: Any,
    generator: Any,
    left: dict[str, Any],
    right: dict[str, Any],
) -> dict[str, Any]:
    label_comparison = compare_templates(
        inverse, generator, left["label_template"], right["label_template"]
    )
    if left["occurrence"] != right["occurrence"]:
        earlier_is_left = left["occurrence"] < right["occurrence"]
        chronological_order = -1 if earlier_is_left else 1
        bit = int(label_comparison["order"] == chronological_order)
        module_comparison = None
        chronology = "literal_occurrence_order"
    else:
        module_comparison = compare_templates(
            inverse, generator, left["module_template"], right["module_template"]
        )
        assert module_comparison["order"] != 0
        assert left["polarity"] == right["polarity"]
        bit = int(
            label_comparison["order"]
            == left["polarity"] * module_comparison["order"]
        )
        chronology = (
            "same_occurrence_increasing"
            if left["polarity"] == 1
            else "same_occurrence_decreasing"
        )
    return {
        "left": left["id"],
        "right": right["id"],
        "source_pair": "+".join(sorted((left["source"], right["source"]))),
        "occurrences": [left["occurrence"], right["occurrence"]],
        "chronology": chronology,
        "label_method": label_comparison["method"],
        "label_order": label_comparison["order"],
        "module_method": None
        if module_comparison is None
        else module_comparison["method"],
        "module_order": None
        if module_comparison is None
        else module_comparison["order"],
        "bit": bit,
    }


def semantic_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        key: record[key]
        for key in (
            "left",
            "right",
            "source_pair",
            "occurrences",
            "chronology",
            "label_order",
            "module_order",
            "bit",
        )
    }


def canonical_line(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def cell_result(
    inverse: Any,
    generator: Any,
    cell: Any,
    g_zero_templates: dict[tuple[str, str], Any],
    g_q_templates: dict[tuple[str, str], Any],
    metadata: dict[str, dict[str, Any]],
    occurrences: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    fibers, equality_methods = cell_fibers(
        inverse, generator, g_q_templates, metadata, cell
    )
    tokens = token_rows(
        cell, g_zero_templates, g_q_templates, fibers, occurrences
    )
    digest = hashlib.sha256()
    semantic_digest = hashlib.sha256()
    bit_count = 0
    pair_count = 0
    source_counts: Counter[str] = Counter()
    source_xors: Counter[str] = Counter()
    chronology_counts: Counter[str] = Counter()
    label_methods: Counter[str] = Counter()
    module_methods: Counter[str] = Counter()
    for left_index, left in enumerate(tokens):
        for right in tokens[left_index + 1 :]:
            record = pair_record(inverse, generator, left, right)
            digest.update(canonical_line(record))
            semantic_digest.update(canonical_line(semantic_record(record)))
            pair_count += 1
            bit_count += record["bit"]
            source_counts[record["source_pair"]] += 1
            source_xors[record["source_pair"]] ^= record["bit"]
            chronology_counts[record["chronology"]] += 1
            label_methods[record["label_method"]] += 1
            if record["module_method"] is not None:
                module_methods[record["module_method"]] += 1
    assert pair_count == 168 * 167 // 2 == 14028
    return {
        "cell": cell.cell_id,
        "predicate": {
            "a": cell.a_value if cell.a_value is not None else ">=3",
            "n": cell.n_value if cell.n_value is not None else ">=3",
        },
        "g_q_collision_fibers": fibers,
        "g_q_fiber_counts": {
            "total": len(fibers),
            "active": sum(item["activity_parity"] for item in fibers),
            "equality_methods": equality_methods,
        },
        "token_counts": {"g0": 24, "gQ": 144, "total": len(tokens)},
        "pair_count": pair_count,
        "one_count": bit_count,
        "N": bit_count % 2,
        "ordered_pair_digest_sha256": digest.hexdigest(),
        "semantic_pair_digest_sha256": semantic_digest.hexdigest(),
        "pair_source_counts": dict(sorted(source_counts.items())),
        "pair_source_xors": dict(sorted(source_xors.items())),
        "chronology_counts": dict(sorted(chronology_counts.items())),
        "label_method_counts": dict(sorted(label_methods.items())),
        "module_method_counts": dict(sorted(module_methods.items())),
    }


def cell_contains(cell: Cell, a: int, n: int) -> bool:
    return (
        a >= 0
        and n >= 0
        and (a == cell.a_value if cell.a_value is not None else a >= 3)
        and (n == cell.n_value if cell.n_value is not None else n >= 3)
    )


def direct_shortlex(left: tuple[int, ...], right: tuple[int, ...]) -> int:
    return -1 if (len(left), left) < (len(right), right) else 1 if left != right else 0


def direct_tokens(
    generator: Any,
    metadata: dict[str, dict[str, Any]],
    occurrences: dict[int, dict[str, Any]],
    a: int,
    n: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    actions = {
        order: generator.parse_raw(item["quotient_prefix"])
        for order, item in occurrences.items()
    }
    provenance = []
    for row_key, row in sorted(
        metadata.items(), key=lambda item: (item[1]["nu"], item[1]["k"])
    ):
        nu = row["nu"]
        delta_values = (0, 1)
        p_forest, c_forest, q_forest = generator.BLOCKS[nu - 1]
        p_word = generator.eval_path(p_forest)
        c_word = generator.eval_path(c_forest)
        q_word = generator.eval_path(q_forest)
        root = generator.parse_raw(generator.W_ROOTS[nu - 1])
        letter = q_forest[row["k"]]
        slot, incidence, multiplier, _ = generator.edge_rule(letter)
        assert slot == row["slot"] and incidence == row["incidence"]
        prefix = generator.eval_path(q_forest[: row["k"]])
        for delta in delta_values:
            vertex = generator.lift.c_vertex(
                generator.lift.quotient_reduce(
                    (
                        *multiplier,
                        *prefix,
                        *generator.quotient_power(q_word, a),
                        *c_word,
                        *generator.quotient_power(p_word, a + n + 1 + delta),
                        *root,
                    )
                )
            )
            provenance.append(
                {
                    "id": f"{row_key}:delta{delta}",
                    "slot": slot,
                    "coefficient": row["source_sign"]
                    * incidence
                    * (1 if delta == 0 else -1),
                    "vertex": vertex,
                }
            )
    assert len(provenance) == 184
    grouped: dict[tuple[int, tuple[int, ...]], list[dict[str, Any]]] = {}
    for row in provenance:
        grouped.setdefault((row["slot"], row["vertex"]), []).append(row)
    fibers = []
    for (slot, vertex), members in grouped.items():
        members = sorted(members, key=lambda item: item["id"])
        coefficient_sum = sum(item["coefficient"] for item in members)
        fibers.append(
            {
                "slot": slot,
                "vertex": vertex,
                "members": [item["id"] for item in members],
                "integral_coefficient_sum": coefficient_sum,
                "activity_parity": coefficient_sum % 2,
            }
        )
    fibers.sort(key=lambda item: (item["slot"], item["members"]))
    assert len(fibers) == 106
    assert sum(item["activity_parity"] for item in fibers) == 72

    tokens = []
    gamma = generator.eval_path(generator.BLOCKS[0][2])
    gamma_inverse = generator.lift.quotient_inverse(gamma)
    p_inverse = generator.lift.quotient_inverse(generator.parse_raw("tc"))
    corners = {
        "00": (a + 1, a + n + 2),
        "01": (a, a + n + 2),
        "11": (a + 1, a + n + 3),
        "12": (a, a + n + 3),
    }
    for corner, (q_exponent, p_exponent) in corners.items():
        vertex = generator.lift.c_vertex(
            generator.lift.quotient_reduce(
                (
                    *p_inverse,
                    *generator.quotient_power(gamma, q_exponent),
                    *generator.parse_raw("c"),
                    *generator.quotient_power(gamma_inverse, p_exponent),
                    *generator.parse_raw("t"),
                )
            )
        )
        for occurrence in (3, 4, 7, 8, 11, 12):
            tokens.append(
                {
                    "id": f"g0:{corner}:o{occurrence}",
                    "source": "g0",
                    "occurrence": occurrence,
                    "polarity": occurrences[occurrence]["polarity"],
                    "module_word": vertex,
                    "label_word": generator.lift.c_vertex(
                        generator.lift.quotient_multiply(
                            actions[occurrence], vertex
                        )
                    ),
                }
            )
    occurrences_by_slot = {2: (1, 6), 3: (9, 14), 4: (15, 16)}
    for fiber_index, fiber in enumerate(fibers):
        if not fiber["activity_parity"]:
            continue
        for occurrence in occurrences_by_slot[fiber["slot"]]:
            vertex = fiber["vertex"]
            tokens.append(
                {
                    "id": f"gq:f{fiber_index:03d}:o{occurrence}",
                    "source": "gQ",
                    "occurrence": occurrence,
                    "polarity": occurrences[occurrence]["polarity"],
                    "module_word": vertex,
                    "label_word": generator.lift.c_vertex(
                        generator.lift.quotient_multiply(
                            actions[occurrence], vertex
                        )
                    ),
                }
            )
    tokens.sort(key=lambda item: item["id"])
    assert len(tokens) == 168
    return tokens, fibers


def direct_semantic_record(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    label_order = direct_shortlex(left["label_word"], right["label_word"])
    if left["occurrence"] != right["occurrence"]:
        chronological_order = -1 if left["occurrence"] < right["occurrence"] else 1
        bit = int(label_order == chronological_order)
        module_order = None
        chronology = "literal_occurrence_order"
    else:
        module_order = direct_shortlex(left["module_word"], right["module_word"])
        assert module_order != 0
        assert left["polarity"] == right["polarity"]
        bit = int(label_order == left["polarity"] * module_order)
        chronology = (
            "same_occurrence_increasing"
            if left["polarity"] == 1
            else "same_occurrence_decreasing"
        )
    return {
        "left": left["id"],
        "right": right["id"],
        "source_pair": "+".join(sorted((left["source"], right["source"]))),
        "occurrences": [left["occurrence"], right["occurrence"]],
        "chronology": chronology,
        "label_order": label_order,
        "module_order": module_order,
        "bit": bit,
    }


def direct_replay(
    generator: Any,
    metadata: dict[str, dict[str, Any]],
    occurrences: dict[int, dict[str, Any]],
    cells: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    expected = {item["cell"]: item for item in cells}
    points = ((0, 0), (0, 4), (1, 0), (2, 2), (4, 0), (4, 4))
    output = []
    for a, n in points:
        matched = [cell for cell in CELLS if cell_contains(cell, a, n)]
        assert len(matched) == 1
        cell = matched[0]
        tokens, fibers = direct_tokens(generator, metadata, occurrences, a, n)
        digest = hashlib.sha256()
        one_count = 0
        pair_count = 0
        for left_index, left in enumerate(tokens):
            for right in tokens[left_index + 1 :]:
                record = direct_semantic_record(left, right)
                digest.update(canonical_line(record))
                one_count += record["bit"]
                pair_count += 1
        assert pair_count == 14028
        expected_cell = expected[cell.cell_id]
        assert digest.hexdigest() == expected_cell["semantic_pair_digest_sha256"]
        assert one_count == expected_cell["one_count"]
        output.append(
            {
                "a": a,
                "n": n,
                "i": a + n + 1,
                "d": a + 1,
                "cell": cell.cell_id,
                "fibers": len(fibers),
                "active_fibers": sum(item["activity_parity"] for item in fibers),
                "tokens": len(tokens),
                "pairs": pair_count,
                "one_count": one_count,
                "N": one_count % 2,
                "semantic_pair_digest_sha256": digest.hexdigest(),
            }
        )
    return output


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_manifest() -> dict[str, Any]:
    inverse = load_module("new_new_inverse_checker", INVERSE_CHECKER_PATH)
    generator = inverse.load_raw_generator()
    p = generator.parse_raw("tc")
    assert generator.lit(p) == "tc"
    assert generator.lit(generator.lift.quotient_inverse(p)) == "cT"
    g_q_schemas, metadata = inverse.schema_words(generator)
    g_q_templates = build_templates(inverse, generator, g_q_schemas)
    g_zero_schema_map = g_zero_schemas(inverse, generator)
    g_zero_templates = build_templates(inverse, generator, g_zero_schema_map)
    occurrences = {item["order"]: item for item in generator.trace_ast()[1]}
    cells = [
        cell_result(
            inverse,
            generator,
            cell,
            g_zero_templates,
            g_q_templates,
            metadata,
            occurrences,
        )
        for cell in CELLS
    ]
    assert len(cells) == 16
    assert all(item["N"] == 0 for item in cells)
    replays = direct_replay(generator, metadata, occurrences, cells)
    return {
        "format": "period-two-new-new-aggregate-v1",
        "domain": "a=d-1>=0, n=i-d>=0",
        "raw_parser_guard": {"p": "tc", "p_inverse": "cT"},
        "theorem": {
            "name": "N(i,d)=Q(g^(0)+g^(Q))",
            "formula": "N(i,d)=0 for every i>=d>=1",
            "cell_values": {item["cell"]: item["N"] for item in cells},
        },
        "g_zero_schemas": {
            schema_id: {
                "source_left": generator.lit(schema.source_left),
                "source_q": generator.lit(schema.source_q),
                "source_middle": generator.lit(schema.source_middle),
                "source_p": generator.lit(schema.source_p),
                "source_right": generator.lit(schema.source_right),
                "q_core": generator.lit(schema.q_core),
                "q_multiplier": schema.q_multiplier,
                "p_core": generator.lit(schema.p_core),
                "p_multiplier": schema.p_multiplier,
                "p_offset": schema.p_offset,
            }
            for schema_id, schema in sorted(g_zero_schema_map.items())
        },
        "cells": cells,
        "direct_replays": replays,
        "checks": {
            "cells": len(cells),
            "g_zero_schemas": len(g_zero_schema_map),
            "g_zero_templates": len(g_zero_templates),
            "g_q_provenance_rows": 184,
            "g_q_fibers_per_cell": 106,
            "g_q_active_fibers_per_cell": 72,
            "tokens_per_cell": 168,
            "pairs_per_cell": 14028,
            "pairs_all_cells": 16 * 14028,
            "direct_replays": len(replays),
            "direct_replay_failures": 0,
            "coverage_failures": 0,
            "collision_failures": 0,
            "chronology_failures": 0,
        },
        "provenance": {
            "inputs": {
                str(INVERSE_CHECKER_PATH.relative_to(ROOT)): sha256_path(
                    INVERSE_CHECKER_PATH
                ),
                ".scratch/period_two_inverse_q_companion_manifest.json": sha256_path(
                    ROOT / ".scratch/period_two_inverse_q_companion_manifest.json"
                ),
                ".scratch/period_two_residual_augmented_defect.md": sha256_path(
                    ROOT / ".scratch/period_two_residual_augmented_defect.md"
                ),
            },
            "checker_sha256": sha256_path(Path(__file__).resolve()),
        },
    }


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def write_manifest() -> dict[str, Any]:
    manifest = build_manifest()
    MANIFEST_PATH.write_bytes(canonical_json(manifest))
    return manifest


def check_manifest() -> dict[str, Any]:
    manifest = build_manifest()
    assert MANIFEST_PATH.read_bytes() == canonical_json(manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    if args.write:
        manifest = write_manifest()
    elif args.check:
        manifest = check_manifest()
    else:
        manifest = build_manifest()
    print(
        json.dumps(
            {
                "status": "PASS",
                "cell_values": manifest["theorem"]["cell_values"],
                "checks": manifest["checks"],
                "pair_digests": {
                    item["cell"]: item["ordered_pair_digest_sha256"]
                    for item in manifest["cells"]
                },
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
