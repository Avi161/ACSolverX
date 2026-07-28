from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


CHECKER_PATH = Path(__file__).parents[2] / ".scratch" / "depth4_provenance_check.py"
SPEC = spec_from_file_location("depth4_provenance_check", CHECKER_PATH)
assert SPEC is not None and SPEC.loader is not None
CHECKER = module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


def test_all_depth_four_low_minority_classes_are_closed() -> None:
    records = CHECKER.low_minority_certificate_records()
    assert len(records) == 24
    assert not any(record.found_target for record in records)


def multiply_and_cyclically_reduce(parts, orders):
    value = ()
    for part in parts:
        value = CHECKER.fp_multiply(value, part, orders)
    return CHECKER.cyclic_reduce(value, orders)


def positive_control(quotient):
    orders, images = CHECKER.QUOTIENTS[quotient]
    minority = "B" if quotient == "Q_A" else "A"
    source = CHECKER.cyclic_reduce(
        CHECKER.evaluate(CHECKER.SOURCES[minority], images, orders),
        orders,
    )
    source_rotations = CHECKER.rotations(source)
    for connector, connector_inverse in CHECKER.stream_reduced_connectors(orders, 2):
        for left_rotation in source_rotations:
            for right_rotation in source_rotations:
                parts = (
                    left_rotation,
                    connector,
                    right_rotation,
                    connector_inverse,
                )
                target = multiply_and_cyclically_reduce(parts, orders)
                loss = 2 * len(source) + 2 * len(connector) - len(target)
                if len(target) < 2 or not 0 <= loss < len(source):
                    continue
                target_subwords = {
                    length: CHECKER.cyclic_subwords(target, length)
                    if length <= len(target)
                    else set()
                    for length in range(1, 3)
                }
                leaf_admitted = CHECKER.connector_can_retain_target_subword(
                    connector,
                    len(source),
                    len(target),
                    target_subwords,
                )
                prefixes_admitted = all(
                    CHECKER.connector_prefix_can_reach_target(
                        connector[:prefix_length],
                        len(source),
                        len(target),
                        2,
                        target_subwords,
                    )
                    for prefix_length in range(len(connector) + 1)
                )
                optimized = CHECKER.cyclic_reduce_for_target_lengths(
                    parts,
                    orders,
                    {len(target)},
                )
                if leaf_admitted and prefixes_admitted and optimized == target:
                    return orders, source, target, target_subwords
    raise AssertionError(f"no positive control survived in {quotient}")


def test_positive_controls_exercise_both_quotient_pruning_paths() -> None:
    for quotient in ("Q_A", "Q_B"):
        orders, source, target, target_subwords = positive_control(quotient)
        unpruned_hits = set()
        pruned_hits = set()

        def branch_possible(prefix):
            return CHECKER.connector_prefix_can_reach_target(
                prefix,
                len(source),
                len(target),
                2,
                target_subwords,
            )

        for branch, hits in ((None, unpruned_hits), (branch_possible, pruned_hits)):
            for connector, connector_inverse in CHECKER.stream_reduced_connectors(
                orders,
                2,
                branch,
            ):
                if not CHECKER.connector_can_retain_target_subword(
                    connector,
                    len(source),
                    len(target),
                    target_subwords,
                ):
                    continue
                for left_rotation in CHECKER.rotations(source):
                    for right_rotation in CHECKER.rotations(source):
                        reduced = CHECKER.cyclic_reduce_for_target_lengths(
                            (
                                left_rotation,
                                connector,
                                right_rotation,
                                connector_inverse,
                            ),
                            orders,
                            {len(target)},
                        )
                        if reduced in CHECKER.rotations(target):
                            hits.add((connector, left_rotation, right_rotation))

        assert pruned_hits
        assert pruned_hits == unpruned_hits


def test_every_leaf_admitted_connector_has_admitted_prefixes() -> None:
    for quotient in ("Q_A", "Q_B"):
        orders, source, target, target_subwords = positive_control(quotient)
        for connector, _ in CHECKER.stream_reduced_connectors(orders, 2):
            if not CHECKER.connector_can_retain_target_subword(
                connector,
                len(source),
                len(target),
                target_subwords,
            ):
                continue
            assert all(
                CHECKER.connector_prefix_can_reach_target(
                    connector[:prefix_length],
                    len(source),
                    len(target),
                    2,
                    target_subwords,
                )
                for prefix_length in range(len(connector) + 1)
            )


def test_target_length_reducer_matches_ordinary_reduction() -> None:
    for orders, _ in CHECKER.QUOTIENTS.values():
        connectors = tuple(CHECKER.stream_reduced_connectors(orders, 2))
        for left, _ in connectors:
            for right, _ in connectors:
                parts = (left, right)
                ordinary = multiply_and_cyclically_reduce(parts, orders)
                assert CHECKER.cyclic_reduce_for_target_lengths(
                    parts,
                    orders,
                    {len(ordinary)},
                ) == ordinary
                assert CHECKER.cyclic_reduce_for_target_lengths(
                    parts,
                    orders,
                    {len(ordinary) + 1},
                ) is None
