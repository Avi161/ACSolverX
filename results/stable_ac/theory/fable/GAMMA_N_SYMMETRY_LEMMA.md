# Lemma — γ_N and the full defect histogram are invariant under rotation, inversion, and
relator permutation (fable line, 29-07-2026)

Claim addressed: canonicalization soundness for all γ_N censuses/dedup on this line (used
by R1d). Status: proof below + independent computational confirmation (advisor's
implementation reproduced both codex histograms and verified invariance on AK(3)/orbit-2);
adversarial audit still to be run on the written proof.

**Lemma.** Let P = ⟨g₁..gₙ | w₁..w_m⟩ be as in the Neuwirth setting (exact nonempty cyclic
words). Each of the following operations induces a bijection of compatible rotation
systems preserving the surface defect pointwise; hence the full defect histogram, the
compatible count, and γ_N are unchanged:
(i) cyclic rotation of any wⱼ; (ii) replacing any wⱼ by wⱼ⁻¹; (iii) permuting the
relators.

**Proof.** In each case we exhibit a germ-preserving bijection β of the dart set E
intertwining the structure: β A β⁻¹ = A′, β B β⁻¹ = B′, ν′∘β = ν. Conjugation by such a β
maps compatible C′ (for the new data) to compatible β⁻¹C′β... equivalently C ↦ βCβ⁻¹ maps
the old compatible set bijectively onto the new (compatibility C_{τv} = B C_v⁻¹ B is
preserved because β intertwines B and preserves germs, and τ acts on germs only), and the
defect |A| − |C| + 2L − |AC| is preserved because cycle/orbit counts are invariant under
simultaneous conjugation.

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

**Non-invariances (for contrast, all evidenced in the corpus):** AC1 multiplication (codex
two-line counterexample: γ_N jumps 0→1), Aut(F₂) images (relabel changes words
arbitrarily), and free/cyclic REDUCTION (the exact complex changes: states 23, 24 of the
P25 path have A-loops exactly until reduced). The canonical key for censuses is therefore
the lex-min over rotations × inversions × relator permutations, computed on exact
(unreduced) words — reduction is a separate, recorded step.
