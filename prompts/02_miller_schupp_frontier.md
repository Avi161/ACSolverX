# Prompt 02 — The Miller–Schupp frontier: trivialize the 124, or isolate a hard candidate

> **Read [`00_operating_contract.md`](00_operating_contract.md) first and adopt it in full.** This prompt adds the Miller–Schupp–specific content. Have your plan reviewed by `ac-advisor` before implementing.

## The target, precisely

The **Miller–Schupp family** is

```
MS(n, w) = ⟨ x, y | x⁻¹yⁿx·y⁻⁽ⁿ⁺¹⁾,  x⁻¹w ⟩,   n ∈ {1,…,7},  w one of 170 zero-x-exponent words,
```

which produces exactly the **1190** canonical pairs of `data/1190MS.txt` (this is the confirmed construction — three other plausible conventions do *not* reproduce the file; verified in `experiments/equivalence_classes/phases/phase0_provenance.py`). It is the community benchmark for AC search.

**The frontier, as a reduction chain** (all in `results/equivalence_classes/EQUIVALENCE_FINDING.md`, verified by `experiments/equivalence_classes/verify/verify_proofs.py`):

- Of the 1190 cells, **640 are trivial** (they collapse to only **113** distinct Aut(F₂)-orbits — 5.7× redundant) and **550 are unsolved**.
- The 550 unsolved cells carry **261 distinct representatives** (an upstream AC-reduction grouped cells bottoming out at the same short presentation).
- **261 → 168** distinct problems under exact Aut(F₂) change-of-variables (Whitehead's algorithm). **This is a wall — no change of variables can reduce it further.**
- **168 → 124** under **ACA** (AC moves *and* change of variables together), via 137 machine-checked edges. This is an **upper bound only**: the search is sound (every merge certified) but incomplete, and there is **no lower bound** — all 261 present the trivial group, so if AC is true they are a *single* class. Say "124 distinct problems," never "124 AC-classes."

Run the verifier once yourself and confirm it prints `ALL 137 EDGES VERIFY. The 261 presentations are 124 distinct problems.` before trusting any of these numbers. The exact presentations live in `data/ms_unsolved_reps/` (`aca_124.csv`, `ms_reps_unsolved.txt`) and `results/equivalence_classes/PROOFS.md`.

## What a complete result looks like — and the honest ceiling

- **What would actually settle the 261:** exhibit a verified trivialization for one representative of each of the 124 classes. **Today that count is 0 of 124** — at a million nodes per presentation, not one has been trivialized. Every class you trivialize (stably or unstably, independently replayed) is real, publishable progress. Label each certificate AC-trivial vs stably-AC-trivial.
- **A verified merge** lowers the 124 upper bound. A merge proves two presentations are *the same problem*; it never certifies they are *different*. The count has moved 126 → 125 → 124 by exactly this route, each step a certified edge — and the levers that moved it are not exhausted (below).
- **A counterexample** would require an **ACA-invariant with ≥ 2 values** — which does not exist and whose construction would *disprove* AC. Every cheap invariant is already known blind here: `|det| = 1` for all 261, and `|Hom(G,H)| = 1` for every finite `H` tested (S₃, D₄, Q₈, A₄, S₄, SL(2,3), A₅, S₅). The provable floor is 1. Do not hunt for a counterexample by "the search can't solve these" — that is the search-failure fallacy (contract Red Line 3).

## The hardest residual — where to point the search

- **The 9 singleton classes** (no merge found by any sweep — individually the hardest to reduce): classes 116–124 in `PROOFS.md`, names `13_1, 15_1, 16_1, 14_1, 14_2, 16_2, 16_3, 18_2, 20_2`, lengths 13–20. **`13_1` (class 116) is Aut(F₂)-equivalent to AK(3)** — route it to [`01_ak3.md`](01_ak3.md), not here. Pull the exact relator strings from `data/ms_unsolved_reps/` / `PROOFS.md`; do not trust a transcription.
- **The abelianized-magnitude-2 MS family** (6 reps, `r1 = YXXXyxx`, `r2 = YⁿXyⁿx`, n = 2..7) — flagged in `IDEAS.md` as a good place to start the residual sweep because they share structure.
- **The length-21 hump** — the two newest merges (`21_3≡21_29` and `21_7≡21_28`, four reps between them) both meet at Aut-minimal length **30**, well above the cap-28 search space. This is why "converged at cap 28" was wrong, and why a bigger cap keeps finding merges.

## The levers (with measured first results)

Grounded in `experiments/IDEAS.md`, `experiments/IMPLEMENTATION_IDEAS.md`, `experiments/heuristic_search/`, and `results/stable_ac/`. These help the *124 residual* specifically (they are near-inert on AK(3)):

1. **Productionized CoV-restart portfolio (the lead recommendation).** Race change-of-variables restarts, ranked by a cheap key. Mechanism validated on the known-trivial ladder: best strategy 16/22 vs baseline 10/22 at budget 1000, one case solved in 39 nodes vs a 574k-node baseline optimum. Best ranker found: the lexicographic key `(abel_magnitude, total_length, max_relator)` (`cov_abel_len_lex`). **Caveat that must travel with every number:** ladder cases are known-AC-trivial — cracking them validates the *mechanism*, not a 124 solve. The open, load-bearing test is to run this at production budget *on the 124*, which nobody has done.
2. **Per-relator cap-fit pre-filter** — ship-ready, trivial cost, mathematically proven (`STABLE_AC_NEW.tex`, checked 13,712 relator-checks / 0 violations). Turns the proven length-change bound into an arithmetic reject filter that cheapens every CoV lever above.
3. **Iterated / multi-hop CoV restart tree** — reachable Aut-orbits grow ~geometrically with hop depth (no saturation through 3 hops); single-hop CoV under-explores by an order of magnitude. Target `n_subs ≥ 2` CoVs (the only ones that leave the input's orbit — `PROOFS.tex` Thm 1).
4. **Same-orbit automorphic re-seed** — a genuinely distinct coverage mechanism: a *same-orbit* re-seed (not a new orbit, not a bare relabel) solved in 39 nodes what the baseline missed — relabels alone give **zero** new coverage but same-orbit re-seeds do. New, evidence-backed (the ms634 finding).
5. **Stall-triggered Lemma-11 CoV escape** — apply a stable-move CoV when the length-guided search plateaus, resume in new coordinates. Shipped (`stall_escape.py`): beats plain greedy at matched total budget, **12/22 vs 10/22, 0 losses** on `combined_22`. This is the closest lever to the project's core mission (crossing the Two-Hump valley via a genuine stable supermove). A CoV solve certifies **stable** triviality only.
6. **Knot/block heap ordering (the shape heuristic — a *ranking* signal, never an obstruction).** The baseline greedy orders its open set by total relator length alone. Replacing that single priority with a tuned blend of knot/block features improves solve rate at fixed budget: **17→30/60 at budget 100, 29→43/60 at budget 1000** (`experiments/heuristic_search/`, `results/heuristic_search/`), never losing a presentation, margin growing with budget — budget-100 tuned (30) beats budget-1000 baseline (29). The features come from the separate clustering analysis (`experiments/clustering/`, `results/clustering/`): the strongest *classifier* of solved-vs-unsolved is `smaller mean block` (the thinner generator's mean run length; AUC 0.912, rule `> 1.25` in `results/clustering/signal_ranking.json`), and `max_knots ≥ 4` / `min_knots ≥ 3` each flag 14/124 unsolved with zero false positives (`results/clustering/`). **Use these only to order the search and to prioritize candidate targets — "unsolved cluster" is never a counterexample; shape-predicts-solvability is an empirical regularity about search difficulty (and only "unsolved at the budgets tried"), not an AC-invariant** (this is the search-failure fallacy in ML clothing).
7. **A bigger Aut-minimal length cap** — the one lever *confirmed twice* to lower the count (cap 34 broke 126→125; caps 30–36 broke 125→124). Untried now: **caps 38–40 at real depth** and **more RAM** (state/RSS limits ended 3 of 5 overnight arms before exhaustion, not budget). Search on the ACA graph keyed by Whitehead canonical form; never key on the cheap peak-reduced form (not confluent — splits 168 into 259).

## Your first three moves

1. **Verify the frontier against source.** Run `experiments/equivalence_classes/verify/verify_proofs.py` and confirm `ALL 137 EDGES VERIFY`. Read `EQUIVALENCE_FINDING.md` and skim `PROOFS.md`. Confirm the 640/550, 261, 168, 124 numbers for yourself and note that 124 is an *upper bound*.
2. **Choose: trivialize or reduce.** For *trivializing*, the highest-EV first build is the **production CoV-restart portfolio (lever 1) plus the cap-fit pre-filter (lever 2) and the knot/block ordering (lever 6)**, pointed at the 124 residual — prepare and validate locally at ≤1000 nodes, hand the production budget off. For *reducing the count*, the highest-EV lever is a **bigger Aut-minimal cap (38–40) with more RAM (lever 7)** — the only lever with a track record of moving the number.
3. **Gate, build, verify, report.** Run `ac-advisor` on the concrete plan; reconcile every REVISE/BLOCK. New files only. Verify every solved row by independent replay (`verify_results.py`) and every merge by `verify_proofs.py`. Report per the contract: which classes were trivialized (labelled AC vs stable), whether the 124 count moved by a *verified* edge, and every negative stated as bounded ("unsolved within budget/cap B"), never as a counterexample.
