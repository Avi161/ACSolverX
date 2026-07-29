# AK(3) Aut(F2)-Image Thickenability Frontier Design

## Goal and theorem boundary

Construct a frozen, replayable census of at most 1,000 explicitly certified
automorphisms of `F(x,y)`, form three exact word-realized presentations from
each simultaneous AK(3) image, and decide thickenability only inside the
already proved Neuwirth solver envelopes.

A spherical record is not an AK(3) result in this checkout.  It is quarantined
until a separately constructed regular-neighbourhood encoder and an
independent Regina `isBall()` replay validate the claimed thickening.  After
that validation, Lackenby's theorem makes the image classically AC-trivial,
while the stable ambient-automorphism theorem transports only the **stable**
conclusion back to AK(3).

Every negative is bounded to one exact spelling in the frozen manifest.  The
census proves neither thickenability invariance under `Aut(F2)`, closure of an
Aut orbit, unstable ambient equivalence, nor an AC/stable-AC obstruction.

## Why the frontier is admissible

The displayed AK(3) complex is nonthickenable, but the reviewed exact-complex
audit proves that only signed generator permutations are known to preserve
that verdict.  A Nielsen transvection changes the marked rose by a
non-embedded fold when its output is respelled on the original rose; no cited
theorem identifies the resulting literal occurrence-book complex with the
old embedded spine.  Therefore reduced transvection images cannot be pruned
from a direct thickenability test.

The route passed an initial hostile AC/stable-AC gate subject to the contracts
below.  Implementation remains forbidden until the frozen design itself
passes the requested rereview.  It is a finite exact-complex census, not an
AC search and not evidence for a counterexample if it finds no positive.

## Frozen Nielsen manifest

### Ordered inverse-closed alphabet

Use this exact ordered alphabet of substitutions, written as the image pair
`(nu(x), nu(y))`:

```text
0 swap      = (y, x)       inverse 0
1 inv_x     = (X, y)       inverse 1
2 inv_y     = (x, Y)       inverse 2
3 x_mul_y   = (xy, y)      inverse 4
4 x_mul_Y   = (xY, y)      inverse 3
5 y_mul_x   = (x, yx)      inverse 6
6 y_mul_X   = (x, yX)      inverse 5
```

Words use lowercase generators and uppercase inverses.  Every stored map
image is freely reduced.

### Composition convention

If the parent is `phi` and the edge is `nu`, the child is

```text
child = phi o nu,
child(a) = freely_reduce(substitute(nu(a), phi(x), phi(y))).
```

The identity `(x,y)` is record zero.  A map key is the exact freely reduced
pair `(phi(x), phi(y))`.  Breadth-first search uses a FIFO queue and visits
the seven edge labels in the displayed order.  First discovery fixes parent,
edge, depth, and Nielsen word.

Retain the first 1,000 distinct map keys, including the identity.  If the cap
cuts a depth shell, call the object only the **frozen 1,000-map BFS prefix**.
It is not a ball, frontier closure, or generator-closed subset.

For every record store:

- map index, parent, edge, depth, and Nielsen edge word;
- inverse edge word (reverse the word and replace every edge by its displayed
  inverse);
- `phi(x), phi(y)` and independently derived inverse images;
- both composition replays `phi o phi^-1 = id` and
  `phi^-1 o phi = id`.

The map set is selected and hashed before any Neuwirth call.  Verdicts may
never alter or extend the prefix.

## Three exact spelling tracks

Use AK(3)'s exact source tuple

```text
xxxYYYY | xyxYXY
```

For each distinct map, derive all tracks from the stored reduced image
dictionary, never by replaying the first-discovery Nielsen word.

1. **Literal.** Replace each lowercase occurrence by the corresponding map
   image and each uppercase occurrence by its formal inverse block; concatenate
   without any cancellation.
2. **Freely reduced.** Freely reduce each literal relator.  Retain only the
   resulting word; no cancellation trace or trace digest is certificate data.
3. **Cyclically reduced.** Starting from the freely reduced word, repeatedly
   peel inverse first/last letters.  Retain the peeled conjugating prefix and
   the deterministic remaining word.  For every relator replay the exact
   reconstruction
   `free_word == prefix + cyclic_core + formal_inverse(prefix)`.  Do not
   silently choose another cyclic rotation.

The three tracks are three exact complexes.  A positive on any track is
algebraically usable after independent topological validation; a negative
does not transfer to either other track.  Empty relators, disconnected links,
and unsupported occurrence patterns fail closed.

## Exact-cellular symmetry key

Deduplicate only by homeomorphisms of the exact word-realized complex:

- the eight signed permutations of `x,y`;
- relator permutation;
- independent cyclic rotation of each nonempty relator; and
- independent inversion of each relator.

The key is the lexicographically least ordered pair among this finite orbit.
Compare the first relator and then the second by raw ASCII/code-point string
order; on the allowed alphabet this is `X < Y < x < y`.  Perform no reduction
and use no alternate generator order during comparison.  No free reduction,
cyclic reduction, transvection, Aut-canonical form, AC move, or arbitrary
conjugation is part of the key.

Every map/spelling record retains both its raw pair and cellular key, and
every bucket retains all contributing map IDs and spelling modes.

## Prior-certificate deduplication

Before calling a result new, ingest and hash exactly this frozen rank-two
prior corpus, in the displayed order:

```text
results/stable_ac/theory/ak3_neuwirth_census.json
results/stable_ac/theory/ak3_component_thickenability.json
results/stable_ac/theory/ak3_cov_thickenability.json
results/stable_ac/theory/ak3_two_hop_cov_thickenability.json
results/stable_ac/theory/ak3_primitive_quotient_thickenability.json
```

Deliberately exclude
`results/stable_ac/theory/ak3_rank3_rigid_thickenability.json`: its exact
complexes have rank three and cannot share a rank-two cellular key.  Any later
change to the prior corpus requires a new manifest/certificate schema version;
it is never an execution-time choice.

Compute their cellular keys with the new key implementation.  A duplicate
references the prior certificate path, record ID, source hash, and prior
verdict.  It is not rerun or counted as a new exact-complex decision unless a
dedicated audit flag explicitly requests a replay.  No prior Aut-canonical or
free-reduced identity is accepted as an exact-cellular duplicate.

## Fail-closed Neuwirth dispatcher

The certificate phase may decide only the proved connected rank-two support
envelopes:

1. loopless positive parallel `K4`, `K4-e`, or `C4` via
   `neuwirth_rank_solver.py`;
2. loopless positive parallel `P4` via `neuwirth_p4_solver.py`;
3. exactly one one-edge `A`-loop over a positive parallel `K4` or `K4-e`
   core via `neuwirth_one_loop_solver.py`; and
4. exactly one one-edge `A`-loop over a positive parallel paw, away from the
   articulation, via `neuwirth_paw_one_loop_solver.py`.

Everything else is `UNSUPPORTED`, including disconnected links, multiple
loops, loop multiplicity greater than one, and unproved loop/core supports.
`check_thickenable.py` is an unverified prototype and is never a fallback.

A negative requires `spherical == False` and `counters.exhaustive == True`.
A positive requires a replayed compatible spherical rotation witness, but is
recorded only as `SPHERICAL_REQUIRES_INDEPENDENT_VALIDATION`.  The final
categories are:

```text
PRIOR_EXACT_DUPLICATE
NOT_SPHERICAL_EXACT
SPHERICAL_REQUIRES_INDEPENDENT_VALIDATION
UNSUPPORTED
```

## Positive quarantine

This checkout has neither the required exact regular-neighbourhood encoder
nor a working Regina validation path.  A spherical row therefore cannot be
announced as thickenable or used to invoke Lackenby.

Validation is a separate project milestone:

1. build `N(K)` from the exact occurrence rotation independently of the
   Neuwirth solver;
2. verify the resulting triangulation is valid and is a 3-manifold with the
   claimed presentation spine;
3. run Regina `isBall()` on that exact object; and
4. obtain a hand/topological hostile review.

Only after all four pass does the implication become:

```text
validated thickenable Aut-image
  => image is classically AC-trivial (Lackenby)
  => AK(3) is stably AC-trivial (stable ambient automorphism).
```

The Nielsen depth is not an elementary stable-AC move length.

## Artifacts and separation of phases

Manifest phase, before any topology call:

- `experiments/stable_ac/thickenable/ak3_aut_frontier_manifest.py`
- `tests/stable_ac/test_ak3_aut_frontier_manifest.py`
- `results/stable_ac/theory/ak3_aut_frontier_manifest.json`

Decision phase, consuming the frozen manifest byte-for-byte:

- `experiments/stable_ac/thickenable/ak3_aut_frontier_certificate.py`
- `tests/stable_ac/test_ak3_aut_frontier_certificate.py`
- `results/stable_ac/theory/ak3_aut_frontier_certificate.json`
- `results/stable_ac/theory/AK3_AUT_FRONTIER_RESULT.md`

No existing solver, runner, or certificate implementation is modified.

## Replay and integrity

The manifest verifier must independently:

- rebuild every child from its parent edge;
- verify first-discovery order and the exact 1,000-map prefix;
- verify both inverse compositions;
- rederive all three spelling tracks from the source and stored map images;
- recompute every exact-cellular key; and
- require byte-for-byte canonical JSON equality.

The decision verifier must independently:

- re-ingest the frozen manifest hash;
- rebuild the prior-certificate key index;
- reclassify every support before selecting a solver;
- rerun every new supported exact key;
- replay every negative exhaustion or positive rotation witness; and
- require byte-for-byte canonical JSON equality.

The manifest hashes only its frozen design/configuration, its manifest driver,
the map/word/free-reduction/cyclic-peel and cellular-key code used to build it,
and the exact AK(3) source tuple.  It neither names nor hashes the future
decision driver, prior corpus, dispatcher, solver, or support proof.  Once the
manifest is committed, the decision phase consumes those exact bytes and
never regenerates the manifest.

The decision certificate hashes the committed manifest bytes, its own
driver/dispatcher, every file in the explicit frozen prior corpus, each
selected file from this fixed solver list,

```text
experiments/stable_ac/thickenable/neuwirth_rank_solver.py
experiments/stable_ac/thickenable/neuwirth_p4_solver.py
experiments/stable_ac/thickenable/neuwirth_one_loop_solver.py
experiments/stable_ac/thickenable/neuwirth_paw_one_loop_solver.py
```

and all four exact support proofs:

```text
literature/proofs/AK3_SYNCHRONIZED_PLANARITY.md
literature/proofs/AK3_P4_SYNCHRONIZED_PLANARITY.md
literature/proofs/AK3_ONE_LOOP_SYNCHRONIZED_PLANARITY.md
literature/proofs/AK3_PAW_ONE_LOOP_PLANARITY.md
```

Ordered record digests bind iteration order in each artifact.

## Non-goals and reporting

- No AC/greedy search is run.
- No relator-length cap filters the manifest.
- The 1,000-map prefix is not a saturation or closure theorem.
- Unsupported rows are not negatives.
- No failed row is evidence of an AC or stable-AC counterexample.
- Runtime/support histograms compare spelling modes only on the same frozen
  map manifest.
- If there is no validated positive, the only reportable result is the
  bounded exact histogram and its replayable certificate.

## Acceptance criteria

- Hostile advisor re-review approves this frozen contract before code.
- Manifest and decision phases are separate and deterministic.
- Exactly 1,000 distinct maps are selected without consulting verdicts.
- Every map and inverse replays both ways.
- Literal, free, and cyclic tracks are retained separately.
- Cellular deduplication uses only proved homeomorphisms.
- Prior exact decisions are provenance-linked rather than rediscovered.
- The prior rank-two corpus is exactly the frozen five-file list above.
- Solver dispatch fails closed outside the four proved envelopes.
- Every negative is exhaustive; every positive remains quarantined.
- Focused tests and independent payload replay pass.
- No unnecessary proof/test process remains after verification.
