# S20 — The link-planarity obstruction: a real lower bound on `γ_N`, and why it does not close the cubic route

Branch `claude/stable-ac-conjecture-stabilization-rwo9as`. **This branch must be merged into
`fable/proof` by the user** — a cloud session can only push to its own `claude/*` branch, so
nothing here reaches `fable/proof` on its own. No PR opened (`FRAMING` trap 10). No existing
file under `experiments/` or `ac_solver/` was modified and no existing `.md` was edited; the
only new code is `experiments/stable_ac/fable/s20_planarity_probe.py`.

---

# VERDICT: **PARTIAL**

| step | claim | verdict |
|---|---|---|
| **1** | link graph non-planar ⇒ `γ_N ≥ 1` | **PROVED** — and it is a genuine **LOWER** bound on `γ_N`, the first written down on this line. It is not new to the repo: `neuwirth_rank_n.classify_support_n` already returns `NOT_SPHERICAL` on this exact ground. |
| **2** | non-planarity is inherited upward along the cubic pipeline's moves | **FALSE for A6's length-3 SPLIT**, by an explicit, doubly-certified counterexample. **True and proved for chord refinement** (both directions). **Proved for S8's length-2 bigon split** at graph level (that move is not in the cubic pipeline). |
| **3** | therefore the cubic route provably cannot certify AK(3) | **DEAD, twice over.** AK(3)'s link is **planar** — necessarily so: *every* rank-2 presentation has a planar link, because 2 generators give 4 germs and every graph on ≤ 4 vertices is planar. And even from a non-planar start, step 2 fails. |

**Nothing here proves or disproves the AC or the stable AC conjecture, and nothing here
closes the cubic route.** What survives is one proved lower-bound tool (step 1), one
falsified conjecture (step 2 for SPLIT), and a measurement that answers the mechanism
question S17 raised — in the negative.

---

## 0. THE FALSIFICATION TEST, stated first because it is the load-bearing check

If step 1 is right, **every** `γ_N = 0` state must have a planar link. One counterexample
kills the whole idea.

> **`γ_N = 0` states tested: 945 distinct states. Planar: 945. Non-planar: 0.
> Uncertified: 0. VIOLATIONS: 0.**

Composition of the 945 (all distinct, deduplicated on exact words): the 759 `γ_N = 0` hits
of `s4b_control_decided.jsonl.gz` — the brief's named target — plus the 916 `γ_N = 0` SPLIT
children and 186 `γ_N = 0` SPLIT parents of `s17_transition_edges.jsonl.gz`, whose union is
945. The 759 were also swept separately in `s20_planarity_sweep.json`: **759/759 planar,
0 violations, 0 uncertified.**

Every one of those 945 planar verdicts carries an explicit face set that was re-checked by
`verify_sphere_embedding` — every face a closed walk in the graph, every edge on exactly two
faces, the corner multigraph at every vertex a single cycle, and `|V| − |E| + |F| = 2`. The
checker is independent of the algorithm that produced the embedding.

**Step 1 survives its falsification test at every scale tested.** Across the whole corpus
(≈ 180,000 state probes) no state with `minimum_defect = 0` was ever found non-planar, and
no state found non-planar ever had `minimum_defect = 0`.

---

## 1. The instrument, and why its verdicts can be trusted

`networkx` is **not installed** in this clone (`python3 -c "import networkx"` →
`ModuleNotFoundError`), so `check_planarity` (Left–Right) was unavailable. The repo's own
exact test, `neuwirth_rank_n.macro_rotations`, enumerates *every* rotation system of the
simple support and keeps the genus-0 ones — exact, but its family size is
`∏_v (deg v − 1)!`, which blows past the 2 · 10⁶ macro budget on the rank-12/13 supports
this probe had to sweep (measured: the repo's own cut-scheme classifier returns
`UNSUPPORTED — family 5,308,416 exceeds budget` on the very state §3 uses as a
counterexample).

So `s20_planarity_probe.py` implements the classical **Demoucron–Malgrange–Pertuiset**
path-addition test. Per the brief's instruction not to hand-roll a heuristic, **no verdict
is taken on the algorithm's word**:

* **PLANAR** → an explicit face set per biconnected block, re-verified by
  `verify_sphere_embedding` (conditions above). A wrong embedding is rejected.
* **NON-PLANAR** → greedy edge deletion down to an **edge-minimal non-planar subgraph**,
  which is then verified to be a subdivision of `K5` or `K3,3` (suppress degree-2 vertices;
  check 5 vertices/10 arcs/4-regular, or 6 vertices/9 arcs/3-regular/bipartite) and to be a
  subgraph of the link. By Kuratowski's theorem this certificate stands on its own,
  independently of Demoucron.

**Cross-validation against a completely different algorithm** (`selftest`, artifact
`s20_selftest.json`): 15 named graphs — `C5, K4, K5, K5−e, K6, K3,3, K3,3−e`, a `K3,3`
subdivision, `Q3`, the octahedron, Petersen, Wagner `V8`, the prism, a two-`K5`-block graph,
a tree — **all 15 correct**, and each cross-checked against `macro_rotations` where its
budget allowed. Plus **105 random graphs** on 5–8 vertices decided by both methods:
**0 disagreements, 0 uncertified verdicts.**

Every non-planar verdict in the entire S20 corpus was certified, and — a small structural
fact worth recording — **every single one was a `K3,3` subdivision; `K5` never appeared.**
That is what the near-cubic regime predicts: a `K5` subdivision needs five branch vertices of
degree ≥ 4, and in a cubic-ish link most germs have degree 3.

---

## 2. Step 1 — PROVED. Non-planar link ⇒ `γ_N ≥ 1`

### 2.1 What `minimum_defect` actually measures (read from the code, not from a description)

In `neuwirth_rank_n.build_link_n` the link is a multigraph `G_A`:

* **vertices** = the *present germs*, `g+ = 2k` and `g− = 2k+1` for the `k`-th generator;
  `nC = len(data.present_germs) = |V(G_A)|`;
* **edges** = the orbits of the corner involution `A`; each of the `n_occurrences` letter
  occurrences contributes one, so `nA = data.n_occurrences = |E(G_A)|`. Concretely, the
  relator `c₁…c_m` contributes the `m` edges `{end(c_k), start(c_{k+1})}` cyclically, where
  `start(g), end(g) = g+, g−` and `start(G), end(G) = g−, g+`.

`gamma_N_factorial_n` then enumerates a family of rotation systems `C` and scores

```python
defect = nA - nC + 2 * L - nAC          # L = data.link_components, nAC = # face cycles
```

so `χ = V − E + F = 2L − defect`, i.e. `defect = Σᵢ 2gᵢ` over the `L` components of the
orientable rotation surface, and `minimum_genus = minimum_defect // 2`. This is the repo's
`γ_N`: `γ_N = minimum_defect // 2` (`FRAMING`; `S3` §0). **`minimum_defect = 2·γ_N`, and the
two are not interchanged anywhere below.**

The enumerated family (`compatible_orders_n`) fixes the order at each positive germ freely
and forces `C(g−) = B ∘ reverse(C(g+))`. It is therefore a **subfamily of all rotation
systems** of `G_A` — which is the only property the proof needs.

### 2.2 The proof

> **Theorem S20.1.** Let `P` be a presentation whose link multigraph is `G_A` with simple
> support `S`. If `S` is non-planar then `γ_N(P) ≥ 1`. Equivalently: `γ_N(P) = 0 ⇒ S` planar.

*Proof.* Suppose `γ_N(P) = 0`, i.e. some compatible rotation system `C` has `defect = 0`.
By §2.1, `defect = Σᵢ 2gᵢ` over the components of the closed orientable surface `Σ` that `C`
embeds `G_A` in, so every `gᵢ = 0` and `Σ` is a disjoint union of `L` spheres. Hence `G_A`
embeds in `S²` component by component, i.e. `G_A` is planar. Planarity is unaffected by
deleting loops and by collapsing parallel edges, and `S` is exactly `G_A` with those removed,
so `S` is planar. Contrapositive: `S` non-planar ⇒ no compatible rotation system has
`defect = 0` ⇒ `minimum_defect ≥ 2` ⇒ `γ_N ≥ 1`. ∎

Two remarks the proof makes explicit:

* the argument works because compatible rotation systems are a **subset** of all rotation
  systems, so non-planarity kills all of them at once — no property of the compatibility
  constraint is used;
* it is strictly one-directional. **Planar does not imply `γ_N = 0`.** AK(3) is the cleanest
  witness: its link is `K4`, planar, and `γ_N(AK(3)) = 2`.

### 2.3 Verified against the repo's actual implementation

Step 1 is **already load-bearing repo code**, which is the strongest possible check that the
project's own machinery agrees with the reading above:

* `neuwirth_rank_n.classify_support_n` returns `SupportN("NONPLANAR", …)` when
  `macro_rotations` certifies non-planarity, with the in-code justification *"planarity of
  `G_A` implies planarity of its subgraph `S`, so a certified non-planar `S` rules out EVERY
  rotation system"*; `solve_spherical_n` converts that to `NOT_SPHERICAL` with
  `counters.exhaustive = True` — i.e. as a **certified** negative, not a budget failure.
* `neuwirth_cut_schemes` does the same through the SPQR decomposition
  (`decomp.status == NONPLANAR → NOT_SPHERICAL`), and `s12_hunt.decide` labels that branch
  `r1c_v2_nonplanar`.

So the implication is not this session's invention; it is the rule the repo's deciders
already use. What is new here is (i) writing the proof down with the bound direction stated,
and (ii) actually **measuring** where the obstruction fires — nobody had.

### 2.4 Bound direction, stated explicitly

`S` non-planar ⇒ `γ_N ≥ 1` bounds `γ_N` **FROM BELOW**. Every other instrument on this line
bounds `Γ(P) = min{γ_N(Q) : Q ~_st P}` from **ABOVE** (`S15` §4, `S16` §5, `S17` §6).

**But it does not bound `Γ` from below.** `Γ` is a minimum over the whole stable class, and
`γ_N(T_n) = 0` with `T_n`'s link planar (a perfect matching on `2n` germs), so
non-planarity is not a stable-AC invariant. `S15` §6's conclusion — *no monotone lower-bound
quantity is known on this line* — **stands untouched**. S20.1 is a per-state certificate,
not a class obstruction, and §3 shows it is not even monotone under the cubic pipeline's own
move.

One immediate use: the rank-13 cubic form `C1` of `S15` §3 has a **certified non-planar**
link (26 germs, 35 simple edges, `K3,3`), so `γ_N(C1) ≥ 1` is now **proved** rather than only
census-measured. This independently reproduces the `S13` audit's finding on `C1` from a
different code path.

---

## 3. Step 2 — FALSE for A6's SPLIT, by counterexample

### 3.1 What SPLIT does to the link (derived from `cubic_split_search.split_apply`)

SPLIT rotates/inverts relator `i` to `R′ = λ u v`, appends the definition relator
`D = t u v` with `t` fresh, and rewrites `k` chosen occurrences of `λ^{±1}` in *other*
relators to `t^{±1}` (sign preserved). On the link:

1. germ `start(λ)` is **split** into `start(λ)` and `start(t)`, the `k` re-routed corners
   moving to the new germ; likewise `end(λ)` into `end(λ)` and `end(t)`;
2. `D` adds three edges: `{end(t), start(u)}`, `{end(u), start(v)}`, `{end(v), start(t)}`
   (the middle one a parallel copy of an edge relator `i` already contributes).

**Why the S8 argument does not transfer.** S8's move uses the length-2 bigon `u g⁻¹`, whose
two link edges are exactly `{u−, g−}` and `{g+, u+}` — re-derived here and confirmed —
so contracting them merges `u±` into `g±` and gives `link(P)` back as a **minor** of
`link(P′)`. A6's SPLIT has **no** `t±—λ±` edge to contract: the shortest route from `end(t)`
to `end(λ)` has length 2, through `start(u)`, and contracting it would swallow `start(u)`
too. `S15` §6 already warned that the two moves must not be conflated; this is a concrete
reason.

### 3.2 The counterexample (certified two independent ways)

From the persisted AK(3) pool chain `ak3|src0|root14|d3`, replayed step by step with the
repo's own `cubic_split_search.split_apply` (replay reproduced the persisted `words` exactly):

| # | rank | state | link | `γ_N` |
|---|---|---|---|---|
| 0 | 9 | `('dCx','YFG','ayx','bXX','cYa','dXY','eXy','feb','gYY')` | 18 germs, 26 edges, **PLANAR** | 2 |
| 1 | 10 | `('dCx','ygf','ayx','bXX','cHa','dXH','eXy','feb','gYY','hgf')` | 20 germs, 29 edges, **NON-PLANAR** (`K3,3`) | 2 |
| **2** | **11** | `('xdC','ygf','ayi','bXX','cHa','dXH','eIy','feb','gYY','hgf','idC')` | 22 germs, 31 edges, **NON-PLANAR** (`K3,3`) | 2 |
| **3** | **12** | `('xdC','ygf','aji','bXX','cHa','dXH','yeI','feb','gYJ','hgf','idC','jeI')` | 24 germs, 33 edges, **PLANAR** | 2 |

**State 2 → state 3 is one SPLIT, and it destroyed the non-planarity.**

State 2's `K3,3` is small enough to check by hand. The certified witness subgraph has branch
vertices `{x+, y−, y+}` against `{i+, g+, f−}`, joined by the nine arcs

```
x+ –c+– i+ ,  x+ –h−– g+ ,  x+ –x−–d+–h+– f− ,
y− – i+    ,  y− – g+    ,  y− –e+– f−       ,
y+ – i+    ,  y+ – g+    ,  y+ – f−
```

— all fifteen edges verified to lie in state 2's link. State 3's planarity is certified by a
face set with 24 vertices, 33 edges, **11 faces**, `χ = 2`, re-verified by
`verify_sphere_embedding`.

Both states have `γ_N = 2` (exact census 9,216, `minimum_defect` 4), so this is not a
degenerate or ill-defined case.

**Consequence.** `link(P)` is **not** in general a minor of `link(P′)` under A6's SPLIT, and
non-planarity is **not absorbing** along the cubic pipeline. The corollary the brief hoped
for — *once non-planar, `γ_N ≥ 1` forever after* — is false.

### 3.3 How common the escape is (measured, three ways)

| measurement | escapes | opportunities | rate |
|---|---|---|---|
| replayed pool chains, AK(3) family (`s20_chain_planarity.json`) | 1 `N→P` | 300 chains / 910 transitions | 0.11 % |
| fresh SPLIT children from non-planar parents via the repo's own `split_children` (`s20_split_escape.json`) | 36 planar children | 8,700 children from 58 parents | 0.41 % |
| **persisted S17 edge list, `γ_N = 1` parents only** (`s20_s17_planarity.json`) | **226 `N→P` edges** | 10,881 edges from non-planar parents | **2.08 %** |

The escape is rare but systematic and reproducible on three independent corpora. It is not a
sampling artefact.

### 3.4 Chord refinement — PROVED planarity-neutral, both directions

`S3` Lemma S3′ (audited) establishes that a chord refinement subdivides exactly **two** link
edges, inserting two degree-2 germs, and induces a defect-preserving dart-level bijection of
the compatible censuses. Subdivision of a graph preserves planarity in **both** directions
(the two graphs are homeomorphic). Hence chord refinement can neither create nor destroy the
S20.1 obstruction — exactly as it can neither create nor destroy `γ_N` itself. Nothing in
the cubic route's first half can move this quantity.

---

## 4. Step 3 — DEAD. AK(3)'s link is planar, and necessarily so

> **AK(3) = `('xyxYXY','xxxYYYY')`: link support = 4 germs, 6 simple edges, all degrees 3 —
> that is exactly `K4`. PLANAR, certified. `γ_N(AK(3)) = 2`.**

This is not an accident of AK(3)'s spelling. A rank-2 presentation has exactly **4 germs**,
so its simple support is a subgraph of `K4`, and every simple graph on at most 4 vertices is
planar. Therefore:

> **Corollary S20.2.** The link-planarity obstruction can never fire at rank 2. `K5` needs 5
> vertices and `K3,3` needs 6, so a non-planar link requires at least 5 germs, i.e. **rank
> ≥ 3**.

(Direction check, per `experiments/lessons/parallel-runs-and-bound-direction.md`: "rank ≥ 3
is required" is established by an *impossibility* argument — `K4` is planar — not by
constructing a rank-3 example, so it is a genuine necessary condition and not a
construction read backwards.)

Measured, as a sanity check on the corollary: **0 of 300 random rank-2 presentations** over
`{x,X,y,Y}` had a non-planar link.

**Every entry point to the cubic route is planar too.** All 100 rank-9 cubic roots present in
the three pools were tested: 40 AK(3) roots, 29 control0 roots, 31 control2 roots — **100/100
PLANAR** (`s20_ak3_roots.json`). Non-planarity in this corpus is entirely *manufactured by
SPLIT* on the way up in rank; there is nothing to inherit from AK(3).

So step 3 fails on both legs: there is no non-planar starting point at rank 2, and step 2's
inheritance is false anyway.

---

## 5. Where the obstruction *does* fire (measurements)

### 5.1 The `s4b` decided pools

Reservoir samples of 3,000 rows each, plus **all** `γ_N = 0` rows, from
`s4b_decided.jsonl.gz` / `s4b_control_decided.jsonl.gz` / `s4b_ctrl2_decided.jsonl.gz`
(`s20_planarity_sweep.json`, 99.6 s):

| corpus | rows on disk | sampled | planar | **non-planar** | `γ_N = 0` rows | all `γ_N=0` planar? |
|---|---|---|---|---|---|---|
| AK(3) class | 45,111 | 3,000 | 76 | **2,924 (97.5 %)** | 0 | — |
| control0 (thickenable root) | 50,320 | 3,000 | 1,628 | **1,372 (45.7 %)** | 759 | **759/759 ✓** |
| control2 (non-thickenable roots) | 46,298 | 3,000 | 338 | **2,662 (88.7 %)** | 0 | — |

All 6,958 non-planar verdicts certified (`K3,3`, 6,958/6,958); 0 uncertified; 0 errors; **0
violations**. In the cross-tab of planarity against the persisted `minimum_defect`, no
non-planar state had defect 0 and no defect-0 state was non-planar — 9,759 further
independent confirmations of S20.1.

**Caution, per `experiments/lessons/contrast-length-confound.md` and `S16`.** The 97.5 % vs
45.7 % gap between AK(3) and control0 must **not** be read as a contrast result. There are
only three source families, they are not length- or rank-matched at the state level, and
`S16` showed that between-source variance on exactly these pools swamps target-vs-control
differences. No p-value is quoted and none should be: these states come from a move tree and
are not independent draws.

### 5.2 `γ_N` against planarity over the whole S17 corpus

Every distinct state appearing in `s17_transition_edges.jsonl.gz` (`s20_s17_planarity.json`,
116 s):

| `γ_N` | distinct states (as SPLIT child) | planar | non-planar | non-planar % |
|---|---|---|---|---|
| **0** | 916 | **916** | **0** | **0.0 %** |
| 1 | 33,321 | 20,902 | 12,419 | 37.3 % |
| 2 | 129,198 | 18,678 | 110,520 | 85.5 % |
| 3 | 10,743 | 20 | 10,723 | 99.8 % |

| `γ_N` | distinct states (as SPLIT parent) | planar | non-planar |
|---|---|---|---|
| 0 | 186 | 186 | 0 |
| 1 | 1,958 | 1,627 | 331 |
| 2 | 4,222 | 988 | 3,234 |
| 3 | 81 | 0 | 81 |

The `γ_N = 0` row is **forced** by Theorem S20.1 — it is the theorem, not evidence for it.
The other rows are free measurements, and they show non-planarity climbing steeply and
monotonically with `γ_N`.

---

## 6. The mechanism question from `S17`: is planarity why `1 → 0` is empty? **NO**

`S17` measured `1 → 0` = **0 in 56,388** single-SPLIT opportunities from **1,958** distinct
`γ_N = 1` parents, and asked whether the planarity obstruction is the mechanism. A `γ_N = 0`
child must be planar (S20.1), so planarity can only block those edges whose **child** is
non-planar. Both halves were measured directly.

**(a) How many `γ_N = 1` parents are actually blocked?**

> **331 of 1,958 (16.9 %) of the `γ_N = 1` parents have a non-planar link.
> 1,627 (83.1 %) are PLANAR** — i.e. the great majority were never blocked at all.

**(a′) How many of the 56,388 chances were unblocked?** — the sharper question, because
`226/10,881 = 2.1 %` of edges out of a *non-planar* parent still produce a planar child
(§3.3), so a non-planar parent is not blocked either:

| edges out of `γ_N = 1` parents | count | of which child `γ_N = 0` |
|---|---|---|
| parent planar → child planar | 26,535 | 0 |
| parent non-planar → child **planar** | 226 | 0 |
| **child planar, total** | **26,761 (47.5 %)** | **0** |
| parent planar → child non-planar | 18,972 | — (blocked) |
| parent non-planar → child non-planar | 10,655 | — (blocked) |
| **child non-planar, total** | **29,627 (52.5 %)** | — |

> **26,761 of the 56,388 opportunities produced a PLANAR child — a child on which
> `γ_N = 0` was not obstructed by planarity in any way — and not one of them was `γ_N = 0`.**

**Conclusion.** The planarity obstruction is **consistent** with S17's empty `1 → 0` cell —
it was never once violated — but it is **not its mechanism**. It accounts for at most 52.5 %
of the opportunities and leaves **26,761 genuinely unblocked chances unexplained**. The
coordinator's framing was the right test, and the answer it returns is the negative one:
"consistent with a planarity obstruction", **not** "the planarity obstruction is the
mechanism". Whatever makes `1 → 0` empty in this move set, planarity is at most half of it.

The `γ_N = 1` planar children are also worth naming as the residual target: 18,922 edges land
on a **planar** `γ_N = 1` child. Those are the states where the S20.1 certificate says
nothing and something else must.

---

## 7. Follow-on lead (a LEAD, not a result): which moves preserve non-planarity?

Since `γ_N(T_n) = 0` forces `T_n`'s link planar (S15.1 + S20.1), **any move set under which
link non-planarity is invariant cannot connect a non-planar-linked presentation to `T_n`.**
That is the shape of a disproof — and it is exactly why nothing of the sort is available.
What this session can say about the move set:

| move | effect on link planarity | status |
|---|---|---|
| chord refinement (`S3`) | subdivision: **preserved in both directions** | **PROVED** (S3 Lemma S3′ + subdivision invariance) |
| generator splitting, S8's length-2 bigon `u g⁻¹` | `link(P)` is a **minor** of `link(P′)` (contract `{u−,g−}`, `{g+,u+}`) ⇒ non-planarity preserved **upward** | **PROVED at graph level** here; S8's own `[GAP-S8-1]` about the defect bookkeeping is untouched and unused |
| A6's length-3 SPLIT `t u v` | **destroys** non-planarity, ≈ 0.1–2 % of the time | **REFUTED** by §3.2's counterexample |
| AC1 (invert), AC3 (conjugate), AC4/AC5 | not analysed here | **open** |
| **AC2 (`rᵢ → rᵢrⱼ`)** | not analysed here; almost certainly not minor-monotone — AC2 rewrites relator *content*, which is precisely what `T-S8` says is the only thing that can pay | **open, and the reason the route cannot be closed** |

The honest summary: the one move family for which non-planarity is provably monotone (S8's
bigon split) is a **bookkeeping** move that `S8` already showed is monotone for `γ_N`
directly — so it buys nothing new — and the move that actually drives the cubic search
breaks the monotonicity. A move set that both preserves non-planarity *and* is rich enough to
be an AC-move set has not been exhibited, here or anywhere in this repo.

---

## 8. Status of every claim in this file

| # | claim | status | bounds `γ_N` from |
|---|---|---|---|
| S20.1 | `S` non-planar ⇒ `γ_N ≥ 1` | **PROVED** (§2.2), and it is the rule the repo's own deciders already implement (§2.3) | **BELOW** |
| — | `γ_N = 0 ⇒ S` planar (same statement, contrapositive) | **PROVED** | — |
| — | planar ⇏ `γ_N = 0` (one-directional) | **PROVED by witness**: AK(3) is planar (`K4`) with `γ_N = 2` | — |
| §0 | 945/945 `γ_N = 0` states planar, 0 violations, 0 uncertified | **MEASURED** (this session, certified embeddings) | — |
| §1 | planarity test agrees with `macro_rotations` on 15 named + 105 random graphs, 0 disagreements | **MEASURED** | — |
| S20.2 | non-planar link needs rank ≥ 3; rank 2 is always planar | **PROVED** (`K4` is planar); 0/300 random rank-2 states non-planar | — |
| §3.2 | A6's SPLIT can turn a non-planar link planar | **PROVED by explicit doubly-certified counterexample** (`K3,3` witness + verified sphere embedding, both states `γ_N = 2`) | — |
| §3.3 | escape rate 0.11 % / 0.41 % / 2.08 % on three corpora | **MEASURED** | — |
| §3.4 | chord refinement preserves planarity both ways | **PROVED**, given `S3` Lemma S3′ (audited) | — |
| §3.1 | S8's bigon split makes `link(P)` a minor of `link(P′)` | **PROVED at graph level** here; unused downstream | — |
| §4 | AK(3)'s link is `K4`, planar | **MEASURED + PROVED** (structural: 4 germs) | — |
| §4 | 100/100 rank-9 cubic roots planar | **MEASURED** | — |
| §5.1 | 97.5 % / 45.7 % / 88.7 % non-planar in the three pools | **MEASURED**; **NOT** a calibrated contrast (§5.1 caution) | — |
| §5.2 | `γ_N` × planarity table | **MEASURED**; the `γ_N = 0` row is forced by S20.1, not evidence for it | — |
| §6 | 331/1,958 (16.9 %) of `γ_N = 1` parents non-planar | **MEASURED** | — |
| §6 | 26,761/56,388 (47.5 %) of edges from `γ_N = 1` parents have a planar child; 0 reach `γ_N = 0` | **MEASURED** | — |
| §6 | planarity is **not** the mechanism of S17's empty `1 → 0` cell | **ESTABLISHED**, follows from the two rows above | — |
| §7 | AC2 / AC1 / AC3 / AC4 / AC5 vs non-planarity | **not analysed** — open | — |

---

## 9. What is NOT concluded

1. **The stable AC conjecture is not touched, in either direction.** Nothing here is
   evidence for or against it.
2. **The cubic route is not closed.** The brief's target — upgrading `S16`'s "0 creations in
   93,638" from a measurement to a theorem — **was not reached**, and the two reasons are
   independent and both fatal: AK(3)'s link is planar (§4), and SPLIT does not inherit
   non-planarity (§3.2). `S16` §4 and `S17` §6 stand exactly as written: instrument facts,
   not obstructions.
3. **`Γ(P) = min{γ_N(Q) : Q ~_st P}` is not bounded from below by anything here.** S20.1
   bounds a *single state's* `γ_N` from below. Since `T_n`'s link is planar and SPLIT can
   restore planarity, non-planarity is not invariant along the stable class, so it yields no
   lower bound on `Γ`. `S15` §6's "no monotone lower-bound quantity is known" is **not**
   overturned.
4. **`γ_N = 0` remains the *orientable* PL thickenability predicate** (`S3` R3/T-S9). S20.1
   inherits that restriction exactly: a non-planar link rules out orientable thickenings, and
   the non-orientable case is untouched.
5. **The 97.5 % vs 45.7 % non-planarity gap is not a result about AK(3)** (§5.1). Three
   source families, no matching, and `S16`'s retraction of exactly this style of comparison
   applies verbatim.
6. **No claim is made that non-planarity explains the empty `1 → 0` cell.** §6 measures the
   opposite.

---

## 10. Reproduce

```
python3 -m experiments.stable_ac.fable.s20_planarity_probe selftest --random 200
python3 -m experiments.stable_ac.fable.s20_planarity_probe ak3
python3 -m experiments.stable_ac.fable.s20_planarity_probe sweep      --sample 3000
python3 -m experiments.stable_ac.fable.s20_planarity_probe chains     --chains 300
python3 -m experiments.stable_ac.fable.s20_planarity_probe splitprobe --parents 60 --children 150
python3 -m experiments.stable_ac.fable.s20_planarity_probe s17
```

New artifacts (all under `results/stable_ac/fable/`): `s20_selftest.json`,
`s20_ak3_roots.json`, `s20_planarity_sweep.json`, `s20_chain_planarity.json`,
`s20_split_escape.json`, `s20_s17_planarity.json`. Every long run went through
`guarded_run.py` with a preflight on the same code path; no search was run and no search
node was spent — every state was read from a persisted artifact or replayed deterministically
from `root` + `trace` with the repo's own `split_apply`.
