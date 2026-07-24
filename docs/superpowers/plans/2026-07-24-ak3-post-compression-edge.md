# AK(3) Post-Compression Edge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:executing-plans` task-by-task.

**Goal:** Prove and exactly decide whether one full Definition-2.1
multiplication from the 20 canonical one-edge compression endpoints reaches
Aut-floor at most 12.

**Architecture:** A short theorem composes the certified stable corridor with
one classical AC edge and the length-12 theorem. A new pure-Python enumerator
loads the bound roots, exhausts every signed pair of rotations, and carries a
first literal witness for every canonical child. A separate verifier validates
the upstream certificate, independently replays every edge and Whitehead
witness, and reruns the full payload.

**Tech stack:** Python 3, pytest, existing read-only word/Aut libraries,
Markdown, JSON, SHA-256.

## Constraints

- New task files only.
- Enumerate full cyclic moves; no seam restriction.
- No graph traversal or second-neighborhood expansion.
- Do not use a length cap to omit literal products.
- A null refutes only this finite post-compression lemma.
- CPU only; `.venv/bin/python3`.
- Commit and push at theorem, implementation, and certificate checkpoints.
- No PR or merge; do not touch unrelated untracked files.

### Task 1: Prove the stable implication

- [ ] Create `literature/proofs/AK3_POST_COMPRESSION_EDGE.md`.
- [ ] Prove every stored canonical root is stably AC-equivalent to AK(3).
- [ ] Prove every signed product of rotations is AC1--AC3.
- [ ] Prove floor at most 12 plus the classical length theorem gives stable
  triviality.
- [ ] State the exact finite candidate and negative scope.
- [ ] Consistency-scan, commit, and push.

### Task 2: Implement the complete one-edge image test-first

- [ ] Create `tests/stable_ac/test_post_compression_edge.py` with a failing
  exact move/replay fixture.
- [ ] Create
  `experiments/stable_ac/rank3_compression/post_compression_edge.py`.
- [ ] Load the 20 canonical roots from the verified upstream schema.
- [ ] Enumerate target, sign, and every pair of rotation offsets.
- [ ] Store literal-move count, distinct root-child count, distinct global
  child count, trace, first edge witnesses, Aut records, floor distribution,
  and minimum.
- [ ] Pin the disposable counts only after the implementation reproduces them.
- [ ] Run focused tests, commit, and push.

### Task 3: Build and replay the production certificate

- [ ] Create
  `experiments/stable_ac/rank3_compression/post_compression_edge_certificate.py`.
- [ ] Add a small explicit-root certificate replay test.
- [ ] Validate `ak3_one_edge.json` before accepting its roots.
- [ ] Independently replay every stored edge and every Aut witness.
- [ ] Rerun the entire finite image and require payload equality.
- [ ] Generate `results/stable_ac/theory/ak3_post_compression_edge.json`.
- [ ] Replay it, run regressions, commit, and push.

### Task 4: Adjudicate and continue the proof loop

- [ ] Create `results/stable_ac/theory/AK3_POST_COMPRESSION_EDGE.md`.
- [ ] If minimum is at most 12, expand and replay the complete stable proof.
- [ ] Otherwise state the exact local-ridge theorem and its finite scope.
- [ ] Formulate a symbolic ridge-crossing attempt that respects the
  1,000-node local search cap.
- [ ] Commit and push; keep the research goal active unless AK(3) is actually
  resolved.
