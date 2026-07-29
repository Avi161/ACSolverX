# Solved-1hop Aut-clean @ 1M — ship note

**Branch:** `cursor/heur-12h-anti-overfit-a42e`

**ac-advisor:** REVISE on first plan → addressed before ship (Aut-clean freeze,
presentation-major jobs, certificate verifier, complete-row denominator).

## Dataset

| | |
|---|---|
| Freeze | `results/heuristic_search/splits/solved_1hop_autclean.json` |
| Kept | **432** (seed=58, moved_cov=374, short_relator=38) |
| Supersedes | `solved_1hop_nob60.json` (477; had 45 Aut leaks into selection surfaces) |
| selected_on | AC1M-hard tune train + campaign_12h S-grid/arms + scale10k slices |
| evaluated_on | this freeze |

These rows present the trivial group via *stable* CoV from solved MS seeds.
The search tests *unstable* trivializability — do not call them AC-trivial by
construction. Eval searches the `aut_min` representative.

## Arms (same weights as bench60 1M)

`baseline`, `s12`, `s28`, `s20_mk2`, `s24_k1_mk2`

Always report Δ vs length baseline at the same budget, on **complete rows**
(all five arms present). Stratify seed / moved_cov / short_relator.

## Colab notebooks (5 chunks)

```
experiments/heuristic_search/hsearch_colab_solved1hop_1m_c{1..5}.ipynb
```

| knob | value |
|---|---|
| BRANCH | `cursor/heur-12h-anti-overfit-a42e` |
| NODE_BUDGET | `1_000_000` |
| ENGINE | `hcompact` |
| N_WORKERS | `auto` (~6 on 50 GB / 8 cores) |
| CHUNKS | 5 (~87/87/86/86/86) |
| DRIVE_DIR | `/content/drive/MyDrive/acsolverx/hsearch_solved1hop_1m` |
| Job order | presentation-major |

Open each notebook from GitHub on this branch → Runtime → Run all.
Restart → Run all resumes (UPDATE_REPO + flock + RESUME).

## After Colab

```bash
# merge chunk jsonls (same merge helper as bench60; pin glob to _b1000000_mrl48)
python3 -m experiments.heuristic_search.verify.verify_solved1hop_certs \
  results/hsearch/hsearch_solved1hop_1m_*_b1000000_mrl48.jsonl
```

Do not publish any solve that fails certificate replay.

## Local mini (plumbing only — not a ranking)

```bash
.venv/bin/python3 -m experiments.heuristic_search.runners.mini_solved1hop_b50
```

Budget 50, 8 strided orbits × 5 arms. Do not promote any arm from this run.
