"""Run one search arm or policy over a ladder subset and record every row.

    PYTHONPATH=. python3 -m benchmark.ladder.run_ladder --subset 60 --engine greedy --budget 10000
    PYTHONPATH=. python3 -m benchmark.ladder.run_ladder --subset 200 --engine s20_mk2 --budget 100000 --workers 4
    PYTHONPATH=. python3 -m benchmark.ladder.run_ladder --subset 200 --engine policy --policy K3p_notable --budget 1000

Engines
    greedy    plain length-ordered greedy (``config=None``), pop-for-pop the historical
              baseline, through ``experiments.heuristic_search.core.hcompact``
    s20_mk2   the same engine under ``experiments.search.heuristics.S20_MK2``
    policy    any name in ``research/residual_20260909/policies.py`` (+ ``policies_round2``),
              run through ``research.residual_20260909.harness.run_row`` verbatim

Units differ by engine and are never mixed: ``greedy``/``s20_mk2`` count heap pops;
``policy`` counts the policy's charged units, and under a table policy a lookup is
free, so those units are a budget and not a difficulty measure (AGENTS.md section 5).

Every pop-engine solve is replayed independently -- ``words.canon_pair`` then
``words.replay_move`` over the recorded moves, never the engine's own replay -- and a
row is ``verified`` only if that replay ends on two distinct single letters.  Policy
rows carry ``run_row``'s own two-decoder verification.

Memory: the compact engine reserves ~6 GB at 1,000,000 pops.  Budgets above that are
refused unless ``LADDER_ALLOW_BIG=1``; above 300,000 the run is forced to one worker.

Output: ``<out>/<tag>.jsonl`` (one record per row, written atomically, resumable by
name) and ``<out>/<tag>.summary.json``.  Default tag ``<panel>_<engine>_b<budget>_c<cap>``.
"""
import argparse
import csv
import hashlib
import json
import multiprocessing as mp
import os
import statistics
import subprocess
import sys
import time
from collections import Counter, OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
for _v in ('OMP_NUM_THREADS', 'NUMBA_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

HERE = Path(__file__).resolve().parent
POP_ENGINES = ('greedy', 's20_mk2')
ENGINES = POP_ENGINES + ('policy',)
BIG_BUDGET = 1_000_000
ONE_WORKER_ABOVE = 300_000
WARMUP = ('YYXyX', 'YXXyx')

# --- worker state --------------------------------------------------------------
_ENGINE = None
_CONFIG = None
_POLICY = None
_BUDGET = None
_CAP = None


def _init_worker(engine, policy_name, budget, cap, warmup):
    global _ENGINE, _CONFIG, _POLICY, _BUDGET, _CAP
    _ENGINE, _BUDGET, _CAP = engine, budget, cap
    if engine in POP_ENGINES:
        from experiments.search.heuristics import S20_MK2
        _CONFIG = None if engine == 'greedy' else S20_MK2
        if warmup:
            _run_pop('warmup', WARMUP)
    else:
        from research.residual_20260909 import policies, policies_round2  # noqa: F401 (registers P*)
        _POLICY = policies.REGISTRY[policy_name]
        if warmup:
            from research.residual_20260909.harness import run_row
            run_row(_POLICY, 'warmup', WARMUP, min(budget, 1000))


def _replay_pops(r1, r2, path, path_moves):
    """Independent replay of a pop-engine certificate; returns (verified, reason)."""
    from experiments.equivalence_classes.lib.words import canon_pair, replay_move
    state = canon_pair(r1, r2)
    if path and list(state) != list(path[0]):
        return False, 'start mismatch'
    for i, move in enumerate(path_moves):
        state = replay_move(state, tuple(int(v) for v in move.split('_')))
        if path and list(state) != list(path[i + 1]):
            return False, f'state mismatch at move {i}'
    a, b = state
    ok = len(a) == len(b) == 1 and a.lower() != b.lower()
    return ok, ('' if ok else 'did not end on (x, y)')


def _run_pop(name, pair):
    from experiments.heuristic_search.core.hcompact import greedy_search_hcompact
    r1, r2 = pair
    t0 = time.perf_counter()
    res = greedy_search_hcompact(r1, r2, _BUDGET, max_relator_length=_CAP, config=_CONFIG, track_path=True)
    wall = time.perf_counter() - t0
    rec = OrderedDict(name=name, r1=r1, r2=r2, engine=_ENGINE, budget=_BUDGET, cap=_CAP,
                      solved=bool(res['solved']), nodes=int(res['nodes_explored']), units='pops',
                      verified=False, path_length=int(res['path_length']) if res['solved'] else None,
                      min_total_length_seen=int(res['min_relator_length']),
                      max_relator_length_expanded=int(res['max_relator_length_expanded']),
                      search_wall=round(wall, 4), certificate_wall=0.0, path_moves=[])
    if res['solved']:
        t1 = time.perf_counter()
        ok, why = _replay_pops(r1, r2, res['path'], res['path_moves'])
        rec['verified'] = ok
        rec['certificate_wall'] = round(time.perf_counter() - t1, 4)
        rec['path_moves'] = res['path_moves']
        if not ok:
            rec['error'] = 'replay failed: ' + why
    return rec


def _run_policy(name, pair):
    from research.residual_20260909.harness import run_row
    r = run_row(_POLICY, name, pair, _BUDGET)
    rec = OrderedDict(name=name, r1=pair[0], r2=pair[1], engine='policy', policy=_POLICY.policy_name,
                      budget=_BUDGET, cap=None, solved=bool(r['solved']), nodes=int(r['nodes_explored']),
                      units='charged', verified=bool(r.get('verified', False)),
                      path_length=int(r.get('elementary_count', 0)) if r['solved'] else None,
                      min_total_length_seen=r.get('min_total_length_seen'),
                      search_wall=round(float(r['search_wall']), 4),
                      certificate_wall=round(float(r.get('certificate_wall', 0.0)), 4),
                      route=r.get('policy_route'))
    for k in ('prepass_charges', 'plain_charges', 'fallback_nodes', 'winner', 'ball_hit', 'ball_depth'):
        if k in r:
            rec[k] = r[k]
    if r['solved']:
        rec['states'] = r.get('states')
        rec['steps'] = r.get('steps')
        if 'elementary_tail' in r:
            rec['elementary_tail'] = r['elementary_tail']
    return rec


def _work(job):
    index, row = job
    try:
        rec = _run_pop(row['name'], (row['r1'], row['r2'])) if _ENGINE in POP_ENGINES \
            else _run_policy(row['name'], (row['r1'], row['r2']))
    except Exception as exc:  # noqa: BLE001 -- recorded per row, the run continues
        rec = OrderedDict(name=row['name'], r1=row['r1'], r2=row['r2'], engine=_ENGINE, budget=_BUDGET,
                          cap=_CAP, solved=False, nodes=0, verified=False,
                          error=f'{type(exc).__name__}: {exc}')
    rec['index'] = index
    for k in ('level', 'source', 'form', 'greedy_nodes', 'greedy_run', 'pair_id'):
        if k in row:
            rec[k] = row[k]
    return rec


# --- panel ---------------------------------------------------------------------
def load_rows(args):
    if args.panel:
        path = Path(args.panel)
    elif args.subset == 'all':
        path = HERE / 'ladder_all.csv'
    elif args.subset == 'unsolved124':
        path = HERE / 'unsolved_124.csv'
    elif args.subset == 'originals':
        path = HERE / 'originals_45.csv'
    else:
        path = HERE / f'ladder_{args.subset}.csv'
    if not path.exists():
        sys.exit(f'panel not found: {path} (run build_ladder.py first?)')
    with open(path, newline='') as fh:
        rows = list(csv.DictReader(fh))
    if not rows or not {'name', 'r1', 'r2'} <= set(rows[0]):
        sys.exit(f'{path}: need columns name,r1,r2')
    for row in rows:
        if not (row['r1'] and row['r2'] and set(row['r1'] + row['r2']) <= set('xXyY')):
            sys.exit(f"{row['name']}: words must be nonempty over xXyY")
    if args.levels:
        if 'level' not in rows[0]:
            sys.exit('--levels needs a level column')
        keep = parse_levels(args.levels)
        rows = [r for r in rows if int(r['level']) in keep]
    if args.names:
        want = args.names.split(',')
        have = {r['name']: r for r in rows}
        missing = [n for n in want if n not in have]
        if missing:
            sys.exit(f'--names not in panel: {missing[:5]}')
        rows = [have[n] for n in want]
    if args.limit:
        rows = rows[:args.limit]
    return path, rows


def parse_levels(spec):
    keep = set()
    for part in spec.split(','):
        if '-' in part:
            lo, hi = part.split('-')
            keep.update(range(int(lo), int(hi) + 1))
        else:
            keep.add(int(part))
    return keep


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def git_head():
    try:
        return subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        return None


# --- summary -------------------------------------------------------------------
def summarize(records, args, panel_path, panel_sha, wall):
    def med(xs):
        return statistics.median(xs) if xs else None
    by_level = OrderedDict()
    levels = sorted({int(r['level']) for r in records if r.get('level') not in (None, '')})
    for lvl in levels:
        rs = [r for r in records if r.get('level') not in (None, '') and int(r['level']) == lvl]
        solved = [r for r in rs if r['solved']]
        by_level[str(lvl)] = OrderedDict(
            rows=len(rs), solved=len(solved), verified=sum(1 for r in rs if r['verified']),
            errors=sum(1 for r in rs if r.get('error')),
            median_nodes_solved=med([r['nodes'] for r in solved]),
            total_nodes=sum(r['nodes'] for r in rs),
            search_wall=round(sum(r.get('search_wall', 0.0) for r in rs), 3))
    solved = [r for r in records if r['solved']]
    return OrderedDict(
        panel=str(panel_path.relative_to(ROOT) if panel_path.is_relative_to(ROOT) else panel_path),
        panel_sha256=panel_sha, engine=args.engine, policy=args.policy, budget=args.budget,
        cap=args.cap if args.engine in POP_ENGINES else None,
        units='pops' if args.engine in POP_ENGINES else 'charged (table lookups free)',
        levels_filter=args.levels, workers=args.workers, tag=args.tag,
        rows=len(records), solved=len(solved), verified=sum(1 for r in records if r['verified']),
        errors=sum(1 for r in records if r.get('error')),
        unsolved_names=[r['name'] for r in records if not r['solved']],
        total_nodes=sum(r['nodes'] for r in records),
        median_nodes_solved=med([r['nodes'] for r in solved]),
        search_wall=round(sum(r.get('search_wall', 0.0) for r in records), 3),
        certificate_wall=round(sum(r.get('certificate_wall', 0.0) for r in records), 3),
        run_wall=round(wall, 3), by_level=by_level,
        routes=OrderedDict(sorted(Counter(r.get('route') for r in records if r.get('route')).items())),
        git_head=git_head(), created_unix=int(time.time()))


# --- main ----------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group()
    src.add_argument('--subset', default='60',
                     help='20|40|60|100|200|300|500|all|unsolved124|originals (default 60)')
    src.add_argument('--panel', help='any CSV with columns name,r1,r2 (level optional)')
    ap.add_argument('--levels', default=None, help='filter by level, e.g. 3-9 or 1,5,10')
    ap.add_argument('--names', default=None, help='comma-separated row names, in that order')
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--engine', choices=ENGINES, required=True)
    ap.add_argument('--policy', default=None, help='policy name for --engine policy')
    ap.add_argument('--budget', type=int, required=True, help='pops (greedy/s20_mk2) or charged units (policy)')
    ap.add_argument('--cap', type=int, default=48, help='max relator length for the pop engines (default 48; '
                                                         '24 reproduces the ms640 grading)')
    ap.add_argument('--workers', type=int, default=1)
    ap.add_argument('--big-workers', action='store_true',
                    help=f'keep --workers above {ONE_WORKER_ABOVE:,} pops (each 1M-pop worker holds a few GB)')
    ap.add_argument('--out', type=Path, default=HERE / 'runs')
    ap.add_argument('--tag', default=None)
    ap.add_argument('--force', action='store_true', help='discard an existing <tag>.jsonl instead of resuming')
    ap.add_argument('--warmup', action=argparse.BooleanOptionalAction, default=True)
    args = ap.parse_args(argv)

    if args.engine == 'policy':
        if not args.policy:
            sys.exit('--engine policy needs --policy NAME')
        from research.residual_20260909 import policies, policies_round2  # noqa: F401
        if args.policy not in policies.REGISTRY:
            sys.exit(f'unknown policy {args.policy!r}; known: {", ".join(sorted(policies.REGISTRY))}')
    elif args.policy:
        sys.exit('--policy only applies to --engine policy')
    if args.budget < 1:
        sys.exit('--budget must be >= 1')
    if args.engine in POP_ENGINES:
        if not 1 <= args.cap <= 128:
            sys.exit('--cap must be in 1..128 (compact engine stores the move in int8)')
        if args.budget > BIG_BUDGET and os.environ.get('LADDER_ALLOW_BIG') != '1':
            sys.exit(f'--budget {args.budget:,} > {BIG_BUDGET:,}: the compact engine reserves ~6 GB per '
                     f'1,000,000 pops; set LADDER_ALLOW_BIG=1 to run anyway')
        if args.budget > ONE_WORKER_ABOVE and args.workers != 1 and not args.big_workers:
            print(f'[run_ladder] budget {args.budget:,} > {ONE_WORKER_ABOVE:,}: forcing --workers 1 (memory; '
                  f'--big-workers keeps them)')
            args.workers = 1

    panel_path, rows = load_rows(args)
    if not rows:
        sys.exit('no rows selected')
    panel_sha = sha256_file(panel_path)
    if args.tag is None:
        stem = Path(args.panel).stem if args.panel else f'ladder_{args.subset}'
        arm = args.policy if args.engine == 'policy' else args.engine
        args.tag = f'{stem}_{arm}_b{args.budget}' + (f'_c{args.cap}' if args.engine in POP_ENGINES else '')
        if args.levels:
            args.tag += '_L' + args.levels.replace(',', '_')
    args.out.mkdir(parents=True, exist_ok=True)
    out_path = args.out / f'{args.tag}.jsonl'
    partial = args.out / f'{args.tag}.jsonl.partial'

    done = OrderedDict()
    if out_path.exists() and not args.force:
        with open(out_path) as fh:
            for line in fh:
                if line.strip():
                    rec = json.loads(line)
                    done[rec['name']] = rec
        same = all(rec.get('engine') == args.engine and rec.get('budget') == args.budget
                   and (args.engine == 'policy' or rec.get('cap') == args.cap) for rec in done.values())
        if not same:
            sys.exit(f'{out_path} holds a different engine/budget/cap; use --force or another --tag')
        print(f'[run_ladder] resuming: {len(done)} rows already in {out_path.name}')
    todo = [(i, r) for i, r in enumerate(rows) if r['name'] not in done]

    t0 = time.time()
    records = list(done.values())
    with open(partial, 'w') as fh:
        for rec in records:
            fh.write(json.dumps(rec) + '\n')
        fh.flush()
        init = (args.engine, args.policy, args.budget, args.cap, args.warmup)
        if todo:
            if args.workers > 1:
                ctx = mp.get_context('spawn')
                with ctx.Pool(args.workers, initializer=_init_worker, initargs=init) as pool:
                    for rec in pool.imap_unordered(_work, todo, chunksize=1):
                        records.append(rec)
                        fh.write(json.dumps(rec) + '\n')
                        fh.flush()
                        _progress(rec, len(records), len(rows))
            else:
                _init_worker(*init)
                for job in todo:
                    rec = _work(job)
                    records.append(rec)
                    fh.write(json.dumps(rec) + '\n')
                    fh.flush()
                    _progress(rec, len(records), len(rows))
        os.fsync(fh.fileno())
    records.sort(key=lambda r: r['index'])
    with open(partial, 'w') as fh:
        for rec in records:
            fh.write(json.dumps(rec) + '\n')
    os.replace(partial, out_path)
    summary = summarize(records, args, panel_path, panel_sha, time.time() - t0)
    (args.out / f'{args.tag}.summary.json').write_text(json.dumps(summary, indent=1) + '\n')
    print(f"[run_ladder] {summary['solved']}/{summary['rows']} solved, {summary['verified']} verified, "
          f"{summary['errors']} errors, {summary['run_wall']:.1f}s -> {out_path}")
    for lvl, s in summary['by_level'].items():
        print(f"   level {lvl:>2}: {s['solved']:3}/{s['rows']:<3}  median nodes {s['median_nodes_solved']}")
    return 1 if summary['errors'] or summary['solved'] != summary['verified'] else 0


def _progress(rec, k, n):
    flag = 'ok ' if rec['solved'] and rec['verified'] else ('ERR' if rec.get('error') else ' - ')
    print(f"  [{k:4}/{n}] {flag} {rec['name']:16} L{rec.get('level', '?'):>2} nodes={rec['nodes']:>9,} "
          f"{rec.get('search_wall', 0):7.2f}s{('  ' + rec['error']) if rec.get('error') else ''}", flush=True)


if __name__ == '__main__':
    sys.exit(main())
