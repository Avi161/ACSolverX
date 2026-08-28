# W6: rank-three thickenability is available in theory — and the W5 §5 target, as spelled, is the rank-two question again

Date: 2026-08-28 · Lane: `fable/proofs` · Status: **feasibility study — one decisive
structural negative, one genuinely new open object, zero positives**

Checker: `checkers/rank3_link_graph.py` (three modes, all guarded, all green).
Run records: `checkers/out/w6_controls.json`, `w6_link_graphs.json`,
`w6_ac_ball_c{16,18,20,22}.json`.

```bash
python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- \
  python3 fable/proofs/checkers/rank3_link_graph.py controls      # 29 PASS, 0 FAIL
python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- \
  python3 fable/proofs/checkers/rank3_link_graph.py targets
python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- \
  python3 fable/proofs/checkers/rank3_link_graph.py ball --ceiling 20 --pops 1000 \
    --ball-genus-budget 200000
```

---

## 0. The four answers in one paragraph

**(a)** The theory gate is **OPEN — rank-general**, on this repo's own records; there
is no rank-2 restriction anywhere in them, and the repo has already shipped a
rank-3 thickenability certificate that invokes Lackenby Thm 1.3 at rank 3.
**(b)** The object is the 6-germ occurrence link graph with the Neuwirth genus
potential `γ_N`; the *criterion* is unchanged and rank-general, but **none of the
four certified rank-2 solver families applies at rank 3** (they are hard-wired to
4 germs), and the one certified rank-3 family (`K6 − E(P5)`) is rigid in a way the
targets are not. **(c)** Two of the three targets are **decided NEGATIVE — and by
the rank-2 machinery, because a bare `z` row is thickenability-inert** (Lemma W6.1
below). The third, `Tpub`, is the only genuinely rank-3 object and is undecided by
everything that exists. **(d)** The rank-3 AC ball around `(AK3, z)` **closes** under
the 1,000-pop law at total-length ceiling ≤ 20 (503 canonical states) and
**0 of those 503 lie in any certified family**; at ceiling 22 it stops closing
(≥ 1,868 states) and coverage is 24/1,868 ≈ 1.3 %.

---

## 1. (a) THEORY GATE — rank-general, with exact citations

**Verdict: the thickenability ⇒ AC-triviality theorem is stated for balanced
presentations of the trivial group with no restriction on the number of
generators.** The lane may proceed to rank 3. Evidence, all from this repo:

| record | what it says | rank restriction? |
|---|---|---|
| `literature/proofs/AK3_NEUWIRTH.md`, "Scope and exact inputs" | fixes `P = ⟨g₁,…,g_n \| w₁,…,w_n⟩`, any `n`; the whole occurrence dictionary (`A`, `B`, `C`, `\|C\| = 2n`) is written for general `n` | **none** |
| same, **Theorem 2** ("Euler-only Neuwirth criterion") | `K_P` embeds in an orientable PL 3-manifold ⟺ some compatible ordering satisfies `(E)`, ⟺ `γ_N(P) = 0` | none on rank; **one hypothesis: the link graph is connected** |
| same, **Corollary 3** | balanced + `π₁(K_P)=1` + `(E)` ⇒ `N ≅ B³`, then: *"Lackenby's Theorem 1.3 states that every thickenable balanced presentation of the trivial group can be converted to a standard presentation by Andrews–Curtis moves, without stabilization. It applies to `P`."* | **none** |
| `experiments/stable_ac/thickenable/NEUWIRTH_FEASIBILITY.md` §(a) | quotes Thm 1.3 verbatim: *"Any thickenable balanced presentation of the trivial group can be converted to a standard presentation using Andrews-Curtis moves."* Its §(b) heading *"The key simplification for **2 generators**"* is explicitly a simplification **of our targets**, not a hypothesis of the theorem — and it says a `K5`/`K3,3` link obstruction *"needs ≥3 generators so the link has ≥5 vertices"*, i.e. the memo already contemplates rank ≥ 3 | none |
| `results/stable_ac/theory/OBSTRUCTION_BARRIER.md` | works with `P = ⟨x₁,…,xₙ \| r₁,…,rₙ⟩` throughout | none |
| `literature/proofs/AK3_RANK3_RIGID_THICKENABILITY.md` §7 + `results/…/AK3_RANK3_RIGID_THICKENABILITY.md` | a **shipped rank-3 certificate**: 64 rank-3 trivial-group presentations, and *"one compatible spherical rotation … would make that exact presentation classically AC-trivial by Lackenby's Theorem 1.3"* | none — the repo already acted on the rank-general reading |

**How the rank-3 hypotheses read concretely.** For `P = ⟨x,y,z | r₁,r₂,r₃⟩` presenting
the trivial group, `K_P` has one 0-cell, three 1-cells, three 2-cells, so `χ(K_P) = 1`;
`π₁ = 1` forces `H₂ = 0` and `K_P` contractible; a thickening `N ↘ K_P` is a
contractible compact 3-manifold, hence (Poincaré + PL Schoenflies, Corollary 3's
argument verbatim — it never uses `n = 2`) a 3-ball. Thm 1.3 then applies to `P`.
So **thickenable `(r₁,r₂,z)` ⇒ `(r₁,r₂,z)` is AC-trivial in `F₃`**, which is exactly
statement (4) of Theorem W5.1, hence the bridge, hence AK(3) after one
stabilization. The lever is live at rank 3.

**One caveat, and it bites immediately.** Theorem 2 carries the hypothesis *"suppose
its link graph is connected"*. At rank 2 that is nearly automatic; at rank 3 with a
bare `z` row it **fails by construction** (§2). See Lemma W6.3 for what survives.

**Not verified against the paper.** `arxiv.org` is blocked by this environment's
egress proxy (`EGRESS_BLOCKED`) and `literature/txt/lackenby_stable_ac_thickenable.txt`
does not exist in this checkout. The gate verdict therefore rests on the repo's
records as quoted above, which are consistent across five independent documents and
one shipped certificate. If someone later obtains the paper and finds a rank-2
hypothesis in Thm 1.3, **this verdict and every rank-3 conclusion below fall**, and
so does the repo's already-shipped `AK3_RANK3_RIGID_THICKENABILITY` result.

---

## 2. (b) THE COMBINATORIAL OBJECT AT RANK 3

### 2.1 What replaces the rank-2 link graph — nothing, it is the same construction

The occurrence link graph of `AK3_NEUWIRTH.md` is already rank-general and is
reimplemented independently in `checkers/rank3_link_graph.py`:

* **germ vertices**: `2n` of them; at rank 3, six — `x±, y±, z±` (ids `0..5`, `2k`/`2k+1`).
* **darts**: two per letter occurrence (`d` departs, `h` arrives); `B` pairs them.
* **edges**: one per *cyclic corner* `aᵢaᵢ₊₁` of each relator — `A` joins the arrival
  germ of `aᵢ` to the departure germ of `aᵢ₊₁`. Total edges = total relator length.
* **compatible ordering `C`**: one cyclic order of the `m_g` darts at each `g⁺`; the
  order at `g⁻` is forced to be the reversed `B`-image. Exactly `Π_g (m_g − 1)!` of them.
* **criterion**: `Σ_C` is the ribbon surface; `γ_N(P) = min_C (|A| − |C| + 2L(C) − |AC|)/2`
  is the summed genus, and `γ_N = 0` is the thickenability condition (Theorem 2).

Verified identical to the repo's rank-2 builder (`neuwirth_rank_solver._build_link_data`)
on 5 word pairs, dart for dart (`A`, `B`, `germ`, edge classes) — control (2) below.

### 2.2 What *is* different at rank 3

1. **Planarity can now fail.** With 4 germ vertices no graph is ever non-planar; with
   6 it can be. A word-level control confirms it happens: `("YZyzzx","zxxxZY","YXyX")`
   has a `K5` minor in its simple support. *But it never fired on anything we care
   about*: **0 non-planar link graphs among the 1,868 states of the largest AC ball
   (the smaller balls are nested inside it) and all six targets.** The easy obstruction is still useless here — exactly as
   NEUWIRTH_FEASIBILITY §(b) predicted for rank 2, and now measured at rank 3.
2. **The link graph is disconnected on exactly the states W5 §5 names.** Rank-2
   links can split too, but the once-stabilized triples split *by construction*
   (§2.3) — and Theorem 2 excludes disconnected links by hypothesis, so the repo's
   whole certified ladder answers `UNSUPPORTED` on them (verified: "A-link is
   disconnected").
3. **Supports are 6-vertex**, so `K4`, `K4−e`, `C4`, `P4` — every family the rank-2
   ladder decides — cannot arise. `neuwirth_rank_solver._letter_germs` raises
   `ValueError` on the letter `z` and `GERMS = (0,1,2,3)`: those solvers do not merely
   fail closed at rank 3, **they cannot be fed a rank-3 word at all**.

### 2.3 Lemma W6.1 (z-row splitting) — a bare `z` row is thickenability-inert

> Let `r₁, r₂ ∈ F(x,y)` be nonempty and `z`-free, and `T = (r₁, r₂, z)`. Then
> `γ_N(T) = γ_N(r₁, r₂)` **exactly**.

*Proof.* (i) The word `z` has one occurrence and one cyclic corner, joining its own
arrival germ `z⁻` to its own departure germ `z⁺`; no other relator contains a `z`
letter, so no other corner touches `z±`. Hence the link graph of `T` is the disjoint
union of the rank-2 link graph on `{x±,y±}` and a single edge `z⁺—z⁻`.
(ii) `m_z = 1`, so `(m_z − 1)! = 1`: the compatible orderings of `T` are in bijection
with those of `(r₁,r₂)`, generator by generator.
(iii) On the `z`-component, `|C| = 2`, `|A| = 1`, `|AC| = 1`, `L = 1` ⇒ `χ = 2`,
genus 0. Rotations are germ-local and the components are disjoint, so genus is
additive: `Σ_C(T) = Σ_C(r₁,r₂) ⊔ S²`.
(iv) Minimising over the same index set gives the claim. ∎

**Checked numerically, not just argued**: on AK(3), a *complete* enumeration of all
**86,400** compatible orderings gives `γ_N(xxxYYYY, xyxYXY) = 2` and
`γ_N(xxxYYYY, xyxYXY, z) = 2` (control (6)).

> **Corollary W6.2.** One stabilization by a bare `z` row does not move the Neuwirth
> genus potential at all. Statements (3) and (4) of Theorem W5.1 — in the exact
> spellings W5 records — are **not a new thickenability target**: they are literally
> the rank-2 question the route-3 program has been on since 2026-07. The new freedom
> at rank 3 is entirely in AC-moving *within* rank 3, which mixes `z` into the other
> rows (e.g. `Tpub`), not in the act of stabilizing.

### 2.4 Lemma W6.3 (what survives the connectivity hypothesis) — and the quarantine line

> **(necessity, safe, produces negatives)** If `K_P` embeds in an orientable
> 3-manifold then `γ_N(P) = 0`, connected link or not. Contrapositive: **`γ_N(P) > 0`
> is a certified negative at any rank and any number of components.**

*Proof.* The necessity half of `AK3_NEUWIRTH.md` Theorem 2 puts `F = K_P ∩ ∂R` inside
the oriented 2-sphere `∂R` and reads the compatible `C` off the sphere orientation;
none of that uses connectivity. A graph embedded in `S²` has each of its components
embedded in `S²`, so each component's ribbon surface is a sphere and the genus sum is
0. Only the *sufficiency* half needs `F` cellularly embedded, i.e. connected. ∎

> **(sufficiency, NOT certified here, would produce positives — QUARANTINED)**
> `γ_N(P) = 0` with `L > 1` components would need the extra step "place the `L`
> spherically-embeddable components in `L` disjoint discs of one `S²`". That is
> believable — the standard presentation `(x,y,z)` has `γ_N = 0`, three components,
> and is thickenable by Lackenby's Lemma 3.1 (three cancelling 1-/2-handle pairs) —
> but it is **not** in the repo's Theorem 2, and Pipeline B (Regina `isBall` on an
> independently built `N(K)`) still does not exist. Per `NEUWIRTH_FEASIBILITY` §(e)
> and the W3b tripwire, any `γ_N = 0` verdict is a **suspected Pipeline-A bug first**
> and a result never. **No `γ_N = 0` occurred anywhere in this study.**

### 2.5 Which certified solver families still apply

| family | solver | germs | applies at rank 3? |
|---|---|---:|---|
| `K4`, `K4−e`, `C4` | `neuwirth_rank_solver.solve_spherical` | 4 | **no** — rejects the letter `z` outright |
| `P4` | `neuwirth_p4_solver` | 4 | **no** — same |
| one-loop, paw one-loop | `neuwirth_one_loop_solver`, `neuwirth_paw_one_loop_solver` | 4 | **no** — same |
| `K6 − E(P5)` | `neuwirth_rank3_rigid_solver.solve_rigid_spherical` | 6 | **yes — the only one** |

`K6 − E(P5)` is *rigid*: the theorem behind it (`AK3_RANK3_RIGID_THICKENABILITY.md`)
leans on `H` being **3-connected** and planar, so Whitney gives exactly two spherical
rotations (a reflection pair) and `H − {u,v}` connected kills the relative-shift
freedom the `P4` solver had to handle. That is precisely what our targets fail:

| support | κ (vertex connectivity) | 3-connected | spherical rotations of the simple support |
|---|---:|---|---:|
| AK(3) rank-2 (`K4`) | 3 | yes | **2** (rigid Whitney pair) |
| `Q` rank-2 (`K4−e`) | 2 | no | 2 |
| **`Tpub`** | **2** | **no** | **4** |
| `Txy` | 2 | no | 4 |

So a new rank-3 family for `Tpub` would need **a `P4`-style relative-shift analysis
over four macro embeddings on a 2-connected 6-vertex support**, not a Whitney-pair
argument. That is the shape of the missing theorem.

---

## 3. (c) THE THREE TARGET GRAPHS

Germ ids `0,1,2,3,4,5 = x⁺,x⁻,y⁺,y⁻,z⁺,z⁻`. All from `checkers/out/w6_link_graphs.json`.

### 3.1 `(xxxYYYY, xyxYXY, z)` — the once-stabilized AK(3), total length 14

* 6 germs, 14 corner edges, degrees `[3,3,3,3,1,1]`.
* Simple support `{01,02,03,12,13,23}` on `{x±,y±}` (a `K4`) **plus the isolated edge
  `45`** → **2 components**, planar.
* Parallel multiplicities `01:2, 02:2, 03:2, 12:2, 13:2, 23:3, 45:1`.
* Repo rank-3 rigid solver: **`UNSUPPORTED` — "A-link is disconnected"**.
* Our exact enumeration: **86,400 compatible orderings, all scanned, `γ_N = 2`**.

> **Verdict: NOT THICKENABLE — for this exact spelling** (Lemma W6.3, necessity).
> Independently: the repo's *certified* `K4` solver returns `NOT_SPHERICAL` on the
> rank-2 pair, and Lemma W6.1 transports that verdict verbatim. Two routes, same
> answer; the exact `γ_N = 2` and the certified `NOT_SPHERICAL` agree (control (7)).

### 3.2 `(Q1, Q2, z)` — total length 26

* 6 germs, 26 corner edges, degrees `[2,2,3,3,1,1]`.
* Simple support = `K4 − e` on `{x±,y±}` (missing `01`) **plus the isolated edge `45`**
  → **2 components**, planar. Multiplicities `02:7, 03:4, 12:4, 13:7, 23:3, 45:1`.
* Repo rank-3 rigid solver: **`UNSUPPORTED` — "A-link is disconnected"**.
* Exact `γ_N`: **out of reach** — `2.26 × 10¹⁶` compatible orderings.

> **Verdict: NOT THICKENABLE — for this exact spelling.** Not by brute force, but by
> **Lemma W6.1 + a certified rank-2 negative**: `(Q1,Q2)` has `K4−e` support and the
> repo's proven `neuwirth_rank_solver` returns `NOT_SPHERICAL` with `exhaustive`
> counters, so `γ_N(Q1,Q2) > 0`, so `γ_N(Q1,Q2,z) > 0`. This is the study's one
> *new* decided state, and it cost no new machinery.

### 3.3 `Tpub = (xzYXyxZXYxyZ, XyxZXYXyxzXYxy, Xyz)` — total length 29

* 6 germs, 29 corner edges, degrees `[3,4,2,4,3,2]` (`x⁺,x⁻,y⁺,y⁻,z⁺,z⁻`).
* **Connected**, loopless, **planar** (9 simple edges — under the 9-edge floor logic it
  is checked by the full Wagner test, and it is planar).
* Simple support (9 edges): `02, 03, 04, 12, 13, 14, 15, 34, 35`.
  Complement in `K6` (6 edges): `01, 05, 23, 24, 25, 45` — note **`x⁺x⁻` and `y⁺y⁻`
  are both absent**, which is not the `P5 + isolate` complement `K6 − E(P5)` requires.
* Parallel multiplicities `02:6, 03:6, 04:1, 12:4, 13:1, 14:4, 15:4, 34:1, 35:2`.
* κ = 2, not 3-connected, **4** spherical rotations of the simple support.
* Repo rank-3 rigid solver: **`UNSUPPORTED` — "simple support is not K6 minus P5"**.
* Exact `γ_N`: **out of reach** — `2.09 × 10¹⁶` compatible orderings.

> **Verdict: UNDECIDED. No certified family covers it and brute force is 10¹⁶ away.**
> This is the only one of the three that is a genuinely rank-3 object, and it is
> exactly the object W5 §5 was reaching for. *A new certified solver family is
> required*, and §2.5 says what shape it must have.

`Txy = (A, B, zYX)` — the *certified AC-trivial* triple — has the same profile
(connected, planar, κ = 2, 4 rotations, `UNSUPPORTED`, 2.09 × 10¹⁶ orderings). It is
therefore available as a **positive control for any new rank-3 family**: whatever
solver is built, it must run on `Txy` too, and a `NOT_SPHERICAL` there is a real
outcome (thickenability is not AC-invariant) while a `SPHERICAL` there is a
false-positive tripwire on a state whose AC-triviality is already certified.

---

## 4. (d) THE SEARCH SPACE, HONESTLY

Start `(xxxYYYY, xyxYXY, z)`, canonicalized. **Move set** (declared, not inherited):
AC2 `rᵢ ← reduce(rᵢ · rⱼ^{±1})` for the 6 ordered pairs (12 moves) and AC3
`rᵢ ← reduce(g rᵢ g⁻¹)` for `g ∈ {x,X,y,Y,z,Z}` (18 moves). AC1 and cyclic
conjugation are absorbed by the canonical form: each relator is replaced by the
lexicographic minimum over all cyclic rotations of it *and* of its inverse, and the
three relators are sorted. That quotient is exactly the one the link graph already
sees — rotation, inversion and row order do not change the presentation complex —
so canonical states are in bijection with the distinct link-graph problems.
Best-first by total length, hard cap **1,000 pops**.

| total-length ceiling | canonical states | pops used | **closes?** | disconnected | in a certified family | non-planar | `γ_N` brute-forced |
|---:|---:|---:|---|---:|---:|---:|---|
| 16 | 17 | 17 | **yes** | 5 | **0** | 0 | 13 states, all `γ_N = 2` |
| 18 | 125 | 125 | **yes** | 13 | **0** | 0 | 13 states, all `γ_N = 2` |
| 20 | 503 | 503 | **yes** | 27 | **0** | 0 | 13 states, all `γ_N = 2` |
| 22 | ≥ 1,868 | 1,000 | **no** | 43 | **24** (all `K6−E(P5)`) | 0 | — |

Readings:

* **The ≤ 20 ball is a closure, not a truncated search.** Every canonical rank-3 AC
  state reachable from `(AK3, z)` through states of total length ≤ 20 was enumerated —
  503 of them — and **not one lies in any certified family**. Today's rank-3 machinery
  has *zero* coverage of that closed ball. This is the sharpest number in the study.
* The first certified-family states appear only at ceiling 22, and there are 24 of
  them out of ≥ 1,868 (**≈ 1.3 %**). All 24 were run through
  `neuwirth_rank3_rigid_solver.solve_rigid_spherical` (after the `x,y,z → x,z,t`
  relabel, which is an identity on germ ids): **24/24 `NOT_SPHERICAL`, all with
  `exhaustive` counters** (a non-exhaustive negative raises in the checker).
* Growth is ×7.4, ×4.0, ×3.7 per `+2` of ceiling. A ceiling of 30 — the region where
  AK(3)'s own greedy work lives — is `10⁵–10⁶` canonical states, i.e. **three orders
  of magnitude past the 1,000-pop law**. Any real sweep is a Colab job, not a local one.
* **Brute-force `γ_N` is not a strategy.** Only 13 states in any ball have
  `Π(m_g − 1)! ≤ 2 × 10⁵`; the count explodes with total length (`Tpub`: `2 × 10¹⁶`).
  Coverage has to come from *theorems* (new certified families), not from enumeration.
* **Zero positives, zero tripwire events**, consistent with W3b.

---

## 5. Controls that could have failed (all 29 green)

1. **Planarity oracle vs an independent oracle.** The Wagner minor test and a
   brute-force rotation-system genus-0 search agree on `K5`, `K3,3`, `K4`, `C4`, `P4`,
   `K5−e`, and `K6−E(P5)` — including that `K6−E(P5)` *is* planar.
2. **Dictionary vs the repo.** Our rank-general builder reproduces
   `neuwirth_rank_solver._build_link_data` exactly (`A`, `B`, `germ`, edge classes) on
   AK(3), `Q`, and the three repo calibration pairs.
3. **`Π(m_g−1)!` vs the repo's pinned `expected_cases`**: 6, 4, 12 — exact match on all
   three `two_hop_cov_thickenability_certificate.CALIBRATIONS` fixtures.
4. **Exact `γ_N` vs the repo's pinned `minimum_genus`**: 0, 1, 0 — exact match on the
   same three fixtures, including the one non-spherical fixture.
5. **Word-level non-planar rank-3 control**: `("YZyzzx","zxxxZY","YXyX")` → `K5` minor.
   Without it, "planar" would be an untested constant on our data.
6. **Positive control**: the standard `(x,y,z)` has `γ_N = 0` and **3 components** —
   demonstrating both that the machinery finds a genuine positive and that the repo's
   certified ladder calls a *provably thickenable* presentation `UNSUPPORTED`.
7. **Cross-check of verdicts**: our exact `γ_N = 2` on AK(3) agrees with the repo's
   certified `K4` solver's `NOT_SPHERICAL`.
8. **Splitting lemma checked numerically**, not only proved (§2.3).

---

## 6. Scope and nonclaims

* **No AK(3) claim, no AC claim, no stable-AC claim, no bridge claim.** Nothing here
  says AK(3) is or is not AC-trivial, stably AC-trivial, or thickenable.
* **What is proved:** Lemma W6.1 (z-row splitting, exact, and numerically confirmed);
  Lemma W6.3 necessity (a restatement of the repo's Theorem 2 necessity half with the
  connectivity hypothesis dropped, which that proof never uses).
* **What is doctrine-quarantined:** the sufficiency direction for disconnected links
  (§2.4) — never used to conclude anything here, and moot, since no `γ_N = 0` arose.
* **What is a negative, and how narrow it is:** `γ_N > 0` decides **one spelling**.
  AC moves change the link graph, and stable-ACC explicitly permits passing through
  non-thickenable states (`NEUWIRTH_FEASIBILITY` §(a)). The negatives on
  `(AK3₁,AK3₂,z)` and `(Q1,Q2,z)` therefore **prune two states and decide nothing**.
* **What is inherited, not re-derived:** the repo's `NOT_SPHERICAL` verdicts from
  `neuwirth_rank_solver` and `neuwirth_rank3_rigid_solver` (used as certified inputs);
  the `AK3_NEUWIRTH.md` Theorem 2 / Corollary 3 derivation; Lackenby Thm 1.3 itself,
  which **could not be read** (arXiv egress-blocked, no local text) — see §1's caveat.
* **The 1,000-pop law was respected everywhere**: the largest search was 1,000 pops;
  the ≤ 20 ball closed at 503. `γ_N` enumerations are complete finite closures over
  compatible orderings, not searches, and popped no state.
* The AC-ball census depends on the declared move set and canonicalization of §4. A
  different move set (e.g. AC2 with non-trivial conjugators) reaches more states; the
  closure claim is a closure **for that move set**.

---

## 7. Most decisive next step

**Build the certified solver family that `Tpub` needs: 2-connected planar 6-germ
support, four macro rotations, parallel bundles with relative shifts.** It is the
`P4` solver's mechanism (`AK3_P4_SYNCHRONIZED_PLANARITY.md` — bundles are cyclic
intervals; the middle bundle's `m` relative shifts must be enumerated) lifted from a
4-vertex path to a 2-connected 6-vertex support, and the `K6−E(P5)` rigidity proof
tells you exactly which step it must replace. It is the only thing standing between
the lane and a verdict on `Tpub` and on the 476 + 1,801 `OTHER`-support states the
AC ball is made of.

Two things **not** to do first:

* **Do not sweep the stabilized `(r₁,r₂,z)` states.** Corollary W6.2 says they carry
  no information the rank-2 sweep did not already have. W5 §5's target, taken
  literally, is the rank-2 target.
* **Do not filter on planarity.** Zero non-planar link graphs among the 1,868
  AC-ball states (the smaller balls are nested inside it) and all six targets. The cheap obstruction does not fire here, as at rank 2.

Secondary, and cheap: `Txy` is a free positive control for the new family (§3.3), and
`checkers/rank3_link_graph.py ball` already emits the exact state list to run it on.
Independently: Pipeline B remains absent, so no positive is announceable at any rank
until an `N(K)` is built and `isBall`-confirmed — that gap is now the binding
constraint on the *upside*, exactly as it was in W3b.
