# AK(3) seam-robust relative-product plan

**Goal:** Classify arbitrary relative conjugators in one Q/carrier
edge at the six nonprimitive D-tail checkpoints.

**Architecture:** Split conjugated factor axes in the Cayley tree.
Use seam-robust Whitehead graphs to reject every disjoint-axis
product, then exhaust the finite intersecting-axis signed-rotation
tables in transformed bases.

**Tech Stack:** Markdown proof plus dependency-free Whitehead-graph
and exact free-word replay.

## Constraints

- Theory before implementation.
- No AC graph search.
- Prove the tree normal form, including cancellation at seams.
- Treat transformed-basis rotations, not original-basis rotations.
- Transport primitive classes back through exact inverse maps.
- Separate changed-row conjugacy from full-tuple endpoint claims.
- AK(3), AC, and stable AC remain open.

### Task 1: Bridge theorem

- [x] Define linear-cut graphs and seam robustness.
- [x] Prove the disjoint-axis bridge normal form.
- [x] Prove intersecting axes reduce to signed rotations.
- [x] Derive the Whitehead nonprimitivity consequence.

### Task 2: Six seam certificates

- [x] Pin the four automorphisms and their inverses.
- [x] Verify all six transformed Q-rows.
- [x] Cover every linear cut by a spanning cycle.

### Task 3: Exceptional finite tables

- [x] Enumerate transformed carrier rotations for every row.
- [x] Minimize every graph-positive product completely.
- [x] Map every primitive child back to the original basis.
- [x] Compare carrier labels and checkpoints with Result 49.

### Task 4: Endpoint inheritance

- [x] Prove the full tuple matches a Result 49 state after changed-row
  conjugation/inversion.
- [x] Inherit direct-pair and changed-row-first endpoint closures.
- [x] State all alternate-order and two-edge exclusions.

### Task 5: Audit and checkpoint

- [x] Obtain hostile audit.
- [x] Record Result 53 and update the live lead.
- [x] Run focused replay and `git diff --check`.
- [x] Commit and push.
