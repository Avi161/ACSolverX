# `data/` — the input presentations

Everything a search reads as a *starting point*. Nothing here is ever written by a run: run outputs go to [`results/`](../results/README.md), and the frozen evaluation set built from them is [`benchmark/`](../benchmark/README.md).

## Encoding

Every `.txt` file here is one presentation per line, as a flat list of ints:

```
[r1 padded to max_relator_length | r2 padded to max_relator_length]
```

so `max_relator_length = len(line) // 2`. The alphabet is `1 = x`, `-1 = X`, `2 = y`, `-2 = Y`, `0 = pad`. The 24-int relator slots in `ms640_solved.txt` are a property of **that file's layout**, not a fixed constant of the algorithm — the per-relator cap is a knob (`MAX_RELATOR_LENGTH`), and re-padding a presentation when you change it is what `envs/utils.py:change_max_relator_length_of_presentation` is for. Never hand-roll the re-pad.

| file | rows | what it is |
|---|---|---|
| `ms640_solved.txt` | 640 | the Miller–Schupp presentations the baseline greedy solves. `max_relator_length = 24`. The workhorse input for the greedy pipeline. |
| `1190MS.txt` | 1,190 | the full Miller–Schupp series the 640 and the unsolved reps are drawn from. |
| `AC19.txt` | 140,535 | the AC19 corpus. |
| `AC19_extended.txt` | 156,762 | AC19 plus the extension. |
| `AC1M.txt.gz` | — | the 1M-presentation corpus, shipped **compressed**. The decompressed `data/AC1M.txt` is gitignored on purpose — decompress locally, never commit the result. |

## `ms_unsolved_reps/` — the hard residual

The presentations the baseline greedy does *not* solve, plus the derived structure that showed there are fewer distinct problems here than there are rows.

| file | what it is |
|---|---|
| `ms_reps_unsolved.txt` / `.csv` | the 261 unsolved representatives |
| `ms_reps_126.txt` | 126 lines — the 261 collapsed under the equivalence search. The class count is not a single number to quote loosely: 126 here, 125 once a raised length ceiling exposed a further merge, 168 up to change of variables. Read [the finding](../results/equivalence_classes/EQUIVALENCE_FINDING.md) and [the proofs](../results/equivalence_classes/PROOFS.md) before citing any of them |
| `aca_124.csv` | the 124 distinct classes under AC moves — the residual every escape experiment is pointed at |
| `aca_124_best.csv` | **the drop-in twin of `aca_124.csv`** — same five columns, byte-identical on the 85 unreduced classes, `r1`/`r2` swapped to the reduced pair on the 39 reduced ones (2446 → 2356 total letters). Anything that loads `aca_124.csv` loads this unchanged, which is the whole point: it carries no reduction bookkeeping. Read `aca_124_reduced.csv` to find out *which* rows moved and on which criterion — 3 of the 39 swaps are same-orbit re-spellings at identical `mu` |
| `aca_124_reduced.csv` | `aca_124.csv` + a reduction verdict per class: `reduced` yes/no, `reduce_kind`, `mu_in`, `mu_out`, `new_r1`, `new_r2`, `n_hops`, `source`, `ext_label`; the 85 unreduced carry `none`. **Read `reduce_kind`, not `reduced`** — 39 rows say yes but on two incomparable criteria: **36** are `mu_floor` (the μ-ladder reached a strictly lower Aut-orbit floor, `mu_out < mu_in`, each re-verified against the pure-Python `aut_canon`) and **3** are `length_only` (an external table shortened one member's spelling; `aut_canon` puts the finish at `mu_out == mu_in`, i.e. the same orbit, zero orbit distance). All 124 class reps are themselves Aut-canonical, so `mu_in` is equally the rep's raw length. A solve from a `mu_floor` start certifies **stable** AC-triviality of the class; a `length_only` start certifies nothing new. Written by `experiments/stable_ac/cov/ladder/export_aca124_reduced.py` |
| `ak3_only.csv` | AK(3) alone. Its stable triviality is **OPEN**; nothing in this repo treats it as settled |
| `ms_solved_grid.csv` | which (budget, config) solved which presentation |
| `mu_descents_d2.csv` / `mu_descents_d4.csv` | the depth-2 and depth-4 μ-descent maps from the orbit-floor scan |
| `mu_floors_r8.csv` | the rung-8 μ-floor census |

## `cov/unique_aut_orbits_1hop/`

The single-hop change-of-variables orbit census: which `Aut(F₂)`-orbits each residual class can reach in one CoV hop, with the parent/edge/class tables and the run log that produced them. Written once by `experiments/stable_ac/cov/run/unique_aut_orbits_1hop.py`; consumed as an input by the μ-ladder and the orbit→greedy pilot.

## Reading a file

Scripts locate this directory by walking up until they see both `experiments/` and `data/` — never by counting `os.path.dirname()` levels, which bakes in a file's depth and silently repoints the moment that file moves.
