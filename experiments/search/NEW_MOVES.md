# New moves besides substitution — the conjugate-donor macro

[`macro_moves.py`](macro_moves.py) adds the one genuinely new sound move available to the
rank-2 search, [`certify.py`](certify.py) proves every path it returns, and
[`bench_new_moves.py`](bench_new_moves.py) scores it against the greedy baseline and the
`s20_mk2` ordering on the frozen 60-row benchmark at 100–1,000-node budgets.

## Why "new moves" means exactly one thing here

The search state is a pair of cyclically reduced words, canonical up to rotation, inversion
and swap. Conjugating a whole relator is invisible on such states, so every possible single
AC step is "multiply one relator by a conjugate of the other":

```
r_i  <-  cyc( r_i · w r_j^ε w⁻¹ ),    ε ∈ {+1, −1},
```

where the conjugator `w` matters only modulo powers of the root of `r_j^ε`. The Definition
2.1 substitution move `rot_k1(r_i)·rot_k2(r_j^ε)` realises exactly the cosets `w = u·v⁻¹`
with `u` a prefix of `r_i` and `v` a prefix of `r_j^ε` — and the implemented generator
additionally keeps only children with a cancelling concatenation seam (a search restriction,
not a soundness condition). Everything else in the one-step AC neighbourhood is unreachable
in one substitution step, and *every* sound one-step extension of the move set is a wider
conjugator family. That family widening is the **conjugate-donor macro**:

```
r_i  <-  r_i · (w r_j^ε w⁻¹),      r_j unchanged (the donor is restored).
```

It is an explicit AC composite, never a new axiom. For `ε = +1`: conjugate `r_j` by `w⁻¹`
one letter at a time, right-multiply `r_i` by the conjugated donor, undo the conjugations.
For `ε = −1`, wrap that in an invert/restore pair. Costs are tracked both ways: macro cost
3 (5 for `ε = −1`) certificate-level actions, elementary cost `2|w|+1` (`2|w|+3`) one-letter
conjugations — the honest expansion cost, reported per solved path as `elementary_cost`.

Conjugator families shipped (finite; sizes are search parameters, not hypotheses):

* every freely reduced `w` with `|w| ≤ 2` — including `w = ''`, the plain multiply that the
  substitution seam filter excludes;
* every cyclic subword of the two current relators and of their inverses with length 3–4 —
  bridge words that can cancel deeply where prefix-product cosets cannot;
* **goal-directed proposals** (`goal_conjugators`): for each short candidate replacement `s`
  with `|s| ≤ 2`, the right defect `f = r_i⁻¹·s` is checked for conjugacy to `r_j^ε` — a
  decidable cyclic-word equality — and on a hit the match yields `w` with `f = w r_j^ε w⁻¹`
  explicitly, so `r_i → s` becomes ONE donor edge (the design's goal-directed defect
  factorisation, restricted to single-factor certificates, which need no oracle). The
  proposer changes which children are offered, never what an edge means: a proposed edge is
  an ordinary donor certificate and verifies the same way.

## What is deliberately NOT in the move set

The move set must match the claim the benchmark makes. Every arm here claims **ordinary
AC-triviality with an explicit path** (`AC_EQ`), because the baseline it is scored against
claims exactly that. Three families from the wider design were evaluated and excluded from
*this* benchmark on soundness-taxonomy grounds, not implementation difficulty:

| candidate | relation it proves | why it cannot be an arm here |
|---|---|---|
| stabilise → work → destabilise round trips, CoV/compression portals | stable-AC equivalence (`STABLE_EQ`) | a path through rank 3 proves stable triviality only, even when it returns to rank 2; counting it as a solve would silently upgrade the claim |
| Lemma-11 generalised stabilisation/removal | `STABLE_EQ`, existential (no elementary trace, no move count) | same, plus it has no honest node cost to charge the budget |
| ambient automorphism portals | `AC_TRIVIAL_IFF` (simultaneous trivialisability, not pairwise equivalence) | a solve would be a theorem-composed existence proof, not an explicit path; a fair comparison against path-finding arms needs a separate scoreboard |

These are worth building — as portal edges in a proof DAG that keeps `relation_kind`
explicit — but mixing them into an `AC_EQ` benchmark would make the solve counts
incomparable.

## Proof-carrying: certificates and the independent verifier

A solved path returns `path_certs`, one typed certificate per edge:

```
["sub",   target, jsign, k1, k2]     Definition 2.1 substitution
["donor", target, jsign, w]          conjugate-donor with conjugator w
```

`certify.py` shares no inference code with the engine (plain strings, no numba). It expands
each certificate into primitive AC moves — invert, right-multiply, one-letter conjugation —
from the *stored parent state*, replays them, and then walks the replayed words onto the
stored child state with explicit "hop" primitives: cyclic reduction and rotation are letter
conjugations, inversion is a primitive, and the pair swap is materialised as the classical
six-move-plus-conjugation composite (`swap_ops`). A verified path is therefore one flat
primitive-move trace from the input presentation to a trivial one, with every stored state
checked letter for letter.

The verifier also rejects a trap the solved test cannot see: a final state like `(x, x)` is
two length-1 relators but normally closes a proper subgroup. On a genuine trivial-group
input it is unreachable, but the check costs nothing and caught two malformed synthetic
inputs during development.

`tests/test_macro_moves.py` pins: the control gate (donor moves off + length ordering IS the
baseline, pop for pop), engine/verifier agreement on random states, end-to-end verification
of real solved paths, mutation resistance (corrupted sign / target / conjugator / rotation,
reordered edges, truncated paths all fail), and the degenerate-endpoint rejection.

## Benchmark

`python -m experiments.search.bench_new_moves` runs the 2×2 grid — move set
{substitution, substitution+donor} × ordering {length, `s20_mk2`} — on
[`benchmark_subset_60`](../../benchmark/subsets/benchmark_subset_60.csv), one 1,000-node run
per arm per row (a budget-B search is the first B pops of a longer one, so one run yields
the whole 100–1,000 curve). Cap 24, cyclic reduction on. A solve counts only if its path
verifies; `s20_mk2 = L + 20·S + 2·MK` is the research branch's arm, ported verbatim as
`heuristics.S20_MK2`. The tuned five-feature `RECOMMENDED` vector is deliberately not an
arm: its weights were fitted on rows this subset overlaps, so its numbers here read as
overfit and it was dropped from the comparison.

### Results

All solves verified; nothing unverified, no lost jobs. Full per-row data in
[`results/new_moves/`](../../results/new_moves/): `bench60_newmoves.*` is this table's run
(defaults), `ablation1000_blind_*` the subword-bridge family at the same budget
(`--goal-smax 0 --subw 3 4`).

| arm | moves | ordering | @100 | @250 | @500 | @1000 | median nodes | wall s |
|---|---|---|---:|---:|---:|---:|---:|---:|
| greedy | sub | `L` | 17 | 20 | 26 | **29** | 61 | 40.2 |
| s20_mk2 | sub | `s20_mk2` | 21 | 28 | 35 | **37** | 52 | 56.1 |
| macro_L | sub+donor | `L` | 17 | 20 | 26 | **29** | 61 | 114.3 |
| macro_s20_mk2 | sub+donor | `s20_mk2` | 21 | 28 | 35 | **37** | 52 | 77.2 |

**The macro arms tie their plain counterparts exactly — not just in solve counts but
per row**: all 60 presentations, both orderings, identical `(solved, solved_at,
path_length)`, zero donor edges on any solved path. The donor children are generated and
enter the frontier by the tens of thousands, and not one of them wins a heap pop inside
1,000 nodes. Node budgets are pop counts and the macro arms pay 1.4–2.8× the wall time per
pop, so at equal *time* the macro arms are strictly worse here.

### Why, mechanistically

* A blind donor child has length at least `|r_i| + |r_j| − 2|w|` — the conjugator can
  cancel at both of its boundaries, nothing more. Substitution's rotation family already
  realises the maximal single-boundary cancellations, so under any length-dominated
  ordering the blind donor children never outrank the best substitution children. Measured
  twice: this run's short-word family, and the full subword-bridge family at the same
  1,000-node budget (`ablation1000_blind_*`: `--goal-smax 0 --subw 3 4`, hundreds of
  extra children per node) — exact ties again, at 2.8–3.8× the plain arms' wall time.
* The goal-directed proposer is the one source of genuinely *short* children — but its
  precondition (`|cyc(r_i⁻¹s)| = |r_j|`) needs near-matched relator lengths. Instrumented
  over 7 benchmark rows: it fires on **7 of 4,384 expanded states**, every one an endgame
  state of total length ≤ 8 (e.g. `(Y, YYX)`) where substitution descends anyway. On the
  ms640 mid-game — one long relator, one short — the length match cannot hold with short
  `s`.
* Raising the cap to `goal_smax=6` (so the proposer can fire mid-game) flips **zero** of
  the rows unsolved at 1,000 nodes, at ~10× the wall cost: the unsolved frontier (bins
  6–9, 7k–272k baseline nodes) is deep in pops, not one edge away.

So at tiny budgets on this benchmark the move set is not the binding constraint — the
**ordering** is (29 → 37 at a fixed move set). The one-step AC neighbourhood is,
for short children, essentially saturated by substitution; that is now a measured fact
with a mechanism, not a hunch.

## Stage 2 — multi-factor rewrites and the automorphism portal, measured

Two of the design's remaining stages are now arms
(`python -m experiments.search.bench_new_moves --stage2`, data in
`results/new_moves/stage2_*`):

**The multi-factor normal-closure rewrite** (`ncrw`) is the search-usable distillate of
the forest-flow / class-two pipeline, specialised to one donor: to replace `r_i` by a
short `s` in one edge, factor the defect `ρ(r_i⁻¹s)` into conjugates of `r_j^±1` — an
abelianisation obstruction filter first (the class-repair pattern: `ab(f) = t·ab(r_j)`
must have an integer solution), then a peeling lift (the flow pattern: an occurrence of a
rotated donor copy `f = p·ρ·q` peels off as the exact factor `(pρp⁻¹)·(pq)`). A hit is
one certificate, `["ncrw", i, [[ε₁,w₁],…]]`, an exact chained-donor AC composite whose
intermediates live inside the edge — so it also tunnels through the length cap.

**The change-of-variables portal** (`cov`) applies Whitehead peak reduction
(`experiments/analysis/whitehead.py`) to land on the Aut(F₂)-orbit's minimal-length
representative, then runs the plain substitution search on the image. Solving the image
proves the original AC-trivial (`AC_TRIVIAL_IFF`); no path for the original is
materialised, and the claim column keeps that distinction explicit everywhere.

| arm | moves | ordering | claim | @100 | @250 | @500 | @1000 | wall s |
|---|---|---|---|---:|---:|---:|---:|---:|
| greedy | sub | `L` | AC_EQ path | 17 | 20 | 26 | **29** | 37.7 |
| s20_mk2 | sub | `s20_mk2` | AC_EQ path | 21 | 28 | 35 | **37** | 57.6 |
| ncrw_L | sub+goal+ncrw | `L` | AC_EQ path | 17 | 20 | 26 | **29** | 84.7 |
| ncrw_s20_mk2 | sub+goal+ncrw | `s20_mk2` | AC_EQ path | 21 | 28 | 35 | **37** | 56.6 |
| cov_L | Whitehead → sub | `L` | AC_TRIVIAL_IFF | 20 | 24 | 32 | **36** | 43.4 |
| cov_s20_mk2 | Whitehead → sub | `s20_mk2` | AC_TRIVIAL_IFF | 22 | 30 | 35 | **37** | 43.7 |

What the per-row data says:

* **The rewrite edges fire and help — the first nonzero move-set effect — but by 1–3
  pops.** Unlike the blind donors, `ncrw`/goal edges sit on the solved paths of 28
  (`L`) and 36 (`s20_mk2`) of the 60 rows, and on every such row `solved_at` strictly
  improves (9→6, 7→4, 10→7, …), never worsens. The savings are endgame jumps — one
  rewrite replaces the last few substitution pops — and at 1–3 pops each they never
  cross a budget checkpoint, so the solve counts tie. Path lengths shorten too (median
  22→20 under `s20_mk2`).
* **The portal is a strict improvement on its baseline and reaches rows nothing else
  does.** `cov_L` solves every row `greedy` solves plus 7 more (538, 544, 565, 575,
  609, 628, 633); `cov_s20_mk2` weakly dominates `s20_mk2` early (+1 @100, +2 @250) and
  ties late. Across all arms the union of rows **proved AC-trivial is 41/60 — s20_mk2
  alone proves 37** — with rows 565, 575, 628, 633 reached only through the portal.
  (Pooling the union is legitimate because both claim types prove AC-triviality; the
  split — 37 with explicit paths, +4 portal-only — must travel with the number.)
* **Tiny coordinate changes, outsized effect.** Whitehead reduction shortens 38 of the
  60 starts by a mean of only 1.2 letters (max 5, mean 1.2 automorphism steps) — yet
  that is worth +7 solves to the length-ordered greedy. Orbit-minimal coordinates and
  the `s20_mk2` ordering exploit overlapping structure (both prefer untangled words),
  which is why the portal lifts the weak ordering far more than the strong one.

Still untested from the design: general two-gluing composites ("cap tunnels" whose
factors are substitutions rather than factorizable defects), Lemma-11/CoV `STABLE_EQ`
portals on a stable scoreboard, and deeper linear layers (finite-quotient relation-module
solving) feeding the factorizer when peeling stalls. The engine, certificate format, and
verifier here are the infrastructure all of them plug into; the claim column is the
honesty gate that keeps their scoreboards separated. The powered-connector rewrite (I)
has no search analogue — nothing in this pipeline evaluates cochain invariants — and
collision-first batching (J) appears here only as the aggregation discipline inside the
abelian filter.
