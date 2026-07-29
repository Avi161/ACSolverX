from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

try:
    from experiments.stable_ac import depth4_period_two_degree_two_escape_certificate as escape
    from experiments.stable_ac import depth4_period_two_eight_direction_obstruction_certificate as eight
    from experiments.stable_ac import depth4_period_two_eleven_direction_obstruction_certificate as eleven
    from experiments.stable_ac import depth4_period_two_nine_direction_obstruction_certificate as nine
    from experiments.stable_ac import depth4_period_two_phi4_escape_certificate as phi4
    from experiments.stable_ac import depth4_period_two_seven_direction_obstruction_certificate as seven
    from experiments.stable_ac import depth4_period_two_subgroup_rewrite_certificate as rewrite
    from experiments.stable_ac import depth4_period_two_ten_direction_obstruction_certificate as ten
except ModuleNotFoundError:
    import depth4_period_two_degree_two_escape_certificate as escape
    import depth4_period_two_eight_direction_obstruction_certificate as eight
    import depth4_period_two_eleven_direction_obstruction_certificate as eleven
    import depth4_period_two_nine_direction_obstruction_certificate as nine
    import depth4_period_two_phi4_escape_certificate as phi4
    import depth4_period_two_seven_direction_obstruction_certificate as seven
    import depth4_period_two_subgroup_rewrite_certificate as rewrite
    import depth4_period_two_ten_direction_obstruction_certificate as ten


lift = escape.lift

C_ACTION = (1, 0, 3, 2)
T_ACTION = (0, 2, 3, 1)
T_INVERSE = (0, 3, 1, 2)


def compose(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(right[left[index]] for index in range(len(left)))


def vertex_action_class(word: lift.Word) -> tuple[int, ...]:
    action = tuple(range(4))
    for letter in word:
        letter_action = (
            C_ACTION
            if abs(letter) == lift.C
            else T_ACTION
            if letter == lift.T
            else T_INVERSE
        )
        action = compose(action, letter_action)
    return min(action, compose(action, C_ACTION))


def source_vertices(max_depth: int) -> tuple[lift.Word, ...]:
    seen = {lift.c_vertex(()): 0}
    frontier = {lift.c_vertex(())}
    for depth in range(1, max_depth + 1):
        next_frontier: set[lift.Word] = set()
        for vertex in frontier:
            for letter in (lift.C, lift.T, -lift.T):
                target = lift.c_vertex(lift.quotient_multiply((letter,), vertex))
                if target not in seen:
                    seen[target] = depth
                    next_frontier.add(target)
        frontier = next_frontier
    return tuple(sorted(seen, key=lambda word: (seen[word], len(word), word)))


def orbit_component(word: lift.Word) -> int:
    return 0 if phi4.orbit_state(word) in (0, 1) else 1


def orbit_sums(boundary: lift.ModuleVector) -> tuple[int, int]:
    sums = [0, 0]
    for word, coefficient in boundary.items():
        sums[orbit_component(word)] += coefficient
    return tuple(sums)  # type: ignore[return-value]


def paired_boundaries(
    boundary: lift.ModuleVector,
) -> tuple[tuple[lift.Word, lift.Word], ...] | None:
    by_component: dict[int, dict[int, list[lift.Word]]] = defaultdict(
        lambda: {1: [], -1: []},
    )
    for word, coefficient in boundary.items():
        sign = 1 if coefficient > 0 else -1
        by_component[orbit_component(word)][sign].extend([word] * abs(coefficient))
    if any(
        len(entries[1]) != len(entries[-1])
        for entries in by_component.values()
    ):
        return None
    return tuple(
        (negative, positive)
        for component in sorted(by_component)
        for negative, positive in zip(
            sorted(by_component[component][-1], key=lambda word: (len(word), word)),
            sorted(by_component[component][1], key=lambda word: (len(word), word)),
        )
    )


@dataclass(frozen=True)
class SourceFlowDirection:
    source: tuple[tuple[str, int], ...]
    paths: tuple[tuple[str, str, str], ...]
    variables: escape.ModuleVariables


def source_entries(source: lift.ModuleVector) -> tuple[tuple[str, int], ...]:
    return tuple(
        (lift.literal(word), coefficient)
        for word, coefficient in sorted(source.items(), key=lambda item: (len(item[0]), item[0]))
    )


def build_l0_direction_from_pairs(
    source: dict[lift.Word, int],
    pairs: tuple[tuple[lift.Word, lift.Word], ...],
) -> SourceFlowDirection:
    _, _, _, _, operators = escape.recurrence_data()
    normalized_source = lift.add_vectors(source)
    boundary = lift.apply_operator(operators[0], normalized_source)
    assert orbit_sums(boundary) == (0, 0)
    paired_boundary: dict[lift.Word, int] = defaultdict(int)
    for start, end in pairs:
        paired_boundary[start] -= 1
        paired_boundary[end] += 1
    assert lift.add_vectors(paired_boundary) == boundary

    generators = phi4.forest_generators(operators)
    generators.update({
        name.lower(): lift.quotient_inverse(word)
        for name, word in tuple(generators.items())
    })
    variables: list[dict[lift.Word, int]] = [defaultdict(int) for _ in range(5)]
    variables[0].update(normalized_source)
    paths: list[tuple[str, str, str]] = []
    for start, end in pairs:
        path = rewrite.path_between(start, end)
        current = start
        for name in path:
            target = escape.act(generators[name], current)
            if name == "A":
                variables[4][current] -= 1
            elif name == "a":
                variables[4][target] += 1
            elif name == "B":
                variables[2][current] += 1
            elif name == "b":
                variables[2][target] -= 1
            elif name == "G":
                variables[3][lift.quotient_multiply((-lift.T,), current)] -= 1
            elif name == "g":
                variables[3][lift.quotient_multiply((-lift.T,), target)] += 1
            else:
                raise AssertionError(f"unknown forest edge {name!r}")
            current = target
        assert current == end
        paths.append((lift.literal(start), path, lift.literal(end)))
    direction = tuple(lift.clean_vector(variable) for variable in variables)
    assert not escape.correction_image(direction, operators)
    return SourceFlowDirection(source_entries(normalized_source), tuple(paths), direction)


def build_l0_direction(source: dict[lift.Word, int]) -> SourceFlowDirection:
    _, _, _, _, operators = escape.recurrence_data()
    normalized_source = lift.add_vectors(source)
    boundary = lift.apply_operator(operators[0], normalized_source)
    assert orbit_sums(boundary) == (0, 0)
    pairs = paired_boundaries(boundary)
    assert pairs is not None
    return build_l0_direction_from_pairs(normalized_source, pairs)


KNOWN_SOURCES = (
    (("T", 1), ("ttttct", 1)),
    (("T", 1), ("TTct", 1)),
    (("TT", 1), ("tcTct", 1)),
    (("cT", 1), ("TcTTT", 1)),
    (("TTcttt", 1), ("cTcTct", 1)),
)


def source_from_entries(entries: tuple[tuple[str, int], ...]) -> lift.ModuleVector:
    return {
        lift.parse_quotient(label): coefficient
        for label, coefficient in entries
    }


@dataclass(frozen=True)
class PeriodTwoSourceFlowCertificate:
    vertex_action_classes: int
    representative_signatures: tuple[tuple[str, tuple[int, int], tuple[int, int]], ...]
    known_sources: tuple[tuple[tuple[str, int], ...], ...]
    known_reconstructions: int


def source_flow_certificate() -> PeriodTwoSourceFlowCertificate:
    _, _, _, _, operators = escape.recurrence_data()
    representatives: dict[tuple[int, ...], lift.Word] = {}
    for vertex in source_vertices(12):
        representatives.setdefault(vertex_action_class(vertex), vertex)
    signatures = tuple(
        (
            lift.literal(vertex),
            orbit_sums(lift.apply_operator(operators[0], {vertex: 1})),
            orbit_sums(lift.apply_operator(operators[1], {vertex: 1})),
        )
        for _, vertex in sorted(
            representatives.items(), key=lambda item: (len(item[1]), item[1]),
        )
    )
    assert len(representatives) == 6

    expected_directions = (
        seven.reconstruct_from_forest_paths(operators),
        eight.reconstruct_from_forest_paths(operators),
        nine.reconstruct_from_forest_paths(operators),
        ten.reconstruct_from_forest_paths(operators),
        eleven.reconstruct_from_forest_paths(operators),
    )
    reconstructions = tuple(
        build_l0_direction(source_from_entries(source))
        for source in KNOWN_SOURCES
    )
    assert tuple(direction.variables for direction in reconstructions) == expected_directions
    return PeriodTwoSourceFlowCertificate(
        vertex_action_classes=len(representatives),
        representative_signatures=signatures,
        known_sources=KNOWN_SOURCES,
        known_reconstructions=len(reconstructions),
    )
