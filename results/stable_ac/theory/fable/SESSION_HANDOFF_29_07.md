# Fable line — session handoff (29-07-2026, updated ~13:02 UTC)

Entry point for the next session. Read CLAUDE.md first, then this. Branch:
`claude/ac-stable-ac-conjecture-ijfzgz` (merge → `fable/proof` by the user; never `main`;
no PRs). Push was 403-blocked all session (GitHub app write permission); if still blocked,
notify the user and keep the retry cadence.

## Where the line stands

- Goal (stable ACC) OPEN. AK(3) sub-goal OPEN. Nothing here is a counterexample claim.
- Route R1 (thickenability transfer) fully framed: AK(3) stably trivial ⟺ its stable
  class contains a thickenable member (R1_EQUIVALENCE_AND_RECON.md). Decision machinery
  COMPLETE and certified for ranks 2–3 INCLUDING disconnected links:
  `experiments/stable_ac/fable/` (480 tests; run bare `pytest` before believing
  anything).
- NEW (this update): **R1e arc complete.** Theorem D (disconnected-link thickenability:
  γ_N with the general 2L defect decides, no connectivity hypothesis), Lemma S (wedge
  decomposition under no-straddle), Corollary Z (γ_N + full defect histogram invariant
  under exact AC4/AC5 — first stabilization invariance), Lemma P (canonicalization is
  an AC composite; 6-move swap derivation) — advisor-vetted, adversarially audited
  (REPAIRABLE → repairs F1–F8 applied), all in R1E_DISCONNECTED_LINK.md. Applied: the
  382 round-2 disconnected states = 382 distinct rank-2 pairs in AK(3)'s STABLE class
  (85 via AK3+z, 297 via the P25+z path certificate) — ALL NOT_SPHERICAL
  (disconnected_split_verdicts.jsonl; ΣE 0.0526; 0 undecided; joint-census
  cross-checks histogram-identical; 10/10 corpus agreements). Round 2 is now
  11,273/11,273 decided.
- Certified corpus: ~17,100 non-thickenable exact realizations across the classical
  corridor (P25/Q/path/images/harvest), the rank-3 stable harvests (rounds 1–2), and
  the rank-2 shadow of the direct stable walk. Zero spherical ever. Statistics still
  within the null model (AK(2) control; ΣE bookkeeping in each results file).
- Theorems audited this session: rank-n 3-connected (R1C_RANK_N_THREECONNECTED.md),
  cut schemes (R1C_V2_CUT_SCHEMES.md with normative errata E1–E5), γ_N symmetry lemma
  (audit still pending on its own text — flag inherited where cited), Theorem D et al.
  (R1E_DISCONNECTED_LINK.md).
- R2 (Wirtinger repair) DORMANT; R3 invariant walls documented; R3′ (synchronization
  defect / class-functional obstruction) is the live disproof-side program
  (R3PRIME_DIGON_EXCESS.md).

## Next actions, in order of value

1. USER: run the Colab tier (R1_COLAB_RUNNER_SPEC.md — deep harvest with E-descending
   priority, the AK(2) control to ΣE ≫ 1, false-NO control, rank-3 sweeps). The
   interpretation matrix is in the spec; hits decide AK(3), matched-ΣE zeros create the
   first genuine phenomenon for R3′. Consider adding a rank-2-shadow harvest round
   (walk at rank 3, project every destabilizable state via Lemma S — the round-2 walk
   found 382 such states without trying; a walk BIASED toward z-inert returns could
   multiply that).
2. R3′: formalize the phase-obstruction technique at the class-functional level — how
   phase systems transform under AC1 corner grafting. Division of labor with codex
   recorded in R3PRIME doc. Codex's new period-two augmented cut covariance work
   (.scratch/period_two_augmented_cut_covariance.md at 06ac5b0) is adjacent — read
   before starting to stay complementary.
3. Run the γ_N symmetry lemma's own adversarial audit (small; the R1e auditor already
   hand-verified the inversion bijection incl. N = 1) to clear the inherited flag.
4. Verify from sources when network allows: Lackenby Thm 1.3 (flagged), MMS02 Prop 1.2 /
   Q provenance (NOTES_FOR_CODEX_LINE.md item 5).
5. Relay NOTES_FOR_CODEX_LINE.md to the codex line (now 8 items — item 7 lets them lift
   their disconnected fail-closed gate).

## Session discipline notes

Two disclosed budget deviations logged earlier (one 3,000-pop shared queue; one
subagent 5k/20k diagnostic probe) — both classification-only, neither produced result
claims. R1e arc ran with zero deviations (pure classification, pinned budgets, no AC
search). Lessons in experiments/lessons/ + CLAUDE.md index. Codex fetched every ≤30 min
all session (their frontier: Hessian/phase-obstruction, Aut-frontier manifest work; no
collisions).
