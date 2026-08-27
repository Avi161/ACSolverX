#!/usr/bin/env python3
"""Structural and mutation tests for diagonal pure-P raw certificate."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / ".scratch/period_two_diagonal_pure_p_raw_checker.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("diagonal_pure_p_raw_checker_tested", CHECKER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(CHECKER_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class DiagonalPurePRawCheckerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.checker = load_checker()
        cls.manifest = cls.checker.build_manifest()

    def failures(self, candidate):
        return self.checker.verification_failures(candidate, expected=self.manifest)

    def assert_rejected(self, mutate, prefix: str | None = None) -> None:
        candidate = deepcopy(self.manifest)
        mutate(candidate)
        failures = self.failures(candidate)
        self.assertTrue(failures)
        if prefix is not None:
            self.assertTrue(any(failure.startswith(prefix) for failure in failures), failures)

    def test_clean_manifest_is_structurally_valid(self) -> None:
        self.assertEqual(self.failures(self.manifest), [])
        self.assertEqual(
            self.manifest["scope"]["status"],
            "provisional_pending_independent_replay_and_sol_review",
        )

    def test_hand_derived_five_family_fixture(self) -> None:
        expected = {
            "long_p1": 14,
            "long_pstar": 18,
            "short_w3": 4,
            "short_z3": 6,
            "short_w2": 4,
        }
        self.assertEqual(self.manifest["five_family_traversal_inventory"], expected)
        self.assertEqual(
            Counter(row["family"] for row in self.manifest["provenance"]),
            Counter(expected),
        )
        ids = {row["id"] for row in self.manifest["provenance"]}
        self.assertIn("diag:long_p1:new_segment:W:nu1:P:0:o+1", ids)
        self.assertIn("diag:long_pstar:new_segment:W:nu3:P:17:o+1", ids)
        self.assertIn("diag:short_w3:old:W:nu4:C:18:o+1", ids)
        self.assertIn("diag:short_w3:new:W:nu4:C:19:o+1", ids)
        self.assertIn("diag:short_z3:old:W:nu5:C:18:o+1", ids)
        self.assertIn("diag:short_z3:new:W:nu5:C:20:o+1", ids)
        self.assertIn("diag:short_w2:old:W:nu6:C:19:o+1", ids)
        self.assertIn("diag:short_w2:new:W:nu6:C:20:o+1", ids)

    def test_cells_parser_guard_and_exact_counts(self) -> None:
        self.assertEqual(
            [cell["id"] for cell in self.manifest["cells"]],
            ["e0_n0", "e0_n1", "e0_n2", "e0_nge3"],
        )
        self.assertEqual(
            self.manifest["raw_parser_guard"],
            {"raw_p": "tc", "raw_p_inverse": "cT", "module_parser_p": "t"},
        )
        self.assertEqual(
            self.manifest["source_bindings"]["checker"]["path"],
            ".scratch/period_two_diagonal_pure_p_raw_checker.py",
        )
        self.assertEqual(
            self.manifest["source_bindings"]["tests"]["path"],
            ".scratch/test_period_two_diagonal_pure_p_raw_checker.py",
        )
        self.assertEqual(len(self.manifest["provenance"]), 46)
        self.assertEqual(len(self.manifest["coordinate_schemas"]), 42)
        profile = Counter(row["slot"] for row in self.manifest["coordinate_schemas"])
        self.assertEqual(profile, Counter({2: 9, 3: 15, 4: 18}))
        self.assertEqual(
            {row["family"] for row in self.manifest["coordinate_schemas"]},
            {"long_p1", "long_pstar", "short_w3", "short_z3", "short_w2"},
        )
        for result in self.manifest["cell_results"]:
            self.assertEqual(result["collision"]["active_coordinate_count"], 42)
            self.assertEqual(result["collision"]["active_slot_profile"], {"2": 9, "3": 15, "4": 18})
            self.assertEqual(len(result["tokens"]), 84)
            self.assertEqual(len(result["raw_records"]), 84)
            self.assertEqual(result["computed"]["raw_observable_count"], 84)
            self.assertEqual(result["computed"]["L_slot_zero"], 0)

    def test_unbounded_cell_has_complete_pump_witnesses(self) -> None:
        result = next(
            item for item in self.manifest["cell_results"] if item["cell"]["id"] == "e0_nge3"
        )
        self.assertEqual(sum(len(record["pumps"]) for record in result["raw_records"]), 84)
        for record in result["raw_records"]:
            self.assertEqual(len(record["pumps"]), 1)
            pump = record["pumps"][0]
            self.assertEqual(pump["variable"], "i")
            self.assertGreater(pump["affine_increment"], 0)
            self.assertEqual(
                pump["saturated_boundary"],
                pump["insertion_split"]
                + pump["affine_increment"] * pump["core_length"],
            )
            self.assertTrue(pump["horizon_saturated"])
            self.assertTrue(pump["base_next_observable_signature_equal"])
            self.assertGreater(pump["central_length_slope"], 0)
            self.assertTrue(pump["stable_schema_equality"])
        for bounded in self.manifest["cell_results"][:3]:
            self.assertTrue(
                all(not record["pumps"] for record in bounded["raw_records"])
            )

    def test_cell_xors_are_recomputed_not_theorem_constants(self) -> None:
        for result in self.manifest["cell_results"]:
            expected = sum(
                record["base"]["rho"] for record in result["raw_records"]
            ) % 2
            self.assertEqual(result["computed"]["L_nonzero"], expected)
        self.assertNotIn("expected_L_nonzero", self.manifest["scope"])

    def test_mutated_provenance_rejected(self) -> None:
        self.assert_rejected(
            lambda manifest: manifest["provenance"][0].__setitem__(
                "integral_coefficient",
                manifest["provenance"][0]["integral_coefficient"] + 1,
            ),
            "collision_coefficient",
        )

    def test_mutated_raw_bit_rejected(self) -> None:
        self.assert_rejected(
            lambda manifest: manifest["cell_results"][0]["raw_records"][0]["base"].__setitem__(
                "rho", 1 - manifest["cell_results"][0]["raw_records"][0]["base"]["rho"]
            ),
            "raw_bit",
        )

    def test_mutated_parser_guard_rejected(self) -> None:
        self.assert_rejected(
            lambda manifest: manifest["raw_parser_guard"].__setitem__(
                "module_parser_p", "tc"
            ),
            "raw_parser_guard",
        )

    def test_mutated_raw_signature_rejected(self) -> None:
        def mutate(manifest):
            labels = manifest["cell_results"][0]["raw_records"][0]["base"]["first_half_labels"]
            labels.append("T")

        self.assert_rejected(mutate, "recomputed_manifest_mismatch")

    def test_mutated_support_and_profile_rejected(self) -> None:
        self.assert_rejected(
            lambda manifest: manifest["coordinate_schemas"][0].__setitem__("slot", 99),
            "coordinate_schema_profile",
        )
        self.assert_rejected(
            lambda manifest: manifest["cell_results"][0]["collision"].__setitem__(
                "active_slot_profile", {"2": 8, "3": 16, "4": 18}
            ),
            "active_slot_profile",
        )

    def test_mutated_pump_shield_and_slope_rejected(self) -> None:
        self.assert_rejected(
            lambda manifest: manifest["cell_results"][3]["raw_records"][0]["pumps"][0].__setitem__(
                "insertion_split",
                manifest["cell_results"][3]["raw_records"][0]["pumps"][0]["insertion_split"] + 1,
            ),
            "pump",
        )
        self.assert_rejected(
            lambda manifest: manifest["cell_results"][3]["raw_records"][0]["pumps"][0].__setitem__(
                "central_length_slope", 0
            ),
            "pump",
        )

    def test_mutated_cell_xor_rejected(self) -> None:
        self.assert_rejected(
            lambda manifest: manifest["cell_results"][0]["computed"].__setitem__(
                "L_nonzero", 1 - manifest["cell_results"][0]["computed"]["L_nonzero"]
            ),
            "cell_xor",
        )

    def test_mutated_source_hash_rejected(self) -> None:
        self.assert_rejected(
            lambda manifest: manifest["source_bindings"]["raw"].__setitem__(
                "sha256", "0" * 64
            ),
            "source_hash:raw",
        )


if __name__ == "__main__":
    unittest.main()
