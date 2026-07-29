# Solved-1hop Aut-clean @ 100k — ship / layout

**Branch:** `cursor/heur-12h-anti-overfit-a42e`  
**Colab tip that produced the chunks:** `9279591`  
**Actual budget:** **100,000** (folder was briefly misnamed `hsearch_solved1hop_1m/`).

## Layout

```
results/heuristic_search/hsearch_solved1hop_100k/
  chunks/c{1..5}of5_solved_1hop_autclean_b100000_mrl48.{jsonl,md}
  merged_solved_1hop_autclean_b100000_mrl48.jsonl
  residual_unsolved_100k.json
  RESULTS.md
  SHIP.md
```

## Dataset

| | |
|---|---|
| Freeze | `results/heuristic_search/splits/solved_1hop_autclean.json` |
| Kept | **432** (seed=58, moved_cov=374, short_relator=38) |
| selected_on | AC1M-hard tune + campaign S-grid/arms + scale10k |
| evaluated_on | this freeze |

## Run knobs (as executed)

| knob | value |
|---|---|
| NODE_BUDGET | `100_000` |
| MAX_RELATOR_LENGTH | 48 (per-relator) |
| ENGINE | hcompact |
| N_WORKERS | auto |
| ARMS | baseline, s12, s28, s20_mk2, s24_k1_mk2 |
| Job order | presentation-major |

## Verify

```bash
.venv/bin/python3 -m experiments.heuristic_search.verify.verify_solved1hop_certs \
  results/heuristic_search/hsearch_solved1hop_100k/merged_solved_1hop_autclean_b100000_mrl48.jsonl
```

Must print all solved certificates replay. Do not publish a solve that fails.

## Next (optional 1M escalation)

Escalate **every** cell in `residual_unsolved_100k.json` (140 cells), not a subsample.
Keep mrl=48; pin `N_WORKERS=4` at 1M if deep cert-recovery RAM spikes.
