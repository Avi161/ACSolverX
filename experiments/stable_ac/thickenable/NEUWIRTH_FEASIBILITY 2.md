# Neuwirth thickenability decision — feasibility memo (T7)

**Scope.** Feasibility only. Can we implement, on this project's CPU+python stack, a decision procedure "is the presentation 2-complex of a balanced 2-generator trivial-group presentation thickenable?", and use a positive answer as an Andrews-Curtis-triviality certificate for AK(3) / the 124 targets? Deliverable is this memo + a go/no-go. Sources are cited inline; where the original (Neuwirth 1968) was inaccessible I reconstruct from Lackenby's own summary and the modern rotation-system literature and say so.

**Sources actually read.** Lackenby, *The stable AC conjecture and thickenable group presentations*, arXiv:2606.06122v1 [math.GR], 4 Jun 2026 — full text via `literature/txt/lackenby_stable_ac_thickenable.txt` (§1, §2.5, §3.1–3.4, §5, §6.2 read directly). Neuwirth, *An algorithm for the construction of 3-manifolds from 2-complexes*, Proc. Cambridge Philos. Soc. 64 (1968) 603–613 — **paywalled; only the Cambridge Core abstract was obtained**, so the algorithm below is reconstructed from secondary sources, not from Neuwirth's text. Carmesin, *Embedding simply connected 2-complexes in 3-space, I (Kuratowski-type characterisation)* arXiv:1709.04642 and *II (Rotation systems)* arXiv:1709.04643 (Thm 1.1). Fulek & Kynčl, *Atomic Embeddability, Clustered Planarity, and Thickenability*, JACM 2022 / arXiv:1907.13086. Matveev, *Algorithmic Topology and Classification of 3-Manifolds* (special-spine / special-polyhedron theory) via secondary summaries. Regina 7.4.x API docs (`Triangulation3.isBall`/`isSphere`).

---

## (a) The decision problem for our objects

Fix a balanced 2-generator presentation `P = <x, y | r1, r2>` with `r1, r2` cyclically reduced words in `F(x,y)` and total length `|r1|+|r2| ≤ 25` (the T-track cap). Its **presentation 2-complex** `K` has exactly: one 0-cell `v`; two 1-cells, the loops `x` and `y`; two 2-cells (discs) `D1, D2` attached along the closed edge-paths spelled by `r1` and `r2`. `K` is a finite CW 2-complex, generally **not** simplicial (single vertex, loop edges). [Lackenby §1: "a cell complex K … with a single 0-cell, a 1-cell for each generator, and a 2-cell attached along the path specified by each relation".]

`P` is **thickenable** iff `K` embeds in some 3-manifold; then `K` has a regular neighbourhood `N(K)`, a compact 3-manifold with a handle structure (0-handle `v`, 1-handles `x,y`, 2-handles `D1,D2`) that deformation-retracts onto `K`. [Lackenby §3.1.] The **decision problem** is: *does such an `N(K)` exist?* — equivalently (Neuwirth's framing) *is `K` a spine of a compact orientable 3-manifold?*

**Why the answer matters (and how much).** Every state we will feed the checker is a balanced presentation of the **trivial group** (all 124 targets and AK(3) present the trivial group; AC moves preserve the group, so every state in an orbit does too). For a balanced trivial-group presentation, `χ(K) = 1 − 2 + 2 = 1`, `π1(K) = 1`, hence `H2(K) = 0` and `K` is **contractible**. Therefore if `K` is thickenable, `N(K)` is a contractible compact 3-manifold, which by Perelman's Poincaré conjecture is a **3-ball**. [Lackenby §3.1.] Two payoffs then fire immediately:

- **Thm 1.3 (unstable ACC):** "Any thickenable balanced presentation of the trivial group can be converted to a standard presentation using Andrews-Curtis moves." So *thickenable ⟹ the state is AC-trivial* — a positive settlement.
- **Thm 1.2 (stable bound):** `SAC(P) ≤ 2^(2^(cℓ²))`, `c = 2·10⁶` — an explicit (astronomically large, but finite) stable-move bound.

Consequence for AK(3): if **any** state reachable in AK(3)'s AC-orbit is thickenable, AK(3) is AC-trivial — resolving the decades-open case. This is the T7 escape mechanism: thickenability is a *certificate of trivialisability that is checkable without exhibiting the full AC path*.

**Payoff is one-sided — state this honestly.** A **negative** answer (a state is *not* thickenable) settles nothing. Lackenby's own reformulation (§1) is that stable-ACC is equivalent to "any balanced presentation of the trivial group can be converted into a *thickenable* one using stable AC moves"; you are allowed to pass through non-thickenable states, so non-thickenability of one state — even AK(3)'s own base complex — is not a counterexample and not a disproof. Only **positives** decide. The task's "major either way" should be read as "a positive is a major theorem; a negative is informative (it prunes) but not decisive." Do not oversell a negative.

---

## (b) The algorithm, as concretely as the sources allow

### What Neuwirth proved (from the abstract + Lackenby's use of it)

Neuwirth 1968 gives "necessary and sufficient conditions for the canonical 2-complex which corresponds to a group presentation to be a spine" of a connected closed orientable 3-manifold, and "an effective algorithm" that, by enumerating presentations, systematically attempts to build such a manifold. [Neuwirth 1968 abstract, Cambridge Core.] Lackenby uses it as a black box: "it is easily checked whether or not a group presentation is thickenable, via an algorithm of Neuwirth" (§1), and in §6.2 "determine whether it is thickenable, using the algorithm of Neuwirth … This algorithm also provides a thickening `N(K)`." **The paper gives no restatement of the algorithm's internals** — §6.2 only cites it. So the concrete content below is the *modern equivalent*, which is what one would actually implement.

### The combinatorial structure that is enumerated: link graph + rotation system

The modern, implementable form of "does `K` thicken" is the **rotation-system criterion** (Carmesin II, Thm 1.1): *a simply connected complex `C` embeds in `S³` iff `C` has a planar rotation system*; the more general "embeds in **some** orientable 3-manifold" (= thickenable) is the same local machinery with the global sphere condition relaxed, and is the object Fulek–Kynčl decide. The pieces:

- **Link graph `L` at the vertex `v`** ("Whitehead graph"). Vertices of `L` = the ends of edges at `v`. Each loop `x` contributes two vertices, written `x⁺, x⁻` (equivalently the four directed germs `x, X, y, Y`). Edges of `L` = the **disc corners**: reading each relator cyclically, every adjacent letter-pair `(a_i, a_{i+1})` is one corner, drawn as an arc joining the germ where `a_i` arrives to the germ where `a_{i+1}` departs. There are exactly `|r1|+|r2|` such arcs. This `L` is precisely the **Whitehead graph** of `{r1, r2}` — confirmed: "the Whitehead graph of a presentation is the link of the single vertex of the presentation complex, and it embeds in the link of the single vertex of the manifold; when the link of the vertex is the 2-sphere, the Whitehead graph has a planar embedding on this sphere." [search-confirmed statement of the presentation-complex link; consistent with Carmesin I/II.] The Whitehead graph is already a first-class object in this codebase's domain (Whitehead moves), so building `L` from `(r1, r2)` is a few lines.

- **Rotation system.** "A rotation system … consists of, for each edge `e` of `C`, a cyclic orientation `σ(e)` of the faces incident with `e`." [Carmesin II.] Concretely: for edge `x`, list the disc-corners running along `x` in the cyclic order in which they wrap the tube of the `x`-handle; likewise `y`. Equivalently this assigns a cyclic order to the arcs of `L` around each of its 4 vertices — i.e. a combinatorial embedding of `L` into a surface.

- **Acceptance condition (thickenable).** The rotation system must make the **vertex link a 2-sphere** (the link of a point in a 3-manifold is `S²`). Building the surface from `(L, σ)` by the closed-walk / face-tracing rule [Carmesin II: trace directed edges through the rotators to get the boundary walks] gives a surface of Euler characteristic `V − E + F`; accept iff that surface is a sphere (`χ = 2`, genus 0), **for a rotation `σ` that additionally satisfies the edge-consistency**: at the two ends `x⁺, x⁻` of a loop the induced rotators must be **reverses** of one another (Carmesin's "cyclic orientations at edge-vertices agree, with sign adjustments based on direction"). "Planar rotation system" = such a genus-0, edge-consistent `σ`. Embeds-in-`S³` (the strong form) additionally needs `L` itself planar plus simple connectivity — automatic for our contractible `K`.

> **[unverified — reconstructed]** The exact edge-consistency (which end reverses, and the treatment of a letter and its inverse in the same relator) is stated only in summary form in the sources I could read; it must be pinned against Regina before any positive is trusted. This is the load-bearing subtlety, and getting it wrong silently manufactures false certificates (see riskiest step).

### The key simplification for **2 generators**

`L` has exactly **4 vertices** (`x⁺, x⁻, y⁺, y⁻`). Every (multi)graph on ≤ 4 vertices is planar (`K5` needs 5 vertices, `K3,3` needs 6; parallel edges and loops never break planarity). **Therefore the planarity obstruction — the thing that makes general 2-complex embeddability NP-hard [Matoušek–Sedgewick–Tancer–Wagner, cited in Carmesin I] and drives Carmesin I's nine excluded minors — can never fire for a 2-generator presentation.** [derivation; solid graph theory, but flagged.] The entire thickenability question for our targets collapses to: *does an edge-consistent genus-0 rotation system on this fixed 4-vertex multigraph exist?* That is a finite check over the cyclic orders at 4 vertices (each of degree ≤ 25), brute-forceable outright.

Note this cuts both ways: because planarity of the link never fails here, non-planarity — the *easy* obstruction — is useless as a filter for us; every "no" must come from the rotation-consistency/genus computation, the harder-to-get-right part. And the converse warning from Carmesin I holds in general: **planarity of the link graph is necessary but not sufficient** — "there exists a simply connected 2-complex that is not embeddable in 3-space and has no [minor] with a non-planar link graph." So one cannot shortcut to "4 vertices ⟹ always thickenable"; the rotation computation is doing the real work.

### Complexity for our sizes

General 2-complex embeddability in `R³`: decidable, NP-hard [MSTW]. **Thickenability specifically (embeds in some orientable 3-manifold): polynomial time** [Fulek–Kynčl, JACM 2022, arXiv:1907.13086 — "thickenability can be tested in polynomial time"]. For **our** objects the size is trivial: 4 link-vertices, ≤ 25 arcs, 2 tube-rotations to choose. A naive enumeration of edge-consistent rotations is at worst on the order of `(deg!)` per vertex with `deg ≤ ~13`, and with the consistency constraint far less; sub-second per state, easily millions of states. Complexity is a non-issue; **correctness is the only hard part.**

---

## (c) The Matveev / special-spine alternative route

Matveev's theory (*Algorithmic Topology and Classification of 3-Manifolds*) works with **special polyhedra**: a simple 2-polyhedron is *special* if it has a true (4-valent) vertex, its singular graph is connected, and its 2-strata are open discs; a special polyhedron `P` is a *special spine* of `M` if `M∖P` is a ball (closed `M`) or `∂M × [0,1)` (with boundary). The homeomorphism type of a special spine determines `M` uniquely. **Crucially, "not all almost special (or even special) polyhedra are thickenable"** [Matveev; ScienceDirect, *A classification of 3-thickenings of 2-polyhedra*, S0166864198000364] — thickenability is a genuine restriction even after making the complex special.

Route: subdivide `K` to a special polyhedron, then apply a thickenability criterion phrased on the true-vertex links (each true vertex's link is a specified 4-vertex graph — the "butterfly"). **Assessment: not cleaner than the rotation-system route for us.** The subdivision inflates a length-≤25 complex into many strata and true vertices, and the local thickenability check at each true vertex is the same "does the link embed on `S²` consistently" computation, now replicated at every vertex with global gluing constraints — strictly more bookkeeping than the single 4-vertex link of the un-subdivided presentation complex. Its value is as a **cross-check** and as the natural bridge to Regina (special spines have a canonical dual triangulation, which Regina consumes), not as the primary decision procedure. **Recommendation: primary = rotation system on the 4-vertex Whitehead-graph link (§b); Matveev special spine = the encoder used to hand `N(K)` to Regina (§d).**

---

## (d) Full pipeline sketch and calibration-set design

Two logically distinct pipelines; the project needs both because they check each other.

**Pipeline A — the certificate (critical path).** `(r1, r2)` → build link graph `L` (Whitehead graph) → search for an edge-consistent genus-0 rotation system → **thickenable? yes/no**. For a known-trivial-group target, "yes" already yields *AC-trivial* by Thm 1.3, with no 3-manifold recognition required. This is the whole logical need. It is ~200 lines of pure python, no Regina.

**Pipeline B — the independent validator (mandatory, off the logical critical path).** From an accepted rotation system, construct `N(K)` explicitly as a handle decomposition / special-spine dual, triangulate `N(K)` (0-handle + two 1-handles + two 2-handles glued per the rotation and the relator words), cap `∂N(K)` (Lackenby §3.3: subdivide 2-cells to triangles, cone the boundary `S²` over a vertex avoiding length-1/2 cycles — Lemma 3.2) to a closed triangulation, and run **Regina `Triangulation3.isBall(N(K))`** (equivalently `isSphere` on the capped sphere). Rubinstein–Thompson 3-sphere/3-ball recognition [Lackenby §6.2, refs 27 Rubinstein, 30 Thompson]. Regina here is *not* needed to conclude triviality (Poincaré already gives ball) — it exists to **catch a wrong thickenability verdict** (Pipeline A bug) by independently confirming the topology of the object A claims to have built. Per the ESCAPE_PLAN verification rule ("any thickenable claim would need a second independent tool"), **no positive is announced on Pipeline A alone.**

**Where it plugs into the night's work.** T4's stall-escape emits plateau-leader states; T7 runs Pipeline A over that frontier as a certificate filter. A single "yes" (validated by B) on any frontier state of a target settles that target. This is exactly the "get far, then descend" payoff — except the "descent" is replaced by a topological certificate.

**Calibration set (design before trusting any verdict).**

| class | example | source / citation | expected verdict |
|---|---|---|---|
| thickenable, trivial | `<x,y \| x, y>` and `<x \| x>` (standard) | Lackenby §1 (standard is thickenable), §3.1 | YES → `N(K)` = 3-ball |
| thickenable, trivial, non-collapsible spine | Zeeman dunce-hat presentation `<x \| x²x⁻¹>` type spine of `B³` | classical (dunce hat is a spine of the 3-ball) | YES → `N(K)` = 3-ball |
| thickenable, **non**-trivial group (guards the "trivial" assumption) | a genuine 3-manifold spine, e.g. Lackenby §6.1 Heegaard example; or lens-space / `T³` standard spine | Lackenby §6.1; Matveev spine tables | YES → `N(K)` = that manifold (not a ball) |
| **not** thickenable (link non-planar) | cone over `K5` (or `K3,3`) — needs ≥3 generators so the link has ≥5 vertices | classical van Kampen/Flores obstruction; Carmesin I | NO |
| **not** thickenable, planar link (the hard near-miss) | a Carmesin I non-embeddable simply-connected complex "with no minor with non-planar link graph" | Carmesin I, arXiv:1709.04642 | NO |

The last two rows are the essential adversarial cases: the `K5`-cone confirms the code says NO when it must, and the Carmesin "planar link yet non-embeddable" example confirms the code does **not** shortcut to YES on planarity alone. Note the `K5` cone and Carmesin examples are **≥3-generator**, so they exercise Pipeline B's general-`n` path, not the 4-vertex 2-generator fast path; a purely 2-generator known-NOT-thickenable citeable example is not established in the literature I found — constructing one (by exhibiting a 2-generator relator pair whose only edge-consistent rotation has positive genus) is itself a useful sub-deliverable and a sharp test.

---

## (e) Effort estimate and the single riskiest step

**Effort (one competent person, this stack).**

- Phase 0 — environment: the default interpreter here is **Python 3.14.3, and Regina is not importable in it or in any python on this machine right now** (verified: `import regina` fails in system `python3`, the `ACSolverX/.venv`, and `python3.11`; no regina wheel for 3.14). A pinned **Python 3.12/3.13 venv + regina wheel** is required for Pipeline B. ~0.5 day.
- Phase 1 — Pipeline A (link-graph builder + edge-consistent genus-0 rotation checker, 2-generator): **2–3 days**.
- Phase 2 — calibration set + validation of A against hand-computed small cases: **2–3 days**.
- Phase 3 — Pipeline B (handle/special-spine → Regina triangulation encoder, cap, `isBall`): **4–7 days** — the fiddly part.
- **Minimal useful deliverable (Phases 0–2, checker + calibration, no Regina): ~1 person-week.** Fully validated A+B: **~2–2.5 person-weeks.**

**Single riskiest step: correctness of the thickenability criterion in Pipeline A — specifically the edge-consistency / genus computation of the rotation system.** It is riskiest not because it is slow (it is instant) but because a subtle sign or consistency error produces a **false positive**, and a false positive here does not fail loudly — it *silently prints a proof that AK(3) is AC-trivial.* That is the worst possible failure mode for this project (a wrong major claim). Mitigation is non-negotiable and is exactly why Pipeline B is mandatory: every accepted state must have its `N(K)` independently built and confirmed a genuine 3-ball by Regina, and the calibration set must include the two adversarial NO-cases before any target is run. The `[unverified]` tag on the consistency rule in §b stays until Regina agreement is demonstrated on the full calibration set.

---

## (f) Go / no-go

**GO — scoped, and with the validator treated as mandatory rather than optional.**

Rationale: (1) the core decision (Pipeline A) is small, pure CPU+python, and fits the stack with zero new heavy infrastructure; complexity is a non-issue for `|r1|+|r2| ≤ 25` (poly-time in general [Fulek–Kynčl], trivial for 4-vertex links). (2) The upside is uniquely high: it is *the only T-track lever that can positively settle AK(3) or a target*, via a certificate that needs no explicit AC path. (3) It composes directly with T4's frontier.

Guardrails that make it a GO rather than a trap: (i) build it as a **certificate filter over search-frontier states**, not a standalone solver — its value is entirely in finding one thickenable state; (ii) **never announce a positive on Pipeline A alone** — gate behind Regina's independent `isBall` on a separately-constructed `N(K)`, plus a hand audit, per the ESCAPE_PLAN two-independent-tools rule; (iii) internalise the **one-sided payoff** — a negative on any single state (including AK(3)'s base complex) is inconclusive, so success is "found a thickenable frontier state", never "proved something is not thickenable"; (iv) fix the Python-3.12/3.13-plus-Regina-wheel environment first (Regina is not currently importable here). Under those guardrails the expected cost to a *usable* checker is ~1 person-week, and the risk (false positive) is fully contained by the mandatory validator.

---

## (3) Proof-of-concept: the criterion is simple enough to write down

Because the 2-generator link graph is a fixed 4-vertex object, Pipeline A is genuinely short. Pseudocode (decision only):

```
# Thickenability of <x,y | r1, r2>, r1,r2 cyclically reduced.  [unverified consistency rule]
def link_graph(r1, r2):
    # vertices: 'x+','x-','y+','y-'  (directed germs; 'x-' == germ of X, etc.)
    # one arc per corner of each cyclic relator word
    arcs = []
    for r in (r1, r2):
        w = list(r); m = len(w)
        for i in range(m):
            a, b = w[i], w[(i+1) % m]     # consecutive letters (cyclic)
            arcs.append((arrive_germ(a), depart_germ(b)))
    return arcs                            # multigraph on {x+,x-,y+,y-}

def is_thickenable(r1, r2):
    L = link_graph(r1, r2)                 # always planar (4 vertices)
    for sigma in edge_consistent_rotations(L):   # loop-reversal at x+/x-, y+/y-
        S = trace_boundary_walks(L, sigma)       # faces F of the vertex-link surface
        V, E, F = 4, len(L), num_walks(S)
        if V - E + F == 2:                 # genus 0  <=>  vertex link is S^2
            return True, sigma             # -> thickenable; hand to Regina to confirm N(K)=B^3
    return False, None
```

`edge_consistent_rotations` enumerates cyclic orders of the arcs at each of the 4 germs subject to: the rotator at `x+` is the reverse of the rotator at `x-` (and same for `y`). `trace_boundary_walks` follows each directed arc to the next per the rotators; `F` = number of closed walks. Accept on the first genus-0, edge-consistent choice.

### Hand-verification on `<x, y | x, y>`

This is the presentation the task names. Its relators have **length 1**, which is the degenerate case for the raw link-graph checker: a length-1 relator `"x"` contributes a single self-corner (the only adjacent pair is `x,x` cyclically), so `L` has multi-arcs/half-loops and the rotation enumeration is ill-posed. The honest hand-check is therefore the **handle/collapse argument**, which is rigorous and is exactly Lackenby's Lemma 3.1 mechanism:

- `K` = one vertex + loops `x, y` + discs `D1` (along `x`) and `D2` (along `y`). Topologically `K` = a wedge of two discs (each loop bounds its disc), hence **contractible**.
- Thicken: vertex → 0-handle `B³`; each loop → a 1-handle; each disc → a 2-handle. Disc `r1 = x` is a 2-handle running over the single 1-handle `x` **once** — a **cancelling 1-handle/2-handle pair** [Lackenby §3.1: "a relation of length 1 … corresponds to a 2-handle that runs over a single 1-handle; we can collapse these two handles"]. Same for `r2 = y`. Cancelling both pairs against the 0-handle leaves just `B³`.
- **Therefore `<x,y | x, y>` is thickenable, and `N(K) = B³` (a 3-ball); `∂N(K) = S²`; `K` is a spine of the 3-ball.** Regina would confirm `isBall(N(K)) = True`. Consistent with Thm 1.3 (it is trivially AC-trivial: two length-1 relators trivialise directly).

So the required hand example resolves **YES, thickens to the 3-ball** — and it simultaneously exposes that length-1/2 relators must be pre-collapsed (Lackenby Lemma 3.1: reduce to relators of length ≥ 3 first) before the raw rotation checker is meaningful. That pre-collapse is a required front-end step of Pipeline A and belongs in the build. A non-degenerate worked example (e.g. AK(3): `r1 = x y x Y X Y`, `r2 = xxxx YYY`, total length 13, 4-vertex link with 13 arcs) is exactly the intended first real input, but its verdict is for the implemented+Regina-validated checker to pronounce, not for hand computation — precisely because the consistency rule is the `[unverified]`, false-positive-prone step.

---

**Bottom line.** GO on a scoped build: Pipeline A (thickenability certificate) is small, CPU+python, and for 2 generators reduces to an edge-consistent genus-0 rotation check on a fixed 4-vertex Whitehead graph — poly-time in theory, instant in practice. Its payoff is one-sided but uniquely high (a single positive on any orbit-frontier state settles that target, AK(3) included, via Lackenby Thm 1.3). The one real hazard is a false positive from a wrong consistency rule silently "proving" AK(3); it is fully contained only by making Regina's independent `N(K)`-is-a-3-ball check mandatory, which in turn requires a Python 3.12/3.13 + regina-wheel venv (Regina is **not** importable in this machine's current Python 3.14). Riskiest single step: getting the rotation-system consistency/genus criterion exactly right.

---

## Regina validator groundwork (2026-07-21)

**Environment claim above is superseded — corrected here.** Regina 7.4.1 ships prebuilt macosx_11_0_arm64 wheels for cp311, cp313, **and cp314**, and all three were pip-installed and exercised successfully on this machine in throwaway venvs; the earlier claim that "Regina is not importable in this machine's current Python 3.14" was wrong, and no pinned 3.12/3.13 venv is required — `pip install regina` works directly against this machine's default `python3` (3.14.3, the same version as `ACSolverX/.venv`).

**Working recipe (verbatim, reproducible from any writable directory):** `python3.14 -m venv <dir>/regina_venv && <dir>/regina_venv/bin/pip install regina` then `<dir>/regina_venv/bin/python -c "import regina; t = regina.Example3.figureEight(); print(t.isValid(), t.homology())"` prints `True` and `Z`; this was verified identically for `python3.14`, `python3.13`, and `python3.11` (Homebrew `/opt/homebrew/bin/python3.13`/`python3.14`, and `/Users/avigyapaudel/.local/bin/python3.11`), all pulling `regina-7.4.1-cp3{11,13,14}-cp3{11,13,14}-macosx_11_0_arm64.whl`; `import regina` cost ~1.5-1.6s cold on every version tested, and there is no functional difference across the three — recommend just using `python3.14` (matches the project's existing `.venv` interpreter, one fewer moving part).

**Verified API calls (validation-relevant surface).** `Triangulation3.isBall()` and `Triangulation3.isSphere()` exist directly as documented methods and both run on the triangulation *as-is*, with its real boundary — no manual `hasBoundary` + `simplify` + `recognizer` dance and no manual "capping" of boundary spheres is needed before calling `isBall()`; the docstring states `isBall()` is "based on `isSphere()`" (Rubinstein 3-sphere recognition + Jaco-Rubinstein 0-efficiency prime decomposition) and both carry the standard warning that the underlying normal-surface-theory algorithms can be slow on larger triangulations, with `knowsBall()`/`knowsSphere()` available to check for a cached/fast-path answer. Confirmed positive and negative cases, all sub-millisecond at this trivial scale: `regina.Example3.ball().isBall() == True` (0.0002s), `regina.Example3.threeSphere().isSphere() == True` and `regina.Example3.sphere().isSphere() == True` (both ~0.0001s), and as a sanity negative `regina.Example3.figureEight().isBall() == False` (the ideal figure-eight-knot-complement triangulation, which has torus boundary and is not a ball). Manual construction was also verified end to end: `t = regina.Triangulation3()`, `a = t.newTetrahedron()` (a dimension-specific alias of `newSimplex()`), and `a.join(facet, other_simplex, regina.Perm4(...))` (the method is `join`, not `joinTo`) — gluing all four facets of two fresh tetrahedra together pairwise via the identity `Perm4()` reproduces the standard two-tetrahedron triangulation of `S^3` and `isSphere()` returns `True` on it (0.0001s); a single `newTetrahedron()` with zero gluings has one boundary component and `isBall()` returns `True` on it directly (0.0002s), confirming boundary facets left unglued are read correctly as manifold boundary with no extra capping step. No higher-level shortcut constructor was found for going from a rotation system / ribbon graph / group presentation straight to a marked handle-attached triangulation: `regina.Example3.handlebody(genus)` exists but returns an arbitrary minimal *layered* triangulation with no control over which boundary curves correspond to which meridians; `regina.Handlebody` is a `Manifold`-classification wrapper (`genus`, `homology`, `construct()`) for census/recognition use, not a curve-specifying builder; `regina.GroupPresentation`/`HomGroupPresentation` are abstract Tietze-transformation objects with no 3-manifold-construction role; and no `spine`/`ribbon`/`fatgraph`/`pachner`-named constructor exists anywhere in the `regina` namespace. Conclusion: `N(K)` has to be hand-built tetrahedron-by-tetrahedron via `newTetrahedron()`/`join()`/`Perm4`, there is no scaffolding to lean on.

**Pipeline sketch (pseudocode, using only the API names verified above).** (1) 0-handle: `t = regina.Triangulation3()`; build a small triangulated ball with enough distinct boundary triangles to serve as 4 disjoint "germ discs" (`+x`,`-x`,`+y`,`-y`) — a bare `t.newTetrahedron()` only exposes 4 boundary facets total, exactly enough for the degenerate case, so in general this ball needs subdividing (more tetrahedra, still all `newTetrahedron()`+`join()` internally, one facet of each left open per germ) until the 4 marked discs sit in the cyclic order that Pipeline A's accepted rotation system specifies around the vertex link. (2) two 1-handles (tubes) for `x` and `y`: each a small triangulated `D^2 x I` (a handful of `newTetrahedron()`s glued into a prism-like solid), with its two end facets `join()`-ed via an explicit `regina.Perm4` onto the `+g`/`-g` germ discs on the 0-handle boundary — this is the load-bearing translation step: the abstract rotation-system coupling in `check_thickenable.py` ("rotation at `-g` = reverse(pairing-image of rotation at `+g`)") has to be converted into a concrete `Perm4` per gluing, and that translation is itself new, unverified, correctness-critical code, not yet designed below the pseudocode level. (3) after step 2, the result `H` should be a genus-2 handlebody; sanity-check independently via `H.isValid()` and `H.homology()` (expect free rank 2, `Z+Z`, comparable to but not identical in triangulation to `regina.Example3.handlebody(2)`). (4) two 2-handles for `r1`, `r2`: each attaches along an annular neighbourhood of the closed curve on `boundary(H)` spelled out letter-by-letter by the relator word, tracing exactly the same germ "corners" Pipeline A already computes (`arcs` / `trace_boundary_walks` in `check_thickenable.py`); realising that curve as a normal curve in a (probably re-subdivided) triangulation of `boundary(H)` and then inserting a strip of new tetrahedra (the thickened disc) and `join()`-ing each of its boundary triangles one at a time along the strip is the single most labor-intensive, least off-the-shelf part of the whole pipeline — expect it to be machine-generated per letter of the relator by a script, not hand-authored. (5) once both 2-handles are attached, call `isValid()`, then `isBall()` directly on the resulting triangulation with no separate capping pass — per the verified finding above, `isBall()` already handles genuine boundary correctly, so if the construction is right and `K` really is contractible with a single 2-sphere boundary component, `N(K).isBall()` should just return `True`; the "cap the boundary" language elsewhere in this memo describes Lackenby's abstract topological argument (Lemma 3.2), not a required Regina preprocessing step.

**Honest effort estimate (revises §e Phase 0 and Phase 3 above).** Phase 0 (environment) collapses from the memo's original 0.5 day to effectively **0** — Regina installs cleanly into the project's own default Python 3.14 with a single `pip install regina`, no pinned interpreter needed. Phase 3 (Pipeline B, the `N(K)` triangulation encoder) should be revised **upward** from the memo's 4-7 days to a more honest **6-10 days**: there is no ribbon-graph/handle/presentation-to-triangulation shortcut anywhere in Regina's API (confirmed above by direct inspection, not assumption), so every tetrahedron of the 0-handle, both 1-handles, and both 2-handles has to be placed and `join()`-ed by hand-written (likely per-relator-letter, script-generated) code, and the rotation-system-to-`Perm4` translation in step (2) above is new design work with no precedent in the codebase to build from. None of this changes the go/no-go in §f — Pipeline A is unaffected and remains the critical path — but it does mean Pipeline B should not be scheduled as a quick validation pass; it is a genuine second implementation project of comparable weight to Pipeline A itself.
