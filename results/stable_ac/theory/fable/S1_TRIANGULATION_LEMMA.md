# S1 — The free-definition move, the Triangulation Lemma, and the rank-(n+1) stable
# ambient automorphism principle

Task A1 of `S0_HIGH_RANK_PLAN.md`. Standing frame: `FRAMING.md` (move numbering AC1–AC5,
trap list — binding). Branch `claude/stable-ac-conjecture-stabilization-rwo9as`; **must be
merged into `fable/proof` by the user.**

Status of this document: **self-contained proofs**, machine-checked where the task asked
for it (§4.4, §5.4, §7). Everything that is only sketched is labelled `[GAP]`; everything
imported from outside is labelled and ledgered in §6. The single external input is
Nielsen's generation theorem for `Aut(F_n)` (§5.3), and it is used only in the *last* step
of Corollary F1 — the rest of F1 is proved from scratch.

**Sourcing note (FRAMING §5 / project lesson `literature-absent-in-cloud-clones.md`).**
FRAMING §5 attributes the rank-2 case of Corollary F1 to "PROOFS.tex Thm 3 (this project)".
`find . -iname "PROOFS*"` over this clone returns **nothing**: that file is not present
here and **was not read**. It is therefore *not* cited anywhere below as a source, and none
of the arguments here depend on it. `literature/` contains only `literature/fake_surfaces/`
(a repo README and a CSV-labelling-convention PDF) — **no papers at all**. Accordingly **no
paper is cited anywhere in this document**, and the one classical fact used is flagged
`[UNVERIFIED-CLASSICAL-1]` in §5.3 with its blast radius bounded there.

---

## 0. What is and is not claimed

| claim | strength |
|---|---|
| Lemma S-a (free-definition move) | **proved**, and proved **sharp** (§3.3, iff) |
| Lemma S-b (Triangulation) | **proved** (§4) |
| AK(3) has an explicit rank-9 all-length-3 triangulation | **proved + machine-verified** (§4.4) |
| AK(3) also has a rank-**8** one (shared definition) | **proved + machine-verified** (§4.5) |
| Corollary F1 (Aut(F_n)-orbit inside rank n+1) | **proved**, modulo Nielsen's theorem (§5) |
| AK(3) is stably AC-trivial | **NOT claimed.** Nothing here decides it. |
| N = n + Σ max(0,\|r_i\|−3) is *minimal* over all triangulations | **NOT claimed** — disproved for AK(3) itself, §4.5 |
| any move-count / complexity bound | **NOT claimed** (trap 6 / T-S5, §6.3) |

**Vocabulary discipline (CLAUDE.md).** Throughout: *"presents the trivial group"* is a
statement about the group `F/⟪R⟫`; *"AC-trivial"* means reachable from the standard
presentation by AC1–AC3 at fixed rank; *"stably AC-trivial"* means reachable by AC1–AC5.
This document proves **no** AC-triviality and **no** stable AC-triviality of anything. It
proves *equivalences* — edges in the stable graph — plus one structural normal form.
FRAMING §3 is explicit that a new stable equivalence between two non-standard
presentations is an edge, not a resolution.

---

## 1. Conventions

`F_n = F(x_1,…,x_n)` is free on the given basis. A **presentation** is a pair
(ordered alphabet `X`, ordered tuple `R = (r_1,…,r_m)` of elements of `F(X)`); it is
**balanced** if `m = |X|`. The group presented is `F(X)/⟪R⟫`, where `⟪S⟫^{G}` denotes the
normal closure of `S` in `G` (superscript dropped when the ambient group is clear).

**Moves** (project operating-contract numbering, FRAMING §1 — papers permute these; trap 5):

- **AC1** (invert) `r_i ↦ r_i^{-1}`.
- **AC2** (multiply) `r_i ↦ r_i r_j`, `j ≠ i`.
- **AC3** (conjugate) `r_i ↦ u r_i u^{-1}`, `u ∈ F(X)` arbitrary.
- **(0)** free / cyclic reduction.
- **AC4** (stabilize) adjoin a fresh generator `z` and the relator `z`.
- **AC5** (destabilize) inverse of AC4: delete a generator `g` together with a relator
  equal to `g`, legal only when `g` occurs in no other relator.

**Relators are free-group elements, not spellings.** Under that convention move (0) is not
a move at all — it is the identity — and **all proofs below use AC1–AC3 (+AC4/AC5 where
stated) and nothing else.** Readers who prefer the spelling convention (relators are words,
AC2 concatenates literally) should insert move (0) after each AC2; §4.2 and §5.2 record
exactly where the seam cancellations occur, in accordance with FRAMING trap 3
("free-reduce every substituted relator completely, including the seam").

**AC4/AC5 and generator names.** AC4 adjoins a generator; which position it occupies in the
ordered alphabet is immaterial, and AC5 may delete *any* generator satisfying its
hypothesis, not only the last one. Two presentations differing only by a bijection of the
generator *symbols* are the same presentation. This is a convention about names, not a
move; it is used once, in §5.2 Step 6, and flagged there.

**Notation for words** (repo convention, `experiments/stable_ac/fable/ac_words.py`):
a lowercase letter is a generator, the corresponding uppercase letter is its inverse; e.g.
`AK(3)` is `r_1 = "xyxYXY"`, `r_2 = "xxxYYYY"`. (The repo's own tuple in
`tests/fable/helpers_fable.py:23` lists these in the opposite order,
`AK3 = ("xxxYYYY", "xyxYXY")`; the numbering here is the task's and nothing depends on it.)

**Reversibility.** AC1 is an involution; AC3 with `u` is inverted by AC3 with `u^{-1}`; AC2
`r_i ↦ r_i r_j` is inverted by AC1(j), AC2(i,j), AC1(j). Hence AC1–AC3 generate a group of
transformations and "AC1–AC3-equivalent at fixed rank" is an equivalence relation. Used
without further comment.

---

## 2. Lemma 0 — the compound moves

Everything below is built from three compound moves. They are stated once, proved once, and
then used as primitives.

### Lemma 0.1 (right multiplication by a conjugate of another relator)

Let `(s_1,…,s_M)` be a relator tuple over `F(X)`, let `i ≠ j`, `u ∈ F(X)`, `ε ∈ {±1}`.
Then the tuple with `s_i` replaced by `s_i · (u s_j^{ε} u^{-1})` and **every other entry,
including `s_j`, restored exactly** is obtained by AC1–AC3.

*Proof.* Perform, in order:

1. `AC3(j, u)`: `s_j ↦ u s_j u^{-1}`.
2. If `ε = −1`: `AC1(j)`, giving `u s_j^{-1} u^{-1}`.
3. `AC2(i, j)`: `s_i ↦ s_i · (u s_j^{ε} u^{-1})`. Legal since `i ≠ j`.
4. If `ε = −1`: `AC1(j)`, restoring `u s_j u^{-1}`.
5. `AC3(j, u^{-1})`: `u s_j u^{-1} ↦ u^{-1}(u s_j u^{-1})u = s_j`. Restored. ∎

This is exactly the bookkeeping the task asks to be made explicit: **AC3 changes `s_j`
permanently**, so the conjugation must be undone by a second AC3 with the inverse
conjugator, and if `ε = −1` the inversion must be undone by a second AC1. Steps 1 and 5 are
*not* optional decoration; without them the tuple is not the claimed one.

### Lemma 0.2 (left multiplication; the AC1;AC2;AC1 sandwich)

For `i ≠ j`, the sequence `AC1(i), AC2(i,j), AC1(i)` sends

    s_i  ↦  s_i^{-1}  ↦  s_i^{-1} s_j  ↦  (s_i^{-1} s_j)^{-1} = s_j^{-1} s_i ,

all other entries fixed. Sandwiching with `AC1(j)` on both sides gives `s_i ↦ s_j s_i` with
`s_j` restored. Composing with Lemma 0.1's conjugation bracket gives, for any `u ∈ F(X)`
and `ε ∈ {±1}`,

    s_i  ↦  (u s_j^{ε} u^{-1}) · s_i ,   all other entries restored exactly.

*Proof.* The displayed computation is the definition of the three moves; note
`(s_i^{-1}s_j)^{-1} = s_j^{-1} s_i`. For the last statement, conjugate `s_j` by `u`
(AC3), invert if `ε = −1` (AC1), run the sandwich with the appropriate inner sign, then
undo (AC1, AC3) as in Lemma 0.1. ∎

So **left-multiplication is available, and it costs exactly the AC1;AC2;AC1 sandwich**:
AC2 alone only multiplies on the right, and the two flanking AC1's convert that into a left
multiplication by the *inverse* of the other relator.

### Lemma 0.3 (transfer primitive — the master move)

Let `(s_1,…,s_M)` be a relator tuple over `F(X)`, fix `i`, and put

    C_i  :=  ⟪ s_j : j ≠ i ⟫^{F(X)}    (normal closure of the OTHER relators).

Then for every `c ∈ C_i` the tuple with `s_i` replaced by `s_i c` — and every other entry
restored exactly — is obtained from `(s_1,…,s_M)` by AC1–AC3. The same holds for `c s_i`.

*Proof.* Write `c = ∏_{k=1}^{K} u_k s_{j_k}^{ε_k} u_k^{-1}` with `j_k ≠ i` (possible by the
definition of normal closure). Apply Lemma 0.1 with `(u_1, j_1, ε_1)`, then with
`(u_2, j_2, ε_2)`, and so on; after step `k` the `i`-th entry is
`s_i · ∏_{l≤k} u_l s_{j_l}^{ε_l} u_l^{-1}` and all other entries equal their original
values. After `K` steps the `i`-th entry is `s_i c`. For `c s_i` use Lemma 0.2 and apply the
factors in the reverse order. ∎

**Warning (what Lemma 0.3 does *not* say).** `C_i` is *not* preserved by AC1–AC3: an AC2
move into slot `j ≠ i` changes `s_j`, hence changes `C_i`. Lemma 0.3 is a *sufficient*
condition computed in the tuple you currently hold, and it must be re-evaluated after every
move that touches a slot other than `i`. In the applications below `C_i` is recomputed
explicitly at each use.

---

## 3. Lemma S-a — the free-definition move

### 3.1 Statement

> **Lemma S-a.** Let `P = ⟨x_1,…,x_n | r_1,…,r_n⟩` be a balanced presentation **of the
> trivial group**, and let `P^+ = ⟨x_1,…,x_n, z | r_1,…,r_n, z⟩` be its AC4 stabilization.
> Then for **every** `w ∈ F(x_1,…,x_n)` the tuples
>
>     (r_1, …, r_n, z)     and     (r_1, …, r_n, z·w)
>
> are AC1–AC3-equivalent over `F(x_1,…,x_n,z)`, i.e. **at fixed rank n+1 and without any
> further stabilization or destabilization**. All of `r_1,…,r_n` are restored exactly.

### 3.2 Proof

`P` presents the trivial group, i.e. `F_n/⟪r_1,…,r_n⟫^{F_n} = 1`, i.e.

    ⟪r_1,…,r_n⟫^{F_n}  =  F_n .                                        (†)

Let `w ∈ F(x_1,…,x_n)`. By (†) there are `K ≥ 0`, `u_k ∈ F_n`, `ε_k ∈ {±1}`,
`i_k ∈ {1,…,n}` with

    w  =  ∏_{k=1}^{K} u_k r_{i_k}^{ε_k} u_k^{-1} .

In the rank-(n+1) tuple `(r_1,…,r_n,z)` take `i = n+1`. Its "other relators" normal closure
is `C_{n+1} = ⟪r_1,…,r_n⟫^{F(x_1..x_n,z)} ⊇ ⟪r_1,…,r_n⟫^{F_n} = F_n ∋ w`. Apply Lemma 0.3:

    (r_1,…,r_n, z)  ⟶  (r_1,…,r_n, z·w) ,

with `r_1,…,r_n` restored exactly. Unwinding Lemma 0.3 through Lemma 0.1, the elementary
sequence is, for each factor `k`:

    AC3(i_k, u_k) ;  [AC1(i_k) if ε_k = −1] ;  AC2(n+1, i_k) ;
    [AC1(i_k) if ε_k = −1] ;  AC3(i_k, u_k^{-1}) .

Reversibility (§1) gives the converse direction, so the two tuples are equivalent. ∎

**Free reduction.** `z` is a fresh generator, so no letter of `w` cancels against `z`:
`z·w` is freely reduced whenever `w` is. Under the spelling convention the only
cancellations are inside the products `u_k r^{ε_k} u_k^{-1}` and at the `K−1` seams between
consecutive factors; move (0) after each AC2 handles them (trap 3).

**Corollary S-a′ (both sides).** Combining with Lemma 0.2, the last relator may be changed
`z ↦ v · z · w` for any `v, w ∈ F(x_1,…,x_n)`.

**Remark S-a″ (a free strengthening).** `C_{n+1} = ⟪r_1,…,r_n⟫^{F(x_1..x_n,z)}` is in fact
the normal closure of `F_n` in `F_n * ⟨z⟩`, which is the kernel of the retraction
`σ_z : F(x_1..x_n,z) → ⟨z⟩ ≅ ℤ` (`x_i ↦ 1`, `z ↦ z`). So the lemma actually gives
`z ↦ z·w` for **every** `w ∈ F(x_1,…,x_n,z)` of total `z`-exponent-sum 0 — words in which
`z` itself may occur. Not needed below, recorded because it costs nothing.

### 3.3 Sharpness — the hypothesis is exactly right, and it is an *iff*

Triviality of `G = F_n/⟪r_1..r_n⟫` was used in exactly one place: to guarantee `w ∈ ⟪r_i⟫`.
That use is **unavoidable**, and the following is a converse, not merely a counterexample.

> **Proposition S-a-sharp.** Let `P = ⟨x_1..x_n | r_1..r_n⟩` be *any* balanced presentation
> (no hypothesis on `G`), and `w ∈ F(x_1,…,x_n)`. Then
>
>     (r_1,…,r_n, z) ~_{AC1–AC3} (r_1,…,r_n, z·w)  at rank n+1
>       ⟺  w ∈ ⟪r_1,…,r_n⟫^{F_n}   ⟺   w = 1 in G.

*Proof of ⟸.* Verbatim the proof of §3.2: it only ever used `w ∈ ⟪r_i⟫^{F_n}`, never (†)
in full.

*Proof of ⟹.* First, each of AC1, AC2, AC3 replaces one entry of a tuple `T` by an element
of `⟪T⟫` and leaves the rest alone, so `⟪T'⟫ ⊆ ⟪T⟫`; the moves are invertible (§1), so
`⟪T'⟫ = ⟪T⟫`. Hence **AC1–AC3 preserve the normal closure of the relator tuple exactly**
(not merely the isomorphism type of the quotient). Write

    N₁ := ⟪r_1,…,r_n, z⟫^{F(x_1..x_n,z)} .

Let `ρ : F(x_1..x_n,z) → F_n` be the retraction `z ↦ 1`, `x_i ↦ x_i`. Since `ρ` is onto,
`ρ(N₁) = ⟪ρ(r_1),…,ρ(r_n), ρ(z)⟫^{F_n} = ⟪r_1,…,r_n⟫^{F_n}`; and `ρ` restricts to the
identity on `F_n`, so

    N₁ ∩ F_n  =  ρ(N₁ ∩ F_n)  ⊆  ρ(N₁)  =  ⟪r_1,…,r_n⟫^{F_n} ,

with the reverse inclusion obvious. Thus `N₁ ∩ F_n = ⟪r_1,…,r_n⟫^{F_n}`. Now assume the two
tuples are AC1–AC3-equivalent. Then `⟪r_1,…,r_n, z·w⟫ = N₁`, so `z·w ∈ N₁`; since `z ∈ N₁`
this gives `w ∈ N₁`, and `w ∈ F_n`, so `w ∈ N₁ ∩ F_n = ⟪r_1,…,r_n⟫^{F_n}`. ∎

So: **the lemma holds for every `w` precisely when `⟪r_i⟫ = F_n`, i.e. precisely when `G`
is trivial.** This is FRAMING trap 2 ("state the triviality hypothesis; it is sharp") made
concrete and turned into a biconditional.

### 3.4 An explicit counterexample for a non-trivial group (elementary, machine-checked)

Take `n = 1`, `P = ⟨x | x²⟩`, a balanced presentation of `G = ℤ/2 ≠ 1`, and `w = x`
(`w ≠ 1` in `G`). Claim: `(x², z)` and `(x², z x)` are **not** AC1–AC3-equivalent at rank 2.

*Certificate (no normal-closure theory needed).* Send each relator to its exponent-sum
vector in `ℤ² = H_1`. AC1 negates a row, AC2 adds one row to another, AC3 does nothing. All
three preserve the **subgroup of ℤ^{n+1} spanned by the rows**. Now

    (x², z)  ↦ rows (2,0), (0,1)   spanning  L₁ = {(a,b) : a even},
    (x², zx) ↦ rows (2,0), (1,1)   spanning  L₂ ∋ (1,1) ∉ L₁ .

`L₁ ≠ L₂`, so no AC1–AC3 chain joins them. ∎

Control, confirming the boundary is exactly `w =_G 1`: for `w = x²` (which *is* trivial in
`G`) the rows are `(2,0),(2,1)`, spanning `L₁` again — and indeed Proposition S-a-sharp's
`⟸` applies and the move is legal. Both computations are asserted in the check script of §7.

**Why the presented group alone cannot detect this.** `⟨x,z | x², z⟩` and `⟨x,z | x², zx⟩`
both present `ℤ/2` (Tietze-eliminate `z`). The obstruction is *not* the isomorphism type of
the quotient; it is the normal subgroup `N₁ ⊆ F(x,z)` itself (equivalently, here, its
abelianized shadow). Anyone attempting to weaken the triviality hypothesis by "the groups
agree anyway" is walking into this.

### 3.5 Move counts

**No bound is claimed and none may be quoted** (FRAMING trap 6; `S0` trap T-S5). The length
of the chain in §3.2 is `≤ 5K` elementary moves where `K` is the number of factors in *some*
expression of `w` as a product of conjugates of the `r_i^{±1}`. The minimal such `K` is the
*area* of `w` with respect to `⟨x | r⟩` — a Dehn-function quantity — and for balanced
presentations of the trivial group it has no known elementary bound; the Bridson/Lishak
tower families (FRAMING trap 8) are exactly the calibration anti-benchmark here. Every
statement in this document is about **existence of a chain**, never about its length.

---

## 4. Lemma S-b — the Triangulation Lemma

### 4.1 Statement

> **Lemma S-b (Triangulation).** Let `P = ⟨x_1,…,x_n | r_1,…,r_n⟩` be a balanced
> presentation **of the trivial group**, with the `r_i` freely reduced. Put
>
>     N  :=  n  +  Σ_{i=1}^{n} max(0, |r_i| − 3).
>
> Then, using **AC4 stabilizations and AC1–AC3 only — never AC5** — `P` is transformed into
> a presentation `P_Δ` at rank `N` such that
>
>  (i)  every step is a legal AC move sequence;
>  (ii) `P_Δ` is balanced (`N` generators, `N` relators) and presents the **trivial group**;
>  (iii) every relator of `P_Δ` has length ≤ 3; more precisely every relator has length
>        exactly 3 except for those `r_i` of `P` with `|r_i| ≤ 2`, which appear unchanged.
>
> In particular `P` and `P_Δ` are **stably AC-equivalent**, and the chain joining them is
> rank-monotone (rank never decreases).

Note the direction of the last clause carefully, per the project lesson
`parallel-runs-and-bound-direction.md`: this is a **construction**, so it bounds the
triangulation rank of `P` from **above**. Nothing here says `N` is needed, minimal, or
first (see §4.5).

### 4.2 The peel step

**Setup.** Suppose the current presentation is `Q = ⟨y_1,…,y_M | s_1,…,s_M⟩`, balanced,
presenting the trivial group, all `s_k` freely reduced, and fix `i` with

    s_i  =  a_1 a_2 a_3 ⋯ a_m ,     m = |s_i| ≥ 4,

each `a_t` a letter of `{y_1^{±1},…,y_M^{±1}}`.

**Step P1 (stabilize).** AC4: adjoin a fresh generator `z` and the relator `z`. Rank `M+1`,
tuple `(s_1,…,s_M, z)`.

**Step P2 (define `z := a_1 a_2`).** `Q` presents the trivial group, so Lemma S-a applies
with base `Q` and `w = (a_1a_2)^{-1} ∈ F(y_1..y_M)`. Result:

    D  :=  z · a_2^{-1} a_1^{-1} ,     tuple  (s_1,…,s_M, D).

`|D| = 3`, and `D` is freely reduced: `z` is fresh so `z·a_2^{-1}` does not cancel, and
`a_2^{-1}a_1^{-1}` is reduced because `a_1a_2` is. The relator `D` says exactly `z = a_1a_2`.

**Step P3 (shorten `s_i`).** Apply Lemma 0.2 with `j = M+1` (left multiplication by the
relator `D`, sandwich `AC1(M+1), AC1(i), AC2(i,M+1), AC1(i), AC1(M+1)`), giving

    s_i  ⟼  D · s_i  =  z a_2^{-1} a_1^{-1} · a_1 a_2 a_3 ⋯ a_m  =  z a_3 ⋯ a_m ,

with `D` and all other relators restored exactly. **The seam.** Exactly two cancellations
occur, `a_1^{-1}a_1` and then `a_2^{-1}a_2`; the resulting word `z a_3⋯a_m` is freely
reduced (`a_3⋯a_m` is reduced, and `z` is fresh so `z a_3` does not cancel). Under the
spelling convention, one application of move (0) at the seam realizes this. New length
`3 + m − 4 = m − 1`.

**Net effect of one peel:** rank `+1`, one new relator of length exactly 3, `|s_i|`
decreased by exactly 1, every other relator unchanged, presentation still balanced and
still presenting the trivial group (Step P1 is a Tietze transformation adjoining a
generator and a defining relator equal to the empty word; Steps P2, P3 are AC1–AC3, which
preserve the normal closure of the relator tuple by §3.3 and hence preserve the quotient).

### 4.3 Proof of Lemma S-b

Process the relators in any order. For each `i` with `|r_i| ≥ 4`, run the peel step
repeatedly on the current version of that relator:

    |r_i| = m  →  m−1  →  m−2  →  ⋯  →  3 ,

i.e. `m − 3` peels. **The loop invariant** — the current presentation is balanced, presents
the trivial group, has all relators freely reduced, and the relator being worked on is
`z_k a_{k+2} ⋯ a_m` for the most recently introduced `z_k` — is preserved by §4.2, and in
particular re-establishes the hypothesis of Lemma S-a needed at the *next* Step P2. (This
is the only place induction is required, and it is what makes it legitimate to invoke
Lemma S-a at rank `M > n`: the lemma's hypothesis is about the *current* presentation, not
about `P`.)

*(i)* Each peel is AC4 followed by AC1–AC3 (Lemma S-a, Lemma 0.2). No AC5 is ever used.

*(ii)* Each peel adds one generator and one relator, so balance is preserved; AC1–AC3
preserve counts. Total generators `n + Σ_i (m_i − 3)^+ = N`, total relators `N`.
Triviality of the presented group is preserved as noted in §4.2. (Explicitly: AC4 turns
`G` into `G * ⟨z | z⟩ ≅ G`; AC1–AC3 fix `⟪R⟫ ⊆ F(X)` exactly, hence fix `F(X)/⟪R⟫`.)

*(iii)* Relators of `P` with `|r_i| ≥ 4` terminate at length exactly 3; every relator
created by a peel is a `D` of length exactly 3; relators of `P` with `|r_i| ≤ 3` are never
touched. Since a balanced presentation of the trivial group has no trivial relator (its
abelianization is a surjection `ℤ^n ↠ ℤ^n`, so no row may be zero), the only lengths below
3 that can occur in `P_Δ` are 1 and 2, and only if they were already in `P`. ∎

**Remark (padding to exactly 3).** A length-1 relator `g` can be inflated to length 3 by a
single AC3: `g ↦ u g u^{-1}` with `u` a generator, `u ≠ g^{±1}`, giving a reduced word of
length 3. A length-2 relator has no such one-move fix (AC3 by a length-1 word gives length
4), and I do not know whether "all relators of length **exactly** 3" is always attainable
at rank `N`. **`[GAP-1]`** — flagged, unused. It does not affect AK(3), whose triangulation
has all nine relators of length exactly 3.

### 4.4 Worked example — AK(3), rank 9, nine relators of length 3

    P = AK(3) = ⟨x, y | r_1, r_2⟩,   r_1 = "xyxYXY"  (= xyx(yxy)^{-1}, length 6)
                                     r_2 = "xxxYYYY" (= x³y^{-4},      length 7)

    N = 2 + (6−3) + (7−3) = 2 + 3 + 4 = 9.

Choose the left-prefix bracketing of §4.2 and name the seven new generators `a,b,c,d,e,f,g`
in order of creation.

**Peel trace for `r_1` (three peels).**

| peel | current relator | prefix peeled | new gen & definition | new definition relator | shortened relator |
|---|---|---|---|---|---|
| 1 | `xyxYXY` (6) | `xy` | `a = xy`    | `aYX` | `axYXY` (5) |
| 2 | `axYXY` (5)  | `ax` | `b = a·x`   | `bXA` | `bYXY` (4)  |
| 3 | `bYXY` (4)   | `bY` | `c = b·Y`   | `cyB` | `cXY` (3)   |

**Peel trace for `r_2` (four peels).**

| peel | current relator | prefix peeled | new gen & definition | new definition relator | shortened relator |
|---|---|---|---|---|---|
| 4 | `xxxYYYY` (7) | `xx` | `d = xx`  | `dXX` | `dxYYYY` (6) |
| 5 | `dxYYYY` (6)  | `dx` | `e = d·x` | `eXD` | `eYYYY` (5)  |
| 6 | `eYYYY` (5)   | `eY` | `f = e·Y` | `fyE` | `fYYY` (4)   |
| 7 | `fYYY` (4)    | `fY` | `g = f·Y` | `gyF` | `gYY` (3)    |

**The triangulation `P_Δ(AK(3))`.**

> **Generators (9):**  `x  y  a  b  c  d  e  f  g`
>
> **Relators (9), each of length exactly 3:**
>
>     R1 = cXY      R2 = gYY
>     R3 = aYX      R4 = bXA      R5 = cyB
>     R6 = dXX      R7 = eXD      R8 = fyE      R9 = gyF
>
> (`R1, R2` are the descendants of `r_1, r_2`; `R3..R9` are the seven definition relators.)

**Definitions in closed form** (each `D = z·W^{-1}` reads `z = W`):

    a = xy        b = xyx      c = xyxY
    d = xx        e = xxx      f = xxxY      g = xxxYY

**Back-substitution check (FRAMING trap 3: free-reduce fully).**

    R1 = c·X·Y   →   (xyxY)·X·Y   =  "xyxYXY"  =  r_1     ✓
    R2 = g·Y·Y   →   (xxxYY)·Y·Y  =  "xxxYYYY" =  r_2     ✓

and each definition relator back-substitutes to the empty word, e.g.
`R5 = c·y·B → (xyxY)·y·(xyx)^{-1} = xyxYy XYX = xyx·XYX = 1` ✓. All of this — the peel
arithmetic, free reduction at every seam, reducedness of all nine relators, balance, the
rank formula, and the two back-substitutions — is machine-verified (§7).

**Conservation cross-check.** Peeling never creates or destroys an occurrence of an
*original* letter. AK(3) contains 6 `x`-letters and 7 `y`-letters (3+3 in `r_1`, 3+4 in
`r_2`); the nine relators of `P_Δ` contain exactly 6 `x`-letters and 7 `y`-letters, plus 2
occurrences of each of `a..g`. Total `6 + 7 + 14 = 27 = 3·9` ✓. This is an independent
arithmetic check on the whole trace.

**Note for task A4 (T-S4).** Each of `a,…,g` occurs exactly **twice** in `P_Δ`. Low
occurrence multiplicity means low germ degree in the link graph, so the S0 §2 estimate
("average germ degree exactly 3") is an *average* and the individual degrees here are far
from uniform: `x` and `y` carry 6 and 7 occurrences, `a..g` carry 2 each. Per S0 trap T-S4
the 3-connectivity fast path of the rank-n Neuwirth solver must **not** be used on this
input; the exact census `gamma_N_factorial_n` is the right tool. Recorded here so A4 does
not rediscover it.

### 4.5 The family of triangulations (part (iii) of the task)

`N` is **exact for the bracketing specified in §4.2** — that algorithm performs exactly
`Σ_i (|r_i|−3)^+` stabilizations, one per unit of length removed. It is **not** a minimum
(see the last item below). The following choices all produce legal triangulations, and by
Lemma S-b(i) each is joined to `P` by AC4 + AC1–AC3 alone, hence **every member of the
family lies in the stable class of `P`**:

1. **Order of processing.** Relators may be peeled in any order, and peels on different
   relators may be interleaved. Rank count unchanged.
2. **Cyclic rotation.** Before a peel, AC3 with `u^{-1}` sends `s = u v ↦ v u`. So any
   cyclic rotation of the current relator may be presented to the peel step, i.e. **any**
   adjacent pair of the cyclic word may be the pair that is peeled. If `s` is cyclically
   reduced the rotation preserves `|s|` and the rank count is unchanged; if `s` is not
   cyclically reduced the rotation can shorten it, and the terminal rank is then **below**
   `N`.
3. **Which end.** Instead of the prefix one may peel the **suffix** `a_{m-1}a_m`: define
   `z = a_{m-1}a_m` via Lemma S-a (relator `D = z a_m^{-1} a_{m-1}^{-1}`, length 3), then
   AC3 the definition slot by `z^{-1}` to get `X := z^{-1}Dz = a_m^{-1}a_{m-1}^{-1} z`, and
   right-multiply `s ↦ s·X = a_1⋯a_{m-2} z` (AC2, then AC3 back). Same length drop, same
   count.
4. **Inverse convention.** `z := a_1a_2` (relator `z a_2^{-1}a_1^{-1}`) or
   `z := (a_1a_2)^{-1}` (relator `z a_1 a_2`); the shortened relator becomes `z a_3⋯a_m` or
   `z^{-1}a_3⋯a_m` respectively. Same length.
5. **Spelling of the definition relator.** `D` may be replaced by its inverse (AC1) or by
   any of its three cyclic rotations (AC3 by a prefix inverse, e.g.
   `z^{-1}(z a_2^{-1}a_1^{-1})z = a_2^{-1}a_1^{-1}z`), all still of length 3. This is the
   "`z` defined as a conjugated word" freedom in its length-preserving form. Conjugating
   `D` by a longer word *does* change its length and is excluded from the family.
6. **`z` defined as an arbitrary length-2 word.** Lemma S-a permits `z := w` for **any**
   `w`; taking `|w| = 2` keeps `|D| = 3`. The shortening move then applies to any relator
   in which `w^{±1}` appears as a (cyclic) subword.

**Consequence: `N` is an upper bound, not a minimum — and for AK(3) it is already not
attained.** Items 2 and 6 combine: a rotation can expose the *same* length-2 factor at the
front of two different relators, and then **one** definition shortens **both**, removing two
units of length for one generator.

> **Proposition (rank-8 triangulation of AK(3)).** `AK(3)` has a triangulation at rank
> **8**, not 9. Rotate `r_1` and `r_2` by AC3 so that both begin with the shared factor
> `xY`:
>
>     r_1 = xyxYXY  --AC3 by (xy)^{-1}-->  xYXYxy
>     r_2 = xxxYYYY --AC3 by (xx)^{-1}-->  xYYYYxx
>
> Define `a := xY` **once** (relator `ayX`) and left-multiply into both:
> `xYXYxy ↦ aXYxy` (5) and `xYYYYxx ↦ aYYYxx` (6). Then peel each down by §4.2 (2 more
> peels for the first, 3 for the second). Result — 8 generators, 8 relators, all length 3:
>
>     generators:  x  y  a  b  c  d  e  f
>     relators:    cxy   fxx   ayX   bxA   cyB   dyA   eyD   fyE
>     definitions: a = xY,  b = xYX,  c = xYXY,  d = xYY,  e = xYYY,  f = xYYYY
>
> Back-substitution gives `cxy ↦ xYXYxy` and `fxx ↦ xYYYYxx`, i.e. the **rotations** of
> `r_1, r_2` — which is exactly right, since the rotations were produced by AC3 and are
> conjugates of the originals (`xy·(xYXYxy)·(xy)^{-1} = r_1`, `xx·(xYYYYxx)·(xx)^{-1} = r_2`).
> Machine-verified (§7).

So **`tri(AK(3)) ≤ 8`**, and `N = 9` is merely what the naive left-prefix algorithm spends.
**The minimal triangulation rank `tri(P)` is `≤ N` and is otherwise OPEN.** In particular
*nothing here says `tri(AK(3)) = 9` or `= 8`*; both are witnesses, i.e. upper bounds
(`parallel-runs-and-bound-direction.md`: a construction bounds from **above**, and "the
class first meets the profile at rank 9" would be exactly the backwards reading that lesson
was written about). **`[OPEN-1]`**

**This matters operationally for A4:** the `γ_N` census cost grows with `N`, so the rank-8
member is the cheaper first target, and the rank-9/rank-8 pair are *different* presentations
whose thickenability must be tested separately (T-S1 forbids transferring the answer between
them, even though both are in AK(3)'s stable class).

### 4.6 What Lemma S-b does and does not license

- ✔ `P_Δ` is stably AC-equivalent to `P`, by a chain that never destabilizes.
- ✔ `P_Δ` is a balanced presentation of the trivial group at rank `N` with all relators of
  length ≤ 3, so it is in range of the exact `γ_N` census (S0 §2).
- ✘ **Nothing may be inferred about the thickenability of `P_Δ` from that of `P`, or vice
  versa** (S0 trap T-S1). `P_Δ` is 3-deformation equivalent to `P` but not homeomorphic to
  it, and thickenability is not a homotopy invariant. In particular the codex line's finding
  that AK(3) and its censused CoV family are non-thickenable says **nothing** about
  `P_Δ(AK(3))`. That is precisely why running the test on `P_Δ` is informative.
- ✘ No move count, no complexity claim (T-S5).
- ✘ If some triangulation of AK(3) *is* found thickenable, the inference "therefore AK(3)
  is stably AC-trivial" runs through Lackenby Thm 1.3, which `LITERATURE_STATUS.md` §1 marks
  **[UNVERIFIED]** — even its theorem number is unconfirmed. Such a hit must be reported as
  "a thickenable member of AK(3)'s stable class exists", never as a triviality result, until
  task A2 settles the source.

---

## 5. Corollary F1 — the rank-(n+1) stable ambient automorphism principle

### 5.1 Statement

> **Corollary F1.** Let `P = ⟨x_1,…,x_n | r_1,…,r_n⟩` be a balanced presentation **of the
> trivial group** and let `φ ∈ Aut(F_n)`. Then `P` and `φ(P) := ⟨x_1..x_n | φ(r_1),…,φ(r_n)⟩`
> are joined by a chain of AC1–AC5 moves in which **the rank never exceeds `n+1`**.
> Equivalently, in the notation of `S0` §4, `φ(P) ~^{(1)} P`.
>
> Consequently the whole `Aut(F_n)`-orbit of `P` lies in the `~^{(1)}`-class of `P`.

**The honest number is `n+1`, with no fudge**: the chain is a sequence of *excursions*, one
per elementary factor of `φ`, each of the shape `n → n+1 → n`. Rank `n+1` is attained;
`n+2` never is.

**This is the STABLE form only.** FRAMING §3 records that the *unstable* pairwise
automorphism principle (same statement with the rank pinned at `n`, no stabilization) is
**open and conjectured false** by Panteleev–Ushakov. Corollary F1 says nothing about it;
the single stabilization is doing real work, and §5.2 Step 4 shows exactly what.

*Preliminary.* If `P` presents the trivial group so does `φ(P)`: `φ` is an automorphism, so
`⟪φ(r_i)⟫ = φ(⟪r_i⟫) = φ(F_n) = F_n`. Both endpoints are therefore legitimate inputs for
Lemma S-a.

### 5.2 The excursion for one elementary substitution

Call `α ∈ Aut(F_n)` an **elementary substitution** if for some index (wlog `1`) and some
`w ∈ F_n`,

    α(x_1) = w,   α(x_j) = x_j  (j ≥ 2),    and  (w, x_2, …, x_n) is a basis of F_n.

Since `(w,x_2,…,x_n)` is a basis, there is a unique word `W` with
`x_1 = W(w, x_2, …, x_n)`.

**Fact F1-β.** Define `β ∈ End(F_n)` by `β(x_1) = W(x_1, x_2, …, x_n)`, `β(x_j) = x_j`.
Then `β = α^{-1}`. *Proof:* `α` is a homomorphism and `W` is a word, so
`α(β(x_1)) = W(α x_1, x_2, …, x_n) = W(w, x_2, …, x_n) = x_1`, and `α(β(x_j)) = x_j`;
hence `α ∘ β = id`. As `α` is an automorphism, `β = α^{-1}`. ∎

> **Proposition F1-elem.** For every balanced presentation `P` of the trivial group and
> every elementary substitution `α`, the presentations `P` and `α^{-1}(P)` are joined by a
> chain `n → n+1 → n` of AC1–AC5 moves.

*Proof.*

**Step 1 — stabilize.** AC4 with fresh `z`: tuple `(r_1,…,r_n, z)` over `F(x_1..x_n,z)`.
Rank `n+1`.

**Step 2 — define `z := w`.** `P` presents the trivial group, so Lemma S-a applies with
`w^{-1}`:

    (r_1,…,r_n, z)  ⟶  (r_1,…,r_n, D),      D := z·w^{-1} .

**Step 3 — substitute `x_1` away.** Let `H := F(x_2,…,x_n,z) ⊆ F(x_1,…,x_n,z)`, a free
factor, and define the homomorphism

    θ : F_n → H,     θ(x_1) = W(z, x_2,…,x_n),   θ(x_j) = x_j  (j ≥ 2).

`θ` is an **isomorphism onto `H`**. Let `ζ : F_n → H` be the basis-to-basis map
`x_1 ↦ z`, `x_j ↦ x_j` — an isomorphism, since `(z, x_2,…,x_n)` is a basis of `H`. Then
`ζ(β(x_1)) = ζ(W(x_1,x_2,…,x_n)) = W(z,x_2,…,x_n) = θ(x_1)` and `ζ(β(x_j)) = x_j = θ(x_j)`,
so `θ = ζ ∘ β` with `β = α^{-1}` an automorphism (Fact F1-β). A composite of two
isomorphisms, hence an isomorphism onto `H`.

Claim: for each `i`, `r_i^{-1}θ(r_i) ∈ ⟪D⟫^{F(x_1..x_n,z)}`. Indeed
`F(x_1..x_n,z)/⟪D⟫ ≅ F_n` via `z ↦ w` (Tietze: `D` is a defining relator for `z`), and
under that map `θ(x_1) = W(z,x_2..x_n) ↦ W(w,x_2..x_n) = x_1` and `θ(x_j) ↦ x_j`; so
`θ(r_i) ↦ r_i` and the claim follows.

Now apply Lemma 0.3 to slot `i` with `c = r_i^{-1}θ(r_i)`: its "other relators" normal
closure contains `⟪D⟫`, since `D` sits in slot `n+1 ≠ i`. Doing this for `i = 1,…,n` in
turn (the slot `n+1` still holds `D` throughout, because Lemma 0.3 restores it) yields

    (θ(r_1), …, θ(r_n), D) ,     rank still n+1.

Because `θ(F_n) = H`, the generator `x_1` **occurs in none of `θ(r_1),…,θ(r_n)`**.

**Step 4 — turn `D` into a single generator. (Triviality is used here, again.)** Since `θ`
is an isomorphism onto `H` and `⟪r_1..r_n⟫^{F_n} = F_n` (triviality of the presented
group), `⟪θ(r_1),…,θ(r_n)⟫^{H} = θ(F_n) = H`. As `F(x_1..x_n,z) = ⟨x_1⟩ * H`, the normal
closure of `H` in it is the kernel of the exponent-sum homomorphism
`σ : F(x_1..x_n,z) → ℤ`, `x_1 ↦ 1`, `x_j, z ↦ 0`. Hence

    C_{n+1} = ⟪θ(r_1),…,θ(r_n)⟫^{F(x_1..x_n,z)} = ker σ .

Abelianize the basis condition: `(ŵ, e_2,…,e_n)` is a basis of `ℤ^n`, so the `e_1`-coefficient
of `ŵ` — which is `σ_{x_1}(w)` — is `±1`. Put `ε := σ(D) = −σ_{x_1}(w) ∈ {+1,−1}` and
`t := x_1^{ε}`. Then `σ(D^{-1} t) = −ε + ε = 0`, so `c := D^{-1}t ∈ ker σ = C_{n+1}`, and
Lemma 0.3 gives

    (θ(r_1),…,θ(r_n), D)  ⟶  (θ(r_1),…,θ(r_n), x_1^{ε}) ,

followed if `ε = −1` by AC1 on slot `n+1`, producing the relator **exactly `x_1`**.

*This is the step the task warned about, and it is the second and last use of triviality.*
AC5 requires the deleted relator to be a single generator, and `D = z w^{-1}` is a
cyclically reduced word of length `|w|+1 ≥ 2`, so no amount of AC1/AC3 can turn it into
`x_1` — conjugation and inversion preserve cyclically-reduced length. Only the transfer
primitive can, and it needs `D^{-1}x_1^{ε} ∈ ⟪θ(r_i)⟫`, which is where `⟪r_i⟫ = F_n` enters.

**Step 5 — destabilize.** `x_1` occurs in no relator other than the one equal to it
(Step 3), so AC5 deletes the generator `x_1` and that relator:

    ⟨x_2,…,x_n, z | θ(r_1),…,θ(r_n)⟩ ,     rank n, balanced.

**Step 6 — rename.** Apply the bijection of generator symbols `ν : z ↦ x_1`, `x_j ↦ x_j`
(§1: names, not a move). The resulting presentation over `{x_1,…,x_n}` has relators
`νθ(r_i)`. Now `ν = ζ^{-1}`, so `ν θ = ζ^{-1}ζβ = β = α^{-1}` by Fact F1-β. Hence the
endpoint is `α^{-1}(P)`. The rank was `n, n+1, …, n+1, n`. ∎

**Both directions come free.** `α^{-1}` is again an elementary substitution (its `x_1`-image
is `W(x_1,x_2,…,x_n)`, and `(W(x_1,x_2..x_n), x_2,…,x_n)` is a basis), so the proposition
applied to `α^{-1}` gives `P ~^{(1)} α(P)` as well. Concretely: to realize the transvection
`x_1 ↦ x_1x_2` take `w = x_1x_2^{-1}`.

### 5.3 From elementary substitutions to all of `Aut(F_n)`

Let `E ⊆ Aut(F_n)` be the set of elementary substitutions.

**(a) Composition.** If `β = α_k ∘ ⋯ ∘ α_1` with `α_l ∈ E`, run one excursion per factor:

    P  ~^{(1)}  α_1(P)  ~^{(1)}  α_2α_1(P)  ~^{(1)}  ⋯  ~^{(1)}  β(P) .

Each intermediate `α_l⋯α_1(P)` is again a balanced presentation of the trivial group
(§5.1 preliminary), so Proposition F1-elem applies at every stage. Every excursion peaks at
rank `n+1`, so the concatenated chain never exceeds `n+1`.

**(b) `E` generates `Aut(F_n)`.** Nielsen's theorem states that `Aut(F_n)` is generated by
the elementary Nielsen transformations: permutations of the basis, inversion of one basis
element, and `x_i ↦ x_i x_j`. Inversions and transvections are in `E` by inspection. For the
permutations it suffices to handle a transposition, and a transposition of two basis
elements is a product of four elements of `E` acting on that pair alone. Work on `F(x,y)`
and put

    α_1 : x ↦ xy ,    α_2 : y ↦ yX ,    α_3 : x ↦ yx ,    α_4 : y ↦ Y

(each changes exactly one basis element, and in each case the resulting pair is a basis:
`(xy,y)`, `(x,yX)`, `(yx,y)`, `(x,Y)`), so `α_1,…,α_4 ∈ E`. Their composite is the
transposition. Tracking the basis pair `(β(x), β(y))` for the partial composites
`β = α_1`, `α_1α_2`, `α_1α_2α_3`, `α_1α_2α_3α_4`:

    (x, y) → (xy, y) → (xy, X) → (y, X) → (y, x)

so `α_1 ∘ α_2 ∘ α_3 ∘ α_4 : x ↦ y, y ↦ x`. (Machine-verified in §7.) The same four moves
applied to the pair `(x_i, x_j)`, fixing all other generators, transpose `x_i` and `x_j`;
transpositions generate all permutations.

Therefore `⟨E⟩ = Aut(F_n)`, and (a) gives Corollary F1 for every `φ ∈ Aut(F_n)`. ∎

**`[UNVERIFIED-CLASSICAL-1]` — the one external input.** Nielsen's generation theorem
("the elementary Nielsen transformations generate `Aut(F_n)`") is a standard textbook fact,
but no source was opened in this session and `literature/` holds no group-theory texts, so
per CLAUDE.md's literature rule it is flagged rather than cited. Note the containment of the
risk: it is used **only** in §5.3(b), only to pass from `⟨E⟩` to `Aut(F_n)`. If it were
somehow wrong, Corollary F1 would survive verbatim in the form *"for every `φ ∈ ⟨E⟩`"*, and
`⟨E⟩` already contains all inversions, all transvections and all permutations by the
computation above. Lemma S-a, Lemma S-b, the AK(3) triangulation and §5.2 do not depend on
it at all.

### 5.4 Machine check of the F1 algebra

For the five elementary substitutions `α : x ↦ w` on `F(x,y)` with
`w ∈ {xy, xY, X, yx, Yx}`, the script of §7 verifies, with `R` set to AK(3)'s relators:

| `α : x ↦` | `θ : x ↦` | `D = z w^{-1}` | `σ_{x}(D)` | relator before AC5 | `νθ = α^{-1} : x ↦` |
|---|---|---|---|---|---|
| `xy` | `zY` | `zYX` | −1 | `X` → AC1 → `x` | `xY` |
| `xY` | `zy` | `zyX` | −1 | `X` → AC1 → `x` | `xy` |
| `X`  | `Z`  | `zx`  | +1 | `x`              | `X`  |
| `yx` | `Yz` | `zXY` | −1 | `X` → AC1 → `x` | `Yx` |
| `Yx` | `yz` | `zXy` | −1 | `X` → AC1 → `x` | `yx` |

and in every row: `W(w,y) = x`; `x` does not occur in `θ(r_i)`; `θ(r_i)` collapses to `r_i`
under `z ↦ w`; `σ_x(D^{-1}t) = 0`; and `νθ ∘ α = α ∘ νθ = id`.

### 5.5 Relation to `S0` §4 question F1

`S0` asks: *is `~^{(1)}` already the full `Aut(F_n)`-orbit closure?* This corollary settles
one inclusion only:

    (AC1–AC3-class of the Aut(F_n)-orbit of P)   ⊆   the ~^{(1)}-class of P.

The reverse inclusion — that a single stabilization buys **nothing more** than ambient
automorphisms and unstable AC moves — is **not** proved here and I see no reason to expect
it. **`[OPEN-2]`** Note the direction hazard: this corollary *constructs* chains, so it
bounds the `~^{(1)}`-class from **below** (it makes the class bigger). It can never be used
to argue that some presentation is *outside* `~^{(1)}`.

---

## 6. Hypothesis ledger — exactly what is used where

### 6.1 Where "the group is trivial" is used

| location | what is needed | why triviality |
|---|---|---|
| Lemma S-a §3.2 | `w ∈ ⟪r_1..r_n⟫^{F_n}` for the *given* `w` | to have it for **all** `w`, need `⟪r_i⟫ = F_n` |
| Lemma S-b §4.2 Step P2 | Lemma S-a at every intermediate rank | loop invariant: each intermediate presentation still presents 1 |
| F1 §5.2 Step 2 | Lemma S-a with `w^{-1}` | same as above |
| F1 §5.2 Step 4 | `⟪θ(r_i)⟫ = ker σ`, so that `D` can be converted to `x_1^{±1}` | uses `⟪r_i⟫^{F_n} = F_n` |

**Not** used: F1 §5.2 Step 3 (the substitution `r_i ↦ θ(r_i)`) is valid for *any* balanced
presentation — it only needs `θ(r_i) = r_i` modulo `⟪D⟫`, which is formal.

Sharpness: Proposition S-a-sharp (§3.3) shows the hypothesis in Lemma S-a is not merely
convenient but necessary and sufficient, with the explicit `ℤ/2` counterexample of §3.4.
The triviality uses in Lemma S-b and F1 are inherited from it; I have **not** proved that
F1's Step-4 use is separately sharp. **`[GAP-2]`** (a non-trivial-group counterexample to F1
as a whole would settle it; not attempted).

### 6.2 Where "balanced" is used

Only to make the statements about rank and about `AC5` line up: AC4/AC5 preserve balance,
and `P_Δ`/`α^{-1}(P)` being balanced is part of the conclusions. The proofs of Lemmas 0.1–0.3
and of Lemma S-a never use balance.

### 6.3 What is deliberately **not** claimed

- **No move counts** anywhere (FRAMING trap 6, S0 trap T-S5). §3.5 explains why: the chain
  length is an area/Dehn-function quantity.
- **No minimality** of `N` (§4.5, `[OPEN-1]`), and no "first/at least" phrasing about rank 9
  — a construction bounds from **above** (project lesson `parallel-runs-and-bound-direction.md`).
- **No thickenability inference** between `P` and `P_Δ` in either direction (T-S1).
- **No AC-triviality and no stable AC-triviality** of AK(3) or of anything else.
- **No paper cited.** `PROOFS.tex` is absent from this clone and was not read;
  `literature/` holds no papers. The only external input is `[UNVERIFIED-CLASSICAL-1]`.

### 6.4 Index of flags

| flag | content | impact if wrong |
|---|---|---|
| `[GAP-1]` §4.3 | can every relator be made length **exactly** 3 (length-2 relators)? | none for AK(3); cosmetic for the general normal form |
| `[GAP-2]` §6.1 | is F1's Step-4 use of triviality separately sharp? | none — it is a *sufficiency* proof |
| `[OPEN-1]` §4.5 | minimal triangulation rank `tri(P)`; proved `tri(AK(3)) ≤ 8` | none — 8 and 9 are both witnesses (upper bounds) |
| `[OPEN-2]` §5.5 | is `~^{(1)}` *exactly* the Aut-orbit closure? | none — only one inclusion is used |
| `[UNVERIFIED-CLASSICAL-1]` §5.3 | Nielsen generation of `Aut(F_n)` | F1 retreats to `φ ∈ ⟨E⟩`; nothing else affected |

---

## 7. Reproducible checks

Small, self-contained, < 0.05 s. Copy into a scratch file and run with `python3` (no
dependencies). It verifies the whole §4.4 trace, both back-substitutions, the letter
conservation count, the §3.4 lattice certificate and its control, and the §5.3(b) swap
identity.

```python
def inv(w): return w[::-1].swapcase()
def fr(w):
    o=[]
    for c in w:
        if o and o[-1]==c.swapcase(): o.pop()
        else: o.append(c)
    return "".join(o)
def sub(w,t): return fr("".join(t.get(c,c) if c.islower() else inv(t.get(c.lower(),c.lower())) for c in w))

r1, r2 = "xyxYXY", "xxxYYYY"
assert fr("xyx"+inv("yxy"))==r1 and fr("xxx"+inv("yyyy"))==r2      # the words are AK(3)

fresh=list("abcdefg"); defs=[]
def peel(r):
    cur=r
    while len(cur)>3:
        z=fresh.pop(0); D=fr(z+inv(cur[:2]))
        assert len(D)==3
        new=fr(D+cur); assert len(new)==len(cur)-1                  # seam: exactly 2 cancels
        defs.append((z,cur[:2],D)); cur=new
    return cur
R1, R2 = peel(r1), peel(r2)
rel=[R1,R2]+[D for _,_,D in defs]
assert (R1,R2)==("cXY","gYY")
assert [D for _,_,D in defs]==["aYX","bXA","cyB","dXX","eXD","fyE","gyF"]
assert len(rel)==9==2+max(0,len(r1)-3)+max(0,len(r2)-3)             # balanced, rank formula
assert all(len(w)==3 for w in rel)

tab={}
for z,word,D in defs: tab[z]=sub(word,tab)
assert tab=={"a":"xy","b":"xyx","c":"xyxY","d":"xx","e":"xxx","f":"xxxY","g":"xxxYY"}
assert sub(R1,tab)==r1 and sub(R2,tab)==r2                          # back-substitution
assert all(sub(D,tab)=="" for _,_,D in defs)
from collections import Counter
c=Counter("".join(rel).lower())
assert c["x"]==6 and c["y"]==7 and sum(c.values())==27               # conservation

# 4.5: the shared-definition rank-8 triangulation of AK(3)
def rot(s,k): return fr(inv(s[:k])+s+s[:k])                          # AC3: s = uv -> vu
A,B = rot(r1,2), rot(r2,2)
assert A=="xYXYxy" and B=="xYYYYxx" and A[:2]==B[:2]=="xY"           # shared factor
fresh=list("abcdef"); defs8=[]
def define(z,word):
    D=fr(z+inv(word)); assert len(D)==3; defs8.append((z,word,D)); return D
def shorten(s,D):
    new=fr(D+s); assert len(new)==len(s)-1; return new
D0=define(fresh.pop(0),"xY"); A,B = shorten(A,D0), shorten(B,D0)      # ONE def, BOTH relators
def down(s):
    while len(s)>3: s=shorten(s,define(fresh.pop(0),s[:2]))
    return s
A,B = down(A), down(B)
rel8=[A,B]+[D for _,_,D in defs8]
assert len(rel8)==8 and all(len(w)==3 for w in rel8)                  # rank 8 < 9
assert rel8==["cxy","fxx","ayX","bxA","cyB","dyA","eyD","fyE"]
t8={}
for z,word,D in defs8: t8[z]=sub(word,t8)
assert t8=={"a":"xY","b":"xYX","c":"xYXY","d":"xYY","e":"xYYY","f":"xYYYY"}
assert sub(A,t8)==rot(r1,2) and sub(B,t8)==rot(r2,2)                  # rotations of r1, r2
assert fr("xy"+rot(r1,2)+inv("xy"))==r1 and fr("xx"+rot(r2,2)+inv("xx"))==r2

# 3.4: row lattices in Z^2 for (x^2, z) vs (x^2, zx) vs (x^2, zxx)
def hnf(M):
    a,b=[list(r) for r in M]
    while b[0]!=0:
        if a[0]==0 or abs(a[0])<abs(b[0]): a,b=b,a
        q=a[0]//b[0]; a=[a[0]-q*b[0],a[1]-q*b[1]]; a,b=b,a
    if a[0]<0: a=[-a[0],-a[1]]
    if b[1]<0: b=[-b[0],-b[1]]
    if b[1]: a=[a[0],a[1]%b[1]]
    return (tuple(a),tuple(b))
assert hnf([[2,0],[0,1]]) != hnf([[2,0],[1,1]])                      # w = x   : NOT equivalent
assert hnf([[2,0],[0,1]]) == hnf([[2,0],[2,1]])                      # w = x^2 : consistent

# 5.3(b): swap is a product of four elementary substitutions
def comp(f,g): return {k:sub(v,f) for k,v in g.items()}
beta=comp({"x":"xy","y":"y"},comp({"x":"x","y":"yX"},comp({"x":"yx","y":"y"},{"x":"x","y":"Y"})))
assert beta=={"x":"y","y":"x"}
print("ALL CHECKS PASS")
```

---

## 8. Handoff

- **A3 (`triangulate.py`)**: §4.2 is the transform; §4.5 items 1–6 are the choice family;
  the replay certifier required by T-S3 must reproduce, from `P` alone, the AC4 + AC1–AC3
  chain and land on the claimed `P_Δ` — note that the *Lemma S-a* portion of the chain
  requires an expression of `w` as a product of conjugates of the `r_i^{±1}`, which is a
  search problem in its own right (§3.5). A certifier that verifies only the *peel
  arithmetic* (as §7 does) certifies (ii)/(iii) but **not** (i); a full elementary-move
  replay needs that expression. Recommended: certify (i) at the level of the compound moves
  of Lemma 0, which is exactly what the proofs use.
- **A4 (`γ_N` census)**: two ready inputs, the rank-**8** presentation of §4.5 (cheaper —
  run it first) and the rank-**9** one of §4.4; they are different presentations and T-S1
  forbids transferring a verdict between them. Heed the germ-degree warning at the end of
  §4.4 (T-S4: exact census, not the 3-connectivity fast path). Calibrate on a positive
  ladder first
  (`calibrate-one-sided-hunts-on-a-positive-ladder.md`) — a null from an uncalibrated hunt
  bounds nothing.
- **A5 (audit)**: the three places most worth attacking are (α) the loop invariant in §4.3
  (does Lemma S-a really re-apply at every intermediate rank?), (β) Step 4 of §5.2 (the
  `ker σ` computation and the `σ_{x_1}(w) = ±1` claim), and (γ) the renaming convention in
  §5.2 Step 6 — if a reader insists that generator symbols are rigid, F1's conclusion must
  be restated as "`P` and `α^{-1}(P)` up to the canonical relabelling", which is what §1
  licenses.
