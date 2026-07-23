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

---

## Head-to-head: the strongest single signal

`experiments/clustering/rank_signals.py` → `signal_ranking.json`. Every candidate had originally been measured somewhere different — `max_knots` on the whole population, `smaller mean block` only inside one bucket, unevenness only in the matched band — so picking a winner from those numbers would be picking a winner from four different experiments. This puts all of them on one footing: both populations, raw AUC, AUC with total length regressed out, AUC inside the matched band. **Total length is the yardstick, not a candidate.**

### Winner: `smaller mean block`

The mean run length of whichever generator appears in *shorter* runs.

| | A tables (113+124) | B provenance-matched (113+159) |
|---|---|---|
| raw AUC | **0.912** | 0.827 |
| AUC, length removed | **0.751** | **0.706** |
| AUC, matched band 13–25 | **0.904** | 0.818 |
| best cut | `> 1.25` | `> 1.25` |
| balanced accuracy | **0.945** | 0.807 |

On the full 237 the rule `smaller mean block > 1.25` gives **117 tp / 6 fp / 7 fn / 107 tn** — precision 0.951, recall 0.944. The same threshold is optimal in both populations independently, which is not something a fitted parameter usually does.

> In a solvable presentation the thinner generator appears as **isolated single letters**; in an unsolvable one it **clumps into runs of two or more**.

Inside the max_knots = 2 bucket it sharpens further: AUC 0.989 raw / 0.981 length-removed, and `> 1.25` catches **all 23 unsolved with only 6 false positives** (recall 1.000).

### What this demotes

- **`max_knots`** — AUC 0.860 on A with a clean monotone gradient, but **0.673 on B and 0.490 (chance) with length removed**. Once both sides are produced the same way it is largely a length proxy. Its *rules* survive (`max_knots ≥ 4`, `min_knots ≥ 3`, each 14 unsolved / 0 solved) because those describe a tail, not a correlation.
- **Block unevenness (`max ÷ mean block`)** — 0.803 / 0.820 raw but 0.636 / 0.588 length-removed, and it collapses entirely *within* a bucket (0.689 → 0.432). A real between-bucket effect, not a within-bucket one.
- **Total length** is itself a serious confound at 0.809 / 0.831; only `smaller mean block` clearly clears it on both populations.

### Caveats

Hypothesis-driven and supervised — not protected by the unsupervised sweep's permutation null (the within-bucket nulls in the previous section are its own). And "unsolved" means *not yet trivialised at the budgets tried*, so this may track what current search finds hard rather than what is AC-nontrivial.

## 8. Held-out validation: 70/30 split, 200 seeds

`experiments/clustering/holdout_eval.py` → `holdout_eval.json`. Everything above was fitted and scored on the *same* states, so those accuracies are upper bounds, not estimates — the threshold was chosen by scanning every value in the data. Here the cut is refit on a stratified 70% and scored on a 30% the fit never saw, over 200 seeds.

### The 11 columns

Ten candidates plus total length. Length is the *yardstick* when a statistic competes against it alone, but a legitimate term once it is only one column of a model — so `ALL (logistic)` is 11 wide, not 10. All are computed on the concatenated signed-block decomposition of both relators, and all are rotation-invariant.

| # | column | what it is |
|---|---|---|
| 1 | `smaller mean block` | mean run length of whichever generator appears in **shorter** runs |
| 2 | `larger mean block` | the same for the other generator |
| 3 | `max_knots` | `max(knots(r1), knots(r2))` |
| 4 | `min_knots` | `min(knots(r1), knots(r2))` |
| 5 | `knot number (sum)` | `knots(r1) + knots(r2)` |
| 6 | `knot density` | knot sum ÷ total length |
| 7 | `max ÷ mean block` | block unevenness — how much the longest run exceeds the average |
| 8 | `block CV` | standard deviation ÷ mean of run lengths |
| 9 | `max block length` | longest single run |
| 10 | `mean block length` | mean run length over both generators |
| — | `total length` | `|r1| + |r2|` — the confound, and the 11th column |

### Results

| model | A tables · 71 held out | B provenance-matched · 82 held out |
|---|---|---|
| all 11 columns, logistic | **0.981 ± 0.013** | **0.867 ± 0.030** |
| 3-feature (`smaller mean block` + `max_knots` + length) | 0.975 ± 0.018 | 0.857 ± 0.030 |
| 2-feature (`smaller mean block` + `knot number`) | 0.980 ± 0.016 | 0.745 ± 0.043 ⚠ |
| `smaller mean block` alone | 0.945 ± 0.024 | 0.787 ± 0.036 |
| `max_knots` alone | 0.853 ± 0.035 | 0.638 ± 0.041 |
| total length alone (yardstick) | 0.760 ± 0.042 | 0.777 ± 0.046 |
| labels shuffled (leakage control) | 0.522 *(base rate 0.523)* | 0.556 *(base rate 0.585)* |

**Nothing was lost to held-out evaluation.** The in-sample 0.945 for `smaller mean block` reproduces exactly out-of-sample, because 1.25 is refit identically from all 200 training halves — with a threshold that stable there is nothing to overfit. `tests/clustering/test_holdout_eval.py` pins that: 200 seeds, 200 identical fits.

### Which columns the model actually uses

`forward_selection` adds one column at a time, each scored out-of-sample. A weight table cannot answer this — the columns are heavily collinear (`knot number` = `max_knots` + `min_knots`; `block CV` and `max ÷ mean block` measure one thing twice), so L2 splits a shared effect across correlated columns and each looks individually modest.

| step | A tables | B provenance-matched |
|---|---|---|
| 1 | `smaller mean block` → 0.933 | `smaller mean block` → 0.798 |
| 2 | `knot number (sum)` → **0.983** *(+0.051)* | `mean block length` → 0.843 *(+0.045)* |
| 3 | `total length` → 0.988 *(+0.004)* | `knot number (sum)` → 0.863 *(+0.020)* |
| 4 | flat | `block CV` → 0.875 *(+0.012)* |
| | all 11 = 0.982 | all 11 = 0.870 |

**Block thickness enters first in both populations, and it is most of the model.** On A, two columns then match all eleven.

### ⚠ The two-column model does not transfer

On A, `smaller mean block` + `knot number` reaches 0.980 against 0.981 for all eleven — and it is exactly the pairing the knot hypothesis predicts, which is what makes it worth stating carefully. On the provenance-matched population it scores **0.745, below the single feature at 0.787**. Once both sides are produced the same way the knot count stops carrying information independent of block thickness, and a column that adds nothing still costs variance. Forward selection on B agrees: it picks `mean block length` second, not knots.

The **3-feature model is the one that survives both** (0.975 / 0.857). Pinned as a test so the pair is not later promoted to the headline.

### The seed is not a result

Best of 200 seeds on A is **1.000** against a mean of 0.981 and a worst seed of 0.930. With 71 test points a single split's standard error is ≈ 0.04, so the maximum of 200 draws sits about 2σ high *by construction* — the same garden-of-forking-paths the unsupervised sweep corrects with a permutation null. A seed is a property of the split, not of the model: it does not transfer to the next 30%. The mean is the estimate; the spread is the honest error bar.
