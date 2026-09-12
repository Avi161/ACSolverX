"""Independent replay and serial bounded screen of primitive compression."""

from __future__ import annotations

import argparse
import ast
from collections import Counter
from copy import deepcopy
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
import primitive_compression as subject

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PROOF_ROOT = ROOT / ".claude/worktrees/codex-proofs"
LEGACY = PROOF_ROOT / "experiments/stable_ac/rank3_compression/rank3_whitehead.py"
THEOREM = PROOF_ROOT / "literature/proofs/AK3_PRIMITIVE_SINGLE.md"
OUTPUT = HERE / "primitive_compression_report.json"
MARKDOWN = HERE / "primitive_compression_report.md"
ALPHABET = "xXyYzZ"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def inverse(word):
    translations = {"x": "X", "X": "x", "y": "Y", "Y": "y", "z": "Z", "Z": "z"}
    return "".join(translations[c] for c in reversed(word))


def reduce_word(word):
    need(isinstance(word, str) and all(c in ALPHABET for c in word), "invalid free word")
    while True:
        previous = word
        for pair in ("xX", "Xx", "yY", "Yy", "zZ", "Zz"):
            word = word.replace(pair, "")
        if previous == word:
            return word


def apply(word, images):
    out = []
    for c in word:
        out.append(images[c.lower()] if c.islower() else inverse(images[c.lower()]))
    return reduce_word("".join(out))


def canonical(word):
    word = reduce_word(word)
    while len(word) > 1 and word[0] == inverse(word[-1]):
        word = word[1:-1]
    return min((base[i:] + base[:i] for base in (word, inverse(word))
                for i in range(len(base))), default="")


def verify_inverse(images, backwards):
    need(set(images) == set(backwards), "inverse map basis mismatch")
    for g in images:
        need(apply(images[g], backwards) == g and apply(backwards[g], images) == g,
             "map compositions are not both identity")


def verify_normalization(before, after, witnesses):
    need(len(before) == len(after) == len(witnesses), "tuple normalization cardinality")
    for word, result, witness in zip(before, after, witnesses):
        sign, conjugator = witness["sign"], witness["conjugator"]
        need(type(sign) is int and sign in (-1, 1), "invalid canonicalization sign")
        need(reduce_word(inverse(conjugator) + (word if sign == 1 else inverse(word)) + conjugator)
             == result == canonical(word), "canonicalization witness failed")


def legacy_inventory():
    source = LEGACY.read_text()
    tree = ast.parse(source)
    names = {"second_kind_automorphisms", "_validate_generators"}
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    namespace = {"lru_cache": lru_cache}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(LEGACY), "exec"), namespace)
    maps = namespace["second_kind_automorphisms"](("x", "y", "z"))
    need(len(maps) == 90, "legacy inventory does not have 90 maps")
    return maps


def check_boundary(boundary):
    words = boundary["relators"]
    need(boundary["rank"] == len(words), "boundary rank mismatch")
    need(all(reduce_word(w) == w for w in words), "unreduced boundary word")
    need(boundary["relator_lengths"] == list(map(len, words)), "boundary relator lengths")
    need(boundary["total_length"] == sum(map(len, words)), "boundary total excludes relator")


def verify_record(record, all_maps):
    pair, candidate = record["input"], record["candidate"]
    source, sign, conjugator = candidate["source"], candidate["source_sign"], candidate["source_conjugator"]
    need(type(source) is int and source in (0, 1), "source index")
    need(type(sign) is int and sign in (-1, 1), "source orientation sign")
    word = pair[source] if sign == 1 else inverse(pair[source])
    oriented = reduce_word(inverse(conjugator) + word + conjugator)
    need(oriented == candidate["oriented_source"], "source orientation witness")
    defining, isolator, companion = (candidate[k] for k in
                                      ("defining_word", "isolator", "companion_template"))
    need(2 <= len(defining) <= 6 and all(c in "xXyY" for c in defining), "defining word limits")
    counts = Counter(canonical(isolator).lower())
    need("z" in counts and all(n >= 2 for n in counts.values()), "literal isolator was not excluded")
    images = {"x": "x", "y": "y", "z": defining}
    need(apply(isolator, images) == oriented, "compressed isolator expansion")
    need(apply(companion, images) == pair[1-source], "compressed companion expansion")
    donor = reduce_word("Z" + defining)
    initial = [donor, isolator, companion]
    need(initial == record["initial_rank3"], "initial tuple")
    normalization = record["initial_normalization"]
    need(normalization["before"] == initial, "initial normalization source")
    verify_normalization(initial, normalization["after"], normalization["canonical_witnesses"])
    current = normalization["after"]
    expected_boundaries = [pair, [donor, oriented, pair[1-source]], initial, current]
    keys = {tuple(m[g] for g in "xyz") for m in all_maps}
    for step in record["whitehead_steps"]:
        need(step["before"] == current, "Whitehead chain mismatch")
        need(tuple(step["images"][g] for g in "xyz") in keys, "map outside full Type-II inventory")
        verify_inverse(step["images"], step["inverse_images"])
        raw = [apply(w, step["images"]) for w in current]
        need(raw == step["raw_image"], "whole tuple was not mapped")
        verify_normalization(raw, step["after"], step["canonical_witnesses"])
        need(len(step["after"][1]) < len(current[1]), "Whitehead step is not strict")
        current = step["after"]
        expected_boundaries.extend((raw, current))
    need(current == record["rank3_endpoint"], "rank3 endpoint")
    if record["status"] == "nonprimitive_whitehead_minimum":
        need(len(current[1]) > 1, "nonprimitive singleton")
        need(all(len(canonical(apply(current[1], images))) >= len(current[1]) for images in all_maps),
             "claimed minimum has a Whitehead descent")
    if "endpoint" in record:
        need(record["status"] == "primitive_with_replayed_rank2_macro_endpoint", "primitive status")
        need(len(current[1]) == 1, "primitive alone does not supply a singleton witness")
        deletion = record["deletion"]
        axis = current[1].lower()
        need(deletion["axis"] == axis and deletion["before"] == current, "deletion source")
        need(deletion["isolator_sign"] == (1 if current[1] == axis else -1), "singleton inversion")
        substitutions = {g: "" if g == axis else g for g in "xyz"}
        remaining = [apply(current[i], substitutions) for i in (0, 2)]
        need(remaining == deletion["surviving_words"], "not every surviving word was substituted")
        deleted = [remaining[0], axis, remaining[1]]
        need(deletion["after_substitution"] == deleted, "strict deletion tuple")
        survivors = [g for g in "xyz" if g != axis]
        relabel = dict(zip(survivors, "xy"))
        need(record["relabel"] == relabel, "remaining basis relabel")
        rank2 = [apply(w, relabel) for w in remaining]
        need(record["raw_rank2_endpoint"] == rank2, "rank2 quotient words")
        expected_boundaries.extend((deleted, rank2))
        descent = record["rank2_nielsen"]
        norm = descent["initial_normalization"]
        need(norm["before"] == rank2, "rank2 normalization source")
        verify_normalization(rank2, norm["after"], norm["canonical_witnesses"])
        current2 = norm["after"]
        for step in descent["steps"]:
            need(step["before"] == current2, "Nielsen chain mismatch")
            verify_inverse(step["images"], step["inverse_images"])
            raw = [apply(w, step["images"]) for w in current2]
            need(raw == step["raw_image"], "rank2 image mismatch")
            verify_normalization(raw, step["after"], step["canonical_witnesses"])
            need(sum(map(len, step["after"])) < sum(map(len, current2)), "Nielsen step is not strict")
            current2 = step["after"]
        need(current2 == descent["endpoint"] == record["endpoint"], "rank2 endpoint mismatch")
        need(sum(map(len, current2)) == record["endpoint_length"], "endpoint length")
        need(record["strict_length_gain"] == (sum(map(len, current2)) < sum(map(len, pair))), "gain flag")
    need([b["relators"] for b in record["boundaries"]] == expected_boundaries, "boundary stream incomplete")
    for boundary in record["boundaries"]:
        check_boundary(boundary)
    need(record["recorded_rank3_boundary_max_total_length"] == max(
        b["total_length"] for b in record["boundaries"] if b["rank"] == 3), "rank3 peak mismatch")
    charges = record["image_evaluation_counts"]
    rounds = len(record["whitehead_steps"]) + (record["status"] == "nonprimitive_whitehead_minimum")
    need(charges.get("rank3_candidate_images", 0) == 90 * rounds, "missing 90-map rounds")
    need(charges.get("selected_whole_rank3_images", 0) == 3 * len(record["whitehead_steps"]), "whole tuple charge")
    if "rank2_nielsen" in record:
        descent = record["rank2_nielsen"]
        rounds2 = len(descent["steps"]) + (descent["stop"] == "no_strict_nielsen_descent")
        need(charges.get("rank2_candidate_images", 0) == 16 * rounds2, "rank2 image charge")
    need(sum(charges.values()) == record["image_evaluations"] <= 1000, "attempt image accounting")
    return True


def verify_row(row, all_maps):
    need(row["name"] != "aca_115", "AK3 was not excluded")
    need(row["image_evaluations"] <= row["image_limit"] <= 1000, "row image budget")
    need(sum(a["image_evaluations"] for a in row["attempts"]) == row["image_evaluations"], "shared candidate budget")
    need(sum(row["image_evaluation_counts"].values()) == row["image_evaluations"], "row counts")
    for record in row["attempts"]:
        need(record["input"] == row["input"], "attempt input differs")
        verify_record(record, all_maps)
    endpoints = [a for a in row["attempts"] if "endpoint" in a]
    need(len(endpoints) == row["primitive_candidates"], "primitive count")
    best = min(endpoints, key=lambda a: (a["endpoint_length"], a["endpoint"])) if endpoints else None
    need(row["best_endpoint"] == (best["endpoint"] if best else None), "row best endpoint")
    need(row["strict_length_gain"] == bool(best and best["strict_length_gain"]), "row gain")
    return True


def planted_checks(all_maps):
    counts = Counter()
    need({tuple(m[g] for g in "xyz") for m in subject.whitehead_maps()}
         == {tuple(m[g] for g in "xyz") for m in all_maps}, "legacy map inventory differs")
    for images in subject.whitehead_maps():
        verify_inverse(images, subject.map_inverses()[tuple(images[g] for g in "xyz")])
        counts["rank3_maps_with_both_inverse_compositions"] += 1
    examples = []
    for defining, isolator, companion in (("yy", "zxzxx", "xy"),
                                          ("YY", "zxzxx", "xY"),
                                          ("yy", "XXZXZ", "xy"),
                                          ("YY", "XXZXZ", "xY")):
        expansion = {"x": "x", "y": "y", "z": defining}
        source = apply(isolator, expansion)
        # The companion sets y=x^-1 (or y=x), after which the source is x^±1.
        y_image = "X" if companion == "xy" else "x"
        need(apply(source, {"x": "x", "y": y_image}) in ("x", "X"), "planted triviality proof")
        candidate = {"source": 0, "source_sign": 1, "source_conjugator": "",
                     "oriented_source": source, "defining_word": defining,
                     "isolator": isolator, "companion_template": companion}
        record = subject.compile_candidate([source, companion], candidate, subject.Meter())
        verify_record(record, all_maps)
        need("endpoint" in record and record["strict_length_gain"], "planted compression did not reduce length")
        examples.append(record)
        counts["independently_replayed_planted_primitive_macros"] += 1
    for budget in (0, 1, 89, 90, 92, 93, 185, 186, 278, 279, 999, 1000):
        record = subject.compile_candidate(examples[0]["input"], examples[0]["candidate"], subject.Meter(budget))
        verify_record(record, all_maps)
        need(record["image_evaluations"] <= budget, "planted budget overflow")
        counts["image_budget_boundaries"] += 1
    literal = deepcopy(examples[0]["candidate"])
    literal["isolator"] = "zx"
    for invalid in (literal, dict(examples[0]["candidate"], source_sign=0),
                    dict(examples[0]["candidate"], companion_template="x")):
        try:
            subject.compile_candidate(examples[0]["input"], invalid, subject.Meter())
        except ValueError:
            counts["invalid_candidate_rejection"] += 1
        else:
            raise ValueError("invalid candidate was accepted")
    corruptions = []
    broken = deepcopy(examples[0]); broken["whitehead_steps"][0]["raw_image"][0] += "x"; corruptions.append(broken)
    broken = deepcopy(examples[0]); broken["whitehead_steps"][0]["inverse_images"]["x"] += "x"; corruptions.append(broken)
    broken = deepcopy(examples[0]); broken["deletion"]["surviving_words"][0] += "x"; corruptions.append(broken)
    broken = deepcopy(examples[0]); broken["boundaries"][1]["total_length"] -= 1; corruptions.append(broken)
    broken = deepcopy(examples[0]); broken["endpoint_length"] -= 1; corruptions.append(broken)
    for broken in corruptions:
        try:
            verify_record(broken, all_maps)
        except ValueError:
            counts["corrupt_macro_rejection"] += 1
        else:
            raise ValueError("corrupt macro was accepted")
    return {"status": "pass", "counts": dict(counts), "examples": examples,
            "planted_triviality_proof": "The companion xy (respectively xY) sets y=x^-1 (respectively x). Substitution into the source relator freely reduces to x or X, so the input group is trivial."}


def source_hashes():
    paths = [HERE / "primitive_compression.py", HERE / "primitive_compression_checks.py",
             HERE / "coupled_power_word_compression.py", HERE / "u124_inventory.json", LEGACY, THEOREM,
             HERE / "STABLE_CERTIFICATE_CONVENTIONS.md"]
    return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def write_report(report):
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n")
    rows = report["rows"]
    lines = ["# Primitive-single compressed-relator screen", "",
             f"Status: **{report['status']}**; {len(rows)}/{len(report['selected_ids'])} fixed panel rows evaluated.", "",
             "This applies the known primitive-single-relator removal theorem. It is not a new theorem or an ordinary expanded certificate. The source presentations are known trivial-group Miller–Schupp representatives; triviality is a hypothesis of the stable defining-word and ambient-map realizations.", "",
             "A candidate has D=Z w and exact templates I[z=w]=oriented R, C[z=w]=S. Every generator appearing in cyclically reduced I must occur at least twice; z must appear and the abelian exponent gcd must be one. Thus the existing literal single-occurrence isolator is excluded. Defining words are literal cyclic substrings of length2..6. Each decomposition call retains at most64 templates; two shortest companion templates are kept, then64 shortest distinct candidate combinations per row.", "",
             "Each complete descent round tests all90 rank3 Type-II Whitehead maps against I. The chosen invertible map acts on all three relators, followed by explicit individual conjugation/inversion witnesses. A singleton I is normalized to its positive generator, that generator is set to1 in both remaining words, and the pair is relabelled to x,y and strictly Nielsen-reduced. Primitivity alone is never labelled a gain.", "",
             "Every stored rank3 boundary counts all three relators, including D. The reported maximum is only the maximum over these recorded boundaries. A theorem-backed stable realization of an ambient rank3 map may briefly use rank4; its internal ordinary states and maximum length have not been expanded or bounded.", "",
             "The shared budget is1000 word-image evaluations per input, including all rank3 candidate images, chosen whole-tuple images, and rank2 Nielsen candidate images. Candidate template generation and independent replay are timed separately from these work counts. No heap, search campaign, JIT, or AK3 rerun is used.", "",
             f"Planted checks: {json.dumps(report['planted']['counts'], sort_keys=True)}.", "",
             f"Panel CPU time (candidate generation and independent replay included): {report['panel_cpu_seconds']:.6f}s. Serial cooldown:0.1s after each new row.", "",
             "| Input | Eligible candidates | Tried | Primitive endpoints | Images | Input L | Best endpoint L | Gain |",
             "|---|---:|---:|---:|---:|---:|---:|---|"]
    for row in rows:
        lines.append(f"| {row['name']} | {row['candidate_generation']['distinct_eligible_candidates']} | {len(row['attempts'])} | {row['primitive_candidates']} | {row['image_evaluations']} | {row['input_length']} | {row['best_endpoint_length']} | {row['strict_length_gain']} |")
    gains = [r for r in rows if r["strict_length_gain"]]
    lines += ["", f"Strict endpoint gains: {len(gains)}/{len(rows)} evaluated rows. Primitive endpoint occurrences: {sum(r['primitive_candidates'] for r in rows)}. Every stored attempt and endpoint passed the independent string-rewrite verifier.", "",
              "The JSON contains full map inverses, whole tuples, source orientations, exact compression substitutions, canonicalization witnesses, deletion/relabel witnesses, rank2 descent, all boundary lengths, per-candidate charges and source hashes. A null result concerns only these finite templates and the declared shared budget.", "",
              "Known theorem source: `codex-proofs/literature/proofs/AK3_PRIMITIVE_SINGLE.md`. The prior AK3 negative census was read for scope and was not rerun.", ""]
    MARKDOWN.write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit-rows", type=int, default=19)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--cpu-limit", type=float, default=10.0)
    args = parser.parse_args()
    need(0 <= args.limit_rows <= 19 and args.cpu_limit > 0, "invalid screen limit")
    all_maps = legacy_inventory()
    hashes = source_hashes()
    inventory = json.loads((HERE / "u124_inventory.json").read_text())
    panel = [r for r in inventory["panel"]["rows"] if r["name"] != "aca_115"]
    need(len(panel) == 19 and len({r["name"] for r in panel}) == 19, "fixed panel cardinality")
    if args.resume:
        report = json.loads(OUTPUT.read_text())
        need(report["source_sha256"] == hashes, "source changed since partial screen")
        need(report["selected_ids"] == [r["name"] for r in panel], "panel changed since partial screen")
        for row in report["rows"]:
            verify_row(row, all_maps)
    else:
        start = time.process_time()
        planted = planted_checks(all_maps)
        report = {"status": "partial", "certificate_kind": "theorem_backed_stable_macro_not_ordinary_expanded",
                  "source_sha256": hashes, "selected_ids": [r["name"] for r in panel],
                  "selection": "Original fixed20 inventory panel minus aca_115 (AK3), with no replacement.",
                  "limits": {"images_per_input": 1000, "max_defining_length": 6,
                             "decompositions_per_word": 64, "shortest_companion_templates": 2,
                             "retained_candidate_combinations": 64, "cooldown_seconds": 0.1},
                  "planted": planted, "planted_cpu_seconds": time.process_time() - start,
                  "panel_cpu_seconds": 0.0, "rows": []}
        write_report(report)
    complete = {r["name"] for r in report["rows"]}
    count = 0
    for row in panel:
        if row["name"] in complete:
            continue
        if count >= args.limit_rows or report["panel_cpu_seconds"] >= args.cpu_limit:
            break
        start = time.process_time()
        result = subject.row_probe(row)
        verify_row(result, all_maps)
        result["independent_macro_replay"] = "pass"
        result["total_cpu_seconds_with_independent_replay"] = time.process_time() - start
        report["panel_cpu_seconds"] += result["total_cpu_seconds_with_independent_replay"]
        report["rows"].append(result)
        count += 1
        write_report(report)
        print(json.dumps({k: result[k] for k in ("name", "image_evaluations", "primitive_candidates", "best_endpoint_length", "strict_length_gain", "total_cpu_seconds_with_independent_replay")}), flush=True)
        time.sleep(0.1)
    report["status"] = "pass" if len(report["rows"]) == len(panel) else "partial"
    report["stop_reason"] = ("complete_fixed_panel" if report["status"] == "pass" else
                             "cpu_limit" if report["panel_cpu_seconds"] >= args.cpu_limit else "row_limit")
    report["python_optimization"] = sys.flags.optimize
    write_report(report)
    print(json.dumps({"status": report["status"], "rows": len(report["rows"]),
                      "panel_cpu_seconds": report["panel_cpu_seconds"],
                      "gains": [r["name"] for r in report["rows"] if r["strict_length_gain"]]}))


if __name__ == "__main__":
    main()
