#!/usr/bin/env python3
"""Independent replay of frozen diagonal pure-P raw manifest.

This module never imports the primary diagonal checker.  It reconstructs the
46 signed P/C source rows from the authoritative row generator, derives its
own powered normal forms from the reviewed normalizer, collision-aggregates
the current, and evaluates literal rho observables with the reviewed raw
evaluator.  It verifies only the provisional nonzero-slot raw certificate.
No old-new, quadratic, diagonal, period-two, AK3, stable-AC, or AC conclusion
is made.
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
MANIFEST_PATH = ROOT / ".scratch/period_two_diagonal_pure_p_raw_manifest.json"
GENERATOR_PATH = ROOT / ".scratch/period_two_raw_stream_manifest_generator.py"
NORMALIZER_PATH = ROOT / ".scratch/period_two_inverse_q_companion_checker.py"
RAW_PATH = ROOT / ".scratch/period_two_residual_augmented_defect_raw_checker.py"
THEORY_PATH = ROOT / "literature/proofs/AK3_PURE_P_INCREMENT_NORMAL_FORM.md"
REPLAY_PATH = Path(__file__).resolve()
TEST_PATH = ROOT / ".scratch/test_period_two_diagonal_pure_p_raw_independent_replay.py"
THEORY_SECTION_START = b"### 4.1 Raw boundary-locality pump\n"
THEORY_SECTION_END = b"### 4.2 All-power raw theorem\n"
Word = tuple[int, ...]

CELLS = (
    ("e0_n0", 0, False),
    ("e0_n1", 1, False),
    ("e0_n2", 2, False),
    ("e0_nge3", 3, True),
)
OCCURRENCES_BY_SLOT = {2: (1, 6), 3: (9, 14), 4: (15, 16)}
EXPECTED_FAMILIES = {
    "long_p1": 14,
    "long_pstar": 18,
    "short_w2": 4,
    "short_w3": 4,
    "short_z3": 6,
}
EXPECTED_PROFILE = {"2": 9, "3": 15, "4": 18}


@dataclass(frozen=True)
class Schema:
    schema_id: str
    source_left: Word
    source_power: Word
    source_right: Word
    fixed_left: Word
    core: Word
    multiplier: int
    fixed_right: Word
    offset: int


@dataclass(frozen=True)
class Template:
    schema_id: str
    base_i: int
    blocks: tuple[tuple[str, Word, tuple[int, int, int] | None], ...]
    base_word: Word
    split: int
    left_copy: int
    right_copy: int


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


def exact_section_record(data: bytes) -> dict[str, Any]:
    if data.count(THEORY_SECTION_START) != 1 or data.count(THEORY_SECTION_END) != 1:
        raise AssertionError("theory_section_markers")
    start = data.index(THEORY_SECTION_START) + len(THEORY_SECTION_START)
    end = data.index(THEORY_SECTION_END)
    if end < start:
        raise AssertionError("theory_section_order")
    section = data[start:end]
    return {
        "start_marker": THEORY_SECTION_START.decode().removesuffix("\n"),
        "end_marker": THEORY_SECTION_END.decode().removesuffix("\n"),
        "byte_length": len(section),
        "section_sha256": hashlib.sha256(section).hexdigest(),
    }


def theory_section_binding() -> dict[str, Any]:
    return {
        "path": str(THEORY_PATH.relative_to(ROOT)),
        "scope": "source-bound raw boundary-locality induction only",
        **exact_section_record(THEORY_PATH.read_bytes()),
    }


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def parse_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    return json.loads(path.read_text())


def const_value(exponent: dict[str, Any]) -> int | None:
    return exponent.get("value") if exponent.get("op") == "const" else None


def variable_name(exponent: dict[str, Any]) -> str | None:
    return exponent.get("name") if exponent.get("op") == "var" else None


def selected_sources(generator: Any) -> list[dict[str, Any]]:
    _, source_rows = generator.build_w_rows()
    by_id = {row["id"]: row for row in source_rows}
    selected: list[dict[str, Any]] = []

    def append(source_id: str, family: str, state: str, offset: int, sign: int) -> None:
        source = by_id[source_id]
        selected.append(
            {
                "source": source,
                "family": family,
                "state": state,
                "offset": offset,
                "direction_sign": sign,
                "factor_order": source["module_vertex"]["factors"],
            }
        )

    for nu, family in ((1, "long_p1"), (3, "long_pstar")):
        for position in range(len(generator.BLOCKS[nu - 1][0])):
            append(
                f"W:nu{nu}:P:{position}:o+1",
                family,
                "new_segment",
                1,
                1,
            )

    short_specs = (
        (4, "short_w3", generator.BLOCKS[2][0]),
        (5, "short_z3", generator.BLOCKS[2][0]),
        (6, "short_w2", generator.BLOCKS[1][1]),
    )
    for nu, family, prefix in short_specs:
        word = generator.BLOCKS[nu - 1][1]
        if not word.startswith(prefix):
            raise AssertionError((nu, prefix, word))
        for position in range(len(prefix), len(word)):
            source_id = f"W:nu{nu}:C:{position}:o+1"
            append(source_id, family, "old", 0, -1)
            append(source_id, family, "new", 1, 1)
    if len(selected) != 46:
        raise AssertionError(len(selected))
    return selected


def schema_from_factors(
    normalizer: Any,
    generator: Any,
    schema_id: str,
    factors: list[dict[str, Any]],
    variable: str,
    offset: int,
) -> Schema:
    positions = [
        index
        for index, factor in enumerate(factors)
        if variable_name(factor["exponent"]) == variable
    ]
    if len(positions) != 1:
        raise AssertionError((schema_id, variable, positions, factors))
    variable_index = positions[0]
    for index, factor in enumerate(factors):
        if index != variable_index and const_value(factor["exponent"]) != 1:
            raise AssertionError((schema_id, index, factor["exponent"]))
    words = [generator.parse_raw(factor["word"]) for factor in factors]
    power = words[variable_index]
    _, cyclic_core, _ = normalizer.cyclic_decomposition(generator, power)
    reference, _ = normalizer.primitive_power(cyclic_core)
    fixed_left, core, multiplier, fixed_right = (
        normalizer.reference_primitive_decomposition(generator, power, reference)
    )
    return Schema(
        schema_id=schema_id,
        source_left=tuple(
            letter for word in words[:variable_index] for letter in word
        ),
        source_power=power,
        source_right=tuple(
            letter for word in words[variable_index + 1 :] for letter in word
        ),
        fixed_left=fixed_left,
        core=core,
        multiplier=multiplier,
        fixed_right=fixed_right,
        offset=offset,
    )


def prefixed_schema(schema: Schema, schema_id: str, action: Word) -> Schema:
    return Schema(
        schema_id=schema_id,
        source_left=(*action, *schema.source_left),
        source_power=schema.source_power,
        source_right=schema.source_right,
        fixed_left=schema.fixed_left,
        core=schema.core,
        multiplier=schema.multiplier,
        fixed_right=schema.fixed_right,
        offset=schema.offset,
    )


def schema_record(generator: Any, schema: Schema) -> dict[str, Any]:
    return {
        "id": schema.schema_id,
        "source": {
            "left": generator.lit(schema.source_left),
            "q": "",
            "q_exponent": [1, 0, 0],
            "middle": "",
            "p": generator.lit(schema.source_power),
            "p_exponent": [0, 1, schema.offset],
            "right": generator.lit(schema.source_right),
        },
        "normal_form": {
            "fixed_0": generator.lit(schema.source_left),
            "q_core": "",
            "q_multiplier": 0,
            "fixed_1": generator.lit(schema.fixed_left),
            "p_core": generator.lit(schema.core),
            "p_multiplier": schema.multiplier,
            "fixed_2": generator.lit(
                (*schema.fixed_right, *schema.source_right)
            ),
        },
    }


def expected_inventory(
    normalizer: Any,
    generator: Any,
    actions: dict[int, Word],
) -> tuple[list[dict[str, Any]], dict[str, Schema], list[dict[str, Any]]]:
    provenance: list[dict[str, Any]] = []
    schemas: dict[str, Schema] = {}
    factor_audit: list[dict[str, Any]] = []
    for item in selected_sources(generator):
        source = item["source"]
        variable = "h" if source["key"]["block"] == "P" else "i"
        row_id = f"diag:{item['family']}:{item['state']}:{source['id']}"
        module_id = f"{row_id}:module"
        module = schema_from_factors(
            normalizer,
            generator,
            module_id,
            item["factor_order"],
            variable,
            item["offset"],
        )
        schemas[module_id] = module
        label_ids: dict[str, str] = {}
        slot = source["key"]["slot"]
        for occurrence in OCCURRENCES_BY_SLOT[slot]:
            label_id = f"{row_id}:label:o{occurrence}"
            schemas[label_id] = prefixed_schema(
                module, label_id, actions[occurrence]
            )
            label_ids[str(occurrence)] = label_id
        provenance.append(
            {
                "id": row_id,
                "source_row_id": source["id"],
                "family": item["family"],
                "state": item["state"],
                "power_offset": item["offset"],
                "nu": source["key"]["nu"],
                "block": source["key"]["block"],
                "position": source["key"]["position"],
                "stored_letter": source["stored_letter"],
                "actual_letter": source["actual_letter"],
                "slot": slot,
                "source_scale": source["source_scale"],
                "incidence_sign": source["incidence_sign"],
                "direction_sign": item["direction_sign"],
                "integral_coefficient": (
                    item["direction_sign"] * source["coefficient"]
                ),
                "module_schema": module_id,
                "label_schemas": label_ids,
                "source_binding": "build_w_rows:P(h=i+1) or C-tail(i+delta)",
            }
        )
        factor_audit.append(
            {
                "id": row_id,
                "source_row_id": source["id"],
                "factor_order": item["factor_order"],
            }
        )
    provenance.sort(key=lambda row: row["id"])
    factor_audit.sort(key=lambda row: row["id"])
    return provenance, schemas, factor_audit


def factor_order_failures(generator: Any, selected: list[dict[str, Any]]) -> list[str]:
    failures: list[str] = []
    for item in selected:
        source = item["source"]
        expected_pre = [
            generator.factor(
                generator.eval_path(factor["word"]), factor["exponent"]
            )
            for factor in reversed(source["raw_prefix"])
        ] + [generator.factor(source["root"], generator.const(1))]
        _, _, multiplier, _ = generator.edge_rule(source["actual_letter"])
        expected = [
            generator.factor(multiplier, generator.const(1)),
            *expected_pre,
        ]
        if source["module_vertex"]["factors"] != expected:
            failures.append(f"factor_order:{source['id']}")
    return failures


def direct_vertex(generator: Any, schema: Schema, i: int) -> Word:
    powered = generator.quotient_power(schema.source_power, i + schema.offset)
    return generator.lift.c_vertex(
        generator.lift.quotient_reduce(
            (*schema.source_left, *powered, *schema.source_right)
        )
    )


def tagged_vertex(generator: Any, schema: Schema, i: int) -> list[tuple[int, tuple[Any, ...]]]:
    exponent = schema.multiplier * (i + schema.offset)
    expanded: list[tuple[int, tuple[Any, ...]]] = []
    expanded.extend(
        (letter, ("fixed", 0, phase))
        for phase, letter in enumerate(schema.source_left)
    )
    expanded.extend(
        (letter, ("fixed", 1, phase))
        for phase, letter in enumerate(schema.fixed_left)
    )
    expanded.extend(
        (letter, ("p", copy, phase))
        for copy in range(exponent)
        for phase, letter in enumerate(schema.core)
    )
    suffix = (*schema.fixed_right, *schema.source_right)
    expanded.extend(
        (letter, ("fixed", 2, phase))
        for phase, letter in enumerate(suffix)
    )
    reduced: list[tuple[int, tuple[Any, ...]]] = []
    for raw_letter, tag in expanded:
        letter = (
            generator.lift.C
            if abs(raw_letter) == generator.lift.C
            else raw_letter
        )
        inverse = generator.lift.C if abs(letter) == generator.lift.C else -letter
        if reduced and reduced[-1][0] == inverse:
            reduced.pop()
        else:
            reduced.append((letter, tag))
    if reduced and abs(reduced[-1][0]) == generator.lift.C:
        return reduced[:-1]
    return reduced


def build_template(normalizer: Any, generator: Any, schema: Schema) -> Template:
    tagged = tagged_vertex(generator, schema, 3)
    boundary = normalizer.intact_boundary(tagged, "p", len(schema.core))
    if boundary is None:
        raise AssertionError((schema.schema_id, "missing_intact_boundary"))
    base_word = tuple(letter for letter, _ in tagged)
    split = boundary["split"]
    blocks: list[tuple[str, Word, tuple[int, int, int] | None]] = []
    if base_word[:split]:
        blocks.append(("fixed", base_word[:split], None))
    blocks.append(("p", schema.core, (0, schema.multiplier, -3 * schema.multiplier)))
    if base_word[split:]:
        blocks.append(("fixed", base_word[split:], None))
    return Template(
        schema_id=schema.schema_id,
        base_i=3,
        blocks=tuple(blocks),
        base_word=base_word,
        split=split,
        left_copy=boundary["left_copy"],
        right_copy=boundary["right_copy"],
    )


def expand_template(template: Template, i: int) -> Word:
    output: list[int] = []
    for kind, word, affine in template.blocks:
        if kind == "fixed":
            output.extend(word)
        else:
            if affine is None:
                raise AssertionError(template.schema_id)
            copies = affine[0] * 0 + affine[1] * i + affine[2]
            if copies < 0:
                raise AssertionError((template.schema_id, i, copies))
            output.extend(word * copies)
    return tuple(output)


def coordinate_id(members: list[dict[str, Any]]) -> str:
    payload = "|".join(sorted(member["id"] for member in members)).encode()
    return f"coord:{hashlib.sha256(payload).hexdigest()[:16]}"


def collision_groups(
    normalizer: Any,
    generator: Any,
    provenance: list[dict[str, Any]],
    schemas: dict[str, Schema],
    i: int,
    unbounded: bool,
) -> list[dict[str, Any]]:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    template_cache: dict[str, Template] = {}
    for row in provenance:
        schema = schemas[row["module_schema"]]
        if unbounded:
            template = template_cache.setdefault(
                schema.schema_id, build_template(normalizer, generator, schema)
            )
            key_word = normalizer.normalize_blocks(template.blocks)
        else:
            key_word = direct_vertex(generator, schema, i)
        grouped.setdefault((row["slot"], key_word), []).append(row)
    fibers: list[dict[str, Any]] = []
    for members in sorted(
        grouped.values(),
        key=lambda rows: (rows[0]["slot"], sorted(row["id"] for row in rows)),
    ):
        members = sorted(members, key=lambda row: row["id"])
        representative = members[0]
        coefficient = sum(row["integral_coefficient"] for row in members)
        fibers.append(
            {
                "coordinate_id": coordinate_id(members),
                "slot": representative["slot"],
                "families": sorted({row["family"] for row in members}),
                "members": [row["id"] for row in members],
                "integral_coefficient_sum": coefficient,
                "activity_parity": coefficient % 2,
                "module_schema": representative["module_schema"],
                "label_schemas": {
                    str(occurrence): representative["label_schemas"][str(occurrence)]
                    for occurrence in OCCURRENCES_BY_SLOT[representative["slot"]]
                },
            }
        )
    return fibers


def observable_record(generator: Any, observable: tuple[Any, ...]) -> dict[str, Any]:
    labels, equalities, rho, central = observable
    return {
        "first_half_labels": [generator.lit(label) for label in labels],
        "equalities": list(equalities),
        "rho": rho,
        "central_label": generator.lit(central),
        "central_length": len(central),
        "max_first_half_length": max((len(label) for label in labels), default=-1),
    }


def expected_pump(
    normalizer: Any,
    residual: Any,
    generator: Any,
    schema: Schema,
    action: Word,
    base_observable: tuple[Any, ...],
) -> dict[str, Any]:
    template = build_template(normalizer, generator, schema)
    base_vertex = direct_vertex(generator, schema, 3)
    next_vertex = direct_vertex(generator, schema, 4)
    next_observable = residual.raw_observable(generator, action, next_vertex)
    increment = schema.multiplier
    boundary = template.split + increment * len(schema.core)
    return {
        "variable": "i",
        "block": "p",
        "core": generator.lit(schema.core),
        "core_length": len(schema.core),
        "insertion_split": template.split,
        "affine_increment": increment,
        "action_horizon": len(action) + 1,
        "saturated_boundary": boundary,
        "horizon_saturated": boundary > len(action) + 1,
        "base_next_observable_signature_equal": (
            base_observable[:3] == next_observable[:3]
        ),
        "central_length_slope": len(next_observable[3]) - len(base_observable[3]),
        "stable_schema_equality": (
            template.base_word == base_vertex
            and expand_template(template, 3) == base_vertex
            and expand_template(template, 4) == next_vertex
        ),
        "one_step": observable_record(generator, next_observable),
    }


def expected_tokens_and_raw(
    normalizer: Any,
    residual: Any,
    generator: Any,
    occurrences: dict[int, dict[str, Any]],
    actions: dict[int, Word],
    schemas: dict[str, Schema],
    fibers: list[dict[str, Any]],
    cell_id: str,
    i: int,
    unbounded: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    tokens: list[dict[str, Any]] = []
    raw: list[dict[str, Any]] = []
    for fiber in fibers:
        if not fiber["activity_parity"]:
            continue
        family = (
            fiber["families"][0]
            if len(fiber["families"]) == 1
            else "+".join(fiber["families"])
        )
        schema = schemas[fiber["module_schema"]]
        vertex = direct_vertex(generator, schema, i)
        for occurrence in OCCURRENCES_BY_SLOT[fiber["slot"]]:
            label_schema = fiber["label_schemas"][str(occurrence)]
            token_id = f"{cell_id}:{fiber['coordinate_id']}:o{occurrence}"
            tokens.append(
                {
                    "id": token_id,
                    "coordinate_id": fiber["coordinate_id"],
                    "family": family,
                    "slot": fiber["slot"],
                    "occurrence": occurrence,
                    "polarity": occurrences[occurrence]["polarity"],
                    "module_schema": fiber["module_schema"],
                    "label_schema": label_schema,
                }
            )
            action = actions[occurrence]
            observable = residual.raw_observable(generator, action, vertex)
            base = observable_record(generator, observable)
            locality = {
                "action_horizon": len(action) + 1,
                "all_first_half_noncentral": not any(observable[1]),
                "central_strictly_longer": (
                    not observable[0]
                    or len(observable[3])
                    > max(len(label) for label in observable[0])
                ),
            }
            raw.append(
                {
                    "id": f"raw:{token_id}",
                    "token_id": token_id,
                    "coordinate_id": fiber["coordinate_id"],
                    "family": family,
                    "slot": fiber["slot"],
                    "occurrence": occurrence,
                    "action": generator.lit(action),
                    "module_schema": fiber["module_schema"],
                    "base": base,
                    "locality": locality,
                    "pumps": (
                        [
                            expected_pump(
                                normalizer,
                                residual,
                                generator,
                                schema,
                                action,
                                observable,
                            )
                        ]
                        if unbounded
                        else []
                    ),
                    "source_binding": "literal raw_observable + one-increment horizon shield",
                }
            )
    tokens.sort(key=lambda token: token["id"])
    raw.sort(key=lambda record: record["token_id"])
    return tokens, raw


def current_source_hash_failures(manifest: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    bindings = manifest.get("source_bindings", {})
    for name, record in bindings.items():
        if name == "theory":
            continue
        path = ROOT / record["path"]
        if not path.is_file():
            failures.append(f"source_missing:{name}:{record['path']}")
        elif record.get("sha256") != sha256_path(path):
            failures.append(f"source_hash:{name}")
    if bindings.get("theory") != theory_section_binding():
        failures.append("source_section:theory")
    return failures


def replay_bindings() -> dict[str, dict[str, str]]:
    return {
        "replay": {
            "path": str(REPLAY_PATH.relative_to(ROOT)),
            "sha256": sha256_path(REPLAY_PATH),
        },
        "tests": {
            "path": str(TEST_PATH.relative_to(ROOT)),
            "sha256": sha256_path(TEST_PATH),
        },
    }


def verification_failures(manifest: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    try:
        if manifest.get("format") != "period-two-diagonal-pure-p-raw-provisional-v1":
            failures.append("format")
        if manifest.get("generation_failures"):
            failures.append("generation_failures")
        if manifest.get("scope", {}).get("status") != (
            "provisional_pending_independent_replay_and_sol_review"
        ):
            failures.append("status")
        failures.extend(current_source_hash_failures(manifest))

        normalizer = load_module("diag_raw_replay_normalizer", NORMALIZER_PATH)
        residual = load_module("diag_raw_replay_observable", RAW_PATH)
        generator = normalizer.load_raw_generator()
        occurrences = {item["order"]: item for item in generator.trace_ast()[1]}
        actions = {
            order: generator.parse_raw(item["quotient_prefix"])
            for order, item in occurrences.items()
        }
        parser_guard = {
            "raw_p": generator.lit(generator.parse_raw("tc")),
            "raw_p_inverse": generator.lit(
                generator.lift.quotient_inverse(generator.parse_raw("tc"))
            ),
            "module_parser_p": generator.lit(
                generator.lift.parse_quotient("tc")
            ),
        }
        if manifest.get("raw_parser_guard") != parser_guard:
            failures.append("raw_parser_guard")

        provenance, schemas, factor_audit = expected_inventory(
            normalizer, generator, actions
        )
        failures.extend(factor_order_failures(generator, selected_sources(generator)))
        if manifest.get("provenance") != provenance:
            failures.append("provenance")
        if len(factor_audit) != 46 or len({row["source_row_id"] for row in factor_audit}) != 39:
            failures.append("factor_order_audit")
        manifest_schemas = {
            record["id"]: record for record in manifest.get("schemas", [])
        }
        expected_schemas = {
            schema_id: schema_record(generator, schema)
            for schema_id, schema in schemas.items()
        }
        if manifest_schemas != expected_schemas:
            failures.append("schemas_and_factor_order")
        if len(manifest.get("schemas", [])) != 138 or len(manifest_schemas) != 138:
            failures.append("schema_count")
        if Counter(row["family"] for row in provenance) != Counter(EXPECTED_FAMILIES):
            failures.append("family_inventory")

        manifest_cells = manifest.get("cell_results", [])
        if [result.get("cell", {}).get("id") for result in manifest_cells] != [
            cell_id for cell_id, _, _ in CELLS
        ]:
            failures.append("cell_catalog")
        expected_cells = [
            {
                "id": cell_id,
                "i": "ge3" if unbounded else i,
                "base_i": i,
            }
            for cell_id, i, unbounded in CELLS
        ]
        if manifest.get("cells") != expected_cells:
            failures.append("top_cell_catalog")
        expected_catalog: list[dict[str, Any]] | None = None
        for index, (cell_id, i, unbounded) in enumerate(CELLS):
            result = manifest_cells[index]
            if result.get("cell") != expected_cells[index]:
                failures.append(f"cell_descriptor:{cell_id}")
            fibers = collision_groups(
                normalizer, generator, provenance, schemas, i, unbounded
            )
            manifest_fibers = result.get("collision", {}).get("fibers")
            if manifest_fibers != fibers:
                failures.append(f"fibers:{cell_id}")
            active = [fiber for fiber in fibers if fiber["activity_parity"]]
            profile = {
                str(slot): sum(fiber["slot"] == slot for fiber in active)
                for slot in (2, 3, 4)
            }
            if len(fibers) != 44:
                failures.append(f"fiber_count:{cell_id}")
            if len(active) != 42:
                failures.append(f"active_count:{cell_id}")
            if profile != EXPECTED_PROFILE:
                failures.append(f"profile:{cell_id}")
            collision = result.get("collision", {})
            if (
                collision.get("fiber_count") != 44
                or collision.get("active_coordinate_count") != 42
                or collision.get("active_slot_profile") != EXPECTED_PROFILE
            ):
                failures.append(f"collision_summary:{cell_id}")

            catalog = [
                {
                    "coordinate_id": fiber["coordinate_id"],
                    "slot": fiber["slot"],
                    "family": (
                        fiber["families"][0]
                        if len(fiber["families"]) == 1
                        else "+".join(fiber["families"])
                    ),
                    "members": fiber["members"],
                    "integral_coefficient_sum": fiber["integral_coefficient_sum"],
                    "module_schema": fiber["module_schema"],
                }
                for fiber in sorted(active, key=lambda fiber: fiber["coordinate_id"])
            ]
            if expected_catalog is None:
                expected_catalog = catalog
            elif catalog != expected_catalog:
                failures.append(f"unstable_catalog:{cell_id}")

            tokens, raw = expected_tokens_and_raw(
                normalizer,
                residual,
                generator,
                occurrences,
                actions,
                schemas,
                fibers,
                cell_id,
                i,
                unbounded,
            )
            if result.get("tokens") != tokens:
                failures.append(f"tokens:{cell_id}")
            if result.get("raw_records") != raw:
                failures.append(f"raw_observables:{cell_id}")
            if len(tokens) != 84 or len(raw) != 84:
                failures.append(f"observable_count:{cell_id}")
            if len({token["id"] for token in tokens}) != 84:
                failures.append(f"token_ids:{cell_id}")
            if any(len(record["pumps"]) != (1 if unbounded else 0) for record in raw):
                failures.append(f"pump_count:{cell_id}")
            for record in raw:
                if unbounded:
                    pump = record["pumps"][0]
                    if (
                        not pump["horizon_saturated"]
                        or not pump["base_next_observable_signature_equal"]
                        or pump["central_length_slope"] <= 0
                        or not pump["stable_schema_equality"]
                        or not record["locality"]["all_first_half_noncentral"]
                        or not record["locality"]["central_strictly_longer"]
                    ):
                        failures.append(f"pump_hypothesis:{record['id']}")
            raw_xor = sum(record["base"]["rho"] for record in raw) % 2
            expected_computed = {
                "L_slot_zero": 0,
                "L_nonzero": raw_xor,
                "raw_observable_count": 84,
                "status": "provisional_pending_independent_replay_and_sol_review",
            }
            if result.get("computed") != expected_computed:
                failures.append(f"computed:{cell_id}")
            if result.get("generation_failures"):
                failures.append(f"cell_generation_failures:{cell_id}")

        if manifest.get("coordinate_schemas") != (expected_catalog or []):
            failures.append("coordinate_catalog")
        if manifest.get("five_family_traversal_inventory") != EXPECTED_FAMILIES:
            failures.append("five_family_traversal_inventory")
    except Exception as exc:
        failures.append(f"manifest_shape:{type(exc).__name__}:{exc}")
    return failures


def verify_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    failures = verification_failures(manifest)
    if failures:
        raise AssertionError(failures[:24])
    return manifest


def summary(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "independent replay passed",
        "manifest_format": manifest["format"],
        "provenance_rows": len(manifest["provenance"]),
        "active_coordinates": len(manifest["coordinate_schemas"]),
        "cell_xors": {
            result["cell"]["id"]: result["computed"]["L_nonzero"]
            for result in manifest["cell_results"]
        },
        "replay_bindings": replay_bindings(),
        "strict_nonclaim": (
            "raw replay only; no old-new, Q, diagonal, lift, AK3, stable-AC, or AC claim"
        ),
    }


def argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    return parser


def main() -> None:
    args = argument_parser().parse_args()
    manifest = verify_manifest(parse_manifest(args.manifest))
    print(json.dumps(summary(manifest), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
