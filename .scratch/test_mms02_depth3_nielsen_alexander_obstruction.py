from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT / ".scratch"
CHECKER = SCRATCH / "mms02_depth3_nielsen_alexander_obstruction.py"


def load_checker():
    if str(SCRATCH) not in sys.path:
        sys.path.insert(0, str(SCRATCH))
    spec = importlib.util.spec_from_file_location(
        "mms02_depth3_nielsen_alexander_obstruction",
        CHECKER,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_complete_depth3_obstruction() -> None:
    checker = load_checker()
    result = checker.verify()

    assert result["nielsen_alphabet_size"] == 18
    assert result["maximum_depth"] == 3
    assert result["nielsen_map_count"] == 2527
    assert result["depth_histogram"] == {
        0: 1,
        1: 18,
        2: 218,
        3: 2290,
    }
    assert result["a5_solution_count"] == 180
    assert result["a5_epimorphism_count"] == 120
    assert result["a5_diagonal_count"] == 60
    assert set(result["a5_solution_stabilizers"]) == {
        checker.IDENTITY_BASIS,
        checker.PSI,
        checker.ETA_Y,
        checker.ETA_Z,
    }
    assert result["candidate_records"][checker.PSI]["remainders"] == (
        (2, -3, 1),
        (-1, 1, 0, -1),
    )
    assert result["candidate_records"][checker.ETA_Y]["remainders"] == (
        (-2,),
        (2, -6, 10, -4),
    )
    assert result["candidate_records"][checker.ETA_Z]["remainders"] == (
        (-2, 2, -2),
        (2, -4, 6, -2),
    )


if __name__ == "__main__":
    test_complete_depth3_obstruction()
    print("PASS: depth-3 Nielsen/Alexander obstruction tests")
