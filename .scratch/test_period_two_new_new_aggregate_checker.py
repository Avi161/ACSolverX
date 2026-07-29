from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / ".scratch/period_two_new_new_aggregate_checker.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("tested_new_new_checker", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError(CHECKER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    checker = load_checker()
    manifest = checker.check_manifest()
    assert len(manifest["cells"]) == 16
    assert all(item["N"] == 0 for item in manifest["cells"])
    assert all(item["token_counts"]["total"] == 168 for item in manifest["cells"])
    assert all(item["pair_count"] == 14028 for item in manifest["cells"])
    assert len(manifest["direct_replays"]) == 6
    assert not manifest["checks"]["direct_replay_failures"]
    print("PASS: period-two new-new aggregate tests")


if __name__ == "__main__":
    main()
