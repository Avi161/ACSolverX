# Unsupervised structure in the 237 minimal automorphic states

Built by `experiments/clustering/run_cluster_237.py` (`python3 -m experiments.clustering.run_cluster_237`, ~25 s, numpy + scipy only). Live write-up: the published artifact.

**Question.** Does *unsupervised* clustering of the minimal automorphic states recover the solved / unsolved split without ever being shown it? The clustering never sees the label; the label is used only to score a partition afterwards. **No AC moves are run anywhere** — this is purely about the initial states, treated as pairs of cyclic words.

| file | what it is |
|---|---|
| `cluster_report.json` | every number on the page, both populations |
| `cluster_grid_tables.csv` | all 4,898 scored clusterings, population A |
| `cluster_grid_provenance-matched.csv` | all 4,918 scored clusterings, population B |

## Two populations, and why the second one is the point

**A — tables**: 113 solved Aut(F₂)-orbit reps + 124 unsolved ACA-class reps.

**B — provenance-matched**: 113 + 159 orbits, every one produced *identically* as `raw MS cell → aut_canon`. Population A's two sides were **manufactured by different processes** — the unsolved reps had already been rewritten by an upstream bounded AC reduction (`EQUIVALENCE_FINDING.md` §1: local minima of somebody else's search, on average 2.74 letters shorter than the cells they name). A clustering could separate those by detecting *which pipeline emitted the word*. Population B removes the difference.

## Result

| | best ARI | null max (1000 perms) | p |
|---|---|---|---|
| A tables | **0.5815** | 0.0761 | < 0.001 |
| B provenance-matched | **0.3184** | 0.0822 | < 0.001 |

Reporting the best of ~4,900 (representation × preprocessing × metric × algorithm × k) combinations is a garden of forking paths, so the calibrating statistic is **best-observed vs best-under-permuted-labels on the identical grid**. Roughly 45% of population A's signal was provenance (0.58 → 0.32) — which is exactly why the control was worth running. What remains is still 3.9× the null maximum.

On its own terms, the unsupervised k=4 split of population B puts **104 states in a cluster that is 98.1% unsolved** and 71 in one that is 86% solved. The axis is the same in both populations: longer words with more uneven block structure are the unsolved-rich clusters.

## Representations

All 17 are **rotation-invariant**, enforced as a gate (re-featurise randomly rotated rings; max deviation 1.1e-16). A feature that can see where the canonicaliser cut the ring measures the tie-break, not the mathematics.

The headline one is the **ring autocorrelation**, a training-free analogue of the Two-Hump paper's Dual-Ring Transformer. That architecture gives its attention a cyclic relative positional encoding (`d(i,j) = (i−j) mod L`); where it *learns* weights over that distance we *tabulate* the empirical distribution `A[a,b,d] = #{i : w[i]=a, w[(i+d) mod L]=b}`. Rotation multiplies every letter channel's DFT by the same phase, so `Ŝ_a·conj(Ŝ_b)` has its phases cancel. **The cross-*ring* product is not invariant** — the rings rotate independently — so cross-ring features may only combine per-ring magnitudes.

A second gate is **faithfulness**: does the representation even separate the 237 distinct orbits? Several standard choices do not — the Whitehead graph, the most mathematically native object here, collapses 133 of them.

## The knot statistic (hypothesis-driven — not covered by the sweep's null)

A **knot** is a block of one generator squashed inside the other, counted cyclically; `knots = max(#x-blocks, #y-blocks)`.

> **Theorem.** If a cyclic word contains at least one x-type *and* one y-type letter, #x-blocks = #y-blocks.
>
> *Proof.* Maximal blocks partition the cycle into arcs whose labels alternate by maximality, so `ℓⱼ = ℓ₁` for odd `j` and `ℓⱼ = ℓ₂ ≠ ℓ₁` for even `j`. Cyclicity forces `ℓ_m ≠ ℓ₁`; if `m` were odd then `ℓ_m = ℓ₁`, a contradiction. So `m` is even and exactly `m/2` arcs carry each generator. ∎

Counting on x or on y is therefore *forced* to agree, not a convention. The sole exception is a **pure power** (`X`, `yyy`), outside the hypothesis, where the counts are 1 vs 0 — and it really occurs (`sol_001` ships `r₁ = X`). `max` resolves it. All of this is machine-checked in `tests/clustering/test_knots.py` (8 tests): exhaustively over every cyclically reduced two-generator word to length 9, on every shipped relator, plus invariance under rotation, relator inversion and the x↔y swap.

**Where the hypothesis lands.** Unsolved really do carry more knots (AUC 0.860) — but that is largely **length**, and it weakens to 0.673 under the provenance control. Per unit length the sign *flips*: knot density gives AUC 0.286 in the clean population, i.e. unsolved have **fewer** knots per letter and **longer** blocks. The robust signal is **unevenness**: `max ÷ mean block` is scale-free by construction, scores AUC 0.803 / 0.820 across the two populations, holds at 0.779 / 0.795 inside the matched length band, and unlike knot count gets *stronger* under the control. Unsolved presentations are not more finely knotted — they carry one dominant long block among shorter ones.

**The threshold is > 2, not > 3.** `some relator has > 2 knots ⇒ unsolved` reaches 0.854 balanced accuracy (precision 0.894, recall 0.815). At `> 3` the rule is *perfectly precise* — 14 hits, zero false positives, so ≥4 knots is a **sufficient** condition in this data — but it catches only 11%.

## Caveats

- **Not causation, not a solvability test.** "Unsolved" means *not yet trivialised at the budgets tried*, so this may describe what current search finds hard rather than what is AC-nontrivial.
- **Length is not fully removed.** Residualising on *total* length leaves the |r₁| vs |r₂| asymmetry; in population B no representation beat the shape control once total length was regressed out.
- Population A mixes two granularities (Aut(F₂) on one side, the coarser ACA on the other). B is the cleaner object.
- The knot features were chosen because of a conjecture about the label, so their AUCs are **not** protected by the permutation null that covers the sweep.
- The supervised classifier in the report is a **diagnostic**, not a result — it is shown the labels, and serves only as an upper bound on what any unsupervised method could recover.
