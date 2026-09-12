"""Bounded compatible link-rotation checks on saved stable tuples."""
import hashlib
import json
import math
from pathlib import Path
import time

import networkx as nx
from . import snapshot_neuwirth_permutation_certificate as source

HERE = Path(__file__).resolve().parent


def nth_permutation(values, index):
    pool, output = list(values), []
    for remaining in range(len(pool), 0, -1):
        block = math.factorial(remaining - 1)
        digit, index = divmod(index, block)
        output.append(pool.pop(digit))
    return tuple(output)


def screen(words, budget=1000):
    data = source.OccurrenceData.from_words(tuple(words))
    endpoint_germ = {}
    for generator, ends in data.positive_ends.items():
        for end in ends:
            endpoint_germ[end] = generator
            endpoint_germ[data.B[end]] = generator.upper()
    graph = nx.Graph()
    graph.add_nodes_from(endpoint_germ.values())
    graph.add_edges_from((endpoint_germ[i], endpoint_germ[data.A[i]]) for i in range(len(data.A)))
    planar, _ = nx.check_planarity(graph)
    if not planar:
        return {"status": "nonplanar_link", "orders_tested": 0, "complete": True, "positive": None}
    ends = [tuple(sorted(v)) for v in data.positive_ends.values()]
    radices = [math.factorial(len(v) - 1) for v in ends]
    total = math.prod(radices)
    count = min(total, budget)
    minimum = None
    for i in range(count):
        index = i * total // count
        remaining, orders = index, []
        for vertices, radix in zip(ends, radices):
            digit, remaining = remaining % radix, remaining // radix
            orders.append((vertices[0], *nth_permutation(vertices[1:], digit)))
        C = source._build_C(data, tuple(orders))
        faces = source._cycle_count(source._compose(data.A, C))
        components = source._orbit_count((data.A, C))
        defect = len(data.A) // 2 - source._cycle_count(C) + 2 * components - faces
        if defect < 0 or defect % 2:
            raise ValueError("invalid orientable surface defect")
        minimum = defect if minimum is None else min(minimum, defect)
        if defect == 0:
            return {"status": "thickenability_candidate_pending_independent_audit", "orders_tested": i + 1,
                    "order_space": total, "complete": True, "minimum_observed_genus": 0,
                    "positive": {"index": index, "positive_orders": orders, "faces": faces,
                                 "link_components": components, "rotation": C}}
    return {"status": "no_compatible_spherical_order" if count == total else "unknown_at_order_cap",
            "orders_tested": count, "order_space": total, "complete": count == total,
            "minimum_observed_genus": minimum // 2, "positive": None}


def main():
    if screen(["x", "y", "z"])["positive"] is None:
        raise ValueError("basis positive control failed")
    if screen(["XXYXZYYZZ"])["status"] != "nonplanar_link":
        raise ValueError("K33 negative control failed")
    table_path = HERE / "u124_final_table.json"
    table = json.loads(table_path.read_text())
    seeds = [r for r in table["rows"] if r["best_rank"] == 3]
    (HERE / "stable_neuwirth_seed_snapshot.json").write_text(json.dumps(seeds, indent=2) + "\n")
    cpu, wall = time.process_time(), time.perf_counter()
    rows = []
    for seed in seeds:
        result = screen(seed["best_words"])
        rows.append({"name": seed["name"], "words": seed["best_words"],
                     "source_certificate_pointer": seed["source_certificate_pointer"], **result})
        time.sleep(0.1)
    report = {"status": "bounded_thickenability_screen", "rows": rows,
              "table_snapshot_sha256": hashlib.sha256(table_path.read_bytes()).hexdigest(),
              "source_hashes": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                                (Path(__file__), HERE / "snapshot_neuwirth_permutation_certificate.py")},
              "positive_ids": [r["name"] for r in rows if r["positive"]],
              "complete_negative_ids": [r["name"] for r in rows if r["complete"] and not r["positive"]],
              "unknown_ids": [r["name"] for r in rows if not r["complete"]],
              "orders_tested": sum(r["orders_tested"] for r in rows),
              "cpu_seconds": time.process_time() - cpu,
              "wall_seconds_including_cooling": time.perf_counter() - wall,
              "scope": "Compatibility uses occurrence-pair reversal. Capped orders are evenly spaced mixed-radix permutation indices, without constructing factorial arrays. A positive is not admitted as a solved row until independent geometric replay and theorem-hypothesis review."}
    (HERE / "stable_neuwirth_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in ("rows", "unknown_ids", "complete_negative_ids")}, indent=2))


if __name__ == "__main__":
    main()
