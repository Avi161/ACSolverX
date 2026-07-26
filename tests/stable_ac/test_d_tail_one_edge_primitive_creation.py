from __future__ import annotations

from collections import Counter, defaultdict, deque
from collections.abc import Mapping, Sequence
from functools import lru_cache
from itertools import permutations, product


INVERSE_LETTER = {
    "x": "X",
    "X": "x",
    "t": "T",
    "T": "t",
    "z": "Z",
    "Z": "z",
    "q": "Q",
    "Q": "q",
    "y": "Y",
    "Y": "y",
}
GENERATORS4 = ("x", "t", "z", "q")
LETTERS4 = "xXtTzZqQ"

A = "qxxxQTTTT"
C = "qxQtq"
W = A + "Z" + C
D = "TzxZ"

WordMap = Mapping[str, str]
StateKey = tuple[int, int, int, str, str, str]


def free_reduce(word: str) -> str:
    stack: list[str] = []
    for letter in word:
        if stack and INVERSE_LETTER[letter] == stack[-1]:
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def inverse_word(word: str) -> str:
    return "".join(INVERSE_LETTER[letter] for letter in reversed(word))


def cyclic_reduce(word: str) -> str:
    word = free_reduce(word)
    while (
        len(word) > 1
        and INVERSE_LETTER[word[0]] == word[-1]
    ):
        word = free_reduce(word[1:-1])
    return word


def canonical_relator(word: str) -> str:
    word = cyclic_reduce(word)
    if not word:
        return ""
    candidates: list[str] = []
    for orientation in (word, inverse_word(word)):
        candidates.extend(
            orientation[index:] + orientation[:index]
            for index in range(len(orientation))
        )
    return min(candidates)


def canonical_tuple(words: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted(canonical_relator(word) for word in words))


def substitute(word: str, images: WordMap) -> str:
    result = ""
    for letter in word:
        image = images[letter.lower()]
        if letter.isupper():
            image = inverse_word(image)
        result = free_reduce(result + image)
    return result


def compose(
    outer: WordMap,
    inner: WordMap,
    generators: Sequence[str],
) -> dict[str, str]:
    return {
        generator: substitute(inner[generator], outer)
        for generator in generators
    }


def identity_map(generators: Sequence[str]) -> dict[str, str]:
    return {generator: generator for generator in generators}


def tuple_map(
    images: Sequence[str],
    generators: Sequence[str],
) -> dict[str, str]:
    return dict(zip(generators, images, strict=True))


def word_power(word: str, exponent: int) -> str:
    if exponent < 0:
        word = inverse_word(word)
        exponent = -exponent
    return free_reduce(word * exponent)


def d_tail(eta: int, epsilon: int, delta: int) -> str:
    return free_reduce(
        word_power("q", eta)
        + word_power(W, epsilon)
        + word_power(D, delta)
    )


def rotations(word: str) -> tuple[str, ...]:
    return tuple(
        word[index:] + word[:index]
        for index in range(len(word))
    )


def signed_rotations(word: str) -> tuple[str, ...]:
    return rotations(word) + rotations(inverse_word(word))


@lru_cache(maxsize=None)
def second_kind_automorphisms(
    generators: tuple[str, ...],
) -> tuple[tuple[str, ...], ...]:
    signed = tuple(
        letter
        for generator in generators
        for letter in (generator, generator.upper())
    )
    identity = tuple(generators)
    maps: set[tuple[str, ...]] = set()
    for multiplier in signed:
        other_letters = tuple(
            letter
            for letter in signed
            if letter not in (
                multiplier,
                INVERSE_LETTER[multiplier],
            )
        )
        for mask in range(1 << len(other_letters)):
            subset = {multiplier}
            subset.update(
                letter
                for index, letter in enumerate(other_letters)
                if mask & (1 << index)
            )
            images: dict[str, str] = {}
            for generator in generators:
                if generator in (
                    multiplier,
                    INVERSE_LETTER[multiplier],
                ):
                    images[generator] = generator
                    continue
                positive = generator in subset
                negative = generator.upper() in subset
                if positive and not negative:
                    images[generator] = generator + multiplier
                elif negative and not positive:
                    images[generator] = (
                        INVERSE_LETTER[multiplier] + generator
                    )
                elif positive and negative:
                    images[generator] = (
                        INVERSE_LETTER[multiplier]
                        + generator
                        + multiplier
                    )
                else:
                    images[generator] = generator
            maps.add(tuple(
                images[generator] for generator in generators
            ))
    maps.discard(identity)
    return tuple(sorted(maps))


@lru_cache(maxsize=None)
def first_kind_automorphisms(
    generators: tuple[str, ...],
) -> tuple[tuple[str, ...], ...]:
    maps: set[tuple[str, ...]] = set()
    for permuted in permutations(generators):
        for signs in product((1, -1), repeat=len(generators)):
            maps.add(tuple(
                letter if sign == 1 else letter.upper()
                for letter, sign in zip(permuted, signs, strict=True)
            ))
    return tuple(sorted(maps))


@lru_cache(maxsize=None)
def whitehead_reduce(
    words: tuple[str, ...],
    generators: tuple[str, ...],
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[int, ...]]:
    current = canonical_tuple(words)
    combined = identity_map(generators)
    lengths = [sum(map(len, current))]
    while True:
        candidates: list[
            tuple[
                int,
                tuple[str, ...],
                tuple[str, ...],
                dict[str, str],
            ]
        ] = []
        for images_tuple in second_kind_automorphisms(generators):
            images = tuple_map(images_tuple, generators)
            child = canonical_tuple(
                substitute(word, images) for word in current
            )
            total = sum(map(len, child))
            if total < lengths[-1]:
                candidates.append(
                    (total, child, images_tuple, images)
                )
        if not candidates:
            return (
                current,
                tuple(combined[generator] for generator in generators),
                tuple(lengths),
            )
        total, current, _, images = min(
            candidates,
            key=lambda item: (item[0], item[1], item[2]),
        )
        combined = compose(images, combined, generators)
        lengths.append(total)


def is_primitive_word(
    word: str,
    generators: tuple[str, ...],
) -> bool:
    minimum, _, _ = whitehead_reduce((word,), generators)
    return len(minimum[0]) == 1


def is_primitive_pair(
    left: str,
    right: str,
    generators: tuple[str, ...],
) -> bool:
    minimum, _, _ = whitehead_reduce(
        canonical_tuple((left, right)),
        generators,
    )
    return (
        sum(map(len, minimum)) == 2
        and len(set(letter.lower() for letter in minimum)) == 2
    )


def whitehead_graph(word: str) -> dict[str, set[str]]:
    word = cyclic_reduce(word)
    graph = {letter: set() for letter in LETTERS4}
    for left, right in zip(word, word[1:] + word[:1]):
        first = INVERSE_LETTER[left]
        graph[first].add(right)
        graph[right].add(first)
    return graph


def whitehead_graph_on(
    word: str,
    generators: tuple[str, ...],
) -> dict[str, set[str]]:
    word = cyclic_reduce(word)
    letters = tuple(
        letter
        for generator in generators
        for letter in (generator, generator.upper())
    )
    graph = {letter: set() for letter in letters}
    for left, right in zip(word, word[1:] + word[:1]):
        first = INVERSE_LETTER[left]
        graph[first].add(right)
        graph[right].add(first)
    return graph


def graph_is_connected(
    graph: Mapping[str, set[str]],
    omitted: str | None = None,
) -> bool:
    vertices = [
        vertex for vertex in graph
        if vertex != omitted
    ]
    seen = {vertices[0]}
    frontier = [vertices[0]]
    while frontier:
        vertex = frontier.pop()
        for neighbor in graph[vertex]:
            if neighbor != omitted and neighbor not in seen:
                seen.add(neighbor)
                frontier.append(neighbor)
    return len(seen) == len(vertices)


def passes_primitive_graph_gate(word: str) -> bool:
    return passes_primitive_graph_gate_on(word, GENERATORS4)


def passes_primitive_graph_gate_on(
    word: str,
    generators: tuple[str, ...],
) -> bool:
    if len(word) <= 1:
        return True
    graph = whitehead_graph_on(word, generators)
    if not graph_is_connected(graph):
        return True
    return any(
        not graph_is_connected(graph, omitted=vertex)
        for vertex in graph
    )


def unique_z_straightener(word: str) -> tuple[str, ...]:
    positions = [
        index for index, letter in enumerate(word)
        if letter in "zZ"
    ]
    assert len(positions) == 1
    index = positions[0]
    left = word[:index]
    z_letter = word[index]
    right = word[index + 1:]
    assert not set(left + right) & set("zZ")
    images = identity_map(GENERATORS4)
    if z_letter == "z":
        images["z"] = free_reduce(
            inverse_word(left) + "z" + inverse_word(right)
        )
    else:
        images["z"] = free_reduce(right + "Z" + left)
    assert canonical_relator(substitute(word, images)) == "Z"
    return tuple(images[generator] for generator in GENERATORS4)


def relabel_to_xy(
    words: Sequence[str],
    generators: tuple[str, str],
) -> tuple[str, ...]:
    images = {
        generators[0]: "x",
        generators[1]: "y",
    }
    return canonical_tuple(
        substitute(word, images) for word in words
    )


@lru_cache(maxsize=None)
def rank2_aut_canonical(words: tuple[str, str]) -> tuple[str, str]:
    generators = ("x", "y")
    minimum, _, _ = whitehead_reduce(
        canonical_tuple(words),
        generators,
    )
    floor = sum(map(len, minimum))
    seen = {minimum}
    queue = deque([minimum])
    maps = (
        second_kind_automorphisms(generators)
        + first_kind_automorphisms(generators)
    )
    while queue:
        state = queue.popleft()
        for images_tuple in maps:
            images = tuple_map(images_tuple, generators)
            child = canonical_tuple(
                substitute(word, images) for word in state
            )
            if sum(map(len, child)) != floor or child in seen:
                continue
            seen.add(child)
            queue.append(child)
    return min(seen)


def delete_coordinates(
    words: Sequence[str],
    images_tuple: tuple[str, ...],
    generators: tuple[str, ...],
    killed: set[str],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    images = tuple_map(images_tuple, generators)
    surviving_generators = tuple(
        generator for generator in generators
        if generator not in killed
    )
    quotient = {
        generator: "" if generator in killed else generator
        for generator in generators
    }
    return (
        tuple(
            canonical_relator(
                substitute(substitute(word, images), quotient)
            )
            for word in words
        ),
        surviving_generators,
    )


def primitive_terminal_generators(
    words: Sequence[str],
    images_tuple: tuple[str, ...],
    generators: tuple[str, ...],
) -> set[str]:
    images = tuple_map(images_tuple, generators)
    terminals = {
        canonical_relator(substitute(word, images)).lower()
        for word in words
    }
    assert all(
        len(generator) == 1 and generator in generators
        for generator in terminals
    )
    return terminals


def enumerate_states() -> tuple[
    dict[StateKey, int],
    dict[StateKey, tuple[tuple[str, str], ...]],
]:
    multiplicities: dict[StateKey, int] = defaultdict(int)
    survivors: dict[
        StateKey,
        tuple[tuple[str, str], ...],
    ] = {}
    carriers = {"A": A, "W": W, "D": D}
    for eta, epsilon in ((1, 1), (-1, 1), (-1, -1)):
        for delta in (1, -1):
            q_word = d_tail(eta, epsilon, delta)
            rows = {**carriers, "Q": q_word}
            for carrier, carrier_word in carriers.items():
                for direction in ("Q<-carrier", "carrier<-Q"):
                    if direction == "Q<-carrier":
                        target_name = "Q"
                        target = q_word
                        source = carrier_word
                    else:
                        target_name = carrier
                        target = carrier_word
                        source = q_word
                    remaining = tuple(sorted(
                        (name, word)
                        for name, word in rows.items()
                        if name != target_name
                    ))
                    for target_rotation in rotations(target):
                        for source_rotation in signed_rotations(source):
                            child = canonical_relator(
                                target_rotation + source_rotation
                            )
                            key = (
                                eta,
                                epsilon,
                                delta,
                                carrier,
                                direction,
                                child,
                            )
                            multiplicities[key] += 1
                            survivors[key] = remaining
    return dict(multiplicities), survivors


def classify_one_edge_creation() -> dict[str, object]:
    multiplicities, survivor_rows = enumerate_states()
    global_children = {
        key[-1] for key in multiplicities
    }
    graph_positive_states = {
        key for key in multiplicities
        if passes_primitive_graph_gate(key[-1])
    }
    primitive_children = {
        child for child in {
            key[-1] for key in graph_positive_states
        }
        if is_primitive_word(child, GENERATORS4)
    }
    primitive_states = {
        key for key in graph_positive_states
        if key[-1] in primitive_children
    }
    primitive_states_by_direction = Counter(
        key[4] for key in primitive_states
    )
    primitive_states_by_carrier_child = Counter(
        (key[3], key[-1]) for key in primitive_states
    )
    primitive_literals_by_carrier_child: Counter[
        tuple[str, str]
    ] = Counter()
    for key in primitive_states:
        primitive_literals_by_carrier_child[
            (key[3], key[-1])
        ] += multiplicities[key]

    unchanged_base_pair_floors = {}
    for left_name, left, right_name, right in (
        ("A", A, "W", W),
        ("A", A, "D", D),
        ("W", W, "D", D),
    ):
        minimum, _, _ = whitehead_reduce(
            canonical_tuple((left, right)),
            GENERATORS4,
        )
        unchanged_base_pair_floors[
            (left_name, right_name)
        ] = sum(map(len, minimum))
    unchanged_q_pair_count = 0
    for eta, epsilon in ((1, 1), (-1, 1), (-1, -1)):
        for delta in (1, -1):
            q_word = d_tail(eta, epsilon, delta)
            unchanged_q_pair_count += sum(
                is_primitive_pair(
                    q_word,
                    carrier,
                    GENERATORS4,
                )
                for carrier in (A, W, D)
            )

    direct_endpoints: list[tuple[str, str]] = []
    sequential_endpoints: list[tuple[str, str]] = []
    quotient_primitive_counts: Counter[int] = Counter()
    quotient_primitive_pair_count = 0

    for key in sorted(primitive_states):
        child = key[-1]
        survivors = survivor_rows[key]

        for _, partner in survivors:
            pair_minimum, pair_images, _ = whitehead_reduce(
                canonical_tuple((child, partner)),
                GENERATORS4,
            )
            if (
                sum(map(len, pair_minimum)) != 2
                or len({
                    letter.lower() for letter in pair_minimum
                }) != 2
            ):
                continue
            killed = primitive_terminal_generators(
                (child, partner),
                pair_images,
                GENERATORS4,
            )
            unpaired = tuple(
                word for _, word in survivors
                if word != partner
            )
            quotient, generators2 = delete_coordinates(
                unpaired,
                pair_images,
                GENERATORS4,
                killed,
            )
            assert len(quotient) == 2
            assert len(generators2) == 2
            direct_endpoints.append(rank2_aut_canonical(
                relabel_to_xy(quotient, generators2)
            ))

        child_minimum, child_images, _ = whitehead_reduce(
            (child,),
            GENERATORS4,
        )
        assert len(child_minimum[0]) == 1
        killed_child = primitive_terminal_generators(
            (child,),
            child_images,
            GENERATORS4,
        )
        quotient_words, generators3 = delete_coordinates(
            tuple(word for _, word in survivors),
            child_images,
            GENERATORS4,
            killed_child,
        )
        primitive_indices = [
            index
            for index, word in enumerate(quotient_words)
            if is_primitive_word(word, generators3)
        ]
        quotient_primitive_counts[len(primitive_indices)] += 1
        for left_index in range(3):
            for right_index in range(left_index + 1, 3):
                if is_primitive_pair(
                    quotient_words[left_index],
                    quotient_words[right_index],
                    generators3,
                ):
                    quotient_primitive_pair_count += 1

        for primitive_index in primitive_indices:
            second = quotient_words[primitive_index]
            second_minimum, second_images, _ = whitehead_reduce(
                (second,),
                generators3,
            )
            assert len(second_minimum[0]) == 1
            killed_second = primitive_terminal_generators(
                (second,),
                second_images,
                generators3,
            )
            final_words, generators2 = delete_coordinates(
                tuple(
                    word
                    for index, word in enumerate(quotient_words)
                    if index != primitive_index
                ),
                second_images,
                generators3,
                killed_second,
            )
            assert len(final_words) == 2
            assert len(generators2) == 2
            sequential_endpoints.append(rank2_aut_canonical(
                relabel_to_xy(final_words, generators2)
            ))

    known_floor23 = (
        "YXXXXyxxx",
        "YYXXXXyxxxYxyx",
    )
    known_floor27 = (
        "YYYXXXX",
        "YYYXXXXYxxxxyyyXyXYx",
    )
    known_endpoints = {
        rank2_aut_canonical(known_floor23),
        rank2_aut_canonical(known_floor27),
    }

    return {
        "symmetry_reduced_literal_move_count": sum(
            multiplicities.values()
        ),
        "full_oriented_literal_move_count": 2 * sum(
            multiplicities.values()
        ),
        "direction_tagged_state_count": len(multiplicities),
        "global_child_count": len(global_children),
        "graph_positive_state_count": len(graph_positive_states),
        "primitive_children": primitive_children,
        "primitive_state_count": len(primitive_states),
        "primitive_literal_count": sum(
            multiplicities[key] for key in primitive_states
        ),
        "primitive_states_by_direction": (
            primitive_states_by_direction
        ),
        "primitive_states_by_carrier_child": (
            primitive_states_by_carrier_child
        ),
        "primitive_literals_by_carrier_child": (
            primitive_literals_by_carrier_child
        ),
        "unchanged_base_pair_floors": (
            unchanged_base_pair_floors
        ),
        "unchanged_q_pair_count": unchanged_q_pair_count,
        "direct_endpoint_counts": Counter(
            direct_endpoints
        ),
        "quotient_primitive_counts": quotient_primitive_counts,
        "quotient_primitive_pair_count": (
            quotient_primitive_pair_count
        ),
        "sequential_endpoint_counts": Counter(
            sequential_endpoints
        ),
        "new_endpoint_count": sum(
            endpoint not in known_endpoints
            for endpoint in direct_endpoints + sequential_endpoints
        ),
        "whitehead_map_counts": {
            rank: len(second_kind_automorphisms(generators))
            for rank, generators in (
                (4, GENERATORS4),
                (3, ("x", "t", "z")),
                (2, ("x", "y")),
            )
        },
    }


@lru_cache(maxsize=1)
def result() -> dict[str, object]:
    return classify_one_edge_creation()


def test_edge_image_and_primitive_gate_are_complete():
    observed = result()
    assert observed["whitehead_map_counts"] == {
        4: 504,
        3: 90,
        2: 12,
    }
    assert observed["symmetry_reduced_literal_move_count"] == 12_992
    assert observed["full_oriented_literal_move_count"] == 25_984
    assert observed["direction_tagged_state_count"] == 9_480
    assert observed["global_child_count"] == 4_720
    assert observed["graph_positive_state_count"] == 88
    assert observed["primitive_state_count"] == 28
    assert observed["primitive_literal_count"] == 298
    assert observed["primitive_states_by_direction"] == {
        "Q<-carrier": 14,
        "carrier<-Q": 14,
    }
    assert observed["primitive_children"] == {
        "QQQTqXQzttttqXXX",
        "QTTTTZqxQtqxxx",
        "QTqXQzQTzxZ",
        "QTqXQzQzXZt",
        "QTzxZ",
        "QzXZt",
    }
    assert observed["primitive_states_by_carrier_child"] == {
        ("A", "QTqXQzQTzxZ"): 2,
        ("A", "QTqXQzQzXZt"): 2,
        ("W", "QTzxZ"): 6,
        ("W", "QzXZt"): 6,
        ("D", "QQQTqXQzttttqXXX"): 8,
        ("D", "QTTTTZqxQtqxxx"): 4,
    }
    assert observed["primitive_literals_by_carrier_child"] == {
        ("A", "QTqXQzQTzxZ"): 20,
        ("A", "QTqXQzQzXZt"): 20,
        ("W", "QTzxZ"): 100,
        ("W", "QzXZt"): 98,
        ("D", "QQQTqXQzttttqXXX"): 40,
        ("D", "QTTTTZqxQtqxxx"): 20,
    }


def test_unchanged_pairs_are_not_silent_primitive_routes():
    observed = result()
    assert observed["unchanged_base_pair_floors"] == {
        ("A", "W"): 8,
        ("A", "D"): 11,
        ("W", "D"): 16,
    }
    assert observed["unchanged_q_pair_count"] == 0


def test_direct_primitive_pairs_reach_only_known_endpoints():
    observed = result()
    assert observed["direct_endpoint_counts"] == {
        ("XXXXYYxyxYxxxy", "XXXXYxxxy"): 18,
        ("XXXXYYY", "XXXXYYYxYXyXyyyxxxxY"): 12,
    }


def test_sequential_deletions_reach_only_known_endpoints():
    observed = result()
    assert observed["quotient_primitive_counts"] == {
        1: 24,
        2: 4,
    }
    assert observed["quotient_primitive_pair_count"] == 0
    assert observed["sequential_endpoint_counts"] == {
        ("XXXXYYxyxYxxxy", "XXXXYxxxy"): 20,
        ("XXXXYYY", "XXXXYYYxYXyXyyyxxxxY"): 12,
    }
    assert observed["new_endpoint_count"] == 0


@lru_cache(maxsize=1)
def classify_carrier_edge_creation() -> dict[str, object]:
    carriers = {"A": A, "W": W, "D": D}
    pair_names = (("A", "W"), ("A", "D"), ("W", "D"))
    global_children: dict[str, set[str]] = {}
    direction_children: dict[
        tuple[str, str],
        Counter[str],
    ] = {}
    one_checkpoint_literal_count = 0

    for left_name, right_name in pair_names:
        pair_name = f"{left_name}-{right_name}"
        left = carriers[left_name]
        right = carriers[right_name]
        global_children[pair_name] = set()
        for target_name, source_name in (
            (left_name, right_name),
            (right_name, left_name),
        ):
            target = carriers[target_name]
            source = carriers[source_name]
            counts: Counter[str] = Counter()
            for target_rotation in rotations(target):
                for source_rotation in signed_rotations(source):
                    child = canonical_relator(
                        target_rotation + source_rotation
                    )
                    counts[child] += 1
                    global_children[pair_name].add(child)
            direction_children[
                (pair_name, f"{target_name}<-{source_name}")
            ] = counts
            one_checkpoint_literal_count += sum(counts.values())

    aw_children = global_children["A-W"]
    assert all(
        sum(letter in "zZ" for letter in child) == 1
        for child in aw_children
    )
    primitive_children = {
        "A-W": set(aw_children),
        "A-D": {
            child for child in global_children["A-D"]
            if passes_primitive_graph_gate(child)
            and is_primitive_word(child, GENERATORS4)
        },
        "W-D": {
            child for child in global_children["W-D"]
            if passes_primitive_graph_gate(child)
            and is_primitive_word(child, GENERATORS4)
        },
    }
    child_minimum_distributions = {
        pair_name: Counter(
            len(whitehead_reduce(
                (child,),
                GENERATORS4,
            )[0][0])
            for child in global_children[pair_name]
        )
        for pair_name in ("A-D", "W-D")
    }
    primitive_wd_chains = {
        child: whitehead_reduce(
            (child,),
            GENERATORS4,
        )[2]
        for child in primitive_children["W-D"]
    }

    aw_child_d_pair_floor_distribution: Counter[int] = Counter()
    for child in aw_children:
        minimum, _, _ = whitehead_reduce(
            canonical_tuple((child, D)),
            GENERATORS4,
        )
        aw_child_d_pair_floor_distribution[
            sum(map(len, minimum))
        ] += 1
    aw_child_w_pair_floor_distribution = Counter(
        sum(map(len, whitehead_reduce(
            canonical_tuple((child, W)),
            GENERATORS4,
        )[0]))
        for child in aw_children
    )
    aw_child_a_pair_floor_distribution = Counter(
        sum(map(len, whitehead_reduce(
            canonical_tuple((child, A)),
            GENERATORS4,
        )[0]))
        for child in aw_children
    )
    wd_child_d_pair_floor_distribution = Counter(
        sum(map(len, whitehead_reduce(
            canonical_tuple((child, D)),
            GENERATORS4,
        )[0]))
        for child in primitive_children["W-D"]
    )
    wd_child_w_pair_floor_distribution = Counter(
        sum(map(len, whitehead_reduce(
            canonical_tuple((child, W)),
            GENERATORS4,
        )[0]))
        for child in primitive_children["W-D"]
    )
    wd_child_a_pair_floor_distribution = Counter(
        sum(map(len, whitehead_reduce(
            canonical_tuple((child, A)),
            GENERATORS4,
        )[0]))
        for child in primitive_children["W-D"]
    )
    unchanged_pair_floors = {
        "A changed; W,D survive": sum(map(len, whitehead_reduce(
            canonical_tuple((W, D)),
            GENERATORS4,
        )[0])),
        "W changed; A,D survive": sum(map(len, whitehead_reduce(
            canonical_tuple((A, D)),
            GENERATORS4,
        )[0])),
        "D changed; A,W survive": sum(map(len, whitehead_reduce(
            canonical_tuple((A, W)),
            GENERATORS4,
        )[0])),
    }

    direction_roles: dict[
        tuple[str, str],
        tuple[str, str],
    ] = {}
    for left_name, right_name in pair_names:
        pair_name = f"{left_name}-{right_name}"
        direction_roles[
            (pair_name, f"{left_name}<-{right_name}")
        ] = (left_name, right_name)
        direction_roles[
            (pair_name, f"{right_name}<-{left_name}")
        ] = (right_name, left_name)

    carrier_is_primitive = {
        name: is_primitive_word(word, GENERATORS4)
        for name, word in carriers.items()
    }
    direct_primitive_pair_count = 0
    for direction_key, child_counts in direction_children.items():
        pair_name, _ = direction_key
        target_name, _ = direction_roles[direction_key]
        for child in (
            set(child_counts) & primitive_children[pair_name]
        ):
            for partner_name, partner in carriers.items():
                if partner_name == target_name:
                    continue
                if not carrier_is_primitive[partner_name]:
                    continue
                if is_primitive_pair(
                    child,
                    partner,
                    GENERATORS4,
                ):
                    direct_primitive_pair_count += 6

    quotient_primitive_counts: Counter[int] = Counter()
    quotient_primitive_pair_count = 0
    sequential_endpoints: list[tuple[str, str]] = []
    checkpoints = tuple(
        (eta, epsilon, delta)
        for eta, epsilon in ((1, 1), (-1, 1), (-1, -1))
        for delta in (1, -1)
    )

    for direction_key, child_counts in direction_children.items():
        pair_name, _ = direction_key
        target_name, _ = direction_roles[direction_key]
        for child in sorted(
            set(child_counts) & primitive_children[pair_name]
        ):
            if pair_name == "A-W":
                child_images = unique_z_straightener(child)
            else:
                child_minimum, child_images, _ = whitehead_reduce(
                    (child,),
                    GENERATORS4,
                )
                assert len(child_minimum[0]) == 1
            killed_child = primitive_terminal_generators(
                (child,),
                child_images,
                GENERATORS4,
            )

            for eta, epsilon, delta in checkpoints:
                rows = {
                    **carriers,
                    "Q": d_tail(eta, epsilon, delta),
                }
                survivor_rows = tuple(sorted(
                    (name, word)
                    for name, word in rows.items()
                    if name != target_name
                ))
                quotient_words, generators3 = delete_coordinates(
                    tuple(word for _, word in survivor_rows),
                    child_images,
                    GENERATORS4,
                    killed_child,
                )
                primitive_indices = [
                    index
                    for index, word in enumerate(quotient_words)
                    if passes_primitive_graph_gate_on(
                        word,
                        generators3,
                    )
                    and is_primitive_word(word, generators3)
                ]
                quotient_primitive_counts[
                    len(primitive_indices)
                ] += 1

                if len(primitive_indices) >= 2:
                    for left_index in range(3):
                        for right_index in range(
                            left_index + 1,
                            3,
                        ):
                            quotient_primitive_pair_count += (
                                is_primitive_pair(
                                    quotient_words[left_index],
                                    quotient_words[right_index],
                                    generators3,
                                )
                            )

                for primitive_index in primitive_indices:
                    second = quotient_words[primitive_index]
                    second_minimum, second_images, _ = (
                        whitehead_reduce(
                            (second,),
                            generators3,
                        )
                    )
                    assert len(second_minimum[0]) == 1
                    killed_second = primitive_terminal_generators(
                        (second,),
                        second_images,
                        generators3,
                    )
                    final_words, generators2 = delete_coordinates(
                        tuple(
                            word
                            for index, word in enumerate(
                                quotient_words
                            )
                            if index != primitive_index
                        ),
                        second_images,
                        generators3,
                        killed_second,
                    )
                    sequential_endpoints.append(
                        rank2_aut_canonical(
                            relabel_to_xy(
                                final_words,
                                generators2,
                            )
                        )
                    )

    known_ak3 = ("XXXXYYY", "XYxYXy")

    return {
        "symmetry_reduced_literal_move_count": (
            6 * one_checkpoint_literal_count
        ),
        "full_oriented_literal_move_count": (
            12 * one_checkpoint_literal_count
        ),
        "checkpoint_direction_state_count": 6 * sum(
            len(children)
            for children in direction_children.values()
        ),
        "global_child_count": sum(
            len(children) for children in global_children.values()
        ),
        "global_children_by_pair": {
            pair_name: len(children)
            for pair_name, children in global_children.items()
        },
        "primitive_children_by_pair": {
            pair_name: len(children)
            for pair_name, children in primitive_children.items()
        },
        "primitive_wd_children": primitive_children["W-D"],
        "child_minimum_distributions": (
            child_minimum_distributions
        ),
        "primitive_wd_chains": primitive_wd_chains,
        "carrier_is_primitive": carrier_is_primitive,
        "direct_primitive_pair_count": (
            direct_primitive_pair_count
        ),
        "aw_child_d_pair_floor_distribution": (
            aw_child_d_pair_floor_distribution
        ),
        "directional_source_pair_floor_distributions": {
            "A<-W with W": aw_child_w_pair_floor_distribution,
            "W<-A with A": aw_child_a_pair_floor_distribution,
            "W<-D with D": wd_child_d_pair_floor_distribution,
            "D<-W with W": wd_child_w_pair_floor_distribution,
            "W-D child with A": (
                wd_child_a_pair_floor_distribution
            ),
        },
        "unchanged_pair_floors": unchanged_pair_floors,
        "quotient_primitive_counts": quotient_primitive_counts,
        "quotient_primitive_pair_count": (
            quotient_primitive_pair_count
        ),
        "sequential_endpoint_counts": Counter(
            sequential_endpoints
        ),
        "new_endpoint_count": sum(
            endpoint != known_ak3
            for endpoint in sequential_endpoints
        ),
    }


def test_carrier_edge_image_and_primitive_children_are_complete():
    observed = classify_carrier_edge_creation()
    assert observed["symmetry_reduced_literal_move_count"] == 5_544
    assert observed["full_oriented_literal_move_count"] == 11_088
    assert observed["checkpoint_direction_state_count"] == 4_104
    assert observed["global_child_count"] == 342
    assert observed["global_children_by_pair"] == {
        "A-W": 186,
        "A-D": 58,
        "W-D": 98,
    }
    assert observed["primitive_children_by_pair"] == {
        "A-W": 186,
        "A-D": 0,
        "W-D": 4,
    }
    assert observed["primitive_wd_children"] == {
        "QQTqXQTzxttttqXXX",
        "QQTqXQtzXttttqXXX",
        "QTTTTZqxQtqXZtzqxxx",
        "QTTTTZqxQtqxZTzqxxx",
    }
    assert observed["child_minimum_distributions"] == {
        "A-D": {9: 11, 11: 11, 13: 36},
        "W-D": {
            1: 4,
            13: 3,
            14: 7,
            15: 14,
            16: 28,
            17: 18,
            18: 24,
        },
    }
    assert observed["primitive_wd_chains"] == {
        "QQTqXQTzxttttqXXX": (
            17, 14, 13, 12, 11, 10, 9, 8, 7, 5, 4, 3, 2, 1,
        ),
        "QQTqXQtzXttttqXXX": (
            17, 14, 13, 11, 10, 8, 7, 6, 5, 4, 3, 2, 1,
        ),
        "QTTTTZqxQtqXZtzqxxx": (
            19, 15, 14, 13, 12, 11, 9, 7, 6, 5, 4, 2, 1,
        ),
        "QTTTTZqxQtqxZTzqxxx": (
            19, 15, 14, 13, 11, 10, 8, 7, 6, 5, 4, 3, 2, 1,
        ),
    }


def test_carrier_edges_create_no_direct_primitive_pair():
    observed = classify_carrier_edge_creation()
    assert observed["carrier_is_primitive"] == {
        "A": False,
        "W": True,
        "D": True,
    }
    assert observed["direct_primitive_pair_count"] == 0
    assert observed["aw_child_d_pair_floor_distribution"] == {
        7: 1,
        17: 4,
        18: 2,
        19: 6,
        20: 4,
        21: 16,
        22: 6,
        23: 31,
        25: 116,
    }
    assert observed[
        "directional_source_pair_floor_distributions"
    ] == {
        "A<-W with W": {9: 186},
        "W<-A with A": {8: 186},
        "W<-D with D": {16: 4},
        "D<-W with W": {26: 4},
        "W-D child with A": {8: 4},
    }
    assert observed["unchanged_pair_floors"] == {
        "A changed; W,D survive": 16,
        "W changed; A,D survive": 11,
        "D changed; A,W survive": 8,
    }


def test_carrier_changed_row_first_branches_only_return_to_ak3():
    observed = classify_carrier_edge_creation()
    assert observed["quotient_primitive_counts"] == {
        0: 2_268,
        1: 12,
    }
    assert observed["quotient_primitive_pair_count"] == 0
    assert observed["sequential_endpoint_counts"] == {
        ("XXXXYYY", "XYxYXy"): 12,
    }
    assert observed["new_endpoint_count"] == 0


def test_carrier_cancellation_has_a_uniform_unique_q_return():
    h = "QTqXQz"
    theta = {
        "x": "x",
        "t": "t",
        "z": free_reduce(C + "z"),
        "q": "q",
    }
    kill_z = {"x": "x", "t": "t", "z": "", "q": "q"}
    assert substitute(h, theta) == "z"
    assert substitute(substitute(W, theta), kill_z) == A

    d_zero = "T" + C + "x" + inverse_word(C)
    assert substitute(substitute(D, theta), kill_z) == d_zero

    beta_inverse = {
        "x": "Qxq",
        "t": "t",
        "z": "z",
        "q": "q",
    }
    r_word = "xxxTTTT"
    e_word = "TxtxTX"
    assert substitute(A, beta_inverse) == r_word
    assert substitute(C, beta_inverse) == "xtq"
    assert substitute(d_zero, beta_inverse) == e_word

    for eta, epsilon in ((1, 1), (-1, 1), (-1, -1)):
        for delta in (1, -1):
            q_bar = free_reduce(
                word_power("q", eta)
                + word_power(A, epsilon)
                + word_power(d_zero, delta)
            )
            transformed = substitute(q_bar, beta_inverse)
            expected = free_reduce(
                word_power("q", eta)
                + word_power(r_word, epsilon)
                + word_power(e_word, delta)
            )
            assert transformed == expected
            positions = [
                index
                for index, letter in enumerate(transformed)
                if letter in "qQ"
            ]
            assert len(positions) == 1
            index = positions[0]
            left = transformed[:index]
            q_letter = transformed[index]
            right = transformed[index + 1:]
            straightener = {
                "x": "x",
                "t": "t",
                "q": (
                    free_reduce(
                        inverse_word(left)
                        + "q"
                        + inverse_word(right)
                    )
                    if q_letter == "q"
                    else free_reduce(right + "Q" + left)
                ),
            }
            assert substitute(transformed, straightener) == "q"
            assert substitute(r_word, straightener) == r_word
            assert substitute(e_word, straightener) == e_word

    assert rank2_aut_canonical(relabel_to_xy(
        (r_word, e_word),
        ("x", "t"),
    )) == ("XXXXYYY", "XYxYXy")
