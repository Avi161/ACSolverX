# W2i: d₂ = 1 — layer 2 is blind too, and `Ξ_Z` is not a shadow but an isomorphism

Date: 2026-08-28 · Checker: `checkers/layer2_d2_invariant.py`
(imports `infinite_index_liveness.py` and, through it, `g_stratum_death.py`,
`period_two_parametric_solvability.py`, `period_two_liveness_invariance.py`,
`period_two_baseline_liveness.py` and the codex lift certificate, all unmodified;
guarded foreground runs.)
Run records: `checkers/out/w2i_identity_a.json`, `w2i_identity_b.json`,
`w2i_lambda1.json`, `w2i_d2_a.json`, `w2i_d2_b.json`, `w2i_d2_detail.json`,
`w2i_d2_deep.json`, `w2i_d2_wide.json`, `w2i_uniform.json`, `w2i_torsion.json`,
`w2i_probe_a.json`, `w2i_probe_b.json`, `w2i_inf_a.json`, `w2i_inf_b.json`,
`w2i_inf_align_a.json`, `w2i_inf_align_b.json`, `w2i_inf_align_c21.json`,
`w2i_inf_align_c22.json`.

Answers `W2H_INFINITE_INDEX_LIVENESS.md` §7: *"What is `d₂` — the double-coset
invariant of the SAME `Γ = ⟨R,U,w⟩` acting on `Λ²M`?"*

---

## 0. Verdict

| question | answer | status |
|---|---|---|
| Is the `Λ²M` identification of W2h §5.4 correct as stated? | **Verified, with two hypotheses W2h did not name** (§1.3): `N` must be free on the Schreier generators `r_v`, `v ∈ X = Q/⟨c⟩` (it is), and (3.5)'s "same coefficients `a_{r,g}`" is an *asserted* variation identity, justified in the source by γ₂N being central mod γ₃N. Everything downstream of (3.5) is then exact. | **VERIFIED** |
| Is `Λ²M/I_Γ Λ²M` free, or does it carry the 2-torsion W2h flagged? | **Free — no 2-torsion, on all 67 chains.** A `γ ∈ Γ` reversing a pair is *forced* to be an involution, and `Γ = ⟨R,U,w⟩` is **torsion-free for all 67** (no `c`-fixed vertex in its Stallings core). W2h's "*can* carry torsion" is right; it does not. | **PROVED** (§3.1) |
| Can `d₂ = 1` mean at layer 2 what `d = 1` meant at layer 1 ("the image is everything")? | **No — that branch was already closed by the source doc.** (3.16) kills every `L_r^{(2)}` in the full `Q`-coinvariants, so `Ξ_Z : C₂ ↠ W_Q` and `C₂` is *always* infinite with both free and `Z/2` parts. W2h §7's first bullet is unreachable as written. | **PROVED** (§1.4) |
| So what is `d₂`? | The gap between the operator image and `ker(Ξ_Z)` — the exact analogue of `image = ker ε`. Measured: **`d₂ = 1` for every displacement class of all 44 finite-index chains**, i.e. `Ξ_Z : C₂ → W_Q` is an **isomorphism**, not merely onto. | **PROVED** (§3.2, §3.3) |
| …and on the 23 infinite-index chains? | Same picture, at W2h's evidential strength: the coverage front on `Z[Γ\Q]` advances one-for-one with the radius; **23/23 have nonempty certified coverage**, none is obstructed. | **EVIDENCED** (§3.4) |
| Was an obstruction found? | **No.** Nothing beyond the `Ξ` the codex note already tracks. | — |
| Does the detector work at all? | **Yes.** Synthetic system (`L0, L1` doubled): fires on **44/44** chains, **1,056/1,056** blocks, silent on the real ones *with* a re-multiplied membership witness, two independent linear-algebra paths agreeing. The torsion path, vacuous on the real `Γ`, is fired separately on `Γ' = ⟨R,U,w,c⟩`: **268 torsion classes, 268 verified γ-swap witnesses.** | **verified** |
| What it means | The period-two double-coset machinery is **blind through layer 2**: `Γ` refines nothing that `Q` did not already see. The codex note's tracked obstruction `Ξ_Z(Θ(F))` is therefore not a shadow of `C₂` — it *is* `C₂`. | §5 |

---

## 1. The module, and its exact hypotheses

### 1.1 Where the identification actually comes from

W2h cites "(3.1)/(3.5) of the codex layer-2 structure". The source is
`literature/proofs/AK3_DEPTH4_PERIOD_TWO_FULL_LIFT_BOUNDARY.md` §3 (not the
handoff note, which only *reports* wedge computations). Verbatim:

```text
(3.1)  W := γ₂N/γ₃N = [N,N]/[[N,N],N] ≅ Λ²M        "Since N is free on the
                                                    Schreier generators (r_v)_{v∈X}"
(3.2)  Θ(F) := [R_can(F)] ∈ W                      the layer-2 defect
(3.3)  L_r = Σ_{g∈Q} a_{r,g} g
(3.4)  g·(m ∧ n) = (gm) ∧ (gn)
(3.5)  L_r^{(2)}(m ∧ n) := Σ_g a_{r,g} (gm ∧ gn)
(3.6)  [R(F;k)] = Θ(F) + Σ_{r=0..4} L_r^{(2)} Y_r
(3.7)  I₂ := Σ_r im L_r^{(2)},   C₂ := Λ²M / I₂
(3.8)  a lift through F(c,t)/γ₃N exists  ⟺  ∃F ∈ H_fin : [Θ(F)] = 0 in C₂
```

with `Q = ⟨c,t | c²⟩`, `N = ker(F(c,t) → Q)`, `M = N_ab`, `H = ⟨c⟩`, `X = Q/H`.

### 1.2 What W2h got right

`Λ²M` with the diagonal action (3.4) is a left `Z[Q]`-module and (3.5) is
*literally* the group-ring element `L_r` acting on it — so W2g's Lemma 1 (an
identity between group-ring elements) and Lemma 2 (telescoping, a statement about
any left `Z[Q]`-module) transfer verbatim:

```text
L2^{(2)}Λ²M + L3^{(2)}Λ²M + L4^{(2)}Λ²M = I_Γ · Λ²M ,   Γ = ⟨R, U, w⟩
A₂ := Λ²M / I_Γ Λ²M   (the Γ-coinvariants)
C₂ = A₂ / image(L0^{(2)}, L1^{(2)})
```

All of this is confirmed here, and the two fiats are guarded effectively (§4, C2/C3).

### 1.3 The two hypotheses W2h did not state

1. **`N` free on `(r_v)_{v∈X}`.** (3.1) is the free-Lie-algebra degree-2 fact
   `γ₂/γ₃ ≅ Λ²(ab)`, valid *because* `N` is free on the Schreier basis
   `r_v = ṽc²ṽ⁻¹` indexed by `X = Q/⟨c⟩` (1.4). This holds — but it is a
   hypothesis, and it is what makes `M = Z[X]` a *permutation* module and `Λ²M`
   a *signed permutation* module. Nothing here is true for a general `M`.
2. **(3.5) is an asserted variation identity, not a derived one.** The source's
   justification is one sentence: modulo `γ₃N`, `γ₂N` is central in `N`, so only
   the `Q`-class `g` of a prefix acts, "with the same integral coefficient
   `a_{r,g}` as in `L_r`". This note takes (3.5) as given. **Everything below is
   conditional on it**; if the layer-2 coefficients differed from the layer-1
   ones, the operators would differ and `d₂` would be a different number. What is
   *not* conditional is the module structure of `Λ²M`, the transfer of Lemmas 1–2,
   and the shape of `A₂` — those follow from (3.1)/(3.4) alone.

Also worth correcting: the layer-2 defect is **not** "the wedge of layer-1 data".
By (3.2)/(1.9)/(1.11) it is `Θ(F) = [R_can(F)]`, the class of the *literal
free-group residual* of the canonical shortlex section (1.5) — an integral
**affine-quadratic** function of `F`. See §5.3.

### 1.4 The one place W2h's framing is wrong

W2h §7 offers "if `d₂ = 1` and the torsion part is trivial, the quotient obstructs
nothing at layers 1 *or* 2". That branch cannot be reached, and the reason is in
the same source section W2h cites. (3.16):

```text
Ξ₀(L_r^{(2)} w) = Σ_g a_{r,g} Ξ₀(g w) = ε(L_r) Ξ₀(w) = 0 ,   r = 0..4
```

because `Ξ` is *diagonally `Q`-invariant* and every `L_r` has augmentation 0. So
the full-`Q` coinvariant map kills the entire operator image and (3.17) gives a
**surjection** `Ξ_Z : C₂ ↠ W_Q ≅ ⊕_{𝒟₂} Z ⊕ ⊕_{𝒟₁} Z/2`, both index sets
infinite. `C₂` is therefore never trivial and the image is never everything, for
**any** `Γ`. The honest layer-2 analogue of W2g's `d = 1` is instead

```text
image(L0^{(2)}, L1^{(2)})  =  ker( Ξ_Z : A₂ ↠ W_Q ) ,     block by block,
```

i.e. `Ξ_Z : C₂ → W_Q` is an isomorphism. That is what `d₂ = 1` means here, and it
is what is computed.

---

## 2. The structure: `Ω₂`, exactly

### 2.1 The classification of pair orbits (Lemma 6)

**Lemma 6.** For `u, v ∈ Q` with `uH ≠ vH`, the `Γ`-orbit of the ordered pair
`(uH, vH)` is classified exactly by

```text
κ(u,v) := min over h₁,h₂ ∈ H of  ( h₁⁻¹ u⁻¹v h₂ ,  Γ u h₁ )
```

*Proof.* `Γ\(Q × Q) → Γ\Q × Q`, `(u,v) ↦ (Γu, u⁻¹v)` is a bijection (if
`(Γu,u⁻¹v) = (Γu',u'⁻¹v')` then `u' = γu` forces `v' = γv`), and the right
`H × H` action is `(u,v) ↦ (uh₁, vh₂)`, i.e. `(Γu, z) ↦ (Γu·h₁, h₁⁻¹zh₂)`.
Minimising over the four-element `H × H` orbit is a complete invariant. ∎

Two consequences run the whole computation:

- **`z = u⁻¹v` is a diagonal invariant.** `g·(u,v)` has the same `z`. So every
  operator row is supported inside one **displacement block**, indexed by the
  `H`-double coset `D = HzH`. That is exactly the source doc's index set (3.12),
  with the reduced normal form (3.15) `t^{n₀}c t^{n₁}c ⋯ c t^{n_k}`, `n_j ≠ 0`,
  modulo `D ∼ D⁻¹`.
- **Inside a block the only remaining coordinate is `Γu ∈ Γ\Q`.** For a fixed
  representative `z` the map `s ↦ κ(s,z)` is a *bijection* `Γ\Q → {classes of the
  block}` (the `z`-part of `κ` is the same for every `s`; the state part is
  uniformly `s` or uniformly `s·c`).

### 2.2 `Ω₂` and its signs

`Λ²M` is a **signed** permutation module, so the coinvariants are

```text
A₂ = ⊕ Z    over Γ-orbits of ordered pairs NOT fixed by reversal (paired with
            their reverse, one free generator per pair)
   ⊕ Z/2    over orbits some γ ∈ Γ reverses      (there [x] = −[x])
```

Reversal is `ς : κ(u,v) ↦ κ(v,u)`, i.e. `(s,z) ↦ (s·z, z⁻¹)`, which maps block
`D` to block `D⁻¹`. Hence, per inversion-orbit `{D, D⁻¹}`:

| case | `A₂` of the block | `Ξ_Z` target `W_Q` | why |
|---|---|---|---|
| `D ≠ D⁻¹` | `Z[Γ\Q]` (free, rank `\|Γ\Q\|`) | `Z` | `ς` identifies the `D` and `D⁻¹` copies with one global sign |
| `D = D⁻¹` | `Z[Γ\Q] / (e_{ι s} = −e_s)`, `ι` a fixed-point-free involution | `Z/2` | `ς` folds the single copy |
| `ι` has a fixed point | that generator becomes `Z/2` | — | 2-torsion |

and `Ξ_Z` is, in these coordinates, the **augmentation** of `Z[Γ\Q]` (mod 2 in the
self-inverse case). For `Γ = Q` this degenerates to `\|Γ\Q\| = 1` and reproduces
the source doc's (3.13)/(3.15a)/(3.15b) exactly — an independent check that
Lemma 6 is the right classification.

### 2.3 The uniform reduction (Lemma 7) — why this is a theorem, not a sample

**Lemma 7.** In the coordinates of §2.1 the layer-2 row of `L_r^{(2)}` on the pair
`(u, uz)` is

```text
Σ_g a_{r,g} · e_{ρ(u)(σ(g))}     in  Z[Γ\Q] ,      σ(g) = Γg ,  ρ(u) ∈ P
```

**with no `z` in it.** *Proof.* The row terms are `κ(Γ(gu), z) = κ(σ(g)·u, z)`;
the block bijection of §2.1 sends that to `σ(g)·u = ρ(u)(σ(g))`; and the
orientation sign is constant on a block. ∎

So:

- for **every** `D ≠ D⁻¹`, `C₂(D) = Z[Γ\Q] / ⟨L0, L1 columns⟩` — **one group, the
  same for all such `D`**. This is W2g's layer-1 computation run one level finer:
  on `Γ\Q` instead of `Ω = Γ\Q/⟨c⟩`. Layer 2 does see one extra level of
  resolution; the question is whether the columns still fill the augmentation-zero
  part there.
- for **every** `D = D⁻¹`, `ς` is right multiplication by `z·h` for some `h ∈ H`,
  i.e. *some* `ρ ∈ P`; looping over the involutions of `P` covers all of them.

Both loops are finite. On the 44 finite-index chains the verdict is therefore a
statement about **all** displacement classes, not a truncated sample.

---

## 3. Results

### 3.1 `A₂` is free: no layer-2 2-torsion anywhere on the census

**Lemma 8.** If `γ ∈ Γ` reverses a pair (`γuH = vH`, `γvH = uH`) then `γ² = 1`.

*Proof.* `γ = v h u⁻¹` for some `h ∈ H`, and `γvH = uH` forces `z h z ∈ H` with
`z = u⁻¹v`. If `h = 1` then `z² ∈ H`, so `γ² = u z² u⁻¹ ∈ uHu⁻¹`; `γ² = ucu⁻¹ ≠ 1`
would give `γ` order 4, impossible in `C₂ * Z` (finite subgroups of a free product
are conjugate into a factor), so `γ² = 1`. If `h = c` then `zcz ∈ H`; `zcz = 1`
would make `cz` of order 4, so `zcz = c` and `γ² = u(zc)²u⁻¹ = 1`. ∎

So `A₂` has 2-torsion **iff `Γ` contains an involution**, i.e. iff its Stallings
core has a `c`-fixed vertex. Measured (`--mode torsion`, all 67 chains):

| | chains |
|---|---:|
| `Γ = ⟨R,U,w⟩` whose core has a `c`-loop (⇒ `Γ` has torsion) | **0 / 67** |
| 2-torsion classes found over the sampled `z` and a radius-5 ball of `u` | **0** |
| **control** `Γ' = ⟨R,U,w,c⟩`: core has a `c`-loop | **67 / 67** |
| **control**: torsion classes found | **268** |
| **control**: each shipping an explicit `γ` verified in `Γ'` by folding, and verified to swap the pair | **268 / 268** |

**`A₂ = (Λ²M)_Γ` is a free abelian group for every census chain.** W2h §5.4's
structural observation — that a signed permutation module *can* carry 2-torsion
where `Z[Ω]` cannot — is correct, and the answer is that on this family it does
not, for a reason that has nothing to do with the operators: `Γ` is torsion-free.
(The `Z/2` summands of `W_Q` are still there; they come from `Q`, not from `Γ`.)

### 3.2 `d₂ = 1` on the sampled blocks — 44 chains × 44 displacement classes

`--mode d2 --zk 3 --zn 2` (44 classes `D`: all `t^{n₀}`, `t^{n₀}ct^{n₁}`,
`t^{n₀}ct^{n₁}ct^{n₂}` with `\|n_j\| ≤ 2`, modulo inversion):

| | value |
|---|---:|
| chains | **44** |
| blocks (chain × `D`) | **1,936** |
| blocks with `image = ker Ξ_Z`, i.e. `d₂(D) = 1` | **1,936 / 1,936** |
| blocks with any extra obstruction | **0** |
| torsion generators | **0** |
| `C₂(D)` shapes seen | `Z` (`D ≠ D⁻¹`), `Z/2` (`D = D⁻¹`) — exactly `W_Q(D)` |

Every chain has `\|Γ\Q\| = 4`, so a generic block is `A₂ = Z⁴ → C₂ = Z`, and a
self-inverse block is `A₂ = Z² → C₂ = Z/2`. Deeper and wider `z` families
(`--zk 5 --zn 1`, 34 classes; `--zk 2 --zn 4`, 40 classes) give the same.

### 3.3 …and `d₂ = 1` for *every* displacement class (Lemma 7 made effective)

`--mode uniform`, all 44 finite-index chains:

| | value |
|---|---:|
| `L2, L3, L4` rows nonvanishing in `Z[Γ\Q]` | **0** (they die because `X, U, w ∈ Γ`) |
| generic block `C₂ = Z[Γ\Q]/⟨L0,L1⟩` equal to `Z` | **44 / 44** |
| fixed-point-free involutions of `P` enumerated per chain | 3 |
| self-inverse-block `C₂` shapes over all of them | `Z/2` only, **44 / 44** |
| sampled concrete blocks disagreeing with the uniform prediction | **0 / 1,936** |

**Theorem (44 finite-index chains).** `Σ_r im L_r^{(2)} = ker(Ξ_Z)` on `Λ²M`, so

```text
Ξ_Z : C₂ ⟶ W_Q      is an ISOMORPHISM,   not merely the surjection of (3.17).
```

The layer-2 obstruction group of the period-two quotient is *exactly* the
`Q`-coinvariant group the codex note already computes. `Γ` adds nothing.

### 3.4 The 23 infinite-index chains: the margin law again, one level finer

`Γ\Q` is infinite there (W2h's core-plus-cones), so a block has infinitely many
generators and the coverage discipline of W2h §3.4 applies unchanged — on
`Z[Γ\Q]` instead of `Z[Ω]`. `--mode inf`, plain ball, `L = 6,7,8,9,10`:

| behaviour of the covered depth | chains |
|---|---:|
| advances **+1 per +1 in `L`** from `L = 6`, margin constant (`μ ∈ {1,2,3,5}`) | **12** |
| starts at `L = 9`, then advances +1 per +1 | **4** |
| still `−1` at `L = 10` (deep state tuple) | 7 |

With W2h's aligned word family (`--align 8`) five of those seven start (covered
depth 2–7); the last two (`g = Tc`, 4-state core) start at `--align 12, L = 12`,
covering to depth 3 with 3,466 certified differences. **23/23 have nonempty
certified coverage; none is obstructed.** `L2, L3, L4` rows vanish in `Z[Γ\Q]` on
every run of every chain.

Status: **EVIDENCED, not proved** — exactly W2h §3.4's status, and for the same
reason (the induction transporting a certificate one depth outward is stated, not
closed). Every negative was a radius artifact that dissolved when the enumeration
grew, as in W2h.

---

## 4. Controls

Every control runs on every run and each was demonstrated able to fail.
Exit 0 = all green (a negative verdict is a *result*); exit 2 = control failure,
run void.

| control | guards | how it can fail | result |
|---|---|---|---|
| C1 fixed-`h` witness `(21,48,0)` | the imported lifting calculus is the codex one | defect mismatch ⇒ exit 2 | passes every run |
| **C2 layer-2 Lemma 2′** (`--mode identity`) | the fiat that only `L0, L1` carry information at layer 2 | any nonzero `A₂`-row among the `L2, L3, L4` columns ⇒ exit 2 | **73,968 rows, 0 nonvanishing**, all 67 chains |
| C3 corruption breaks C2 | C2 is not vacuous | dropping one term of `L2` must produce a nonzero row | fires **67/67** |
| **C4 `Ξ_Z(row) = 0`** | (3.16) as an assertion about the rows this code really builds | any row with nonzero `Ξ_Z` ⇒ exit 2 | **49,312 rows, 0 nonzero** |
| **C5 `Γ`-invariance of `κ`** | Lemma 6 — the classification the whole note rests on | `κ(γu,γv) ≠ κ(u,v)` for `γ ∈ Γ` ⇒ exit 2; and an element *outside* `Γ` (found by folding, since `w = t` on the `g = ""` chains) must **move** the class | **16,080 checks, 0 failures**; the non-`Γ` witness moves it on every chain |
| C6 base-coset pinning | the W2g defect (union-find re-rooting the base) cannot recur | `σ(R), σ(U), σ(w) ≠ base` ⇒ exit 2 | 67/67 |
| **C7 finite specialization** (`--mode lambda1`) | the layer-2 machinery is a *generalisation*, not a different computation | run the same `Frame`/`σ`/`P` code on `M`: `d`, `m`, `\|Ω\|`, `\|P\|` must equal `out/w2g_omega_all.json` | **44/44 agree**, `d = 1` |
| **C8 positive control** (`--mode probe`) | **the detector can fire at all** | on the real systems the image contains `ker Ξ_Z`, so nothing can ever be certified; the control runs on a **synthetic** system (`L0, L1` doubled ⇒ image inside `2A₂`): a *primitive* `ker Ξ_Z` vector **must** be certified not-in-image there, **must** be in the real image, and the two independent linear-algebra paths (Hermite echelon vs Smith normal form) **must** agree | fires **44/44 chains, 1,056/1,056 blocks**; witnesses re-multiplied out; paths agree everywhere |
| **C9 torsion positive control** (`--mode torsion`) | the 2-torsion path is not vacuously green | the real `Γ` has no involutions, so the torsion branch never executes; it is therefore fired on `Γ' = ⟨R,U,w,c⟩`, where torsion classes **must** appear and each **must** ship an explicit `γ` verified in `Γ'` by folding and verified to swap the pair | **268 classes, 268 witnesses, 0 missing**, 67/67 |
| C10 witness re-multiplication | the echelon membership answer | recompute `Σ c·row` and compare term by term | every positive answer |
| C11 uniform-vs-concrete | Lemma 7's abstract reduction against the concrete block computation | any sampled block disagreeing with the uniform prediction ⇒ exit 2 | **0 / 1,936 mismatches** |

C2/C4/C5 are the load-bearing trio and each is a direct descendant of W2g's
lesson (*a control must assert the load-bearing step itself*): C2 asserts the
layer-2 form of Lemma 2′, C4 asserts (3.16) on the rows actually built, C5 asserts
Lemma 6 — with a *non*-`Γ` element required to break it, found by folding rather
than assumed, because `w = gtg⁻¹` is literally `t` on the `g = ""` chains and a
hard-coded `t` would have made that control silently inert.

Reproduce (each command is its own guarded run):

```bash
python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- python3 \
  fable/proofs/checkers/layer2_d2_invariant.py --mode identity --chains 0:34 \
  --radius 4 --zmax 8 --zk 2 --zn 2 \
  --json fable/proofs/checkers/out/w2i_identity_a.json
# ... --chains 34:67 -> w2i_identity_b.json

python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- python3 \
  fable/proofs/checkers/layer2_d2_invariant.py --mode lambda1 \
  --json fable/proofs/checkers/out/w2i_lambda1.json

python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- python3 \
  fable/proofs/checkers/layer2_d2_invariant.py --mode d2 --chains 0:22 \
  --zmax 200 --zk 3 --zn 2 --radius 6 \
  --json fable/proofs/checkers/out/w2i_d2_a.json
# ... --chains 22:44 -> w2i_d2_b.json
# ... --chains 0:4 --zk 5 --zn 1 -> w2i_d2_deep.json
# ... --chains 4:8 --zk 2 --zn 4 -> w2i_d2_wide.json
# ... --chains 0:1 --zk 2 --zn 1 --zmax 6 --detail -> w2i_d2_detail.json

python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- python3 \
  fable/proofs/checkers/layer2_d2_invariant.py --mode uniform --zmax 44 \
  --zk 3 --zn 2 --json fable/proofs/checkers/out/w2i_uniform.json

python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- python3 \
  fable/proofs/checkers/layer2_d2_invariant.py --mode torsion --zmax 200 \
  --zk 3 --zn 2 --radius 5 \
  --json fable/proofs/checkers/out/w2i_torsion.json

python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- python3 \
  fable/proofs/checkers/layer2_d2_invariant.py --mode probe --chains 0:22 \
  --zmax 24 --zk 3 --zn 2 \
  --json fable/proofs/checkers/out/w2i_probe_a.json
# ... --chains 22:44 -> w2i_probe_b.json

python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- python3 \
  fable/proofs/checkers/layer2_d2_invariant.py --mode inf --chains 0:12 \
  --radii 6,7,8,9,10 --zmax 0 \
  --json fable/proofs/checkers/out/w2i_inf_a.json
# ... --chains 12:23 -> w2i_inf_b.json
# ... --radii 8,9,10 --align 8 -> w2i_inf_align_a.json / _b.json
# ... --chains 21:22 --radii 8,10,12 --align 12 -> w2i_inf_align_c21.json
# ... --chains 22:23 --radii 8,10,12 --align 12 -> w2i_inf_align_c22.json
```

---

## 5. What it means

### 5.1 The blindness theorem through layer 2

**Theorem (stated at its exact scope).** For each of the 44 finite-index census
chains, with `Γ = ⟨R,U,w⟩` and the operators `build_operators_general` returns at
window `k = 0`:

```text
Λ²M / Σ_{r=0..4} im L_r^{(2)}   ≅   (Λ²M)_Q   =   ⊕_{𝒟₂} Z ⊕ ⊕_{𝒟₁} Z/2
```

*via* `Ξ_Z`. Equivalently `d₂ = 1` at every displacement class. On the other 23
the same statement is EVIDENCED by the margin law at the radii computed.

Reading it, in one sentence: **the period-two quotient's layer 2 sees nothing that
the diagonal `Q`-action did not already see** — every `Γ`-refinement of the
layer-2 cokernel collapses, exactly as `d = 1` collapsed the layer-1 one. W2h's
"first real obstruction" branch (`d₂ > 1`, or nonzero 2-torsion missing the
defect, on some stratum) is **closed**: there is no such stratum, and the 2-torsion
`A₂` could have carried is identically absent because `Γ` is torsion-free.

### 5.2 What this gives the codex route

The source doc says of (3.17)/(3.18): "*If a balanced source pair kills the
mod-two histogram, its signed integral buckets, and then its complete class in
`C₂`, must still be evaluated.*" §3.3 removes the third step: for these `Γ`,
`Ξ_Z` is injective, so *the complete class in `C₂` **is** the signed integral
bucket vector*. `Ξ_Z(Θ(F)) = 0` is not merely necessary for (3.8) — for the
period-two census presentations it is **necessary and sufficient**. That upgrades
(3.18) from a necessary condition to the whole layer-2 question, and it means the
fifteen tracked bits are a genuine (lossy) shadow of a complete invariant, not of
something strictly finer.

*(This is a statement about the layer-2 cokernel only. It says nothing about
whether `Θ(F)` can be made to vanish — see §5.3.)*

### 5.3 The defect question, stated open

`Θ(F) = [R_can(F)]` where `R_can(F) = R(F; 1)` is the literal free-group residual
(1.8)–(1.9) of the canonical shortlex section (1.5) of the layer-1 solution
`x⁰⁰ + F`. It is an **affine-quadratic** function of `F`, and it is computed
nowhere in this repository except for the codex witness chain (for `F = 0` the
tracked freely reduced word of length 82; and for the four one-hop parity classes,
`AK3_DEPTH4_HANDOFF.md` "Degree two forces nonlocal first-layer support"). For the
other 66 census baselines **it is not computed and is not derivable from the
layer-1 records** — the W2g/W2h lift certificates give `x` with `D + Σ L_i x_i = 0`
in `M`, which is precisely the *input* to a `Θ` computation, not `Θ` itself.

So: **the defect question is open, and this note deliberately does not guess it.**
What §3 settles is the other half — the obstruction *group* — and that half is
decisive on its own in one direction: since the group is exactly `W_Q`, no defect
of any census baseline can be obstructed by anything finer than `Ξ_Z`.

### 5.4 Status ledger

| claim | status |
|---|---|
| `Λ²M` with (3.4) is a `Z[Q]`-module and (3.5) is `L_r` acting on it; W2g Lemmas 1–2 transfer | **VERIFIED** (from (3.1)/(3.4)/(3.5), hypotheses in §1.3) |
| Lemma 6 (`κ` classifies pair orbits) and Lemma 7 (the row is `z`-free in `Z[Γ\Q]`) | **proved**, and machine-verified with corruption controls |
| Lemma 8 (a reversing `γ` is an involution) ⇒ `A₂` free iff `Γ` torsion-free | **proved** |
| `Γ = ⟨R,U,w⟩` is torsion-free on all 67 census chains ⇒ **no layer-2 2-torsion** | **PROVED** (0/67 `c`-loops), control fires 67/67 on `Γ + ⟨c⟩` |
| the operator image can never be all of `A₂`; `Ξ_Z : C₂ ↠ W_Q` always | **PROVED** (source (3.16)/(3.17)); corrects W2h §7's first bullet |
| `d₂ = 1` at every displacement class, i.e. `Ξ_Z : C₂ → W_Q` is an isomorphism | **PROVED** for the 44 finite-index chains |
| … for the 23 infinite-index chains | **EVIDENCED** (margin law, `L ≤ 12`, align `≤ 12`; 23/23 nonempty coverage) |
| the detector can fire when an obstruction exists | **verified** on a synthetic doubled system, 1,056/1,056 blocks, two independent paths agreeing |
| the value of `Θ(F)` for the 66 non-witness baselines | **UNCOMPUTED — open** |
| whether `Ξ_Z(Θ(F))` can be made to vanish for some `F` | **open** (this is the codex route's own question) |
| anything about the free-group depth-four class, the bridge, AK(3), stable AC, or AC | **no claim** |

---

## 6. Scope and nonclaims

- **PROVED / VERIFIED / EVIDENCED / open** are used in the senses of §5.4 and are
  not interchangeable.
- **Everything downstream of (3.5) is conditional on (3.5).** The source states
  the layer-2 variation operator with the *same* coefficients `a_{r,g}` and gives
  a one-sentence justification. This note does not re-derive it. If (3.5) were
  wrong, `d₂` would be a different number; the module structure and `A₂`'s shape
  would survive.
- **The 44-chain theorem is at window `k = 0`.** Unlike W2g's layer-1 result the
  `(k₂,k₃)` axes are not closed here by a separate argument; what makes the
  statement window-robust in spirit is Lemma 7 (the block group depends on the
  window only through `Γ\Q` and the states `σ(g)`, and `Γ` itself is
  window-independent). *That is an argument, not a computation, and it is not
  claimed as proved.*
- **The 23 infinite-index results are coverage measurements, not a theorem.** A
  miss at a given radius is a truncation statement. No chain is reported as
  obstructed and none was.
- **`d₂ = 1` is not liftability.** It says the layer-2 obstruction group is
  exactly `W_Q`; it says nothing about whether any `Θ(F)` vanishes in it, and
  nothing about layer ≥ 3, the full lift, or the noncancellation tower.
- **Caps are ceilings.** The census is complete only for `max(|R|,|S|,|U|) ≤ 15`
  and `|g| ≤ 5`; "all 67" means all 67 *at that cap*.
- **The displacement families are samples where they are called samples.** §3.2's
  1,936 blocks are a sample; §3.3's uniform result is not (it quantifies over all
  `D` by Lemma 7 plus a finite loop over `P`).
- No claim about the free-group depth-four class, the bridge, AK(3), stable AC, or
  AC. This is a scope-quantification of one quotient layer of one signature.

---

## 7. The single most decisive next question

> **Compute `Ξ_Z(Θ(F))` — the signed integral displacement histogram of the
> layer-2 defect — for a census baseline other than the codex witness, and ask
> whether the balanced-source family `F ↦ Ξ_Z(Θ(F))` can hit zero.**

§3.3 says this is now the *whole* layer-2 question for the period-two quotient,
not a shadow of it: the obstruction group is `W_Q` and nothing finer exists. The
machinery needed is a `Θ` evaluator — the literal replay (1.8)–(1.9) at the
canonical section (1.5), then Reidemeister–Schreier rewriting into `(r_v)` and the
degree-2 Magnus coefficients — which exists for the witness
(`experiments/stable_ac/depth4_period_two_degree_two_escape_certificate.py`) and
for nobody else. Two consequences make this the fork:

- **If `Ξ_Z(Θ(F))` is forced nonzero on a whole parameter stratum,** that is the
  uniform layer-2 argument W2h §5.2 says the programme needs, and by §3.3 it is
  the *strongest possible* one at this layer — it cannot be sharpened by a finer
  double-coset invariant, because there is none.
- **If it vanishes for some `F` on the witness or any baseline,** layers 1 and 2
  are both clear and the obstruction must be sought at `γ₃N` or outside this
  quotient entirely.

Two discipline notes, paid for by this programme's own history. First, `Θ` is
affine-*quadratic* in `F`: a linear-algebra solver over the `Ξ_Z` coordinates is
answering a different question, and saying so up front is cheaper than
discovering it in the results. Second, `𝒟₁` (the self-inverse displacements)
carries `Z/2` coordinates whose sign information is destroyed — that is the
`p = 2` place W2f found permissive and W2h warned about, and it is still the one
whose nulls nobody has read.

---

## Summary of status

| claim | status |
|---|---|
| `[N,N]/[[N,N],N] ≅ Λ²M` with the diagonal action; `L_r^{(2)}` = `L_r` acting on it | **VERIFIED against the source**, hypotheses named in §1.3 |
| `L2^{(2)}, L3^{(2)}, L4^{(2)}` images `= I_Γ Λ²M`; their `A₂`-rows vanish identically | **proved**; **machine-verified** 73,968 rows, 0 nonvanishing, corruption fires 67/67 |
| Lemma 6: `κ(u,v)` classifies `Γ`-orbits of ordered pairs exactly | **proved**; 16,080 invariance checks, 0 failures, non-`Γ` witness moves the class |
| `Ω₂` structure: one copy of `Γ\Q` per displacement class `D ∈ (H\Q/H)∖{H}`, folded by reversal | **proved**; degenerates to the source doc's (3.13)/(3.15a) at `Γ = Q` |
| `Ξ_Z(row) = 0` for every row of every operator | **machine-verified**, 49,312 rows, 0 nonzero |
| the same machinery, run at layer 1, reproduces `w2g_omega_all.json` | **verified**, 44/44 |
| Lemma 8 ⇒ layer-2 2-torsion exists iff `Γ` has an involution; `Γ` torsion-free on all 67 ⇒ **`A₂` free, no 2-torsion** | **PROVED**; positive control fires 67/67, 268 verified swap witnesses |
| `d₂ = 1` on 1,936 sampled blocks (44 chains × 44 displacement classes) | **PROVED** at those blocks |
| `d₂ = 1` at **every** displacement class (Lemma 7 + finite loop over `P`) | **PROVED**, 44/44 chains, 0/1,936 uniform-vs-concrete mismatches |
| `Ξ_Z : C₂ → W_Q` is an isomorphism, upgrading the source's (3.17) surjection | **PROVED** for the 44 |
| the 23 infinite-index chains show the same, by coverage | **EVIDENCED**, 23/23 nonempty, margin constant on 12 at `L = 6..10` |
| the detector can fire | **verified**, synthetic doubled system, 1,056/1,056 blocks, echelon and SNF paths agree |
| the layer-2 defect `Θ(F)` for the 66 non-witness baselines | **UNCOMPUTED — stated open** |
| anything about lifting, the bridge, AK(3), stable AC, or AC | **no claim** |
