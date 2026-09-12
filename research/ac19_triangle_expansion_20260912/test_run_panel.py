import unittest

import run_panel as subject


class PanelChecks(unittest.TestCase):
    def test_saved_rank_two_certificates(self):
        self.assertEqual(len(subject.load_panel()), 4)

    def test_all_expansions_replay_and_are_triangular(self):
        for row in subject.load_panel():
            original = subject.fixed_engine.search.normalize(
                (subject.parse_word(row['r1']), subject.parse_word(row['r2'])))
            endpoint, events, _ = subject.triangulate(original)
            self.assertEqual(subject.excess(endpoint), 0)
            self.assertEqual(subject.replay_expansion(original, events), endpoint)
            self.assertEqual(len(endpoint), 2 + len(events))
            self.assertTrue(all(event['kind'] == 'defining_compression'
                                for event in events))

    def test_terminal_compiler_preserves_rank(self):
        endpoint = ((1,), (-2, 1))
        compiled = subject.terminal_compile(endpoint)
        self.assertIsNotNone(compiled)
        self.assertEqual(compiled['rank_preserved'], 2)

    def test_fast_phase_retains_an_independently_replayable_path(self):
        initial = subject.fixed_engine.search.normalize(((1, 2, 1), (1,)))
        result = subject.phase(initial, pops=1, cap=4, beam=128,
                               neighborhood='quartic')
        self.assertEqual(
            subject.replay_fixed(initial, result['events']),
            subject.tuple_words(result['endpoint']))


if __name__ == '__main__':
    unittest.main()
