# Reviews of the AK(3) prior index and fail-closed dispatcher

Date: 2026-07-29

## Prior exact-certificate index

The implementation freezes exactly five rank-two corpora, 2,691 provenance
rows, and 737 exact-cellular buckets.  It hashes raw source bytes, preserves
literal pairs and stable record identities, and never treats free/cyclic
reduction, ambient automorphism, or an AC relation as duplicate evidence.

Initial review found three Important test gaps: an invalid claimed
cyclic-only adversary, self-referential corpus-order expectations, and failure
to assert all three members of a shared exact-cellular bucket.  Commit
`ab451ab` repairs all three with the genuine freely reduced conjugate `yxY`, a
test-owned literal five-path tuple, and complete ordered provenance.  Scoped
rereview: **all findings addressed; no new Critical/Important breakage**.

Controller verification: 12 tests passed in 1.97 seconds; Ruff 0.16.0 clean.
One nonblocking Minor remains: expose the bucket mapping immutably before a
downstream caller can mutate duplicate evidence.

## Fail-closed theorem dispatcher

The dispatcher classifies the exact literal occurrence-link inventory before
lazy solver import and admits only four proved envelopes: loopless
`K4`/`K4-e`/`C4`, loopless `P4`, one multiplicity-one loop over
`K4`/`K4-e`, and one multiplicity-one loop over a paw away from its
articulation.  Negatives require exact false spherical status plus
`counters.exhaustive is True`; positives require an independently replayed
spherical rotation and remain quarantined.

Initial review found that admitted solver outcomes were not rejected theorem
near-misses and that `xX | y` had two loop classes rather than one loop over a
wrong core.  Commit `39379ea` adds explicit boundary near-misses and the real
literal single-loop-over-`C4` fixture `xy | xXyxY`.  The synthetic paw loop at
the articulation is confined to the private inventory classifier and its germ
degrees `(5,2,2,1)` prove it cannot arise from a balanced literal rank-two
link.  Scoped rereview: **all findings addressed; no new Critical/Important
breakage**.

Controller verification: 61 tests passed in 4.87 seconds; Ruff 0.16.0 clean.
One nonblocking Minor remains: add direct positive-dispatch fixtures for the
permitted loopless `K4` and `C4` kinds in addition to the retained `K4-e`
fixture.

Neither task ran the frozen manifest decision, invoked topology, or made an
AC/stable-AC claim.
