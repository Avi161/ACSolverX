"""Exact reverse-coordinate search using Stallings folding and rewriting."""

from __future__ import annotations

import argparse
import csv
import json
from collections import deque
from pathlib import Path

from experiments.stable_ac.supermoves.certified_acm import (
    cyclic_orientations,
    cyclic_reduce,
    free_reduce,
    inverse,
)
from experiments.stable_ac.supermoves.quotient_isolator import exponent_sum
from experiments.stable_ac.supermoves.search_coordinate_descents import (
    reduced_words,
    substitute_pair,
)


def edge_key(u: int, letter: str, v: int):
    edge = (u, letter, v)
    reverse = (v, letter.swapcase(), u)
    return min(edge, reverse)


class StallingsRewriter:
    def __init__(self, left: str, right: str, nielsen_reduce, apply_nielsen):
        words = (free_reduce(left), free_reduce(right))
        edges: list[tuple[int, str, int]] = []
        vertex_count = 1
        for word in words:
            current = 0
            for index, letter in enumerate(word):
                if index == len(word) - 1:
                    target = 0
                else:
                    target = vertex_count
                    vertex_count += 1
                edges.append((current, letter, target))
                edges.append((target, letter.swapcase(), current))
                current = target

        parent = list(range(vertex_count))

        def find(value: int) -> int:
            while parent[value] != value:
                parent[value] = parent[parent[value]]
                value = parent[value]
            return value

        def union(left_vertex: int, right_vertex: int) -> bool:
            left_root = find(left_vertex)
            right_root = find(right_vertex)
            if left_root == right_root:
                return False
            parent[right_root] = left_root
            return True

        while True:
            transitions: dict[tuple[int, str], int] = {}
            changed = False
            for source, letter, target in edges:
                source = find(source)
                target = find(target)
                key = (source, letter)
                if key in transitions:
                    changed |= union(transitions[key], target)
                else:
                    transitions[key] = target
            if not changed:
                break

        base = find(0)
        adjacency: dict[tuple[int, str], int] = {}
        vertices = {base}
        for source, letter, target in edges:
            source = find(source)
            target = find(target)
            adjacency[(source, letter)] = target
            vertices.update((source, target))
        self.base = base
        self.adjacency = adjacency

        path_word = {base: ""}
        tree_edges = set()
        queue = deque([base])
        while queue:
            source = queue.popleft()
            for letter in "xXyY":
                target = adjacency.get((source, letter))
                if target is None or target in path_word:
                    continue
                path_word[target] = free_reduce(path_word[source] + letter)
                tree_edges.add(edge_key(source, letter, target))
                queue.append(target)
        if set(path_word) != vertices:
            raise AssertionError("folded subgroup graph is disconnected")

        undirected = {
            edge_key(source, letter, target)
            for (source, letter), target in adjacency.items()
        }
        non_tree = sorted(undirected - tree_edges)
        if len(non_tree) != 2:
            raise ValueError(f"expected a rank-two subgroup, got rank {len(non_tree)}")
        oriented = {non_tree[0]: non_tree[0], non_tree[1]: non_tree[1]}
        symbols = {non_tree[0]: "x", non_tree[1]: "y"}
        contributions: dict[tuple[int, str], str] = {}
        for (source, letter), target in adjacency.items():
            key = edge_key(source, letter, target)
            if key in tree_edges:
                contributions[(source, letter)] = ""
            elif (source, letter, target) == oriented[key]:
                contributions[(source, letter)] = symbols[key]
            else:
                contributions[(source, letter)] = symbols[key].upper()
        self.contributions = contributions

        image_in_graph_basis = tuple(self._rewrite_loop(word) for word in words)
        moves = nielsen_reduce(image_in_graph_basis)
        if moves is None:
            raise AssertionError("input generators did not form a basis of their subgroup")
        domain = ("a", "b")
        image = image_in_graph_basis
        for move in moves:
            image = apply_nielsen(image, move)
            domain = self._apply_generic_nielsen(domain, move)
        inverse_images: dict[str, str] = {}
        for slot, value in enumerate(image):
            generator = value.lower()
            inverse_images[generator] = (
                domain[slot] if value.islower() else inverse(domain[slot])
            )
        if set(inverse_images) != {"x", "y"}:
            raise AssertionError("Nielsen inverse did not recover both graph generators")
        self.inverse_images = inverse_images

    @staticmethod
    def _apply_generic_nielsen(pair, move):
        other = pair[1 - move.target]
        if move.sign == -1:
            other = inverse(other)
        target = pair[move.target]
        replacement = (
            free_reduce(target + other)
            if move.side == "right"
            else free_reduce(other + target)
        )
        child = list(pair)
        child[move.target] = replacement
        return tuple(child)

    def _rewrite_loop(self, word: str) -> str:
        current = self.base
        output = []
        for letter in free_reduce(word):
            key = (current, letter)
            if key not in self.adjacency:
                raise KeyError(word)
            output.append(self.contributions[key])
            current = self.adjacency[key]
        if current != self.base:
            raise KeyError(word)
        return free_reduce("".join(output))

    def preimage(self, word: str) -> str | None:
        try:
            graph_word = self._rewrite_loop(word)
        except KeyError:
            return None
        pieces = []
        for letter in graph_word:
            image = self.inverse_images[letter.lower()]
            pieces.append(image if letter.islower() else inverse(image))
        abstract = free_reduce("".join(pieces))
        return abstract.translate(str.maketrans({"a": "x", "A": "X", "b": "y", "B": "Y"}))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--checker-root", type=Path, required=True)
    parser.add_argument("--max-image-length", type=int, default=8)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    import experiments
    import experiments.stable_ac

    package_path = str(args.checker_root / "experiments")
    stable_path = str(args.checker_root / "experiments/stable_ac")
    if package_path not in experiments.__path__:
        experiments.__path__.append(package_path)
    if stable_path not in experiments.stable_ac.__path__:
        experiments.stable_ac.__path__.append(stable_path)
    from experiments.equivalence_classes.lib.autcanon import aut_canon
    from experiments.stable_ac.rank3_compression.primitive_bases import (
        apply_nielsen,
        nielsen_reduce,
    )

    with args.data.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    sources = []
    for row in rows:
        pair = (row["r1"], row["r2"])
        floor, rep, _ = aut_canon(pair)
        sources.append((row["name"], pair, floor, rep))

    candidates = 0
    membership_pairs = 0
    records = []
    for generator in ("x", "y"):
        fixed = "y" if generator == "x" else "x"
        for image_word in reduced_words(args.max_image_length):
            if exponent_sum(image_word, generator) not in (-1, 1):
                continue
            image_pair = (
                (image_word, fixed) if generator == "x" else (fixed, image_word)
            )
            if nielsen_reduce(image_pair) is not None:
                continue
            candidates += 1
            rewriter = StallingsRewriter(
                image_pair[0], image_pair[1], nielsen_reduce, apply_nielsen
            )
            for name, source, source_floor, source_rep in sources:
                preimages = []
                exact_images = []
                for relator in source:
                    choices = []
                    for orientation in cyclic_orientations(relator):
                        preimage = rewriter.preimage(orientation)
                        if preimage is None:
                            continue
                        mapped = substitute_pair(
                            preimage, image_pair[0], image_pair[1]
                        )
                        if cyclic_reduce(mapped) != cyclic_reduce(orientation):
                            raise AssertionError("rewritten preimage does not replay")
                        choices.append((len(cyclic_reduce(preimage)), preimage, orientation))
                    if not choices:
                        break
                    _, preimage, orientation = min(choices)
                    preimages.append(cyclic_reduce(preimage))
                    exact_images.append(orientation)
                if len(preimages) != 2:
                    continue
                membership_pairs += 1
                preimage_pair = tuple(preimages)
                pre_floor, pre_rep, pre_witness = aut_canon(preimage_pair)
                if pre_floor >= source_floor or pre_rep == source_rep:
                    continue
                records.append(
                    {
                        "name": name,
                        "generator": generator,
                        "coordinate_image": image_word,
                        "endomorphism_images": list(image_pair),
                        "source": list(source),
                        "source_floor": source_floor,
                        "source_representative": list(source_rep),
                        "preimage": list(preimage_pair),
                        "preimage_floor": pre_floor,
                        "preimage_representative": list(pre_rep),
                        "floor_delta": pre_floor - source_floor,
                        "exact_oriented_images": exact_images,
                        "preimage_whitehead_witness": pre_witness,
                    }
                )

    payload = {
        "max_image_length": args.max_image_length,
        "proper_coordinate_candidates": candidates,
        "source_pairs_in_coordinate_images": membership_pairs,
        "strict_nonautomorphic_floor_descents": len(records),
        "records": sorted(
            records,
            key=lambda row: (
                row["floor_delta"], row["name"], row["generator"], row["coordinate_image"]
            ),
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in payload.items() if key != "records"}))
    for record in payload["records"][:20]:
        print(json.dumps(record, sort_keys=True))


if __name__ == "__main__":
    main()
