"""Exact immediate two-stabilization corridors for balanced rank-two pairs."""

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from itertools import product

from experiments.equivalence_classes.lib.acmoves import canon
from experiments.equivalence_classes.lib.autcanon import aut_canon


OLD_ALPHABET = "xXyY"
ALPHABET = "xXyYzZtT"
VALID_LETTERS = frozenset(ALPHABET)


def inverse(word: str) -> str:
    _validate_word(word)
    return "".join(letter.swapcase() for letter in reversed(word))


def free_reduce(word: str) -> str:
    _validate_word(word)
    stack: list[str] = []
    for letter in word:
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def cyclic_orientations(word: str) -> tuple[str, ...]:
    reduced = free_reduce(word)
    if not reduced:
        return ("",)
    orientations: set[str] = set()
    for spelling in (reduced, inverse(reduced)):
        for offset in range(len(spelling)):
            orientations.add(spelling[offset:] + spelling[:offset])
    return tuple(sorted(orientations))


def substitute_new(template: str, word_z: str, word_t: str) -> str:
    _validate_old_word(word_z)
    _validate_old_word(word_t)
    _validate_word(template)
    images = {
        "z": word_z,
        "Z": inverse(word_z),
        "t": word_t,
        "T": inverse(word_t),
    }
    return free_reduce("".join(images.get(letter, letter) for letter in template))


def substitute_generator(word: str, generator: str, expr: str) -> str:
    if generator not in "xyzt":
        raise ValueError(f"unknown generator: {generator!r}")
    _validate_word(word)
    _validate_word(expr)
    expr_inverse = inverse(expr)
    return free_reduce(
        "".join(
            expr
            if letter == generator
            else expr_inverse
            if letter == generator.upper()
            else letter
            for letter in word
        )
    )


def solve_isolator(word: str, generator: str) -> str:
    if generator not in "xyzt":
        raise ValueError(f"unknown generator: {generator!r}")
    _validate_word(word)
    positions = [
        index
        for index, letter in enumerate(word)
        if letter.lower() == generator
    ]
    if len(positions) != 1:
        raise ValueError(
            f"isolator must contain exactly one {generator} letter; "
            f"found {len(positions)}"
        )
    index = positions[0]
    rotated = word[index:] + word[:index]
    suffix = rotated[1:]
    return free_reduce(
        inverse(suffix) if rotated[0].islower() else suffix
    )


def derive_rank3(
    pair: tuple[str, str],
    source_index: int,
    word_z: str,
    word_t: str,
    template: str,
    eliminated: str = "y",
) -> tuple[str, str, str]:
    if len(pair) != 2:
        raise ValueError("two-stabilization corridors require two relators")
    if source_index not in (0, 1):
        raise ValueError("source_index must be 0 or 1")
    if eliminated not in "xy":
        raise ValueError("first eliminated generator must be x or y")
    if not any(letter.lower() == "z" for letter in template):
        raise ValueError("template must use z")
    if not any(letter.lower() == "t" for letter in template):
        raise ValueError("template must use t")
    expanded = substitute_new(template, word_z, word_t)
    if expanded not in cyclic_orientations(pair[source_index]):
        raise ValueError(
            f"expanded template {expanded!r} is not a source relator orientation"
        )
    expression = solve_isolator(template, eliminated)
    other = pair[1 - source_index]
    return (
        substitute_generator(other, eliminated, expression),
        substitute_generator("Z" + word_z, eliminated, expression),
        substitute_generator("T" + word_t, eliminated, expression),
    )


def remove_second(
    rank3: tuple[str, str, str],
    isolator_index: int,
    eliminated: str = "x",
) -> tuple[str, str]:
    if len(rank3) != 3:
        raise ValueError("second removal requires three relators")
    if isolator_index not in (0, 1, 2):
        raise ValueError("isolator_index must be 0, 1, or 2")
    expression = solve_isolator(rank3[isolator_index], eliminated)
    outputs = [
        substitute_generator(relator, eliminated, expression)
        for index, relator in enumerate(rank3)
        if index != isolator_index
    ]
    return tuple(_relabel_survivors(word) for word in outputs)


@dataclass(frozen=True)
class TwoStabilizationRow:
    word_z: str
    word_t: str
    template: str
    expanded: str
    expression_y: str
    rank3: tuple[str, str, str]
    second_isolator_index: int
    expression_x: str
    output: tuple[str, str]

    def to_json(self) -> dict[str, object]:
        return {
            "word_z": self.word_z,
            "word_t": self.word_t,
            "template": self.template,
            "expanded": self.expanded,
            "expression_y": self.expression_y,
            "rank3": list(self.rank3),
            "second_isolator_index": self.second_isolator_index,
            "expression_x": self.expression_x,
            "output": list(self.output),
        }


@dataclass(frozen=True)
class AutRecord:
    output: tuple[str, str]
    minimum_total: int
    representative: tuple[str, str]
    phi: dict[str, str]

    def to_json(self) -> dict[str, object]:
        return {
            "output": list(self.output),
            "minimum_total": self.minimum_total,
            "representative": list(self.representative),
            "phi": self.phi,
        }


@dataclass(frozen=True)
class TwoStabilizationCensus:
    pair: tuple[str, str]
    max_word_length: int
    max_template_length: int
    defining_word_count: int
    structural_template_count: int
    tested_cases: int
    accepted_source_identities: int
    distinct_rank3_count: int
    certificates: tuple[TwoStabilizationRow, ...]
    distinct_raw_output_count: int
    aut_records: tuple[AutRecord, ...]
    floor_distribution: dict[int, int]
    trace_sha256: str

    @property
    def triangular_certificate_count(self) -> int:
        return len(self.certificates)

    @property
    def minimum_output_floor(self) -> int | None:
        if not self.aut_records:
            return None
        return min(record.minimum_total for record in self.aut_records)

    def to_json(self) -> dict[str, object]:
        return {
            "pair": list(self.pair),
            "bounds": {
                "max_word_length": self.max_word_length,
                "max_template_length": self.max_template_length,
            },
            "defining_word_count": self.defining_word_count,
            "structural_template_count": self.structural_template_count,
            "tested_cases": self.tested_cases,
            "accepted_source_identities": self.accepted_source_identities,
            "distinct_rank3_count": self.distinct_rank3_count,
            "triangular_certificate_count": self.triangular_certificate_count,
            "distinct_raw_output_count": self.distinct_raw_output_count,
            "trace_sha256": self.trace_sha256,
            "floor_distribution": {
                str(floor): count
                for floor, count in sorted(self.floor_distribution.items())
            },
            "minimum_output_floor": self.minimum_output_floor,
            "certificates": [row.to_json() for row in self.certificates],
            "aut_records": [record.to_json() for record in self.aut_records],
        }


def enumerate_immediate_two_stabilizations(
    pair: tuple[str, str],
    max_word_length: int = 2,
    max_template_length: int = 6,
) -> TwoStabilizationCensus:
    if len(pair) != 2:
        raise ValueError("two-stabilization census requires two relators")
    if max_word_length < 1:
        raise ValueError("max_word_length must be positive")
    if max_template_length < 2:
        raise ValueError("max_template_length must be at least two")
    for relator in pair:
        _validate_old_word(relator)

    words = tuple(_reduced_words(OLD_ALPHABET, 1, max_word_length))
    templates = tuple(
        template
        for template in _reduced_words(
            ALPHABET, 2, max_template_length, cyclic=True
        )
        if sum(letter.lower() == "y" for letter in template) == 1
        and any(letter.lower() == "z" for letter in template)
        and any(letter.lower() == "t" for letter in template)
    )
    source_orientations = frozenset(cyclic_orientations(pair[1]))
    trace = sha256()
    accepted_source = 0
    rank3_states: set[tuple[str, str, str]] = set()
    certificates: list[TwoStabilizationRow] = []

    for word_z in words:
        for word_t in words:
            for template in templates:
                expanded = substitute_new(template, word_z, word_t)
                source_match = expanded in source_orientations
                trace.update(
                    b"S\0"
                    + "\0".join(
                        (
                            word_z,
                            word_t,
                            template,
                            expanded,
                            "1" if source_match else "0",
                        )
                    ).encode("ascii")
                    + b"\n"
                )
                if not source_match:
                    continue
                accepted_source += 1
                expression_y = solve_isolator(template, "y")
                rank3 = derive_rank3(
                    pair, 1, word_z, word_t, template, eliminated="y"
                )
                rank3_states.add(rank3)
                for isolator_index, relator in enumerate(rank3):
                    x_count = sum(
                        letter.lower() == "x" for letter in relator
                    )
                    accepted = x_count == 1
                    trace.update(
                        b"X\0"
                        + "\0".join(
                            (
                                word_z,
                                word_t,
                                template,
                                str(isolator_index),
                                str(x_count),
                                "1" if accepted else "0",
                            )
                        ).encode("ascii")
                        + b"\n"
                    )
                    if not accepted:
                        continue
                    expression_x = solve_isolator(relator, "x")
                    output = remove_second(rank3, isolator_index, "x")
                    certificates.append(
                        TwoStabilizationRow(
                            word_z=word_z,
                            word_t=word_t,
                            template=template,
                            expanded=expanded,
                            expression_y=expression_y,
                            rank3=rank3,
                            second_isolator_index=isolator_index,
                            expression_x=expression_x,
                            output=output,
                        )
                    )

    raw_outputs = {row.output for row in certificates}
    canonical_outputs = sorted({canon(*output) for output in raw_outputs})
    aut_records: list[AutRecord] = []
    floor_by_canonical: dict[tuple[str, str], int] = {}
    for output in canonical_outputs:
        minimum_total, representative, phi = aut_canon(output)
        floor_by_canonical[output] = minimum_total
        aut_records.append(
            AutRecord(
                output=output,
                minimum_total=minimum_total,
                representative=representative,
                phi=phi,
            )
        )
    floor_distribution = Counter(
        floor_by_canonical[canon(*output)] for output in raw_outputs
    )
    return TwoStabilizationCensus(
        pair=tuple(pair),
        max_word_length=max_word_length,
        max_template_length=max_template_length,
        defining_word_count=len(words),
        structural_template_count=len(templates),
        tested_cases=len(words) * len(words) * len(templates),
        accepted_source_identities=accepted_source,
        distinct_rank3_count=len(rank3_states),
        certificates=tuple(certificates),
        distinct_raw_output_count=len(raw_outputs),
        aut_records=tuple(aut_records),
        floor_distribution=dict(sorted(floor_distribution.items())),
        trace_sha256=trace.hexdigest(),
    )


def _validate_word(word: str) -> None:
    invalid = [letter for letter in word if letter not in VALID_LETTERS]
    if invalid:
        raise ValueError(f"invalid letters: {invalid!r}")


def _validate_old_word(word: str) -> None:
    if any(letter not in OLD_ALPHABET for letter in word):
        raise ValueError("old words must use only x and y")


def _relabel_survivors(word: str) -> str:
    if any(letter.lower() in ("x", "y") for letter in word):
        raise ValueError("old generator survived second removal")
    return free_reduce(
        "".join(
            "x"
            if letter == "z"
            else "X"
            if letter == "Z"
            else "y"
            if letter == "t"
            else "Y"
            if letter == "T"
            else letter
            for letter in word
        )
    )


def _reduced_words(
    alphabet: str,
    minimum_length: int,
    maximum_length: int,
    cyclic: bool = False,
):
    for length in range(minimum_length, maximum_length + 1):
        for letters in product(alphabet, repeat=length):
            if any(
                letters[index] == letters[index + 1].swapcase()
                for index in range(length - 1)
            ):
                continue
            if cyclic and length > 1 and letters[0] == letters[-1].swapcase():
                continue
            yield "".join(letters)
