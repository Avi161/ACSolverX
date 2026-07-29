#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / ".scratch/period_two_inverse_q_companion_checker.py"


class CompanionCheckerContract(unittest.TestCase):
    def run_summary(self) -> dict[str, object]:
        completed = subprocess.run(
            [sys.executable, str(CHECKER), "--summary-json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=30,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def test_raw_parser_and_exact_record_universe(self) -> None:
        summary = self.run_summary()
        self.assertEqual(summary["raw_round_trip"], {"p": "tc", "p_inverse": "cT"})
        self.assertEqual(summary["records"], 736)
        self.assertEqual(summary["record_ids_unique"], 736)
        self.assertEqual(summary["factor_order"], "m E(Q_<k) q^(d-1) c p^(i+delta) r")

    def test_certificate_has_symbolic_partition_and_all_power_formula(self) -> None:
        summary = self.run_summary()
        self.assertEqual(summary.get("coverage_failures"), 0)
        self.assertEqual(summary.get("overlap_failures"), 0)
        self.assertEqual(summary.get("normal_form_failures"), 0)
        self.assertEqual(summary.get("comparison_failures"), 0)
        self.assertEqual(summary.get("collision_pair_equality_failures"), 0)
        self.assertEqual(summary.get("collision_pair_equality_methods"), {
            "affine_length": 49917,
            "affine_pumped_first_mismatch": 30,
            "canonical_pumped_word_equality": 900,
            "fixed_prefix_first_mismatch": 309,
        })
        self.assertEqual(summary.get("collision_fiber_counts"), {cell: 106 for cell in (
            "a0_n0", "a0_n1", "a0_nge2", "a1_n0", "a1_n1",
            "a1_nge2", "age2_n0", "age2_n1", "age2_nge2",
        )})
        self.assertEqual(summary.get("parity_failures"), 0)
        self.assertIn("theta_formula", summary)


if __name__ == "__main__":
    unittest.main()
