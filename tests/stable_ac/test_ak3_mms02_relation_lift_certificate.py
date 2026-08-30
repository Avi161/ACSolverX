from collections import defaultdict, deque
from dataclasses import dataclass
from hashlib import sha256
from itertools import permutations, product
from math import gcd
from runpy import run_path
import sys


sys.setrecursionlimit(100_000)


A, B, U, V = "xzYXyxZXYxyZ", "XyxZXYXyxzXYxy", "zYX", "Xyz"
M0, M1, R, S = "xYxYXyyXYxyXy", "XyyXYXyxYYxy", "xxxYYYY", "xyxYXY"
WORDS = {"A": A, "B": B, "u": U, "v": V, "M0": M0, "M1": M1, "R": R, "S": S}
SIGNED_INVOLUTION = {"x": "Z", "y": "Y", "z": "X"}
VALUE_LIMIT = 100_000
NODE_BUDGET = 100_000


def inv(word):
    return "".join(letter.swapcase() for letter in reversed(word))


def red(word):
    stack = []
    for letter in word:
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def signed_involution(word):
    return red(
        "".join(
            SIGNED_INVOLUTION[letter]
            if letter.islower()
            else inv(SIGNED_INVOLUTION[letter.lower()])
            for letter in word
        )
    )


def apply_images(word, images):
    return red(
        "".join(
            images[letter]
            if letter.islower()
            else inv(images[letter.lower()])
            for letter in word
        )
    )


def canonical_cyclic_word(word):
    word = red(word)
    while len(word) > 1 and word[0] == word[-1].swapcase():
        word = red(word[1:-1])
    orientations = (word, inv(word))
    return min(
        oriented[index:] + oriented[:index]
        for oriented in orientations
        for index in range(len(oriented))
    )


def canonical_cyclic_pair(pair):
    return tuple(sorted(canonical_cyclic_word(word) for word in pair))


def rank_two_whitehead_automorphisms():
    signed = ("x", "X", "y", "Y")
    unique = {}
    for multiplier in signed:
        others = tuple(
            letter
            for letter in signed
            if letter not in (multiplier, multiplier.swapcase())
        )
        for mask in range(1 << len(others)):
            subset = {multiplier}
            subset.update(
                letter
                for index, letter in enumerate(others)
                if mask & (1 << index)
            )
            images = {}
            for generator in ("x", "y"):
                positive = generator in subset
                negative = generator.upper() in subset
                if generator in (multiplier, multiplier.swapcase()):
                    images[generator] = generator
                elif positive and not negative:
                    images[generator] = generator + multiplier
                elif negative and not positive:
                    images[generator] = multiplier.swapcase() + generator
                elif positive and negative:
                    images[generator] = multiplier.swapcase() + generator + multiplier
                else:
                    images[generator] = generator
            key = tuple(images[generator] for generator in ("x", "y"))
            if key != ("x", "y"):
                unique[key] = images
    return tuple(unique[key] for key in sorted(unique))


def rank_three_whitehead_automorphisms():
    generators = ("x", "y", "z")
    signed = tuple(
        letter
        for generator in generators
        for letter in (generator, generator.upper())
    )
    identity = {generator: generator for generator in generators}
    unique = {}
    for multiplier in signed:
        others = tuple(
            letter
            for letter in signed
            if letter not in (multiplier, multiplier.swapcase())
        )
        for mask in range(1 << len(others)):
            subset = {multiplier}
            subset.update(
                letter
                for index, letter in enumerate(others)
                if mask & (1 << index)
            )
            images = {}
            for generator in generators:
                if generator in (multiplier, multiplier.swapcase()):
                    images[generator] = generator
                    continue
                positive = generator in subset
                negative = generator.upper() in subset
                if positive and not negative:
                    images[generator] = generator + multiplier
                elif negative and not positive:
                    images[generator] = multiplier.swapcase() + generator
                elif positive and negative:
                    images[generator] = multiplier.swapcase() + generator + multiplier
                else:
                    images[generator] = generator
            key = tuple(images[generator] for generator in generators)
            if images != identity:
                unique[key] = images
    return tuple(unique[key] for key in sorted(unique))


def rank_three_exponent_vector(word):
    return tuple(
        word.count(generator) - word.count(generator.upper())
        for generator in "xyz"
    )


def rank_three_pair_minors(pair):
    left, right = map(rank_three_exponent_vector, pair)
    return (
        left[0] * right[1] - left[1] * right[0],
        left[0] * right[2] - left[2] * right[0],
        left[1] * right[2] - left[2] * right[1],
    )


def replay_whitehead_pair_floor(pair, steps):
    current = canonical_cyclic_pair(pair)
    totals = [sum(map(len, current))]
    for images in steps:
        image = canonical_cyclic_pair(
            tuple(apply_images(word, images) for word in current)
        )
        assert sum(map(len, image)) < totals[-1]
        current = image
        totals.append(sum(map(len, current)))
    return current, tuple(totals)


def whitehead_minimum(pair, automorphisms):
    current = canonical_cyclic_pair(pair)
    path = []
    while True:
        candidates = []
        for images in automorphisms:
            image = canonical_cyclic_pair(
                tuple(apply_images(word, images) for word in current)
            )
            if sum(map(len, image)) < sum(map(len, current)):
                candidates.append(
                    (
                        sum(map(len, image)),
                        image,
                        tuple(images[generator] for generator in ("x", "y")),
                    )
                )
        if not candidates:
            return current, tuple(path)
        _, current, step = min(candidates)
        path.append(step)


def exponent_vector(word):
    return (
        word.count("x") - word.count("X"),
        word.count("y") - word.count("Y"),
    )


def matrix_determinant(matrix):
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def matrix_inverse(matrix):
    determinant = matrix_determinant(matrix)
    assert abs(determinant) == 1
    return (
        (matrix[1][1] // determinant, -matrix[0][1] // determinant),
        (-matrix[1][0] // determinant, matrix[0][0] // determinant),
    )


def matrix_multiply(left, right):
    return tuple(
        tuple(
            sum(left[row][middle] * right[middle][column] for middle in range(2))
            for column in range(2)
        )
        for row in range(2)
    )


def ambient_automorphism_representatives(required_matrices):
    generators = (
        {"x": "y", "y": "x"},
        {"x": "X", "y": "y"},
        {"x": "xy", "y": "y"},
    )
    identity_matrix = ((1, 0), (0, 1))
    representatives = {identity_matrix: {"x": "x", "y": "y"}}
    queue = deque(representatives.values())
    while required_matrices - representatives.keys():
        assert queue and len(representatives) < 1_000
        current = queue.popleft()
        for generator in generators:
            image = {
                letter: apply_images(current[letter], generator)
                for letter in ("x", "y")
            }
            matrix = tuple(exponent_vector(image[letter]) for letter in ("x", "y"))
            if matrix not in representatives:
                representatives[matrix] = image
                queue.append(image)
    return representatives


@dataclass(frozen=True)
class Expr:
    kind: str
    args: tuple
    value: str | None
    support: frozenset[str]


def lit(word):
    return Expr("lit", (), word, frozenset())


def leaf(source):
    return Expr("leaf", (source,), WORDS[source], frozenset((source,)))


def is_empty(item):
    return item.kind == "lit" and item.value == ""


def shallow(item):
    return item.kind, item.value, item.support, len(item.args)


def prod(*items):
    items = tuple(item for item in items if not is_empty(item))
    if not items:
        return lit("")
    if len(items) == 1:
        return items[0]
    raw = None if any(item.value is None for item in items) else "".join(item.value for item in items)
    value = red(raw) if raw is not None and len(raw) <= VALUE_LIMIT else None
    return Expr("prod", items, value, frozenset().union(*(item.support for item in items)))


def inverse(item):
    return Expr("inv", (item,), None if item.value is None else inv(item.value), item.support)


def conj(word, item):
    coefficient = word.value if isinstance(word, Expr) else word
    raw = None if coefficient is None or item.value is None else coefficient + item.value + inv(coefficient)
    return Expr("conj", (word, item), red(raw) if raw is not None and len(raw) <= VALUE_LIMIT else None, item.support)


def subst(item, source, image):
    return Expr("subst", (item, source, image), None, (item.support - {source}) | image.support)


def subst_evidence(item, source, equality):
    return Expr("subst-evidence", (item, source, equality.evidence), None, equality.support)


def nodes(item):
    seen, stack = set(), [item]
    while stack:
        node = stack.pop()
        if id(node) in seen:
            continue
        seen.add(id(node))
        assert len(seen) < NODE_BUDGET
        stack.extend(arg for arg in node.args if isinstance(arg, Expr))
    return len(seen)


def leaf_coefficients(item):
    basis = {"A": (1, 0, 0), "B": (0, 1, 0), "u": (0, 0, 1)}
    memo = {}

    def visit(node):
        key = id(node)
        if key in memo:
            return memo[key]
        assert len(memo) < NODE_BUDGET
        if node.kind == "leaf":
            result = basis[node.args[0]]
        elif node.kind == "lit":
            result = (0, 0, 0)
        elif node.kind == "prod":
            children = tuple(visit(child) for child in node.args)
            result = tuple(sum(child[index] for child in children) for index in range(3))
        elif node.kind == "inv":
            result = tuple(-coefficient for coefficient in visit(node.args[0]))
        elif node.kind == "conj":
            result = visit(node.args[1])
        else:
            raise AssertionError(node.kind)
        memo[key] = result
        return result

    return visit(item)


def _laurent_add(left, right):
    result = dict(left)
    for degree, coefficient in right.items():
        result[degree] = result.get(degree, 0) + coefficient
    return {
        degree: coefficient
        for degree, coefficient in result.items()
        if coefficient
    }


def _laurent_shift(poly, degree, scalar=1):
    return {
        source_degree + degree: scalar * coefficient
        for source_degree, coefficient in poly.items()
        if scalar * coefficient
    }


def _cyclic_quotient_exponent(word):
    return sum(1 if letter.islower() else -1 for letter in word)


def _coordinate_add(left, right):
    return (
        _laurent_add(left[0], right[0]),
        _laurent_add(left[1], right[1]),
    )


def _coordinate_shift(coordinate, degree, scalar=1):
    return (
        _laurent_shift(coordinate[0], degree, scalar),
        _laurent_shift(coordinate[1], degree, scalar),
    )


def _cyclic_expression_degree_visit(node, memo, replacements=()):
    key = id(node), tuple((name, id(image)) for name, image in replacements)
    if key in memo:
        return memo[key]

    replacement_map = dict(replacements)
    if node.kind == "leaf":
        name = node.args[0]
        if name in replacement_map:
            reduced_replacements = tuple(
                pair for pair in replacements if pair[0] != name
            )
            result = _cyclic_expression_degree_visit(
                replacement_map[name],
                memo,
                reduced_replacements,
            )
        else:
            result = {"A": 0, "B": 0, "u": -1, "v": 1}[name]
    elif node.kind == "lit":
        result = _cyclic_quotient_exponent(node.value)
    elif node.kind == "prod":
        result = sum(
            _cyclic_expression_degree_visit(child, memo, replacements)
            for child in node.args
        )
    elif node.kind == "inv":
        result = -_cyclic_expression_degree_visit(node.args[0], memo, replacements)
    elif node.kind == "conj":
        result = _cyclic_expression_degree_visit(node.args[1], memo, replacements)
    elif node.kind == "subst":
        source, image = node.args[1:]
        next_replacements = tuple(
            pair for pair in replacements if pair[0] != source
        ) + ((source, image),)
        result = _cyclic_expression_degree_visit(
            node.args[0],
            memo,
            tuple(sorted(next_replacements)),
        )
    else:
        raise AssertionError(node.kind)

    memo[key] = result
    return result


def cyclic_expression_degree(item):
    return _cyclic_expression_degree_visit(item, {})


def cyclic_evidence_coordinates(item):
    memo = {}
    degree_memo = {}

    def visit(node):
        key = id(node)
        if key in memo:
            return memo[key]

        if node.kind == "leaf":
            name = node.args[0]
            assert name in ("A", "B")
            result = ({0: 1}, {}) if name == "A" else ({}, {0: 1})
        elif node.kind == "lit":
            assert red(node.value) == ""
            result = ({}, {})
        elif node.kind == "prod":
            result = ({}, {})
            for child in node.args:
                result = _coordinate_add(result, visit(child))
        elif node.kind == "inv":
            result = _coordinate_shift(visit(node.args[0]), 0, -1)
        elif node.kind == "conj":
            conjugator = node.args[0]
            degree = (
                _cyclic_expression_degree_visit(conjugator, degree_memo)
                if isinstance(conjugator, Expr)
                else _cyclic_quotient_exponent(conjugator)
            )
            result = _coordinate_shift(visit(node.args[1]), -degree)
        else:
            raise AssertionError(node.kind)

        memo[key] = result
        return result

    return visit(item)


def cyclic_substitution_coordinates(item, source, difference_coordinates):
    memo = {}
    degree_memo = {}

    def visit(node):
        key = id(node)
        if key in memo:
            return memo[key]

        if node.kind == "leaf":
            result = difference_coordinates if node.args[0] == source else ({}, {})
        elif node.kind == "lit":
            result = ({}, {})
        elif node.kind == "prod":
            result = ({}, {})
            prefix_degree = 0
            for child in node.args:
                result = _coordinate_add(
                    result,
                    _coordinate_shift(visit(child), -prefix_degree),
                )
                prefix_degree += _cyclic_expression_degree_visit(child, degree_memo)
        elif node.kind == "inv":
            result = _coordinate_shift(
                visit(node.args[0]),
                _cyclic_expression_degree_visit(node.args[0], degree_memo),
                -1,
            )
        elif node.kind == "conj":
            conjugator = node.args[0]
            degree = (
                _cyclic_expression_degree_visit(conjugator, degree_memo)
                if isinstance(conjugator, Expr)
                else _cyclic_quotient_exponent(conjugator)
            )
            result = _coordinate_shift(visit(node.args[1]), -degree)
        else:
            raise AssertionError(node.kind)

        memo[key] = result
        return result

    return visit(item)


A5_IMAGES = {
    "x": (0, 1, 3, 4, 2),
    "y": (0, 2, 3, 1, 4),
    "z": (2, 0, 1, 3, 4),
}
A5_IDENTITY = tuple(range(5))


def compose_permutations(left, right):
    return tuple(left[right[index]] for index in range(5))


def invert_permutation(value):
    result = [0] * 5
    for index, image in enumerate(value):
        result[image] = index
    return tuple(result)


def evaluate_permutation_word(word):
    result = A5_IDENTITY
    for letter in word:
        image = A5_IMAGES[letter.lower()]
        if letter.isupper():
            image = invert_permutation(image)
        result = compose_permutations(result, image)
    return result


def expression_permutation(item, memo=None):
    if memo is None:
        memo = {}
    key = id(item)
    if key in memo:
        return memo[key]

    if item.kind == "leaf":
        name = item.args[0]
        result = (
            A5_IDENTITY
            if name in ("A", "B")
            else evaluate_permutation_word(WORDS[name])
        )
    elif item.kind == "lit":
        result = evaluate_permutation_word(item.value)
    elif item.kind == "prod":
        result = A5_IDENTITY
        for child in item.args:
            result = compose_permutations(
                result,
                expression_permutation(child, memo),
            )
    elif item.kind == "inv":
        result = invert_permutation(expression_permutation(item.args[0], memo))
    elif item.kind == "conj":
        conjugator = item.args[0]
        conjugator_value = (
            expression_permutation(conjugator, memo)
            if isinstance(conjugator, Expr)
            else evaluate_permutation_word(conjugator)
        )
        result = compose_permutations(
            compose_permutations(
                conjugator_value,
                expression_permutation(item.args[1], memo),
            ),
            invert_permutation(conjugator_value),
        )
    else:
        raise AssertionError(item.kind)

    memo[key] = result
    return result


def _group_ring_add(left, right):
    result = dict(left)
    for group_element, coefficient in right.items():
        result[group_element] = result.get(group_element, 0) + coefficient
        if result[group_element] == 0:
            del result[group_element]
    return result


def finite_quotient_evidence_coordinates(item):
    memo = {}
    value_memo = {}

    def visit(node):
        key = id(node)
        if key in memo:
            return memo[key]

        if node.kind == "leaf":
            name = node.args[0]
            assert name in ("A", "B")
            result = (
                ({A5_IDENTITY: 1}, {})
                if name == "A"
                else ({}, {A5_IDENTITY: 1})
            )
        elif node.kind == "lit":
            assert expression_permutation(node, value_memo) == A5_IDENTITY
            result = ({}, {})
        elif node.kind == "prod":
            result = ({}, {})
            for child in node.args:
                child_coordinates = visit(child)
                result = (
                    _group_ring_add(result[0], child_coordinates[0]),
                    _group_ring_add(result[1], child_coordinates[1]),
                )
        elif node.kind == "inv":
            child_coordinates = visit(node.args[0])
            result = tuple(
                {
                    group_element: -coefficient
                    for group_element, coefficient in coordinate.items()
                }
                for coordinate in child_coordinates
            )
        elif node.kind == "conj":
            conjugator = node.args[0]
            conjugator_value = (
                expression_permutation(conjugator, value_memo)
                if isinstance(conjugator, Expr)
                else evaluate_permutation_word(conjugator)
            )
            inverse_conjugator = invert_permutation(conjugator_value)
            child_coordinates = visit(node.args[1])
            result = tuple(
                {
                    compose_permutations(group_element, inverse_conjugator): coefficient
                    for group_element, coefficient in coordinate.items()
                }
                for coordinate in child_coordinates
            )
        else:
            raise AssertionError(node.kind)

        memo[key] = result
        return result

    return visit(item)


@dataclass(frozen=True)
class Proof:
    left: Expr
    right: Expr
    evidence: Expr
    support: frozenset[str]
    rule: str
    children: tuple = ()


def same(left, right):
    return left is right or (left.value is not None and left.value == right.value)


def refl(item):
    return Proof(item, item, lit(""), frozenset(), "refl")


def sym(proof):
    return Proof(proof.right, proof.left, inverse(proof.evidence), proof.support, "sym", (proof,))


def trans(first, second):
    assert same(first.right, second.left)
    return Proof(first.left, second.right, prod(first.evidence, second.evidence), first.support | second.support, "trans", (first, second))


def pprod(first, second):
    return Proof(prod(first.left, second.left), prod(first.right, second.right), prod(first.evidence, conj(first.right, second.evidence)), first.support | second.support, "prod", (first, second))


def pinv(proof):
    return Proof(inverse(proof.left), inverse(proof.right), conj(inverse(proof.left), inverse(proof.evidence)), proof.support, "inv", (proof,))


def pconj(word, proof):
    return Proof(conj(word, proof.left), conj(word, proof.right), conj(word, proof.evidence), proof.support, "conj", (proof,))


def psubst(item, source, equality):
    assert equality.right.kind == "leaf" and equality.right.args[0] == source
    return Proof(subst(item, source, equality.left), item, subst_evidence(item, source, equality), equality.support, "subst", (equality,))


def verify(proof):
    seen, stack = set(), [proof]
    while stack:
        proof = stack.pop()
        if id(proof) in seen:
            continue
        seen.add(id(proof))
        assert len(seen) < NODE_BUDGET
        if proof.rule == "refl":
            assert proof.left is proof.right and not proof.support
        elif proof.rule == "sym":
            assert proof.left is proof.children[0].right
        elif proof.rule == "trans":
            assert same(proof.children[0].right, proof.children[1].left)
        elif proof.rule == "prod":
            left, right = proof.children
            assert shallow(proof.left) == shallow(prod(left.left, right.left))
            assert shallow(proof.right) == shallow(prod(left.right, right.right))
        elif proof.rule == "inv":
            child = proof.children[0]
            assert shallow(proof.left) == shallow(inverse(child.left))
            assert shallow(proof.right) == shallow(inverse(child.right))
        elif proof.rule == "conj":
            child = proof.children[0]
            assert proof.left.kind == "conj" and shallow(proof.right) == shallow(conj(proof.left.args[0], child.right))
        elif proof.rule == "drop":
            assert proof.left.kind == "leaf" and is_empty(proof.right)
        elif proof.rule == "free":
            assert is_empty(proof.evidence) and same(proof.left, proof.right)
        elif proof.rule == "checked":
            assert proof.left.value is not None and proof.right.value is not None
        elif proof.rule == "subst":
            child = proof.children[0]
            assert proof.left.kind == "subst" and proof.right is proof.left.args[0]
            assert proof.left.args[1] == child.right.args[0]
            assert proof.left.args[2] is child.left and proof.evidence.kind == "subst-evidence"
            assert proof.support == child.support
        else:
            raise AssertionError(proof.rule)
        assert proof.evidence.support <= proof.support
        if proof.evidence.value is not None and proof.left.value is not None and proof.right.value is not None:
            assert proof.evidence.value == red(proof.left.value + inv(proof.right.value))
        stack.extend(proof.children)


def project(item, keep):
    memo = {}
    def visit(node):
        key = id(node)
        if key in memo:
            return memo[key]
        assert len(memo) < NODE_BUDGET
        if node.kind == "leaf": result = node if node.args[0] in keep else lit("")
        elif node.kind == "lit": result = node
        elif node.kind == "prod": result = prod(*(visit(arg) for arg in node.args))
        elif node.kind == "inv": result = inverse(visit(node.args[0]))
        elif node.kind == "subst": result = subst(visit(node.args[0]), node.args[1], node.args[2])
        else: result = conj(node.args[0], visit(node.args[1]))
        memo[key] = result
        return result
    return visit(item)


def project_proof(item, keep):
    memo = {}
    def visit(node):
        key = id(node)
        if key in memo: return memo[key]
        assert len(memo) < NODE_BUDGET
        if node.kind == "leaf": result = refl(node) if node.args[0] in keep else Proof(node, lit(""), node, frozenset((node.args[0],)), "drop")
        elif node.kind == "lit": result = refl(node)
        elif node.kind == "prod":
            result = refl(lit(""))
            for arg in node.args: result = pprod(result, visit(arg))
        elif node.kind == "inv": result = pinv(visit(node.args[0]))
        elif node.kind == "subst": result = psubst(node.args[0], node.args[1], node.args[2])
        else: result = pconj(node.args[0], visit(node.args[1]))
        memo[key] = result
        return result
    return visit(item)


def replace(item, source, image):
    memo = {}
    def visit(node):
        key = id(node)
        if key in memo: return memo[key]
        assert len(memo) < NODE_BUDGET
        if node.kind == "leaf": result = image if node.args[0] == source else node
        elif node.kind == "lit": result = node
        elif node.kind == "prod": result = prod(*(visit(arg) for arg in node.args))
        elif node.kind == "inv": result = inverse(visit(node.args[0]))
        elif node.kind == "subst": result = subst(visit(node.args[0]), node.args[1], node.args[2])
        else: result = conj(node.args[0], visit(node.args[1]))
        memo[key] = result
        return result
    return visit(item)


def replace_proof(item, source, equality):
    memo = {}
    def visit(node):
        key = id(node)
        if key in memo: return memo[key]
        assert len(memo) < NODE_BUDGET
        if node.kind == "leaf": result = equality if node.args[0] == source else refl(node)
        elif node.kind == "lit": result = refl(node)
        elif node.kind == "prod":
            result = refl(lit(""))
            for arg in node.args: result = pprod(result, visit(arg))
        elif node.kind == "inv": result = pinv(visit(node.args[0]))
        elif node.kind == "subst": result = psubst(node.args[0], node.args[1], node.args[2])
        else: result = pconj(node.args[0], visit(node.args[1]))
        memo[key] = result
        return result
    return visit(item)


def rank_three_rows():
    code = run_path(".scratch/mms02_u_xy_bridge_checker.py")
    states, steps = code["expand_path"](code["MISPRINTED_RANK_THREE"], code["RANK_THREE_MOVES"])
    assert len(code["RANK_THREE_MOVES"]) == 11 and len(steps) == 134
    rows = [leaf("A"), leaf("B"), leaf("u")]
    for step in steps:
        if step.kind == "AC1":
            rows[step.target] = prod(rows[step.target], rows[step.operand])
        elif step.kind == "AC2":
            rows[step.target] = inverse(rows[step.target])
        else:
            rows[step.target] = conj(step.operand, rows[step.target])
        assert rows[step.target].value == step.after[step.target]
    assert tuple(row.value for row in rows) == states[-1] == ("Z", "Y", "X")
    return tuple(rows)


def replay_rank_three_words(kill_word):
    code = run_path(".scratch/mms02_u_xy_bridge_checker.py")
    _, steps = code["expand_path"](
        code["MISPRINTED_RANK_THREE"], code["RANK_THREE_MOVES"]
    )
    rows = [A, B, kill_word]
    for step in steps:
        if step.kind == "AC1":
            rows[step.target] = red(rows[step.target] + rows[step.operand])
        elif step.kind == "AC2":
            rows[step.target] = inv(rows[step.target])
        else:
            rows[step.target] = red(
                step.operand + rows[step.target] + inv(step.operand)
            )
    return tuple(rows)


def test_signed_involution_common_kill_target() -> None:
    code = run_path(".scratch/mms02_u_xy_bridge_checker.py")
    _, steps = code["expand_path"](
        code["MISPRINTED_RANK_THREE"], code["RANK_THREE_MOVES"]
    )
    assert tuple(signed_involution(word) for word in (A, B, U, V)) == (
        "ZXyzYZxzyZYx",
        "zYZxzyzYZXzyZY",
        V,
        U,
    )
    assert all(
        signed_involution(signed_involution(word)) == word
        for word in (A, B, U, V)
    )

    current = tuple(signed_involution(word) for word in code["MISPRINTED_RANK_THREE"])
    for step in steps:
        rows = list(current)
        if step.kind == "AC1":
            rows[step.target] = red(rows[step.target] + rows[step.operand])
        elif step.kind == "AC2":
            rows[step.target] = inv(rows[step.target])
        else:
            conjugator = signed_involution(step.operand)
            rows[step.target] = red(conjugator + rows[step.target] + inv(conjugator))
        current = tuple(rows)
        assert current == tuple(signed_involution(word) for word in step.after)
    assert current == ("x", "y", "z")


def test_common_kill_projected_pairs_have_distinct_whitehead_floors() -> None:
    quotient = {"x": "x", "y": "y", "z": "Yx"}
    source = tuple(apply_images(word, quotient) for word in (A, B))
    target = tuple(
        apply_images(signed_involution(word), quotient) for word in (A, B)
    )
    assert source == (M0, M1)
    assert target == ("XXyxYxy", "YxYXyxYxxYXyXYxyX")

    automorphisms = rank_two_whitehead_automorphisms()
    assert len(automorphisms) == 12
    source_minimum, source_path = whitehead_minimum(source, automorphisms)
    target_minimum, target_path = whitehead_minimum(target, automorphisms)
    assert source_minimum == ("XXYYXyxYxy", "XYXYXyxYxyy")
    assert target_minimum == ("XXYxY", "XXYxyXYYYXyxxY")
    assert source_path == (("xy", "y"), ("x", "xy"))
    assert target_path == (("x", "xy"), ("xy", "y"))
    assert sum(map(len, source_minimum)) == 21
    assert sum(map(len, target_minimum)) == 19
    for minimum in (source_minimum, target_minimum):
        assert all(
            sum(
                map(
                    len,
                    canonical_cyclic_pair(
                        tuple(apply_images(word, images) for word in minimum)
                    ),
                )
            )
            >= sum(map(len, minimum))
            for images in automorphisms
        )


def test_one_projected_base_multiplication_cannot_reach_common_kill_target() -> None:
    quotient = {"x": "x", "y": "y", "z": "Yx"}
    source = tuple(apply_images(word, quotient) for word in (A, B))
    target = tuple(
        apply_images(signed_involution(word), quotient) for word in (A, B)
    )
    source_matrix = tuple(exponent_vector(word) for word in source)
    target_matrix = tuple(exponent_vector(word) for word in target)
    assert source_matrix == ((0, 1), (-1, 1))
    assert target_matrix == ((0, 1), (1, -2))

    cases = []
    required_matrices = set()
    for changed in (0, 1):
        unchanged = 1 - changed
        for old_sign, donor_sign in product((1, -1), repeat=2):
            changed_matrix = list(source_matrix)
            changed_matrix[changed] = tuple(
                old_sign * source_matrix[changed][coordinate]
                + donor_sign * source_matrix[unchanged][coordinate]
                for coordinate in range(2)
            )
            changed_matrix = tuple(changed_matrix)
            for assignment in permutations((0, 1)):
                for target_signs in product((1, -1), repeat=2):
                    oriented_target = tuple(
                        tuple(
                            target_signs[row]
                            * target_matrix[assignment[row]][coordinate]
                            for coordinate in range(2)
                        )
                        for row in range(2)
                    )
                    ambient_matrix = matrix_multiply(
                        matrix_inverse(changed_matrix), oriented_target
                    )
                    required_matrices.add(ambient_matrix)
                    cases.append(
                        (
                            changed,
                            unchanged,
                            assignment,
                            ambient_matrix,
                        )
                    )

    assert len(cases) == 64
    assert len(required_matrices) == 32
    representatives = ambient_automorphism_representatives(required_matrices)
    length_table = defaultdict(set)
    for changed, unchanged, assignment, ambient_matrix in cases:
        images = representatives[ambient_matrix]
        assert tuple(exponent_vector(images[letter]) for letter in ("x", "y")) == ambient_matrix
        unchanged_image = canonical_cyclic_word(apply_images(source[unchanged], images))
        target_word = canonical_cyclic_word(target[assignment[unchanged]])
        assert unchanged_image != target_word
        length_table[(changed, assignment[unchanged])].add(len(unchanged_image))

    assert dict(length_table) == {
        (0, 0): {11, 13, 15, 17},
        (0, 1): {13, 15, 19},
        (1, 0): {11, 13, 15, 17},
        (1, 1): {11, 15, 19},
    }
    assert tuple(len(canonical_cyclic_word(word)) for word in target) == (7, 17)


def h_step(words, rows, move):
    first, second = words
    left, right = rows
    if move == 1:
        return (first, red(second + first)), (left, prod(right, left))
    if move == 2:
        return (red(first + inv(second)), second), (prod(left, inverse(right)), right)
    if move == 3:
        return (first, red(second + inv(first))), (left, prod(right, inverse(left)))
    if move == 4:
        return (red(first + second), second), (prod(left, right), right)
    table = {5: (1, "X"), 6: (0, "Y"), 7: (1, "Y"), 8: (0, "x"), 9: (1, "x"), 10: (0, "y"), 11: (1, "y"), 12: (0, "X")}
    target, word = table[move]
    new_words, new_rows = [first, second], [left, right]
    new_words[target] = red(word + new_words[target] + inv(word))
    new_rows[target] = conj(word, new_rows[target])
    return tuple(new_words), tuple(new_rows)


def two_row_rows():
    code = run_path(".scratch/mms02_wirtinger_repair_attack_checker.py")
    words, rows = (M0, M1), (leaf("M0"), leaf("M1"))
    words, rows = (inv(words[0]), words[1]), (inverse(rows[0]), rows[1])
    word = words[0][-1]
    words, rows = (red(word + words[0] + inv(word)), words[1]), (conj(word, rows[0]), rows[1])
    words, rows = (words[0], inv(words[1])), (rows[0], inverse(rows[1]))
    assert words == code["PUBLISHED_P"] and tuple(row.value for row in rows) == words
    assert len(code["MISPRINTED_TO_AK3"]) == 53
    for move in code["MISPRINTED_TO_AK3"]:
        words, rows = h_step(words, rows, move)
        assert tuple(row.value for row in rows) == words
    assert words == (R, S)
    return rows


def ak3_expr(cert, row_r, row_s):
    rows = {"R": row_r, "S": row_s}
    terms = []
    for factor in cert.factors:
        row = rows[factor.relator]
        terms.append(conj(factor.conjugator, row if factor.sign == 1 else inverse(row)))
    return prod(*terms)


def z_sub(source, target):
    result = refl(lit(""))
    for letter in source:
        if letter == "z":
            step = Proof(lit("z"), lit("Yx"), conj("z", leaf("v")), frozenset(("v",)), "checked")
        elif letter == "Z":
            step = Proof(lit("Z"), lit("Xy"), inverse(leaf("v")), frozenset(("v",)), "checked")
        else:
            step = refl(lit(letter))
        result = pprod(result, step)
    assert result.left.value == source and result.right.value == target
    return result


def free_proof(left, right):
    assert same(left, right)
    return Proof(left, right, lit(""), frozenset(), "free")


def relation_lift_data():
    rows = rank_three_rows()
    assert tuple(map(leaf_coefficients, rows)) == (
        (2, 1, 1),
        (1, 0, 1),
        (1, 1, 1),
    )
    v_expr = prod(rows[2], inverse(rows[1]), inverse(rows[0]))
    assert v_expr.value == V
    h = project(v_expr, {"u"})
    h_eq_v = sym(project_proof(v_expr, {"u"}))
    verify(h_eq_v)
    assert same(h_eq_v.left, h) and h_eq_v.support <= {"A", "B"}

    row_r, row_s = two_row_rows()
    ak3 = run_path("tests/stable_ac/test_ak3_normal_closure_certificate.py")["certificate"]()
    x_m, y_m = ak3_expr(ak3["x_one"], row_r, row_s), ak3_expr(ak3["y_one"], row_r, row_s)
    assert x_m.value == "x" and y_m.value == "y"

    a_m0, b_m1 = z_sub(A, M0), z_sub(B, M1)
    verify(a_m0)
    verify(b_m1)
    m0_a, m1_b = sym(a_m0), sym(b_m1)
    m0_abv = prod(m0_a.evidence, leaf("A"))
    m1_abv = prod(m1_b.evidence, leaf("B"))
    assert m0_abv.value == M0 and m1_abv.value == M1
    x_abv = replace(replace(x_m, "M0", m0_abv), "M1", m1_abv)
    y_abv = replace(replace(y_m, "M0", m0_abv), "M1", m1_abv)
    assert x_abv.value == "x" and y_abv.value == "y"

    u_inverse = lit("xyZ")
    u_to_xyxy = z_sub("xyZ", "xyXy")
    x_one = Proof(lit("x"), lit(""), x_abv, x_abv.support, "checked")
    y_one = Proof(lit("y"), lit(""), y_abv, y_abv.support, "checked")
    xyxy_one = pprod(pprod(pprod(x_one, y_one), pinv(x_one)), y_one)
    u_inverse_one = trans(u_to_xyxy, xyxy_one)
    verify(u_inverse_one)
    evidence_projection = project_proof(u_inverse_one.evidence, {"v"})
    k = evidence_projection.right
    k_eq_u_inverse = sym(trans(free_proof(u_inverse, u_inverse_one.evidence), evidence_projection))
    verify(k_eq_u_inverse)

    h_a, h_b = prod(leaf("A"), h), prod(leaf("B"), h)
    h_a_eq_v = trans(pprod(Proof(leaf("A"), lit(""), leaf("A"), frozenset(("A",)), "drop"), h_eq_v), free_proof(h_eq_v.right, leaf("v")))
    h_b_eq_v = trans(pprod(Proof(leaf("B"), lit(""), leaf("B"), frozenset(("B",)), "drop"), h_eq_v), free_proof(h_eq_v.right, leaf("v")))
    verify(h_a_eq_v)
    verify(h_b_eq_v)

    k_a, k_b = subst(k, "v", h_a), subst(k, "v", h_b)
    k_eq_k_a = sym(psubst(k, "v", h_a_eq_v))
    k_eq_k_b = sym(psubst(k, "v", h_b_eq_v))
    k_a_eq_u_inverse = trans(sym(k_eq_k_a), k_eq_u_inverse)
    k_b_eq_u_inverse = trans(sym(k_eq_k_b), k_eq_u_inverse)
    e_a, e_b = prod(leaf("u"), k_a), prod(leaf("u"), k_b)
    e_a_eq_one = trans(pprod(refl(leaf("u")), k_a_eq_u_inverse), free_proof(prod(leaf("u"), u_inverse), lit("")))
    e_b_eq_one = trans(pprod(refl(leaf("u")), k_b_eq_u_inverse), free_proof(prod(leaf("u"), u_inverse), lit("")))
    verify(e_a_eq_one)
    verify(e_b_eq_one)
    assert (e_a, leaf("B"), h_a)[1].value == B
    assert (leaf("A"), e_b, h_b)[0].value == A
    return {
        "h": h,
        "k": k,
        "k_eq_u_inverse": k_eq_u_inverse,
        "h_a": h_a,
        "h_b": h_b,
        "e_a": e_a,
        "e_b": e_b,
        "h_a_eq_v": h_a_eq_v,
        "h_b_eq_v": h_b_eq_v,
        "e_a_eq_one": e_a_eq_one,
        "e_b_eq_one": e_b_eq_one,
    }


def test_mms02_relation_lift_certificate_dag():
    data = relation_lift_data()
    assert data["e_a_eq_one"].support <= {"A", "B"}
    assert data["h_a_eq_v"].support <= {"A", "B"}
    assert data["e_b_eq_one"].support <= {"A", "B"}
    assert data["h_b_eq_v"].support <= {"A", "B"}
    assert nodes(data["e_a"]) < 25_000 and nodes(data["e_b"]) < 25_000

    branch_a = (B, data["h_a"].value)
    branch_b = (A, data["h_b"].value)
    assert tuple(map(rank_three_exponent_vector, branch_a)) == (
        (-1, 1, 0),
        (2, 1, -2),
    )
    assert tuple(map(rank_three_exponent_vector, branch_b)) == (
        (1, 0, -1),
        (0, 2, -1),
    )
    assert rank_three_pair_minors(branch_a) == (-3, 2, -2)
    assert rank_three_pair_minors(branch_b) == (2, -1, 2)
    assert gcd(*rank_three_pair_minors(branch_a)) == 1
    assert gcd(*rank_three_pair_minors(branch_b)) == 1

    first = {"x": "x", "y": "xyX", "z": "zX"}
    second = {"x": "x", "y": "y", "z": "zy"}
    certificates = (
        (
            branch_a,
            (first, second),
            (363, 357, 351),
            (337, 14),
            "15e51dc47cabaadf7a02082959e9d6068648ee6db91dc1133b15632845c2db36",
        ),
        (
            branch_b,
            (second, first),
            (363, 355, 349),
            (339, 10),
            "4284e78d86ce52707c695c1e2c69c1eb4be1b2f1421fd55b74a49acaadf05842",
        ),
    )
    automorphisms = rank_three_whitehead_automorphisms()
    assert len(automorphisms) == 90
    for pair, steps, expected_totals, expected_lengths, expected_hash in certificates:
        minimum, totals = replay_whitehead_pair_floor(pair, steps)
        assert totals == expected_totals
        assert tuple(map(len, minimum)) == expected_lengths
        assert sha256("|".join(minimum).encode()).hexdigest() == expected_hash
        endpoint_total = sum(map(len, minimum))
        neighbor_totals = tuple(
            sum(
                map(
                    len,
                    canonical_cyclic_pair(
                        tuple(apply_images(word, images) for word in minimum)
                    ),
                )
            )
            for images in automorphisms
        )
        assert min(neighbor_totals) == endpoint_total
        assert neighbor_totals.count(endpoint_total) == 8
        assert sum(total > endpoint_total for total in neighbor_totals) == 82


def test_mms02_actual_base_is_a_torsion_free_one_relator_group():
    forward = {
        "x": "zXyZ",
        "y": "y",
        "z": "zYxZYzYzYxZyzXyZ",
    }
    backward = {
        "x": B,
        "y": "y",
        "z": "yxzXYxy",
    }
    for generator in "xyz":
        assert apply_images(apply_images(generator, forward), backward) == generator
        assert apply_images(apply_images(generator, backward), forward) == generator

    assert apply_images(B, forward) == "x"
    transformed_a = apply_images(A, forward)
    assert transformed_a == "YzYzYxZyzXyZXyZyzYxZYzXyZyZyzXyZ"
    one_relator = apply_images(
        transformed_a,
        {"x": "", "y": "y", "z": "z"},
    )
    cyclic_relator = canonical_cyclic_word(one_relator)
    assert cyclic_relator == "YZYzYzYZyzyZYzYzYZYzyZyZyz"
    assert len(cyclic_relator) == 26
    assert red(cyclic_relator) == cyclic_relator
    assert cyclic_relator[0] != cyclic_relator[-1].swapcase()
    for root_length in (1, 2, 13):
        assert any(
            cyclic_relator[index] != cyclic_relator[index % root_length]
            for index in range(root_length, len(cyclic_relator))
        )


def test_mms02_actual_base_relator_is_not_primitive():
    renamed_relator = canonical_cyclic_word(
        "YZYzYzYZyzyZYzYzYZYzyZyZyz".translate(
            str.maketrans({"y": "x", "Y": "X", "z": "y", "Z": "Y"})
        )
    )
    reducing_automorphism = {"x": "xy", "y": "y"}
    minimum = canonical_cyclic_word(
        apply_images(renamed_relator, reducing_automorphism)
    )

    assert len(renamed_relator) == 26
    assert minimum == "XXXYYXyxxxyXYYXXXYxyyxY"
    assert len(minimum) == 23
    assert min(
        len(canonical_cyclic_word(apply_images(minimum, images)))
        for images in rank_two_whitehead_automorphisms()
    ) == len(minimum)


def test_mms02_fixed_pair_base_relator_is_not_primitive():
    steps = (
        {"x": "x", "y": "y", "z": "zy"},
        {"x": "x", "y": "xyX", "z": "z"},
        {"x": "x", "y": "Zy", "z": "z"},
    )
    minimum, totals = replay_whitehead_pair_floor((A, A), steps)

    assert totals == (24, 22, 18, 16)
    assert minimum == ("XYXyzxZy", "XYXyzxZy")
    assert min(
        sum(
            map(
                len,
                canonical_cyclic_pair(
                    tuple(apply_images(word, images) for word in minimum)
                ),
            )
        )
        for images in rank_three_whitehead_automorphisms()
    ) == 16


def test_mms02_canonical_lift_base_pairs_fail_the_cyclic_module_unit_test():
    data = relation_lift_data()
    branch_a_diagonal_coefficients = (
        4,
        8,
        -30,
        -8,
        100,
        -96,
        -70,
        176,
        -54,
        -212,
        198,
        100,
        -370,
        212,
        186,
        -404,
        146,
        300,
        -460,
        118,
        277,
        -241,
        23,
        109,
        -87,
        16,
        48,
        56,
        -62,
        -48,
        168,
        -108,
        -92,
        184,
        -4,
        -134,
        22,
        98,
        -68,
        -8,
        20,
        0,
        -6,
        -12,
        6,
        4,
        -4,
    )
    branch_b_diagonal_coefficients = (
        2,
        0,
        -12,
        4,
        10,
        -30,
        2,
        22,
        -30,
        -24,
        38,
        -26,
        -48,
        56,
        -22,
        -48,
        60,
        -2,
        -58,
        58,
        -3,
        -6,
        26,
        6,
        2,
        10,
        12,
        20,
        -14,
        14,
        22,
        -30,
        4,
        18,
        -8,
        -16,
        4,
        2,
        -12,
        4,
        -6,
        4,
        -4,
    )

    def coefficient_dict(first_degree, coefficients):
        return {
            degree: coefficient
            for degree, coefficient in zip(
                range(first_degree, first_degree + len(coefficients)),
                coefficients,
                strict=True,
            )
            if coefficient
        }

    def coordinate_digest(coordinate):
        payload = ";".join(
            f"{degree}:{coordinate[degree]}" for degree in sorted(coordinate)
        )
        return sha256(payload.encode()).hexdigest()

    base_coordinates = cyclic_evidence_coordinates(
        data["k_eq_u_inverse"].evidence
    )

    def endpoint_coordinates(branch):
        substitution_difference = cyclic_evidence_coordinates(
            data[f"h_{branch}_eq_v"].evidence
        )
        substitution_coordinates = cyclic_substitution_coordinates(
            data["k"],
            "v",
            substitution_difference,
        )
        return _coordinate_shift(
            _coordinate_add(substitution_coordinates, base_coordinates),
            1,
        )

    branch_a = endpoint_coordinates("a")
    branch_b = endpoint_coordinates("b")
    branch_a_diagonal = coefficient_dict(-21, branch_a_diagonal_coefficients)
    branch_b_diagonal = coefficient_dict(-19, branch_b_diagonal_coefficients)
    assert branch_a[0] == branch_a_diagonal
    assert branch_b[1] == branch_b_diagonal
    assert coordinate_digest(branch_a[1]) == (
        "90f3651152ed8a50bd411ba39545d6dcbe55c7ffd0fbb3d9494a41a581ed03dc"
    )
    assert coordinate_digest(branch_b[0]) == (
        "ba63e496db45e8a993c1862597ed99e8b9769e8dd00081daa7cdf143f5ab30be"
    )
    assert tuple(sum(coordinate.values()) for coordinate in branch_a) == (1, 0)
    assert tuple(sum(coordinate.values()) for coordinate in branch_b) == (0, 1)
    assert (len(branch_a_diagonal), min(branch_a_diagonal), max(branch_a_diagonal)) == (
        46,
        -21,
        25,
    )
    assert (len(branch_b_diagonal), min(branch_b_diagonal), max(branch_b_diagonal)) == (
        42,
        -19,
        23,
    )


def test_mms02_tag_residual_has_a_cyclic_unit_minor():
    data = relation_lift_data()
    tag_coordinates = cyclic_evidence_coordinates(
        data["h_b_eq_v"].evidence
    )

    assert tag_coordinates[1] == {1: 1}


def test_mms02_tag_coefficient_delta_is_nonmonomial_in_a5():
    assert evaluate_permutation_word(A) == A5_IDENTITY
    assert evaluate_permutation_word(B) == A5_IDENTITY

    generated = {A5_IDENTITY}
    frontier = [A5_IDENTITY]
    while frontier:
        current = frontier.pop()
        for generator in A5_IMAGES.values():
            image = compose_permutations(current, generator)
            if image not in generated:
                generated.add(image)
                frontier.append(image)
    assert len(generated) == 60
    assert all(
        sum(
            value[left] > value[right]
            for left in range(5)
            for right in range(left + 1, 5)
        )
        % 2
        == 0
        for value in generated
    )

    nested = finite_quotient_evidence_coordinates(
        conj("x", conj("y", leaf("B")))
    )[1]
    expected_nested_label = compose_permutations(
        invert_permutation(A5_IMAGES["y"]),
        invert_permutation(A5_IMAGES["x"]),
    )
    wrong_nested_label = compose_permutations(
        invert_permutation(A5_IMAGES["x"]),
        invert_permutation(A5_IMAGES["y"]),
    )
    assert expected_nested_label != wrong_nested_label
    assert nested == {expected_nested_label: 1}

    data = relation_lift_data()
    tag_coordinates = finite_quotient_evidence_coordinates(
        data["h_b_eq_v"].evidence
    )
    cyclic_coordinates = cyclic_evidence_coordinates(
        data["h_b_eq_v"].evidence
    )
    delta = tag_coordinates[1]
    payload = ";".join(
        f"{''.join(map(str, group_element))}:{delta[group_element]}"
        for group_element in sorted(delta)
    )

    assert tuple(sum(coordinate.values()) for coordinate in tag_coordinates) == tuple(
        sum(coordinate.values()) for coordinate in cyclic_coordinates
    ) == (2, 1)
    assert len(delta) == 7
    assert sum(abs(coefficient) for coefficient in delta.values()) == 7
    assert delta[A5_IDENTITY] == 1
    assert delta[(1, 3, 4, 2, 0)] == -1
    assert sha256(payload.encode()).hexdigest() == (
        "d02e2d270444a6943c1a3fb90232841b7baced497fd434bcea83c839cd904fc8"
    )


def test_published_kill_slp_replay_has_nonprimitive_canonical_pivot():
    rows = replay_rank_three_words(V)
    assert tuple(map(len, rows)) == (349, 251, 195)
    matrix = tuple(map(rank_three_exponent_vector, rows))
    assert matrix == (
        (0, 2, -1),
        (0, 1, 0),
        (-1, 2, 0),
    )
    determinant = (
        matrix[0][0]
        * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1]
        * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2]
        * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )
    assert determinant == -1

    pivot = (rows[1], rows[2])
    assert rank_three_pair_minors(pivot) == (1, 0, 0)
    maps = (
        {"x": "x", "y": "xy", "z": "z"},
        {"x": "x", "y": "y", "z": "zy"},
    )
    minimum, totals = replay_whitehead_pair_floor(pivot, maps)
    assert totals == (446, 419, 413)
    assert tuple(map(len, minimum)) == (232, 181)
    assert sha256("|".join(minimum).encode()).hexdigest() == (
        "ecd216a89a91ffc5b3a84720412bed41c82ae1cb03ae9895a3c8f932c5f02a50"
    )

    automorphisms = rank_three_whitehead_automorphisms()
    neighbor_totals = tuple(
        sum(
            map(
                len,
                canonical_cyclic_pair(
                    tuple(apply_images(word, images) for word in minimum)
                ),
            )
        )
        for images in automorphisms
    )
    assert min(neighbor_totals) == 413
    assert neighbor_totals.count(413) == 6
    assert sum(total > 413 for total in neighbor_totals) == 84

    difference_pivot = (red(rows[0] + inv(rows[2])), red(rows[1] + inv(rows[2])))
    assert tuple(map(len, difference_pivot)) == (154, 56)
    assert red(difference_pivot[0] + rows[2]) == rows[0]
    assert red(difference_pivot[1] + rows[2]) == rows[1]
    assert tuple(map(rank_three_exponent_vector, difference_pivot)) == (
        (1, 0, -1),
        (1, -1, 0),
    )
    assert rank_three_pair_minors(difference_pivot) == (-1, 1, -1)

    difference_minimum, difference_totals = replay_whitehead_pair_floor(
        difference_pivot, maps
    )
    assert difference_totals == (208, 197, 192)
    assert tuple(map(len, difference_minimum)) == (49, 143)
    assert sha256("|".join(difference_minimum).encode()).hexdigest() == (
        "eba9943c1feaf47894deacef4db33ee9e9ab773437e55f010461c3c67e8a2ba2"
    )

    difference_neighbor_totals = tuple(
        sum(
            map(
                len,
                canonical_cyclic_pair(
                    tuple(
                        apply_images(word, images) for word in difference_minimum
                    )
                ),
            )
        )
        for images in automorphisms
    )
    assert min(difference_neighbor_totals) == 192
    assert difference_neighbor_totals.count(192) == 6
    assert sum(total > 192 for total in difference_neighbor_totals) == 84


def test_published_kill_slp_replay_has_no_primitive_row():
    rows = replay_rank_three_words(V)
    maps = (
        {"x": "x", "y": "xy", "z": "z"},
        {"x": "x", "y": "y", "z": "zy"},
    )
    certificates = (
        (
            (349, 329, 328),
            "c84243962616f210689d10c4f1e0a965548c8b7d97ad1c189edab0147096eb60",
        ),
        (
            (251, 236, 232),
            "814aeb93cba36991a5d57544b855b1fd04bdc3d2c62f52f377852cbcbd3cde5d",
        ),
        (
            (195, 183, 181),
            "0ecb301a5ee0f61ac6d1a3a3c5a09b9db32b795774669e3d47f0daa513091e71",
        ),
    )
    automorphisms = rank_three_whitehead_automorphisms()
    for word, (expected_totals, expected_hash) in zip(rows, certificates):
        current = canonical_cyclic_word(word)
        totals = [len(current)]
        for images in maps:
            current = canonical_cyclic_word(apply_images(current, images))
            assert len(current) < totals[-1]
            totals.append(len(current))
        assert tuple(totals) == expected_totals
        assert sha256(current.encode()).hexdigest() == expected_hash
        neighbor_lengths = tuple(
            len(canonical_cyclic_word(apply_images(current, images)))
            for images in automorphisms
        )
        assert min(neighbor_lengths) == len(current)
        assert neighbor_lengths.count(len(current)) == 6
        assert sum(length > len(current) for length in neighbor_lengths) == 84
