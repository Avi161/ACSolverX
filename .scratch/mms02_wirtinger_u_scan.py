from __future__ import annotations

import runpy
import sys
from itertools import product
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))

from experiments.analysis.whitehead import peak_reduce, total  # noqa: E402

ROOT = Path(__file__).resolve().parent
REPAIR = runpy.run_path(str(ROOT / "mms02_wirtinger_repair_checker.py"), run_name="repair")
FREE_REDUCE = REPAIR["free_reduce"]
INVERSE = REPAIR["inverse"]
SUBSTITUTE = REPAIR["substitute"]
RENAME_XYZ = REPAIR["rename_xyz"]
THREE_GENERATOR_DESCENDANT = REPAIR["three_generator_descendant"]


def meridian_exponent(word: str) -> int:
    return sum(1 if letter.islower() else -1 for letter in word)


def freely_reduced_words(length: int):
    for letters in product("xXyY", repeat=length):
        if all(left != right.swapcase() for left, right in zip(letters, letters[1:])):
            yield "".join(letters)


def pair_for_z(image: str) -> tuple[str, str]:
    relators, _ = THREE_GENERATOR_DESCENDANT(corrected=True)
    return tuple(
        SUBSTITUTE(RENAME_XYZ(relator), "z", image) for relator in relators
    )


def main() -> None:
    records: list[tuple[int, int, str, tuple[str, str]]] = []
    checked = 0
    for length in range(0, 10):
        candidates = [""] if length == 0 else freely_reduced_words(length)
        for image in candidates:
            if meridian_exponent(image) not in (0, 2):
                continue
            checked += 1
            pair = pair_for_z(image)
            floor_pair = peak_reduce(pair)
            records.append((total(floor_pair), sum(map(len, pair)), image, floor_pair))
    records.sort()
    print("checked", checked)
    for floor, raw_length, image, pair in records[:40]:
        print(floor, raw_length, image or "eps", pair)


if __name__ == "__main__":
    main()
