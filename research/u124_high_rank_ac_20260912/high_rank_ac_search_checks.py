"""Focused checks for the retained-triangle ordinary-AC search."""
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path[:0] = [str(HERE), str(ROOT / 'research/u124_rank_3h_20260912'),
                str(ROOT / 'research/rank_unbounded_20260912')]

import high_rank_ac_search as subject
import high_rank_ac_search_v2 as subject_v2
import search
import verify


class HighRankAcSearchChecks(unittest.TestCase):
    def test_rotation_product_transport_replays(self):
        words = search.normalize(((-3, 1, 2), (3, -2, -2), (2,)))
        for i in range(len(words)):
            for j in range(len(words)):
                if i == j:
                    continue
                for sign in (1, -1):
                    for k1 in range(len(words[i])):
                        for k2 in range(len(words[j])):
                            after, event = subject.normal_product_event(
                                words, i, j, sign, k1, k2)
                            self.assertEqual(verify.verify_event(event, known_trivial=True), after)

    def test_generate_is_complete_under_declared_cap(self):
        words = search.normalize(((-3, 1, 2), (3, -2, -2), (2,)))
        generated, attempted = subject.generate(words, 4)
        expected = set()
        raw_attempts = 0
        for i, target in enumerate(words):
            for j, donor in enumerate(words):
                if i == j:
                    continue
                for sign in (1, -1):
                    base = donor if sign == 1 else search.inverse(donor)
                    for k1 in range(len(target)):
                        for k2 in range(len(base)):
                            raw_attempts += 1
                            product = search.canonical(target[k1:] + target[:k1]
                                                       + base[k2:] + base[:k2])
                            if product != target and len(product) <= 4:
                                expected.add(search.normalize(words[:i] + (product,) + words[i + 1:]))
        self.assertEqual(attempted, raw_attempts)
        self.assertEqual({state for state, _ in generated}, expected)

    def test_budget_is_strict(self):
        words = search.normalize(((-3, 1, 2), (3, -2, -2), (2,)))
        result = subject.search_row(words, pop_budget=3, relator_cap=4, beam=8)
        self.assertLessEqual(result['heap_pops'], 3)
        current = words
        for event in result['events']:
            self.assertEqual(tuple(map(tuple, event['before'])), current)
            current = verify.verify_event(event, known_trivial=True)
        self.assertEqual(current, result['endpoint'])

    def test_shared_digram_is_exact_one_move_bigon_signal(self):
        words = search.normalize(((1, 2, 3), (-3, -2, 4)))
        self.assertEqual(len(search.canonical((1, 2, 3, -3, -2, 4))), 2)
        self.assertLess(subject.structural_score(words)[6], 0)

    def test_two_donor_triangle_slide_is_generated(self):
        words = search.normalize(((1, 2, 3), (-3, 4, 5), (-6, 2, 4),
                                  (2,), (3,), (4,)))
        macros, _ = subject.generate_short_macros(words)
        expected = search.normalize(((1, 6, 5), (-3, 4, 5), (-6, 2, 4),
                                     (2,), (3,), (4,)))
        path = next(path for endpoint, path in macros if endpoint == expected)
        self.assertEqual(len(path), 2)
        current = words
        for event in path:
            current = verify.verify_event(event, known_trivial=True)
        self.assertEqual(current, expected)

    def test_terminal_generated_on_last_pop_is_reported(self):
        words = search.normalize(((1, 2, 1), (1,)))
        result = subject_v2.search_row(words, pop_budget=1, relator_cap=4,
                                       beam=8, neighborhood='quartic')
        self.assertTrue(result['solved_to_length_at_most_two'])
        self.assertEqual(result['endpoint_score'][0], 0)
        self.assertGreater(result['generated_terminal_states'], 0)


if __name__ == '__main__':
    unittest.main()
