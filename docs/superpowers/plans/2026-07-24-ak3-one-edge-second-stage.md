# AK(3) One-Edge Second-Stage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:executing-plans` to implement this plan task-by-task.

**Goal:** Prove the finite one-edge triangular-compression theorem and exactly
decide whether one Definition-2.1 cyclic multiplication after the first
two-stabilization removal produces an AK(3) endpoint of Aut-floor at most 12.

**Architecture:** A theorem note separates the general stable implication from
the finite cyclic-rotation move class and proves that cancelling-seam
enumeration is complete whenever a new one-\(x\) isolator is created from two
non-isolating factors. A new enumerator reconstructs the certified rank-3
source set, exhausts that move class, and stores one exact witness per
rank-2 output. A separate verifier replays every stored witness and reruns the
complete census and Whitehead certificates.

**Tech stack:** Python 3 standard library, pytest, existing read-only
`two_stabilization`, `acmoves.canon`, `autcanon`, Markdown, JSON, SHA-256.

## Global constraints

- Create new task files only, except for required project `AGENTS.md` lessons.
- Reconstruct sources from the immediate two-stabilization bounds:
  defining words of length at most two and templates of length at most six.
- Work with cyclically reduced rank-3 relators and preserve \(x\) as the
  distinguished generator; do not quotient by ambient automorphisms.
- Enumerate exactly one target-first product of signed cyclic rotations.
- The seam theorem is about this finite move class, not arbitrary relative
  conjugators \(U c V c^{-1}\).
- Existing immediate isolators are excluded from the new-move census because
  the prior certificate already decides them.
- No AC graph search contributes to the verdict.
- CPU only; use `.venv/bin/python3`.
- A floor-13 minimum refutes only this finite candidate.
- Commit and push `codex/proofs` at least every twenty minutes; no PR or merge.
- Do not touch unrelated untracked `hsearch-hyper.bundle`, `prompts/`, or
  `tmp/`.

---

### Task 1: Prove the cyclic one-edge theorem

**Files:**

- Create: `literature/proofs/AK3_ONE_EDGE_COMPRESSION.md`

- [ ] State the move as
  \(\operatorname{cyc}(U'V')\), where \(U'\) is a cyclic rotation of the
  target relator and \(V'\) is a cyclic rotation of the other relator or its
  inverse.
- [ ] Prove it is an AC1--AC3 composite and that a resulting one-\(x\)
  relator permits the second Lemma-11 removal.
- [ ] Prove the seam lemma: if cyclically reduced \(U',V'\), each with at
  least two \(x^{\pm1}\), yield a cyclic reduction with one \(x^{\pm1}\),
  some cyclic representation of the same target-first product has
  `last(U') == inverse(first(V'))`.
- [ ] Treat cancellation cascades by identifying the first seam cancellation.
  If cancellation starts at the wrap seam, rotate both factors across the
  cancelled boundary; the reduced cyclic word remains unchanged.
- [ ] State explicitly that the theorem does not cover an unrestricted
  relative conjugator.
- [ ] State the exact AK(3) finite candidate and its limited negative scope.
- [ ] Run a placeholder/consistency scan, then commit and push.

### Task 2: Implement the word-level move layer test-first

**Files:**

- Create: `experiments/stable_ac/rank3_compression/one_edge.py`
- Create: `tests/stable_ac/test_one_edge.py`

- [ ] Write failing tests for free/cyclic reduction, rotations, displayed-seam
  detection, and exact replay of a hand-checked one-edge isolator.
- [ ] Implement:
  `cyclic_reduce`, `rotations`, `canonical_relator`,
  `canonical_rank3`, `seam_moves`, `apply_one_edge`, and
  `remove_one_edge_isolator`.
- [ ] Make `canonical_rank3` invariant only under relator order and each
  relator's rotation/inversion; preserve generator names.
- [ ] Rebuild accepted immediate rank-3 tuples with the existing
  two-stabilization enumerator inputs, then cyclically canonicalize and
  deduplicate them.
- [ ] Exclude rank-3 states with an immediate one-\(x\) isolator.
- [ ] Hash every deterministic source/move/gate result, including target,
  other, sign, rotation offsets, child, isolator index, expression, and
  output.
- [ ] Deduplicate raw rank-2 outputs before `canon` and `aut_canon`.
- [ ] Run the focused test file, then commit and push.

### Task 3: Build and independently replay the exact certificate

**Files:**

- Create:
  `experiments/stable_ac/rank3_compression/one_edge_certificate.py`
- Create: `results/stable_ac/theory/ak3_one_edge.json`

- [ ] Write a small-bound build/replay test before implementing the driver.
- [ ] Store source-census counts, seam-product count, one-\(x\) incidence
  count, raw/canonical output counts, trace hash, complete floor distribution,
  Aut-orbit groups with witnesses, all minimum-output witnesses, and verdict.
- [ ] Store one exact corridor witness for every raw output.
- [ ] Independently replay each stored source/move/removal row and verify each
  Aut witness with `autcanon.check`.
- [ ] Rerun the full census and require byte-for-byte payload equality.
- [ ] Generate the production JSON with `PYTHONHASHSEED=0`.
- [ ] Run certificate verification and focused regressions, then commit and
  push.

### Task 4: Adjudicate and choose the next proof attempt

**Files:**

- Create: `results/stable_ac/theory/AK3_ONE_EDGE.md`

- [ ] Record only verified counts and the exact theorem scope.
- [ ] If the minimum is at most 12, expand the corridor and classical endpoint
  path into a full independently replayed stable proof.
- [ ] If the minimum is 13, test the return-wall proposition that every
  floor-13 endpoint has AK(3)'s complete Whitehead representative.
- [ ] Explain whether the wall is universal, which combinatorial features
  survive, and formulate the next mechanism from that evidence.
- [ ] Run the relevant stable-AC regression slice and certificate replay.
- [ ] Commit and push. Keep the research goal active unless an actual proof or
  obstruction has been obtained.
