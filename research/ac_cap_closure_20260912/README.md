# Cap-bounded Andrews–Curtis closure BFS — 2026-09-12

An exact, exhaustive breadth-first search of the Andrews–Curtis graph of rank-2
balanced presentations **restricted to a length cap**, together with a slow
reference implementation, an independent certificate replayer and a test suite
that pins the three against each other.

The point of the module is to produce two kinds of statement:

* **CLOSED at cap `c`** — the set of presentations reachable from the start
  without ever letting a relator exceed length `c` is finite and has been
  enumerated completely. If the trivial presentation is not in it, *no* AC
  sequence whose intermediate presentations all stay within the cap trivialises
  the start.
* **SOLVED at cap `c`** — a path to `{x, y}` inside the cap, emitted as a
  machine-checkable certificate and replayed by `verify_path.py`.

Headline run (this machine, 4 CPUs): **AK(3) = `(xxxYYYY, xyxYXY)` has a closed
component at every cap up to 16**, the cap-16 component having 2,333,976
states. So no AC trivialisation of AK(3) exists in which every intermediate
relator has length ≤ 16.

---

## 1. The model, exactly

### 1.1 States

`F2 = F(x, y)`; in ASCII a lowercase letter is a generator and the uppercase
letter its inverse, so `YXYxyx` is `y^-1 x^-1 y^-1 x y x`.

A **state** is an unordered pair `{r1, r2}` of **nonempty cyclically reduced
cyclic words**: each relator is taken up to cyclic rotation and up to
inversion, and the pair is unordered.

* *Rotation* is free because AC3 (conjugating a relator) is an AC move, and
  conjugating by a prefix is exactly a cyclic rotation, at no length cost.
* *Inversion* is free because AC1 (replacing `r` by `r^-1`) is an AC move.
* *Order* is free because relabelling which relator is which is an AC move.

**Canonical key of a relator**: the minimum, under the fixed letter order
`x < X < y < Y`, over the `n` rotations of the word and the `n` rotations of its
inverse. **Canonical key of a state**: the two relator keys sorted by
`(length, letters)`.

A relator is never allowed to be empty. (`{1, r}` has abelianised determinant
0, and the determinant is an AC invariant, so no presentation with
`det = ±1` — in particular no candidate AC counterexample and no presentation
of the trivial group — can ever reach such a state. Dropping them loses
nothing for the intended use and keeps "relator" synonymous with "nonempty
cyclically reduced word".)

### 1.2 The cap

The cap `c` bounds the length of **each** relator (i.e. the maximum relator
length) of **every** state on a path, the start included. Lengths are always
lengths of freely/cyclically reduced words: an unreduced concatenation formed
inside a single move is not a presentation and is not subject to the cap.

### 1.3 Moves

From a state with canonical relators `(r_0, r_1)`, for `i != j` in `{0, 1}`:

* a sign `e ∈ {+1, -1}`;
* a rotation `a` of `r_i` — `rot_a(w) = w[a:] + w[:a]`, `0 ≤ a < |r_i|`;
* a rotation `p` of `r_j^e`, `0 ≤ p < |r_j|`;
* a **connector** `w`: any freely reduced word (possibly empty) with

  ```
  |w| ≤ floor( (c - |r_i| - |r_j|) / 2 )
  ```

  (when that bound is negative, only `w = ε` is tried);

giving

```
R = cyclic_reduce( free_reduce( rot_a(r_i) · w · rot_p(r_j^e) · w^-1 ) ).
```

The move is **allowed iff `1 ≤ |R| ≤ c`**, and the new state is `{R, r_j}`.
Note the donor `r_j` is unchanged, so only one relator moves per step.

### 1.4 Why this is exactly "one AC2 move, with AC1/AC3 free"

**(⊆, the move set is not too big.)** Every move above is realised by
elementary AC moves that stay under the cap. (First replace the triple
`(a, p, w)` by its normal form under the cancellation rewrites of the next
paragraph — same `R`, connector no longer — so that no junction touching `w`
cancels; then:)

1. rotate `r_j` to `rot_p(r_j^e)` (AC1 + AC3 conjugations by single letters;
   every intermediate relator is again a rotation of `r_j^e`, so the length
   never changes);
2. conjugate it by `w` one letter at a time: the intermediate relators are
   `w_k · rot_p(r_j^e) · w_k^-1` for suffixes `w_k` of `w`, of length
   `|r_j| + 2k ≤ |r_j| + 2|w| ≤ |r_i| + |r_j| + 2|w|`, and in the normal form
   that last quantity **is** `|R| ≤ c`, so the donor stays under the cap;
3. rotate `r_i` to `rot_a(r_i)` (again free), and apply one AC2 move
   `r_i ← r_i · (w rot_p(r_j^e) w^-1)`. Its result, reduced, is `R`, of length
   `≤ c` by the guard.

**(⊇, the move set is not too small.)** Conversely, take any AC2 move
`r_i ← r_i · (u r_j^e u^-1)` with a completely **arbitrary** conjugator `u`,
applied to any representative of the cyclic word `r_i` (any rotation of `r_i`
or of `r_i^-1`), whose reduced result `R` has `|R| ≤ c`. Then `R` is produced
by one of the moves above. Three observations:

* *Rotations of `r_i^-1` are already covered.* As a cyclic word,
  `(A · w · P · w^-1)^-1` equals `A' · w · P^-1 · w^-1` for a rotation `A'` of
  `A^-1`, and relators are stored up to inversion; so ranging `e` over both
  signs makes rotations of `r_i^-1` redundant.
* *An arbitrary conjugator normalises.* Writing `u = w·q` with `q` the length-`p`
  prefix gives `u r_j^e u^-1 = w · rot_p(r_j^e) · w^-1`, so every conjugate of
  `r_j^e` has the form used above.
* *Cancellation shortens the connector.* If the freely reduced product cancels
  at any junction that involves `w`, the same cyclic word is produced by a
  strictly shorter connector:
  - `w`↔`rot_p(r_j^e)`: if `w = w'c` and `rot_p(r_j^e) = c^-1 T` then
    `w P w^-1 = w' (Tc) w'^-1` and `Tc = rot_{p+1}(r_j^e)`;
  - `rot_p(r_j^e)`↔`w^-1`: symmetric, using `rot_{p-1}`;
  - `rot_a(r_i)`↔`w` and `w^-1`↔`rot_a(r_i)` (the cyclic wrap): the cancelled
    letter moves across the cyclic word and changes `a` by one.

  Iterating terminates, so every AC2 result is the cyclic word of some
  `rot_a(r_i) · w · rot_p(r_j^e) · w^-1` **with no cancellation at any junction
  touching `w`**. For that normal form the product is already cyclically
  reduced and

  ```
  |R| = |r_i| + |r_j| + 2|w|,   hence   |w| = (|R| - |r_i| - |r_j|)/2
                                             ≤ (c - |r_i| - |r_j|)/2,
  ```

  which is precisely the connector bound. The bound therefore loses nothing —
  no matter how long the original `u` was.

**Consequence (what a CLOSED result means).** The component computed here is
exactly the set of presentations reachable from the start by sequences of
elementary AC moves (AC1, AC2 with an arbitrary conjugator, AC3) in which every
intermediate presentation has both relators of length ≤ c. Hence

> the component is closed under cap `c`  ⟺  no sequence of elementary AC moves
> connects the state to the trivial presentation with every intermediate
> relator of length ≤ `c`.

`test_capbfs.py::test_b2_move_set_is_the_full_ac2_move_set` checks the ⊇
direction computationally as well: for six states it enumerates *all*
conjugators `u` with `|u| ≤ 4`, all rotations of `±r_i` and of `±r_j`, and both
signs, and finds the resulting neighbour set equal (not merely contained) to
the model's.

### 1.5 Search

Breadth-first from the canonicalised initial state, recording for each
discovered state its parent and the move `(i, j, e, a, p, w)` that produced it.
BFS runs **whole levels**; it stops

* when the frontier is empty → `closed: true` (the component is exhausted);
* at the end of the level in which `{x, y}` is discovered → `solved: true`
  (finishing the level makes the returned state set exactly a ball of some
  radius, hence independent of the order moves are enumerated in — which is
  what lets the fast and the reference engine be compared as *sets*);
* immediately if a new state would push the count past `--max-states` →
  `closed: false`, `budget_exhausted: true`. Such a run proves nothing about
  closure.

An initial presentation already equal to `{x, y}` is solved with an empty path
and one state.

### 1.6 Output

```json
{
  "initial": ["xyxYXY", "xxxYYYY"],  "cap": 14,
  "closed": true, "solved": false,
  "states": 339056, "max_states": 3000000,
  "min_total_length_seen": 13, "frontier_size_at_stop": 0,
  "seconds": 13.31, "nodes_per_second": 25471,
  "popped": 339056, "budget_exhausted": false, "engine": "capbfs-numba"
}
```

and, when solved, additionally

* `"path"`: one object per move, `{"i", "j", "e", "a", "p", "w"}`, where `i` is
  the index **into the parent state as printed** of the relator being replaced,
  `j = 1 - i`, `e ∈ {1, -1}`, `a`/`p` are the left-rotation offsets and `w` the
  connector as an `xXyY` string (`""` for the empty connector);
* `"path_states"`: the `len(path) + 1` intermediate presentations as
  `[r1, r2]` string pairs, canonicalised, starting at `initial` and ending at
  `["x", "y"]`.

---

## 2. Files

| file | what it is |
|---|---|
| `capbfs.py` | the fast engine (numba, nopython) plus the CLI |
| `capbfs_reference.py` | pure-Python oracle: tuples of signed ints, no packing, no tricks |
| `verify_path.py` | independent certificate replayer (plain Python strings; imports neither engine) |
| `test_capbfs.py` | pytest suite (a)–(f) |

### Representation used by the fast engine

A letter is 2 bits — `bit1` = generator (`0 = x`, `1 = y`), `bit0` = inverse
flag — so `x = 0, X = 1, y = 2, Y = 3`, inversion is `code ^ 1`, and the induced
letter order is the `x < X < y < Y` the reference uses. A word of length
`n ≤ 31` is **one int64**: letter `t` at bits `2(n-1-t)`, most significant
letter first, plus a sentinel bit `1 << 2n` recording the length. Because the
sentinel dominates, comparing two keys as integers *is* comparing
`(length, letters)`, which is also how a canonical pair is sorted — so the pair
ordering is a single integer compare.

This buys the two hot operations as register work:

* rotate left by one letter is `((b << 2) & mask) | (b >> 2(n-1))`, so the
  canonical form (min over `n` rotations of `w` and `n` of `w^-1`) is `2n`
  register ops — no `(n, 2)` bool array, no Booth pass, no allocation;
* free reduction of the concatenation pushes letters into an accumulator and
  cancels against `acc & 3`.

States live in an open-addressing table (linear probing, load factor ½, keyed by
the two int64s, grown by doubling with a rehash). Move enumeration, reduction,
canonicalisation, dedup and parent/move recording all happen inside one
`@njit(cache=True)` kernel; nothing crosses into Python during the search. The
connector table (all freely reduced words of length ≤ `(c-2)//2`, `2·3^W - 1` of
them) is built once per run with numpy, in the same order the reference
generates it, so connector indices mean the same thing in both engines.

**The cap is limited to 16, not 31.** A relator key holds up to 31 letters,
but the *unreduced* product of a move, `rot_a(r_i) · w · rot_p(r_j^e) · w^-1`,
is freely reduced letter by letter into one int64 accumulator before it is
cyclically reduced, and with an empty connector it has up to
`|r_i| + |r_j| ≤ 2c` letters. `_cyc_reduce` reads the leading letter with a
shift of `2(len − 1)` bits: 32 letters are exact (shift 62), 33 need a shift
of 64, which is undefined behaviour and on x86 wraps silently, so legal moves
would be dropped (measured: ≈ 15 % of the moves in that regime at cap 31, none
spuriously accepted — see section 6). `bfs` therefore refuses any cap above
`MAX_CAP = 16`; every number in this document is at a cap ≤ 16, and test (g)
pins the first layer of the search against the reference exactly at the
32-letter boundary.

---

## 3. CLI

Single presentation:

```
python capbfs.py --r1 YXYxyx --r2 YYYYxxx --cap 12 --max-states 5000000 --out out.json
```

Batch over a CSV with `name,r1,r2` columns (extra columns are ignored), one
JSON object per line per `(row, cap)`:

```
python capbfs.py --csv rows.csv --caps 8,10,12,14 --max-states 5000000 --out out.jsonl
python capbfs.py --csv ../../data/AC19_extended_aut_min.csv --caps 8,10 --limit 50 --out ac19.jsonl
```

Other flags: `--no-stop-when-solved` (keep expanding after `{x, y}` is found —
use this when you want the full component of a solvable presentation),
`--limit N` (first `N` CSV rows).

Verify certificates (works on both `.json` and `.jsonl`, skips unsolved rows):

```
python verify_path.py out.json
python verify_path.py out.jsonl
```

`verify_path.py` re-derives every step from the recorded parent state with its
own string code: it checks the move descriptor is well formed, that the
connector respects the budget `2|w| ≤ c - |r_i| - |r_j|`, that
`R = cyc_reduce(rot_a(r_i) · w · rot_p(r_j^e) · w^-1)` has `1 ≤ |R| ≤ c`, that
`{R, r_j}` canonicalises to the next recorded state, that every recorded state
is canonical with nonempty relators of length ≤ `c`, and that the last state is
`{x, y}`. Exit status is 1 on any failure and **3 when no input contained a
solved result at all**, so a truncated or edited batch cannot pass silently;
`--allow-empty` accepts an all-unsolved batch (a closure table) with status 0.

---

## 4. Measured results

Machine: 4 CPUs, 15 GB RAM, Python 3.11.15, numba 0.63.1, numpy 2.1.3;
single-threaded.

### AK(3) = `(xxxYYYY, xyxYXY)`

`--no-stop-when-solved` is irrelevant here: the trivial state is never reached.

| cap | states | closed | solved | seconds | popped nodes/s |
|---:|---:|:--|:--|---:|---:|
| 7 | 1 | yes | no | 0.00 | — |
| 8 | 1 | yes | no | 0.00 | — |
| 9 | 814 | yes | no | 0.02 | 42,007 |
| 10 | 4,188 | yes | no | 0.11 | 38,931 |
| 11 | 21,388 | yes | no | 0.64 | 33,561 |
| 12 | 42,856 | yes | no | 1.37 | 31,271 |
| 13 | 172,192 | yes | no | 6.32 | 27,231 |
| 14 | **339,056** | yes | no | 13.31 | **25,471** |
| 15 | 1,254,188 | yes | no | 56.54 | 22,182 |
| 16 | 2,333,976 | yes | no | 113.79 | 20,512 |

At caps 7 and 8 nothing at all is reachable: `|r_1| + |r_2| = 13`, so every
move with an empty connector produces a relator of length 13 unless it cancels,
and no admissible cancellation lands at or below 8. `min_total_length_seen` is
13 at every cap in the table — no state in any of these components is shorter in
total than the start.

**Throughput: 25,471 popped nodes/second at cap 14 on AK(3)** (target: ≥
20,000), measured by `test_throughput_ak3_cap14`, which asserts the target.
Peak RSS is ≈ 200 MB for the cap-14 run and ≈ 530 MB for the cap-16 run.

### AC19 rows (`data/AC19_extended_aut_min.csv`)

| row | presentation | minimal cap that solves | path length |
|---|---|---:|---:|
| `ac19_0` | `X`, `YYXyx` | 5 | 2 |
| `ac19_1` | `YYXyX`, `YXXyx` | 5 | 5 |
| `ac19_2` | `YYXyx`, `YXXyx` | 5 | 3 |

Each is minimal in the sense that every admissible smaller cap (down to the
longest initial relator) gives a CLOSED component not containing `{x, y}`, and
each certificate is replayed successfully by `verify_path.py`. The reference
engine independently finds a path of the same length at the same cap.

### The three rank-2 U124 rows

`data/ms_unsolved_reps/aca_124_best.csv` has three rank-2 rows: `aca_115` is
AK(3) in another spelling (`YXYxyx, YYYYxxx`), `aca_116` = `YYYXyyX, YXXXyxx`
and `aca_117` = `YYYXyyx, YXXXyxx` (the two length-14 rows,
`MS(2, x⁻²yx²y)` and `MS(2, x⁻²yx²y⁻¹)`). All three were run at every cap from
7 to 16 with `--max-states 5000000`; every run is CLOSED, none is SOLVED, no
budget was exhausted, and `min_total_length_seen` is the start's own length
(13 / 14 / 14) at every cap. Exact records: `records/u124_rank2_caps7_16.jsonl`
(`verify_path.py --allow-empty` accepts it; without the flag it correctly
returns 3, since there is nothing to verify). The `aca_115` column reproduces
the AK(3) table above from a different spelling of the start.

| cap | `aca_115` = AK(3) | `aca_116` | `aca_117` | closed | solved | seconds |
|---:|---:|---:|---:|:--|:--|---:|
| 7 | 1 | 1 | 1 | yes | no | 0.02 / 0.00 / 0.00 |
| 8 | 1 | 1 | 1 | yes | no | 0.00 / 0.00 / 0.00 |
| 9 | 814 | 1 | 1 | yes | no | 0.02 / 0.00 / 0.00 |
| 10 | 4,188 | 14 | 19 | yes | no | 0.11 / 0.00 / 0.00 |
| 11 | 21,388 | 278 | 1,156 | yes | no | 0.65 / 0.01 / 0.03 |
| 12 | 42,856 | 1,082 | 3,508 | yes | no | 1.37 / 0.03 / 0.11 |
| 13 | 172,192 | 21,512 | 16,580 | yes | no | 6.33 / 0.77 / 0.59 |
| 14 | 339,056 | 44,208 | 35,212 | yes | no | 13.29 / 1.68 / 1.35 |
| 15 | 1,254,188 | 169,064 | 123,500 | yes | no | 58.20 / 7.39 / 5.38 |
| 16 | 2,333,976 | 357,952 | 319,212 | yes | no | 113.11 / 16.81 / 14.79 |

So none of the three has an AC trivialisation in which every intermediate
relator has length ≤ 16. For the two length-14 rows nothing at all moves below
cap 10 (`|r_1| + |r_2| = 14`, and no admissible cancellation lands at or below
9), and their cap-16 components are about 6.5 × smaller than AK(3)'s. This is
a statement about short trivialisations only — see section 5 — and says
nothing about paths through longer relators, stable moves or higher rank.

### Test suite

`pytest research/ac_cap_closure_20260912/test_capbfs.py` — all tests pass
(67 tests, ≈ 60 s on this machine), covering

* **(a)** 30 random AC-trivial presentations (built by random AC moves from
  `(x, y)` with relator lengths ≤ 8, seed 12345) × caps 6–10: the fast and the
  reference state sets are equal as sorted lists of canonical key strings, and
  `states` / `solved` / `closed` / `min_total_length_seen` agree;
* **(b)** for four CLOSED components, every neighbour of every member, computed
  by the *reference* generator, is again a member;
* **(b2)** the bounded-connector move set equals brute-force AC2 over all
  conjugators `|u| ≤ 4` and all rotations of `±r_i`, `±r_j`;
* **(c)** `component(cap c) ⊆ component(cap c+1)` for three families;
* **(d)** minimal solving caps for three AC19 rows, with certificates replayed
  by `verify_path.py`, plus a negative control (a certificate with one rotation
  offset altered is rejected);
* **(e)** AK(3) is unsolved and CLOSED at caps 7–11 with sizes
  `1, 1, 814, 4188, 21388`;
* **(f)** BFS from `(r1, r2)` and from `(r2, r1)` produce identical state sets;
* **(g)** the packing boundary: caps 17, 24, 31 and 32 are refused; for eight
  constructed states with two length-16 relators at cap 16 (every move
  concatenates exactly 32 letters, the most the accumulator holds, and the
  construction guarantees a nonempty first layer) the kernel's children of the
  root equal the reference neighbour set; and `verify_path` returns 3 on an
  input with nothing to verify, 0 with `--allow-empty`.

---

## 5. What a CLOSED result does and does not certify

**It does certify**, for the stated start and cap `c`: the set of presentations
AC-reachable from the start *without any intermediate relator ever exceeding
length `c`* is exactly the enumerated set. If `{x, y}` is not in it, then there
is **no** sequence of elementary AC moves (AC1, AC2 with an arbitrary
conjugator, AC3) from the start to the trivial presentation all of whose
intermediate presentations respect the cap. Equivalently: any AC trivialisation
of the start, if one exists, must at some point produce a relator of length
`> c`.

**It does not certify** any of the following.

* *Nothing about longer paths.* A presentation may be AC-trivial and still have
  a closed component at every cap you can afford; closure at cap `c` says only
  that the peak relator length of any trivialisation exceeds `c`. Growing the
  cap by one can change the picture completely (AK(3): 21,388 states at cap 11,
  2,333,976 at cap 16).
* *Nothing about stable AC.* The whole search lives in rank 2. Adding a
  generator and the relator `z` (stabilisation) is outside the model, and
  stably-AC-trivial presentations are known to exist that this search can say
  nothing about.
* *Nothing about other move sets.* Only the balanced rank-2 AC moves above are
  modelled — no Nielsen/Whitehead automorphisms applied to the pair, no
  substitutions of `x, y` by other bases, no rank-3 detours.
* *Nothing beyond the budget.* A run with `budget_exhausted: true` (or
  `closed: false` for any reason) has enumerated a subset of the component and
  certifies nothing at all about closure. Only `closed: true` counts, and
  `frontier_size_at_stop` must be 0.
* *Not a proof about the AC conjecture.* AK(3) being closed at cap 16 is a
  statement about short trivialisations, not a counterexample claim.

The trust surface of a CLOSED claim is `capbfs.py` alone — unlike a SOLVED
claim, there is no small certificate to re-check. That is why the suite pins the
fast engine to a pure-Python oracle set-for-set on 126 (presentation, cap)
pairs, checks closure of the reported components with the *reference* move
generator, and checks the move generator itself against brute-force AC2 — and
why the module was handed to two adversarial reviewers before it was committed
(section 6).

---

## 6. Adversarial verification

After the module was written, two independent reviewers were asked to refute
it: one attacked the **model** (is the implemented move set under the
per-relator cap exactly the set of cyclic-word pairs reachable by elementary AC
moves — AC1, AC2 with an arbitrary conjugator, AC3 — with every intermediate
relator of length ≤ `c`?), the other the **code**. Their scripts and raw
outputs are kept verbatim under `adversarial/` (see the README there for how
each was run). Neither had seen the other's work. Sections 6.1 and 6.2 are the
model reviewer's report; the code reviewer's report is section 6.3.

### 6.1 The model: not refuted

* **Completeness (no missing moves).** A formulation with nothing in common
  with the module — enumerate `r_i · (u r_j^e u^-1)` over *all* freely reduced
  conjugators `u` (no rotations enumerated, no connector bound; rotations are
  absorbed into `u`), words as strings, canonical form under the *different*
  letter order `y < Y < x < X` — reproduces the module's neighbour sets on 50
  `(state, cap)` combinations at caps 5–14, with the brute set saturating in
  `|u|` far beyond the model's `⌊(c − |r_i| − |r_j|)/2⌋` connector bound
  (AK(3) at cap 14: model bound `|w| ≤ 0`, brute `|u| ≤ 8`, the same 84
  neighbours). Full-BFS state sets agree brute = reference = fast on 18 runs at
  caps 5–7 (largest 2,333 states). Split cancellation, partially cancelling
  conjugators, donor = target (`{xy, xy}`), length-1 relators and using
  `r_i^-1` as the representative were all covered and added nothing.
* **Soundness (no extra moves, cap-respecting realisation).** Over *all*
  84,454 ordered pairs of the 275 canonical cyclic-word classes of length ≤ 7
  at caps 4–8 (160,319 distinct model outcomes, including the
  `|r_i| + |r_j| > c` regime), every model move has a rotation/connector choice
  whose freely reduced AC2 product word already has length ≤ `c`, so the
  elementary realisation never exceeds the cap: 0 violations. Same on 400
  random states at caps 4–12 (4,327 outcomes). The shortest product word is
  often longer than `|R|` (split cancellation is real) but never past the cap.
* **Canonicalisation.** A complete invariant of the cyclic-word-up-to-inversion
  class: 1,791 classes over all 29,540 cyclically reduced words of length ≤ 9,
  identical in both engines and class-for-class identical to the
  different-order implementation; pair canonicalisation is symmetric on 3,000
  random pairs.
* **Certificates.** All 30 certificates produced by the *reference* engine for
  the random AC-trivial panel verify, so `verify_path.py` is not merely
  replaying `capbfs`'s conventions; 10 tamperings of a 4-step certificate are
  all rejected. The one leniency found — a batch with every row marked
  unsolved passed with status 0 — is fixed (status 3, `--allow-empty`).
* **Headline table.** AK(3) = 814 / 4,188 / 21,388 / 42,856 states at caps
  9–12 re-derived by the pure-Python reference, sets equal — two caps beyond
  what the suite checks.
* **Modelling choices restated.** Pruning moves that produce an empty relator
  is vacuous for `det = ±1` starts (and both engines agree on degenerate
  starts such as `{x, x}`); AK(3) "closed at caps 7 and 8" is the vacuous
  single-state component (zero admissible moves, confirmed by the brute
  generator with `|u| ≤ 8`).

### 6.2 The engine: one real defect, fixed

The int64 word packing is exact only while the intermediate freely reduced
concatenation has at most 32 letters. From 33 letters on, `_cyc_reduce` shifts
by ≥ 64 bits — undefined behaviour, and the same helpers gave different
results inlined in the kernel than compiled standalone. That regime is entered
whenever `|r_i| + |r_j| ≥ 33`, i.e. at any cap ≥ 17, and `bfs` accepted caps up
to 31. Measured at cap 31: 6,623 of 45,029 overflow-regime move evaluations
were silently rejected although their true result was legal (0 spurious
accepts); on a state the engine itself visits at cap 17, 3 of 17 rotations
were dropped. No state-set error was observed (248 random overflow-regime
states at caps 17–31, child sets equal to the reference) because every dropped
move lies in a rotation orbit `(a + t, p − t)` that yields the same child, and
the orbit member with the wrap cancellation at the middle junction has
accumulator peak `max(|r_i|, |R|) ≤ c ≤ 31` and is computed correctly — a
saving invariant that was nowhere stated or tested, while nothing in the suite
exercised a cap above 12.

Fix: `bfs` refuses any cap above `MAX_CAP = 16`, the packing paragraph in
section 2 says why, and test (g) pins the first layer against the reference at
the 32-letter boundary. Every number in this document was already at a cap ≤ 16.

### 6.3 The code: review in progress

The code-focused reviewer had not finished when this revision was committed
(it had reproduced the AK(3) cap-16 component, 2,333,976 states, on the fixed
module and re-run the 67-test suite green). Its scripts and final report are
added under `adversarial/code/` in the follow-up commit, and this section is
rewritten from that report.
