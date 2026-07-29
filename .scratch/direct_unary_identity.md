# Direct Fox--Magnus reduction of the unary delta problem

Date: 2026-07-29

## Status

The literal all-index identities

\[
 I_{ij}=1_{\{i-j\in\{-1,0\}\}},\qquad
 J_{ij}=1_{\{i-j\in\{0,1\}\}},\qquad u_{00}=1
\tag{0.1}
\]

are **not proved or refuted here**.  The existing exact finite evaluation
does establish the required seed value \(u_{00}=1\), but it does not prove
either all-index edge identity.

There is, however, a substantial exact reformulation.  The last unary
coordinate can be computed directly from the literal raw word, without the
crossed-coordinate tensor recurrence or a final orientation comparison
between emitted labels.  It is the matching-independent parity of
heterochromatic crossings in a same-label chord diagram of raw Schreier
events.  This statement retains every quotient-section defect, every
one-vertex transport defect, every `c_vertex`
normalization, and every raw inverse sign because the events are extracted
from the final literal word itself.

Consequently (0.1) is reduced to three chronology-plus-equality
chord-crossing identities in Section 4.  The smallest remaining algebraic
obstruction is
constructing the *actual chronologically ordered* event stream, then its
identical-label pairing, and telescoping its crossing parity.  The
chronology inside every canonical correction leaf still depends on the
certificate's shortlex sort of that leaf's support.  Thus the chord formula
does not eliminate the shortlex normalizer; it only eliminates the final
wedge-orientation comparison and the separate tensor bookkeeping.

No index grid, census, search, or new numerical replay was used.

## 1. Literal Schreier events

Let

\[
 F=F(c,t),\qquad Q=\langle c,t\mid c^2=1\rangle,
 \qquad K=\ker(F\to Q).
\]

Put \(X=Q/\langle c\rangle\), represented by the code's canonical
post-`c_vertex` quotient words.  Reidemeister--Schreier gives the free basis

\[
 r_x=\widehat x\,c^2\widehat x^{-1}\qquad(x\in X)
\tag{1.1}
\]

of \(K\).  Scan a raw word \(W\in K\) from left to right with its current
quotient prefix.  Use exactly the `_KernelStream` rules:

* a positive raw \(c\) emits when the old quotient prefix ends in \(c\);
* a negative raw \(c^{-1}\) emits when the old quotient prefix does not end
  in \(c\); and
* in either case the event label is the canonical module vertex returned
  after the consumed raw letter, equivalently the `c_vertex` label used by
  `_append_kernel_letter`.

This produces a chronological signed stream

\[
 \mathsf E(W)=((x_1,\varepsilon_1),\ldots,(x_m,\varepsilon_m)),
 \qquad \varepsilon_a\in\{\pm1\}.
\tag{1.2}
\]

It is the literal Schreier word before optional adjacent free cancellation.
In particular, a transported generator is scanned as its actual raw word

\[
 \widehat q\,\widehat x\,c c\,
 \widehat x^{-1}\widehat q^{-1};
\]

one must not replace this prematurely by a single canonical generator.
Thus all transport and section defects are already present in (1.2).

## 2. Stable-sort formula for the full-wedge bit

Give \(X\) the certificate's shortlex order.  For a stream (1.2), set

\[
 \operatorname{sort}(W)=
 \sum_{1\le a<b\le m} [x_a<x_b]\pmod2.
\tag{2.1}
\]

### Theorem 2.1

If \(W\in[K,K]\), then the certificate's full-wedge readout of the
degree-two Fox--Magnus coordinate of \(W\) is exactly

\[
 \boxed{\phi_\infty(W)=\operatorname{sort}(W).}
\tag{2.2}
\]

Moreover, (2.1) is unchanged by deleting adjacent inverse Schreier letters,
and it is also the parity of the opposite inversion count

\[
 \sum_{a<b}[x_a>x_b].
\tag{2.3}
\]

#### Proof

Appending \(r_x^{\varepsilon}\) to a kernel word whose current linear
coordinate is \(a\) adds \(a\otimes(\varepsilon e_x)\) to its degree-two
coordinate; if \(\varepsilon=-1\), it additionally adds
\(e_x\otimes e_x\).  Induction over (1.2) therefore gives, for distinct
\(x,y\),

\[
 A_{xy}=
 \sum_{a<b\atop x_a=x,\ x_b=y}\varepsilon_a\varepsilon_b.
\tag{2.4}
\]

The extra inverse terms are diagonal and never enter the exterior readout.
Modulo two every \(\varepsilon_a\varepsilon_b\) is one.  Summing (2.4) over
the certificate orientation \(x<y\) proves (2.2).

Because \(W\in[K,K]\), the signed exponent sum of every \(r_x\) is zero.
Hence the unsigned number \(m_x\) of occurrences of \(x\) is even.  For
each distinct pair \(x<y\), the sum of the two possible chronological
counts is \(m_xm_y=0\pmod2\).  Thus (2.1) equals (2.3).

Deleting adjacent \(r_xr_x^{-1}\) removes two adjacent occurrences of the
same label.  Their combined contribution with every other occurrence is
twice one bit, and the pair between them is diagonal.  Hence (2.1) is
unchanged.  This also proves compatibility with free reduction.  \(\square\)

An immediate corollary is that \(\phi_\infty:[K,K]\to\mathbb F_2\) is a
homomorphism.  If \(W,V\in[K,K]\), the cross contribution between their
streams is zero because every label occurs evenly in each stream, so

\[
 \phi_\infty(WV)=\phi_\infty(W)+\phi_\infty(V),
 \qquad \phi_\infty(W^{-1})=\phi_\infty(W).
\tag{2.5}
\]

## 3. Matching-independent heterochromatic chord formula

Forget the event signs but retain their chronological positions and exact
canonical labels.  Every label has even multiplicity by Theorem 2.1.  Let
\(\mathcal M\) be **any** perfect matching which pairs positions carrying
the same label.  For two chords, say that they cross when their endpoints
alternate.  Define

\[
 \operatorname{cr}_{\ne}(W;\mathcal M)
\tag{3.1}
\]

to be the parity of crossings only between chords with distinct labels.
The subscript is load-bearing: monochromatic chord crossings are omitted.

### Theorem 3.1

For every \(W\in[K,K]\) and every same-label perfect matching
\(\mathcal M\),

\[
 \boxed{
 \phi_\infty(W)=\operatorname{cr}_{\ne}(W;\mathcal M).
 }
\tag{3.2}
\]

In particular, the right side is independent of the chosen same-label
matching.

#### Proof

Fix distinct labels \(x,y\).  For an \(x\)-chord, the number modulo two of
crossing \(y\)-chords is the number of \(y\)-endpoints strictly inside that
chord: a \(y\)-chord contributes one exactly when it has one endpoint
inside and one outside.  This does not depend on the \(y\)-matching.

Now fix a \(y\)-endpoint at chronological cut \(p\).  For any matching of
the \(x\)-endpoints, the parity of \(x\)-chords straddling \(p\) is the
number of \(x\)-endpoints before \(p\).  Indeed, if \(L\) is that number,
then

\[
 L=2(\text{number of \(x\)-chords wholly left of \(p\)})
   +(\text{number of \(x\)-chords crossing the cut}),
\tag{3.3}
\]

so the two quantities agree modulo two.  Summing (3.3) over all
\(y\)-endpoints gives the chronological \(x\)-before-\(y\) count, independent
of the \(x\)-matching.  Summing over unordered distinct label pairs proves
(3.2) from (2.1).  \(\square\)

The omission of monochromatic crossings cannot be dropped.  The signed
stream

\[
 r_x^2r_x^{-2}
\tag{3.4}
\]

represents the identity and has four events labelled \(x\).  Pairing
\((1,2),(3,4)\) gives no crossing, whereas pairing
\((1,3),(2,4)\) gives one crossing.  Both have
\(\operatorname{cr}_{\ne}=0=\phi_\infty\), because that crossing is between
two chords of the same label.  Thus arbitrary *total* crossing parity is
not matching-independent.

For the consecutive same-label matching \(\mathcal M_{\rm con}\), chords of
one label never cross.  Hence the earlier total-crossing formula remains the
special case

\[
 \operatorname{cr}_{\rm con}(W)
 :=\operatorname{cr}(W;\mathcal M_{\rm con})
 =\operatorname{cr}_{\ne}(W;\mathcal M_{\rm con})
 =\phi_\infty(W).
\tag{3.5}
\]

Once the *actual stream* has been constructed, (3.2) uses only its
chronology and equality of its post-`c_vertex` labels.  This must not be
confused with freedom to reorder the stream.  The canonical correction
section `lift_module_vector` shortlex-sorts the merged support of every
correction leaf, so shortlex determines generator chronology before
transport.  Swapping two distinct adjacent generators changes (2.1), hence
\(\phi_\infty\), by exactly one.  No invariance under changing that
within-leaf order is asserted.

## 4. Exact reformulation of the three requested identities

Let \(\mathcal R(F)\) denote the literal corrected residual word evaluated
with the fixed base correction \(B\) plus an integral homogeneous direction
\(F\).  This is the word represented by `_residual_ast`, not a mixed
occurrence approximation.  Its quotient and relation-module coordinates
are zero integrally, as follows.  Corrections lie in \(K\), so they do not
change the already-trivial quotient of the residual.  The
Reidemeister--Schreier relation module is the integral abelianization
\(K_{\rm ab}\), with basis \(([r_x])_{x\in X}\).  If \(d\) is the
uncorrected residual class and \(\operatorname{im}\) is the integral
correction-image map, the fixed lift certificate proves
\(d+\operatorname{im}(B)=0\).  By definition an integral homogeneous
direction satisfies \(\operatorname{im}(F)=0\).  Hence

\[
 [\mathcal R(F)]_{K_{\rm ab}}
 =d+\operatorname{im}(B)+\operatorname{im}(F)=0,
 \qquad \mathcal R(F)\in[K,K].
\tag{4.1}
\]

For the approved ray put \(D_{ij}=H(y_{ij})\), preserving the exact integral
anchor, raw right-deck paths, and signs.  Define three literal difference
words

\[
\begin{aligned}
 Z^0&=\mathcal R(D_{00})\mathcal R(0)^{-1},\\
 Z^i_{ij}&=\mathcal R(D_{i+1,j})\mathcal R(D_{ij})^{-1},\\
 Z^j_{ij}&=\mathcal R(D_{i,j+1})\mathcal R(D_{ij})^{-1}.
\end{aligned}
\tag{4.2}
\]

All three words lie in \([K,K]\).  By (2.5), base subtraction and the
quadratic edge formulas collapse as follows.  Let
\(\mathcal M^0,\mathcal M^i_{ij},\mathcal M^j_{ij}\) be arbitrary
same-label perfect matchings of the three actual event streams.  Then

\[
\boxed{
\begin{aligned}
 u_{00}
 &=\operatorname{cr}_{\rm con}(Z^0)
 =\operatorname{cr}_{\ne}(Z^0;\mathcal M^0),\\
 I_{ij}
 &=\operatorname{cr}_{\rm con}(Z^i_{ij})
 =\operatorname{cr}_{\ne}(Z^i_{ij};\mathcal M^i_{ij}),\\
 J_{ij}
 &=\operatorname{cr}_{\rm con}(Z^j_{ij})
 =\operatorname{cr}_{\ne}(Z^j_{ij};\mathcal M^j_{ij}).
\end{aligned}
}
\tag{4.3}
\]

Therefore the desired theorem is *equivalent* to

\[
\boxed{
\begin{aligned}
 \operatorname{cr}_{\ne}(Z^0;\mathcal M^0)&=1,\\
 \operatorname{cr}_{\ne}(Z^i_{ij};\mathcal M^i_{ij})
   &=[i-j=-1]+[i-j=0],\\
 \operatorname{cr}_{\ne}(Z^j_{ij};\mathcal M^j_{ij})
   &=[i-j=0]+[i-j=1],
\end{aligned}}
\tag{4.4}
\]

for any such same-label matchings.  Equivalently, one may replace every
\(\operatorname{cr}_{\ne}\) in (4.4) by
\(\operatorname{cr}_{\rm con}\); no arbitrary total-crossing readout is
intended.

This is not a redefinition of the evaluator.  The proof of Theorem 2.1
starts from the same `_KernelStream` recurrence as the exact certificate,
and (4.2) uses the whole literal residual at both endpoints.  Thus:

* `c_vertex` is applied at the actual event time;
* the ordinary quotient-prefix evaluation remains anti-homomorphic where
  the raw right-deck construction requires it;
* fixed base--direction interactions are present inside each endpoint
  stream before the two values are combined;
* quotient-section and transport defects are present as their extra raw
  events; and
* inverse diagonals are retained in the Magnus proof and disappear only
  because the final readout is exterior.

The existing exact finite evaluator gives
\(U(D_{00})=\texttt{010111100110111}\), so its last coordinate verifies the
finite base case \(\operatorname{cr}_{\rm con}(Z^0)=1\).  No finite cell evaluation is
used for either all-index line of (4.4).

As a separate finite sanity check of the direct reformulation, the literal
word for the exact
\(y_{00}=\texttt{cTcTctttcTcTctttcTcTctttcTct}\) gives a difference word
\(Z^0\) of raw length 5234 with 424 Schreier events and 93 distinct labels.
Every label multiplicity is even, and the direct stable-sort parity is one,
agreeing with the normalized symbolic last bit.  These finite counts verify
the seed transcription only; they are not evidence for either all-index
edge identity.

## 5. Concrete next certificate specification

The all-index crossing identities (4.4) remain open.  The next artifact must
work at the resolution of the two complete unary endpoint residuals.  A
twelve-occurrence directional or mixed-Hessian trace is insufficient: the
literal unary AST has sixteen correction occurrences, with slot counts
\((6,4,2,2,2)\), and each occurrence uses the canonical section of the
*merged* current \(B_s+F_s\).

### 5.1 Exact endpoint event index set

For one of the three difference words, write its endpoint directions as
\(F^-\) and \(F^+\).  Thus they are respectively
\((0,D_{00})\), \((D_{ij},D_{i+1,j})\), or
\((D_{ij},D_{i,j+1})\).  Expand the full `_residual_ast` without performing
optional adjacent free cancellations; Theorem 2.1 proves those cancellations
do not affect the answer.

Let \(\mathcal O\) be the ordered set of all sixteen correction
occurrences.  For endpoint \(\epsilon\in\{-,+\}\), occurrence
\(o\in\mathcal O\), and its slot \(s(o)\), form first

\[
 C^\epsilon_o=B_{s(o)}+F^\epsilon_{s(o)}
\tag{5.1}
\]

integrally.  The atom list of that leaf is obtained by sorting
\(\operatorname{supp}(C^\epsilon_o)\) by the exact certificate key, then
listing \(|(C^\epsilon_o)_x|\) copies of \(r_x\) with the coefficient sign.
For a negative correction occurrence the complete atom list is reversed
and inverted.  Base and direction atoms may not be concatenated as separate
sections.  Slot-one occurrences remain in \(\mathcal O\); an empty merged
section must be proved empty rather than deleted by appeal to the anchored
mixed normal form.

The event index set \(\mathcal E^\epsilon\) must then contain:

1. \((\epsilon,o,x,k,r)\) for every correction occurrence, merged-support
   atom, coefficient copy, and raw position \(r\) which emits under the
   literal `_KernelStream` rule at that AST quotient prefix; and
2. \((\epsilon,\ell,r)\) for every emitting raw position in every fixed
   literal leaf \(\ell\).

The first class includes all section, transport, inverse, fixed-base, and
direction events; the second includes every literal-source and fixed
quotient-section event.  Each record must print its raw sign, chronological
key, quotient prefix before and after the raw letter, and final
post-`c_vertex` label.  The stream for
\(\mathcal R(F^+)\mathcal R(F^-)^{-1}\) is the forward
\(\mathcal E^+\) stream followed by the reversed, sign-inverted
\(\mathcal E^-\) stream.

Chronology is therefore fixed in this order: AST leaf order, polarity,
the exact shortlex merge in (5.1), coefficient-copy order, and raw-letter
order.  A certificate must give disjoint domains covering every event and
must prove its chronology formulas, rather than recover order from a final
wedge comparison.

### 5.2 Label-preserving provenance matching

For each of the three difference streams, the certificate must supply an
explicit fixed-point-free involution

\[
 \iota_{ij}:\mathcal E_{ij}\longrightarrow\mathcal E_{ij},
 \qquad \iota_{ij}^2=1,
 \qquad \iota_{ij}(e)\ne e,
 \qquad \ell(\iota_{ij}(e))=\ell(e),
\tag{5.2}
\]

where \(\ell(e)\) is the exact final post-`c_vertex` label.  Every event
must occur in exactly one pair.  Global vanishing of the relation-module
coordinate proves only that such a matching exists abstractly; it does not
prove any proposed provenance formula in (5.2).  The label equality of each
matching branch and complete coverage/overlap emptiness are separate proof
obligations.

The readout is

\[
 \operatorname{cr}_{\ne}(\mathcal E_{ij};\iota_{ij}),
\tag{5.3}
\]

so the involution need not find consecutive mates.  Monochromatic crossings
are discarded exactly as required by Theorem 3.1.

### 5.3 Proved two-stream provenance observation

There is one general cancellation rule available before any ray-specific
calculation.  Suppose a provenance event \(p\) occurs at both endpoints
with the same final label and is matched between the forward \(+\) stream
and the reversed \(-\) stream.  Do the same for \(q\).  If the two chord
labels are distinct, their chords cross exactly when the relative order of
\(p,q\) reverses between the two original endpoint streams.

Indeed, if \(p<q\) in the \(+\) stream, the two chords cross precisely when
the inverse block lists the \(-\) copy of \(p\) before the \(-\) copy of
\(q\).  Since that block reverses the original \(-\) chronology, this is
equivalent to \(q<p\) at the \(-\) endpoint.  Therefore fixed AST block
order and unchanged common canonical atom/provenance keys give no
common--common crossing.  Under a matching which pairs all such common
provenance across endpoints, only events inserted, removed, relabelled, or
reordered by the merged section boundary can contribute the remaining cuts.
This observation is
conditional on the certificate proving common provenance and unchanged
final labels; it supplies neither fact by itself.

### 5.4 Precise leaf step and non-circular local formula

A source-tree induction is admissible only after specifying a leaf operation
\(L:F\mapsto F'\) integrally.  For every one of the sixteen occurrences it
must recompute (5.1), its support, coefficient signs and multiplicities,
and the resulting canonical merge.  It must identify a survivor provenance
bijection which preserves final labels,
\(\ell_{\rm old}(e)=\ell_{\rm new}(e)\), prove that the new involution is
the restriction of the old one on those survivors, and express the changed
event set as complete matched chords.  Every relabelled chord is treated as
an old deleted chord plus a new inserted chord, not as a survivor.  Any
change in survivor chronology caused by the new shortlex merge must be
printed as an explicit permutation \(\pi_L\).

There is an exact non-circular formula for the crossing change once those
data exist.  Delete the changed chords one at a time in a prescribed order.
For a chord \(C=(a,b)\), with \(a<b\), in the current stream put

\[
 \lambda_{\rm del}(C)
 =\sum_{a<e<b}[\ell(e)\ne\ell(C)]\pmod2.
\tag{5.4}
\]

This is the parity of heterochromatic chords crossing \(C\): each other
chord contributes the number of its endpoints in \((a,b)\), namely zero or
two if it does not cross and one if it crosses.

The stages are fixed.  Start with the old stream and delete old-only changed
chords one at a time, evaluating \(\lambda_{\rm del}(C)\) in the current
stream immediately before each deletion.  Next apply \(\pi_L\) to the
label-preserving survivors.  Finally insert new-only chords one at a time,
evaluating \(\lambda_{\rm ins}(C)\) by (5.4) in the current stream
immediately after that insertion.  Thus deleted--deleted and
inserted--inserted crossings are each counted exactly once.  Reordering the
survivors contributes the heterochromatic inversion parity

\[
 \lambda_{\rm ord}(\pi_L)
 =\sum_{e<_{\rm old}f}
   [f<_{\rm new}e]\,[\ell(e)\ne\ell(f)]\pmod2.
\tag{5.5}
\]

To justify (5.5), fix two survivor chords with distinct labels.  Their
crossing indicator is the parity of the four chronological comparisons
between an endpoint of the first chord and an endpoint of the second.
Consequently its old/new crossing change is precisely the parity of those
cross-label endpoint pairs whose relative order reverses.  Summing over all
heterochromatic survivor-chord pairs gives (5.5); same-label endpoint pairs
are correctly omitted.

Thus a valid leaf certificate must define, before using the desired answer,

\[
 \boxed{
 \lambda(L)
 =\sum_{C\ \mathrm{deleted/inserted}}\lambda_{\rm del/ins}(C)
  +\lambda_{\rm ord}(\pi_L).
 }
\tag{5.6}
\]

The prescribed sequential streams in (5.4) prevent double counting.
Equations (5.4)--(5.6) depend only on explicit event labels and chronology,
not on the target indicator or on a previously computed global crossing
parity.  The remaining all-index work is to substitute the exact
\(P_\nu^iC_\nu Q_\nu^{i-j}\) source schemas into (5.4)--(5.6), prove the
leaf recurrence, and derive independently the boundary values
\(\{-1,0\}\) for the \(i\)-edge and \(\{0,1\}\) for the \(j\)-edge.
No such sixteen-occurrence involution or leaf calculation is currently
proved.

## 6. Proof boundary

Proved exactly here:

1. the raw-event stable-sort formula (2.2) for the certificate's full-wedge
   coordinate;
2. the matching-independent heterochromatic chord formula (3.2), including
   the consecutive-matching special case and the monochromatic
   counterexample boundary;
3. integral membership of every homogeneous residual in \([K,K]\) and
   homomorphic cancellation of the fixed base between adjacent unary values;
4. the exact equivalence between the requested identities and the three
   chord equations (4.4); and
5. the relative-order-reversal criterion for two common cross-endpoint
   provenance chords.

Retained finite fact:

* the exact typed-AST seed evaluation gives \(u_{00}=1\).

Still open:

* both all-index edge identities in (0.1);
* the explicit sixteen-occurrence event manifest, label-preserving
  involution, and leaf calculation specified in Section 5; and
* therefore the all-index identity \(u_{ij}=\delta_{ij}\).
