# EXP-07 — is knot-progress a leading indicator of a solve?

The gate before any experiment ranks the second hump on `min_K`. The second hump never solves at these budgets, so its only signal is a proxy; this checks the proxy where the ground truth is visible — the **boundary rows**, not solved by 500 but solved by 1,000.

Windows (a not-solved-at-500 search that had a 1,000 outcome): **187**.

## Knot-progress at the 500-node mark

- searches that went on to **solve** by 1,000: mean knot drop **+0.62**
- searches that **never** solved: mean knot drop **+0.75**

## Did *any* knot drop by 500 separate them?

| | solved by 1,000 | never solved |
|---|---|---|
| dropped ≥1 knot by 500 | 12 | 109 |
| no knot drop by 500 | 9 | 57 |

- P(solve | dropped a knot) = **0.10**
- P(solve | no knot drop) = **0.14**

## Companion: is length-progress any better?

Rejecting the knot proxy only means something if its obvious replacement is not equally blind.

- eventual solvers: mean length-progress by 500 = **+5.05**
- never solved: mean length-progress by 500 = **+5.87**

Almost every unsolved search has already shortened *something* by 500, so length-progress is near-constant across both groups and separates them no better than knots do. **Neither checkpoint proxy forecasts a solve** — at these budgets solving is a discrete event, not the endpoint of visible progress.

## Verdict

NOT VALIDATED — knot-progress does not discriminate at the boundary; do not rank the second hump on it, use min_total and real solves instead

