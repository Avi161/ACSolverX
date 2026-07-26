# AK(3) z-free A--W conjugator plan

**Goal:** Prove that every normalized z-free relative-conjugator
A--W edge, followed by changed-row-first deletion, is a stable
self-loop.

**Architecture:** Normalize both ordered target directions to a
one-z primitive row, delete it symbolically, use the retained A
normal closure to remove the arbitrary conjugator shadow, and delete
the resulting q-coordinate.

**Tech Stack:** Markdown proof plus dependency-free exact free-word
replay.

## Constraints

- Theory before implementation.
- No AC graph search.
- No bound on \(u\in F(x,t,q)\).
- Separate classical rank-three gauges from stable deletions.
- State the normalized-conjugator scope literally.
- AK(3), AC, and stable AC remain open.

### Task 1: Exact normal forms

- [x] Derive both ordered target directions and both source signs.
- [x] Prove unique-z primitivity and the exact deletion substitution.
- [x] Transport every surviving checkpoint row.

### Task 2: Unbounded collapse

- [x] Apply the fixed-source normal-closure lemma to D and Q.
- [x] Reduce the last row to q and delete it.
- [x] Identify the final pair with AK(3)'s floor-13 orbit.

### Task 3: Certificate and boundary

- [x] Replay representative arbitrary-length conjugators.
- [x] Exhibit the pairwise distinct \(u=q^n\) family.
- [x] Prove both target directions, rather than assuming symmetry.
- [x] Record exact exclusions for z-dependent traffic.

### Task 4: Proof and checkpoint

- [x] Obtain hostile audit.
- [x] Record Result 52 and update the live lead.
- [x] Run focused replay and `git diff --check`.
- [x] Commit and push.
