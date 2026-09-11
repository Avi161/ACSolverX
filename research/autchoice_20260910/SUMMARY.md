# Which automorphic image is easiest to search from? — summary

Question (2026-09-10): the same AC-move sequence read from an AC19 original is a
flat length profile and from its aut-min representative a mountain; at 10M greedy
pops 40/40 originals solve and 0/28 representatives do. "Shortest under Aut(F₂)"
is not "easiest to search from". Can the easy image be found, and does it crack
anything nothing solves? Three parts, each with its own README, commands, input
hashes and independently replayed certificates.

## 1. The atlas (`ATLAS.md`, `atlas.jsonl`)

124 rows (20 each from ladder levels 3–5, the 28 level-9 representatives plain
greedy cannot solve at 10M, and their 40 originals); every image within two
Whitehead moves (`autcanon.AUTOS`, relabel-deduplicated, cap 48; median 13 images
per row); S20_MK2 at 20,000 pops through `hcompact`; 1,612 searches, 715 solves,
all replayed from the row's own pair through the automorphism steps.

- **Choosing the image is worth more than a decade of budget.** Best-of-13 (an
  oracle) raises solves at 20k from 94/124 to 119/124 and at 5k from 64 to 101.
  On the 28 level-9 representatives: the row as given 6, the best image 26.
- The row as given is the cheapest image on 10/124 rows; some image is strictly
  cheaper on 114/124, by a median factor of 10^0.67 ≈ 4.7.
- **Length is not the ordering.** The shortest image is the cheapest on 10/124;
  Spearman(image length, log cost) = 0.22 pooled. The winning image is usually
  two moves deep and longer than the row.
- No single Whitehead move helps on average (best one strictly cheaper than the
  identity on 26% of rows).
- The originals: the original as given beats the best image of its
  representative's radius-2 ball on 29/40 pairs; the original's relabel class
  lies in that ball on 17/40 and within radius 4 on 40/40.
- `plot_pairs.py` reproduces the length-profile figure from the committed data.

## 2. The predictor (`predictor/PREDICTOR.md`, `rank_images.py`)

72 cheap features of the image's start state (block/knot statistics, exponent
sums, S20 priority, lengths, generator sequence), a pairwise logistic ranker on
feature differences with per-row normalisation, numpy only; 5 outer folds with no
source row in two folds, regularisation by inner CV; selected on top-1 regret.

| top-1 pick of the 13 images (held out) | solved @20k /124 | @5k /124 | level 9 /28 | regret (log10 over best) |
|---|---:|---:|---:|---:|
| row as given | 94 | 64 | 6 | 0.720 |
| shortest image | 62 | 33 | 6 | 1.040 |
| lowest S20 priority | 71 | 41 | 8 | 0.961 |
| **pairwise ranker** | **99** | **76** | **17** | **0.434** |
| oracle | 119 | 101 | 26 | 0.000 |

The ranker closes 55% of the identity-to-oracle gap on level 9 at 20k (67% at
5k), wins 13 / loses 8 rows against the row as given, and at equal compute its
top-1 beats spreading the budget over several images. Hand-made two-feature
rules do not transfer between folds. `rank(pair, radius=2, cap=48)` returns the
images ranked, with the automorphism sequence for each.

## 3. Applied to the unsolved (`applied/APPLIED.md`)

Targets: the 124 unsolved Miller–Schupp classes in both forms (as first found
and μ-reduced) and the two level-9 AC19 orbits whose radius-2 ball did not
solve in the atlas. Phase 1: every radius-2 image at 20k (3,238 records, 2,100
distinct searches). Phase 2: radius-3 images at 20k and the ranker's top images
at 200k on the 2 leftovers + the 10 closest classes. Every claim re-verified in a
fresh process from the JSONL alone (3,458 records, 2 claimed solves, 2 ok).

- **0 of 124 classes solved**, in either form, at any budget run. On the
  μ-reduced forms no image's search ever saw a state below the start; on the
  un-reduced forms the drops seen are the known μ-reduction rediscovered.
- **`ac19_7284` solves** from a depth-3 image (the same Whitehead move three
  times, image length 22 vs 19) in 14,030 pops with 75 AC moves; replayed from
  the original pair. With radius 3, 27 of the 28 level-9 representatives have a
  sub-20k S20_MK2 image; `ac19_27254` is the one left (best image reaches
  length 15 from 19, not 2).
- **One new shorter form of an unsolved class.** From `aca_111` as first found
  (length 25; best known 24), a 42-move AC path with peak length 41 reaches a
  state of total length 23, `(YYXXYxyxxyX, YYYYYYXXXyxx)` — certified by the
  engine's parent walk and by an independent replay (`applied/short_states.json`,
  and again in this session with `words.replay_move`). The census's "best" forms
  came from caps 30–36; this path needs 41. The frozen files under `data/` are
  not touched; this is a record for the next census pass.

## What it means

The image matters and can be predicted, on the hard-but-solvable rows: the
ranker turns 6 → 17 of the 28 level-9 representatives at 20k (oracle 26), and a
radius-3 ball reaches 27 of 28. It does not reach the 124 classes nothing has
solved: their balls sit at the start length whatever the image. The next lever
for those is not the automorphism but the AC path length itself (the `aca_111`
path needs peak 41, beyond every cap the census used).

## Ladder note (2026-09-11)

After this study the ladder was reshaped: the 124 unsolved classes moved off it into
`benchmark/ladder/unsolved_124.csv` / `unsolved_all_forms.csv`, and the 28 "level 9"
representatives above are now level 9 (19, S20_MK2 solves them) and level 10 (9, only
the cascades do). `panel.csv` and `applied/targets.csv` are unchanged in content.

A second reshape on the same day took the 45 `form = original` rows out of the ladder's
panel strata: they are the originals of only 33 orbits, selected because their aut-min
partner is greedy-unsolved at 10M, so they are not a sample of `AC19_extended.txt` and
round-robin was giving them 12–20% of a panel (and scoring 21 of 22 orbits twice, once
as the original and once as its partner). They stay in `ladder_all.csv` — which is
byte-identical, so every hash recorded here still resolves — in `ladder_pairs.csv` and
in the new `benchmark/ladder/originals_45.csv`. `ladder_200.csv` did change in levels
1–4; `panel.csv` is frozen against the 2026-09-10 copy (sha in `panel_manifest.json`)
and is not rebuilt, so `build_panel.py` no longer reproduces it from the current ladder.
Nothing in this study's numbers depends on panel membership: it reads the originals and
the level-9/10 rows from the pool.

## Provenance

Git head at run time `460904f9` (B1, B2) and `7fa813ae`–`85b5d079` (B3's final
phases); inputs hashed in each README; the certificates carry elementary
automorphism steps followed by substitution moves, decodable by
`harness.run_row`'s decoder.
