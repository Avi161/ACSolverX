# AK(3) A--D \(BS(3,4)\) Module Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Decide whether the universal A--D pair quotient supplies a
right-module obstruction for all three Result 56 projection fibers.

**Architecture:** Rewrite the pair quotient as
\(BS(3,4)*\langle z\rangle\), verify the exact evaluated Fox row, and
reduce right-unimodularity to a three-relation cyclic module. Use exact
finite quotient modules for discovery, then prove either a uniform
module construction or an exact obstruction to that construction.

**Tech Stack:** Markdown proof, dependency-free Python, finite
permutations, modular Gaussian elimination.

## Global Constraints

- Theory before implementation.
- No AC graph search.
- No conclusion from bounded conjugator length or finitely many
  quotients.
- Mark the three Result 56 fibers open unless a uniform module proof
  covers them.
- AK(3), AC, and stable AC remain open unless an independently replayed
  stable proof is obtained.

---

### Task 1: Universal quotient and Fox row

**Files:**
- Create: `experiments/stable_ac/verify_ad_bs34_module.py`
- Create: `tests/stable_ac/test_ad_bs34_module.py`
- Read: `literature/proofs/AK3_AD_INDUCED_MODULE_SIEVE.md`

**Interfaces:**
- Produces: `GroupRingElement = dict[str, int]`
- Produces: `evaluated_ad_rows() -> tuple[tuple[GroupRingElement, ...], tuple[GroupRingElement, ...]]`
- Produces: `four_state_residuals(sigma: int, g: str) -> tuple[GroupRingElement, ...]`

- [ ] **Step 1: Write the failing quotient test**

Assert the substitutions

```python
forward = {"x": "x", "t": "zxZ", "z": "z", "q": "zy"}
```

send D to the identity and A to a conjugate of
`yxxxYXXXX`, and assert the inverse generator formulas
`t=zxZ`, `q=zy`, `y=Zq`.

- [ ] **Step 2: Run the quotient test and verify failure**

Run:

```bash
UV_CACHE_DIR=.scratch/uv-cache uv run --with pytest \
  python3 -m pytest -q tests/stable_ac/test_ad_bs34_module.py
```

Expected: import failure for `verify_ad_bs34_module`.

- [ ] **Step 3: Implement free-word substitution and group-ring Fox evaluation**

Differentiate the literal A and D words, then impose only the quotient
equalities

```text
qx^3q^-1 = t^4
zxz^-1 = t
```

needed to obtain

```text
A_x = q(1+x+x^2)       D_x = t^-1 z
A_t = -(1+t+t^2+t^3)   D_t = -t^-1
A_z = 0                 D_z = t^-1-1
A_q = 1-t^4             D_q = 0
```

- [ ] **Step 4: Verify the four-state reduction**

Represent the formal vector actions

```text
v t^4 = v
v g = -sigma * v(1+t+t^2+t^3)
v q(1+x+x^2) = v(1+t+t^2+t^3) z
```

and assert that substitution annihilates all four coordinates of
`A_row + sigma*g*D_row`.

- [ ] **Step 5: Run the focused test**

Expected: every quotient, Fox-row, and four-state assertion passes.

---

### Task 2: Exact finite quotient discovery

**Files:**
- Modify: `experiments/stable_ac/verify_ad_bs34_module.py`
- Modify: `tests/stable_ac/test_ad_bs34_module.py`
- Create: `results/stable_ac/analysis/ad_bs34_finite_module_scan.txt`

**Interfaces:**
- Produces: `Permutation = tuple[int, ...]`
- Produces: `bs34_s5_models() -> tuple[dict[str, Permutation], ...]`
- Produces: `common_right_annihilator_dimension(row, model, prime) -> int`

- [ ] **Step 1: Write failing finite-model tests**

Use \(x=(0\,1\,2\,3\,4)\). Enumerate permutations y satisfying
\(yx^3y^{-1}=x^4\), and arbitrary z in \(S_5\). Define
`t=z*x*z^-1`, `q=z*y`; assert A and D evaluate to the identity.

- [ ] **Step 2: Implement permutation and modular linear algebra**

Implement composition, inverse, word evaluation, regular right action,
row-matrix assembly, and row reduction over primes 5, 7, and 11.

- [ ] **Step 3: Scan structurally distinct residual samples**

For each sign, include:

```text
pi(c)=1:       1, x, t, [x,q], qxq^-1
pi(c)=qz^-1:  qz^-1, xqz^-1, qxq^-1 qz^-1, [x,t]qz^-1
```

Record model counts and annihilator dimensions. The file must label
these as discovery evidence, never as an arbitrary-c theorem.

- [ ] **Step 4: Extract a candidate uniform representation**

Group successful certificates by the orbit of
`(v, vt, vt^2, vt^3, vg)`. Retain only a pattern expressible from g and
the group operations; discard certificates depending on the sampled
spelling length.

- [ ] **Step 5: Run focused tests and save the scan**

Expected: every reported certificate is replayed by direct matrix
multiplication.

---

### Task 3: Prove or refute the cyclic-module construction

**Files:**
- Create: `literature/proofs/AK3_AD_BS34_MODULE_OBSTRUCTION.md`
- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`
- Modify: `docs/superpowers/plans/2026-07-27-ak3-ad-bs34-module.md`

**Interfaces:**
- Consumes the exact right ideal

```text
I_sigma,g = <
  t^4-1,
  g+sigma(1+t+t^2+t^3),
  q(1+x+x^2)-(1+t+t^2+t^3)z
>_right
```

- Produces either a proof that \(I_{\sigma,g}\ne R\) uniformly on a
  Result 56 fiber, or a literal Bézout/collapse certificate showing
  that this proposed module cannot obstruct that fiber.

- [ ] **Step 1: Translate the finite pattern into normal-form identities**

Write every proposed action in the free-product normal form
\(BS(3,4)*\langle z\rangle\). Check the HNN pinches only through
\(yx^3y^{-1}=x^4\).

- [ ] **Step 2: Prove nonzero or exhibit collapse**

For a positive result, identify a basis vector or coset whose
coefficient is invariant under all three right-ideal generators; this
proves \(1\notin I_{\sigma,g}\). For a negative result, display
right coefficients \(b_1,b_2,b_3\) satisfying

```text
(t^4-1)b1
+ (g+sigma(1+t+t^2+t^3))b2
+ (q(1+x+x^2)-(1+t+t^2+t^3)z)b3
= 1.
```

- [ ] **Step 3: State only the proved scope**

If all three fibers are covered, conclude that arbitrary A--D relative
products never create a primitive row. Otherwise state the exact
covered fibers and the exact residual condition; do not extrapolate
from Task 2.

- [ ] **Step 4: Add independent replay assertions**

Replay every displayed group-ring or matrix certificate literally in
`test_ad_bs34_module.py`.

- [ ] **Step 5: Run verification and hostile audit**

Run the focused tests, the Result 56 regression, syntax compilation,
and `git diff --check`. Obtain a read-only hostile audit of Fox
handedness, module nonzeroness, and scope.

---

### Task 4: Checkpoint and continue

**Files:**
- Modify: `AGENTS.md` only if the attempt exposes a non-obvious trap.

- [ ] **Step 1: Stage normal files and force-add the ignored proof**

- [ ] **Step 2: Inspect staged scope and commit**

- [ ] **Step 3: Push `codex/proofs`**

- [ ] **Step 4: Continue the proof loop**

If A--D closes, move to arbitrary W--D products. If it does not, attack
the exact residual group-ring condition from Task 3 with a different
module or quotient.
