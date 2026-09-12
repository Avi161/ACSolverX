"""Read-only scope of the proved residue family in the exact MS census."""

import ast
from collections import Counter
import json
from pathlib import Path
import time

from .ac_words import canon
from .check_complement import sha256
from .endpoint_gates import ms_matches

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(path):
    rows = []
    letters = {1: "x", -1: "X", 2: "y", -2: "Y"}
    for index, line in enumerate(path.read_text().splitlines()):
        if not line.strip():
            continue
        values = ast.literal_eval(line)
        if len(values) != 48 or any(type(x) is not int or x not in (0, 1, -1, 2, -2) for x in values):
            raise ValueError(f"malformed48-symbol row {index + 1}")
        pair = tuple("".join(letters[v] for v in half if v) for half in (values[:24], values[24:]))
        rows.append((index + 1, pair))
    return rows


def key(pair):
    return tuple(sorted(canon(word) for word in pair))


def main():
    start_cpu, start_wall = time.process_time(), time.perf_counter()
    census_path, solved_path = ROOT / "data/1190MS.txt", ROOT / "data/ms640_solved.txt"
    census, solved = load(census_path), load(solved_path)
    assert len(census) == 1190 and len(solved) == 640
    solved_keys = {key(pair) for _, pair in solved}
    counts, records = Counter(), []
    for line_index, pair in census:
        matches = ms_matches(pair)
        if not matches:
            continue
        terminal_matches = [m for m in matches if m["terminal"]]
        was_solved = key(pair) in solved_keys
        counts["matched_rows"] += 1
        counts["terminal_rows"] += bool(terminal_matches)
        counts["terminal_already_in_solved640"] += bool(terminal_matches) and was_solved
        counts["terminal_outside_solved640"] += bool(terminal_matches) and not was_solved
        records.append({"census_line_1based": line_index, "pair": pair,
                        "already_in_solved640": was_solved, "matches": matches,
                        "terminal_by_proved_residue_criterion": bool(terminal_matches)})
    result = {"status": "literal_scope_scan", "counts": dict(counts), "rows": records,
              "input_rows": len(census), "saved_solved_rows": len(solved),
              "input_sha256": sha256(census_path), "solved_input_sha256": sha256(solved_path),
              "script_sha256": sha256(Path(__file__)),
              "scope": "Exact cyclic/inverse/signed-axis literal recognition of the new three-stable-letter residue family. The general parameter theorem establishes completion for terminal residues, but no census elementary streams were generated in this read-only scan. Coverage already in solved640 is a new theorem route, not a new solve.",
              "cpu_seconds": time.process_time() - start_cpu,
              "wall_seconds": time.perf_counter() - start_wall}
    (HERE / "ms_census_scope.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()
