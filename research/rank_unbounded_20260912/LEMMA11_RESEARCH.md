# Exact substitution and removal at arbitrary finite rank

This note and `lemma11.py` use **Lemma 11, Substitution and Removal**, in
Shehper et al., *What makes math problems hard for reinforcement learning?*,
Section 9.1, page 43 of [arXiv:2408.15332](https://arxiv.org/pdf/2408.15332).
The inspected local transcription begins at line 2499 of
`literature/txt/math_ml_paper_2408.15332.txt` in the parent checkout.
The required input is a **known balanced presentation of the trivial group**.
The implementation checks exact word identities; it does not decide that
hypothesis. In particular, determinant ±1 does not replace it.

The lemma permits a defining relator `g^-1 w`, with `w` avoiding `g`, to
substitute `g=w` in every other relator and then remove that defining row and
generator, up to stable AC equivalence. Its proof needs an unspecified finite
normal-product expression for `w` in the surviving relators. Accordingly the
records here are **theorem-backed stable composites**, with no assertion that
one charged removal is one elementary AC move. No normal-product expansion
or useful upper bound on that expansion is supplied.

## 1. A unique occurrence is an exact sufficient condition

Let one current cyclically reduced relator be `R=P g^e Q`, where `e=±1`, and
suppose neither `P` nor `Q` contains either sign of `g`. The following are
literal free-group identities:

| Occurrence | Word assigned to `g` | Defining normal form |
|---|---|---|
| `e=-1` | `w=QP` | `P^-1 R P = g^-1 w` |
| `e=+1` | `w=P^-1 Q^-1` | `Q R^-1 Q^-1 = g^-1 w` |

Thus **any** unique signed occurrence in **any** current row admits the exact
lemma. It need not be the newest helper or a one-letter relator. Counts are
unsigned occurrence counts, not exponent sums. If a row offers several such
generators, these are separate elimination candidates with potentially very
different substitution costs.

The module retains the original row, its position, the occurrence sign and
position, `w`, and an explicit pair `(sign, conjugator)` satisfying
`conjugator^-1 R^sign conjugator = g^-1 w`. It substitutes into every surviving
row, including all earlier defining rows. Both the unreduced expanded words
and their free reductions are stored. Final cyclic reduction, inversion,
rotation and row sorting have separate conjugation witnesses.

For completeness, the substitution portion itself has ordinary AC donor
identities. With `D=g^-1 w`, a target `A g B` becomes `A w B` after right
multiplication by `B^-1 D B`. A target `A g^-1 B` becomes `A w^-1 B` after
right multiplication by `B^-1 g D^-1 g^-1 B`. Temporary donor changes can
be restored. The further deletion of `D` is precisely where the lemma uses
the trivial-group hypothesis and the unexpanded normal-product identity.

Generator labels are nonzero signed Python integers. A removal retains the
identities of all surviving generators; gaps are deliberate, with
`generator_relabeling=identity_on_survivors` recorded. This agrees with
`search.normalize` and avoids an unrecorded coordinate change. Adding another
definition chooses a fresh integer above the existing maximum. Neither the
identifier size nor the number of surviving generators has a fixed cap.

## 2. Rank eliminations should be scored after all substitutions

Let the current full tuple have total length `L`. Let the defining row have
length `d`, the isolated word have length `m`, and let `N` be the number of
occurrences of either sign of `g` in **all other rows together**. The total
length immediately after literal substitution and deleting the defining row,
before free or cyclic cancellation, is exactly

\[
E=L-d+N(m-1).
\]

If `C` is the total number of letters removed by subsequent free and cyclic
reduction, the final length and gain are

\[
L'=L-d+N(m-1)-C,\qquad L-L'=d-N(m-1)+C.
\]

Here `C` is nonnegative and even. For a cyclically reduced defining row
with a unique occurrence, `d=m+1`. The important special cases are:

- `m=0`: a singleton donor removes one letter plus every occurrence of its
  generator elsewhere, followed by any further cancellations.
- `m=1`: a length-two donor always shortens total length by at least two.
- `m>=2`: removal can increase total length. Literal occurrence counts alone
  cannot predict the result when substitution causes cancellations.

The computable score is therefore the exact `L'`, with all current rows
included. `generate_removals` evaluates candidates within the available work
and sorts their complete normalized endpoints by this score. Longer endpoints
are returned as legitimate transitions too; the caller decides its search
policy. A bounded scan ranks only the candidates actually evaluated and does
not claim that the best omitted removal is worse.

In particular, introducing a helper and then eliminating a different old
generator is a change of marking, not necessarily undoing the definition.
An old helper may gain length during that substitution. Omitting that row
would turn a real cost into a fictitious improvement.

## 3. Optional exposure by a whole-tuple automorphism

`generate_removals(..., expose_primitives=True)` also considers relators with
no currently unique occurrence. For each selected target row it performs
strict Whitehead descent using the minimum-cut routines in `whitehead.py`.
Each selected automorphism is applied to **every** current relator, and its
forward and inverse images are verified. The target row's identity is tracked
through row sorting. The process stops as soon as any generator in that row
has a unique occurrence, which can happen before the row reaches length one.
It then attempts the corresponding exact removals.

This objective can temporarily increase the full tuple's length. The final
substituted tuple is still scored using every row. The implementation does
not infer that other relators are a free basis or a free complement from the
target's primitivity. It needs only the explicit defining normal form and the
known triviality of the whole input. Ambient maps have the stable realization
explained in
[`STABLE_CERTIFICATE_CONVENTIONS.md`](../theory_patterns_20260912/STABLE_CERTIFICATE_CONVENTIONS.md).

The optional scan is deliberately bounded. Failure may mean that its budget
ended, that this descent did not expose a defining row, or that it reached a
minimum for the selected target. The API makes no global nonprimitivity,
nonshortenability, or stable AC obstruction claim from an empty candidate list.
Different minimum cuts with the same target gain can affect the remaining
relators differently; this routine does not enumerate all tied cuts.

## 4. A verified rank-changing example

Write `Z=z^-1`. Start with

\[
P=\langle x,y\mid xyxyx,\;xyxyxyx\rangle.
\]

Both relators have at least two occurrences of each generator. Thus no direct
single-occurrence removal is available. This is independently a trivial-group
presentation: writing `v=xy`, the relators are `v^2 x` and `v^3 x`; their
product `(v^3 x)(v^2 x)^-1` freely reduces to `v`, and then they force `x`
and `y` to be trivial.

Introduce `z=xy` and substitute its five displayed occurrences. This gives

\[
\langle x,y,z\mid Zxy,\;zzx,\;zzzx\rangle.
\]

The full length falls from 12 to 10. The old relator `zzx` now contains exactly
one `x`. Isolate `x=ZZ` and substitute into **both** other rows:

\[
Zxy\longmapsto ZZZy,\qquad zzzx\longmapsto zzzZZ=z.
\]

Removing the defining `zzx` row leaves the rank-two tuple `(ZZZy,z)`, of total
length 5. The older helper row `Zxy` grew from length 3 to length 4 and was
fully charged in that endpoint. The rank history is `2 -> 3 -> 2`; the length
history is `12 -> 10 -> 5`. Further singleton removals give `(y)` and then
the empty rank-zero presentation.

This demonstrates a genuine newly available old-generator removal after a
rank increase. It does **not** claim that stabilization was necessary or that
no direct automorphism route exists: the optional per-relator descent also
reduces this original example. The five direct elimination candidates from
the compressed rank-three tuple have verified endpoint lengths
`5, 6, 7, 9, 12`, so even this tiny example shows why post-substitution scoring
matters.

## 5. A sufficient joint-donor extension

A further computable route is to select several donor rows and apply a common
ambient automorphism to the full presentation. If the selected rows become
one-letter relators on **distinct** generators, delete those generators by
successive exact substitutions. A certificate consists of the full common
map and its inverse, each row's conjugation/inversion to its singleton, and
the complete sequential removal records. All other rows, including old
helpers, remain in every score.

This is a sufficient certificate for the selected donor subset to be usable
as a partial free basis, up to its recorded relator conjugations. Individual
primitivity of each donor is not a certificate for the subset jointly. For
example, two copies of `x` are individually primitive and do not form a
two-element free basis. An implementation must require distinct exposed
axes under the **same** verified map.

A candidate mechanism would build the Whitehead graph of a selected donor
subset, seek strict descent of the sum of those donor lengths, apply each
selected map to the full tuple, and test the exposed distinct axes. Charge
every subset minimum cut and every subsequent removal. An unsuccessful
bounded subset descent proves no obstruction. This extension is a research
suggestion; it is not implemented or included in the current measurements.

More generally, triangular defining rows can be eliminated in sequence when
their dependencies permit it. Mutual equations cannot simply be deleted in
parallel: after each elimination, replay all substitutions and recheck the
next row's actual unique-occurrence condition.

## 6. API and validation scope

`generate_removals(words, remaining, *, expose_primitives=False)` returns
`(candidates, charged)`, where each candidate is `(after_tuple, event_list)`.
Direct removals come before optional exposure in the work schedule. One
attempted removal costs one unit; every per-relator minimum cut costs one.
Duplicate outcomes and unsuccessful cuts still consume work. A selected
whole-tuple map is included in its cut work, and syntactic normalization and
candidate enumeration do not receive separate units. Consequently these are
heterogeneous accounting units, not a uniform CPU-cost model.

At least one unit is reserved for removal during an optional descent. The
function never returns `charged > remaining`. If all direct candidates fit,
they are all evaluated before optional cuts. There is no rank limit, word
length limit, or acceptance ceiling inside the function; its finite budget
does not make it an exhaustive search over arbitrary stable ranks.

`replay_removal` checks the normal form, every surviving row's exact expansion,
its free reduction, final conjugation witnesses and row order, deleted-axis
absence, and final total length. It also works after JSON serialization.
The full elementary normal-product expansion remains absent by design and
is explicitly labelled absent in each removal event.

The command `python -B research/rank_unbounded_20260912/lemma11_checks.py`
passes 11 focused tests using this checkout's parent `.venv/bin/python`.
They verify both occurrence signs; cyclic conjugation witnesses; all-row
substitution; JSON replay; singleton and rank-zero endpoints; rank 11 with
large, noncontiguous generator IDs; malformed inputs; work limits;
unsuccessful cut and duplicate-attempt charging; the rank-changing example;
and whole-tuple automorphism/inverse replay during exposure. The recorded
test run completed in 0.003 seconds. No census or large presentation search
was run for this module.
