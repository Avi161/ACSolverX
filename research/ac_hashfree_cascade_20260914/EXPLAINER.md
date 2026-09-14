# The two 1k-budget solvers in this repository, explained

Two different fixed procedures in this repository reach near-complete coverage at a
budget of 1,000 work units per presentation.  They are related but not the same
algorithm, and both keep a visited-set hash map and a small pattern table somewhere
inside.  This note explains what each one does, step by step, and what the
`hfcascade.py` in this directory changes.

## 1. The MS-640 cascade (`experiments/search/cascade_heuristics.py`)

Result: 640/640 solved Miller–Schupp presentations at 1,000 charged units,
at most 404 units on one row (`results/heuristic_search/goal_frontiers/MS640_RESULTS.md`).

The cascade is three components in a fixed order, sharing one budget.

**(a) Basis normalisation** (`basis_moves.reduce_basis_key`).  Apply, while one
exists, the Nielsen map among `x->xy, x->xY, y->yx, y->yX` whose exact cyclic-length
response (computed from signed adjacent-letter counts) is the most negative; then
choose the smallest of the eight signed generator permutations.  Every accepted map
is one unit and is recorded as an `automorphism` step of the certificate.  This is a
strict descent: it cannot cycle and needs no memory.

**(b) The short-relator rewrite** (`bs_collapse.bs_collapse`).  If one relator is,
up to rotation, inversion and a signed choice of generators, `b^-1 a b a^-2` (the
Baumslag–Solitar relation `b^-1 a b = a^2`), and the companion has `b`-exponent sum
±1, the companion is rewritten with that relation.  Each rewrite moves one `b` across
a block of `a`'s (`b^-1 a^k -> a^{2k} b^-1`, or `b a^{2k} -> a^k b`) and is realised
as ONE ordinary substitution move: the companion is multiplied by a cyclic conjugate
of the donor whose seam cancels the block.  Blocks double at every crossing, so the
companion temporarily grows (to 131 letters on the hardest rows) while its number of
`b`-letters falls by one per crossing.  When a single `b` remains the companion reads
`b = a^k`; the donor is rewritten to `a^-1`, which then deletes the remaining `a`'s.
This is Britton reduction in the HNN extension BS(1,2), compiled into AC moves.

**(c) Two searches, in order.**  If (b) is not applicable or stalls, restart from the
original input with a best-first search over substitution moves plus the four Nielsen
neighbours, ordered by `L + 40 S` (`S` = smaller mean block), for at most 500 pops;
then hand the remaining budget to the production `S20_MK2` ordering
`L + 20 S + 2 MK`.  On MS-640 no row ever reached the last arm: 254 rows finish in
(b) and 386 in the first search.

Where the hash map and the table are: the searches keep a `parent` dictionary
keyed by the packed canonical state (visited set and path reconstruction), and
recogniser (b) enumerates the eight spellings of `b^-1 a b a^-2` and matches the
donor against them.

## 2. The AC19 final policy (`research/supermoves_20260908/final_policy.py`)

Result: 72,052 / 72,779 Aut-minimal AC19 representatives at 1,000 heterogeneous
units, no relator-length cap; 727 unsolved
(`results/heuristic_search/ac19_final_policy_full_1k/`).

Three stages, one shared budget:

**Stage 1, strict donor route (≤ 250 units).**  For each relator in turn, apply the
Nielsen map that shortens THAT relator most (its cyclic length), even when the
companion grows, until nothing shortens it.  If the pair now shows a certified
finishing pattern — a two-block pair `(x^m y^n, x^p y^q)` with determinant ±1 (solved
by Euclid on the exponent matrix, each row operation four AC moves), a relator with a
single occurrence of one generator (primitive; the companion's letters are deleted
one by one), or a consecutive Baumslag–Solitar pair `b^-1 a^m b a^-(m+1)` whose
Britton preflight pinches to one stable letter — a small `S20` search with those
terminals is run inside the remaining stage budget.

**Stage 2, plain `S20_MK2` (≤ 872 units).**  Restart from the input and run the
ordinary best-first substitution search with `L + 20 S + 2 MK`.  This is the
production heuristic; 43,405 of the 43,406 rows routed here solve.

**Stage 3, incumbent restart (the remainder).**  Restart once more with the same
score plus a Whitehead term `1.5 W` (best Nielsen-map length change), Nielsen
neighbours as edges when no stalled BS core is present, a `4 T` term (stable letters
minus one) when one is, all gates checked on generated states, and a bounded
"high-core escape" continuation.  612 of 1,338 rows routed here solve; the 726
failures of this stage plus one failure of stage 2 are the 727.

Where the hash map and the tables are: every search keeps the packed-state
`parent` dictionary; the BS recogniser (`cheap_gates._bs_patterns_for_length`,
`bs_preflight.donor_orientations`) is a cached table of the canonical spellings of
`b^-1 a^m b a^-(m+1)` for each donor length; the two-block and one-occurrence gates
are structural.

## 3. What the 727 leftovers look like

Measured on `unsolved.csv` (script in the session record, reproduced by
`analyse727.py` there):

* none of the 727 has a primitive relator (strict Whitehead descent of either
  relator stalls above length 1);
* 88 have a relator of the conjugation shape `g^a h^p g^-a h^q` (56 of those are
  `x^2 y^-2 x^-2 y`, i.e. `x^-2 y x^2 = y^2`, where the stable letter is a SQUARE and
  the census tables, keyed on `b^-1 a^m b a^-(m+1)`, do not fire);
* the other 639 are generic pairs with 4–12 syllables per relator and neither
  structure; plain length-first greedy solves 333 of the 727 within 10,000 nodes
  (101 within 1,000), so a third of the leftovers are ordering failures, not
  hardness;
* 9 rows resist every arm at 10,000,000 nodes from the Aut-minimal spelling
  (`ac19_16286, 27254, 28131, 44381, 50841, 51034, 59576, 65753, 7284`), yet every
  one of their pre-minimisation originals solves in 190–10,229 nodes: the
  Aut-minimal spelling sits at the bottom of a length well and the exit passes over
  relators 25–49 letters long (`ac19_orig_10m/WORKED_EXAMPLE.md` on the
  `claude/ac19-leftover-solver-notebook-6yan6d` branch).

## 4. What the new solver does differently

Same certificate contract, no hash map, no table.  The final procedure (`hfhybrid.solve`,
one tuned parameter) is:

1. **Whitehead descent** of the pair and of each relator (strict cyclic-length
   decrease under the four Nielsen maps); a relator that reaches one letter, or that
   contains one generator exactly once, finishes the pair by substitution (the
   primitive-donor theorem compiled into products: replace every occurrence of the
   letter in the companion, the companion becomes the other generator by
   abelianisation, delete the letters of the donor).
2. **Pinch cascade** for a relator parsed as `g^a h^p g^-a h^q` (any `a`, `p`, `q`;
   this generalises both the BS(1,2) rewrite of the MS-640 cascade and the
   consecutive-BS tables of the census policy): an exponent-level dry run decides
   applicability for free, each rule use is one product move.
3. **One best-first search, one budget, no closed-set hashing.**  Rank-two states
   are canonical under rotation, inversion, relator order and the eight signed
   generator permutations; their children are the seam-cancelling rotation products
   (the repository's compiled kernel) **and the four Nielsen maps** (recorded as
   automorphism steps).  Every popped rank-two state also offers `define` children
   (a new generator for a repeated cyclic digram), higher-rank states are expanded
   with capped products, `define`, `eliminate` and Nielsen transvections, and a child
   that returns to rank two re-enters the rank-two path.  Two frontiers: the rank-two
   one ordered by total length, the higher-rank one by total length plus five letters
   per generator above two; the higher-rank frontier is served only while its pops
   are at most half the rank-two pops (plus twenty), its states waiting otherwise.
   The closed sets are block-sorted arrays searched by bisection, tested when a state
   is popped.  Gates 1-2 are tried on every generated rank-two child.
4. One unit per popped state, per accepted map, per image evaluation and per
   substitution move; nothing else is charged.

Why it works where the census policy stalled: the Nielsen edges let the search leave
the Aut-minimal spelling, which sits at the bottom of a length well; seven of the nine
rows that resisted 10,000,000 fixed-basis nodes solve in at most 318 units once basis
changes are search edges.  The define/eliminate moves supply the last few rows, whose
rank-two certificates need 1,100 to 10,000 units: in rank three or four they are
reached in a few hundred.  The results are in `RESULTS.md`.
