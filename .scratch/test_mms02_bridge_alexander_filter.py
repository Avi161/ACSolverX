from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / ".scratch/mms02_bridge_alexander_filter.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("mms02_bridge_alexander_filter", CHECKER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_exact_module_and_symmetry_rejections() -> None:
    checker = load_checker()
    result = checker.verify()

    assert result["relators"] == (
        "xzYXyxZXYxyZ",
        "XyxZXYXyxzXYxy",
    )
    assert result["module_generator_relation"] == {
        -1: -1,
        0: 2,
        1: -1,
    }
    assert result["alexander_polynomial"] == (1, -3, 5, -3, 1)

    cyclic = result["cyclic_failure"]
    assert cyclic["images"] == ("xY", "Y", "zy")
    assert cyclic["exponent_sums"] == (0, -1, 2)

    module = result["module_failure"]
    assert module["images"] == ("y", "x", "zyX")
    assert module["psi_A_remainder"] == (2, -3, 1)
    assert module["psi_B_remainder"] == (-1, 1, 0, -1)


if __name__ == "__main__":
    test_exact_module_and_symmetry_rejections()
    print("PASS: MMS02 bridge Alexander-filter tests")
