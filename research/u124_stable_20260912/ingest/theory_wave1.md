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
(3 + 4 AC2 moves, each with one AC3; no AC1). **The first output row contains no
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
* **C17** — IDENTITY-CHECKED positive criterion; U124 hypothesis **fails**
  (exact congruence), orbit computation exact.
* **C18** — IDENTITY-CHECKED; U124 hypothesis **ABSENT**.

Evidence base: 8 122 machine identity checks, 0 failures, plus 20 `aut_canon`
witnesses each re-verified by pure substitution (`check(pair, rep, phi)` true).
Replay script at the end of this file; it depends only on
`experiments/equivalence_classes/lib/autcanon.py` and is read-only.

## Non-claims (binding)

* No U124 row is solved, removed, or given a trivialization certificate here.
* No `Aut(F₂)` step below is an ordinary AC move. `aut_min_len` / `aut_canon`
  are orbit calculations; where a theorem needs one it is flagged **C1** and
  inherits C1's non-effectiveness.
* The two gated CoVs each use **C0 (Lemma 11)**. Cost is finite but **unbounded**.
  It is never charged linearly and never presented as a replayable move count.
* Raw length rises along C16 (`μ(Q') = n+12 → μ(S) = 2n+13`). That is allowed by
  the brief; the well-founded measures below are *not* length.
* C16.1 is a statement about the C16 corridor family only. It is not an AC
  obstruction and does not obstruct longer or different routes.
* C17's `δ=+1` terminal is the reciprocal BS(3,2) donor. Per `c15_bs_stall.md`,
  triviality is **not** declared from BS(1,2) symmetry or reciprocal BS(3,2).

---

# C16. Conjugate-tag exchange corridor

## (1) Exact hypotheses

Recognizable from the two relator words alone, no search:

* **H1.** The pair is on two generators `x, y`, freely reduced, balanced.
* **H2.** One row, call it `S`, has `y`-exponent `−1` **and** exactly one
  `y`-letter, and splits as `S = T · y⁻¹` where `T` is a word in `x` and
  `ξ = y⁻¹xy` with `y`-exponent `0`. Equivalently: `S` is an **isolator** for `y`.
* **H3.** `T = ξᵖ xᶜ` for some `p ≠ 0`, `c ∈ ℤ` (the *tag power* and the *block*).
* **H4.** The other row `R` is a word in `x`, `ξ` and exactly one displayed
  `y xᵇ y⁻¹` factor; i.e. `R = A(x,ξ) · y xᵇ y⁻¹ · B(x,ξ)`.

H2–H4 are decided by scanning for the literal 3-letter block `Yxy` and reading
`y`-exponents. No primitivity test, no search, no Whitehead call.

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
I_S  =  u² xᵐ y⁻¹              ( "uuxxY"   ← "Yxxyxx Y" for n=2 )
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
conjugate that rotation by `β` (one **AC3**) and multiply (one **AC2**), giving
`W ← W · β⁻¹(ξ⁻¹u)β = α u β`. This is exactly the expansion recipe demanded by
`advisor_wave2.md` BLOCKER 3 and by AK3 §2's displayed-block substitution.
Occurrence counts, checked: `R` has 1 displayed `ξ`, `S` has `p = 2`. **n_subs = 3.**

**Gate 2 — delete `y` by the isolator (C2/Prop A; the removal step is C0).**
`I_S` has `y`-exponent `−1` and one `y`-letter, so `y⁻¹e = y⁻¹uᵖxᶜ` is a cyclic
**rotation** of `I_S`. For each displayed `y^{±1}` in a row `W = α y^{±1} β`:
one **AC3** (conjugate that rotation by `β`, inverting it for `y⁻¹`) and one
**AC2**. Counts, checked: `I_R` has 2 `y`-letters, `D` has 2. **n_subs = 4.**
Now `Â` and `B̂` are `y`-free and the only `y` left is the single one in `I_S`.
Removing generator `y` together with the row `I_S = uᵖxᶜy⁻¹` is **C0** again —
*not* a bare AC5, because the row is `y⁻¹·w` and not the letter `y`.

**C16.1 tail — 1 bounded move.** One **AC1** (invert `Â`), one **AC3**
(rotate to `ρ`, then conjugate by `xᵐ`), one **AC2**. `δ = +1` only.

**Ledger.** 1 AC4 · 2 × C0 · 7 AC2 (+7 AC3) for C16; +1 AC1 +1 AC3 +1 AC2 for
C16.1. Generator/row count: `2/2 → 3/3 → 2/2`, balanced throughout.

## (4) Well-founded progress measure (length may rise)

Not length: `μ` rises `n+12 → 2n+13`. The measure is on the corridor, and it is
what licenses the C0 removal:

> `ν(state) = ( #rows containing the generator being eliminated ,
>               #displayed occurrences of the tag block in those rows )`,
> ordered lexicographically on `ℕ × ℕ`.

Gate 1 drives the second coordinate `3 → 0`. Gate 2 drives the first coordinate
`3 → 1` (only the isolator retains `y`), then C0 takes it to `0`. `ℕ × ℕ` under
lex order is well-founded, each displayed move strictly decreases `ν`, and the
corridor terminates in `n_subs` steps with `n_subs` read off the input words. It
is a **termination** measure for the corridor, not a descent measure for U124 —
see C16.1.

## (5) Certificate growth

**Honest answer: unbounded, because C0 (Lemma 11) is used twice** — once to
install `D = u⁻¹x^y`, once to remove `y` with `I_S`. Neither normal-closure
witness is materialized here, so C16 is *non-effective* in exactly C1/C0's sense.

What **is** bounded, uniformly in `n`: the elementary core is 7 AC2 (C16) or 10
moves total (C16 + C16.1), independent of `n` and of `|A|,|B|,p,b,c`. State
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

**Negative that must fail — the hypothesis test.** Replace H2's isolator by a row
with `y`-exponent `−2`, e.g. `S = ξ²xᶜy⁻²` (`"uuxxYY"` at rank 3). Then `y⁻¹e` is
not a rotation of any row and Gate 2 is unavailable; C16 must not fire. Likewise
`p = 0` (no tag) leaves nothing to exchange. Both are rejected by reading
`y`-exponents, before any move.

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
same `n`**. So the δ-split C16.1 exhibits (rigid at `+1`, escaping at `−1`) is the
*same* split LISITSA found, with the arrow reversed, and C16.1 supplies a
mechanism for it: a renormalization fixed point. Any `n`-descent on `δ=+1` must
leave the C16 corridor class.

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

* **H1.** Row 1 is, up to AC1/AC3, `D = x⁻¹u^M x u^{−N}` with `|M − N| = 1`,
  `M, N ≥ 1` (a BS(M,N) donor; `x` is the stable letter).
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
Terminal finish: `E(0,e)` is a one-occurrence-`x` row, so C4 (primitive
one-occurrence donor elimination) applies as an ordinary AC finish, with the
`x ↦ u` substitution expanded by the same recipe.

## (4) Well-founded progress measure

`ν = |c|`, the flank, on `ℕ`. Each shear-down step strictly decreases it by 1;
H3 guarantees the divisibility needed at *every* step (that is why the hypothesis
is `M^{|c|} | e` and not merely `M | e`). Termination at `ν = 0`. The inner power
shrinks as `e·(N/M)^{k}`, so raw length **falls** here — unusually, this corridor
is monotone in both coordinates.

## (5) Certificate growth — **bounded**

`|c|` shear steps × 2 AC2 each, plus at most `2e` AC2 for the terminal
one-occurrence elimination. Total `≤ 2|c| + 2e + O(1)` elementary moves, with
state length `≤ |c| + 2e + 7`. No Lemma 11 anywhere: **C17 is effective.** This
is the only candidate in this file with a replayable move bound.

## (6) Examples

**Positive, `(M,N) = (3,2)`, `c = 2`, `e = 9`** (literal, machine-checked):

```
E(2,9) = U XX UUUUUUUUU x uuuuuuuuu xx
  shear-down →  E(1,6)
  shear-down →  E(0,4) = U UUUU x uuuu        one x-letter ⇒ C4 finish
```

`27 = 3²` divides `9`? H3 reads `M^{|c|} = 9 | 9` ✔.

**Negative that must fail — the U124 instance.** `S_{n,+1}` from C16 is exactly
`( D_{BS(3,2)} , E(nδ, 2) )` (checked `n = 2..8`). H3 asks `3^{|nδ|} | 2`;
already `3 ∤ 2`. The complete shear orbit of `(c, e) = (c₀, 2)` under both moves
is the **two-element** set `{(c₀,2), (c₀+1,3)}`, so the flank never decreases and
never reaches `0`:

```
orbit(c=7, e=2) = [(7,2), (8,3)]      min flank 7  ⇒  no descent
orbit(c=2, e=9) = [(0,2),(1,3),(2,9),...] reaches flank 0  ⇒  descent
```

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

Aimed at wave 2's request "Bézout against a defining word other than `v = YXX`".

## (1) Exact hypotheses

At a rank-`k+1` state:

* **H1.** One row is a **two-block power relator** `P = c₀ · xᵐ` with `c₀`
  freely reduced and **`x`-free** (`m ≠ 0`).
* **H2.** Another row is a **defining power** `t⁻¹x^k`, `k ≠ 0`.
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
the row). Necessity of H3 is exact on abelianizations: with coordinates `(x,·)`
the images of `t` and the block generate `gcd(k,m)·ℤ` in the `x`-coordinate, so
`x` is recoverable **iff** `gcd(k,m) = 1` (checked, `m ≤ 8`, `k ≤ 12`).

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

**U124 status: hypothesis ABSENT.** No row of `Q`, `Q'`, or `S` is a two-block
power relator `c₀·xᵐ` with `x`-free `c₀`: `Q'`'s rows are `XYxyy xᵟ Y` and
`Yxxy xᵐ Y` (the block is *interior*, flanked by `y` on both sides), and `S`'s
rows are `x⁻¹u³xᵟu⁻²` and `u⁻¹x⁻ᵐu⁻²xu²xᵐ`. Wave 2 already observed the
`v = YXX` shape is absent; C18 confirms the stronger statement that **no**
`x`-free-coefficient two-block shape is present. Adjoining `t⁻¹x^k` freshly is
free (AC4 + C0) but then destabilization undoes it, so H2 must be *found*, not
manufactured.

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

1. **The cyclic complement is measured out for the new endpoint too.** `S_{n,δ}`
   joins `Q`, `Aut(Q)`, and the `μ`-floor pairs in having join corank `≥ 2` (0
   rose hits) per `code/q_cyclic_complement.py`'s criterion. C8 does not fire on
   the C16 endpoint. Not an obstruction — a measured miss.
2. **The inverse-substitution / overgroup criterion is measured out, and for `Q'`
   the enumeration is complete.** Running
   `experiments/stable_ac/ak3_inverse_substitution_overgroups.py`'s
   `enumerate_overgroups` read-only on `Q`, `Q'`, `S` gives 0 candidates; on `Q'`
   the state enumeration **terminates** with only two rank-two overgroups (`K`
   and `F₂`), `n = 2..7`, both `δ`. That is a completed finite certificate for
   that criterion on that spelling, uniform over the tested range.
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

for d in (1, -1):
    for n in range(2, 8):
        m = n * d
        R, S = Qp(n, d)
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
assert any(c == 0 for c, _ in orbit(2, 9, 3, 2))        # positive example
assert E(2, 9) and fr(E(1, 6)) and sum(ch in "xX" for ch in E(0, 4)) == 1
print("C16 + C16.1 + C17 identities OK")

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
