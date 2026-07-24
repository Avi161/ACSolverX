# AK(3) Neuwirth Theory and Certificate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove the exact Neuwirth thickenability criterion needed for AK(3), independently decide the two base presentation complexes, and use the resulting obstruction profile to inspect the known height-17 classical component without mislabelling any negative as an AC obstruction.

**Architecture:** A theory note is load-bearing. Two dependency-free finite enumerators then realize the same occurrence-order census using different dart numberings: one follows Neuwirth's \(A,B,C\) permutations, the other traces a rotation system directly. A small driver compares their ordered traces and writes a replayable JSON certificate; a separate bounded component scan is attempted only after the base certificate passes.

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

- [ ] **Step 5: Run both target audits**

Run:

```bash
.venv/bin/python3 -m pytest tests/stable_ac/test_neuwirth_dart_audit.py -q
```

Expected: PASS with identical complete trace digests.

- [ ] **Step 6: Generate the JSON certificate**

The CLI writes:

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

Each target entry contains exact words, degrees, expected/enumerated cases, full defect histogram, minimum genus, accepting orders with correct boundary-orbit counts, both trace digests, and a fail-closed verdict. Generate from a clean commit so `source_commit` identifies the code state.

Run:

```bash
.venv/bin/python3 -m experiments.stable_ac.thickenable.neuwirth_permutation_certificate --audit --output results/stable_ac/theory/ak3_neuwirth_census.json
```

- [ ] **Step 7: Replay from JSON**

Run:

```bash
.venv/bin/python3 -m experiments.stable_ac.thickenable.neuwirth_permutation_certificate --verify results/stable_ac/theory/ak3_neuwirth_census.json
```

Expected: recomputation succeeds and both module/content digests match.

- [ ] **Step 8: Commit the independent audit and certificate**

Run:

```bash
git add experiments/stable_ac/thickenable/neuwirth_dart_audit.py tests/stable_ac/test_neuwirth_dart_audit.py results/stable_ac/theory/ak3_neuwirth_census.json
git commit -m "result: certify AK3 Neuwirth rotation census"
```

---

### Task 4: Extract the obstruction profile and test the known height-17 component

**Files:**
- Create: `experiments/stable_ac/thickenable/scan_ak3_component.py`
- Create: `results/stable_ac/theory/AK3_NEUWIRTH_RESULT.md`
- Create: `results/stable_ac/theory/ak3_component_thickenability.json`

**Interfaces:**
- Consumes: the direct census, the independent audit, and the read-only `component(AK3, 17)` generator.
- Produces: a bounded, reproducible census over exactly the known 1,000-state component, with explicit `DECIDED` versus `SKIPPED_COST` accounting.

- [ ] **Step 1: Derive the human obstruction profile**

From both target histograms, state the maximum face count, minimum compatible genus, number of minimum-genus orders, and whether the two classically equivalent representatives have identical or different profiles. Attempt a combinatorial explanation in terms of forced interlacing of occurrence bands; label it `[PROVEN]` only if it is derived without relying on the enumeration.

- [ ] **Step 2: Implement the bounded component driver**

Recompute `component(AK3, 17)` with the existing hard `POP_CAP=1000`; assert its size is exactly 1,000 and its set is closed using the existing child generator. For each exact canonical word pair:

```python
cost = product(factorial(degree[g] - 1) for g in generators)
if cost > max_orderings:
    record SKIPPED_COST
else:
    run the direct census
    independently rerun any Euler-positive through the dart audit
```

Default `max_orderings=2_000_000`. Never infer a verdict for skipped states.

- [ ] **Step 3: Fail closed on any positive**

If any state has an Euler-accepting order, stop result promotion and emit `REGINA_REQUIRED` with the exact state and order. Do not call it a solution until a separate exact regular-neighbourhood triangulation verifies `isBall()`.

- [ ] **Step 4: Write the bounded report**

The Markdown report must use four sections:

1. `What counts`: theorem/certificate, plus any independently validated positive.
2. `What was ruled out`: exact base complexes and component coverage, including order cap and skipped count.
3. `Live leads`: a structural interlacing lemma, a Regina witness if needed, and uncovered high-cost states.
4. `Open ledger`: AK(3) remains one open AC/stable-AC problem unless a positive survived Regina.

- [ ] **Step 5: Run the full relevant tests**

Run:

```bash
.venv/bin/python3 -m pytest tests/stable_ac/test_neuwirth_permutation_certificate.py tests/stable_ac/test_neuwirth_dart_audit.py tests/stable_ac/test_thickenable.py -q
.venv/bin/python3 -m experiments.stable_ac.cov.ak_3_universal_test.certify_classical --verify
```

Expected: all tests pass; the classical bridge replays.

- [ ] **Step 6: Commit the bounded scan and report**

Run:

```bash
git add experiments/stable_ac/thickenable/scan_ak3_component.py results/stable_ac/theory/AK3_NEUWIRTH_RESULT.md results/stable_ac/theory/ak3_component_thickenability.json
git commit -m "result: map thickenability across AK3 height-17 component"
```

Expected: only new files are committed; pre-existing untracked `prompts/` and temporary source-render files remain untouched.
