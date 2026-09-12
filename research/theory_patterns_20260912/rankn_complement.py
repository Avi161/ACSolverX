"""Finite cyclic-complement checks over an explicit finite free basis."""

from collections import deque
from itertools import combinations
import json
from pathlib import Path
import time

from .check_complement import sha256

HERE = Path(__file__).resolve().parent


def inverse(word):
    return word.swapcase()[::-1]


def reduce_word(word, generators):
    alphabet = set(generators + generators.upper())
    stack = []
    for letter in word:
        if letter not in alphabet:
            raise ValueError("letter outside the declared free basis")
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def fold(edges, count, generators, identify=None):
    parent = list(range(count))
    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v
    def union(a, b):
        a, b = find(a), find(b)
        if a == b:
            return False
        parent[max(a, b)] = min(a, b)
        return True
    if identify is not None:
        union(*identify)
    while True:
        transitions, changed = {}, False
        for u, letter, v in edges:
            key, v = (find(u), letter), find(v)
            if key in transitions:
                changed |= union(transitions[key], v)
            else:
                transitions[key] = v
        if not changed:
            break
    edges = {(find(u), letter, find(v)) for u, letter, v in edges}
    transitions = {(u, letter): v for u, letter, v in edges}
    names, queue = {find(0): 0}, deque([find(0)])
    while queue:
        u = queue.popleft()
        for letter in generators + generators.upper():
            v = transitions.get((u, letter))
            if v is not None and v not in names:
                names[v] = len(names)
                queue.append(v)
    return tuple(sorted((names[u], letter, names[v]) for u, letter, v in edges))


def graph(words, generators):
    edges, count = [], 1
    for word in words:
        word = reduce_word(word, generators)
        u = 0
        for index, letter in enumerate(word):
            v = 0 if index + 1 == len(word) else count
            count += bool(v)
            edges.extend(((u, letter, v), (v, letter.swapcase(), u)))
            u = v
    return fold(edges, count, generators)


def rose(generators):
    return tuple(sorted((0, letter, 0) for letter in generators + generators.upper()))


def analyze(words, generators, limit=1000):
    core = graph(words, generators)
    vertices = {0} | {u for u, _, _ in core}
    if core == rose(generators):
        return {"status": "already_generates", "complement": "", "complete": True, "checks": 0}
    if len(vertices) == 1:
        missing = [letter for letter in generators if (0, letter, 0) not in core]
        return {"status": "cyclic_complement" if len(missing) == 1 else "no_cyclic_complement",
                "complement": missing[0] if len(missing) == 1 else None, "complete": True, "checks": 0}
    transitions = {(u, letter): v for u, letter, v in core}
    paths, queue = {0: ""}, deque([0])
    while queue:
        u = queue.popleft()
        for letter in generators + generators.upper():
            v = transitions.get((u, letter))
            if v is not None and v not in paths:
                paths[v] = paths[u] + letter
                queue.append(v)
    count = 0
    for u, v in combinations(sorted(vertices), 2):
        if count == limit:
            return {"status": "unknown_capped", "complement": None, "complete": False, "checks": count}
        count += 1
        if fold(core, len(vertices), generators, (u, v)) == rose(generators):
            word = reduce_word(paths[u] + inverse(paths[v]), generators)
            if graph([*words, word], generators) != rose(generators):
                raise AssertionError("explicit complement fails appended-loop check")
            return {"status": "cyclic_complement", "complement": word, "complete": True,
                    "checks": count, "identified": [u, v]}
    return {"status": "no_cyclic_complement", "complement": None, "complete": True, "checks": count}


def checks():
    assert analyze(["x", "y", "zz"], "xyz")["complement"] is not None
    assert analyze(["x", "yy", "zz"], "xyz")["complement"] is None
    assert analyze(["x", "y"], "xyz")["complement"] == "z"
    assert analyze(["x"], "xyz")["complement"] is None
    assert analyze(["x", "y", "z"], "xyz")["status"] == "already_generates"
    assert analyze(["x", "y", "zz"], "xyz", 0)["complete"] is False


def main():
    checks()
    source = HERE / "stable_dictionary_compression_report.json"
    saved = json.loads(source.read_text())
    started_cpu, started_wall = time.process_time(), time.perf_counter()
    rows = []
    for row in saved["rows"]:
        if row["best"] is None:
            continue
        words = row["best"]["relators"]
        result = analyze(words, "xyz")
        rows.append({"name": row["name"], "input_rank3": words, **result})
        time.sleep(.05)
    report = {"status": "rank3_complement_screen", "source_sha256": sha256(source),
              "script_sha256": sha256(Path(__file__)), "rows": rows,
              "criterion_candidate_ids": [r["name"] for r in rows if r["complement"] is not None],
              "complete_rows": sum(r["complete"] for r in rows), "checks": sum(r["checks"] for r in rows),
              "cpu_seconds": time.process_time() - started_cpu,
              "wall_seconds_including_cooling": time.perf_counter() - started_wall,
              "scope": "Exact cyclic-complement test of each saved shorter rank3 dictionary tuple, max1000identifications each. A positive requires independent graph and general-rank stable-criterion proof review before being admitted as a solve."}
    (HERE / "rank3_complement_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()
