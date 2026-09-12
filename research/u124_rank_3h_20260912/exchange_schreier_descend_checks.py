"""Focused selection, reserve, padding and complete higher-rank descent checks."""
import json
import unittest

import exchange_schreier as schreier
import exchange_schreier_checks as plants
import exchange_schreier_descend as route
import lemma11
import search
import verify


class DescendChecks(unittest.TestCase):
    def replay(self, before, events):
        current = before
        for event in json.loads(json.dumps(events)):
            self.assertEqual(tuple(tuple(w) for w in event['before']), current)
            current = verify.verify_event(event, known_trivial=True)
        return current

    def test_forced_rank3_4_11_detours_solve_with_reserve(self):
        for index, rank in ((2, 3), (3, 4), (10, 11)):
            before = plants.planted(index)
            candidates, cost = route.probe(before, 1000, indices=(index,), axis=1)
            self.assertEqual(len(candidates), 1)
            after, events = candidates[0]
            self.assertEqual(after, ())
            self.assertEqual(self.replay(before, events), after)
            descent = events[0]['schreier_immediate_descent']
            self.assertEqual(descent['start_rank'], rank)
            self.assertEqual(descent['reserved_units'], 400)
            self.assertGreater(descent['whitehead_min_cuts'], 0)
            self.assertLessEqual(cost, 1000)

    def test_select_one_plan_and_preserve_descent_budget(self):
        before = plants.planted(10)
        plan, cost = route.select(before, 1000)
        self.assertEqual((plan['axis'], plan['index']), (1, 5))
        self.assertLessEqual(cost + plan['dictionary_required_units'], 600)
        candidates, used = route.probe(before, 1000)
        after, events = candidates[0]
        self.assertEqual(after, ())
        dictionary = [e for e in events if e['kind'] == 'defining_template_compression']
        self.assertEqual(len(dictionary), 5)
        self.assertEqual(self.replay(before, events), after)
        self.assertLessEqual(used, 1000)

    def test_no_wrap_larger_indices_only_add_removable_padding(self):
        before = plants.planted(3)
        profiles = [route._profile(w, 1) for w in before]
        threshold = max([2] + [p['maximum_height'] + 1 for p in profiles]
                        + [2 * p['exponent'] for p in profiles])
        self.assertEqual(threshold, 3)
        cores = []
        for index in (3, 5, 10):
            after, events, _, _ = schreier.build(before, 1, index, 1000)
            self.assertTrue(all(not any(abs(t) == 3 for t in row['template'])
                                for row in events[0]['schreier_rewrites']))
            for helper in list(range(index + 2, threshold + 2, -1)) + [3]:
                target = next(i for i, w in enumerate(after) if sum(abs(t) == helper for t in w) == 1)
                after, removal = lemma11.remove_one(after, target, helper)
                self.assertEqual(verify.verify_event(removal, known_trivial=True), after)
            cores.append(after)
        self.assertTrue(all(core == cores[0] for core in cores))

    def test_forecast_counts_raw_scanner_tokens(self):
        before = plants.planted(3)
        profiles = [route._profile(w, 1) for w in before]
        for index in (2, 3, 5):
            forecast = route._forecast(profiles, 2, index)
            power, _, helpers, images = schreier.dictionary((1, 2), 1, index)
            for i, word in enumerate(before):
                oriented, _, _ = schreier.orientation(word, 1)
                _, record = schreier.rewrite(oriented, 1, index, power, helpers, images)
                raw = sum(len(s['emitted']) for s in record['steps'])
                raw += int(record['negative_residue_carry']) + abs(record['signed_residue'])
                self.assertEqual(raw, forecast['raw_template_lengths'][i])

    def test_tiny_budgets_and_unbounded_requested_index(self):
        before = plants.planted(2)
        for budget in (0, 1, 3, 20, 60, 100):
            candidates, used = route.probe(before, budget)
            self.assertLessEqual(used, budget)
            for after, events in candidates:
                self.assertEqual(self.replay(before, events), after)
        candidates, used = route.probe(before, 1000, indices=(10**20,), axis=1)
        self.assertEqual(candidates, [])
        self.assertLess(used, 10)


if __name__ == '__main__':
    unittest.main()
