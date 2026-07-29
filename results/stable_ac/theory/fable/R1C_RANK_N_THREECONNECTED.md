# R1c — Synchronized planarity for 3-connected supports at arbitrary rank (DRAFT)

Status: theorem DRAFT (fable line, 29-07-2026) — pending adversarial audit; do not build
on it until audited. Claim addressed: infrastructure for deciding thickenability (γ_N = 0)
of higher-rank states in AK(3)'s stable class; generalizes the codex 4-germ K₄ theorem
(their `AK3_SYNCHRONIZED_PLANARITY.md` Thm 3.1/4.3, whose proofs this draft adapts) to
every rank with 3-connected planar simple support. New content: Claims R1–R4 below; the
phase/propagation layer is theirs verbatim, re-stated at rank n.

## Setting

P = ⟨g₁,…,gₙ | w₁,…,w_m⟩, every wᵢ a nonempty cyclic word, cyclically reduced (hence the
link is loopless), every generator occurring. Exact word-realized complex K_P; occurrence
dictionary D/A/B and germ map ν exactly as in `lit_AK3_NEUWIRTH.md`; compatible rotation
C = one cyclic order C_v per germ with C_{τv} = B C_v⁻¹ B. Link multigraph G_A on the 2n
germs; S = simple support. Assume:

  (H1) G_A connected;
  (H2) S is 3-connected (so 2n ≥ 4, min degree ≥ 3);
  (H3) S planar.

(For n = 2 this is exactly S = K₄. C₄/K₄−e are NOT 3-connected — they remain covered by
the codex special theorems; everything else stays fail-closed.)

## Theorem R (spherical rotation systems, rank n)

Under (H1)–(H3), a rotation system ρ of G_A is spherical iff:
1. (blocks) at every germ u and every support neighbor v, the darts of the parallel class
   P_uv form one cyclic interval of ρ_u;
2. (macro) contracting each class to one edge, the induced rotation of S is one of the two
   reflections of THE planar embedding of S (unique up to reflection by Whitney's theorem,
   S being 3-connected and planar);
3. (reversal) for every class, the linear order of its darts at one endpoint is the
   reverse of the order at the other.
The number of labeled spherical rotation systems is 2·∏_{uv ∈ E(S)} m_uv!.

### Proof of necessity (adapting the K₄ argument; new ingredient = (H2))

Fix a spherical embedding and a support pair {u,v}. The parallel uv-bundle divides S² into
m_uv regions. By (H2), S − {u,v} is connected; the plane subgraph induced on the other
2n − 2 germs is connected and disjoint from the bundle arcs, hence lies in ONE
complementary region R. Any edge from u to a germ w ∉ {u,v} leaves u through an angular
gap and cannot cross the bundle, so it lies in the region containing w, namely R; likewise
at v. Hence all non-uv darts at u (resp. v) lie in the single gap adjacent to R: the
P_uv-darts form one interval at both endpoints — (1). All regions other than R are empty
digons; reading their boundaries gives the endpoint reversal — (3). Contract each class to
one representative (independent of representative by (1)): a plane embedding of S; Whitney
gives (2).

For the count: reflection of a spherical embedding reverses every ρ_u; a macro-rotation of
S with all degrees ≥ 3 (by (H2)) is never equal to its own reversal, so the two
reflections are distinct and there is no overcount: 2·∏ m_uv!.

### Proof of sufficiency

Embed S by its unique embedding (either reflection); replace each simple edge by a narrow
ribbon carrying the labeled members of P_uv in the prescribed linear order (reversed at
the far end); ribbons have disjoint interiors. Faces: each face of S survives, plus
Σ_{uv} (m_uv − 1) empty digons. With V = 2n, E = |E(G_A)|, E_S = |E(S)|, F_S = faces of S:
χ = V − E + (F_S + (E − E_S)) = V − E_S + F_S = 2 by planarity of S. Connected + χ = 2 ⇒
sphere. ∎

## Theorem P (compatible spherical decision, rank n)

Under (H1)–(H3), fixing one of the two macro-reflections loses no compatible solutions
(reflection preserves (2.1), as in the codex §4 argument, verbatim). With slot maps built
from the macro-order and per-class ranks exactly as their (4.2), Lemma 4.1 holds per
generator: compatibility ⟺ existence of one phase s_g ∈ Z/deg(g⁺) per generator with the
modular equation (4.3) for every B-transposition. Lemma 4.2 holds verbatim: H_{A,B} is
2-regular with components = the m relator cycles. Theorem 4.3's seed-rank propagation is
unchanged: enumerate the ∏_g deg(g⁺) joint phase tuples; per phase tuple, per relator
cycle, try each seed rank and propagate uniquely; retain closed consistent assignments;
combine across cycles rejecting rank collisions; require union cardinality m_uv in every
class. Decision cost: O(∏_g n_g · Σ_cycles (max class size) · N) — polynomial for fixed n;
for n = 3 and N ≤ 40 this is ≪ 10⁶ elementary steps.

Fail-closed boundary (inherits all nine codex conditions, plus): any germ of degree < 3,
any 2-cut in S, S non-planar (then NO is immediate for sphericity of ANY rotation — but
report it as NOT_SPHERICAL only after verifying non-planarity by a certified test, else
UNSUPPORTED), disconnected G_A ⇒ UNSUPPORTED.

## Why this matters for the stable hunt

If AK(3) is stably AC-trivial but not AC-trivial, the thickenable states of its stable
class may live ONLY behind rank-changing corridors (the rank-2 slice of the stable class
splits into many classical classes; ours need not contain the thickenable ones). Deciding
rank-3 states is therefore not optional for the stable-direction hunt. Targets once
implemented: z-stabilized/CoV-intermediate variants of the 54 path states and P25
(codex covered such variants of AK(3) only), MMS3(w) members (per-w TC triviality check
first), Lucas's B₃-route 3-generator stages.

## Audit checklist for the reviewer

- Claim 1's "connected subgraph avoiding the bundle lies in one region" — verify no edge
  between two non-{u,v} germs can pinch through the bundle at u or v themselves (it
  cannot: its interior avoids all vertices, and crossing between regions requires meeting
  a bundle arc or passing through u/v).
- Whitney uniqueness needs S SIMPLE and 3-connected — we contract classes first; verify
  the contraction of a spherical multigraph embedding induces an embedding of S (blocks
  give exactly this).
- Reflection-uniqueness of macro-rotations at degree ≥ 3 (used for the factor 2 and for
  "fixing one reflection loses nothing").
- The n = 2 specialization must reproduce the codex K₄ theorem exactly (count
  2·∏ m_uv!).
- Lemma 4.1/4.2/4.3 transfers: check no step of their proofs uses n = 2 beyond notation
  (their H_{A,B} components argument is per-relator, rank-free; their slot-map injectivity
  is per-germ, rank-free).
