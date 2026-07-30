import copy
import functools
import hashlib
import importlib.util
import io
import json
import operator
import re
import sys
from dataclasses import replace
from pathlib import Path

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
    with pytest.raises(module.WireFormatError):
        module.decode_family_records(
            io.BytesIO(payload),
            expected_family="fixed",
            scope="production-full",
        )


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
    assert verifier.verify_v2_package(index_path) == (
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
    assert verifier.verify_v2_package(index_path) == logical
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
    assert all(isinstance(value, float) and value >= 0 for value in snapshot["stages"].values())
    assert all(isinstance(value, int) and value >= 0 for value in snapshot["record_counts"].values())
    assert all(isinstance(value, int) and value >= 0 for value in snapshot["byte_counts"].values())
    forbidden = {"command", "pid", "timestamp", "secret", "payload"}
    assert forbidden.isdisjoint(snapshot)
