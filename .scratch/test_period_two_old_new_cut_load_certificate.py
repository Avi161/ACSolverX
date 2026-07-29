import functools
import importlib.util
import operator
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / ".scratch/period_two_old_new_cut_load_certificate.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_generator():
    return load_module("old_new_load_generator", GENERATOR)


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
    expected_paths = {
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
    }
    assert set(context.source_digests) == expected_paths
    assert all(
        re.fullmatch(r"[0-9a-f]{64}", digest)
        for digest in context.source_digests.values()
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
