# [2026-07-24] A knob chosen for a superseded configuration keeps being carried, and it costs a simplification [TRAP]

The heuristic program fixed the endgame phase boundary at total length 16 in EXP-03. That was a real measurement: swept over nine thresholds, with an inverted-direction control that never beat the baseline, `T = 16` won.

But it was measured **at budget 500, for the ordering `L + 8·knots`**, on the stratified train slice. Over the following experiments the recommendation moved to a richer multi-feature climb at budget 1,000 — and `T = 16` was carried along untouched, appearing in every later config as though it were a property of the problem rather than a fit to a configuration that no longer existed.

Re-sweeping it (EXP-18), with `T = 0` (no endgame segment at all) as the control, showed the boundary is load-bearing only for the *lean* climbs:

| climb | terms | endgame worth (budget 500 / 1000) |
|---|---|---|
| `L + 8K` | length + knots | **+3 / +3** |
| `L + 8.9K − 6·xyimb` | length + knots + imbalance | **+4 / +5** |
| the richer climb | + max-knots, smaller-block | +1 / **+0** |
| the block climb | length + block extremes | +0 / **+0** |

The recommended ordering scores an identical 19/24 with and without the phase. So the carried-forward knob was not wrong, it was **inert** — and inert in a way that made the published recommendation more complicated than the evidence required. The correct recommendation is a single weight vector with no segments at all.

The mechanism is worth keeping, because it predicts where the phase will and will not be needed. Near the trivial state there is nothing structural left to buy, so an ordering carrying *only* a knot term keeps paying for knots and wanders instead of cancelling; the phase forces it back to length. A climb that already carries `smaller-block` and `max-knots` self-regulates, because both fall as the pair approaches trivial. The phase is a fix for a deficiency in the lean vector, not a feature of the search.

## Rule

**When the winning configuration changes, re-sweep the knobs that were tuned for the old one — and include the knob's *off* setting as a control.** A parameter fitted to a superseded configuration is not evidence about the new one; it just travels. The `off` arm is what distinguishes "still optimal" from "no longer doing anything", and only the second answer buys a simplification.

Cheap heuristic for spotting these: any constant that appears in every config in an experiment program, and was set once early on, is a candidate. Ask which experiment chose it, under what ordering and budget, and whether either still holds. Related: [compare on the same denominator](compare-on-the-same-denominator.md), the other way an early choice silently propagates.
