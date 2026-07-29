from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256

try:
    from experiments.stable_ac import depth4_period_two_cyclic_degree_two_obstruction_certificate as cyclic
    from experiments.stable_ac import depth4_period_two_degree_two_escape_certificate as escape
    from experiments.stable_ac import depth4_period_two_eight_direction_obstruction_certificate as eight
    from experiments.stable_ac import depth4_period_two_eleven_direction_obstruction_certificate as eleven
    from experiments.stable_ac import depth4_period_two_five_direction_obstruction_certificate as five
    from experiments.stable_ac import depth4_period_two_nine_direction_obstruction_certificate as nine
    from experiments.stable_ac import depth4_period_two_remote_syzygy_certificate as remote
    from experiments.stable_ac import depth4_period_two_seven_direction_obstruction_certificate as seven
    from experiments.stable_ac import depth4_period_two_six_direction_obstruction_certificate as six
    from experiments.stable_ac import depth4_period_two_source_flow_certificate as source
    from experiments.stable_ac import depth4_period_two_ten_direction_obstruction_certificate as ten
except ModuleNotFoundError:
    import depth4_period_two_cyclic_degree_two_obstruction_certificate as cyclic
    import depth4_period_two_degree_two_escape_certificate as escape
    import depth4_period_two_eight_direction_obstruction_certificate as eight
    import depth4_period_two_eleven_direction_obstruction_certificate as eleven
    import depth4_period_two_five_direction_obstruction_certificate as five
    import depth4_period_two_nine_direction_obstruction_certificate as nine
    import depth4_period_two_remote_syzygy_certificate as remote
    import depth4_period_two_seven_direction_obstruction_certificate as seven
    import depth4_period_two_six_direction_obstruction_certificate as six
    import depth4_period_two_source_flow_certificate as source
    import depth4_period_two_ten_direction_obstruction_certificate as ten


lift = escape.lift
REMOTE_FOUR_POINT_ACTION = ((0, 1, 3, 2), (1, 2, 0, 3))


def projected_wedge(
    kernel_word: tuple[tuple[lift.Word, int], ...],
    action: tuple[tuple[int, ...], tuple[int, ...]],
    prime: int = 2,
) -> tuple[int, ...]:
    """Stream a kernel word into the oriented projected wedge coordinates."""
    size = len(action[0])
    linear = [0] * size
    quadratic = [[0] * size for _ in range(size)]
    for module_vertex, sign in kernel_word:
        target = remote.point_image(module_vertex, 0, *action)
        for source_point, coefficient in enumerate(linear):
            quadratic[source_point][target] += coefficient * sign
        if sign == -1:
            quadratic[target][target] += 1
        linear[target] += sign
    assert all(value % prime == 0 for value in linear)

    result = []
    for left in range(size):
        for right in range(left + 1, size):
            assert (quadratic[left][right] + quadratic[right][left]) % prime == 0
            result.append(quadratic[left][right] % prime)
    return tuple(result)


def _paired_bits(vector: tuple[int, ...], covectors: tuple[tuple[int, ...], ...]) -> tuple[int, ...]:
    return tuple(
        sum(coefficient * coordinate for coefficient, coordinate in zip(covector, vector)) % 2
        for covector in covectors
    )


def projected_fourteen_bits(
    kernel_word: tuple[tuple[lift.Word, int], ...],
) -> tuple[int, ...]:
    """The Result 152–157 finite bits, ordered after Phi_infinity."""
    result_152 = (
        sum(projected_wedge(kernel_word, ((0, 2, 1), (1, 2, 0)))) % 2,
        sum(projected_wedge(kernel_word, REMOTE_FOUR_POINT_ACTION)) % 2,
        sum(projected_wedge(kernel_word, cyclic.CYCLIC_ACTION)) % 2,
        sum(projected_wedge(kernel_word, five.NEW_THREE_POINT_ACTION)) % 2,
        sum(projected_wedge(kernel_word, six.TWO_POINT_ACTION)) % 2,
    )
    identity = projected_wedge(kernel_word, seven.IDENTITY_FOUR_POINT_ACTION)
    twisted = projected_wedge(kernel_word, seven.TWISTED_FOUR_POINT_ACTION)
    result_153 = (
        *_paired_bits(identity, seven.IDENTITY_FOUR_POINT_COVECTORS),
        *_paired_bits(twisted, (seven.TWISTED_FOUR_POINT_COVECTOR,)),
    )
    result_154 = _paired_bits(
        projected_wedge(kernel_word, eight.NEW_FOUR_POINT_ACTION),
        (eight.NEW_FOUR_POINT_COVECTOR,),
    )
    result_155 = _paired_bits(
        projected_wedge(kernel_word, nine.INVERSE_FOUR_POINT_ACTION),
        (nine.INVERSE_FOUR_POINT_COVECTOR,),
    )
    result_156 = _paired_bits(
        projected_wedge(kernel_word, ten.FIVE_POINT_ACTION),
        ten.FIVE_POINT_COVECTORS,
    )
    result_157 = _paired_bits(
        projected_wedge(kernel_word, eleven.NEW_ACTION),
        eleven.NEW_COVECTORS,
    )
    bits = (*result_152, *result_153, *result_154, *result_155, *result_156, *result_157)
    assert len(bits) == 14
    return bits


def _direct_fourteen_bits(value: escape.WedgeVector) -> tuple[int, ...]:
    def projected(action: tuple[tuple[int, ...], tuple[int, ...]]) -> tuple[int, ...]:
        return remote.finite_wedge_vector(value, *action)

    result_152 = (
        sum(projected(((0, 2, 1), (1, 2, 0)))) % 2,
        sum(projected(REMOTE_FOUR_POINT_ACTION)) % 2,
        sum(projected(cyclic.CYCLIC_ACTION)) % 2,
        sum(projected(five.NEW_THREE_POINT_ACTION)) % 2,
        sum(projected(six.TWO_POINT_ACTION)) % 2,
    )
    result_153 = (
        *_paired_bits(projected(seven.IDENTITY_FOUR_POINT_ACTION), seven.IDENTITY_FOUR_POINT_COVECTORS),
        *_paired_bits(projected(seven.TWISTED_FOUR_POINT_ACTION), (seven.TWISTED_FOUR_POINT_COVECTOR,)),
    )
    result_154 = _paired_bits(projected(eight.NEW_FOUR_POINT_ACTION), (eight.NEW_FOUR_POINT_COVECTOR,))
    result_155 = _paired_bits(projected(nine.INVERSE_FOUR_POINT_ACTION), (nine.INVERSE_FOUR_POINT_COVECTOR,))
    result_156 = _paired_bits(projected(ten.FIVE_POINT_ACTION), ten.FIVE_POINT_COVECTORS)
    result_157 = _paired_bits(projected(eleven.NEW_ACTION), eleven.NEW_COVECTORS)
    return (*result_152, *result_153, *result_154, *result_155, *result_156, *result_157)


@dataclass(frozen=True)
class PeriodTwoDepth6L0CensusCertificate:
    max_source_depth: int
    source_vertices: int
    balanced_pairs: int
    projected_direct_fixtures: int
    projected_direct_matches: int
    projected_near_survivors: tuple[tuple[str, str, int, int], ...]
    zero_syndrome_pairs: tuple[tuple[str, str, int], ...]
    census_sha256: str


@lru_cache(maxsize=1)
def depth6_l0_census_certificate() -> PeriodTwoDepth6L0CensusCertificate:
    _, _, _, defect, operators = escape.recurrence_data()
    base = escape.variables_from_entries(lift.CORRECTION)
    assert REMOTE_FOUR_POINT_ACTION == remote.period_two_remote_syzygy_certificate().four_point_action

    matches = 0
    for entries in source.KNOWN_SOURCES:
        direction = source.build_l0_direction(source.source_from_entries(entries)).variables
        residual = escape.corrected_residual(escape.add_variables(base, direction))
        kernel_word = escape.schreier_word(residual)
        streamed = projected_fourteen_bits(kernel_word)
        wedge = escape.degree_two(kernel_word)
        direct = _direct_fourteen_bits(wedge)
        assert streamed == direct == eleven.obstruction_bits(wedge)[1:]
        matches += 1

    records = []
    for vertex in source.source_vertices(6):
        boundary = lift.apply_operator(operators[0], {vertex: 1})
        scalar = source.orbit_sums(boundary)[0]
        assert scalar != 0
        records.append((vertex, scalar))
    records.sort(key=lambda item: (len(item[0]), item[0]))

    digest = sha256()
    balanced_pairs = 0
    near_survivors = []
    zero_syndrome_pairs = []
    for left_index, (left, left_scalar) in enumerate(records):
        for right, right_scalar in records[left_index + 1:]:
            if abs(left_scalar) != abs(right_scalar):
                continue
            right_coefficient = -left_scalar // right_scalar
            assert right_coefficient in (-1, 1)
            direction = source.build_l0_direction({left: 1, right: right_coefficient}).variables
            assert not escape.correction_image(direction, operators)
            variables = escape.add_variables(base, direction)
            assert not lift.add_vectors(defect, escape.correction_image(variables, operators))
            kernel_word = escape.schreier_word(escape.corrected_residual(variables))
            bits = projected_fourteen_bits(kernel_word)
            full_bit = 2
            if not any(bits):
                wedge = escape.degree_two(kernel_word)
                assert bits == _direct_fourteen_bits(wedge) == eleven.obstruction_bits(wedge)[1:]
                full_bit = sum(wedge.values()) % 2
                near_survivors.append((
                    lift.literal(left),
                    lift.literal(right),
                    right_coefficient,
                    full_bit,
                ))
                if not full_bit:
                    zero_syndrome_pairs.append((
                        lift.literal(left),
                        lift.literal(right),
                        right_coefficient,
                    ))
            record = (lift.literal(left), lift.literal(right), right_coefficient, *bits, full_bit)
            digest.update((repr(record) + "\n").encode())
            balanced_pairs += 1

    certificate = PeriodTwoDepth6L0CensusCertificate(
        max_source_depth=6,
        source_vertices=len(records),
        balanced_pairs=balanced_pairs,
        projected_direct_fixtures=len(source.KNOWN_SOURCES),
        projected_direct_matches=matches,
        projected_near_survivors=tuple(near_survivors),
        zero_syndrome_pairs=tuple(zero_syndrome_pairs),
        census_sha256=digest.hexdigest(),
    )
    assert certificate.source_vertices == 127
    assert certificate.balanced_pairs == 4671
    assert certificate.projected_near_survivors == (
        ("TT", "TTTct", 1, 1),
        ("Tctt", "Tctct", 1, 1),
    )
    assert not certificate.zero_syndrome_pairs
    assert certificate.census_sha256 == (
        "02a688c2e0bfd1831202c6b76f8d3af9b4340c71e08d9b1e2efeea59d8301ff3"
    )
    return certificate
