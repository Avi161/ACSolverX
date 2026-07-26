from experiments.stable_ac.verify_ad_relative_product_fox_sieve import (
    A,
    D,
    FOX_SLICE_RESIDUAL_CASES,
    abelian_exponent_sums,
    fox_gradient_mod,
    free_reduce,
    finite_modulus_witness,
    fox_gradient_qz,
    inverse_word,
    projection_sieve_kind,
    project_qz,
    qz_axis_power,
    word_value_mod,
)


def relative_product(conjugator: str, sigma: int) -> str:
    source = D if sigma == 1 else inverse_word(D)
    return free_reduce(A + conjugator + source + inverse_word(conjugator))


def test_literal_fox_row_has_the_universal_two_coordinate_slice():
    modulus = 101
    inverse_three = pow(3, -1, modulus)
    samples = (
        "",
        "q",
        "z",
        "xTqZ",
        "qzxTZQ",
        "TQztxqXZ",
    )

    for sigma in (1, -1):
        for z_value in (1, 2, 17, 73):
            q_value = 4 * z_value * inverse_three % modulus
            values = {
                "x": 1,
                "t": 1,
                "z": z_value,
                "q": q_value,
            }
            for conjugator in samples:
                conjugator_value = word_value_mod(
                    conjugator,
                    values,
                    modulus,
                )
                expected = (
                    3 * q_value
                    + sigma * conjugator_value * z_value,
                    -4 - sigma * conjugator_value,
                    0,
                    0,
                )
                assert fox_gradient_mod(
                    relative_product(conjugator, sigma),
                    values,
                    modulus,
                ) == tuple(
                    coordinate % modulus for coordinate in expected
                )


def test_nonzero_total_exponent_examples_give_common_torus_zeros():
    modulus = 101
    inverse_three = pow(3, -1, modulus)

    for sigma in (1, -1):
        examples = (
            ("z", -4 * sigma),
            ("q", -3 * sigma),
        )
        for conjugator, z_value in examples:
            values = {
                "x": 1,
                "t": 1,
                "z": z_value % modulus,
                "q": (
                    4 * z_value * inverse_three
                ) % modulus,
            }
            assert fox_gradient_mod(
                relative_product(conjugator, sigma),
                values,
                modulus,
            ) == (0, 0, 0, 0)


def test_zero_total_exponent_modular_witnesses_leave_exactly_three_cases():
    observed_residual = set()

    for sigma in (1, -1):
        for q_exponent in range(-24, 25):
            modulus = finite_modulus_witness(
                sigma,
                q_exponent,
            )
            if modulus is None:
                observed_residual.add((sigma, q_exponent))
                continue

            assert modulus > 1
            assert modulus % 2 and modulus % 3
            ratio = 4 * pow(3, -1, modulus)
            value = pow(
                ratio,
                q_exponent,
                modulus,
            )
            assert value == (-4 * sigma) % modulus

    assert observed_residual == FOX_SLICE_RESIDUAL_CASES


def test_exponent_sums_ignore_nonabelian_conjugator_shape():
    assert abelian_exponent_sums("qzxTZQXt") == {
        "x": 0,
        "t": 0,
        "z": 0,
        "q": 0,
    }
    assert abelian_exponent_sums("qqZZxTzt") == {
        "x": 1,
        "t": 0,
        "z": -1,
        "q": 2,
    }


def test_qz_projection_and_axis_membership_are_exact_free_word_checks():
    h = "qZ"

    assert project_qz("xqtZXT") == h
    assert project_qz("xqQtzZT") == ""
    assert qz_axis_power("") == 0
    assert qz_axis_power(h) == 1
    assert qz_axis_power(inverse_word(h)) == -1
    assert qz_axis_power(h * 7) == 7
    assert qz_axis_power(inverse_word(h) * 5) == -5

    same_exponents_but_noncyclic = h + "qzQZ"
    assert abelian_exponent_sums(
        same_exponents_but_noncyclic
    )["q"] == 1
    assert abelian_exponent_sums(
        same_exponents_but_noncyclic
    )["z"] == -1
    assert qz_axis_power(same_exponents_but_noncyclic) is None


def test_induced_module_sieve_leaves_three_exact_projection_fibers():
    h = "qZ"
    residual = {
        (1, h),
        (-1, ""),
        (-1, h),
    }
    observed = set()

    candidates = (
        "",
        h,
        inverse_word(h),
        h * 2,
        inverse_word(h) * 2,
        h + "qzQZ",
        "qzQZ",
        "xqtZXT",
        "xqzQZT",
    )
    for sigma in (1, -1):
        for conjugator in candidates:
            kind = projection_sieve_kind(conjugator, sigma)
            projected = project_qz(conjugator)
            if kind == "residual":
                observed.add((sigma, projected))
            elif qz_axis_power(projected) is None:
                assert kind == "induced-module"
            else:
                assert kind == "cyclic-modular"

    assert observed == residual


def test_literal_noncommutative_fox_row_depends_only_on_qz_projection():
    samples = (
        "",
        "qZ",
        "xqtZXT",
        "qZqzQZ",
        "TQztxqXZ",
    )

    for sigma in (1, -1):
        for conjugator in samples:
            projected = project_qz(conjugator)
            gz = free_reduce(projected + "z")
            expected_x = {"q": 3}
            expected_x[gz] = expected_x.get(gz, 0) + sigma
            expected_x = {
                word: coefficient
                for word, coefficient in expected_x.items()
                if coefficient
            }
            expected_t = {"": -4}
            expected_t[projected] = (
                expected_t.get(projected, 0) - sigma
            )
            expected_t = {
                word: coefficient
                for word, coefficient in expected_t.items()
                if coefficient
            }

            assert fox_gradient_qz(
                relative_product(conjugator, sigma)
            ) == (
                expected_x,
                expected_t,
                {},
                {},
            )
