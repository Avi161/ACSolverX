# [2026-07-09] Never run a production-budget search locally — 10-minute cap [TRAP]

## What happened

To answer "did presentation 12 solve at 1M nodes?", I launched the real search locally:
1M nodes, `mrl=48`, heavy solver. That is ~9 GB of `visited` set on a 16 GB Mac. It swapped,
starved the parallel verification running beside it, and after ~20 minutes had produced
**zero output**. I killed it.

The question it was meant to answer had *already* been settled — by a 20k-node,
20-presentation repro that ran in **75 seconds** and showed the mechanism directly
(`solved 8/20` printed, zero solved rows in the jsonl). The expensive run would have added a
single data point about one presentation; the cheap run proved the bug.

## Rules

- **Cap any local run at 10 minutes.** If it can't finish in that, it does not belong on this
  machine. Production budgets belong on Colab.
- **Verify on a small subset (~10-20 presentations) at a small budget (~10k nodes).** Test the
  *mechanism* — row written / resumed / recovered / parity — not the production scale.
- **Keep the pipeline budget-agnostic**, then assert that. If a fix is correct at 5k and 10k
  and contains no budget-specific constant, it is correct at 1M. Verifying one budget by brute
  force is both slower and weaker evidence than verifying two cheap ones.
- To learn a *specific* presentation's outcome, read it off the existing jsonl
  (`solved`, `nodes_explored`) rather than re-running the search.
- Reach for the **smallest experiment that discriminates the hypotheses**, not the most
  faithful reproduction of production.

## Related

The same instinct is what made [`max-relator-length-is-inert`](max-relator-length-is-inert.md)
cheap to settle: measure the mechanism on a subset, don't re-run the sweep.
