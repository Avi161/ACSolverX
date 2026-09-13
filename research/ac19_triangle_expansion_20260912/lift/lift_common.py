"""Shared helpers: lift rank-2 AC paths into triangle systems.

Every rank-2 state along a saved solution path is triangulated with the exact
``high_rank_triangles.triangulate`` used by the fixed-rank experiment.  We then
record the rank, the fully expanded dictionary (definitions as words in x, y),
and how expensive the state is to encode under the *initial* dictionary alone.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PANEL_DIR = HERE.parent
ROOT = PANEL_DIR.parent.parent
U124 = ROOT / 'research/u124_rank_3h_20260912'
HIGH_RANK = ROOT / 'research/u124_high_rank_ac_20260912'
PRIOR = ROOT / 'research/rank_unbounded_20260912'
sys.path[:0] = [str(ROOT), str(HIGH_RANK), str(U124), str(PRIOR)]

import search                                    # noqa: E402
from high_rank_triangles import excess, triangulate   # noqa: E402
import high_rank_ac_search as engine             # noqa: E402
from experiments.search.greedy_baseline import (  # noqa: E402
    moves_to_states, str_to_move)

LABELS = {'x': 1, 'y': 2}
HARD_PANEL = PANEL_DIR / 'hard_solved_panel.jsonl'
S20_PANEL = PANEL_DIR / 's20_panel_records.jsonl'
EASY_PANEL = PANEL_DIR / 'easy_control_panel.jsonl'
AC19 = ROOT / 'data/AC19_extended_aut_min.csv'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse_word(value):
    return tuple(LABELS[c.lower()] * (1 if c.islower() else -1) for c in value)


def render_word(word):
    out = []
    for x in word:
        letter = 'x' if abs(x) == 1 else ('y' if abs(x) == 2 else 'g%d' % abs(x))
        out.append(letter if x > 0 else letter.upper())
    return ''.join(out) or '1'


def state_words(pair):
    return search.normalize((parse_word(pair[0]), parse_word(pair[1])))


# --------------------------------------------------------------------------
# dictionaries


def expand_definitions(events):
    """Fully expand each ``defining_compression`` helper into a word in x, y."""
    expansion = {1: (1,), 2: (2,)}
    words = []
    for event in events:
        helper = event['helper']
        built = ()
        for letter in event['defining']:
            piece = expansion[abs(letter)]
            built += piece if letter > 0 else search.inverse(piece)
        built = search.reduced(built)
        if len(built) < 2:
            raise AssertionError('definition collapsed below length two')
        expansion[helper] = built
        words.append(built)
    return words, expansion


def definition_key(word):
    """Definitions are words, not relators: canonical only up to inversion."""
    return render_word(min(word, search.inverse(word)))


def lift_state(pair, budget=1000):
    """Triangulate one rank-2 state; return the full record."""
    words = state_words(pair)
    tri, events, units = triangulate(words, budget=budget)
    if excess(tri):
        raise AssertionError('triangularization incomplete for ' + str(pair))
    definitions, _ = expand_definitions(events)
    return {
        'words': words,
        'total_length': search.length(words),
        'max_relator_length': max(map(len, words)),
        'triangle_words': tri,
        'rank': len(tri),
        'definition_count': len(events),
        'triangles': sum(len(w) == 3 for w in tri),
        'charged_units': units,
        'definitions': [render_word(w) for w in definitions],
        'definition_keys': [definition_key(w) for w in definitions],
        'definition_lengths': [len(w) for w in definitions],
    }


# --------------------------------------------------------------------------
# encoding a rank-2 state under a FIXED dictionary


def build_table(definition_words):
    """Token table: every definition and its inverse, longest first."""
    table = []
    for index, word in enumerate(definition_words):
        table.append((word, index))
        inverted = search.inverse(word)
        if inverted != word:
            table.append((inverted, index))
    table.sort(key=lambda item: (-len(item[0]), item[1]))
    return table


def greedy_encode_length(word, table):
    """Greedy longest-match tokenization of a linear word."""
    i, tokens = 0, 0
    n = len(word)
    while i < n:
        for piece, _ in table:
            size = len(piece)
            if size <= n - i and word[i:i + size] == piece:
                i += size
                break
        else:
            i += 1
        tokens += 1
    return tokens


def optimal_encode_length(word, table):
    """Minimum number of tokens over ALL tokenizations (DP lower bound)."""
    n = len(word)
    best = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        value = 1 + best[i + 1]
        for piece, _ in table:
            size = len(piece)
            if size <= n - i and word[i:i + size] == piece:
                candidate = 1 + best[i + size]
                if candidate < value:
                    value = candidate
        best[i] = value
    return best[0]


def encode_relator(word, table):
    """Cyclic word: take the best rotation for each measure."""
    if not word:
        return {'greedy': 0, 'optimal': 0}
    rotations = [word[k:] + word[:k] for k in range(len(word))]
    return {
        'greedy': min(greedy_encode_length(r, table) for r in rotations),
        'optimal': min(optimal_encode_length(r, table) for r in rotations),
    }


def encode_state(words, table):
    per = [encode_relator(word, table) for word in words]
    return {
        'greedy_max': max(p['greedy'] for p in per),
        'optimal_max': max(p['optimal'] for p in per),
        'greedy_per_relator': [p['greedy'] for p in per],
        'optimal_per_relator': [p['optimal'] for p in per],
    }


# --------------------------------------------------------------------------
# path loading


def load_hard_paths():
    """Both saved certificates for each of the four hard-but-solved rows."""
    greedy_rows = [json.loads(line) for line in HARD_PANEL.read_text().splitlines()]
    s20_rows = [json.loads(line) for line in S20_PANEL.read_text().splitlines()]
    s20_by_name = {row['name']: row for row in s20_rows}
    out = []
    for row in greedy_rows:
        name = row['name']
        replayed = moves_to_states(row['r1'], row['r2'],
                                   [str_to_move(m) for m in row['path_moves']])
        if replayed != row['path'] or replayed[-1] != ['Y', 'X']:
            raise AssertionError(name + ': greedy certificate replay failed')
        out.append({'name': name, 'arm': 'greedy', 'states': replayed})
        record = s20_by_name[name]
        s20_states = moves_to_states(row['r1'], row['r2'],
                                     [str_to_move(m) for m in record['path_moves']])
        if s20_states[0] != [row['r1'], row['r2']] and \
                state_words(s20_states[0]) != state_words([row['r1'], row['r2']]):
            raise AssertionError(name + ': s20 start differs from census')
        if s20_states[-1] != ['Y', 'X']:
            raise AssertionError(name + ': s20 certificate did not reach the trivial pair')
        out.append({'name': name, 'arm': 's20_mk2', 'states': s20_states})
    return out


def load_easy_paths(count=3):
    """The ``count`` longest easy-control paths (the most demanding controls)."""
    rows = [json.loads(line) for line in EASY_PANEL.read_text().splitlines()]
    rows = [row for row in rows if row['solved']]
    rows.sort(key=lambda row: (-len(row['states']), row['index']))
    chosen = rows[:count]
    out = []
    for row in chosen:
        states = row['states']
        if states[-1] != ['Y', 'X']:
            raise AssertionError(row['name'] + ': easy certificate did not reach ["Y","X"]')
        if states[0] != row['pair']:
            raise AssertionError(row['name'] + ': easy path does not start at the census pair')
        out.append({'name': row['name'], 'arm': 'easy_plain_s20', 'states': states})
    return out


# --------------------------------------------------------------------------
# path-level analysis


def analyse_path(entry):
    steps = []
    for index, pair in enumerate(entry['states']):
        record = lift_state(pair)
        record['step'] = index
        record['state'] = list(pair)
        steps.append(record)

    initial_defs, _ = expand_definitions(
        triangulate(state_words(entry['states'][0]))[1])
    table = build_table(initial_defs)
    initial_keys = set(steps[0]['definition_keys'])

    for index, record in enumerate(steps):
        keys = set(record['definition_keys'])
        previous = set(steps[index - 1]['definition_keys']) if index else keys
        record['shared_with_previous'] = len(keys & previous)
        record['dictionary_changed'] = bool(index and keys != previous)
        record['shared_with_initial'] = len(keys & initial_keys)
        record['new_vs_initial'] = len(keys - initial_keys)
        record.update({'encoded_' + k: v for k, v in
                       encode_state(record['words'], table).items()})
        record['triangle_words'] = [render_word(w) for w in record['triangle_words']]
        record['words'] = [render_word(w) for w in record['words']]

    changes = sum(record['dictionary_changed'] for record in steps[1:])
    runs, current = [], 1
    for record in steps[1:]:
        if record['dictionary_changed']:
            runs.append(current)
            current = 1
        else:
            current += 1
    runs.append(current)
    distinct = set()
    for record in steps:
        distinct.update(record['definition_keys'])
    ranks = [record['rank'] for record in steps]
    optimal_caps = [record['encoded_optimal_max'] for record in steps]
    greedy_caps = [record['encoded_greedy_max'] for record in steps]

    def first_exit(cap):
        for record in steps:
            if record['encoded_optimal_max'] > cap:
                return record['step']
        return None

    # The terminal states of a solved path are trivial (["Y","X"]), so the
    # minimum over the whole path is degenerate.  "Interior" excludes the
    # endgame: states whose rank-two total length is already at most six.
    interior = [record for record in steps if record['total_length'] > 6]
    interior_caps = [record['encoded_optimal_max'] for record in interior]

    return {
        'name': entry['name'],
        'arm': entry['arm'],
        'steps': steps,
        'summary': {
            'path_states': len(steps),
            'path_moves': len(steps) - 1,
            'max_rank2_total_length': max(r['total_length'] for r in steps),
            'max_rank2_relator_length': max(r['max_relator_length'] for r in steps),
            'dictionary_change_steps': changes,
            'dictionary_change_fraction': changes / max(1, len(steps) - 1),
            'longest_unchanged_run': max(runs),
            'distinct_definitions_on_path': len(distinct),
            'min_rank': min(ranks),
            'max_rank': max(ranks),
            'mean_rank': sum(ranks) / len(ranks),
            'initial_rank': ranks[0],
            'initial_dictionary_size': len(initial_keys),
            'min_over_path_encoded_optimal_max': min(optimal_caps),
            'max_over_path_encoded_optimal_max': max(optimal_caps),
            'min_over_path_encoded_greedy_max': min(greedy_caps),
            'max_over_path_encoded_greedy_max': max(greedy_caps),
            'steps_encodable_within_cap_4': sum(c <= 4 for c in optimal_caps),
            'steps_encodable_within_cap_5': sum(c <= 5 for c in optimal_caps),
            'steps_encodable_within_cap_6': sum(c <= 6 for c in optimal_caps),
            'steps_exceeding_cap_6': sum(c > 6 for c in optimal_caps),
            'fraction_exceeding_cap_6': sum(c > 6 for c in optimal_caps) / len(steps),
            'first_step_exceeding_cap_4': first_exit(4),
            'first_step_exceeding_cap_5': first_exit(5),
            'first_step_exceeding_cap_6': first_exit(6),
            'interior_states': len(interior),
            'min_interior_encoded_optimal_max': min(interior_caps) if interior_caps else None,
            'max_interior_encoded_optimal_max': max(interior_caps) if interior_caps else None,
            'steps_above_initial_rank': sum(r > ranks[0] for r in ranks),
            'steps_below_initial_rank': sum(r < ranks[0] for r in ranks),
            'steps_at_initial_rank': sum(r == ranks[0] for r in ranks),
            'rank_change_steps': sum(a != b for a, b in zip(ranks, ranks[1:])),
            'rank_change_fraction': sum(a != b for a, b in zip(ranks, ranks[1:])) / max(1, len(steps) - 1),
            'mean_shared_with_initial': sum(r['shared_with_initial'] for r in steps) / len(steps),
            'steps_with_dictionary_equal_to_initial': sum(
                set(r['definition_keys']) == initial_keys for r in steps),
        },
    }


# --------------------------------------------------------------------------
# gradient flatness


def gradient_report(pair, relator_cap=4):
    words = state_words(pair)
    tri, _, _ = triangulate(words)
    parent = engine.structural_score(tri)
    emitted, attempted = engine.generate(tri, relator_cap)
    scores = [engine.structural_score(endpoint) for endpoint, _ in emitted]
    counts = Counter(scores)
    better = sum(score < parent for score in scores)
    equal = sum(score == parent for score in scores)
    worse = sum(score > parent for score in scores)
    best = min(scores) if scores else None
    component_values = [len({score[i] for score in scores}) for i in range(len(parent))]
    lengths = Counter(sum(map(len, endpoint)) for endpoint, _ in emitted)
    return {
        'rank': len(tri),
        'parent_score': list(parent),
        'parent_total_length': sum(map(len, tri)),
        'attempted_products': attempted,
        'neighbours': len(emitted),
        'distinct_scores': len(counts),
        'best_score': list(best) if best else None,
        'best_score_multiplicity': counts[best] if best else 0,
        'best_score_tie_fraction': (counts[best] / len(scores)) if scores else 0.0,
        'largest_score_class': max(counts.values()) if counts else 0,
        'largest_class_fraction': (max(counts.values()) / len(scores)) if scores else 0.0,
        'tie_fraction_all': 1 - len(counts) / len(scores) if scores else 0.0,
        'strictly_better': better,
        'equal_to_parent': equal,
        'strictly_worse': worse,
        'distinct_values_per_component': component_values,
        'component_names': ['has_excess', 'excess', 'max_length', 'n_long',
                            'neg_units', 'neg_pairs', 'neg_shared_digrams',
                            'repeated', 'min_degree', 'total_length', 'rank'],
        'neighbour_total_length_histogram': {str(k): v for k, v in sorted(lengths.items())},
        'neighbours_all_triangle': sum(
            all(len(w) <= 3 for w in endpoint) for endpoint, _ in emitted),
        'constant_components': [name for name, count in zip(
            ['has_excess', 'excess', 'max_length', 'n_long', 'neg_units',
             'neg_pairs', 'neg_shared_digrams', 'repeated', 'min_degree',
             'total_length', 'rank'], component_values) if count == 1],
    }
