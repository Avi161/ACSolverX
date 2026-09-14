"""How many ordinary AC substitution moves does a hybrid certificate cost?

A hybrid certificate mixes three step kinds: `substitution` (one AC product move),
`automorphism` (a Nielsen map or a signed permutation of the basis) and `dyn`
(a Lemma-11 define/eliminate composite).  Only the first is an AC move as stored,
but an automorphism-assisted path is still an AC solve: AC moves are equivariant
under Aut(F2), so pushing the accumulated basis change back through the path turns
every automorphism step into a no-op and leaves a pure AC path, and the search's
terminal is a basis, which Nielsen's theorem returns to (x, y) by tuple moves that
are themselves AC moves.  That transport is implemented and trusted in
`research/supermoves_20260908/certificate_decoder.py`; this module is the *counter*
that rides on it.

Reading its output at the multiply granularity gives the cost exactly:

    ac_moves = substitution steps + Nielsen automorphism steps

because the decoder emits one `multiply` per substitution step and one per Nielsen
image in the terminal tail, while a signed permutation emits only swaps and inverts.
`validate` checks that identity against the decoder itself, row by row.

`dyn` certificates have no rank-two move count: they prove *stable* AC-triviality
with the composites unexpanded, so this module reports them as such and counts
nothing for them.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.ac_hashfree_cascade_20260914 import hfhybrid, verify as SV  # noqa: E402

NIELSEN_IMAGES = [dict(n) for n in SV.NIELSEN]


def classify(step):
    """'substitution', 'nielsen', 'perm' or 'dyn'."""
    kind = step['kind']
    if kind != 'automorphism':
        return kind
    img = step['images']
    if any(img == n for n in NIELSEN_IMAGES):
        return 'nielsen'
    if set(img) == {'x', 'y'} and all(v in ('x', 'X', 'y', 'Y') for v in img.values()):
        return 'perm'
    raise ValueError(f'automorphism image is neither Nielsen nor a signed permutation: {img}')


def count(steps):
    """Move counts for one certificate.  `ac_moves` is None for a dyn certificate."""
    c = {'substitution': 0, 'nielsen': 0, 'perm': 0, 'dyn': 0}
    for s in steps:
        c[classify(s)] += 1
    stable = c['dyn'] > 0
    return dict(ac_moves=None if stable else c['substitution'] + c['nielsen'],
                substitution=c['substitution'], nielsen=c['nielsen'],
                perm=c['perm'], dyn=c['dyn'], steps=len(steps), stable=stable)


def states_of(pair, steps):
    """The canonical state after each step, as the decoder wants them (len(steps) + 1)."""
    cur = SV.canon_pair(*pair)
    out = [cur]
    for i, step in enumerate(steps):
        if step['kind'] == 'dyn':
            raise ValueError('dyn certificates have no rank-two state sequence')
        cur = hfhybrid._replay_one(cur, step, i)
        out.append(cur)
    return out


def decode_counts(pair, steps):
    """Run the repository's decoder and count its elementary operations.

    Returns the op histogram; `multiply` is the number of ordinary AC substitutions
    the transported, pure rank-two path actually performs.  Raises whatever the
    decoder raises -- every internal frame check of that module stays armed.
    """
    from research.supermoves_20260908 import certificate_decoder as CD
    moves = CD.decode_elementary(tuple(pair), states_of(pair, steps), steps)
    hist = dict(multiply=0, invert=0, swap=0, conjugate=0)
    for m in moves:
        hist[m['op']] = hist.get(m['op'], 0) + 1
    hist['total'] = len(moves)
    return hist


# ---------------------------------------------------------------- CLI

def _stream(path):
    import gzip, json
    op = gzip.open if str(path).endswith('.gz') else open
    with op(path, 'rt') as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def _name(rec, i, prefix):
    for k in ('name', 'pres_id'):
        if k in rec:
            return f'{prefix}{rec[k]}' if k == 'pres_id' else rec[k]
    return f'{prefix}{i}'


def cmd_count(args):
    import csv, gzip
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    opener = gzip.open if out.name.endswith('.gz') else open
    tally = dict(rows=0, stable=0, ac_moves=0, max_ac=0, no_steps=0)
    with opener(out, 'wt', newline='') as f:
        w = csv.writer(f)
        w.writerow(['name', 'r1', 'r2', 'length', 'stage', 'units', 'steps',
                    'substitution', 'nielsen', 'perm', 'dyn', 'ac_moves', 'stable'])
        for path in args.records:
            for i, r in enumerate(_stream(path)):
                if not r.get('solved'):
                    continue
                if 'steps' not in r:
                    tally['no_steps'] += 1
                    continue
                c = count(r['steps'])
                tally['rows'] += 1
                tally['stable'] += c['stable']
                if c['ac_moves'] is not None:
                    tally['ac_moves'] += c['ac_moves']
                    tally['max_ac'] = max(tally['max_ac'], c['ac_moves'])
                w.writerow([_name(r, i, args.prefix), r['r1'], r['r2'],
                            len(r['r1']) + len(r['r2']), r.get('stage'), r['units'],
                            c['steps'], c['substitution'], c['nielsen'], c['perm'],
                            c['dyn'], '' if c['ac_moves'] is None else c['ac_moves'],
                            int(c['stable'])])
    import json
    print(json.dumps(tally))


def cmd_validate(args):
    """Check `ac_moves` against the repository's decoder on a stratified sample."""
    import json, random
    rows = []
    for path in args.records:
        for i, r in enumerate(_stream(path)):
            if r.get('solved') and 'steps' in r:
                c = count(r['steps'])
                if not c['stable']:
                    rows.append((Path(path).name, _name(r, i, args.prefix), r['r1'], r['r2'], r['steps'], c))
    # stratify: the longest, the most automorphism-heavy, every row carrying a signed
    # permutation, and a random remainder -- the cases where the identity could break
    by_len = sorted(rows, key=lambda t: -t[5]['steps'])[:args.sample // 4]
    by_aut = sorted(rows, key=lambda t: -(t[5]['nielsen'] + t[5]['perm']))[:args.sample // 4]
    perms = [t for t in rows if t[5]['perm']][:args.sample // 4]
    rng = random.Random(20260914)
    rest = rng.sample(rows, min(len(rows), args.sample))
    seen, pick = set(), []
    for t in by_len + by_aut + perms + rest:
        if (t[0], t[1]) in seen:
            continue
        seen.add((t[0], t[1]))
        pick.append(t)
        if len(pick) >= args.sample:
            break
    ok = bad = 0
    failures = []
    for src, name, r1, r2, steps, c in pick:
        try:
            d = decode_counts((r1, r2), steps)
            if d.get('multiply') == c['ac_moves']:
                ok += 1
            else:
                bad += 1
                failures.append(dict(source=src, name=name, formula=c['ac_moves'],
                                     decoder=d.get('multiply')))
        except Exception as exc:                                  # noqa: BLE001
            bad += 1
            failures.append(dict(source=src, name=name, error=f'{type(exc).__name__}: {exc}'))
    res = dict(sampled=len(pick), agree=ok, disagree=bad, failures=failures[:20],
               with_perm=sum(1 for t in pick if t[5]['perm']),
               with_nielsen=sum(1 for t in pick if t[5]['nielsen']),
               max_steps=max(t[5]['steps'] for t in pick))
    print(json.dumps(res, indent=2))
    if args.out:
        Path(args.out).write_text(json.dumps(res, indent=2) + '\n')
    return 0 if bad == 0 else 1


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('count', help='write a per-presentation AC-move table')
    c.add_argument('--records', nargs='+', required=True)
    c.add_argument('--prefix', default='row_')
    c.add_argument('--out', required=True)
    c.set_defaults(fn=cmd_count)
    v = sub.add_parser('validate', help='check the count against the repository decoder')
    v.add_argument('--records', nargs='+', required=True)
    v.add_argument('--prefix', default='row_')
    v.add_argument('--sample', type=int, default=300)
    v.add_argument('--out')
    v.set_defaults(fn=cmd_validate)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == '__main__':
    raise SystemExit(main())
