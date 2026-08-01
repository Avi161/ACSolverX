import copy
import functools
import gc
import hashlib
import importlib.util
import inspect
import io
import json
import operator
import re
import sys
import tracemalloc
import weakref
from dataclasses import fields, replace
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / ".scratch/period_two_old_new_cut_load_certificate.py"
VERIFIER = ROOT / ".scratch/period_two_old_new_cut_load_verify.py"
ARTIFACT_DIR = ROOT / ".scratch/test-artifacts/old-new-load"
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
EXPECTED_INVERSE_CELL_IDS = {
    "a0_n0",
    "a0_n1",
    "a0_nge2",
    "a1_n0",
    "a1_n1",
    "a1_nge2",
    "age2_n0",
    "age2_n1",
    "age2_nge2",
}
CORE_R = (1, 2, 1, -2, -2, -2, 1, 2)
CORE_S = (1, -2, 1, 2, 2, 2, 1, -2)
TYPED_ENCODING = "task4-typed-sha256-v1"
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


def literal_inverse(letter: int) -> int:
    return 1 if abs(letter) == 1 else -letter


def literal_cvert(word: tuple[int, ...]) -> tuple[tuple[int, ...], int | None]:
    reduced = []
    for raw_letter in word:
        letter = 1 if abs(raw_letter) == 1 else raw_letter
        if reduced and reduced[-1] == literal_inverse(letter):
            reduced.pop()
        else:
            reduced.append(letter)
    terminal = reduced[-1] if reduced else None
    if terminal == 1:
        reduced.pop()
    return tuple(reduced), terminal


def literal_schema_word(schema, point: tuple[int, ...]) -> tuple[int, ...]:
    word = []
    for _, block_word, affine in schema.blocks:
        copies = 1 if affine is None else sum(
            coefficient * value
            for coefficient, value in zip(affine[:-1], point)
        ) + affine[-1]
        word.extend(block_word if affine is None else block_word * copies)
    return literal_cvert(tuple(word))[0]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_generator():
    return load_module("old_new_load_generator", GENERATOR)


def with_manifest(context, name: str, manifest):
    manifests = dict(context.manifests)
    manifests[name] = manifest
    return replace(context, manifests=manifests)


def typed_hash_update(hasher, value) -> None:
    if value is None:
        hasher.update(b"N")
        return
    if isinstance(value, bool):
        hasher.update(b"B\x01" if value else b"B\x00")
        return
    if isinstance(value, int):
        payload = str(value).encode("ascii")
        hasher.update(b"I" + len(payload).to_bytes(4, "big") + payload)
        return
    if isinstance(value, str):
        payload = value.encode("utf-8")
        hasher.update(b"S" + len(payload).to_bytes(4, "big") + payload)
        return
    if isinstance(value, (list, tuple)):
        hasher.update(b"L" + len(value).to_bytes(4, "big"))
        for item in value:
            typed_hash_update(hasher, item)
        return
    if isinstance(value, dict):
        assert all(isinstance(key, str) for key in value)
        keys = sorted(value, key=lambda key: key.encode("utf-8"))
        hasher.update(b"M" + len(keys).to_bytes(4, "big"))
        for key in keys:
            typed_hash_update(hasher, key)
            typed_hash_update(hasher, value[key])
        return
    raise TypeError(f"unsupported typed hash value: {type(value).__name__}")


def recompute_template_catalog_digests(catalog: dict) -> None:
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
        typed_hash_update(identity_hasher, value)
        typed_hash_update(replay_hasher, value)
    cell_count = len(catalog["cell_table"])
    for identity_index, witness_id in enumerate(
        catalog["identity_witness_ids"]
    ):
        schema_index, cell_index = divmod(identity_index, cell_count)
        typed_hash_update(
            identity_hasher, [schema_index, cell_index, witness_id]
        )
        typed_hash_update(
            replay_hasher, [schema_index, cell_index, witness_id]
        )
        typed_hash_update(
            replay_hasher, catalog["witness_table"][witness_id]
        )
    catalog["identity_sha256"] = identity_hasher.hexdigest()
    catalog["replay_sha256"] = replay_hasher.hexdigest()
    payload = {key: value for key, value in catalog.items() if key != "catalog_sha256"}
    catalog["catalog_sha256"] = hashlib.sha256(
        json.dumps(
            payload,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
    ).hexdigest()


def reseal_source_bindings(source_bindings: dict) -> None:
    payload = {
        key: value
        for key, value in source_bindings.items()
        if key != "sha256"
    }
    source_bindings["sha256"] = hashlib.sha256(
        json.dumps(
            payload,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
    ).hexdigest()


def test_generator_file_exists_before_loading() -> None:
    assert GENERATOR.exists(), "grouped-load generator is not implemented"


def test_verifier_file_exists_before_loading() -> None:
    assert VERIFIER.exists(), "independent grouped-load verifier is not implemented"


def test_generator_cli_writes_checks_and_summarizes_canonical_json(
    monkeypatch, capsys
) -> None:
    module = load_generator()
    manifest = {
        "format": "period-two-old-new-cut-load-v1",
        "status": "generated-awaiting-independent-replay",
        "summary": {"active_comparisons": 1491840},
    }
    target = ARTIFACT_DIR / "cli-unit.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(module, "build_manifest", lambda: copy.deepcopy(manifest))
    try:
        assert module.main(["--write", str(target)]) == 0
        assert target.read_bytes() == (
            module.canonical_json(manifest) + "\n"
        ).encode("ascii")
        assert not tuple(target.parent.glob(f".{target.name}.*.tmp"))

        assert module.main(["--check", str(target)]) == 0
        assert module.main(["--summary"]) == 0
        assert capsys.readouterr().out.splitlines()[-1] == module.canonical_json(
            {"status": manifest["status"], "summary": manifest["summary"]}
        )

        target.write_text("{}\n", encoding="ascii")
        with pytest.raises(module.CertificateFailure):
            module.main(["--check", str(target)])
    finally:
        target.unlink(missing_ok=True)
        if target.parent.is_dir() and not tuple(target.parent.iterdir()):
            target.parent.rmdir()


def test_source_bindings_serialize_complete_old_b_and_anchor_proofs() -> None:
    module = load_generator()
    catalog = module.build_task4_schema_catalog(module.load_source_context())

    source_bindings = module.build_source_bindings(catalog)

    assert set(source_bindings) == {"format", "old", "b", "sha256"}
    assert source_bindings["format"] == "task4-source-bindings-v1"
    assert source_bindings["old"] == catalog.old_source_proof
    assert source_bindings["b"] == catalog.b_source_proof
    assert set(source_bindings["old"]["integral_fibers"]) == {
        "base",
        "P",
        "C",
        "Q",
    }
    old_fibers = [
        fiber
        for fibers in source_bindings["old"]["integral_fibers"].values()
        for fiber in fibers
    ]
    assert any(not fiber["active"] for fiber in old_fibers)
    assert all(
        fiber["member_ids"] == [member["id"] for member in fiber["members"]]
        and fiber["coefficients"]
        == [member["coefficient"] for member in fiber["members"]]
        and sum(fiber["coefficients"]) == fiber["integral_sum"]
        and fiber["parity"] == fiber["integral_sum"] % 2
        and fiber["active"] == bool(fiber["parity"])
        and all(member["domain"] for member in fiber["members"])
        and all(member["current_equality"] for member in fiber["members"])
        for fiber in old_fibers
    )
    assert {
        family: len(records)
        for family, records in source_bindings["old"][
            "one_member_sources"
        ].items()
    } == {"fixed": 70, "singleton": 1}
    assert all(
        set(record)
        == {
            "identity",
            "member_id",
            "coefficient",
            "domain",
            "current_equality",
        }
        for records in source_bindings["old"]["one_member_sources"].values()
        for record in records
    )
    assert source_bindings["old"]["anchor_rows"] == 21
    assert len(source_bindings["old"]["anchor_provenance"]) == 21
    assert source_bindings["old"]["anchor_integral_sum"] == sum(
        row["coefficient"]
        for row in source_bindings["old"]["anchor_provenance"]
    )
    assert source_bindings["old"]["raw_provenance_counts"] == {
        "V": 167,
        "W": 397,
        "A": 21,
    }
    assert source_bindings["old"]["raw_ids_unique"] is True
    assert source_bindings["old"]["missing_raw_provenance"] == []

    b_fibers = source_bindings["b"]["collision_fibers"]
    assert len(b_fibers) == 53
    assert any(not fiber["active"] for fiber in b_fibers)
    assert all(
        fiber["member_coefficients"]
        == [list(pair) for pair in zip(fiber["members"], fiber["coefficients"])]
        and sum(fiber["coefficients"]) == fiber["integral_sum"]
        and fiber["parity"] == fiber["integral_sum"] % 2
        and fiber["active"] == bool(fiber["parity"])
        and fiber["label_equality_witness"]["equal"] is True
        for fiber in b_fibers
    )
    module.validate_source_bindings(source_bindings, catalog)


def test_source_binding_validation_rejects_resealed_semantic_mutations() -> None:
    module = load_generator()
    catalog = module.build_task4_schema_catalog(module.load_source_context())
    source_bindings = module.build_source_bindings(catalog)
    inactive_old = next(
        (family, index, fiber)
        for family, fibers in source_bindings["old"]["integral_fibers"].items()
        for index, fiber in enumerate(fibers)
        if not fiber["active"]
    )
    inactive_b_index = next(
        index
        for index, fiber in enumerate(source_bindings["b"]["collision_fibers"])
        if not fiber["active"]
    )

    mutations = []
    family, fiber_index, _ = inactive_old

    wrong_old_coefficient = copy.deepcopy(source_bindings)
    wrong_old_coefficient["old"]["integral_fibers"][family][fiber_index][
        "members"
    ][0]["coefficient"] += 2
    mutations.append(wrong_old_coefficient)

    wrong_old_domain = copy.deepcopy(source_bindings)
    wrong_old_domain["old"]["integral_fibers"][family][fiber_index]["members"][
        0
    ]["domain"] = {"op": "false"}
    mutations.append(wrong_old_domain)

    wrong_old_equality = copy.deepcopy(source_bindings)
    wrong_old_equality["old"]["integral_fibers"][family][fiber_index][
        "members"
    ][0]["current_equality"] = {"op": "false"}
    mutations.append(wrong_old_equality)

    wrong_b_alignment = copy.deepcopy(source_bindings)
    wrong_b_alignment["b"]["collision_fibers"][inactive_b_index][
        "member_coefficients"
    ][0][1] += 2
    mutations.append(wrong_b_alignment)

    wrong_anchor = copy.deepcopy(source_bindings)
    wrong_anchor["old"]["anchor_provenance"][0]["coefficient"] += 2
    mutations.append(wrong_anchor)

    for mutated in mutations:
        reseal_source_bindings(mutated)
        with pytest.raises(module.CertificateFailure):
            module.validate_source_bindings(mutated, catalog)


def test_typed_sha256_v1_has_frozen_literal_encoding_and_hash_vectors() -> None:
    module = load_generator()
    vectors = (
        (
            None,
            "4e",
            "8ce86a6ae65d3692e7305e2c58ac62eebd97d3d943e093f577da25c36988246b",
        ),
        (
            False,
            "4200",
            "f6c6e57cc3dac1d6a2349701056ff5a3e48134efe4496a8c0f5cb9fc9e6dfc12",
        ),
        (
            True,
            "4201",
            "4cb1fd840b329ec808f95c7a17d95ccc8848275c382ab11e4dfabd290c068070",
        ),
        (
            -42,
            "49000000032d3432",
            "e784f3ee909bd36a20a1b8744709944fa744303294c4a30d7db1d781018338b4",
        ),
        (
            "π",
            "5300000002cf80",
            "7c7ce74baef2b17651aa994a54f2a843ee4db132694817069a2cea9bd497ac97",
        ),
        (
            [None, True, -7, "π"],
            "4c000000044e420149000000022d375300000002cf80",
            "d7eafd067331b065d8f491697eec5c3c5ed6a6cf947534d9d21c979d245833b9",
        ),
        (
            {"β": False, "a": [1, None]},
            (
                "4d000000025300000001614c000000024900000001314e"
                "5300000002ceb24200"
            ),
            "84036cd670c5990f2f714a3f5407856268284749d99d4170db43b651cc5aa125",
        ),
    )

    for value, expected_hex, expected_sha256 in vectors:
        assert module.typed_encode(value).hex() == expected_hex
        assert module.typed_sha256(value) == expected_sha256


def test_compact_v2_catalog_binds_every_schema_major_cell_identity(
    monkeypatch,
) -> None:
    module = load_generator()
    schemas = {
        "z:pump": module.Schema(
            "z:pump", ("a",), (("p", CORE_R, (1, 0)),)
        ),
        "a:fixed": module.Schema(
            "a:fixed", ("a",), (("fixed", (2,), None),)
        ),
    }
    cells = tuple(reversed(module.make_cells(("a",))))
    templates = {
        (schema_id, cell.cell_id): module.build_template(schema, cell)
        for schema_id, schema in schemas.items()
        for cell in cells
    }
    monkeypatch.setattr(
        module.Template,
        "to_record",
        lambda _self: pytest.fail("compact-v2 must not call Template.to_record"),
    )

    catalog = module.build_compact_template_catalog(
        "unit", schemas, cells, templates
    )

    assert catalog["format"] == "task4-template-catalog-v2"
    assert catalog["typed_encoding"] == TYPED_ENCODING
    assert catalog["family"] == "unit"
    assert catalog["field_orders"] == TEMPLATE_FIELD_ORDERS
    assert [row[0] for row in catalog["schema_table"]] == [
        "a:fixed",
        "z:pump",
    ]
    assert [row[0] for row in catalog["cell_table"]] == [
        "age0",
        "age1",
        "age2",
        "age3",
    ]
    assert catalog["template_count"] == 8
    assert len(catalog["identity_witness_ids"]) == 8
    assert set(catalog["identity_witness_ids"]) == set(
        range(len(catalog["witness_table"]))
    )
    assert catalog["identity_order"] == "schema-major-cell-minor"
    independently_rehashed = copy.deepcopy(catalog)
    recompute_template_catalog_digests(independently_rehashed)
    assert independently_rehashed == catalog
    module.validate_compact_template_catalog(catalog)


def test_compact_v2_rejects_noncanonical_catalog_mutations() -> None:
    module = load_generator()
    schemas = {
        "z:pump": module.Schema(
            "z:pump", ("a",), (("p", CORE_R, (1, 0)),)
        ),
        "a:fixed": module.Schema(
            "a:fixed", ("a",), (("fixed", (2,), None),)
        ),
    }
    cells = module.make_cells(("a",))
    templates = {
        (schema_id, cell.cell_id): module.build_template(schema, cell)
        for schema_id, schema in schemas.items()
        for cell in cells
    }
    catalog = module.build_compact_template_catalog(
        "unit", schemas, cells, templates
    )
    assert len(catalog["witness_table"]) >= 2

    unknown_field = copy.deepcopy(catalog)
    unknown_field["extra"] = None

    missing_field = copy.deepcopy(catalog)
    missing_field.pop("typed_encoding")

    unused_witness = copy.deepcopy(catalog)
    unused_witness["witness_table"].append(
        copy.deepcopy(unused_witness["witness_table"][0])
    )
    unused_witness["witness_count"] += 1
    recompute_template_catalog_digests(unused_witness)

    non_ascii_schema = copy.deepcopy(catalog)
    non_ascii_schema["schema_table"][0][0] = "á:fixed"
    recompute_template_catalog_digests(non_ascii_schema)

    reindexed = copy.deepcopy(catalog)
    reindexed["witness_table"][0], reindexed["witness_table"][1] = (
        reindexed["witness_table"][1],
        reindexed["witness_table"][0],
    )
    reindexed["identity_witness_ids"] = [
        1 if witness_id == 0 else 0 if witness_id == 1 else witness_id
        for witness_id in reindexed["identity_witness_ids"]
    ]
    recompute_template_catalog_digests(reindexed)

    aliased_field_order = catalog
    aliased_field_order["field_orders"]["schema"].reverse()
    recompute_template_catalog_digests(aliased_field_order)

    for mutated in (
        unknown_field,
        missing_field,
        unused_witness,
        non_ascii_schema,
        reindexed,
        aliased_field_order,
    ):
        with pytest.raises(module.CertificateFailure):
            module.validate_compact_template_catalog(mutated)


def test_compact_v2_rejects_rehashed_nested_positional_mutations() -> None:
    module = load_generator()
    schemas = {
        "z:pump": module.Schema(
            "z:pump", ("a",), (("p", CORE_R, (1, 0)),)
        ),
        "a:fixed": module.Schema(
            "a:fixed", ("a",), (("fixed", (2,), None),)
        ),
    }
    cells = module.make_cells(("a",))
    templates = {
        (schema_id, cell.cell_id): module.build_template(schema, cell)
        for schema_id, schema in schemas.items()
        for cell in cells
    }
    catalog = module.build_compact_template_catalog(
        "unit", schemas, cells, templates
    )
    pumping_witness_id = next(
        witness_id
        for witness_id, witness in enumerate(catalog["witness_table"])
        if witness[2]
    )

    extra_pump_field = copy.deepcopy(catalog)
    extra_pump_field["witness_table"][pumping_witness_id][2][0].append(99)
    recompute_template_catalog_digests(extra_pump_field)

    non_bool_terminal_deletion = copy.deepcopy(catalog)
    non_bool_terminal_deletion["witness_table"][pumping_witness_id][1] = 1
    recompute_template_catalog_digests(non_bool_terminal_deletion)

    bool_block_letter = copy.deepcopy(catalog)
    bool_block_letter["schema_table"][0][2][0][1][0] = True
    recompute_template_catalog_digests(bool_block_letter)

    bool_cell_state = copy.deepcopy(catalog)
    bool_cell_state["cell_table"][0][2][0] = False
    recompute_template_catalog_digests(bool_cell_state)

    for mutated in (
        extra_pump_field,
        non_bool_terminal_deletion,
        bool_block_letter,
        bool_cell_state,
    ):
        with pytest.raises(module.CertificateFailure):
            module.validate_compact_template_catalog(mutated)


def test_compact_v2_rejects_rehashed_wrong_terminal_value() -> None:
    module = load_generator()
    schema = module.Schema(
        "fixed", ("a",), (("fixed", (2,), None),)
    )
    cells = module.make_cells(("a",))
    catalog = module.build_compact_template_catalog(
        "unit",
        {schema.schema_id: schema},
        cells,
        {
            (schema.schema_id, cell.cell_id): module.build_template(
                schema, cell
            )
            for cell in cells
        },
    )
    mutated = copy.deepcopy(catalog)
    assert mutated["witness_table"] == [[2, False, []]]
    mutated["witness_table"][0][0] = -2
    mutated["witness_table"][0][1] = False
    recompute_template_catalog_digests(mutated)

    with pytest.raises(module.CertificateFailure):
        module.validate_compact_template_catalog(mutated)


def test_compact_slice_includes_all_tied_maximum_pump_schemas() -> None:
    module = load_generator()
    cells = module.make_cells(("a",))
    schemas = {
        f"s{index:02d}": module.Schema(
            f"s{index:02d}", ("a",), (("fixed", (2,), None),)
        )
        for index in range(10)
    }
    schemas["s01"] = module.Schema(
        "s01", ("a",), (("r", CORE_R, (1, 0)),)
    )
    schemas["s02"] = module.Schema(
        "s02",
        ("a",),
        (("fixed", (2, -2), None), ("s", CORE_S, (1, 0))),
    )
    family = module.Task4FamilyCatalog(
        family="unit",
        variables=("a",),
        cells=cells,
        schemas=schemas,
        old_tokens=(),
        b_tokens=(),
        old_schema_refs={},
        b_schema_refs={},
        old_footprint_bindings={},
    )
    catalog = module.Task4SchemaCatalog(
        families={"unit": family},
        dependency_digests={},
        old_source_proof={},
        b_source_proof={},
        occurrence_leafs={},
        occurrence_polarities={},
        occurrence_slots={},
        fixed_metadata={},
        chronology_digest="",
        b_identity_table=(),
        b_identity_digest="",
    )

    metrics = module.measure_compact_catalog_slice(catalog)
    family_metrics = metrics["families"]["unit"]

    assert metrics["selection"] == (
        "every-eighth-ascii-schema-plus-all-maximum-pump-schemas"
    )
    assert family_metrics["highest_pump_count"] == 1
    assert family_metrics["highest_pump_schema_ids"] == ["s01", "s02"]
    assert family_metrics["sample_schema_ids"] == ["s00", "s01", "s02", "s08"]


def test_compact_v2_deterministic_slice_clears_projection_gate() -> None:
    module = load_generator()
    measure = module.measure_compact_catalog_slice
    catalog = module.build_task4_schema_catalog(module.load_source_context())

    metrics = measure(catalog)
    print(json.dumps(metrics, sort_keys=True))

    assert metrics["selection"] == (
        "every-eighth-ascii-schema-plus-all-maximum-pump-schemas"
    )
    assert metrics["total_schema_count"] == 1304
    assert metrics["total_identity_count"] == 48252
    assert metrics["sample_identity_count"] > 0
    assert metrics["sample_catalog_bytes"] > 0
    assert metrics["extraction_intern_seconds"] >= 0
    assert metrics["canonical_serialization_seconds"] >= 0
    assert metrics["projected_full_overhead_seconds"] >= 0
    assert metrics["doubled_projected_full_overhead_seconds"] < 3.0
    for family, family_metrics in metrics["families"].items():
        item = catalog.families[family]
        schema_ids = sorted(item.schemas)
        assert set(schema_ids[::8]) <= set(family_metrics["sample_schema_ids"])
        assert set(family_metrics["highest_pump_schema_ids"]) <= set(
            family_metrics["sample_schema_ids"]
        )
        assert family_metrics["total_identity_count"] == (
            len(item.schemas) * len(item.cells)
        )
        assert family_metrics["sample_identity_count"] == (
            len(family_metrics["sample_schema_ids"]) * len(item.cells)
        )


def test_cells_cover_exact_threshold_states_and_p_domain() -> None:
    module = load_module("load_generator", GENERATOR)
    assert len(module.make_cells(("a", "n"))) == 16
    assert len(module.make_cells(("h", "k", "n"))) == 64
    p_cells = tuple(
        cell
        for cell in module.make_cells(("a", "h", "r"))
        if module.p_domain_nonempty(cell)
    )
    assert len(p_cells) == 54
    assert "age3_h0_r0" not in {cell.cell_id for cell in p_cells}
    assert "age3_h0_rge3" in {cell.cell_id for cell in p_cells}


def test_bucket_masks_form_one_exact_84_token_partition() -> None:
    module = load_module("load_generator_masks", GENERATOR)
    records = tuple(
        {"token_index": index, "bit": index % 2, "chronology": "fixed"}
        for index in range(84)
    )
    buckets = module.bucketize_records(records, key_fields=("bit", "chronology"))
    assert sum(bucket.count for bucket in buckets) == 84
    assert sum(
        bin(bucket.mask).count("1")  # noqa: FURB161 - Python 3.9 compatibility
        for bucket in buckets
    ) == 84
    assert functools.reduce(operator.or_, (bucket.mask for bucket in buckets), 0) == (1 << 84) - 1


def test_integral_collision_fibers_cancel_before_parity() -> None:
    module = load_generator()
    cell = module.make_cells(("a", "n"))[0]
    true_domain = {"op": "true"}
    current_equality = {"op": "equal_module_term"}
    rows = (
        module.TokenRef(
            token_id="cancel:plus",
            family="fixture",
            coefficient=1,
            slot=2,
            occurrence=1,
            polarity=1,
            module_schema="module:equal",
            label_schema="label:equal:left",
            domain=true_domain,
            current_equality=current_equality,
        ),
        module.TokenRef(
            token_id="cancel:minus",
            family="fixture",
            coefficient=-1,
            slot=2,
            occurrence=1,
            polarity=1,
            module_schema="module:equal",
            label_schema="label:equal:right",
            domain=true_domain,
            current_equality=current_equality,
        ),
        module.TokenRef(
            token_id="active:three",
            family="fixture",
            coefficient=3,
            slot=3,
            occurrence=9,
            polarity=-1,
            module_schema="module:active",
            label_schema="label:active",
            domain=true_domain,
            current_equality=current_equality,
        ),
    )
    templates = {
        ("module:equal", cell.cell_id): module.Template(
            "module:equal", ("module", "equal")
        ),
        ("label:equal:left", cell.cell_id): module.Template(
            "label:equal:left", ("label", "equal")
        ),
        ("label:equal:right", cell.cell_id): module.Template(
            "label:equal:right", ("label", "equal")
        ),
        ("module:active", cell.cell_id): module.Template(
            "module:active", ("module", "active")
        ),
        ("label:active", cell.cell_id): module.Template(
            "label:active", ("label", "active")
        ),
    }

    fibers = module.aggregate_integral_fibers(rows, templates, cell)

    assert len(fibers) == 2
    absorbed = next(fiber for fiber in fibers if not fiber.active)
    active = next(fiber for fiber in fibers if fiber.active)
    assert absorbed.member_ids == ("cancel:minus", "cancel:plus")
    assert absorbed.coefficients == (-1, 1)
    assert absorbed.integral_sum == 0
    assert absorbed.parity == 0
    assert absorbed.label_equality_witness["equal"] is True
    assert active.member_ids == ("active:three",)
    assert active.integral_sum == 3
    assert active.parity == 1


def test_bound_source_has_84_collision_first_b_tokens() -> None:
    module = load_generator()
    context = module.load_source_context()
    assert context.source_digests == EXPECTED_SOURCE_DIGESTS
    assert all(
        re.fullmatch(r"[0-9a-f]{64}", digest)
        for digest in context.source_digests.values()
    )
    assert (
        set(context.manifests["inverse"]["collision_fibers"])
        == EXPECTED_INVERSE_CELL_IDS
    )
    assert len(context.raw_rows) == 585
    assert all(row["domain"] and row["current_equality"] for row in context.raw_rows)

    tokens, proof = module.build_b_catalog(context)
    assert len(tokens) == 84
    assert proof["occurrences"] == 16
    assert proof["path_fibers"] == 53
    assert proof["active_path_fibers"] == 36
    assert proof["slot_zero_tokens"] == 12
    assert proof["bound_cells"] == 9
    assert sum(token.coefficient % 2 for token in tokens) == 84
    assert all(
        all(isinstance(coefficient, int) for coefficient in fiber["coefficients"])
        and sum(fiber["coefficients"]) == fiber["integral_sum"]
        for fiber in proof["collision_fibers"]
    )

    old_rows, old_proof = module.build_old_rows(context)
    assert len(old_rows) == 236
    assert old_proof["raw_family_rows"] == {"P": 100, "C": 113, "Q": 92}
    assert old_proof["active_family_fibers"] == {
        "fixed": 70,
        "base": 2,
        "singleton": 1,
        "P": 32,
        "C": 39,
        "Q": 92,
    }
    assert old_proof["anchor_rows"] == 21
    assert old_proof["anchor_integral_sum"] == 2
    assert old_proof["missing_raw_provenance"] == []


def test_b_activity_is_derived_from_integer_coefficients_before_parity() -> None:
    module = load_generator()
    context = module.load_source_context()
    inverse_manifest = copy.deepcopy(context.manifests["inverse"])
    target_members = ["nu1:k10:delta0"]
    changed = 0
    for fibers in inverse_manifest["collision_fibers"].values():
        for fiber in fibers:
            if fiber["members"] == target_members:
                fiber["activity_parity"] = 0
                changed += 1
    assert changed == 9
    tampered = with_manifest(context, "inverse", inverse_manifest)

    with pytest.raises(ValueError, match="integer-first B parity mismatch"):
        module.build_b_catalog(tampered)


def test_old_family_fibers_preserve_signed_integer_members_before_parity() -> None:
    module = load_generator()
    context = module.load_source_context()
    _, proof = module.build_old_rows(context)
    target_members = ["W:nu2:P:9:o+1", "W:nu6:P:9:o+1"]
    fiber = next(
        item
        for item in proof["integral_fibers"]["P"]
        if item["member_ids"] == target_members
    )

    assert fiber["coefficients"] == [-1, -1]
    assert fiber["integral_sum"] == -2
    assert fiber["parity"] == 0
    assert fiber["active"] is False


def test_bound_source_replays_exact_v_rows_and_unique_family_ids() -> None:
    module = load_generator()
    context = module.load_source_context()
    _, proof = module.build_old_rows(context)
    assert proof["raw_provenance_counts"] == {"V": 167, "W": 397, "A": 21}
    assert proof["raw_ids_unique"] is True

    raw_manifest = copy.deepcopy(context.manifests["raw"])
    raw_manifest["source_schema_manifest"]["V_rows"][0]["coefficient"] += 2
    tampered = with_manifest(context, "raw", raw_manifest)
    with pytest.raises(ValueError, match="live V rows differ"):
        module.build_old_rows(tampered)


def test_b_catalog_requires_exact_inverse_q_cell_ids() -> None:
    module = load_generator()
    context = module.load_source_context()
    inverse_manifest = copy.deepcopy(context.manifests["inverse"])
    collision_cells = inverse_manifest["collision_fibers"]
    collision_cells["copied_cell"] = collision_cells.pop("a0_n1")
    assert len(collision_cells) == 9

    with pytest.raises(ValueError, match="exact inverse-Q cell IDs"):
        module.build_b_catalog(with_manifest(context, "inverse", inverse_manifest))


def test_b_catalog_derives_and_rejects_member_label_inequality(monkeypatch) -> None:
    module = load_generator()
    context = module.load_source_context()
    _, proof = module.build_b_catalog(context)
    assert all(
        fiber["label_equality_witness"]["method"]
        == "canonical_member_action_blocks_all_inverse_cells"
        and fiber["label_equality_witness"]["checks"]
        for fiber in proof["collision_fibers"]
    )

    inverse = context.modules["inverse"]
    original_build_templates = inverse.build_templates

    def tampered_build_templates(generator):
        templates, metadata = original_build_templates(generator)
        templates[("partner:action:nu4:k12:delta0:o1", "a0_n0")] = templates[
            ("terminal:module", "a0_n0")
        ]
        return templates, metadata

    monkeypatch.setattr(inverse, "build_templates", tampered_build_templates)
    with pytest.raises(ValueError, match="unequal transported labels"):
        module.build_b_catalog(context)


def test_b_fiber_serialization_keeps_member_coefficient_alignment() -> None:
    module = load_generator()
    context = module.load_source_context()
    inverse_manifest = copy.deepcopy(context.manifests["inverse"])
    sorted_members = [
        "nu3:k10:delta0",
        "nu4:k12:delta0",
        "nu5:k7:delta0",
    ]
    changed = 0
    for fibers in inverse_manifest["collision_fibers"].values():
        for fiber in fibers:
            if sorted(fiber["members"]) == sorted_members:
                fiber["members"] = list(reversed(sorted_members))
                changed += 1
    assert changed == 9

    _, proof = module.build_b_catalog(
        with_manifest(context, "inverse", inverse_manifest)
    )
    fiber = next(
        item
        for item in proof["collision_fibers"]
        if item["members"] == sorted_members
    )
    assert list(zip(fiber["members"], fiber["coefficients"])) == [
        ("nu3:k10:delta0", 1),
        ("nu4:k12:delta0", 1),
        ("nu5:k7:delta0", -1),
    ]


def synthetic_two_power_schema(module):
    return module.Schema(
        schema_id="synthetic:two-power",
        variables=("a", "n"),
        blocks=(
            ("fixed", (3,), None),
            ("r", CORE_R, (1, 0, 0)),
            ("fixed", (3,), None),
            ("s", CORE_S, (0, 1, 0)),
            ("fixed", (1,), None),
        ),
    )


def test_primitive_cores_and_two_distinct_intact_boundaries_pump() -> None:
    module = load_generator()
    for core in (CORE_R, CORE_S):
        assert core
        assert len(core) == 8
        assert all(
            right != literal_inverse(left)
            for left, right in zip(core, (*core[1:], core[:1]))
        )

    schema = synthetic_two_power_schema(module)
    cell = next(
        item for item in module.make_cells(schema.variables)
        if item.cell_id == "age3_nge3"
    )
    template = module.build_template(schema, cell)

    assert template.base_word == literal_schema_word(schema, (3, 3))
    assert module.expand_template(template, (3, 3)) == literal_schema_word(
        schema, (3, 3)
    )
    assert module.expand_template(template, (4, 4)) == literal_schema_word(
        schema, (4, 4)
    )
    assert template.terminal_full_letter == 1
    assert template.terminal_c_deleted is True
    assert [witness.to_record() for witness in template.pumping_witnesses] == [
        {
            "block_name": "r",
            "block_index": 1,
            "core": list(CORE_R),
            "base_copies": 3,
            "slopes": [1, 0],
            "split_position": 9,
            "left_copy_id": 0,
            "right_copy_id": 1,
            "left_core_offset": 7,
            "right_core_offset": 0,
        },
        {
            "block_name": "s",
            "block_index": 3,
            "core": list(CORE_S),
            "base_copies": 3,
            "slopes": [0, 1],
            "split_position": 34,
            "left_copy_id": 0,
            "right_copy_id": 1,
            "left_core_offset": 7,
            "right_core_offset": 0,
        },
    ]
    assert module.verify_intact_boundaries(schema, cell, template) == (
        template.pumping_witnesses
    )


def test_all_approved_powered_schemas_have_intact_threshold_three_boundaries() -> None:
    module = load_generator()
    context = module.load_source_context()
    inverse = context.modules["inverse"]
    aggregate = context.modules["aggregate"]
    raw = context.modules["raw"]
    inverse_schemas, _ = inverse.schema_words(raw)
    real_powered_schemas = {
        **inverse_schemas,
        **aggregate.g_zero_schemas(inverse, raw),
    }
    schemas = {
        schema_id: module.schema_from_powered(
            powered,
            variables=("a", "n"),
            q_exponent=(1, 0, 0),
            p_exponent=(1, 1, powered.p_offset),
        )
        for schema_id, powered in real_powered_schemas.items()
    }
    templates = {
        (schema_id, cell.cell_id): module.build_template(schema, cell)
        for schema_id, schema in schemas.items()
        for cell in module.make_cells(("a", "n"))
    }

    assert len(schemas) == 583
    assert len(templates) == 9328
    assert {
        witness.core
        for template in templates.values()
        for witness in template.pumping_witnesses
    } == {CORE_R, CORE_S}


def test_task4_catalog_builds_every_decorated_family_schema_and_cell() -> None:
    module = load_generator()
    catalog = module.build_task4_schema_catalog(module.load_source_context())

    assert set(catalog.families) == {
        "fixed",
        "base",
        "singleton",
        "P",
        "C",
        "Q",
    }
    assert {
        family: len(item.cells)
        for family, item in catalog.families.items()
    } == {
        "fixed": 16,
        "base": 16,
        "singleton": 16,
        "P": 54,
        "C": 16,
        "Q": 64,
    }
    assert {
        family: len(item.old_tokens)
        for family, item in catalog.families.items()
    } == {
        "fixed": 70,
        "base": 2,
        "singleton": 1,
        "P": 32,
        "C": 39,
        "Q": 92,
    }
    assert all(
        len(item.b_tokens) == 84
        for item in catalog.families.values()
    )
    assert all(
        token.token_id in item.old_schema_refs
        and item.old_schema_refs[token.token_id].label_schemas
        for item in catalog.families.values()
        for token in item.old_tokens
    )
    assert all(
        token.token_id in item.b_schema_refs
        and item.b_schema_refs[token.token_id].module_schema is not None
        and len(item.b_schema_refs[token.token_id].label_schemas) == 1
        for item in catalog.families.values()
        for token in item.b_tokens
    )
    assert {
        family: len(item.schemas)
        for family, item in catalog.families.items()
    } == {
        "fixed": 192,
        "base": 128,
        "singleton": 129,
        "P": 218,
        "C": 239,
        "Q": 398,
    }
    records = module.build_task4_template_records(catalog)
    assert {
        family: len(family_records)
        for family, family_records in records.items()
    } == {
        "fixed": 3072,
        "base": 2048,
        "singleton": 2064,
        "P": 11772,
        "C": 3824,
        "Q": 25472,
    }
    assert sum(map(len, records.values())) == 48252
    assert all(
        "terminal_full_letter" in record
        and "terminal_c_deleted" in record
        and "pumping_witnesses" in record
        for family_records in records.values()
        for record in family_records.values()
    )


def test_template_proof_record_replays_and_rejects_terminal_mutations() -> None:
    module = load_generator()
    schema = synthetic_two_power_schema(module)
    cell = next(
        item for item in module.make_cells(schema.variables)
        if item.cell_id == "age3_nge3"
    )
    template = module.build_template(schema, cell)
    record = template.to_record()

    assert set(record) == {
        "schema_id",
        "cell_id",
        "variables",
        "tagged_base_word",
        "base_word",
        "normalized_blocks",
        "terminal_full_letter",
        "terminal_c_deleted",
        "pumping_witnesses",
    }
    assert record["terminal_full_letter"] == 1
    assert record["terminal_c_deleted"] is True
    assert record["base_word"] == list(literal_schema_word(schema, (3, 3)))
    assert module.verify_template_record(schema, cell, record) == template

    mutations = []
    for field in ("terminal_full_letter", "terminal_c_deleted"):
        mutated = dict(record)
        del mutated[field]
        mutations.append(mutated)
    changed_letter = dict(record)
    changed_letter["terminal_full_letter"] = 2
    mutations.append(changed_letter)
    changed_branch = dict(record)
    changed_branch["terminal_c_deleted"] = False
    mutations.append(changed_branch)
    for mutated in mutations:
        with pytest.raises(ValueError, match="template proof record differs"):
            module.verify_template_record(schema, cell, mutated)


def test_compare_templates_serializes_exactly_three_all_power_methods() -> None:
    module = load_generator()
    cell = next(
        item for item in module.make_cells(("a",))
        if item.cell_id == "age3"
    )
    strict_left = module.build_template(
        module.Schema("strict:left", ("a",), (("r", CORE_R, (1, 0)),)),
        cell,
    )
    strict_right = module.build_template(
        module.Schema("strict:right", ("a",), (("fixed", (3,), None),)),
        cell,
    )
    identical_left = module.build_template(
        module.Schema(
            "identical:left",
            ("a",),
            (("fixed", CORE_R, None), ("r", CORE_R, (1, 0))),
        ),
        cell,
    )
    identical_right = module.build_template(
        module.Schema(
            "identical:right", ("a",), (("r", CORE_R, (1, 1)),)
        ),
        cell,
    )
    mismatch_left = module.build_template(
        module.Schema(
            "mismatch:left",
            ("a",),
            (("r", CORE_R, (1, 0)), ("fixed", (-3,), None)),
        ),
        cell,
    )
    mismatch_right = module.build_template(
        module.Schema(
            "mismatch:right",
            ("a",),
            (("r", CORE_R, (1, 0)), ("fixed", (3,), None)),
        ),
        cell,
    )

    strict = module.compare_templates(strict_left, strict_right, cell)
    identical = module.compare_templates(identical_left, identical_right, cell)
    mismatch = module.compare_templates(mismatch_left, mismatch_right, cell)

    assert strict == {
        "method": "strict_affine_length",
        "order": 1,
        "difference": [8, -1],
    }
    assert identical == {
        "method": "identical_pumped_blocks",
        "order": 0,
        "normalized_blocks": [
            {"block_name": "r", "word": list(CORE_R), "affine": [1, 1]}
        ],
    }
    assert mismatch == {
        "method": "fixed_mismatch_after_pumped_prefix",
        "order": -1,
        "prefix_length": [8, 0],
        "mismatch_letters": [-3, 3],
    }


def test_missing_intact_boundary_is_rejected() -> None:
    module = load_generator()
    schema = module.Schema(
        "mutation:missing-boundary",
        ("a",),
        (("r", CORE_R, (1, -2)),),
    )
    cell = next(
        item for item in module.make_cells(("a",))
        if item.cell_id == "age3"
    )
    with pytest.raises(ValueError, match="missing intact boundary"):
        module.build_template(schema, cell)


def test_coincident_selected_boundaries_are_rejected() -> None:
    module = load_generator()
    schema = synthetic_two_power_schema(module)
    cell = next(
        item for item in module.make_cells(schema.variables)
        if item.cell_id == "age3_nge3"
    )
    template = module.build_template(schema, cell)
    first, second = template.pumping_witnesses
    tampered = replace(
        template,
        pumping_witnesses=(
            first,
            replace(second, split_position=first.split_position),
        ),
    )
    with pytest.raises(ValueError, match="coincident intact boundaries"):
        module.verify_intact_boundaries(schema, cell, tampered)


def test_terminal_c_branch_change_is_rejected() -> None:
    module = load_generator()
    schema = synthetic_two_power_schema(module)
    cell = next(
        item for item in module.make_cells(schema.variables)
        if item.cell_id == "age3_nge3"
    )
    template = module.build_template(schema, cell)
    tampered = replace(
        template,
        terminal_full_letter=2,
        terminal_c_deleted=False,
    )
    with pytest.raises(ValueError, match="terminal-c branch changed"):
        module.verify_intact_boundaries(schema, cell, tampered)


def test_nonconstant_affine_length_sign_is_rejected() -> None:
    module = load_generator()
    cell = next(
        item for item in module.make_cells(("a",))
        if item.cell_id == "age3"
    )
    left = module.build_template(
        module.Schema("sign:left", ("a",), (("r", CORE_R, (1, 0)),)),
        cell,
    )
    right = replace(left, schema_id="sign:right", length_affine=(7, 3))
    with pytest.raises(ValueError, match="no fixed strict sign"):
        module.compare_templates(left, right, cell)


def test_first_mismatch_inside_a_powered_block_is_rejected() -> None:
    module = load_generator()
    changed_core = (1, 2, 1, -2, -2, 3, 1, 2)
    cell = next(
        item for item in module.make_cells(("a",))
        if item.cell_id == "age3"
    )
    left = module.build_template(
        module.Schema("inside:left", ("a",), (("r", CORE_R, (1, 0)),)),
        cell,
    )
    right = module.build_template(
        module.Schema(
            "inside:right", ("a",), (("r", changed_core, (1, 0)),)
        ),
        cell,
    )
    left = replace(left, blocks=(("r", CORE_R, (1, 0)),))
    right = replace(right, blocks=(("r", changed_core, (1, 0)),))
    with pytest.raises(ValueError, match="mismatch lies inside powered block"):
        module.compare_templates(left, right, cell)


def test_manifest_census_expands_every_catalog_occurrence_footprint() -> None:
    module = load_generator()
    catalog = module.build_task4_schema_catalog(module.load_source_context())

    manifest = module.build_manifest(catalog=catalog)
    summary = manifest["summary"]

    assert summary["load_rows"] == {
        "fixed": 1120,
        "base": 32,
        "singleton": 16,
        "P": 1728,
        "C": 624,
        "Q": 5888,
    }
    assert summary["total_load_rows"] == 9408
    assert summary["footprint_sizes"] == {
        "fixed": {"1": 70},
        "base": {"2": 2},
        "singleton": {"6": 1},
        "P": {"2": 32},
        "C": {"2": 39},
        "Q": {"2": 92},
    }
    assert summary["occurrence_loads"] == {
        "fixed": 1120,
        "base": 64,
        "singleton": 96,
        "P": 3456,
        "C": 1248,
        "Q": 11776,
    }
    assert summary["total_occurrence_loads"] == 17760
    assert summary["b_tokens_per_occurrence"] == 84
    assert summary["active_comparisons"] == 1491840
    assert summary["template_counts"] == {
        "fixed": 3072,
        "base": 2048,
        "singleton": 2064,
        "P": 11772,
        "C": 3824,
        "Q": 25472,
    }
    assert summary["total_templates"] == 48252
    b_identity_table = manifest["b_identity_table"]
    assert len(b_identity_table) == 84
    assert [row["token_index"] for row in b_identity_table] == list(range(84))
    assert len({row["token_id"] for row in b_identity_table}) == 84
    assert b_identity_table[0]["token_id"] == "b0:g0:00:o11"
    assert b_identity_table[-1]["token_id"] == "b0:path:f052:o16"
    assert manifest["b_identity_digest"] == (
        "a8c7f0ad73b9f9b88b758f7983724aa921c6dfa3a2ab7a4eeceb6cfb0f973bbd"
    )
    assert manifest["dependency_digests"] == EXPECTED_SOURCE_DIGESTS
    template_catalogs = [
        ledger["template_catalog"]
        for ledger in manifest["family_ledgers"].values()
    ]
    assert sum(catalog["template_count"] for catalog in template_catalogs) == 48252
    assert all(
        catalog["format"] == "task4-template-catalog-v2"
        and catalog["field_orders"] == TEMPLATE_FIELD_ORDERS
        and catalog["identity_order"] == "schema-major-cell-minor"
        and len(catalog["schema_table"]) == catalog["schema_count"]
        and len(catalog["cell_table"]) == catalog["cell_count"]
        and len(catalog["identity_witness_ids"])
        == catalog["template_count"]
        and len(catalog["witness_table"]) == catalog["witness_count"]
        and set(catalog["identity_witness_ids"])
        == set(range(catalog["witness_count"]))
        and [row[0] for row in catalog["schema_table"]]
        == sorted(row[0] for row in catalog["schema_table"])
        and [row[0] for row in catalog["cell_table"]]
        == sorted(row[0] for row in catalog["cell_table"])
        for catalog in template_catalogs
    )
    pumping_records = [
        record
        for catalog in template_catalogs
        for record in catalog["witness_table"]
        if record[2]
    ]
    assert pumping_records
    assert all(
        len(record) == 3
        and all(len(pump) == 8 for pump in record[2])
        for record in pumping_records
    )
    for template_catalog in template_catalogs:
        independently_rehashed = copy.deepcopy(template_catalog)
        recompute_template_catalog_digests(independently_rehashed)
        assert independently_rehashed == template_catalog
    assert manifest["status"] == "generated-awaiting-independent-replay"
    assert "independent_verifier_attestation" not in manifest
    assert not manifest["status"].startswith("proved")
    assert {
        family: {cell["value"] for cell in ledger["cells"]}
        for family, ledger in manifest["family_ledgers"].items()
        if family != "C"
    } == {
        "fixed": {0},
        "base": {0},
        "singleton": {1},
        "P": {0},
        "Q": {0},
    }
    assert {
        cell["cell_id"]
        for cell in manifest["family_ledgers"]["C"]["cells"]
        if cell["value"]
    } == {"age0_n0", "age0_n1", "age0_n2", "age0_nge3"}


def test_comparison_records_pin_all_five_chronology_branches() -> None:
    module = load_generator()
    cell = next(
        item for item in module.make_cells(("a",)) if item.cell_id == "age0"
    )
    templates = {
        schema_id: module.build_template(
            module.Schema(
                schema_id, ("a",), (("fixed", (letter,), None),)
            ),
            cell,
        )
        for schema_id, letter in {
            "module:2": 2,
            "module:3": 3,
            "label:2": 2,
            "label:3": 3,
        }.items()
    }
    fixed_old = {
        "token_id": "old:fixed",
        "source_class": "fixed",
        "coordinate": ["fixed", 1, 1],
        "leaf": 1,
        "occurrence": None,
        "polarity": None,
        "module_schema": None,
        "label_schema": "label:2",
    }
    correction_old = {
        "token_id": "old:correction",
        "source_class": "old_path",
        "coordinate": ["correction", 1, "module:2"],
        "leaf": 2,
        "occurrence": 1,
        "polarity": 1,
        "module_schema": "module:2",
        "label_schema": "label:2",
    }
    positive_new = {
        "token_id": "b:positive",
        "token_index": 0,
        "source_class": "b_path",
        "coordinate": ["correction", 1, "module:3"],
        "leaf": 2,
        "occurrence": 1,
        "polarity": 1,
        "module_schema": "module:3",
        "label_schema": "label:3",
    }
    cases = (
        (
            fixed_old,
            positive_new,
            {
                "token_index": 0,
                "old_occurrence": None,
                "old_leaf": 1,
                "b_source_class": "b_path",
                "b_coordinate": ["correction", 1, "module:3"],
                "equality_exclusion": False,
                "old_polarity": None,
                "module_method": None,
                "module_order": None,
                "chronology": "fixed_vs_correction_literal_leaf_order",
                "chronology_order": -1,
                "label_method": "fixed_mismatch_after_pumped_prefix",
                "label_order": -1,
                "contribution_bit": 1,
            },
        ),
        (
            correction_old,
            {
                **positive_new,
                "token_id": "b:distinct",
                "coordinate": ["correction", 2, "module:3"],
                "leaf": 3,
                "occurrence": 2,
            },
            {
                "token_index": 0,
                "old_occurrence": 1,
                "old_leaf": 2,
                "b_source_class": "b_path",
                "b_coordinate": ["correction", 2, "module:3"],
                "equality_exclusion": False,
                "old_polarity": 1,
                "module_method": None,
                "module_order": None,
                "chronology": "distinct_occurrences_literal_AST_order",
                "chronology_order": -1,
                "label_method": "fixed_mismatch_after_pumped_prefix",
                "label_order": -1,
                "contribution_bit": 1,
            },
        ),
        (
            correction_old,
            {
                **positive_new,
                "token_id": "b:equal",
                "coordinate": ["correction", 1, "module:2"],
                "module_schema": "module:2",
                "label_schema": "label:2",
            },
            {
                "token_index": 0,
                "old_occurrence": 1,
                "old_leaf": 2,
                "b_source_class": "b_path",
                "b_coordinate": ["correction", 1, "module:2"],
                "equality_exclusion": True,
                "old_polarity": 1,
                "module_method": "identical_pumped_blocks",
                "module_order": 0,
                "chronology": "equal_coordinate_excluded",
                "chronology_order": 0,
                "label_method": "identical_pumped_blocks",
                "label_order": 0,
                "contribution_bit": 0,
            },
        ),
        (
            correction_old,
            positive_new,
            {
                "token_index": 0,
                "old_occurrence": 1,
                "old_leaf": 2,
                "b_source_class": "b_path",
                "b_coordinate": ["correction", 1, "module:3"],
                "equality_exclusion": False,
                "old_polarity": 1,
                "module_method": "fixed_mismatch_after_pumped_prefix",
                "module_order": -1,
                "chronology": "same_occurrence_increasing",
                "chronology_order": -1,
                "label_method": "fixed_mismatch_after_pumped_prefix",
                "label_order": -1,
                "contribution_bit": 1,
            },
        ),
        (
            {**correction_old, "polarity": -1, "label_schema": "label:3"},
            {**positive_new, "polarity": -1, "label_schema": "label:2"},
            {
                "token_index": 0,
                "old_occurrence": 1,
                "old_leaf": 2,
                "b_source_class": "b_path",
                "b_coordinate": ["correction", 1, "module:3"],
                "equality_exclusion": False,
                "old_polarity": -1,
                "module_method": "fixed_mismatch_after_pumped_prefix",
                "module_order": -1,
                "chronology": "same_occurrence_decreasing",
                "chronology_order": 1,
                "label_method": "fixed_mismatch_after_pumped_prefix",
                "label_order": 1,
                "contribution_bit": 1,
            },
        ),
    )

    assert [
        module.comparison_record(old, new, templates, cell)
        for old, new, _ in cases
    ] == [expected for _, _, expected in cases]


def test_histogram_for_load_serializes_one_complete_84_token_partition() -> None:
    module = load_generator()
    cell = next(
        item for item in module.make_cells(("a",)) if item.cell_id == "age0"
    )
    templates = {
        schema_id: module.build_template(
            module.Schema(
                schema_id, ("a",), (("fixed", (letter,), None),)
            ),
            cell,
        )
        for schema_id, letter in {
            "module:2": 2,
            "module:3": 3,
            "label:2": 2,
            "label:3": 3,
        }.items()
    }
    old = {
        "token_id": "old:correction",
        "source_class": "old_path",
        "coordinate": ["correction", 1, "module:2"],
        "leaf": 2,
        "occurrence": 1,
        "polarity": 1,
        "module_schema": "module:2",
        "label_schema": "label:2",
    }
    new_tokens = tuple(
        {
            "token_id": f"b:{index:02d}",
            "token_index": index,
            "source_class": "b_path",
            "coordinate": ["correction", 2, "module:3"],
            "leaf": 3,
            "occurrence": 2,
            "polarity": 1,
            "module_schema": "module:3",
            "label_schema": "label:3",
        }
        for index in range(84)
    )

    histogram = module.histogram_for_load(old, new_tokens, templates, cell)

    assert histogram == {
        "old_occurrence": 1,
        "old_leaf": 2,
        "old_polarity": 1,
        "comparison_count": 84,
        "one_count": 84,
        "value": 0,
        "buckets": [
            {
                "key": {
                    "old_occurrence": 1,
                    "old_leaf": 2,
                    "b_source_class": "b_path",
                    "b_coordinate": ["correction", 2, "module:3"],
                    "equality_exclusion": False,
                    "old_polarity": 1,
                    "module_method": None,
                    "module_order": None,
                    "chronology": "distinct_occurrences_literal_AST_order",
                    "chronology_order": -1,
                    "label_method": "fixed_mismatch_after_pumped_prefix",
                    "label_order": -1,
                    "contribution_bit": 1,
                },
                "count": 84,
                "mask": "fffffffffffffffffffff",
            }
        ],
    }


def literal_complete_histogram() -> dict:
    return {
        "old_occurrence": 1,
        "old_leaf": 2,
        "old_polarity": 1,
        "comparison_count": 84,
        "one_count": 84,
        "value": 0,
        "buckets": [
            {
                "key": {
                    "old_occurrence": 1,
                    "old_leaf": 2,
                    "b_source_class": "b_path",
                    "b_coordinate": ["fixture"],
                    "equality_exclusion": False,
                    "old_polarity": 1,
                    "module_method": None,
                    "module_order": None,
                    "chronology": "distinct_occurrences_literal_AST_order",
                    "chronology_order": -1,
                    "label_method": "fixed_mismatch_after_pumped_prefix",
                    "label_order": -1,
                    "contribution_bit": 1,
                },
                "count": 84,
                "mask": "fffffffffffffffffffff",
            }
        ],
    }


def test_histogram_validation_rejects_missing_and_duplicated_mask_bits() -> None:
    module = load_generator()
    valid = literal_complete_histogram()
    assert module.validate_histogram(valid) == valid

    missing = copy.deepcopy(valid)
    missing["buckets"][0]["count"] = 83
    missing["buckets"][0]["mask"] = "7ffffffffffffffffffff"
    with pytest.raises(module.CertificateFailure, match="do not cover"):
        module.validate_histogram(missing)

    duplicated = copy.deepcopy(valid)
    duplicate = copy.deepcopy(duplicated["buckets"][0])
    duplicate["count"] = 1
    duplicate["mask"] = "000000000000000000001"
    duplicated["buckets"].append(duplicate)
    with pytest.raises(module.CertificateFailure, match="overlap"):
        module.validate_histogram(duplicated)


def test_histogram_validation_rejects_wrong_occurrence_and_polarity() -> None:
    module = load_generator()
    wrong_occurrence = literal_complete_histogram()
    wrong_occurrence["old_occurrence"] = 2
    with pytest.raises(module.CertificateFailure, match="old occurrence"):
        module.validate_histogram(wrong_occurrence)

    wrong_polarity = literal_complete_histogram()
    wrong_polarity["old_polarity"] = -1
    with pytest.raises(module.CertificateFailure, match="old polarity"):
        module.validate_histogram(wrong_polarity)


def test_manifest_rejects_wrong_catalog_footprint_and_polarity_binding() -> None:
    module = load_generator()
    catalog = module.build_task4_schema_catalog(module.load_source_context())
    singleton = catalog.families["singleton"]
    token = singleton.old_tokens[0]
    reference = singleton.old_schema_refs[token.token_id]
    short_reference = replace(
        reference, label_schemas=reference.label_schemas[:-1]
    )
    wrong_references = dict(singleton.old_schema_refs)
    wrong_references[token.token_id] = short_reference
    wrong_singleton = replace(
        singleton, old_schema_refs=wrong_references
    )
    wrong_families = dict(catalog.families)
    wrong_families["singleton"] = wrong_singleton
    with pytest.raises(module.CertificateFailure, match="occurrence footprint"):
        module.build_manifest(catalog=replace(catalog, families=wrong_families))

    wrong_polarities = dict(catalog.occurrence_polarities)
    wrong_polarities[4] = 1
    with pytest.raises(
        module.CertificateFailure, match="chronology metadata digest"
    ):
        module.build_manifest(
            catalog=replace(catalog, occurrence_polarities=wrong_polarities)
        )


def test_old_footprint_rejects_same_length_wrong_slot_occurrence() -> None:
    module = load_generator()
    catalog = module.build_task4_schema_catalog(module.load_source_context())
    singleton = catalog.families["singleton"]
    token = singleton.old_tokens[0]
    reference = singleton.old_schema_refs[token.token_id]
    p_family = catalog.families["P"]
    wrong_occurrence, wrong_label = next(
        label
        for p_reference in p_family.old_schema_refs.values()
        for label in p_reference.label_schemas
        if label[0] not in {item[0] for item in reference.label_schemas}
    )
    mutated = replace(
        reference,
        label_schemas=(
            (wrong_occurrence, wrong_label),
            *reference.label_schemas[1:],
        ),
    )

    with pytest.raises(
        module.CertificateFailure, match="old footprint binding mismatch"
    ):
        module._old_occurrence_records(token, mutated, catalog)


def test_b_identity_table_rejects_duplicate_token_with_fresh_index() -> None:
    module = load_generator()
    catalog = module.build_task4_schema_catalog(module.load_source_context())
    fixed = catalog.families["fixed"]
    tokens = list(fixed.b_tokens)
    tokens[1] = replace(tokens[0], token_index=1)
    mutated = replace(fixed, b_tokens=tuple(tokens))

    with pytest.raises(
        module.CertificateFailure, match="duplicate B token ID"
    ):
        module._b_occurrence_records(mutated, catalog)


def test_family_ledger_rejects_duplicate_old_and_grouped_load_ids() -> None:
    module = load_generator()
    catalog = module.build_task4_schema_catalog(module.load_source_context())
    fixed = catalog.families["fixed"]
    old_tokens = list(fixed.old_tokens)
    old_tokens[1] = old_tokens[0]
    with pytest.raises(
        module.CertificateFailure, match="duplicate old token ID"
    ):
        module.family_ledger(
            replace(fixed, old_tokens=tuple(old_tokens)), catalog
        )

    cells = list(fixed.cells)
    cells[1] = cells[0]
    with pytest.raises(
        module.CertificateFailure, match="duplicate grouped load ID"
    ):
        module.family_ledger(replace(fixed, cells=tuple(cells)), catalog)


def test_family_ledger_serializes_each_approved_footprint_binding() -> None:
    module = load_generator()
    catalog = module.build_task4_schema_catalog(module.load_source_context())
    singleton = catalog.families["singleton"]

    ledger = module.family_ledger(singleton, catalog)

    first_load = ledger["cells"][0]["loads"][0]
    token_id = singleton.old_tokens[0].token_id
    assert first_load["footprint_bindings"] == [
        dict(binding)
        for binding in singleton.old_footprint_bindings[token_id]
    ]
    assert len(first_load["footprint_bindings"]) == 6
    assert all(
        set(binding)
        == {
            "token_id",
            "source_slot",
            "source_members",
            "module_schema",
            "occurrence",
            "occurrence_slot",
            "polarity",
            "leaf",
            "label_schema",
        }
        for binding in first_load["footprint_bindings"]
    )


def test_family_ledger_rejects_one_flipped_derived_bit(monkeypatch) -> None:
    module = load_generator()
    catalog = module.build_task4_schema_catalog(module.load_source_context())
    original = module.histogram_for_load
    flipped = False

    def flip_first_histogram(*args, **kwargs):
        nonlocal flipped
        histogram = original(*args, **kwargs)
        if not flipped:
            flipped = True
            histogram = dict(histogram)
            histogram["value"] ^= 1
        return histogram

    monkeypatch.setattr(module, "histogram_for_load", flip_first_histogram)
    with pytest.raises(
        module.CertificateFailure,
        match=r"family=fixed, cell=age0_n0.*first_odd_load_ids",
    ):
        module.family_ledger(catalog.families["fixed"], catalog)


def test_canonical_generator_writes_end_to_end_manifest() -> None:
    module = load_generator()
    target = ARTIFACT_DIR / "manifest.json"
    target.parent.mkdir(parents=True, exist_ok=True)

    assert module.main(["--write", str(target)]) == 0

    manifest = json.loads(target.read_text(encoding="ascii"))
    assert target.read_bytes() == (
        module.canonical_json(manifest) + "\n"
    ).encode("ascii")
    assert manifest["summary"]["total_load_rows"] == 9408
    assert manifest["summary"]["total_occurrence_loads"] == 17760
    assert manifest["summary"]["active_comparisons"] == 1491840
    assert not tuple(target.parent.glob(f".{target.name}.*.tmp"))


def test_canonical_generator_checks_manifest_byte_for_byte() -> None:
    target = ARTIFACT_DIR / "manifest.json"
    assert target.is_file(), "run the generator write gate first"

    assert load_generator().main(["--check", str(target)]) == 0


def test_independent_verifier_replays_and_rejects_semantic_mutations() -> None:
    target = ARTIFACT_DIR / "manifest.json"
    assert target.is_file(), "run the generator write gate first"
    verifier = load_module("old_new_load_independent_verifier", VERIFIER)
    manifest = json.loads(target.read_text(encoding="ascii"))

    try:
        result = verifier.verify_manifest(target)
        assert result["status"] == "independently-verified"
        assert result["summary"]["total_load_rows"] == 9408
        assert result["summary"]["total_occurrence_loads"] == 17760
        assert result["summary"]["active_comparisons"] == 1491840
        assert result["family_values"] == {
            "fixed": [0],
            "base": [0],
            "singleton": [1],
            "P": [0],
            "C": [0, 1],
            "Q": [0],
        }

        mutations = []

        wrong_mask = copy.deepcopy(manifest)
        bucket = wrong_mask["family_ledgers"]["fixed"]["cells"][0]["loads"][0][
            "histograms"
        ][0]["buckets"][0]
        bucket["mask"] = f"{int(bucket['mask'], 16) ^ 1:021x}"
        mutations.append(("mask", wrong_mask, verifier.MaskVerificationError))

        wrong_coefficient = copy.deepcopy(manifest)
        wrong_coefficient["family_ledgers"]["fixed"]["cells"][0]["loads"][0][
            "coefficient"
        ] += 2
        mutations.append(
            (
                "coefficient",
                wrong_coefficient,
                verifier.RawCoefficientVerificationError,
            )
        )

        pumping_family = next(
            family
            for family, ledger in manifest["family_ledgers"].items()
            if any(
                record[2]
                for record in ledger["template_catalog"]["witness_table"]
            )
        )
        pumping_witness_id = next(
            witness_id
            for witness_id, record in enumerate(
                manifest["family_ledgers"][pumping_family]["template_catalog"]
                ["witness_table"]
            )
            if record[2]
        )
        wrong_boundary = copy.deepcopy(manifest)
        boundary_catalog = wrong_boundary["family_ledgers"][pumping_family][
            "template_catalog"
        ]
        boundary_catalog["witness_table"][pumping_witness_id][2][0][4] += 1
        recompute_template_catalog_digests(boundary_catalog)
        mutations.append(
            ("boundary", wrong_boundary, verifier.PumpingVerificationError)
        )

        wrong_terminal = copy.deepcopy(manifest)
        terminal_catalog = wrong_terminal["family_ledgers"][pumping_family][
            "template_catalog"
        ]
        terminal_record = terminal_catalog["witness_table"][pumping_witness_id]
        terminal_record[1] = not terminal_record[1]
        recompute_template_catalog_digests(terminal_catalog)
        mutations.append(
            ("terminal", wrong_terminal, verifier.PumpingVerificationError)
        )

        wrong_mapping = copy.deepcopy(manifest)
        mapping_catalog = wrong_mapping["family_ledgers"][pumping_family][
            "template_catalog"
        ]
        mapping_catalog["identity_witness_ids"].pop()
        mapping_catalog["template_count"] -= 1
        recompute_template_catalog_digests(mapping_catalog)
        mutations.append(
            ("mapping", wrong_mapping, verifier.PumpingVerificationError)
        )

        wrong_redirect = copy.deepcopy(manifest)
        redirect_catalog = wrong_redirect["family_ledgers"][pumping_family][
            "template_catalog"
        ]
        original_id = redirect_catalog["identity_witness_ids"][0]
        redirect_catalog["identity_witness_ids"][0] = next(
            witness_id
            for witness_id in range(redirect_catalog["witness_count"])
            if witness_id != original_id
        )
        recompute_template_catalog_digests(redirect_catalog)
        mutations.append(
            ("redirect", wrong_redirect, verifier.PumpingVerificationError)
        )

        wrong_schema = copy.deepcopy(manifest)
        schema_catalog = wrong_schema["family_ledgers"][pumping_family][
            "template_catalog"
        ]
        schema_catalog["schema_table"][0][2][0][1][0] *= -1
        recompute_template_catalog_digests(schema_catalog)
        mutations.append(
            ("schema", wrong_schema, verifier.PumpingVerificationError)
        )

        wrong_cell = copy.deepcopy(manifest)
        cell_catalog = wrong_cell["family_ledgers"][pumping_family][
            "template_catalog"
        ]
        cell_catalog["cell_table"][0][3][0] += 1
        recompute_template_catalog_digests(cell_catalog)
        mutations.append(
            ("cell", wrong_cell, verifier.PumpingVerificationError)
        )

        wrong_family = copy.deepcopy(manifest)
        wrong_family["family_ledgers"]["fixed"]["cells"][0]["value"] ^= 1
        mutations.append(
            ("family", wrong_family, verifier.FamilyVerificationError)
        )

        wrong_status = copy.deepcopy(manifest)
        wrong_status["status"] = "proved-by-generator"
        mutations.append(
            ("status", wrong_status, verifier.StatusVerificationError)
        )

        wrong_identity = copy.deepcopy(manifest)
        wrong_identity["b_identity_table"][0]["coefficient"] += 2
        wrong_identity["b_identity_digest"] = hashlib.sha256(
            json.dumps(
                wrong_identity["b_identity_table"],
                ensure_ascii=True,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("ascii")
        ).hexdigest()
        mutations.append(
            ("identity", wrong_identity, verifier.BIdentityVerificationError)
        )

        wrong_dependency = copy.deepcopy(manifest)
        dependency = next(iter(wrong_dependency["dependency_digests"]))
        digest = wrong_dependency["dependency_digests"][dependency]
        wrong_dependency["dependency_digests"][dependency] = (
            ("0" if digest[0] != "0" else "1") + digest[1:]
        )
        mutations.append(
            (
                "dependency",
                wrong_dependency,
                verifier.DependencyVerificationError,
            )
        )

        for name, mutated, error_type in mutations:
            mutation_path = ARTIFACT_DIR / f"mutation-{name}.json"
            mutation_path.write_text(
                json.dumps(
                    mutated,
                    ensure_ascii=True,
                    separators=(",", ":"),
                    sort_keys=True,
                )
                + "\n",
                encoding="ascii",
            )
            with pytest.raises(error_type):
                verifier.verify_manifest(mutation_path)
    finally:
        for artifact in ARTIFACT_DIR.glob("*.json"):
            artifact.unlink()
        if ARTIFACT_DIR.is_dir() and not tuple(ARTIFACT_DIR.iterdir()):
            ARTIFACT_DIR.rmdir()


PACKAGE_V2_ROOT_FIELDS = (
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
PACKAGE_V2_DESCRIPTOR_FIELDS = (
    "role",
    "family",
    "path",
    "sha256",
    "total_bytes",
    "record_count",
    "record_counts",
)
PACKAGE_V2_SHARED_FIELDS = {
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
    "b_coordinate": ("tag", "token_index", "source_class", "coordinate"),
    "shared_footer": (
        "tag",
        "coordinate_count",
        "records_before_footer",
        "bytes_before_footer",
    ),
}
PACKAGE_V2_FAMILY_FIELDS = {
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


def load_package_v2_verifier():
    return load_module("old_new_load_package_v2_verifier", VERIFIER)


def literal_package_v2_template_catalog(family, cell_ids):
    if family == "fixed":
        catalog = {
            "format": "task4-template-catalog-v2",
            "typed_encoding": TYPED_ENCODING,
            "family": family,
            "field_orders": copy.deepcopy(TEMPLATE_FIELD_ORDERS),
            "identity_order": "schema-major-cell-minor",
            "schema_count": 1,
            "cell_count": len(cell_ids),
            "template_count": len(cell_ids),
            "witness_count": 1,
            "schema_table": [
                ["fixture-schema", ["a"], [["fixed", [2], None]]]
            ],
            "cell_table": [
                [cell_id, ["a"], [index], [index]]
                for index, cell_id in enumerate(sorted(cell_ids))
            ],
            "witness_table": [[2, False, []]],
            "identity_witness_ids": [0] * len(cell_ids),
        }
    else:
        catalog = {
            "format": "task4-template-catalog-v2",
            "typed_encoding": TYPED_ENCODING,
            "family": family,
            "field_orders": copy.deepcopy(TEMPLATE_FIELD_ORDERS),
            "identity_order": "schema-major-cell-minor",
            "schema_count": 0,
            "cell_count": 0,
            "template_count": 0,
            "witness_count": 0,
            "schema_table": [],
            "cell_table": [],
            "witness_table": [],
            "identity_witness_ids": [],
        }
    recompute_template_catalog_digests(catalog)
    return catalog


def literal_package_v2_histogram():
    return {
        "old_occurrence": None,
        "old_leaf": 1,
        "old_polarity": None,
        "comparison_count": 84,
        "one_count": 0,
        "value": 0,
        "buckets": [
            {
                "key": {
                    "old_occurrence": None,
                    "old_leaf": 1,
                    "b_source_class": "fixture-b",
                    "b_coordinate": ["fixture", 0],
                    "equality_exclusion": False,
                    "old_polarity": None,
                    "module_method": None,
                    "module_order": None,
                    "chronology": "fixed_vs_correction_literal_leaf_order",
                    "chronology_order": -1,
                    "label_method": "identical_pumped_blocks",
                    "label_order": 0,
                    "contribution_bit": 0,
                },
                "count": 84,
                "mask": "fffffffffffffffffffff",
            }
        ],
    }


def literal_package_v2_logical_fixture(*, two_cells=False, production=False):
    families = ("fixed", "base", "singleton", "P", "C", "Q")
    cell_ids = ("z-cell", "a-cell") if two_cells else ("fixture-cell",)
    fixed_catalog = literal_package_v2_template_catalog("fixed", cell_ids)
    template_catalogs = {
        family: (
            fixed_catalog
            if family == "fixed"
            else literal_package_v2_template_catalog(family, ())
        )
        for family in families
    }
    footprint_binding = {
        "token_id": "old:fixed:0",
        "source_slot": None,
        "source_members": ["fixture-source"],
        "module_schema": None,
        "occurrence": None,
        "occurrence_slot": None,
        "polarity": None,
        "leaf": 1,
        "label_schema": "fixture-label",
    }
    fixed_cells = []
    for cell_id in cell_ids:
        load_id = f"fixed|{cell_id}|old:fixed:0"
        fixed_cells.append(
            {
                "cell_id": cell_id,
                "load_count": 1,
                "occurrence_load_count": 1,
                "comparison_count": 84,
                "odd_load_ids": [],
                "value": 0,
                "loads": [
                    {
                        "load_id": load_id,
                        "old_token_id": "old:fixed:0",
                        "coefficient": 1,
                        "source_members": ["fixture-source"],
                        "occurrence_footprint": 1,
                        "footprint_bindings": [
                            copy.deepcopy(footprint_binding)
                        ],
                        "histograms": [literal_package_v2_histogram()],
                        "value": 0,
                    }
                ],
            }
        )
    family_ledgers = {
        family: {
            "family": family,
            "cells": fixed_cells if family == "fixed" else [],
            "template_catalog": copy.deepcopy(template_catalogs[family]),
            "summary": {
                "load_rows": len(cell_ids) if family == "fixed" else 0,
                "occurrence_loads": (
                    len(cell_ids) if family == "fixed" else 0
                ),
                "comparisons": 84 * len(cell_ids) if family == "fixed" else 0,
            },
        }
        for family in families
    }
    source_bindings = {
        "format": "task4-source-bindings-v1",
        "old": {"fixture": "old"},
        "b": {"fixture": "b"},
    }
    reseal_source_bindings(source_bindings)
    b_identity_table = [
        {
            "token_index": token_index,
            "token_id": f"b:{token_index:02d}",
            "source_class": "fixture-b",
            "coefficient": 1,
            "slot": 0,
            "occurrence": 1,
            "polarity": 1,
            "module_schema": "fixture-module",
            "label_schema": "fixture-label",
            "source_members": [],
        }
        for token_index in range(84)
    ]
    b_identity_digest = hashlib.sha256(
        json.dumps(
            b_identity_table,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
    ).hexdigest()
    load_rows = {
        family: len(cell_ids) if family == "fixed" else 0
        for family in families
    }
    occurrence_loads = dict(load_rows)
    template_counts = dict(load_rows)
    summary = {
        "load_rows": load_rows,
        "total_load_rows": len(cell_ids),
        "footprint_sizes": {
            family: {"1": 1} if family == "fixed" else {}
            for family in families
        },
        "occurrence_loads": occurrence_loads,
        "total_occurrence_loads": len(cell_ids),
        "b_tokens_per_occurrence": 84,
        "active_comparisons": 84 * len(cell_ids),
        "template_counts": template_counts,
        "total_templates": len(cell_ids),
    }
    return {
        "format": "period-two-old-new-cut-load-v1",
        "domain": "fixture a>=0",
        "status": (
            "generated-awaiting-independent-replay"
            if production
            else "preflight-sample-not-a-certificate"
        ),
        "summary": summary,
        "dependency_digests": {"fixture/source.json": "0" * 64},
        "source_bindings": source_bindings,
        "b_identity_table": b_identity_table,
        "b_identity_digest": b_identity_digest,
        "family_ledgers": family_ledgers,
    }


def encoded_package_v2_with_two_fixed_buckets():
    generator = load_generator()
    logical = literal_package_v2_logical_fixture()
    histogram = logical["family_ledgers"]["fixed"]["cells"][0]["loads"][0][
        "histograms"
    ][0]
    first = copy.deepcopy(histogram["buckets"][0])
    first["count"] = 1
    first["mask"] = f"{1:021x}"
    second = copy.deepcopy(histogram["buckets"][0])
    second["key"]["b_coordinate"] = ["fixture", 1]
    second["count"] = 83
    second["mask"] = f"{((1 << 84) - 2):021x}"
    histogram["buckets"] = [first, second]
    return generator, generator.encode_tiny_v2_package(logical)


def reseal_package_v2_object(generator, encoded, descriptor_index, payload):
    root = copy.deepcopy(encoded.index)
    descriptor = root["shards"][descriptor_index]
    old_path = descriptor["path"]
    digest = hashlib.sha256(payload).hexdigest()
    new_path = f"objects/{digest}.jsonl"
    descriptor["path"] = new_path
    descriptor["sha256"] = digest
    descriptor["total_bytes"] = len(payload)
    root["shard_bytes_total"] = sum(
        item["total_bytes"] for item in root["shards"]
    )
    root_without_hash = {
        key: value for key, value in root.items() if key != "root_sha256"
    }
    root["root_sha256"] = hashlib.sha256(
        generator.canonical_json_line(root_without_hash)
    ).hexdigest()
    objects = dict(encoded.objects)
    objects.pop(old_path)
    objects[new_path] = payload
    return replace(
        encoded,
        index=root,
        index_bytes=generator.canonical_json_line(root),
        objects=objects,
    )


def test_package_v2_constants_and_tag_grammars_are_exact() -> None:
    module = load_generator()

    assert module.PACKAGE_V2_FORMAT == "period-two-old-new-cut-package-v2"
    assert module.LOGICAL_V1_FORMAT == "period-two-old-new-cut-load-v1"
    assert module.CANONICAL_LINE_ENCODING == "canonical-json-ascii-lines-v1"
    assert module.MASK_ENCODING == "uint84-be11-base64url-nopad-v1"
    assert module.FAMILY_ORDER == ("fixed", "base", "singleton", "P", "C", "Q")
    assert module.SHARD_ORDER == (
        "shared",
        "fixed",
        "base",
        "singleton",
        "P",
        "C",
        "Q",
    )
    assert module.ROOT_INDEX_FIELDS == PACKAGE_V2_ROOT_FIELDS
    assert module.SHARD_DESCRIPTOR_FIELDS == PACKAGE_V2_DESCRIPTOR_FIELDS
    assert module.SHARED_RECORD_FIELDS == PACKAGE_V2_SHARED_FIELDS
    assert module.FAMILY_RECORD_FIELDS == PACKAGE_V2_FAMILY_FIELDS
    assert {tag: len(fields) for tag, fields in module.SHARED_RECORD_FIELDS.items()} == {
        "shared_header": 9,
        "dependency": 3,
        "source_bindings": 2,
        "b_identity": 11,
        "b_coordinate": 4,
        "shared_footer": 4,
    }
    assert {tag: len(fields) for tag, fields in module.FAMILY_RECORD_FIELDS.items()} == {
        "family_header": 14,
        "old_load": 8,
        "footprint": 9,
        "bucket_class": 11,
        "load": 5,
        "cell_footer": 7,
        "template_header": 10,
        "template_schema": 5,
        "template_cell": 6,
        "template_witness": 5,
        "template_identity_chunk": 3,
        "template_footer": 4,
        "family_footer": 8,
    }
    assert module.COMPARISON_METHODS == (
        None,
        "strict_affine_length",
        "identical_pumped_blocks",
        "fixed_mismatch_after_pumped_prefix",
    )
    assert module.CHRONOLOGIES == (
        "fixed_vs_correction_literal_leaf_order",
        "distinct_occurrences_literal_AST_order",
        "equal_coordinate_excluded",
        "same_occurrence_increasing",
        "same_occurrence_decreasing",
    )
    assert module.TEMPLATE_FIELD_ORDERS == TEMPLATE_FIELD_ORDERS
    assert module.PACKAGE_BYTE_CAP == 100_000_000
    assert module.MAX_CANONICAL_LINE_BYTES == 16_777_216


def test_package_v2_foundation_preserves_logical_v1_catalog_summary() -> None:
    module = load_generator()
    empty_catalog = module.Task4SchemaCatalog(
        families={},
        dependency_digests={},
        old_source_proof={},
        b_source_proof={},
        occurrence_leafs={},
        occurrence_polarities={},
        occurrence_slots={},
        fixed_metadata={},
        chronology_digest="",
        b_identity_table=(),
        b_identity_digest="",
    )

    assert module._catalog_summary(empty_catalog) == {
        "load_rows": {},
        "total_load_rows": 0,
        "footprint_sizes": {},
        "occurrence_loads": {},
        "total_occurrence_loads": 0,
        "b_tokens_per_occurrence": 84,
        "active_comparisons": 0,
        "template_counts": {},
        "total_templates": 0,
    }


def test_package_v2_generator_and_verifier_literals_agree() -> None:
    generator = load_generator()
    verifier = load_package_v2_verifier()

    for name, expected in {
        "PACKAGE_V2_FORMAT": "period-two-old-new-cut-package-v2",
        "LOGICAL_V1_FORMAT": "period-two-old-new-cut-load-v1",
        "CANONICAL_LINE_ENCODING": "canonical-json-ascii-lines-v1",
        "MASK_ENCODING": "uint84-be11-base64url-nopad-v1",
        "FAMILY_ORDER": ("fixed", "base", "singleton", "P", "C", "Q"),
        "SHARD_ORDER": (
            "shared",
            "fixed",
            "base",
            "singleton",
            "P",
            "C",
            "Q",
        ),
        "ROOT_INDEX_FIELDS": PACKAGE_V2_ROOT_FIELDS,
        "SHARD_DESCRIPTOR_FIELDS": PACKAGE_V2_DESCRIPTOR_FIELDS,
        "SHARED_RECORD_FIELDS": PACKAGE_V2_SHARED_FIELDS,
        "FAMILY_RECORD_FIELDS": PACKAGE_V2_FAMILY_FIELDS,
    }.items():
        assert getattr(generator, name) == expected
        assert getattr(verifier, name) == expected
    assert generator.pack_mask is not verifier.pack_mask
    assert generator.iter_canonical_json_lines is not verifier.iter_canonical_json_lines
    assert "period_two_old_new_cut_load_certificate" not in verifier.__dict__


@pytest.mark.parametrize("module_loader", (load_generator, load_package_v2_verifier))
def test_package_v2_masks_round_trip_and_reject_malformed_tokens(
    module_loader,
) -> None:
    module = module_loader()
    assert module.pack_mask(0) == "AAAAAAAAAAAAAAA"
    assert module.pack_mask(1) == "AAAAAAAAAAAAAAE"
    assert module.pack_mask(1 << 83) == "CAAAAAAAAAAAAAA"
    assert module.pack_mask((1 << 84) - 1) == "D_____________8"
    for mask in (0, 1, 2, 1 << 83, (1 << 84) - 1):
        assert module.unpack_mask(module.pack_mask(mask)) == mask
    for invalid in (
        "AAAAAAAAAAAAAA",
        "AAAAAAAAAAAAAA=",
        "AAAAAAAAAAAAAA!",
        "EAAAAAAAAAAAAAA",
        "AAAAAAAAAAAAAAB",
    ):
        with pytest.raises(module.WireFormatError):
            module.unpack_mask(invalid)


@pytest.mark.parametrize("module_loader", (load_generator, load_package_v2_verifier))
def test_package_v2_histogram_masks_cover_token_bits_without_reversal(
    module_loader,
) -> None:
    module = module_loader()
    low = module.pack_mask(1)
    rest = module.pack_mask(((1 << 84) - 1) ^ 1)
    assert module.validate_mask_partition((low, rest)) == (1 << 84) - 1
    assert module.unpack_mask(low) == 1
    assert module.unpack_mask(module.pack_mask(1 << 83)) == 1 << 83
    with pytest.raises(module.WireFormatError):
        module.validate_mask_partition((low, low, rest))
    with pytest.raises(module.WireFormatError):
        module.validate_mask_partition((rest,))
    with pytest.raises(module.WireFormatError):
        module.validate_mask_partition((module.pack_mask(0), module.pack_mask((1 << 84) - 1)))


@pytest.mark.parametrize("module_loader", (load_generator, load_package_v2_verifier))
def test_package_v2_canonical_decoder_rejects_noncanonical_lines(
    module_loader,
) -> None:
    module = module_loader()
    record = ["dependency", "fixture/source.json", "0" * 64]
    encoded = module.canonical_json_line(record)
    assert list(module.iter_canonical_json_lines(io.BytesIO(encoded))) == [record]
    invalid_lines = (
        b'["source_bindings",{"a":1,"a":2}]\n',
        b"[1.0]\n",
        b"[NaN]\n",
        b"[Infinity]\n",
        b"[-0]\n",
        b"[1, 2]\n",
        b"[1]\r\n",
        b"\n",
        b"[1]",
        b"\xff\n",
    )
    for payload in invalid_lines:
        with pytest.raises(module.WireFormatError):
            tuple(module.iter_canonical_json_lines(io.BytesIO(payload)))
    with pytest.raises(module.WireFormatError):
        tuple(
            module.iter_canonical_json_lines(
                io.BytesIO(b'["123456789"]\n'), max_line_bytes=8
            )
        )


@pytest.mark.parametrize("module_loader", (load_generator, load_package_v2_verifier))
@pytest.mark.parametrize(
    "value",
    (
        {"x": 1.5},
        {"x": float("nan")},
        {1: "coerced-key"},
        {"x": object()},
    ),
)
def test_package_v2_canonical_encoder_rejects_values_outside_wire_domain(
    module_loader,
    value,
) -> None:
    module = module_loader()
    with pytest.raises(module.WireFormatError):
        module.canonical_json_line(value)


@pytest.mark.parametrize("module_loader", (load_generator, load_package_v2_verifier))
def test_package_v2_canonical_encoder_rejects_oversized_lines(
    module_loader,
    monkeypatch,
) -> None:
    module = module_loader()
    monkeypatch.setattr(module, "MAX_CANONICAL_LINE_BYTES", 32)

    with pytest.raises(module.WireFormatError, match="line"):
        module.canonical_json_line({"value": "x" * 32})


@pytest.mark.parametrize("module_loader", (load_generator, load_package_v2_verifier))
def test_package_v2_tag_decoders_reject_width_field_and_order_mutations(
    module_loader,
) -> None:
    module = module_loader()
    logical = literal_package_v2_logical_fixture()
    encoded = load_generator().encode_tiny_v2_package(logical)
    shared = [list(record) for record in encoded.shard_records["shared"]]
    assert module.decode_shared_records(
        io.BytesIO(b"".join(module.canonical_json_line(row) for row in shared))
    )["records"] == tuple(tuple(row) for row in shared)

    mutations = []
    unknown = copy.deepcopy(shared)
    unknown[1][0] = "unknown"
    mutations.append(unknown)
    wrong_width = copy.deepcopy(shared)
    wrong_width[0].pop()
    mutations.append(wrong_width)
    wrong_order = copy.deepcopy(shared)
    wrong_order[0], wrong_order[1] = wrong_order[1], wrong_order[0]
    mutations.append(wrong_order)
    trailing = copy.deepcopy(shared)
    trailing.append(["dependency", "later", "0" * 64])
    mutations.append(trailing)
    for rows in mutations:
        with pytest.raises(module.WireFormatError):
            module.decode_shared_records(
                io.BytesIO(
                    b"".join(module.canonical_json_line(row) for row in rows)
                )
            )


@pytest.mark.parametrize("module_loader", (load_generator, load_package_v2_verifier))
def test_package_v2_shared_rejects_resealed_source_binding_format(
    module_loader,
) -> None:
    module = module_loader()
    encoded = load_generator().encode_tiny_v2_package(
        literal_package_v2_logical_fixture()
    )
    records = [list(row) for row in copy.deepcopy(encoded.shard_records["shared"])]
    source_row = next(row for row in records if row[0] == "source_bindings")
    source_row[1]["format"] = "wrong-source-bindings-format"
    reseal_source_bindings(source_row[1])
    records[-1][3] = sum(
        len(module.canonical_json_line(row)) for row in records[:-1]
    )
    payload = b"".join(module.canonical_json_line(row) for row in records)
    with pytest.raises(module.WireFormatError, match="source-binding format"):
        module.decode_shared_records(io.BytesIO(payload))


@pytest.mark.parametrize("module_loader", (load_generator, load_package_v2_verifier))
def test_package_v2_source_and_compact_cell_indices_are_distinct_strict_ints(
    module_loader,
) -> None:
    module = module_loader()
    logical = literal_package_v2_logical_fixture(two_cells=True)
    encoded = load_generator().encode_tiny_v2_package(logical)
    fixed = [list(record) for record in encoded.shard_records["fixed"]]
    footers = [record for record in fixed if record[0] == "cell_footer"]
    assert [(row[1], row[2], row[3]) for row in footers] == [
        (0, 1, "z-cell"),
        (1, 0, "a-cell"),
    ]
    mutated = copy.deepcopy(fixed)
    next(row for row in mutated if row[0] == "cell_footer")[1] = True
    with pytest.raises(module.WireFormatError):
        module.decode_family_records(
            io.BytesIO(
                b"".join(module.canonical_json_line(row) for row in mutated)
            ),
            expected_family="fixed",
            scope="preflight-sample",
        )


@pytest.mark.parametrize("module_loader", (load_generator, load_package_v2_verifier))
def test_package_v2_preflight_selected_old_subset_is_a_distinct_domain(
    module_loader,
) -> None:
    module = module_loader()
    encoded = load_generator().encode_tiny_v2_package(
        literal_package_v2_logical_fixture()
    )
    records = [
        list(record)
        for record in encoded.shard_records["fixed"]
        if record[0] != "load"
    ]
    records[0][4] = []
    cell_footer = next(row for row in records if row[0] == "cell_footer")
    cell_footer[4:] = [[], 0, 0]
    family_footer = records[-1]
    family_footer[3:6] = [0, 0, 0]
    family_footer[6] = len(records) - 1
    family_footer[7] = sum(
        len(module.canonical_json_line(row)) for row in records[:-1]
    )
    payload = b"".join(module.canonical_json_line(row) for row in records)

    decoded = module.decode_family_records(
        io.BytesIO(payload),
        expected_family="fixed",
        scope="preflight-sample",
    )
    assert decoded["ledger"]["cells"][0]["loads"] == []
    assert decoded["ledger"]["cells"][0]["load_count"] == 0
    assert decoded["ledger"]["summary"] == {
        "load_rows": 0,
        "occurrence_loads": 0,
        "comparisons": 0,
    }
    with pytest.raises(
        module.WireFormatError, match="production old indices"
    ):
        module.decode_family_records(
            io.BytesIO(payload),
            expected_family="fixed",
            scope="production-full",
        )


@pytest.mark.parametrize("module_loader", (load_generator, load_package_v2_verifier))
def test_package_v2_foundation_never_materializes_production_shards(
    module_loader,
) -> None:
    module = module_loader()

    class HeaderOnlyStream:
        def __init__(self, header):
            self.header = header
            self.calls = 0

        def readline(self, _limit):
            self.calls += 1
            if self.calls == 1:
                return module.canonical_json_line(self.header)
            raise AssertionError("foundation attempted to materialize production")

    shared = HeaderOnlyStream(
        [
            "shared_header",
            "period-two-old-new-cut-package-v2",
            "production-full",
            "period-two-old-new-cut-load-v1",
            "canonical-json-ascii-lines-v1",
            "uint84-be11-base64url-nopad-v1",
            "fixture a>=0",
            "generated-awaiting-independent-replay",
            ["shared", "fixed", "base", "singleton", "P", "C", "Q"],
        ]
    )
    with pytest.raises(module.WireFormatError, match="production"):
        module.decode_shared_records(shared)
    assert shared.calls == 1

    family = HeaderOnlyStream(
        [
            "family_header",
            "fixed",
            ["a"],
            1,
            [0],
            1,
            1,
            1,
            84,
            [
                None,
                "strict_affine_length",
                "identical_pumped_blocks",
                "fixed_mismatch_after_pumped_prefix",
            ],
            [
                "fixed_vs_correction_literal_leaf_order",
                "distinct_occurrences_literal_AST_order",
                "equal_coordinate_excluded",
                "same_occurrence_increasing",
                "same_occurrence_decreasing",
            ],
            list(module.HISTOGRAM_KEY_FIELDS),
            copy.deepcopy(module.TEMPLATE_FIELD_ORDERS),
            "product-order-with-P-domain-filter",
        ]
    )
    with pytest.raises(module.WireFormatError, match="production"):
        module.decode_family_records(
            family,
            expected_family="fixed",
            scope="production-full",
        )
    assert family.calls == 1


@pytest.mark.parametrize("module_loader", (load_generator, load_package_v2_verifier))
def test_package_v2_family_header_rejects_resealed_b_token_count(
    module_loader,
) -> None:
    module = module_loader()
    encoded = load_generator().encode_tiny_v2_package(
        literal_package_v2_logical_fixture()
    )
    records = [list(record) for record in encoded.shard_records["fixed"]]
    records[0][8] = 83
    records[-1][7] = sum(
        len(module.canonical_json_line(row)) for row in records[:-1]
    )
    payload = b"".join(module.canonical_json_line(row) for row in records)
    with pytest.raises(module.WireFormatError, match="B token count"):
        module.decode_family_records(
            io.BytesIO(payload),
            expected_family="fixed",
            scope="preflight-sample",
        )


@pytest.mark.parametrize("module_loader", (load_generator, load_package_v2_verifier))
def test_package_v2_family_header_variables_bind_catalog_domain(
    module_loader,
) -> None:
    module = module_loader()
    encoded = load_generator().encode_tiny_v2_package(
        literal_package_v2_logical_fixture()
    )
    records = [list(row) for row in copy.deepcopy(encoded.shard_records["fixed"])]
    records[0][2] = ["wrong"]
    records[-1][7] = sum(
        len(module.canonical_json_line(row)) for row in records[:-1]
    )
    payload = b"".join(module.canonical_json_line(row) for row in records)
    with pytest.raises(module.WireFormatError, match="variables"):
        module.decode_family_records(
            io.BytesIO(payload),
            expected_family="fixed",
            scope="preflight-sample",
        )


def test_package_v2_generator_rejects_out_of_order_load_rows() -> None:
    generator, encoded = encoded_package_v2_with_two_fixed_buckets()
    records = [list(row) for row in copy.deepcopy(encoded.shard_records["fixed"])]
    load_positions = [
        index for index, row in enumerate(records) if row[0] == "load"
    ]
    assert len(load_positions) == 2
    first, second = load_positions
    records[first], records[second] = records[second], records[first]
    records[-1][7] = sum(
        len(generator.canonical_json_line(row)) for row in records[:-1]
    )

    with pytest.raises(generator.WireFormatError, match="ordered"):
        generator.decode_family_records(
            io.BytesIO(
                b"".join(generator.canonical_json_line(row) for row in records)
            ),
            expected_family="fixed",
            scope="preflight-sample",
        )


def test_package_v2_generator_rejects_duplicate_bucket_per_footprint() -> None:
    generator, encoded = encoded_package_v2_with_two_fixed_buckets()
    records = [list(row) for row in copy.deepcopy(encoded.shard_records["fixed"])]
    loads = [row for row in records if row[0] == "load"]
    assert len(loads) == 2
    loads[1][3] = loads[0][3]
    records[-1][7] = sum(
        len(generator.canonical_json_line(row)) for row in records[:-1]
    )

    with pytest.raises(generator.WireFormatError, match="repeats"):
        generator.decode_family_records(
            io.BytesIO(
                b"".join(generator.canonical_json_line(row) for row in records)
            ),
            expected_family="fixed",
            scope="preflight-sample",
        )


@pytest.mark.parametrize("module_loader", (load_generator, load_package_v2_verifier))
def test_package_v2_empty_family_header_variables_are_frozen(
    module_loader,
) -> None:
    module = module_loader()
    encoded = load_generator().encode_tiny_v2_package(
        literal_package_v2_logical_fixture()
    )
    records = [list(row) for row in copy.deepcopy(encoded.shard_records["base"])]
    records[0][2] = ["wrong"]
    records[-1][7] = sum(
        len(module.canonical_json_line(row)) for row in records[:-1]
    )
    payload = b"".join(module.canonical_json_line(row) for row in records)

    with pytest.raises(module.WireFormatError, match="variables"):
        module.decode_family_records(
            io.BytesIO(payload),
            expected_family="base",
            scope="preflight-sample",
        )


@pytest.mark.parametrize("module_loader", (load_generator, load_package_v2_verifier))
@pytest.mark.parametrize("summary_field", ("emitted_summary", "full_summary"))
def test_package_v2_root_rejects_rehashed_malformed_summary_schema(
    module_loader,
    summary_field,
) -> None:
    module = module_loader()
    encoded = load_generator().encode_tiny_v2_package(
        literal_package_v2_logical_fixture()
    )
    root = copy.deepcopy(encoded.index)
    root[summary_field] = {"bogus": 1}
    root["root_sha256"] = hashlib.sha256(
        module.canonical_json_line(
            {key: value for key, value in root.items() if key != "root_sha256"}
        )
    ).hexdigest()
    with pytest.raises(module.WireFormatError, match="summary"):
        module.decode_root_index(module.canonical_json_line(root))


@pytest.mark.parametrize("module_loader", (load_generator, load_package_v2_verifier))
def test_package_v2_root_keeps_footprint_and_cell_load_domains_distinct(
    module_loader,
) -> None:
    module = module_loader()
    encoded = load_generator().encode_tiny_v2_package(
        literal_package_v2_logical_fixture(two_cells=True)
    )

    assert module.decode_root_index(encoded.index_bytes) == encoded.index


@pytest.mark.parametrize("module_loader", (load_generator, load_package_v2_verifier))
def test_package_v2_template_validator_rejects_rehashed_pump_dereference(
    module_loader,
) -> None:
    generator = load_generator()
    module = module_loader()
    schema = generator.Schema(
        "fixture:pump",
        ("a",),
        (("r", CORE_R, (1, 0)),),
    )
    cells = generator.make_cells(schema.variables)
    catalog = generator.build_compact_template_catalog(
        "fixed",
        {schema.schema_id: schema},
        cells,
        {
            (schema.schema_id, cell.cell_id): generator.build_template(
                schema, cell
            )
            for cell in cells
        },
    )
    pumping_witness_id = next(
        witness_id
        for witness_id, witness in enumerate(catalog["witness_table"])
        if witness[2]
    )
    mutated = copy.deepcopy(catalog)
    mutated["witness_table"][pumping_witness_id][2][0][0] = 99
    recompute_template_catalog_digests(mutated)

    with pytest.raises(module.WireFormatError, match="catalog"):
        module._validate_v2_template_catalog(mutated)


def test_package_v2_verifier_rejects_rehashed_out_of_domain_cell_state() -> None:
    generator = load_generator()
    verifier = load_package_v2_verifier()
    logical = literal_package_v2_logical_fixture()
    encoded = generator.encode_tiny_v2_package(logical)
    records = [list(row) for row in copy.deepcopy(encoded.shard_records["fixed"])]
    catalog = copy.deepcopy(logical["family_ledgers"]["fixed"]["template_catalog"])
    catalog["cell_table"][0][2] = [7]
    catalog["cell_table"][0][3] = [7]
    recompute_template_catalog_digests(catalog)
    cell_row = next(row for row in records if row[0] == "template_cell")
    cell_row[4] = [7]
    cell_row[5] = [7]
    footer = next(row for row in records if row[0] == "template_footer")
    footer[1:] = [
        catalog["identity_sha256"],
        catalog["replay_sha256"],
        catalog["catalog_sha256"],
    ]
    records[-1][7] = sum(
        len(verifier.canonical_json_line(row)) for row in records[:-1]
    )

    with pytest.raises(verifier.WireFormatError, match="state"):
        verifier.decode_family_records(
            io.BytesIO(
                b"".join(verifier.canonical_json_line(row) for row in records)
            ),
            expected_family="fixed",
            scope="preflight-sample",
        )


@pytest.mark.parametrize("module_loader", (load_generator, load_package_v2_verifier))
def test_package_v2_root_decoder_stops_after_second_line(module_loader) -> None:
    module = module_loader()
    encoded = load_generator().encode_tiny_v2_package(
        literal_package_v2_logical_fixture()
    )

    class TwoLineRootStream:
        def __init__(self):
            self.calls = 0

        def readline(self, _limit):
            self.calls += 1
            if self.calls == 1:
                return encoded.index_bytes
            if self.calls == 2:
                return b"{}\n"
            raise AssertionError("root decoder read beyond the second line")

    stream = TwoLineRootStream()
    with pytest.raises(module.WireFormatError, match="exactly one"):
        module.decode_root_index(stream)
    assert stream.calls == 2


def test_package_v2_tiny_logical_v1_round_trip() -> None:
    generator = load_generator()
    verifier = load_package_v2_verifier()
    logical = literal_package_v2_logical_fixture()

    encoded = generator.encode_tiny_v2_package(logical)
    assert verifier.decode_v2_package(
        encoded.index_bytes, encoded.objects
    ) == logical
    assert len(encoded.index["shards"]) == 7
    assert [descriptor["family"] for descriptor in encoded.index["shards"]] == [
        None,
        "fixed",
        "base",
        "singleton",
        "P",
        "C",
        "Q",
    ]
    for descriptor in encoded.index["shards"]:
        expected_tags = (
            PACKAGE_V2_SHARED_FIELDS
            if descriptor["family"] is None
            else PACKAGE_V2_FAMILY_FIELDS
        )
        assert set(descriptor["record_counts"]) == set(expected_tags)
        assert sum(descriptor["record_counts"].values()) == descriptor["record_count"]


def test_package_v2_content_addresses_and_rejects_reuse_mismatch(
    tmp_path,
) -> None:
    generator = load_generator()
    verifier = load_package_v2_verifier()
    encoded = generator.encode_tiny_v2_package(
        literal_package_v2_logical_fixture()
    )
    index_path = tmp_path / "index.json"
    result = generator.publish_v2_package(encoded, index_path)
    assert result.state == "COMMITTED"
    assert len(result.created_objects) == 7
    assert result.reused_objects == ()
    assert verifier.decode_v2_package_path(index_path) == (
        literal_package_v2_logical_fixture()
    )
    for descriptor in encoded.index["shards"]:
        object_path = tmp_path / descriptor["path"]
        payload = object_path.read_bytes()
        assert len(payload) == descriptor["total_bytes"]
        assert hashlib.sha256(payload).hexdigest() == descriptor["sha256"]
        assert descriptor["path"] == f"objects/{descriptor['sha256']}.jsonl"

    replay = generator.publish_v2_package(encoded, index_path)
    assert replay.created_objects == ()
    assert len(replay.reused_objects) == 7

    mismatch_root = tmp_path / "mismatch"
    mismatch_index = mismatch_root / "index.json"
    descriptor = encoded.index["shards"][0]
    mismatch_object = mismatch_root / descriptor["path"]
    mismatch_object.parent.mkdir(parents=True)
    mismatch_object.write_bytes(b"not-the-content-addressed-object\n")
    with pytest.raises(generator.PublicationFailure) as error:
        generator.publish_v2_package(encoded, mismatch_index)
    assert error.value.state == "PREPARED"
    assert mismatch_object.read_bytes() == b"not-the-content-addressed-object\n"
    assert not mismatch_index.exists()


def test_package_v2_publish_rejects_mutated_new_object_before_replace(
    tmp_path,
) -> None:
    generator = load_generator()
    encoded = generator.encode_tiny_v2_package(
        literal_package_v2_logical_fixture()
    )
    relative_path = encoded.index["shards"][-1]["path"]
    payload = encoded.objects[relative_path]
    objects = dict(encoded.objects)
    objects[relative_path] = bytes([payload[0] ^ 1]) + payload[1:]
    mutated = replace(encoded, objects=objects)
    index_path = tmp_path / "index.json"
    prior = b"prior-index\n"
    index_path.write_bytes(prior)
    publication_events = []

    with pytest.raises(generator.PublicationFailure) as error:
        generator.publish_v2_package(
            mutated,
            index_path,
            failure_injector=lambda stage, detail: publication_events.append(
                (stage, detail)
            ),
        )

    assert error.value.state == "PREPARED"
    assert isinstance(error.value.cause, generator.WireFormatError)
    assert not publication_events
    assert index_path.read_bytes() == prior
    assert not tuple((tmp_path / "objects").glob("*.jsonl"))


def test_package_v2_publish_rejects_divergent_index_views(tmp_path) -> None:
    generator = load_generator()
    encoded = generator.encode_tiny_v2_package(
        literal_package_v2_logical_fixture()
    )
    mutated = replace(encoded, index_bytes=b"{}\n")
    index_path = tmp_path / "index.json"
    prior = b"prior-index\n"
    index_path.write_bytes(prior)

    with pytest.raises(generator.PublicationFailure) as error:
        generator.publish_v2_package(mutated, index_path)

    assert error.value.state == "PREPARED"
    assert isinstance(error.value.cause, generator.WireFormatError)
    assert index_path.read_bytes() == prior
    assert not tuple((tmp_path / "objects").glob("*.jsonl"))


def test_package_v2_publish_rejects_cap_above_frozen_ceiling(tmp_path) -> None:
    generator = load_generator()
    encoded = generator.encode_tiny_v2_package(
        literal_package_v2_logical_fixture(production=True),
        scope="production-full",
    )
    index_path = tmp_path / "index.json"

    with pytest.raises(generator.WireFormatError, match="cap"):
        generator.publish_v2_package(
            encoded,
            index_path,
            package_cap=generator.PACKAGE_BYTE_CAP + 1,
        )

    assert not index_path.exists()
    assert not (tmp_path / "objects").exists()


def test_package_v2_publish_rejects_rehashed_oversized_object_line(
    tmp_path,
) -> None:
    generator = load_generator()
    encoded = generator.encode_tiny_v2_package(
        literal_package_v2_logical_fixture()
    )
    oversized = b'["' + b"x" * generator.MAX_CANONICAL_LINE_BYTES + b'"]\n'
    mutated = reseal_package_v2_object(generator, encoded, 0, oversized)
    index_path = tmp_path / "index.json"
    prior = b"prior-index\n"
    index_path.write_bytes(prior)

    with pytest.raises(generator.PublicationFailure) as error:
        generator.publish_v2_package(mutated, index_path)

    assert error.value.state == "PREPARED"
    assert isinstance(error.value.cause, generator.WireFormatError)
    assert "line" in str(error.value.cause)
    assert index_path.read_bytes() == prior
    assert not tuple((tmp_path / "objects").glob("*.jsonl"))


def test_package_v2_commit_state_precedes_index_temp_bookkeeping() -> None:
    source = GENERATOR.read_text(encoding="utf-8")
    replace_offset = source.index("os.replace(index_temporary, target)")
    committed_offset = source.index('state = "COMMITTED"', replace_offset)
    bookkeeping_offset = source.index(
        "temporary_paths.remove(index_temporary)", replace_offset
    )

    assert replace_offset < committed_offset < bookkeeping_offset


def test_package_v2_prepared_temp_cleanup_fsyncs_objects_directory(
    monkeypatch,
    tmp_path,
) -> None:
    generator = load_generator()
    encoded = generator.encode_tiny_v2_package(
        literal_package_v2_logical_fixture()
    )
    objects_dir = tmp_path / "objects"
    fsynced = []
    monkeypatch.setattr(
        generator,
        "_fsync_directory",
        lambda path: fsynced.append(
            (Path(path), tuple(objects_dir.glob(".object.*.tmp")))
        ),
    )

    def inject(stage, _detail):
        if stage == "object_temp_fsynced":
            raise OSError("injected temp-boundary failure")

    with pytest.raises(generator.PublicationFailure):
        generator.publish_v2_package(
            encoded,
            tmp_path / "index.json",
            failure_injector=inject,
        )

    assert (objects_dir, ()) in fsynced


def test_package_v2_prepared_cleanup_tracks_object_replace_before_return(
    monkeypatch,
    tmp_path,
) -> None:
    generator = load_generator()
    encoded = generator.encode_tiny_v2_package(
        literal_package_v2_logical_fixture()
    )
    index_path = tmp_path / "index.json"
    prior = b"prior-index\n"
    index_path.write_bytes(prior)
    real_replace = generator.os.replace
    raised = False

    def replace_then_raise(source, destination):
        nonlocal raised
        real_replace(source, destination)
        if not raised and Path(destination).parent == tmp_path / "objects":
            raised = True
            raise OSError("injected after object replacement")

    monkeypatch.setattr(generator.os, "replace", replace_then_raise)

    with pytest.raises(generator.PublicationFailure) as error:
        generator.publish_v2_package(encoded, index_path)

    assert error.value.state == "PREPARED"
    assert index_path.read_bytes() == prior
    objects = tmp_path / "objects"
    assert not objects.exists() or not tuple(objects.iterdir())
    assert not tuple(tmp_path.rglob("*.tmp"))


@pytest.mark.parametrize(
    "failure_stage",
    (
        "object_temp_fsynced",
        "object_replaced",
        "objects_dir_fsynced",
        "index_temp_fsynced",
        "before_index_replace",
    ),
)
def test_package_v2_prepared_failures_preserve_prior_index_and_clean(
    tmp_path, failure_stage
) -> None:
    generator = load_generator()
    encoded = generator.encode_tiny_v2_package(
        literal_package_v2_logical_fixture()
    )
    attempt_root = tmp_path / failure_stage
    index_path = attempt_root / "index.json"
    index_path.parent.mkdir(parents=True)
    prior = b'{"prior":true}\n'
    index_path.write_bytes(prior)

    def fail(stage, _detail):
        if stage == failure_stage:
            raise RuntimeError(failure_stage)

    with pytest.raises(generator.PublicationFailure) as error:
        generator.publish_v2_package(
            encoded, index_path, failure_injector=fail
        )
    assert error.value.state == "PREPARED"
    assert error.value.stage == failure_stage
    assert index_path.read_bytes() == prior
    objects = attempt_root / "objects"
    assert not objects.exists() or not tuple(objects.iterdir())
    assert not tuple(attempt_root.rglob("*.tmp"))


@pytest.mark.parametrize(
    "failure_stage", ("index_replaced", "index_dir_fsynced")
)
def test_package_v2_committed_failures_leave_complete_package(
    tmp_path, failure_stage
) -> None:
    generator = load_generator()
    verifier = load_package_v2_verifier()
    logical = literal_package_v2_logical_fixture()
    encoded = generator.encode_tiny_v2_package(logical)
    attempt_root = tmp_path / failure_stage
    index_path = attempt_root / "index.json"

    def fail(stage, _detail):
        if stage == failure_stage:
            raise RuntimeError(failure_stage)

    with pytest.raises(generator.PublicationFailure) as error:
        generator.publish_v2_package(
            encoded, index_path, failure_injector=fail
        )
    assert error.value.state == "COMMITTED"
    assert error.value.stage == failure_stage
    assert verifier.decode_v2_package_path(index_path) == logical
    assert not tuple(attempt_root.rglob("*.tmp"))
    assert not (attempt_root / "attestation.json").exists()
    assert not (attempt_root / "receipt.json").exists()


def test_package_v2_cap_blocks_production_index_replacement(tmp_path) -> None:
    generator = load_generator()
    logical = literal_package_v2_logical_fixture(production=True)
    encoded = generator.encode_tiny_v2_package(
        logical, scope="production-full"
    )
    index_path = tmp_path / "index.json"
    prior = b'{"prior":true}\n'
    index_path.write_bytes(prior)
    with pytest.raises(generator.PublicationFailure) as error:
        generator.publish_v2_package(encoded, index_path, package_cap=1)
    assert error.value.state == "PREPARED"
    assert error.value.stage == "before_index_replace"
    assert index_path.read_bytes() == prior
    objects = tmp_path / "objects"
    assert not objects.exists() or not tuple(objects.iterdir())


def test_package_v2_metrics_do_not_change_package_bytes() -> None:
    generator = load_generator()
    logical = literal_package_v2_logical_fixture()
    plain = generator.encode_tiny_v2_package(logical)
    metrics = generator.PhaseMetrics(enabled=True)
    instrumented = generator.encode_tiny_v2_package(
        logical, metrics=metrics
    )

    assert instrumented.index_bytes == plain.index_bytes
    assert instrumented.objects == plain.objects
    snapshot = metrics.snapshot()
    assert set(snapshot) == {"format", "stages", "record_counts", "byte_counts"}
    assert set(snapshot["stages"]) == set(generator.METRIC_STAGES)
    assert set(snapshot["record_counts"]) == set(generator.METRIC_TAGS)
    assert set(snapshot["byte_counts"]) == set(generator.METRIC_TAGS)
    assert all(
        isinstance(value, float) and value >= 0
        for value in snapshot["stages"].values()
    )
    assert all(
        isinstance(value, int) and value >= 0
        for value in snapshot["record_counts"].values()
    )
    assert all(
        isinstance(value, int) and value >= 0
        for value in snapshot["byte_counts"].values()
    )
    forbidden = {"command", "pid", "timestamp", "secret", "payload"}
    assert forbidden.isdisjoint(snapshot)


def test_task2_preflight_old_selection_and_sample_censuses_are_literal() -> None:
    module = load_generator()
    expected = {
        "fixed": (0, 8, 15, 23, 31, 38, 46, 54, 61, 69),
        "base": (0, 1),
        "singleton": (0,),
        "P": (0, 3, 5, 8, 10, 13, 16, 18, 21, 23, 26, 28, 31),
        "C": (0, 19, 38),
        "Q": (0, 15, 30, 46, 61, 76, 91),
    }
    assert module.PREFLIGHT_SELECTED_OLD_INDICES == expected
    assert module.PREFLIGHT_SOURCE_LOADS == 1_406
    assert module.PREFLIGHT_OCCURRENCE_LOADS == 2_716
    assert module.PREFLIGHT_COMPARISONS == 228_144
    assert 2_716 * 84 == 228_144


def test_task2_production_selected_old_indices_are_complete_ranges() -> None:
    module = load_generator()
    catalog = module.build_task4_schema_catalog(module.load_source_context())
    discovery = module.discover_family_generation(
        catalog,
        "base",
        selected_old_indices=(0,),
    )
    with pytest.raises(
        module.CertificateFailure,
        match="production old indices are not complete",
    ):
        next(
            module.iter_family_records(
                catalog,
                discovery,
                scope=module.PRODUCTION_SCOPE,
            )
        )


def test_task2_template_selection_is_zero_based_every_eighth_union_all_tied_maxima(
    monkeypatch,
) -> None:
    module = load_generator()
    schema_ids = tuple(f"schema-{index:02d}" for index in range(17))
    schemas = {
        schema_id: module.Schema(schema_id, ("a",), ())
        for schema_id in reversed(schema_ids)
    }
    cell = module.Cell("cell", ("a",), (0,), (0,))
    pump_counts = {
        schema_id: 3 if index in (2, 5) else 1
        for index, schema_id in enumerate(schema_ids)
    }

    def fake_build_template(schema, _cell):
        return SimpleNamespace(
            pumping_witnesses=(None,) * pump_counts[schema.schema_id]
        )

    monkeypatch.setattr(module, "build_template", fake_build_template)
    family = module.Task4FamilyCatalog(
        family="fixed",
        variables=("a",),
        cells=(cell,),
        schemas=schemas,
        old_tokens=(),
        b_tokens=(),
        old_schema_refs={},
        b_schema_refs={},
        old_footprint_bindings={},
    )
    assert module.preflight_template_selection(family) == (
        (0, 2, 5, 8, 16),
        ("schema-02", "schema-05"),
    )


def test_task2_cold_full_catalog_precompute_precedes_template_filter(
    monkeypatch,
) -> None:
    module = load_generator()
    events = []
    original_load = module.load_source_context
    original_build = module.build_task4_schema_catalog
    original_select = module.preflight_template_selection

    def observed_load():
        events.append(("load",))
        return original_load()

    def observed_build(context):
        catalog = original_build(context)
        schema_count = sum(
            len(item.schemas) for item in catalog.families.values()
        )
        identity_count = sum(
            len(item.schemas) * len(item.cells)
            for item in catalog.families.values()
        )
        events.append(("catalog", schema_count, identity_count))
        return catalog

    def observed_select(family_catalog):
        events.append(("selection", family_catalog.family))
        return original_select(family_catalog)

    monkeypatch.setattr(module, "load_source_context", observed_load)
    monkeypatch.setattr(module, "build_task4_schema_catalog", observed_build)
    monkeypatch.setattr(module, "preflight_template_selection", observed_select)
    context = module.load_source_context()
    catalog = module.build_task4_schema_catalog(context)
    module.preflight_template_selection(catalog.families["singleton"])
    assert events == [
        ("load",),
        ("catalog", 1_304, 48_252),
        ("selection", "singleton"),
    ]


def test_task2_shared_iterator_emits_complete_source_and_84_token_tables() -> None:
    module = load_generator()
    catalog = module.build_task4_schema_catalog(module.load_source_context())
    records = tuple(
        module.iter_shared_records(
            catalog,
            scope=module.PREFLIGHT_SCOPE,
            status=module.PREFLIGHT_STATUS,
        )
    )
    dependency_rows = [row for row in records if row[0] == "dependency"]
    source_row = next(row for row in records if row[0] == "source_bindings")
    identities = [row for row in records if row[0] == "b_identity"]
    coordinates = [row for row in records if row[0] == "b_coordinate"]
    assert dependency_rows == [
        ("dependency", path, catalog.dependency_digests[path])
        for path in sorted(catalog.dependency_digests)
    ]
    assert source_row[1] == module.build_source_bindings(catalog)
    assert source_row[1]["format"] == "task4-source-bindings-v1"
    assert [row[1] for row in identities] == list(range(84))
    assert [row[1] for row in coordinates] == list(range(84))
    assert len(identities) == len(coordinates) == 84


def test_task2_adapters_pass_when_build_manifest_is_monkeypatched_to_raise(
    monkeypatch,
) -> None:
    module = load_generator()

    def forbidden_manifest(*_args, **_kwargs):
        raise AssertionError("Task 2 must not call build_manifest")

    monkeypatch.setattr(module, "build_manifest", forbidden_manifest)
    catalog = module.build_task4_schema_catalog(module.load_source_context())
    selected_schema_indices, _tied_ids = module.preflight_template_selection(
        catalog.families["singleton"]
    )
    discovery = module.discover_family_generation(
        catalog,
        "singleton",
        selected_old_indices=(0,),
    )
    shared = module.iter_shared_records(
        catalog,
        scope=module.PREFLIGHT_SCOPE,
        status=module.PREFLIGHT_STATUS,
    )
    assert next(shared)[0] == "shared_header"
    family_records = module.iter_family_records(
        catalog,
        discovery,
        scope=module.PREFLIGHT_SCOPE,
        selected_template_schema_indices=selected_schema_indices,
    )
    destination = ARTIFACT_DIR / "task2-adapter-singleton.jsonl"
    streamed = module.write_jsonl_stream(family_records, destination)
    assert streamed.record_count > 0
    assert module.ceil_ratio(5, 11, 3) == 19
    projection_inputs = tuple(
        module.FamilyProjectionInput(
            family=family,
            selected_old_indices=module.PREFLIGHT_SELECTED_OLD_INDICES[family],
            selected_schema_indices=(0,),
            tied_max_schema_ids=(f"{family}-max",),
            full_schema_count=2,
            full_comparisons=168,
            sampled_comparisons=84,
            sampled_two_pass_ns=1,
            sampled_load_bucket_bytes=1,
            sampled_load_record_count=1,
            projected_bucket_class_count=3,
            full_identity_count=2,
            sampled_identity_count=1,
            sampled_template_ns=1,
            sampled_template_bytes=1,
            fixed_family_ns=1,
            fixed_family_bytes=1,
        )
        for family in module.FAMILY_ORDER
    )
    projection = module.project_generation(
        source_catalog_precompute_ns=1,
        shared_ns=1,
        shared_bytes=1,
        projected_index_ns=1,
        projected_index_input=_task2_fix2_projected_index_input(
            module,
            projection_inputs,
            shared_bytes=1,
        ),
        families=projection_inputs,
    )
    assert projection.format == "period-two-old-new-cut-generation-projection-v1"
    payload = module.build_generation_receipt_payload(
        run_id="bounded-task2",
        scope=module.PREFLIGHT_SCOPE,
        index_path=".scratch/test-artifacts/old-new-load/index.json",
        index_sha256="1" * 64,
        root_sha256="2" * 64,
        state="committed",
        package_bytes=streamed.total_bytes,
        created_objects=(streamed.path.name,),
        reused_objects=(),
        generator_sha256="3" * 64,
        metrics={},
    )
    assert payload["run_id"] == "bounded-task2"


@pytest.fixture(scope="module")
def task2_catalog_fixture():
    module = load_generator()
    return module, module.build_task4_schema_catalog(module.load_source_context())


@pytest.fixture(scope="module")
def task2_singleton_discovery(task2_catalog_fixture):
    module, catalog = task2_catalog_fixture
    return module.discover_family_generation(
        catalog,
        "singleton",
        selected_old_indices=(0,),
    )


def test_task2_phase_a_freezes_canonical_bucket_table_before_any_load(
    task2_catalog_fixture, task2_singleton_discovery
) -> None:
    module, _catalog = task2_catalog_fixture
    discovery = task2_singleton_discovery
    encoded = [module.canonical_json(list(row)).encode("ascii") for row in discovery.bucket_classes]
    assert encoded == sorted(set(encoded))
    assert len(discovery.cell_footers) == discovery.source_cell_count
    assert all(footer.load_record_count > 0 for footer in discovery.cell_footers)


def test_task2_phase_a_retains_no_rows_masks_or_family_ledger(
    task2_singleton_discovery,
) -> None:
    discovery = task2_singleton_discovery
    assert tuple(field.name for field in fields(discovery)) == (
        "family",
        "variables",
        "selected_old_indices",
        "source_cell_count",
        "old_load_count",
        "footprint_count",
        "bucket_classes",
        "cell_footers",
        "load_rows",
        "occurrence_loads",
        "comparisons",
    )
    assert all(isinstance(row, tuple) for row in discovery.bucket_classes)
    assert all(isinstance(footer.odd_old_indices, tuple) for footer in discovery.cell_footers)
    forbidden = {"row", "rows", "mask", "masks", "ledger", "logical_v1"}
    assert forbidden.isdisjoint(field.name for field in fields(discovery))


def test_task2_phase_b_recomputes_and_rejects_bucket_not_in_frozen_table(
    task2_catalog_fixture, task2_singleton_discovery, monkeypatch
) -> None:
    module, catalog = task2_catalog_fixture
    original = module.comparison_record

    def changed_bucket(*args, **kwargs):
        record = dict(original(*args, **kwargs))
        record["b_source_class"] = f"{record['b_source_class']}-new"
        return record

    monkeypatch.setattr(module, "comparison_record", changed_bucket)
    with pytest.raises(module.CertificateFailure, match="frozen bucket"):
        tuple(
            module.iter_family_records(
                catalog,
                task2_singleton_discovery,
                scope=module.PREFLIGHT_SCOPE,
                selected_template_schema_indices=(0,),
            )
        )


def test_task2_family_iterator_order_and_footer_prefixes_are_exact(
    task2_catalog_fixture, task2_singleton_discovery
) -> None:
    module, catalog = task2_catalog_fixture
    selected, _tied = module.preflight_template_selection(
        catalog.families["singleton"]
    )
    records = tuple(
        module.iter_family_records(
            catalog,
            task2_singleton_discovery,
            scope=module.PREFLIGHT_SCOPE,
            selected_template_schema_indices=selected,
        )
    )
    tags = [row[0] for row in records]
    assert tags[0] == "family_header"
    assert tags[1 : 1 + task2_singleton_discovery.old_load_count] == [
        "old_load"
    ] * task2_singleton_discovery.old_load_count
    footprint_start = 1 + task2_singleton_discovery.old_load_count
    assert tags[
        footprint_start : footprint_start + task2_singleton_discovery.footprint_count
    ] == ["footprint"] * task2_singleton_discovery.footprint_count
    bucket_start = footprint_start + task2_singleton_discovery.footprint_count
    assert tags[
        bucket_start : bucket_start + len(task2_singleton_discovery.bucket_classes)
    ] == ["bucket_class"] * len(task2_singleton_discovery.bucket_classes)
    assert tags[-1] == "family_footer"
    assert records[-1][6] == len(records) - 1
    assert records[-1][7] == sum(
        len(module.canonical_json_line(row)) for row in records[:-1]
    )
    footers = [row for row in records if row[0] == "cell_footer"]
    assert tuple(row[1:] for row in footers) == tuple(
        (
            footer.source_cell_index,
            footer.compact_cell_index,
            footer.cell_id,
            list(footer.odd_old_indices),
            footer.value,
            footer.load_record_count,
        )
        for footer in task2_singleton_discovery.cell_footers
    )


def _task2_reseal_source_bindings(module, source_bindings) -> None:
    payload = {key: value for key, value in source_bindings.items() if key != "sha256"}
    source_bindings["sha256"] = hashlib.sha256(
        module.canonical_json(payload).encode("ascii")
    ).hexdigest()


def _task2_multimember_old_fiber(old):
    return next(
        fiber
        for fibers in old["integral_fibers"].values()
        for fiber in fibers
        if len(fiber["members"]) > 1
    )


def _task2_old_fiber(old, *, active):
    return next(
        fiber
        for fibers in old["integral_fibers"].values()
        for fiber in fibers
        if fiber["active"] is active
    )


def _task2_b_fiber(source_bindings, *, active=None, multimember=False):
    return next(
        fiber
        for fiber in source_bindings["b"]["collision_fibers"]
        if (active is None or fiber["active"] is active)
        and (not multimember or len(fiber["members"]) > 1)
    )


def _task2_mutated_source_bindings(module, catalog, mutation):
    source = module.build_source_bindings(catalog)
    old = source["old"]
    if mutation == "raw-row":
        family = next(iter(old["raw_family_rows"]))
        old["raw_family_rows"][family] += 1
    elif mutation == "raw-provenance":
        old["raw_provenance_counts"]["W"] += 1
    elif mutation == "raw-provenance-count":
        old["raw_provenance_counts"]["V"] += 1
    elif mutation == "raw-id-duplicate":
        old["raw_ids_unique"] = False
    elif mutation == "missing-provenance":
        old["missing_raw_provenance"] = ["missing"]
    elif mutation in {"inactive-old-fiber", "active-old-fiber"}:
        fiber = _task2_old_fiber(old, active=mutation.startswith("active"))
        fiber["active"] = not fiber["active"]
    elif mutation == "member-id-order":
        fiber = _task2_multimember_old_fiber(old)
        fiber["member_ids"] = list(reversed(fiber["member_ids"]))
    elif mutation == "coefficient-order":
        fiber = _task2_multimember_old_fiber(old)
        fiber["coefficients"] = list(reversed(fiber["coefficients"]))
        if fiber["coefficients"] == [
            member["coefficient"] for member in fiber["members"]
        ]:
            fiber["coefficients"][0] += 1
    elif mutation == "member-table-row":
        fiber = _task2_multimember_old_fiber(old)
        fiber["members"][0]["id"] += "-mutated"
    elif mutation == "integral-sum":
        _task2_old_fiber(old, active=True)["integral_sum"] += 1
    elif mutation == "parity":
        _task2_old_fiber(old, active=True)["parity"] ^= 1
    elif mutation == "activity":
        fiber = _task2_old_fiber(old, active=True)
        fiber["active"] = False
    elif mutation == "domain":
        _task2_old_fiber(old, active=True)["members"][0]["domain"] = {"op": "mutated"}
    elif mutation == "current-equality":
        _task2_old_fiber(old, active=True)["members"][0]["current_equality"] = {"op": "mutated"}
    elif mutation == "label-witness":
        _task2_old_fiber(old, active=True)["label_equality_witness"] = {"equal": False}
    elif mutation in {"fixed-one-member", "singleton-one-member"}:
        family = mutation.removesuffix("-one-member")
        old["one_member_sources"][family][0]["coefficient"] += 2
    elif mutation == "anchor-pair":
        old["anchor_provenance"][0]["coefficient"] += 1
    elif mutation == "anchor-sum":
        old["anchor_integral_sum"] += 1
    elif mutation == "anchor-provenance":
        old["anchor_provenance"][0]["id"] += "-mutated"
    elif mutation in {"inactive-b-fiber", "active-b-fiber"}:
        fiber = _task2_b_fiber(source, active=mutation.startswith("active"))
        fiber["active"] = not fiber["active"]
    elif mutation == "b-member-order":
        fiber = _task2_b_fiber(source, multimember=True)
        fiber["members"] = list(reversed(fiber["members"]))
    elif mutation == "b-coefficient-order":
        fiber = _task2_b_fiber(source, multimember=True)
        fiber["coefficients"] = list(reversed(fiber["coefficients"]))
        if fiber["coefficients"] == [
            pair[1] for pair in fiber["member_coefficients"]
        ]:
            fiber["coefficients"][0] += 1
    elif mutation == "b-member-coefficient-pair":
        fiber = _task2_b_fiber(source, multimember=True)
        fiber["member_coefficients"][0][1] += 1
    elif mutation == "b-integral-sum":
        _task2_b_fiber(source, active=True)["integral_sum"] += 1
    elif mutation == "b-parity":
        _task2_b_fiber(source, active=True)["parity"] ^= 1
    elif mutation == "b-activity":
        _task2_b_fiber(source, active=True)["active"] = False
    elif mutation == "b-slot":
        _task2_b_fiber(source)["slot"] = "bad"
    elif mutation == "b-module-schema":
        _task2_b_fiber(source)["canonical_module_schema"] = ""
    elif mutation == "b-label-witness":
        _task2_b_fiber(source)["label_equality_witness"] = {"equal": False}
    elif mutation == "source-digest":
        old["source_digests"] = {**old["source_digests"], "extra": "0" * 64}
    else:
        raise AssertionError(f"unknown source mutation: {mutation}")
    _task2_reseal_source_bindings(module, source)
    return source


def _task2_assert_source_mutation_fails(module, catalog, monkeypatch, mutation):
    pristine = module.build_source_bindings(catalog)
    mutated = _task2_mutated_source_bindings(module, catalog, mutation)
    calls = 0

    def injected_source_bindings(_catalog):
        nonlocal calls
        calls += 1
        return copy.deepcopy(mutated if calls == 1 else pristine)

    monkeypatch.setattr(module, "build_source_bindings", injected_source_bindings)
    with pytest.raises(module.CertificateFailure):
        module.discover_family_generation(
            catalog,
            "singleton",
            selected_old_indices=(0,),
        )


@pytest.mark.parametrize(
    "mutation",
    (
        "raw-row",
        "raw-provenance",
        "raw-provenance-count",
        "raw-id-duplicate",
        "missing-provenance",
    ),
)
def test_task2_old_raw_rows_and_provenance_mutations_fail_closed(
    task2_catalog_fixture, monkeypatch, mutation
) -> None:
    module, catalog = task2_catalog_fixture
    _task2_assert_source_mutation_fails(module, catalog, monkeypatch, mutation)


@pytest.mark.parametrize("mutation", ("inactive-old-fiber", "active-old-fiber"))
def test_task2_old_integral_fiber_mutations_fail_closed(
    task2_catalog_fixture, monkeypatch, mutation
) -> None:
    module, catalog = task2_catalog_fixture
    _task2_assert_source_mutation_fails(module, catalog, monkeypatch, mutation)


@pytest.mark.parametrize(
    "mutation",
    (
        "member-id-order",
        "coefficient-order",
        "member-table-row",
        "integral-sum",
        "parity",
        "activity",
        "domain",
        "current-equality",
        "label-witness",
    ),
)
def test_task2_old_member_alignment_domain_and_equality_mutations_fail_closed(
    task2_catalog_fixture, monkeypatch, mutation
) -> None:
    module, catalog = task2_catalog_fixture
    _task2_assert_source_mutation_fails(module, catalog, monkeypatch, mutation)


@pytest.mark.parametrize(
    "mutation",
    (
        "fixed-one-member",
        "singleton-one-member",
        "anchor-pair",
        "anchor-sum",
        "anchor-provenance",
    ),
)
def test_task2_one_member_and_anchor_mutations_fail_closed(
    task2_catalog_fixture, monkeypatch, mutation
) -> None:
    module, catalog = task2_catalog_fixture
    _task2_assert_source_mutation_fails(module, catalog, monkeypatch, mutation)


@pytest.mark.parametrize("mutation", ("inactive-b-fiber", "active-b-fiber"))
def test_task2_b_all_fiber_and_activity_mutations_fail_closed(
    task2_catalog_fixture, monkeypatch, mutation
) -> None:
    module, catalog = task2_catalog_fixture
    _task2_assert_source_mutation_fails(module, catalog, monkeypatch, mutation)


@pytest.mark.parametrize(
    "mutation",
    (
        "b-member-order",
        "b-coefficient-order",
        "b-member-coefficient-pair",
        "b-integral-sum",
        "b-parity",
        "b-activity",
        "b-slot",
        "b-module-schema",
        "b-label-witness",
    ),
)
def test_task2_b_fiber_member_mutations_fail_closed(
    task2_catalog_fixture, monkeypatch, mutation
) -> None:
    module, catalog = task2_catalog_fixture
    _task2_assert_source_mutation_fails(module, catalog, monkeypatch, mutation)


@pytest.mark.parametrize(
    "mutation",
    (
        "b-member-order",
        "b-coefficient-order",
        "b-member-coefficient-pair",
        "b-integral-sum",
        "b-parity",
        "b-activity",
        "b-slot",
        "b-module-schema",
        "b-label-witness",
        "token-index",
        "token-id",
        "source-class",
        "token-coefficient",
        "token-slot",
        "occurrence",
        "polarity",
        "module-schema",
        "label-schema",
        "source-members",
        "coordinate",
        "source-digest",
        "chronology-digest",
        "b-identity-digest",
        "catalog-digest",
    ),
)
def test_task2_b_identity_coordinate_and_schema_mutations_fail_closed(
    task2_catalog_fixture, task2_singleton_discovery, monkeypatch, mutation
) -> None:
    module, catalog = task2_catalog_fixture
    source_mutations = {
        "b-member-order",
        "b-coefficient-order",
        "b-member-coefficient-pair",
        "b-integral-sum",
        "b-parity",
        "b-activity",
        "b-slot",
        "b-module-schema",
        "b-label-witness",
        "source-digest",
    }
    if mutation in source_mutations:
        _task2_assert_source_mutation_fails(module, catalog, monkeypatch, mutation)
        return
    if mutation == "chronology-digest":
        mutated_catalog = replace(catalog, chronology_digest="0" * 64)
    elif mutation == "b-identity-digest":
        mutated_catalog = replace(catalog, b_identity_digest="0" * 64)
    elif mutation == "catalog-digest":
        original = module.build_compact_template_catalog

        def mutated_catalog_digest(*args, **kwargs):
            value = original(*args, **kwargs)
            value["catalog_sha256"] = "0" * 64
            return value

        monkeypatch.setattr(module, "build_compact_template_catalog", mutated_catalog_digest)
        with pytest.raises(module.CertificateFailure):
            tuple(
                module.iter_family_records(
                    catalog,
                    task2_singleton_discovery,
                    scope=module.PREFLIGHT_SCOPE,
                    selected_template_schema_indices=(0,),
                )
            )
        return
    elif mutation == "coordinate":
        item = catalog.families["singleton"]
        tokens = list(item.b_tokens)
        tokens[0] = replace(tokens[0], source_members=("mutated",))
        families = dict(catalog.families)
        families["singleton"] = replace(item, b_tokens=tuple(tokens))
        mutated_catalog = replace(catalog, families=families)
    else:
        field_by_mutation = {
            "token-index": "token_index",
            "token-id": "token_id",
            "source-class": "source_class",
            "token-coefficient": "coefficient",
            "token-slot": "slot",
            "occurrence": "occurrence",
            "polarity": "polarity",
            "module-schema": "module_schema",
            "label-schema": "label_schema",
            "source-members": "source_members",
        }
        rows = [dict(row) for row in catalog.b_identity_table]
        field = field_by_mutation[mutation]
        value = rows[0][field]
        rows[0][field] = value + 1 if isinstance(value, int) else "mutated"
        table = tuple(rows)
        mutated_catalog = replace(
            catalog,
            b_identity_table=table,
            b_identity_digest=module._identity_digest(table),
        )
    with pytest.raises(module.CertificateFailure):
        module.discover_family_generation(
            mutated_catalog,
            "singleton",
            selected_old_indices=(0,),
        )


def _task2_reverse_84_bits(mask):
    return sum(((mask >> index) & 1) << (83 - index) for index in range(84))


def _task2_mutate_histogram(histogram, mutation):
    mutated = copy.deepcopy(histogram)
    buckets = mutated["buckets"]
    if mutation == "comparison-count-83":
        mutated["comparison_count"] = 83
    elif mutation == "comparison-count-85":
        mutated["comparison_count"] = 85
    elif mutation == "zero-mask":
        buckets[0]["mask"] = "0" * 21
    elif mutation == "overlapping-masks":
        first = int(buckets[0]["mask"], 16)
        buckets[1]["mask"] = f"{int(buckets[1]['mask'], 16) | (first & -first):021x}"
    elif mutation == "missing-union-bit":
        first = int(buckets[0]["mask"], 16)
        buckets[0]["mask"] = f"{first & (first - 1):021x}"
    elif mutation == "token-bit-reversal":
        for bucket in buckets:
            bucket["mask"] = f"{_task2_reverse_84_bits(int(bucket['mask'], 16)):021x}"
    elif mutation == "stored-count":
        buckets[0]["count"] += 1
    elif mutation == "mask-popcount":
        donor_index = next(
            index
            for index, bucket in enumerate(buckets)
            if bin(int(bucket["mask"], 16)).count("1") > 1  # noqa: FURB161
        )
        receiver_index = next(
            index for index in range(len(buckets)) if index != donor_index
        )
        donor_mask = int(buckets[donor_index]["mask"], 16)
        receiver_mask = int(buckets[receiver_index]["mask"], 16)
        moved_bit = donor_mask & -donor_mask
        buckets[donor_index]["mask"] = f"{donor_mask ^ moved_bit:021x}"
        buckets[receiver_index]["mask"] = f"{receiver_mask | moved_bit:021x}"
    elif mutation == "bucket-key":
        buckets[0]["key"]["b_source_class"] += "-mutated"
    elif mutation == "contribution-bit":
        buckets[0]["key"]["contribution_bit"] ^= 1
    elif mutation == "occurrence-parity":
        mutated["value"] ^= 1
    else:
        raise AssertionError(f"unknown histogram mutation: {mutation}")
    return mutated


@pytest.mark.parametrize(
    "mutation",
    (
        "comparison-count-83",
        "comparison-count-85",
        "zero-mask",
        "overlapping-masks",
        "missing-union-bit",
        "token-bit-reversal",
        "stored-count",
        "mask-popcount",
        "bucket-key",
        "contribution-bit",
        "occurrence-parity",
        "cell-parity",
        "family-parity",
        "source-load-census",
        "occurrence-load-census",
        "comparison-census",
    ),
)
def test_task2_every_footprint_partition_mutation_fails_closed(
    task2_catalog_fixture, task2_singleton_discovery, monkeypatch, mutation
) -> None:
    module, catalog = task2_catalog_fixture
    discovery = task2_singleton_discovery
    if mutation in {
        "cell-parity",
        "family-parity",
        "source-load-census",
        "occurrence-load-census",
        "comparison-census",
    }:
        if mutation == "cell-parity":
            footers = list(discovery.cell_footers)
            footers[0] = replace(footers[0], value=footers[0].value ^ 1)
            discovery = replace(discovery, cell_footers=tuple(footers))
        elif mutation == "family-parity":
            original_expected = module._expected_family_value

            def mutated_family_value(family, cell):
                value = original_expected(family, cell)
                return (
                    value ^ 1
                    if cell == catalog.families[family].cells[0]
                    else value
                )

            monkeypatch.setattr(module, "_expected_family_value", mutated_family_value)
        elif mutation == "source-load-census":
            discovery = replace(discovery, load_rows=discovery.load_rows + 1)
        elif mutation == "occurrence-load-census":
            discovery = replace(
                discovery, occurrence_loads=discovery.occurrence_loads + 1
            )
        else:
            discovery = replace(discovery, comparisons=discovery.comparisons + 1)
    elif mutation == "token-bit-reversal":
        original_comparison = module.comparison_record

        def reversed_token_bit(*args, **kwargs):
            comparison = dict(original_comparison(*args, **kwargs))
            comparison["token_index"] = 83 - comparison["token_index"]
            return comparison

        monkeypatch.setattr(module, "comparison_record", reversed_token_bit)
    else:
        original = module._generation_histogram

        def mutated_histogram(*args, **kwargs):
            histogram = original(*args, **kwargs)
            return _task2_mutate_histogram(histogram, mutation)

        monkeypatch.setattr(module, "_generation_histogram", mutated_histogram)
    with pytest.raises(module.CertificateFailure):
        tuple(
            module.iter_family_records(
                catalog,
                discovery,
                scope=module.PREFLIGHT_SCOPE,
                selected_template_schema_indices=(0,),
            )
        )


def test_task2_fix2_reversed_masks_reach_token_bucket_orientation_gate(
    task2_catalog_fixture, task2_singleton_discovery, monkeypatch
) -> None:
    module, catalog = task2_catalog_fixture
    original_comparison = module.comparison_record
    original_histogram = module._generation_histogram
    observed_token_indices = []

    def observed_comparison(*args, **kwargs):
        comparison = original_comparison(*args, **kwargs)
        observed_token_indices.append(comparison["token_index"])
        return comparison

    def reversed_masks(*args, **kwargs):
        histogram = original_histogram(*args, **kwargs)
        return _task2_mutate_histogram(histogram, "token-bit-reversal")

    monkeypatch.setattr(module, "comparison_record", observed_comparison)
    monkeypatch.setattr(module, "_generation_histogram", reversed_masks)
    with pytest.raises(
        module.CertificateFailure,
        match="token-to-bucket orientation",
    ):
        tuple(
            module.iter_family_records(
                catalog,
                task2_singleton_discovery,
                scope=module.PREFLIGHT_SCOPE,
                selected_template_schema_indices=(0,),
            )
        )
    assert observed_token_indices == list(range(module.TOKEN_COUNT))


def test_task2_fix2_valid_masks_pass_token_bucket_orientation_gate(
    task2_catalog_fixture,
) -> None:
    module, catalog = task2_catalog_fixture
    item = catalog.families["singleton"]
    token = item.old_tokens[0]
    old = next(
        iter(
            module._old_occurrence_records(
                token,
                item.old_schema_refs[token.token_id],
                catalog,
            )
        )
    )
    histogram = module._generation_histogram(
        old,
        module._b_occurrence_records(item, catalog),
        item.schemas,
        item.cells[0],
    )
    assert module._validate_generation_histogram(histogram, old) is histogram


@pytest.mark.parametrize(
    "field",
    ("load_rows", "occurrence_loads", "comparisons"),
)
def test_task2_derived_family_census_and_parity_mutations_fail_closed(
    task2_catalog_fixture, task2_singleton_discovery, field
) -> None:
    module, catalog = task2_catalog_fixture
    discovery = replace(
        task2_singleton_discovery,
        **{field: getattr(task2_singleton_discovery, field) + 1},
    )
    with pytest.raises(module.CertificateFailure):
        tuple(
            module.iter_family_records(
                catalog,
                discovery,
                scope=module.PREFLIGHT_SCOPE,
                selected_template_schema_indices=(0,),
            )
        )


def test_task2_stream_writer_is_incremental_and_bounded() -> None:
    module = load_generator()
    destination = ARTIFACT_DIR / "task2-incremental.jsonl"
    observations = []

    def records():
        for index in range(128):
            if index:
                observations.append(destination.stat().st_size)
                assert observations[-1] > (observations[-2] if len(observations) > 1 else 0)
            yield ("dependency", str(index), f"{index:064x}" + "x" * 16_384)

    metrics = module.PhaseMetrics(enabled=True)
    tracemalloc.start()
    streamed = module.write_jsonl_stream(records(), destination, metrics=metrics)
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert streamed.record_count == 128
    assert streamed.total_bytes == destination.stat().st_size
    assert streamed.sha256 == hashlib.sha256(destination.read_bytes()).hexdigest()
    assert streamed.record_counts == {"dependency": 128}
    assert observations == sorted(observations)
    assert peak < 2_000_000
    assert metrics.snapshot()["record_counts"]["dependency"] == 128


def _task2_projection_inputs():
    module = load_generator()
    inputs = []
    for family in module.FAMILY_ORDER:
        is_target = family == "fixed"
        inputs.append(
            module.FamilyProjectionInput(
                family=family,
                selected_old_indices=module.PREFLIGHT_SELECTED_OLD_INDICES[family],
                selected_schema_indices=(0,),
                tied_max_schema_ids=(f"{family}-max",),
                full_schema_count=13 if is_target else 2,
                full_comparisons=924 if is_target else 168,
                sampled_comparisons=252 if is_target else 84,
                sampled_two_pass_ns=5 if is_target else 0,
                sampled_load_bucket_bytes=17 if is_target else 0,
                sampled_load_record_count=2 if is_target else 1,
                projected_bucket_class_count=9 if is_target else 3,
                full_identity_count=13 if is_target else 2,
                sampled_identity_count=4 if is_target else 1,
                sampled_template_ns=7 if is_target else 0,
                sampled_template_bytes=19 if is_target else 0,
                fixed_family_ns=30 if is_target else 0,
                fixed_family_bytes=300 if is_target else 0,
            )
        )
    return module, tuple(inputs)


def _task2_arithmetic_projection():
    module, inputs = _task2_projection_inputs()
    return module, inputs, module.project_generation(
        source_catalog_precompute_ns=10,
        shared_ns=20,
        shared_bytes=100,
        projected_index_ns=40,
        projected_index_input=_task2_fix2_projected_index_input(
            module,
            inputs,
            shared_bytes=100,
        ),
        families=inputs,
    )


def test_task2_projection_uses_integer_ceiling_and_separate_denominators() -> None:
    module, _inputs, projection = _task2_arithmetic_projection()
    assert module.ceil_ratio(5, 11, 3) == 19
    assert module.ceil_ratio(7, 13, 4) == 23
    assert module.ceil_ratio(17, 11, 3) == 63
    assert module.ceil_ratio(19, 13, 4) == 62
    assert projection.generation_ns_before_margin == 142
    assert projection.projected_generation_ns == 284
    assert projection.package_bytes_before_margin == (
        100 + projection.projected_index_bytes + 300 + 63 + 62
    )
    assert projection.projected_package_bytes == 2 * (
        100 + projection.projected_index_bytes + 300 + 63 + 62
    )
    target = projection.families[0]
    assert target.projected_two_pass_ns == 19
    assert target.projected_template_ns == 23
    assert target.projected_load_bucket_bytes == 63
    assert target.projected_template_bytes == 62


def test_task2_projection_charges_full_precompute_shared_and_family_tables() -> None:
    module, inputs, projection = _task2_arithmetic_projection()
    assert projection.generation_ns_before_margin == 10 + 20 + 30 + 40 + 19 + 23
    assert projection.package_bytes_before_margin == (
        100 + projection.projected_index_bytes + 300 + 63 + 62
    )
    changed_inputs = (
        replace(inputs[0], fixed_family_ns=37, fixed_family_bytes=311),
        *inputs[1:],
    )
    changed = module.project_generation(
        source_catalog_precompute_ns=11,
        shared_ns=22,
        shared_bytes=103,
        projected_index_ns=44,
        projected_index_input=_task2_fix2_projected_index_input(
            module,
            changed_inputs,
            shared_bytes=103,
        ),
        families=changed_inputs,
    )
    assert changed.generation_ns_before_margin - projection.generation_ns_before_margin == 1 + 2 + 4 + 7
    assert changed.package_bytes_before_margin - projection.package_bytes_before_margin == 3 + 11


def test_task2_projected_index_oracle_uses_actual_root_and_64_hex_fields() -> None:
    module, inputs = _task2_projection_inputs()
    index_input = _task2_fix2_projected_index_input(
        module,
        inputs,
        shared_bytes=1,
    )
    family_projections = tuple(
        module._generation_family_projection(value) for value in inputs
    )
    oracle = module.build_projected_index_oracle(
        index_input,
        shared_bytes=1,
        families=family_projections,
    )
    assert set(oracle) == set(module.ROOT_INDEX_FIELDS)
    assert all(
        len(descriptor["sha256"]) == 64 and descriptor["sha256"] == "0" * 64
        for descriptor in oracle["shards"]
    )
    projected_index_bytes = len(module.canonical_json_line(oracle))
    projection = module.project_generation(
        source_catalog_precompute_ns=1,
        shared_ns=1,
        shared_bytes=1,
        projected_index_ns=1,
        projected_index_input=index_input,
        families=inputs,
    )
    assert projection.projected_index_bytes == projected_index_bytes
    assert len(module.canonical_json_line(oracle)) == projection.projected_index_bytes


def test_task2_projection_applies_one_final_factor_two() -> None:
    _module, _inputs, projection = _task2_arithmetic_projection()
    assert projection.projected_generation_ns == 2 * projection.generation_ns_before_margin
    assert projection.projected_package_bytes == 2 * projection.package_bytes_before_margin
    assert projection.families[0].projected_two_pass_ns == 19
    assert projection.families[0].projected_template_ns == 23


def _task2_assert_no_float(value) -> None:
    assert not isinstance(value, float)
    if hasattr(value, "__dataclass_fields__"):
        for field in fields(value):
            _task2_assert_no_float(getattr(value, field.name))
    elif isinstance(value, (tuple, list, dict)):
        values = value.values() if isinstance(value, dict) else value
        for item in values:
            _task2_assert_no_float(item)


def test_task2_generation_projection_is_deterministic_and_has_no_floats() -> None:
    module, inputs, projection = _task2_arithmetic_projection()
    repeated = module.project_generation(
        source_catalog_precompute_ns=10,
        shared_ns=20,
        shared_bytes=100,
        projected_index_ns=40,
        projected_index_input=_task2_fix2_projected_index_input(
            module,
            inputs,
            shared_bytes=100,
        ),
        families=tuple(reversed(inputs)),
    )
    assert repeated == projection
    _task2_assert_no_float(projection)
    for args in ((True, 1, 1), (1.0, 1, 1), (-1, 1, 1), (1, 1, 0)):
        with pytest.raises(module.CertificateFailure):
            module.ceil_ratio(*args)
    invalid_inputs = (
        replace(inputs[0], sampled_comparisons=0),
        replace(inputs[0], sampled_comparisons=inputs[0].full_comparisons),
        replace(inputs[0], sampled_comparisons=inputs[0].full_comparisons + 1),
        replace(inputs[0], sampled_identity_count=0),
        replace(inputs[0], sampled_identity_count=inputs[0].full_identity_count),
        replace(inputs[0], sampled_two_pass_ns=1.0),
        replace(inputs[0], tied_max_schema_ids=()),
        replace(inputs[0], selected_old_indices=(0,)),
    )
    index_input = _task2_fix2_projected_index_input(
        module,
        inputs,
        shared_bytes=100,
    )
    for invalid in invalid_inputs:
        with pytest.raises(module.CertificateFailure):
            module.project_generation(
                source_catalog_precompute_ns=10,
                shared_ns=20,
                shared_bytes=100,
                projected_index_ns=40,
                projected_index_input=index_input,
                families=(invalid, *inputs[1:]),
            )
    with pytest.raises(module.CertificateFailure):
        module.project_generation(
            source_catalog_precompute_ns=10,
            shared_ns=20,
            shared_bytes=100,
            projected_index_ns=40,
            projected_index_input=index_input,
            families=inputs[:-1],
        )


def test_task2_generation_receipt_payload_constructor_is_pure(monkeypatch) -> None:
    module = load_generator()

    def filesystem_forbidden(*_args, **_kwargs):
        raise AssertionError("pure receipt constructor touched the filesystem")

    monkeypatch.setattr(Path, "write_text", filesystem_forbidden)
    monkeypatch.setattr(Path, "write_bytes", filesystem_forbidden)
    monkeypatch.setattr("builtins.open", filesystem_forbidden)
    monkeypatch.setattr(module.os, "replace", filesystem_forbidden)
    monkeypatch.setattr(module, "write_generation_receipt", filesystem_forbidden, raising=False)
    monkeypatch.setattr(module, "write_generation_attestation", filesystem_forbidden, raising=False)
    payload = module.build_generation_receipt_payload(
        run_id="task2-run",
        scope=module.PRODUCTION_SCOPE,
        index_path=".scratch/period-two-old-new-cut-package-v2/index.json",
        index_sha256="1" * 64,
        root_sha256="2" * 64,
        state="COMMITTED",
        package_bytes=725,
        created_objects=("objects/a.jsonl",),
        reused_objects=("objects/b.jsonl",),
        generator_sha256="3" * 64,
        metrics={"format": "period-two-old-new-cut-phase-metrics-v1"},
    )
    assert payload == {
        "format": "period-two-old-new-cut-generation-receipt-v1",
        "run_id": "task2-run",
        "scope": "production-full",
        "index_path": ".scratch/period-two-old-new-cut-package-v2/index.json",
        "index_sha256": "1" * 64,
        "root_sha256": "2" * 64,
        "state": "COMMITTED",
        "package_bytes": 725,
        "created_objects": ["objects/a.jsonl"],
        "reused_objects": ["objects/b.jsonl"],
        "generator_sha256": "3" * 64,
        "metrics": {"format": "period-two-old-new-cut-phase-metrics-v1"},
    }


def test_task2_writes_no_production_package_or_durable_evidence() -> None:
    module = load_generator()
    protected = (
        ROOT / ".scratch/period-two-old-new-cut-package-v2/index.json",
        ROOT / ".scratch/period-two-old-new-cut-package-v2/receipt.json",
        ROOT / ".scratch/period-two-old-new-cut-package-v2/attestation.json",
        ROOT / "docs/AK3_PROMISE_LEDGER.md",
    )
    before = {
        path: path.read_bytes() if path.exists() else None
        for path in protected
    }
    module.build_generation_receipt_payload(
        run_id="bounded-no-write",
        scope=module.PREFLIGHT_SCOPE,
        index_path=".scratch/test-artifacts/old-new-load/index.json",
        index_sha256="1" * 64,
        root_sha256="2" * 64,
        state="PREPARED",
        package_bytes=0,
        created_objects=(),
        reused_objects=(),
        generator_sha256="3" * 64,
        metrics={},
    )
    after = {
        path: path.read_bytes() if path.exists() else None
        for path in protected
    }
    assert after == before


def _task2_fix1_mutated_catalog(module, catalog, mutation):
    families = dict(catalog.families)
    family = families["Q"]
    if mutation == "missing-schema":
        schemas = dict(family.schemas)
        schemas.pop(max(schemas))
        families["Q"] = replace(family, schemas=schemas)
        return replace(catalog, families=families)
    if mutation == "replaced-schema":
        schemas = dict(family.schemas)
        schema_id = max(schemas)
        schema = schemas[schema_id]
        schemas[schema_id] = replace(
            schema,
            blocks=(*schema.blocks, ("mutated", (1,), None)),
        )
        families["Q"] = replace(family, schemas=schemas)
        return replace(catalog, families=families)
    if mutation == "missing-cell":
        families["Q"] = replace(family, cells=family.cells[:-1])
        return replace(catalog, families=families)
    if mutation == "replaced-cell":
        cells = list(family.cells)
        cells[-1] = replace(
            cells[-1],
            base_values=tuple(value + 1 for value in cells[-1].base_values),
        )
        families["Q"] = replace(family, cells=tuple(cells))
        return replace(catalog, families=families)
    if mutation == "replaced-identity":
        rows = [dict(row) for row in catalog.b_identity_table]
        rows[-1]["token_id"] += "-mutated"
        table = tuple(rows)
        return replace(
            catalog,
            b_identity_table=table,
            b_identity_digest=module._identity_digest(table),
        )
    raise AssertionError(f"unknown catalog mutation: {mutation}")


@pytest.mark.parametrize(
    "entry",
    ("sample-census", "shared", "discover", "family"),
)
@pytest.mark.parametrize(
    "mutation",
    (
        "missing-schema",
        "replaced-schema",
        "missing-cell",
        "replaced-cell",
        "replaced-identity",
    ),
)
def test_task2_fix1_every_entry_rejects_incomplete_or_replaced_full_catalog(
    task2_catalog_fixture,
    task2_singleton_discovery,
    entry,
    mutation,
) -> None:
    module, catalog = task2_catalog_fixture
    mutated = _task2_fix1_mutated_catalog(module, catalog, mutation)
    with pytest.raises(module.CertificateFailure, match="full generation catalog"):
        if entry == "sample-census":
            module.preflight_sample_census(mutated)
        elif entry == "shared":
            next(
                module.iter_shared_records(
                    mutated,
                    scope=module.PREFLIGHT_SCOPE,
                    status=module.PREFLIGHT_STATUS,
                )
            )
        elif entry == "discover":
            module.discover_family_generation(
                mutated,
                "singleton",
                selected_old_indices=(0,),
            )
        else:
            next(
                module.iter_family_records(
                    mutated,
                    task2_singleton_discovery,
                    scope=module.PREFLIGHT_SCOPE,
                    selected_template_schema_indices=(0,),
                )
            )


def test_task2_fix1_production_requires_complete_template_schema_range(
    task2_catalog_fixture,
    task2_singleton_discovery,
) -> None:
    module, catalog = task2_catalog_fixture
    with pytest.raises(
        module.CertificateFailure,
        match="production template schema indices are not complete",
    ):
        next(
            module.iter_family_records(
                catalog,
                task2_singleton_discovery,
                scope=module.PRODUCTION_SCOPE,
                selected_template_schema_indices=(0,),
            )
        )


def test_task2_fix1_six_family_preflight_census_is_catalog_derived(
    task2_catalog_fixture,
    monkeypatch,
) -> None:
    module, catalog = task2_catalog_fixture
    assert module.preflight_sample_census(catalog) == (1_406, 2_716, 228_144)
    selections = dict(module.PREFLIGHT_SELECTED_OLD_INDICES)
    selections["Q"] = selections["Q"][:-1]
    monkeypatch.setattr(module, "PREFLIGHT_SELECTED_OLD_INDICES", selections)
    with pytest.raises(module.CertificateFailure, match="preflight sample census"):
        module.preflight_sample_census(catalog)


def test_task2_fix1_phase_a_derives_tables_without_materializing_rows(
    task2_catalog_fixture,
    monkeypatch,
) -> None:
    module, catalog = task2_catalog_fixture

    def forbidden_tables(*_args, **_kwargs):
        raise AssertionError("Phase A materialized complete row tables")

    monkeypatch.setattr(
        module,
        "_generation_old_and_footprint_rows",
        forbidden_tables,
        raising=False,
    )
    discovery = module.discover_family_generation(
        catalog,
        "singleton",
        selected_old_indices=(0,),
    )
    assert discovery.old_load_count == 1
    assert discovery.footprint_count == 6


def test_task2_fix1_phase_a_runtime_retention_is_per_footprint(
    task2_catalog_fixture,
    monkeypatch,
) -> None:
    module, catalog = task2_catalog_fixture
    original = module.comparison_record
    active_comparisons = 0
    peak_comparisons = 0
    template_scopes = {}

    class TrackedComparison(dict):
        def __init__(self, value):
            nonlocal active_comparisons, peak_comparisons
            super().__init__(value)
            active_comparisons += 1
            peak_comparisons = max(peak_comparisons, active_comparisons)

        def __del__(self):
            nonlocal active_comparisons
            active_comparisons -= 1

    def tracked_comparison(*args, **kwargs):
        templates = args[2]
        scope_id = templates.generation_scope_id
        template_scopes.setdefault(scope_id, weakref.ref(templates))
        return TrackedComparison(original(*args, **kwargs))

    monkeypatch.setattr(module, "comparison_record", tracked_comparison)
    discovery = module.discover_family_generation(
        catalog,
        "singleton",
        selected_old_indices=(0,),
    )
    gc.collect()
    assert peak_comparisons <= 3
    assert len(template_scopes) == discovery.occurrence_loads
    assert all(reference() is None for reference in template_scopes.values())


def test_task2_fix1_phase_b_yields_first_bucket_row_without_buffering_footprint(
    task2_catalog_fixture,
    task2_singleton_discovery,
    monkeypatch,
) -> None:
    module, catalog = task2_catalog_fixture
    original = module.pack_mask
    pack_calls = 0

    def observed_pack(mask):
        nonlocal pack_calls
        pack_calls += 1
        return original(mask)

    monkeypatch.setattr(module, "pack_mask", observed_pack)
    records = module.iter_family_records(
        catalog,
        task2_singleton_discovery,
        scope=module.PREFLIGHT_SCOPE,
        selected_template_schema_indices=(0,),
    )
    first_load = next(record for record in records if record[0] == "load")
    assert first_load[0] == "load"
    assert pack_calls == 1


def test_task2_fix1_template_serialization_does_not_retain_identity_map(
    task2_catalog_fixture,
    monkeypatch,
) -> None:
    module, catalog = task2_catalog_fixture
    item = catalog.families["singleton"]
    original = module.build_template
    live_templates = 0
    peak_templates = 0

    def release_template():
        nonlocal live_templates
        live_templates -= 1

    def tracked_template(*args, **kwargs):
        nonlocal live_templates, peak_templates
        template = original(*args, **kwargs)
        live_templates += 1
        peak_templates = max(peak_templates, live_templates)
        weakref.finalize(template, release_template)
        return template

    monkeypatch.setattr(module, "build_template", tracked_template)
    compact = module._generation_template_catalog(item, (0,))
    gc.collect()
    assert compact["template_count"] == len(item.cells)
    assert peak_templates <= 2
    assert live_templates == 0


def _task2_fix2_projected_index_input(module, family_inputs, *, shared_bytes):
    by_family = {value.family: value for value in family_inputs}
    load_rows = {}
    footprint_sizes = {}
    occurrence_loads = {}
    template_counts = {}
    template_catalogs = {}
    family_record_counts = {}
    family_bytes = {}
    for family_index, family in enumerate(module.FAMILY_ORDER):
        value = by_family[family]
        assert value.full_identity_count % value.full_schema_count == 0
        cell_count = value.full_identity_count // value.full_schema_count
        assert value.full_comparisons % module.TOKEN_COUNT == 0
        occurrences = value.full_comparisons // module.TOKEN_COUNT
        assert occurrences % cell_count == 0
        footprints = occurrences // cell_count
        old_load_count = (
            len(value.selected_old_indices)
            if value.sampled_comparisons == value.full_comparisons
            else 1
        )
        minimum_footprint, larger_footprint_count = divmod(
            footprints, old_load_count
        )
        assert minimum_footprint > 0
        load_rows[family] = old_load_count * cell_count
        footprint_sizes[family] = {}
        if old_load_count > larger_footprint_count:
            footprint_sizes[family][str(minimum_footprint)] = (
                old_load_count - larger_footprint_count
            )
        if larger_footprint_count:
            footprint_sizes[family][str(minimum_footprint + 1)] = (
                larger_footprint_count
            )
        occurrence_loads[family] = occurrences
        template_counts[family] = value.full_identity_count
        witness_count = family_index + 1
        template_catalogs[family] = {
            "format": module.TEMPLATE_CATALOG_FORMAT,
            "typed_encoding": module.TEMPLATE_TYPED_ENCODING,
            "identity_order": "schema-major-cell-minor",
            "schema_count": value.full_schema_count,
            "cell_count": cell_count,
            "template_count": value.full_identity_count,
            "witness_count": witness_count,
            "identity_sha256": "1" * 64,
            "replay_sha256": "2" * 64,
            "catalog_sha256": "3" * 64,
        }
        projected_load_records = (
            value.sampled_load_record_count * value.full_comparisons
            + value.sampled_comparisons
            - 1
        ) // value.sampled_comparisons
        family_record_counts[family] = {
            "family_header": 1,
            "old_load": old_load_count,
            "footprint": footprints,
            "bucket_class": value.projected_bucket_class_count,
            "load": projected_load_records,
            "cell_footer": cell_count,
            "template_header": 1,
            "template_schema": value.full_schema_count,
            "template_cell": cell_count,
            "template_witness": witness_count,
            "template_identity_chunk": (
                value.full_identity_count + module.IDENTITY_CHUNK_SIZE - 1
            )
            // module.IDENTITY_CHUNK_SIZE,
            "template_footer": 1,
            "family_footer": 1,
        }
        projected_load_bytes = (
            value.sampled_load_bucket_bytes * value.full_comparisons
            + value.sampled_comparisons
            - 1
        ) // value.sampled_comparisons
        projected_template_bytes = (
            value.sampled_template_bytes * value.full_identity_count
            + value.sampled_identity_count
            - 1
        ) // value.sampled_identity_count
        family_bytes[family] = (
            value.fixed_family_bytes
            + projected_load_bytes
            + projected_template_bytes
        )
    summary = {
        "load_rows": load_rows,
        "total_load_rows": sum(load_rows.values()),
        "footprint_sizes": footprint_sizes,
        "occurrence_loads": occurrence_loads,
        "total_occurrence_loads": sum(occurrence_loads.values()),
        "b_tokens_per_occurrence": module.TOKEN_COUNT,
        "active_comparisons": sum(occurrence_loads.values()) * module.TOKEN_COUNT,
        "template_counts": template_counts,
        "total_templates": sum(template_counts.values()),
    }
    shared_record_counts = {
        "shared_header": 1,
        "dependency": 2,
        "source_bindings": 1,
        "b_identity": module.TOKEN_COUNT,
        "b_coordinate": module.TOKEN_COUNT,
        "shared_footer": 1,
    }
    shards = [
        {
            "role": "shared",
            "family": None,
            "total_bytes": shared_bytes,
            "record_count": sum(shared_record_counts.values()),
            "record_counts": shared_record_counts,
        }
    ]
    for family in module.FAMILY_ORDER:
        counts = family_record_counts[family]
        shards.append(
            {
                "role": "family",
                "family": family,
                "total_bytes": family_bytes[family],
                "record_count": sum(counts.values()),
                "record_counts": counts,
            }
        )
    return {
        "scope": module.PRODUCTION_SCOPE,
        "status": module.PRODUCTION_STATUS,
        "shared_dependency_count": 2,
        "shards": tuple(shards),
        "emitted_summary": copy.deepcopy(summary),
        "full_summary": summary,
        "template_catalogs": template_catalogs,
    }


def test_task2_fix1_projected_index_oracle_is_constructed_internally() -> None:
    module, family_inputs = _task2_projection_inputs()
    index_input = _task2_fix2_projected_index_input(
        module,
        family_inputs,
        shared_bytes=100,
    )
    family_projections = tuple(
        module._generation_family_projection(value) for value in family_inputs
    )
    oracle = module.build_projected_index_oracle(
        index_input,
        shared_bytes=100,
        families=family_projections,
    )
    assert set(oracle) == set(module.ROOT_INDEX_FIELDS)
    assert oracle["root_sha256"] == "0" * 64
    assert oracle["source_bindings_sha256"] == "0" * 64
    assert oracle["b_identity_digest"] == "0" * 64
    assert all(descriptor["sha256"] == "0" * 64 for descriptor in oracle["shards"])
    assert all(
        descriptor["path"] == f"objects/{'0' * 64}.jsonl"
        for descriptor in oracle["shards"]
    )
    assert all(
        summary[field] == "0" * 64
        for summary in oracle["template_catalogs"].values()
        for field in ("identity_sha256", "replay_sha256", "catalog_sha256")
    )
    expected_bytes = len(module.canonical_json_line(oracle))
    projection = module.project_generation(
        source_catalog_precompute_ns=10,
        shared_ns=20,
        shared_bytes=100,
        projected_index_ns=40,
        projected_index_input=index_input,
        families=family_inputs,
    )
    assert projection.projected_index_bytes == expected_bytes


def test_task2_projection_allows_exact_fully_sampled_comparison_families() -> None:
    module, baseline = _task2_projection_inputs()
    values = tuple(
        replace(value, sampled_comparisons=value.full_comparisons)
        if value.family in {"base", "singleton"}
        else value
        for value in baseline
    )
    projection = module.project_generation(
        source_catalog_precompute_ns=10,
        shared_ns=20,
        shared_bytes=100,
        projected_index_ns=40,
        projected_index_input=_task2_fix2_projected_index_input(
            module,
            values,
            shared_bytes=100,
        ),
        families=values,
    )
    by_family = {value.family: value for value in projection.families}
    for family in ("base", "singleton"):
        assert by_family[family].projected_two_pass_ns == 0
        assert by_family[family].projected_load_bucket_bytes == 0
        assert by_family[family].projected_load_record_count == 1


def test_task2_projection_rejects_incomplete_comparison_range_at_ratio_one() -> None:
    module, baseline = _task2_projection_inputs()
    values = (
        replace(
            baseline[0],
            sampled_comparisons=baseline[0].full_comparisons,
        ),
        *baseline[1:],
    )
    with pytest.raises(module.CertificateFailure, match="old range is incomplete"):
        module.project_generation(
            source_catalog_precompute_ns=10,
            shared_ns=20,
            shared_bytes=100,
            projected_index_ns=40,
            projected_index_input=_task2_fix2_projected_index_input(
                module,
                baseline,
                shared_bytes=100,
            ),
            families=values,
        )


def test_task2_projection_rejects_incomplete_identity_range_at_ratio_one() -> None:
    module, baseline = _task2_projection_inputs()
    values = (
        replace(
            baseline[0],
            sampled_identity_count=baseline[0].full_identity_count,
        ),
        *baseline[1:],
    )
    with pytest.raises(module.CertificateFailure, match="schema range is incomplete"):
        module.project_generation(
            source_catalog_precompute_ns=10,
            shared_ns=20,
            shared_bytes=100,
            projected_index_ns=40,
            projected_index_input=_task2_fix2_projected_index_input(
                module,
                values,
                shared_bytes=100,
            ),
            families=values,
        )


@pytest.mark.parametrize("dimension", ("comparison", "identity"))
def test_task2_projection_requires_global_dynamic_range(dimension) -> None:
    module, baseline = _task2_projection_inputs()
    index_input = _task2_fix2_projected_index_input(
        module,
        baseline,
        shared_bytes=100,
    )
    if dimension == "comparison":
        values = tuple(
            replace(value, sampled_comparisons=value.full_comparisons)
            for value in baseline
        )
    else:
        values = tuple(
            replace(
                value,
                selected_schema_indices=tuple(range(value.full_schema_count)),
                sampled_identity_count=value.full_identity_count,
            )
            for value in baseline
        )
    with pytest.raises(
        module.CertificateFailure,
        match=f"global {dimension} projection lacks dynamic range",
    ):
        module.project_generation(
            source_catalog_precompute_ns=10,
            shared_ns=20,
            shared_bytes=100,
            projected_index_ns=40,
            projected_index_input=index_input,
            families=values,
        )


def test_task2_fix2_projected_index_oracle_binds_derived_digit_widths() -> None:
    module, baseline_inputs = _task2_projection_inputs()
    count_wider_inputs = (
        replace(baseline_inputs[0], sampled_load_record_count=3),
        *baseline_inputs[1:],
    )

    def project(values, shared_bytes):
        return module.project_generation(
            source_catalog_precompute_ns=10,
            shared_ns=20,
            shared_bytes=shared_bytes,
            projected_index_ns=40,
            projected_index_input=_task2_fix2_projected_index_input(
                module,
                values,
                shared_bytes=shared_bytes,
            ),
            families=values,
        )

    baseline = project(baseline_inputs, 99)
    count_wider = project(count_wider_inputs, 99)
    bytes_wider = project(baseline_inputs, 100)
    assert count_wider.projected_index_bytes > baseline.projected_index_bytes
    assert bytes_wider.projected_index_bytes > baseline.projected_index_bytes


@pytest.mark.parametrize("mutation", ("shared-bytes", "family-count"))
def test_task2_fix2_projection_rejects_unbound_descriptor_census(mutation) -> None:
    module, family_inputs = _task2_projection_inputs()
    index_input = _task2_fix2_projected_index_input(
        module,
        family_inputs,
        shared_bytes=100,
    )
    shards = [copy.deepcopy(shard) for shard in index_input["shards"]]
    if mutation == "shared-bytes":
        shards[0]["total_bytes"] = 101
    else:
        shards[1]["record_count"] += 1
        shards[1]["record_counts"]["family_header"] += 1
    index_input = {**index_input, "shards": tuple(shards)}
    with pytest.raises(module.CertificateFailure, match="projected shard"):
        module.project_generation(
            source_catalog_precompute_ns=10,
            shared_ns=20,
            shared_bytes=100,
            projected_index_ns=40,
            projected_index_input=index_input,
            families=family_inputs,
        )


@pytest.mark.parametrize("anchor_index", range(21))
def test_task2_fix1_every_anchor_row_is_targeted(
    task2_catalog_fixture,
    anchor_index,
) -> None:
    module, catalog = task2_catalog_fixture
    source = module.build_source_bindings(catalog)
    rows = source["old"]["anchor_provenance"]
    rows[anchor_index]["id"] = rows[(anchor_index + 1) % len(rows)]["id"]
    _task2_reseal_source_bindings(module, source)
    with pytest.raises(module.CertificateFailure, match="anchor provenance identities repeat"):
        module.validate_source_bindings(source, catalog)


@pytest.mark.parametrize("fiber_index", range(53))
def test_task2_fix1_every_b_fiber_row_is_targeted(
    task2_catalog_fixture,
    fiber_index,
) -> None:
    module, catalog = task2_catalog_fixture
    source = module.build_source_bindings(catalog)
    source["b"]["collision_fibers"][fiber_index]["label_equality_witness"] = {
        "equal": False
    }
    _task2_reseal_source_bindings(module, source)
    with pytest.raises(module.CertificateFailure, match="B label equality witness is missing"):
        module.validate_source_bindings(source, catalog)


@pytest.mark.parametrize("identity_index", range(84))
def test_task2_fix1_every_identity_row_is_targeted(
    task2_catalog_fixture,
    identity_index,
) -> None:
    module, catalog = task2_catalog_fixture
    rows = [dict(row) for row in catalog.b_identity_table]
    rows[identity_index]["token_id"] += "-mutated"
    table = tuple(rows)
    mutated = replace(
        catalog,
        b_identity_table=table,
        b_identity_digest=module._identity_digest(table),
    )
    with pytest.raises(module.CertificateFailure, match="full generation catalog"):
        module._validate_generation_identity_coordinates(mutated)


@pytest.mark.parametrize("coordinate_index", range(84))
def test_task2_fix2_every_coordinate_row_reaches_fixed_coordinate_binding(
    task2_catalog_fixture,
    coordinate_index,
) -> None:
    module, catalog = task2_catalog_fixture
    assert module._identity_digest(catalog.b_identity_table) == (
        module.FULL_GENERATION_B_IDENTITY_SHA256
    )
    item = catalog.families["fixed"]
    coordinates = tuple(
        (
            token.token_index,
            token.family,
            (token.slot, *token.source_members),
        )
        for token in item.b_tokens
    )
    mutated = list(coordinates)
    row = mutated[coordinate_index]
    mutated[coordinate_index] = (
        row[0],
        row[1],
        (*row[2], "mutated"),
    )
    mutated_table = tuple(mutated)
    mutable_digest = module.typed_sha256(mutated_table)
    with pytest.raises(
        module.CertificateFailure,
        match="fixed generation B coordinate binding differs",
    ):
        module._validate_generation_coordinate_table(
            mutated_table,
            mutable_digest,
        )


TASK3_FAMILY_ORDER = ("fixed", "base", "singleton", "P", "C", "Q")
TASK3_GLOBAL_CHARGE_DOMAINS = (
    "root-index-descriptor-authentication",
    "shared-wire-stream-read-hash",
    "shared-source-reference-validation",
    "logical-v1-framing-finalization",
)
TASK3_FAMILY_CHARGE_DOMAINS = (
    "family-wire-stream-read-hash",
    "comparison-replay",
    "template-replay",
    "logical-v1-canonical-fragment",
    "reference-validation",
)
TASK3_SELECTED_OLD_INDICES = {
    "fixed": (0, 8, 15, 23, 31, 38, 46, 54, 61, 69),
    "base": (0, 1),
    "singleton": (0,),
    "P": (0, 3, 5, 8, 10, 13, 16, 18, 21, 23, 26, 28, 31),
    "C": (0, 19, 38),
    "Q": (0, 15, 30, 46, 61, 76, 91),
}
TASK3_FAMILY_CENSUS = {
    "fixed": (70, 192, 16, 3_072, 94_080, 13_440),
    "base": (2, 128, 16, 2_048, 5_376, 5_376),
    "singleton": (1, 129, 16, 2_064, 8_064, 8_064),
    "P": (32, 218, 54, 11_772, 290_304, 117_936),
    "C": (39, 239, 16, 3_824, 104_832, 8_064),
    "Q": (92, 398, 64, 25_472, 989_184, 75_264),
}
TASK3_EXPECTED_GLOBAL_PROJECTED_NS = (20, 22, 24, 26)
TASK3_EXPECTED_FAMILY_PROJECTED_NS = {
    "fixed": (40, 210, 320, 150, 120),
    "base": (42, 31, 328, 153, 122),
    "singleton": (44, 32, 319, 156, 124),
    "P": (46, 82, 335, 159, 126),
    "C": (48, 442, 351, 162, 128),
    "Q": (50, 460, 359, 165, 130),
}
TASK3_GENERATION_TOP_FIELDS = (
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
TASK3_GENERATION_FAMILY_FIELDS = (
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
TASK3_GENERATION_CENSUS = {
    "fixed": (192, 16, 3_072, 1_120, 160, 1_120, 160, 94_080, 13_440),
    "base": (128, 16, 2_048, 32, 32, 64, 64, 5_376, 5_376),
    "singleton": (129, 16, 2_064, 16, 16, 96, 96, 8_064, 8_064),
    "P": (218, 54, 11_772, 1_728, 702, 3_456, 1_404, 290_304, 117_936),
    "C": (239, 16, 3_824, 624, 48, 1_248, 96, 104_832, 8_064),
    "Q": (398, 64, 25_472, 5_888, 448, 11_776, 896, 989_184, 75_264),
}
TASK3_GENERATION_TIE_INDICES = {
    "fixed": (5, 191),
    "base": (7, 127),
    "singleton": (3, 128),
    "P": (9, 217),
    "C": (11, 238),
    "Q": (13, 397),
}
TASK3_GENERATION_SELECTED_SCHEMA_INDICES = {
    "fixed": (
        0, 5, 8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104,
        112, 120, 128, 136, 144, 152, 160, 168, 176, 184, 191,
    ),
    "base": (
        0, 7, 8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104,
        112, 120, 127,
    ),
    "singleton": (
        0, 3, 8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104,
        112, 120, 128,
    ),
    "P": (
        0, 8, 9, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104,
        112, 120, 128, 136, 144, 152, 160, 168, 176, 184, 192, 200,
        208, 216, 217,
    ),
    "C": (
        0, 8, 11, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104,
        112, 120, 128, 136, 144, 152, 160, 168, 176, 184, 192, 200,
        208, 216, 224, 232, 238,
    ),
    "Q": (
        0, 8, 13, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104,
        112, 120, 128, 136, 144, 152, 160, 168, 176, 184, 192, 200,
        208, 216, 224, 232, 240, 248, 256, 264, 272, 280, 288, 296,
        304, 312, 320, 328, 336, 344, 352, 360, 368, 376, 384, 392,
        397,
    ),
}
TASK3_GENERATION_BUCKET_COUNTS = {
    "fixed": 17,
    "base": 19,
    "singleton": 23,
    "P": 29,
    "C": 31,
    "Q": 37,
}
TASK3_GENERATION_WITNESS_COUNTS = {
    "fixed": 2,
    "base": 3,
    "singleton": 5,
    "P": 7,
    "C": 11,
    "Q": 13,
}


TASK3_RECORD_FIELDS = {
    "EngineeringVerificationFailure": ("stage", "detail"),
    "ProofAttemptFailure": ("stage", "detail"),
    "VerificationChargeInput": (
        "domain",
        "sampled_ns",
        "full_record_count",
        "sampled_record_count",
    ),
    "VerificationChargeProjection": (
        "domain",
        "sampled_ns",
        "full_record_count",
        "sampled_record_count",
        "projected_ns",
    ),
    "FamilyVerificationProjectionInput": (
        "family",
        "selected_old_indices",
        "selected_schema_indices",
        "full_old_load_count",
        "full_schema_count",
        "charges",
        "invariant_family_ns",
    ),
    "FamilyVerificationProjection": (
        "family",
        "selected_old_indices",
        "selected_schema_indices",
        "full_old_load_count",
        "full_schema_count",
        "charges",
        "invariant_family_ns",
        "verification_ns_before_margin",
    ),
    "VerificationProjection": (
        "format",
        "family_order",
        "global_charges",
        "invariant_ns",
        "families",
        "verification_ns_before_margin",
        "projected_verification_ns",
    ),
    "IndependentReplayResult": (
        "run_id",
        "scope",
        "package_status",
        "status",
        "semantic_replay_complete",
        "attestable",
        "index_path",
        "index_sha256",
        "root_sha256",
        "logical_v1_sha256",
        "generation_projection_sha256",
        "verification_projection",
    ),
}


TASK3_PROJECTED_ORACLE_LINE = b"{\"b_identity_digest\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"canonical_encoding\":\"canonical-json-ascii-lines-v1\",\"domain\":\"a=d-1>=0, n>=0; positive chamber d>=1\",\"emitted_summary\":{\"active_comparisons\":1491840,\"b_tokens_per_occurrence\":84,\"footprint_sizes\":{\"C\":{\"2\":39},\"P\":{\"2\":32},\"Q\":{\"2\":92},\"base\":{\"2\":2},\"fixed\":{\"1\":70},\"singleton\":{\"6\":1}},\"load_rows\":{\"C\":624,\"P\":1728,\"Q\":5888,\"base\":32,\"fixed\":1120,\"singleton\":16},\"occurrence_loads\":{\"C\":1248,\"P\":3456,\"Q\":11776,\"base\":64,\"fixed\":1120,\"singleton\":96},\"template_counts\":{\"C\":3824,\"P\":11772,\"Q\":25472,\"base\":2048,\"fixed\":3072,\"singleton\":2064},\"total_load_rows\":9408,\"total_occurrence_loads\":17760,\"total_templates\":48252},\"format\":\"period-two-old-new-cut-package-v2\",\"full_summary\":{\"active_comparisons\":1491840,\"b_tokens_per_occurrence\":84,\"footprint_sizes\":{\"C\":{\"2\":39},\"P\":{\"2\":32},\"Q\":{\"2\":92},\"base\":{\"2\":2},\"fixed\":{\"1\":70},\"singleton\":{\"6\":1}},\"load_rows\":{\"C\":624,\"P\":1728,\"Q\":5888,\"base\":32,\"fixed\":1120,\"singleton\":16},\"occurrence_loads\":{\"C\":1248,\"P\":3456,\"Q\":11776,\"base\":64,\"fixed\":1120,\"singleton\":96},\"template_counts\":{\"C\":3824,\"P\":11772,\"Q\":25472,\"base\":2048,\"fixed\":3072,\"singleton\":2064},\"total_load_rows\":9408,\"total_occurrence_loads\":17760,\"total_templates\":48252},\"logical_v1_format\":\"period-two-old-new-cut-load-v1\",\"mask_encoding\":\"uint84-be11-base64url-nopad-v1\",\"root_sha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"scope\":\"production-full\",\"shard_bytes_total\":3740,\"shard_order\":[\"shared\",\"fixed\",\"base\",\"singleton\",\"P\",\"C\",\"Q\"],\"shards\":[{\"family\":null,\"path\":\"objects/0000000000000000000000000000000000000000000000000000000000000000.jsonl\",\"record_count\":182,\"record_counts\":{\"b_coordinate\":84,\"b_identity\":84,\"dependency\":11,\"shared_footer\":1,\"shared_header\":1,\"source_bindings\":1},\"role\":\"shared\",\"sha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"total_bytes\":107},{\"family\":\"fixed\",\"path\":\"objects/0000000000000000000000000000000000000000000000000000000000000000.jsonl\",\"record_count\":598,\"record_counts\":{\"bucket_class\":17,\"cell_footer\":16,\"family_footer\":1,\"family_header\":1,\"footprint\":70,\"load\":210,\"old_load\":70,\"template_cell\":16,\"template_footer\":1,\"template_header\":1,\"template_identity_chunk\":1,\"template_schema\":192,\"template_witness\":2},\"role\":\"family\",\"sha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"total_bytes\":580},{\"family\":\"base\",\"path\":\"objects/0000000000000000000000000000000000000000000000000000000000000000.jsonl\",\"record_count\":224,\"record_counts\":{\"bucket_class\":19,\"cell_footer\":16,\"family_footer\":1,\"family_header\":1,\"footprint\":4,\"load\":31,\"old_load\":2,\"template_cell\":16,\"template_footer\":1,\"template_header\":1,\"template_identity_chunk\":1,\"template_schema\":128,\"template_witness\":3},\"role\":\"family\",\"sha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"total_bytes\":455},{\"family\":\"singleton\",\"path\":\"objects/0000000000000000000000000000000000000000000000000000000000000000.jsonl\",\"record_count\":233,\"record_counts\":{\"bucket_class\":23,\"cell_footer\":16,\"family_footer\":1,\"family_header\":1,\"footprint\":6,\"load\":32,\"old_load\":1,\"template_cell\":16,\"template_footer\":1,\"template_header\":1,\"template_identity_chunk\":1,\"template_schema\":129,\"template_witness\":5},\"role\":\"family\",\"sha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"total_bytes\":467},{\"family\":\"P\",\"path\":\"objects/0000000000000000000000000000000000000000000000000000000000000000.jsonl\",\"record_count\":547,\"record_counts\":{\"bucket_class\":29,\"cell_footer\":54,\"family_footer\":1,\"family_header\":1,\"footprint\":64,\"load\":82,\"old_load\":32,\"template_cell\":54,\"template_footer\":1,\"template_header\":1,\"template_identity_chunk\":3,\"template_schema\":218,\"template_witness\":7},\"role\":\"family\",\"sha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"total_bytes\":516},{\"family\":\"C\",\"path\":\"objects/0000000000000000000000000000000000000000000000000000000000000000.jsonl\",\"record_count\":877,\"record_counts\":{\"bucket_class\":31,\"cell_footer\":16,\"family_footer\":1,\"family_header\":1,\"footprint\":78,\"load\":442,\"old_load\":39,\"template_cell\":16,\"template_footer\":1,\"template_header\":1,\"template_identity_chunk\":1,\"template_schema\":239,\"template_witness\":11},\"role\":\"family\",\"sha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"total_bytes\":790},{\"family\":\"Q\",\"path\":\"objects/0000000000000000000000000000000000000000000000000000000000000000.jsonl\",\"record_count\":1323,\"record_counts\":{\"bucket_class\":37,\"cell_footer\":64,\"family_footer\":1,\"family_header\":1,\"footprint\":184,\"load\":460,\"old_load\":92,\"template_cell\":64,\"template_footer\":1,\"template_header\":1,\"template_identity_chunk\":7,\"template_schema\":398,\"template_witness\":13},\"role\":\"family\",\"sha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"total_bytes\":825}],\"source_bindings_sha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"status\":\"generated-awaiting-independent-replay\",\"template_catalogs\":{\"C\":{\"catalog_sha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"cell_count\":16,\"format\":\"task4-template-catalog-v2\",\"identity_order\":\"schema-major-cell-minor\",\"identity_sha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"replay_sha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"schema_count\":239,\"template_count\":3824,\"typed_encoding\":\"task4-typed-sha256-v1\",\"witness_count\":11},\"P\":{\"catalog_sha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"cell_count\":54,\"format\":\"task4-template-catalog-v2\",\"identity_order\":\"schema-major-cell-minor\",\"identity_sha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"replay_sha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"schema_count\":218,\"template_count\":11772,\"typed_encoding\":\"task4-typed-sha256-v1\",\"witness_count\":7},\"Q\":{\"catalog_sha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"cell_count\":64,\"format\":\"task4-template-catalog-v2\",\"identity_order\":\"schema-major-cell-minor\",\"identity_sha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"replay_sha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"schema_count\":398,\"template_count\":25472,\"typed_encoding\":\"task4-typed-sha256-v1\",\"witness_count\":13},\"base\":{\"catalog_sha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"cell_count\":16,\"format\":\"task4-template-catalog-v2\",\"identity_order\":\"schema-major-cell-minor\",\"identity_sha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"replay_sha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"schema_count\":128,\"template_count\":2048,\"typed_encoding\":\"task4-typed-sha256-v1\",\"witness_count\":3},\"fixed\":{\"catalog_sha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"cell_count\":16,\"format\":\"task4-template-catalog-v2\",\"identity_order\":\"schema-major-cell-minor\",\"identity_sha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"replay_sha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"schema_count\":192,\"template_count\":3072,\"typed_encoding\":\"task4-typed-sha256-v1\",\"witness_count\":2},\"singleton\":{\"catalog_sha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"cell_count\":16,\"format\":\"task4-template-catalog-v2\",\"identity_order\":\"schema-major-cell-minor\",\"identity_sha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"replay_sha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"schema_count\":129,\"template_count\":2064,\"typed_encoding\":\"task4-typed-sha256-v1\",\"witness_count\":5}}}\n"
TASK3_PROJECTED_ORACLE_LENGTH = 7809
TASK3_BASELINE_GENERATION_PROJECTION = {
    "format": "period-two-old-new-cut-generation-projection-v1",
    "family_order": list(TASK3_FAMILY_ORDER),
    "full_schema_count": 1_304,
    "full_identity_count": 48_252,
    "sampled_source_loads": 1_406,
    "sampled_occurrence_loads": 2_716,
    "sampled_comparisons": 228_144,
    "source_catalog_precompute_ns": 101,
    "shared_ns": 103,
    "shared_bytes": 107,
    "projected_index_ns": 109,
    "projected_index_bytes": 7_809,
    "families": [
        {"family": "fixed", "selected_old_indices": list(TASK3_SELECTED_OLD_INDICES["fixed"]), "selected_schema_indices": list(TASK3_GENERATION_SELECTED_SCHEMA_INDICES["fixed"]), "tied_max_schema_ids": ["fixed-schema-005", "fixed-schema-191"], "full_schema_count": 192, "full_comparisons": 94_080, "sampled_comparisons": 13_440, "sampled_two_pass_ns": 10, "projected_two_pass_ns": 70, "sampled_load_bucket_bytes": 20, "projected_load_bucket_bytes": 140, "sampled_load_record_count": 30, "projected_load_record_count": 210, "projected_bucket_class_count": 17, "full_identity_count": 3_072, "sampled_identity_count": 416, "sampled_template_ns": 40, "projected_template_ns": 296, "sampled_template_bytes": 50, "projected_template_bytes": 370, "fixed_family_ns": 60, "fixed_family_bytes": 70},
        {"family": "base", "selected_old_indices": list(TASK3_SELECTED_OLD_INDICES["base"]), "selected_schema_indices": list(TASK3_GENERATION_SELECTED_SCHEMA_INDICES["base"]), "tied_max_schema_ids": ["base-schema-007", "base-schema-127"], "full_schema_count": 128, "full_comparisons": 5_376, "sampled_comparisons": 5_376, "sampled_two_pass_ns": 11, "projected_two_pass_ns": 11, "sampled_load_bucket_bytes": 21, "projected_load_bucket_bytes": 21, "sampled_load_record_count": 31, "projected_load_record_count": 31, "projected_bucket_class_count": 19, "full_identity_count": 2_048, "sampled_identity_count": 288, "sampled_template_ns": 41, "projected_template_ns": 292, "sampled_template_bytes": 51, "projected_template_bytes": 363, "fixed_family_ns": 61, "fixed_family_bytes": 71},
        {"family": "singleton", "selected_old_indices": list(TASK3_SELECTED_OLD_INDICES["singleton"]), "selected_schema_indices": list(TASK3_GENERATION_SELECTED_SCHEMA_INDICES["singleton"]), "tied_max_schema_ids": ["singleton-schema-003", "singleton-schema-128"], "full_schema_count": 129, "full_comparisons": 8_064, "sampled_comparisons": 8_064, "sampled_two_pass_ns": 12, "projected_two_pass_ns": 12, "sampled_load_bucket_bytes": 22, "projected_load_bucket_bytes": 22, "sampled_load_record_count": 32, "projected_load_record_count": 32, "projected_bucket_class_count": 23, "full_identity_count": 2_064, "sampled_identity_count": 288, "sampled_template_ns": 42, "projected_template_ns": 301, "sampled_template_bytes": 52, "projected_template_bytes": 373, "fixed_family_ns": 62, "fixed_family_bytes": 72},
        {"family": "P", "selected_old_indices": list(TASK3_SELECTED_OLD_INDICES["P"]), "selected_schema_indices": list(TASK3_GENERATION_SELECTED_SCHEMA_INDICES["P"]), "tied_max_schema_ids": ["P-schema-009", "P-schema-217"], "full_schema_count": 218, "full_comparisons": 290_304, "sampled_comparisons": 117_936, "sampled_two_pass_ns": 13, "projected_two_pass_ns": 32, "sampled_load_bucket_bytes": 23, "projected_load_bucket_bytes": 57, "sampled_load_record_count": 33, "projected_load_record_count": 82, "projected_bucket_class_count": 29, "full_identity_count": 11_772, "sampled_identity_count": 1_620, "sampled_template_ns": 43, "projected_template_ns": 313, "sampled_template_bytes": 53, "projected_template_bytes": 386, "fixed_family_ns": 63, "fixed_family_bytes": 73},
        {"family": "C", "selected_old_indices": list(TASK3_SELECTED_OLD_INDICES["C"]), "selected_schema_indices": list(TASK3_GENERATION_SELECTED_SCHEMA_INDICES["C"]), "tied_max_schema_ids": ["C-schema-011", "C-schema-238"], "full_schema_count": 239, "full_comparisons": 104_832, "sampled_comparisons": 8_064, "sampled_two_pass_ns": 14, "projected_two_pass_ns": 182, "sampled_load_bucket_bytes": 24, "projected_load_bucket_bytes": 312, "sampled_load_record_count": 34, "projected_load_record_count": 442, "projected_bucket_class_count": 31, "full_identity_count": 3_824, "sampled_identity_count": 512, "sampled_template_ns": 44, "projected_template_ns": 329, "sampled_template_bytes": 54, "projected_template_bytes": 404, "fixed_family_ns": 64, "fixed_family_bytes": 74},
        {"family": "Q", "selected_old_indices": list(TASK3_SELECTED_OLD_INDICES["Q"]), "selected_schema_indices": list(TASK3_GENERATION_SELECTED_SCHEMA_INDICES["Q"]), "tied_max_schema_ids": ["Q-schema-013", "Q-schema-397"], "full_schema_count": 398, "full_comparisons": 989_184, "sampled_comparisons": 75_264, "sampled_two_pass_ns": 15, "projected_two_pass_ns": 198, "sampled_load_bucket_bytes": 25, "projected_load_bucket_bytes": 329, "sampled_load_record_count": 35, "projected_load_record_count": 460, "projected_bucket_class_count": 37, "full_identity_count": 25_472, "sampled_identity_count": 3_328, "sampled_template_ns": 45, "projected_template_ns": 345, "sampled_template_bytes": 55, "projected_template_bytes": 421, "fixed_family_ns": 65, "fixed_family_bytes": 75},
    ],
    "generation_ns_before_margin": 3_069,
    "package_bytes_before_margin": 11_549,
    "projected_generation_ns": 6_138,
    "projected_package_bytes": 23_098,
}


def _task3_generation_premises(module):
    profiles = {}
    for family in TASK3_FAMILY_ORDER:
        count = TASK3_GENERATION_CENSUS[family][0]
        ties = set(TASK3_GENERATION_TIE_INDICES[family])
        profiles[family] = tuple(
            (f"{family}-schema-{index:03d}", 2 if index in ties else 1)
            for index in range(count)
        )
    return module._GenerationProjectionPremises(
        domain="a=d-1>=0, n>=0; positive chamber d>=1",
        shared_dependency_count=11,
        schema_profiles=profiles,
        bucket_class_counts=dict(TASK3_GENERATION_BUCKET_COUNTS),
        family_witness_counts=dict(TASK3_GENERATION_WITNESS_COUNTS),
    )


def _task3_generation_fixture(module):
    return copy.deepcopy(TASK3_BASELINE_GENERATION_PROJECTION), _task3_generation_premises(module)


def test_task3_generation_projection_schema_and_canonical_binding_are_exact() -> None:
    module = load_package_v2_verifier()
    projection, premises = _task3_generation_fixture(module)
    assert set(projection) == set(TASK3_GENERATION_TOP_FIELDS)
    assert all(set(family) == set(TASK3_GENERATION_FAMILY_FIELDS) for family in projection["families"])
    assert tuple(field.name for field in fields(module._GenerationProjectionPremises)) == (
        "domain", "shared_dependency_count", "schema_profiles",
        "bucket_class_counts", "family_witness_counts",
    )
    binding = module._validate_generation_projection(projection, premises)
    expected_json = json.dumps(projection, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
    assert binding.normalized == expected_json
    assert binding.sha256 == hashlib.sha256(expected_json.encode("ascii")).hexdigest()
    assert tuple(field.name for field in fields(binding)) == ("normalized", "sha256")
    root = module._generation_projected_root_oracle(premises, projection, projection["families"])
    assert len(TASK3_PROJECTED_ORACLE_LINE) == TASK3_PROJECTED_ORACLE_LENGTH
    assert module._generation_projected_index_line(root) == TASK3_PROJECTED_ORACLE_LINE
    assert projection["projected_index_bytes"] == TASK3_PROJECTED_ORACLE_LENGTH
    with pytest.raises(AttributeError):
        binding.sha256 = "0" * 64
    assert not hasattr(binding, "attestable")


def test_task3_generation_projection_rejects_exact_recursive_types_and_premise_order() -> None:
    module = load_package_v2_verifier()
    projection, premises = _task3_generation_fixture(module)

    class HostileString(str):
        def __eq__(self, _other):
            return True
        __hash__ = str.__hash__

    bad_projection = copy.deepcopy(projection)
    bad_projection["format"] = HostileString(projection["format"])
    with pytest.raises(module.EngineeringVerificationFailure, match="exact ASCII string"):
        module._validate_generation_projection(bad_projection, premises)
    bad_family = copy.deepcopy(projection)
    bad_family["families"][0]["family"] = HostileString("fixed")
    with pytest.raises(module.EngineeringVerificationFailure, match="exact ASCII string"):
        module._validate_generation_projection(bad_family, premises)
    bad_domain = replace(premises, domain=HostileString(premises.domain))
    with pytest.raises(module.EngineeringVerificationFailure, match="exact ASCII string"):
        module._validate_generation_projection(projection, bad_domain)
    bad_profile = dict(premises.schema_profiles)
    bad_profile["fixed"] = tuple(reversed(bad_profile["fixed"]))
    with pytest.raises(module.EngineeringVerificationFailure, match="schema profile order differs"):
        module._validate_generation_projection(projection, replace(premises, schema_profiles=bad_profile))
    bad_bucket = dict(premises.bucket_class_counts)
    bad_bucket["fixed"] = True
    with pytest.raises(module.EngineeringVerificationFailure, match="exact positive integer"):
        module._validate_generation_projection(projection, replace(premises, bucket_class_counts=bad_bucket))


def test_task3_generation_projection_literals_cover_selections_censuses_and_gates() -> None:
    module = load_package_v2_verifier()
    projection, premises = _task3_generation_fixture(module)
    for family_index, family in enumerate(TASK3_FAMILY_ORDER):
        bad = copy.deepcopy(projection)
        selected_old = bad["families"][family_index]["selected_old_indices"]
        if family == "base":
            selected_old.pop()
            expected_old_gate = "selected old indices differ"
        elif family == "singleton":
            selected_old.clear()
            expected_old_gate = "not a strict valid range"
        else:
            selected_old[0] += 1
            expected_old_gate = "selected old indices differ"
        with pytest.raises(
            module.EngineeringVerificationFailure,
            match=expected_old_gate,
        ):
            module._validate_generation_projection(bad, premises)
        bad = copy.deepcopy(projection)
        bad["families"][family_index]["selected_schema_indices"].pop()
        with pytest.raises(module.EngineeringVerificationFailure, match="selected schema indices differ"):
            module._validate_generation_projection(bad, premises)
        bad = copy.deepcopy(projection)
        bad["families"][family_index]["tied_max_schema_ids"].pop()
        with pytest.raises(module.EngineeringVerificationFailure, match="tied maximum schema IDs differ"):
            module._validate_generation_projection(bad, premises)
        for field in ("full_schema_count", "full_comparisons", "sampled_comparisons", "full_identity_count", "sampled_identity_count"):
            bad = copy.deepcopy(projection)
            bad["families"][family_index][field] += 1
            with pytest.raises(module.EngineeringVerificationFailure, match="denominator census differs"):
                module._validate_generation_projection(bad, premises)
    for field in ("full_schema_count", "full_identity_count", "sampled_source_loads", "sampled_occurrence_loads", "sampled_comparisons"):
        bad = copy.deepcopy(projection)
        bad[field] += 1
        with pytest.raises(module.EngineeringVerificationFailure, match="top generation census differs"):
            module._validate_generation_projection(bad, premises)


def test_task3_generation_projection_accepts_equal_width_premise_and_projection_deltas() -> None:
    module = load_package_v2_verifier()
    projection, premises = _task3_generation_fixture(module)
    baseline_oracle = module._generation_projected_root_oracle(
        premises, projection, projection["families"]
    )
    baseline_line = module._generation_projected_index_line(baseline_oracle)
    assert len(baseline_line) == TASK3_PROJECTED_ORACLE_LENGTH
    baseline_shared = baseline_oracle["shards"][0]
    dependency = replace(
        premises,
        shared_dependency_count=premises.shared_dependency_count + 1,
    )
    dependency_oracle = module._generation_projected_root_oracle(
        dependency, projection, projection["families"]
    )
    dependency_shared = dependency_oracle["shards"][0]
    assert dependency_shared["record_counts"]["dependency"] == (
        baseline_shared["record_counts"]["dependency"] + 1
    )
    assert dependency_shared["record_count"] == (
        baseline_shared["record_count"] + 1
    )
    for tag in (
        "shared_header",
        "source_bindings",
        "b_identity",
        "b_coordinate",
        "shared_footer",
    ):
        assert dependency_shared["record_counts"][tag] == (
            baseline_shared["record_counts"][tag]
        )
    assert len(module._generation_projected_index_line(dependency_oracle)) == (
        TASK3_PROJECTED_ORACLE_LENGTH
    )
    module._validate_generation_projection(projection, dependency)
    for family in TASK3_FAMILY_ORDER:
        witnesses = dict(premises.family_witness_counts)
        witnesses[family] += 1
        witness_premises = replace(
            premises, family_witness_counts=witnesses
        )
        witness_oracle = module._generation_projected_root_oracle(
            witness_premises, projection, projection["families"]
        )
        descriptor_index = TASK3_FAMILY_ORDER.index(family) + 1
        baseline_descriptor = baseline_oracle["shards"][descriptor_index]
        witness_descriptor = witness_oracle["shards"][descriptor_index]
        assert witness_oracle["template_catalogs"][family]["witness_count"] == (
            baseline_oracle["template_catalogs"][family]["witness_count"]
            + 1
        )
        assert witness_descriptor["record_counts"]["template_witness"] == (
            baseline_descriptor["record_counts"]["template_witness"] + 1
        )
        assert witness_descriptor["record_count"] == (
            baseline_descriptor["record_count"] + 1
        )
        for other_family in TASK3_FAMILY_ORDER:
            expected_witness_count = baseline_oracle["template_catalogs"][
                other_family
            ]["witness_count"]
            expected_descriptor_count = baseline_oracle["shards"][
                TASK3_FAMILY_ORDER.index(other_family) + 1
            ]["record_counts"]["template_witness"]
            if other_family != family:
                assert witness_oracle["template_catalogs"][other_family][
                    "witness_count"
                ] == expected_witness_count
                assert witness_oracle["shards"][
                    TASK3_FAMILY_ORDER.index(other_family) + 1
                ]["record_counts"]["template_witness"] == expected_descriptor_count
        assert len(module._generation_projected_index_line(witness_oracle)) == (
            TASK3_PROJECTED_ORACLE_LENGTH
        )
        module._validate_generation_projection(projection, witness_premises)
    domain_premises = replace(
        premises, domain=premises.domain.replace("d-1", "e-1")
    )
    domain_oracle = module._generation_projected_root_oracle(
        domain_premises, projection, projection["families"]
    )
    assert domain_oracle["domain"] == domain_premises.domain
    assert domain_oracle["domain"] != baseline_oracle["domain"]
    assert len(module._generation_projected_index_line(domain_oracle)) == (
        TASK3_PROJECTED_ORACLE_LENGTH
    )
    module._validate_generation_projection(projection, domain_premises)
    longer_domain_premises = replace(premises, domain=premises.domain + "x")
    longer_domain_oracle = module._generation_projected_root_oracle(
        longer_domain_premises, projection, projection["families"]
    )
    assert len(module._generation_projected_index_line(longer_domain_oracle)) == (
        TASK3_PROJECTED_ORACLE_LENGTH + 1
    )
    longer_domain_projection = copy.deepcopy(projection)
    longer_domain_projection["projected_index_bytes"] += 1
    longer_domain_projection["package_bytes_before_margin"] += 1
    longer_domain_projection["projected_package_bytes"] += 2
    module._validate_generation_projection(
        longer_domain_projection, longer_domain_premises
    )
    shared = copy.deepcopy(projection)
    shared["shared_bytes"] += 1
    shared["package_bytes_before_margin"] += 1
    shared["projected_package_bytes"] += 2
    module._validate_generation_projection(shared, premises)
    family_bytes = copy.deepcopy(projection)
    family_bytes["families"][0]["fixed_family_bytes"] += 1
    family_bytes["package_bytes_before_margin"] += 1
    family_bytes["projected_package_bytes"] += 2
    module._validate_generation_projection(family_bytes, premises)
    bucket_counts = dict(premises.bucket_class_counts)
    bucket_counts["fixed"] += 1
    bucket = copy.deepcopy(projection)
    bucket["families"][0]["projected_bucket_class_count"] += 1
    module._validate_generation_projection(bucket, replace(premises, bucket_class_counts=bucket_counts))
    load = copy.deepcopy(projection)
    load["families"][1]["sampled_load_record_count"] += 1
    load["families"][1]["projected_load_record_count"] += 1
    module._validate_generation_projection(load, premises)


def test_task3_generation_projection_rejects_one_stale_redundant_field_at_named_gate() -> None:
    module = load_package_v2_verifier()
    projection, premises = _task3_generation_fixture(module)
    stale_shared = copy.deepcopy(projection)
    stale_shared["shared_bytes"] += 1
    with pytest.raises(module.EngineeringVerificationFailure, match="derived generation totals differ"):
        module._validate_generation_projection(stale_shared, premises)
    bucket_counts = dict(premises.bucket_class_counts)
    bucket_counts["fixed"] += 1
    with pytest.raises(module.EngineeringVerificationFailure, match="derived generation projection differs"):
        module._validate_generation_projection(projection, replace(premises, bucket_class_counts=bucket_counts))
    stale_load = copy.deepcopy(projection)
    stale_load["families"][1]["sampled_load_record_count"] += 1
    with pytest.raises(module.EngineeringVerificationFailure, match="derived generation projection differs"):
        module._validate_generation_projection(stale_load, premises)
    longer_domain = replace(premises, domain=premises.domain + "x")
    with pytest.raises(module.EngineeringVerificationFailure, match="projected index byte cost differs"):
        module._validate_generation_projection(projection, longer_domain)


def _task3_verification_inputs(module):
    global_charges = tuple(
        module.VerificationChargeInput(
            domain=domain,
            sampled_ns=10 + index,
            full_record_count=10 + 2 * index,
            sampled_record_count=5 + index,
        )
        for index, domain in enumerate(TASK3_GLOBAL_CHARGE_DOMAINS)
    )
    families = []
    for family_index, family in enumerate(TASK3_FAMILY_ORDER):
        (
            full_old_load_count,
            full_schema_count,
            cell_count,
            full_identity_count,
            full_comparisons,
            sampled_comparisons,
        ) = TASK3_FAMILY_CENSUS[family]
        schema_indices = tuple(range(0, full_schema_count, 8))
        sampled_ns_by_domain = {
            "family-wire-stream-read-hash": 20 + family_index,
            "comparison-replay": 30 + family_index,
            "template-replay": 40 + family_index,
            "logical-v1-canonical-fragment": 50 + family_index,
            "reference-validation": 60 + family_index,
        }
        charges = []
        for domain in TASK3_FAMILY_CHARGE_DOMAINS:
            full_count = 10
            sampled_count = 5
            if domain == "comparison-replay":
                full_count = full_comparisons
                sampled_count = sampled_comparisons
            elif domain == "template-replay":
                full_count = full_identity_count
                sampled_count = len(schema_indices) * cell_count
            elif domain == "logical-v1-canonical-fragment":
                full_count = 9
                sampled_count = 3
            elif domain == "reference-validation":
                full_count = 8
                sampled_count = 4
            charges.append(
                module.VerificationChargeInput(
                    domain=domain,
                    sampled_ns=sampled_ns_by_domain[domain],
                    full_record_count=full_count,
                    sampled_record_count=sampled_count,
                )
            )
        families.append(
            module.FamilyVerificationProjectionInput(
                family=family,
                selected_old_indices=TASK3_SELECTED_OLD_INDICES[family],
                selected_schema_indices=schema_indices,
                full_old_load_count=full_old_load_count,
                full_schema_count=full_schema_count,
                charges=tuple(charges),
                invariant_family_ns=0,
            )
        )
    return global_charges, tuple(families)


def test_task3_api_records_and_python39_signatures_are_exact() -> None:
    module = load_package_v2_verifier()
    assert module.FAMILY_ORDER == TASK3_FAMILY_ORDER
    assert (
        module.GLOBAL_VERIFICATION_CHARGE_DOMAINS
        == TASK3_GLOBAL_CHARGE_DOMAINS
    )
    assert (
        module.FAMILY_VERIFICATION_CHARGE_DOMAINS
        == TASK3_FAMILY_CHARGE_DOMAINS
    )
    for name, expected_fields in TASK3_RECORD_FIELDS.items():
        record_type = getattr(module, name)
        assert tuple(field.name for field in fields(record_type)) == expected_fields
        assert record_type.__dataclass_params__.frozen is True

    failure = module.EngineeringVerificationFailure("stage", "detail")
    with pytest.raises(AttributeError):
        failure.stage = "mutated"

    verify = inspect.signature(module.verify_v2_package)
    assert tuple(verify.parameters) == (
        "index_path",
        "run_id",
        "generation_projection",
        "metrics",
    )
    assert verify.parameters["index_path"].default is inspect.Parameter.empty
    assert verify.parameters["run_id"].default is inspect.Parameter.empty
    assert (
        verify.parameters["generation_projection"].default
        is inspect.Parameter.empty
    )
    assert verify.parameters["metrics"].kind is inspect.Parameter.KEYWORD_ONLY
    assert verify.parameters["metrics"].default is None

    projection = inspect.signature(module.project_verification)
    assert tuple(projection.parameters) == (
        "global_charges",
        "invariant_ns",
        "families",
    )
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in projection.parameters.values()
    )
    attestation = inspect.signature(module.build_attestation_payload)
    assert tuple(attestation.parameters) == (
        "result",
        "verifier_sha256",
        "metrics",
    )
    metrics = inspect.signature(module.PhaseMetrics)
    assert tuple(metrics.parameters) == ("enabled",)
    assert metrics.parameters["enabled"].kind is inspect.Parameter.KEYWORD_ONLY
    assert metrics.parameters["enabled"].default is False


def test_task3_verification_projection_scales_every_record_domain_and_margin() -> None:
    module = load_package_v2_verifier()
    global_charges, families = _task3_verification_inputs(module)
    projection = module.project_verification(
        global_charges=global_charges,
        invariant_ns=0,
        families=families,
    )
    assert projection.format == (
        "period-two-old-new-cut-verification-projection-v1"
    )
    assert projection.family_order == TASK3_FAMILY_ORDER
    assert tuple(
        charge.domain for charge in projection.global_charges
    ) == TASK3_GLOBAL_CHARGE_DOMAINS
    assert tuple(
        charge.projected_ns for charge in projection.global_charges
    ) == TASK3_EXPECTED_GLOBAL_PROJECTED_NS
    for family in projection.families:
        expected = TASK3_EXPECTED_FAMILY_PROJECTED_NS[family.family]
        assert tuple(
            charge.domain for charge in family.charges
        ) == TASK3_FAMILY_CHARGE_DOMAINS
        assert tuple(charge.projected_ns for charge in family.charges) == expected
        assert family.invariant_family_ns == 0
        assert family.verification_ns_before_margin == sum(expected)
    for family in projection.families[1:3]:
        comparison = family.charges[1]
        assert comparison.domain == "comparison-replay"
        assert comparison.sampled_record_count == comparison.full_record_count
        assert comparison.projected_ns == comparison.sampled_ns
    assert tuple(
        family.verification_ns_before_margin
        for family in projection.families
    ) == (840, 676, 675, 748, 1_131, 1_164)
    assert projection.invariant_ns == 0
    assert projection.verification_ns_before_margin == 5_326
    assert projection.projected_verification_ns == 10_652
    assert sum(
        charge.projected_ns for charge in projection.global_charges
    ) == 92
    assert sum(
        family.verification_ns_before_margin
        for family in projection.families
    ) == 5_234
    assert projection.verification_ns_before_margin == (
        sum(charge.projected_ns for charge in projection.global_charges)
        + sum(
            family.verification_ns_before_margin
            for family in projection.families
        )
    )


def _task3_replace_family_charge(family, domain, **changes):
    return replace(
        family,
        charges=tuple(
            replace(charge, **changes) if charge.domain == domain else charge
            for charge in family.charges
        ),
    )


def test_task3_verification_projection_rejects_invalid_family_inputs() -> None:
    module = load_package_v2_verifier()
    global_charges, families = _task3_verification_inputs(module)

    invalid_global_charges = (
        (replace(global_charges[0], sampled_ns=True), *global_charges[1:]),
        (replace(global_charges[0], full_record_count=1.0), *global_charges[1:]),
        (replace(global_charges[0], sampled_record_count=0), *global_charges[1:]),
        (replace(global_charges[0], sampled_record_count=11), *global_charges[1:]),
        (
            SimpleNamespace(
                domain=TASK3_GLOBAL_CHARGE_DOMAINS[0],
                sampled_ns=10,
                full_record_count=10,
                sampled_record_count=5,
            ),
            *global_charges[1:],
        ),
        global_charges[:-1],
        (global_charges[0], global_charges[0], *global_charges[2:]),
    )
    for invalid_global in invalid_global_charges:
        with pytest.raises(module.EngineeringVerificationFailure):
            module.project_verification(
                global_charges=invalid_global,
                invariant_ns=0,
                families=families,
            )

    for invalid_invariant in (-1, 1, True, 1.0):
        with pytest.raises(module.EngineeringVerificationFailure):
            module.project_verification(
                global_charges=global_charges,
                invariant_ns=invalid_invariant,
                families=families,
            )

    repeated_families = (families[0], families[0], *families[2:])
    with pytest.raises(module.EngineeringVerificationFailure):
        module.project_verification(
            global_charges=global_charges,
            invariant_ns=0,
            families=repeated_families,
        )

    wrong_family_type = (SimpleNamespace(family="fixed"), *families[1:])
    with pytest.raises(module.EngineeringVerificationFailure):
        module.project_verification(
            global_charges=global_charges,
            invariant_ns=0,
            families=wrong_family_type,
        )

    nonzero_family_invariant = (
        replace(families[0], invariant_family_ns=1),
        *families[1:],
    )
    with pytest.raises(module.EngineeringVerificationFailure):
        module.project_verification(
            global_charges=global_charges,
            invariant_ns=0,
            families=nonzero_family_invariant,
        )

    invalid_family_values = (
        replace(families[0], full_old_load_count=True),
        replace(families[0], full_schema_count=0),
        replace(families[0], selected_old_indices=(0, 0)),
        replace(families[0], selected_old_indices=(True,)),
        replace(families[0], selected_schema_indices=(0, 0)),
        replace(families[0], selected_schema_indices=(192,)),
        replace(
            families[0],
            charges=(families[0].charges[0], *families[0].charges[:-1]),
        ),
    )
    for invalid_family in invalid_family_values:
        with pytest.raises(module.EngineeringVerificationFailure):
            module.project_verification(
                global_charges=global_charges,
                invariant_ns=0,
                families=(invalid_family, *families[1:]),
            )

    comparison_ratio_one_on_incomplete_range = _task3_replace_family_charge(
        families[0],
        "comparison-replay",
        sampled_record_count=94_080,
    )
    comparison_strict_on_complete_range = replace(
        families[0], selected_old_indices=tuple(range(70))
    )
    identity_ratio_one_on_incomplete_range = _task3_replace_family_charge(
        families[0],
        "template-replay",
        sampled_record_count=3_072,
    )
    identity_strict_on_complete_range = replace(
        families[0], selected_schema_indices=tuple(range(192))
    )
    for invalid_family in (
        comparison_ratio_one_on_incomplete_range,
        comparison_strict_on_complete_range,
        identity_ratio_one_on_incomplete_range,
        identity_strict_on_complete_range,
    ):
        with pytest.raises(module.EngineeringVerificationFailure):
            module.project_verification(
                global_charges=global_charges,
                invariant_ns=0,
                families=(invalid_family, *families[1:]),
            )

    all_comparisons_ratio_one = tuple(
        _task3_replace_family_charge(
            replace(
                family,
                selected_old_indices=tuple(range(family.full_old_load_count)),
            ),
            "comparison-replay",
            sampled_record_count=next(
                charge.full_record_count
                for charge in family.charges
                if charge.domain == "comparison-replay"
            ),
        )
        for family in families
    )
    with pytest.raises(module.EngineeringVerificationFailure):
        module.project_verification(
            global_charges=global_charges,
            invariant_ns=0,
            families=all_comparisons_ratio_one,
        )

    all_identities_ratio_one = tuple(
        _task3_replace_family_charge(
            replace(
                family,
                selected_schema_indices=tuple(range(family.full_schema_count)),
            ),
            "template-replay",
            sampled_record_count=next(
                charge.full_record_count
                for charge in family.charges
                if charge.domain == "template-replay"
            ),
        )
        for family in families
    )
    with pytest.raises(module.EngineeringVerificationFailure):
        module.project_verification(
            global_charges=global_charges,
            invariant_ns=0,
            families=all_identities_ratio_one,
        )


def test_task3_verification_projection_has_no_bytes_or_generation_restatement() -> None:
    module = load_package_v2_verifier()
    global_charges, families = _task3_verification_inputs(module)
    projection = module.project_verification(
        global_charges=global_charges,
        invariant_ns=0,
        families=families,
    )
    field_names = {
        field.name for record in (projection, *projection.families)
        for field in fields(record)
    }
    assert not any("byte" in name for name in field_names)
    assert not any("generation" in name for name in field_names)
    assert not any("package" in name for name in field_names)
    assert all(
        charge.domain
        in {
            *TASK3_GLOBAL_CHARGE_DOMAINS,
            *TASK3_FAMILY_CHARGE_DOMAINS,
        }
        for charge in (
            *projection.global_charges,
            *(
                charge
                for family in projection.families
                for charge in family.charges
            ),
        )
    )


def test_task3_direct_verification_projection_is_pure_arithmetic_and_non_attestable() -> None:
    module = load_package_v2_verifier()
    global_charges, families = _task3_verification_inputs(module)
    projection = module.project_verification(
        global_charges=global_charges,
        invariant_ns=0,
        families=families,
    )
    assert projection == module.project_verification(
        global_charges=global_charges,
        invariant_ns=0,
        families=families,
    )
    assert isinstance(projection, module.VerificationProjection)
    assert not {"attestable", "status", "run_id"} & {
        field.name for field in fields(projection)
    }
    attestation_signature = inspect.signature(module.build_attestation_payload)
    assert (
        attestation_signature.parameters["result"].annotation
        == "IndependentReplayResult"
    )
    verify_signature = inspect.signature(module.verify_v2_package)
    assert all(
        parameter.annotation != "VerificationProjection"
        for parameter in verify_signature.parameters.values()
    )
    with pytest.raises(
        module.EngineeringVerificationFailure,
        match="arithmetic only and non-attestable",
    ):
        module.build_attestation_payload(
            projection,
            "0" * 64,
            {},
        )
