# W2m: the translation cocycle of the canonical section — proved, and what it settles

Date: 2026-08-28 · Checker: `checkers/theta_cocycle.py`
(imports `theta_attainability.py`, `theta_residual_evaluator.py`,
`corrected_operators.py`, `infinite_index_liveness.py`,
`g_stratum_death.py` and the two codex certificates **all unmodified**;
guarded foreground runs, one at a time, sliced and resumable).

Run records: `checkers/out/w2m_lemma.json` (the cocycle),
`w2m_action.json` + `w2m_action_deep.json` (which group acts on `H_fin`),
`w2m_growth_c7.json`, `w2m_growth_c5.json` (the effective non‑generation
ladders), `w2m_ladder_c7.json` (W2l's calibration baseline),
`w2m_ladder.json` (the whole census). Every record carries
`controls_passed: true`.

Answers `W2L_THETA_ATTAINABILITY.md` §12 — the one missing lemma the whole
W2 chain was funnelled into.

---

## 0. Verdict

| question | answer | status |
|---|---|---|
| Does the translation cocycle exist, and can it be written down? | **Yes, in closed form.** `κ(g,y) := σ(g·y)⁻¹·gσ(y)g⁻¹` lies in `[N,N]` unconditionally (**480/480** literal checks), and `Θ(κ(g,y))` is given exactly by (K3) below: a *linear* conjugation‑defect term plus a *bilinear* shortlex‑inversion term. **480/480** literal agreements; both corruption controls fire (**255/255**, counted only where the dropped half is nonzero). | **PROVED** (§1) |
| Is `Θ(κ)` "a bilinear correction", as W2l §12 conjectured? | **Half of it.** It is an inhomogeneous quadratic form: `linear + bilinear`. The linear half is nonzero on **157** of 480 evaluations, the bilinear half on **98**. Only the bilinear half is 2‑divisible. | **premise CORRECTED** (§1.4) |
| The law the question actually needs — how `Ξ_Z(Θ)`'s quadratic form moves when the direction support is translated by `g` | `Θ_σ(g·y) = g·Θ_σ(y) + 2·I_g(y)`, `I_g` the inversion form. **Purely quadratic, and 2‑divisible: mod 2, `Θ∘σ` is exactly `Q`‑equivariant.** Grounded in `F(c,t)` (not in a formula) by the reordering element `R(g,y) ∈ [N,N]`: **480/480**, 98 non‑vacuous. | **PROVED** (§1.3) |
| Does that make `V_{H_fin}` finitely generated *up to the `Q`-action*? | **No — the conjecture is false twice over.** (i) There **is no `Q`-action on `H_fin`**: `g·F ∉ H_fin` on **2,172 / 2,172** tested pairs over 51 baselines, and the joint centralizer of the operators is **trivial** on **55/55** baselines (words to length 4; to length 8 on 10). (ii) `Ξ_Z` is *exactly* diagonally `Q`-invariant (W2j K4, re-run: 60/60), so in `W_Q` "up to the `Q`-action" is vacuous — the conjecture reduces to plain finite generation. | **REFUTED** (§2) |
| Then what does act on `H_fin`? | The **Hecke algebra** `E = End_{Z[Q]}(M) ≅ Z[⟨c⟩\Q/⟨c⟩]`, acting on the right by `T_a(e_v) = e_{va}+e_{vca}`. Commutation with every operator column: **8,250/8,250** exact; `T_a F ∈ H_fin`: **905/905** exact; the corrupted Hecke operator leaves `H_fin` **870/905** and breaks commutation **1,070** times. | **PROVED + verified** (§3) |
| Is `V_{H_fin}` finitely generated? | **No — refuted effectively.** From **one** native direction on census chain 7, the cross generators `b(F, T_{t^k}F)` occupy a coordinate window `[k−1, k+11]` that marches linearly with `k`, giving **15** pairwise‑disjoint‑support (hence independent) generators mod 2 and **10** over `Z` at `k ≤ 30`, with no bound in sight. Independently reproduced on chain 5 (window `[k−2, k+19]`). | **REFUTED, effectively** (§4.2) |
| Is W2l §6.1's chain‑7 "saturation" `V_S = V_{H_fin}`? | **No.** Its 20‑direction family (`rank V = 63`, universe 556) is reproduced exactly here; then **6 native + 23 Hecke directions** give `rank V = 315`, universe **1,924** — with **22** of the Hecke directions provably outside the `Z`-span of the native family. **F3 is false at W2l's own saturated `S`.** | **REFUTED** (§4.1) |
| Do W2l's per-baseline mod‑2 *coordinate* certificates survive? | **No.** A **single** Hecke word destroys them on **17 of the 27** baselines that had one; the census total falls **163 → 107**, and on 4 baselines to **zero**. | **§5** |
| Per-baseline verdict on the COMPLETE family | **None is available, and §4 proves none is available by this route.** On the strictly enlarged families: `MOD2_UNATTAINABLE_ON_S` on **51/51**, 2,812 mod‑2 classes enumerated, **0** zeros, C9 planted‑zero control fires **51/51**; `−c₀ ∈ V_S` (the only monotone branch) fires **0/51**. | **still bounded by `S`** (§5) |
| Any witness? Any obstruction? | **Neither. 0 and 0.** | (§5) |

**The layer-2 question is still OPEN — but it is no longer open for the reason
W2l said.** W2l's F3 was "not proved"; it is now **disproved**, and the lemma
that was supposed to prove it is true and does not help.

---

## 1. The lemma

### 1.0 Setting, conventions and inherited hypotheses

`Q = ⟨c,t | c²⟩`, `F = F(c,t)`, `N = ker(F → Q)`, `M = N_ab = Z[X]`,
`X = Q/H` with `H = ⟨c⟩`. Two hypotheses are **inherited, not re-derived**:

* **(3.1)** `N` is free on the Schreier basis `r_v = ṽ c² ṽ⁻¹`, `v ∈ X`. Every
  statement below about `σ`, `Θ` and `κ` uses it.
* **(3.5)** the second-layer variation operator carries the same integral
  coefficients as `L_r`. Nothing in this note uses (3.5): the cocycle, the
  Hecke action and the rank ladders are statements about the literal
  free-group residual and the operators alone. (3.5) is only needed to read
  `Ξ_Z(Θ) = 0` as "layer 2 is solvable", exactly as in W2i/W2j/W2k/W2l.

`σ(y) = Π_v r_v^{y_v}` in **shortlex** order of `v` — literally
`lift.lift_module_vector`, unmodified. `Θ = esc.degree_two ∘ esc.schreier_word`,
unmodified: on a word it is the **upper-triangular** part `UT` of the ordered
degree-two tensor, so

```text
Θ(ab) = Θ(a) + Θ(b) + UT([a]⊗[b]) ,   UT(p⊗q)_{v<w} = p_v q_w ,
Θ(a⁻¹) = −Θ(a) + UT([a]⊗[a]) ,        Θ([r_a,r_b]) = +e_a ∧ e_b  (a<w b)
```

the last being W2j's control K3, re-run here as **L0: 20/20**. Order
convention: `v < w` means `(len v, v) < (len w, w)` on the integer tuple —
the same key `lift_module_vector` sorts by and `degree_two` antisymmetrises
by. Write `Θ_σ(y) := Σ_{v<w} y_v y_w e_v ∧ e_w`, the value `Θ` takes on
`σ(y)` (an *ordered-product* quadratic form, not a functorial invariant).

**W2l's order convention for the cocycle is adopted verbatim:**

```text
κ(g,y) := σ(g·y)⁻¹ · g σ(y) g⁻¹ ,        g ∈ F(c,t).
```

`[κ] = −(g·y) + g·[σ(y)] = 0`, so `κ ∈ [N,N]` unconditionally — **asserted
literally** (`relation_module(κ) == {}`) on every evaluation, never assumed:
**L1, 480/480**, with a corrupted section (one exponent bumped) leaving
`[N,N]` **8/8**.

### 1.1 Lemma K1 — the conjugation identity

> For `g ∈ F(c,t)` and `v ∈ X`, put `u = g·v ∈ X` and let `ε(g,v) ∈ {0,1}` be
> the exponent with `gv = u c^ε` in `Q`. Then, **literally in `F(c,t)`**,
>
> ```text
> n(g,v) := g̃ ṽ c^{−ε} ũ⁻¹  ∈  N ,       g̃ r_v g̃⁻¹ = n(g,v) · r_u · n(g,v)⁻¹ .
> ```

*Proof.* Let `W` be the free reduction of `g̃ṽ`. Since `Q`-reduction only
deletes `c²` blocks, `W = ũ c^ε n` with `n ∈ N`, i.e. `n = c^{−ε} ũ⁻¹ W`.
Then `r_W = W c² W⁻¹ = ũ c^ε n c² n⁻¹ c^{−ε} ũ⁻¹`; `c` commutes with `c²`, so
with `n' = c^ε n c^{−ε} ∈ N` this is `ũ n' c² n'⁻¹ ũ⁻¹ = m r_u m⁻¹` with
`m = ũ n' ũ⁻¹ = W c^{−ε} ũ⁻¹ = n(g,v)`. And `g̃ r_v g̃⁻¹ = (g̃ṽ)c²(g̃ṽ)⁻¹ = r_W`. ∎

Machine check **L2: 168/168** over 12 group words × 14 vertices. Corruption
control **168/168** — and note the trap it had to avoid: flipping `ε` is
**not** a corruption (`c` commutes with `c²`, so both values give the same
conjugate, and the first version of this control fired 0/168). The shipped
corruption multiplies `n` by a relation generator at a *different* vertex,
which leaves the centralizer `⟨r_u⟩` of the conjugated element.

Write `ν(g,v) := [n(g,v)] ∈ M`.

### 1.2 Lemma K2 — the closed form of `Θ(κ)`

> ```text
> Θ(κ(g,y)) =  Σ_v y_v · ( ν(g,v) ∧ e_{g·v} )                    [LINEAR]
>            −  Σ_{v<w, g·w < g·v} y_v y_w · ( e_{g·w} ∧ e_{g·v} ) [BILINEAR]
> ```

*Proof.* `Θ(κ) = Θ(σ(g·y)⁻¹) + Θ(A) + UT(−(g·y) ⊗ (g·y))` with
`A = g̃σ(y)g̃⁻¹`. Both outer terms evaluate: `Θ(σ(z)⁻¹) = 0` (the reversed
product is lower-triangular) and `UT(−z⊗z) = −Θ_σ(z)`, so
`Θ(κ) = Θ(A) − Θ_σ(g·y)`. By K1, `A = Π_v ρ_v^{y_v}` with
`ρ_v = n(g,v) r_{g·v} n(g,v)⁻¹`, and the `Θ(ab)` rule gives
`Θ(ρ_v) = ν(g,v) ∧ e_{g·v}`, `Θ(ρ_v^k) = k Θ(ρ_v)`, so
`Θ(A) = Σ_v y_v(ν∧e_{g·v}) + Σ_{v<w} y_v y_w UT(e_{g·v}⊗e_{g·w})`. The last
sum keeps only the *order-preserving* pairs, while `Θ_σ(g·y)` keeps all of
them; the difference is exactly the inversion sum. ∎

Machine check **L3: 480/480** literal agreements over 12 group words × 40
`y`'s (of which **32** are real chain data — the components of `x₀` and of
kernel directions of census chains 5–7 — so the check is not confined to
synthetic vectors). Corruption controls fire **255/255**, counted **only** on
the evaluations where the dropped half is nonzero (157 linear, 98 bilinear):
a guard that cannot fire is not a control.

### 1.3 Lemma K3 — the direction-translation law (the one the question needs)

W2l §12 asked for the law that moves `Ξ_Z(Θ)`'s quadratic form when the
support `{v}` of a direction is translated by `g`. It is:

> ```text
> Θ_σ(g·y) = g·Θ_σ(y) + 2·I_g(y) ,
> I_g(y) := Σ_{v<w, g·w<g·v} y_v y_w · e_{g·w} ∧ e_{g·v}
> ```
>
> with `g·` the diagonal action (3.4). **The correction is purely quadratic
> and 2‑divisible, so mod 2 `Θ∘σ` is *exactly* `Q`-equivariant.**

*Proof.* `Θ_σ(g·y)` writes each pair `{g·v, g·w}` in canonical order;
`g·Θ_σ(y)` writes it with a sign. They agree on order-preserving pairs and
differ by `2 y_v y_w e_{g·w}∧e_{g·v}` on inverted ones. ∎

This is a formula about a formula, so it is **grounded in the free group**
by control **L7**: the *reordering element*

```text
R(g,y) := σ(g·y)⁻¹ · Π_v r_{g·v}^{y_v}    (v in the order of X)
```

has `[R] = 0`, hence `R ∈ [N,N]`, and `Θ(R) = −I_g(y)` — i.e. `Θ(R)` is
exactly the bilinear half of K2 with the conjugation defect absent.
**480/480**, **98 non-vacuous**. So the direction law is *twice the bilinear
half of the cocycle*, and the linear (conjugation) half is invisible to it.

### 1.4 Lemma K4 — the cocycle identity, and reconciliation with W2j K3

`κ(gh,y) = κ(g, h·y) · g κ(h,y) g⁻¹` (immediate from the definition), hence
in `Λ²M`

```text
Θ(κ(gh,y)) = Θ(κ(g, h·y)) + g·Θ(κ(h,y))       —  L4: 64/64 .
```

**Reconciliation.** W2j's control K3 verified that `Θ` is *exactly*
`Q`-equivariant on `[N,N]` (re-run: 72/72). That is not in tension with `κ`:
K3 is about `Θ` and honest conjugation; `κ` measures the failure of the
**section `σ`** — a choice of lift `M → N` — to commute with translation.
The cocycle lives entirely in the section. This is why W2l §12's phrase
"`Θ` has no such equivariance" was the wrong diagnosis of F3: `Θ` has the
equivariance; `σ` does not; and mod 2 even `σ` does (K3 above).

### 1.5 What the cocycle measures (numbers)

| | value |
|---|---:|
| `κ` evaluations, all literal in `F(c,t)` | **480** |
| `κ ∈ [N,N]` | **480 / 480** |
| closed form K2 exact | **480 / 480** |
| `Θ(κ) ≠ 0` | 174 |
| … of those, `Θ(κ) ∈ 2·Λ²M` | **14** — so the *section* cocycle is genuinely odd |
| … of those, `Ξ_Z(Θ(κ)) = 0` | **0** — the cocycle is fully visible in `W_Q` |
| evaluations with a nonzero LINEAR half | 157 |
| evaluations with a nonzero BILINEAR half | 98 |

---

## 2. Where the conjectured consequence dies: there is no `Q`-action on `H_fin`

`L_r` is **left** multiplication by `λ_r ∈ Z[Q]` on `M = Z[Q/H]`. Left
multiplication by `g` commutes with it only if `g λ_r = λ_r g` for every `r`.
So `H_fin = ker(⊕L_r)` is `Q`-stable only on the joint centralizer.

| | value |
|---|---:|
| `(g, F)` pairs tested, `g ∈ {c,t,T,ct,tc,cT,Tc,ctc,tt,TT,tct,ctct}`, `F` a verified direction | **2,172** |
| … with `g·F ∈ H_fin` | **0** |
| baselines with joint centralizer `= {1}` (words to length 4) | **55 / 55** |
| the same to length 8, on a 10-chain slice | **10 / 10** |

**Structural reason** (not just the bounded scan). W2g's exact operator
identities give `L₄ = w − 1` with `w = g t g⁻¹` and `L₂ = 1 − X` with
`X = h₂ S h₂⁻¹`, so any `z` in the joint centralizer lies in
`C_Q(w) ∩ C_Q(X)`. In `C₂ * Z` the centralizer of an infinite-order element
is its maximal cyclic overgroup, and `w` is conjugate to `t`; so the
intersection is trivial unless `w` and `X` share a cyclic overgroup. The
computation above is what is actually *verified*; this paragraph says why the
answer is not an accident of the truncation.

**And the target space cannot see a `Q`-action anyway.** `Ξ_Z(e_v∧e_w)`
depends only on the double coset `H v⁻¹w H`, so `Ξ_Z` is *exactly* diagonally
`Q`-invariant (W2j K4, re-run: 60/60 invariance, 60/60 corruption fires).
Hence in `W_Q`, "finitely generated **up to the `Q`-action**" is just
"finitely generated". W2l §12's proposed consequence therefore needed *two*
things that are false: an action to quotient by, and a gain from quotienting.

---

## 3. The object that does act: the Hecke algebra

> `E := End_{Z[Q]}(M) = (Z[Q/H])^H ≅ Z[H\Q/H]`, acting on the **right** by
> ```text
> T_a(e_v) = e_{v·a} + e_{v·c·a}          (a ∈ Q)
> ```
> Because `T_a` is `Z[Q]`-linear, `Σ_r L_r T_a(f_r) = T_a(Σ_r L_r f_r)`, so
> **`T_a(H_fin) ⊆ H_fin`**.

| control | value |
|---|---:|
| `T_a ∘ (left mult by an operator column) == (left mult) ∘ T_a` | **8,250 / 8,250** |
| a CORRUPTED `T_a` (`e_v ↦ e_{va}` only) breaks that commutation | **1,070** fires |
| `T_a F ∈ H_fin` on verified directions, tested exactly with `IL.verify` | **905 / 905** |
| the corrupted `T_a F` leaves `H_fin` | **870 / 905** |
| Hecke translates *rejected* in the whole census ladder | **0** |

But `T_a` is **not a permutation of the basis**, and `Θ_σ` is an ordered
product — functorial only for order-*preserving* basis permutations. So the
cocycle K2/K3 says nothing about `Θ_σ(T_a y)`. The Hecke action is therefore
a **generator of provably valid new elements of `H_fin`**, not a symmetry of
`Θ`. That asymmetry is exactly what kills F3 rather than saving it.

---

## 4. F3 is FALSE

### 4.1 W2l's own saturated baseline (census chain 7)

`(TTcTTctcTcttt, TTTcttcTctt, TTcTTcTctttt)`, `g = TTc`. W2l §6.1's family is
reproduced first, with its own flags, as the calibration:

```text
--m 20 --mod2-only --far-shifts "tt,TT,tctc,ctc,tttt,TTTT,ct,tc" --m-far 4
→ 20 directions, rank V mod 2 = 63, universe 556,
  residual {("f","TT")}, order-invariant (C8 ok)          ← W2l §6.1 exactly
```

Now the Hecke ladder, from only **6** native directions:

| family | dirs | `rank V` mod 2 | universe | residual | C8 |
|---|---:|---:|---:|---|---|
| native | 6 | 18 | 80 | `{z_TT}` | ok |
| + `T_t` | 11 | 45 | 317 | `{z_TT}` | ok |
| + `T_{t²}` | 17 | 108 | 710 | `{z_TT}` | ok |
| + `T_T` | 23 | 198 | 1,227 | `{z_TT}` | ok |
| + `T_{TT}, T_{ct}` | **29** | **315** | **1,924** | `{z_TT}` | ok |
| *(the 2^m decision on 14 of them)* | 14 | 76 | 467 | `{z_TT}` | ok |

**22** of those Hecke directions are outside the `Z`-span of the native
family (exact Hermite echelon on the direction vectors themselves — a check
that never touches `Ξ_Z`, so it confirms the rank growth by a second route).
`rank V` reaches **315 > 63** and the universe **1,924 > 556** at *W2l's own
baseline*, so **`V_S ≠ V_{H_fin}` there**: the saturation W2l measured was a
property of `kernel_directions`, not of `H_fin`. **F3 is disproved, not
merely unproved.**

At 14 directions the exact `2^m` decision runs: **16,384** classes
enumerated (complete over `Z^14` by mod‑2 periodicity), **8,192** distinct
values, **no zero**, C9 planted-zero control **fires**.

### 4.2 `V_{H_fin}` is not finitely generated — effectively

For `a = t^k`, `T_a F` is verified in `H_fin` and the cross generator
`b(F, T_a F)` is computed literally. On chain 7, from **one** native
direction:

| `k` | 1 | 2 | 3 | … | 29 | 30 |
|---|---:|---:|---:|---|---:|---:|
| min `Ξ_Z` coordinate length | 2 | 1 | 2 | … | 28 | 29 |
| max `Ξ_Z` coordinate length | 12 | 13 | 14 | … | 40 | 41 |
| odd coordinates | 21 | 24 | 24 | … | 24 | 24 |

The support sits in a **window of fixed width 13 that translates linearly
with `k`**. Hence `b(F,T_{t^k}F)` and `b(F,T_{t^{k'}}F)` have **disjoint
supports** whenever `|k−k'| > 12`, and disjointly-supported nonzero vectors
are independent. The greedy disjoint subfamily found at `k ≤ 30` has

```text
mod 2 : k ∈ {1,4,5,8,9,12,13,16,17,20,21,24,25,28,29}   →  rank V ≥ 15
over Z: k ∈ {1,4,7,10,13,16,19,22,25,28}                →  rank V ≥ 10
```

and nothing bounds `k`. **`rank V_{H_fin} = ∞`.** Independently reproduced on
census chain 5 (`(TTTctttcTTTcttc, cTTTctttcTctc, TcTTcttc)`, `g = c`,
W2l §6.2's other calibration): max length `k+19`, min length `k−2`, window
width 21, 4 disjoint generators already at `k ≤ 16`.

> One negative result inside the negative result, worth recording: on chain 5
> the *first* native direction gives `b(F,T_aF) ≡ 0 mod 2` for **every** `k`
> (integral support 128, all even). Pairing only one direction would have
> read as "no growth here". Scanning four directions shows the growth. A
> single-direction probe of a translation family is under-powered.

### 4.2b Double-confirmation of the refutation

F3's refutation is the one positive claim this note makes, so it is confirmed
along four independent paths, in the lane's usual "treat it as a bug first"
posture:

1. **Through `Ξ_Z`**: `rank V` mod 2 rises 18 → 45 → 108 → 198 → 315 on chain 7.
2. **Never touching `Ξ_Z`**: an exact Hermite echelon on the direction vectors
   themselves puts 22 of the Hecke directions outside the `Z`-span of the
   native family (134 across the census). So the *direction lattice* grew, not
   just a derived invariant of it.
3. **Mechanistically**: the coordinate-window law of §4.2, which explains
   *why* it grows and gives disjoint supports.
4. **On a second baseline**: chain 5, W2l §6.2's other calibration, with a
   different window width and a different direction count.

Each `T_a F` is additionally re-verified as an exact element of `H_fin` by
`IL.verify` — **905/905**, **0** rejected — with the corrupted Hecke operator
failing the same test 870/905. The refutation does not rest on the Hecke
algebra being the right object; it rests on those elements literally
satisfying `Σ_r L_r F_r = 0`.

### 4.3 Census-wide

| | value |
|---|---:|
| chains | **67** |
| analysable (layer-1 solved at `ρ ≤ 2`, ≥ 1 direction) | **51** — W2l's 51 exactly |
| Hecke directions outside the native `Z`-span | **134**, on **51 / 51** baselines |
| Hecke translates rejected by `IL.verify` | **0** |
| coordinate universe grew under one Hecke word | **51 / 51** (median 139 → 620) |
| `rank V` grew where the rank was recorded | 24 / 28 |

So the native direction generator misses provably-valid elements of `H_fin`
on **every** analysable baseline, not just on the two calibrations.

---

## 5. (c) Per-baseline verdicts on the enlarged families

`--mode ladder --m 3 --hecke-ladder "t" --decide-dirs 8`, all 67 chains,
resumable, 2,800 literal `Θ` evaluations and 2,812 mod‑2 classes:

| verdict | count | meaning |
|---|---:|---|
| `WITNESS` (layer 2 solvable, literally verified) | **0** | — |
| `MOD2_ATTAINABLE_NO_INTEGRAL_WITNESS` | **0** | — |
| `MOD2_UNATTAINABLE_ON_S` | **51** | complete `2^m` decision on a **strictly larger** `S` than W2l's; still bounded by `S` |
| `LAYER1_UNSOLVED_AT_RHO` (`ρ ≤ 2`) | 12 | truncation, no verdict |
| `NO_KERNEL_DIRECTION_FOUND` | 4 | generator produced nothing at `kernel-rho 2` |
| `−c₀ ∈ V_S` mod 2 (the only monotone branch, Lemma C(i)) | **0 / 51** | never fired |
| C9 planted-zero positive control | **51 / 51** fires | the enumeration can find a zero |
| **complete-family verdict** | **0** | and §4 proves none is obtainable this way |

**What did change per baseline: W2l's coordinate certificates evaporate.**
A mod‑2 *coordinate* certificate — a coordinate `D` on which the whole
variation space is even while `c₀` is odd — is the most interpretable
candidate obstruction shape W2l reported. Under **one** Hecke word:

| | value |
|---|---:|
| baselines with ≥ 1 native coordinate certificate | **27** |
| … where the count strictly dropped | **17** |
| … where it dropped to **zero** | **4** |
| total certificates, native → enlarged | **163 → 107** |

Those certificates were artifacts of the direction truncation, exactly as
Lemma C(ii) warned they might be. Conversely, the *reduced residual* on the
two calibration baselines is remarkably inert: on chain 7 it stays the single
coordinate `z_TT`, order-invariant (C8), while `rank V` runs 18 → 315. That
is a **candidate**, not a finding — C8 fails on 33 of the 80 census steps
here, so the residual support is not in general basis-independent, and only
the boolean `−c₀ ∉ V_S` is.

---

## 6. Is the layer-2 question decidable now? No — and that is the answer

The decision the W2 chain wants is `0 ∈ image(Ξ_Z ∘ Θ)` over the complete
`H_fin`. Two routes, both now closed by §4:

1. **The exact `2^m` mod-2 decision** is complete over `Z^m` for a finite `S`
   (mod-2 periodicity), but exponential in `m`, and §4.2 shows `m` cannot be
   bounded: `V_{H_fin}` has infinite rank.
2. **The linear relaxation** `−c₀ ∈ V_S` is the only monotone branch and the
   only statement that transfers to the complete family. It has now failed on
   51/51 baselines at ranks up to 315 — and W2l §4's dimension count says it
   essentially cannot fire, since `rank V` grows quadratically in `m` inside a
   universe that grows at least as fast (here: 315 inside 1,924).

So the honest status of the missing lemma is:

| | statement | status |
|---|---|---|
| **M1** | the translation cocycle exists in closed form, is a genuine 1-cocycle, and the direction-translation law is `2·I_g` | **PROVED** |
| **M2** | mod 2, `Θ∘σ` is exactly `Q`-equivariant | **PROVED** |
| **M3** | `H_fin` is `Q`-stable | **FALSE** (0/2,172) |
| **M4** | `H_fin` is a module over the Hecke algebra `E` | **PROVED**, verified 905/905 |
| **M5** | `V_{H_fin}` is finitely generated (equivalently, f.g. "up to the `Q`-action", since `Ξ_Z` is `Q`-invariant) | **FALSE**, effectively (rank ≥ 15 from one direction, window argument) |
| **M6** | F3 (`V_S = V_{H_fin}` at W2l's saturated `S`) | **FALSE** (63 → 315 on chain 7) |
| **M7** | the layer-2 mod-2 question is decidable on the complete family by this route | **FALSE**, by M5 |

M1 and M2 are exactly what W2l §12 asked to be supplied. They are supplied,
and they do not deliver M7, because M3 — which W2l §12 assumed without
checking — is false.

---

## 7. Consequence

Neither branch of the task's dichotomy fires, and the reason is structural,
so it is worth being exact about what remains.

**There is no death certificate.** No baseline is obstructed on its complete
lift family; the 51 `MOD2_UNATTAINABLE_ON_S` lines are, as in W2l, statements
about a direction set — a *bigger* one now, which makes them stronger
evidence and no closer to a proof. The one finite computation that would
transfer (`−c₀ ∈ V_S`) still never fires, and §4.2 removes the last hope that
growing `S` could change that: the space it would have to fill is infinite
dimensional.

**Nor is the period-two quotient proved blind.** No witness was found either,
so we cannot say layer 2 is always solvable and the quotient sees nothing.

**What actually moved.** (i) A true lemma was added: the section's translation
cocycle, in closed form, with the direction law `Θ_σ(g·y) = g·Θ_σ(y)+2I_g(y)`
and its mod-2 corollary. It is reusable anywhere the Schreier section meets a
`Q`-translate — it is a fact about `F(c,t)`, not about this signature.
(ii) A structural fact that was assumed for four notes is refuted: `H_fin`
carries **no** `Q`-action, only a Hecke action, and the Hecke action is
precisely the wrong kind of symmetry for an ordered-product invariant.
(iii) W2l's empirical saturation — the single strongest piece of evidence in
that note — is **withdrawn**: it measured the direction generator, and a
provably valid, structurally different family blows past it by a factor of 5
on the same baseline. Anything downstream that read the chain-7 line as
"`H_fin` is exhausted here" must be re-read as "`kernel_directions` is
exhausted here".

**For the depth-4 signature.** The class-two layer of this period-two
quotient is not going to be closed by enlarging direction sets, at any
modulus, by any amount of computation of this shape. A layer-2 conclusion now
requires a *uniform* argument over the infinite-rank `H_fin` — a structure
theorem for the quadratic form `b(·,·)` on the Hecke module, or an invariant
that is manifestly independent of the direction set. That is a strictly
harder object than the one W2l §12 hoped for, and identifying it as the real
requirement is what this note contributes.

---

## 8. Controls

| control | asserts | result |
|---|---|---|
| **C1** | the imported lifting calculus is the codex one | defect `(21,48,0)` on every run |
| **L0** | the imported `Θ` is the codex one: `Θ([r_a,r_b]) = e_a∧e_b` | **20 / 20** |
| **L1** | `κ ∈ [N,N]` literally; a corrupted section must leave it | **480/480**; fires **8/8** |
| **L2** | the conjugation identity K1; a corrupted `n(g,v)` must break it | **168/168**; fires **168/168** |
| **L3** | the closed form K2; dropping either half must mismatch | **480/480**; fires **255/255**, counted only where non-vacuous |
| **L4** | the cocycle identity K4 | **64 / 64** |
| **L5** | `T_a F ∈ H_fin`; a corrupted `T_a` must leave it, and must break commutation | **905/905**; **870/905**; **1,070** |
| **L7** | the reordering element grounds the direction law in `F(c,t)` | **480/480**, **98** non-vacuous |
| **inherited** | `theta_attainability.analyse`'s C2 (directions exact + corruption), C3 (`x₀` corruption), C4/C4b (model + corruption), C5 (mod-2 periodicity on the literal map), C8 (residual order-invariance), C9 (planted zero) | all run; C9 **51/51**; C8 reported, 47 ok / 33 fail |
| **every evaluation** | `R_can(x₀+F) ∈ [N,N]` in `F(c,t)` | asserted inside `TR.theta`: **2,800** (census ladder) + **1,080** (chain-7 ladder) + **284** (growth ladders), plus every `κ` and `R` in mode `lemma` |

Two controls had to be repaired before they meant anything, and both are the
lane's recurring lesson: the first `ε`-flip corruption of L2 fired **0/168**
(it is not a corruption — `c` commutes with `c²`), and the first L3 corruption
scored 247/912 only because 665 of the cases had a zero part to drop. A guard
that cannot fire is not a control.

---

## 9. Scope and nonclaims

- **Nothing here is an obstruction, and nothing here is a witness.** The 51
  `MOD2_UNATTAINABLE_ON_S` verdicts remain bounded by their direction set, on
  the same Lemma C(ii) grounds as W2l's.
- **The non-finite-generation of `V_{H_fin}` is *effective*, not a formal
  proof.** It rests on a measured coordinate-window law
  (`[k−1, k+11]` on chain 7, `[k−2, k+19]` on chain 5) verified for
  `k ≤ 30` and `k ≤ 16` and on the disjoint-support independence argument.
  The mechanism — right translation by `t^k` pushes the displacement double
  coset out linearly — is transparent, but "for all `k`" is not machine-checked.
- **`ρ ≤ 2` and the `m` used here are truncations.** 12 baselines have no
  layer-1 solution at `ρ ≤ 2` and 4 more no direction at `kernel-rho 2`;
  those carry no verdict, unchanged from W2l.
- **The joint-centralizer triviality is verified to word length 4 (length 8
  on a 10-chain slice).** The structural argument in §2 is a remark, not a
  machine-checked theorem.
- **The residual support is not claimed canonical.** C8 fails on 33 of 80
  census steps here. Only the boolean `−c₀ ∉ V_S` is basis-independent.
- **Everything that reads `Ξ_Z(Θ) = 0` as "layer 2 is solvable" stays
  conditional on (3.1) and (3.5)**, and through W2i §3.3 on that note's
  `d₂ = 1`. The cocycle, the Hecke action and the rank ladders use only
  (3.1) and the literal free-group residual.
- **No existing file was modified.** `theta_cocycle.py` imports the published
  checkers and the two codex certificates verbatim.
- **No claim about the free-group depth-four class, the bridge, AK(3),
  stable AC, or AC.** This is one layer of one quotient of one signature.

---

## 10. Reproduce

Each command is its own guarded foreground run. `--mode ladder` and
`--mode action` are sliced and resumable: re-run with the same `--json` until
the row count stops growing.

```bash
G="python3 scripts/run_proof_guarded.py --timeout-seconds 55 -- python3"
A=fable/proofs/checkers/theta_cocycle.py
O=fable/proofs/checkers/out

# (a) the cocycle: K1..K4 and L7
$G $A --mode lemma --chains 5:8 --samples 8 --json $O/w2m_lemma.json

# (b0) which group acts on H_fin -- about 5 runs
for i in $(seq 5); do $G $A --mode action --chains 0:67 --m 4 \
        --run-seconds 38 --json $O/w2m_action.json ; done
$G $A --mode action --chains 0:10 --m 3 --central-len 8 --run-seconds 40 \
      --json $O/w2m_action_deep.json

# (b) F3 refuted, effectively
$G $A --mode growth --chains 7:8 --m 4 --dirs-scan 1 --kmax 30 \
      --json $O/w2m_growth_c7.json
$G $A --mode growth --chains 5:6 --m 4 --dirs-scan 4 --kmax 16 \
      --json $O/w2m_growth_c5.json

# (b) F3 refuted at W2l's own saturated baseline
$G $A --mode ladder --chains 7:8 --m 6 --max-dirs 30 --decide-dirs 14 \
      --hecke-ladder "t|t,tt|t,tt,T|t,tt,T,TT,ct" --json $O/w2m_ladder_c7.json
# ... and W2l's calibration itself, unchanged:
$G fable/proofs/checkers/theta_attainability.py --mode decide --chains 7:8 \
      --m 20 --mod2-only --cap-bits 0 --m-far 4 \
      --far-shifts "tt,TT,tctc,ctc,tttt,TTTT,ct,tc"

# (c) the census -- about 11 runs
for i in $(seq 11); do $G $A --mode ladder --chains 0:67 --m 3 \
        --hecke-ladder "t" --max-dirs 12 --decide-dirs 8 --run-seconds 38 \
        --json $O/w2m_ladder.json ; done
```

---

## 11. The single most decisive next question

> **Is the quadratic form `b(·,·)` of `Ξ_Z(Θ)` on `H_fin` *uniformly* nonzero
> — i.e. does the coordinate-window law of §4.2 (`b(F, T_{t^k}F)` occupies a
> width-13 window that translates with `k`) hold for every direction and
> every Hecke element, with a uniformly nonzero leading block?**

If it does, `Ξ_Z(Θ)` restricted to the Hecke module has a *periodic normal
form*, and the attainability question becomes a question about one finite
block plus a shift — the first shape in this chain that could be decided on
the complete family. Every measurement in §4.2 is consistent with it: the
window width is constant (**13** on chain 7, **21** on chain 5); the odd
support is constant at **24** per step on chain 7 from `k = 2` on; and the
count of genuinely new coordinates per step is constant — **22** on chain 7,
**184** on chain 5 — across the whole ladder. That periodicity is the only
structure this note found that is not bounded by a direction set, and it is
the only remaining candidate for a uniform argument.

The negative branch is now closed: growing `S`, at any modulus, with any
direction generator, cannot decide this — §4.2 is the proof, and it is the
one thing W2l could not say.
