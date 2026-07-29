# R1e — Disconnected-link thickenability (Theorem D), decomposition, and the 382-state bucket

STATUS: AUDITED — ac-advisor verdict REVISE reconciled (ledger at the end), then
independent adversarial audit returned REPAIRABLE with three required repairs (F1
mis-citation, F2 cross-check construction, F3 novelty/naming) — ALL APPLIED in this
revision, together with the recommended items F4–F8 (audit ledger at the end). The
audit's numeric checks confirmed the full Corollary-Z histogram identity on the AK3+z
root bin-by-bin ({4:724, 6:14882, 8:55438, 10:15356}, rank-3 vs rank-2 censuses equal),
the standard ("x","y","z") defect 0 with naive-formula illegal value −4, and the
straddle example. Theorem D, Lemma S, Corollary Z, Corollary D3 may now be cited as
established MACHINERY of this line (modulo the explicitly flagged external dependency:
Lackenby Thm 1.3 [unverified this session] wherever the positive-direction consequence
chain is invoked, and the GAMMA_N_SYMMETRY_LEMMA audit-pending flag noted at Corollary
Z).

Claims addressed (per FRAMING.md tags): Theorem D, Lemma S, Corollary Z are MACHINERY
(decision criteria for exact complexes). The application bears on **stable
AC-triviality of AK(3)** in the positive direction (via the master equivalence and
Lackenby arXiv:2606.06122 Thm 1.3, FLAGGED [unverified this session — full text
proxy-blocked; three agreeing secondary sources]); negatives close exact tested
realizations only and say nothing about AK(3) itself (route ceiling,
R1_THICKENABILITY_TRANSFER.md).

Dependencies: the occurrence dictionary, involutions A and B, compatible rotations C,
Lemma 1 (Euler dictionary), Theorem 2 (connected-link criterion) and Corollary 3 of the
codex re-proof `lit_AK3_NEUWIRTH.md` (scratchpad copy; framework summary committed in
R1_IMPLEMENTATION_SPEC.md §2). Notation: |Q| = number of
cycles of a permutation Q including 1-cycles; products act right-to-left; the UNHALVED
defect is defect(C) = |A| − |C| + 2L(C) − |AC| and γ_N = min_C defect(C)/2. NOTE ON
UNITS: `gamma_N_factorial_n` returns `minimum_defect` = 2·γ_N (unhalved); every test
must pin this convention.

## Setting — scope is BALANCE-FREE

P = ⟨g₁,…,gₙ | w₁,…,w_m⟩ with every wⱼ a nonempty cyclic word and every gₖ occurring in
at least one word; K_P the exact word-realized one-vertex presentation complex (no free
or cyclic reduction, no identification of repeated occurrences). Balance (m = n) is NOT
assumed anywhere in Lemma L0, Theorem D, Lemma S, or Corollary Z: the proofs of Lemma 1
and of both directions of Theorem 2 in `lit_AK3_NEUWIRTH.md` never use balance (checked
line by line — balance enters that note only in Corollary 3's χ = 1 computation and the
balanced-case transitivity remark). This matters because Lemma S applies Theorem D to
wedge summands P_ℓ that are in general NOT balanced even when P is. ERRATUM
CROSS-REFERENCE: R1C_V2_CUT_SCHEMES.md §1 Scope note [R4] says the Theorem-2 bridge is
proved "for balanced presentations with connected link; use it only there" — that
restriction on BALANCE was conservative packaging, not mathematical necessity; erratum
E5 appended there points here. The CONNECTIVITY restriction was real and is what
Theorem D removes.

Darts E (|E| = 2·total length), B the tube involution, A the corner involution
(fixed-point-free — a 1-letter relator z contributes the single legal corner (h₀ d₀),
h₀ ≠ d₀; on that component A = B, which breaks nothing below), C a compatible rotation:
one cycle per germ (|C| = 2n), the negative-end cycle the B-reversal of the positive-end
cycle. The link graph Λ(P) has the 2n germs as vertices and one edge per A-corner.
Theorem 2 of `lit_AK3_NEUWIRTH.md` assumes Λ(P) connected; this note removes that
hypothesis. (The `MIN_RELATOR_LENGTH` gate at `neuwirth_rank_n.py:542` and the
connected-link gates are SOLVER fail-closed boundaries, not hypotheses of the proofs;
`classify_cut_support` has no short-relator gate, consistent with R1C_V2 §8.1 item 8.)

**Lemma L0 (component count is C-independent).** The orbits of ⟨A, C⟩ on E coincide
with the dart-preimages of the connected components of Λ(P), for every compatible C.
Hence L(C) = L(P) := #components of Λ(P), independent of C.

*Proof.* Each cycle of C permutes exactly the darts at one germ transitively (one cycle
per germ, by construction). So the ⟨C⟩-orbits are the germ classes, and adjoining A
merges germ classes exactly along the edges of Λ(P). ∎

## Theorem D (disconnected-link Euler criterion)

**Theorem D.** Let P be as above (Λ(P) with L ≥ 1 components; connectivity NOT assumed;
balance NOT assumed). Then K_P embeds in an orientable PL 3-manifold if and only if
there is a compatible C with

  defect(C) = |A| − |C| + 2L − |AC| = 0,

equivalently every component of the rotation surface Σ_C is a sphere; i.e. K_P is
orientably thickenable ⟺ γ_N(P) = 0 with the general (2L-term) defect.

*Proof — necessity.* Suppose K_P is PL embedded in an orientable 3-manifold (if K_P
meets the boundary, push it into the interior first — audit note F7). Take a small
regular ball R about the unique vertex, transverse to the incident cells;
F = K_P ∩ ∂R is a copy of Λ(P) embedded in the single oriented 2-sphere ∂R, its L
components disjoint. The sphere orientation induces a cyclic order at every germ
vertex; the derivation that these orders form a compatible C (transport through an
oriented neighbourhood of each generator 1-cell reverses the transported list, giving
the B-reversal) is verbatim the per-generator-handle argument in Theorem 2's necessity
proof: it is local to one 1-handle at a time, uses only the single global orientation
of ∂R, and never uses connectivity of F.

Genus count, per component. CAUTION (this is where connectivity mattered in Theorem 2's
one-line Euler finish): for L ≥ 2 the complementary regions of the union F ⊂ ∂R need
not be discs — a component nested inside a region bounded by another turns that region
into an annulus or worse — so |C| − |A| + #regions = 2 is FALSE in general and the
union's face count must not be used. Instead, fix a component F_ℓ and DELETE the other
components from the sphere. Deletion does not change C|_ℓ, for the elementary local
reason that the cyclic order induced at a germ vertex of F_ℓ involves only the darts of
F_ℓ itself — no citation needed (audit repair F1: an earlier revision cited R1C_V2
Lemma 2.1 here, which is a different statement — restriction of a spherical rotation of
a connected ambient graph — and would be circular in this position; the correct content
is this one-line locality observation). Now F_ℓ is a CONNECTED nonempty compact graph
embedded in S². By Alexander duality in S², H̃₁(S² ∖ F_ℓ) ≅ H̃⁰(F_ℓ) = 0, so every
complementary component U of F_ℓ alone is an open subsurface of S² with trivial first
homology. Such a U is an open disc (audit item F5, connective steps): U is open in the
connected S² and proper (F_ℓ ≠ ∅), so U is noncompact (a compact open subset would be
clopen, forcing U = S²); an open planar surface has free π₁, so H₁(U) = 0 forces
π₁(U) = 1; and a simply connected noncompact surface is homeomorphic to ℝ². The
embedding of F_ℓ alone is therefore CELLULAR, so its rotation surface — the
⟨A,C⟩-orbit component Σ_{C,ℓ} of Lemma 1, by the Heffter–Edmonds correspondence — is S²
itself: genus 0. (Isolated germs cannot occur: every generator occurs, and every dart
lies in exactly one A-corner, so every germ has degree ≥ 1.) This holds for every ℓ, so
defect(C) = 2·Σ_ℓ q_ℓ = 0 by Lemma 1. ∎(necessity)

*Proof — sufficiency.* Let C be compatible with defect(C) = 0, i.e. every component of
Σ_C a sphere. Build the 0-handle H⁰ ≅ B³ and orient ∂H⁰. Embed the components
F_1,…,F_L of Λ(P) in ∂H⁰ disjointly: pick pairwise disjoint round discs
D_1,…,D_L ⊂ ∂H⁰. The rotation surface Σ_{C,ℓ} is by construction an ORIENTED closed
genus-0 surface in which F_ℓ sits cellularly realizing C|_ℓ; choose an
orientation-preserving PL homeomorphism Σ_{C,ℓ} → S²_std, delete an open complementary
face disc, and shrink the image into int(D_ℓ) ⊂ ∂H⁰ matching orientations. This
realizes C|_ℓ exactly (no reflection case-split is needed: orientation-preserving
transport of an oriented realization realizes the same rotation), and every component
realizes its prescribed rotation with respect to the SAME global orientation of ∂H⁰.
Nesting is immaterial: the D_ℓ are disjoint, and no step below reads the
complementary-region structure of the union.

From here Neuwirth's construction, as re-proved in `lit_AK3_NEUWIRTH.md` (sufficiency
of Theorem 2), applies verbatim; the three touch points where disconnectedness could in
principle enter, and why it does not:

1. *Vertex piece.* Cone the corner pieces of F to an interior point of H⁰. The cone
   over a disconnected graph from one point is connected and is exactly the star of the
   single vertex of K_P (whose vertex link IS Λ(P), disconnected or not). No face
   structure of the union is used.
2. *1-handles.* For each generator g, the discs D_g⁺, D_g⁻ around its two germ vertices
   are disjoint (whether or not the germs lie in different components — the straddling
   case is allowed here), and the orientable 1-handle H¹_g is attached ABSTRACTLY along
   them with the reversed page book. The page-book/orientation agreement is exactly the
   compatibility condition at g — a per-generator condition independent of components.
   W is built abstractly by handle attachment; there is no ambient sphere that nesting
   could obstruct. [Reply to the codex caution "the two B-pipes may also couple
   rotations belonging to different link components" (lit_AK3_SYNCHRONIZED_PLANARITY
   fail-closed note): that coupling is a constraint on ENUMERATING compatible C — which
   Theorem D takes as given — not on this construction; and under the no-straddle
   hypothesis of Lemma S it cannot occur at all.]
3. *2-handles.* The attaching curves λ_j are traced through corner arcs (each contained
   in a small neighbourhood of its A-edge, inside whichever region of ∂H⁰ is adjacent
   to that corner) and page arcs through the 1-handles. Pairwise disjointness and
   simplicity are local properties of these arcs (distinct darts, distinct corners,
   distinct pages) and hold verbatim; this includes the 1-letter-relator curve (one
   corner arc + one page). Traversing λ_j meets the generator handles in the occurrence
   order and signs of w_j, so the embedded polyhedron is the exact K_P.

W = H⁰ ∪ (1-handles) ∪ (2-handles) is a compact orientable PL 3-manifold with
K_P ⊂ int(W) — for the interiority, make the standard choice that the 2-handle
attaching annuli S¹ × [−1,1] cover the partial 2-cells' intersection with the
handlebody boundary (corner-arc bases and page free-edges), exactly as in the connected
case (audit note F8). For the regular neighbourhood: K_P is a compact polyhedron in the
interior of the PL 3-manifold W, so a regular neighbourhood N of K_P in W exists with
N ↘ K_P by the PL regular-neighbourhood theorem (Rourke–Sanderson, *Introduction to
Piecewise-Linear Topology*, Ch. 3). No connectivity input, no hand-built retraction. ∎

Remark (why Theorem 2 needed L = 1). Only for the one-line Euler finish
|C| − |A| + |AC| = 2 in necessity, which reads |AC| off the union's face count — valid
only when the union is connected (and then automatically cellular by the same Alexander
argument). The per-component argument replaces it; the handle construction never needed
connectivity. The codex fail-closed caution ("relative nesting in the common sphere is
not recorded by the component rotations") is about CAPPING complementary regions;
the construction CONES them, and cones exist for regions of any topology.

Remark (boundary connectivity — where nesting DOES matter, and the ⟨AC,BC⟩ audit).
The orbits of ⟨AC,BC⟩ trace ∂N-components in the CONNECTED-link balanced setting. For
L ≥ 2 with no straddling generator, A, B, C all preserve link components, so
⟨AC,BC⟩-orbits are confined within components and transitivity is IMPOSSIBLE — yet
γ_N = 0 states with connected ∂N exist (the standard ("x","y","z") has ∂N ≅ S²: ∂N
assembly merges component boundaries through the shared 0-handle in a nesting-dependent
way the per-component combinatorics do not track). Consequence for machinery: the
transitivity audit (AuditContradiction) is RESCOPED to L = 1; an L ≥ 2 witness checker
must check compatibility and per-component Euler only. This is an implementation
CONTRACT, not just prose: `witness_check_n.py` refuses L ≠ 1 and would spuriously
quarantine every legitimate L ≥ 2 positive; the new module ships its own L-general
checker (new file, existing code untouched).

## Lemma S (wedge decomposition under no-straddle)

Say a generator g *straddles* if its two germs g⁺, g⁻ lie in different components of
Λ(P). (Example: relator `xy` alone — components {x⁻,y⁺}, {y⁻,x⁺}, both generators
straddle.)

**Lemma S.** Suppose no generator of P straddles. Then:
(i) each relator's corner edges lie in a single component of Λ(P): the corner e_i joins
ν(h_i) to ν(d_{i+1}); since B(d_i) = h_i and ν(B·) = τν(·), the germ pair
{ν(d_i), ν(h_i)} = {g⁺, g⁻} for g = |a_i|, so consecutive corners e_{i−1}, e_i meet the
two germs of one generator — the same component by no-straddle; induct around the
cyclic word;
(ii) hence relators and generators partition by component;
(iii) K_P = K_{P_1} ∨ … ∨ K_{P_L} (wedge at the vertex), where P_ℓ is the presentation
on the generators and relators of component ℓ, and Λ(P_ℓ) = Λ_ℓ is connected;
(iv) compatible rotations for P are exactly tuples of compatible rotations for the P_ℓ
(the free datum — one cyclic order per generator — is partitioned by (ii)), and defect
is additive across components (Lemma 1 is a per-component statement), hence

  γ_N(P) = Σ_ℓ γ_N(P_ℓ),

and K_P is orientably thickenable ⟺ every K_{P_ℓ} is — by Theorem D applied to P and
to each P_ℓ; each P_ℓ has connected link, but P_ℓ need NOT be balanced, which is why
Theorem D's balance-free scope is load-bearing here. ∎

(For the record, in the 382-state application every summand IS balanced anyway:
(u,v) on {x,y} and (z) on {z}.)

## Corollary Z (exact defect-HISTOGRAM identity under plain stabilization)

Let P = (w_1,…,w_m) and P⁺ = (w_1,…,w_m, z) with z a fresh generator (exact AC-move
image; AC4 in the project convention). Both z-germs carry exactly one dart, so the
z-component's compatible rotation is unique (empty free datum) and the compatible sets
of P and P⁺ are in canonical bijection C ↔ C⁺. For corresponding rotations:
|A|⁺ = |A| + 1, |C|⁺ = |C| + 2, L⁺ = L + 1, |AC|⁺ = |AC| + 1, hence

  defect⁺(C⁺) = defect(C)  identically.

So the ENTIRE defect histogram — not just the minimum — is preserved:
γ_N(P⁺) = γ_N(P), and the full multiset of defects matches bin by bin. The same holds
for relator z⁻¹ (relator inversion preserves the full defect histogram —
GAMMA_N_SYMMETRY_LEMMA.md; FLAG inherited per audit item F6: that lemma's own
adversarial audit is still pending, though the R1e auditor hand-verified the inversion
bijection including the load-bearing 1-corner case N = 1). Consequently γ_N of the
EXACT complex is invariant under exact stabilization AC4 and destabilization AC5 (legal
exactly when the last relator is z^{±1} and z occurs nowhere else — precisely the
1-edge-component shape). Novelty rescoped (audit repair F3): this is the first
invariance of γ_N under the STABILIZATION moves AC4/AC5; invariance under relator
inversion (AC1) is already GAMMA_N_SYMMETRY_LEMMA.md; γ_N is NOT invariant under
relator multiplication AC2 (the codex 0→1 counterexample) and is not claimed invariant
under general AC composites. Machinery claim only.

Independent cross-check (thickenability half WITHOUT Theorem D — rewritten per audit
repair F2, whose original "ball neighbourhood of the vertex on ∂N / meridian disc"
phrasing was unsound since the vertex lies in int(N)): suppose K_P thickens, and take a
regular neighbourhood N, so N ∖ K_P ≅ ∂N × [0,1) (regular-neighbourhood collar of the
complement). Choose an arc α from the vertex to ∂N with α ∩ K_P = {vertex}: start with
a short radial arc inside a small vertex ball, missing the 1-dimensional link of the
vertex in K_P, then follow the collar to ∂N. Attach an external 3-ball to N along a
disc of ∂N met by α, and realize the fresh z-loop as α · (an arc through the external
ball) · (a push-off of α)⁻¹, with its spanning 2-disc a thin band along the doubled arc
capped inside the external ball. N ∪ (band thickening) ∪ (external ball) is an
orientable thickening of K_{P⁺}; conversely K_P ⊂ K_{P⁺} restricts any thickening. So
thickenable(P⁺) ⟺ thickenable(P) by elementary means, agreeing with the Theorem-D route
— a consistency check on Theorem D itself.

## Corollary D3 (π₁ = 1 balanced consequence, disconnected link allowed)

Under Theorem D's hypotheses, if additionally P is balanced and π₁(K_P) = 1, and some
compatible C has defect 0, then the regular neighbourhood N of K_P is a 3-ball, and P
is classically AC-trivializable. [Chain: Corollary 3 of `lit_AK3_NEUWIRTH.md` used only
N ↘ K_P, χ(K_P) = 1, π₁ = 1, duality, and surface classification — no link
connectivity; Theorem D supplies N. The transitivity clause of Corollary 3 is NOT
extended (see the boundary remark above): ∂N-connectivity here is derived
homologically, not combinatorially. Final step is Lackenby arXiv:2606.06122 Thm 1.3,
FLAGGED [unverified this session]. Any positive result quoted from this corollary must
carry that flag.]

## Application: the round-2 disconnected bucket decides through 382 rank-2 pairs

Empirical facts (advisor-verified independently, to be re-verified by the committed
implementation): the round-2 harvest has 11,273 canonical states; the 382 gated
"disconnected link" ALL have exactly 2 components, NO straddling generator (x±, y± form
one component in all 382), third relator EXACTLY `Z`, and the clean shape
(u(x,y), v(x,y), Z) with z occurring exactly once. By Lemma S + Corollary Z each state
decides through its rank-2 pair:

  γ_N(u, v, Z) = γ_N(u, v),

and the joint rank-3 census size EQUALS the rank-2 census size (the z-germs have degree
1, contributing a factor (1−1)! = 1), so joint-vs-split cross-validation is free
wherever the rank-2 census runs at all.

Provenance (CORRECTED after advisor measurement — root histogram is 85 from AK3+z, 297
from P25+z): every bucket state lies in the exact AC-orbit of its harvest root.
- For the 85 AK3+z-rooted states the chain is: AK(3) →AC4→ AK3+z →round-2 walk (exact
  rank-3 AC moves)→ state.
- For the 297 P25+z-rooted states the chain additionally uses the doubly
  replay-verified 53-move classical AC path AK(3) ↔ P25 (R1_EQUIVALENCE_AND_RECON.md;
  p25_path_states.json): AK(3) →53 moves→ P25 →AC4→ P25+z →round-2 walk→ state. That
  path is a SEPARATE certificate and is cited, not assumed.
Then AC1-inversion of the third relator (Z → z; unconditional — all 382 have `Z`;
project convention: AC1 = invert, AC2 = multiply) followed by AC5 destabilization gives
(u,v).

**Lemma P (canonicalization is an AC composite — audit repair F4).** The canonical
representative of a state (lex-min over relator rotations × inversions × relator
permutations, on exact words) is AC-equivalent to every exact realization in its class:
rotation of a cyclic word is conjugation by its leading letter (AC3), inversion is AC1,
and a transposition of two relators (a, b) is the explicit 6-move composite

  (a, b) →AC2 (ab, b) →AC1 ((ab)⁻¹, b) = (B A, b) →AC2 (BA, bBA) = (BA, A)
  →AC1 (BA, a) →AC2 (BAa, a) = (B, a) →AC1 (b, a),

using only inversion and right-multiplication (A = a⁻¹, B = b⁻¹; free reduction is
Lackenby's move (0)). General permutations are products of transpositions. ∎

Hence membership is UNCONDITIONAL for the whole bucket: every harvest state was
generated by applying legal rank-3 AC moves (the generator applies `ac_words` moves
directly; round-1 replay sample 305/305 exact), canonicalization is an AC composite by
Lemma P, and the destabilization chain above is stable-AC. So every (u,v) is a **rank-2
member of AK(3)'s STABLE class** — reached through rank-3 walks that may have entangled
z at intermediate states, so (u,v) need not lie in AK(3)'s classical AC-component.
Novelty claim (narrowed): these are the first rank-2 stable-class members of AK(3)
produced by a DIRECT STABLE-MOVE-SPACE SEARCH; the codex line's one-stabilization
compression corridor (AK3_RANK3_COMPRESSION.md, 2026-07-24) produced rank-2
stable-class members earlier by a proved corridor — a different, complementary route
(cited).

Replay caveat (hit protocol): the harvest's `parent`/`move` fields are NOT a replayable
chain (the round-2 frontier is keyed on exact words while parents are recorded as
canonical keys, so the recorded parent's exact realization need not be the exact parent
the move was applied to). This does not weaken membership (previous paragraph), but any
SPHERICAL hit must additionally produce an explicitly reconstructed AC1–AC5 move list
from AK(3) to (u,v) plus a full replay — the certificate standard for a headline claim
— before any claim is made. Group check per hit: TC certificate (index 1) on (u,v);
sampled TC on non-hits.

Interpretation matrix:
- ANY (u,v) with γ_N = 0 ⇒ (u,v) thickenable ⇒ [Corollary D3 at rank 2,
  Lackenby-flagged] (u,v) classically AC-trivial ⇒ AK(3) STABLY AC-trivial. This would
  achieve the session goal's AK(3) sub-goal in the stable form — commit and notify
  immediately, after the hit protocol above.
- All 382 NOT_SPHERICAL ⇒ 382 more certified non-thickenable exact realizations
  (extending the corpus into the rank-2 shadow of the stable walk); zero content about
  AK(3) itself; ΣE bookkeeping added for the K4/K4-e/C4-support subset (validated
  e_yield formulas only).
- UNDECIDED_BUDGET rows are named and counted, never folded into "all NO".

## Implementation contract (per advisor reconciliation)

New files only; existing code imported, never modified; no `.venv` on this branch —
plain `python3`. Budgets pinned VERBATIM to round 2 so verdicts join the corpus:
scheme_budget = 200_000, branch_budget = 2_000_000, fallback census cap = 2_000_000;
budget exhaustion → UNDECIDED_BUDGET, never NOT_SPHERICAL; all knobs recorded in the
output summary.

- `experiments/stable_ac/fable/disconnected_split.py`: independent recomputation of
  components/straddle/shape per state (own union-find, not `build_link_n`); projection
  to (u,v) + canon dedup; decision via the round-2 stack (R1c-v2 cut-scheme solver
  first — pre-scan says all 382 pairs are IN_SCOPE — census fallback second); JOINT
  cross-validation calls `gamma_N_factorial_n` DIRECTLY (it is already L-general:
  `defect = nA − nC + 2L − nAC` at `neuwirth_rank_n.py:1038`) — no second census
  implementation that could diverge; an L-general witness checker (compatibility +
  per-component Euler; transitivity audit ONLY when L = 1); output
  `results/stable_ac/fable/disconnected_split_verdicts.jsonl` + summary.
- `tests/fable/test_disconnected_split.py`:
  (a) standard ("x","y","z"): L = 3, defect 0, SPHERICAL — degenerate positive control;
  plus the ILLEGAL-NEGATIVE regression: the naive connected formula (2 for 2L) gives −4
  on this input — proves the 2L term is load-bearing;
  (b) AK3+z root: joint rank-3 census defect = rank-2 census defect = 4 (γ_N = 2,
  matching the codex-certified γ_N(AK(3)) = 2) and verdict NOT_SPHERICAL;
  (c) additivity/histogram identity (Corollary Z: full histogram equality, not just
  min): on the 2 census-affordable bucket states (sizes 86,400 and 967,680) AND on
  synthetic small (u,v,z) stabilizations of tiny pairs — "≥ 3 affordable bucket states"
  is arithmetically impossible at the 2M cap and is not claimed;
  (d) a NON-degenerate disconnected positive: ⟨x,y,z | u₀,v₀,z⟩ with (u₀,v₀) a rank-2
  pair certified γ_N = 0 with nontrivial link (constructed via the rank-2 census) —
  must decide SPHERICAL through the split pipeline AND through the joint census;
  (e) straddle detection on a 2-letter-relator example correctly excludes Lemma S
  (fail-closed);
  (f) clean-shape verification on all 382; the 10 corpus-overlap pairs ASSERTED equal
  to their stored verdicts; codex's independently-certified length-14 rank-2
  stable-class target `YXXYx | YYYYXyyyx` (AK3_RANK3_COMPRESSION.md) added as an extra
  agreement row;
  (g) full bare `pytest` green before any claim.

## What this note does NOT claim

No invariance of γ_N under relator multiplication (AC2) or general AC composites
(inversion AC1 is the symmetry lemma; AC4/AC5 is Corollary Z; nothing more is claimed);
no propagation of any negative along AC paths; no
claim that the 382 pairs exhaust the rank-2 shadow of the stable class (they are what a
budgeted round-2 walk reached); no unconditional use of Lackenby Thm 1.3; no claim
about non-orientable thickenings; no extension of Corollary 3's transitivity clause to
L ≥ 2.

## Advisor reconciliation ledger (REVISE → v2)

1. Provenance corrected: 85 AK3+z / 297 P25+z roots; P25 path certificate cited;
   AC1-naming fixed (project convention AC1 = invert); inversion unconditional (all 382
   have `Z`). 11,273 states (not 11,274).
2. Witness-checker blocker recorded as implementation contract: L-general checker in
   the new module; transitivity audit rescoped to L = 1 (impossibility proof for
   no-straddle L ≥ 2 in the boundary remark).
3. Hand-built proof paragraphs replaced by citations: Alexander-duality cellularity
   (+ R1C_V2 Lemma 2.1) for necessity; Rourke–Sanderson Ch. 3 for N ↘ K_P; sufficiency
   reflection case-split dropped for oriented transport.
4. Scope restated balance-free with the line-by-line check recorded; erratum E5
   cross-filed in R1C_V2_CUT_SCHEMES.md; Corollary Z upgraded to the exact
   defect-histogram identity + elementary K_P ∨ disc cross-check independent of
   Theorem D.
5. Experimental spec fixed: budgets pinned verbatim; `gamma_N_factorial_n` called
   directly; test (c) scoped to the 2 affordable states + synthetics; illegal-negative
   regression, non-degenerate disconnected positive, 10-corpus assertions, codex
   length-14 row added; novelty claim narrowed with codex citation; replay caveat and
   hit protocol added.

## Adversarial audit ledger (REPAIRABLE → repairs applied, this revision)

Auditor: independent adversarial subagent, 29-07-2026 (separate from the ac-advisor).
Verdict REPAIRABLE; findings F1–F9 with F9 the verified-sound inventory (compatibility
locality, Heffter–Edmonds identification, chirality handling incl. straddling
generators, 1-letter-relator dictionary check by machine, Lemma S dictionary
verification against `neuwirth_rank_n.py:684`, Corollary Z increments by hand and
machine, transitivity-impossibility and the ("x","y","z") ∂N ≅ S² witness via
collapsibility, Corollary 3 line-by-line balance/connectivity scan, legality of the
full move chain, and the cited line numbers).

- F1 (REQUIRED) Lemma 2.1 mis-citation in necessity → replaced by the one-line
  locality argument; dependency header pruned.
- F2 (REQUIRED) Corollary Z elementary cross-check was unsound as phrased (vertex is
  interior; no meridian disc) → rewritten with the regular-neighbourhood collar
  argument.
- F3 (REQUIRED) Novelty/naming: rescoped to first AC4/AC5 invariance; AC1 = inversion
  invariance credited to GAMMA_N_SYMMETRY_LEMMA.md, whose own "AC1 multiplication"
  naming slip was corrected in place (numbering-trap note added there).
- F4 (RECOMMENDED) Membership under-scoped → Lemma P added (canonicalization is an AC
  composite; explicit 6-move relator-swap derivation), membership now unconditional;
  replay requirement retained for hit certificates only.
- F5 (RECOMMENDED) "H₁ = 0 ⇒ open disc" connective steps added (noncompactness, free
  π₁ of open planar surfaces, simply connected noncompact surface ≅ ℝ²).
- F6 (RECOMMENDED) GAMMA_N_SYMMETRY_LEMMA audit-pending flag now inherited explicitly
  at Corollary Z's inversion clause (auditor hand-verified the inversion bijection incl.
  N = 1).
- F7/F8 (NOTES) interior-push phrasing in necessity; attaching-annuli choice for
  K_P ⊂ int(W) made explicit.
