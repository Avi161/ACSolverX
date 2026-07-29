import copy
import functools
import importlib.util
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
        len(catalog["mapping"]) == catalog["template_count"]
        and len(catalog["records"]) == catalog["record_count"]
        and set(catalog["mapping"].values()) <= set(catalog["records"])
        for catalog in template_catalogs
    )
    pumping_records = [
        record
        for catalog in template_catalogs
        for record in catalog["records"].values()
        if record["pumping_witnesses"]
    ]
    assert pumping_records
    assert all(
        set(record)
        == {
            "variables",
            "tagged_base_word",
            "base_word",
            "normalized_blocks",
            "terminal_full_letter",
            "terminal_c_deleted",
            "pumping_witnesses",
        }
        for record in pumping_records
    )
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
                record["pumping_witnesses"]
                for record in ledger["template_catalog"]["records"].values()
            )
        )
        pumping_digest = next(
            digest
            for digest, record in manifest["family_ledgers"][pumping_family][
                "template_catalog"
            ]["records"].items()
            if record["pumping_witnesses"]
        )
        wrong_boundary = copy.deepcopy(manifest)
        wrong_boundary["family_ledgers"][pumping_family]["template_catalog"][
            "records"
        ][pumping_digest]["pumping_witnesses"][0]["left_copy_id"] += 1
        mutations.append(
            ("boundary", wrong_boundary, verifier.PumpingVerificationError)
        )

        wrong_terminal = copy.deepcopy(manifest)
        terminal_record = wrong_terminal["family_ledgers"][pumping_family][
            "template_catalog"
        ]["records"][pumping_digest]
        terminal_record["terminal_c_deleted"] = not terminal_record[
            "terminal_c_deleted"
        ]
        mutations.append(
            ("terminal", wrong_terminal, verifier.PumpingVerificationError)
        )

        wrong_mapping = copy.deepcopy(manifest)
        mapping = wrong_mapping["family_ledgers"][pumping_family][
            "template_catalog"
        ]["mapping"]
        del mapping[next(iter(mapping))]
        mutations.append(
            ("mapping", wrong_mapping, verifier.PumpingVerificationError)
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
