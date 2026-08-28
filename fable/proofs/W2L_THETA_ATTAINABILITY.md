# W2l: is `0 ∈ image(Ξ_Z ∘ Θ)` over the layer-1 solution family?

Date: 2026-08-28 · Checker: `checkers/theta_attainability.py`
(imports `theta_residual_evaluator.py`, `corrected_operators.py`,
`infinite_index_liveness.py`, `period_two_baseline_liveness.py`,
`period_two_parametric_solvability.py` and the two codex certificates
**all unmodified**; guarded foreground runs, one at a time, sliced and
resumable).

Run records: `checkers/out/w2l_decide.json` (the whole census),
`w2l_witness.json` (the codex calibration), `w2l_struct.json` (the
independent structural path), `w2l_stab_c5.json`, `w2l_stab_c5_r2.json`,
`w2l_stab_c5_r3.json`, `w2l_stab_c5_far.json`, `w2l_stab_c7.json`,
`w2l_stab_c7b.json`, `w2l_saturated_c7.json`. Every record carries
`controls_passed: true`.

Answers `W2K_CORRECTED_REVERIFY.md` §12, the only question left in the W2
chain that can change the layer-2 answer.

---

## 0. Verdict

| question | answer | status |
|---|---|---|
| Is the mod-2 reduction of `F ↦ Ξ_Z(Θ(x₀+F))` affine-**linear**, so that mod-2 attainability is GF(2) linear algebra? | **No — the premise is wrong.** `G mod 2` is periodic (that is what W2j proved) but *quadratic*: the polarisation `b_jk` is odd on **979 of 1,047** cross pairs over 48 census baselines; only **4** baselines are genuinely affine-linear mod 2. Two independent code paths agree **16/16**. | **PROVED / premise CORRECTED** (§2) |
| Is `0` attainable mod 2 on the direction sets reached? | **No, on 51/51 baselines** — by *complete* enumeration of all `2^m` classes (9,338 classes; complete over `Z^m`, not a box), with a positive control that fires **51/51**. | **complete over each `S`** (§3) |
| Is that an obstruction? | **NO.** Every one of these statements is bounded by the direction set `S`, and enlarging `S` can only help. The one shape of finite computation that WOULD transfer to all of `H_fin` (Lemma C(i): `-c₀ ∈ V_S`) **never fired** — and §4 shows it essentially cannot, for dimension reasons. | **§4** |
| Any integral witness? | **None. 0 found.** The integral search never even fires: mod 2 already excludes `0` on every tested `S`, so there is no mod-2 class to search inside. | **§5** |
| Is there a local (mod 4, 8, 3, 9, 5) obstruction? | **Not one that means anything.** `-c₀ ∉ V_S` at every modulus on 51/51 — but that is the same bounded statement, and a local failure computed on a sublattice is **not** window-independent, contrary to the framing this task was set with. | **§5, premise CORRECTED** |
| Does the picture survive when the direction set is pushed as far as the generator goes? | **Yes, and on one baseline the generator provably closes.** On census chain 7 the direction search **saturates** (20 directions, `rank V = 63`, coordinate universe 556, unchanged under 8 far-translate seeds): all **1,048,576** mod-2 classes enumerated, **no zero**. On chain 5 the residual is *identical* (the same 11 coordinates) as `rank V` grows 9 → 119 across three direction families. | **strongest evidence, still bounded** (§6) |
| Calibration against the codex escape certificate | **exact.** Residual lengths `[82, 442, 678, 614]`, obstruction bits `(1,1) (0,1) (0,1) (1,0)`, 4 mod-2 classes, none vanishing, 4 distinct — W2j §4.3 reproduced, and the witness's residual is the single coordinate `z_{TcTct}` that W2j §3 reports. | **VERIFIED** (§7) |
| **The layer-2 question itself** | **OPEN.** No witness, no obstruction. What moved is the *shape* of the remaining question (§9). | **open** |

---

## 1. The mathematics, before any computing

### 1.1 The object

For a census chain `(R,S,U)`, target conjugator `g`, gauge window and
conjugator tuple `h = (h₀,h₁,h₂,h₃,g)`, let `L = (L₀..L₄)` be the **corrected**
layer-1 operators (`corrected_operators.build_operators_exact`, equal column
for column to `theta_residual_evaluator.exact_operators` on 67/67 chains,
W2k §7) and `D` the defect. The layer-1 solution family is the affine set

```text
{ x ∈ M⁵ : [D] + Σ_r L_r x_r = 0 }  =  x₀ + H_fin ,   H_fin = ker(L : M⁵ → M)
```

with `M = Z[X]`, `X = Q/⟨c⟩` free abelian of **infinite** rank — the
"complete balanced source-pair space" of the source's §3.2. Put

```text
Ψ(F) := Θ(x₀ + F) ∈ Λ²M ,      G(F) := Ξ̃(Ψ(F))
```

in the raw `Ξ_Z` coordinates (free double cosets over `Z`; self-inverse ones
kept integral so the polynomial model is exact). By W2i §3.3 — conditional on
(3.1) and (3.5) — layer 2 is solvable at `x₀ + F` **iff**

```text
every free coordinate of G(F) vanishes over Z, and every self-inverse
coordinate is EVEN.                                                     (Z)
```

Every evaluation of `G` in this note goes through
`theta_residual_evaluator.theta`, which replays (1.8) literally in `F(c,t)`
and asserts `R_can ∈ [N,N]` before computing anything. **2,316 evaluations in
the census run, every one of them a free-group ground-truth test** — the
discipline W2j/W2k made mandatory. Nothing is verified through the operators
that produced it.

### 1.2 Lemma A — the polynomial law

`Ψ` is a polynomial map of degree ≤ 2 on `H_fin`. `N` is free on the Schreier
basis `(r_v)` and the section is `σ(y) = Π_v r_v^{y_v}` in a fixed order, so

```text
Θ(σ(y)) = Σ_{v<w} y_v y_w · e_v ∧ e_w                                    (Q)
```

is *already* a genuine quadratic form in `y` (and `Θ(r_v^k) = 0`); everything
else in the recurrence enters through products of conjugates whose `M`-classes
are affine in `F`, and `Θ(ab) = Θ(a)+Θ(b)+[a]∧[b]` contributes only bilinear
terms. Hence on the lattice spanned by directions `F_1..F_m`,

```text
G(n) = c₀ + Σ_j a_j n_j + Σ_j b_jj n_j² + Σ_{j<k} b_jk n_j n_k
```

with integral vector coefficients, read off by finite differences of the
literal map and then **verified by held-out literal prediction**: 566
predictions, 566 agreements, including `n_j = −1`, `n_j = 3` and random
`n ∈ [−2,3]^m` (control C4; a corrupted coefficient breaks it, C4b fires).

### 1.3 Lemma B — mod 2 the map is periodic but QUADRATIC

Degree ≤ 2 with integer coefficients gives, for **every** modulus `q`,

```text
G(n + q e_j) − G(n) = q a_j + b_jj(2 q n_j + q²) + q Σ_k b_jk n_k ≡ 0 (mod q)  (P)
```

so `G mod q` factors through `(Z/q)^m`. That is W2j's periodicity, and it is
what makes the `2^m` enumeration *complete over `Z^m`* rather than a box
search. It is **not** linearity. Over `F₂`, `n_j² = n_j`, so

```text
Φ(n) := G(n) mod 2 = c₀ + Σ_j (a_j + b_jj) n_j + Σ_{j<k} b_jk n_j n_k
```

which is affine-linear only if every polarisation `b_jk` is even. §2 measures
it: it is not. **Mod-2 attainability of `0` is therefore a system of
`F₂`-quadratic forms, not GF(2) linear algebra.**

### 1.4 Lemma C — what a finite computation can and cannot transfer

Let `V_S` be the `Z`-span of the value differences of `G` on the sublattice
spanned by a finite direction set `S`. From Lemma A,

```text
{ G(n) − c₀ : n ∈ Z^m }  spans  V_S = ⟨ a_j + b_jj , 2 b_jj , b_jk ⟩
```

(`n = e_j` gives `a_j+b_jj`; `n = 2e_j` gives `2a_j+4b_jj`, and twice the
first minus that gives `−2b_jj`; `n = e_j+e_k` gives the rest). Add `2 e_D`
for every self-inverse coordinate, since (Z) asks only that those be even;
call the result `V_S⁺`. Then `G(n) ∈ c₀ + V_S⁺` for every `n`, so

> **(i) `−c₀ ∈ V_S⁺` is MONOTONE in `S`.** Enlarging the direction set can
> only enlarge `V_S⁺`. So membership at one finite `S` transfers to `H_fin`
> and proves **no linear certificate exists at all** — no homomorphism
> `f : W_Q → Z` or `→ Z/q` with `f(G(F))` a fixed nonzero constant on the
> whole family. This is the *only* window-independent negative a finite
> computation here can deliver. It strictly generalises W2j §5.2.2, which
> killed the single functional "the whole mod-2 vector" (constancy).
>
> **(ii) `−c₀ ∉ V_S⁺` is NOT an obstruction.** It is a statement about `S`,
> and the same monotonicity says a larger `S` can destroy it.

The same asymmetry governs everything: a WITNESS is window-independent (it is
an actual element of `H_fin`); an ABSENCE on a sublattice never is. **In
particular a failure of local solvability mod `p^k` computed on a sublattice
is not window-independent either** — the honest local statement is the linear
relaxation of (i)/(ii) at that modulus, and that is what §5 computes.

### 1.5 The finiteness statement, and its proof status

| | statement | status |
|---|---|---|
| **F1** | For a finite `S`: the model of Lemma A, the exact mod-2 decision by `2^m` enumeration (complete over `Z^m` by (P)), and the memberships `−c₀ ∈ V_S⁺` mod `q` and over `Q`, are finite exact computations. | **PROVED** |
| **F2** | Membership `−c₀ ∈ V_S⁺` at any single finite `S` transfers to `H_fin` (Lemma C(i)). | **PROVED** |
| **F3** | `V_S⁺ = V_{H_fin}⁺` for the computed `S`, i.e. the direction search saturates. | **NOT PROVED** |

F3 is the whole gap, and it is worth saying exactly why there is no analogue
of W2h's Lemma 5 here. That lemma works because `π(L_i e_v)` is a *translate*
of one fixed finite pattern, which makes the row lattice finitely generated.
`Θ` has no such equivariance: the section `σ` is not equivariant
(`g σ(x) g⁻¹ = σ(g·x)` only modulo `[N,N]`, and that error is precisely what
`Θ` measures), and the conjugators `h_r` are fixed while the perturbation is
not, so replacing `x` by `g·x` does not conjugate the recurrence. What is
reported instead of a theorem is the **empirical saturation** of §6.

---

## 2. Lemma B measured — the premise this task was set with is wrong

`--mode decide` records the polarisation of every evaluated cross pair;
`--mode struct` recomputes the same fact from literal evaluations alone,
without the model class, as an independent path.

| | value |
|---|---:|
| baselines with ≥ 1 cross pair | **48** |
| cross pairs evaluated | **1,047** |
| pairs with `Φ(e_j+e_k) ≠ Φ(e_j)+Φ(e_k)+Φ(0)` (mod 2) | **979** |
| baselines genuinely affine-linear mod 2 | **4** |
| baselines quadratic mod 2 | **44** |
| independent `--mode struct` path: baselines / pairs / nonlinear | 16 / 216 / **185** |
| struct vs decide agreement on the linear/quadratic call | **16 / 16** |
| mod-2 periodicity (P) checked on the literal map | **566 / 566** |

The four affine-linear baselines are

```text
(TTTctttcTTTcttc, cTTTctttcTctc, TTTctttcTctcTc)  g=c    m=8, 28 pairs, all even
(TTctcTctc, TcTcttc, TTctcTcttcTTct)              g=""   m=4,  6 pairs, all even
(TTctcTctc, cTctcTcTctctc, TTctcTcttcTTct)        g=""   m=2,  1 pair
(cTcTctcTTcttc, TcTcttc, TcTTcttc)                g=Tc   m=2,  1 pair
```

> **Consequence for method.** "Decide mod-2 attainability by linear algebra on
> `ker(L) mod 2`" cannot be executed as stated. What replaces it is the
> complete `2^m` enumeration (Gray-coded, `O(m)` per class) plus the *linear
> relaxation* of Lemma C, which is the only part that transfers.

---

## 3. (a) The mod-2 decision across the census

`--mode decide --m 8`, window `(0,0,0,0)`, `ρ ≤ 2`, all 67 census chains:

| | value |
|---|---:|
| chains | **67** |
| exact layer-1 solution at `ρ ≤ 2` (matches W2j/W2k's 55) | 55 |
| … with at least one kernel direction found | **51** |
| … with none (`NO_KERNEL_DIRECTION_FOUND`) | 4 |
| no layer-1 solution at `ρ ≤ 2` (truncation, not a death claim) | 12 |
| direction-set ranks reached | `m = 8` on 36, `≤ 5` on 15 |
| literal `[N,N]` evaluations of `Θ` | **2,316** |
| mod-2 classes enumerated (complete over each `Z^m`) | **9,338** |
| classes with `Ξ_Z(Θ) ≡ 0 (mod 2)` | **0** |
| baselines where the map is injective on `(Z/2)^m` (`2^m` distinct values) | **35 / 51** |
| **integral witnesses** | **0** |
| positive control C9 (the enumeration finds a planted zero) | **51 / 51** |

So on every baseline reached, `0` is unattainable mod 2 — hence over `Z` —
on the whole lattice spanned by the directions found. That is W2j's rank-2/4
result at rank 8, on 51 baselines instead of 24, with the corrected operators
and a positive control.

**It is still a statement about `S`.**

---

## 4. The linear relaxation — and why its useful branch cannot fire

| | value |
|---|---:|
| baselines with `−c₀ ∈ V_S⁺` mod 2 | **0 / 51** |
| … mod 4, 8, 3, 9, 5, and over `Q` | **0 / 51** each |
| baselines whose certificate is a single **coordinate** functional mod 2 | 16 (97 coordinates in total) |
| baselines whose certificate is a genuine non-coordinate functional | 35 |
| `mod-2` residual weight (35 baselines where it is defined) | min 1, median 3, max 20 |
| residual support independent of elimination order (C8) | **18 / 35** |
| coordinate universe (size of the ambient `F₂` space) | min 13, median 406, max 5,973 |
| `rank V_S` mod 2 at `m = 8` | ≤ **36** |

Read this honestly. `rank V_S ≤ m + m(m−1)/2 + m` grows quadratically in `m`,
while the coordinate universe grows at least as fast (it is the union of the
supports of those same generators). At `m = 8` a rank-36 subspace sits inside
a space of median dimension 406. **A vector of `c₀`'s size lies in such a
subspace essentially never**, so `−c₀ ∉ V_S⁺` is what a dimension count
predicts and carries no evidential weight whatever. And C8 shows the residual
*support* is not even basis-independent on half the baselines: only the
boolean `−c₀ ∉ V_S⁺` is invariant, not the coordinates that block it.

> **Methodological finding.** Lemma C(i) — the only window-independent
> negative available from a finite computation — is *practically unreachable*
> by this route, because the branch that would fire it is a measure-zero
> coincidence at every rank the computation can reach. The finite computation
> is one-sided in exactly the direction that cannot fire. Any future attempt
> at an obstruction here must come from structure, not from enlarging `S`.

---

## 5. (b) and (c) — the integral and local questions are vacuous here

The integral hunt searches `n = ε + 2k` inside a mod-2 solution class, capped
at 1,000 evaluated points (repo hard rule). **It never fires**: there is no
mod-2 solution class on any of the 51 baselines. The same is true of every
local question: mod 4, 8, 3, 9 and 5 are all decided negatively, and all of
them by the *same bounded* linear relaxation of §4.

> **The task's framing that "a failure mod `p^k` IS window-independent" is
> wrong, and the correction matters.** Local solvability is a property of the
> value set; enlarging the direction set enlarges the value set; so a local
> failure at rank `m` says nothing about rank `m+1`, let alone about `H_fin`.
> The window-independent local statement is the *membership* `−c₀ ∈ V_S⁺ mod
> p^k` (Lemma C(i)), which is monotone — and it did not fire either (§4).

Consequently **no local-global (Hasse) discussion is reachable yet**: one
cannot ask whether the quadratic system represents `0` over every `Z_p` and
over `R` while it is not even represented mod 2 on any sublattice tested. The
honest position is that the local conditions have **not** all passed; they
have not been tested on a lattice where mod 2 permits a solution.

---

## 6. (F3) How far the direction set can be pushed

Two ladders, `--mode stability`, mod-2 model only (the `G(2e_j)` evaluations
are unnecessary mod 2, which is what makes large `m` reachable).

### 6.1 Census chain 7 — the direction generator SATURATES

`(TTcTTctcTcttt, TTTcttcTctt, TTcTTcTctttt)`, `g = TTc`:

| `m` requested (+ 3 far-translate seed families) | directions | `rank V` mod 2 | universe | residual |
|---:|---:|---:|---:|---|
| 4 | 7 | 25 | 299 | `{z_TT}` |
| 8 | 11 | 51 | 484 | `{z_TT}` |
| 12 | 15 | **63** | **556** | `{z_TT}` |
| 16 | 19 | **63** | **556** | `{z_TT}` |
| 20 | 19 | **63** | **556** | `{z_TT}` |
| 24, with **8** far-translate seed families (32 extra requested) | **20** | **63** | **556** | `{z_TT}` |

The generator closes: adding eight families of directions seeded at
*translates* of the defect support (`tt, TT, tctc, ctc, tttt, TTTT, ct, tc`)
produces nothing new. On that saturated family, `--mode decide --m 20`:

```text
all 1,048,576 mod-2 classes enumerated  →  0 UNATTAINABLE
4,096 distinct mod-2 values (so the map is non-constant, W2j §5.2.2 holds)
153 of 190 cross pairs odd  →  quadratic mod 2
residual = { ("f","TT") } , order-invariant
```

> This is the strongest per-baseline statement in the note: on a direction
> family that the generator **cannot extend**, `0` is unattainable mod 2 over
> the whole lattice `Z^20`. It is still not an obstruction — "the generator
> cannot extend it" is not "`H_fin` has no more elements" (F3).

### 6.2 Census chain 5 — the residual is stable under everything tested

`(TTTctttcTTTcttc, cTTTctttcTctc, TcTTcttc)`, `g = c`:

| `m` | `rank V` mod 2 | universe | residual weight |
|---:|---:|---:|---:|
| 2 | — (3 coordinate certificates) | 197 | — |
| 4 | 9 | 824 | **11** |
| 6 | 15 | 1,024 | **11** |
| 8 | 26 | 1,468 | **11** |
| 10 | 40 | 1,692 | **11** |
| 12 | 50 | 1,925 | **11** |
| 14 | 60 | 2,334 | **11** |
| 16 | 91 | 2,737 | **11** |
| 18 | 105 | 3,285 | **11** |
| 20 | 119 | 3,612 | **11** |

and the **same 11 coordinates** appear at `kernel-rho = 2` (`m = 4…16`) and
`kernel-rho = 3` (`m = 4…12`), and with five far-translate direction families
mixed in (`m = 15`, universe 4,729):

```text
TTTctct, TTct, TTctct, TcTctctttcT, TcTctttcT, TcTctttcTTctttcT,
TcttcTTctttcT, TctttcT, tcTTTcttcT, tcTTTcttcTT   (free)   +   tcT (self-inverse)
```

`rank V` grows by 110 while the residual does not move by one coordinate.
Suggestive — and still exactly what a dimension count predicts (§4), which is
why it is filed as a *candidate*, not a finding. C8 (order-invariance) holds
on this baseline but fails on 17 of 35 census baselines, so the residual
support is not in general a canonical object.

---

## 7. Calibration — the codex escape certificate

`--mode witness` runs the codex conjugator tuple `CODEX_H`, the codex
`CORRECTION` as `x₀`, and the certificate's **own** two kernel directions
`k₀ = ALTERNATE_10 − base`, `k₁ = ALTERNATE_01 − base`:

| | got | expected |
|---|---|---|
| residual lengths, 4 parity classes | `[82, 442, 678, 614]` | identical |
| degree-two obstruction bits | `(1,1) (0,1) (0,1) (1,0)` | identical |
| mod-2 classes / vanishing / distinct | 4 / **0** / 4 | W2j §4.3 |
| residual of `−c₀` mod `V` | `{ ("f","TcTct") }` | W2j §3: `Ξ_Z(Θ(x_codex)) = −1·z_{TcTct}` |
| C2 / C3 / C4b corruption controls | fire | fire |

The four-parity-class escape certificate is reproduced exactly by the mod-2
machinery, and the reduced residual is the single coordinate W2j reports as
the whole value of `Ξ_Z(Θ)` at the codex witness. **The calibration control is
green.**

---

## 8. Controls

| control | asserts | result |
|---|---|---|
| **C1** fixed-`h` witness | the imported lifting calculus is the codex one | defect `(21,48,0)` on every run |
| **C2** kernel directions exact | `Σ_r L_r F_r = 0` term by term, and a CORRUPTED direction is rejected | **51/51** exact; corruption fires **51/51** |
| **C3** literal layer-1 test can fail | a corrupted `x₀` leaves `[N,N]` | fires **14/14** run |
| **C4** the integral model | held-out literal prediction incl. `n_j = −1`, `3`, random `n ∈ [−2,3]^m` | **566 / 566** |
| **C4b** model corruption | a corrupted coefficient breaks the prediction | fires on every baseline |
| **C5** mod-2 periodicity (P) | on the literal map, not on the fit | **566 / 566** |
| **C6** codex calibration | certificate lengths, bits, and W2j §4.3's 4-class line | **exact** (§7) |
| **C7** membership re-multiplied out | a positive membership answer is checked term by term | no positive answer occurred; the check is wired and runs |
| **C8** residual order-invariance | the reduced representative under a reversed generator list | holds 18/35, **fails 17/35** — reported, and the reason the residual support is not claimed as canonical |
| **C9** positive control | the `2^m` enumeration finds a *planted* zero (`c₀ := α₀`) | fires **51 / 51** |
| every evaluation | `R_can(x₀+F) ∈ [N,N]` in `F(c,t)` | **2,316 / 2,316** |

---

## 9. Verdict tree, per baseline

| verdict | count | meaning |
|---|---:|---|
| `WITNESS` (layer-2 solvable, literally verified) | **0** | — |
| `MOD2_ATTAINABLE_NO_INTEGRAL_WITNESS` | **0** | — |
| `MOD2_UNATTAINABLE_ON_S` | **51** | complete `2^m` decision on the directions found; **bounded by `S`** |
| `LAYER1_UNSOLVED_AT_RHO` (`ρ ≤ 2`) | 12 | truncation, not a death claim |
| `NO_KERNEL_DIRECTION_FOUND` | 4 | the generator produced nothing at `kernel-rho 2` |
| `OBSTRUCTED mod m` (double-confirmed) | **0** | none claimed; §4 explains why none could be |
| `LOCALLY SOLVABLE BUT NO WITNESS` | **0** | not reachable: mod 2 already excludes `0` on every `S` |

Per-baseline rows (chain, `g`, `m`, `c₀` support, `rank V`, universe, residual
weight, C8) are in `out/w2l_decide.json`. The six baselines closest to the
membership that would kill every linear certificate at once — residual weight
**1**, i.e. one coordinate short — are the natural targets for a bigger
direction set:

| chain | `g` | `m` | `c₀` sup | `rank V` | universe | resid | C8 |
|---|---|---:|---:|---:|---:|---:|---|
| `(TTcTTctcTcttt, TTTcttcTctt, TTcTTcTctttt)` | `TTc` | 8 | 8 | 30 | 158 | 1 | ok |
| `(TTcTTctcTcttt, cTctcTcTctctc, TTcTTcTctttt)` | `TTc` | 8 | 11 | 30 | 145 | 1 | fails |
| `(TTctcTctc, TTTcttcTctt, TTctcTcttcTTct)` | `""` | 2 | 2 | 3 | 80 | 1 | ok |
| `(TTctcTctc, TTTcttcTctt, TTcttcTc)` (the codex chain) | `""` | 8 | 2 | 36 | 435 | 1 | ok |
| `(TTctcTctc, TcTcttc, TctcTcTctc)` | `""` | 1 | 5 | 1 | 13 | 1 | ok |
| `(TTctcTctc, cTctcTcTctctc, TTcttcTc)` | `""` | 8 | 2 | 36 | 692 | 1 | ok |

The first of these is census chain 7, where §6.1 already pushed the direction
generator to saturation and the residual did not move.

**The layer-2 question is OPEN.** It was open before and it is open now; what
changed is that the mod-2 route is now understood (quadratic, not linear),
the negative results are correctly labelled as bounded, and one baseline is
known where the direction generator itself closes.

---

## 10. Scope and nonclaims

- **Nothing here is an obstruction.** Every "0 unattainable" is over the
  lattice spanned by a finite direction set inside an infinite-rank `H_fin`.
  The one finite computation that would transfer (Lemma C(i)) never fired,
  and §4 argues it essentially cannot at any reachable rank.
- **F3 is not proved.** The saturation of §6.1 is a property of
  `kernel_directions` under the seeds tried, not a theorem about `H_fin`.
- **`ρ ≤ 2` and `m ≤ 8` (census) are truncations.** 12 baselines have no
  layer-1 solution at `ρ ≤ 2` and 4 more no direction at `kernel-rho 2`;
  those carry no verdict.
- **The residual support is not claimed canonical.** C8 fails on 17 of 35
  baselines. Only the boolean `−c₀ ∉ V_S⁺` is basis-independent.
- **Everything that reads `Ξ_Z(Θ) = 0` as "layer 2 is solvable" stays
  conditional on (3.1) and (3.5)**, and through W2i §3.3 on that note's
  `d₂ = 1` — unchanged from W2i/W2j/W2k. `G(F)` itself is unconditional: it is
  a function of the literal free-group residual alone.
- **No existing file was modified.** `theta_attainability.py` imports the
  published checkers and the two codex certificates verbatim.
- **No claim about the free-group depth-four class, the bridge, AK(3), stable
  AC, or AC.** This is one layer of one quotient of one signature.

---

## 11. Reproduce

Each command is its own guarded foreground run (`--timeout-seconds ≤ 55`).
`--mode decide` and `--mode struct` are sliced and resumable: re-run with the
same `--json` until the summary stops growing.

```bash
G="python3 scripts/run_proof_guarded.py --timeout-seconds 55 -- python3"
A=fable/proofs/checkers/theta_attainability.py
O=fable/proofs/checkers/out

# calibration (C6)
$G $A --mode witness --json $O/w2l_witness.json

# (a)+(b)+(c) the census, rank 8, resumable -- about 11 runs
for i in $(seq 11); do $G $A --mode decide --m 8 --run-seconds 44 \
                            --json $O/w2l_decide.json; done

# Lemma B by the independent, model-free path
for i in $(seq 3); do $G $A --mode struct --chains 0:20 --m 6 \
                            --run-seconds 44 --json $O/w2l_struct.json; done

# (F3) the ladders -- `--mode stability` is resumable per (chain, m)
for L in 2,4,6,8 10,12 14,16 18,20; do \
  $G $A --mode stability --chains 5:6 --ladder $L --mod2-only --cap-bits 16 \
        --run-seconds 42 --json $O/w2l_stab_c5.json ; done
$G $A --mode stability --chains 5:6 --ladder 8 --mod2-only --cap-bits 0 \
      --far-shifts "tt,TT,tctc,ctc,tttt" --m-far 4 --json $O/w2l_stab_c5_far.json
for L in 4,8 12,16; do $G $A --mode stability --chains 5:6 --ladder $L \
      --mod2-only --cap-bits 0 --kernel-rho 2 --json $O/w2l_stab_c5_r2.json; done
for L in 4,8 12;    do $G $A --mode stability --chains 5:6 --ladder $L \
      --mod2-only --cap-bits 0 --kernel-rho 3 --json $O/w2l_stab_c5_r3.json; done

for L in 4,8,12 16,20; do $G $A --mode stability --chains 7:8 --ladder $L \
      --mod2-only --cap-bits 0 --far-shifts "tt,TT,tctc" --m-far 3 \
      --json $O/w2l_stab_c7.json ; done
$G $A --mode stability --chains 7:8 --ladder 24 --mod2-only --cap-bits 0 \
      --far-shifts "tt,TT,tctc,ctc,tttt,TTTT,ct,tc" --m-far 4 \
      --json $O/w2l_stab_c7b.json                       # saturation: 20 dirs

# the saturated family, all 2^20 mod-2 classes
$G $A --mode decide --chains 7:8 --m 20 --mod2-only --cap-bits 20 \
      --far-shifts "tt,TT,tctc,ctc,tttt,TTTT,ct,tc" --m-far 4 \
      --json $O/w2l_saturated_c7.json
```

---

## 12. The single most decisive next question

> **Is `Ξ̃(Θ)`'s linear part `λ : H_fin → Λ²M / (Ξ_Z-kernel)` finitely
> generated as a module over anything — i.e. is there a translation law for
> `Θ` playing the role W2h's Lemma 5 plays for `π`?**

Everything in this note reduces to F3, and F3 is not a computation, it is a
missing lemma. Three reasons this is the fork.

**First, the negative branch is closed by dimension counting.** §4 shows the
only window-independent negative a finite computation can produce
(`−c₀ ∈ V_S⁺`) is a coincidence that will not occur at any rank the machine
can reach. Growing `S` is therefore not a plan; it only produces more bounded
"unattainable on `S`" lines like the 51 here.

**Second, the positive branch is a needle in `H_fin`, and the mod-2 filter is
quadratic.** 9,338 complete mod-2 classes and 1,048,576 more on the saturated
family produced no zero. If a witness exists it is not near any `x₀` the
layer-1 solver finds, and finding it needs the family described, not sampled.

**Third, `Θ`'s failure of equivariance is explicit and might be computable.**
`g σ(x) g⁻¹ = σ(g·x) · κ(g,x)` with `κ(g,x) ∈ [N,N]`, and `Θ(κ(g,x))` is a
*bilinear* correction in `(g, x)`. If that cocycle can be written down, then
`λ(g·F)` is `g·λ(F)` plus an explicit term, `V_{H_fin}` becomes a module with
finitely many generators up to the `Q`-action, and both branches of Lemma C
become decidable on the complete family — which is exactly what W2k §12
asked for and what this note could not supply.

## Post-hoc correction (cycle 23)

`W2M_THETA_COCYCLE.md` withdraws this note's chain-7 **saturation** reading:
the 20-direction rank-63 stabilisation was a bounded-set artifact — six
native plus 23 Hecke-translated directions raise it to rank 315 in a
universe of 1,924, with 22 directions outside the native Z-span
(double-confirmed four ways). `rank V_{H_fin} = ∞`: growing any direction
set S can never decide attainability at any modulus, in either direction.
The per-baseline verdicts here remain correct as stated (bounded by S);
what is withdrawn is only the suggestion that chain 7's S was complete.
The conjectured finite generation "up to the Q-action" is refuted — no
Q-action on H_fin exists; the object that acts is the Hecke algebra
Z[<c>\Q/<c>], and the surviving candidate structure is the fixed-width
coordinate-window law under Hecke translation (W2M §6).
