# Coupled relators and compressed Baumslag–Solitar corridors

This note develops exact donor rewrites and changes of the retained helper
alphabet from the 2180-length U124 baseline. Ordinary substitution formulas
are proved directly in free groups. Stable additions/removals use the stated
known-triviality hypothesis, and the fixed-donor geodesic corollary additionally
uses the cited HNN theorems. A negative bounded screen is not an obstruction
to stable AC shortening.

## The concrete donor pattern

Several displayed baseline tuples contain a root definition `ZYY` or `ZYYY`
and another donor `XZZxYzz`. With `ZYY=1`, substitution gives `z=y^-2`, so the
second donor becomes

\[
 x^{-1}y^4xy^{-5}.
\]

With `ZYYY`, the same displayed donor becomes `x^-1 y^6 x y^-7`. The variant
`XZZyxzzz` with `ZYY` becomes `x^-1 y^5 x y^-6`. Thus these states retain short
encodings of a two-generator Baumslag–Solitar donor. They offer algebraic
structure that a bounded sequence of literal substring moves can miss.

The implemented sufficient recognition is broader: one retained donor
isolates a helper as `z=y^k`, with nonzero integer `k`; after using this
definition, a second retained donor is conjugate to a signed copy of
`x^-1 y^m x y^-n`, with `m>0` and `n!=0`. Both original donors are retained.
There is no requirement that either donor alone trivializes its quotient.

The exact source for stable defining-generator removal is Lemma11 of
Shehper et al., *What makes math problems hard for reinforcement learning:
A case study*, Section9.1, page43; see the local primary-paper text
[`math_ml_paper_2408.15332.txt:2499`](/Users/avigyapaudel/Documents/surf/ACSolverX/literature/txt/math_ml_paper_2408.15332.txt:2499).
That lemma needs known triviality and does not bound the normal-product
expansion used for removal. **The initial corridor macro does not remove a
donor or generator and does not need this hypothesis:** its recorded ordinary
AC identities hold in any presentation containing the two retained donors.
Later sections explicitly identify constructions that add or remove helpers.

## Root-power metric

Within a word using only `y,z` with `z=y^k`, let the expanded `y` exponent
be `e`. The minimum spelling length over these two letters is

\[
 c_k(e)=\min_{b\in\mathbb Z}\bigl(|e-kb|+|b|\bigr).
\]

Any spelling with net counts `(a,b)` has `e=a+kb` and length at least
`|a|+|b|`. Conversely `y^a z^b` realizes that length, proving the equality.
The objective in `b` is convex and piecewise linear, with breaks at zero
and `e/k`, so zero and the adjacent integers to `e/k` suffice. The code also
considers both orders of the two powers for deterministic lexical tie-breaking.

This is a relative root-block metric. It does not claim the same spelling
is shortest after also using the second donor or arbitrary AC moves.

## Simultaneous corridor flows

After expanding the helper, write a cyclic target as

\[
 s_0y^{e_0}s_1y^{e_1}\cdots s_{t-1}y^{e_{t-1}},
 \qquad s_i\in\{x,x^{-1}\}.
\]

Zero exponents and consecutive stable letters are allowed. Set

\[
 (A_i,B_i)=
 \begin{cases}(m,n)&s_i=x,\\(n,m)&s_i=x^{-1}.\end{cases}
\]

For arbitrary integers `q_i`, the donor relation permits the transfer

\[
 s_i y^{B_iq_i}=y^{A_iq_i}s_i.
\]

All transfers together change the root exponents to

\[
 e_i'=e_i-B_iq_i+A_{i+1}q_{i+1},
\]

with indices modulo `t`. Accordingly the module minimizes

\[
 \sum_{i=0}^{t-1}c_k(e_i-B_iq_i+A_{i+1}q_{i+1})
 \quad\text{over}\quad -b\le q_i\le b.
\]

Fixing `q_0` converts this cycle into a finite dynamic program. The state is
the latest flow value; the accumulated edge cost is the optimal cost of the
completed root blocks. At the last edge, add the cost connecting back to the
fixed first value. This proves optimality **within the declared flow box**.
Ties prefer fewer total transfer units and then lexical flow order.

The stable-letter contribution `t` is constant in this objective. Free and
cyclic reduction after transfer can remove additional stable letters, so the
actual endpoint may be shorter still. The module does not claim to minimize
that extra cancellation over all tied flow assignments, to find geodesics
in the Baumslag–Solitar group, or to optimize outside its finite box.

This is a simultaneous arithmetic rewrite rather than a shortest path
through length-nonincreasing intermediate tuples. Individual transfers and
helper expansion can increase length while their complete composition gives
a shorter target. Ordinary single-donor local minima therefore need not be
fixed points of the new macro.

## Exact normal-product certificates

Every factor has the convention `c^-1 R_j^sign c`, with `sign` exactly `+1`
or `-1`. A certificate records

\[
 R_{target}'=\operatorname{red}\left(
 R_{target}\prod_j c_j^{-1}R_{d_j}^{\epsilon_j}c_j\right),
 \qquad d_j\ne target.
\]

The final tuple includes every original donor and has explicit conjugation,
inversion, and row-permutation normalization witnesses. Temporarily conjugate
or invert each donor, right-multiply the target, then restore the donor to
expand this normal product into finitely many ordinary elementary AC moves.
An elementary stream is not emitted by this module; the exact normal product
is independently replayed instead.

Let `N=z^-1 y^k` be the oriented root donor, itself a witnessed conjugate of
a signed original relator. Replacing `z` by `y^k` has correction `N`;
replacing `Z` by `y^-k` has correction `z N^-1 Z`. At a substring with suffix
`Q`, conjugate its correction by `Q`. Iterating these identities expands any
helper word with an explicit product of the original root donor. Reversing
the certificate for an optimal packed word provides the repacking witness.

The recovered BS word `Q=x^-1 y^m x y^-n` is itself expressed as a product
of conjugates of the two original donors. For `C=x^-1 y^m x` and `B=y^n`,
the correction `C^-1 B` is `B^-1 Q^-1 B`. The inverse corridor uses the
corresponding conjugate of `Q`. Replacing powers repeats that correction,
conjugated by each remaining suffix; negative powers reverse and conjugate
the factor list. Every primitive correction is checked against its exact
free-group word before use.

A transfer across the chosen cyclic boundary also rotates a prefix. The
compiler tracks the cumulative conjugator and transports every later donor
factor back to the original target frame. This is essential: merely cyclically
reducing a quotient identity would not supply the correct normal product.

## API and work limits

`theory_corridor.probe(words, remaining, flow_bound=2)` returns
`(candidates, charged)`, where a candidate is `(after, events)`. Inputs use
arbitrary signed integer generator IDs. `remaining` is restricted to0..1000,
and the flow bound to0..3. No rank or presentation-length ceiling is imposed.

A relative root collection and an attempted second-donor recognition each
cost one unit. Every dynamic-program transition, including a failed or
incomplete attempt, costs one. An incomplete dynamic program returns no
flow candidate. Ordinary algebra replay, root recognition, and bookkeeping
are not separately charged. These units are not elementary move counts or
uniform CPU costs. Successful, equal-length, and uphill distinct endpoints
can be returned so the caller can choose its exploration policy.

The module is independent of the parent process's general plateau search.
Census execution and incorporation into the global frontier are delegated to
the parent so CPU campaigns remain serial.

## Verification performed before handoff

227 small checks passed, without running any census row:

- 125 root-metric comparisons for exponents−12..12 and root exponents
  `k=-3,-2,1,2,3`, against direct integer enumeration.
- 81 complete three-flow certificates over `q_i=-1,0,1`, with positive and
  negative root exponents and both signs of the second BS exponent. Each
  certificate passed the independent `verify.normal_product_event` decoder
  after JSON round-trip.
- Three dynamic-program optima matched direct enumeration of all27 flow
  vectors each; twelve truncated-budget checks exhausted exactly the
  supplied allowance without claiming an optimum.
- Six probe-budget checks on the known-trivial planted tuple
  `(Zyy, XzxYYY, xY)` passed full event replay. Here the coupled BS donor is
  `BS(2,3)`, and the flow `q=-1` changes target `xY` to `x` up to inversion
  and normalization. This validates a local mechanism, not a census solve.

The general `m>1` case still has Britton divisibility obstructions: stable
exponent `+1` or `-1` does not force a reducible pinch or a solve. The macro
returns only exact candidate identities and leaves all unsuccessful cases
unresolved.

## Extension: remove pinches, then search a mathematically sufficient box

`theory_flow_exact.py` strengthens the initial arbitrary flow box in two ways.
Its API is `probe(words, remaining, audits=None)`. Supplying a list as
`audits` collects completed or incomplete per-corridor search information,
including negative results. Its candidate/event format matches the first module.

**Residue lemma, including the cyclic boundary.** If `s_i=x` and
`s_(i+1)=X`, then

\[
 e_i'=e_i+n(q_{i+1}-q_i).
\]

If the signs are `X,x`, replace `n` by `m`. Thus a flow can make this
intervening root exponent zero if and only if the original exponent is
divisible by the corresponding integer. The statement uses cyclic indices,
so it applies unchanged to the last/first stable pair and to negative `n`.

The divisibility conditions are exactly the visible Britton pinches
`x y^(nq) X -> y^(mq)` and `X y^(mq) x -> y^(nq)`. The new module repeatedly
applies these long-power replacements and packs the result, emitting the same
exact normal-product certificate for each pass. Each pass removes at least
two stable letters; a complete scan with no such pair certifies that this
particular cyclic word is Britton-reduced.

On a cyclically Britton-reduced word, **no simultaneous flow can create its
first stable-letter cancellation**, by the residue lemma. Consequently
`t+sum c_k(e_i')` is the actual cyclically reduced target length after optimal
root packing. The initial module's omission of extra cancellation from its
objective therefore matters only when pinches were already available. This
observation avoids a general context-free cancellation optimizer; it is not
a theorem that every stable-exponent-one word has a pinch.

**Finite complete-search bound.** Let `M` be the cyclic transfer matrix:

\[
 (Mq)_i=-B_iq_i+A_{i+1}q_{i+1},\qquad e'=e+Mq.
\]

When `M` is nonsingular, write `H=M^-1`. If the desired total root cost is at
most `C`, every possible improving integer flow satisfies

\[
 |q_i|\le\left\lfloor
 |(He)_i|+K C\max_j|H_{ij}|
 \right\rfloor,\qquad K=\max(1,|k|).
\]

Indeed `q=-He+He'`, and `|e_j'|<=K c_k(e_j')`; applying the triangle
inequality and the **total** cost bound gives the displayed inequality. The
code computes `H` with exact rational products along the cyclic recurrence
`q_(i+1)=(B_i q_i+e_i'-e_i)/A_(i+1)` and verifies its inverse identity. This
retains the cancellations between large common factors; no floating-point
matrix inversion or magnitude estimate is used.

The recurrence multiplier over one cycle is
`(n/m)^(sum sign(s_i))`. It differs from one when `m,n` are positive distinct
integers and the stable exponent is nonzero. For the actual balanced rank-three
model there is a stronger elementary check: after eliminating the root helper
in the exponent matrix, its determinant has absolute value

\[
 |m-n|\,|\operatorname{exp}_x(W)|.
\]

Unimodularity therefore forces `|m-n|=1` and stable exponent`+1` or`-1`.
With the orientation `m>0`, `n!=0`, this also forces `n>0`. Every recognized
unimodular rank-three model consequently has a nonsingular flow matrix.
For more general inputs the implementation reports the singular case as
outside this sufficient complete-search bound.

The sparse optimizer enumerates desired root exponents whose exact root cost
fits the remaining cost allowance, uses the recurrence's divisibility to infer
the next flow, and checks the sufficient coordinate bound. This can be much
smaller than traversing every combination in the box. Nevertheless every
tested transition is charged, and a 1000-unit truncation is explicitly
incomplete. “Complete” means no cheaper flow exists for the fixed retained
donor pair and Britton-reduced stable corridor; it does not exclude other AC
operations, different donors, or further stabilizations.

The companion pattern `XXXYxYxY`, with `BS(4,5)` and root exponent`-2`,
has a strict root-cost target`C=2` whose sufficient flow bounds are
`[10,8,6,7,9]`. This illustrates why a chosen box`[-2,2]` cannot be treated
as complete.

Verification added nine exact sparse-DP comparisons against finite-box
enumeration; four signed/cyclic pinch-certificate controls; five probe-budget
checks; and an end-to-end planted `BS(4,5)` corridor requiring flow`q=-7`,
beyond either initial fixed box. The result passes the independent event
decoder. An initial planted pinch word was replaced because cyclic reduction
already removed its intended stable-letter pair before the test; this was a
test-input issue and did not require changing the compiler.

The initial prose also misread `XZZyxzzz`: exact expansion places the extra
`y` **before** the positive `x`, yielding `BS(5,6)`, not `BS(4,7)`. The note
above is corrected; exact code and original certificates always used the
computed exponents. The three displayed donor-family expansions are now
checked directly as `BS(4,5)`, `BS(6,7)`, and `BS(5,6)`.

For endpoint-rank bounds, reuse Section2 of
[`THEOREM_NOTE.md`](../rank_unbounded_20260912/THEOREM_NOTE.md): after singleton
cleanup a balanced unimodular tuple has `L>=2r+1`. Hence any strict improvement
from a baseline of length at most21 has rank at most9 at that cleaned boundary.
Higher ranks can still be useful intermediate states; this is not a search
rank ceiling or a new stable-AC obstruction.

## Measured scope of the complete-flow exclusion

The parent process ran the root diagnostic serially and saved
`flow_exact_diagnostic.json`. Among43 root-bearing rows inspected from the
124-row baseline, all33 recognized BS-corridor cases completed the sufficient
flow search. None supplied a cheaper flow or a newly shorter presentation.
The diagnostic used11,191 total work units and0.063 CPU seconds across rows;
the per-row allowance remained1000.

This is a complete exclusion of cheaper integer flows **for those fixed root
and BS donors and the retained Britton-reduced stable corridors**, not a
failed small-box screen. It gives a specific reason to change donors or
coordinates. It does not exclude different ordinary AC products, a different
subsystem normal form, longer intermediate stable words, or additional
generators. These campaign figures are attributed to the parent's serial
run; this worker ran no census campaign.

## New direction: expose a primitive root while retaining its helper

`theory_primitive_root.py` handles a defining donor `z=w^k`, `k>=2`, where
the shortest cyclic root `w` is not already a single generator. A concrete
example is the first donor of the displayed `aca_13` state, `XYXYz`, which
says `z=(yx)^2`. The basis change fixing `x,z` and mapping old `y` to `yX`
turns this into `z=y^2`. This illustrates a possible preparer; no gain on
that census row is asserted here.

The preparer differs from immediate Lemma11 elimination of `z`: it keeps
`z` and every other relator, and changes the basis to expose the power
structure. Subsequent root/corridor macros can therefore act on a retained
short definition that was previously written in a longer primitive word.

The exact construction has two parts.

1. If a canonicalization witness gives `v=c^-1 u^s c` for the current helper
   definition `z=u`, with `s=+1` or`-1`, apply the ambient map
   `z -> c z^s c^-1`, fixing all other generators. Its inverse maps
   `z -> c^-1 z^s c`. Since `u,c` avoid `z`, both inverse compositions are
   exact. The defining donor then becomes `z=v` up to its recorded relator
   conjugation/inversion normalization. This absorbs conjugated powers
   without silently changing the helper's meaning.
2. Form the Whitehead graph of the shortest cyclic root of `v` alone.
   Apply a length-decreasing cut map to the entire tuple; the helper stays
   fixed because it does not occur in that graph. Recanonicalize its updated
   definition using the first part, and repeat while work remains.

Every accepted cut has its selected-root length formula checked independently
from its whole-tuple length change. Canonical row sorting transports the
defining donor's index through explicit normalization witnesses. A recognized
primitive root is accepted only when its final exact defining word uses one
signed generator. An exponent vector or a local minimum supplies no such
recognition. A partial or nonprimitive-root descent is still a valid basis
change candidate, labelled without a primitive-root claim.

The API is `probe(words, remaining) -> (candidates, charged)`, with arbitrary
signed integer generator IDs and an allowance in0..1000. Each tested
defining-row/helper pair, helper-frame map, and minimum cut costs one unit,
including unsuccessful checks. Already pure power definitions are skipped;
there is no total-length or rank ceiling. The output uses the existing
`ambient_automorphism`, `ambient_whitehead`, and normalization event schemas
and so composes with the independent verifier and both corridor modules.

Twenty-four planted/budget controls passed full independent JSON event replay.
They cover ordinary and sparse generator IDs, a conjugated cube, and a
commutator-square definition whose root was correctly **not** promoted to a
primitive root. Budgets0,1,2,5,20,100 were checked. All complete control runs
used8 work units; this is validation of the mechanism, not an empirical U124
coverage result.

## New direction: change the retained root metric

The fixed-root exclusion leaves a different basis choice open. If the retained
definition is `z=y^k`, then the ambient Nielsen shear

\[
 z\longmapsto y^{k-\ell}z,
 \qquad z\longmapsto y^{\ell-k}z\text{ for the inverse},
\]

fixing every other generator, changes that definition to `z=y^ell`. After
expanding the new helper, every original target has the same old-generator
image as before. The underlying BS exponents and corridor stay fixed, while
their short-spelling cost changes from `c_k` to `c_ell`. No new generator or
unsupported root-taking operation is introduced.

`theory_root_metric.py` optimizes this route on rank-three tuples. After a
complete no-pinch check, a candidate absolute denomination `ell>=1` has
retained-donor cost

\[
 (\ell+1)+2+c_\ell(m)+c_\ell(n).
\]

For a starting total length `L` and `t` stable letters in the companion, a
strict improvement therefore permits only companion root cost

\[
 C=L-1-(\ell+1)-2-c_\ell(m)-c_\ell(n)-t.
\]

Negative `C` excludes that denomination immediately. The retained defining
relator itself costs `ell+1`, so the candidate range is finite; the code uses
the loose safe range `ell<=L-t-4` and then applies the exact cost test above.
It prioritizes denominations near `m/2`, `n/2`, `|k|+1`, `|k|-1`, `m`, and
`n`. Both signs of a feasible denomination share one metric optimization but
produce separately charged, explicitly certified shears.

The sparse complete-flow routine optimizes this new cost using the proved
sufficient flow bounds. To compile a candidate, first apply the selected
flow in the original basis, then apply the shear, then cyclically repack both
remaining relators using the new root relation. This ordering preserves the
original corridor's indexing and avoids silently transporting a flow vector
through canonical inversions or rotations. Temporary lengths can increase.
Every resulting strict-gain prediction is checked against the full final
tuple length and independently replayed.

The wrapper deliberately excludes inputs with an existing Britton pinch;
those should pass through `theory_flow_exact.pinch_prefix` first. It also
excludes rank other than three, where the displayed total-cost formula would
omit additional relators. These are sufficient-recognizer boundaries, not
claims about the algebraic possibilities outside them. The current absolute
denomination is skipped because it is the already tested fixed metric.

The API is `probe(words, remaining, audits=None)`. Each BS-donor test,
cyclic-pinch test, absolute-denomination test, sparse DP transition, and
compiled signed rebase costs one. Its allowance remains0..1000, and failed
or incomplete cases remain in the returned charge and optional audit list.
The witnesses use existing ambient-map and ordinary-normal-product schemas.

Thirty-six signed shear/repacking certificates passed independent JSON event
replay for `BS(4,5)` and `BS(6,7)`, both old-root signs, four new signed
denominations, and three flow values. Six budget controls passed. On the
planted one-stable-letter `BS(4,5)` case, allowance1000 used369 units and
returned12 strict candidates across different retained metrics; no census
coverage is inferred from this positive control.

The parent's subsequent serial pilot found a new exact gain on `aca_101`,
21 to20. Its certified route changes retained exponent7 to4, temporarily
raises total length21 to24, then cyclically repacks to20. The saved
`root_metric_pilot.json` chain passes the independent record verifier.
This is an empirical gain from changing the metric, beyond the earlier
complete fixed-root flow exclusion. The pilot contained nine rows and used
4,375 heterogeneous work units and0.033 CPU seconds; it was not run by this
worker. The full-census follow-up is recorded separately by the parent.

## Higher-rank extension: a triangular two-power metric

`theory_multi_metric.py` raises rank3 to4 and retains two power generators.
For integers `2<=l<k`, keep the triangular definitions

\[
 u=y^l,\qquad z=y^a u^b,\qquad a+lb=k,
 \qquad |a|+|b|=c_l(k).
\]

Their combined length is `l+2+c_l(k)`. All other relators can be spelled
in the signed coin metric

\[
 c_{l,k}(e)=\min_{b\in\mathbb Z}\bigl(|b|+c_l(e-kb)\bigr).
\]

This formula is exact: any word over `y,u,z` has signed exponent counts
with value `e`; collecting those counts never increases its length.
Conversely every triple of counts supplies a word of the displayed cost.
The incumbent `c_l(e)` bounds `|b|` in a minimum, so the implementation
checks only `-c_l(e)<=b<=c_l(e)`. Arbitrary orderings of the commuting
power letters are not needed to achieve this minimum. Their commutation
is used only modulo the retained defining donors, with exact correction
factors supplied below.

The previous flow matrix and opposite-sign residue invariant are unchanged.
For total companion root-cost ceiling `C`, every affordable exponent vector
satisfies `sum |e'_i|<=k C`. Substituting `K=k` into the already proved
inverse-matrix estimate gives a sufficient finite box for **all** flows
that can meet that cost ceiling. `_flow` searches that box through sparse
divisibility transitions, using `c_{l,k}` as its additive cost.

There is also a finite complete list of denomination pairs for this specified
endpoint family. Let `t` be the companion's retained stable-letter count and
let `v` count cyclic adjacent stable letters of opposite sign. After a complete
no-pinch check, all these `v` separating exponents remain nonzero for every
flow, so their total coin cost is at least `v`. Both BS powers are nonzero,
and hence its donor costs at least4. Put `d=c_l(k)>=2`. Any endpoint in this
family therefore has length at least

\[
 l+2+d+4+t+v=l+d+t+v+6.
\]

To beat input length `L`, necessarily

\[
 2\le l\le L-t-v-9,\qquad
 2\le d\le L-t-v-l-7,\qquad
 l<k\le l\,(L-t-v-l-7).
\]

The last bound follows from `|k|<=l c_l(k)`. The implementation enumerates
this finite superset, then tests the exact definition and BS-donor costs
before invoking the complete-flow routine. With their actual costs, the
companion's allowed cost is

\[
 C=L-1-[l+2+c_l(k)]-[2+c_{l,k}(m)+c_{l,k}(n)]-t.
\]

`C<v` excludes the pair without flow search. Positive denominations lose
no coin-cost possibilities from changing their signs; explicit ambient
shears orient the retained generator as required.

The certificate construction is deliberately triangular. It first compiles
the chosen corridor flow using the old donors and old root metric. It then
shears old `z` to exponent `k`, adds `u=y^l` with a standard defining-addition
witness, and rewrites the old defining row using **only** the new `u` donor.
The latter ordinary operation produces `z=y^a u^b`. The exact power identity
`z^-1 y^k` is then reconstructed as a normal product of these two retained
defining rows. Neither BS nor companion is among those factors. Expanding
and repacking each of these two remaining rows therefore gives ordinary
normal-product substitutions that do not use their own target as a donor.
Canonical row sorting transports every donor index. Every word identity is
checked in the compiler before returning it.

The module keeps all four relators. Intermediate length growth is allowed,
and the new helper may initially occur only in its defining donor. Definition
addition and the ambient basis changes use the established known-trivial
stable-AC lineage; all subsequent donor products have explicit factors.
This is neither an ordinary-AC-only stream nor an assertion that every
unimodular tuple admits the stable macros.

The API is `probe(words, remaining, audits=None) -> (candidates, charged)`,
with allowance0..1000. Tested BS models, cyclic pinches, denomination pairs,
sparse flow transitions, and final compiled constructions each cost one.
Exact coin arithmetic is part of evaluating these work units; they are not
CPU-operation counts or elementary-move counts. Existing cyclic pinches
and non-rank3 inputs are excluded by the current wrapper. The finite pair
bound is complete for this triangular two-power endpoint family with the
same BS donor and stable corridor; a budget may stop before all pairs or
flows complete. It says nothing about other higher-rank definition networks,
different relator products, or longer intermediate stable corridors.

`theory_multi_metric_checks.py` reproducibly verifies26 exact metric values
against686 independently enumerated coefficient triples, six complete
one-stable-letter flow optima including negative BS exponents,18 signed
flow/shear/add/repack chains, and six budget controls. All chains replay
through JSON in the independent verifier. The known-trivial planted tuple
has companion `x y^11`, so substituting `x=y^-11` into its BS(4,5) donor
forces `y=1`; its root donor then forces `z=1`. At allowance1000 the wrapper
returns seven strict rank4 candidates on this plant. Results and the tested
module hash are saved in `theory_multi_metric_checks.json`; this worker
performed no census evaluation.

## Stable-letter power shifts add no missing consecutive-BS flows

The apparently different ambient family `x -> y^p x y^q`, fixing the base
and every power helper, preserves the BS donor up to conjugation:

\[
 \phi(x^{-1}y^mxy^{-n})=y^{-q}(x^{-1}y^mxy^{-n})y^q.
\]

Write each stable-letter sign as `epsilon_i=+1` or`-1`. The exponent in the
following cyclic gap changes by `(p+q)v_i`, where
`v_i=(epsilon_i+epsilon_{i+1})/2`. In particular, opposite-sign gaps do not
change. For the already defined flow matrix `M`, direct substitution gives

\[
 M\mathbf1=(m-n)v.
\]

When `|m-n|=1`, the constant integer flow
`q_i=(p+q)/(m-n)` therefore produces exactly the same expanded cyclic
companion as this shear. A complete flow optimization in a fixed power
metric already includes every such stable-letter shift. The statement
includes shifts written as powers of retained root generators, since their
expanded values are base powers. The proof is at the cyclic-word level and
does not claim that the two certificate streams are identical.

Twenty-four direct free-word checks cover both consecutive orientations,
positive and negative single stable letters, two mixed-sign cyclic patterns,
and three signed `(p,q)` choices. They verify the donor conjugation, the
cyclic gap formula, and the constant-flow identity, including the wrap gap.
For general `m-n`, only shifts with `m-n` dividing `p+q` are supplied by
this constant-flow argument. The balanced unimodular rank3 root/BS criterion
is what makes all shifts redundant in the current recognized U124 cases.

## Stronger fixed-donor exclusion for the current short companions

This section derives a corollary from the HNN normal-form and conjugacy
theorems. The primary research source used is Borovik, Myasnikov and
Remeslennikov, [*Conjugacy problem in HNN-extensions: regular elements and
black holes*](https://eprints.maths.manchester.ac.uk/991/1/OmskVestnik.pdf),
Section2.2 and Theorem3.9 (printed pages3 and9). The source states that
reduced HNN forms have invariant stable length, and that conjugate cyclically
reduced elements of positive stable length have the same length; one obtains
the conjugacy by a cyclic permutation and an associated-subgroup conjugation.
It also gives the standard coset normal forms. The length corollary below
is our deduction, not a theorem claimed to appear verbatim in that source.

First fix the root donor `z=y^k` and the BS donor, so that their quotient
is `G=BS(m,n)`. More generally, a fixed triangular system of power definitions
is allowed. Let `c(e)` be the exact signed coin cost of a base power in the
chosen generating alphabet. This is a **fixed** alphabet and fixed metric.

For cyclically Britton-reduced words of positive stable length, the HNN
normal forms identify all possible conjugate cyclic words as follows: rotate
the cyclic stable sequence, then transfer associated-subgroup powers across
its stable edges. At edge `i`, the transported powers are exactly
`y^(A_i q_i)` and `y^(B_i q_i)` for an integer `q_i`. Counting each transfer's
contribution to its two adjacent gaps gives

\[
 e'_i=e_i-B_iq_i+A_{i+1}q_{i+1}.
\]

Conversely each such transfer is a BS relation, as explicitly certified
earlier. The seam transfer includes the associated-subgroup conjugator in
the HNN conjugacy theorem; an outer base conjugation disappears on viewing
the word cyclically. Thus rotations together with the integer-flow formula
describe the whole cyclically Britton-reduced conjugacy class. Rotation
only reindexes the additive cost, so it creates no additional minimum.
This conclusion uses the full conjugacy criterion, not only equality of
stable exponent sums.

**Short-companion corollary.** Suppose a companion is cyclically
Britton-reduced with stable length `t>=3`, stable exponent sum `+1` or`-1`,
and fully packed length `t+C0` with `C0<=3`. If complete integer-flow
optimization finds no cost below `C0`, it is a shortest word in its
conjugacy class in `G`, measured in the chosen power-generating alphabet.

To prove this, take a shortest freely and cyclically reduced competing word
`V`, and let `T` count its stable letters before expanding the power helpers.
Cyclic Britton reduction cannot increase `T`; HNN conjugacy invariance forces
`T>=t`. Stable exponent sum is still `+1` or`-1`, so `T` and `t` are odd.
If `T>t`, then `T>=t+2`. Both stable signs occur, and cyclic free reduction
requires a nonempty power-letter gap at each of at least two transitions
between those signs. Consequently `|V|>=T+2>=t+4`, which is larger than
the available word of length at most `t+3`. Therefore `T=t`. Expanding
helpers and Britton-reducing `V` cannot remove a stable pair, because that
would give a conjugate of cyclic stable length less than `t`. Its expanded
cyclic form is consequently covered by the integer-flow formula. Repacking
its base powers only improves its spelling, so the completed cost minimum
excludes a shorter `V`. Inverting the companion has the same minimum by
the symmetry of word length.

This reasoning specifically rules out shorter representatives that hide
additional Britton pinches: the extra stable letters already cost too much.
For larger `C0`, no such conclusion follows; a pinch may encode a large
base power economically. This caveat agrees with Diekert and Laun,
[*On Computing Geodesics in Baumslag–Solitar Groups*](https://arxiv.org/pdf/0907.5114),
Section3 (printed page6), which explicitly distinguishes Britton reduction
from shortest-word computation.

Read-only assertions on `flow_exact_diagnostic.json` verify the corollary's
recorded hypotheses for all33 recognized cases: all have `t=5`, stable
exponent sum of absolute value1, zero required Britton-prefix events, exact
complete flow searches with no cheaper result, and actual companion length
equal to the packed cost. Two companions have length7 and31 have length8.
No search was rerun to obtain this classification.

Accordingly, those33 saved companions cannot be shortened by **any** sequence
of ordinary products with the two fixed donors, target conjugations, and
target inversions, regardless of intermediate length. This remains a local
statement about that one relator and those fixed donors. Allowing a donor
to acquire companion factors, changing the ambient power metric, adding new
generators, or modifying multiple relators leaves the hypothesis. It is not
an AC-nontriviality result, a proof of presentation minimality, or a claim
that the current U124 list consists of distinct AC classes.

## Donor-changing direction: an abelianization-preserving commutator pair

A single change `R -> R W^j` shifts a BS donor's stable exponent by `j`
times the companion's nonzero stable exponent; with `j!=0` it cannot itself
land in a two-stable-letter BS donor. A paired ordinary operation avoids
that obstruction:

\[
 R\longmapsto R[W,g]=R W^{-1}g^{-1}Wg.
\]

Its exact normal-product factors are `(donor=W, sign=-1, conjugator=1)`
followed by `(donor=W, sign=+1, conjugator=g)`. The companion stays fixed.
The correction has zero exponent sum in every generator, so it preserves
the entire abelianization vector of `R` while changing the nonabelian donor.
The intermediate `R W^-1` may be longer even when the final paired result
has useful cancellations, so this macro supplies a concrete route beyond
strict or equal-length individual rewrite searches. Testing signed letters
and cyclic prefixes of `W` for `g`, then applying exact root/BS recognition
to the final row, is a proposed sufficient search. No U124 gain or exhaustive
exclusion for this new donor-changing family is claimed here.

## Higher-rank extension: retain two stable spellings

`theory_stable_metric.py` keeps the root definition and the old stable letter
`x`, while adjoining a new helper

\[
 h=y^p x y^q.
\]

The two base powers in this definition are stored in their shortest old-root
spellings, so its defining relator has length `2+c_k(p)+c_k(q)`. This is a
different generating alphabet from a uniform stable-letter shear: each
occurrence can now independently use `x` or `h`, and both remain available.

For a sign `s_i` and choice bit `b_i`, define the inserted prefix/suffix
pair `(P_i,S_i)` as `(0,0)` when `b_i=0`, `(p,q)` when `b_i=1,s_i>0`,
and `(-q,-p)` when `b_i=1,s_i<0`. After integer BS flow, its remaining
cyclic gap is

\[
 g_i=e_i-B_i f_i+A_{i+1}f_{i+1}-S_i-P_{i+1}.
\]

The companion cost in this specified family is
`t+sum c_k(g_i)`. For fixed helper parameters and an expanded cyclic word,
the best bits are obtained by a two-state cyclic dynamic program: the gap
cost depends only on its two adjacent bits. This gives exact repacking
without searching arbitrary words over the expanded alphabet.

For the BS donor itself, the two bits have difference `delta` in
`{-1,0,1}`, giving exact packed donor cost

\[
 B(p,q)=2+\min_{\delta\in\{-1,0,1\}}
       [c_k(m+p\delta)+c_k(n-q\delta)].
\]

The retained root donor costs `|k|+1`. To beat total length `L`, the
companion cost ceiling is therefore

\[
 C=L-1-(|k|+1)-[2+c_k(p)+c_k(q)]-B(p,q)-t.
\]

Since `B(p,q)>=2`, only parameters satisfying

\[
 c_k(p)+c_k(q)\le L-|k|-t-6=:D
 \quad\text{and hence}\quad
 |p|,|q|\le \max(1,|k|)D
\]

can improve the tuple. This is a finite endpoint-derived list, not an
intermediate word-length cap. The code prioritizes offsets near the root
exponent and BS powers, then lazily traverses this finite box. It charges
the tested parameter pairs even when the exact cost bound rejects them.

For each bit pattern, apply the previous complete-flow routine to the
shifted exponent vector `e_i-S_i-P_{i+1}`. When `C=0`, every desired `g_i`
must be zero, and the nonsingular flow matrix gives the unique rational
solution

\[
 f=-M^{-1}(e-S-P_{\rm next}).
\]

Thus one exact integrality test is a complete flow decision for that pattern;
there is no small-box approximation. When `C>0`, the established sufficient
finite-box DP applies instead. Singular flow matrices remain explicitly
incomplete. Cheap residue tests reject impossible zero-cost patterns before
the rational solve: opposite-sign gaps retain their residues modulo their
associated BS divisor. In particular a positive/negative transition needs
its original residue to equal `q` or`-q` modulo `n`, and a negative/positive
transition needs `p` or`-p` modulo `m`. The bit-specific test then fixes
the relevant sign of each offset.

There is a useful preflight bound for the33 old fixed-root diagnostics.
The triangle inequality for `c_k` gives

\[
 [2+c_k(p)+c_k(q)]+B(p,q)-[2+c_k(m)+c_k(n)]\ge2.
\]

So adjoining one stable spelling increases the combined defining/BS-donor
cost by at least2. With old companion power cost at most3, any strict gain
in this family must have old cost3, zero new power cost, and donor overhead
exactly2; the total gain can only be one letter. These are properties of the
33 saved starting metrics and must be rechecked after another metric change.

This also proves that a **one-sided** helper cannot improve those33 states.
For `p=0`, every negative/positive gap keeps its nonzero Britton residue and
needs at least one power letter; for `q=0`, positive/negative gaps do so.
Both transition types occur because `t>=3` and stable exponent is `+1` or
`-1`. A two-sided helper can affect both types. For example, in the syntactic
`k=2, BS(4,5)` model, `p=-2,q=4` has donor overhead exactly2 and neither
offset is divisible by its corresponding BS divisor. This passes necessary
arithmetic gates; it is not a claim of a U124 gain.

To compile, first perform the chosen flow with the old donors. Adjoin the
helper with a literal defining-addition event, leaving all old relators
present. Repack the BS donor and companion using only the root and helper
defining rows as normal-product donors. The helper's negative image has a
base prefix, so the compiler explicitly compensates the first atom's prefix
in its cyclic frame before constructing its exact word identity. It then
transports donor indices through each canonical sort. This avoids silently
turning a cyclic equality into an incorrect free-word certificate.

The API is `probe(words, remaining, audits=None) -> (candidates, charged)`.
Each attempted BS model, cyclic-pinch check, signed parameter pair, atom-bit
pattern, rational flow solve or sparse-DP transition, and compiled candidate
costs one. The allowance is0..1000. The public wrapper currently recognizes
rank3 inputs with no existing cyclic Britton pinch and creates rank4 outputs;
there is no intermediate length cap. Finite pair and per-pattern completion
claims are local to this retained-spelling family. The known-trivial stable
lineage is needed for definition addition; all subsequent donor operations
have explicit ordinary-AC normal products.

`theory_stable_metric_checks.py/json` records a passing reproducible control
set:252 independently enumerated atom patterns check18 cyclic bit optima;
36 signed flow/add/repack chains pass full JSON replay; six allowance controls
pass. A separate known-trivial plant exercises68 exact zero-cost rational
solves, all producing replayed strict candidates within647 units. Its longer
one-stable-letter control returns15 strict candidates at allowance1000.
These are mechanism controls, not coverage claims. No census run was made
by this worker.

### Exact cost-ball enumeration for retained stable spellings

The frozen `theory_stable_metric_v2.py` preserves the first implementation
and changes how its finite parameter set is generated. It enumerates all
coefficient pairs `(a,b)` with `|a|+|b|<=D`, collecting their values `a+kb`
and minimum costs. There are exactly `2D^2+2D+1` such coefficient pairs;
each is charged, including duplicates of an exponent value. This produces
the complete ball `{e:c_k(e)<=D}` with exact costs. Cost buckets then emit
only `(p,q)` with `c_k(p)+c_k(q)<=D`, each once. Every emitted parameter
pair is still charged. This avoids spending the small work budget on the
many impossible pairs in a surrounding coordinate box.

The optional audit records the exact ball and distinguishes enumeration of
all parameter pairs from completion of every flow calculation. Its
`parameter_family_complete` flag is true only when both have finished;
budget exits or an incomplete flow cannot acquire that flag. Existing
bit-pattern and exact word-certificate machinery is unchanged.

`theory_stable_metric_v2_checks.py/json` replays the inherited controls and
checks12 complete signed cost balls and428 admissible parameter pairs
independently. All pass. The zero-cost planted run now completes68 certified
strict candidates in468 charged units. The source version and tested hash
are retained separately from the first implementation.

## Safe conjugate-base bridges and an invalid consequence replacement

Adjoin `h=X y^e x`, where `X=x^-1`. The old BS equation gives the consequence
`h^m=y^(en)`. Replacing the BS donor by this consequence is generally invalid.
After eliminating the new defining row in abelianization, the new power
donor has base exponent `e(m-n)` instead of `m-n`. Thus replacing that row
multiplies the balanced tuple's determinant by `e`. For `|e|>1`, it cannot
preserve a unimodular tuple. The extra condition `gcd(e,m)=1` does not remove
this obstruction; a formal Bezout root expression is not an invertible
relator replacement certificate.

There is, however, a direct safe divisor case. If `e>0` divides `m`, then

\[
 Xy^mxy^{-n}\longmapsto h^{m/e}y^{-n}
\]

is an exact substitution using only the new defining donor. Expanding
`h^(m/e)` freely gives `X y^m x`, so the usual expansion/repacking identity
supplies an ordinary normal-product certificate. Similarly, adjoining
`h=x y^e X` when `e` divides `n` gives the reverse-orientation version.
No old donor is discarded or replaced by an unsupported consequence.

`theory_conjugate_bridge.py` implements these divisible helpers. The old
root helper stays available. The new definition has length `3+c_k(e)`,
and the rewritten BS donor can have length `|m/e|+c_k(n)`. In the common
syntactic case `m=2k,n=2k+1,e=k>=2`, the old BS donor costs7, the new helper
definition costs4, and the repacked BS donor costs5: combined donor cost
increases by2. Repacking one companion block `X y^(kj) x` as `h^j` saves2,
so this supplies a neutral rank increase when that block is present. It is
intended as an intermediate state before other operations, not a promise
of a direct shortening.

The compiler examines cyclic rotations and uses interval tokenization to
select nonoverlapping blocks `x^s y^(ej) x^-s`, replacing them by `h^j`.
Other base blocks retain their shortest old-root spellings. It preserves
an explicit cyclic frame, expands the packed candidate back to the original
free word, and constructs its normal-product factors using only the retained
root and new helper rows. The BS donor is processed first, followed by every
other nondefining relator. Canonical normalization witnesses transport all
row indices.

The wrapper returns the intermediate bridge even if it is neutral or longer.
It separately applies whole-tuple Whitehead descent and length-nonincreasing
Lemma11 peeling, retaining a distinct cleaned endpoint as another candidate.
This avoids losing a useful intermediate solely because cleanup returns to
the starting rank. A per-branch work allowance reserves cleanup work; there
is no intermediate length or rank cap. Unlike the rank3 metric wrappers,
this API can process a recognized root/BS subsystem in an arbitrary-rank
tuple and repacks all remaining relators.

The API is `probe(words, remaining, audits=None) -> (candidates, charged)`.
BS-model and divisor attempts, defining additions, tested cyclic rotations,
Whitehead cuts, and peeling attempts are charged, including failures. A
truncated rotation scan can still return its explicitly verified best
candidate, with `repacking_complete=False`; that flag is not a complete
normal-form claim. The known-trivial stable lineage is required for helper
addition, ambient basis normalization and Lemma11 cleanup. Ordinary packing
steps have fully explicit donor products.

`theory_conjugate_bridge_checks.py/json` records ten signed divisor chains,
six budget controls, and a sparse-generator control with largest input ID
`10^25`; every returned event chain passes independent JSON replay. The
complete ordinary-label planted run uses313 units and returns six distinct
bridge/cleanup candidates. This validates the construction and ledger;
no census evaluation was performed by this worker.

### A controlled longer-state composition

In the `m=2k,n=2k+1,e=k` bridge, one convenient oriented donor is
`h^2 z^-2 y^-1`. It isolates `y=h^2 z^-2`, so Lemma11 elimination of `y`
turns the old root relation into `z=(h^2 z^-2)^k`. The relation `h=X z x`
remains. This gives a longer rank3 state with a different root word, suitable
for a subsequent definition exchange. It must use the actual normalized
row's isolation witness: a different ordering of old commuting power
letters may instead isolate `z^-2 h^2`, and `h,z` cannot be commuted freely.
For the checked `k=2` control, the normalized row `(-4,-4,2,3,3)` has exact
isolation word `(4,4,-3,-3)`; the Lemma11 event replays independently.

The root word `h^2 z^-2` is nonprimitive in the free group on `h,z`: its
exponent vector `(2,-2)` is not primitive in integer homology. An ambient
automorphism therefore cannot expose it as a single generator. The resulting
power row is a route toward different overlapping definitions or donor
operations; it is outside the primitive-root preparer's sufficient family.
This conclusion concerns that explicit root word and basis, not every
presentation obtained after further relator operations.

### Forced base elimination followed by a different dictionary

The separate frozen `theory_conjugate_exchange.py` composes this bridge with
an explicit one-occurrence elimination of the original base generator. It
does so even when the resulting total length increases. The row used for
elimination is selected from the actual bridged tuple, and its exact
`isolating_word` is the substitution used in every other row. No commutation
of the surviving helper letters is presumed.

Before comparing final lengths, the wrapper tries up to six repeated-word
definitions in the expanded tuple and applies whole-tuple Whitehead descent
and nonincreasing Lemma11 peeling. It excludes the exact isolation word and
its inverse from that definition list, because those would simply reinstate
the removed generator. Different subwords remain eligible. The intermediate
bridge, the tuple after elimination, and the new compressed tuples are
retained as candidates as well as their cleaned endpoints. There is no
intermediate rank or length cap.

The API is `probe(words, remaining, audits=None) -> (candidates, charged)`;
its public work allowance is0..1000. Every attempted model, divisor, addition,
cyclic packing cut, base removal, candidate compression, Whitehead cut and
peeling attempt is charged. The search is a bounded sufficient family:
six definitions and the per-bridge allocation do not claim complete
dictionary exchange. A partial bridge still has exact word certificates;
`bridge_repacking_complete` only reports whether its cyclic packing scans
finished. Stable events require a known balanced trivial-group input and
retain their theorem-backed status instead of claiming an expanded elementary
move stream.

`theory_conjugate_exchange_checks.py/json` records six signed planted inputs
and136 replayed direct chains. Of those chains,119 include an uphill base
removal and118 include a subsequent new definition. Six budget controls,
sparse generator labels through`10^25`, and an unnormalized input all pass.
These are repeated certificate checks on six known-trivial plants, not136
distinct group problems or a census-coverage measurement.

### A retained-donor central-power rule after base elimination

The new two-generator donor has more structure than an arbitrary repeated
word. Put `w=h^2 z^-2` and `D=z^-1 w^k`. In the quotient by `D`, set `y=w`.
Then `z=y^k` and `h^2=y z^2=y^(2k+1)`. Conversely the equations
`h^2=y^(2k+1)` and `z=y^k` give `w=y`. Thus this donor presents the same
two-generator group as `h^2=y^(2k+1)`. In particular `h^2` commutes with
`z`; this does not assert that `h` commutes with `z`.

For `k>=1`, the donor itself is also nonprimitive in the free group on
`h,z`. Sending `h` to an involution and `z` to an element of order`2k+1`
gives a quotient onto the nonabelian free product `C_2 * C_(2k+1)`, since
`D` maps to `z^(-2k-1)`. A primitive relator in rank two would leave the
cyclic free group as its quotient, which cannot have this nonabelian quotient.
This is an explicit obstruction to primitive exposure of that donor alone;
the central consequence supplies a different useful operation.

More generally suppose an oriented retained donor is

\[
 D=z^{-1}w^k,\qquad w=h^d z^a.
\]

The following is a free-word identity, with no group-triviality hypothesis:

\[
 C=z^{-1}h^d z h^{-d}=D\,w\,D^{-1}\,w^{-1}.
\]

Indeed the right side freely reduces to `z^-1 w z w^-1`; the powers
`z^a` then cancel across the intervening `z`. In the convention
`c^-1 R^sign c`, the two factors are `(D,+1,c=1)` and
`(D,-1,c=w^-1)`. If the recognized `D` is a rotation or inverse of the
stored donor, its exact orientation conjugator is composed into these
factors. The original donor stays in the tuple throughout.

Consequently every block `z^s h^(dj) z^-s`, with `s=+1` or`-1`, can be
replaced by `h^(dj)` using ordinary products with that retained donor.
The compiler obtains the signed single-power correction from `C` and
telescopes it over `j`; negative `j` uses its inverse correction. For a
cyclic occurrence it also retains the rotation frame in every conjugator.
The replacement removes two letters before any additional cancellations,
so each accepted normalized endpoint strictly decreases total length.

`theory_central_pinch.py` recognizes this sufficient two-block power syntax
and applies these pinches to all other rows, transporting donor indices
through normalization. It can act in any rank and does not remove or
replace the donor by its consequence. Its public API is
`probe(words, remaining, audits=None) -> (candidates, charged)`. Every donor
preflight, tested signed cyclic orientation, and tested pinch position is
charged, including failures. Half the allowance is reserved for recognition;
the rest remains available for exact reductions. A truncated recognition
scan is not a complete donor-family exclusion.

The separate frozen `theory_conjugate_exchange_central.py` reserves half
its0..1000 allowance for the original conjugate exchange. It then runs the
central rule on retained candidates ending with the forced base removal,
and applies bounded whole-tuple Whitehead/peeling cleanup to strict outputs.
The stable prefix still needs known triviality; the central steps themselves
are explicit ordinary-AC normal products and require no such premise.

`theory_central_pinch_checks.py/json` verifies48 signed consequence identities
and48 signed pinch chains, including36 nontrivial cyclic frames. Both APIs
pass six allowance controls, and a rank-four control preserves all rows with
generator labels through`10^25`. A known-trivial rank-three plant of length25
has two fully replayed composed paths containing the bridge, forced removal
and central pinch; the shortest recorded endpoint has length13 within623
charged units. This is a planted mechanism check, not a new U124 gain.

### Full torus collection recovers the donor, not just one consequence

Let `D=z^-1(h^d z^a)^k`, with `d,k>=1`, `a<0`, and put
`c=h^d`, `w=c z^a`, and `n=1-ak>0`. The retained donor supplies both
`[c,z]=1` and `c^k=z^n`. Together these recover `D`: commutativity gives
`(c z^a)^k=c^k z^(ak)=z^(n+ak)=z`. Consequently

\[
 \langle\!\langle D\rangle\!\rangle
 =\langle\!\langle z^{-1}czc^{-1},\;c^kz^{-n}\rangle\!\rangle.
\]

This equality of normal closures is used to rewrite other relators while
retaining `D`; it does not authorize replacing one donor by two rows.
The power relation alone is strictly weaker when `k>1`: in the free product
`C_(dk)*C_n`, let `h,z` be the standard generators. Then `h^(dk)=z^n=1`,
whereas `z^-1(h^d z^a)^k` has a nonempty reduced free-product form.
Here `h^d` has order`k>1` and `gcd(a,n)=1`. Thus the power consequence
cannot replace the full donor even though their exponent vectors agree.

The group defined by `D` is `H=<h,w | h^d=w^n>`, with `z=w^k`.
Since `gcd(k,n)=1`, the powers `z^r`, `0<=r<n`, form a transversal for
the central subgroup`<c>` in the cyclic`w` factor. Amalgamated-product
normal forms therefore give a unique expression `c^Q U`, where `U` is
an alternating word in residues `h^r` with`0<r<d` and `z^s` with`0<s<n`.
The central coordinate changes by1 when an`h^d` block is extracted and by
`k` when a`z^n` block is extracted. The primary reference for the central
subgroup and quotient normal forms of torus groups is Elder, Elston and
Ostheimer, [*On groups that have normal forms computable in logspace*](https://arxiv.org/pdf/1201.4363),
Lemma34 and Corollary35, printed page14. The following metric optimization
in the retained`h,z` alphabet is derived here.

Suppose the nonzero`h` residues of`U` are`r_1,...,r_H`, and the nonzero`z`
residues are`s_1,...,s_Z`. Include one extra zero-residue slot of each type
to allow a separate central block. For an integer`A`, define

\[
 f_h(A)=\min_{\sum A_i=A}\sum_i|r_i+dA_i|,
 \qquad
 f_z(B)=\min_{\sum B_j=B}\sum_j|s_j+nB_j|.
\]

The minimum length of this element over`h,z` is exactly

\[
 \min_{B\in\mathbb Z}\bigl(f_h(Q-kB)+f_z(B)\bigr).
\]

For the lower bound, take any spelling and reduce its image in`C_d*C_n`.
Whenever an entire syllable becomes trivial in that quotient, its original
power block is central; move it aside without changing its length. Merge
newly adjacent powers of the same generator, which cannot increase length.
This leaves the unique alternating residue sequence, with arbitrary integer
central allocations in its surviving syllables and in the two extra slots.
It is a candidate in the displayed minimum. Conversely every such allocation
has central coordinate`Q` and gives a spelling of the desired element.
Thus extra quotient-canceling excursions cannot beat this allocation problem.

The allocation costs are convex piecewise-linear functions on the integers.
For a nonnegative allocation, each extra unit costs the modulus. For a
negative allocation, first subtract one modulus from the largest remaining
positive residue; the marginal costs are `d-2r_i` or`n-2s_j` in increasing
order. After every residue has been used, each further unit again costs the
modulus. Therefore`f_h` has breakpoints at`0,-1,...,-H` and`f_z` at
`0,-1,...,-Z`. It suffices to evaluate integer points nearest

\[
 B=-j\quad(0\le j\le Z),\qquad
 B=(Q+j)/k\quad(0\le j\le H).
\]

This is a finite exact optimization depending on the number of syllables,
not an arbitrary box on the central exponent. Its scope is the fixed linear
word metric in this single-donor quotient, not cyclic conjugacy minimum,
total presentation minimum, or stable-AC minimality.

`theory_torus_collect.py` compiles this construction. It first collects
`D=z^-1(c z^a)^k` into`c^k z^-n` using the already certified central
commutations, retaining the normal-product factors in the original`D`.
It then derives the correction for`z^n -> c^k`. Both the incoming block
and its optimized spelling are normalized to the same exact`(Q,U)`;
incoming factors followed by reversed outgoing factors certify the
substitution. Signed powers and cyclic frames are explicit. Other generator
letters separate the processed blocks; the compiler does not silently use
the other relators as extra quotient relations. This single pass is not
claimed to produce a geodesic for an entire mixed-alphabet relator: a block
that vanishes may expose additional outside-letter cancellation and new
adjacent torus blocks for a later pass.

For example`D=z^-1(h^2 z^-2)^2` permits`z^5 -> h^4`. This saves one letter
and contains no central-power pinch. Thus full-donor collection can add an
operation beyond the preceding pinch rule while retaining the new metric.
There is a precise return-to-old-frame route, but it is optional: reintroduce
`w=h^d z^a`, then eliminate the conjugate helper`h=X z x`. The remaining
rows become`z=w^k` and`X w^(dk) x=w^n`, recovering the old root/BS frame.
Keeping`h,z` instead, as this collector does, avoids that particular return.
Eliminating`z` after adjoining`w` is a different conjugated-helper frame,
so no universal claim that every such exchange returns the old metric is made.

Both`theory_torus_collect.py` and the separate
`theory_conjugate_exchange_torus.py` expose
`probe(words,remaining,audits=None) -> (candidates,charged)`, with arbitrary
rank and a shared allowance of0..1000. Model attempts, each central crossing,
each power substitution, each normal-form block and each tested breakpoint
are charged, including abandoned budget-truncated compilations. Every
returned collector event is an explicit ordinary-AC normal product. The
exchange prefix retains its known-triviality requirement. No truncated probe
is labelled a complete scan of all donors, orientations or dictionaries.

`theory_torus_collect_checks.py/json` checks341 signed words through length4,
covering117 normal forms and their shortest enumerated lengths, eleven
independent finite-box comparisons of the scalar convex optimum, and44
signed replay chains. Both APIs pass six budget controls; a sparse rank-four
control preserves all rows. The direct planted probe returns three candidates
within74 units, and the composed wrapper control returns31 within772 units.
These controls do not establish any new census gain or AC-counterexample
evidence; all general negative conclusions remain restricted to their stated
families.

The independent [torus audit](verification_torus.json) passes85 separate
signature/word-ledger controls, nine allocation minima computed without
reusing the compiler's allocation helper, and22 signed sparse rank-four
chains. It also checks all33 saved pilot records: there are no new strict
gains beyond their available seeds. Those bounded composed probes do not
turn the exact block-metric theorem into an exclusion of every bridge,
conjugacy frame, mixed-alphabet word, or stable-AC path.

### Multiple stable spellings alone cannot evade the old short-cost bound

For `r` additional flat helpers `h_j=y^(p_j)x y^(q_j)`, the defining rows
cost `2r+sum_j[c_k(p_j)+c_k(q_j)]`. The BS donor uses only two stable atoms;
the triangle inequality bounds its saving by the summed power costs of
their definitions, and hence by the sum over all helpers. Therefore the
combined donor overhead is at least `2r`. With the old expanded stable
sequence fixed, a companion of power cost at most3 can save at most3.
Thus `r>=2` cannot give a strict endpoint gain for those old33 metrics.

The same argument covers nested helpers whose definition contains one
earlier stable atom, `h_j=y^(a_j) h_parent y^(b_j)`, over the fixed power
alphabet. These dependencies form a tree rooted at `x`. The difference
between the offsets of the two BS atoms is a sum along their tree path;
the common initial path cancels, and its power cost is bounded by the
sum of defining-edge costs. The overhead remains at least `2r` at any
nesting depth. Inverting a helper to orient its stable exponent positively
does not change this length bound.

This is not a rank bound for stable AC. Helpers encoding several stable
letters, conjugate-base helpers, power-metric changes, donor changes, or
longer intermediate presentations leave the stated family. It explains
why merely adding more retained spellings of a single stable step cannot
improve the already completed short-cost cases.

## Verification and attribution map

The earlier strict-compression formula and endpoint bound`L>=2r+1` remain
in [`THEOREM_NOTE.md`](../rank_unbounded_20260912/THEOREM_NOTE.md). The stronger
bound for a normalized tuple with no nonincreasing one-occurrence elimination,
`L>=3r+2`, was already derived by the main research and audited in
[`VERIFY_DEGREE_BOUND.md`](VERIFY_DEGREE_BOUND.md). It is not a new result of
this note. It uses the exact substitution upper bound
`Delta L <= (degree-2)*(donor_length-2)-2`; all such endpoint bounds permit
arbitrarily larger intermediate rank.

| Construction or claim | Independent verification | Exact scope |
| --- | --- | --- |
| Corridor substitutions and root collection | [VERIFY_CORRIDOR.md](VERIFY_CORRIDOR.md), [VERIFY_ROOT.md](VERIFY_ROOT.md) | Ordinary normal-product word identities with retained donors |
| Complete integer-flow optimization | [VERIFY_FLOW_EXACT.md](VERIFY_FLOW_EXACT.md) | Fixed root metric and fixed cyclic stable sequence; completion flags required |
| Primitive-root exposure and root metric change | [VERIFY_PREPARERS.md](VERIFY_PREPARERS.md) | Exact forward/inverse ambient maps and retained defining rows |
| Two-power metric and stable-letter shear exclusion | [VERIFY_MULTI_METRIC.md](VERIFY_MULTI_METRIC.md), [VERIFY_FIXED_DONOR.md](VERIFY_FIXED_DONOR.md) | Declared metric family and consecutive-BS shear identity |
| Short-companion fixed-donor geodesicity | [VERIFY_FIXED_DONOR.md](VERIFY_FIXED_DONOR.md) | The33 saved companion metrics satisfying every corollary hypothesis |
| Two-sided stable spellings and finite parameter balls | [VERIFY_STABLE_METRIC.md](VERIFY_STABLE_METRIC.md) | One additional retained stable atom, fixed old power metric |
| Full torus-donor block metric and explicit collection | [verification_torus.json](verification_torus.json) | Complete signed spelling metric for each processed two-generator block; bounded bridge wrapper |

The conjugate-base bridge and forced base-exchange controls are separately
reproducible in their `theory_*_checks.py/json` artifacts. Main-run census
records and later gains retain their own input provenance and charge totals.
No negative result above proves presentation minimality, stable-AC
nontriviality, or distinctness of the124 retained bounded-search components.

## Final rank-two projection diagnostics from the exact current witnesses

`theory_projection_panel.py/json` takes the18 new rank-three winners in the
2162-length CURRENT snapshot and resolves their exact witness-file pointers
and prefix lengths. It attempts every one-occurrence Lemma11 removal, allowing
temporary growth, then alternates whole-tuple Whitehead descent and
nonincreasing peeling before comparing endpoints. All61 projections finish
their normalization, using879 new charged units in total. None beats the
saved rank-two length or the current any-rank incumbent, and none solves.

Four best projection lengths are one above the saved rank-two lengths:
`aca_75`, `aca_83`, `aca_84`, and `aca_111`. The other14 match those lengths.
Twelve rows have explicit signed-permutation returns to the saved normalized
rank-two tuple. `aca_79` and `aca_80` match the saved lengths without that
particular return witness; equality of lengths is not an Aut-equivalence proof.

The separate`theory_projection_neutral_panel.py/json` first tests90 neutral
whole-Whitehead candidates per input, within its allowance of96. Only
`aca_43` has a distinct returned neutral neighbor; its three projections
also complete without gain. This second stage uses1658 new units in total.
Each stage has its own shared1000-unit allowance per row, and neither uses
a heap search. Direct and neutral search CPU times are respectively0.121615s
and0.013577s; imported witness discovery is historical.

Both reports use the diagnostic key`projection_rows`, retaining exact
projection endpoints separately from the best certified prefixes. They are
not automatically imported as frontier records by`refresh_results.py`.
This finite projection result does not cover arbitrary neutral Aut chains,
other primitive exposures, or unrestricted stable rank changes.

## Fixed-rank terminal rule for relators of length at most two

This responds to the final steering toward many short relators, without
reducing rank merely to reduce the number of generators. The following rule
is proved directly and uses ordinary AC moves, with no stable macro.

**Theorem.** Let a balanced presentation have `r` declared generators and
`r` freely reduced relators, each of length at most two. It presents the
trivial group if and only if its unsigned incidence graph is a forest with
exactly one singleton relator at each tree component. Here a two-letter
relator is an edge between its generator labels (a square gives a loop),
and a singleton marks its vertex. In that case there is an explicit ordinary
AC path, at the same rank throughout, to the positive standard generators
up to relator permutation. No relator ever exceeds length two on this path.

**Proof.** For any component without a singleton, send all its generators
to the nonidentity element of `C2`, and send all other generators to the
identity. Every two-letter row maps to the identity, as do empty rows and
singletons in the other components. This is a nontrivial quotient. Thus a
trivial presentation must have at least one singleton in every component.
A component with `v` vertices needs at least `v-1` edges to be connected and
at least one singleton; summing over components uses at least `r` rows.
Balance forces equality everywhere: exactly `v-1` edges and one singleton,
with no empty rows, loops or cycles. Conversely, invert each root singleton
if necessary to obtain its positive generator. Traverse its tree outwards.
For an edge leading from an already solved parent `p` to a child `x`, invert
and cyclically rotate its relator to `x p^epsilon`. Right-multiply it by the
singleton `p^-epsilon`; when needed invert the donor temporarily and restore
it immediately afterwards. The edge becomes `x`. Continue to obtain every
positive generator, each in a distinct row. These are relator inversions,
conjugations and multiplications only. Up to five such moves per tree edge,
plus at most one inversion per root, suffice. Relator permutation, if an
ordered terminal tuple is required, is an ordinary Nielsen operation. QED.

In particular, a nonempty presentation with **every** relator of length
exactly two always has a nontrivial `C2` quotient, regardless of rank or
balance. Length at most two is different: units are exactly what permits
triviality. The theorem itself is a constructive terminal classifier, so it
does not need a prior assumption that the input is known trivial.

`theory_short_relators.py` implements this classifier, returns an explicit
nontrivial `C2` assignment in the negative case, and otherwise emits the
ordinary AC move stream while retaining every generator and relator. Its
separate replay checks each move and the length-two bound. The frozen JSON
has 32 signed three-vertex trees, one sparse-label positive control, and
four quotient-negative controls; all pass. The generator list can be
supplied explicitly so unused declared generators are not silently omitted.
No presentation search or census evaluation was used.

### Structural progress after triangulation

A cheap useful score for a length-at-most-three presentation is the size of
its **residual triangular system after exhausting units and bigons**, with
rank retained. Record `(number of residual triangles, number of active
non-singleton generators, their incidence-degree histogram)` together with
the number of explicit singleton rows produced. Here is a certificate-safe
closure, rather than a claim that triangular form alone solves anything.

1. A singleton generator can be removed from every other row by ordinary
   AC substitutions using its singleton donor, while retaining that donor
   and generator. This cannot increase any row length.
2. A bigon on distinct generators, oriented `x y^epsilon`, permits replacing
   every occurrence of `x` in other rows by `y^-epsilon`, using normal
   products of the retained bigon. Each letter is replaced by one letter,
   so free reduction cannot increase a row. The other rows then avoid `x`.
   Apply the explicit ambient Nielsen map `x -> x y^-epsilon` (all other
   generators fixed); the bigon becomes singleton `x`, and all other rows
   stay unchanged. This last step is an ambient basis transformation, not
   mislabeled as an ordinary relator AC move. Its inverse is explicit.
3. Iterate these operations until no new unit or distinct-generator bigon
   appears. Squared-generator bigons must be retained unless another
   justified relation handles them; they are not equality pivots.

This process exploits cancellations between actual relations, keeps rank,
and never expands a relator. It does not simply expand the helper triangle
back to its defining word. Its closure may expose new units or bigons and
turn a triangular presentation into the proved length-two terminal case.
An original triangular helper relation by itself gives no such progress.
One additional sufficient pattern is a generator with exactly one occurrence
in the whole tuple: after orienting its triangle as `x u v`, the ambient
map `x -> x (u v)^-1` makes that row a singleton and changes no other row.
Again this is a recorded whole-basis map, not an asserted ordinary AC move.
Degree two alone is not a collapse certificate; two triangles sharing a
letter may instead create a longer relation, so it should remain a measured
pattern with exact cancellation checks.

The earlier projection direction is now stopped. Its final finite orbit
check did prove that the selected `aca_79` and `aca_80` rank-two projections
lie outside the respective saved minimal Aut orbits: both minimum checks
completed, and each neutral orbit closed at one representative modulo all
eight signed permutations. This used 72 additional units in total and makes
no claim about different AC orbits. These diagnostics are retained as
historical results, not as the current high-rank short-relator objective.
