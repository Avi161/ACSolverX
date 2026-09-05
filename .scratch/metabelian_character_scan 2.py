from __future__ import annotations

# [unverified] Research diagnostic: the p=3 scan completed without an
# obstruction, but the larger p=5 scans were interrupted for runtime.

from itertools import product


PHI = {
    1: (2,),
    2: (3,),
    3: (4,),
    4: (-3, 2, -3, -1, 2, 4, -3, 4),
}
Q = (3, -4, -2, 1, 3, -2, 3, -4, -3, -1, 2, 4, -3, 2, -3, -1)
M = (
    (0, 0, 0, -1),
    (1, 0, 0, 2),
    (0, 1, 0, -3),
    (0, 0, 1, 2),
)
MI_INV = (
    (0, 1, 1, 1),
    (-2, -2, -1, -1),
    (1, 1, 1, 2),
    (-1, -1, -1, -1),
)
Q_AB = (-1, 0, 0, -1)


def inv_word(word: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(-letter for letter in reversed(word))


def mul_affine(
    left: tuple[int, tuple[int, ...]],
    right: tuple[int, tuple[int, ...]],
    prime: int,
) -> tuple[int, tuple[int, ...]]:
    scalar, vector = left
    other_scalar, other_vector = right
    return (
        scalar * other_scalar % prime,
        tuple(
            (vector[index] + scalar * other_vector[index]) % prime
            for index in range(4)
        ),
    )


def inv_affine(
    value: tuple[int, tuple[int, ...]], prime: int
) -> tuple[int, tuple[int, ...]]:
    scalar, vector = value
    scalar_inverse = pow(scalar, -1, prime)
    return (
        scalar_inverse,
        tuple(-scalar_inverse * entry % prime for entry in vector),
    )


def evaluate(
    word: tuple[int, ...], character: tuple[int, ...], prime: int
) -> tuple[int, tuple[int, ...]]:
    value = (1, (0, 0, 0, 0))
    generators = []
    for index, scalar in enumerate(character):
        basis = tuple(1 if index == coordinate else 0 for coordinate in range(4))
        generators.append((scalar, basis))
    for letter in word:
        image = generators[abs(letter) - 1]
        if letter < 0:
            image = inv_affine(image, prime)
        value = mul_affine(value, image, prime)
    return value


def transition_character(
    character: tuple[int, ...], prime: int
) -> tuple[int, ...]:
    return tuple(evaluate(PHI[index], character, prime)[0] for index in range(1, 5))


def character_orbits(prime: int) -> list[tuple[tuple[int, ...], ...]]:
    unseen = set(product(range(1, prime), repeat=4))
    orbits = []
    while unseen:
        start = min(unseen)
        orbit = []
        current = start
        while current not in orbit:
            orbit.append(current)
            unseen.discard(current)
            current = transition_character(current, prime)
        assert current == start
        orbits.append(tuple(orbit))
    return orbits


def jacobian(character: tuple[int, ...], prime: int) -> tuple[tuple[int, ...], ...]:
    return tuple(evaluate(PHI[index], character, prime)[1] for index in range(1, 5))


def row_matrix(row: tuple[int, ...], matrix: tuple[tuple[int, ...], ...], prime: int) -> tuple[int, ...]:
    return tuple(
        sum(row[index] * matrix[index][column] for index in range(4)) % prime
        for column in range(4)
    )


def transform_data(
    data: tuple[tuple[int, tuple[int, ...]], ...],
    jacobians: tuple[tuple[tuple[int, ...], ...], ...],
    prime: int,
) -> tuple[tuple[int, tuple[int, ...]], ...]:
    length = len(data)
    return tuple(
        (
            data[(index + 1) % length][0],
            row_matrix(data[(index + 1) % length][1], jacobians[index], prime),
        )
        for index in range(length)
    )


def data_orbit(
    word: tuple[int, ...],
    characters: tuple[tuple[int, ...], ...],
    jacobians: tuple[tuple[tuple[int, ...], ...], ...],
    prime: int,
    cap: int = 200_000,
) -> tuple[tuple[tuple[int, tuple[int, ...]], ...], ...]:
    start = tuple(evaluate(word, character, prime) for character in characters)
    values = []
    current = start
    while current not in values:
        values.append(current)
        if len(values) >= cap:
            raise RuntimeError(f"data orbit exceeded cap {cap}")
        current = transform_data(current, jacobians, prime)
    assert current == start
    return tuple(values)


def mat_vec(matrix: tuple[tuple[int, ...], ...], vector: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sum(matrix[row][column] * vector[column] for column in range(4)) for row in range(4))


def mat_mul(left: tuple[tuple[int, ...], ...], right: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(sum(left[row][middle] * right[middle][column] for middle in range(4)) for column in range(4))
        for row in range(4)
    )


def mat_pow(exponent: int) -> tuple[tuple[int, ...], ...]:
    assert exponent >= 0
    result = tuple(tuple(1 if row == column else 0 for column in range(4)) for row in range(4))
    base = M
    while exponent:
        if exponent & 1:
            result = mat_mul(result, base)
        base = mat_mul(base, base)
        exponent >>= 1
    return result


def add_rows(
    equations: list[list[int]], coefficients: list[int], constant: int, prime: int
) -> None:
    equations.append([entry % prime for entry in coefficients] + [constant % prime])


def is_consistent(equations: list[list[int]], variables: int, prime: int) -> bool:
    rows = [row[:] for row in equations]
    pivot_row = 0
    for column in range(variables):
        pivot = next((row for row in range(pivot_row, len(rows)) if rows[row][column] % prime), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        inverse = pow(rows[pivot_row][column], -1, prime)
        rows[pivot_row] = [entry * inverse % prime for entry in rows[pivot_row]]
        for row in range(len(rows)):
            if row == pivot_row or not rows[row][column]:
                continue
            factor = rows[row][column]
            rows[row] = [
                (rows[row][index] - factor * rows[pivot_row][index]) % prime
                for index in range(variables + 1)
            ]
        pivot_row += 1
    return all(any(row[column] for column in range(variables)) or row[-1] == 0 for row in rows)


def exponent_vector(n_index: int, j_index: int, orientation: int) -> tuple[int, ...]:
    target = mat_vec(mat_pow(j_index), (orientation, 0, 0, 0))
    mq = mat_vec(M, Q_AB)
    mnq = mat_vec(mat_pow(n_index), Q_AB)
    right = tuple(target[index] + mq[index] - mnq[index] for index in range(4))
    return mat_vec(MI_INV, right)


def character_value(character: tuple[int, ...], exponents: tuple[int, ...], prime: int) -> int:
    value = 1
    for scalar, exponent in zip(character, exponents):
        value = value * pow(scalar, exponent, prime) % prime
    return value


def system_is_solvable(
    prime: int,
    characters: tuple[tuple[int, ...], ...],
    jacobians: tuple[tuple[tuple[int, ...], ...], ...],
    q_orbit: tuple[tuple[tuple[int, tuple[int, ...]], ...], ...],
    target_orbit: tuple[tuple[tuple[int, tuple[int, ...]], ...], ...],
    n_index: int,
    j_index: int,
    orientation: int,
) -> bool:
    length = len(characters)
    variables = 8 * length
    q_inverse_phi = transform_data(
        tuple(inv_affine(value, prime) for value in q_orbit[0]),
        jacobians,
        prime,
    )
    r_data = q_orbit[n_index]
    target_data = target_orbit[j_index]
    if orientation == -1:
        target_data = tuple(inv_affine(value, prime) for value in target_data)
    w_exponents = exponent_vector(n_index, j_index, orientation)
    w_scalars = tuple(character_value(character, w_exponents, prime) for character in characters)

    for conjugator_exponents in product(range(prime - 1), repeat=4):
        conjugator_scalars = tuple(
            character_value(character, conjugator_exponents, prime)
            for character in characters
        )
        equations: list[list[int]] = []
        for index, character in enumerate(characters):
            next_index = (index + 1) % length
            w_offset = 4 * index
            next_w_offset = 4 * next_index
            k_offset = 4 * length + 4 * index

            coefficients = [0] * variables
            for coordinate in range(4):
                coefficients[w_offset + coordinate] = character[coordinate] - 1
            add_rows(equations, coefficients, w_scalars[index] - 1, prime)

            coefficients = [0] * variables
            for coordinate in range(4):
                coefficients[k_offset + coordinate] = character[coordinate] - 1
            add_rows(equations, coefficients, conjugator_scalars[index] - 1, prime)

            sa, va = q_inverse_phi[index]
            s1 = w_scalars[next_index]
            sr, vr = r_data[index]
            st, vt = target_data[index]
            sc = sa * s1 * sr * pow(w_scalars[index], -1, prime) % prime
            if sc != st:
                break
            for coordinate in range(4):
                coefficients = [0] * variables
                for source in range(4):
                    coefficients[next_w_offset + source] += sa * jacobians[index][source][coordinate]
                coefficients[w_offset + coordinate] -= sc
                coefficients[k_offset + coordinate] -= 1 - st
                constant = (
                    conjugator_scalars[index] * vt[coordinate]
                    - va[coordinate]
                    - sa * s1 * vr[coordinate]
                )
                add_rows(equations, coefficients, constant, prime)
        else:
            if is_consistent(equations, variables, prime):
                return True
    return False


def relaxed_system_is_solvable(
    prime: int,
    characters: tuple[tuple[int, ...], ...],
    jacobians: tuple[tuple[tuple[int, ...], ...], ...],
    q_orbit: tuple[tuple[tuple[int, tuple[int, ...]], ...], ...],
    target_orbit: tuple[tuple[tuple[int, tuple[int, ...]], ...], ...],
    n_index: int,
    j_index: int,
    orientation: int,
) -> bool:
    length = len(characters)
    variables = 9 * length
    q_inverse_phi = transform_data(
        tuple(inv_affine(value, prime) for value in q_orbit[0]),
        jacobians,
        prime,
    )
    r_data = q_orbit[n_index]
    target_data = target_orbit[j_index]
    if orientation == -1:
        target_data = tuple(inv_affine(value, prime) for value in target_data)
    w_exponents = exponent_vector(n_index, j_index, orientation)
    w_scalars = tuple(character_value(character, w_exponents, prime) for character in characters)
    equations: list[list[int]] = []
    for index, character in enumerate(characters):
        next_index = (index + 1) % length
        w_offset = 4 * index
        next_w_offset = 4 * next_index
        k_offset = 4 * length + 4 * index
        k_scalar_offset = 8 * length + index

        coefficients = [0] * variables
        for coordinate in range(4):
            coefficients[w_offset + coordinate] = character[coordinate] - 1
        add_rows(equations, coefficients, w_scalars[index] - 1, prime)

        coefficients = [0] * variables
        for coordinate in range(4):
            coefficients[k_offset + coordinate] = character[coordinate] - 1
        coefficients[k_scalar_offset] = -1
        add_rows(equations, coefficients, -1, prime)

        sa, va = q_inverse_phi[index]
        s1 = w_scalars[next_index]
        sr, vr = r_data[index]
        st, vt = target_data[index]
        sc = sa * s1 * sr * pow(w_scalars[index], -1, prime) % prime
        if sc != st:
            return False
        for coordinate in range(4):
            coefficients = [0] * variables
            for source in range(4):
                coefficients[next_w_offset + source] += sa * jacobians[index][source][coordinate]
            coefficients[w_offset + coordinate] -= sc
            coefficients[k_offset + coordinate] -= 1 - st
            coefficients[k_scalar_offset] -= vt[coordinate]
            constant = -va[coordinate] - sa * s1 * vr[coordinate]
            add_rows(equations, coefficients, constant, prime)
    return is_consistent(equations, variables, prime)


def scan_prime_relaxed(prime: int) -> None:
    for orbit_number, characters in enumerate(character_orbits(prime)):
        if all(all(value == 1 for value in character) for character in characters):
            continue
        jacobians = tuple(jacobian(character, prime) for character in characters)
        q_orbit = data_orbit(Q, characters, jacobians, prime)
        target_orbit = data_orbit((1,), characters, jacobians, prime)
        print(
            f"relaxed p={prime} orbit={orbit_number} chars={len(characters)} "
            f"q_period={len(q_orbit)} target_period={len(target_orbit)}",
            flush=True,
        )
        for n_index in range(len(q_orbit)):
            for j_index in range(len(target_orbit)):
                for orientation in (1, -1):
                    if not relaxed_system_is_solvable(
                        prime,
                        characters,
                        jacobians,
                        q_orbit,
                        target_orbit,
                        n_index,
                        j_index,
                        orientation,
                    ):
                        print(
                            "RELAXED OBSTRUCTION",
                            prime,
                            orbit_number,
                            n_index,
                            j_index,
                            orientation,
                            flush=True,
                        )
                        return
    print(f"relaxed p={prime} no obstruction", flush=True)


def scan_prime(prime: int) -> None:
    for orbit_number, characters in enumerate(character_orbits(prime)):
        if all(all(value == 1 for value in character) for character in characters):
            continue
        jacobians = tuple(jacobian(character, prime) for character in characters)
        q_orbit = data_orbit(Q, characters, jacobians, prime)
        target_orbit = data_orbit((1,), characters, jacobians, prime)
        print(
            f"p={prime} orbit={orbit_number} chars={len(characters)} "
            f"q_period={len(q_orbit)} target_period={len(target_orbit)}",
            flush=True,
        )
        for n_index in range(len(q_orbit)):
            for j_index in range(len(target_orbit)):
                for orientation in (1, -1):
                    if not system_is_solvable(
                        prime,
                        characters,
                        jacobians,
                        q_orbit,
                        target_orbit,
                        n_index,
                        j_index,
                        orientation,
                    ):
                        print(
                            "OBSTRUCTION",
                            prime,
                            orbit_number,
                            n_index,
                            j_index,
                            orientation,
                            flush=True,
                        )
                        return
    print(f"p={prime} no obstruction", flush=True)


def self_check() -> None:
    for prime in (3, 5):
        for characters in character_orbits(prime):
            jacobians = tuple(jacobian(character, prime) for character in characters)
            direct = tuple(evaluate(PHI[1], character, prime) for character in characters)
            transformed = transform_data(
                tuple(evaluate((1,), character, prime) for character in characters),
                jacobians,
                prime,
            )
            assert direct == transformed
    assert mat_mul(tuple(tuple(M[row][column] - (row == column) for column in range(4)) for row in range(4)), MI_INV) == tuple(
        tuple(1 if row == column else 0 for column in range(4)) for row in range(4)
    )


if __name__ == "__main__":
    self_check()
    scan_prime(3)
