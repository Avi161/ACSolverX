"""Acyclic multi-elimination corridors built from Lemma 11 stages."""

from __future__ import annotations

from dataclasses import dataclass

from experiments.stable_ac.supermoves.certified_acm import (
    cyclic_key,
    free_reduce,
    inverse,
)


@dataclass(frozen=True)
class AMECStage:
    fresh_generator: str
    defining_word: str
    compressed_relators: tuple[str, ...]
    eliminated_generator: str
    isolator_index: int


@dataclass(frozen=True)
class AMECStageReplay:
    source: tuple[str, ...]
    definition: str
    compressed: tuple[str, ...]
    displayed_substitution_count: int
    isolator: str
    expression: str
    output: tuple[str, ...]


@dataclass(frozen=True)
class AMECReplay:
    source: tuple[str, ...]
    source_generators: tuple[str, ...]
    triviality_provenance: str
    stages: tuple[AMECStageReplay, ...]
    final_generators: tuple[str, ...]
    displayed_substitution_count: int
    target_before_relabel: tuple[str, ...]
    target: tuple[str, ...]


def replay_amec(
    source: tuple[str, ...],
    stages: tuple[AMECStage, ...],
    *,
    generators: tuple[str, ...],
    triviality_provenance: str,
    relabel: dict[str, str] | None = None,
) -> AMECReplay:
    """Verify and replay a dynamically acyclic Lemma-11 corridor.

    Each stage adds one fresh defining relator by inverse Lemma 11, verifies a
    mechanically derivable compression certificate by re-expansion, and
    removes one old generator using an isolator that exists after all earlier
    stage substitutions.
    """

    if not triviality_provenance.strip():
        raise ValueError("trusted triviality provenance is required")
    _validate_basis(generators)
    if len(source) != len(generators):
        raise ValueError("AMEC requires a balanced relator tuple")
    current_generators = list(generators)
    source_alphabet = {letter.lower() for word in source for letter in word}
    if not source_alphabet.issubset(current_generators):
        raise ValueError("source relator uses an undeclared generator")
    current = tuple(free_reduce(word) for word in source)
    replays: list[AMECStageReplay] = []
    for stage in stages:
        _validate_generator(stage.fresh_generator)
        _validate_generator(stage.eliminated_generator)
        if stage.fresh_generator in current_generators:
            raise ValueError("fresh generator already occurs in the state")
        if stage.eliminated_generator not in current_generators:
            raise ValueError("eliminated generator is not currently declared")
        defining_alphabet = {
            letter.lower() for letter in stage.defining_word
        }
        if not defining_alphabet.issubset(current_generators):
            raise ValueError("defining word uses an undeclared generator")
        if len(stage.compressed_relators) != len(current):
            raise ValueError("compressed relator count must match the state")

        compressed = tuple(
            free_reduce(word) for word in stage.compressed_relators
        )
        augmented_generators = set(current_generators) | {
            stage.fresh_generator
        }
        compressed_alphabet = {
            letter.lower() for word in compressed for letter in word
        }
        if not compressed_alphabet.issubset(augmented_generators):
            raise ValueError("compressed relator uses an undeclared generator")
        for old, new in zip(current, compressed):
            expanded = substitute_generator(
                new,
                stage.fresh_generator,
                stage.defining_word,
            )
            if cyclic_key(expanded) != cyclic_key(old):
                raise ValueError(
                    f"compressed relator {new!r} does not expand to {old!r}"
                )

        definition = stage.fresh_generator.upper() + stage.defining_word
        augmented = compressed + (free_reduce(definition),)
        if not 0 <= stage.isolator_index < len(augmented):
            raise ValueError("isolator index out of range")
        isolator = augmented[stage.isolator_index]
        expression = solve_isolator(
            isolator,
            stage.eliminated_generator,
        )
        output = tuple(
            substitute_generator(
                relator,
                stage.eliminated_generator,
                expression,
            )
            for index, relator in enumerate(augmented)
            if index != stage.isolator_index
        )
        if any(
            letter.lower() == stage.eliminated_generator
            for word in output
            for letter in word
        ):
            raise AssertionError("eliminated generator survived substitution")
        replays.append(
            AMECStageReplay(
                source=current,
                definition=definition,
                compressed=compressed,
                displayed_substitution_count=sum(
                    letter.lower() == stage.fresh_generator
                    for word in compressed
                    for letter in word
                ),
                isolator=isolator,
                expression=expression,
                output=output,
            )
        )
        current = output
        current_generators.append(stage.fresh_generator)
        current_generators.remove(stage.eliminated_generator)

    target_before_relabel = current
    if relabel is not None:
        _validate_signed_basis_relabel(relabel, tuple(current_generators))
        target = tuple(apply_homomorphism(word, relabel) for word in current)
    else:
        target = current
    return AMECReplay(
        source=tuple(source),
        source_generators=tuple(generators),
        triviality_provenance=triviality_provenance,
        stages=tuple(replays),
        final_generators=tuple(current_generators),
        displayed_substitution_count=sum(
            stage.displayed_substitution_count for stage in replays
        ),
        target_before_relabel=target_before_relabel,
        target=target,
    )


def solve_isolator(word: str, generator: str) -> str:
    _validate_generator(generator)
    word = free_reduce(word)
    positions = [
        index
        for index, letter in enumerate(word)
        if letter.lower() == generator
    ]
    if len(positions) != 1:
        raise ValueError(
            f"isolator must contain exactly one {generator}; found {len(positions)}"
        )
    index = positions[0]
    rotated = word[index:] + word[:index]
    suffix = rotated[1:]
    if rotated[0] == generator:
        return free_reduce(inverse(suffix))
    return free_reduce(suffix)


def substitute_generator(word: str, generator: str, image: str) -> str:
    _validate_generator(generator)
    image = free_reduce(image)
    image_inverse = inverse(image)
    return free_reduce(
        "".join(
            image
            if letter == generator
            else image_inverse
            if letter == generator.upper()
            else letter
            for letter in word
        )
    )


def apply_homomorphism(word: str, images: dict[str, str]) -> str:
    for generator in images:
        _validate_generator(generator)
    normalized = {
        generator: free_reduce(image) for generator, image in images.items()
    }
    return free_reduce(
        "".join(
            normalized[letter]
            if letter in normalized
            else inverse(normalized[letter.lower()])
            if letter.isupper() and letter.lower() in normalized
            else letter
            for letter in word
        )
    )


def aca120_replay() -> AMECReplay:
    return replay_amec(
        ("YXXXYxx", "YYYYXyyyx"),
        (
            AMECStage(
                fresh_generator="z",
                defining_word="xy",
                compressed_relators=("ZXXYxx", "YYYZyyyx"),
                eliminated_generator="x",
                isolator_index=1,
            ),
            AMECStage(
                fresh_generator="t",
                defining_word="yyy",
                compressed_relators=("ZTZZYzzt", "ZTzty"),
                eliminated_generator="y",
                isolator_index=0,
            ),
        ),
        generators=("x", "y"),
        triviality_provenance="aca_124.csv:aca_120",
        relabel={"z": "x", "t": "y"},
    )


def _validate_generator(generator: str) -> None:
    if len(generator) != 1 or not generator.isalpha() or not generator.islower():
        raise ValueError("generator must be one lowercase letter")


def _validate_basis(generators: tuple[str, ...]) -> None:
    for generator in generators:
        _validate_generator(generator)
    if len(set(generators)) != len(generators):
        raise ValueError("declared generators must be distinct")


def _validate_signed_basis_relabel(
    relabel: dict[str, str], final_generators: tuple[str, ...]
) -> None:
    if set(relabel) != set(final_generators):
        raise ValueError("relabel must cover the final declared basis exactly")
    images = tuple(relabel[generator] for generator in final_generators)
    if any(len(image) != 1 or not image.isalpha() for image in images):
        raise ValueError("relabel images must be signed basis letters")
    if len({image.lower() for image in images}) != len(images):
        raise ValueError("relabel images must be a bijective signed permutation")
