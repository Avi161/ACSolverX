# R3′ step 1 — the non-cancelling AC2 graft calculus (fibration, defect transformation, move-ordering heuristic)

STATUS: DRAFT — time-boxed step-1 deliverable, pending adversarial audit. Claims
addressed: MACHINERY only.

This is the time-boxed step-1 deliverable of the R3′ arc plan
(R3PRIME_DIGON_EXCESS.md, "R3′ arc plan — REVISED per advisor verdict"). Per the
pre-registration recorded there (item 3), the structural yield is expected to be, and
IS, only the per-graft ceiling γ_N(post) ≥ γ_N(pre) − 1 — vacuous as an invariant-
building tool at AK(3) — plus a move-ordering heuristic for harvests. Both are
delivered below; per the plan, steps 2/4 are NOT entered on this basis. Every claim in
this note is machinery about EXACT word-realized complexes; nothing transports any
verdict along AC paths (see §6).

Dependencies (cited, not re-proved): the occurrence dictionary, involutions A and B,
compatible rotations C, Lemma 1 (Euler dictionary) of the codex re-proof
`lit_AK3_NEUWIRTH.md` (scratchpad copy; framework summary in R1_IMPLEMENTATION_SPEC.md
§2); Theorem D and Corollary Z of R1E_DISCONNECTED_LINK.md (AUDITED); the
rotation/inversion/permutation histogram symmetries of GAMMA_N_SYMMETRY_LEMMA.md
(AUDITED); Lemma D1/D2 context of R3PRIME_DIGON_EXCESS.md. Conventions: unhalved
defect(C) = |A| − |C| + 2L(C) − |AC| with γ_N = min_C defect(C)/2; |Q| = number of
cycles including 1-cycles; products right-to-left; `gamma_N_factorial_n` returns
`minimum_defect` = 2·γ_N. Move naming (project convention): AC1 = invert,
AC2 = multiply r_i ← r_i·r_j (i ≠ j), AC3 = conjugate, AC4/AC5 = (de)stabilize,
(0) = Lackenby's free/cyclic reduction.

## 0. Scope — strict, per the time-box

**In scope.** The EXACT AC2 graft

  P = (w_1, …, w_m) → P′ = (w_1, …, w_{i−1}, w_i·w_j, w_{i+1}, …, w_m),  i ≠ j,

in the Neuwirth setting (nonempty exact cyclic words, every generator occurring), with
both w_i =: r_i and w_j =: r_j cyclically reduced and the seam NON-CANCELLING:

  (NC)  last(r_i) ≠ first(r_j)⁻¹  and  last(r_j) ≠ first(r_i)⁻¹.

The first inequality makes the junction J₁ (seam) reduced, the second makes the new
word's wrap reduced; together with cyclic reducedness of r_i, r_j they make r_i·r_j
CYCLICALLY REDUCED as an exact word. Consequently move (0) acts trivially on the graft
image: on this subdomain the exact move AC2 EQUALS the class-relevant composite
(AC2 ∘ (0)), which is how this note complies with the move-(0) formalism required by
the advisor reconciliation (item 1). Rotations of r_i, r_j prior to grafting (exact
cyclic rotation, histogram-safe by GAMMA_N_SYMMETRY_LEMMA.md case (i), no (0) needed)
are treated as part of the move parameters (§4). Full conjugation w r w⁻¹ is NOT in
scope (it always creates an A-loop until reduced; it is safe only as (AC3 ∘ (0)) and
is not analyzed here).

**Out of scope: the cancelling seam.** If (NC) fails, the exact concatenation contains
a corner (u, u⁻¹). Two independent reasons for exclusion: (a) locality death at the
class level — the class-relevant move is (AC2 ∘ (0)), and the reduction cascade deletes
occurrence pairs, possibly deep into r_i and r_j and around the wrap; the dart-set
inclusion E ⊂ E′ on which everything below rests simply does not exist, so no
restriction map is available. (b) Even at the exact level, the corner (u, u⁻¹) is an
A-loop at a germ (corner (a,b) joins the arrival germ of a to the departure germ of b;
these coincide iff b = a⁻¹ — check the two signed cases), which leaves the loopless
setting of Lemma D1 and the solver's supported domain. The cancelling case is handled
at the class level only by the Φ_min framing, i.e. it is behind wall 5
(R3_INVARIANT_LANDSCAPE.md); see §6. Note for the audit: the permutation-level lemmas
of §§1–3 never actually invoke (NC) — but without (NC) the exact image is not the
state a reduced-word harvest visits, so the calculus would be about a complex nobody
reaches; (NC) is what makes the exact calculus class-relevant.

**Duplication, not consumption.** The graft DUPLICATES the guest: w_j survives
unchanged as a relator of P′, and w_i·w_j contains a fresh COPY of r_j's letters. This
(advisor-corrected) fact drives all bookkeeping below and is the structural reason the
symmetry-lemma template cannot extend to AC2: |E′| = |E| + 2|r_j| > |E|, so no
germ-preserving bijection β with βA′β⁻¹ = A can exist — A′ is not a conjugate of A in
any dictionary; the correct replacement is a FIBRATION (§2).

## 1. Setup and bookkeeping [MACHINERY]

Write N_i = |r_i|, N_j = |r_j|, and let occ_j(g) = number of unsigned occurrences of
generator g in r_j. Number the occurrences of P′ so that positions 1..N_i of w_i·w_j
carry r_i's letters, positions N_i+1..N_i+N_j carry the copy's letters, and every other
relator (including the surviving w_j) keeps its letters. This gives a canonical
identification

  E′ = E ⊔ E_c,  E_c = the copy's 2N_j darts,

under which the letters, the tube involution B, and the germ map ν of the surviving
darts are unchanged (they depend only on the letter carried by the occurrence, which is
unchanged). Write h^i_k, d^i_k for the arrival/departure darts of r_i's k-th
occurrence, h^c_k, d^c_k for the copy's.

**Lemma G1 (bookkeeping).** Under (NC) with r_i, r_j cyclically reduced:

(i) A′ = A on all corners except: r_i's wrap corner {h^i_{N_i}, d^i_1} is DELETED;
ADDED are the copy's N_j − 1 internal corners {h^c_k, d^c_{k+1}} (k = 1..N_j−1), the
seam junction J₁ = {h^i_{N_i}, d^c_1}, and the wrap junction J₂ = {h^c_{N_j}, d^i_1}.
Hence |A′| = |A| − 1 + (N_j − 1) + 2 = **|A| + N_j**, and |E′| = |E| + 2N_j.

(ii) deg′(g⁺) = deg(g⁺) + occ_j(g) and deg′(g⁻) = deg(g⁻) + occ_j(g) for every
generator g (each unsigned occurrence contributes exactly one dart at each of the two
germs of its generator). The present-germ set is unchanged, so |C′| = |C| = 2n for
compatible rotations.

(iii) All corners of P′ are loopless, and w_i·w_j is cyclically reduced (§0).

(iv) L′ = L − δ_comp, where δ_comp ∈ {0,1} is 1 iff the Λ(P)-component containing
r_i's wrap germs {ν(h^i_{N_i}), ν(d^i_1)} differs from the component containing r_j's
wrap germs. In particular L′ = L whenever Λ(P) is connected.

*Proof.* (i)–(iii) are direct counts plus §0. (iv): Λ′ contains every Λ-edge except
r_i's wrap (the surviving w_j contributes the SAME germ-pair edges as r_j's full corner
set, including its wrap; the copy's internal corners are parallel to surviving-w_j
edges and add no connectivity). The deleted wrap's endpoints stay connected in Λ′
through the path J₁ · (surviving w_j's wrap edge) · J₂:
ν(h^i_{N_i}) — ν(d^c_1) = ν(d^j_1) — ν(h^j_{N_j}) — ν(d^i_1). So no component splits;
the only possible merge is between the two named components, via J₁ (equivalently J₂),
and it happens iff they were distinct. By Lemma L0 of R1E_DISCONNECTED_LINK.md, L is
C-independent on both sides, so δ_comp is determined by the words. ∎

Equivalent "two-wrap" bookkeeping (used in the plan's phrasing): through the
intermediate repeated-relator presentation P_mid = (w_1, …, w_m, r_j) — a legal
Neuwirth-setting object, not an AC move — the graft adds the copy as a full cyclic
relator (+N_j corners including its wrap), then rewires: DELETE the two wrap corners
(r_i's wrap and the copy's wrap) and ADD the two junction corners J₁, J₂. Net
−2 + 2 + N_j = +N_j, agreeing with (i). P_mid has the same darts, germs and B as P′,
so 𝒞(P_mid) = 𝒞(P′) (compatibility never reads A); A′ differs from A_mid by the
2-edge rewiring only. The interpolation of §3 uses the direct order of (i) (the copy's
wrap is never instantiated), which is what the machine checks verify.

Numerical anchor (advisor-verified numbers reproduced by `build_link_n`): the AK(3)
self-graft ("xxxYYYY","xyxYXY") → ("xxxYYYYxyxYXY","xyxYXY") has |A| 13 → 19 = 13 + 6,
darts 26 → 38, degrees (x,y) = (6,7) → (9,10) = (6+3, 7+3), L = 1 → 1. (§5, V1.)

## 2. The fibration [MACHINERY]

Let 𝒞(P) be the compatible rotation systems of P (one cyclic order per germ, one
cycle per germ, negative-end cycle the B-reversal of the positive-end cycle — the free
datum is one cyclic order per positive germ). Define the restriction map

  ρ : 𝒞(P′) → 𝒞(P),  ρ(C′) = C′ with the copy's darts deleted from each germ cycle,

reading darts through the identification E′ = E ⊔ E_c of §1.

**Lemma G2 (ρ is well-defined).** For every C′ ∈ 𝒞(P′), ρ(C′) ∈ 𝒞(P).

*Proof.* Fix a generator g with pre-graft degree d = deg(g⁺) ≥ 1 (every generator
occurs in P) and m = occ_j(g). Let σ′ = (q_1 … q_{d+m}) be C′'s cyclic order at g⁺;
compatibility forces the cycle at g⁻ to be

  σ′⁻ = (B q_{d+m}, …, B q_1) = reverse(B(σ′)).

The crux is that the deletions at the two germs of g are SIMULTANEOUS in the right
sense. Let S ⊂ {q_1..q_{d+m}} be the copy darts at g⁺. Key fact: **the copy darts at
g⁻ are exactly B(S)** — B pairs the two endpoints of one occurrence, each occurrence
contributes one dart at g⁺ and one at g⁻, and an occurrence lies in the copy iff
either (hence each) of its darts does. Now deletion of a subset from a cyclic sequence
commutes with elementwise application of the bijection B (delete_{B(S)}(B(σ)) =
B(delete_S(σ))) and with reversal (delete_T(reverse(σ)) = reverse(delete_T(σ))).
Therefore

  delete_{B(S)}(σ′⁻) = reverse(B(delete_S(σ′))):

the restricted cycles again satisfy the B-reversal constraint at g. Restricting leaves
a nonempty cyclic order at every germ (d ≥ 1), one cycle per germ; and by Lemma G1(ii)
the non-copy darts at each germ of P′ are exactly the darts of P at that germ. So the
restricted system is a compatible rotation system of P. ∎

**Lemma G3 (surjectivity and uniform fiber size).** ρ is surjective, and for every
C ∈ 𝒞(P)

  |ρ⁻¹(C)| = Fib(P, j) := ∏_g (deg(g⁺) + occ_j(g) − 1)! / (deg(g⁺) − 1)!,

independent of C. Consequently |𝒞(P′)| = |𝒞(P)| · Fib(P, j), matching the census
convention |𝒞(P)| = ∏_g (deg(g⁺) − 1)! of `census_size`
(experiments/stable_ac/fable/neuwirth_rank_n.py:275; the enumerator
`compatible_orders_n` at :960 pins one anchor dart per positive germ and permutes the
tail, hence enumerates each CYCLIC order exactly once — the anchor is an enumeration
device, not extra data).

*Proof.* Given C, choose at each positive germ g⁺ any cyclic order σ′_g on the
d + m darts whose restriction to the d old darts is C's cycle; let the negative-end
cycles be forced by B-reversal. The resulting C′ is compatible by construction and
restricts to C: at positive germs by choice, at negative germs because
delete(reverse(B(σ′_g))) = reverse(B(σ_g)) by the commutations in G2. This proves
surjectivity, and the choices at distinct generators are independent, so the fiber is
the product over g of the count of cyclic orders on a (d+m)-set restricting to a FIXED
cyclic order on a distinguished d-subset (d ≥ 1). That count is
(d+m−1)!/(d−1)!: fix an old anchor dart a; cyclic orders on the full set correspond to
linear orders of the other d+m−1 darts read after a, and the restriction corresponds
to the induced linear order of the d−1 old non-anchor darts; each target order is hit
by choosing the m new darts' positions among d+m−1 slots and their arrangement,
C(d+m−1, m)·m! = (d+m−1)!/(d−1)! ways — independent of the target, so fibers are
uniform. When m = 0 the factor is 1. ∎

CAUTION recorded for future implementers: the naive LINEAR count
∏ (deg+occ)!/deg! is WRONG for cyclic orders — at the AK(3) self-graft it predicts
362,880 where the true fiber is 8!/5! · 9!/6! = 336·504 = **169,344**, and only the
cyclic count reproduces the census ratio 14,631,321,600 / 86,400 = 169,344 (§5, V1).

Remark (L-generality). Nothing in G2/G3 uses connectivity of Λ(P) or non-straddling;
the ("xyxy","xy") anchor of §5 has L = 2 with both generators straddling and the
fibration checks pass verbatim. Remark (stabilized states). If P carries a spare
z-component (AC4 shape), grafts not involving z leave it untouched and Corollary Z of
R1E_DISCONNECTED_LINK.md composes with this calculus with no interaction; grafts
involving the z relator are themselves in scope when (NC) holds, with G1(iv) handling
the component merge (the ("xx","yy") anchor is exactly this shape).

## 3. Defect transformation [MACHINERY]

For a finite ribbon graph R (vertices = germs carrying ≥ 1 dart, with cyclic dart
orders; edges = unordered dart pairs; untwisted bands) define

  def(R) = e(R) − v(R) + 2c(R) − f(R)

(edges − vertices + 2·components − boundary circles of the oriented thickening). By
the capped-surface computation of Lemma 1 (Euler dictionary), def(R) = 2·(genus-sum of
the capped components) ≥ 0, and for the ribbon graph of a compatible C on a Neuwirth
complex, def = defect(C).

**Lemma G4 (elementary insertion/deletion dichotomy).** Let R′ be obtained from R by
inserting one edge {a, b} whose darts are placed at prescribed slots of the rotations
(creating their germ-vertices if absent). Then def(R′) − def(R) ∈ {0, 2}, and it is 2
exactly when both germs already carried darts and the two insertion slots lie on
DISTINCT boundary circles of the SAME component of R ("genus-raising insertion").
Symmetrically, deleting one edge (removing its darts, and any emptied vertices) gives
def(R) − def(R_del) ∈ {0, 2}, with 2 exactly in the mirror case ("genus-lowering
deletion": both endpoints keep degree ≥ 1, the edge's two band sides lie on one
boundary circle, and the deletion does not disconnect its component).

*Proof.* Both-vertices-occupied insertion: the thickening |R′| is |R| with an
untwisted band attached along two boundary arcs; e += 1 so χ −= 1. Ribbon-graph
thickenings with untwisted bands are orientable (Heffter–Edmonds), so the attachment
is orientation-compatible. Three cases. Feet on the same boundary circle: an
orientation-compatible band attached to a single circle must SPLIT it (the non-split
outcome is the Möbius-style attachment, excluded by orientability): f += 1, c
unchanged, Δdef = 1 − 1 = 0. Feet on distinct circles of one component: the circles
merge, f −= 1, Δdef = 1 + 1 = 2 (one handle appears). Feet on circles of distinct
components: f −= 1, c −= 1, Δdef = 1 − 2 + 1 = 0 (a connected sum, genus-sum
unchanged — this is why the 2L term is load-bearing). Degenerate insertions: a pendant
insertion (one germ fresh) has Δe = +1, Δv = +1, Δf = 0, Δc = 0, Δdef = 0; a fresh
isolated edge (both germs fresh) has Δe = +1, Δv = +2, Δf = +1, Δc = +1, Δdef = 0.
Deletion is the exact mirror of each case (pendant deletion Δdef = −1+1+0−0 = 0;
isolated-edge deletion Δdef = −1+2−2+1 = 0; bridge deletion Δdef = −1+2−1 = 0;
face-merging deletion Δdef = −1+0+1 = 0; genus-lowering deletion Δdef = −1−1 = −2). ∎

**Theorem G5 (master formula).** Fix C′ ∈ 𝒞(P′) and let C = ρ(C′). Define the
canonical interpolation R_0 → R_1 → … → R_{N_j+2}: every R_t has rotation C′
restricted to its current dart set, R_0 is the ribbon graph of (P, C) (so
def(R_0) = defect(C), using C′|_E = C), and the ops are, in order:

  (op 1)                delete r_i's wrap corner {h^i_{N_i}, d^i_1};
  (ops 2 .. N_j)        insert the copy's internal corners {h^c_k, d^c_{k+1}} in word order;
  (op N_j+1, op N_j+2)  insert J₁ = {h^i_{N_i}, d^c_1}, then J₂ = {h^c_{N_j}, d^i_1}.

The final ribbon graph is that of (P′, C′) (Lemma G1(i); machine-checked), so
def(R_{N_j+2}) = defect′(C′). By Lemma G4 each op moves def by 0 or ±2, giving

  **defect′(C′) = defect(ρ(C′)) − 2·X⁻(C′) + 2·X⁺(C′)** ,

where X⁻(C′) ∈ {0,1} is 1 iff op 1 is genus-lowering and X⁺(C′) ∈ {0, …, N_j+1} is
the number of genus-raising insertions among ops 2..N_j+2. Moreover:

(a) X⁻(C′) = glower(C; i) depends only on the BASE POINT C and on which corner of r_i
is the wrap: op 1 is performed on R_0 = the ribbon graph of (P, C), before any copy
dart exists. It is pre-graft-readable data. (Operational definition of glower(C; c)
for a corner c: delete c's A-edge from the ribbon graph of (P, C) and retrace;
glower = (def drop)/2 ∈ {0, 1}. glower = 0 forced whenever defect(C) = 0.)

(b) X⁺(C′) depends on the fiber coordinate (the interleavings) and on r_j. The
difference X⁺ − X⁻ is determined by the endpoints; the individual counts depend on the
chosen op order, which the canonical order fixes.

(c) The 2L bookkeeping is automatic: intermediate component counts roam freely
(deletions may disconnect, insertions may merge — the ("xx","yy") anchor merges), and
def absorbs them; the endpoint identity L′ = L − δ_comp is G1(iv). ∎

**Corollary G6 (the pre-registered ceiling; two-sided).** For every C′,
defect′(C′) ≥ defect(ρ(C′)) − 2. Minimizing over 𝒞(P′) (and using surjectivity, G3):

  **γ_N(P′) ≥ γ_N(P) − 1**,  and (from X⁺ ≤ N_j + 1)  γ_N(P′) ≤ γ_N(P) + N_j + 1.

Per the pre-registration this is the structural ceiling of step 1 and it is VACUOUS at
AK(3) for invariant-building: γ_N(AK(3)) = 2 gives only γ_N ≥ 1 after ONE
non-cancelling graft and nothing after two. The bound does not compose usefully along
paths, covers only the non-cancelling exact AC2 subdomain, and transports no negative
along AC paths. No claim beyond the ceiling is made.

**Corollary G7 (the ceiling is tight; non-monotone both ways INSIDE the scope).**
The −1 in G6 cannot be improved to 0: the non-cancelling graft
("yyxYxy","yx") → ("yyxYxyyx","yx") has minimum defect 2 → 0 (machine-verified, §5,
V7; 4 of the 720 post-graft rotations attain the pointwise floor defect′ =
defect(ρ) − 2). Jumps of +2 also occur inside the scope (e.g. ("XXyXY","XX") 2 → 4,
and the codex two-line counterexample ("yxx","y") 0 → 2 is non-cancelling). So γ_N is
non-monotone in BOTH directions already on the non-cancelling subdomain — previously
recorded at class level, now witnessed inside this calculus's own scope. The decrease
witness also exhibits, at the exact level, a non-thickenable complex (min defect 2)
whose one-graft image is THICKENABLE (min defect 0, Theorem D of
R1E_DISCONNECTED_LINK.md): non-thickenability does not survive even one in-scope move —
a concrete reinforcement of the no-transport clause in §6, and of why only class-level
functionals (wall 5) could ever carry a negative.

**Corollary G8 (one-move buffer at AK(3); observation, not a route).** Every exact
presentation obtained from any realization of the AK(3) pair in its
rotation × inversion × permutation orbit (the histogram is constant on that orbit —
GAMMA_N_SYMMETRY_LEMMA.md) by ONE non-cancelling AC2 graft satisfies γ_N ≥ 1, i.e. its
exact complex is non-thickenable — using the certified γ_N(AK(3)) = 2 (codex
certificate; corpus). This is a finite, one-move statement; it does NOT iterate (G6
degrades per move), says nothing about cancelling grafts or conjugation-with-reduction,
and is NOT progress toward a class statement. Recorded because it certifies a
one-move non-cancelling "moat" of non-thickenable exact complexes around AK(3) without
running any census on the (1.46 × 10¹⁰-sized) post-graft families.

## 4. The move-ordering heuristic Δ̂ [MACHINERY — the deliverable with positive-direction value]

The min over a fiber of X⁺ is the "junction term": at the AK(3) self-graft each fiber
has 169,344 elements and the full post census 1.46 × 10¹⁰ dwarfs the 200k cap, so the
junction term is not computable by enumeration on real targets (advisor item 3). The
heuristic replaces it by its optimistic value 0.

**Definition (Δ̂).** Input: an exact pre-graft state P (cyclically reduced words), a
candidate move (i, j, ρ_i, ρ_j) where ρ_i, ρ_j are cyclic rotations applied to r_i,
r_j before grafting. Output: an integer Δ̂ (UNHALVED defect units) and a validity bit.

  Δ̂(P; i, j, ρ_i, ρ_j) = min_{C ∈ 𝒞(P)} [ defect(C) − 2·glower(C; c_wrap(i, ρ_i)) ],

where c_wrap(i, ρ_i) is the corner of r_i that becomes the wrap after rotation ρ_i
(rotating r_i changes WHICH corner is deleted — that is the only way ρ_i enters;
census and histogram are rotation-invariant). Validity bit = [(NC) holds for the
rotated pair] AND [the min was taken over the FULL census (affordable or cached)].

**Proposition G9 (guarantees).** (a) If the validity bit is set, Δ̂ is a certified
lower bound: 2·γ_N(P′) ≥ Δ̂ — immediate from G5(a) + G6 pointwise, minimizing over
fibers and bases. (b) Δ̂ is optimistic-exact: 2·γ_N(P′) = Δ̂ iff over some argmin base
C some fiber element achieves X⁺ = 0, i.e. an interleaving making ALL N_j + 1
insertions cofacial. "All cofacial achievable" is a CONSTRAINED condition — the free
slots are only the positive-germ interleavings, the negative-germ slots being forced
by B-reversal — and it genuinely fails: ("yxx","y") has Δ̂ = 0 but post-minimum 2
(both fiber elements forced X⁺ ≥ 1 — the forced genus-raising insertion of §5, V3/V4),
likewise ("xyxy","xy") (Δ̂ 0, post-min 2), while ("xx","yy") and the decrease witness
("yyxYxy","yx") achieve exactness (§5). (c) Δ̂'s value is j-independent by design
(cofacial optimism erases the guest); j enters through the validity bit (seam
legality) and through exactness. Refining the estimate by lower-bounding forced
genus-raises from r_j's B-coupling is future work outside this time-box.

Degraded fallback (validity bit off): with any certified lower bound 2γ ≤ min defect
(full census, or the solver's NOT_SPHERICAL certificate giving min ≥ 2), use
Δ̂_fallback = 2γ − 2 — still a true bound by G6, but blunt (no corner sensitivity).

**Intended use (harvest priority).** Rank candidate AC2 grafts of a stable harvest
frontier by Δ̂ ASCENDING (predicted best-case post defect — steer toward predicted
thickenable images), tie-breaking by the E-DESCENDING priority already adopted in the
Colab runner spec (R3PRIME_DIGON_EXCESS.md, AK(2)-control item 3), replacing blind
length- or E-only ordering for the move-choice dimension. Implementation contract for
a later session: one census pass over P computes the whole vector
m(c) = min_C [defect(C) − 2·glower(C; c)] for EVERY corner c of every relator
simultaneously (cost: one extra face-trace per (C, corner), O(|A|·darts) per C on top
of the census; the census convention and defect line are
`neuwirth_rank_n.py` `compatible_orders_n`:960 and `gamma_N_factorial_n`:1038); then
every move (i, j, ρ_i, ρ_j) reads its Δ̂ off the vector entry c_wrap(i, ρ_i) after the
O(1) (NC) check. Canonicalization discipline: compute m(·) once per canonical class
representative and re-index corners through the recorded rotation/inversion — sound
because rotation/inversion/permutation are histogram symmetries
(GAMMA_N_SYMMETRY_LEMMA.md), with the reduced-key caveat recorded there (F6) kept at
the call site.

## 5. Numerical anchors — machine-verified this session

All checks run against the committed dictionary (`build_link_n`, `census_size`,
`compatible_orders_n`, `gamma_N_factorial_n` in
experiments/stable_ac/fable/neuwirth_rank_n.py) by two session-scratchpad scripts
(verify_graft_calculus.py: 51 + 28 checks, all PASS; probe_graft.py: bounded scan).
Scripts are session-scratchpad artifacts (this task's write scope is this file only);
§§1–4 contain every definition needed to regenerate them.

V1 AK(3) self-graft ("xxxYYYY","xyxYXY") → ("xxxYYYYxyxYXY","xyxYXY"):
   |A| 13 → 19, darts 26 → 38, degrees (6,7) → (9,10), L 1 → 1;
   census 86,400 → 14,631,321,600; fiber formula (8!/5!)·(9!/6!) = 336·504 = 169,344
   = exact census ratio; naive linear formula gives 362,880 (rejected).
V2 Fibration checks (restriction computed dart-by-dart, fibers grouped, every
   restricted system found in the enumerated pre census, every fiber exactly the G3
   size): ("yxx","y") 1 → 2 (fiber 2); ("xxyy","xy") 4 → 36 (fibers all 9);
   ("xx","yy") 1 → 6 (fiber 6); ("xyxy","xy") 4 → 36 (fibers all 9, L = 2 with
   straddling generators); ("yyxYxy","yx") 48 → 720 (fibers all 15).
V3 Anchor histograms: ("yxx","y") {0:1} → ("yxxy","y") {2:2} (matches the
   GAMMA_N_SYMMETRY_LEMMA machine-confirmed 0→1 γ_N jump).
V4 Interpolation dichotomy: for EVERY post-graft compatible rotation of the five
   V2 grafts (800 rotation systems total), the canonical op walk of G5 was traced;
   every insertion step ∈ {0,+2}, the deletion step ∈ {0,−2}, endpoints equal to the
   dictionary defects. Pointwise Δ = defect′ − defect(ρ) histograms:
   ("yxx","y") {2:2}; ("xxyy","xy") {0:6, 2:22, 4:8}; ("xx","yy") {0:2, 2:4};
   ("xyxy","xy") {0:12, 2:24}; ("yyxYxy","yx") {−2:4, 0:164, 2:442, 4:110}.
   All ≥ −2: the G6 floor holds pointwise and is attained (only) in the last case.
V5 Heuristic: Δ̂ verified as a per-fiber and global lower bound on all five grafts;
   exact on ("xx","yy") (Δ̂ = 0 = post min) and ("yyxYxy","yx") (Δ̂ = 0 = post min);
   strictly below on ("yxx","y"), ("xxyy","xy"), ("xyxy","xy") (Δ̂ = 0, post min 2 —
   the forced genus-raising insertion).
V6 Component merge: ("xx","yy") → ("xxyy","yy") has L 2 → 1 (δ_comp = 1, G1(iv));
   ("xyxy","xy") keeps L 2 → 2 (δ_comp = 0: both wrap-germ pairs in one component).
V7 Ceiling tightness scan (bounded probe, 16 curated + 4,000 random non-cancelling
   grafts over {x,y}, 147 with pre-minimum defect ≥ 2 analyzed): ONE strict decrease
   found — ("yyxYxy","yx"): min defect 2 → 0 — plus four +2 jumps (e.g.
   ("XXyXY","XX") 2 → 4) and 0 otherwise (among rows with affordable post census);
   139/147 carried at least one pre-graft C with glower(wrap r_1) = 1 (e.g.
   ("xyxy","xy"), census 4, all defects 2, two rotations with glower 1).

## 6. Honesty section

- **Wall 5 (the Φ_min tautology) restated.** The only (0)-invariant packaging of γ_N
  is Φ_min(class) = min over exact realizations; Φ_min = 0 ⟺ the class contains a
  thickenable member, i.e. Φ_min IS the search target, so only computable STRICT LOWER
  BOUNDS on Φ_min can constitute progress. This document produces NO such bound: G6 is
  a per-move ceiling that degrades by 1 per graft and dies immediately under
  composition; Δ̂ is a search prioritizer, not an invariant. Nothing here transports
  any negative (or positive) along AC paths — Corollary G7's decrease witness is an
  explicit in-scope demonstration of why transport fails.
- **Ceiling status.** γ_N(P′) ≥ γ_N(P) − 1 is exactly the pre-registered expected
  yield (plan item 3) and is VACUOUS at AK(3) (γ_N = 2): one move leaves ≥ 1, two
  leave nothing. Per the pre-registration, the arc STOPS here: machinery + heuristic
  committed, steps 2/4 not entered (no candidate functional is proposed, so the
  battery-(b) and type-check preconditions of plan items 4/5 are not triggered).
- **Cancelling seam is out of scope**, for the two reasons of §0 (reduction cascades
  delete occurrences and destroy the E ⊂ E′ locality; A-loops leave the supported
  setting). It is handled at the class level only by the Φ_min framing — i.e. it sits
  behind wall 5, where this calculus does not reach.
- **Per-realization phase seed (codex; cited, not re-derived).** The structural
  γ_N(AK(3)) ≥ 2 content used by G8, and any future attempt to push phase data through
  this fibration, rests on codex's `AK3_NEUWIRTH_PHASE_OBSTRUCTION.md` (codex/proof,
  a17c7bf; scratchpad mirror lit_AK3_NEUWIRTH_PHASE_OBSTRUCTION.md) — the
  human-readable phase-equation proof for the displayed complex. Their 192-case
  analysis is NOT re-derived here; division of labor per
  R3PRIME_DIGON_EXCESS.md ("Complementarity note").
- **No Lackenby dependency.** Nothing above invokes Lackenby Thm 1.3; thickenability
  readings of defect 0 use Theorem D (audited machinery of this line). The
  [unverified this session] flag therefore does not attach to this document.
- **Not claimed:** any AC2 invariance of γ_N or of the histogram (false — V3, V7);
  any class functional; any stable-AC consequence; anything about the cancelling
  case; any content about AK(3) beyond the one-move buffer G8, which is finite,
  non-iterable and explicitly not a route. Advisor priors recorded for honesty
  (plan item 6): machinery of this kind ~0.7 prior (delivered); genuine invariant
  ≤ 0.5% (not attempted here).
