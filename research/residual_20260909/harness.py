"""Experiment harness: run one registered policy over a CSV panel of AC pairs.

For each panel row, serially:

  1. validate that ``r1`` and ``r2`` use only the generator alphabet
     ``xXyY`` (the same check ``strict_donor_route_fast.match`` makes);
  2. run the chosen policy, timing wall and CPU clocks around the call;
  3. if solved, decode the mixed certificate to elementary AC moves with
     ``certificate_decoder_compact_moves.decode_elementary`` (passing
     ``elementary_tail`` through when the policy produced one, exactly as
     ``run_full_ac19_final1k.py`` does) and independently replay those moves
     with ``certificate_decoder.replay_elementary``, requiring the replayed
     pair to reduce to the trivial basis ``{x, y}``.

One JSON record per row is appended to ``<out>/<tag>.jsonl`` -- written
incrementally to a same-directory ``.partial`` file (flushed after every
row, so a crash mid-run leaves a readable partial) and atomically renamed to
the final path once the whole panel has run. A ``<out>/<tag>.summary.json``
aggregate is written afterward.

Example:
    PYTHONPATH=. python3 -m research.residual_20260909.harness \\
        --panel research/residual_20260909/panels/smoke_solved.csv \\
        --policy frozen --budget 1000 \\
        --out research/residual_20260909/screens --tag smoke_frozen
"""
import argparse
import csv
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

for _var in ('NUMBA_NUM_THREADS', 'OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ.setdefault(_var, '1')

from research.supermoves_20260908.certificate_decoder import replay_elementary
from research.supermoves_20260908.certificate_decoder_compact_moves import decode_elementary

# ``research.residual_20260909.policies`` is imported lazily (inside main(), and
# by callers such as census_run.py) rather than at module load time: it is
# under active extension by other agents, and importing this module -- to
# reuse run_row/_validate_word/_git_head/etc. -- should not fail just because
# the registry is mid-edit elsewhere.

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]  # research/residual_20260909 -> research -> repo root
ALPHABET = frozenset('xXyY')
WARMUP_PAIR = ('YYXyX', 'YXXyx')


def _validate_word(word, which, row_name):
    """Raise ValueError unless ``word`` is a nonempty string over xXyY."""
    if not isinstance(word, str) or not word or any(c not in ALPHABET for c in word):
        raise ValueError(f'row {row_name!r}: {which} must be a nonempty word over xXyY, got {word!r}')


def load_panel(path, limit=None, names=None):
    """Read a ``name,r1,r2`` CSV panel, optionally filtered/truncated."""
    with open(path, newline='') as stream:
        rows = list(csv.DictReader(stream))
    missing_cols = {'name', 'r1', 'r2'} - set(rows[0].keys() if rows else ())
    if missing_cols:
        raise ValueError(f'panel {path} missing required column(s): {sorted(missing_cols)}')
    if names is not None:
        wanted = list(names)
        by_name = {row['name']: row for row in rows}
        missing = [name for name in wanted if name not in by_name]
        if missing:
            raise ValueError(f'panel {path} is missing requested --names entries: {missing}')
        rows = [by_name[name] for name in wanted]
    if limit is not None:
        rows = rows[:limit]
    return rows


def _source_files():
    """The dependency set the campaign cares about: the frozen census
    modules (read-only) and this harness's own package."""
    files = []
    for directory in (ROOT / 'research' / 'supermoves_20260908', HERE):
        files.extend(sorted(directory.glob('*.py')))
    return files


def _source_hashes():
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in _source_files()}


def _git_head():
    try:
        return subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def _versions():
    versions = dict(python=sys.version.split()[0], platform=platform.platform())
    for name in ('numpy', 'numba', 'llvmlite'):
        try:
            versions[name] = __import__(name).__version__
        except Exception:
            versions[name] = None
    return versions


def run_row(policy_fn, name, pair, budget):
    """Run one panel row through ``policy_fn`` and, on a solve, decode plus
    independently replay the certificate. Returns the JSON-serializable
    record. Exceptions propagate to the caller, which is responsible for
    catching them per row so the run keeps going.
    """
    record = dict(name=name, pair=list(pair), budget=budget)
    wall0, cpu0 = time.perf_counter(), time.process_time()
    result = policy_fn(pair, budget)
    record.update(
        search_wall=time.perf_counter() - wall0,
        search_cpu=time.process_time() - cpu0,
        solved=bool(result.get('solved')),
        nodes_explored=result.get('nodes_explored'),
        policy_route=result.get('policy_route'),
        best_state=result.get('best_state'),
        min_total_length_seen=result.get('min_total_length_seen'),
    )
    if record['solved']:
        wall1, cpu1 = time.perf_counter(), time.process_time()
        moves = decode_elementary(pair, result['states'], result['steps'], result.get('elementary_tail'))
        replayed = replay_elementary(pair, moves)
        # The census runner (run_full_ac19_final1k.py) requires literal
        # equality to ['x', 'y']. decode_elementary itself already asserts
        # exactly that internally (certificate_decoder_fast.py, end of
        # decode_elementary) before ever returning, by Nielsen-reducing
        # whatever basis the search actually stopped on -- so for any
        # decode that returns without raising, this sorted/lower-cased
        # check and the census's literal check are guaranteed equivalent.
        # We use the slightly more tolerant form here because this harness
        # also runs policies the census never exercised (aut_edges_s20,
        # ordinary_T, ...), and a tolerant *independent* check is a better
        # bug detector than one that silently inherits decode_elementary's
        # own internal assumption about orientation.
        verified = sorted(word.lower() for word in replayed) == ['x', 'y']
        record.update(
            verified=verified,
            certificate_wall=time.perf_counter() - wall1,
            certificate_cpu=time.process_time() - cpu1,
            elementary_count=len(moves),
            states=result['states'],
            steps=result['steps'],
        )
        if 'elementary_tail' in result:
            record['elementary_tail'] = result['elementary_tail']
    else:
        record.update(verified=False, certificate_wall=0., certificate_cpu=0., elementary_count=0)
    return record


def _summarize(records, args, panel_sha256, warmup_wall):
    solved = sum(record['solved'] for record in records)
    verified = sum(record.get('verified', False) for record in records)
    errors = sum('error' in record for record in records)
    unsolved_names = [record['name'] for record in records if not record['solved']]
    total_nodes = sum(record.get('nodes_explored') or 0 for record in records)
    elementary_counts = [record['elementary_count'] for record in records if record.get('solved') and 'elementary_count' in record]
    route_counts = {}
    for record in records:
        route = record.get('policy_route')
        route_counts[route] = route_counts.get(route, 0) + 1
    clocks = {}
    for key in ('search_wall', 'search_cpu', 'certificate_wall', 'certificate_cpu'):
        values = [record.get(key) or 0. for record in records]
        clocks[key] = dict(sum=sum(values), max=max(values) if values else 0.)
    return dict(
        rows=len(records), solved=solved, verified=verified, errors=errors,
        unsolved_names=unsolved_names, total_nodes_explored=total_nodes,
        mean_elementary_count=(sum(elementary_counts) / len(elementary_counts)) if elementary_counts else None,
        route_counts=route_counts, clocks=clocks,
        panel=str(args.panel), panel_sha256=panel_sha256,
        policy=args.policy, budget=args.budget, tag=args.tag,
        limit=args.limit, names=args.names.split(',') if args.names else None,
        warmup_wall=warmup_wall,
        git_head=_git_head(), versions=_versions(),
        source_sha256=_source_hashes(),
    )


def main(argv=None):
    from research.residual_20260909.policies import REGISTRY  # lazy: see note above
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--panel', required=True, type=Path, help='CSV with columns name,r1,r2')
    parser.add_argument('--policy', required=True, choices=sorted(REGISTRY), help='registered policy name')
    parser.add_argument('--budget', required=True, type=int, help='shared work-unit budget per row')
    parser.add_argument('--out', required=True, type=Path, help='output directory')
    parser.add_argument('--tag', required=True, help='output file stem: <out>/<tag>.jsonl')
    parser.add_argument('--limit', type=int, default=None, help='only run the first N panel rows')
    parser.add_argument('--names', default=None, help='comma-separated subset of panel names to run, in that order')
    parser.add_argument('--force', action='store_true', help='overwrite an existing <tag>.jsonl')
    parser.add_argument('--warmup', action=argparse.BooleanOptionalAction, default=True,
                        help='run the policy once on a fixed warmup pair before timing (default: on)')
    args = parser.parse_args(argv)

    if args.budget < 1:
        raise ValueError('--budget must be a positive integer')
    args.out.mkdir(parents=True, exist_ok=True)
    final_path = args.out / f'{args.tag}.jsonl'
    partial_path = args.out / f'{args.tag}.jsonl.partial'
    if final_path.exists() and not args.force:
        raise SystemExit(f'refusing to overwrite existing {final_path} (pass --force)')

    panel_bytes = args.panel.read_bytes()
    panel_sha256 = hashlib.sha256(panel_bytes).hexdigest()
    names = args.names.split(',') if args.names else None
    rows = load_panel(args.panel, limit=args.limit, names=names)

    policy_fn = REGISTRY[args.policy]

    warmup_wall = None
    if args.warmup:
        warm_started = time.perf_counter()
        policy_fn(WARMUP_PAIR, args.budget)
        warmup_wall = time.perf_counter() - warm_started

    records = []
    with partial_path.open('w') as stream:
        for row in rows:
            name, r1, r2 = row['name'], row['r1'], row['r2']
            pair = (r1, r2)
            try:
                _validate_word(r1, 'r1', name)
                _validate_word(r2, 'r2', name)
                record = run_row(policy_fn, name, pair, args.budget)
                record['policy'] = args.policy
            except Exception as error:
                record = dict(name=name, pair=list(pair), budget=args.budget, policy=args.policy,
                              solved=False, verified=False, error=str(error), error_type=type(error).__name__)
            stream.write(json.dumps(record, separators=(',', ':')) + '\n')
            stream.flush()
            os.fsync(stream.fileno())
            records.append(record)
    partial_path.replace(final_path)

    summary = _summarize(records, args, panel_sha256, warmup_wall)
    summary_path = args.out / f'{args.tag}.summary.json'
    summary_path.write_text(json.dumps(summary, indent=2) + '\n')

    print(json.dumps(dict(
        rows=summary['rows'], solved=summary['solved'], verified=summary['verified'],
        errors=summary['errors'], route_counts=summary['route_counts'],
        out=str(final_path), summary=str(summary_path),
    ), indent=2))
    return summary


if __name__ == '__main__':
    main()
