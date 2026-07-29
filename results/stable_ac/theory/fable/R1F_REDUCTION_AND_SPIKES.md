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

## ANSWER (experiment complete): monotonicity is REFUTED, and where it fails matters

Three tiers, 110,917 measured spiked complexes, all decided by exact census (the solver
cannot see loop-bearing complexes at all):

* **Tier 1, exhaustive at total length ≤ 9**: 3,511 canonical bases, 81,942 distinct
  single spikes. **424 counterexamples** — spikes that strictly LOWER gamma_N. Every one
  of them lies in the DEGENERATE stratum (some relator shorter than 3 letters, or a
  relator using only one generator). In the STRICT stratum (every relator ≥ 3 letters
  and using both generators): 736 bases, 18,156 spikes, **0 counterexamples**.
* **Tier 2, double spikes**: 28,786 measured, 40 counterexamples, again 0 in the strict
  stratum. Two spikes can raise gamma_N by 2, so the effect compounds upward.
* Effect distribution overall: gamma_N is unchanged by the overwhelming majority of
  spikes (104,610 of 110,917), raised by 5,652, lowered by 480.

So the naive conjecture is false, but the failures were confined to degenerate
presentations — exactly the ones the R1c-v2 solver already gates out, and not the
regime AK(3) lives in. That would have been a tidy ending.

**It is not the ending, because AK(3) itself breaks the strict-stratum pattern.**
Tier 3 measured the real targets, which sit at length 13 rather than ≤ 9:

| target | gamma_N | best single-spike gamma_N |
|---|---|---|
| **AK(3)** = ("xxxYYYY","xyxYXY") | **2** | **1** |
| AK(3) class member ("YXYxyx","YYYxxxx") | 2 | 1 |
| AK(2) = ("xxYYY","xyxYXY") | 1 | 1 |
| AK(3) gateway ("YYXXyx","YYYxyXX") | 1 | 1 |
| AK(3) gateway ("YYXXyx","YYxyXXX") | 1 | 1 |

AK(3) has relators of length 7 and 6, each using both generators — it is squarely in the
strict stratum, and a single spike drops its gamma_N from 2 to 1. The strict-stratum
cleanliness of tiers 1-2 is therefore a small-length artefact, not a law.

### The AK(3) row, independently re-verified — with named witnesses

The tier-3 row was originally a single measurement by the experiment's own exact census
(cap 20,000,000; 39 spikes, 0 skipped). It has now been re-established by a **different
tool and a different kind of certificate**, `experiments/stable_ac/fable/spike_witness.py`:

    a single explicit compatible rotation system of defect 2d is a WITNESS for
    gamma_N <= d, re-derived and re-checked in isolation by
    gateway_scan.verify_witness (which recomputes the defect from the dart data and
    re-checks the B-reversal compatibility law C_{tau v} = B C_v^-1 B).

An upper bound is exactly what the claim needs: AK(3) itself has gamma_N = 2 by exact
census (86,400 systems, pinned as a test fixture), so any spiked spelling with a
verified defect-2 witness is a STRICT DROP. The tool enumerates the 39 distinct single
spikes — independently reproducing the experiment's count of 39, having deduplicated on
a spelling key that quotients only by rotation, inversion and relator permutation, and
deliberately NOT by free reduction — and hill-climbs each for a witness (80,000
evaluations per state, seed 20260729).

**Eight of the 39 carry a verified defect-2 rotation system.** They are, verbatim:

| # | spiked spelling | verified defect | bound |
|---|---|---|---|
| 7 | ("xyYxxYYYY", "xyxYXY") | 2 | gamma_N <= 1 |
| 8 | ("xxYyxYYYY", "xyxYXY") | 2 | gamma_N <= 1 |
| 14 | ("xxxYXxYYY", "xyxYXY") | 2 | gamma_N <= 1 |
| 16 | ("xxxYxXYYY", "xyxYXY") | 2 | gamma_N <= 1 |
| 20 | ("xxxYYYXxY", "xyxYXY") | 2 | gamma_N <= 1 |
| 21 | ("xxxYYYxXY", "xyxYXY") | 2 | gamma_N <= 1 |
| 27 | ("xxxYYYY", "xxXyxYXY") | 2 | gamma_N <= 1 |
| 29 | ("xxxYYYY", "xyXxxYXY") | 2 | gamma_N <= 1 |

The other 31 returned defect 4 (bound gamma_N <= 2), which is silence, not a value.
Full data: `results/stable_ac/fable/spike_witness.json`.

So the strict-stratum break is CONFIRMED, and by eight independent witnesses rather
than one: AK(3) sits at spelling distance 1 from gateway level in eight different ways,
six of them in the first relator and two in the second.

### Exact values, and the gamma_N = 0 question closed for single spikes

The witnesses bound gamma_N from ABOVE only, which is the whole of the strict-drop
claim but does not distinguish gamma_N = 1 from gamma_N = 0 — and gamma_N = 0 would be a
THICKENABLE spelling of AK(3), the outcome that decides the sub-goal. That gap is now
closed by exhaustive census, at cap 20,000,000 with 100% coverage, run independently of
the witness hunt and re-verified through the audited `gamma_N_factorial_n`:

**every one of the eight has minimum defect exactly 2, i.e. gamma_N = 1 exactly**, with
precisely 2 minimising rotation systems out of 3,628,800 (six of them) or 4,838,400
(two of them). **No single spike of AK(3) is thickenable.** The 39 spiked spellings
split as gamma_N histogram {1: 8, 2: 31}.

The two runs are a genuine cross-check, not one measurement counted twice: they use
different search strategies (exhaustive census versus hill-climbed witness), different
engines (a numba census kernel cross-validated 844 times against the audited pure-Python
census inside its own tier-1 run, 0 disagreements, versus the pure-Python rotation
verifier), and different deduplication code — yet they independently produce the SAME
count of 39 distinct spikes and the SAME set of 8 minimisers, spelling for spelling.

The tightness is worth recording: 2 minimising systems in 3.6 million is a needle the
uniform sampler of an earlier session could never have found, and is why the hunt for
gamma_N = 0 at greater lengths must use witnesses rather than censuses (see R7).

### The eight are the ceiling being attained, not a lucky find

[ADDED after adversarial audit; the derivation is being written up and audited as the
SPIKE CEILING in `R7_SPELLING_SPACE.md`, and until that audit returns the statement here
is a CONJECTURE with a proof sketch, not a theorem.]

A spike is one edge-deletion plus three edge-insertions in the ribbon graph, so the graft
calculus's own machinery (Lemma G2's restriction map, Lemma G4's boundary-circle case
analysis, Theorem G5's canonical interpolation) should give

    gamma_N(spike(P)) >= gamma_N(P) - 1,   hence   gamma_N(spike^k(P)) >= gamma_N(P) - k.

If that holds then, since gamma_N(AK(3)) = 2, **no single spike of AK(3) can be
thickenable** — which is exactly what the exhaustive census found, and the eight
minimisers at gamma_N = 1 are the bound being attained rather than a discovery. The
scope condition that must be checked rather than assumed: G6's stated domain in
`R3PRIME_GRAFT_CALCULUS.md` requires both words cyclically reduced and the seam
non-cancelling, and spiked spellings are by construction neither.

The corresponding empirical prior, from the 110,917 measured spiked complexes: all 464
observed strict drops are 2 -> 1, **not one reaches 0**; the 2,514 bases at gamma_N = 1
produced no thickenable spike in ~58,000 attempts; and every one of the 13,976 spiked
complexes at gamma_N = 0 descends from a base already at gamma_N = 0. So across the whole
corpus, "spiked thickenable => reduced thickenable" holds with zero counterexamples,
while the converse is refuted by the counterexample at the top of this document. If that
implication can be PROVED, the spelling-space route closes completely — and that is a
clean negative result worth having.

## What this changes

1. **Reduced-form search is NOT without loss of generality.** Every harvest in this
   project — and, as far as the literature review found, every published AC search —
   normalises to cyclically reduced words. But move (0) is an AC move, so the class
   contains every spelling, and here the unreduced spellings are strictly CLOSER to
   thickenable than the reduced one: gamma_N = 1 versus 2. The reduced representative is
   not the best representative.
2. **AK(3) reaches gateway level at spelling distance 1 — but it is NOT free.**
   [CORRECTED after adversarial audit. The original text here read "it costs nothing to
   reach", and that is wrong in the only sense that matters.] R1g established that
   gamma_N = 1 states are the only ones from which a single graft can reach a thickenable
   presentation, and that they are rare (1 in 2,500 sampled class members). AK(3) has
   eight at spelling distance 1. But a spike consumes exactly the same one unit of
   ceiling budget as a graft does (see the spike ceiling below): the spiked states are
   NEW states, not CHEAPER states. Reaching gamma_N = 1 by spelling buys a different
   launchpad, not a discount.
3. **The 150 undecided rows of `gateway_neighborhood.json` cannot be waved away.** They
   are loop-bearing spellings, and this result says loop-bearing spellings can be
   genuinely better than their reductions — so their verdicts must be computed, not
   inherited.
4. The cancelling-graft gap in the graft calculus stays open, and is now known to be a
   real phenomenon rather than a technicality: reduction moves gamma_N in both
   directions, and neither direction is bounded by anything proved so far.

Actionable: run the harvest over SPIKED spellings of AK(3) and of its gamma_N = 1
gateways — a search space nobody has entered, entered from states one rung below where
every previous search started.

## The original open question (now answered above)

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
