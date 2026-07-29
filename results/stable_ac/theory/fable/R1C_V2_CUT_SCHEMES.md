# R1c-v2 — Synchronized planarity for NON-3-connected supports, at arbitrary rank

**Status: AUDITED (29-07-2026, ~10:20 UTC) — hostile referee verdict REPAIRABLE with zero
mathematical errors; the four presentational repairs are recorded as normative errata
below and OVERRIDE the body where they touch it.** The referee (independent fable agent,
own implementations, none of the author's code): Lemma 3.2 survived 35 two-connected
instances incl. 10 nested-bridge constructions (0 violations; 182 violations on
non-2-connected controls — the trap is real and correctly scoped); Kreweras/(5.1)
independently REPROVED on 34 vectors to t = 5, N = 9; Lemma 7.4 probed with
shift-census-uniformity tests (exactly ∏m! per shift value — no under-count); Thm 6.S
verified on untested configurations incl. one-pole-cut blocks (no shift, as claimed);
decomposition-order independence on 425 graphs × 5 strategies (0 discrepancies);
compatibility layer completeness on all 1,152 (rotation, generator) pairs of a test link +
both recorded false-negative witnesses end-to-end; master formula on 425 random connected
planar multigraphs (218 with cut vertices, 35 with t ≥ 3, 263 with nested split depth ≥ 2):
0 mismatches; K₅/K₃,₃ correctly 0 via non-planar R-nodes.

## NORMATIVE ERRATA (the four required repairs)

E1 (Lemma 3.2 proof): after the Jordan curve J is formed, add — "the two angular sectors
at a bounded by e(d₁), e(d₂) lie in DIFFERENT components of S² ∖ J, since J = ∂Ω = ∂Ω′
and J has exactly two branches at a"; and note that |D_i^a| ≤ 1 is trivially an interval.
E2 ((6.1) and Thm 6.S case 1): the P-node factor list and the parameter c are pinned to
the CANONICAL decomposition — c = number of components of B − {u,v} inside the block B of
G containing the class; only the VALUE of the product, not the factor multiset, is
decomposition-independent.
E3 (§8.3): the simple-degree-2 dichotomy is scoping prose only and is not exhaustive as
worded (P-node poles like c, d of K₄−e fall in neither case); nothing downstream depends
on it.
E4 (Lemma 7.4): the "bijection by induction" sketch is completed by the anchor-consumption
bookkeeping: the anchor at the reference pole consumes exactly one rotation-offset factor
per cut vertex, leaving precisely the net class multiplicity of Theorem 6.S (referee
reconstructed and verified this bookkeeping).

**Contract.** This is the "cut-scheme extension" promised in the R1c-v2 sketch at the end of
`R1C_RANK_N_THREECONNECTED.md`: decide compatible sphericity (hence, via the Neuwirth
bridge, orientable thickenability) for connected loopless Neuwirth links at arbitrary rank
whose **simple support is planar but not 3-connected**. It subsumes R1c (Theorem R is
recovered as Corollary 6.R), the codex `K₄`, `K₄−e`, `C₄`, `P₄` and paw-core theorems
(§9), and it closes the gate that stopped 100 % of the round-1 rank-3 harvest.

**Empirical driver.** In the round-1 direct stable-move harvest (`rank3_harvest_round1.jsonl`,
3,104 distinct states) the R1c gate histogram is

| gate | states |
|---|---:|
| `relator shorter than 3` | 1,032 |
| `simple degree < 3` | 1,444 |
| `2-cut in S (not 3-connected)` | 628 |
| **in scope for R1c (3-connected planar)** | **0** |

Every one of the 628 two-cut states carries the *same* cut, `(H2) fails: 2-cut {0, 2}` =
`{x⁺, y⁺}` (germ indices `0=x⁺,1=x⁻,2=y⁺,3=y⁻,4=z⁺,5=z⁻`). Of the states that possess a
non-degenerate support, 1,853 are 2-connected, 199 have a cut vertex with two blocks, and
**20 have a cut vertex with three blocks** — i.e. the paw-note trap ("the interval lemma is
FALSE for ≥ 3 components at a cut vertex") is not hypothetical here. It is handled in §5,
not excluded.

---

## 1. Setting, notation, inherited hypotheses

Fix `P = ⟨g₁,…,g_n | w₁,…,w_r⟩`, every `w_j` a nonempty cyclic word, cyclically reduced,
every generator occurring. Retain **verbatim** the occurrence dictionary `(D, A, B, ν)` of
`lit_AK3_NEUWIRTH.md` / `R1C_RANK_N_THREECONNECTED.md`:

* `D` = the `2·Σ|w_j|` endpoint symbols `d_i, h_i`; `B = ∏_i (d_i h_i)`; `A` = the corner
  involution; `V` = the `2n` germs `g_k^±`; `τ` = the germ-swap; `ν : D → V`, `ν(Bd) = τν(d)`.
* `G := G_A` — the **link multigraph** on `V`: one labelled edge per `A`-orbit.
  `P_uv` = the parallel class, `m_uv = |P_uv|`. `S` = the **simple support**.
  `D_v = ν^{-1}(v)`, `n_v = |D_v| = deg_G(v)`, and `n_v = n_{τv}` (2.0).
* A **compatible rotation** `C` is one cyclic order `C_v` per germ with

  ```
  C_{τv} = B C_v^{-1} B.                                        (2.1)
  ```

* A rotation system `ρ` of `G` is **spherical** iff its rotation surface `Σ_ρ` is `S²`;
  for connected `G` this is `|C| − |A| + |AC| = 2` (Euler dictionary, Lemma 1 of
  `lit_AK3_NEUWIRTH.md`). Write `N(G)` for the number of labelled spherical rotation
  systems of `G`, ignoring (2.1).

**Standing hypotheses of R1c-v2.**

```
(H1)  G is connected.
(H2') no hypothesis on the connectivity of S beyond (H1).      [ this replaces R1c's (H2) ]
(H3)  S is planar.
(H4)  G is loopless  (guaranteed by cyclic reduction: an A-loop needs a_{i+1} = a_i^{-1}).
(H5)  2n ≥ 4, i.e. n ≥ 2.
```

`(H5)` is used only in §7.3 (rank normalisation); with `n = 1`, `G` is a single dipole and
the *count* theorems still hold but the scheme normalisation degenerates.

**Scope note (inherited, [R4]).** Everything in §§2–7 is a pure rotation-system statement and
needs no balance. The bridge "γ_N = 0 ⟺ orientably thickenable" is proved in
`lit_AK3_NEUWIRTH.md` Thm 2 for **balanced** presentations with **connected** link; use it
only there.

**Numbering convention.** Displayed equations `(2.0)`, `(2.1)`, `(4.1)`, `(4.3)` are the
codex's, cited by their original numbers. All other displayed numbers — `(3.1)`, `(3.2)`,
`(5.1)`, `(5.2)`, `(6.1)`, `(7.1)`–`(7.3)` — are new to this note; where a codex equation has
a clashing number it is written "codex `(x.y)`".

**Two imported classical facts** (not reproved here; flagged for the referee in §11):

* **(W) Whitney.** A 3-connected planar *simple* graph has exactly two spherical rotation
  systems, mutually vertex-wise reversed. (Mohar–Thomassen form; already imported by R1c.)
* **(K) Kreweras 1972.** The number of non-crossing partitions of an `N`-element cyclically
  ordered set into `t` *labelled* parts of prescribed sizes `d₁,…,d_t` is `N!/(N−t+1)!`.
  (Kreweras' unlabelled statement `n!/((n−k+1)! ∏_j r_j!)` times `∏_j r_j!`.)
  Numerically re-verified for all size vectors used here, §10.2.

---

## 2. Two structural preliminaries

### Lemma 2.1 (subembedding)

Let `ρ` be a spherical rotation system of a connected graph `G`, and let `G′ ⊆ G` be a
connected subgraph. Then `ρ|_{G′}` (restrict each cyclic order to the darts of `G′`) is a
spherical rotation system of `G′`.

*Proof.* `ρ` realises `G` cellularly in `S²`. Deleting edges and isolated vertices leaves
`G′` embedded in `S²` with the restricted rotations. A connected graph embedded in `S²` has
all complementary regions open discs, so the embedding is cellular and the rotation surface
of `ρ|_{G′}` is `S²`. ∎

> **Trap.** Lemma 2.1 is *false* for disconnected `G′` in the sense needed later: the
> rotation surface of a disconnected ribbon graph caps components separately and forgets
> their relative nesting. Every use below restricts to a **connected** subgraph.

### Lemma 2.2 (digon bijection — imported [R1])

Let `u ≠ v` and let the `m ≥ 1` parallel `uv`-edges be embedded in `S²`. The complement has
exactly `m` regions; every region is a digon whose closure contains exactly one angular gap
at `u` and one at `v`; regions and gaps are in bijection; and the cyclic order of the darts
at `v` is the reverse of the cyclic order at `u`.

*Proof.* Verbatim [R1] of `R1C_RANK_N_THREECONNECTED.md`: Euler gives `m` faces with `2m`
edge-sides, all boundary walks alternate `u,v` hence have `≥ 2` sides, so each face has
exactly 2; a face bordered twice by one edge would make that edge a bridge, impossible for
`m ≥ 2`, and trivial for `m = 1`. Reading the digon boundaries gives the reversal. ∎

---

## 3. Bridge decomposition at a 2-cut (part (a))

Throughout §3, `H` is a **2-connected** loopless multigraph (this is where the block
decomposition of §5 must have been performed first — see the trap box at the end of §3).

**Definition 3.1 (split pair, bridges).** `{a,b} ⊆ V(H)`, `a ≠ b`. The `{a,b}`-**bridges**
are

* one **trivial bridge** per edge of `P_ab` (there are `m := m_ab` of them), and
* one **nontrivial bridge** per connected component `C` of `H − {a,b}`: the subgraph induced
  by `C` together with all edges joining `C` to `a` or to `b` (and the vertices `a,b`).
  There are `c` of them.

Put `k := m + c`. `{a,b}` is a **split pair** iff `k ≥ 2`. Because `H` is 2-connected, every
component `C` has a neighbour at `a` and a neighbour at `b`; hence every nontrivial bridge
contains an `a–b` path with interior in `C`, and `|E(B_i)| ≥ 2`. A nontrivial bridge
contains **no** `ab`-edge (those are trivial bridges by definition).

For a bridge `B_i` write `B_i⁺ := B_i + e_i` where `e_i` is a new **virtual** `ab`-edge.

### Lemma 3.2 (bridge intervals — generalises Lemma 5.1 of `lit_AK3_SYNCHRONIZED_PLANARITY.md`)

Let `ρ` be a spherical rotation system of `H` and `{a,b}` a split pair with `k ≥ 2` bridges.
Then for every `i`, the darts of `B_i` at `a` form one cyclic interval of `ρ_a`, and likewise
at `b`.

*Proof.* Trivial bridges have exactly one dart at `a`; nothing to prove. Let `B_i` be
nontrivial with component `C_i`, and let `d₁, d₂` be two darts of `B_i` at `a` that are
**consecutive** in the induced cyclic order of `D_i^a` (the `B_i`-darts at `a`); let `γ` be
the open arc of `ρ_a` strictly between them containing no `B_i`-dart. Since `B_i` has no
`ab`-edge, the heads of `d₁,d₂` lie in `C_i`; `C_i` is connected, so choose a simple path
`P ⊆ C_i` between those heads (possibly a single vertex). Then

```
J := d₁ ∪ P ∪ d₂
```

is a Jordan curve through `a` whose vertex set is `{a} ∪ V(P) ⊆ {a} ∪ C_i`; in particular
`b ∉ J`. `J` splits `S²` into open discs `Ω` (meeting the gap `γ`) and `Ω′`.

Let `B_j`, `j ≠ i`, have a dart in `γ`. As vertex sets `B_j ∩ B_i = {a,b}`, and `b ∉ J`, so
`B_j ∩ J ⊆ {a}`. `B_j − a` is connected (for a trivial bridge it is the vertex `b` with half
an edge; for a nontrivial bridge it is `C_j ∪ {b}` plus the `C_j`–`b` edges, connected
because `H` is 2-connected) and it is disjoint from `J`, hence contained in one component of
`S² ∖ J`; its dart into `γ` puts it in `Ω`. Therefore **`b ∈ Ω`**.

Now suppose `D_i^a` is *not* a cyclic interval. Then at least two distinct gaps of `D_i^a`
contain non-`B_i` darts. Choose `d₁,d₂` bounding one such gap `γ ⊆ Ω`, and let `γ′` be
another occupied gap; because `d₁,d₂` are consecutive in `D_i^a`, `γ′` lies in the
complementary arc, hence in `Ω′`. Applying the previous paragraph to a bridge with a dart in
`γ` gives `b ∈ Ω`, and to a bridge with a dart in `γ′` gives `b ∈ Ω′`. Contradiction. Hence
`D_i^a` is a cyclic interval; the argument at `b` is symmetric. ∎

> **Where the hypothesis bites.** The proof uses "**every** bridge contains `b`" twice. That
> is exactly what fails at a cut vertex, and exactly why the block decomposition must be
> done *before* any 2-cut analysis. See §5 and the trap box below.

### Lemma 3.3 (bridge order reverses)

Under the hypotheses of Lemma 3.2, let `σ_a` be the cyclic order of the `k` bridges at `a`
(well defined by Lemma 3.2) and `σ_b` the one at `b`. Then `σ_b = rev σ_a`.

*Proof.* In each bridge choose one `a–b` path `π_i` (the edge itself for a trivial bridge; a
path through `C_i` for a nontrivial one). Delete from `H` every vertex and edge not on
`⋃_i π_i`. The result `H′ = ⋃π_i` is connected and, by Lemma 2.1, spherical with the
restricted rotations. Since each `π_i` keeps exactly one dart inside the interval `D_i^a`,
the cyclic order of those `k` surviving darts at `a` is `σ_a`, and at `b` it is `σ_b`.
Suppressing the internal degree-2 vertices of the `π_i` (a homeomorphism of the embedding)
turns `H′` into the dipole with `k` parallel `ab`-edges. By Lemma 2.2 its dart order at `b`
is the reverse of the one at `a`. ∎

### Lemma 3.4 (poles are cofacial in a bridge)

Under the hypotheses of Lemma 3.2, in the induced spherical embedding of a single bridge
`B_i` the poles `a` and `b` lie on a common face; consequently `ρ` induces a well-defined
spherical rotation system `ρ_i` of `B_i⁺` (place the virtual dart at `a` in the unique gap of
`D_i^a` occupied by the other bridges, likewise at `b`).

*Proof.* Pick `j ≠ i` and an `a–b` path `π_j ⊆ B_j`. Its interior is disjoint from `B_i`
and connected, hence lies inside one face `F` of the embedding of `B_i`; its endpoints `a,b`
are on `∂F`. Draw the virtual edge inside `F`. By Lemma 3.2 all non-`B_i` darts at `a` lie
in one gap of `D_i^a`, which is the gap of `F`; so the virtual dart's position is forced and
`ρ_i` is well defined. `B_i⁺` is connected and embedded in `S²`, hence spherical. ∎

**Remark 3.4a (`B_i⁺` is 2-connected; the virtual edge is not a bridge).** For a trivial
bridge, `B_i⁺` is the 2-edge dipole. For a nontrivial bridge, suppose `v` were a cut vertex of
`B_i⁺`. `v ∉ {a,b}` (deleting `a` leaves `C_i ∪ {b}` plus the `C_i`–`b` edges, connected;
symmetrically for `b`), so `v ∈ C_i` and some `X ⊆ C_i` is separated from `{a,b}` in
`B_i⁺ − v`. Since every path from `X` to the rest of `H` runs through `C_i ∪ {a,b}`, `X` is
then separated in `H − v` as well, contradicting 2-connectivity of `H`. Hence `B_i⁺` is
2-connected, `e_i` lies on two distinct faces, and deleting `e_i` from an embedding of `B_i⁺`
merges them into a single face carrying both `a` and `b` on its boundary — which is what
Theorem 3.5's converse uses.

### Theorem 3.5 (P-node composition — the exact analogue of codex (5.1))

Let `H` be 2-connected loopless, `{a,b}` a split pair with bridges `B₁,…,B_k`, `k ≥ 2`. The
map

```
ρ  ⟼  ( ρ₁, …, ρ_k ; σ_a )
```

of Lemmas 3.2–3.4 is a **bijection** from the spherical rotation systems of `H` onto

```
{ spherical rotation systems of B₁⁺ } × … × { … of B_k⁺ }  ×  { cyclic orders of {1,…,k} }.
```

Consequently

```
N(H) = (k − 1)! · ∏_{i=1}^{k} N(B_i⁺).                                   (3.1)
```

*Proof.* *Well defined and injective.* Given `ρ`, Lemma 3.4 produces each `ρ_i` and Lemma
3.2 produces `σ_a`. Conversely `ρ_a` is recovered from `σ_a` by replacing bridge `i` by the
linear order obtained from `ρ_i` at `a` by deleting the virtual dart (this is a linear, not
merely cyclic, datum precisely because the virtual dart supplies the cut); `ρ_b` likewise,
using `σ_b = rev σ_a` (Lemma 3.3); at any other vertex `v` (which lies in exactly one `C_i`)
`ρ_v = ρ_{i,v}`. So `ρ` is determined.

*Surjective.* Given `(ρ_i)_i` and any cyclic order `σ` of `{1,…,k}`: embed the `k`-edge
dipole in `S²` with order `σ` at `a` and `rev σ` at `b` (possible by Lemma 2.2). Thicken
each dipole edge to a closed strip; the `k` strips are pairwise disjoint. Embed `B_i⁺` in
`S²` with rotation `ρ_i`, cut along the virtual edge and along small discs at `a,b`: this
yields `B_i` drawn in a closed disc with `a,b` on its boundary circle and the `a`-darts (resp.
`b`-darts) leaving in the prescribed linear order. Paste that disc into the `i`-th strip.
The result is an embedding of `H` in `S²` realising `(ρ_i)_i` and `σ`. It is connected, so
its rotation system is spherical. ∎

**The cut parameter, explicitly.** Fix an origin bridge (any nontrivial one if `c ≥ 1`). A
cyclic order of `k = m + c` labelled items is equivalent to

```
( a cyclic order of the c nontrivial bridges )                     (c − 1)!  choices
× ( a composition m = i₁ + … + i_c , i_j ≥ 0 )                     C(m+c−1, c−1) choices
× ( a linear order L = (e₁,…,e_m) of the labelled central edges )  m!  choices
```

— the `j`-th arc between consecutive nontrivial bridges receives the next `i_j` entries of
`L` — and `(c−1)!·C(m+c−1,c−1)·m! = (m+c−1)! = (k−1)!`. For `c = 2` this is precisely
codex `(5.1)`: origin `𝖢`, then `L[:i]`, then `𝖣`, then `L[i:]`, with `i ∈ {0,…,m}`, giving
`(m+1)!`. **The linear order `L` is never enumerated**: it is carried by the all-different
ranks `z_e ∈ {0,…,m−1}` of (4.1). What *is* enumerated is the *shape*

```
  shape(P-node) :=  (c−1)! · C(m+c−1, c−1)  =  (m+c−1)! / m!  =  (m+1)(m+2)⋯(m+c−1).   (3.2)
```

For `c = 1` this equals **1** — a parallel class with only one nontrivial bridge carries *no*
enumerated parameter at all, only ranks. This is why `K₄` and `C₄` need a single scheme.

### The shift question at a 2-cut, answered

> **No free `Z/m` shift ever appears at a split pair of a 2-connected graph.**

By Lemma 3.3 the bridge order at `b` is *the* reverse cyclic order of the labelled bridge
order at `a` — a cyclic order of pairwise distinguishable items has no rotational freedom
once the items are labelled. Concretely, expanding (3.2) at the two poles:

```
at a :   B_{π(1)},  L[0:i₁],  B_{π(2)},  L[i₁:i₁+i₂],  … , B_{π(c)},  L[…:m]
at b :   B_{π(1)},  rev L[…:m],  B_{π(c)}, … ,  B_{π(2)},  rev L[0:i₁]
```

(arcs in reversed order, each arc internally reversed). For `c = 2` this is literally the
`K₄−e` display `P_ac, L[:i], P_ad, L[i:]` / `P_bc, rev(L[i:]), P_bd, rev(L[:i])`.

The `P₄`-style shift is a **cut-vertex** phenomenon, not a 2-cut phenomenon (Theorem 6.S
makes this exact). The trap is:

> **TRAP 1 (the P₄ lesson, restated as a scoping rule).** If `{a,b}` merely disconnects the
> *simple support* `S`, `{a,b}` need not be a split pair of a single **block**: a piece may
> hang off `a` alone. Lemmas 3.2/3.3 then FAIL, and imposing "order at `b` = reverse of order
> at `a`" produces **false negatives** — exactly the `m−1` lost shifts of `P₄`. The recorded
> counterexamples to the naive rule are `⟨x,y | xY, yy⟩` (central multiplicity 2, spherical
> only in the omitted shift) and `⟨x,y | xxx, xxy⟩` (central multiplicity 4)
> (`lit_AK3_P4_SYNCHRONIZED_PLANARITY.md` §5). **Rule: block-decompose first (§5), then
> split-pair-decompose inside each block (§3).** Never the other way round.

---

## 4. Base cases

### 4.1 Dipole (P-leaf)

`H` = two vertices, `m` parallel edges. By Lemma 2.2, `ρ_b` is forced by `ρ_a`, so
`N = (m−1)!`. (Consistent with (3.1): `k = m`, `c = 0`, every `B_i⁺` a 2-edge dipole with
`N = 1`.)

### 4.2 Cycle (S-node)

`H` = a simple cycle of length `≥ 3`. Every vertex has degree 2, so its cyclic order is
unique: `N = 1`, **no parameter**. (Equivalently the recursion of §6 splits a cycle at
`k = 2` split pairs, each contributing `(2−1)! = 1`, down to triangles.)

### 4.3 Three-connected skeleton (R-node) — Theorem R

`H` = a simple 3-connected graph on `≥ 4` vertices. If `H` is non-planar, `N = 0`. If planar,
`N = 2` by **(W)**, and the two systems are mutual reversals; since `min deg ≥ 3` no rotation
equals its own reversal, so the two are distinct. This is the `m_uv ≡ 1` case of Theorem R of
`R1C_RANK_N_THREECONNECTED.md`; the general Theorem R (`2·∏ m_uv!`) is recovered in §6.1.

---

## 5. Cut vertices — the ≥ 3-component case done correctly (part (a), continued)

Now let `G` be connected, loopless, with cut vertex `a`. Let `Q₁,…,Q_t` be the components of
`G − a` and let `B_i := Q_i ∪ {a} ∪ (edges from a to Q_i)` be the **branches** at `a`
(`t ≥ 2`). Put `d_i := deg_{B_i}(a)`, `N_a := Σ d_i = deg_G(a)`, and let `D_i^a` be the
corresponding dart sets.

**Remark 5.0 (branches vs. blocks).** Each branch `B_i` contains exactly one block incident
with `a` — if it contained two, `a` would separate them inside `B_i`, contradicting
connectedness of `B_i − a = Q_i` — and that block carries *all* of `D_i^a`. So branches and
blocks-at-`a` induce the **same** partition of `D_a` and the same numbers `d_i`; §5 is stated
for branches (whose defining property `B_i − a` connected is what the proofs use) and the
counts may be read off blocks. All statements are the "blocks at a cut vertex" statements.

### Lemma 5.1 (pairwise non-crossing — necessity)

If `ρ` is spherical, then for `i ≠ j` the dart sets `D_i^a` and `D_j^a` do **not** interleave
in `ρ_a`: there are no `d₁, d₂ ∈ D_i^a` and `e₁, e₂ ∈ D_j^a` in cyclic order `d₁ e₁ d₂ e₂`.

*Proof.* `B_i − a = Q_i` is connected. Take a simple path `P ⊆ Q_i` between the heads of
`d₁,d₂`; `J := d₁ ∪ P ∪ d₂` is a Jordan curve through `a`. `e₁,e₂` leave `a` into opposite
components of `S² ∖ J`. `B_j − a = Q_j` is connected and meets `B_i` only at `a` (distinct
components of `G − a`), so it is disjoint from `J`; but it contains the heads of `e₁` and
`e₂`. Contradiction. ∎

> **TRAP 2 (the paw trap, made precise and then defused).** Lemma 5.1 is *strictly weaker*
> than "each `D_i^a` is a cyclic interval". For `t = 2` the two are equivalent (in a cyclic
> order, a set is an interval iff its complement is), which is exactly the cut-vertex block
> lemma (Lemma 2.1) of `lit_AK3_PAW_ONE_LOOP_PLANARITY.md`. For `t ≥ 3` the interval statement is **FALSE**.
> Minimal witness: `a` joined to `u` by two parallel edges and to leaves `v, w` by one edge
> each. The rotation `ρ_a = (au₁, av, au₂, aw)` is spherical (put `v` in one face of the
> `au`-dipole and `w` in the other) yet `D_{dipole}^a = {au₁, au₂}` is not an interval.
> Brute force: 6 spherical systems, of which **2** have a non-interval block (§10.1).
> R1c-v2 does **not** exclude this case; it replaces the interval lemma by Lemma 5.1 +
> Theorem 5.3. In the round-1 harvest, 20 states need this.

### Lemma 5.2 (a non-crossing partition of a cycle has an interval part)

Let `π = {π₁,…,π_t}` be a non-crossing partition of a finite cyclically ordered set. Then some
part `π_j` is a cyclic interval.

*Proof.* Induction on `t`. `t = 1` is trivial. Pick any part `π_{i₀}`. If it is an interval we
are done. Otherwise `π_{i₀}` has `≥ 2` occupied gaps; pick one, `γ`, and let `T_γ` be the set
of parts meeting `γ`. By non-crossing, each part meeting `γ` lies *inside* `γ`; `i₀ ∉ T_γ`, and
any part inside another occupied gap is not in `T_γ`, so `1 ≤ |T_γ| < t`. The restriction of
`π` to the arc `γ` is a non-crossing partition of that (linearly, hence cyclically, ordered)
set with `|T_γ|` parts; by induction one of them is an interval of `γ`, and an interval of an
arc containing no other part is an interval of the whole cycle. ∎

### Lemma 5.2a (merge sufficiency at one cut vertex)

Let `G` be connected with cut vertex `a` and branches `B₁,…,B_t`. Let `ρ` be a rotation system
of `G` such that each `ρ|_{B_i}` is spherical and the partition `{D_i^a}` is non-crossing in
`ρ_a`. Then `ρ` is spherical.

*Proof.* Induction on `t`; `t = 1` is the hypothesis. For `t ≥ 2`, Lemma 5.2 gives a branch
`B_j` with `D_j^a` a cyclic interval. `G′ := ⋃_{i≠j} B_i` is connected, has `t−1` branches at
`a`, and `ρ|_{G′}` satisfies the same hypotheses (restrictions of spherical systems are
spherical, Lemma 2.1; restrictions of non-crossing partitions are non-crossing), so by
induction `ρ|_{G′}` is spherical: embed `G′` in `S²`. Deleting the interval `D_j^a` from `ρ_a`
leaves a distinguished angular gap of `ρ_a|_{G′}`, i.e. a face `F` of `G′` incident with `a`.
`B_j` is spherical and connected, hence realisable in a closed disc with `a` on the boundary
circle and the prescribed linear order of `D_j^a` leaving `a`; paste that disc into `F`. The
result embeds `G` in `S²` realising `ρ`, and `G` is connected, so `ρ` is spherical. ∎

### Theorem 5.3 (cut-vertex composition, structure, and count)

**(a) Structure.** A rotation system `ρ` of a connected loopless `G` is spherical **iff**
(i) `ρ|_B` is spherical for every block `B` of `G`, and (ii) at every cut vertex `a` the
partition of `D_a` into branch dart-sets is non-crossing in `ρ_a`.

**(b) Count at one cut vertex.** Given the cyclic orders `ρ|_{D_i^a}`, the number of cyclic
orders of `⊔_i D_i^a` restricting to them and satisfying (ii) depends only on `(d₁,…,d_t)`:

```
A(d₁,…,d_t)  =  ( ∏_i d_i ) · (N−1)! / (N−t+1)! ,        N = Σ d_i.            (5.1)
```

**(c) Global count.**

```
N(G)  =  ∏_{blocks B} N(B)  ·  ∏_{cut vertices a} A( d₁(a),…,d_{t(a)}(a) ).      (5.2)
```

*Proof of (b), i.e. of (5.1).* Fix a dart `δ₀ ∈ D₁^a`. A cyclic order on the `N`-element dart
set is the same as a bijection `Z/N → darts` up to rotation of `Z/N`; normalise by `δ₀ ↦ 0`.
The datum splits as (i) the partition of `Z/N` induced by the branches — a **non-crossing**
partition
(Lemma 5.1) into labelled parts of sizes `d₁,…,d_t` with `0` in part 1 — and (ii) for each
`i` a bijection part-`i` → `D_i^a` respecting the prescribed cyclic order, i.e. `d_i` rotations
for `i ≥ 2` and exactly one for `i = 1` (pinned by `δ₀`). By **(K)** the number of labelled
non-crossing partitions is `M = N!/(N−t+1)!`; the family is invariant under rotating the
ground cycle, so the number with `0` in part 1 is `M·d₁/N`. Hence

```
A = (∏_{i≥2} d_i) · (d₁/N) · N!/(N−t+1)! = (∏_i d_i)·(N−1)!/(N−t+1)!.  ∎
```

Special cases used constantly below: `A(d₁,d₂) = d₁d₂`; `A(1,…,1) = (t−1)!`;
`A(d₁,d₂,d₃) = d₁d₂d₃·(N−1)`.

*Proof of (a).* (⇒) Blocks are connected subgraphs, so Lemma 2.1 gives (i); Lemma 5.1 gives
(ii). (⇐) Induction on the number of blocks. If `G` has no cut vertex it is a single block and
(i) is the claim. Otherwise pick a cut vertex `a`; by Lemma 5.2 some branch `B_j` at `a` has
`D_j^a` an interval. Both `B_j` and `G′ := ⋃_{i≠j} B_i` are connected, have strictly fewer
blocks than `G`, and inherit (i) and (ii) (their blocks are blocks of `G`, their cut vertices
are cut vertices of `G`, and branch partitions restrict to branch partitions). By induction
both are spherical; insert `B_j`'s disc into the face of `G′` at the gap vacated by `D_j^a`
exactly as in Lemma 5.2a. ∎

*Proof of (c).* By (a), a spherical `ρ` is exactly the data of: one spherical `ρ|_B` per block,
plus, at each cut vertex `a`, one merge pattern of the branch dart-sets that is non-crossing.
These data are independent: the blocks are edge-disjoint, every dart belongs to exactly one
germ, and two distinct blocks meet in at most one vertex (if they shared two, their union
would be 2-connected, contradicting maximality), so the merge pattern at `a` constrains no
dart outside `D_a` and no two cut vertices share a dart. By (b) the number of merge patterns
at `a` is `A(d₁(a),…,d_{t(a)}(a))` regardless of the block rotations. ∎

---

## 6. The recursion, the master count, and where the shift lives (part (b))

**Definition 6.1 (admissible split pair).** A split pair `{a,b}` of a 2-connected `H` with
`k` bridges is *admissible* if `k ≥ 3`, or `k = 2` and both bridges have `≥ 2` edges.
(The inadmissible case is `k = 2` with a trivial bridge, where `B⁺ ≅ H` and (3.1) is vacuous.)

**Lemma 6.2 (termination and exhaustiveness).** Let `H` be 2-connected, loopless, with
`≥ 3` vertices, not a cycle, not 3-connected-simple. Then `H` has an admissible split pair,
and every bridge satisfies `|E(B_i⁺)| < |E(H)|`.

*Proof.* If `H` has a parallel class `P_uv` with `m ≥ 2`, then `H − {u,v} ≠ ∅` and is a union
of `c ≥ 1` components, so `k = m + c ≥ 3`: admissible. Otherwise `H` is simple; not
3-connected and `|V| ≥ 4` gives a 2-cut `{u,v}` with `c ≥ 2` components, so `k = m_uv + c ≥ 2`,
and if `k = 2` then `m_uv = 0` and both bridges are nontrivial hence have `≥ 2` edges:
admissible. (`|V| = 3` simple 2-connected is the triangle, a cycle, excluded.) Size: if
`k ≥ 3` then `|E(B_i)| ≤ |E(H)| − 2`; if `k = 2` with both bridges `≥ 2` edges then
`|E(B_i)| ≤ |E(H)| − 2`; either way `|E(B_i⁺)| ≤ |E(H)| − 1`. ∎

**The recursion.** For connected loopless `G`:

```
N(G) = ∏_{blocks B} N(B) · ∏_{cut vertices a} A(a)                       (Theorem 5.3)
N(B) = (m−1)!                        if B is a dipole with m edges       (§4.1)
     = 1                             if B is a cycle                     (§4.2)
     = 2  (or 0 if non-planar)       if B is simple 3-connected          (§4.3, Whitney)
     = (k−1)! · ∏_i N(B_i⁺)          at an admissible split pair         (Theorem 3.5)
```

Grouping the recursion by *maximal* split pairs reproduces the SPQR tree of `B`
(P-nodes = split pairs, S-nodes = cycles, R-nodes = 3-connected skeletons); a greedy grouping
does not, but the resulting *count* is the same, because every step is a bijection:

### Theorem 6.M (master count)

For a connected loopless planar multigraph `G`,

```
N(G) = [ ∏_{cut vertices a} A(a) ] · ∏_{blocks B} [ 2^{#R(B)} · ∏_{P-nodes of B} (k_P − 1)! ]
                                                                                    (6.1)
```

where `#R(B)` is the number of R-nodes of `B` and `k_P = m_P + c_P` is the number of bridges
at the P-node `P`. `N(G) = 0` iff some R-node skeleton is non-planar. The value is
independent of every choice made in the recursion (it counts a fixed finite set).

*Proof.* Combine Theorem 5.3, Theorem 3.5, Lemma 6.2 and §4, by induction on `|E|`.
Independence of choices is automatic: each step is a *bijection*, so the product counts the
set of spherical rotation systems of `G`, which does not depend on the decomposition. ∎

*(Corollary: the classical statement "the combinatorial embeddings of a 2-connected planar
graph are parameterised by one flip per R-node and one cyclic order per P-node" is
re-derived in-house; SPQR uniqueness is used only as terminology, never as a proof step.)*

### Corollary 6.R (Theorem R of R1c)

Let `S` be 3-connected planar simple, `G` its parallel expansion. `G` is 2-connected with a
single R-node (skeleton `S`) and, for each class with `m_uv ≥ 2`, one P-node with
`m = m_uv`, `c = 1` (because `S − {u,v}` is connected), so `k = m+1`. Hence

```
N(G) = 2 · ∏_{uv ∈ E(S)} m_uv!    ✓  (Theorem R of R1C_RANK_N_THREECONNECTED.md)
```

and Lemma 3.2 with `c = 1` reproduces Theorem R's block condition (1) while Lemma 3.3
reproduces its reversal condition (3), and Whitney reproduces (2).

### Theorem 6.S (shift dichotomy — exactly when a free `Z/m` appears)

Let `P_uv` be a parallel class, `m = m_uv`. Normalise the count by the rank families, i.e.
divide `N(G)` by `∏_{classes} m_uv!` (this is legitimate, §7.3). Then the enumerated
("scheme") multiplicity attached to `P_uv` is:

1. **Inside a 2-connected block, `c ≥ 1`:** `(m+c−1)!/m! = (m+1)(m+2)⋯(m+c−1)`.
   * `c = 1` → **1**: no parameter, no shift. (All classes of `K₄`, `C₄`, of any R-node
     skeleton, and of every leg of `K₄−e`.)
   * `c = 2` → **`m+1`**: the `K₄−e` cut `i ∈ {0,…,m}`. Not a shift — a *composition*.
   * `c ≥ 3` → `(m+1)⋯(m+c−1)`, together with `(c−1)!` orders of the nontrivial bridges.
2. **The class is an entire block (`c = 0`, i.e. `P_uv` is a "bundle block" of the
   block–cut tree).** Its own factor is `(m−1)!/m! = 1/m`, and each pole that is a cut vertex
   contributes a factor `d_i = m` inside `A(·)` (5.1). Hence the net multiplicity of the class is
   * **both poles cut vertices → `m`**: one free **`Z/m` shift**. This is the `P₄` central
     class, codex Lemma 2.2 / factor `m` of codex (2.2).
   * **exactly one pole a cut vertex (the other a leaf germ of `S`) → `1`**: no shift; the
     leaf rotation is forced as a cycle. (`P₄`'s outer classes `P`, `Q`; the paw's pendant
     class.)
   * both poles non-cut → `G` is a single dipole, excluded by (H5).

*Proof.* Direct expansion of (6.1) divided by `∏ m_uv!`, using (3.2) for case 1 and
`A(d₁,…,d_t) = (∏ d_i)(N−1)!/(N−t+1)!` for case 2; the factors `d_i` of `A` are in bijection
with the blocks at the cut vertex, and the one belonging to the bundle block equals `m`. ∎

> **Reading of Theorem 6.S.** "Both poles are cut into by adjacent blocks" is the right
> intuition, but it must be said at the level of **blocks**, not poles: the shift exists iff
> the class is *itself a block* and *both* of its ends carry further blocks. A class sitting
> inside a 2-connected block never has a shift, however many other classes touch its poles —
> the reversal of Lemma 3.3 pins it.

---

## 7. Schemes, slot maps and the compatibility layer (part (c))

### 7.1 Schemes

**Definition 7.1.** A **scheme** `σ` for `G` is a tuple consisting of

| node type | datum | count |
|---|---|---|
| R-node | one bit (which Whitney reflection of the 3-connected skeleton) | `2` |
| P-node, `c ≥ 1` | cyclic order of the `c` nontrivial bridges **and** a composition `m = i₁+…+i_c` | `(m+c−1)!/m!` |
| P-node, `c = 0` (bundle block) | — | `1/m` (bookkeeping; see below) |
| S-node | — | `1` |
| cut vertex `a` | a *positional* non-crossing merge pattern of its `t` blocks together with one rotation offset per block | `A(d₁,…,d_t)` |

and the **scheme count** is

```
|Σ|  =  N(G) / ∏_{uv ∈ E(S)} m_uv!  =  [∏_{cut a} A(a)] · ∏_{blocks} ε(B),
ε(B) := N(B) / ∏_{P_uv ⊆ B} m_uv!  =  2^{#R(B)} ∏_{P-nodes} (m_P + c_P − 1)!/m_P! ,
ε(dipole block with m edges) = 1/m ,   ε(single-edge block) = 1.               (7.1)
```

`|Σ|` is a positive **integer** whenever `G` is connected with `≥ 3` vertices (Lemma 7.4);
the fractional-looking `1/m` of a bundle block is always cancelled by a factor `m` from an
incident cut vertex.

The merge pattern at a cut vertex is specified **positionally** (which *slot indices* of each
block's dart sequence at `a` interleave how), never by dart identities; hence it is
independent of the ranks.

### 7.2 Layouts and slot maps

**Definition 7.2 (layout).** Given a scheme `σ`, define for each germ `v` a **layout**
`L_v^σ`: a bijection from `Z/n_v` onto the pairs (class incident to `v`, position within
class), built top-down:

* if `v` is a cut vertex, splice the blocks' sequences at `v` according to the merge pattern;
* inside a block, walk the decomposition: at a P-node with poles `{a,b}` and `v = a`,
  concatenate the `k` bridge segments in the chosen cyclic order — a trivial bridge is one
  dart of the class `P_ab` at within-class position given by its rank, a nontrivial bridge
  contributes its own layout at `a` computed in `B_i⁺` minus the virtual dart; if `v = b`,
  use the reversed bridge order with each segment internally reversed; if `v ∉ {a,b}`,
  recurse into the unique bridge containing `v`;
* at an R-node, use the Whitney macro-rotation selected by the bit, each skeleton edge
  replaced by its sub-segment;
* at an S-node, concatenate the two sub-segments (unique cyclic order).

Then, for a dart `d` at `v` belonging to class `class(d)` of size `m`, the **slot map**

```
P_d^σ : {0,…,m−1} → Z/n_v ,      z ↦ position of the class-member of rank z in L_v^σ .   (7.2)
```

**Lemma 7.3 (slot maps are injective and partition).** For every scheme `σ` and every germ
`v`, the maps `{P_d^σ : d ∈ D_v}` grouped by class are injective, their images are pairwise
disjoint, and together they exhaust `Z/n_v`.

*Proof.* Immediate from Definition 7.2: `L_v^σ` is a bijection `Z/n_v →` (class, within-class
position), so the positions occupied by a class of size `m` form a set of size `m` and
`P_d^σ` is the induced order-preserving-per-arc bijection from `{0,…,m−1}` onto it. ∎

**Shape of the slot maps.** The set of positions of a class `P_uv` at `u` is a union of arcs:

* `c` arcs from its own P-node composition (Theorem 3.5), reversed in order and internally at
  the other pole `v`;
* possibly further split by insertions of other blocks if `u` is a cut vertex (the paw's
  remark "the chosen gap may lie inside a triangle parallel class" — a solver that inserts
  only *between* classes is incomplete).

On each arc `P_d^σ` is affine `z ↦ β + z` or `z ↦ β + (m−1−z)`. So the general slot map is
**piecewise signed-affine with at most `c + t_u − 1` pieces** — exactly the `K₄−e`
generalisation ("the central maps are affine on the two rank intervals separated by `i`").
Injectivity, which is all that Theorem 4.3 needs, never depends on the number of pieces.

**Lemma 7.4 (rank normalisation; integrality of `|Σ|`).** Assume `G` connected with `≥ 3`
vertices. For each class choose a **reference pole** of simple-degree `≥ 2` (one exists:
if both poles had simple-degree 1 then `G` would be that dipole). Define ranks `z_e` at the
reference pole and reversed ranks at the other. Then

```
(scheme σ, all-different ranks (z_e))  ⟼  rotation system ρ
```

is a **bijection** onto the spherical rotation systems of `G`. In particular
`|Σ| = N(G)/∏ m_uv!` is a positive integer.

*Proof.* Surjectivity and injectivity follow by induction from the bijections of Theorem 3.5
and Theorem 5.3(a): each writes the rotation data as (a discrete parameter) × (data of
strictly smaller pieces), so by induction the composite is a bijection onto the spherical
rotation systems, once the rank datum of every class is *anchored* — i.e. once the cyclic
order of the class at its reference pole `u` is cut at a distinguished place, so that
"the linear order `L`" is a well-defined function of the ranks rather than a cyclic order.
The anchor exists at a pole `u` of simple-degree `≥ 2`, and it is one of exactly three things:
(i) the neighbouring bridge segment of the class's own P-node when `c ≥ 1`;
(ii) when `c = 0` (bundle block) and `u` is a cut vertex, the insertion point at `u` of another
branch (this is the `d_i = m` factor of `A(u)`, and it is exactly the `P₄` shift of
Theorem 6.S);
(iii) when `c = 0` and `u` is not a cut vertex — impossible for `u` of simple-degree `≥ 2`,
since then some other class at `u` would put `u` in a second block.
The non-reference pole `v` needs no anchor: its cyclic order is the reverse of `u`'s
(Lemma 2.2/3.3), and if `v` is a leaf germ its origin is arbitrary and absorbed by the phase
`s_g` ([R3], §7.3). Integrality of `N(G)/∏ m_uv!` is then automatic. Machine-verified on
1,861 random connected multigraphs, §10.3. **This is the single step in §7 most likely to
hide an over- or under-count; see §11.6.** ∎

### 7.3 Phases, constraint cycles and propagation

Nothing in the codex compatibility layer is rank- or support-specific; all three statements
transfer with `P_d` replaced by `P_d^σ`:

* **Lemma 4.1 (phases), rank-`n` form.** For a generator `g`, put `v = g⁺`, `n_v = deg(v)`.
  The rotations defined by the slot maps satisfy (2.1) iff there is one phase
  `s_g ∈ Z/n_v` with `P_d^σ(z_{e(d)}) + P_{Bd}^σ(z_{e(Bd)}) + s_g ≡ 0 (mod n_v)` for every
  `B`-transposition. *Proof:* verbatim; it uses only that both sides are cyclic orders on
  `n_v` slots and that reversal is "slot sum = const". The arbitrary linear cut of each
  germ's cyclic order shifts every slot at that germ by a constant, absorbed into `s_g`
  ([R3]); only the *sum* of the two germ shifts of a generator is seen by (4.3), and each
  germ occurs in exactly one generator's equations.
* **Lemma 4.2 (constraint cycles).** `H_{A,B}` (vertices = `A`-edges, one constraint edge per
  `B`-transposition) is 2-regular with components in canonical bijection with the `r`
  relators. Verbatim, rank-free, support-free.
* **Theorem 4.3 (propagation).** For fixed `σ` and phases: on each component of `H_{A,B}`
  pick a seed `A`-edge, try each of its `|class|` ranks, and propagate uniquely around the
  cycle by inverse slot lookup (`P^σ` injective by Lemma 7.3); retain the closures; combine
  one retained assignment per relator cycle subject to global per-class all-different, and
  verify `|⋃ ranks in P_uv| = m_uv` for every class.

### Theorem 7.5 (R1c-v2 decision theorem)

Let `G` satisfy (H1), (H3), (H4), (H5). Then `P` admits a Neuwirth-compatible spherical
rotation **iff** there exist

```
a scheme σ ∈ Σ ,   a phase tuple (s_g)_{g} ∈ ∏_g Z/n_{g⁺} ,
and all-different ranks (z_e) per class
```

satisfying every equation (4.3) in the form of §7.3. The enumeration

```
|Σ|  ×  ∏_g n_{g⁺}  ×  (seeds and retained-combination search of Theorem 4.3)      (7.3)
```

is **exhaustive**: a NO verdict is valid only after all of it has been searched.

*Proof.* (⇐) A satisfying triple defines, by Lemma 7.4, a rotation system that is spherical
(Theorem 6.M's bijections) and, by Lemma 4.1, satisfies (2.1). (⇒) Given a compatible
spherical `C`, Lemma 7.4 reads off its scheme and ranks and Lemma 4.1 its phases;
Theorem 4.3 shows the ranks are found by seed propagation. ∎

**Global reflection.** `ρ ↦ ρ^{-1}` preserves sphericity and (2.1)
(`B(C_v^{-1})^{-1}B = BC_vB = (BC_v^{-1}B)^{-1}`), and acts on `Σ × ranks` by flipping every
R-bit, reversing every P-node cyclic order and merge pattern, and sending `z ↦ m−1−z`. It is
**free** whenever some germ has degree `≥ 3` (a rotation equal to its own reverse forces
degree `≤ 2`; brute-force check §10.1). Hence it is sound to fix one R-node bit, halving
`|Σ|`. If there is no R-node, do **not** quotient unless a specific free binary coordinate
has been exhibited — the safe default is no quotient (cost: factor 2).

**Cost.** Per `(σ, phases)` pair: one propagation per relator cycle, cost
`≤ (max class size)·(cycle length)`, then the cross-cycle combination under global
all-different, worst case `∏_{cycles}(#retained) ≲ |E(G)|^r` ([R2], unchanged). Total
elementary steps `≲ |Σ| · ∏_g n_{g⁺} · |E|^r`. Polynomial for bounded `r`; the `n = r = 3`
targets are trivially machine-checkable (§9.6).

---

## 8. Scope and fail-closed boundary (part (d))

### 8.1 What R1c-v2 DECIDES

A YES/NO verdict may be returned only when **all** of the following are established for the
exact word-realised input:

1. the endpoint data are exactly the `(D, A, B, ν)` dictionary of `lit_AK3_NEUWIRTH.md`;
2. `G = G_A` is **loopless** (equivalently every relator is cyclically reduced);
3. `G` is **connected**;
4. `S` is **planar**, established by a *certified* planarity test (an embedding witness), or
   `S` is certified **non-planar** (a `K₅`/`K_{3,3}` subdivision witness or an equivalent
   certificate) — in the latter case `N(G) = 0` and the verdict is `NOT_SPHERICAL`;
5. `2n ≥ 4`;
6. the block–cut decomposition and, within each block, the split-pair recursion terminate
   with every leaf a dipole, a cycle, or a **simple 3-connected** skeleton to which Whitney
   applies;
7. every slot map is injective with images partitioning each germ's slots (Lemma 7.3, to be
   re-checked at run time, not assumed);
8. each `B`-transposition contributes exactly one equation (4.3); constraint loops
   (one-letter relators) and constraint 2-cycles (two-letter relators) are *tested*, not
   simplified away;
9. before returning NO, the search has exhausted **every** scheme `σ ∈ Σ` (all R-bits — modulo
   at most one global reflection bit —, all P-node bridge orders and compositions, all
   cut-vertex merge patterns), every phase tuple in `∏_g Z/n_{g⁺}`, every seed rank on every
   component of `H_{A,B}`, and every retained component-solution combination;
10. an accepted witness independently reconstructs the `2n` rotations, replays (2.1), verifies
    the per-class rank partitions, and recomputes `χ = 2` from `|C| − |A| + |AC|`.

Under 1–10, **every connected loopless planar support at every rank is in scope**: 3-connected
(R1c, now a corollary), 2-connected with arbitrary SPQR structure, and arbitrary block–cut
structure including cut vertices with `t ≥ 3` blocks.

### 8.2 What is STILL excluded (fail-closed → `UNSUPPORTED`)

* **`A`-loops.** A loop at a germ (from a non-cyclically-reduced relator) is outside every
  lemma here and outside the general Synchronized Planarity statement as used. The codex
  one-loop and paw-one-loop notes cover *specific* one-loop supports; R1c-v2 does **not**
  subsume them and does not extend them. Reason: Lemma 2.2 and Lemma 3.2 both assume
  `ν(d) ≠ ν(A(d))`. *(A loop-removal reduction is plausible — a loop's two darts are
  consecutive whenever `G − v` is connected — but it is not proved here.)*
* **Disconnected `G`.** Excluded twice over: the Neuwirth bridge (Thm 2 of
  `lit_AK3_NEUWIRTH.md`) needs a connected link, and a rotation system of a disconnected link
  caps its components separately, forgetting their relative nesting in the common sphere
  (Lemma 2.1's trap box). The `B`-pipes may also couple rotations in different components.
* **`S` non-planar but not certified.** Return `UNDETERMINED`, never `NOT_SPHERICAL`.
* **`n = 1`** (two germs): `G` is a dipole, Lemma 7.4's rank normalisation degenerates
  (`|Σ| = 1/m`). The count `N = (m−1)!` is still correct; the scheme machinery is not needed.
* **Anything not verified by 8.1.1–10.** In particular a decomposition that stalls (no
  admissible split pair while the piece is neither dipole, cycle nor 3-connected simple) is an
  **audit contradiction**, not an `UNSUPPORTED`: by Lemma 6.2 it cannot happen, so it signals
  an implementation bug.
* **Non-orientable / non-PL questions, AC-invariance.** Unchanged from R1c: a negative applies
  only to the exact word-realised complex tested, and neither verdict is an AC invariant.

### 8.3 What is *no longer* excluded (delta against R1c)

R1c's fail-closed list `"any germ of degree < 3, any 2-cut in S"` is **removed**. Degree-1 and
degree-2 germs are handled: a simple-degree-1 germ is the far pole of a bundle block (its
rotation is forced as a cycle, its origin absorbed by the phase); a simple-degree-2 germ is
either an interior vertex of an S-node (no free parameter, Theorem 6.S case 1 with `c = 1`) or
a cut vertex with `t = 2` blocks (free parameters `A(d₁,d₂) = d₁d₂`, Theorem 6.S case 2).

---

## 9. Sanity anchors (part (e))

All numbers in §9 are reproduced by the master formula (6.1) *and* independently by
brute-force enumeration of rotation systems where the instance is small enough (§10).

### 9.1 `K₄` multigraph → Theorem 3.1 of the codex

One R-node, six P-nodes with `c = 1`:
`N = 2 · ∏_{u<v} m_uv!` ✓ codex (3.2). `|Σ| = 2` — one scheme after fixing the reflection, exactly
"fix the first tetrahedral macro-rotation".

### 9.2 `C₄` multigraph → Theorem 6.1 of the codex

One S-node, four P-nodes with `c = 1`: `N = ∏ m_uv!` ✓ codex (6.1). `|Σ| = 1` — the
single `C₄` scheme.

### 9.3 `K₄−e` → Theorem 5.2, count `(m+1)!·m_ac!m_bc!m_ad!m_bd!`

`S = K₄ − cd`, poles `a,b` of degree 3, `c,d` of degree 2. `G` is 2-connected, no cut
vertices. Split pair `{a,b}`: `m = m_ab` trivial bridges and `c = 2` nontrivial bridges
`𝖢` (through `c`) and `𝖣` (through `d`), so `k = m+2` and

```
N(G) = (m+2−1)! · N(𝖢⁺) · N(𝖣⁺).
```

`𝖢⁺` is the triangle `a–c–b` with classes `m_ac`, `m_bc` and the virtual `ab`-edge: an S-node
(triangle) with two P-nodes of `c = 1`, so `N(𝖢⁺) = m_ac!·m_bc!`; likewise
`N(𝖣⁺) = m_ad!·m_bd!`. Hence

```
N(G) = (m+1)! · m_ac! m_bc! m_ad! m_bd!      ✓ = codex (5.2)
```

and by (7.1) `|Σ| = (m+1)!/m! = m+1` — **exactly the `m+1` cuts `i ∈ {0,…,m}` of codex (5.1)**,
with `L` carried by ranks. Lemmas 3.2/3.3 specialise to codex Lemma 5.1, and the display of §3
specialises to the `Q_i` slot scheme of the codex verbatim. Brute-forced for
`(m; legs)` = `(1;1,1,1,1)`, `(2;1,1,1,1)`, `(1;2,1,1,1)`, `(0;2,1,1,1)`, `(2;2,1,1,1)`,
`(3;1,1,1,1)`, `(1;1,2,1,1)` — all agree (§10.1).

*Nota bene:* the case `m = 0` is included (`k = 2`, `|Σ| = 1`) and gives `N = m_ac!m_bc!m_ad!m_bd!`.
It is the shape of the harvest bridges below.

### 9.4 `P₄` → Theorem 2.3, count `p!·m!·m·q!`

`S = a−b−c−d`, classes `P` (`p`), `M` (`m`), `Q` (`q`). `G` is **not** 2-connected: `b` and
`c` are cut vertices, and there are three blocks, each a bundle (dipole) block. By (6.1)

```
N(G) = [ (p−1)!·(m−1)!·(q−1)! ] · A(p,m) · A(m,q)
     = (p−1)!(m−1)!(q−1)! · (p·m) · (m·q)
     = p! · m! · m · q!            ✓ = codex (2.2)
```

and `|Σ| = N/(p!m!q!) = m` — **exactly the central shift `s ∈ Z/m` of the P₄ note's Lemma 2.2**, and exactly the
`m` schemes `Q_s` of Corollary 3.1. Theorem 6.S case 2 identifies it: `M` is a bundle block
with *both* poles cut vertices. The outer classes `P`, `Q` are bundle blocks with only one
cut-vertex pole, hence carry no shift — matching "the leaf rotation at `a` is forced as a
cycle". Brute-forced for `(p,m,q)` = `(1,1,1)`, `(2,1,1)`, `(1,2,1)`, `(2,2,1)`, `(1,3,1)`,
`(2,1,2)`, `(1,2,2)` — all agree (§10.1).

### 9.5 Paw core (a cut vertex, `t = 2`) → Theorem 3.2, count `p·∏ m!`

Triangle `abc` plus pendant class `ad`; `a` is a cut vertex with blocks
`B₁ =` parallel triangle (`d₁ = m_ab + m_ac =: p`) and `B₂ =` pendant bundle (`d₂ = m_ad`).

```
N = N(B₁)·N(B₂)·A(p, m_ad) = [m_ab! m_ac! m_bc!] · (m_ad − 1)! · p · m_ad
  = p · m_ab! m_ac! m_bc! m_ad!        ✓ = (3.2) of the paw note
```

`|Σ| = p` — the `p` insertion gaps. The paw note's warning that the gap may fall *inside* a
triangle class is precisely the "further arc splitting at a cut vertex" of §7.2.

### 9.6 The harvest instance: a 2-cut separating a `K₄` core from a `z`-bridge

**Provenance.** Round-1 harvest, root `AK3+z`, depth 3, move `AC1 r3←r3·r2⁻¹`, exact state

```
w₁ = xxxYYYYz ,  w₂ = xyxYXYZ ,  w₃ = zzyxyXYX
canonical key: ("ZxyxYXY", "ZZxyxYXY", "ZyyyyXXX")   (total length 23)
```

`neuwirth_rank_n.classify_support_n` returns `UNSUPPORTED`,
reason `"(H2) fails: 2-cut {0, 2}"`, `planar = True`, `three_connected = False`. Simple
support (6 germs, 10 simple edges) and multiplicities:

```
x⁺x⁻ 2   x⁺y⁻ 4   x⁺z⁺ 2   x⁺z⁻ 1   x⁻y⁺ 4
x⁻y⁻ 3   y⁺y⁻ 3   y⁺z⁺ 1   y⁺z⁻ 2   z⁺z⁻ 1
degrees:  n_{x±} = 9 ,  n_{y±} = 10 ,  n_{z±} = 4     (|E(G)| = 23)
```

**Correction to the sketch's description.** The separating pair is **`{x⁺, y⁺}`**, *not*
`{z⁺, z⁻}`. The `z`-germs are the **interior** of one bridge. This is uniform: all 628
two-cut states of round 1 have the cut `{x⁺, y⁺}`, in two shapes (336 without an `x⁺y⁺`
edge, 292 with one).

**Decomposition.** `G` is 2-connected (no cut vertices). `G − {x⁺,y⁺}` has two components,
`{x⁻,y⁻}` and `{z⁺,z⁻}`, and `m_{x⁺y⁺} = 0`, so the split pair `{x⁺,y⁺}` has `k = 0 + 2 = 2`
bridges:

* **core bridge** `𝖢`: interior `{x⁻,y⁻}`. `𝖢⁺` (add the virtual `x⁺y⁺` edge) is a **`K₄`
  multigraph** on `{x⁺,y⁺,x⁻,y⁻}` with classes
  `x⁺y⁺ = 1 (virtual), x⁺x⁻ = 2, x⁺y⁻ = 4, x⁻y⁺ = 4, y⁺y⁻ = 3, x⁻y⁻ = 3`;
* **`z`-bridge** `𝖹`: interior `{z⁺,z⁻}`. `𝖹⁺` is a **`K₄` multigraph** on `{x⁺,y⁺,z⁺,z⁻}`
  with classes `x⁺y⁺ = 1 (virtual), x⁺z⁺ = 2, x⁺z⁻ = 1, y⁺z⁺ = 1, y⁺z⁻ = 2, z⁺z⁻ = 1`.

So the SPQR shape is **P(k=2) — R — R**, with a P-node per parallel class of multiplicity `≥ 2`
hanging off each R-node. Applying (6.1):

```
N(𝖢⁺) = 2 · 1!·2!·4!·4!·3!·3! = 2 · 41 472 = 82 944
N(𝖹⁺) = 2 · 1!·2!·1!·1!·2!·1! =  2 ·      4 =      8
N(G)  = (2−1)! · 82 944 · 8   = 663 552
∏ m_uv! = 2!·4!·2!·1!·4!·3!·3!·1!·2!·1! = 165 888
|Σ|   = 663 552 / 165 888 = 4  =  2 (core R-bit) × 2 (z R-bit) × 1 (P-node, k = 2)
```

**Enumeration budget.**

| quantity | value |
|---|---:|
| compatible-rotation census `∏_g (n_{g⁺}−1)! = 8!·9!·3!` | **87 787 929 600** |
| labelled spherical rotation systems `N(G)` | 663 552 |
| schemes `\|Σ\|` | **4** (→ **2** after fixing one R-bit) |
| phase tuples `n_{x⁺}·n_{y⁺}·n_{z⁺} = 9·10·4` | **360** |
| top-level branches `\|Σ\|/2 × phases` | **720** |
| seeds per relator cycle | `≤ max m_uv = 4` |
| relator cycles | 3 |

so the whole decision is `720 × (3 cycles × ≤ 4 seeds × propagation of length ≤ |w_j|)` plus a
cross-cycle combination of at most `4³ = 64` — order `10⁵` elementary steps, against a
factorial census of `8.8 × 10¹⁰` that the harvest had to abandon
(`census family 87787929600 exceeds the per-state cap 2000000`). The gate string
`(H2) fails: 2-cut {0, 2}` becomes `IN SCOPE (R1c-v2, P-R-R)`.

**Shape B (the 292 states with an `x⁺y⁺` edge).** Example
`("YXYxyx", "ZxyxYXY", "ZZyyyyXXX")`, multiplicities as above but `x⁺y⁺ = 1`,
`x⁺z⁺ = x⁺z⁻ = y⁺z⁺ = y⁺z⁻ = 1`. Now `k = 1 + 2 = 3` at the 2-cut, `𝖹⁺` is the *simple* `K₄`:

```
N = (3−1)! · [2·1!·2!·4!·4!·3!·3!] · [2·1!·1!·1!·1!·1!·1!] = 2 · 82 944 · 2 = 331 776
∏ m! = 41 472 ,  |Σ| = 8 = 2 × 2 × (m+c−1)!/m! with m = 1, c = 2  (= 2!/1! = 2)
phases = 9·10·3 = 270 ,  top-level branches = (8/2)·270 = 1 080
```

versus its census `8!·9!·2! = 29 262 643 200` (the harvest's recorded
`census family 29262643200`).

---

## 10. Machine verification performed (small range; not a proof)

The checking scripts were written in an ephemeral session scratchpad and are **not**
committed; they are ~150 lines and are fully specified by this recipe, which the referee
should re-implement rather than trust: (a) *brute force* — enumerate all rotation systems
(fix one dart per vertex, permute the rest), count faces as the cycles of `d ↦ other(next(d))`,
accept iff `V − E + F = 2`; (b) *predictor* — biconnected components by DFS on edge indices,
then the recursion of §6 (first admissible split pair, bridges by components of `H − {a,b}`),
with `A(·)` from (5.1); (c) compare on random connected multigraphs.

**10.1 End-to-end.** The master formula (6.1)+(5.2) was compared with brute force on
**1,355 connected planar multigraphs** with 3–6 vertices and 3–7 edges (random,
deduplicated): **0 mismatches**. In the 1,100 instrumented cases, **854 have at least one cut
vertex** and **193 have a cut vertex with `t ≥ 3` blocks**, so the delicate branch of §5 is
genuinely exercised. Additionally every published anchor of §9.1–9.5 was checked directly
(`K₄`, `C₄`, `K₄−e` at 7 multiplicity vectors, `P₄` at 7, paw at 6): all agree with both the
published closed forms and brute force.

Structural spot-checks: (i) on a 2-connected graph with a `k = 3` split pair, all 4 spherical
systems have every bridge an interval at both poles and the bridge order at `b` the exact
reverse of the one at `a` — **0 violations**; (ii) on the `t = 3` cut-vertex witness of
TRAP 2, **2 of the 6** spherical systems have a non-interval block — confirming that the
two-component interval lemma must not be extended; (iii) reflection `ρ ↦ ρ^{-1}` has no fixed
spherical system on the tested graphs with max degree `≥ 3`, and has one on the triangle
(all degrees 2) — confirming the freeness caveat of §7.3.

**10.2 Kreweras step.** The labelled non-crossing-partition count `N!/(N−t+1)!` was
enumerated exhaustively for size vectors `(2,2), (2,1,1), (2,2,1), (3,2), (2,2,2), (3,1,1),
(1,1,1,1), (2,1,1,1), (3,2,1)`: all agree, and the derived `A(d)` of (5.1) agrees with the
brute-force embedding counts in every case.

**10.3 Integrality of `|Σ|`.** `N(G)/∏ m_uv!` is an integer on 1,861 random connected
multigraphs (3–6 vertices, 3–7 edges): **0 non-integers**.

**Not verified:** anything with `≥ 8` edges, anything non-planar, the phase/rank layer at
`n = 3` (that is the implementation's job — R1c's [R2] cost analysis is inherited unchanged),
and the harvest instance's `N = 663 552` (too large for brute force; it is a two-step
application of the already-verified formula).

---

## 11. Audit checklist for the referee — attack in this order

1. **Lemma 3.2, the `b ∈ Ω` *and* `b ∈ Ω′` contradiction.** This is the load-bearing new
   argument. Check: (a) the path `P` really avoids `b` — it does *only because* a nontrivial
   bridge contains no `ab`-edge, so both heads lie in `C_i`; (b) `B_j − a` is connected for a
   *trivial* bridge too; (c) `d₁, d₂` are consecutive **in `D_i^a`**, so that all other gaps of
   `D_i^a` lie in the complementary arc. Try to build a 2-connected counterexample with a
   nested bridge.
2. **Theorem 5.3 / equation (5.1), and its dependence on Kreweras (K).** (K) is imported, not
   reproved. Attack the reduction "merge patterns ↔ labelled non-crossing partitions with `0`
   in part 1, times `∏_{i≥2} d_i`" — in particular the rotation-invariance step used to get
   the factor `d₁/N`. Independent falsification: extend the brute-force table of §10.1 to
   `t = 4,5` with mixed `d_i`.
3. **Lemma 5.2 and Lemma 5.2a.** The claim "a non-crossing partition of a cycle always has a
   part that is an interval" is proved by a strictly decreasing recursion into an occupied
   gap; check the degenerate branches (`|T_γ| = 1`, parts of size 1, `t = 2`) and the step
   "an interval of an arc containing no other part is an interval of the whole cycle". Then
   check that Lemma 5.2a's induction really peels an *interval* branch and never an arbitrary
   leaf of the block–cut tree — the naive sequential-insertion count is **order-dependent and
   wrong** (it gives `6` for `d = (2,1,1)` but `4` for `d = (1,1,2)`; the truth is `6`).
4. **Independence of the choices at distinct cut vertices** (last paragraph of the proof of
   Theorem 5.3). This is the step that would break if two blocks shared *two* cut vertices —
   they cannot (they would then lie in one block), but say so explicitly.
5. **Theorem 6.S / TRAP 1.** Verify that no `Z/m` shift has been dropped by checking `P₄`
   *through the general machinery* (§9.4) rather than by quoting codex (2.2), and re-run the two
   recorded false-negative witnesses `⟨x,y | xY, yy⟩` and `⟨x,y | xxx, xxy⟩` against an
   implementation of §7.
6. **Lemma 7.4 (rank normalisation).** The bijection claim is where a *silent over- or
   under-count* would hide. Under-counting is fatal (false NO); over-counting is only wasted
   work. Attack the reference-pole choice when a class has **both** poles of simple-degree 2,
   and the case where a class is split into arcs at *both* its poles by cut-vertex insertions.
7. **The global-reflection quotient** (§7.3). It is sound to fix one R-bit; it is *not*
   obviously sound to fix a P-node cyclic order when `k = 2` (reversal acts trivially there).
   Check that the implementation never quotients in the absence of an R-node.
8. **Whitney (W) at R-nodes with parallel classes re-inflated.** We apply (W) to the *simple*
   skeleton only; verify that the recursion always strips parallel classes into P-nodes first
   (Lemma 6.2's first branch) so that no R-node skeleton ever carries a multi-edge.
9. **Planarity certification.** `N(G) = 0` is claimed exactly when some R-node skeleton is
   non-planar. Verify that a non-planar *whole* graph always exhibits itself that way (it does:
   S- and P-nodes are planar and Theorem 3.5/5.3 are bijections), and that the implementation
   never reports `NOT_SPHERICAL` from an uncertified planarity failure.
10. **Loops and disconnection** (§8.2). Confirm no lemma silently assumes away a loop that the
    input could contain, and that the `UNSUPPORTED` routing is unconditional.
11. **The `n = r = 3` regression.** Recompute §9.6 independently (its two `K₄` bridges are pure
    Theorem R instances) and check that the resulting solver's YES witnesses replay (2.1) and
    `χ = 2`.

---

## 12. Summary of new content

* **Lemma 3.2** — bridge-interval lemma for an arbitrary split pair of a 2-connected
  multigraph, with a proof that isolates *why* it needs 2-connectivity (both `b ∈ Ω` and
  `b ∈ Ω′`). Generalises the codex Lemma 5.1 from `K₄−e` to arbitrary supports and arbitrary rank.
* **Theorem 3.5 + (3.2)** — P-node composition as a bijection, with the exact analogue of the
  `K₄−e` cut parameter: `(c−1)!` bridge orders × `C(m+c−1,c−1)` compositions × `m!` ranks.
* **Lemma 5.1 / Theorem 5.3 / (5.1)** — the correct cut-vertex theory for **any** number of
  blocks, replacing the two-component interval lemma (which is false for `t ≥ 3`) by
  non-crossing partitions, with the closed count `A(d) = (∏d_i)(N−1)!/(N−t+1)!`.
* **Theorem 6.M** — master count for every connected loopless planar support at every rank,
  decomposition-independent, with Theorem R as a corollary.
* **Theorem 6.S** — the exact shift dichotomy: a free `Z/m` appears **iff** the class is itself
  a block with both poles cut vertices. This is the formal statement of the `P₄` lesson.
* **§7** — layouts, piecewise signed-affine slot maps, the scheme count
  `|Σ| = N(G)/∏ m_uv!`, and the transfer of Lemmas 4.1/4.2 and Theorem 4.3.
* **§9.6** — the first in-scope rank-3 harvest instance, decomposed `P–R–R`, with the
  enumeration reduced from `8.8 × 10¹⁰` compatible rotations to `720` top-level branches.

## Sources

1. `results/stable_ac/theory/fable/R1C_RANK_N_THREECONNECTED.md` — Theorems R and P, [R1]–[R5].
2. `lit_AK3_SYNCHRONIZED_PLANARITY.md` — Thm 3.1, Lemma 5.1, Thm 5.2 (5.1)/(5.2), Thm 6.1,
   Lemma 4.1, Lemma 4.2, Thm 4.3.
3. `lit_AK3_P4_SYNCHRONIZED_PLANARITY.md` — Lemma 2.1, Lemma 2.2 (central shift), Thm 2.3,
   Cor 3.1, and the two recorded zero-shift false negatives.
4. `lit_AK3_PAW_ONE_LOOP_PLANARITY.md` — Lemma 2.1 (two-component cut-vertex intervals) and
   Thm 3.2 (the `p` insertion gaps).
5. `lit_AK3_NEUWIRTH.md` — the `(D,A,B,ν)` dictionary, Lemma 1 (Euler), Theorem 2, Corollary 3.
6. G. Kreweras, "Sur les partitions non croisées d'un cycle", *Discrete Math.* 1 (1972),
   333–350 — the non-crossing partition count (K).
7. B. Mohar, C. Thomassen, *Graphs on Surfaces*, Whitney's uniqueness theorem (W).
8. T. Bläsius, S. D. Fink, I. Rutter, "Synchronized Planarity …", ESA 2021 / *ACM TALG* 19(4)
   (2023) — the general polynomial-time framework this note gives a constructive, in-house
   special case of.
