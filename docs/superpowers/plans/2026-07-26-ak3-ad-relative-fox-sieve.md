# AK(3) A--D Relative-Product Fox Sieve Plan

**Goal:** Prove an unbounded nonprimitivity theorem for arbitrary A--D
relative products, leaving only the exact exponent classes not detected
by the chosen character slice.

**Architecture:** Derive the abelianized Fox row symbolically, solve its
common-zero equations over characteristic zero or a finite field, and
replay the identities independently from literal words.

**Tech Stack:** Markdown proof and dependency-free Python replay.

## Constraints

- Theory before implementation.
- No AC graph search.
- No bounded-conjugator inference.
- State the finite-field characteristic restrictions.
- Treat the three residual exponent classes as open.
- AK(3), AC, and stable AC remain open.

### Task 1: Universal Fox slice

- [x] Prove the primitive-row common-zero obstruction.
- [x] Derive the exact gradients of A and D at \(x=t=1\).
- [x] Show that the conjugator derivative cancels for arbitrary c.

### Task 2: Solve the character equation

- [x] Handle \(e_q+e_z\ne0\) over an algebraic closure.
- [x] Handle the zero-total-exponent line by elementary prime divisors.
- [x] Isolate the three exact failures of this slice.

### Task 3: Replay and proof

- [x] Write the failing verifier tests first.
- [x] Implement the dependency-free Fox verifier.
- [x] Record the theorem and update the live lead.

### Task 4: Checkpoint

- [x] Run focused and regression tests.
- [x] Obtain a hostile proof audit.
- [ ] Commit and push the branch.
