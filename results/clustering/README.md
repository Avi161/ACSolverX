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

---

## Bucket enumeration: does knots = 0 or 1 occur?

Buckets are enumerated from 0, never only over the values present — an omitted bucket reads as "not counted" when it means "empty".

- **knots = 0 does occur** — 7 of the 474 relators, every one of them the bare relator `X`, in `sol_001`…`sol_007`. A pure power has one block of its own generator and none of the other, so nothing is squashed inside anything and the literal reading of the definition gives **0**. A `max(#x,#y)` tie-break would say 1, but that rule exists to reconcile the counts when they *disagree*, and here there is no tie to break. 0 is also the informative value: a pure-power relator kills a generator outright (`sol_001` is ⟨x,y | x, YYXyx⟩, i.e. x = 1), so it flags a degenerate, trivially-collapsing presentation.
  The choice is **inert where it matters**: no presentation's `max_knots` changes at all, and only `min_knots` shifts 1 → 0 for exactly those 7. Pinned by `test_pure_power_convention_does_not_move_max_knots`.
- **knots = 1 occurs on 2 relators** — `YYYYxxx` and `YYYYxxxxxxx`, which have one block of *each* generator and so are genuinely one knot.
- **max_knots = 1 never occurs**: every presentation with a 1-knot relator has the other relator at ≥2. So max_knots ranges over {2,3,4,5} and min_knots over {1,2,3}.

## Two independent sufficient conditions

Solved presentations occupy a tight box: `max_knots ∈ {2,3}` **and** `min_knots ∈ {0,1,2}`. Anything outside it is unsolved.

| rule | solved | unsolved | precision | recall |
|---|---|---|---|---|
| `max_knots ≥ 4` (some relator is busy) | 0 | 14 | 1.000 | 0.113 |
| `min_knots ≥ 3` (**both** relators busy) | 0 | 14 | 1.000 | 0.113 |
| **either** | **0** | **24** | **1.000** | **0.194** |
| both | 0 | 4 | 1.000 | 0.032 |

They overlap on only 4 states, so together they certify **24 of the 124 unsolved with zero false positives** — nearly double either alone.

The mirror also holds: **`min_knots = 0` is a pure *solved* bucket, 7 for 7** — exactly the presentations whose relator kills a generator. (`min_knots = 1` holds only 2 states; read nothing into it.)

## Inside a bucket: exponent signs vs block sizes

`experiments/clustering/within_bucket.py` (`python3 -m experiments.clustering.within_bucket`) → `within_bucket.json`. Feature code in `signed_knots.py`; a **signed block** is `(generator, length, exponent sum)`.

### The exponent ±1 carries nothing, and it cannot

All three "sign alternates inside a block" features measure **exactly 0.00** on all 237. That is a theorem, not a dataset quirk:

> **In a freely reduced word, every maximal same-generator block is a pure power.** Two adjacent letters in a block share a generator; opposite signs would make the word contain `xX` or `Xx` and it would not be reduced. So a block is always `x^k` or `X^k`.

The fingerprint is that **mean |exponent| and mean block length have identical AUCs** (0.769/0.769 at max_knots = 2; 0.989/0.989 at 3) — because |exponent| = length for every block. The only remaining sign freedom is one sign per block, and that tests at chance (AUC 0.515, 0.522). Pinned over 50,000+ blocks in `tests/clustering/test_signed_knots.py`.

### What does separate: the *thinner* generator's block size

Every feature is scored both raw and with total length regressed out, because length still varies inside a bucket.

**max_knots = 2 (101 solved / 23 unsolved).** Length alone gives AUC 0.797. `smaller mean block` — the mean run length of whichever generator runs thinner — gives **0.989 raw and 0.981 with length removed**, the only feature that beats length. Every other block statistic collapses: max block length 0.743 → **0.500**, unevenness 0.689 → 0.432, block-length sd 0.748 → 0.483. So the between-bucket "unevenness" story does **not** operate within a bucket.

Distributions barely touch: solved span 1.00–1.75 (median 1.25), unsolved 1.50–1.75 (median 1.75). The rule `smaller mean block > 1.25` flags **all 23 unsolved and only 6 of 101 solved** — recall 1.000, balanced accuracy 0.970.

> In a solvable presentation the thin generator appears as **isolated single letters**; in an unsolvable one it clumps into runs of two or more.

Null: best |AUC−0.5| over all 14 features = 0.489 against a 95th percentile of 0.161 and a max of 0.298 over 2,000 permutations → p < 0.001. Not the small bucket talking.

**max_knots = 3 (12 solved / 87 unsolved).** Length alone reaches AUC 0.994 (13.0 vs 19.6 letters), so little room is left. Mean block length holds 0.885 after length removal, but with 12 solved states treat this bucket as corroboration, not independent evidence.

### Block signatures

Necklace-canonical block-size sequences — literally how many x's and y's sit between each knot. Read `x1y7x1y8` as x-block 1, y-block 7, x-block 1, y-block 8.

| | most common |
|---|---|
| solved, max_knots 2 | `x1y2x3y1 \| x2y1x3y1`, `x1y1x2y1 \| x1y2x1y3` |
| unsolved, max_knots 2 | `x1y7x1y8 \| x2y2x3y1`, `x1y4x1y5 \| x2y1x3y1` |
| solved, max_knots 3 | `x1y1x1y2x1y2 \| x1y1x2y1` |
| unsolved, max_knots 3 | `x1y1x2y1x2y1 \| x1y3x1y4`, `x1y1x2y1x2y1 \| x1y7x1y8` |

Solved presentations are built from small numbers throughout; unsolved ones carry a long single-generator run. Same knot count, very different interiors.

**Caveat.** This section is hypothesis-driven and supervised — it asks what separates a known label — so it is not covered by the unsupervised sweep's null. Its own within-bucket permutation nulls are reported above instead.
