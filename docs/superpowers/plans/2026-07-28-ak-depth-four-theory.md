# AK Depth-Four Theory Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove that every row reached from the original AK pair by at
most four AC2 multiplications is nonprimitive, or isolate the exact
dependent equations that prevent that theorem.

**Architecture:** Signed source-leaf provenance reduces arbitrary AC1
and AC3 moves to 54 finite depth-four signatures. Majority-killing
virtually free quotients handle rows with one or two minority leaves.
For three minority leaves, exact `SU(2)` conjugacy-angle intervals turn
the problem into scalar inequalities; any survivors receive separate
representations or dependent-history analysis.

**Tech Stack:** Python 3 exact integer/rational arithmetic, pytest,
free-product Bass--Serre normal forms, unit-quaternion `SU(2)` geometry,
Markdown/LaTeX proof ledgers, Git branch `codex/proofs`.

## Global Constraints

- Work only in `.claude/worktrees/codex-proofs`.
- Never claim a bounded numerical search as proof.
- Mark incomplete diagnostics `[unverified]`.
- Preserve arbitrary conjugators in every certificate.
- Run `git diff --check` before every commit.
- Commit and push `codex/proofs` at verified checkpoints and at least
  every 20 minutes while changes are pending.
- AK(3), stable Andrews--Curtis, and Andrews--Curtis remain open unless
  an end-to-end proof or counterexample is independently verified.

---

### Task 1: Finish the 24 low-minority free-product certificates

**Files:**
- Modify: `.scratch/depth4_provenance_check.py`
- Create: `tests/stable_ac/test_ak_depth_four_barriers.py`
- Modify: `results/stable_ac/theory/AK3_DEPTH4_HANDOFF.md`

**Interfaces:**
- Consumes: canonical leaf signatures from `row_multisets(4)` and the
  quotients `Q_A=C_3*C_4`, `Q_B=C_2*C_3`.
- Produces: `low_minority_certificate_records()` returning one exact
  record for each of the 24 signatures, with no surviving target.

- [ ] **Step 1: Write the failing completion test**

```python
def test_all_depth_four_low_minority_classes_are_closed() -> None:
    records = low_minority_certificate_records()
    assert len(records) == 24
    assert not any(record.found_target for record in records)
```

- [ ] **Step 2: Verify the current checker misses the completion gate**

Run:

```text
PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=.scratch/uv-cache \
uv run --with pytest python3 -m pytest -q \
tests/stable_ac/test_ak_depth_four_barriers.py
```

Expected: failure because the reusable certificate function does not
yet exist or does not terminate under the test bound.

- [ ] **Step 3: Stream and prune connectors**

Generate reduced connectors depth-first.  Track current syllable length
and stop a branch once even maximal boundary cancellation cannot reach
the target cyclic length.  Compare cyclic rotations immediately rather
than materializing a global connector list.

- [ ] **Step 4: Run the focused certificate test**

Run the command from Step 2.  Expected: 24 records and zero survivors.

- [ ] **Step 5: Record exact counts and hashes**

Update `AK3_DEPTH4_HANDOFF.md` with the completed certificate hash,
per-signature connector bounds, and the focused test output.  Remove
the `[unverified]` label only from this low-minority result.

- [ ] **Step 6: Commit and push**

```text
git add .scratch/depth4_provenance_check.py \
tests/stable_ac/test_ak_depth_four_barriers.py \
results/stable_ac/theory/AK3_DEPTH4_HANDOFF.md
git commit -m "Close low-minority AK depth-four classes"
git push origin codex/proofs
```

### Task 2: Prove the three-conjugate SU(2) interval

**Files:**
- Create: `literature/proofs/AK3_SU2_THREE_CLASS_INTERVAL.md`
- Modify: `tests/stable_ac/test_ak_depth_four_barriers.py`

**Interfaces:**
- Consumes: an `SU(2)` conjugacy angle `alpha` in `[0, pi]`.
- Produces: the exact attainable interval for a product of three copies
  of the conjugacy class and its scalar separation criterion.

- [ ] **Step 1: Write endpoint tests for the piecewise interval**

```python
def test_three_class_interval_endpoints() -> None:
    assert triple_class_interval(Fraction(1, 4)) == (0, Fraction(3, 4))
    assert triple_class_interval(Fraction(2, 5)) == (0, 1)
    assert triple_class_interval(Fraction(3, 4)) == (Fraction(1, 4), 1)
```

The test uses angles normalized by `pi`, so `1` denotes `pi`.

- [ ] **Step 2: Prove the two-class interval and compose it twice**

For angles `alpha,beta`, use

```text
[abs(alpha-beta), pi-abs(pi-alpha-beta)]
```

and take the union over the first product angle.  Prove the union is
connected and has endpoints

```text
[0,3 alpha], [0,pi], [3 alpha-2 pi,pi]
```

in the three stated regimes.

- [ ] **Step 3: Derive the scalar-only certificate**

Use `cos(3 alpha)=4 cos(alpha)^3-3 cos(alpha)` to prove:

```text
s > 1/2 and t < 4s^3-3s
```

or

```text
s < -1/2 and t > 4s^3-3s
```

separates the target from the triple product.

- [ ] **Step 4: Run the focused tests and proof-text checks**

```text
UV_CACHE_DIR=.scratch/uv-cache uv run --with pytest python3 -m pytest -q \
tests/stable_ac/test_ak_depth_four_barriers.py
git diff --check
```

- [ ] **Step 5: Commit and push**

```text
git add tests/stable_ac/test_ak_depth_four_barriers.py
git add -f literature/proofs/AK3_SU2_THREE_CLASS_INTERVAL.md
git commit -m "Prove the SU2 three-class interval"
git push origin codex/proofs
```

### Task 3: Certify the 24 screened three-minority signatures exactly

**Files:**
- Create: `experiments/stable_ac/depth4_su2_certificates.py`
- Modify: `tests/stable_ac/test_ak_depth_four_barriers.py`
- Modify: `literature/proofs/AK3_SU2_THREE_CLASS_INTERVAL.md`

**Interfaces:**
- Consumes: a rational quaternion parameter and a signed provenance
  signature.
- Produces: exact source scalar `s`, target scalar `t`, and a positive
  rational margin for one of the two scalar criteria.

- [ ] **Step 1: Write the failing certificate-table test**

```python
def test_exact_su2_table_closes_twenty_four_three_minority_cases() -> None:
    certificates = exact_three_minority_certificates()
    assert len(certificates) == 24
    assert all(certificate.margin_lower_bound > 0 for certificate in certificates)
```

- [ ] **Step 2: Implement exact directed rational intervals**

Represent every radical by rational lower and upper bounds obtained
with integer square roots at a fixed decimal scale.  Implement outward
rounded addition, subtraction, multiplication, and quaternion word
evaluation.  Refine the scale until each required sign is strict.

- [ ] **Step 3: Verify the majority-killing relations exactly**

For `B=1`, use equal quaternion angles and

```text
d=(cos(theta)^2-1/2)/sin(theta)^2
```

at `cos(theta)^2=37/50` and `2/5`.

For `A=1`, use angles `pi/3`, `pi/4` and axis products

```text
-1/3, -1/4, 8/15, 4/5.
```

Verify `B=1` or `A=1` before accepting any scalar margin.

- [ ] **Step 4: Emit a stable exact certificate table**

Each record contains the signature, exponent vector, representation
identifier, interval for `s`, interval for `t`, and rational lower
bound on the separation margin.  Sort records before hashing.

- [ ] **Step 5: Run focused tests and an independent replay**

```text
UV_CACHE_DIR=.scratch/uv-cache uv run --with pytest python3 -m pytest -q \
tests/stable_ac/test_ak_depth_four_barriers.py
PYTHONDONTWRITEBYTECODE=1 python3 \
experiments/stable_ac/depth4_su2_certificates.py
```

- [ ] **Step 6: Promote only the exact 24-case theorem and commit**

```text
git add experiments/stable_ac/depth4_su2_certificates.py \
tests/stable_ac/test_ak_depth_four_barriers.py
git add -f literature/proofs/AK3_SU2_THREE_CLASS_INTERVAL.md
git commit -m "Certify 24 AK depth-four SU2 barriers"
git push origin codex/proofs
```

### Task 4: Resolve the six three-minority survivors

**Files:**
- Modify: `results/stable_ac/theory/AK3_DEPTH4_HANDOFF.md`
- Modify: `tests/stable_ac/test_ak_depth_four_barriers.py`
- Create when proved: `literature/proofs/AK3_DEPTH4_FINAL_SIX.md`

**Interfaces:**
- Consumes: the six signatures and their exact dependent leaf histories.
- Produces: either one arbitrary-conjugator obstruction per signature or
  an exact dependent-history equation for every unresolved signature.

- [ ] **Step 1: Reconstruct every legal history shape**

Enumerate histories, not only signed multisets, and retain shared row
subexpressions.  Canonicalize only by valid row inversion, exchange,
and global conjugation gauges.

- [ ] **Step 2: Test three proof routes independently**

1. other central-power `SU(2)` representations satisfying `A=1` or
   `B=1`;
2. exact triple conjugacy-class products in `C_3*C_4` and `C_2*C_3`;
3. dependent-history reductions analogous to Results 132--136.

- [ ] **Step 3: Require an arbitrary-conjugator certificate**

A bounded word search may nominate a representation but cannot close a
case.  Closure requires a class-product interval, Bass--Serre normal
form, finite quotient class-product separation, or an equivalent exact
invariant.

- [ ] **Step 4: Add one focused regression test per proved signature**

The test must replay the exact representation or normal-form
certificate and assert the target class is absent.

- [ ] **Step 5: Commit each verified survivor batch**

```text
git add results/stable_ac/theory/AK3_DEPTH4_HANDOFF.md \
tests/stable_ac/test_ak_depth_four_barriers.py
git add -f literature/proofs/AK3_DEPTH4_FINAL_SIX.md
git commit -m "Resolve remaining AK depth-four barriers"
git push origin codex/proofs
```

### Task 5: Promote the complete original-source depth-four theorem

**Files:**
- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`
- Modify: `literature/proofs/AK3_PARAFREE_STABLE_SELF_EMBEDDING.md`
- Modify: `literature/proofs/AK3_CONJUGATED_CONSEQUENCE_STORAGE_SELF_LOOP.md`
- Modify: `results/stable_ac/theory/AK3_DEPTH4_HANDOFF.md`

**Interfaces:**
- Consumes: exact closure certificates for all 54 new signatures.
- Produces: the theorem that no row at original-source AC2 depth at most
  four is primitive.

- [ ] **Step 1: Audit all 54 signatures against a certificate record**

Require a bijection between the canonical signature list and the union
of the low-minority, exact `SU(2)`, and final-survivor certificate
tables.

- [ ] **Step 2: Write the theorem in all three ledgers**

State the precise move depth, arbitrary-conjugator scope, quotient or
representation families, and certificate-table hashes.  Do not extend
the theorem to the first proper image without a separate enumeration.

- [ ] **Step 3: Run focused and full verification**

```text
UV_CACHE_DIR=.scratch/uv-cache uv run --with pytest --with numpy --with jax \
python3 -m pytest -q tests/stable_ac
git diff --check
```

Expected: the full stable-AC suite passes with no import or assertion
failures.

- [ ] **Step 4: Commit and push the theorem checkpoint**

```text
git add results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md \
results/stable_ac/theory/AK3_DEPTH4_HANDOFF.md \
tests/stable_ac/test_ak_depth_four_barriers.py
git add -f literature/proofs/AK3_PARAFREE_STABLE_SELF_EMBEDDING.md \
literature/proofs/AK3_CONJUGATED_CONSEQUENCE_STORAGE_SELF_LOOP.md
git commit -m "Close original AK depth four"
git push origin codex/proofs
```
