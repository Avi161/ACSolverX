import copy
import functools
import importlib.util
import operator
import re
import sys
from dataclasses import replace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / ".scratch/period_two_old_new_cut_load_certificate.py"
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
