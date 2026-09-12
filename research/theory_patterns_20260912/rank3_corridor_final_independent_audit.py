"""A third replay implementation for the signed corridor terminal fixtures."""
import hashlib
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
ENCODING = {"x": 1, "y": 2, "z": 3, "X": -1, "Y": -2, "Z": -3}


def reduce(values):
    result = []
    for value in values:
        if result and result[-1] == -value:
            result.pop()
        else:
            result.append(value)
    return result


def invert(values):
    return [-value for value in reversed(values)]


def power(value, exponent):
    return [value if exponent >= 0 else -value] * abs(exponent)


def main():
    cpu = time.process_time()
    source = HERE / "rank3_corridor_final_analysis_checks.json"
    data = json.loads(source.read_text())
    cases = data["rows"]
    assert len(cases) == 14
    assert {(r["parameters"]["n"], r["parameters"]["k"]) for r in cases} == {
        (n, n + sign) for n in range(-3, 4) for sign in (-1, 1)}
    moves, states, peak = 0, 0, 0
    for case in cases:
        p = case["parameters"]
        assert p["m"] == -1 and abs(p["k"] - p["n"]) == 1
        current = [reduce([ENCODING[c] for c in word]) for word in case["initial"]]
        expected = [reduce([3, -1] + power(2, p["n"])), [-3, 1, 2, 1],
                    reduce([3] + power(2, p["k"]) + [-3, 2, 1])]
        assert current == expected
        states += 1
        for move in case["moves"]:
            target = move["target"]
            assert type(target) is int and 0 <= target < 3
            if move["op"] == "AC1":
                current[target] = invert(current[target])
            elif move["op"] == "AC2":
                donor = move["donor"]
                assert type(donor) is int and 0 <= donor < 3 and donor != target
                current[target] = reduce(current[target] + current[donor])
            elif move["op"] == "AC3":
                assert len(move["by"]) == 1 and move["by"] in ENCODING
                letter = ENCODING[move["by"]]
                current[target] = reduce([-letter] + current[target] + [letter])
            else:
                raise ValueError("not an elementary move")
            states += 1
            moves += 1
            peak = max(peak, sum(map(len, current)))
        assert current == [[1], [2], [3]]
    report = {"status": "pass", "signed_fixtures": 14, "elementary_moves": moves,
        "replayed_states": states, "maximum_replayed_total_length": peak,
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "auditor_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "cpu_seconds": time.process_time()-cpu,
        "scope": "Independent literal signed input construction and strict zero-based AC1/AC2/one-letter-AC3 replay to exactly(x,y,z). No imports from author or prior replayers; no search and no U124 solve claim. The infinite family proof is the algebraic unit-elimination argument in rank3_corridor_final_analysis.md."}
    (HERE / "rank3_corridor_final_independent_audit.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
