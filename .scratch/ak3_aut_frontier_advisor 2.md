# Hostile advisor review: direct Aut(F2)-image thickenability frontier

**VERDICT: REVISE**

The proposed experiment is mathematically legitimate and is not blocked by a
known theorem or prior null result.  It may test a frozen finite family of
exact word-realized complexes obtained from AK(3) by simultaneous ambient
automorphisms.  A validated positive would prove **stable** AC-triviality of
AK(3), not unstable AC-triviality; every negative would be local to the exact
recorded spelling.  Implementation must not begin, however, until the five
load-bearing contracts below are made explicit.  In particular, “the first
1,000 automorphisms” and “the reduced image” are not intrinsic objects without
an ordered Nielsen alphabet, a composition convention, a deterministic word
lift, and a final-shell rule.

## Mathematical soundness

1. `literature/proofs/AK3_DUAL_SOURCE_COMPRESSION.md`, Proposition 3.3,
   proves that for every balanced trivial-group presentation \(P\) and every
   \(\phi\in\operatorname{Aut}(F_n)\), simultaneous application of \(\phi\)
   to the complete relator tuple preserves the **stable** AC class.  It does
   not transport thickenability and it does not prove the unstable pairwise
   ambient-automorphism principle.

2. `literature/proofs/AK3_NEUWIRTH.md`, Theorem 2, decides orientable
   thickenability of an exact nonempty word-realized presentation with
   connected link by existence of a compatible spherical occurrence
   rotation.  Its scope explicitly forbids implicit free or cyclic reduction.
   Corollary 3 and Lackenby Theorem 1.3 then imply that a thickenable balanced
   trivial-group image is classically AC-trivial.  Combining that classical
   endpoint with Proposition 3.3 proves only
   \(AK(3)\sim_{\mathrm{st}}\text{standard}\).

3. `literature/proofs/AK3_NEUWIRTH_PHASE_OBSTRUCTION.md` proves only that
   the displayed exact complex
   `xxxYYYY | xyxYXY` is nonthickenable.  It supplies no negative transport to
   a transvection image, a freely reduced spelling, or a cyclically reduced
   spelling.  `.scratch/ak3_aut_thickenability.md` and its approved hostile
   review correctly isolate this gap.

4. Free and cyclic reduction preserve the represented free-group relator but
   not the exact word-realized CW complex.  Therefore a positive on any of the
   literal, freely reduced, or cyclically reduced versions is usable
   algebraically, while a negative is confined to that one version.  The
   three versions must never be silently identified.

No premise invokes thickenability invariance under \(\operatorname{Aut}(F_2)\),
the unstable ambient principle, or a failed-search obstruction.  Subject to
the revisions below, the mathematical implication is sound.

## Numbered load-bearing objections

1. **The BFS object is not yet defined.**  Freeze an inverse-closed ordered
   list of explicit Nielsen substitutions, state whether composition is
   left- or right-action, include the identity, and key a map by the unique
   freely reduced pair \((\phi(x),\phi(y))\).  Store the first-discovery
   parent, edge label, depth, Nielsen word, inverse Nielsen word, inverse
   images, and replay both
   \(\phi\phi^{-1}=\phi^{-1}\phi=\mathrm{id}\).  A cap of 1,000 may cut a
   depth shell and is then a deterministic **BFS prefix**, not a ball and not
   a generator-closed frontier.  Either use that exact phrase and freeze the
   generator-order tie-break, or retain only complete shells whose total is
   at most 1,000.  No finite retained set may be described as closed under the
   Nielsen generators.

2. **Map equality and literal-spelling equality are different contracts.**
   For each distinct map, use the stored freely reduced images
   \(\phi(x),\phi(y)\) as the substitution dictionary; map an inverse letter
   to the formal inverse block, concatenate occurrence by occurrence into
   both AK(3) relators, and perform no cancellation in the `literal` field.
   Do not obtain the literal field by sequentially applying the discovered
   Nielsen word: different Nielsen words for the same map can leave different
   unreduced spellings.  From the frozen literal pair derive and retain a
   deterministic freely reduced pair and then a deterministic cyclically
   reduced pair, including any peeled conjugating prefixes.  Test all three
   exact pairs separately unless two have the same canonical key under the
   proved cellular symmetries.

3. **The current fast solver is not a general Neuwirth implementation.**  A
   generic dispatcher may return YES or NO only in the following proved
   rank-two envelopes:

   - connected loopless \(K_4\), \(K_4-e\), or \(C_4\):
     `neuwirth_rank_solver.py`;
   - connected loopless \(P_4\): `neuwirth_p4_solver.py`;
   - exactly one one-edge A-loop whose deletion leaves a positive parallel
     \(K_4\) or \(K_4-e\) core: `neuwirth_one_loop_solver.py`;
   - exactly one one-edge A-loop over a positive parallel paw, attached away
     from the articulation: `neuwirth_paw_one_loop_solver.py`.

   Every disconnected support, every other loopless support, multiple A-loops,
   a loop class of multiplicity greater than one, and every other one-loop
   core is `UNSUPPORTED`.  `check_thickenable.py` is explicitly an
   `[unverified]` prototype and is not an admissible fallback.  A negative is
   recordable only when the selected proved solver returns
   `spherical == False` and `counters.exhaustive == True`; a positive must
   carry a replayed spherical witness.  No solver or theorem may be extended
   during this experiment.

4. **Prior exact censuses must be ingested before calling the frontier new.**
   At minimum compare exact-cellular keys against the base/orbit-2 and
   1,000-state height-17 records in
   `results/stable_ac/theory/AK3_NEUWIRTH_RESULT.md`, the 34 one-hop records in
   `ak3_cov_thickenability.json`, and the 1,352 two-hop records in
   `ak3_two_hop_cov_thickenability.json`.  Thirty of the one-hop records have
   `n_subs == 1` and are already algebraic automorphic-image presentations;
   the direct frontier can therefore duplicate prior reduced/cyclic outputs.
   Other shipped thickenability certificates may also duplicate exact pairs
   even when their construction is not a direct Aut frontier.  A duplicate
   should point to and hash the prior certificate, not be reported as a new
   decision.  Dedupe only by an explicitly implemented cellular-homeomorphism
   key: signed generator permutations, relator permutation, independent
   cyclic basepoint changes, and independent 2-cell orientation reversals.
   Do not quotient by free reduction, cyclic reduction, a transvection, AC
   equivalence, Aut-canonical form, or common/individual arbitrary
   conjugation.

5. **There is presently no positive-validation path in this checkout.**  A
   direct health check found no `regina` executable and
   `ModuleNotFoundError: No module named 'regina'` in both `/usr/bin/python3`
   and the main ACSolverX `.venv`.  More importantly, the separately
   constructed regular-neighbourhood/handle-to-triangulation encoder required
   by `NEUWIRTH_FEASIBILITY.md` has not been built.  Thus a spherical solver
   witness must be quarantined as `POSITIVE_UNVALIDATED`; it may not invoke
   Lackenby or be announced as an AK(3) result.  Validation requires a
   separately constructed exact \(N(K)\), manifold/validity checks, and an
   independent Regina `isBall()` result (plus hand audit).  Installing Regina
   alone does not close the encoder gap.

## Experimental design

The experiment should be a frozen census, not an adaptive search.  First emit
and hash the complete automorphism manifest and all three spelling tracks;
only afterward attach Neuwirth outcomes.  Do not stop or enlarge the map set
in response to a verdict.  There is no AC/greedy search in scope, and no
failed image may be called a counterexample, hard instance, orbit obstruction,
or saturation result.

Each per-image certificate should contain:

- schema version; exact AK(3) source words; map index, depth, parent and edge;
  reduced map and inverse images; Nielsen words; two-sided inverse replay;
- literal, freely reduced, and cyclically reduced relator pairs, plus their
  exact-cellular canonical keys and all map IDs sharing each key;
- support inventory and the exact solver/theorem selected, or the precise
  fail-closed reason;
- exhaustive counters for a negative, or the complete reconstructed rotation
  witness for a positive;
- prior-certificate provenance when deduplicated;
- SHA-256 hashes of the enumerator, word/reduction code, cellular-key code,
  dispatcher and every solver/proof source relied upon, plus an ordered record
  digest.

The verifier must rebuild every map from its parent edge, verify the inverse,
rederive all three spelling tracks from the source, recompute the
exact-cellular key without trusting stored buckets, rerun the selected solver,
and require byte-for-byte payload equality.  Unsupported cases are a result
category, not a negative.  Internal Neuwirth scheme/phase/seed exhaustion is
not an AC node search, but its counters and runtime must be reported; no
AC/greedy `node_budget > 1000` run is authorized.

## Known-trap check

1. **AK(3) open:** avoided; the plan begins from an open problem and makes no
   prior-settlement claim.
2. **Unstable ambient automorphism:** avoided; only Proposition 3.3's stable
   form is used.
3. **Failed search as counterexample:** avoided if every NO is scoped to the
   frozen spelling/key and every unsupported case stays unknown.
4. **CoV/relabel as search no-op:** not used; prior CoV outputs are only a
   duplicate-control corpus.
5. **Lemma 11/(4+) move costs:** not compared or counted.  Do not report the
   Nielsen-word depth as a stable-AC move length.
6. **Theorem hypotheses versus measured rows:** touched and load-bearing;
   exact support classification must precede every solver call.
7. **No-collapse gates:** not applicable to direct Aut substitution; do not
   import CoV gate language into this census.
8. **Length caps:** no relator-length cap may filter the manifest.  Word growth
   is an observed property; the 1,000-map bound alone makes the result finite.
9. **Closure/saturation:** touched and presently underspecified; a capped BFS
   prefix is not a closed ball or orbit census.
10. **Like-with-like comparisons:** no performance comparison is proposed.
    If runtime/support rates are later compared across spelling modes, use the
    same frozen map manifest and report mode-specific duplicates.

## Smallest safe plan

1. Freeze a versioned, inverse-closed Nielsen alphabet, composition rule,
   deterministic 1,000-map BFS-prefix rule, exact substitution/reduction
   rules, and exact-cellular symmetry key.  Hash this configuration.
2. In a new manifest-only driver, enumerate the maps, inverses, and three
   spelling tracks; independently replay the manifest; compare it against the
   shipped exact-certificate corpus; then freeze and hash it.  Do not call a
   Neuwirth solver while the manifest is still being selected.
3. In a separate new certificate driver, route each distinct exact-cellular
   key through only the four proved support envelopes above.  Emit
   `NOT_SPHERICAL_EXACT`, `SPHERICAL_REQUIRES_INDEPENDENT_VALIDATION`, or
   `UNSUPPORTED`, with complete replay data and source hashes.  Do not modify
   any existing solver.
4. If there is no spherical witness, publish only the bounded histogram:
   frozen maps, spelling/key counts, prior duplicates, supported exhaustive
   negatives, and unsupported cases.  State that nothing was proved outside
   those exact spellings.
5. If there is a spherical witness, continue the census but quarantine the
   claim.  Build and independently review the exact regular-neighbourhood
   encoder in a separate task, provision Regina, and require valid
   3-manifold plus `isBall()` confirmation before invoking Lackenby.  Only
   then conclude stable AC-triviality of AK(3).

## What I checked

- `.claude/agents/ac-advisor.md` (complete local advisor contract).
- `AGENTS.md`, `CLAUDE.md`, `experiments/stable_ac/ESCAPE_PLAN.md`, and
  `docs/superpowers/specs/2026-07-23-ak3-neuwirth-theory-design.md` for the
  operating/result bar.
- `.scratch/ak3_aut_thickenability.md` and
  `.scratch/ak3_aut_thickenability_review.md`, including the APPROVE rereview.
- `literature/proofs/AK3_NEUWIRTH_PHASE_OBSTRUCTION.md` and
  `literature/proofs/AK3_NEUWIRTH.md`.
- `literature/proofs/AK3_DUAL_SOURCE_COMPRESSION.md`, Proposition 3.3 and its
  use downstream.
- `experiments/stable_ac/thickenable/NEUWIRTH_FEASIBILITY.md`,
  `.scratch/neuwirth_phase_obstruction_report.md`, and
  `results/stable_ac/theory/AK3_NEUWIRTH_RESULT.md`.
- The support classifiers and decision entry points in
  `neuwirth_rank_solver.py`, `neuwirth_p4_solver.py`,
  `neuwirth_one_loop_solver.py`, `neuwirth_paw_one_loop_solver.py`, the direct
  occurrence census in `neuwirth_permutation_certificate.py`, and the explicit
  warning/scope in `check_thickenable.py`.
- `literature/proofs/AK3_SYNCHRONIZED_PLANARITY.md`,
  `AK3_P4_SYNCHRONIZED_PLANARITY.md`,
  `AK3_ONE_LOOP_SYNCHRONIZED_PLANARITY.md`, and
  `AK3_PAW_ONE_LOOP_PLANARITY.md` for the fail-closed boundaries.
- `results/stable_ac/theory/AK3_COV_THICKENABILITY.md`,
  `AK3_TWO_HOP_COV_THICKENABILITY.md`, their JSON certificate inventories,
  and the existing exact thickenability corpus for duplicate risk.
- `experiments/equivalence_classes/lib/autcanon.py` for the repository's map
  composition convention and exact reduced-map representation.  Its
  Aut-canonical presentation key is **not** approved as an exact-complex
  quotient here.
- Current local Regina availability in the system interpreter and the main
  project virtual environment.

## Frozen-design rereview

**REREVIEW VERDICT: REVISE**

The frozen design closes the mathematical red lines and most of the first
review's implementation contracts.  The seven Nielsen substitutions, all
inverse IDs, and the declared composition direction are correct.  The design
is not yet internally executable as phased, however, and its prior-certificate
universe and two byte-level conventions are still not frozen.  These are
surgical specification repairs; there is no mathematical reason to block the
experiment.

### Prior findings now closed

1. **Nielsen alphabet, composition, and inverses — closed.**  The displayed
   alphabet is inverse-closed:

   ```text
   swap^-1 = swap
   inv_x^-1 = inv_x
   inv_y^-1 = inv_y
   x_mul_y^-1 = x_mul_Y
   y_mul_x^-1 = y_mul_X
   ```

   With `child = phi o nu` and `child(a) = substitute(nu(a), phi)`, appending
   an edge to the discovery word gives the stated composition order, and
   reversing the edge word while replacing each edge by its inverse gives
   the inverse map in the correct order.  I independently replayed all seven
   displayed inverse pairs through the repository's reduced-map composition;
   both products are `(x,y)` in every case.

2. **Finite-map scope and replay — closed.**  Identity is record zero; map
   equality is the exact freely reduced image pair; FIFO order plus the fixed
   seven-edge order defines first discovery; and the cap is honestly called a
   deterministic 1,000-map BFS prefix, not a ball, closure, or orbit census.
   Parent/edge/depth, forward and inverse edge words, inverse images, and both
   inverse compositions are all required before topology is consulted.

3. **Exact spelling separation — closed, subject only to Finding 4 below.**
   Literal images are derived from the unique stored reduced map dictionary,
   not from a nonunique Nielsen path.  Formal inverse blocks are concatenated
   without cancellation; free reduction starts from that literal word; cyclic
   peeling starts from that freely reduced word; and the peeled prefix is
   retained.  The three exact complexes are never identified by a negative.

4. **Cellular quotient — mathematically closed, subject only to the ordering
   convention in Finding 3 below.**  The proposed orbit uses exactly the eight
   signed basis permutations, relator swap, independent relator rotations,
   and independent relator inversions.  Those are genuine cellular
   homeomorphisms.  Free/cyclic reduction, transvections, Aut-canonicalization,
   AC moves, and arbitrary conjugation are correctly excluded.

5. **Solver support and verdict scope — closed.**  The four proved envelopes
   are stated exactly and every other support fails closed.  The unverified
   `check_thickenable.py` is excluded.  NO requires a false spherical flag and
   exhaustive counters; YES requires a replayed spherical witness and remains
   `SPHERICAL_REQUIRES_INDEPENDENT_VALIDATION`.

6. **Positive and global reporting red lines — closed.**  The missing
   regular-neighbourhood encoder and Regina path are explicit blockers.  No
   spherical row invokes Lackenby; the entire frozen prefix is still processed;
   negatives and unsupported rows remain bounded; Nielsen depth is not costed
   as stable moves; and only a separately validated positive yields the
   stable-only AK(3) conclusion.

### Exact open findings

1. **The source-hash contract contradicts the two-phase plan.**  The design
   says both artifacts hash the prior inputs, dispatcher, selected solvers,
   and support proofs.  But Task 2 must emit, verify, commit, and freeze the
   manifest before Task 3 creates the new certificate/dispatcher module.
   Therefore the manifest cannot hash that future dispatcher while remaining
   the committed byte-for-byte input to the decision phase.  It also should
   not change when a decision solver or prior certificate changes.  Repair:
   the manifest hashes only its frozen design/configuration, manifest driver,
   map/word/reduction/cyclic-peel code, cellular-key code, and exact source
   tuple.  The decision certificate hashes the manifest bytes plus its own
   driver/dispatcher, the explicit prior inputs, selected solvers, and exact
   support proofs.  Do not regenerate the manifest after decision code lands.

2. **The prior-certificate corpus is still open-ended and omits a shipped
   rank-two exact census.**  “Ingest and hash at least” is not a frozen input
   identity, and Task 3 names only the base/component, one-hop, and two-hop
   files.  The repository also ships
   `results/stable_ac/theory/ak3_primitive_quotient_thickenability.json`, with
   303 exact rank-two quotient records.  Those may or may not intersect the
   direct Aut-image keys; novelty must be checked rather than assumed.
   Replace “at least” with the exact frozen list:

   ```text
   results/stable_ac/theory/ak3_neuwirth_census.json
   results/stable_ac/theory/ak3_component_thickenability.json
   results/stable_ac/theory/ak3_cov_thickenability.json
   results/stable_ac/theory/ak3_two_hop_cov_thickenability.json
   results/stable_ac/theory/ak3_primitive_quotient_thickenability.json
   ```

   Record that `ak3_rank3_rigid_thickenability.json` is deliberately excluded
   because its exact complexes have rank three and cannot share a rank-two
   cellular key.  Any later prior corpus change belongs in a new manifest/
   certificate schema version, not an execution-time choice.

3. **“Lexicographically least” does not freeze the cellular key's total
   order.**  The result must be identical across replay implementations.
   Specify comparison of the ordered relator pair by raw code-point/ASCII
   string order, first relator then second; for this alphabet that is
   `X < Y < x < y`.  No reduction or alternate symbol order may occur during
   comparison.  Hash this convention with the key implementation.

4. **The stored free-reduction trace and peeled-conjugator replay are not
   byte-defined.**  Different cancellation orders give the same reduced word
   but different “full traces.”  Either remove the trace/digest as unnecessary
   certificate data, or freeze a left-to-right stack reducer and the exact
   canonical trace record (including original input positions and cancelled
   pair) before tests are written.  Also require the explicit reconstruction
   assertion
   `free_word == prefix + cyclic_core + formal_inverse(prefix)` for every
   relator.  The reduced words themselves are already mathematically
   unambiguous; this finding concerns deterministic payload replay.

### Smallest repair before implementation

Make only the four specification edits above, preserve every already-frozen
mathematical boundary, and rereview the edited paragraphs.  Do not alter the
seven substitutions, inverse IDs, composition direction, BFS cap, solver
envelopes, positive quarantine, or stable-only conclusion; those are correct.

## Final frozen-design rereview — 2026-07-29

**FINAL REREVIEW VERDICT: APPROVE**

The surgically edited design and implementation plan close all four residual
findings from the preceding rereview.  I found no new residual finding and no
drift in an already-closed mathematical boundary.

1. **Phase-consistent integrity inputs — closed.**  The manifest now hashes
   only its frozen design/configuration, manifest driver, manifest-side
   map/word/free-reduction/cyclic-peel/cellular-key code, and exact AK(3)
   source tuple.  It explicitly excludes the future decision driver, prior
   corpus, dispatcher, solvers, and support proofs.  The decision certificate
   separately hashes the committed manifest bytes, its driver/dispatcher,
   frozen prior inputs, selected solvers, and the four exact support proofs.
   The plan freezes and commits the manifest before creating decision code and
   forbids later manifest regeneration.  The former phase contradiction is
   removed.

2. **Exact prior corpus and schema rule — closed.**  Both documents freeze the
   same ordered five-file rank-two corpus:

   ```text
   ak3_neuwirth_census.json
   ak3_component_thickenability.json
   ak3_cov_thickenability.json
   ak3_two_hop_cov_thickenability.json
   ak3_primitive_quotient_thickenability.json
   ```

   They explicitly exclude `ak3_rank3_rigid_thickenability.json` because a
   rank-three exact complex cannot share a rank-two cellular key, reject
   runtime additions, and require a new schema version for any later corpus
   change.  Prior provenance remains path/record/verdict/file-hash based and
   only exact-cellular equality deduplicates.

3. **Cellular-key total order — closed.**  The key compares the first relator
   and then the second by raw ASCII/code-point string order, explicitly
   `X < Y < x < y`, with no reduction or alternate generator order during
   comparison.  The plan includes a dedicated failing test for that order.
   The quotient group itself is unchanged and still contains only signed
   generator permutations, relator swap, independent cyclic rotations, and
   independent relator inversions.

4. **Reduction/cyclic replay bytes — closed.**  Cancellation traces and trace
   digests have been removed from certificate data.  The free track retains
   only its unambiguous freely reduced word.  The cyclic track retains the
   deterministic peeled prefix and core and must replay
   `free_word == prefix + cyclic_core + formal_inverse(prefix)` for every
   relator.  The plan tests that identity and empty-word guards explicitly.

### No boundary drift

- The seven inverse-closed Nielsen substitutions, inverse IDs, composition
  direction, map key, identity record, FIFO edge order, and deterministic
  1,000-map BFS-prefix scope are unchanged.
- Literal/free/cyclic spellings remain dictionary-derived and separate exact
  complexes; negatives never transfer between them.
- Cellular deduplication still uses only proved exact homeomorphisms.
- The four proved Neuwirth envelopes are unchanged; all other supports remain
  `UNSUPPORTED`, and `check_thickenable.py` remains forbidden.
- Every negative still requires exhaustive solver counters.  Every spherical
  witness remains quarantined until the separate exact-neighbourhood encoder,
  valid 3-manifold construction, Regina `isBall()`, and hostile hand review
  all succeed.
- No AC/greedy search, Aut closure, thickenability invariance, unstable
  ambient automorphism, failed-search obstruction, or Nielsen-depth move-cost
  claim has been introduced.
- Lackenby is invoked only after independent positive validation, and the
  transported conclusion for AK(3) remains **stable AC-triviality only**.

The frozen contract is approved for implementation as written.  This
approval does not approve any future result until the manifest and decision
payloads pass the specified independent replays and source-hash checks.
