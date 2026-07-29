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
