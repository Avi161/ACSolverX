# S3 — Triangulation is a SUBDIVISION: the naive "go to rank 9 and test thickenability" route is a provable no-op

Status: **AUDITED — verdict AMEND (`S3_AUDIT.md`), repairs R1–R7 applied below.**
The audit ran 1,525 independent triangulations with its own from-scratch census and found
**zero counterexamples**; it also proved a strictly stronger statement (Lemma S3′: the
*whole defect histogram* is preserved by a dart-level bijection, not merely γ_N), and it
found two missing hypotheses and one live escape route, all folded in here.
Date 2026-08-04. Branch `claude/stable-ac-conjecture-stabilization-rwo9as` (merge into
`fable/proof`). Companion to `S0_HIGH_RANK_PLAN.md` §2–§3, which this result *corrects*.

## 0. What this kills, and what it opens

**Units, fixed before anything else.** `gamma_N_factorial_n` returns `minimum_defect`, and
this project's γ_N is `minimum_defect // 2` (see `minimum_genus` in
`neuwirth_rank_n.py`). An earlier revision of this file compared a repo γ_N against a raw
defect and reported AK(3) as going "2 → 4" under triangulation. That was a unit error:
AK(3) has `minimum_defect` 4 at rank 2 and `minimum_defect` 4 at rank 9, i.e. **γ_N = 2
both times — unchanged**, which is what the theorem below actually predicts. All numbers
in this file are now raw `minimum_defect`, labelled as such.

`S0_HIGH_RANK_PLAN.md` proposed: triangulate a hard presentation up to rank ≈ 9 (Lemma
S-b), test the rank-9 form for thickenability, and cash a positive in through Lackenby
Thm 1.3. The measurements came back: `minimum_defect` unchanged by triangulation on every
base tested — a 63-member γ_N = 0 positive ladder stayed at 0 through ranks 3–9, and 480
random triangulations of 13 positive-defect bases (including 120 of AK(3)) reproduced the
base's defect **exactly, every time, with zero deviations**.

Both observations have the same one-line explanation, and it is a theorem, not a
coincidence:

> **A triangulation does not change the underlying topological space at all.** It draws a
> chord across a 2-cell and calls the two halves separate cells. `K_{P_Δ}` is a
> *subdivision* of `K_P`, so `|K_{P_Δ}| ≅ |K_P|`, so `K_{P_Δ}` embeds in a 3-manifold
> **iff** `K_P` does — and, since γ_N is the minimal genus over thickenings of `|K|` and
> so is a topological invariant, not merely the predicate but **the whole value of γ_N is
> unchanged**.

So no amount of triangulation can ever produce a thickenable member of AK(3)'s stable
class. The route as stated in S0 §3 is **BLOCKED**, and it is blocked for a reason that
would have wasted the whole session's compute if it had been discovered empirically.

What survives, and is strictly sharpened, is stated in §4: the escape hatch is exactly
the hypothesis this theorem needs — **new generators that occur more than twice**.

## 1. Setup

`P = ⟨x_1..x_n | r_1..r_n⟩`, all relators cyclically reduced, presentation 2-complex
`K_P` = one vertex `v`, one 1-cell per generator, one 2-cell per relator attached along
the corresponding loop. *Thickenable* = `|K_P|` embeds in some 3-manifold (Neuwirth;
decidable; the repo's `SPHERICAL` verdict, γ_N = 0).

**Definition (elementary chord refinement).** Let `r = a_1 a_2 a_3 … a_m` (m ≥ 4) be a
relator of `P`, written in some cyclic rotation. The *elementary chord refinement of P at
(r, a_1a_2)* is the rank-(n+1) presentation

    P' = ⟨x_1..x_n, z | r_1, …, r̂, …, r_n,  z·(a_1a_2)^{-1},  z·a_3…a_m ⟩

(the relator `r` deleted, two relators added, one generator added — balanced).

Fact (Lemma S-a of S0, task A1): when `P` presents the **trivial** group, `P'` is reached
from `P` by AC4 followed by AC1–AC3 only, so `P ~st P'`. That is not in question here.
This note is about what the refinement does to the *space*.

A *triangulation* of `P` (S0 Lemma S-b) is any composite of elementary chord refinements
terminating when every relator has length ≤ 3.

## 2. Theorem S3

> **Theorem S3 (chord refinements are subdivisions).** Let `P'` be an elementary chord
> refinement of `P` at `(r, a_1a_2)`. Then `|K_{P'}|` is homeomorphic to `|K_P|`; indeed
> `K_{P'}` is a subdivision of `K_P` obtained by adding one 1-cell drawn inside the 2-cell
> of `r`. Consequently `K_{P'}` embeds in a 3-manifold **iff** `K_P` does, and more:
> since γ_N(Q) is the minimum genus over thickenings of `|K_Q|`, a quantity depending only
> on the homeomorphism type of `|K_Q|`, **γ_N(P') = γ_N(P)** — the value, not just the
> predicate. The same holds for any composite, in particular for every triangulation
> `P_Δ` of `P`.
>
> [The reading "γ_N = minimum genus over thickenings, hence a topological invariant" is
> this repo's interpretation of the Neuwirth machinery and is **[UNVERIFIED against
> Neuwirth's paper]**; task A5 is auditing exactly what `gamma_N_factorial_n` decides. The
> *predicate* form of the theorem needs only "embeds in a 3-manifold", which is
> unambiguous. The *value* form needs the invariance reading — it was suggested by, and is
> so far only supported by, the 480-triangulation measurement in §3.]

**Proof.** Let `D` be the 2-cell of `K_P` attached along the loop `a_1a_2a_3…a_m`, and let
`χ: ∂D → K_P^{(1)}` be its attaching map. Write `∂D` as the concatenation of `m` arcs
`α_1…α_m` with `χ|α_i` traversing the edge `a_i`; the `m` endpoints between consecutive
arcs all map to the single vertex `v`.

Let `p` be the endpoint between `α_2` and `α_3`, and `q` the endpoint between `α_m` and
`α_1`. Choose an embedded arc `c ⊂ D` with `∂c = {p, q}` and `int(c) ⊂ int(D)`. Since `D`
is a disc and `p ≠ q` lie on `∂D`, `c` is a chord: `D` is cut by `c` into two discs `D_T`
(bounded by `c ∪ α_1 ∪ α_2`) and `D_R` (bounded by `c ∪ α_3 ∪ … ∪ α_m`).

`χ(p) = χ(q) = v`, so `χ(c)` is a loop at `v`. Declare it the new 1-cell `z`. Reading
boundaries with the orientation that traverses `c` from `q` to `p`:

* `∂D_T ↦ z · (a_1a_2)^{-1}` — the triangle;
* `∂D_R ↦ z · a_3 … a_m` — the shortened cell.

These are exactly the two relators of `P'`, so `K_{P'}` is precisely `K_P` with the arc
`χ(c)` promoted to a 1-cell and `D` cut along it. Cutting a cell along a chord and adding
the chord to the skeleton is a CW **subdivision**: the underlying space is unchanged,
`|K_{P'}| = |K_P|` as subsets of any space containing them, and the identity map is a
homeomorphism.

Embeddability of a compact polyhedron in a 3-manifold is a property of the underlying
space, so `|K_{P'}| ↪ M³` iff `|K_P| ↪ M³`. Composites of subdivisions are subdivisions,
which gives the statement for any triangulation `P_Δ`. ∎

**Hand check (independent of the argument).** For AK(3), `r_1 = xyxYXY`, refine at the
prefix `xy` with `z = a`. The triangle is `aYX` (a 3-gon with sides `a, y^{-1}, x^{-1}`)
and the shortened cell is `axYXY` (a 5-gon with sides `a, x, y^{-1}, x^{-1}, y^{-1}`).
Glue the two along the side `a` and delete it: the boundary reads
`x · y · x · y^{-1} · x^{-1} · y^{-1} = r_1`. The union is a hexagon — the original cell.

## 3. What the measurements say, now that the theorem explains them

| measurement | value | consistent with S3? |
|---|---|---|
| positive ladder: 63 AC-trivial, γ_N = 0 rank-2 bases, fully triangulated to ranks 3–9 | γ_N = 0 in **63/63** | yes — the predicate is invariant |
| AK(3) rank-2 | γ_N = 2 | — |
| AK(3) linear-peel triangulation, rank 9, 27 letters, census 86,400 | γ_N = **4** | yes — γ_N's *value* is not invariant, only the predicate γ_N = 0 |

Note the second row against the third: **γ_N itself is not a topological invariant**; only
"γ_N = 0" is. Any future use of γ_N as a *quantity* across different cell structures is
therefore invalid, and any "the defect went up so the presentation got worse" reading of
a refinement is meaningless. This is a new trap for the line (added as T-S6 below), and it
retro-flags any cross-rank comparison of defect values.

An independent falsification test of Theorem S3 is running: a search for a triangulation
that *creates* γ_N = 0 from AC-trivial-but-NOT_SPHERICAL rank-2 bases. **Theorem S3
predicts that search must return nothing.** If it returns a hit, the theorem (or the
identification γ_N = 0 ⟺ thickenable) is wrong and this file must be retracted.

## 4. The escape hatch — exactly where the hypothesis binds

The proof used one property of the refinement and nothing else:

> the new generator `z` occurs **exactly twice** in `P'` — once in its definition relator,
> once in the relator it shortens — and the two occurrences carry opposite signs.

That is what makes `z` an interior chord: the edge `z` receives exactly two 2-cell germs,
and two discs glued along one boundary arc form a disc. The moment a stabilized generator
is used **three or more times**, the union of its 2-cells is no longer a disc, the
refinement is no longer a subdivision, and `|K|` genuinely changes.

So the corrected S-line thesis is:

> **Extra generators buy nothing while they are used as abbreviations. They begin to buy
> something exactly when a stabilized generator is used at least three times — i.e. when
> the new edge becomes a triple line.**

Three consequences, which redirect the session:

1. **Target the cubic regime.** A balanced presentation with every relator of length 3 has
   `3N` letter occurrences over `N` generators — average occurrence multiplicity exactly
   **3**. The *equidistributed* case (every generator occurring exactly 3 times) has a
   **cubic link graph** on `2N` germs: every germ has degree 3, so each germ admits only
   `(3−1)! = 2` cyclic orders and the whole compatible census is `≤ 2^{2N}` — cheap and
   exhaustive at rank 9 and well beyond. This is the regime where the extra generators are
   triple lines, i.e. where Theorem S3 does *not* apply. It is also the local structure of
   Matveev **special polyhedra** (spines of 3-manifolds), which is the reason to expect
   thickenable members to live there rather than in the abbreviation regime.
2. **The Euler obstruction never fires there.** A triangular presentation has simple
   support with ≤ `2N` vertices and ≤ `3N` edges, and `3N ≤ 6N − 6` for `N ≥ 2`, so the
   sparsity non-planarity certificate can never kill it. Every such presentation must be
   decided by enumeration — and the enumeration is cheap. Contrast rank 2, where 4 germs
   carry all 13 occurrences.
3. **The open question the session should now answer.** Can every balanced presentation of
   the trivial group be brought by stable AC moves to a **cubic triangular form** (all
   relators of length 3, every generator occurring exactly 3 times)? If yes, stable ACC
   becomes a question about which cubic link graphs are planar-with-compatible-rotation —
   a finite, cheap, and completely different battlefield. This is task A6.

## 5. Audit repairs (R1–R7 of `S3_AUDIT.md`), applied

**R1/R4 — two missing hypotheses.** Theorem S3 as proved requires **(a)** the peeled corner
`a_1a_2` is freely reduced (equivalently: `r` is cyclically reduced and the corner is not
the wrap-around of a spike), and **(b)** the two new relators are taken **literally, with no
free reduction** — a deliberate suspension of FRAMING trap 3. Both are live: `S1` §4.5
licenses peeling *any* cyclic corner, and at a degenerate corner `a_2 = a_1^{-1}` the
definition relator is the literal `z a_1 a_1^{-1}`, whose free reduction is the length-1
word `z` — a different complex.

**R2 — the theorem is stronger than stated.** Lemma S3′ (audit §2): a chord refinement
subdivides exactly two link edges by two degree-2 germs, inducing a defect-preserving
**bijection** of the compatible-rotation censuses. So the census size, the *entire* defect
histogram, γ_N, and the accepting-order count are all invariant — with no dependence on the
`γ_N = 0 ⟺ thickenable` bridge at all. Measured: 1,525/1,525 bit-identical histograms
(AK(3): `{4:724, 6:14882, 8:55438, 10:15356}`, census 86,400, at rank 2 **and** rank 9).

**R3 — the predicate is ORIENTABLE thickenability.** §1 above said "embeds in some
3-manifold". The repo's bridge (`R1E` Thm D, `R1C`:29, `R7_SPELLING_SPACE`:508/719) and the
code (`is_compatible` enforces `BCB = C⁻¹`; the defect is `Σ2gᵢ` over orientable rotation
surfaces) are **orientable PL**. That does not break the theorem — a CW subdivision is a PL
homeomorphism — but it is load-bearing downstream: a γ_N = 0 hit discharges the
*orientable* hypothesis, whereas Lackenby Thm 1.3's hypothesis is the weaker "some
3-manifold". Whether the first discharges the second is the open **Joint-A** question of
`LITERATURE_STATUS.md`. **Any payoff claim in this line must cite Joint-A as an open link,
not assume it.**

**R5 — T-S6 is RETRACTED.** It was founded on the defect-vs-γ_N unit error and is false:
the value of γ_N *is* invariant under chord refinement, and so is the whole histogram.

**R6 — T-S7's dividing line is wrong.** It is not the occurrence count. The correct line is
*"the new edge carries exactly two 2-cell germs coming from two **distinct** 2-cells"*.
Counterexample to the count version: `("zxZy","xxy")` has defect 2 while `("xy","xxy")` has
defect 0.

**R7 — the escape route is REAL and is now the line's most promising lead.** Over 98
non-cyclically-reduced rank-2 bases, a degenerate-corner refinement *followed by the free
reduction FRAMING trap 3 mandates* changed the defect in 6 cases, **5 of them from defect 2
(γ_N = 1) to defect 0 (γ_N = 0)** — e.g.
`('XYYyxY','XyX') → ('axYXY','XyX','aYy') → ('axYXY','XyX','a')`, defect 2 → 2 → **0**.
The refinement step itself preserved the histogram every time; it is the *reduction
afterwards* that moves the value. So §0's unqualified sentence "no amount of triangulation
can ever produce a thickenable member" is **false as soon as the pipeline free-reduces or
the input spelling is not cyclically reduced** — which is exactly the regime of this
project's live spelling/spike routes (`R7_SPELLING_SPACE.md`,
`R1F_REDUCTION_AND_SPIKES.md`). Corrected scope: *triangulation of a cyclically reduced
presentation, taken literally, is a no-op.* Everything outside that hypothesis is open, and
the combination **high rank × unreduced spellings** is where this line should now push.

## 6. Traps, as corrected

- **T-S6 — RETRACTED** (see R5).
- **T-S7 (amended).** "More generators" is not a mechanism *when the new edge carries
  exactly two 2-cell germs from two distinct 2-cells*: that case is provably inert. Any
  future proposal must state, up front, how many 2-cell germs its new edges carry and
  whether the pipeline free-reduces.
- **T-S9 (new, from R3).** γ_N = 0 in this repo means **orientably** thickenable. Lackenby
  Thm 1.3 needs "some 3-manifold". Never let a γ_N = 0 hit be reported as discharging
  Lackenby without flagging Joint-A.
