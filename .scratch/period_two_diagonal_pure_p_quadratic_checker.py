#!/usr/bin/env python3
"""[unverified] Provisional 48-chord certificate for diagonal pure-P Q.

This artifact computes, but does not prescribe, Q(q_i) for
q_i=A_(i+1,i+1)+A_(i,i).  It reuses the approved collision schemas from the
diagonal raw checker, constructs the deterministic 48-chord matching from
the seven surviving path pieces, proves the all-power within-slot ranks by
39 adjacent comparisons in each cell, and evaluates Q only by the prefix
sweep in AK3_PURE_P_INCREMENT_NORMAL_FORM.md (7.6)--(7.7).  Status remains
provisional until guarded execution, independent replay, and Sol review.
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
TEST_PATH = ROOT / ".scratch/test_period_two_diagonal_pure_p_quadratic_checker.py"
RAW_CHECKER_PATH = ROOT / ".scratch/period_two_diagonal_pure_p_raw_checker.py"
RAW_MANIFEST_PATH = ROOT / ".scratch/period_two_diagonal_pure_p_raw_manifest.json"
APPROVED_PATH = ROOT / ".scratch/period_two_inverse_pure_increment_checker.py"
NORMALIZER_PATH = ROOT / ".scratch/period_two_inverse_q_companion_checker.py"
GENERATOR_PATH = ROOT / ".scratch/period_two_raw_stream_manifest_generator.py"
DIRECT_PATH = ROOT / ".scratch/period_two_seven_family_covariance_checker.py"
THEORY_PATH = ROOT / "literature/proofs/AK3_PURE_P_INCREMENT_NORMAL_FORM.md"
MANIFEST_PATH = ROOT / ".scratch/period_two_diagonal_pure_p_quadratic_manifest.json"

SLOT_ZERO_OCCURRENCES = (3, 4, 7, 8, 11, 12)
OCCURRENCES_BY_SLOT = {2: (1, 6), 3: (9, 14), 4: (15, 16)}
ACTIVE_OCCURRENCES = (1, 3, 4, 6, 7, 8, 9, 11, 12, 14, 15, 16)
EXPECTED_PROFILE = {2: 9, 3: 15, 4: 18}
EXPECTED_POLARITY = {
    1: 1, 3: 1, 4: -1, 6: -1, 7: 1, 8: -1,
    9: 1, 11: 1, 12: -1, 14: -1, 15: 1, 16: -1,
}
EXPECTED_BOUNDARY_TYPES = Counter({
    (1, 3): 1, (3, 15): 1, (4, 9): 2, (6, 11): 1,
    (6, 7): 1, (9, 11): 1, (7, 9): 1, (8, 9): 2,
    (12, 15): 2,
})
EXPECTED_ADJACENCY_TYPES = Counter({
    (1, 16): 4, (6, 9): 4, (14, 16): 11, (9, 15): 4,
    (9, 14): 1, (1, 15): 3, (1, 6): 1, (6, 15): 2,
    (15, 16): 3, (14, 15): 3,
})
REPEATED_LABEL_PAIR = (
    "residual_b:boundary:right",
    "new_component3:junction",
)


@dataclass(frozen=True)
class EndpointSpec:
    kind: str
    delta: int | None = None
    occurrence: int | None = None
    member_id: str | None = None
    endpoint: str | None = None


@dataclass(frozen=True)
class ChordSpec:
    chord_id: str
    kind: str
    left: EndpointSpec
    right: EndpointSpec


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def shortlex(word: tuple[int, ...]) -> tuple[int, tuple[int, ...]]:
    return len(word), word


def boundary(delta: int, occurrence: int) -> EndpointSpec:
    return EndpointSpec("slot0", delta=delta, occurrence=occurrence)


def edge(member_id: str, endpoint: str) -> EndpointSpec:
    if endpoint not in ("pre", "post"):
        raise ValueError(endpoint)
    return EndpointSpec("edge", member_id=member_id, endpoint=endpoint)


def provenance_id(family: str, state: str, source_id: str) -> str:
    return f"diag:{family}:{state}:{source_id}"


def long_id(nu: int, family: str, position: int) -> str:
    return provenance_id(
        family, "new_segment", f"W:nu{nu}:P:{position}:o+1"
    )


def short_id(nu: int, family: str, state: str, position: int) -> str:
    return provenance_id(family, state, f"W:nu{nu}:C:{position}:o+1")


def path_chords(
    name: str,
    members: list[str],
    left_boundary: EndpointSpec,
    right_boundary: EndpointSpec,
) -> list[ChordSpec]:
    if not members:
        raise AssertionError(name)
    rows = [
        ChordSpec(
            f"{name}:boundary:left",
            "boundary",
            left_boundary,
            edge(members[0], "pre"),
        )
    ]
    rows.extend(
        ChordSpec(
            f"{name}:adjacency:{index}",
            "adjacency",
            edge(members[index - 1], "post"),
            edge(members[index], "pre"),
        )
        for index in range(1, len(members))
    )
    rows.append(
        ChordSpec(
            f"{name}:boundary:right",
            "boundary",
            edge(members[-1], "post"),
            right_boundary,
        )
    )
    return rows


def topology_catalog() -> list[ChordSpec]:
    p1 = [long_id(1, "long_p1", position) for position in range(14)]
    pstar = [long_id(3, "long_pstar", position) for position in range(2, 18)]
    old_z = [short_id(5, "short_z3", "old", 18 + position) for position in range(3)]
    new_z = [short_id(5, "short_z3", "new", 18 + position) for position in range(3)]
    new_w = [short_id(4, "short_w3", "new", 18 + position) for position in range(2)]
    old_u = [short_id(6, "short_w2", "old", 19 + position) for position in range(2)]
    new_u = [short_id(6, "short_w2", "new", 19 + position) for position in range(2)]

    rows: list[ChordSpec] = []
    rows.extend(path_chords("terminal_p1", p1, boundary(0, 3), boundary(1, 3)))
    rows.extend(path_chords("old_component2_w", old_u, boundary(0, 12), boundary(0, 8)))
    rows.extend(path_chords("new_component2_w", new_u, boundary(1, 12), boundary(1, 8)))
    rows.extend(path_chords("old_component3_z", old_z, boundary(0, 11), boundary(0, 4)))
    rows.extend(path_chords("residual_b", pstar, boundary(0, 7), boundary(1, 11)))

    rows.extend(
        ChordSpec(
            f"new_component3_w:adjacency:{index}",
            "adjacency",
            edge(new_w[index - 1], "post"),
            edge(new_w[index], "pre"),
        )
        for index in range(1, len(new_w))
    )
    rows.append(
        ChordSpec(
            "new_component3_w:boundary:right",
            "boundary",
            edge(new_w[-1], "post"),
            boundary(1, 7),
        )
    )
    rows.extend(
        ChordSpec(
            f"new_component3_z:adjacency:{index}",
            "adjacency",
            edge(new_z[index - 1], "post"),
            edge(new_z[index], "pre"),
        )
        for index in range(1, len(new_z))
    )
    rows.append(
        ChordSpec(
            "new_component3_z:boundary:right",
            "boundary",
            edge(new_z[-1], "post"),
            boundary(1, 4),
        )
    )
    rows.append(
        ChordSpec(
            "new_component3:junction",
            "adjacency",
            edge(new_w[0], "pre"),
            edge(new_z[0], "pre"),
        )
    )
    if len(rows) != 48:
        raise AssertionError(len(rows))
    if Counter(row.kind for row in rows) != Counter({"boundary": 12, "adjacency": 36}):
        raise AssertionError(Counter(row.kind for row in rows))
    return rows


def endpoint_occurrence(actual_letter: str, endpoint: str) -> int:
    table = {
        "B": {"pre": 1, "post": 6},
        "b": {"pre": 6, "post": 1},
        "G": {"pre": 14, "post": 9},
        "g": {"pre": 9, "post": 14},
        "A": {"pre": 16, "post": 15},
        "a": {"pre": 15, "post": 16},
    }
    try:
        return table[actual_letter][endpoint]
    except KeyError as exc:
        raise AssertionError((actual_letter, endpoint)) from exc


def slot_zero_schemas(
    raw: Any,
    approved: Any,
    normalizer: Any,
    generator: Any,
    actions: dict[int, tuple[int, ...]],
) -> dict[str, Any]:
    gamma_inverse = generator.lift.quotient_inverse(
        generator.eval_path(generator.BLOCKS[0][2])
    )
    p_inverse = generator.lift.quotient_inverse(generator.parse_raw("tc"))
    factors = [
        {"word": generator.lit(p_inverse), "exponent": {"op": "const", "value": 1}},
        {"word": "c", "exponent": {"op": "const", "value": 1}},
        {"word": generator.lit(gamma_inverse), "exponent": {"op": "var", "name": "i"}},
        {"word": "t", "exponent": {"op": "const", "value": 1}},
    ]
    schemas: dict[str, Any] = {}
    for delta, offset in ((0, 1), (1, 2)):
        module_id = f"quadratic:slot0:delta{delta}:module"
        module = raw.affine_i_schema(
            approved, normalizer, generator, module_id, factors, "i", offset
        )
        schemas[module_id] = module
        for occurrence in SLOT_ZERO_OCCURRENCES:
            label_id = f"quadratic:slot0:delta{delta}:label:o{occurrence}"
            schemas[label_id] = raw.label_schema(
                approved, module, label_id, actions[occurrence]
            )
    return schemas


def common_phase_schemas(
    approved: Any,
    normalizer: Any,
    generator: Any,
    schemas: dict[str, Any],
) -> tuple[dict[str, Any], tuple[int, ...]]:
    seed_id = next(
        schema_id
        for schema_id in sorted(schemas)
        if schema_id.startswith("diag:long_p1:") and schema_id.endswith(":module")
    )
    seed = schemas[seed_id]
    _, cyclic, _ = normalizer.cyclic_decomposition(generator, seed.source_p)
    reference, _ = normalizer.primitive_power(cyclic)
    rephased: dict[str, Any] = {}
    for schema_id, schema in schemas.items():
        if schema.source_q or schema.source_middle or not schema.source_p:
            raise AssertionError((schema_id, "unexpected_schema_shape"))
        p_left, p_core, p_multiplier, p_right = (
            normalizer.reference_primitive_decomposition(
                generator, schema.source_p, reference
            )
        )
        rephased[schema_id] = approved.AffineENSchema(
            schema_id=schema.schema_id,
            source_left=schema.source_left,
            source_q=schema.source_q,
            source_middle=schema.source_middle,
            source_p=schema.source_p,
            source_right=schema.source_right,
            fixed_0=schema.source_left,
            q_core=(),
            q_multiplier=0,
            fixed_1=p_left,
            p_core=p_core,
            p_multiplier=p_multiplier,
            fixed_2=(*p_right, *schema.source_right),
            q_offset=schema.q_offset,
            p_offset=schema.p_offset,
        )
    return rephased, reference


def raw_manifest_structure() -> dict[str, Any]:
    manifest = json.loads(RAW_MANIFEST_PATH.read_text())
    if manifest.get("format") != "period-two-diagonal-pure-p-raw-provisional-v1":
        raise AssertionError("raw manifest format")
    if manifest.get("generation_failures"):
        raise AssertionError("raw manifest failures")
    if len(manifest.get("coordinate_schemas", ())) != 42:
        raise AssertionError("raw manifest coordinate count")
    if [cell.get("id") for cell in manifest.get("cells", ())] != [
        "e0_n0", "e0_n1", "e0_n2", "e0_nge3"
    ]:
        raise AssertionError("raw manifest cells")
    for result in manifest.get("cell_results", ()):
        if result["collision"]["active_slot_profile"] != {"2": 9, "3": 15, "4": 18}:
            raise AssertionError("raw manifest profile")
    return manifest


def build_runtime() -> dict[str, Any]:
    raw = load_module("diag_q_raw_checker", RAW_CHECKER_PATH)
    approved = load_module("diag_q_approved", APPROVED_PATH)
    normalizer = load_module("diag_q_normalizer", NORMALIZER_PATH)
    direct = load_module("diag_q_direct", DIRECT_PATH)
    generator = normalizer.load_raw_generator()
    occurrences = {row["order"]: row for row in generator.trace_ast()[1]}
    actions = {
        order: generator.parse_raw(row["quotient_prefix"])
        for order, row in occurrences.items()
    }
    schemas, provenance, schema_failures = raw.build_schemas_and_provenance(
        approved, normalizer, generator, actions
    )
    zero = slot_zero_schemas(raw, approved, normalizer, generator, actions)
    schemas.update(zero)
    schemas, common_reference = common_phase_schemas(
        approved, normalizer, generator, schemas
    )
    templates, template_failures = raw.build_templates(
        approved, normalizer, generator, schemas
    )
    return {
        "raw": raw,
        "approved": approved,
        "normalizer": normalizer,
        "direct": direct,
        "generator": generator,
        "occurrences": occurrences,
        "actions": actions,
        "schemas": schemas,
        "common_primitive_reference": common_reference,
        "templates": templates,
        "provenance": provenance,
        "failures": [*schema_failures, *template_failures],
    }


def cell_runtime(runtime: dict[str, Any], cell: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    raw = runtime["raw"]
    fibers, fiber_failures, _ = raw.cell_fibers(
        runtime["approved"], runtime["normalizer"], runtime["generator"],
        cell, runtime["provenance"], runtime["templates"],
    )
    path_tokens, token_failures = raw.build_tokens(
        cell, fibers, runtime["templates"], runtime["occurrences"]
    )
    tokens = list(path_tokens)
    for delta in (0, 1):
        for occurrence in SLOT_ZERO_OCCURRENCES:
            module_id = f"quadratic:slot0:delta{delta}:module"
            label_id = f"quadratic:slot0:delta{delta}:label:o{occurrence}"
            tokens.append({
                "id": f"{cell.cell_id}:slot0:delta{delta}:o{occurrence}",
                "coordinate_id": f"slot0:delta{delta}",
                "family": "slot0",
                "slot": 0,
                "occurrence": occurrence,
                "polarity": runtime["occurrences"][occurrence]["polarity"],
                "module_schema": module_id,
                "module_template": runtime["templates"][(module_id, cell.cell_id)],
                "label_schema": label_id,
                "label_template": runtime["templates"][(label_id, cell.cell_id)],
            })
    tokens.sort(key=lambda row: row["id"])
    active = [fiber for fiber in fibers if fiber["activity_parity"]]
    return tokens, active, [*fiber_failures, *token_failures]


def ranked_slots(runtime: dict[str, Any], cell: Any, fibers: list[dict[str, Any]]) -> tuple[dict[int, list[str]], list[dict[str, Any]], list[str]]:
    approved = runtime["approved"]
    normalizer = runtime["normalizer"]
    generator = runtime["generator"]
    templates = runtime["templates"]
    failures: list[str] = []
    ordered: dict[int, list[str]] = {}
    witnesses: list[dict[str, Any]] = []
    for slot, expected in EXPECTED_PROFILE.items():
        rows = [fiber for fiber in fibers if fiber["slot"] == slot]
        rows.sort(key=lambda fiber: shortlex(templates[(fiber["module_schema"], cell.cell_id)].base_word))
        ordered[slot] = [fiber["coordinate_id"] for fiber in rows]
        if len(rows) != expected:
            failures.append(f"rank_size:{cell.cell_id}:s{slot}:{len(rows)}")
        for rank, (left, right) in enumerate(zip(rows, rows[1:])):
            comparison = approved.compare_templates_en(
                normalizer,
                generator,
                templates[(left["module_schema"], cell.cell_id)],
                templates[(right["module_schema"], cell.cell_id)],
            )
            witnesses.append({
                "id": f"rank:s{slot}:{rank}",
                "slot": slot,
                "left_coordinate": left["coordinate_id"],
                "right_coordinate": right["coordinate_id"],
                "comparison": comparison,
                "common_phase": comparison.get("order") == -1,
            })
            if comparison.get("order") != -1:
                failures.append(
                    f"adjacent_rank:{cell.cell_id}:s{slot}:{rank}:{comparison.get('method')}"
                )
    if len(witnesses) != 39:
        failures.append(f"adjacent_witness_count:{cell.cell_id}:{len(witnesses)}")
    return ordered, witnesses, failures


def slot_zero_order(runtime: dict[str, Any], cell: Any) -> tuple[dict[str, Any], list[str]]:
    templates = runtime["templates"]
    comparison = runtime["approved"].compare_templates_en(
        runtime["normalizer"], runtime["generator"],
        templates[("quadratic:slot0:delta0:module", cell.cell_id)],
        templates[("quadratic:slot0:delta1:module", cell.cell_id)],
    )
    failures = [] if comparison.get("order") == -1 else [
        f"slot_zero_order:{cell.cell_id}:{comparison.get('method')}"
    ]
    return {
        "left": "slot0:delta0",
        "right": "slot0:delta1",
        "comparison": comparison,
        "old_before_new": comparison.get("order") == -1,
    }, failures


def chronology_positions(
    tokens: list[dict[str, Any]],
    ranked: dict[int, list[str]],
    zero_order: dict[str, Any],
) -> tuple[dict[str, int], list[str]]:
    failures: list[str] = []
    by_occurrence: dict[int, list[dict[str, Any]]] = {}
    for token in tokens:
        by_occurrence.setdefault(token["occurrence"], []).append(token)
    positions: dict[str, int] = {}
    cursor = 0
    for occurrence in ACTIVE_OCCURRENCES:
        block = by_occurrence.get(occurrence, [])
        polarity = block[0]["polarity"] if block else None
        if occurrence in SLOT_ZERO_OCCURRENCES:
            positive = ["slot0:delta0", "slot0:delta1"]
            if not zero_order["old_before_new"]:
                failures.append(f"slot_zero_unranked:o{occurrence}")
            coordinates = positive if polarity == 1 else list(reversed(positive))
        else:
            slot = next((slot for slot, pair in OCCURRENCES_BY_SLOT.items() if occurrence in pair), None)
            if slot is None:
                failures.append(f"unknown_occurrence:{occurrence}")
                continue
            positive = ranked[slot]
            coordinates = positive if polarity == 1 else list(reversed(positive))
        token_map = {token["coordinate_id"]: token for token in block}
        if set(coordinates) != set(token_map):
            failures.append(f"chronology_block:{occurrence}")
            continue
        for rank, coordinate_id in enumerate(coordinates):
            positions[token_map[coordinate_id]["id"]] = cursor + rank
        cursor += len(coordinates)
    if cursor != 96 or len(positions) != 96:
        failures.append(f"chronology_size:{cursor}:{len(positions)}")
    return positions, failures


def resolve_chords(
    runtime: dict[str, Any],
    cell: Any,
    tokens: list[dict[str, Any]],
    fibers: list[dict[str, Any]],
    positions: dict[str, int],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    failures: list[str] = []
    token_by_coordinate_occurrence = {
        (token["coordinate_id"], token["occurrence"]): token for token in tokens
    }
    token_by_id = {token["id"]: token for token in tokens}
    member_to_coordinate: dict[str, str] = {}
    for fiber in fibers:
        for member in fiber["members"]:
            if member in member_to_coordinate:
                failures.append(f"member_duplicate:{cell.cell_id}:{member}")
            member_to_coordinate[member] = fiber["coordinate_id"]
    provenance = {row["id"]: row for row in runtime["provenance"]}

    def resolve(spec: EndpointSpec) -> dict[str, Any]:
        if spec.kind == "slot0":
            token_id = f"{cell.cell_id}:slot0:delta{spec.delta}:o{spec.occurrence}"
            token = token_by_id[token_id]
            return token
        if spec.member_id not in member_to_coordinate:
            raise AssertionError(f"inactive or unknown member {spec.member_id}")
        source = provenance[spec.member_id]
        occurrence = endpoint_occurrence(source["actual_letter"], str(spec.endpoint))
        return token_by_coordinate_occurrence[(member_to_coordinate[spec.member_id], occurrence)]

    rows: list[dict[str, Any]] = []
    representative_templates: dict[str, Any] = {}
    for spec in topology_catalog():
        left = resolve(spec.left)
        right = resolve(spec.right)
        comparison = runtime["approved"].compare_templates_en(
            runtime["normalizer"], runtime["generator"],
            left["label_template"], right["label_template"],
        )
        label_equal = (
            runtime["approved"].canonical_blocks(runtime["normalizer"], left["label_template"])
            == runtime["approved"].canonical_blocks(runtime["normalizer"], right["label_template"])
        )
        if comparison.get("order") != 0 or not label_equal:
            failures.append(f"chord_label:{cell.cell_id}:{spec.chord_id}:{comparison.get('method')}")
        endpoints = [left, right]
        endpoint_positions = sorted(positions[token["id"]] for token in endpoints)
        rows.append({
            "id": spec.chord_id,
            "kind": spec.kind,
            "endpoint_ids": [left["id"], right["id"]],
            "endpoint_coordinates": [left["coordinate_id"], right["coordinate_id"]],
            "endpoint_occurrences": [left["occurrence"], right["occurrence"]],
            "occurrence_type": sorted([left["occurrence"], right["occurrence"]]),
            "positions": endpoint_positions,
            "endpoint_label_equal": label_equal,
            "endpoint_label_comparison": comparison,
        })
        representative_templates[spec.chord_id] = left["label_template"]

    repeated: list[dict[str, Any]] = []
    equal_pairs: list[tuple[str, str]] = []
    for left_index, left in enumerate(rows):
        for right in rows[left_index + 1 :]:
            same = (
                runtime["approved"].canonical_blocks(
                    runtime["normalizer"], representative_templates[left["id"]]
                )
                == runtime["approved"].canonical_blocks(
                    runtime["normalizer"], representative_templates[right["id"]]
                )
            )
            if not same:
                continue
            pair = tuple(sorted((left["id"], right["id"])))
            equal_pairs.append(pair)
            l0, l1 = left["positions"]
            r0, r1 = right["positions"]
            nested = (l0 < r0 < r1 < l1) or (r0 < l0 < l1 < r1)
            repeated.append({
                "chords": list(pair),
                "same_label": True,
                "nested": nested,
                "positions": [left["positions"], right["positions"]],
            })
    expected_pair = tuple(sorted(REPEATED_LABEL_PAIR))
    if equal_pairs != [expected_pair]:
        failures.append(f"repeated_labels:{cell.cell_id}:{equal_pairs}")
    if len(repeated) != 1 or not repeated[0]["nested"]:
        failures.append(f"repeated_label_nesting:{cell.cell_id}")
    return rows, repeated, failures


def prefix_sweep(chords: list[dict[str, Any]]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for index, chord in enumerate(chords):
        left, right = chord["positions"]
        inside: list[str] = []
        integer_count = 0
        for prior in chords[:index]:
            hits = sum(left < endpoint < right for endpoint in prior["positions"])
            integer_count += hits
            if hits:
                inside.extend([prior["id"]] * hits)
        records.append({
            "chord_id": chord["id"],
            "open_interval": [left, right],
            "prior_endpoint_hits": inside,
            "integer_count": integer_count,
            "lambda": integer_count % 2,
        })
    return {
        "rows": records,
        "lambda_count": len(records),
        "lambda_sum": sum(row["lambda"] for row in records),
        "Q": sum(row["lambda"] for row in records) % 2,
    }


def direct_replay(
    runtime: dict[str, Any],
    cell: Any,
    tokens: list[dict[str, Any]],
    prefix_q: int,
) -> dict[str, Any]:
    direct = runtime["direct"]
    generator = runtime["generator"]
    left = direct.anchored_direction(cell.base_i, cell.base_i)
    right = direct.anchored_direction(cell.base_i + 1, cell.base_i + 1)
    increment = direct.add_directions(right, direct.negate(left))
    replay_tokens = direct.correction_tokens(
        increment, f"diag_q_replay:{cell.cell_id}", compute_raw=False
    )
    replay_by_key = {
        (token.occurrence, token.module_vertex): token for token in replay_tokens
    }
    production_keys: dict[str, tuple[int, tuple[int, ...]]] = {}
    coordinate_failures: list[str] = []
    label_failures: list[str] = []
    for token in tokens:
        module = runtime["approved"].direct_schema_vertex(
            generator, runtime["schemas"][token["module_schema"]], 0, cell.base_i
        )
        label = runtime["approved"].direct_schema_vertex(
            generator, runtime["schemas"][token["label_schema"]], 0, cell.base_i
        )
        key = (token["occurrence"], module)
        production_keys[token["id"]] = key
        replay = replay_by_key.get(key)
        if replay is None:
            coordinate_failures.append(token["id"])
        elif replay.label != label or replay.polarity != token["polarity"]:
            label_failures.append(token["id"])
    extra = sorted(
        f"o{occurrence}:{generator.lit(module)}"
        for occurrence, module in set(replay_by_key) - set(production_keys.values())
    )
    direct_q = direct.quadratic(tuple(replay_tokens))
    return {
        "base_i": cell.base_i,
        "direct_token_count": len(replay_tokens),
        "production_token_count": len(tokens),
        "coordinate_failures": coordinate_failures,
        "label_failures": label_failures,
        "extra_coordinates": extra,
        "direct_Q": direct_q,
        "prefix_Q": prefix_q,
        "Q_matches": direct_q == prefix_q,
    }


def cell_result(runtime: dict[str, Any], cell: Any) -> dict[str, Any]:
    tokens, fibers, failures = cell_runtime(runtime, cell)
    ranked, witnesses, rank_failures = ranked_slots(runtime, cell, fibers)
    zero_order, zero_failures = slot_zero_order(runtime, cell)
    positions, chronology_failures = chronology_positions(tokens, ranked, zero_order)
    chords, repeated, chord_failures = resolve_chords(
        runtime, cell, tokens, fibers, positions
    )
    sweep = prefix_sweep(chords)
    replay = direct_replay(runtime, cell, tokens, sweep["Q"])
    if (
        replay["direct_token_count"] != 96
        or replay["production_token_count"] != 96
        or replay["coordinate_failures"]
        or replay["label_failures"]
        or replay["extra_coordinates"]
        or not replay["Q_matches"]
    ):
        failures.append(f"direct_replay:{cell.cell_id}")
    boundary_types = Counter(
        tuple(chord["occurrence_type"])
        for chord in chords if chord["kind"] == "boundary"
    )
    adjacency_types = Counter(
        tuple(chord["occurrence_type"])
        for chord in chords if chord["kind"] == "adjacency"
    )
    if boundary_types != EXPECTED_BOUNDARY_TYPES:
        failures.append(f"boundary_types:{cell.cell_id}:{boundary_types}")
    if adjacency_types != EXPECTED_ADJACENCY_TYPES:
        failures.append(f"adjacency_types:{cell.cell_id}:{adjacency_types}")
    token_records = [{
        key: token[key]
        for key in (
            "id", "coordinate_id", "family", "slot", "occurrence",
            "polarity", "module_schema", "label_schema",
        )
    } for token in tokens]
    return {
        "cell": {"id": cell.cell_id, "i": "ge3" if cell.value is None else cell.value, "base_i": cell.base_i},
        "tokens": token_records,
        "ranked_active_slots": {str(slot): rows for slot, rows in ranked.items()},
        "adjacent_witnesses": witnesses,
        "slot_zero_order": zero_order,
        "chords": chords,
        "repeated_chord_labels": repeated,
        "prefix_sweep": sweep,
        "direct_base_replay": replay,
        "computed": {
            "Q": sweep["Q"],
            "status": "provisional_pending_guarded_execution_independent_replay_and_sol_review",
        },
        "generation_failures": [
            *failures, *rank_failures, *zero_failures,
            *chronology_failures, *chord_failures,
        ],
    }


def binding_paths() -> dict[str, Path]:
    return {
        "raw_checker": RAW_CHECKER_PATH,
        "raw_manifest": RAW_MANIFEST_PATH,
        "approved_helpers": APPROVED_PATH,
        "normalizer": NORMALIZER_PATH,
        "generator": GENERATOR_PATH,
        "direct_replay": DIRECT_PATH,
        "theory": THEORY_PATH,
        "checker": CHECKER_PATH,
        "tests": TEST_PATH,
    }


def source_bindings() -> dict[str, Any]:
    bindings = {
        name: {
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256_path(path),
        }
        for name, path in binding_paths().items()
    }
    bindings["raw_manifest"]["validation"] = (
        "full hash plus live structure; raw manifest carries the stable Section 4.1 digest"
    )
    bindings["theory"]["sections"] = ["5.1", "5.2", "5.3", "7.1"]
    return bindings


def build_manifest() -> dict[str, Any]:
    raw_manifest = raw_manifest_structure()
    runtime = build_runtime()
    cells = [cell_result(runtime, cell) for cell in runtime["raw"].CELLS]
    failures = [*runtime["failures"]]
    failures.extend(
        failure for cell in cells for failure in cell["generation_failures"]
    )
    live_coordinate_ids = {
        coordinate_id
        for rows in cells[0]["ranked_active_slots"].values()
        for coordinate_id in rows
    }
    if live_coordinate_ids != {
        row["coordinate_id"] for row in raw_manifest["coordinate_schemas"]
    }:
        failures.append("raw_manifest_live_coordinate_catalog")
    return {
        "format": "period-two-diagonal-pure-p-quadratic-provisional-v1",
        "scope": {
            "parameter": "i>=0, cells 0,1,2,>=3",
            "increment": "q_i=A_(i+1,i+1)+A_(i,i)",
            "computed_target": "Q(q_i) by deterministic 48-chord prefix sweep",
            "status": "provisional_pending_guarded_execution_independent_replay_and_sol_review",
            "nonclaim": (
                "No expected Q value is imposed. This artifact alone proves no diagonal, "
                "unary-delta, period-two, AK3, stable-AC, or AC claim."
            ),
        },
        "source_bindings": source_bindings(),
        "raw_manifest_structure": {
            "format": raw_manifest["format"],
            "cells": [cell["id"] for cell in raw_manifest["cells"]],
            "coordinate_count": len(raw_manifest["coordinate_schemas"]),
            "binding_note": "full-file theory hash intentionally not copied; structure is replayed live",
        },
        "topology": {
            "chord_count": 48,
            "boundary_count": 12,
            "adjacency_count": 36,
            "repeated_label_pair": list(REPEATED_LABEL_PAIR),
        },
        "normal_form": {
            "common_primitive_reference": runtime["generator"].lit(
                runtime["common_primitive_reference"]
            ),
            "scope": "all path and slot-zero schemas",
        },
        "cells": cells,
        "generation_failures": failures,
    }


def verification_failures(
    manifest: dict[str, Any], expected: dict[str, Any] | None = None
) -> list[str]:
    failures: list[str] = []
    try:
        recomputed = build_manifest() if expected is None else expected
        if manifest["format"] != "period-two-diagonal-pure-p-quadratic-provisional-v1":
            failures.append("format")
        if manifest["scope"]["status"] != "provisional_pending_guarded_execution_independent_replay_and_sol_review":
            failures.append("status")
        if "expected_Q" in manifest["scope"]:
            failures.append("expected_Q_forbidden")
        if manifest["generation_failures"]:
            failures.append("generation_failures")
        for name, path in binding_paths().items():
            if manifest["source_bindings"][name]["sha256"] != sha256_path(path):
                failures.append(f"source_hash:{name}")
        if manifest["topology"] != {
            "chord_count": 48,
            "boundary_count": 12,
            "adjacency_count": 36,
            "repeated_label_pair": list(REPEATED_LABEL_PAIR),
        }:
            failures.append("topology")
        if manifest["normal_form"] != recomputed["normal_form"]:
            failures.append("common_primitive_reference")
        for cell in manifest["cells"]:
            cell_id = cell["cell"]["id"]
            tokens = cell["tokens"]
            token_by_id = {token["id"]: token for token in tokens}
            if len(tokens) != 96 or len(token_by_id) != 96:
                failures.append(f"token_count:{cell_id}")
            if Counter(token["slot"] for token in tokens) != Counter({0: 12, 2: 18, 3: 30, 4: 36}):
                failures.append(f"token_profile:{cell_id}")
            if any(
                token["polarity"] != EXPECTED_POLARITY.get(token["occurrence"])
                for token in tokens
            ):
                failures.append(f"polarity:{cell_id}")
            ranks = cell["ranked_active_slots"]
            if {slot: len(rows) for slot, rows in ranks.items()} != {"2": 9, "3": 15, "4": 18}:
                failures.append(f"rank_profile:{cell_id}")
            ranked_coordinates = {
                coordinate_id for rows in ranks.values() for coordinate_id in rows
            }
            path_coordinates = {
                token["coordinate_id"] for token in tokens if token["slot"] != 0
            }
            if ranked_coordinates != path_coordinates:
                failures.append(f"rank_coverage:{cell_id}")
            witnesses = cell["adjacent_witnesses"]
            if len(witnesses) != 39 or any(
                witness["comparison"].get("order") != -1 or not witness["common_phase"]
                for witness in witnesses
            ):
                failures.append(f"adjacent_witness:{cell_id}")
            expected_adjacent = {
                (int(slot), left, right)
                for slot, rows in ranks.items()
                for left, right in zip(rows, rows[1:])
            }
            actual_adjacent = {
                (row["slot"], row["left_coordinate"], row["right_coordinate"])
                for row in witnesses
            }
            if actual_adjacent != expected_adjacent:
                failures.append(f"rank_adjacency:{cell_id}")
            if (
                not cell["slot_zero_order"]["old_before_new"]
                or cell["slot_zero_order"]["comparison"].get("order") != -1
            ):
                failures.append(f"slot_zero_order:{cell_id}")
            chords = cell["chords"]
            if len(chords) != 48 or Counter(chord["kind"] for chord in chords) != Counter({"boundary": 12, "adjacency": 36}):
                failures.append(f"chord_count:{cell_id}")
            endpoint_ids = [endpoint for chord in chords for endpoint in chord["endpoint_ids"]]
            if Counter(endpoint_ids) != Counter({token_id: 1 for token_id in token_by_id}):
                failures.append(f"chord_assignment:{cell_id}")
            for chord in chords:
                if any(endpoint not in token_by_id for endpoint in chord["endpoint_ids"]):
                    failures.append(f"chord_endpoint:{cell_id}:{chord['id']}")
                    continue
                bound_occurrences = [token_by_id[endpoint]["occurrence"] for endpoint in chord["endpoint_ids"]]
                if bound_occurrences != chord["endpoint_occurrences"]:
                    failures.append(f"endpoint_occurrence:{cell_id}:{chord['id']}")
                if not chord["endpoint_label_equal"] or chord["endpoint_label_comparison"].get("order") != 0:
                    failures.append(f"label_equality:{cell_id}:{chord['id']}")
                if chord["positions"] != sorted(chord["positions"]) or chord["positions"][0] == chord["positions"][1]:
                    failures.append(f"chord_positions:{cell_id}:{chord['id']}")
            boundary_types = Counter(
                tuple(chord["occurrence_type"])
                for chord in chords if chord["kind"] == "boundary"
            )
            adjacency_types = Counter(
                tuple(chord["occurrence_type"])
                for chord in chords if chord["kind"] == "adjacency"
            )
            if boundary_types != EXPECTED_BOUNDARY_TYPES:
                failures.append(f"boundary_types:{cell_id}")
            if adjacency_types != EXPECTED_ADJACENCY_TYPES:
                failures.append(f"adjacency_types:{cell_id}")
            repeated = cell["repeated_chord_labels"]
            if len(repeated) != 1 or repeated[0]["chords"] != list(sorted(REPEATED_LABEL_PAIR)) or not repeated[0]["nested"]:
                failures.append(f"repeated_label_nesting:{cell_id}")
            recomputed_sweep = prefix_sweep(chords)
            if cell["prefix_sweep"] != recomputed_sweep:
                failures.append(f"prefix_lambda:{cell_id}")
            if cell["computed"]["Q"] != recomputed_sweep["Q"]:
                failures.append(f"Q:{cell_id}")
            replay = cell["direct_base_replay"]
            if (
                replay["direct_token_count"] != 96
                or replay["production_token_count"] != 96
                or replay["coordinate_failures"]
                or replay["label_failures"]
                or replay["extra_coordinates"]
                or not replay["Q_matches"]
                or replay["direct_Q"] != cell["computed"]["Q"]
            ):
                failures.append(f"direct_replay:{cell_id}")
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


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    manifest = write_manifest() if args.write else check_manifest() if args.check else verify_manifest(build_manifest())
    print(json.dumps({
        "format": manifest["format"],
        "status": manifest["scope"]["status"],
        "failures": len(manifest["generation_failures"]),
        "cells": [
            {"id": cell["cell"]["id"], "Q": cell["computed"]["Q"]}
            for cell in manifest["cells"]
        ],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
