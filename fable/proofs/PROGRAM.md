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

> **Status after 21 cycles (2026-08-28): see [`SYNTHESIS.md`](SYNTHESIS.md).**
> W1 closed (vacuity theorem). W2 ran far past its original scope: census →
> normal form → layer-1 obstruction-free theorem (W2g/W2h) → layer-2 collapse
> to `Ξ_Z(Θ) = 0` (W2i) → complete mod-2 exclusions with no claimable
> obstruction (W2l); the open item is the W2m cocycle lemma. W3 grew into the
> W6 chain: rank-3 machinery, `Tpub` decided not thickenable as spelled, the
> closed rank-3 ball fully decided at ceilings ≤ 18 (all negative). W5 proved
> the bridge IS one-stabilization AK(3) and the invariant battery blind.
> AK(3): open both ways; the deciding levers are ranked in the synthesis.

- **W1 — CLOSED (method-closure theorem; original premise retracted).** The
  original premise ("`G_mis` nontrivial ⇒ finite quotients bite on the bridge")
  was FALSE: with the base rows killed, the third entry normally generates the
  image on both sides, forcing orbit equality in ANY group (vacuity theorem,
  `W1_BRIDGE_FINITE_TEST.md`), and Borovik–Lubotzky–Myasnikov 2005 closes every
  finite quotient for the non-base-killing variant too. Deliverables kept: the
  blindness theorem, the move-model regression pins, and the retraction record.
  Refuting the bridge now requires infinite-quotient / noncommutative invariants
  (Alexander–Fox, Quinn-type); proving it requires search or structure
  (`W1C_TPUB_PREFLIGHT.md` production handoff stands: greedy descends 29 → 14
  within 1,000 nodes; production budget is the user's, on Colab).
- **W2 — Period-two baseline uniqueness.** The agreed scope gap in the codex tower:
  classify solutions of the backward conjugacy system in `C_2 * Z` up to gauge, and
  either prove the chosen witness is the unique baseline (making a completed
  noncancellation close the signature at class two) or exhibit a second baseline
  (bounding what the tower can conclude). Outcome is valuable in both directions.
- **W3 — Thickenability / Lackenby lever (plan pending advisor gate).**
  Lackenby (arXiv:2606.06122, 2026) proves thickenable balanced presentations of
  the trivial group satisfy the UNSTABLE Andrews–Curtis conjecture, with an
  explicit (tower) bound. Therefore exhibiting ANY thickenable presentation
  AC-equivalent to AK(3) proves AK(3) AC-trivializable — a theorem-backed
  decisive endpoint, and the only known one for the unstable question. The repo's
  route 3 frontier (1,000-map Aut(F2) scan, bounded null) barely scratches this.
  Before any work: read `experiments/stable_ac/thickenable/`,
  `results/stable_ac/theory/*THICKENABILITY*`, pin Lackenby's exact statement,
  and gate a plan through ac-advisor.
- **W4 (reserve) — all-depth potential.** Only if W2/W3 produce structure
  suggesting a well-founded potential surviving the self-loop/gauge analysis.

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
