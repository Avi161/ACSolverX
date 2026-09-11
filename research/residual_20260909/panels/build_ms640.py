"""Rebuild ``panels/ms640.csv`` from ``data/ms640_solved.txt``.

The 640 Miller-Schupp presentations that the greedy baseline solved (at a
1,000,000-node budget, ``mrl=24``) are stored as 48 padded integers per row:
two 24-slot relators over ``{1: x, -1: X, 2: y, -2: Y}`` with 0 as padding.
This writes them as the ``name,r1,r2`` CSV the census runner reads, keeping
the source file's row order (``ms_000`` .. ``ms_639``).

Usage: PYTHONPATH=. python3 -m research.residual_20260909.panels.build_ms640
"""
import ast
import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'data/ms640_solved.txt'
OUT = Path(__file__).resolve().parent / 'ms640.csv'
SOURCE_SHA256 = 'fbf976f78ce2ebba33e5a66940987047dff585a537a72725977b5dfcb0132a43'
SYMBOL = {1: 'x', -1: 'X', 2: 'y', -2: 'Y'}


def main():
    raw = SOURCE.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != SOURCE_SHA256:
        raise SystemExit(f'{SOURCE}: sha256 {digest}, expected {SOURCE_SHA256}')
    rows = [ast.literal_eval(line) for line in raw.decode().splitlines() if line.strip()]
    if len(rows) != 640 or any(len(row) != 48 for row in rows):
        raise SystemExit('expected 640 rows of 48 integers')
    with OUT.open('w', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['name', 'r1', 'r2'])
        for index, row in enumerate(rows):
            words = [''.join(SYMBOL[n] for n in half if n) for half in (row[:24], row[24:])]
            writer.writerow([f'ms_{index:03d}', *words])
    print(OUT.relative_to(ROOT), 'sha256', hashlib.sha256(OUT.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
