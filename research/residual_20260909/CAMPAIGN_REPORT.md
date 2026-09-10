# Closing the AC19 Aut-minimal census at 1,000 charged units

Campaign of 2026-09-09 on the 727 rows of `data/AC19_extended_aut_min.csv`
(72,779 rows, SHA-256 `7e220253...4ae2`) that the published policy
(`research/supermoves_20260908/final_policy.py`, commit 98f719e2, 72,052 solved)
left unsolved at 1,000 charged units per presentation.

**Result: 72,779 / 72,779 solved and independently verified at 1,000 units,
0 lost, with 7.0x fewer charged units and 8.3x less search wall than the
published census.** Bundle: `results/heuristic_search/ac19_ball14_cascade_full_1k/`.

| census (1,000 units, all 72,779 rows) | solved | charged units | search wall | certificate wall | census wall (4 workers) |
|---|---:|---:|---:|---:|---:|
| published `final_policy` (98f719e2) | 72,052 | 6,621,411 | 389.2 s | 109.4 s | serial, 1,976 s incl. 1,471 s cooldown |
| control: the same cascade, **no table** (`K3p_notable`) | 72,562 | 5,871,522 | 840.1 s | 213.3 s | 279 s |
| round 1: cascade + cap-12 aut table (`K3p_c12aut`) | 72,738 | 2,829,457 | 172.4 s | 203.1 s | 108 s |
| **round 2: cascade + cap-14 aut table (`K3p_c14aut`)** | **72,779** | **949,521** | **46.7 s** | 186.2 s | **70 s** |

**How to read the units.** The cap-14 table is precomputed search (BFS
outward from the trivial pair, 12.8M states, 27 min to build once, no census
input) and its lookups are uncharged, so the "1,000 units" of `K3p_c14aut` is
the forward search *on top of* that ball. 66,151 of the 72,779 roots (91%) lie
inside it and cost 0 units. The no-table control row separates the two
ingredients: the new rules alone take the census from 72,052 to 72,562 (567
gained, 57 lost) at 11% fewer units than the published policy; the table
accounts for exactly the last 217 rows and for the drop from 5.87M to 0.95M
units. Every table hit still yields a genuine AC path, replayed independently.
Details: `results/heuristic_search/ac19_K3p_notable_full_1k/README.md` and
NOTES.md, "What the table does, stated plainly".

Worst single row: 0.456 s search wall (published 0.454 s). No row is charged
more under `K3p_c14aut` than it was under the published policy. The one cost
that rose is certificate decoding (the stored table tails are decoded and
replayed on every solve), and the elementary certificates are 4 % longer in
total on the rows both policies solve (median 243 moves against 248).

## 1. What the theorems are worth

`THEOREMS_PROOFS_AND_FREQUENCY.md` audits every completion rule inherited from
the supermoves campaign: hypotheses, proof status, where the code deviates from
the prose, and how many census rows each one actually closed. The ranking that
came out of it:

1. Plain `S20_MK2` greedy search closes 60 % of the census. Not a theorem.
2. The consecutive BS(m, m+1) collapse with its Britton preflight closes 35 %,
   6.8x every other theorem together, at 53 units per row, cheaper than the
   search it replaces. It is the strongest theorem, as believed, and the belief
   is tested in section 5 of that document rather than assumed.
3. Primitive-donor elimination through the one-occurrence gate: 5 %.
4. Two-block unimodular reduction: 99 rows. Everything else (torus/amalgam,
   stable-power, splice-power, stable-square, Christoffel, the escape features)
   closes nothing at this budget.

None of these rules, nor the new ones proved during the campaign (BS-DEMOTE
for stalled BS companions, the four-block theorems F1/F3/L1, the family
theorems W2-W4 and Rule W-TRANSPORT), reaches more than a few of the residual
rows: the 727 are 97 % non-BS rows on which the search simply ran out of
budget. The diagnosis that settled the campaign was that the frozen cascade's
0/102 on the dev panel is an allocation artifact (the incumbent stage alone
solves 87/102 with the whole budget), and that what the residual needed was a
cheap, exact terminal, not another recognizer.

## 2. The method: an exact backward ball as terminal

`B(cap)` is the set of canonical pairs from which an elementary path to
`(x, y)` exists with every intermediate relator of length at most `cap`,
closed under the four Nielsen automorphisms. It is built backwards from
`(x, y)` with full products, forward-verified against the search kernel, and
replay-checked; every entry stores its successor and move, so a hit splices a
stored tail into the certificate (`BACKWARD_TABLE.md`). The cascade looks the
root and every generated state up in the table; lookups are uncharged but
counted. Because the cascade is otherwise unchanged and a lookup can only
terminate a search earlier, it dominates the frozen cascade at the same
allocation: every row the frozen policy solved is solved at no greater charge
(confirmed row by row on the census).

| table | states | file | load | RSS | rows resolved at the root |
|---|---:|---:|---:|---:|---:|
| cap 12, automorphism-closed (dict) | 1,488,649 | 68.7 MB | 1.9 s | 0.5 GB | 24,708 |
| cap 14, automorphism-closed (compact) | 12,803,449 | 281.7 MB | 1.3 s | 0.37 GB | 66,151 |

The cap-14 table (26.9 min single-thread build, 1.95 GB peak) is stored in a
packed uint64 format (`CompactTable`), key-for-key identical to the dict
builder at caps 8-12, and is gitignored with its manifest and rebuild command
committed. On top of the table the shipped cascade `K3'` keeps the published
stage order with a reallocated split: 250-unit strict-donor stage with a
certified overrun for preflight-accepted BS collapses (needed by ac19_109),
300-unit plain S20 stage, incumbent restart, plus BS-DEMOTE.

## 3. Protocol and measurements

The 727 residual rows were clustered on cheap features and saved traces and
split into three disjoint stratified panels (dev 102, val 102, test 101) plus
422 held-out rows; 60 near-limit rows the published policy solves form the
regression panel. Rules were developed on planted positives, adversarial
near-misses and dev only; val was opened once to choose among the pre-registered
candidates K0-K5 (rule written down in `NOTES.md` before opening it); test was
opened once after the choice. Round 2 changed only the table (cap 12 to cap
14); no constant was re-tuned.

| panel (1,000 units) | published policy | `K3p_c12aut` | `K3p_c14aut` |
|---|---:|---:|---:|
| dev (102) | 0 | 94 | **102** |
| val (102, hidden) | 0 | 94 | **102** |
| test (101, frozen) | 0 | 97 | **101** |
| regression 60 | 60 | 60 | **60** (0 units) |
| round-1 residual (41) | 6 | 0 | **41** (max 201 units) |

Every solve in every table above was decoded to elementary AC moves and
replayed independently to `(x, y)`.

## 4. Verification of the final bundle

- `verify_bundle.py`: input hash, 73 shards tiling the census once, names unique
  and in input order, 0 errors, max charge 699, solved == verified == 72,779,
  SUMMARY.json totals and clocks recomputed from the rows, the manifest's 42
  source hashes and 8 table hashes equal to the tree at commit 4a4500af. PASS.
- `replay_census.py`: all 72,779 stored mixed paths re-decoded and re-replayed
  in fresh processes with the two independent decoders, all ending at `(x, y)`
  with the recorded move count; 0 failures (`replay_check.json`).
- `census_summarize.py --baseline`: 727 gained, 0 lost, 0 rows missing.
- 341 tests pass (`research/residual_20260909/tests`).

## 5. Negative results worth keeping

- A score-guided best-first table (storing the states a heuristic search would
  reach first) was worse than the uniform ball.
- The stable-power gate charged failed attempts and lost a regression row; the
  stable-square donor never fires on the dev donor rows; four-block rule N1 is
  false (counterexample recorded); F1/F3/L1 are proved but reach no residual row.
- A capped "pocket" plain stage before the cascade (`policies_round2.py`)
  gained 1 dev row on the cap-12 table and became unnecessary at cap 14.
- Rule TRAIL (layering certified states from published certificates) reaches
  30/41 of the round-1 residual on the cap-12 table; superseded by cap 14.

## 6. Caveats

- Under a table terminal, charged units count only the search work outside
  the ball; 90.9 % of the census is charged 0. The unit count is a budget, not
  a difficulty measure; wall time is reported alongside for that reason.
- The cap-14 table is 269 MiB on disk and 0.37 GB per worker in memory; it
  must be rebuilt (27 min) from the committed manifest's command before the
  census can be reproduced.
- Certificates are on average 4 % longer than the published ones and the
  longest grew from 17,485 to 26,002 elementary moves.
- The family theory (`theory/FAMILY_THEORY.md`) explains why 20 of the 41
  round-1 roots were hard and certifies them by transport; one family
  (r1 = YYXXYxYXX) is solved by the table but not yet explained.

## 7. Reproduction

```bash
PYTHONPATH=. python3 -m research.residual_20260909.backward_table --cap 14 --aut-edges --compact \
    --out research/residual_20260909/tables/ball_cap14_aut.npz        # 27 min, 2 GB
PYTHONPATH=. python3 -m research.residual_20260909.census_run \
    --input data/AC19_extended_aut_min.csv --policy K3p_c14aut --budget 1000 \
    --out results/heuristic_search/ac19_ball14_cascade_full_1k --offset 0 --limit 72779 \
    --shard-size 1000 --workers 4
PYTHONPATH=. python3 -m research.residual_20260909.census_summarize --input data/AC19_extended_aut_min.csv \
    --result-dir results/heuristic_search/ac19_ball14_cascade_full_1k \
    --baseline results/heuristic_search/ac19_final_policy_full_1k
PYTHONPATH=. python3 -m research.residual_20260909.verify_bundle --result-dir results/heuristic_search/ac19_ball14_cascade_full_1k
PYTHONPATH=. python3 -m research.residual_20260909.replay_census --result-dir results/heuristic_search/ac19_ball14_cascade_full_1k --workers 4
```
