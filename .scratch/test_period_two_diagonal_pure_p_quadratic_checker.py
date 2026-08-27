#!/usr/bin/env python3
"""[unverified] Structural and hostile tests for the pure-P Q certificate."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / ".scratch/period_two_diagonal_pure_p_quadratic_checker.py"


def load_checker():
    spec = importlib.util.spec_from_file_location(
        "period_two_diagonal_pure_p_quadratic_checker_tested", CHECKER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(CHECKER_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class DiagonalPurePQuadraticCheckerTests(unittest.TestCase):
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
            self.assertTrue(
                any(failure.startswith(prefix) for failure in failures), failures
            )

    def test_clean_manifest_is_provisional_and_has_no_expected_q(self) -> None:
        self.assertEqual(self.failures(self.manifest), [])
        self.assertEqual(
            self.manifest["scope"]["status"],
            "provisional_pending_guarded_execution_independent_replay_and_sol_review",
        )
        self.assertNotIn("expected_Q", self.manifest["scope"])

    def test_exact_chord_and_token_inventory(self) -> None:
        self.assertEqual(
            self.manifest["topology"],
            {
                "chord_count": 48,
                "boundary_count": 12,
                "adjacency_count": 36,
                "repeated_label_pair": [
                    "residual_b:boundary:right",
                    "new_component3:junction",
                ],
            },
        )
        for cell in self.manifest["cells"]:
            self.assertEqual(len(cell["tokens"]), 96)
            self.assertEqual(
                Counter(token["slot"] for token in cell["tokens"]),
                Counter({0: 12, 2: 18, 3: 30, 4: 36}),
            )
            self.assertEqual(len(cell["chords"]), 48)
            self.assertEqual(
                Counter(chord["kind"] for chord in cell["chords"]),
                Counter({"boundary": 12, "adjacency": 36}),
            )
            endpoints = [
                endpoint
                for chord in cell["chords"]
                for endpoint in chord["endpoint_ids"]
            ]
            self.assertEqual(
                Counter(endpoints),
                Counter({token["id"]: 1 for token in cell["tokens"]}),
            )

    def test_exact_occurrence_type_multisets(self) -> None:
        for cell in self.manifest["cells"]:
            boundary = Counter(
                tuple(chord["occurrence_type"])
                for chord in cell["chords"]
                if chord["kind"] == "boundary"
            )
            adjacency = Counter(
                tuple(chord["occurrence_type"])
                for chord in cell["chords"]
                if chord["kind"] == "adjacency"
            )
            self.assertEqual(boundary, self.checker.EXPECTED_BOUNDARY_TYPES)
            self.assertEqual(adjacency, self.checker.EXPECTED_ADJACENCY_TYPES)
            self.assertIn((8, 9), boundary)
            self.assertEqual(boundary[(4, 9)], 2)
            self.assertEqual(boundary[(7, 9)], 1)

    def test_ranked_slots_and_common_phase_witnesses(self) -> None:
        for cell in self.manifest["cells"]:
            self.assertEqual(
                {slot: len(rows) for slot, rows in cell["ranked_active_slots"].items()},
                {"2": 9, "3": 15, "4": 18},
            )
            self.assertEqual(len(cell["adjacent_witnesses"]), 39)
            self.assertTrue(
                all(
                    row["common_phase"] and row["comparison"]["order"] == -1
                    for row in cell["adjacent_witnesses"]
                )
            )
            self.assertTrue(cell["slot_zero_order"]["old_before_new"])

    def test_chord_labels_and_sole_nested_repeat(self) -> None:
        expected = sorted(self.checker.REPEATED_LABEL_PAIR)
        for cell in self.manifest["cells"]:
            self.assertTrue(
                all(
                    chord["endpoint_label_equal"]
                    and chord["endpoint_label_comparison"]["order"] == 0
                    for chord in cell["chords"]
                )
            )
            self.assertEqual(len(cell["repeated_chord_labels"]), 1)
            repeated = cell["repeated_chord_labels"][0]
            self.assertEqual(repeated["chords"], expected)
            self.assertTrue(repeated["nested"])

    def test_prefix_sweep_recomputes_q_without_theorem_constant(self) -> None:
        for cell in self.manifest["cells"]:
            sweep = self.checker.prefix_sweep(cell["chords"])
            self.assertEqual(cell["prefix_sweep"], sweep)
            self.assertEqual(len(sweep["rows"]), 48)
            self.assertEqual(cell["computed"]["Q"], sweep["Q"])
            self.assertNotIn("expected_Q", cell["computed"])

    def test_direct_base_replay_covers_full_96_token_kernel(self) -> None:
        for cell in self.manifest["cells"]:
            replay = cell["direct_base_replay"]
            self.assertEqual(replay["direct_token_count"], 96)
            self.assertEqual(replay["production_token_count"], 96)
            self.assertEqual(replay["coordinate_failures"], [])
            self.assertEqual(replay["label_failures"], [])
            self.assertEqual(replay["extra_coordinates"], [])
            self.assertTrue(replay["Q_matches"])
            self.assertEqual(replay["direct_Q"], cell["computed"]["Q"])

    def test_mutated_chord_assignment_rejected(self) -> None:
        self.assert_rejected(
            lambda manifest: manifest["cells"][0]["chords"][0]["endpoint_ids"].__setitem__(
                0, manifest["cells"][0]["chords"][1]["endpoint_ids"][0]
            ),
            "chord_assignment",
        )

    def test_mutated_endpoint_occurrence_rejected(self) -> None:
        self.assert_rejected(
            lambda manifest: manifest["cells"][0]["chords"][0]["endpoint_occurrences"].__setitem__(0, 99),
            "endpoint_occurrence",
        )

    def test_mutated_label_equality_rejected(self) -> None:
        self.assert_rejected(
            lambda manifest: manifest["cells"][0]["chords"][0].__setitem__("endpoint_label_equal", False),
            "label_equality",
        )

    def test_mutated_repeated_label_nesting_rejected(self) -> None:
        self.assert_rejected(
            lambda manifest: manifest["cells"][0]["repeated_chord_labels"][0].__setitem__("nested", False),
            "repeated_label_nesting",
        )

    def test_mutated_rank_rejected(self) -> None:
        def mutate(manifest):
            rows = manifest["cells"][0]["ranked_active_slots"]["2"]
            rows[0], rows[1] = rows[1], rows[0]

        self.assert_rejected(mutate, "rank_adjacency")

    def test_mutated_adjacent_witness_rejected(self) -> None:
        self.assert_rejected(
            lambda manifest: manifest["cells"][0]["adjacent_witnesses"][0].__setitem__("common_phase", False),
            "adjacent_witness",
        )

    def test_mutated_common_primitive_reference_rejected(self) -> None:
        self.assert_rejected(
            lambda manifest: manifest["normal_form"].__setitem__(
                "common_primitive_reference", "wrong"
            ),
            "common_primitive_reference",
        )

    def test_mutated_polarity_rejected(self) -> None:
        self.assert_rejected(
            lambda manifest: manifest["cells"][0]["tokens"][0].__setitem__("polarity", 0),
            "polarity",
        )

    def test_mutated_prefix_lambda_and_q_rejected(self) -> None:
        self.assert_rejected(
            lambda manifest: manifest["cells"][0]["prefix_sweep"]["rows"][0].__setitem__("lambda", 1),
            "prefix_lambda",
        )
        self.assert_rejected(
            lambda manifest: manifest["cells"][0]["computed"].__setitem__(
                "Q", 1 - manifest["cells"][0]["computed"]["Q"]
            ),
            "Q",
        )

    def test_mutated_source_hash_rejected(self) -> None:
        self.assert_rejected(
            lambda manifest: manifest["source_bindings"]["raw_checker"].__setitem__("sha256", "0" * 64),
            "source_hash:raw_checker",
        )

    def test_theory_binding_is_scoped_and_mutations_are_rejected(self) -> None:
        binding = self.manifest["source_bindings"]["theory"]
        self.assertNotIn("sha256", binding)
        self.assertEqual(
            [interval["id"] for interval in binding["intervals"]],
            ["matching_and_order", "certificate_interface"],
        )
        self.assertTrue(
            all(
                interval["byte_length"] > 0 and len(interval["sha256"]) == 64
                for interval in binding["intervals"]
            )
        )
        self.assert_rejected(
            lambda manifest: manifest["source_bindings"]["theory"]["intervals"][0].__setitem__(
                "sha256", "0" * 64
            ),
            "source_interval:theory",
        )


if __name__ == "__main__":
    unittest.main()
