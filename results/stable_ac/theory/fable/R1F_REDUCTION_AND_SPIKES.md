# R1f — Free reduction can CREATE thickenability: a counterexample, and what it costs

STATUS: VERIFIED COUNTEREXAMPLE (machine-checked twice, by two independent tools) +
one sharp OPEN question. Claims addressed: MACHINERY. Nothing here is an AC-triviality
claim about AK(3) in either direction.

## The counterexample

Let move (0) be Lackenby's free/cyclic reduction, and call the inverse operation a
SPIKE: inserting a letter immediately followed by its inverse into a relator.

    reduced   P' = ("xyXY", "xxy")    gamma_N = 0   (SPHERICAL / orientably thickenable)
    spiked    P  = ("xyXY", "yYxxy")  gamma_N = 1   (NOT thickenable)

Verification (both directions, independently):
* census `gamma_N_factorial_n`: P' has 12 compatible rotations, histogram
  {0: 2, 2: 6, 4: 4}, minimum defect 0; P has 144, histogram {2: 26, 4: 94, 6: 24},
  minimum defect 2. (Defects are UNHALVED: gamma_N = defect/2.)
* the R1c-v2 solver decides P' SPHERICAL, and on P it fails CLOSED with
  "A-link has 1 loop edge(s); (H4) fails" — the loop is the spike's own corner, so the
  two tools agree exactly where each is in scope.
* `free_reduce("yYxxy") = "xxy"`, so P and P' are the same presentation, differing only
  in the spelling of one relator.

## What it kills

**The spike lemma is FALSE.** The natural conjecture

    thickenable(reduced)  =>  thickenable(spiked)                      [FALSE]

fails on the pair above. The geometric intuition behind it — "push a thin finger of the
attaching curve over the g-handle and back; the disc should follow" — does not survive:
the returning finger has to re-enter the page book of the g 1-handle, and the
B-reversal coupling at the two ends can force the extra pages to cross.

**Consequence for the moat programme.** The one-move picture of how gamma_N can change
is now: AC1 invert — invariant (GAMMA_N_SYMMETRY_LEMMA, AUDITED); AC3 conjugate then
reduce — invariant; AC4/AC5 — invariant (R1E Corollary Z, AUDITED); AC2 non-cancelling
graft — drops by at most 1 and that is TIGHT (R3PRIME_GRAFT_CALCULUS Thm G6, AUDITED);
AC2 CANCELLING graft — still unbounded. The hoped-for closure ("graft first, then argue
reduction is harmless") is exactly what this counterexample forbids, because reduction
is demonstrably not harmless: it moved gamma_N from 1 to 0 here. The gap is real and
must not be papered over.

**Consequence for what a negative verdict covers.** gamma_N is a property of the EXACT
word-realized complex. Two spellings of one presentation, related by a single move (0),
can sit on opposite sides of thickenability. So a NOT_SPHERICAL verdict on one exact
realization says nothing about the others without a further theorem — and the AC class,
which is closed under move (0), contains every spelling. Our harvests key and decide on
cyclically reduced forms; that is a CHOICE of representative, not a loss-free
normalisation, until the open question below is settled.

## The open question (under test)

    SPIKE MONOTONICITY:  gamma_N(spike(P))  >=  gamma_N(P)   for every single spike.

i.e. reduction never increases gamma_N, so the reduced spelling is the gamma_N-minimal
member of its spelling family. The counterexample above is consistent with this (it has
gamma_N going UP under spiking, 0 -> 1); the question is whether a spike can ever go
DOWN. A 68-case probe found none; a three-tier experiment (exhaustive at small size,
double spikes, and the real targets including AK(3) itself) is running.

Why it matters, concretely:
1. If TRUE, searching cyclically reduced representatives is WITHOUT LOSS OF GENERALITY,
   and every recorded NOT_SPHERICAL verdict extends for free to the infinite family of
   spiked spellings of that state — retroactively strengthening the whole corpus
   (~141,000 exact complexes) from single realizations to spelling families.
2. If TRUE, the 150 UNDECIDED rows of `gateway_neighborhood.json` — all of them
   loop-bearing exact graft images, where the solver fails closed and the census is
   astronomically over cap — are decided by their reductions, all of which came back
   NOT_SPHERICAL. The exhaustive one-move neighbourhood of AK(3)'s gateways would then
   be complete, not 78% complete.
3. If FALSE, the consequence is larger and more interesting: unreduced spellings would
   be a genuinely unexplored part of every AC class, reachable only through move (0)'s
   inverse, and every harvest ever run in this project (and, as far as we know, in the
   literature) would have been searching a strictly smaller space than the conjecture
   ranges over. A spiked spelling with gamma_N = 0 anywhere in AK(3)'s class would be a
   thickenable member and would decide the sub-goal.

Either answer is worth having, which is why the experiment is worth its budget.

## Data

Counterexample verified inline (both tools) at ~15:15 UTC; the systematic experiment
writes `results/stable_ac/fable/spike_monotonicity.json`. The gateway neighbourhood's
undecided rows are in `results/stable_ac/fable/gateway_neighborhood.json` with reason
strings naming the loop count.
