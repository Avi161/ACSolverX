"""Time-boxed Morse -> rank-3 search -> primitive destabilization benchmark."""

from __future__ import annotations

import argparse
import csv
import hashlib
import heapq
import json
import sys
import time
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / ".claude/worktrees/codex-proofs"
sys.path.insert(0, str(ROOT))

import experiments.equivalence_classes  # noqa: E402
import experiments.equivalence_classes.lib  # noqa: E402
import experiments.search  # noqa: E402
import experiments.stable_ac  # noqa: E402

proof_equivalence = str(PROOF / "experiments/equivalence_classes")
proof_equivalence_lib = str(PROOF / "experiments/equivalence_classes/lib")
proof_search = str(PROOF / "experiments/search")
proof_stable = str(PROOF / "experiments/stable_ac")
if proof_equivalence not in experiments.equivalence_classes.__path__:
    experiments.equivalence_classes.__path__.append(proof_equivalence)
if proof_equivalence_lib not in experiments.equivalence_classes.lib.__path__:
    experiments.equivalence_classes.lib.__path__.append(proof_equivalence_lib)
if proof_search not in experiments.search.__path__:
    experiments.search.__path__.append(proof_search)
if proof_stable not in experiments.stable_ac.__path__:
    experiments.stable_ac.__path__.append(proof_stable)

from experiments.equivalence_classes.lib.acmoves import canon  # noqa: E402
from experiments.stable_ac.rank3_compression.one_edge import cyclic_reduce  # noqa: E402
from experiments.stable_ac.rank3_compression.rank3_whitehead import (  # noqa: E402
    apply_automorphism,
    check_word_reduction,
    is_primitive_word,
    reduce_word,
    reduce_word_fast,
)
from experiments.stable_ac.solvern import (  # noqa: E402
    Pres,
    canonical_presentation,
    move_to_str,
    str_to_word,
    word_to_str,
)
from experiments.stable_ac.solvern_fast import (  # noqa: E402
    _pack_key,
    _solved,
    _unpack_key,
    _unpack_state_nj,
    expand_node_packed_nj,
)
from experiments.stable_ac.supermoves.morse_internal_collapse import (  # noqa: E402
    critical_cells,
    presentation_poset,
    replay,
    sample_target_rank_matching,
)


GENERATORS3 = ("x", "y", "z")


def inverse(word: str) -> str:
    return word[::-1].swapcase()


def free_reduce(word: str) -> str:
    stack: list[str] = []
    for letter in word:
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def reconstruct(parents: dict[bytes, tuple[bytes, tuple[int, ...]] | None], key: bytes):
    moves = []
    states = []
    while key is not None:
        states.append(tuple(word_to_str(word) for word in _unpack_key(key)))
        entry = parents[key]
        if entry is None:
            break
        key, move = entry
        moves.append(move_to_str(move))
    states.reverse()
    moves.reverse()
    return states, moves


def basis_solved(packed: bytes, rank: int) -> bool:
    if not _solved(packed, rank):
        return False
    words = _unpack_key(packed)
    return {abs(word[0]) for word in words} == set(range(1, rank + 1))


def expand_packed(packed: bytes, n_rel: int, cap: int):
    words, lens = _unpack_state_nj(np.frombuffer(packed, dtype=np.uint8), n_rel)
    rows, row_lens, totals, moves, count = expand_node_packed_nj(
        words, lens, n_rel, cap, True
    )
    for index in range(count):
        move = tuple(int(value) for value in moves[index])
        yield rows[index, : row_lens[index]].tobytes(), int(totals[index]), move


def bounded_search(words: tuple[str, ...], budget: int, cap: int) -> dict[str, object]:
    if max(map(len, words)) > cap:
        raise ValueError("search start exceeds the declared relator cap")
    relators = tuple(str_to_word(word) for word in words)
    start = canonical_presentation(relators, True)
    packed = _pack_key(start)
    total = sum(map(len, start))
    parents: dict[bytes, tuple[bytes, tuple[int, ...]] | None] = {packed: None}
    queue = [(total, 0, packed)]
    minimum = packed
    minimum_total = total
    solved = None
    nodes = 0
    while queue and nodes < budget:
        current_total, depth, current = heapq.heappop(queue)
        nodes += 1
        if basis_solved(current, len(words)):
            solved = current
            break
        for child, child_total, move in expand_packed(current, len(words), cap):
            if child in parents:
                continue
            parents[child] = (current, move)
            if child_total < minimum_total:
                minimum = child
                minimum_total = child_total
            heapq.heappush(queue, (child_total, depth + 1, child))
    min_states, min_moves = reconstruct(parents, minimum)
    solved_states, solved_moves = ([], []) if solved is None else reconstruct(parents, solved)
    return {
        "solved": solved is not None,
        "nodes": nodes,
        "minimum_total": minimum_total,
        "minimum": list(min_states[-1]),
        "minimum_path": min_states,
        "minimum_moves": min_moves,
        "solution_path": solved_states,
        "solution_moves": solved_moves,
    }


def destabilize(
    words: tuple[str, str, str], relator_index: int, reduction
) -> tuple[str, str]:
    transformed = tuple(
        cyclic_reduce(apply_automorphism(word, reduction.phi)) for word in words
    )
    isolator = transformed[relator_index]
    if len(isolator) != 1:
        raise AssertionError("primitive reduction did not produce one letter")
    eliminated = isolator.lower()
    survivors = tuple(generator for generator in GENERATORS3 if generator != eliminated)
    rename = {
        survivors[0]: "x",
        survivors[0].upper(): "X",
        survivors[1]: "y",
        survivors[1].upper(): "Y",
    }
    output = []
    for index, word in enumerate(transformed):
        if index == relator_index:
            continue
        quotient = free_reduce(
            "".join(letter for letter in word if letter.lower() != eliminated)
        )
        output.append(free_reduce("".join(rename[letter] for letter in quotient)))
    return canon(*output)


def rank3_search_for_exits(
    words: tuple[str, str, str], budget: int, cap: int, exit_limit: int = 4
) -> dict[str, object]:
    start = canonical_presentation(tuple(str_to_word(word) for word in words), True)
    packed = _pack_key(start)
    total = sum(map(len, start))
    parents: dict[bytes, tuple[bytes, tuple[int, ...]] | None] = {packed: None}
    queue = [(total, 0, packed)]
    reduction_cache = {}
    exits = {}
    solved = None
    nodes = 0
    while queue and nodes < budget:
        current_total, depth, current = heapq.heappop(queue)
        nodes += 1
        if basis_solved(current, 3):
            solved = current
            break
        current_words = tuple(word_to_str(word) for word in _unpack_key(current))
        for relator_index, word in enumerate(current_words):
            if not word:
                continue
            reduction = reduction_cache.get(word)
            if reduction is None:
                reduction = reduce_word_fast(word, GENERATORS3)
                reduction_cache[word] = reduction
            if not is_primitive_word(reduction):
                continue
            reduction = reduce_word(word, GENERATORS3)
            check_word_reduction(word, reduction)
            if not is_primitive_word(reduction):
                raise AssertionError("fast primitive screen disagrees with exact replay")
            output = destabilize(current_words, relator_index, reduction)
            if output in exits:
                continue
            states, moves = reconstruct(parents, current)
            exits[output] = {
                "rank3_state": list(current_words),
                "rank3_path": states,
                "rank3_moves": moves,
                "primitive_relator_index": relator_index,
                "primitive_word": word,
                "primitive_phi": dict(reduction.phi),
                "primitive_steps": [dict(step) for step in reduction.steps],
                "eliminated_output": list(output),
                "found_at_node": nodes,
            }
            if len(exits) >= exit_limit:
                break
        for child, child_total, move in expand_packed(current, 3, cap):
            if child in parents:
                continue
            parents[child] = (current, move)
            heapq.heappush(queue, (child_total, depth + 1, child))
    solution_states, solution_moves = ([], []) if solved is None else reconstruct(parents, solved)
    return {
        "solved": solved is not None,
        "nodes": nodes,
        "exits": list(exits.values()),
        "solution_path": solution_states,
        "solution_moves": solution_moves,
    }


def morse_rank3_samples(
    source: tuple[str, str], source_key: str, count: int, cap: int
):
    poset = presentation_poset(("x", "y"), source)
    outputs = []
    attempts = 0
    base = int(hashlib.sha256(source_key.encode()).hexdigest()[:12], 16)
    while len(outputs) < count and attempts < 12:
        seed = base + attempts
        attempts += 1
        matching = sample_target_rank_matching(poset, seed, 3)
        if matching is None:
            continue
        critical = critical_cells(poset, matching)
        result = replay(source, matching)
        if max(map(len, result.endpoint_words), default=0) > cap:
            continue
        endpoint = tuple(result.endpoint_words)
        if endpoint in {row["endpoint"] for row in outputs}:
            continue
        outputs.append(
            {
                "seed": seed,
                "matching": [list(edge) for edge in matching],
                "topological_order": list(result.topological_order),
                "critical_cells": [list(level) for level in result.critical_cells],
                "endpoint": endpoint,
            }
        )
    return outputs, attempts


def guided_trial(
    name: str,
    source: tuple[str, str],
    total_budget: int,
    rank3_budget: int,
    samples: int,
    cap: int,
) -> dict[str, object]:
    direct = bounded_search(source, total_budget, cap)
    stabilized = bounded_search((*source, "z"), total_budget, cap)
    morse, attempts = morse_rank3_samples(source, name, samples, cap)
    rank3_records = []
    exit_by_output = {}
    rank3_nodes = 0
    for row in morse:
        result = rank3_search_for_exits(row["endpoint"], rank3_budget, cap)
        rank3_nodes += int(result["nodes"])
        row = dict(row)
        row["search"] = result
        rank3_records.append(row)
        for exit_row in result["exits"]:
            output = tuple(exit_row["eliminated_output"])
            exit_by_output.setdefault(output, exit_row)
    remaining = max(0, total_budget - rank3_nodes)
    ranked_exits = sorted(exit_by_output.items(), key=lambda item: (sum(map(len, item[0])), item[0]))[:2]
    per_exit = remaining // len(ranked_exits) if ranked_exits else 0
    exit_records = []
    guided_solved = any(row["search"]["solved"] for row in rank3_records)
    best_minimum = None
    guided_nodes = rank3_nodes
    for output, witness in ranked_exits:
        search = bounded_search(output, per_exit, cap) if per_exit else None
        if search is not None:
            guided_nodes += int(search["nodes"])
            guided_solved = guided_solved or bool(search["solved"])
            best_minimum = (
                search["minimum_total"]
                if best_minimum is None
                else min(best_minimum, search["minimum_total"])
            )
        exit_records.append({"witness": witness, "rank2_search": search})
    return {
        "name": name,
        "source": list(source),
        "source_total": sum(map(len, source)),
        "budget": total_budget,
        "cap": cap,
        "direct": direct,
        "natural_stabilization": stabilized,
        "morse_attempts": attempts,
        "morse_rank3_count": len(morse),
        "rank3": rank3_records,
        "destabilized": exit_records,
        "guided_nodes": guided_nodes,
        "guided_solved": guided_solved,
        "guided_best_rank2_total": best_minimum,
    }


def load_inputs():
    subset_path = PROOF / "results/benchmark/subsets/benchmark_subset_60.json"
    subset = json.loads(subset_path.read_text())["subset"]
    bench = [(f"bench60_{row['pres_id']}", (row["r1"], row["r2"])) for row in subset]
    aca_path = PROOF / "data/ms_unsolved_reps/aca_124.csv"
    with aca_path.open(newline="") as handle:
        aca = [(row["name"], (row["r1"], row["r2"])) for row in csv.DictReader(handle)]
    return bench, aca


def summary(rows):
    return {
        "count": len(rows),
        "direct_solved": sum(bool(row["direct"]["solved"]) for row in rows),
        "guided_solved": sum(bool(row["guided_solved"]) for row in rows),
        "guided_only_solved": [
            row["name"] for row in rows
            if row["guided_solved"] and not row["direct"]["solved"]
        ],
        "direct_only_solved": [
            row["name"] for row in rows
            if row["direct"]["solved"] and not row["guided_solved"]
        ],
        "guided_beats_direct_minimum": [
            row["name"] for row in rows
            if row["guided_best_rank2_total"] is not None
            and row["guided_best_rank2_total"] < row["direct"]["minimum_total"]
        ],
        "guided_strict_source_descent": [
            row["name"] for row in rows
            if row["guided_best_rank2_total"] is not None
            and row["guided_best_rank2_total"] < row["source_total"]
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--minutes", type=float, default=12.0)
    parser.add_argument("--budget", type=int, default=120)
    parser.add_argument("--rank3-budget", type=int, default=20)
    parser.add_argument("--samples", type=int, default=2)
    parser.add_argument("--cap", type=int, default=32)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    # Compile the Numba expansion kernel before starting the experiment clock.
    bounded_search(("x", "y"), 1, args.cap)
    rank3_search_for_exits(("x", "y", "z"), 1, args.cap)
    bench, aca = load_inputs()
    started = time.monotonic()
    deadline = started + args.minutes * 60
    groups = {"benchmark60": [], "aca124": []}
    for group, inputs in (("benchmark60", bench), ("aca124", aca)):
        for index, (name, source) in enumerate(inputs, start=1):
            if time.monotonic() >= deadline:
                break
            before = time.monotonic()
            row = guided_trial(
                name, source, args.budget, args.rank3_budget, args.samples, args.cap
            )
            row["wall_seconds"] = time.monotonic() - before
            groups[group].append(row)
            print(
                f"{group} {index}/{len(inputs)} {name}: "
                f"direct={row['direct']['solved']} guided={row['guided_solved']} "
                f"mins={row['direct']['minimum_total']}/{row['guided_best_rank2_total']} "
                f"{row['wall_seconds']:.2f}s",
                flush=True,
            )
        if time.monotonic() >= deadline:
            break
    payload = {
        "schema": "mini-morse-greedy-v1",
        "parameters": {
            "minutes": args.minutes,
            "budget": args.budget,
            "rank3_budget_per_morse_sample": args.rank3_budget,
            "morse_samples": args.samples,
            "max_relator_length": args.cap,
            "budget_rule": "rank3 popped nodes plus rank2 popped nodes <= direct budget",
        },
        "wall_seconds": time.monotonic() - started,
        "groups": groups,
        "summary": {name: summary(rows) for name, rows in groups.items()},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload["summary"], indent=2), flush=True)


if __name__ == "__main__":
    main()
