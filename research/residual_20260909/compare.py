"""Compare two or more harness.py <tag>.jsonl runs made on the same panel.

Reports, per run: rows/solved/verified/errors, total nodes explored, and
summed wall/CPU clocks. For every pair of runs: which panel rows each
solved that the other did not (gained/lost), a McNemar-style discordant
count (with the continuity-corrected chi-square statistic and its
asymptotic p-value, computed without a scipy dependency), and the mean
elementary-move count on rows both runs solved and verified.

Prints a markdown report to stdout and writes the same data as JSON.

Example:
    PYTHONPATH=. python3 -m research.residual_20260909.compare \\
        --runs research/residual_20260909/screens/smoke_frozen.jsonl \\
               research/residual_20260909/screens/smoke_plain_s20.jsonl \\
        --out research/residual_20260909/screens/compare_frozen_vs_plain.json
"""
import argparse
import itertools
import json
import math
from pathlib import Path


def _label_for(spec):
    """A run may be given as ``path`` or ``label=path``; default label is
    the file stem (the harness's --tag)."""
    if '=' in spec and not Path(spec).exists():
        label, path = spec.split('=', 1)
        return label, Path(path)
    path = Path(spec)
    return path.stem, path


def load_run(path):
    """Read one <tag>.jsonl into {name: record}, in file order."""
    records = {}
    with open(path) as stream:
        for line in stream:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            name = record['name']
            if name in records:
                raise ValueError(f'{path}: duplicate row name {name!r}')
            records[name] = record
    return records


def run_summary(records):
    values = list(records.values())
    solved = [r for r in values if r.get('solved')]
    verified = [r for r in values if r.get('verified')]
    errors = [r for r in values if 'error' in r]
    return dict(
        rows=len(values), solved=len(solved), verified=len(verified), errors=len(errors),
        nodes_explored_sum=sum(r.get('nodes_explored') or 0 for r in values),
        search_wall_sum=sum(r.get('search_wall') or 0. for r in values),
        search_cpu_sum=sum(r.get('search_cpu') or 0. for r in values),
        certificate_wall_sum=sum(r.get('certificate_wall') or 0. for r in values),
        certificate_cpu_sum=sum(r.get('certificate_cpu') or 0. for r in values),
    )


def _mcnemar(b, c):
    """Continuity-corrected McNemar chi-square (df=1) for discordant counts
    b (solved by A only) and c (solved by B only), and its asymptotic
    p-value via the normal tail (chi2_1 = Z^2), with no scipy dependency."""
    if b + c == 0:
        return dict(b=b, c=c, statistic=0., p_value=1.)
    statistic = (abs(b - c) - 1) ** 2 / (b + c)
    p_value = math.erfc(math.sqrt(statistic / 2))
    return dict(b=b, c=c, statistic=statistic, p_value=p_value)


def compare_pair(label_a, records_a, label_b, records_b):
    names_a, names_b = set(records_a), set(records_b)
    common_names = names_a & names_b
    if names_a != names_b:
        only_a, only_b = sorted(names_a - names_b), sorted(names_b - names_a)
    else:
        only_a = only_b = []

    solved_a = {n for n in common_names if records_a[n].get('solved')}
    solved_b = {n for n in common_names if records_b[n].get('solved')}
    gained = sorted(solved_b - solved_a)   # B solved, A did not
    lost = sorted(solved_a - solved_b)     # A solved, B did not
    mcnemar = _mcnemar(len(lost), len(gained))

    both_solved_verified = sorted(
        n for n in solved_a & solved_b
        if records_a[n].get('verified') and records_b[n].get('verified'))
    elem_a = [records_a[n]['elementary_count'] for n in both_solved_verified]
    elem_b = [records_b[n]['elementary_count'] for n in both_solved_verified]
    node_deltas = {n: records_b[n].get('nodes_explored') - records_a[n].get('nodes_explored')
                  for n in both_solved_verified
                  if records_a[n].get('nodes_explored') is not None
                  and records_b[n].get('nodes_explored') is not None}

    return dict(
        a=label_a, b=label_b,
        panel_names_only_in_a=only_a, panel_names_only_in_b=only_b,
        common_rows=len(common_names),
        gained_by_b=gained, lost_by_b=lost,
        mcnemar=mcnemar,
        both_solved_verified=len(both_solved_verified),
        mean_elementary_count_a=(sum(elem_a) / len(elem_a)) if elem_a else None,
        mean_elementary_count_b=(sum(elem_b) / len(elem_b)) if elem_b else None,
        mean_nodes_delta_b_minus_a=(sum(node_deltas.values()) / len(node_deltas)) if node_deltas else None,
        max_abs_nodes_delta=max((abs(v) for v in node_deltas.values()), default=None),
    )


def _fmt(x, digits=4):
    if x is None:
        return 'n/a'
    if isinstance(x, float):
        return f'{x:.{digits}g}'
    return str(x)


def to_markdown(summaries, pairwise, name_cap=15):
    lines = ['# Policy comparison', '', '## Run summary', '',
             '| run | rows | solved | verified | errors | nodes | search wall (s) | search cpu (s) |',
             '|---|---:|---:|---:|---:|---:|---:|---:|']
    for label, summary in summaries.items():
        lines.append('| {} | {} | {} | {} | {} | {} | {} | {} |'.format(
            label, summary['rows'], summary['solved'], summary['verified'], summary['errors'],
            summary['nodes_explored_sum'], _fmt(summary['search_wall_sum']), _fmt(summary['search_cpu_sum'])))
    lines.append('')
    for pair in pairwise:
        lines.append(f"## {pair['a']} vs {pair['b']}")
        lines.append('')
        if pair['panel_names_only_in_a'] or pair['panel_names_only_in_b']:
            lines.append(f"- panel mismatch: {len(pair['panel_names_only_in_a'])} rows only in "
                         f"{pair['a']}, {len(pair['panel_names_only_in_b'])} only in {pair['b']} "
                         f"(comparison restricted to the {pair['common_rows']} common rows)")
        lines.append(f"- gained by {pair['b']} (solved by {pair['b']}, not {pair['a']}): "
                     f"{len(pair['gained_by_b'])}")
        if pair['gained_by_b']:
            shown = pair['gained_by_b'][:name_cap]
            more = f", ... (+{len(pair['gained_by_b']) - name_cap} more)" if len(pair['gained_by_b']) > name_cap else ''
            lines.append(f"  {', '.join(shown)}{more}")
        lines.append(f"- lost by {pair['b']} (solved by {pair['a']}, not {pair['b']}): "
                     f"{len(pair['lost_by_b'])}")
        if pair['lost_by_b']:
            shown = pair['lost_by_b'][:name_cap]
            more = f", ... (+{len(pair['lost_by_b']) - name_cap} more)" if len(pair['lost_by_b']) > name_cap else ''
            lines.append(f"  {', '.join(shown)}{more}")
        m = pair['mcnemar']
        lines.append(f"- McNemar: b(lost)={m['b']}, c(gained)={m['c']}, "
                     f"chi2(continuity-corrected, df=1)={_fmt(m['statistic'])}, p={_fmt(m['p_value'])}")
        lines.append(f"- common solved+verified rows: {pair['both_solved_verified']}; "
                     f"mean elementary count {pair['a']}={_fmt(pair['mean_elementary_count_a'])}, "
                     f"{pair['b']}={_fmt(pair['mean_elementary_count_b'])}; "
                     f"mean nodes delta ({pair['b']}-{pair['a']})={_fmt(pair['mean_nodes_delta_b_minus_a'])}")
        lines.append('')
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--runs', nargs='+', required=True,
                        help='two or more run files, as PATH or LABEL=PATH (default label: file stem)')
    parser.add_argument('--out', type=Path, required=True, help='JSON report path')
    parser.add_argument('--name-cap', type=int, default=15, help='max gained/lost names shown per pair in markdown')
    args = parser.parse_args(argv)

    if len(args.runs) < 2:
        raise ValueError('--runs needs at least two run files to compare')

    labeled = [_label_for(spec) for spec in args.runs]
    labels = [label for label, _ in labeled]
    if len(set(labels)) != len(labels):
        raise ValueError(f'duplicate run labels: {labels}')
    loaded = {label: load_run(path) for label, path in labeled}

    summaries = {label: run_summary(records) for label, records in loaded.items()}
    pairwise = [compare_pair(a, loaded[a], b, loaded[b]) for a, b in itertools.combinations(labels, 2)]

    report = dict(runs={label: str(path) for label, path in labeled}, summaries=summaries, pairwise=pairwise)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + '\n')

    markdown = to_markdown(summaries, pairwise, name_cap=args.name_cap)
    print(markdown)
    print(f'\nJSON report: {args.out}')
    return report


if __name__ == '__main__':
    main()
