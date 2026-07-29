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
SOURCE_PATHS = (
    ".scratch/period_two_raw_stream_manifest_generator.py",
    ".scratch/period_two_raw_stream_manifest.json",
    ".scratch/period_two_inverse_q_companion_checker.py",
    ".scratch/period_two_inverse_q_companion_manifest.json",
    ".scratch/period_two_new_new_aggregate_checker.py",
    ".scratch/period_two_new_new_aggregate_manifest.json",
    ".scratch/period_two_seven_family_covariance_checker.py",
    ".scratch/period_two_seven_family_covariance_manifest.json",
    ".scratch/period_two_old_new_cut_selector_theory.md",
    ".scratch/period_two_old_new_cut_endpoint_potential.md",
    ".scratch/period_two_intact_boundary_pumping_lemma.md",
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


def load_source_context() -> SourceContext:
    source_digests: dict[str, str] = {}
    for relative_path in SOURCE_PATHS:
        path = ROOT / relative_path
        if not path.is_file():
            raise FileNotFoundError(path)
        source_digests[relative_path] = _sha256_path(path)

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
    raw_rows = tuple(
        source_schema["V_rows"]
        + source_schema["W_rows"]
        + source_schema["anchor_rows"]
    )
    for row in raw_rows:
        if not row.get("domain") or not row.get("current_equality"):
            raise ValueError(f"raw row lacks typed provenance: {row.get('id')}")
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
                "integral_sum": fiber["integral_coefficient_sum"],
                "parity": fiber["activity_parity"],
                "canonical_module_schema": fiber["canonical_module_schema"],
                "slot": fiber["slot"],
            }
            for fiber in delta_fibers
        ]
    )
    unstable_cells = [
        cell_id
        for cell_id, fibers in collision_cells.items()
        if canonical_json(
            [
                {
                    "members": sorted(fiber["members"]),
                    "integral_sum": fiber["integral_coefficient_sum"],
                    "parity": fiber["activity_parity"],
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
    active_fibers = [fiber for fiber in delta_fibers if fiber["activity_parity"]]
    if len(active_fibers) != 36:
        raise ValueError("bound inverse-Q source does not contain 36 active fibers")
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

    tokens = []
    true_domain = {"op": "true"}
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
    collision_records = []
    for fiber_index, fiber in enumerate(delta_fibers):
        members = tuple(sorted(fiber["members"]))
        coefficients = tuple(record_coefficients[member] for member in members)
        if sum(coefficients) != fiber["integral_coefficient_sum"]:
            raise ValueError(f"fiber coefficient mismatch: {members}")
        collision_records.append(
            {
                "members": list(members),
                "coefficients": list(coefficients),
                "integral_sum": fiber["integral_coefficient_sum"],
                "parity": fiber["activity_parity"],
                "active": fiber["activity_parity"] != 0,
                "canonical_module_schema": fiber["canonical_module_schema"],
                "slot": fiber["slot"],
                "label_equality_witness": {
                    "equal": True,
                    "method": "bound_functional_equality_iff_canonical_key",
                    "source_cell": source_cell,
                },
            }
        )
        if not fiber["activity_parity"]:
            continue
        representative = members[0]
        row_key = representative.removesuffix(":delta0")
        for occurrence in occurrences_by_slot[fiber["slot"]]:
            occurrence_row = context.occurrences[occurrence]
            tokens.append(
                TokenRef(
                    token_id=f"b0:path:f{fiber_index:03d}:o{occurrence}",
                    family="b_path",
                    coefficient=fiber["integral_coefficient_sum"],
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
        "bound_cells": len(collision_cells),
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
