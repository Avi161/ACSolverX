# AK(3) Changed-Q-Source Gauge Plan

**Goal:** Prove that a nonliteral source \(Q=qV\), with \(V\) carried by
passive q-free retained sources, gives the ordinary q-deletion endpoint
even after arbitrary \(Q\)-source target traffic.

**Architecture:** Straighten \(Q\), compare its deletion evaluation with
ordinary q-deletion modulo the passive-source normal closure, then give
an exact retained-factor return for \(V=D\).

**Tech Stack:** Markdown proof and dependency-free exact word replay.

## Constraints

- Theory before implementation.
- No AC graph search.
- Keep the passive sources literal through \(Q\)'s manufacture and
  distinct until deletion; afterward permit only \(Q\)-traffic into
  them.
- Keep \(Q\) unchanged after its manufacture and delete it first.
- Do not extend the theorem to q-dependent \(V\).
- AK(3) remains open.

### Task 1: Prove the general gauge theorem

- [x] Define the straightening and deletion map for \(Q=qV\).
- [x] Prove arbitrary \(Q\)-normal-closure traffic vanishes.
- [x] Compare the endpoint with ordinary q-deletion modulo passive sources.
- [x] State the sharp hypotheses.

### Task 2: Prove the exact AK return

- [x] Specialize to \(V=D\).
- [x] Compute \(R_D,p_D,W_D\).
- [x] Factor \(R^{-1}R_D\) and \(U^{-1}W_D\) into D-source factors.
- [x] Return \(U\) to \(B\) by one R-source factor.

### Task 3: Replay and verify

- [x] Verify the transvection and inverse.
- [x] Replay representative \(Q\)-source traffic.
- [x] Verify every exact endpoint and factor identity.
- [x] Run focused tests and a hostile audit.
- [ ] Record the result, commit, and push the branch.
