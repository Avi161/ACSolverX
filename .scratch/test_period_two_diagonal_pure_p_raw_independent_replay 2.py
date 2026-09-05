#!/usr/bin/env python3
"""Hostile tests for independent diagonal raw replay."""

from __future__ import annotations

from copy import deepcopy
import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPLAY_PATH = ROOT / ".scratch/period_two_diagonal_pure_p_raw_independent_replay.py"


def load_replay():
    spec = importlib.util.spec_from_file_location(
        "diagonal_pure_p_raw_independent_replay_tested", REPLAY_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(REPLAY_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class IndependentDiagonalRawReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.replay = load_replay()
        cls.manifest = cls.replay.parse_manifest()

    def failures(self, manifest):
        return self.replay.verification_failures(manifest)

    def assert_rejected(self, mutate, prefix: str) -> None:
        candidate = deepcopy(self.manifest)
        mutate(candidate)
        failures = self.failures(candidate)
        self.assertTrue(failures)
        self.assertTrue(any(item.startswith(prefix) for item in failures), failures)

    def test_clean_frozen_manifest(self) -> None:
        self.assertEqual(self.failures(self.manifest), [])
        source = REPLAY_PATH.read_text()
        self.assertNotIn("period_two_diagonal_pure_p_raw_checker.py", source)
        self.assertNotIn("build_manifest(", source)
        bindings = self.replay.replay_bindings()
        self.assertEqual(
            bindings["replay"]["path"],
            ".scratch/period_two_diagonal_pure_p_raw_independent_replay.py",
        )
        self.assertEqual(
            bindings["tests"]["path"],
            ".scratch/test_period_two_diagonal_pure_p_raw_independent_replay.py",
        )

    def test_exact_census(self) -> None:
        self.assertEqual(len(self.manifest["provenance"]), 46)
        self.assertEqual(len(self.manifest["coordinate_schemas"]), 42)
        self.assertEqual(
            [result["collision"]["active_slot_profile"] for result in self.manifest["cell_results"]],
            [{"2": 9, "3": 15, "4": 18}] * 4,
        )
        self.assertEqual(
            [len(result["raw_records"]) for result in self.manifest["cell_results"]],
            [84, 84, 84, 84],
        )
        self.assertEqual(
            [sum(len(record["pumps"]) for record in result["raw_records"]) for result in self.manifest["cell_results"]],
            [0, 0, 0, 84],
        )

    def test_mutated_provenance_rejected(self) -> None:
        self.assert_rejected(
            lambda manifest: manifest["provenance"][0].__setitem__(
                "integral_coefficient",
                manifest["provenance"][0]["integral_coefficient"] + 1,
            ),
            "provenance",
        )

    def test_mutated_factor_order_schema_rejected(self) -> None:
        self.assert_rejected(
            lambda manifest: manifest["schemas"][0]["source"].__setitem__(
                "left", manifest["schemas"][0]["source"]["left"] + "T"
            ),
            "schemas_and_factor_order",
        )

    def test_mutated_fiber_rejected(self) -> None:
        self.assert_rejected(
            lambda manifest: manifest["cell_results"][0]["collision"]["fibers"][0]["members"].append(
                manifest["provenance"][0]["id"]
            ),
            "fibers",
        )
        self.assert_rejected(
            lambda manifest: manifest["cell_results"][0]["collision"]["fibers"][0].__setitem__(
                "integral_coefficient_sum", 99
            ),
            "fibers",
        )

    def test_mutated_observable_rejected(self) -> None:
        self.assert_rejected(
            lambda manifest: manifest["cell_results"][0]["raw_records"][0]["base"].__setitem__(
                "rho", 1 - manifest["cell_results"][0]["raw_records"][0]["base"]["rho"]
            ),
            "raw_observables",
        )
        self.assert_rejected(
            lambda manifest: manifest["cell_results"][0]["raw_records"][0]["base"]["first_half_labels"].append(
                "T"
            ),
            "raw_observables",
        )

    def test_mutated_pump_rejected(self) -> None:
        self.assert_rejected(
            lambda manifest: manifest["cell_results"][3]["raw_records"][0]["pumps"][0].__setitem__(
                "insertion_split",
                manifest["cell_results"][3]["raw_records"][0]["pumps"][0]["insertion_split"] + 1,
            ),
            "raw_observables",
        )
        self.assert_rejected(
            lambda manifest: manifest["cell_results"][3]["raw_records"][0]["pumps"][0].__setitem__(
                "central_length_slope", 0
            ),
            "raw_observables",
        )
        self.assert_rejected(
            lambda manifest: manifest["cell_results"][3]["raw_records"][0]["pumps"][0].__setitem__(
                "stable_schema_equality", False
            ),
            "raw_observables",
        )

    def test_mutated_support_and_xor_rejected(self) -> None:
        self.assert_rejected(
            lambda manifest: manifest["coordinate_schemas"][0].__setitem__("slot", 99),
            "coordinate_catalog",
        )
        self.assert_rejected(
            lambda manifest: manifest["cell_results"][0]["computed"].__setitem__(
                "L_nonzero", 1 - manifest["cell_results"][0]["computed"]["L_nonzero"]
            ),
            "computed",
        )

    def test_theory_section_binding_is_exact_and_scoped(self) -> None:
        binding = self.manifest["source_bindings"]["theory"]
        self.assertEqual(binding, self.replay.theory_section_binding())
        data = self.replay.THEORY_PATH.read_bytes()
        self.assertEqual(
            self.replay.exact_section_record(data),
            self.replay.exact_section_record(data + b"\noutside-bound-section\n"),
        )
        with self.assertRaises(AssertionError):
            self.replay.exact_section_record(data + self.replay.THEORY_SECTION_START)
        with self.assertRaises(AssertionError):
            self.replay.exact_section_record(
                data.replace(self.replay.THEORY_SECTION_START, b"", 1)
            )
        with self.assertRaises(AssertionError):
            self.replay.exact_section_record(
                self.replay.THEORY_SECTION_END
                + b"reversed"
                + self.replay.THEORY_SECTION_START
            )
        for field, value in (
            ("section_sha256", "0" * 64),
            ("start_marker", "wrong start"),
            ("end_marker", "wrong end"),
            ("byte_length", binding["byte_length"] + 1),
        ):
            self.assert_rejected(
                lambda manifest, field=field, value=value: manifest["source_bindings"][
                    "theory"
                ].__setitem__(field, value),
                "source_section:theory",
            )


if __name__ == "__main__":
    unittest.main()
