#!/usr/bin/env python3
"""Independent all-power replay of diagonal pure-P quadratic data.

No producer module is imported and no producer scalar Q is read.  The replay
selects the 39 authoritative source rows locally, expands them into 46 signed
contexts, constructs common-phase affine schemas, collision fibers, 96
decorated tokens, and the 48 source-path chords.  Q is computed independently
by the prefix sweep and by the authoritative 4560-pair direct kernel at the
four cell bases; only those two independent values are compared.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import importlib.util
from itertools import combinations
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPLAY_PATH = Path(__file__).resolve()
TEST_PATH = ROOT / ".scratch/test_period_two_diagonal_pure_p_quadratic_independent_replay.py"
GENERATOR_PATH = ROOT / ".scratch/period_two_raw_stream_manifest_generator.py"
NORMALIZER_PATH = ROOT / ".scratch/period_two_inverse_q_companion_checker.py"
APPROVED_PATH = ROOT / ".scratch/period_two_inverse_pure_increment_checker.py"
RAW_MANIFEST_PATH = ROOT / ".scratch/period_two_diagonal_pure_p_raw_manifest.json"
DIRECT_PATH = ROOT / ".scratch/period_two_seven_family_covariance_checker.py"
PRIMARY_CHECKER_PATH = ROOT / ".scratch/period_two_diagonal_pure_p_quadratic_checker.py"
PRIMARY_MANIFEST_PATH = ROOT / ".scratch/period_two_diagonal_pure_p_quadratic_manifest.json"
HESSIAN_PATH = ROOT / "experiments/stable_ac/depth4_period_two_phi_infinity_hessian_certificate.py"
TREE_PATH = ROOT / "experiments/stable_ac/depth4_period_two_tree_flow_factorization_certificate.py"
LIFT_PATH = ROOT / "experiments/stable_ac/depth4_period_two_lift_certificate.py"
THEORY_PATH = ROOT / "literature/proofs/AK3_PURE_P_INCREMENT_NORMAL_FORM.md"

THEORY_INTERVALS = (
    ("matching_and_order", "### 5.1 Deterministic 48-chord matching\n", "## 6. Exact head--tail interface\n", False),
    ("certificate_interface", "### 7.1 Minimal quadratic certificate interface\n", "<!-- AK3_PURE_P_Q_SECTION_7_1_END -->\n", True),
)
SLOT_ZERO = (3, 4, 7, 8, 11, 12)
OCCURRENCES_BY_SLOT = {2: (1, 6), 3: (9, 14), 4: (15, 16)}
ACTIVE_OCCURRENCES = (1, 3, 4, 6, 7, 8, 9, 11, 12, 14, 15, 16)
EXPECTED_POLARITY = {1: 1, 3: 1, 4: -1, 6: -1, 7: 1, 8: -1, 9: 1, 11: 1, 12: -1, 14: -1, 15: 1, 16: -1}
EXPECTED_FAMILIES = {"long_p1": 14, "long_pstar": 18, "short_w3": 4, "short_z3": 6, "short_w2": 4}
EXPECTED_PROFILE = {"2": 9, "3": 15, "4": 18}
EXPECTED_BOUNDARY = Counter({(1, 3): 1, (3, 15): 1, (4, 9): 2, (6, 11): 1, (6, 7): 1, (9, 11): 1, (7, 9): 1, (8, 9): 2, (12, 15): 2})
EXPECTED_ADJACENCY = Counter({(1, 16): 4, (6, 9): 4, (14, 16): 11, (9, 15): 4, (9, 14): 1, (1, 15): 3, (1, 6): 1, (6, 15): 2, (15, 16): 3, (14, 15): 3})
REPEATED_PAIR = ("new_component3:junction", "residual_b:boundary:right")


@dataclass(frozen=True)
class ICell:
    cell_id: str
    value: int | None
    base_i: int


CELLS = (ICell("e0_n0", 0, 0), ICell("e0_n1", 1, 1), ICell("e0_n2", 2, 2), ICell("e0_nge3", None, 3))


@dataclass(frozen=True)
class Endpoint:
    kind: str
    delta: int | None = None
    occurrence: int | None = None
    member: str | None = None
    side: str | None = None


@dataclass(frozen=True)
class Chord:
    chord_id: str
    kind: str
    left: Endpoint
    right: Endpoint


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


def canonical_line(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def marked_intervals() -> list[dict[str, Any]]:
    data = THEORY_PATH.read_bytes()
    rows = []
    for interval_id, start_text, end_text, include_end in THEORY_INTERVALS:
        start, end = start_text.encode(), end_text.encode()
        if data.count(start) != 1 or data.count(end) != 1:
            raise AssertionError((interval_id, data.count(start), data.count(end)))
        left, right = data.index(start), data.index(end)
        if right <= left:
            raise AssertionError((interval_id, left, right))
        if include_end:
            right += len(end)
        payload = data[left:right]
        rows.append({"id": interval_id, "start_marker": start_text.rstrip(), "end_marker": end_text.rstrip(), "include_end_marker": include_end, "byte_length": len(payload), "sha256": hashlib.sha256(payload).hexdigest()})
    return rows


def binding_paths() -> dict[str, Path]:
    return {"generator": GENERATOR_PATH, "normalizer": NORMALIZER_PATH, "approved": APPROVED_PATH, "raw_manifest": RAW_MANIFEST_PATH, "direct": DIRECT_PATH, "primary_checker": PRIMARY_CHECKER_PATH, "primary_manifest": PRIMARY_MANIFEST_PATH, "hessian": HESSIAN_PATH, "tree": TREE_PATH, "lift": LIFT_PATH, "replay": REPLAY_PATH, "tests": TEST_PATH}


def source_bindings() -> dict[str, Any]:
    rows = {name: {"path": str(path.relative_to(ROOT)), "sha256": sha256_path(path)} for name, path in binding_paths().items()}
    rows["theory_intervals"] = marked_intervals()
    return rows


def const_value(expr: dict[str, Any]) -> int | None:
    return expr.get("value") if expr.get("op") == "const" else None


def variable_name(expr: dict[str, Any]) -> str | None:
    return expr.get("name") if expr.get("op") == "var" else None


def primitive_reference(normalizer: Any, generator: Any, row: dict[str, Any]) -> tuple[int, ...]:
    factors = row["module_vertex"]["factors"]
    positions = [index for index, item in enumerate(factors) if variable_name(item["exponent"]) == "h"]
    if len(positions) != 1:
        raise AssertionError((row["id"], positions))
    power = generator.parse_raw(factors[positions[0]]["word"])
    _, cyclic, _ = normalizer.cyclic_decomposition(generator, power)
    reference, multiplier = normalizer.primitive_power(cyclic)
    if multiplier != 3:
        raise AssertionError((row["id"], "primitive_multiplier", multiplier))
    return reference


def schema_from_factors(approved: Any, normalizer: Any, generator: Any, schema_id: str, factors: list[dict[str, Any]], variable: str, offset: int, reference: tuple[int, ...]) -> Any:
    variable_positions = [index for index, item in enumerate(factors) if variable_name(item["exponent"]) == variable]
    if len(variable_positions) != 1:
        raise AssertionError((schema_id, "variable_positions", variable_positions))
    variable_index = variable_positions[0]
    if any(const_value(item["exponent"]) != 1 for index, item in enumerate(factors) if index != variable_index):
        raise AssertionError((schema_id, "factor_order_or_exponent"))
    words = [generator.parse_raw(item["word"]) for item in factors]
    power = words[variable_index]
    p_left, p_core, p_multiplier, p_right = normalizer.reference_primitive_decomposition(generator, power, reference)
    if p_core != reference or p_multiplier != 3:
        raise AssertionError((schema_id, "common_phase", generator.lit(p_core), p_multiplier))
    left = tuple(letter for word in words[:variable_index] for letter in word)
    right = tuple(letter for word in words[variable_index + 1:] for letter in word)
    return approved.AffineENSchema(schema_id=schema_id, source_left=left, source_q=(), source_middle=(), source_p=power, source_right=right, fixed_0=left, q_core=(), q_multiplier=0, fixed_1=p_left, p_core=p_core, p_multiplier=p_multiplier, fixed_2=(*p_right, *right), q_offset=0, p_offset=offset)


def label_schema(approved: Any, module: Any, schema_id: str, action: tuple[int, ...]) -> Any:
    return approved.AffineENSchema(schema_id=schema_id, source_left=(*action, *module.source_left), source_q=module.source_q, source_middle=module.source_middle, source_p=module.source_p, source_right=module.source_right, fixed_0=(*action, *module.fixed_0), q_core=module.q_core, q_multiplier=module.q_multiplier, fixed_1=module.fixed_1, p_core=module.p_core, p_multiplier=module.p_multiplier, fixed_2=module.fixed_2, q_offset=module.q_offset, p_offset=module.p_offset)


def selected_contexts(generator: Any) -> tuple[list[dict[str, Any]], list[str]]:
    _, source_rows = generator.build_w_rows()
    by_id = {row["id"]: row for row in source_rows}
    contexts, failures = [], []
    def add(source_id: str, family: str, state: str, offset: int, sign: int) -> None:
        source = by_id[source_id]
        if source["coefficient"] != source["source_scale"] * source["incidence_sign"]:
            failures.append(f"source_sign:{source_id}")
        contexts.append({"source": source, "family": family, "state": state, "offset": offset, "direction_sign": sign})
    for nu, family in ((1, "long_p1"), (3, "long_pstar")):
        for position in range(len(generator.BLOCKS[nu - 1][0])):
            add(f"W:nu{nu}:P:{position}:o+1", family, "new_segment", 1, 1)
    for nu, family, prefix in ((4, "short_w3", generator.BLOCKS[2][0]), (5, "short_z3", generator.BLOCKS[2][0]), (6, "short_w2", generator.BLOCKS[1][1])):
        c_word = generator.BLOCKS[nu - 1][1]
        if not c_word.startswith(prefix):
            failures.append(f"prefix:{nu}")
            continue
        for position in range(len(prefix), len(c_word)):
            source_id = f"W:nu{nu}:C:{position}:o+1"
            add(source_id, family, "old", 0, -1)
            add(source_id, family, "new", 1, 1)
    if len(contexts) != 46 or len({row["source"]["id"] for row in contexts}) != 39 or Counter(row["family"] for row in contexts) != Counter(EXPECTED_FAMILIES):
        failures.append("context_inventory")
    for item in contexts:
        source = item["source"]
        expected_pre = [generator.factor(generator.eval_path(factor["word"]), factor["exponent"]) for factor in reversed(source["raw_prefix"])] + [generator.factor(source["root"], generator.const(1))]
        _, _, multiplier, _ = generator.edge_rule(source["actual_letter"])
        expected_factors = [generator.factor(multiplier, generator.const(1)), *expected_pre]
        if source["module_vertex"]["factors"] != expected_factors:
            failures.append(f"factor_order:{source['id']}")
    return contexts, failures


def build_schemas(approved: Any, normalizer: Any, generator: Any, actions: dict[int, tuple[int, ...]]) -> tuple[dict[str, Any], list[dict[str, Any]], list[str], tuple[int, ...]]:
    contexts, failures = selected_contexts(generator)
    seed = next(row["source"] for row in contexts if row["source"]["id"] == "W:nu1:P:0:o+1")
    reference = primitive_reference(normalizer, generator, seed)
    schemas, provenance = {}, []
    for item in contexts:
        source = item["source"]
        row_id = f"diag:{item['family']}:{item['state']}:{source['id']}"
        variable = "h" if source["key"]["block"] == "P" else "i"
        module_id = f"{row_id}:module"
        try:
            module = schema_from_factors(approved, normalizer, generator, module_id, source["module_vertex"]["factors"], variable, item["offset"], reference)
        except Exception as exc:
            failures.append(f"schema:{row_id}:{type(exc).__name__}:{exc}")
            continue
        schemas[module_id] = module
        labels = {}
        slot = source["key"]["slot"]
        for occurrence in OCCURRENCES_BY_SLOT[slot]:
            label_id = f"{row_id}:label:o{occurrence}"
            schemas[label_id] = label_schema(approved, module, label_id, actions[occurrence])
            labels[str(occurrence)] = label_id
        provenance.append({"id": row_id, "source_row_id": source["id"], "source_key": source["key"], "family": item["family"], "state": item["state"], "power_variable": variable, "power_offset": item["offset"], "nu": source["key"]["nu"], "block": source["key"]["block"], "position": source["key"]["position"], "stored_letter": source["stored_letter"], "actual_letter": source["actual_letter"], "slot": slot, "source_scale": source["source_scale"], "incidence_sign": source["incidence_sign"], "source_coefficient": source["coefficient"], "direction_sign": item["direction_sign"], "integral_coefficient": item["direction_sign"] * source["coefficient"], "module_schema": module_id, "label_schemas": labels, "factor_order": source["module_vertex"]["factors"], "source_binding": "local BLOCKS/build_w_rows/trace_ast/parse_raw selection"})
    gamma_inverse = generator.lift.quotient_inverse(generator.eval_path(generator.BLOCKS[0][2]))
    p_inverse = generator.lift.quotient_inverse(generator.parse_raw("tc"))
    zero_factors = [{"word": generator.lit(p_inverse), "exponent": {"op": "const", "value": 1}}, {"word": "c", "exponent": {"op": "const", "value": 1}}, {"word": generator.lit(gamma_inverse), "exponent": {"op": "var", "name": "i"}}, {"word": "t", "exponent": {"op": "const", "value": 1}}]
    for delta, offset in ((0, 1), (1, 2)):
        module_id = f"quadratic:slot0:delta{delta}:module"
        module = schema_from_factors(approved, normalizer, generator, module_id, zero_factors, "i", offset, reference)
        schemas[module_id] = module
        for occurrence in SLOT_ZERO:
            label_id = f"quadratic:slot0:delta{delta}:label:o{occurrence}"
            schemas[label_id] = label_schema(approved, module, label_id, actions[occurrence])
    provenance.sort(key=lambda row: row["id"])
    return schemas, provenance, failures, reference


def build_templates(approved: Any, normalizer: Any, generator: Any, schemas: dict[str, Any]) -> tuple[dict[tuple[str, str], Any], list[dict[str, Any]], list[str]]:
    templates, audit, failures = {}, [], []
    for schema_id, schema in sorted(schemas.items()):
        for cell in CELLS:
            en_cell = approved.ENCell(cell.cell_id, 0, cell.value, 0, cell.base_i)
            try:
                template = approved.build_template_en(normalizer, generator, schema, en_cell)
                base = approved.direct_schema_vertex(generator, schema, 0, cell.base_i)
                if template.base_word != base or approved.expand_template_en(template, 0, cell.base_i) != base:
                    failures.append(f"template_base:{schema_id}:{cell.cell_id}")
                if cell.value is None:
                    for i in (4,):
                        direct = approved.direct_schema_vertex(generator, schema, 0, i)
                        if approved.expand_template_en(template, 0, i) != direct:
                            failures.append(f"template_i4:{schema_id}")
                if schema.p_multiplier != 3:
                    failures.append(f"template_multiplier:{schema_id}:{schema.p_multiplier}")
                templates[(schema_id, cell.cell_id)] = template
                audit.append({
                    "schema_id": schema_id,
                    "cell": cell.cell_id,
                    "cell_is_unbounded": cell.value is None,
                    "p_multiplier": schema.p_multiplier,
                    "p_core": generator.lit(schema.p_core),
                    "p_offset": schema.p_offset,
                    "base_word": generator.lit(base),
                    "base_matches": template.base_word == base,
                    "next_i": 4 if cell.value is None else None,
                    "next_word": generator.lit(approved.expand_template_en(template, 0, 4)) if cell.value is None else None,
                    "next_matches": cell.value is not None or approved.expand_template_en(template, 0, 4) == approved.direct_schema_vertex(generator, schema, 0, 4),
                    "i4_word": generator.lit(approved.expand_template_en(template, 0, 4)) if cell.value is None else None,
                    "i4_matches": cell.value is not None or approved.expand_template_en(template, 0, 4) == approved.direct_schema_vertex(generator, schema, 0, 4),
                })
            except Exception as exc:
                failures.append(f"template:{schema_id}:{cell.cell_id}:{type(exc).__name__}:{exc}")
    return templates, audit, failures


def coordinate_id(members: list[dict[str, Any]]) -> str:
    payload = "|".join(sorted(row["id"] for row in members)).encode()
    return f"coord:{hashlib.sha256(payload).hexdigest()[:16]}"


def collision_fibers(approved: Any, normalizer: Any, generator: Any, cell: ICell, provenance: list[dict[str, Any]], templates: dict[tuple[str, str], Any]) -> tuple[list[dict[str, Any]], list[str]]:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for row in provenance:
        key = (row["slot"], approved.canonical_blocks(normalizer, templates[(row["module_schema"], cell.cell_id)]))
        grouped.setdefault(key, []).append(row)
    fibers, failures = [], []
    for members in sorted(grouped.values(), key=lambda rows: (rows[0]["slot"], sorted(row["id"] for row in rows))):
        members = sorted(members, key=lambda row: row["id"])
        coefficient = sum(row["integral_coefficient"] for row in members)
        representative = members[0]
        labels = {str(o): representative["label_schemas"][str(o)] for o in OCCURRENCES_BY_SLOT[representative["slot"]]}
        witnesses = []
        for member in members[1:]:
            module_comparison = approved.compare_templates_en(normalizer, generator, templates[(representative["module_schema"], cell.cell_id)], templates[(member["module_schema"], cell.cell_id)])
            witnesses.append({"kind": "module", "representative": representative["id"], "member": member["id"], "comparison": module_comparison})
            if module_comparison.get("order") != 0:
                failures.append(f"collision_module:{cell.cell_id}:{representative['id']}:{member['id']}")
            for occurrence in OCCURRENCES_BY_SLOT[representative["slot"]]:
                label_comparison = approved.compare_templates_en(normalizer, generator, templates[(representative["label_schemas"][str(occurrence)], cell.cell_id)], templates[(member["label_schemas"][str(occurrence)], cell.cell_id)])
                canonical_equal = approved.canonical_blocks(normalizer, templates[(representative["label_schemas"][str(occurrence)], cell.cell_id)]) == approved.canonical_blocks(normalizer, templates[(member["label_schemas"][str(occurrence)], cell.cell_id)])
                witnesses.append({"kind": "label", "occurrence": occurrence, "representative": representative["id"], "member": member["id"], "canonical_equal": canonical_equal, "comparison": label_comparison})
                if label_comparison.get("order") != 0 or not canonical_equal:
                    failures.append(f"collision_label:{cell.cell_id}:o{occurrence}:{representative['id']}:{member['id']}")
        fibers.append({"coordinate_id": coordinate_id(members), "slot": representative["slot"], "families": sorted({row["family"] for row in members}), "members": [row["id"] for row in members], "integral_coefficient_sum": coefficient, "activity_parity": coefficient % 2, "module_schema": representative["module_schema"], "label_schemas": labels, "collision_witnesses": witnesses})
    inactive = [fiber for fiber in fibers if not fiber["activity_parity"]]
    expected_inactive = [
        sorted([f"diag:long_pstar:new_segment:W:nu3:P:{position}:o+1", f"diag:short_w3:old:W:nu4:C:{18 + position}:o+1"])
        for position in (0, 1)
    ]
    if len(fibers) != 44 or sorted(fiber["members"] for fiber in inactive) != sorted(expected_inactive):
        failures.append(f"fiber_shape:{cell.cell_id}")
    active = [fiber for fiber in fibers if fiber["activity_parity"]]
    profile = {str(slot): sum(fiber["slot"] == slot for fiber in active) for slot in (2, 3, 4)}
    if len(active) != 42 or profile != EXPECTED_PROFILE:
        failures.append(f"active_profile:{cell.cell_id}:{profile}")
    return fibers, failures


def catalog(fibers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"coordinate_id": fiber["coordinate_id"], "slot": fiber["slot"], "family": fiber["families"][0] if len(fiber["families"]) == 1 else "+".join(fiber["families"]), "members": fiber["members"], "integral_coefficient_sum": fiber["integral_coefficient_sum"], "module_schema": fiber["module_schema"]} for fiber in sorted(fibers, key=lambda row: row["coordinate_id"]) if fiber["activity_parity"]]


def build_tokens(cell: ICell, fibers: list[dict[str, Any]], templates: dict[tuple[str, str], Any], occurrences: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    tokens = []
    for fiber in fibers:
        if not fiber["activity_parity"]:
            continue
        for occurrence in OCCURRENCES_BY_SLOT[fiber["slot"]]:
            label_id = fiber["label_schemas"][str(occurrence)]
            tokens.append({"id": f"{cell.cell_id}:{fiber['coordinate_id']}:o{occurrence}", "coordinate_id": fiber["coordinate_id"], "family": fiber["families"][0], "slot": fiber["slot"], "occurrence": occurrence, "polarity": occurrences[occurrence]["polarity"], "module_schema": fiber["module_schema"], "module_template": templates[(fiber["module_schema"], cell.cell_id)], "label_schema": label_id, "label_template": templates[(label_id, cell.cell_id)]})
    for delta in (0, 1):
        for occurrence in SLOT_ZERO:
            module_id = f"quadratic:slot0:delta{delta}:module"
            label_id = f"quadratic:slot0:delta{delta}:label:o{occurrence}"
            tokens.append({"id": f"{cell.cell_id}:slot0:delta{delta}:o{occurrence}", "coordinate_id": f"slot0:delta{delta}", "family": "slot0", "slot": 0, "occurrence": occurrence, "polarity": occurrences[occurrence]["polarity"], "module_schema": module_id, "module_template": templates[(module_id, cell.cell_id)], "label_schema": label_id, "label_template": templates[(label_id, cell.cell_id)]})
    tokens.sort(key=lambda row: row["id"])
    if len(tokens) != 96 or Counter(token["slot"] for token in tokens) != Counter({0: 12, 2: 18, 3: 30, 4: 36}):
        raise AssertionError((cell.cell_id, len(tokens), Counter(token["slot"] for token in tokens)))
    return tokens


def ranked(approved: Any, normalizer: Any, generator: Any, cell: ICell, fibers: list[dict[str, Any]], templates: dict[tuple[str, str], Any]) -> tuple[dict[int, list[str]], list[dict[str, Any]], list[str]]:
    order, witnesses, failures = {}, [], []
    for slot, expected in ((2, 9), (3, 15), (4, 18)):
        rows = [fiber for fiber in fibers if fiber["activity_parity"] and fiber["slot"] == slot]
        rows.sort(key=lambda fiber: (len(templates[(fiber["module_schema"], cell.cell_id)].base_word), templates[(fiber["module_schema"], cell.cell_id)].base_word))
        order[slot] = [fiber["coordinate_id"] for fiber in rows]
        if len(rows) != expected:
            failures.append(f"rank_count:{cell.cell_id}:s{slot}")
        for index, (left, right) in enumerate(zip(rows, rows[1:])):
            comparison = approved.compare_templates_en(normalizer, generator, templates[(left["module_schema"], cell.cell_id)], templates[(right["module_schema"], cell.cell_id)])
            witnesses.append({"id": f"rank:s{slot}:{index}", "slot": slot, "left_coordinate": left["coordinate_id"], "right_coordinate": right["coordinate_id"], "comparison": comparison, "common_phase": comparison.get("order") == -1})
            if comparison.get("order") != -1:
                failures.append(f"rank_unresolved:{cell.cell_id}:s{slot}:{index}")
    if len(witnesses) != 39:
        failures.append(f"rank_witness_count:{cell.cell_id}")
    return order, witnesses, failures


def endpoint_map(letter: str, side: str) -> int:
    return {"B": {"pre": 1, "post": 6}, "b": {"pre": 6, "post": 1}, "G": {"pre": 14, "post": 9}, "g": {"pre": 9, "post": 14}, "A": {"pre": 16, "post": 15}, "a": {"pre": 15, "post": 16}}[letter][side]


def boundary(delta: int, occurrence: int) -> Endpoint:
    return Endpoint("slot0", delta=delta, occurrence=occurrence)


def edge(member: str, side: str) -> Endpoint:
    return Endpoint("edge", member=member, side=side)


def row_id(family: str, state: str, source: str) -> str:
    return f"diag:{family}:{state}:{source}"


def path_chords(name: str, members: list[str], left: Endpoint, right: Endpoint) -> list[Chord]:
    rows = [Chord(f"{name}:boundary:left", "boundary", left, edge(members[0], "pre"))]
    rows.extend(Chord(f"{name}:adjacency:{i}", "adjacency", edge(members[i - 1], "post"), edge(members[i], "pre")) for i in range(1, len(members)))
    rows.append(Chord(f"{name}:boundary:right", "boundary", edge(members[-1], "post"), right))
    return rows


def chord_specs() -> list[Chord]:
    long = lambda nu, family, pos: row_id(family, "new_segment", f"W:nu{nu}:P:{pos}:o+1")
    short = lambda nu, family, state, pos: row_id(family, state, f"W:nu{nu}:C:{pos}:o+1")
    p1 = [long(1, "long_p1", i) for i in range(14)]
    ps = [long(3, "long_pstar", i) for i in range(2, 18)]
    oz = [short(5, "short_z3", "old", 18 + i) for i in range(3)]
    nz = [short(5, "short_z3", "new", 18 + i) for i in range(3)]
    nw = [short(4, "short_w3", "new", 18 + i) for i in range(2)]
    ou = [short(6, "short_w2", "old", 19 + i) for i in range(2)]
    nu = [short(6, "short_w2", "new", 19 + i) for i in range(2)]
    rows = path_chords("terminal_p1", p1, boundary(0, 3), boundary(1, 3)) + path_chords("old_component2_w", ou, boundary(0, 12), boundary(0, 8)) + path_chords("new_component2_w", nu, boundary(1, 12), boundary(1, 8)) + path_chords("old_component3_z", oz, boundary(0, 11), boundary(0, 4)) + path_chords("residual_b", ps, boundary(0, 7), boundary(1, 11))
    rows += [Chord(f"new_component3_w:adjacency:{i}", "adjacency", edge(nw[i - 1], "post"), edge(nw[i], "pre")) for i in range(1, 2)]
    rows += [Chord("new_component3_w:boundary:right", "boundary", edge(nw[-1], "post"), boundary(1, 7))]
    rows += [Chord(f"new_component3_z:adjacency:{i}", "adjacency", edge(nz[i - 1], "post"), edge(nz[i], "pre")) for i in range(1, 3)]
    rows += [Chord("new_component3_z:boundary:right", "boundary", edge(nz[-1], "post"), boundary(1, 4)), Chord("new_component3:junction", "adjacency", edge(nw[0], "pre"), edge(nz[0], "pre"))]
    if len(rows) != 48 or Counter(row.kind for row in rows) != Counter({"boundary": 12, "adjacency": 36}):
        raise AssertionError("chord inventory")
    return rows


def chronology(tokens: list[dict[str, Any]], rank: dict[int, list[str]], slot_zero_comparison: dict[str, Any]) -> tuple[dict[str, int], list[str]]:
    failures, positions, cursor = [], {}, 0
    by_occ = {o: [token for token in tokens if token["occurrence"] == o] for o in ACTIVE_OCCURRENCES}
    for occurrence in ACTIVE_OCCURRENCES:
        block = by_occ[occurrence]
        polarity = EXPECTED_POLARITY[occurrence]
        if any(token["polarity"] != polarity for token in block):
            failures.append(f"polarity:o{occurrence}")
        if occurrence in SLOT_ZERO:
            coords = ["slot0:delta0", "slot0:delta1"]
            if slot_zero_comparison.get("order") != -1:
                failures.append(f"slotzero_order:o{occurrence}")
        else:
            slot = next(slot for slot, pair in OCCURRENCES_BY_SLOT.items() if occurrence in pair)
            coords = rank[slot]
        if polarity == -1:
            coords = list(reversed(coords))
        token_map = {token["coordinate_id"]: token for token in block}
        if set(coords) != set(token_map):
            failures.append(f"chronology_block:o{occurrence}")
            continue
        for index, coord in enumerate(coords):
            positions[token_map[coord]["id"]] = cursor + index
        cursor += len(coords)
    if cursor != 96 or len(positions) != 96:
        failures.append("chronology_size")
    return positions, failures


def resolve_chords(approved: Any, normalizer: Any, generator: Any, cell: ICell, tokens: list[dict[str, Any]], fibers: list[dict[str, Any]], provenance: list[dict[str, Any]], positions: dict[str, int]) -> tuple[list[dict[str, Any]], dict[str, Any], list[str]]:
    failures, rows, reps = [], [], {}
    token_key = {(token["coordinate_id"], token["occurrence"]): token for token in tokens}
    token_id = {token["id"]: token for token in tokens}
    member_coord = {member: fiber["coordinate_id"] for fiber in fibers if fiber["activity_parity"] for member in fiber["members"]}
    provenance_by_id = {row["id"]: row for row in provenance}
    def resolve(endpoint: Endpoint) -> dict[str, Any]:
        if endpoint.kind == "slot0":
            return token_id[f"{cell.cell_id}:slot0:delta{endpoint.delta}:o{endpoint.occurrence}"]
        source = provenance_by_id[endpoint.member]
        occurrence = endpoint_map(source["actual_letter"], str(endpoint.side))
        return token_key[(member_coord[endpoint.member], occurrence)]
    for spec in chord_specs():
        left, right = resolve(spec.left), resolve(spec.right)
        comparison = approved.compare_templates_en(normalizer, generator, left["label_template"], right["label_template"])
        canonical_equal = approved.canonical_blocks(normalizer, left["label_template"]) == approved.canonical_blocks(normalizer, right["label_template"])
        if comparison.get("order") != 0 or not canonical_equal:
            failures.append(f"chord_label:{cell.cell_id}:{spec.chord_id}")
        row = {"id": spec.chord_id, "kind": spec.kind, "endpoint_ids": [left["id"], right["id"]], "endpoint_coordinates": [left["coordinate_id"], right["coordinate_id"]], "endpoint_occurrences": [left["occurrence"], right["occurrence"]], "occurrence_type": sorted([left["occurrence"], right["occurrence"]]), "positions": sorted([positions[left["id"]], positions[right["id"]]]), "endpoint_label_equal": canonical_equal, "endpoint_label_comparison": comparison}
        rows.append(row)
        reps[spec.chord_id] = left["label_template"]
    pair_records, equal_pairs, digest = [], [], hashlib.sha256()
    for left, right in combinations(rows, 2):
        comparison = approved.compare_templates_en(normalizer, generator, reps[left["id"]], reps[right["id"]])
        canonical_equal = approved.canonical_blocks(normalizer, reps[left["id"]]) == approved.canonical_blocks(normalizer, reps[right["id"]])
        record = {"left": left["id"], "right": right["id"], "order": comparison.get("order"), "method": comparison.get("method"), "canonical_equal": canonical_equal}
        pair_records.append(record); digest.update(canonical_line(record))
        if comparison.get("order") is None:
            failures.append(f"chord_pair_unresolved:{cell.cell_id}:{left['id']}:{right['id']}")
        if (comparison.get("order") == 0) != canonical_equal:
            failures.append(f"chord_pair_comparator_disagreement:{cell.cell_id}:{left['id']}:{right['id']}")
        if canonical_equal:
            equal_pairs.append(tuple(sorted((left["id"], right["id"]))))
    expected = tuple(sorted(REPEATED_PAIR))
    if equal_pairs != [expected]:
        failures.append(f"repeated_pair:{cell.cell_id}:{equal_pairs}")
    a = next(row for row in rows if row["id"] == expected[0]); b = next(row for row in rows if row["id"] == expected[1])
    a0, a1 = a["positions"]; b0, b1 = b["positions"]
    nested = (a0 < b0 < b1 < a1) or (b0 < a0 < a1 < b1)
    repeated = {"chords": list(expected), "same_label": True, "nested": nested, "positions": [a["positions"], b["positions"]]}
    if not nested:
        failures.append(f"repeat_nesting:{cell.cell_id}")
    audit = {"pair_count": len(pair_records), "equal_pairs": [list(pair) for pair in equal_pairs], "method_counts": dict(Counter(row["method"] for row in pair_records)), "digest_sha256": digest.hexdigest()}
    return rows, {"repeated": repeated, "all_pair_audit": audit}, failures


def prefix_sweep(chords: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    for index, chord in enumerate(chords):
        left, right = chord["positions"]
        hits = [prior["id"] for prior in chords[:index] for endpoint in prior["positions"] if left < endpoint < right]
        rows.append({"chord_id": chord["id"], "open_interval": [left, right], "prior_endpoint_hits": hits, "integer_count": len(hits), "lambda": len(hits) % 2})
    return {"rows": rows, "lambda_count": len(rows), "lambda_sum": sum(row["lambda"] for row in rows), "Q": sum(row["lambda"] for row in rows) % 2}


def direct_replay(direct: Any, approved: Any, generator: Any, cell: ICell, tokens: list[dict[str, Any]], schemas: dict[str, Any], prefix_q: int) -> dict[str, Any]:
    old, new = direct.anchored_direction(cell.base_i, cell.base_i), direct.anchored_direction(cell.base_i + 1, cell.base_i + 1)
    increment = direct.add_directions(new, direct.negate(old))
    replay = direct.correction_tokens(increment, f"independent:{cell.cell_id}", compute_raw=False)
    replay_by_key = {(token.occurrence, token.module_vertex): token for token in replay}
    production_keys, failures = {}, []
    for token in tokens:
        module = approved.direct_schema_vertex(generator, schemas[token["module_schema"]], 0, cell.base_i)
        label = approved.direct_schema_vertex(generator, schemas[token["label_schema"]], 0, cell.base_i)
        production_keys[token["id"]] = (token["occurrence"], module)
        actual = replay_by_key.get((token["occurrence"], module))
        if actual is None or actual.label != label or actual.polarity != token["polarity"]:
            failures.append(token["id"])
    digest, one_count, pair_count = hashlib.sha256(), 0, 0
    for left, right in combinations(replay, 2):
        bit = direct.kernel(left, right)
        record = [left.occurrence, generator.lit(left.module_vertex or ()), right.occurrence, generator.lit(right.module_vertex or ()), bit]
        digest.update(canonical_line(record)); pair_count += 1; one_count += bit
    pair_q = one_count % 2
    direct_q = direct.quadratic(replay)
    return {"base_i": cell.base_i, "token_count": len(replay), "production_token_count": len(tokens), "occurrence_profile": dict(sorted(Counter(token.occurrence for token in replay).items())), "semantic_failures": failures, "extra_coordinates": sorted(f"o{o}:{generator.lit(v)}" for o, v in set(replay_by_key) - set(production_keys.values())), "pair_ledger": {"pair_count": pair_count, "one_count": one_count, "digest_sha256": digest.hexdigest(), "Q": pair_q}, "authoritative_quadratic": direct_q, "prefix_Q": prefix_q, "agreement": pair_count == 4560 and pair_q == direct_q == prefix_q}


def semantic_projection(cell: dict[str, Any]) -> dict[str, Any]:
    projection = {key: cell[key] for key in ("cell", "tokens", "ranked_active_slots", "adjacent_witnesses", "slot_zero_order", "chords")}
    projection["repeated_chord_labels"] = [
        {
            **row,
            "chords": sorted(row["chords"]),
            "positions": sorted(row["positions"]),
        }
        for row in cell["repeated_chord_labels"]
    ]
    projection["prefix_sweep_excluding_Q"] = {key: value for key, value in cell["prefix_sweep"].items() if key != "Q"}
    return projection


def cell_result(runtime: dict[str, Any], cell: ICell) -> dict[str, Any]:
    approved, normalizer, generator = runtime["approved"], runtime["normalizer"], runtime["generator"]
    fibers, failures = collision_fibers(approved, normalizer, generator, cell, runtime["provenance"], runtime["templates"])
    tokens = build_tokens(cell, fibers, runtime["templates"], runtime["occurrences"])
    rank, witnesses, rank_failures = ranked(approved, normalizer, generator, cell, fibers, runtime["templates"])
    z0 = runtime["templates"][("quadratic:slot0:delta0:module", cell.cell_id)]
    z1 = runtime["templates"][("quadratic:slot0:delta1:module", cell.cell_id)]
    zero_comparison = approved.compare_templates_en(normalizer, generator, z0, z1)
    zero_order = {"left": "slot0:delta0", "right": "slot0:delta1", "comparison": zero_comparison, "old_before_new": zero_comparison.get("order") == -1}
    positions, chronology_failures = chronology(tokens, rank, zero_comparison)
    chords, repeat_audit, chord_failures = resolve_chords(approved, normalizer, generator, cell, tokens, fibers, runtime["provenance"], positions)
    sweep = prefix_sweep(chords)
    direct = direct_replay(runtime["direct"], approved, generator, cell, tokens, runtime["schemas"], sweep["Q"])
    token_records = [{key: token[key] for key in ("id", "coordinate_id", "family", "slot", "occurrence", "polarity", "module_schema", "label_schema")} for token in tokens]
    result = {"cell": {"id": cell.cell_id, "i": "ge3" if cell.value is None else cell.value, "base_i": cell.base_i}, "tokens": token_records, "token_inventory": {"path": sum(token["slot"] != 0 for token in tokens), "slot_zero": sum(token["slot"] == 0 for token in tokens), "total": len(tokens), "slot_profile": dict(sorted(Counter(token["slot"] for token in tokens).items()))}, "ranked_active_slots": {str(slot): rows for slot, rows in rank.items()}, "adjacent_witnesses": witnesses, "slot_zero_order": zero_order, "chords": chords, "repeated_chord_labels": [repeat_audit["repeated"]], "chord_pair_audit": repeat_audit["all_pair_audit"], "prefix_sweep": sweep, "direct_base_replay": direct, "computed": {"Q": sweep["Q"]}, "collision": {"fiber_count": len(fibers), "active_count": sum(fiber["activity_parity"] for fiber in fibers), "active_profile": {str(slot): sum(fiber["activity_parity"] and fiber["slot"] == slot for fiber in fibers) for slot in (2, 3, 4)}, "fibers": fibers}, "catalog": catalog(fibers), "failures": [*failures, *rank_failures, *chronology_failures, *chord_failures]}
    if not direct["agreement"] or direct["semantic_failures"] or direct["extra_coordinates"]:
        result["failures"].append(f"direct:{cell.cell_id}")
    return result


def build_replay() -> dict[str, Any]:
    generator = load_module("independent_q_generator", GENERATOR_PATH)
    normalizer = load_module("independent_q_normalizer", NORMALIZER_PATH)
    approved = load_module("independent_q_approved", APPROVED_PATH)
    direct = load_module("independent_q_direct", DIRECT_PATH)
    occurrences = {row["order"]: row for row in generator.trace_ast()[1]}
    if {o: occurrences[o]["polarity"] for o in ACTIVE_OCCURRENCES} != EXPECTED_POLARITY:
        raise AssertionError("occurrence polarity")
    actions = {o: generator.parse_raw(row["quotient_prefix"]) for o, row in occurrences.items()}
    schemas, provenance, schema_failures, reference = build_schemas(approved, normalizer, generator, actions)
    templates, template_audit, template_failures = build_templates(approved, normalizer, generator, schemas)
    runtime = {"generator": generator, "normalizer": normalizer, "approved": approved, "direct": direct, "occurrences": occurrences, "actions": actions, "schemas": schemas, "provenance": provenance, "templates": templates}
    cells = [cell_result(runtime, cell) for cell in CELLS]
    raw_manifest = json.loads(RAW_MANIFEST_PATH.read_text())
    primary = json.loads(PRIMARY_MANIFEST_PATH.read_text())
    primary_cells = {cell["cell"]["id"]: cell for cell in primary["cells"]}
    failures = [*schema_failures, *template_failures, *(failure for cell in cells for failure in cell["failures"])]
    raw_profiles = {row["cell"]["id"]: row["collision"]["active_slot_profile"] for row in raw_manifest.get("cell_results", [])}
    raw_projection = {"catalog_digest": hashlib.sha256(canonical_json(raw_manifest.get("coordinate_schemas"))).hexdigest(), "profiles": raw_profiles}
    if raw_manifest.get("format") != "period-two-diagonal-pure-p-raw-provisional-v1" or raw_manifest.get("generation_failures") or cells[0]["catalog"] != raw_manifest.get("coordinate_schemas") or any(cell["catalog"] != cells[0]["catalog"] for cell in cells[1:]) or any(cell["collision"]["active_profile"] != raw_profiles.get(cell["cell"]["id"]) for cell in cells):
        failures.append("raw_catalog_semantics")
    projections = []
    for cell in cells:
        cell_id = cell["cell"]["id"]
        ours, theirs = semantic_projection(cell), semantic_projection(primary_cells[cell_id])
        match = canonical_json(ours) == canonical_json(theirs)
        projections.append({"cell": cell_id, "matches": match, "digest": hashlib.sha256(canonical_json(ours)).hexdigest()})
        if not match:
            failures.append(f"primary_semantic_projection:{cell_id}")
    occurrence_audit = [{"occurrence": o, "slot": occurrences[o]["slot"], "polarity": occurrences[o]["polarity"], "quotient_prefix": occurrences[o]["quotient_prefix"], "action": generator.lit(actions[o])} for o in ACTIVE_OCCURRENCES]
    return {"format": "period-two-diagonal-pure-p-quadratic-independent-all-power-replay-v2", "status": "provisional_pending_guarded_execution_and_sol_review", "nonclaim": "No producer scalar Q is read or assumed; this artifact alone proves no diagonal, unary-delta, period-two, AK3, stable-AC, or AC claim.", "source_bindings": source_bindings(), "cells": [{key: value for key, value in cell.items() if key not in ("catalog", "failures")} for cell in cells], "source_inventory": {"contexts": len(provenance), "distinct_source_rows": len({row['source_row_id'] for row in provenance}), "family_counts": dict(Counter(row["family"] for row in provenance)), "schema_count": len(schemas), "template_count": len(template_audit), "common_primitive": generator.lit(reference), "primitive_multiplier": 3, "signed_contexts": provenance, "occurrence_actions": occurrence_audit, "template_audit": template_audit}, "raw_manifest_projection_catalog_and_profile_only": raw_projection, "primary_semantic_projection_excluding_Q": projections, "generation_failures": failures}


def verification_failures(replay: dict[str, Any], expected: dict[str, Any] | None = None) -> list[str]:
    failures = []
    try:
        if replay["format"] != "period-two-diagonal-pure-p-quadratic-independent-all-power-replay-v2": failures.append("format")
        if replay["status"] != "provisional_pending_guarded_execution_and_sol_review": failures.append("status")
        if replay["generation_failures"]: failures.append("generation_failures")
        if "expected_Q" in replay: failures.append("producer_Q_forbidden")
        for name, path in binding_paths().items():
            if replay["source_bindings"][name]["sha256"] != sha256_path(path): failures.append(f"source_hash:{name}")
        if replay["source_bindings"]["theory_intervals"] != marked_intervals(): failures.append("source_hash:theory_intervals")
        inventory = replay["source_inventory"]
        if inventory["contexts"] != 46 or inventory["distinct_source_rows"] != 39 or inventory["family_counts"] != EXPECTED_FAMILIES or inventory["schema_count"] != 152 or inventory["template_count"] != 608 or inventory["primitive_multiplier"] != 3: failures.append("source_inventory")
        contexts = inventory["signed_contexts"]
        if len(contexts) != 46 or len({row["source_row_id"] for row in contexts}) != 39 or Counter(row["family"] for row in contexts) != Counter(EXPECTED_FAMILIES): failures.append("signed_context_inventory")
        for row in contexts:
            if row["source_coefficient"] != row["source_scale"] * row["incidence_sign"] or row["integral_coefficient"] != row["direction_sign"] * row["source_coefficient"]: failures.append(f"signed_context:{row['id']}")
            if row["power_offset"] != (0 if row["state"] == "old" else 1) or row["power_variable"] != ("h" if row["block"] == "P" else "i"): failures.append(f"source_offset:{row['id']}")
            if not isinstance(row["factor_order"], list) or not row["factor_order"]: failures.append(f"factor_order:{row['id']}")
        actions = inventory["occurrence_actions"]
        if [row["occurrence"] for row in actions] != list(ACTIVE_OCCURRENCES) or {row["occurrence"]: row["polarity"] for row in actions} != EXPECTED_POLARITY: failures.append("occurrence_actions")
        template_audit = inventory["template_audit"]
        if not template_audit or any(row["p_multiplier"] != 3 or not row["base_matches"] or not row["next_matches"] or not row["i4_matches"] or (row["cell_is_unbounded"] and (row["next_i"] != 4 or row["next_word"] != row["i4_word"])) for row in template_audit): failures.append("template_audit")
        raw_projection = replay["raw_manifest_projection_catalog_and_profile_only"]
        if len(raw_projection["catalog_digest"]) != 64 or raw_projection["profiles"] != {cell.cell_id: EXPECTED_PROFILE for cell in CELLS}: failures.append("raw_manifest_projection")
        if [cell["cell"]["id"] for cell in replay["cells"]] != [cell.cell_id for cell in CELLS]: failures.append("cell_predicate")
        for cell in replay["cells"]:
            cid = cell["cell"]["id"]
            expected_cell = next(item for item in CELLS if item.cell_id == cid)
            if cell["cell"] != {"id": expected_cell.cell_id, "i": "ge3" if expected_cell.value is None else expected_cell.value, "base_i": expected_cell.base_i}: failures.append(f"cell_predicate:{cid}")
            collision = cell["collision"]
            if collision["fiber_count"] != 44 or collision["active_count"] != 42 or collision["active_profile"] != EXPECTED_PROFILE: failures.append(f"collision:{cid}")
            inactive = [fiber for fiber in collision["fibers"] if not fiber["activity_parity"]]
            expected_inactive = [sorted([f"diag:long_pstar:new_segment:W:nu3:P:{position}:o+1", f"diag:short_w3:old:W:nu4:C:{18 + position}:o+1"]) for position in (0, 1)]
            if len(collision["fibers"]) != 44 or sorted(fiber["members"] for fiber in inactive) != sorted(expected_inactive) or any(fiber["integral_coefficient_sum"] != 0 for fiber in inactive): failures.append(f"inactive_fibers:{cid}")
            if any(witness["comparison"].get("order") != 0 or (witness["kind"] == "label" and not witness["canonical_equal"]) for fiber in collision["fibers"] for witness in fiber["collision_witnesses"]): failures.append(f"collision_witness:{cid}")
            if len(cell["tokens"]) != 96 or Counter(token["slot"] for token in cell["tokens"]) != Counter({0: 12, 2: 18, 3: 30, 4: 36}): failures.append(f"token_profile:{cid}")
            if cell["token_inventory"] != {"path": 84, "slot_zero": 12, "total": 96, "slot_profile": {0: 12, 2: 18, 3: 30, 4: 36}}: failures.append(f"token_inventory:{cid}")
            if any(token["polarity"] != EXPECTED_POLARITY[token["occurrence"]] for token in cell["tokens"]): failures.append(f"token_polarity:{cid}")
            ranks = cell["ranked_active_slots"]
            if {slot: len(rows) for slot, rows in ranks.items()} != EXPECTED_PROFILE: failures.append(f"rank_profile:{cid}")
            expected_adjacency = {(int(slot), left, right) for slot, rows in ranks.items() for left, right in zip(rows, rows[1:])}
            witnesses = cell["adjacent_witnesses"]
            actual_adjacency = {(row["slot"], row["left_coordinate"], row["right_coordinate"]) for row in witnesses}
            if len(witnesses) != 39 or actual_adjacency != expected_adjacency or any(not row["common_phase"] or row["comparison"].get("order") != -1 for row in witnesses): failures.append(f"rank:{cid}")
            if not cell["slot_zero_order"]["old_before_new"] or cell["slot_zero_order"]["comparison"].get("order") != -1: failures.append(f"slotzero:{cid}")
            chords = cell["chords"]
            if len(chords) != 48 or Counter(chord["kind"] for chord in chords) != Counter({"boundary": 12, "adjacency": 36}): failures.append(f"chords:{cid}")
            endpoints = [x for chord in chords for x in chord["endpoint_ids"]]
            if Counter(endpoints) != Counter({token["id"]: 1 for token in cell["tokens"]}): failures.append(f"chord_membership:{cid}")
            token_by_id = {token["id"]: token for token in cell["tokens"]}
            for chord in chords:
                if any(endpoint not in token_by_id for endpoint in chord["endpoint_ids"]):
                    failures.append(f"chord_endpoint:{cid}:{chord['id']}")
                    continue
                if chord["endpoint_occurrences"] != [token_by_id[endpoint]["occurrence"] for endpoint in chord["endpoint_ids"]]: failures.append(f"endpoint_map:{cid}:{chord['id']}")
                if not chord["endpoint_label_equal"] or chord["endpoint_label_comparison"].get("order") != 0: failures.append(f"chord_label:{cid}:{chord['id']}")
            if Counter(tuple(chord["occurrence_type"]) for chord in chords if chord["kind"] == "boundary") != EXPECTED_BOUNDARY or Counter(tuple(chord["occurrence_type"]) for chord in chords if chord["kind"] == "adjacency") != EXPECTED_ADJACENCY: failures.append(f"chord_census:{cid}")
            audit = cell["chord_pair_audit"]
            repeated = cell["repeated_chord_labels"]
            if audit["pair_count"] != 1128 or audit["equal_pairs"] != [list(REPEATED_PAIR)] or len(repeated) != 1 or not repeated[0]["same_label"] or not repeated[0]["nested"]: failures.append(f"label_pair_audit:{cid}")
            if cell["prefix_sweep"] != prefix_sweep(chords): failures.append(f"prefix:{cid}")
            direct = cell["direct_base_replay"]
            expected_occurrence_profile = {1: 9, 3: 2, 4: 2, 6: 9, 7: 2, 8: 2, 9: 15, 11: 2, 12: 2, 14: 15, 15: 18, 16: 18}
            ledger = direct["pair_ledger"]
            if direct["token_count"] != 96 or direct["production_token_count"] != 96 or direct["occurrence_profile"] != expected_occurrence_profile or direct["semantic_failures"] or direct["extra_coordinates"] or ledger["pair_count"] != 4560 or len(ledger["digest_sha256"]) != 64 or not direct["agreement"] or ledger["Q"] != direct["authoritative_quadratic"] or direct["authoritative_quadratic"] != cell["prefix_sweep"]["Q"]: failures.append(f"direct:{cid}")
        projections = replay["primary_semantic_projection_excluding_Q"]
        if [row["cell"] for row in projections] != [cell.cell_id for cell in CELLS] or not all(row["matches"] and len(row["digest"]) == 64 for row in projections): failures.append("primary_semantic_projection")
        recomputed = build_replay() if expected is None else expected
        if canonical_json(replay) != canonical_json(recomputed): failures.append("recomputed_replay_mismatch")
    except Exception as exc:
        failures.append(f"shape:{type(exc).__name__}:{exc}")
    return failures


def verify_replay(replay: dict[str, Any]) -> dict[str, Any]:
    failures = verification_failures(replay)
    if failures: raise AssertionError(failures[:32])
    return replay


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--check", action="store_true"); parser.parse_args()
    replay = verify_replay(build_replay())
    print(json.dumps({"format": replay["format"], "status": replay["status"], "cells": [{"id": cell["cell"]["id"], "Q": cell["prefix_sweep"]["Q"]} for cell in replay["cells"]]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
