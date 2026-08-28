# W2g: the g-stratum has no death certificate — on its finite-index part, death is impossible

Date: 2026-08-28 · Checker: `checkers/g_stratum_death.py`
(imports `period_two_parametric_solvability.py`, `period_two_liveness_invariance.py`,
`period_two_baseline_liveness.py` and the codex lift certificate unmodified; guarded
foreground runs).
Run records: `checkers/out/w2g_gamma.json`, `w2g_omega_all.json`,
`w2g_omega_stratum.json`, `w2g_period_all.json`, `w2g_period_stratum.json`,
`w2g_probe.json`, `w2g_quotients_s3.json`, `w2g_lift_s3.json`, `w2g_lift_s7.json`,
`w2g_lift_s8.json`.

Answers `W2F_PARAMETRIC_SOLVABILITY.md` §8: *"does a non-abelian quotient of `Q`
kill `S2` (`g ∉ {"", "TTc"}`, 22 chains)?"*

---

## 0. Verdict

| question | answer | status |
|---|---|---|
| Is there a window-independent **death certificate** for the g-stratum? | **No.** | see below |
| …because the search failed? | **No — because on the stratum's finite-index part death is impossible.** For **15 of the 22** chains the operator image is provably *all* of `ker(ε)`, so `D + Σ L_i x_i = 0` is solvable over **Z** at **every** window (every `k0,k1,k2,k3 ∈ Z`, every `K`, every prime). | **PROVED** |
| Is that backed by an explicit solution, or only by the quotient argument? | **By both.** At **27 windows** W2f calls DEAD mod 2, 3 **and** 5 (3 chains × 9 windows, covering all three `g` values of the finite-index part), an explicit integral `x = (x₀..x₄)` is constructed and `D + Σ L_i x_i = 0` is verified term by term with the unmodified `apply_operator`. | **PROVED + WITNESSED** |
| Then what are W2f's 1,782 zero-solvable windows? | **Artifacts of the one-hop support truncation** on those 15 chains. W2f's numbers are correct *as one-hop numbers*; the truncation, not the algebra, is what is empty. | **PROVED** |
| The invariant that could have killed the stratum, in closed form | `λ = χ_{Ω₀}` on `Ω = Γ \ Q / ⟨c⟩` with `Γ = ⟨R, U, w⟩`. It annihilates all five operators mod `p` iff `p \| d`, and kills the defect iff `p ∤ m`. Measured: **`d = 1` at every window of all 44 finite-index chains**, so no `λ` survives at any prime. | **PROVED** |
| Does the detector work at all? | **Yes** — on a synthetic `d = 2` system it certifies an odd-class defect dead mod 2 and the independent one-hop solver agrees; it stays silent on the even-class defect, which the one-hop solver finds solvable mod 2. | **verified**, 15/15 chains |
| Remaining gap | 7 of the 22 stratum chains have `[Q : Γ] = ∞`; the finite computation is silent there. | **open** |

---

## 1. What layer-1 liveness actually asks

W2b builds the lifting equation

```text
D + Σ_{i=0..4} L_i x_i = 0        in  M = Z[Q/⟨c⟩],   Q = ⟨c, t | c²⟩
```

where `x_i` is the relation-module class of the correction `n_i ∈ N` applied to
conjugator `i`. Since `N ↠ M = N/[N,N]`, the `x_i` range over **all of `M`**.
`period_two_baseline_liveness.one_hop_system` restricts them to the vertices whose
operator image already meets `supp(D)` — a decidable **truncation** of the question,
which W2b flags in its own nonclaim ("support escape possible") and which W2e and
W2f inherit.

This note works with the untruncated question, which turns out to be decidable by
structure rather than by search.

---

## 2. The structure

Write `X = h2 S h2⁻¹`, `w = g t g⁻¹`, `bridge = h2 + U⁻¹h3`, and use W2e §4.1's
closed forms.

**Lemma 1 (operator identities).** For every window,

```text
L2 = 1 − X ,   X = U⁻¹R          L4 = w − 1          L3 + L4 = U⁻¹ − 1
ε(L_i) = 0   for i = 0..4
```

*Status: machine-verified as exact group-ring equalities at every window the checker
touches (`identities_ok`), on the operators `build_operators_general` actually
returns.* `X = U⁻¹R` is the slot condition, so `L2` is window-independent, and
`L3, L4` depend on the window only through `g` — exactly W2e's "representative-stable"
half of the system.

**Lemma 2 (telescoping).** Let `Γ = ⟨X, U, w⟩ = ⟨R, U, w⟩ ≤ Q`. Then

```text
L2·M + L3·M + L4·M  =  I_Γ·M ,        M / I_Γ M  ≅  Z[Ω]   free,
Ω = Γ \ Q / ⟨c⟩  (the Γ-orbits on Q/⟨c⟩)
```

*Proof.* `⊆` is Lemma 1. For `⊇`, a word `γ = g₁···g_k` in the generators satisfies
`γu − u = Σ_j (g_j − 1)(g_{j+1}···g_k u)` — the peeled generator is always leftmost,
so **no left prefix survives** and every summand is one of `±L2 e`, `±L4 e`,
`±(L3+L4) e` (inverses via `(g⁻¹−1)y = −g⁻¹(g−1)y`, again a single operator column:
e.g. `(X⁻¹−1)e_v = L2 e_{X⁻¹v}`). Hence `[γ u] = [u]` in the quotient, and the quotient
is free on the Γ-orbits. ∎

The six moves and the operator columns they cost are tabulated in `move_table`;
`--mode lift` uses exactly them to build the explicit solutions of §3.3.

**Lemma 2′ (Lemma 1 made effective).** In the computed `Z[Ω]`, the images of the
`L2, L3, L4` columns **vanish identically** — equivalently `trace(X) = trace(U) =
trace(w) = ` the base coset. This is asserted by `omega_row_set(...)[i∈{2,3,4}] == 0`
on every chain in `--mode omega` and `--mode probe`, and corrupting one term of `L2`
must break it. *It is the control that mattered — see §2.2.*

**Lemma 3 (finite parameterisation).** If `[Q : Γ] < ∞`, then `Γ\Q` is a finite right
`Q`-set; let `P ≤ Sym(Γ\Q)` be the image of `Q`. Writing `s_γ = Γγ`, the `Ω`-image of
the column `L_i e_v` is

```text
π(L_i e_v)_j  =  Σ_{γ ∈ supp(L_i),  ω(s_γ · v) = j}  coef_i(γ)
```

which depends on `v` **only through** `ρ(v) ∈ P`. So the set of all `Ω`-images, over
all `v ∈ Q/⟨c⟩` at once, is computed by a finite loop over `P`.

*Status: machine-verified two ways.* Control `omega_rows_direct` recomputes
`π(L_i e_v)` vertex by vertex for a ball of words `v` and requires every row to occur
in the `P`-enumerated set (0 missing rows, every run); and the §2.2 diagnostic
compares a fully `P`-free evaluation of `(1−X)e_v`, `(U⁻¹−w)e_v`, `(w−1)e_v` against
the `P`-row for the same `v` on 15 explicit cases — **agreement 15/15**.

**Theorem.** Assume `[Q:Γ] < ∞` and `|Ω| = 2`. Every `L_i` has augmentation 0, so
every row lies in `Z·(1,−1)`; let `d = gcd` of the entries of the `L0/L1` rows
(legitimate by Lemma 2′) and `m = ` the mass of `D` on `Ω₀`. Then

```text
Σ_i L_i M = π⁻¹( d·Z·(1,−1) ) ,   so
    D ∈ Σ_i L_i M           ⟺  d | m
    D ∈ Σ_i L_i M ⊗ F_p     ⟺  ( p | d  ⇒  p | m )
```

In particular **`d = 1 ⇒ Σ_i L_i M = ker(ε)`**, and since every census defect has
augmentation 0 (W2b: `DEAD (augmentation) = 0`), every window of such a chain is
layer-1 solvable **over Z**.

The candidate death certificate is therefore exactly

```text
λ = χ_{Ω₀} : Q/⟨c⟩ → Z ,   λ(v) = 1 if Γ v ⟨c⟩ = Ω₀ else 0
```

— a **double-coset character** of `Γ = ⟨R,U,w⟩`, not a character of a finite quotient
of `Q`. (§6 explains why the finite-quotient search W2f §8 proposed cannot see it.)

### 2.1 The window axes are closed, not sampled

`h0` and `h1` **do not occur in any `L_i`** (only in the defect), so `d` does not
depend on `k0, k1` at all. `h2 = h2_base·ζ2^{k2}` and `h3 = h3_base·ζ3^{k3}` enter the
rows only through `trace(h) ∈ Γ\Q`, and `trace(h_b ζ^k) = trace(h_b)·ζ^k` is periodic
in `k` with period `ord(ρ(ζ))`.

> **Measured (`--mode period`, all 44 finite-index chains): `ord(ρ(ζ2)) = ord(ρ(ζ3)) = 1`.**
> Both centralizer generators act **trivially** on `Γ\Q`. So `d` is literally constant
> over `(k2,k3) ∈ Z²`.

Hence `d = 1` is an invariant of the pair (chain, `g`) — not of a window, not of a box.
Since `d = 1` makes `m` irrelevant, the `k0,k1` axes need no argument at all. That is
what makes the conclusion window-independent in the strong sense.

### 2.2 A defect in this checker, found by a control and fixed

The first version of `--mode probe` "mutated" `L2` and asked whether `d` changed. That
control was **inert by construction**: `omega_invariant` reads `d` off the `L0/L1`
rows only, so no corruption of `L2` could ever move it, and the result was not even
folded into the pass condition. Replacing it with the guard the shortcut actually
needs — *assert that the `L2, L3, L4` rows vanish identically* (Lemma 2′) — made it
**fail**.

The definitive experiment (`scratchpad`, reproduced by `--mode probe`'s controls) was
to compute the `Ω`-class sums of `(1−X)e_v`, `(U⁻¹−w)e_v`, `(w−1)e_v` directly, with
no `P` machinery, for five explicit `v` each, and compare with the `P`-rows. The two
agreed on all 15 cases — so the row construction was correct — but the shared value
was nonzero for `L4`, and the diagnostic printed

```text
trace(1) = 0    trace(R) = 1    trace(U) = 1    trace(w) = 2    trace(X) = 0
```

`R`, `U`, `w` **generate** `Γ`, so each must trace back to the base coset. They did
not. Cause: `Folded._drain` let union-find re-root the base class, so `find(0) ≠ 0`
and `CosetTable` took index 0 — no longer the base — as `Γ·1`. Every `trace`, hence
every `Ω`-class, hence every `d` and `m`, was computed from the wrong coset. Fixed by
pinning the base class's root; after the fix

```text
trace(R) = trace(U) = trace(w) = trace(X) = base,   rows_i2 = rows_i3 = rows_i4 = 0
```

**What the bug changed in the results.** The pre-fix run reported `d = 2` for 3 chains
(with `m` even) and `d = 1` for 41; post-fix **`d = 1` for all 44**, so the theorem
covers *more* chains, not fewer, and the `d = 2` caveat disappears. The pre-fix
`--mode lift` could route only 8 of 24 defect vertices (it was routing them to the
wrong `Ω` base); post-fix it routes **all** of them and closes every window it is
given. The Stallings *index* (44 finite / 23 infinite) is unaffected — index does not
depend on which state is labelled base — and so is `--mode quotients`, which never
uses `CosetTable`.

---

## 3. Results

### 3.1 `Γ = ⟨R, U, w⟩` in `Q` (`--mode gamma`, all 67 census chains)

| `[Q : Γ]` | chains | `\|Ω\|` | `\|P\|` |
|---|---:|---:|---:|
| 4 | **44** | 2 | 12 |
| ∞ | 23 | — | — |

Split by W2f's labels: 15 of the 22 g-stratum chains and 18 of the 21 live chains have
index 4 — **`[Q:Γ]` does not separate live from dead**, the first sign that the
deadness is not living in this quotient.

Folder controls (each returns a known value, each able to fail):
`⟨t⟩ → ∞`, `⟨c,t⟩ = Q → 1`, `ker(Q → C₂, c ↦ 1) = ⟨c, tct⁻¹, t²⟩ → 2`, `⟨c,t²⟩ → ∞`.
All pass.

### 3.2 The invariant `d` and the defect class `m`

| | all 67 | g-stratum (22) |
|---|---:|---:|
| `[Q:Γ] = 4` | 44 | 15 |
| …of those, `d = 1` for **every** `(k2,k3) ∈ Z²` | **44** | **15** |
| …of those, `d ≥ 2` | 0 | 0 |
| **chains with a death certificate (`p \| d` and `p ∤ m`)** | **0** | **0** |
| `[Q:Γ] = ∞` (method silent) | 23 | 7 |

The g-stratum's finite-index part is `g ∈ {Tc (6), cTTc (6), TcTTc (3)}`; the silent
part is `g ∈ {c (3), Tc (2), cTTc (1), cTTTc (1)}`.

For all 44: `Σ_i L_i M = ker ε`, so `D ∈ Σ_i L_i M` at *every* window. Layer-1 death
is impossible for them — at any `K`, any gauge representative, any prime. W2f records
`0/81` windows solvable mod 3 and mod 5 for each of the 15 stratum members; those
zeros are the one-hop truncation, not the module.

### 3.3 Explicit verified solutions at windows W2f calls dead

`--mode lift` builds `x` out of Lemma 2's moves (route each defect vertex to its
`Ω`-class base; then one `L0` column to cancel the residual class) and checks
`D + Σ L_i x_i` with the unmodified `apply_operator`.

| chain | `g` | windows | one-hop dead (2,3,5) | **explicit solution verified** |
|---|---|---:|---:|---:|
| `(TTcTTctcTcttt, TTTcttcTctt, TcTTcTctcTcttt)` | `TcTTc` | 9 | 9 | **9** |
| `(cTcTctcTTcttc, TTTcttcTctt, TcTTcttc)` | `Tc` | 9 | 9 | **9** |
| `(cTcTctcTTcttc, TTTcttcTctt, cTTTcttcTTcttc)` | `cTTc` | 9 | 9 | **9** |

27 of 27. A typical solution has `x_terms = [1, 0, 205, 442, 477]` — 1,125 module
terms, all integral, `residual_after_lift = 0`. Dropping one term of `L4` leaves 34
residual terms, so the verification is not vacuous.

This is what closes the argument: the quotient theorem says a solution exists; these
runs hand one over, term by term, at windows W2f decided were dead at all three primes.

---

## 4. Controls

Every control runs on every run and each was demonstrated able to fail.

| control | guards | how it can fail | result |
|---|---|---|---|
| C1 fixed-h witness `(21,48,0)` | the imported lifting calculus is the codex one | defect mismatch ⇒ exit 2 | passes every run |
| C2 folder vs known subgroups | the Stallings index is right | any of the four known indices wrong ⇒ exit 2 | 4/4 pass |
| C3 `omega_rows_direct` | Lemma 3's `P`-parameterisation equals a direct vertex-by-vertex evaluation | any directly-produced row missing from the `P` enumeration ⇒ exit 2 | 0 missing, every run |
| C4 operator identities | Lemma 1 is what `build_operators_general` really returns | any of `L2 = 1−X`, `X = U⁻¹R`, `L4 = w−1`, `L3+L4 = U⁻¹−1`, `ε(L_i) = 0` false ⇒ exit 2 | passes at every window |
| **C5 effective vanishing** (`l234_omega_rows_vanish`) | the shortcut in `omega_invariant` — that `d` may be read off the `L0/L1` rows alone | any nonzero `Ω`-row among the `L2, L3, L4` columns ⇒ exit 2 | **caught a real defect (§2.2)**; passes after the fix, 15/15 stratum + 44/44 all |
| C6 corruption breaks vanishing | C5 is not vacuous | dropping one term of `L2` must produce a nonzero row | fires, 15/15 |
| **C7 positive control** (`--mode probe`) | **the detector can fire at all** | on the real systems `d = 1`, so nothing can ever be certified; the control therefore runs on a **synthetic** system (same `L2,L3,L4`, doubled `L0,L1`, hence `d = 2` by construction): an odd-`Ω`-class defect **must** be certified dead mod 2 **and** the independent `one_hop_system` solver must agree it is unsolvable mod 2, while the even-class defect must **not** be certified and **is** one-hop solvable mod 2 | fires / silent / agrees, 15/15 |
| C8 `d \| m` on every real defect | the reason no real chain is certified is arithmetic, not a silent failure | any `d ∤ m` ⇒ exit 2 | passes, 15/15 |
| C9 explicit lift (`--mode lift`) | the theorem's conclusion, constructively | `D + Σ L_i x_i ≠ 0` under the unmodified `apply_operator` ⇒ control fails | 27/27 verified; corrupting `L4` leaves 34 residual terms |

C5 is the load-bearing one: the earlier "mutation" control it replaced was inert by
construction and let a base-coset defect through. C7 is the other: a detector that can
never fire is not evidence, and since `d = 1` everywhere the firing has to be
demonstrated on a system built to have `d = 2`.

Reproduce (each command is its own guarded run):

```bash
python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- python3 \
  fable/proofs/checkers/g_stratum_death.py --mode gamma \
  --json fable/proofs/checkers/out/w2g_gamma.json

python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- python3 \
  fable/proofs/checkers/g_stratum_death.py --mode omega --k 0 \
  --json fable/proofs/checkers/out/w2g_omega_all.json

python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- python3 \
  fable/proofs/checkers/g_stratum_death.py --mode omega --stratum-only --k 1 \
  --json fable/proofs/checkers/out/w2g_omega_stratum.json

python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- python3 \
  fable/proofs/checkers/g_stratum_death.py --mode period --k 2 \
  --json fable/proofs/checkers/out/w2g_period_all.json

python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- python3 \
  fable/proofs/checkers/g_stratum_death.py --mode period --stratum-only --k 3 \
  --json fable/proofs/checkers/out/w2g_period_stratum.json

python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- python3 \
  fable/proofs/checkers/g_stratum_death.py --mode probe --stratum-only \
  --json fable/proofs/checkers/out/w2g_probe.json

python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- python3 \
  fable/proofs/checkers/g_stratum_death.py --mode quotients --stratum-only \
  --index 3 --degree 4 \
  --json fable/proofs/checkers/out/w2g_quotients_s3.json

# explicit verified solutions, one chain per run (indices 3 / 7 / 8 = g = TcTTc / Tc / cTTc)
python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- python3 \
  fable/proofs/checkers/g_stratum_death.py --mode lift --stratum-only \
  --index 3 --k 1 --depth 6 --radius 10 \
  --json fable/proofs/checkers/out/w2g_lift_s3.json
```

Exit 0 = every control green (a negative verdict is a *result*). Exit 2 = control
failure, run void.

---

## 5. Scope and nonclaims

- **PROVED vs TESTED.** *Proved:* Lemmas 1, 2, 2′, 3 and the Theorem, and therefore
  `Σ L_i M = ker ε` for **all 44** finite-index chains (15 in the g-stratum), at every
  integer window on every axis — `d = 1` makes the defect class irrelevant, so no box
  is involved anywhere in that statement. *Witnessed:* 27 explicit integral solutions
  at windows W2f calls dead at all three primes. *Tested only:* nothing that the
  verdict rests on.
- **23 chains (7 in the stratum) are untouched.** `[Q:Γ] = ∞` there, `Ω` is infinite,
  and the finite `P`-computation does not apply. Nothing here says those are live *or*
  dead. All three `g = c` chains are in this set.
- **Layer-1 liveness is not liftability.** `D ∈ Σ L_i M` says the obstruction dies in
  `N/[N,N]`; it moves to layer 2. No statement about the full lift, the noncancellation
  tower, or the codex route.
- **W2f's numbers are not contradicted.** Its 6,156 window decisions are correct
  one-hop decisions. What this note refutes is the *reading* of them as a module
  obstruction on the chains it covers — and W2b's original nonclaim ("not live at
  tested windows is not death") reserved exactly this.
- **The routing in `--mode lift` is a heuristic, not part of the proof.** It succeeds
  on every window tried, but a failure there would be a search failure, not a
  mathematical one; the theorem does not depend on it. Conversely its *successes* are
  hard evidence, because each is checked by exact module arithmetic.
- No claim about the free-group depth-four class, the bridge, AK(3), stable AC, or AC.

---

## 6. Why W2f §8's proposal could not have worked

§8 asked for a **finite non-abelian quotient** `Q → G` with `c` of order 2, and a
`PSU(2)`-style collapse of `L3, L4`. A pushforward `M → Z[G/⟨c̄⟩]` is a legitimate
necessary condition, but:

- the functional it can carry must be `Γ`-invariant (Lemma 1), i.e. constant on the
  `π(Γ)`-orbits of `G/⟨c̄⟩`;
- `w = g t g⁻¹` is a conjugate of `t`, so `π(Γ) ⊇ ⟨π(t)^{π(g)}⟩` — in a quotient
  generated by `c̄, t̄`, `π(Γ)` is rarely small, and orbit counts collapse;
- `--mode quotients` executes the proposal: **all** `(involution, element)` pairs in
  `S₄` — 221 quotients, `|G| ≤ 24`, of which **24** have ≥ 2 `Γ`-orbits on `G/⟨c̄⟩`
  (so the search is not vacuous). Over `p = 2, 3, 5` the **maximum joint left-null
  dimension of the five operators is 1** — the augmentation, which kills every
  augmentation-zero defect. **0 death certificates.**

The obstruction that *could* have existed lives in `Z[Γ \ Q / ⟨c⟩]`, a **double-coset**
module of a finite-index subgroup, and its content is an integer `d` (a torsion index),
not a representation. That is the shape §8's representation ansatz could not reach —
and on this family `d` is 1, so even that obstruction group is trivial.

---

## 7. The single most decisive next question

> **Is the one-hop truncation a usable liveness proxy at all?**

If not — and §3 says it is not on 15 stratum chains, with 27 explicit
counter-witnesses — then W2b's six live chains, W2e's 161 "counterexamples" and W2f's
five strata are all statements about the truncation, and the correct layer-1 index is
the pair `([Q : Γ], d)`, computable in milliseconds per chain and *already*
window-independent. Concretely, in order:

1. **Extend the theorem to `[Q:Γ] = ∞`** (23 chains, 7 in the stratum). `Ω` is
   infinite but the Schreier graph of `Γ` is a finite core with trees; the `L0/L1`
   rows for `v` far out in a tree are computable, and showing they generate
   `Z[Ω]_0` would close the family. All three `g = c` chains sit here.
2. **Recompute the whole W2b/W2e/W2f corpus with `d`** instead of one-hop
   solvability, and see whether any chain at any cap has `d ∤ m`. That is the honest
   layer-1 census, and it is cheap.
3. **Go to layer 2.** If layer 1 never obstructs, the period-two baseline question is
   entirely a `[N,N]` question — where the codex noncancellation tower already is —
   and W2's scope gap has to be restated at that layer.

---

## Summary of status

| claim | status |
|---|---|
| `L2 = 1−X`, `X = U⁻¹R`, `L4 = w−1`, `L3+L4 = U⁻¹−1`, `ε(L_i)=0` | **machine-verified**, every window touched |
| `L2M+L3M+L4M = I_Γ M` and `M/I_Γ M = Z[Ω]` (telescoping) | **proved**; its move calculus is what builds the §3.3 solutions |
| the `Ω`-images of the `L2, L3, L4` columns vanish identically | **machine-verified** (C5), with a corruption control that fires (C6) |
| the `Ω`-row set is computed exactly by a finite loop over `P` | **proved**; controlled against direct evaluation (0 missing rows; 15/15 agreement in the §2.2 diagnostic) |
| `Σ L_i M = π⁻¹(dZ(1,−1))`; solvable over `Z` iff `d \| m`; mod `p` iff `p\|d ⇒ p\|m` | **proved** |
| `[Q:Γ] = 4`, `\|Ω\| = 2`, `\|P\| = 12` for 44 of 67 census chains; `∞` for 23 | **verified** |
| `ζ2, ζ3` act trivially on `Γ\Q` ⇒ `d` constant over all `(k2,k3) ∈ Z²` | **verified**, 44/44 |
| `d = 1` for **all 44** finite-index chains (15 of the 22 g-stratum) ⇒ `Σ L_i M = ker ε` ⇒ **every window layer-1 solvable over Z** | **PROVED** |
| explicit integral `x` with `D + Σ L_i x_i = 0` at windows W2f calls dead mod 2,3,5 | **VERIFIED**, 27/27 windows, 3 chains, all three finite-index `g` values |
| a window-independent death certificate for the g-stratum | **does not exist** on the 15 finite-index chains; **open** on the other 7 |
| W2f's `S2` zero-solvable windows are one-hop truncation artifacts | **PROVED** on 15 of the 22 chains |
| the detector can produce a death certificate when one exists | **verified** on a synthetic `d = 2` system, cross-confirmed by the one-hop solver, 15/15 |
| a base-coset defect in this checker's Stallings graph, found by control C5 | **fixed**; effect on results recorded in §2.2 |
| anything about lifting, the bridge, AK(3), stable AC, or AC | **no claim** |
