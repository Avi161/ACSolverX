"""Apply the audited attachment criterion to the 104 rows outside the saved panel."""
import hashlib
import json
from pathlib import Path
import time

from .conjugated_complement_probe import screen, require

HERE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    panel_path = HERE / "conjugated_complement_panel20.json"
    roots_path = HERE / "cyclic_complement_u124.json"
    audit_path = HERE / "complement_audit.json"
    panel = json.loads(panel_path.read_text())
    excluded = {r["name"] for r in panel["rows"]}
    audit = json.loads(audit_path.read_text())
    require(len(excluded) == 20, "exact prior panel")
    require(audit["status"] == "pass" and audit["hashes"][roots_path.name] == digest(roots_path), "audited roots")
    roots = json.loads(roots_path.read_text())["records"]
    cpu, wall = time.process_time(), time.perf_counter()
    rows = []
    with (HERE / "conjugated_complement_remaining104.jsonl").open("w") as output:
        for root in roots:
            if root["name"] in excluded:
                continue
            require(root["complete"] and root["status"] == "no_cyclic_complement", "negative root seed")
            row = {"name": root["name"], **screen(root["pair"], 1000, tuple(map(tuple, root["graph"])))}
            output.write(json.dumps(row, separators=(",", ":")) + "\n")
            output.flush()
            rows.append({k: v for k, v in row.items() if k != "records"})
            time.sleep(0.1)
    require(len(rows) == 104 and len({r["name"] for r in rows}) == 104, "exact remaining104")
    report = {"status": "complete_capped_remaining104_screen", "rows": rows,
              "source_hashes": {p.name: digest(p) for p in (panel_path, roots_path, audit_path, Path(__file__), HERE / "conjugated_complement_probe.py")},
              "per_input_physical_identification_cap": 1000, "prior_panel_reexecuted": False,
              "physical_identifications": sum(r["pairs_checked"] for r in rows),
              "positive_ids": [r["name"] for r in rows if r["positive"]],
              "complete_negative_ids": [r["name"] for r in rows if r["complete"] and not r["positive"]],
              "unknown_ids": [r["name"] for r in rows if not r["complete"]],
              "cpu_seconds": time.process_time() - cpu,
              "wall_seconds_including_cooling": time.perf_counter() - wall}
    (HERE / "conjugated_complement_remaining104.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in ("rows", "unknown_ids")}, indent=2))


if __name__ == "__main__":
    main()
