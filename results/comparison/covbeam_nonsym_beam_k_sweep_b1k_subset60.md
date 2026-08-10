# Nonsym CoV beam — K sweep @ greedy budget 1,000 (bench60)

Algorithm: non-automorphic CoV → Whitehead Aut-min → keep top-K → repeat until μ≤12 / closed / `max_aut_canon=1000`; then length-greedy @ 1000 from Aut-min `best_rep`.

Controls (loaded, not re-run) from `/workspace/results/comparison/cov_heur_b1k_subset60.csv`: greedy 29/60, heur 43/60, covgreedy 45/60.

## Sweep

| K | hits_stop (μ≤12) | greedy@1k solved | descended | mean n_aut_canon | wall_s |
|---:|---:|---:|---:|---:|---:|
| 1 | **34**/60 | **44**/60 | 53/60 | 131.0 | 26.9 |
| 2 | **39**/60 | **47**/60 | 53/60 | 204.6 | 28.9 |
| 4 | **43**/60 | **49**/60 | 53/60 | 367.9 | 39.4 ← best |
| 8 | **41**/60 | **45**/60 | 53/60 | 467.1 | 46.4 |
| 10 | **39**/60 | **43**/60 | 53/60 | 501.1 | 50.7 |
| 16 | **37**/60 | **43**/60 | 53/60 | 572.2 | 57.9 |
| 32 | **28**/60 | **42**/60 | 53/60 | 650.2 | 73.2 |

**Best K = 4** by greedy@1k solve rate (49/60), tie-break hits_stop=43/60, then smaller K.

Larger K is worse under `max_aut_canon=1000`: the rung-local beam spends the Whitehead budget expanding a wider rim and under-descends (hits_stop 43→28 from K=4→32; greedy 49→42). Same lesson as rung-local-beam-abandons-the-low-shell — here the binding knob is the Aut-min call cap, not depth.

Vs shipped @1k: greedy 29, heur 43, covgreedy 45; best beam K=4 → greedy@1k from best_rep **49/60** (matches prior best-first α=0 full1k).

Claim hygiene: μ≤12 is a *stable*-AC-triviality lead (MU_CRITERION), not an AC solve. Greedy solves certify the Aut-min start is AC-trivial within budget; source is stably AC-trivial via Prop A + Thm 3 + path.

Next: freeze **K=4**, raise greedy budget to 10k on Colab
(`hsearch_colab_covbeam_nonsym_b10k.ipynb` after regenerating climb
jsonl with `climb_beam(..., beam_k=4)`).

Wall 323.3s. Artifacts: `covbeam_nonsym_beam_k_sweep_b1k_subset60.*`.
