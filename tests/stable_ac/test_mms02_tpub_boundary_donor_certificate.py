from experiments.stable_ac.thickenable.mms02_tpub_boundary_donor_certificate import (
    decide_tpub_boundary_donors,
    enumerate_boundary_products,
)


def test_raw_boundary_products_have_exactly_four_shortening_cases():
    products = enumerate_boundary_products()
    assert len(products) == 12
    shortened = tuple(
        product
        for product in products
        if len(product.transformed_word)
        < {"A": 12, "B": 14}[product.row] + 3
    )
    assert tuple(
        (
            product.row,
            product.sign,
            product.multiplier,
            product.transformed_word,
        )
        for product in shortened
    ) == (
        ("A", "+", "yzX", "zYXyxZXYxyZyz"),
        ("A", "+", "zXy", "xzYXyxZXYxyXy"),
        ("B", "-", "ZYx", "xZXYXyxzXYxyZ"),
        ("B", "-", "YxZ", "XyxZXYXyxzXYxxZ"),
    )


def test_boundary_donor_signed_rank_exhaustions_are_pinned():
    decisions = decide_tpub_boundary_donors()
    assert tuple(
        (
            decision.transformed_word,
            decision.macro_rotation_budget,
            decision.spherical_scheme_count,
            decision.counters.phase_tuple_budget,
            decision.counters.component_seed_budget,
            decision.counters.closed_component_assignments,
            decision.counters.component_combination_budget,
        )
        for decision in decisions
    ) == (
        ("zYXyxZXYxyZyz", 864, 2, 1_848, 11_088, 96, 0),
        ("xzYXyxZXYxyXy", 288, 12, 9_240, 120_120, 338, 0),
        ("xZXYXyxzXYxyZ", 16, 2, 1_512, 12_096, 40, 0),
        ("XyxZXYXyxzXYxxZ", 144, 4, 3_528, 38_808, 120, 0),
    )
    for decision in decisions:
        counters = decision.counters
        assert decision.verdict == "NOT_SPHERICAL_EXACT_COMPLEX"
        assert decision.witness is None
        assert counters.scheme_budget == decision.spherical_scheme_count
        assert counters.schemes_considered == counters.scheme_budget
        assert counters.phase_tuples_considered == counters.phase_tuple_budget
        assert counters.component_seed_attempts == counters.component_seed_budget
        assert counters.component_combinations_considered == 0
        assert counters.exhaustive
