# R1g — The gamma_N landscape of AK(3)'s classical class, and a distance corollary

STATUS: MEASUREMENT + one corollary that follows from AUDITED machinery. Claims
addressed: the classical claim (AK(3) AC-trivial?) via the R1 transfer; nothing here
is a proof in either direction. Every number below is reproducible from committed
artifacts.

## Why measure gamma_N rather than just "is it 0?"

Every verdict this project has recorded is binary: SPHERICAL (gamma_N = 0, thickenable)
or not. That discards the quantity that actually orders the search. By the AUDITED
ceiling (`R3PRIME_GRAFT_CALCULUS.md` Thm G6) a non-cancelling AC2 graft lowers gamma_N
by at most 1, and gamma_N is invariant under AC1, AC3-then-reduce, and AC4/AC5
(`GAMMA_N_SYMMETRY_LEMMA.md`, `R1E` Corollary Z — both AUDITED). So gamma_N is a
*graded* obstruction: a member at gamma_N = k is k rungs below the target, and the
gamma_N = 1 members are the only states from which a single graft can possibly land on
a thickenable presentation.

## The instrument

Exact censuses die at total length 14 (`prod (deg-1)!` exceeds every affordable cap).
`gateway_scan.py` gets the number anyway, by combining two tools that certify opposite
sides:

* the R1c-v2 solver has already certified every harvest member NOT_SPHERICAL —
  exhaustive, not sampled — giving **gamma_N >= 1**;
* a hill-climbed compatible rotation with defect 2, re-verified exactly, gives
  **gamma_N <= 1**.

Together: gamma_N = 1, certified, with no census. Calibration: the climber recovers the
exact gamma_N of four known targets in ~0.1 s each, including a needle of exactly 2
minimising rotations out of 86,400 (the length-13 state `("YYXXyx","YYxyXXX")`, whose
census histogram is {2: 2, 4: 702, 6: 14932, 8: 55132, 10: 15632}). Sampling can only
UNDER-report gateways, so all gateway counts below are honest lower bounds.

## What the class looks like

Sample: 2,500 of the 124,296 members of `ak3_matched_members.jsonl.gz`, 8,000 rotation
evaluations each (~20 million rotation systems in total).

    gamma_hat:   1 -> 1     2 -> 63     3 -> 316    4 -> 932
                 5 -> 814   6 -> 355    7 -> 19

**Read the direction of this inequality carefully.** gamma_hat is an UPPER bound:
gamma_N <= gamma_hat, because a witness proves the minimum is no worse than what was
found. It is NOT evidence that the class sits high — a member reported at gamma_hat = 5
could have gamma_N = 1 with the climber simply failing to find the rare minimiser. The
climber is exact on every calibration target (all six length-13 members, AK(3), and the
2-in-86,400 needle), but its accuracy at length 20+ — where the compatible family is
~10^10 and the sample is 8,000 — is UNVERIFIED. Since a weaker search reports higher
values, the apparent growth of gamma_hat with length is exactly what climber degradation
would also produce, and the two explanations are not separated by this experiment.
Calibrating the climber against exact censuses at lengths 14-15 (the largest still
affordable) is the missing control and is recorded as the next step.

What IS certified: of the six length-13 members the harvest found, exact censuses give
four at gamma_N = 1 and two at gamma_N = 2 (AK(3) itself is one of the latter); and one
further gateway at length 14, `("YYYXXyx","YXYXyxx")`, gamma_N = 1 exactly (solver
NOT_SPHERICAL gives >= 1, verified witness gives <= 1). Gateways are rare in the sample —
1 in 2,500 — but that rarity is a lower bound on their true density, not a measurement
of it.

**Corpus cross-validation (free, and worth recording).** Those ~20 million sampled
rotation systems produced **zero** defect-0 witnesses — no sampled rotation ever
contradicted a solver verdict. That is an independent check of the NOT_SPHERICAL corpus
by a method with nothing in common with the decision procedure: random search over
rotation systems versus an exhaustive combinatorial solver.

## Corollary (distance), with its gap stated

**Corollary.** Let P have gamma_N(P) = k. Then any AC path from P to a thickenable
presentation that uses only relator inversion (AC1), conjugation (AC3), stabilisation
and destabilisation (AC4/AC5), and NON-CANCELLING AC2 grafts has length at least k.

*Proof.* The first four move types leave gamma_N unchanged (symmetry lemma; Corollary
Z); each non-cancelling graft lowers it by at most 1 (Thm G6); the target has
gamma_N = 0. []

Applying it requires a LOWER bound on gamma_N, which only the exhaustive tools supply:
the solver's NOT_SPHERICAL gives gamma_N >= 1 for every member (hence distance >= 1
class-wide), and an exact census gives the exact value. So the certified statements are:
**AK(3) is at distance >= 2** (census: gamma_N = 2), each length-13 gateway at distance
>= 1, and no further. The gamma_hat histogram does NOT license "a typical member is at
distance >= 4" — that would read an upper bound as a lower one. Separately, and
exhaustively rather than statistically: the one-move neighbourhoods of AK(3) and of all
four length-13 gateways contain no thickenable member
(`gateway_neighborhood.json`: 420/420 reduced images NOT_SPHERICAL; the 150 undecided
rows are exactly the loop-bearing unreduced images, which R1f's open question would
settle).

**The gap, stated plainly.** The corollary excludes cancelling grafts, and it must:
`R1F_REDUCTION_AND_SPIKES.md` exhibits a verified case where free reduction — move (0),
the reduction half of a cancelling graft — takes gamma_N from 1 to 0 by itself. So no
distance claim covering cancelling grafts is available, and none is made here. Whether
the drop is bounded at all is exactly the open SPIKE MONOTONICITY question of R1f.

## Reading, honestly

Two things are established and one tempting thing is not. Established: the bottom of the
class (length 13-14) is fully measured and contains gateways at gamma_N = 1 but nothing
at 0; and the exhaustive one-move neighbourhoods of those gateways are clean. NOT
established: that the rest of the class is far from thickenable — the gamma_hat
histogram is an upper-bound landscape and cannot support that reading, however much its
shape invites it. Anyone continuing this line should resist exactly that inference until
the climber is calibrated at length 14-15 against exact censuses.

And even a genuinely distant class would not settle anything: gamma_N is not an AC
invariant (the codex 0->1 counterexample; the tight graft witness `("yyxYxy","yx")`
dropping 1 -> 0), so a hit can sit beyond any searched corridor, and what is measured
here is one corridor of an infinite class.

Concrete consequence for the search, which is the actionable part: **rank candidates by
gamma_hat ascending, not by length or by E**. The gateway states are where a hit can
come from, they are rare (1 in 2,500 sampled), and no harvest to date has used this
signal — `gateway_scan.py` computes it in ~0.1 s per state at any length.

## Artifacts

`results/stable_ac/fable/gamma_floor_measurement.json` (exact censuses, per-stratum
coverage), `results/stable_ac/fable/gateway_scan.json` (gamma_hat landscape + certified
gateways with witness rotations), `results/stable_ac/fable/gateway_neighborhood.json`
(exhaustive one-move neighbourhoods). Instruments: `gamma_floor.py`, `gateway_scan.py`,
`gateway_neighborhood.py`.
