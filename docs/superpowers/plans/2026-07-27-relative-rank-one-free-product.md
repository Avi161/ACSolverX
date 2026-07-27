# Relative rank-one free-product implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development to implement this plan
> task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove the exact trimmed-core injectivity criterion for
\(A*\langle s\rangle\to A*C\), then use torsion-freeness to reduce
Result 58's unresolved residue to the internal \(BS(3,4)\) cases.

**Architecture:** Prove a simultaneous syllable-length induction for
powers of a word beginning and ending in one free factor.  Combine it
with a relative Nielsen endpoint trim.  Replay only the literal
normal-form identities in dependency-free Python, then update the
module proof and theory index.

**Tech Stack:** Markdown proof, free-product normal forms,
Bass--Serre torsion arguments, dependency-free Python, pytest.

## Global constraints

- The Markdown induction is the proof; finite replay is not.
- State the criterion using the \(A\)-trimmed core, not the order of
  the original element.
- Preserve the \(C_2*C_2\), \(u=ac\) counterexample to the tempting
  untrimmed-order criterion.
- Do not infer torsion-freeness of \(BS(3,4)\) from experiments.
- Keep every \(u\in B\) case open after this phase.
- AK(3), AC, and stable AC remain open.

---

### Task 1: Prove the relative rank-one theorem

**Files:**
- Create: `literature/proofs/RELATIVE_RANK_ONE_FREE_PRODUCT.md`

- [x] State the exact trimmed-core iff criterion and its necessary
  kernel word.
- [x] Prove endpoint trimming is a relative Nielsen automorphism.
- [x] Prove the power-endpoint lemma by simultaneous induction.
- [x] Prove injectivity by expanding an arbitrary reduced relative word.
- [x] Audit zero powers, negative powers, length-one words, internal
  elements, and the \(C_2*C_2\) untrimmed-order counterexample.

---

### Task 2: Add independent normal-form replay

**Files:**
- Create: `experiments/stable_ac/verify_relative_free_product.py`
- Create: `tests/stable_ac/test_relative_free_product.py`

**Interfaces:**
- `reduce_syllables(word, orders=None)`
- `power_syllables(word, exponent, orders=None)`
- `trim_base_endpoints(word, base_factor="A")`
- `evaluate_relative_word(relative_word, u, orders=None)`

- [x] Write tests for both branches of the power lemma.
- [x] Write tests for endpoint trimming and alternating-word seams.
- [x] Pin the \(C_2*C_2\) infinite-untrimmed/finite-core kernel and an
  internal-element kernel.
- [x] Implement only enough exact syllable algebra to replay the tests.

---

### Task 3: Apply the theorem to Result 58

**Files:**
- Modify: `literature/proofs/AK3_AD_BS34_MODULE_OBSTRUCTION.md`
- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`

- [x] Prove \(BS(3,4)\) torsion-free from its HNN tree.
- [x] Prove \(BS(3,4)*\langle z\rangle\) torsion-free.
- [x] Replace the conditional noninternal residue by the exact condition
  \(u\notin B\), equivalently \(g\notin zBz^{-1}\).
- [x] State the three remaining internal exponent classes without
  claiming they are obstructed.

---

### Task 4: Verify, review, and checkpoint

- [x] Run the focused relative-free tests.
- [x] Run the Result 57--58 and Result 56 regressions.
- [x] Run syntax compilation and `git diff --check`.
- [x] Obtain independent proof and scope reviews; resolve every
  Critical or Important finding.
- [ ] Force-add the new proof file, inspect staged scope, commit, and
  push `codex/proofs`.
- [ ] Continue with the internal \(BS(3,4)\) module problem.
