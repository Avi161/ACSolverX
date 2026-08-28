# Fable lane lessons

## 2026-08-28

### Grep the hypothesis before building the instrument

[TRAP] W1 built a complete finite-orbit decision procedure whose refutation
branch was mathematically unreachable: with the base rows killed, both
kill-word images normally generate the image (both triples present the
trivial group), and a 5-line chain then forces connectivity in ANY group.
The repo's `cited-theorem-hypothesis-never-fires` lesson, violated verbatim
— the hypothesis an obstruction needs (distinct normal closures) fires on
0 of 180 A5 homs.

[WORKS] Before designing any invariant-based test, compute the invariant's
value on both endpoints BY HAND first (here: normal closure = everything on
both sides, 2 minutes), and only build machinery if they can differ.

### Check for decidability theorems before running decision computations

[TRAP] The A5/S5/PSL(2,7)/A6 sweeps re-derived, group by group, a corollary
of Borovik–Lubotzky–Myasnikov 2005 Thm 1.1 (finite AC-graph components =
abelianization preimages), which settles every finite group at once and was
citable in the first hour.

[WORKS] For any "does this finite structure obstruct" question, do the
literature pass FIRST and treat computation as validation of the cited
theorem, not as the source of truth.

### A positive control must be able to fail

[TRAP] W1's control (certified-trivial triple's image orbit contains the
trivializer) was itself forced by the same vacuity, so it could not have
detected a wrong move model.

[WORKS] Pair every positive control with an adversarial control — a
deliberately broken variant (e.g. a move set missing `mult`) asserted to
FAIL — before reading any result.

### Block on the advisor gate, don't race it

[TRAP] The W1 checker was implemented, run, and committed while the
ac-advisor review was still in flight; the review returned BLOCK and the
committed note needed a retraction pass.

[WORKS] For each new workstream: write the plan, get the advisor verdict,
reconcile, then implement. Concurrency is for independent derivation and
literature agents, not for the gate itself.

### Secondary literature on AK(3) stable status is actively wrong

[TRAP] 2025–26 print (Lisitsa arXiv:2501.18601 abstract; arXiv:2607.23611)
asserts AK(3) is stably AC-trivial; the claim delegates to the MMS02 chain
voided by the misprint found in Shehper et al. arXiv:2408.15332 v2 App. F.

[WORKS] AK(3) stable AC status is OPEN. Cite Shehper et al. for the
misprint; trust the repo's own `ac-advisor.md` record over search-engine
summaries; verify any "settled" claim against the primary chain.

### A descending greedy profile can be a disguised self-loop

[TRAP] The Tpub preflight's 29 -> 14 descent was pitched as making a
production run "genuinely promising"; Tietze-collapsing the floor state and
aut_canon-ing the result showed the floor IS AK(3) itself (plus one z
letter) — the search had looped back to the original problem.

[WORKS] Before selling any descent profile on a stabilized/transformed
start, eliminate the auxiliary generator at the floor state and aut_canon
the residue; if it lands in the source orbit, the descent is a self-loop
and the route's difficulty equals the source's.

### Ask what a SUCCESSFUL separation would prove, before hunting invariants

[TRAP] W5 opened as "find an invariant separating the MMS02 bridge triples".
A five-lemma reduction (basis change + z-elimination + the certified rank-2
replays) then showed the bridge is EQUIVALENT to "AK(3) is AC-trivial after
exactly one stabilization" — so any separating invariant is a partial negative
resolution of the headline open problem. The hunt was never a shortcut, and
every null it produces is the expected behaviour of a cheap invariant on a hard
question, not evidence.

[WORKS] Before building an invariant battery, spend the first hour reducing
the two endpoints to canonical form. If the reduction lands on a known open
statement, say so and re-aim; if a probe then *does* separate, treat it as a
red flag on the probe, not as a discovery.

### A constructive connectivity method needs its positive control at every parameter

[TRAP] The free-nilpotent chain construction succeeded at class 2, failed at
class 3 with row-local gadgets, and fails at class 4 today. Each failure looks
like "the quotient might separate the bridge" and is nothing of the kind: the
certified-AC-trivial triple's own control failed in exactly the same runs, i.e.
the gadget pool was too small. Class 3 was fixed by adding a cross-row
`transfer` gadget (row-local corrections span only rank 6 of the 8-dimensional
degree-3 Lie layer).

[WORKS] Run the positive control at EVERY parameter value, and have the
checker withhold the verdict automatically when the control fails, rather than
printing a null the reader has to discount by hand.
