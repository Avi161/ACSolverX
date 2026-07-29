# R1b — stable-neighbor generator mechanism (notes, 29-07-2026)

Claim context: these are STABLE-class memberships (each item names its edge). Source:
Shehper et al. LaTeX (sec/stable.tex, app/mms.tex, comment blocks with Lucas Fagan's Sage
derivations), obtained from github.com/ammedmar/ac_paper@d86984d. All quoted derivations
must be independently replayed before load-bearing use — they currently have
"paper-source" status, not "verified" status (except where noted).

## The substitution-and-removal edge generator

Lemma (Substitution and Removal, = this repo's Lemma-11 usage): for a presentation of the
trivial group ⟨x₁..xₙ, y | r₁..rₙ, y⁻¹w⟩, eliminating y by substituting w is a stable AC
equivalence to ⟨x₁..xₙ | r₁'..rₙ'⟩. Every elimination ORDER and every intermediate stage
yields presentations in the SAME stable class. So each 14-generator seed below spawns a
tree of stable neighbors (3-generator and 2-generator leaves included).

## Seeds in AK(3)'s stable class (via the misprinted diagram W′, r₇ route)

- W′ = the misprinted 14-relator "Wirtinger" presentation (13th relator x₁₃ = x₅x₁₂x₅⁻¹).
  W′ minus r₇ presents B₃ (Shehper app/mms.tex). Lucas's comment-block derivation:
  W′ minus r₇, eliminating generators in a recorded order, reaches
  ⟨x₇,x₁₃ | x₇x₁₃x₇ = x₁₃x₇x₁₃⟩ ≅ B₃; hence W′ minus r₇ plus w is stably AC-equivalent to
  ⟨x,y | xyx=yxy, w⟩. With w chosen so that this is AK(3) (e.g. w = x³y⁻⁴ up to the braid
  quotient — exact w to be pinned by replay), EVERY intermediate stage of that elimination
  is a stable neighbor of AK(3): ranks 14 down to 2.
- The r₁₂ route (MMS02 Thm 1.4's choice) gives the 3-generator MMS3 family
  ⟨x,y,z | x = z·[[y⁻¹,x⁻¹],z], y = x·[[y⁻¹,x⁻¹],z⁻¹]·[z⁻¹,x], w⟩; with w = x⁻¹yz and
  z eliminated → P25 (already in the target list; NOTE the r₁₂-route group facts are
  misprint-poisoned: W′ minus r₁₂ is NOT Z — each member's triviality must be checked
  per-w, not assumed).
- The verified 53-move AC path AK(3) ↔ P25 (classical class) — already fixtures.

## Consequences for the hunt

1. Rank-2 targets now: P25, Q, 54 path states (all K₄/K₄−e — decidable).
2. Rank-3 targets next: MMS3(w) members and Lucas's B₃-route 3-generator stages. Neuwirth
   applies at every rank, but the polynomial solver theory currently covers only 4-germ
   supports (K₄, K₄−e, C₄ [+ codex's P₄, one-loop, paw, K₆−E(P₅) rigid]). A 6-germ
   (rank-3) synchronized-planarity rank solver is a NOVEL theory contribution this line
   can own — none exists beyond the rigid K₆−E(P₅) case. Parked as R1c.
3. The w-parameter gives infinite families: for each elimination stage, sweeping short w
   with exponent-sum ±1 gives many stable-class members (their triviality varies! Each
   candidate needs a per-w triviality check before Thm 1.3 can be invoked — e.g.
   ⟨x,y | xyx=yxy, yx²yx⁻³⟩ is SL(2,5), order 120, NOT trivial (Lucas's Sage note). A
   γ_N = 0 hit on a NON-trivial-group member proves nothing about AK(3)).

## Trap ledger additions

- The Wirtinger redundancy property (∏ rᵢ^{±1} = 1) FAILS for W′ — never invoke
  prop:unknot-stable / thm:unknot for anything derived from W′.
- Group triviality is per-(seed, w) and must be certified before any transfer (only the
  states on verified AC/stable chains from AK(3) inherit triviality for free).
- thm:unknot / "conj:unknot" in the paper source are draft-grade (label inconsistencies,
  terse AC4/AC5-commutation argument); do not build on them without independent audit.
