"""Search conjugating coordinate endomorphisms for raw length descents."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from experiments.stable_ac.supermoves.certified_acm import cyclic_reduce, inverse
from experiments.stable_ac.supermoves.quotient_isolator import (
    coordinate_endomorphism_move,
)


LETTERS = "xXyY"


def reduced_words(max_length: int):
    yield ""
    level = [""]
    for _ in range(max_length):
        level = [
            prefix + letter
            for prefix in level
            for letter in LETTERS
            if not prefix or prefix[-1] != letter.swapcase()
        ]
        yield from level


def search(rows: list[dict[str, str]], max_conjugator_length: int):
    best: dict[str, tuple[int, str, str, tuple[str, ...]]] = {}
    for h in reduced_words(max_conjugator_length):
        for generator in ("x", "y"):
            image = h + generator + inverse(h)
            for row in rows:
                source = (row["r1"], row["r2"])
                target = coordinate_endomorphism_move(
                    source, generator, image
                ).target
                delta = sum(map(len, target)) - sum(map(len, source))
                candidate = (delta, generator, image, target)
                if row["name"] not in best or candidate < best[row["name"]]:
                    best[row["name"]] = candidate
    return best


def substitute_pair(word: str, x_image: str, y_image: str) -> str:
    images = {
        "x": x_image,
        "X": inverse(x_image),
        "y": y_image,
        "Y": inverse(y_image),
    }
    return cyclic_reduce("".join(images[letter] for letter in word))


def search_coupled(rows: list[dict[str, str]], max_conjugator_length: int):
    best: dict[str, tuple[int, str, str, tuple[str, ...]]] = {}
    words = tuple(reduced_words(max_conjugator_length))
    for hx in words:
        x_image = hx + "x" + inverse(hx)
        for hy in words:
            y_image = hy + "y" + inverse(hy)
            for row in rows:
                source = (row["r1"], row["r2"])
                target = tuple(
                    substitute_pair(relator, x_image, y_image)
                    for relator in source
                )
                delta = sum(map(len, target)) - sum(map(len, source))
                candidate = (delta, x_image, y_image, target)
                if row["name"] not in best or candidate < best[row["name"]]:
                    best[row["name"]] = candidate
    return best


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--max-conjugator-length", type=int, default=8)
    parser.add_argument("--coupled", action="store_true")
    args = parser.parse_args()
    with args.data.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    searcher = search_coupled if args.coupled else search
    best = searcher(rows, args.max_conjugator_length)
    descents = [(name, *candidate) for name, candidate in best.items() if candidate[0] < 0]
    for record in sorted(descents, key=lambda item: (item[1], item[0])):
        print(record)
    print(f"descents={len(descents)}/{len(rows)}")


if __name__ == "__main__":
    main()
