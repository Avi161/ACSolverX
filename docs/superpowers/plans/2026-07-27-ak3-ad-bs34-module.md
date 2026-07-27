# AK(3) A--D \(BS(3,4)\) Module Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Decide whether the universal A--D pair quotient supplies a
right-module obstruction for all three Result 56 projection fibers.

**Architecture:** Rewrite the pair quotient as
\(BS(3,4)*\langle z\rangle\), verify the exact evaluated Fox row, and
reduce right-unimodularity to a three-relation cyclic module. Use exact
finite-order algebra to prove why finite quotients erase the HNN index
gap, then test an infinite Bass--Serre module for the three residual
fibers.

**Tech Stack:** Markdown proof, dependency-free Python, free-product
and HNN normal forms, exact integer arithmetic.

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

- [x] **Step 1: Write the failing quotient test**

Assert the substitutions

```python
forward = {"x": "x", "t": "zxZ", "z": "z", "q": "zy"}
```

send D to the identity and A to a conjugate of
`yxxxYXXXX`, and assert the inverse generator formulas
`t=zxZ`, `q=zy`, `y=Zq`.

- [x] **Step 2: Run the quotient test and verify failure**

Run:

```bash
UV_CACHE_DIR=.scratch/uv-cache uv run --with pytest \
  python3 -m pytest -q tests/stable_ac/test_ad_bs34_module.py
```

Expected: import failure for `verify_ad_bs34_module`.

- [x] **Step 3: Implement free-word substitution and group-ring Fox evaluation**

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

- [x] **Step 4: Verify the four-state reduction**

Represent the formal vector actions

```text
v t^4 = v
v g = -sigma * v(1+t+t^2+t^3)
v q(1+x+x^2) = v(1+t+t^2+t^3) z
```

and assert that substitution annihilates all four coordinates of
`A_row + sigma*g*D_row`.

- [x] **Step 5: Run the focused test**

Expected: every quotient, Fox-row, and four-state assertion passes.

---

### Task 2: Finite-quotient collapse theorem

**Files:**
- Modify: `experiments/stable_ac/verify_ad_bs34_module.py`
- Modify: `tests/stable_ac/test_ad_bs34_module.py`
- Create: `literature/proofs/AK3_AD_FINITE_QUOTIENT_MODULE_BARRIER.md`
- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`

**Interfaces:**
- Produces: `finite_bs34_order_compatible(n: int) -> bool`
- Produces: `finite_cyclic_collapse_certificate(n: int) -> tuple[int, int]`
- Establishes: every finite image of x has order coprime to 12
- Establishes: a finite-module four-state vector satisfies
  `v*t = v` and `3*v*(q*z^-1) = 4*v`

- [ ] **Step 1: Write the failing order-spectrum tests**

For every \(1\le n\le300\), assert

```python
finite_bs34_order_compatible(n) == (gcd(n, 12) == 1)
```

For each compatible n, require
`finite_cyclic_collapse_certificate(n)` to return `(a, b)` satisfying

```text
4*a = 1 (mod n)
3*b = 1 (mod n).
```

- [ ] **Step 2: Prove the finite-order lemma**

If x has order n, compute
\(\operatorname{ord}(x^k)=n/\gcd(n,k)\). Since \(x^3\) and \(x^4\)
are conjugate, their orders agree. Prove that
\(\gcd(n,3)=\gcd(n,4)\) is possible only when both equal one.

- [ ] **Step 3: Derive the module collapse**

Let n be the order of t. Use \(4a\equiv1\pmod n\) to derive
\(vt=v\) from \(vt^4=v\). Put \(w=vz\). Derive, in order,

```text
w*x = w
w*y*x^3 = w*y
w*y*x = w*y
3*w*y = 4*w
3*v*(q*z^-1) = 4*v.
```

State exactly that finite quotients erase the HNN index gap but may
still detect the kernel component of a particular g.

- [ ] **Step 4: Close only the literal representatives**

Using `v*g = -4*sigma*v`, prove \(v=0\) for exactly

```text
(sigma, g) = (+1, q*z^-1)
(sigma, g) = (-1, 1)
(sigma, g) = (-1, q*z^-1).
```

Do not replace the Result 56 conditions
`pi(g) in {1, q*z^-1}` by these literal equalities.

- [ ] **Step 5: Run the focused replay and update the theory index**

Run the focused pytest file and syntax compilation. Label the result a
finite-quotient module barrier, not an arbitrary-c obstruction.

---

### Task 3: Infinite HNN module for the residual fibers

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

- [ ] **Step 1: Parameterize the exact fibers**

Let \(h=qz^{-1}=zyz^{-1}\) and let K be the kernel of the map killing
x. Write the three fibers without choosing bounded representatives:

```text
sigma=+1: g=k*h
sigma=-1: g=k or g=k*h
```

for arbitrary \(k\in K\).

- [ ] **Step 2: Construct the infinite normal-form module**

Use an infinite coset or Bass--Serre-tree basis in which
\(\langle x^3\rangle\) and \(\langle x^4\rangle\) have different
indices. Define the right actions of x, y, and z and verify the HNN
relation before imposing any relation involving g.

- [ ] **Step 3: Prove nonzero or exhibit collapse**

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

- [ ] **Step 4: State only the proved scope**

If all three fibers are covered, conclude that arbitrary A--D relative
products never create a primitive row. Otherwise state the exact
covered fibers and the exact residual condition. Do not infer an
arbitrary-g theorem from the finite-quotient collapse in Task 2.

- [ ] **Step 5: Add independent replay assertions**

Replay every displayed group-ring or matrix certificate literally in
`test_ad_bs34_module.py`.

- [ ] **Step 6: Run verification and hostile audit**

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
