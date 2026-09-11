"""The run panel of AC19 originals: every distinct presentation in data/AC19_extended.txt
that is not already an aut-min representative.

    156,762 lines  ->  156,753 distinct canonical pairs (9 duplicate lines)
                   ->  24,848 of them ARE their aut-min representative (already graded)
                   ->  131,905 new rows, named ac19x_<first line index>

Words are canonicalised with ``words.canon_pair`` (the form every search starts from);
``orbit`` is the aut-min orbit the line belongs to (``members`` of AC19_extended_aut_min.csv).

    PYTHONPATH=. python3 -m benchmark.ac19_ladder.originals_panel
"""
import ast
import csv
import hashlib
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from experiments.equivalence_classes.lib.words import canon_pair  # noqa: E402

HERE = Path(__file__).resolve().parent
SYMBOL = {1: 'x', -1: 'X', 2: 'y', -2: 'Y'}
FIELDS = ['name', 'r1', 'r2', 'orbit', 'line', 'n_lines']


def decode_padded(line):
    ints = ast.literal_eval(line.strip())
    assert len(ints) == 48, len(ints)
    return (''.join(SYMBOL[v] for v in ints[:24] if v), ''.join(SYMBOL[v] for v in ints[24:] if v))


def build():
    lines = [l for l in (ROOT / 'data' / 'AC19_extended.txt').read_text().splitlines() if l.strip()]
    assert len(lines) == 156_762, len(lines)
    reps, orbit_of_line = {}, {}
    with open(ROOT / 'data' / 'AC19_extended_aut_min.csv', newline='') as fh:
        for row in csv.DictReader(fh):
            reps[(row['r1'], row['r2'])] = row['name']
            for m in row['members'].split():
                orbit_of_line[int(m)] = row['name']
    assert len(reps) == 72_779 and len(orbit_of_line) == len(lines)
    seen = OrderedDict()
    same_as_rep = 0
    for i, line in enumerate(lines):
        pair = canon_pair(*decode_padded(line))
        if pair in reps:
            same_as_rep += 1
            continue
        if pair in seen:
            seen[pair]['n_lines'] += 1
            assert seen[pair]['orbit'] == orbit_of_line[i]
            continue
        seen[pair] = dict(name=f'ac19x_{i}', r1=pair[0], r2=pair[1], orbit=orbit_of_line[i], line=i, n_lines=1)
    rows = list(seen.values())
    return rows, same_as_rep


def main():
    rows, same_as_rep = build()
    out = HERE / 'sources' / 'originals_panel.csv'
    with open(out, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    sha = hashlib.sha256(out.read_bytes()).hexdigest()
    print(f'{len(rows):,} rows -> {out.relative_to(ROOT)}  (sha256 {sha[:12]}...)')
    print(f'  {same_as_rep:,} lines are their aut-min representative; '
          f'{sum(r["n_lines"] - 1 for r in rows)} duplicate lines folded')


if __name__ == '__main__':
    main()
