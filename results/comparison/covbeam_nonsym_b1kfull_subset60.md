# Non-automorphic CoV beam → best_rep, then greedy@1000 (CoV cost EXTRA)

- Control: shipped `b1k_greedy_*` from cov_heur_b1k_subset60.csv (**not re-run**).
- CoV beam: n_subs>1, Aut-min after every hop, visited=Aut-min orbits.
- This table gives each start a full 1000-node greedy from best_rep; CoV wall is **not** deducted (secondary / non-matched).
- Cost-matched B_rem arm (prior artifact): **17/60** solves.

## Headline (full 1k from best_rep)

- shipped greedy@1k (original): **29/60**
- greedy@1k from CoV Aut-min best_rep: **41/60**
- μ-descenders: **55/60**
- new solves: ['538', '606', '544', '549', '565', '602', '632', '586', '581', '575', '628', '633']
- lost solves: —
- both-solved: 29; mean nodes ctrl/treat: 175.5 / 17.3

Artifacts: `results/comparison/covbeam_nonsym_b1kfull_subset60.jsonl`, `results/comparison/covbeam_nonsym_b1kfull_subset60.csv`

Unsolved ≠ counterexample. CoV prefix stably AC only.
