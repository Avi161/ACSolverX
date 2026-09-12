"""Finite cyclic attachments, with a shared physical identification cap."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import time
from pathlib import Path

from . import ac_words, cyclic_complement
from .check_complement import ROSE, complement, independent_graph, inverse, reduce_word, sha256

HERE = Path(__file__).resolve().parent


def require(value, message):
    if not value:
        raise AssertionError(message)


def support(pair):
    return {c.lower() for word in pair for c in word}


def cyclically_reduced(word):
    return word == reduce_word(word) and bool(word) and word[0] != inverse(word[-1])


def short_path(word, cut):
    paths = (word[:cut], inverse(word[cut:]))
    return min(paths, key=lambda w: (len(w), w))


def attachments(pair):
    r, s = pair
    output, seen = [], set()
    for i, j in itertools.product(range(len(r)), range(len(s))):
        rotated = (r[i:] + r[:i], s[j:] + s[:j])
        if rotated in seen:
            continue
        seen.add(rotated)
        p, q = short_path(r, i), short_path(s, j)
        c = reduce_word(q + inverse(p))
        require(reduce_word(inverse(p) + r + p) == rotated[0], "R cyclic witness")
        require(reduce_word(inverse(q) + s + q) == rotated[1], "S cyclic witness")
        output.append({"cuts": [i, j], "pair": rotated, "p": p, "q": q, "conjugator": c})
    return sorted(output, key=lambda a: (len(a["conjugator"]), a["cuts"]))


def positive_witness(original, attachment, extra):
    r, s = original
    p, c = attachment["p"], attachment["conjugator"]
    w = reduce_word(p + extra + inverse(p))
    second = reduce_word(inverse(c) + s + c)
    prefix = [{"op": "conjugate", "target": 2, "by": letter} for letter in c]
    require(ac_words.replay(original, prefix) == [r, second], "AC3 prefix replay")
    joined = [r, second, w]
    require(independent_graph(joined) == ROSE == cyclic_complement.graph(joined), "full-rose witness")
    require(independent_graph([*attachment["pair"], extra]) == ROSE, "rotated full-rose witness")
    return {"claim": "stable_criterion_candidate_not_automatic_solve", "conjugator": c, "complement": w,
            "conjugated_pair": [r, second], "prefix_moves": prefix, "full_rose_checked_by_two_folders": True,
            "conjugator_length_bound": len(r) // 2 + len(s) // 2}


def screen(pair, budget, seeded_graph=None):
    require(all(cyclically_reduced(w) for w in pair), "requires nonempty cyclically reduced words")
    started_cpu, started_wall = time.process_time(), time.perf_counter()
    choices = attachments(pair)
    cache = {}
    if seeded_graph is not None:
        require(seeded_graph == independent_graph(pair), "seeded graph mismatch")
        cache[seeded_graph] = {"status": "no_cyclic_complement", "pairs_checked": 0, "complete": True,
                               "cache_source": "independently audited literal root"}
    records, checks, positive = [], 0, None
    for attachment in choices:
        if checks == budget:
            break
        graph = independent_graph(attachment["pair"])
        require(graph == cyclic_complement.graph(attachment["pair"]), "fold implementations disagree")
        reused = graph in cache
        if reused:
            result = {**cache[graph], "pairs_checked": 0}
        else:
            result = complement(graph, budget - checks, shortest_first=True)
            cache[graph] = result
        checks += result["pairs_checked"]
        require(checks <= budget, "physical identification budget")
        item = {**attachment, **result, "reused_exact_graph": reused,
                "graph_sha256": hashlib.sha256(json.dumps(graph).encode()).hexdigest()}
        records.append(item)
        if "complement" in result:
            positive = positive_witness(pair, attachment, result["complement"])
            break
    complete = positive is not None or (len(records) == len(choices) and all(r["complete"] for r in records))
    full_support = support(pair) == {"x", "y"}
    status = "stable_criterion_candidate" if positive else (
        "no_conjugated_cyclic_complement_by_finite_theorem" if complete and full_support else
        "no_complement_in_declared_attachments_outside_theorem_scope" if complete else "unknown_at_shared_cap")
    return {"input": list(pair), "status": status, "theorem_hypotheses": full_support,
            "attachment_count": len(choices), "tested_attachments": len(records), "pairs_checked": checks,
            "complete": complete, "positive": positive, "records": records,
            "cpu_seconds": time.process_time() - started_cpu, "wall_seconds": time.perf_counter() - started_wall}


def controls():
    cases = [("full_basis", ["x", "y"]), ("separate_powers", ["xx", "yyy"]),
             ("nonprimitive_positive", ["xyxY", "xxYYY"]),
             ("commutator_and_even_word", ["xyXY", "xxyy"]),
             ("shared_power_axis_outside_scope", ["xx", "xxx"]),
             ("shared_power_axis_negative_outside_scope", ["xx", "xxxx"]),
             ("AK2", ["xxYYY", "xyxYXY"])]
    rows = []
    conjugators = [""] + list("xXyY") + [a + b for a, b in itertools.product("xXyY", repeat=2) if a != inverse(b)]
    for name, pair in cases:
        row = {"name": name, **screen(pair, 1000)}
        direct = []
        if name != "AK2":
            for c in conjugators:
                words = [pair[0], reduce_word(inverse(c) + pair[1] + c)]
                result = complement(independent_graph(words), max_pairs=1000)
                require(result["complete"], "small direct control capped")
                if "complement" in result:
                    require(independent_graph([*words, result["complement"]]) == ROSE, "direct positive")
                    if row["theorem_hypotheses"] and row["complete"]:
                        require(row["positive"] is not None, "counterexample to finite criterion")
                direct.append({"conjugator": c, "status": result["status"], "pairs_checked": result["pairs_checked"]})
        row["direct_short_conjugator_checks"] = direct
        rows.append(row)
    return {"status": "PASS", "scope": "soundness and bounded counterexample controls; not a proof of necessity",
            "rows": rows, "physical_attachment_identifications": sum(r["pairs_checked"] for r in rows),
            "physical_direct_identifications": sum(c["pairs_checked"] for r in rows for c in r["direct_short_conjugator_checks"])}


def panel():
    source = HERE / "prepared_frames_panel20.jsonl"
    roots_file = HERE / "cyclic_complement_u124.json"
    audited_file = HERE / "complement_audit.json"
    audited = json.loads(audited_file.read_text())
    require(audited["status"] == "pass", "root audit did not pass")
    require(audited["hashes"][roots_file.name] == sha256(roots_file), "root archive hash changed")
    roots = {r["name"]: r for r in json.loads(roots_file.read_text())["records"]}
    rows, seen = [], set()
    with source.open() as stream, (HERE / "conjugated_complement_panel20.jsonl").open("w") as output:
        for line in stream:
            data = json.loads(line)
            name, pair = data["name"], data["input"]
            require(name not in seen, "duplicate panel input")
            seen.add(name)
            root = roots[name]
            require(root["pair"] == pair and root["complete"] and root["status"] == "no_cyclic_complement", "root seed")
            row = {"name": name, **screen(pair, 1000, tuple(map(tuple, root["graph"])))}
            output.write(json.dumps(row, separators=(",", ":")) + "\n")
            output.flush()
            rows.append({k: v for k, v in row.items() if k != "records"})
            time.sleep(0.1)
    require(len(rows) == 20, "wrong panel denominator")
    return {"status": "complete_capped_screen", "per_input_physical_identification_cap": 1000,
            "cooldown_seconds_per_input": 0.1, "rows": rows,
            "source_sha256": {p.name: sha256(p) for p in (source, roots_file, audited_file, Path(__file__),
                                                           HERE / "check_complement.py", HERE / "cyclic_complement.py",
                                                           HERE / "conjugated_complement_theory.md")},
            "pairs_checked": sum(r["pairs_checked"] for r in rows), "heap_nodes": 0,
            "positive_ids": [r["name"] for r in rows if r["positive"]],
            "complete_negative_ids": [r["name"] for r in rows if r["complete"] and not r["positive"]],
            "unknown_ids": [r["name"] for r in rows if not r["complete"]]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("controls", "panel"), required=True)
    args = parser.parse_args()
    result = controls() if args.mode == "controls" else panel()
    output = HERE / ("conjugated_complement_controls.json" if args.mode == "controls" else "conjugated_complement_panel20.json")
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("rows", "source_sha256")}, indent=2))


if __name__ == "__main__":
    main()
