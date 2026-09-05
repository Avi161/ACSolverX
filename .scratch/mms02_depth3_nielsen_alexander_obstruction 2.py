from __future__ import annotations

import sys
from collections import Counter, deque
from itertools import permutations, product
from pathlib import Path
from typing import Any

SCRATCH = Path(__file__).resolve().parent
if str(SCRATCH) not in sys.path:
    sys.path.insert(0, str(SCRATCH))

from mms02_bridge_alexander_filter import (  # noqa: E402
    DELTA,
    apply_images,
    exponent_sum,
    module_coordinate,
)
from mms02_bridge_alexander_filter import (  # noqa: E402
    verify as verify_base_filter,
)
from mms02_wirtinger_repair_checker import (  # noqa: E402
    free_reduce,
    inverse,
    rename_xyz,
    three_generator_descendant,
    token,
)

BASE = ("xzYXyxZXYxyZ", "XyxZXYXyxzXYxy")
KILL_WORDS = ("zYX", "Xyz")
IDENTITY_BASIS = ("x", "y", "z")
MAX_DEPTH = 3

PSI = ("y", "x", "zyX")
ETA_Y = ("x", "zYz", "z")
ETA_Z = ("x", "y", "yZy")
EXPECTED_STABILIZERS = {IDENTITY_BASIS, PSI, ETA_Y, ETA_Z}

EXPECTED_IMAGES = {
    PSI: (
        "yzyXXYxyxYZYXyxxYZ",
        "YxyxYZYXYxyzyXYXyx",
    ),
    ETA_Y: (
        "xyZXzYzxZXZyZxzY",
        "XzYzxZXZyZXzYzxzXZyZxzYz",
    ),
    ETA_Z: (
        "xyZXyxYzYXYxzY",
        "XyxYzYXYXyxyZyXYxy",
    ),
}

EXPECTED_REMAINDERS = {
    PSI: ((2, -3, 1), (-1, 1, 0, -1)),
    ETA_Y: ((-2,), (2, -6, 10, -4)),
    ETA_Z: ((-2, 2, -2), (2, -4, 6, -2)),
}

Permutation = tuple[int, ...]
Operation = tuple[str, int, int, int]


def inverse_rename_xyz(word: str) -> str:
    mapping = {
        "x": token(5),
        "X": token(5, False),
        "y": token(7),
        "Y": token(7, False),
        "z": token(12),
        "Z": token(12, False),
    }
    return "".join(mapping[letter] for letter in word)


def canonical_relator(word: str) -> str:
    word = free_reduce(word)
    while len(word) > 1 and word[0] == word[-1].swapcase():
        word = free_reduce(word[1:-1])
    candidates = []
    for oriented in (word, inverse(word)):
        candidates.extend(
            oriented[index:] + oriented[:index]
            for index in range(len(oriented))
        )
    return min(candidates)


def signed_permutation_stabilizers() -> tuple[tuple[str, str, str], ...]:
    target = sorted(map(canonical_relator, BASE))
    stabilizers = []
    for permutation in permutations("xyz"):
        for signs in product((1, -1), repeat=3):
            images = tuple(
                generator if sign == 1 else generator.upper()
                for generator, sign in zip(permutation, signs)
            )
            transformed = sorted(
                canonical_relator(apply_images(relator, images))
                for relator in BASE
            )
            if transformed == target:
                stabilizers.append(images)
    return tuple(stabilizers)


def elementary_operations() -> tuple[Operation, ...]:
    operations: list[Operation] = []
    for target in range(3):
        operations.append(("I", target, -1, 0))
    for left in range(3):
        for right in range(left + 1, 3):
            operations.append(("S", left, right, 0))
    for target in range(3):
        for source in range(3):
            if target == source:
                continue
            for sign in (1, -1):
                operations.append(("R", target, source, sign))
    assert len(operations) == 18
    return tuple(operations)


def apply_operation(
    basis: tuple[str, str, str],
    operation: Operation,
) -> tuple[str, str, str]:
    result = list(basis)
    kind, first, second, sign = operation
    if kind == "I":
        result[first] = inverse(result[first])
    elif kind == "S":
        result[first], result[second] = result[second], result[first]
    elif kind == "R":
        source = result[second] if sign == 1 else inverse(result[second])
        result[first] = free_reduce(result[first] + source)
    else:
        raise AssertionError(operation)
    return tuple(result)


def inverse_operation(operation: Operation) -> Operation:
    kind, first, second, sign = operation
    if kind in {"I", "S"}:
        return operation
    if kind == "R":
        return (kind, first, second, -sign)
    raise AssertionError(operation)


def replay_path(
    path: tuple[Operation, ...],
) -> tuple[str, str, str]:
    basis = IDENTITY_BASIS
    for operation in path:
        basis = apply_operation(basis, operation)
    return basis


def inverse_path(
    path: tuple[Operation, ...],
) -> tuple[Operation, ...]:
    return tuple(inverse_operation(operation) for operation in reversed(path))


def nielsen_ball() -> dict[
    tuple[str, str, str],
    tuple[int, tuple[Operation, ...]],
]:
    records = {IDENTITY_BASIS: (0, ())}
    queue = deque([IDENTITY_BASIS])
    operations = elementary_operations()
    while queue:
        basis = queue.popleft()
        depth, path = records[basis]
        if depth == MAX_DEPTH:
            continue
        for operation in operations:
            child = apply_operation(basis, operation)
            if child in records:
                continue
            records[child] = (depth + 1, path + (operation,))
            queue.append(child)
    return records


class A5Model:
    def __init__(self) -> None:
        self.elements = tuple(
            permutation
            for permutation in permutations(range(5))
            if self.parity(permutation) == 0
        )
        self.index = {
            permutation: index
            for index, permutation in enumerate(self.elements)
        }
        self.identity = self.index[tuple(range(5))]
        self.multiply = tuple(
            tuple(
                self.index[
                    tuple(left[right[index]] for index in range(5))
                ]
                for right in self.elements
            )
            for left in self.elements
        )
        inverses = []
        for permutation in self.elements:
            result = [0] * 5
            for index, image in enumerate(permutation):
                result[image] = index
            inverses.append(self.index[tuple(result)])
        self.inverses = tuple(inverses)

    @staticmethod
    def parity(permutation: Permutation) -> int:
        return sum(
            permutation[left] > permutation[right]
            for left in range(5)
            for right in range(left + 1, 5)
        ) % 2

    def evaluate(
        self,
        word: str,
        images: tuple[int, int, int],
    ) -> int:
        result = self.identity
        for letter in word:
            image = images[ord(letter.lower()) - ord("x")]
            if letter.isupper():
                image = self.inverses[image]
            result = self.multiply[result][image]
        return result

    def generated_subgroup(self, generators: tuple[int, ...]) -> set[int]:
        subgroup = {self.identity}
        frontier = [self.identity]
        steps = generators + tuple(self.inverses[value] for value in generators)
        while frontier:
            current = frontier.pop()
            for step in steps:
                child = self.multiply[current][step]
                if child not in subgroup:
                    subgroup.add(child)
                    frontier.append(child)
        return subgroup

    def conjugacy_class(self, element: int) -> set[int]:
        return {
            self.multiply[
                self.multiply[conjugator][element]
            ][self.inverses[conjugator]]
            for conjugator in range(60)
        }


def a5_solutions(
    model: A5Model,
) -> tuple[set[tuple[int, int, int]], set[tuple[int, int, int]]]:
    solutions = {
        images
        for images in product(range(60), repeat=3)
        if model.evaluate(BASE[0], images) == model.identity
        and model.evaluate(BASE[1], images) == model.identity
    }
    epimorphisms = {
        images
        for images in solutions
        if len(model.generated_subgroup(images)) == 60
    }
    return solutions, epimorphisms


def preserves_a5_solution_set(
    model: A5Model,
    solutions: set[tuple[int, int, int]],
    basis: tuple[str, str, str],
) -> bool:
    image_set = {
        tuple(model.evaluate(word, images) for word in basis)
        for images in solutions
    }
    return image_set == solutions


def remainder_mod_delta(
    polynomial: dict[int, int],
) -> tuple[int, ...]:
    if not polynomial:
        return ()
    minimum = min(polynomial)
    coefficients = [
        polynomial.get(power, 0)
        for power in range(minimum, max(polynomial) + 1)
    ]
    while len(coefficients) > len(DELTA) - 1:
        leading = coefficients[-1]
        offset = len(coefficients) - len(DELTA)
        for index, coefficient in enumerate(DELTA):
            coefficients[offset + index] -= leading * coefficient
        while coefficients and coefficients[-1] == 0:
            coefficients.pop()
    while coefficients and coefficients[0] == 0:
        coefficients.pop(0)
    return tuple(coefficients)


def verify() -> dict[str, Any]:
    base_filter = verify_base_filter()
    assert tuple(base_filter["relators"]) == BASE
    z_coordinate = dict(base_filter["module_generator_relation"])
    assert tuple(base_filter["alexander_polynomial"]) == DELTA

    raw_relators, _ = three_generator_descendant(corrected=False)
    renamed = tuple(rename_xyz(word) for word in raw_relators)
    assert renamed == BASE
    for raw, word in zip(raw_relators, renamed):
        assert inverse_rename_xyz(word) == raw
        assert rename_xyz(inverse_rename_xyz(word)) == word

    assert signed_permutation_stabilizers() == (IDENTITY_BASIS,)

    model = A5Model()
    solutions, epimorphisms = a5_solutions(model)
    assert len(solutions) == 180
    assert len(epimorphisms) == 120
    diagonal = {(element, element, element) for element in range(60)}
    assert solutions - epimorphisms == diagonal

    records = nielsen_ball()
    depth_histogram = Counter(depth for depth, _ in records.values())
    assert len(records) == 2527
    assert depth_histogram == Counter({0: 1, 1: 18, 2: 218, 3: 2290})

    stabilizers = {
        basis
        for basis in records
        if preserves_a5_solution_set(model, solutions, basis)
    }
    assert stabilizers == EXPECTED_STABILIZERS

    candidate_records = {}
    for basis in (PSI, ETA_Y, ETA_Z):
        depth, path = records[basis]
        assert depth == 3
        assert replay_path(path) == basis
        assert replay_path(path + inverse_path(path)) == IDENTITY_BASIS
        assert tuple(apply_images(word, basis) for word in basis) == IDENTITY_BASIS
        assert tuple(exponent_sum(word) for word in basis) == (1, 1, 1)

        transformed = tuple(apply_images(relator, basis) for relator in BASE)
        assert transformed == EXPECTED_IMAGES[basis]
        raw_classes = tuple(
            module_coordinate(word, z_coordinate)
            for word in transformed
        )
        remainders = tuple(
            remainder_mod_delta(polynomial)
            for polynomial in raw_classes
        )
        assert remainders == EXPECTED_REMAINDERS[basis]
        assert all(remainder for remainder in remainders)
        candidate_records[basis] = {
            "depth": depth,
            "path": path,
            "transformed_relators": transformed,
            "remainders": remainders,
        }

    witness = {
        "x": (0, 1, 3, 4, 2),
        "y": (0, 2, 3, 1, 4),
        "z": (2, 0, 1, 3, 4),
    }
    witness_indices = tuple(model.index[witness[generator]] for generator in "xyz")
    assert witness_indices in epimorphisms
    short_image = model.evaluate(KILL_WORDS[0], witness_indices)
    published_image = model.evaluate(KILL_WORDS[1], witness_indices)
    assert short_image not in model.conjugacy_class(published_image)
    assert short_image not in model.conjugacy_class(
        model.inverses[published_image]
    )

    return {
        "relators": BASE,
        "kill_words": KILL_WORDS,
        "signed_permutation_stabilizers": signed_permutation_stabilizers(),
        "nielsen_alphabet_size": len(elementary_operations()),
        "maximum_depth": MAX_DEPTH,
        "nielsen_map_count": len(records),
        "depth_histogram": dict(sorted(depth_histogram.items())),
        "a5_solution_count": len(solutions),
        "a5_epimorphism_count": len(epimorphisms),
        "a5_diagonal_count": len(diagonal),
        "a5_solution_stabilizers": tuple(sorted(stabilizers)),
        "candidate_records": candidate_records,
    }


def main() -> None:
    result = verify()
    print("PASS: complete depth-3 Nielsen/Alexander obstruction")
    print("base", result["relators"])
    print("kill_words", result["kill_words"])
    print(
        "Nielsen ball",
        result["nielsen_map_count"],
        result["depth_histogram"],
    )
    print(
        "A5 solutions",
        result["a5_solution_count"],
        "epimorphisms",
        result["a5_epimorphism_count"],
        "diagonal",
        result["a5_diagonal_count"],
    )
    for basis, record in result["candidate_records"].items():
        print("candidate", basis)
        print("  relators", record["transformed_relators"])
        print("  remainders", record["remainders"])


if __name__ == "__main__":
    main()
