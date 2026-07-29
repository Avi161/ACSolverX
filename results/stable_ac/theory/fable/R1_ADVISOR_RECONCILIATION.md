# R1 — ac-advisor gate verdict (REVISE) and reconciliation, 29-07-2026

Gate ran as a general-purpose opus agent operating under `.claude/agents/ac-advisor.md`.
Verdict: **REVISE** — transfer chain (i)–(iii) airtight; (iv) conditional on MMS02
Prop 1.2; five must-address items. Every item is reconciled below before implementation.

Advisor's independent contributions adopted into the plan:
- **Q, P25, AK(3) all present the trivial group** — proven by the advisor's own HLT
  Todd–Coxeter enumerator (index 1 with 453/564/34 cosets; validated on six control
  groups). The fable stack re-implements TC independently as the π₁ = 1 verifier.
- **Regina is NOT logically required for a positive**: Theorem 2's sufficiency is a
  complete PL construction from (a) compatibility, (b) Euler pass, (c) L(C) = 1;
  Corollary 3 reaches N ≅ B³ via Poincaré + PL Schoenflies. Independent permutation
  arithmetic on (a)(b)(c) IS the proof; Regina is prudence.
- **E-yield model** (heuristic, flagged as such; calibrated on AK(3): 384/86,400 =
  4.4e−3 predicted vs 0 observed spherical): P25 ≈ 1.6e−5, Q ≈ 1.9e−9, Σ path ≈ 0.13,
  Aut-image sweeps of Q ≈ 3.7e−7 (dropped as primary effort). Yield ranking for future
  sweeps: E ∝ (#spherical rotations of support)/∏(n_g − 1)! — rank candidates by this
  before testing; short neighbors dominate.
- **Published checksum**: app/ac_paths.tex carries a commented (move, total_length)
  53-entry trace; the advisor verified our fixture matches all 53 lengths — a
  non-circular external checksum the replay must assert.

Item-by-item reconciliation:
1. FRAMING.md provenance error FIXED (Q ≠ P25; Q total length 32; Q triviality proven;
   Lackenby Thm 1.3 marked [unverified this session] pending source read).
2. Priorities re-ordered: path+P25 first, Q conditional add-on, Q-Aut sweeps dropped;
   route ceiling stated outright: **R1 succeeds iff AK(3) is (stably) AC-trivial — a
   negative sweep has zero content beyond a bounded negative** (recorded also in
   R1_EQUIVALENCE_AND_RECON.md). Note: the oracle reconnaissance (run before the gate
   returned; the advisor independently recommended a scout step) already shows
   NOT_SPHERICAL on all 56 core targets + 610 Aut-images — so the build's primary
   deliverables are (a) independent confirmation → certified bounded negative, (b) the
   false-NO alarm control, (c) the ranked neighbor-hunt engine.
3. Calibration hole closed in the spec: exhaustive ≤7 batch must reproduce codex's
   328 K₄ / 568 K₄−e / 516 C₄ = 1,412 inventory with YES-SET EQUALITY (not counts);
   a K₄−e fixture with m_central ≥ 2 and a split cut 0 < i < m verified by factorial
   census; an at-scale random YES-rate control at total length 25 (~10⁵ certificate
   evaluations locally; expected hit rate ~1e−5; ZERO hits in 10⁶ = false-NO alarm;
   the 10⁶-scale control is a Colab runner for the user). Oracle = neuwirth_rank_solver
   ONLY (check_thickenable precollapses via Tietze — decides a different complex).
4. witness_check strengthened: assert L(C) = #Orb⟨A,C⟩ = 1; assert ⟨AC,BC⟩ transitivity
   (right-to-left) with failure = AUDIT CONTRADICTION (Corollary 3), never a soft skip;
   independent TC π₁ = 1 recheck; degenerate gate — any relator below 3 letters or fewer
   than 4 germs ⇒ UNSUPPORTED, never NO.
5. Path re-derivation decoupled from the authors' code: h₁…h₁₂ implemented literally from
   app/ac_paths.tex; assert endpoint AND the 53-entry published length trace AND
   per-transition membership among the 12 recomputed children; record states 23, 24 as
   non-cyclically-reduced (A-loops in exact realization; reduced forms are AC3-equivalent
   and K₄); dedup the ≤16-length tail (indices ~32–53) against codex
   ak3_component_thickenability.json before any novelty claim.

Also absorbed: advisor flags its own instruction file's engineering section as stale for
this checkout (no .venv, no experiments/stable_ac, envs/ is JAX) — the mandatory test
gate on this branch is bare `pytest` (CI parity), which the spec already uses.
