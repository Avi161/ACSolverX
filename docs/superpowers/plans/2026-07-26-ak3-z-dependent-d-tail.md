# AK(3) Z-Dependent D-Tail Plan

**Goal:** Classify primitivity of all eight words
\(q^\eta W^\epsilon D^\delta\) with exact Whitehead certificates.

**Architecture:** Use strict Whitehead descents for the two primitive
rows and explicit terminal spanning-cycle graphs for the six
nonprimitive rows.

**Tech Stack:** Markdown proof and dependency-free rank-four word
replay.

## Constraints

- Theory before implementation.
- No AC graph search.
- Check all eight sign triples.
- Distinguish primitivity from stable productivity.
- Do not claim the primitive deletion endpoints close until computed.
- AK(3) remains open.

### Task 1: Primitive certificates

- [x] Record exact reduced source words.
- [x] Replay the 12-step certificate for \(qW^{-1}D\).
- [x] Replay the 13-step certificate for \(qW^{-1}D^{-1}\).
- [x] Verify every step is an automorphism and strictly reduces length.

### Task 2: Nonprimitive certificates

- [x] Give the common first Whitehead automorphism.
- [x] Give the two exceptional second reduction moves.
- [x] Record all six terminal words and exact graphs.
- [x] Exhibit a spanning 8-cycle in every graph.
- [x] Apply the cut-vertex lemma with exact scope.

### Task 3: Verification and checkpoint

- [x] Build a dependency-free rank-four replay.
- [x] Run focused tests and hostile audit.
- [x] Record Result 46 and narrow the live lead.
- [x] Commit and push.
