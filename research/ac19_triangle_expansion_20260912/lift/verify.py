"""Independently re-derive every headline number in RESULTS.md from the saved JSON.

Recomputes each summary field from the per-step records, re-runs `triangulate`
on a deterministic sample of states, and re-solves the initial-dictionary
encoding with a forward shortest-path formulation (the run used a backward DP).

    python3 research/ac19_triangle_expansion_20260912/lift/verify.py
"""
from __future__ import annotations

import heapq
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE)]

import lift_common as L  # noqa: E402

CHECKS = []


def check(label, got, want):
    ok = got == want
    CHECKS.append((label, ok, got, want))
    if not ok:
        raise AssertionError('%s: got %r want %r' % (label, got, want))


def close(label, got, want, tol=1e-9):
    ok = abs(got - want) <= tol
    CHECKS.append((label, ok, got, want))
    if not ok:
        raise AssertionError('%s: got %r want %r' % (label, got, want))


# --------------------------------------------------------------------------
# independent encoder: forward Dijkstra over letter positions


def independent_encode(word, tokens):
    """Shortest token count for a cyclic word, over every rotation."""
    if not word:
        return 0
    best_overall = None
    for start in range(len(word)):
        rotated = word[start:] + word[:start]
        n = len(rotated)
        dist = {0: 0}
        heap = [(0, 0)]
        best = None
        while heap:
            cost, position = heapq.heappop(heap)
            if cost > dist.get(position, 1 << 30):
                continue
            if position == n:
                best = cost
                break
            for piece in tokens:
                size = len(piece)
                if size <= n - position and rotated[position:position + size] == piece:
                    if cost + 1 < dist.get(position + size, 1 << 30):
                        dist[position + size] = cost + 1
                        heapq.heappush(heap, (cost + 1, position + size))
            if cost + 1 < dist.get(position + 1, 1 << 30):
                dist[position + 1] = cost + 1
                heapq.heappush(heap, (cost + 1, position + 1))
        if best_overall is None or best < best_overall:
            best_overall = best
    return best_overall


def unrender(text):
    out = []
    for c in text:
        base = 1 if c.lower() == 'x' else 2
        out.append(base if c.islower() else -base)
    return tuple(out)


# --------------------------------------------------------------------------


def verify_path_report(report, sample_stride):
    steps = report['steps']
    summary = report['summary']
    tag = '%s/%s' % (report['name'], report['arm'])

    ranks = [record['rank'] for record in steps]
    caps = [record['encoded_optimal_max'] for record in steps]
    check(tag + ' path_states', len(steps), summary['path_states'])
    check(tag + ' min_rank', min(ranks), summary['min_rank'])
    check(tag + ' max_rank', max(ranks), summary['max_rank'])
    close(tag + ' mean_rank', sum(ranks) / len(ranks), summary['mean_rank'])
    check(tag + ' cap_to_follow', max(caps),
          summary['max_over_path_encoded_optimal_max'])
    check(tag + ' steps_exceeding_cap_6', sum(c > 6 for c in caps),
          summary['steps_exceeding_cap_6'])
    close(tag + ' fraction_exceeding_cap_6', sum(c > 6 for c in caps) / len(steps),
          summary['fraction_exceeding_cap_6'])

    # dictionary drift, recomputed from the per-step definition keys
    keysets = [set(record['definition_keys']) for record in steps]
    changes = sum(a != b for a, b in zip(keysets, keysets[1:]))
    check(tag + ' dictionary_change_steps', changes, summary['dictionary_change_steps'])
    close(tag + ' dictionary_change_fraction', changes / (len(steps) - 1),
          summary['dictionary_change_fraction'])
    runs, current = [], 1
    for a, b in zip(keysets, keysets[1:]):
        if a != b:
            runs.append(current)
            current = 1
        else:
            current += 1
    runs.append(current)
    check(tag + ' longest_unchanged_run', max(runs), summary['longest_unchanged_run'])
    check(tag + ' distinct_definitions', len(set().union(*keysets)),
          summary['distinct_definitions_on_path'])
    check(tag + ' shared_with_initial[0]', len(keysets[0]), steps[0]['shared_with_initial'])
    check(tag + ' rank_is_two_plus_defs',
          [2 + record['definition_count'] for record in steps], ranks)

    # re-triangulate and re-encode a deterministic sample of states
    initial_defs, _ = L.expand_definitions(
        L.triangulate(L.state_words(steps[0]['state']))[1])
    tokens = set()
    for word in initial_defs:
        tokens.add(word)
        tokens.add(L.search.inverse(word))
    for record in steps[::sample_stride]:
        words = L.state_words(record['state'])
        tri, events, _ = L.triangulate(words)
        check('%s step %d rank' % (tag, record['step']), len(tri), record['rank'])
        expanded, _ = L.expand_definitions(events)
        check('%s step %d defs' % (tag, record['step']),
              [L.definition_key(w) for w in expanded], record['definition_keys'])
        check('%s step %d L' % (tag, record['step']),
              L.search.length(words), record['total_length'])
        again = max(independent_encode(word, tokens) for word in words)
        check('%s step %d encoded cap' % (tag, record['step']),
              again, record['encoded_optimal_max'])


def verify_gradient(row):
    tag = 'gradient/' + row['name']
    words = L.state_words(row['state'])
    tri, _, _ = L.triangulate(words)
    check(tag + ' rank', len(tri), row['rank'])
    check(tag + ' parent_total_length', sum(map(len, tri)), 3 * len(tri))
    emitted, _ = L.engine.generate(tri, 4)
    check(tag + ' neighbours', len(emitted), row['neighbours'])
    parent = L.engine.structural_score(tri)
    scores = [L.engine.structural_score(endpoint) for endpoint, _ in emitted]
    check(tag + ' strictly_better', sum(s < parent for s in scores), row['strictly_better'])
    check(tag + ' equal_to_parent', sum(s == parent for s in scores), row['equal_to_parent'])
    check(tag + ' strictly_worse', sum(s > parent for s in scores), row['strictly_worse'])
    check(tag + ' distinct_scores', len(set(scores)), row['distinct_scores'])
    close(tag + ' tie_fraction_all', 1 - len(set(scores)) / len(scores),
          row['tie_fraction_all'])
    check(tag + ' all children have length 3r+1',
          {sum(map(len, endpoint)) for endpoint, _ in emitted}, {3 * len(tri) + 1})
    check(tag + ' all_triangle_children',
          sum(all(len(w) <= 3 for w in endpoint) for endpoint, _ in emitted),
          row['neighbours_all_triangle'])
    constant = [name for name, count in zip(row['component_names'],
                                            row['distinct_values_per_component'])
                if count == 1]
    check(tag + ' constant_components', constant, row['constant_components'])


def main():
    hard = json.loads((HERE / 'lift_hard.json').read_text())
    easy = json.loads((HERE / 'lift_easy.json').read_text())
    gradient = json.loads((HERE / 'gradient.json').read_text())

    for name, digest in hard['inputs_sha256'].items():
        path = {'hard_solved_panel.jsonl': L.HARD_PANEL,
                's20_panel_records.jsonl': L.S20_PANEL,
                'easy_control_panel.jsonl': L.EASY_PANEL,
                'AC19_extended_aut_min.csv': L.AC19,
                'high_rank_triangles.py': L.U124 / 'high_rank_triangles.py',
                'high_rank_ac_search.py': L.HIGH_RANK / 'high_rank_ac_search.py',
                'lift_common.py': HERE / 'lift_common.py'}[name]
        check('sha256 ' + name, L.sha(path), digest)

    # the saved certificates still replay to the trivial pair
    for entry in L.load_hard_paths():
        check('certificate %s/%s endpoint' % (entry['name'], entry['arm']),
              entry['states'][-1], ['Y', 'X'])
    for entry in L.load_easy_paths(3):
        check('certificate %s endpoint' % entry['name'], entry['states'][-1], ['Y', 'X'])

    for report in hard['rows']:
        verify_path_report(report, sample_stride=7)
    for report in easy['rows']:
        verify_path_report(report, sample_stride=3)
    for row in gradient['rows']:
        verify_gradient(row)

    hs = [row['summary'] for row in hard['rows']]
    es = [row['summary'] for row in easy['rows']]
    grows = gradient['rows']
    headline = {
        'checks_passed': len(CHECKS),
        'hard_paths': len(hs),
        'easy_paths': len(es),
        'hard_cap_to_follow_path': [min(s['max_over_path_encoded_optimal_max'] for s in hs),
                                    max(s['max_over_path_encoded_optimal_max'] for s in hs)],
        'easy_cap_to_follow_path': [min(s['max_over_path_encoded_optimal_max'] for s in es),
                                    max(s['max_over_path_encoded_optimal_max'] for s in es)],
        'hard_dictionary_drift_fraction': [min(s['dictionary_change_fraction'] for s in hs),
                                           max(s['dictionary_change_fraction'] for s in hs)],
        'easy_dictionary_drift_fraction': [min(s['dictionary_change_fraction'] for s in es),
                                           max(s['dictionary_change_fraction'] for s in es)],
        'longest_unchanged_run_any_path': max(s['longest_unchanged_run'] for s in hs + es),
        'hard_max_triangle_rank': [min(s['max_rank'] for s in hs), max(s['max_rank'] for s in hs)],
        'easy_max_triangle_rank': [min(s['max_rank'] for s in es), max(s['max_rank'] for s in es)],
        'hard_distinct_definitions': [min(s['distinct_definitions_on_path'] for s in hs),
                                      max(s['distinct_definitions_on_path'] for s in hs)],
        'easy_distinct_definitions': [min(s['distinct_definitions_on_path'] for s in es),
                                      max(s['distinct_definitions_on_path'] for s in es)],
        'hard_fraction_outside_cap_6': [min(s['fraction_exceeding_cap_6'] for s in hs),
                                        max(s['fraction_exceeding_cap_6'] for s in hs)],
        'easy_fraction_outside_cap_6': [min(s['fraction_exceeding_cap_6'] for s in es),
                                        max(s['fraction_exceeding_cap_6'] for s in es)],
        'hard_first_step_outside_cap_6': sorted(
            {s['first_step_exceeding_cap_6'] for s in hs}),
        'gradient_total_children': sum(row['neighbours'] for row in grows),
        'gradient_children_not_worse_than_parent': sum(
            row['strictly_better'] + row['equal_to_parent'] for row in grows),
        'gradient_all_triangle_children': sum(row['neighbours_all_triangle'] for row in grows),
        'gradient_tie_fraction': [min(row['tie_fraction_all'] for row in grows),
                                  max(row['tie_fraction_all'] for row in grows)],
        'gradient_constant_components_of_11': [min(len(row['constant_components']) for row in grows),
                                               max(len(row['constant_components']) for row in grows)],
    }
    print(json.dumps(headline, indent=2))
    print('\nALL %d CHECKS PASSED' % len(CHECKS))


if __name__ == '__main__':
    main()
