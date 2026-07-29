# R1e — Disconnected-link thickenability (Theorem D), decomposition, and the 382-state bucket

STATUS: DRAFT — pending ac-advisor reconciliation and adversarial audit. Do not cite as
proved until the AUDITED header lands.

Claims addressed (per FRAMING.md tags): the theorem and lemmas are MACHINERY (decision
criteria for exact complexes). The application section bears on **stable AC-triviality of
AK(3)** in the positive direction (via the master equivalence and Lackenby Thm 1.3,
FLAGGED [unverified this session]); negatives close exact tested realizations only and
say nothing about AK(3) itself (route ceiling, R1_THICKENABILITY_TRANSFER.md).

Dependencies: the occurrence dictionary, involutions A and B, compatible rotations C,
Lemma 1 (Euler dictionary), Theorem 2 (connected-link criterion) and Corollary 3 of the
codex re-proof `lit_AK3_NEUWIRTH.md` (scratchpad copy; committed summary of the framework
in R1_IMPLEMENTATION_SPEC.md §2). Notation: for a permutation Q, |Q| = number of cycles
including 1-cycles; products act right-to-left; defect(C) = (|A| − |C| + 2L(C) − |AC|)/2.

## Setting

P = ⟨g₁,…,gₙ | w₁,…,wₙ⟩ balanced, every wⱼ a nonempty cyclic word, every gₖ occurring in
at least one word; K_P the exact word-realized one-vertex presentation complex (no free
or cyclic reduction, no identification of repeated occurrences). Darts E (|E| = 2·total
length), B the tube involution, A the corner involution (fixed-point-free — note a
1-letter relator z contributes the single legal corner (h₀ d₀), h₀ ≠ d₀), C a compatible
rotation: one cycle per germ (|C| = 2n), the negative-end cycle the B-reversal of the
positive-end cycle. The link graph Λ(P) has the 2n germs as vertices and one edge per
A-corner (endpoints: the germs containing the two darts). Theorem 2 of
`lit_AK3_NEUWIRTH.md` assumes Λ(P) connected; this note removes that hypothesis.

**Lemma L0 (component count is C-independent).** The orbits of ⟨A, C⟩ on E coincide with
the dart-preimages of the connected components of Λ(P), for every compatible C. Hence
L(C) = L(P) := #components of Λ(P), independent of C.

*Proof.* Each cycle of C permutes exactly the darts at one germ transitively (one cycle
per germ, by construction). So the ⟨C⟩-orbits are the germ classes, and adjoining A
merges germ classes exactly along A-edges, i.e., along the edges of Λ(P). ∎

## Theorem D (disconnected-link Euler criterion)

**Theorem D.** Let P be as above (link graph Λ(P) with L ≥ 1 components; connectivity
NOT assumed). Then the exact complex K_P embeds in an orientable PL 3-manifold if and
only if there is a compatible C with

  |A| − |C| + 2L − |AC| = 0,

equivalently defect(C) = 0, equivalently every component of the rotation surface Σ_C is
a sphere. In particular K_P is orientably thickenable ⟺ γ_N(P) = 0, where γ_N minimizes
defect(C) over compatible C (the general form of the potential, with the 2L(C) term).

*Proof — necessity.* Suppose K_P is PL embedded in an orientable 3-manifold. Take a small
regular ball R about the unique vertex, transverse to the incident cells; F = K_P ∩ ∂R
is a copy of Λ(P) embedded in the single oriented 2-sphere ∂R, its L components disjoint.
The sphere orientation induces a cyclic order at every germ vertex; the derivation that
these orders form a compatible C (transport through an oriented neighbourhood of each
generator 1-cell reverses the transported list, giving the B-reversal) is verbatim the
per-generator-handle argument in Theorem 2's necessity proof and never uses connectivity
of F — it is local to one 1-handle at a time, and the orientation used is the single
global orientation of ∂R.

Genus count, per component. CAUTION (this is where connectivity mattered in Theorem 2's
one-line Euler finish): for L ≥ 2 the complementary regions of the union F ⊂ ∂R need not
be discs — a component nested inside a face of another turns that region into an annulus
or worse — so |C| − |A| + #regions = 2 is FALSE in general and the union's Euler count
must not be used. Instead, fix a component F_ℓ and forget the others: F_ℓ is a connected
graph embedded in the sphere ∂R with the rotation induced by the global orientation, i.e.
the restriction C|_ℓ of C to the darts of F_ℓ. For a CONNECTED graph, the ribbon surface
built from an embedding's rotation system is the surface of the embedding itself; being
embedded in S² with connected complement-independent data, its ribbon surface Σ_{C,ℓ} is
a sphere: the classical fact used is that a connected graph embedded in S² has its
rotation-system genus equal to 0 (Euler for the component alone: its own complementary
regions IN ITS OWN ribbon surface are the AC-cycles supported on its darts; the
components of Σ_C are exactly the ⟨A,C⟩-orbit surfaces of Lemma 1). Hence every
component of Σ_C has genus 0, so Σ q_ℓ = defect(C) = 0 by Lemma 1. [AUDIT POINT 1: the
claim "connected graph embedded in S² ⇒ induced rotation system has genus 0" is the
standard rotation-system/embedding correspondence for cellular embeddings; for a
non-cellular embedding of F_ℓ in S² (which happens exactly when other components sit in
its faces or when F_ℓ does not fill the sphere), pass to the component alone: an
embedding of a connected graph in S² is isotopic to a cellular one on its own ribbon
neighbourhood — concretely, the ribbon surface of the induced rotation embeds in ∂R as a
regular neighbourhood of F_ℓ, a compact surface with boundary in S², and capping its
boundary circles with discs gives a closed orientable surface of genus 0 because every
compact subsurface of S² has planar genus. This is the precise statement used.]

*Proof — sufficiency.* Let C be compatible with defect(C) = 0, i.e., every component of
Σ_C a sphere. Build the 0-handle H⁰ ≅ B³ with an orientation of ∂H⁰. Embed the
components F_1,…,F_L of Λ(P) in ∂H⁰ disjointly, as follows: pick pairwise disjoint round
discs D_1,…,D_L ⊂ ∂H⁰ and embed F_ℓ cellularly in the interior of D_ℓ realizing the
rotation C|_ℓ with respect to the global orientation of ∂H⁰. This is possible: Σ_{C,ℓ}
is a sphere, so F_ℓ has a cellular embedding in S² realizing C|_ℓ up to global
reflection; deleting an open face disc gives an embedding in a disc; if the realized
rotation is C|_ℓ⁻¹ rather than C|_ℓ, compose with a reflection of D_ℓ. The reflection
choice is made independently per component, so every component realizes its prescribed
rotation with respect to the SAME global orientation. Nesting is immaterial: the D_ℓ are
disjoint, and no step below reads the complementary-region structure of the union.

From here Neuwirth's construction, as re-proved in `lit_AK3_NEUWIRTH.md` (sufficiency of
Theorem 2), applies verbatim; we list the three touch points where disconnectedness
could in principle enter, and why it does not:

1. *Vertex piece.* Cone the corner pieces of F to an interior point of H⁰. The cone over
   a disconnected graph from one point is connected and is exactly the star of the
   single vertex of K_P (whose vertex link IS Λ(P), disconnected or not). No face
   structure of the union is used.
2. *1-handles.* For each generator g, the discs D_g⁺, D_g⁻ around its two germ vertices
   are disjoint (whether or not the germs lie in different components or in nested
   discs), and the orientable 1-handle H¹_g is attached ABSTRACTLY along them with the
   reversed page book. The page-book/orientation agreement is exactly the compatibility
   condition at g — a per-generator condition independent of components. W is being
   built abstractly by handle attachment; there is no ambient sphere that nesting could
   obstruct.
3. *2-handles.* The attaching curves λ_j are traced through corner arcs (each contained
   in a small neighbourhood of its A-edge, inside whichever region of ∂H⁰ is adjacent to
   that corner) and page arcs through the 1-handles. Pairwise disjointness and
   simplicity are local properties of these arcs (distinct darts, distinct corners,
   distinct pages) and hold verbatim. Traversing λ_j meets the generator handles in the
   occurrence order and signs of w_j, so the embedded polyhedron is the exact K_P.

W = H⁰ ∪ (1-handles) ∪ (2-handles) is a compact orientable PL 3-manifold containing
K_P. The regular-neighbourhood refinement (N ⊂ W, N ↘ K_P) also goes through: the
retraction's 0-handle piece cones each complementary region of F ⊂ ∂H⁰ and projects
radially; that projection is defined for regions of any topology (an annular region
radially retracts to the coned graph exactly as a disc does — the cone point is the
same), and the 1-/2-handle pieces are product projections as before. ∎

Remark (why Theorem 2 needed L = 1). Only for the one-line Euler finish |C| − |A| + |AC|
= 2 in necessity, which reads |AC| off the union's face count — valid only when the
union is connected and its embedding cellular. The per-component argument above replaces
it. The handle construction itself never needed connectivity, confirming the codex
fail-closed note's caution was about the face/region bookkeeping ("nesting … not
captured by per-component rotations"), which enters no step of the construction: nesting
changes region topology, and region topology is coned, not capped, in the construction.

Remark (boundary connectivity — where nesting DOES matter). The orbits of ⟨AC, BC⟩ trace
∂N-components in the connected-link balanced setting; for L ≥ 2 the nesting choices in
∂H⁰ genuinely change how ∂N assembles, so no per-rotation transitivity audit is claimed
here. This affects only Corollary-level boundary bookkeeping; for the π₁ = 1 balanced
consequence, ∂N-connectivity is derived homologically (below), not combinatorially.

## Lemma S (wedge decomposition under no-straddle)

Say a generator g *straddles* if its two germs g⁺, g⁻ lie in different components of
Λ(P). (Example: relator `xy` alone — components {x⁻,y⁺}, {y⁻,x⁺}, both generators
straddle.)

**Lemma S.** Suppose no generator of P straddles. Then:
(i) each relator's corner edges lie in a single component of Λ(P) — consecutive corners
of a relator share the two germs of one generator (the corner ending at dep-germ(w_i)
and the corner starting at arr-germ(w_i) meet opposite germs of the same unsigned
generator), which the no-straddle hypothesis puts in one component;
(ii) hence relators and generators partition by component: writing Λ_1,…,Λ_L for the
components, each generator's two germs lie in exactly one Λ_ℓ, and every relator's
letters use only the generators of its component (a letter of g in w_j puts corner edges
at both germs of g into w_j's component);
(iii) K_P = K_{P_1} ∨ … ∨ K_{P_L} (wedge at the vertex), where P_ℓ is the presentation
on the generators and relators of component ℓ, and Λ(P_ℓ) = Λ_ℓ is connected;
(iv) compatible rotations for P are exactly tuples of compatible rotations for the P_ℓ
(the free datum — one cyclic order per generator — is partitioned by (ii)), and defect
is additive across components (Lemma 1 is a per-component statement), hence

  γ_N(P) = Σ_ℓ γ_N(P_ℓ),

and K_P is orientably thickenable ⟺ every K_{P_ℓ} is (by Theorem D applied to P and to
each P_ℓ — each P_ℓ has connected link, so Theorem 2 also suffices for the parts).

*Proof.* (i) is the two-line computation stated; (ii) follows by induction along each
relator's cyclic letter sequence; (iii) is immediate from (ii) — the exact complex is
determined by the per-relator letter data, which splits; (iv): the cyclic-order data at
the germs of component ℓ is exactly the free datum of P_ℓ, compatibility is
per-generator, and |A|, |C|, |AC|, L all split as sums over ⟨A,C⟩-orbits. Minimizing a
sum of independent nonnegative terms minimizes each term. ∎

Note P_ℓ is in general NOT balanced even when P is; Theorem D and Lemma 1 nowhere use
balance (balance enters only at Corollary-3 level). [AUDIT POINT 2: check that the parts
of our bucket ARE balanced anyway — they are: (u,v) on {x,y} and (z) on {z}.]

## Corollary Z (γ_N is inert under exact plain stabilization)

Let P = (w_1,…,w_n) and P⁺ = (w_1,…,w_n, z) with z a fresh generator (exact AC4 image).
The z-component of Λ(P⁺) is the single A-edge z⁻—z⁺ (corner (h₀ d₀) of the 1-letter
cyclic word z); both germs have one dart, so the compatible rotation there is unique and
its component defect is (1 − 2 + 2 − 1)/2 = 0 with |AC|-restriction the single 2-cycle
(d₀ h₀) — a sphere (the boundary of a regular neighbourhood of an unknotted arc… the
combinatorics suffice: Lemma 1). No generator straddles between the old link and the new
component. By Lemma S,

  γ_N(P⁺) = γ_N(P), and K_{P⁺} thickenable ⟺ K_P thickenable.

The same holds for relator z⁻¹ (relator inversion leaves the full defect histogram
invariant — GAMMA_N_SYMMETRY_LEMMA.md). Consequently γ_N of the EXACT complex is
invariant under exact stabilization AC4 and destabilization AC5 (when legal, i.e., the
last relator is exactly z^{±1} and z occurs nowhere else — which is precisely the
disconnected shape with a 1-edge component). This is the first positive AC-move
invariance statement for γ_N in this project (contrast: NOT invariant under AC1;
GAMMA_N_SYMMETRY_LEMMA.md records the symmetry group that IS safe). Machinery claim
only.

## Corollary D3 (π₁ = 1 balanced consequence, disconnected link allowed)

Under Theorem D's hypotheses, if additionally P is balanced and π₁(K_P) = 1, and some
compatible C has defect 0, then the regular neighbourhood N of K_P is a 3-ball, and P is
classically AC-trivializable. [Chain: Corollary 3 of `lit_AK3_NEUWIRTH.md` used only
N ↘ K_P, χ(K_P) = 1, π₁ = 1, duality, and surface classification — no link
connectivity; Theorem D supplies N. Final step is Lackenby arXiv:2606.06122 Thm 1.3,
FLAGGED [unverified this session — three agreeing secondary sources, full text
proxy-blocked]. Any positive result quoted from this corollary must carry that flag.]

## Application: the round-2 disconnected bucket is 382 rank-2 stable-class members

Empirical facts (recomputed independently of the harvest gate; verification script to be
committed with the implementation): all 382 round-2 states gated "disconnected link"
have exactly 2 components, no straddling generator, and the clean shape
(u(x,y), v(x,y), z^{±1}) with z occurring exactly once. By Lemma S + Corollary Z each
such state decides through the rank-2 pair (u,v):

  γ_N(u, v, z^{±1}) = γ_N(u, v).

Provenance: each state lies in the exact AC-orbit of AK3+z (round-2 walk = exact AC
moves), and AC2-inversion (if the relator is Z) followed by AC5 destabilizes it to
(u,v). Hence every (u,v) is a **rank-2 member of AK(3)'s STABLE class** — reached
through rank-3 walks that may have entangled z at intermediate states, so (u,v) need not
lie in AK(3)'s classical AC-component. These are, to our knowledge, the first rank-2
stable-class members produced by a direct stable-move-space search (382 distinct pairs
after canon dedup, total lengths 13–38; 10 already in the previously decided classical
corpus, all NOT_SPHERICAL there).

Group check: rank-3 AC moves preserve the presented group (trivial, from AK3+z), and
⟨x,y,z | u,v,z⟩ ≅ ⟨x,y | u,v⟩, so each (u,v) is a balanced rank-2 presentation of the
trivial group (to be TC-certified per hit; sampled otherwise).

Interpretation matrix:
- ANY (u,v) with γ_N = 0 ⇒ (u,v) thickenable ⇒ [Corollary D3, Lackenby-flagged]
  (u,v) classically AC-trivial ⇒ AK(3) STABLY AC-trivial (it is stably equivalent to
  (u,v)). This would achieve the session goal's AK(3) sub-goal in the stable form —
  commit and notify immediately.
- All 382 NOT_SPHERICAL ⇒ 382 more certified non-thickenable exact realizations
  (extending the corpus into the rank-2 shadow of the stable walk); zero content about
  AK(3) itself; ΣE bookkeeping to be added to the running total.
- UNDECIDED_BUDGET rows are named and counted, never folded into "all NO".

## What this note does NOT claim

No AC1-invariance of γ_N; no propagation of any negative along AC paths; no claim that
the 382 pairs exhaust the rank-2 shadow of the stable class (they are what a budgeted
round-2 walk reached); no unconditional use of Lackenby Thm 1.3 (flag propagates through
every positive-direction statement); no claim about non-orientable thickenings.
