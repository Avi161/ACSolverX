"""Bounded neutral-prefix and independent coupled-collection replay checks."""
import json
import unittest

import exchange_aut_collect as route
import exchange_collect_checks as plants
import search
import verify


class AutCollectionChecks(unittest.TestCase):
    def replay(self, before, events):
        current = before
        for event in json.loads(json.dumps(events)):
            self.assertEqual(tuple(tuple(w) for w in event['before']), current)
            current = verify.verify_event(event, known_trivial=True)
        return current

    def test_neutral_prefix_then_collector_solves_rank_four_plant(self):
        before = plants.higher_rank_plant()
        candidates, used = route.probe(before, 1000)
        self.assertEqual(candidates[0][0], ())
        self.assertEqual(used, 455)
        for after, events in candidates:
            self.assertEqual(events[0]['kind'], 'ambient_whitehead')
            self.assertEqual(search.length(events[0]['before']), search.length(events[0]['after']))
            self.assertEqual(self.replay(before, events), after)
            event = next(e for e in events if e['kind'] == 'defining_template_compression')
            self.assertEqual(event['neutral_ambient_prefix']['prefix_moves'], 1)
            self.assertFalse(event['neutral_ambient_prefix']['orbit_exhaustive'])
            self.assertLessEqual(event['neutral_collect_accounting']['selected_plans'], 3)

    def test_no_changed_neutral_representative_is_a_valid_empty_result(self):
        candidates, used = route.probe(plants.hidden_commutator(), 1000)
        self.assertEqual(candidates, [])
        self.assertEqual(used, 12)

    def test_tiny_budgets_and_work_reservations(self):
        before = plants.higher_rank_plant()
        for budget in (0, 1, 20, 80, 150, 500):
            candidates, used = route.probe(before, budget)
            self.assertLessEqual(used, budget)
            for after, events in candidates:
                self.assertEqual(self.replay(before, events), after)

    def test_gapped_large_generator_ids(self):
        names = {1: 101, 2: 307, 3: 10**20, 4: 10**20 + 9}
        before = search.normalize(tuple(tuple(names[abs(x)] if x > 0 else -names[abs(x)] for x in row)
                                        for row in plants.higher_rank_plant()))
        candidates, used = route.probe(before, 1000)
        self.assertEqual(candidates[0][0], ())
        self.assertLessEqual(used, 1000)
        self.assertEqual(self.replay(before, candidates[0][1]), ())

    def test_rank_eleven_and_invalid_budgets(self):
        before = search.normalize(tuple((10**20 + 17 * i,) for i in range(1, 12)))
        candidates, used = route.probe(before, 1000)
        self.assertLessEqual(used, 1000)
        for after, events in candidates:
            self.assertEqual(self.replay(before, events), after)
        for budget in (-1, 1001, True):
            with self.assertRaises(ValueError):
                route.probe(before, budget)


if __name__ == '__main__':
    unittest.main()
