"""Small exact collection controls; no presentation census search."""
import json
import unittest

import exchange_collect as collect
import exchange_templates
import lemma11
import search
import verify


def hidden_commutator():
    return search.normalize(((1, 2, 2, -1, -2), (1, 1, 2, -1, -2)))


def higher_rank_plant():
    rows = [(1, 2)]
    for other, depth in ((2, 3), (3, 3), (4, 2)):
        commutator = (1,) * depth + (other,) + (-1,) * depth + (-other,)
        rows.append(commutator * 2 + (other,))
    return search.normalize(tuple(rows))


class CollectionChecks(unittest.TestCase):
    def replay(self, before, events):
        current = before
        for event in json.loads(json.dumps(events)):
            self.assertEqual(tuple(tuple(w) for w in event['before']), current)
            current = verify.verify_event(event, known_trivial=True)
        return current

    def test_hidden_plant_uses_one_helper_and_solves(self):
        before = hidden_commutator()
        after, events, cost, metadata = collect.build(before, 1, 1000)
        self.assertEqual((len(after), search.length(after), metadata['helper_count'], cost), (3, 10, 1, 69))
        self.assertEqual(self.replay(before, events), after)
        candidates, used = collect.probe(before, 1000, axis=1)
        self.assertEqual(candidates[0][0], ())
        self.assertEqual(self.replay(before, candidates[0][1]), ())
        self.assertEqual(used, 85)

    def test_rank11_detour_preserves_all_eight_definitions(self):
        before = higher_rank_plant()
        after, events, cost, metadata = collect.build(before, 1, 1000)
        self.assertEqual((len(before), search.length(before), len(after), search.length(after), cost),
                         (4, 27, 12, 79, 269))
        self.assertEqual(len(events), 8)
        for i, event in enumerate(events):
            self.assertEqual(len(event['before']), 4 + i)
            self.assertEqual(len(event['rows']), 4 + i)
        candidates, used = collect.probe(before, 1000, axis=1)
        after, events = candidates[0]
        self.assertEqual(after, ())
        self.assertEqual(self.replay(before, events), ())
        self.assertEqual(events[0]['collection_immediate_descent']['start_rank'], 11)
        self.assertEqual(used, 612)

    def test_signed_conjugate_chains_exactly_expand(self):
        axis, other = 101, 10**20
        names, definitions, images = collect.dictionary((axis, other), axis, {(1, other): 4, (-1, other): 4})
        for height in range(-4, 5):
            for sign in (1, -1):
                template = collect.conjugate_template(sign * other, height, names)
                power = ((axis,) if height >= 0 else (-axis,)) * abs(height)
                expected = search.reduced(power + (sign * other,) + search.inverse(power))
                self.assertEqual(exchange_templates._expand(template, images), expected)
                self.assertEqual(len(template), 2 ** abs(height))
        self.assertEqual(len(definitions), 8)

    def test_left_right_frames_are_distinct_and_exact(self):
        before = hidden_commutator()
        endpoints = []
        for direction in ('left', 'right'):
            after, events, cost, metadata = collect.build(before, 1, 1000, direction=direction)
            self.assertEqual(self.replay(before, events), after)
            endpoints.append((len(after), search.length(after)))
        self.assertEqual(endpoints, [(3, 10), (4, 19)])

    def test_budget_preflight_and_no_nilpotent_truncation(self):
        before = hidden_commutator()
        _, _, required, _ = collect.build(before, 1, 1000)
        after, events, cost, metadata = collect.build(before, 1, required - 1)
        self.assertIsNone(after)
        self.assertEqual((events, cost, metadata['status']), ([], 1, 'work_budget_before_collection'))
        high = search.normalize(((1, 2), (1,) * 100 + (2, 2) + (-1,) * 100 + (-2,)))
        after, events, cost, metadata = collect.build(high, 1, 1000)
        self.assertIsNone(after)
        self.assertEqual(events, [])
        self.assertEqual(cost, 1)
        for budget in (0, 1, 3, 20, 60, 100):
            candidates, used = collect.probe(before, budget)
            self.assertLessEqual(used, budget)
            for after, events in candidates:
                self.assertEqual(self.replay(before, events), after)

    def test_gapped_rank_four_input_and_stage_work(self):
        relabel = {1: 101, 2: 307, 3: 10**20, 4: 10**20 + 9}
        before = search.normalize(tuple(tuple(relabel[abs(x)] if x > 0 else -relabel[abs(x)] for x in row)
                                        for row in higher_rank_plant()))
        after, events, cost, metadata = collect.build(before, 101, 1000)
        self.assertEqual(len(after), 12)
        self.assertEqual(sum(e['charged_units'] for e in events), cost)
        self.assertEqual(self.replay(before, events), after)


if __name__ == '__main__':
    unittest.main()
