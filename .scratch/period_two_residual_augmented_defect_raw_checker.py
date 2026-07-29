"""All-power certificate for the raw inverse-Q residual term."""

from __future__ import annotations

import importlib.util
import sys
from itertools import combinations
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INVERSE_CHECKER = ROOT / ".scratch/period_two_inverse_q_companion_checker.py"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def raw_observable(
    generator: Any,
    action: tuple[int, ...],
    vertex: tuple[int, ...],
) -> tuple[
    tuple[tuple[int, ...], ...],
    tuple[bool, ...],
    int,
    tuple[int, ...],
]:
    overlap = generator.actual_overlap(action, vertex)
    raw_word, _ = generator.branch_word({"k": overlap}, action, vertex)
    events = generator.formula_events(raw_word)
    assert len(events) % 2 == 1
    middle = len(events) // 2
    central = generator.lift.c_vertex(
        generator.lift.quotient_multiply(action, vertex)
    )
    assert events[middle][0] == central
    assert [label for label, _ in events[:middle]] == [
        label for label, _ in reversed(events[middle + 1 :])
    ]
    first_labels = tuple(label for label, _ in events[:middle])
    equalities = tuple(label == central for label in first_labels)
    rho = sum(not equality for equality in equalities) % 2
    return first_labels, equalities, rho, central


def raw_rho(generator: Any, action: tuple[int, ...], vertex: tuple[int, ...]) -> int:
    return raw_observable(generator, action, vertex)[2]


def raw_q_bits(
    inverse: Any,
    generator: Any,
    schemas: dict[str, Any],
    metadata: dict[str, dict[str, Any]],
    actions: dict[int, tuple[int, ...]],
    a: int,
    n: int,
) -> tuple[int, ...]:
    bits: list[int] = []
    slot_occurrences = {2: (1, 6), 3: (9, 14), 4: (15, 16)}
    for row_key, row in metadata.items():
        for delta in (0, 1):
            schema = schemas[f"partner:module:{row_key}:delta{delta}"]
            vertex = tuple(
                letter
                for letter, _ in inverse.tagged_c_vertex(generator, schema, a, n)
            )
            bits.append(sum(
                raw_rho(generator, actions[occurrence], vertex)
                for occurrence in slot_occurrences[row["slot"]]
            ) % 2)
    assert len(bits) == 184
    return tuple(bits)


def raw_q_observables(
    inverse: Any,
    generator: Any,
    schemas: dict[str, Any],
    metadata: dict[str, dict[str, Any]],
    actions: dict[int, tuple[int, ...]],
    a: int,
    n: int,
) -> tuple[
    tuple[tuple[tuple[int, ...], ...], tuple[bool, ...], int, tuple[int, ...]],
    ...,
]:
    output = []
    slot_occurrences = {2: (1, 6), 3: (9, 14), 4: (15, 16)}
    for row_key, row in metadata.items():
        for delta in (0, 1):
            schema = schemas[f"partner:module:{row_key}:delta{delta}"]
            vertex = tuple(
                letter
                for letter, _ in inverse.tagged_c_vertex(generator, schema, a, n)
            )
            output.extend(
                raw_observable(generator, actions[occurrence], vertex)
                for occurrence in slot_occurrences[row["slot"]]
            )
    assert len(output) == 368
    return tuple(output)


def shortlex_order(left: tuple[int, ...], right: tuple[int, ...]) -> int:
    return -1 if (len(left), left) < (len(right), right) else 1 if left != right else 0


def slot_zero_new_new(
    generator: Any,
    occurrences: dict[int, dict[str, Any]],
    actions: dict[int, tuple[int, ...]],
    a: int,
    n: int,
) -> tuple[int, int]:
    gamma = generator.eval_path(generator.BLOCKS[0][2])
    gamma_inverse = generator.lift.quotient_inverse(gamma)
    p_inverse = generator.lift.quotient_inverse(generator.parse_raw("tc"))
    corners = ((a + 1, a + n + 2), (a, a + n + 2), (a + 1, a + n + 3), (a, a + n + 3))
    vertices = []
    for exponent, tail in corners:
        vertex = generator.lift.c_vertex(
            generator.lift.quotient_reduce(
                (
                    *p_inverse,
                    *generator.quotient_power(gamma, exponent),
                    *generator.parse_raw("c"),
                    *generator.quotient_power(gamma_inverse, tail),
                    *generator.parse_raw("t"),
                )
            )
        )
        vertices.append(vertex)
    assert len(set(vertices)) == 4

    footprints = []
    token_data = {}
    for vertex in vertices:
        footprint = []
        for occurrence in (3, 4, 7, 8, 11, 12):
            label = generator.lift.c_vertex(
                generator.lift.quotient_multiply(actions[occurrence], vertex)
            )
            token = (occurrence, vertex)
            footprint.append(token)
            token_data[token] = (
                occurrence,
                occurrences[occurrence]["polarity"],
                vertex,
                label,
            )
        footprints.append(frozenset(footprint))

    def kernel(left_token: tuple[int, tuple[int, ...]], right_token: tuple[int, tuple[int, ...]]) -> int:
        if left_token == right_token:
            return 0
        left = token_data[left_token]
        right = token_data[right_token]
        left_occurrence, left_polarity, left_vertex, left_label = left
        right_occurrence, _, right_vertex, right_label = right
        if left_occurrence != right_occurrence:
            chronological_left = left_occurrence < right_occurrence
        else:
            module_order = shortlex_order(left_vertex, right_vertex)
            assert module_order != 0
            chronological_left = module_order == left_polarity
        first_label, second_label = (
            (left_label, right_label) if chronological_left else (right_label, left_label)
        )
        return int(shortlex_order(first_label, second_label) == -1)

    def add_sets(*values: frozenset[tuple[int, tuple[int, ...]]]) -> frozenset[tuple[int, tuple[int, ...]]]:
        result = frozenset()
        for value in values:
            result = result.symmetric_difference(value)
        return result

    def quadratic(value: frozenset[tuple[int, tuple[int, ...]]]) -> int:
        return sum(kernel(left, right) for left, right in combinations(value, 2)) % 2

    def bilinear(
        left: frozenset[tuple[int, tuple[int, ...]]],
        right: frozenset[tuple[int, tuple[int, ...]]],
    ) -> int:
        return sum(kernel(left_token, right_token) for left_token in left for right_token in right) % 2

    corner_00, corner_01, corner_11, corner_12 = footprints
    b_zero = add_sets(corner_00, corner_01)
    f_zero = add_sets(corner_00, corner_11)
    g_zero = add_sets(corner_00, corner_01, corner_11, corner_12)
    q_g_zero = quadratic(g_zero)
    complete_new_new = (
        q_g_zero
        ^ bilinear(b_zero, f_zero)
        ^ bilinear(b_zero, g_zero)
        ^ bilinear(f_zero, g_zero)
    )
    return q_g_zero, complete_new_new


def main() -> None:
    inverse = load_module("residual_inverse_q_checker", INVERSE_CHECKER)
    generator = inverse.load_raw_generator()
    schemas, metadata = inverse.schema_words(generator)
    templates, template_metadata = inverse.build_templates(generator)
    assert metadata == template_metadata
    occurrences = {item["order"]: item for item in generator.trace_ast()[1]}
    actions = {
        order: generator.parse_raw(item["quotient_prefix"])
        for order, item in occurrences.items()
    }

    assert raw_rho(generator, generator.parse_raw("tc"), generator.parse_raw("cT")) == 1
    assert raw_rho(generator, (), ()) == 0

    refined_values = (("0", 0), ("1", 1), ("2", 2), ("ge3", 3))
    points = [
        (f"a{a_id}_n{n_id}", a, n)
        for a_id, a in refined_values
        for n_id, n in refined_values
    ]
    results = []
    for point_id, a, n in points:
        bits = raw_q_bits(
            inverse,
            generator,
            schemas,
            metadata,
            actions,
            a,
            n,
        )
        results.append((point_id, sum(bits), sum(bits) % 2))
    assert all(value == 0 for _, _, value in results)
    assert all(one_count == (84 if point_id.startswith("a0_") else 80) for point_id, one_count, _ in results)

    print("PASS: sixteen-cell raw inverse-Q all-power certificate")
    for point_id, one_count, value in results:
        print(f"{point_id}: ones={one_count}, xor={value}")

    transition_failures = []
    central_stability_failures = []
    for fixed in range(4):
        left_full = raw_q_observables(
            inverse, generator, schemas, metadata, actions, 3, fixed
        )
        right_full = raw_q_observables(
            inverse, generator, schemas, metadata, actions, 4, fixed
        )
        left = tuple(item[:3] for item in left_full)
        right = tuple(item[:3] for item in right_full)
        if left != right:
            transition_failures.append(("a", fixed, sum(x != y for x, y in zip(left, right))))
        central_stability_failures.extend(
            ("a", fixed, index)
            for index, (_, equalities, _) in enumerate(left)
            if any(equalities)
        )
        central_stability_failures.extend(
            ("a_length", fixed, index)
            for index, (first_labels, _, _, central) in enumerate(left_full)
            if first_labels and len(central) <= max(len(label) for label in first_labels)
        )
        left_full = raw_q_observables(
            inverse, generator, schemas, metadata, actions, fixed, 3
        )
        right_full = raw_q_observables(
            inverse, generator, schemas, metadata, actions, fixed, 4
        )
        left = tuple(item[:3] for item in left_full)
        right = tuple(item[:3] for item in right_full)
        if left != right:
            transition_failures.append(("n", fixed, sum(x != y for x, y in zip(left, right))))
        central_stability_failures.extend(
            ("n", fixed, index)
            for index, (_, equalities, _) in enumerate(left)
            if any(equalities)
        )
        central_stability_failures.extend(
            ("n_length", fixed, index)
            for index, (first_labels, _, _, central) in enumerate(left_full)
            if first_labels and len(central) <= max(len(label) for label in first_labels)
        )
    assert not transition_failures
    assert not central_stability_failures

    shield_checks = 0
    for row_key, row in metadata.items():
        action_horizon = max(
            len(actions[occurrence])
            for occurrence in {2: (1, 6), 3: (9, 14), 4: (15, 16)}[row["slot"]]
        ) + 1
        for delta in (0, 1):
            schema_id = f"partner:module:{row_key}:delta{delta}"
            for a_id, a in refined_values:
                for n_id, n in refined_values:
                    if a_id != "ge3" and n_id != "ge3":
                        continue
                    coarse_cells = [
                        cell
                        for cell in inverse.CELLS
                        if inverse.cell_contains(cell, a, n)
                    ]
                    assert len(coarse_cells) == 1
                    template = templates[(schema_id, coarse_cells[0].cell_id)]
                    for variable in (
                        *(("a",) if a_id == "ge3" else ()),
                        *(("n",) if n_id == "ge3" else ()),
                    ):
                        coefficient_index = 0 if variable == "a" else 1
                        changing_blocks = [
                            (name, core, affine)
                            for name, core, affine in template.blocks
                            if affine is not None and affine[coefficient_index] > 0
                        ]
                        assert changing_blocks
                        name, core, affine = changing_blocks[0]
                        exponent = affine[0] * a + affine[1] * n + affine[2]
                        split = dict(template.insertion_splits)[name]
                        assert exponent >= 3
                        assert len(core) == 8
                        assert split + exponent * len(core) > action_horizon
                        assert template.length_affine_an[coefficient_index] > 0
                        shield_checks += 1

    print("observable transition failures: 0")
    print("central-stability failures on pump cells: 0")
    print(f"primitive-core shield checks: {shield_checks}")

    g_zero_values = []
    for point_id, a, n in points:
        g_zero_values.append(
            (point_id, *slot_zero_new_new(generator, occurrences, actions, a, n))
        )
    print("bounded slot-zero new-new values Q(g0), complete:")
    for point_id, q_value, complete_value in g_zero_values:
        print(f"{point_id}: {q_value}, {complete_value}")


if __name__ == "__main__":
    main()
