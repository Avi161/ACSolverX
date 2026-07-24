# [2026-07-24] Before crediting a transform for an escape, price the untransformed route [TRAP]

The eight benchmark rows `ms622`–`ms625` / `ms636`–`ms639` (one Aut class, `aut_class 106`) are the only ones neither the greedy nor **any** change of variables solves at 10,000 nodes. Re-running their entire subword-CoV family at 20,000 nodes — same cap, same reduction, budget the only difference, joined pair by pair against the b10k sweep to prove it — made all eight escape. The cheapest CoV start solves in 14,352–14,469 nodes.

Read alone that is an 4.2×–18.9× speedup over the plain greedy on the untransformed pair, which needs 59,710–272,953 nodes at budget 1M. It is not a speedup you can have, for two separate reasons, and neither is visible without pulling the untransformed column in:

1. **The oracle's denominator.** 14.4k is the cheapest of ~170 searches. Finding it cost 909 searches and 17,313,543 nodes — ~2.2M per presentation, about **ten times** what it costs to just run the greedy longer.
2. **The runnable version is a coin-flip on half the rows.** 221 of 909 pairs solve (24.3%), so a blind restart — draw the CoV starts in random order, stop at the first that trivialises — has expected cost `((n+1)/(k+1) - 1) · B + mean_solved_nodes`. That is 80.8k–83.0k on the four bin-9 rows against the greedy's 213.9k–273.0k (**2.58×–3.38×**, a real win) and 62.5k–63.0k on the four bin-8 rows against 59.7k–78.8k (**0.95×–1.26×**, nothing). The headline splits by bin, and the pooled number hides it.

And the *tuned heap ordering* solves all eight at ~62.5k nodes in one search with no restarts — cheaper than both the blind restart and the greedy on every one of the eight. The transform was never the cheapest route to any of them.

Two more things that only showed up when the number was pushed on:

**The collection budget `B` is a knob inside the metric, and it was never swept.** `B = 20,000` was chosen before the data existed, but both `k(B)` and `mean_solved(B)` move with it, so the ratio belongs to `(method, B)` — not to the method. A search at budget `B` is exactly the first `B` pops of a longer one, so re-scoring every row at every smaller `B` costs **zero new search**. Doing it showed the ratio is not monotone (it drifts down as failed draws get dearer and jumps whenever a cluster of solves comes into range) and that **20,000 is the most favourable `B` on four of the eight rows and within 5% on the rest**. At `B = 15,000` the blind restart loses to the greedy on six of eight. The published ratio was an optimistic bound presented as a measurement. What survived was the *direction*: bin 8 never clears 1.3 at any `B`, bin 9 clears 1.8 at every `B ≥ 16,000`.

**A ratio that improves on the harder rows is the denominator moving until proven otherwise.** "CoV pays off where the problem is harder" reads as the transform doing something special on bin 9. It isn't: the blind restart is nearly flat across all eight (62.5k–83.0k) while the greedy goes 59.7k–78.8k → 213.9k–273.0k. Print both columns, and say which one moved.

Related but distinct from [`control-with-no-dynamic-range.md`](control-with-no-dynamic-range.md): there the control could not move, so the null was untestable. Here the control moves fine — it was simply never put in the table, because the arm under test had a within-arm baseline (its own budget-10,000 verdict) that felt like one.

**Rule:** an escape claim needs the cost of *not* doing the thing, at the budget where the untransformed route actually succeeds — not the budget where it was last observed to fail. Report the oracle and the runnable procedure as separate columns, and check whether the win survives stratification before pooling it.
