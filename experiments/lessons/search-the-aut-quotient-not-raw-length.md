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

## A checker that has never failed is not evidence — mutate it

The proof book (`PROOFS.md` / `certificates.json`, built by `make_proof_book.py`) is re-checked by
`verify_proofs.py` from the raw CSV alone. It passed all 135 edges on the first run. That means
nothing until it can be made to fail, so `test_equivalence.py` now tampers with the shipped
certificates seven ways — a substitution that doesn't carry `A` to `B`, a rotated AC move, the right
words under the wrong `pres_id`, a non-invertible `φ` (`x ↦ xx`), two classes fused with no edge to
justify it, a `pure_ac_path` flag set on an impure path, a wrong meeting state — and requires a
non-zero exit on each.

Writing those tests **immediately found a bug in the checker**: `Checker.bad()` returned `False`
instead of `None`, so a failed side leaked `False` into the caller, which then did `list(False)` and
died with a `TypeError`. It exited non-zero — for entirely the wrong reason, with no diagnosis. A
falsy sentinel that is not `None` is indistinguishable from a *value* one frame up.

**Rule:** an error sink returns `None`, never a falsy value. And the mutation that matters most is
the **over-merge** (fuse two classes, add no edge): it is exactly the failure that checking edges one
at a time cannot see, and only the partition rebuild catches it.

## One certificate shape does not fit two kinds of edge

A change-of-variables merge is provable in one line — recover `ψ = φ_B⁻¹ ∘ φ_A` (Nielsen reduction
with tracking, `autinv.py`) and assert `canon(ψ(A)) == canon(B)`. It is by far the most readable
form, and it holds for all 93 of them.

It is tempting to reuse it on the 42 AC edges. **It is false there, by construction.** The two roots
of an `ac` edge lie in *different* `Aut` orbits — that is why an AC move was needed at all — so their
images under any `ψ` have different canonical forms; the two sides differ by exactly the AC moves. A
checker that asserted that equality on an `ac` edge would **reject a correct certificate**. There,
`ψ` is checked for being an automorphism and nothing more, and the proof is the path replay.

The same trap in reverse on the reporting side: on 6 of the 42 the path has an identity `φ` at every
step, so it *is* a pure AC path — but between `A` and `ψ(B)`, not between `A` and `B`. `ψ` is never
the identity, so **no pair of the 261 is joined by a raw AC path.** Round that off and you have
silently upgraded ACA to `~AC`, which is the one error this project keeps having to correct.

## A canonical form hides the very step the reader needs to see

The first proof book printed, for a change-of-variables merge:

```
Substitute x -> x, y -> Y into 19_45:
    (YYYxxyyX, YYYYXyxxYxx)  ==>  (YYYxyyXX, YYYYXXYXXyx)   = 19_50  [MATCH]
```

The user read it and said: *"I don't see it."* They were right — **`y → Y` does not turn the left
string into the right one.** Canonicalisation had silently inverted *and* rotated both relators in
between. Every state in the book is a canonical form, and `canonical_pair_nj` freely reduces, may
invert, rotates to the lex-least form, and may swap the two relators. All four are free (a relator
is a relation, so `r = 1` ⟺ `r⁻¹ = 1`; a rotation is a conjugate, `vu = u⁻¹(uv)u`; both are AC
moves) — but "free" is not "invisible". Printing only the endpoints made a *correct* proof look
false.

The fix is a **normalisation witness** per relator — which raw relator it came from, whether it was
inverted, by how much it was rotated — rendered as one mechanical operation per line:

```
  r1 = YYYxxyyX
       substitute      ->  yyyxxYYX
       invert          ->  xyyXXYYY
       rotate by 3     ->  YYYxyyXX      = r1 of 19_50   [MATCH]
```

**Rule:** if a value is displayed in a normal form, the derivation must show the normalisation, not
just its result. The reader cannot re-derive a canonical form in their head, and a proof they cannot
follow is a receipt.

## Verify the steps you *print*, not just the endpoints

Having added the pencil-steps, the checker still only confirmed that the canonical endpoints agreed.
That is a different claim. A derivation could print `rotate by 4` when the truth is 3, and every
state-level check would still pass — the endpoints match regardless of what the prose says. Only the
*human* is misled, which is worse than a crash, because the book's whole purpose is to be read.

So `verify_proofs.py` now replays each printed step literally: cyclically reduce, invert iff the line
says invert, rotate by exactly `k`, and require the printed result. Three mutation tests corrupt the
printed derivation while leaving the endpoints intact (wrong rotation count, flipped inversion,
corrupted concatenation piece) and require a non-zero exit.

**Rule:** whatever a human is told to check by hand is part of the claim, and must be machine-checked
as literally as it is written. A checker that verifies a *stronger* invariant than the one displayed
still leaves the displayed one unverified.

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
