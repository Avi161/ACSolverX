# R1c — Synchronized planarity for 3-connected supports at arbitrary rank (AUDITED)

Status: adversarially audited 29-07-2026 — verdict REPAIRABLE, no counterexample found
(referee ran exhaustive rotation-system enumeration over five 6-germ instances, 750k+
systems, every predicted count confirmed; plus a 2-cut control confirming (H2) is
load-bearing). The five required repairs are incorporated below, marked [R1]–[R5].
Independent calibration point: the T³ presentation (`xyXY`,`yzYZ`,`zxZX`) has octahedral
(3-connected planar) support, factorial census 216 rotations, minimum genus 0 with
EXACTLY 2 accepting orders — the two Whitney reflections, matching the count 2·∏m_uv! = 2. Claim addressed: infrastructure for deciding thickenability (γ_N = 0)
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

  (H1) G_A connected ([R5] redundant given (H2): S connected ⇒ G_A connected; kept for
       readability);
  (H2) S is 3-connected (so 2n ≥ 4, min degree ≥ 3);
  (H3) S planar.

[R4] Scope note: Theorems R and P below are pure rotation-system statements and need no
balance. The BRIDGE "γ_N = 0 ⟺ orientably thickenable" (lit_AK3_NEUWIRTH.md Thm 2) is
proved there for balanced presentations with connected link; use the bridge only on
balanced states (all intended stable-class targets are balanced).

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

[R1] **Digon-bijection lemma** (an unproven substep in the K₄ source, now closed): the
subembedding consisting of u, v and the m = m_uv parallel uv-edges (m ≥ 1, connected) has,
by Euler, exactly m complementary regions; its boundary walks alternate u, v so each has
≥ 2 edge-sides, and with 2m sides over m faces each face has EXACTLY 2; a face bordered
twice by one edge would make that edge a bridge (impossible for m ≥ 2; for m = 1 the
single region trivially borders one gap at each endpoint). Hence every complementary
region is a digon whose closure contains exactly one angular gap at u and one at v —
regions and gaps are in bijection.

Fix a spherical embedding and a support pair {u,v} ∈ E(S). The parallel uv-bundle divides
S² into m_uv regions. By (H2), S − {u,v} is connected (vertex deletion, incident edges
removed) and nonempty; the plane subgraph induced on the other 2n − 2 germs is connected,
disjoint from the closed bundle, hence lies in ONE complementary region R. Any edge from
u to a germ w ∉ {u,v} has interior avoiding all vertices and the bundle arcs; being
connected it stays in one region, and it accumulates at w ∈ R, so it lies in R. By the
digon-bijection lemma, R meets exactly one angular gap at u and one at v; hence all
non-uv darts at u (resp. v) lie in that single gap: the P_uv-darts form one cyclic
interval at both endpoints — (1). All regions other than R are empty digons; reading
their boundaries gives the endpoint reversal — (3). [R5] Delete all but one representative
of each class (deletion, NOT graph contraction — contraction would merge u and v; the
macro order is representative-independent by (1)): a spherical embedding of the simple S,
which is cellular since S is connected; Whitney (Mohar–Thomassen form: a 3-connected
planar simple graph has exactly two spherical rotation systems, mutual vertex-wise
reversals) gives (2).

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

Under (H1)–(H3), fixing one of the two macro-reflections loses no compatible solutions:
C′_v := C_v⁻¹ gives C′_{τv} = (B C_v⁻¹ B)⁻¹ = B C_v B = B (C′_v)⁻¹ B, preserving (2.1) and
the genus while flipping the Whitney reflection. [R3] At each germ, fix an ARBITRARY
linear cut of the cyclic macro-rotation to define the block offsets b_{v,u} (an embedding
supplies only cyclic orders; changing the cut shifts every slot at that germ by one
constant, uniform over its darts, and is absorbed by the enumerated phase s_g). With slot
maps built from the cut macro-order and per-class ranks as in (4.2), Lemma 4.1 holds per
generator: compatibility ⟺ one phase s_g ∈ Z/deg(g⁺) per generator satisfying (4.3) for
every B-transposition. Lemma 4.2 holds verbatim: H_{A,B} is 2-regular with components =
the m relator cycles. Theorem 4.3's seed-rank propagation is unchanged per cycle.
[R2] Decision cost: enumerate ∏_g n_g joint phase tuples; per tuple and per relator cycle,
seed-propagate (cost ≤ (max class size)·(cycle length) per cycle); then COMBINE one
retained assignment per cycle under global per-class all-different — worst case
∏_cycles (#retained per cycle) ≲ N^m joint checks. Polynomial for BOUNDED m (balanced
presentations of bounded rank; the intended n = m = 3 targets); the earlier "≪ 10⁶ for
n = 3, N ≤ 40" claim is withdrawn — the phase product alone is ≈ 2.4·10³ and the honest
worst-case bound is phases × N^m ≈ 10⁸–10⁹ elementary steps, still trivially machine-
checkable per instance but not "≪ 10⁶". Practical instances prune far below the bound
(most seeds fail to close).

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

## R1c-v2 (next iteration, sketch — motivated by rank-3 harvest round 1)

Empirical driver: in the first direct stable-move harvest (roots AK(3)+z, P25+z), ~100% of
harvested states are out of scope — the z-germ pair {z⁺, z⁻} is a 2-cut (or has degree
< 3) in almost every reachable support, because a freshly adjoined generator appears in
few relators and a length-priority search avoids z-entangling growth. Two responses:

1. **Theory (the real fix): cut-scheme extension.** Generalize Theorem 5.2's bridge
   machinery from K₄−e to arbitrary 2-cuts: for a support S with a 2-cut {a,b}, the
   {a,b}-bridges (each bridge = a 2-connected component of material between the poles)
   admit a cyclic bridge order at a, reversed at b (Lemma 5.1's argument is
   bridge-generic); each nontrivial bridge recursively carries its own scheme; trivial
   bridges (parallel central edges) carry the cut parameter. An SPQR-tree recursion
   (R-nodes: 3-connected pieces via Theorem R; P-nodes: parallel/dipole schemes with cut
   choices; S-nodes: cycles via the C₄-style unique scheme) covers ALL connected loopless
   supports — this is the in-house constructive version of general Synchronized
   Planarity, with the phase/rank propagation layered on the composed slot schemes.
   Draft-and-audit as the next theory block; the K₄−e case is the template and the
   n = 2 regression anchor.
2. **Search (the cheap fix): z-entangling priorities.** Bias the rank-3 harvest toward
   states where z occurs ≥ 3 times per sign (substitute-into-both-relators prefixes);
   raise the per-relator cap for rank-3 roots grown from length-25 states (cap 15 chokes
   the P25+z root: its queue exhausts at 93 pops).
