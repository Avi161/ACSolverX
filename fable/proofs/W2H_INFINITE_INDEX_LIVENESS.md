# W2h: the other 23 chains die too — layer 1 obstructs nothing on the whole census

Date: 2026-08-28 · Checker: `checkers/infinite_index_liveness.py`
(imports `g_stratum_death.py` and, through it, `period_two_parametric_solvability.py`,
`period_two_liveness_invariance.py`, `period_two_baseline_liveness.py` and the codex
lift certificate, all unmodified; guarded foreground runs).
Run records: `checkers/out/w2h_identity.json`, `w2h_finite_specialization.json`,
`w2h_image_a.json`, `w2h_image_b.json`, `w2h_margin_a.json`, `w2h_margin_b.json`,
`w2h_lift_a.json`, `w2h_lift_b.json`, `w2h_lift_c.json`, `w2h_lift_c9.json`,
`w2h_lift_c11.json`, `w2h_probe_a.json`, `w2h_probe_b.json`, `w2h_zeta_scan.json`,
`w2h_period.json`.

Answers `W2G_G_STRATUM_DEATH.md` §7 item 1: *"extend the theorem to `[Q:Γ] = ∞`
(23 chains, 7 in the stratum)"*, and then restates the W2 programme's obstruction
gap at the layer where it actually lives.

---

## 0. Verdict

| question | answer | status |
|---|---|---|
| Do the 23 infinite-index chains carry a layer-1 death certificate? | **No — `d = 1` again.** For **all 23**, `π(D)` lies in the image of the operators in `Z[Ω]`, so `D ∈ Σ_i L_i M` and the window is layer-1 solvable **over Z**. | **PROVED + WITNESSED** (§3.2) |
| Backed by explicit corrections, or only by the quotient argument? | **By both.** Every membership ships an integer combination of rows (1–27 rows at the base window, 96 at the widest window tested) that is re-multiplied out and compared term by term; and on **22 of 23** an explicit `x = (x₀..x₄) ∈ M⁵` with `D + Σ L_i x_i = 0` is built and verified with the **unmodified** `apply_operator`. | **PROVED + WITNESSED** (§3.3) |
| Is the whole census now covered? | **Yes at the computed windows: 67 of 67.** 44 by W2g at every window; 23 here. | see §3, §5 |
| Is the infinite-index result *window-independent* like W2g's? | **No — and this is the one place the two halves differ.** `ζ2, ζ3` act trivially on `Γ\Q` on **44/44** finite-index chains and on **0/23** infinite-index ones, so W2g §2.1's closure of the `(k2,k3)` axes has no analogue here. The window-independent statement rests on `A = Z[Ω]₀`, which is **evidenced by an exact margin law**, not proved. | **EVIDENCED** (§3.4, §3.5) |
| Was a genuine obstruction found? | **No.** Every candidate was a truncation artifact of the enumeration radius; each one dissolved when the radius grew (§3.5 exhibits the sharpest case). | **PROVED** for the rows shipped |
| Does the detector work at all? | **Yes** — on a synthetic system with `L0, L1` doubled (lattice `2A` by construction) a *primitive* `Ω`-difference defect is certified **not** in the image, its double **is**, and the independent one-hop solver agrees it is unsolvable mod 2. Fires 23/23. | **verified** |
| Where does that leave the period-two route? | Layer 1 is obstruction-free for the entire census; every death must come from **layer ≥ 2** or from outside this quotient. | §5 |

---

## 1. What was open

W2g decided the layer-1 question by a finite computation: with `Γ = ⟨R, U, w⟩` of
finite index in `Q = C₂ * Z`, the `Q`-set `Γ\Q` is finite, the permutation group
`P ≤ Sym(Γ\Q)` it induces is finite, and the whole set of `Ω`-rows is enumerated by
one loop over `P` (its Lemma 3). For 23 of the 67 census chains `[Q : Γ] = ∞`; `P`
is infinite and that loop does not exist. Nothing in W2g's Lemmas 1, 2, 2′ uses
finiteness — only Lemma 3 does — so what was missing was an exact description of
the rows over an **infinite** `Ω`.

---

## 2. The structure

### 2.1 The space: a finite core plus cones (Lemma 4)

`Q = ⟨c⟩ * ⟨t⟩ = C₂ * Z` is a free product of two groups whose own Cayley graphs
are trees, so **the Cayley graph of `Q` on `{c, t}` is a tree**. Hence the Schreier
graph of any subgroup is its Stallings core with cones of that tree hung on the
missing slots:

```text
vertex of Γ\Q  =  (u, W),   u a core state,  W a reduced word over {c, t, T}
                  W = ()  ⇔  a core vertex
reading x from (u, W), W ≠ ():   W·x freely reduced   (back-edge = INV[last(W)])
reading x from (u, ()):          the core edge if present, else (u, (x,))
```

*Status: this is exact, not an approximation.* Every vertex of the completed graph
has exactly one `c`-slot, one `t`-out and one `t`-in; the cones are the cones of the
Cayley tree; the construction degenerates to the core itself when the core is
already complete, which is what makes the **finite specialization** of §4 (C5) a
real control rather than a separate code path.

`Ω = Γ\Q/⟨c⟩` is the set of `c`-orbits; each has one or two members, and the class
is named by its shallower member, so every class has a well-defined **depth**.

### 2.2 The rows: a signed sum over a fixed finite state tuple (Lemma 5)

This is the new algebraic content and the reason the infinite case is decidable.

**Lemma 5.** Write `σ(x) = Γx ∈ Γ\Q`, let `·` be the right `Q`-action, `ω(·)` the
`Ω`-class, `β = S⁻¹B`. Then for **every** `v ∈ Q/⟨c⟩`

```text
π(L1 e_v) = [ω(σ(h2 β)·v)] + [ω(σ(h3 β)·v)] − [ω(σ(h2)·v)] − [ω(σ(h3)·v)]

π(L0 e_v) = [ω(σ(R)·v)] + [ω(σ(h2 R)·v)] + [ω(σ(h3 R)·v)]
          − [ω(σ(A)·v)] − [ω(σ(h2 A)·v)] − [ω(σ(h3 A)·v)]
```

and `π(L2 e_v) = π(L3 e_v) = π(L4 e_v) = 0`.

*Proof.* `X = h2 S h2⁻¹ ∈ Γ` gives `h2 S = X h2`, hence `Γ h2 S z = Γ h2 z`; the
defect identity `U⁻¹ h3 S h3⁻¹ = w` in `Q` (this is exactly `D ∈ N`) gives
`U⁻¹h3 S = w h3` with `w ∈ Γ`, hence `Γ U⁻¹h3 S z = Γ h3 z`; and `U, R, w, X ∈ Γ`
kill the remaining prefixes. Substituting into `L0 = −(U⁻¹ + (h2 + U⁻¹h3)S)(A − R)`
and `L1 = (h2 + U⁻¹h3)(B − S)` and using `bridge·B = bridge·S·β` gives the two
displays. ∎

Three consequences make the infinite case tractable:

- every coefficient is `±1` — the `Ω`-image of an operator column is a *signed
  incidence pattern*, not a weighted one;
- the dependence on `v` is **only** through the right action on a fixed 4- (resp.
  6-) element tuple of states — this is the exact form of *"the operators have
  finite support, so far-out tree classes are hit in a translation-invariant
  pattern"*;
- once the tuple has been carried far enough out that all six entries share a
  nonempty common tail `τ`, no two of them can be `c`-partners (a `c`-partner
  differs by a trailing `c`, which a common reduced tail forbids), so the deep rows
  have **full support with all coefficients `±1`** and shift rigidly as `τ` grows.
  That is the freezing behaviour behind §3.4's margin law.

Lemma 5 is an **algebraic fiat** and is guarded accordingly: `--mode identity`
asserts, for every reduced `v` in a ball and every one of the 67 chains, that the
Lemma-5 row **equals** the row obtained by tracing every term of the operator
`build_operators_general` actually returns, and that dropping one term of `L1`
breaks the equality. It also asserts `π(L2), π(L3), π(L4) = 0` directly (W2g's
Lemma 2′ in the tree frame) with its own corruption control, and asserts the base
coset is pinned (`σ(R) = σ(U) = σ(w) = base` — the W2g defect, re-guarded here).

### 2.3 What is being decided, and what a positive answer proves

Let `A ≤ Z[Ω]` be the subgroup generated by all Lemma-5 rows. Since
`L2M + L3M + L4M = I_Γ M = ker π` (W2g Lemma 2 — its telescoping proof uses no
finiteness),

```text
D ∈ Σ_i L_i M     ⟺     π(D) ∈ A
A = Z[Ω]₀ (the augmentation-zero part)  is the infinite-index form of  "d = 1".
```

`π(D) ∈ A` is decided by **exact integer (Hermite) elimination** on the rows with
`|v| ≤ L`: a positive answer is a genuine integer combination of genuine elements
of `A`, hence a **proof**, independent of `L`; a negative answer at a given `L` is
only "not found at this radius". Every positive answer here ships its combination,
which the checker re-multiplies out and compares term by term against `π(D)`.

Because a state sitting at depth `D` in a cone is only ever brought back toward the
core by a `v` whose first `D` letters spell its escape word backwards, the plain
ball `|v| ≤ L` is a poor enumeration when the tuple is deep. `--mode image` adds an
**aligned family** `winv(escape) · u`, `|u| ≤ align`. Aligning changes which
certificates are *found*, never which are *valid*.

---

## 3. Results

### 3.1 The 23 cores

| core states | chains | missing `c`-slots | missing `t`-slots (out/in) |
|---:|---:|---:|---:|
| 4 | 6 | 0 | 1 / 1 |
| 6 | 1 | 0 | 1 / 1 |
| 8 | 11 | 0 | 2 / 2 |
| 9 | 2 | 1 | 2 / 2 |
| 12 | 3 | 4 | 2 / 2 |

By `g`: `"" (13)`, `c (3)`, `TTc (3)`, `Tc (2)`, `cTTc (1)`, `cTTTc (1)`. Seven are
in W2f's g-stratum `S2`; three are one-hop live; all three `g = c` chains sit here,
as W2g flagged. The codex witness chain is **not** here — it has `[Q:Γ] = 4`.

### 3.2 `π(D) ∈ A` over `Z` — all 23

`--mode image --radii 10,12 --align 10`:

| | chains |
|---|---:|
| `π(D)` has augmentation 0 | **23/23** |
| `π(D)` an **integer** combination of Lemma-5 rows | **23/23** |
| combination re-multiplied out and equal term by term | **23/23** |
| chains with a death certificate | **0** |

Witness sizes run from 1 row (chain `(TTctcTctc, TTTctctttcTctcT, ttcTctcTTTTctc)`)
to 27 rows (the two `g = Tc` chains). Since `π(D) ∈ A ⟺ D ∈ Σ_i L_i M`, every one
of these 23 windows is **layer-1 solvable over Z** — at a window W2f's one-hop
sweep records as dead at every prime for the 7 stratum members.

### 3.3 Explicit verified corrections — 22 of 23

`--mode lift` solves `D + Σ_i L_i x_i = 0` **in the module**, with no `Ω`
machinery in the verification: the variable set is a `ρ`-hop expansion of W2b's own
`one_hop_system` (`ρ = 1` *is* the one-hop truncation), optionally seeded with the
columns the `Ω` witness names, and the answer is checked with the unmodified
`apply_operator`.

| | value |
|---|---:|
| chains with `D + Σ L_i x_i = 0`, residual **0** | **22 / 23** |
| hops needed | 2 (21 chains), 3 (1 chain) |
| typical `x_terms` | `[1, 6, 23, 31, 15]` … `[9, 18, 51, 124, 134]` |
| mutation control: drop one term of `L4` | residual **8–20 terms**, fires every run |

The single miss is `(TTctcTctc, TTTctctttcTctcT, ttcTctcTTTTctc)`: its `Ω` witness
is one row, but the residual that then has to be absorbed by `L2, L3, L4` (18 terms,
provably inside `I_Γ M`) was not routed within the hop budget. **That is a search
failure, not a mathematical one** — the theorem is §3.2's, and it does not depend on
this construction. Conversely the 22 successes are hard evidence, because each is
checked by exact module arithmetic.

`ρ = 1` is exactly W2b's truncation. **`ρ = 2` already suffices on 21 of the 23.**
The one-hop bar and the module question are one hop apart.

### 3.4 The margin law: coverage advances one-for-one with the radius

`--mode image --align 0 --radii 6,8,10,12` measures, for each `L`, the largest depth
`d(L)` such that **every** `Ω`-class of depth `≤ d(L)` reached by the ball satisfies
`[ω] − [ω_base] ∈ A`.

| behaviour of `d(L)` over `L = 6, 8, 10, 12` | chains |
|---|---:|
| `d(L) = L − μ` with `μ` constant from `L = 6` (`μ ∈ {1,2,3,5}`) | **12** |
| starts at `L = 8` or `10`, then advances by exactly `+2` per `+2` in `L` | **7** |
| advances at half rate (`−1, −1, 0, 1`) | 1 |
| never leaves `−1` at `L ≤ 12` (state tuple at depth 16) | 3 |

So on 19 of 23 the coverage front recedes from the truncation boundary at exactly
the rate of `L`: the boundary, not the module, is what limits it, and in the limit
`L → ∞` every `Ω`-difference lies in `A`, i.e. `A = Z[Ω]₀` and `d = 1`. The
mechanism is §2.2's freezing: past a bounded radius the row shapes stop changing and
only translate outward. **Status: EVIDENCED, not proved** — the induction that would
turn the measured law into a theorem (transport a certificate at depth `d` to depth
`d+1` by the tail shift) is stated, not closed. `π(D) ∈ A` itself is proved
independently of it (§3.2).

### 3.5 What is *not* closed: the window axes

W2g closed `(k2, k3)` over all of `Z` because `ζ2, ζ3` act **trivially** on the
finite `Γ\Q` (`ord(ρ(ζ)) = 1`, 44/44). Re-measured here on the completed graph:

| | `ζ2` and `ζ3` act trivially on a radius-6 ball |
|---|---:|
| finite-index chains | **44 / 44** (reproduces W2g) |
| infinite-index chains | **0 / 23** |

So the `(k2,k3)` closure has no analogue here, and `k0, k1` matter too because they
grow the defect. `--mode period` on two chains at `K = 1` (81 windows each) finds
`π(D) ∈ A` at 45 of 81 windows at `(L, align) = (10, 8)`. **Those 36 are truncation,
not death:** the sharpest one, window `(1,1,1,1)` of
`(TTTcTctcttc, TTTctcTcTctcttt, TTTcTcttct)`, is unsolved at `align = 8` and
`align = 10` and then **solvable with a 96-row witness at `align = 14`** (157,325
rows). Every candidate obstruction examined behaved this way. The honest statement:

- **PROVED**: layer-1 solvable over `Z` at every window actually computed.
- **EVIDENCED**: layer-1 solvable at *every* window, via `A = Z[Ω]₀` (§3.4), which
  makes the defect class irrelevant exactly as `d = 1` does in W2g.

---

## 4. Controls

Every control runs on every run and each was demonstrated able to fail. Exit 0 = all
green (a negative verdict is a *result*); exit 2 = control failure, run void.

| control | guards | how it can fail | result |
|---|---|---|---|
| C1 fixed-`h` witness `(21,48,0)` | the imported lifting calculus is the codex one | defect mismatch ⇒ exit 2 | passes every run |
| **C2 Lemma-5 identity** (`--mode identity`) | the algebraic fiat of §2.2 — the whole method | any `v` where the σ-tuple row ≠ the row traced from `build_operators_general`'s own operator ⇒ exit 2 | **25,460 checks, 0 mismatches**, all 67 chains |
| C3 corruption breaks C2 | C2 is not vacuous | dropping one term of `L1` must change some row | fires **67/67** |
| **C4 effective vanishing** | Lemma 2′ in the tree frame — that only `L0, L1` carry information | any nonzero `Ω`-row among the `L2, L3, L4` columns ⇒ exit 2 | **38,190 rows, 0 nonvanishing**; corruption of `L2` fires 67/67 |
| C5 base-coset pinning | the W2g defect (union-find re-rooting the base class) cannot recur | `σ(R), σ(U), σ(w) ≠ base` ⇒ exit 2 | passes 67/67 |
| **C6 finite specialization** (`--mode finite`) | the extended machinery is a *generalisation*, not a different computation | run the tree code on the 44 finite-index chains: `d`, `\|Ω\|` and `image_is_ker_eps` must equal `out/w2g_omega_all.json` exactly | **44/44 agree**, `d = 1`, `\|Ω\| = 2` |
| C7 witness re-multiplication | the Hermite membership answer | recompute `Σ c·row` and compare with `π(D)` term by term | 23/23 |
| C8 explicit module lift + mutation | the theorem's conclusion, constructively, with no `Ω` machinery | `D + Σ L_i x_i ≠ 0` under the unmodified `apply_operator`; and dropping one `L4` term must leave a residual | 22/23 verified; corruption leaves 8–20 terms |
| **C9 positive control** (`--mode probe`) | **the detector can fire at all** | on the real systems nothing can ever be certified, so the control runs on a **synthetic** system (`L0, L1` doubled ⇒ lattice `2A`): a *primitive* `Ω`-difference defect **must** be certified not-in-image, its **double must** be certified in-image, and the independent `one_hop_system` solver **must** agree the primitive one is unsolvable mod 2 | fires / silent / agrees, **23/23** |

C2 and C4 are the load-bearing pair, and they are the direct descendants of W2g's
lesson: *a control must assert the load-bearing step itself, not a shadow of it.*
C2 asserts Lemma 5 (the fiat that makes the infinite case finite) against the
operators the certificate really produces; C4 asserts the fiat that lets only `L0`
and `L1` be considered. Both are broken on demand by a one-term corruption. C6 is
the third: it forbids the extended code from being a *different* computation that
happens to agree in spirit.

Reproduce (each command is its own guarded run):

```bash
python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- python3 \
  fable/proofs/checkers/infinite_index_liveness.py --mode identity --radius 6 \
  --json fable/proofs/checkers/out/w2h_identity.json

python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- python3 \
  fable/proofs/checkers/infinite_index_liveness.py --mode finite --radius 8 \
  --json fable/proofs/checkers/out/w2h_finite_specialization.json

python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- python3 \
  fable/proofs/checkers/infinite_index_liveness.py --mode image --chains 0:12 \
  --radii 10,12 --align 10 \
  --json fable/proofs/checkers/out/w2h_image_a.json
# ... --chains 12:23 -> w2h_image_b.json

python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- python3 \
  fable/proofs/checkers/infinite_index_liveness.py --mode image --chains 0:12 \
  --radii 6,8,10,12 --align 0 \
  --json fable/proofs/checkers/out/w2h_margin_a.json
# ... --chains 12:23 -> w2h_margin_b.json

python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- python3 \
  fable/proofs/checkers/infinite_index_liveness.py --mode lift --rho 2 \
  --resid-rho 4 --k 0 --chains 0:9 --radii 12 --align 10 \
  --json fable/proofs/checkers/out/w2h_lift_a.json
# ... --chains 9:16 -> w2h_lift_b.json ; --chains 16:23 -> w2h_lift_c.json
# ... --rho 3 --resid-rho 6 --chains 9:10 -> w2h_lift_c9.json

python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- python3 \
  fable/proofs/checkers/infinite_index_liveness.py --mode probe --chains 0:12 \
  --radii 10 --align 8 \
  --json fable/proofs/checkers/out/w2h_probe_a.json
# ... --chains 12:23 -> w2h_probe_b.json

python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- python3 \
  fable/proofs/checkers/infinite_index_liveness.py --mode period --k 0 \
  --radii 10 --align 8 --radius 6 \
  --json fable/proofs/checkers/out/w2h_zeta_scan.json
# ... --chains 0:2 --k 1 -> w2h_period.json  (81 windows per chain)
```

---

## 5. The honest restatement: where the W2 obstruction gap actually lives

### 5.1 The four facts, and what they now add up to

| fact | source | status |
|---|---|---|
| the census family is **unbounded**: 17 / 36 / 55 / 67 / 91 / 106 essential chains at caps 12–17, strictly increasing, no plateau; caps are ceilings so every count is a lower bound | W2c | **EVIDENCED** |
| a **six-parameter normal form** `(k1,p1,k2,p2,k3,p3)` plus `g` generates the family exactly, and each chain has exactly one tuple | W2d (c.2, c.3), W2f §1 | **verified**, 67/67 |
| liveness does **not** factor through `cyc(S)` — the one reduction that would have collapsed the index set is dead | W2e | **PROVED** |
| layer 1 obstructs nothing on the 44 finite-index chains, at **every** window | W2g | **PROVED** |
| layer 1 obstructs nothing on the remaining 23, at every window computed | **W2h** (§3.2) | **PROVED + WITNESSED** |

**Conclusion (PROVED, at the stated scope).** *The period-two quotient's layer 1 is
obstruction-free for the entire cap-15 census.* There is no `Z`-linear, no mod-`p`,
no double-coset-character death certificate for any of the 67 baselines. Any death
of the depth-four signature through this quotient must come from **layer ≥ 2** or
from **outside the quotient**.

This also finishes the correction W2f §6.5 began. W2b's live/dead split, W2e's 161
"counterexamples" and W2f's five strata are now known to be statements about the
**one-hop truncation** for the whole family, not about the relation module. The
correct layer-1 index of a census baseline is not a bit; it is the constant `1`.

### 5.2 The codex obligation, restated

`AK3_DEPTH4_PERIOD_TWO_FULL_LIFT_BOUNDARY.md` (1.6)–(1.10) writes the literal
period-two lifting problem for the codex witness as

```text
∃ F ∈ H_fin,  ∃ k = (k0..k4) ∈ [N,N]^5 :   R(F; k) = 1   in F(c,t).     (1.10)
```

`F` is the **layer-1** freedom (relation-module corrections, `M = N_ab ≅ Z[Q/⟨c⟩]`);
`k` is the **layer-2** freedom (`[N,N]`, with the next honest obstruction living in
`[N,N]/[[N,N],N]`, per `AK3_DEPTH4_HANDOFF.md`). The codex universal-noncancellation
obligation is the `k`-half. W2's census established that (1.10) is *anchored*: every
member of that family corrects the **witness's** conjugators by elements of `N` and
`[N,N]`, so every member has the witness's `Q`-image, and each other census baseline
generates a lift family **disjoint** from (1.10).

Three sentences, which is what the restatement amounts to:

1. **Every census baseline is live at layer 1** (W2g + W2h), so the escape hatch
   W2 named — *"a dead baseline needs no tower"* — is now **closed**: not one of the
   67 is disposed of before layer 2.
2. Therefore **each baseline spawns its own layer-2 obligation** of exactly (1.10)'s
   shape, over its own residual family `R_b(F; k) ∈ [N,N]`, and a completed
   noncancellation theorem over (1.10) closes the witness's family **only**.
3. The number of such obligations is unbounded and growing with the cap, so a
   per-baseline layer-2 argument **cannot terminate**; closing the depth-four
   signature through this quotient requires a layer-2 argument uniform over the
   whole census, or a different quotient.

### 5.3 Does every live baseline spawn its own layer-2 obligation?

**Yes — PROVED, given the census.** The argument has no computational content and
is worth stating because its two halves come from different notes:

- (a) *Disjointness.* (1.10)'s corrections lie in `N` and `[N,N]`, both of which are
  trivial in `Q`; so the `Q`-image of every member of (1.10) is the witness's chain
  `(TTctcTctc, TTTcttcTctt, TTcttcTc)`. A census chain different from the witness is
  therefore reached by no member of (1.10) (W2, *Why this matters*).
- (b) *No layer-1 escape.* For a baseline to need no layer-2 argument it would have
  to fail already in `N/[N,N]` — i.e. its defect would have to lie outside
  `Σ_i L_i M`. W2g proves that impossible for 44 chains at every window; W2h proves
  `π(D) ∈ A` for the other 23 at every window computed, with witnesses.

So the obligation count is at least the essential-chain count: **≥ 67 at cap 15,
≥ 106 at cap 17, with no plateau in sight.**

### 5.4 Is there a finite-description hope at layer 2?

Layer by layer, the honest answer:

| layer | finite description? | what it is | status |
|---|---|---|---|
| 0 (the baselines themselves) | **yes** | W2d's six-integer normal form + `g`; exact hit on the enumerated chains, one tuple per chain | **verified** |
| 1 (`N/[N,N] = M`) | **yes, and it is trivial** | the pair `([Q:Γ], d)`; `d = 1` on all 67, computable in milliseconds per chain, constant over the whole parameter lattice | **PROVED** (44) / **PROVED + EVIDENCED** (23) |
| 2 (`[N,N]/[[N,N],N] ≅ Λ²M`) | **yes, in principle — the same one** | `Γ = ⟨R,U,w⟩` acting on unordered pairs of `Q/⟨c⟩`-vertices; the same five operators, the same telescoping (below) | **PROVED** that the machinery transfers; the invariant itself is **uncomputed** |

What is actually known at layer 2, kept separate from what is hoped. The codex note
`AK3_DEPTH4_PERIOD_TWO_FULL_LIFT_BOUNDARY.md` §3 makes layer 2 completely explicit,
and reading it changes the answer this section would otherwise have given:

```text
W := γ₂N/γ₃N = [N,N]/[[N,N],N] ≅ Λ²M                                  (3.1)
L_r^{(2)}(m ∧ n) := Σ_{g ∈ Q} a_{r,g} (g m ∧ g n)                     (3.5)
[R(F; k)] = Θ(F) + Σ_{r=0..4} L_r^{(2)} Y_r                            (3.6)
```

with **the same integral coefficients `a_{r,g}`** as the layer-1 operators `L_r`
(the reason given there is that `γ₂N` is central mod `γ₃N`, so only the `Q`-class of
a prefix acts).

- **PROVED (structural, from (3.1)/(3.5)):** `Λ²M` with the *diagonal* action
  `g·(m ∧ n) = gm ∧ gn` is a left `Z[Q]`-module, and `L_r^{(2)}` is nothing other
  than the group-ring element `L_r` acting on it. Therefore **W2g's Lemmas 1 and 2
  transfer verbatim to layer 2** — Lemma 1 is an identity between group-ring
  elements (`L2 = 1 − X`, `L4 = w − 1`, `L3 + L4 = U⁻¹ − 1`, all `ε(L_i) = 0`) and so
  is independent of which module they act on, and the telescoping identity
  `(g₁···g_k − 1)u = Σ_j (g_j − 1)(g_{j+1}···g_k u)` is a statement about a left
  `Z[Q]`-module, which `Λ²M` is. Hence

  ```text
  L2^{(2)}W + L3^{(2)}W + L4^{(2)}W = I_Γ · W ,   W / I_Γ W = a double-coset module
  ```

  with `Γ = ⟨R, U, w⟩` — **the same `Γ`**. So the answer to "is there a finite
  description at layer 2 analogous to the normal form at layer 0" is not the flat
  "none known" it looked like: the *same* machinery applies, and the layer-2
  obstruction group is the image of `L0^{(2)}, L1^{(2)}` in that quotient. **This is
  computable by the code in this note's checker with one change of basis** (from
  `Q/⟨c⟩` to unordered pairs of distinct `Q/⟨c⟩`-vertices).
- **The one structural difference, and it is exactly where an obstruction could
  hide.** `M` is a *permutation* module — `Q` permutes the basis `Q/⟨c⟩` — so
  `M/I_Γ M = Z[Ω]` is **free** on `Ω`. `Λ²M` is only a **signed** permutation module:
  `g(e_u ∧ e_v) = e_{gu} ∧ e_{gv}`, which is `−e_{gv} ∧ e_{gu}` when the diagonal
  action reverses the pair's order. So `Λ²M / I_Γ Λ²M` is `Z[Γ\B]` (`B` = unordered
  pairs) **modulo `2x = 0` on every orbit some `γ ∈ Γ` reverses** — a double-coset
  module that can carry **2-torsion**, which `Z[Ω]` cannot. `d = 1` was possible at
  layer 1 partly because the target was free; a torsion summand is a place a defect
  can fail to be hit for reasons no augmentation-style invariant sees, and it lives
  at `p = 2` — the prime W2f found permissive and therefore never binding at layer 1.
  *(Stated as a structural observation. It is not computed here, and "can carry
  torsion" is not "does".)*
- **SPECULATION:** that a completed noncancellation theorem over (1.10) would extend
  uniformly to the other baselines; that the six-parameter normal form controls the
  layer-2 data as well as it controls the layer-0 data; that the 2-torsion just
  described is nonzero on any census baseline.

### 5.5 Status ledger for §5

| claim | status |
|---|---|
| layer 1 obstructs nothing on all 67 census chains at the windows computed | **PROVED** |
| … at *every* window, for the 44 | **PROVED** (W2g) |
| … at *every* window, for the 23 | **EVIDENCED** (§3.4's margin law) |
| every census baseline spawns its own layer-2 obligation | **PROVED** (§5.3, given the census and disjointness) |
| the number of such obligations is unbounded | **EVIDENCED** (four caps, strictly increasing; caps are ceilings) |
| a per-baseline layer-2 tower cannot terminate | **PROVED**, given the previous two lines at their stated strengths |
| layer 2 (`Λ²M`, diagonal action) is a `Z[Q]`-module on which the SAME operators act, so W2g Lemmas 1–2 transfer and a double-coset invariant `d₂` is defined | **PROVED**, from (3.1)/(3.5) as cited |
| `Λ²M/I_Γ Λ²M` is a *signed* double-coset module and can carry 2-torsion, unlike the free `Z[Ω]` of layer 1 | **PROVED** (structural) |
| the value of `d₂`, and whether that torsion is nonzero on any census baseline | **UNCOMPUTED** — §7 |
| layer 2 collapses the way layer 1 did | **SPECULATION** in both directions |
| anything about the free-group depth-four class, the bridge, AK(3), stable AC, or AC | **no claim** |

---

## 6. Scope and nonclaims

- **PROVED vs EVIDENCED vs SPECULATION** are used in the strict senses of §5.5 and
  are not interchangeable anywhere in this note.
- **The 23 results are per-window proofs, not a window-independent theorem.** Unlike
  W2g, the `(k2,k3)` axes are *not* closed here: `ζ2, ζ3` act nontrivially on `Γ\Q`
  for all 23 (§3.5). The all-window statement is carried by the margin law, which is
  measured, not proved.
- **A negative membership answer is never read as death.** Every one encountered was
  a radius artifact and dissolved when the enumeration grew; §3.5 exhibits the
  extreme case (96-row witness at `align = 14`). No chain is reported as obstructed,
  and none was.
- **The explicit lift routing is a heuristic, not part of the proof.** It succeeds on
  22 of 23; the one failure is a search failure. Its *successes* are hard evidence,
  because each is checked by exact module arithmetic with the unmodified operators.
- **Caps are ceilings.** The census is complete only for `max(|R|,|S|,|U|) ≤ 15` and
  `|g| ≤ 5`. "All 67" means all 67 *at that cap*; the family grows.
- **Layer-1 liveness is not liftability.** `D ∈ Σ L_i M` says the obstruction dies in
  `N/[N,N]` and moves to layer 2. Nothing here is a statement about the full lift,
  the noncancellation tower, or the codex route succeeding or failing.
- No claim about the free-group depth-four class, the bridge, AK(3), stable AC, or
  AC. This is a scope-quantification of one quotient layer of one signature.

---

## 7. The single most decisive next question

> **What is `d₂` — the double-coset invariant of the SAME `Γ = ⟨R,U,w⟩` acting on
> `Λ²M`?**

§5.4 shows the layer-2 lifting equation (3.6) is a `Z[Q]`-module equation with the
**same five operators**, so W2g's Lemmas 1 and 2 transfer and the layer-2 obstruction
group is

```text
image of  L0^{(2)}, L1^{(2)}  in   Λ²M / I_Γ Λ²M
```

— a signed double-coset module on `Γ`-orbits of unordered pairs of `Q/⟨c⟩`-vertices.
This is the exact analogue of the computation this note and W2g just did, one change
of basis away from the existing checker, and it decides the shape of everything
downstream:

- **If `d₂ = 1` and the torsion part is trivial:** the period-two quotient obstructs
  nothing at layers 1 *or* 2, uniformly over the whole census, and the codex tower's
  noncancellation obligation over (1.10) cannot be what kills the signature — the
  route has to be re-aimed rather than completed.
- **If `d₂ > 1`, or the 2-torsion summand is nonzero and misses the defect, on some
  parameter stratum:** that stratum is the first real obstruction the programme has
  produced, with a closed-form certificate and a finite description — exactly the
  uniform layer-2 argument §5.2 says is required, and it would apply to **all**
  baselines in the stratum at once, breaking the per-baseline explosion of §5.3.
- **If the pair-orbit space `Γ\B` is infinite** (it will be, for the 23 chains of
  this note, and possibly for the 44 too since `B` is much bigger than `Q/⟨c⟩`):
  §2's core-plus-cones machinery and Lemma 5's fixed-state-tuple reduction are
  already the tools for that case.

Two discipline notes for whoever runs it, both paid for by this programme's own
history. First, run C9 **before** reading any result: `d = 1` everywhere at layer 1
means a layer-2 detector that never fires would look identical to a layer-2 detector
that is broken, so demonstrate firing on a synthetic system first. Second, the
2-torsion lives at `p = 2` — the prime W2f found permissive and therefore the one
whose nulls nobody has been reading. Do not let a layer-2 `p = 2` certificate be
believed before it has survived a corruption control.

---

## Summary of status

| claim | status |
|---|---|
| `Γ\Q` = finite Stallings core + cones of the Cayley tree of `Q`; exact, and degenerates to the core when the core is complete | **proved** |
| Lemma 5: `π(L0 e_v)`, `π(L1 e_v)` are `±1`-signed sums of `Ω`-classes of a fixed 6- (resp. 4-) element state tuple under the right `Q`-action | **proved**, and **machine-verified** against the operators `build_operators_general` returns — 25,460 checks, 0 mismatches, all 67 chains, corruption fires 67/67 |
| `π(L2), π(L3), π(L4) = 0` in the tree frame (W2g Lemma 2′ extended) | **machine-verified**, 38,190 rows, 0 nonvanishing; corruption fires 67/67 |
| base coset pinned: `σ(R) = σ(U) = σ(w) = base` | **verified**, 67/67 |
| the extended machinery, run in its finite specialization, reproduces `w2g_omega_all.json` exactly (`d = 1`, `\|Ω\| = 2`, `image_is_ker_eps`) | **verified**, 44/44 |
| `π(D)` is an **integer** combination of the rows ⇒ `D ∈ Σ_i L_i M` ⇒ layer-1 solvable over `Z` | **PROVED + WITNESSED**, 23/23 chains, every witness re-multiplied out |
| explicit `x` with `D + Σ_i L_i x_i = 0` under the unmodified `apply_operator` | **VERIFIED**, 22/23; the miss is a routing (search) failure |
| `ρ = 2` hops suffice where W2b's `ρ = 1` does not | **verified**, 21/23 |
| every `Ω`-class of depth `≤ L − μ` has `[ω] − [ω_base] ∈ A`, `μ` constant in `L` (⇒ `A = Z[Ω]₀`, ⇒ every window) | **EVIDENCED**, exact on 19/23 over `L = 6,8,10,12` |
| `ζ2, ζ3` act trivially on `Γ\Q` | **verified**: 44/44 finite-index (reproduces W2g), **0/23** infinite-index — the `(k2,k3)` axes are NOT closed here |
| a window-independent death certificate for any census chain | **does not exist** on the 44 (W2g); **none found and none expected** on the 23, at every window computed |
| layer 1 obstructs nothing on the whole cap-15 census (67 chains) | **PROVED** at the windows computed |
| every census baseline spawns its own layer-2 obligation; their number is unbounded | **PROVED** / **EVIDENCED** (§5.3) |
| layer 2 is `Λ²M` with the same operators, so `d₂` is defined and computable | **PROVED** (§5.4); `d₂` itself **uncomputed** |
| anything about lifting, the bridge, AK(3), stable AC, or AC | **no claim** |

## Post-hoc correction (cycle 18)

`W2I_LAYER2_D2.md` (§1.3–1.4) corrects two points of this note's part (b):
(i) the Λ²M identification needs two hypotheses this note did not state (N
free on the Schreier basis — true; and the "same coefficients" variation
identity (3.5), which the source asserts in one sentence — everything at
layer 2 is conditional on it); (ii) the "d₂ = 1 ⇒ blind" branch as framed
here is unreachable, because (3.16)/(3.17) already kill every L^{(2)} in the
full Q-coinvariants — the honest analogue of d = 1 is "operator image =
ker Ξ_Z", which W2i then proves (Ξ_Z is an isomorphism). The predicted
layer-2 2-torsion is identically absent: Γ is torsion-free on all 67 chains,
a reason independent of the operators.

---

## Post-hoc correction (same day, cycle 16): Lemma 5's `L0` row gains `h1`; every conclusion holds

`W2J_THETA_RESIDUAL.md` §1 found that `build_operators_general`'s `L0` column
omits a `q(h1)` factor, so on the 59 of 67 census chains with `q(h1) ≠ 1` this
note's `π(L0 e_v)` — and the `sigma_terms` shortcut derived from it — were
computed from the wrong operator. `W2K_CORRECTED_REVERIFY.md` §6 re-derives the
row formula and re-runs this note's own modes on the corrected operators.

**Lemma 5, corrected.** With `X = h2 S h2⁻¹ ∈ Γ` and `U⁻¹h3 S h3⁻¹ = w ∈ Γ`,
the extra right factor `h1` survives the same two cancellations —
`Γ h2 S h1 = Γ h2 h1` and `Γ U⁻¹h3 S h1 = Γ h3 h1` — so the corrected row is
this note's row with **`h2 → h2·h1` and `h3 → h3·h1`** in the four bridge terms:

```text
π(L0 e_v) = [ω(σ(R)·v)] + [ω(σ(h2h1 R)·v)] + [ω(σ(h3h1 R)·v)]
          − [ω(σ(A)·v)] − [ω(σ(h2h1 A)·v)] − [ω(σ(h3h1 A)·v)]

π(L1 e_v)  unchanged            π(L2 e_v) = π(L3 e_v) = π(L4 e_v) = 0
```

Every coefficient is still `±1` and the state tuple is still fixed and finite,
so §2.2's three consequences and the whole decidability argument go through
verbatim.

| control | result |
|---|---:|
| identity checks `row_sigma` vs `row_direct`, corrected form, all 67 chains | **25,460**, mismatches **0** |
| `L2, L3, L4` row checks / nonvanishing | 38,190 / **0** |
| base-coset pinning `σ(R) = σ(U) = σ(w) = base` | 67 / 67 |
| corruption breaks identity / vanishing | fires 67 / 67 |
| **the OLD Lemma 5 row against the corrected `L0`** | **fails 316 / 440** — the corrected form is not vacuous |

**The results.**

| | this note | corrected |
|---|---:|---:|
| infinite-index chains | 23 | 23 |
| `π(D)` an integer combination of the rows | **23** | **23** |
| witnesses re-multiplied out | 23 | **23** |
| `d_eff = 1` | 23 | **23** |
| chains with a death certificate | 0 | **0** |
| explicit `x` at the published settings (`--rho 2 --resid-rho 4 --radii 12 --align 10`) | 21 of 23 | **21 of 23** |
| margins seen (radii 10,12, align 10) | `{1..8}` and `{1,2,3,5,9,11}` | **`{1,…,5}` and `{1,2,3,5}`** |
| `coverage_depth_min` | 4 / 1 | **7 / 7** |

The margins **shrink** and the coverage front runs **deeper**: the corrected
`L0` covers more of `Z[Γ\Q]`, so §3.4/§3.5's margin law is on better evidence
than this note had. Its status is unchanged — **EVIDENCED**, not proved:
`A = Z[Ω]₀` still rests on the front advancing with the radius.

One chain (`TTTctttcTTTcttc, cTTctttcTTctc, TTcTcttc`, `g = c`) misses at
radii 8–12 with `align 0` — **on both operator sets**, so it is the enumeration
radius and not the correction; at `--radii 14,16 --align 6` it lands with a
re-verified 10-term witness. That is exactly the behaviour §3.5 documents.

**The verification upgrade.** This note's "explicit `x` … verified with the
unmodified `apply_operator`" is a check *through the operators that produced
it*. The W2k driver re-tests the same `seeded_lift` output in `F(c,t)`
(`n_r = σ(x_r)`, replay the recurrence, assert the residual is in `[N,N]`):

* corrected operators — **21 solved, 21/21 literally verified**;
* shipped operators — 21 solved, **6 verified, 15 literally rejected**.

So the *conclusion* "layer 1 obstructs nothing on the whole census" is
unchanged and now carries a free-group certificate; the *individual witnesses*
this note shipped were, on 15 of 23 chains, not layer-1 solutions.

Run records: `checkers/out/w2k_inf_identity_a.json` / `_b`,
`w2k_inf_image_a.json` / `_b`, `w2k_inf_lift_a.json` / `_b` / `_c`,
`w2k_inf_liftlit.json`.
