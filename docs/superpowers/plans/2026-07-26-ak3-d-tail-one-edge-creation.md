# AK(3) D-Tail One-Edge Primitive Creation Plan

**Goal:** Exhaust every one-AC2-edge primitive-single and
primitive-pair creation route involving a nonprimitive first D-tail
row and one of A, W, D.

**Architecture:** Enumerate the exact cyclic edge image, attach complete
rank-four Whitehead certificates, then transport the full tuple for
every positive.

**Tech Stack:** Markdown proof and dependency-free free-group replay.

## Constraints

- Theory before implementation.
- No AC graph search.
- Cover both target directions and every cyclic AC2 realization.
- Retain exact move witnesses after deduplication.
- Use complete Whitehead minima, not a greedy positive heuristic.
- Transport every positive through the full tuple before judging it.
- Distinguish classical backtracks, stable floor-14 merges, and new
  endpoints.
- AK(3) remains open.

### Task 1: Exhaustive edge image

- [x] Prove the target/source orientation model is complete.
- [x] Enumerate all six sign rows, three carriers, and two directions.
- [x] Record literal and distinct-child counts with a deterministic
  trace.

### Task 2: Primitive gates

- [x] Classify every distinct changed row individually.
- [x] Classify every relevant displayed relator pair.
- [x] Record explicit certificates for every positive and complete
  negative minima for all other children.

### Task 3: Endpoint transport

- [x] Identify exact tail-cancellation backtracks.
- [x] Transport every non-backtracking positive through deletion.
- [x] Compare every endpoint with the known stable corridors.

### Task 4: Verification and checkpoint

- [x] Build and run an independent replay.
- [x] Obtain a hostile audit.
- [x] Record Result 49 and update the live lead.
- [x] Commit and push.
