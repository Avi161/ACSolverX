# [2026-07-24] A rung-local beam ladder saturates at depth ~9 — deepening it 32× buys one class [TRAP]

## Evidence

The big μ-ladder (`mu_ladder_big`, `rungs=256, beam=64`, 124 classes, commit `f4056f8`) cost **346.8 CPU-hours and 5,579,015 orbits** — 90× the orbits per class of the r8/b12 ladder that preceded it. Measured from the per-rung `best` series in the summary rows:

- **Every one of the 36 descenders first touched its final `best_mu` by rung 9** — 14 of them at rung 2, and only `aca_100` as late as 9.
- **98% of all rungs that ran, ran after their class's last gain.**
- Against the closed prior census (35/124 at r8, beams 12 and 24) the entire run bought **one new descender** (`aca_67`, 21→20) and 5 deeper floors. Zero regressions.
- Only **367 of 5,579,015 orbits (0.0066%) sit below their own class's starting μ**; 97.5% are above μ 24 and the distribution runs to μ 302.

The 48 rows the 4h backstop cut are irrelevant to this: they were all cut long after rung 9, so no floor was lost to a timeout.

## The rule

**Depth is not the knob on a rung-local beam.** Before spending compute on more rungs, plot *the rung at which each result was first achieved* — if that number is small and flat while the rung ceiling is large, every additional rung is climbing the cone, not searching. This is the second occurrence of the same mechanism as [`rung-local-beam-abandons-the-low-shell`](rung-local-beam-abandons-the-low-shell.md): the beam keeps only *this rung's* top-K, so the front drifts monotonically upward and more orbits buy strictly worse states. Widening the beam 5× and deepening 32× did not change that — it only bought a proportional amount of high-μ territory.

Corollary for reporting: a run like this measures a **plateau**, never a wall. Only a global best-first heap over the open set can make a closure claim ("no orbit below μ X anywhere in the ball"), and that is the arm the compute should have gone to.

## Also confirmed here

The saturation number is what makes the run's nulls cheap to trust and its scale worth keeping anyway: the 5.58M-orbit dump enabled three collision scans (ms640's 113 seed orbits, cross-class, AK(3)) that the 35-floor-rep dumps could not attempt. Depth was wasted; the *provenance* was not.
