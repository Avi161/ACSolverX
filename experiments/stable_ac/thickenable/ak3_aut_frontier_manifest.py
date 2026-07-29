"""Pure free-word infrastructure for the frozen AK(3) Aut(F2) frontier."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from itertools import product


WordMap = tuple[str, str]
IDENTITY_MAP: WordMap = ("x", "y")
SOURCE_RELATORS = ("xxxYYYY", "xyxYXY")


@dataclass(frozen=True)
class NielsenEdge:
    name: str
    x_image: str
    y_image: str
    inverse_id: int

    @property
    def images(self) -> WordMap:
        return (self.x_image, self.y_image)


@dataclass(frozen=True)
class MapRecord:
    id: int
    images: WordMap
    parent_id: int | None
    depth: int
    edge_word: tuple[int, ...]


EDGES = (
    NielsenEdge("swap", "y", "x", 0),
    NielsenEdge("inv_x", "X", "y", 1),
    NielsenEdge("inv_y", "x", "Y", 2),
    NielsenEdge("x_mul_y", "xy", "y", 4),
    NielsenEdge("x_mul_Y", "xY", "y", 3),
    NielsenEdge("y_mul_x", "x", "yx", 6),
    NielsenEdge("y_mul_X", "x", "yX", 5),
)


def formal_inverse(word: str) -> str:
    return "".join(letter.swapcase() for letter in reversed(word))


def free_reduce(word: str) -> str:
    reduced: list[str] = []
    for letter in word:
        if reduced and reduced[-1] == letter.swapcase():
            reduced.pop()
        else:
            reduced.append(letter)
    return "".join(reduced)


def _image(letter: str, images: WordMap) -> str:
    if letter == "x":
        return images[0]
    if letter == "y":
        return images[1]
    if letter == "X":
        return formal_inverse(images[0])
    if letter == "Y":
        return formal_inverse(images[1])
    raise ValueError(f"not an F2 letter: {letter!r}")


def substitute_literal(word: str, images: WordMap) -> str:
    return "".join(_image(letter, images) for letter in word)


def substitute_free(word: str, images: WordMap) -> str:
    return free_reduce(substitute_literal(word, images))


def compose_maps(phi: WordMap, nu: WordMap) -> WordMap:
    """Return phi o nu, with phi substituted into each image of nu."""
    return (substitute_free(nu[0], phi), substitute_free(nu[1], phi))


def inverse_edge_word(edge_word: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(EDGES[edge_id].inverse_id for edge_id in reversed(edge_word))


def map_from_edge_word(edge_word: tuple[int, ...]) -> WordMap:
    images = IDENTITY_MAP
    for edge_id in edge_word:
        images = compose_maps(images, EDGES[edge_id].images)
    return images


def build_bfs_prefix(cap: int) -> tuple[MapRecord, ...]:
    if cap <= 0:
        return ()
    records = [MapRecord(0, IDENTITY_MAP, None, 0, ())]
    seen = {IDENTITY_MAP}
    pending = deque([0])
    while pending and len(records) < cap:
        parent_id = pending.popleft()
        parent = records[parent_id]
        for edge_id, edge in enumerate(EDGES):
            images = compose_maps(parent.images, edge.images)
            if images in seen:
                continue
            child = MapRecord(
                len(records), images, parent_id, parent.depth + 1, parent.edge_word + (edge_id,)
            )
            records.append(child)
            seen.add(images)
            pending.append(child.id)
            if len(records) == cap:
                break
    return tuple(records)


def cyclic_peel(word: str) -> tuple[str, str, str]:
    prefix = ""
    core = word
    while len(core) >= 2 and core[0] == core[-1].swapcase():
        prefix += core[0]
        core = core[1:-1]
    return (prefix, core, formal_inverse(prefix))


def _rotations(word: str) -> tuple[str, ...]:
    if not word:
        return (word,)
    return tuple(word[index:] + word[:index] for index in range(len(word)))


def _signed_generator_maps() -> tuple[WordMap, ...]:
    maps: list[WordMap] = []
    for x_image in ("x", "X", "y", "Y"):
        y_choices = ("y", "Y") if x_image.lower() == "x" else ("x", "X")
        maps.extend((x_image, y_image) for y_image in y_choices)
    return tuple(maps)


def exact_cellular_key(relators: tuple[str, str]) -> tuple[str, str]:
    candidates: list[tuple[str, str]] = []
    for images in _signed_generator_maps():
        transformed = tuple(substitute_literal(word, images) for word in relators)
        options = [
            tuple(_rotations(word)) + tuple(_rotations(formal_inverse(word)))
            for word in transformed
        ]
        for first, second in product(*options):
            candidates.append((first, second))
            candidates.append((second, first))
    return min(candidates)
