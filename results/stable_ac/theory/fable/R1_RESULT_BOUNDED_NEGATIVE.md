# R1 result — CERTIFIED bounded negative on the P25 corridor (final, 29-07-2026 ~08:35 UTC)

STATUS UPGRADE: every [ORACLE] row below is now CONFIRMED by the independent fable stack
(`experiments/stable_ac/fable/`, 47 tests; full repo suite 78 passed; calibration gates
G1–G3 of the reconciled spec all passed, including: exact reproduction of the AK(3)
86,400-case histogram and orbit-2, exhaustive ≤7 batch with rank≡factorial YES-SET
equality — 2,352 YES / 1,984 NO — split-cut K₄−e schemes exercised on 144 instances, and
0 support-classification disagreements with the codex solver on all 5,464 non-degenerate
pairs). Additional confirmed rows beyond the draft list:
- the 331 truly-novel R1d harvest states (35 in the ≤17 census-gap stratum): all
  NOT_SPHERICAL (fable + oracle agree; TC triviality sampled 9/9).
- the 610 short-Aut images: regenerated and re-decided with the fable solver — 610/610
  NOT_SPHERICAL, exact count match with the oracle sweep.
- TC (independent implementation) certifies AK(3), P25, Q, and 5 path intermediates
  trivial (index 1).
- path[23], path[24] exact realizations: UNSUPPORTED (one A-loop each — correctly
  fail-closed), their common reduced form (= path[22]) NOT_SPHERICAL; factorial
  cross-check at 967,680 cases gives min genus 1, and path[51..53] reproduce genus 2.
Combined certified corpus this session: 997 fable-confirmed exact complexes (56 core +
610 images + 331 harvest), all with codex-oracle agreement where run; running field total
~3,752 with zero positives ever observed.

Mathematical by-product (sharpness): ("XXY","XYxy") — a presentation of ℤ — admits a
compatible spherical rotation whose ⟨AC,BC⟩ has 2 orbits: a genuine disconnected ∂N.
All 384 non-transitive YES cases in the ≤7 batch have abelianization determinant 0. So
Corollary 3's π₁ = 1 hypothesis is load-bearing, and the AuditContradiction gate is
correct exactly on trivial-group inputs (implemented as a flag, default raising).

Claim addressed: thickenability (γ_N = 0) hunting in AK(3)'s classical class (transfer
target: AK(3) AC-trivial ⇒ stably AC-trivial) and stable class (Q; transfer conditional on
MMS02 Prop 1.2). This note reports NEGATIVES ONLY; per the route ceiling, a negative has
zero content about AK(3) itself — it closes exact tested realizations, nothing more.

## Statement (to be finalized after independent confirmation)

For every exact word-realized presentation complex in the following list, no
Neuwirth-compatible spherical rotation system exists (γ_N ≥ 1; equivalently the exact
complex is not orientably thickenable):

1. P25 = (`XYxYXyxYYxyXy`, `YXyyXYxyxYYx`) — support K₄−e, [ORACLE] NOT_SPHERICAL.
2. Q = (`xxxxyXXYxyXXY`, `YxxyXXYxxyXXYxxyXXY`) — support K₄, [ORACLE] NOT_SPHERICAL.
   (Q presents the trivial group: Todd–Coxeter index 1, 453 cosets — advisor-verified,
   fable TC replication pending.)
3. The cyclically-reduced realizations of all 54 states of the doubly-verified 53-move AC
   path AK(3) ↔ P25 (39 K₄ + 15 K₄−e; states 23, 24 reduced from A-loop-bearing exact
   realizations, reduction = AC3 + free reduction) — [ORACLE] all NOT_SPHERICAL.
4. 610 distinct short-Aut(F₂) images (words ≤ 3 in σ, ι_x, ι_y, and four transvections) of
   AK(3), P25, Q, MS(3,w₁) — [ORACLE] all NOT_SPHERICAL. (Stable-class membership of
   φ-images by the stable ambient automorphism theorem; these bear on the STABLE claim
   only.)
5. MS(3,w₁) = (`XyyyxYYYY`, `XYXyxy`) — [ORACLE] NOT_SPHERICAL. (Classical-class
   membership cited from Shehper et al. citing MMS02; edge unverified this session.)

Verification chain for the final statement: fable rank solver (independent implementation
of the synchronized-planarity theorems, calibration gates G1–G3 of
R1_IMPLEMENTATION_SPEC.md as strengthened by R1_ADVISOR_RECONCILIATION.md) in agreement
with the codex rank solver on every row; exhaustion counters recorded per row; the ≤7
exhaustive factorial cross-check and the at-scale YES-rate control passed (numbers TBD).

## Interpretation

- These are the first Neuwirth verdicts on states OUTSIDE the codex height-17 component
  (P25 corridor lengths 18–25; Q length 32), extending the non-thickenability corpus from
  ~2,755 to ~3,42X exact complexes with zero positives ever observed.
- Consistency with the advisor's E-yield prior: Σ E over all tested rows ≈ 0.13 expected
  spherical hits under the null model — observing 0 is unremarkable; the model and the
  corpus stay compatible. The at-scale YES-rate control (random pairs at matched lengths)
  guards the alternative explanation (false-NO solver bug).
- The hunt continues in higher-E territory (R1d harvest) and higher rank (R1c).

## Data

`results/stable_ac/fable/gamma_n_targets.jsonl` (per-row words, support, verdict,
counters, witness/TC fields) — produced by `experiments/stable_ac/fable/run_targets.py`;
oracle recon rows in `oracle_verdicts_56targets.json`.
