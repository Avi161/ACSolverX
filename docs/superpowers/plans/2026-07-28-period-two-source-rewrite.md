# Period-Two Exact Source Rewrite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Promote the exact complete-cover subgroup rewrite and balanced-source census into tracked certificate code, reproducing the depth-six fifteen-bit census without scratch imports.

**Architecture:** Three modules separate subgroup algebra, source-flow reconstruction, and obstruction census.  The first two expose exact deterministic interfaces; the census consumes them and the existing Result 157 obstruction constants, using projected wedge evaluation before the full wedge-sum check.

**Tech Stack:** Python 3, existing sparse group-ring certificate modules, dataclasses, `hashlib.sha256`, pytest through isolated `uv run`.

## Global Constraints

- Work only in the existing `codex/proofs` linked worktree.
- Do not import any `.scratch` module from tracked code or tests.
- Do not use bounded-radius subgroup search; every forest path comes from the complete Stallings cover.
- Keep the census explicitly scoped to source-word depth six.
- Set `PYTHONPYCACHEPREFIX=.scratch/pycache` for every Python command.
- Run pytest through approved `uv run --with numba --with numpy --with pytest`.
- Add new proof notes under ignored `literature/proofs/` with a separate `git add -f`.
- Preserve the original open-problem scope: no claim about all source depths, stable AC, or AC.

## File Structure

- Create `experiments/stable_ac/depth4_period_two_subgroup_rewrite_certificate.py`: semidirect normal form, complete-core coordinates, Nielsen inverse, exact (K)-rewrite, forest path construction.
- Create `tests/stable_ac/test_ak_depth_four_period_two_subgroup_rewrite.py`: cover, round-trip, and fixed-path tests.
- Create `experiments/stable_ac/depth4_period_two_source_flow_certificate.py`: source vertices, orbit signatures, boundary pairing, and homogeneous edge-flow reconstruction.
- Create `tests/stable_ac/test_ak_depth_four_period_two_source_flow.py`: six action classes, signatures, balanced-pair and Result 153--157 reconstruction tests.
- Create `experiments/stable_ac/depth4_period_two_depth6_l0_census_certificate.py`: fourteen projected bits, final wedge-sum bit, complete depth-six census, deterministic hash.
- Create `tests/stable_ac/test_ak_depth_four_period_two_depth6_l0_census.py`: counts, near-survivors, zero-survivor and hash tests.
- Modify `literature/proofs/AK3_DEPTH4_PERIOD_TWO_DEPTH6_BALANCED_L0_CENSUS.md`: replace the research-only status with tracked checker details while retaining bounded scope.
- Modify `results/stable_ac/theory/AK3_DEPTH4_HANDOFF.md`: point the next continuation at the all-depth transition-state derivation.
- Modify `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`: record the tracked certificate and hash.

---

### Task 1: Exact complete-cover subgroup rewrite

**Files:**
- Create: `experiments/stable_ac/depth4_period_two_subgroup_rewrite_certificate.py`
- Create: `tests/stable_ac/test_ak_depth_four_period_two_subgroup_rewrite.py`

**Interfaces:**
- Consumes: `depth4_period_two_binomial_forest_certificate`, `depth4_period_two_degree_two_escape_certificate`, and `depth4_period_two_phi4_escape_certificate`.
- Produces: `q_normal_form(word) -> tuple[tuple[int, ...], int]`, `in_k(value) -> bool`, `rewrite_k(value) -> tuple[int, ...]`, `path_between(start, end) -> str`, `subgroup_rewrite_certificate() -> PeriodTwoSubgroupRewriteCertificate`.

- [ ] **Step 1: Write the failing fixed-path and cover test**

```python
from experiments.stable_ac.depth4_period_two_subgroup_rewrite_certificate import (
    CORE,
    CORE_BASE,
    path_between,
    subgroup_rewrite_certificate,
)
from experiments.stable_ac import depth4_period_two_degree_two_escape_certificate as escape


def test_complete_cover_and_fixed_paths() -> None:
    certificate = subgroup_rewrite_certificate()
    assert certificate.core_vertices == 4
    assert certificate.core_directed_edges == 16
    assert certificate.core_free_rank == 5
    assert certificate.fixed_paths == (
        ("ctcTcttct", "aGbaGaGbAA", "tt"),
        ("ttct", "aaBgA", "ctcTctt"),
        ("", "aaBgA", "ctcTctcTT"),
        ("ctcT", "aGaGbA", "tcTT"),
    )
```

- [ ] **Step 2: Run the test and verify the module is missing**

Run:

```bash
PYTHONPYCACHEPREFIX=.scratch/pycache uv run --with numba --with numpy --with pytest python3 -m pytest -q tests/stable_ac/test_ak_depth_four_period_two_subgroup_rewrite.py
```

Expected: collection fails with `ModuleNotFoundError` for the new certificate.

- [ ] **Step 3: Implement exact semidirect and core rewriting**

Implement these exact types and functions:

```python
HWord = tuple[int, ...]
Semidirect = tuple[HWord, int]


def q_normal_form(word: lift.Word) -> Semidirect: ...
def q_inverse(value: Semidirect) -> Semidirect: ...
def q_multiply(left: Semidirect, right: Semidirect) -> Semidirect: ...
def in_k(value: Semidirect) -> bool: ...
def evaluate_k_word(word: tuple[int, ...]) -> Semidirect: ...
def rewrite_k(value: Semidirect) -> tuple[int, ...]: ...
def path_between(start: lift.Word, end: lift.Word) -> str: ...
```

Use the complete core from `forest.fold` and `forest.prune_core`.  Build a spanning tree, assign one free generator to every non-tree edge, invert the five Reidemeister--Schreier images by strictly length-reducing Nielsen moves, and assert `evaluate_k_word(rewrite_k(value)) == value`.

- [ ] **Step 4: Add exhaustive depth-six round-trip coverage**

```python
def test_depth_six_k_words_round_trip() -> None:
    certificate = subgroup_rewrite_certificate()
    assert certificate.depth_six_words_checked == 127
    assert certificate.depth_six_k_elements > 0
    assert certificate.depth_six_round_trips == certificate.depth_six_k_elements
```

The certificate enumerates canonical quotient vertices through depth six, checks every normal form accepted by `in_k`, and round-trips it through `rewrite_k`.

- [ ] **Step 5: Run the focused test**

Run the Task 1 pytest command.  Expected: all tests pass.

- [ ] **Step 6: Commit and push Task 1**

```bash
git add experiments/stable_ac/depth4_period_two_subgroup_rewrite_certificate.py tests/stable_ac/test_ak_depth_four_period_two_subgroup_rewrite.py
git commit -m "Certify exact period-two subgroup rewrite"
git push origin codex/proofs
```

---

### Task 2: Source orbit signatures and homogeneous edge flows

**Files:**
- Create: `experiments/stable_ac/depth4_period_two_source_flow_certificate.py`
- Create: `tests/stable_ac/test_ak_depth_four_period_two_source_flow.py`

**Interfaces:**
- Consumes: `path_between` from Task 1 and existing period-two operators.
- Produces: `source_vertices(max_depth) -> tuple[lift.Word, ...]`, `orbit_sums(boundary) -> tuple[int, int]`, `paired_boundaries(boundary)`, `build_l0_direction(source) -> SourceFlowDirection`, `source_flow_certificate() -> PeriodTwoSourceFlowCertificate`.

- [ ] **Step 1: Write the failing action-class test**

```python
def test_six_vertex_action_classes_and_signatures() -> None:
    certificate = source_flow_certificate()
    assert certificate.vertex_action_classes == 6
    assert certificate.representative_signatures == (
        ("", (2, -2), (1, -1)),
        ("T", (1, -1), (-1, 1)),
        ("t", (-1, 1), (0, 0)),
        ("cT", (-1, 1), (1, -1)),
        ("ct", (1, -1), (0, 0)),
        ("Tct", (-2, 2), (-1, 1)),
    )
```

- [ ] **Step 2: Run the focused test and verify failure**

Run:

```bash
PYTHONPYCACHEPREFIX=.scratch/pycache uv run --with numba --with numpy --with pytest python3 -m pytest -q tests/stable_ac/test_ak_depth_four_period_two_source_flow.py
```

Expected: collection fails because the module does not exist.

- [ ] **Step 3: Implement canonical vertices, action classes, and pairing**

```python
def source_vertices(max_depth: int) -> tuple[lift.Word, ...]: ...
def vertex_action_class(word: lift.Word) -> tuple[int, ...]: ...
def orbit_sums(boundary: lift.ModuleVector) -> tuple[int, int]: ...
def paired_boundaries(boundary: lift.ModuleVector) -> tuple[tuple[lift.Word, lift.Word], ...] | None: ...
```

Use canonical `lift.c_vertex` reduction after each left multiplication by `c`, `t`, or `T`.  Sort words by discovery depth, reduced length, then tuple order.  Pair negative and positive boundary entries within each of the two phi4 orbit components.

- [ ] **Step 4: Implement exact (L_0) direction reconstruction**

```python
@dataclass(frozen=True)
class SourceFlowDirection:
    source: tuple[tuple[str, int], ...]
    paths: tuple[tuple[str, str, str], ...]
    variables: escape.ModuleVariables


def build_l0_direction(source: dict[lift.Word, int]) -> SourceFlowDirection: ...
```

Apply `operators[0]`, require zero orbit sums, call `path_between` for every paired endpoint, convert `A/a/B/b/G/g` edges into components `4/2/3`, and assert the total correction image is empty.

- [ ] **Step 5: Add known-direction fixtures**

```python
def test_result_153_through_157_sources_reconstruct() -> None:
    fixtures = (
        (("T", 1), ("ttttct", 1)),
        (("T", 1), ("TTct", 1)),
        (("TT", 1), ("tcTct", 1)),
        (("cT", 1), ("TcTTT", 1)),
        (("TTcttt", 1), ("cTcTct", 1)),
    )
    certificate = source_flow_certificate()
    assert certificate.known_sources == fixtures
    assert certificate.known_reconstructions == 5
```

- [ ] **Step 6: Run Task 1 and Task 2 tests**

Run both focused test files.  Expected: all pass.

- [ ] **Step 7: Commit and push Task 2**

```bash
git add experiments/stable_ac/depth4_period_two_source_flow_certificate.py tests/stable_ac/test_ak_depth_four_period_two_source_flow.py
git commit -m "Certify period-two source flows"
git push origin codex/proofs
```

---

### Task 3: Projected fifteen-bit evaluator and depth-six census

**Files:**
- Create: `experiments/stable_ac/depth4_period_two_depth6_l0_census_certificate.py`
- Create: `tests/stable_ac/test_ak_depth_four_period_two_depth6_l0_census.py`

**Interfaces:**
- Consumes: Task 2 `source_vertices`, `orbit_sums`, and `build_l0_direction`; Result 147--157 action/covector constants.
- Produces: `projected_wedge(kernel_word, action, prime=2)`, `projected_fourteen_bits(kernel_word)`, `depth6_l0_census_certificate() -> PeriodTwoDepth6L0CensusCertificate`.

- [ ] **Step 1: Write the failing projected/direct agreement test**

```python
def test_projected_bits_match_direct_wedge_on_known_directions() -> None:
    certificate = depth6_l0_census_certificate()
    assert certificate.projected_direct_fixtures == 5
    assert certificate.projected_direct_matches == 5
```

Each fixture constructs its Schreier kernel, evaluates fourteen projected bits directly, constructs the full wedge, and asserts equality with `eleven.obstruction_bits(wedge)[1:]`.

- [ ] **Step 2: Write the failing census test with the pinned hash**

```python
def test_depth_six_balanced_l0_census() -> None:
    certificate = depth6_l0_census_certificate()
    assert certificate.max_source_depth == 6
    assert certificate.source_vertices == 127
    assert certificate.balanced_pairs == 4671
    assert certificate.projected_near_survivors == (
        ("TT", "TTTct", 1, 1),
        ("Tctt", "Tctct", 1, 1),
    )
    assert certificate.zero_syndrome_pairs == ()
    assert certificate.census_sha256 == (
        "02a688c2e0bfd1831202c6b76f8d3af9b4340c71e08d9b1e2efeea59d8301ff3"
    )
```

- [ ] **Step 3: Run the focused test and verify failure**

Run:

```bash
PYTHONPYCACHEPREFIX=.scratch/pycache uv run --with numba --with numpy --with pytest python3 -m pytest -q tests/stable_ac/test_ak_depth_four_period_two_depth6_l0_census.py
```

Expected: collection fails because the census module does not exist.

- [ ] **Step 4: Implement streaming projected wedge evaluation**

```python
def projected_wedge(
    kernel_word: tuple[tuple[lift.Word, int], ...],
    action: tuple[tuple[int, ...], tuple[int, ...]],
    prime: int = 2,
) -> tuple[int, ...]: ...
```

Track the projected linear prefix and upper-triangular quadratic coordinates while streaming the kernel word.  Assert projected abelianization is zero and the two orientations of every wedge pair agree with the expected sign modulo `prime`.

Assemble fourteen bits in this exact order: Result 152 bits after `Phi_infinity`, Result 153 identity/twisted bits, Result 154 bit, Result 155 bit, Result 156 two five-cycle bits, and Result 157 two double-transposition bits.

- [ ] **Step 5: Implement the complete deterministic census**

For every balanced pair in sorted source order:

```python
record = (
    lift.literal(left),
    lift.literal(right),
    right_coefficient,
    *projected_bits,
    full_bit_or_two,
)
digest.update((repr(record) + "\n").encode())
```

Use sentinel `2` for `full_bit_or_two` unless all fourteen projected bits vanish.  Only then construct the full wedge and calculate `sum(wedge.values()) % 2`.  Assert the two near-survivors have full bit one and no pair has all fifteen bits zero.

- [ ] **Step 6: Run the three focused test files**

Run Task 1--3 tests.  Expected: all pass and the census hash equals the pinned digest.

- [ ] **Step 7: Commit and push Task 3**

```bash
git add experiments/stable_ac/depth4_period_two_depth6_l0_census_certificate.py tests/stable_ac/test_ak_depth_four_period_two_depth6_l0_census.py
git commit -m "Certify depth-six balanced source census"
git push origin codex/proofs
```

---

### Task 4: Proof integration, independent audit, and next-state extraction

**Files:**
- Modify: `literature/proofs/AK3_DEPTH4_PERIOD_TWO_DEPTH6_BALANCED_L0_CENSUS.md`
- Modify: `results/stable_ac/theory/AK3_DEPTH4_HANDOFF.md`
- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`
- Modify: `AGENTS.md` only if implementation reveals a non-obvious trap or confirmed reusable method.

**Interfaces:**
- Consumes: all three certificate modules and their exact outputs.
- Produces: a reproducible bounded proof note and an explicit transition-state research frontier.

- [ ] **Step 1: Update the bounded proof note**

Add the tracked checker path, exact census hash, projected bit order, sentinel rule, and focused test command.  Retain the sentences that the result is bounded and makes no depth-seven or all-depth claim.

- [ ] **Step 2: Update theory and handoff**

Record that the complete-cover rewrite, source classifier, and depth-six census are tracked.  Set the next theorem target to transition closure of:

```text
(source action class, L0 boundary pairing type, projected fourteen-bit state, Phi_infinity gate)
```

under left extension by `c`, `t`, and `T`.

- [ ] **Step 3: Run full verification**

Run:

```bash
PYTHONPYCACHEPREFIX=.scratch/pycache uv run --with numba --with numpy --with pytest python3 -m pytest -q tests/stable_ac/test_ak_depth_four_period_two_*.py
git diff --check
```

Expected: the complete period-two chain passes, including the three new focused files.

- [ ] **Step 4: Obtain an independent audit**

The reviewer must independently replay the four fixed paths, depth-six (K) round trips, six action signatures, five known directions, 4,671-pair census, two near-survivors, zero final survivors, and digest `02a688c2e0bfd1831202c6b76f8d3af9b4340c71e08d9b1e2efeea59d8301ff3`.

- [ ] **Step 5: Stage, commit, and push the integration checkpoint**

```bash
git add experiments/stable_ac tests/stable_ac results/stable_ac/theory docs/superpowers AGENTS.md
git add -f literature/proofs/AK3_DEPTH4_PERIOD_TWO_DEPTH6_BALANCED_L0_CENSUS.md
git diff --cached --check
git commit -m "Promote exact period-two source census"
git push origin codex/proofs
```
