from __future__ import annotations

import runpy
from collections import deque
from pathlib import Path


TOOLS = runpy.run_path(
    str(Path(__file__).with_name("mms02_killer_quotient_scan.py")), run_name="a5_tools"
)
COMPOSE = TOOLS["compose"]
INVERSE = TOOLS["inverse"]
EVALUATE = TOOLS["evaluate"]
GENERATED_SUBGROUP = TOOLS["generated_subgroup"]
EXCHANGE_QUOTIENT = TOOLS["exchange_quotient"]

K_IMAGE = (1, 2, 3, 4, 0)
N_IMAGE = (2, 0, 4, 1, 3)
IDENTITY = tuple(range(5))
_, PROBES, _ = EXCHANGE_QUOTIENT()
IMAGES = {"k": K_IMAGE, "n": N_IMAGE, "l": INVERSE(N_IMAGE)}
CORRECT = EVALUATE(PROBES[0], IMAGES)
MISPRINT = EVALUATE(PROBES[1], IMAGES)
A5 = sorted(GENERATED_SUBGROUP((K_IMAGE, N_IMAGE)))


def conjugate(element, by):
    return COMPOSE(COMPOSE(by, element), INVERSE(by))


def conjugacy_class(element):
    return sorted({conjugate(element, by) for by in A5})


def neighbours(state):
    left, right = state
    yield (INVERSE(left), right), ("invert", 0, None)
    yield (left, INVERSE(right)), ("invert", 1, None)
    for target, element in enumerate((left, right)):
        for conjugate_element in conjugacy_class(element):
            if conjugate_element == element:
                continue
            child = (conjugate_element, right) if target == 0 else (left, conjugate_element)
            yield child, ("conjugate", target, conjugate_element)
    for target, (base, source) in enumerate(((left, right), (right, left))):
        factors = set(conjugacy_class(source) + conjugacy_class(INVERSE(source)))
        for factor in sorted(factors):
            product = COMPOSE(base, factor)
            child = (product, right) if target == 0 else (left, product)
            yield child, ("multiply_conjugate", target, factor)


def main() -> None:
    start = (IDENTITY, CORRECT)
    targets = {(IDENTITY, element) for element in conjugacy_class(MISPRINT)}
    parents = {start: None}
    moves = {}
    queue = deque([start])
    goal = None
    while queue:
        state = queue.popleft()
        if state in targets:
            goal = state
            break
        for child, move in neighbours(state):
            if child in parents:
                continue
            parents[child] = state
            moves[child] = move
            queue.append(child)
    assert goal is not None
    path = []
    cursor = goal
    while parents[cursor] is not None:
        path.append((moves[cursor], cursor))
        cursor = parents[cursor]
    path.reverse()
    print("states_seen", len(parents), "macro_length", len(path))
    print("start", start)
    for index, (move, state) in enumerate(path, start=1):
        print(index, move, state)


if __name__ == "__main__":
    main()
