"""Summarise the applied campaign: did any Aut(F2)-image solve a presentation nothing solves?

    PYTHONPATH=. python3 -m research.autchoice_20260910.applied.analyze_applied

Reads ``targets.csv``, ``phase1.jsonl``, ``phase2.jsonl`` (if present), ``verify_applied.json``
and the run/selection/ranking JSONs, and writes ``APPLIED.md`` + ``applied_summary.json``.
Every number in the markdown is computed here from the JSONL.

A record counts as a solve only if ``s20.solved`` and ``s20.verified`` are both true **and**
``verify_applied.py``'s fresh-process re-check did not list it as a failure; a claim that
fails either check is reported as a failure, never as a solve.

Per target: the images searched (radius 2 in phase 1, depth-3 images and 200k escalations in
phase 2), the identity's ``min_total_length_seen`` and the ball's minimum with the image that
reached it, the number of images whose minimum went below the target's start length, the
best solve.  Per form and per class (``aca_N`` and ``acabest_N`` are one class): targets with
at least one solving image, targets with any image below the start, the distribution of
``ball_min - start_len``.  The two AC19 level-9 leftovers get their own section.
"""
import csv
import json
import statistics
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.autcanon import AUTOS  # noqa: E402

HERE = Path(__file__).resolve().parent
FORMS = ('aca_initial', 'aca_best', 'ac19_level9_leftover')


def read_jsonl(path):
    if not path.exists():
        return []
    return [json.loads(l) for l in open(path) if l.strip()]


def load_json(name, default=None):
    p = HERE / name
    return json.load(open(p)) if p.exists() else default


def fmt_int(v):
    return '-' if v is None else f'{v:,}'


def seq_str(seq):
    return 'id' if not seq else ' '.join(str(i) for i in seq)


def phi_str(phi):
    return f"x->{phi['x']}, y->{phi['y']}"


def main():
    targets = list(csv.DictReader(open(HERE / 'targets.csv')))
    tmap = {t['name']: t for t in targets}
    p1 = read_jsonl(HERE / 'phase1.jsonl')
    p2 = read_jsonl(HERE / 'phase2.jsonl')
    ver = load_json('verify_applied.json', {'checked': 0, 'ok': 0, 'failed': 0, 'failures': [], 'records': 0})
    failed_keys = {(f['file'], f['row'], f['image_index'], f['budget']) for f in ver.get('failures', [])}
    run1 = load_json('phase1_run.json', {})
    run2 = load_json('phase2_run.json', {})
    sel2 = load_json('phase2_selection.json', {})
    rank2 = load_json('phase2_ranking.json', {})

    def is_solve(file, d):
        return bool(d['s20']['solved'] and d['s20']['verified']) and \
            (file, d['row'], d['image_index'], d['budget']) not in failed_keys

    claimed_not_verified = [(f, d['row'], d['image_index'], d['budget']) for f, recs in (('phase1.jsonl', p1), ('phase2.jsonl', p2))
                            for d in recs if d['s20']['solved'] and not is_solve(f, d)]
    rejected = [(f, d['row'], d['image_index']) for f, recs in (('phase1.jsonl', p1), ('phase2.jsonl', p2))
                for d in recs if d['s20'].get('rejected')]

    # ---------------------------------------------------------------- per target
    per = OrderedDict()
    for t in targets:
        per[t['name']] = OrderedDict(
            name=t['name'], form=t['form'], r1=t['r1'], r2=t['r2'], start_len=len(t['r1']) + len(t['r2']),
            images_r2=0, identity_min=None, identity_max_expanded=None, ball_min=None, ball_min_image=None,
            n_below_start=0, n_at_or_below_start=0, n_images_longer=0, n_images_shorter=0,
            images_r3=0, ball_min_r3=None, ball_min_r3_image=None, n_below_start_r3=0,
            runs_200k=0, min_200k=None, min_200k_image=None,
            solves=[], best_solve=None)
    for file, recs in (('phase1.jsonl', p1), ('phase2.jsonl', p2)):
        for d in recs:
            s = per.get(d['row'])
            if s is None:
                continue
            m = d['s20']['min_total_length_seen']
            img = OrderedDict(image_index=d['image_index'], depth=d['depth'], seq=d['seq'], phi=d['phi'],
                              r1=d['r1'], r2=d['r2'], image_len=len(d['r1']) + len(d['r2']), min_len=m,
                              nodes=d['s20']['nodes'], budget=d['budget'], phase=d['phase'])
            if d['phase'] == '1':
                s['images_r2'] += 1
                if d['image_index'] == 0:
                    s['identity_min'] = m
                    s['identity_max_expanded'] = d['s20']['max_expanded']
                if s['ball_min'] is None or (m, d['image_index']) < (s['ball_min'], s['ball_min_image']['image_index']):
                    s['ball_min'], s['ball_min_image'] = m, img
                s['n_below_start'] += int(m < s['start_len'])
                s['n_at_or_below_start'] += int(m <= s['start_len'])
                s['n_images_longer'] += int(img['image_len'] > s['start_len'])
                s['n_images_shorter'] += int(img['image_len'] < s['start_len'])
            elif d['phase'] == '2a':
                s['images_r3'] += 1
                if s['ball_min_r3'] is None or (m, d['image_index']) < (s['ball_min_r3'], s['ball_min_r3_image']['image_index']):
                    s['ball_min_r3'], s['ball_min_r3_image'] = m, img
                s['n_below_start_r3'] += int(m < s['start_len'])
            elif d['phase'] == '2b':
                s['runs_200k'] += 1
                img['ranker'] = d.get('ranker')
                img['rank'] = d.get('rank')
                if s['min_200k'] is None or (m, d['image_index']) < (s['min_200k'], s['min_200k_image']['image_index']):
                    s['min_200k'], s['min_200k_image'] = m, img
            if is_solve(file, d):
                sv = OrderedDict(file=file, **img)
                sv['path_len'] = d['s20']['path_len']
                sv['max_expanded'] = d['s20']['max_expanded']
                sv['path_moves'] = d['s20']['path_moves']
                s['solves'].append(sv)
    for s in per.values():
        if s['solves']:
            s['best_solve'] = min(s['solves'], key=lambda v: (v['nodes'], v['image_index']))

    # ---------------------------------------------------------------- aggregates
    def agg(rows):
        rows = list(rows)
        run = [r for r in rows if r['images_r2'] > 0]
        drops = [r['ball_min'] - r['start_len'] for r in run]
        return OrderedDict(
            targets=len(rows), run=len(run),
            solved=sum(1 for r in run if r['best_solve']),
            any_image_below_start=sum(1 for r in run if r['n_below_start'] > 0),
            ball_min_below_identity_min=sum(1 for r in run if r['identity_min'] is not None and r['ball_min'] < r['identity_min']),
            identity_below_start=sum(1 for r in run if r['identity_min'] is not None and r['identity_min'] < r['start_len']),
            drop_min=min(drops) if drops else None, drop_median=statistics.median(drops) if drops else None,
            drop_max=max(drops) if drops else None,
            images_total=sum(r['images_r2'] for r in run),
            images_below_start=sum(r['n_below_start'] for r in run),
            images_at_or_below_start=sum(r['n_at_or_below_start'] for r in run),
            targets_all_images_back_to_start=sum(1 for r in run if r['n_at_or_below_start'] == r['images_r2']),
            ball_min_hist=OrderedDict(sorted(((str(d), drops.count(d)) for d in set(drops)), key=lambda kv: int(kv[0])))
        )
    per_form = OrderedDict((f, agg(r for r in per.values() if r['form'] == f)) for f in FORMS)
    classes = defaultdict(list)
    for r in per.values():
        if r['form'].startswith('aca'):
            classes[r['name'].rsplit('_', 1)[1]].append(r)
    class_solved = sorted(k for k, rs in classes.items() if any(r['best_solve'] for r in rs))
    class_any_below = sum(1 for rs in classes.values() if any(r['n_below_start'] > 0 for r in rs))
    # the best-known length of a class is the aca_best start length; did any image beat it?
    best_len = {k: next(r['start_len'] for r in rs if r['form'] == 'aca_best') for k, rs in classes.items()
                if any(r['form'] == 'aca_best' for r in rs)}
    for r in per.values():
        k = r['name'].rsplit('_', 1)[1] if r['form'].startswith('aca') else None
        r['best_known_len'] = best_len.get(k)
        r['ball_min_vs_best_known'] = None if (r['best_known_len'] is None or r['ball_min'] is None) else r['ball_min'] - r['best_known_len']
    class_min = {k: min(r['ball_min'] for r in rs if r['ball_min'] is not None) for k, rs in classes.items()
                 if any(r['ball_min'] is not None for r in rs)}
    class_below_best = sorted(k for k, m in class_min.items() if k in best_len and m < best_len[k])
    class_at_best = sum(1 for k, m in class_min.items() if k in best_len and m == best_len[k])
    initial_reached_best = sum(1 for r in per.values() if r['form'] == 'aca_initial' and r['ball_min'] is not None
                               and r['best_known_len'] is not None and r['ball_min'] <= r['best_known_len'])
    initial_identity_reached_best = sum(1 for r in per.values() if r['form'] == 'aca_initial' and r['identity_min'] is not None
                                        and r['best_known_len'] is not None and r['identity_min'] <= r['best_known_len'])
    solves = [r for r in per.values() if r['best_solve']]

    summary = OrderedDict(
        git_head=load_json('targets_manifest.json', {}).get('git_head'),
        phase1=run1, phase2=run2, verification=OrderedDict(records=ver.get('records'), checked=ver.get('checked'),
                                                            ok=ver.get('ok'), failed=ver.get('failed'),
                                                            failures=ver.get('failures', [])),
        claimed_but_unverified=claimed_not_verified, rejected_by_image_replay=rejected,
        new_solves_per_form=OrderedDict((f, [r['name'] for r in solves if r['form'] == f]) for f in FORMS),
        classes=OrderedDict(total=len(classes), solved=len(class_solved), solved_names=class_solved,
                            any_image_below_start=class_any_below, below_best_known=class_below_best,
                            at_best_known=class_at_best, initial_ball_reached_best_known=initial_reached_best,
                            initial_identity_reached_best_known=initial_identity_reached_best),
        per_form=per_form,
        leftovers=OrderedDict((r['name'], r) for r in per.values() if r['form'] == 'ac19_level9_leftover'),
        phase2_selection=sel2, phase2_ranking=rank2,
        per_target=per)
    with open(HERE / 'applied_summary.json', 'w') as f:
        json.dump(summary, f, indent=1)
        f.write('\n')

    # ---------------------------------------------------------------- markdown
    L = []
    w = L.append
    n_targets_run = sum(1 for r in per.values() if r['images_r2'] > 0)
    w('# The applied campaign: B1\'s radius-2 trick on the presentations nothing solves\n')
    w(f"Targets: the 124 unsolved Miller-Schupp classes in both forms (`aca_N` as first found, "
      f"`acabest_N` mu-reduced) and the two AC19 level-9 orbits whose radius-2 ball did not solve at "
      f"20,000 pops in the atlas (`ac19_27254`, `ac19_7284`); {len(targets)} rows, {n_targets_run} run.  "
      f"Phase 1: every radius-2 image (cap 48, relabel-deduped) searched with `S20_MK2` at "
      f"{run1.get('budget', 20000):,} pops; {len(p1):,} records, "
      f"{sum(1 for d in p1 if not d['s20'].get('shared'))} distinct searches (identical pairs searched once).  "
      f"Phase 2: {len(p2):,} records (below).  Built by `analyze_applied.py` from `phase1.jsonl` / `phase2.jsonl`.\n")

    w('## The answer\n')
    if not solves:
        w(f"**Zero new solves.**  No image of any of the {n_targets_run} targets solved at any budget run "
          f"({run1.get('budget', 20000):,} pops on {sum(1 for d in p1)} radius-2 records"
          + (f", {sum(1 for d in p2 if d['phase'] == '2a')} depth-3 records at {run2.get('budget', 20000):,} and "
             f"{sum(1 for d in p2 if d['phase'] == '2b')} escalations at {run2.get('big_budget', 200000):,}" if p2 else '')
          + ").  The trick that turns 26/28 unsolvable-at-10M AC19 representatives into sub-20k solves does not "
          "touch the unsolved Miller-Schupp classes at these budgets, nor the two AC19 leftovers.\n")
    else:
        ms_solved = per_form['aca_initial']['solved'] + per_form['aca_best']['solved']
        n2a = sum(1 for d in p2 if d['phase'] == '2a' and d['form'].startswith('aca'))
        n2b = sum(1 for d in p2 if d['phase'] == '2b' and d['form'].startswith('aca'))
        w(f"**{len(solves)} target(s) with at least one verified solving image** "
          + ', '.join(f"{per_form[f]['solved']} {f}" for f in FORMS) + '.\n')
        if ms_solved == 0:
            w(f"**On the 124 unsolved Miller-Schupp classes: zero new solves.**  Neither form solved from any of its "
              f"{per_form['aca_initial']['images_total'] + per_form['aca_best']['images_total']:,} radius-2 images at "
              f"{run1.get('budget', 20000):,} pops"
              + (f", nor from the {n2a} depth-3 images at {run2.get('budget', 20000):,} or the {n2b} ranked images at "
                 f"{run2.get('big_budget', 200000):,} pops on the 10 closest classes" if p2 else '')
              + ".  The trick that turns 26/28 unsolvable-at-10M AC19 representatives into sub-20k solves does not touch "
              "the MS residue at these budgets; what it did reach is below.\n")
        w('| target | form | image | depth | seq (AUTOS) | phi | image r1, r2 | pops | AC moves | budget |')
        w('|---|---|---:|---:|---|---|---|---:|---:|---:|')
        for r in solves:
            b = r['best_solve']
            w(f"| {r['name']} | {r['form']} | {b['image_index']} | {b['depth']} | {seq_str(b['seq'])} | {phi_str(b['phi'])} | "
              f"`{b['r1']}`, `{b['r2']}` | {b['nodes']:,} | {b['path_len']} | {b['budget']:,} |")
        w('')
    w('| form | targets | run | with a solving image | any image below start length | ball min < identity min | identity below start | images | images below start | images back to start length | targets where every image got back |')
    w('|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|')
    for f in FORMS:
        a = per_form[f]
        w(f"| {f} | {a['targets']} | {a['run']} | {a['solved']} | {a['any_image_below_start']} | {a['ball_min_below_identity_min']} | "
          f"{a['identity_below_start']} | {a['images_total']} | {a['images_below_start']} | {a['images_at_or_below_start']} | {a['targets_all_images_back_to_start']} |")
    w(f"\nPer class (`aca_N` and `acabest_N` together): {summary['classes']['solved']}/{summary['classes']['total']} classes "
      f"solved, {class_any_below}/{summary['classes']['total']} with any image below the start length in either form.  "
      f"Against the class's **best-known length** (the `acabest_N` start length): {len(class_below_best)} classes where any "
      f"image's search found a state shorter than the best-known form"
      + (f" ({', '.join(class_below_best)})" if class_below_best else '')
      + f"; {class_at_best} where the ball's minimum equals it.  On the un-reduced `aca_initial` rows the ball reaches the "
      f"best-known length on {initial_reached_best}/124 (the identity alone on {initial_identity_reached_best}/124), i.e. "
      f"a drop below the `aca_initial` start is the known mu-reduction rediscovered, not new ground.\n")
    if claimed_not_verified or rejected:
        w(f"**Claims that failed verification (reported as failures, not solves):** {len(claimed_not_verified)} "
          f"claimed solves not verified: {claimed_not_verified}; {len(rejected)} rejected by the image replay: {rejected}.\n")
    else:
        w('No engine claim failed either replay (0 rejected, 0 unverified).\n')

    w('## What the ball reached (non-solves)\n')
    w('`ball_min` is the smallest total relator length the search discovered from any radius-2 image (the '
      'engine\'s `min_relator_length`); `identity min` the same from the row as given; `drop` = `ball_min - start_len`.  '
      'A negative drop means some image\'s search found a state shorter than the target; zero means nothing below '
      'the start was ever seen.  `images back to start` counts images (usually longer than the row) whose search '
      'rediscovered a state no longer than the row.  Images longer than the row are the norm (B1: the cheapest image '
      'is longer than the row on 99/114), so `images longer` says how the ball sits.\n')
    w('| form | run | drop min / median / max | histogram of drop (drop: targets) |')
    w('|---|---:|---|---|')
    for f in FORMS:
        a = per_form[f]
        hist = ', '.join(f"{k}: {v}" for k, v in a['ball_min_hist'].items())
        w(f"| {f} | {a['run']} | {a['drop_min']} / {a['drop_median']} / {a['drop_max']} | {hist} |")
    w('')
    w('### Per target (sorted by ball_min, then drop)\n')
    w('| target | form | start len | best-known len | identity min | identity max exp | ball min | drop | vs best-known | at image (idx, depth, seq, len) | images below start | images back to start | images longer / shorter than row | r3 min | 200k min |')
    w('|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---|---:|---:|')
    for r in sorted((r for r in per.values() if r['images_r2'] > 0),
                    key=lambda r: (r['ball_min'], r['ball_min'] - r['start_len'], r['name'])):
        bi = r['ball_min_image']
        at = f"{bi['image_index']}, d{bi['depth']}, {seq_str(bi['seq'])}, {bi['image_len']}" if bi else '-'
        w(f"| {r['name']} | {r['form']} | {r['start_len']} | {'-' if r['best_known_len'] is None else r['best_known_len']} | "
          f"{r['identity_min']} | {r['identity_max_expanded']} | {r['ball_min']} | "
          f"{r['ball_min'] - r['start_len']} | {'-' if r['ball_min_vs_best_known'] is None else r['ball_min_vs_best_known']} | {at} | {r['n_below_start']}/{r['images_r2']} | {r['n_at_or_below_start']}/{r['images_r2']} | {r['n_images_longer']} / {r['n_images_shorter']} | "
          f"{'-' if r['ball_min_r3'] is None else r['ball_min_r3']} | {'-' if r['min_200k'] is None else r['min_200k']} |")
    w('')

    ss = load_json('short_states.json', {'certified': [], 'failed': []})
    w('## States shorter than a class\'s best-known form\n')
    if not ss['certified'] and not ss['failed']:
        w('None found: no image\'s search discovered a state shorter than the `acabest_N` form of its class '
          '(`certify_short_states.py` had nothing to certify).\n')
    else:
        w(f"`certify_short_states.py` re-ran every search whose `min_total_length_seen` is below the class's best-known "
          f"length, walked the solver's parent chain to the minimum, and replayed the AC moves with `words.replay_move` "
          f"from the image (and the automorphism sequence from the row): {len(ss['certified'])} certified, "
          f"{len(ss['failed'])} failed (`short_states.json` has the moves).\n")
        w('| class | best-known len | new state | len | from row / image (seq) | image len | AC moves | peak len on the path |')
        w('|---|---:|---|---:|---|---:|---:|---:|')
        for e in ss['certified']:
            for r in e['carried_by']:
                w(f"| {e['cls']} | {e['best_known_len']} | `{e['state'][0]}`, `{e['state'][1]}` | {e['state_len']} | "
                  f"{r['row']} / {r['image_index']} ({seq_str(r['seq'])}) | {e['image_len']} | {e['n_moves']} | {e['peak_len']} |")
        w('')
        cls_new = sorted({e['cls'] for e in ss['certified']})
        w(f"So {len(cls_new)} of the 124 classes ({', '.join(cls_new)}) now has a representative strictly shorter than "
          f"`data/ms_unsolved_reps/aca_124_best.csv`'s -- found from the **un-reduced** form (the mu-reduced one, a "
          f"local minimum, never discovers it), over a hump the strict descent cannot cross.  It is a shorter start, not a solve.\n")
    summary['short_states'] = ss
    w('## The two AC19 level-9 leftovers\n')
    for name, r in summary['leftovers'].items():
        out = 'SOLVED' if r['best_solve'] else 'not solved'
        w(f"- **{name}** (`{r['r1']}`, `{r['r2']}`, length {r['start_len']}): {out}.  Radius 2 at 20k: identity min "
          f"{r['identity_min']}, ball min {r['ball_min']} over {r['images_r2']} images ({r['n_below_start']} below the start)"
          + (f"; radius-3 images at 20k: {r['images_r3']} more, min {r['ball_min_r3']} ({r['n_below_start_r3']} below)" if r['images_r3'] else '')
          + (f"; {r['runs_200k']} images at 200k: min {r['min_200k']}" if r['runs_200k'] else '') + '.'
          + (f"  Best solve: image {r['best_solve']['image_index']} seq {seq_str(r['best_solve']['seq'])} at {r['best_solve']['nodes']:,} pops, "
             f"{r['best_solve']['path_len']} AC moves." if r['best_solve'] else ''))
    w('')

    w('## Phase 2\n')
    if not p2:
        w('Not run (no `phase2.jsonl`).\n')
    else:
        w(f"Selection ({sel2.get('rule', '')}): " + ', '.join(s['name'] for s in sel2.get('selected', [])) + '.\n')
        w('| target | form | start len | r2 ball min | r3 images | r3 min | below start (r3) | 200k runs | ranker | 200k images (idx, depth, seq): min len, pops |')
        w('|---|---|---:|---:|---:|---:|---:|---:|---|---|')
        for s in sel2.get('selected', []):
            r = per[s['name']]
            runs = [d for d in p2 if d['row'] == s['name'] and d['phase'] == '2b']
            runs.sort(key=lambda d: d.get('rank') or 0)
            rk = runs[0].get('ranker') if runs else '-'
            desc = '; '.join(f"({d['image_index']}, d{d['depth']}, {seq_str(d['seq'])}): {d['s20']['min_total_length_seen']}, "
                             f"{d['s20']['nodes']:,}{' SOLVED' if is_solve('phase2.jsonl', d) else ''}" for d in runs)
            w(f"| {s['name']} | {r['form']} | {r['start_len']} | {r['ball_min']} | {r['images_r3']} | {r['ball_min_r3']} | "
              f"{r['n_below_start_r3']} | {r['runs_200k']} | {rk} | {desc} |")
        w('')

    w('## Compute\n')
    w('| phase | budget (pops) | cap | workers | records | searches | wall |')
    w('|---|---:|---:|---:|---:|---:|---:|')
    if run1:
        w(f"| 1 (radius 2) | {run1['budget']:,} | {run1['cap']} | {run1['workers']} | {len(p1):,} | "
          f"{sum(1 for d in p1 if not d['s20'].get('shared')):,} | {run1['wall_seconds'] / 60:.1f} min ({run1.get('started_utc')} - {run1.get('finished_utc')}) |")
    if run2:
        st = run2.get('stages', {})
        sw = run2.get('stage_wall_seconds', {})
        for k, label, b in (('A', '2a (depth 3)', run2['budget']), ('B', '2b (top images)', run2['big_budget'])):
            if k in st:
                w(f"| {label} | {b:,} | {run2['cap']} | {st[k]['workers']} | {st[k]['records']} | {st[k]['searches']} | {sw.get(k, 0) / 60:.1f} min |")
        w(f"| 2 total | | | | {len(p2)} | | {run2['wall_seconds'] / 60:.1f} min ({run2.get('started_utc')} - {run2.get('finished_utc')}) |")
    total_wall = (run1.get('wall_seconds', 0) + run2.get('wall_seconds', 0)) / 3600
    w(f"\nTotal search wall {total_wall:.2f} h (phase-1 budget 2.5 h, phase-2 cap 1 h).  Identical pairs are searched once "
      f"(the engine is deterministic) and the result re-recorded under every (row, image) carrying them with `s20.shared`; "
      f"the per-row `verify_from_original` is never shared.\n")

    w('## Verification\n')
    w(f"In-run: every claimed solve replayed from the image with `words.replay_move` (`common.search`) and from the target's own "
      f"pair through the elementary automorphism sequence (`engine.verify_from_original`).  Fresh process "
      f"(`verify_applied.py`, reads only `applied/*.jsonl` + `targets.csv`, imports nothing from the engine): "
      f"{ver.get('records', 0):,} records, {ver.get('checked', 0)} claimed solves checked, {ver.get('ok', 0)} ok, "
      f"{ver.get('failed', 0)} failed.\n")

    w('## Caveats\n')
    w('- Costs are censored at the budget; "not solved at 20k" is not "unsolvable" -- the same images at 200k (phase 2) '
      'are the escalation, and the atlas showed the trick\'s wins at <= 14,071 pops on AC19.')
    w('- `min_total_length_seen` is the length of the shortest *discovered* state, which need not lie on any path '
      'the search will ever complete; it is a proxy for "how close", not a distance.')
    w('- The ball is relabel-deduplicated and the run image is the first discovered in BFS order (B1\'s convention), '
      'so an image\'s cost is that of one representative of its relabel class.')
    with open(HERE / 'APPLIED.md', 'w') as f:
        f.write('\n'.join(L) + '\n')
    with open(HERE / 'applied_summary.json', 'w') as f:
        json.dump(summary, f, indent=1)
        f.write('\n')
    print(f"APPLIED.md: {n_targets_run} targets run, {len(solves)} with a solving image; "
          f"verification {ver.get('checked', 0)} checked / {ver.get('ok', 0)} ok / {ver.get('failed', 0)} failed")


if __name__ == '__main__':
    main()
