# S6 — Which AC moves can change thickenability, and what stabilization actually buys

Task A8, branch `claude/stable-ac-conjecture-stabilization-rwo9as` (merge into
`fable/proof`). Date 2026-08-04.

STATUS: the topological lemmas (T1, T4, T4′, T0) are **proofs written this session,
NOT yet independently audited** — per the standing rule they are drafts, not results.
The empirical flip counts are exact censuses and are reported as measurements. Every
statement imported from another note carries that note's own status flag.

Claims addressed (FRAMING.md taxonomy): everything here is **MACHINERY** — properties of
exact word-realized presentation complexes and of the moves acting on them. Nothing here
claims anything about AK(3)'s AC-triviality or stable AC-triviality in either direction.

---

## 0. What the predicate actually is (checked against the code, not remembered)

`gamma_N_factorial_n` (`experiments/stable_ac/fable/neuwirth_rank_n.py:989`) builds the
exact occurrence dictionary of the **word-realized** complex — no free reduction, no
cyclic reduction, no identification of repeated occurrences (`build_link_n`, l. 154) —
enumerates every **compatible** rotation system (`compatible_orders_n`, l. 960: one cycle
per germ, one cyclic order chosen freely at each positive germ with the first dart pinned,
the negative germ forced to the `B`-reversal `C_{τv} = B C_v^{-1} B`), and returns

    minimum_defect = min_C ( |A| − |C| + 2L − |AC| ),      minimum_genus = defect / 2.

So the returned `minimum_genus` is `γ_N`, and the predicate used throughout this note is
`γ_N = 0`. Three things the code fixes that must not be blurred:

1. **`γ_N = 0` ⟺ `K_P` embeds in an ORIENTABLE PL 3-manifold** — Theorem D of
   `R1E_DISCONNECTED_LINK.md` (AUDITED), with the general `2L` term so disconnected links
   are covered. R1E explicitly disclaims any statement about non-orientable thickenings.
   **[GAP-O]** Lackenby's Thm 1.3 hypothesis is "embeds in *some* 3-manifold"; the
   orientable/general gap is not closed on this line. Everything proved *topologically*
   below (T1, T4, T4′) is orientation-agnostic and therefore survives [GAP-O]; everything
   *measured* is orientable thickenability only.
2. **`γ_N` is a function of the SPELLING, not of the presentation.** The complex depends
   on the exact cyclic words. This is the whole reason move (0) is a move here.
3. **`γ_N`'s value is not comparable across cell structures; only `γ_N = 0` is
   topological** (trap T-S6 of `S3_SUBDIVISION_INVARIANCE.md`). Below, "inert" always
   means *the predicate is preserved*, and where a stronger statement (whole histogram, or
   homeomorphic underlying space) holds it is said explicitly.

Notation. `P = ⟨x_1..x_n | r_1..r_m⟩`, `K_P` the one-vertex presentation complex, `v` its
vertex, `Λ(P)` the link multigraph (vertices = the `2n` germs `g^±`, one edge per corner of
a relator). For a generator `g`, `m_g` = the number of occurrences of `g^{±1}` across all
relator words — the **multiplicity of the edge `g`**. Move numbering is FRAMING.md's:
AC1 = invert, AC2 = multiply, AC3 = conjugate, (0) = free/cyclic reduction,
AC4/AC5 = (de)stabilize.

---

## 1. The table

| move | changes the space? | preserves `γ_N = 0`? | direction | proof / counterexample | empirical flips (destroy / create, out of measured) |
|---|---|---|---|---|---|
| **M1** AC1 `r → r^{-1}` | no — homeomorphic | **yes** | both | **T1** (§2): a cellular homeomorphism, identity on the 1-skeleton. Stronger: whole defect histogram preserved — `GAMMA_N_SYMMETRY_LEMMA`, AUDITED | 0 / 0 of 2,236 |
| *(ROT)* cyclic rotation of a relator | no — homeomorphic | **yes** | both | rotation of the polygon; `GAMMA_N_SYMMETRY_LEMMA` (i), AUDITED | 0 / 0 of 4,472 |
| **M4** AC4/AC5 stabilize / destabilize | yes, but only by a wedge | **yes** | both | **T4** (§3): the space becomes the one-point union with a 2-disc, glued at a *boundary* point of that disc. Stronger: whole histogram — `R1E` Corollary Z, AUDITED | 0 / 0 of 1,118 |
| **M4′** first AC2 slide over a fresh stabilizer, `r_i → r_i z^{±1}` | **no — subdivision** | **yes** | both | **T4′** (§3, NEW): the loop `z` is a chord of the `r_i`-cell cutting off a monogon, so `K_G` is a CW subdivision of `K_P` | 0 / 0 of 3,332 (`G1`) and 3,332 (`G1i`); `γ_N` equal exactly in all |
| *(S3)* chord refinement / triangulation | **no — subdivision** | **yes** | both | Theorem S3, `S3_SUBDIVISION_INVARIANCE.md` (audit A5 pending) | 63/63 positive ladder, ranks 3–9 (S3 §3) |
| **M0** move (0), free / cyclic reduction | **YES** | **NO — reduction can CREATE it** | one-way in practice | `("xyXY","yYxxy")` `γ_N = 1` reduces to `("xyXY","xxy")` `γ_N = 0` (`R1F`, re-verified this session); mechanism **T0** (§4). The destroying direction is ¬Conjecture SR of `R7` — **[OPEN]**, 0 counterexamples in ≈114,000 measured complexes | creates in 315 of 2,510 non-thickenable spellings; destroys in **0 of 997** thickenable spellings |
| **M2** AC3 `r → c r c^{-1}`, `c` a single generator, product freely reduced | **YES** | **NO — conjugation can DESTROY it** | one-way in practice | **T2** (§5): this move *is* a single spike up to cyclic rotation, so `R1F`'s counterexample is an AC3 counterexample verbatim — `("xyXY","xxy")` `γ_N = 0`, conjugate `r_2` by `Y`, `("xyXY","Yxxyy")` `γ_N = 1` | **315 destroy / 0 create of 3,507** — 24.0 % of thickenable bases; 0 of 2,195 non-thickenable bases |
| **M2c** AC3 with cancellation (`r` starts with `c^{-1}` or ends with `c`) | yes | **yes, empirically** | — | no proof; measured only (Conjecture S6-C, §5). The fin is planted beside an existing strand of the same 1-handle | **0 destroy / 0 create of 3,413**; `γ_N` preserved exactly in 2,230 / 2,230 |
| **M3** AC2 `r_i → freered(r_i r_j^{±1})` | **YES** | **NO — in both directions** | neither | explicit pairs in §6; a genuine 2-handle slide | **425 destroy / 73 create of 1,863** — 51.5 % of thickenable bases lose it, 7.0 % of non-thickenable bases gain it |

"Measured" = pairs decided by exact census within the rotation cap; skipped pairs are
counted in §7 and never converted into a verdict. For M0 the denominators are read in the
reduction direction: the 315 events are pairs whose spiked spelling has `γ_N > 0` and whose
reduction has `γ_N = 0`.

---

## 2. T1 — AC1 (inversion) is a homeomorphism

**Theorem T1.** Let `P' ` be `P` with `r_i` replaced by `r_i^{-1}`. Then there is a
homeomorphism `|K_P| → |K_{P'}|` which is the identity on the 1-skeleton. Hence `K_P`
embeds in a 3-manifold `M` iff `K_{P'}` does, for `M` orientable or not.

*Proof.* Write the attaching map of the `i`-th 2-cell as `φ: S¹ → K_P^{(1)}`, `φ` reading
`r_i` from a basepoint. Let `ρ: S¹ → S¹` be the reflection fixing the basepoint. Then
`φ ∘ ρ` reads `r_i^{-1}`, i.e. it is the attaching map of the `i`-th 2-cell of `P'`.
Extend `ρ` to the reflection `ρ̄: D² → D²` — a homeomorphism of the closed disc. The map
which is the identity on `K_P^{(1)}` and on the other 2-cells, and `ρ̄` on the `i`-th cell,
respects the two attaching maps by construction and therefore descends to a homeomorphism
of the quotient spaces. Embeddability of a compact polyhedron in a 3-manifold is a property
of the underlying space. ∎

The same argument with a rotation of `S¹` proves the ROT row (cyclic rotation of a relator).
`GAMMA_N_SYMMETRY_LEMMA.md` (AUDITED) proves the stronger combinatorial statement that the
entire defect histogram, not just `γ_N`, is preserved by rotation, inversion and relator
permutation. Our 2,236 + 4,472 measured pairs are a re-confirmation on a fresh corpus, not
new information.

---

## 3. T4 — stabilization wedges on a disc; T4′ — the first slide over the stabilizer is a
subdivision

**Theorem T4 (AC4/AC5).** Let `P⁺ = ⟨x_1..x_n, z | r_1..r_m, z^{±1}⟩` be an AC4 image of
`P = ⟨x_1..x_n | r_1..r_m⟩`. Then

    |K_{P⁺}|  ≅  |K_P| ∨_v D²,

the one-point union of `|K_P|` with a 2-disc glued at a point `v` of **∂D²**. Consequently
`|K_{P⁺}|` embeds in a 3-manifold `M` **iff** `|K_P|` does — `M` orientable or not.

*Proof.* `K_{P⁺} = K_P ∪ e¹_z ∪ e²`, where `e¹_z` is a 1-cell attached to `v` at both ends
(a loop) and `e²` is a 2-cell attached along the length-**one** word `z`, i.e. by a
*homeomorphism* `∂D² → \overline{e¹_z} ≅ S¹`. Because that attaching map is a homeomorphism
and not merely a degree-1 map with folds, `Δ := \overline{e¹_z ∪ e²}` is a 2-disc with
`∂Δ = \overline{e¹_z}`, and `Δ ∩ |K_P| = {v} ⊂ ∂Δ`. That is exactly the asserted wedge.
This is the subtlety flagged in the task: the disc is glued along a **loop at the single
vertex**, so the wedge point is on the disc's *boundary*, not in its interior — the two
wedges are different spaces and only the boundary one is what AC4 produces.

(⇐, destabilization AC5). `|K_P|` is a closed subspace of `|K_{P⁺}|`, so any embedding
restricts.

(⇒, stabilization AC4). Let `h: |K_P| ↪ M³` be a PL embedding and `v̂ = h(v)`. Take a
regular neighbourhood `R ≅ B³` of `v̂` meeting `h(|K_P|)` in the cone from `v̂` over the
link graph `Λ ⊂ ∂R ≅ S²`. `Λ` is a compact 1-complex, so `S² ∖ Λ` is a nonempty open set;
pick an embedded arc `β ⊂ S² ∖ Λ`. Then `T := cone(v̂, β) ⊂ R` is a PL 2-disc, `v̂` is a
(corner) point of `∂T`, and `T ∩ h(|K_P|) = {v̂}` because a cone point of `cone(v̂,β)` other
than the apex lies over `β`, which misses `Λ`. Both `Δ` and `T` are 2-discs with a marked
boundary point, so there is a homeomorphism `Δ → T` sending `v ↦ v̂`; glueing it to `h`
gives an embedding of `|K_{P⁺}|`. Orientability is never used. ∎

`R1E` Corollary Z (AUDITED) proves the stronger combinatorial fact that the *entire defect
histogram* is preserved, by the bookkeeping `|A|⁺ = |A|+1`, `|C|⁺ = |C|+2`, `L⁺ = L+1`,
`|AC|⁺ = |AC|+1`. T4 adds the topological reason: the new link component is the arc
`z⁺ —— z⁻`, which is exactly the link of a **boundary** point of a disc. Our 1,118 measured
pairs re-confirm it.

**Theorem T4′ (the first slide over a fresh stabilizer is a subdivision) — NEW.** Let
`P⁺` be as above and let

    G = ⟨x_1..x_n, z | freered(r_1 z^{ε}), r_2, …, r_m, z⟩,   ε = ±1,

the AC2 image of `r_1` by the stabilizer relator (no free reduction occurs: `z` does not
appear in `r_1`). Then `K_G` is a **CW subdivision of `K_P`**; in particular
`|K_G| ≅ |K_P|` and `γ_N(G) = 0 ⟺ γ_N(P) = 0`.

*Proof.* Let `Φ: D² → K_P` be the characteristic map of the 2-cell of `r_1`, with
`k = |r_1|` boundary vertices `p_0,…,p_{k−1}` all mapping to `v`, and `Φ|_{int D²}`
injective. Choose an embedded arc `c ⊂ D²` with both endpoints at `p_0` and
`int(c) ⊂ int(D²)`. Then `c ∪ {p_0}` is a simple closed curve in `D²` meeting `∂D²` only at
`p_0`, so by Schoenflies it separates `D²` into a disc `E` with `∂E = c ∪ {p_0}` and a disc
`F` with `∂F = c ∪ ∂D²`. Since `Φ(p_0) = v` and `Φ` is injective on the interior, `Φ(c)` is
an embedded **loop at `v`**: declare it a new 1-cell `z`, oriented so that `∂E` reads the
monogon `z^{-ε}` and `∂F` reads `r_1 z^{ε}` (the two orientations of `c` realize both signs;
and in any case relator inversion is a homeomorphism by T1, so all four sign combinations
give homeomorphic complexes). Hence the CW complex obtained from `K_P` by adding the 1-cell
`Φ(c)` and cutting the `r_1`-cell along it is precisely `K_G`. Adding a cell inside a cell
and cutting along it is a CW subdivision, so `|K_G| = |K_P|` as sets and the identity is a
homeomorphism; embeddability is a property of the underlying space. ∎

T4′ is the exact analogue of Theorem S3 for the *stabilizer* relator: S3's chord runs
between two **distinct** boundary vertices and cuts off a polygon; T4′'s chord runs from a
boundary vertex **to itself** and cuts off a monogon. Both are subdivisions, so both are
inert. The consequence is stated in §8.

Measured (`stab_graft.py`, 3,332 rank-2 bases, cap 3·10⁵): `P⁺ = (r_1, r_2, z)`,
`G1 = (r_1 z, r_2, z)` and `G1i = (r_1 Z, r_2, z)` each matched the base's `γ_N`
**exactly — not merely the predicate — in 3,332 of 3,332 triples, three times over**.
That is the strongest form of T4 and T4′ the census can express. A worked instance
(verified inline, §10):

| presentation | census size | `γ_N` | |
|---|---|---|---|
| `("xYY","xYx")` | 4 | 0 | base |
| `("xYY","xYx","z")` | 4 | 0 | AC4 — T4 |
| `("xYYz","xYx","z")` | 4 | 0 | one slide — T4′ |
| `("xYYZ","xYx","z")` | 4 | 0 | one slide, other sign — T4′ |
| `("xYYzz","xYx","z")` | 8 | **1** | `m_z = 3`: no longer a chord, and thickenability is gone |

---

## 4. T0 — move (0) genuinely changes the space, and it can CREATE thickenability

**The local model.** For an interior point `p` of the edge `g`, a neighbourhood of `p` in
`|K_P|` is `ℝ × cone(m_g points)` — the book with `m_g` pages — because the 2-cells
approach `g` along exactly one germ per occurrence of `g^{±1}`. Hence

    H_2(|K_P|, |K_P| ∖ p; ℤ) ≅ ℤ^{m_g − 1}   (m_g ≥ 1),

so `m_g = 0` is a free edge, `m_g = 1` a boundary point, `m_g = 2` a surface point, and
`m_g ≥ 3` a **triple line** — a genuinely singular point.

**Theorem T0 (the mechanism).** A *spike* — the inverse of one move-(0) step — replaces a
relator's cyclic word `w` by `u · g · g^{-1} · u'` (`w = u u'`). Then

* `m_g` increases by exactly **2** and every other multiplicity is unchanged, so the local
  models along the edge `g` change (a free edge becomes a triple line, a surface line
  becomes a 4-page book, and so on);
* the two new occurrences are cyclically adjacent, so the attaching map **folds** there:
  two adjacent boundary arcs of the polygon map onto the same edge path in opposite
  directions, and the corner between them is a **loop edge of `Λ`** at the germ `arr(g)`.
  (Loops of `Λ` are *exactly* the cyclically adjacent cancelling pairs of the spelling —
  `R7` Lemma M1 / `R1F`'s solver diagnostic "A-link has 1 loop edge(s)".)

So `|K|` is genuinely a different space; move (0) is not a normalization at this level. ∎

**Confirmation on the repo's own example** (re-run this session, `gamma_N_factorial_n`,
cap 2·10⁶):

| spelling | census size | defect histogram | `γ_N` | `m_x`, `m_y` |
|---|---|---|---|---|
| `("xyXY","xxy")` (reduced) | 12 | `{0:2, 2:6, 4:4}` | **0** | 4, 3 |
| `("xyXY","yYxxy")` (spiked) | 144 | `{2:26, 4:94, 6:24}` | **1** | 4, 5 |

Two independent certificates that the spaces differ. (i) By T0, the reduced complex has
local `H_2`-rank 3 along the `x`-edge and 2 along the `y`-edge, while the spiked one has 3
and **4**; local homology rank at a point is a homeomorphism invariant, and the spiked
complex has an arc of rank-4 points where the reduced one has none. (ii) Decisively, the
verdicts themselves: orientable thickenability is a property of the underlying space
(Theorem D), and they differ. **Free reduction created thickenability here.**

**Direction.** Whether move (0) can ever *destroy* thickenability is exactly the negation
of `R7`'s **Conjecture SR** (`γ_N(spike(P)) = 0 ⇒ γ_N(P) = 0`) and is **[OPEN]**. What is
known:

* `R7` Corollary S5 (the spike ceiling, draft): `γ_N(spike(P)) ≥ γ_N(P) − 1`. So if a
  spiked spelling is thickenable then the reduced one has `γ_N ≤ 1`: **reduction can lose
  at most one unit**, never more.
* `R7` Theorem S10 (draft): if the spiked complex has a defect-0 rotation system in which
  the spike is **unnested**, the reduced complex is thickenable. Only *nested* defect-0
  systems could witness a counterexample.
* Empirically 0 counterexamples: `R1F`'s 110,917 measured spiked complexes, plus this
  session's **997** pairs whose spiked spelling is thickenable (§7), in every one of which
  the reduction was thickenable too.

---

## 5. T2 — AC3 by a single generator IS a spike. It can destroy thickenability.

This is the interesting move and the answer is sharp.

**Theorem T2 (identification).** Let `r = a_0 … a_{N−1}` be a cyclic word and `c` a letter
(a generator or an inverse generator).

*(a)* `c · r · c^{-1}` and `r · c^{-1} · c` are **the same cyclic word** (move the last
letter to the front). The second is `SPIKE(r; k = 0, u = c^{-1})` in `R7` §0's notation —
insert `u u^{-1}` at position `k` of the cyclic word.

*(b)* Conversely `SPIKE(r; k, u)` with `|u| = 1` is, as a cyclic word,
`u^{-1} · rot_k(r) · u` — the AC3 image by `u^{-1}` of the cyclic rotation of `r` starting
at position `k`.

Since cyclic rotation of a relator induces a homeomorphism of the presentation complex
(T1/ROT) and preserves the full defect histogram (`GAMMA_N_SYMMETRY_LEMMA` (i), AUDITED),
**single-generator AC3 and single spikes are the same operation up to homeomorphism.** ∎

*(`SPIKE` is `R7` §0's notation: insert `u u^{-1}` at position `k` of the cyclic word.)*

Three consequences, in increasing order of usefulness.

**Corollary T2.a (AC3 is inert modulo (0)).** For `r` cyclically reduced,
`cycred(c r c^{-1})` is a cyclic rotation of `r`; more generally the cyclic reduction of any
conjugate `w r w^{-1}` is a cyclic rotation of `r`. So **AC3 followed by move (0) is the
identity on presentations up to relator rotation, hence topologically inert.** The entire
content of AC3 therefore sits in two places, and nowhere else:

1. the **spelling** it produces (an unreduced relator is a different complex — §4), and
2. its **composition with AC2**, i.e. the conjugated graft
   `r_i → freered(r_i · w r_j^{±1} w^{-1})`, obtained as AC3 · AC2 · AC3⁻¹.

**Corollary T2.b (the spike calculus transfers verbatim to AC3).** Every statement of
`R7` §1 about spikes is a statement about single-generator AC3. In particular, *conditional
on `R7`'s audit* (its lemmas are drafts):

* `γ_N(P) − 1 ≤ γ_N(c r c^{-1}) ≤ γ_N(P) + 2` (S5);
* AC3 by a word `w` of length `k` is a composite of `k` single-generator conjugations —
  `c_1(c_2 r c_2^{-1})c_1^{-1}` is a spike of the cyclic word `c_2 r c_2^{-1}` — hence
  `γ_N(w r w^{-1}) ≥ γ_N(r) − k`;
* therefore **AC3 by a word of length `k` cannot create thickenability from a presentation
  with `γ_N > k`**; a single-generator conjugation can create it only from `γ_N = 1`;
* by S10, an AC3 image that is thickenable via an **unnested** defect-0 system forces the
  original to be thickenable, so a "create" event requires a *nested* witness.

**Corollary T2.c (the finger/ribbon question is settled: NO).** The task's picture is that
the new 2-cell is a polygon whose two boundary arcs at the basepoint map onto the same edge
path `c` in opposite directions — a disc with a fin folded over the edge `c` — and asks
whether the fin can always be pushed into a free sector around `c`. **It cannot.**
Counterexample, verified by exact census this session:

    P  = ("xyXY", "xxy")      γ_N = 0     (thickenable)
    P' = ("xyXY", "Yxxyy")    γ_N = 1     (not thickenable)

`P'` is `P` with `r_2` conjugated by `Y = y^{-1}`; the product is freely reduced
(`r_2` starts with `x ≠ y` and ends with `y ≠ Y`), so this is a bona fide non-cancelling
single-generator AC3 move. Its defect histogram `{2:26, 4:94, 6:24}` is **identical** to
that of `R1F`'s free spike `("xyXY","yYxxy")`, as Theorem T2 predicts — the two words are
cyclic rotations of one another.

*Why the "free sector" heuristic fails.* The fin's two new germs must be inserted into the
rotation at **both** ends of the 1-handle `c`, and Neuwirth compatibility
`C_{τv} = B C_v^{-1} B` forces the insertion at `c⁻` to be the `B`-mirror of the insertion
at `c⁺`. A sector that is free at one end is the *mirrored* sector at the other; on top of
that, the fin must splice into the boundary walk of its own 2-cell at the basepoint. That
is one choice constrained in three places, and it can be jointly unsatisfiable. `R7` §1.3's
four-operation walk is the exact accounting, and its nested/unnested dichotomy is the
precise form of "does the finger have strands threaded through it". **The pinch at the
basepoint is a real obstruction, not a bookkeeping artefact.**

**Corollary T2.d (the AC-relevant version).** The counterexample above is not a presentation
of the trivial group, so a targeted run was done on presentations that are **AC-trivial by
construction** (random AC1/AC2/AC3 walks from the standard `("x","y")`, hence trivial group
and AC-trivial). Among 296 such bases with `γ_N = 0`, of 1,040 measured non-cancelling
single-generator conjugations, **170 (16.3 %) destroyed thickenability**. Example:

    ("xYY","xYxYY")    γ_N = 0    →   conjugate r_1 by x   →   ("xxYYX","xYxYY")   γ_N = 1

So AC3 can move an AC-trivial, trivial-group presentation off the Lackenby-thickenable
locus. **This is the single most consequential finding of the task**: it says
thickenability is *not* a property of a presentation-up-to-AC3, and therefore the
thickenability search must range over spellings, not over cyclically reduced
representatives. (Cf. `R1F` §"What this changes" item 1, of which this is a sharpened,
move-labelled form.)

**The cancelling case (M2c) is empirically different, and sharply so.** When `r` starts
with `c^{-1}` or ends with `c`, the AC3 word `c r c^{-1}` contains a cyclically adjacent
triple `c · c^{-1} · c` (or its mirror) — the fin is planted immediately beside an existing
strand of the same 1-handle, and the middle occurrence has a **loop of `Λ` on both of its
corners**. In 3,413 sweep pairs the predicate never flipped in either direction, and a
separate exact-value run (`m2_exact.py`, 568 bases) found `γ_N` **preserved exactly** in
all 2,230 measured cancelling conjugations (`0→0`: 931, `1→1`: 1,259, `2→2`: 40; no other
transition occurred). Compare the non-cancelling table on the same corpus: `0→0`: 773,
`0→1`: 184, `1→1`: 1,268, `1→2`: 1, `2→1`: 15, `2→2`: 25 — `γ_N` moves in both directions
there, including 15 genuine drops `2→1` (the `R7` S5 ceiling being attained), but **never
reaches 0 from above**.

> **Conjecture S6-C [OPEN].** If `c r c^{-1}` is not freely reduced (`r` begins with
> `c^{-1}` or ends with `c`), then `γ_N` of the AC3 image equals `γ_N` of the base exactly.

No proof. The natural guess is that the doubled-loop configuration always admits an
unnested defect-0 lift in `R7`'s sense, but that is not established, and the conjecture is
stated only to record a very clean measured regularity.

---

## 6. M3 — AC2 changes the space and flips the predicate in BOTH directions

AC2 `r_i → freered(r_i r_j^{±1})` is a 2-handle slide: the `i`-th 2-cell is re-attached
along a different loop, of a different length, and the multiplicity vector `m` changes for
several generators at once. It is the **only move in the list that changes the presentation
modulo (0)**, and — together with move (0) itself — the only one observed to create
thickenability. Explicit pairs from the sweep (all exact censuses, both relators of length
≥ 3, both generators used):

    DESTROY   ("xYY","xYx")     γ_N = 0  →  r_1 · r_2         ("xYYxYx","xYx")      γ_N = 1
    DESTROY   ("yyXy","XXXY")   γ_N = 0  →  r_1 · r_2         ("yyXyXXXY","XXXY")   γ_N = 1
    CREATE    ("yxxx","yXYX")   γ_N = 1  →  r_2 · r_1^{-1}    ("yxxx","yXYXXXXY")   γ_N = 0   [non-cancelling]
    CREATE    ("xyy","XYXYXX")  γ_N = 1  →  r_2 · r_1         ("xyy","XYXYXyy")     γ_N = 0   [cancelling seam]

All 73 create events in the sweep came from a base with `γ_N = 1` exactly; none from
`γ_N = 2` (20 such pairs were measured). For the **non-cancelling** grafts that is what
`R3PRIME_GRAFT_CALCULUS.md` Corollary G6 (AUDITED) predicts — a non-cancelling graft lowers
`γ_N` by at most 1, tightly. The cancelling-graft case is still outside G6's stated domain
(`R1F` records that gap explicitly), so for those rows the observation is data, not theory.

---

## 7. The measurement

**Protocol.** Random cyclically reduced rank-2 bases `(r_1, r_2)`, each relator of length
3–7, both generators used, total length 6–14, deduplicated up to rotation / inversion /
relator permutation. For each base, every image under M1, ROT (shifts 1 and 2), M4, M2
(both relators × all four conjugators, split by whether the product is freely reduced),
and M3 (`r_i r_j^{±1}`, both `i`) was decided by the exact census
`gamma_N_factorial_n` with `cap_rotations` as stated. A base was accepted only if the
predicted total census work of its whole derived family fitted a work budget, so that no
sub-family was silently truncated; a state whose own census exceeded the cap was **skipped
and counted**, never converted into a verdict.

Three sweeps: A and C in the band (relator length 3–6, total 6–11, state cap 6·10⁴,
seeds 20260804 / 555001), B in the band (length 4–7, total 11–14, state cap 9·10⁵,
seed 990804). 300 s each, run in parallel; 1,118 bases and 22,000 distinct exact complexes
in total. Scripts:
`/tmp/…/scratchpad/move_flip_sweep.py`, `actrivial_conj.py`, `stab_graft.py`,
`m2_exact.py` (scratch, not committed — the numbers below are the deliverable).

**Aggregate flip table (sweeps A + B + C).**

| move | measured pairs | skipped | destroy (`0 → >0`) | create (`>0 → 0`) | destroy rate among thickenable bases | create rate among non-thickenable bases |
|---|---|---|---|---|---|---|
| M1 (AC1 invert) | 2,236 | 0 | **0** | **0** | 0 / 720 | 0 / 1,516 |
| ROT (rotate relator) | 4,472 | 0 | **0** | **0** | 0 / 1,440 | 0 / 3,032 |
| M4 (AC4 stabilize) | 1,118 | 0 | **0** | **0** | 0 / 360 | 0 / 758 |
| **M2nc (AC3, freely reduced)** | **3,507** | 965 | **315** | **0** | **315 / 1,312 = 24.0 %** | **0 / 2,195** |
| M2c (AC3, with cancellation) | 3,413 | 1,059 | **0** | **0** | 0 / 1,272 | 0 / 2,141 |
| M3 (AC2 multiply) | 1,863 | 2,595 | **425** | **73** | 425 / 825 = 51.5 % | 73 / 1,038 = 7.0 % |

Two seeds in the same band reproduce each other closely (A: 145 destroys of 1,743 M2nc
pairs; C: 166 of 1,708), which is the only stability check the design supports.

**AC-trivial corpus** (`actrivial_conj.py`, 150 s, seed 4242): 296 AC-trivial `γ_N = 0`
bases, 1,040 measured non-cancelling conjugations, **170 destroyed thickenability, 0 could
create it** (the corpus is all-`γ_N = 0` by construction, so the create direction is not
probed there).

**Exact `γ_N` transitions under AC3** (`m2_exact.py`, 180 s, seed 31337, 568 bases,
cap 2·10⁵) — the predicate table above coarsens this:

| | `0→0` | `0→1` | `1→1` | `1→2` | `2→1` | `2→2` | `→0` from above |
|---|---|---|---|---|---|---|---|
| non-cancelling | 773 | **184** | 1,268 | 1 | 15 | 25 | **0** |
| cancelling | 931 | 0 | 1,259 | 0 | 0 | 40 | 0 |

**Stabilizer inertness** (`stab_graft.py`, 202 s, seed 777, 3,332 bases, cap 3·10⁵):
`P⁺ = (r_1, r_2, z)`, `G1 = (r_1 z, r_2, z)` and `G1i = (r_1 Z, r_2, z)` matched the base's
`γ_N` exactly in **3,332 of 3,332** triples each, as T4 and T4′ predict;
`G2 = (r_1 z z, r_2, z)` (the stabilizer used three times) differed in 2,076 of 3,332 and
flipped the predicate 1,303 times, and `Gc = (r_1 w z w^{-1}, r_2, z)` (conjugated slide)
differed in 144 of 3,321 and flipped 135 times. These are the first stabilization-derived
states that are not inert. Directions in §8.

**What the nulls are worth.** The zero entries are *exact censuses*, not heuristic
searches, so within the measured set they are exact — there is no detection-rate
calibration issue (cf. the lesson `calibrate-one-sided-hunts-on-a-positive-ladder.md`).
What they do **not** cover: (i) states above the rotation cap — 965 M2nc and 2,595 M3 pairs
were skipped, and skipping is length-biased, so all rates are rates *inside the measured
length band* (cf. `contrast-length-confound.md`); (ii) rank ≥ 3 — the whole sweep is rank 2
except for the M4/T4′ triples; (iii) AK(3) itself, whose conjugates need 3.6·10⁶–4.8·10⁶
rotation systems, over this run's cap — **[GAP-A]**, though `R1F` already measured all 39 of
its single spikes (histogram `{1:8, 2:31}`, none thickenable) at cap 2·10⁷, and by T2 those
39 *are* its single-generator AC3 images up to rotation. No p-values are quoted: the derived
states of one base are not independent draws.

---

## 8. What stabilization actually buys

Collect the inert moves. **M1 (AC1)** is a homeomorphism (T1). **ROT** and relator
permutation are homeomorphisms (T1). **M4 (AC4/AC5)** is a wedge with a disc (T4). **M4′**,
the first AC2 slide over a fresh stabilizer, is a *subdivision* (T4′). **S3 chord
refinements**, i.e. triangulation to lower relator length, are subdivisions
(`S3_SUBDIVISION_INVARIANCE.md`). **M2 (AC3) modulo (0)** is the identity up to rotation
(T2.a). What is left is:

> Along any stable AC chain, every change in the thickenability predicate is produced by
> **AC2 (M3)** and by the **choice of spelling** (M0 / the spike direction of AC3). Nothing
> else in the move set can move the predicate at all.

And the spelling direction is, as far as every measurement goes, **one-way**: reduction can
create thickenability (315 events here, plus `R1F`'s original), spiking never created it
(0 of 2,195 here, 0 of 110,917 in `R1F`). If `R7`'s Conjecture SR holds, the cyclically
reduced spelling is always at least as good as any of its spikes, the spelling direction
collapses, and

> **stable ACC becomes a statement purely about AC2**: every balanced presentation of 1
> must reach a thickenable presentation by conjugated grafts
> `r_i → cycred(r_i · w r_j^{±1} w^{-1})`, with AC1, AC3, AC4 and AC5 contributing only by
> changing *which* grafts are available.

That is what makes the AC3 result of §5 matter in the other direction too: AC3 is not a
free normalization one may apply to tidy a presentation before testing it — 24 % of the
time it *costs* the property one is testing for.

**Now the extra generators.** Stabilization adds `z` and the relator `z`. Its 2-cell is a
disc wedged at a boundary point (T4). The first thing one can do with `z` is slide it onto
another relator, `r_1 → r_1 z^{±1}` — and T4′ says **that is a subdivision too**. So after
AC4 *and* one slide, the space has not changed at all. The stabilizer becomes useful only
when it stops being a chord:

| use of the fresh `z` | multiplicity `m_z` | status |
|---|---|---|
| AC4 alone, relator `z` | 1 | inert (T4: wedge) |
| `r_i → r_i z^{±1}` (one plain slide) | 2 | inert (T4′: subdivision) |
| S3 chord refinement (`z` splits one relator) | 2 | inert (Theorem S3: subdivision) |
| `r_i → r_i z^{±1} z^{±1}`, or slides onto two different relators | ≥ 3 | **not inert** — `z` is a triple line |
| `r_i → r_i · w z^{±1} w^{-1}` (conjugated slide) | 2, but `m_g` rises by 2 for every letter `g` of `w` | **not inert** — it is a graft composed with `|w|` spikes |

Measured (`stab_graft.py`, 3,332 bases, cap 3·10⁵): `P⁺`, `G1` and `G1i` reproduced the
base's `γ_N` exactly in 3,332/3,332 each — the inert rows are inert to the last case.
`G2` (`m_z = 3`) changed `γ_N` in 2,076 of 3,332 and flipped the predicate 1,303 times;
`Gc` (conjugated slide) changed it in 144 of 3,321 and flipped 135 times. Directions, from
the companion run `stab_dir.py` (seed 8888):

| exact `γ_N` transition | `0→0` | `0→1` | `1→1` | `1→2` | `2→1` | `2→2` | `2→3` | `→0` from above |
|---|---|---|---|---|---|---|---|---|
| `G2 = (r_1 z z, r_2, z)` | 29 | **1,248** | 1,060 | 722 | 0 | 49 | 1 | **0** |
| `Gc = (r_1 w z w^{-1}, r_2, z)` | 1,146 | **126** | 1,779 | 1 | 8 | 42 | 0 | **0** |

(3,109 bases, seed 8888, cap 3·10⁵.) The split T4′ predicts is a clean line, not a
gradient: the inert uses of `z` are inert with zero exceptions, and `G2` — the first use in
which `z` becomes a triple line — destroys thickenability in 1,248 of the 1,277 thickenable
bases it was applied to.

**And in one step it never bought anything.** Neither `G2` nor `Gc` produced a single
`γ_N > 0 → 0` transition in 3,109 + 3,109 measurements. That is a genuine, and
uncomfortable, null: the *only* moves in the whole classification that created
thickenability anywhere in this session were plain rank-2 AC2 slides (73 events) and move
(0) reductions (315 events). **[GAP-1STEP]** Read it for exactly what it is: two specific
one-step families, in one length band, at rank 3, with `z` used in one specific arrangement.
It is *not* evidence that `m_z ≥ 3` states are useless — S3 §4's cubic regime is a large
region of `m_z ≥ 3` space that no one-step schedule reaches, and a null on a one-step
neighbourhood says nothing about a many-step one (the same bound-direction discipline as
`parallel-runs-and-bound-direction.md`). What it does say is that *stabilization pays, if at
all, over a schedule and not at the first non-inert step* — so search budgets should not be
spent on one-step rank-3 neighbourhoods of rank-2 states.

This sharpens `S3_SUBDIVISION_INVARIANCE.md`'s escape hatch (its §4: "extra generators buy
nothing while they are used as abbreviations") into a move-level statement:

> **Stabilization can buy at most two things.** (a) A *new relator* `z` that can be
> grafted, so that conjugated grafts `r_i → r_i · w z^{±1} w^{-1}` become available which
> were not available at lower rank. (b) A *new edge* which, once it carries three or more
> germs, changes the local topology of the space in a way no rank-`n` move can. The extra
> generator itself is worth nothing: as a bare stabilizer (T4), as an abbreviation (S3), and
> as the target of one plain slide (T4′), it is **provably inert**.

The inert half of that statement is proved; the useful half is only an opening, and
[GAP-1STEP] says the opening was not cashed in one step anywhere we looked. The practical
reading for the route portfolio:

* a stabilization schedule that adds `z` and then uses it once is a **guaranteed no-op** and
  should never be searched — that is a proof (T4, T4′), not a heuristic;
* budgets belong on schedules that reach `m_z ≥ 3` in a *structured* way — the cubic regime
  of S3 §4 — rather than on the naive `r_i → r_i z z`, which measured at 1,248 destructions
  and 0 gains;
* conjugated grafts with `z` pay for their conjugation in spikes. By `R7` S5, each letter of
  `w` can raise `γ_N` by up to 2 (proved; empirically at most 1) and can lower it by at most
  1. **Note the asymmetry and its direction**: conjugation is cheap to lose by and expensive
  to gain by, so long conjugators are a bad bet unless the graft they enable is worth more
  than the spikes they cost.

---

## 9. Gaps, and traps added to the line

**[GAP-O]** `γ_N = 0` decides *orientable* thickenability (Theorem D). Lackenby Thm 1.3's
hypothesis is embedding in *some* 3-manifold. T1, T4 and T4′ are proved for arbitrary `M`,
so the classification of the inert moves is unaffected; every *measured* row is about
orientable thickenability only.

**[GAP-SR]** Whether move (0) can destroy thickenability (equivalently, whether AC3 can
create it) is `R7`'s Conjecture SR and is open. It is the hinge of §8's collapse to "stable
ACC is a statement about AC2". `R7` S5 bounds the damage to one unit and S10 settles the
unnested case; the nested case is what remains.

**[GAP-A]** AK(3)'s own single-generator AC3 images are above this run's rotation cap.
By T2 they coincide, up to rotation, with `R1F`'s 39 single spikes, all of which were
censused there (`{1:8, 2:31}`, none thickenable) — so the gap is only in *this* run's
independent coverage, not in the repo's knowledge. Iterated (depth ≥ 2) AC3 images of AK(3)
are genuinely unmeasured.

**[GAP-M2c]** The complete inertness of the *cancelling* AC3 case (0 flips in 3,413 pairs,
exact `γ_N` preserved in every measured case) has no proof.

**[GAP-T]** The empirical corpus is not restricted to presentations of the trivial group,
except in the `actrivial_conj.py` run. This is deliberate — the move classification is a
statement about word-realized complexes, at which level the AC moves act identically — but
the flip *rates* are rates over a corpus of arbitrary balanced rank-2 presentations, not
over the AC class of any particular presentation.

**Traps for the standing list:**

* **T-S8.** AC3 is not a normalization. "Conjugate to a nicer form, then test
  thickenability" destroys the property 24 % of the time on a thickenable base. Any
  pipeline that conjugates before deciding must re-decide after.
* **T-S9.** A move being trivial *on the group*, or even trivial *modulo move (0)*, says
  nothing about its effect on `|K|`. AC3 modulo (0) is the identity and AC3 alone flips the
  predicate; both statements are true simultaneously because `γ_N` is a function of the
  spelling.
* **T-S10.** "More generators" remains not a mechanism (S3's T-S7), and now with a
  sharper threshold: the stabilizer is inert through its first plain slide as well
  (T4′). Any proposal must say how many times its new generator occurs **and** whether the
  slides that introduce it are conjugated.

---

## 10. Reproduction

```
PYTHONPATH=/home/user/ACSolverX python - <<'PY'
from experiments.stable_ac.fable.neuwirth_rank_n import gamma_N_factorial_n
for w in [("xyXY","xxy"), ("xyXY","yYxxy"), ("xyXY","Yxxyy")]:
    r = gamma_N_factorial_n(w, cap_rotations=2_000_000, keep_accepting=False)
    print(w, r["expected_cases"], r["defect_histogram"], "gamma_N =", r["minimum_genus"])
PY
```

expected output:

```
('xyXY', 'xxy')    12  {0: 2, 4: 4, 2: 6}       gamma_N = 0
('xyXY', 'yYxxy')  144 {2: 26, 4: 94, 6: 24}    gamma_N = 1
('xyXY', 'Yxxyy')  144 {4: 94, 2: 26, 6: 24}    gamma_N = 1
```
