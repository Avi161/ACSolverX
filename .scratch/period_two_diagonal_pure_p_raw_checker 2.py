#!/usr/bin/env python3
"""Provisional all-power raw certificate for the diagonal pure-P increment.

This checker certifies only the nonzero-slot raw xor of

    p_i^Delta = A_(i+1,i+1) + A_(i,i),  i >= 0.

It derives 46 signed literal traversals from the approved P/C source rows,
collision-aggregates them to 42 active coordinate schemas, expands those at
the two correction occurrences of their slot, and evaluates all 84 literal
rho observables.  The unbounded cell uses an intact one-increment pump with
an action-horizon shield.  Generated values are reported, never imposed as a
theorem.  Status stays provisional until independent replay and Sol review.
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
CHECKER_PATH = Path(__file__).resolve()
TEST_PATH = ROOT / ".scratch/test_period_two_diagonal_pure_p_raw_checker.py"
APPROVED_PATH = ROOT / ".scratch/period_two_inverse_pure_increment_checker.py"
NORMALIZER_PATH = ROOT / ".scratch/period_two_inverse_q_companion_checker.py"
RAW_PATH = ROOT / ".scratch/period_two_residual_augmented_defect_raw_checker.py"
GENERATOR_PATH = ROOT / ".scratch/period_two_raw_stream_manifest_generator.py"
PROOF_PATH = ROOT / "literature/proofs/AK3_PURE_P_INCREMENT_NORMAL_FORM.md"
MANIFEST_PATH = ROOT / ".scratch/period_two_diagonal_pure_p_raw_manifest.json"
THEORY_SECTION_START = b"### 4.1 Raw boundary-locality pump\n"
THEORY_SECTION_END = b"### 4.2 All-power raw theorem\n"
Word = tuple[int, ...]


@dataclass(frozen=True)
class ICell:
    cell_id: str
    value: int | None
    base_i: int


CELLS = (
    ICell("e0_n0", 0, 0),
    ICell("e0_n1", 1, 1),
    ICell("e0_n2", 2, 2),
    ICell("e0_nge3", None, 3),
)

OCCURRENCES_BY_SLOT = {2: (1, 6), 3: (9, 14), 4: (15, 16)}
EXPECTED_TRAVERSAL_FAMILIES = {
    "long_p1": 14,
    "long_pstar": 18,
    "short_w3": 4,
    "short_z3": 6,
    "short_w2": 4,
}
EXPECTED_ACTIVE_PROFILE = {"2": 9, "3": 15, "4": 18}


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
        "path": str(PROOF_PATH.relative_to(ROOT)),
        "scope": "source-bound raw boundary-locality induction only",
        **exact_section_record(PROOF_PATH.read_bytes()),
    }


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def cell_contains(cell: ICell, i: int) -> bool:
    return i >= 0 and (i == cell.value if cell.value is not None else i >= cell.base_i)


def matching_cells(i: int) -> tuple[ICell, ...]:
    return tuple(cell for cell in CELLS if cell_contains(cell, i))


def const_value(exponent: dict[str, Any]) -> int | None:
    return exponent.get("value") if exponent.get("op") == "const" else None


def variable_name(exponent: dict[str, Any]) -> str | None:
    return exponent.get("name") if exponent.get("op") == "var" else None


def affine_i_schema(
    approved: Any,
    normalizer: Any,
    generator: Any,
    schema_id: str,
    factors: list[dict[str, Any]],
    variable: str,
    offset: int,
) -> Any:
    variable_positions = [
        index
        for index, factor in enumerate(factors)
        if variable_name(factor["exponent"]) == variable
    ]
    if len(variable_positions) != 1:
        raise AssertionError((schema_id, variable, variable_positions))
    variable_index = variable_positions[0]
    for index, factor in enumerate(factors):
        if index == variable_index:
            continue
        if const_value(factor["exponent"]) != 1:
            raise AssertionError((schema_id, index, factor["exponent"]))
    words = [generator.parse_raw(factor["word"]) for factor in factors]
    power = words[variable_index]
    _, cyclic, _ = normalizer.cyclic_decomposition(generator, power)
    reference, _ = normalizer.primitive_power(cyclic)
    p_left, p_core, p_multiplier, p_right = (
        normalizer.reference_primitive_decomposition(generator, power, reference)
    )
    left = tuple(letter for word in words[:variable_index] for letter in word)
    right = tuple(letter for word in words[variable_index + 1 :] for letter in word)
    return approved.AffineENSchema(
        schema_id=schema_id,
        source_left=left,
        source_q=(),
        source_middle=(),
        source_p=power,
        source_right=right,
        fixed_0=left,
        q_core=(),
        q_multiplier=0,
        fixed_1=p_left,
        p_core=p_core,
        p_multiplier=p_multiplier,
        fixed_2=(*p_right, *right),
        q_offset=0,
        p_offset=offset,
    )


def label_schema(approved: Any, schema: Any, schema_id: str, action: Word) -> Any:
    return approved.AffineENSchema(
        schema_id=schema_id,
        source_left=(*action, *schema.source_left),
        source_q=schema.source_q,
        source_middle=schema.source_middle,
        source_p=schema.source_p,
        source_right=schema.source_right,
        fixed_0=(*action, *schema.fixed_0),
        q_core=schema.q_core,
        q_multiplier=schema.q_multiplier,
        fixed_1=schema.fixed_1,
        p_core=schema.p_core,
        p_multiplier=schema.p_multiplier,
        fixed_2=schema.fixed_2,
        q_offset=schema.q_offset,
        p_offset=schema.p_offset,
    )


def selected_source_rows(generator: Any) -> list[dict[str, Any]]:
    _, rows = generator.build_w_rows()
    by_id = {row["id"]: row for row in rows}
    selected: list[dict[str, Any]] = []

    def add_row(source: dict[str, Any], family: str, state: str, offset: int, sign: int) -> None:
        selected.append(
            {
                "source": source,
                "family": family,
                "state": state,
                "offset": offset,
                "direction_sign": sign,
            }
        )

    for nu, family in ((1, "long_p1"), (3, "long_pstar")):
        word = generator.BLOCKS[nu - 1][0]
        for position in range(len(word)):
            add_row(by_id[f"W:nu{nu}:P:{position}:o+1"], family, "new_segment", 1, 1)

    short_specs = (
        (4, "short_w3", generator.BLOCKS[2][0]),
        (5, "short_z3", generator.BLOCKS[2][0]),
        (6, "short_w2", generator.BLOCKS[1][1]),
    )
    for nu, family, prefix in short_specs:
        c_word = generator.BLOCKS[nu - 1][1]
        if not c_word.startswith(prefix):
            raise AssertionError((nu, prefix, c_word))
        for position in range(len(prefix), len(c_word)):
            source = by_id[f"W:nu{nu}:C:{position}:o+1"]
            add_row(source, family, "old", 0, -1)
            add_row(source, family, "new", 1, 1)
    return selected


def build_schemas_and_provenance(
    approved: Any,
    normalizer: Any,
    generator: Any,
    actions: dict[int, Word],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    schemas: dict[str, Any] = {}
    provenance: list[dict[str, Any]] = []
    failures: list[str] = []
    selected = selected_source_rows(generator)
    for item in selected:
        source = item["source"]
        source_id = source["id"]
        variable = "h" if source["key"]["block"] == "P" else "i"
        row_id = f"diag:{item['family']}:{item['state']}:{source_id}"
        module_id = f"{row_id}:module"
        try:
            module = affine_i_schema(
                approved,
                normalizer,
                generator,
                module_id,
                source["module_vertex"]["factors"],
                variable,
                item["offset"],
            )
        except Exception as exc:
            failures.append(f"schema:{row_id}:{type(exc).__name__}:{exc}")
            continue
        schemas[module_id] = module
        label_ids: dict[str, str] = {}
        slot = source["key"]["slot"]
        for occurrence in OCCURRENCES_BY_SLOT[slot]:
            label_id = f"{row_id}:label:o{occurrence}"
            schemas[label_id] = label_schema(
                approved, module, label_id, actions[occurrence]
            )
            label_ids[str(occurrence)] = label_id
        provenance.append(
            {
                "id": row_id,
                "source_row_id": source_id,
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
                "integral_coefficient": item["direction_sign"] * source["coefficient"],
                "module_schema": module_id,
                "label_schemas": label_ids,
                "source_binding": "build_w_rows:P(h=i+1) or C-tail(i+delta)",
            }
        )
    provenance.sort(key=lambda row: row["id"])
    return schemas, provenance, failures


def build_templates(
    approved: Any,
    normalizer: Any,
    generator: Any,
    schemas: dict[str, Any],
) -> tuple[dict[tuple[str, str], Any], list[str]]:
    templates: dict[tuple[str, str], Any] = {}
    failures: list[str] = []
    for schema_id, schema in sorted(schemas.items()):
        for cell in CELLS:
            en_cell = approved.ENCell(cell.cell_id, 0, cell.value, 0, cell.base_i)
            try:
                template = approved.build_template_en(
                    normalizer,
                    generator,
                    schema,
                    en_cell,
                )
                direct = approved.direct_schema_vertex(
                    generator, schema, 0, cell.base_i
                )
                if template.base_word != direct:
                    failures.append(f"base_normal_form:{schema_id}:{cell.cell_id}")
                if approved.expand_template_en(template, 0, cell.base_i) != direct:
                    failures.append(f"base_expansion:{schema_id}:{cell.cell_id}")
                if cell.value is None:
                    next_direct = approved.direct_schema_vertex(
                        generator, schema, 0, cell.base_i + 1
                    )
                    if approved.expand_template_en(template, 0, cell.base_i + 1) != next_direct:
                        failures.append(f"next_expansion:{schema_id}:{cell.cell_id}")
                templates[(schema_id, cell.cell_id)] = template
            except Exception as exc:
                failures.append(
                    f"template:{schema_id}:{cell.cell_id}:{type(exc).__name__}:{exc}"
                )
    return templates, failures


def coordinate_id(members: list[dict[str, Any]]) -> str:
    payload = "|".join(sorted(member["id"] for member in members)).encode()
    return f"coord:{hashlib.sha256(payload).hexdigest()[:16]}"


def cell_fibers(
    approved: Any,
    normalizer: Any,
    generator: Any,
    cell: ICell,
    provenance: list[dict[str, Any]],
    templates: dict[tuple[str, str], Any],
) -> tuple[list[dict[str, Any]], list[str], dict[str, int]]:
    failures: list[str] = []
    methods: Counter[str] = Counter()
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for row in provenance:
        template = templates[(row["module_schema"], cell.cell_id)]
        key = (row["slot"], approved.canonical_blocks(normalizer, template))
        grouped.setdefault(key, []).append(row)
    same_slot_checks = 0
    for left_index, left in enumerate(provenance):
        for right in provenance[left_index + 1 :]:
            if left["slot"] != right["slot"]:
                continue
            comparison = approved.compare_templates_en(
                normalizer,
                generator,
                templates[(left["module_schema"], cell.cell_id)],
                templates[(right["module_schema"], cell.cell_id)],
            )
            same_slot_checks += 1
            methods[comparison["method"]] += 1
            same = approved.canonical_blocks(
                normalizer, templates[(left["module_schema"], cell.cell_id)]
            ) == approved.canonical_blocks(
                normalizer, templates[(right["module_schema"], cell.cell_id)]
            )
            if comparison["order"] is None:
                failures.append(
                    f"collision_compare:{cell.cell_id}:{left['id']}:{right['id']}:{comparison['method']}"
                )
            elif (comparison["order"] == 0) != same:
                failures.append(
                    f"collision_equivalence:{cell.cell_id}:{left['id']}:{right['id']}"
                )
    fibers: list[dict[str, Any]] = []
    for members in sorted(
        grouped.values(),
        key=lambda group: (group[0]["slot"], sorted(row["id"] for row in group)),
    ):
        members = sorted(members, key=lambda row: row["id"])
        representative = members[0]
        coefficient = sum(row["integral_coefficient"] for row in members)
        families = sorted({row["family"] for row in members})
        if coefficient % 2 and len(families) != 1:
            failures.append(
                f"cross_family_active_collision:{cell.cell_id}:{coordinate_id(members)}:{families}"
            )
        label_schemas: dict[str, str] = {}
        for occurrence in OCCURRENCES_BY_SLOT[representative["slot"]]:
            representative_label = representative["label_schemas"][str(occurrence)]
            for member in members[1:]:
                member_label = member["label_schemas"][str(occurrence)]
                comparison = approved.compare_templates_en(
                    normalizer,
                    generator,
                    templates[(representative_label, cell.cell_id)],
                    templates[(member_label, cell.cell_id)],
                )
                if comparison["order"] != 0:
                    failures.append(
                        f"collision_label:{cell.cell_id}:{representative['id']}:{member['id']}:o{occurrence}"
                    )
            label_schemas[str(occurrence)] = representative_label
        fibers.append(
            {
                "coordinate_id": coordinate_id(members),
                "slot": representative["slot"],
                "families": families,
                "members": [row["id"] for row in members],
                "integral_coefficient_sum": coefficient,
                "activity_parity": coefficient % 2,
                "module_schema": representative["module_schema"],
                "label_schemas": label_schemas,
            }
        )
    return fibers, failures, {
        "same_slot_pair_checks": same_slot_checks,
        **dict(sorted(methods.items())),
    }


def build_tokens(
    cell: ICell,
    fibers: list[dict[str, Any]],
    templates: dict[tuple[str, str], Any],
    occurrences: dict[int, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    tokens: list[dict[str, Any]] = []
    for fiber in fibers:
        if not fiber["activity_parity"]:
            continue
        for occurrence in OCCURRENCES_BY_SLOT[fiber["slot"]]:
            label_schema = fiber["label_schemas"][str(occurrence)]
            tokens.append(
                {
                    "id": f"{cell.cell_id}:{fiber['coordinate_id']}:o{occurrence}",
                    "coordinate_id": fiber["coordinate_id"],
                    "family": fiber["families"][0] if len(fiber["families"]) == 1 else "+".join(fiber["families"]),
                    "slot": fiber["slot"],
                    "occurrence": occurrence,
                    "polarity": occurrences[occurrence]["polarity"],
                    "module_schema": fiber["module_schema"],
                    "module_template": templates[(fiber["module_schema"], cell.cell_id)],
                    "label_schema": label_schema,
                    "label_template": templates[(label_schema, cell.cell_id)],
                }
            )
    tokens.sort(key=lambda token: token["id"])
    failures: list[str] = []
    keys = [
        (token["occurrence"], token["coordinate_id"])
        for token in tokens
    ]
    if len(keys) != len(set(keys)):
        failures.append(f"duplicate_decorated_coordinate:{cell.cell_id}")
    return tokens, failures


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
    approved: Any,
    residual: Any,
    generator: Any,
    cell: ICell,
    tokens: list[dict[str, Any]],
    schemas: dict[str, Any],
    actions: dict[int, Word],
) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    failures: list[str] = []
    for token in tokens:
        schema = schemas[token["module_schema"]]
        template = token["module_template"]
        action = actions[token["occurrence"]]
        vertex = approved.direct_schema_vertex(generator, schema, 0, cell.base_i)
        base = residual.raw_observable(generator, action, vertex)
        base_record = observable_record(generator, base)
        locality = {
            "all_first_half_noncentral": not any(base[1]),
            "central_strictly_longer": (
                not base[0] or len(base[3]) > max(len(label) for label in base[0])
            ),
            "action_horizon": len(action) + 1,
        }
        pumps: list[dict[str, Any]] = []
        if cell.value is None:
            candidates = [
                (kind, core, affine)
                for kind, core, affine in template.blocks
                if affine is not None and affine[1] > 0
            ]
            if len(candidates) != 1:
                failures.append(f"pump_block:{token['id']}:{len(candidates)}")
            else:
                kind, core, affine = candidates[0]
                split = dict(template.insertion_splits).get(kind)
                if split is None:
                    failures.append(f"pump_split:{token['id']}")
                else:
                    next_vertex = approved.direct_schema_vertex(
                        generator, schema, 0, cell.base_i + 1
                    )
                    next_observable = residual.raw_observable(generator, action, next_vertex)
                    increment = affine[1]
                    saturated_boundary = split + increment * len(core)
                    stable_signature = base[:3] == next_observable[:3]
                    central_slope = len(next_observable[3]) - len(base[3])
                    stable_schema = (
                        approved.expand_template_en(template, 0, cell.base_i) == vertex
                        and approved.expand_template_en(template, 0, cell.base_i + 1)
                        == next_vertex
                    )
                    pump = {
                        "variable": "i",
                        "block": kind,
                        "core": generator.lit(core),
                        "core_length": len(core),
                        "insertion_split": split,
                        "affine_increment": increment,
                        "action_horizon": locality["action_horizon"],
                        "saturated_boundary": saturated_boundary,
                        "horizon_saturated": saturated_boundary > locality["action_horizon"],
                        "base_next_observable_signature_equal": stable_signature,
                        "central_length_slope": central_slope,
                        "stable_schema_equality": stable_schema,
                        "one_step": observable_record(generator, next_observable),
                    }
                    pumps.append(pump)
                    if (
                        not pump["horizon_saturated"]
                        or not stable_signature
                        or central_slope <= 0
                        or not stable_schema
                    ):
                        failures.append(f"pump_guard:{token['id']}")
            if not locality["all_first_half_noncentral"] or not locality["central_strictly_longer"]:
                failures.append(f"raw_locality:{token['id']}")
        records.append(
            {
                "id": f"raw:{token['id']}",
                "token_id": token["id"],
                "coordinate_id": token["coordinate_id"],
                "family": token["family"],
                "slot": token["slot"],
                "occurrence": token["occurrence"],
                "action": generator.lit(action),
                "module_schema": token["module_schema"],
                "base": base_record,
                "locality": locality,
                "pumps": pumps,
                "source_binding": "literal raw_observable + one-increment horizon shield",
            }
        )
    return records, failures


def cell_result(
    approved: Any,
    normalizer: Any,
    residual: Any,
    generator: Any,
    cell: ICell,
    provenance: list[dict[str, Any]],
    schemas: dict[str, Any],
    templates: dict[tuple[str, str], Any],
    occurrences: dict[int, dict[str, Any]],
    actions: dict[int, Word],
) -> dict[str, Any]:
    fibers, fiber_failures, methods = cell_fibers(
        approved, normalizer, generator, cell, provenance, templates
    )
    tokens, token_failures = build_tokens(cell, fibers, templates, occurrences)
    raw, raw_failures = raw_records(
        approved, residual, generator, cell, tokens, schemas, actions
    )
    active = [fiber for fiber in fibers if fiber["activity_parity"]]
    profile = {
        str(slot): sum(fiber["slot"] == slot for fiber in active)
        for slot in (2, 3, 4)
    }
    raw_xor = sum(record["base"]["rho"] for record in raw) % 2
    return {
        "cell": {
            "id": cell.cell_id,
            "i": "ge3" if cell.value is None else cell.value,
            "base_i": cell.base_i,
        },
        "collision": {
            "fibers": fibers,
            "fiber_count": len(fibers),
            "active_coordinate_count": len(active),
            "active_slot_profile": profile,
            "comparison_method_counts": methods,
        },
        "tokens": [
            {
                key: token[key]
                for key in (
                    "id",
                    "coordinate_id",
                    "family",
                    "slot",
                    "occurrence",
                    "polarity",
                    "module_schema",
                    "label_schema",
                )
            }
            for token in tokens
        ],
        "raw_records": raw,
        "computed": {
            "L_slot_zero": 0,
            "L_nonzero": raw_xor,
            "raw_observable_count": len(raw),
            "status": "provisional_pending_independent_replay_and_sol_review",
        },
        "generation_failures": [*fiber_failures, *token_failures, *raw_failures],
    }


def coordinate_catalog(cells: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    failures: list[str] = []
    partitions: list[dict[str, dict[str, Any]]] = []
    for result in cells:
        partitions.append(
            {
                fiber["coordinate_id"]: fiber
                for fiber in result["collision"]["fibers"]
                if fiber["activity_parity"]
            }
        )
    baseline = partitions[0] if partitions else {}
    baseline_shape = {
        coordinate_id: (
            fiber["slot"],
            tuple(fiber["families"]),
            tuple(fiber["members"]),
        )
        for coordinate_id, fiber in baseline.items()
    }
    for index, partition in enumerate(partitions[1:], start=1):
        shape = {
            coordinate_id: (
                fiber["slot"],
                tuple(fiber["families"]),
                tuple(fiber["members"]),
            )
            for coordinate_id, fiber in partition.items()
        }
        if shape != baseline_shape:
            failures.append(f"unstable_coordinate_partition:{cells[index]['cell']['id']}")
    catalog = [
        {
            "coordinate_id": coordinate_id,
            "slot": fiber["slot"],
            "family": fiber["families"][0] if len(fiber["families"]) == 1 else "+".join(fiber["families"]),
            "members": fiber["members"],
            "integral_coefficient_sum": fiber["integral_coefficient_sum"],
            "module_schema": fiber["module_schema"],
        }
        for coordinate_id, fiber in sorted(baseline.items())
    ]
    return catalog, failures


def source_bindings() -> dict[str, Any]:
    return {
        "generator": {
            "path": str(GENERATOR_PATH.relative_to(ROOT)),
            "functions": ["build_w_rows", "trace_ast"],
            "selection": (
                "P rows nu=1,3 at h=i+1; C-tail rows nu=4,5,6 at i and i+1 "
                "with signed new-minus-old provenance"
            ),
            "sha256": sha256_path(GENERATOR_PATH),
        },
        "approved_helpers": {
            "path": str(APPROVED_PATH.relative_to(ROOT)),
            "functions": [
                "AffineENSchema",
                "build_template_en",
                "compare_templates_en",
                "direct_schema_vertex",
            ],
            "sha256": sha256_path(APPROVED_PATH),
        },
        "normalizer": {
            "path": str(NORMALIZER_PATH.relative_to(ROOT)),
            "functions": [
                "reference_primitive_decomposition",
                "intact_boundary",
                "normalize_blocks",
            ],
            "sha256": sha256_path(NORMALIZER_PATH),
        },
        "raw": {
            "path": str(RAW_PATH.relative_to(ROOT)),
            "function": "raw_observable",
            "sha256": sha256_path(RAW_PATH),
            "locality_lemma": (
                "For A R^(k t) B, once one affine increment has split + increment*core_length "
                "beyond the finite action horizon, exact base/next observable signatures "
                "(first-half labels, equality bits, and rho) agree, "
                "central length has positive slope, and the affine schema replay is stable, "
                "later insertions cannot change the horizon prefix."
            ),
        },
        "theory": theory_section_binding(),
        "checker": {
            "path": str(CHECKER_PATH.relative_to(ROOT)),
            "sha256": sha256_path(CHECKER_PATH),
        },
        "tests": {
            "path": str(TEST_PATH.relative_to(ROOT)),
            "sha256": sha256_path(TEST_PATH),
        },
    }


def build_manifest() -> dict[str, Any]:
    approved = load_module("diag_approved_inverse_checker", APPROVED_PATH)
    normalizer = load_module("diag_pure_p_normalizer", NORMALIZER_PATH)
    residual = load_module("diag_pure_p_raw", RAW_PATH)
    generator = normalizer.load_raw_generator()
    occurrences = {item["order"]: item for item in generator.trace_ast()[1]}
    actions = {
        order: generator.parse_raw(item["quotient_prefix"])
        for order, item in occurrences.items()
    }
    schemas, provenance, schema_failures = build_schemas_and_provenance(
        approved, normalizer, generator, actions
    )
    templates, template_failures = build_templates(
        approved, normalizer, generator, schemas
    )
    cells = [
        cell_result(
            approved,
            normalizer,
            residual,
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
    catalog, catalog_failures = coordinate_catalog(cells)
    all_failures = [
        *schema_failures,
        *template_failures,
        *catalog_failures,
        *(failure for result in cells for failure in result["generation_failures"]),
    ]
    return {
        "format": "period-two-diagonal-pure-p-raw-provisional-v1",
        "scope": {
            "parameter": "i>=0, cells 0,1,2,>=3",
            "increment": "p_i^Delta=A_(i+1,i+1)+A_(i,i)",
            "computed_target": "L_nonzero(p_i^Delta)",
            "status": "provisional_pending_independent_replay_and_sol_review",
            "nonclaim": (
                "Computed raw xors are not hardcoded theorem values. This artifact proves no "
                "old-new, Q, diagonal, period-two, AK3, stable-AC, or AC claim."
            ),
        },
        "source_bindings": source_bindings(),
        "raw_parser_guard": approved.raw_parser_guard(generator),
        "cells": [
            {"id": cell.cell_id, "i": "ge3" if cell.value is None else cell.value, "base_i": cell.base_i}
            for cell in CELLS
        ],
        "five_family_traversal_inventory": dict(EXPECTED_TRAVERSAL_FAMILIES),
        "provenance": provenance,
        "schemas": [approved.schema_record(generator, schema) for schema in schemas.values()],
        "coordinate_schemas": catalog,
        "cell_results": cells,
        "generation_failures": all_failures,
    }


def binding_paths() -> dict[str, Path]:
    return {
        "generator": GENERATOR_PATH,
        "approved_helpers": APPROVED_PATH,
        "normalizer": NORMALIZER_PATH,
        "raw": RAW_PATH,
        "checker": CHECKER_PATH,
        "tests": TEST_PATH,
    }


def verification_failures(
    manifest: dict[str, Any],
    expected: dict[str, Any] | None = None,
) -> list[str]:
    failures: list[str] = []
    try:
        if manifest["format"] != "period-two-diagonal-pure-p-raw-provisional-v1":
            failures.append("format")
        if manifest["scope"]["status"] != "provisional_pending_independent_replay_and_sol_review":
            failures.append("status")
        if manifest["generation_failures"]:
            failures.append("generation_failures")
        if manifest["raw_parser_guard"] != {
            "raw_p": "tc",
            "raw_p_inverse": "cT",
            "module_parser_p": "t",
        }:
            failures.append("raw_parser_guard")
        if [cell["id"] for cell in manifest["cells"]] != [cell.cell_id for cell in CELLS]:
            failures.append("cell_catalog")
        if any(len(matching_cells(i)) != 1 for i in range(12)):
            failures.append("cell_coverage")
        if manifest["five_family_traversal_inventory"] != EXPECTED_TRAVERSAL_FAMILIES:
            failures.append("five_family_inventory")
        provenance = manifest["provenance"]
        provenance_by_id = {row["id"]: row for row in provenance}
        if len(provenance) != 46 or len(provenance_by_id) != 46:
            failures.append("provenance_count")
        family_counts = Counter(row["family"] for row in provenance)
        if dict(family_counts) != EXPECTED_TRAVERSAL_FAMILIES:
            failures.append("provenance_family_profile")
        catalog = manifest["coordinate_schemas"]
        coordinate_by_id = {row["coordinate_id"]: row for row in catalog}
        if len(catalog) != 42 or len(coordinate_by_id) != 42:
            failures.append("coordinate_schema_count")
        catalog_profile = {
            str(slot): sum(row["slot"] == slot for row in catalog)
            for slot in (2, 3, 4)
        }
        if catalog_profile != EXPECTED_ACTIVE_PROFILE:
            failures.append("coordinate_schema_profile")
        if {row["family"] for row in catalog} != set(EXPECTED_TRAVERSAL_FAMILIES):
            failures.append("coordinate_schema_families")
        for name, path in binding_paths().items():
            if manifest["source_bindings"][name]["sha256"] != sha256_path(path):
                failures.append(f"source_hash:{name}")
        if manifest["source_bindings"].get("theory") != theory_section_binding():
            failures.append("source_section:theory")
        for result in manifest["cell_results"]:
            cell_id = result["cell"]["id"]
            fibers = result["collision"]["fibers"]
            members = [member for fiber in fibers for member in fiber["members"]]
            if sorted(members) != sorted(provenance_by_id):
                failures.append(f"collision_partition:{cell_id}")
            for fiber in fibers:
                coefficient = sum(
                    provenance_by_id[member]["integral_coefficient"]
                    for member in fiber["members"]
                )
                if coefficient != fiber["integral_coefficient_sum"]:
                    failures.append(f"collision_coefficient:{cell_id}:{fiber['coordinate_id']}")
                if coefficient % 2 != fiber["activity_parity"]:
                    failures.append(f"collision_parity:{cell_id}:{fiber['coordinate_id']}")
            if result["collision"]["active_coordinate_count"] != 42:
                failures.append(f"active_coordinate_count:{cell_id}")
            if result["collision"]["active_slot_profile"] != EXPECTED_ACTIVE_PROFILE:
                failures.append(f"active_slot_profile:{cell_id}")
            tokens = result["tokens"]
            token_by_id = {token["id"]: token for token in tokens}
            if len(tokens) != 84 or len(token_by_id) != 84:
                failures.append(f"token_count:{cell_id}")
            token_profile = {
                str(slot): sum(token["slot"] == slot for token in tokens) // 2
                for slot in (2, 3, 4)
            }
            if token_profile != EXPECTED_ACTIVE_PROFILE:
                failures.append(f"token_profile:{cell_id}")
            raw = result["raw_records"]
            if len(raw) != 84 or len({row["token_id"] for row in raw}) != 84:
                failures.append(f"raw_count:{cell_id}")
            unbounded = cell_id == "e0_nge3"
            for record in raw:
                token = token_by_id.get(record["token_id"])
                if (
                    token is None
                    or token["coordinate_id"] != record["coordinate_id"]
                    or token["occurrence"] != record["occurrence"]
                    or token["slot"] != record["slot"]
                ):
                    failures.append(f"raw_binding:{cell_id}:{record['id']}")
                expected_rho = sum(not value for value in record["base"]["equalities"]) % 2
                if expected_rho != record["base"]["rho"]:
                    failures.append(f"raw_bit:{cell_id}:{record['id']}")
                if len(record["pumps"]) != (1 if unbounded else 0):
                    failures.append(f"pump_count:{cell_id}:{record['id']}")
                for pump in record["pumps"]:
                    expected_boundary = (
                        pump["insertion_split"]
                        + pump["affine_increment"] * pump["core_length"]
                    )
                    expected_signature_equal = all(
                        record["base"][field] == pump["one_step"][field]
                        for field in ("first_half_labels", "equalities", "rho")
                    )
                    expected_slope = (
                        pump["one_step"]["central_length"]
                        - record["base"]["central_length"]
                    )
                    if (
                        pump["core_length"] != len(pump["core"])
                        or pump["affine_increment"] <= 0
                        or pump["action_horizon"] != record["locality"]["action_horizon"]
                        or pump["saturated_boundary"] != expected_boundary
                        or pump["horizon_saturated"]
                        != (expected_boundary > pump["action_horizon"])
                        or not pump["horizon_saturated"]
                        or pump["base_next_observable_signature_equal"] != expected_signature_equal
                        or not expected_signature_equal
                        or pump["central_length_slope"] != expected_slope
                        or expected_slope <= 0
                        or not pump["stable_schema_equality"]
                    ):
                        failures.append(f"pump:{cell_id}:{record['id']}")
            raw_xor = sum(record["base"]["rho"] for record in raw) % 2
            if result["computed"]["L_nonzero"] != raw_xor:
                failures.append(f"cell_xor:{cell_id}")
            if result["computed"]["raw_observable_count"] != 84:
                failures.append(f"computed_raw_count:{cell_id}")
            if result["computed"]["L_slot_zero"] != 0:
                failures.append(f"slot_zero:{cell_id}")
        recomputed = build_manifest() if expected is None else expected
        if canonical_json(manifest) != canonical_json(recomputed):
            failures.append("recomputed_manifest_mismatch")
    except Exception as exc:
        failures.append(f"manifest_shape:{type(exc).__name__}:{exc}")
    return failures


def verify_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    failures = verification_failures(manifest)
    if failures:
        raise AssertionError(failures[:24])
    return manifest


def write_manifest() -> dict[str, Any]:
    manifest = verify_manifest(build_manifest())
    MANIFEST_PATH.write_bytes(canonical_json(manifest))
    return manifest


def check_manifest() -> dict[str, Any]:
    manifest = verify_manifest(build_manifest())
    if MANIFEST_PATH.read_bytes() != canonical_json(manifest):
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
        "status": manifest["scope"]["status"],
        "generation_failures": len(manifest["generation_failures"]),
        "coordinate_schemas": len(manifest["coordinate_schemas"]),
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
        manifest = verify_manifest(build_manifest())
    print(json.dumps(summary(manifest), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
