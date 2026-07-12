# [2026-07-11] To find AC merges, search modulo Aut(F₂) — raw length is the wrong ruler [WORKS]

## The problem

The 261 "unsolved" Miller–Schupp reps are 168 distinct problems up to change of variables
(Whitehead's algorithm — exact, and a wall: no `Aut(F₂)` argument can do better). Going below 168
requires finding genuine **AC-move** connections between the roots. The 1M-node greedy sweep found
exactly 2, both by accident.

## What did not work, and the measurement that killed it

The obvious approach — a multi-source AC-move BFS from all 168 roots, union-find merging any two
whose balls touch — **fails at any locally affordable budget.** Calibrating against the one merge
we already knew (`19_52 ≡ 18_9`):

| total-length cap | states in the ball of both roots | merged? |
|---|---|---|
| 24 | 372 (exhausted) | no |
| 26 | 1,854 (exhausted) | no |
| 28 | **8,923 (exhausted — heap empty)** | **no** |
| 30 | 44,939 | no |
| 32 | 223,251 (hit the 20k/source pop budget) | no |

The ball is *exhaustively* explored at cap 28 and the roots do not meet. Ball size grows ~5× per
+2 of cap. So the AC path between two roots of length 18 and 19 **climbs above total length 30**,
and a length-ordered BFS must enumerate everything under the hump before it can cross. This is the
Two-Hump paper's hump, and it is fatal to brute force.

## What worked

**Search the AC graph modulo `Aut(F₂)`, and measure the hump in `Aut`-minimal length.**

A state of raw length 34 can be one change of variables away from a state of length 16. Re-rulered
that way, the *same two roots merge in 8 pops, in 0.4 seconds* — versus no merge at 20,000 pops per
source in the raw search. That is a ~2,500× improvement, and it is the difference between the
experiment being impossible and being cheap.

- **Node** = an `Aut(F₂)`-class, keyed by its Whitehead canonical form.
- **Edge** = an AC move applied to the class's `Aut`-minimal representative.
- **Priority** = `Aut`-minimal total length.

Each edge is "a change of variables, then an AC move"; both preserve AC-triviality, so a collision
proves the two roots are **the same problem** (ACA-equivalent). It does *not* prove an AC path
exists between them — keep those two claims separate.

Result: **168 → 127 or better**, every merge machine-checked.

## Three traps inside the fix

1. **Peak reduction alone is not a valid key.** It is tempting to skip Whitehead's phase 2 (the
   minimal-level-set BFS) because it costs 25× more than the descent. Don't: peak reduction is
   **not confluent**, and keying on the peak-reduced form splits the 168 true classes into **259**.
   Phase 2 is what makes the invariant complete. Use the cheap phase-1 length as a *pre-filter*
   (drop children over the cap before paying for phase 2), never as the key.

2. **Never call `canon_pair` inside the peak-reduction descent.** The descent only needs the
   cyclically-reduced *length* of each candidate, and `canon_pair` is an O(n²) rotation scan.
   Calling it for all 20 Whitehead automorphisms on every descent step cost **11 ms/state ≈ 16 h**
   over the sweep. Reducing instead of canonicalising, plus Booth's O(n) least rotation, brought it
   to 0.18 ms. Memoise the two phases *separately* — many raw states peak-reduce to the same
   minimal pair, so phase 2 is hit far more often than phase 1.

3. **The verifier must not share the canonicalisation the search uses.** Both sides originally
   called `words.canon_pair` — my own freshly written Booth routine. A bug in it would have been
   invisible: search and checker would agree on a wrong canonical form and a bad merge would pass.
   The verifier now canonicalises through the repo's numba `canonical_pair_nj`, which the greedy
   test suite already guards.

## Verify the partition, not just the merges — and never trust a derived field

Two separate near-misses, both caught only because the checks were *external* to the search:

1. **Verifying every merge does not verify the count.** The verifier happily checked all 135
   merges while never confirming that the reported 126 classes were the transitive closure of
   *those* merges. A union-find that over-merged would have sailed through — every individual
   merge still checks out, and the `|det|` guard is toothless when `|det| = 1` everywhere. The
   fix is ten lines: rebuild the partition from the verified pairs alone and require set equality
   with the reported classes. Only then is the *number* a result. (Doing this immediately caught a
   bug in the check itself: with bridge sources seeded, a chain runs `rep → bridge → rep`, so the
   closure must be taken over **all** sources and then projected onto the ones you are counting.)

2. **A derived field reported four presentations as SOLVED.** The runner computed the trivial
   component as `dsu.find(S - 1)` — correct only while `TRIVIAL` was the last source. The moment
   bridge sources were appended after it, `S - 1` became a bridge and the code reported *that*
   component as solved. Four of the 261 appeared to be AC-trivial. They are not; `TRIVIAL` is alone
   in its class in every run. **A claimed solve is the biggest claim the pipeline can make, so it
   must be cross-checked against the recorded partition, never read off an index.**

## Validate against facts the search did not produce

Four external controls, all of which the machinery passes — this is what makes a *negative* result
(0 of the 261 are AC-trivial) mean something instead of nothing:

- the 2 merges the 1M-node sweep found by accident → **2/2** rediscovered;
- the upstream 550 → 261 AC-reduction of the Miller–Schupp cells → **12/12** reproduced;
- the 640 MS cells the grid marks **trivial**, seeded against a trivial source → **13/14** correctly
  identified as AC-trivial, usually in <20 pops;
- the known 261 → 168 `Aut` partition, reproduced at seed time with zero search → **168/168**.

**Rule:** when a search must cross a length hump, first ask whether the length function is the
right one. Quotient by every symmetry that preserves the *question* (here `Aut(F₂)`), and re-measure
the hump in the quotient before spending compute on the raw graph. And validate a search against
equivalences produced by somebody else's code, not against its own output.
