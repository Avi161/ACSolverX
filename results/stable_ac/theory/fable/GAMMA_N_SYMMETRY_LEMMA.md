# Lemma — γ_N and the full defect histogram are invariant under rotation, inversion, and
relator permutation (fable line, 29-07-2026)

Claim addressed: canonicalization soundness for all γ_N censuses/dedup on this line (used
by R1d). Status: AUDITED — adversarial audit 29-07 ~13:25 UTC returned SOUND (all three
clauses verified independently including N = 1 and N = 2 edge cases; every cited
non-invariance machine-confirmed; recommended notational repairs F1–F3, F5–F6 applied in
this revision). Machine checks: four presentations × {rotation, inversion, swap,
composite} all bit-identical histograms; multiplication 0→1 counterexample confirmed
(("yxx","y") {0:1} → ("yxxy","y") {2:2}); Aut(F₂) x↦xy non-invariance {0:1}→{0:2,2:4};
reduction non-invariance ("xxX") {0:2} vs ("x") {0:1}.

**Lemma.** Let P = ⟨g₁..gₙ | w₁..w_m⟩ be as in the Neuwirth setting (exact nonempty cyclic
words). Each of the following operations induces a bijection of compatible rotation
systems preserving the surface defect pointwise; hence the full defect histogram, the
compatible count, and γ_N are unchanged:
(i) cyclic rotation of any wⱼ; (ii) replacing any wⱼ by wⱼ⁻¹; (iii) permuting the
relators.

**Proof.** In each case we exhibit a germ-preserving bijection β : E′ → E from the new
dart set to the old, intertwining the structure: β A′ β⁻¹ = A, β B′ β⁻¹ = B, ν∘β = ν′
(audit repair F1: one consistent direction convention throughout; case (ii) below is
stated in exactly this direction). Then C′ := β⁻¹Cβ satisfies C′_{τv} = β⁻¹C_{τv}β =
β⁻¹ B C_v⁻¹ B β = B′ C′_v⁻¹ B′, so C ↦ β⁻¹Cβ maps the old compatible set bijectively
onto the new (audit repair F2: the constraint set is τ-symmetric, so no direction issue
arises), and the defect |A| − |C| + 2L − |AC| is preserved because cycle counts are
invariant under conjugation and L is the orbit count of ⟨A,C⟩ ↦ β⁻¹⟨A,C⟩β. Compatibility
also requires the cycles of C to be exactly the occupied-germ fibers (|C| = #present
germs); this is preserved because ν∘β = ν′ makes β a bijection of germ fibers (audit
repair F3).

(i) Rotation renames occurrence indices cyclically within wⱼ; take β = identity on darts
under the induced renaming: A, B, ν are literally unchanged as permutations of the
renamed set.

(iii) Permuting relators renames occurrences; same as (i).

(ii) Inversion. Write wⱼ = a₁…a_N cyclically; wⱼ⁻¹ = a_N⁻¹…a₁⁻¹, whose i-th occurrence
o′ᵢ carries letter a_{N+1−i}⁻¹. Define β(d′ᵢ) = h_{N+1−i} and β(h′ᵢ) = d_{N+1−i} (darts of
other relators: identity).
- Germs: the departure germ of letter a⁻¹ equals the arrival germ of letter a, so
  ν′(d′ᵢ) = ν(h_{N+1−i}) and ν′(h′ᵢ) = ν(d_{N+1−i}): ν′ = ν∘β. ✓
- B: B′ swaps d′ᵢ ↔ h′ᵢ; β maps this pair to {h_{N+1−i}, d_{N+1−i}}, a B-pair. ✓
- A: the corner of wⱼ⁻¹ between positions i, i+1 pairs {h′ᵢ, d′ᵢ₊₁}; β sends it to
  {d_{N+1−i}, h_{N−i}}, which is exactly the A-pair of the corner of wⱼ between positions
  N−i, N+1−i. Cyclic wrap: the corner (i = N) maps to wⱼ's corner between positions N, 1
  (indices mod N). ✓
Hence A′ = βAβ⁻¹ up to the renaming, and the bijection of compatible systems follows. ∎

**Non-invariances (for contrast, all evidenced in the corpus):** relator MULTIPLICATION
rᵢ → rᵢrⱼ — AC2 in the project convention, which fixes AC1 = invert, AC2 = multiply,
AC3 = conjugate (naming corrected 29-07 during the R1e audit; an earlier revision of this
line called the move "AC1", the numbering-trap the advisor's ground truth warns about)
(codex two-line counterexample: γ_N jumps 0→1, machine-confirmed ("yxx","y") → ("yxxy","y")),
GENERAL Aut(F₂) images (audit repair F5: pure generator relabelings/inversions ARE
histogram symmetries — machine-confirmed x↔y identity — but general images are not:
x ↦ xy sends {0:1} to {0:2, 2:4}), and free/cyclic REDUCTION (the exact complex changes:
states 23, 24 of the P25 path have A-loops exactly until reduced). The canonical key for
censuses is therefore the lex-min over rotations × inversions × relator permutations,
computed on exact (unreduced) words — reduction is a separate, recorded step. Deployment
boundary (audit note F6): the deployed harvest key (`rank3_stable_harvest.canon_relator`)
composes cyclic reduction BEFORE the lex-min; that is sound only under the R1d convention
that the census population consists of the reduced states, which R1d records — keep that
convention documented at every new call site rather than folding reduction into this
lemma's claim.
