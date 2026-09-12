# Theory wave 1 — general stable-AC theorems for U124 power-block pairs

Author: theory inventor. Owned file. Proposes catalogue entries **C16, C17, C18**.
Nothing here claims a U124 row is solved. See "Non-claims" before quoting anything.

---

## HEADLINE CANDIDATE — C16, conjugate-tag exchange corridor

Let `ξ = y⁻¹xy`. For **any** words `A`, `B` in the two letters `x, ξ`, any `p ≠ 0`
and any `b, c ∈ ℤ`:

```
⟨ x, y |  A(x,ξ) · y xᵇ y⁻¹ · B(x,ξ) ,   ξᵖ xᶜ y⁻¹ ⟩
   ~_st
⟨ x, u |  A(x,u) · uᵖ xᵇ u⁻ᵖ · B(x,u) ,   u⁻¹ x⁻ᶜ u⁻ᵖ x uᵖ xᶜ ⟩
```

by two gated CoVs (C2/Prop A) plus a bounded, explicitly counted elementary core
(3 + 4 AC2 moves, each with one AC3 and at most one AC1). **The first output row contains no
`c` at all, and every occurrence of `c` in the second output row is a conjugating
flank `x^{±c}`.** The corridor therefore *exchanges the power block `x^c` from
conjugated content into pure conjugator* — the "rank-3 isolator corridor through
the `x^{nδ}` block" in exact, `n`-free, parameter form.

Instance `(A,B,p,b,c) = (x⁻¹ξ, 1, 2, δ, nδ)` **is** `Q'_{n,δ}` (the `y ↦ x⁻²y`
image of `Q_{n,δ}`), with output

```
S_{n,δ}  =  ( x⁻¹u³xᵟu⁻² ,  u⁻¹ x⁻ⁿᵟ u⁻² x u² xⁿᵟ )
```

**Corollary C16.1 (rigidity, `δ=+1`).** One further legal AC2 (donor = an AC3
rotation of row 1 inverted) sends `S_{n,+1}` to `P_{n,+1}` **verbatim** under the
generator shift `(x,y) ↦ (u,x)`, same `n`. The corridor is a *closed loop*: no
member of the C16 family can move `n` on the `δ=+1` branch. For `δ=−1` that
rotation does not exist and the corridor escapes to a new, non-HNN donor class.

---

## Status labels (THEOREM_CATALOGUE.md convention)

* **C16** — IDENTITY-CHECKED (general parameter sweep + U124 instance, exact).
  Stable expansion displayed; two C0 uses make it non-effective. Independent
  replay pending → not PROVEN.
* **C16.1** — IDENTITY-CHECKED NEGATIVE (exact, bounded; `n = 2..7`, `δ=+1`).
* **C17** — IDENTITY-CHECKED positive criterion, *conditional on C4's Nielsen
  descent being certified*; the shear corridor itself is effective and
  Lemma-11-free. U124 hypothesis **fails** (exact congruence); the orbit
  computation is exact and complete relative to the two shear moves.
* **C18** — IDENTITY-CHECKED; a generalization of the existing **C9**
  (power–Bézout) off the AK3 root, plus a radix corollary. U124 hypothesis
  **ABSENT**, strengthening C9's `v = y⁻¹x⁻²` diagnostic.

Evidence base, all reproducible:

| what | scale | result |
|---|---|---|
| C16/C17/C18 identity sweeps | 8 122 checks | 0 failures |
| `aut_canon` orbit witnesses | 30 pairs (`P`, `Q'`, `S`; `n=2..6`; both `δ`) | every witness re-verified by pure substitution, `check(pair, rep, phi)` true |
| C18 H1 shape census | 1 764 rotations/inversions | 0 hits |
| overgroup criterion (C8-adjacent) | 36 pairs | 0 candidates; `Q'` complete |
| cyclic-complement rose probe | 12 `S`-pairs | 0 rose hits |

The replay script at the end of this file reproduces rows 1, 2 and 3 and is
read-only; it depends only on `experiments/equivalence_classes/lib/autcanon.py`.
Rows 4 and 5 use the campaign's own code unmodified —
`experiments/stable_ac/ak3_inverse_substitution_overgroups.py`
(`enumerate_overgroups(words=…, max_states=5000)`) and
`research/u124_stable_20260912/code/q_cyclic_complement.py`'s
`initial_graph`/`merge_vertices` rose test — applied to the `S` and `Q'` words
displayed below.

## Non-claims (binding)

* No U124 row is solved, removed, or given a trivialization certificate here.
* No `Aut(F₂)` step below is an ordinary AC move. `aut_min_len` / `aut_canon`
  are orbit calculations; where a theorem needs one it is flagged **C1** and
  inherits C1's non-effectiveness.
* The two gated CoVs each use **C0 (Lemma 11)**. Cost is finite but **unbounded**.
  It is never charged linearly and never presented as a replayable move count.
* Length rises along C16: `μ` goes `n+12 → 2n+13`, and raw total goes
  `n+12 → 2n+13`. That is allowed by the brief; the well-founded measures below
  are *not* length, and no length drop anywhere here is offered as progress.
* C16.1 is a statement about the C16 corridor family only. It is not an AC
  obstruction and does not obstruct longer or different routes.
* C17's `δ=+1` terminal is the reciprocal BS(3,2) donor. Per `c15_bs_stall.md`,
  triviality is **not** declared from BS(1,2) symmetry or reciprocal BS(3,2).

---

# C16. Conjugate-tag exchange corridor

## (1) Exact hypotheses

Stated in **Magnus coordinates**, so that they are decided by one linear scan of
each relator word and nothing else. Write `ξ_i = y⁻ⁱ x yⁱ` (so `ξ_0 = x`, and
`ξ_1 = ξ = x^y`). Scanning a word left to right and recording, for each maximal
`x`-block, the running `y`-exponent `s` of the prefix before it, gives the unique
**Magnus decomposition**

```
W  =  ξ_{−s₁}^{e₁} · ξ_{−s₂}^{e₂} · ⋯ · ξ_{−s_k}^{e_k} · y^{h}
```

with `h` the total `y`-exponent. (Checked: the decomposition rebuilds each `Q'`
row letter-for-letter.) The hypotheses are:

* **H1.** The pair is on two generators `x, y`, freely reduced, balanced.
* **H2 (the isolator row).** One row `S` has total `y`-exponent `h = −1` and
  Magnus support `{1, 0}` in that order, with exactly one block at each:
  `S = ξ_1^p · ξ_0^c · y⁻¹`, `p ≠ 0`, `c ∈ ℤ`. Call `p` the **tag power** and `c`
  the **block**.
* **H3 (the companion row).** The other row `R` has total `y`-exponent `h = 0`,
  Magnus support contained in `{0, 1, −1}`, and **exactly one** block at index
  `−1`, of exponent `b`. Writing the blocks before it as `A(x,ξ)` and after it as
  `B(x,ξ)` — both words in `ξ_0 = x` and `ξ_1 = ξ` — this is precisely
  `R = A(x,ξ) · ξ_{−1}^{b} · B(x,ξ) = A(x,ξ) · y xᵇ y⁻¹ · B(x,ξ)`.

No primitivity test, no search, no Whitehead call, no heap. The verified `Q'`
decompositions are

```
R  =  ξ_0⁻¹ · ξ_1 · ξ_{−1}^δ                blocks [(0,−1),(1,1),(−1,δ)], h = 0
S  =  ξ_1²  · ξ_0^{nδ} · y⁻¹                blocks [(1,2),(0,nδ)],        h = −1
```

so `(A, B, p, b, c) = (x⁻¹ξ, 1, 2, δ, nδ)`. Note `S` has **three** `y`-letters at
rank 2 (`ξ_1² = Yxxy` after cancellation); the "exactly one `y`-letter" that makes
it an isolator is a *consequence* of Gate 1, not a hypothesis — see (3).

> Note on why the campaign did not see this. `ingest/q_common_tail.md` ran an
> isolator census with `|w| ≤ 2`, `|I| ≤ 5` and accepted 0 of 62 464 templates on
> `Q_{2,−1}`. The correct tag here is `ξ = x^y = Yxy`, of length **3**. That
> census structurally could not represent it. The 0/62 464 is therefore not
> evidence against C16.

## (2) Free-group identities, written out

With `ξ = Yxy` and `m = nδ`, for `Q'_{n,δ} = ( XYxyy xᵟ Y , Yxxy xᵐ Y )`:

```
R  =  x⁻¹ · ξ · y xᵟ y⁻¹                       (A = x⁻¹ξ, B = 1, b = δ)
S  =  ξ² · xᵐ · y⁻¹                            (p = 2, c = m)
```

Rank-3 rows after the first gated CoV (`u := ξ`), with the hidden cancellations
shown — `ξ`'s trailing `y` merges with the following `y`:

```
I_R  =  x⁻¹ u  y xᵟ y⁻¹        ( "XuyxY"   ← "XYxyyxY" ,  |7| → |5| )
I_S  =  u² xᵐ y⁻¹              ( "uuxxY"   ← "YxxyxxY" ,   |7| → |5| , n=2 )
D    =  u⁻¹ y⁻¹ x y            ( "UYxy" ,  the tag definition )
```

Faithfulness (checked, not assumed): substituting `u ↦ Yxy` into `I_R` returns
`R` letter-for-letter, and into `I_S` returns `S`. `I_S` contains exactly one
`y`-letter.

Isolator: `I_S = 1 ⟺ y = u^p x^c =: e`. Substituting `y ↦ e` in `I_R` and `D`:

```
Â  =  A(x,u) uᵖ xᵇ u⁻ᵖ B(x,u)             ⟶  x⁻¹ u³ xᵟ u⁻²        ("XuuuxUU")
B̂  =  u⁻¹ x⁻ᶜ u⁻ᵖ x uᵖ xᶜ                 ⟶  u⁻¹x⁻ᵐu⁻²xu²xᵐ       ("UXXUUxuuxx", n=2)
```

`Â` is `c`-free; rebuilding with `c+11` gives the identical `Â` (checked for
every parameter tuple in the sweep).

Auxiliary identities used by C16.1 (`δ = +1`):

```
ρ  :=  x⁻¹u⁻³xu²          is a cyclic rotation of  Â⁻¹ = u²x⁻¹u⁻³x       ✔ δ=+1
ρ  is NOT a rotation of Â⁻¹ = u²xu⁻³x                                    ✘ δ=−1
B̂ · (x⁻ᵐ ρ xᵐ)⁻¹  =  u⁻¹ x⁻ᵐ (ux) xᵐ  =  u⁻¹x⁻ⁿ u xⁿ⁺¹        (δ=+1, m=n)
```

so `S'_n := ( x⁻¹u³xu⁻² , u⁻¹x⁻ⁿuxⁿ⁺¹ )`, and writing `(a,t) = (u,x)`:

```
row 1 of S'_n  =  rotation of ( t⁻¹a⁻³ta² )⁻¹   =  P₁ of P_{n,+1} under (x,y)↦(u,x)
row 2 of S'_n  =  ( t⁻⁽ⁿ⁺¹⁾a⁻¹tⁿa )⁻¹           =  P₂ of P_{n,+1} under (x,y)↦(u,x)
```

## (3) Expansion into AC1–AC3 + stabilization/destabilization

**Gate 1 — adjoin the tag (C2/Prop A; the adjunction step is C0).**
`⟨x,y | R,S⟩ → ⟨x,y,u | R,S,u⟩` is AC4. Converting the row `u` into
`D = u⁻¹y⁻¹xy` is the **C0 (Lemma 11)** composite, legal because the ambient
group is trivial; cost finite, **unbounded**.

**Gate 1 substitutions — bounded, 3 moves.** To replace a displayed block `ξ` in
a row `W = α ξ β` by `u`: the word `ξ⁻¹u` is a cyclic rotation of `D⁻¹`, so
invert `D` (one **AC1**), conjugate that rotation by `β` (one **AC3**) and
multiply (one **AC2**), giving `W ← W · β⁻¹(ξ⁻¹u)β = α u β`. This is exactly the
expansion recipe demanded by `advisor_wave2.md` BLOCKER 3 and by AK3 §2's
displayed-block substitution. Occurrence counts for the U124 instance, checked:
`R` has 1 displayed `ξ`, `S` has `p = 2`. **n_subs = 3.** In general
`n_subs = (#ξ in A) + (#ξ in B) + |p|`.

**Gate 2 — delete `y` by the isolator (C2/Prop A; the removal step is C0).**
`I_S` has `y`-exponent `−1` and one `y`-letter, so `y⁻¹e = y⁻¹uᵖxᶜ` is a cyclic
**rotation** of `I_S`. For each displayed `y^{±1}` in a row `W = α y^{±1} β`:
one **AC3** (conjugate that rotation by `β`; for a displayed `y⁻¹` the rotation
needed is `y x⁻ᶜu⁻ᵖ`, a rotation of `I_S⁻¹`, so one **AC1** first) and one
**AC2**. Counts, checked: `I_R` has 2 `y`-letters, `D` has 2. **n_subs = 4.**
Now `Â` and `B̂` are `y`-free and the only `y` left is the single one in `I_S`.
Removing generator `y` together with the row `I_S = uᵖxᶜy⁻¹` is **C0** again —
*not* a bare AC5, because the row is `y⁻¹·w` and not the letter `y`.

**C16.1 tail — 1 bounded move.** One **AC1** (invert `Â`), one **AC3**
(rotate to `ρ`, then conjugate by `xᵐ`), one **AC2**. `δ = +1` only.

**Ledger.** 1 AC4 · 2 × C0 · 7 AC2, each preceded by one AC3 and by one AC1
whenever the needed rotation is of the *inverted* row (`D⁻¹` in Gate 1, `I_S⁻¹`
for each displayed `y⁻¹` in Gate 2); then +1 AC1 +1 AC3 +1 AC2 for C16.1.
Generator/row count: `2/2 → 3/3 → 2/2`, balanced throughout.

## (4) Well-founded progress measure (length may rise)

Not length: `μ` rises `n+12 → 2n+13`. The measure is on the corridor, and it is
what makes the corridor terminate and what licenses the C0 removal:

> `ν(state) = ( # displayed ξ-blocks in the rows ,
>               # displayed y-letters in the rows other than the isolator )`,
> ordered lexicographically on `ℕ × ℕ`.

Gate 1 drives the first coordinate `3 → 0`, one per move. Gate 2 then drives the
second coordinate `4 → 0`, one per move, and cannot raise the first: at rank 3
the substituted word is `uᵖxᶜ`, which displays no `ξ`-block. So `ν` strictly
decreases lexicographically at every displayed move, `ℕ × ℕ` under lex order is
well-founded, and the corridor terminates in exactly `3 + 4 = 7` moves — a count
read off the input words before starting. At `ν = (0,0)` the only remaining `y`
is the single one in the isolator, which is exactly the hypothesis C0 needs.

This is a **termination** measure for the corridor, not a descent measure for
U124. C16.1 shows no such descent measure can exist inside this corridor class
on the `δ=+1` branch.

## (5) Certificate growth

**Honest answer: unbounded, because C0 (Lemma 11) is used twice** — once to
install `D = u⁻¹x^y`, once to remove `y` with `I_S`. Neither normal-closure
witness is materialized here, so C16 is *non-effective* in exactly C1/C0's sense.

What **is** bounded, uniformly in `n`: the elementary core is 7 AC2 (C16), or 8
AC2 with C16.1, each with one AC3 and at most one AC1 — independent of `n` and,
for the U124 instance, of `b` and `c`; in general the Gate-1 count is
`(#ξ in A) + (#ξ in B) + |p|` and the Gate-2 count is always 4. State
length along the core stays `O(|A|+|B|+|p|+|b|+|c|)`: the largest donor is
`x⁻ᵐρxᵐ` of length `2|c|+7`, and the endpoint has raw total `2n+13` (C16) or
`2n+10` (C16.1) versus the input's `n+12`.

## (6) Examples

**Positive, `n = 2`, `δ = +1`** (every word literal and machine-checked):

```
Q'_{2,+1} = ( XYxyyxY , YxxyxxY )                 μ = 14
 gate 1 → ( XuyxY , uuxxY , UYxy )                rank 3, n_subs 3
 gate 2 → ( XuuuxUU , UXXUUxuuxx )      = S_{2,+1},  μ = 17
 C16.1  → ( XuuuxUU , UXXuxxx )         = S'_2,      raw total 14
 relabel (x,y)↦(u,x):  P_{2,+1} = ( XUUUxuu , XXXUxxu ) up to AC1+AC3   ⇒ LOOP
```

**Negative that must fail — the hypothesis test.** Three rejections, all decided
by the Magnus scan before any move is made:

* `h = −2` instead of `−1`, e.g. `S = ξ²xᶜy⁻²` (`"uuxxYY"` at rank 3). Then no
  rotation of the row equals `y⁻¹·(y`-free`)`, so `y` is not isolated and Gate 2
  is unavailable. C16 must not fire.
* `p = 0` (no tag block at index 1): nothing to exchange, and the output row 2
  degenerates to `u⁻¹x⁻ᶜxxᶜ`, which is not a relator of the claimed shape.
* `R` with **two** blocks at index `−1`, or with any block at index `|i| ≥ 2`:
  H3 fails, the single `y xᵇ y⁻¹` factor does not exist, and the Gate-2 count is
  no longer 4.

**Negative that must fail — the `δ = −1` branch of C16.1.** `Â⁻¹ = "uuxUUUx"`,
whose seven rotations are `{uuxUUUx, uxUUUxu, xUUUxuu, UUUxuux, UUxuuxU,
UxuuxUU, xuuxUUU}`; `ρ = "XUUUxuu"` is **not** among them (it differs from
`xUUUxuu` in the first letter's sign). The `δ = −1` corridor therefore stops at
`S_{n,−1} = ( x⁻¹u³x⁻¹u⁻² , u⁻¹xⁿu⁻²xu²x⁻ⁿ )`, whose donor has `x`-exponent `−2`
and so is **not** an HNN/BS relator at all. Using `ρ` there would be an illegal
move that silently shortens to `2n+8`; it is recorded here precisely so nobody
replays it.

## (7) Why this is not the obstructed `n → n+1` induction

`LISITSA_TRANSFER.md` builds the spine `⟨x,y,z | R1s, R2s, z⁻¹xⁿ⟩` and needs
`z⁻¹xⁿ ~ z⁻¹xⁿ⁺¹` in `G_δ`; that is provably obstructed for `δ=+1` (S₄, 1 584
homs) and holds-but-`Θ(n)` for `δ=−1`.

C16 differs at the spine: its adjoined generator is defined by a **conjugate**,
`D = u⁻¹x^y`, not by a **power** `z⁻¹xⁿ`. No transfer between `n` and `n+1` is
ever asserted or needed — `n` is *fixed* through the whole corridor, and `n`
appears in the output only as a conjugating flank.

C16.1 then says something the transfer route could not: on `δ=+1` the corridor is
an exact self-map of the family with generator shift `(x,y) ↦ (u,x)` and **the
same `n`**. Both results single out `δ=+1` as the rigid branch — LISITSA by a
finite-quotient obstruction to *moving* `n`, C16.1 by an exact self-map that
*fixes* `n` — and C16.1 supplies a candidate mechanism for that rigidity: a
renormalization fixed point. Any `n`-descent on `δ=+1` must leave the C16
corridor class. This is an explanation offered, not a proof that the two
phenomena have a common cause; establishing that link is open.

## (8) What would falsify it

* **C16 identities.** Exhibit `(A,B,p,b,c)` with `sub(I_R, u↦Yxy) ≠ R` or
  `sub(I_S, u↦Yxy) ≠ S`, or with `Â` depending on `c`. Replay: the sweep below
  covers `A ∈ {x⁻¹ξ, ξ², x, 1, x⁻¹ξ², ξx⁻¹}`, `B ∈ {1, x, ξx⁻¹}`,
  `p ∈ {1,2,3,−2}`, `b ∈ {−1,1,2}`, `c ∈ {−5,−2,0,3,7}`; widen it.
* **C16 legality.** Show that Gate 2's "rotation of `I_S`" claim fails for some
  admissible `I_S`, or that the removal of `y` can be done by a bare AC5 (which
  would *improve* C16 to effective, and is worth trying).
* **C16.1.** Produce `n ≤ 7` where `S'_n` is not `P_{n,+1}` relabelled up to
  AC1+AC3 — i.e. break `same_cyc` in the replay. Or defeat the corollary's scope
  by exhibiting C16 parameters with input `Q'_{n,+1}` and an endpoint whose
  `μ ≠ 2n+10`; that would mean the loop is an artefact of the `(x⁻¹ξ,1,2,δ,nδ)`
  tuple rather than of the corridor class.
* **Cheap disproof of usefulness.** If someone finds a *bounded* AC move on
  `S_{n,δ}` that lowers `n`, C16.1's "must leave the corridor class" is vacuous.

---

# C17. Flank shear over a BS(M,N) donor — a bounded, Lemma-11-free criterion

Aimed at the `c15_bs_stall.md` target, which asks for exactly this: "change the
donor by AC1–AC3 so every `y`-syllable length is a multiple of `m`, then rerun
Britton **as a proof not a 10k search**."

## (1) Exact hypotheses

* **H1.** Row 1 is, up to AC1/AC3, `D = x⁻¹u^M x u^{−N}` with `M, N ≥ 1` (a
  BS(M,N) donor; `x` is the stable letter), and `|M − N| = 1`. The shear
  identities in (2) need only the donor; `|M − N| = 1` is used only by the C4
  tail, where it gives `u^{M−N} = u^{±1}`.
* **H2.** Row 2 is, up to AC1/AC3, `E(c,e) = u⁻¹ x⁻ᶜ u⁻ᵉ x uᵉ xᶜ` for integers
  `c` (the **flank**) and `e ≠ 0` (the **inner power**).
* **H3 (the criterion).** `M^{|c|}` divides `e` when `c > 0`; `N^{|c|}` divides
  `e` when `c < 0`.

All three are decided by reading exponents. No search, no Britton preflight.

## (2) Free-group identities

The donor gives `uᴺ = x⁻¹uᴹx`, i.e. the two **shear** rewritings

```
shear-down (needs M | e):   uᶠ ↦ x u^{Nf/M} x⁻¹     ⇒  E(c,e) ↦ E(c−1, Ne/M)
shear-up   (needs N | e):   uᶠ ↦ x⁻¹u^{Mf/N} x      ⇒  E(c,e) ↦ E(c+1, Me/N)
```

both verified **literally** as free words for `(M,N) ∈ {(2,1),(3,2),(4,3),(5,4)}`,
`c ∈ {−3,0,2,5}`, `e ∈ {N, 2N, MN, M²N}`. The two displayed `u^{±e}` blocks shear
simultaneously; the flanking `x^{±c}` absorbs the produced `x^{∓1}`.

Terminal: `E(0,e)` has **exactly one** `x`-letter, so it isolates `x`; e.g.
`E(0,4) = u⁻¹u⁻⁴xu⁴`, and substituting `x ↦ u` kills it, while the same
substitution sends `D = x⁻¹u³xu⁻²` to `u`.

## (3) Expansion into AC1–AC3

Each shear is the AK3 §2 displayed-block substitution against row 1: rotate/invert
row 1 so the block to be replaced is displayed (one **AC3**, one **AC1** if
needed), conjugate by the suffix (**AC3**), multiply (**AC2**). Two blocks per
shear ⇒ 2 AC2 per step. **No stabilization, no destabilization, no C0, no C1.**
Terminal finish: `E(0,e) = u^{−(e+1)} x u^{e}` has exactly one `x`-letter, hence
is primitive (`x ↦ u^{e+1} x u^{−e}` is a Nielsen automorphism carrying it to
`x`), and `x = u` follows; substituting into `D = x⁻¹u^M x u^{−N}` leaves
`u^{M−N} = u^{±1}`. This is **C4**, and C4's own caution applies verbatim: *the
one-occurrence flag is not a solve, and the Nielsen descent to a generator is
extra work that must be certified.* C17 therefore reduces its class to a
certified-C4 obligation; it does not discharge C4.

## (4) Well-founded progress measure

`ν = |c|`, the flank, on `ℕ`. Each shear-down step strictly decreases it by 1;
H3 guarantees the divisibility needed at *every* step (that is why the hypothesis
is `M^{|c|} | e` and not merely `M | e`). Termination at `ν = 0`. The inner power
shrinks as `e·(N/M)^{k}`, so raw length **falls** here — unusually, this corridor
is monotone in both coordinates.

## (5) Certificate growth — **bounded**

`|c|` shear steps × 2 AC2 each, plus at most `2e` AC2 for the terminal
one-occurrence elimination *once C4's Nielsen descent is certified*. Total
`≤ 2|c| + 2e + O(1)` elementary moves, with state length `≤ |c| + 2e + 7`. No
Lemma 11 and no C1 anywhere in the shear corridor: **the shear part of C17 is
effective**, which makes it the only candidate here with a replayable move
bound. The C4 tail is inherited and uncertified, so "C17 trivializes its class"
is a claim about the shear plus a C4 obligation, not a finished certificate.

## (6) Examples

**Positive, `(M,N) = (3,2)`, `c = 2`, `e = 9`** (literal, machine-checked):

```
E(2,9) = U XX UUUUUUUUU x uuuuuuuuu xx
  shear-down →  E(1,6)
  shear-down →  E(0,4) = U UUUU x uuuu        one x-letter ⇒ C4 finish
```

H3 reads `M^{|c|} = 3² = 9`, and `9 | e = 9` ✔. Smallest positive case:
`(c,e) = (1,3)`, orbit `{(1,3), (0,2)}`, flank reaches `0`.

**Negative that must fail — the U124 instance.** `S_{n,+1}` from C16 is exactly
`( D_{BS(3,2)} , E(nδ, 2) )` (checked `n = 2..8`). H3 asks `3^{|nδ|} | 2`;
already `3 ∤ 2`. The complete shear orbit of `(c, e) = (c₀, 2)` under both moves
is the **two-element** set `{(c₀,2), (c₀+1,3)}`, so the flank never decreases and
never reaches `0`:

```
orbit(c=7, e=2) = [(7,2), (8,3)]              min flank 7  ⇒  no descent
orbit(c=1, e=4) = [(1,4), (2,6), (3,9)]       min flank 1  ⇒  no descent  (3 ∤ 4)
orbit(c=2, e=9) = [(0,4), (1,6), (2,9)]       reaches flank 0  ⇒  descent
```

The orbits are computed to closure under **both** shear moves, so they are exact
for that move set — note the `(1,4)` orbit also fails, which shows the obstruction
is the congruence and not the particular value `e = 2`.

This two-element orbit is, as far as this file can tell, the algebraic reason
behind the campaign's 122 842 Britton-rejected BS-donor states (C5): the shear
has nowhere to go, so no reorientation can make the `u`-syllable lengths
multiples of `M`.

**Negative that must fail — `δ = −1`.** `S_{n,−1}`'s row 1 is `x⁻¹u³x⁻¹u⁻²`,
`x`-exponent `−2`, which is not of BS shape; H1 fails outright (checked).

## (7) Why this is not the obstructed `n → n+1` induction

C17 inducts on the **flank** `|c|`, downward, inside a fixed group; it never
relates `P_n` to `P_{n±1}` and never adjoins a power-defined generator. Its
failure mode on U124 is a *congruence*, `3 ∤ 2`, decided in one line — whereas
LISITSA's obstruction needed a 1 584-homomorphism `S₄` computation. The two are
independent: C17 says the shear cannot move the flank; LISITSA says the spine
cannot move `n`.

## (8) What would falsify it

* Exhibit `(M,N,c,e)` satisfying H1–H3 where a shear step does **not** return
  `E(c∓1, ·)` as a literal free word (replay below sweeps 64 tuples; widen it).
* Exhibit a *third* shear-type move on `E(c,e)` — anything that changes `(c,e)`
  other than the two rewritings above — since the orbit computation, and hence the
  U124 negative, is only complete relative to those two.
* Show the terminal `E(0,e)` is not eliminable by C4 for some `e` (e.g. by
  exhibiting a non-primitive one-occurrence row), which would break H3's payoff.
* Weaken H3: if `M | e` alone suffices (because some intermediate state admits a
  rotation that restores divisibility), the hypothesis is too strong and the U124
  negative would have to be recomputed.

---

# C18. Coprime defining-power Bézout, and radix compression

Generalizes the existing **C9** off the AK3 root, and answers wave 2's request
"Bézout against a defining word other than `v = YXX`". C9's diagnostic was that
no cyclic conjugate of `Q`'s first relator has the shape `v^{±m}·(v`-free`)` for
the single word `v = y⁻¹x⁻²`; (6) below strengthens that to *every* `x`-free
coefficient, and extends it to `Q'` and to the C16 endpoint `S`.

## (1) Exact hypotheses

At a state of rank `r ≥ 3`:

* **H1.** One row is a **two-block power relator** `P = c₀ · xᵐ` with `c₀`
  freely reduced and **`x`-free** (`m ≠ 0`).
* **H2.** Another row is a **defining power** `t⁻¹x^k`, `k ≠ 0`, for some
  generator `t ≠ x`.
* **H3 (the criterion).** `gcd(k, m) = 1`.

H1 is what U124 lacks: see (6).

## (2) Free-group identities

The Euclid step is one AC2 by `x⁻ᵐc₀⁻¹`, up to rotation:

```
( c₀⁻ⁱ t⁻¹ x^{k−im} ) · ( x⁻ᵐ c₀⁻¹ )   ~_cyc   c₀⁻⁽ⁱ⁺¹⁾ t⁻¹ x^{k−(i+1)m}
```

verified for `m ∈ {2,3,5,7}`, `k ∈ {m+1, 2m+1, 3m+1}`, all intermediate `i`, as
cyclic words (the identity holds up to rotation, **not** literally — recorded
because comparing literal spellings here gives false failures).

After `q = ⌊(k−1)/m⌋` steps the row is the **isolator** `c₀⁻ᵠ t⁻¹ x`, which has
one `x`-letter and solves `x = t c₀ᵠ` (checked: substituting it back annihilates
the row). Necessity of H3 is a one-line Bézout argument, not a computation: the
two rows contribute `x`-coordinates `k` (from `t⁻¹xᵏ`) and `m` (from `c₀xᵐ`) to
the abelianization, so they generate `gcd(k,m)·ℤ` there and `x` is recoverable
**iff** `gcd(k,m) = 1`. The machine check (`m ≤ 8`, `k ≤ 12`) only confirms the
bookkeeping; the lattice statement is the proof.

**Dichotomy (the cost of success).** Back-substituting `x = t c₀ᵠ` into `P`
multiplies the block's length: `|c₀| + m·|t c₀ᵠ|`. So the corridor isolates `x`
only at the price of a factor-`m` blow-up unless `q = 0`. Verified as an exact
length identity for every case above.

**Radix corollary.** A displayed `xᵐ` compresses to length `O(log m)`: adjoin
`t₁,…,t_j`, `j = ⌊log₂ m⌋`, with rows `t_{i+1}⁻¹t_i²` (`t₀ = x`), and write `xᵐ`
in binary. Checked `m ∈ {1,2,3,4,5,7,8,12,15,16,31,64,100,255,1000,4096}`, and
checked on the literal `Q'` second relator: `"Yxxy" + xⁿᵟ + "Y"` becomes
`"Yxxy" + w + "Y"` with `|w| = popcount(|nδ|)`, and back-substituting
`t_i ↦ x^{2^i}` returns the literal original.

```
m = 12   : word "bc"      (len 2), 3 extra rows [Axx, Baa, Cbb],  bottom-up moves 10
m = 100  : word "bef"     (len 3), 6 extra rows,                  bottom-up moves 97
m = 1000 : word "cefghi"  (len 6), 9 extra rows,                  bottom-up moves 994
```

## (3) Expansion into AC1–AC3 + stabilization

Each `t_{i+1}` is an AC4 stabilization; converting its row to `t_{i+1}⁻¹t_i²` is
**C0**, as in C16 Gate 1. Each Euclid step and each radix contraction is one AC3
+ one AC2 by the AK3 §2 recipe. Destabilizing the `t_i` afterwards is **C0** again.

## (4) Well-founded progress measure

`ν = k mod m` for the Euclid corridor — strictly decreasing, well-founded on `ℕ`,
terminating at `gcd(k,m)`. For the radix corollary, `ν =` the number of displayed
`x`-letters, which halves each level.

## (5) Certificate growth — **the honest split**

The radix corollary compresses **presentation length** to `O(log m)` but **not the
move count**. The bottom-up chain that produces the compressed word costs
`m/2 + m/4 + ⋯ ≈ m − O(log m)` AC2 multiplications (994 for `m = 1000`, checked).
C18 therefore does **not** beat the `Θ(n)` certificate barrier; it compresses the
*state*, not the proof. No sub-linear realization is claimed, and no lower bound
is claimed either — AC2 conjugators are unbounded, so length arguments give none.
The `t_i` adjunctions are C0, hence **unbounded** on top of that.

## (6) Examples

**Positive.** `m = 3`, `k = 7`, `c₀ = y⁻¹u²` (the `x`-free coefficient of the
rewritten `Q'` relator): two Euclid steps reach the isolator `c₀⁻²t⁻¹x`, giving
`x = t c₀²`; blow-up factor `m = 3` as predicted.

**Negative that must fail.** `gcd(k,m) = d > 1`, e.g. `(k,m) = (6,4)`: the Euclid
corridor stops at `x²` and `x` is provably not recoverable — the abelianization
lattice misses `x` by index `d`. This is the same shape as AK3 Prop 4.1's
even-power abelian obstruction and must be reported as an obstruction, not a
search miss.

**U124 status: hypothesis ABSENT — exact and exhaustive.** H1 asks for a row
which, read cyclically, has exactly **one** maximal run in the power letter (that
is what "`c₀` is `x`-free" means). Census over **every** rotation and inversion of
**every** row of `Q`, `Q'`, and `S`, for `n = 2..8`, both `δ`, and for **both**
choices of power letter: **1 764 candidate spellings tested, 0 hits.**

That is an exact bounded certificate for H1 on these three spellings — not a
heap search and not a sampled census. It strengthens C9's diagnostic in two
directions: C9 ruled out the single word `v = y⁻¹x⁻²` on `Q`'s first relator,
whereas this rules out *every* `x`-free coefficient on *all* rows of all three
spellings. Concretely `Q'`'s rows are `XYxyy xᵟ Y` and `Yxxy xᵐ Y`, where the
power block is *interior*, flanked by `y` on both sides; and `S`'s rows are
`x⁻¹u³xᵟu⁻²` and `u⁻¹x⁻ᵐu⁻²xu²xᵐ`, which have two and three `x`-runs
respectively.

Adjoining `t⁻¹x^k` freshly is free (AC4 + C0) but then destabilization undoes it
and the Euclid corridor just returns `x`, so H2 must be *found*, not
manufactured. As always, a bounded miss on three spellings is not an obstruction
to other spellings in the AC orbit.

## (7) Why this is not the obstructed `n → n+1` induction

C18's induction is the Euclidean algorithm on the pair `(k, m)` at fixed `n`; `n`
enters only as the value of `m`. It never transports a relator from `G_n` to
`G_{n+1}`. Its obstruction, when it fires, is an abelian index computation, not
a finite-quotient homomorphism count.

## (8) What would falsify it

* A Euclid step that fails as a **cyclic** identity (replay sweeps `m ≤ 7`).
* A case with `gcd(k,m) = d > 1` where `x` *is* recoverable — that would refute
  the abelian necessity and is the single cheapest test of C18.
* A radix contraction chain with sub-linear move count, which would upgrade (5)
  and make C18 interesting for the `Θ(n)` barrier.
* Finding H1 somewhere in the `Q`/`S` AC-orbit after bounded moves, which would
  move the U124 status from ABSENT to live.

---

# What this file rules out, and what it redirects

1. **The cyclic complement is measured out for the new endpoint too.** Using
   `code/q_cyclic_complement.py`'s criterion (one vertex-pair identification of
   the Stallings folded core onto the rose), `S_{n,δ}` gives **0 rose hits in all
   12 cases** (`n = 2..7`, both `δ`; folded rank 2 throughout, 15–26 core
   vertices). So `S_{n,δ}` joins `Q`, `Aut(Q)`, and the `μ`-floor pairs at join
   corank `≥ 2`, and C8 does not fire on the C16 endpoint. As that file itself
   states, this only proves join corank `≥ 2` for those exact pairs — a measured
   miss, not an AC obstruction.
2. **The inverse-substitution / overgroup criterion is measured out; only the
   `Q'` enumeration is complete.** Running
   `experiments/stable_ac/ak3_inverse_substitution_overgroups.py`'s
   `enumerate_overgroups(max_states=5000)` read-only gives **0 candidates** on all
   36 pairs tried (`Q`, `Q'`, `S`; `n = 2..7`; both `δ`), with exactly two
   rank-two folded overgroups every time — the root core `⟨R₁,R₂⟩` and the full
   rose `F₂`. Completeness differs sharply, and the distinction matters:
   * `Q'`: `complete = True` for **all 12** cases (143 → 2 661 states). That is a
     completed finite certificate for this criterion on this spelling, uniform
     over the tested range.
   * `Q`: complete only for `n ≤ 4` (`δ=+1`) and `n ≤ 3` (`δ=−1`); `S`: complete
     only for `n = 2, δ=+1` (1 894 states). All other cases hit the 5 000-state
     cap, so they are **bounded reports, not certificates**, and per
     `advisor_wave1.md`/`advisor_wave2.md` no bounded negative search is an
     obstruction.
3. **`μ` cannot finish any of these endpoints.** MU_CRITERION's `μ ≤ 12` gate:
   `μ(P) = 2n+10`, `μ(Q') = n+12`, `μ(S) = 2n+13`, all `≥ 14` for `n ≥ 2`, and
   `Q'`, `P`, `S` are in three **distinct** `Aut(F₂)` orbits (complete Whitehead
   canonical forms, `n = 2..6`, both `δ`, every witness re-verified by
   substitution). `μ = 13` is never a removal, so no endpoint here is a
   μ-finish.
4. **A useful by-product for the coordinator.** The `Aut`-canonical form of
   `S_{n,δ}` is `( y⁻¹x⁻³yᵟx² , y⁻ⁿx⁻²y⁻¹x²yⁿxᵟ )` — its **first row is exactly
   the MS relator of `P_{n,δ}`**, and its second row is the `y⁻ⁿ`-conjugated tag
   `x⁻²y⁻¹x²` instead of `P`'s tag `y⁻¹x⁻¹`. So `P` and the C16 endpoint are two
   members of one **tag family** `⟨x,y | y⁻¹x⁻³yᵟx² , y⁻ⁿ C yⁿ x^ε⟩` with `C` of
   `y`-exponent `−1`. Identifying that family, and which tags `C` are
   interchangeable, looks like the right next general question — it is the
   "adjoin a word appearing in BOTH relators" mechanism in its natural coordinates.
   This uses **C1** (an ambient automorphism) and is therefore conditional and
   non-effective; the raw C16 endpoint `S_{n,δ}` is the AC-legal object.
5. **Redirect.** Given C16.1, effort spent on corridors through the `x^{nδ}`
   block on the `δ=+1` rows is effort spent inside a loop. The `δ=−1` branch is
   where C16 escapes, and its endpoint donor `x⁻¹u³x⁻¹u⁻²` (`x`-exponent `−2`,
   not HNN) is a genuinely new state class for this campaign.

---

# Replay

Self-contained, read-only, no repo file modified. Depends on
`experiments/equivalence_classes/lib/autcanon.py` for (C) only.

```python
# (A) C16 identities + C16.1 loop, and (B) C17 shear orbits.
import sys; sys.path.insert(0, "/workspace")

def fr(w):
    o = []
    for c in w:
        if o and o[-1] == c.swapcase(): o.pop()
        else: o.append(c)
    return "".join(o)
def rinv(w): return w[::-1].swapcase()
def cyc(w):
    w = fr(w)
    while len(w) >= 2 and w[0] == w[-1].swapcase(): w = fr(w[1:-1])
    return w
def same_cyc(a, b):
    a, b = cyc(a), cyc(b)
    return b in {a[i:] + a[:i] for i in range(len(a))}
def pw(l, k): return l * k if k >= 0 else l.swapcase() * (-k)
def sub(w, im):
    o = []
    for c in w:
        g = im.get(c.lower())
        o.append(c if g is None else (g if c.islower() else rinv(g)))
    return fr("".join(o))

XI = "Yxy"
def Qp(n, d): return (fr("XYxyy" + pw("x", d) + "Y"), fr("Yxxy" + pw("x", n * d) + "Y"))
def P(n, d):  return (fr("Y" + "XXX" + pw("y", d) + "xx"),
                      fr(pw("y", -(n + 1)) + "X" + pw("y", n) + "x"))

def magnus(w):
    """Magnus decomposition: [(index i, exponent e) for xi_i blocks], total y-exponent."""
    h, blocks = 0, []
    for c in w:
        if c in "yY":
            h += 1 if c == "y" else -1
        else:
            e = 1 if c == "x" else -1
            if blocks and blocks[-1][0] == -h: blocks[-1] = (-h, blocks[-1][1] + e)
            else: blocks.append((-h, e))
    return [b for b in blocks if b[1] != 0], h
def rebuild(blocks, tot):
    return fr("".join(pw("y", -i) + pw("x", e) + pw("y", i) for i, e in blocks) + pw("y", tot))

for d in (1, -1):
    for n in range(2, 8):
        m = n * d
        R, S = Qp(n, d)
        bR, hR = magnus(R); bS, hS = magnus(S)          # hypotheses H2, H3
        assert rebuild(bR, hR) == R and rebuild(bS, hS) == S
        assert bR == [(0, -1), (1, 1), (-1, d)] and hR == 0
        assert bS == [(1, 2), (0, m)] and hS == -1
        I_R = fr("X" + "u" + "y" + pw("x", d) + "Y")     # gate 1
        I_S = fr("uu" + pw("x", m) + "Y")
        D   = fr("U" + XI)
        assert sub(I_R, {"u": XI}) == R and sub(I_S, {"u": XI}) == S   # faithful
        assert sum(c in "yY" for c in I_S) == 1                       # isolator
        e = fr("uu" + pw("x", m))                                     # gate 2
        A_, B_ = sub(I_R, {"y": e}), sub(D, {"y": e})
        assert A_ == fr("X" + "uuu" + pw("x", d) + "UU")
        assert B_ == fr("U" + pw("x", -m) + "UU" + "x" + "uu" + pw("x", m))
        assert sub(I_R, {"y": fr("uu" + pw("x", m + 11))}) == A_      # c-free row 1
        rho = fr("X" + pw("u", -3) + "x" + "uu")                      # C16.1
        legal = same_cyc(rho, rinv(A_))
        assert legal == (d == 1), (n, d)
        if legal:
            out = fr(B_ + rinv(fr(pw("x", -m) + rho + pw("x", m))))
            assert out == fr("U" + pw("x", -n) + "u" + pw("x", n + 1))
            Pr = (sub(P(n, 1)[0], {"x": "u", "y": "x"}),
                  sub(P(n, 1)[1], {"x": "u", "y": "x"}))
            assert same_cyc(A_, rinv(Pr[0])) and same_cyc(out, rinv(Pr[1]))   # LOOP

def E(c, e): return fr("U" + pw("x", -c) + pw("u", -e) + "x" + pw("u", e) + pw("x", c))
def orbit(c0, e0, M, N, cap=4000):
    seen, st = set(), [(c0, e0)]
    while st and len(seen) < cap:
        s = st.pop()
        if s in seen: continue
        seen.add(s); c, e = s
        if e % M == 0: st.append((c - 1, N * e // M))
        if e % N == 0: st.append((c + 1, M * e // N))
    return sorted(seen)
assert orbit(7, 2, 3, 2) == [(7, 2), (8, 3)]            # U124: flank never drops
assert orbit(1, 4, 3, 2) == [(1, 4), (2, 6), (3, 9)]     # 3 does not divide 4
assert orbit(2, 9, 3, 2) == [(0, 4), (1, 6), (2, 9)]     # positive example
assert orbit(1, 3, 3, 2) == [(0, 2), (1, 3)]             # smallest positive case
def shear_down(c, e, M, N):
    assert e % M == 0
    f = N * e // M
    return fr("U" + pw("x", -c) + rinv("x" + pw("u", f) + "X")
              + "x" + "x" + pw("u", f) + "X" + pw("x", c)), (c - 1, f)
w, st = shear_down(2, 9, 3, 2);  assert w == E(*st) == E(1, 6)
w, st = shear_down(*st, 3, 2);   assert w == E(*st) == E(0, 4)
assert sum(ch in "xX" for ch in E(0, 4)) == 1 and E(0, 4) == "UUUUUxuuuu"
print("C16 + C16.1 + C17 identities OK")

# (B2) C18: Euclid chain (cyclic), radix compression, and the exact H1 census.
import re
from math import gcd
def cyc_w(w):
    w = fr(w)
    while len(w) >= 2 and w[0] == w[-1].swapcase(): w = fr(w[1:-1])
    return w
def rots(w): return [w[i:] + w[:i] for i in range(len(w))]
def same_cyc2(a, b):
    a, b = cyc_w(a), cyc_w(b)
    return b in rots(a)
def pw2(word, k): return word * k if k >= 0 else rinv(word) * (-k)

C0 = "Yuu"                                          # an x-free coefficient
for m in (2, 3, 5, 7):
    for k in (m + 1, 2 * m + 1, 3 * m + 1):
        q, word = (k - 1) // m, fr("T" + pw("x", k))
        for i in range(q):                          # Euclid: one AC2 by x^-m c0^-1
            word = cyc_w(fr(word + pw("x", -m) + rinv(C0)))
            want = cyc_w(fr(pw2(rinv(C0), i + 1) + "T" + pw("x", k - (i + 1) * m)))
            assert same_cyc2(word, want), (m, k, i, word, want)
            word = want
        assert sum(ch in "xX" for ch in word) == 1   # isolator
        assert same_cyc2(word, fr(pw2(rinv(C0), q) + "T" + "x"))
        assert fr(sub(fr(pw2(rinv(C0), q) + "Tx"), {"x": fr("t" + pw2(C0, q))})) == ""

LET = "xabcdefghijklmnopqrstuvw"                     # t_0 = x, t_1 = a, ...
for m in (1, 2, 3, 4, 5, 7, 8, 12, 15, 16, 31, 64, 100, 255, 1000, 4096):
    bits, r = [], m
    while r: bits.append(r & 1); r >>= 1
    j = len(bits) - 1
    word = "".join(LET[i] for i, b in enumerate(bits) if b)
    defs = [LET[i + 1].upper() + LET[i] * 2 for i in range(j)]
    images = {LET[i]: pw("x", 2 ** i) for i in range(j + 1)}
    assert sub(word, images) == pw("x", m) and all(sub(d, images) == "" for d in defs)
    assert len(word) <= j + 1 and len(defs) == j     # length O(log m), j extra rows
    moves, cur = 0, m
    while cur >= 2: moves += cur // 2; cur //= 2     # ... but Theta(m) moves
    assert m - moves <= m.bit_length() + 1

def runs(w, g): return len(re.findall(f"[{g}{g.upper()}]+", w))
def Qraw(n, d):
    xd = "x" if d == 1 else "X"
    return ("XYxyxxy" + xd + "YXX", "Yxxy" + xd * n + "YXX")
def S2(n, d):
    m = n * d
    return (fr("X" + "uuu" + pw("x", d) + "UU"),
            fr("U" + pw("x", -m) + "UU" + "x" + "uu" + pw("x", m)))
tested = hits = 0
for name, f, gens in (("Q", Qraw, "xy"), ("Qp", Qp, "xy"), ("S", S2, "xu")):
    for d in (1, -1):
        for n in range(2, 9):
            for row in f(n, d):
                w = cyc_w(row)
                for cand in rots(w) + rots(rinv(w)):
                    tested += 1
                    for g in gens:                   # H1: exactly one run, at the end
                        if runs(cand, g) == 1 and re.search(f"[{g}{g.upper()}]+$", cand):
                            hits += 1
assert (tested, hits) == (1764, 0), (tested, hits)
print("C18 Euclid + radix identities OK; H1 census 1764 spellings, 0 hits")

# (C) mu values and orbit separation (this part is Aut, i.e. C1 -- not AC moves)
from experiments.equivalence_classes.lib.autcanon import aut_canon, check
def Su(n, d):
    m = n * d
    return (fr("X" + "yyy" + pw("x", d) + "YY"),
            fr("Y" + pw("x", -m) + "YY" + "x" + "yy" + pw("x", m)))
for d in (1, -1):
    for n in range(2, 7):
        for lbl, pr, want in (("P", P(n, d), 2 * n + 10), ("Qp", Qp(n, d), n + 12),
                              ("S", Su(n, d), 2 * n + 13)):
            t, rep, phi = aut_canon(pr)
            assert t == want and check(pr, rep, phi), (lbl, n, d, t, want)
        assert len({aut_canon(P(n, d))[1][0] + "|" + aut_canon(P(n, d))[1][1],
                    aut_canon(Qp(n, d))[1][0] + "|" + aut_canon(Qp(n, d))[1][1],
                    aut_canon(Su(n, d))[1][0] + "|" + aut_canon(Su(n, d))[1][1]}) == 3
print("mu(P)=2n+10, mu(Q')=n+12, mu(S)=2n+13, three distinct Aut orbits OK")
```
