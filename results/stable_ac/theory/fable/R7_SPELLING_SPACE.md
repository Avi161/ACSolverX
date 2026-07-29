# R7 — Spelling space: the spike calculus, the spike ceiling, and what γ\* can and cannot buy

STATUS: proofs below are DRAFTS that have survived the author's own adversarial pass plus
machine verification; they have NOT yet been through an independent adversarial audit, so
per the standing rule they are results-in-waiting, not results. Every numerical claim is
machine-checked and the checking code is described well enough to regenerate.

Claims addressed, per lemma (FRAMING.md tags):

| item | claim class |
|---|---|
| S1–S5, S8–S10, M1–M2 | **MACHINERY** (properties of exact word-realized complexes) |
| B, B1 | **MACHINERY** + topology (embedding ⟺ spine of B³) |
| B2, B3 | **AC-trivial** / **stably AC-trivial** (both carry external citations) |
| A1 (the AC-trivial γ_N = 1 examples) | **AC-trivial** (certified by construction) |
| Conjectures U, SR, R | MACHINERY, unproved |

Nothing in this note claims anything new about AK(3)'s AC-triviality or stable
AC-triviality in either direction. What it does claim about AK(3) is a **spelling-depth
lower bound** (Corollary S6) and, conditionally on Conjecture SR, the exact value
γ\*(AK(3)) = 1.

Dependencies cited, not re-proved: the occurrence dictionary / involutions A, B /
compatible rotations / Lemma 1 (Euler dictionary) of `lit_AK3_NEUWIRTH.md`; Theorem D and
Lemma L0 of `R1E_DISCONNECTED_LINK.md` (AUDITED); Lemma G4 of
`R3PRIME_GRAFT_CALCULUS.md` (AUDITED — re-derived here in the loop-bearing case, §1.3);
`GAMMA_N_SYMMETRY_LEMMA.md` (AUDITED); the exact censuses of `R1F_REDUCTION_AND_SPIKES.md`.

---

## 0. Conventions, the object γ\*, and the scope repair

**Conventions.** `|Q|` = number of cycles of a permutation including fixed points;
products act right-to-left; the **UNHALVED** defect is
`defect(C) = |A| − |C| + 2L − |AC|` and `γ_N = min_C defect(C)/2`;
`gamma_N_factorial_n` returns `minimum_defect = 2·γ_N`. For a letter `a`, `dep(a)` and
`arr(a)` are its departure and arrival germs, with `dep(g) = g⁺`, `arr(g) = g⁻`,
`dep(g⁻¹) = g⁻`, `arr(g⁻¹) = g⁺`; note `arr(a) = dep(a⁻¹)`. Occurrence `i` carries darts
`d_i` (at `dep(a_i)`) and `h_i` (at `arr(a_i)`); `B` swaps them; the corner involution `A`
pairs `h_i` with `d_{i+1}` cyclically inside each relator. Λ(P) is the link multigraph
(vertices = germs, one edge per corner).

**MOVE-NUMBERING TRAP.** `FRAMING.md` uses AC1 = multiply, AC2 = invert; `R1E`,
`R3PRIME` and this note use the *operating-contract* numbering AC1 = invert,
AC2 = multiply, AC3 = conjugate, AC4/AC5 = (de)stabilize, (0) = free/cyclic reduction.
Below, moves are always named in words as well as by number.

**Spike.** `SPIKE(P; j, k, u)` replaces the cyclic relator
`w_j = a_0 … a_{N−1}` by `a_0 … a_{k−1} · u · u⁻¹ · a_k … a_{N−1}` (indices mod N).
Write `g = |u|`, `s = dep(u)`, `t = arr(u)` — the two germs of `g`, always distinct — and
let `p, q` be the two new occurrences (letters `u`, `u⁻¹`). A spike is the inverse of one
step of Lackenby's move (0).

**Standing hypothesis (H):** `g` occurs in `P` (so `deg_P(s) = deg_P(t) = occ_P(g) ≥ 1`).
This holds automatically in the Neuwirth setting whenever the spike re-uses an existing
generator, which is the only case relevant to spelling space (a spike with a fresh letter
changes the generating set and is a different move; it is excluded here).

**Spelling space and γ\*.** The exact complex sees each relator only as a CYCLIC word.
Two cyclic words are *spellings of the same relator* iff they have the same cyclic
reduction; every spelling is obtained from the cyclically reduced one by a finite sequence
of spikes, and conversely. Define

    γ*(P) = min { γ_N(K) : K a spelling complex of P }.

γ\* is well defined on tuples of free-group elements, is invariant under relator inversion
(AC1), relator permutation and **conjugation (AC3)** — conjugation does not change the
cyclic word class at all — and satisfies γ\*(P) ≤ γ_N(P_red). R1F proved
γ\*(AK(3)) ≤ 1 < 2 = γ_N(AK(3)), so the inequality is strict in the one case we care about.

**SCOPE REPAIR (the load-bearing step the orchestrator flagged).**
`R3PRIME_GRAFT_CALCULUS.md` §0 restricts the graft calculus to *cyclically reduced*
factors with a *non-cancelling* seam (NC). Spiked spellings violate both by construction:
they are not reduced, and the spike's own corner `ℓ = {h_p, d_q}` is an **A-loop**.
Corollary G6 as written therefore does **not** cover spikes, and citing it would be an
error. What follows does **not** cite G2, G3, G5 or G6. It re-derives each of them for the
spike from scratch, and isolates the single external ingredient — Lemma G4, the elementary
insertion/deletion dichotomy — whose proof is checked below to be loop-safe (§1.3).
R3PRIME's audit repair F1 ("G2–G6 never need looplessness") is consistent with this, but
it was a remark, not a checked statement; §1.3 checks it.

---

## 1. Q2 — exactly how the Neuwirth defect changes under ONE spike

### 1.1 Bookkeeping

**Theorem S1 (exact spike bookkeeping) [MACHINERY].** Under (H), with
`X := arr(a_{k−1})`, `Y := dep(a_k)` and `e_0 := {h_{k−1}, d_k}` the corner of `w_j`
between positions `k−1` and `k`:

1. **Length / darts / corners.** `|A′| = |A| + 2`, `|E′| = |E| + 4`.
   The corner set changes by exactly one deletion and three insertions:

       DELETE  e_0 = {h_{k−1}, d_k}                  (the edge X — Y of Λ(P))
       ADD     J₁ = {h_{k−1}, d_p}                   (edge X — s)
       ADD     ℓ  = {h_p,      d_q}                  (a LOOP at t)
       ADD     J₂ = {h_q,      d_k}                  (edge s — Y)

   so `|A′| = |A| − 1 + 3 = |A| + 2`. ✔
2. **Germ degrees.** `deg′(s) = deg(s) + 2`, `deg′(t) = deg(t) + 2`, every other germ
   unchanged. Reason: each unsigned occurrence of `g` contributes exactly one dart at
   `g⁺` and one at `g⁻`, and the spike adds two occurrences of `g`.
3. **Present germs / |C|.** Unchanged, so `|C′| = |C| = #present germs` for every
   compatible rotation. (This is where (H) is used: without it `s, t` would be fresh.)
4. **Components.** `L′ = L − δ`, where `δ = 1` iff `s` lies in a different Λ(P)-component
   from `X`, else `0`. *Proof:* deleting `e_0` cannot disconnect `X` from `Y`, because
   `J₁, J₂` restore a path `X — s — Y`; the only possible change is the merge of
   `comp(s)` into `comp(X) = comp(Y)`, which happens iff they were distinct. The loop `ℓ`
   adds no connectivity (`t` is already present by (H)). By Lemma L0 of R1E, `L` is
   C-independent on both sides, so `δ` is read off the words. In particular `L′ = L`
   whenever Λ(P) is connected — the AK(3) case.
5. **Census size.** `|𝒞(P′)| = |𝒞(P)| · D(D+1)` with `D = deg_P(g⁺) = occ_P(g)`,
   because `census_size = ∏_g (deg(g⁺) − 1)!` and `(D+1)!/(D−1)! = D(D+1)`.
6. **Loops.** `ℓ` is the only loop the spike creates, and A-loops correspond bijectively
   to cyclically adjacent cancelling pairs (the corner `(a_i, a_{i+1})` is a loop iff
   `arr(a_i) = dep(a_{i+1})` iff `a_{i+1} = a_i⁻¹`). So every non-reduced spelling is
   loop-bearing, the R1c-v2 cut-scheme solver fails closed on all of them, and only a
   census or an explicit witness decides them. This is the structural reason R1F had to
   census the 39 AK(3) spikes rather than solve them.

*Numerical anchor, independent of R1F's code.* AK(3) has `D_x = 6`, `D_y = 7`, census
`5!·6! = 86,400`. S1(5) predicts a single **x**-spike to have census
`86,400 · 6 · 7 = 3,628,800` and a single **y**-spike `86,400 · 7 · 8 = 4,838,400`.
R1F reports precisely these two numbers for its eight γ_N = 1 gateway spikes, "six of
them" at 3,628,800 and "two" at 4,838,400 — and reading the eight verbatim spellings,
exactly six insert an `x`-pair and exactly two insert a `y`-pair. Formula and experiment
agree case by case.

### 1.2 The spike fibration

**Theorem S2 (fibration) [MACHINERY].** Under (H) the restriction map

    ρ : 𝒞(P′) → 𝒞(P),   ρ(C′) = C′ with the four spike darts deleted from each germ cycle,

is well defined and surjective, with all fibres of size `D(D+1)`.

*Proof.* The deleted set is `{d_p, h_q}` at `s` and `{h_p, d_q}` at `t`. It is a union of
whole occurrences, hence **B-closed**, and its two halves correspond under `B`:
`B(d_p) = h_p`, `B(h_q) = d_q`. That is the only property the G2 argument uses: deletion
of a subset from a cyclic sequence commutes with elementwise `B` and with reversal, so the
B-reversal law `C_{g⁻} = B C_{g⁺}⁻¹ B` survives restriction. Every germ retains at least
one dart by (H), and germ fibres are preserved, so `ρ(C′)` is compatible for `P`.
Surjectivity and uniformity: at `g⁺` the degree goes `D → D+2`, and the number of cyclic
orders on a `(D+2)`-set restricting to a fixed cyclic order on a distinguished `D`-subset
is `(D+1)!/(D−1)! = D(D+1)` — the *cyclic*, not linear, count; the `g⁻` cycle is then
forced, and no other generator is touched. ∎

**(NC) and looplessness are used nowhere in this proof.** That is the scope repair for
G2/G3.

### 1.3 Lemma G4 is loop-safe

**Lemma S3 [MACHINERY].** Lemma G4 of R3PRIME holds verbatim for ribbon graphs with loops
and parallel edges. Inserting one edge at prescribed rotation slots changes
`def(R) = e − v + 2c − f` by `0` or `+2`, and by `+2` exactly when both germs already
carry darts and the two slots lie on **distinct boundary circles of the same component**;
deleting one edge changes `def` by `0` or `−2`, mirror-wise.

*Why looplessness is not needed:* G4's proof attaches an untwisted band along two boundary
arcs and counts boundary circles. It never reads the identity of the two endpoint germs.
For a loop both feet are at one vertex, hence automatically in one component, so only the
sub-cases "same circle" (`Δ = 0`, a monogon or a face split) and "distinct circles of one
component" (`Δ = +2`) can occur; the "distinct components" branch is vacuous. Orientability
(untwisted bands, Heffter–Edmonds) is what excludes the Möbius attachment, and it holds
here because compatible rotation systems are by construction orientable.

*Machine check:* the loop-insertion step was traced dart-by-dart in every compatible
rotation system of seven spikes across five base presentations (234 systems); it took the
value `0` or `+2` and nothing else, in every case; the deletion step took `0` or `−2`.

### 1.4 The master formula

**Theorem S4 (spike master formula) [MACHINERY].** Fix `C′ ∈ 𝒞(P′)`, let `C = ρ(C′)`, and
run the canonical interpolation, each stage carrying `C′` restricted to its dart set:

    R₀ = ribbon graph of (P, C)                       def(R₀) = defect(C)
    op 1   DELETE e_0                        → R₁     Δ ∈ {0, −2}
    op 2   INSERT ℓ   (the loop at t)        → R₂     Δ ∈ {0, +2}
    op 3   INSERT J₁                         → R₃     Δ ∈ {0, +2}
    op 4   INSERT J₂                         → R₄     Δ ∈ {0, +2}
    R₄ = ribbon graph of (P′, C′)                     def(R₄) = defect′(C′)

Then

    defect′(C′)  =  defect(ρ(C′))  −  2·X⁻(C′)  +  2·X⁺(C′),
        X⁻ ∈ {0, 1},   X⁺ ∈ {0, 1, 2, 3}.

`X⁻ = glower(C; e_0)` is **pre-spike-readable**: op 1 acts on `R₀`, the ribbon graph of the
*unspiked* complex, so `X⁻` depends only on `C` and on which corner of `w_j` the spike
splits. `X⁺` is the number of genus-raising insertions among ops 2–4 and depends on the
fibre coordinate. In face-count form, using S1,

    |A′C′| − |AC|  =  2 − 2δ + 2X⁻ − 2X⁺,

which is the complete term-by-term answer to Q2: `|A|` rises by 2, `|C|` is fixed, `2L`
falls by `2δ`, `n_occurrences` rises by 2, `present_germs` is fixed, and the whole of the
remaining freedom sits in `|AC|` through the four-op walk. ∎

*Machine check:* the walk was traced for **every** compatible rotation system of seven
spikes (234 systems, 820 assertions in total including S1 and S2): every op landed in its
predicted set, `def(R₀)` equalled `defect(ρ(C′))` in every case, and `def(R₄)` equalled the
dictionary defect of `(P′, C′)` in every case.

### 1.5 The spike ceiling

**Corollary S5 (THE SPIKE CEILING) [MACHINERY].** Under (H),

    γ_N(spike(P))  ≥  γ_N(P) − 1,      and      γ_N(spike(P))  ≤  γ_N(P) + 2.

*Proof.* Lower: pointwise `defect′(C′) ≥ defect(ρ(C′)) − 2 ≥ 2γ_N(P) − 2`; minimise over
`C′`. (Surjectivity of ρ is not needed for this half.) Upper: take `C` attaining the pre
minimum and build `C′ ∈ ρ⁻¹(C)` (non-empty by S2) with `d_p, h_q` inserted **adjacently**
into a single corner of `s`; then `h_p, d_q` are adjacent at `t` by B-reversal, so op 2
inserts `ℓ` into one corner and creates a monogon: `Δf = +1`, `Δ = 0`. Only ops 3 and 4
can raise, so `defect′ ≤ defect(C) + 4`. ∎

Iterating gives `γ_N(spike^k(P)) ≥ γ_N(P) − k`.

**TIGHTNESS of the −1, and what it says about R1F's gateways.** The `−1` cannot be
improved to `0`: `γ_N(AK(3)) = 2` (exact census, 86,400 cases, pinned test fixture) and
eight of its 39 distinct single spikes have `γ_N` exactly `1` (R1F, exhaustive census at
100 % coverage, cross-checked by independent defect-2 witnesses). So the eight gateways are
**the ceiling being attained**, not a lucky find; and their value is pinned from below by
S5 without any census at all — the census only had to rule out `γ_N = 0`, which S5 now also
does (next corollary). The `+2` side is not known to be attained; R1F's 110,917 measured
spiked complexes never show a single spike raising `γ_N` by more than 1. See Conjecture R.

**Corollary S6 (spelling depth at AK(3)) [MACHINERY].** Since `γ_N(AK(3)) = 2`:

* every spelling of AK(3) at spike-depth `≤ 1` has `γ_N ≥ 1`; in particular **no single
  spike of AK(3) is thickenable**. This is a *proof* of what R1F established by two
  exhaustive censuses over 3.6M and 4.8M rotation systems.
* every spelling at spike-depth `≤ 1` in fact has `γ_N ∈ {1, 2}`, and R1F's exhaustive
  histogram `{1: 8, 2: 31}` shows both values occur.
* a thickenable spelling of AK(3), if one exists, has **spike-depth ≥ 2**.

**Corollary S7 (the ceiling cannot answer Q3) [MACHINERY].** Spelling space is the set of
spike-images of the cyclically reduced spelling, and is infinite. Iterating S5 gives
`γ_N(spike^k(P)) ≥ γ_N(P) − k`, which is vacuous as soon as `k ≥ γ_N(P)`. Hence the
interpolation/ceiling method yields **no** unconditional lower bound on `γ*(P)` beyond
`γ* ≥ 0`. Any bound on γ\* must come from a mechanism that does not degrade per spike.
§3 supplies exactly such a mechanism, for the value 0 only.

---

## 2. Why spikes help at all — the monogon budget

This subsection explains mechanically what R1F observed empirically, and kills the whole
family of *counting* candidates suggested for Q1.

**Lemma M1 (monogons come only from cancelling pairs) [MACHINERY].** For any rotation
system, a face of degree 1 is a fixed point of `AC`, i.e. a dart `d` with `C(d) = A(d)`;
this forces `ν(A(d)) = ν(d)`, i.e. the corner `{d, A(d)}` is a **loop** of Λ, and loops of
Λ are exactly the cyclically adjacent cancelling pairs of the spelling (S1(6)). Each loop
edge carries at most 2 darts, so

    #(faces of degree 1)  ≤  2 · #(cancelling adjacent pairs of the spelling),

and a cyclically reduced spelling has **no** faces of degree 1. ∎

**Lemma M2 (the face-degree budget, and why it relaxes under spiking) [MACHINERY].**
If `defect(C) = 0` then `f := |AC| = |A| − |C| + 2L`, while `Σ_faces deg = 2|A|`. Writing
`f_1, f_2, f_{≥3}` for the face counts by degree,

    2·f_1 + f_2  ≥  3f − 2|A|  =  |A| − 3|C| + 6L.

For reduced AK(3) (`|A| = 13`, `|C| = 4`, `L = 1`, `f_1 = 0` by M1) this demands
`f_2 ≥ 7` out of only `f = 11` faces: at least seven of the eleven faces of a hypothetical
thickenable rotation must be bigons. One spike changes the arithmetic to
`|A| = 15`, `f = 13`, requirement `9`, allowance `2f_1 ≤ 4` — so the demand on bigons drops
from 7 to 5. **Each spike raises the requirement by 2 but raises the monogon allowance by
up to 4.** Every counting bound of this shape therefore *relaxes* under spiking and can
never be spelling-independent. ∎

That is the precise sense in which spikes "buy" thickenability: a monogon is a free face,
and the only source of monogons is a cancelling pair.

---

## 3. Q1 and Q3 — the reduction theorem, proved under one hypothesis

The only mechanism found that does not degrade per spike controls the **value 0** — which
is the value that matters, since `γ* = 0` is the whole question.

**Definition (nested / unnested).** For `C′ ∈ 𝒞(P′)` call the spike **unnested under C′**
if the two new darts `d_p, h_q` are cyclically adjacent in `C′|_s`. Writing
`C′|_s = (z_1 … z_M)` with `z_α = d_p`, `z_β = h_q`, compatibility forces
`C′|_t = (Bz_M, …, Bz_1)`, so the old darts strictly between `h_q` and `d_p` at `s` are
exactly the `B`-images of the old darts strictly between `h_p` and `d_q` at `t`; hence
"unnested at `s`" and "unnested at `t`" are the same condition. **Nested** means old
occurrences of `g` sit on both sides — the spike's finger has strands threaded through it.

**Lemma S8 (subgraphs of a spherical ribbon graph) [MACHINERY].** If `def(R) = 0` then
`def(R − e) = 0` for every edge `e`; hence every sub-ribbon-graph of a `def`-0 ribbon graph
has `def` 0. *Proof:* deletion moves `def` by `0` or `−2` (S3), and `def ≥ 0`. ∎

**Lemma S9 (cofaciality survives deletion) [MACHINERY].** Let `def(R) = 0` and let `α, β`
be corners of `R`. Write `α ≍ β` for "α and β lie on one boundary circle, **or** at germs
in different components". If `α ≍ β` in `R`, then `α ≍ β` in `R − e` for every edge `e`
(corners merging in the obvious way when a dart disappears).

*Proof.* `def(R − e) = 0` by S8, so the genus-lowering deletion branch of S3 (both sides of
`e` on one circle, deletion non-disconnecting, `Δ = −2`) is impossible. The surviving
branches are: (i) the two sides of `e` lie on distinct circles — the deletion **merges**
those two circles, leaves all others and all components alone, so `≍` is preserved and only
improves; (ii) `e` is a bridge, its two sides lie on one circle `f` — `f`'s boundary walk
crosses `e` exactly twice, so it splits into one closed walk per new component, whence two
corners of `f` in the same new component stay on one circle and two in different components
are `≍` by the component clause; (iii) pendant / isolated-edge deletions do not split
circles. Finally, when a dart `a` disappears, the two corners flanking it merge, and those
two corners sit on the two sides of `e`, which case (i) has just merged into one circle. ∎

**Theorem S10 (reduction under unnesting) [MACHINERY].** Let `C′ ∈ 𝒞(P′)` with
`defect′(C′) = 0` and the spike **unnested** under `C′`. Then `defect(ρ(C′)) = 0`;
in particular `γ_N(P) = 0`.

*Proof.* `R₄` has `def` 0, hence so does every `R_i` (S8); in particular `def(R₁) = 0`
where `R₁ = Λ(P) − e_0` with rotation `ρ(C′)`. Since `defect(ρ(C′)) = def(R₁ + e_0)` and
insertions move `def` by `0` or `+2` (S3), it suffices to show that the `R₁`-slot of
`h_{k−1}` at `X` and the `R₁`-slot of `d_k` at `Y` satisfy `≍` in `R₁`. (If `X` or `Y`
retains no other dart, the insertion is pendant or isolated and `Δ = 0` outright, so assume
both retain darts.) Put `v = C′⁻¹(h_{k−1})`, `v′ = C′(h_{k−1})` at `X` and
`w = C′⁻¹(d_k)`, `y′ = C′(d_k)` at `Y`; the two `R₁`-slots are the corners `(v, v′)` and
`(w, y′)`.

Unnesting gives `C′(h_q) = d_p` or `C′(d_p) = h_q`. Let `φ = A′C′` be the face permutation
of `R₄`, so the step `z ↦ φ(z)` traverses the corner `(z, C′(z))`.

*Case `C′(h_q) = d_p`.*  `φ(w) = A′(d_k) = h_q`, `φ(h_q) = A′(d_p) = h_{k−1}`,
`φ(h_{k−1}) = A′(v′)`. So a single boundary circle of `R₄` traverses, consecutively, the
corner `(w, d_k)` at `Y`, the corner `(h_q, d_p)` at `s`, and the corner `(h_{k−1}, v′)` at
`X`. Hence `α₀ := (h_{k−1}, v′)` and `β₀ := (w, d_k)` are cofacial in `R₄`.

*Case `C′(d_p) = h_q`.*  Symmetrically `φ(v) = A′(h_{k−1}) = d_p`, `φ(d_p) = A′(h_q) = d_k`,
`φ(d_k) = A′(y′)`, so `α₁ := (v, h_{k−1})` and `β₁ := (d_k, y′)` are cofacial in `R₄`.

Now delete `ℓ, J₁, J₂` to reach `R₁`. By S9 the relation `≍` survives each deletion; when
`h_{k−1}` goes (with `J₁`) the corners `(v, h_{k−1})` and `(h_{k−1}, v′)` merge into the
`R₁`-slot of `h_{k−1}`, and when `d_k` goes (with `J₂`) the corners `(w, d_k)` and
`(d_k, y′)` merge into the `R₁`-slot of `d_k`. Either case therefore delivers
slot`_X` `≍` slot`_Y` in `R₁`, so inserting `e_0` is not genus-raising and
`def(R₀) = def(R₁) = 0`. ∎

*Machine verification of S10.* Exhaustive over all cyclically reduced 2-relator bases on
`{x, y}` of total length 6 (1,400 bases) and all of their single spikes: **115,264**
compatible rotation systems of spiked complexes had `defect′ = 0` **and** were unnested;
in **every one** of them `defect(ρ(C′)) = 0`. Zero violations. The hypothesis is not
decoration: **12,736** nested `defect′ = 0` rows also occurred, and **4,288** of those had
`defect(ρ(C′)) = 2`. So the naive statement "ρ preserves defect 0" is FALSE, and unnesting
is exactly what repairs it.

### 3.1 The two conjectures

**Conjecture U (unnesting).** Every spiked complex with `γ_N = 0` admits an **unnested**
defect-0 rotation system.

**Conjecture SR (spelling reduction).** `γ_N(spike(P)) = 0 ⇒ γ_N(P) = 0`; i.e. if a spelled
complex is thickenable, so is the complex one free reduction closer to reduced.

By Theorem S10, **U ⇒ SR**. (The converse is not claimed: SR could hold for another reason.)

**Evidence for U and SR.**
* U: 23,328 of 23,328 spiked complexes with `γ_N = 0` at total length 6 possess an unnested
  defect-0 witness — no exception. (Same run as above.)
* SR: R1F's 110,917 measured spiked complexes contain zero counterexamples; every one of
  the 13,976 spiked complexes with `γ_N = 0` descends from a base already at `γ_N = 0`; the
  2,514 bases sitting at `γ_N = 1` produced ≈ 58,000 spikes and not one reached 0; all 464
  observed strict drops are `2 → 1`.
* This note's independent re-derivation, by a different method (randomized defect-0 witness
  hunt rather than census — the correct bound direction, since 0 is the floor so an upper
  bound of 0 is exact): exhaustive over total length 8 (77 canonical bases, 48 of them with
  `γ_N ≥ 1`, 1,080 spiked complexes tested) — **0 counterexamples**; and over the 12
  certified AC-trivial states of §5 — **0 counterexamples**. The witness hunter was
  calibrated first on seven anchors of known γ_N including AK(3) itself and two of R1F's
  gateway spikes (where the minimisers are 2-in-3.6M needles): it reproduced all seven
  exactly.
* The converse of SR is FALSE and has a verified counterexample: R1F's
  `("xyXY","xxy")` (γ_N = 0) → `("xyXY","yYxxy")` (γ_N = 1). So the implication is genuinely
  one-directional; that asymmetry is what makes SR believable rather than a symmetry.

**Where a proof of U would have to come from.** In the nested case the spike's finger has
`a ≥ 1` old `g`-strands threaded on one side and `b ≥ 1` on the other. Since `def(R₄) = 0`,
the loop `ℓ` at `t` is then a **separating** curve in the sphere: the `a`-side and `b`-side
neighbours of `t` lie in different components of `R₄ − t`. That is a strong structural
constraint on nested defect-0 systems and is the natural place to look for either a proof
of U (show a nested witness can always be re-threaded into an unnested one at equal defect)
or a counterexample (build a nested defect-0 system whose every re-threading raises the
defect). The author could not close either direction.

### 3.2 What SR would deliver

**Corollary (conditional on SR) [MACHINERY].** For every `P` all of whose relators are
non-trivial in `F`, `γ*(P) = 0 ⟺ γ_N(P_red) = 0`. *Proof:* every spelling is `spike^k` of
the cyclically reduced spelling; apply SR `k` times, the induction terminating at the
cyclically reduced word (it cannot terminate at a freely trivial relator, excluded by
hypothesis). ∎

**Corollary (conditional on SR).** `γ*(AK(3)) = 1` exactly: `≥ 1` because
`γ_N(AK(3)) = 2 ≠ 0`, and `≤ 1` by R1F's eight gateway spikes. **No spelling of AK(3) is
thickenable**, and the entire spelling-space route to a thickenable AK(3) is closed.

**Corollary (conditional on SR) — the real payoff.** Every NOT_SPHERICAL verdict in this
project's corpus (≈ 17,100 exact complexes across ranks 2–3) is currently a statement about
one exact realization. Under SR each one upgrades to a statement about the whole infinite
spelling family of that state, and the 150 undecided loop-bearing rows of
`gateway_neighborhood.json` are decided by their reductions. That is the retroactive
strengthening R1F identified as the prize; SR is exactly the missing lemma.

---

## 4. Q1 — the other candidate invariants, and why each dies

Q1 asked for `I(P)` with `γ_N(K) ≥ I(P)` for every spelling `K`. Candidates examined:

| candidate | verdict |
|---|---|
| `\|A\|`, `\|C\|`, `L`, `\|AC\|` separately | **dead.** S1 gives the exact compensating motions: `\|A\| += 2`, `\|C\|` fixed, `2L −= 2δ`, and all remaining freedom is inside `\|AC\|`. No individual term is spelling-stable. |
| parity / mod-2 residues | **dead.** `defect ≡ \|A\| − \|C\| − \|AC\| (mod 2)` is always 0 because `defect = 2·Σ genus`; there is no residue left to carry information. |
| face-degree counting bounds | **dead, and quantifiably so** (Lemma M2): each spike raises the requirement by 2 and the monogon allowance by up to 4, so every bound of this shape relaxes under spiking. |
| planarity of the link Λ(P) | **vacuous at rank 2.** Λ has `2n` vertices; a multigraph on ≤ 4 vertices is always planar (loops and parallel edges never obstruct planarity, and `K₅`, `K_{3,3}` need ≥ 5 vertices). So at rank 2 the *entire* content of the criterion is the rotation/B-reversal condition, not planarity. At rank ≥ 3 planarity of Λ is a real condition but is itself spelling-dependent (a spike deletes `X—Y` and routes through the existing vertex `s`, which is not a subdivision). |
| van Kampen / deleted-product obstruction | **not applicable.** The classical van Kampen obstruction obstructs embedding an `n`-complex in `R^{2n}`, i.e. a 2-complex in `R⁴`, not in `R³`. |
| homological obstruction to embedding | **dead by contractibility.** `K` is acyclic (§6), so no homological invariant of `K` can obstruct anything; any obstruction must be about the embedding itself, i.e. exactly the rotation system. |
| the `∂N ≅ S²` condition | **no extra content.** For a balanced trivial-group presentation, `defect = 0` already forces `∂N ≅ S²` homologically (§6); R1E's `⟨AC, BC⟩`-transitivity test adds nothing beyond `γ_N = 0` and is in any case rescoped to `L = 1`. |
| **the spike interpolation itself** | **degrades** (S7): `−1` per spike, vacuous after `γ_N(P)` spikes. |
| **Conjecture SR** | the only surviving mechanism; it does not degrade, but it controls only the value `0` — which is, however, the only value that matters. |

**Verdict on Q1.** There is no spelling-independent lower bound in the "counting /
homological / parity" families, and the reason is structural, not a failure of ingenuity:
spikes buy faces (monogons) at a better exchange rate than they cost edges. The one
mechanism that survives is the *cofaciality* argument of §3, and it delivers a
spelling-independent lower bound of the only kind that is useful — `γ* ≥ 1` — but only
conditionally on U/SR.

---

## 5. What a spelling-independent bound would and would not buy (a correction)

This section corrects an inference that is easy to make and is **wrong**.

**Proposition A1 [AC-trivial; certified by construction].** There exist balanced
**AC-trivial** presentations of the trivial group whose reduced spelling has `γ_N = 1`.
Twelve of them lie within 4 AC-moves of the standard presentation `("x","y")`; the shortest
have total length 7:

    ("Yx", "yyXYx")   ("YxxyX", "yX")   ("xY", "XyyxY")
    ("xxYXy", "Xy")   ("xxyXY", "yx")   ("xy", "yyxYX")      γ_N = 1, census 12

and six more of total length 8 with census 48 (e.g. `("Yxx","yXYxx")`, `("xxY","XyxxY")`).
Each was produced by a breadth-first walk from `("x","y")` using only AC1 (invert), AC2
(multiply, both `r_i r_j` and `r_i r_j⁻¹`), AC3 (conjugate) and move (0), so
AC-triviality is certified by construction, not searched for; `γ_N = 1` is by exact census
(cap 500,000, status OK). None of the six length-7 states has a single spike reaching
`γ_N = 0` (all single spikes hunted for defect-0 witnesses; 0 hits).

**Consequences.**

1. **`γ_N` of the reduced spelling is not an AC invariant, and neither, apparently, is
   γ\*.** Under SR these twelve states have `γ*(P) = 1 > 0` while being AC-trivial.
2. **The converse of Lackenby Thm 1.3 fails.** "P AC-trivial ⇒ some spelling of P is
   thickenable" is therefore not a theorem one may assume; the thickenability test is
   *sufficient* for AC-triviality, never necessary.
3. **Hence a proof of `γ*(AK(3)) ≥ 1` would NOT disprove the AC conjecture.** It would
   close the spelling-space route and nothing more. Any hope that Q1 is a shortcut to a
   disproof of AC at the minimal open case is misplaced.
4. **The stable picture is different, and the orchestrator's framing is right there.**
   Because stable ACC is *equivalent* to "every balanced presentation of 1 reaches SOME
   thickenable presentation by stable AC moves" (⟸ is Lackenby Thm 1.3, ⟹ is trivial since
   the standard presentation is thickenable), a proof that **AK(3)'s whole stable class**
   contains no thickenable member would disprove stable ACC outright. But note what SR
   contributes to that target and what it does not: SR does **not** produce a class-wide
   obstruction. What it does is make the target well-posed — it collapses the uncountable
   spelling space of each class member to its single reduced representative, turning
   "no thickenable member in any spelling" into a statement about a countable set of
   reduced presentations, one census each. That is a genuine reduction of a disproof
   target, not a disproof.
5. A partial geometric argument for the converse of Lackenby (handle slides on the
   handle decomposition of `B³` induced by a spine realize `r_i → r_i·(w r_j^{±1} w⁻¹)`)
   was attempted and **does not close**: the band realizing the slide must be embedded in
   `∂V` and disjoint from the other attaching curves, so only some conjugators `w` are
   realizable, and the exact move `r_i → r_i r_j` is not visibly among them. A1 shows the
   gap is real, not merely technical.

---

## 6. Q4 — contractibility, spines of the 3-ball, and the literature

**Theorem B (spelling complexes of balanced trivial presentations) [MACHINERY + topology].**
Let `P` be balanced with trivial group and let `K` be any spelling complex of `P`
(one vertex, `n` 1-cells, `n` 2-cells). Then `K` is **contractible**, and the following are
equivalent:

  (i) `γ_N(K) = 0`;  (ii) `K` PL-embeds in some orientable 3-manifold;  (iii) `K` is a
  **spine of the 3-ball** (`B³ ↘ K`).

*Proof.* Contractibility: `π₁(K) = 1` so `H₁ = 0`; `H₂(K)` is free (2-complex) and
`χ(K) = 1 − n + n = 1` forces `rk H₂ = 0`; acyclic + simply connected ⇒ contractible
(Hurewicz + Whitehead). (i) ⟺ (ii) is Theorem D of R1E (audited machinery of this line).
(iii) ⇒ (ii) is trivial. (ii) ⇒ (iii): push `K` into the interior and take a regular
neighbourhood `N`; `N ↘ K` (Rourke–Sanderson Ch. 3), so `N` is a compact contractible
orientable 3-manifold. Poincaré–Lefschetz gives `H₂(N, ∂N) ≅ H¹(N) = 0` and
`H₁(N, ∂N) ≅ H²(N) = 0`; the long exact sequences then give `H₁(∂N) = 0` and
`H₀(∂N) ≅ H₀(N) = Z`, so `∂N` is a single 2-sphere. Capping with a ball produces a closed
simply connected 3-manifold (van Kampen), hence `S³` by the Poincaré conjecture
(Perelman), and Alexander's theorem gives `N ≅ B³`. ∎

**Corollary B1.** `γ*(P) = 0 ⟺ some spelling of `P` is a spine of `B³`. So γ\* is exactly
the "distance to being a ball-spine" measured in Neuwirth genus, and Q4's reformulation is
correct.

**Corollary B2 [AC-trivial] — a citation-independent route to the positive consequence.**
A spine of `B³` yields a genus-`n` Heegaard diagram of `S³` (double the induced handle
decomposition), and *the Andrews–Curtis conjecture holds for all balanced presentations of
the trivial group coming from Heegaard diagrams of `S³`* — **Guangyuan Guo,
arXiv:1601.06871, "Heegaard Diagrams of S³ and the Andrews–Curtis Conjecture" (2016)**;
the derived statement "a spine of a 3-ball can even be Q-trivialized without intermediate
prolongations, a special case of Guo's result on Heegaard decompositions" is quoted in
arXiv:2412.12293. So `γ*(P) = 0 ⇒ P AC-trivial` has a **second, 2016-vintage source**
independent of the 2026 Lackenby preprint that the project has been flagging.
[SOURCING LEVEL: abstract/secondary-quote, obtained by web search this session; the full
texts of 1601.06871 and 2412.12293 are 403-blocked by this container's proxy. Treat as
CORROBORATED, not READ.]

**Lackenby arXiv:2606.06122 — flag upgraded.** The paper's own abstract, retrieved this
session, states that it "establishes an explicit upper bound on the number of stable
Andrews–Curtis moves that convert thickenable balanced presentations of the trivial group
to the standard one-generator presentation" and "presents a proof that thickenable balanced
presentations of the trivial group satisfy the (unstable) Andrews–Curtis conjecture".
That is exactly the project's recorded Thm 1.2 / Thm 1.3. The flag can move from
"[unverified this session — two agreeing secondary restatements]" to **"abstract confirmed
this session from the arXiv listing; full text still proxy-blocked (403)"**. The theorem
numbering itself is still unverified.

**Corollary B3 [stably AC-trivial] — the classical fallback.** `B³ ↘ K` and `B³ ↘ pt`
make `K` 3-deformation equivalent to a point; the classical correspondence
"Q\*\*-transformations of presentations ⟷ 3-deformations of 2-dimensional CW-complexes"
(attributed to Wright, *Trans. Amer. Math. Soc.* **208** (1975); restated in
Hog-Angeloni–Metzler–Sieradski) then gives `P` **stably AC-trivial**. The topological form
of stable ACC — "every contractible 2-complex 3-deforms to a point" — is standard and was
confirmed by search this session. [SOURCING LEVEL: secondary; the primary texts are not
reachable. Use B2 in preference; B3 is a redundancy check, and its value is that it rests
on a different, much older citation.]

**Known obstructions to being a spine of `B³` — what exists and what does not.**
* *Local:* the link of every point of a 2-complex embedded in a 3-manifold must be planar.
  For a one-vertex complex the only non-trivial link is Λ(P), and at rank 2 Λ has 4
  vertices and is therefore always planar. So there is **no local obstruction at rank 2**;
  the Neuwirth rotation condition is the whole of it. (At an interior point of a 1-cell the
  link is a `d`-fold banana, always planar — no obstruction there either at any rank.)
* *Collapsibility is not necessary and gives no obstruction:* Bing's house with two rooms
  is the standard contractible, **non-collapsible** 2-complex which nevertheless is a spine
  of `B³` (confirmed by search this session). So "K is not collapsible" is never evidence.
* *Zeeman's conjecture:* for standard 2-polyhedra that are spines of PL 3-manifolds,
  Zeeman's conjecture is equivalent to the Poincaré conjecture (confirmed by search); this
  is a statement *about* spines, not an obstruction *to* being one.
* *Could not source, listed so a future session does not re-derive them from memory:*
  H. Ikeda's characterization of which special polyhedra are spines of 3-manifolds;
  Matveev's special-spine complexity theory; Casler's theorem. All **[UNVERIFIED]** —
  do not cite until read.
* *Structural conclusion:* for balanced presentations of the trivial group there is **no
  known invariant obstructing "spine of B³" other than the Neuwirth criterion itself**,
  and §4 explains why the obvious candidates cannot exist. This is a negative answer to Q4
  as posed, and it is consistent: `K` is acyclic, so nothing homotopy-theoretic is left.

---

## 7. Summary — PROVED / CONJECTURED / REFUTED / OPEN

### PROVED (draft-grade: author-audited + machine-verified, awaiting independent audit)

* **S1** exact spike bookkeeping: `|A′| = |A| + 2`, `|C′| = |C|`, `deg′(s) = deg(s)+2`,
  `deg′(t) = deg(t)+2`, `L′ = L − δ`, `|𝒞(P′)| = |𝒞(P)|·D(D+1)`; one corner deleted, three
  added, exactly one of them a loop. Reproduces R1F's two census sizes case by case.
* **S2** the spike fibration: `ρ` well defined, surjective, uniform fibres `D(D+1)` —
  re-derived without (NC) and without looplessness (the scope repair).
* **S3** Lemma G4 is loop-safe (checked, not assumed).
* **S4** the spike master formula `defect′ = defect(ρ) − 2X⁻ + 2X⁺`, `X⁻ ∈ {0,1}`,
  `X⁺ ∈ {0,1,2,3}`, with `X⁻` pre-spike-readable and the equivalent face identity
  `|A′C′| − |AC| = 2 − 2δ + 2X⁻ − 2X⁺`. **This is the full answer to Q2.**
* **S5 THE SPIKE CEILING:** `γ_N(spike(P)) ≥ γ_N(P) − 1`, tight; and `≤ γ_N(P) + 2`.
* **S6** no single spike of AK(3) is thickenable (proof, replacing two exhaustive censuses);
  a thickenable spelling of AK(3) has spike-depth ≥ 2; R1F's eight gateways attain the
  ceiling.
* **S8, S9, S10** the reduction theorem under unnesting: a defect-0 rotation system of a
  spiked complex whose two new darts are adjacent at `s` restricts to a defect-0 rotation
  system of the base. 115,264 machine checks, 0 violations; and the hypothesis is
  load-bearing (4,288 nested rows restrict to defect 2).
* **M1, M2** monogons come only from cancelling pairs, and the face-degree budget relaxes by
  2 per spike — the mechanism behind everything R1F observed, and the reason no counting
  invariant can be spelling-independent.
* **B, B1** for a balanced trivial-group presentation, every spelling complex is
  contractible and `γ_N = 0 ⟺ embeds in an orientable 3-manifold ⟺ is a spine of `B³``
  (uses Perelman).
* **A1** there are AC-trivial balanced presentations of the trivial group with
  `γ_N(reduced) = 1` — twelve explicit ones within 4 AC moves of standard.

### CONJECTURED

* **U (unnesting):** every spiked complex with `γ_N = 0` has an unnested defect-0 witness.
  Evidence: 23,328/23,328 at total length 6. **U ⇒ SR** by S10.
* **SR (spelling reduction):** `γ_N(spike(P)) = 0 ⇒ γ_N(P) = 0`. Evidence: R1F's 110,917
  measured spiked complexes plus this note's independent witness-hunt scans, zero
  counterexamples anywhere. **A proof of SR closes the spelling-space route: it gives
  `γ*(AK(3)) = 1` exactly and upgrades the project's ≈17,100 negative verdicts from single
  realizations to whole spelling families.** This is the single most valuable open item
  produced here.
* **R (rise ceiling):** a single spike raises `γ_N` by at most 1 (proved: at most 2).
  Evidence: R1F's 110,917 spikes, never more than +1.
* **Spike saturation:** `γ_N(spike^k(P)) ≥ γ_N(P) − 1` for all `k` (i.e. the −1 does not
  compound). Evidence: R1F's tier-2 double spikes show drops of 1 but never 2. Implied for
  the value 0 by SR; unproved in general.

### REFUTED

* "ρ preserves defect 0" — FALSE without the unnesting hypothesis: 4,288 nested defect-0
  rotation systems at total length 6 restrict to defect 2.
* "A spelling-independent lower bound on `γ_N` would disprove the AC conjecture at AK(3)" —
  FALSE (A1: AC-triviality does not imply `γ_N(reduced) = 0`, so the converse of Lackenby
  Thm 1.3 is not available).
* "Counting/parity/planarity/homological invariants can bound `γ*` from below" — refuted
  family by family in §4, with a quantitative reason (M2).
* "`γ_N` of the reduced spelling is a canonical representative's invariant that survives
  spiking" — refuted already by R1F; S5 now bounds exactly how badly (`−1` per spike, tight).

### OPEN

* U and SR (above). The natural attack: in a nested defect-0 system the spike loop is a
  separating curve of the sphere, which is a strong constraint — exploit it or break it.
* Whether the `+2` in S5's upper half is attained.
* Whether a thickenable spelling of AK(3) exists at spike-depth 2 (S6 says depth ≥ 2 is
  necessary). Censuses are out of reach there (`≥ 2·10⁸` rotation systems); only witness
  hunts can decide, and a negative witness hunt is silence.
* Whether `γ*(P⁺) = γ*(P)` under stabilization (AC4). Corollary Z gives it for `γ_N`;
  for `γ*` only `≤` is immediate, since the fresh `z`-relator has its own spellings.
* Whether AC-triviality implies "some spelling is a spine of `B³`" (the converse of
  Lackenby Thm 1.3). A1 makes this look FALSE, but A1 only refutes the reduced-level
  version outright and the spelling-level version modulo SR.

---

## 8. Machine-check ledger

All checks were run against the committed dictionary (`build_link_n`, `census_size`,
`compatible_orders_n`, `gamma_N_factorial_n` in
`experiments/stable_ac/fable/neuwirth_rank_n.py`) by session-scratchpad scripts; **no
existing code was modified and no new file was added to the repo except this note**.
§§0–3 contain every definition needed to regenerate them.

1. *Bookkeeping + fibration + interpolation* (`verify_spike.py`): 7 spikes over 5 bases,
   234 compatible rotation systems traced dart-by-dart, **820 assertions, 0 failures**.
   Covered: `|A′|`, dart count, present germs, every germ degree, census ratio `D(D+1)`,
   the identity `A′ = A − e_0 + {J₁, ℓ, J₂}`, germ placement of the four new darts,
   `ρ` landing in the pre census, `ρ` surjective, fibres uniform of size `D(D+1)`,
   `def(R₀) = defect(ρ(C′))`, per-op ranges (`op1 ∈ {0,−2}`, `ops 2–4 ∈ {0,+2}`), and the
   endpoint identity `def(R₄) = defect′(C′)`.
   `L` motion observed in both regimes: `("xx","yy") → ("yYxx","yy")` has `L 2 → 1`
   (`δ = 1`), `("xyxy","xy") → ("xyxXxy","xy")` has `L 2 → 2` (`δ = 0`) — both predicted
   correctly by S1(4).
2. *Unnesting / Theorem S10* (`adjacency_test.py`, total length 6): 1,400 bases, all single
   spikes, full censuses. `spiked γ_N = 0`: 23,328; of these, **23,328 have an unnested
   defect-0 witness** (0 exceptions → Conjecture U). Rows: **115,264 unnested defect-0 rows,
   all with `defect(ρ) = 0`** → **0 violations of S10**; **12,736 nested defect-0 rows**, of
   which **8,448 have `defect(ρ) = 0` and 4,288 have `defect(ρ) = 2`** → the unnesting
   hypothesis is necessary. SR counterexamples found: **0**.
3. *SR counterexample hunt* (`sr_hunt.py`, total length 8, exhaustive): 77 canonical
   cyclically reduced bases, 48 with `γ_N ≥ 1`, **1,080 spiked complexes** searched for
   defect-0 witnesses (60 restarts × 400 hill-climb steps each) — **0 counterexamples**.
   Witness-hunter calibration (7 anchors, all reproduced exactly): `("xyXY","xxy")` → 0,
   `("xyXY","yYxxy")` → 2, AK(3) → 4, `("xyYxxYYYY","xyxYXY")` → 2,
   `("xxxYYYY","xxXyxYXY")` → 2, `("x","y")` → 0, `("xy","y")` → 0 (unhalved defects).
4. *AC-trivial states* (`actrivial_gamma.py`): BFS of depth 4 from `("x","y")` under
   AC1/AC2/AC3 + move (0), 578 certified AC-trivial reduced states of total length ≤ 14;
   **12 with `γ_N ≥ 1`** by exact census; the six shortest were spike-hunted (all single
   spikes, defect-0 witness search) with **0 hits**.

Scripts live in the session scratchpad only, per the task's "new files only, and the
deliverable is this note" instruction.

---

## 9. What this note does NOT claim

* No claim that AK(3) is or is not AC-trivial, or stably AC-trivial, in either direction.
* No unconditional lower bound on `γ*` for any presentation. `γ*(AK(3)) = 1` is stated
  **only** as a consequence of Conjecture SR.
* No transport of any `γ_N` verdict along AC paths. `γ_N` is not AC2-invariant (codex's
  `("yxx","y") → ("yxxy","y")` counterexample) and §5 shows even `γ*` is not.
* No claim that spikes with a **fresh** generator behave as in S1–S5 — hypothesis (H) is
  used throughout and such a spike is a different move (`|C|` changes).
* No claim about non-orientable thickenings.
* Lackenby Thm 1.3 is used only where flagged, and only in the direction
  thickenable ⇒ AC-trivial; Guo arXiv:1601.06871 and Wright 1975 are CORROBORATED by
  search but NOT READ this session, and are flagged accordingly at each use.
* Theorem B uses the Poincaré conjecture (Perelman) and the PL regular-neighbourhood
  theorem; both are cited, not proved.
* The proofs in §§1 and 3 have **not** been through an independent adversarial audit. Per
  the standing rule they are drafts. The two most audit-sensitive steps are: S9's bridge
  case (the claim that a boundary walk crossing a bridge splits along component lines), and
  S10's degenerate configurations (`X` or `Y` equal to `s` or `t`, or of degree 1) — both
  are argued in the text and covered by the machine checks, but an auditor should attack
  them first.
