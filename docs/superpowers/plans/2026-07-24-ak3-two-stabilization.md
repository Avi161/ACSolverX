# AK(3) Immediate Two-Stabilization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove the triangular two-removal theorem and exactly decide whether defining words of length at most two and a braid template of length at most six produce an AK(3) endpoint of Aut-floor at most 12.

**Architecture:** A theorem note proves two generalized stabilizations followed by two immediate Lemma-11 removals. A dependency-free word enumerator constructs every finite certificate and deduplicates rank-3/rank-2 outputs. A separate certificate driver replays literal source identities, both isolator solutions, every output, the complete trace, and all Aut witnesses.

**Tech Stack:** Python 3 standard library, pytest, existing read-only `autcanon`, Markdown, JSON, SHA-256.

## Global Constraints

- Create new task files only; do not modify existing corridor engines, certificates, solvers, runners, notebooks, tests, or results.
- Literal expansion to the exact source orientation is mandatory before deriving any tuple.
- Defining words have individual length at most two.
- First templates have length at most six, exactly one `y/Y`, and use both `z/Z` and `t/T`.
- The second removal is immediate: one of the three derived relators must already contain exactly one `x/X`.
- No AC graph search contributes to the candidate verdict.
- A floor-13 minimum refutes only this finite lemma.
- CPU only; use `.venv/bin/python3`.
- Commit and push `codex/proofs` at theorem, implementation, certificate, and adjudication checkpoints, never more than twenty minutes apart while tracked changes exist.
- Do not open a pull request or merge.

---

### Task 1: Prove the triangular two-removal theorem

**Files:**
- Create: `literature/proofs/AK3_TWO_STABILIZATION.md`

**Interfaces:**
- Consumes: `AK3_RANK3_COMPRESSION.md` Section 2 and Theorem 3.1.
- Produces: the exact two-stage formulas implemented by Task 2.

- [ ] **Step 1: State simultaneous substitution**

For words \(w_z,w_t\), define:

```text
sub_new(I) = red(I[z->w_z, Z->w_z^-1, t->w_t, T->w_t^-1])
```

Prove that every displayed replacement is an AC1--AC3 composite using the
two defining relators.

- [ ] **Step 2: Prove the first removal**

If `sub_new(I_y)` is the source relator and `I_y` has one `y/Y`, rotate to
`y^eps q`, solve:

```text
e_y = inv(q) if eps == +1 else q
```

and derive exactly:

```text
R_y = sub_y(other_source, e_y)
Z_y = sub_y(Z + w_z, e_y)
T_y = sub_y(T + w_t, e_y)
```

- [ ] **Step 3: Prove the immediate second removal**

If one of `(R_y, Z_y, T_y)` has exactly one `x/X`, solve it by the same
formula, remove it with `x`, substitute `e_x` in the other two relators, and
relabel `z -> x`, `t -> y`. Prove the output is stably AC-equivalent to the
input.

- [ ] **Step 4: Pin the valid and invalid braid orders**

Show:

```text
sub_new("zxYT", w_z="xy", w_t="yx") == "xyxYXY"
sub_new("zxTY", w_z="xy", w_t="yx") == "xY"
```

State that the second spelling is quarantined and cannot seed a proof.

- [ ] **Step 5: State the finite candidate and scope**

Copy the exact word/template/removal bounds. State that a null is not a stable
obstruction and that the next theorem permits one second-stage compression.

- [ ] **Step 6: Commit and push**

Run:

```bash
git add -f literature/proofs/AK3_TWO_STABILIZATION.md
git commit -m "docs: prove triangular two-stabilization theorem"
git push origin codex/proofs
```

---

### Task 2: Implement the exact two-removal census by TDD

**Files:**
- Create: `experiments/stable_ac/rank3_compression/two_stabilization.py`
- Create: `tests/stable_ac/test_two_stabilization.py`

**Interfaces:**
- Produces:
  - `inverse(word: str) -> str`
  - `free_reduce(word: str) -> str`
  - `cyclic_orientations(word: str) -> tuple[str, ...]`
  - `substitute_new(template: str, word_z: str, word_t: str) -> str`
  - `substitute_generator(word: str, generator: str, expr: str) -> str`
  - `solve_isolator(word: str, generator: str) -> str`
  - `derive_rank3(pair, source_index, word_z, word_t, template, eliminated="y") -> tuple[str, str, str]`
  - `remove_second(rank3, isolator_index, eliminated="x") -> tuple[str, str]`
  - `enumerate_immediate_two_stabilizations(pair, max_word_length=2, max_template_length=6) -> TwoStabilizationCensus`

- [ ] **Step 1: Write failing literal-identity tests**

Create:

```python
AK3 = ("xxxYYYY", "xyxYXY")


def test_valid_two_word_braid_factorization():
    assert substitute_new("zxYT", "xy", "yx") == "xyxYXY"


def test_invalid_factor_order_is_quarantined():
    assert substitute_new("zxTY", "xy", "yx") == "xY"
    with pytest.raises(ValueError, match="source relator"):
        derive_rank3(AK3, 1, "xy", "yx", "zxTY")
```

- [ ] **Step 2: Run and require import failure**

Run:

```bash
.venv/bin/python3 -m pytest tests/stable_ac/test_two_stabilization.py -q
```

Expected: FAIL because `two_stabilization.py` does not exist.

- [ ] **Step 3: Implement an independent word layer**

Use alphabet `xXyYzZtT`. Implement stack free reduction locally; do not import
the one-stabilization word functions. Simultaneous substitution must map:

```python
{
    "z": word_z,
    "Z": inverse(word_z),
    "t": word_t,
    "T": inverse(word_t),
}
```

in one pass before free reduction.

- [ ] **Step 4: Write first-removal tests**

Add:

```python
def test_valid_factor_derives_exact_rank3_tuple():
    assert solve_isolator("zxYT", "y") == "Tzx"
    assert derive_rank3(AK3, 1, "xy", "yx", "zxYT") == (
        "xxZtXZtXZtXZt",
        "ZxTzx",
        "TTzxx",
    )
```

The words are still over surviving generators `x,z,t`; do not relabel them
at the rank-3 stage.

- [ ] **Step 5: Implement exact first removal**

Require literal source-orientation equality, exactly one eliminated letter,
and both new generators in the template. Solve the isolator and substitute
in the non-source relator plus both defining relators.

- [ ] **Step 6: Write complete triangular fixture tests**

Use the preflight witness:

```python
def test_known_triangular_certificate_returns_to_ak3_floor():
    rank3 = derive_rank3(AK3, 1, "x", "xy", "ytZT")
    assert rank3[2] == "TxtzT"
    assert solve_isolator(rank3[2], "x") == "ttZT"
    assert remove_second(rank3, 2) == (
        "yyXyXyXXXXXY",
        "XyyXY",
    )
```

Independently check its Aut representative in the certificate layer, not in
the word layer.

- [ ] **Step 7: Implement second removal and relabelling**

Require exactly one `x/X` in the selected rank-3 relator. Solve, substitute in
the other two, and simultaneously rename:

```text
z -> x, Z -> X, t -> y, T -> Y
```

Reject a selected relator with zero or multiple `x/X`.

- [ ] **Step 8: Write bounded-census tests**

Add:

```python
def test_length_two_length_four_census_contains_fixture():
    census = enumerate_immediate_two_stabilizations(
        AK3, max_word_length=2, max_template_length=4
    )
    assert any(
        row.word_z == "x"
        and row.word_t == "xy"
        and row.template == "ytZT"
        and row.second_isolator_index == 2
        for row in census.certificates
    )
    assert census.minimum_output_floor == 13
    assert census.trace_sha256
```

- [ ] **Step 9: Implement deterministic complete enumeration**

Generate reduced defining words in length/alphabet order and structural
templates in length/alphabet order. Count structural templates once. Hash
every:

```text
word_z NUL word_t NUL template NUL expanded NUL source_match
NUL second_index NUL x_count NUL accepted
```

Store every accepted triangular certificate. Track accepted source
identities, distinct rank-3 tuples, triangular-certificate count, distinct
raw outputs, canonical outputs, complete Aut records, floor distribution,
and global minimum.

- [ ] **Step 10: Run focused tests**

Run:

```bash
PYTHONHASHSEED=0 .venv/bin/python3 -m pytest \
  tests/stable_ac/test_two_stabilization.py -q
```

Expected: PASS.

- [ ] **Step 11: Commit and push**

Run:

```bash
git add experiments/stable_ac/rank3_compression/two_stabilization.py tests/stable_ac/test_two_stabilization.py
git commit -m "feat: enumerate triangular two-stabilization corridors"
git push origin codex/proofs
```

---

### Task 3: Build and independently replay the certificate

**Files:**
- Create: `experiments/stable_ac/rank3_compression/two_stabilization_certificate.py`
- Create: `results/stable_ac/theory/ak3_two_stabilization.json`

**Interfaces:**
- Produces:
  - `build_certificate(max_word_length=2, max_template_length=6) -> dict[str, object]`
  - `verify_certificate(data: dict[str, object]) -> None`

- [ ] **Step 1: Write a failing small-certificate test**

Add:

```python
def test_small_two_stabilization_certificate_replays():
    data = build_certificate(max_word_length=1, max_template_length=4)
    assert data["schema"] == "ak3-two-stabilization-v1"
    assert data["defining_word_count"] == 4
    verify_certificate(data)
```

- [ ] **Step 2: Run and require import failure**

Run:

```bash
.venv/bin/python3 -m pytest tests/stable_ac/test_two_stabilization.py -q
```

Expected: FAIL because the certificate module does not exist.

- [ ] **Step 3: Implement compact result serialization**

Store exact bounds, all aggregate counts, trace SHA-256, floor distribution,
one literal witness per distinct raw output, all canonical-output Aut
witnesses, minimum-output records, and the derived `PROVED|REFUTED` verdict.
Do not store eleven million rejected cases.

- [ ] **Step 4: Implement independent row replay**

For every stored output witness:

1. substitute `z,t` literally and match the source orientation;
2. solve `y` afresh;
3. recompute the rank-3 tuple;
4. verify the exact-one-`x` gate;
5. solve `x` and recompute the rank-2 output;
6. verify its canonical and Aut witness.

- [ ] **Step 5: Implement complete fail-closed replay**

Rerun the entire finite enumeration and compare the full derived payload:
bounds, structural-template count, tested cases, accepted identities,
rank-3 count, triangular count, raw/canonical output counts, trace,
floor distribution, minima, and verdict.

- [ ] **Step 6: Add CLI**

Support:

```bash
PYTHONHASHSEED=0 .venv/bin/python3 -m \
  experiments.stable_ac.rank3_compression.two_stabilization_certificate
PYTHONHASHSEED=0 .venv/bin/python3 -m \
  experiments.stable_ac.rank3_compression.two_stabilization_certificate --verify
```

- [ ] **Step 7: Run focused tests and commit code**

Run:

```bash
PYTHONHASHSEED=0 .venv/bin/python3 -m pytest \
  tests/stable_ac/test_two_stabilization.py -q
git add experiments/stable_ac/rank3_compression/two_stabilization_certificate.py tests/stable_ac/test_two_stabilization.py
git commit -m "feat: add two-stabilization certificate"
git push origin codex/proofs
```

- [ ] **Step 8: Build and verify the production result**

Run both CLI commands. Expected preflight-aligned output:

```text
CERTIFICATE WRITTEN: 256 word pairs, 352 outputs, minimum 13, lemma REFUTED
CERTIFICATE VERIFIES: 256 word pairs, 352 outputs, minimum 13, lemma REFUTED
```

- [ ] **Step 9: Run regressions**

Run:

```bash
PYTHONHASHSEED=0 .venv/bin/python3 -m pytest \
  tests/stable_ac/test_two_stabilization.py \
  tests/stable_ac/test_primitive_basis_corridors.py \
  tests/stable_ac/test_rank3_compression.py \
  tests/stable_ac/test_cov.py \
  tests/stable_ac/test_ak3.py -q
```

Expected: PASS.

- [ ] **Step 10: Commit and push the result**

Run:

```bash
git add results/stable_ac/theory/ak3_two_stabilization.json
git commit -m "result: decide immediate AK3 two-stabilizations"
git push origin codex/proofs
```

---

### Task 4: Adjudicate and begin the next mechanism

**Files:**
- Create: `results/stable_ac/theory/AK3_TWO_STABILIZATION.md`

**Interfaces:**
- Consumes: the verified production JSON.
- Produces: the exact verdict and second-stage-compression theorem statement.

- [ ] **Step 1: Record the theorem and exact census**

State the proven triangular-removal theorem, all certificate counts, floor
distribution, minimum orbits, trace, and replay commands.

- [ ] **Step 2: Quarantine the invalid nine-move solve**

Record the literal failed identity and state that no path from it is included
in the certificate.

- [ ] **Step 3: State scope**

For the expected null:

```text
No immediate triangular two-removal certificate in the exact finite class
lands below floor 13. This refutes only the stated finite lemma.
```

- [ ] **Step 4: Start the next theorem**

State:

```text
Second-stage compression theorem [unverified]:
after removing y, one AC-composite replacement using either surviving
defining relator is allowed before testing a remaining relator for its unique
x occurrence.
```

Prove the replacement is still an AC1--AC3 composite and specify the finite
dependency data needed by the next design.

- [ ] **Step 5: Verify, commit, and push**

Run:

```bash
git diff --check
git status --short
git add results/stable_ac/theory/AK3_TWO_STABILIZATION.md
git commit -m "docs: adjudicate immediate AK3 two-stabilizations"
git push origin codex/proofs
```

Leave `prompts/` and `tmp/` untouched and keep the main goal active unless a
full proof/disproof has independently replayed.
