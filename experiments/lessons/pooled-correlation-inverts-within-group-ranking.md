# [2026-08-04] Score a within-group ranking task within the group — pooling inverts which feature wins [TRAP]

## What happened

The CoV sweeps hold ~100 candidate changes of variables per presentation, and the deployable question is which one to run first. The first look at the data was a pooled correlation over all 6,722 rows against log cost:

```
r(log cost, total relator length) = +0.459
r(log cost, abelian mass)         = +0.109
```

Read literally that says: pick the z that gives the shortest relators, and ignore the abelianisation. Both halves are wrong. Scored inside each presentation — which is where the choice is actually made, against that presentation's own candidates — the ordering reverses:

```
median Spearman rho vs cost, over the 52 presentations some CoV solves
  abelian mass          +0.809   (positive on 52 / 52)
  total relator length  +0.356
```

Sorting a presentation's candidates by ascending abelian mass and running the **three** cheapest solves **52/66 — the exact set the full oracle sweep solves** — at 3 searches instead of ~109. Running one gets 47.4/66; shortest-result, running one, gets 47/66.

### A second trap in the same analysis: the tie-break

Running *one* lowest-mass candidate was first reported as **52/66**. That was wrong. Abelian mass is a small integer, a median of **6** candidates tie at each presentation's minimum, and a stable `argsort` was silently breaking those ties by the sweep's file order — so the number scored the input file's ordering, not the rule. With random tie-breaks averaged over 200 draws: 47.4/66 (27 worst case, 52 best case; 25 of 66 presentations have a *mixed* tied group where some tied candidates solve and some do not).

**Rule: a ranking evaluation must randomise ties and average, or it reports the arbitrary order its input happened to arrive in.** A fractional solve count is the honest signature of a rule that shortlists rather than picks — if the count comes out a clean integer, check that the score actually has no ties before believing it.

## Root cause

Simpson's paradox. The 66 presentations differ by orders of magnitude in baseline difficulty, so a hard presentation's *best* CoV routinely costs more than an easy presentation's *worst*. Pooling puts all of that between-presentation variance into the denominator: it measures "does this feature identify an easy presentation", not "does this feature order one presentation's options". Relator length correlates with which presentation you are looking at, so it wins the pooled contest and loses the real one.

The reversal reproduces at every budget (100 / 1,000 / 10,000), so it is structural, not noise.

## Why the winning feature is the right one

For pair ⟨r₁, r₂⟩ the exponent-sum matrix M = [[Σx(r₁), Σy(r₁)], [Σx(r₂), Σy(r₂)]] has |det M| = 1 on every row here (presentations of the trivial group). AC moves act on M by row operations and the target ⟨x, y⟩ has M = ±I, i.e. |Σ| summing to 2. Abelian mass is therefore how far the abelianisation still has to travel, and — unlike length — a substitution cannot fake it by inflating words. It shows up split cleanly:

- picks solvers from non-solvers within a presentation at median AUC 0.922
- among solved rows only, ranks **path length** at ρ +0.83 (nodes +0.81; length manages +0.25)

A gradient-boosted model over 81 features, GroupKFold'd over Aut-orbits, independently lands on it: permutation importance `d_exp_l1` +0.478, next feature +0.043.

## Rule

**When the decision is made inside a group, compute the statistic inside the group and aggregate afterwards — never pool first.** A pooled correlation answers "which group is this", which is a different question and can rank features in the opposite order. Concretely, before believing any feature ranking on this data: state whether the consumer of the number chooses *between* presentations or *within* one, and match the estimator to it.

Corollary already paid for elsewhere in this repo: the same defect shape as scoring one run's arm against another run's denominator (`compare-on-the-same-denominator.md`) — a number computed over the wrong population reads as skill.

Evidence: [`results/stable_ac/cov/ml/COV_QUALITY.md`](COV_QUALITY.md), `simpson.png`, `rank_b{100,1000,10000}.json`. Code: [`experiments/stable_ac/cov/ml/`](../stable_ac/cov/ml/).
