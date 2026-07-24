# AK(3) Rank-3 Compression Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove the hidden-cancellation rank-3 corridor theorem, exactly decide the first short-corridor lemma for AK(3), and either expand a resulting stable trivialization certificate or preserve the exact falsifier and start the primitive-isolator lemma.

**Architecture:** A load-bearing proof note defines a general one-stabilization corridor in free-group words. A new dependency-light enumerator decides the finite short-corridor statement and emits complete trace data. A separate certificate layer independently reconstructs every accepted word identity and reruns the full enumeration before any mathematical claim is recorded.

**Tech Stack:** Python 3 standard library, pytest, existing read-only `autcanon` checker, Markdown, JSON, SHA-256.

## Global Constraints

- Create new task files only; do not modify existing solvers, runners, notebooks, tests, or result files.
- Use exact free-group reduction; do not confuse freely equal spellings with distinct relators.
- No local AC graph search may exceed `node_budget = 1000`; the corridor enumeration is a finite word-equation decision, not an AC search.
- A bounded null falsifies only the stated short-corridor lemma.
- A positive is not a solution until the full AC1--AC5 chain is independently replayed.
- CPU only; use `.venv/bin/python3`.
- Commit and push `codex/proofs` at least every twenty minutes while tracked changes exist.
- Do not create a pull request or merge.

---

### Task 1: Prove the rank-3 corridor theorem

**Files:**
- Create: `literature/proofs/AK3_RANK3_COMPRESSION.md`

**Interfaces:**
- Consumes: `literature/proofs/PROOFS.tex` Proposition `prop:lem11` and Theorem `thm:stable`.
- Produces: the exact theorem and substitution formulas implemented by Task 2.

- [ ] **Step 1: State the word conventions**

Write:

```text
inv(u_1...u_n)=u_n^{-1}...u_1^{-1};
red is ordinary free reduction;
sub_z(I,w)=red(I[z->w,Z->inv(w)]);
relators are compared up to cyclic rotation and inversion only after red.
```

- [ ] **Step 2: Prove the corridor theorem**

Prove that if `sub_z(I,w)` is a source relator and `I` has one
`b^{+-1}`, rotating `I=b^eps q` gives:

```text
expr = inv(q) if eps == +1 else q
output_1 = red(substitute(other_relator, b, expr))
output_2 = red(substitute(inv("z") + w, b, expr))
```

Give the AC proof as generalized stabilization, explicit occurrence
substitutions, Lemma-11 removal, and stable relabeling.

- [ ] **Step 3: Work the AK(3) witness letter by letter**

Record:

```text
A = xxxYYYY
B = xyxYXY
w = xy
I = zxZY
sub_z(I,w) = xyxYXY
expr(y) = zxZ
output = xxxzXXXXZ | ZxzxZ
relabel(z->y) = xxxyXXXXY | YxyxY
```

Verify the displayed reductions manually in the note.

- [ ] **Step 4: State the exact finite lemma and its scope**

Copy the bounds `1 <= |w| <= 4`, `2 <= |I| <= 6`, exactly one eliminated
generator, and at least two `z` letters. State that a null is not an AC
obstruction.

- [ ] **Step 5: Commit the theorem note**

Run:

```bash
git add literature/proofs/AK3_RANK3_COMPRESSION.md
git commit -m "docs: prove rank3 corridor transform"
git push origin codex/proofs
```

Expected: only the new proof note is committed and pushed.

---

### Task 2: Implement exact corridor primitives by TDD

**Files:**
- Create: `experiments/stable_ac/rank3_compression/__init__.py`
- Create: `experiments/stable_ac/rank3_compression/corridors.py`
- Create: `tests/stable_ac/test_rank3_compression.py`

**Interfaces:**
- Produces:
  - `inverse(word: str) -> str`
  - `free_reduce(word: str) -> str`
  - `cyclic_orientations(word: str) -> tuple[str, ...]`
  - `substitute_generator(word: str, generator: str, expr: str) -> str`
  - `substitute_z(template: str, word: str) -> str`
  - `solve_isolator(template: str, eliminated: str) -> str`
  - `corridor_output(pair: tuple[str, str], source_index: int, word: str, template: str, eliminated: str) -> tuple[str, str]`
  - `enumerate_short_corridors(pair: tuple[str, str], max_word_length: int = 4, max_template_length: int = 6) -> CorridorCensus`

- [ ] **Step 1: Write failing word-algebra tests**

Add:

```python
def test_free_word_primitives():
    assert inverse("xyX") == "xYX"
    assert free_reduce("xyYX") == ""
    assert substitute_z("zxZY", "xy") == "xyxYXY"


def test_ak3_corridor_output():
    pair = ("xxxYYYY", "xyxYXY")
    assert corridor_output(pair, 1, "xy", "zxZY", "y") == (
        "xxxyXXXXY", "YxyxY",
    )
```

- [ ] **Step 2: Run the focused tests and require import failure**

Run:

```bash
.venv/bin/python3 -m pytest tests/stable_ac/test_rank3_compression.py -q
```

Expected: FAIL because `rank3_compression.corridors` does not exist.

- [ ] **Step 3: Implement the minimal exact word layer**

Use the following validation and reduction rules:

```python
ALPHABET = frozenset("xXyYzZ")

def inverse(word):
    return "".join(c.swapcase() for c in reversed(word))

def free_reduce(word):
    stack = []
    for c in word:
        if c not in ALPHABET:
            raise ValueError(f"invalid letter: {c!r}")
        if stack and stack[-1] == c.swapcase():
            stack.pop()
        else:
            stack.append(c)
    return "".join(stack)
```

`cyclic_orientations` must free-reduce first and return the sorted distinct
rotations of the word and inverse.

- [ ] **Step 4: Implement isolator solution and corridor output**

Find the unique index whose lowercase letter equals `eliminated`, rotate it
to the front, require the remaining suffix to be eliminated-generator-free,
and return `inverse(suffix)` for a lowercase leading letter or `suffix` for
an uppercase leading letter. Reject zero or multiple occurrences.

For the output, independently require:

```python
substitute_z(template, word) in cyclic_orientations(pair[source_index])
template.count("z") + template.count("Z") >= 1
```

Substitute the solved expression in the non-source relator and in
`"Z" + word`, free-reduce both, replace `z/Z` by the eliminated generator
and its inverse, and return the pair.

- [ ] **Step 5: Write finite-enumerator tests**

Add:

```python
def test_short_enumerator_contains_hidden_ak3_witness():
    census = enumerate_short_corridors(
        ("xxxYYYY", "xyxYXY"), max_word_length=2, max_template_length=4
    )
    assert any(
        row.word == "xy"
        and row.template == "zxZY"
        and row.output == ("xxxyXXXXY", "YxyxY")
        for row in census.accepted
    )
    assert census.enumerated_templates > 0
    assert census.trace_sha256


def test_one_z_templates_are_excluded():
    census = enumerate_short_corridors(
        ("xxxYYYY", "xyxYXY"), max_word_length=2, max_template_length=3
    )
    assert all(row.template.count("z") + row.template.count("Z") >= 2
               for row in census.accepted)
```

- [ ] **Step 6: Implement deterministic enumeration**

Generate freely reduced words in length/lexicographic order with alphabet
order `x,X,y,Y`. Generate freely and cyclically reduced templates in
length/lexicographic order over `x,X,y,Y,z,Z`. For each eliminated generator,
require exactly one occurrence in either sign and at least two `z` letters.
Hash every tested tuple:

```text
source_index NUL eliminated NUL word NUL template NUL substituted NUL accepted
```

Store accepted rows in this same order. The census records bounds,
`enumerated_templates`, `accepted_count`, and `trace_sha256`.

- [ ] **Step 7: Attach exact Aut-floor data after word enumeration**

Deduplicate outputs first. For each distinct output, call the existing
read-only `aut_canon(output)` and record:

```python
AutRecord(
    output=output,
    minimum_total=minimum_total,
    representative=representative,
    phi=phi,
)
```

Do not use Aut data to prune enumeration.

- [ ] **Step 8: Run focused tests**

Run:

```bash
PYTHONHASHSEED=0 .venv/bin/python3 -m pytest tests/stable_ac/test_rank3_compression.py -q
```

Expected: PASS.

- [ ] **Step 9: Commit and push the exact enumerator**

Run:

```bash
git add experiments/stable_ac/rank3_compression tests/stable_ac/test_rank3_compression.py
git commit -m "feat: enumerate hidden rank3 corridors"
git push origin codex/proofs
```

---

### Task 3: Build and replay the short-corridor certificate

**Files:**
- Create: `experiments/stable_ac/rank3_compression/certificate.py`
- Create: `results/stable_ac/theory/ak3_rank3_corridors.json`

**Interfaces:**
- Consumes: `CorridorCensus.to_json()`.
- Produces:
  - `build_certificate() -> dict[str, object]`
  - `verify_certificate(data: dict[str, object]) -> None`

- [ ] **Step 1: Write failing certificate tests**

Add to the new test file:

```python
def test_certificate_replays(tmp_path):
    data = build_certificate()
    assert data["schema"] == "ak3-rank3-corridors-v1"
    assert data["pair"] == ["xxxYYYY", "xyxYXY"]
    assert data["bounds"] == {"max_word_length": 4,
                              "max_template_length": 6,
                              "minimum_z_occurrences": 2}
    verify_certificate(data)
```

- [ ] **Step 2: Run the test and require import failure**

Run:

```bash
.venv/bin/python3 -m pytest tests/stable_ac/test_rank3_compression.py -q
```

Expected: FAIL because `certificate.py` does not exist.

- [ ] **Step 3: Implement certificate construction**

The schema must contain:

```json
{
  "schema": "ak3-rank3-corridors-v1",
  "claim": "finite decision of the stated short-corridor lemma only",
  "pair": ["xxxYYYY", "xyxYXY"],
  "bounds": {
    "max_word_length": 4,
    "max_template_length": 6,
    "minimum_z_occurrences": 2
  },
  "enumerated_templates": 0,
  "accepted_count": 0,
  "trace_sha256": "",
  "accepted": [],
  "aut_orbits": [],
  "minimum_output_floor": null,
  "candidate_lemma": "PROVED|REFUTED"
}
```

Set `PROVED` exactly when `minimum_output_floor` is not null and is at most
12; otherwise set `REFUTED`. Never use `SOLVED`.

- [ ] **Step 4: Implement independent row replay**

For every accepted JSON row, recompute `I[z->w]`, solve the isolator, and
recompute the output without trusting its recorded output. Verify each Aut
witness with `autcanon.check`. Then rerun `enumerate_short_corridors` and
compare the full JSON payload except for source metadata.

- [ ] **Step 5: Add the CLI and write the result**

Support:

```bash
.venv/bin/python3 -m experiments.stable_ac.rank3_compression.certificate
.venv/bin/python3 -m experiments.stable_ac.rank3_compression.certificate --verify
```

The first command writes
`results/stable_ac/theory/ak3_rank3_corridors.json`; the second reads and
verifies it.

- [ ] **Step 6: Run the complete certificate**

Run both commands. Expected:

```text
CERTIFICATE WRITTEN: ...
CERTIFICATE VERIFIES: ...
```

The candidate-lemma verdict is discovered by this run.

- [ ] **Step 7: Run all focused regression tests**

Run:

```bash
PYTHONHASHSEED=0 .venv/bin/python3 -m pytest \
  tests/stable_ac/test_rank3_compression.py \
  tests/stable_ac/test_cov.py \
  tests/stable_ac/test_ak3.py -q
```

Expected: PASS.

- [ ] **Step 8: Commit and push the certificate**

Run:

```bash
git add experiments/stable_ac/rank3_compression/certificate.py results/stable_ac/theory/ak3_rank3_corridors.json tests/stable_ac/test_rank3_compression.py
git commit -m "result: decide short AK3 rank3 corridors"
git push origin codex/proofs
```

---

### Task 4: Adjudicate the lemma and continue the proof loop

**Files:**
- Create: `results/stable_ac/theory/AK3_RANK3_COMPRESSION.md`

**Interfaces:**
- Consumes: the verified JSON certificate.
- Produces: an exact theorem/falsifier report and the next proof lemma.

- [ ] **Step 1: State the discovered verdict exactly**

If `candidate_lemma == "PROVED"`, name the witness and state only that it
lands at an Aut-floor at most 12. If it is `REFUTED`, state:

```text
No corridor within the theorem's exact bounds lands at Aut-floor <= 12.
This refutes the short-corridor lemma and says nothing about longer
corridors or stable AC in general.
```

- [ ] **Step 2: Preserve the structural AK(3) corollary**

Regardless of the finite verdict, state and prove:

```text
AK(3) ~st <x,y | xxxyXXXXY, YxyxY>.
```

Record its exact Aut-floor and representative from the certificate.

- [ ] **Step 3: Follow the correct proof branch**

For a proved candidate lemma, construct a classical AC certificate from the
floor-at-most-12 endpoint to standard, prepend the explicit corridor, and
require an independent AC1--AC5 replay before making any resolution claim.

For a refuted candidate lemma, state the next candidate:

```text
Primitive-isolator corridor lemma [unverified]:
there is a one-stabilization corridor I=z u z^-1 v^-1 for AK(3),
where v is primitive with an explicit Nielsen witness, whose normalized
rank-2 output has Aut-floor <= 12.
```

The next plan must classify primitive `v` by Nielsen reduction rather than
increase `|w|` or `|I|` blindly.

- [ ] **Step 4: Verify documentation and repository scope**

Run:

```bash
git diff --check
git status --short
```

Expected: only the new task files are modified or untracked; pre-existing
`prompts/` and `tmp/` remain untouched.

- [ ] **Step 5: Commit and push the adjudication**

Run:

```bash
git add results/stable_ac/theory/AK3_RANK3_COMPRESSION.md
git commit -m "docs: adjudicate AK3 rank3 compression lemma"
git push origin codex/proofs
```

- [ ] **Step 6: Keep the main research goal active**

Do not mark the goal complete unless the full stable/classical certificate
or a genuine all-moves invariant proof has passed independent verification.
