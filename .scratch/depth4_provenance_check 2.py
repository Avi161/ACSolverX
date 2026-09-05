from __future__ import annotations

# The 30 three-minority cases are enumerated here but are not certified.

from collections import Counter, defaultdict
from hashlib import sha256
from itertools import product
from math import gcd
from typing import Callable, Iterator, NamedTuple


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


def cyclic_reduce_for_target_lengths(
    parts: tuple[FPWord, ...],
    orders: dict[str, int],
    target_lengths: set[int],
) -> FPWord | None:
    total_length = sum(len(part) for part in parts)
    possible_lengths = {length for length in target_lengths if length <= total_length}
    if not possible_lengths:
        return None

    reduced: list[tuple[str, int]] = []
    processed = 0
    for part in parts:
        for factor, exponent in part:
            processed += 1
            if reduced and reduced[-1][0] == factor:
                combined = (reduced[-1][1] + exponent) % orders[factor]
                reduced.pop()
                if combined:
                    reduced.append((factor, combined))
            else:
                reduced.append((factor, exponent))

            maximum_final_length = len(reduced) + total_length - processed
            possible_lengths = {
                length
                for length in possible_lengths
                if length <= maximum_final_length
            }
            if not possible_lengths:
                return None

    cyclically_reduced = cyclic_reduce(tuple(reduced), orders)
    if len(cyclically_reduced) not in possible_lengths:
        return None
    return cyclically_reduced


def rotations(word: FPWord) -> set[FPWord]:
    return {word[index:] + word[:index] for index in range(len(word))}


def cyclic_subwords(word: FPWord, length: int) -> set[FPWord]:
    if not length:
        return {()}
    doubled = word + word
    return {
        doubled[index : index + length]
        for index in range(len(word))
    }


def connector_can_retain_target_subword(
    connector: FPWord,
    source_length: int,
    target_length: int,
    target_subwords: dict[int, set[FPWord]],
) -> bool:
    raw_length = 2 * source_length + 2 * len(connector)
    syllable_loss = raw_length - target_length
    if syllable_loss < 0:
        return False
    retained_length = len(connector) - syllable_loss
    if retained_length <= 0:
        return True
    return any(
        connector[start : start + retained_length] in target_subwords[retained_length]
        for start in range(syllable_loss + 1)
    )


def connector_prefix_can_reach_target(
    prefix: FPWord,
    source_length: int,
    target_length: int,
    connector_bound: int,
    target_subwords: dict[int, set[FPWord]],
) -> bool:
    first_factor = prefix[0][0] if prefix else None
    factors = {word[0][0] for word in target_subwords[1]}
    for final_length in range(len(prefix), connector_bound + 1):
        syllable_loss = 2 * source_length + 2 * final_length - target_length
        if syllable_loss < 0:
            continue
        retained_length = final_length - syllable_loss
        if retained_length <= 0:
            return True
        for start in range(syllable_loss + 1):
            for target_segment in target_subwords[retained_length]:
                if first_factor is not None:
                    expected_factor = first_factor if start % 2 == 0 else next(
                        factor for factor in factors if factor != first_factor
                    )
                    if target_segment[0][0] != expected_factor:
                        continue
                overlap_end = min(start + retained_length, len(prefix))
                if start < overlap_end:
                    overlap = prefix[start:overlap_end]
                    if overlap != target_segment[: len(overlap)]:
                        continue
                return True
    return False


def conjugate(left: FPWord, right: FPWord, orders: dict[str, int]) -> bool:
    left = cyclic_reduce(left, orders)
    right = cyclic_reduce(right, orders)
    if len(left) != len(right):
        return False
    if len(left) < 2:
        return left == right
    return left in rotations(right)


def stream_reduced_connectors(
    orders: dict[str, int],
    maximum_length: int,
    branch_possible: Callable[[FPWord], bool] | None = None,
) -> Iterator[tuple[FPWord, FPWord]]:
    if branch_possible is not None and not branch_possible(()):
        return
    yield (), ()

    def extend(word: FPWord, inverse: FPWord) -> Iterator[tuple[FPWord, FPWord]]:
        if len(word) == maximum_length:
            return
        for factor, order in orders.items():
            if word and word[-1][0] == factor:
                continue
            for exponent in range(1, order):
                candidate = word + ((factor, exponent),)
                candidate_inverse = (
                    (factor, (-exponent) % order),
                ) + inverse
                if branch_possible is not None and not branch_possible(candidate):
                    continue
                yield candidate, candidate_inverse
                yield from extend(candidate, candidate_inverse)

    yield from extend((), ())


def connector_count(orders: dict[str, int], maximum_length: int) -> int:
    counts = {factor: order - 1 for factor, order in orders.items()}
    total = 1 + sum(counts.values())
    ending_counts = counts
    for _ in range(2, maximum_length + 1):
        ending_counts = {
            factor: (order - 1)
            * sum(count for other, count in ending_counts.items() if other != factor)
            for factor, order in orders.items()
        }
        total += sum(ending_counts.values())
    return total


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


class LowMinorityCertificate(NamedTuple):
    signature: tuple[int, int, int, int, int]
    quotient: str
    minority_length: int
    target_length: int
    connector_bound: int | None
    candidate_products_certified: int
    found_target: bool


def new_depth_four_multisets() -> set[Leaves]:
    depth_four = row_multisets(4)
    old = set().union(*(row_multisets(depth) for depth in range(4)))
    new = depth_four - old
    signatures = sorted(signature(leaves) for leaves in new)
    assert len(depth_four) == 82
    assert len(old) == 28
    assert len(new) == 54
    assert len(set(signatures)) == 54
    return new


def low_minority_certificate_records() -> tuple[LowMinorityCertificate, ...]:
    new = new_depth_four_multisets()
    signatures = sorted(signature(leaves) for leaves in new)

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

    records: dict[tuple[int, int, int, int, int], LowMinorityCertificate] = {}
    two_minority_groups: dict[
        tuple[str, tuple[int, int]],
        list[
            tuple[
                tuple[int, int, int, int, int],
                int,
                FPWord,
            ]
        ],
    ] = defaultdict(list)
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
            records[sig] = LowMinorityCertificate(
                sig,
                quotient,
                len(minority_image),
                len(target_image),
                None,
                1,
                found,
            )
            continue

        source_length = len(minority_image)
        target_length = len(target_image)
        bridge_length = (
            (target_length - 2 * source_length) // 2
            if target_length >= 2 * source_length
            else 0
        )
        connector_bound = bridge_length + 2
        two_minority_groups[(quotient, tuple(signs))].append(
            (sig, connector_bound, target_image)
        )

    for (quotient, signs), cases in two_minority_groups.items():
        orders, images = QUOTIENTS[quotient]
        minority = "B" if quotient == "Q_A" else "A"
        minority_image = cyclic_reduce(evaluate(SOURCES[minority], images, orders), orders)
        signed_images = tuple(
            minority_image if sign > 0 else fp_inverse(minority_image, orders)
            for sign in signs
        )
        left_rotations = rotations(signed_images[0])
        right_rotations = rotations(signed_images[1])
        targets_by_length: dict[
            int,
            list[
                tuple[
                    tuple[int, int, int, int, int],
                    int,
                    set[FPWord],
                    dict[int, set[FPWord]],
                ]
            ],
        ] = defaultdict(list)
        for sig, connector_bound, target_image in cases:
            target_rotations = rotations(target_image) if len(target_image) >= 2 else {target_image}
            target_subwords = {
                length: cyclic_subwords(target_image, length)
                if length <= len(target_image)
                else set()
                for length in range(1, connector_bound + 1)
            }
            targets_by_length[len(target_image)].append(
                (sig, connector_bound, target_rotations, target_subwords)
            )

        maximum_bound = max(connector_bound for _, connector_bound, _ in cases)
        found_signatures = set()

        def branch_possible(prefix: FPWord) -> bool:
            return any(
                sig not in found_signatures
                and connector_prefix_can_reach_target(
                    prefix,
                    len(minority_image),
                    target_length,
                    connector_bound,
                    target_subwords,
                )
                for target_length, targets in targets_by_length.items()
                for sig, connector_bound, _, target_subwords in targets
            )

        for connector, connector_inverse in stream_reduced_connectors(
            orders,
            maximum_bound,
            branch_possible,
        ):
            active_targets = [
                (target_length, sig, target_rotations)
                for target_length, targets in targets_by_length.items()
                for sig, connector_bound, target_rotations, target_subwords in targets
                if len(connector) <= connector_bound
                and sig not in found_signatures
                and connector_can_retain_target_subword(
                    connector,
                    len(minority_image),
                    target_length,
                    target_subwords,
                )
            ]
            if not active_targets:
                continue
            active_lengths = {target_length for target_length, _, _ in active_targets}
            for left_rotation in left_rotations:
                for right_rotation in right_rotations:
                    reduced = cyclic_reduce_for_target_lengths(
                        (
                            left_rotation,
                            connector,
                            right_rotation,
                            connector_inverse,
                        ),
                        orders,
                        active_lengths,
                    )
                    if reduced is None:
                        continue
                    for target_length, sig, target_rotations in active_targets:
                        if len(reduced) == target_length and reduced in target_rotations:
                            found_signatures.add(sig)

        rotation_pairs = len(left_rotations) * len(right_rotations)
        for sig, connector_bound, target_image in cases:
            records[sig] = LowMinorityCertificate(
                sig,
                quotient,
                len(minority_image),
                len(target_image),
                connector_bound,
                rotation_pairs * connector_count(orders, connector_bound),
                sig in found_signatures,
            )

    ordered_records = tuple(records[sig] for sig in sorted(records))
    assert len(ordered_records) == 24
    return ordered_records


def main() -> None:
    new = new_depth_four_multisets()
    signatures = sorted(signature(leaves) for leaves in new)
    cases_by_minority: dict[int, list[tuple[int, int, int, int, int]]] = defaultdict(list)
    for sig in signatures:
        _, a_count, b_count, _, _ = sig
        cases_by_minority[min(a_count, b_count)].append(sig)

    records = low_minority_certificate_records()
    assert not any(record.found_target for record in records)

    signature_payload = "\n".join(",".join(map(str, sig)) for sig in signatures)
    record_payload = "\n".join(repr(record) for record in records)
    print("new depth-four multisets:", len(new))
    print("minority split:", {key: len(value) for key, value in cases_by_minority.items()})
    print("signature sha256:", sha256(signature_payload.encode()).hexdigest())
    print("certificate sha256:", sha256(record_payload.encode()).hexdigest())
    print(
        "two-minority candidate products certified:",
        sum(
            record.candidate_products_certified
            for record in records
            if record.connector_bound is not None
        ),
    )
    print("\nCLOSED CASES")
    for record in records:
        print(record)
    print("\nTHREE-MINORITY SURVIVORS")
    for sig in cases_by_minority[3]:
        print(sig)


if __name__ == "__main__":
    main()
