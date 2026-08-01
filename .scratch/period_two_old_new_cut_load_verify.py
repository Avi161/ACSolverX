from __future__ import annotations

import base64
import hashlib
import io
import json
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

TOKEN_COUNT = 84
PACKAGE_V2_FORMAT = "period-two-old-new-cut-package-v2"
LOGICAL_V1_FORMAT = "period-two-old-new-cut-load-v1"
CANONICAL_LINE_ENCODING = "canonical-json-ascii-lines-v1"
MASK_ENCODING = "uint84-be11-base64url-nopad-v1"
FAMILY_ORDER = ("fixed", "base", "singleton", "P", "C", "Q")
SHARD_ORDER = ("shared",) + FAMILY_ORDER
PACKAGE_BYTE_CAP = 100_000_000
MAX_CANONICAL_LINE_BYTES = 16_777_216
PRODUCTION_SCOPE = "production-full"
PREFLIGHT_SCOPE = "preflight-sample"
PRODUCTION_STATUS = "generated-awaiting-independent-replay"
PREFLIGHT_STATUS = "preflight-sample-not-a-certificate"
SOURCE_CELL_ORDER = "product-order-with-P-domain-filter"
SOURCE_BINDINGS_FORMAT = "task4-source-bindings-v1"
IDENTITY_CHUNK_SIZE = 4096
TEMPLATE_CATALOG_FORMAT = "task4-template-catalog-v2"
TEMPLATE_TYPED_ENCODING = "task4-typed-sha256-v1"
TEMPLATE_FIELD_ORDERS = {
    "schema": ["schema_id", "variables", "blocks"],
    "block": ["block_name", "word", "affine"],
    "cell": ["cell_id", "names", "states", "base_values"],
    "witness": [
        "terminal_full_letter",
        "terminal_c_deleted",
        "pumps",
    ],
    "pump": [
        "block_index",
        "base_copies",
        "slopes",
        "split_position",
        "left_copy_id",
        "right_copy_id",
        "left_core_offset",
        "right_core_offset",
    ],
}
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
ROOT_INDEX_FIELDS = (
    "format",
    "scope",
    "logical_v1_format",
    "canonical_encoding",
    "mask_encoding",
    "domain",
    "status",
    "shard_order",
    "shards",
    "shard_bytes_total",
    "emitted_summary",
    "full_summary",
    "source_bindings_sha256",
    "b_identity_digest",
    "template_catalogs",
    "root_sha256",
)
SHARD_DESCRIPTOR_FIELDS = (
    "role",
    "family",
    "path",
    "sha256",
    "total_bytes",
    "record_count",
    "record_counts",
)
SHARED_RECORD_FIELDS = {
    "shared_header": (
        "tag",
        "format",
        "scope",
        "logical_v1_format",
        "canonical_encoding",
        "mask_encoding",
        "domain",
        "status",
        "shard_order",
    ),
    "dependency": ("tag", "path", "sha256"),
    "source_bindings": ("tag", "value"),
    "b_identity": (
        "tag",
        "token_index",
        "token_id",
        "source_class",
        "coefficient",
        "slot",
        "occurrence",
        "polarity",
        "module_schema",
        "label_schema",
        "source_members",
    ),
    "b_coordinate": (
        "tag",
        "token_index",
        "source_class",
        "coordinate",
    ),
    "shared_footer": (
        "tag",
        "coordinate_count",
        "records_before_footer",
        "bytes_before_footer",
    ),
}
FAMILY_RECORD_FIELDS = {
    "family_header": (
        "tag",
        "family",
        "variables",
        "source_cell_count",
        "selected_old_indices",
        "old_load_count",
        "footprint_count",
        "bucket_class_count",
        "b_token_count",
        "comparison_methods",
        "chronologies",
        "histogram_key_fields",
        "template_field_orders",
        "source_cell_order",
    ),
    "old_load": (
        "tag",
        "old_index",
        "old_token_id",
        "coefficient",
        "source_members",
        "source_slot",
        "footprint_start",
        "footprint_count",
    ),
    "footprint": (
        "tag",
        "footprint_index",
        "old_index",
        "occurrence",
        "occurrence_slot",
        "polarity",
        "leaf",
        "module_schema",
        "label_schema",
    ),
    "bucket_class": (
        "tag",
        "b_source_class",
        "b_coordinate",
        "equality_exclusion",
        "module_method",
        "module_order",
        "chronology",
        "chronology_order",
        "label_method",
        "label_order",
        "contribution_bit",
    ),
    "load": (
        "tag",
        "old_index",
        "footprint_index",
        "bucket_class_index",
        "mask",
    ),
    "cell_footer": (
        "tag",
        "source_cell_index",
        "compact_cell_index",
        "cell_id",
        "odd_old_indices",
        "value",
        "load_record_count",
    ),
    "template_header": (
        "tag",
        "format",
        "typed_encoding",
        "family",
        "field_orders",
        "identity_order",
        "schema_count",
        "cell_count",
        "template_count",
        "witness_count",
    ),
    "template_schema": (
        "tag",
        "schema_index",
        "schema_id",
        "variables",
        "blocks",
    ),
    "template_cell": (
        "tag",
        "compact_cell_index",
        "cell_id",
        "names",
        "states",
        "base_values",
    ),
    "template_witness": (
        "tag",
        "witness_id",
        "terminal_full_letter",
        "terminal_c_deleted",
        "pumps",
    ),
    "template_identity_chunk": (
        "tag",
        "start_identity_index",
        "witness_id_list",
    ),
    "template_footer": (
        "tag",
        "identity_sha256",
        "replay_sha256",
        "catalog_sha256",
    ),
    "family_footer": (
        "tag",
        "source_cell_count",
        "old_load_count",
        "load_rows",
        "occurrence_loads",
        "comparisons",
        "records_before_footer",
        "bytes_before_footer",
    ),
}
COMPARISON_METHODS = (
    None,
    "strict_affine_length",
    "identical_pumped_blocks",
    "fixed_mismatch_after_pumped_prefix",
)
CHRONOLOGIES = (
    "fixed_vs_correction_literal_leaf_order",
    "distinct_occurrences_literal_AST_order",
    "equal_coordinate_excluded",
    "same_occurrence_increasing",
    "same_occurrence_decreasing",
)
_FAMILY_VARIABLES = {
    "fixed": ("a", "n"),
    "base": ("a", "n"),
    "singleton": ("a", "n"),
    "P": ("a", "h", "r"),
    "C": ("a", "n"),
    "Q": ("h", "k", "n"),
}
PACKAGE_V2_TEMPLATE_SUMMARY_FIELDS = (
    "format",
    "typed_encoding",
    "identity_order",
    "schema_count",
    "cell_count",
    "template_count",
    "witness_count",
    "identity_sha256",
    "replay_sha256",
    "catalog_sha256",
)
PACKAGE_V2_SUMMARY_FIELDS = (
    "load_rows",
    "total_load_rows",
    "footprint_sizes",
    "occurrence_loads",
    "total_occurrence_loads",
    "b_tokens_per_occurrence",
    "active_comparisons",
    "template_counts",
    "total_templates",
)
_HASH_PATTERN = re.compile(r"[0-9a-f]{64}")
_MASK_PATTERN = re.compile(r"[A-Za-z0-9_-]{15}")
GENERATION_PROJECTION_FORMAT = (
    "period-two-old-new-cut-generation-projection-v1"
)
VERIFICATION_PROJECTION_FORMAT = (
    "period-two-old-new-cut-verification-projection-v1"
)
GLOBAL_VERIFICATION_CHARGE_DOMAINS = (
    "root-index-descriptor-authentication",
    "shared-wire-stream-read-hash",
    "shared-source-reference-validation",
    "logical-v1-framing-finalization",
)
FAMILY_VERIFICATION_CHARGE_DOMAINS = (
    "family-wire-stream-read-hash",
    "comparison-replay",
    "template-replay",
    "logical-v1-canonical-fragment",
    "reference-validation",
)
GENERATION_PROJECTION_FIELDS = (
    "format",
    "family_order",
    "full_schema_count",
    "full_identity_count",
    "sampled_source_loads",
    "sampled_occurrence_loads",
    "sampled_comparisons",
    "source_catalog_precompute_ns",
    "shared_ns",
    "shared_bytes",
    "projected_index_ns",
    "projected_index_bytes",
    "families",
    "generation_ns_before_margin",
    "package_bytes_before_margin",
    "projected_generation_ns",
    "projected_package_bytes",
)
GENERATION_FAMILY_PROJECTION_FIELDS = (
    "family",
    "selected_old_indices",
    "selected_schema_indices",
    "tied_max_schema_ids",
    "full_schema_count",
    "full_comparisons",
    "sampled_comparisons",
    "sampled_two_pass_ns",
    "projected_two_pass_ns",
    "sampled_load_bucket_bytes",
    "projected_load_bucket_bytes",
    "sampled_load_record_count",
    "projected_load_record_count",
    "projected_bucket_class_count",
    "full_identity_count",
    "sampled_identity_count",
    "sampled_template_ns",
    "projected_template_ns",
    "sampled_template_bytes",
    "projected_template_bytes",
    "fixed_family_ns",
    "fixed_family_bytes",
)
_GENERATION_PROJECTED_ROOT_FIELDS = (
    "domain",
    "shared_dependency_count",
    "schema_profiles",
    "bucket_class_counts",
    "family_witness_counts",
)
_GENERATION_SELECTED_OLD_INDICES = {
    "fixed": (0, 8, 15, 23, 31, 38, 46, 54, 61, 69),
    "base": (0, 1),
    "singleton": (0,),
    "P": (0, 3, 5, 8, 10, 13, 16, 18, 21, 23, 26, 28, 31),
    "C": (0, 19, 38),
    "Q": (0, 15, 30, 46, 61, 76, 91),
}
_GENERATION_CENSUS = {
    "fixed": (192, 16, 3_072, 1_120, 160, 1_120, 160, 94_080, 13_440),
    "base": (128, 16, 2_048, 32, 32, 64, 64, 5_376, 5_376),
    "singleton": (129, 16, 2_064, 16, 16, 96, 96, 8_064, 8_064),
    "P": (218, 54, 11_772, 1_728, 702, 3_456, 1_404, 290_304, 117_936),
    "C": (239, 16, 3_824, 624, 48, 1_248, 96, 104_832, 8_064),
    "Q": (398, 64, 25_472, 5_888, 448, 11_776, 896, 989_184, 75_264),
}
_SHARED_DEPENDENCY_MAX = 11
_FAMILY_STREAM_RECORD_CAPS = {
    "fixed": {"bucket_class": 17, "load": 210, "template_witness": 2},
    "base": {"bucket_class": 19, "load": 31, "template_witness": 3},
    "singleton": {"bucket_class": 23, "load": 32, "template_witness": 5},
    "P": {"bucket_class": 29, "load": 82, "template_witness": 7},
    "C": {"bucket_class": 31, "load": 442, "template_witness": 11},
    "Q": {"bucket_class": 37, "load": 460, "template_witness": 13},
}


@dataclass(frozen=True)
class EngineeringVerificationFailure(RuntimeError):
    stage: str
    detail: str


@dataclass(frozen=True)
class ProofAttemptFailure(RuntimeError):
    stage: str
    detail: str


@dataclass(frozen=True)
class VerificationChargeInput:
    domain: str
    sampled_ns: int
    full_record_count: int
    sampled_record_count: int


@dataclass(frozen=True)
class VerificationChargeProjection:
    domain: str
    sampled_ns: int
    full_record_count: int
    sampled_record_count: int
    projected_ns: int


@dataclass(frozen=True)
class FamilyVerificationProjectionInput:
    family: str
    selected_old_indices: tuple[int, ...]
    selected_schema_indices: tuple[int, ...]
    full_old_load_count: int
    full_schema_count: int
    charges: tuple[VerificationChargeInput, ...]
    invariant_family_ns: int


@dataclass(frozen=True)
class FamilyVerificationProjection:
    family: str
    selected_old_indices: tuple[int, ...]
    selected_schema_indices: tuple[int, ...]
    full_old_load_count: int
    full_schema_count: int
    charges: tuple[VerificationChargeProjection, ...]
    invariant_family_ns: int
    verification_ns_before_margin: int


@dataclass(frozen=True)
class VerificationProjection:
    format: str
    family_order: tuple[str, ...]
    global_charges: tuple[VerificationChargeProjection, ...]
    invariant_ns: int
    families: tuple[FamilyVerificationProjection, ...]
    verification_ns_before_margin: int
    projected_verification_ns: int


@dataclass(frozen=True)
class IndependentReplayResult:
    run_id: str
    scope: str
    package_status: str
    status: str
    semantic_replay_complete: bool
    attestable: bool
    index_path: str
    index_sha256: str
    root_sha256: str
    logical_v1_sha256: str | None
    generation_projection_sha256: str
    verification_projection: VerificationProjection


@dataclass(frozen=True)
class _GenerationProjectionValidation:
    normalized: str
    sha256: str


@dataclass(frozen=True)
class _GenerationProjectionPremises:
    domain: str
    shared_dependency_count: int
    schema_profiles: Mapping[str, tuple[tuple[str, int], ...]]
    bucket_class_counts: Mapping[str, int]
    family_witness_counts: Mapping[str, int]


@dataclass(frozen=True)
class _AuthenticatedWireState:
    root: Mapping[str, Any]
    root_sha256: str
    premises: _GenerationProjectionPremises
    generation_projection_sha256: str | None


class PhaseMetrics:
    def __init__(self, *, enabled: bool = False) -> None:
        if type(enabled) is not bool:
            raise ValueError("metrics enabled flag must be boolean")
        self.enabled = enabled
        self._stages = {
            stage: 0.0
            for stage in (
                "encode_shared",
                "encode_family",
                "write_objects",
                "publish_index",
                "verify_package",
            )
        }
        tags = (*SHARED_RECORD_FIELDS, *FAMILY_RECORD_FIELDS, "root_index")
        self._record_counts = {tag: 0 for tag in tags}
        self._byte_counts = {tag: 0 for tag in tags}

    def add_stage(self, stage: str, elapsed: float) -> None:
        if stage not in self._stages:
            raise ValueError(f"unknown metrics stage: {stage}")
        if type(elapsed) not in (int, float) or elapsed < 0:
            raise ValueError("metrics elapsed value is invalid")
        if self.enabled:
            self._stages[stage] += elapsed

    def record(self, tag: str, byte_count: int) -> None:
        if tag not in self._record_counts:
            raise ValueError(f"unknown metrics tag: {tag}")
        if type(byte_count) is not int or byte_count < 0:
            raise ValueError("metrics byte count is invalid")
        if self.enabled:
            self._record_counts[tag] += 1
            self._byte_counts[tag] += byte_count

    def snapshot(self) -> dict[str, Any]:
        return {
            "format": "period-two-old-new-cut-phase-metrics-v1",
            "stages": dict(self._stages),
            "record_counts": dict(self._record_counts),
            "byte_counts": dict(self._byte_counts),
        }


class WireFormatError(ValueError):
    pass


def _exact_int(value: Any, name: str, *, minimum: int | None = None) -> int:
    if type(value) is not int:
        raise WireFormatError(f"{name} is not an exact integer")
    if minimum is not None and value < minimum:
        raise WireFormatError(f"{name} is below {minimum}")
    return value


def _exact_hash(value: Any, name: str) -> str:
    if not isinstance(value, str) or _HASH_PATTERN.fullmatch(value) is None:
        raise WireFormatError(f"{name} is not a lowercase SHA-256")
    return value


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )


def _validate_canonical_json_value(value: Any) -> None:
    if value is None or type(value) in (bool, int, str):
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            _validate_canonical_json_value(item)
        return
    if isinstance(value, Mapping):
        if not all(isinstance(key, str) for key in value):
            raise WireFormatError("canonical JSON mappings require string keys")
        for item in value.values():
            _validate_canonical_json_value(item)
        return
    raise WireFormatError(
        f"unsupported canonical JSON value: {type(value).__name__}"
    )


def canonical_json_line(value: Any) -> bytes:
    try:
        _validate_canonical_json_value(value)
        payload = json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
    except (TypeError, UnicodeError, ValueError) as error:
        raise WireFormatError("value is not canonical JSON") from error
    line = payload + b"\n"
    if len(line) > MAX_CANONICAL_LINE_BYTES:
        raise WireFormatError("canonical JSON line exceeds byte limit")
    return line


def _reject_json_float(token: str) -> Any:
    raise WireFormatError(f"floating JSON number is forbidden: {token}")


def _parse_json_int(token: str) -> int:
    if token == "-0":
        raise WireFormatError("negative zero is forbidden")
    return int(token)


def _reject_json_constant(token: str) -> Any:
    raise WireFormatError(f"JSON constant is forbidden: {token}")


def _object_without_duplicate_keys(
    pairs: Sequence[tuple[str, Any]],
) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise WireFormatError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _decode_canonical_line(line: bytes) -> Any:
    if b"\r" in line:
        raise WireFormatError("carriage return is forbidden")
    if line == b"\n":
        raise WireFormatError("blank canonical line is forbidden")
    if not line.endswith(b"\n"):
        raise WireFormatError("canonical line is missing final LF")
    try:
        text = line[:-1].decode("ascii")
    except UnicodeDecodeError as error:
        raise WireFormatError("canonical line is not ASCII") from error
    try:
        value = json.loads(
            text,
            parse_int=_parse_json_int,
            parse_float=_reject_json_float,
            parse_constant=_reject_json_constant,
            object_pairs_hook=_object_without_duplicate_keys,
        )
    except WireFormatError:
        raise
    except (json.JSONDecodeError, ValueError) as error:
        raise WireFormatError("canonical line is invalid JSON") from error
    if canonical_json_line(value) != line:
        raise WireFormatError("JSON line is not canonical")
    return value


def iter_canonical_json_lines(
    stream: Any, *, max_line_bytes: int = MAX_CANONICAL_LINE_BYTES
) -> Iterable[Any]:
    if type(max_line_bytes) is not int or not 1 <= max_line_bytes <= (
        MAX_CANONICAL_LINE_BYTES
    ):
        raise WireFormatError("invalid canonical line cap")
    while True:
        line = stream.readline(max_line_bytes + 1)
        if line == b"":
            return
        if not isinstance(line, bytes):
            raise WireFormatError("canonical stream must be binary")
        if len(line) > max_line_bytes:
            raise WireFormatError("canonical line exceeds byte cap")
        yield _decode_canonical_line(line)


def pack_mask(mask: int) -> str:
    _exact_int(mask, "mask", minimum=0)
    if mask >= 1 << TOKEN_COUNT:
        raise WireFormatError("mask is outside uint84")
    token = base64.b64encode(
        mask.to_bytes(11, "big"), altchars=b"-_"
    ).rstrip(b"=")
    return token.decode("ascii")


def unpack_mask(token: str) -> int:
    if not isinstance(token, str) or _MASK_PATTERN.fullmatch(token) is None:
        raise WireFormatError("mask token is not 15-character base64url")
    try:
        raw = base64.b64decode(
            (token + "=").encode("ascii"),
            altchars=b"-_",
            validate=True,
        )
    except (ValueError, UnicodeError) as error:
        raise WireFormatError("mask token has invalid base64url") from error
    if len(raw) != 11 or raw[0] & 0xF0:
        raise WireFormatError("mask token is outside uint84")
    value = int.from_bytes(raw, "big")
    if pack_mask(value) != token:
        raise WireFormatError("mask token is not canonical")
    return value


def validate_mask_partition(tokens: Sequence[str]) -> int:
    union = 0
    for token in tokens:
        mask = unpack_mask(token)
        if mask == 0:
            raise WireFormatError("histogram masks must be nonzero")
        if union & mask:
            raise WireFormatError("histogram masks overlap")
        union |= mask
    if union != (1 << TOKEN_COUNT) - 1:
        raise WireFormatError("histogram masks do not cover uint84")
    return union


def _typed_encode_into(update: Any, value: Any) -> None:
    if value is None:
        update(b"N")
        return
    if isinstance(value, bool):
        update(b"B\x01" if value else b"B\x00")
        return
    if isinstance(value, int):
        payload = str(value).encode("ascii")
        update(b"I" + len(payload).to_bytes(4, "big") + payload)
        return
    if isinstance(value, str):
        payload = value.encode("utf-8")
        update(b"S" + len(payload).to_bytes(4, "big") + payload)
        return
    if isinstance(value, (list, tuple)):
        update(b"L" + len(value).to_bytes(4, "big"))
        for item in value:
            _typed_encode_into(update, item)
        return
    if isinstance(value, Mapping):
        if not all(isinstance(key, str) for key in value):
            raise WireFormatError("typed mappings require string keys")
        keys = sorted(value, key=lambda key: key.encode("utf-8"))
        update(b"M" + len(keys).to_bytes(4, "big"))
        for key in keys:
            _typed_encode_into(update, key)
            _typed_encode_into(update, value[key])
        return
    raise WireFormatError(
        f"unsupported typed value: {type(value).__name__}"
    )


def _typed_encode(value: Any) -> bytes:
    payload = bytearray()
    _typed_encode_into(payload.extend, value)
    return bytes(payload)


def _compact_rolling_hashes(
    catalog: Mapping[str, Any],
) -> tuple[str, str]:
    identity_hasher = hashlib.sha256()
    replay_hasher = hashlib.sha256()
    shared = (
        catalog["format"],
        catalog["typed_encoding"],
        catalog["family"],
        catalog["field_orders"],
        catalog["identity_order"],
        catalog["schema_count"],
        catalog["cell_count"],
        catalog["template_count"],
        catalog["witness_count"],
        catalog["schema_table"],
        catalog["cell_table"],
        catalog["witness_table"],
    )
    for value in shared:
        _typed_encode_into(identity_hasher.update, value)
        _typed_encode_into(replay_hasher.update, value)
    cell_count = catalog["cell_count"]
    for identity_index, witness_id in enumerate(
        catalog["identity_witness_ids"]
    ):
        schema_index, cell_index = divmod(identity_index, cell_count)
        mapping = [schema_index, cell_index, witness_id]
        _typed_encode_into(identity_hasher.update, mapping)
        _typed_encode_into(replay_hasher.update, mapping)
        _typed_encode_into(
            replay_hasher.update, catalog["witness_table"][witness_id]
        )
    return identity_hasher.hexdigest(), replay_hasher.hexdigest()


def _source_stream(source: Any) -> tuple[Any, bool]:
    if isinstance(source, (bytes, bytearray)):
        return io.BytesIO(bytes(source)), True
    if hasattr(source, "readline"):
        return source, False
    raise WireFormatError("canonical source must be bytes or a binary stream")


def _validate_tagged_record(record: Any) -> None:
    if (
        not isinstance(record, list)
        or not record
        or not isinstance(record[0], str)
    ):
        raise WireFormatError("tagged record is not a nonempty array")


def _require_tag_width(
    record: Sequence[Any],
    tag: str,
    declarations: Mapping[str, Sequence[str]],
) -> None:
    if record[0] != tag:
        raise WireFormatError(f"expected {tag}, got {record[0]}")
    fields = declarations.get(tag)
    if fields is None or len(record) != len(fields):
        raise WireFormatError(f"{tag} width differs")


def _validate_root_summary(summary: Any, name: str) -> None:
    if not isinstance(summary, Mapping) or set(summary) != set(
        PACKAGE_V2_SUMMARY_FIELDS
    ):
        raise WireFormatError(f"{name} summary fields differ")
    family_maps = (
        "load_rows",
        "footprint_sizes",
        "occurrence_loads",
        "template_counts",
    )
    for field in family_maps:
        values = summary[field]
        if not isinstance(values, Mapping) or set(values) != set(FAMILY_ORDER):
            raise WireFormatError(f"{name} summary {field} families differ")
    for field in ("load_rows", "occurrence_loads", "template_counts"):
        for family, value in summary[field].items():
            _exact_int(value, f"{name} {field} {family}", minimum=0)
    for family, histogram in summary["footprint_sizes"].items():
        if not isinstance(histogram, Mapping):
            raise WireFormatError(
                f"{name} footprint histogram is invalid: {family}"
            )
        for footprint_size, count in histogram.items():
            if (
                not isinstance(footprint_size, str)
                or re.fullmatch(r"[1-9][0-9]*", footprint_size) is None
            ):
                raise WireFormatError(
                    f"{name} footprint-size key is invalid: {family}"
                )
            _exact_int(
                count,
                f"{name} footprint-size count {family}",
                minimum=1,
            )
    totals = {
        "total_load_rows": sum(summary["load_rows"].values()),
        "total_occurrence_loads": sum(summary["occurrence_loads"].values()),
        "total_templates": sum(summary["template_counts"].values()),
    }
    for field, expected in totals.items():
        if _exact_int(summary[field], f"{name} {field}", minimum=0) != expected:
            raise WireFormatError(f"{name} {field} differs")
    if summary["b_tokens_per_occurrence"] != TOKEN_COUNT:
        raise WireFormatError(f"{name} B token count differs")
    comparisons = _exact_int(
        summary["active_comparisons"],
        f"{name} active comparisons",
        minimum=0,
    )
    if comparisons != summary["total_occurrence_loads"] * TOKEN_COUNT:
        raise WireFormatError(f"{name} active comparison total differs")


def _validate_root_template_summary(summary: Any, family: str) -> None:
    if not isinstance(summary, Mapping) or set(summary) != set(
        PACKAGE_V2_TEMPLATE_SUMMARY_FIELDS
    ):
        raise WireFormatError(f"root template summary fields differ: {family}")
    if (
        summary["format"] != TEMPLATE_CATALOG_FORMAT
        or summary["typed_encoding"] != TEMPLATE_TYPED_ENCODING
        or summary["identity_order"] != "schema-major-cell-minor"
    ):
        raise WireFormatError(f"root template declarations differ: {family}")
    for field in (
        "schema_count",
        "cell_count",
        "template_count",
        "witness_count",
    ):
        _exact_int(summary[field], f"root {family} {field}", minimum=0)
    for field in ("identity_sha256", "replay_sha256", "catalog_sha256"):
        _exact_hash(summary[field], f"root {family} {field}")


def decode_root_index(source: Any) -> dict[str, Any]:
    stream, owned = _source_stream(source)
    iterator = iter_canonical_json_lines(stream)
    try:
        try:
            value = next(iterator)
        except StopIteration as error:
            raise WireFormatError(
                "root index must contain exactly one object line"
            ) from error
        try:
            next(iterator)
        except StopIteration:
            pass
        else:
            raise WireFormatError(
                "root index must contain exactly one object line"
            )
    finally:
        if owned:
            stream.close()
    if not isinstance(value, Mapping):
        raise WireFormatError("root index must contain exactly one object line")
    root = dict(value)
    if set(root) != set(ROOT_INDEX_FIELDS):
        raise WireFormatError("root index fields differ")
    if root["format"] != PACKAGE_V2_FORMAT:
        raise WireFormatError("root package format differs")
    if root["logical_v1_format"] != LOGICAL_V1_FORMAT:
        raise WireFormatError("root logical-v1 format differs")
    if root["canonical_encoding"] != CANONICAL_LINE_ENCODING:
        raise WireFormatError("root canonical encoding differs")
    if root["mask_encoding"] != MASK_ENCODING:
        raise WireFormatError("root mask encoding differs")
    expected_status = {
        PRODUCTION_SCOPE: PRODUCTION_STATUS,
        PREFLIGHT_SCOPE: PREFLIGHT_STATUS,
    }.get(root["scope"])
    if expected_status is None or root["status"] != expected_status:
        raise WireFormatError("root scope/status pair differs")
    if not isinstance(root["domain"], str) or not root["domain"]:
        raise WireFormatError("root domain is invalid")
    if root["shard_order"] != list(SHARD_ORDER):
        raise WireFormatError("root shard order differs")
    shards = root["shards"]
    if not isinstance(shards, list) or len(shards) != len(SHARD_ORDER):
        raise WireFormatError("root shard descriptor count differs")
    for position, (descriptor, family) in enumerate(
        zip(shards, (None,) + FAMILY_ORDER)
    ):
        if not isinstance(descriptor, Mapping) or set(descriptor) != set(
            SHARD_DESCRIPTOR_FIELDS
        ):
            raise WireFormatError("shard descriptor fields differ")
        expected_role = "shared" if family is None else "family"
        if (
            descriptor["role"] != expected_role
            or descriptor["family"] != family
        ):
            raise WireFormatError(f"shard role differs at {position}")
        digest = _exact_hash(descriptor["sha256"], "descriptor sha256")
        if descriptor["path"] != f"objects/{digest}.jsonl":
            raise WireFormatError("descriptor path is not content addressed")
        _exact_int(descriptor["total_bytes"], "descriptor bytes", minimum=1)
        record_count = _exact_int(
            descriptor["record_count"], "descriptor records", minimum=1
        )
        declarations = (
            SHARED_RECORD_FIELDS if family is None else FAMILY_RECORD_FIELDS
        )
        counts = descriptor["record_counts"]
        if not isinstance(counts, Mapping) or set(counts) != set(declarations):
            raise WireFormatError("descriptor record-count tags differ")
        for tag, count in counts.items():
            _exact_int(count, f"{tag} count", minimum=0)
        if sum(counts.values()) != record_count:
            raise WireFormatError("descriptor record counts do not sum")
    shard_total = _exact_int(
        root["shard_bytes_total"], "root shard bytes", minimum=1
    )
    if shard_total != sum(item["total_bytes"] for item in shards):
        raise WireFormatError("root shard byte total differs")
    if shard_total > PACKAGE_BYTE_CAP:
        raise WireFormatError("root shard bytes exceed package cap")
    _exact_hash(root["source_bindings_sha256"], "source bindings sha256")
    _exact_hash(root["b_identity_digest"], "B identity digest")
    catalogs = root["template_catalogs"]
    if not isinstance(catalogs, Mapping) or set(catalogs) != set(FAMILY_ORDER):
        raise WireFormatError("root template catalog families differ")
    for family, summary in catalogs.items():
        _validate_root_template_summary(summary, family)
    _validate_root_summary(root["emitted_summary"], "emitted")
    _validate_root_summary(root["full_summary"], "full")
    if root["scope"] == PRODUCTION_SCOPE and (
        root["emitted_summary"] != root["full_summary"]
    ):
        raise WireFormatError("production emitted/full summaries differ")
    payload = {
        key: value for key, value in root.items() if key != "root_sha256"
    }
    expected_hash = hashlib.sha256(canonical_json_line(payload)).hexdigest()
    if _exact_hash(root["root_sha256"], "root sha256") != expected_hash:
        raise WireFormatError("root hash differs")
    return root


def decode_shared_records(source: Any) -> dict[str, Any]:
    stream, owned = _source_stream(source)
    iterator = iter_canonical_json_lines(stream)
    try:
        try:
            header = next(iterator)
        except StopIteration as error:
            raise WireFormatError("shared shard is empty") from error
        _validate_tagged_record(header)
        _require_tag_width(header, "shared_header", SHARED_RECORD_FIELDS)
        expected_status = {
            PRODUCTION_SCOPE: PRODUCTION_STATUS,
            PREFLIGHT_SCOPE: PREFLIGHT_STATUS,
        }.get(header[2])
        if (
            header[1] != PACKAGE_V2_FORMAT
            or header[3] != LOGICAL_V1_FORMAT
            or header[4] != CANONICAL_LINE_ENCODING
            or header[5] != MASK_ENCODING
            or expected_status is None
            or header[7] != expected_status
            or header[8] != list(SHARD_ORDER)
        ):
            raise WireFormatError("shared header payload differs")
        if not isinstance(header[6], str) or not header[6]:
            raise WireFormatError("shared domain is invalid")
        if header[2] == PRODUCTION_SCOPE:
            raise WireFormatError(
                "production streaming replay is deferred to Task 3"
            )
        records = [header]
        for record in iterator:
            _validate_tagged_record(record)
            records.append(record)
    finally:
        if owned:
            stream.close()
    if len(records) < 3:
        raise WireFormatError("shared shard is incomplete")
    cursor = 1
    dependencies = {}
    dependency_paths = []
    while cursor < len(records) and records[cursor][0] == "dependency":
        row = records[cursor]
        _require_tag_width(row, "dependency", SHARED_RECORD_FIELDS)
        path, digest = row[1:]
        if not isinstance(path, str) or not path or not path.isascii():
            raise WireFormatError("dependency path is invalid")
        if path in dependencies:
            raise WireFormatError("dependency path repeats")
        dependencies[path] = _exact_hash(digest, "dependency sha256")
        dependency_paths.append(path)
        cursor += 1
    if dependency_paths != sorted(dependency_paths):
        raise WireFormatError("dependencies are not in ASCII order")
    source_row = records[cursor]
    _require_tag_width(source_row, "source_bindings", SHARED_RECORD_FIELDS)
    source_bindings = source_row[1]
    if not isinstance(source_bindings, Mapping) or set(source_bindings) != {
        "format",
        "old",
        "b",
        "sha256",
    }:
        raise WireFormatError("source-binding fields differ")
    if source_bindings["format"] != SOURCE_BINDINGS_FORMAT:
        raise WireFormatError("source-binding format differs")
    source_payload = {
        key: value
        for key, value in source_bindings.items()
        if key != "sha256"
    }
    if source_bindings["sha256"] != hashlib.sha256(
        _canonical_json(source_payload).encode("ascii")
    ).hexdigest():
        raise WireFormatError("source-binding digest differs")
    cursor += 1
    identities = []
    while cursor < len(records) and records[cursor][0] == "b_identity":
        row = records[cursor]
        _require_tag_width(row, "b_identity", SHARED_RECORD_FIELDS)
        if _exact_int(row[1], "B token index", minimum=0) != len(identities):
            raise WireFormatError("B identity indices are not consecutive")
        if not isinstance(row[2], str) or not isinstance(row[3], str):
            raise WireFormatError("B identity string field is invalid")
        _exact_int(row[4], "B coefficient")
        for name, value in (
            ("B slot", row[5]),
            ("B occurrence", row[6]),
            ("B polarity", row[7]),
        ):
            if value is not None:
                _exact_int(value, name)
        if not isinstance(row[8], str) or not isinstance(row[9], str):
            raise WireFormatError("B schema reference is invalid")
        if not isinstance(row[10], list) or not all(
            isinstance(member, str) for member in row[10]
        ):
            raise WireFormatError("B source members are invalid")
        identities.append(row)
        cursor += 1
    coordinates = []
    while cursor < len(records) and records[cursor][0] == "b_coordinate":
        row = records[cursor]
        _require_tag_width(row, "b_coordinate", SHARED_RECORD_FIELDS)
        token_index = _exact_int(
            row[1], "B coordinate index", minimum=0
        )
        if token_index != len(coordinates):
            raise WireFormatError("B coordinate indices are not consecutive")
        if token_index >= len(identities) or row[2] != identities[token_index][3]:
            raise WireFormatError("B coordinate identity reference differs")
        if not isinstance(row[3], list):
            raise WireFormatError("B coordinate is not an array")
        coordinates.append(row)
        cursor += 1
    if len(coordinates) != len(identities):
        raise WireFormatError("B identity/coordinate counts differ")
    if len(identities) != TOKEN_COUNT:
        raise WireFormatError("shared B token count differs")
    if cursor != len(records) - 1:
        raise WireFormatError("shared records are out of order")
    footer = records[cursor]
    _require_tag_width(footer, "shared_footer", SHARED_RECORD_FIELDS)
    if _exact_int(footer[1], "coordinate count", minimum=0) != len(
        coordinates
    ):
        raise WireFormatError("shared coordinate count differs")
    if _exact_int(footer[2], "shared prefix records", minimum=0) != len(
        records
    ) - 1:
        raise WireFormatError("shared prefix record count differs")
    prefix_bytes = sum(len(canonical_json_line(row)) for row in records[:-1])
    if _exact_int(footer[3], "shared prefix bytes", minimum=0) != prefix_bytes:
        raise WireFormatError("shared prefix byte count differs")
    return {
        "records": tuple(tuple(record) for record in records),
        "header": tuple(header),
        "dependencies": dependencies,
        "source_bindings": dict(source_bindings),
        "identities": tuple(tuple(row) for row in identities),
        "coordinates": tuple(tuple(row) for row in coordinates),
    }


def _template_catalog_from_tagged_rows(
    template_header: Sequence[Any],
    schema_rows: Sequence[Sequence[Any]],
    cell_rows: Sequence[Sequence[Any]],
    witness_rows: Sequence[Sequence[Any]],
    identity_rows: Sequence[Sequence[Any]],
    template_footer: Sequence[Any],
) -> dict[str, Any]:
    return {
        "format": template_header[1],
        "typed_encoding": template_header[2],
        "family": template_header[3],
        "field_orders": template_header[4],
        "identity_order": template_header[5],
        "schema_count": template_header[6],
        "cell_count": template_header[7],
        "template_count": template_header[8],
        "witness_count": template_header[9],
        "schema_table": [
            [row[2], row[3], row[4]] for row in schema_rows
        ],
        "cell_table": [
            [row[2], row[3], row[4], row[5]] for row in cell_rows
        ],
        "witness_table": [
            [row[2], row[3], row[4]] for row in witness_rows
        ],
        "identity_witness_ids": [
            witness_id
            for row in identity_rows
            for witness_id in row[2]
        ],
        "identity_sha256": template_footer[1],
        "replay_sha256": template_footer[2],
        "catalog_sha256": template_footer[3],
    }


def _validate_template_schema_rows(rows: Sequence[Any]) -> None:
    identifiers = []
    for row in rows:
        if not isinstance(row, list) or len(row) != 3:
            raise WireFormatError("template schema row width differs")
        schema_id, variables, blocks = row
        if (
            not isinstance(schema_id, str)
            or not schema_id
            or not schema_id.isascii()
        ):
            raise WireFormatError("template schema ID is invalid")
        identifiers.append(schema_id)
        if not isinstance(variables, list) or not all(
            isinstance(variable, str) for variable in variables
        ):
            raise WireFormatError("template schema variables are invalid")
        if not isinstance(blocks, list):
            raise WireFormatError("template blocks are invalid")
        for block in blocks:
            if not isinstance(block, list) or len(block) != 3:
                raise WireFormatError("template block width differs")
            name, word, affine = block
            if not isinstance(name, str) or not name:
                raise WireFormatError("template block name is invalid")
            if not isinstance(word, list) or not all(
                type(letter) is int for letter in word
            ):
                raise WireFormatError("template block word is invalid")
            if affine is not None and (
                not isinstance(affine, list)
                or not all(type(value) is int for value in affine)
                or len(affine) != len(variables) + 1
            ):
                raise WireFormatError("template block affine is invalid")
    if identifiers != sorted(set(identifiers)):
        raise WireFormatError("template schemas are not strictly ASCII sorted")


def _validate_template_cell_rows(rows: Sequence[Any]) -> None:
    identifiers = []
    for row in rows:
        if not isinstance(row, list) or len(row) != 4:
            raise WireFormatError("template cell row width differs")
        cell_id, names, states, base_values = row
        if (
            not isinstance(cell_id, str)
            or not cell_id
            or not cell_id.isascii()
        ):
            raise WireFormatError("template cell ID is invalid")
        identifiers.append(cell_id)
        if not isinstance(names, list) or not all(
            isinstance(name, str) for name in names
        ):
            raise WireFormatError("template cell names are invalid")
        if not isinstance(states, list) or not all(
            state is None or type(state) is int for state in states
        ):
            raise WireFormatError("template cell states are invalid")
        if any(
            state is not None and state not in (0, 1, 2)
            for state in states
        ):
            raise WireFormatError("template cell state is outside threshold")
        if not isinstance(base_values, list) or not all(
            type(value) is int for value in base_values
        ):
            raise WireFormatError("template cell bases are invalid")
        if not (len(names) == len(states) == len(base_values)):
            raise WireFormatError("template cell coordinate widths differ")
        if any(
            base != (3 if state is None else state)
            for state, base in zip(states, base_values)
        ):
            raise WireFormatError("template cell base differs from state")
    if identifiers != sorted(set(identifiers)):
        raise WireFormatError("template cells are not strictly ASCII sorted")


def _validate_template_witness_rows(rows: Sequence[Any]) -> None:
    for witness in rows:
        if not isinstance(witness, list) or len(witness) != 3:
            raise WireFormatError("template witness width differs")
        terminal, terminal_deleted, pumps = witness
        if terminal is not None and type(terminal) is not int:
            raise WireFormatError("template terminal is invalid")
        if not isinstance(terminal_deleted, bool):
            raise WireFormatError("template deletion flag is invalid")
        if terminal_deleted != (terminal == 1):
            raise WireFormatError("template deletion branch differs")
        if not isinstance(pumps, list):
            raise WireFormatError("template pumps are invalid")
        for pump in pumps:
            if not isinstance(pump, list) or len(pump) != 8:
                raise WireFormatError("template pump width differs")
            for index in (0, 1, 3, 4, 5, 6, 7):
                _exact_int(pump[index], "template pump integer", minimum=0)
            if not isinstance(pump[2], list) or not all(
                type(slope) is int and slope >= 0 for slope in pump[2]
            ):
                raise WireFormatError("template pump slopes are invalid")
            if pump[3] == 0 or pump[5] != pump[4] + 1:
                raise WireFormatError("template pump boundary differs")


def _validate_v2_template_catalog(catalog: Mapping[str, Any]) -> None:
    expected_fields = {
        "format",
        "typed_encoding",
        "family",
        "field_orders",
        "identity_order",
        "schema_count",
        "cell_count",
        "template_count",
        "witness_count",
        "schema_table",
        "cell_table",
        "witness_table",
        "identity_witness_ids",
        "identity_sha256",
        "replay_sha256",
        "catalog_sha256",
    }
    if set(catalog) != expected_fields:
        raise WireFormatError("template catalog fields differ")
    if catalog["format"] != TEMPLATE_CATALOG_FORMAT:
        raise WireFormatError("template catalog format differs")
    if catalog["typed_encoding"] != TEMPLATE_TYPED_ENCODING:
        raise WireFormatError("template typed encoding differs")
    if catalog["field_orders"] != TEMPLATE_FIELD_ORDERS:
        raise WireFormatError("template field orders differ")
    if catalog["identity_order"] != "schema-major-cell-minor":
        raise WireFormatError("template identity order differs")
    for name in (
        "schema_count",
        "cell_count",
        "template_count",
        "witness_count",
    ):
        _exact_int(catalog[name], f"template {name}", minimum=0)
    if catalog["schema_count"] != len(catalog["schema_table"]):
        raise WireFormatError("template schema count differs")
    if catalog["cell_count"] != len(catalog["cell_table"]):
        raise WireFormatError("template cell count differs")
    if catalog["witness_count"] != len(catalog["witness_table"]):
        raise WireFormatError("template witness count differs")
    expected_templates = catalog["schema_count"] * catalog["cell_count"]
    identities = catalog["identity_witness_ids"]
    if (
        catalog["template_count"] != expected_templates
        or not isinstance(identities, list)
        or len(identities) != expected_templates
    ):
        raise WireFormatError("template identity count differs")
    _validate_template_schema_rows(catalog["schema_table"])
    _validate_template_cell_rows(catalog["cell_table"])
    _validate_template_witness_rows(catalog["witness_table"])
    if any(
        type(witness_id) is not int
        or witness_id < 0
        or witness_id >= catalog["witness_count"]
        for witness_id in identities
    ):
        raise WireFormatError("template witness reference is invalid")
    if set(identities) != set(range(catalog["witness_count"])):
        raise WireFormatError("template witness table has unused rows")
    if expected_templates == 0 and any(
        catalog[name]
        for name in (
            "schema_table",
            "cell_table",
            "witness_table",
            "identity_witness_ids",
        )
    ):
        raise WireFormatError("empty template catalog has table rows")
    first_seen = {}
    for witness_id in identities:
        key = _typed_encode(catalog["witness_table"][witness_id])
        prior = first_seen.get(key)
        if prior is None:
            if witness_id != len(first_seen):
                raise WireFormatError("template witnesses are not first-seen")
            first_seen[key] = witness_id
        elif witness_id != prior:
            raise WireFormatError("template witness value repeats")
    cell_count = catalog["cell_count"]
    for identity_index, witness_id in enumerate(identities):
        schema_index, cell_index = divmod(identity_index, cell_count)
        _, variables, blocks = catalog["schema_table"][schema_index]
        _, names, states, base_values = catalog["cell_table"][cell_index]
        if variables != names:
            raise WireFormatError("template catalog variable domains differ")
        expected_pumps = {}
        for block_index, (_, _, affine) in enumerate(blocks):
            if affine is None:
                continue
            slopes = [
                coefficient if state is None else 0
                for coefficient, state in zip(affine[:-1], states)
            ]
            if any(slopes):
                expected_pumps[block_index] = (
                    slopes,
                    sum(
                        coefficient * value
                        for coefficient, value in zip(
                            affine[:-1], base_values
                        )
                    )
                    + affine[-1],
                )
        pumps = catalog["witness_table"][witness_id][2]
        pump_indices = [pump[0] for pump in pumps]
        if (
            len(set(pump_indices)) != len(pump_indices)
            or set(pump_indices) != set(expected_pumps)
        ):
            raise WireFormatError("template catalog pump coverage differs")
        split_positions = [pump[3] for pump in pumps]
        if (
            len(set(split_positions)) != len(split_positions)
            or split_positions != sorted(split_positions)
        ):
            raise WireFormatError("template catalog pump splits differ")
        for pump in pumps:
            block_index = pump[0]
            if block_index >= len(blocks):
                raise WireFormatError(
                    "template catalog pump block reference is out of range"
                )
            _, word, _ = blocks[block_index]
            slopes, base_copies = expected_pumps[block_index]
            if pump[1] != base_copies or pump[2] != slopes:
                raise WireFormatError("template catalog pump affine data differs")
            if pump[5] >= pump[1]:
                raise WireFormatError("template catalog pump copy is out of range")
            if not word or pump[6] != len(word) - 1 or pump[7] != 0:
                raise WireFormatError("template catalog pump offsets differ")
    identity_digest, replay_digest = _compact_rolling_hashes(catalog)
    if catalog["identity_sha256"] != identity_digest:
        raise WireFormatError("template identity digest differs")
    if catalog["replay_sha256"] != replay_digest:
        raise WireFormatError("template replay digest differs")
    payload = {
        key: value
        for key, value in catalog.items()
        if key != "catalog_sha256"
    }
    expected_catalog_digest = hashlib.sha256(
        _canonical_json(payload).encode("ascii")
    ).hexdigest()
    if catalog["catalog_sha256"] != expected_catalog_digest:
        raise WireFormatError("template catalog digest differs")


def _bucket_key_from_rows(
    footprint: Sequence[Any], bucket_class: Sequence[Any]
) -> dict[str, Any]:
    return {
        "old_occurrence": footprint[3],
        "old_leaf": footprint[6],
        "b_source_class": bucket_class[1],
        "b_coordinate": bucket_class[2],
        "equality_exclusion": bucket_class[3],
        "old_polarity": footprint[5],
        "module_method": bucket_class[4],
        "module_order": bucket_class[5],
        "chronology": bucket_class[6],
        "chronology_order": bucket_class[7],
        "label_method": bucket_class[8],
        "label_order": bucket_class[9],
        "contribution_bit": bucket_class[10],
    }


def _validate_family_header(header: Sequence[Any], family: str) -> None:
    _require_tag_width(header, "family_header", FAMILY_RECORD_FIELDS)
    if header[1] != family:
        raise WireFormatError("family header name differs")
    if not isinstance(header[2], list) or not all(
        isinstance(name, str) for name in header[2]
    ):
        raise WireFormatError("family variables are invalid")
    for index, name in (
        (3, "source cell count"),
        (5, "old load count"),
        (6, "footprint count"),
        (7, "bucket class count"),
        (8, "B token count"),
    ):
        _exact_int(header[index], name, minimum=0)
    if header[8] != TOKEN_COUNT:
        raise WireFormatError("family B token count differs")
    selected = header[4]
    if (
        not isinstance(selected, list)
        or any(type(index) is not int or index < 0 for index in selected)
        or selected != sorted(set(selected))
    ):
        raise WireFormatError("selected old indices are invalid")
    if any(index >= header[5] for index in selected):
        raise WireFormatError("selected old index is out of range")
    if header[9] != list(COMPARISON_METHODS):
        raise WireFormatError("comparison method declaration differs")
    if header[10] != list(CHRONOLOGIES):
        raise WireFormatError("chronology declaration differs")
    if header[11] != list(HISTOGRAM_KEY_FIELDS):
        raise WireFormatError("histogram field declaration differs")
    if header[12] != TEMPLATE_FIELD_ORDERS:
        raise WireFormatError("template field declaration differs")
    if header[13] != SOURCE_CELL_ORDER:
        raise WireFormatError("source-cell order declaration differs")


def decode_family_records(
    source: Any, *, expected_family: str, scope: str
) -> dict[str, Any]:
    if expected_family not in FAMILY_ORDER:
        raise WireFormatError("unknown family shard")
    if scope not in {PREFLIGHT_SCOPE, PRODUCTION_SCOPE}:
        raise WireFormatError("unknown package scope")
    stream, owned = _source_stream(source)
    iterator = iter_canonical_json_lines(stream)
    try:
        try:
            header = next(iterator)
        except StopIteration as error:
            raise WireFormatError("family shard is empty") from error
        _validate_tagged_record(header)
        _validate_family_header(header, expected_family)
        if (
            scope == PRODUCTION_SCOPE
            and header[4] != list(range(header[5]))
        ):
            raise WireFormatError("production old indices are not complete")
        if scope == PRODUCTION_SCOPE:
            raise WireFormatError(
                "production streaming replay is deferred to Task 3"
            )
        records = [header]
        for record in iterator:
            _validate_tagged_record(record)
            records.append(record)
    finally:
        if owned:
            stream.close()
    if len(records) < 4:
        raise WireFormatError("family shard is incomplete")
    _validate_family_header(header, expected_family)
    selected_old_indices = header[4]
    selected_old_set = set(selected_old_indices)
    if (
        scope == PRODUCTION_SCOPE
        and selected_old_indices != list(range(header[5]))
    ):
        raise WireFormatError("production old indices are not complete")
    cursor = 1

    old_rows = []
    for old_index in range(header[5]):
        if cursor >= len(records):
            raise WireFormatError("old-load table is truncated")
        row = records[cursor]
        _require_tag_width(row, "old_load", FAMILY_RECORD_FIELDS)
        if _exact_int(row[1], "old index", minimum=0) != old_index:
            raise WireFormatError("old-load indices are not consecutive")
        if not isinstance(row[2], str) or not row[2]:
            raise WireFormatError("old token ID is invalid")
        _exact_int(row[3], "old coefficient")
        if not isinstance(row[4], list) or not all(
            isinstance(member, str) for member in row[4]
        ):
            raise WireFormatError("old source members are invalid")
        if expected_family == "fixed":
            if row[5] is not None:
                raise WireFormatError("fixed old source slot is not null")
        else:
            _exact_int(row[5], "old source slot")
        _exact_int(row[6], "footprint start", minimum=0)
        _exact_int(row[7], "old footprint count", minimum=1)
        old_rows.append(row)
        cursor += 1

    footprint_rows = []
    for footprint_index in range(header[6]):
        if cursor >= len(records):
            raise WireFormatError("footprint table is truncated")
        row = records[cursor]
        _require_tag_width(row, "footprint", FAMILY_RECORD_FIELDS)
        if _exact_int(
            row[1], "footprint index", minimum=0
        ) != footprint_index:
            raise WireFormatError("footprint indices are not consecutive")
        old_index = _exact_int(row[2], "footprint old index", minimum=0)
        if old_index >= len(old_rows):
            raise WireFormatError("footprint old reference is out of range")
        if expected_family == "fixed":
            if (row[3], row[4], row[5], row[7]) != (
                None,
                None,
                None,
                None,
            ):
                raise WireFormatError("fixed footprint null domain differs")
        else:
            _exact_int(row[3], "footprint occurrence")
            _exact_int(row[4], "footprint occurrence slot")
            _exact_int(row[5], "footprint polarity")
            if not isinstance(row[7], str):
                raise WireFormatError("footprint module schema is invalid")
        _exact_int(row[6], "footprint leaf", minimum=0)
        if not isinstance(row[8], str) or not row[8]:
            raise WireFormatError("footprint label schema is invalid")
        footprint_rows.append(row)
        cursor += 1
    expected_footprint = 0
    for old_index, old_row in enumerate(old_rows):
        if old_row[6] != expected_footprint:
            raise WireFormatError("footprint intervals are not contiguous")
        stop = old_row[6] + old_row[7]
        if any(
            footprint_rows[index][2] != old_index
            for index in range(old_row[6], stop)
        ):
            raise WireFormatError("footprint interval owner differs")
        expected_footprint = stop
    if expected_footprint != len(footprint_rows):
        raise WireFormatError("footprint intervals do not cover the table")

    bucket_rows = []
    for _ in range(header[7]):
        if cursor >= len(records):
            raise WireFormatError("bucket-class table is truncated")
        row = records[cursor]
        _require_tag_width(row, "bucket_class", FAMILY_RECORD_FIELDS)
        if not isinstance(row[1], str) or not isinstance(row[2], list):
            raise WireFormatError("bucket B coordinate is invalid")
        if not isinstance(row[3], bool):
            raise WireFormatError("bucket equality exclusion is invalid")
        for method, order, label in (
            (row[4], row[5], "module"),
            (row[8], row[9], "label"),
        ):
            if method not in COMPARISON_METHODS:
                raise WireFormatError(f"bucket {label} method differs")
            if method is None:
                if order is not None:
                    raise WireFormatError(f"bucket {label} null order differs")
            else:
                _exact_int(order, f"bucket {label} order")
        if row[6] not in CHRONOLOGIES:
            raise WireFormatError("bucket chronology differs")
        _exact_int(row[7], "bucket chronology order")
        if row[10] not in (0, 1) or type(row[10]) is not int:
            raise WireFormatError("bucket contribution bit differs")
        bucket_rows.append(row)
        cursor += 1
    bucket_keys = [_canonical_json(row[1:]) for row in bucket_rows]
    if bucket_keys != sorted(set(bucket_keys)):
        raise WireFormatError("bucket classes are not canonical")

    cell_groups = []
    for source_cell_index in range(header[3]):
        load_rows = []
        while cursor < len(records) and records[cursor][0] == "load":
            row = records[cursor]
            _require_tag_width(row, "load", FAMILY_RECORD_FIELDS)
            old_index = _exact_int(row[1], "load old index", minimum=0)
            footprint_index = _exact_int(
                row[2], "load footprint index", minimum=0
            )
            bucket_index = _exact_int(
                row[3], "load bucket-class index", minimum=0
            )
            if old_index >= len(old_rows):
                raise WireFormatError("load old reference is out of range")
            if old_index not in selected_old_set:
                raise WireFormatError("load references an unselected old index")
            if footprint_index >= len(footprint_rows):
                raise WireFormatError("load footprint reference is out of range")
            if footprint_rows[footprint_index][2] != old_index:
                raise WireFormatError("load footprint owner differs")
            if bucket_index >= len(bucket_rows):
                raise WireFormatError("load bucket reference is out of range")
            if unpack_mask(row[4]) == 0:
                raise WireFormatError("load mask is zero")
            load_rows.append(row)
            cursor += 1
        if cursor >= len(records):
            raise WireFormatError("cell footer is missing")
        footer = records[cursor]
        _require_tag_width(footer, "cell_footer", FAMILY_RECORD_FIELDS)
        if _exact_int(
            footer[1], "source cell index", minimum=0
        ) != source_cell_index:
            raise WireFormatError("source cell indices are not consecutive")
        _exact_int(footer[2], "compact cell index", minimum=0)
        if not isinstance(footer[3], str) or not footer[3]:
            raise WireFormatError("cell ID is invalid")
        if (
            not isinstance(footer[4], list)
            or any(type(index) is not int for index in footer[4])
            or footer[4] != sorted(set(footer[4]))
        ):
            raise WireFormatError("odd old indices are invalid")
        if footer[5] not in (0, 1) or type(footer[5]) is not int:
            raise WireFormatError("cell value is invalid")
        if _exact_int(
            footer[6], "cell load-record count", minimum=0
        ) != len(load_rows):
            raise WireFormatError("cell load-record count differs")
        cell_groups.append((load_rows, footer))
        cursor += 1

    template_header = records[cursor]
    _require_tag_width(
        template_header, "template_header", FAMILY_RECORD_FIELDS
    )
    if (
        template_header[1] != TEMPLATE_CATALOG_FORMAT
        or template_header[2] != TEMPLATE_TYPED_ENCODING
        or template_header[3] != expected_family
        or template_header[4] != TEMPLATE_FIELD_ORDERS
        or template_header[5] != "schema-major-cell-minor"
    ):
        raise WireFormatError("template header declarations differ")
    for index, name in (
        (6, "template schema count"),
        (7, "template cell count"),
        (8, "template identity count"),
        (9, "template witness count"),
    ):
        _exact_int(template_header[index], name, minimum=0)
    cursor += 1

    schema_rows = []
    for schema_index in range(template_header[6]):
        row = records[cursor]
        _require_tag_width(row, "template_schema", FAMILY_RECORD_FIELDS)
        if _exact_int(row[1], "schema index", minimum=0) != schema_index:
            raise WireFormatError("schema indices are not consecutive")
        schema_rows.append(row)
        cursor += 1
    cell_rows = []
    for compact_cell_index in range(template_header[7]):
        row = records[cursor]
        _require_tag_width(row, "template_cell", FAMILY_RECORD_FIELDS)
        if _exact_int(
            row[1], "template compact cell index", minimum=0
        ) != compact_cell_index:
            raise WireFormatError("compact cell indices are not consecutive")
        cell_rows.append(row)
        cursor += 1
    witness_rows = []
    for witness_index in range(template_header[9]):
        row = records[cursor]
        _require_tag_width(row, "template_witness", FAMILY_RECORD_FIELDS)
        if _exact_int(row[1], "witness index", minimum=0) != witness_index:
            raise WireFormatError("witness indices are not consecutive")
        witness_rows.append(row)
        cursor += 1
    identity_rows = []
    next_identity = 0
    while (
        cursor < len(records)
        and records[cursor][0] == "template_identity_chunk"
    ):
        row = records[cursor]
        _require_tag_width(
            row, "template_identity_chunk", FAMILY_RECORD_FIELDS
        )
        if _exact_int(
            row[1], "identity chunk start", minimum=0
        ) != next_identity:
            raise WireFormatError("identity chunks are not consecutive")
        if not isinstance(row[2], list) or not row[2]:
            raise WireFormatError("identity chunk is empty")
        if len(row[2]) > IDENTITY_CHUNK_SIZE:
            raise WireFormatError("identity chunk is too wide")
        next_identity += len(row[2])
        identity_rows.append(row)
        cursor += 1
    if identity_rows and any(
        len(row[2]) != IDENTITY_CHUNK_SIZE for row in identity_rows[:-1]
    ):
        raise WireFormatError("nonfinal identity chunk is not full")
    if next_identity != template_header[8]:
        raise WireFormatError("identity chunks do not cover the catalog")
    template_footer = records[cursor]
    _require_tag_width(
        template_footer, "template_footer", FAMILY_RECORD_FIELDS
    )
    for value in template_footer[1:]:
        _exact_hash(value, "template footer digest")
    cursor += 1
    if cursor != len(records) - 1:
        raise WireFormatError("family records are out of order")
    family_footer = records[cursor]
    _require_tag_width(
        family_footer, "family_footer", FAMILY_RECORD_FIELDS
    )
    for index, name in (
        (1, "footer source cell count"),
        (2, "footer old load count"),
        (3, "footer load rows"),
        (4, "footer occurrence loads"),
        (5, "footer comparisons"),
        (6, "family prefix records"),
        (7, "family prefix bytes"),
    ):
        _exact_int(family_footer[index], name, minimum=0)
    if family_footer[1] != len(cell_groups):
        raise WireFormatError("family footer cell count differs")
    if family_footer[2] != len(old_rows):
        raise WireFormatError("family footer old count differs")
    if family_footer[6] != len(records) - 1:
        raise WireFormatError("family prefix record count differs")
    prefix_bytes = sum(len(canonical_json_line(row)) for row in records[:-1])
    if family_footer[7] != prefix_bytes:
        raise WireFormatError("family prefix byte count differs")

    catalog = _template_catalog_from_tagged_rows(
        template_header,
        schema_rows,
        cell_rows,
        witness_rows,
        identity_rows,
        template_footer,
    )
    _validate_v2_template_catalog(catalog)
    expected_variables = (
        catalog["schema_table"][0][1]
        if catalog["schema_table"]
        else list(_FAMILY_VARIABLES[expected_family])
    )
    catalog_variables = [
        row[1]
        for table in (catalog["schema_table"], catalog["cell_table"])
        for row in table
    ]
    if header[2] != expected_variables or any(
        variables != expected_variables for variables in catalog_variables
    ):
        raise WireFormatError("family header variables differ from catalog")
    compact_cells = {row[1]: row[2] for row in cell_rows}
    if len(compact_cells) != len(cell_rows):
        raise WireFormatError("compact cell index repeats")
    for _, footer in cell_groups:
        if compact_cells.get(footer[2]) != footer[3]:
            raise WireFormatError("source/compact cell bijection differs")
    source_ids = {footer[3] for _, footer in cell_groups}
    if len(source_ids) != len(cell_groups) or source_ids != set(
        compact_cells.values()
    ):
        raise WireFormatError("source/compact cell domains differ")

    logical_cells = []
    total_occurrences = 0
    total_comparisons = 0
    for load_records, footer in cell_groups:
        if load_records != sorted(
            load_records, key=lambda row: (row[1], row[2], row[3])
        ):
            raise WireFormatError("cell load rows are not ordered")
        by_footprint = {}
        for row in load_records:
            key = (row[1], row[2])
            if any(existing[3] == row[3] for existing in by_footprint.get(key, [])):
                raise WireFormatError("bucket class repeats in a footprint")
            by_footprint.setdefault(key, []).append(row)
        logical_loads = []
        derived_odd = []
        cell_value = 0
        for old_index in selected_old_indices:
            old_row = old_rows[old_index]
            histograms = []
            footprint_bindings = []
            load_value = 0
            for footprint_index in range(
                old_row[6], old_row[6] + old_row[7]
            ):
                footprint = footprint_rows[footprint_index]
                rows = by_footprint.get((old_index, footprint_index), [])
                validate_mask_partition([row[4] for row in rows])
                buckets = []
                one_count = 0
                for row in rows:
                    mask = unpack_mask(row[4])
                    bucket_class = bucket_rows[row[3]]
                    count = bin(mask).count("1")  # noqa: FURB161
                    one_count += count * bucket_class[10]
                    buckets.append(
                        {
                            "key": _bucket_key_from_rows(
                                footprint, bucket_class
                            ),
                            "count": count,
                            "mask": f"{mask:021x}",
                        }
                    )
                histogram_value = one_count % 2
                load_value ^= histogram_value
                histograms.append(
                    {
                        "old_occurrence": footprint[3],
                        "old_leaf": footprint[6],
                        "old_polarity": footprint[5],
                        "comparison_count": TOKEN_COUNT,
                        "one_count": one_count,
                        "value": histogram_value,
                        "buckets": buckets,
                    }
                )
                footprint_bindings.append(
                    {
                        "token_id": old_row[2],
                        "source_slot": old_row[5],
                        "source_members": old_row[4],
                        "module_schema": footprint[7],
                        "occurrence": footprint[3],
                        "occurrence_slot": footprint[4],
                        "polarity": footprint[5],
                        "leaf": footprint[6],
                        "label_schema": footprint[8],
                    }
                )
            load_id = f"{expected_family}|{footer[3]}|{old_row[2]}"
            if load_value:
                derived_odd.append(old_index)
            cell_value ^= load_value
            logical_loads.append(
                {
                    "load_id": load_id,
                    "old_token_id": old_row[2],
                    "coefficient": old_row[3],
                    "source_members": old_row[4],
                    "occurrence_footprint": old_row[7],
                    "footprint_bindings": footprint_bindings,
                    "histograms": histograms,
                    "value": load_value,
                }
            )
        if footer[4] != derived_odd or footer[5] != cell_value:
            raise WireFormatError("cell parity footer differs")
        occurrence_count = sum(
            old_rows[index][7] for index in selected_old_indices
        )
        comparison_count = occurrence_count * TOKEN_COUNT
        total_occurrences += occurrence_count
        total_comparisons += comparison_count
        logical_cells.append(
            {
                "cell_id": footer[3],
                "load_count": len(selected_old_indices),
                "occurrence_load_count": occurrence_count,
                "comparison_count": comparison_count,
                "odd_load_ids": [
                    f"{expected_family}|{footer[3]}|{old_rows[index][2]}"
                    for index in derived_odd
                ],
                "value": cell_value,
                "loads": logical_loads,
            }
        )
    expected_summary = [
        len(selected_old_indices) * len(cell_groups),
        total_occurrences,
        total_comparisons,
    ]
    if family_footer[3:6] != expected_summary:
        raise WireFormatError("family footer summary differs")
    ledger = {
        "family": expected_family,
        "cells": logical_cells,
        "template_catalog": catalog,
        "summary": {
            "load_rows": family_footer[3],
            "occurrence_loads": family_footer[4],
            "comparisons": family_footer[5],
        },
    }
    return {
        "records": tuple(tuple(record) for record in records),
        "header": tuple(header),
        "ledger": ledger,
        "template_catalog": catalog,
    }


class _HashingReader:
    def __init__(self, stream: Any) -> None:
        self._stream = stream
        self.hasher = hashlib.sha256()
        self.total_bytes = 0
        self.last_line = b""

    def readline(self, limit: int = -1) -> bytes:
        line = self._stream.readline(limit)
        if not isinstance(line, bytes):
            raise WireFormatError("package object stream must be binary")
        self.last_line = line
        self.hasher.update(line)
        self.total_bytes += len(line)
        return line


def _record_count_map(
    records: Sequence[Sequence[Any]],
    declarations: Mapping[str, Sequence[str]],
) -> dict[str, int]:
    counts = {tag: 0 for tag in declarations}
    for record in records:
        if record[0] not in counts:
            raise WireFormatError(f"unknown record tag: {record[0]}")
        counts[record[0]] += 1
    return counts


def _template_summary(catalog: Mapping[str, Any]) -> dict[str, Any]:
    return {
        field: catalog[field]
        for field in PACKAGE_V2_TEMPLATE_SUMMARY_FIELDS
    }


def _derived_summary(
    ledgers: Mapping[str, Mapping[str, Any]], b_token_count: int
) -> dict[str, Any]:
    load_rows = {}
    footprint_sizes = {}
    occurrence_loads = {}
    template_counts = {}
    active_comparisons = 0
    for family in FAMILY_ORDER:
        ledger = ledgers[family]
        load_rows[family] = ledger["summary"]["load_rows"]
        occurrence_loads[family] = ledger["summary"]["occurrence_loads"]
        active_comparisons += ledger["summary"]["comparisons"]
        template_counts[family] = ledger["template_catalog"][
            "template_count"
        ]
        loads = ledger["cells"][0]["loads"] if ledger["cells"] else []
        sizes = [load["occurrence_footprint"] for load in loads]
        footprint_sizes[family] = {
            str(size): sizes.count(size) for size in sorted(set(sizes))
        }
    return {
        "load_rows": load_rows,
        "total_load_rows": sum(load_rows.values()),
        "footprint_sizes": footprint_sizes,
        "occurrence_loads": occurrence_loads,
        "total_occurrence_loads": sum(occurrence_loads.values()),
        "b_tokens_per_occurrence": b_token_count,
        "active_comparisons": active_comparisons,
        "template_counts": template_counts,
        "total_templates": sum(template_counts.values()),
    }


def _validate_b_coordinate_bindings(
    ledgers: Mapping[str, Mapping[str, Any]],
    coordinate_rows: Sequence[Sequence[Any]],
) -> None:
    observed = {}
    for family in FAMILY_ORDER:
        for cell in ledgers[family]["cells"]:
            for load in cell["loads"]:
                for histogram in load["histograms"]:
                    for bucket in histogram["buckets"]:
                        key = bucket["key"]
                        mask = int(bucket["mask"], 16)
                        coordinate = (
                            key["b_source_class"],
                            key["b_coordinate"],
                        )
                        for token_index in range(TOKEN_COUNT):
                            if not mask & (1 << token_index):
                                continue
                            prior = observed.get(token_index)
                            if prior is not None and prior != coordinate:
                                raise WireFormatError(
                                    "logical token coordinate conflicts"
                                )
                            observed[token_index] = coordinate
    if set(observed) != set(range(len(coordinate_rows))):
        raise WireFormatError("logical token coordinate coverage differs")
    for row in coordinate_rows:
        if observed[row[1]] != (row[2], row[3]):
            raise WireFormatError("shared/logical token coordinate differs")


def _decode_package_from_root(root: Mapping[str, Any], supplier: Any) -> dict:
    decoded_shared = None
    family_results = {}
    for descriptor in root["shards"]:
        stream = supplier(descriptor)
        hashing = _HashingReader(stream)
        try:
            if descriptor["family"] is None:
                decoded = decode_shared_records(hashing)
                decoded_shared = decoded
                declarations = SHARED_RECORD_FIELDS
            else:
                family = descriptor["family"]
                decoded = decode_family_records(
                    hashing,
                    expected_family=family,
                    scope=root["scope"],
                )
                family_results[family] = decoded
                declarations = FAMILY_RECORD_FIELDS
        finally:
            stream.close()
        if hashing.total_bytes != descriptor["total_bytes"]:
            raise WireFormatError("descriptor object byte count differs")
        if hashing.hasher.hexdigest() != descriptor["sha256"]:
            raise WireFormatError("descriptor object digest differs")
        records = decoded["records"]
        if len(records) != descriptor["record_count"]:
            raise WireFormatError("descriptor object record count differs")
        if _record_count_map(records, declarations) != descriptor[
            "record_counts"
        ]:
            raise WireFormatError("descriptor tag counts differ")
    if decoded_shared is None or set(family_results) != set(FAMILY_ORDER):
        raise WireFormatError("package shard roles are incomplete")
    shared_header = decoded_shared["header"]
    if (
        shared_header[1] != root["format"]
        or shared_header[2] != root["scope"]
        or shared_header[3] != root["logical_v1_format"]
        or shared_header[4] != root["canonical_encoding"]
        or shared_header[5] != root["mask_encoding"]
        or shared_header[6] != root["domain"]
        or shared_header[7] != root["status"]
        or shared_header[8] != root["shard_order"]
    ):
        raise WireFormatError("shared header/root binding differs")
    source_bindings = decoded_shared["source_bindings"]
    if source_bindings["sha256"] != root["source_bindings_sha256"]:
        raise WireFormatError("root source-binding digest differs")
    identity_fields = SHARED_RECORD_FIELDS["b_identity"][1:]
    b_identity_table = [
        {
            field: value
            for field, value in zip(identity_fields, row[1:])
        }
        for row in decoded_shared["identities"]
    ]
    b_identity_digest = hashlib.sha256(
        _canonical_json(b_identity_table).encode("ascii")
    ).hexdigest()
    if b_identity_digest != root["b_identity_digest"]:
        raise WireFormatError("root B identity digest differs")
    ledgers = {
        family: family_results[family]["ledger"] for family in FAMILY_ORDER
    }
    if {
        family: _template_summary(ledgers[family]["template_catalog"])
        for family in FAMILY_ORDER
    } != root["template_catalogs"]:
        raise WireFormatError("root template catalog summaries differ")
    _validate_b_coordinate_bindings(
        ledgers, decoded_shared["coordinates"]
    )
    summary = _derived_summary(ledgers, len(b_identity_table))
    if summary != root["emitted_summary"]:
        raise WireFormatError("root emitted summary differs")
    return {
        "format": root["logical_v1_format"],
        "domain": root["domain"],
        "status": root["status"],
        "summary": summary,
        "dependency_digests": decoded_shared["dependencies"],
        "source_bindings": source_bindings,
        "b_identity_table": b_identity_table,
        "b_identity_digest": b_identity_digest,
        "family_ledgers": ledgers,
    }


def decode_v2_package(
    index_bytes: bytes, objects: Mapping[str, bytes]
) -> dict[str, Any]:
    root = decode_root_index(index_bytes)

    def supply(descriptor: Mapping[str, Any]) -> Any:
        path = descriptor["path"]
        payload = objects.get(path)
        if not isinstance(payload, bytes):
            raise WireFormatError(f"package object is missing: {path}")
        return io.BytesIO(payload)

    return _decode_package_from_root(root, supply)


def decode_v2_package_path(index_path: Path) -> dict[str, Any]:
    target = Path(index_path).resolve()
    with target.open("rb") as handle:
        root = decode_root_index(handle)
    object_root = target.parent.resolve()

    def supply(descriptor: Mapping[str, Any]) -> Any:
        relative = Path(descriptor["path"])
        if (
            relative.is_absolute()
            or len(relative.parts) != 2
            or relative.parts[0] != "objects"
        ):
            raise WireFormatError("descriptor object path is invalid")
        path = (object_root / relative).resolve()
        if path.parent != object_root / "objects":
            raise WireFormatError("descriptor object path escapes package")
        return path.open("rb")

    return _decode_package_from_root(root, supply)


def _generation_projection_failure(detail: str) -> None:
    raise EngineeringVerificationFailure("generation-projection", detail)


def _generation_projection_mapping(
    value: Any,
    fields: Sequence[str],
    name: str,
) -> Mapping[str, Any]:
    if (
        not isinstance(value, Mapping)
        or any(type(key) is not str for key in value)
        or set(value) != set(fields)
    ):
        _generation_projection_failure(f"{name} fields differ")
    return value


def _generation_projection_int(
    value: Any,
    name: str,
    *,
    positive: bool = False,
) -> int:
    minimum = 1 if positive else 0
    if type(value) is not int or value < minimum:
        qualifier = "positive" if positive else "nonnegative"
        _generation_projection_failure(
            f"{name} must be an exact {qualifier} integer"
        )
    return value


def _generation_projection_sequence(value: Any, name: str) -> tuple[Any, ...]:
    if type(value) not in (list, tuple):
        _generation_projection_failure(f"{name} must be a list or tuple")
    return tuple(value)


def _generation_projection_ascii_string(value: Any, name: str) -> str:
    if type(value) is not str or not value or not value.isascii():
        _generation_projection_failure(f"{name} must be an exact ASCII string")
    return value


def _generation_projection_indices(
    value: Any,
    name: str,
    *,
    upper_bound: int,
) -> tuple[int, ...]:
    indices = _generation_projection_sequence(value, name)
    if (
        not indices
        or any(type(index) is not int for index in indices)
        or indices != tuple(sorted(set(indices)))
        or indices[0] < 0
        or indices[-1] >= upper_bound
    ):
        _generation_projection_failure(f"{name} is not a strict valid range")
    return indices


def _generation_projection_ascii_ids(value: Any, name: str) -> tuple[str, ...]:
    identifiers = _generation_projection_sequence(value, name)
    if (
        not identifiers
        or any(
            type(identifier) is not str
            or not identifier
            or not identifier.isascii()
            for identifier in identifiers
        )
        or identifiers != tuple(sorted(set(identifiers)))
    ):
        _generation_projection_failure(
            f"{name} must be strict ASCII-sorted identifiers"
        )
    return identifiers


def _validated_generation_projection_premises(
    premises: _GenerationProjectionPremises,
) -> _GenerationProjectionPremises:
    if type(premises) is not _GenerationProjectionPremises:
        _generation_projection_failure("generation projection premises differ")
    domain = _generation_projection_ascii_string(
        premises.domain, "projected root domain"
    )
    dependency_count = _generation_projection_int(
        premises.shared_dependency_count, "shared dependency count"
    )
    maps = {
        "schema_profiles": premises.schema_profiles,
        "bucket_class_counts": premises.bucket_class_counts,
        "family_witness_counts": premises.family_witness_counts,
    }
    for field, family_map in maps.items():
        if (
            not isinstance(family_map, Mapping)
            or any(type(key) is not str for key in family_map)
            or set(family_map) != set(FAMILY_ORDER)
        ):
            _generation_projection_failure(
                f"projected root {field} families differ"
            )

    profiles = {}
    bucket_counts = {}
    witness_counts = {}
    for family in FAMILY_ORDER:
        rows = maps["schema_profiles"][family]
        if type(rows) is not tuple or not rows:
            _generation_projection_failure(f"{family} schema profiles differ")
        normalized_rows = []
        for row in rows:
            if type(row) is not tuple or len(row) != 2:
                _generation_projection_failure(
                    f"{family} schema profile width differs"
                )
            schema_id, pump_count = row
            if (
                type(schema_id) is not str
                or not schema_id
                or not schema_id.isascii()
            ):
                _generation_projection_failure(
                    f"{family} schema profile ID is invalid"
                )
            normalized_rows.append(
                (
                    schema_id,
                    _generation_projection_int(
                        pump_count,
                        f"{family} schema pump count",
                    ),
                )
            )
        if tuple(normalized_rows) != tuple(
            sorted(normalized_rows, key=lambda row: row[0].encode("ascii"))
        ):
            _generation_projection_failure(
                f"{family} schema profile order differs"
            )
        if len({row[0] for row in normalized_rows}) != len(normalized_rows):
            _generation_projection_failure(f"{family} schema IDs repeat")
        profiles[family] = tuple(normalized_rows)
        bucket_counts[family] = _generation_projection_int(
            maps["bucket_class_counts"][family],
            f"{family} bucket-class count",
            positive=True,
        )
        witness_counts[family] = _generation_projection_int(
            maps["family_witness_counts"][family],
            f"{family} witness count",
            positive=True,
        )
    return _GenerationProjectionPremises(
        domain=domain,
        shared_dependency_count=dependency_count,
        schema_profiles=profiles,
        bucket_class_counts=bucket_counts,
        family_witness_counts=witness_counts,
    )


def _generation_projection_ceil(
    sampled: int,
    full_count: int,
    sampled_count: int,
) -> int:
    return (sampled * full_count + sampled_count - 1) // sampled_count


def _generation_projected_root_oracle(
    premises: _GenerationProjectionPremises,
    projection: Mapping[str, Any],
    families: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    zero_digest = "0" * 64
    family_values = {value["family"]: value for value in families}
    load_rows = {}
    footprint_sizes = {}
    occurrence_loads = {}
    template_counts = {}
    template_catalogs = {}
    family_descriptors = []
    for family in FAMILY_ORDER:
        (
            full_schema_count,
            cell_count,
            full_identity_count,
            full_loads,
            _sampled_loads,
            full_occurrences,
            _sampled_occurrences,
            _full_comparisons,
            _sampled_comparisons,
        ) = _GENERATION_CENSUS[family]
        family_projection = family_values[family]
        old_load_count, old_remainder = divmod(full_loads, cell_count)
        footprint_count, footprint_remainder = divmod(
            full_occurrences, cell_count
        )
        footprint_size, footprint_size_remainder = divmod(
            footprint_count, old_load_count
        )
        if old_remainder or footprint_remainder or footprint_size_remainder:
            _generation_projection_failure(
                f"{family} root census is not integral"
            )
        load_rows[family] = full_loads
        footprint_sizes[family] = {str(footprint_size): old_load_count}
        occurrence_loads[family] = full_occurrences
        template_counts[family] = full_identity_count
        witness_count = premises.family_witness_counts[family]
        template_catalogs[family] = {
            "format": TEMPLATE_CATALOG_FORMAT,
            "typed_encoding": TEMPLATE_TYPED_ENCODING,
            "identity_order": "schema-major-cell-minor",
            "schema_count": full_schema_count,
            "cell_count": cell_count,
            "template_count": full_identity_count,
            "witness_count": witness_count,
            "identity_sha256": zero_digest,
            "replay_sha256": zero_digest,
            "catalog_sha256": zero_digest,
        }
        record_counts = {
            "family_header": 1,
            "old_load": old_load_count,
            "footprint": footprint_count,
            "bucket_class": family_projection[
                "projected_bucket_class_count"
            ],
            "load": family_projection["projected_load_record_count"],
            "cell_footer": cell_count,
            "template_header": 1,
            "template_schema": full_schema_count,
            "template_cell": cell_count,
            "template_witness": witness_count,
            "template_identity_chunk": (
                full_identity_count + IDENTITY_CHUNK_SIZE - 1
            )
            // IDENTITY_CHUNK_SIZE,
            "template_footer": 1,
            "family_footer": 1,
        }
        total_bytes = (
            family_projection["fixed_family_bytes"]
            + family_projection["projected_load_bucket_bytes"]
            + family_projection["projected_template_bytes"]
        )
        family_descriptors.append(
            {
                "role": "family",
                "family": family,
                "path": f"objects/{zero_digest}.jsonl",
                "sha256": zero_digest,
                "total_bytes": total_bytes,
                "record_count": sum(record_counts.values()),
                "record_counts": record_counts,
            }
        )

    summary = {
        "load_rows": load_rows,
        "total_load_rows": sum(load_rows.values()),
        "footprint_sizes": footprint_sizes,
        "occurrence_loads": occurrence_loads,
        "total_occurrence_loads": sum(occurrence_loads.values()),
        "b_tokens_per_occurrence": TOKEN_COUNT,
        "active_comparisons": sum(occurrence_loads.values()) * TOKEN_COUNT,
        "template_counts": template_counts,
        "total_templates": sum(template_counts.values()),
    }
    shared_record_counts = {
        "shared_header": 1,
        "dependency": premises.shared_dependency_count,
        "source_bindings": 1,
        "b_identity": TOKEN_COUNT,
        "b_coordinate": TOKEN_COUNT,
        "shared_footer": 1,
    }
    shared_descriptor = {
        "role": "shared",
        "family": None,
        "path": f"objects/{zero_digest}.jsonl",
        "sha256": zero_digest,
        "total_bytes": projection["shared_bytes"],
        "record_count": sum(shared_record_counts.values()),
        "record_counts": shared_record_counts,
    }
    descriptors = [shared_descriptor, *family_descriptors]
    return {
        "format": PACKAGE_V2_FORMAT,
        "scope": PRODUCTION_SCOPE,
        "logical_v1_format": LOGICAL_V1_FORMAT,
        "canonical_encoding": CANONICAL_LINE_ENCODING,
        "mask_encoding": MASK_ENCODING,
        "domain": premises.domain,
        "status": PRODUCTION_STATUS,
        "shard_order": list(SHARD_ORDER),
        "shards": descriptors,
        "shard_bytes_total": sum(
            descriptor["total_bytes"] for descriptor in descriptors
        ),
        "emitted_summary": summary,
        "full_summary": summary,
        "source_bindings_sha256": zero_digest,
        "b_identity_digest": zero_digest,
        "template_catalogs": template_catalogs,
        "root_sha256": zero_digest,
    }


def _generation_projected_index_line(root: Mapping[str, Any]) -> bytes:
    return canonical_json_line(root)


def _generation_projected_index_bytes(root: Mapping[str, Any]) -> int:
    return len(_generation_projected_index_line(root))


def _validate_generation_projection(
    value: Mapping[str, Any],
    premises: _GenerationProjectionPremises,
) -> _GenerationProjectionValidation:
    premises = _validated_generation_projection_premises(premises)
    projection = _generation_projection_mapping(
        value,
        GENERATION_PROJECTION_FIELDS,
        "generation projection",
    )
    projection_format = _generation_projection_ascii_string(
        projection["format"], "generation projection format"
    )
    if projection_format != GENERATION_PROJECTION_FORMAT:
        _generation_projection_failure("generation projection format differs")
    family_order = _generation_projection_sequence(
        projection["family_order"], "generation family order"
    )
    if any(type(family) is not str for family in family_order):
        _generation_projection_failure(
            "generation family order must contain exact strings"
        )
    if family_order != FAMILY_ORDER:
        _generation_projection_failure("generation family order differs")
    family_rows = _generation_projection_sequence(
        projection["families"], "generation families"
    )
    if len(family_rows) != len(FAMILY_ORDER):
        _generation_projection_failure("generation family count differs")

    top_numeric_fields = (
        "full_schema_count",
        "full_identity_count",
        "sampled_source_loads",
        "sampled_occurrence_loads",
        "sampled_comparisons",
        "source_catalog_precompute_ns",
        "shared_ns",
        "shared_bytes",
        "projected_index_ns",
        "projected_index_bytes",
        "generation_ns_before_margin",
        "package_bytes_before_margin",
        "projected_generation_ns",
        "projected_package_bytes",
    )
    normalized_top_numbers = {
        field: _generation_projection_int(
            projection[field], f"generation {field}"
        )
        for field in top_numeric_fields
    }

    normalized_families = []
    comparison_dynamic_range = False
    identity_dynamic_range = False
    for expected_family, raw_family in zip(FAMILY_ORDER, family_rows):
        family_projection = _generation_projection_mapping(
            raw_family,
            GENERATION_FAMILY_PROJECTION_FIELDS,
            f"{expected_family} generation projection",
        )
        family = _generation_projection_ascii_string(
            family_projection["family"], "generation family"
        )
        if family != expected_family:
            _generation_projection_failure("generation family order repeats")
        (
            full_schema_count,
            cell_count,
            full_identity_count,
            full_loads,
            _sampled_loads,
            _full_occurrences,
            _sampled_occurrences,
            full_comparisons,
            sampled_comparisons,
        ) = _GENERATION_CENSUS[family]
        profiles = premises.schema_profiles[family]
        if len(profiles) != full_schema_count:
            _generation_projection_failure(
                f"{family} full schema census differs"
            )
        maximum_pumps = max(pump_count for _, pump_count in profiles)
        tied_ids = tuple(
            schema_id
            for schema_id, pump_count in profiles
            if pump_count == maximum_pumps
        )
        tied_indices = {
            index
            for index, (_, pump_count) in enumerate(profiles)
            if pump_count == maximum_pumps
        }
        selected_schema_indices = tuple(
            sorted({*range(0, full_schema_count, 8), *tied_indices})
        )
        old_load_count, old_remainder = divmod(full_loads, cell_count)
        if old_remainder:
            _generation_projection_failure(
                f"{family} old-load denominator is not integral"
            )
        selected_old_indices = _generation_projection_indices(
            family_projection["selected_old_indices"],
            f"{family} selected old indices",
            upper_bound=old_load_count,
        )
        if selected_old_indices != _GENERATION_SELECTED_OLD_INDICES[family]:
            _generation_projection_failure(
                f"{family} selected old indices differ"
            )
        supplied_schema_indices = _generation_projection_indices(
            family_projection["selected_schema_indices"],
            f"{family} selected schema indices",
            upper_bound=full_schema_count,
        )
        if supplied_schema_indices != selected_schema_indices:
            _generation_projection_failure(
                f"{family} selected schema indices differ"
            )
        supplied_tied_ids = _generation_projection_ascii_ids(
            family_projection["tied_max_schema_ids"],
            f"{family} tied maximum schema IDs",
        )
        if supplied_tied_ids != tied_ids:
            _generation_projection_failure(
                f"{family} tied maximum schema IDs differ"
            )

        numeric_fields = GENERATION_FAMILY_PROJECTION_FIELDS[4:]
        family_numbers = {
            field: _generation_projection_int(
                family_projection[field], f"{family} {field}"
            )
            for field in numeric_fields
        }
        for field in (
            "full_schema_count",
            "full_comparisons",
            "sampled_comparisons",
            "sampled_load_record_count",
            "projected_load_record_count",
            "projected_bucket_class_count",
            "full_identity_count",
            "sampled_identity_count",
        ):
            if family_numbers[field] == 0:
                _generation_projection_failure(f"{family} {field} is zero")
        sampled_identity_count = len(selected_schema_indices) * cell_count
        expected_denominators = {
            "full_schema_count": full_schema_count,
            "full_comparisons": full_comparisons,
            "sampled_comparisons": sampled_comparisons,
            "full_identity_count": full_identity_count,
            "sampled_identity_count": sampled_identity_count,
        }
        if any(
            family_numbers[field] != expected
            for field, expected in expected_denominators.items()
        ):
            _generation_projection_failure(
                f"{family} generation denominator census differs"
            )
        comparison_ratio_one = sampled_comparisons == full_comparisons
        identity_ratio_one = sampled_identity_count == full_identity_count
        if comparison_ratio_one != (
            selected_old_indices == tuple(range(old_load_count))
        ):
            _generation_projection_failure(
                f"{family} comparison ratio-one range differs"
            )
        if identity_ratio_one != (
            selected_schema_indices == tuple(range(full_schema_count))
        ):
            _generation_projection_failure(
                f"{family} identity ratio-one range differs"
            )
        comparison_dynamic_range |= not comparison_ratio_one
        identity_dynamic_range |= not identity_ratio_one

        expected_derived = {
            "projected_two_pass_ns": _generation_projection_ceil(
                family_numbers["sampled_two_pass_ns"],
                full_comparisons,
                sampled_comparisons,
            ),
            "projected_load_bucket_bytes": _generation_projection_ceil(
                family_numbers["sampled_load_bucket_bytes"],
                full_comparisons,
                sampled_comparisons,
            ),
            "projected_load_record_count": _generation_projection_ceil(
                family_numbers["sampled_load_record_count"],
                full_comparisons,
                sampled_comparisons,
            ),
            "projected_bucket_class_count": premises.bucket_class_counts[
                family
            ],
            "projected_template_ns": _generation_projection_ceil(
                family_numbers["sampled_template_ns"],
                full_identity_count,
                sampled_identity_count,
            ),
            "projected_template_bytes": _generation_projection_ceil(
                family_numbers["sampled_template_bytes"],
                full_identity_count,
                sampled_identity_count,
            ),
        }
        if any(
            family_numbers[field] != expected
            for field, expected in expected_derived.items()
        ):
            _generation_projection_failure(
                f"{family} derived generation projection differs"
            )
        normalized_families.append(
            {
                "family": family,
                "selected_old_indices": list(selected_old_indices),
                "selected_schema_indices": list(selected_schema_indices),
                "tied_max_schema_ids": list(supplied_tied_ids),
                **family_numbers,
            }
        )

    if not comparison_dynamic_range or not identity_dynamic_range:
        dimension = "comparison" if not comparison_dynamic_range else "identity"
        _generation_projection_failure(
            f"global generation {dimension} projection lacks dynamic range"
        )
    expected_top_census = {
        "full_schema_count": sum(row[0] for row in _GENERATION_CENSUS.values()),
        "full_identity_count": sum(row[2] for row in _GENERATION_CENSUS.values()),
        "sampled_source_loads": sum(row[4] for row in _GENERATION_CENSUS.values()),
        "sampled_occurrence_loads": sum(
            row[6] for row in _GENERATION_CENSUS.values()
        ),
        "sampled_comparisons": sum(
            row[8] for row in _GENERATION_CENSUS.values()
        ),
    }
    if any(
        normalized_top_numbers[field] != expected
        for field, expected in expected_top_census.items()
    ):
        _generation_projection_failure("top generation census differs")

    normalized = {
        "format": GENERATION_PROJECTION_FORMAT,
        "family_order": list(FAMILY_ORDER),
        **{
            field: normalized_top_numbers[field]
            for field in top_numeric_fields
            if field
            not in {
                "generation_ns_before_margin",
                "package_bytes_before_margin",
                "projected_generation_ns",
                "projected_package_bytes",
            }
        },
        "families": normalized_families,
        "generation_ns_before_margin": normalized_top_numbers[
            "generation_ns_before_margin"
        ],
        "package_bytes_before_margin": normalized_top_numbers[
            "package_bytes_before_margin"
        ],
        "projected_generation_ns": normalized_top_numbers[
            "projected_generation_ns"
        ],
        "projected_package_bytes": normalized_top_numbers[
            "projected_package_bytes"
        ],
    }
    root_oracle = _generation_projected_root_oracle(
        premises,
        normalized,
        normalized_families,
    )
    projected_index_bytes = _generation_projected_index_bytes(root_oracle)
    if normalized_top_numbers["projected_index_bytes"] != projected_index_bytes:
        _generation_projection_failure("projected index byte cost differs")
    generation_before_margin = (
        normalized_top_numbers["source_catalog_precompute_ns"]
        + normalized_top_numbers["shared_ns"]
        + normalized_top_numbers["projected_index_ns"]
        + sum(
            family["fixed_family_ns"]
            + family["projected_two_pass_ns"]
            + family["projected_template_ns"]
            for family in normalized_families
        )
    )
    package_before_margin = (
        normalized_top_numbers["shared_bytes"]
        + projected_index_bytes
        + sum(
            family["fixed_family_bytes"]
            + family["projected_load_bucket_bytes"]
            + family["projected_template_bytes"]
            for family in normalized_families
        )
    )
    expected_top_derived = {
        "generation_ns_before_margin": generation_before_margin,
        "package_bytes_before_margin": package_before_margin,
        "projected_generation_ns": 2 * generation_before_margin,
        "projected_package_bytes": 2 * package_before_margin,
    }
    if any(
        normalized_top_numbers[field] != expected
        for field, expected in expected_top_derived.items()
    ):
        _generation_projection_failure("derived generation totals differ")
    normalized_json = _canonical_json(normalized)
    return _GenerationProjectionValidation(
        normalized=normalized_json,
        sha256=hashlib.sha256(normalized_json.encode("ascii")).hexdigest(),
    )


def _projection_int(value: Any, name: str, *, positive: bool = False) -> int:
    if type(value) is not int or value < (1 if positive else 0):
        qualifier = "positive" if positive else "nonnegative"
        raise EngineeringVerificationFailure(
            "verification-projection",
            f"{name} must be an exact {qualifier} integer",
        )
    return value


def _projection_indices(
    value: Any,
    name: str,
    *,
    upper_bound: int,
) -> tuple[int, ...]:
    if not isinstance(value, (list, tuple)):
        raise EngineeringVerificationFailure(
            "verification-projection", f"{name} must be a list or tuple"
        )
    indices = tuple(value)
    if (
        not indices
        or any(type(index) is not int for index in indices)
        or indices != tuple(sorted(set(indices)))
        or indices[0] < 0
        or indices[-1] >= upper_bound
    ):
        raise EngineeringVerificationFailure(
            "verification-projection", f"{name} is not a strict valid range"
        )
    return indices


def _project_verification_charge(
    charge: VerificationChargeInput,
) -> VerificationChargeProjection:
    if type(charge) is not VerificationChargeInput:
        raise EngineeringVerificationFailure(
            "verification-projection", "charge input type differs"
        )
    sampled_ns = _projection_int(charge.sampled_ns, "sampled nanoseconds")
    full_count = _projection_int(
        charge.full_record_count, "full record count", positive=True
    )
    sampled_count = _projection_int(
        charge.sampled_record_count, "sampled record count", positive=True
    )
    if sampled_count > full_count:
        raise EngineeringVerificationFailure(
            "verification-projection",
            "sampled record count exceeds the full record count",
        )
    return VerificationChargeProjection(
        domain=charge.domain,
        sampled_ns=sampled_ns,
        full_record_count=full_count,
        sampled_record_count=sampled_count,
        projected_ns=(
            sampled_ns * full_count + sampled_count - 1
        )
        // sampled_count,
    )


def _ordered_verification_charges(
    charges: Any,
    expected_domains: tuple[str, ...],
) -> tuple[VerificationChargeProjection, ...]:
    if not isinstance(charges, (list, tuple)):
        raise EngineeringVerificationFailure(
            "verification-projection", "charges must be a list or tuple"
        )
    values = tuple(charges)
    if tuple(
        charge.domain if type(charge) is VerificationChargeInput else None
        for charge in values
    ) != expected_domains:
        raise EngineeringVerificationFailure(
            "verification-projection",
            "charge domains are incomplete, repeated, or out of order",
        )
    return tuple(_project_verification_charge(charge) for charge in values)


def project_verification(
    *,
    global_charges: Sequence[VerificationChargeInput],
    invariant_ns: int,
    families: Sequence[FamilyVerificationProjectionInput],
) -> VerificationProjection:
    invariant = _projection_int(invariant_ns, "global invariant nanoseconds")
    if invariant != 0:
        raise EngineeringVerificationFailure(
            "verification-projection",
            "global invariant nanoseconds must be zero; use a named charge",
        )
    projected_global = _ordered_verification_charges(
        global_charges, GLOBAL_VERIFICATION_CHARGE_DOMAINS
    )
    if not isinstance(families, (list, tuple)):
        raise EngineeringVerificationFailure(
            "verification-projection", "families must be a list or tuple"
        )
    values = tuple(families)
    if tuple(
        value.family
        if type(value) is FamilyVerificationProjectionInput
        else None
        for value in values
    ) != FAMILY_ORDER:
        raise EngineeringVerificationFailure(
            "verification-projection",
            "verification families are incomplete, repeated, or out of order",
        )

    comparison_dynamic_range = False
    identity_dynamic_range = False
    projected_families = []
    for value in values:
        full_old_count = _projection_int(
            value.full_old_load_count,
            f"{value.family} full old-load count",
            positive=True,
        )
        full_schema_count = _projection_int(
            value.full_schema_count,
            f"{value.family} full schema count",
            positive=True,
        )
        old_indices = _projection_indices(
            value.selected_old_indices,
            f"{value.family} selected old indices",
            upper_bound=full_old_count,
        )
        schema_indices = _projection_indices(
            value.selected_schema_indices,
            f"{value.family} selected schema indices",
            upper_bound=full_schema_count,
        )
        projected_charges = _ordered_verification_charges(
            value.charges, FAMILY_VERIFICATION_CHARGE_DOMAINS
        )
        by_domain = {charge.domain: charge for charge in projected_charges}
        comparison = by_domain["comparison-replay"]
        complete_old_range = old_indices == tuple(range(full_old_count))
        if (
            comparison.sampled_record_count == comparison.full_record_count
        ) != complete_old_range:
            raise EngineeringVerificationFailure(
                "verification-projection",
                f"{value.family} comparison ratio-one selection differs",
            )
        comparison_dynamic_range |= (
            comparison.sampled_record_count < comparison.full_record_count
        )

        template = by_domain["template-replay"]
        complete_schema_range = schema_indices == tuple(
            range(full_schema_count)
        )
        if (
            template.sampled_record_count == template.full_record_count
        ) != complete_schema_range:
            raise EngineeringVerificationFailure(
                "verification-projection",
                f"{value.family} identity ratio-one selection differs",
            )
        identity_dynamic_range |= (
            template.sampled_record_count < template.full_record_count
        )

        family_invariant = _projection_int(
            value.invariant_family_ns,
            f"{value.family} invariant nanoseconds",
        )
        if family_invariant != 0:
            raise EngineeringVerificationFailure(
                "verification-projection",
                f"{value.family} invariant nanoseconds must be zero; "
                "use a named charge",
            )
        family_total = family_invariant + sum(
            charge.projected_ns for charge in projected_charges
        )
        projected_families.append(
            FamilyVerificationProjection(
                family=value.family,
                selected_old_indices=old_indices,
                selected_schema_indices=schema_indices,
                full_old_load_count=full_old_count,
                full_schema_count=full_schema_count,
                charges=projected_charges,
                invariant_family_ns=family_invariant,
                verification_ns_before_margin=family_total,
            )
        )
    if not comparison_dynamic_range or not identity_dynamic_range:
        dimension = "comparison" if not comparison_dynamic_range else "identity"
        raise EngineeringVerificationFailure(
            "verification-projection",
            f"global {dimension} projection lacks dynamic range",
        )

    before_margin = (
        invariant
        + sum(charge.projected_ns for charge in projected_global)
        + sum(
            family.verification_ns_before_margin
            for family in projected_families
        )
    )
    return VerificationProjection(
        format=VERIFICATION_PROJECTION_FORMAT,
        family_order=FAMILY_ORDER,
        global_charges=projected_global,
        invariant_ns=invariant,
        families=tuple(projected_families),
        verification_ns_before_margin=before_margin,
        projected_verification_ns=2 * before_margin,
    )


def _stream_record(
    iterator: Iterable[Any],
    reader: _HashingReader,
) -> tuple[Any, int]:
    try:
        record = next(iterator)
    except StopIteration as error:
        raise WireFormatError("shard is missing its terminal footer") from error
    _validate_tagged_record(record)
    return record, len(reader.last_line)


def _authenticate_footer(
    record: Sequence[Any],
    *,
    tag: str,
    declarations: Mapping[str, Sequence[str]],
    records_before_footer: int,
    bytes_before_footer: int,
) -> None:
    _require_tag_width(record, tag, declarations)
    if tag == "shared_footer":
        record_index, byte_index = 2, 3
    else:
        record_index, byte_index = 6, 7
    if _exact_int(record[record_index], f"{tag} prefix records", minimum=0) != (
        records_before_footer
    ):
        raise WireFormatError(f"{tag} prefix record count differs")
    if _exact_int(record[byte_index], f"{tag} prefix bytes", minimum=0) != (
        bytes_before_footer
    ):
        raise WireFormatError(f"{tag} prefix byte count differs")


def _family_stream_caps(family: str) -> dict[str, int]:
    (
        schema_count,
        cell_count,
        identity_count,
        load_count,
        _sampled_load_count,
        occurrence_count,
        _sampled_occurrence_count,
        _comparison_count,
        _sampled_comparison_count,
    ) = _GENERATION_CENSUS[family]
    caps = {
        "family_header": 1,
        "old_load": load_count // cell_count,
        "footprint": occurrence_count // cell_count,
        "bucket_class": 0,
        "load": 0,
        "cell_footer": cell_count,
        "template_header": 1,
        "template_schema": schema_count,
        "template_cell": cell_count,
        "template_witness": 0,
        "template_identity_chunk": (
            identity_count + IDENTITY_CHUNK_SIZE - 1
        ) // IDENTITY_CHUNK_SIZE,
        "template_footer": 1,
        "family_footer": 1,
    }
    caps.update(_FAMILY_STREAM_RECORD_CAPS[family])
    return caps


def _authenticate_descriptor_stream(
    descriptor: Mapping[str, Any],
    stream: Any,
) -> tuple[dict[str, int], dict[str, Any]]:
    family = descriptor["family"]
    declarations = (
        SHARED_RECORD_FIELDS if family is None else FAMILY_RECORD_FIELDS
    )
    reader = _HashingReader(stream)
    iterator = iter_canonical_json_lines(reader)
    counts = {tag: 0 for tag in declarations}
    retained: dict[str, Any] = {}
    records_before_footer = 0
    try:
        if family is None:
            phase = 0
            identities: dict[int, tuple[Any, ...]] = {}
            coordinates: dict[int, tuple[Any, ...]] = {}
            header = None
            source_bindings = None
            while True:
                record, line_bytes = _stream_record(iterator, reader)
                tag = record[0]
                if tag not in counts:
                    raise WireFormatError("shared shard has an unknown record tag")
                if tag in {"shared_header", "source_bindings"} and counts[tag]:
                    raise WireFormatError("shared singleton record repeats")
                if tag == "dependency":
                    if phase > 1:
                        raise WireFormatError("shared records are out of order")
                    if counts[tag] >= _SHARED_DEPENDENCY_MAX:
                        raise WireFormatError(
                            "shared dependency census exceeds cap"
                        )
                    phase = 1
                elif tag == "source_bindings":
                    if phase > 2:
                        raise WireFormatError("shared records are out of order")
                    phase = 2
                elif tag == "b_identity":
                    if phase not in (2, 3):
                        raise WireFormatError("shared records are out of order")
                    phase = 3
                elif tag == "b_coordinate":
                    if phase not in (3, 4):
                        raise WireFormatError("shared records are out of order")
                    phase = 4
                elif tag == "shared_footer":
                    if phase != 4 or counts[tag]:
                        raise WireFormatError("shared records are out of order")
                    _authenticate_footer(
                        record,
                        tag=tag,
                        declarations=declarations,
                        records_before_footer=records_before_footer,
                        bytes_before_footer=reader.total_bytes - line_bytes,
                    )
                    counts[tag] += 1
                    try:
                        next(iterator)
                    except StopIteration:
                        break
                    raise WireFormatError("records follow the shared footer")
                elif tag != "shared_header" or phase != 0 or counts[tag]:
                    raise WireFormatError("shared records are out of order")
                _require_tag_width(record, tag, declarations)
                if tag == "shared_header":
                    header = tuple(record)
                elif tag == "source_bindings":
                    source_bindings = record[1]
                elif tag == "b_identity":
                    if len(identities) >= TOKEN_COUNT:
                        raise WireFormatError("B identity census exceeds cap")
                    index = _exact_int(record[1], "B token index", minimum=0)
                    if index != len(identities):
                        raise WireFormatError("B identity indices are not consecutive")
                    identities[index] = tuple(record)
                elif tag == "b_coordinate":
                    if len(coordinates) >= TOKEN_COUNT:
                        raise WireFormatError("B coordinate census exceeds cap")
                    index = _exact_int(record[1], "B coordinate index", minimum=0)
                    if index != len(coordinates) or index not in identities:
                        raise WireFormatError("B coordinate identity reference differs")
                    coordinates[index] = tuple(record)
                counts[tag] += 1
                records_before_footer += 1
            if (
                counts["shared_header"] != 1
                or counts["source_bindings"] != 1
                or counts["shared_footer"] != 1
            ):
                raise WireFormatError("shared singleton record count differs")
            if len(identities) != TOKEN_COUNT or len(coordinates) != TOKEN_COUNT:
                raise WireFormatError("shared B reference count differs")
            retained = {
                "dependency_count": counts["dependency"],
                "header": header,
                "source_bindings": source_bindings,
                "identities": identities,
                "coordinates": coordinates,
            }
        else:
            required = (
                "family_header",
                "old_load",
                "footprint",
                "bucket_class",
                "load",
                "cell_footer",
                "template_header",
                "template_schema",
                "template_cell",
                "template_witness",
                "template_identity_chunk",
                "template_footer",
                "family_footer",
            )
            phase = 0
            schema_ids: list[str] = []
            old_loads: list[tuple[Any, ...]] = []
            footprints: list[tuple[Any, ...]] = []
            bucket_classes: list[tuple[Any, ...]] = []
            cells: list[tuple[Any, ...]] = []
            witnesses: list[int] = []
            witness_rows: list[tuple[Any, ...]] = []
            identity_witness_ids: list[int] = []
            cell_count = 0
            template_header = None
            caps = _family_stream_caps(family)
            while True:
                record, line_bytes = _stream_record(iterator, reader)
                tag = record[0]
                if tag not in counts:
                    raise WireFormatError("family shard has an unknown record tag")
                if tag in {
                    "family_header",
                    "template_header",
                    "template_footer",
                } and counts[tag]:
                    raise WireFormatError("family singleton record repeats")
                position = required.index(tag)
                if tag == "load":
                    if phase != position:
                        raise WireFormatError("family records are out of order")
                elif tag == "cell_footer":
                    if phase not in (4, position):
                        raise WireFormatError("family records are out of order")
                elif tag == "family_footer":
                    if phase != position - 1 or counts[tag]:
                        raise WireFormatError("family records are out of order")
                    _authenticate_footer(
                        record,
                        tag=tag,
                        declarations=declarations,
                        records_before_footer=records_before_footer,
                        bytes_before_footer=reader.total_bytes - line_bytes,
                    )
                    counts[tag] += 1
                    try:
                        next(iterator)
                    except StopIteration:
                        break
                    raise WireFormatError("records follow the family footer")
                else:
                    if position < phase:
                        raise WireFormatError("family records are out of order")
                    while phase < position:
                        current = required[phase]
                        if counts[current] != descriptor["record_counts"][current]:
                            raise WireFormatError(
                                "family descriptor tag counts differ"
                            )
                        phase += 1
                _require_tag_width(record, tag, declarations)
                if counts[tag] >= caps[tag]:
                    raise WireFormatError("family record census exceeds cap")
                if tag == "family_header":
                    _validate_family_header(record, family)
                    if any(
                        record[index] > caps[name]
                        for index, name in (
                            (3, "cell_footer"),
                            (5, "old_load"),
                            (6, "footprint"),
                            (7, "bucket_class"),
                        )
                    ):
                        raise WireFormatError("family census exceeds cap")
                elif tag == "old_load":
                    old_loads.append(tuple(record))
                elif tag == "footprint":
                    footprints.append(tuple(record))
                elif tag == "bucket_class":
                    bucket_classes.append(tuple(record))
                elif tag == "cell_footer":
                    cells.append(tuple(record))
                elif tag == "template_header":
                    if record[3] != family:
                        raise WireFormatError("template header family differs")
                    schema_count = _exact_int(
                        record[6], "template schema count", minimum=0
                    )
                    declared_cell_count = _exact_int(
                        record[7], "template cell count", minimum=0
                    )
                    template_count = _exact_int(
                        record[8], "template identity count", minimum=0
                    )
                    witness_count = _exact_int(
                        record[9], "template witness count", minimum=0
                    )
                    if (
                        schema_count > caps["template_schema"]
                        or declared_cell_count > caps["template_cell"]
                        or template_count > _GENERATION_CENSUS[family][2]
                        or witness_count > caps["template_witness"]
                    ):
                        raise WireFormatError(
                            "template header census exceeds cap"
                        )
                    template_header = tuple(record)
                    cell_count = declared_cell_count
                elif tag == "template_schema":
                    index = _exact_int(record[1], "template schema index", minimum=0)
                    if index != len(schema_ids) or not isinstance(record[2], str):
                        raise WireFormatError("template schema profiles differ")
                    schema_ids.append(record[2])
                elif tag == "template_witness":
                    index = _exact_int(record[1], "template witness index", minimum=0)
                    if index != len(witnesses) or not isinstance(record[4], list):
                        raise WireFormatError("template witness profiles differ")
                    witnesses.append(len(record[4]))
                    witness_rows.append(tuple(record))
                elif tag == "template_identity_chunk":
                    start = _exact_int(record[1], "identity chunk start", minimum=0)
                    if (
                        start != len(identity_witness_ids)
                        or type(record[2]) is not list
                        or not record[2]
                    ):
                        raise WireFormatError("template identity profiles differ")
                    if (
                        len(record[2]) > IDENTITY_CHUNK_SIZE
                        or len(identity_witness_ids) + len(record[2])
                        > _GENERATION_CENSUS[family][2]
                    ):
                        raise WireFormatError(
                            "template identity census exceeds cap"
                        )
                    identity_witness_ids.extend(record[2])
                counts[tag] += 1
                records_before_footer += 1
            if any(
                counts[tag] != 1
                for tag in (
                    "family_header",
                    "template_header",
                    "template_footer",
                    "family_footer",
                )
            ):
                raise WireFormatError("family singleton record count differs")
            if not schema_ids or cell_count < 1:
                raise WireFormatError("template schema profiles are incomplete")
            if schema_ids != sorted(set(schema_ids)):
                raise WireFormatError("template schema profiles are not ASCII ordered")
            expected_identities = len(schema_ids) * cell_count
            if len(identity_witness_ids) != expected_identities:
                raise WireFormatError("template identity profiles do not cover cells")
            if any(
                type(witness_id) is not int
                or not 0 <= witness_id < len(witnesses)
                for witness_id in identity_witness_ids
            ):
                raise WireFormatError("template identity witness reference differs")
            profiles = []
            for schema_index, schema_id in enumerate(schema_ids):
                start = schema_index * cell_count
                profiles.append(
                    (
                        schema_id,
                        max(
                            witnesses[item]
                            for item in identity_witness_ids[
                                start:start + cell_count
                            ]
                        ),
                    )
                )
            retained = {
                "schema_profiles": tuple(profiles),
                "old_loads": tuple(old_loads),
                "footprints": tuple(footprints),
                "bucket_classes": tuple(bucket_classes),
                "cells": tuple(cells),
                "template_header": template_header,
                "witnesses": tuple(witness_rows),
                "bucket_class_count": counts["bucket_class"],
                "witness_count": len(witnesses),
                "identity_witness_ids": tuple(identity_witness_ids),
            }
    finally:
        stream.close()
    if reader.total_bytes != descriptor["total_bytes"]:
        raise WireFormatError("descriptor object byte count differs")
    if reader.hasher.hexdigest() != descriptor["sha256"]:
        raise WireFormatError("descriptor object digest differs")
    if sum(counts.values()) != descriptor["record_count"]:
        raise WireFormatError("descriptor object record count differs")
    if counts != descriptor["record_counts"]:
        raise WireFormatError("descriptor object tag counts differ")
    return counts, retained


def _authenticate_v2_streams(
    root_source: Any,
    supplier: Any,
    generation_projection: Mapping[str, Any] | None = None,
) -> _AuthenticatedWireState:
    root = decode_root_index(root_source)
    if not callable(supplier):
        raise WireFormatError("object supplier must be callable")
    descriptors = {
        descriptor["family"]: descriptor for descriptor in root["shards"]
    }
    shared_descriptor = descriptors[None]
    _, shared = _authenticate_descriptor_stream(
        shared_descriptor,
        supplier(shared_descriptor),
    )
    header = shared["header"]
    if header is None or (
        header[1] != root["format"]
        or header[2] != root["scope"]
        or header[3] != root["logical_v1_format"]
        or header[4] != root["canonical_encoding"]
        or header[5] != root["mask_encoding"]
        or header[6] != root["domain"]
        or header[7] != root["status"]
        or header[8] != root["shard_order"]
    ):
        raise WireFormatError("shared header/root binding differs")
    family_retained = {}
    for family in ("C", "P", "Q", "base", "fixed", "singleton"):
        descriptor = descriptors[family]
        _, family_retained[family] = _authenticate_descriptor_stream(
            descriptor,
            supplier(descriptor),
        )
        template_header = family_retained[family]["template_header"]
        catalog = root["template_catalogs"][family]
        if template_header is None or (
            template_header[6] != catalog["schema_count"]
            or template_header[7] != catalog["cell_count"]
            or template_header[8] != catalog["template_count"]
            or template_header[9] != catalog["witness_count"]
        ):
            raise WireFormatError("template catalog/root binding differs")
    premises = _GenerationProjectionPremises(
        domain=root["domain"],
        shared_dependency_count=shared["dependency_count"],
        schema_profiles={
            family: family_retained[family]["schema_profiles"]
            for family in FAMILY_ORDER
        },
        bucket_class_counts={
            family: family_retained[family]["bucket_class_count"]
            for family in FAMILY_ORDER
        },
        family_witness_counts={
            family: family_retained[family]["witness_count"]
            for family in FAMILY_ORDER
        },
    )
    projection_sha256 = None
    if generation_projection is not None:
        projection_sha256 = _validate_generation_projection(
            generation_projection, premises
        ).sha256
    return _AuthenticatedWireState(
        root=root,
        root_sha256=root["root_sha256"],
        premises=premises,
        generation_projection_sha256=projection_sha256,
    )


def verify_v2_package(
    index_path: Path,
    run_id: str,
    generation_projection: Mapping[str, Any],
    *,
    metrics: PhaseMetrics | None = None,
) -> IndependentReplayResult:
    if not isinstance(index_path, Path):
        raise EngineeringVerificationFailure(
            "api", "index_path must be a pathlib.Path"
        )
    if not isinstance(run_id, str) or not run_id or not run_id.isascii():
        raise EngineeringVerificationFailure(
            "api", "run_id must be a nonempty ASCII string"
        )
    if not isinstance(generation_projection, Mapping):
        raise EngineeringVerificationFailure(
            "generation-projection", "projection must be a mapping"
        )
    if metrics is not None and not isinstance(metrics, PhaseMetrics):
        raise EngineeringVerificationFailure(
            "api", "metrics must be verifier-owned PhaseMetrics"
        )
    target = index_path.resolve()
    object_root = target.parent.resolve()

    def supply(descriptor: Mapping[str, Any]) -> Any:
        relative = Path(descriptor["path"])
        if (
            relative.is_absolute()
            or len(relative.parts) != 2
            or relative.parts[0] != "objects"
        ):
            raise WireFormatError("descriptor object path is invalid")
        candidate = (object_root / relative).resolve()
        if candidate.parent != object_root / "objects":
            raise WireFormatError("descriptor object path escapes package")
        return candidate.open("rb")

    try:
        with target.open("rb") as root_stream:
            _authenticate_v2_streams(
                root_stream,
                supply,
                generation_projection,
            )
    except (OSError, WireFormatError, EngineeringVerificationFailure) as error:
        if isinstance(error, EngineeringVerificationFailure):
            raise
        raise EngineeringVerificationFailure(
            "wire-authentication", str(error)
        ) from error
    raise EngineeringVerificationFailure(
        "generation-projection",
        "generation projection semantic binding is not yet complete",
    )


def build_attestation_payload(
    result: IndependentReplayResult,
    verifier_sha256: str,
    metrics: Mapping[str, Any],
) -> dict[str, Any]:
    if isinstance(result, VerificationProjection):
        raise EngineeringVerificationFailure(
            "attestation",
            "a direct verification projection is arithmetic only and "
            "non-attestable",
        )
    raise EngineeringVerificationFailure(
        "attestation", "attestation construction is not part of this slice"
    )
