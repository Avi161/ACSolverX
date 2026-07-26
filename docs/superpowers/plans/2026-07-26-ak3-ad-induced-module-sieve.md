# AK(3) A--D Induced-Module Sieve Plan

**Goal:** Refine the arbitrary A--D Fox obstruction from exponent
classes to exact \(F(q,z)\)-projection fibers.

**Architecture:** Evaluate the Fox row noncommutatively, construct an
induced right module from \(\langle qz^{-1},\pi(c)\rangle\), and use the
old modular witnesses only on the residual cyclic subgroup.

**Tech Stack:** Markdown proof and dependency-free free-word replay.

## Constraints

- Theory before implementation.
- No AC graph search and no bounded-conjugator inference.
- Prove the right-module handedness explicitly.
- Do not call the three surviving projection fibers primitive.
- AK(3), AC, and stable AC remain open.

### Task 1: Noncommutative Fox obstruction

- [x] Derive the exact evaluated row over \(\mathbb Z[F(q,z)]\).
- [x] Construct the induced right module and annihilating vector.
- [x] Prove the rank-two subgroup character exists.

### Task 2: Cyclic residual subgroup

- [x] Prove \(g\in\langle qz^{-1}\rangle\) is necessary.
- [x] Reuse the all-integer modular argument.
- [x] Isolate the three exact projection fibers.

### Task 3: Replay and checkpoint

- [x] Write and run the failing verifier additions first.
- [x] Implement projection and cyclic-membership replay.
- [x] Record Result 56 and update the live lead.
- [x] Run regression and obtain a hostile audit.
- [ ] Commit and push.
