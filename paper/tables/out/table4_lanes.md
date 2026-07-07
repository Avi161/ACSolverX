| Lane | Method | Trials/Probes | Solved | Floor reached |
|---|---|---|---|---|
| A: MITM | Meet-in-the-middle ball search from AK(3)/P25 (targets = 1,177 certified stably-trivial states) | 2 @ 2,000,000 nodes/side | 0/2 | 13 |
| B: StableSolver | Best-first search over substitution + stabilize + eliminate moves | 6 @ 300k-800k nodes | 0/6 | 13 |
| C: trivial-z | n-generator (n=3,4,5) trivial-z stabilization + plain greedy substitution, rep & textbook forms | 6 @ 800k-2,000,000 nodes | 0/6 | 14-16 (rep_n3=14, rep_n4=15, rep_n5=16, textbook_n3=14, textbook_n4=15, textbook_n5=16) |
| D: plateau-elim | Harvest visited stabilized states, Lemma-11 eliminate, dedupe by signed-relabel symmetry, greedy re-solve every fresh 2-gen quotient | 16,870 trials / 6,058 distinct (180,645 harvested) | 0/16,870 | 13:16,844; 19:23; 20:3 |
| E: RL beam | Beam search with a pretrained 2-generator PPO policy (zero-shot), widths 512 and 2048 | 155 + 30 | 0/155 + 0/30 | n/a (beam search records no min-total-length floor) |

*Note: Trials/Solved/floor counts for lanes A-D are computed directly from archive/campaign_grid_probes.jsonl.gz (A, B, C) and archive/campaign_trials.jsonl.gz (D), cross-checked against collect_summary.json's authoritative totals (trials=16870, candidates=180645, grid_probes=14); all matched.*

*Note: Lane D's source-facet breakdown (trial counts): laneD:D1=5866, laneD:D2=5350, laneD:D3=5497, resolve=157.*

*Note: Lane E counts are row counts of runs/beam_laneD_floor.csv (155) and runs/beam_laneD_floor_w2048.csv (30); both have solved=False on every row.*
