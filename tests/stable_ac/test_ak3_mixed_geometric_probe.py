import json
from pathlib import Path


def inverse(word):
    return "".join(letter.swapcase() for letter in reversed(word))


def reduce_word(word):
    stack = []
    for letter in word:
        assert letter in "xXyY"
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def test_saved_mixed_geometric_probe_has_independent_literal_replay():
    artifact_path = Path(__file__).resolve().parents[2] / "results/stable_ac/theory/ak3_mixed_geometric_probe_20260905.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    source = ("xxxYYYY", "xyxYXY")
    assert tuple(artifact["source"]) == source
    assert artifact["schema"] == "acsolverx.ak3.mixed-geometric-probe.v1"
    assert artifact["config"]["seed"] == 20260905
    assert artifact["config"]["restart_interval"] == 32
    assert artifact["config"]["max_free_length"] == 32
    controls = artifact["controls"]
    assert len(controls) == 2
    assert [tuple(control["words"]) for control in controls] == [("X", "XYXy"), source]
    assert [control["spherical"] for control in controls] == [True, False]
    assert all(control["status"] == "PASSED" and control["spherical"] is control["expected_spherical"]
               for control in controls)
    assert artifact["summary"] == {
        "accepted_moves": 677, "attempted_moves": 1000, "below_length": 211,
        "completed_solver_calls": 37, "duplicates": 429, "rejected_moves": 323,
        "restarts": 32, "solver_calls": 37, "unsupported": 0,
    }
    candidates = artifact["candidates"]
    assert len(candidates) == 37
    keys, move_count, last_candidate_attempt = set(), 0, 0
    for candidate in candidates:
        attempt = candidate["attempt"]
        assert last_candidate_attempt < attempt <= 1000
        last_candidate_attempt = attempt
        block_start = ((attempt - 1) // 32) * 32 + 1
        previous_attempt, pair = block_start - 1, source
        trail = candidate["from_root_trail"]
        assert trail and trail[-1]["attempt"] == attempt
        for step in trail:
            assert block_start <= step["attempt"] <= attempt
            assert step["attempt"] > previous_attempt
            previous_attempt = step["attempt"]
            operation = step["operation"]
            rows = list(pair)
            kind = operation[0]
            if kind == "swap":
                assert operation == ["swap"]
                rows = rows[::-1]
            elif kind == "invert":
                assert len(operation) == 2 and operation[1] in (0, 1)
                rows[operation[1]] = inverse(rows[operation[1]])
            elif kind == "multiply":
                assert len(operation) == 3 and operation[1] in (0, 1) and operation[2] in (-1, 1)
                recipient, sign = operation[1:]
                donor = rows[1 - recipient]
                rows[recipient] += donor if sign == 1 else inverse(donor)
            else:
                assert kind == "conjugate" and len(operation) == 3
                recipient, prefix = operation[1:]
                assert recipient in (0, 1) and prefix in ("x", "X", "y", "Y")
                rows[recipient] = prefix + rows[recipient] + inverse(prefix)
            pair = tuple(reduce_word(row) for row in rows)
            assert pair == tuple(step["resulting_pair"])
            assert all(pair) and sum(map(len, pair)) <= 32
            move_count += 1
        assert pair == tuple(candidate["freely_reduced_pair"])
        cores, prefixes = [], []
        for row in pair:
            left, right = 0, len(row)
            while right - left > 1 and row[left] == row[right - 1].swapcase():
                left += 1
                right -= 1
            prefix, core = row[:left], row[left:right]
            assert reduce_word(prefix + core + inverse(prefix)) == row
            assert reduce_word(inverse(prefix) + row + prefix) == core
            assert core and reduce_word(core) == core
            assert len(core) == 1 or core[0] != core[-1].swapcase()
            prefixes.append(prefix)
            cores.append(core)
        assert cores == candidate["cores"]
        assert prefixes == candidate["peel_prefixes"]
        assert [inverse(prefix) for prefix in prefixes] == candidate["final_conjugators"]
        assert sum(map(len, cores)) >= 18
        key = tuple(sorted(min(word[index:] + word[:index]
                               for word in (core, inverse(core)) for index in range(len(core)))
                           for core in cores))
        assert key not in keys
        keys.add(key)
        assert candidate["decision"]["spherical"] is False
        assert candidate["decision"]["verdict"] == "NOT_SPHERICAL"
        assert candidate["decision"]["support"] in ("K4", "K4-e", "C4")
    assert move_count == 266
    assert artifact["status"] == "bounded_probe_completed"
    assert artifact["attempt_budget_reached"] is True
    assert artifact["solver_budget_reached"] is False
    assert artifact["positive_found"] is False
    assert artifact["ac_obstruction_claimed"] is False
