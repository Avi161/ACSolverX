"""Census-scale runner: apply one registered policy to every row of a CSV
(``name,r1,r2,...``), with the same audit discipline as
``research/supermoves_20260908/run_full_ac19_final1k.py`` -- atomic
per-shard JSONL, a provenance manifest, one thread per worker -- but
generalized to any input file (the full 72,779-row census, the 727-row
residual, a panel, ...) and any registered policy, with optional
multi-process parallelism across contiguous row shards.

Per row this records exactly the fields ``harness.py`` records (both share
the same ``run_row``/``_validate_word`` implementation, imported from
``harness.py``, so a row processed by both tools produces the same fields
from the same inputs), plus ``index`` -- the row's 0-based position in
``--input``.

Provenance and resume
----------------------
Each invocation computes a *fingerprint*: the input file's SHA-256, the
policy name, the budget, the SHA-256 of every ``research/supermoves_20260908/
*.py`` and ``research/residual_20260909/*.py`` source file, and the SHA-256
of every ``research/residual_20260909/tables/*.pkl`` and ``*.npz`` table file. This is
written to ``manifest_<offset>_<end>.json`` (one per invocation, covering
its whole ``[offset, end)`` row range) -- "verify the input SHA-256" here
means computing and recording it, and cross-checking it (with the rest of
the fingerprint) against any manifest already on file for the same
``[offset, end)`` interval; there is no single hard-coded expected hash,
because unlike the frozen census runner this tool is meant to run on
different inputs.

The row range is tiled into contiguous shards of ``--shard-size`` rows
(``rows_<start>_<stop>.jsonl``), the same unit ``run_full_ac19_final1k.py``
uses. For each shard, before doing any work:

- if no finalized file for it exists, it is (re)computed;
- if a finalized file exists and an on-disk manifest whose interval covers
  the shard has a fingerprint matching this invocation's, the shard is
  **skipped** (resume) -- this requires resumed and original invocations to
  agree on ``--shard-size``/``--offset`` alignment, exactly like the
  original census runner's shard tiling;
- otherwise (finalized file exists with no matching covering manifest, i.e.
  unknown or conflicting provenance) the run refuses, unless ``--force``.

Parallelism
-----------
``--workers 1`` (default) processes shards one at a time in this process,
serially within each shard, one thread (env vars pinned before the first
policy-touching import). ``--workers N>1`` hands the shard list to a
``multiprocessing`` pool of ``N`` processes (the ``spawn`` start method, so
each worker is a fresh interpreter -- the one-thread env vars are set
*before* anything numba-adjacent is imported in that process, which matters
for numba/OpenMP/OpenBLAS thread-pool initialization). Each worker still
processes its shards one row at a time, single-threaded; a worker runs its
own JIT warmup once, before its first shard.

Example:
    PYTHONPATH=. python3 -m research.residual_20260909.census_run \\
        --input data/AC19_extended_aut_min.csv --policy frozen --budget 1000 \\
        --out results/residual_scratch/frozen_1k --offset 0 --limit 300
"""
import argparse
import csv
import hashlib
import json
import multiprocessing
import os
import time
from pathlib import Path

for _var in ('NUMBA_NUM_THREADS', 'OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ.setdefault(_var, '1')

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TABLES_DIR = HERE / 'tables'
FINGERPRINT_KEYS = ('input_sha256', 'population', 'policy', 'budget', 'source_sha256', 'table_sha256')


def read_rows(input_path):
    """Parse a ``name,r1,r2,...`` CSV into a list of row dicts, in order."""
    with open(input_path, newline='') as stream:
        rows = list(csv.DictReader(stream))
    missing = {'name', 'r1', 'r2'} - set(rows[0].keys() if rows else ())
    if missing:
        raise ValueError(f'{input_path}: missing required column(s) {sorted(missing)}')
    return rows


def table_hashes():
    """SHA-256 of every research/residual_20260909/tables/*.pkl and *.npz
    table file (the compact ``.npz`` tables joined in round 2; the round-1
    manifests, written before that, list the ``.pkl`` files only)."""
    if not TABLES_DIR.is_dir():
        return {}
    paths = sorted(list(TABLES_DIR.glob('*.pkl')) + list(TABLES_DIR.glob('*.npz')))
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in paths}


def _shard_intervals(offset, end, shard_size):
    return [(start, min(start + shard_size, end)) for start in range(offset, end, shard_size)]


def _shard_paths(out_dir, start, stop):
    final_path = out_dir / f'rows_{start:05d}_{stop:05d}.jsonl'
    return final_path, final_path.with_suffix(final_path.suffix + '.partial')


def _shard_totals(records):
    totals = dict(rows=0, solved=0, verified=0, errors=0, nodes=0, elementary_moves=0,
                  search_wall=0., search_cpu=0., certificate_wall=0., certificate_cpu=0.)
    for record in records:
        totals['rows'] += 1
        totals['solved'] += bool(record.get('solved'))
        totals['verified'] += bool(record.get('verified'))
        totals['errors'] += 'error' in record
        totals['nodes'] += record.get('nodes_explored') or 0
        totals['elementary_moves'] += record.get('elementary_count') or 0
        for key in ('search_wall', 'search_cpu', 'certificate_wall', 'certificate_cpu'):
            totals[key] += record.get(key) or 0.
    return totals


def _read_shard_totals(path):
    """Totals for an already-finalized shard file (used for resumed/skipped shards)."""
    records = []
    with open(path) as stream:
        for line in stream:
            records.append(json.loads(line))
    return _shard_totals(records)


# --------------------------------------------------------------------------
# Worker-process state (multiprocessing pool with an initializer: the JIT
# warmup and policy import happen once per worker process, not once per
# shard task).
# --------------------------------------------------------------------------
_worker = {}


def _init_worker(input_path_str, policy_name, budget, warmup):
    for var in ('NUMBA_NUM_THREADS', 'OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
        os.environ[var] = '1'
    from research.residual_20260909.harness import WARMUP_PAIR, _validate_word, run_row
    from research.residual_20260909.policies import REGISTRY
    _worker['rows'] = read_rows(Path(input_path_str))
    _worker['policy_name'] = policy_name
    _worker['policy_fn'] = REGISTRY[policy_name]
    _worker['budget'] = budget
    _worker['run_row'] = run_row
    _worker['validate_word'] = _validate_word
    warmup_wall = None
    if warmup:
        started = time.perf_counter()
        _worker['policy_fn'](WARMUP_PAIR, budget)
        warmup_wall = time.perf_counter() - started
    _worker['warmup_wall'] = warmup_wall


def _run_shard(start, stop, out_dir):
    """Process rows [start, stop) using the current process's worker state
    (set up by ``_init_worker``), writing rows_<start>_<stop>.jsonl
    atomically. Returns a small progress summary, not the row records
    themselves (those stay on disk -- census_summarize.py reads them back)."""
    rows, policy_fn, policy_name, budget = (
        _worker['rows'], _worker['policy_fn'], _worker['policy_name'], _worker['budget'])
    run_row, validate_word = _worker['run_row'], _worker['validate_word']
    final_path, partial_path = _shard_paths(out_dir, start, stop)
    records = []
    shard_started = time.perf_counter()
    with partial_path.open('w') as stream:
        for index in range(start, stop):
            row = rows[index]
            name, r1, r2 = row['name'], row['r1'], row['r2']
            record = dict(index=index, name=name, pair=[r1, r2], budget=budget, policy=policy_name)
            try:
                validate_word(r1, 'r1', name)
                validate_word(r2, 'r2', name)
                result = run_row(policy_fn, name, (r1, r2), budget)
                record.update(result)
            except Exception as error:
                record.update(solved=False, verified=False, error=str(error), error_type=type(error).__name__)
            stream.write(json.dumps(record, separators=(',', ':')) + '\n')
            stream.flush()
            os.fsync(stream.fileno())
            records.append(record)
    partial_path.replace(final_path)
    totals = _shard_totals(records)
    return dict(start=start, stop=stop, final_path=str(final_path), resumed=False,
                shard_wall=time.perf_counter() - shard_started, warmup_wall=_worker.get('warmup_wall'),
                **totals)


def _pool_task(payload):
    start, stop, out_dir_str = payload
    return _run_shard(start, stop, Path(out_dir_str))


def _covering_manifest(out_dir, start, stop):
    """The most recent manifest_*.json in out_dir whose recorded interval
    covers [start, stop), or None. This includes the manifest this very
    invocation just (re)wrote for its own [offset, end) -- by the time
    shards are scanned that manifest already reflects the current
    fingerprint, so a same-shape resume (same offset/limit/policy/budget/
    input) is its own proof of matching provenance."""
    best = None
    for path in sorted(out_dir.glob('manifest_*.json')):
        try:
            item = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        if item.get('offset') is None or item.get('end') is None:
            continue
        if item['offset'] <= start and stop <= item['end']:
            best = item
    return best


def _fingerprint_matches(manifest_item, fingerprint):
    return all(manifest_item.get(key) == fingerprint[key] for key in FINGERPRINT_KEYS)


def run_census(input_path, policy_name, budget, out_dir, offset, limit, shard_size, workers, warmup, force):
    """Run one census-scale invocation. Returns the list of per-shard result
    dicts (fresh or resumed) covering [offset, end)."""
    if budget < 1:
        raise ValueError('budget must be a positive integer')
    if shard_size < 1:
        raise ValueError('shard_size must be a positive integer')
    if workers < 1:
        raise ValueError('workers must be a positive integer')
    input_path = Path(input_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    from research.residual_20260909.harness import _git_head, _source_hashes, _versions
    from research.residual_20260909.policies import REGISTRY
    if policy_name not in REGISTRY:
        raise ValueError(f'unknown policy {policy_name!r}; registered: {sorted(REGISTRY)}')

    input_bytes = input_path.read_bytes()
    input_sha256 = hashlib.sha256(input_bytes).hexdigest()
    rows = read_rows(input_path)
    population = len(rows)
    if not 0 <= offset <= population:
        raise ValueError(f'--offset {offset} out of range for {population} input rows')
    end = population if limit is None else min(population, offset + limit)
    if end <= offset:
        raise ValueError('empty row range: --offset/--limit select zero rows')

    fingerprint = dict(input_sha256=input_sha256, population=population, policy=policy_name,
                       budget=budget, source_sha256=_source_hashes(), table_sha256=table_hashes())

    manifest_path = out_dir / f'manifest_{offset:05d}_{end:05d}.json'
    if manifest_path.exists():
        existing = json.loads(manifest_path.read_text())
        if not _fingerprint_matches(existing, fingerprint) and not force:
            raise ValueError(f'{manifest_path} already exists with different provenance '
                            '(input/policy/budget/source/table hashes differ); pass --force to override')

    # Decide, shard by shard, whether an existing finalized file may be
    # trusted (resumed) -- using only manifests that were already on disk
    # before this invocation touched anything. This must happen BEFORE this
    # invocation writes its own manifest below: once that manifest exists it
    # trivially "covers" this invocation's own [offset, end) interval, which
    # would let it silently vouch for files it never actually produced (a
    # stray or foreign rows_*.jsonl dropped into --out would otherwise be
    # accepted as resumable just because a matching-shaped run happened to
    # start).
    shards = _shard_intervals(offset, end, shard_size)
    to_run, results = [], []
    for start, stop in shards:
        final_path, _ = _shard_paths(out_dir, start, stop)
        if not final_path.exists():
            to_run.append((start, stop))
            continue
        if force:
            to_run.append((start, stop))
            continue
        covering = _covering_manifest(out_dir, start, stop)
        if covering is not None and _fingerprint_matches(covering, fingerprint):
            totals = _read_shard_totals(final_path)
            results.append(dict(start=start, stop=stop, final_path=str(final_path), resumed=True,
                                shard_wall=0., warmup_wall=None, **totals))
            print(json.dumps(dict(resumed=True, start=start, stop=stop, **totals)), flush=True)
            continue
        raise ValueError(f'refuse to overwrite finalized shard {final_path} '
                        '(no matching-provenance manifest covers it); pass --force to override')

    manifest = dict(fingerprint, input_path=str(input_path), offset=offset, end=end,
                    shard_size=shard_size, workers=workers, warmup=warmup,
                    git_head=_git_head(), versions=_versions(), created_unix=time.time())
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')

    if to_run:
        if workers == 1:
            _init_worker(str(input_path), policy_name, budget, warmup)
            for start, stop in to_run:
                result = _run_shard(start, stop, out_dir)
                results.append(result)
                print(json.dumps({k: v for k, v in result.items() if k != 'final_path'}), flush=True)
        else:
            ctx = multiprocessing.get_context('spawn')
            payloads = [(start, stop, str(out_dir)) for start, stop in to_run]
            with ctx.Pool(processes=workers, initializer=_init_worker,
                         initargs=(str(input_path), policy_name, budget, warmup)) as pool:
                for result in pool.imap_unordered(_pool_task, payloads):
                    results.append(result)
                    print(json.dumps({k: v for k, v in result.items() if k != 'final_path'}), flush=True)

    results.sort(key=lambda r: r['start'])
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--input', required=True, type=Path, help='CSV with columns name,r1,r2,...')
    parser.add_argument('--policy', required=True, help='registered policy name (see policies.py)')
    parser.add_argument('--budget', type=int, default=1000)
    parser.add_argument('--out', required=True, type=Path, help='output directory')
    parser.add_argument('--offset', type=int, default=0)
    parser.add_argument('--limit', type=int, default=None, help='default: to the end of --input')
    parser.add_argument('--shard-size', type=int, default=1000)
    parser.add_argument('--workers', type=int, default=1)
    parser.add_argument('--warmup', action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument('--force', action='store_true', help='overwrite finalized shards / manifest mismatches')
    args = parser.parse_args(argv)

    started = time.perf_counter()
    results = run_census(args.input, args.policy, args.budget, args.out, args.offset, args.limit,
                         args.shard_size, args.workers, args.warmup, args.force)
    totals = _shard_totals([])
    for key in totals:
        totals[key] = sum(r.get(key, 0) for r in results)
    summary = dict(shards=len(results), resumed=sum(r['resumed'] for r in results),
                   computed=sum(not r['resumed'] for r in results), elapsed=time.perf_counter() - started,
                   **totals)
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == '__main__':
    main()
