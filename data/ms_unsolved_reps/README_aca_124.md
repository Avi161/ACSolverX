# The 124 unsolved ACA classes — initial, reduced, and best-known

Three views of the same 124 rows (`aca_0` … `aca_123`), the ACA classes of the
550 unsolved Miller–Schupp presentations. Keyed by `name`; `members` lists the
**A-equivalence class representatives** merged into each ACA class, not the raw
cells — the 124 `n_members` sum to **261**, the rep count of CLAUDE.md §4, and
the column matches `reps` in `results/equivalence_classes/ms1190_tables/
unsolved_124_aca_classes.csv` row for row (that table's `n_cells` is what sums
to 550). So these files record the 261 → 124 step. Copied from
`experiments/ppo` (`data/ms_unsolved_reps/`) — see `docs/BRANCH_MAP.md`.

| file | columns | what it holds |
|---|---|---|
| `aca_124_initial.csv` (source name: `aca_124.csv`) | `name,r1,r2,n_members,members` | the presentations **as first found** — no reduction applied |
| `aca_124_reduced.csv` | + `reduced,reduce_kind,mu_in,mu_out,new_r1,new_r2,n_hops,source,ext_label` | the reduction record: which rows moved, by how much, and from where |
| `aca_124_best.csv` | `name,r1,r2,n_members,members` | **the one to actually use.** Same schema as `initial`, with the 36 reduced rows substituted in — initial and reduced collapsed into one drop-in table |

## Why three files

`initial` and `reduced` are the inputs; `best` is the answer.

- `initial` — where each class started.
- `reduced` — the **ledger**: one row per class saying whether it moved, by how
  much, over how many AC moves, and from which run. Provenance, not a working
  table; `r1`/`r2` here are still the initial words.
- `best` — the **result**: `initial` with the 36 reductions applied. Nothing in
  it that isn't derivable from the other two, but it's the file you point a
  solver at, so you don't re-join two tables every time.

If you only keep one, keep `best`. If you need to justify a number, `reduced`.

## What the reduction did

Of the 124:

- **36 got strictly shorter** (`reduce_kind = mu_floor`, `mu_out < mu_in`).
  Source `mu_ladder_r256_b64`, `n_hops` AC moves. Total length over all 124
  drops **2446 → 2356**; the largest single drop is 25 → 19.
- **88 are untouched** (`reduced = no`); `new_r1/new_r2` are `none` and
  `aca_124_best.csv` carries the initial pair unchanged.

Equal-length rewrites are **excluded by choice**. Three classes — `aca_2`,
`aca_14`, `aca_53` — had a `length_only` rewrite from an external length table:
different words, identical total length, no gain. They have been reverted to
their initial pairs and marked `reduced = no`. Consequence: `reduce_kind` is now
only `mu_floor` or `none`, and the `source` / `ext_label` columns carry `none`
on every row (they are kept so the schema still matches the upstream file on
`experiments/ppo`, where those three rows are still rewritten).

So "the reduced ones" is **36**, unambiguously — every changed row is a strictly
shorter row.

`mu_in`/`mu_out` are total length `len(r1) + len(r2)`; both agree with the words
in `aca_124_initial.csv` and `aca_124_best.csv` on every mu_floor row.

## Caveat

The reductions come from the μ-ladder line, which `CLAUDE.md` §3 records as **not
production** — these files are a data record, not a recommended pipeline. The
124 itself is an **upper bound** from a bounded AC-move search (§4).
