# Stable-AC learnings — nulls, refutations, retractions

The stable-AC program's code and proofs stay on their branches (this collection ships no
proof work). What is worth carrying is the conclusions: each entry below closed a
direction, and a closed direction not written down gets reopened by accident.

## covmeet: a verified null (`origin/experiments/ppo`, later commits)

`covmeet` pools the `Aut`-minimised outputs of every valid change of variables from each
of the 124 unsolved classes into one store; a collision between two classes would prove
them stably AC-equivalent. Final audited state: **14,627,414 orbits, 9,336,325 expanded,
0 merges** — audited as a null (300/300 sampled orbits are aut-min fixed points, 25 chains
replayed, the 124-class count re-derived from masks). Census along the way: a median state
has 65 raw CoVs, only **6** non-automorphic. The orbit-memo speedup it produced is in
[`speedups.md`](speedups.md).

## The drop-floor refutation (`origin/claude/ac-stable-ac-conjecture-ijfzgz`)

A deep dive on whether AK(3) could be certified a stable-AC counterexample via a
planarity/sphere-decision invariant (γ_N), spike calculus, and meet-in-the-middle search.
The branch's final commit is a self-correction: the claimed pointwise drop floor is
**refuted** and the equivalence built on it withdrawn; a weaker "spike ceiling" survives.
~17,100 certified non-thickenable realizations, zero positive witnesses. No proof either
way — and a model of writing the retraction into the record.

## S24: an uninformative null (`origin/claude/stable-ac-conjecture-stabilization-rwo9as`)

Launching AC2 moves from AK(3)'s 527 γ_N=1 states found zero γ_N=0 hits — but the
session's own null-model control also scored 0/18 on a class *known* to contain a γ_N=0
member. The negative result therefore says nothing about the conjecture; the bottleneck
was the decider's budget ceiling. Recorded precisely because "we found nothing" and "the
instrument couldn't have found anything" look identical until you run the control.

## The abelianized ranking key (`origin/research/w5/stable-ac-escape`)

Search-free CoV ranking by abelianized magnitude, validated at scale: 640/640 rank-1
solves at budget 100k (vs 633/640 plain baseline) — but only economical **paired with
early-stop-on-success** (+232% cost without it, −8.3% with). The same key is what the
top-3 CoV result in [`heuristic-search.md`](heuristic-search.md) is built on.

## The Shehper rescission and canonical form F (`origin/test/stable-ac-moves`)

Shehper et al.'s 2024 claim that AK(3) is stably AC-trivial was **rescinded in their v2**
(a misprinted Wirtinger presentation) — the reason this whole research line exists. The
branch's own 12-hour proof attempt also failed, flooring at total length 13 across five
method families, but found a new canonical form **F**: a 71%-dominant attractor with a
certified 21-move path F → AK(3). The branch also carries the ICML paper source.

## The d-o-t split (`origin/test/eda`)

Not proof work: a frozen 38,384-row train/val/test split (`dot_splits_v2.npz`) for a
distance-of-trivialization regressor, with anchor/cousin leakage controls. Feeds any
future value-function line; out of scope for this collection.

## Ongoing, no claims (`origin/codex/proofs`)

An active formal-algebra track reducing an infinite periodicity claim (a crossed-derivative
recurrence tied to an AK(3)-adjacent evaluator) to a finite verification window, with
two-auditor discipline per step. Every commit disclaims any lift/AK3/stable-AC/AC claim.
Deliberately not ported — this branch collects results, and there is no result yet.
