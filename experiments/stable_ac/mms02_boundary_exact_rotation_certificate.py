"""Complete compatible-rotation check for one exact boundary presentation."""

from collections import Counter
from dataclasses import dataclass
from itertools import permutations, product
from math import factorial

from experiments.stable_ac.thickenable.neuwirth_rank3_rigid_solver import _build_link_data

EXACT_WORDS = ("txTZ", "tzTZZxZ", "zzXZt")
EXPECTED_DEGREES = (3, 3, 8, 8, 5, 5)
EXPECTED_HISTOGRAM = {2: 115836, 4: 109814, 6: 15840, 8: 424, 10: 6}
EXPECTED_BUDGET = 241920


def exact_link_data():
    data = _build_link_data(EXACT_WORDS)
    if len(data.A) != 32 or len(data.B) != 32:
        raise AssertionError("the exact boundary dart count drifted")
    stars = tuple(data.vertex_darts[vertex] for vertex in range(6))
    if sorted(dart for star in stars for dart in star) != list(range(32)):
        raise AssertionError("the boundary stars do not partition the darts")
    for involution in (data.A, data.B):
        if any(mate == dart or not 0 <= mate < 32 or involution[mate] != dart
               for dart, mate in enumerate(involution)):
            raise AssertionError("the boundary pairing is not a fixed-point-free involution")
    if tuple(map(len, stars)) != EXPECTED_DEGREES:
        raise AssertionError("the boundary germ degrees drifted")
    if any(set(data.B[dart] for dart in stars[vertex]) != set(stars[vertex ^ 1])
           for vertex in range(6)):
        raise AssertionError("B does not pair opposite boundary stars")
    neighbors = [set() for _ in range(6)]
    for dart, mate in enumerate(data.A):
        left, right = data.germ[dart], data.germ[mate]
        if left == right:
            raise AssertionError("the exact boundary support has a loop")
        neighbors[left].add(right)
    reached, pending = {0}, [0]
    while pending:
        for neighbor in neighbors[pending.pop()] - reached:
            reached.add(neighbor)
            pending.append(neighbor)
    if reached != set(range(6)):
        raise AssertionError("the simple boundary support is disconnected")
    return data


def verify_rotations(data, rotations: tuple[tuple[int, ...], ...]) -> tuple[int, ...]:
    if len(rotations) != 6:
        raise AssertionError("six boundary rotations are required")
    dart_count = len(data.A)
    sigma = [-1] * dart_count
    predecessor = [-1] * dart_count
    for vertex, rotation in enumerate(rotations):
        if len(rotation) != len(data.vertex_darts[vertex]) or set(rotation) != set(data.vertex_darts[vertex]):
            raise AssertionError("the rotation does not partition its exact star")
        for index, dart in enumerate(rotation):
            sigma[dart] = rotation[(index + 1) % len(rotation)]
            predecessor[dart] = rotation[index - 1]
    if any(sigma[data.B[dart]] != data.B[predecessor[dart]] for dart in range(dart_count)):
        raise AssertionError("the negative boundary order is not B-reversed")
    return tuple(sigma)


def enumerate_face_histogram(data) -> tuple[dict[int, int], int]:
    dart_count = len(data.A)
    choices = []
    for vertex in (0, 2, 4):
        star = tuple(sorted(data.vertex_darts[vertex]))
        choices.append(tuple((star[0],) + tail for tail in permutations(star[1:])))
    histogram = Counter()
    considered = 0
    for positives in product(*choices):
        sigma = [-1] * dart_count
        for positive in positives:
            negative = tuple(data.B[dart] for dart in reversed(positive))
            for rotation in (positive, negative):
                for index, dart in enumerate(rotation):
                    sigma[dart] = rotation[(index + 1) % len(rotation)]
        unseen, faces = (1 << dart_count) - 1, 0
        while unseen:
            dart = (unseen & -unseen).bit_length() - 1
            faces += 1
            while unseen & (1 << dart):
                unseen &= ~(1 << dart)
                dart = sigma[data.A[dart]]
        histogram[faces] += 1
        considered += 1
    return dict(sorted(histogram.items())), considered


@dataclass(frozen=True)
class ExactRotationDecision:
    words: tuple[str, str, str]
    dart_count: int
    degrees: tuple[int, ...]
    scheme_budget: int
    schemes_considered: int
    face_histogram: dict[int, int]
    spherical_face_count: int
    maximum_euler_characteristic: int
    exhaustive: bool
    ac_invariant_claimed: bool
    verdict: str


def decide_boundary_exact_rotations() -> ExactRotationDecision:
    data = exact_link_data()
    budget = 1
    for vertex in (0, 2, 4):
        budget *= factorial(len(data.vertex_darts[vertex]) - 1)
    histogram, considered = enumerate_face_histogram(data)
    if budget != EXPECTED_BUDGET or considered != budget:
        raise AssertionError("the complete boundary rotation budget drifted")
    if histogram != EXPECTED_HISTOGRAM:
        raise AssertionError("the exact boundary face histogram drifted")
    maximum_euler = 6 - 16 + max(histogram)
    if histogram.get(12, 0) or maximum_euler != 0:
        raise AssertionError("the exact boundary spherical-rotation result drifted")
    return ExactRotationDecision(
        EXACT_WORDS, 32, EXPECTED_DEGREES, budget, considered, histogram, 12,
        maximum_euler, True, False, "EXACT_BOUNDARY_COMPLEX_HAS_NO_COMPATIBLE_SPHERICAL_ROTATION",
    )
