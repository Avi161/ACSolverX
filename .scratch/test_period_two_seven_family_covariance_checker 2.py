from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / ".scratch/period_two_seven_family_covariance_checker.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("tested_seven_family_checker", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError(CHECKER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    checker = load_checker()
    fixed = checker.fixed_tokens()
    assert len(fixed) == 70
    assert checker.raw_parser_guard() == ("tc", "cT")

    rectangle = checker.direct_rectangle(0, 0)
    assert rectangle["token_counts"] == {"a": 150, "b": 84, "f": 96, "g": 168}
    assert rectangle["endpoint_values"] == [
        {"raw": 1, "sort": 1, "phi": 0},
        {"raw": 1, "sort": 0, "phi": 1},
        {"raw": 1, "sort": 1, "phi": 0},
        {"raw": 1, "sort": 0, "phi": 1},
    ]
    assert rectangle["cochain_and_three_bilinears"] == [0, 1, 0, 1]
    assert rectangle["defect"] == 0

    boundary = checker.seven_family_rectangle(1, 0)
    assert boundary["seven_values"] == [0, 0, 1, 0, 0, 1, 0]
    assert boundary["seven_xor"] == 0
    interior = checker.seven_family_rectangle(2, 0)
    assert interior["seven_values"] == [0, 1, 1, 0, 0, 0, 0]
    assert interior["seven_xor"] == 0

    manifest = checker.check_manifest()
    assert len(manifest["cells"]) == 16
    assert all(cell["Q_b0"] == cell["Q_b1"] for cell in manifest["cells"])
    assert all(cell["B_b_g"] == 0 for cell in manifest["cells"])
    assert all(cell["token_counts"] == {"b0": 84, "b1": 84} for cell in manifest["cells"])
    assert all(cell["pair_counts"] == {"b0": 3486, "b1": 3486} for cell in manifest["cells"])
    assert len(manifest["direct_replays"]) == 16
    print("PASS: period-two seven-family covariance checker tests")


if __name__ == "__main__":
    main()
