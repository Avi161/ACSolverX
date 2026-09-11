"""Build the AC difficulty ladder: ten levels, the full graded pool, nested subsets.

Difficulty is the plain length-ordered greedy search's node count ``g`` on record
(``benchmark/ladder/LADDER.md`` says where every number comes from).  Levels 1-8 are
bands of ``g``; level 9 is "greedy fails at 10,000,000 nodes but S20_MK2 solves it"
(19 AC19 orbits); level 10 is "greedy and S20_MK2 both fail at 10,000,000, only the
cascades solve it" (9 orbits).  Every ladder row is solved by something on record.
The 124 unsolved Miller-Schupp classes are NOT on the ladder: they go to
``unsolved_124.csv`` (as first found) and ``unsolved_all_forms.csv`` (all four forms).

    level 1   g <      1,000            level 5   100,000 <= g <   316,228
    level 2   1,000   <= g <    10,000  level 6   316,228 <= g < 1,000,000
    level 3   10,000  <= g <    31,623  level 7   1,000,000 <= g < E
    level 4   31,623  <= g <   100,000  level 8   E <= g <= 10,000,000

``E`` is the log-median of the AC19 rows in [1M, 10M] so that levels 7 and 8 split
those ~60 rows evenly; it is computed here and written into every subset's JSON.

Inputs are the committed runs.  Three live on research branches that are never
merged (docs/BRANCH_MAP.md); they are read with ``git show <sha>:<path>`` at the
commits pinned below, and the sha256 of every blob goes into ``ladder_manifest.json``.
Nothing is searched here: ``grade_open8.py`` is the one fresh run, kept as a rung file.

Outputs (all under benchmark/ladder/):
    ladder_all.csv                 every graded row (the pool)
    ladder_pairs.csv               the original/representative pairs side by side
    originals_45.csv               the 45 dataset originals, off the panels, runnable on their own
    ladder_{20,40,60,100,200,300,500}.csv + .json   nested subsets, size/10 per level
    ladder_{20,...,300}_s20hard.csv + .json         the S20-hard family (LADDER.md)
    unsolved_124.csv, unsolved_all_forms.csv         the unsolved MS classes, off the ladder
    ladder_manifest.json           sources, hashes, populations, E, notes

    PYTHONPATH=. python3 -m benchmark.ladder.build_ladder [--force]
"""
import argparse
import ast
import csv
import hashlib
import heapq
import io
import json
import math
import subprocess
import sys
import time
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.words import canon_pair, replay_move  # noqa: E402

HERE = Path(__file__).resolve().parent

# --- pinned inputs -------------------------------------------------------------
LEFTOVER = 'dab82a8412b007f23cffd35bee2727d977510de0'   # origin/claude/ac19-leftover-solver-notebook-6yan6d
SUMMER = '9033f13efd06241762b66210c72be3d09b842b6e'     # origin/claude/summer-results-docs-scoring-u6klsb
GREEDY_COMMIT = '525050dd9ed9b9e1ee06cde2d739ad05940c8172'  # the ms640 1M greedy baseline blob
HS = 'results/heuristic_search/'

SOURCES = OrderedDict([
    ('autmin', (None, 'data/AC19_extended_aut_min.csv')),
    ('originals_txt', (None, 'data/AC19_extended.txt')),
    ('greedy10k', (LEFTOVER, HS + 'ac19_autmin_10k/ac19_autmin_10k_greedy_b10000_mrl48.jsonl')),
    ('s20_10k', (LEFTOVER, HS + 'ac19_autmin_10k/ac19_autmin_10k_s20_mk2_b10000_mrl48.jsonl')),
    ('greedy100k', (LEFTOVER, HS + 'hsearch_ac19_hard100k/ac19_unsolved10k_baseline_b100000_mrl48.jsonl')),
    ('s20_100k', (LEFTOVER, HS + 'hsearch_ac19_hard100k/ac19_unsolved10k_s20_mk2_b100000_mrl48.jsonl')),
    ('greedy1m', (LEFTOVER, HS + 'leftovers_1m/leftovers_1m_greedy_b1000000_mrl48.jsonl')),
    ('s20_1m', (LEFTOVER, HS + 'leftovers_1m/leftovers_1m_s20_mk2_b1000000_mrl48.jsonl')),
    ('greedy5m', (LEFTOVER, HS + 'leftovers_5m/leftovers_5m_greedy_b5000000_mrl64.jsonl')),
    ('s20_5m', (LEFTOVER, HS + 'leftovers_5m/leftovers_5m_s20_mk2_b5000000_mrl64.jsonl')),
    ('greedy10m', (LEFTOVER, HS + 'ac19_10m/ac19_10m_greedy_b10000000_mrl64.jsonl')),
    ('s20_10m', (LEFTOVER, HS + 'ac19_10m/ac19_10m_s20_mk2_b10000000_mrl64.jsonl')),
    ('pairs40', (LEFTOVER, HS + 'ac19_autmin_screen/unsolved_10m_orig_baseline.csv')),
    ('orig10m', (LEFTOVER, HS + 'ac19_orig_10m/ac19_orig_10m_greedy_b10000000_mrl64.jsonl')),
    ('open8_orig', (LEFTOVER, HS + 'ac19_orig_cascade/orig_of_cascade_open8.csv')),
    ('open8_greedy', (None, 'benchmark/ladder/sources/open8_greedy_mrl64.jsonl')),
    ('unescalated_greedy', (None, 'benchmark/ladder/sources/unescalated_greedy_mrl48.jsonl')),
    ('unescalated_s20', (None, 'benchmark/ladder/sources/unescalated_s20_mrl48.jsonl')),
    ('s20_ms640_orig', (None, 'benchmark/ladder/sources/s20_ms640_originals_b100000_c48.jsonl')),
    ('ms640_1m', (GREEDY_COMMIT, 'results/greedy_baseline/greedy_1000000_640_mrl24_cyc_all_07_11_26.jsonl')),
    ('ms640_bins', (SUMMER, 'benchmark/difficulty_bins.csv')),
    ('ms640_txt', (None, 'data/ms640_solved.txt')),
    ('ms1190_txt', (None, 'data/1190MS.txt')),
    ('aca_initial', (None, 'data/ms_unsolved_reps/aca_124_initial.csv')),
    ('aca_best', (None, 'data/ms_unsolved_reps/aca_124_best.csv')),
    ('ms_reps261', (None, 'data/ms_unsolved_reps/ms_reps_unsolved.csv')),
    ('notable_unsolved', (None, HS + 'ac19_K3p_notable_full_1k/unsolved.csv')),
    ('final_unsolved', (None, HS + 'ac19_final_policy_full_1k/unsolved.csv')),
])

# greedy rung -> (label, budget, cap); the chain order is the escalation order
GREEDY_RUNGS = [('greedy10k', 'greedy@10k', 10_000, 48),
                ('greedy100k', 'greedy@100k', 100_000, 48),
                ('greedy1m', 'greedy@1M', 1_000_000, 48),
                ('greedy5m', 'greedy@5M', 5_000_000, 64),
                ('greedy10m', 'greedy@10M', 10_000_000, 64)]
S20_RUNGS = [('s20_10k', 's20_mk2@10k', 10_000, 48),
             ('s20_100k', 's20_mk2@100k', 100_000, 48),
             ('s20_1m', 's20_mk2@1M', 1_000_000, 48),
             ('s20_5m', 's20_mk2@5M', 5_000_000, 64),
             ('s20_10m', 's20_mk2@10M', 10_000_000, 64)]

EDGES = [1_000, 10_000, 31_623, 100_000, 316_228, 1_000_000]   # levels 1..6 upper edges
TOP = 10_000_000
TRIVIAL_POPS = 1        # a root that is already (x, y): solved on the first pop, never sampled
SIZES = (20, 40, 60, 100, 200, 300, 500)
S20HARD_SIZES = (20, 40, 60, 100, 200, 300)   # the variant that keeps, per level, the rows hardest for S20_MK2
N_LEVELS = 10
# strata that feed the subsets, in round-robin order; everything else stays in the pool.
# The 45 dataset originals are deliberately NOT a stratum: they are not a sample of the
# 156,762 lines of AC19_extended.txt but the originals of the 33 orbits plain greedy
# cannot solve at 10M, they are cheap (509-52,143 pops, so levels 1-4 only), and giving
# them a third of those levels would put 12-20% of a panel on one narrow family and
# score 21 of 22 orbits twice (once as the original, once as its aut-min partner).
# They stay in the pool, in ladder_pairs.csv and in originals_45.csv -- see LADDER.md.
STRATA = [('ac19', 'autmin'), ('ms640', 'ms_raw')]

FIELDS = ['name', 'r1', 'r2', 'level', 'source', 'form', 'orbit', 'pair_id',
          'greedy_solved', 'greedy_nodes', 'greedy_budget', 'greedy_cap', 'greedy_run',
          's20_solved', 's20_nodes', 's20_run', 'start_len', 'hump', 'hump_source',
          'climb', 'solved_by', 'aut_class']

SYMBOL = {1: 'x', -1: 'X', 2: 'y', -2: 'Y'}


# --- input plumbing ------------------------------------------------------------
class Sources:
    """Read every input once, hash it, remember where it came from."""

    def __init__(self):
        self.manifest = OrderedDict()
        self._cache = {}

    def blob(self, key):
        if key in self._cache:
            return self._cache[key]
        commit, path = SOURCES[key]
        if commit is None:
            data = (ROOT / path).read_bytes()
        else:
            data = subprocess.run(['git', 'show', f'{commit}:{path}'], cwd=ROOT,
                                  capture_output=True, check=True).stdout
        self.manifest[key] = OrderedDict(path=path, commit=commit,
                                         sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
        self._cache[key] = data
        return data

    def text(self, key):
        return self.blob(key).decode()

    def csv(self, key):
        return list(csv.DictReader(io.StringIO(self.text(key))))

    def jsonl(self, key):
        return [json.loads(line) for line in self.text(key).splitlines() if line.strip()]

    def exists(self, key):
        commit, path = SOURCES[key]
        return commit is not None or (ROOT / path).exists()


def decode_padded(line):
    ints = ast.literal_eval(line.strip())
    assert len(ints) == 48, len(ints)
    r1 = ''.join(SYMBOL[v] for v in ints[:24] if v != 0)
    r2 = ''.join(SYMBOL[v] for v in ints[24:] if v != 0)
    return r1, r2


def as_bool(v):
    return v is True or v == 1 or str(v).lower() in ('true', '1')


def by_name(records):
    """{name: record}.  A rung written by resumed lanes can carry, for one name, a few
    'worker died' error records before the real one; those are dropped.  Two complete
    records for one name must agree on (solved, nodes_explored)."""
    out = {}
    for r in records:
        if r.get('error') or r.get('nodes_explored') is None:
            continue
        prev = out.get(r['name'])
        if prev is not None:
            assert (as_bool(prev['solved']), int(prev['nodes_explored'])) == \
                   (as_bool(r['solved']), int(r['nodes_explored'])), f"conflicting duplicates for {r['name']}"
        out[r['name']] = r
    names_with_errors = {r['name'] for r in records if r.get('error') or r.get('nodes_explored') is None}
    missing = names_with_errors - set(out)
    assert not missing, f'rows with only error records: {sorted(missing)[:5]}'
    return out


def peak_minus_start(states):
    totals = [len(a) + len(b) for a, b in states]
    return max(totals) - totals[0]


def replay_moves(r1, r2, moves):
    """Independent replay of a greedy move string list; None if it does not verify."""
    state = canon_pair(r1, r2)
    states = [state]
    for move in moves:
        state = replay_move(state, tuple(int(v) for v in move.split('_')))
        states.append(state)
    a, b = state
    if not (len(a) == len(b) == 1 and a.lower() != b.lower()):
        return None
    return states


# --- grading -------------------------------------------------------------------
def chain(src, rungs, all_names, extra_key=None):
    """Walk an escalation chain; return {name: (solved, nodes, label, budget, cap, record)}.

    Every rung must contain exactly the names the previous rung left unsolved --
    asserted, so a missing or extra row in the record is a build failure, not a
    silently mis-graded row.  The one sanctioned exception is ``extra_key``: the
    rows the record never escalated, graded by ``grade_extra.py`` (label
    ``<arm>@extra<budget>``; a row still unsolved there is censored at that budget
    and reported as ``unsolved@extra``).
    """
    out = {}
    expected = set(all_names)
    extras = by_name(src.jsonl(extra_key)) if extra_key and src.exists(extra_key) else {}
    arm = rungs[0][1].split('@')[0]
    for key, label, budget, cap in rungs:
        recs = by_name(src.jsonl(key))
        missing = expected - set(recs)
        if missing:
            assert missing <= set(extras), (key, 'unescalated rows without a grade_extra record:',
                                            sorted(missing - set(extras))[:5])
            for name in missing:
                r = extras[name]
                assert r['arm'] == arm, (name, r['arm'], arm)
                if as_bool(r['solved']):
                    out[name] = (True, int(r['nodes_explored']), f"{arm}@extra{int(r['budget']) // 1000}k",
                                 int(r['budget']), int(r['max_relator_length']), r)
                else:
                    out[name] = (False, int(r['budget']), 'unsolved@extra', int(r['budget']),
                                 int(r['max_relator_length']), None)
            expected -= missing
        assert set(recs) == expected, (key, len(recs), len(expected),
                                        sorted(set(recs) ^ expected)[:5])
        nxt = set()
        for name, r in recs.items():
            assert int(r['budget']) == budget, (key, name, r['budget'])
            cap_seen = int(r.get('max_relator_length', r.get('mrl')))
            assert cap_seen == cap, (key, name, cap_seen)
            solved = as_bool(r['solved'])
            nodes = int(r['nodes_explored'])
            if solved:
                out[name] = (True, nodes, label, budget, cap, r)
            else:
                assert nodes == budget, (key, name, nodes)
                nxt.add(name)
        expected = nxt
    for name in expected:  # unsolved at the last rung: censored there
        out[name] = (False, budget, label, budget, cap, None)
    return out


def level_of(g, E):
    for lvl, edge in enumerate(EDGES, start=1):
        if g < edge:
            return lvl
    if g < E:
        return 7
    assert g <= TOP, g
    return 8


def hump_of(record, r1, r2):
    """(hump, source) from a greedy record's certificate, or ('', 'none')."""
    if record is None:
        return '', 'none'
    path = record.get('path')
    if path:
        return peak_minus_start([tuple(s) for s in path]), 'path'
    moves = record.get('path_moves')
    if moves:
        if isinstance(moves, str):
            moves = ast.literal_eval(moves)
        states = replay_moves(r1, r2, moves)
        if states is None:
            return '', 'replay_failed'
        return peak_minus_start(states), 'path_moves'
    return '', 'none'


def build_rows(src, notes):
    rows = []
    autmin = src.csv('autmin')
    names = [r['name'] for r in autmin]
    assert len(names) == 72_779 and names == [f'ac19_{i}' for i in range(len(names))]

    greedy = chain(src, GREEDY_RUNGS, names, extra_key='unescalated_greedy')
    s20 = chain(src, S20_RUNGS, names, extra_key='unescalated_s20')
    g10k = by_name(src.jsonl('greedy10k'))
    notable_unsolved = {r['name'] for r in src.csv('notable_unsolved')}
    final_unsolved = {r['name'] for r in src.csv('final_unsolved')}
    assert len(notable_unsolved) == 217 and len(final_unsolved) == 727

    pairs = src.csv('pairs40')
    orig10m = by_name(src.jsonl('orig10m'))
    assert len(pairs) == 40 and set(orig10m) == {p['name'] for p in pairs}
    pair_orbits = {p['orbit'] for p in pairs}

    open8 = []
    if src.exists('open8_greedy'):
        open8_orig = {r['name']: r for r in src.csv('open8_orig')}
        for rec in src.jsonl('open8_greedy'):
            assert rec['name'] in open8_orig and rec['orbit'] == open8_orig[rec['name']]['orbit']
            open8.append(rec)
        pair_orbits |= {rec['orbit'] for rec in open8 if as_bool(rec['solved'])}
    else:
        notes.append('open8_greedy rung absent: the 8 ac19_orig_cascade originals are not on the ladder '
                     '(run benchmark/ladder/grade_open8.py to add them)')

    # E from the AC19 rows greedy-solved in [1M, 10M]
    mid = sorted(math.log10(v[1]) for v in greedy.values() if v[0] and 1_000_000 <= v[1] <= TOP)
    assert mid, 'no rows in [1M, 10M]'
    med = (mid[len(mid) // 2 - 1] + mid[len(mid) // 2]) / 2 if len(mid) % 2 == 0 else mid[len(mid) // 2]
    E = int(round(10 ** med))

    # --- AC19 aut-min orbits ---
    for r in autmin:
        name, r1, r2 = r['name'], r['r1'], r['r2']
        gs, gn, glabel, gbud, gcap, grec = greedy[name]
        ss, sn, slabel, sbud, scap, _ = s20[name]
        if not gs and glabel == 'unsolved@extra':
            notes.append(f'{name}: never escalated on record and unsolved by greedy at {gbud:,} in '
                         'grade_extra; no level, left off the ladder')
            continue
        start = len(r1) + len(r2)
        rec10k = g10k[name]
        climb_rec = grec if grec is not None else rec10k
        climb = int(climb_rec['max_relator_length_expanded']) - start
        hump, hsrc = hump_of(grec, r1, r2)
        if gs:
            solved_by = glabel
        elif ss:
            solved_by = slabel
        elif name not in notable_unsolved:
            solved_by = 'K3p_notable@1k'
        else:
            solved_by = 'K3p_c14aut@1k'
        level = level_of(gn, E) if gs else (9 if ss else 10)   # 9: S20_MK2 solves it; 10: only the cascades do
        rows.append(dict(
            name=name, r1=r1, r2=r2, level=level, source='ac19', form='autmin', orbit=name,
            pair_id=name if name in pair_orbits else '',
            greedy_solved=int(gs), greedy_nodes=gn, greedy_budget=gbud, greedy_cap=gcap,
            greedy_run=glabel.split('@')[1] if gs else 'unsolved@10M',
            s20_solved=int(ss), s20_nodes=sn,
            s20_run=slabel.split('@')[1] if ss else ('unsolved@10M' if slabel != 'unsolved@extra' else f'unsolved@extra{sbud // 1000}k'),
            start_len=start, hump=hump, hump_source=('greedy@' + glabel.split('@')[1]) if hump != '' else 'none',
            climb=climb, solved_by=solved_by, aut_class=name))

    # --- the originals of the hard orbits (graded by their OWN greedy cost) ---
    def original_row(name, r1, r2, orbit, rec, label, budget, cap):
        assert as_bool(rec['solved'])
        gn = int(rec['nodes_explored'])
        start = len(r1) + len(r2)
        hump, _ = hump_of(rec, r1, r2)
        return dict(
            name=name, r1=r1, r2=r2, level=level_of(gn, E), source='ac19', form='original',
            orbit=orbit, pair_id=orbit,
            greedy_solved=1, greedy_nodes=gn, greedy_budget=budget, greedy_cap=cap, greedy_run=label,
            s20_solved='', s20_nodes='', s20_run='',
            start_len=start, hump=hump, hump_source=('greedy@' + label) if hump != '' else 'none',
            climb=int(rec['max_relator_length_expanded']) - start,
            solved_by='greedy@' + label, aut_class=orbit)

    for p in pairs:
        rec = orig10m[p['name']]
        assert (rec['r1'], rec['r2']) == (p['r1'], p['r2']), p['name']
        assert p['orbit'] in greedy and not greedy[p['orbit']][0], p  # its rep is greedy-unsolved
        rows.append(original_row(p['name'], p['r1'], p['r2'], p['orbit'], rec, 'orig10M', 10_000_000, 64))
    have = {r['name'] for r in rows}
    for rec in open8:
        if rec['name'] in have:   # also one of the 40: the committed 10M record grades it
            notes.append(f"{rec['name']} is in both open8 and the 40 pairs; graded by the 10M run")
            continue
        if not as_bool(rec['solved']):
            notes.append(f"{rec['name']} (orbit {rec['orbit']}) unsolved by greedy at {rec['budget']:,}: "
                         'no level, left off the ladder')
            continue
        rows.append(original_row(rec['name'], rec['r1'], rec['r2'], rec['orbit'], rec,
                                 f"open8_{rec['budget'] // 1000}k", int(rec['budget']), int(rec['max_relator_length'])))

    # --- MS640 ---
    ms_txt = [decode_padded(line) for line in src.text('ms640_txt').splitlines() if line.strip()]
    assert len(ms_txt) == 640
    bins = {int(r['pres_id']): r for r in src.csv('ms640_bins')}
    ms_recs = src.jsonl('ms640_1m')
    assert len(ms_recs) == 640
    for rec in ms_recs:
        pid = int(rec['pres_id'])
        r1, r2 = rec['r1'], rec['r2']
        assert (r1, r2) == ms_txt[pid], pid
        assert int(rec['node_budget']) == 1_000_000 and int(rec['max_relator_length_cap']) == 24
        assert as_bool(rec['solved'])
        gn = int(rec['nodes_explored'])
        start = len(r1) + len(r2)
        rows.append(dict(
            name=f'ms_{pid:03d}', r1=r1, r2=r2, level=level_of(gn, E), source='ms640', form='ms_raw',
            orbit='', pair_id='',
            greedy_solved=1, greedy_nodes=gn, greedy_budget=1_000_000, greedy_cap=24, greedy_run='ms640_1M',
            s20_solved='', s20_nodes='', s20_run='',
            start_len=start, hump='', hump_source='none',
            climb=int(rec['max_relator_length_expanded']) - start,
            solved_by='greedy@1M', aut_class=f"ms_aut_{bins[pid]['aut_class']}"))

    # --- S20_MK2 on the originals and MS640 (run here: run_ladder.py, 100k pops, cap 48) ---
    s20x = {}
    for rec in src.jsonl('s20_ms640_orig'):
        assert rec['engine'] == 's20_mk2' and int(rec['cap']) == 48 and int(rec['budget']) == 100_000, rec['name']
        assert not rec.get('error') and (not rec['solved'] or rec['verified']), rec['name']
        assert rec['name'] not in s20x, rec['name']
        s20x[rec['name']] = rec
    graded = 0
    for row in rows:
        if row['form'] in ('original', 'ms_raw'):
            rec = s20x[row['name']]
            assert (rec['r1'], rec['r2']) == (row['r1'], row['r2']), row['name']
            row['s20_solved'] = int(bool(rec['solved']))
            row['s20_nodes'] = int(rec['nodes']) if rec['solved'] else ''
            row['s20_run'] = 'ladder100k' if rec['solved'] else 'unsolved@ladder100k'
            graded += 1
    assert graded == len(s20x) == 685, (graded, len(s20x))

    # --- MS unsolved: NOT on the ladder; their own files, in four forms ---
    unsolved = []

    def unsolved_row(name, r1, r2, form, aut_class):
        return dict(name=name, r1=r1, r2=r2, level='unsolved', source='ms_unsolved', form=form, orbit='', pair_id='',
                    greedy_solved=0, greedy_nodes='', greedy_budget='', greedy_cap='', greedy_run='',
                    s20_solved=0, s20_nodes='', s20_run='',
                    start_len=len(r1) + len(r2), hump='', hump_source='none', climb='',
                    solved_by='none', aut_class=aut_class)

    aca_initial = src.csv('aca_initial')
    aca_best = src.csv('aca_best')
    assert [r['name'] for r in aca_initial] == [f'aca_{i}' for i in range(124)]
    assert [r['name'] for r in aca_best] == [r['name'] for r in aca_initial]
    for r in aca_initial:
        unsolved.append(unsolved_row(r['name'], r['r1'], r['r2'], 'aca_initial', r['name']))
    for r in aca_best:
        unsolved.append(unsolved_row('acabest_' + r['name'][4:], r['r1'], r['r2'], 'aca_best', r['name']))
    reps = src.csv('ms_reps261')
    assert len(reps) == 261
    for r in reps:
        unsolved.append(unsolved_row('msrep_' + r['name'], r['r1'], r['r2'], 'ms_rep261', 'msrep_' + r['name']))
    solved_set = set(ms_txt)
    raw = [(i, decode_padded(line)) for i, line in enumerate(src.text('ms1190_txt').splitlines()) if line.strip()]
    assert len(raw) == 1190
    unsolved_raw = [(i, pr) for i, pr in raw if pr not in solved_set]
    assert len(unsolved_raw) == 550, len(unsolved_raw)
    for i, (r1, r2) in unsolved_raw:
        unsolved.append(unsolved_row(f'msraw_{i}', r1, r2, 'ms_raw', f'msraw_{i}'))

    # sanity: names unique, words over xXyY, every ladder row solved by something on record
    seen = set()
    for row in rows + unsolved:
        assert row['name'] not in seen, row['name']
        seen.add(row['name'])
        assert row['r1'] and row['r2'] and set(row['r1'] + row['r2']) <= set('xXyY'), row['name']
    assert all(row['solved_by'] != 'none' for row in rows)
    assert all(row['solved_by'] == 'none' for row in unsolved) and len(unsolved) == 1_059
    return rows, E, unsolved


# --- nested ranking ------------------------------------------------------------
def farthest_point_order(n, limit):
    """Indices 0..n-1 in farthest-point order on a line: the median first (so a
    single pick is representative, as the old ladder's k=1 rule), then both
    endpoints, then the midpoint of the largest remaining gap (leftmost gap on ties,
    lower index inside a gap).  Every prefix is a near-uniform grid over the range.
    Only the first ``limit`` positions are produced; the rest follow in plain order
    (they are never reached by a subset)."""
    if n == 0:
        return []
    if n == 1:
        return [0]
    if n == 2:
        return [0, 1]
    mid = (n - 1) // 2
    order = [mid, 0, n - 1]
    picked = {mid, 0, n - 1}
    heap = [(-(mid - 0), 0, mid), (-(n - 1 - mid), mid, n - 1)]  # (-gap, a, b)
    while heap and len(order) < min(n, limit):
        neg, a, b = heapq.heappop(heap)
        if b - a < 2:
            continue
        m = (a + b) // 2
        if m in picked:
            continue
        order.append(m)
        picked.add(m)
        heapq.heappush(heap, (-(m - a), a, m))
        heapq.heappush(heap, (-(b - m), m, b))
    if len(order) < n:
        order.extend(i for i in range(n) if i not in picked)
    return order


def sort_key(row):
    lvl = row['level']
    if lvl == 10:   # nothing but the cascades solves these; no pop cost to spread over
        return (row['climb'], row['start_len'], row['name'])
    if lvl == 9:
        s = row['s20_nodes'] if row['s20_solved'] == 1 else TOP
        return (s, row['climb'], row['name'])
    return (math.log10(row['greedy_nodes']), row['climb'] if row['climb'] != '' else 0, row['name'])


def rank_level(rows, limit):
    """One ranked list for a level: round-robin over strata, farthest-point inside.

    No Aut(F2)-class dedup, deliberately: two automorphic presentations are two
    different search problems with different costs (that difference is what the
    original/representative pairs and ``research/autchoice_20260910`` are about), so
    both are legitimate test rows.  ``aut_class`` stays in the CSV as information.
    """
    eligible = []
    for row in sorted(rows, key=sort_key):
        if (row['source'], row['form']) not in STRATA:
            continue
        if row['greedy_solved'] == 1 and row['greedy_nodes'] <= TRIVIAL_POPS:
            continue   # solved at the root pop: in the pool, never a test row
        eligible.append(row)

    def ordered(rows_):
        rows_ = sorted(rows_, key=sort_key)
        return [rows_[i] for i in farthest_point_order(len(rows_), limit)]

    def round_robin(lists):
        out, idx = [], [0] * len(lists)
        while any(idx[j] < len(lists[j]) for j in range(len(lists))):
            for j, lst in enumerate(lists):
                if idx[j] < len(lst):
                    out.append(lst[idx[j]])
                    idx[j] += 1
        return out

    by_stratum = defaultdict(list)
    for row in eligible:
        by_stratum[(row['source'], row['form'])].append(row)
    return round_robin([ordered(by_stratum[s]) for s in STRATA])


def s20_cost(row):
    """S20_MK2 pops on record, censored at 10M + 1 when unsolved (level 9's residue)."""
    if row['s20_solved'] == 1:
        return row['s20_nodes']
    return TOP + 1


def s20hard_key(row):
    """Hardest for S20_MK2 first; ties (the censored rows) by the plain greedy cost,
    hardest first, then by name."""
    g = row['greedy_nodes'] if row['greedy_solved'] == 1 else TOP + 1
    return (-s20_cost(row), -g, row['name'])


def rank_level_s20hard(rows, spread_ranked):
    """The S20-hard list for a level: the eligible rows (same strata, no root pop,
    no Aut dedup) in order of decreasing S20_MK2 cost, no round-robin over strata --
    the hardest rows win whatever their source.  Level 10 has no S20 cost (S20_MK2
    never solves it; only the cascades do), so it keeps the spread order."""
    if rows and rows[0]['level'] == 10:
        return spread_ranked
    eligible = [row for row in rows
                if (row['source'], row['form']) in STRATA
                and not (row['greedy_solved'] == 1 and row['greedy_nodes'] <= TRIVIAL_POPS)]
    assert all(row['s20_run'] for row in eligible), 'every eligible row below level 10 carries an S20 grade'
    return sorted(eligible, key=s20hard_key)


# --- output --------------------------------------------------------------------
def write_csv(path, rows):
    with open(path, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator='\n')
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, '') for k in FIELDS})


def level_table(E):
    edges = [0] + EDGES + [E, TOP]
    table = []
    for lvl in range(1, 9):
        table.append(OrderedDict(level=lvl, lo_nodes=edges[lvl - 1], hi_nodes=edges[lvl],
                                 rule=f'{edges[lvl-1]:,} <= g < {edges[lvl]:,}' if lvl < 8 else f'{E:,} <= g <= {TOP:,}'))
    table.append(OrderedDict(level=9, lo_nodes=None, hi_nodes=None,
                             rule='plain greedy unsolved at 10,000,000 nodes; S20_MK2 solves it'))
    table.append(OrderedDict(level=10, lo_nodes=None, hi_nodes=None,
                             rule='plain greedy and S20_MK2 both unsolved at 10,000,000 nodes; only the cascades solve it'))
    return table


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--out', type=Path, default=HERE)
    ap.add_argument('--force', action='store_true')
    args = ap.parse_args()
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    targets = [out / 'ladder_all.csv', out / 'ladder_pairs.csv', out / 'ladder_manifest.json',
               out / 'unsolved_124.csv', out / 'unsolved_all_forms.csv', out / 'originals_45.csv'] + \
              [out / f'ladder_{n}.{ext}' for n in SIZES for ext in ('csv', 'json')] + \
              [out / f'ladder_{n}_s20hard.{ext}' for n in S20HARD_SIZES for ext in ('csv', 'json')]
    existing = [t for t in targets if t.exists()]
    if existing and not args.force:
        sys.exit(f'{len(existing)} output files exist (e.g. {existing[0]}); pass --force to overwrite')

    t0 = time.time()
    src = Sources()
    notes = []
    rows, E, unsolved = build_rows(src, notes)
    rows.sort(key=lambda r: (r['level'], r['source'], r['form'], sort_key(r)))
    write_csv(out / 'ladder_all.csv', rows)
    write_csv(out / 'unsolved_124.csv', [r for r in unsolved if r['form'] == 'aca_initial'])
    write_csv(out / 'unsolved_all_forms.csv', unsolved)

    # the 45 dataset originals: in the pool, off every panel, runnable as their own panel
    originals = sorted((r for r in rows if r['form'] == 'original'), key=lambda r: (r['orbit'], r['name']))
    write_csv(out / 'originals_45.csv', originals)

    # pairs table
    reps = {r['name']: r for r in rows if r['form'] == 'autmin'}
    with open(out / 'ladder_pairs.csv', 'w', newline='') as fh:
        w = csv.writer(fh, lineterminator='\n')
        w.writerow(['pair_id', 'orig_name', 'orig_r1', 'orig_r2', 'orig_level', 'orig_greedy_nodes', 'orig_hump',
                    'rep_name', 'rep_r1', 'rep_r2', 'rep_level', 'rep_greedy_run', 'rep_s20_nodes', 'rep_solved_by'])
        for o in originals:
            rep = reps[o['orbit']]
            w.writerow([o['pair_id'], o['name'], o['r1'], o['r2'], o['level'], o['greedy_nodes'], o['hump'],
                        rep['name'], rep['r1'], rep['r2'], rep['level'], rep['greedy_run'], rep['s20_nodes'],
                        rep['solved_by']])

    # nested subsets
    by_level = defaultdict(list)
    for row in rows:
        by_level[row['level']].append(row)
    ranked = {lvl: rank_level(by_level[lvl], limit=max(SIZES) // N_LEVELS + 10) for lvl in range(1, N_LEVELS + 1)}
    populations = OrderedDict()
    for lvl in range(1, N_LEVELS + 1):
        populations[str(lvl)] = OrderedDict(
            total=len(by_level[lvl]),
            eligible=sum(1 for r in by_level[lvl] if (r['source'], r['form']) in STRATA
                         and not (r['greedy_solved'] == 1 and r['greedy_nodes'] <= TRIVIAL_POPS)),
            by_source_form=OrderedDict(sorted(Counter(f"{r['source']}/{r['form']}" for r in by_level[lvl]).items())))
    for size in SIZES:
        k = size // N_LEVELS
        chosen, actual = [], OrderedDict()
        for lvl in range(1, N_LEVELS + 1):
            take = ranked[lvl][:k]
            chosen.extend(take)
            actual[str(lvl)] = len(take)
        assert not any(r['form'] == 'original' for r in chosen), f'ladder_{size}: originals are off the panels'
        write_csv(out / f'ladder_{size}.csv', chosen)
        meta = OrderedDict(
            size=len(chosen), requested_size=size, per_level=k, per_level_actual=actual, n_levels=N_LEVELS,
            difficulty_variable='plain length-ordered greedy node count g on record (see greedy_run/greedy_cap per row)',
            levels=level_table(E), E=E, nested=True,
            strata_order=[f'{s}/{f}' for s, f in STRATA],
            within_level_selection='rows solved at the root pop excluded; NO Aut(F2)-class dedup '
                                   '(automorphic presentations are different search problems); '
                                   'round-robin over strata; farthest-point order (median, endpoints, '
                                   'then bisect the largest gap) over (log10 g, climb, name) inside a '
                                   'stratum (level 9: S20_MK2 pops; level 10: climb, then start length)',
            sources=src.manifest, subset=[r['name'] for r in chosen])
        (out / f'ladder_{size}.json').write_text(json.dumps(meta, indent=1) + '\n')

    # the S20-hard variant: same levels, same strata, the rows S20_MK2 finds hardest.
    # Levels stay the greedy bands; a row S20_MK2 never solves is level 10 (only the
    # cascades solve it) -- on record every such row is greedy-unsolved too.
    for row in rows:
        if row['s20_solved'] == 0:
            assert row['greedy_solved'] == 0 and row['level'] == 10, row['name']
    ranked_s20 = {lvl: rank_level_s20hard(by_level[lvl], ranked[lvl]) for lvl in range(1, N_LEVELS + 1)}
    for size in S20HARD_SIZES:
        k = size // N_LEVELS
        chosen, actual = [], OrderedDict()
        for lvl in range(1, N_LEVELS + 1):
            take = ranked_s20[lvl][:k]
            chosen.extend(take)
            actual[str(lvl)] = len(take)
        assert not any(r['form'] == 'original' for r in chosen), f'ladder_{size}_s20hard: originals are off the panels'
        write_csv(out / f'ladder_{size}_s20hard.csv', chosen)
        meta = OrderedDict(
            variant='s20hard', size=len(chosen), requested_size=size, per_level=k, per_level_actual=actual,
            n_levels=N_LEVELS,
            difficulty_variable='levels: plain greedy node count g on record (as ladder_N); within a level: '
                                'S20_MK2 pops on record (s20_nodes; unsolved rows count as 10M+1)',
            levels=level_table(E), E=E, nested=True,
            within_level_selection='rows solved at the root pop excluded; NO Aut(F2)-class dedup; NO '
                                   'round-robin over strata; the k rows with the largest S20_MK2 cost '
                                   '(unsolved first, ties by plain greedy cost then name); level 10 '
                                   '(no S20 cost) keeps the order of ladder_N',
            sources=src.manifest, subset=[r['name'] for r in chosen])
        (out / f'ladder_{size}_s20hard.json').write_text(json.dumps(meta, indent=1) + '\n')

    manifest = OrderedDict(
        built_unix=int(t0), git_head=subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True,
                                                     text=True, check=True).stdout.strip(),
        rows=len(rows), E=E, levels=level_table(E), populations=populations,
        hump_available=sum(1 for r in rows if r['hump'] != ''),
        hump_sources=OrderedDict(sorted(Counter(r['hump_source'] for r in rows).items())),
        pairs=len(originals),
        strata=[f'{s_}/{f_}' for s_, f_ in STRATA],
        originals=OrderedDict(
            rows=len(originals), orbits=len({r['orbit'] for r in originals}), file='originals_45.csv',
            by_level=OrderedDict(sorted((str(k), v) for k, v in
                                        Counter(r['level'] for r in originals).items())),
            greedy_nodes=OrderedDict(lo=min(r['greedy_nodes'] for r in originals),
                                     hi=max(r['greedy_nodes'] for r in originals)),
            rule='the AC19_extended.txt lines of the orbits plain greedy cannot solve at 10,000,000; '
                 'in the pool and in ladder_pairs.csv, never a panel row (not a sample of the dataset)'),
        unsolved=OrderedDict(rows=len(unsolved), files=['unsolved_124.csv', 'unsolved_all_forms.csv'],
                             by_form=OrderedDict(sorted(Counter(r['form'] for r in unsolved).items()))),
        sizes=list(SIZES), s20hard_sizes=list(S20HARD_SIZES), sources=src.manifest, notes=notes)
    (out / 'ladder_manifest.json').write_text(json.dumps(manifest, indent=1) + '\n')

    print(f'rows {len(rows):,}   E = {E:,}   {time.time() - t0:.1f}s')
    for lvl in range(1, N_LEVELS + 1):
        p = populations[str(lvl)]
        print(f"  level {lvl:2}: {p['total']:6,} rows  ({', '.join(f'{k} {v}' for k, v in p['by_source_form'].items())})")
    print(f"  unsolved (not on the ladder): {len(unsolved):,} rows in unsolved_all_forms.csv, "
          f"{sum(1 for r in unsolved if r['form'] == 'aca_initial')} in unsolved_124.csv")
    print(f"  originals (in the pool, off the panels): {len(originals)} rows from "
          f"{len({r['orbit'] for r in originals})} orbits in originals_45.csv")
    for n in notes:
        print('  note:', n)


if __name__ == '__main__':
    main()
