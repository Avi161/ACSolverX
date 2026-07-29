# Reviews of the bounded AK(3) Aut(F2) decision certificate

Date: 2026-07-29

## Exact bounded result

The committed frozen manifest contains 1,000 maps, 285 exact-cellular keys,
and 3,000 ordered spelling memberships.  The decision certificate processes
all 285 keys in committed order and records:

```text
PRIOR_EXACT_DUPLICATE                    50
NOT_SPHERICAL_EXACT                     35
SPHERICAL_REQUIRES_INDEPENDENT_VALIDATION 0
UNSUPPORTED                            200
```

The 35 new negatives split across the proved envelopes as rank 16, `P4` 3,
one-loop 3, and paw-one-loop 13.  Every negative has exact false spherical
status, exact negative verdict, complete solver-specific counters, and
`exhaustive is true`.  Unsupported rows contain no solver evidence.  The 50
prior rows retain 695 ordered provenance records and bypass dispatch.

## Hostile mathematical review

The initial review independently reconstructed all 285 row/member/support/
prior/hash invariants and approved the bounded theorem interpretation, but
returned **REVISE** because the dispatcher had checked and then discarded the
solver's exact `spherical` boolean before serialization.

The fix carries `spherical: bool | null` through the dispatcher and every
result row, with the exact category contract: false on all 35 negatives, true
only on a quarantined positive, and null on every prior or unsupported row.
Missing, flipped, and integer substitutes are rejected during replay.

Focused mathematical rereview: **APPROVE — all findings addressed; no
mathematical drift**.

## Code-quality review

The quality review agreed with the same Important finding and found the
manifest-first ordering, representative/member recovery, prior bypass,
canonical digest/newline, source-hash lifecycle, deterministic Markdown, and
non-writing check path sound.  Focused rereview after the fix: **APPROVE — no
Critical/Important findings**.

Two nonblocking Minors remain for a later branch review:

1. the fixture-only overridden `root` is split from module-global `_ROOT` for
   driver/solver/proof hashing; and
2. no test independently pins the checked-in 285-row artifact bytes/digest
   rather than deriving both digest values from the payload under test.

## Final reviewed bytes and controller replay

```text
driver/test module  58b5c2395125971179c68c4cfb37473b25fefa86234183aec08fb8c8a9a372b1
test module         199dae3fc0a84220a2fa24120c2f172182762759c8a34fbcdbe24cc2a7656bd8
certificate JSON    e8e4b1192e8bb77fab04e0a33c6d8ec2fe9f3968df2dea3cd90b394b7e2e72e3
bounded Markdown    4737f83b7b9f498bb1ff9d836342f6e38d098107960ce20af58a92e41dd4e0e8
ordered row digest  87031a3cb346199a0805d1a6d005778159282406b4ecec3524699f108ab221ee
```

Fresh controller evidence on these bytes: full non-writing decision replay
`OK` in 30.44 seconds, 77 focused/solver tests passed in 4.83 seconds, and
Ruff 0.16.0 passed.

## Proof boundary

The zero spherical count is only a bounded null result for the 285 exact
complexes represented by the three stored spellings of the frozen 1,000-map
BFS prefix.  It proves no `Aut(F2)` closure, no thickenability invariance, no
fact about untested spellings, no AC or stable-AC obstruction, and no
counterexample.  Because there is no spherical row, the positive-only
regular-neighborhood/Regina gate is not triggered.
