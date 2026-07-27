# Relative rank-one free-product implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development to implement this plan
> task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove the exact injectivity criterion for
\(A*\langle s\rangle\to A*C\), then use it to reduce Result 58's
unresolved residue to the internal \(BS(3,4)\) cases.

**Architecture:** Prove a simultaneous syllable-length induction for
powers of a word beginning and ending in one free factor.  Combine it
with a relative Nielsen endpoint trim.  Replay only the literal
normal-form identities in dependency-free Python, then update the
module proof and theory index.

**Tech Stack:** Markdown proof, free-product normal forms,
Bass--Serre torsion arguments, dependency-free Python, pytest.

## Global constraints

- The Markdown induction is the proof; finite replay is not.
- Preserve the finite-order exception in the general theorem.
- Do not infer torsion-freeness of \(BS(3,4)\) from experiments.
- Keep every \(u\in B\) case open after this phase.
- AK(3), AC, and stable AC remain open.

---

### Task 1: Prove the relative rank-one theorem

**Files:**
- Create: `literature/proofs/RELATIVE_RANK_ONE_FREE_PRODUCT.md`

- [ ] State the exact iff criterion and both necessary counterexamples.
- [ ] Prove endpoint trimming is a relative Nielsen automorphism.
- [ ] Prove the power-endpoint lemma by simultaneous induction.
- [ ] Prove injectivity by expanding an arbitrary reduced relative word.
- [ ] Audit zero powers, negative powers, length-one words, and torsion.

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

- [ ] Write tests for both branches of the power lemma.
- [ ] Write tests for endpoint trimming and alternating-word seams.
- [ ] Pin an outside finite-order kernel and an internal-element kernel.
- [ ] Implement only enough exact syllable algebra to replay the tests.

---

### Task 3: Apply the theorem to Result 58

**Files:**
- Modify: `literature/proofs/AK3_AD_BS34_MODULE_OBSTRUCTION.md`
- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`

- [ ] Prove \(BS(3,4)\) torsion-free from its HNN tree.
- [ ] Prove \(BS(3,4)*\langle z\rangle\) torsion-free.
- [ ] Replace the conditional noninternal residue by the exact condition
  \(u\notin B\), equivalently \(g\notin zBz^{-1}\).
- [ ] State the three remaining internal exponent classes without
  claiming they are obstructed.

---

### Task 4: Verify, review, and checkpoint

- [ ] Run the focused relative-free tests.
- [ ] Run the Result 57--58 and Result 56 regressions.
- [ ] Run syntax compilation and `git diff --check`.
- [ ] Obtain independent proof and scope reviews; resolve every
  Critical or Important finding.
- [ ] Force-add the new proof file, inspect staged scope, commit, and
  push `codex/proofs`.
- [ ] Continue with the internal \(BS(3,4)\) module problem.
