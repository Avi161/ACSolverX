# Calibrate one-sided witness hunts on a known-positive ladder before reading nulls

**Trap.** A one-sided instrument (e.g. `sampled_min_defect` hunting defect-0
rotation systems) emits the same output — silence — whether the witness is absent or
merely beyond the budget.  A null from such a hunt at budget B and length L is
meaningless until the detection rate of budget B on states KNOWN to carry a witness
at length L has been measured.  We nearly over-read two large nulls (150 states at
lengths 19-20 x 120k evals; 1,759 states up to length 24 x 40k evals) before
calibrating.

**Method that worked** (`experiments/stable_ac/fable/witness_sensitivity.py`,
artifact `results/stable_ac/fable/witness_sensitivity.json`): grow a ladder of
gamma_N = 0 states by spikes/grafts from a census-confirmed fixture, certifying
every rung by exact census while `prod_g (deg(g)-1)!` is affordable and by an
independently re-verified defect-0 witness beyond that; then replay the production
budgets on each rung with >= 10 independent seeds per cell.

**Measured cliff (2026-07-29 run).** Detection at 40k evals: 100% through L16, 70%
at L17, 40% at L18, 20% at L19, 0/10 from L21 on.  At 120k: 40% (L19), 20% (L20),
0-10% (L21-22).  At 200k: 60% (L19) falling to 10% (L22).  Ladder growth itself
stalled at L23/L24 — 2M-eval climbs certified NO gamma-0 child of either L21/L22
tip (best defect found: 2).  So production-budget hunts are blind above total
length ~20, and even 2M-eval certification fails by ~L23 on this ladder.

**Two bias directions to record every time** (extends
`parallel-runs-and-bound-direction.md`):

1. the sampler bounds gamma_N from ABOVE — silence never proves gamma_N > 0;
2. the calibration ladder bounds sensitivity from ABOVE — rungs are by construction
   states the climber COULD certify, so real states at the same length can only be
   harder.  A low cell is conclusive (null = vacuous); a high cell is optimistic,
   never a licence to read a null as evidence of absence.

**Practical rule.** Before running (or citing) any witness hunt above the last
calibrated length, extend the ladder first; if the ladder itself cannot be extended
at budget B, no hunt at budget <= B at that length can support any conclusion, and
its cost should be redirected.
