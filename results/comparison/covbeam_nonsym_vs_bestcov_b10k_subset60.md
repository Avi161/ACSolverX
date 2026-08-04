# Nonsym CoV-beam vs oracle best-CoV @ budget 10,000 (bench60)

Local hard cap forbids launching greedy @10k here. Numbers below are from existing artifacts only (climb+greedy@1k jsonl, one-shot covsweep@10k, shipped bestcov@10k table).

## Headlines

| arm | solves/60 | what it is |
|---|---:|---|
| nonsym beam → Aut-min `best_rep` → greedy, **proven @10k** | **49** | truncation of greedy@1k (`full1k_solved`; 49/60 at ≤1k) |
| same + Aut-orbit **witness** in covsweep@10k | **52** | some one-shot CoV in the *same Aut-orbit* as `best_rep` solves ≤10k — **not** a run from our Aut-min string (exact best_rep hits in sweep: 0/60) |
| oracle best-CoV @10k (brute every subword CoV, pick cheapest) | **52** | [`greedy_vs_bestcov_subset60_b10000.csv`](../stable_ac/cov/greedy_vs_bestcov_subset60_b10000.csv) |

- Orbit-witness-only rows (need Colab greedy@10k from Aut-min to confirm): ['596', '605', '610']
- Still open even with orbit witness: ['622', '623', '624', '625', '636', '637', '638', '639']
- bestcov@10k solves we lack even as orbit witness: —
- orbit witness solves bestcov@10k misses: —

## Verdict

Oracle best-CoV @10k = **52/60**. Our runnable nonsym beam is **proven** at **49/60** for budget 10k (already done by 1k). Joining the one-shot sweep by Aut-orbit lifts the *optimistic* count to **52/60** — matching bestcov — but those +3 (['596', '605', '610']) are **different string labels** of the same orbit (relabel trap) with sweep caps 32–33 vs our `treat_cap` 30. Do **not** headline 52 as our algorithm until Colab runs greedy@10k from Aut-min `best_rep`.

The eight aut-class-106 rows (`622–625`, `636–639`) stay open for both: bestcov needs 20k, and our multi-hop `best_rep` orbit has no solving one-shot CoV in the 10k sweep.

## Side note — if “10 budget” meant node_budget=10

- nonsym → greedy rescore @10: **31**/60
- bestcov rescore @10 (from 10k table, nodes≤10): **15**/60
- bestcov @10k remains **52/60**

True Aut-min greedy@10k: `experiments/heuristic_search/hsearch_colab_covbeam_nonsym_b10k.ipynb`.

Open for proven arm: ['596', '605', '610', '622', '623', '624', '625', '636', '637', '638', '639']
