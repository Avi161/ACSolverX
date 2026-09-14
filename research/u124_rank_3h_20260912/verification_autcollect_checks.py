"""Saved neutral-ambient commutator control and exact cohort replay."""
import json
from pathlib import Path

import verify as v
from verification_consequence_checks import pilot

HERE = Path(__file__).resolve().parent


def main():
    saved = json.loads((HERE / 'exchange_aut_collect_control.json').read_text())
    v.require(saved['source_sha256'] == v.sha(HERE / 'exchange_aut_collect.py'), 'neutral collector source differs')
    cursor = v.words(saved['before'])
    lengths = [v.size(cursor)]
    for index, event in enumerate(saved['events']):
        v.require(v.words(event['before']) == cursor, 'neutral collection prefix differs')
        if 'neutral_ambient_prefix' in event:
            meta = event['neutral_ambient_prefix']
            v.require(meta['source_length'] == lengths[0] and meta['prefix_length'] == v.size(cursor) and meta['prefix_moves'] == index and meta['orbit_exhaustive'] is False, 'neutral prefix metadata differs')
            account = event['neutral_collect_accounting']
            v.require(account['neutral_cut_checks'] <= 96 and account['selected_plans'] <= 3 and account['catalog_checks'] == account['catalogs'] * (2 + 4 * len(cursor)), 'neutral planning counts differ')
        cursor = v.verify_event(event, known_trivial=True)
        lengths.append(v.size(cursor))
    v.require(cursor == v.words(saved['after']) == () and saved['charged_units'] == 455, 'neutral control endpoint differs')
    first, second = pilot('aut_collect_pilot21.json'), pilot('aut_collect_remaining103.json')
    a, b = {r['name'] for r in first['rows']}, {r['name'] for r in second['rows']}
    v.require(not a & b and a | b == set(v.load_baseline()), 'neutral collector cohort differs')
    output = {'status': 'PASS', 'saved_control_lengths': lengths, 'saved_control_charged': 455,
              'exact21_plus103_partition': True, 'pilot': first, 'remainder': second,
              'source_sha256': v.sha(HERE / 'exchange_aut_collect.py'), 'census_reruns': 0,
              'scope': 'Bounded neutral ambient prefix followed by existing fully checked per-row aliases and coupled signed Whitehead cuts; finite plans do not exhaust the neutral orbit. Saved control known triviality follows from its exact terminal empty chain.'}
    (HERE / 'verification_autcollect.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'saved_control_lengths': lengths, 'cohort': 124}))


if __name__ == '__main__':
    main()
