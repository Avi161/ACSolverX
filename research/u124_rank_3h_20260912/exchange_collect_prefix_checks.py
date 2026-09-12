"""Focused first-helper identities, useful saved prefix and reserve controls."""
import json
from pathlib import Path
import unittest

import exchange_collect_checks as plants
import exchange_collect_prefix as prefix
import exchange_templates
import search
import verify


class PrefixChecks(unittest.TestCase):
    def replay(self, before, events):
        current = before
        for event in json.loads(json.dumps(events)):
            self.assertEqual(tuple(tuple(w) for w in event['before']), current)
            current = verify.verify_event(event, known_trivial=True)
        return current

    def test_all_signed_linear_formulas(self):
        for q in (101, -101):
            for b in (307, -307):
                images = {101: (101,), 307: (307,), 1000: (q, b, -q, -b)}
                for n in range(-4, 5):
                    for letter in (b, -b):
                        template = prefix.conjugate(letter, n, q, b, 1000)
                        expected = search.reduced(prefix.power(q, n) + (letter,) + prefix.power(q, -n))
                        self.assertEqual(exchange_templates._expand(template, images), expected)
                        self.assertLessEqual(len(template), 3 * abs(n) + 1)

    def test_saved_aca43_useful_prefix_without_later_definitions(self):
        source = Path(__file__).with_name('collector_remaining113.json')
        data = json.loads(source.read_text())
        record = next(r for r in data['rows'] if r['name'] == 'aca_43')
        stage = next(e for e in record['events'] if e['kind'] == 'defining_template_compression')
        before = tuple(tuple(w) for w in stage['before'])
        after, event, used = prefix.compress(before, 3, 2, 1000, mode='one_direction')
        self.assertEqual((search.length(before), len(after), search.length(after), used), (18, 3, 16, 8))
        self.assertEqual(len(event['helpers']), 1)
        self.assertEqual(self.replay(before, [event]), after)

    def test_hidden_plant_shorter_dictionary_and_complete_paths(self):
        before = plants.hidden_commutator()
        candidates, used = prefix.probe(before, 1000)
        self.assertEqual(candidates[0][0], ())
        self.assertTrue(any(len(after) == 3 and search.length(after) == 9 for after, _ in candidates))
        for after, events in candidates:
            self.assertEqual(self.replay(before, events), after)
        self.assertLessEqual(used, 1000)

    def test_large_height_has_linear_exact_template(self):
        q, b, z = 101, 10**20, 10**20 + 1
        mapping = {q: (q,), b: (b,), z: (q, b, -q, -b)}
        for height in (-100, 100):
            template = prefix.conjugate(b, height, q, b, z)
            self.assertLessEqual(len(template), 301)
            self.assertEqual(exchange_templates._expand(template, mapping),
                             prefix.power(q, height) + (b,) + prefix.power(q, -height))

    def test_work_accounting_and_tiny_budgets(self):
        before = plants.hidden_commutator()
        for budget in (0, 1, 7, 8, 12, 30, 100):
            candidates, used = prefix.probe(before, budget)
            self.assertLessEqual(used, budget)
            for after, events in candidates:
                self.assertEqual(self.replay(before, events), after)
        _, event, used = prefix.compress(before, -1, 2, 1000, mode='all_heights')
        self.assertEqual(sum(event['work_counts'].values()), used)
        self.assertEqual(event['work_counts']['prefix_row_frame_checks'], 4)

    def test_arbitrary_rank_signed_axes_and_gapped_ids(self):
        mapping = {1: 101, 2: 307, 3: 10**20, 4: 10**20 + 9}
        before = search.normalize(tuple(tuple(mapping[abs(t)] if t > 0 else -mapping[abs(t)] for t in w)
                                        for w in plants.higher_rank_plant()))
        for mode in ('all_heights', 'one_direction'):
            after, event, used = prefix.compress(before, -101, -307, 1000, mode=mode)
            self.assertEqual(len(after), 5)
            self.assertEqual(self.replay(before, [event]), after)
            self.assertLess(used, 1000)


if __name__ == '__main__':
    unittest.main()
