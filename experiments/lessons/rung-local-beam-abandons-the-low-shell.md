# [2026-07-23] A rung-local beam abandons the low shell; best-first buys closure [WORKS]

`mu_ladder_big.climb_one_big` keeps `beam = cand[:K]` where `cand` is **only the current rung's** new orbits. So an orbit at the moat rim is expanded exactly once — in the rung that discovered it — and is then gone forever, and its siblings that missed that rung's top-K are never expanded at all. The front drifts; it is not a frontier.

Measured on `aca_39` (μ_in 19, beam 64, 480 s, fast canon): the beam's *lowest* member climbs 22 (rung 2) → 24 (rung 10) → 27 (rung 40) while the candidate mass sits at μ 31–39 (mode ~35, tail to 153). 18,684 orbits, and only 41 of them (0.2%) are at μ ≤ 24. More orbits at this rule buy states further **up** the cone. That is what "we explored 30k orbits and reduced nothing" looks like from the inside, and it is a property of the selection rule, not of the class.

Swapping the rung-local beam for a **global best-first heap over every discovered-but-unexpanded orbit, ordered by μ** — same hop generator, same dedup, same wall clock — expanded 5,831 of 22,224 orbits in μ order: all 5 at μ=22, all 20 at 23, all 21 at 24, 61 at 25, … up to 175 at 35. Because best-first pops in μ order, reaching μ=35 means **every discovered orbit below 35 had already been expanded**, so the CoV-reachable set is *closed* for μ ≤ 34 and its minimum is 22 against a start of 19.

That is the payoff: not "we didn't find a descent" but "there is no descent in this ball" — a completeness-by-closure statement a beam structurally cannot make (cf. `floor-census-not-min-length.md`, same rule from the other side).

**Rule:** when a search saturates, check whether the selection rule ever revisits the good states. A rung-local (generation-synchronized) beam discards them by construction; a global priority queue over the open set does not, and it converts a negative result into a closure proof. Do not read closure as global: it holds for routes that stay under the popped μ, and a descent reachable only via a higher-μ detour is *not* excluded — the two-hump shape survives this argument intact.
