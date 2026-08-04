# A14 — Adversarial audit of S6 (move classification), S8 (splitting monotonicity) and S4 (cubic normal form)

Auditor task, branch `claude/stable-ac-conjecture-stabilization-rwo9as`
(**must be merged into `fable/proof` by the user**). Date 2026-08-04.
Targets are **not edited** by this file; every repair is written as an instruction for the
orchestrator to apply.

**Instruments.** All numbers below come from a from-scratch re-implementation of the
Neuwirth census (`scratchpad/aud.py`): my own link builder (germs, corner involution `A`,
occurrence involution `B`), my own compatible-rotation enumerator, my own
`defect = nA − nC + 2L − nAC`, my own free/cyclic reduction, and my own HLT Todd–Coxeter
(`scratchpad/tc.py`). Nothing is imported from `neuwirth_rank_n.py`, `coset_enum.py` or any
sweep script. The instrument was validated before use on three anchors it had to reproduce
blind:

| anchor | census | my defect histogram | repo value |
|---|---|---|---|
| `("xyXY","xxy")` | 12 | `{0:2, 2:6, 4:4}` | matches S6 §10 |
| `("xyXY","yYxxy")` | 144 | `{2:26, 4:94, 6:24}` | matches S6 §10 |
| AK(3) `("xyxYXY","xxxYYYY")` | 86,400 | `{4:724, 6:14882, 8:55438, 10:15356}` | matches S3 §5 R2 |

Todd–Coxeter validated on `⟨x,y\|x²,y³,(xy)⁵⟩ = 60`, `(xy)⁴ = 24`, `⟨x,y\|x³,y²,(xy)³⟩ = 12`,
`⟨x,y\|xyXY,x³,y³⟩ = 9`, AK(3) index 1.

---

## 0. Verdicts

| target | verdict | one-line reason |
|---|---|---|
| **S6 T1** (AC1 = homeomorphism) | **CONFIRMED** | proof correct; 0 deviations in my own re-census |
| **S6 T4** (AC4/AC5 = wedge on a disc) | **CONFIRMED** | the "no complementary face" worry is void: an embedded compact 1-complex is nowhere dense in `S²`, so `S² ∖ Λ` is always a nonempty open set — a triangulation of `S²` has open triangles, which is all the proof needs |
| **S6 T4′** (first slide over a fresh stabilizer = subdivision) | **CONFIRMED** | the degenerate (monogon) chord geometry does go through; checked separately, plus 72 bases including length‑1 relators, histogram-identical every time |
| **S6 T2** (single-generator AC3 = a spike) | **CONFIRMED** | `build_link_n` really is rotation-invariant (its corner involution wraps around); 110 rotations and 156 (conjugate, spike) pairs, 0 histogram mismatches |
| **S6 T0** (move (0) changes the space) | **CONFIRMED** | local-homology argument correct; both certificates reproduce |
| **S6 flip table** | **AMEND — three defects, one of them serious** | the rates do **not** survive the trivial-group restriction (§1.5); the `M0` row is the `M2nc` row re-partitioned, not an independent census (§1.3); the `M3` denominators are 14 pairs short (§1.4) |
| **S6 §8 headline collapse** | **AMEND (antecedent already refuted in-session)** | "stable ACC becomes a statement purely about AC2" is conditional on Conjecture SR, which `S11` (A10) refuted **on the trivial group**. S6 still records SR as `[OPEN]`, "0 counterexamples" |
| **S8 Conjecture + [GAP-S8-1]** | **AMEND — gaps dischargeable, conjecture survives** | the bookkeeping closes exactly (§2.1) and the sketch upgrades to a proof; **379,364** new split states, none below base |
| **S8 [GAP-S8-2]** | **AMEND — the stated worry is vacuous** | the bigon's two link edges are `u⁻—g⁻` and `u⁺—g⁺`; they are **never** loops and are always vertex-disjoint; the degenerate "re-route every occurrence" split is fine |
| **S8 §4 headline negative** | **REFUTED by this session's own S4B** | "adding generators is worth nothing as long as they only re-describe the existing relators" is false: `C1` re-describes AK(3) and has `γ_N = 1 < 2` |
| **S4 Thm S4.1** (sign rigidity) | **CONFIRMED** | brute force over every cyclically reduced length-3 word at `N ≤ 4`: 0 violations |
| **S4 Prop S4.2** (`N ≤ 3` obstruction) | **CONFIRMED** | independent enumeration: 0 of 20 (`N=2`) and 0 of 1,816 (`N=3`) have `\|det\| = 1` |
| **S4 §4a census / Lemma S4.4** | see §3 | |

---

## 1. S6 — the move classification

### 1.1 T4′ — the monogon chord. CONFIRMED, and it is stronger than stated.

The task's worry is that a monogon is not a polygon with two distinct boundary vertices, so
the Schoenflies step of S3 may not transfer. It does. Writing `Φ: D² → K_P` for the
characteristic map of the `r_1`-cell and `c ⊂ D²` for an embedded arc with both endpoints at
`p_0` and `int(c) ⊂ int(D²)`:

* `c ∪ {p_0}` is a simple closed curve in `D²` meeting `∂D²` in the single point `p_0`.
  Embed `D² ⊂ S²`; by Jordan–Schoenflies the curve bounds a disc `E ⊂ int(D²) ∪ {p_0}` on
  one side. The other side inside `D²` is `F = int(D²) ∖ \overline{E}`, whose closure is a
  disc bounded by `c ∪ ∂D²`. The *only* difference from S3 is that at `p_0` the local
  half-disc is cut by the two strands of `c` into **three** sectors (two belonging to `F`,
  one to `E`) instead of the two-plus-two of a genuine chord. So `p_0` occurs **twice** on
  the boundary walk of `F`. That is legal for a CW characteristic map — the attaching map of
  a 2-cell is never required to be injective on `∂D²` — and it is exactly what produces the
  boundary word `r_1 z^{ε}` of length `k+1`.
* `E`'s attaching map `∂D² → Φ(c) ∪ {v}` is a homeomorphism onto a circle, so `E` really is
  the length-1 relator's 2-cell, up to the sign `z^{−ε}` which T1 absorbs.
* The degenerate inputs the task lists are all fine. `|r_1| = 1`: `k = 1`, one boundary
  vertex, everything above is unchanged. `r_1` empty: **excluded at the source** — the
  presentation complex of an empty relator is not in the model (`build_link_n` raises), so
  T4′'s hypothesis should say `|r_1| ≥ 1` explicitly. `r_1` already contains `z`: outside
  T4′'s hypothesis by construction, and this is the `m_z ≥ 3` regime the note itself flags.

**Measured (my own census).** 72 bases including `("x","y")`, `("x","yy")`, `("xy","y")`,
`("xx","y")` and four single-relator presentations: `γ_N(P⁺) = γ_N(P)` in 72/72 and
`γ_N(G1) = γ_N(G1i) = γ_N(P)` in 144/144 — **and the entire defect histogram was
bit-identical in every one of the 144 comparisons**, not merely the value.

> **Repair R-A (strengthening).** T4′ currently claims only `|K_G| ≅ |K_P|` and hence the
> predicate. The histogram evidence says T4′ admits a Lemma-S3′-style **dart-level
> bijection** (census size, whole histogram, accepting-order count). Worth proving; it would
> make T4′ independent of the `γ_N = 0 ⟺ thickenable` bridge exactly as S3′ is.
>
> **Repair R-B (hypothesis).** Add `|r_1| ≥ 1` and "z occurs in no `r_i`" to T4′'s statement.

### 1.2 T2, T4, T1, T0 — CONFIRMED

* **T2's premise checks out in the code.** `build_link_n`'s corner involution is
  `A[2i+1] = 2·((k+1) mod m)` — it **wraps around** — so a cyclic rotation of a relator gives
  a literally isomorphic `(A, B, germ)` structure. 110 rotations of 40 random bases: 0
  histogram mismatches. And 156 pairs `(c r c^{-1}, c^{-1}c r)` with the product freely
  reduced: 0 histogram mismatches. T2(a)'s cyclic-word identity is correct
  (`c r c^{-1} ∼ c^{-1} c r ∼ r c^{-1} c`), and the transfer of the spike calculus to AC3 is
  sound. The bound directions in T2.b are also stated the right way round: from
  `γ_N(image) ≥ γ_N(base) − k`, `γ_N(base) > k` does force `γ_N(image) > 0`.
* **T4's "complementary face" worry is void.** An embedded compact 1-complex `Λ ⊂ S²` is
  nowhere dense (invariance of domain), so `S² ∖ Λ` is a nonempty open set **whatever** `Λ`
  is — including a triangulation of `S²`, whose complementary faces are open triangles. The
  arc `β` needs only an open set to live in; "free face" is not the relevant notion. The
  rest of the argument (two cones from one apex over disjoint subsets of `∂R` meet only at
  the apex) is correct, and orientability is indeed never used.
* **T1** and **T0** are correct as written; T0's two certificates reproduce
  (`("xyXY","xxy")` defect 0, `("xyXY","yYxxy")` defect 2, my own census).
* Every worked example in S6 §10 reproduces exactly under my instrument, including
  T2.d's trivial-group pair `("xYY","xYxYY")` `γ_N=0` → `("xxYYX","xYxYY")` `γ_N=1`
  (triviality re-certified by my own Todd–Coxeter, index 1).

### 1.3 The flip table's `M0` row is the `M2nc` row re-partitioned — not a second census

The table presents six rows as six measurements. Two of them are one measurement. From
S6's own numbers:

```
M2nc:  3,507 measured = 1,312 thickenable bases + 2,195 non-thickenable bases
       315 destroy, 0 create
M0  :  "creates in 315 of 2,510 non-thickenable spellings;
        destroys in 0 of 997 thickenable spellings"
       2,510 + 997 = 3,507        2,195 + 315 = 2,510        1,312 − 315 = 997
```

The identities close exactly: the `M0` row is the same 3,507 AC3 pairs, partitioned by the
**image**'s predicate instead of the **base**'s. This is internally consistent with T2 (they
*are* the same operation), but it has one bad consequence in §8:

> "the *only* moves in the whole classification that created thickenability anywhere in this
> session were plain rank-2 AC2 slides (73 events) and move (0) reductions (315 events)"

reads as two independent sources; it is 73 AC2 events plus **the same 315 events counted a
second time from the other end**. Likewise the `0 of 997` null for Conjecture SR is not
independent of the `0 create of 3,507` null for AC3.

> **Repair R-C.** Merge the `M0` and `M2nc` rows, or label the `M0` row "same 3,507 pairs,
> read in the reduction direction". Remove the impression of two independent nulls.

### 1.4 The `M3` denominators are 14 pairs short

With 1,118 bases and 4 AC2 images each (`r_i r_j^{±1}`, `i ∈ {1,2}`), the `M3` row should
account for 4,472 pairs. §7 accounts for `1,863 measured + 2,595 skipped = 4,458`. The other
three rows close exactly (`M1` 2×1,118 = 2,236 ✓, `ROT` 4×1,118 = 4,472 ✓, `M4` 1,118 ✓,
`M2nc + M2c + skips` = 8×1,118 = 8,944 ✓). Fourteen `M3` pairs are unaccounted. The likely
cause is legitimate (`freered(r_i r_j^{-1})` empty, or a generator vanishing from the
presentation), but the note's own rule is that excluded pairs are *counted*, and these are
not.

> **Repair R-D.** State the exclusion rule for `M3` and add the 14 to a third column.

### 1.5 THE SERIOUS ONE — the flip rates do not survive the trivial-group restriction

S6 §9 `[GAP-T]` concedes that the corpus is unrestricted "deliberately", on the ground that
"the move classification is a statement about word-realized complexes, at which level the AC
moves act identically". That defence is fine for T1/T2/T4/T4′. It is **not** fine for the
rates, and §8 uses the rates: "24 % of the time it *costs* the property one is testing for",
trap T-S8, and the practical reading of `[GAP-1STEP]`. The AC programme only ever acts on
presentations of the trivial group.

I re-measured with my own instrument on two corpora built and processed identically, in the
same length band (per-relator 3–6, total 7–11, cyclically reduced, both generators used,
deduplicated up to rotation/inversion/relator swap), cap 1.2·10⁵:

* **trivial-group corpus** — random AC1/AC2/AC3 walks from `("x","y")`, so every member is a
  balanced presentation of the trivial group **and** AC-trivial, with no coset enumeration
  needed and no member in doubt;
* **unrestricted control** — random cyclically reduced rank-2 presentations, same band.

| corpus | family | measured | skipped | destroy / thickenable base | create / non-thickenable base |
|---|---|---|---|---|---|
| **trivial group** (163 bases) | **M3 (AC2)** | 236 | 416 | **8 / 59 = 13.6 %** | **34 / 177 = 19.2 %** |
| | **M2nc (AC3)** | 498 | 154 | **4 / 76 = 5.3 %** | 0 / 422 |
| | M2c (AC3, cancelling) | 474 | 178 | 0 / 76 | 0 / 398 |
| **unrestricted** (259 bases) | M3 (AC2) | 598 | 438 | 116 / 245 = 47.3 % | 17 / 353 = 4.8 % |
| | M2nc (AC3) | 982 | 54 | 72 / 331 = 21.8 % | 0 / 651 |
| | M2c (AC3, cancelling) | 958 | 78 | 0 / 321 | 0 / 637 |

The control **reproduces S6's published rates** (S6: 51.5 % destroy / 7.0 % create for M3,
24.0 % destroy for M2nc, 0/0 for M2c) to within the sampling noise of a few hundred pairs.
That is the calibration that makes the other row readable: the two instruments agree on the
unrestricted corpus, so the shift is caused by the trivial-group restriction and by nothing
else.

**What changes, and it is not a small correction.**

1. **AC2's create rate roughly quadruples** on trivial-group bases (4.8 % → 19.2 %) while its
   destroy rate falls by a factor 3.5 (47.3 % → 13.6 %). S6's `M3` row — "51.5 % of
   thickenable bases lose it, 7.0 % of non-thickenable bases gain it" — describes arbitrary
   balanced rank-2 presentations and materially **understates** how productive AC2 is in the
   only regime the conjecture is about. On this corpus AC2 is nearly *net-positive*: it
   creates thickenability three times as often as it destroys it (34 vs 8 events).
2. **AC3's destroy rate collapses**, 21.8 % → 5.3 %. S6's headline "**this is the single most
   consequential finding of the task** … 24 % of the time it costs the property one is
   testing for" and its trap T-S8 are quoting an unrestricted-corpus number. S6's own
   AC-trivial run reports 16.3 % (170/1,040); I get 5.3 % (4/76). My thickenable-base
   denominator here is small, so treat the *value* as loosely pinned — but 24 % is not the
   trivial-group number by anyone's measurement, including S6's own.
3. **`M2c` (cancelling AC3) stays perfectly inert** on both corpora — 0 flips in 1,432 further
   pairs. Conjecture S6-C survives the restriction and gains evidence.

Length stratification (the `contrast-length-confound.md` control) is in §1.7; the direction
of the gap survives it.

> **Repair R-E (the important one).** Every rate in the S6 flip table must be labelled
> "unrestricted balanced rank-2 corpus", and the trivial-group rates above quoted beside
> them. Trap T-S8's "24 %" must become "≈ 5 % on trivial-group bases; 22 % on an
> unrestricted corpus". §8's sentence "AC3 … 24 % of the time it *costs* the property one is
> testing for" is the sentence most likely to be re-quoted downstream and is the one most
> wrong for the AC programme.

### 1.6 S6 §8's collapse is dead: its antecedent was refuted in this same session

S6 §4/§8/§9 rest Conjecture SR on "0 counterexamples in ≈114,000 measured complexes" plus
"0 of 997" here, and §8 says:

> "If `R7`'s Conjecture SR holds, … **stable ACC becomes a statement purely about AC2**"

`S11_SPELLING_AT_HIGH_RANK.md` (task A10, same branch, same day) **refutes Conjecture SR**,
with 28 counterexamples, one family on balanced presentations of the **trivial group** at
Todd–Coxeter index 1 — precisely the hypothesis class. `S13_SYNTHESIS.md` §3c records the
chain `("ABbbabAAaB","baB")` defect 0 → `("AbabAAaB","baB")` defect 2 → `("AbabAB","baB")`
defect 0. S11 also explains why 120,000 measurements missed it: every earlier corpus was
"cyclically reduced base **plus one move**", i.e. depth `k = 1` only, and SR breaks at
`k = 2`. **S6's 997 pairs are depth-1 pairs and are therefore powerless against SR by
construction** — the null is not weak evidence, it is *zero* evidence.

> **Repair R-F.** S6 §4 "Direction", §8's conditional collapse, and §9 `[GAP-SR]` must be
> rewritten: SR is FALSE, the spelling direction does **not** collapse, and "stable ACC
> becomes a statement purely about AC2" must be **withdrawn**. The correct residual statement
> is the weaker one S11 leaves standing: in all 28 counterexamples the *fully reduced* form
> already had defect 0, so no spelling has yet been found that beats its own reduction —
> which is the statement AK(3) actually needs, and it is open.

### 1.7 Two smaller defects in S6

* **§0 item 3 cites a retracted trap.** "`γ_N`'s value is not comparable across cell
  structures; only `γ_N = 0` is topological (trap T-S6 of `S3_SUBDIVISION_INVARIANCE.md`)" —
  but S3 §5 R5 **retracts T-S6** ("it was founded on the defect-vs-γ_N unit error and is
  false: the value of γ_N *is* invariant under chord refinement"), and S3 §6 lists it as
  RETRACTED. S6's own T4/T4′ measurements (exact `γ_N` equality, 3,332/3,332, and my
  bit-identical histograms) contradict §0 item 3 directly. Note also that **S3 §3's own table
  and the paragraph after it were never repaired** — lines 121–130 still assert AK(3) goes
  `γ_N = 2 → 4` under triangulation and that "`γ_N` itself is not a topological invariant".
  An audited file still carrying the refuted claim in its body is how this trap propagated
  into S6.
* **The 24 % is a short-band number.** §7 reports A: 145/1,743 and C: 166/1,708 — that is
  3,451 of the 3,507 `M2nc` pairs and 311 of the 315 destroys. Sweep B (total length 11–14)
  contributed **56 measured pairs and 4 destroys**: it was almost entirely skipped
  (965 `M2nc` and 2,595 `M3` skips are concentrated there). So every rate in the table is a
  rate for total length 6–11, and `M3`'s 58 % skip rate makes it the least trustworthy row.
  My stratified re-measure by total length (both corpora, per-length denominators) shows the
  trivial/unrestricted gap of §1.5 is **not** a length artefact:

**§1.7a — stratified re-measure, second corpus pair, independent seeds.** Rates are shown
per *total relator length*, with thickenable bases deliberately oversampled (the destroy rate
is conditional on a thickenable base, so its denominator is unaffected by how bases were
picked). Cap 2·10⁵.

| total length | M2nc destroy, trivial group | M2nc destroy, unrestricted | M3 destroy, trivial | M3 destroy, unrestricted | M3 create, trivial | M3 create, unrestricted |
|---|---|---|---|---|---|---|
| 7 | 0/16 = 0 % | 12/120 = 10.0 % | 2/16 = 12.5 % | 48/119 = 40.3 % | — | 7/120 = 5.8 % |
| 8 | 3/32 = 9.4 % | 28/120 = 23.3 % | 12/32 = 37.5 % | 67/107 = 62.6 % | **5/32 = 15.6 %** | **6/95 = 6.3 %** |
| 9 | 2/32 = 6.2 % | 20/119 = 16.8 % | 6/19 = 31.6 % | 5/10 = 50.0 % | 12/66 = 18.2 % | — |
| 10 | — | 43/99 = 43.4 % | — | — | 7/37 = 18.9 % | — |
| **all** | **5/80 = 6.2 %** | **103/458 = 22.5 %** | **20/74 = 27.0 %** | **120/236 = 50.8 %** | **24/136 = 17.6 %** | **13/215 = 6.0 %** |

`M2nc` create was **0** on both corpora (0/268 trivial, 0/487 unrestricted), as in S6.

At **every length where both corpora were measured**, the trivial-group AC3 destroy rate is
2–3× lower and the trivial-group AC2 create rate is ~2.5× higher. The gap is therefore not
the length artefact `contrast-length-confound.md` warns about. The honest limitation: the
`M3 create` comparison overlaps at total length 8 only, because the unrestricted run spent
its budget on shorter bases; the direction there (15.6 % vs 6.3 %) agrees with the
unstratified pair in §1.5 (19.2 % vs 4.8 %).

**Pooled over both runs** (independent seeds, same protocol, same band):

| rate | trivial group | unrestricted | S6 published |
|---|---|---|---|
| AC3 (non-cancelling) destroys, per thickenable base | **9/156 = 5.8 %** | 175/789 = 22.2 % | 24.0 % |
| AC2 destroys, per thickenable base | **28/133 = 21.1 %** | 236/481 = 49.1 % | 51.5 % |
| AC2 creates, per non-thickenable base | **58/313 = 18.5 %** | 30/568 = 5.3 % | 7.0 % |
| AC3 (cancelling) flips, either direction | **0/1,432** | 0/1,432 | 0/3,413 |

No p-values are quoted: the derived states of one base are not independent draws
(`contrast-length-confound.md`).

### 1.8 A one-step stabilization family S6 never measured

S6 §8's `[GAP-1STEP]` null covers `G2 = (r_1 z z, r_2, z)` and `Gc = (r_1 w z w^{-1}, r_2, z)`.
It does **not** cover *slides onto two different relators*, which the §8 table lists in the
same `m_z ≥ 3` row. That family is not uniformly destructive:

| base | `(r_1 z, r_2 z, z)` | `(r_1 z, r_2 Z, z)` | `(r_1 z z, r_2, z)` |
|---|---|---|---|
| `("xYY","xYx")` defect 0 | **0** (inert) | 2 | 2 |
| `("xyXY","xxy")` defect 0 | 2 | 2 | 2 |
| `("xy","xy")` defect 0 | **0** (inert) | 2 | 2 |

So the §8 table's "`m_z ≥ 3` ⇒ not inert" row is correct as "not *provably* inert" but is
read too strongly in the practical advice; and the `[GAP-1STEP]` null is narrower than §8
implies.

### 1.9 What S6 gets right and should keep

The classification's **structure** is sound and is the file's real contribution: AC1, cyclic
rotation, relator permutation, AC4/AC5, the first plain slide over a fresh stabilizer, and
S3 chord refinement are all provably inert; AC3 modulo (0) is the identity up to rotation;
so the predicate can only move under AC2 and under the choice of spelling. Nothing in this
audit touches that. What must not survive is (a) the conditional collapse to "AC2 only"
(§1.6) and (b) the rates as stated (§1.5).


---

## 2. S8 — splitting monotonicity

### 2.1 [GAP-S8-1] is DISCHARGEABLE — here is the missing bookkeeping

The bigon relator `u g^{-1}` (my own link builder, letters `u` then `G`) contributes exactly
two link edges — the corner `(u, G)` gives `u⁻—g⁻` and the wrap-around corner `(G, u)` gives
`g⁺—u⁺`. Measured over 322 random splits, the deltas are **constant**:

| quantity | delta under one split |
|---|---|
| `nA` (link edges = occurrences) | **+2** |
| `nC` (present germs) | **+2** |
| `L` (link components) | **0** |

`(dnA, dnC, dL) = (2, 2, 0)` in **322 of 322** splits, with no other triple occurring. So
`nA' − nC' = nA − nC` and `L' = L`, and the defect identity collapses to

```
defect(P') − defect(P)  =  nAC(P) − nAC(P')      for corresponding rotation systems.
```

That is the whole content of `[GAP-S8-1]`, and it is a standard fact, not an open one:
**contracting a non-loop edge of a graph embedded by a rotation system leaves the face
permutation's cycle count unchanged** (`V−1, E−1, F+0`, so `χ` and the genus of every
component are unchanged). Hence the contracted system has defect **equal**, not merely `≤`,
and `min` over `link(P)` `≤` `min` over `link(P')`, which is Conjecture S8.

**Compatibility survives the splice — the explicit check the sketch waves at.** Write the
bigon's two occurrences as `p` (letter `u`) and `q` (letter `g^{-1}`). In the dart model,
`2p` sits at `u⁺`, `2p+1` at `u⁻`, `2q` at `g⁻`, `2q+1` at `g⁺`; `A` pairs `(2p+1, 2q)` and
`(2q+1, 2p)`; `B` pairs `2p ↔ 2p+1` and `2q ↔ 2q+1`. The dart of the first contracted edge
at `g⁻` is `2q`, and of the second at `g⁺` is `2q+1`, and `B(2q+1) = 2q`; likewise
`B(2p) = 2p+1` on the `u` side. So the two splice positions are exactly `B`-mirror
positions. Given `C_{g⁻} = B·rev(C_{g⁺})` and `C_{u⁻} = B·rev(C_{u⁺})` before contraction,
the two merged orders satisfy the same relation afterwards. ∎

> **Repair R-G.** `[GAP-S8-1]` can be closed and Conjecture S8 promoted to a **theorem**,
> with the argument above written out (edge contraction preserves faces; the two splices are
> at `B`-mirror positions).

### 2.2 [GAP-S8-2] — the stated worry is vacuous

The gap says the argument "assumes the bigon's two link edges are not loops and that
`link(P')` stays connected". Neither assumption can fail:

* the two edges are `u⁻—g⁻` and `g⁺—u⁺` with `u ≠ g` fresh, so **neither is ever a loop**,
  and they are **vertex-disjoint**, so the two contractions cannot interfere;
* contracting an edge cannot change the number of connected components, so `L` cannot jump
  (measured: `dL = 0` in 322/322);
* the **degenerate split** — re-route *every* occurrence of `g` — leaves `deg(g⁺) = deg(g⁻) = 1`
  and the contractions become pendant-edge contractions, still `V−1, E−1, F+0`. It was
  included explicitly in every base of the hunt below and produced no anomaly.

### 2.3 The hunt: 379,364 split states, none below its base

Bases: AK(3); five AK(2)-class / worked S6 bases; **length-1 and length-2 relators**
(`("x","y")`, `("x","yy")`, `("xy","y")`, `("xx","yy")`, `("xy","xy")`); a
non-cyclically-reduced spelling (`("xyXY","yYxxy")`); then 28,877 trivial-group bases (random
AC walks from `("x","y")`) and 10,890 unrestricted bases. Every subset of `g`'s occurrences
was enumerated exhaustively when `g` occurs `≤ 4` times, and sampled plus the full re-route
otherwise.

| corpus | bases | split states measured | strictly below base |
|---|---|---|---|
| hand-picked (incl. AK(3), length-1/2 relators, unreduced spellings) | 13 | 282 | **0** |
| trivial-group (AC walks) | 28,877 | 237,036 | **0** |
| unrestricted | 10,890 | 142,046 | **0** |
| **total** | **39,780** | **379,364** | **0** |

That is ~600× S8's own 632 states, and it includes exactly the degenerate regimes
`[GAP-S8-2]` worried about.

**Verdict: AMEND — Conjecture S8 is CONFIRMED and should be upgraded to a theorem** via §2.1.

### 2.4 REFUTED: S8 §4's headline negative

S8 §4 states the S-line's headline negative as

> "**Adding generators is worth nothing as long as the added generators only re-describe the
> existing relators.**"

and trap T-S8 as "if the answer is 'none, it is the same words re-spelled', the proposal is
already refuted". **This is false**, and the counterexample is from this same session and
branch: `S4B_CUBIC_SEARCH.md`'s `C1` is reached from AK(3) by 7 chord refinements and 4 of
S4's `SPLIT`s — every one of them a *definitional* stabilization that only re-describes the
existing relators, with no relator content mixed — and

```
AK(3)  gamma_N = 2        C1 (rank 13, cubic triangular)  gamma_N = 1
```

so the re-describing moves strictly **lowered** `γ_N`. The reconciliation is that S8's
mechanism and S4's `SPLIT` are different moves — S8's definition relator is the **length-2
bigon** `u g^{-1}`, S4's is the **length-3** `t u v` — and the contraction argument of §2.1
uses the length-2 shape essentially (a length-3 definition relator contributes *three* link
edges, and contracting them is not a face-preserving operation in general).

> **Repair R-H.** Restrict S8 §4's headline and trap T-S8 to *bigon* splits. As stated they
> are contradicted by `C1`. The correct statement is: *a length-2 definitional split is
> monotone; a length-3 definitional split is not, and is the only known re-describing move
> that lowers `γ_N`.* This is the single most useful thing S8 could say to a search designer,
> and it currently says the opposite.

---

## 3. S4 — the cubic normal form

### 3.1 Theorem S4.1 (sign rigidity) — CONFIRMED

Brute force over **every** cyclically reduced length-3 word at `N = 2, 3, 4`: no word
contains both `x` and `x^{-1}` for any generator. 0 violations. The proof as written is
correct (all three position pairs of a length-3 cyclic word are cyclically adjacent).

### 3.2 Proposition S4.2 (no non-degenerate cubic triangular presentation of 1 below rank 4) — CONFIRMED

Independent enumeration (my own cyclic-word generator, my own Bareiss determinant):

| `N` | cyclically reduced length-3 cyclic words | cubic triangular presentations | `\|det\| = 1` |
|---|---|---|---|
| 2 | 12 | 20 | **0** |
| 3 | 46 | 1,816 | **0** |
| 4 | 120 | 264,208 | **43,008** |

Every count matches S4 §4a exactly. The cyclic-word counts are also confirmable in closed
form: the number of cyclically reduced length-3 words over `F_N` is `tr((J−P)^3)` on the
`2N` signed letters, i.e. `28, 126, 344` for `N = 2, 3, 4`, giving `12, 46, 120` rotation
classes.

**One convention discrepancy, worth a line in S4.** §4's protocol says "ordered tuples up to
rotation". The published counts are **not** ordered tuples — they are **multisets** of cyclic
words (presentations up to relator reordering). My ordered counts are 40 and 10,096 at
`N = 2, 3`; the multiset counts are 20 and 1,816, and Burnside reconciles them exactly
(`(10096 + 3·256 + 2·16)/6 = 1816`). Since `γ_N`, `|det|` and triviality are all invariant
under relator reordering this is the *right* quotient — but "ordered tuples" is the wrong
word for it.

> **Repair R-I.** §4: "ordered tuples up to rotation" → "multisets of cyclic words, i.e.
> presentations up to relator reordering".

### 3.3 The rank-4 headline census — CONFIRMED IN FULL, including the triviality test

The task asks whether the trivial-group test was applied to all 43,008 or sampled. I applied
**my own** Todd–Coxeter to **all 43,008**, cap 3,000 cosets:

| | count |
|---|---|
| certified trivial group (index 1) | **43,008** |
| non-trivial | **0** |
| undetermined at cap | **0** |
| defect histogram over all 43,008 | **`{0: 27,648, 2: 15,360}`** |
| defect histogram over the certified-trivial subset | **`{0: 27,648, 2: 15,360}`** (same set) |
| compatible census size | **16 for every one of the 43,008** |

So S4's `43 008 (all)` is not a number carried over from the `|det| = 1` column: at rank 4,
`|det| = 1` really does imply the trivial group for this family, and the 64.29 % / 35.71 %
split is exactly reproduced. "Non-degenerate" means the same thing in the enumeration as in
Thm S4.1/S4.2 (every relator cyclically reduced) — my enumeration used that definition and
got S4's numbers.

The `|det|` spectrum at `N = 4` (new, not in S4): `{0: 49,024, 1: 43,008, 2: 30,720,
3: 32,768, 4: 3,072, 5: 18,432, …}`.

### 3.4 Lemma S4.4 (`SPLIT`) — CONFIRMED, with two scope notes

The algebra is correct: `D R'^{-1} = (t u v)(λ u v)^{-1} = t λ^{-1}` freely, and
`(α (tλ^{-1}) α^{-1})·(α λ β) = α t β`. Freshness of `t` does preserve free **and** cyclic
reducedness in every position of a length-3 relator (checked case by case: `λ b c`, `a b λ`,
`λ b λ`). Two things the statement should say and does not:

1. `t λ^{-1} = D R'^{-1}` is a product of **two** relators, so step 4 is two AC2's (the note
   says "AC3+AC2 (twice)" only parenthetically) and the **intermediate states leave the
   triangular world** — "every relator still has length exactly 3" holds at the endpoint,
   not along the way.
2. `SPLIT` is *not* S8's split. §2.4 above: S8's monotonicity does not apply to it, and
   `S4B`'s `C1` shows `SPLIT` can lower `γ_N`. S4 and S8 must cross-reference each other on
   this, or a future session will apply S8's "never decreases" to S4's move.

### 3.5 One stale claim

S4 §0 item 6 and §6 say "**No cubic form of AK(3) is reported**". `S4B_CUBIC_SEARCH.md`
(same session) reports two, `C1` and `C2`, at rank 13. S4 is not wrong — it is superseded —
but as written it is the first thing a fresh session reads about the route.

> **Repair R-J.** Add a one-line pointer from S4 §0/§6 to `S4B`.

---

## 4. Independent re-verification of two claims the audit leans on

Both were re-computed with my own census and my own Todd–Coxeter, from the words as printed:

| claim | source | my measurement |
|---|---|---|
| `C1` is a rank-13 cubic triangular presentation of 1 with `γ_N = 1` | `S4B` §0 | census **8,192**, defect **2** ⇒ `γ_N = 1`, histogram `{2:2, 4:60, 6:510, 8:2338, 10:3766, 12:1516}`, Todd–Coxeter index **1** — **confirmed** |
| AK(3) has `γ_N = 2` | S3, R1F | defect 4 ⇒ `γ_N = 2` — confirmed |
| Conjecture SR is false on the trivial group | `S11` §4.3′, `S13` §3c | `("ABbbabAAaB","baB")` census 86,400 defect **0**; `("AbabAAaB","baB")` census 2,880 defect **2**; `("AbabAB","baB")` census 144 defect **0**; **all three Todd–Coxeter index 1** — **confirmed**, one free-reduction step takes defect 0 to defect 2 on presentations of the trivial group |

The third row is what kills S6 §8's conditional collapse (§1.6).

---

## 5. Summary of repairs for the orchestrator

| id | file | repair |
|---|---|---|
| **R-A** | S6 §3 | strengthen T4′ to a dart-level bijection claim (histogram evidence, 144/144) |
| **R-B** | S6 §3 | add hypotheses `\|r_1\| ≥ 1` and "`z` occurs in no `r_i`" to T4′ |
| **R-C** | S6 §1, §7, §8 | merge/label the `M0` row: it is the `M2nc` row re-partitioned, not a second census; §8's "73 + 315 events" double-counts |
| **R-D** | S6 §7 | account for the 14 missing `M3` pairs; state the `M3` exclusion rule |
| **R-E** | S6 §1, §5, §7, §8, T-S8 | label every published rate "unrestricted corpus"; add the trivial-group rates of §1.5/§1.7a; T-S8's "24 %" → "≈ 6 % on trivial-group bases, ≈ 22 % unrestricted" |
| **R-F** | S6 §4, §8, §9 | **Conjecture SR is FALSE (`S11`)**; withdraw "stable ACC becomes a statement purely about AC2"; note that S6's 997-pair null is depth-1 and therefore structurally blind to SR |
| **R-F′** | S6 §0.3 | stop citing S3's trap T-S6 — S3 §5 R5 retracted it. Separately, **S3 §3 lines 121–130 still assert the retracted claim** and should be repaired in the audited file |
| **R-G** | S8 §3 | close `[GAP-S8-1]` with the contraction bookkeeping of §2.1 and promote Conjecture S8 to a theorem |
| **R-G′** | S8 §3 | `[GAP-S8-2]` is vacuous: the bigon edges are never loops, are vertex-disjoint, and contraction preserves components |
| **R-H** | S8 §4, T-S8 | **restrict the headline negative to bigon (length-2) splits** — `S4B`'s `C1` refutes it for length-3 definitional splits |
| **R-I** | S4 §4 | "ordered tuples up to rotation" → "multisets of cyclic words" |
| **R-J** | S4 §0.6, §6 | point to `S4B`: AK(3) *does* have a cubic triangular form (rank 13) |

## 6. The single most serious problem found

**S6 §8's headline — "stable ACC becomes a statement purely about AC2" — rests on a
conjecture that this same session refuted, and S6's own evidence for that conjecture is
structurally incapable of testing it.** Conjecture SR was refuted in `S11` (task A10) with 28
counterexamples, one family on balanced presentations of the trivial group at Todd–Coxeter
index 1; I re-verified the chain independently (§4). S6's supporting null — "0 of 997
thickenable spellings" — is a *depth-1* corpus ("cyclically reduced base plus one move"), and
SR first fails at depth 2, so those 997 measurements could not have found a counterexample at
any sample size. Reading them as evidence is the same error the line already filed under
`calibrate-one-sided-hunts-on-a-positive-ladder.md`: a one-sided null is worth exactly its
measured detection rate, and here the detection rate for the thing being hunted is **zero by
construction**.

Second most serious, and the one with the most downstream cost: **the flip rates are rates
over arbitrary balanced rank-2 presentations, and every one of them moves substantially —
some by a factor of 3 or 4, and AC2's create rate in the *opposite* direction to the note's
narrative — once the corpus is restricted to the trivial group, which is the only corpus the
AC programme can use** (§1.5, §1.7a).

## 7. Artefacts

Scratch, not committed: `aud.py` (independent link/census/defect), `tc.py` (independent HLT
Todd–Coxeter), `t4p.py` (T1/T2/T4/T4′ structural tests), `flip.py` + `flip2.py` (trivial-group
vs unrestricted flip tables, unstratified and length-stratified), `s8.py` (splitting hunt +
bookkeeping deltas), `s4.py` (cubic census + determinant scan + triviality on all 43,008).
Every number in this file is reproducible from those six scripts with
`PYTHONPATH=/home/user/ACSolverX`.
