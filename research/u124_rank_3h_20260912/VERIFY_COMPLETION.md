# Derived-consequence audit: PASS

`completion.py` maintains an exact invariant: each stored consequence is the
free-group product of its listed conjugates of **nontarget** original donors.
For factors `c^-1 D^eps c`, inversion reverses the factor list and negates each
sign. Conjugating the whole consequence by `u` appends `u` to every conjugator,
since `u^-1 c^-1 D^eps c u=(c u)^-1 D^eps(c u)`. Free reduction of `c u`
preserves the identity.

Consequently the canonicalization witness transports both signs and cyclic
conjugation correctly. A critical composition `L^-1 R` has the reversed,
sign-negated proof for `L` followed by the proof for `R`. Applying this again
to a derived consequence preserves the invariant by induction. There is no
assumption that the derived word is a free basis element, nor that a normal
consequence can replace a relator without a factor ledger.

For a derived relation `S=A C` and target rotation `A B`, the replacement
`C^-1 B` uses the conjugated inverse proof of `S`. The restored original target
frame is included in the conjugator. The independent checker expands every
factor and verifies the resulting full free-word identity, retaining all
nontarget relators. The original donors remain unchanged throughout the
finite composite.

The tiny controls verify18 signed/cyclic orientations, seven consequences
from48 critical compositions, and nested normal-product width up to four.
Applying the library evaluates29 matched rules and yields16 independently
replayed endpoints. The planted tuple is known trivial: `(aba,ba)` kills
`a,b`, after which the third relator kills generator9. No census search is
rerun; these are finite algebraic controls.

All nine saved `completion_pilot.json` paths and metrics pass. **There is no
new strict gain beyond the imported seeds.** Every retained path is exactly
an imported plateau path, including the three length improvements for
`aca_75`, `aca_83` and `aca_84`. Thus its summary's165→162 comparison is
against the older2180 baseline, not evidence of three new completion gains.

The new probe spends9000 units, excluding the historical seed discovery.
Its two imported full seed files cost28307 units in their own earlier campaign;
that aggregate is reported separately, not allocated anew to these nine rows.
Seed insertion/replay does not make discovery free, and these units do not
measure elementary normal-product expansion cost.

`completion_pilot.json` pins the older verifier hash from before the template
event extension. That historical hash is preserved in
`verification_completion.json`; this audit rechecks all stored paths with the
current independent checker. All other recorded source hashes match.

This is a bounded consequence generator, not a completed confluent rewriting
system. The queue can grow longer words and wider proof products, and its work
charge counts tested critical pairs and matches rather than all word-processing
or elementary-AC work. A negative pilot is not a normal-closure obstruction.

Reproduce with `verification_consequence_checks.py`; machine results are in
`verification_completion.json`. No proof-transport bug was found.
