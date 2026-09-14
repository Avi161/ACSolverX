"""Independent Cartesian alias scores, retained gain and forced-exchange controls."""
from copy import deepcopy
from itertools import product
import json
from pathlib import Path

import exchange_collect_aliases as aliases
import theory_conjugate_exchange as exchange
import theory_corridor as corridor
import verify
from verification_consequence_checks import pilot, p

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
need = verify.require


def replay(initial, endpoint, events):
    current = verify.words(initial)
    for event in json.loads(json.dumps(events)):
        need(verify.words(event['before']) == current, 'alias/exchange chain discontinuity')
        current = verify.verify_event(event, known_trivial=True)
    need(current == verify.words(endpoint), 'alias/exchange endpoint differs')


def alias_controls():
    initial = verify.normalized(((1, 2, 2, -1, -2), (1, 1, 2, -1, -2)))
    plan, charged = aliases.catalog(initial, -1, 2, 100)
    need(charged == 10, 'alias catalog work differs')
    combinations = list(aliases.combinations(plan))
    expected = set(product(*(range(len(rows)) for rows in plan['rows'])))
    need(len(combinations) == len(expected) and set(combinations) == expected, 'Cartesian alias enumeration differs')
    lengths, scores, scored_events = [], [], []
    for indices in combinations:
        after, event = aliases.assemble(plan, indices)
        endpoint, tail, charged, score = aliases.score(after)
        event['coupled_whitehead_score'] = score
        replay(initial, endpoint, [event] + tail)
        need(charged == 2 * len(after), 'alias score omits signed multiplier work')
        lengths.append(verify.size(after))
        scores.append({'indices': indices, 'dictionary_length': verify.size(after), 'one_step_length': verify.size(endpoint)})
        scored_events.append(event)
    need(min(lengths) == 12 and max(lengths) == 19 and lengths.count(12) == 2, 'neutral/longer alias controls changed')
    need({row['one_step_length'] for row in scores if row['dictionary_length'] == 12} == {10, 12}, 'equal-length aliases no longer distinguish Whitehead scores')
    state = verify.words(scored_events[0]['after'])
    basis = {abs(x) for w in state for x in w}
    vertices = sorted(basis | {-g for g in basis})
    best, sides = verify.size(state), 0
    for multiplier in vertices:
        movable = [v for v in vertices if abs(v) != abs(multiplier)]
        for bits in product((False, True), repeat=len(movable)):
            side = {multiplier} | {v for v, take in zip(movable, bits) if take}
            mapping = {g: ((g,) if g == abs(multiplier) else ((-multiplier,) if -g in side else ()) + (g,) + ((multiplier,) if g in side else ())) for g in basis}
            after = verify.normalized(tuple(verify.image(w, mapping) for w in state))
            best = min(best, verify.size(after))
            sides += 1
    need(sides == 96 and best == scored_events[0]['coupled_whitehead_score']['one_step_length'], 'complete tiny Whitehead side oracle differs')
    broken = []
    event = json.loads(json.dumps(scored_events[0]))
    bad = deepcopy(event); bad['coupled_whitehead_score']['signed_multipliers'].pop(); broken.append(bad)
    bad = deepcopy(event); bad['coupled_whitehead_score']['signed_multipliers'][0]['capacity'] += 1; broken.append(bad)
    bad = deepcopy(event); bad['coupled_whitehead_score']['one_step_length'] -= 1; broken.append(bad)
    bad = deepcopy(event); bad['alias_indices'][0] = (bad['alias_indices'][0] + 1) % bad['alias_catalog_sizes'][0]; broken.append(bad)
    rejected = 0
    for bad in broken:
        try:
            verify.verify_event(bad, known_trivial=True)
        except AssertionError:
            rejected += 1
    need(rejected == len(broken), 'corrupted alias/score metadata accepted')
    high = 10 ** 24 + 17
    sparse = verify.normalized(tuple(tuple(({1: 101, 2: high}[abs(x)]) * (1 if x > 0 else -1) for x in w) for w in initial) + ((high + 2,), (high + 4,)))
    plan, _ = aliases.catalog(sparse, -101, -high, 100)
    after, event = aliases.assemble(plan, (0,) * 4)
    endpoint, tail, charged, score = aliases.score(after)
    event['coupled_whitehead_score'] = score
    replay(sparse, endpoint, [event] + tail)
    need(charged == 10 and len(after) == 5, 'gapped rank4 alias score differs')
    return {'status': 'PASS', 'complete_cartesian_combinations': len(combinations), 'catalog_sizes': [2, 3],
            'scores': scores, 'exhaustive_signed_Whitehead_sides': sides, 'rejected_corruptions': rejected,
            'gapped_rank4_to5_score_signed_cuts': charged, 'census_searches': 0}


def retained_gain():
    path = HERE / 'collector_aliases_remaining107.json'
    report = json.loads(path.read_text())
    for source, expected in report['hashes'].items():
        need(source.endswith('/verify.py') or verify.sha(HERE.parent / source) == expected, 'alias pilot source changed')
    seeds = []
    for source, expected in report['seed_hashes'].items():
        need(verify.sha(ROOT / source) == expected, 'alias pilot seed changed')
        seeds += json.loads((ROOT / source).read_text())['rows']
    baseline, rows, gains = verify.load_baseline(), [], []
    for row in report['rows']:
        checked = verify.verify_record(row, baseline)
        need(row['best_length'] == checked['endpoint_length'] and row['best_rank'] == checked['endpoint_rank'], 'alias saved endpoint metrics differ')
        need(row['total_units'] == sum(row['costs'].values()) <= row['budget'] == 1000, 'alias budget differs')
        imported = [r for r in seeds if r['name'] == row['name']]
        for old in imported:
            verify.verify_record(old, baseline)
        previous = min([baseline[row['name']]['length']] + [verify.size(e['after']) for r in imported for e in r['events']])
        gain = previous - row['best_length']
        result = {'name': row['name'], 'status': 'PASS', 'preprobe_best_length': previous,
                  'endpoint_length': row['best_length'], 'endpoint_rank': row['best_rank'], 'new_gain_beyond_seeds': gain}
        if gain:
            need(row['name'] == 'aca_5' and previous == 18 and row['best_length'] == 17 and row['best_rank'] == 3, 'unexpected alias gain')
            result.update({'source_key': row['source_key'],
                           'boundary_lengths': [verify.size(row['initial'])] + [verify.size(e['after']) for e in row['events']],
                           'boundary_ranks': [len(row['initial'])] + [len(e['after']) for e in row['events']],
                           'independently_checked_coupled_score': row['events'][0]['coupled_whitehead_score']})
            gains.append(result)
        rows.append(result)
    need(len(gains) == 1, 'missing aca5 alias gain')
    first = pilot('collector_aliases_pilot17.json')
    a, b = {r['name'] for r in first['rows']}, {r['name'] for r in rows}
    need(not a & b and a | b == set(baseline), 'alias 17+107 cohorts do not partition124')
    return {'status': 'PASS', 'rows': rows, 'new_gain': gains[0], 'pilot': first,
            'exact17_plus107_partition': True, 'new_probe_units': report['summary']['total_units'], 'file_sha256': verify.sha(path)}


def exchange_controls():
    cases, forced, uphill, recompressed = [], 0, 0, 0
    high = 10 ** 25 + 19
    for exponent in (-2, 2):
        initial = verify.normalized(((-high,) + p(5, exponent), (-2,) + p(5, 4) + (2,) + p(5, -5), (2,) + p(5, 11)))
        root = next(r for r in corridor.roots(initial) if r.helper == high)
        model = next(m for i in range(3) if i != root.donor and (m := corridor.bs_model(initial, root, i)))
        candidates, charged, audit = exchange.exchange_bridge(initial, root, model, -model['stable'], 2, 200)
        need(charged <= 200 and audit['base_pivots'], 'forced base exchange not exercised')
        for after, events in candidates:
            replay(initial, after, events)
            for i, event in enumerate(events):
                if event['kind'] == 'lemma11_removal' and event['generator'] == root.base:
                    forced += 1
                    uphill += event['length_change'] > 0
                    following = [e for e in events[i + 1:] if e['kind'] == 'defining_compression']
                    forbidden = {tuple(event['isolating_word']), verify.invert(tuple(event['isolating_word']))}
                    need(all(tuple(e['defining']) not in forbidden for e in following), 'forced exchange simply reinstates the exact isolation word')
                    recompressed += bool(following)
                    break
        cases.append({'root_exponent': exponent, 'charged': charged, 'candidate_chains_replayed': len(candidates)})
    need(forced and uphill and recompressed, 'forced/uphill/recompression branches missing')
    budgets = []
    for allowance in (0, 1, 2, 10, 100):
        candidates, charged = exchange.probe(tuple(reversed(initial)), allowance)
        need(charged <= allowance, 'forced exchange budget exceeded')
        for after, events in candidates:
            replay(tuple(reversed(initial)), after, events)
        budgets.append({'allowance': allowance, 'charged': charged, 'candidate_chains_replayed': len(candidates)})
    return {'status': 'PASS', 'signed_high_label_cases': cases, 'chains_with_forced_base_removal': forced,
            'chains_with_uphill_base_removal': uphill, 'chains_with_recompression': recompressed,
            'unnormalized_input_budget_controls': budgets, 'census_searches': 0,
            'known_triviality': 'The companion x*y^11 and the consecutive BS(4,5) donor force y=x=1; all other rows are definitions or singleton relators.'}


def main():
    result = {'status': 'PASS', 'controls': alias_controls(), 'saved_gain_validation': retained_gain(),
              'source_sha256': verify.sha(HERE / 'exchange_collect_aliases.py'), 'verifier_sha256': verify.sha(HERE / 'verify.py')}
    (HERE / 'verification_collection_aliases.json').write_text(json.dumps(result, indent=2) + '\n')
    forced = {'status': 'PASS', 'controls': exchange_controls(), 'pilot': pilot('conjugate_exchange_all33.json'),
              'source_sha256': verify.sha(HERE / 'theory_conjugate_exchange.py'), 'verifier_sha256': verify.sha(HERE / 'verify.py')}
    (HERE / 'verification_conjugate_exchange.json').write_text(json.dumps(forced, indent=2) + '\n')
    print(json.dumps({'alias_controls': result['controls'], 'alias_gain': result['saved_gain_validation']['new_gain'],
                      'forced_exchange_controls': forced['controls'], 'forced_exchange_new_gains': forced['pilot']['new_strict_gains_beyond_available_seeds']}, indent=2))


if __name__ == '__main__':
    main()
