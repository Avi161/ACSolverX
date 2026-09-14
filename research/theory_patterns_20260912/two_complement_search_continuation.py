"""One tiny S20 continuation on the saved, marked aca116 tag-pair target."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
PARENT = next(path for path in HERE.parents if (path / ".venv/bin/python").is_file())
for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMBA_NUM_THREADS"):
    os.environ[variable] = "1"
sys.path.insert(0, str(PARENT))
from experiments.search import heuristic_1k as original

spec = importlib.util.spec_from_file_location("captured_mixed_search", HERE / "captured_mixed_search.py")
captured = importlib.util.module_from_spec(spec)
spec.loader.exec_module(captured)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_prefix(pair, record):
    states = record["states"] if record["solved"] else record["best_states"]
    steps = record["steps"] if record["solved"] else record["best_steps"]
    current = original.canon_pair(*pair)
    if list(current) != states[0] or len(states) != len(steps) + 1:
        raise ValueError("prefix start or length")
    for step, expected in zip(steps, states[1:]):
        if step["kind"] != "substitution":
            raise ValueError("unexpected ambient edge in ordinary S20 continuation")
        current = tuple(original.moves_to_states(*current, [original.str_to_move(step["move"])])[-1])
        if list(current) != expected:
            raise ValueError("substitution prefix replay failed")
    return current


def main():
    source_path = PARENT / "experiments/search/heuristic_1k.py"
    if digest(source_path) != captured.SOURCE_SHA256:
        raise ValueError("parent source differs from captured function snapshot")
    warm_cpu, warm_wall = time.process_time(), time.perf_counter()
    control = ("xyx", "yxx")
    baseline = original.mixed_search(control, "s20", budget=1, cap=None)
    candidate = captured.mixed_search(control, "s20", budget=1, cap=None)
    if any(candidate[k] != value for k, value in baseline.items()):
        raise ValueError("capture changed original control outcome")
    verify_prefix(control, candidate)
    warm_cpu, warm_wall = time.process_time()-warm_cpu, time.perf_counter()-warm_wall
    pair = ("yyxYxyxYx", "XyXYYxxyXYXX")
    cpu, wall = time.process_time(), time.perf_counter()
    result = captured.mixed_search(pair, "s20", budget=16, cap=None)
    search_cpu, search_wall = time.process_time()-cpu, time.perf_counter()-wall
    endpoint = verify_prefix(pair, result)
    if result["solved"]:
        original.verify(pair, result)
    report = {"status": "verified_tiny_ordinary_continuation", "name": "aca_116",
              "input": pair, "input_length": sum(map(len, pair)),
              "original_u124_start_length": 14, "result": result,
              "verified_endpoint": endpoint, "search_cpu_seconds": search_cpu,
              "search_wall_seconds": search_wall, "warmup_and_control_cpu_seconds": warm_cpu,
              "warmup_and_control_wall_seconds": warm_wall,
              "relator_cap": None, "heap_pop_budget": 16, "previous_conservative_candidate_units": 984,
              "conservative_combined_units": 984 + result["nodes_explored"],
              "capture_control": "All original one-pop result fields agree exactly; best prefix additionally replays.",
              "source_hashes": {str(p): digest(p) for p in (source_path, Path(original.expand_and_score_h.py_func.__code__.co_filename),
                                                           HERE / "captured_mixed_search.py", Path(__file__))},
              "scope": "S20_MK2=L+20S+2MK; one thread, uncapped relators. Image candidates and heap pops are heterogeneous units, not an equal-compute baseline. U124 admission additionally requires the independently audited stable tag-pair bridge."}
    (HERE / "two_complement_search_continuation.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k not in ("result", "source_hashes")}, indent=2))
    print(json.dumps({k:v for k,v in result.items() if k not in ("states","steps","best_states","best_steps")}, indent=2))


if __name__ == "__main__":
    main()
