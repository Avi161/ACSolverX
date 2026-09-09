"""Bounded donor-only Nielsen normalization on seven saved survivors."""
import hashlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.words import apply_hom, apply_pair, canon_pair, canon_rel
from experiments.search.heuristic_1k import NIELSEN
from research.supermoves_20260908.bs_preflight import preflight
from research.supermoves_20260908.cheap_gates import bs_gate, one_occurrence_donor, two_block_gate
from research.supermoves_20260908.consecutive_bs import collapse as bs_collapse
from research.supermoves_20260908.certificate_decoder import decode_elementary, replay_elementary
from research.supermoves_20260908.stable_power import canonical_donor_gate


MAX_WORK = 1000
MAX_ACCEPTED = 10


def inspect(state):
    bs = bs_gate(state, general=True)
    check = preflight(state) if bs is not None else None
    result = {
        "general_bs": bs is not None,
        "bs_preflight": check,
        "stable_power_donors": canonical_donor_gate(state),
        "two_block": two_block_gate(state),
        "one_occurrence_relators": [i for i, word in enumerate(state) if one_occurrence_donor(word)],
    }
    # A conservative explicit price: one full-pair symbol scan for each of the
    # four gates, plus the comparison count reported by Britton preflight.
    cost = 4 * sum(map(len, state)) + (check or {}).get("scans", 0)
    return result, cost


def main():
    source_path = HERE / "DYNAMIC_BS_ENTRY.json"
    source = json.loads(source_path.read_text())
    selected = [row for row in source["rows"] if row["name"] not in {
        "ac19_14690", "ac19_23123", "ac19_28696", "ac19_32031",
        "ac19_3820", "ac19_9271",
    }]
    if len(selected) != 7:
        raise AssertionError([row["name"] for row in selected])

    output_rows = []
    for row in selected:
        root = tuple(canon_pair(*row["input_pair"]))
        work = 1
        started_wall = time.perf_counter()
        started_cpu = time.process_time()
        attempts = []
        root_gate, root_gate_cost = inspect(root)
        work += root_gate_cost
        for donor_start in (0, 1):
            if work >= MAX_WORK:
                attempts.append({
                    "donor_start_index": donor_start, "accepted_count": 0,
                    "terminal": "shared_work_limit_before_attempt", "accepted": [],
                })
                continue
            state = root
            donor = state[donor_start]
            cumulative = {"x": "x", "y": "y"}
            accepted = []
            terminal = None
            for depth in range(MAX_ACCEPTED):
                choices = []
                for index, transform in enumerate(NIELSEN):
                    cost = len(donor)
                    if work + cost > MAX_WORK:
                        terminal = "work_limit"
                        break
                    work += cost
                    image = canon_rel(apply_hom(donor, transform))
                    if len(image) < len(donor):
                        choices.append((len(image), image, index, transform))
                if terminal == "work_limit":
                    break
                if not choices:
                    terminal = "donor_minimal"
                    break
                _, next_donor, transform_index, transform = min(choices, key=lambda item: item[:3])
                pair_cost = sum(map(len, state))
                if work + pair_cost > MAX_WORK:
                    terminal = "work_limit_before_pair_map"
                    break
                work += pair_cost
                state = tuple(apply_pair(state, transform))
                cumulative = {g: apply_hom(cumulative[g], transform) for g in "xy"}
                if next_donor not in state:
                    raise AssertionError("tracked donor absent after accepted map")
                donor = next_donor
                gates, gate_cost = inspect(state)
                if work + gate_cost > MAX_WORK:
                    accepted.append({
                        "depth": depth + 1, "transform_index": transform_index,
                        "transform": transform, "state": list(state), "donor": donor,
                        "cumulative_images": cumulative,
                        "terminal_before_gates": "work_limit_before_inspection",
                    })
                    terminal = "work_limit_before_inspection"
                    break
                work += gate_cost
                entry = {
                    "depth": depth + 1, "transform_index": transform_index,
                    "transform": transform, "state": list(state), "donor": donor,
                    "cumulative_images": cumulative, "work_after_inspection": work,
                    "gates": gates,
                }
                if gates["general_bs"] and gates["bs_preflight"]["status"] == "accept":
                    remaining = MAX_WORK - work
                    if remaining >= 1:
                        result = bs_collapse(state, budget=remaining, intermediate_cap=None)
                        entry["certified_collapse"] = result
                        entry["collapse_work"] = result["nodes_explored"]
                        work += result["nodes_explored"]
                        if result["solved"]:
                            moves = decode_elementary(
                                state, result["states"], result["steps"],
                                result.get("elementary_tail"),
                            )
                            replay = replay_elementary(state, moves)
                            verified = sorted(word.lower() for word in replay) == ["x", "y"]
                            if not verified:
                                raise AssertionError("decoded transformed collapse is not terminal")
                            entry["transformed_certificate"] = {
                                "elementary_move_count": len(moves),
                                "replay_terminal": list(replay),
                                "verified": verified,
                                "original_pair_transport_compiled": False,
                            }
                accepted.append(entry)
                if entry.get("certified_collapse", {}).get("solved"):
                    terminal = "transformed_pair_collapsed"
                    break
            else:
                terminal = "accepted_transform_limit"
            attempts.append({
                "donor_start_index": donor_start, "accepted_count": len(accepted),
                "terminal": terminal, "accepted": accepted,
            })
        output_rows.append({
            "name": row["name"], "input_pair": list(root), "root_gates": root_gate,
            "work": work, "attempts": attempts,
            "wall_seconds": time.perf_counter() - started_wall,
            "cpu_seconds": time.process_time() - started_cpu,
        })

    artifact = {
        "scope": "Seven donor-normalization probes; no heap search and no original-pair solve claim.",
        "configuration": {
            "work_limit_per_root_across_both_donors": MAX_WORK,
            "accepted_transform_limit_per_donor": MAX_ACCEPTED,
            "nielsen_order": list(NIELSEN),
            "choice_order": "(image length, canonical image, transform index)",
            "work": (
                "root unit; donor input symbols for every Nielsen image; full-pair input "
                "symbols for accepted maps; four full-pair scans plus reported Britton "
                "comparisons per gate inspection; certified collapse nodes added"
            ),
        },
        "source": {"path": source_path.name, "sha256": hashlib.sha256(source_path.read_bytes()).hexdigest()},
        "rows": output_rows,
    }
    output = HERE / "DONOR_NORMALIZED_BS.json"
    output.write_text(json.dumps(artifact, indent=2) + "\n")
    print(json.dumps({
        "rows": len(output_rows),
        "accepted_maps": sum(a["accepted_count"] for r in output_rows for a in r["attempts"]),
        "transformed_collapses": sum(a["terminal"] == "transformed_pair_collapsed" for r in output_rows for a in r["attempts"]),
    }))


if __name__ == "__main__":
    main()
