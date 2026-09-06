"""Explicit presentation complexes, staircase prisms, and recorded collapses."""

from dataclasses import asdict, dataclass
from itertools import combinations
import json
import random

AK3_WORDS = ("xxxYYYY", "xyxYXY")
SEED = 20260906


def face_closure(simplices):
    return {face for simplex in simplices for size in range(1, len(simplex) + 1)
            for face in combinations(tuple(sorted(set(simplex))), size)}


def f_vector(complex_faces):
    if not complex_faces:
        return ()
    return tuple(sum(len(face) == size for face in complex_faces)
                 for size in range(1, max(map(len, complex_faces)) + 1))


def rose_word_walk(word):
    cycles = {"x": (0, 1, 2, 0), "y": (0, 3, 4, 0)}
    walk = [0]
    for letter in word:
        cycle = cycles[letter.lower()]
        if letter.isupper():
            cycle = cycle[::-1]
        walk.extend(cycle[1:])
    return tuple(walk)


@dataclass(frozen=True)
class PresentationComplex:
    relators: tuple[str, ...]
    walks: tuple[tuple[int, ...], ...]
    domain_cycles: tuple[tuple[int, ...], ...]
    apices: tuple[int, ...]
    simplices: tuple[tuple[int, ...], ...]


def presentation_complex(words=AK3_WORDS):
    words = tuple(words)
    if not words or any(not word or any(letter not in "xXyY" for letter in word) for word in words):
        raise ValueError("nonempty x,y relator words are required")
    cells = [(0, 1), (1, 2), (0, 2), (0, 3), (3, 4), (0, 4)]
    walks, domains, apices = [], [], []
    next_vertex = 5
    for word in words:
        walk = rose_word_walk(word)
        length = len(walk) - 1
        domain = tuple(range(next_vertex, next_vertex + length))
        apex = next_vertex + length
        next_vertex = apex + 1
        walks.append(walk)
        domains.append(domain)
        apices.append(apex)
        for index in range(length):
            following = (index + 1) % length
            cells.extend(((walk[index], walk[index + 1], domain[following]),
                          (walk[index], domain[index], domain[following]),
                          (apex, domain[index], domain[following])))
    return PresentationComplex(words, tuple(walks), tuple(domains), tuple(apices),
                               tuple(sorted(face_closure(cells))))


def staircase_prism(base):
    maximal_staircases = []
    for simplex in sorted(base):
        for index in range(len(simplex)):
            maximal_staircases.append(tuple(2 * vertex for vertex in simplex[:index + 1])
                                      + tuple(2 * vertex + 1 for vertex in simplex[index:]))
    return face_closure(maximal_staircases)


def bottom_copy(base):
    return {tuple(2 * vertex for vertex in simplex) for simplex in base}


def canonical_prism_pairs(base):
    pairs = []
    for simplex in sorted(base, key=lambda face: (-len(face), face)):
        for index in range(len(simplex)):
            sigma = tuple(sorted(tuple(2 * vertex for vertex in simplex[:index + 1])
                                 + tuple(2 * vertex + 1 for vertex in simplex[index:])))
            tau = tuple(sorted(tuple(2 * vertex for vertex in simplex[:index])
                               + tuple(2 * vertex + 1 for vertex in simplex[index:])))
            pairs.append((sigma, tau))
    return tuple(pairs)


def verify_collapse(initial, pairs, expected_final=None):
    remaining = set(initial)
    if face_closure(remaining) != remaining:
        raise AssertionError("the initial complex is not face closed")
    for sigma, tau in pairs:
        sigma, tau = tuple(sigma), tuple(tau)
        if sigma not in remaining or tau not in remaining:
            raise AssertionError("a collapse simplex is absent")
        if len(sigma) != len(tau) + 1 or not set(tau) < set(sigma):
            raise AssertionError("the collapse pair is not codimension one")
        proper_cofaces = {simplex for simplex in remaining if set(tau) < set(simplex)}
        if proper_cofaces != {sigma}:
            raise AssertionError("the face does not have exactly the specified proper coface")
        remaining.remove(sigma)
        remaining.remove(tau)
    if expected_final is not None and remaining != set(expected_final):
        raise AssertionError("the collapse endpoint differs from the expected complex")
    return remaining


@dataclass(frozen=True)
class GreedyCollapseAttempt:
    seed: int
    pairs: tuple[tuple[tuple[int, ...], tuple[int, ...]], ...]
    remaining_maximal_simplices: tuple[tuple[int, ...], ...]
    remaining_f_vector: tuple[int, ...]
    success: bool


def greedy_collapse(initial, seed=SEED):
    remaining = set(initial)
    if face_closure(remaining) != remaining:
        raise AssertionError("the greedy input is not face closed")
    cofaces = {simplex: set() for simplex in remaining}
    for simplex in remaining:
        for size in range(1, len(simplex)):
            for face in combinations(simplex, size):
                cofaces[face].add(simplex)
    rng, pairs = random.Random(seed), []
    while True:
        free_pairs = []
        for tau, proper_cofaces in cofaces.items():
            if len(proper_cofaces) == 1:
                sigma = next(iter(proper_cofaces))
                if len(sigma) == len(tau) + 1:
                    free_pairs.append((sigma, tau))
        if not free_pairs:
            break
        top_dimension = max(len(sigma) for sigma, _ in free_pairs)
        sigma, tau = rng.choice(sorted(pair for pair in free_pairs if len(pair[0]) == top_dimension))
        pairs.append((sigma, tau))
        for removed in (sigma, tau):
            for size in range(1, len(removed)):
                for face in combinations(removed, size):
                    if face in cofaces:
                        cofaces[face].discard(removed)
            remaining.remove(removed)
            del cofaces[removed]
    maximal = tuple(sorted(simplex for simplex, proper_cofaces in cofaces.items() if not proper_cofaces))
    success = len(remaining) == 1 and len(next(iter(remaining))) == 1
    return GreedyCollapseAttempt(seed, tuple(pairs), maximal, f_vector(remaining), success)


def data():
    construction = presentation_complex()
    base = set(construction.simplices)
    prism = staircase_prism(base)
    canonical = canonical_prism_pairs(base)
    if f_vector(base) != (46, 162, 117) or f_vector(prism) != (92, 532, 792, 351) or len(canonical) != 721:
        raise AssertionError("the pinned AK3 construction counts drifted")
    verify_collapse(prism, canonical, bottom_copy(base))
    attempt = greedy_collapse(prism)
    endpoint = face_closure(attempt.remaining_maximal_simplices)
    verify_collapse(prism, attempt.pairs, endpoint)
    return {"words": AK3_WORDS, "base_f_vector": f_vector(base), "prism_f_vector": f_vector(prism),
            "canonical_pairs": canonical, "canonical_pair_count": len(canonical),
            "attempt": asdict(attempt), "status": "single_recorded_collapse_attempt"}


if __name__ == "__main__":
    print(json.dumps(data(), sort_keys=True))
