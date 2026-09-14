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
signs, and finds the resulting brute-force neighbour set **contained** in the
model's — and, on those six `(state, cap)` pairs, equal to it.

Read that equality as a property of the six pairs, not as a theorem. Only the
containment `brute(|u| ≤ U) ⊆ model` is general (it is the ⊇ direction above,
restricted to short conjugators); brute force at a fixed `U` can be a *strict*
subset, because the model admits connectors up to
`⌊(c − |r_i| − |r_j|)/2⌋`, which may exceed `U`. At `{x, y}` with `c = 12` that
bound is 5 and the brute sets have sizes 4, 4, 16, 48, 152 for `|u| ≤ 0…4`
against the model's 472, with equality only from `|u| ≤ 5`
(`test_b2_containment_is_the_general_direction_equality_is_not`). What the
argument in this section establishes — and what the suite checks in the
saturated cases — is that nothing escapes the model, at any conjugator length.

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

`frontier_size_at_stop` is the number of discovered states whose neighbourhood
was **not** fully expanded: the unprocessed remainder of the interrupted level
plus everything discovered beyond it (`states − popped + 1` on a
budget-exhausted run, `0` on a CLOSED one). It is **not** the size of the next
level; both engines compute this same quantity, so the two JSON outputs can be
diffed field by field (test (h)).

---

## 2. Files

| file | what it is |
|---|---|
| `capbfs.py` | the fast engine (numba, nopython) plus the CLI |
| `capbfs_reference.py` | pure-Python oracle: tuples of signed ints, no packing, no tricks |
| `verify_path.py` | independent certificate replayer (plain Python strings; imports neither engine) |
| `test_capbfs.py` | pytest suite (a)–(j) |
| `run_min_cap.py` | cap ladder per CSV row: closure records below the minimal solving cap (or budget) |
| `make_separator.py` | reduces ladders to one line per row; the tables in section 4 |
| `records/` | exact JSONL records of every run quoted in section 4 |

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

**Exit status.** Single-presentation mode propagates a rejected input as an
exception (status 1). Batch mode keeps going — a refused `(row, cap)` is
written as an `{"initial", "cap", "error"}` record so the output stays
one line per `(row, cap)` — but it prints every rejection to stderr and
**exits 1**, so a sweep that only checks the status cannot mistake "this cap
produced nothing" for "this cap is closed" (test (j)).

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

Re-measured after the section 6.3 fixes: every state count below is
reproduced exactly (caps 12–16: 42,856 / 172,192 / 339,056 / 1,254,188 /
2,333,976, all CLOSED with `frontier_size_at_stop = 0`), and the timings move
by a few per cent with machine load — 1.45 s, 6.73 s, 14.18 s, 60.6 s, 120.0 s
on the re-run, i.e. 29,504 / 25,570 / 23,909 / 20,712 / 19,454 popped nodes/s.
The ≥ 20,000 nodes/s target at cap 14 is met with margin in every run.

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

### Minimal solving cap as a separator: every U124 row that fits is closed at 16, most solved rows are not

The user-level question behind this module is whether some cheap, exact test
tells the 124 unsolved Miller–Schupp classes apart from the solved-but-hard
ones. Rank-raising does not (`research/ac19_triangle_theory_20260913/`). The
cap-bounded closure does, up to a stated limit. `run_min_cap.py` walks every
row up its cap ladder — from its floor (the longer relator) to 16, stopping at
the first cap that SOLVES or exhausts the 5,000,000-state budget — and
`make_separator.py` reduces the ladders to one line per row. Exact records:
`records/separator/u124_caps_le16.jsonl` (745 runs),
`records/separator/solved60_caps_le16.jsonl` (78 runs, every one of the 45
solved certificates replayed by `verify_path.py`), `summary.json`, `TABLES.md`.

**Scope limit first.** The engine's cap is 16, so a row enters the ladder only
if its longer relator has length ≤ 16. In this spelling the `MS(n, w)` rows
with `n ≥ 7` have a defining relator of length `2n + 3 ≥ 17`: **4 of the 124
U124 rows** (`aca_101`–`aca_104`) and **12 of the 60 solved-ladder rows** (one
each in bins 0 and 6, two in bin 7, four in each of bins 8 and 9) are out of
reach and are simply absent below.

**U124 (120 of 124 rows).** Every admissible cap up to 16 gives a CLOSED,
unsolved component; no budget was ever exhausted. Total cost 329 CPU-s, of
which 190 s is AK(3) (`aca_115`) alone; the median row costs 0.02 s because a
long start leaves almost no room under the cap (`aca_123`, total length 17,
has 124 states at cap 14). So for 120 of the 124 classes: **no AC
trivialisation exists in which every intermediate relator has length ≤ 16.**
The largest components after AK(3): `aca_116` 357,952, `aca_118` 321,680,
`aca_117` 319,212, `aca_8` 227,028 states at cap 16.

**Solved ladder (48 of 60 rows).** 45 solve within cap 16 and their minimal
cap tracks the difficulty bin; 3 do not (bins 7, 8, 8: rows `596`, `605`,
`610`), and those three are, under this test, indistinguishable from U124 —
each closes at cap 16 with 51,192 states. Total cost 389 CPU-s (median 2.1 s,
maximum 56 s).

| bin | rows in reach | minimal solving caps | closed at 16 |
|---:|---:|---|---:|
| 0 | 5 | 5, 7, 9, 11, 15 | 0 |
| 1 | 6 | 8, 8, 8, 8, 8, 15 | 0 |
| 2 | 6 | 8, 8, 8, 9, 10, 11 | 0 |
| 3 | 6 | 9, 9, 10, 10, 10, 13 | 0 |
| 4 | 6 | 10, 11, 13, 13, 14, 15 | 0 |
| 5 | 6 | 12, 12, 12, 12, 14, 15 | 0 |
| 6 | 5 | 14, 14, 14, 14, 15 | 0 |
| 7 | 4 | 13, 13, 13 | 1 |
| 8 | 2 | — | 2 |
| 9 | 2 | 15, 15 | 0 |

So the test is exact in one direction and strong in the other: a row that
solves within the cap is AC-trivial with a replayable certificate; a row that
closes at 16 is either unsolved (all 120 reachable U124 rows) or a solved row
whose every trivialisation needs a relator longer than 16 (3 of 48). What it
costs is bounded — under four minutes for the worst row (AK(3)), seconds for
almost everything else — and what it cannot do is reach the `n ≥ 7` family at
all. A sharper separator would need either a longer packing (two words per
relator, cap 32) or a different spelling of those rows.

Three side remarks. (i) The minimal caps of the solved rows are far below the
relator lengths their heuristic certificates reach: bin-6 rows solve at cap
14–15 with 25–92 moves, where the `S20_MK2` runs used a per-relator cap of 48.
(ii) Two bin-9 rows (`634`, `635`) solve at cap 15 in 40 moves each, so
"bin 9" measures heuristic-search effort, not peak relator length.
(iii) The three closed-at-16 rows `596`, `605`, `610` have the *same*
cap-16 component — the three enumerated state sets are identical (51,192
states, checked set-for-set) — so under the cap they are one AC class, not
three independent misses: exactly one reachable solved class needs a relator
longer than 16.

### Test suite

`pytest research/ac_cap_closure_20260912/test_capbfs.py` — all tests pass
(89 tests, ≈ 95 s on this machine), covering

* **(a)** 30 random AC-trivial presentations (built by random AC moves from
  `(x, y)` with relator lengths ≤ 8, seed 12345) × caps 6–10: the fast and the
  reference state sets are equal as sorted lists of canonical key strings, and
  `states` / `solved` / `closed` / `min_total_length_seen` agree;
* **(b)** for four CLOSED components, every neighbour of every member, computed
  by the *reference* generator, is again a member;
* **(b2)** brute-force AC2 over all conjugators `|u| ≤ 4` and all rotations of
  `±r_i`, `±r_j` is contained in the bounded-connector move set — always — and
  equal to it on the six chosen `(state, cap)` pairs; a companion test pins the
  case where containment is strict (`{x, y}` at cap 12, equality only from
  `|u| ≤ 5`), so the equality is not misread as a theorem;
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
  root equal the reference neighbour set; `2·MAX_CAP ≤ 32 < 2·(MAX_CAP+1)` is
  asserted, so the constant cannot drift away from the packing invariant; and
  `verify_path` returns 3 on an input with nothing to verify, 0 with
  `--allow-empty`;
* **(h)** the two engines agree field by field — `states`, `popped`, `closed`,
  `solved`, `budget_exhausted`, `min_total_length_seen` and
  `frontier_size_at_stop` — on budget-exhausted runs (five budgets × both
  stop modes) as well as on CLOSED, SOLVED and already-trivial runs;
* **(i)** `max_states ≤ 0` still allocates room for the root and returns what
  the reference returns (one state, `budget_exhausted`), instead of writing
  the root past the end of zero-length node arrays;
* **(j)** batch mode writes an `error` record for a refused `(row, cap)` **and**
  exits 1, while an all-good batch exits 0.

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

### 6.3 The code: three small defects, fixed; the numbers reproduce

The code-focused reviewer worked against the module as delivered and, in
parallel, against the patched tree. Its scripts are under `adversarial/code/`.

**Independently confirmed.** The packing defect of section 6.2 was found a
second time, from the other side (`probe5.py`, `probe16.py`: the threshold is
exactly `|r_i| + |r_j| = 33`, i.e. cap ≥ 17 — 0 diverging moves in 4.3 M
evaluations at sums 30–32, first divergence at 33), and the patched boundary
was stressed deliberately rather than randomly: 400 constructed 16/16 pairs
whose every move concatenates exactly 32 letters and then cyclically reduces
8–15 rounds, 204,800 moves compared as reduced words *and* as packed canonical
keys, 0 divergences (`cap16.py`). The fast-vs-reference differential was also
extended through the band the suite never covered: 468 `(presentation, cap)`
pairs at caps 10–12 (`diff1012.py`) and 5,815 full CLOSED components at caps
13–16 (`diff1316.py`), 0 mismatches, plus 12 adversarial inputs — single-letter
relators, `r1 = r2`, `r1 = r2^-1`, `cap = 1`, a cap below `|r_1| + |r_2|` —
all agreeing (`adv.py`). Every published number reproduced: the AK(3) table,
the cap-16 headline component (2,333,976 states, 113.7 s, ≈ 530 MB peak RSS),
monotonicity across caps 9–14, ≥ 20,000 popped nodes/s at cap 14, and the
CLI/certificate round trip (`ak16.py`, `mono.py`, `thr.py`).

**Fixed here.** Three defects, none of which can change a published number
(all are outside the search itself or outside the caps used), but each of which
could mislead a later consumer:

1. *`max_states ≤ 0` wrote outside the node arrays.* The kernel clamped its
   initial node capacity to `max_states`, so `max_states = 0` allocated
   ten zero-length arrays and then wrote the root into them. numba has bounds
   checking off, so these were silent heap writes past the end; the run still
   returned `states = 1, budget_exhausted = true`, which hid it. The capacity
   is now floored at 1 (the root always fits), the budget still trips on the
   first child, and test (i) pins the result against the reference.
2. *`frontier_size_at_stop` meant different things in the two engines.* On a
   budget-exhausted run `capbfs` returned `count − head` (the unprocessed
   remainder of the interrupted level plus everything beyond it) while
   `capbfs_reference` returned `len(frontier)` (only the next level) — e.g. 46
   vs 11 at `max_states = 50`. Nothing published was affected (§5 only uses the
   field on CLOSED runs, where both were 0), but the two engines' JSON could not
   be diffed field by field. The reference now reports the same quantity
   (`len(seen) − expanded`), and test (h) compares every field on budget,
   CLOSED, SOLVED and already-trivial runs.
3. *Batch mode swallowed a rejected cap.* `--csv` caught the `ValueError` from
   a refused cap, wrote it as an `error` record and still exited 0, so a cap
   sweep checking only the exit status would read "this cap produced nothing"
   as "this cap is closed". The batch still completes and still writes the
   record, but now prints each rejection to stderr and exits 1 (test (j)).

**Wording corrected.** README §1.4 said the brute-force AC2 neighbour set at
`|u| ≤ 4` is "equal (not merely contained)" to the model's. That equality holds
at the six `(state, cap)` pairs the test uses, but it is not general: whenever
the model's connector bound `⌊(c − |r_i| − |r_j|)/2⌋` exceeds 4, brute force at
`|u| ≤ 4` is a strict subset (at `{x, y}`, `c = 12`: 152 vs 472, equality only
from `|u| ≤ 5`). Only the containment direction is a theorem, and it is the one
the soundness argument needs; §1.4 now says so and
`test_b2_containment_is_the_general_direction_equality_is_not` pins the strict
case. The reviewer found no escape from the model at any `|u| ≤ 6` on eight
`(state, cap)` pairs (`model.py`).

**Still true after the fixes**: `verify_path.py` rejects all ten tamperings of
a certificate and accepts certificates produced by the *other* engine, and the
"nothing to verify" leniency is gone (status 3 unless `--allow-empty`).

**What was and was not re-verified after the fixes.** The three fixes and the
wording change were made by a separate fixer pass that reproduced each finding
first, then re-ran the whole suite (89 tests green) and the reviewer's own
`budget.py` / `adv.py` reproductions against the fixed tree. A further
independent re-verification pass was scheduled but did not run (it was cut off
by a usage limit), so the post-fix evidence is the fixer's runs plus a
maintainer re-run of the full suite — 89 passed in 85 s, throughput 23,700
popped nodes/s at cap 14 — not a third reviewer. The engine's exactness at
caps ≤ 16, which is what every published number rests on, is unaffected by
the three fixes (none touches the move evaluation) and remains covered by the
reviewer's pre-fix differentials in section 6.3 and by tests (a), (e), (g)
and (h).
