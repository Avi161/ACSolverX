"""Tiny index2/3/10 stable dictionary and rank-exchange controls."""
import json
import unittest

import exchange_schreier as schreier
import exchange_templates
import lemma11
import search


def planted(index):
    k = index - 1
    commutator = (1,) * k + (2,) + (-1,) * k + (-2,)
    return search.normalize(((1, 2), commutator * 4 + (2,)))


class SchreierChecks(unittest.TestCase):
    def test_index2_3_10_complete_stages_and_rank_changes(self):
        for index, start_length, final_rank, final_length in ((2, 15, 3, 12), (3, 21, 4, 15), (10, 63, 11, 50)):
            before = planted(index)
            after, events, cost, metadata = schreier.build(before, 1, index, 1000)
            self.assertEqual(search.length(before), start_length)
            self.assertEqual(len(events), index)
            self.assertEqual(len(after), index + 2)
            self.assertEqual(sum(e['charged_units'] for e in events), cost)
            current = before
            for event in events:
                self.assertEqual(event['before'], current)
                current = exchange_templates.replay(json.loads(json.dumps(event)))
            self.assertEqual(current, after)
            target = next(i for i, w in enumerate(after) if sum(abs(x) == 1 for x in w) == 1)
            endpoint, removal = lemma11.remove_one(after, target, 1)
            self.assertEqual((len(endpoint), search.length(endpoint)), (final_rank, final_length))
            self.assertEqual(lemma11.replay_removal(json.loads(json.dumps(removal))), endpoint)
            self.assertLess(cost + 1, 1000)
            for word in before:
                value = search.reduced(x for t in word for x in ((-2,) if t == 1 else (2,) if t == -1 else (t,)))
                self.assertIn(value, ((), (-2,), (2,)))

    def test_rank11_bridge_using_all_schreier_helper_images(self):
        word = tuple(x for k in range(1, 11) for x in
                     ((1,) * k + (2,) + (-1,) * k + (-2,))) + (2,)
        before = search.normalize(((1, 2), word))
        after, events, cost, _ = schreier.build(before, 1, 10, 1000)
        self.assertEqual((search.length(before), search.length(after), cost), (129, 70, 465))
        target = next(i for i, w in enumerate(after) if sum(abs(x) == 1 for x in w) == 1)
        endpoint, _ = lemma11.remove_one(after, target, 1)
        self.assertEqual((len(endpoint), search.length(endpoint)), (11, 64))
        emitted = {abs(t) for row in events[0]['schreier_rewrites'] for step in row['steps'] for t in step['emitted']}
        self.assertTrue(set(range(3, 13)) <= emitted)

    def test_positive_and_negative_residual_singletons(self):
        for index in (2, 3, 10):
            power, definitions, helpers, images = schreier.dictionary((101, 307), 101, index)
            for sign in (1, -1):
                word = (sign * 101,) * (index + 1) + (307,) + (-sign * 101,) * index
                template, witness = schreier.rewrite(word, 101, index, power, helpers, images)
                self.assertEqual(witness['signed_residue'], sign)
                self.assertEqual(sum(abs(x) == 101 for x in template), 1)
                self.assertEqual(exchange_templates._expand(template, images), word)

    def test_triangular_definitions_retain_every_prior_row(self):
        after, events, _, _ = schreier.build(planted(3), 1, 3, 1000)
        for stage, event in enumerate(events):
            self.assertEqual(len(event['before']), 2 + stage)
            self.assertEqual(len(event['rows']), 2 + stage)
            self.assertEqual(len(event['after']), 3 + stage)
        self.assertEqual(events[2]['defining_words'], ((1, 4, -1),))

    def test_large_requested_index_fails_budget_before_allocation(self):
        after, events, cost, metadata = schreier.build(planted(2), 1, 10**20, 1000)
        self.assertIsNone(after)
        self.assertEqual(events, [])
        self.assertEqual(cost, 1)
        self.assertEqual(metadata['status'], 'work_budget_before_dictionary')

    def test_arbitrary_old_rank_and_integer_gaps(self):
        words = search.normalize(((101, 307), (307,), (10**20,)))
        after, events, cost, metadata = schreier.build(words, 101, 3, 1000)
        self.assertEqual((len(after), metadata['rank_after_one_removal']), (8, 7))
        self.assertEqual(exchange_templates.replay(events[-1]), after)
        self.assertLess(cost, 1000)


if __name__ == '__main__':
    unittest.main()
