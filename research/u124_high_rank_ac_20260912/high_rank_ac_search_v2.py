"""Instrumented terminal-safe runner built on the frozen v1 search engine."""
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import high_rank_ac_search as base


_search_row_v1 = base.search_row


def search_row(initial, *, pop_budget=250, relator_cap=4, beam=128,
               neighborhood='short_macros'):
    hits = {'generated_states_with_unit': 0,
            'generated_states_with_bigon': 0,
            'generated_terminal_states': 0}
    original_generate = base.generate
    original_macros = base.generate_short_macros

    def count(children):
        for endpoint, _ in children:
            lengths = tuple(map(len, endpoint))
            hits['generated_states_with_unit'] += any(n == 1 for n in lengths)
            hits['generated_states_with_bigon'] += any(n == 2 for n in lengths)
            hits['generated_terminal_states'] += all(n <= 2 for n in lengths)

    def tracked_generate(words, cap):
        children, attempted = original_generate(words, cap)
        count(children)
        return children, attempted

    def tracked_macros(words):
        children, attempted = original_macros(words)
        count(children)
        return children, attempted

    if neighborhood == 'quartic':
        base.generate = tracked_generate
    else:
        base.generate_short_macros = tracked_macros
    try:
        result = _search_row_v1(initial, pop_budget=pop_budget,
                                relator_cap=relator_cap, beam=beam,
                                neighborhood=neighborhood)
    finally:
        base.generate = original_generate
        base.generate_short_macros = original_macros
    terminal = not base.structural_score(result['endpoint'])[0]
    result['solved_to_length_at_most_two'] = terminal
    result.update(hits)
    return result


def main():
    base.search_row = search_row
    base.__file__ = __file__
    base.main()


if __name__ == '__main__':
    main()
