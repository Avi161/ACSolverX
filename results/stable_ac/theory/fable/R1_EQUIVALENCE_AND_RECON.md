# R1 master framing + oracle reconnaissance (29-07-2026)

## The equivalence that makes R1 a complete framing (not a heuristic)

**Observation (AK(3) instance of Lackenby's reformulation).** Let 𝒮 be the stable AC class
of AK(3). Then:

  AK(3) is stably AC-trivial  ⟺  𝒮 contains a thickenable presentation.

(⇐) If P ∈ 𝒮 is thickenable, P presents the trivial group (class of AK(3)) and is balanced,
so by Lackenby arXiv:2606.06122 Thm 1.3, P is classically AC-trivial; hence standard ∈ 𝒮 and
AK(3) ~st standard. (⇒) If AK(3) ~st standard, then standard ∈ 𝒮, and the standard
presentation complex is thickenable (it embeds in S³: wedge of circles with n obvious
2-discs). ∎

Consequently the two live directions of this route are exhaustive for the AK(3) sub-goal:
- POSITIVE: exhibit one γ_N = 0 state in 𝒮 (with verified witness + verified membership
  chain) — settles AK(3) stably AC-trivial.
- NEGATIVE: prove NO state of 𝒮 is thickenable — DISPROVES nothing less than the stable AC
  conjecture itself (𝒮 would be a class with no thickenable member, contradicting the
  conjecture via (⇐) applied to the conjectured trivialization). This direction needs a
  class-invariant obstruction (R3′): a quantity invariant under AC1–AC5, nonzero on AK(3),
  zero on standard, forcing γ_N > 0 — subject to the R3 walls. No such invariant is known;
  any progress here is publishable.

Both directions live in one geometry: rotation-system defect over 𝒮.

## Oracle reconnaissance (codex rank solver used as a tested tool; NOT yet independently
confirmed — no result claims until the fable solver confirms)

Inputs and verdicts (exact cyclically-reduced word realizations;
`oracle_verdicts_56targets.json` for the 56 core rows):

- AK(3), orbit-2 sanity: NOT_SPHERICAL (matches their census certificates γ_N = 2, 1).
- P25 (`XYxYXyxYYxyXy`,`YXyyXYxyxYYx`): NOT_SPHERICAL.
- Q (`xxxxyXXYxyXXY`,`YxxyXXYxxyXXYxxyXXY`): NOT_SPHERICAL.
- All 54 states of the doubly-verified 53-move AC path AK(3) ↔ P25: NOT_SPHERICAL.
- MS(3,w₁) = (`XyyyxYYYY`,`XYXyxy`) (length-15 MMS02 partner, AC-equiv to AK(3) per
  Shehper et al. citing MMS — edge itself not yet independently verified): NOT_SPHERICAL.
- 610 distinct short-Aut(F₂)-images (aut words ≤ 3 over σ, ι_x, ι_y, 4 transvections) of
  AK(3)/P25/Q/MS(3,w₁): all NOT_SPHERICAL, zero UNSUPPORTED.

Running total of exact complexes known non-thickenable in/near 𝒮: ~2,755 (codex certified)
+ 666 (fable oracle recon, pending independent confirmation). Zero positives anywhere.

Reading: the thickenable states of 𝒮 (if any) are not within trivial reach; either they
live much deeper (longer words / higher rank / different elimination trees — R1b/R1c), or
there is a structural obstruction awaiting formulation (R3′). Both continuations are live
and INCOMPATIBLE — exactly the portfolio shape the workflow demands.

## Next actions

1. (After ac-advisor reconciliation) build the independent fable solver stack per
   R1_IMPLEMENTATION_SPEC.md; confirm the 666 negatives → then this file's recon section
   upgrades to a certified bounded negative.
2. R1b: per-w triviality-checked neighbor generation (elimination trees; deeper Aut-balls;
   one-ply AC1 neighborhoods of the 56 targets, ≤1,000 states per local run; production
   sweeps → Colab runner spec for the user).
3. R1c: 6-germ (rank-3) synchronized-planarity solver theory — opens the MMS3(w) and
   B₃-route 3-generator neighbor families; novel contribution.
4. R3′: formulate candidate defect lower-bound obstructions; test against the accumulated
   negative corpus; every candidate must be attacked with the R3 walls and the γ_N
   non-invariance counterexample in mind.
