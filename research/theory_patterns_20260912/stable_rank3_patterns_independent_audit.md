# Independent review of the three-relator corridor

Verdict: **PASS** for the statements in `stable_rank3_patterns.md` at the
source hash recorded in the adjacent JSON. This is a local normal-form and
BS-entry result, not a U124 trivialization.

The first restored-donor product is checked directly:

    (zQ)(Q^-1 I Q) = x^-m y x^(m+1) y^n,

where Q=x^m y^n and I=z^-1 x^-m yx. Inversion and the specified conjugation
produce K=x^-(m+1) y^-1 x^m y^-n. Writing A=z y^k z^-1, the second identity
uses A^-1 C A=yx A, so it replaces the exact factor x^-1 y^-1 by A. These
are free-group identities for all signed m,k,n, including zero; no assumption
about normal forms or the presented group is hidden in the cancellation.

The coordinate z=x^m t is invertible, with inverse t=x^-m z. The final two
donor operations reduce the third row to x^m y^n x^m t while restoring both
donors. The exponent determinant is k-n, so unimodularity is correctly stated
as necessary, not sufficient. The three soluble subfamilies use the ordinary
first segment and then expose a generator directly; they do not depend on
the stable-coordinate convention or an assumed trivial-group conclusion.

For the actual aca_24 tuple, a separate integer-word replayer validates the
35-move first ordinary segment and18-move second ordinary segment, with total
relator-length peaks27 and29. It checks every move has a distinct donor or a
single signed-generator conjugation. The gap between these segments is the
explicit invertible coordinate map; its stable elementary expansion is not
claimed to have been emitted. Independent integer checks also verify216
signed parameter triples and their determinant identities.

The extra-generator warning is essential: a BS donor on y,t together with
companions involving an independent x is not the two-generator terminal
problem. Eliminating t leaves the displayed two-relator problem in x,y,
which this argument does not trivialize. The final total19 does not improve
the certified15-letter seed.
