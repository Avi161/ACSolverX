"""Cyclic-complement / join-corank probe for Q_{n,δ}.

Uses the existing Stallings fold from
``experiments.stable_ac.ak3_inverse_substitution_overgroups``. A unimodular
pair whose folded core has a vertex-pair identification to the full rose has
join corank 1, hence (by the cyclic-complement criterion) is stably AC-trivial
at rank 3. Failure of every pair fold only proves join corank ≥ 2 for that
exact pair; it is not an AC obstruction.

No heap search. Finite graph folds only.
"""

from __future__ import annotations

import json
import sys
import time
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.stable_ac.ak3_inverse_substitution_overgroups import (  # noqa: E402
    AK3,
    graph_rank,
    initial_graph,
    merge_vertices,
)

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"
ROSE = ((0, -2, 0), (0, -1, 0), (0, 1, 0), (0, 2, 0))
CHAR = {"x": 1, "X": -1, "y": 2, "Y": -2}


def compact_to_tuple(word: str) -> tuple[int, ...]:
    return tuple(CHAR[letter] for letter in word)


def q_pair(n: int, delta: int) -> tuple[str, str]:
    xd = "x" if delta == 1 else "X"
    return "XYxyxxy" + xd + "YXX", "Yxxy" + xd * n + "YXX"


def vertices(graph) -> list[int]:
    return sorted({0} | {vertex for source, _, target in graph for vertex in (source, target)})


def rose_hits(graph) -> list[list[int]]:
    hits = []
    verts = vertices(graph)
    for left, right in combinations(verts, 2):
        folded = merge_vertices(graph, (left, right))
        if folded == ROSE:
            hits.append([left, right])
    return hits


def probe_words(tag: str, words: tuple[tuple[int, ...], ...]) -> dict:
    graph = initial_graph(words)
    hits = rose_hits(graph)
    verts = vertices(graph)
    return {
        "tag": tag,
        "n_vertices": len(verts),
        "n_undirected_edges": len(graph) // 2,
        "rank": graph_rank(graph),
        "already_full_rose": graph == ROSE,
        "pair_folds": len(verts) * (len(verts) - 1) // 2,
        "rose_hits": hits,
        "join_corank_one": bool(hits) or graph == ROSE,
    }


def main() -> None:
    t0 = time.perf_counter()
    rows = []
    # Positive control: <x, y^2> has join corank 1.
    rows.append(probe_words("control_x_y2", ((1,), (2, 2))))
    # Negative-ish control: AK3 has join corank 2 (0 rose hits among 45 pairs).
    rows.append(probe_words("control_ak3", AK3))
    for delta in (-1, 1):
        for n in range(2, 8):
            r1, r2 = q_pair(n, delta)
            rows.append(
                probe_words(
                    f"Q_n{n}_d{delta:+d}",
                    (compact_to_tuple(r1), compact_to_tuple(r2)),
                )
            )
    wall = time.perf_counter() - t0
    n_q = [row for row in rows if row["tag"].startswith("Q_")]
    summary = {
        "wall_time_seconds": wall,
        "control_x_y2_join_corank_one": rows[0]["join_corank_one"],
        "control_ak3_rose_hits": len(rows[1]["rose_hits"]),
        "q_rows": len(n_q),
        "q_join_corank_one": sum(row["join_corank_one"] for row in n_q),
        "caveat": (
            "Join corank 1 would give a cyclic-complement stable trivialization. "
            "Zero rose hits means join corank ≥ 2 for these exact Q pairs, not an "
            "AC obstruction and not a certificate."
        ),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    payload = {"summary": summary, "rows": rows}
    path = OUT / "q_cyclic_complement.json"
    partial = path.with_name(path.name + ".partial")
    partial.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    partial.replace(path)
    print(json.dumps(summary, indent=2))
    print("control_x_y2", rows[0])
    print("control_ak3 rose_hits", len(rows[1]["rose_hits"]), "verts", rows[1]["n_vertices"])
    if not rows[0]["join_corank_one"]:
        raise SystemExit("positive control failed")
    if rows[1]["rose_hits"]:
        raise SystemExit("AK3 control unexpectedly found a cyclic complement")


if __name__ == "__main__":
    main()
