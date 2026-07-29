# R3′ seed — the digon-excess form of sphericity (29-07-2026)

Claim addressed: infrastructure for BOTH directions of the R1 equivalence (find γ_N = 0 in
AK(3)'s stable class / prove none exists). Elementary but organizing; to be adversarially
checked before any load-bearing use.

Setting: balanced 2-generator pair, cyclically reduced words, loopless CONNECTED link
(support ⊆ K₄), N = total letters, darts 2N, |C| = 4, L = 1.

**Lemma D1 (no monogons).** For a loopless link, AC has no fixed points: AC(d) = d would
need C(d) = A(d), but C(d) stays at the germ ν(d) while ν(A(d)) ≠ ν(d). So every face has
length ≥ 2 (in darts; face lengths sum to 2N).

**Lemma D2 (excess form).** Write E(C) = Σ_faces (len − 2) = 2N − 2·|AC| for the
digon-excess. Then the defect is |A| − |C| + 2L − |AC| = N − 2 − |AC| = E(C)/2 − 2, so

    genus-sum(C) = E(C)/4 − 1/2 …  [defect = 2·genus-sum; E = 4 + 4·genus-sum]

i.e. **C is spherical ⟺ E(C) = 4**: all faces are digons except a total excess of exactly
four (four triangles' worth in K₄'s tetrahedral picture: 4 triangles × excess 1 = 4 ✓,
consistent with Theorem 3.1's macro-faces; K₄−e and C₄ distribute the same excess
differently).

Consequently:
- γ_N ≥ 1 (non-thickenable) ⟺ every compatible C has E ≥ 8;
- the AK(3) certificate (γ_N = 2) says every compatible C has E ≥ 12 — the census
  histogram (defect ≥ 4 across all 86,400) is exactly this statement.

**Why this matters.** Sphericity = "the A-edges admit a compatible rotation organizing
them into parallel digon chains with only 4 units of slack." The obstruction to
thickenability is thus a statement about the corner structure of the two cyclic words:
which A-edge classes can be made block-parallel under the B-reversal coupling (2.1). The
R3′ program in this language: find a functional of the corner multiset that (a)
lower-bounds E over ALL compatible C, and (b) has controlled behavior under AC1–AC5 at the
CLASS level. (γ_N itself fails (b) — the codex two-line counterexample. The walls of
R3_INVARIANT_LANDSCAPE.md apply to any candidate; a corner-combinatorial invariant is
outside the four walled families, which is what makes this direction worth keeping alive.)

Adversarial check needed: Lemma D1's germ argument uses ν(C(d)) = ν(d) — true since C
permutes darts within a germ cycle by construction; and looplessness for cyclically
reduced words — a loop would need a corner (u, u⁻¹) which reduced words forbid (checked:
also cyclically at the seam). Both steps elementary; audit welcome.

## Addendum (same day): the obstruction is pure synchronization

The link multigraph of any pair with planar simple support (always true at rank 2:
support ⊆ K₄, and parallel edges never destroy planarity) has UNCONSTRAINED orientable
genus 0 — some rotation system embeds it in S². Therefore γ_N > 0 is caused ENTIRELY by
the B-coupling constraint C_{τv} = B C_v⁻¹ B, i.e. by how the occurrence pairing (the
letter order of the two cyclic words) forces the two ends of each generator handle to
interleave. γ_N is a "constrained genus" / synchronization defect of the word pair.

Consequences for R3′:
- Any candidate obstruction must be a functional of the occurrence pairing (word
  combinatorics), not of the abstract multigraph (which is always planar here).
- Move behavior: AC3 is free (cyclic words); AC1 grafts one relator's corner set into the
  other (link grows by the guest's germ degrees, two junction corners replace two seam
  corners); AC4 adds a two-germ component bridged by a single A-edge. γ_N is known
  non-monotone under AC1 in both directions, so only quotient/aggregate functionals can
  survive the class — a candidate must be tested against move-grafting explicitly.
- Related classical machinery to consult when sources are reachable: Wicks forms / genus
  of words (one-face constrained surfaces — dual to our unrestricted-faces,
  constrained-vertices setting), and quadratic-word genus theory. [unverified this
  session — proxy blocks the literature; flag for the user's Colab session.]

## The AK(2) control (29-07, ~08:45 UTC) — calibrating what "zero hits" means

Experiment: exact-key best-first harvest (1,000 pops, cap 15) from AK(2) =
(`xxYYY`,`xyxYXY`) — a TRIVIAL and provably AC-TRIVIAL class — yielding 1,251 canonical
non-degenerate presentations; fable rank solver: **1,251/1,251 NOT_SPHERICAL** (1
UNSUPPORTED). Also: an exhaustive sweep of ALL cyclically-reduced pairs with relator
lengths 3–4 contains NO trivial-group presentations at all, and its 5,872 spherical pairs
are all non-trivial groups.

Reading: sphericity among non-degenerate class members is ~E-rare in EVERY class,
trivial or not; a trivialized class's guaranteed-thickenable members are its
short/degenerate states (standard itself has length-1 relators — below the gate). So
AK(3)'s accumulated zeros are, so far, indistinguishable from the null model — there is
NO phenomenon yet demanding an obstruction. The falsifiable program:
1. Run the AK(2) control at Colab scale until ΣE ≫ 1. Hits at ~E rate ⇒ null model
   validated end-to-end (and the machinery demonstrably CAN find hits).
2. Run AK(3)'s class at matched ΣE. Zero hits when AK(2) shows the expected rate ⇒ a
   genuine class-level phenomenon ⇒ R3′ gets a concrete target.
3. Search-priority upgrade for all future harvests: best-first by E-DESCENDING (the E
   formula rewards concentrated corner distributions, not shortness — a length-ascending
   harvest under-samples the high-E tail). Adopted into the Colab runner spec.

## Complementarity note (08:50 UTC): codex phase-obstruction proof

Codex just committed `AK3_NEUWIRTH_PHASE_OBSTRUCTION.md` (a17c7bf): a human,
non-factorial proof that the DISPLAYED AK(3) complex is non-thickenable, derived from the
phase equations — their dormant "derive γ_N ≥ 2 structurally" task waking up. Division of
labor from here: codex owns per-realization phase-obstruction proofs; the fable line owns
(a) the experimental control program (AK(2) control, E-priority harvests, Colab scale),
(b) the rank-3 stable-move hunt, and (c) any CLASS-functional obstruction theory (how
phase systems transform under AC1 grafting — the move-level analysis their per-realization
proofs do not touch). Their proof is the natural technique seed for (c): if the
phase-contradiction pattern can be shown stable under the AC1 corner-grafting operation on
some invariant summary of the phase system, that is the R3′ candidate.
