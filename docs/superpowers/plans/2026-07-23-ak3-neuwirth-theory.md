# AK(3) Neuwirth Theory and Certificate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove the exact Neuwirth thickenability criterion needed for AK(3), independently decide the two base presentation complexes, and use the resulting obstruction profile to inspect the known height-17 classical component without mislabelling any negative as an AC obstruction.

**Architecture:** A theory note is load-bearing. Two dependency-free finite enumerators realize the same occurrence-order census using different dart numberings: one follows Neuwirth's \(A,B,C\) permutations, the other traces a rotation system directly. A small driver compares their ordered traces and writes a replayable JSON certificate. For the 1,000-state component, a second theorem classifies all spherical rotations of the only three support types present and turns the compatibility problem into modular signed-rank propagation on the two relator cycles.

**Tech Stack:** Python 3 standard library, pytest, SHA-256, existing read-only AC component generator, Markdown.

## Global Constraints

- Create new files only; do not modify solver, runner, notebook, existing result, or existing test files.
- Do not freely or cyclically reduce relator words in the thickenability code.
- Permutation products act right-to-left: `compose(P, Q)[e] == P[Q[e]]`.
- Use Neuwirth's geometrically supported boundary test \(\langle AC,BC\rangle\), and separately pin the printed \(CB\) discrepancy.
- A positive on AK(3) or any classically equivalent state is quarantined pending an exact Regina regular-neighbourhood witness.
- A negative applies only to the exact presentation complex tested; it is not an AC or stable-AC obstruction.
- No AC search may exceed `node_budget = 1000`; rotation-order enumeration is a separate finite decision procedure.
- Use `.venv/bin/python3`.

---

### Task 1: Write the load-bearing theorem and proof

**Files:**
- Create: `literature/proofs/AK3_NEUWIRTH.md`

**Interfaces:**
- Consumes: Neuwirth 1968, pp. 604--611; Lackenby Theorem 1.3 and §3.1; the exact words `xxxYYYY|xyxYXY` and `YYXXyx|YYYxyXX`.
- Produces: definitions and theorem statements that the certificate code implements literally.

- [ ] **Step 1: State the exact occurrence dictionary**

Write the following definitions, with a worked two-letter corner:

```text
For occurrence o_i of letter a_i, let d_i be its departure endpoint and
h_i its arrival endpoint.  B=(d_i h_i) over occurrences.  For every cyclic
corner a_i a_{i+1}, A pairs h_i with d_{i+1}.  At the positive end of an
unsigned generator g, occurrence i contributes d_i when a_i=g and h_i when
a_i=g^{-1}.  If this positive cycle is (p_1 ... p_m), the negative cycle is
(B(p_m) ... B(p_1)).
```

- [ ] **Step 2: Prove the Euler criterion**

Prove that \(|C|\), \(|A|\), and \(|AC|\) count vertices, edges, and faces of the induced orientable link surface. For \(L\) components,

```text
chi = |C| - |A| + |AC|,
genus_sum = (2L - chi)/2,
```

so the connected-link planar condition is \(|A|-|C|+2=|AC|\). Explicitly note that \(AC\) and \(CA\) are conjugate, while the \(BC/CB\) transitivity expressions need not agree.

- [ ] **Step 3: Prove necessity and sufficiency**

Give the small-sphere necessity argument. For sufficiency, spell out the PL 0-/1-/2-handle construction from Neuwirth p.611 and the compatible radial collapse \(N\searrow K_P\). State transitivity only as the extra connected-boundary/one-3-cell condition.

- [ ] **Step 4: Prove the balanced-trivial corollary**

Use, in order:

```text
balance + pi_1(K)=1 => chi(K)=1 and H_2(K)=0 => K acyclic;
simply connected + acyclic CW complex => K contractible;
N retracts to K;
Poincare--Lefschetz duality => boundary N is a connected homology 2-sphere;
surface classification => boundary N = S^2;
cap + van Kampen + 3D Poincare + PL Schoenflies => N = B^3;
Lackenby Theorem 1.3 => the presentation is classically AC-trivial.
```

Conclude that Euler-pass/transitivity-fail on a balanced trivial target is an audit contradiction.

- [ ] **Step 5: Record scope and non-implications**

State that Neuwirth is load-bearing; Fulek--Tóth is corroboration only unless a PL subdivision bridge is supplied. State that a base-complex negative is not preserved by AC moves and does not make AK(3) a counterexample.

- [ ] **Step 6: Commit the proof note**

Run:

```bash
git add literature/proofs/AK3_NEUWIRTH.md
git commit -m "docs: prove Neuwirth criterion used for AK3"
```

Expected: one new proof file committed, with no pre-existing file changed.

---

### Task 2: Build the direct Neuwirth permutation census by TDD

**Files:**
- Create: `experiments/stable_ac/thickenable/neuwirth_permutation_certificate.py`
- Create: `tests/stable_ac/test_neuwirth_permutation_certificate.py`

**Interfaces:**
- Produces:
  - `OccurrenceData.from_words(words: tuple[str, ...]) -> OccurrenceData`
  - `compose(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]`
  - `cycle_count(p: tuple[int, ...]) -> int`
  - `orbit_count(generators: tuple[tuple[int, ...], ...]) -> int`
  - `enumerate_trace(words: tuple[str, ...]) -> Census`
  - `Census.to_json() -> dict[str, object]`

- [ ] **Step 1: Write failing dictionary and convention tests**

Add tests asserting:

```python
def test_products_act_right_to_left():
    p = (1, 0, 2)
    q = (0, 2, 1)
    assert compose(p, q) == (1, 2, 0)


def test_commutator_occurrence_dictionary():
    data = OccurrenceData.from_words(("xyXY",))
    assert len(data.A) == 8
    assert cycle_count(data.A) == 4
    assert cycle_count(data.B) == 4
    assert {g: len(es) for g, es in data.positive_ends.items()} == {"x": 2, "y": 2}
```

- [ ] **Step 2: Run the focused tests and see the import fail**

Run:

```bash
.venv/bin/python3 -m pytest tests/stable_ac/test_neuwirth_permutation_certificate.py -q
```

Expected: FAIL because the new module does not yet exist.

- [ ] **Step 3: Implement exact parsing and the occurrence permutations**

Implement immutable tuples with:

```python
depart = 2 * occurrence
arrive = depart + 1
B[depart] = arrive
B[arrive] = depart
A[arrive(current)] = depart(next)
A[depart(next)] = arrive(current)
positive_endpoint = depart if letter.islower() else arrive
```

Reject empty words, nonletters, and a generator appearing zero times. Do not call any reduction function.

- [ ] **Step 4: Implement order enumeration and \(C\)**

For each generator, sort positive endpoints, fix the first, and permute the tail. If `positive_order` is `(p0,...,pk)`, define:

```python
negative_order = tuple(B[p] for p in reversed(positive_order))
```

Set successors around both cycles. Assert every endpoint receives exactly one successor.

- [ ] **Step 5: Implement the complete trace**

For every Cartesian product of generator orders, record:

```python
AC = compose(A, C)
BC = compose(B, C)
CB = compose(C, B)
L = orbit_count((A, C))
faces = cycle_count(AC)
defect = cycle_count(A) - cycle_count(C) + 2 * L - faces
boundary_orbits_BC = orbit_count((AC, BC))
boundary_orbits_CB = orbit_count((AC, CB))
trace_item = (L, faces, defect, boundary_orbits_BC, boundary_orbits_CB)
```

Update SHA-256 with the canonical order descriptor and `trace_item` for every case. Do not stop at the first accept.

- [ ] **Step 6: Add the adversarial fixtures**

Test the exact occurrence word `("xxX",)` against the hostile review's fixed \(A,B,C\): Euler passes, `BC` is transitive, and `CB` has two orbits. Test `("x", "xyXY")`: at least one connected-link order passes Euler and fails correct `BC` transitivity.

- [ ] **Step 7: Add topology calibration fixtures**

Assert an Euler-accepting order exists for `("x", "y")`, `("xyXY",)`, `("xyxYXY",)`, and `("xx",)`. Assert no Euler-accepting order exists for the \(K_{3,3}\)-link word `("XXYXZYYZZ",)`. These are exact-word checks; no pre-collapse or reduction is allowed.

- [ ] **Step 8: Add target completeness tests**

Assert for each target:

```python
census.expected_cases == 86_400
census.enumerated_cases == 86_400
census.link_components == {1}
sum(census.defect_histogram.values()) == 86_400
```

Do not yet pin target verdicts; the first correct run is allowed to reveal them.

- [ ] **Step 9: Run focused tests**

Run:

```bash
.venv/bin/python3 -m pytest tests/stable_ac/test_neuwirth_permutation_certificate.py -q
```

Expected: PASS, including two full 86,400-case censuses in under one minute.

- [ ] **Step 10: Commit the direct implementation**

Run:

```bash
git add experiments/stable_ac/thickenable/neuwirth_permutation_certificate.py tests/stable_ac/test_neuwirth_permutation_certificate.py
git commit -m "feat: add direct Neuwirth permutation census"
```

---

### Task 3: Add an independent dart audit and replayable target certificate

**Files:**
- Create: `experiments/stable_ac/thickenable/neuwirth_dart_audit.py`
- Create: `experiments/stable_ac/thickenable/neuwirth_target_certificate.py`
- Create: `tests/stable_ac/test_neuwirth_dart_audit.py`
- Create: `results/stable_ac/theory/ak3_neuwirth_census.json`

**Interfaces:**
- Consumes only exact word tuples; it must not import the direct census module or the existing prototype.
- Produces `audit_trace(words: tuple[str, ...]) -> AuditCensus` with the same canonical order descriptors and trace items as Task 2.

- [ ] **Step 1: Write a failing cross-implementation test**

The test imports both modules only at the assertion layer:

```python
@pytest.mark.parametrize("words", [
    ("xxxYYYY", "xyxYXY"),
    ("YYXXyx", "YYYxyXX"),
])
def test_independent_ordered_trace_agrees(words):
    direct = enumerate_trace(words)
    audit = audit_trace(words)
    assert audit.enumerated_cases == direct.enumerated_cases == 86_400
    assert audit.trace_sha256 == direct.trace_sha256
    assert audit.defect_histogram == direct.defect_histogram
    assert audit.accepting_orders == direct.accepting_orders
```

- [ ] **Step 2: Run it and see the import fail**

Run:

```bash
.venv/bin/python3 -m pytest tests/stable_ac/test_neuwirth_dart_audit.py -q
```

Expected: FAIL because `neuwirth_dart_audit.py` does not exist.

- [ ] **Step 3: Implement independent corner-dart numbering**

Number the two darts of cyclic corner \(a_i a_{i+1}\) consecutively. Store occurrence-to-departure/arrival dart maps after all corners are built. Pair corner darts by `alpha[d] = d ^ 1`; pair the two tube ends of an occurrence in a separate `tube_pair` array. Do not copy or import Task 2's `A`, `B`, or `C`.

- [ ] **Step 4: Trace faces directly**

Build `sigma` as the vertex-rotation successor. Count faces as orbits of:

```python
phi[d] = sigma[alpha[d]]
```

Construct the boundary audit from the independently numbered corner and tube transitions and return the same invariant tuple in the same order descriptor. Document the conjugacy explaining why direct `phi` face counts match \(|AC|\).

- [ ] **Step 5: Write a failing certificate-driver test**

Before creating the driver, add a small-fixture test that imports `build_certificate` and `verify_certificate`, asserts the schema/composition strings, source commit, module hashes, equal direct/audit digests, exact summary fields, and fail-closed verdict semantics. Run the focused test and require an import failure before implementation.

- [ ] **Step 6: Add the separate certificate driver**

Create `neuwirth_target_certificate.py` as the only integration layer allowed to import both new enumerators. Do not retrofit CLI behavior into the already committed direct module. Its CLI writes:

```json
{
  "schema": "ak3-neuwirth-census-v1",
  "composition": "right-to-left: PQ(e)=P(Q(e))",
  "targets": {},
  "source_commit": "",
  "direct_module_sha256": "",
  "audit_module_sha256": ""
}
```

Each target entry contains exact words, degrees, expected/enumerated cases, full defect histogram, minimum genus, accepting orders with correct boundary-orbit counts, both trace digests, and a fail-closed verdict. The result file stores the trace digests rather than duplicating all 172,800 trace records; replay recomputes and compares the complete ordered traces.

- [ ] **Step 7: Run both target audits and driver tests**

Run:

```bash
.venv/bin/python3 -m pytest tests/stable_ac/test_neuwirth_dart_audit.py -q
```

Expected: PASS with identical complete trace digests.

- [ ] **Step 8: Commit and push the code state**

Run:

```bash
git add experiments/stable_ac/thickenable/neuwirth_dart_audit.py experiments/stable_ac/thickenable/neuwirth_target_certificate.py tests/stable_ac/test_neuwirth_dart_audit.py
git commit -m "feat: add independent Neuwirth dart audit"
git push origin codex/proofs
```

The result generator must now run from a clean working tree and record this exact code commit as `source_commit`.

- [ ] **Step 9: Generate the JSON certificate**

Run:

```bash
.venv/bin/python3 -m experiments.stable_ac.thickenable.neuwirth_target_certificate --output results/stable_ac/theory/ak3_neuwirth_census.json
```

- [ ] **Step 10: Replay from JSON**

Run:

```bash
.venv/bin/python3 -m experiments.stable_ac.thickenable.neuwirth_target_certificate --verify results/stable_ac/theory/ak3_neuwirth_census.json
```

Expected: recomputation succeeds and both module/content digests match.

- [ ] **Step 11: Commit and push the generated certificate**

Run:

```bash
git add results/stable_ac/theory/ak3_neuwirth_census.json
git commit -m "result: certify AK3 Neuwirth rotation census"
git push origin codex/proofs
```

---

### Task 4: Prove the signed-rank spherical-rotation criterion

**Files:**
- Create: `literature/proofs/AK3_SYNCHRONIZED_PLANARITY.md`

**Interfaces:**
- Consumes: the exact Neuwirth dart dictionary and the support multigraph.
- Produces: necessary-and-sufficient criteria for \(K_4\), \(K_4-e\), and \(C_4\), plus the modular rank equations implemented in Task 5.

- [ ] **Step 1: Prove the \(K_4\) multigraph theorem**

Prove the block, tetrahedral macro-rotation, and reversed-class-order
conditions in both directions.  Include the exact count
\(2\prod_{uv}m_{uv}!\), and address the fact that a chosen skeleton edge may
have parallel copies on both of its sides.

- [ ] **Step 2: Derive the signed-rank equations**

Define endpoint slot maps, the two cyclic phases, and the modular equation for
each \(B\)-pair.  Prove that the \(A\)-contracted constraint graph is the union
of the two relator cycles and that seed propagation plus per-class
all-different constraints is necessary and sufficient.

- [ ] **Step 3: Prove the \(K_4-e\) classification**

Use the \(\{a,b\}\)-bridge decomposition to prove that the central class is
split exactly as
`C, L[:i], D, L[i:]`, for \(0\le i\le m_{ab}\), with reverse order at the
other pole.  Prove that this lists every spherical scheme exactly once after
fixing reflection and cyclic origin.

- [ ] **Step 4: Prove the \(C_4\) classification and state scope**

Prove the unique reversed-block scheme.  State that other or disconnected
supports must fail closed into a general Synchronized Planarity path; do not
silently extrapolate the specialized theorem.

- [ ] **Step 5: Hostile mathematical review and commit**

Require a reviewer to try to construct omitted embeddings, especially a split
central class in \(K_4-e\), and to audit every modular sign.  Resolve all
Critical/Important findings before:

```bash
git add -f literature/proofs/AK3_SYNCHRONIZED_PLANARITY.md
git commit -m "docs: prove signed-rank planarity criterion"
git push origin codex/proofs
```

---

### Task 5: Implement and cross-check the exact rank solver by TDD

**Files:**
- Create: `experiments/stable_ac/thickenable/neuwirth_rank_solver.py`
- Create: `tests/stable_ac/test_neuwirth_rank_solver.py`

**Interfaces:**
- `classify_support(words) -> SupportClass`
- `embedding_schemes(data) -> tuple[Scheme, ...]`
- `solve_spherical(words) -> RankDecision`
- A positive decision contains exact rotations, ranks, phases, scheme, faces,
  Euler characteristic, and genus.

- [ ] **Step 1: Write failing support and scheme tests**

Pin generated labeled examples of \(K_4\), both forms of \(K_4-e\), and
\(C_4\).  Assert exact scheme counts and injective/partitioning slot maps.
Assert unsupported inputs fail closed.

- [ ] **Step 2: Write failing signed-rank propagation tests**

Pin hand-sized satisfiable and unsatisfiable systems, including a
\(K_4-e\) case where only a genuinely split central class works.  Require
closure, no repeated rank within an individual relator cycle, disjoint
class-rank bitsets across relators, and exhaustion of every class rank rather
than trusting a reconstructed face count alone.

- [ ] **Step 3: Implement the minimal theorem-shaped solver**

Build \(D,A,B\) from exact words, classify support, enumerate the proved
schemes, enumerate phases, propagate each relator cycle from seed ranks, and
combine cycle assignments by class bitsets.  Do not import or invoke the
factorial target enumerators in production solving.

- [ ] **Step 4: Independently reconstruct and face-trace every positive**

Construct the four rotations from the returned witness and trace
\(\phi=\sigma\alpha\).  A solver acceptance is valid only if the trace has
Euler characteristic two and all Neuwirth reversal equations replay.

- [ ] **Step 5: Cross-check against exhaustive enumeration**

Compare decisions with the direct factorial census on:

- all 18 component states of cost at most 2,000,000;
- every ordered pair of nonempty cyclically reduced words over
  \(\{x,X,y,Y\}\) with total length at most 7, quotienting only cyclic rotation
  of each relator and relator swap, whose loopless connected support is
  \(K_4\), \(K_4-e\), or \(C_4\);
- AK(3) and orbit-2, which must remain negative.

Assert the exact number of canonical systems and the exact count in each
support class.  Compare every decision case-by-case with factorial
enumeration.  This bounded equivalence census, rather than a random sample,
must exercise both modular signs, both relator-cycle closures, every
\(K_4-e\) split index available at the bound, within-cycle rank collisions,
and cross-cycle rank collisions.

- [ ] **Step 6: Commit code and tests**

```bash
git add experiments/stable_ac/thickenable/neuwirth_rank_solver.py tests/stable_ac/test_neuwirth_rank_solver.py
git commit -m "feat: solve Neuwirth planarity by signed ranks"
git push origin codex/proofs
```

---

### Task 6: Certify the full known height-17 component and report

**Files:**
- Create: `experiments/stable_ac/thickenable/scan_ak3_component.py`
- Create: `tests/stable_ac/test_scan_ak3_component.py`
- Create: `results/stable_ac/theory/AK3_NEUWIRTH_RESULT.md`
- Create: `results/stable_ac/theory/ak3_component_thickenability.json`

- [ ] **Step 1: Recompute and authenticate the bounded component**

Recompute the existing AK(3), height-17 component with the hard
`node_budget=1000`.  Merely reaching 1,000 states is not completeness:
require that the BFS queue is empty after the 1,000th pop and explicitly
check closure under every permitted height-17 move.  Record and verify:

```text
root exact words;
height ceiling = 17;
pop cap = 1000 and actual pop count;
queue-exhausted and closure-verified flags;
canonicalization function and implementation hash;
move generator and implementation hash;
all child options, including cap and seam_only=False;
SHA-256 of the sorted exact state set;
source commit and scanner/rank-solver module hashes.
```

This is the maximum permitted AC search.

- [ ] **Step 2: Decide all 1,000 exact complexes**

Require the support histogram `720 K4 / 278 K4-e / 2 C4`, zero unsupported
states, and a signed-rank decision for every state.  Store a canonical
per-state decision record and its ordered digest.  Replay every positive
witness independently.  Never infer anything from an omitted or failed state.

- [ ] **Step 3: Quarantine positives**

Any positive is reported as `REGINA_REQUIRED` with the exact state, scheme,
phases, ranks, rotations, and face trace.  It is not promoted to an AC
certificate until an independently constructed triangulation returns
`isBall() == True` and its handle incidences match.

- [ ] **Step 4: Extract the obstruction profile**

Report the exact target \(\gamma_N\) histograms only from the separate
86,400-case factorial certificates; the rank solver decides the zero-versus-
positive question and does not minimize positive genus.  Include the human
proof that orbit-2 has no **synchronized compatible spherical rotation** and
its explicit genus-one witness.  Do not call its abstract \(K_4\) support
nonplanar.  State that \(\gamma_N\) changes under AC moves and is only a search
potential.  For AK(3), label the exact \(\gamma_N=2\) conclusion census-derived
unless a separate short-face packing proof is completed.

- [ ] **Step 5: Write the four-part report**

Use `What counts`, `What was ruled out`, `Live leads`, and `Open ledger`.
Distinguish classical AC, stable AC, thickenability of an exact complex, and
bounded component evidence in every claim.

- [ ] **Step 6: Build the fail-closed replay verifier**

The scanner CLI has separate `--output` and `--verify` modes.  Verification
must rebuild the exact component, compare its identity and sorted-state digest,
and rerun support classification plus the complete scheme/phase/seed search
for all 1,000 states.  It compares every canonical per-state record and the
ordered decision digest.  It fails closed on any source/hash/option mismatch,
unsupported state, incomplete search, or witness replay failure.

- [ ] **Step 7: Commit the clean source state**

Run all new focused tests, the existing thickenability tests, both target
certificate replays, and the 17-macro-edge classical certificate replay.
Then commit and push only the scanner and its tests.  Generate no promoted JSON
or report from a dirty source tree.

- [ ] **Step 8: Generate, replay, review, and commit the result**

Generate the JSON from the clean source commit, run `--verify`, and have a
fresh reviewer audit the source/result binding, queue-exhaustion/closure
evidence, exact state digest, all 1,000 rerun decisions, and every claimed
count before:

```bash
git add results/stable_ac/theory/AK3_NEUWIRTH_RESULT.md results/stable_ac/theory/ak3_component_thickenability.json
git commit -m "result: certify AK3 height-17 thickenability census"
git push origin codex/proofs
```

Expected: all 1,000 states are accounted for; only new task files are changed.
