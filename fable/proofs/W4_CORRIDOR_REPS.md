# W4: corridor representatives and the Tpub self-loop

Date: 2026-08-28 · Checkers: `checkers/q_corridor_mu.py`,
`checkers/corridor_reps.py` (both guarded, budgets ≤ 1,000, aut_canon
certificate-checked on every call; AK(3) control μ=13 green).

## Facts established

1. **μ(Q) = 21.** The published-elimination pair
   `Q = (xYxYXyyXYxyXy, XyyXYXyxYYxy)` (Tpub with z = Yx eliminated; the
   MMS02 published descendant, hand-verified twice in the corridor audit)
   has Aut-canonical rep `(YYXXYxyXyx, YXYXYxyXyxx)`, a different Aut-orbit
   from AK(3)'s. Greedy from Q: 25 → 13 total, unsolved at 1,000 nodes.
2. **The Tpub greedy floor state is AK(3) up to Aut and one Tietze move.**
   A 1,000-node greedy from `Tpub = (A, B, Xyz)` reproduces the committed
   bridge record `(ZYx, ZxyX, ZZZyyyy)` (total 14; matches
   `.scratch/ak3_rank3_positive_audit.md`). Row 0 isolates `z = Yx`;
   mechanical elimination (consistency-checked) gives `(XyxyX, XyXyXyyyyy)`
   whose `aut_canon` is **exactly** `(YXYxyx, YYYYxxx)` — AK(3)'s own
   canonical representative, μ = 13.
3. **A second elimination gives a new stable representative.** Row 1
   isolates `z = xyX`; elimination gives `(xYXYx, xYYYXyyyy)` with
   Aut-canon `(YXXYx, YYYYXyyyx)`, **μ = 14** — not AK(3)'s orbit, stably
   AC-equivalent to AK(3) through the corridor + Tietze. Its greedy also
   drains to total 13, unsolved at 1,000 nodes.

## Consequences

- **W1c downgraded.** The `29 → 14` descent recorded in
  `W1C_TPUB_PREFLIGHT.md` is now explained: the Tpub basin at this budget
  drains to an Aut-image of AK(3) itself plus a `z = Yx` Tietze letter. The
  bridge-by-search route therefore buys no easier hump geometry at its
  observed floor: a production run on Tpub should be expected to be
  approximately as hard as a production run on AK(3) directly. The
  production handoff stands but with this corrected prior; the honest
  remaining content of promise-ledger route 1 is its structural
  second-stage gates, not search.
- Scope of the self-loop statement: it is proved for THIS floor state at
  THIS budget (the one-move-shell audit already showed the state is a
  strict local minimum). It is not a theorem about every Tpub floor state.
- The stable class of AK(3) now has three concrete committed rank-2
  Aut-orbits on record: μ=13 (AK3 itself), μ=14 `(YXXYx, YYYYXyyyx)` (new),
  μ=21 (Q). All greedy-drain to the 13-floor at 1,000 nodes; the class's
  known μ-floor remains 13; nothing here approaches the μ ≤ 12 finish line.

## Nonclaims

No AK(3), stable AC, AC, or bridge claim. The μ=14 and μ=21 orbits are new
*data points* in the stable class, not progress claims; a bounded greedy
null is never evidence of unsolvability.
