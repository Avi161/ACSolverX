# The 124 unsolved ACA classes: initial, reduced and best-known

**TL;DR.** Three views of the same 124 rows (`aca_0` … `aca_123`), the ACA classes of the 550 unsolved Miller–Schupp
presentations. **Use `aca_124_best.csv`**: the initial pairs with the 36 strict μ-ladder reductions applied (total
length over all 124: **2446 → 2356**). The reductions come from a line its branch's notes call **not production**, and
the 124 is an **upper bound** from a bounded AC-move search.

> Copied from `origin/cursor/u124-stable-ac-1b54` (this note added), itself copied from `experiments/ppo`
> (`data/ms_unsolved_reps/`). The `docs/BRANCH_MAP.md`, `experiments/ppo` and `results/` references point into that
> branch history, not this checkout.

| file | columns | what it holds |
|---|---|---|
| `aca_124_initial.csv` (source name: `aca_124.csv`) | `name,r1,r2,n_members,members` | the presentations **as first found**, no reduction |
| `aca_124_reduced.csv` | + `reduced,reduce_kind,mu_in,mu_out,new_r1,new_r2,n_hops,source,ext_label` | the **ledger**: per class, whether it moved, by how much, over how many AC moves, from which run (`r1`/`r2` are still the initial words) |
| `aca_124_best.csv` | `name,r1,r2,n_members,members` | **the one to use**: `initial` with the 36 reductions substituted in, so a solver needs no join |

**Members.** `members` lists the **A-equivalence class representatives** merged into each ACA class, not the raw
cells: the 124 `n_members` sum to **261** and match `reps` in
`results/equivalence_classes/ms1190_tables/unsolved_124_aca_classes.csv` row for row (whose `n_cells` sums to 550).
These files record the 261 → 124 step.

## What the reduction did

- **36 got strictly shorter** (`reduce_kind = mu_floor`, `mu_out < mu_in`), source `mu_ladder_r256_b64`, `n_hops` AC
  moves; the largest single drop is 25 → 19.
- **88 are untouched** (`reduced = no`; `new_r1`/`new_r2` are `none`).
- Equal-length rewrites are **excluded by choice**: `aca_2`, `aca_14` and `aca_53` had a `length_only` rewrite from an
  external length table (different words, same length) and were reverted to their initial pairs. So `reduce_kind` is
  only `mu_floor` or `none`, and `source` / `ext_label` are `none` on every row (kept so the schema matches the upstream
  file on `experiments/ppo`, where those three are still rewritten).

`mu_in`/`mu_out` are total length `len(r1) + len(r2)` and agree with the words of `aca_124_initial.csv` and
`aca_124_best.csv` on every `mu_floor` row. That the 124 is an upper bound is the source's §4.
