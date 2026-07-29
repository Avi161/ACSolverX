# R10 — Zeeman route: is AK(3)'s `K x I` collapsible?

STATUS: **INSTRUMENT REPORT + PARTIAL POSITIVE RESULTS + CALIBRATED NULL.**
Not a proof of anything about AK(3). Everything below is either machine-certified,
proved here, or explicitly flagged.

Branch note (project rule): this session could only write to
`claude/ac-stable-ac-conjecture-ijfzgz`. **This branch must be merged back into
`fable/proof` by the user.**

Instruments: `experiments/stable_ac/fable/zeeman_collapse.py` (engine, builders,
verifier), `experiments/stable_ac/fable/zeeman_battery.py` (driver).
Data: `results/stable_ac/fable/zeeman_collapse.json`,
certificates in `results/stable_ac/fable/zeeman_certs/`.

---

## 0. The question, stated exactly

Let `P = AK(3) = <x, y | x x x Y Y Y Y, x y x Y X Y>` (uppercase = inverse), i.e.
`x^3 = y^4`, `xyx = yxy`. `P` is a balanced presentation of the trivial group, so its
presentation 2-complex is acyclic and simply connected, hence **contractible**
(Hurewicz + Whitehead). Zeeman's conjecture asserts that for every contractible finite
2-complex `K`, `K x I` is collapsible. So:

> **Q.** For an explicit triangulation `K'` of AK(3)'s presentation 2-complex, is
> `K' x I` collapsible?

An affirmative answer is a **complete, replayable positive certificate**: a finite list
of elementary free-face collapses, checkable by anyone against the face list, with no
reference to the search that found it. A negative answer is *not* produced by this
instrument at all — the search is one-sided, and its silence is worth exactly its
measured detection rate (§4).

### What a hit would and would not mean

This must be read before any number below.

1. **A hit is about ONE COMPLEX, i.e. machinery + topology — not about AK(3) as a
   presentation, and not about the group.** Collapsibility of `K' x I` is a property of
   the combinatorial datum `K'`, which is determined by *the relators as spelled* plus
   the subdivision parameters. It is not a homotopy invariant and not a topological
   invariant (§5).
2. **The useful implication direction is Zeeman ⇒ AC.** Do not read anything here as
   AC ⇒ Zeeman. In particular AK(2) being AC-trivial does **not** imply that AK(2)'s
   `K x I` is collapsible; that is why AK(2) is a *plausibility* control here and the
   dunce hat and Bing's house are the *guaranteed* ones (§4).
3. **Even in the best case the conclusion is STABLE AC-triviality, not unstable.** The
   final link is the Q**-transformation / 3-deformation correspondence, and Q**
   includes stabilisation. See §6 for the precise chain and each link's status.
4. **A miss on one triangulation says nothing about other triangulations**, and a miss
   on one spelling says nothing about other spellings in AK(3)'s AC class. This is the
   exact analogue of the spelling-dependence this line already established for
   `gamma_N` (R7), and it cuts the same way.

---

## 1. The triangulation, stated so a third party can rebuild it

`presentation_complex(words, gens, subdivision=s)` in `zeeman_collapse.py`. Words are
used **exactly as spelled**, with no free reduction, because the 2-complex depends on
the spelling (the dunce hat is the complex of the *unreduced* word `xxX`; the complex of
`x` is a disc — same group element, different complex, and one is collapsible while the
other is not).

* One base vertex `v`. Each generator `g` becomes a loop subdivided into `s >= 3` edges
  `v - g1 - ... - g(s-1) - v`, so the 1-skeleton is a simple graph: a bouquet of
  `s`-cycles wedged at `v`.
* Each relator `w` gives a disc glued along the closed edge-walk `p` of length
  `m = s * |w|` that spells `w` in the 1-skeleton. The disc is triangulated as a
  **collar plus a cone**: fresh inner cycle `u_0 .. u_{m-1}`, fresh apex `c`, and the
  triangles, for `i = 0..m-1`, `j = i+1 mod m`:

      (p_i, p_j, u_i),   (p_j, u_i, u_j),   (c, u_i, u_j).

  Every triangle contains a fresh vertex and consecutive walk vertices are distinct, so
  the quotient is an honest simplicial complex.
* `K' x [0, L]` uses the standard **staircase** product triangulation: vertex `v` at
  level `j` is `v + j*n` (`n = |V(K')|`), and for each face `sigma = [v_0<...<v_d]` and
  each layer `j` the prism is cut into the `d+1` simplices
  `[(v_0,j) .. (v_i,j), (v_i,j+1) .. (v_d,j+1)]`.

Sizes actually used (all machine-measured, `s = subdivision`, `L = layers`):

| complex | `f`-vector of `K'` | faces of `K'` | free faces of `K'` | faces of `K' x [0,L]` |
|---|---|---|---|---|
| AK(3), s=3 | [46, 162, 117] | 325 | **0** | 1767 (L=1), 3209 (L=2) |
| AK(3), s=4 | [61, 216, 156] | 433 | **0** | 2355 (L=1), 4277 (L=2) |
| AK(2), s=3 | [40, 138, 99] | 277 | **0** | 1503 (L=1), 2729 (L=2) |
| dunce `<x|xxX>`, s=3 | [13, 39, 27] | 79 | **0** | 423 (L=1), 767 (L=2) |
| Bing house | [72, 237, 166] | 475 | **0** | 2563 (L=1), 4651 (L=2) |

`K'` itself has **no free face at all** for every target of interest, so `K'` is
immediately stuck: nothing about these complexes is collapsible for free.

---

## 2. Anchor table — the engine audited against known answers

Re-verified from scratch this session (`--phase anchors`); every column is computed by
the code, and `H_*` is integer simplicial homology via Smith normal form. `bottom` is
the **deterministic** (search-free) collapse `K x I \searrow K x {0}` of §3, replayed by
the independent verifier. `prism -> pt` is the *blind* search that phase C uses.

| anchor | `f(K)` | chi | `H_*(K)` | free faces | known: contractible? | known: `K` collapsible? | engine: `K` collapsible? | known: `K x I` collapsible? | engine: `K x I -> pt`? | `K x I -> K x {0}` replay |
|---|---|---|---|---|---|---|---|---|---|---|
| 3-simplex `ball3` | [4,6,4,1] | 1 | `Z,0,0,0` | 4 | yes | yes | **yes** | yes | **yes** | ok |
| hexagonal disc | [7,12,6] | 1 | `Z,0,0` | 6 | yes | yes | **yes** | yes | **yes** | ok |
| `<x \| x>` (disc) | [7,15,9] | 1 | `Z,0,0` | 3 | yes | yes | **yes** | yes | **yes** | ok |
| `S^2 = d(3-simplex)` | [4,6,4] | 2 | `Z,0,Z` | **0** | no (`b_2=1`) | no | **no** | no | **no** | ok |
| `RP^2 = <x \| xx>` | [10,27,18] | 1 | `Z,Z/2,0` | **0** | no (`H_1=Z/2`) | no | **no** | no | **no** | ok |
| dunce hat `<x \| xxX>` | [13,39,27] | 1 | `Z,0,0` | **0** | yes | **no** | **no** | yes (Zeeman's example) | **yes** | ok |
| **Bing's house** | [72,237,166] | 1 | `Z,0,0` | **0** | yes | **no** | **no** | expected yes | **yes** | ok |

Reading of the table:

* **The two anchors that break a wrong engine both behave correctly.** The dunce hat and
  Bing's house are contractible with **zero** free faces, so an engine that reports
  either of them as collapsible is broken. Ours reports both as non-collapsible.
  Contractibility of Bing's house is *certified*, not assumed: `H_* = (Z, 0, 0)` by Smith
  normal form, and `pi_1 = 1` by building the edge-path presentation from a spanning
  tree (166 generators, 166 relators) and Tietze-reducing it to `< | >` — 0 generators,
  0 relators.
* **The two negative controls on the product are also correct.** `S^2 x I` and
  `RP^2 x I` are not contractible (`H_2` resp. `H_1` survives), so they *cannot* be
  collapsible, and the search reports no hit — 0 hits in 40,000 runs for `RP^2 x I` in a
  separate direct measurement. The hit detector therefore does not manufacture
  positives.
* Every `K x I \searrow K x {0}` claim is the deterministic sequence of §3, replayed
  step-by-step by `verify_collapse_sequence`, which recomputes each free face by
  brute-force scan and shares no bookkeeping with the search.

---

## 3. PROVED here: `K x [0,L] \searrow K x {0}`, with no search

This is leg (a) of the certificate and it needs no luck.

**Proposition R10.1.** Let `K` be a finite simplicial complex with vertices ordered, and
give `K x [0,L]` the staircase triangulation of §1. Then the explicit sequence produced
by `cylinder_collapse_sequence(K, L)` is a collapse `K x [0,L] \searrow K x {0}`.

*Proof.* Fix a layer and a simplex `sigma = [v_0 < ... < v_d]`; write `v'` for the copy
of `v` one level up. The faces of `sigma x [j,j+1]` whose vertex shadow is all of
`sigma` are exactly

  `S_i = [v_0..v_i, v_i', .., v_d']`  and  `tau_i = S_i \ {v_i} = [v_0..v_{i-1}, v_i', .., v_d']`
  for `i = 0..d`, together with the flat copies `sigma x {j}` and `sigma x {j+1}`;
  note `tau_0 = sigma x {j+1}`.

Inside the prism, `tau_i` has exactly the two cofaces `S_{i-1}` and `S_i` (adding
`v_{i-1}'` resp. `v_i` to the chain), and `tau_0` has only `S_0`. So `tau_0` is free,
and once `(tau_{i-1}, S_{i-1})` is gone `tau_i` is free. Collapsing `(tau_i, S_i)` for
`i = 0..d` therefore removes exactly `{S_i} u {tau_i}`, i.e. every face with shadow
`sigma` except `sigma x {j}`. Sweeping `sigma` in order of **decreasing dimension** makes
each `S_i` maximal when reached (its cofaces live over shadows strictly containing
`sigma`, already removed), and sweeping layers from the top down chains the layers.
What survives is exactly the set of faces contained in `K x {0}`. ∎

**Machine-certified for every target**, by independent replay:

| complex | L | prism faces | deterministic steps | replay |
|---|---|---|---|---|
| AK(3), s=3 | 1 | 1767 | 721 | ok |
| AK(3), s=3 | 2 | 3209 | 1442 | ok |
| AK(2), s=3 | 1 | 1503 | 613 | ok |
| Bing house | 1 | 2563 | 1044 | ok |
| dunce, s=3 | 1 | 423 | 172 | ok |

**Corollary R10.2 (PROVED).** If `K' x I \searrow point` for one of these
triangulations, then `K' \nearrow K' x I \searrow point` is a **3-deformation of `K'` to a
point** (a finite sequence of elementary expansions and collapses through complexes of
dimension `<= 3`, since `dim K' x I = 3`). No literature is used: leg (a) is
Proposition R10.1 run backwards, leg (b) would be the certificate.

So the whole route reduces to one finite combinatorial question per triangulation, and
the only external input is the *last* step, §6.

---

## 4. Power calibration — MANDATORY, and read this before §5

The instrument is one-sided. An uncalibrated one-sided null is worth nothing; this line
has already made that mistake once
(`experiments/lessons/calibrate-one-sided-hunts-on-a-positive-ladder.md`). So the
question "does the search find collapses that exist, at this size, on complexes of this
shape?" is answered *first*.

Positive rungs, in increasing order of evidential value:

* **dunce hat x I** — contractible, `K` not collapsible, 0 free faces, and
  `K x I` collapsible is Zeeman's own example. Guaranteed positive.
* **padded dunce hats** `<x, a, b, .. | xxX, a, b, ..>` — the padding relators are single
  letters, so each padding disc is glued along a loop occurring in no other relator;
  every edge of that loop lies in exactly one triangle, the padding collapses away, and
  `K \searrow` dunce hat. Guaranteed positive at growing size with the hard core fixed.
* **Bing's house x I** — contractible, `K` not collapsible, 0 free faces, prism *larger*
  than AK(3)'s. This is the closest structural analogue of the AK targets available.

**Measured hit rates (blind search, per restart, strategies `uniform-lifo`/`top-lifo`,
score partition `copy`).** `basefree` = free faces of `K` itself.

| rung | basefaces | basefree | prism faces | hits / runs | rate | certificate |
|---|---|---|---|---|---|---|
| dunce s=3 L=1 | 79 | 0 | 423 | 222 / 6220 | **3.57 %** | replay ok, 211 steps |
| dunce s=3 L=2 | 79 | 0 | 767 | 208 / 3194 | **6.51 %** | replay ok, 383 steps |
| dunce s=4 L=1 | 105 | 0 | 563 | 169 / 4634 | **3.65 %** | replay ok, 281 steps |
| dunce s=5 L=1 | 131 | 0 | 703 | 229 / 3575 | **6.41 %** | replay ok, 351 steps |
| dunce s=6 L=1 | 157 | 0 | 843 | 96 / 2544 | **3.77 %** | replay ok, 421 steps |
| dunce+2pad | 139 | 6 | 735 | 132 / 2656 | **4.97 %** | replay ok, 367 steps |
| dunce+4pad | 199 | 12 | 1047 | 110 / 1791 | **6.14 %** | replay ok, 523 steps |
| dunce+6pad | 259 | 18 | 1359 | 46 / 1350 | **3.41 %** | replay ok, 679 steps |
| dunce+8pad | 319 | 24 | 1671 | 52 / 1054 | **4.93 %** | replay ok, 835 steps |
| dunce+10pad | 379 | 30 | 1983 | 34 / 759 | **4.48 %** | replay ok, 991 steps |
| **Bing's house L=1** | 475 | **0** | 2563 | 0 / 835 (ladder) | **0 %** | — |
| **Bing's house L=1** | 475 | **0** | 2563 | hit at restart **313** (anchor phase, different seed) | ~`3e-3` | replay ok, 1281 steps |
| **Bing's house L=2** | 475 | **0** | 4651 | 1 / 542 | **0.18 %** | replay ok, 2325 steps |

Three readings, and the third is the one that matters:

1. **Raw size is not the difficulty axis.** The dunce ladder holds a flat 3.4–6.5 % hit
   rate from 423 up to 1,983 prism faces — a 4.7× size increase with no measurable
   decay. So a null at AK-scale cannot be blamed on size alone.
2. **The instrument has demonstrated power on a genuinely hard positive.**
   `(Bing's house) x I` collapses, and we hold a machine-replayed 1,281-step certificate
   for it (`zeeman_certs/zeeman_cert_anchor_bing_prism_to_point.json`). Bing's house is
   the closest available structural analogue of the AK complexes: contractible, **zero**
   free faces, base larger than AK(3)'s, prism larger than AK(3)'s. This is the single
   most important calibration fact in this document, and it is a hit, not an assumption.
3. **But the power there is 20–40× weaker.** Two independent measurements put the
   Bing-house rate at roughly `1e-3` to `3e-3` per restart, against ~`5e-2` on the
   dunce ladder. **The operative detection rate for AK-shaped inputs is therefore
   ~`1e-3`, not ~`5e-2`.** Any null below a few thousand restarts is close to
   uninformative, and every number in §5 must be read against `1e-3`.

Note carefully what AK(2) is and is not. AK(2) is AC-trivial, but *Zeeman is strictly
stronger than AC*: AC-triviality does **not** imply that `K x I` is collapsible. So
AK(2) is a **plausibility** control, not a guaranteed positive, and an AK(2) null cannot
by itself convict the instrument. Bing's house is what certifies the instrument's power.

---

## 5. The AK results — PARTIAL

**This section is incomplete.** The battery was terminated by the session coordinator
partway through phase C, after the AK(2) `s=3, L=1` unit and *before any AK(3) unit ran*.
The AK(3) leg-(b) numbers below therefore come from earlier smaller foreground probes,
not from the battery, and are labelled as such. Runs are per-restart counts.

### 5.1 Leg (a) — certified for AK(3) and AK(2)

| complex | L | prism faces | deterministic steps | independent replay |
|---|---|---|---|---|
| AK(3) s=3 | 1 | 1767 | 721 | **ok** |
| AK(3) s=3 | 2 | 3209 | 1442 | **ok** |
| AK(2) s=3 | 1 | 1503 | 613 | **ok** (`zeeman_cert_ak2_s3_L1_onto_bottom.json`) |
| AK(2) s=3 | 2 | 2729 | 1226 | **ok** |

This is Proposition R10.1 and it is not in doubt. It is also, on its own, of no use
without leg (b).

**Artifact caveat.** The two AK(2) rows have certificate files on disk
(`zeeman_cert_ak2_s3_L{1,2}_onto_bottom.json`, both `replay_ok=true`). The two **AK(3)
rows were verified in-memory in a foreground probe and no certificate file was written**
before the run was stopped, so a reader should re-derive them rather than take this
table's word — three lines, seconds to run:
`cx,_=build_target('ak3',3); pr,bot=prism(cx,L);
verify_collapse_sequence(sorted(pr.faces), cylinder_collapse_sequence(cx,L),
target='subcomplex', protected=bot)`. There are **no AK(3) certificates of any kind in
`zeeman_certs/`**; the directory holds 25 files, all anchors, ladder rungs, and AK(2)
leg (a).

### 5.2 AK(2) — the mandatory control: **NO COLLAPSE FOUND**

`s = 3, L = 1`, prism 1,503 faces:

* blind search: **0 hits / 5,749 restarts**
* guided search (structural opening: spend the prism over `k` random 2-cells first,
  `k` uniform in `1..12`): **0 hits / 3,134 restarts**
* graded near-miss, best of 1,577 randomized discrete-Morse sweeps: Morse vector
  **`[1, 2, 2]`** (5 critical cells; Euler check `1 - 2 + 2 = 1` ✓). So the best sweep
  found was **two critical pairs short** of a collapse.

**Stated plainly: the AK(2) positive control did not collapse.** Consequences, in order:

* Against the operative detection rate of ~`1e-3` (§4, rung 3), 5,749 restarts with zero
  hits is *suggestive* — one would expect a handful of hits if `AK(2) x I` were
  collapsible at Bing-house difficulty — but it is **not decisive**, and it is only about
  the `s=3, L=1` triangulation.
* It does **not** invalidate the instrument, because AK(2)'s prism was never a guaranteed
  positive (§4, last paragraph). The instrument's power is certified by Bing's house, and
  that certification stands.
* It does mean that **no AK(3) null in this document is backed by a matched positive at
  AK-exact structure and AK-exact size.** The nearest matched positive is Bing's house,
  which is a *different* complex, larger, and with a rate 20–40× below the dunce ladder.
  Read every AK(3) statement below with that gap in mind.

### 5.3 AK(3) — no collapse found; the battery unit never ran

What exists (foreground probes only, `s = 3`, `L = 1`, prism 1,767 faces):

| probe | strategies / score | restarts | result |
|---|---|---|---|
| A | `uniform-lifo`, score `none` | 200 | no hit, best 325 faces left, residual `f = [46,162,117]` |
| B | `top-lifo`, `bottom-lifo`, `uniform-rand`, `top-rand`, score `none` | ~200 each | no hit, best 325 left, same residual |
| C | same five strategies, score `copy` / `extreme` | ~12–200 each | no hit, best 537–585 left |
| D | `uniform-lifo`, score `none`, `s = 4` (`L = 1`), `s = 3` (`L = 2`), `s = 4` (`L = 2`) | 200 each | no hit; best 433 / 743 / 1053 left |

**Best AK(3) result: no collapse; `best_faces_left = 325`, residual
`f-vector = [46, 162, 117]`.** That residual f-vector is *exactly* `K`'s own f-vector
(§1) — the search collapses `K x I` vertically onto the copy `K x {0}` and dies there,
because `K` has zero free faces. That is a terminal state no bounded tail-rollback can
repair, which is why the plateau depth of 325 is worthless as a progress signal (see
`experiments/lessons/plateau-depth-is-not-progress.md`).

**Total AK(3) effort is of order 10^3 restarts — roughly ONE Bing-house detection time.**
So the AK(3) null is at present **uncalibrated in the sense that matters**: it is right
at the threshold where the measured `1e-3` rate begins to bite, so it excludes almost
nothing. It should not be described as evidence against collapsibility of `AK(3) x I`.
The one experiment that would change this is §9.

---

## 6. The Zeeman ⇒ AC implication, stated precisely, with sourcing status

The chain, link by link. `P` is the presentation, `K_P` its standard (one-vertex)
presentation 2-complex, `K'` the subdivided simplicial model of §1.

| # | link | status |
|---|---|---|
| L1 | `K'` is contractible (`AK(3)` balanced, trivial group ⇒ acyclic; `pi_1 = 1` ⇒ contractible) | **PROVED** (homology machine-checked here; `pi_1 = 1` is the defining property of `AK(3)`) |
| L2 | `K' x [0,L] \searrow K' x {0}` | **PROVED** (Prop. R10.1) + machine-replayed |
| L3 | `K' x I \searrow pt` ⇒ `K'` 3-deforms to a point | **PROVED** (Cor. R10.2) |
| L4 | `K'` 3-deforms to a point ⇒ `K_P` 3-deforms to a point (subdivision bridge) | **[UNVERIFIED]**, but reducible to L5's easy direction — see below |
| L5 | `K_P` 3-deforms to a point ⇒ `P` is Q**-equivalent to the trivial presentation | **[UNVERIFIED]** — the substantive external theorem |
| L6 | Q**-equivalent to the trivial presentation = **stably** AC-trivial (Q** contains stabilisation) | **[UNVERIFIED]** as a quotation; conservative reading adopted |

**L4 in more detail.** `K'` is a subdivision of `K_P`. Subdivision is not free: 3-deformation
type is not known to be a homotopy invariant of 2-complexes (that would essentially *be*
the AC conjecture). But it does follow from the *easy, constructive* direction of the
Q**/3-deformation correspondence ("a Q** move on attaching words is realised by a
3-deformation"), by the standard argument: to subdivide a 1-cell `e` (`p -> q`), expand by
a vertex `w` and 1-cell `f` (`q -> w`), expand by a 1-cell `g` (`p -> w`) together with a
2-cell `G` with `dG = e f g^{-1}` (an elementary expansion, since `g` occurs once in
`dG`), then use 3-deformations to replace every occurrence of `e` in every attaching word
by `g f^{-1}`; `e` then occurs only in `dG`, so `(e, G)` collapses, and the result is the
subdivided complex. Subdividing a 2-cell by an arc is the same argument one dimension up.
So L4 costs no *new* external theorem beyond L5 — but it is a sketch written here, not a
quotation, and it has not been adversarially audited.

**Sourcing attempts this session, all recorded.** `arxiv.org/html/2412.12293`,
`arxiv.org/abs/2412.12293`, `en.wikipedia.org/wiki/Andrews–Curtis_conjecture`,
`link.springer.com/.../978-3-642-22003-6_11.pdf` (the HMS-adjacent chapter "The
Andrews–Curtis Conjecture"), and Kupers' expository notes on Zeeman's conjecture
(`utsc.utoronto.ca/.../GJM2021-Kupers.pdf`, `.../zeemansconjecture.pdf`) — **every one
returned HTTP 403 through this container's proxy**, exactly as
`experiments/lessons/cloud-session-network-and-push-constraints.md` predicts.
GitHub code search for a LaTeX mirror of 2412.12293: no source mirror.

**What IS sourced verbatim** (arXiv RSS mirrored on GitHub, `ehijano/rss_fetch`, and
`MystenLabs/snowreads`; both re-checked this session):

> *Stable Andrews-Curtis Conjecture via Fake Surfaces and Zeeman Conjecture* — Fagan,
> Qiu, Wang. "We propose an induction scheme that aims at establishing the stable
> Andrews-Curtis conjecture in the affirmative. **The stable Andrews-Curtis conjecture is
> equivalent to the conjecture that every contractible fake surface is 3-deformable to a
> point.** We prove that every contractible fake surface of complexity less than 6 is
> 3-deformable to a point by induction."

> *Classification of Cellular Fake Surfaces* (arXiv:2406.09439v3). "...two-dimensional
> generic polyhedra with an eye towards applications to low-dimensional topology,
> **especially the Andrews-Curtis and Zeeman conjectures**."

That first quotation is the strongest available support for L5+L6 *in the stable form*:
"3-deformable to a point" is paired with **stable** AC, for fake surfaces. It is not a
quotation about 2-complexes, so the transfer to `K_P` remains **[UNVERIFIED]**.

**Explicitly NOT sourced, and not to be cited from this document:** any attribution of
"Zeeman ⇒ AC" to a named author or theorem number. Web search surfaced sentences of the
form "Wright formulated an equivalent conjecture about 3-deformations of 2-CW-complexes
..., thus showing that Zeeman conjecture implies the Andrews-Curtis conjecture" and
"Q**-transformations of group presentations are equivalent to 3-deformations of
CW-complexes of dimension 2" — but only from search-result snippets and from
LLM-generated secondary repositories (`0thernes/unsolved-mathematics`, `loning/the-math`,
`jcraig949jfi/Prometheus`), one of which even carries an invented theorem attribution.
Under this line's provenance rules
(`results/stable_ac/theory/fable/LITERATURE_STATUS.md`) those are worth zero. They are
recorded here as *leads to verify*, not as citations.

**Standing instruction.** The first network-capable session should fetch Wright's paper
on 3-deformations, the Hog-Angeloni–Metzler–Sieradski chapter on the AC conjecture, and
`arxiv.org/html/2412.12293v2`, store them under `literature/txt/` with `git add -f`, and
then L4/L5/L6 can be upgraded from [UNVERIFIED] to quotations in one pass.

---

## 7. Triangulation dependence, stated as sharply as the spelling dependence

**Collapsibility is not a topological invariant, and not a homotopy invariant.** Three
facts from the anchor table alone make this concrete:

* the dunce hat and Bing's house are contractible and *not* collapsible, while a disc is;
* `<x | x>` and `<x | xxX>` have the same relator as a *group element* (`x`), present the
  same group, and give a disc and a dunce hat respectively — collapsible and not;
* therefore the object being tested, `K'`, is a function of the **spelling** of the
  relators and of the subdivision parameters `s` and `L`, not of `AK(3)` as a
  presentation and certainly not of the trivial group.

Consequences, both directions:

* **A hit transfers.** If `K' x [0,L]` collapses for *any* `s`, `L`, or any spelling in
  AK(3)'s AC class, Cor. R10.2 applies to that `K'`, and (given L4) the conclusion about
  `K_P` is the same. Zeeman's conjecture is itself normally read "collapsible after
  subdivision", so trying several triangulations is legitimate, not cheating. This gives
  the route a whole extra search dimension — spellings — that has not been exploited.
* **A miss does not transfer.** A null at `(s, L)` says nothing about `(s', L')`, and
  nothing about other spellings. Any future summary that writes "AK(3)'s `K x I` is not
  collapsible" is wrong: the correct statement is "no collapse was found for these
  triangulations at this budget, by a search with the measured hit rates of §4".

---

## 8. PROVED / CONJECTURED / OPEN

**PROVED (this session, machine-certified and independently replayable):**

1. Prop. R10.1: the explicit search-free collapse `K x [0,L] \searrow K x {0}` for the
   staircase triangulation, with proof. Verified by independent replay for
   **AK(3) at `s = 3`, `L in {1,2}`**, AK(2) at `s = 3`, `L in {1,2}`, Bing's house,
   the dunce hat, and every anchor. (`s = 4` was *not* replayed — only its sizes were
   measured. The proposition covers it; the machine check does not.)
2. Cor. R10.2: leg (a) reversed + leg (b) is a 3-deformation of `K'` to a point.
3. The anchor table of §2, including: Bing's house as built here is contractible
   (`H_* = (Z,0,0)`, `pi_1` Tietze-reduced to `< | >`) and has no free face; the dunce
   hat likewise; `S^2 x I` and `RP^2 x I` are not collapsible and the search correctly
   returns no hit on them (`RP^2 x I`: 0 hits in 40,000 restarts in a direct
   measurement, 0 in 3,627 in the battery).
4. **`(Bing's house) x I` is collapsible** for the staircase triangulation used here —
   a 1,281-step certificate, independently replayed
   (`zeeman_certs/zeeman_cert_anchor_bing_prism_to_point.json`). Likewise
   `(dunce hat) x I` (211 steps) and every rung of the §4 ladder. These are the
   route's only new positive results, and they concern anchors, not AK(3).

**CONJECTURED / measured but not proved:**

5. The hit rates of §4 are measurements of *this* search on *these* triangulations. They
   bound the detection rate from **below** only in the trivial sense that a longer run
   can only find more; they do not bound the true collapsibility of anything.
6. The minimal discrete-Morse vectors of §5 are **upper** bounds on the true minimum
   (they come from a randomized sweep). A large observed minimum is *not* evidence of
   non-collapsibility, and the same histogram shape is produced by a degrading search
   and by a real obstruction
   (`experiments/lessons/parallel-runs-and-bound-direction.md`).

**OPEN:**

7. Is `K' x I` collapsible for AK(3), for any `(spelling, s, L)`? Undecided here.
8. L4, L5, L6 of §6 — the subdivision bridge and the Q**/3-deformation correspondence —
   are unsourced in this container. Until L5 is sourced, **a hit must be reported as
   "AK(3)'s presentation 2-complex 3-deforms to a point", never as "AK(3) is stably
   AC-trivial"**, exactly as R7's Joint A gates its own transfer.
9. Zeeman's conjecture itself, for the class of 2-complexes this route needs, is open in
   the literature; nothing here changes that.
10. **Is `AK(2) x I` collapsible for any triangulation?** Open. The `s=3, L=1` null
    (0/5,749 blind, 0/3,134 guided, best Morse `[1,2,2]`) is the only measurement.

---

## 9. The one experiment that most advances R10

The missing cell is the whole point of the route: **AK(3)'s leg (b) blind search never
ran under the battery.** It is a single-threaded run under 10 minutes.

Preflight (same code path, same functions, ~35–50 s):

    nice -n 15 timeout 55 python3 -m experiments.stable_ac.fable.zeeman_battery \
      --phase targets --subdivisions 3 --layers 1 \
      --target-seconds 8 --morse-seconds 4 \
      --out /tmp/zeeman_preflight.json --certdir /tmp/zeeman_preflight_certs

Expect: two `[target]` lines (`ak2 s=3 L=1`, `ak3 s=3 L=1`), each reporting
`onto_bottom replay_ok=true` and a nonzero blind `runs` count. If either line is missing
or `replay_ok` is false, stop — the code path is broken and the main run is worthless.

Main run (4 units, ~9.5 min: per unit ≈ 80 s blind + 40 s guided + 20 s Morse + ~3 s
build/verify = 143 s):

    nice -n 15 python3 -m experiments.stable_ac.fable.zeeman_battery \
      --phase targets --subdivisions 3 --layers 1 2 \
      --target-seconds 80 --morse-seconds 20 \
      --out results/stable_ac/fable/zeeman_ak_targets.json \
      --certdir results/stable_ac/fable/zeeman_certs

Covers AK(2) and AK(3) at `L = 1` and `L = 2` (`L = 2` is where Bing's house hit, and
where the dunce rate roughly doubled — it is the more promising triangulation, not merely
a bigger one). Output is flushed after every unit, so a kill at any moment leaves usable
partial data.

What it decides: at ~5,000 blind restarts per unit against a measured `1e-3` AK-shaped
detection rate, a hit is a certificate and closes §8.7 affirmatively for that
triangulation; a null finally puts AK(3) on the same evidential footing as the AK(2)
control instead of an order of magnitude below it. Either way the Morse vector gives a
graded near-miss comparable across the two targets.
