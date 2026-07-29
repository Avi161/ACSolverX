from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from itertools import product
from pathlib import Path
from typing import Any

TOKEN_COUNT = 84
THRESHOLD_STATES = (0, 1, 2, None)
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
class Template:
    schema_id: str
    canonical_key: Any


@dataclass(frozen=True)
class CollisionFiber:
    collision_key: Any
    member_ids: tuple[str, ...]
    coefficients: tuple[int, ...]
    integral_sum: int
    parity: int
    label_equality_witness: Mapping[str, Any]
    active: bool


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True)


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
        coefficients = tuple(record_coefficients[member] for member in fiber["members"])
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
