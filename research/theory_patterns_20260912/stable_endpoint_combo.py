"""Small stable isolator screen after saved ordinary theorem prefixes."""

import json
from pathlib import Path
import sys
import time

from .check_complement import sha256
from .endpoint_nielsen import pair_canon

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from coupled_power_word_compression import row_probe

PANEL = {"aca_115", "aca_116", "aca_1", "aca_13", "aca_30", "aca_55", "aca_80",
         "aca_59", "aca_79", "aca_82", "aca_109", "aca_108", "aca_101", "aca_117",
         "aca_9", "aca_67", "aca_86", "aca_106", "aca_54", "aca_5"}


def main():
    source_path = HERE / "endpoint_nielsen.jsonl"
    start_wall, start_cpu = time.perf_counter(), time.process_time()
    rows = []
    for line in source_path.open():
        saved = json.loads(line)
        if saved["name"] not in PANEL:
            continue
        original = pair_canon(saved["input"])
        unique = {}
        for index, state in enumerate(saved["states"]):
            pair = pair_canon(state["best_pair"])
            if pair == original or max(map(len, pair)) > 50:
                continue
            unique.setdefault(pair, index)
        selected = sorted(unique, key=lambda p: (sum(map(len, p)), p))[:3]
        attempts, used = [], 0
        for pair in selected:
            if used >= 500:
                break
            result = row_probe({"name": saved["name"], "r1": pair[0], "r2": pair[1]}, 500 - used, 6)
            used += result["attempted_endpoints"]
            attempts.append({"saved_state_index": unique[pair], "stable": result})
        rows.append({"name": saved["name"], "input": saved["input"], "input_length": saved["input_length"],
                     "available_new_basis_endpoints": len(unique), "attempted_basis_endpoints": len(attempts),
                     "stable_endpoints": used, "attempts": attempts,
                     "best_length_including_start": min([saved["input_length"]] + [
                         a["stable"]["best"]["best_length"] for a in attempts if a["stable"]["best"]])})
        time.sleep(.1)
    assert {row["name"] for row in rows} == PANEL
    result = {"status": "complete", "source_sha256": sha256(source_path),
              "script_sha256": sha256(Path(__file__)),
              "scope": "A priori20 panel; at most3 shortest new normalized endpoints per input, each relator<=50; <=500 evaluated stable endpoints shared across the row; defining words<=6, decomposition subproblem cap64. Additional algebraic screen, not total1k compute claim.",
              "certificate_kind": "composed ordinary prefix, invertible ambient maps and theorem-backed stable isolator; elementary stable expansion not emitted",
              "rows": rows, "new_strict_gain_ids": [r["name"] for r in rows if r["best_length_including_start"] < r["input_length"]],
              "stable_endpoints": sum(r["stable_endpoints"] for r in rows),
              "basis_endpoints": sum(r["attempted_basis_endpoints"] for r in rows),
              "cpu_seconds": time.process_time() - start_cpu,
              "wall_seconds_including_cooling": time.perf_counter() - start_wall}
    (HERE / "stable_endpoint_combo.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()
