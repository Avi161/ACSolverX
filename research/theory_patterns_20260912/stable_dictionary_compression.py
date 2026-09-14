"""One defining generator for repeated literal words, with exact stable witnesses."""

import csv
from functools import lru_cache
import json
from pathlib import Path
import time

from .ac_words import inv, red
from .check_complement import sha256

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def tokenize(word, defining):
    inverse = inv(defining)
    best = [None] * (len(word) + 1)
    best[-1] = ""
    for position in range(len(word) - 1, -1, -1):
        choices = [word[position] + best[position + 1]]
        for block, token in ((defining, "z"), (inverse, "Z")):
            if word.startswith(block, position):
                choices.append(token + best[position + len(block)])
        best[position] = min(choices, key=lambda w: (len(w), w))
    return best[0]


@lru_cache(maxsize=65536)
def cyclic_compression(word, defining):
    candidates = []
    for cut in range(max(1, len(word))):
        oriented = word[cut:] + word[:cut]
        compressed = tokenize(oriented, defining)
        candidates.append((len(compressed), compressed, cut))
    _, compressed, cut = min(candidates)
    return compressed, cut


def independent_expand(word, defining):
    values = {"x": 1, "X": -1, "y": 2, "Y": -2}
    block = [values[c] for c in defining]
    stack = []
    for letter in word:
        part = block if letter == "z" else [-v for v in reversed(block)] if letter == "Z" else [values[letter]]
        for value in part:
            if stack and stack[-1] == -value:
                stack.pop()
            else:
                stack.append(value)
    alphabet = {v: k for k, v in values.items()}
    return "".join(alphabet[v] for v in stack)


def verify(input_pair, witness):
    defining = witness["defining_word"]
    if not defining or red(defining) != defining:
        raise ValueError("definition must be a nonempty reduced old word")
    compressed = witness["compressed_relators"]
    if len(compressed) != 2 or len(witness["cuts"]) != 2:
        raise ValueError("two source relators required")
    for original, word, cut in zip(input_pair, compressed, witness["cuts"]):
        if type(cut) is not int or not 0 <= cut < max(1, len(original)):
            raise ValueError("invalid cyclic cut")
        if independent_expand(word, defining) != original[cut:] + original[:cut]:
            raise ValueError("compressed expansion differs from rotated input")
    expected = ["Z" + defining, *compressed]
    if witness["relators"] != expected:
        raise ValueError("all three relators, including the definition, must be retained")
    if witness["rank"] != 3 or witness["total_length"] != sum(map(len, expected)):
        raise ValueError("rank or total length mismatch")
    if any(w[i] == inv(w[i + 1]) for w in expected for i in range(len(w) - 1)):
        raise ValueError("recorded stable tuple is not freely reduced")
    return True


def compress(pair):
    pair = tuple(pair)
    if len(pair) != 2 or any(red(word) != word for word in pair):
        raise ValueError("expected two reduced old relators")
    total = sum(map(len, pair))
    defining_words = set()
    for word in pair:
        for length in range(2, min(len(word), total // 2) + 1):
            doubled = word + word
            for cut in range(len(word)):
                candidate = doubled[cut:cut + length]
                if red(candidate) == candidate:
                    defining_words.add(min(candidate, inv(candidate)))
    best = None
    for defining in sorted(defining_words, key=lambda w: (len(w), w)):
        first, cut1 = cyclic_compression(pair[0], defining)
        second, cut2 = cyclic_compression(pair[1], defining)
        new_total = len(defining) + 1 + len(first) + len(second)
        if new_total >= total or best is not None and new_total >= best["total_length"]:
            continue
        witness = {"defining_word": defining, "cuts": [cut1, cut2],
                   "compressed_relators": [first, second], "relators": ["Z" + defining, first, second],
                   "rank": 3, "total_length": new_total,
                   "certificate_kind": "theorem_backed_stable_definition_and_literal_compression"}
        verify(pair, witness)
        best = witness
    return {"candidate_definitions": len(defining_words), "best": best,
            "best_length_including_start": best["total_length"] if best else total}


def checks():
    positive = ("xxxxxxxxxxy", "x")
    result = compress(positive)
    assert result["best"] and result["best"]["total_length"] < sum(map(len, positive))
    assert verify(positive, result["best"])
    damaged = dict(result["best"], total_length=result["best"]["total_length"] - 1)
    try:
        verify(positive, damaged)
    except ValueError:
        pass
    else:
        raise AssertionError("length corruption accepted")
    assert compress(("x", "y"))["best"] is None


def main():
    checks()
    path = ROOT / "data/ms_unsolved_reps/aca_124_best.csv"
    start_cpu, start_wall = time.process_time(), time.perf_counter()
    rows = []
    for row in csv.DictReader(path.open()):
        pair = [row["r1"], row["r2"]]
        result = compress(pair)
        rows.append({"name": row["name"], "input": pair, "input_length": sum(map(len, pair)), **result})
        time.sleep(.05)
    report = {"status": "all124_stable_prefixes_author_verified_pending_independent_audit",
              "source_sha256": sha256(path), "script_sha256": sha256(Path(__file__)), "rows": rows,
              "strict_stable_gain_ids": [r["name"] for r in rows if r["best"]],
              "rank2_gain_ids": [], "solved_ids": [],
              "starting_total": sum(r["input_length"] for r in rows),
              "best_total_including_start": sum(r["best_length_including_start"] for r in rows),
              "candidate_definitions": sum(r["candidate_definitions"] for r in rows),
              "maximum_candidate_definitions_per_input": max(r["candidate_definitions"] for r in rows),
              "cpu_seconds": time.process_time() - start_cpu,
              "wall_seconds_including_cooling": time.perf_counter() - start_wall,
              "scope": "One fresh generator z for one old literal word w, all cyclic cuts and shortest disjoint w/w^-1 tokenizations; length<=floor(inputtotal/2), since a longer definingword cannot occur twice and yield a strict token-count gain. No heap search. No claim of optimality under general stable AC or hidden-cancellation compression.",
              "proof": "STABLE_CERTIFICATE_CONVENTIONS.md; known Miller-Schupp triviality guarantees finite normal-product realization of addingZ*w. Then exact ordinary donor-restored substitutions compress each displayed block. No normal-product expansion emitted; all three relators retained."}
    (HERE / "stable_dictionary_compression_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()
