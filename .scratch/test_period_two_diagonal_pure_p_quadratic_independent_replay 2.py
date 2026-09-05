#!/usr/bin/env python3
"""Hostile tests for the independent diagonal pure-P Q replay."""

from __future__ import annotations

import ast
from collections import Counter
import copy
import importlib.util
from pathlib import Path
import re
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPLAY_PATH = ROOT / ".scratch/period_two_diagonal_pure_p_quadratic_independent_replay.py"


def load_replay():
    spec = importlib.util.spec_from_file_location("independent_diagonal_q_replay_tests", REPLAY_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(REPLAY_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class IndependentReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.replay_module = load_replay()
        cls.baseline = cls.replay_module.build_replay()

    def rejected(self, mutate, expected_fragment: str | None = None) -> None:
        candidate = copy.deepcopy(self.baseline)
        mutate(candidate)
        failures = self.replay_module.verification_failures(candidate, self.baseline)
        self.assertTrue(failures)
        if expected_fragment is not None:
            self.assertTrue(any(expected_fragment in failure for failure in failures), failures)

    def test_clean_baseline_verifies(self) -> None:
        self.assertEqual(
            self.replay_module.verification_failures(
                self.baseline, self.baseline
            ),
            [],
        )

    def test_independence_import_and_call_ban(self) -> None:
        source = REPLAY_PATH.read_text()
        tree = ast.parse(source)
        imported = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        }
        self.assertFalse(any("raw_checker" in name or "quadratic_checker" in name for name in imported))
        loaded_paths = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name) or node.func.id != "load_module":
                continue
            if len(node.args) > 1 and isinstance(node.args[1], ast.Name):
                loaded_paths.append(node.args[1].id)
        self.assertNotIn("PRIMARY_CHECKER_PATH", loaded_paths)
        self.assertNotIn("RAW_CHECKER_PATH", loaded_paths)
        for forbidden in (
            r"raw\.build_schemas\s*\(",
            r"raw\.build_fibers\s*\(",
            r"raw\.build_tokens\s*\(",
            r"raw\.build_manifest\s*\(",
            r"primary\.build_manifest\s*\(",
            r"primary\.verification_failures\s*\(",
        ):
            self.assertIsNone(re.search(forbidden, source))

    def test_no_hardcoded_or_primary_scalar_q(self) -> None:
        source = REPLAY_PATH.read_text()
        self.assertIsNone(re.search(r"[\"']Q[\"']\s*:\s*1(?:\D|$)", source))
        self.assertNotIn('primary_cells[cell_id]["computed"]', source)
        for cell in self.baseline["cells"]:
            projection = self.replay_module.semantic_projection(cell)
            self.assertNotIn("computed", projection)
            self.assertNotIn("Q", projection["prefix_sweep_excluding_Q"])
            direct = cell["direct_base_replay"]
            self.assertEqual(direct["pair_ledger"]["Q"], direct["authoritative_quadratic"])
            self.assertEqual(direct["authoritative_quadratic"], cell["prefix_sweep"]["Q"])

    def test_exact_cells_sources_and_templates(self) -> None:
        self.assertEqual([cell["cell"]["id"] for cell in self.baseline["cells"]], ["e0_n0", "e0_n1", "e0_n2", "e0_nge3"])
        inventory = self.baseline["source_inventory"]
        self.assertEqual(inventory["contexts"], 46)
        self.assertEqual(inventory["distinct_source_rows"], 39)
        self.assertEqual(inventory["family_counts"], self.replay_module.EXPECTED_FAMILIES)
        self.assertEqual((inventory["schema_count"], inventory["template_count"]), (152, 608))
        self.assertEqual(len(inventory["signed_contexts"]), 46)
        self.assertTrue(all(row["p_multiplier"] == 3 and row["base_matches"] and row["next_matches"] and row["i4_matches"] for row in inventory["template_audit"]))
        ge3 = [row for row in inventory["template_audit"] if row["cell"] == "e0_nge3"]
        self.assertTrue(ge3)
        self.assertTrue(all(row["i4_word"] is not None for row in ge3))

    def test_exact_fibers_tokens_ranks_and_chords(self) -> None:
        for cell in self.baseline["cells"]:
            collision = cell["collision"]
            self.assertEqual((collision["fiber_count"], collision["active_count"]), (44, 42))
            self.assertEqual(collision["active_profile"], {"2": 9, "3": 15, "4": 18})
            inactive = [fiber for fiber in collision["fibers"] if not fiber["activity_parity"]]
            self.assertEqual(len(inactive), 2)
            self.assertEqual([len(fiber["members"]) for fiber in inactive], [2, 2])
            self.assertEqual(len(cell["tokens"]), 96)
            self.assertEqual(Counter(token["slot"] for token in cell["tokens"]), Counter({0: 12, 2: 18, 3: 30, 4: 36}))
            self.assertEqual({slot: len(rows) for slot, rows in cell["ranked_active_slots"].items()}, {"2": 9, "3": 15, "4": 18})
            self.assertEqual(len(cell["adjacent_witnesses"]), 39)
            self.assertEqual(Counter(chord["kind"] for chord in cell["chords"]), Counter({"boundary": 12, "adjacency": 36}))
            self.assertEqual(cell["chord_pair_audit"]["pair_count"], 1128)
            self.assertEqual(cell["chord_pair_audit"]["equal_pairs"], [list(self.replay_module.REPEATED_PAIR)])
            self.assertTrue(cell["repeated_chord_labels"][0]["same_label"])
            self.assertTrue(cell["repeated_chord_labels"][0]["nested"])
            self.assertEqual(cell["direct_base_replay"]["pair_ledger"]["pair_count"], 4560)

    def test_mutated_source_identity_sign_offset_and_factor_order_rejected(self) -> None:
        self.rejected(lambda value: value["source_inventory"]["signed_contexts"][0].__setitem__("source_row_id", "mutated"))
        self.rejected(lambda value: value["source_inventory"]["signed_contexts"][0].__setitem__("source_scale", -value["source_inventory"]["signed_contexts"][0]["source_scale"]), "signed_context")
        self.rejected(lambda value: value["source_inventory"]["signed_contexts"][0].__setitem__("incidence_sign", -value["source_inventory"]["signed_contexts"][0]["incidence_sign"]), "signed_context")
        self.rejected(lambda value: value["source_inventory"]["signed_contexts"][0].__setitem__("direction_sign", -value["source_inventory"]["signed_contexts"][0]["direction_sign"]), "signed_context")
        self.rejected(lambda value: value["source_inventory"]["signed_contexts"][0].__setitem__("integral_coefficient", 99), "signed_context")
        self.rejected(lambda value: value["source_inventory"]["signed_contexts"][0].__setitem__("power_offset", 9), "source_offset")
        factor_row = next(index for index, row in enumerate(self.baseline["source_inventory"]["signed_contexts"]) if len(row["factor_order"]) > 1)
        self.rejected(lambda value: value["source_inventory"]["signed_contexts"][factor_row]["factor_order"].__setitem__(slice(0, 2), list(reversed(value["source_inventory"]["signed_contexts"][factor_row]["factor_order"][:2]))))

    def test_mutated_fiber_activity_and_provenance_rejected(self) -> None:
        self.rejected(lambda value: value["cells"][0]["collision"].__setitem__("fiber_count", 43), "collision")
        self.rejected(lambda value: value["cells"][0]["collision"]["fibers"][0].__setitem__("activity_parity", 1 - value["cells"][0]["collision"]["fibers"][0]["activity_parity"]))
        self.rejected(lambda value: value["cells"][0]["collision"]["fibers"][0]["members"].append("fake:member"))
        multi = next(index for index, fiber in enumerate(self.baseline["cells"][0]["collision"]["fibers"]) if fiber["collision_witnesses"])
        self.rejected(lambda value: value["cells"][0]["collision"]["fibers"][multi]["collision_witnesses"][0]["comparison"].__setitem__("order", 1), "collision_witness")

    def test_mutated_primitive_phase_and_template_evidence_rejected(self) -> None:
        self.rejected(lambda value: value["source_inventory"].__setitem__("common_primitive", value["source_inventory"]["common_primitive"] + "a"))
        self.rejected(lambda value: value["source_inventory"].__setitem__("primitive_multiplier", 2), "source_inventory")
        self.rejected(lambda value: value["source_inventory"]["template_audit"][0].__setitem__("p_core", "mutated"))
        self.rejected(lambda value: value["source_inventory"]["template_audit"][0].__setitem__("base_matches", False), "template_audit")
        ge3 = next(index for index, row in enumerate(self.baseline["source_inventory"]["template_audit"]) if row["cell"] == "e0_nge3")
        self.rejected(lambda value: value["source_inventory"]["template_audit"][ge3].__setitem__("i4_matches", False), "template_audit")

    def test_mutated_slotzero_action_and_order_rejected(self) -> None:
        self.rejected(lambda value: value["source_inventory"]["occurrence_actions"][0].__setitem__("action", "mutated"))
        self.rejected(lambda value: value["source_inventory"]["occurrence_actions"][0].__setitem__("polarity", -value["source_inventory"]["occurrence_actions"][0]["polarity"]), "occurrence_actions")
        self.rejected(lambda value: value["cells"][0]["slot_zero_order"].__setitem__("old_before_new", False), "slotzero")
        self.rejected(lambda value: value["cells"][0]["slot_zero_order"]["comparison"].__setitem__("order", 1), "slotzero")
        slotzero = next(index for index, token in enumerate(self.baseline["cells"][0]["tokens"]) if token["slot"] == 0)
        self.rejected(lambda value: value["cells"][0]["tokens"][slotzero].__setitem__("occurrence", 1))

    def test_mutated_endpoint_map_chord_assignment_and_label_rejected(self) -> None:
        self.rejected(lambda value: value["cells"][0]["chords"][0]["endpoint_occurrences"].__setitem__(0, 16))
        self.rejected(lambda value: value["cells"][0]["chords"][0]["endpoint_ids"].__setitem__(0, value["cells"][0]["chords"][1]["endpoint_ids"][0]), "chord_membership")
        self.rejected(lambda value: value["cells"][0]["chords"][0].__setitem__("endpoint_label_equal", False))
        self.rejected(lambda value: value["cells"][0]["chords"][0]["endpoint_label_comparison"].__setitem__("order", 1))
        self.rejected(lambda value: value["cells"][0]["chord_pair_audit"].__setitem__("equal_pairs", []), "label_pair_audit")
        self.rejected(lambda value: value["cells"][0]["chord_pair_audit"].__setitem__("digest_sha256", "0" * 64))
        self.rejected(lambda value: value["cells"][0]["repeated_chord_labels"][0].__setitem__("nested", False), "label_pair_audit")

    def test_mutated_rank_polarity_prefix_and_direct_ledger_rejected(self) -> None:
        self.rejected(lambda value: value["cells"][0]["adjacent_witnesses"][0]["comparison"].__setitem__("order", 0), "rank")
        self.rejected(lambda value: value["cells"][0]["ranked_active_slots"]["2"].reverse())
        self.rejected(lambda value: value["cells"][0]["tokens"][0].__setitem__("polarity", -value["cells"][0]["tokens"][0]["polarity"]), "token_polarity")
        self.rejected(lambda value: value["cells"][0]["prefix_sweep"]["rows"][0].__setitem__("lambda", 1 - value["cells"][0]["prefix_sweep"]["rows"][0]["lambda"]), "prefix")
        self.rejected(lambda value: value["cells"][0]["prefix_sweep"].__setitem__("Q", 1 - value["cells"][0]["prefix_sweep"]["Q"]), "prefix")
        self.rejected(lambda value: value["cells"][0]["direct_base_replay"]["pair_ledger"].__setitem__("pair_count", 4559), "direct")
        self.rejected(lambda value: value["cells"][0]["direct_base_replay"]["pair_ledger"].__setitem__("digest_sha256", "f" * 64))
        self.rejected(lambda value: value["cells"][0]["direct_base_replay"]["pair_ledger"].__setitem__("Q", 1 - value["cells"][0]["direct_base_replay"]["pair_ledger"]["Q"]), "direct")
        self.rejected(lambda value: value["cells"][0]["direct_base_replay"].__setitem__("authoritative_quadratic", 1 - value["cells"][0]["direct_base_replay"]["authoritative_quadratic"]), "direct")
        self.rejected(lambda value: value["cells"][0]["direct_base_replay"].__setitem__("agreement", False), "direct")

    def test_mutated_cell_predicate_and_semantic_projection_rejected(self) -> None:
        self.rejected(lambda value: value["cells"][3]["cell"].__setitem__("id", "e0_nge4"), "cell_predicate")
        self.rejected(lambda value: value["cells"][3]["cell"].__setitem__("base_i", 4))
        self.rejected(lambda value: value["primary_semantic_projection_excluding_Q"][0].__setitem__("matches", False), "primary_semantic_projection")
        self.rejected(lambda value: value["primary_semantic_projection_excluding_Q"][0].__setitem__("digest", "0" * 64))
        self.rejected(lambda value: value["raw_manifest_projection_catalog_and_profile_only"].__setitem__("catalog_digest", "0" * 64))
        self.rejected(lambda value: value["raw_manifest_projection_catalog_and_profile_only"]["profiles"]["e0_n0"].__setitem__("2", 8), "raw_manifest_projection")

    def test_every_source_binding_and_scoped_theory_mutation_rejected(self) -> None:
        for name in self.replay_module.binding_paths():
            with self.subTest(binding=name):
                self.rejected(lambda value, key=name: value["source_bindings"][key].__setitem__("sha256", "0" * 64), f"source_hash:{name}")
        for index in range(len(self.baseline["source_bindings"]["theory_intervals"])):
            with self.subTest(theory_interval=index):
                self.rejected(lambda value, position=index: value["source_bindings"]["theory_intervals"][position].__setitem__("sha256", "0" * 64), "source_hash:theory_intervals")


if __name__ == "__main__":
    unittest.main()
