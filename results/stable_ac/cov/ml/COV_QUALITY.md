# Which change of variables is worth running?

Every presentation in the 66-row benchmark admits ~100 applicable changes of variables, and week 5 only ever reported what the *best* one costs — an oracle number, paid for by running all of them. This asks the deployable question instead: **given the candidate list and no search budget spent yet, which z should you run first?**

Code: [`experiments/stable_ac/cov/ml/`](../../../../experiments/stable_ac/cov/ml/) — `cov_features.py` (feature table), `cov_rank.py` (train + evaluate), `cov_figures.py`. Data: the week-5 sweeps at budgets 10,000 / 1,000 / 100, unchanged. No new search was run.

## Headline

**The abelianisation of the transformed pair, not its length, says whether a CoV is worth running.** Define the *abelian mass* of a pair ⟨r₁, r₂⟩ as

```
mass = |Σx(r₁)| + |Σy(r₁)| + |Σx(r₂)| + |Σy(r₂)|
```

where Σg(r) is the exponent sum of generator g in r. It costs O(|r₁| + |r₂|) to compute — no search, no canonicalisation. Sorting a presentation's candidate z's by ascending abelian mass and taking the first one:

| searches per presentation | how the z is chosen | solved | mean nodes, same 31 |
|---|---|---:|---:|
| 0 | plain greedy, no CoV at all | 40 / 66 | — |
| 1 | at random | 42 / 66 | 832 |
| 1 | non-automorphic only, then at random | 41 / 66 | 612 |
| 1 | shortest resulting relators | 47 / 66 | 377 |
| 1 | **lowest abelian mass** | **47.4 / 66** | 447 |
| 3 | **lowest abelian mass** | **52 / 66** | 70 |
| ~109 | oracle — keep the winner | 52 / 66 | — |

**Three searches, chosen by a one-line rule, match what running all ~109 achieves.** One search does not — 47.4 / 66.

Two things about that table. "Solved" is fractional because abelian mass is a small integer and **a median of 6 candidates tie at a presentation's minimum**: the rule shortlists, it does not pick, so the score is an expectation over which tied candidate you draw (200 random draws). And "mean nodes" is scored on the 31 presentations *every* picker solves — letting each picker average over its own solved set would let the weak ones drop exactly the presentations they failed, which are the expensive ones.

### The tie-break is not a detail

An earlier version of this analysis sorted with a stable `argsort`, which breaks ties by the sweep's file order, and reported **52 / 66 for a single lowest-mass pick — the oracle set exactly**. That number was the file ordering, not the rule. Over the tied group at each presentation's minimum mass:

| | solved |
|---|---:|
| worst case — every draw unlucky | 27 / 66 |
| average over random draws | **47.4 / 66** |
| best case — every draw lucky | 52 / 66 |

On 25 of the 66 presentations the tied group is mixed — some tied candidates solve and some do not. That is what makes the average fractional, and what best-of-3 repairs.

## The rule is not "pick the short one"

This is the part worth being careful about, because pooling the data says the opposite.

Pooled over all 6,722 rows, abelian mass looks inert (r = +0.11 against log cost) and total relator length looks like the real signal (r = +0.46). **Both readings are artifacts of pooling.** Presentations differ enormously in baseline difficulty, so a hard presentation's best CoV can cost more than an easy presentation's worst, and that between-presentation spread swamps the within-presentation ordering that actually governs the choice. Scored where the decision is actually made — inside one presentation, against its own candidates:

| within one presentation, median over the 52 presentations some CoV solves | Spearman ρ vs cost |
|---|---:|
| abelian mass | **+0.81** |
| total relator length | +0.36 |
| non-automorphic (moved) or not | +0.00 |
| random | +0.02 |

abelian mass is positive on **52 / 52** presentations. See `simpson.png` — left panel is the pooled scatter that says nothing, right panel is the same data per presentation.

## Why it works

The exponent-sum matrix M = [[Σx(r₁), Σy(r₁)], [Σx(r₂), Σy(r₂)]] has |det M| = 1 for every row in this data (all are presentations of the trivial group — it is the invariant `tests/greedy` already checks the solver against). AC moves act on M by row operations, and the target ⟨x, y⟩ has M = ±I, i.e. mass exactly 2. So abelian mass measures how far the abelianised presentation still has to travel, and unlike relator length it cannot be faked by a substitution that merely inflates the words. Splitting the signal:

- **Does this z solve at all?** Ranking a presentation's candidates by ascending mass separates solvers from non-solvers with median AUC **0.922** (over the 33 presentations at budget 10,000 that have both outcomes).
- **How fast?** Among solved rows only, mass ranks path length at ρ **+0.83** and nodes at ρ **+0.81**; total length manages ρ +0.25 on nodes.

The path-length correlation is the mechanism showing through: mass is a lower-bound-shaped quantity on the abelian work remaining, and path length is what pays it.

The gradient-boosted model independently rediscovers this. Permutation importance on held-out folds gives `d_exp_l1` (the change in abelian mass) **+0.478**, with the next feature at +0.043 — an order of magnitude down.

## Replication across budgets

Same protocol, same features, the two other sweeps:

| | b = 100 | b = 1,000 | b = 10,000 |
|---|---:|---:|---:|
| solved rows | 15.8% | 32.6% | 52.7% |
| presentations some CoV solves | 34 / 66 | 45 / 66 | 52 / 66 |
| ρ, abelian mass (within presentation) | **+0.70** | **+0.80** | **+0.81** |
| ρ, total length | +0.23 | +0.33 | +0.36 |
| AUC, mass picks the solvers | 0.929 | 0.933 | 0.922 |
| ρ vs path, solved rows only | +0.82 | +0.89 | +0.83 |
| pooled r — mass / length | +0.09 / +0.28 | +0.11 / +0.40 | +0.11 / +0.46 |

The mechanism is budget-independent, as it should be: a search at budget B is the first B pops of a longer one, so the ordering it induces over starts cannot depend much on where you stop it. The pooled-vs-per-presentation reversal reproduces at all three budgets.

**What a trained model buys is the tie-break.** Mass narrows ~109 candidates to ~6; ordering *within* that group is the part a rule cannot do. One search each, random tie-breaks throughout:

| solved, ONE search | b = 100 | b = 1,000 | b = 10,000 |
|---|---:|---:|---:|
| lowest abelian mass | 25.7 / 66 | 35.8 / 66 | 47.5 / 66 |
| ridge, centred | **33 / 66** | 39 / 66 | 50 / 66 |
| GBT, centred | 31 / 66 | **40 / 66** | **52 / 66** |
| oracle | 34 / 66 | 45 / 66 | 52 / 66 |

The model beats the bare rule at every budget, and by most at the tightest one — at b = 100 the lowest-mass candidate is more often *just* out of reach, so which member of the tied group you pick matters most. Running three by mass instead of one closes most of the gap for free (b = 10,000: 47.5 → 52; b = 1,000: 35.8 → 41), which is the cheaper answer unless a single search is all you can afford.

Note the linear ridge beats the gradient-boosted trees at budget 100 (33 vs 31). With 51 orbits to split across, the trees are the more overfit arm, not the stronger one.

## What this does not say

- **It shortlists, it does not pick.** The minimum-mass group holds a median of 6 candidates and the rule imposes no order inside it. Quote it as best-of-k, or name the tie-break.
- **It ranks, it does not screen.** The rule orders a presentation's own candidates. It says nothing about whether *this presentation* is worth attacking with a CoV at all — the pooled correlation is exactly the number that would answer that, and it is +0.11.
- **The 14 presentations no CoV solves at budget 10,000 are untouched.** They contribute no rank correlation (constant cost column) and are excluded from every ρ above, which is why the medians are over 52 and not 66.
- **Grouping is by Aut-orbit, never `pres_id`.** The 66 rows hold 51 distinct orbits; a `pres_id` split would train on a presentation's own relabelled twin. All model numbers are 8-fold `GroupKFold` over `aut_canon_orig`. The abelian-mass rule is untrained, so it cannot leak at all — which is part of why it is the more trustworthy number.
- **`max_relator_length_cap` varies per CoV row** (it is sized to fit the transformed relators), so cross-row node counts are not strictly like-for-like. The cap is in the feature set and the model does not lean on it; the abelian-mass rule never sees it.

## Files

| | |
|---|---|
| `rank_b{100,1000,10000}.json` | full per-presentation results, per picker |
| `simpson.png` | pooled vs per-presentation — why the pooled reading is wrong |
| `abelian_mass.png` | solve rate and cost against abelian mass |
| `picker.png` | what one / three / five starts cost, per picker |

Reproduce:

```
.venv/bin/python3 experiments/stable_ac/cov/ml/cov_rank.py --out results/stable_ac/cov/ml/rank_b10000.json
.venv/bin/python3 experiments/stable_ac/cov/ml/cov_figures.py
```
