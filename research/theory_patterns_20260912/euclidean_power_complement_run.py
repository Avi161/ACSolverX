"""One direct power-complement transfer; no Nielsen candidate search."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import two_complement_unit_gate as gate
from .two_complement_search_continuation import original, captured, verify_prefix
from .compile_search_prefix import compile_prefix


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = HERE / "euclidean_power_complement_report.json"
    if output.exists():
        raise ValueError("saved experiment already exists")
    source_path = HERE / "two_complement_unit_gate_report.json"
    old = next(r for r in json.loads(source_path.read_text())["rows"] if r["name"] == "aca_59")
    original_pair = old["input"]
    assert original_pair == ["YXXYxxyxx", "YYYYxxxxxxx"]
    swap = str.maketrans("xXyY", "yYxX")
    pair = [original_pair[0].translate(swap), gate.prototype.inv(original_pair[1]).translate(swap)]
    assert pair == ["XYYXyyxyy", "YYYYYYYxxxx"]
    initial = [*pair, "x", "yy"]
    images, basis, moves = tuple(initial), tuple("rstu"), []
    budget = gate.prototype.Budget(1000)
    assert budget.charge("input_inversion_and_two_ambient_word_images", 3)
    assert budget.charge("initial_image_words", 4)
    started = time.process_time()
    for donor, sign, repeats in ((2, -1, 4), (3, 1, 3)):
        for _ in range(repeats):
            move = {"op": "multiply", "target": 1, "donor": donor, "sign": sign, "side": "right"}
            images = gate.prototype.row_move(images, move)
            basis = gate.prototype.row_move(basis, move)
            moves.append(move)
            assert budget.charge("direct_Euclidean_image_updates", 1)
    assert images[1] == "Y" and images[2] == "x"
    search = gate.finish_if_possible(initial, (images, basis, moves), budget, Counter(), "direct")
    assert search is not None and search["images"] == ["", "", "x", "y"]
    projected = gate.project(search)
    row = {"name": "aca_59", "input": pair, "input_length": sum(map(len, pair)),
        "original_input": original_pair, "original_input_length": sum(map(len, original_pair)),
        "input_bridge": {"ordinary_invert_relator": 2, "ambient_images": {"x": "y", "y": "x"},
                         "inverse_ambient_images": {"x": "y", "y": "x"}},
        "complements": ["x", "yy"], "initial_image_tuple": initial,
        "join_is_full": gate.prototype.graph(initial, "xy") == gate.prototype.rose("xy"),
        "image_limit": 1000, "search": search, "status": "marked_kernel_basis_found",
        "projected": {"pair": projected, "total_length": sum(map(len, projected)),
            "determinant": gate.prototype.determinant(projected),
            "cyclic_inverse_permutation_match": gate.prototype.pair_key(projected) == gate.prototype.pair_key(pair)},
        "stable_equivalence_witness": gate.prototype.stable_equivalence_witness(pair, search),
        "image_evaluations": budget.used, "image_evaluation_counts": dict(budget.counts),
        "remaining_shared_budget": 1000-budget.used, "prefix_cpu_seconds": time.process_time()-started}
    warm_cpu, warm_wall = time.process_time(), time.perf_counter()
    test_pair = ("xyx", "yxx")
    before = original.mixed_search(test_pair, "s20", budget=1, cap=None)
    after = captured.mixed_search(test_pair, "s20", budget=1, cap=None)
    assert all(after[k] == v for k, v in before.items())
    warm_cpu, warm_wall = time.process_time()-warm_cpu, time.perf_counter()-warm_wall
    started, wall = time.process_time(), time.perf_counter()
    result = captured.mixed_search(projected, "s20", budget=row["remaining_shared_budget"], cap=None)
    row["search_cpu_seconds"], row["search_wall_seconds"] = time.process_time()-started, time.perf_counter()-wall
    endpoint = verify_prefix(projected, result)
    started = time.process_time()
    cert = compile_prefix(projected, result["states"] if result["solved"] else result["best_states"],
                          result["steps"] if result["solved"] else result["best_steps"])
    row["compile_cpu_seconds"] = time.process_time()-started
    cert_path = HERE / "euclidean_power_complement_certificate.json"
    cert_path.write_text(json.dumps({"name": "aca_59", **cert}, indent=2)+"\n")
    row.update(result=result, solved=result["solved"], best_pair=list(endpoint), best_length=sum(map(len, endpoint)),
        improves_original=sum(map(len, endpoint)) < row["original_input_length"],
        heap_pops=result["nodes_explored"], combined_units=budget.used+result["nodes_explored"],
        elementary_move_count=cert["elementary_move_count"])
    assert row["combined_units"] <= 1000
    report = {"status": "author_verified_pending_independent_audit", "rows": [row],
        "solved_ids": ["aca_59"] if row["solved"] else [],
        "strict_original_gain_ids": ["aca_59"] if row["improves_original"] else [],
        "relator_cap": None, "certificate_file": cert_path.name, "certificate_sha256": digest(cert_path),
        "warmup_and_control_cpu_seconds": warm_cpu, "warmup_and_control_wall_seconds": warm_wall,
        "source_hashes": {p.name:digest(p) for p in (Path(__file__), source_path, Path(gate.__file__),
                            HERE / "captured_mixed_search.py", Path(original.__file__), HERE / "compile_search_prefix.py")},
        "scope": "One fresh independently budgeted1000-unit attempt on aca59. Input inversion and ambient axis swap are explicit; a direct Euclidean free-basis construction replaces Nielsen search. Prefix image/compiler operations and heap pops are heterogeneous units, not equal compute or a cumulative limit over earlier attempts. Stable prefix finite-realizability is theorem-backed; ordinary search suffix fully emitted."}
    output.write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({k:v for k,v in row.items() if k not in ("search", "result", "stable_equivalence_witness")}, indent=2))


if __name__ == "__main__":
    main()
