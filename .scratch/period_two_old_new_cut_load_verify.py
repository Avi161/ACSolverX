from __future__ import annotations

import base64
import hashlib
import io
import json
import re
from collections.abc import Iterable, Mapping, Sequence
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
_HASH_PATTERN = re.compile(r"[0-9a-f]{64}")
_MASK_PATTERN = re.compile(r"[A-Za-z0-9_-]{15}")


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


def canonical_json_line(value: Any) -> bytes:
    try:
        return _canonical_json(value).encode("ascii") + b"\n"
    except (TypeError, UnicodeError, ValueError) as error:
        raise WireFormatError("value is not canonical JSON") from error


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


def _tagged_records(source: Any) -> tuple[list[Any], ...]:
    stream, owned = _source_stream(source)
    try:
        records = tuple(iter_canonical_json_lines(stream))
    finally:
        if owned:
            stream.close()
    for record in records:
        if (
            not isinstance(record, list)
            or not record
            or not isinstance(record[0], str)
        ):
            raise WireFormatError("tagged record is not a nonempty array")
    return records


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


def decode_root_index(source: Any) -> dict[str, Any]:
    stream, owned = _source_stream(source)
    try:
        values = tuple(iter_canonical_json_lines(stream))
    finally:
        if owned:
            stream.close()
    if len(values) != 1 or not isinstance(values[0], Mapping):
        raise WireFormatError("root index must contain exactly one object line")
    root = dict(values[0])
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
    _exact_hash(root["source_bindings_sha256"], "source bindings sha256")
    _exact_hash(root["b_identity_digest"], "B identity digest")
    catalogs = root["template_catalogs"]
    if not isinstance(catalogs, Mapping) or set(catalogs) != set(FAMILY_ORDER):
        raise WireFormatError("root template catalog families differ")
    for family, summary in catalogs.items():
        if not isinstance(summary, Mapping) or set(summary) != set(
            PACKAGE_V2_TEMPLATE_SUMMARY_FIELDS
        ):
            raise WireFormatError(
                f"root template summary fields differ: {family}"
            )
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
    records = _tagged_records(source)
    if len(records) < 3:
        raise WireFormatError("shared shard is incomplete")
    header = records[0]
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
    selected = header[4]
    if (
        not isinstance(selected, list)
        or any(type(index) is not int or index < 0 for index in selected)
        or selected != sorted(set(selected))
    ):
        raise WireFormatError("selected old indices are invalid")
    if selected != list(range(header[5])):
        raise WireFormatError("fixture old indices are not the complete range")
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
    records = _tagged_records(source)
    if len(records) < 4:
        raise WireFormatError("family shard is incomplete")
    header = records[0]
    _validate_family_header(header, expected_family)
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
        for old_index, old_row in enumerate(old_rows):
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
        occurrence_count = sum(old_row[7] for old_row in old_rows)
        comparison_count = occurrence_count * TOKEN_COUNT
        total_occurrences += occurrence_count
        total_comparisons += comparison_count
        logical_cells.append(
            {
                "cell_id": footer[3],
                "load_count": len(old_rows),
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
        len(old_rows) * len(cell_groups),
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

    def readline(self, limit: int = -1) -> bytes:
        line = self._stream.readline(limit)
        if not isinstance(line, bytes):
            raise WireFormatError("package object stream must be binary")
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


def verify_v2_package(index_path: Path) -> dict[str, Any]:
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
