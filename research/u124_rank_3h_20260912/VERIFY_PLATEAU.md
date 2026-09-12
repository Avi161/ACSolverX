# Plateau audit: PASS

`verification_plateau_checks.py` independently replays the six-row rewrite
pilot, its separate six-row Whitehead pilot and the118-row rewrite remainder.
The rewrite pilot and remainder partition exactly the124 current baseline IDs.
The saved paths, complete lengths/ranks, source labels and shared-work sums
pass. No census search was rerun for this audit.

| New length gain | Current baseline | Attained length | Rank |
|---|---:|---:|---:|
| `aca_75` |19|18|3|
| `aca_83` |20|19|3|
| `aca_84` |20|19|3|

These gains reduce the current2180 total to2177. Each path first makes a
length-neutral donor rewrite, then a strict donor rewrite. Their new ordinary
AC segments begin at previously certified stable sources; they are not claimed
as ordinary rank-two certificates from the original presentations.

`aca_109` retains length20 while moving rank4→3, with boundaries
`(4,20)→(4,20)→(3,21)→(3,20)`. This exact three-event path appears in both
pilots. `aca_111` retains length21 while moving rank4→3: two neutral rewrites
at rank4 precede a removal to rank3 length22, then six neutral rewrites and a
Whitehead reduction to21. Neither saved endpoint misses a shorter or
same-length lower-rank prefix.

The rewrite pilot costs3569 recorded units and its remainder24738, totaling
28307 physical units. The separate Whitehead pilot costs6000 more. These
figures count matched rewrites, minimum cuts and removal checks; they do not
count elementary-certificate expansions or establish equal cost per unit.

## Circular correction convention

Write the target as `R=p q`, where the selected rotation is `q p=A B`.
Here `A` is the matched block and `B` its suffix in that rotation. Let a signed
donor rotation be `t^-1 D^eps t=A C`, so the replacement is `C^-1`.
The displayed result in the original target frame is

`R' = freely_reduce(p C^-1 B p^-1)`.

The implementation uses correction exponent `-eps` and conjugator

`c = freely_reduce(t A B p^-1)`.

Then direct free-group multiplication gives

`R c^-1 D^-eps c = p A B p^-1 p B^-1 A^-1 t^-1 D^-eps t A B p^-1`

`= p (A C)^-1 A B p^-1 = p C^-1 B p^-1 = R'`.

Thus the wrapping convention and donor sign are correct. The audit verifies
both this complete product identity and the rule metadata: the target cut,
matched block, replaced word, exact signed donor rotation, reduced correction
conjugator and restored target frame. All other relators must remain present.

Every event kind emitted by `plateau.py` is covered independently:
normal-product substitutions, whole-tuple Whitehead maps with two-sided inverse
checks, Lemma11 removals, relator normalization and literal definitions. The
`whitehead` mode enumerates finite partitions and the `mixed` mode can add
definitions; correctness of a recorded event does not depend on their candidate
ordering or completeness. The shared budget and incomplete screens must remain
explicit; frontier exhaustion is exhaustion of this screened policy.

## Signed wrapping control with generator gaps

The planted tuple on IDs2,5,9 is

`((5), (2,5,5,5,5,5), (-5,-5,9,-5,-5))`.

It is known trivial: the singleton kills5, the second relator then kills2,
and the last relator kills9. The finite rewrite call evaluates25 matched
rules and returns10 distinct endpoints. All10 independently replay, including
four that wrap the end of the target. This is a tiny planted control, not a
census screen.

One selected event uses the inverse donor's four-letter block
`(-5,-5,-5,-5)` at target cut3, replacing it by `(2,5)`. Its correction uses
the **positive** original donor and conjugator `(-5,-5)`. The freely reduced
target in the original frame is `(-5,-5,9,2,5,5,5)`; its cyclic reduction has
length3. Flipping the donor sign fails the exact product check. Dropping the
outer target-frame conjugation also fails, even though it preserves a cyclic
conjugacy class. These controls catch errors hidden by comparing normalized
endpoints alone.

`verification_plateau.json` contains the source hashes, all row checks,
boundary metrics and selected planted event. No flaw was found in the circular
correction convention or in the saved improvements.
