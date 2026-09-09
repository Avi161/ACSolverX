# What is still unsolved after budget 100,000 — the run list

**For a cloud agent picking this up cold.** Everything needed to launch the next budget
lift is in this file: the exact presentations, their relators, the notebook, and the five
config lines to change.

Branch: **`experiments/ppo`** (this branch). The 100k result files under
[`../hsearch_ac19_hard100k/`](../hsearch_ac19_hard100k/) existed **only on one laptop's local
`main`** until this commit — they are on no other branch. Do not delete them.

## The two residuals

| arm | ordering | still unsolved @100k | run list (CSV, ready to run) | names |
|---|---|---:|---|---|
| `baseline` ("greedy") | total length | **221** (+1, see below) | [`unsolved_100k_baseline.csv`](unsolved_100k_baseline.csv) — 222 rows | [`.txt`](unsolved_100k_baseline.txt) |
| `s20_mk2` ("heuristic") | `L + 20·S + 2·MK` | **39** | [`unsolved_100k_s20_mk2.csv`](unsolved_100k_s20_mk2.csv) — 39 rows | [`.txt`](unsolved_100k_s20_mk2.txt) |

The 39 are a **subset** of the 221 — both arms fail on the same 39; `s20_mk2` recovers 182 of
length's failures and loses none the other way.

### Why the baseline CSV has 222 rows, not 221

`RESULTS.md` scores over the **common denominator** of 70,723 orbits both arms searched at 10k
(`baseline` 71,556 rows, `s20_mk2` 71,582 — the sets differ). Exactly one baseline failure,
**`ac19_33435`**, sits outside that intersection: `s20_mk2` never searched it at 10k. So
221 = common-set count, 222 = every orbit `baseline` actually failed. The CSV ships all 222 —
drop `ac19_33435` if you need to stay on the common denominator.

## The 39 (both arms, the genuinely hard tail)

```
ac19_7284  ac19_10584 ac19_12445 ac19_14060 ac19_16286 ac19_20270 ac19_26211 ac19_26598
ac19_27254 ac19_27551 ac19_27683 ac19_28131 ac19_28930 ac19_31298 ac19_36350 ac19_39288
ac19_40312 ac19_42768 ac19_43611 ac19_44381 ac19_45019 ac19_45978 ac19_46363 ac19_49095
ac19_50841 ac19_51034 ac19_54616 ac19_54765 ac19_54835 ac19_55019 ac19_57992 ac19_59576
ac19_65206 ac19_65753 ac19_67055 ac19_68854 ac19_70028 ac19_72113 ac19_72328
```

## Presentation data

Both CSVs carry the presentations inline, in the **same schema the runner already reads**
(`load_hard_rows` in
[`experiments/heuristic_search/runners/run_ac19_hard_residual_100k.py`](../../../experiments/heuristic_search/runners/run_ac19_hard_residual_100k.py)):

```
name,r1,r2,n_members,members,nodes_explored,min_relator_length
ac19_7284,YYXXXyXX,YXyxYXXXyxx,3,8769 16286 101025,100000,17
```

- `r1`, `r2` — the relators. Upper = generator, lower = inverse (`X`=x, `x`=x⁻¹, `Y`=y, `y`=y⁻¹).
- `n_members`, `members` — the Aut(F₂) orbit this row represents and its members' indices into
  `data/AC19_extended.txt`. **These are Aut-minimal representatives**; difficulty is not
  orbit-invariant, so a failure here is a failure *for this representative*.
- `nodes_explored` — always 100,000 (the budget it exhausted). `min_relator_length` — the
  shortest relator reached, i.e. how close it got.

No join is needed. Source of truth for the presentations is
[`data/AC19_extended_aut_min.csv`](../../../data/AC19_extended_aut_min.csv) (72,779 orbits).

## How to run the next lift

Use the arm's existing single-arm notebook — do not write a new one:

| arm | notebook |
|---|---|
| `baseline` | [`experiments/heuristic_search/hsearch_colab_ac19_hard100k_baseline.ipynb`](../../../experiments/heuristic_search/hsearch_colab_ac19_hard100k_baseline.ipynb) |
| `s20_mk2` | [`experiments/heuristic_search/hsearch_colab_ac19_hard100k_s20_mk2.ipynb`](../../../experiments/heuristic_search/hsearch_colab_ac19_hard100k_s20_mk2.ipynb) |

Open in Colab → Runtime → Run All. In **cell 0 (CONFIG) only**, change these five, e.g. for
`s20_mk2` at 1M:

```python
BRANCH    = "experiments/ppo"                  # was cursor/heur-12h-anti-overfit-a42e
DRIVE_DIR = "/content/drive/MyDrive/acsolverx/hsearch_ac19_hard1m_s20_mk2"
cfg["NODE_BUDGET"] = 1_000_000
cfg["CHECKPOINTS"] = [100, 250, 500, 1000, 2500, 5000, 10000, 25000,
                      50000, 100000, 250000, 500000, 1000000]
cfg["HARD_CSV"]  = "results/heuristic_search/ac19_autmin_screen/unsolved_100k_s20_mk2.csv"
cfg["DATASET"]   = "ac19_unsolved100k_s20_mk2"
cfg["OUT_STEM"]  = "hsearch_ac19_hard1m_s20_mk2"
```

Leave `ENGINE="hcompact"`, `MAX_RELATOR_LENGTH=48`, `RESUME=True`, `N_WORKERS="auto"` and
`ARMS` alone — the notebook asserts the arm and the engine, and `MAX_RELATOR_LENGTH` is a
space bound, not a speed knob (lowering it can only reduce the solve rate).

A search at budget *B* is exactly the first *B* pops of any longer search, so `solved_at` and
`nodes_explored` from a longer run are **true totals** and splice onto these without adjustment.
39 searches at 1M is a small job; 222 is the larger one.

## Caveats carried forward (from the 10k `ac-advisor` review)

- Aut-**minimal representatives** — difficulty is not orbit-invariant.
- Stratify L > 19 in any write-up.
- Exclude the 142 selection-overlap names when scoring `s20_mk2` against `baseline`.
- Path length is **not** improved by `s20_mk2` (~13% longer certificates). The gain is node
  efficiency only — do not claim shorter proofs.

## Provenance

- 10k wave: [`../hsearch_ac19_autmin_1k/`](../hsearch_ac19_autmin_1k/) (5 chunks × {1k, 10k}), run 2026-07-31.
- 10k residual lists: `unsolved_10k_{baseline,s20_mk2,s20_f4,s20_mk2_mK2}.csv`, plan in
  [`HARD_RESIDUAL_100k.md`](HARD_RESIDUAL_100k.md).
- 100k wave: [`../hsearch_ac19_hard100k/RESULTS.md`](../hsearch_ac19_hard100k/RESULTS.md), pulled 2026-08-04.
- This index derived from those jsonl by re-reading `solved == false`; counts verified against
  `RESULTS.md` (609/831 and 220/259 solved).
