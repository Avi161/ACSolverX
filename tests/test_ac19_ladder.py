"""Pins on ``benchmark/ac19_ladder/``: the AC19 pool in both forms and its six panels.

These read the shipped CSV/JSON files; they do not rebuild the ladder and run no search.
"""
import csv
import hashlib
import json
import os
from collections import Counter

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, 'benchmark', 'ac19_ladder')
PER_LEVEL = (1, 2, 4, 6, 10, 20)
LEVELS = range(1, 11)
EDGES = [1_000, 10_000, 31_623, 100_000, 316_228, 1_000_000]
TOP = 10_000_000
ALPHABET = set('xXyY')


def _rows(name):
    with open(os.path.join(HERE, name), newline='') as fh:
        return list(csv.DictReader(fh))


def _json(name):
    with open(os.path.join(HERE, name)) as fh:
        return json.load(fh)


pytestmark = pytest.mark.skipif(not os.path.exists(os.path.join(HERE, 'pool.csv')),
                                reason='benchmark/ac19_ladder is not built (pool.csv absent)')


@pytest.fixture(scope='module')
def pool():
    return _rows('pool.csv')


@pytest.fixture(scope='module')
def manifest():
    return _json('manifest.json')


@pytest.fixture(scope='module')
def panels():
    return {10 * k: (_rows(f'ladder_{10 * k}.csv'), _json(f'ladder_{10 * k}.json')) for k in PER_LEVEL}


def _s20_cost(r):
    return int(r['s20_nodes']) if r['s20_solved'] == '1' else int(r['s20_budget']) + 1


def _greedy_cost(r):
    return int(r['greedy_nodes']) if r['greedy_solved'] == '1' else int(r['greedy_budget']) + 1


def test_pool_is_every_ac19_presentation_once(pool, manifest):
    assert len(pool) == 72_779 + 131_905 == manifest['rows']
    assert Counter(r['form'] for r in pool) == {'autmin': 72_779, 'original': 131_905}
    names = [r['name'] for r in pool]
    assert len(names) == len(set(names))
    pairs = {(r['r1'], r['r2']) for r in pool}
    assert len(pairs) == len(pool)                       # no presentation twice, across forms
    for r in pool:
        assert r['r1'] and r['r2'] and set(r['r1'] + r['r2']) <= ALPHABET, r['name']
        assert int(r['start_len']) == len(r['r1']) + len(r['r2']), r['name']
        assert r['name'].startswith('ac19_' if r['form'] == 'autmin' else 'ac19x_'), r['name']


def _label(budget):
    return f'{budget // 1000}k' if budget < 1_000_000 else f'{budget // 1_000_000}M'


def test_levels_follow_the_greedy_bands(pool, manifest):
    E = manifest['E']
    assert 1_000_000 < E < TOP
    edges = [0] + EDGES + [E, TOP + 1]
    ceiling = manifest['max_budget']            # the last rung the originals were escalated to
    for r in pool:
        if r['level'] == 'ungraded':
            assert r['form'] == 'original' and r['greedy_solved'] == '0'
            assert int(r['greedy_budget']) == ceiling and r['greedy_run'] == f'unsolved@{_label(ceiling)}', r['name']
            continue
        lvl = int(r['level'])
        assert lvl in LEVELS, r['name']
        if r['greedy_solved'] == '0':
            assert r['form'] == 'autmin' and int(r['greedy_budget']) == TOP, r['name']
            assert lvl == (9 if r['s20_solved'] == '1' else 10), r['name']
            continue
        g = int(r['greedy_nodes'])
        assert edges[lvl - 1] <= g < edges[lvl], (r['name'], g, lvl)
        assert g <= int(r['greedy_budget']), r['name']
        if r['form'] == 'original':
            assert lvl <= 6 and int(r['greedy_budget']) <= ceiling, r['name']
            assert r['greedy_path_length'] != '' and int(r['greedy_path_length']) >= 1, r['name']


def test_every_solve_has_a_solver_and_the_originals_carry_both_grades(pool, manifest):
    ceiling = manifest['max_budget']
    for r in pool:
        if r['form'] == 'original':
            assert r['greedy_run'] and r['s20_run'], r['name']
            for eng in ('greedy', 's20'):
                if r[f'{eng}_solved'] == '1':
                    assert int(r[f'{eng}_nodes']) <= int(r[f'{eng}_budget']), r['name']
                    assert int(r[f'{eng}_path_length']) >= 1, r['name']
                else:
                    assert int(r[f'{eng}_nodes']) == int(r[f'{eng}_budget']) == ceiling, r['name']
        if r['level'] != 'ungraded':
            assert r['solved_by'] != 'none', r['name']
        else:
            assert r['solved_by'] in ('none',) or r['solved_by'].startswith('s20_mk2@'), r['name']


def test_autmin_rows_match_the_ladder_pool(pool):
    ladder = {r['name']: r for r in csv.DictReader(open(os.path.join(ROOT, 'benchmark', 'ladder', 'ladder_all.csv')))}
    for r in pool:
        if r['form'] != 'autmin':
            continue
        L = ladder[r['name']]
        for k in ('r1', 'r2', 'level', 'orbit', 'greedy_solved', 'greedy_nodes', 'greedy_budget', 'greedy_run',
                  's20_solved', 's20_nodes', 's20_run', 'start_len', 'solved_by'):
            assert r[k] == L[k], (r['name'], k, r[k], L[k])


def test_panels_are_nested_sized_and_hardest_for_s20_first(pool, panels, manifest):
    by_name = {r['name']: r for r in pool}
    eligible = {}
    for r in pool:
        if r['level'] != 'ungraded' and not (r['greedy_solved'] == '1' and int(r['greedy_nodes']) <= 1):
            eligible.setdefault(int(r['level']), []).append(r)
    prev = None
    for k in PER_LEVEL:
        rows, meta = panels[10 * k]
        names = [r['name'] for r in rows]
        assert len(names) == len(set(names)) == meta['size'] == sum(meta['per_level_actual'].values())
        assert meta['requested_size'] == 10 * k and meta['per_level'] == k and meta['nested'] is True
        assert meta['subset'] == names and meta['E'] == manifest['E']
        for r in rows:
            assert r == by_name[r['name']], (k, r['name'])        # pool rows verbatim
            assert r['level'] != 'ungraded' and r['solved_by'] != 'none'
        for lvl in LEVELS:
            picks = [r for r in rows if int(r['level']) == lvl]
            assert len(picks) == min(k, len(eligible.get(lvl, []))) == meta['per_level_actual'][str(lvl)], (k, lvl)
            costs = [(_s20_cost(r), _greedy_cost(r)) for r in picks]
            assert costs == sorted(costs, reverse=True), (k, lvl)    # hardest for S20_MK2 first
            if picks:
                worst = _s20_cost(picks[-1])
                rest = [r for r in eligible[lvl] if r['name'] not in {p['name'] for p in picks}]
                assert all(_s20_cost(r) <= worst for r in rest), (k, lvl)   # nothing harder left behind
        if prev is not None:
            assert set(prev) <= set(names), k
        prev = names


def test_ungraded_file_and_manifest_hashes(pool, manifest):
    ungraded = _rows('ungraded.csv')
    assert [r['name'] for r in ungraded] == [r['name'] for r in pool if r['level'] == 'ungraded']
    assert manifest['ungraded']['rows'] == len(ungraded)
    for key in ('ladder_all.csv', 'originals_panel.csv'):
        rel = {'ladder_all.csv': 'benchmark/ladder/ladder_all.csv',
               'originals_panel.csv': 'benchmark/ac19_ladder/sources/originals_panel.csv'}[key]
        with open(os.path.join(ROOT, rel), 'rb') as fh:
            assert hashlib.sha256(fh.read()).hexdigest() == manifest['sources'][key]['sha256'], key
    for name, src in manifest['sources']['runs'].items():
        path = os.path.join(HERE, 'sources', 'runs', name)
        assert os.path.exists(path), name
        with open(path, 'rb') as fh:
            assert hashlib.sha256(fh.read()).hexdigest() == src['sha256'], name
