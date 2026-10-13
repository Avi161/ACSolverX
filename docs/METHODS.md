# Methods

Plain-language definitions of what the code does and what its numbers mean; the worked examples were run against `acx`.
Results are in [RESULTS.md](RESULTS.md), the module map and exact interfaces in [ARCHITECTURE.md](ARCHITECTURE.md), the
relator cap and its counters in [CAP.md](CAP.md), the rank-n brute force in [RANK3.md](RANK3.md), where each part came
from in [PROVENANCE.md](PROVENANCE.md).

Every method is run by `python run.py --config configs/<name>.toml` and has its own config sections ([USAGE.md](USAGE.md)).

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
child states after reduction and canonicalisation); `tests/test_core.py` and `tests/test_spec.py` pin the move
enumeration and the child states.

**Why it is an AC move.** A rotation of a cyclic word is a conjugate, `rot_k(r) = u^-1 r u`. So the S-move is
`(u^-1 r_i u)(p^-1 r_j^j p)`, which equals `u^-1 [ r_i . (c^-1 r_j^j c) ] u` with `c = p u^-1`; the outer conjugation is
absorbed by the canonical form. Every S-move is therefore "multiply `r_i` by a conjugate of the other relator or its
inverse", and it expands to `|c|` single-letter conjugations of the other relator, one multiplication, and the undoing
conjugations. The seam-cancel rule is a pruning for speed: it keeps only moves in which at least one letter pair
cancels at the seam, so the product is shorter than the two lengths added, and it is why a decoded path (section 9) may
use moves the search never emitted.

## 4. The relator cap

A child state is kept only if **both** relators, after reduction, have length at most the cap. The cap is a config
value (`SearchConfig.cap`, default 24; `cap = "none"` is uncapped, at a speed cost), never hard-coded. The cap is a
limit on the *search graph*, not on a path: the same row at cap 24 and cap 48 is a different search. Conventions in the
results: 24 for the MS640 baseline, 48 for AC19 and AC1M rungs, 64 for the largest budgets, and
`max(24, longest + 16)` for change-of-variables starts (a relator pinned exactly at the cap can never lengthen over the
hump, so a transformed run needs slack). The numbers 24 and 48 in a results table are caps, not move counts.

The cap never decides silently what the search pops. Every search counts the children the cap dropped and whether a
dropped child would have been popped had the cap been larger, in six fields of every record (`cap`, `cap_dropped`,
`cap_dropped_min_total`, `cap_would_pop`, `cap_first_bind`, `cap_needed`) and a `caps` block of `summary.json`.
`cap_would_pop == 0` means the same run at any larger cap. The counting is one module that knows no heuristic
([CAP.md](CAP.md)).

Every other cap reads the same way (`acx.core.config.parse_cap`: a positive int or `"none"`; `0` and booleans are
errors): the hybrid's `r2_cap` (default `"parent"`), `dyn_cap` (default 8) and `slack` (default 8, `0` allowed), CoV's `max_len` and
`cap_headroom`, and the RL beam's `cap` (at most 24, the policy's input width). `run.py` rejects a section the method
does not read, so a cap can never be set and silently ignored.

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

Config: `[search]` (`priority`, `cap`, `budget`, `backend`, `cyclic`), as in `configs/greedy_fast.toml`,
`s20_mk2_fast.toml` and `baseline_spec.toml`.

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
(finely interleaved) and `+2 MK` prefers states whose worse relator is less tangled.

**Two invariants** are tested: with LENGTH the engine reproduces the baseline pop for pop (a control that merely scores
the same is not the same search), and the priority is a pure function of the state. No other priority ships; the
counters of section 4 work with any future one, because they only compare the scores a search passes in.

## 7. Backends: spec and fast, and the parity contract

Both backends run the search of section 5 (`acx.search.search(pres, cfg)`); the priority and the config are data.

- **spec** (`acx.search.spec`) is pure Python: a heap and a dict, one move generator, written to be read. It is the
  reference and the slow baseline.
- **fast** (`acx.search.fast`) is numba: states are rows of Booth symbols (one byte each; integer order is the Booth
  order and `b ^ 1` is the inverse) in a flat arena with an int32 heap and an FNV-1a dedup table; a path is stored as
  `(parent, move)`. The expansion kernel skips a child that is a cyclic *cut shift* of the previous child of the same
  block (the raw words are conjugate, so they reduce to the same cyclic word) and still counts every dropped move,
  including a whole block whose untouched relator is over the cap. Canonicalisation is a general two-pointer
  least-rotation scan, so the kernels run at any number of generators and relators.

**The contract** is step for step, not "same answer": for the same start, priority, cap and budget, `fast` pops the same
states in the same order. `tests/test_fast.py` compares `solved`, `pops`, the path, the end state, the full popped-state
trace and the statistics `discovered`, the six cap-counter fields, `min_total`, `max_total`, `max_total_expanded`,
`max_expanded` on MS640 rows at budget 10,000 under both priorities (a larger sweep is in the `slow` set), at several
caps and `None`, with `cyclic=False`, at three generators, and from a start over the cap. `tests/test_spec.py` pins
`spec` to the baseline's golden file and to budget-prefix invariance. On all 640 MS640 rows `fast` reproduces the
baseline's per-row pops and path lengths (RESULTS.md section 0).

The kernels are a library (`acx.search.fast.kernels`: `encode`, `expand`, `score`, `children`): the hybrid and the
Aut-minimal form run on them.

## 8. Automorphisms: Whitehead, canonical forms and transport

`Aut(F2)` is the group of automorphisms of the free group on `x, y`. Two presentations related by an automorphism are
the same problem in different coordinates, and AC-triviality is constant on an orbit.

- **Whitehead canonical form.** There are 20 Whitehead automorphisms of `F2`: 8 of the first kind (signed permutations of
  the generators) and 12 of the second kind (such as `x -> xy`). Peak reduction applies second-kind maps while any
  strictly lowers the total cyclic length, reaching the orbit's minimal total length `mu`. A breadth-first walk of the
  minimal level set then takes its lexicographic minimum, a *complete* invariant of the orbit. `aut_canon(P)` returns
  `(total, rep, phi)` with `canon(phi(P)) == rep`, so the witnessing automorphism ships its own proof. A numba twin
  (`acx.aut.fast`, reached through `orbit_key(P, "fast")`) reproduces the same representatives (parity-tested against
  the pure form in `tests/test_aut.py`, a larger sample in the `slow` set). It returns no witness, so only the pure
  form drives transport.
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

The `aut` method (`configs/aut.toml`, `[search]`): search the Aut-minimal representative of the row with the greedy
search, then transport the path back; the record keeps both the search's S-move count and the elementary length on the
row. If the row is its own representative, the shorter of the transport and the decoded S-move path is kept.

## 9. Decoder and path-length units

**Elementary decoder** (`acx.verify.decode`). An S-move path becomes the generator-level stream (invert `I`, swap `S`,
conjugate by a letter `C`, multiply `M`; stabilise `Z` and destabilise `D` pass through): rotate the relators by
conjugations, multiply, then restore the exact canonical form (strip the cyclic tail, invert, rotate, swap). Both
conjugator choices of each side are tried and the shortest expansion kept. The output replays from the raw row with `normalize=False`, with no
implicit canonicalisation, and performs no search; it costs 6 to 10 elementary moves per S-move on MS640.
**Aut-assisted paths** are an `ac_path` only after transport (section 8) writes them out on the row.

**Units.** Do not compare numbers across these.

| unit | what it counts | where |
|---|---|---|
| node / pop | heap pops of the search | every search budget |
| S-move | one substitution move (a conjugated multiplication) | `path_length` of a search |
| elementary move | invert / swap / conjugate-by-letter / multiply | decoder output (a single S-move costs about `2|c| + 1`) |
| work unit | pops of the search, and in the cascade and gates Nielsen images evaluated, automorphisms accepted and S-moves applied, one each | hybrid solver |
| transformed-coordinate length | S-moves on the *CoV-transformed* pair | change-of-variables results |

`run.py` reports every solve in both path units: `sub_moves` (S-moves of the search; for the hybrid, the S-move steps of
its certificate) and `elem_moves` (the replayed elementary path on the row). A CoV `stable_cert` has no elementary path
on the row (`elem_moves` is null): its transform is a Lemma 11 chain, not AC moves.

## 10. Hybrid solver

A deterministic solver for balanced two-generator presentations that adds dynamic-rank moves to the fast engine: the
number of generators can change during the search. Config: `[hybrid]` (`configs/hybrid.toml`): `budget` (work units),
`penalty`, `dyn_ratio`, `dyn_cap`, `slack`, `min_uses`, `r2_cap`, `backend` (`fast` or `spec` for the rank-two
expansion). It takes balanced two-generator presentations; a start with `|det| != 1` (section 2) has no AC path and
returns unsolved at 0 units.

1. **Rank-two states** are expanded by the fast kernel: seam-cancelling products and the four Nielsen maps
   (`x -> xy`, `x -> xY`, `y -> yx`, `y -> yX`), canonical under the eight signed permutations. A cascade (Nielsen
   descent, primitive deletion, pinch cascade) runs first, and its finishing gates run at pop time: *relator descent*
   (shorten one relator by Nielsen maps while carrying the other; a relator that reaches length 1 is a primitive donor
   whose letter is deleted from the companion), and a *pinch cascade* (a relator of the shape `g^a h^p g^-a h^q` pinches
   the companion's `g` syllables when the enclosed exponent divides).
2. **`define`**: pick a cyclic digram `ab` that occurs at least twice across the relators, add a generator `h` with
   defining relator `h^-1 a b`, and replace occurrences of `ab` by `h` (and `BA` by `H`). The rank goes from n to n+1.
3. **`eliminate`**: a generator `g` that occurs exactly once in a relator `R = g^e u` is solved for (`g = u^-1` or `u`),
   substituted into the other relators, and the relator is deleted. The rank goes from n to n-1; reaching rank 0 is
   solved.

`define` and `eliminate` are stable-AC composites (Lemma 11 of arXiv:2408.15332). `acx.hybrid.certify` writes every
certificate out as elementary moves on the row itself, with AC4/AC5 for `define`/`eliminate`, and replays it. A
certificate without them is an `ac_path`, counted as aut-assisted when it has any automorphism step, a Nielsen map or
a signed permutation (the permutation canonical form of a popped state is such a step, so a certificate whose only
automorphisms are relabellings is aut-assisted too); one with them is a `stable_cert`.

Frontier: two heaps. The rank-two heap is ordered by total length, its states deduplicated up to a signed permutation of
the generators; the higher-rank heap by total length plus `penalty` (default 5) per generator above two, and it also
holds the deferred `define` children of rank-two states. A pop serves the higher-rank heap when its top is no worse and
its pops stay within `dyn_ratio` (default 0.5, a number >= 0) times the rank-two pops plus 20, else the rank-two heap.
A defined digram must occur `min_uses` (default 2) times. Cost is counted in work units: one per pop of either heap,
plus the cascade's and the gates' units (section 9).

**Three limits, three counters.** `r2_cap` (default `"parent"`: a child relator may not exceed the parent's total
length, which can never reject; an int or `"none"` otherwise), `dyn_cap` (default 8: the longest relator a higher-rank
product or elimination may create; `"none"` uncaps it) and `slack` (default 8: the total-length ceiling above the
search root; `"none"` lifts it). Each reports the six fields of section 4 under the prefixes `cap_`, `dyn_cap_` and
`slack_`, counting classes of dropped children and distinct canonical pairs rather than moves. The hybrid has two
queues, so its counts are first order: zero in all three means the same run at any larger limit, a non-zero count
says only that the run may change ([CAP.md](CAP.md)).

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

**The default policy** (`acx.cov.run_cov`; `[search]` and `[cov]` in `configs/cov.toml`, with `total_budget`, `control`,
`cap_headroom`, `max_len`, `until`, `family`) is one-shot: the row itself first (`control`), then the images in
enumeration order, each searched with at most `search.budget` pops and the images at cap
`max(cap, longest written relator + 16)`, until `total_budget` pops are spent or one solves. There is no ranking, no
abel top-3, no selection key and no beam or ladder (RESULTS.md, Tried). An oracle (the best candidate) is a lower bound,
not a procedure; the deployable cost includes the failed candidates (RESULTS.md section 5).

### The z-family name `subnc2pxysb`, letter by letter

The tag names the *rule that decides which `w` and which branches are tried*. It is the default of `[cov] family`
(the rules are in `acx/cov/family.py`, the word operations in `acx/cov/substitution.py`):

| letters | meaning |
|---|---|
| `sub` | `w` is drawn from the presentation's own **sub**words: every cyclic window of a (cyclically reduced) relator of length 2 or more, the seam included, with `w` and `W` counted once |
| `nc2` | the **n**o-**c**ollapse gate: a `w` whose substitution brings *any* relator it fires on to length 2 or less is dropped (`MIN_TRANSFORMED = 3`), even when `w` was read off the other relator. This is the only length rule. The earlier `sub<K>` tags bounded `|w|` by a global K instead |
| `p` | **p**ure powers (`xx`, `yyy`, ...) are included; the earlier family had mixed-generator words only |
| `xy` | both isolation targets are tried for each `w`: eliminate `x` and eliminate `y` |
| `s` | cyclic-**s**eam matches count in the substitution; the earlier family missed an occurrence that straddles the wrap-around |
| `b` | every isolating **b**ranch is its own row: when both `r1'` and `r2'` isolate the generator they are two different coordinate changes, kept apart by `iso_index` (the earlier files kept only the first) |

Outputs that land on the same pair are searched once. The default family reads the relators cyclically reduced and
substitutes in one pass over each relator in its written rotation: a relator padded with a cancelling conjugator
(`g r g^-1` that reduces back to `r`) gives the same images, but a rotation of `r` can give others.

`family = "suballpxyb8"` is the exhaustive family of the MS640 sweep (`cov/all-subsets-sweep`, stored in
[results/stable_ac/cov_all/](../results/stable_ac/cov_all/README.md)): `w` is any proper cyclic subword
(`2 <= |w| <= |r| - 1`, no `nc2` gate), **all** sets of non-overlapping occurrences in the cyclically reduced relators
are substituted (partial substitution included; the seam is an ordinary position), and one image is kept per class
under relator order, rotation, inversion and the **8** signed permutations, the row's own class left out
(`acx.cov.images.class_key`). It does not depend on how a relator is rotated. On MS640 it gives the sweep's 114,042
starts (the default family's images fall in 13,727 of those classes), and the best start of either family solves the
same presentations at 100, 1,000, 10,000 and 100,000 nodes (RESULTS.md section 5). Under the one-shot policy above its
order is worse: all patterns of the shortest `w` come first. `zf3` (every reduced word of length 2 to 4, first valid
transform wins) was tried on research branches and is not shipped.

**One image per class in the default family: measured, not applied.** Searching each `class_key` class of the default
family once, as `suballpxyb8` does, would solve bench60 40 and MS640 586 under the shipped policy, against 39 and 584.
The default family keeps its exact-pair dedup, so the published numbers stand.

## 12. n-generator search and short-relator forms

**n-generator search** (`acx.ngen`; the search is `acx.search` itself, on either backend). The S-move generalises to
`n` relators with a source index: `r_i <- rot_k1(r_i) . rot_k2(r_j ^ s)` for `j` different from `i`, enumerated in the
order `i, j, s, k1, k2` (at two relators this collapses to the baseline's order, which the depth tie-break depends on).
The solver runs on `n` generators and `n` or more relators, with goal "every relator a single letter and every
generator present". `spec` and `fast` are trace-equal on triangle roots of rank 4 to 6 (`tests/test_ngen.py`; the
MS640 roots run from rank 4 to 11). Only the LENGTH priority exists past two generators. Config (`configs/ngen_sac.toml`):
`[search]` and `[ngen]` (`sac`, default true; the runner always lifts a solve).

**Stable moves in a path.** `acx` paths use only AC4 (`{"op": "stabilize"}`: add generator `n+1` and relator `n+1`)
and AC5 (`{"op": "destabilize"}`); a definition `z = w` is AC4 followed by AC moves, so every stable certificate replays
under the same `acx.verify.replay`.

**The transform to relators of length at most 3** (`acx.ngen.sac.triangulate`, then `acx.ngen.lift`). While some
relator is longer than 3 it applies `define` (section 10) to a cyclic digram of a long relator, the one with the most
occurrences over all relators (ties: more occurrences in the long relators, then the smallest), so the *triangle
excess* `sum(max(0, |r| - 3))` strictly decreases and the loop ends; it returns the all-triangle root and the `define`
steps as certificate steps. `acx.ngen` searches the root at fixed rank and lifts a solve to an elementary stable AC
path on the input (AC4 per definition, the automorphism `h -> d^-1 h`, the transported S-moves, AC5 at the end), a
`stable_cert` replayed on the row. The transform matches the original `triangulate` digram for digram on all 142,365
rows of MS640, AC19 and 1190MS (`tests/test_ngen.py` pins a sample). It is a stable-AC transform (every step is a
Tietze extension followed by AC moves). Measured use is in RESULTS.md section 7: as a one-shot preprocessing step it
hurts, and the gain comes from `define`/`eliminate` interleaved with the search.

**Rank-n brute force** (`acx.ngen.sweep`, [RANK3.md](RANK3.md)). Add `extra` generators `z_i` with relators
`Z_i.w_i` for every freely reduced word `w_i` up to a length, search each stabilised start with `acx.search` under the
same cap and budget, and compare with the two-generator control. It measures how much a good stabilising word helps
greedy; its solves are reported as "solved from the stabilised start", not as certificates. Config: `[search]` and
`[rankn]` (`configs/rank{3,4,5}_bf.toml`, run with `run.py`).

## 13. Learned policy (RL, optional)

`acx.rl` is the paper's PPO policy (the step-1000 weights, `acx/rl/checkpoint/610model_1000.pt`, ported to PyTorch) used
as a beam search: each step scores every legal substitution move of every live state with the network, keeps the global
top `width` by cumulative log-probability, drops duplicate and already visited states, and stops when a state of two
length-1 relators appears or after `steps` steps. It needs `pip install -e .[rl]`. Config: `[rl]` in `configs/rl.toml`
(`width`, `steps`, `alpha`, `cap`); two generators only, relators of length at most 24 (the policy's input width), so a
longer row comes back unsolved with `skipped` set. `cost` is the number of states the network scored. The path is a
list of S-moves, replayed like any other. Training code is included (`acx.rl.env`, `acx.rl.ppo`).
PPO's reward normalizer is the JAX trainer's `NormalizeVecReward`, which trained the shipped weights, quirks kept: a
step's own `done` clears the return before that step's reward is added, so a terminal reward carries into the next
episode's return. Keep it so, or training no longer reproduces the checkpoint's.

## 14. Verification

Run `pytest` (the default selection, a few minutes) and `pytest -m ""` (adds the slow parity and census sets). Every
solved record with `path=true` is replayed before it is written; `path=false` records are unverified search counts.
To check a finished run again, replay each record on its
row: `replay(pres, decode_path(rec["path"]))` for a plain greedy `ac_path` (`acx.core.moves.decode_path`), and
`replay(pres, unpack(rec["elementary"]), normalize=False)` for any record that has `elementary` moves (aut-assisted,
hybrid, n-generator and CoV paths; `acx.verify.pack.unpack`), with `pres` from `acx.data.rows(benchmark)`.

A certified result counts only after it replays on the presentation it claims to solve. Replay is separate from the
optimized expansion kernels, but shares Python word operations and move definitions with the reference solver;
it is not an independent formal proof checker. It checks every move is legal, `|det M| = 1` at the start and after
every move, no S-move child over the configured cap, and a trivial
end (`acx.verify.replay`). An aut-assisted solve counts after transport to the original row; a `stable_cert` replays
its search leg with the replayer and its transform in the CoV code (`acx.cov.check_cert`), or its stabilised elementary
path (hybrid, n-generator) directly, and is reported separately from an `ac_path`. With `path=true`, `run.py` writes a
solved record only after this replay. Summaries keep `ac_path`, `aut_assisted` and `stable_cert` apart.
