# Elliot Steffen's searches with the full CoV family

The three greedy searches of ACSolverES (E. Steffen) on MS640, bench60 and ladder100, with their CoV steps replaced
by every CoV image of the state. Code: `benchmark/elliot/fullcov/`. Run in the session container (4 cores), 5 Nov 2026;
every row is solved within 31,332 units, so no larger run was needed.

## The searches

The queue engines are a pure-Python port of the C++ of ACSolverES (`engine.py`). With the 24 auto-CoV maps the port
gives the committed nodes and path of all 714 distinct presentations of `results/elliot_100k` (`check_port.py`), both
as the dual and as the triple with its CoV queue switched off. Parameters are the paper config of ACSolverES:
preference thresholds 2, no gap between CoV moves, the start state CoV-expanded once (not charged), ties to the
deepest state.

| method | queues |
|---|---|
| dual, single CoV | sub queue + one CoV queue: every CoV image (was: single CoV, always an automorphism) |
| dual, auto CoV | sub queue + one CoV queue: the 24 maps x -> x y^k, y -> y x^k (1 <= abs(k) <= 6), then every CoV image (was: the 24 maps only) |
| triple | sub queue + auto queue (the 24 maps) + CoV queue: every CoV image (was: complete CoV) |

Changes from the original beyond the CoV step:

- **No length bound.** The C++ stores at most 64 letters per state and drops longer children; the port keeps every
  state. States up to total length 145 were discovered (none is on a solution path: path states reach at most total length 25 and relator length 20).
- **Triple:** every state popped from the sub queue enters the CoV queue (the original admits only states passing a
  composite letter-count filter, which fits its k >= 2 complete CoV only), and every CoV pop is charged one unit, even
  one with no image (the original charged none).

**Units:** one per pop of any queue, as in the paper. The enumeration of the images is not charged.

## The CoV images: `acx.cov.states.cov_states`

The function shared with the CoV-gate search (the same images, order and representatives as
`acx.cov.images.iter_images(..., max_len=None, family="suballpxyb8")`, 3x faster). For a state (r1, r2):

- **Words:** w is any cyclic subword of either relator of length 2 <= |w| <= |r| - 1. The whole relator is excluded,
  and w and w^-1 count as one word.
- **Substitution:** every set of non-overlapping occurrences of w and w^-1 is substituted (at least one), the seam
  included. Then either generator is eliminated, from either relator that holds it once.
- **Identification:** images are merged up to relator order, rotation, inversion, cyclic reduction and the 8 signed
  relabellings of x, y. An image in the class of the state itself is dropped.

**Rotation.** Every rotation of the input is used: all cyclic windows w and all occurrences across the seam. So the
different z^-1 w relators that different rotations give are all generated. Only finished images whose relators differ
by a rotation are merged. Rotating a relator is a conjugation, and the engine already stores states up to rotation,
inversion and order, so those images are the same state for the search. Keeping them apart would change nothing.

## AC path or stable certificate

A CoV step is an **automorphism** when the isolating relator holds exactly one z. Then the elimination reads
t = s^a z^(+-1) s^b, and psi: t -> expr is an automorphism of F2. Let z = zeta(s, t) solve it. Then psi^-1 of the
image is (the other relator with each w replaced by zeta, zeta^-1 w). Here zeta^-1 w is a conjugate of the isolating
relator R, so each replacement multiplies by a conjugate of R^(+-1), which is an AC move. A row whose CoV steps are all
automorphisms (and the 24 maps, which are) is therefore an **AC path**, transported by Aut(F2). Any other row is a
**stable AC certificate** (Lemma 11).

## Results (`SUMMARY_TABLE.md`)

| benchmark | method | 10^3 | 10^4 | 10^5 | 10^6 | 10^7 | AC path | stable cert |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| MS640 | dual, single CoV | 612 | 634 | 640 | 640 | 640 | 465 | 175 |
| | dual, auto CoV | 612 | 627 | 640 | 640 | 640 | 477 | 163 |
| | triple | 612 | 637 | 640 | 640 | 640 | 484 | 156 |
| bench60 | dual, single CoV | 49 | 57 | 60 | 60 | 60 | 26 | 34 |
| | dual, auto CoV | 49 | 53 | 60 | 60 | 60 | 28 | 32 |
| | triple | 49 | 58 | 60 | 60 | 60 | 31 | 29 |
| ladder100 | dual, single CoV | 73 | 98 | 100 | 100 | 100 | 47 | 53 |
| | dual, auto CoV | 72 | 94 | 100 | 100 | 100 | 55 | 45 |
| | triple | 73 | 97 | 100 | 100 | 100 | 60 | 40 |

The search is deterministic and the budget only stops it, so a row solved in u units is solved at every budget >= u.
The 10^6 and 10^7 columns follow from the 10^5 run.

## Files and checks

- **`<bench>__<algo>.jsonl`:** one record per row. It holds the units (`units` = `nodes`), the pops per queue, the
  path, `path_length` (each CoV counts 1), the S-moves, the CoV moves by kind (`full_cov_aut`, `full_cov_stable`,
  `auto_cov`), `kind`, the longest relator and total, and `cov_used`. Each `cov_used` entry is a CoV step with its
  states, w, eliminated generator, isolating relator, expr, substituted pair, number of occurrences and automorphism
  flag. Rows solved within 10^4 carry `carried_from`.
- **`VERIFY.json`:** `benchmark/elliot/fullcov/verify_fullcov.py` replayed every step of every solved path, with
  `all_pass: true`:
  - S-moves are checked by their own loop.
  - The 24 maps are reapplied.
  - Every CoV step is redone with `acx.cov.apply_steps` (Lemma 11 and |det| = 1).
  - The AC / stable verdict is re-derived (the form of expr, and zeta^-1 w conjugate to R) and agrees with the
    logged one on every step and row.
