from __future__ import annotations

# [unverified] The provenance assertions are fast, but the two-minority
# connector census was interrupted before completion; optimize before relying on it.

from collections import Counter, defaultdict
from hashlib import sha256
from itertools import product
from math import gcd


Leaf = tuple[str, int]
Leaves = tuple[Leaf, ...]
FPWord = tuple[tuple[str, int], ...]


def invert_leaves(leaves: Leaves) -> Leaves:
    return tuple((source, -sign) for source, sign in reversed(leaves))


def canonical_leaf_multiset(leaves: Leaves) -> Leaves:
    direct = tuple(sorted(leaves))
    inverted = tuple(sorted(invert_leaves(leaves)))
    return min(direct, inverted)


def rows_after(moves: int) -> set[tuple[Leaves, Leaves]]:
    states = {((("A", 1),), (("B", 1),))}
    for _ in range(moves):
        next_states = set()
        for rows in states:
            for target in (0, 1):
                source = 1 - target
                for invert_target, invert_source in product((False, True), repeat=2):
                    next_rows = list(rows)
                    left = invert_leaves(rows[target]) if invert_target else rows[target]
                    right = invert_leaves(rows[source]) if invert_source else rows[source]
                    next_rows[target] = left + right
                    next_states.add(tuple(next_rows))
        states = next_states
    return states


def row_multisets(moves: int) -> set[Leaves]:
    return {
        canonical_leaf_multiset(row)
        for rows in rows_after(moves)
        for row in rows
    }


def signature(leaves: Leaves) -> tuple[int, int, int, int, int]:
    counts = Counter(leaves)
    a_count = counts["A", 1] + counts["A", -1]
    b_count = counts["B", 1] + counts["B", -1]
    a_coefficient = counts["A", 1] - counts["A", -1]
    b_coefficient = counts["B", 1] - counts["B", -1]
    return (
        len(leaves),
        a_count,
        b_count,
        a_coefficient,
        b_coefficient,
    )


def fp_multiply(left: FPWord, right: FPWord, orders: dict[str, int]) -> FPWord:
    reduced = list(left)
    for factor, exponent in right:
        exponent %= orders[factor]
        if not exponent:
            continue
        if reduced and reduced[-1][0] == factor:
            combined = (reduced[-1][1] + exponent) % orders[factor]
            reduced.pop()
            if combined:
                reduced.append((factor, combined))
        else:
            reduced.append((factor, exponent))
    return tuple(reduced)


def fp_inverse(word: FPWord, orders: dict[str, int]) -> FPWord:
    return tuple(
        (factor, (-exponent) % orders[factor])
        for factor, exponent in reversed(word)
    )


def evaluate(word: str, images: dict[str, FPWord], orders: dict[str, int]) -> FPWord:
    result: FPWord = ()
    for letter in word:
        image = images[letter.lower()]
        if letter.isupper():
            image = fp_inverse(image, orders)
        result = fp_multiply(result, image, orders)
    return result


def cyclic_reduce(word: FPWord, orders: dict[str, int]) -> FPWord:
    reduced = word
    while len(reduced) > 1 and reduced[0][0] == reduced[-1][0]:
        factor = reduced[0][0]
        exponent = (reduced[-1][1] + reduced[0][1]) % orders[factor]
        prefix = ((factor, exponent),) if exponent else ()
        reduced = fp_multiply(prefix, reduced[1:-1], orders)
    return reduced


def rotations(word: FPWord) -> set[FPWord]:
    return {word[index:] + word[:index] for index in range(len(word))}


def conjugate(left: FPWord, right: FPWord, orders: dict[str, int]) -> bool:
    left = cyclic_reduce(left, orders)
    right = cyclic_reduce(right, orders)
    if len(left) != len(right):
        return False
    if len(left) < 2:
        return left == right
    return left in rotations(right)


def reduced_connectors(orders: dict[str, int], maximum_length: int) -> list[FPWord]:
    connectors: list[FPWord] = [()]
    frontier: list[FPWord] = [()]
    for _ in range(maximum_length):
        next_frontier = []
        for word in frontier:
            for factor, order in orders.items():
                if word and word[-1][0] == factor:
                    continue
                for exponent in range(1, order):
                    candidate = word + ((factor, exponent),)
                    connectors.append(candidate)
                    next_frontier.append(candidate)
        frontier = next_frontier
    return connectors


def christoffel(x_exponent: int, y_exponent: int) -> str:
    x_letter = "x" if x_exponent >= 0 else "X"
    y_letter = "y" if y_exponent >= 0 else "Y"
    x_count = abs(x_exponent)
    y_count = abs(y_exponent)
    length = x_count + y_count
    if not x_count:
        return y_letter
    if not y_count:
        return x_letter
    return "".join(
        x_letter
        if ((index + 1) * x_count) // length > (index * x_count) // length
        else y_letter
        for index in range(length)
    )


QUOTIENTS = {
    "Q_A": (
        {"X": 3, "Y": 4},
        {"x": (("X", 1),), "y": (("Y", 1),)},
    ),
    "Q_B": (
        {"s": 2, "t": 3},
        {
            "x": (("t", 2), ("s", 1)),
            "y": (("s", 1), ("t", 2)),
        },
    ),
}
SOURCES = {"A": "xxxYYYY", "B": "xyxYXY"}


def main() -> None:
    depth_four = row_multisets(4)
    old = set().union(*(row_multisets(depth) for depth in range(4)))
    new = depth_four - old
    signatures = sorted(signature(leaves) for leaves in new)
    assert len(depth_four) == 82
    assert len(old) == 28
    assert len(new) == 54
    assert len(set(signatures)) == 54

    cases_by_minority: dict[int, list[tuple[int, int, int, int, int]]] = defaultdict(list)
    leaves_by_signature = {signature(leaves): leaves for leaves in new}
    for sig in signatures:
        _, a_count, b_count, _, _ = sig
        cases_by_minority[min(a_count, b_count)].append(sig)
    assert {key: len(value) for key, value in cases_by_minority.items()} == {
        1: 10,
        2: 14,
        3: 30,
    }

    assert evaluate(SOURCES["A"], *reversed(QUOTIENTS["Q_A"])) == ()
    assert evaluate(SOURCES["B"], *reversed(QUOTIENTS["Q_B"])) == ()

    records = []
    checked_words = 0
    connector_cache: dict[tuple[str, int], list[FPWord]] = {}
    for sig in cases_by_minority[1] + cases_by_minority[2]:
        _, a_count, b_count, a_coefficient, b_coefficient = sig
        majority = "A" if a_count > b_count else "B"
        minority = "B" if majority == "A" else "A"
        quotient = f"Q_{majority}"
        orders, images = QUOTIENTS[quotient]
        leaves = leaves_by_signature[sig]
        signs = [sign for source, sign in leaves if source == minority]
        minority_image = cyclic_reduce(evaluate(SOURCES[minority], images, orders), orders)
        p = 3 * a_coefficient + b_coefficient
        q = -4 * a_coefficient - b_coefficient
        assert gcd(abs(p), abs(q)) == 1
        target_image = cyclic_reduce(evaluate(christoffel(p, q), images, orders), orders)

        if len(signs) == 1:
            signed = minority_image if signs[0] > 0 else fp_inverse(minority_image, orders)
            found = conjugate(signed, target_image, orders)
            records.append(
                (sig, quotient, len(minority_image), len(target_image), "-", 1, found)
            )
            continue

        signed_images = [
            minority_image if sign > 0 else fp_inverse(minority_image, orders)
            for sign in signs
        ]
        source_length = len(minority_image)
        target_length = len(target_image)
        bridge_length = (
            (target_length - 2 * source_length) // 2
            if target_length >= 2 * source_length
            else 0
        )
        connector_bound = bridge_length + 2
        cache_key = (quotient, connector_bound)
        if cache_key not in connector_cache:
            connector_cache[cache_key] = reduced_connectors(orders, connector_bound)
        connectors = connector_cache[cache_key]
        target_rotations = rotations(target_image) if len(target_image) >= 2 else {target_image}
        found = False
        local_checked = 0
        for left_rotation in rotations(signed_images[0]):
            for right_rotation in rotations(signed_images[1]):
                for connector in connectors:
                    product_word = fp_multiply(left_rotation, connector, orders)
                    product_word = fp_multiply(product_word, right_rotation, orders)
                    product_word = fp_multiply(product_word, fp_inverse(connector, orders), orders)
                    local_checked += 1
                    reduced = cyclic_reduce(product_word, orders)
                    if len(reduced) == target_length and reduced in target_rotations:
                        found = True
                        break
                if found:
                    break
            if found:
                break
        checked_words += local_checked
        records.append(
            (
                sig,
                quotient,
                source_length,
                target_length,
                connector_bound,
                local_checked,
                found,
            )
        )

    assert len(records) == 24
    assert not any(record[-1] for record in records)

    signature_payload = "\n".join(",".join(map(str, sig)) for sig in signatures)
    record_payload = "\n".join(repr(record) for record in records)
    print("depth-four row multisets:", len(depth_four))
    print("old through depth three:", len(old))
    print("new depth-four multisets:", len(new))
    print("minority split:", {key: len(value) for key, value in cases_by_minority.items()})
    print("signature sha256:", sha256(signature_payload.encode()).hexdigest())
    print("certificate sha256:", sha256(record_payload.encode()).hexdigest())
    print("two-minority candidate words checked:", checked_words)
    print("\nCLOSED CASES")
    for record in records:
        print(record)
    print("\nTHREE-MINORITY SURVIVORS")
    for sig in cases_by_minority[3]:
        print(sig)


if __name__ == "__main__":
    main()
