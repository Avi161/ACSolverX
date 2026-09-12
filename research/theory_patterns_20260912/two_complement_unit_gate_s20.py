"""Serial residual-budget S20 on independently marked stable projections."""
import hashlib
import json
from pathlib import Path
import time

from .two_complement_search_continuation import original, captured, verify_prefix
from .compile_search_prefix import compile_prefix

HERE = Path(__file__).resolve().parent
SOURCE_SHA256 = "a87446e02b89c2fa10977eb11e0b81100d588577ccbc2f00b18f45ce143daa74"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source_path = HERE / "two_complement_unit_gate_report.json"
    if digest(source_path) != SOURCE_SHA256:
        raise ValueError("projection source changed")
    engine_path = Path(original.__file__)
    if digest(engine_path) != captured.SOURCE_SHA256:
        raise ValueError("parent search differs from frozen capture source")
    source = json.loads(source_path.read_text())
    selected = [row for row in source["rows"] if row["projected"]]
    assert len(selected) == 15
    warm_cpu, warm_wall = time.process_time(), time.perf_counter()
    pair = ("xyx", "yxx")
    old = original.mixed_search(pair, "s20", budget=1, cap=None)
    new = captured.mixed_search(pair, "s20", budget=1, cap=None)
    if any(new[key] != value for key, value in old.items()):
        raise ValueError("capture changed search control")
    verify_prefix(pair, new)
    warm_cpu = time.process_time() - warm_cpu
    warm_wall = time.perf_counter() - warm_wall
    rows, certificates = [], []
    batch_wall = time.perf_counter()
    for prefix in selected:
        pair = tuple(prefix["projected"]["pair"])
        budget = prefix["remaining_shared_budget"]
        assert budget + prefix["image_evaluations"] == 1000
        cpu, wall = time.process_time(), time.perf_counter()
        outcome = captured.mixed_search(pair, "s20", budget=budget, cap=None)
        search_cpu, search_wall = time.process_time()-cpu, time.perf_counter()-wall
        verify_cpu, verify_wall = time.process_time(), time.perf_counter()
        endpoint = verify_prefix(pair, outcome)
        states = outcome["states"] if outcome["solved"] else outcome["best_states"]
        steps = outcome["steps"] if outcome["solved"] else outcome["best_steps"]
        certificate = compile_prefix(pair, states, steps)
        if certificate["endpoint"] != list(endpoint):
            raise ValueError("elementary compiler disagrees with search replay")
        if outcome["solved"]:
            original.verify(pair, outcome)
        verify_cpu, verify_wall = time.process_time()-verify_cpu, time.perf_counter()-verify_wall
        certificates.append({"name": prefix["name"], "projection_source_sha256": SOURCE_SHA256,
                             "source_pointer": "two_complement_unit_gate_report.json#" + prefix["name"],
                             **certificate})
        rows.append({"name": prefix["name"], "original_input": prefix["input"],
            "original_input_length": prefix["input_length"], "projected_input": list(pair),
            "projected_input_length": sum(map(len, pair)), "solved": outcome["solved"],
            "best_pair": list(endpoint), "best_length": sum(map(len, endpoint)),
            "improves_original": sum(map(len, endpoint)) < prefix["input_length"],
            "prefix_units": prefix["image_evaluations"], "heap_pop_budget": budget,
            "heap_pops": outcome["nodes_explored"],
            "combined_units": prefix["image_evaluations"] + outcome["nodes_explored"],
            "search_cpu_seconds": search_cpu, "search_wall_seconds": search_wall,
            "replay_and_compile_cpu_seconds": verify_cpu, "replay_and_compile_wall_seconds": verify_wall,
            "elementary_move_count": certificate["elementary_move_count"],
            "result": outcome})
        assert rows[-1]["combined_units"] <= 1000
        print(json.dumps({key: value for key, value in rows[-1].items() if key != "result"}), flush=True)
        time.sleep(.08)
    certificate_path = HERE / "two_complement_unit_gate_s20_certificates.jsonl"
    partial = certificate_path.with_suffix(".jsonl.partial")
    partial.write_text("".join(json.dumps(row, separators=(",", ":"))+"\n" for row in certificates))
    partial.replace(certificate_path)
    report = {"status": "elementary_suffixes_verified_pending_independent_admission", "rows": rows,
        "projection_source_sha256": SOURCE_SHA256, "certificate_file": certificate_path.name,
        "certificate_sha256": digest(certificate_path), "input_count": len(rows),
        "solved_ids": [row["name"] for row in rows if row["solved"]],
        "strict_original_gain_ids": [row["name"] for row in rows if row["improves_original"]],
        "search_cpu_seconds": sum(row["search_cpu_seconds"] for row in rows),
        "search_wall_seconds": sum(row["search_wall_seconds"] for row in rows),
        "replay_and_compile_cpu_seconds": sum(row["replay_and_compile_cpu_seconds"] for row in rows),
        "replay_and_compile_wall_seconds": sum(row["replay_and_compile_wall_seconds"] for row in rows),
        "batch_wall_seconds_including_cooling": time.perf_counter()-batch_wall,
        "cooldown_seconds_per_row": .08, "warmup_and_control_cpu_seconds": warm_cpu,
        "warmup_and_control_wall_seconds": warm_wall, "relator_cap": None,
        "total_heap_pops": sum(row["heap_pops"] for row in rows),
        "total_combined_units": sum(row["combined_units"] for row in rows),
        "source_hashes": {path.name: digest(path) for path in (Path(__file__), engine_path,
            Path(original.expand_and_score_h.py_func.__code__.co_filename), HERE / "captured_mixed_search.py",
            HERE / "compile_search_prefix.py", HERE / "ac_words.py")},
        "scope": "Serial S20_MK2 without a relator cap; initial complementary-kernel projection uses theorem-backed stable AC equivalence, followed by fully emitted ordinary suffixes. Prefix image/compiler units and heap pops are heterogeneous, not equal compute. Five proper-join rejects were not searched. No baseline rerun. Each input's combined count is at most1000; independent certification is additional measured overhead."}
    (HERE / "two_complement_unit_gate_s20_report.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({key:value for key,value in report.items() if key not in ("rows", "source_hashes")}, indent=2))


if __name__ == "__main__":
    main()
