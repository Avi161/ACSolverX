# Fable line — session handoff (29-07-2026, ~11:40 UTC)

Entry point for the next session. Read CLAUDE.md first, then this. Branch:
`claude/ac-stable-ac-conjecture-ijfzgz` (merge → `fable/proof` by the user; never `main`;
no PRs). Push was 403-blocked all session (GitHub app write permission); if still blocked,
notify the user and keep the retry cadence.

## Where the line stands

- Goal (stable ACC) OPEN. AK(3) sub-goal OPEN. Nothing here is a counterexample claim.
- Route R1 (thickenability transfer) fully framed: AK(3) stably trivial ⟺ its stable
  class contains a thickenable member (R1_EQUIVALENCE_AND_RECON.md). Decision machinery
  COMPLETE and certified for ranks 2–3: `experiments/stable_ac/fable/` (465 tests; run
  bare `pytest` before believing anything).
- Certified corpus: ~16,700 non-thickenable exact realizations across the classical
  corridor (P25/Q/path/images/harvest) and the rank-3 stable harvests (rounds 1–2), zero
  spherical ever. Statistics still within the null model (AK(2) control; cumulative
  ΣE ≈ 1 at rank 2). Full details: R1_RESULT_BOUNDED_NEGATIVE.md + the two
  rank3_harvest jsonl files.
- Theorems audited this session: rank-n 3-connected (R1C_RANK_N_THREECONNECTED.md),
  cut schemes (R1C_V2_CUT_SCHEMES.md with normative errata), γ_N symmetry lemma.
- R2 (Wirtinger repair) DORMANT; R3 invariant walls documented; R3′ (synchronization
  defect / class-functional obstruction) is the live disproof-side program
  (R3PRIME_DIGON_EXCESS.md).

## Next actions, in order of value

1. USER: run the Colab tier (R1_COLAB_RUNNER_SPEC.md — deep harvest with E-descending
   priority, the AK(2) control to ΣE ≫ 1, false-NO control, rank-3 sweeps). The
   interpretation matrix is in the spec; hits decide AK(3), matched-ΣE zeros create the
   first genuine phenomenon for R3′.
2. THEORY GAP: the 382 round-2 states with disconnected links (z decoupled) need a
   disconnected-link thickenability theorem — Neuwirth Thm 2 requires L = 1; nesting of
   components in a common sphere is not captured by per-component rotations (codex
   fail-closed note). New theorem, then re-decide that bucket.
3. R3′: formalize the phase-obstruction technique (codex AK3_NEUWIRTH_PHASE_OBSTRUCTION,
   a17c7bf) at the class-functional level — how phase systems transform under AC1 corner
   grafting. Division of labor with codex recorded in R3PRIME doc.
4. Verify from sources when network allows: Lackenby Thm 1.3 (flagged), MMS02 Prop 1.2 /
   Q provenance (NOTES_FOR_CODEX_LINE.md item 5).
5. Relay NOTES_FOR_CODEX_LINE.md to the codex line.

## Session discipline notes

Two disclosed budget deviations logged (one 3,000-pop shared queue; one subagent 5k/20k
diagnostic probe) — both classification-only, neither produced result claims. Lessons in
experiments/lessons/ + CLAUDE.md index. Codex fetched every ≤30 min all session (their
frontier: Hessian/phase-obstruction work; no collisions).
