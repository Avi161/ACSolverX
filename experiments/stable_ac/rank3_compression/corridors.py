"""Exact finite word-equation census for hidden rank-3 corridors.

This is not an AC graph search.  It enumerates the finite statement in
``literature/proofs/AK3_RANK3_COMPRESSION.md``: a defining word ``z = w`` and
an isolator template whose literal ``z -> w`` expansion is one input relator.
Every accepted row is therefore a stable-AC transform by Theorem 3.1 there.
"""

from dataclasses import dataclass
from hashlib import sha256
from itertools import product

from experiments.equivalence_classes.lib.acmoves import canon
from experiments.equivalence_classes.lib.autcanon import aut_canon


WORD_ALPHABET = "xXyY"
TEMPLATE_ALPHABET = "xXyYzZ"
VALID_LETTERS = frozenset(TEMPLATE_ALPHABET)


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


def substitute_generator(word: str, generator: str, expr: str) -> str:
    if generator not in "xyz":
        raise ValueError(f"generator must be lowercase x, y, or z: {generator!r}")
    _validate_word(word)
    _validate_word(expr)
    expr_inverse = inverse(expr)
    pieces: list[str] = []
    for letter in word:
        if letter.lower() != generator:
            pieces.append(letter)
        elif letter.islower():
            pieces.append(expr)
        else:
            pieces.append(expr_inverse)
    return free_reduce("".join(pieces))


def substitute_z(template: str, word: str) -> str:
    return substitute_generator(template, "z", word)


def solve_isolator(template: str, eliminated: str) -> str:
    if eliminated not in "xy":
        raise ValueError(f"eliminated generator must be x or y: {eliminated!r}")
    _validate_word(template)
    positions = [
        index
        for index, letter in enumerate(template)
        if letter.lower() == eliminated
    ]
    if len(positions) != 1:
        raise ValueError(
            f"isolator must contain exactly one {eliminated} letter; "
            f"found {len(positions)}"
        )
    index = positions[0]
    rotated = template[index:] + template[:index]
    leading = rotated[0]
    suffix = rotated[1:]
    if any(letter.lower() == eliminated for letter in suffix):
        raise AssertionError("unique eliminated letter reappeared after rotation")
    return free_reduce(inverse(suffix) if leading.islower() else suffix)


def corridor_output(
    pair: tuple[str, str],
    source_index: int,
    word: str,
    template: str,
    eliminated: str,
) -> tuple[str, str]:
    if len(pair) != 2:
        raise ValueError("corridors require exactly two relators")
    if source_index not in (0, 1):
        raise ValueError("source_index must be 0 or 1")
    if template.count("z") + template.count("Z") < 1:
        raise ValueError("template must contain z or Z")
    substituted = substitute_z(template, word)
    if substituted not in cyclic_orientations(pair[source_index]):
        raise ValueError(
            f"expanded template {substituted!r} is not a source relator orientation"
        )
    expression = solve_isolator(template, eliminated)
    other = pair[1 - source_index]
    output_other = substitute_generator(other, eliminated, expression)
    output_defining = substitute_generator("Z" + word, eliminated, expression)
    return (
        _relabel_z(output_other, eliminated),
        _relabel_z(output_defining, eliminated),
    )


@dataclass(frozen=True)
class CorridorRow:
    source_index: int
    source_orientation: str
    eliminated: str
    word: str
    template: str
    substituted: str
    expression: str
    output: tuple[str, str]

    def to_json(self) -> dict[str, object]:
        return {
            "source_index": self.source_index,
            "source_orientation": self.source_orientation,
            "eliminated": self.eliminated,
            "word": self.word,
            "template": self.template,
            "substituted": self.substituted,
            "expression": self.expression,
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
class CorridorCensus:
    pair: tuple[str, str]
    max_word_length: int
    max_template_length: int
    minimum_z_occurrences: int
    enumerated_templates: int
    accepted: tuple[CorridorRow, ...]
    aut_records: tuple[AutRecord, ...]
    trace_sha256: str

    @property
    def accepted_count(self) -> int:
        return len(self.accepted)

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
                "minimum_z_occurrences": self.minimum_z_occurrences,
            },
            "enumerated_templates": self.enumerated_templates,
            "accepted_count": self.accepted_count,
            "trace_sha256": self.trace_sha256,
            "accepted": [row.to_json() for row in self.accepted],
            "aut_records": [record.to_json() for record in self.aut_records],
            "minimum_output_floor": self.minimum_output_floor,
        }


def enumerate_short_corridors(
    pair: tuple[str, str],
    max_word_length: int = 4,
    max_template_length: int = 6,
) -> CorridorCensus:
    if len(pair) != 2:
        raise ValueError("corridors require exactly two relators")
    if max_word_length < 1:
        raise ValueError("max_word_length must be positive")
    if max_template_length < 2:
        raise ValueError("max_template_length must be at least two")
    for relator in pair:
        if any(letter not in WORD_ALPHABET for letter in relator):
            raise ValueError("input relators must use only x and y")

    words = tuple(_reduced_words(WORD_ALPHABET, 1, max_word_length))
    templates = {
        eliminated: tuple(
            template
            for template in _reduced_words(
                TEMPLATE_ALPHABET, 2, max_template_length, cyclic=True
            )
            if sum(
                letter.lower() == eliminated for letter in template
            )
            == 1
            and template.count("z") + template.count("Z") >= 2
        )
        for eliminated in "xy"
    }
    source_orientations = tuple(
        frozenset(cyclic_orientations(relator)) for relator in pair
    )
    trace = sha256()
    accepted: list[CorridorRow] = []
    enumerated = 0

    for source_index in (0, 1):
        orientations = source_orientations[source_index]
        for eliminated in "xy":
            for word in words:
                for template in templates[eliminated]:
                    substituted = substitute_z(template, word)
                    is_accepted = substituted in orientations
                    trace.update(
                        "\0".join(
                            (
                                str(source_index),
                                eliminated,
                                word,
                                template,
                                substituted,
                                "1" if is_accepted else "0",
                            )
                        ).encode("ascii")
                        + b"\n"
                    )
                    enumerated += 1
                    if not is_accepted:
                        continue
                    expression = solve_isolator(template, eliminated)
                    output = corridor_output(
                        pair, source_index, word, template, eliminated
                    )
                    accepted.append(
                        CorridorRow(
                            source_index=source_index,
                            source_orientation=substituted,
                            eliminated=eliminated,
                            word=word,
                            template=template,
                            substituted=substituted,
                            expression=expression,
                            output=output,
                        )
                    )

    canonical_outputs = sorted({canon(*row.output) for row in accepted})
    aut_records: list[AutRecord] = []
    for output in canonical_outputs:
        minimum_total, representative, phi = aut_canon(output)
        aut_records.append(
            AutRecord(
                output=output,
                minimum_total=minimum_total,
                representative=representative,
                phi=phi,
            )
        )
    return CorridorCensus(
        pair=tuple(pair),
        max_word_length=max_word_length,
        max_template_length=max_template_length,
        minimum_z_occurrences=2,
        enumerated_templates=enumerated,
        accepted=tuple(accepted),
        aut_records=tuple(aut_records),
        trace_sha256=trace.hexdigest(),
    )


def _validate_word(word: str) -> None:
    invalid = [letter for letter in word if letter not in VALID_LETTERS]
    if invalid:
        raise ValueError(f"invalid letters: {invalid!r}")


def _relabel_z(word: str, replacement: str) -> str:
    return free_reduce(
        "".join(
            replacement
            if letter == "z"
            else replacement.upper()
            if letter == "Z"
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
