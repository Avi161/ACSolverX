# S4 — The Cubic Normal Form problem (task A6)

Date 2026-08-04. Branch `claude/stable-ac-conjecture-stabilization-rwo9as` (merge into
`fable/proof` by the user). Standing frame: `FRAMING.md`. Direct successor of
`S3_SUBDIVISION_INVARIANCE.md` §4, which posed the question this file attacks.

Everything below is about **balanced presentations of the trivial group**; every claim
names which of *trivial group* / *AC-trivial* / *stably AC-trivial* it addresses.

---

## 0. Answers, up front

> **Q.** Can every balanced presentation `P` of the trivial group be transformed, by stable
> AC moves, into **cubic triangular form** — every relator of length exactly 3, every
> generator occurring exactly 3 times?

**Answer: OPEN, and the question as posed splits into two genuinely different questions
that must never again be conflated.** The split is forced by a theorem proved here.

| | statement | status |
|---|---|---|
| **Q-deg** | reach a cubic triangular form, *degenerate relators allowed* (a length-3 relator that is not cyclically reduced) | OPEN; but such a form is worth **much less** than it looks — Thm S4.3 |
| **Q-red** | reach a cubic triangular form with **all relators cyclically reduced** | OPEN; **provably impossible below rank 4** (Thm S4.1 + Prop S4.2), possible in principle from rank 4 on |

Concretely delivered here:

1. **Thm S4.1 + Prop S4.2 (an obstruction, proved).** A cubic triangular presentation with
   all relators cyclically reduced has an abelianised matrix `M` whose entrywise absolute
   value is a nonnegative integer matrix with all row *and* column sums 3. For `N ≤ 3` no
   sign pattern of such a matrix has `|det| = 1`, so **there is no cyclically reduced cubic
   triangular presentation of the trivial group of rank 2 or 3.** In particular the
   motivating example `⟨x,y | xyX, yxY⟩` *cannot* be non-degenerate, and it is not: both its
   relators fail cyclic reduction.
2. **Thm S4.3 (degeneracy collapses).** A cubic triangular presentation of the trivial group
   containing a non-cyclically-reduced relator is AC-equivalent to a presentation of rank
   `N−1`; if *every* relator is degenerate it is AC-equivalent to the standard presentation.
   This is exactly the "secret trivialisation" the task warned about (FRAMING trap 4), and
   it is why Q-deg is the weak question.
3. **Existence settled by census.** Non-degenerate cubic triangular presentations of the
   trivial group **exist from rank 4**: there are exactly **43 008** of them at rank 4.
4. **The headline empirical number.** Of those 43 008 rank-4 non-degenerate cubic triangular
   presentations of the trivial group, **27 648 (64.29 %) are thickenable (γ_N = 0)** and
   15 360 (35.71 %) have γ_N = 2. No other defect value occurs. **A large fraction — this is
   the strongest available motivation for the cubic route**, and it is not vacuous: 36 % are
   *not* thickenable, so γ_N = 0 is a real test inside the cubic world, not automatic.
5. **A constructive calculus (proved legal) and where it stalls.** §5 gives `SPLIT`, a stable
   AC move that changes occurrence multiplicities while keeping every relator at length 3
   and preserving cyclic reducedness, together with its exact occurrence-vector bookkeeping.
   **There is no counting obstruction** — the bookkeeping is identically balanced. The
   sticking point is stated precisely in §5.4: the move set is *state-dependent*, so
   equalisation is a reachability problem in a growing labelled structure, not a solvable
   linear system.
6. **AK(3): no cubic form found; the null is calibrated.** Beam search over 48 different
   triangulations of AK(3) produced no cubic triangular member. On a *matched-difficulty*
   positive ladder (AC-trivial rank-2 presentations of total length 13, triangulated to rank
   9, equalisation cost 14 — the same numbers AK(3) has) the same search succeeds
   **4/12 = 33 %** of the time. So this null is worth exactly 48 correlated attempts at a
   33 % marginal rate: **suggestive, not evidence** (the 48 attempts are triangulations of
   the same two words and the search is deterministic given the triangulation). **No cubic
   form of AK(3) is reported.**

Route verdict: **NOT blocked, not delivered.** It does not reduce stable ACC to another open
problem (FRAMING §3), and it has a measured 64 % thickenability prior at rank 4. It is
delivered as a live route with a sharpened target (Q-red, rank ≥ 4) and a working move
calculus.

---

## 1. Definitions, made exact

`P = ⟨x_1..x_N | r_1..r_N⟩`, balanced. `m_i` = the number of occurrences of `x_i` in
`r_1 … r_N`, counting both signs.

* **triangular**: every `|r_j| = 3`.
* **cubic**: every `m_i = 3`.
* **cubic triangular form**: both. Then `Σ_i m_i = Σ_j |r_j| = 3N` automatically — the two
  conditions are *jointly* the statement that the link graph is 3-regular on `2N` germs
  (`deg(x_i^+) = deg(x_i^-) = m_i`; verified against `neuwirth_rank_n.build_link_n`, which
  reports `degrees = {g: 3}` exactly when `m_g = 3`).
* A length-3 relator is **degenerate** if it is not cyclically reduced. A freely reduced
  length-3 word that is not cyclically reduced is `a b a^{-1}` up to rotation, with
  `b ∉ {a, a^{-1}}`. A presentation is **non-degenerate cubic triangular** if it is cubic
  triangular and every relator is cyclically reduced.

Why the census is cheap here (S3 §4, re-confirmed): each germ has degree 3, so it admits
`(3−1)! = 2` cyclic orders and the compatible-rotation census has size `≤ 2^{2N}`; and the
simple support has `≤ 2N` vertices and `≤ 3N` edges with `3N ≤ 6N − 6` for `N ≥ 2`, so the
Euler sparsity non-planarity certificate can never fire. Measured census sizes: 4 at `N = 2`,
8 at `N = 3`, 16 at `N = 4` — i.e. `2^{2N}` is a wild over-estimate in practice.

---

## 2. Theorem S4.1 — sign rigidity, and the abelianised obstruction

> **Theorem S4.1 (sign rigidity).** In a cyclically reduced word of length 3, all
> occurrences of any one generator carry the same sign.

**Proof.** Let `w = w_1 w_2 w_3` be cyclically reduced. In a cyclic word of length 3 every
pair of positions is cyclically adjacent: `{1,2}`, `{2,3}` are adjacent in `w`, and `{3,1}`
is adjacent cyclically. If two positions held `x` and `x^{-1}` in some order, then `w`
would contain `x x^{-1}` or `x^{-1} x` as a subword (positions 1,2 or 2,3), contradicting
free reduction, or `w_3 = w_1^{-1}`, contradicting cyclic reduction. ∎

> **Corollary S4.1.1.** For a non-degenerate cubic triangular `P`, let `c_{ji}` = number of
> occurrences of `x_i` in `r_j` and let `M` be the abelianised relation matrix. Then
> `|M_{ji}| = c_{ji}`, and `C = (c_{ji})` is a nonnegative integer matrix with **every row
> sum and every column sum equal to 3** (rows: `|r_j| = 3`; columns: `m_i = 3`).

By Birkhoff–von Neumann `C` is a sum of three permutation matrices, i.e. `C` is the
biadjacency matrix of a 3-regular bipartite multigraph on `N + N` nodes. `M = S ∘ C` for
some sign matrix `S` on the support of `C`.

> **Proposition S4.2 (rank obstruction below 4).** There is **no** non-degenerate cubic
> triangular presentation of the trivial group of rank `N ≤ 3`.

**Proof.** `P` presents the trivial group ⇒ `H_1 = coker M = 0` ⇒ `|det M| = 1`. Negating a
row of `M` is AC1 (invert that relator) and negating a column is replacing a generator by its
inverse; both preserve the cubic triangular property and `|det|`. Hence signs may be gauge
fixed to `+1` on a spanning forest of the bipartite support graph of `C`, leaving
`|E| − (2N − c)` free signs. Exhausting all `C` and all gauge-fixed sign patterns:

| `N` | # of `C` (row/col sums 3) | sign patterns with `|det| = 1` |
|---|---|---|
| 2 | 4 | **0** |
| 3 | 55 | **0** |
| 4 | 2 008 | 936 |
| 5 | 153 040 | 174 240 |

`N = 2` is also immediate by hand: `C ∈ {3P, P_1+P_2}` gives `|det| ∈ {9, 3, 5}`. ∎
*(Scan: `det_obstruction.py`; independently corroborated by direct word enumeration — all 20
cubic triangular relator-tuples at `N = 2` and all 1 816 at `N = 3` have `|det| ≠ ±1`.)*

**Read the direction correctly** (lesson `parallel-runs-and-bound-direction.md`): Prop S4.2
is a *non-existence* statement below rank 4. It says nothing about ranks ≥ 4 — and the table
shows the abelianised obstruction **vanishes** there, which the census in §4 confirms with
explicit words.

---

## 3. Theorem S4.3 — what a degenerate triangle does (task item 3)

> **Theorem S4.3.** Let `P` be cubic triangular and present the trivial group.
> (a) If some relator `r_j` is degenerate, then `P` is AC-equivalent to a presentation of
> rank `N − 1` (using move (0), AC2, AC3 and one AC5).
> (b) If **every** relator is degenerate, `P` is AC-equivalent to the standard presentation
> `⟨x_1..x_N | x_1,…,x_N⟩`; in particular `P` is **AC-trivial**.

**Proof.** (a) Up to rotation `r_j = a b a^{-1}` with `b ∉ {a, a^{-1}}`; cyclic reduction
(move (0), equivalently AC3 by `a^{-1}`) replaces it by the single letter `b`. With a
length-1 relator `b` present, every occurrence of `b` in every other relator is deleted by
AC3+AC2 (multiply by the appropriate conjugate of `b^{∓1}`), after which `b` occurs in no
relator but its own and AC5 destabilises. (b) After cyclic reduction all `N` relators are
single letters `b_1,…,b_N`. The group is trivial, so `⟪b_1..b_N⟫ = F(x_1..x_N)`; `N` letters
normally generating a free group of rank `N` must be the `N` distinct generators up to sign,
so `P` is AC-equivalent (AC1 + relabelling) to the standard presentation. ∎

**Consequences, which reshape the route.**

* The motivating example `⟨x,y | xyX, yxY⟩` has **both** relators degenerate; by (b) it is
  AC-trivial, and indeed AC3 by `x^{-1}` turns `xyX` into `y`. It is a *correct* cubic
  triangular presentation of the trivial group and a *misleading* advertisement for the
  route.
* A degenerate cubic form is **not worthless**: `K_P` is still its own complex, `γ_N(P) = 0`
  is still a genuine (and cheap) test, and thickenable + trivial group ⇒ AC-trivialisable
  (Lackenby Thm 1.3, `[UNVERIFIED this session — LITERATURE_STATUS.md §1]`) ⇒ the source of
  the stable chain is stably AC-trivial. But by (a) a degenerate cubic form always carries a
  free rank drop, so it can never be the *terminal* normal form the route wanted.
* Therefore the target the route must aim at is **Q-red**, and by Prop S4.2 the answer to
  Q-red for `N ≤ 3` is NO. This is the "state what happens when a relator would become
  length < 3" requirement of the task, answered structurally rather than by input shape
  (FRAMING trap 4): the transform is excluded by **what it produces** — a relator that
  cyclically reduces below length 3 — not by how its input looked.

---

## 4. The census (task item 1) — existence and the thickenable fraction

Exhaustive enumeration of cubic triangular relator tuples (relators as cyclic words, ordered
tuples up to rotation), abelianised prefilter `|det| = 1`, triviality certified by HLT
Todd–Coxeter over the trivial subgroup (cap 20 000, no case undetermined), classes taken
modulo generator permutation, generator inversion, relator inversion and relator reordering,
exact `γ_N` from `gamma_N_factorial_n`.

### 4a. Non-degenerate (all relators cyclically reduced)

| `N` | triangle cyclic-words | cubic tuples | `\|det\| = 1` | trivial group | γ_N = 0 |
|---|---|---|---|---|---|
| 2 | 12 | 20 | **0** | **0** | — |
| 3 | 46 | 1 816 | **0** | **0** | — |
| 4 | 120 | 264 208 | 43 008 | **43 008 (all)** | **27 648 = 64.29 %** |

At `N = 4` the defect histogram over all 43 008 is exactly `{0: 27648, 2: 15360}`.
First example in the enumeration (lexicographic), hand-checked:

```
Q4 = ⟨a,b,c,d | a⁻¹a⁻¹b⁻¹ , a⁻¹b⁻¹c⁻¹ , b⁻¹c⁻¹d⁻¹ , c⁻¹dd⟩          (words AAB, ABC, BCD, Cdd)
```
`b = a^{-2}`, `c = a^{-1}b^{-1} = a`, `d = b^{-1}c^{-1} = a`, `d² = c ⇒ a = 1`; every relator
is cyclically reduced of length 3; `m_a = m_b = m_c = m_d = 3`; census 16 cases;
**γ_N = 0**. A non-thickenable sibling: `(ABC, ABD, ACD, Bcd)`, same shape, **γ_N = 2**.

### 4b. Degenerate allowed

| `N` | triangle cyclic-words | cubic tuples | trivial group | classes | classes with γ_N = 0 |
|---|---|---|---|---|---|
| 2 | 20 | 68 | 48 | 2 | **2 (100 %)** |
| 3 | 70 | 5 304 | 896 | 3 | **2 (66.7 %)** |

The three `N = 3` classes are `(AAB, ACC, BCb)` with **γ_N = 2**, `(AAB, cAC, BCb)` and
`(ABa, cAC, BCb)` with γ_N = 0. All three are AC-trivial by Thm S4.3(a); the first shows
that **cubic triangular does not imply thickenable** even in the degenerate world.

### 4c. What the fraction means

The task's key empirical question was: what fraction of cubic triangular presentations of
the trivial group are thickenable? Answer at the first rank where the question is not vacuous
(`N = 4`, non-degenerate): **64.29 %**, with the complement at defect exactly 2. That is a
large fraction and a strong motivation for the route; it is also not 100 %, so the Neuwirth
census stays informative inside the cubic world.

Two honesty caveats, both mandatory here.
* **These are not independent draws.** They are all the members of an exhaustively enumerated
  finite set at one rank, dominated by relabelings of a few classes; no p-value is quotable
  (lesson `contrast-length-confound.md`).
* Every presentation in this census is AC-trivial (they are tiny). A high thickenable
  fraction among *easy* presentations is evidence about the geometry of the cubic regime,
  **not** evidence that a hard presentation's cubic form would be thickenable.

---

## 5. The constructive attack (task item 2): the `SPLIT` calculus

### 5.1 Why the obvious moves cannot work inside the triangular world

Inside a presentation with all relators of length 3: AC1 and cyclic rotation (AC3) preserve
lengths but not multiplicities; a *single* AC2 is impossible, because `|r_i r_j|` after free
reduction is `6 − 2k ∈ {6,4,2,0}` — **never 3**. So the only length-preserving,
multiplicity-changing moves must route through a stabilisation. That is exactly the regime
S3 §4 identified as the one where extra generators stop being inert.

### 5.2 The move

> **Lemma S4.4 (`SPLIT`, a stable AC move).** Let `P = ⟨x_1..x_N | r_1..r_N⟩` present the
> **trivial** group and let `R` be a relator of length 3. Rotate `R` (AC3 + free reduction)
> to `R' = λ u v` with `λ, u, v` single signed letters. Then, with a fresh generator `t`:
> 1. AC4 adjoins `(t, t)`;
> 2. the free-definition move (S0 Lemma S-a; **triviality hypothesis is sharp**) replaces the
>    relator `t` by `t·w` for any `w ∈ F(x_1..x_N)` — take `w = uv`, giving the length-3
>    relator `D = t u v`;
> 3. as free words `D R'^{-1} = (t u v)(λ u v)^{-1} = t λ^{-1}`, so for any word `α`,
>    `α (t λ^{-1}) α^{-1} = (α D α^{-1})(α R'^{-1} α^{-1}) ∈ ⟪D, R'⟫`;
> 4. hence for every relator `S = α λ β` other than `R'` and `D`,
>    `α t β = (α (tλ^{-1}) α^{-1})·S` is reached by AC3+AC2 (twice), i.e. **any occurrence of
>    the letter `λ` (resp. `λ^{-1}`) outside `R'` and `D` may be rewritten to `t` (resp.
>    `t^{-1}`) by AC1–AC3.**
>
> Rank `+1`, relator count `+1`, **every relator still has length exactly 3**, and (because
> `t` is fresh) no relator loses free or cyclic reducedness. ∎

The identity in step 3 is asserted as an executable check in the implementation and fires on
every application.

*Move-count warning (FRAMING trap 6 / T-S5): step 2 is exponentially long in elementary moves.
Nothing here may be quoted as a move count.*

### 5.3 The occurrence-vector bookkeeping, as a linear system

Let `k` be the number of occurrences rewritten in step 4. Writing `g_λ, g_u, g_v` for the
generators of `λ, u, v` and `δ = m − 3·𝟙`:

```
m(t) = 1 + k ,   m(g_λ) −= k ,   m(g_u) += 1 ,   m(g_v) += 1
Δδ  = −k·e_{g_λ} + e_{g_u} + e_{g_v} + (k−2)·e_t          (e_t a NEW coordinate)
Σ Δδ = −k + 1 + 1 + (k−2) = 0                              ✔ always
```

`Σ_i m_i = 3N` before and after; the target `δ = 0` also has `Σδ = 0`. **So the occurrence
vector bookkeeping is identically balanced and there is no counting, parity or homological
obstruction coming from it.** (Corollary: introducing a generator adds 1 to the generator
count *and* 1 to the relator count *and* consumes exactly the occurrences its definition
relator spends — the three effects cancel exactly. This settles the task's bookkeeping
question in the negative: the linear system is never the obstruction.)

Useful special cases (all with `k = 2`, so the new generator lands at `m_t = 3` and is done):

| relator content (generator multiset) | choice of `λ` | `Δδ` | effect on `Σ\|δ\|` |
|---|---|---|---|
| `{a,b,c}` distinct | `a` | `−2e_a + e_b + e_c` | `−4` if `δ_a ≥ 2`, `δ_b,δ_c < 0` |
| `{a,a,b}` | `a` | `−e_a + e_b` | `−2` if `δ_a > 0 > δ_b` (the **parity-transfer** move) |
| `{a,b,b}` | `a` | `−2e_a + 2e_b` | `−4` if `δ_a ≥ 2`, `δ_b ≤ −2` |

`k = 1` and `k = 3` are also legal and give `δ_t = −1`, `+1` respectively.

### 5.4 The precise sticking point

The moves available at a given state are **not** a fixed lattice: `Δδ = −k e_a + e_b + e_c +
(k−2)e_t` is available only when `{a,b,c}` is the generator content of a relator that is
*actually present*, and the set of present relators is itself changed by every move. So
equalisation is a **reachability problem in a growing labelled bipartite structure**, not a
linear-solvability question. Concretely, the recurring terminal state in the searches is
`δ` with exactly one `+1` and one `−1`, which needs a parity-transfer relator of content
`{a,a,b}` with `a` the excess and `b` the deficit generator.

> **Observation S4.5 (the +1/−1 residue, a near-obstruction).** Every relator created by
> `SPLIT` has content `{t, g_u, g_v}` with `t` **fresh**. Such a relator has a repeated
> generator only when `g_u = g_v`, and then its *singleton* letter is the fresh `t`. So a
> parity-transfer move manufactured by `SPLIT` can only ever transfer one unit **out of the
> repeated generator**, never out of an arbitrary chosen excess generator; a residual excess
> sitting on an old generator can only be discharged along parity-transfer relators the
> triangulation already supplied, or relayed through fresh generators.

Observation S4.5 is **not** proved to be an obstruction — the relay through fresh generators
is not excluded, and the searches do escape the residue on some inputs (§6). `[GAP]` Whether
the relay always closes is exactly the open core of Q-red.

Two clean sufficient conditions do follow from the table in §5.3, and they are worth
recording because they are what a proof of Q would have to establish in general:

> **Lemma S4.6 (local sufficiency).** If at some state with `δ ≠ 0` there is a relator whose
> content is `{a,b,c}` with `δ_a > 0` and `δ_b, δ_c < 0`, or `{a,a,b}` with `δ_a > 0 > δ_b`,
> or `{a,b,b}` with `δ_a ≥ 2, δ_b ≤ −2`, then one `SPLIT` strictly reduces `Σ|δ|`.
> Consequently, if such a relator exists at every non-terminal state, equalisation
> terminates and **Q-red holds for that input**.

`[GAP]` No proof that such a relator always exists. That is the whole remaining content of Q.

### 5.5 A second, equivalent formalisation (recorded for the next session)

Restricting to *pure definitional stabilisation* (every new relator is `D_k = z_k w_k^{-1}`
with `|w_k| = 2`, every rewritten relator `s_i` has `|s_i| = 3` and `ρ(s_i) = r_i` under the
retraction `ρ: z_k ↦ w_k`), Q becomes an exact combinatorial DAG problem:

> **Shared straight-line program form.** Q holds for `P` (in this regime) iff there is a
> finite DAG with `n` **roots** (in-degree 0, out-degree 3), `M` **internal** nodes
> (in-degree **exactly 2**, out-degree 2), `n` **leaves** `x_1..x_n` (in-degree **exactly 3**),
> signed edges, whose root expansions freely reduce to an AC1–AC3 image of `(r_1..r_n)`.

"`z_k` occurs 3 times" is exactly "`z_k` is used twice besides its own definition", i.e.
in-degree 2 — the S3 §4 triple-line condition, restated as a degree condition. Slot counting
again cancels identically (`3n + 2M` out-slots vs `2M + 3n` in-slots), so again **no counting
obstruction**; the content is realisability of the expansion under the hard cap "each node may
be used at most twice, each original generator at most three times". Two worked instances:

```
⟨x | x⟩          ~st  ⟨x, z | z x z^{-1}, z x^{-1} x^{-1}⟩            (rank 2, γ_N = 0)
⟨x, y | x, y⟩    ~st  ⟨x,y,z,w | z x z^{-1}, z x^{-1}x^{-1}, w y w^{-1}, w y^{-1}y^{-1}⟩
                                                                       (rank 4, γ_N = 0)
```
both verified: all relators length 3, all multiplicities 3, trivial group, `γ_N = 0`. Both are
*degenerate* (the conjugation relator is not cyclically reduced), consistent with Prop S4.2.

---

## 6. AK(3) (task item 5): searched, not found, null calibrated

`AK(3) = ⟨x,y | xyxYXY, x³Y⁴⟩`, `L = 13`. The S0 triangulation (peel length-2 prefixes) gives
rank 9, nine relators of length 3:

```
P_Δ = ⟨x,y,p,q,r,s,t,u,v |  pYX, qXP, ryQ, rXY, sXX, tXS, uyT, vyU, vYY⟩
       m = (x:6, y:7, p..v: 2 each)   Σm = 27 = 3·9 ,   Σ|δ| = 14
```
certified trivial (Todd–Coxeter, index 1). Every relator here is cyclically reduced, and
`SPLIT` preserves that, so any equalisation of `P_Δ` lands in the **non-degenerate** world —
where Prop S4.2 forbids ranks ≤ 3 but permits everything from rank 4, so no contradiction.

**Search.** Beam search over `SPLIT` with `k ∈ {1,2,3}` and every subset of rewritten
occurrences, heuristic `Σ|δ| + 2·#{even multiplicities}` (a plain `Σ|δ|` heuristic gets
trapped on a parity plateau at `Σ|δ| = 2` — the residue of Observation S4.5), beam 45–60,
depth 8–14, over **48 distinct triangulations of AK(3)** (all rotations and inversions of the
two relators). **No cubic triangular form found.**

**Calibration, before reading that null** (lesson
`calibrate-one-sided-hunts-on-a-positive-ladder.md`):

| ladder | inputs | detection rate |
|---|---|---|
| small AC-trivial (rank 5–8 triangulations, `L ≤ 16`) | 3 | 3/3 = 100 % |
| **matched difficulty** — AC-trivial rank-2, `L = 13`, triangulated to rank 9, `Σ\|δ\| = 14` | 12 | **4/12 = 33 %** |

Successful matched-difficulty examples (each solved at rank 13):
`(Yxyyyxyyy, YYYX)`, `(xYXYX, xyxyyxyy)`, `(xyyXXXY, yyXXXY)`, `(XYXXXYXXX, YXXX)`.

**Therefore: the AK(3) null is worth 48 *correlated* attempts at a 33 % marginal rate.** The
48 attempts are triangulations of the same two words and the search is deterministic given the
triangulation, so they are far from independent; this is suggestive of a real obstruction on
AK(3) but is emphatically **not** evidence, and it must never be reported as one. A negative
here would in any case only be a statement about *this* move calculus, not about stable AC.

**No cubic triangular presentation in AK(3)'s stable class is delivered by this file.**

---

## 7. What this changes for the S-line

1. **S3 §4's target must be restated.** "Bring `P` to cubic triangular form" is two questions;
   only the cyclically-reduced one (Q-red) is a real normal form, and it has no solutions
   below rank 4. Any future work quoting the `⟨x,y | xyX, yxY⟩` motivation is quoting a
   degenerate example that is AC-trivial by move (0) alone.
2. **The route is worth continuing**, on the strength of the 64 % thickenable fraction at
   rank 4 and the fact that the cubic census is 16 cases where AK(3)'s rank-2 census is
   astronomically larger.
3. **The next concrete step** is Lemma S4.6: find a proof (or a counterexample) that a
   `Σ|δ|`-reducing relator always exists, or find the invariant behind Observation S4.5.
   Either outcome is publishable on this line: the first proves Q-red, the second is the
   first genuine obstruction theorem about high-rank normal forms.

## 8. Traps added to the line

* **T-S8.** *Cubic triangular is two conditions, not one.* A length-3 relator that is not
  cyclically reduced is `a b a^{-1}` and cyclically reduces to a single letter, dropping the
  rank (Thm S4.3). Never quote a cubic form without saying whether it is degenerate. No
  non-degenerate cubic triangular presentation of the trivial group exists below rank 4.
* **T-S9.** *`γ_N` is cheap in the cubic regime but not automatic.* 36 % of rank-4
  non-degenerate cubic triangular presentations of 1 have `γ_N = 2`. "Cubic ⇒ thickenable" is
  false; the route buys a cheap decision, not a positive answer.
* **T-S10.** *Occurrence-vector counting is never the obstruction.* Both formalisations of
  Q (the `SPLIT` calculus, §5.3, and the SSLP DAG, §5.5) have identically balanced slot
  accounting. Any future claim of a "counting/parity obstruction to cubic form" should be
  checked against these two identities before it is believed.
* **T-S11.** *A `Σ|δ|` greedy on `SPLIT` has a parity plateau at `Σ|δ| = 2`.* The escape
  requires a temporarily cost-increasing move that makes all multiplicities odd. A search
  that stalls at cost 2 has found a heuristic artefact, not an obstruction.

---

### Artefacts (scratch, not committed)

`enum_cubic2.py` (census), `det_obstruction.py` (Prop S4.2 scan), `equalize.py`
(triangulation + `SPLIT` + search) in the session scratchpad. All computations here are
reproducible from `experiments/stable_ac/fable/neuwirth_rank_n.gamma_N_factorial_n` and
`experiments/stable_ac/fable/coset_enum.is_trivial_group` with `PYTHONPATH=/home/user/ACSolverX`.
