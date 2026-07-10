# [2026-07-09] Never run a search above budget 1,000 yourself — hard cap [TRAP]

## The rule, restated (2026-07-09, user directive)

> "do not run code by yourself for high node budget, just do max of 1000 node budget"

The original entry below said "~10k nodes". That is now **1,000**, and it is a hard ceiling on
every search *Claude* launches, in any context — shell, test, repro, scratch script. It matches
the test suite's existing `MAX_BUDGET = 1_000` ([test-budget-ceiling](test-budget-ceiling.md)),
and for the same reason: a search at budget `B` is exactly the first `B` pops of any longer
search, so a bigger budget buys a slower repro, never a different behaviour. Production budgets
are the user's to run, on Colab.

This held up immediately. The "rows 7 and 8 vanished from the jsonl under parallelism"
question — which *looks* like it needs a 1M-node reproduction — was settled at budget 1,000 in
under a minute: 3 forked workers, 12 presentations, 12/12 rows, out of order, no duplicates.
See [jsonl-hole-is-not-a-write-race](jsonl-hole-is-not-a-write-race.md).

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

- **Never exceed `node_budget = 1_000` in a search you launch.** Not "prefer smaller" — a cap.
- **Cap any local run at 10 minutes.** If it can't finish in that, it does not belong on this
  machine. Production budgets belong on Colab.
- **Verify on a small subset (~10-20 presentations).** Test the *mechanism* — row written /
  resumed / recovered / parity — not the production scale.
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
