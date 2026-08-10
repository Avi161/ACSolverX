# Bench60 non-automorphic CoV best-first (advisor-REVISE claims)

Control arms loaded from `/workspace/results/comparison/cov_heur_b1k_subset60.csv` — **not re-run**.

## Shipped baselines @1000 / cap 24

- `b1k_greedy` (length): **29/60**
- `b1k_heur` (tuned ordering): **43/60**
- `b1k_covgreedy` (oracle CoV + length): **45/60**

## Full greedy@1000 from μ-selected Aut-min best_rep (CoV compute EXTRA / α=0)

- solves: **49/60**
- μ-descenders: **53/60**
- rows with treat_cap > 24: **19/60** (cap confound vs shipped)
- new vs `b1k_greedy`: ['609', '538', '606', '544', '549', '543', '565', '602', '632', '573', '586', '581', '575', '568', '578', '583', '628', '633', '634', '635'] (20; cap-clean among them: ['609', '538', '606', '544', '549', '543', '602', '632', '573', '568', '578', '583', '628', '633', '634', '635'])
- lost vs `b1k_greedy`: —

**Honest framing (ac-advisor):** compare against `b1k_heur` and `b1k_covgreedy` in the same CSV, not only plain greedy; state cap confound (`treat_cap>24`) and Aut-min-only control. Do **not** headline raw “+N over greedy” alone — `b1k_heur` is the free ordering baseline at cap 24.

This run: full1k-from-best_rep **49/60** vs greedy 29, heur 43, oracle-CoV 45; Aut-min-only @treat_cap 36/60; original @treat_cap 29/60.

## Cap-matched local controls @1000 (same treat_cap)

- original @ treat_cap: **29/60**
- Aut-min(original) @ treat_cap (Thm-3 relabel, no CoV): **36/60**

Attribute gains to CoV only when full1k beats **both** of these at the same cap.

Wall 74.0s. Artifacts beside this file.

Unsolved ≠ counterexample. A solve from best_rep certifies the source **stably** AC-trivial (Prop A + Thm 3 + AC path), never AC-trivial unqualified. μ-descent is structural, not a solve predictor.
