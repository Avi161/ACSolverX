from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256


BOUNDARY_WORDS = (
    "yyXyyXyyXyX",
    "xxxYYYY",
    "xxxYYYY",
    "xxxYYYY",
    "yxyXYX",
    "yxyXYX",
    "yxyXYX",
    "yxyXYX",
    "yxyXYX",
)

PAIRS = [
    (0, 31), (1, 30), (2, 45), (3, 23), (4, 22), (5, 57), (6, 15),
    (7, 14), (8, 13), (9, 42), (10, 25), (11, 37), (12, 43), (16, 56),
    (17, 32), (18, 49), (19, 55), (20, 59), (21, 58), (24, 44),
    (26, 41), (27, 53), (28, 52), (29, 46), (33, 61), (34, 60),
    (35, 39), (36, 38), (40, 54), (47, 51), (48, 50),
]


@dataclass(frozen=True)
class FatgraphCertificate:
    positions: int
    edges: int
    vertices: int
    boundaries: int
    euler_characteristic: int
    genus: int
    connected: bool
    pair_sha256: str


def cycle_count(permutation: tuple[int, ...]) -> int:
    seen = set()
    count = 0
    for start in range(len(permutation)):
        if start in seen:
            continue
        count += 1
        current = start
        while current not in seen:
            seen.add(current)
            current = permutation[current]
    return count


def verify_certificate() -> FatgraphCertificate:
    boundary = "".join(BOUNDARY_WORDS)
    positions = len(boundary)
    paired_positions = [position for pair in PAIRS for position in pair]
    assert sorted(paired_positions) == list(range(positions))
    inverse_letter = {"x": "X", "X": "x", "y": "Y", "Y": "y"}
    assert all(boundary[right] == inverse_letter[boundary[left]] for left, right in PAIRS)

    sigma = list(range(positions))
    offset = 0
    for word in BOUNDARY_WORDS:
        for index in range(len(word)):
            sigma[offset + index] = offset + (index + 1) % len(word)
        offset += len(word)

    tau = list(range(positions))
    for left, right in PAIRS:
        tau[left] = right
        tau[right] = left

    vertex_permutation = tuple(sigma[tau[position]] for position in range(positions))
    vertices = cycle_count(vertex_permutation)
    edges = len(PAIRS)
    boundaries = len(BOUNDARY_WORDS)
    euler_characteristic = vertices - edges
    genus_numerator = 2 - boundaries - euler_characteristic
    assert genus_numerator % 2 == 0
    genus = genus_numerator // 2

    orbit = {0}
    frontier = [0]
    while frontier:
        position = frontier.pop()
        for following in (sigma[position], tau[position]):
            if following not in orbit:
                orbit.add(following)
                frontier.append(following)
    connected = len(orbit) == positions

    return FatgraphCertificate(
        positions=positions,
        edges=edges,
        vertices=vertices,
        boundaries=boundaries,
        euler_characteristic=euler_characteristic,
        genus=genus,
        connected=connected,
        pair_sha256=sha256(repr(PAIRS).encode()).hexdigest(),
    )


if __name__ == "__main__":
    print(verify_certificate())
