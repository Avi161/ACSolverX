"""Exact crossed Fox--Magnus data for the period-two residual circuit."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from typing import Union

try:
    from experiments.stable_ac import depth4_period_two_cyclic_degree_two_obstruction_certificate as cyclic
    from experiments.stable_ac import depth4_period_two_degree_two_escape_certificate as escape
    from experiments.stable_ac import depth4_period_two_eight_direction_obstruction_certificate as eight
    from experiments.stable_ac import depth4_period_two_eleven_direction_obstruction_certificate as eleven
    from experiments.stable_ac import depth4_period_two_five_direction_obstruction_certificate as five
    from experiments.stable_ac import depth4_period_two_lift_certificate as lift
    from experiments.stable_ac import depth4_period_two_nine_direction_obstruction_certificate as nine
    from experiments.stable_ac import depth4_period_two_remote_syzygy_certificate as remote
    from experiments.stable_ac import depth4_period_two_seven_direction_obstruction_certificate as seven
    from experiments.stable_ac import depth4_period_two_six_direction_obstruction_certificate as six
    from experiments.stable_ac import depth4_period_two_source_flow_certificate as source
    from experiments.stable_ac import depth4_period_two_ten_direction_obstruction_certificate as ten
    from experiments.stable_ac import depth4_period_two_tree_flow_factorization_certificate as tree
except ModuleNotFoundError:
    import depth4_period_two_cyclic_degree_two_obstruction_certificate as cyclic
    import depth4_period_two_degree_two_escape_certificate as escape
    import depth4_period_two_eight_direction_obstruction_certificate as eight
    import depth4_period_two_eleven_direction_obstruction_certificate as eleven
    import depth4_period_two_five_direction_obstruction_certificate as five
    import depth4_period_two_lift_certificate as lift
    import depth4_period_two_nine_direction_obstruction_certificate as nine
    import depth4_period_two_remote_syzygy_certificate as remote
    import depth4_period_two_seven_direction_obstruction_certificate as seven
    import depth4_period_two_six_direction_obstruction_certificate as six
    import depth4_period_two_source_flow_certificate as source
    import depth4_period_two_ten_direction_obstruction_certificate as ten
    import depth4_period_two_tree_flow_factorization_certificate as tree


TensorKey = tuple[lift.Word, lift.Word]
Tensor = dict[TensorKey, int]
KernelWord = tuple[tuple[lift.Word, int], ...]
ModuleVariables = tuple[lift.ModuleVector, ...]
WedgeVector = dict[TensorKey, int]


@dataclass(frozen=True)
class Literal:
    word: lift.Word


@dataclass(frozen=True)
class Correction:
    slot: int


@dataclass(frozen=True)
class Product:
    factors: tuple[Node, ...]


@dataclass(frozen=True)
class Inverse:
    value: Node


@dataclass(frozen=True)
class Conjugation:
    payload: Node
    conjugator: Node


Node = Union[Literal, Correction, Product, Inverse, Conjugation]


@dataclass(frozen=True)
class _ExpandedLeaf:
    literal: lift.Word | None = None
    slot: int | None = None
    polarity: int = 1


@dataclass(frozen=True)
class Occurrence:
    slot: int
    polarity: int
    quotient_prefix: lift.Word


def _product(*factors: Node) -> Product:
    return Product(tuple(factors))


def _conjugate(payload: Node, conjugator: Node) -> Conjugation:
    return Conjugation(payload, conjugator)


def _residual_ast() -> Node:
    corrections = tuple(Correction(slot) for slot in range(5))
    conjugators = (
        _product(corrections[0], Literal(lift.H0)),
        _product(corrections[1], Literal(lift.H1)),
        _product(corrections[2], Literal(lift.H2)),
        _product(corrections[3], Literal(lift.H3)),
    )
    r = _product(
        Literal(lift.SOURCE_A),
        _conjugate(Inverse(Literal(lift.SOURCE_B)), conjugators[0]),
    )
    s = _product(
        Literal(lift.SOURCE_B),
        _conjugate(Inverse(r), conjugators[1]),
    )
    u = _product(r, _conjugate(Inverse(s), conjugators[2]))
    z = _product(Inverse(u), _conjugate(s, conjugators[3]))
    target = _conjugate(Literal(lift.TARGET), corrections[4])
    return _product(z, Inverse(target))


def _expand(node: Node, inverted: bool = False) -> tuple[_ExpandedLeaf, ...]:
    if isinstance(node, Literal):
        return (_ExpandedLeaf(literal=lift.inverse(node.word) if inverted else node.word),)
    if isinstance(node, Correction):
        return (_ExpandedLeaf(slot=node.slot, polarity=-1 if inverted else 1),)
    if isinstance(node, Product):
        factors = reversed(node.factors) if inverted else node.factors
        return tuple(
            leaf
            for factor in factors
            for leaf in _expand(factor, inverted)
        )
    if isinstance(node, Inverse):
        return _expand(node.value, not inverted)
    if isinstance(node, Conjugation):
        expanded = _product(node.conjugator, node.payload, Inverse(node.conjugator))
        return _expand(expanded, inverted)
    raise TypeError(f"unknown AST node {node!r}")


def _parse_quotient_word(value: str) -> lift.Word:
    alphabet = {"c": lift.C, "C": -lift.C, "t": lift.T, "T": -lift.T}
    return lift.quotient_reduce(tuple(alphabet[letter] for letter in value))


_PINNED_OCCURRENCES = (
    (2, 1, ""),
    (1, 1, "tc"),
    (0, 1, "tc"),
    (0, -1, "ctcTTTcttc"),
    (1, -1, "ctcTctt"),
    (2, -1, "ctcTcTctc"),
    (0, 1, "ctcTcTctc"),
    (0, -1, "ctcTTTTcttc"),
    (3, 1, "ctcTTctt"),
    (1, 1, "ctcTctc"),
    (0, 1, "ctcTctc"),
    (0, -1, "cTTcttc"),
    (1, -1, "tt"),
    (3, -1, "t"),
    (4, 1, "t"),
    (4, -1, ""),
)


def _ast_occurrences() -> tuple[Occurrence, ...]:
    prefix: lift.Word = ()
    occurrences = []
    for leaf in _expand(_residual_ast()):
        if leaf.literal is not None:
            prefix = lift.quotient_multiply(prefix, lift.quotient_reduce(leaf.literal))
            continue
        assert leaf.slot is not None
        occurrences.append(Occurrence(leaf.slot, leaf.polarity, prefix))
    assert prefix == ()
    return tuple(occurrences)


def residual_occurrences() -> tuple[Occurrence, ...]:
    pinned = tuple(
        Occurrence(slot, polarity, _parse_quotient_word(prefix))
        for slot, polarity, prefix in _PINNED_OCCURRENCES
    )
    ast_occurrences = _ast_occurrences()
    assert ast_occurrences == pinned
    return ast_occurrences


def occurrence_operator(slot: int) -> lift.GroupRing:
    assert 0 <= slot < 5
    return lift.group_ring(*(
        (occurrence.polarity, occurrence.quotient_prefix)
        for occurrence in residual_occurrences()
        if occurrence.slot == slot
    ))


def _clean_tensor(value: dict[TensorKey, int]) -> Tensor:
    return {key: coefficient for key, coefficient in value.items() if coefficient}


def _add_tensors(*values: Tensor) -> Tensor:
    result: dict[TensorKey, int] = defaultdict(int)
    for value in values:
        for key, coefficient in value.items():
            result[key] += coefficient
    return _clean_tensor(result)


def _scale_tensor(value: Tensor, coefficient: int) -> Tensor:
    return _clean_tensor({key: coefficient * entry for key, entry in value.items()})


def _outer(left: lift.ModuleVector, right: lift.ModuleVector) -> Tensor:
    return _clean_tensor({
        (left_vertex, right_vertex): left_coefficient * right_coefficient
        for left_vertex, left_coefficient in lift.add_vectors(left).items()
        for right_vertex, right_coefficient in lift.add_vectors(right).items()
    })


def gamma_positive(
    left: lift.ModuleVector,
    right: lift.ModuleVector,
) -> Tensor:
    canonical_left = lift.add_vectors(left)
    canonical_right = lift.add_vectors(right)
    vertices = sorted(
        set(canonical_left) | set(canonical_right),
        key=lambda word: (len(word), word),
    )
    result: dict[TensorKey, int] = defaultdict(int)
    for index, left_vertex in enumerate(vertices):
        result[left_vertex, left_vertex] += (
            canonical_left.get(left_vertex, 0) * canonical_right.get(left_vertex, 0)
        )
        for right_vertex in vertices[index + 1:]:
            result[left_vertex, right_vertex] += (
                canonical_left.get(left_vertex, 0) * canonical_right.get(right_vertex, 0)
                + canonical_right.get(left_vertex, 0) * canonical_left.get(right_vertex, 0)
            )
    return _clean_tensor(result)


def gamma_negative(
    left: lift.ModuleVector,
    right: lift.ModuleVector,
) -> Tensor:
    return _add_tensors(
        _scale_tensor(gamma_positive(left, right), -1),
        _outer(left, right),
        _outer(right, left),
    )


def raw_tensor_from_kernel_word(word: KernelWord) -> Tensor:
    linear: dict[lift.Word, int] = defaultdict(int)
    tensor: dict[TensorKey, int] = defaultdict(int)
    for raw_vertex, sign in word:
        assert sign in (-1, 1)
        module_vertex = lift.c_vertex(raw_vertex)
        for left_vertex, coefficient in tuple(linear.items()):
            tensor[left_vertex, module_vertex] += coefficient * sign
        if sign == -1:
            tensor[module_vertex, module_vertex] += 1
        linear[module_vertex] += sign
        if not linear[module_vertex]:
            del linear[module_vertex]
    return _clean_tensor(tensor)


def _action(prefix: lift.Word, value: lift.ModuleVector) -> lift.ModuleVector:
    result: dict[lift.Word, int] = defaultdict(int)
    for module_vertex, coefficient in lift.add_vectors(value).items():
        target = lift.c_vertex(lift.quotient_multiply(prefix, module_vertex))
        result[target] += coefficient
    return lift.add_vectors(result)


def _translate_tensor(prefix: lift.Word, value: Tensor) -> Tensor:
    result: dict[TensorKey, int] = defaultdict(int)
    for (left_vertex, right_vertex), coefficient in value.items():
        translated_left = lift.c_vertex(lift.quotient_multiply(prefix, left_vertex))
        translated_right = lift.c_vertex(lift.quotient_multiply(prefix, right_vertex))
        result[translated_left, translated_right] += coefficient
    return _clean_tensor(result)


def _operators() -> tuple[lift.GroupRing, ...]:
    _, _, _, _, operators = escape.recurrence_data()
    return operators


def _assert_direction(direction: ModuleVariables) -> None:
    assert len(direction) == 5
    assert not escape.correction_image(direction, _operators()), (
        "expected a homogeneous correction direction"
    )


@dataclass(frozen=True)
class MixedTensorSubtotals:
    positive_internal: Tensor
    negative_internal: Tensor
    external: Tensor
    propagated_diagonal: Tensor


def symbolic_mixed_subtotals(
    left: ModuleVariables,
    right: ModuleVariables,
) -> MixedTensorSubtotals:
    _assert_direction(left)
    _assert_direction(right)
    occurrences = residual_occurrences()
    positive_internal: list[Tensor] = []
    negative_internal: list[Tensor] = []
    propagated_diagonal: list[Tensor] = []
    for occurrence in occurrences:
        gamma = gamma_positive if occurrence.polarity == 1 else gamma_negative
        translated = _translate_tensor(
            occurrence.quotient_prefix,
            gamma(left[occurrence.slot], right[occurrence.slot]),
        )
        diagonal = {
            pair: coefficient
            for pair, coefficient in translated.items()
            if pair[0] == pair[1]
        }
        off_diagonal = {
            pair: coefficient
            for pair, coefficient in translated.items()
            if pair[0] != pair[1]
        }
        propagated_diagonal.append(diagonal)
        target = positive_internal if occurrence.polarity == 1 else negative_internal
        target.append(off_diagonal)
    external: list[Tensor] = []
    for left_index, left_occurrence in enumerate(occurrences):
        left_d = _action(left_occurrence.quotient_prefix, left[left_occurrence.slot])
        left_e = _action(left_occurrence.quotient_prefix, right[left_occurrence.slot])
        for right_occurrence in occurrences[left_index + 1:]:
            right_d = _action(right_occurrence.quotient_prefix, left[right_occurrence.slot])
            right_e = _action(right_occurrence.quotient_prefix, right[right_occurrence.slot])
            coefficient = left_occurrence.polarity * right_occurrence.polarity
            external.extend((
                _scale_tensor(_outer(left_d, right_e), coefficient),
                _scale_tensor(_outer(left_e, right_d), coefficient),
            ))
    return MixedTensorSubtotals(
        positive_internal=_add_tensors(*positive_internal),
        negative_internal=_add_tensors(*negative_internal),
        external=_add_tensors(*external),
        propagated_diagonal=_add_tensors(*propagated_diagonal),
    )


def symbolic_mixed_tensor(
    left: ModuleVariables,
    right: ModuleVariables,
) -> Tensor:
    subtotals = symbolic_mixed_subtotals(left, right)
    return _add_tensors(
        subtotals.positive_internal,
        subtotals.negative_internal,
        subtotals.external,
        subtotals.propagated_diagonal,
    )


def _mixed_tensor_to_wedge(value: Tensor) -> WedgeVector:
    assert all(left != right for left, right in value), "mixed tensor diagonal is nonzero"
    for (left, right), coefficient in value.items():
        assert value.get((right, left), 0) == -coefficient, (
            "mixed tensor is not opposite-orientation antisymmetric"
        )
    return {
        (left, right): coefficient
        for (left, right), coefficient in value.items()
        if (len(left), left) < (len(right), right)
    }


def symbolic_mixed_wedge(
    left: ModuleVariables,
    right: ModuleVariables,
) -> WedgeVector:
    return _mixed_tensor_to_wedge(symbolic_mixed_tensor(left, right))


class _KernelStream:
    def __init__(self) -> None:
        self.quotient_prefix: lift.Word = ()
        self.linear: dict[lift.Word, int] = defaultdict(int)
        self.tensor: dict[TensorKey, int] = defaultdict(int)

    def _append_kernel_letter(self, module_vertex: lift.Word, sign: int) -> None:
        canonical_vertex = lift.c_vertex(module_vertex)
        for left_vertex, coefficient in tuple(self.linear.items()):
            self.tensor[left_vertex, canonical_vertex] += coefficient * sign
        if sign == -1:
            self.tensor[canonical_vertex, canonical_vertex] += 1
        self.linear[canonical_vertex] += sign
        if not self.linear[canonical_vertex]:
            del self.linear[canonical_vertex]

    def append_literal(self, word: lift.Word) -> None:
        for letter in word:
            if letter == lift.C and self.quotient_prefix and abs(self.quotient_prefix[-1]) == lift.C:
                self._append_kernel_letter(self.quotient_prefix[:-1], 1)
            elif letter == -lift.C and not (
                self.quotient_prefix and abs(self.quotient_prefix[-1]) == lift.C
            ):
                self._append_kernel_letter(self.quotient_prefix, -1)
            self.quotient_prefix = lift.quotient_append(self.quotient_prefix, letter)

    def result(self) -> tuple[lift.Word, lift.ModuleVector, Tensor]:
        return (
            self.quotient_prefix,
            lift.add_vectors(self.linear),
            _clean_tensor(self.tensor),
        )


def _base_variables() -> ModuleVariables:
    return escape.variables_from_entries(lift.CORRECTION)


def _add_variables(*values: ModuleVariables) -> ModuleVariables:
    return tuple(
        lift.add_vectors(*(value[slot] for value in values))
        for slot in range(5)
    )


@dataclass(frozen=True)
class _CrossedCoordinate:
    quotient: lift.Word
    linear: lift.ModuleVector
    tensor: Tensor


def _kernel_product(
    *coordinates: tuple[lift.ModuleVector, Tensor],
) -> tuple[lift.ModuleVector, Tensor]:
    linear: lift.ModuleVector = {}
    tensor: Tensor = {}
    for right_linear, right_tensor in coordinates:
        tensor = _add_tensors(tensor, right_tensor, _outer(linear, right_linear))
        linear = lift.add_vectors(linear, right_linear)
    return linear, tensor


def _kernel_inverse(
    linear: lift.ModuleVector,
    tensor: Tensor,
) -> tuple[lift.ModuleVector, Tensor]:
    return (
        lift.scale_vector(linear, -1),
        _add_tensors(_scale_tensor(tensor, -1), _outer(linear, linear)),
    )


@lru_cache(maxsize=None)
def _literal_coordinate(word: lift.Word) -> _CrossedCoordinate:
    stream = _KernelStream()
    stream.append_literal(word)
    quotient, linear, tensor = stream.result()
    return _CrossedCoordinate(quotient, linear, tensor)


def _canonical_section_coordinate(value: lift.ModuleVector) -> _CrossedCoordinate:
    canonical = lift.add_vectors(value)
    vertices = sorted(canonical, key=lambda word: (len(word), word))
    tensor: dict[TensorKey, int] = defaultdict(int)
    for index, left_vertex in enumerate(vertices):
        coefficient = canonical[left_vertex]
        tensor[left_vertex, left_vertex] += coefficient * (coefficient - 1) // 2
        for right_vertex in vertices[index + 1:]:
            tensor[left_vertex, right_vertex] += coefficient * canonical[right_vertex]
    return _CrossedCoordinate((), canonical, _clean_tensor(tensor))


@lru_cache(maxsize=None)
def _transported_generator_coordinate(
    quotient: lift.Word,
    module_vertex: lift.Word,
) -> _CrossedCoordinate:
    word = lift.multiply(
        quotient,
        lift.relation_generator(module_vertex),
        lift.inverse(quotient),
    )
    coordinate = _literal_coordinate(word)
    assert coordinate.quotient == ()
    expected = _action(quotient, {module_vertex: 1})
    assert coordinate.linear == expected
    return coordinate


def _transport_kernel(
    quotient: lift.Word,
    linear: lift.ModuleVector,
    tensor: Tensor,
) -> tuple[lift.ModuleVector, Tensor]:
    transported_linear = _action(quotient, linear)
    transported_tensor = _translate_tensor(quotient, tensor)
    one_vertex_terms = tuple(
        _scale_tensor(
            _transported_generator_coordinate(quotient, module_vertex).tensor,
            coefficient,
        )
        for module_vertex, coefficient in lift.add_vectors(linear).items()
    )
    return transported_linear, _add_tensors(transported_tensor, *one_vertex_terms)


@lru_cache(maxsize=None)
def _omega_coordinate(left: lift.Word, right: lift.Word) -> _CrossedCoordinate:
    product = lift.quotient_multiply(left, right)
    word = lift.multiply(left, right, lift.inverse(product))
    coordinate = _literal_coordinate(word)
    assert coordinate.quotient == ()
    return coordinate


def _coordinate_product(
    left: _CrossedCoordinate,
    right: _CrossedCoordinate,
) -> _CrossedCoordinate:
    transported = _transport_kernel(left.quotient, right.linear, right.tensor)
    omega = _omega_coordinate(left.quotient, right.quotient)
    linear, tensor = _kernel_product(
        (left.linear, left.tensor),
        transported,
        (omega.linear, omega.tensor),
    )
    return _CrossedCoordinate(
        lift.quotient_multiply(left.quotient, right.quotient),
        linear,
        tensor,
    )


def _coordinate_inverse(value: _CrossedCoordinate) -> _CrossedCoordinate:
    section_inverse = _literal_coordinate(lift.inverse(value.quotient))
    inverse_linear, inverse_tensor = _kernel_inverse(value.linear, value.tensor)
    kernel_inverse = _CrossedCoordinate((), inverse_linear, inverse_tensor)
    return _coordinate_product(section_inverse, kernel_inverse)


def _evaluate_ast_coordinate(
    node: Node,
    variables: ModuleVariables,
) -> _CrossedCoordinate:
    if isinstance(node, Literal):
        return _literal_coordinate(node.word)
    if isinstance(node, Correction):
        return _canonical_section_coordinate(variables[node.slot])
    if isinstance(node, Product):
        result = _CrossedCoordinate((), {}, {})
        for factor in node.factors:
            result = _coordinate_product(result, _evaluate_ast_coordinate(factor, variables))
        return result
    if isinstance(node, Inverse):
        return _coordinate_inverse(_evaluate_ast_coordinate(node.value, variables))
    if isinstance(node, Conjugation):
        conjugator = _evaluate_ast_coordinate(node.conjugator, variables)
        payload = _evaluate_ast_coordinate(node.payload, variables)
        return _coordinate_product(
            _coordinate_product(conjugator, payload),
            _coordinate_inverse(conjugator),
        )
    raise TypeError(f"unknown AST node {node!r}")


def _symbolic_residual_coordinate(
    direction: ModuleVariables,
) -> tuple[lift.ModuleVector, Tensor]:
    assert len(direction) == 5
    variables = _add_variables(_base_variables(), direction)
    coordinate = _evaluate_ast_coordinate(_residual_ast(), variables)
    assert coordinate.quotient == ()
    return coordinate.linear, coordinate.tensor


def symbolic_residual_tensor(direction: ModuleVariables) -> Tensor:
    return _symbolic_residual_coordinate(direction)[1]


def symbolic_unary_tensor(direction: ModuleVariables) -> Tensor:
    return _add_tensors(
        symbolic_residual_tensor(direction),
        _scale_tensor(symbolic_residual_tensor(({}, {}, {}, {}, {})), -1),
    )


def _residual_tensor_to_wedge(linear: lift.ModuleVector, tensor: Tensor) -> WedgeVector:
    assert not linear, "residual has nonzero linear coordinate"
    assert all(left != right for left, right in tensor), "residual tensor diagonal is nonzero"
    for (left, right), coefficient in tensor.items():
        assert tensor.get((right, left), 0) == -coefficient, (
            "residual tensor is not opposite-orientation antisymmetric"
        )
    return {
        (left, right): coefficient
        for (left, right), coefficient in tensor.items()
        if (len(left), left) < (len(right), right)
    }


_REMOTE_FOUR_POINT_ACTION = ((0, 1, 3, 2), (1, 2, 0, 3))


def _paired_action_bits(
    vector: tuple[int, ...],
    covectors: tuple[tuple[int, ...], ...],
) -> tuple[int, ...]:
    return tuple(
        sum(coefficient * coordinate for coefficient, coordinate in zip(covector, vector)) % 2
        for covector in covectors
    )


def _direct_fourteen_bits(value: WedgeVector) -> tuple[int, ...]:
    def projected(action: tuple[tuple[int, ...], tuple[int, ...]]) -> tuple[int, ...]:
        return remote.finite_wedge_vector(value, *action)

    result_152 = (
        sum(projected(((0, 2, 1), (1, 2, 0)))) % 2,
        sum(projected(_REMOTE_FOUR_POINT_ACTION)) % 2,
        sum(projected(cyclic.CYCLIC_ACTION)) % 2,
        sum(projected(five.NEW_THREE_POINT_ACTION)) % 2,
        sum(projected(six.TWO_POINT_ACTION)) % 2,
    )
    result_153 = (
        *_paired_action_bits(
            projected(seven.IDENTITY_FOUR_POINT_ACTION),
            seven.IDENTITY_FOUR_POINT_COVECTORS,
        ),
        *_paired_action_bits(
            projected(seven.TWISTED_FOUR_POINT_ACTION),
            (seven.TWISTED_FOUR_POINT_COVECTOR,),
        ),
    )
    result_154 = _paired_action_bits(
        projected(eight.NEW_FOUR_POINT_ACTION),
        (eight.NEW_FOUR_POINT_COVECTOR,),
    )
    result_155 = _paired_action_bits(
        projected(nine.INVERSE_FOUR_POINT_ACTION),
        (nine.INVERSE_FOUR_POINT_COVECTOR,),
    )
    result_156 = _paired_action_bits(
        projected(ten.FIVE_POINT_ACTION),
        ten.FIVE_POINT_COVECTORS,
    )
    result_157 = _paired_action_bits(
        projected(eleven.NEW_ACTION),
        eleven.NEW_COVECTORS,
    )
    bits = (*result_152, *result_153, *result_154, *result_155, *result_156, *result_157)
    assert len(bits) == 14
    return bits


def symbolic_syndrome(direction: ModuleVariables) -> tuple[int, ...]:
    _assert_direction(direction)
    linear, tensor = _symbolic_residual_coordinate(direction)
    wedge = _residual_tensor_to_wedge(linear, tensor)
    bits = (*_direct_fourteen_bits(wedge), sum(wedge.values()) % 2)
    assert len(bits) == 15 and all(bit in (0, 1) for bit in bits)
    return bits


def phi_infinity_hessian(
    left: ModuleVariables,
    right: ModuleVariables,
) -> int:
    return sum(symbolic_mixed_wedge(left, right).values()) % 2


@dataclass(frozen=True)
class ActiveAnchoredOccurrence:
    active_order: int
    residual_order: int
    slot: int
    polarity: int
    action: lift.Word


@lru_cache(maxsize=1)
def active_anchored_occurrences() -> tuple[ActiveAnchoredOccurrence, ...]:
    """Return the exact occurrence theorem after the anchored slot-one deletion."""

    active = tuple(
        ActiveAnchoredOccurrence(
            active_order=active_order,
            residual_order=residual_order,
            slot=occurrence.slot,
            polarity=occurrence.polarity,
            action=lift.quotient_reduce(occurrence.quotient_prefix),
        )
        for active_order, (residual_order, occurrence) in enumerate(
            (
                (residual_order, occurrence)
                for residual_order, occurrence in enumerate(residual_occurrences(), start=1)
                if occurrence.slot != 1
            ),
            start=1,
        )
    )
    assert len(active) == 12
    assert len({(record.slot, record.action) for record in active}) == 12
    return active


@dataclass(frozen=True)
class EqualityKernel:
    slot: int
    negative_active_orders: tuple[int, ...]
    integral_multiplicity: int
    mod_two_coefficient: int


@lru_cache(maxsize=1)
def internal_equality_kernels() -> tuple[EqualityKernel, ...]:
    by_slot: dict[int, list[int]] = defaultdict(list)
    for record in active_anchored_occurrences():
        if record.polarity == -1:
            by_slot[record.slot].append(record.active_order)
    kernels = tuple(
        EqualityKernel(
            slot=slot,
            negative_active_orders=tuple(by_slot[slot]),
            integral_multiplicity=len(by_slot[slot]),
            mod_two_coefficient=len(by_slot[slot]) % 2,
        )
        for slot in sorted(by_slot)
    )
    assert tuple(record.slot for record in kernels) == (0, 2, 3, 4)
    assert all(record.mod_two_coefficient == 1 for record in kernels)
    return kernels


@dataclass(frozen=True)
class InversionKernel:
    slot: int
    positive_active_order: int
    negative_active_order: int
    base_action: lift.Word
    paired_action: lift.Word
    multiplier: lift.Word
    mod_two_coefficient: int


@lru_cache(maxsize=1)
def internal_inversion_kernels() -> tuple[InversionKernel, ...]:
    active = active_anchored_occurrences()
    paired_orders = ((2, 3), (5, 6), (8, 9), (1, 4), (7, 10), (11, 12))
    kernels = []
    for positive_order, negative_order in paired_orders:
        positive = active[positive_order - 1]
        negative = active[negative_order - 1]
        assert positive.slot == negative.slot
        assert positive.polarity == 1 and negative.polarity == -1
        kernels.append(InversionKernel(
            slot=positive.slot,
            positive_active_order=positive_order,
            negative_active_order=negative_order,
            base_action=positive.action,
            paired_action=negative.action,
            multiplier=lift.quotient_multiply(
                negative.action,
                lift.quotient_inverse(positive.action),
            ),
            mod_two_coefficient=1,
        ))
    return tuple(kernels)


@dataclass(frozen=True)
class ExternalOrderKernel:
    left_active_order: int
    right_active_order: int
    left_slot: int
    left_action: lift.Word
    right_slot: int
    right_action: lift.Word
    integral_coefficient: int
    mod_two_coefficient: int

    @property
    def ordered_type_key(self) -> tuple[int, lift.Word, int, lift.Word]:
        return self.left_slot, self.left_action, self.right_slot, self.right_action

    @property
    def transpose_type_key(self) -> tuple[int, lift.Word, int, lift.Word]:
        return self.right_slot, self.right_action, self.left_slot, self.left_action


@lru_cache(maxsize=1)
def external_order_kernels() -> tuple[ExternalOrderKernel, ...]:
    active = active_anchored_occurrences()
    kernels = tuple(
        ExternalOrderKernel(
            left_active_order=left.active_order,
            right_active_order=right.active_order,
            left_slot=left.slot,
            left_action=left.action,
            right_slot=right.slot,
            right_action=right.action,
            integral_coefficient=left.polarity * right.polarity,
            mod_two_coefficient=(left.polarity * right.polarity) % 2,
        )
        for left_index, left in enumerate(active)
        for right in active[left_index + 1:]
    )
    keys = {record.ordered_type_key for record in kernels}
    assert len(kernels) == len(keys) == 66
    assert not any(record.transpose_type_key in keys for record in kernels)
    return kernels


def _shortlex_key(vertex: lift.Word) -> tuple[int, lift.Word]:
    canonical = lift.c_vertex(vertex)
    return len(canonical), canonical


def _lt_mod_two(left: lift.ModuleVector, right: lift.ModuleVector) -> int:
    canonical_left = lift.add_vectors(left)
    canonical_right = lift.add_vectors(right)
    return sum(
        left_coefficient * right_coefficient
        for left_vertex, left_coefficient in canonical_left.items()
        for right_vertex, right_coefficient in canonical_right.items()
        if _shortlex_key(left_vertex) < _shortlex_key(right_vertex)
    ) % 2


def _eq_infinity(left: lift.ModuleVector, right: lift.ModuleVector) -> int:
    canonical_left = lift.add_vectors(left)
    canonical_right = lift.add_vectors(right)
    augmentation = sum(canonical_left.values()) * sum(canonical_right.values())
    diagonal = sum(
        coefficient * canonical_right.get(vertex, 0)
        for vertex, coefficient in canonical_left.items()
    )
    return (augmentation + diagonal) % 2


def _polarized_inversion(
    multiplier: lift.Word,
    left: lift.ModuleVector,
    right: lift.ModuleVector,
) -> int:
    canonical_left = lift.add_vectors(left)
    canonical_right = lift.add_vectors(right)
    vertices = sorted(
        set(canonical_left) | set(canonical_right),
        key=_shortlex_key,
    )
    value = 0
    for left_index, left_vertex in enumerate(vertices):
        translated_left = lift.c_vertex(
            lift.quotient_multiply(multiplier, left_vertex),
        )
        for right_vertex in vertices[left_index + 1:]:
            translated_right = lift.c_vertex(
                lift.quotient_multiply(multiplier, right_vertex),
            )
            if _shortlex_key(translated_left) > _shortlex_key(translated_right):
                value += (
                    canonical_left.get(left_vertex, 0)
                    * canonical_right.get(right_vertex, 0)
                    + canonical_right.get(left_vertex, 0)
                    * canonical_left.get(right_vertex, 0)
                )
    return value % 2


def _active_translated_currents(
    direction: ModuleVariables,
) -> tuple[lift.ModuleVector, ...]:
    _assert_direction(direction)
    assert not lift.add_vectors(direction[1]), "anchored direction has nonzero slot one"
    return tuple(
        _action(record.action, direction[record.slot])
        for record in active_anchored_occurrences()
    )


@dataclass(frozen=True)
class AnchoredKernelSubtotals:
    equality_terms: tuple[int, ...]
    inversion_terms: tuple[int, ...]
    external_terms: tuple[int, ...]
    external_reversed_terms: tuple[int, ...]

    @property
    def equality(self) -> int:
        return sum(self.equality_terms) % 2

    @property
    def inversion(self) -> int:
        return sum(self.inversion_terms) % 2

    @property
    def external(self) -> int:
        return sum(self.external_terms) % 2

    @property
    def external_reversed(self) -> int:
        return sum(self.external_reversed_terms) % 2

    @property
    def total(self) -> int:
        return (self.equality + self.inversion + self.external) % 2


def anchored_direction_kernel_subtotals(
    left: ModuleVariables,
    right: ModuleVariables,
) -> AnchoredKernelSubtotals:
    """Evaluate E+I+O for any two anchored homogeneous directions.

    The records come from the Task 1 occurrence theorem.  Slot one vanishes
    by the anchored source construction, while slots two through four are
    the unique linear finite tree flow.  No bounded-source assumption enters.
    """

    left_currents = _active_translated_currents(left)
    right_currents = _active_translated_currents(right)
    equality_terms = tuple(
        record.mod_two_coefficient * _eq_infinity(left[record.slot], right[record.slot]) % 2
        for record in internal_equality_kernels()
    )
    inversion_terms = tuple(
        record.mod_two_coefficient * _polarized_inversion(
            record.multiplier,
            _action(record.base_action, left[record.slot]),
            _action(record.base_action, right[record.slot]),
        ) % 2
        for record in internal_inversion_kernels()
    )
    external_terms = tuple(
        record.mod_two_coefficient * (
            _lt_mod_two(
                left_currents[record.left_active_order - 1],
                right_currents[record.right_active_order - 1],
            )
            + _lt_mod_two(
                right_currents[record.left_active_order - 1],
                left_currents[record.right_active_order - 1],
            )
        ) % 2
        for record in external_order_kernels()
    )
    external_reversed_terms = tuple(
        record.mod_two_coefficient * (
            _lt_mod_two(
                left_currents[record.right_active_order - 1],
                right_currents[record.left_active_order - 1],
            )
            + _lt_mod_two(
                right_currents[record.right_active_order - 1],
                left_currents[record.left_active_order - 1],
            )
        ) % 2
        for record in external_order_kernels()
    )
    subtotals = AnchoredKernelSubtotals(
        equality_terms=equality_terms,
        inversion_terms=inversion_terms,
        external_terms=external_terms,
        external_reversed_terms=external_reversed_terms,
    )
    assert subtotals.external == subtotals.external_reversed
    assert subtotals.total == phi_infinity_hessian(left, right)
    return subtotals


def anchored_hessian_subtotals(
    left: lift.Word,
    right: lift.Word,
) -> AnchoredKernelSubtotals:
    return anchored_direction_kernel_subtotals(
        tree.anchored_direction(lift.c_vertex(left)),
        tree.anchored_direction(lift.c_vertex(right)),
    )


def beta_infinity(left: lift.Word, right: lift.Word) -> int:
    return anchored_hessian_subtotals(left, right).total


def anchored_pair_value(
    left: lift.Word,
    right: lift.Word,
    epsilon: int,
) -> tuple[int, tuple[int, ...]]:
    assert epsilon in (-1, 1)
    canonical_left = lift.c_vertex(left)
    canonical_right = lift.c_vertex(right)
    pair_source = lift.add_vectors(
        {canonical_left: 1},
        {canonical_right: epsilon},
    )
    boundary = lift.apply_operator(_operators()[0], pair_source)
    if source.orbit_sums(boundary) != (0, 0):
        return 0, (0,) * 15
    direction = source.build_l0_direction(pair_source).variables
    return 1, symbolic_syndrome(direction)


def diagonal_left_pair_value(
    context: lift.Word,
    left: lift.Word,
    right: lift.Word,
    epsilon: int,
) -> tuple[int, tuple[int, ...]]:
    quotient_context = lift.quotient_reduce(context)
    translated_left = lift.c_vertex(lift.quotient_multiply(quotient_context, left))
    translated_right = lift.c_vertex(lift.quotient_multiply(quotient_context, right))
    return anchored_pair_value(translated_left, translated_right, epsilon)


@dataclass(frozen=True)
class AnchoredKernelNormalForm:
    active_occurrence_count: int
    active_slot_counts: tuple[int, int, int, int, int]
    equality_terms: int
    inversion_terms: int
    external_pair_terms: int
    external_oriented_monomials: int
    duplicate_external_keys: int
    generic_transpose_pairs: int
    slot4_t_inversion_coefficient: int
    slot_one_zero_on_anchored_directions: bool
    external_reversal_from_homogeneity: bool
    pullback_uses_unique_linear_tree_flow: bool
    coefficient_sha256: str


@lru_cache(maxsize=1)
def anchored_kernel_normal_form() -> AnchoredKernelNormalForm:
    active = active_anchored_occurrences()
    equality = internal_equality_kernels()
    inversion = internal_inversion_kernels()
    external = external_order_kernels()
    active_payload = tuple(
        (
            record.active_order,
            record.residual_order,
            record.slot,
            record.polarity,
            lift.literal(record.action),
        )
        for record in active
    )
    equality_payload = tuple(
        (
            record.slot,
            record.negative_active_orders,
            record.integral_multiplicity,
            record.mod_two_coefficient,
        )
        for record in equality
    )
    inversion_payload = tuple(
        (
            record.slot,
            record.positive_active_order,
            record.negative_active_order,
            lift.literal(record.base_action),
            lift.literal(record.paired_action),
            lift.literal(record.multiplier),
            record.mod_two_coefficient,
        )
        for record in inversion
    )
    external_payload = tuple(
        (
            record.left_active_order,
            record.right_active_order,
            record.left_slot,
            lift.literal(record.left_action),
            record.right_slot,
            lift.literal(record.right_action),
            record.integral_coefficient,
            record.mod_two_coefficient,
        )
        for record in external
    )
    keys = tuple(record.ordered_type_key for record in external)
    key_set = set(keys)
    duplicate_keys = len(keys) - len(key_set)
    transpose_pairs = sum(record.transpose_type_key in key_set for record in external)
    slot_counts = tuple(
        sum(record.slot == slot for record in active)
        for slot in range(5)
    )
    slot4_t = tuple(record for record in inversion if record.slot == 4)
    assert len(slot4_t) == 1
    return AnchoredKernelNormalForm(
        active_occurrence_count=len(active),
        active_slot_counts=slot_counts,  # type: ignore[arg-type]
        equality_terms=len(equality),
        inversion_terms=len(inversion),
        external_pair_terms=len(external),
        external_oriented_monomials=2 * len(external),
        duplicate_external_keys=duplicate_keys,
        generic_transpose_pairs=transpose_pairs,
        slot4_t_inversion_coefficient=slot4_t[0].mod_two_coefficient,
        slot_one_zero_on_anchored_directions=True,
        external_reversal_from_homogeneity=True,
        pullback_uses_unique_linear_tree_flow=True,
        coefficient_sha256=sha256(repr((
            active_payload,
            equality_payload,
            inversion_payload,
            external_payload,
        )).encode()).hexdigest(),
    )


@dataclass(frozen=True)
class KernelNormalForm:
    occurrence_count: int
    slot_counts: tuple[int, int, int, int, int]
    positive_internal_terms: int
    negative_internal_terms: int
    external_pair_terms: int
    propagated_diagonal_terms: int
    coefficient_sha256: str


def kernel_normal_form() -> KernelNormalForm:
    occurrences = residual_occurrences()
    literal_occurrences = tuple(
        (occurrence.slot, occurrence.polarity, lift.literal(occurrence.quotient_prefix))
        for occurrence in occurrences
    )
    external_records = tuple(
        (left_index, right_index, left.polarity * right.polarity)
        for left_index, left in enumerate(occurrences)
        for right_index, right in enumerate(occurrences)
        if left_index < right_index
    )
    payload = literal_occurrences, external_records
    slot_counts = tuple(
        sum(occurrence.slot == slot for occurrence in occurrences)
        for slot in range(5)
    )
    return KernelNormalForm(
        occurrence_count=len(occurrences),
        slot_counts=slot_counts,  # type: ignore[arg-type]
        positive_internal_terms=sum(occurrence.polarity == 1 for occurrence in occurrences),
        negative_internal_terms=sum(occurrence.polarity == -1 for occurrence in occurrences),
        external_pair_terms=len(external_records),
        propagated_diagonal_terms=len(occurrences),
        coefficient_sha256=sha256(repr(payload).encode()).hexdigest(),
    )


def _bits(value: tuple[int, ...]) -> str:
    return "".join(str(bit) for bit in value)


def _xor(*values: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sum(entries) % 2 for entries in zip(*values))


def _tensor_records(value: Tensor) -> tuple[tuple[str, str, int], ...]:
    return tuple(
        (lift.literal(left), lift.literal(right), coefficient)
        for (left, right), coefficient in sorted(
            value.items(),
            key=lambda item: (
                len(item[0][0]),
                item[0][0],
                len(item[0][1]),
                item[0][1],
            ),
        )
    )


def _tensor_sha256(value: Tensor) -> str:
    return sha256(repr(_tensor_records(value)).encode()).hexdigest()


def _direct_raw_residual_tensor(variables: ModuleVariables) -> Tensor:
    residual = escape.corrected_residual(variables)
    return raw_tensor_from_kernel_word(escape.schreier_word(residual))


def _direct_syndrome(direction: ModuleVariables) -> tuple[int, ...]:
    _assert_direction(direction)
    variables = escape.add_variables(_base_variables(), direction)
    residual = escape.corrected_residual(variables)
    wedge = escape.degree_two(escape.schreier_word(residual))
    bits = (*_direct_fourteen_bits(wedge), sum(wedge.values()) % 2)
    assert len(bits) == 15 and all(bit in (0, 1) for bit in bits)
    return bits


@dataclass(frozen=True)
class Certificate:
    normal_form: KernelNormalForm
    anchored_normal_form: AnchoredKernelNormalForm
    operator_matches: tuple[bool, bool, bool, bool, bool]
    raw_commutator_tensor: tuple[tuple[str, str, int], ...]
    raw_commutator_mod_two_diagonal_labels: tuple[str, ...]
    raw_commutator_exterior_zero: bool
    alternate_mixed_raw_matches: bool
    alternate_mixed_tensor_terms: int
    alternate_mixed_tensor_l1: int
    alternate_mixed_tensor_sha256: str
    base_raw_matches: bool
    base_tensor_terms: int
    base_tensor_l1: int
    base_tensor_sha256: str
    unary_raw_matches: tuple[bool, bool]
    syndrome_matches: tuple[bool, bool, bool, bool]
    bounded_base_syndrome: str
    bounded_unary_syndromes: tuple[str, str]
    bounded_cross_syndrome: str
    bounded_biadditivity: str
    bounded_zero_self_polarizations: int
    near_survivor_pair_values: tuple[tuple[str, str, int, int, str], ...]
    near_survivor_direct_matches: tuple[bool, bool]
    negative_balanced_pair_value: tuple[str, str, int, int, str]
    negative_balanced_direct_match: bool
    unbalanced_pair_value: tuple[str, str, int, int, str]
    near_survivor_extensions: tuple[tuple[str, str, str], ...]
    near_survivor_extension_direct_matches: tuple[tuple[bool, bool], ...]
    tracked_direction_syndromes: tuple[str, ...]
    tracked_direction_direct_matches: tuple[bool, ...]


@lru_cache(maxsize=1)
def phi_infinity_hessian_certificate() -> Certificate:
    normal_form = kernel_normal_form()
    anchored_normal_form = anchored_kernel_normal_form()
    _, _, _, _, operators = escape.recurrence_data()
    operator_matches = tuple(
        occurrence_operator(slot) == operator
        for slot, operator in enumerate(operators)
    )

    identity: lift.Word = ()
    doubled_lift = lift.power_word(lift.relation_generator(identity), 2)
    commutator = lift.multiply(
        doubled_lift,
        lift.TARGET,
        lift.inverse(doubled_lift),
        lift.inverse(lift.TARGET),
    )
    assert lift.quotient_reduce(commutator) == ()
    raw_commutator = raw_tensor_from_kernel_word(escape.schreier_word(commutator))
    odd_diagonal_labels = tuple(
        lift.literal(left)
        for (left, right), coefficient in raw_commutator.items()
        if left == right and coefficient % 2
    )
    exterior_zero = not any(
        coefficient % 2
        for (left, right), coefficient in raw_commutator.items()
        if left != right
    )

    base = _base_variables()
    alternate_10 = escape.variables_from_entries(escape.ALTERNATE_10)
    alternate_01 = escape.variables_from_entries(escape.ALTERNATE_01)
    left = escape.subtract_variables(alternate_10, base)
    right = escape.subtract_variables(alternate_01, base)
    alternate_11 = escape.add_variables(base, left, right)
    direct_mixed = _add_tensors(
        _direct_raw_residual_tensor(alternate_11),
        _scale_tensor(_direct_raw_residual_tensor(alternate_10), -1),
        _scale_tensor(_direct_raw_residual_tensor(alternate_01), -1),
        _direct_raw_residual_tensor(base),
    )
    symbolic_mixed = symbolic_mixed_tensor(left, right)

    zero: ModuleVariables = ({}, {}, {}, {}, {})
    x = tree.anchored_direction(lift.parse_quotient("TT"))
    y = tree.anchored_direction(lift.parse_quotient("TTTct"))
    z = tree.anchored_direction(lift.parse_quotient("Tctt"))
    direct_base = _direct_raw_residual_tensor(base)
    direct_x = _direct_raw_residual_tensor(escape.add_variables(base, x))
    direct_y = _direct_raw_residual_tensor(escape.add_variables(base, y))
    symbolic_base = symbolic_residual_tensor(zero)
    syndromes = tuple(
        symbolic_syndrome(direction)
        for direction in (zero, x, y, tree.add_directions(x, y))
    )
    direct_syndromes = tuple(
        _direct_syndrome(direction)
        for direction in (zero, x, y, tree.add_directions(x, y))
    )
    constant, syndrome_x, syndrome_y, syndrome_xy = syndromes
    unary_x = _xor(syndrome_x, constant)
    unary_y = _xor(syndrome_y, constant)
    cross = _xor(syndrome_xy, syndrome_x, syndrome_y, constant)
    biadditivity = _xor(
        symbolic_syndrome(tree.add_directions(x, y, z)),
        syndrome_xy,
        symbolic_syndrome(z),
        constant,
    )
    fixed_directions = (x, y, z, tree.add_directions(x, y))
    zero_self = sum(phi_infinity_hessian(direction, direction) == 0 for direction in fixed_directions)

    near_pairs = (
        ("TT", "TTTct", 1),
        ("Tctt", "Tctct", 1),
    )
    near_pair_values = []
    near_pair_matches = []
    for left_label, right_label, epsilon in near_pairs:
        left_vertex = lift.parse_quotient(left_label)
        right_vertex = lift.parse_quotient(right_label)
        value = anchored_pair_value(left_vertex, right_vertex, epsilon)
        pair_source = lift.add_vectors(
            {left_vertex: 1},
            {right_vertex: epsilon},
        )
        direct_direction = source.build_l0_direction(pair_source).variables
        direct_value = (1, _direct_syndrome(direct_direction))
        near_pair_values.append((
            left_label,
            right_label,
            epsilon,
            value[0],
            _bits(value[1]),
        ))
        near_pair_matches.append(value == direct_value)

    negative_left_label = "TTT"
    negative_right_label = "cTTT"
    negative_epsilon = -1
    negative_left = lift.parse_quotient(negative_left_label)
    negative_right = lift.parse_quotient(negative_right_label)
    negative_value = anchored_pair_value(
        negative_left,
        negative_right,
        negative_epsilon,
    )
    negative_source = lift.add_vectors(
        {negative_left: 1},
        {negative_right: negative_epsilon},
    )
    negative_direct = (
        1,
        _direct_syndrome(source.build_l0_direction(negative_source).variables),
    )
    negative_pair_record = (
        negative_left_label,
        negative_right_label,
        negative_epsilon,
        negative_value[0],
        _bits(negative_value[1]),
    )

    unbalanced_left_label = ""
    unbalanced_right_label = "T"
    unbalanced_epsilon = 1
    unbalanced_value = anchored_pair_value(
        lift.parse_quotient(unbalanced_left_label),
        lift.parse_quotient(unbalanced_right_label),
        unbalanced_epsilon,
    )
    unbalanced_pair_record = (
        unbalanced_left_label,
        unbalanced_right_label,
        unbalanced_epsilon,
        unbalanced_value[0],
        _bits(unbalanced_value[1]),
    )

    extension_records = []
    extension_matches = []
    for context_label in ("c", "t", "T"):
        context = _parse_quotient_word(context_label)
        values = []
        matches = []
        for left_label, right_label, epsilon in near_pairs:
            left_vertex = lift.parse_quotient(left_label)
            right_vertex = lift.parse_quotient(right_label)
            value = diagonal_left_pair_value(context, left_vertex, right_vertex, epsilon)
            translated_left = lift.c_vertex(lift.quotient_multiply(context, left_vertex))
            translated_right = lift.c_vertex(lift.quotient_multiply(context, right_vertex))
            translated_source = lift.add_vectors(
                {translated_left: 1},
                {translated_right: epsilon},
            )
            direct = (
                1,
                _direct_syndrome(source.build_l0_direction(translated_source).variables),
            )
            values.append(_bits(value[1]))
            matches.append(value == direct)
        extension_records.append((context_label, values[0], values[1]))
        extension_matches.append((matches[0], matches[1]))

    tracked_directions = (
        *six.known_directions(base),
        *(
            source.build_l0_direction(source.source_from_entries(entries)).variables
            for entries in source.KNOWN_SOURCES
        ),
    )
    tracked_symbolic = tuple(symbolic_syndrome(direction) for direction in tracked_directions)
    tracked_direct = tuple(_direct_syndrome(direction) for direction in tracked_directions)
    return Certificate(
        normal_form=normal_form,
        anchored_normal_form=anchored_normal_form,
        operator_matches=operator_matches,  # type: ignore[arg-type]
        raw_commutator_tensor=_tensor_records(raw_commutator),
        raw_commutator_mod_two_diagonal_labels=odd_diagonal_labels,
        raw_commutator_exterior_zero=exterior_zero,
        alternate_mixed_raw_matches=symbolic_mixed == direct_mixed,
        alternate_mixed_tensor_terms=len(symbolic_mixed),
        alternate_mixed_tensor_l1=sum(abs(coefficient) for coefficient in symbolic_mixed.values()),
        alternate_mixed_tensor_sha256=_tensor_sha256(symbolic_mixed),
        base_raw_matches=symbolic_base == direct_base,
        base_tensor_terms=len(symbolic_base),
        base_tensor_l1=sum(abs(coefficient) for coefficient in symbolic_base.values()),
        base_tensor_sha256=_tensor_sha256(symbolic_base),
        unary_raw_matches=(
            symbolic_unary_tensor(x) == _add_tensors(direct_x, _scale_tensor(direct_base, -1)),
            symbolic_unary_tensor(y) == _add_tensors(direct_y, _scale_tensor(direct_base, -1)),
        ),
        syndrome_matches=tuple(
            symbolic == direct
            for symbolic, direct in zip(syndromes, direct_syndromes)
        ),  # type: ignore[arg-type]
        bounded_base_syndrome=_bits(constant),
        bounded_unary_syndromes=(_bits(unary_x), _bits(unary_y)),
        bounded_cross_syndrome=_bits(cross),
        bounded_biadditivity=_bits(biadditivity),
        bounded_zero_self_polarizations=zero_self,
        near_survivor_pair_values=tuple(near_pair_values),
        near_survivor_direct_matches=tuple(near_pair_matches),  # type: ignore[arg-type]
        negative_balanced_pair_value=negative_pair_record,
        negative_balanced_direct_match=negative_value == negative_direct,
        unbalanced_pair_value=unbalanced_pair_record,
        near_survivor_extensions=tuple(extension_records),
        near_survivor_extension_direct_matches=tuple(extension_matches),
        tracked_direction_syndromes=tuple(_bits(value) for value in tracked_symbolic),
        tracked_direction_direct_matches=tuple(
            symbolic == direct
            for symbolic, direct in zip(tracked_symbolic, tracked_direct)
        ),
    )


if __name__ == "__main__":
    print(phi_infinity_hessian_certificate())
