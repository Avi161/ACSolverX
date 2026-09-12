"""Small word-identity checks; no census or presentation search."""
from copy import deepcopy
import json
import unittest

from lemma11 import (canonical_witness, generate_removals, normalize_witness,
                     remove_one, replay_removal, single_occurrences)
from search import compress, inverse, length, normalize, reduced
from whitehead import apply


class Lemma11Checks(unittest.TestCase):
    def test_canonical_conjugation_both_signs_and_cyclic_tails(self):
        for core in ((7,), (7, 11, -7, 11), (7, -11, 13), ()):
            for tail in ((), (23,), (23, -29)):
                word = tail + core + inverse(tail)
                after, witness = canonical_witness(word)
                c, sign = witness['conjugator'], witness['sign']
                self.assertEqual(reduced(inverse(c) + (word if sign == 1 else inverse(word)) + c), after)
                self.assertEqual(normalize((word,)), (after,))

    def test_isolating_forms_both_occurrence_signs(self):
        for sign in (-1, 1):
            words = ((7, sign * 101, -11), (101, 13, -101), (-200, 101, 7), (200,))
            after, event = remove_one(words, 0, 101)
            self.assertEqual(event['isolating_word'], (-11, 7) if sign == -1 else (-7, 11))
            self.assertEqual(len(after), 3)
            self.assertEqual([r['input_index'] for r in event['substitutions']], [1, 2, 3])
            self.assertEqual(event['substitutions'][1]['replaced_occurrences'], 1)
            self.assertEqual(replay_removal(json.loads(json.dumps(event))), after)

    def test_singleton_substitutes_both_signs_and_deletes(self):
        after, event = remove_one(((101,), (101, 7, -101, 11)), 0, 101)
        self.assertEqual(event['isolating_word'], ())
        self.assertEqual(after, normalize(((7, 11),)))
        self.assertEqual(event['literal_substitution_length'], 2)

    def test_final_pair_can_be_deleted(self):
        choices, used = generate_removals(((-10**30,),), 1)
        self.assertEqual(used, 1)
        self.assertEqual(choices[0][0], ())
        self.assertEqual(replay_removal(choices[0][1][-1]), ())
        self.assertEqual(generate_removals((), 10, expose_primitives=True), ([], 0))

    def test_no_rank_or_generator_identifier_cap(self):
        ids = tuple(10**20 + 17 * i for i in range(11))
        words = tuple((g,) for g in ids)
        choices, used = generate_removals(words, 11)
        self.assertEqual((len(choices), used), (11, 11))
        for after, path in choices:
            self.assertEqual(len(after), 10)
            self.assertEqual(set(path[-1]['after_generator_ids']), set(ids) - {path[-1]['generator']})
            self.assertEqual(replay_removal(path[-1]), after)

    def test_invalid_arguments_and_nonunique_occurrence(self):
        for value in (-1, True, 2.0):
            with self.assertRaises(ValueError):
                generate_removals(((1,),), value)
        with self.assertRaises(ValueError):
            remove_one(((1, 2, 1), (2,)), 0, 1)
        with self.assertRaises(ValueError):
            generate_removals(((0,),), 0)
        with self.assertRaises(ValueError):
            remove_one(((1, -1), (2,)), 0, 1)

    def test_budget_counts_duplicate_removal_outcomes(self):
        words = ((1, 2), (1,))
        full, used = generate_removals(words, 30)
        self.assertEqual(used, 3)
        self.assertEqual(len(full), 3)
        for budget in range(4):
            candidates, charged = generate_removals(words, budget)
            self.assertEqual(charged, budget)
            self.assertEqual(len(candidates), charged)

    def test_definition_unlocks_old_generator_removal(self):
        start = ((1, 2, 1, 2, 1), (1, 2, 1, 2, 1, 2, 1))
        self.assertTrue(all(not single_occurrences(w) for w in start))
        compressed, definition = compress(normalize(start), (1, 2))
        self.assertEqual((length(start), length(compressed), definition['uses']), (12, 10, 5))
        candidates, charged = generate_removals(compressed, 10)
        self.assertEqual(charged, 5)
        self.assertEqual([length(after) for after, _ in candidates], [5, 6, 7, 9, 12])
        after, path = candidates[0]
        self.assertEqual(after, normalize(((3,), (-3, -3, -3, 2))))
        event = path[-1]
        self.assertEqual(event['generator'], 1)
        self.assertTrue(any(2 in map(abs, row['before']) for row in event['substitutions']))
        self.assertEqual(replay_removal(event), after)

    def test_optional_per_relator_exposure_replays_whole_tuple(self):
        words = ((101, 307, 101, 307, 101), (101, 307, 101, 307, 101, 307, 101))
        self.assertEqual(generate_removals(words, 30), ([], 0))
        candidates, charged = generate_removals(words, 30, expose_primitives=True)
        self.assertEqual(charged, 10)
        self.assertTrue(candidates)
        for after, path in candidates:
            current = tuple(words)
            for event in path:
                self.assertEqual(event['before'], current)
                if event['kind'] == 'ambient_whitehead':
                    self.assertEqual(tuple(apply(w, event['images']) for w in current), event['raw_after'])
                    for g, image in event['images'].items():
                        self.assertEqual(apply(image, event['inverse_images']), (g,))
                    current = normalize(event['raw_after'])
                elif event['kind'] == 'lemma11_removal':
                    current = replay_removal(event)
                else:
                    current, _ = normalize_witness(current)
                self.assertEqual(event['after'], current)
            self.assertEqual(after, current)
            self.assertEqual(length(after), 1)

    def test_failed_cuts_are_charged_and_budget_is_never_exceeded(self):
        for budget in range(12):
            candidates, charged = generate_removals(((1, 1), (2, 2)), budget, expose_primitives=True)
            self.assertEqual(candidates, [])
            self.assertLessEqual(charged, budget)
            self.assertEqual(charged, min(4, max(0, budget - 1)))

    def test_corrupted_word_witness_is_rejected(self):
        _, event = remove_one(((1, 2), (1,)), 0, 1)
        changed = deepcopy(event)
        changed['isolating_word'] = (2,)
        with self.assertRaises(AssertionError):
            replay_removal(changed)
        changed = deepcopy(event)
        changed['substitutions'] = []
        with self.assertRaises(AssertionError):
            replay_removal(changed)


if __name__ == '__main__':
    unittest.main()
