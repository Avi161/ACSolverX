# K=4 nonsym beam → s20_mk2 vs length-greedy @1k (bench60)

Same climb jsonl as the K=4 sweep (`covbeam_nonsym_beam_k4_climb_subset60.jsonl`): nonsym CoV beam, Aut-min every hop, global visited, K=4. Only the terminal search ordering changes.

`s20_mk2` = `L + 20·S + 2·MK`. Budget 1000.

## Solve rates

| arm | solved |
|---|---:|
| shipped `b1k_greedy` (original) | **29**/60 |
| shipped `b1k_heur` (RECOMMENDED, original) | **43**/60 |
| shipped `b1k_covgreedy` (oracle CoV) | **45**/60 |
| K=4 beam → **length-greedy** @1k | **49**/60 |
| K=4 beam → **s20_mk2** @1k | **49**/60 |

- Both solve: 49/60
- Length only: —
- s20_mk2 only: —
- Mean nodes on both-solved intersection (n=49): length 36.1, s20_mk2 26.7

Wall 16.0s. Artifacts: `covbeam_nonsym_beam_k4_s20mk2_b1k_subset60.*`.

Controls loaded from `/workspace/results/comparison/cov_heur_b1k_subset60.csv` (not re-run).
