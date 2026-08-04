# S15 — Why the thickenability route is one-sided, and what "a simple general way" would cost

Branch `claude/stable-ac-conjecture-stabilization-rwo9as`. **This branch must be merged into
`fable/proof` by the user** — a cloud session can only push to its own `claude/*` branch, so
nothing here reaches `fable/proof` on its own. No PR opened (`FRAMING` trap 10).

STATUS: **theory note, written after the session's searches, to say precisely what those
searches could and could not have established.** Everything below is either proved here,
computed here, or explicitly marked as resting on a source this clone does not contain.
Nothing here is a proof of the AC or stable AC conjecture.

This note exists because the session's headline numbers are *nulls* (0/45,111; 0/8 at every
gateway) and a null on this route is worth much less than it looks. §4 is the reason.

---

## 0. Notation

* `P = ⟨x₁,…,x_n | r₁,…,r_n⟩` — a **balanced** presentation; `K_P` its presentation
  2-complex (one vertex, `n` 1-cells, `n` 2-cells).
* `γ_N(P)` — the Neuwirth defect halved, `minimum_defect // 2` in this repo's tooling;
  `γ_N(P) = 0` ⟺ the repo verdict `SPHERICAL` ⟺ `P` is orientably PL **thickenable**.
* `P ~_st Q` — `P` and `Q` are **stably AC-equivalent**: related by AC1–AC3 together with
  stabilization/destabilization AC4/AC5.
* `T_n = ⟨x₁,…,x_n | x₁,…,x_n⟩` — the trivial (standard) presentation of rank `n`.
* **Stably AC-trivial**: `P ~_st T_n` for some `n`. **AC-trivial** (= AC-trivializable):
  `P` reaches `T_n` at its own rank, using AC1–AC3 only.

---

## 1. Lemma S15.1 — the standard presentation is thickenable at every rank

**Lemma.** `γ_N(T_n) = 0` for every `n ≥ 1`.

*Proof.* In `K_{T_n}` the relator `x_i` has length 1, so its 2-cell is attached along the
single loop `x_i`; loop-plus-2-cell is a cone on a circle, i.e. a disc. Hence `K_{T_n}` is a
wedge of `n` discs at the common vertex. Embed it in `ℝ³` by placing `n` discs meeting
pairwise only at that point; a regular neighbourhood is a 3-ball, so the complex is
orientably PL thickenable and the Neuwirth defect is 0. ∎

*Machine check (this session, this clone).* The repo's own decider
(`experiments/stable_ac/fable/s12_hunt.decide`, factorial census, `census_cap = 200000`)
returns `SPHERICAL`, `defect 0` for `T_n`, `n = 2,3,4,5,6`. This is a check of the tooling
against the lemma, not the lemma's proof.

---

## 2. Lemma S15.2 — every balanced presentation of the trivial group is contractible,
## so no homotopy invariant can separate AK(3) from `T_2`

**Lemma.** If `P` is balanced and presents the trivial group then `K_P` is contractible.

*Proof.* `χ(K_P) = 1 − n + n = 1`. `π₁(K_P) = 1` by hypothesis, so `H₁ = 0`. `K_P` is
2-dimensional, so `H₂ = ker ∂₂ ≤ C₂ ≅ ℤⁿ` is free abelian, and `χ = 1 − 0 + rk H₂ = 1`
forces `rk H₂ = 0`, hence `H₂ = 0`. All reduced homology vanishes and `K_P` is simply
connected, so by Hurewicz every `π_i` vanishes; `K_P` is a CW complex, so Whitehead upgrades
weak contractibility to contractibility. ∎

This is not new — it is `R10_ZEEMAN_COLLAPSE.md` L1, machine-checked there for AK(3), and it
is the classical reason the AK complexes are the standard test cases for the Zeeman
conjecture. It is restated here for the corollary, which is the point:

**Corollary S15.2a.** No invariant of the homotopy type of `K_P` can be nonzero on AK(3)
and zero on `T_2`: both complexes are contractible. Any obstruction to `γ_N = 0` must be a
combinatorial invariant of the **spine** — of the link graph and its rotation systems — and
cannot factor through `|K_P|`.

Note how sharply S3 illustrates this. A chord refinement is a *CW subdivision*:
`|K_{P′}| ≅ |K_P|`, homeomorphic, and the entire defect histogram is preserved by a
dart-level bijection. So a move that changes nothing topologically also changes `γ_N`
nothing. `γ_N` sees only combinatorics — and combinatorics is exactly what stabilization is
free to rewrite.

---

## 3. Proposition S15.3 — `γ_N` is **not** a stable-AC invariant, which kills the cleanest
## disproof idea on this line

Define the class minimum

    Γ(P) := min { γ_N(Q) : Q ~_st P }.

`Γ` is a stable-AC invariant **by construction**. `γ_N` itself is not:

**Witness (computed and chain-verified this session, `S4B_CUBIC_SEARCH.md`).**
`γ_N(AK(3)) = 2` at rank 2. The rank-13 cubic form
`C1 = ('kAe','Xgb','aXH','bxH','cYY','ydJ','eid','IfC','gKF','hAe','igb','jfC','kdJ')`
has `γ_N(C1) = 1` (census 8,192, `minimum_defect` 2), presents the trivial group
(Todd–Coxeter index 1, 481 cosets), and lies in AK(3)'s stable class — re-verified with
independent code by un-SPLITting four times to the rank-9 root and un-merging seven times to
`('XyxyXY','xxYYYYx')`, cyclically equal to AK(3). So `AK(3) ~_st C1` with
`γ_N = 2` and `γ_N = 1` respectively.

**Why this matters as a *negative* result.** The cleanest conceivable disproof of the stable
AC conjecture on this line would run: *`γ_N` is a stable-AC invariant; `γ_N(T_n) = 0`
(S15.1) but `γ_N(AK(3)) = 2`; therefore `AK(3) ≁_st T_n` and the conjecture is false.* That
argument is dead, by explicit witness, and it is dead for a structural reason —
Corollary S15.2a says the invariant would have to be combinatorial, and stabilization edits
combinatorics at will. Recording this so no future session spends a day rediscovering it.

**Current bracket.** `0 ≤ Γ(AK(3)) ≤ 1`. The upper bound `1` was already available at
rank 2 and length 14 (`gateway_scan.json`); the rank-13 cubic form ties it and does not beat
it. **High rank did not improve the bracket.**

---

## 4. Proposition S15.4 — the route is one-sided, so this session's nulls close nothing

The transfer theorem this whole route rides on is Lackenby's Theorem 1.3 — *thickenable +
balanced + trivial group ⇒ AC-trivializable, without stabilization*. **Sourcing, stated
plainly:** `literature/` is gitignored and this clone contains only
`literature/fake_surfaces/` (checked by `ls` while writing this sentence — no Lackenby
paper). Per `S2_LITERATURE_HIGH_RANK.md` the abstract is verified from source and the
statement of Thm 1.3 is **source-relayed, secondary-only**, agreed by two mutually
independent channels; whether it is rank-restricted is *high confidence, not source
verified*. Everything below that depends on Thm 1.3 is flagged; the rest does not.

Theorem 1.3 is an **implication, not an equivalence**. Consequently:

* **Positive side (needs an UPPER bound on `Γ`).** Any tool that *exhibits* a member `Q`
  of `P`'s stable class with `γ_N(Q) = 0` settles the case: `Q` is balanced, trivial, and
  thickenable, so [Thm 1.3] `Q` is AC-trivializable, and `P ~_st Q` gives `P` **stably
  AC-trivial**. Every search instrument in this repo lives on this side. A hit is a
  complete, checkable certificate.
* **Negative side (needs a LOWER bound on `Γ`).** A search that *fails* to exhibit one
  bounds nothing. Non-thickenability is not an obstruction to AC-triviality in either
  direction — Thm 1.3 has no converse here. A null is a joint statement about the region
  searched and the detector's measured sensitivity, and about nothing else.

**Therefore, said in the direction the data actually supports:** the session's
`0 / 45,111` over the largest exhaustively decided region of AK(3)'s stable class, and
`0 / 8` at every gateway, are statements that *the certificate is not in the searched
region*. They are not evidence that `Γ(AK(3)) ≥ 1`, and they must never be summarised as
"AK(3) resists". The only quantity they move is the upper bound, and they did not move it.

This is the repo's recurring bound-direction trap
(`experiments/lessons/parallel-runs-and-bound-direction.md`) applied to the route as a
whole rather than to one sentence, and it is why the calibration work matters more than the
nulls: an uncalibrated null on a one-sided route carries **zero** information. The
high-budget gateway sweep makes the point concrete — at 8× nodes the control detection ran
`12/12` at length 15, `8/12` at length 16 and `0/12` at length 18, so the length-18 target
null is not weak evidence, it is *no* evidence.

---

## 5. Theorem S15.5 — "a simple general way" is exactly the conjecture

**(a) Unconditional direction.** If `P` is stably AC-trivial then its stable class contains
a thickenable member. *Proof:* `P ~_st T_n` for some `n`, and `γ_N(T_n) = 0` by S15.1. ∎

**(b) Conditional direction [rests on Lackenby Thm 1.3, source-relayed — see §4].** If some
`Q ~_st P` has `γ_N(Q) = 0`, then `P` is stably AC-trivial. *Proof:* `Q` is balanced
(stabilization preserves balance) and presents the trivial group (stable AC moves preserve
the group), so Thm 1.3 makes `Q` AC-trivializable; compose with `P ~_st Q`. ∎

**Corollary S15.5c [same dependency].** The stable AC conjecture is **equivalent** to:

> every balanced presentation of the trivial group has a Neuwirth-thickenable member
> (`γ_N = 0`) somewhere in its stable AC class,

i.e. to `Γ(P) = 0` for every such `P`.

**What this says about the session brief.** The brief asked whether extra stabilization
gives "a simple general way of solving any presentation with this technique". Corollary
S15.5c answers it in the only way that is honest: *a general construction that thickens an
arbitrary balanced trivial-group presentation after enough stabilizations would **be** a
proof of the stable AC conjecture* — not a step toward one, the whole thing. So the absence
of such a construction after seven hours is not a surprise and is not a defect of the
approach; and, by FRAMING's own rule, any future candidate must be checked for a hidden
reduction to the open problem before it is believed.

The corollary also relocates the difficulty usefully. It is **not** that thickenable
presentations are rare — the matched AC-trivial control produced 759 of them in 50,320
states at rank 12–13. It is that no *construction* is known, only search; and search is on
the upper-bound side, where silence is cheap.

---

## 6. What would a lower-bound tool have to be?

For the disproof side one needs a computable `Φ` with `Φ(AK(3)) > 0`, `Φ(T_n) = 0`, and
`Φ` non-increasing under **every** stable AC move. The candidates and why each is already
dead:

| candidate | why it fails |
|---|---|
| homology, `χ`, `π₂`, Whitehead torsion, any homotopy-type invariant | constant on the class: every balanced trivial presentation is contractible (S15.2) |
| `γ_N` itself | not invariant — `AK(3) ~_st C1` with `γ_N` 2 vs 1 (S15.3) |
| anything a CW subdivision preserves but a length-3 SPLIT can lower | S3 gives the first, the `AK(3) → C1` chain gives the second |
| "splitting never decreases `γ_N`" (S8) as a monotonicity engine | S8 is about the length-2 bigon `uG`; A6's length-3 definition `tuv` demonstrably lowered `γ_N`. The two moves must not be conflated, and S8 is under audit |

No monotone quantity is currently known on this line. That is the honest state of the
disproof side, and it is a *negative result about the route*, filed so the next session does
not mistake the abundance of search instruments for the existence of an obstruction.

---

## 7. Status of every claim in this file

| # | claim | status |
|---|---|---|
| S15.1 | `γ_N(T_n) = 0` for all `n` | **proved** here; machine-checked `n ≤ 6` in this clone |
| S15.2 | balanced + trivial ⇒ `K_P` contractible | **proved** here; not new (`R10` L1) |
| S15.2a | no homotopy invariant separates AK(3) from `T_2` | **proved** (immediate from S15.2) |
| S15.3 | `γ_N` is not a stable-AC invariant | **proved by explicit witness**; the witness chain was re-verified with independent code (`S4B`) |
| S15.4 | the route is one-sided; nulls bound nothing below | **proved** given Thm 1.3's *form* (an implication); does not depend on Thm 1.3 being true |
| S15.5a | stably AC-trivial ⇒ class meets `{γ_N = 0}` | **proved**, unconditional |
| S15.5b/c | converse, and the equivalence | **conditional on Lackenby Thm 1.3**, which is source-relayed only in this clone (§4) |
| §6 table | no monotone lower-bound quantity is known | **survey**, not a proof of nonexistence |

Nothing in this file is a proof or disproof of the AC or stable AC conjecture. Its content
is: one reformulation (S15.5c), one closed disproof idea (S15.3), and one correction to how
the session's nulls may be read (S15.4).
