# W5: the MMS02 bridge has no cheap separating invariant — it *is* one-stabilization AK(3)

Date: 2026-08-28 · Lane: `fable/proofs` · Status: **result + method-closure**

Checkers (all guarded, all green as recorded here):

| checker | what it certifies |
|---|---|
| `checkers/bridge_reduction.py` | Theorem W5.1's four lemmas, literal move by move, with 4 adversarial controls |
| `checkers/bridge_invariant_probe.py` | I1 abelianization, I2 Fox/Alexander over `Z[F3^ab]` (+ certified-positive control) |
| `checkers/nilpotent_bridge_chain.py` | I3 free nilpotent quotients of class 2, 3 (`--degree 2|3|4`) |
| `checkers/w5_words.py`, `checkers/w5_linalg.py` | shared word / integer-linear-algebra support |
| `.scratch/mms02_wirtinger_repair_attack_checker.py` (existing, re-run here) | `Q ~AC AK(3)` by the 53 Appendix-F moves, rank two, no stabilization |

Outputs: `checkers/out/w5_bridge_reduction.json`, `w5_invariant_probe.json`,
`w5_nilpotent_class{2,3,4}.json`.

## The object

`F = F(x,y,z)`, uppercase = inverse. Rank-3 AC moves, no stabilization:
AC1 `r_i -> r_i^-1`, AC2 `r_i -> r_i · w r_j^{±1} w^-1` (`j ≠ i`), AC3
`r_i -> w r_i w^-1`. *AC-trivial* = AC-equivalent to `(x,y,z)`.

```text
A    = xzYXyxZXYxyZ
B    = XyxZXYXyxzXYxy
Txy  = (A, B, zYX)   certified AC-trivial (134 primitive moves)
Tpub = (A, B, Xyz)   the open bridge endpoint
```

---

## 1. Theorem W5.1 (the bridge, restated exactly)

> **The following are equivalent.**
> 1. **(bridge)** `(A,B,zYX) ~AC (A,B,Xyz)`.
> 2. `Tpub = (A,B,Xyz)` is AC-trivial.
> 3. `Q = (xYxYXyyXYxyXy, XyyXYXyxYYxy)` is **AC-trivial after exactly one
>    stabilization**, i.e. `(Q1, Q2, z)` is AC-trivial in `F(x,y,z)`.
> 4. **AK(3)** `= (xxxYYYY, xyxYXY)` is AC-trivial after exactly one
>    stabilization, i.e. `(xxxYYYY, xyxYXY, z)` is AC-trivial in `F(x,y,z)`.

Four lemmas, each machine-checked.

**Lemma 1 (Aut-invariance).** For `φ ∈ Aut(F3)` and any triple `T`: `T` is
AC-trivial iff `φ(T)` is. *Proof.* AC moves commute with `φ`
(`φ(r_i w r_j^e w^-1) = φ(r_i) φ(w) φ(r_j)^e φ(w)^-1`), so a trivializing path
for `T` maps to a path from `φ(T)` to the basis tuple `φ(x,y,z)`; by Nielsen's
theorem a basis tuple is carried to `(x,y,z)` by elementary Nielsen
transformations of the tuple, and each of those is an AC move: `r_i -> r_i
r_j^{±1}` is AC2 with `w = 1`, `r_i -> r_i^-1` is AC1, and a transposition is
the 4-move word `(u,v,w) -> (u,vu,w) -> (v^-1,vu,w) -> (v^-1,u,w) -> (v,u,w)`
(verified on 200 random triples). Apply the same to `φ^-1` for the converse. ∎

**Lemma 2 (basis change).** `α: x,y,z -> x,y,Yxz` is an automorphism of `F3`
(inverse `z -> Xyz`) with `α(Xyz) = z`; `β: x,y,z -> x,y,zxy` is an
automorphism with `β(zYX) = z`. *Checked by composing both ways on generators.*

**Lemma 3 (z-elimination is a literal AC2 path).** If a triple has third entry
`z`, every `z`-letter can be deleted from the other rows by AC2 moves against
row 3: if `r = p·z^e·s` then `r·(s^-1 z^-e s) = p·s`, i.e. the move with
conjugator `w = s^-1`. Five such moves take `α(Tpub) = (αA, αB, z)` to
`(Q1, Q2, z)`, and five take `β(Txy)` to `(P1, P2, z)`; every move is verified
against its own recorded parameters, and corrupting the conjugator, the donor
exponent, or a passive row makes the verifier reject.

**Lemma 4 (identification of the endpoints).**
`(A,B)|_{z:=Yx} = Q` and `(A,B)|_{z:=xy} = P = (xyxYXXY, XyxYXXYXyxxyXYxy)`,
both matching the spellings recorded independently on 2026-07-29 in
`.scratch/mms02_u_xy_bridge.md`. And `Q ~AC AK(3)` in rank two with no
stabilization: the existing checker replays the 53 published Appendix-F
`h_i` moves (each an AC2 multiplication by the other relator or an AC3
conjugation by a generator) from `Q`, up to two inversions and one rotation,
onto `AK(3)`; re-run here, `all exact AC replays: OK`. Rank-2 moves embed in
rank 3 fixing the row `z`, so `(Q1,Q2,z) ~AC (AK3_1, AK3_2, z)`.

*Proof of the theorem.* (1)⟺(2) because `Txy` is certified AC-trivial, so the
bridge holds iff `Tpub` is AC-trivial. (2)⟺(3): by Lemma 1, `Tpub` is
AC-trivial iff `α(Tpub) = (αA, αB, z)` is; by Lemma 3 that triple is joined by
literal AC2 moves to `(Q1,Q2,z)`. (3)⟺(4): Lemma 4. ∎

### Why this is new

`.scratch/mms02_u_xy_bridge.md` (2026-07-29) recorded **one** direction,
unquantified: "such a sequence, combined with the existing published
reduction to AK(3), would prove stable AC-triviality of AK(3)". W5.1 adds the
**converse** and the **quantifier**: the bridge is not a lemma on the way to
AK(3) — it is logically identical to AK(3)-plus-one-stabilization. W4's
observation that the `Tpub` greedy floor Tietze-collapses onto AK(3)'s own
Aut-orbit is the same phenomenon seen from inside a search; here it is an
equivalence, with a certificate, independent of any search.

## 2. Corollary (hardness transfer) — the invariant hunt is not a shortcut

> Let `I` be any function on rank-3 triples that is constant on AC-orbits. If
> `I(Txy) ≠ I(Tpub)`, then **AK(3) is not AC-trivializable after one
> stabilization** — a partial negative resolution of the open stable-AC
> question for AK(3). Conversely, if AK(3) *is* one-stabilization
> trivializable, no such `I` exists.

So the regime W1 left alive (non-base-killing quotients, infinite images) is
alive but **not smaller than the open problem**. This is the honest reading of
every null below: they are not evidence about the bridge, they are the
expected behaviour of cheap invariants on a hard question. It also means a
*successful* separation would be a major result, not a lemma — and should be
treated with the corresponding suspicion.

## 3. The invariant battery

Each probe below carries a control that can fail. Two kinds are used: an
**adversarial control** (a pair that MUST be separated — `(x,y,z)` vs
`(x,y,zz)`, `|det| = 1` vs `2`) and a **certified-positive control** (`Txy` is
AC-trivial, so any true AC-invariant must give it the value of `(x,y,z)`; and
its image must be connected to the standard image in *every* quotient).

### I1 — abelianization: BLIND (and it was never in doubt)

```text
Ab(Txy)  = [[1,0,-1],[-1,1,0],[-1,-1,1]]   det -1
Ab(Tpub) = [[1,0,-1],[-1,1,0],[-1, 1,1]]   det +1
```
Both unimodular; the checker produces an explicit chain of **11** elementary
operations (adds and negations only — literally AC2 with trivial conjugator and
AC1) carrying `Ab(Tpub)` to `Ab(Txy)`, and verifies it by matrix
multiplication. Control: `(x,y,zz)` has `|det| = 2` and the reducer refuses.

### I2 — Fox / Alexander over `R = Z[F3^ab] = Z[t1^±,t2^±,t3^±]`: BLIND, with a proof

**(a)** The Fox implementation is pinned by the fundamental identity
`Σ_k ∂w/∂x_k ·(t_k − 1) = t^{ab(w)} − 1` on 37 words.

**(b) Transformation law (verified on 40 random AC2 moves).** For
`r_i' = r_i · w r_j^e w^-1`,

```text
row_i(J') = row_i(J)  +  t^{a_i}(1 − t^{e·a_j})·d(w)  +  u · row_j(J),
```
with `u` a unit of `R` (`t^{a_i+a_w}` for `e = +1`, `−t^{a_i+a_w−a_j}` for
`e = −1`) and `d(w)` the Fox gradient of the conjugator. The middle term is
**junk**: it is not a row operation over `R`, so the `E_n(R)`/`GE_n(R)`
row-equivalence class of the Jacobian is *not* an AC invariant. The checker
found 64 nonzero junk entries on the bridge triples (witness: `Tpub`,
`i=1, j=2, e=−1, w=zXy`, junk entry `−t1^-2 t2 t3 + t1^-1`).

**(c) Blindness theorem.** Every junk entry lies in the augmentation ideal
`I = (t1−1, t2−1, t3−1)` (checked: augmentation 0 for all of them), and the
ideal generated by the achievable junk *is* `I`: the junk scalars include
`1 − t^{a}` for `a ∈ {a_A, a_B, a_K}`, which is a **Z-basis of Z³** (checked:
`|det| = 1`), so the monomial change of coordinates `s_i = t^{a_i}` identifies
`(1−s_1, 1−s_2, 1−s_3)` with `I`. Hence the largest quotient of `R` on which
the Jacobian's row class survives the AC action is `R/I = Z`, where the
Jacobian is exactly the abelianized matrix — i.e. I1, blind. **The whole
Alexander/Fox route over the free abelianization collapses to abelianization.**
(Over `Z[G]` for the presented group `G` it collapses even faster: both
presentations present the trivial group, so `Z[G] = Z`.)

**(d) The tempting invariant "det J up to units" is refuted by its own
positive control.**

```text
det J(std)  = 1
det J(Txy)  = 12 terms, augmentation −1, NOT a unit
det J(Tpub) = 14 terms, augmentation +1, NOT a unit; not a unit multiple of det J(Txy)
```
`Txy` is certified AC-trivial, so a genuine AC-invariant "det J mod units"
would have to give `Txy` the value of `(x,y,z)`, namely a unit. It does not.
The candidate is therefore **not an invariant**, and the fact that the two
bridge determinants differ carries **no** AC information. (This is exactly the
failure mode the junk lemma predicts.)

**(e) The classical cyclic Alexander datum is blind.** Under
`t1 = t2 = t3 = t`,

```text
det J(Txy)|diag  = −t^-4 · Δ(t),      det J(Tpub)|diag = t^-3 · Δ(t),
Δ(t) = t^4 − 3t^3 + 5t^2 − 3t + 1
```
— the two agree up to the unit `−t^-7`, and `Δ` is exactly the polynomial
recorded in `.scratch/mms02_bridge_alexander_filter.md` as generating
`G_-'/G_-''`. So the 2026-07-29 Alexander module, which *did* refute two
fixed-base symmetry candidates, takes the same value on both bridge endpoints.
It is a fixed-base instrument (it lives on `⟨x,y,z | A,B⟩`, a group that a
general AC path destroys), and on the bridge itself it is blind.

### I3 — infinite, non-base-killing quotients: the free nilpotent tower

This is the regime W1's vacuity theorem leaves alive (`φ(A), φ(B) ≠ 1`) and
BLM 2005 does not reach (`G` infinite). Model: the Magnus truncation
`F3 -> U_d ⊂ Z⟨⟨X1,X2,X3⟩⟩/(deg > d)`, `x_i ↦ 1 + X_i`, kernel
`γ_{d+1}(F3)`; `U_d` is the free class-`d` nilpotent group on 3 generators,
infinite and (for `d ≥ 2`) nonabelian. Checked each run: `φ(A) ≠ 1`,
`φ(B) ≠ 1`, `x` of infinite order, `[x,y] ≠ 1`.

The orbit is infinite, so nothing is searched (repo cap respected: **zero**
popped states anywhere in this note). Instead the checker **constructs** a
finite chain of projected AC moves and verifies each move against its own
parameters: phase A matches the abelianized matrices by elementary row
operations; then for each layer `L = 2..d` the residuals `r_i^-1 v_i` lie in
`γ_L`, hence are central and additive mod `γ_{L+1}`, and a pool of composite
gadgets — `local: r_i -> r_i[w, r_j]` (two AC2 moves, optionally conjugated by
a donor row operation) and `transfer: r_j -> r_j r_i^e ; r_i -> r_i[w,r_j] ;
r_j -> r_j r_i^-e`, which moves a `γ_L` element between two rows — is evaluated
numerically and one exact integer solve over all three rows at once picks the
multiplicities.

| class `d` | bridge `Tpub → Txy` | positive control `Txy → std` | verdict |
|---|---|---|---|
| 2 | **connected, 47 moves** | connected, 40 moves | quotient **BLIND** |
| 3 | **connected, 991 moves** | connected, 166 moves | quotient **BLIND** |
| 4 | integer solve fails at layer 4 | **fails too** (540 columns, dim 243) | **verdict withheld** |

At class 4 the positive control fails, so the method — not the mathematics — is
what ran out; the checker refuses to print a bridge verdict there. (The
class-3 run needed the `transfer` gadget: row-local corrections span only rank
6 of the 8-dimensional `L_3`, missing exactly the bracket directions `[·, a_i]`
that no gadget with `r_i` as target can reach. The first class-3 attempt, with
row-local gadgets only, failed *and its positive control failed with it* —
which is how the weakness was caught rather than shipped as a null.)

Adversarial control at every class: `(x,y,zz) → (x,y,z)` is refused
(`|det| = 2`), and corrupted move parameters are rejected by the verifier.

## 4. Status of each direction

| direction | verdict |
|---|---|
| abelianization | **blind**, chain exhibited |
| all finite quotients | **blind** (BLM 2005 Thm 1.1; W1) |
| any hom killing `A, B` | **blind** (W1 vacuity theorem) |
| Fox/Alexander over `Z[G]`, `G` presented | **blind** (`G = 1` on both sides) |
| Fox/Alexander over `Z[F3^ab]`, row class | **blind by theorem** (junk ideal = augmentation ideal, §I2c) |
| `det J` up to units | **not an invariant** — refuted by the certified-positive control |
| cyclic Alexander `Δ` of the deficiency-one base | **blind** (same `Δ` up to a unit); fixed-base instrument |
| free nilpotent class 2, class 3 | **blind**, explicit verified chains |
| free nilpotent class ≥ 4 | **open**, method-limited (positive control fails) |
| any invariant whatsoever | separating one ⟹ AK(3) is not one-stabilization trivializable (§2) |

Nothing separates. Nothing was expected to, once §2 was in hand.

## 5. Most promising continuation

Stop hunting bridge invariants; by §2 that hunt *is* the open problem. Point
the lane's own W3 lever at the object W5.1 identifies instead:

> **Test Lackenby-thickenability of the once-stabilized AK(3) presentation**
> `(xxxYYYY, xyxYXY, z)` — equivalently of `(Q1,Q2,z)`, or of `Tpub`, or of any
> rank-3 state AC-reachable from them (the repo already has a basin of such
> states from the `Tpub` greedy).

Lackenby (arXiv:2606.06122) gives: thickenable balanced presentation of the
trivial group ⇒ satisfies the **unstable** AC conjecture. A thickenable
presentation anywhere in the AC-class of `Tpub` would therefore prove
statement (2) of W5.1, hence the bridge, hence one-stabilization AC-triviality
of AK(3) — a decisive positive endpoint. The repo's route-3 thickenability
work has been aimed at rank-2 AK(3); W5.1 says the rank-3 stabilized
presentation is the object the bridge is actually about, and it is a *different*
(larger, more flexible) target than the rank-2 one. This should be gated
through ac-advisor before implementation, per the lane's rules.

Secondary: extend I3 to class ≥ 4 by strengthening the gadget pool (the
positive control tells you when it is strong enough). This can only ever
produce more blindness certificates, so it ranks below the thickenability
route.

## 6. Scope and nonclaims

- **No AK(3), stable AC, AC, or bridge claim.** W5.1 is an equivalence between
  two open statements; it decides neither.
- The equivalence depends on two existing repo certificates: the 134-move
  AC-trivialization of `Txy` and the 53-move Appendix-F replay `Q → AK(3)`
  (both re-run or re-derived here). It does **not** depend on any search, any
  budget, or any greedy floor.
- The nilpotent results are statements about the *images* of the two triples in
  `U_2` and `U_3` only. Blindness of a quotient says nothing about `F3`.
- All computation was constructive (finite verified chains and exact integer
  solves). No breadth-first search was run; no state was popped.
- `Δ(t) = t^4 − 3t^3 + 5t^2 − 3t + 1` is reproduced here as the diagonal
  specialization of `det J`; the identification with `G_-'/G_-''` is quoted
  from the 2026-07-29 note, not re-derived.

## 7. Lessons (added to `LESSONS.md`)

1. When an invariant hunt is opened, first ask what a *success* would prove.
   Here a five-lemma reduction showed a separating invariant would refute a
   headline open problem — which reframes every null as expected, and every
   apparent positive as a red flag.
2. A constructive connectivity method needs its own positive control at every
   parameter value. The class-3 and class-4 nilpotent runs both failed; the
   control distinguished "the quotient might separate" (never observed) from
   "my gadget pool is too small" (both times).
