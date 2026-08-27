"""Independent replay of the two strict mini-benchmark reduction hits."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / ".claude/worktrees/codex-proofs"
sys.path.insert(0, str(ROOT))

import experiments.equivalence_classes  # noqa: E402
import experiments.equivalence_classes.lib  # noqa: E402
import experiments.search  # noqa: E402
import experiments.stable_ac  # noqa: E402

for package, relative in (
    (experiments.equivalence_classes, "experiments/equivalence_classes"),
    (experiments.equivalence_classes.lib, "experiments/equivalence_classes/lib"),
    (experiments.search, "experiments/search"),
    (experiments.stable_ac, "experiments/stable_ac"),
):
    path = str(PROOF / relative)
    if path not in package.__path__:
        package.__path__.append(path)

from experiments.equivalence_classes.lib.acmoves import canon  # noqa: E402
from experiments.equivalence_classes.lib.autcanon import aut_canon  # noqa: E402
from experiments.stable_ac.rank3_compression.one_edge import cyclic_reduce  # noqa: E402
from experiments.stable_ac.rank3_compression.rank3_whitehead import (  # noqa: E402
    apply_automorphism,
    check_word_reduction,
    reduce_word,
)
from experiments.stable_ac.solvern import moves_to_states, str_to_word, word_to_str  # noqa: E402
from experiments.stable_ac.supermoves.morse_internal_collapse import replay  # noqa: E402


def free_reduce(word: str) -> str:
    stack = []
    for letter in word:
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def independent_quotient(words, relator_index, phi):
    transformed = tuple(cyclic_reduce(apply_automorphism(word, phi)) for word in words)
    isolator = transformed[relator_index]
    assert len(isolator) == 1
    eliminated = isolator.lower()
    survivors = tuple(generator for generator in "xyz" if generator != eliminated)
    rename = {
        survivors[0]: "x", survivors[0].upper(): "X",
        survivors[1]: "y", survivors[1].upper(): "Y",
    }
    quotient = []
    for index, word in enumerate(transformed):
        if index == relator_index:
            continue
        killed = free_reduce("".join(
            letter for letter in word if letter.lower() != eliminated
        ))
        quotient.append(free_reduce("".join(rename[letter] for letter in killed)))
    return canon(*quotient)


def replay_words(start, moves):
    states = moves_to_states(tuple(str_to_word(word) for word in start), moves, True)
    return [[word_to_str(word) for word in state] for state in states]


def main():
    path = ROOT / "results/stable_ac/morse_mini_greedy_targeted_60.json"
    payload = json.loads(path.read_text())
    hits = {"bench60_327": (15, 13), "bench60_580": (21, 17)}
    rows = {row["name"]: row for row in payload["groups"]["benchmark60"]}
    for name, (direct_total, guided_total) in hits.items():
        row = rows[name]
        assert row["direct"]["minimum_total"] == direct_total
        assert row["guided_best_rank2_total"] == guided_total
        assert row["guided_nodes"] <= row["budget"] == 60
        source_floor, source_rep, _ = aut_canon(tuple(row["source"]))
        assert source_floor == direct_total
        witnessed_floor_descent = False
        for branch in row["rank3"]:
            matching = tuple(tuple(edge) for edge in branch["matching"])
            morse = replay(tuple(row["source"]), matching)
            assert list(morse.endpoint_words) == list(branch["endpoint"])
        for exit_row in row["destabilized"]:
            witness = exit_row["witness"]
            assert replay_words(
                witness["rank3_path"][0], witness["rank3_moves"]
            ) == witness["rank3_path"]
            word = witness["primitive_word"]
            reduction = reduce_word(word, ("x", "y", "z"))
            check_word_reduction(word, reduction)
            assert reduction.minimum_total == 1
            assert reduction.phi == witness["primitive_phi"]
            output = independent_quotient(
                tuple(witness["rank3_state"]),
                witness["primitive_relator_index"],
                reduction.phi,
            )
            assert list(output) == witness["eliminated_output"]
            rank2 = exit_row["rank2_search"]
            assert replay_words(output, rank2["minimum_moves"]) == rank2["minimum_path"]
            assert sum(map(len, rank2["minimum"])) == rank2["minimum_total"]
            minimum_floor, minimum_rep, _ = aut_canon(tuple(rank2["minimum"]))
            if minimum_floor == guided_total:
                assert minimum_rep != source_rep
                witnessed_floor_descent = True
        assert witnessed_floor_descent
        print(f"verified {name}: direct {direct_total}, Morse channel {guided_total}")


if __name__ == "__main__":
    main()
