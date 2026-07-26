# AK(3) All-Integer D-Tail Primitivity Plan

**Goal:** Prove the exact primitivity criterion for
\(q^\eta W^\epsilon D^k\) for all signs and all integers k.

**Architecture:** Combine two prior positive coordinates with one
symbolic Whitehead-graph obstruction covering every remaining
nonzero-power row.

**Tech Stack:** Markdown proof and dependency-free rank-four
free-group replay.

## Constraints

- Theory before implementation.
- No AC graph search and no bounded-power inference.
- Prove all signs of k, including k=0.
- Verify the common map as a rank-four Whitehead automorphism.
- Check every displayed spanning-cycle edge symbolically for arbitrary
  nonzero power.
- Do not infer anything about primitive pairs.
- AK(3) remains open.

### Task 1: Positive rows

- [x] Bind all four k=0 rows to Result 44.
- [x] Bind the \((+,-)\) all-k row to Result 47.

### Task 2: Symbolic negative rows

- [x] Derive the three fixed boundary blocks after the common map.
- [x] Prove the five sign/orientation spanning cycles.
- [x] Apply the cut-vertex lemma uniformly for every nonzero k.

### Task 3: Verification and checkpoint

- [x] Build and run an independent symbolic replay.
- [x] Obtain a hostile audit.
- [x] Record Result 48 and update the live lead.
- [ ] Commit and push.
