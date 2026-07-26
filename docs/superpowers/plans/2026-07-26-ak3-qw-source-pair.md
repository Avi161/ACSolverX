# AK(3) QW Source-Pair Cancellation Plan

**Goal:** Prove every changed source \(q^\eta W^\epsilon\) is a
two-deletion self-loop, including arbitrary later traffic from that
source.

**Architecture:** Use the unique z-letter to straighten and delete the
changed source, show the surviving W-slot becomes literal
\(q^{-\eta\epsilon}\), delete q, then return the common rank-two
endpoint by two R-source factors.

**Tech Stack:** Markdown proof and dependency-free exact word replay.

## Constraints

- Theory before implementation.
- No AC graph search.
- Check all four sign pairs.
- Keep the changed source fixed and delete it before W.
- Permit later traffic only from the changed source.
- AK(3) remains open.

### Task 1: Primitive coordinates

- [x] Write both sign-dependent unique-z factorizations.
- [x] Give each z-coordinate automorphism and explicit inverse.
- [x] Verify both composition orders.

### Task 2: Two-deletion theorem

- [x] Compute the surviving W image for all four signs.
- [x] Prove later changed-source traffic vanishes.
- [x] Delete the literal q-slot.
- [x] Compute the common rank-two endpoint and exact return.

### Task 3: Verification and checkpoint

- [x] Replay all four source words and automorphisms.
- [x] Replay representative traffic in all survivor slots.
- [x] Verify the common endpoint and two-factor orientation.
- [x] Complete hostile audit and focused tests.
- [ ] Record Result 44, commit, and push.
