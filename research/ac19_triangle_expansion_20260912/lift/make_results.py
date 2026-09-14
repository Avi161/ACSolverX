"""Render RESULTS.md from lift_hard.json, lift_easy.json and gradient.json."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name):
    return json.loads((HERE / name).read_text())


def path_table(rows, title):
    lines = ['#### ' + title, '',
             '| row | arm | states | rank-2 L max | rank-2 maxrel | rank_t min..max '
             '(mean) | rank_t at step 0 | rank changes | dict drift | longest stable run '
             '| distinct defs | mean shared w/ init |',
             '|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|']
    for row in rows:
        s = row['summary']
        lines.append('| %s | %s | %d | %d | %d | %d..%d (%.2f) | %d | %.3f | %.3f | %d | %d | %.2f |' % (
            row['name'], row['arm'], s['path_states'], s['max_rank2_total_length'],
            s['max_rank2_relator_length'], s['min_rank'], s['max_rank'], s['mean_rank'],
            s['initial_rank'], s['rank_change_fraction'], s['dictionary_change_fraction'],
            s['longest_unchanged_run'], s['distinct_definitions_on_path'],
            s['mean_shared_with_initial']))
    lines.append('')
    return lines


def cap_table(rows, title):
    lines = ['#### ' + title, '',
             '| row | arm | cap to follow path | interior min | steps needing cap>6 | '
             'fraction | first step past cap 4 | past cap 5 | past cap 6 |',
             '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for row in rows:
        s = row['summary']
        lines.append('| %s | %s | **%d** | %s | %d/%d | %.3f | %s | %s | %s |' % (
            row['name'], row['arm'], s['max_over_path_encoded_optimal_max'],
            s['min_interior_encoded_optimal_max'], s['steps_exceeding_cap_6'],
            s['path_states'], s['fraction_exceeding_cap_6'],
            s['first_step_exceeding_cap_4'], s['first_step_exceeding_cap_5'],
            s['first_step_exceeding_cap_6']))
    lines.append('')
    return lines


def gradient_table(rows):
    lines = ['| row | panel | rank | neighbours | distinct scores | tie fraction | '
             'best-score ties | better | equal | worse | all-triangle children | constant components |',
             '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for row in rows:
        lines.append('| %s | %s | %d | %d | %d | %.3f | %d | %d | %d | %d | %d | %d/11 |' % (
            row['name'], row['panel'], row['rank'], row['neighbours'],
            row['distinct_scores'], row['tie_fraction_all'],
            row['best_score_multiplicity'], row['strictly_better'],
            row['equal_to_parent'], row['strictly_worse'],
            row['neighbours_all_triangle'], len(row['constant_components'])))
    lines.append('')
    return lines


def main():
    hard = load('lift_hard.json')
    easy = load('lift_easy.json')
    gradient = load('gradient.json')
    hrows, erows = hard['rows'], easy['rows']
    hs = [row['summary'] for row in hrows]
    es = [row['summary'] for row in erows]
    grows = gradient['rows']

    hard_cap = [s['max_over_path_encoded_optimal_max'] for s in hs]
    easy_cap = [s['max_over_path_encoded_optimal_max'] for s in es]
    hard_drift = [s['dictionary_change_fraction'] for s in hs]
    easy_drift = [s['dictionary_change_fraction'] for s in es]
    hard_rank = [s['max_rank'] for s in hs]
    easy_rank = [s['max_rank'] for s in es]
    hard_defs = [s['distinct_definitions_on_path'] for s in hs]
    easy_defs = [s['distinct_definitions_on_path'] for s in es]
    hard_exceed = [s['fraction_exceeding_cap_6'] for s in hs]
    easy_exceed = [s['fraction_exceeding_cap_6'] for s in es]
    ties = [row['tie_fraction_all'] for row in grows]
    consts = [len(row['constant_components']) for row in grows]

    text = f"""# Why fixed-rank, fixed-dictionary triangle search cannot shadow the known rank-2 solutions

Companion to `../RESULTS.md` (triangular expansion + fixed-rank ordinary AC search:
0/4 solves on the hard panel, 5/12 on the easy control panel).  Nothing here is a
new search; it is a measurement of the *known* rank-2 certificates, lifted into
the triangle picture with the exact `high_rank_triangles.triangulate` and
`high_rank_ac_search` code the failed experiment used.

## Hypothesis under test

> A fixed-rank, fixed-dictionary triangle search is a search over rank-2
> presentations restricted to those whose compressed encoding under the INITIAL
> dictionary stays within a tiny cap.  The known rank-2 paths require the
> dictionary and the rank to change continually, and they pass through rank-2
> relators of length 33-35, so no fixed-rank triangle path with cap <= 6 can
> shadow them.  At the triangle level every all-triangle state has total length
> 3r, so the length gradient that drives rank-2 search is flat.

**Verdict: supported on all three counts, with one scope limit (see Caveats).**

## Method

For every state of every saved certificate (both arms for each hard row: the
8.2M/1.5M-node greedy path and the S20_MK2 path; the plain S20 path for the easy
controls) we ran `triangulate` and recorded

* the rank-2 total length `L` and maximum relator length,
* the triangle rank `r_t` (always `2 + #definitions`), the number of triangles,
* every defining compression **fully expanded to a word in x, y**, canonical up
  to inversion — this is "the dictionary at that state",
* the cost of writing that rank-2 state using the **initial** dictionary only.
  Both a greedy longest-match tokenization and an exact dynamic program that
  minimises over *all* tokenizations and all rotations are computed; the
  reported cap uses the exact minimum, so it is a genuine lower bound on the
  relator cap a fixed-dictionary search would need.

## 1-2. Dictionary drift and rank drift

{chr(10).join(path_table(hrows, 'Hard panel (4 rows x 2 saved certificates)'))}
{chr(10).join(path_table(erows, 'Easy control panel (3 longest solved paths)'))}
* The fully expanded definition set changes at **{min(hard_drift):.1%}-{max(hard_drift):.1%}** of hard-path
  steps ({min(easy_drift):.1%}-{max(easy_drift):.1%} on the easy controls).  The longest run of consecutive
  steps with an unchanged dictionary is **3** on every single path, hard and easy.
* Only **one** state per path (step 0, by construction) carries exactly the
  initial dictionary.  On average a hard-path state shares
  {min(s['mean_shared_with_initial'] for s in hs):.2f}-{max(s['mean_shared_with_initial'] for s in hs):.2f} of its 5-12 definitions with the initial dictionary.
* **{min(hard_defs)}-{max(hard_defs)} distinct definitions** appear along a hard path, against an initial
  dictionary of 5-7.  The easy controls use {min(easy_defs)}-{max(easy_defs)}.
* The triangle rank is not fixed and not monotone: hard paths reach
  **r_t = {min(hard_rank)}-{max(hard_rank)}** while the fixed-rank search is pinned at the root rank 7-9,
  and they also drop below it (the rank changes at {min(s['rank_change_fraction'] for s in hs):.0%}-{max(s['rank_change_fraction'] for s in hs):.0%} of steps).
  Easy paths stay at **r_t <= {max(easy_rank)}** and spend most of their steps *below* the root
  rank — they descend to rank 2 almost immediately.

## 3. The cap a fixed-dictionary search would need

{chr(10).join(cap_table(hrows, 'Hard panel'))}
{chr(10).join(cap_table(erows, 'Easy control panel'))}
"cap to follow path" is the maximum over path steps of the minimum, over all
tokenizations under the initial dictionary, of the longest encoded relator.
"interior min" excludes the trivial endgame (states of rank-2 total length <= 6),
where the answer collapses to 1-2 for every path.

* Hard paths need cap **{min(hard_cap)}-{max(hard_cap)}**; the experiment ran cap 4 (macro), cap 5 and
  cap 6 (deep).  **{min(hard_exceed):.1%}-{max(hard_exceed):.1%}** of hard-path states are outside cap 6 entirely.
* A cap-6 fixed-dictionary search leaves every hard path at **step 2 or 3** of
  61-97 — it can shadow at most the first two moves.
* Easy paths need cap **{min(easy_cap)}-{max(easy_cap)}**; {sum(s['steps_exceeding_cap_6'] for s in es)} of their {sum(s['path_states'] for s in es)} states sit outside cap 6
  ({min(easy_exceed):.1%}-{max(easy_exceed):.1%} per row, versus {min(hard_exceed):.1%}+ for every hard path).

Worked example (`ac19_66724`, S20_MK2 arm, step 18, the worst state on any path):
the rank-2 pair is `YYYxYxYYYxyXYYxYx`, `YYYxYYYxYxYYYxYxYYXyyx` (L = 39,
max relator 22).  Its own triangulation needs 12 fresh definitions
(r_t = 14), **none of which is in the initial dictionary**.  Under the initial
dictionary `{{XX, xxY, Yxx, yyXX, XXyX}}` no tokenization writes the two relators
in fewer than **22** and **17** letters respectively.

## 4. Gradient flatness at the triangle roots

`high_rank_ac_search.generate(words, relator_cap=4)` at each root, scored with the
engine's own `structural_score`:

{chr(10).join(gradient_table(grows))}
* Every all-triangle root of rank r has total length exactly **3r**, and every
  cap-4 child has total length exactly **3r + 1** — a product of two length-3
  cyclic words has even cyclically reduced length, so no child is all-triangle
  ({sum(row['neighbours_all_triangle'] for row in grows)} across all {sum(row['neighbours'] for row in grows)} children generated here).  The length
  signal is therefore constant across the entire declared neighbourhood.
* **{min(consts)} to {max(consts)} of the 11 score components are literally constant** over the whole
  neighbourhood, including all seven leading components
  (`has_excess, excess, max_length, n_long, -#units, -#bigons, -shared_digrams`) at
  6 of the 7 roots.  Only `repeated` (3-4 values), `min_degree` (2-3 values) and
  occasionally `shared_digrams` (2 values) move at all.
* {min(row['distinct_scores'] for row in grows)}-{max(row['distinct_scores'] for row in grows)} distinct score tuples are spread over {min(row['neighbours'] for row in grows)}-{max(row['neighbours'] for row in grows)} neighbours: a tie
  fraction of **{min(ties):.1%}-{max(ties):.1%}**.  The best-scoring class alone holds
  {min(row['best_score_multiplicity'] for row in grows)}-{max(row['best_score_multiplicity'] for row in grows)} states.
* At every root, **0 children are better than or equal to the parent**; all
  {sum(row['neighbours'] for row in grows)} are strictly worse.  Each root is a strict local minimum of the
  engine's score, and the frontier beyond it is nearly score-blind.  This is the
  mechanism behind the "one-state component" observation in `../RESULTS.md`.

## 5. Positive control

The three longest solved easy-control paths were lifted identically.  Their
dictionaries drift almost as often ({min(easy_drift):.0%}-{max(easy_drift):.0%} of steps), so drift by itself is not
what separates easy from hard.  What separates them is **scale**: peak triangle
rank {max(easy_rank)} vs {max(hard_rank)}, {min(easy_defs)}-{max(easy_defs)} distinct definitions vs {min(hard_defs)}-{max(hard_defs)}, encoding cap
{min(easy_cap)}-{max(easy_cap)} vs {min(hard_cap)}-{max(hard_cap)}, and {sum(s['steps_exceeding_cap_6'] for s in es)}/{sum(s['path_states'] for s in es)} vs {sum(s['steps_exceeding_cap_6'] for s in hs)}/{sum(s['path_states'] for s in hs)} states outside cap 6.  An easy path stays
essentially inside the initial dictionary's reach; a hard path does not.  This
matches the outcome of the original experiment (5/12 easy solved, 0/4 hard).

## Conclusion

The evidence supports the hypothesis.

1. **The dictionary is not fixed along the known solutions.** It changes at
   {min(hard_drift):.0%}+ of steps, never stays put for more than 3 consecutive steps, and a hard
   path visits {min(hard_defs)}-{max(hard_defs)} distinct definitions against an initial dictionary of 5-7.
2. **The rank is not fixed either.** Hard paths run from r_t = 2 to r_t = {max(hard_rank)}
   while the experiment held rank at 7-9, changing rank at roughly half of all steps.
3. **The cap is the binding constraint.** Following a hard path with the initial
   dictionary requires a relator cap of {min(hard_cap)}-{max(hard_cap)}, not 4-6.  A cap-6 search falls off
   every hard path by step 3.  This alone explains 0/4 without appealing to
   search budget: the paths are not in the searched set.
4. **The score cannot compensate.** At the roots, the declared cap-4
   neighbourhood is one flat shell: constant total length 3r+1, {min(consts)}-{max(consts)} of 11 score
   components constant, {min(ties):.0%}+ ties, and no non-worsening child.

A definition-aware search (one that may introduce, retire, and rewrite
definitions, and whose score reads the dependency graph rather than the relator
lengths) is the indicated next step, exactly as `../RESULTS.md` suspected.

## Caveats

* This shows the fixed-rank, fixed-dictionary search cannot **shadow these
  specific certificates**.  It is not a proof that no cap-6 fixed-rank path to a
  solution exists — a fixed-rank search may also rewrite the definition rows
  themselves and take a completely different route.  The gradient result says
  only that its score gives it no help in finding one.
* "The dictionary at a state" means the set produced by the deterministic greedy
  `triangulate`; a different triangulation policy would give different sets.  The
  encoding cap in section 3 does not depend on that choice — it is computed
  against the initial dictionary by exact minimisation.
* Definitions are compared as words up to inversion after full expansion to x, y,
  not up to conjugacy; conjugate definitions count as distinct.
* The panel is small and frozen: 8 hard certificates (4 rows x 2 saved arms)
  and 3 easy-control paths.  These are measurements of saved certificates, not a
  sample of all solutions.

## Reproduce

```bash
cd /home/user/ACSolverX/research/ac19_triangle_expansion_20260912/lift
python3 run_lift.py        # writes lift_hard.json, lift_easy.json, gradient.json, tables/
python3 make_results.py    # regenerates this file from those JSONs
python3 verify.py          # re-derives every headline number from the saved JSON
```

Per-step markdown tables for each row and arm are in `tables/`.
Inputs are pinned by SHA-256 in the `inputs_sha256` block of each JSON.
"""
    (HERE / 'RESULTS.md').write_text(text)
    print('wrote RESULTS.md')


if __name__ == '__main__':
    main()
