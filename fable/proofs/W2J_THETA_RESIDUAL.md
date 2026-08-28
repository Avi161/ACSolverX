# W2j: `Ξ_Z(Θ(F))` beyond the codex witness — evaluated, never zero, and no obstruction

Date: 2026-08-28 · Checker: `checkers/theta_residual_evaluator.py`
(imports `infinite_index_liveness.py`, `g_stratum_death.py`,
`period_two_parametric_solvability.py`, `period_two_baseline_liveness.py` and
the two codex certificates `depth4_period_two_lift_certificate.py` /
`depth4_period_two_degree_two_escape_certificate.py`, all unmodified; guarded
foreground runs, one at a time.)
Run records: `checkers/out/w2j_summary.json`, `w2j_validate.json`,
`w2j_opcheck_a.json` / `_b` / `_c`, `w2j_theta_r2_0_12.json` … `_60_67.json`,
`w2j_family_0_12.json` / `_12_25` / `_25_36` / `_36_52` / `_52_67`,
`w2j_family_rank4.json`, `w2j_family_witness_codexdirs.json`.

Answers `W2I_LAYER2_D2.md` §7: *"Compute `Ξ_Z(Θ(F))` for a census baseline
other than the codex witness, and ask whether the balanced-source family
`F ↦ Ξ_Z(Θ(F))` can hit zero."*

---

## 0. Verdict

| question | answer | status |
|---|---|---|
| Does a `Θ` evaluator for arbitrary chains exist and agree with the codex one? | **Yes.** The general path reproduces the codex escape certificate *exactly* on all four parity classes — residual lengths `[82, 442, 678, 614]`, Schreier lengths `[24, 104, 212, 178]`, obstruction bits `(1,1) (0,1) (0,1) (1,0)` — and the wedge vectors are identical dicts, because `esc.schreier_word` / `esc.degree_two` are **imported, not forked**. | **VERIFIED** (§2.1) |
| Is `Ξ_Z(Θ(F₀))` zero for any census baseline at its layer-1 solution? | **No. 0 / 55.** Fifty-five of the 67 chains got an exact layer-1 solution at ρ ≤ 2; every one has `Ξ_Z(Θ) ≠ 0`, with the **free** part nonzero on 55/55 and the `Z/2` part nonzero on 30/55. | **computed** (§3) |
| Can `F` be moved to make it zero? | **Not on any sublattice tested.** On 24 chains at rank 2, on 2 chains at rank 4, and on the codex witness's own rank-2 kernel, `n ↦ Ξ_Z(Θ(x + Σ n_j F_j))` is verified affine-quadratic and **misses 0 on the whole lattice `Z^m`** (decided completely by the 2^m mod-2 classes, not by a box search). | **complete over those sublattices** (§4) |
| Is that an obstruction? | **NO — and this note says so loudly.** Every statement is over a rank-2/4 sublattice of an infinite-rank `H_fin`. Worse for the obstruction reading: the mod-2 map is **non-constant on 24/24 windows**, so the one window-independent invariant that could have been proved (a constant parity) provably **does not exist** on these families. | **§5.2** |
| Anything else fall out? | **Yes, and it is the most consequential item here.** `build_operators_general`'s `L0` column is **wrong on 59 of the 67 chains** (every chain with `h1 ≠ 1`). Found and pinned by the literal free-group control, 354 mismatches over 2,010 probes, all in column 0. | **PROVED** (§1) |

---

## 1. The `L0` defect — found first, because everything else needs it

### 1.1 What is wrong

`period_two_baseline_liveness.build_operators_general` (used by W2b, W2e,
W2f, W2g, W2h and, through `layer2_d2_invariant.py`, by W2i) builds the `x_0`
column as

```text
L0 = -U^-1 (A - R)  +  bridge * (-S)(A - R) ,     bridge = h2 + U^-1 h3
```

The exact variation of (1.8) under `h_1(F) = σ(x_1) h_1` gives, for the class
of the perturbation of `S`,

```text
[δ_S] = (B - S) x_1  -  (S·q(h1)) [δ_R]
```

— the conjugating factor is `B h1 R^-1 = S·q(h1)`, **not** `S`. The two agree
exactly when `q(h1) = 1`. That is the codex witness's case (`H1 = ()` in
`depth4_period_two_lift_certificate.py`), which is why the codex certificate is
correct and the generalisation silently is not.

### 1.2 How it was caught, and why it could not have been caught by the
existing controls

Every layer-1 "verified solution" in W2g/W2h is verified *through the same
operators* (`verify(defect, ops, x)` recomputes `D + Σ L_i x_i` with the same
`L_i`), so a wrong `L_i` is self-consistent and every control stays green.
The independent path is the free group itself: put `n_r = σ(x_r)`, replay
(1.8) literally, and ask whether the residual lands in `[N,N]`. It does not.

`--mode opcheck`, all 67 chains, six probe vertices × five columns:

| | value |
|---|---:|
| probe checks (per operator set) | **2,010** |
| mismatches, **shipped** operators | **354** |
| columns in which a shipped mismatch occurs | **`{0}`** only |
| chains where the shipped `L0` is wrong | **59 / 67** |
| chains with `q(h1) = 1` (shipped `L0` correct) | 8 / 67 |
| mismatches, **exact** operators (`exact_operators`) | **0** |

On a chain with `q(h1) ≠ 1`, a layer-1 solution obtained from the shipped
operators produces a literal residual with a *nonzero* relation-module image —
i.e. it is **not** a layer-1 solution at all. With the exact `L0` the residual
is in `[N,N]` on every chain, every time.

### 1.3 Scope of the consequence — stated, not assessed

This checker does not modify any existing file and does not re-run W2b–W2i.
What is true is only this: **any layer-1 statement of W2b/W2e/W2f/W2g/W2h/W2i
that passed through the `L0` column on a chain with `q(h1) ≠ 1` rests on the
wrong operator and needs re-checking.** That plausibly includes W2g's `d = 1`
/ `image = ker ε`, W2h's margin law, and W2i's `d₂ = 1` — all of which use the
`L0` row (and, in W2h/W2i, the `sigma_terms` shortcut derived from it). It
plausibly does **not** include the `L2/L3/L4` structure (Lemmas 1–2, the
telescoping, `I_Γ`), which never touches `L0`. Deciding which conclusions
survive is a separate task and is **not claimed here in either direction**.

---

## 2. The evaluator

### 2.1 What it computes, exactly

For a chain `(R,S,U)`, target conjugator `g`, conjugator tuple
`h = (h0,h1,h2,h3,g)` and correction `x ∈ M^5`:

```text
n_r      = σ(x_r) = Π_v r_v^{x_r(v)}        (1.5), lift.lift_module_vector
h_r(x)   = n_r h_r                           (1.7)
R,S,U,Z  = the literal recurrence            (1.8)  in F(c,t)
R_can(x) = Z · (n_4 (g t g^-1) n_4^-1)^-1    (1.9)/(1.11)
           — asserted in [N,N] by lift.relation_module(R_can) == {}
Θ(x)     = [R_can(x)] ∈ Λ²M                  (3.1)/(3.2)
           = esc.degree_two(esc.schreier_word(R_can))     [imported verbatim]
Ξ_Z(Θ)   ∈ ⊕_{𝒟₂} Z ⊕ ⊕_{𝒟₁} Z/2            (3.15a)/(3.15b)
```

`Ξ_Z` is implemented directly from (3.15b): `e_{v1} ∧ e_{v2}` goes to the
double coset `D = H v1^{-1} v2 H`, oriented by comparing the shortlex
representatives of `D` and `D^{-1}` — `±1` on a free coordinate, and a `Z/2`
coordinate exactly when `D = D^{-1}` (3.15c).

`Θ` and `Ξ_Z` are **not** derived from layer-1 data. They are functions of the
literal free-group residual only. That is what makes them independent of the
`L0` defect above: `L0` decides *which* `x` is a layer-1 solution, and the
literal `[N,N]` test then re-decides it from scratch.

### 2.2 Controls (each fires; a failure sets exit 2 and voids the run)

| control | asserts | result |
|---|---|---|
| **K1** fixed-`h` witness | the imported lifting calculus is the codex one | defect `(21, 48, 0)` on every run |
| **K2** codex reproduction | the general path *is* the codex evaluator | residual lengths, Schreier lengths and the two obstruction bits all match on **4/4** parity classes; wedge vectors identical |
| **K3a** `Θ([r_a,r_b]) = e_a ∧ e_b` | the `γ₂/γ₃ ≅ Λ²M` identification (3.1) | **30/30** |
| **K3b** `Θ(w₁w₂) = Θ(w₁)+Θ(w₂)` on `[N,N]` | `Θ` is the homomorphism it is claimed to be | **64/64** |
| **K3c** `Θ(gwg^{-1}) = g·Θ(w)` | the diagonal `Q`-action (3.4) | **72/72** |
| **K3d** `Θ = 0` on `[[N,N],N]` | the quotient is by `γ₃N`, not something coarser | **24/24** |
| **K4a** `Ξ_Z(g·θ) = Ξ_Z(θ)` | `Ξ_Z` is the coinvariant map | **60/60** |
| **K4b** `Ξ_Z(L_r^{(2)} Y) = 0` | **(3.16) made effective on the real operators**, not assumed | **60/60**, on the actual `L_r` of real chains |
| **K4c** corruption of `L_r` breaks K4b | K4b is not vacuous | fires **60/60** |
| **K5** corrupted `x` leaves `[N,N]` | the literal layer-1 test can fail | fires **18/18** chains tested |
| **K6** every operator column vs the literal residual | the whole operator calculus | exact ops **0 / 2,010** mismatches (§1.2) |
| **K7** held-out prediction of the quadratic fit | `Θ` really is affine-quadratic in `F` | **170/170** (rank 2) + 32/32 (rank 4) + 11/11 (witness) |
| **K8** mod-2 periodicity | `G(n) mod 2` depends only on `n mod 2` | **170/170** |

---

## 3. (b) `Ξ_Z(Θ(F₀))` per chain

`--mode theta --rhos 2`, window `(0,0,0,0)`, all 67 census chains, exact
operators, each solution re-verified literally in the free group:

| | value |
|---|---:|
| chains | **67** |
| exact layer-1 solution found at ρ ≤ 2, `R_can ∈ [N,N]` | **55** |
| no solution at ρ ≤ 2 (truncation, *not* a death claim) | 12 |
| **`Ξ_Z(Θ) = 0`** | **0 / 55** |
| `Ξ_Z(Θ) ≠ 0` | **55 / 55** |
| … with the **free** (`𝒟₂`, `Z`) part nonzero | **55 / 55** |
| … with the **torsion** (`𝒟₁`, `Z/2`) part nonzero | **30 / 55** |
| free-coordinate support, min … max | 1 … 138 |
| wedge terms of `Θ`, min … max | 2 … 469 |
| longest literal residual `R_can` | 1,344 letters |
| K5 corruption controls fired | 18 / 18 |

The codex witness itself (`--mode validate`, at `CODEX_H` and the codex
`CORRECTION`) has the smallest defect on the census:

```text
Ξ_Z(Θ(x_codex))  =  −1 · z_{TcTct}        (one free coordinate, no torsion)
```

and its three sibling parity classes have 37, 50 and 65 nonzero free
coordinates plus 3, 1 and 3 torsion coordinates respectively.

**Reading.** For the 44 finite-index chains, W2i §3.3 makes `Ξ_Z(Θ) = 0`
*necessary and sufficient* for the layer-2 equation (3.8) — conditional on
(3.5). So for those, this table says: at the particular layer-1 solution
found, the layer-2 lift does not exist. For the other 23 it is the source's
necessary condition (3.18), and the same conclusion follows a fortiori. What
it does **not** say is anything about other `F`; that is §4.

---

## 4. (c) Varying `F` over the affine family

### 4.1 The family, and why it is a lattice

Layer-1 solutions are `x + F` with `F ∈ H_fin = {F : Σ_r L_r F_r = 0}`
(source (1.3)). Directions are generated basis-free, in two layers:

* **source-moving directions.** A single source column is never in
  `im L2 + im L3 + im L4`, so a column scan alone finds none. The right level
  is `Ω = Γ\Q/⟨c⟩`: by W2g's Lemma 2, `ker(π : M → Z[Ω])` is exactly
  `L2M + L3M + L4M`, so a source *combination* with vanishing `Ω`-row is
  finishable by the telescoping operators alone. Those combinations are the
  linear dependencies among the `Ω`-rows of the source columns — one more
  Hermite echelon. The `Ω`-rows are read straight off the operators this
  checker builds (`IL.row_direct`), never off the `sigma_terms` shortcut
  (which encodes the defective `L0`).
* **telescoping directions.** Dependent columns of the hop expansion.

Every direction is re-verified to satisfy `Σ_r L_r F_r = 0` exactly with the
unmodified `apply_operator`; one that fails is dropped.

### 4.2 The quadratic law, machine-verified

`G(n) := Ξ̃(Θ(x + Σ_j n_j F_j))` in the raw `Ξ_Z` coordinates (free part
integral; the self-inverse part kept integral for the fit and reduced mod 2
only for the verdict) is fitted as a degree-≤2 integer polynomial from
`G(0)`, `G(e_j)`, `G(2e_j)`, `G(e_j+e_k)`, then **predicted** at held-out
points including `n_j = −1`, `n_j = 3` and random `n ∈ [−2,3]^m`:

| | rank 2 sweep | rank 4 | codex witness kernel |
|---|---:|---:|---:|
| chains | 24 | 2 | 1 |
| held-out predictions | **170** | **32** | **11** |
| agreeing | **170** | **32** | **11** |
| `mod 2` periodicity checks / ok | **170 / 170** | 32 / 32 | 11 / 11 |

So `Θ` **is** affine-quadratic in `F` — verified, on real families, not
assumed from (3.2).

### 4.3 Attainability of 0 — complete over each sublattice

Because `G` is a degree-≤2 integer polynomial, `G(n) mod 2` factors through
`(Z/2)^m` (shifting `n_j` by 2 changes `G` by `2ℓ_j + q_{jj}(4n_j+4) + 2Σ…`,
even in every coordinate). Enumerating the `2^m` classes therefore decides
`0 ∈ image(G)` over **all of `Z^m`**, not over a box.

| | value |
|---|---:|
| chains where the family analysis completed (rank 2) | **24** |
| … `mod 2` classes with `Ξ_Z(Θ) ≡ 0` | **0** |
| … therefore `Ξ_Z(Θ(x+F)) ≠ 0` for **every** `F` in that rank-2 lattice | **24 / 24** |
| rank-4 lattices (chains 0, 1) — 16 classes each, vanishing | **0 / 16**, twice |
| codex witness on **its own** rank-2 kernel (`k₀`, `k₁` of the escape certificate) — 4 classes, vanishing | **0 / 4** |
| **families whose `mod 2` value is non-constant** | **24 / 24** (rank 2), 16 distinct values at rank 4, 4 at rank 2 for the witness |
| chains skipped (direction search or fit over the per-chain wall budget) | 21 |
| chains not attempted (run budget) | 14 |
| chains with no layer-1 solution at ρ ≤ 2 | 8 |

The witness line is a small strengthening of the codex's own result: the
escape certificate shows the four **parity classes** `{0,1}²` all carry a
nonzero coarse obstruction; the same statement now holds for the whole lattice
`Z²`, in the *complete* invariant `Ξ_Z` rather than the two tracked bits.

---

## 5. What it means

### 5.1 The positive content

Combining with W2i §3.3 (conditional on (3.5)): for each of the 24 chains
where the family analysis completed, **no first-layer solution in the tested
sublattice admits a second-layer lift** — the layer-2 equation (3.8) has no
solution there, and by the isomorphism `Ξ_Z : C₂ ≅ W_Q` nothing finer than
`Ξ_Z` could have said otherwise. The layer-2 defect is not merely nonzero in
some shadow; it is nonzero in the complete class.

### 5.2 Why this is **not** an obstruction, stated as forcefully as possible

Three reasons, any one of which is fatal to an obstruction claim:

1. **`H_fin` has infinite rank; the windows have rank 2 and 4.** Section 3.2
   of the source is explicit that "a global lift theorem or obstruction must
   be expressed on the complete balanced source-pair space, not on a bounded
   list of previously found directions". Every nonattainability statement here
   is bounded in exactly that way. This lane has been bitten by precisely this
   before (*"a dead stratum in a truncated support is a statement about the
   truncation"*, `LESSONS.md`): W2f's five "dead" strata were killed by the
   one-hop truncation, not by the module.
2. **The one window-independent invariant that would have worked provably does
   not exist.** If the `mod 2` reduction of `F ↦ Ξ_Z(Θ(F))` were *constant* on
   the family, the parity of the base value would obstruct the whole affine
   family at once — a genuine theorem, since `2 ×` quadratic and the linear
   shifts vanish mod 2. It is measured **non-constant on 24/24 windows** (and
   takes all 16 values on both rank-4 windows). So this route to an
   obstruction is closed by the data, not merely unproven.
3. **Coverage.** 24 of 67 chains completed the family analysis; 43 did not
   (21 over the per-chain wall budget, 14 not attempted, 8 with no layer-1
   solution at ρ ≤ 2). A statement about 24 windows on 24 chains is not a
   statement about the census.

### 5.3 The verdict, on W2j's own tree

Branch **(iii) — mixed / undecided, with a uniform empirical signal.** Not
(i): no baseline attained 0, so the period-two quotient is *not* shown blind
through layer 2. Not (ii): no window-independent invariant was found, and the
natural candidate is disproved (§5.2.2), so no baseline is shown obstructed.

### 5.4 Status ledger

| claim | status |
|---|---|
| the general `Θ` evaluator reproduces the codex escape certificate exactly | **VERIFIED** (4/4 classes, identical wedge vectors) |
| `Θ` is the `γ₂N/γ₃N ≅ Λ²M` class, `Q`-equivariantly, and kills `γ₃N` | **machine-verified** (30 + 64 + 72 + 24 checks, 0 failures) |
| `Ξ_Z` is the coinvariant map of (3.15b) and kills every `L_r^{(2)}` image | **machine-verified** on real operators (60 + 60), corruption fires 60/60 |
| `build_operators_general`'s `L0` is wrong iff `q(h1) ≠ 1`; 59/67 chains | **PROVED** (354/2,010 literal mismatches, all in column 0; exact ops 0/2,010) |
| `Ξ_Z(Θ(F₀)) ≠ 0` at an exact layer-1 solution, 55 chains | **computed**, each re-verified literally in `F(c,t)` |
| `Θ` is affine-quadratic in `F` on the tested families | **machine-verified** (213 held-out predictions, 0 disagreements) |
| `Ξ_Z(Θ)` misses 0 on the whole rank-2 (24 chains) / rank-4 (2 chains) sublattice, and on the codex witness's own rank-2 kernel | **complete over those sublattices** (mod-2 enumeration, not a box) |
| the `mod 2` reduction is **non-constant** on every tested family ⇒ no parity obstruction | **PROVED** on those families |
| any baseline's *whole* lift family cannot attain 0 | **NOT CLAIMED — open** |
| the period-two quotient is blind through layer 2 | **NOT CLAIMED — refuted for the tested windows** |
| whether W2g/W2h/W2i's layer-1 and `d₂` conclusions survive the `L0` correction | **OPEN — not assessed here** |
| anything about the free-group depth-four class, the bridge, AK(3), stable AC, or AC | **no claim** |

---

## 6. Scope and nonclaims

- **Everything that reads `Ξ_Z(Θ) = 0` as "layer 2 is solvable" is conditional
  on (3.5)** — the asserted variation identity giving `L_r^{(2)}` the same
  coefficients `a_{r,g}` as `L_r` — and, through W2i §3.3, on that note's
  `d₂ = 1`. `Ξ_Z(Θ(F))` itself is unconditional: it is a function of the
  literal free-group residual, and the only place (3.5) enters this checker is
  control K4b, where it is *tested* on the real operators, not assumed.
- **Everything is also conditional on (3.1)** (`N` free on the Schreier basis
  `(r_v)`), which is what makes `esc.schreier_word` a rewriting into a free
  basis and `esc.degree_two` the `γ₂/γ₃` class.
- **The `L0` correction is asserted only about `L0`.** This note does not
  claim which downstream W2b–W2i conclusions survive it, and does not modify
  any existing file.
- **`ρ ≤ 2` is a truncation.** "No layer-1 solution at ρ ≤ 2" on 12 chains is
  a statement about the hop expansion, never a death certificate. W2g/W2h
  found solutions on those chains by other routes (Ω-seeded lifts) — through
  the defective `L0`, so those are exactly the ones needing rework.
- **The sublattices are sublattices.** "Zero unattainable" always means "on
  the lattice spanned by the produced directions", which has rank 2 or 4
  inside an infinite-rank `H_fin`. It is *complete over that lattice* — the
  mod-2 argument is not a bounded search — and *bounded in the lattice*.
- **The wall budgets are visible in the records.** Chains marked
  `SKIPPED_TIME_BUDGET_*` / `NOT_ATTEMPTED_RUN_BUDGET` carry no verdict.
- **No claim about the free-group depth-four class, the bridge, AK(3), stable
  AC, or AC.** This is one layer of one quotient of one signature.

---

## 7. Reproduce

Each command is its own guarded foreground run (`--timeout-seconds ≤ 60`).

```bash
G="python3 scripts/run_proof_guarded.py --timeout-seconds 55 -- python3"
E=fable/proofs/checkers/theta_residual_evaluator.py
O=fable/proofs/checkers/out

$G $E --mode validate --json $O/w2j_validate.json
$G $E --mode opcheck --chains 0:24  --json $O/w2j_opcheck_a.json
$G $E --mode opcheck --chains 24:48 --json $O/w2j_opcheck_b.json
$G $E --mode opcheck --chains 48:67 --json $O/w2j_opcheck_c.json

# (b): 12-chain slices, --rhos 2
for s in 0:12 12:24 24:36 36:48 48:60 60:67; do
  $G $E --mode theta --rhos 2 --chains $s --json $O/w2j_theta_r2_${s/:/_}.json
done

# (c): rank-2 sweep with per-chain and per-run wall budgets
for s in 0:12 12:25 25:36 36:52 52:67; do
  $G $E --mode family --rhos 2 --chains $s --m 2 --kernel-rho 2 \
       --holdout 4 --chain-seconds 3 --run-seconds 30 \
       --json $O/w2j_family_${s/:/_}.json
done
$G $E --mode family --rhos 2 --chains 0:2 --m 4 --kernel-rho 2 --holdout 8 \
     --json $O/w2j_family_rank4.json
$G $E --mode family --chains 28:29 --witness-dirs \
     --json $O/w2j_family_witness_codexdirs.json
```

---

## 8. The single most decisive next question

> **Re-derive `L0` in the existing checkers and re-run W2g's `d = 1`, W2h's
> margin law and W2i's `d₂ = 1` on the 59 chains with `q(h1) ≠ 1` — then ask
> whether `Ξ_Z(Θ)` can hit zero on a family generated from the *complete*
> balanced source-pair space rather than a rank-2 window.**

Two reasons this is the fork, in that order.

**First, the foundation.** W2i's headline — `Ξ_Z : C₂ ≅ W_Q`, i.e. "`Ξ_Z(Θ) = 0`
is the whole layer-2 question" — is the premise this entire note is built on,
and it is computed from an operator image that includes the `L0` column. On 8
chains that column is right; on 59 it is not. Until that is redone, §5.1's
"no second-layer lift exists there" is conditional on a result computed with a
wrong operator on most of the census. Nothing else should be built on the
layer-1 stack before this is settled.

**Second, the family.** §5.2 shows the cheap route to an obstruction is closed:
the mod-2 map moves. What is left is a genuinely infinite question — is
`0 ∈ image(Ξ_Z ∘ Θ)` over all of `H_fin`? — and the source's §3.2 already says
the answer must be phrased on the complete source-pair space. The right shape
is not a bigger window; it is a `Γ`-equivariance argument on the quadratic
form, or a place (a prime, a coordinate `D`) where the quadratic's value set is
provably a proper subset of `Z` for *structural* reasons. Two discipline notes
from this run: (i) the free part is nonzero on 55/55 baselines, so the `p = 2`
place W2f found permissive and W2i flagged is **not** where the action is —
the integral coordinates are; (ii) any "cannot hit zero" claim must be tested
against a *live* family, and `distinct_mod2_values` is the cheap liveness
check that this run already ships.
