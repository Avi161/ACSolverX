from itertools import permutations, product

from experiments.stable_ac.mms02_depth_five_lift_equations_certificate import (
    EXPECTED_ENDPOINT_BASE_VECTORS,
    EXPECTED_MONODROMY_MATRIX,
)

Permutation = tuple[int, int, int]
S3: tuple[Permutation, ...] = tuple(permutations(range(3)))
IDENTITY: Permutation = (0, 1, 2)


def compose(left: Permutation, right: Permutation) -> Permutation:
    return tuple(left[right[index]] for index in range(3))


def inverse(value: Permutation) -> Permutation:
    result = [0] * 3
    for index, image in enumerate(value):
        result[image] = index
    return tuple(result)


def power(value: Permutation, exponent: int) -> Permutation:
    if exponent < 0:
        return power(inverse(value), -exponent)
    result = IDENTITY
    for _ in range(exponent):
        result = compose(result, value)
    return result


def conjugate(conjugator: Permutation, value: Permutation) -> Permutation:
    return compose(compose(conjugator, value), inverse(conjugator))


def commutator(left: Permutation, right: Permutation) -> Permutation:
    return compose(compose(compose(left, right), inverse(left)), inverse(right))


def matrix_vector(vector: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    return tuple(
        sum(EXPECTED_MONODROMY_MATRIX[row][column] * vector[column] for column in range(4))
        for row in range(4)
    )


def add(left, right):
    return tuple(left[index] + right[index] for index in range(4))


def subtract(left, right):
    return tuple(left[index] - right[index] for index in range(4))


def test_simultaneous_power_conjugations_remove_both_heights() -> None:
    for u, p, h, r in product(S3, S3, S3, range(-2, 3)):
        p0 = conjugate(power(u, r), p)
        h0 = compose(h, power(u, -r))
        assert conjugate(h0, commutator(u, p0)) == conjugate(
            h, commutator(u, p)
        )

    for u, v, q, c, r, m in product(S3, S3, S3, S3, range(-2, 3), range(-2, 3)):
        k = r + m
        c1 = compose(power(u, r), c)
        q0 = conjugate(power(v, k), q)
        c0 = compose(c1, power(v, -k))
        assert conjugate(c0, commutator(v, q0)) == conjugate(
            c1, commutator(v, q)
        )


def test_shift_free_abelian_formulas_replay() -> None:
    alpha, beta = EXPECTED_ENDPOINT_BASE_VECTORS
    constant = (-2, 6, -10, 4)
    samples = (
        (0, 0, 0, 0),
        (1, 0, 0, 0),
        (0, -2, 3, 1),
        (-4, 5, -6, 7),
    )
    for q_vector in samples:
        p_vector = q_vector
        t_vector = add(matrix_vector(p_vector), constant)
        left_first = subtract(matrix_vector(p_vector), p_vector)
        right_first = subtract(matrix_vector(q_vector), q_vector)
        assert left_first == right_first

        one_minus_m_t = subtract(t_vector, matrix_vector(t_vector))
        m_minus_i_p = subtract(matrix_vector(p_vector), p_vector)
        right_second = add(add(one_minus_m_t, alpha), matrix_vector(m_minus_i_p))
        assert right_second == beta
