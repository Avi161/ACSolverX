# AK(3) Five-Orbit Ridge-Return Plan

**Goal:** Exactly decide the one-edge image of the five floor-15 Whitehead
representatives in the certified post-compression wall and determine whether
its minimum is uniquely AK(3)'s orbit-2.

**Architecture:** Reuse the already-tested full cyclic edge enumerator on a
root set derived from the verified upstream certificate. A new chained
certificate validates the upstream payload, extracts exactly the minimum
Aut representatives, independently replays the 540 root-child edges, and
checks every Whitehead witness. A theorem note explains why ambient
Whitehead normalization and the subsequent edge preserve stable equivalence.

**Constraints:** New files only; at most 1,000 root-child states; no second
neighborhood; CPU only; no PR or merge; push checkpoints within twenty
minutes.

## Tasks

- [ ] Create `literature/proofs/AK3_RIDGE_RETURN.md` proving the stable
  implication and finite return proposition's scope.
- [ ] Create
  `experiments/stable_ac/rank3_compression/ridge_return_certificate.py`.
- [ ] Add `tests/stable_ac/test_ridge_return.py` with a failing root-extraction
  and small chained-replay test.
- [ ] Bind and verify `ak3_post_compression_edge.json`.
- [ ] Extract the five distinct Whitehead representatives at its minimum.
- [ ] Reuse the full literal edge enumerator without length pruning.
- [ ] Independently replay every edge and Aut witness.
- [ ] Generate and verify
  `results/stable_ac/theory/ak3_ridge_return.json`.
- [ ] Create `results/stable_ac/theory/AK3_RIDGE_RETURN.md`.
- [ ] If a floor-at-most-12 child appears, expand the stable proof. Otherwise
  prove the exact minimum-orbit return statement and formulate a new
  pre-removal mechanism.
- [ ] Run focused regressions, commit, and push. Keep the proof loop active.
