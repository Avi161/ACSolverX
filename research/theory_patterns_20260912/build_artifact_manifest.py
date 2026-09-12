"""Hash the final local research snapshot without loading large JSONL files."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            result.update(block)
    return result.hexdigest()


def main():
    table = json.loads((HERE / "u124_final_table.json").read_text())
    validation = json.loads((HERE / "final_table_validation.json").read_text())
    if table["status"] != "final_snapshot" or validation["status"] != "pass":
        raise ValueError("final table and independent validation required")
    if validation["table_status"] != "final_snapshot" or validation["snapshot_utc"] != table["snapshot_utc"]:
        raise ValueError("validation belongs to a different table snapshot")
    for filename, expected in validation["artifacts_sha256"].items():
        if digest(HERE / filename) != expected:
            raise ValueError("a validated table artifact changed: " + filename)
    excluded = {"ARTIFACT_MANIFEST.json", "ARTIFACT_MANIFEST.json.partial"}
    files = [p for p in HERE.rglob("*") if p.is_file() and p.name not in excluded
             and "__pycache__" not in p.parts and p.suffix not in (".pyc", ".partial")]
    files += [ROOT / "AGENTS.md", ROOT / "two_complement_q3_run.py"]
    records = [{"path": str(p.relative_to(ROOT)), "bytes": p.stat().st_size, "sha256": digest(p)}
               for p in sorted(files)]
    result = {"status": "final_local_artifact_snapshot", "created_utc": datetime.now(timezone.utc).isoformat(),
        "branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip(),
        "base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "file_count": len(records), "total_bytes": sum(row["bytes"] for row in records), "files": records,
        "table_snapshot_utc": table["snapshot_utc"], "table_rows": table["row_count"],
        "solved_ordinary_ids": table["solved_ordinary_ids"], "solved_stable_ids": table["solved_stable_ids"],
        "best_rank2_length_sum": table["best_rank2_length_sum"],
        "best_any_rank_length_sum": table["best_any_rank_length_sum"],
        "scope": "Research snapshot prepared for commit on this branch. Hashes identify original author reports and later audits separately. Large certificate files are retained in compressed form where required. This manifest does not assert every research artifact passed review; FINAL_REPORT and the independent audits identify the accepted conclusions."}
    output = HERE / "ARTIFACT_MANIFEST.json"
    partial = output.with_suffix(".json.partial")
    partial.write_text(json.dumps(result, indent=2)+"\n")
    partial.replace(output)
    print(json.dumps({key:value for key,value in result.items() if key != "files"}, indent=2))


if __name__ == "__main__":
    main()
