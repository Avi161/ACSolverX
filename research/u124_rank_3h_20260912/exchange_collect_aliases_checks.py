"""Finite Cartesian and complete-tuple min-cut controls for alias choices."""
import itertools
import json
import unittest

import exchange_collect_aliases as aliases
import exchange_collect_checks as plants
import exchange_templates
import search
import verify
import whitehead


class AliasChecks(unittest.TestCase):
    def replay(self, before, events):
        current = before
        for event in json.loads(json.dumps(events)):
            self.assertEqual(tuple(tuple(w) for w in event['before']), current)
            current = verify.verify_event(event, known_trivial=True)
        return current

    def test_cartesian_catalog_retains_neutral_and_longer_aliases(self):
        before = plants.hidden_commutator()
        plan, used = aliases.catalog(before, -1, 2, 1000)
        self.assertEqual([len(rows) for rows in plan['rows']], [2, 3])
        indices = list(aliases.combinations(plan))
        self.assertEqual(set(indices), set(itertools.product(range(2), range(3))))
        self.assertEqual(len(indices), 6)
        lengths = []
        for choice in indices:
            after, event = aliases.assemble(plan, choice)
            self.assertEqual(self.replay(before, [event]), after)
            lengths.append(search.length(after))
        self.assertEqual((min(lengths), max(lengths)), (12, 19))
        self.assertEqual(sum(length == 12 for length in lengths), 2)

    def test_equal_length_aliases_have_distinct_whole_tuple_scores(self):
        plan, _ = aliases.catalog(plants.hidden_commutator(), -1, 2, 1000)
        scores = []
        for choice in ((0, 0), (1, 0)):
            after, event = aliases.assemble(plan, choice)
            endpoint, tail, used, metric = aliases.score(after)
            self.assertEqual(search.length(after), 12)
            self.assertEqual(used, 6)
            self.assertEqual(len(metric['signed_multipliers']), 6)
            self.assertEqual(self.replay(plan['before'], [event] + tail), endpoint)
            scores.append(search.length(endpoint))
        self.assertEqual(scores, [10, 12])

    def test_score_matches_all_small_whitehead_sides(self):
        plan, _ = aliases.catalog(plants.hidden_commutator(), -1, 2, 1000)
        after, _ = aliases.assemble(plan, (0, 0))
        endpoint, _, used, metric = aliases.score(after)
        vertices = sorted({t for word in after for x in word for t in (x, -x)})
        brute = search.length(after)
        evaluations = 0
        for multiplier in vertices:
            movable = [x for x in vertices if abs(x) != abs(multiplier)]
            for mask in range(1 << len(movable)):
                side = {multiplier} | {x for i, x in enumerate(movable) if mask & (1 << i)}
                transformed, _ = whitehead.transform(after, multiplier, side)
                brute = min(brute, search.length(transformed))
                evaluations += 1
        self.assertEqual(evaluations, 96)
        self.assertEqual(search.length(endpoint), brute)

    def test_mixed_modes_and_frames_are_serialized_per_row(self):
        plan, _ = aliases.catalog(plants.hidden_commutator(), -1, 2, 1000)
        after, event = aliases.assemble(plan, (0, 1))
        self.assertEqual([r['prefix_mode'] for r in event['rows']], ['all_heights', 'one_direction'])
        self.assertEqual(event['prefix_mode'], 'per_row')
        self.assertEqual(self.replay(plan['before'], [event]), after)

    def test_complete_probe_and_tiny_budgets(self):
        before = plants.hidden_commutator()
        candidates, used = aliases.probe(before, 1000)
        self.assertEqual(candidates[0][0], ())
        self.assertLessEqual(used, 1000)
        for after, events in candidates:
            self.assertEqual(self.replay(before, events), after)
        for budget in (0, 1, 7, 20, 80):
            candidates, used = aliases.probe(before, budget)
            self.assertLessEqual(used, budget)
            for after, events in candidates:
                self.assertEqual(self.replay(before, events), after)

    def test_gapped_arbitrary_rank_catalog(self):
        names = {1: 101, 2: 307, 3: 10**20, 4: 10**20 + 9}
        before = search.normalize(tuple(tuple(names[abs(x)] if x > 0 else -names[abs(x)] for x in row)
                                        for row in plants.higher_rank_plant()))
        plan, used = aliases.catalog(before, -101, -307, 1000)
        after, event = aliases.assemble(plan, (0,) * 4)
        self.assertEqual(len(after), 5)
        self.assertEqual(self.replay(before, [event]), after)
        endpoint, tail, used, metric = aliases.score(after)
        self.assertEqual(used, 10)
        self.assertEqual(self.replay(before, [event] + tail), endpoint)


if __name__ == '__main__':
    unittest.main()
