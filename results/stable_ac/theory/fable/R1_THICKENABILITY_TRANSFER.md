# R1 — Thickenability transfer along the MMS02 Prop 1.2 stable edge

Status: ACTIVE (fable line). Claim addressed: **stable AC-triviality of AK(3)** (not
AC-triviality, not group triviality). Created 29-07-2026; see FRAMING.md §6.

## The transfer argument (exact logical chain)

1. **MMS02 Prop 1.2** (Myasnikov–Myasnikov–Shpilrain 2002, misprint-unaffected —
   verification from source in progress): AK(3) ~st Q where
   Q = ⟨x,y | x⁴ = yx²y⁻¹·x⁻¹·yx²y⁻¹, y = [x²,y]³⟩.
   As cyclic relator words (r = LHS·RHS⁻¹, [a,b] = aba⁻¹b⁻¹ — conventions to be pinned
   against the source):
   r1 = `xxxxyXXYxyXXY` (13 letters), r2 = `YxxyXXYxxyXXYxxyXXY` (19 letters).
2. **Neuwirth criterion** (codex line's `lit_AK3_NEUWIRTH.md` Theorem 2, re-proved from
   Neuwirth 1968): for a connected link graph, the exact word-realized presentation complex
   K_P is orientably thickenable ⟺ γ_N(P) = 0, decided over compatible rotation systems C
   by the Euler pass |A| − |C| + 2 = |AC|.
3. **Lackenby arXiv:2606.06122 Thm 1.3** + Corollary 3 of `lit_AK3_NEUWIRTH.md`: a
   thickenable balanced presentation of the trivial group is classically AC-trivial.
4. **Transfer**: if γ_N(Q′) = 0 for ANY presentation Q′ in the stable AC class of AK(3),
   then Q′ is AC-trivial ⇒ Q′ ~st standard ⇒ **AK(3) ~st standard**. One γ_N = 0 witness
   anywhere in the class settles AK(3)'s stable case positively.

A γ_N = 0 verdict comes with an explicit witness C; verifying the witness is elementary
permutation arithmetic (compatibility + Euler pass), independently checkable — no search
trust required. Negatives never transport (γ_N is NOT an AC invariant — codex counterexample
on record), so a negative on Q only closes Q's exact realization.

## Why this is virgin territory (complementarity audit, 29-07-2026)

- The codex line certified AK(3) itself γ_N = 2 (86,400-case census), orbit-2 γ_N = 1,
  the full height-17 classical component (1,000 states), one-hop CoV (34 outputs), two-hop
  CoV (1,352 outputs), and the rank-3 corridor quotients (303 + 64 rigid) — ALL
  non-thickenable, zero positives. Their thickenability track has been dormant since
  2026-07-24; current frontier is depth-4 primitive-pair barrier theory (Φ∞ Hessian
  certificates, commits through a1a411b 29-07).
- **No Neuwirth solver has ever been pointed at the Prop 1.2 partner Q** (verified by
  branch-wide grep: MMS02/Prop 1.2 appear only in advisory files, ranked LOW for greedy
  seeding — a different use). Q's stable-class neighborhood is untested.
- Their stated dormant lead is "reach any thickenable presentation in AK(3)'s classical or
  stable move class ... must leave this bounded component — by greater height, by stable
  AC4/AC5 moves, or by another rigorously certified change of representative." Q IS such a
  certified change of representative — reached through MMS02's stable chain, far outside
  their censused families.

## Feasibility (computed 29-07-2026, scratch `p25_support.py`)

With the presumed words: both relators cyclically reduced; occurrence degrees x:21, y:11
(factorial census 20!·10! — impossible); link support = **loopless connected K₄**
(multi-edges: x⁺x⁻:11, x⁻y⁺:5, x⁻y⁻:5, x⁺y⁻:5, x⁺y⁺:5, y⁺y⁻:1). K₄ is in the codex
rank-solver's PROVED support list (`neuwirth_rank_solver.py`, spec
`AK3_SYNCHRONIZED_PLANARITY.md`), which decides sphericality in polynomial time at any
length and was cross-validated against the factorial census on 1,412 length-≤7 pairs with
full agreement. So the decision for Q is computable now.

## Plan of record (pending ac-advisor gate)

1. Pin exact Q words + Prop 1.2 proof mechanism from the MMS02 source (agent in flight);
   re-run the support computation on the pinned words.
2. Independent implementation of the K₄/K₄−e/C₄ rank solver on this branch
   (`experiments/stable_ac/fable/`), calibrated against: AK(3) γ_N = 2 census, orbit-2
   γ_N = 1, and the codex 1,412-pair length-≤7 census — full-agreement gate before any
   verdict on Q is believed. (Their branch's solver is used only as a cross-check oracle,
   never as the sole certifier.)
3. Decide γ_N(Q). If 0: extract witness C, verify independently, write the full transfer
   proof, run mandatory test suites, commit, notify user immediately.
4. If γ_N(Q) > 0: hunt the stable class — γ_N is realization-sensitive, so test
   (a) Aut(F₂)-images φ(Q) for short φ (legitimate: stable ambient automorphism principle,
   PROOFS.tex Thm 3, rank 2, balanced, trivial group — hypotheses all hold);
   (b) small Definition-2.1 / AC neighbors of Q; (c) the other MMS02-mechanism partners if
   the Prop 1.2 proof generalizes (mechanism study = R1b). Small local sweeps only
   (≤ ~100 states, certificates not searches); larger sweeps become a Colab runner for the
   user.
5. All-negative outcome: write up as a bounded negative with exact counts (never as
   evidence about AK(3)); the route then continues through R1b (mechanism-generated
   neighbors) or hands to R2/R3.

## Trap ledger for this route

- Prop 1.2's exact words, orientation, and commutator convention MUST be pinned from the
  source before any verdict is claimed (current words are presumed).
- γ_N negatives do not transport; only positives decide. Never phrase a negative sweep as
  evidence about AK(3).
- The word-realized complex is unreduced: all tested realizations must be given as exact
  cyclic words; cyclically reduce first (loopless support) and SAY SO.
- Stable ambient automorphism is rank-2-proved only; do not apply φ-image testing at rank 3
  without the higher-rank re-derivation.
- Any THICKENABLE verdict is a suspected bug until the witness C is re-verified by an
  independent implementation (permutation arithmetic) — codex protocol, adopted.
