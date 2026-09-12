"""Bounded exact Aut canonicalization of the64 saved residue targets."""

from collections import defaultdict
import json
from pathlib import Path
import time

from experiments.equivalence_classes.lib.autcanon import aut_canon, check, is_automorphism
from .check_complement import sha256

HERE = Path(__file__).resolve().parent


def main():
    source = HERE / "ms_residue_class_probe.json"
    saved = json.loads(source.read_text())
    targets = defaultdict(set)
    for row in saved["rows"]:
        targets[tuple(row["winner"]["normalization"]["endpoint"])].add(row["aca_id"])
    groups, records = defaultdict(set), []
    start_cpu, start_wall = time.process_time(), time.perf_counter()
    for target in sorted(targets):
        try:
            length, representative, images = aut_canon(target, level_cap=1000)
        except RuntimeError as error:
            records.append({"input": target, "classes": sorted(targets[target]), "status": "unknown_capped", "reason": str(error)})
        else:
            assert check(target, representative, images) and is_automorphism(images)
            groups[representative].update(targets[target])
            records.append({"input": target, "classes": sorted(targets[target]), "status": "complete",
                            "representative": representative, "images": images, "length": length})
        time.sleep(.05)
    result = {"status": "completed_bounded_orbit_screen", "source_sha256": sha256(source),
              "script_sha256": sha256(Path(__file__)), "rows": records,
              "targets": len(targets), "complete_orbits": len(groups),
              "capped_targets": sum(r["status"] == "unknown_capped" for r in records),
              "potential_class_merges": [{"representative": pair, "classes": sorted(classes)} for pair, classes in groups.items() if len(classes) > 1],
              "cpu_seconds": time.process_time() - start_cpu,
              "wall_seconds_including_cooling": time.perf_counter() - start_wall,
              "scope": "1000 minimal-level Aut states maximum per distinct target; all witnessing maps verified. Cross-U124 matches, if any, remain candidates until older cell-to-class bridges and new normalization certificates are verified."}
    (HERE / "ms_residue_orbits.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()
