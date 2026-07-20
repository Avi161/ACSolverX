# Branch A (No-CoV) — how the pipeline works, end to end

Every number in this document is measured from the committed evidence in
`results/stable_ac/nocov/` or read directly off the code in this folder. Files referenced:
`run_nocov.py` (runner), `config_nocov.yaml` (production config), `stable_ac_nocov.ipynb`
(Colab notebook), `../solvern.py` (solver), `../word_families.py` (z-words),
`../verify_results.py` (certificate verifier).

## 1. What the experiment is

The Andrews–Curtis conjecture concerns balanced presentations of the trivial group and
whether they reduce to the trivial presentation under AC moves. The **stable** version
allows an extra dimension: add a new generator together with a defining relator, work in
the bigger free group, and see whether the search becomes *easier* there.

Branch A tests exactly that, in its simplest form ("No CoV" = no change of variables —
contrast with Branch B in `../cov/`, which substitutes and eliminates a generator
instead). For each benchmark presentation `⟨x,y | r1, r2⟩` and each word `w(x,y)` drawn
from a family, it builds the **stabilized presentation**

```
⟨x, y, z | r1, r2, z⁻¹·w⟩        (n_gen = 3, n_rel = 3)
```

and runs the same greedy best-first S-move search on it, at the same node budget as the
2-generator baseline. The new relator `z⁻¹w` (stored as the string `"Z" + w`, e.g.
`z_relator: "Zxy"`) is a Tietze extension defining `z = w`, so the group presented is
unchanged — the trivial group. The question is purely about the *search landscape*: does
the extra generator open shortcuts (lower `nodes_explored`, shorter paths, or solves the
2-gen search never finds)?

Two different success criteria, depending on the row's `source`:

- **`ladder` rows** (already solved by the baseline): efficiency. Compare
  `nodes_explored` / `path_length` against the row's `baseline_nodes_at_50k` /
  `baseline_path_at_50k` passthrough columns.
- **`reach` rows** (the baseline never solved them): reach. `solved: true` at any budget
  is a genuinely new solution. The single reach row in `combined_11` is **AK(3)**
  (`r1 = xxxYYYY`, `r2 = xyxYXY`, total length 13) — the open problem; its
  `bar_to_beat` is `min_relator_length < 13`, i.e. even *shrinking* it below its start
  length would be news. Ladder and reach rows are never mixed into one metric.

## 2. Input: the combined benchmark

`BENCHMARK: combined_11` → `results/benchmark/combined/benchmark_combined_11.json`,
built by `experiments/analysis/combined_benchmark.py` as `subset_10` (efficiency ladder,
one presentation per difficulty bin) + `reach_tier_1` (1 unsolved problem). Document
constants: `size: 11`, `n_ladder: 10`, `n_reach: 1`, `comparison_budget: 50000`.

The exact 11 rows (baseline columns are the 2-gen greedy at budget 50,000):

| name | source | bin | r1 | r2 | total len | baseline nodes @50k | solved @50k |
|---|---|---|---|---|---|---|---|
| ms499 | ladder | 0 | `YYYYYYYXyyyyyyx` | `YYYYx` | 20 | 6 | yes |
| ms165 | ladder | 1 | `YYYxyXYX` | `YYXyx` | 13 | 16 | yes |
| ms303 | ladder | 2 | `YYYXyyx` | `YYYxyXYX` | 15 | 70 | yes |
| ms491 | ladder | 3 | `YYYYYYXyyyyyx` | `YYXyyxyx` | 21 | 126 | yes |
| ms527 | ladder | 4 | `YYYYYYYYXyyyyyyyx` | `YYXXyyx` | 24 | 430 | yes |
| ms539 | ladder | 5 | `YYYYYXyyyyx` | `YYYxxYX` | 18 | 1,386 | yes |
| ms629 | ladder | 6 | `YYYYYYYYXyyyyyyyx` | `YYXYXyyx` | 25 | 12,452 | yes |
| ms613 | ladder | 7 | `YYYYYYYXyyyyyyx` | `YYYXYxyX` | 23 | 46,481 | yes |
| ms625 | ladder | 8 | `YYYYYYYYXyyyyyyyx` | `YYXYxyX` | 24 | 50,000 (cap) | no |
| ms637 | ladder | 9 | `YYYYYYYYXyyyyyyyx` | `YYYXyxYX` | 25 | 50,000 (cap) | no |
| AK(3) | reach | — | `xxxYYYY` | `xyxYXY` | 13 | — | never |

(`combined_22/44/66` scale the same construction to 20+2, 40+4, 60+6 rows;
`combined_11` is the screen, `combined_22` the verdict.)

## 3. The z-word families (`../word_families.py`)

Pure-Python string builders (no numba, no solver import). Words are over the input's own
alphabet (lowercase = generator, uppercase = inverse), free-reduced (not cyclically —
they are defining words, not relators), non-empty, exact-deduped in first-seen order, so
job order is deterministic.

- **A1 — curated.** The fixed 16-word list
  `x, y, X, Y, xy, xY, Xy, XY, yx, yX, xyx, yxy, xyX, yxY, xxy, xyy` (all `|w| ≤ 4`
  after reduction; overridable via `A1_WORDS`). Always exactly 16 words per row.
  Pure powers (`xx`, `YYY`, …) are deliberately absent: a `Z·w` relator earns its keep
  by cancelling against both relators, which favours generator-mixing words, and the
  powers that *are* relevant — those occurring inside the presentation's own relators —
  are generated per-presentation by A2 anyway (e.g. AK(3)'s A2 contains
  `xx, xxx, YY, YYY, YYYY`; ms499's contains `yy…y⁶, YY…Y⁷`). Also `z = w` and
  `z = w⁻¹` are the same problem up to renaming `z ↦ z⁻¹`, so an inverse-closed power
  list would half-duplicate itself.
- **A2 — relator prefixes.** Every prefix (length 1..L) of every cyclic rotation of each
  relator: exactly `Σᵢ |rᵢ|²` raw candidates, then free-reduce → drop empties → dedup.
  This is the "the relator itself knows where it hurts" family and **dominates cost**.
  `A2_MAX_WORDS: k` caps it by picking k evenly-spaced survivors (endpoints included);
  `A2_DROP_LEN1: true` drops the length-1 words that duplicate A1's singles.
- **A3 — prefix-fraction grid.** `free_reduce(r1[:⌈p·|r1|⌉] + r2[:⌈q·|r2|⌉])` for
  `(p, q)` over `A3_GRID × A3_GRID`, default grid `0.25, 0.5, 0.75, 1.0` → ≤ 16 words
  (dedup can shrink it). Every cell mixes BOTH relators — the grid has no `0` entry, so
  even `p = 1.0` is all of `r1` *plus* ≥ 1 symbol of `r2`, and `(1.0, 1.0)` is
  `free_reduce(r1·r2)`; pure `r1` is deliberately not a cell because it is already in
  A2. That is the division of labor: A2 = within-relator material (one relator at a
  time), A3 = cross-relator blends A2 can never produce. Short cells can accidentally
  reduce to an A2 word (0–5 per `combined_11` row, e.g. ms499's `YYYY+YY → YYYYYY`);
  the duplicate jobs land in different family files with identical results (the search
  is deterministic), so the redundancy is compute-only.

  **How A3 works, exactly.** The grid values are fractions, applied to each relator's
  length separately, with a ceiling. For each pair `(p, q)` from
  `[0.25, 0.5, 0.75, 1.0] × [0.25, 0.5, 0.75, 1.0]` (16 cells):

  1. Cut a prefix of `r1`: the first `⌈p·|r1|⌉` symbols.
  2. Cut a prefix of `r2`: the first `⌈q·|r2|⌉` symbols.
  3. Glue them: `w = free_reduce(prefix1 + prefix2)` — only free reduction, and the
     only place anything can cancel is the seam where the two prefixes meet.
  4. Dedup at the end, so you get ≤ 16 words.

  Full real example — ms499: `r1 = YYYYYYYXyyyyyyx` (length 15), `r2 = YYYYx`
  (length 5). The cuts are `⌈p·15⌉ = 4, 8, 12, 15` and `⌈q·5⌉ = 2, 3, 4, 5` (note the
  ceiling: 0.25 of 15 gives 4 symbols, not 3). All 16 cells, computed:

  | p | q | pieces | result | len |
  |---|---|---|---|---|
  | 0.25 | 0.25 | `YYYY` + `YY` | `YYYYYY` | 6 |
  | 0.25 | 0.5 | `YYYY` + `YYY` | `YYYYYYY` | 7 |
  | 0.25 | 0.75 | `YYYY` + `YYYY` | `YYYYYYYY` | 8 |
  | 0.25 | 1.0 | `YYYY` + `YYYYx` | `YYYYYYYYx` | 9 |
  | 0.5 | 0.25 | `YYYYYYYX` + `YY` | `YYYYYYYXYY` | 10 |
  | 0.5 | 0.5 | `YYYYYYYX` + `YYY` | `YYYYYYYXYYY` | 11 |
  | 0.5 | 0.75 | `YYYYYYYX` + `YYYY` | `YYYYYYYXYYYY` | 12 |
  | 0.5 | 1.0 | `YYYYYYYX` + `YYYYx` | `YYYYYYYXYYYYx` | 13 |
  | 0.75 | 0.25 | `YYYYYYYXyyyy` + `YY` | `YYYYYYYXyy` | 10 |
  | 0.75 | 0.5 | `YYYYYYYXyyyy` + `YYY` | `YYYYYYYXy` | 9 |
  | 0.75 | 0.75 | `YYYYYYYXyyyy` + `YYYY` | `YYYYYYYX` | 8 |
  | 0.75 | 1.0 | `YYYYYYYXyyyy` + `YYYYx` | `YYYYYYY` | 7 — **duplicate** of (0.25, 0.5) |
  | 1.0 | 0.25 | full `r1` + `YY` | `YYYYYYYXyyyyyyxYY` | 17 |
  | 1.0 | 0.5 | full `r1` + `YYY` | `YYYYYYYXyyyyyyxYYY` | 18 |
  | 1.0 | 0.75 | full `r1` + `YYYY` | `YYYYYYYXyyyyyyxYYYY` | 19 |
  | 1.0 | 1.0 | full `r1` + `YYYYx` | `YYYYYYYXyyyyyyxYYYYx` | 20 |

  Three regimes visible: rows `p = 0.25, 0.5, 1.0` are plain concatenations (their
  pieces end in `Y`, `X`, `x` — none is the inverse of the starting `Y`, so nothing
  cancels). Row `p = 0.75` is the instructive one: its piece ends in `…yyyy`, so the
  `Y…` prefix of `r2` cancels backwards into the seam and the word gets *shorter* as
  `q` grows (10 → 9 → 8 → 7), until `(0.75, 1.0)` fully telescopes (`yyyy·YYYY` gone,
  then `X·x` gone) down to `YYYYYYY` — colliding with cell `(0.25, 0.5)`. Dedup
  removes it: 16 cells → 15 distinct words for ms499. (Footnote: ms499 itself is a
  `combined_11` row used here for exposition — `combined_66`'s ladder draws different
  per-bin members.)

Exact counts on `combined_11` (defaults, no caps):

| name | A1 | A2 raw (Σ\|rᵢ\|²) | A2 after dedup | A3 |
|---|---|---|---|---|
| ms499 | 16 | 250 | 199 | 15 |
| ms165 | 16 | 89 | 76 | 16 |
| ms303 | 16 | 113 | 96 | 16 |
| ms491 | 16 | 233 | 183 | 15 |
| ms527 | 16 | 338 | 268 | 16 |
| ms539 | 16 | 170 | 142 | 15 |
| ms629 | 16 | 353 | 279 | 16 |
| ms613 | 16 | 289 | 238 | 16 |
| ms625 | 16 | 338 | 278 | 16 |
| ms637 | 16 | 353 | 282 | 16 |
| AK(3) | 16 | 85 | 70 | 16 |
| **total** | **176** | **2,611** | **2,111** | **173** |

So one full sweep at one budget = **176 + 2,111 + 173 = 2,460 searches** (A2 is 86% of
them). With `A2_MAX_WORDS: 64` every row's A2 count hits the cap (all are ≥ 70), so A2
drops to 11 × 64 = 704 and the sweep to 1,053 searches.

## 4. The solver: `search_n` (`../solvern.py`)

A numba port of the pure-Python reference `experiments/greedy_tests/spec/search.py`,
generalised to any `n_gen ≤ 26`, any `n_rel ≥ 2` — Branch A calls it at
`n_gen = 3, n_rel = 3`. It reproduces the spec's pop order **exactly** wherever the spec
can run (`n_gen ≤ 3`); `greedy_tests/test_solvern.py` pins that trace equality, so
correctness is a tested property, not an intention. CPU-only: words are 1-D `np.int8`
arrays (generator `i` = `±i`; `x=1, X=-1, y=2, Y=-2, z=3, Z=-3`), the hot loops are
`@njit`, the heap/dict orchestration is plain Python.

**State = canonical presentation.** Each relator is free-reduced (plus cyclic
wrap-around cancellation when `CYCLIC_REDUCE: true`, the production setting), then
replaced by the least element of its orbit under rotation **and inversion** — computed
with Booth's least-rotation algorithm under the **booth symbol order**
`(-abs(g), g > 0)`, i.e. `Z < z < Y < y < X < x`. The relator list is then sorted by
`(length, booth-lex)`. The resulting tuple of int-tuples is both the visited-set key and
the node identity.

**Priority queue.** A binary heap keyed by
`(total_length, depth, tiebreak_bytes)` where `total_length = Σ len(rᵢ)` (greedy: always
pop a shortest presentation first), `depth` = number of moves from the start, and
`tiebreak_bytes` packs each symbol as `abs(g) + 64·(g>0)` with `\x00` separators — a
byte string whose comparison reproduces the spec's rendered-ASCII order
(`X < Y < Z < x < y < z`). Keys are unique per state, so pop order is a strict total
order, independent of insertion order — this is what makes runs deterministic and
budget-prefix-comparable. The two symbol orders (booth for canonicalisation, ASCII for
the tie-break) are deliberate and must never be conflated.

**Expansion = S-moves.** From a popped state, for every target relator `i`, source
`j ≠ i`, sign `s ∈ {+1, −1}` (use `rⱼ` or `rⱼ⁻¹`), and all rotation pairs
`(k1, k2) ∈ [0, |rᵢ|) × [0, |rⱼ|)`: concatenate `rot_k1(rᵢ) · rot_k2(oⱼ)` **only when
the seam cancels** (last symbol of the rotated target = inverse of first symbol of the
rotated source), reduce, and replace relator `i` with the result. Children are dropped
when any relator exceeds the **per-relator cap** (`MAX_RELATOR_LENGTH: 64` for Branch A;
there is deliberately no total-length cap). First-time-seen children are pushed at
`depth + 1` with parent and move recorded for path reconstruction. The seam filter and
the hoisting of source rotations out of the `k1` loop are the two efficiency tricks
inherited from the baseline solver.

**Termination and budget.** A node is "explored" when popped; the search stops when a
popped state has every relator at length exactly 1 (`solved`), or after `node_budget`
pops, or when the frontier empties (cap-pruned exhaustion). Because pop order is a
fixed total order, a budget-`B` run is *exactly* the first `B` pops of any longer run —
the budget-invariance property the verifier checks across files. (All-length-1 with a
repeated generator is impossible from our starts: `|det|` of the exponent matrix is 1 at
the start and preserved by every move, and a repeat would force det 0.)

**Stats.** `min_relator_length` / `max_relator_length` (total lengths, with the state
snapshots) update by first-crossing at push time; `max_relator_length_expanded` tracks
the largest total ever *popped*. A `progress` callback fires every 1,024 pops and is
result-neutral.

**Measured throughput** (M-series MacBook CPU, single core, budgets ≤ 1,000 at
`n_gen = 3`, cap 64): 1,659–2,061 nodes/s across the four evidence files. A full 50,000
budget on an unsolved job at that rate ≈ 25–30 s.

**HIGH_SPEEDUP: `search_n_fast` (`../solvern_fast.py`).** `HIGH_SPEEDUP: true` in the
config swaps `search_n` for its fast twin — the same search with fused bookkeeping.
Profiling showed ~70% of `search_n`'s wall time is per-child *Python* work (the relator
sort, the tie-break byte-packing, tuple conversions), so the fast solver does
expansion + canonicalisation + relator-sort + key-packing in ONE `@njit` kernel call
per pop and carries states as packed bytes (the packed key IS the heap tie-break —
injective, so the pop order is provably identical). It keeps parent/move pointers, so
**every result field is bit-identical, paths included** — whole-dict equality is
pinned by `tests/greedy/test_solvern_fast.py` (parity at n_gen 2–5,
spec trace-equality, kernel-vs-loop child-order equality, abs_det on every kernel
child) and the fast/slow micro-run row-equality test in `test_run_nocov.py`.
Result-neutral ⇒ NOT part of the filename identity: files written in either mode
resume each other. Measured at budgets ≤ 1,000 (M-series, cap 64): **4.6–5.9×** —
e.g. ms527+xy 1,972 → 9,981 nodes/s, AK(3)+xxxYYYY 3,010 → 13,933 nodes/s.

## 5. The runner: `run_nocov.py`

`run_nocov(cfg, node_budget, family)` runs one sweep = one output file. `main()` loops
`for budget in BUDGET: for family in FAMILIES:` — with the default config that is
3 files per budget entry.

**Job list.** Benchmark rows (after optional `NAMES` filter / `ROW_LIMIT` slice) ×
family words (after optional `WORD_LIMIT`), in deterministic order. One job =
`(benchmark row, z_word)`; for each, `nocov_presentation(r1, r2, w)` builds the
3-generator start and `search_n` runs at the sweep's budget.

**Filename = search identity.** Output stem
`nocov_{benchmark}_{family}_{budget}_mrl{cap}_{cyc|noncyc}_{mm_dd_yy}.jsonl`, e.g.
`nocov_combined_11_A1_50000_mrl64_cyc_07_14_26.jsonl`. Everything that changes a
*result* is in the prefix; the date is **not** — resume globs `prefix*.jsonl` and
reattaches to the file with the most rows, whatever day it started. Knobs that only
change *which jobs exist* (`ROW_LIMIT`, `WORD_LIMIT`, `NAMES`, the family knobs) are
also excluded, because resume is keyed per row: a job is skipped iff its
`(name, z_word)` pair is already in the file. So a capped smoke file and a full
production run share one file safely.

**Crash safety.** Before anything opens the files for append, `_repair_jsonl` truncates
a torn trailing line (crash mid-write is the normal failure mode and must not poison
the file). Every row is written + flushed + `fsync`ed individually (`_persist`). On
resume, a torn *final* line is tolerated with a warning; a bad line anywhere else is
real corruption and raises. On Colab with `MOUNT_DRIVE: true`, appends go to a local
`_stage/` copy (Drive's long-idle append handles silently drop rows) and the whole file
is mirrored onto Drive every 60 s and once more in a `finally:` on any exit; a fresh VM
re-seeds its stage from the mirror before reading anything.

**Budget guard.** Any budget > 1,000 refuses to run unless `ACSOLVERX_ALLOW_BIG=1` is
set — production budgets belong on Colab (the notebook RUN cell sets the variable;
local shells must not).

**W&B** (production on, local off): entity `avigyapaudel045-aisc`, project `acsolver`,
`job_type: stable_ac_nocov`, group defaulting to `combined_11-nocov-mrl64-cyc`, run name
like `A1 · 50000 · combined_11 · nocov`. The run id is derived from the date-less
filename prefix with `resume="allow"`, so a Colab disconnect reattaches to the same run.
Per job it logs `run/solve_rate`, `run/n_solved`, `run/cum_nodes`, `run/nodes_per_s`
against a monotone `n_processed` step; at finish it writes `run.summary`
(`n_rows, n_solved, solve_rate, newly_solved_reach, cum_nodes, total_time`), a results
`wandb.Table`, and uploads both jsonls as an artifact. None of this touches the search.

## 6. Output schema

One row per job in the results jsonl. Keys, in order:

- **identity/context**: `name`, `source` (`"ladder"|"reach"`), `pres_id` (null for
  reach), `r1`, `r2`, `base_total_length`, `z_word` (the `w` searched), `z_relator`
  (`"Z"+w`, the third relator as searched), `w_family` (`A1|A2|A3`), `mode` (`"nocov"`),
  `n_gen` (3), `n_rel` (3), `benchmark`, `node_budget`, `max_relator_length_cap`,
  `cyclic_reduce`.
- **results**: `nodes_explored`, `solved`, `path_length` (null when unsolved),
  `min_relator_length`, `min_relator`, `max_relator_length`, `max_relator`,
  `max_relator_length_expanded`, `max_relator_expanded`, `time_seconds`.
- **provenance**: `git_commit` — full 40-hex HEAD of the checkout that produced the row
  (null outside a git repo). Deliberately *not* part of the filename/resume identity:
  rows appended after a code update record the new commit in the same file, which is
  the audit trail wanted. (The committed 07/13 evidence rows predate this field and
  the `nodes_1M`/`path_1M` passthrough; every row written by the current code carries
  them.)
- **baseline passthrough** — ladder rows: `baseline_nodes_at_50k`,
  `baseline_path_at_50k`, `baseline_solved_at_50k`, plus `nodes_1M` / `path_1M` (the
  1M-budget ground truth — every ladder row solves there); reach rows: `bar_to_beat`,
  `start_length`, `aut_min_rep_r1`, `aut_min_rep_r2`. Analysis compares in place, no
  join back into the benchmark file — at ANY run budget, for any combined benchmark
  (the passthrough keys on `source`, not on which combined file).

  **Was this presentation solved by the 2-gen greedy at my budget B?** Every row
  answers it exactly, via budget invariance (solved with `n` nodes ⟹ solved with the
  same `n` at every budget ≥ `n`):

  - *ladder, `baseline_solved_at_50k: true`* — yes at every B ≥ that node count;
    `baseline_nodes_at_50k` / `baseline_path_at_50k` are the exact numbers to beat.
  - *ladder, `baseline_solved_at_50k: false`* (the 50k columns are censored at 50,000)
    — solved at B iff `nodes_1M ≤ B`, and then in exactly `nodes_1M` nodes. Example,
    `combined_66` at B = 500,000: 12 of its 60 ladder rows are censored at 50k; ten
    have `nodes_1M` between 59,710 and 272,953 (baseline solves them at 500k), two sit
    at 574,348 and 574,959 (baseline does NOT solve them at 500k — beating those two
    at 500k is a strict win). For `combined_11`, ms625 (78,770) and ms637 (271,866)
    both fall below 500k.
  - *reach* — the baseline never solved these at budget 1,000,000, so it is unsolved
    at every B ≤ 1M by construction; any `solved: true` here is new, full stop.

Solved jobs additionally append one row to the sibling `*_paths.jsonl`:
`{name, z_word, r1, r2, z_relator, path_moves}`. `path_moves` is a list of
`"i_j_s_k1_k2"` strings — 0-based target `i`, source `j`, sign `s`, rotations
`k1, k2` — and is decoded **only by replay** (`solvern.moves_to_states`), never by
diffing states. Example first row of the A1@100 paths file: `ms499`, `z_word: "x"`,
`z_relator: "Zx"`, 6 moves starting `2_1_-1_0_0, 2_1_-1_0_0, …`.

## 7. Verification (what makes a `solved: true` believable)

Two independent layers:

1. **Tests.** `tests/stable_ac/test_run_nocov.py` (collected by `pytest
   tests/stable_ac -q`, with `test_cov.py`) covers the row schema, resume
   skipping, torn-line repair, filename identity, yaml sanity, the budget guard, and one
   real budget-100 micro-run. The solver itself is pinned in
   `tests/greedy/` — `test_solvern.py` proves trace-equality with the
   pure-Python spec at `n_gen ≤ 3` plus 4-generator seamlessness (752 tests fast tier,
   796 with `--runslow`).
2. **Certificates.** Every `solved: true` row is a claim; its `path_moves` is the proof.
   `.venv/bin/python3 -m experiments.stable_ac.verify_results` replays every certificate
   through `greedy_tests/spec/` **only** (never a solver — a solver bug or a gamed test
   suite cannot self-certify), checking move legality, the 64-cap at every intermediate
   state, a genuinely trivial endpoint, `|det|` preservation, `path_length` consistency,
   the identity binding `z_relator == "Z" + z_word`, and cross-file **budget
   invariance** (a job solved at budget B must be identically solved at every larger
   budget in any other file). Exit non-zero on any bad certificate. Standing count as of
   2026-07-13: **ALL 399 SOLVED-ROW CERTIFICATES VERIFY** (2,680 rows, 8 files — 381
   of those certificates are this pipeline's, 18 are Branch B's), 198 cross-budget
   jobs, 0 violations. Run it on any downloaded production jsonl before believing the
   numbers.

## 8. Committed local evidence (all budgets ≤ 1,000 — the local hard cap)

Four sweeps over the full `combined_11`, committed as pipeline verification:

| file | jobs | solved | rate | cum. nodes | wall time | nodes/s |
|---|---|---|---|---|---|---|
| `…_A1_100_mrl64_cyc_07_13_26` | 176 | 26 | 14.8% | 15,701 | 7.6 s | 2,061 |
| `…_A1_1000_mrl64_cyc_07_13_26` | 176 | 51 | 29.0% | 137,166 | 69.0 s | 1,987 |
| `…_A2_100_mrl64_cyc_07_13_26` | 2,111 | 275 | 13.0% | 189,703 | 114.3 s | 1,659 |
| `…_A3_100_mrl64_cyc_07_13_26` | 173 | 29 | 16.8% | 15,335 | 9.1 s | 1,691 |

Reading of the A1 pair (same jobs, budgets 100 vs 1,000): the 26 solved at 100 are a
strict subset of the 51 solved at 1,000, with identical stats — the budget-invariance
property, live. At budget 1,000 the solves concentrate exactly where the baseline says
they should: ms499 16/16 words, ms165 16/16, ms303 11/16, ms491 8/16, everything from
bin 4 up 0 — a budget of 1,000 simply isn't enough there, as expected. AK(3): 0 solves
in all 102 attempts at ≤ 1,000 (nobody expected otherwise — that is what the 50k+
Colab budgets are for). Solved path lengths observed: 6–27 moves at budget 100,
6–74 at budget 1,000.

## 9. Running it

**Production (Colab)** — open `experiments/stable_ac/nocov/stable_ac_nocov.ipynb` on
branch `test/stable-ac-moves-w4`; three cells:

1. **CONFIG** — `BRANCH`, `BUDGET` (production default `[50000]`), loads
   `config_nocov.yaml`, merges the inline `OVERRIDES` dict.
2. **SETUP** — clone/reset the repo at `BRANCH`, purge stale `sys.modules`, mount
   Drive, W&B login via Colab Secret, `pip install pyyaml`.
3. **RUN** — sets `ACSOLVERX_ALLOW_BIG=1`, then `run_nocov(cfg, budget, family)` for
   every (budget, family).

Output lands in `/content/drive/MyDrive/acsolverx_results/stable_ac/nocov/`; a
disconnect loses nothing (stage + mirror + row-keyed resume: re-running the RUN cell
reports `N already done, M to run`).

**The production config as committed** targets `combined_66` (60 ladder + 6 reach —
the full benchmark) at `BUDGET: [10000]` with `A2_MAX_WORDS: 64` and the families
ordered `[A1, A3, A2]`: A1 = 1,056 jobs and A3 = 1,040 finish first, then A2 = 4,175 —
**6,271 searches total**, worst case ≈ 62.7M nodes. With `HIGH_SPEEDUP: true` (the
committed default, ~5×: §4) the observed Colab range 0.9–2.1k nodes/s becomes
≈ 4.5–10k, so worst case ≈ **1.7–4 h** (8.7–17.4 h without it; expected less either
way — solved jobs stop early). The ladder comparison is exact at
10k despite the 50k snapshot columns, via `nodes_1M`: baseline solves at B iff
`nodes_1M ≤ B`. Both knobs are result-neutral for resume (they only change which jobs
exist; rows are keyed `(name, z_word)`), so the cap can be raised later — only newly
admitted words run — and a later 50k sweep is simply a new set of per-budget files.
For scale at 50k: cap 64 → 44–87 h, cap 100 → 58–115 h, uncapped → 94–187 h.
`A2_DROP_LEN1: true` because A1 already runs the four singles on every row: dropping
them from A2 removes the systematic cross-family duplication and, where the cap binds,
admits more distinctive prefix words in their place (at cap 64 the remaining
accidental overlap is 197 jobs — 156 A1∩A2 short mixed words + 41 A2∩A3 cells). That
remainder is left alone by design: the search is deterministic, so duplicate
`(name, z_word)` jobs across family files carry identical rows — merge-dedup at
analysis time is lossless, whereas runner-side cross-family skipping would couple the
files and break each sweep's self-containment. Worst case ≈ 314M nodes ≈ 44 h at 2,000 nodes/s (87 h at 1,000 — Colab CPUs
are slower than the local M-series); the row-keyed resume makes it safe to spread over
any number of Colab sessions, per family and mid-family alike.

**Cost at `BUDGET: [50000]` on `combined_11`** (yaml overridden back to it): 2,460
searches. Worst case —
every job burning the full budget — is 123M nodes ≈ 17 h single-core at the measured
~2,000 nodes/s; the real number is meaningfully lower because the easy half of the
ladder solves in ≤ a few hundred nodes per word (at budget 100 alone, 13–17% of jobs
already solve). A2 is 86% of the cost — `A2_MAX_WORDS: 64` cuts the sweep to 1,053
searches (≈ 7.3 h worst case) and is the first knob to reach for. One jsonl per
(budget, family): a full default sweep writes 3 results files + 3 paths files.

**Local smoke run** (never above budget 1,000):

```bash
.venv/bin/python3 -c "
import yaml; from experiments.stable_ac.nocov.run_nocov import run_nocov
cfg = yaml.safe_load(open('experiments/stable_ac/nocov/config_nocov.yaml'))
cfg.update({'USE_WANDB': False, 'MOUNT_DRIVE': False})
run_nocov(cfg, 100, 'A1')"
```

**Afterwards, always:**

```bash
.venv/bin/python3 -m experiments.stable_ac.verify_results   # certificates + invariance
```
