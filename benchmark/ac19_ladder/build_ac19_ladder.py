"""Build the AC19 ladder: every AC19 presentation in both forms, ten levels, six panels.

The pool is the 72,779 aut-min orbit representatives (graded on record; the grades and
levels are taken verbatim from ``benchmark/ladder/ladder_all.csv``) plus the 131,905
distinct dataset originals that are not themselves a representative
(``sources/originals_panel.csv``), graded here by the plain greedy search and by S20_MK2
through the escalation 1k -> 10k -> 100k -> 1M pops, cap 48, every solve replayed
(``sources/runs/orig_<engine>_b<budget>_c48.jsonl.gz``).

Levels are the ladder's bands of the plain greedy node count ``g``:

    1  g < 1,000              5  100,000 <= g < 316,228     9   greedy unsolved at 10M, S20_MK2 solves
    2  1,000 <= g < 10,000    6  316,228 <= g < 1,000,000   10  greedy and S20_MK2 unsolved at 10M
    3  10,000 <= g < 31,623   7  1,000,000 <= g < E
    4  31,623 <= g < 100,000  8  E <= g <= 10,000,000       E = 2,253,802 (ladder_manifest.json)

An original greedy leaves unsolved at 1,000,000 has g > 1M and no level (7, 8, 9 or 10
would need the 10M runs that need ~50 GB); it is ``level = ungraded`` and off the panels.

Panels ``ladder_{10,20,40,60,100,200}.csv``: k = 1, 2, 4, 6, 10, 20 rows per level, the k
rows S20_MK2 finds hardest (largest S20_MK2 pops; rows S20_MK2 never solved count as
their censoring budget + 1; ties by greedy pops, then name), stored in that order, so a
panel reads top-down from the hardest for S20_MK2.  Nested by construction.  A level with
fewer than k rows gives what it has.

    PYTHONPATH=. python3 -m benchmark.ac19_ladder.build_ac19_ladder [--force]
"""
import argparse
import csv
import gzip
import hashlib
import json
import subprocess
import sys
import time
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from benchmark.ladder.build_ladder import (  # noqa: E402
    EDGES, GREEDY_RUNGS, S20_RUNGS, TOP, TRIVIAL_POPS, Sources, chain, level_of)

HERE = Path(__file__).resolve().parent
LADDER = ROOT / 'benchmark' / 'ladder'
CAP = 48
BUDGETS = (1_000, 10_000, 100_000, 1_000_000)
PER_LEVEL = (1, 2, 4, 6, 10, 20)
N_LEVELS = 10
FIELDS = ['name', 'r1', 'r2', 'level', 'form', 'orbit',
          'greedy_solved', 'greedy_nodes', 'greedy_budget', 'greedy_run', 'greedy_path_length',
          's20_solved', 's20_nodes', 's20_budget', 's20_run', 's20_path_length',
          'start_len', 'solved_by']


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_jsonl(path):
    opener = gzip.open if str(path).endswith('.gz') else open
    with opener(path, 'rt') as fh:
        return [json.loads(line) for line in fh if line.strip()]


def label(budget):
    return f'{budget // 1000}k' if budget < 1_000_000 else f'{budget // 1_000_000}M'


def grade_originals(panel, runs_dir, engine, manifest):
    """Walk the escalation for one engine: {name: (solved, nodes, budget, run_label, path_length)}."""
    out = {}
    expected = {r['name'] for r in panel}
    for budget in BUDGETS:
        if not expected:
            break
        path = runs_dir / f'orig_{engine}_b{budget}_c{CAP}.jsonl.gz'
        if not path.exists():
            path = path.with_suffix('')      # a plain .jsonl is accepted too
        assert path.exists(), f'missing rung {path}'
        recs = read_jsonl(path)
        manifest[path.name] = OrderedDict(rows=len(recs), sha256=sha256(path), bytes=path.stat().st_size)
        names = {r['name'] for r in recs}
        assert names == expected, (path.name, len(names), len(expected), sorted(names ^ expected)[:5])
        assert all(r['engine'] == engine and r['budget'] == budget and r['cap'] == CAP for r in recs), path.name
        assert not any(r.get('error') for r in recs), (path.name, [r['name'] for r in recs if r.get('error')][:5])
        nxt = set()
        for r in recs:
            if r['solved']:
                assert r['verified'], (path.name, r['name'])
                out[r['name']] = (True, int(r['nodes']), budget, label(budget), int(r['path_length']))
            else:
                assert int(r['nodes']) == budget, (path.name, r['name'], r['nodes'])
                nxt.add(r['name'])
        expected = nxt
    for name in expected:      # censored at the last budget run
        out[name] = (False, BUDGETS[-1], BUDGETS[-1], f'unsolved@{label(BUDGETS[-1])}', '')
    return out


def build(runs_dir):
    manifest = OrderedDict()
    E = json.load(open(LADDER / 'ladder_manifest.json'))['E']
    rows = []

    # --- the aut-min representatives: grades and levels verbatim from the ladder pool ---
    ladder_all = LADDER / 'ladder_all.csv'
    manifest['ladder_all.csv'] = OrderedDict(sha256=sha256(ladder_all), bytes=ladder_all.stat().st_size)
    src = Sources()
    autmin_names = [r['name'] for r in src.csv('autmin')]
    g_rec = chain(src, GREEDY_RUNGS, autmin_names, extra_key='unescalated_greedy')
    s_rec = chain(src, S20_RUNGS, autmin_names, extra_key='unescalated_s20')
    manifest['autmin_rungs'] = src.manifest
    n_autmin = 0
    with open(ladder_all, newline='') as fh:
        for r in csv.DictReader(fh):
            if r['form'] != 'autmin':
                continue
            n_autmin += 1
            gp = g_rec[r['name']][5]
            sp = s_rec[r['name']][5]
            rows.append(OrderedDict(
                name=r['name'], r1=r['r1'], r2=r['r2'], level=int(r['level']), form='autmin', orbit=r['orbit'],
                greedy_solved=int(r['greedy_solved']), greedy_nodes=int(r['greedy_nodes']),
                greedy_budget=int(r['greedy_budget']), greedy_run=r['greedy_run'],
                greedy_path_length=_path_length(gp, r['greedy_solved']),
                s20_solved=int(r['s20_solved']), s20_nodes=int(r['s20_nodes']),
                s20_budget=RUN_BUDGET[r['s20_run']], s20_run=r['s20_run'],
                s20_path_length=_path_length(sp, r['s20_solved']),
                start_len=int(r['start_len']), solved_by=r['solved_by']))
    assert n_autmin == 72_779, n_autmin

    # --- the originals: graded here ---
    panel_path = HERE / 'sources' / 'originals_panel.csv'
    manifest['originals_panel.csv'] = OrderedDict(sha256=sha256(panel_path), bytes=panel_path.stat().st_size)
    with open(panel_path, newline='') as fh:
        panel = list(csv.DictReader(fh))
    assert len(panel) == 131_905, len(panel)
    rep_pairs = {(r['r1'], r['r2']) for r in rows}
    assert not any((p['r1'], p['r2']) in rep_pairs for p in panel), 'an original equals a representative'
    manifest['runs'] = OrderedDict()
    g = grade_originals(panel, runs_dir, 'greedy', manifest['runs'])
    s = grade_originals(panel, runs_dir, 's20_mk2', manifest['runs'])
    for p in panel:
        gs, gn, gb, gl, gpl = g[p['name']]
        ss, sn, sb, sl, spl = s[p['name']]
        level = level_of(gn, E) if gs else 'ungraded'
        if gs:
            solved_by = 'greedy@' + gl
        elif ss:
            solved_by = 's20_mk2@' + sl
        else:
            solved_by = 'none'
        rows.append(OrderedDict(
            name=p['name'], r1=p['r1'], r2=p['r2'], level=level, form='original', orbit=p['orbit'],
            greedy_solved=int(gs), greedy_nodes=gn, greedy_budget=gb, greedy_run=gl, greedy_path_length=gpl,
            s20_solved=int(ss), s20_nodes=sn, s20_budget=sb, s20_run=sl, s20_path_length=spl,
            start_len=len(p['r1']) + len(p['r2']), solved_by=solved_by))
    return rows, E, manifest


RUN_BUDGET = {'10k': 10_000, '100k': 100_000, '1M': 1_000_000, '5M': 5_000_000, '10M': 10_000_000,
              'extra100k': 100_000, 'extra1000k': 1_000_000, 'unsolved@10M': 10_000_000}


def _path_length(record, solved_flag):
    """Path length of a solved aut-min row from its grading record ('' when unsolved or
    the record does not carry it)."""
    if record is None or solved_flag != '1':
        return ''
    v = record.get('path_length')
    return int(v) if v not in (None, '') else ''


def s20_cost(row):
    return row['s20_nodes'] if row['s20_solved'] else row['s20_budget'] + 1


def greedy_cost(row):
    return row['greedy_nodes'] if row['greedy_solved'] else row['greedy_budget'] + 1


def rank_key(row):
    """Hardest for S20_MK2 first (censored rows count as budget + 1), then hardest for
    greedy, then name."""
    return (-s20_cost(row), -greedy_cost(row), row['name'])


def eligible(row):
    return row['level'] != 'ungraded' and not (row['greedy_solved'] and row['greedy_nodes'] <= TRIVIAL_POPS)


def level_table(E):
    edges = [0] + EDGES + [E, TOP]
    t = [OrderedDict(level=l, rule=f'{edges[l-1]:,} <= g < {edges[l]:,}' if l < 8 else f'{E:,} <= g <= {TOP:,}')
         for l in range(1, 9)]
    t.append(OrderedDict(level=9, rule='plain greedy unsolved at 10,000,000 pops; S20_MK2 solves it'))
    t.append(OrderedDict(level=10, rule='plain greedy and S20_MK2 both unsolved at 10,000,000 pops'))
    return t


def write_csv(path, rows):
    with open(path, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--runs-dir', type=Path, default=HERE / 'sources' / 'runs')
    ap.add_argument('--out', type=Path, default=HERE)
    ap.add_argument('--force', action='store_true')
    args = ap.parse_args()
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    targets = [out / 'pool.csv', out / 'ungraded.csv', out / 'manifest.json'] + \
              [out / f'ladder_{10 * k}.{ext}' for k in PER_LEVEL for ext in ('csv', 'json')]
    existing = [t for t in targets if t.exists()]
    if existing and not args.force:
        sys.exit(f'{len(existing)} output files exist (e.g. {existing[0]}); pass --force to overwrite')

    t0 = time.time()
    rows, E, sources = build(args.runs_dir)
    names = [r['name'] for r in rows]
    assert len(names) == len(set(names))
    pairs = [(r['r1'], r['r2']) for r in rows]
    assert len(pairs) == len(set(pairs)), 'duplicate presentation in the pool'

    def level_sort(r):
        return (r['level'] if r['level'] != 'ungraded' else 99, r['form'], rank_key(r))
    rows.sort(key=level_sort)
    write_csv(out / 'pool.csv', rows)
    ungraded = [r for r in rows if r['level'] == 'ungraded']
    write_csv(out / 'ungraded.csv', ungraded)

    by_level = defaultdict(list)
    for r in rows:
        if eligible(r):
            by_level[r['level']].append(r)
    ranked = {lvl: sorted(by_level[lvl], key=rank_key) for lvl in range(1, N_LEVELS + 1)}
    populations = OrderedDict()
    for lvl in range(1, N_LEVELS + 1):
        allrows = [r for r in rows if r['level'] == lvl]
        populations[str(lvl)] = OrderedDict(
            total=len(allrows), eligible=len(ranked[lvl]),
            by_form=OrderedDict(sorted(Counter(r['form'] for r in allrows).items())))
    for k in PER_LEVEL:
        chosen, actual = [], OrderedDict()
        for lvl in range(1, N_LEVELS + 1):
            take = ranked[lvl][:k]
            chosen.extend(take)
            actual[str(lvl)] = len(take)
        size = 10 * k
        write_csv(out / f'ladder_{size}.csv', chosen)
        meta = OrderedDict(
            size=len(chosen), requested_size=size, per_level=k, per_level_actual=actual, n_levels=N_LEVELS,
            nested=True, E=E, levels=level_table(E),
            difficulty_variable='level: plain greedy pops g on record; order inside a level: S20_MK2 pops, '
                                'largest first (unsolved rows count as their censoring budget + 1; ties by '
                                'greedy pops, then name)',
            forms=['autmin', 'original'],
            subset=[r['name'] for r in chosen])
        (out / f'ladder_{size}.json').write_text(json.dumps(meta, indent=1) + '\n')

    manifest = OrderedDict(
        built_unix=int(t0),
        git_head=subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True,
                                check=True).stdout.strip(),
        rows=len(rows), by_form=OrderedDict(sorted(Counter(r['form'] for r in rows).items())),
        E=E, levels=level_table(E), populations=populations,
        ungraded=OrderedDict(rows=len(ungraded), rule='original, plain greedy unsolved at 1,000,000 pops',
                             s20_solved=sum(1 for r in ungraded if r['s20_solved'])),
        solved_by=OrderedDict(sorted(Counter(r['solved_by'] for r in rows).items())),
        sizes=[10 * k for k in PER_LEVEL], per_level=list(PER_LEVEL), cap=CAP, budgets=list(BUDGETS),
        sources=sources)
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=1) + '\n')

    print(f'pool {len(rows):,} rows  ({manifest["by_form"]})   E = {E:,}   {time.time() - t0:.1f}s')
    for lvl in range(1, N_LEVELS + 1):
        p = populations[str(lvl)]
        print(f"  level {lvl:2}: {p['total']:6,} rows  ({', '.join(f'{k} {v:,}' for k, v in p['by_form'].items())})")
    print(f'  ungraded (greedy > 1M, off the panels): {len(ungraded):,}')
    for k in PER_LEVEL:
        m = json.load(open(out / f'ladder_{10 * k}.json'))
        print(f"  ladder_{10 * k}: {m['size']} rows  {dict(m['per_level_actual'])}")


if __name__ == '__main__':
    main()
