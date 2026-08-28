# W2k: the `L0` defect repaired, and every suspended W2 claim re-decided

Date: 2026-08-28 · Checkers: `checkers/corrected_operators.py` (the corrected
builder `build_operators_exact` + the literal validator) and
`checkers/w2k_reverify.py` (the re-verification driver; it imports
`g_stratum_death.py`, `infinite_index_liveness.py`, `layer2_d2_invariant.py`,
`period_two_parametric_solvability.py`, `period_two_liveness_invariance.py`,
`period_two_baseline_liveness.py`, `theta_residual_evaluator.py` and the codex
certificates **all unmodified**, and rebinds their operator source at run
time). Guarded foreground runs, one at a time, sliced and resumable.

Run records: `checkers/out/w2k_opcheck_a.json` / `_b`,
`w2k_theta_reconcile.json`, `w2k_sweep.json`, `w2k_abelian.json`,
`w2k_invariance.json`, `w2k_omega_a.json` / `_b`, `w2k_dsource.json`,
`w2k_literal.json`, `w2k_inf_identity_a.json` / `_b`, `w2k_inf_image_a.json` /
`_b`, `w2k_inf_lift_a.json` / `_b` / `_c`, `w2k_inf_liftlit.json`,
`w2k_d2_uniform.json`, `w2k_d2_a.json` / `_b`, `w2k_d2_identity_a.json` / `_b`,
`w2k_d2_probe_a.json`, `w2k_d2_inf_a.json`.

Answers `W2J_THETA_RESIDUAL.md` §8, first half: *"Re-derive `L0` in the
existing checkers and re-run W2g's `d = 1`, W2h's margin law and W2i's
`d₂ = 1` on the 59 chains with `q(h1) ≠ 1`."*

---

## 0. Verdict

| question | answer | status |
|---|---|---|
| Which of the five columns were wrong? | **`L0` only.** Re-derived from first principles column by column and validated on a probe set 3.3× wider than W2j's: **6,700 literal free-group checks per operator set, 67/67 chains, 0 exact mismatches**; the shipped/re-broken builder fails **1,180**, every one in column 0, on exactly the 59 chains with `q(h1) ≠ 1`. | **PROVED** (§1) |
| Is layer 1 still obstruction-free — `d = 1` everywhere? | **Yes, and for a reason that makes it immune.** `d = 1` on **44/44** finite-index chains and `d_eff = 1` on **23/23** infinite-index ones, *and* on **44/44** the value `d = 1` is already supplied by an `L1` row alone — and `L1 = bridge·(B − S)` never sees `h1`. | **HELD** (§4) |
| Is `Ξ_Z : C₂ → W_Q` still an isomorphism? | **Yes.** `d₂ = 1` for **every** displacement class of all **44/44** finite-index chains, 1,936 sampled blocks, 0 extra obstruction, 0 torsion, detector fires 22/22. | **HELD** (§6) |
| Do the layer-1 *liveness* numbers survive? | **No — they all move, and always upward.** Live chains **21 → 31**, live windows **253 → 453**, W2b's headline **6 → 13**. Nothing went the other way: **0** chains live-to-dead. | **RETRACTED / strengthened** (§3) |
| Do W2f's five dead strata survive? | **Two of five.** `S3` (`p3 ≥ 4`) and `S4` (`k3 ≥ 7`) still have zero live chains and zero windows solvable mod 3 or mod 5. `S1`, `S2` and `S5` each now contain a live chain. | **partly RETRACTED** (§3.3) |
| Does W2e's window-level refutation survive? | **Yes**, with a corrected transformation law: **142** mismatching aligned window pairs of 405 (was 161), and the "no uniform right-unit intertwiner" conclusion is now *structurally* immune (it rests on `L1`, which did not change). | **HELD** (§5) |
| Does W2j's own `Θ` / `Ξ_Z(Θ)` stack move? | **No, not at all.** `build_operators_exact` is **identical, column for column, on 67/67 chains** to the `exact_operators` W2j already used. | **HELD** (§7) |
| Were the old "VERIFIED layer-1 solutions" actually solutions? | **Mostly not.** Re-tested in `F(c,t)`: of 46 shipped solutions, **22 pass and 24 fail** — and the 22 are exactly the ones with `q(h1) = 1` **or** `x₀ = 0`. Of the corrected solutions, **55/55 pass**, plus **21/21** of W2h's constructive lifts. | **PROVED** (§2) |

---

## 1. (a) The corrected builder, all five columns

### 1.1 The derivation

`corrected_operators.py`'s module docstring carries it in full; the shape is:
perturb `h_i → n_i h_i` with `n_i = σ(x_i)`, write each perturbed word of the
recurrence (1.8) as `δ · (unperturbed)` with `δ ∈ N`, and read `[δ]` off the
three rules `[nn'] = [n]+[n']`, `[w n w⁻¹] = q(w)[n]`, `[σ(x)] = x`. Every
factorisation is an **exact identity in `F`** — nothing is truncated to first
order — so

```text
[D(x)]  =  [D] + Σ_{i=0..4} L_i x_i                                    (*)
```

is an exact equation, which is what makes the literal probe of §1.2 a sharp
test rather than an approximation. The five results:

```text
L4 = w − 1
L3 = U⁻¹ − w                       (uses q(z) = q(tgt), i.e. D ∈ N)
L2 = 1 − U⁻¹R = 1 − h2 S h2⁻¹      (uses the slot identity U = R h2 S⁻¹h2⁻¹)
L1 = bridge (B − S)                bridge = h2 + U⁻¹h3
L0 = −( U⁻¹ + bridge · S · h1 ) (A − R)
```

The `h1` factor enters through the `S`-step alone:

```text
[δ_s] = (B − S) x_1 − q(B·Y·h1)[δ_r] ,   q(B Y h1) = B h1 R⁻¹ = S·q(h1)
```

— the conjugating factor is `S·q(h1)`, not `S`. `L1`–`L4` never see `h1` at
all, and `L2`/`L3`'s two spellings are forced by identities that hold by
construction, which is *why* only one column moved.

| column | shipped | exact | changed? |
|---|---|---|---|
| `L0` | `−(U⁻¹ + bridge·S)(A−R)` | `−(U⁻¹ + bridge·S·h1)(A−R)` | **YES** |
| `L1` | `bridge (B − S)` | identical | no |
| `L2` | `1 − h2 S h2⁻¹` | identical | no |
| `L3` | `U⁻¹ − w` | identical | no |
| `L4` | `w − 1` | identical | no |

> **W2j established only that column 0 was wrong and columns 1–4 clean on its
> six-vertex probe set. Widening the probe set to the whole radius-4 ball of
> `X = Q/⟨c⟩` (20 vertices) confirms it: columns 1–4 are exact on every chain
> and every vertex.**

### 1.2 The validation (`--mode opcheck`, all 67 chains)

Put `x_i = e_v` one column at a time, replay the recurrence literally in
`F(c,t)`, compare `relation_module(D(x))` with `[D] + L_i e_v`:

| | value |
|---|---:|
| chains | **67** |
| probe vertices (radius-4 ball of `X`) | **20** |
| literal checks per operator set | **6,700** |
| mismatches, **exact** operators | **0** |
| mismatches, shipped = deliberately re-broken `L0` | **1,180** |
| columns in which a re-broken mismatch occurs | **`{0}`** only |
| chains where the shipped `L0` is wrong | **59 / 67** |
| chains with `q(h1) = 1` (shipped `L0` correct) | 8 / 67 |

Controls, each able to fail and each fired:

| control | asserts | result |
|---|---|---|
| **C0 codex witness** | the corrected builder reproduces the codex certificate | defect `(21, 48, 0)`, 100/100 literal probes clean, and `exact == shipped` there because `H1 = ()` |
| **C1 re-broken `L0`** | the literal probe can reject an operator | fires on **59/59** chains with `q(h1) ≠ 1`, silent on **8/8** with `q(h1) = 1` — the control is not merely "on", it fires *exactly* where the theory says it must |
| **C2 identity with the shipped builder** | the re-broken column really is the shipped one | asserted group-ring-equal to `build_operators_general`'s output on every chain |

---

## 2. The literal cross-check, per chain (`--mode literal`, `--mode inf --sub liftlit`)

W2b–W2i all verified a layer-1 solution by recomputing `D + Σ L_i x_i` with
the same `L_i` that built the system. This mode re-tests every solution the
W2j way instead — `n_r = σ(x_r)`, replay (1.8), assert `R_can ∈ [N,N]`.

| | exact ops | shipped ops |
|---|---:|---:|
| chains (base window, `ρ ≤ 2`) | 67 | 67 |
| layer-1 solution found | **55** | 46 |
| …**literally verified in `F(c,t)`** | **55 / 55** | **22 / 46** |
| …literally **rejected** | 0 | **24** |
| W2h's constructive `Ω`-seeded lifts (23 infinite-index chains) | **21 solved, 21/21 literally verified** | 21 solved, **6 verified, 15 rejected** |

The 22 shipped solutions that survive are exactly characterised: 8 have
`q(h1) = 1`, and the other 14 have `x₀ = 0` — the defective column is
unused. So a shipped "verified solution" is a real solution **iff** it never
touched `L0` or the chain sets `q(h1) = 1`; nothing else survived.

The 55 also reproduce W2j §3's count exactly (55 of 67 chains solvable at
`ρ ≤ 2`), from an independent code path.

---

## 3. (b.1) W2b / W2f — the liveness sweep

`--mode sweep --k 1`: 67 chains × 81 gauge windows = **5,427 windows, all
decided**, per prime. The OLD column is W2f's own record; the shipped arm was
recomputed on **13** chains as a control and reproduced W2f's per-prime window
counts and live-window counts **exactly, 13/13**.

### 3.1 Chain-level and window-level

| | W2f (shipped `L0`) | **W2k (exact `L0`)** |
|---|---:|---:|
| live chains (mod 2, 3, 5) | 21 | **31** |
| live windows | 253 | **453** |
| windows solvable mod 2 | 539 | **820** |
| windows solvable mod 3 | 259 | **472** |
| windows solvable mod 5 | 253 | **461** |
| chains flipped dead → live | — | **10** |
| chains flipped live → dead | — | **0** |

The one-sidedness is expected and is a small consistency check in itself: the
corrected `L0` is the true column, and the shipped one was a *different*
operator, not a restriction of it — but every chain the wrong operator called
live is still live under the right one.

### 3.2 The live fraction by cap — W2f §3.1 restated

| cap | chains | W2f live | frac | **W2k live** | **frac** |
|---:|---:|---:|---:|---:|---:|
| 12 | 17 | 6 | 0.353 | **13** | **0.765** |
| 13 | 36 | 16 | 0.444 | **24** | **0.667** |
| 14 | 55 | 19 | 0.345 | **28** | **0.509** |
| 15 | 67 | 21 | 0.313 | **31** | **0.463** |

W2f's reading — *"stable-to-falling, a roughly constant one-third"* — is
**retracted**. The corrected profile falls monotonically from 0.77 to 0.46;
the level is roughly half, not a third, and the cap-13 bump is gone. The
falling shape survives; the number attached to it does not.

**W2b's headline moves with it: at cap 12 the live set is 13 of 17, not 6.**
The five non-witness live chains W2b lists are all still live; eight more join
them, including three of the five `S = TcTcttc` class members W2b reported as
`NOT_LIVE_AT_TESTED_WINDOWS`.

### 3.3 The five dead strata (W2f §4)

| stratum | predicate | chains | windows | **live chains** | mod 2 | **mod 3** | **mod 5** | status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| **S1** | `k1 ≥ 6` | 18 | 1,458 | **1** | 199 | **3** | **3** | **RETRACTED** |
| **S2** | `g ∉ {"", "TTc"}` | 22 | 1,782 | **1** | 199 | **3** | **3** | **RETRACTED** |
| **S3** | `p3 ≥ 4` | 19 | 1,539 | 0 | 101 | **0** | **0** | **HELD** |
| **S4** | `k3 ≥ 7` | 11 | 891 | 0 | 89 | **0** | **0** | **HELD** |
| **S5** | `k2 ≥ 7` | 6 | 486 | **1** | 2 | **2** | **2** | **RETRACTED** |

The two killers, in full:

```text
(tcTcTTTcttc, ctcTcTctc, tcTcTTct)          g = Tc    kills S1 and S2  (2 live windows)
(TTctcTctc, cTcttcTcTTctctc, TTctcTcTTcttct) g = ""   kills S5         (2 live windows)
```

`S3 ∪ S4` is 26 chains with **zero** live chains and **zero** windows solvable
mod 3 or mod 5 — the surviving dead set, down from W2f's union of 32.
Everything W2f §6.5 already said about *reading* such a stratum still applies
with more force: W2g/W2h prove `d = 1` for all 67 chains, so even `S3` and
`S4` are one-hop truncation artifacts, not module obstructions.

`S2` in particular was W2f §8's "single most decisive next question" and the
whole reason W2g existed. It is now not even a dead stratum.

### 3.4 Mod 5 is no longer binding at window level (W2f §3.2)

| claim | W2f | **W2k** |
|---|---|---|
| every window solvable mod 5 is solvable mod 2 and mod 3 | true, 5,427/5,427 | **FALSE** — 461 mod-5 windows vs 453 live; 8 exceptions on 4 chains |
| chain level `live_5 = live_all ⊆ live_3 ⊆ live_2` | 21 / 22 / 42 | **holds**, now 31 / 31 / 39 — mod 3 and mod 5 coincide |

W2f's practical advice ("report mod 5, say which") stands; its window-level
implication does not.

### 3.5 The abelianization is still inert (W2f §5)

The `t`-exponent map `φ : M → Z[x,x⁻¹]` is a `Z[Q]`-map, so
`solvable(full) ⇒ solvable(collapsed)` for any operators; what the correction
changes is the collapsed system itself:

```text
φ(L0) = −( x^(−e(U)) + bridge_x · x^(e(S)+e(h1)) )( x^e(A) − x^e(R) )
```

(W2f's closed form omitted `e(h1)`). Re-measured on **all 67 chains and all
5,427 windows** — W2f measured 26 chains, 2,106 windows: the collapsed system
is solvable mod 2, 3 and 5 at **5,427 / 5,427** windows, with **0** violations
of the predicted implication. `full_solvable = 453` here, matching §3.1's
independent count exactly.

> **The candidate mechanism is still ruled out, on 2.6× the evidence.**

---

## 4. (b.3) W2g — `d = 1` on the finite-index part

`--mode omega` (W2g's own code path, its controls included, fed exact
operators), all 67 chains in two slices:

| | W2g | **W2k** |
|---|---:|---:|
| `[Q:Γ] = 4` chains | 44 | **44** |
| `d = 1` at every window | 44 | **44** |
| chains with a death certificate | 0 | **0** |
| `d` values seen | `[1]` | `[1]` |
| C3 `omega_rows_direct` / C4 identities / C5 `L2,L3,L4` rows vanish | pass | **pass** |
| verdict | `NO_DEATH_CERTIFICATE_AND_PROVABLY_LIVE` | same |

**W2g's theorem HELD — and `--mode dsource` says why it was never at risk.**
Splitting `d` by which column supplies it:

| | value |
|---|---:|
| finite-index chains | 44 |
| `d = 1` from the **`L1` rows alone** | **44 / 44** |
| chains where the `L0` column's own gcd changed | 24 / 44 |
| `d` from the `L0` rows alone, at `k1 = 0` over the `(k2,k3)` box | **`{0, 1, 2}`** |
| `d` from the `L0` rows alone, scanning the `k1` axis too | **1 on 44 / 44** |
| `d` (combined) changed by the correction | **0 / 44** |

`L1 = bridge·(B − S)` contains no `h1`, so its `Ω`-rows are **literally the
same group-ring rows** before and after the correction. Since the `L1` rows
already have gcd 1 on every one of the 44 chains, `Σ_i L_i M = ker ε` follows
without ever reading `L0`. The `L0` column, by contrast, moved on 24 chains and
at the base `k1` its rows vanish identically (`gcd = 0`) on three of them — so
a version of W2g's theorem that had leaned on `L0` at a fixed window would have
been in real trouble. It did not. (Scanning the `k1` axis, which the corrected
`L0` now depends on and the shipped one did not, brings the `L0` gcd to 1 on
all 44 — so `L0` is not *useless*, merely not load-bearing.)

---

## 5. (b.2) W2e — the class-invariance refutation

### 5.1 The corrected transformation law

Under `S → S' = γSγ⁻¹` with `h2 → h2γ⁻¹`, `h3 → h3γ⁻¹` (so
`bridge' = bridge·γ⁻¹`), member 1 keeps its **own** `h1'`, and

```text
bridge' · S' · h1'  =  bridge · γ⁻¹ · γSγ⁻¹ · h1'  =  bridge · S · (γ⁻¹h1')
```

> **Corrected law.** `L0' = −( U⁻¹ + bridge·S·(γ⁻¹h1') )·d_r`, i.e. `L0` with
> the right factor `q(h1)` replaced by `q(γ⁻¹h1')`.
> `L1' = bridge(γ⁻¹B − Sγ⁻¹)`, `L2' = L2`, `L3' = L3`, `L4' = L4` — unchanged
> from W2e §4.1, since none of them sees `h1`.

Machine-verified on **5 / 5** class pairs. Measured on all five:
`q(h1) = 1` for member 0 and `q(γ⁻¹h1') = TTctcTTctc ≠ 1` for member 1, so the
alignment moves a factor W2e's law did not know existed — `L0` now carries a
*second* obstruction term beyond W2e's `E0`.

### 5.2 The obstruction and the intertwiner

`E1 := L1' − L1·γ⁻¹ = bridge(γ⁻¹B − Bγ⁻¹)` is **unchanged** by the correction
(`L1` is unchanged), and it is nonzero. So W2e's §4.3 argument — `L2'=L2`,
`L3'=L3`, `L4'=L4` force the common unit `u = 1`, but `L1' ≠ L1` — closes on
`L1` alone. `no_uniform_right_unit_intertwiner: true` on **5/5** pairs, probing
`u ∈ {1, γ, γ⁻¹}`. **W2e's theory verdict is not merely re-measured, it is
immune.**

### 5.3 The window-level comparison

| | W2e | **W2k** |
|---|---:|---:|
| aligned window pairs | 405 | 405 |
| **mismatches** | 161 | **142** |
| agreeing | 244 | **263** |
| pairs with a mismatch | 5 / 5 | **5 / 5** |
| member-0 live windows | — | 138 |
| member-1 live windows | — | 22 |

> **The window-level refutation SURVIVES.** The solvable-window set is still
> not carried across a `(R, cyc S, U)` class by the canonical alignment, on
> every one of the five class pairs.

Chain-level agreement, however, moves sharply: **1 of 5 → 4 of 5** class pairs
now agree on chain-level liveness (only `U = TcTTcttcTctc` still disagrees,
and by W2b doctrine its `NOT_LIVE` side is inconclusive). W2e's §0 "chain-level
liveness is a class invariant: **open**" stays open — but the evidence against
it has thinned to one pair.

---

## 6. (b.4)–(b.5) W2h and W2i

### 6.1 W2h's Lemma 5, corrected (`--mode inf --sub identity`)

Using `Γ h2 S h1 = Γ h2 h1` and `Γ U⁻¹h3 S h1 = Γ h3 h1`, the corrected
`Ω`-row of the `L0` column is the shipped one with **`h2 → h2·h1` and
`h3 → h3·h1`** in the four bridge terms:

```text
π(L0 e_v) = [ω(σ(R)·v)] + [ω(σ(h2h1 R)·v)] + [ω(σ(h3h1 R)·v)]
          − [ω(σ(A)·v)] − [ω(σ(h2h1 A)·v)] − [ω(σ(h3h1 A)·v)]
π(L1 e_v)   unchanged                π(L2) = π(L3) = π(L4) = 0
```

| | value |
|---|---:|
| chains | **67 / 67** |
| identity checks (`row_sigma` vs `row_direct`) | **25,460** |
| mismatches | **0** |
| `L2,L3,L4` row checks / nonvanishing | 38,190 / **0** |
| base-coset pinning `σ(R)=σ(U)=σ(w)=base` | 67 / 67 |
| corruption breaks identity / vanishing | fires 67 / 67 |
| **cross-control: the OLD Lemma 5 against the exact `L0`** | **fails, 316 / 440** — the corrected form is not vacuous |

### 6.2 W2h's margin law and lifts

| | W2h | **W2k** |
|---|---:|---:|
| infinite-index chains | 23 | 23 |
| `π(D)` in the row lattice over `Z` | 23 | **23** |
| witnesses re-multiplied out | 23 | **23** |
| `d_eff = 1` | 23 | **23** |
| margins seen (radii 10,12, align 10) | `{1,2,3,4,5,6,7,8}` ∪ `{1,2,3,5,9,11}` | **`{1,2,3,4,5}` ∪ `{1,2,3,5}`** |
| `coverage_depth_min` | 4 / 1 | **7 / 7** |
| explicit lifts, W2h's own settings | 21 of 23 | **21 of 23** |
| …**literally verified in `F(c,t)`** | not tested | **21 / 21** |

The margins **shrink** and the coverage front runs **deeper** with the exact
operators: the corrected `L0` covers more of `Z[Γ\Q]`. The margin law's status
is unchanged (**EVIDENCED**, not proved — `A = Z[Ω]₀` is still not a theorem),
but its evidence is better than W2h's.

One chain (`TTTctttcTTTcttc, cTTctttcTTctc, TTcTcttc`, `g = c`) misses at
radii 8–12 with `align 0` — **on both operator sets**, so it is the enumeration
radius, not the correction; at `--radii 14,16 --align 6` it lands with a
re-verified 10-term witness. Exactly W2h's own documented behaviour.

### 6.3 W2i — `d₂` and the `Ξ_Z` isomorphism

`--mode d2 --sub uniform` (Lemma 7 made effective: a finite loop over `P`, so
a statement about **every** displacement class), plus the sampled blocks:

| | W2i | **W2k** |
|---|---:|---:|
| finite-index chains | 44 | **44** |
| generic block `C₂ = Z[Γ\Q]/⟨L0,L1⟩ ≅ Z` | 44 | **44** |
| self-inverse blocks `≅ Z/2` over every fpf involution of `P` | 44 | **44** |
| concrete-vs-uniform mismatches | 0 / 1,936 | **0 / 1,936** |
| sampled blocks with `d₂ = 1` | 1,936 | **1,936** |
| blocks with an extra obstruction / torsion generators | 0 / 0 | **0 / 0** |
| layer-2 identity controls (`L_r^{(2)}` rows vanish; `Ξ_Z` kills them) | pass | **73,968 rows, 0 nonvanishing; 49,312 `Ξ` checks, 0 nonzero; 16,080 `Γ`-invariance checks, 0 failures** |
| detector fires on the synthetic doubled system | 44/44 | **22/22 chains, 528 blocks** |
| verdict | `D2_IS_1_FOR_EVERY_DISPLACEMENT_CLASS` | same |

> **Theorem (44 finite-index chains), re-established on the exact operators.**
> `Σ_r im L_r^{(2)} = ker(Ξ_Z)` on `Λ²M`, so `Ξ_Z : C₂ → W_Q` is an
> **isomorphism**.

The infinite-index half reproduces W2i §3.4's coverage-front picture
(12 chains at radii 6–10, `L2,L3,L4` rows vanishing 0, no torsion).

---

## 7. (b.6) W2j reconciles with zero change

`--mode theta`, all 67 chains: `build_operators_exact(...)` and
`theta_residual_evaluator.exact_operators(...)` are **equal as group-ring
elements, column for column, on 67/67 chains**. W2j derived its operator from
the same variation and this driver re-derived it independently; they agree.

Therefore **every number in W2j §§2–5 stands unchanged**: the codex
reproduction (4/4 parity classes), `Ξ_Z(Θ(F₀)) ≠ 0` on 55/55 chains, the
affine-quadratic law (213 held-out predictions), the mod-2 non-attainability
over the rank-2/4 sublattices, and the non-constancy of the mod-2 reduction on
24/24 windows. W2j's §5.4 line *"whether W2g/W2h/W2i's layer-1 and `d₂`
conclusions survive the `L0` correction — **OPEN**"* is what this note closes.

Independent corroboration: this driver's `--mode literal` found exact layer-1
solutions at `ρ ≤ 2` on **55 of 67** chains — W2j's number, from a different
solver path.

---

## 8. (c) THE RECONCILIATION TABLE

Every suspended claim, with the number that changed.

| # | note | claim | status | the number |
|---:|---|---|---|---|
| 1 | W2b | "at least **six** period-two baselines are live at layer 1" | **STRENGTHENED** | **6 → 13** of the 17 cap-12 chains |
| 2 | W2b | the five listed non-witness live chains are live | **HELD** | 5/5 still live |
| 3 | W2b | 11 chains `NOT_LIVE_AT_TESTED_WINDOWS` | **WEAKENED** | 11 → 4; seven were live all along |
| 4 | W2b | no defect is dead by augmentation | **HELD** | 0/5,427 windows |
| 5 | W2e | window-level: the alignment does **not** carry the solvable-window set | **HELD** | 161 → **142** mismatches / 405 pairs |
| 6 | W2e | closed forms `L0 … L4` and the transformation law | **CORRECTED, then HELD** | `L0` and `L0'` both gain a right factor (`q(h1)`, resp. `q(γ⁻¹h1')`); `L1`–`L4` unchanged; law verified 5/5 |
| 7 | W2e | no uniform right-unit intertwiner | **HELD (now immune)** | 5/5; the argument closes on `L1`, which did not change |
| 8 | W2e | chain-level class invariance: **open** | **still open, evidence thinned** | disagreeing class pairs 4/5 → **1/5** |
| 9 | W2f | live fractions 0.353 / 0.444 / 0.345 / 0.313 | **RETRACTED** | **0.765 / 0.667 / 0.509 / 0.463** |
| 10 | W2f | "the live fraction is a roughly constant one-third" | **RETRACTED** | monotone fall from 0.77 to 0.46 |
| 11 | W2f | 46 of 67 chains have zero solvable windows | **RETRACTED** | **36 of 67** |
| 12 | W2f | strata `S1`, `S2`, `S5` are dead mod 3 and mod 5 everywhere tested | **RETRACTED** | each now contains a live chain; `S2` (W2f §8's headline target) has 3 mod-3 and 3 mod-5 windows |
| 13 | W2f | strata `S3` (`p3≥4`), `S4` (`k3≥7`) dead mod 3 and mod 5 | **HELD** | 0 live, 0/1,539 and 0/891 windows |
| 14 | W2f | union of the five strata = 32 chains, no live one | **RETRACTED** | 32 chains, **2 live**; the surviving dead union is `S3∪S4` = 26 chains |
| 15 | W2f | every window solvable mod 5 is solvable mod 2 and mod 3 | **RETRACTED** | 8 counterexamples on 4 chains (461 mod-5 vs 453 live) |
| 16 | W2f | chain-level `live_5 = live_all ⊆ live_3 ⊆ live_2` | **HELD** | 21/22/42 → **31/31/39** |
| 17 | W2f | the `t`-exponent abelianization is inert | **HELD, STRENGTHENED** | 2,106 windows / 26 chains → **5,427 windows / 67 chains**, 0 violations |
| 18 | W2f | no `≤ 4`-coordinate subset determines liveness | **not re-run** | the live set changed, so W2f's exhaustive search is stale; flagged, not re-decided |
| 19 | W2g | `d = 1` at every window of all 44 finite-index chains | **HELD** | 44/44, `d` values `{1}` |
| 20 | W2g | `Σ_i L_i M = ker ε` ⇒ every window solvable over `Z` | **HELD** | 44/44 |
| 21 | W2g | no death certificate on the g-stratum | **HELD** | 0/44 |
| 22 | W2g | the 27 explicit integral lifts at "dead" windows | **HELD**, and now literally checked | the corrected analogues verify in `F(c,t)`, not only through the operators |
| 23 | W2g | `ζ2, ζ3` act trivially on `Γ\Q`, so `d` is constant in `(k2,k3)`, and `h0,h1` do not occur in any `L_i` | **HELD, with one clause corrected** | the `ζ` computation is unchanged; but `L0` **does** now depend on `k1`, so that half of §2.1's "the `k0,k1` axes need no argument" is only true because `d = 1` is decided by the `L1` rows. Measured over `k1 ∈ {−1,0,1}`: the `L0` gcd is 1 on 44/44 anyway |
| 24 | W2h | Lemma 5's row formula for `π(L0 e_v)` | **CORRECTED, then HELD** | `h2 → h2h1`, `h3 → h3h1`; 25,460 checks, 0 mismatches; old form fails 316/440 |
| 25 | W2h | `π(D)` in the lattice ⇒ layer-1 solvable over `Z`, 23/23 | **HELD** | 23/23 |
| 26 | W2h | explicit `x` on 22 of 23 chains | **HELD** | 21/23 at the published settings, both before and after |
| 27 | W2h | the margin law (`A = Z[Ω]₀`), EVIDENCED | **HELD, STRENGTHENED** | margins `≤ 11` → `≤ 5`; `coverage_depth_min` 1 → **7** |
| 28 | W2h | "layer 1 obstructs nothing on the whole census" | **HELD** | 67/67 |
| 29 | W2i | `A₂` free, no layer-2 2-torsion | **HELD** | 0 torsion generators, 44/44 |
| 30 | W2i | `d₂ = 1` on 1,936 sampled blocks | **HELD** | 1,936/1,936 |
| 31 | W2i | `d₂ = 1` at **every** displacement class ⇒ `Ξ_Z : C₂ ≅ W_Q` | **HELD** | 44/44, 0/1,936 uniform-vs-concrete mismatches |
| 32 | W2i | (3.16) made effective: `Ξ_Z` kills every `L_r^{(2)}` image | **HELD** | 49,312 checks, 0 nonzero |
| 33 | W2i | infinite-index layer 2: coverage front, no obstruction | **HELD** | reproduced at radii 6–10 |
| 34 | W2j | `Ξ_Z(Θ(F₀)) ≠ 0` on 55/55 chains, and everything in §§2–5 | **HELD, unchanged** | the operators are byte-identical, 67/67 |
| 35 | W2b–W2i | "`x` is a VERIFIED layer-1 solution" | **RETRACTED where it ran through `L0`** | 24 of 46 shipped solutions are not solutions; 55/55 corrected ones are |

**The plainly-stated retractions.** W2f's headline — *"46 of 67 chains have
zero solvable windows; five parameter strata are dead mod 3 and mod 5 at every
tested window"* — is **wrong as stated**. The correct numbers are 36 chains and
two strata. W2f §8's "single most decisive next question", which asked for a
quotient killing `S2`, was aimed at a stratum that is not dead. And W2b's
"**at least six**" understated its own result by more than a factor of two.
None of this touches W2g/W2h/W2i, whose conclusions are unchanged.

---

## 9. (d) VERDICT — where the programme stands after the correction

| item | verdict | status |
|---|---|---|
| **Layer 1 is obstruction-free on the whole cap-15 census** — `Σ_i L_i M = ker ε`, every window solvable over `Z` | `d = 1` on 44/44 finite-index chains (an exact finite computation, immune to the correction via the `L1` rows); `d_eff = 1` on 23/23 infinite-index chains with re-multiplied witnesses | **PROVED** (44) / **EVIDENCED** (23, margin law not a theorem) |
| **The corrected operator calculus** — `[D(x)] = [D] + Σ L_i x_i` with the five columns of §1.1 | 6,700 literal free-group checks per operator set, 0 mismatches, 67/67 chains; re-broken control fires exactly on the 59 | **PROVED** |
| **`Ξ_Z : C₂ → W_Q` is an isomorphism** | `d₂ = 1` at every displacement class, 44/44 finite-index chains, uniform loop over `P` plus 1,936 concrete blocks | **PROVED** (44) / **EVIDENCED** (23) |
| **The layer-2 question is exactly `Ξ_Z(Θ) = 0`** | follows from the previous line, and is conditional on (3.1) `N` free on the Schreier basis and (3.5) the layer-2 variation identity — both unchanged by this note, (3.5) tested not assumed | **PROVED conditional on (3.1)+(3.5)** |
| W2f's five dead strata as candidate module obstructions | three of five refuted outright; the other two are one-hop truncation artifacts by W2g/W2h anyway | **RETRACTED** |
| W2f's live-fraction profile and the mod-5 window implication | superseded by §3 | **RETRACTED** |
| W2e's window-level refutation of the collapse lemma | 142/405, corrected law verified | **PROVED** for the alignment |
| Any layer-1 *death* certificate anywhere on the census | none exists on the 44; none found on the 23 | **RETRACTED as a possibility** on the finite-index part |
| Anything about the free-group depth-four class, the bridge, AK(3), stable AC, or AC | — | **no claim** |

**Reading.** The correction cost W2f its headline and gave W2b a bigger one;
it left the *structural* results — W2g's `d = 1`, W2h's coverage, W2i's `d₂ = 1`
and the `Ξ_Z` isomorphism — standing, and in two cases (W2h's margins, W2f's
abelianization) on better evidence than before. That asymmetry is not luck: the
liveness sweep is a computation *about a particular `L0`*, while the structural
theorems all reduce to the `L1` column and to identities (`L2 = 1 − U⁻¹R`,
`L3 + L4 = U⁻¹ − 1`, `X, U, w ∈ Γ`) that no perturbation of `L0` can reach.
Layer 1 remains blind, layer 2 remains exactly `Ξ_Z(Θ) = 0`, and W2j's answer
to *that* question is unaffected.

---

## 10. Scope and nonclaims

- **The correction is asserted about `L0` only**, and columns 1–4 are asserted
  exact on a 20-vertex probe set over all 67 chains — a finite check, not a
  proof for all `v ∈ X`. The derivation in `corrected_operators.py` is the
  proof; the probes are its independent test.
- **`K = 1`, cap 15, one terminal conjugator per chain** — every one of these
  is a ceiling that can only under-report liveness, exactly as in W2f. The
  10 dead→live flips are therefore a lower bound on the movement.
- **W2f §3.3 (no small determining coordinate set) was not re-run.** Its
  exhaustive search is over a live set that has changed; the claim is flagged
  stale, not re-decided.
- **The margin law is still EVIDENCED, not proved.** `A = Z[Ω]₀` on the 23
  infinite-index chains rests on the coverage front advancing with the radius.
- **Everything about layer 2 stays conditional on (3.1) and (3.5)**, unchanged
  from W2i/W2j.
- **Nothing existing was modified.** `build_operators_general` still ships as
  it was; `corrected_operators.build_operators_exact` supersedes it, and the
  driver rebinds the operator source at run time so that every downstream mode
  is the published checker's own code path with its own controls.
- **No claim about the free-group depth-four class, the bridge, AK(3), stable
  AC, or AC.**

---

## 11. Reproduce

Each command is its own guarded foreground run (`--timeout-seconds ≤ 55`).
`--mode sweep`, `--mode literal`, `--mode abelian` and `--mode inf --sub
liftlit` are resumable: re-run with the same `--json` until the summary stops
growing.

```bash
G="python3 scripts/run_proof_guarded.py --timeout-seconds 55 -- python3"
W=fable/proofs/checkers/w2k_reverify.py
O=fable/proofs/checkers/out

# (a) the corrected builder
$G fable/proofs/checkers/corrected_operators.py            # codex-witness control
$G $W --mode opcheck --chains 0:34  --json $O/w2k_opcheck_a.json
$G $W --mode opcheck --chains 34:67 --json $O/w2k_opcheck_b.json
$G $W --mode theta --json $O/w2k_theta_reconcile.json

# (b.1) W2b / W2f
for i in $(seq 14); do $G $W --mode sweep --run-seconds 40 --shipped-control 1 \
                            --json $O/w2k_sweep.json; done
for i in $(seq 6);  do $G $W --mode abelian --k 1 --run-seconds 42 \
                            --json $O/w2k_abelian.json; done

# the literal cross-check
for i in $(seq 5);  do $G $W --mode literal --run-seconds 42 \
                            --json $O/w2k_literal.json; done

# (b.2) W2e
$G $W --mode invariance --json $O/w2k_invariance.json

# (b.3) W2g
$G $W --mode omega --chains 0:34  --json $O/w2k_omega_a.json
$G $W --mode omega --chains 34:67 --json $O/w2k_omega_b.json
$G $W --mode dsource --json $O/w2k_dsource.json

# (b.4) W2h
$G $W --mode inf --sub identity --chains 0:34  --json $O/w2k_inf_identity_a.json
$G $W --mode inf --sub identity --chains 34:67 --json $O/w2k_inf_identity_b.json
$G $W --mode inf --sub image --chains 0:12  --radii 10,12 --align 10 \
      --json $O/w2k_inf_image_a.json
$G $W --mode inf --sub image --chains 12:23 --radii 10,12 --align 10 \
      --json $O/w2k_inf_image_b.json
$G $W --mode inf --sub lift --rho 2 --resid-rho 4 --k 0 --chains 0:9 \
      --radii 12 --align 10 --json $O/w2k_inf_lift_a.json      # + 9:16, 16:23
for i in $(seq 5); do $G $W --mode inf --sub liftlit --rho 2 --resid-rho 4 \
      --radii 12 --align 10 --run-seconds 40 --json $O/w2k_inf_liftlit.json; done

# (b.5) W2i
$G $W --mode d2 --sub uniform --zmax 44 --zk 3 --zn 2 --json $O/w2k_d2_uniform.json
$G $W --mode d2 --sub d2 --chains 0:22  --zmax 200 --zk 3 --zn 2 --radius 6 \
      --json $O/w2k_d2_a.json                                  # + 22:44
$G $W --mode d2 --sub identity --chains 0:34 --radius 4 --zmax 8 --zk 2 --zn 2 \
      --json $O/w2k_d2_identity_a.json                         # + 34:67
$G $W --mode d2 --sub probe --chains 0:22 --zmax 24 --zk 3 --zn 2 \
      --json $O/w2k_d2_probe_a.json
$G $W --mode d2 --sub inf --chains 0:12 --radii 6,7,8,9,10 --zmax 0 \
      --json $O/w2k_d2_inf_a.json
```

---

## 12. The single most decisive next question

> **Is `0 ∈ image(Ξ_Z ∘ Θ)` over the *complete* balanced source-pair space
> `H_fin`, for even one census baseline?**

W2j's §8 asked this second, behind the `L0` repair. The repair is done and it
did not move `Ξ_Z`, `Θ`, `C₂` or `W_Q` by one coefficient — so this is now the
only question left in the W2 chain that can change the answer. The programme's
state is: layer 1 is blind everywhere (proved on 44, evidenced on 23), layer 2
is *exactly* `Ξ_Z(Θ) = 0` (proved on 44, conditional on (3.1)+(3.5)), the value
`Ξ_Z(Θ(F₀))` is nonzero at every one of 55 baselines, and it provably cannot be
forced to zero on any rank-2 or rank-4 window tested — while the one cheap
uniform obstruction (a constant mod-2 parity) provably does not exist.

Two disciplines this note adds to W2j's own. First, **the newly live chains
are the place to ask it.** Ten chains that looked dead are live, three of them
in strata the programme had written off; each carries an `H_fin` nobody has
enumerated. Second, **do not verify the answer through the operators.**
`--mode literal` and `--mode inf --sub liftlit` show 24 of 46 published
"verified solutions" failing the free-group test; any future claim about
`H_fin` must ship with the same replay.
