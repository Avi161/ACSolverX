# Fable proofs program

Branch: `fable/proofs` (cut from `codex/proofs` @ `0e59e1f`). New files only; nothing
outside `fable/` is modified. No PRs (repo hard rule); work lands on this branch.

## Charter

Independent lane, deliberately orthogonal to the codex program. Codex is deep in the
class-two noncancellation tower for the hardest depth-four signature (route 2 of
`docs/AK3_PROMISE_LEDGER.md`). This lane does not duplicate that work.

Final goal (user directive): a conclusion for AK(3) — trivializable (AC or stable AC)
or genuine counterexample. Honest posture inherited from `.agents/instructions/ac-theory.md`:
bounded results are evidence with their stated scope, never a resolution; no claim is
promoted beyond its proof.

## Workstreams

- **W1 — Finite AC-graph decision for the MMS02 bridge.** The bridge
  `(A,B,zYX) ~AC (A,B,Xyz)` in `F(x,y,z)` (promise-ledger route 1) is the single
  known finite target implying AK(3) stably AC-trivial. The misprinted base group
  `G_mis = <x,y,z | A,B>` is nontrivial, so finite quotients bite on the *bridge*
  (unlike rank-2 AK(3), where any hom killing both relators kills everything).
  For every hom `phi: F(x,y,z) -> G` (G finite) with `phi(A)=phi(B)=1`, an AC path
  forces `(1,1,phi(zYX))` and `(1,1,phi(Xyz))` into one orbit of the AC-move action
  on `G^3` (entrywise inversion; conjugation by `im(phi)`; row_i <- row_i * c with c
  a conjugate of row_j^{±1}, i≠j). This orbit question is a **complete finite
  closure**, not a budgeted search: decide it by exact BFS.
  - Refuted orbit equality for any single phi ⇒ the bridge is FALSE (major negative
    course-correction for route 1; does not decide AK(3) itself).
  - Orbit equality for all tested phi ⇒ the known A5 fixed-base obstruction dies
    entirely; the bridge survives as a search target.
- **W2 — Period-two baseline uniqueness.** The agreed scope gap in the codex tower:
  classify solutions of the backward conjugacy system in `C_2 * Z` up to gauge, and
  either prove the chosen witness is the unique baseline (making a completed
  noncancellation close the signature at class two) or exhibit a second baseline
  (bounding what the tower can conclude). Outcome is valuable in both directions.
- **W3 (reserve) — all-depth potential.** Only if W1/W2 produce structure suggesting
  a well-founded potential surviving the self-loop/gauge analysis.

## Rules of operation

- Computations run foreground through `scripts/run_proof_guarded.py`, short mode
  (≤60 s); one at a time; single numerical thread. Node-budgeted searches ≤1,000
  nodes (repo hard rule). Complete finite closures are certificates, not searches,
  and still respect the wall-clock guard.
- Opus subagents are used for plan review and hostile derivation audit only; no
  subagent runs proof, search, or test computation.
- Every result lands as: a note in `fable/proofs/`, an independent checker in
  `fable/proofs/checkers/`, a `LOG.md` entry with UTC time and commit SHA, then a
  push. Claims carry explicit nonclaims.
- Hourly self-audit (scheduled wake): is the current work rigorous, non-duplicative
  of codex, and moving toward a decision? Re-arm the next check before resuming.
