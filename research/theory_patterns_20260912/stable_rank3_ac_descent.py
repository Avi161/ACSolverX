"""Small exact AC substitution screens on retained rank3 dictionary states."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from primitive_compression import inverse, reduce_word, canonical_witness, normalize_tuple


def descend(words, budget=1000):
    if type(budget) is not int or not 0 <= budget <= 1000:
        raise ValueError("invalid substitution budget")
    current, canonical = normalize_tuple(words)
    initial = {"before": list(words), "after": current, "canonical_witnesses": canonical}
    used, passes, steps = 0, 0, []
    while used < budget:
        options, complete = [], True
        for target in range(3):
            for donor in range(3):
                if target == donor:
                    continue
                for sign in (1, -1):
                    base = current[donor] if sign == 1 else inverse(current[donor])
                    for i in range(max(1, len(current[target]))):
                        for j in range(max(1, len(base))):
                            if used == budget:
                                complete = False
                                break
                            used += 1
                            left = current[target][i:] + current[target][:i]
                            right = base[j:] + base[:j]
                            raw = reduce_word(left + right)
                            child, witness = canonical_witness(raw)
                            if len(child) < len(current[target]):
                                pair = list(current); pair[target] = child
                                options.append((sum(map(len, pair)), tuple(pair), target, donor, sign, i, j, raw, witness))
                        if not complete:
                            break
                    if not complete:
                        break
                if not complete:
                    break
            if not complete:
                break
        passes += int(complete)
        if not options:
            stop = "no_strict_AC_substitution_descent" if complete else "substitution_budget"
            break
        total, child, target, donor, sign, i, j, raw, witness = min(options)
        steps.append({"before": current, "target": target, "donor": donor, "donor_sign": sign,
                      "target_cut": i, "donor_cut": j, "raw_product": raw,
                      "canonical_witness": witness, "after": list(child), "rank": 3,
                      "total_length": total})
        current = list(child)
        if not complete:
            stop = "substitution_budget"
            break
    else:
        stop = "substitution_budget"
    return {"initial_normalization": initial, "steps": steps, "endpoint": current,
            "rank": 3, "total_length": sum(map(len, current)), "substitutions": used,
            "complete_sweeps": passes, "stop": stop}


def main():
    control = descend(["x", "xy", "z"])
    if control["total_length"] != 3 or not control["steps"]:
        raise ValueError("positive substitution control failed")
    source_path = HERE / "stable_dictionary_compression_report.json"
    source = json.loads(source_path.read_text())
    cpu, wall = time.process_time(), time.perf_counter()
    rows = []
    for row in source["rows"]:
        if row["best"] is None:
            continue
        result = descend(row["best"]["relators"])
        rows.append({"name": row["name"], "input": row["input"], "source_witness": row["best"],
                     "result": result, "improves_prefix": result["total_length"] < row["best"]["total_length"]})
        time.sleep(0.05)
    report = {"status": "exact_bounded_AC_substitution_screen", "rows": rows,
              "source_report_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "prefix_improvement_ids": [r["name"] for r in rows if r["improves_prefix"]],
              "substitutions": sum(r["result"]["substitutions"] for r in rows),
              "maximum_substitutions_per_row": max(r["result"]["substitutions"] for r in rows),
              "strict_steps": sum(len(r["result"]["steps"]) for r in rows),
              "locally_minimal_endpoint_rows": sum(r["result"]["stop"] == "no_strict_AC_substitution_descent" for r in rows),
              "cpu_seconds": time.process_time() - cpu,
              "wall_seconds_including_cooling": time.perf_counter() - wall,
              "scope": "Every positive requires separate replay before final-table admission. First-sweep completeness tests one substitution from each retained state, not all AC paths or plateaus."}
    (HERE / "stable_rank3_ac_descent_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()
