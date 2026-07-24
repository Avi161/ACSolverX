# EXP-21 — a second ordering from a *different family*, at full budget

Decidable band (bins 4–7, 24 rows), budget 1000 each, cap 48. Each ordering gets a full budget — this is the 'I have more compute' question, not the 'divide what I have' question that EXP-17 and EXP-20 both answered no.

## Alone

| ordering | solved |
|---|---|
| recommended (richer knot climb) | 19/24 |
| blocks (a finalist, for contrast) | 19/24 |
| complement: S+imbal, no knots | 15/24 |
| complement: Bmin+Lmax+S+xyimb | 15/24 |
| complement: Bmax+Lmax | 12/24 |

## Paired with the recommended climb (19/24 alone)

| second ordering | union | rows it adds |
|---|---|---|
| complement: S+imbal, no knots | **23**/24 | `ms568`, `ms573`, `ms578`, `ms583` |
| complement: Bmax+Lmax | **20**/24 | `ms573` |
| complement: Bmin+Lmax+S+xyimb | **20**/24 | `ms568` |
| blocks (a finalist, for contrast) | **19**/24 | — |

Union of all 5 orderings: **23/24**.

## Reading

A second ordering from a different family reaches **23/24** against the recommended climb's 19 alone — rows the knot climb cannot reach at any point in its 1,000 nodes. Note that at budget 1,000 the union of all five *finalists* is 19/24, exactly the best single: the finalists are redundant with each other, and the gain here comes from leaving that family, not from adding more of it.

**The honest caveat.** These complements were selected *because* they solved rows the finalists miss, so the union above is optimistic on exactly those rows. What it supports is the qualitative claim — a different family reaches different presentations — not the specific count as an out-of-sample estimate. The actionable form: with 2× the compute, run the recommended climb and one structurally different ordering at full budget each, rather than one ordering twice as long or two at half.

