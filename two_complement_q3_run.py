"""Two theory-selected complement changes, each sharing a1000-unit budget."""
import hashlib
import json
from pathlib import Path
import time
import sys

HERE = Path(__file__).resolve().parent / "research/theory_patterns_20260912"
sys.path.insert(0, str(HERE))
import two_complement_unit_gate as gate
from research.theory_patterns_20260912.two_complement_search_continuation import captured, verify_prefix, original
from research.theory_patterns_20260912.compile_search_prefix import compile_prefix


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    destination = HERE / "two_complement_q3_report.json"
    if destination.exists():
        raise ValueError("do not rerun saved experiment")
    source = HERE / "two_complement_unit_gate_report.json"
    if digest(source) != "a87446e02b89c2fa10977eb11e0b81100d588577ccbc2f00b18f45ce143daa74":
        raise ValueError("source changed")
    inputs = {row["name"]: row for row in json.loads(source.read_text())["rows"]}
    for name, power in (("aca_115", 3), ("aca_59", 7)):
        assert inputs[name]["input"][1] == "YYYY" + "x" * power
    warm_cpu, warm_wall = time.process_time(), time.perf_counter()
    control = ("xyx", "yxx")
    base = original.mixed_search(control, "s20", budget=1, cap=None)
    candidate = captured.mixed_search(control, "s20", budget=1, cap=None)
    assert all(candidate[k] == v for k, v in base.items())
    warm_cpu, warm_wall = time.process_time()-warm_cpu, time.perf_counter()-warm_wall
    rows, certificates = [], []
    for name in ("aca_115", "aca_59"):
        pair = inputs[name]["input"]
        initial = [*pair, "x", "yyy"]
        started = time.process_time()
        budget = gate.prototype.Budget(1000)
        folded = gate.prototype.graph(initial, "xy")
        assert folded == gate.prototype.rose("xy")
        search = gate.nielsen(initial, budget)
        row = {"name": name, "input": pair, "input_length": sum(map(len, pair)),
            "complements": ["x", "yyy"], "initial_image_tuple": initial,
            "full_fold_graph": folded, "join_is_full": True, "image_limit": 1000,
            "status": search["status"], "search": search, "projected": None,
            "image_evaluations": budget.used, "image_evaluation_counts": dict(budget.counts),
            "remaining_shared_budget": 1000-budget.used, "solved": False,
            "prefix_cpu_seconds": time.process_time()-started}
        if search["status"] == "marked_kernel_basis_found":
            projected = gate.project(search)
            row["projected"] = {"pair": projected, "total_length": sum(map(len, projected)),
                "determinant": gate.prototype.determinant(projected),
                "cyclic_inverse_permutation_match": gate.prototype.pair_key(projected) == gate.prototype.pair_key(pair)}
            assert abs(row["projected"]["determinant"]) == 1
            row["stable_equivalence_witness"] = gate.prototype.stable_equivalence_witness(pair, search)
            started, wall = time.process_time(), time.perf_counter()
            result = captured.mixed_search(projected, "s20", budget=row["remaining_shared_budget"], cap=None)
            row["search_cpu_seconds"], row["search_wall_seconds"] = time.process_time()-started, time.perf_counter()-wall
            endpoint = verify_prefix(projected, result)
            states = result["states"] if result["solved"] else result["best_states"]
            steps = result["steps"] if result["solved"] else result["best_steps"]
            started = time.process_time()
            cert = compile_prefix(projected, states, steps)
            row["compile_cpu_seconds"] = time.process_time()-started
            certificates.append({"name": name, **cert})
            row.update(result=result, solved=result["solved"], best_pair=list(endpoint),
                best_length=sum(map(len, endpoint)), heap_pops=result["nodes_explored"],
                combined_units=budget.used+result["nodes_explored"],
                improves_original=sum(map(len, endpoint)) < row["input_length"],
                elementary_move_count=cert["elementary_move_count"])
        else:
            row.update(heap_pops=0, combined_units=budget.used, improves_original=False)
        assert row["combined_units"] <= 1000
        rows.append(row)
        print(json.dumps({k:v for k,v in row.items() if k not in ("search", "result", "stable_equivalence_witness")}), flush=True)
        time.sleep(.08)
    cert_path = HERE / "two_complement_q3_certificates.jsonl"
    cert_path.write_text("".join(json.dumps(row)+"\n" for row in certificates))
    report = {"status": "author_verified_pending_independent_audit", "rows": rows,
        "selection": "Only the two prior q2 proper joins with explicit y^4 and x in their subgroup: gcd(3,4)=1 proves adding y^3 gives the full free group.",
        "solved_ids": [row["name"] for row in rows if row["solved"]],
        "strict_original_gain_ids": [row["name"] for row in rows if row["improves_original"]],
        "relator_cap": None, "certificate_file": cert_path.name, "certificate_sha256": digest(cert_path),
        "warmup_and_control_cpu_seconds": warm_cpu, "warmup_and_control_wall_seconds": warm_wall,
        "source_hashes": {path.name:digest(path) for path in (Path(__file__), source, Path(gate.__file__),
            HERE / "captured_mixed_search.py", Path(original.__file__), HERE / "compile_search_prefix.py")},
        "scope": "Two additional exploratory attempts, each at most1000 heterogeneous image/compiler/heap units; not cumulative1000 across all session experiments. Stable prefix theorem requires known trivial input; ordinary suffixes fully emitted and replayed. Negative outcomes are bounded, not obstruction proofs."}
    destination.write_text(json.dumps(report, indent=2)+"\n")


if __name__ == "__main__":
    main()
