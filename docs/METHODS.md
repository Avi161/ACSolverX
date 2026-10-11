# Methods

Plain-language definitions of what the code does and what its numbers mean. Worked examples were run against the source
files named in [PROVENANCE.md](PROVENANCE.md) and against `acx`. Results are in [RESULTS.md](RESULTS.md); the module map
and exact interfaces in [ARCHITECTURE.md](ARCHITECTURE.md).

## 1. Presentations and words

A balanced presentation is `<x, y | r1, r2>`: two generators, two relators, each relator a word that the presentation
sets equal to the identity. Words are written with lowercase for a generator and uppercase for its inverse
(`xxxYYYY` is `x^3 y^-4`) or as signed integers (`x = 1, y = 2, x^-1 = -1`). A relator is read as a *cyclic* word:
rotating it, or inverting it, gives the same relation. The target is the trivial presentation `<x, y | x, y>`: both
relators of length 1, on different generators.

A **state** is a pair of relators after free reduction (cancel adjacent inverse letters) and cyclic reduction (cancel
across the wrap-around), stored in a canonical form: each relator is the least rotation among the rotations of the word
and of its inverse, and the pair is ordered. Two presentations that differ only by rotating, inverting or swapping
relators are therefore one state. Renaming generators is *not* part of the state; it is a separate symmetry (section 7).

## 2. AC moves

The Andrews-Curtis conjecture asks whether every balanced presentation of the trivial group reaches the trivial
presentation by these moves:

- **AC1** replace a relator by its inverse.
- **AC2** replace `r_i` by `r_i r_j`, for `i` different from `j`.
- **AC3** replace `r_i` by a conjugate `w r_i w^-1`.

The elementary decoder uses a finer set: invert a relator, swap the two, conjugate by a single letter, and multiply one
relator into the other. Any conjugation by a word is a run of single-letter conjugations.

**Stable AC** adds two moves: **AC4** adds a generator `z` and the relator `z`, giving `<x, y, z | r1, r2, z>`; **AC5**
is its inverse (remove a generator together with a relator equal to it, when that generator occurs nowhere else). A
presentation is *stably AC-trivial* if AC1 to AC5 reach the trivial presentation. AC-trivial implies stably AC-trivial;
whether the converse holds is open, and AK(3) is the standard test case.

**Invariant.** Let `M` be the matrix of exponent sums (`M[i][g]` = net count of generator `g` in relator `i`). Every move
above multiplies `M` by an elementary integer matrix, so `|det M|` is unchanged, and the trivial presentation has
`|det| = 1`. A search that reaches a state with a different `|det|` has an unsound move, and every verifier here checks
it independently of the solver.

## 3. Substitution moves (Definition 2.1)

A substitution move (S-move) is a composite of AC moves that the search can take in one step. It is named by four
numbers `(i, j, k1, k2)`:

```
r_i  <-  rot_k1(r_i) . rot_k2(r_other ^ j)         (j = +1 or -1; "other" is the relator that is not r_i)
```

where `rot_k` is cyclic rotation by `k` letters, moving the last `k` letters to the front (`np.roll`). The target
`r_i` is never inverted; only the other relator may be.
A move is **emitted only if its seam cancels**: the last letter of `rot_k1(r_i)` is the inverse of the first letter of
`rot_k2(r_other^j)`. The product is then free- and cyclic-reduced (more letters can cancel beyond the seam) and the new
state is canonicalised.

Worked example, on AK(3) = `<x, y | xxxYYYY, xyxYXY>`. Take target `r1`, other `r2`, `j = +1`, `k1 = 0`, `k2 = 5`:

```
rot_0(r1)       = xxxYYYY
rot_5(r2)       = yxYXYx            (xyxYXY rotated by 5)
seam            : Y | y  -> cancels
raw product     = xxxYYYY yxYXYx    (13 letters)
after reduction = xxxYYYxYXYx       (11 letters)
```

The new state is `(xxxYYYxYXYx, xyxYXY)`, total length 17. AK(3) has 42 such legal moves from its start (38 distinct
child states after reduction and canonicalisation); both counts and the product above were checked against `main`'s
`get_neighbors_with_moves_nj` and `replay_move_nj`.

**Why it is an AC move.** A rotation of a cyclic word is a conjugate, `rot_k(r) = u^-1 r u`. So the S-move is
`(u^-1 r_i u)(p^-1 r_j^j p)`, which equals `u^-1 [ r_i . (c^-1 r_j^j c) ] u` with `c = p u^-1`; the outer conjugation is
absorbed by the canonical form. Every S-move is therefore "multiply `r_i` by a conjugate of the other relator or its
inverse", and it expands to `|c|` single-letter conjugations of the other relator, one multiplication, and the undoing
conjugations. The seam-cancel rule is a pruning for speed: it keeps only moves in which at least one letter pair
cancels at the seam, so the product is shorter than the two lengths added, and it is why a decoded path (section 9) may
use moves the search never emitted.

## 4. The relator cap

A child state is kept only if **both** relators, after reduction, have length at most the cap. The cap is a config
value (`SearchConfig.cap`, default 24; `cap = "none"` is uncapped at a speed cost), never hard-coded, and every rejected
move is counted in `stats["cap_rejected"]`, so it is never silent. The cap is a limit on the
*search graph*, not on a path: the same row at cap 24 and cap 48 is a different search. Conventions in the results:
24 for the MS640 baseline, 48 for AC19 and AC1M rungs, 64 for the largest budgets, and `max(24, longest + 16)` for
change-of-variables starts (a relator pinned exactly at the cap can never lengthen over the hump, so a transformed run
needs slack). The numbers 24 and 48 in a results table are caps, not move counts.

Every other cap reads the same way (`acx.core.config.parse_cap`: a positive int or `"none"`; `0` and booleans are
errors): the hybrid's `r2_cap` (default `"parent"`, the source's rule, which reproduces its published counts) and
`dyn_cap` (default 8), CoV's `max_len` and `cap_headroom`, and the RL beam's `cap` (at most 24, the policy's input
width). `run.py` rejects a section the method does not read, so a cap can never be set and silently ignored.

## 5. Greedy best-first search

```
heap <- { (priority(start), depth 0, key(start)) }
while heap is not empty and pops < budget:
    pop the smallest entry; pops += 1
    if both relators have length 1: solved
    for each legal S-move: reduce the new relator; skip if over the cap;
        canonicalise; skip if the state has been seen; else record (parent, move) and push at depth + 1
```

- The heap entry is `(priority, depth, key)`. The key is the state's packed string in a fixed symbol order
  (`X < Y < x < y`), so the three fields form a strict total order and the pop sequence does not depend on the heap
  implementation. The canonical form itself uses a different order (`Y < y < X < x`); the two orders must not be mixed.
- A state's depth and parent are those of its **first** discoverer. There is no decrease-key, so a state's priority
  must be a pure function of the state (never of its depth or parent), or pop order would depend on discovery order.
- **Budget** counts pops, and the solving pop counts. A search at budget B is the first B pops of a longer one.
- The **path** is the chain of parents from the solved state back to the start, so path length is the discovery depth
  of the solution. It is not a shortest path.

## 6. Priorities

Only two priorities ship; lower pops first.

- **LENGTH**: `L`, the total length of the two relators. This is the baseline, and the search with it is the "slow
  baseline" of the results.
- **S20_MK2**: `L + 20 S + 2 MK`, a float.

Features (all read the relators as rings):

- **Block**: a maximal cyclic run of one *generator*, where `x` and `X` are the same generator. A run that wraps past
  the seam is one block.
- **Knots** of a relator: 0 if it is a pure power (one generator absent), otherwise `max(#x-blocks, #y-blocks)`.
  **MK** is the larger knot count of the two relators.
- **S**: take the mean length of the `x`-blocks and of the `y`-blocks, each pooled over both relators; `S` is the smaller
  of the two means (or the one nonzero mean if a generator is absent).

Worked example, AK(3): `xxxYYYY` has one `x`-block (3) and one `y`-block (4); `xyxYXY` has three `x`-blocks and three
`y`-blocks, all of length 1. Pooled, the `x`-mean is 6/4 = 1.5 and the `y`-mean 7/4 = 1.75, so `S = 1.5`. Knots are 1 and
3, so `MK = 3`. `L = 13`. Priority = 13 + 20 x 1.5 + 2 x 3 = **49**.

Because a lower score pops first, the `+20 S` term prefers states in which the thinner generator occurs in *short* runs
(finely interleaved) and `+2 MK` prefers states whose worse relator is less tangled. (One source document states the
sign of `S` the other way; the formula and the code are as written here.)

**Two invariants** are tested: with LENGTH the engine reproduces the baseline pop for pop (a control that merely scores
the same is not the same search), and the priority is a pure function of the state. A vector `RECOMMENDED` (five
features) was withdrawn as overfit and is not shipped.

## 7. Backends: spec and fast, and the parity contract

Both backends run the search of section 5 (`acx.search.search(pres, cfg)`); the priority and the config are data.

- **spec** (`acx.search.spec`) is pure Python: a heap and a dict, one move generator, written to be read. It is the
  reference and the slow baseline.
- **fast** (`acx.search.fast`) is numba: states are rows of Booth symbols (one byte each; integer order is the Booth
  order and `b ^ 1` is the inverse) in a flat arena with an int32 heap and an FNV-1a dedup table; a path is stored as
  `(parent, move)`. The expansion kernel (from `hexpand`) skips a child that is a cyclic *cut shift* of the previous
  child of the same block (the raw words are conjugate, so they reduce to the same cyclic word) and counts every
  rejected move, including a whole block whose untouched relator is over the cap. Canonicalisation is a general
  two-pointer least-rotation scan (the source's 2-bit packing is not ported; it worked at two generators only), so the
  kernels run at any number of generators and relators.

**The contract** is step for step, not "same answer": for the same start, priority, cap and budget, `fast` pops the same
states in the same order. `tests/test_fast.py` compares `solved`, `pops`, the path, the end state, the full popped-state
trace and the statistics `discovered`, `cap_rejected`, `min_total`, `max_total`, `max_total_expanded`, `max_expanded` on
36 MS640 rows at budget 10,000 under both priorities (4 costlier rows and a 40-row sweep of MS640 in the `slow` set), at caps 12, 16, 24 and `None`,
with `cyclic=False`, at three generators, and from a start over the cap. `tests/test_spec.py` pins `spec` to main's
golden file and to budget-prefix invariance. On all 640 MS640 rows `fast` reproduces the original code's per-row pops and
path lengths (RESULTS.md section 0).

The kernels are a library (`acx.search.fast.kernels`: `encode`, `expand`, `score`, `children`): the hybrid, CoV and
n-generator searches run on them.

## 8. Automorphisms: Whitehead, canonical forms and transport

`Aut(F2)` is the group of automorphisms of the free group on `x, y`. Two presentations related by an automorphism are
the same problem in different coordinates, and AC-triviality is constant on an orbit.

- **Whitehead canonical form.** There are 20 Whitehead automorphisms of `F2`: 8 of the first kind (signed permutations of
  the generators) and 12 of the second kind (such as `x -> xy`). Peak reduction applies second-kind maps while any
  strictly lowers the total cyclic length, reaching the orbit's minimal total length `mu`. A breadth-first walk of the
  minimal level set then takes its lexicographic minimum, a *complete* invariant of the orbit. `aut_canon(P)` returns
  `(total, rep, phi)` with `canon(phi(P)) == rep`, so the witnessing automorphism ships its own proof. A numba twin
  (`acx.aut.fast`, from `autcanon_fast`, reached through `orbit_key(P, "fast")`) reproduces the same representatives
  (parity-tested on 267 presentations in the default tests and 2,307 in the `slow` set; about 6x faster here, 15x reported at the
  source). It returns no witness, so only the pure form drives transport.
- **Relabeling.** The 8 signed permutations of `{x, y}` are renamings, a coarser (still exact) key than the Aut orbit.
- **Equivariance.** If `phi` is an automorphism, applying it to every word of an AC move gives the same move on the
  images: `phi(r_i . c^-1 r_j^s c) = phi(r_i) . phi(c)^-1 phi(r_j)^s phi(c)`. The move type, target and sign are
  unchanged and the conjugator `c` becomes `phi(c)`. The engine's `(k1, k2)` rotation offsets do *not* transport, which
  is why the decoder first converts a move to its conjugator word.
- **Certificate transport** (`acx.aut.transport`). A path solving `phi(P)` (for example the Aut-minimal representative)
  is carried to `P` move by move with `psi = phi^-1` (an S-move `r_i . c^-1 r_j^s c` becomes the same move with
  `c -> psi(c)`); the path then ends at the basis `(psi(x), psi(y))`, and precomposing with the Whitehead factors of
  `phi`, last first, is a run of Nielsen moves back to `(x, y)`. Nothing searches. The output is elementary moves on
  `P`'s own words and is replayed there before it is returned. This is how the `aut` method and the CoV images in the
  row's orbit become **aut-assisted** `ac_path`s. A solve whose searched start is the row's own canonical form (a row
  that is already its Aut-minimal form, or a CoV image equal to the row) is a plain `ac_path`, not aut-assisted.

## 9. Decoder and path-length units

**Elementary decoder** (`acx.verify.decode`). An S-move path becomes the generator-level stream (invert `I`, swap `S`,
conjugate by a letter `C`, multiply `M`; stabilise `Z` and destabilise `D` pass through): rotate the relators by
conjugations, multiply, then restore the exact canonical form (strip the cyclic tail, invert, rotate, swap). Both
conjugator choices of each side are tried and the shortest expansion kept (6,302 moves on 60 test paths for the source's
single conjugated-multiply plan, 1,727 here). The output replays from the raw row with `normalize=False`, with no
implicit canonicalisation, and performs no search; it costs 6 to 10 elementary moves per S-move on MS640.
**Aut-assisted paths** are an `ac_path` only after transport (section 8) writes them out on the row.

**Units.** Do not compare numbers across these.

| unit | what it counts | where |
|---|---|---|
| node / pop | heap pops of the search | every search budget |
| S-move | one substitution move (a conjugated multiplication) | `path_length` of a search |
| elementary move | invert / swap / conjugate-by-letter / multiply | decoder output (a single S-move costs about `2|c| + 1`) |
| work unit | pops, accepted automorphisms, image evaluations and substitution moves, one each | hybrid solver |
| `acmoves` | multiplication operations only (conjugation and inversion free) | the source's hybrid cost tables |
| transformed-coordinate length | S-moves on the *CoV-transformed* pair | change-of-variables results |

`run.py` reports every solve in both path units: `sub_moves` (S-moves of the search; for the hybrid, the S-move steps of
its certificate) and `elem_moves` (the replayed elementary path on the row). A CoV `stable_cert` has no elementary path
on the row (`elem_moves` is empty): its transform is a Lemma 11 chain, not AC moves.

## 10. Hybrid solver

A deterministic solver for balanced two-generator presentations that adds dynamic-rank moves to the fast engine. It
keeps the repository's rank-two machinery and lets the number of generators change during the search.

1. **Rank-two states** are packed keys expanded by the `hexpand` kernel: seam-cancelling products and the four Nielsen
   maps (`x -> xy`, `x -> xY`, `y -> yx`, `y -> yX`), canonical under the eight signed permutations. Finishing gates run
   at pop time: *relator descent* (shorten one relator by Nielsen maps while carrying the other; a relator that reaches
   length 1 is a primitive donor whose letter is deleted from the companion), and a *pinch cascade* (a relator of the
   shape `g^a h^p g^-a h^q` pinches the companion's `g` syllables when the enclosed exponent divides).
2. **`define`**: pick a cyclic digram `ab` that occurs at least twice across the relators, add a generator `h` with
   defining relator `h^-1 a b`, and replace occurrences of `ab` by `h` (and `BA` by `H`). The rank goes from n to n+1.
3. **`eliminate`**: a generator `g` that occurs exactly once in a relator `R = g^e u` is solved for (`g = u^-1` or `u`),
   substituted into the other relators, and the relator is deleted. The rank goes from n to n-1; reaching rank 0 is
   solved.

`define` and `eliminate` are stable-AC composites (Lemma 11 of arXiv:2408.15332). `acx.hybrid.certify` writes every
certificate out as elementary moves on the row itself, with AC4/AC5 for `define`/`eliminate`, and replays it. A
certificate without them is an `ac_path`, counted as aut-assisted when it has any automorphism step, a Nielsen map or
a signed permutation (the permutation canonical form of a popped state is such a step, so a certificate whose only
automorphisms are relabellings is aut-assisted too); one with them is a `stable_cert`. Frontier: one heap ordered by total
length plus a penalty per generator above two (default 5); the higher-rank frontier is served only while its pops stay
within `dyn_ratio` (default 0.5) of the rank-two pops plus 20. The higher-rank moves have three more settings, all at
the source's values: `dyn_cap` 8 (longest relator a product or elimination may create; `"none"` uncaps it), `slack` 8
(total-length ceiling above the search root) and `min_uses` 2 (a defined digram must occur this often).
Cost is counted in work units. The rank-two cap is `r2_cap` (default `"parent"`: a child relator may not exceed the
parent's total length, the source's rule; an int or `None` for uncapped), and rejections are counted. The source called
the solver "hash-free"; it keeps a visited set per frontier, so the name is dropped.

## 11. Change of variables and stable AC

A **change of variables** (CoV) re-expresses a presentation in a different generating pair before the ordinary search,
and the search then runs on the new pair with the unchanged greedy. Steps, for a chosen word `w(x, y)`:

1. **Stabilise by a definition.** Add `z` and the relator `Z w` (that is, `z = w`): `<x, y, z | r1, r2, Z w>`.
2. **Substitute.** Wherever `w` or `W` occurs in `r1` and `r2` (cyclic windows, so across the seam too; non-overlapping,
   left to right, then at most one wrap-around match), replace it by `z` or `Z`. Free-reduce.
3. **Isolate.** Find a relator in which the chosen generator (`x` or `y`) occurs exactly once (counted on the cyclically
   reduced word) and in which `z` also occurs. Rotate to `x^e s` and solve: `x = s^-1` or `s`.
4. **Eliminate.** Substitute that expression for the generator in the other two relators, drop the isolating relator
   and the generator. A relator that empties, or exceeds 239 letters, discards the branch.
5. **Relabel** the surviving `(y, z)` or `(x, z)` back to `(x, y)`.

Worked example, AK(3), `w = xy`, eliminate `x`:

```
start               r1 = xxxYYYY      r2 = xyxYXY        defining relator Z xy
substitute xy -> z  r1' = xxxYYYY     r2' = z x Z Y      (xy at the start of r2, YX = (xy)^-1 inside it)
isolate x in r2'    rotate to  x Z Y z   =>   x = (Z Y z)^-1 = Z y z
substitute x := Z y z in r1' and in Z x y:
                    r1'' = Z y y y z Y Y Y Y            defining'' = Z Z y z y
relabel y->x, z->y  new pair  (Y x x x y X X X X ,  Y Y x y x)    total 14, run at cap max(24, 9 + 16) = 25
```

The new pair is what the greedy searches. The outcome of that search says nothing yet about the original; see below.

**What a CoV solve proves.** Steps 1 to 5 are a stabilisation followed by AC moves and a destabilisation, so a solved
transformed pair shows the *original* is **stably** AC-trivial. The transformed path is a path on a *different*
presentation: it is not an AC path on the original and its length is not a length for it. The results therefore keep two
kinds apart:

- **`stable_cert`**: a replayed CoV transform plus a replayed AC path on the transformed pair. Proves stable
  AC-triviality.
- **`ac_path`**: a replayed AC path on the presentation as given (possibly after transport or decoding).

An image in the row's own Aut(F2) orbit (every image with one substitution, and most others) is the exception:
`acx.cov` transports its solve back to the row (section 8), so it counts as an aut-assisted `ac_path`.

A comparison between a CoV arm and an untransformed arm is a cost comparison, not a comparison of two paths of the same
object, and it must hold the cap fixed (CoV rows run at a larger cap).

**The default policy** (`acx.cov.run_cov`) is one-shot: the row itself first (`control`), then the images in enumeration
order, each searched with at most `search.budget` pops and the images at cap `max(cap, longest written relator + 16)`,
until `total_budget` pops are spent or one solves. There is no ranking, no abel top-3, no selection key and no beam or
ladder (RESULTS.md, Tried). An oracle (the best candidate) is a lower bound, not a procedure; the deployable cost includes
the failed candidates (RESULTS.md section 5).

### The z-family name `subnc2pxysb`, letter by letter

The tag names the *rule that decides which `w` and which branches are tried*. In the source it was part of a run's
identity (it is in the result file name), so a different rule could never resume into another's file; `acx` ships this
one family only (`acx.cov.FAMILY_TAG`). From `cov.py`:

| letters | meaning |
|---|---|
| `sub` | `w` is drawn from the presentation's own **sub**words: every cyclic window of a (cyclically reduced) relator of length 2 or more, the seam included, with `w` and `W` counted once |
| `nc2` | the **n**o-**c**ollapse gate: a `w` whose substitution brings *any* relator it fires on to length 2 or less is dropped (`MIN_TRANSFORMED = 3`), even when `w` was read off the other relator. This is the only length rule. The earlier `sub<K>` tags bounded `|w|` by a global K instead |
| `p` | **p**ure powers (`xx`, `yyy`, ...) are included; the earlier family had mixed-generator words only |
| `xy` | both isolation targets are tried for each `w`: eliminate `x` and eliminate `y` |
| `s` | cyclic-**s**eam matches count in the substitution; the earlier family missed an occurrence that straddles the wrap-around |
| `b` | every isolating **b**ranch is its own row: when both `r1'` and `r2'` isolate the generator they are two different coordinate changes, kept apart by `iso_index` (the earlier files kept only the first) |

Outputs that land on the same pair are searched once. Two other families exist. `zf3` (`NAIVE_Z_FAMILY`) is every
reduced word of length 2 to 4, tried in order with the first valid transform winning; it does not depend on the
presentation. `suballpxyb8` (the exhaustive sweep) restricts `w` to proper cyclic subwords (`2 <= |w| <= |r| - 1`),
substitutes every set of non-overlapping occurrences (partial substitution included), drops the no-collapse gate, and
quotients the outputs by relator order, rotation, inversion and the 8 signed permutations; on MS640 at budget 100 it
solves nothing the default family does not (RESULTS.md section 5).

## 12. n-generator search and short-relator forms

**n-generator search** (`acx.ngen`; the search is `acx.search` itself, on either backend). The S-move generalises to `n` relators with a source index: `r_i <- rot_k1(r_i) . rot_k2(r_j ^ s)`
for `j` different from `i`, enumerated in the order `i, j, s, k1, k2` (at two relators this collapses to the baseline's
order, which the depth tie-break depends on). The solver runs on `n` generators and `n` or more relators, with goal
"every relator a single letter and every generator present". `spec` and `fast` are trace-equal on triangle roots of
rank 4 to 6 (`tests/test_ngen.py`; the MS640 roots run from rank 4 to 11). Only the LENGTH priority exists past two generators.

**Stable moves in a path.** `acx` paths use only AC4 (`{"op": "stabilize"}`: add generator `n+1` and relator `n+1`)
and AC5 (`{"op": "destabilize"}`); a definition `z = w` is AC4 followed by AC moves, so every stable certificate replays
under the same `acx.verify.replay`.

**Length-3 transforms.** Two mechanisms put relators of length at most 3 into an n-generator state:

- `define` (section 10) adds `h` with the length-3 relator `h^-1 a b` for a repeated digram.
- `SPLIT` (not shipped) introduces a fresh generator with a length-3 definition `t u v` and reuses it in further positions. With a
  length-2 definition the move is provably inert (the old link graph is a minor of the new one, so no invariant can
  fall); with a length-3 definition the new edge carries three or more germs and the space genuinely changes. The target
  state, a *cubic triangular form* (every relator of length 3, every generator occurring 3 times), exists from rank 4
  but is impossible at rank 2 or 3 when all relators are cyclically reduced.

**The transform to relators of length at most 3** (`acx.ngen.sac.triangulate`, then `acx.ngen.lift`) is `triangulate` in
`claude/vigilant-babbage-nnbuj0:research/ac_dynamic_rank_20260913/dynrank.py` (a separate implementation is
`research/u124_rank_3h_20260912/high_rank_triangles.py` on the same branch). While some relator is longer than 3 it
applies `define` to a cyclic digram of a long relator, the one with the most occurrences over all relators (ties: more
occurrences in the long relators, then the smallest), so the *triangle
excess* `sum(max(0, |r| - 3))` strictly decreases and the loop ends; it returns the all-triangle root and the `define`
steps as certificate steps. `acx.ngen` searches the root at fixed rank and lifts a solve to an elementary stable AC path on
the input (AC4 per definition, the automorphism `h -> d^-1 h`, the transported S-moves, AC5 at the end), a `stable_cert`
replayed on the row. The port equals `dynrank.triangulate` digram for digram on all 142,365 rows of MS640, AC19 and 1190MS. It is a stable-AC transform
(every step is a Tietze extension followed by AC moves). Measured use is in RESULTS.md section 7: as a one-shot
preprocessing step it hurts, and the gain comes from `define`/`eliminate` interleaved with the search. At an
all-triangle root a product of two length-3 words has even length, so a unit cannot appear in one move.

## 13. Verification

A result counts only after it replays on the presentation it claims to solve, through code that shares nothing with the
solver: every move legal, `|det M| = 1` at the start and after every move, no S-move child over the cap, and a trivial
end (`acx.verify.replay`). An aut-assisted solve counts after transport to the original row; a `stable_cert` replays
its search leg with the replayer and its transform in the CoV code (`acx.cov.check_cert`), or its stabilised elementary
path (hybrid, n-generator) directly, and is reported separately from an `ac_path`. `run.py` writes a record only after
this replay, and the summary keeps `ac_path`, `aut_assisted` and `stable_cert` apart.
