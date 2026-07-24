# AK(3) Primitive-Basis Corridors Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Exactly decide whether any short primitive basis exposes an AK(3) hidden rank-3 corridor with output Aut-floor at most 12.

**Architecture:** A proof note establishes completeness of the Nielsen basis ball and soundness of a signed-permutation quotient. A new basis module emits explicit reduction witnesses for all accepted bases and partitions their AK(3) images into symmetry classes. A certificate driver runs the already-verified corridor census on one representative per class and independently reconstructs the entire basis partition and all corridor summaries.

**Tech Stack:** Python 3 standard library, pytest, existing read-only free-word and corridor verifiers, Markdown, JSON, SHA-256.

## Global Constraints

- Create new task files only; do not modify the corridor engine, existing certificate, solvers, runners, notebooks, tests, or result files.
- Every accepted basis must carry a replayable Nielsen witness.
- The basis ball is exactly `|phi(x)| + |phi(y)| <= 4`.
- The corridor bounds remain exactly `max_word_length = 4`, `max_template_length = 6`, and at least two `z` occurrences.
- A null refutes only the finite primitive-basis lemma.
- A positive is not a solution until a complete AC1--AC5 chain is independently replayed.
- CPU only; use `.venv/bin/python3`.
- Commit and push `codex/proofs` at theorem, implementation, certificate, and adjudication checkpoints, at most twenty minutes apart while tracked changes exist.
- Do not open a pull request or merge.

---

### Task 1: Prove basis-ball completeness and quotient soundness

**Files:**
- Create: `literature/proofs/AK3_PRIMITIVE_BASIS_CORRIDORS.md`

**Interfaces:**
- Consumes: `literature/proofs/AK3_RANK3_COMPRESSION.md` Theorem 3.1.
- Produces: the exact finite theorem implemented by Tasks 2--3.

- [ ] **Step 1: State elementary Nielsen moves**

Use ordered pairs \((u,v)\). Define:

```text
M(target=0, side=right, sign=+1): (u,v) -> (red(uv),v)
M(target=0, side=right, sign=-1): (u,v) -> (red(uv^-1),v)
M(target=0, side=left,  sign=+1): (u,v) -> (red(vu),v)
M(target=0, side=left,  sign=-1): (u,v) -> (red(v^-1u),v)
```

and the four mirror moves targeting component 1.

- [ ] **Step 2: Prove the strict reduction criterion**

Prove that a nonterminal ordered basis of \(F_2\) admits one of the eight
displayed moves that strictly decreases `|u| + |v|`. Iterating terminates.
The pair is a basis exactly when the endpoint consists of two distinct signed
generators. Conversely every recorded move is a Nielsen automorphism, so an
endpoint witness proves the input pair is a basis.

- [ ] **Step 3: Prove finite enumeration completeness**

State that generating every nonempty freely reduced word pair with total
length at most four, then applying the strict criterion, enumerates every
automorphism satisfying the candidate bound. No search path is used to
generate candidates, so an intermediate word-length peak cannot omit a basis.

- [ ] **Step 4: Prove the signed quotient**

Let \(\Sigma\) be the eight signed permutations of \((x,y)\). Prove that:

```text
K(Q) = min{canon(sigma(Q)) : sigma in Sigma}
```

has the same corridor minimum for every pair with the same key. Give the
letterwise bijection on `w`, `I`, the isolated generator, and both output
relators. Include relator order, rotation, and inversion invariance.

- [ ] **Step 5: State the candidate and stopping rule**

State the exact basis/corridor bounds and that `minimum <= 12` proves only the
candidate, while `minimum >= 13` refutes only the candidate.

- [ ] **Step 6: Commit and push**

Run:

```bash
git add -f literature/proofs/AK3_PRIMITIVE_BASIS_CORRIDORS.md
git commit -m "docs: prove primitive-basis corridor quotient"
git push origin codex/proofs
```

---

### Task 2: Implement the replayable Nielsen basis census by TDD

**Files:**
- Create: `experiments/stable_ac/rank3_compression/primitive_bases.py`
- Create: `tests/stable_ac/test_primitive_basis_corridors.py`

**Interfaces:**
- Produces:
  - `NielsenMove(target: int, side: str, sign: int)`
  - `apply_nielsen(pair: tuple[str, str], move: NielsenMove) -> tuple[str, str]`
  - `nielsen_reduce(pair: tuple[str, str]) -> tuple[NielsenMove, ...] | None`
  - `replay_nielsen(pair: tuple[str, str], moves: tuple[NielsenMove, ...]) -> tuple[str, str]`
  - `enumerate_bases(max_total: int = 4) -> tuple[BasisRecord, ...]`
  - `apply_basis(pair: tuple[str, str], basis: tuple[str, str]) -> tuple[str, str]`
  - `signed_pair_key(pair: tuple[str, str]) -> tuple[str, str]`
  - `primitive_basis_classes(pair: tuple[str, str], max_total: int = 4) -> tuple[BasisClass, ...]`

- [ ] **Step 1: Write failing Nielsen tests**

Create:

```python
AK3 = ("xxxYYYY", "xyxYXY")


def test_nielsen_witness_reduces_a_basis():
    moves = nielsen_reduce(("x", "xy"))
    assert moves is not None
    assert replay_nielsen(("x", "xy"), moves) in {
        ("x", "y"), ("x", "Y"), ("X", "y"), ("X", "Y"),
        ("y", "x"), ("y", "X"), ("Y", "x"), ("Y", "X"),
    }


def test_nielsen_rejects_nonbasis():
    assert nielsen_reduce(("xx", "y")) is None
```

- [ ] **Step 2: Run and require import failure**

Run:

```bash
.venv/bin/python3 -m pytest tests/stable_ac/test_primitive_basis_corridors.py -q
```

Expected: FAIL because `primitive_bases.py` does not exist.

- [ ] **Step 3: Implement deterministic Nielsen moves**

Use `corridors.free_reduce` and `corridors.inverse`. Generate the eight
multiplication moves in this order:

```python
for target in (0, 1):
    for side in ("right", "left"):
        for sign in (1, -1):
            ...
```

At each reduction step, keep only children with strictly smaller total
length and choose the minimum by:

```python
(total_length, child_pair, target, side, sign)
```

Return `None` if no decreasing child exists and the current pair is not a
signed standard basis.

- [ ] **Step 4: Add replay and tamper tests**

Add:

```python
def test_nielsen_replay_is_exact():
    start = ("xy", "x")
    moves = nielsen_reduce(start)
    assert moves is not None
    assert all(
        sum(map(len, states[i + 1])) < sum(map(len, states[i]))
        for i in range(len(moves))
    )


def test_bad_nielsen_move_is_rejected():
    with pytest.raises(ValueError):
        apply_nielsen(("x", "y"), NielsenMove(2, "right", 1))
```

Expose `nielsen_states` or construct the states in the test by applying each
move; do not add a test-only production method.

- [ ] **Step 5: Write the exact basis-count test**

Add:

```python
def test_complete_total_four_basis_ball():
    bases = enumerate_bases(4)
    assert len(bases) == 200
    assert all(sum(map(len, row.basis)) <= 4 for row in bases)
    assert all(
        _is_signed_standard(replay_nielsen(row.basis, row.moves))
        for row in bases
    )
```

Use a local test helper for `_is_signed_standard`.

- [ ] **Step 6: Implement candidate generation and basis application**

Generate all nonempty freely reduced words over `xXyY` in length order,
then every ordered pair within the total cap. Accept only pairs with a
Nielsen witness. `apply_basis` must perform simultaneous substitution:

```python
x -> basis[0]
y -> basis[1]
X -> inverse(basis[0])
Y -> inverse(basis[1])
```

followed by free reduction.

- [ ] **Step 7: Write the signed-quotient tests**

Add:

```python
def test_total_four_basis_classes():
    classes = primitive_basis_classes(AK3, 4)
    assert len(classes) == 9
    assert sorted(len(cls.members) for cls in classes) == [
        16, 16, 16, 16, 24, 24, 24, 24, 40,
    ]
    assert sum(len(cls.members) for cls in classes) == 200


def test_signed_renaming_preserves_key():
    pair = apply_basis(AK3, ("x", "xy"))
    renamed = apply_basis(pair, ("Y", "x"))
    assert signed_pair_key(pair) == signed_pair_key(renamed)
```

- [ ] **Step 8: Implement the eight-image key and classes**

Construct the eight signed maps explicitly. Apply each simultaneously to
both relators, canonicalize with existing `acmoves.canon`, and take the
lexicographic minimum. Sort classes by key and members by basis.

- [ ] **Step 9: Run focused tests**

Run:

```bash
PYTHONHASHSEED=0 .venv/bin/python3 -m pytest \
  tests/stable_ac/test_primitive_basis_corridors.py -q
```

Expected: PASS.

- [ ] **Step 10: Commit and push**

Run:

```bash
git add experiments/stable_ac/rank3_compression/primitive_bases.py tests/stable_ac/test_primitive_basis_corridors.py
git commit -m "feat: certify primitive basis ball"
git push origin codex/proofs
```

---

### Task 3: Build and replay the nine-class corridor certificate

**Files:**
- Create: `experiments/stable_ac/rank3_compression/primitive_certificate.py`
- Create: `results/stable_ac/theory/ak3_primitive_basis_corridors.json`

**Interfaces:**
- Produces:
  - `build_certificate(max_basis_total: int = 4, max_word_length: int = 4, max_template_length: int = 6, progress=None) -> dict[str, object]`
  - `verify_certificate(data: dict[str, object], progress=None) -> None`

- [ ] **Step 1: Write a failing small-certificate test**

Add:

```python
def test_small_primitive_certificate_replays():
    data = build_certificate(
        max_basis_total=2,
        max_word_length=2,
        max_template_length=4,
    )
    assert data["schema"] == "ak3-primitive-basis-corridors-v1"
    assert data["basis_count"] == 8
    assert data["class_count"] == 1
    verify_certificate(data)
```

- [ ] **Step 2: Run and require import failure**

Run:

```bash
.venv/bin/python3 -m pytest tests/stable_ac/test_primitive_basis_corridors.py -q
```

Expected: FAIL because `primitive_certificate.py` does not exist.

- [ ] **Step 3: Implement basis and partition serialization**

Each basis row stores:

```json
{
  "basis": ["x", "xy"],
  "moves": [{"target": 1, "side": "left", "sign": -1}],
  "transformed_pair": ["...", "..."],
  "class_key": ["...", "..."]
}
```

Hash the sorted rows as canonical compact JSON to form `partition_sha256`.

- [ ] **Step 4: Implement one class summary**

For each class key, call `enumerate_short_corridors`. Store:

```json
{
  "key": ["...", "..."],
  "member_count": 0,
  "enumerated_templates": 2851840,
  "accepted_count": 0,
  "trace_sha256": "",
  "minimum_output_floor": null,
  "output_orbits": [],
  "minimum_corridors": []
}
```

Group `census.aut_records` by representative. A minimum corridor is any
accepted row whose canonical output belongs to an Aut record at the class
minimum. Store every such row.

- [ ] **Step 5: Derive the global verdict**

The top-level schema contains:

```json
{
  "schema": "ak3-primitive-basis-corridors-v1",
  "claim": "finite decision of the stated primitive-basis lemma only",
  "basis_bound": 4,
  "corridor_bounds": {
    "max_word_length": 4,
    "max_template_length": 6,
    "minimum_z_occurrences": 2
  },
  "basis_count": 200,
  "class_count": 9,
  "class_sizes": [16,16,16,16,24,24,24,24,40],
  "partition_sha256": "",
  "bases": [],
  "classes": [],
  "global_minimum_output_floor": null,
  "candidate_lemma": "PROVED|REFUTED"
}
```

Set `PROVED` exactly when the global minimum is not null and is at most 12.

- [ ] **Step 6: Implement fail-closed replay**

The verifier regenerates the complete basis ball and compares every stored
basis, move, transformed pair, class key, class size, and partition digest.
For every class it reruns the complete corridor census and compares the
entire derived summary. Finally it recomputes the global minimum and verdict.

- [ ] **Step 7: Add progress reporting and CLI**

Support:

```bash
PYTHONHASHSEED=0 .venv/bin/python3 -m \
  experiments.stable_ac.rank3_compression.primitive_certificate
PYTHONHASHSEED=0 .venv/bin/python3 -m \
  experiments.stable_ac.rank3_compression.primitive_certificate --verify
```

Before each class, print `CLASS i/9: <key>` so a full build/replay never
appears stalled.

- [ ] **Step 8: Run the focused test**

Run:

```bash
PYTHONHASHSEED=0 .venv/bin/python3 -m pytest \
  tests/stable_ac/test_primitive_basis_corridors.py -q
```

Expected: PASS.

- [ ] **Step 9: Commit code before the production result**

Run:

```bash
git add experiments/stable_ac/rank3_compression/primitive_certificate.py tests/stable_ac/test_primitive_basis_corridors.py
git commit -m "feat: add primitive-basis corridor certificate"
git push origin codex/proofs
```

- [ ] **Step 10: Build and replay the full certificate**

Run both CLI commands. Expected:

```text
CERTIFICATE WRITTEN: 200 bases, 9 classes, ...
CERTIFICATE VERIFIES: 200 bases, 9 classes, ...
```

The minimum and lemma verdict are discovered by this run.

- [ ] **Step 11: Run regressions**

Run:

```bash
PYTHONHASHSEED=0 .venv/bin/python3 -m pytest \
  tests/stable_ac/test_primitive_basis_corridors.py \
  tests/stable_ac/test_rank3_compression.py \
  tests/stable_ac/test_cov.py \
  tests/stable_ac/test_ak3.py -q
```

Expected: PASS.

- [ ] **Step 12: Commit and push the result**

Run:

```bash
git add results/stable_ac/theory/ak3_primitive_basis_corridors.json
git commit -m "result: decide primitive-basis AK3 corridors"
git push origin codex/proofs
```

---

### Task 4: Adjudicate and continue

**Files:**
- Create: `results/stable_ac/theory/AK3_PRIMITIVE_BASIS_CORRIDORS.md`

**Interfaces:**
- Consumes: the verified JSON result.
- Produces: the exact lemma verdict and next theorem attempt.

- [ ] **Step 1: Record exact evidence**

Include the basis count, class count/sizes, partition digest, every class
minimum, global minimum, and corridor trace hashes.

- [ ] **Step 2: State scope**

For a null, write:

```text
No basis within total image length four exposes a corridor within the exact
corridor bounds whose output floor is at most 12. This refutes only the finite
primitive-basis lemma; it is not an AC or stable-AC obstruction.
```

- [ ] **Step 3: Follow the verdict**

For `PROVED`, expand the minimum witness into a stable chain and attach an
independently replayed classical certificate.

For `REFUTED`, begin the two-stabilization simultaneous-isolator theorem:

```text
Adjoin z=w1 and t=w2. Compress the two source relators to templates I1,I2
that isolate the two old basis generators in a triangular order. Remove the
old generators by two Lemma-11 applications. Classify the acyclic dependency
condition that makes both removals legal.
```

- [ ] **Step 4: Verify scope and commit**

Run:

```bash
git diff --check
git status --short
git add results/stable_ac/theory/AK3_PRIMITIVE_BASIS_CORRIDORS.md
git commit -m "docs: adjudicate primitive-basis AK3 lemma"
git push origin codex/proofs
```

Leave pre-existing `prompts/` and `tmp/` untouched. Keep the main goal active
unless an actual full proof/disproof has passed.
