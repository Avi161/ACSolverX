"""Build ``targets.csv``: the presentations nothing on record solves, plus two AC19 leftovers.

    PYTHONPATH=. python3 -m research.autchoice_20260910.applied.build_targets

Rows, in the order they are run (the form that may be dropped on a time overrun is last):

    aca_initial            the 124 unsolved Miller-Schupp classes in the form they were first
                           found (``aca_N``, ``benchmark/ladder/unsolved_all_forms.csv``; level 10 of ``ladder_all.csv`` until 2026-09-11)
    ac19_level9_leftover   the two level-9 AC19 orbits whose radius-2 ball did NOT solve at
                           20,000 pops in B1's atlas -- computed from ``atlas.jsonl`` (level-9
                           rows with no solved S20 image) and asserted against ``ATLAS.md``'s
                           ``ac19_27254`` and ``ac19_7284``
    aca_best               the same 124 classes in the mu-reduced best-known form (``acabest_N``)

Columns ``name, r1, r2, source, form, note``.  ``targets_manifest.json`` records the sha256 of
both inputs and the git head.
"""
import csv
import json
from collections import OrderedDict

from research.autchoice_20260910.applied.common import (
    ATLAS, HERE, LADDER_ALL, TARGET_COLS, TARGETS_CSV, UNSOLVED_ALL, git_head, read_jsonl, sha256,
)

EXPECTED_LEFTOVERS = {'ac19_27254', 'ac19_7284'}


def leftovers_from_atlas():
    solved = {}
    for d in read_jsonl(ATLAS):
        if d['level'] == '9' and d['s20'] is not None:
            solved.setdefault(d['row'], False)
            if d['s20']['solved'] and d['s20']['verified']:
                solved[d['row']] = True
    left = sorted(r for r, s in solved.items() if not s)
    assert len(solved) == 28, f'expected 28 level-9 rows in the atlas, found {len(solved)}'
    assert set(left) == EXPECTED_LEFTOVERS, f'atlas leftovers {left} != ATLAS.md {EXPECTED_LEFTOVERS}'
    return left


def main():
    ladder = {r['name']: r for r in csv.DictReader(open(LADDER_ALL))}
    # the unsolved classes left the ladder pool on 2026-09-11 (benchmark/ladder/LADDER.md):
    # they now live in unsolved_all_forms.csv, same columns, level 'unsolved'
    ladder.update({r['name']: r for r in csv.DictReader(open(UNSOLVED_ALL))})
    out = []
    for form in ('aca_initial', 'aca_best'):
        rows = sorted((r for r in ladder.values() if r['form'] == form),
                      key=lambda r: int(r['name'].rsplit('_', 1)[1]))
        assert len(rows) == 124, (form, len(rows))
        for r in rows:
            note = ('unsolved MS class %s, form first found (un-reduced); 0/261 greedy 1M, '
                    '0/124 S20_MK2 10M, 0/124 cascade probes 10k' % r['aut_class']
                    if form == 'aca_initial' else
                    'unsolved MS class %s, mu-reduced best-known form (the u124 probes ran on it)'
                    % r['aut_class'])
            out.append(OrderedDict(name=r['name'], r1=r['r1'], r2=r['r2'],
                                   source='benchmark/ladder/unsolved_all_forms.csv', form=form, note=note))
    left = leftovers_from_atlas()
    for name in left:
        r = ladder[name]
        assert r['level'] in ('9', '10') and r['form'] == 'autmin', r   # level 10 since the 2026-09-11 split
        out.insert(124 + left.index(name), OrderedDict(
            name=name, r1=r['r1'], r2=r['r2'],
            source='benchmark/ladder/ladder_all.csv + research/autchoice_20260910/atlas.jsonl',
            form='ac19_level9_leftover',
            note='AC19 aut-min orbit; plain greedy and S20_MK2 unsolved at 10M; no radius-2 image '
                 'solved at 20k in the atlas; ladder solved_by=%s' % r['solved_by']))
    assert len(out) == 250 and len({r['name'] for r in out}) == 250
    with open(TARGETS_CSV, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=TARGET_COLS)
        w.writeheader()
        w.writerows(out)
    manifest = OrderedDict(
        git_head=git_head(), rows=len(out),
        per_form=OrderedDict((f, sum(1 for r in out if r['form'] == f))
                             for f in ('aca_initial', 'ac19_level9_leftover', 'aca_best')),
        leftovers=left,
        inputs=OrderedDict([(str(LADDER_ALL.relative_to(HERE.parents[2])), sha256(LADDER_ALL)),
                            (str(UNSOLVED_ALL.relative_to(HERE.parents[2])), sha256(UNSOLVED_ALL)),
                            (str(ATLAS.relative_to(HERE.parents[2])), sha256(ATLAS))]),
        targets_csv_sha256=sha256(TARGETS_CSV))
    with open(HERE / 'targets_manifest.json', 'w') as f:
        json.dump(manifest, f, indent=1)
        f.write('\n')
    print(json.dumps(manifest, indent=1))


if __name__ == '__main__':
    main()
