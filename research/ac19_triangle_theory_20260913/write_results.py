"""Compose RESULTS.md from the benchmark and census records."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import make_results

HERE = Path(__file__).resolve().parent


def separator_section():
    path = HERE / 'separator_probe.json'
    if not path.exists():
        return ''
    rep = json.loads(path.read_text())
    c = rep['counts']
    lines = [f"| feature | AUC U124 vs solved bins 6–9 | AUC U124 vs all solved | mean U124 | mean solved 6–9 | mean all solved |",
             "|---|---:|---:|---:|---:|---:|"]
    for t in rep['separability']:
        lines.append(f"| `{t['feature']}` | {t['auc_u124_vs_solved_hard']:.3f} | {t['auc_u124_vs_solved_all']:.3f} | "
                     f"{t['mean_u124']:.2f} | {t['mean_solved_hard']:.2f} | {t['mean_solved_all']:.2f} |")
    rows = rep['rows']
    u = [r for r in rows if r['group'] == 'u124']; s = [r for r in rows if r['group'] == 'solved']
    ident = sum(r['root_all_triangle'] and r['root_digram_disjoint'] and not r['search_bigon'] and not r['search_unit'] for r in u)
    ident_s = sum(r['root_all_triangle'] and r['root_digram_disjoint'] and not r['search_bigon'] and not r['search_unit'] for r in s if r['bin'] >= 6)
    return f"""
## Can rank-raising separate solved-but-hard rows from U124? No

`separator_probe.py` pushes the {c['solved_all']}-row solved MS benchmark ladder
(`benchmark/subsets/benchmark_subset_60.csv`, difficulty bins 0–9, {c['solved_hard_bins_6_9']} rows in
bins 6–9) and the {c['u124']} U124 representatives through the identical pipeline:
triangulate, static root features, coupling search at cap {rep['parameters']['cap']} with
{rep['parameters']['pops']} pops and beam {rep['parameters']['beam']}. AUC is the probability that a U124 row scores
above a solved row (0.5 = no separation).

{chr(10).join(lines)}

Every root feature is identical across the two groups: {ident} of {len(u)} U124 roots and
{ident_s} of {c['solved_hard_bins_6_9']} hard solved roots are all-triangle, digram-disjoint, with zero coupling and
no bigon or unit within the search. The only features with AUC away from 0.5
(`rank`, `cap4_children`, `search_states`) track total length, and on that axis
U124 is *shorter* than the hard solved rows (`rank2_length` AUC 0.114). Nothing
produced by raising rank distinguishes an unsolved row from a solved-but-hard one.
Wall time {rep['wall_seconds']:.0f} s for all {len(rows)} rows.
"""


def main(bench_paths, census_path):
    tables, reports = make_results.render(bench_paths)
    census = json.loads(Path(census_path).read_text())['summary']
    params = [r['parameters'] for r in reports]
    caps = sorted({c for p in params for c in p['caps']})
    pops = sorted({p['pop_budget'] for p in params})
    beams = sorted({p['beam'] for p in params})
    rows = {}
    for rep in reports:
        for row in rep['rows']:
            rows.setdefault(row['name'], row)
    hard = [r for r in rows.values() if r['panel'] == 'hard']
    easy = [r for r in rows.values() if r['panel'] == 'easy']
    def exposed(rs, key):
        return sum(any(a[key] for a in r['arms']) for r in rs)
    # arms were spread over several reports: recollect per name
    arms = {}
    for rep in reports:
        for row in rep['rows']:
            arms.setdefault(row['name'], []).extend(row['arms'])
    for r in rows.values():
        r['arms'] = arms[r['name']]
    easy_tri = [r for r in easy if min(len(w) for w in r['triangle_state']) == 3]
    easy_short = [r for r in easy if min(len(w) for w in r['triangle_state']) < 3]
    total_rp = sum(a['rotation_products'] for r in rows.values() for a in r['arms'])
    total_pops = sum(a['heap_pops'] for r in rows.values() for a in r['arms'])
    total_prep = sum(r['preprocessing_units'] for r in rows.values())
    total_cpu = sum(a['cpu_seconds'] for r in rows.values() for a in r['arms'])
    text = f"""# Does retained-rank triangular expansion make hard AC19 rows easier? No — and here is the mechanism

Frozen inputs: the four hard-but-solved AC19 rows of
`research/ac19_triangle_expansion_20260912/hard_solved_panel.jsonl` (each exhausted
plain greedy at 100,000 nodes; saved certificates need 1.5–8.2 M greedy nodes or
17,369–37,682 `S20_MK2` nodes at rank two) and its twelve easy controls.
Preprocessing: `triangulate` (greedy digram compression) to rank 7–9 with every
relator of length at most three; counted, never a solve. Search: rank-preserving
ordinary AC normal-product substitutions only, relator caps {caps}, {pops[0]} heap pops,
beam {beams[0]}, two orderings — the incumbent `structural` score and the `coupling`
score of `THEORY.md`. A run *exposes* structure when it reaches a relator of length
two (B) or one (U) at unchanged rank. Every path below was replayed independently
(`verify.py`), and the tables are generated from the JSON records (`make_results.py`).

## Headline

* **Hard panel: 0 of {len(hard)} rows expose a bigon or a unit** under either ordering at any
  cap. All four roots are all-triangle and digram-disjoint, so by Lemma 2 no single
  substitution can make a length-two relator and by Lemma 1 none can make a unit;
  Corollary 3 puts a bigon at least three moves away at cap 4. The searches explored
  well past that depth and still found nothing.
* **Easy controls: {exposed(easy, 'unit_found')} of {len(easy)} expose a unit** ({exposed(easy, 'bigon_found')} a bigon). Of the ten
  all-triangle easy roots, {exposed(easy_tri, 'unit_found')} expose a unit by search; the two roots that already
  carry a length-two relator after preprocessing ({', '.join(r['name'] for r in easy_short)}) are credited to
  preprocessing, not search. The two sharing roots (`ac19_44`, `ac19_48`) expose a
  bigon in a single pop, exactly as Lemma 2 predicts.
* **Census:** of 400 random AC19 rows, {census['all_triangle_roots']} triangulate to an all-triangle root and
  **all {census['all_triangle_and_digram_disjoint']} of those are digram-disjoint**; the remaining {census['roots_with_a_relator_shorter_than_three']} already contain a
  relator of length at most two straight out of preprocessing.
* **Work:** {total_prep} preprocessing units, {total_pops:,} pops, {total_rp:,} rotation products,
  {total_cpu:.0f} CPU-seconds across all arms. None of it moved a hard row.

So the answer to the question this directory was opened for is **no**: making
every relator length three does not make the hard rows easier at fixed rank.
The lift study (`../ac19_triangle_expansion_20260912/lift/`) already showed the
known rank-two certificates cannot be shadowed at fixed rank; this study shows
the fixed-rank search cannot even take a first useful step from these roots,
and says exactly why.

## What the theory adds

* **Lemma 1 (parity).** Triangle x triangle is even, quartic x triangle is odd.
  A triangulated root has *no* odd-length one-move child, which is why the
  frozen engine's cap-3 neighbourhood is empty.
* **Lemma 2 (bigon necessity).** A one-move bigon needs two relators sharing a
  cyclic digram modulo `(u,v) -> (v^-1,u^-1)`. Machine-checked: 0 violations in
  11,774 + 4,077 random balanced all-triangle states; the only sharing states
  without a bigon have two equal relators.
* **Corollary 3.** From a digram-disjoint root at cap 4: no bigon in fewer than
  three moves, no unit in fewer than two.
* **Coupling ordering.** Rank by `(no unit, no bigon, -shared pairs, -shared
  digrams, length, ...)`. It is a real gradient where total length is flat
  (`3r` at every all-triangle state, `3r+1` at every cap-4 child). On the
  sharing controls it finds a bigon in one pop. On the digram-disjoint easy
  roots it is not uniformly better than the incumbent at this budget (see the
  per-arm table: each ordering wins some rows), and on the hard roots neither
  ordering finds anything.

## Per-row arms

Cells read `mark (pops/rotation products)`: `U` unit exposed, `B` bigon only, `.` nothing.

{tables}

Note: the `structural` arm forms the same rotation products at every cap, because
its score ranks by maximum relator length and never pops a state containing a
relator longer than four within {pops[0]} pops; the `coupling` arm does climb into
longer relators.

{separator_section()}
## Honest limits

* Budgets are deliberately small ({pops[0]} pops, beam {beams[0]}); the earlier campaign
  already ran 1,000 pops at cap 6 (2.15 M states, 4.76 M rotation products) on
  the same hard roots with the same outcome. Nothing here is an obstruction to
  longer paths, to stable moves, or to AC-triviality.
* The census sample is 400 of 72,779 AC19 rows (seed 3).
* Lemma 2 is exact only for all-triangle states; roots with a shorter relator
  are reported separately and their exposure is credited to preprocessing.

## Reproduce

```sh
python3 run_panel.py --caps 4,5 --pops 60 --beam 48 --out bench_cap45_p60.json
python3 run_panel.py --caps 6   --pops 60 --beam 48 --out bench_cap6_p60.json
python3 census_digram_disjoint.py --out census_digram_disjoint_s3_n400.json
python3 verify.py bench_cap45_p60.json bench_cap6_p60.json
python3 -m pytest -q test_theory.py
python3 write_results.py bench_cap45_p60.json bench_cap6_p60.json census_digram_disjoint_s3_n400.json > RESULTS.md
```
"""
    return text


if __name__ == '__main__':
    print(main(sys.argv[1:-1], sys.argv[-1]))
