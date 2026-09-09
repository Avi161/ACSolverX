"""Fail-closed aggregation for the complete AC19 final-policy census."""
import argparse, csv, hashlib, json, os, re
from collections import Counter
from pathlib import Path

COUNT = 72779
SHA = '7e220253bd0d950378d6ca6944be46ff4b77e49f30067b9ff6c6c6da82f64ae2'
ROW_RE = re.compile(r'rows_(\d{5})_(\d{5})\.jsonl$')


def atomic(path, text):
    partial = path.with_suffix(path.suffix + '.partial')
    if partial.exists():
        raise ValueError('stale output partial')
    partial.write_text(text)
    os.replace(partial, path)


def summarize(input_path, result_dir, expected_count=COUNT, expected_sha=SHA,
              allow_incomplete=False):
    input_path, result_dir = Path(input_path), Path(result_dir)
    data = input_path.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected_sha:
        raise ValueError('input hash mismatch')
    source = list(csv.DictReader(data.decode().splitlines()))
    if len(source) != expected_count:
        raise ValueError('input population mismatch')
    if any(row['name'] != f'ac19_{i}' for i, row in enumerate(source)):
        raise ValueError('input IDs are not sequential')
    if list(result_dir.glob('*.partial')):
        raise ValueError('unfinished partial files present')
    manifests = []
    for path in sorted(result_dir.glob('manifest_*.json')):
        item = json.loads(path.read_text())
        item['_file'] = path.name
        manifests.append(item)
    if not manifests:
        raise ValueError('no manifests')
    policy = None
    intervals = []
    for item in manifests:
        fixed = (item.get('input_sha256'), item.get('population'), item.get('budget'),
                 item.get('cap'), item.get('threads'), item.get('source_sha256'))
        if fixed[:5] != (expected_sha, expected_count, 1000, None, 1):
            raise ValueError('manifest policy mismatch')
        if policy is None:
            policy = fixed
        elif fixed != policy:
            raise ValueError('manifest source disagreement')
        start, end = item.get('offset'), item.get('end')
        if type(start) is not int or type(end) is not int or not 0 <= start < end <= expected_count:
            raise ValueError('invalid manifest interval')
        intervals.append((start, end, item['_file']))
    intervals.sort()
    if any(left[1] > right[0] for left, right in zip(intervals, intervals[1:])):
        raise ValueError('overlapping manifest intervals')

    records = {}
    routes = {}
    totals = Counter()
    clocks = Counter()
    invocation_rows = {name: Counter() for _, _, name in intervals}
    shards = []
    for path in sorted(result_dir.glob('rows_*.jsonl')):
        match = ROW_RE.fullmatch(path.name)
        if not match:
            continue
        start, end = map(int, match.groups())
        owners = [name for ms, me, name in intervals if ms <= start and end <= me]
        if len(owners) != 1:
            raise ValueError('shard is not owned by exactly one manifest')
        owner = owners[0]
        seen = 0
        with path.open() as stream:
            for line in stream:
                row = json.loads(line)
                index = row.get('index')
                seen += 1
                if type(index) is not int or not start <= index < end or index in records:
                    raise ValueError('bad or duplicate row index')
                expected = source[index]
                if row.get('name') != expected['name'] or row.get('pair') != [expected['r1'], expected['r2']]:
                    raise ValueError('row/source mismatch')
                if row.get('budget') != 1000 or not 0 <= row.get('nodes_explored', -1) <= 1000:
                    raise ValueError('row budget mismatch')
                solved = row.get('solved') is True
                verified = row.get('elementary_verified') is True
                if solved != verified or 'error' in row:
                    raise ValueError('unverified solve or error row')
                records[index] = dict(index=index,name=row['name'],pair=row['pair'],
                    solved=solved,nodes_explored=row['nodes_explored'],
                    route=row.get('route','unknown'))
                totals['solved'] += solved
                totals['verified'] += verified
                totals['nodes'] += row['nodes_explored']
                totals['max_nodes'] = max(totals['max_nodes'], row['nodes_explored'])
                totals['elementary_moves'] += row.get('elementary_count', 0)
                route = row.get('route', 'unknown')
                route_counts = routes.setdefault(route, Counter())
                route_counts['rows'] += 1
                route_counts['solved'] += solved
                route_counts['unsolved'] += not solved
                invocation_rows[owner]['rows'] += 1
                invocation_rows[owner]['solved'] += solved
                invocation_rows[owner]['verified'] += verified
                invocation_rows[owner]['nodes'] += row['nodes_explored']
                invocation_rows[owner]['elementary_moves'] += row.get('elementary_count',0)
                for key in ('search_wall', 'search_cpu', 'certificate_wall', 'certificate_cpu'):
                    clocks[key] += row.get(key, 0.0)
                    invocation_rows[owner][key] += row.get(key,0.0)
        if seen != end - start:
            raise ValueError('incomplete finalized shard')
        shards.append(path.name)
    indices = sorted(records)
    complete = indices == list(range(expected_count))
    if not complete and not allow_incomplete:
        raise ValueError('census incomplete')
    if allow_incomplete:
        return {'provisional': True, 'rows': len(records), 'expected_rows': expected_count,
                'next_missing': next((i for i in range(expected_count) if i not in records), None),
                'solved': totals['solved'], 'verified': totals['verified'],
                'nodes': totals['nodes'],
                'routes': {name: dict(counts) for name, counts in sorted(routes.items())},
                'clocks': dict(clocks)}
    if intervals[0][0] != 0 or intervals[-1][1] != expected_count or any(
            left[1] != right[0] for left, right in zip(intervals, intervals[1:])):
        raise ValueError('manifest intervals do not exactly cover census')

    terminal_summaries = {}
    for path in result_dir.glob('rows_*.summary.json'):
        item = json.loads(path.read_text())
        name = item.get('manifest')
        if name not in invocation_rows:
            raise ValueError('summary names unknown manifest')
        end = next(end for _,end,manifest_name in intervals if manifest_name==name)
        if item.get('next_offset') == end:
            if name in terminal_summaries:raise ValueError('duplicate terminal summary')
            terminal_summaries[name]=item
    if terminal_summaries.keys()!=invocation_rows.keys():
        raise ValueError('missing terminal cumulative summary')
    for name,item in terminal_summaries.items():
        expected=invocation_rows[name]
        for key in ('rows','solved','verified','nodes','elementary_moves'):
            if item.get(key,0)!=expected[key]:raise ValueError('terminal summary counter mismatch')
        if item.get('errors',0)!=0:raise ValueError('terminal summary records errors')
        for key in ('search_wall','search_cpu','certificate_wall','certificate_cpu'):
            if abs(item.get(key,0.0)-expected[key])>1e-9:
                raise ValueError('terminal summary clock mismatch')
    runtime = {key: sum(item.get(key, 0.0) for item in terminal_summaries.values())
               for key in ('elapsed', 'warmup_wall', 'cooldown_wall')}
    runtime['execution_plus_warmup_wall'] = runtime['elapsed'] + runtime['warmup_wall']
    summary = {'complete': True, 'rows': expected_count, 'solved': totals['solved'],
               'unsolved': expected_count - totals['solved'], 'verified': totals['verified'],
               'nodes': totals['nodes'], 'max_nodes_explored': totals['max_nodes'],
               'elementary_moves': totals['elementary_moves'],
               'routes': {name: dict(counts) for name, counts in sorted(routes.items())},
               'clocks': dict(clocks),
               'invocation_runtime': runtime, 'input_sha256': expected_sha,
               'input_path': 'data/AC19_extended_aut_min.csv',
               'source_sha256': policy[-1],
               'source_manifests': [name for _, _, name in intervals],
               'source_portability_manifest':
                   'research/supermoves_20260908/FINAL_PORTABILITY_CHECK.json',
               'algorithm_document':
                   'research/supermoves_20260908/AC19_FULL_CENSUS_ALGORITHM.md',
               'shards': shards}
    unsolved = [records[i] for i in indices if not records[i]['solved']]
    csv_rows = ['index,name,r1,r2,nodes_explored,route'] + [
        f"{r['index']},{r['name']},{r['pair'][0]},{r['pair'][1]},{r['nodes_explored']},{r.get('route','')}"
        for r in unsolved]
    route_rows = ''.join(
        f"| `{name}` | {counts['rows']} | {counts['solved']} | {counts['unsolved']} |\n"
        for name, counts in summary['routes'].items())
    markdown = (f"# AC19 final policy census\n\nVerified coverage: **{summary['solved']}/{expected_count}** "
        f"(verified certificates: **{summary['verified']}**).\n\n"
        f"Unsolved: **{summary['unsolved']}**. Errors: **0**. Maximum observed per-row charge: "
        f"**{summary['max_nodes_explored']}** (limit 1,000).\n\n"
        f"Policy budget: **1,000 heterogeneous charged units per row**; ordinary relator cap: **none**. "
        "These units are not calibrated as CPU-equivalent heap pops.\n\n"
        f"Total charged units: **{summary['nodes']}**. Search wall/CPU: "
        f"**{clocks['search_wall']:.6f}s / {clocks['search_cpu']:.6f}s**. "
        f"Certificate wall/CPU: **{clocks['certificate_wall']:.6f}s / {clocks['certificate_cpu']:.6f}s**.\n\n"
        f"Summed invocation elapsed time: **{runtime['elapsed']:.6f}s**, including "
        f"**{runtime['cooldown_wall']:.6f}s** recorded cooldown and excluding warmup. "
        f"Warmup wall time: **{runtime['warmup_wall']:.6f}s**; elapsed plus warmup: "
        f"**{runtime['execution_plus_warmup_wall']:.6f}s**. Search and certificate clocks report compute phases separately.\n\n"
        "## Outcomes by policy route\n\n"
        "| Route | Rows | Solved | Unsolved |\n|---|---:|---:|---:|\n"
        f"{route_rows}\n"
        "## Provenance\n\n"
        f"Input: [`data/AC19_extended_aut_min.csv`](../../../data/AC19_extended_aut_min.csv), "
        f"SHA-256 `{expected_sha}`. Runtime source hashes are recorded in the interval "
        "`manifest_*.json` files and checked against "
        "[`FINAL_PORTABILITY_CHECK.json`](../../../research/supermoves_20260908/FINAL_PORTABILITY_CHECK.json). "
        "The algorithm and reproduction commands are in "
        "[`AC19_FULL_CENSUS_ALGORITHM.md`](../../../research/supermoves_20260908/AC19_FULL_CENSUS_ALGORITHM.md).\n")
    atomic(result_dir / 'SUMMARY.json', json.dumps(summary, indent=2) + '\n')
    atomic(result_dir / 'RESULTS.md', markdown)
    atomic(result_dir / 'unsolved.csv', '\n'.join(csv_rows) + '\n')
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--result-dir', type=Path, required=True)
    parser.add_argument('--allow-incomplete', action='store_true')
    args = parser.parse_args()
    result = summarize(args.input, args.result_dir, allow_incomplete=args.allow_incomplete)
    if args.allow_incomplete:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps({k: result[k] for k in ('rows', 'solved', 'unsolved', 'nodes')}))


if __name__ == '__main__':
    main()
