from __future__ import annotations

from itertools import permutations, product


Permutation = tuple[int, ...]
Vector = tuple[int, ...]

IDENTITY: Permutation = (0, 1, 2)
GROUP = tuple(permutations(range(3)))
GROUP_INDEX = {element: index for index, element in enumerate(GROUP)}


def multiply(left: Permutation, right: Permutation) -> Permutation:
    return tuple(left[right[index]] for index in range(3))


def inverse(element: Permutation) -> Permutation:
    result = [0] * 3
    for source, target in enumerate(element):
        result[target] = source
    return tuple(result)


def signed_power(element: Permutation, sign: int) -> Permutation:
    return element if sign == 1 else inverse(element)


def conjugate(
    conjugator: Permutation,
    element: Permutation,
) -> Permutation:
    return multiply(
        multiply(conjugator, element),
        inverse(conjugator),
    )


def vector_add(*vectors: Vector) -> Vector:
    return tuple(sum(values) for values in zip(*vectors))


def vector_negate(vector: Vector) -> Vector:
    return tuple(-value for value in vector)


def vector_scale(coefficient: int, vector: Vector) -> Vector:
    return tuple(coefficient * value for value in vector)


def left_action(element: Permutation, vector: Vector) -> Vector:
    result = [0] * len(GROUP)
    for group_element, coefficient in zip(GROUP, vector):
        destination = multiply(element, group_element)
        result[GROUP_INDEX[destination]] += coefficient
    return tuple(result)


def monomial_action(
    coefficient: int,
    element: Permutation,
    vector: Vector,
) -> Vector:
    return vector_scale(coefficient, left_action(element, vector))


def pair_multiply(
    left: tuple[Vector, Permutation],
    right: tuple[Vector, Permutation],
) -> tuple[Vector, Permutation]:
    left_vector, left_group = left
    right_vector, right_group = right
    return (
        vector_add(left_vector, left_action(left_group, right_vector)),
        multiply(left_group, right_group),
    )


def pair_inverse(
    pair: tuple[Vector, Permutation],
) -> tuple[Vector, Permutation]:
    vector, group_element = pair
    group_inverse = inverse(group_element)
    return (
        vector_negate(left_action(group_inverse, vector)),
        group_inverse,
    )


def pair_signed_power(
    pair: tuple[Vector, Permutation],
    sign: int,
) -> tuple[Vector, Permutation]:
    return pair if sign == 1 else pair_inverse(pair)


def pair_conjugate(
    conjugator: tuple[Vector, Permutation],
    pair: tuple[Vector, Permutation],
) -> tuple[Vector, Permutation]:
    return pair_multiply(
        pair_multiply(conjugator, pair),
        pair_inverse(conjugator),
    )


def evaluated_row(
    epsilon: int,
    eta: int,
    theta: int,
) -> tuple[
    Permutation,
    Permutation,
    Permutation,
    Permutation,
    Permutation,
    Permutation,
    Permutation,
]:
    nonidentity = tuple(
        element for element in GROUP if element != IDENTITY
    )
    for b, alpha, beta, gamma, d in product(nonidentity, repeat=5):
        r = conjugate(alpha, signed_power(b, epsilon))
        k = multiply(d, r)
        s = conjugate(beta, signed_power(k, eta))
        c = multiply(b, s)
        final = multiply(k, conjugate(gamma, signed_power(c, theta)))
        if final == IDENTITY:
            return b, alpha, beta, gamma, d, k, c
    raise AssertionError("no nontrivial finite-group row")


def row_l(
    eta: int,
    theta: int,
    k: Permutation,
    gamma: Permutation,
    b: Permutation,
    beta: Permutation,
) -> Permutation:
    if eta == 1 and theta == 1:
        return multiply(multiply(multiply(k, gamma), b), beta)
    if eta == 1 and theta == -1:
        return multiply(multiply(gamma, b), beta)
    if eta == -1 and theta == 1:
        return multiply(
            multiply(multiply(multiply(k, gamma), b), beta),
            inverse(k),
        )
    return multiply(
        multiply(multiply(gamma, b), beta),
        inverse(k),
    )


def test_all_eight_signed_fox_rows_have_the_master_factorization():
    j = (2, -1, 0, 3, -2, 1)
    delta = (-1, 2, 1, 0, 3, -2)
    u_vector = (1, 0, -2, 3, 1, -1)
    v_vector = (0, 2, -1, 1, -3, 2)
    w_vector = (3, -2, 1, 0, 2, -1)

    for epsilon, eta, theta in product((1, -1), repeat=3):
        b, alpha, beta, gamma, d, k, c = evaluated_row(
            epsilon,
            eta,
            theta,
        )

        b_pair = (j, b)
        d_pair = (delta, d)
        u_pair = (u_vector, alpha)
        v_pair = (v_vector, beta)
        w_pair = (w_vector, gamma)

        d1 = pair_multiply(
            d_pair,
            pair_conjugate(
                u_pair,
                pair_signed_power(b_pair, epsilon),
            ),
        )
        b1 = pair_multiply(
            b_pair,
            pair_conjugate(
                v_pair,
                pair_signed_power(d1, eta),
            ),
        )
        d2 = pair_multiply(
            d1,
            pair_conjugate(
                w_pair,
                pair_signed_power(b1, theta),
            ),
        )

        assert d1[1] == k
        assert b1[1] == c
        assert d2[1] == IDENTITY

        r = conjugate(alpha, signed_power(b, epsilon))
        s = conjugate(beta, signed_power(k, eta))
        j_epsilon = (
            j
            if epsilon == 1
            else vector_negate(left_action(inverse(b), j))
        )
        x_vector = vector_add(
            delta,
            left_action(d, u_vector),
            vector_negate(left_action(k, u_vector)),
            left_action(multiply(d, alpha), j_epsilon),
        )

        if eta == 1:
            n_sign, n_group = 1, multiply(b, beta)
        else:
            n_sign = -1
            n_group = multiply(multiply(b, beta), inverse(k))
        y_vector = vector_add(
            j,
            left_action(b, v_vector),
            vector_negate(left_action(multiply(b, s), v_vector)),
            monomial_action(n_sign, n_group, x_vector),
        )

        if theta == 1:
            m_sign, m_group = 1, multiply(k, gamma)
        else:
            m_sign, m_group = -1, gamma
        xi_vector = vector_add(
            x_vector,
            left_action(k, w_vector),
            vector_negate(w_vector),
            monomial_action(m_sign, m_group, y_vector),
        )

        assert d1[0] == x_vector
        assert b1[0] == y_vector
        assert d2[0] == xi_vector

        sign_product = eta * theta
        l_element = row_l(eta, theta, k, gamma, b, beta)
        assert m_sign * n_sign == sign_product
        assert multiply(m_group, n_group) == l_element

        f_epsilon = vector_add(
            delta,
            left_action(multiply(d, alpha), j_epsilon),
        )
        d_minus_k_u = vector_add(
            left_action(d, u_vector),
            vector_negate(left_action(k, u_vector)),
        )
        fixed_and_u = vector_add(f_epsilon, d_minus_k_u)

        a_v_applied = vector_scale(
            -sign_product,
            vector_add(
                left_action(
                    multiply(
                        multiply(l_element, k),
                        inverse(beta),
                    ),
                    v_vector,
                ),
                vector_negate(
                    left_action(
                        multiply(l_element, inverse(beta)),
                        v_vector,
                    )
                ),
            ),
        )
        factorized = vector_add(
            fixed_and_u,
            monomial_action(
                sign_product,
                l_element,
                fixed_and_u,
            ),
            monomial_action(m_sign, m_group, j),
            a_v_applied,
            left_action(k, w_vector),
            vector_negate(w_vector),
        )
        assert xi_vector == factorized

        direct_v_coefficient = monomial_action(
            m_sign,
            m_group,
            vector_add(
                left_action(b, v_vector),
                vector_negate(left_action(multiply(b, s), v_vector)),
            ),
        )
        assert direct_v_coefficient == a_v_applied

        conjugate_k = conjugate(l_element, k)
        bridge_ideal_left = vector_add(
            left_action(
                multiply(
                    multiply(l_element, k),
                    inverse(beta),
                ),
                v_vector,
            ),
            vector_negate(
                left_action(
                    multiply(l_element, inverse(beta)),
                    v_vector,
                )
            ),
        )
        bridge_ideal_right = vector_add(
            left_action(
                multiply(
                    multiply(conjugate_k, l_element),
                    inverse(beta),
                ),
                v_vector,
            ),
            vector_negate(
                left_action(
                    multiply(l_element, inverse(beta)),
                    v_vector,
                )
            ),
        )
        assert bridge_ideal_left == bridge_ideal_right


def path_incidence(edge_coefficients: tuple[int, ...], sign: int):
    vertices = [0] * (len(edge_coefficients) + 1)
    for index, coefficient in enumerate(edge_coefficients):
        vertices[index] += coefficient
        vertices[index + 1] += sign * coefficient
    return tuple(vertices)


def reconstruct_path(
    vertex_coefficients: tuple[int, ...],
    sign: int,
) -> tuple[int, ...]:
    edges = []
    previous = 0
    for index, coefficient in enumerate(vertex_coefficients[:-1]):
        edge = coefficient - sign * previous
        edges.append(edge)
        previous = edge
    assert sign * previous == vertex_coefficients[-1]
    return tuple(edges)


def test_signed_hnn_path_incidence_has_both_exact_image_criteria():
    for edge_count in range(1, 8):
        oriented_vertices = tuple(
            (index % 5) - 2
            for index in range(edge_count)
        )
        oriented_vertices += (-sum(oriented_vertices),)
        oriented_edges = reconstruct_path(oriented_vertices, -1)
        assert path_incidence(oriented_edges, -1) == oriented_vertices
        assert sum(oriented_vertices) == 0

        unsigned_vertices = tuple(
            ((2 * index + 1) % 7) - 3
            for index in range(edge_count)
        )
        required_last = -sum(
            (-1) ** index * coefficient
            for index, coefficient in enumerate(unsigned_vertices)
        )
        required_last *= (-1) ** edge_count
        unsigned_vertices += (required_last,)
        unsigned_edges = reconstruct_path(unsigned_vertices, 1)
        assert path_incidence(unsigned_edges, 1) == unsigned_vertices
        assert sum(
            (-1) ** index * coefficient
            for index, coefficient in enumerate(unsigned_vertices)
        ) == 0

        for candidate in product((-1, 0, 1), repeat=edge_count):
            if any(candidate):
                assert any(path_incidence(candidate, -1))
                assert any(path_incidence(candidate, 1))
