# Non-automorphic CoV beam vs shipped greedy @1k (bench60)

- Control: `/workspace/results/comparison/cov_heur_b1k_subset60.csv` `b1k_greedy_*` (**not re-run**).
- Treatment: n_subs>1 CoV beam (K=10, rungs≤6), Aut-min after every hop, visited=Aut-min orbits; then length-greedy @ B_rem (cost-matched to 1000 node-eq).
- calib `node_eq_ms`=0.1174; wall 7.1s.

## Headline

- shipped greedy@1k solves: **29/60**
- covbeam + greedy@B_rem solves: **17/60**
- μ-descenders under beam: **55/60**
- both-solved intersection: **17**
- mean nodes (ctrl / treat_total_eq): 36.3 / 296.9
- median nodes (ctrl / treat_total_eq): 13.0 / 256.0

- new solves (treat yes, ctrl no): —
- lost solves (ctrl yes, treat no): ['505', '367', '331', '579', '327', '333', '380', '546', '548', '533', '589', '580']

Unsolved means unsolved within the matched budget — never a counterexample. CoV prefix is stably AC (Prop A), not AC-trivial.

Artifacts: `/workspace/results/comparison/covbeam_nonsym_b1keq_subset60.jsonl`, `/workspace/results/comparison/covbeam_nonsym_b1keq_subset60.csv`
