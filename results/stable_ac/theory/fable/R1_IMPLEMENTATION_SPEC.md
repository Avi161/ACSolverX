# R1 implementation spec — independent Neuwirth γ_N decision stack (fable line)

Pending ac-advisor reconciliation; this records the plan of record for the build.
All NEW files; nothing existing is modified. CPU pure Python (+numba only if profiling
demands it — not expected; every instance here is tiny). No search anywhere near the
1,000-node budget rule (certificate evaluations, not searches).

## Modules (experiments/stable_ac/fable/)

- `ac_words.py` — letters x/X/y/Y; free reduction (stack form), cyclic reduction,
  inverse; the 12-move AC-Solver `ACMove` replayer re-implemented from first principles
  (concatenations r_i ← r_i·r_j^{±1} and conjugations r_i ← g^{±1} r_i g^{∓1}, numbering
  pinned to the AC-Solver convention by replaying the published 53-move sequence and
  asserting the endpoint is exactly (`xxxYYYY`, `xyxYXY`)). Purpose: the path fixture
  `p25_path_states.json` becomes reproducible from this branch alone.
- `neuwirth_core.py` — the exact D/A/B occurrence dictionary of the codex re-proof
  (`lit_AK3_NEUWIRTH.md`): darts d_i,h_i per occurrence; involutions B (tube) and A
  (corners); germ map ν; support multigraph + parallel classes; compatible-C enumeration
  (one cyclic order per unsigned generator at the + end, reversed B-image at the − end);
  genus sum from Lemma 1: (|A| − |C| + 2L − |AC|)/2 with L = #orbits⟨A,C⟩.
  `gamma_N_factorial(words, cap)` — exact minimum over all ∏(n_g − 1)! compatible C,
  refusing (UNKNOWN_SIZE) above the cap (default 5·10⁶ rotation systems). This is the
  independent ground-truth layer for small inputs.
- `neuwirth_rank.py` — the polynomial decision for connected loopless supports
  K₄ / K₄−e / C₄ per `lit_AK3_SYNCHRONIZED_PLANARITY.md`:
  Thm 3.1 (K₄ macro-rotation + block + reversal, one fixed macro-orientation justified by
  global reflection), Thm 5.2 (K₄−e bridge orders with cut i = 0..m_central), Thm 6.1 (C₄
  single scheme), Lemma 4.1 (two phases s_x, s_y), Lemma 4.2 (H_{A,B} = two relator
  cycles), Thm 4.3 (seed-rank propagation, per-class all-different + cross-cycle
  disjointness + union cardinality (4.4)).
  Fail-closed: returns UNSUPPORTED for loops, disconnected supports, or any other support
  type; never NO outside the proved scope; NO only after exhausting phases × cuts × seeds ×
  component combinations (counts reported in the verdict object).
  A YES returns the explicit witness rotation system C.
- `witness_check.py` — independent verifier for any YES: rebuilds D/A/B from the words
  alone, checks C is a valid rotation system (one cycle per germ, correct dart sets),
  checks compatibility C_{τv} = B C_v⁻¹ B per generator, computes |C|, |A|, |AC|, L and
  asserts genus 0 (and prints the Euler line). Shares no scheme code with
  `neuwirth_rank.py` (permutation arithmetic only).
- `run_targets.py` — evaluates: P25, Q, and the 54 path states (cyclically reduced
  realizations; the exact tested words are recorded per row). Output: jsonl under
  `results/stable_ac/fable/gamma_n_targets.jsonl` with per-row words, support, verdict,
  witness-or-exhaustion-counts, and solver+checker versions.

## Tests (tests/ — collected by bare pytest)

`tests/test_fable_neuwirth.py` (+ small helpers):
1. AK(3) exact fixture: factorial census gives 86,400 compatible C and γ_N = 2 (pins the
   codex certificate numbers); orbit-2 gives γ_N = 1.
2. Rank solver ≡ factorial census on a deterministic batch of small pairs (total length
   ≤ 7–9) filtered to supports in scope, and the batch MUST contain both YES and NO
   verdicts (no vacuous agreement).
3. Witness round-trip: every YES witness passes `witness_check` and every witness-check
   failure is surfaced loudly (audit-contradiction per Corollary 3, not a soft skip).
4. `ac_words` replay: 53-move sequence from P25 reaches exactly AK(3); path states file
   regenerates byte-identically.
5. Fail-closed: a loopy input (e.g. word pair ("xXy","xXy") exact realization) and a
   disconnected/unsupported support return UNSUPPORTED, not NO.
Budget note: the factorial census on AK(3) is 86,400 rotation systems ≈ seconds; all test
inputs are fixed tiny words; nothing scales with a node budget.

## Calibration gates before ANY verdict on the targets is believed

G1. Tests 1–5 green (default tier; then the mandatory suites of this branch:
    bare `pytest` green).
G2. One-off cross-check (recorded in the results doc, not a committed dependency): the
    codex `neuwirth_rank_solver.py` (scratch copy from their branch) agrees with my rank
    solver on AK(3), orbit-2, and the small-pair batch. Any disagreement = stop, diagnose.
G3. For the actual targets: my rank solver's verdict on P25/Q/path states; any YES
    additionally passes `witness_check` AND the codex solver cross-check.

## Verdict semantics (imported hard rules)

- YES on any target ⇒ (Thm 2 sufficiency + Corollary 3 + Lackenby Thm 1.3) that exact
  complex is thickenable and the presentation is classically AC-trivial ⇒ transfer along
  the verified edge to AK(3). Write the theorem, run suites, commit, notify.
- NO on a target closes only that exact word realization; never transported, never
  evidence about AK(3).
- UNSUPPORTED is routed to (future) general Synchronized Planarity work, not guessed.
