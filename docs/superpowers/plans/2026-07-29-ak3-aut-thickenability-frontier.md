# AK(3) Aut(F2)-Image Thickenability Frontier Implementation Plan

> **Execution rule:** build the frozen manifest and its independent replay
> before making any Neuwirth call.  Use test-driven implementation and obtain
> hostile mathematical plus code-quality review after each phase.

**Goal:** Test a deterministic 1,000-map Nielsen BFS prefix of exact AK(3)
Aut-images for a thickenable representative, without transporting negative
verdicts, conflating spellings, extending an unproved solver envelope, or
announcing an unvalidated positive.

**Scope:** New files only.  No AC/greedy search, no node budget above 1,000,
no solver modification, no Regina claim, and no unstable ambient
automorphism.

## Task 1: Freeze the manifest contract in tests

**Files:**

- Create: `tests/stable_ac/test_ak3_aut_frontier_manifest.py`
- Create: `experiments/stable_ac/thickenable/ak3_aut_frontier_manifest.py`

- [ ] Write failing tests for the seven ordered inverse-closed Nielsen edges,
  their inverse IDs, and the exact composition convention.
- [ ] Write failing tests for identity record zero, first-discovery BFS order,
  distinct reduced map keys, parent/depth consistency, and exact cap 1,000.
- [ ] Write failing tests for inverse-edge words and both map/inverse
  compositions.
- [ ] Write failing tests that distinguish literal, freely reduced, and
  cyclically reduced output, including a case where inverse substitution
  returns only after cancellation.
- [ ] Write failing tests for peeled cyclic conjugators, the reconstruction
  `free_word == prefix + cyclic_core + formal_inverse(prefix)`, and empty-word
  guards.  Store no cancellation trace or trace digest.
- [ ] Write failing tests for the exact-cellular key: signed generator
  permutation, relator swap, independent cyclic rotations and inversions are
  identified; free reduction, transvection, and arbitrary conjugation are not.
- [ ] Write a failing key-order test fixing raw ASCII/code-point comparison of
  the first relator and then the second, with `X < Y < x < y` and no reduction
  during comparison.
- [ ] Implement only enough pure word/map logic to pass these tests.
- [ ] Confirm the module imports no Neuwirth solver and performs no topology
  call.

## Task 2: Emit and independently replay the frozen manifest

**Files:**

- Create: `results/stable_ac/theory/ak3_aut_frontier_manifest.json`
- Extend only the new manifest test/module files.

- [ ] Enumerate the exact 1,000-map BFS prefix using the frozen edge order.
- [ ] Store parent/edge/depth, Nielsen/inverse words, map/inverse images,
  inverse replays, three spelling tracks, peeled prefixes, cellular keys, and
  bucket membership.
- [ ] Add a verifier path that rebuilds every field from the source tuple and
  parent graph rather than trusting the payload.
- [ ] Store an ordered record digest and hashes only of the frozen design and
  manifest-side configuration/driver/map/word/reduction/cyclic-peel/key code,
  plus the exact source tuple; do not hash any future decision-side input.
- [ ] Generate canonical JSON, rerun the verifier, and require byte-for-byte
  equality.
- [ ] Commit and freeze the exact manifest bytes before creating the decision
  driver; never regenerate the manifest after decision code lands.
- [ ] Obtain hostile mathematical review of the map/spelling contracts and a
  separate code-quality review before committing.
- [ ] Commit, append the UTC/hash log entry, and push the branch.

## Task 3: Build the prior exact-certificate index

**Files:**

- Create: `experiments/stable_ac/thickenable/ak3_aut_frontier_certificate.py`
- Create: `tests/stable_ac/test_ak3_aut_frontier_certificate.py`

- [ ] Write failing fixtures that ingest exactly, in frozen order:
  `ak3_neuwirth_census.json`, `ak3_component_thickenability.json`,
  `ak3_cov_thickenability.json`, `ak3_two_hop_cov_thickenability.json`, and
  `ak3_primitive_quotient_thickenability.json`, all under
  `results/stable_ac/theory/`.
- [ ] Reject runtime additions to that corpus and explicitly exclude
  `ak3_rank3_rigid_thickenability.json`, whose rank-three keys cannot equal a
  rank-two cellular key; changing the corpus requires a new schema version.
- [ ] Recompute the new exact-cellular key for every prior exact tuple.
- [ ] Store prior path, record ID, verdict, and file hash for each bucket.
- [ ] Prove by tests that a prior exact duplicate is provenance-linked and not
  rerun by default.
- [ ] Reject Aut-canonical, free-reduced-only, or AC-equivalent matches as
  duplicate evidence.

## Task 4: Implement the fail-closed support dispatcher

**Files:**

- Extend only the new certificate/test files.

- [ ] Write one accepted and one rejected fixture for each of the four proved
  support envelopes.
- [ ] Write unsupported fixtures for disconnected support, multiple loops,
  loop multiplicity greater than one, and an unproved loop/core type.
- [ ] Dispatch only to the existing rank, `P4`, one-loop, and paw-one-loop
  solvers under their exact hypotheses.
- [ ] Require exhaustive counters for every negative and a replayed spherical
  rotation for every positive.
- [ ] Never import or call `check_thickenable.py`.
- [ ] Emit only the four frozen result categories.

## Task 5: Emit and replay the bounded decision certificate

**Files:**

- Create: `results/stable_ac/theory/ak3_aut_frontier_certificate.json`
- Create: `results/stable_ac/theory/AK3_AUT_FRONTIER_RESULT.md`

- [ ] Consume the committed manifest by exact SHA-256.
- [ ] Evaluate each distinct cellular key once unless it is a prior exact
  duplicate.
- [ ] Record support inventory, selected theorem/solver, complete counters or
  witness, prior provenance, and all source hashes.
- [ ] Hash the committed manifest bytes, the decision driver/dispatcher, the
  exact frozen five-file prior corpus, every selected solver, and the exact
  four support-proof files named by the design; do not rebuild or rewrite the
  manifest.
- [ ] Continue through the entire frozen manifest even if a spherical row is
  found.
- [ ] Independently replay every result and require byte-for-byte payload
  equality.
- [ ] Report only bounded map/spelling/key/support/verdict histograms.
- [ ] Label every spherical row
  `SPHERICAL_REQUIRES_INDEPENDENT_VALIDATION`; do not invoke Lackenby.
- [ ] Run focused tests, obtain hostile mathematical and quality reviews,
  inspect exact process exit, commit/log, and push.

## Task 6: Positive-only validation gate

This task is blocked by design unless Task 5 emits at least one spherical
witness.  It is a separate design/review cycle, not part of the initial
frontier implementation.

- [ ] Design an independent occurrence-rotation to regular-neighbourhood
  encoder.
- [ ] Build and validate the exact 3-manifold triangulation.
- [ ] Provision Regina without changing the proof claim.
- [ ] Require `isBall()` plus a hand/topological hostile review.
- [ ] Only then cite Lackenby and the stable ambient theorem to conclude AK(3)
  is **stably** AC-trivial.

## Verification commands

Use the available project Python/`uv` environment identified at execution
time.  The final implementation must provide deterministic commands for:

```text
focused manifest tests
manifest --write followed by manifest --check
focused decision tests
certificate --write followed by certificate --check
```

Do not start detached processes.  Every command must run in the foreground,
record exit status, and be followed by the scoped stale-process audit with
credential-bearing arguments redacted.

## Acceptance criteria

- The advisor-approved frozen contract is implemented without scope drift.
- The manifest contains exactly 1,000 distinct maps and is verdict-independent.
- Both inverse compositions pass for every map.
- All three exact spellings and peeled cyclic data replay.
- Cellular keys use only proved exact homeomorphisms.
- Prior exact duplicates are provenance-linked.
- Unsupported supports fail closed.
- All negatives are exhaustive and all positives quarantined.
- Payloads reproduce byte-for-byte from hashed sources.
- No result is labelled AC/stable-AC without the positive-only validator.
- Branch checkpoints are committed, logged, and pushed at the requested
  interval.
