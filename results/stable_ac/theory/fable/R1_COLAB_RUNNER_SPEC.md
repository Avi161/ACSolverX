# R1 production runner spec (Colab tier — for the user; fable line, 29-07-2026)

Production budgets are the user's, on Colab. This spec parameterizes the committed fable
modules into three runs, per the notebook lessons (3-cell CONFIG/SETUP/RUN pattern,
TIME-based heartbeat — 60 s in-search beat + ~5 min cumulative line — and the
Restart → Run All contract; results jsonl on local disk with whole-file Drive mirror;
resume identity in the filename stem; no dates in resume keys).

## Run A — deep harvest (extends R1d beyond the local round)

- Roots: the 32 path states (indices 0–31) + every novel state from the local round;
  ITERATIVE re-rooting allowed on this tier (novel states become roots), rounds until no
  novel state appears (report a plateau, never a wall).
- Budget: 20,000 pops/root (sweep-check smaller budgets by prefix — a search at B is the
  first B pops of any longer run); per-relator cap: sweep 15 → 20 → 25 (the cap is
  structural: raising it exposes states unreachable at ANY budget below it — report per
  cap, never pooled).
- Every distinct state: canonical key (rotation × inversion × swap), support class,
  E-score; γ_N-test all supported classes (K₄/K₄−e/C₄ + P₄/one-loop/paw when ported +
  rank-n 3-connected when implemented); factorial fallback ≤ 5·10⁶ rotations; UNSUPPORTED
  counted separately.
- Row schema: exact words, reduced words + reduction flag, canonical key, root chain
  (move path to AK(3) — the membership certificate), support + multiplicities, E,
  verdict, counters/witness. Any YES: verify witness in-notebook AND persist immediately
  (a computed result reaches disk before anything else is attempted — heavy-mode lesson).
- Resume: jsonl keyed by canonical key; unique-row-count progress (never line count).

## Run A′ — the AK(2) control (added after the local control experiment)

Identical harvest machinery rooted at AK(2) = (`xxYYY`,`xyxYXY`) (trivial, provably
AC-trivial class), run until cumulative ΣE ≫ 1. Purpose: end-to-end validation that the
pipeline finds hits at the E rate in a class where hits are legitimate. Interpretation
matrix: AK(2) hits at ~E rate + AK(3) zero at matched ΣE ⇒ genuine class-level phenomenon
(R3′ target); both at ~E rate ⇒ the hunt is a pure scale problem; both zero at ΣE ≫ 1 ⇒
suspect the model or the solver (cross-check with Run B). Local round 1 (1,000 pops):
1,251 canonical members, all NOT_SPHERICAL.
SEARCH-PRIORITY NOTE for Run A and A′: best-first by E-DESCENDING (not length) — E
rewards concentrated corner distributions; length-ascending under-samples the high-E tail.

## Run B — false-NO alarm control at scale

Random cyclically-reduced pairs at total lengths {17, 21, 25, 29} with supports in the
decided classes, ≥ 250k pairs per length tier: record predicted E and observed YES rate;
verify every YES witness. Zero hits at a tier where ΣE ≫ 1 = solver alarm — STOP and
report, do not continue harvesting with a suspect solver.

## Run C — rank-3 sweeps (after R1c implementation lands)

Targets in priority order: (1) z-stabilized variants of the 54 path states and P25
(z⁻¹w insertions per the CoV family enumeration, applied at rank 3 WITHOUT immediate
destabilization); (2) MMS3(w) members for short w with exponent-sum ±1 — each row FIRST
gets a TC triviality certificate (the family contains non-trivial groups, e.g. an
SL(2,5) member; a γ_N = 0 on a non-trivial-group row proves nothing); (3) the B₃-route
3-generator elimination stages (R1B doc). Supports outside 3-connected+factorial scope
are counted UNSUPPORTED pending P/S-node schemes.

## Ceilings to respect in all runs

A YES anywhere transfers to AK(3) ONLY through a verified membership chain (classical
chain ⇒ AC-trivial; stable chain ⇒ stably AC-trivial; say which). All-negative outcomes
are bounded negatives about tested realizations at tested caps/budgets — the route
ceiling (R1 succeeds iff AK(3) is (stably) AC-trivial) means a negative sweep never
becomes evidence about AK(3) itself.
