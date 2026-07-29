# R8 — The fake-surface complexity of AK(3)

STATUS: AUDITED. This document has been through an independent adversarial audit this
session (all `AUDIT AMENDMENT` blocks below). Most claims are CONFIRMED, several
strengthened with new independent verification; specific items are REFUTED or downgraded
— most seriously §6 Conclusion 3's search-rank advice, which had the bound direction of
Theorem D backwards (Amendment 5), and the A1 converse, which is refuted with an explicit
witness (Amendment 4). Claims addressed are tagged per lemma; the headline quantity
`c(AK(3))` is a **stable-AC** invariant, so unless a lemma says otherwise it addresses the
STABLE claim. No claim about AC-triviality of AK(3) is made in either direction.

**What you may build on (post-audit).** Theorem A1 forward, now verified on all 102,092
(surface, spanning tree) pairs in *reduced* form with its proof gap closed (Amendments
2–3); Theorem A2; Theorem C's reverse half and the `c = 1` case (dependency-free);
Corollary C1; the headline BLOCKED verdict (CONFIRMED, ROBUST, no FQW input needed at its
core); D1, D2, Theorem D and the formulas `n' = L − 2n`, `V₀ = L − 2n − 1`; `Q₈` as an
existence witness in AK(3)'s stable class with the complexity-8 profile (no move list);
D3 correctly labelled CONJECTURED; §6's four filter counts; the JSON targets as faithful
tree-collapses of the CSV on 5,389/5,389 (Amendments 6–9).

**What you may NOT build on.** The A1 converse (REFUTED with explicit witnesses,
Amendment 4); §6 Conclusion 3's original "search at rank ≈9, not rank 4-6" advice
(REFUTED on bound direction — Theorem D is an upper-bound witness, not a lower bound; the
rank 4-6 programme is restored, Amendment 5); Theorem C's numeral 6 taken as
unconditional (it is exactly as strong as FQW's real threshold and no stronger —
Amendment 6); "the chain is explicit and machine-checked" for D1 (D1 is an existence
claim with no computed move count, Amendment 7); "25 substitutions" (the correct count is
23, Amendment 7); "c(AK(3)) < ∞" as proved (Amendment 8); "8 is optimal for the method"
beyond rank 2 (rests on a carried-in citation absent from `LITERATURE_STATUS`, Amendment
8); "the" tree-collapse presentation in §2.4 as unique (only "some" tree-collapse is
established — but W3 IS load-bearing in Theorem C's forward half, Amendment 8).

Instrument: `experiments/stable_ac/fable/r8_complexity_profile.py` (new file; four
self-checking blocks A–D, all PASS). Primary sources retrieved this session are cached
under `literature/fake_surfaces/` (gitignored — `git add -f` to track).

---

## 0. Verdict up front

Define, for a balanced presentation `P` of the trivial group,

> **c(P) = min { complexity(F) : F a contractible cellular fake surface whose
> tree-collapse presentation is stably AC-equivalent to P }.**

(Well defined by §2.4. "Cellular" is the conservative choice: it is the class the census
and the profile theorem are about, and shrinking the candidate class can only raise the
minimum, so the upper bound in §5.2 is conservative and the dichotomy in §5.1 is
unaffected.)

Then:

| quantity | value | status |
|---|---|---|
| c(AK(3)) lower bound | `c(AK(3)) ≥ 1`, and `c(AK(3)) ≥ 6` **iff** AK(3) is not stably AC-trivial | **PROVED modulo FQW's body** (Thm C) — the numeral 6 is exactly as strong as FQW's real threshold and no stronger; audited, Amendment 6 |
| c(AK(3)) exact, positive branch | `c(AK(3)) = 1` **iff** AK(3) is stably AC-trivial | PROVED (Thm C) — dependency-free, audited CONFIRMED |
| c(AK(3)) upper bound | `c(AK(3)) ≤ 8` | CONJECTURED (Thm D + unproved realizability) |
| c(AK(3)) finite at all | `c(AK(3)) < ∞` | **NOT PROVED** — audit downgrade, §3.1; was "PROVED modulo one sourced theorem" |

**So c(AK(3)) ∈ {1} ∪ {6,7,8,…}, and deciding which is *literally* the open problem.**
Fagan–Qiu–Wang's complexity < 6 theorem therefore **does not settle AK(3)**, and it
cannot: "c(AK(3)) ≤ 5" is not a *sufficient condition* for AK(3) to be stably AC-trivial,
it is a *restatement* of it. This is R3's Wall 5 (the min-realization tautology) again,
now sharpened from R3's "min-complexity < 6 ⟺ stably AC-trivial" to the exact value
`1`, and given an explicit non-tautological companion (Theorem D).

What *is* new and non-tautological: an explicit, verified stable-AC chain carrying AK(3)
to a presentation with the exact numerical profile of a **complexity-8** contractible
cellular fake surface (§5.2), plus a sharp profile theorem (§2.2) that turns "is this
state a census presentation?" into an O(length) test and explains R6's zeros
mechanically (§6).

---

## 1. Verified definitions

**1.1 Fake surface.** *A compact polyhedron P is a fake surface if the link of each of
its points is homeomorphic to one of: (1) a circle; (2) a circle with a diameter; (3) a
circle with three radii.*
[SOURCED-INDIRECT: search-engine synthesis of arXiv:math/9703211 and arXiv:2406.09439 —
the pages themselves are proxy-blocked, see §7]. Type (1) points are surface points,
type (2) points are triple-line points (the local model is `Y × R`, three half-planes on
a line), type (3) points are **true vertices** (local model = cone over the complete
graph `K₄`; "circle with three radii" *is* `K₄`, 4 vertices all of degree 3).

**1.2 Singular graph.** *The union of the singular points (vertices and triple lines) of
a fake surface P is its singular graph SP. The type-1 singularities form a 4-regular
multigraph.* [SOURCED-INDIRECT, same].

> **AUDIT AMENDMENT (mislabel).** "The type-1 singularities form a 4-regular multigraph"
> mislabels the source synthesis — type-1 points are *surface* points (§1.1), not
> singularities. What is 4-regular is **the singular graph `SP` itself** (vertices = true
> vertices, edges = triple lines), consistent with §1.3's convention-PDF confirmation.

**Special polyhedron:** *a fake surface with at
least one vertex, all of whose 2-components are 2-cells* [SOURCED-INDIRECT: Matveev, via
the same synthesis]. **Cellular fake surface:** *every edge is a 1-cell and every face is
a 2-cell* [SOURCED-INDIRECT: arXiv:2406.09439]. Cellular ⊂ special, and the census is of
cellular ones.

**1.3 Complexity = number of true vertices — CONFIRMED, from a primary artifact.**
*"The complexity of a cellular fake surface F is defined as the number of vertices"*
[SOURCED-INDIRECT: arXiv:2406.09439], and independently and decisively from the census's
own convention document, which is on disk:
> *"Viewing the 1-skeletons as 4-regular multigraphs … For a given 1-skeleton of
> complexity n, we choose the adjacency matrix A = (a_{i,j}) and therefore an ordering of
> the vertices that maximizes D(A) … We then label edges from 1 to 2n."*
[SOURCED: `literature/fake_surfaces/Surface_presentation_convention.pdf`, p.1 — PRIMARY,
cloned from github.com/lucasfagan/Fake-Surfaces this session]. Complexity `n` ⇒ the
1-skeleton has `n` vertices and `2n` edges. The project's record of
"complexity = number of true vertices" is **correct**.

**1.4 The FQW theorem.** *"The stable Andrews-Curtis conjecture is equivalent to the
conjecture that every contractible fake surface is 3-deformable to a point. We prove that
every contractible fake surface of complexity less than 6 is 3-deformable to a point by
induction."* [SOURCED: arXiv:2412.12293 abstract, verbatim, already held in-repo]. Title
and authors confirmed this session: *Stable Andrews–Curtis Conjecture via Fake Surfaces
and Zeeman Conjecture*, Lucas Fagan, Yang Qiu, Zhenghan Wang; v2 dated 2026-01-08.

**1.5 Two corrections to the project's picture of the census** (both PRIMARY-sourced):

* The census README says: *"the classification of acyclic cellular fake surfaces of
  complexity 1-4 and **a partial classification of complexity 5: surfaces without small
  disks**"* [SOURCED: `literature/fake_surfaces/Fake-Surfaces_README.md`, PRIMARY]. So the
  514 complexity-5 rows are **not** all complexity-5 surfaces — only those with no face of
  boundary length 1 or 2. R6 and `certified_trivial_targets.json` describe the set as "the
  census of complexity 1–5"; that is a completeness claim the source does not support. It
  does *not* affect soundness of the targets (see next point), only coverage.
* The census is of **acyclic** surfaces; FQW's theorem is about **contractible** ones, and
  their companion paper proves *"the contractibility conjecture for acyclic cellular fake
  surfaces of complexity 4"* [SOURCED-INDIRECT: arXiv:2406.09439] — i.e. acyclic ⇒
  contractible is a theorem only up to complexity 4. For a census row to be a legitimate
  stably-trivial target one needs π₁ = 1 (acyclic + simply connected ⇒ contractible, by
  Hurewicz + Whitehead). The project has that for the **457 rows** where Todd–Coxeter
  completed at index 1, not for all 5,389. The word "certified" in
  `certified_trivial_targets.json` should be read as covering 457 rows; the remaining
  4,932 are *candidate* targets.

> **AUDIT AMENDMENT (CONFIRMED).** Independent of the group-triviality coverage question
> above, the audit verified that the JSON targets are faithful tree-collapses of the CSV
> census on **5,389/5,389** rows — i.e. the presentation-construction pipeline itself
> (surface → spanning tree → presentation) introduces no discrepancy anywhere in the
> census, regardless of which rows are certified-trivial.

**1.6 3-deformation ↔ stable AC (the dictionary that makes any of this transfer).**
A 3-deformation is a formal deformation through complexes of dimension ≤ 3. The
statements in force here:

* (W1) Two finite 2-complexes are 3-deformation equivalent iff their presentations are
  related by Q\*\*-transformations = AC1–AC3 together with (de)stabilization AC4/AC5.
  [SOURCED-INDIRECT: attributed to P. Wright, *Formal 3-deformations of 2-polyhedra*,
  Proc. AMS 37 (1973) 305–308; the search index also returns *"For the trivial group, the
  SAC equivalence class of a presentation is the same as its EAC equivalence class, a
  result from Wright 1975"*. Neither paper was readable this session.]
* (W2) Consequently: **`P` is stably AC-trivial ⟺ `K(P)` 3-deforms to a point.** This is
  exactly the form FQW use — *"every contractible 2-complex 3-deforms to a point"* is the
  topological spelling of the stable AC conjecture [SOURCED-INDIRECT].
* (W3) A connected 2-complex 3-deforms to the presentation complex obtained by collapsing
  a maximal tree of its 1-skeleton. (Standard; the mapping-cylinder argument needs one
  extra dimension, and dim = 2 + 1 = 3, which is why *3*-deformations are the right
  notion.) [UNVERIFIED against a source this session; used in Thm C.]

**Do not blur the three claims.** Every lemma below is tagged. `c(·)` is a function of the
**stable** class only.

---

## 2. The forward dictionary: surface → presentation

### 2.1 The counts (PROVED here; machinery, no AC claim)

Let `F` be a contractible cellular fake surface of complexity `V ≥ 1`. Then `SF` is
4-regular with `V` vertices and `2V` edges (§1.3), each edge carries exactly 3 face-germs
(the triple-line condition), and each vertex has exactly 6 face-corners (`K₄` has 6
edges). `F` is connected, hence its 1-skeleton `SF` is connected, hence a spanning tree
`T` has `V − 1` edges. With `f` faces, `χ(F) = V − 2V + f = f − V = 1`, so `f = V + 1`.
Collapsing `T` (a 3-deformation, W3) gives

* generators: `2V − (V−1) = V + 1`,
* relators: `f = V + 1` (balanced),
* total length: `3·2V − 3(V−1) = 3V + 3`.

Matches the project's derivation exactly. **Confirmed.**

### 2.2 Theorem A1 (SHARP PROFILE) — new, and strictly stronger than "length 3V+3"

> **In the tree-collapse presentation of a contractible cellular fake surface of
> complexity `V`, every generator occurs exactly 3 times** (counting a letter and its
> inverse alike). Hence `V+1` generators, `V+1` relators, total length `3V+3`.

*Proof (original).* Generators are exactly the non-tree edges of `SF`; every edge of `SF`
carries exactly 3 face-germs, and collapsing `T` deletes only tree letters, leaving each
non-tree edge with its 3 occurrences. ∎ (Class: machinery.) This argument is correct for
the **raw spelling** of the tree-collapse word only.

> **AUDIT AMENDMENT (a real proof gap, now closed).** The original proof stops at raw
> spelling, but every downstream use of A1 (the §6 filter, the R3 correction of §4) is
> applied to **freely reduced** words, and free reduction can take an occurrence count
> from 3 to 1 while leaving exponent sums — hence homology and `|det|` — untouched. This
> gap mattered: at complexity 8 no census data exists to check against, and the
> raw-spelling proof was all there was. **Repair, verified on the data:** a cancellation
> would require two mutually inverse non-tree letters separated only by tree letters; the
> intervening letters trace a closed walk in the spanning tree `T`, which must contain a
> backtrack; a backtrack in an attaching map is a corner joining an edge-germ to itself,
> i.e. a loop in the vertex link — impossible in `K₄`. Both hypotheses were checked
> directly against the data: **0/5,389** rows contain a backtrack, and **5,389/5,389**
> satisfy the `K₄`-corner condition (each vertex's 6 corners are the 6 distinct pairs of
> its 4 germs, each exactly once). With this sentence added, A1 holds in **reduced** form
> for all `V` — including complexity 8, where the raw-spelling argument was previously the
> only thing behind Theorem D's target profile (§5.2).

*Verification:* block A of `r8_complexity_profile.py` checks the full statement — `V+1`
generators, `V+1` relators, every generator exactly `3×`, length `3V+3` — on
**5,389/5,389** census rows (one spanning tree each). PASS.

> **AUDIT AMENDMENT (CONFIRMED, strengthened).** The audit re-parsed the census with its
> own tokenizer, reconstructed each singular graph **intrinsically** from disk boundary
> walks (union-find on the `4V` edge-ends, not relying on the upstream convention PDF),
> and enumerated **every** spanning tree — **102,092** (surface, spanning tree) pairs
> versus the document's 5,389 (one tree each); tree counts per surface range from **1 to
> 125**. Results: **0** profile failures on raw spelling, **0** on freely reduced, **0** on
> cyclically reduced, **0** empty relators; `V` vertices / 4-regular / connected on
> **5,389/5,389**; `|det| = 1` on all **102,092** pairs. The profile holds for **every**
> spanning tree, not only the one the script picks.

This is much sharper than the length profile. On the AK(2)+z corpus the length test
`L = 3n` admits 5,880 members and the occurrence test admits 48 — a 122× tightening (§6).

### 2.3 Theorem A2 (complexity 1 is AC-trivial, unstably) — removes an FQW dependency

There are exactly two census rows at complexity 1, and by A1 a **rank-2 census
presentation can only come from complexity 1** (rank = V+1). Both are AC-trivial, with no
stabilization, in the composite chains below — **5 and 7 elementary moves respectively**
under FRAMING's numbering [AUDIT AMENDMENT: corrected from "three moves each" for both;
the 3 composite steps shown each expand to several elementary AC1-AC5 moves; the
correction is cosmetic and does not affect any claim]:

| presentation | chain | result |
|---|---|---|
| `⟨a,b \| baaBA, b⟩` | `r₁→r₂⁻¹r₁`, `r₁→a⁻¹r₁a`, `r₁→r₁r₂` | `⟨a,b \| a, b⟩` |
| `⟨a,b \| bbaBa, a⟩` | `r₁→r₁r₂⁻¹`, `r₁→b⁻¹r₁b`, `r₁→r₁r₂⁻¹` | `⟨a,b \| b, a⟩` |

[Block B, both replayed, PASS.] (Class: **AC-trivial** — of those presentations; nothing
is claimed about AK(3) here.) Consequently the "c = 1" branch of Theorem C below does
**not** depend on FQW at all.

### 2.4 `c(·)` is well defined (PROVED; machinery)

Different spanning trees of the same `F` give different presentations, but all of them are
3-deformation equivalent to `F` (W3) and hence, by W1/W2, mutually stably AC-equivalent.
So "the tree-collapse presentation of `F`" is well defined up to stable AC-equivalence and
`c(P)` does not depend on any tree choice.

> **AUDIT AMENDMENT (downgrade — not load-bearing, weakened to "some").** This section
> rests on two unread sources, W1 and W3 (§1.6, §7). It is **not load-bearing**: replace
> "the tree-collapse presentation of `F`" by "**some** tree-collapse presentation of `F`"
> and every claim in this document survives unchanged — §0's definition of `c(P)` already
> quantifies over `F`, so uniqueness across spanning trees of one `F` is not needed.
> **Caution:** this does **not** mean W3 is dispensable in general — W3 **is** load-bearing
> in Theorem C's forward (⇒) half (§5.1: "by W3 `F ≃₃ K(P_F)`"), which is exactly the step
> that makes the numeral 6 FQW-conditional (Amendment 6).

---

## 3. The reverse dictionary: presentation → surface

### 3.1 What is sourced

> *"Because every 2-complex can be 3-deformed into a fake surface, it suffices to
> demonstrate that all contractible fake surfaces can be 3-deformed to a point"*
[SOURCED-INDIRECT: search-engine synthesis of arXiv:2412.12293's own text].

This is the reverse direction, and it is what makes `c(P) < ∞` for every `P`. It is also
the *only* thing about the reverse direction that could be sourced this session.

> **AUDIT AMENDMENT (downgrade — "c(AK(3)) < ∞" is NOT proved).** The §0 table's "PROVED
> modulo one sourced theorem" status for finiteness does not hold up: finiteness over
> **cellular** surfaces needs a **cellular** version of "every 2-complex 3-deforms to a
> fake surface", and that refinement is not what the quoted sentence states — the
> sentence itself is a search-engine synthesis, not a primary-sourced read (§7), and the
> census/FQW results in force here are about *cellular* fake surfaces specifically
> (§1.2). The §0 table's fourth row now reads **NOT PROVED**. Nothing else in this
> document depends on finiteness; note that "shrinking the candidate class can only raise
> the minimum" (§0's own framing) cuts **against** this row, not for it — a narrower,
> unproved existence claim does not become easier to prove by restricting the class.

### 3.2 What is NOT determined by what could be sourced

**The construction behind that sentence, and therefore its cost in true vertices, could
not be obtained.** I could not read FQW, Wright, Ikeda (*Acyclic fake surfaces*, Topology
10 (1971) 9–36), or Matveev's book; every scholarly host is blocked (§7). So:

* there is **no sourced bound** of the form "a presentation with `n` generators and total
  length `L` 3-deforms to a fake surface of complexity ≤ g(n,L)";
* the honest statement is: **the reverse dictionary's complexity cost is not determined by
  what I could source.** What would determine it: the proof of "every 2-complex 3-deforms
  to a fake surface" (FQW §2 or its source), read for the vertex count of the
  specialization procedure.

### 3.3 What the reverse direction must look like (PROVED here; machinery)

The un-collapse is fully constrained combinatorially, which is why the profile theorem is
usable in reverse. Given a candidate presentation with `n` generators, `n` relators and
every generator occurring exactly `3×` (so length `3n`), realizing it at complexity
`V = n − 1` means splitting the single wedge vertex into `V` four-valent vertices by
inserting `V − 1 = n − 2` tree edges, each occurring 3 times. The bookkeeping closes
exactly:

* vertices `n−1`, edges `n + (n−2) = 2n−2 = 2(n−1)` ✓ 4-regular (`4(n−1) = 2(2n−2)`) ✓
* face length in edges `3n + 3(n−2) = 6n−6 = 6V` ✓ = 6 corners per vertex ✓

and the one remaining condition is local: **at each vertex the 6 corners must realize the
6 distinct pairs of its 4 germs, each exactly once** (that is the `K₄` link). That
condition is not implied by the profile.

### 3.4 The profile is necessary but NOT sufficient (PROVED here; machinery)

Block D and its complexity-2 extension enumerate all presentations with the census
profile that present the trivial group, modulo the full census symmetry group (relabel
generators, invert generators, rotate/invert relators, permute relators):

| profile | profile-admissible + trivial group | realized by a fake surface |
|---|---|---|
| complexity 1 (2 gens, 2 rels, each gen 3×) | **2** | **2** (census, complete) |
| complexity 2 (3 gens, 3 rels, each gen 3×) | **79** | **≤ 68** (17 census surfaces × at most 4 spanning trees each) |

At complexity 1 the profile is exactly sufficient. At complexity 2 it is not: the census
is complete at complexity 2 and a 2-vertex 4-regular multigraph has at most 4 spanning
trees, so at most `17 × 4 = 68 < 79` classes are realizable — **at least 11
profile-admissible trivial-group presentations are the tree-collapse of no complexity-2
contractible cellular fake surface.** Hence any upper bound obtained by exhibiting a
profile-correct presentation is a *candidate*, not a theorem.

> **AUDIT AMENDMENT (converse REFUTED, with explicit witness — strengthens the point above
> 4.5×).** The audit's independent enumeration gives the **exact** figures, replacing the
> `≥ 11` / `≤ 68` estimates: **79** profile-admissible-and-trivial classes at complexity 2,
> **29** realized (not merely `≤ 68`), **50** unrealized (not merely `≥ 11`). Explicit
> witness: `⟨a,b,c | A, AAB, BCBcc⟩` (relators `a⁻¹`, `a⁻²b⁻¹`, `b⁻¹c⁻¹bc²`) — 3
> generators, 3 relators, every generator exactly 3 times, total length 9, cyclically
> reduced, Todd–Coxeter index 1 **complete** — and its canonical class is none of the 29
> realized by the 38 (surface, tree) pairs of the 17 complexity-2 census surfaces. Since
> the acyclic-cellular census is complete at complexity 2 and contractible ⇒ acyclic, it
> is the tree-collapse of **no** complexity-2 contractible cellular fake surface. Four
> further witnesses: `['A','AAB','BCCbc']`, `['A','AABBCCb','C']`, `['A','AABBCbC','C']`,
> `['A','AABBCbc','C']`.

---

## 4. The arithmetic obstruction, resolved

The question posed: total length `3V+3` with `V+1` relators has no solution at AK(3)'s
`(2, 13)`, and `13 + k = 3(2 + k)` gives `k = 3.5`, so no plain stabilization of AK(3)
lands on the profile either. Is that (a) a need for length-changing AC moves, (b) an
artifact of the spanning-tree collapse, or (c) something else?

**Answer: (a), and the profile is not an artifact — but the framing "obstruction" is
wrong, and the arithmetic in the project's current write-up is wrong.**

1. **The profile is a theorem, not an artifact.** §2.1–2.2: `3V+3` is forced for *every*
   spanning tree of *every* contractible cellular fake surface, and the sharper "every
   generator exactly 3×" is forced too. So (b) is ruled out.
2. **Pure stabilization can never reach it.** `13 + k = 3(2+k) ⇒ k = 3.5`. The user's
   arithmetic is correct and this is worth recording as a permanent fact about AK(3).
3. **But total length is not an AC invariant, so no length profile can obstruct
   anything.** AC2 (`rᵢ → rᵢrⱼ`) changes total length by an arbitrary amount. There is no
   obstruction here at all — only a statement about where the *target set* lives.
4. **CORRECTION to `R3_INVARIANT_LANDSCAPE.md` §R5 and, by inheritance, to R6.** R3 states:
   *"the numeric profile … is reachable from AK(3) by pure stabilisation bookkeeping — 4
   AC4 moves plus an AC1 give a 6-generator, length-18 presentation, exactly the
   complexity-5 profile."* Under the project's own move numbering (FRAMING §1: AC1 =
   invert, length-preserving) that sentence is **false**: 4 × AC4 gives `(n,L) = (6,17)`
   and AC1 cannot change 17 to 18. The intended move is **AC2** (multiply by one of the
   fresh stabilizer relators), which does give `(6,18)`. More importantly, even the
   repaired sentence proves less than it claims: `(6,18)` matches the *length* profile but
   **not** the sharp profile — the occurrence vector there is
   `a:7, b:7, p:2, q:1, r:1, s:1`, and a census presentation needs `3,3,3,3,3,3`. Four
   stabilizations plus one multiply do **not** produce "exactly the complexity-5 profile".
5. **What actually reaches the profile:** seven Tietze generator-additions, landing at
   rank 9 / complexity-8 profile (§5.2). Not rank 6.

So the crux of turning R6 from a heuristic into a decision procedure is not the length
arithmetic; it is (i) the sharp profile as an admission filter, and (ii) the rank at which
AK(3)'s stable class can first meet the profile, which is 9 by the canonical construction,
far above the ranks R6 searched.

> **AUDIT AMENDMENT (internal cross-reference).** "The rank at which AK(3)'s stable class
> can first meet the profile, which is 9" repeats the bound-direction error refuted in
> Amendment 5 (§6, Conclusion 3): rank 9 is where *this construction* lands, an upper
> bound / witness, not a proven first-meeting rank. Read this sentence with that
> correction; ranks 4-6 are not excluded.

---

## 5. Bounds on c(AK(3))

### 5.1 Theorem C (the dichotomy) — PROVED modulo FQW's body

*(The `c = 1` half is dependency-free — see the AUDIT AMENDMENT after Corollary C2 below.)*

> **`c(AK(3)) = 1` if AK(3) is stably AC-trivial; `c(AK(3)) ≥ 6` otherwise.**
> Equivalently `c(AK(3)) ≤ 5 ⟺ AK(3) is stably AC-trivial`.

*Proof.* (⇐, giving `c = 1`.) If AK(3) is stably AC-trivial then it is stably
AC-equivalent to every stably AC-trivial presentation, in particular to the complexity-1
census presentation, which is AC-trivial by Theorem A2 — no FQW input needed. And
`c ≥ 1` because a special polyhedron has at least one true vertex by definition (§1.2),
so `c(AK(3)) = 1`.
(⇒.) Suppose some contractible cellular fake surface `F` with `complexity(F) ≤ 5` has
tree-collapse presentation `P_F` stably AC-equivalent to AK(3). By FQW (§1.4) `F`
3-deforms to a point; by W3 `F ≃₃ K(P_F)`; so `K(P_F)` 3-deforms to a point; by W2 `P_F`
is stably AC-trivial; by transitivity so is AK(3). ∎
(Class: **stably AC-trivial**. Dependencies: FQW §1.4 for the `≥ 6` half; W2/W3 for the
transfer; the `= 1` half is dependency-free given A2.)

**Corollary C1 (why the lower-bound side is hopeless as stated).** No unconditional lower
bound `c(AK(3)) ≥ 2` can be proved without *disproving* stable AC-triviality of AK(3),
since `c ≥ 2` already implies `c ≥ 6` implies not stably AC-trivial. This is R3's Wall 5
in its sharpest form: the minimum is `1`, not merely "< 6".

> **AUDIT AMENDMENT (headline BLOCKED verdict — CONFIRMED and ROBUST).** Corollary C1,
> together with §6 Conclusion 1 below, is this document's headline verdict that the naive
> low-rank search route for a *lower* bound on `c(AK(3))` is BLOCKED: any such attempt
> either fails outright or proves stable-AC-non-triviality, and this qualitative
> conclusion needs **no FQW input at all** — it follows from A1 + A2 alone (the exact
> numeral it cites, 6, is FQW-conditional per Amendment 6, but the blocking argument
> itself — "any `c ≥ 2` is already as hard as disproving stable triviality" — does not
> change if the true FQW threshold turns out to be a different `N₀`; see the degradation
> table after Corollary C2). CONFIRMED, ROBUST.

**Corollary C2 (what extending the census would and would not do).** Proving FQW's
induction at complexity `V` for all `V ≤ N` settles AK(3) **iff** `c(AK(3)) ≤ N`. Pushing
the census from 5 to 6 therefore settles AK(3) only in the lucky case `c(AK(3)) = 6`. The
right named target is `N ≥` an *independently established* upper bound for `c(AK(3))` —
which is what §5.2 is for.

> **AUDIT AMENDMENT (Theorem C CONFIRMED as a conditional theorem).** The numeral 6 is
> exactly as strong as FQW's real threshold and no stronger; the table label "PROVED" in
> §0 and §8 for this result must read **PROVED modulo FQW's body**. Hard measurement of
> the complexity-5 gap behind this (§1.5: the census is a "partial classification of
> complexity 5: surfaces without small disks"): **0 of 514** complexity-5 census rows have
> a small disk (min face length ≥ 3), while **4,587 of 4,618** complexity-4 rows (99.3%)
> and **236 of 238** complexity-3 rows do — so if FQW's complexity-5 induction step rests
> on the enumeration, the missing stratum is, by the complexity-4 pattern, the
> overwhelming majority of complexity-5 surfaces.
>
> **Degradation table** (what happens to Theorem C if FQW's real proven threshold differs
> from "complexity < 6"):
>
> | if the real induction covers | negative branch reads | equivalence becomes |
> |---|---|---|
> | complexity < 6, as published | `c(AK(3)) ≥ 6` (this document, unchanged) | `c(AK(3)) ≤ 5 ⟺` stably AC-trivial |
> | complexity ≤ 4 plus complexity-5-without-small-disks | `c(AK(3)) ≥ 5`; if `c(AK(3)) = 5` the realizing surface must have a small disk | `c(AK(3)) ≤ 4 ⟺` stably AC-trivial |
> | complexity ≤ N₀ in general | `c(AK(3)) ≥ N₀ + 1` | `c(AK(3)) ≤ N₀ ⟺` stably AC-trivial |
>
> Cellularity is the **safe** direction: `c` minimizes over cellular surfaces, so a
> cellularity hypothesis on FQW's theorem leaves the forward half (⇐, the `c=1` direction)
> intact in every case above. **In every row, the reverse half (`c=1`), Corollary C1, and
> the headline BLOCKED verdict are unaffected, because Theorem A2 makes them
> dependency-free. Only the numeral 6 is at risk.**
>
> **Source re-check.** The audit re-sourced FQW's abstract **verbatim** this session from
> a fresh sparse clone of `github.com/MystenLabs/snowreads` (`data/abs/2412.12293.json`),
> and this document's §1.4 quote is exact — but that snapshot knows only **v1** (created
> 16 Dec 2024), corroborating **neither** this document's "v2 dated 2026-01-08" **nor**
> `LITERATURE_STATUS`'s "2026-01-09" (which differ from each other). **Mark the v2 date as
> unsourced.** `arXiv:2406.09439` is **not** in the mirror, so the [SOURCED-INDIRECT]
> definitions in §§1.1/1.2/1.5 remain unsourced this session; §1.3 does **not** need it
> (`V` vertices / `2V` edges / 4-regular confirmed from the data itself).

### 5.2 Theorem D (the profile normal form) — PROVED, and the source of the upper bound

**Lemma D1 (Tietze generator-addition is a stable AC move — elementary, no Wright, no
automorphism principle).** Let `P = ⟨X | R⟩` be a balanced presentation of the **trivial
group** and `w ∈ F(X)`. Then `P` is stably AC-equivalent to `⟨X, z | R, z⁻¹w⟩`.
*Proof.* AC4 gives `⟨X,z | R, z⟩`. Because the group is trivial, `w` lies in the normal
closure of `R`, so `w = Π_k u_k r_{j_k}^{ε_k} u_k⁻¹`. Right multiplication of one relator
by a conjugate `u r_j^{ε} u⁻¹` is the AC composite (AC3 on `r_j`; AC2; AC3 back), which
leaves `r_j` restored. Apply AC1 to the relator `z` to get `z⁻¹`, then multiply through by
those conjugates in order to reach `z⁻¹w`. ∎
(Class: **stably AC-trivial**-preserving. The triviality hypothesis is essential and is
satisfied here.)

**Lemma D2 (substitution).** If `ρ = z⁻¹g` is a relator, replacing one occurrence of `g`
in another relator `r = u g v` by `z` yields `r·(v⁻¹ρ⁻¹v)`, and replacing one occurrence
of `g⁻¹` in `r = u g⁻¹ v` by `z⁻¹` yields `(uρu⁻¹)·r`. Both are AC2∘AC3 composites.
[Block C verifies this identity as an exact free-group equation at every one of the
**23** substitutions performed. AUDIT AMENDMENT: corrected from an original miscount of
"25"; D2's two identities were re-verified algebraically in general and at every
substitution.]

**Theorem D.** Let `P` be a balanced presentation of the trivial group with `n`
generators, total length `L`, in which every generator occurs at least 3 times. Then `P`
is stably AC-equivalent to a balanced presentation with

> `n' = L − 2n` generators, `n'` relators, total length `3n'`,
> **every generator occurring exactly 3 times** — the exact profile of a contractible
> cellular fake surface of complexity `V₀ = L − 2n − 1`.

*Proof.* Repeatedly pick a generator `g` occurring `d ≥ 4` times, adjoin a fresh `z` with
relator `ρ = z⁻¹g` (D1) and move `d − 2` occurrences of `g` onto `z` (D2). After the step
`g` occurs `3×` and `z` occurs `(d−1)×`; each step costs `+1` generator and `+2` length,
so the invariant `Δ = 3n − L` rises by exactly 1 per step and the process stops precisely
when `Δ = 0`, after `s = L − 3n` steps. ∎

**For AK(3)** (`n = 2`, `L = 13`, occurrences `a:6, b:7`): `s = 7`, `n' = 9`,
`V₀ = 8`. The presentation bookkeeping and every D2 identity are machine-checked
(block C, PASS); the chain reaching `Q₈` below:

```
AK(3) = ⟨a,b | aaaBBBB, abaBAB⟩
  ↓ 7 Tietze splits (a:6→3, b:7→3, cascading through c,d,e,f,g,h,i)
Q₈ = ⟨a,b,c,d,e,f,g,h,i |  aacBBDD,  cfeFEH,  Ga, Hb, Gc, Id, Ge, If, Ih ⟩
     9 generators, 9 relators, total length 27, every generator exactly 3×,
     Todd–Coxeter over the trivial subgroup completes at index 1 (trivial group).
```

`Q₈` is, as far as this project knows, the first presentation ever exhibited in AK(3)'s
stable class that satisfies the *necessary* profile of a census surface.

> **AUDIT AMENDMENT (Q8 / Lemma D1 CONFIRMED, with two overstatements removed).** The
> audit's independent rebuild reproduces `Q₈` character-for-character:
> `['aacBBDD','cfeFEH','Ga','Hb','Gc','Id','Ge','If','Ih']`, 9 generators / 9 relators /
> length 27, every generator exactly 3 times, all cyclically reduced; Todd–Coxeter index 1
> **complete** — after validating the project's `coset_enum` on a 6-case ladder: standard,
> Z, Z/2, AK(3), AK(3)+z. A **second, independent certificate**: eliminating the 7 short
> relators by hand gives `a=c=e=g` and `b=d=f=h=i` and returns **exactly**
> `AK(3) = ⟨g,i | g³i⁻⁴, gigi⁻¹g⁻¹i⁻¹⟩` — so `Q₈`'s triviality is **inherited** from AK(3),
> not new; the Todd–Coxeter run is a **bug-catcher**, not a load-bearing step, and it is
> **not** evidence of stable AC-equivalence (that rests on D1/D2's algebra, checked
> separately). Lemma D1 is correct and is exactly the anticipated repair: plain AC4
> (adjoin `z` with relator `z`), AC1 on it, then right-multiplication by conjugates of the
> other relators (AC3-AC2-AC3, restoring the conjugated relator), reaching `z⁻¹w`. The
> trivial-group hypothesis is genuinely used, at exactly one point (`w` lies in the normal
> closure of `R`), and survives the induction because each iterate still presents the
> trivial group.
>
> **Two overstatements removed:**
> (i) *"The chain is explicit and machine-checked"* — D1 is an **existence** claim and
> needs no bounded move count, and it has none; the move count would be the length of an
> expression of `w` as a product of conjugates, which the script never computes. What
> **is** machine-checked is the presentation bookkeeping and every D2 identity (reflected
> in the wording above). Under R6's own rule ("any match requires an explicitly
> reconstructed AC1-AC5 move list"), `Q₈` does **not** yet have one.
> (ii) *"25 substitutions"* was wrong; the correct count is **23** (fixed above).
>
> **One more step D3 needs, made explicit.** A realization of the profile is
> automatically **contractible**, not merely a fake surface: `π₁ = 1` (it presents `Q₈`'s
> trivial group), `χ = 1` so `b₂ = 0` so acyclic, and Hurewicz plus Whitehead give
> contractible. This closes a gap Corollary D3 otherwise leaves implicit.

**Sharpness of the method at rank 2.** `V₀ = L − 2n − 1` is minimized by short
presentations. If AK(3) is **not** stably AC-trivial then no rank-2 member of its stable
class has length < 13: such a member would be a 2-generator balanced presentation of the
trivial group of length ≤ 12, hence AC-trivial (Havas–Ramsay [SOURCED-INDIRECT; already
in FRAMING §1]), hence stably AC-trivial, hence so would AK(3) be. So `V₀ ≥ 8` for this
construction at rank 2 — in the only case where the question is live, 8 is optimal for the
method. Starting from AK(3)+`z` (`n=3, L=14`) is worse, not better: `z` occurs once, and
raising it to 3 occurrences costs 2 length, giving `(3,16)` and `V₀ = 9`.

> **AUDIT AMENDMENT (downgrade — "optimal" narrowed to rank 2).** The Havas–Ramsay
> "length ≤ 12" citation behind the rank-2 argument above is carried in from FRAMING §1
> and is **absent from `LITERATURE_STATUS`** — it was not independently re-sourced this
> session. The rank-2 argument itself stands (`V₀ ≥ 8` *for a rank-2 construction*,
> conditional on that citation), but **"8 is optimal for the method" is not established
> beyond rank 2**: the audit scanned all 171,842 AK(3)+z members and found **157,979**
> with every generator occurring at least 3 times and **min `V₀ = 9`** — consistent with 8
> being unreachable by any other rank, but **not a proof**.

**Corollary D3 (CONJECTURED).** `c(AK(3)) ≤ 8`, provided some presentation in AK(3)'s
stable class with the complexity-8 profile is realizable as an actual contractible
cellular fake surface. §3.4 shows the profile alone does not guarantee this, so this is a
conjecture, not a theorem.

**Corollary D4 (the concrete named target).** *If* `c(AK(3)) ≤ 8`, then **extending FQW's
induction from complexity < 6 to complexity ≤ 8 settles AK(3) outright** — either every
contractible fake surface up to complexity 8 3-deforms to a point (⇒ AK(3) stably
AC-trivial) or one of them does not (⇒ the stable AC conjecture is FALSE). "Extend the
census to complexity 6" is the right *shape* of next target but very possibly the wrong
*number*; 8 is the number this construction supplies.

---

## 6. Consequences for the R6 search programme (actionable)

Applying the sharp profile as an admission filter to the corpora already on disk:

| corpus | members | passes `L = 3n` | passes SHARP profile |
|---|---|---|---|
| AK(3) classical class | 124,296 | **0** | **0** |
| AK(3)+z stable class | 171,842 | **0** | **0** |
| AK(2) classical class (positive control) | 13,040 | 12 | **8** |
| AK(2)+z stable class (positive control) | 27,350 | 5,880 | **48** |

Three conclusions:

1. **R6's zeros are explained mechanically and were unavoidable.** Not one harvested
   AK(3) state even satisfies the *arithmetic* precondition for being a census
   presentation, while both AK(2) controls contain states that do. The meet-in-the-middle
   was not measuring distance to the target set; at those ranks it could not have hit it.
2. **The rank-2 and rank-3 targets were self-defeating.** A rank-2 census presentation has
   complexity 1 and is AC-trivial (Thm A2), so a rank-2 match *is* a proof that AK(3) is
   AC-trivial; a rank-3 match needs total length 9 against AK(3)+z's 14. Matching at low
   rank is not a shortcut to the answer, it is the answer.
3. **Use the sharp profile, not the length profile, as the filter** (122× tighter on the
   AK(2)+z control). Note the census does not reach complexity 8, so any pay-off there is
   not a match against existing targets but a realizability construction (§3.3) — the
   local `K₄`-corner condition is the only thing left to satisfy.

   > **AUDIT AMENDMENT — REFUTED ON BOUND DIRECTION (the highest-priority correction in
   > this document).** This conclusion originally continued: *"and search at rank ≈ 9,
   > not rank 4–6: that is where Theorem D says AK(3)'s stable class first meets the
   > profile."* **That is refuted.** Theorem D **exhibits** a rank-9 profile-correct
   > member of AK(3)'s stable class — an **upper** bound on the first rank at which the
   > class meets the profile, i.e. a witness, not a lower bound. Nothing in R8 forbids a
   > sharp-profile member at rank 4, 5 or 6: §4's `k = 3.5` argument rules out only *pure
   > stabilization*, and AC2 changes length freely, so a shorter profile-correct member of
   > the stable class is not excluded by anything proved here. Worse, the original advice
   > ran **backwards** relative to this document's own Theorem C: a surface-backed match
   > at complexity ≤ 5 (rank ≤ 6) gives `c(AK(3)) ≤ 5`, which by Theorem C **proves AK(3)
   > stably AC-trivial using FQW as published** — no extension needed — whereas a match at
   > complexity 8 (rank 9) proves **nothing** until FQW's induction is extended to 8
   > (itself conditional on the unproved D3).
   >
   > **Corrected conclusion: rank 9 is where THIS CONSTRUCTION lands; ranks 4-6 remain the
   > only band where a realized match settles AK(3) outright.** This document's original
   > §6 advice retired R6's rank 4-6 search programme in error. **That programme is
   > restored.** The complexity-8 realizability construction (§3.3, the `K₄`-corner
   > condition) remains worth pursuing as a second, independent route toward Corollary
   > D3/D4, but it is not a substitute for the rank 4-6 search and must not be advised as
   > one.

---

## 7. What could not be sourced

Network reality this session (measured, not assumed): **every outbound HTTP request via
`curl` returns 000 and every `WebFetch` returns 403** — arxiv.org, export.arxiv.org,
ar5iv, semanticscholar, escholarship, researchgate, msp.org, huggingface, openreview, all
of them. **`git clone` from github.com works** and **`WebSearch` works**, returning
search-engine *syntheses* of page content — useful, but a synthesis is not a verbatim
read, and everything tagged [SOURCED-INDIRECT] above rests on one.

Retrieved as PRIMARY (on disk, `literature/fake_surfaces/`, gitignored — `git add -f`):
census `README.md`, `Surface_presentation_convention.pdf`, `check_contractibility.sage`,
plus `fakesurfaces.csv`, `fakesurfaces_cla_6.py`, `generate_one_skeleta.py`,
`ordered_one_skeletons.pdf` in the clone.

Not obtained, and each is a live dependency:

* **arXiv:2412.12293 full text.** Still open: whether the complexity < 6 theorem is stated
  for all fake surfaces or only cellular ones; the exact form of the equivalence; and —
  the one that matters most for this document — the construction behind "every 2-complex
  can be 3-deformed into a fake surface" and its cost in true vertices. Reading that
  proof would convert Corollary D3 from CONJECTURED to a theorem with an explicit bound
  (possibly worse than 8, but proved).
* **Wright, *Formal 3-deformations of 2-polyhedra* (Proc. AMS 37 (1973) 305–308)** and
  Wright 1975 — W1/W2, the dictionary everything transfers through.
* **Ikeda, *Acyclic fake surfaces*, Topology 10 (1971) 9–36**; **Matveev,
  *Algorithmic Topology and Classification of 3-Manifolds***; **Matveev 1987**, *Zeeman's
  conjecture for unthickened special polyhedra is equivalent to the Andrews–Curtis
  conjecture*, Siberian Math. J. (title confirmed by search; text unread).
* **W3** (collapse a maximal tree ⇒ 3-deformation) — standard, but unverified against a
  source this session.

**Two literature notes worth propagating.**
(i) A search-engine synthesis of FQW returns: *"In the case of contractible fake surfaces
that are embeddable in 3-manifolds, the Zeeman conjecture is equivalent to the
3-dimensional Poincaré conjecture, and therefore holds. In the case of contractible fake
surfaces that are not embeddable in 3-manifolds, the Zeeman conjecture is equivalent to
sACC."* This is FQW's own statement of the thickenability split and it corroborates R1's
thickenability route from a second, independent direction. It also means any construction
that realizes `K(AK(3))` as a *spine of a 3-manifold* would prove AK(3) stably AC-trivial
outright — so the fake surface realizing AK(3) must be non-thickenable, and any proposed
"build it inside a 3-manifold" construction is automatically either wrong or a proof.
(ii) The published (Elsevier) abstract of Lisitsa arXiv:2501.18601 still asserts that
AK(3) *"is stably AC-equivalent to the trivial presentation"*; every search engine returns
that claim first. FRAMING trap 1 is correct and this document does not rely on it.

---

## 8. PROVED / CONJECTURED / OPEN

**PROVED (this document, machine-checked where marked; audit status per lemma below).**

* **A1** Sharp profile: tree-collapse presentation of a contractible cellular fake surface
  of complexity `V` has `V+1` generators, `V+1` relators, and *every generator occurs
  exactly 3 times* (hence length `3V+3`). 5,389/5,389 (one tree each); audited on
  **102,092/102,092** (surface, spanning tree) pairs, **in reduced form**, with the raw
  vs. reduced proof gap closed (Amendments 2–3). *Class: machinery.*
* **A2** *Both* complexity-1 census presentations — hence every rank-2 census target — are
  **AC-trivial**, unstably, in 5 and 7 elementary moves respectively (corrected from
  "3 moves each" — Amendment 7); both chains independently replayed. *Class: AC-trivial
  (of those presentations — nothing about AK(3)).* AUDIT: CONFIRMED.
* **§2.4** `c(·)` is independent of the spanning tree used to collapse. *Class: machinery.*
  AUDIT: downgraded — not load-bearing, rests on unread W1/W3; read as "some" tree-collapse
  (Amendment 8). W3 itself remains load-bearing in Theorem C's forward half.
* **C** `c(AK(3)) = 1` if AK(3) is stably AC-trivial, `≥ 6` otherwise; equivalently
  `c(AK(3)) ≤ 5 ⟺ AK(3) stably AC-trivial`. *Class: stably AC-trivial. Depends on FQW +
  W2/W3 for the `≥ 6` half only.* AUDIT: **PROVED modulo FQW's body** — the numeral 6 is
  exactly as strong as FQW's real threshold and no stronger; the `c = 1` / reverse half is
  dependency-free and CONFIRMED (Amendment 6).
* **D1/D2/D** AK(3) is stably AC-equivalent to `Q₈` (9 generators, 9 relators, length 27,
  every generator exactly 3×, trivial group certified by Todd–Coxeter at index 1); general
  formula `n' = L − 2n`, `V₀ = L − 2n − 1`. *Class: stably AC-equivalence (an edge, not a
  triviality claim).* AUDIT: CONFIRMED, independently rebuilt character-for-character, with
  a second certificate (hand-elimination reduces `Q₈` back to AK(3) exactly); this is
  **existence only, no explicit move list** — "the chain is explicit and machine-checked"
  is a removed overstatement (Amendment 7).
* **§3.4** The census profile is necessary but not sufficient: **79** profile-admissible
  trivial-group presentations at the complexity-2 profile, **29** realized, **50**
  unrealized (audited exact figures, superseding "≥ 11" — Amendment 4), with an explicit
  witness `⟨a,b,c | A, AAB, BCBcc⟩` and four further witnesses. *Class: machinery.* AUDIT:
  REFUTED as a converse, CONFIRMED as a non-sufficiency result, strengthened 4.5×.
* **§4** Pure stabilization of AK(3) never meets the profile (`k = 3.5`); R3 §R5's
  "4 AC4 + AC1 ⇒ exactly the complexity-5 profile" is false as written and false in
  substance. *Class: machinery / correction.*
* **§6** Zero of 296,138 harvested AK(3)-class states meets even the length profile, vs 8
  and 48 sharp-profile states in the two AK(2) controls. *Class: negative search evidence,
  not a proof of anything about AK(3).* AUDIT: the four filter counts (124,296 / 171,842 /
  13,040 / 27,350 members; 0/0/12/5,880 length-profile; 0/0/8/48 sharp; 122× tightening)
  reproduced exactly. Conclusion 3's "search at rank ≈9, not rank 4-6" is **REFUTED on
  bound direction** — see Amendment 5; the rank 4-6 programme is restored.

**CONFIRMED BY INDEPENDENT ADVERSARIAL AUDIT (this session) — consolidated.** So the
document's remaining strength is legible: A2; Theorem C's reverse half and the `c = 1`
case (dependency-free); Corollary C1; the headline BLOCKED verdict (CONFIRMED and
ROBUST — its core needs no FQW input at all); D1, D2, Theorem D and the formulas
`n' = L − 2n`, `V₀ = L − 2n − 1`; `Q₈` as a member of AK(3)'s stable class with the
complexity-8 profile (existence only, no move list); Corollary D3 / `c(AK(3)) ≤ 8`
correctly labelled CONJECTURED; §6's four filter counts, reproduced exactly; and the JSON
targets verified as faithful tree-collapses of the CSV on 5,389/5,389.

**CONJECTURED.**

* **D3** `c(AK(3)) ≤ 8`. Needs: a complexity-8 contractible cellular fake surface whose
  tree-collapse presentation lies in AK(3)'s stable class — i.e. an un-collapse of `Q₈`
  (or of any profile-correct member of the class) satisfying the `K₄`-corner condition at
  all 8 vertices. AUDIT: correctly labelled CONJECTURED, CONFIRMED; note (Amendment 7)
  that a realization of the profile is automatically contractible (`π₁ = 1`, `χ = 1` so
  acyclic, Hurewicz + Whitehead), which closes a step D3 otherwise left implicit.
* **D4** Extending FQW's induction to complexity ≤ 8 settles AK(3) (conditional on D3).

**OPEN (unchanged by this document).**

* Is AK(3) stably AC-trivial? Equivalently (Thm C) is `c(AK(3)) = 1`?
* Is the profile-plus-corner realization problem for `Q₈` solvable? (Finite, well-posed,
  and the single most concrete unblocked computation this route offers.)
* What is the true complexity cost of the reverse dictionary — i.e. the vertex count of
  the "every 2-complex 3-deforms to a fake surface" construction? **Not determined by
  anything I could source.** Determining it requires reading FQW §2 or its source.

---

## 9. Artifacts

* `experiments/stable_ac/fable/r8_complexity_profile.py` — blocks A–D, all PASS (new file).
* `literature/fake_surfaces/` — primary census sources (gitignored; `git add -f`).
* Corpus filter counts in §6 reproduce from the on-disk `results/stable_ac/fable/*.jsonl*`.
* Upstream clone: `git clone https://github.com/lucasfagan/Fake-Surfaces.git`.
