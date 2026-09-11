"""Fail-closed aggregation for a census_run.py result directory.

Generalizes ``research/supermoves_20260908/summarize_full_ac19_final1k.py``
to any ``--input`` and any range of it (a 300-row validation slice, the full
72,779-row census, the 727-row residual, ...): "complete" here means the
``manifest_*.json`` files present in ``--result-dir`` exactly tile some
contiguous ``[range_start, range_end)`` with no gaps or overlaps, and every
row in that range has a finalized, internally-consistent record -- not that
the range happens to be the whole input file.

Fails closed (raises, writes nothing) on: a ``.partial`` file still present;
no manifests; manifests that disagree on input hash, population, policy,
budget, or source/table hashes; a gap or overlap between manifest
intervals or between shard row indices; a shard whose finalized line count
does not match its filename range; a row naming a shard it does not belong
to (or two shards both owning it); a row whose ``name``/``pair`` does not
match ``--input`` at that index; a duplicate ``name`` anywhere in the
result set; a row recording an ``error``; ``nodes_explored`` exceeding that
row's own ``budget``; or ``solved != verified``.

On success writes, atomically, into ``--result-dir``:

- ``SUMMARY.json`` -- rows, solved, unsolved, verified, total/max nodes,
  elementary moves total, per-route counts, summed clocks, input sha256,
  source sha256 map, table sha256 map, and the shard file list;
- ``unsolved.csv`` -- ``index,name,r1,r2,nodes_explored,route``;
- ``RESULTS.md`` -- a factual report in the style of
  ``results/heuristic_search/ac19_final_policy_full_1k/RESULTS.md``.

With ``--baseline DIR`` (a finalized census_run.py or
run_full_ac19_final1k.py result directory, e.g.
``results/heuristic_search/ac19_final_policy_full_1k/``), also compares
solved names against that baseline over the same index range and writes
``COMPARISON.md`` and ``comparison.json`` -- gained (solved now, not in the
baseline), lost (solved in the baseline, not now), each broken down by
route.

Example:
    PYTHONPATH=. python3 -m research.residual_20260909.census_summarize \\
        --input data/AC19_extended_aut_min.csv \\
        --result-dir results/residual_scratch/frozen_1k \\
        --baseline results/heuristic_search/ac19_final_policy_full_1k
"""
import argparse
import hashlib
import json
import os
import re
from collections import Counter
from pathlib import Path

from research.residual_20260909.census_run import read_rows

SHARD_RE = re.compile(r'rows_(\d{5})_(\d{5})\.jsonl$')
FIXED_KEYS = ('input_sha256', 'population', 'policy', 'budget', 'source_sha256', 'table_sha256')


def _atomic_write(path, text):
    partial = path.with_suffix(path.suffix + '.partial')
    partial.write_text(text)
    os.replace(partial, path)


def _load_manifests(result_dir):
    manifests = []
    for path in sorted(result_dir.glob('manifest_*.json')):
        item = json.loads(path.read_text())
        item['_file'] = path.name
        manifests.append(item)
    return manifests


def summarize(input_path, result_dir):
    """Aggregate one result directory. Returns the SUMMARY.json dict."""
    input_path, result_dir = Path(input_path), Path(result_dir)
    if list(result_dir.glob('*.partial')):
        raise ValueError('unfinished .partial file(s) present in ' + str(result_dir))

    input_bytes = input_path.read_bytes()
    input_sha256 = hashlib.sha256(input_bytes).hexdigest()
    source_rows = read_rows(input_path)
    population = len(source_rows)

    manifests = _load_manifests(result_dir)
    if not manifests:
        raise ValueError('no manifest_*.json files in ' + str(result_dir))

    fixed = None
    for item in manifests:
        if item.get('input_sha256') != input_sha256:
            raise ValueError(f"{item['_file']}: input_sha256 does not match --input")
        if item.get('population') != population:
            raise ValueError(f"{item['_file']}: population does not match --input row count")
        current = {key: item.get(key) for key in FIXED_KEYS}
        if fixed is None:
            fixed = current
        elif current != fixed:
            raise ValueError(f"{item['_file']}: disagrees with other manifests on policy/budget/"
                            "input/source/table provenance")
    policy_name, budget = fixed['policy'], fixed['budget']

    intervals = sorted((item['offset'], item['end'], item['_file']) for item in manifests)
    for left, right in zip(intervals, intervals[1:]):
        if left[1] > right[0]:
            raise ValueError(f'overlapping manifest intervals: {left[2]} and {right[2]}')
        if left[1] < right[0]:
            raise ValueError(f'gap between manifest intervals: {left[2]} ends at {left[1]}, '
                            f'{right[2]} starts at {right[0]}')
    range_start, range_end = intervals[0][0], intervals[-1][1]

    records, routes, name_seen = {}, {}, set()
    totals = Counter()
    clocks = Counter()
    shards = []
    for path in sorted(result_dir.glob('rows_*.jsonl')):
        match = SHARD_RE.fullmatch(path.name)
        if not match:
            continue
        start, stop = map(int, match.groups())
        owners = [name for ms, me, name in intervals if ms <= start and stop <= me]
        if len(owners) != 1:
            raise ValueError(f'{path.name}: not owned by exactly one manifest ({len(owners)} candidates)')
        seen = 0
        with path.open() as stream:
            for line in stream:
                row = json.loads(line)
                seen += 1
                index = row.get('index')
                if type(index) is not int or isinstance(index, bool) or not start <= index < stop:
                    raise ValueError(f'{path.name}: row with bad or out-of-range index {index!r}')
                if index in records:
                    raise ValueError(f'{path.name}: duplicate row index {index}')
                if not 0 <= index < population:
                    raise ValueError(f'{path.name}: index {index} outside input population {population}')
                expected = source_rows[index]
                if row.get('name') != expected['name']:
                    raise ValueError(f"{path.name}: row {index} name {row.get('name')!r} != "
                                    f"input name {expected['name']!r}")
                if row.get('pair') != [expected['r1'], expected['r2']]:
                    raise ValueError(f'{path.name}: row {index} pair does not match --input')
                name = row['name']
                if name in name_seen:
                    raise ValueError(f'duplicate name across result set: {name!r}')
                name_seen.add(name)
                if 'error' in row:
                    raise ValueError(f"{path.name}: row {index} ({name}) recorded an error: {row['error']!r}")
                nodes = row.get('nodes_explored')
                row_budget = row.get('budget', budget)
                if type(nodes) is not int or isinstance(nodes, bool) or not 0 <= nodes <= row_budget:
                    raise ValueError(f'{path.name}: row {index} ({name}) charges {nodes!r} '
                                    f'exceed its budget {row_budget!r}')
                solved = row.get('solved') is True
                verified = row.get('verified') is True
                if solved != verified:
                    raise ValueError(f'{path.name}: row {index} ({name}) solved={solved} != verified={verified}')
                route = row.get('policy_route') or 'unknown'
                records[index] = dict(index=index, name=name, pair=row['pair'], solved=solved,
                                     nodes_explored=nodes, route=route)
                totals['solved'] += solved
                totals['verified'] += verified
                totals['nodes'] += nodes
                totals['max_nodes'] = max(totals['max_nodes'], nodes)
                totals['elementary_moves'] += row.get('elementary_count') or 0
                route_counts = routes.setdefault(route, Counter())
                route_counts['rows'] += 1
                route_counts['solved'] += solved
                route_counts['unsolved'] += not solved
                for key in ('search_wall', 'search_cpu', 'certificate_wall', 'certificate_cpu'):
                    clocks[key] += row.get(key) or 0.
        if seen != stop - start:
            raise ValueError(f'{path.name}: {seen} lines but filename declares {stop - start} rows')
        shards.append(path.name)

    indices = sorted(records)
    if indices != list(range(range_start, range_end)):
        raise ValueError('shard row indices do not exactly tile the manifest-declared range '
                        f'[{range_start}, {range_end}) -- gap or overlap in the row data itself')

    summary = dict(
        complete=True, range_start=range_start, range_end=range_end, rows=len(records),
        solved=totals['solved'], unsolved=len(records) - totals['solved'], verified=totals['verified'],
        nodes=totals['nodes'], max_nodes_explored=totals['max_nodes'],
        elementary_moves=totals['elementary_moves'],
        routes={name: dict(counts) for name, counts in sorted(routes.items())},
        clocks=dict(clocks), input_sha256=input_sha256, input_path=str(input_path),
        policy=policy_name, budget=budget,
        source_sha256=fixed['source_sha256'], table_sha256=fixed['table_sha256'],
        manifests=[name for _, _, name in intervals], shards=shards,
    )

    unsolved = [records[i] for i in indices if not records[i]['solved']]
    csv_rows = ['index,name,r1,r2,nodes_explored,route'] + [
        f"{r['index']},{r['name']},{r['pair'][0]},{r['pair'][1]},{r['nodes_explored']},{r['route']}"
        for r in unsolved]

    route_rows = ''.join(
        f"| `{name}` | {counts['rows']} | {counts['solved']} | {counts['unsolved']} |\n"
        for name, counts in summary['routes'].items())
    markdown = (
        f"# Census run summary\n\n"
        f"Range: rows **[{range_start}, {range_end})** of `{input_path}` "
        f"({len(records)} rows) -- policy **`{policy_name}`**, budget **{budget}**.\n\n"
        f"Solved: **{summary['solved']}/{len(records)}** (verified certificates: **{summary['verified']}**). "
        f"Unsolved: **{summary['unsolved']}**. Errors: **0** (fail-closed on any error row). "
        f"Maximum observed per-row charge: **{summary['max_nodes_explored']}** (limit {budget}).\n\n"
        f"Total charged units: **{summary['nodes']}**. Search wall/CPU: "
        f"**{clocks['search_wall']:.6f}s / {clocks['search_cpu']:.6f}s**. "
        f"Certificate wall/CPU: **{clocks['certificate_wall']:.6f}s / {clocks['certificate_cpu']:.6f}s**. "
        f"Total elementary moves: **{summary['elementary_moves']}**.\n\n"
        "## Outcomes by policy route\n\n"
        "| Route | Rows | Solved | Unsolved |\n|---|---:|---:|---:|\n"
        f"{route_rows}\n"
        "## Provenance\n\n"
        f"Input: `{input_path}`, SHA-256 `{input_sha256}`. Source hashes cover "
        f"{len(fixed['source_sha256'])} files under `research/supermoves_20260908/` and "
        f"`research/residual_20260909/`; table hashes cover {len(fixed['table_sha256'])} pickle "
        "file(s) under `research/residual_20260909/tables/`, all recorded in the interval "
        f"`manifest_*.json` files: {', '.join(summary['manifests'])}.\n"
    )

    _atomic_write(result_dir / 'SUMMARY.json', json.dumps(summary, indent=2) + '\n')
    _atomic_write(result_dir / 'unsolved.csv', '\n'.join(csv_rows) + '\n')
    _atomic_write(result_dir / 'RESULTS.md', markdown)
    return summary


def _load_baseline(baseline_dir, range_start, range_end):
    """name -> (solved, route) for every baseline row whose shard file range
    overlaps [range_start, range_end). Reads only overlapping shard files."""
    baseline_dir = Path(baseline_dir)
    out = {}
    for path in sorted(baseline_dir.glob('rows_*.jsonl')):
        match = SHARD_RE.fullmatch(path.name)
        if not match:
            continue
        start, stop = map(int, match.groups())
        if stop <= range_start or start >= range_end:
            continue
        with path.open() as stream:
            for line in stream:
                row = json.loads(line)
                index = row.get('index')
                if index is None or not range_start <= index < range_end:
                    continue
                out[row['name']] = dict(solved=row.get('solved') is True,
                                        route=row.get('route') or row.get('policy_route') or 'unknown')
    return out


def compare_to_baseline(summary, result_dir, baseline_dir):
    """Compare this summary's solved names to a baseline result directory
    over the same index range. Writes COMPARISON.md and comparison.json."""
    result_dir, baseline_dir = Path(result_dir), Path(baseline_dir)
    baseline = _load_baseline(baseline_dir, summary['range_start'], summary['range_end'])

    # name -> {solved, route}, read back from this run's own finalized shard files
    # (cheap: the same files summarize() just walked).
    now = {}
    for path in sorted(result_dir.glob('rows_*.jsonl')):
        match = SHARD_RE.fullmatch(path.name)
        if not match:
            continue
        with path.open() as stream:
            for line in stream:
                row = json.loads(line)
                now[row['name']] = dict(solved=row.get('solved') is True, route=row.get('policy_route') or 'unknown')

    solved_now_names = {name for name, r in now.items() if r['solved']}
    solved_baseline_names = {name for name, r in baseline.items() if r['solved']}
    common_names = set(now) & set(baseline)
    missing_from_baseline = sorted(set(now) - set(baseline))

    gained = sorted(solved_now_names - solved_baseline_names)
    lost = sorted(solved_baseline_names - solved_now_names)
    common_solved = solved_now_names & solved_baseline_names

    gained_by_route = Counter(now[name]['route'] for name in gained)
    lost_by_route = Counter(baseline[name]['route'] for name in lost)

    comparison = dict(
        range_start=summary['range_start'], range_end=summary['range_end'],
        rows_compared=len(common_names), rows_missing_from_baseline=len(missing_from_baseline),
        solved_now=len(solved_now_names), solved_baseline=len(solved_baseline_names),
        common_solved=len(common_solved),
        gained=dict(count=len(gained), names=gained, by_route=dict(gained_by_route)),
        lost=dict(count=len(lost), names=lost, by_route=dict(lost_by_route)),
        missing_from_baseline=missing_from_baseline,
        baseline_dir=str(baseline_dir), result_dir=str(result_dir),
    )

    def _name_list(names, cap=30):
        shown = ', '.join(f'`{n}`' for n in names[:cap])
        more = f' (+{len(names) - cap} more)' if len(names) > cap else ''
        return (shown + more) if names else '(none)'

    markdown = (
        f"# Comparison to baseline\n\n"
        f"Baseline: `{baseline_dir}`. Range compared: rows [{summary['range_start']}, "
        f"{summary['range_end']}) ({comparison['rows_compared']} rows present in both; "
        f"{comparison['rows_missing_from_baseline']} present here but not found in the baseline range).\n\n"
        f"Solved now: **{comparison['solved_now']}**. Solved in baseline: **{comparison['solved_baseline']}**. "
        f"Common solved: **{comparison['common_solved']}**.\n\n"
        f"## Gained ({comparison['gained']['count']}) -- solved now, not in the baseline\n\n"
        f"By route (this run): " +
        ', '.join(f'`{route}`: {count}' for route, count in sorted(gained_by_route.items())) + "\n\n"
        f"{_name_list(gained)}\n\n"
        f"## Lost ({comparison['lost']['count']}) -- solved in the baseline, not now\n\n"
        f"By route (baseline): " +
        ', '.join(f'`{route}`: {count}' for route, count in sorted(lost_by_route.items())) + "\n\n"
        f"{_name_list(lost)}\n"
    )

    _atomic_write(result_dir / 'comparison.json', json.dumps(comparison, indent=2) + '\n')
    _atomic_write(result_dir / 'COMPARISON.md', markdown)
    return comparison


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--result-dir', required=True, type=Path)
    parser.add_argument('--baseline', type=Path, default=None,
                        help='a finalized result dir to compare solved names against')
    args = parser.parse_args(argv)

    summary = summarize(args.input, args.result_dir)
    print(json.dumps({k: summary[k] for k in ('rows', 'solved', 'unsolved', 'verified', 'nodes')}))

    if args.baseline is not None:
        comparison = compare_to_baseline(summary, args.result_dir, args.baseline)
        print(json.dumps({k: comparison[k] for k in ('solved_now', 'solved_baseline', 'common_solved')} |
                         {'gained': comparison['gained']['count'], 'lost': comparison['lost']['count']}))
    return summary


if __name__ == '__main__':
    main()
