# Intact-boundary pumping for the old--new cut

Date: 2026-07-29

## 0. Status

This note proves the specialized word-theoretic lemma needed to turn the
threshold-three seed cells in the interrupted old--new checker into genuine
all-power cells.  It does not assert that every concrete schema satisfies the
hypotheses, nor does it prove the six numerical family parities.  Those are
separate finite application obligations.

## 1. Setup

Let (F) be a free product in which canonical words are represented by freely
reduced words, with the order-two letter (c=c^{-1}) normalized after each
letter.  Let

\[
 W(x)=b_0 r_1^{e_1(x)}b_1\cdots r_m^{e_m(x)}b_m
 \tag{1.1}
\]

be a fixed powered schema on an orthant

\[
 {cal O}=x_0+\mathbb N^k.
 \tag{1.2}
\]

Each (r_j) is a nonempty reduced cyclic word, each (b_j) is fixed, and

\[
 e_j(x)=e_j(x_0)+\delta_j(x),\qquad
 \delta_j(x)=\sum_s\lambda_{js}(x_s-x_{0,s}),qquad
 \lambda_{js}\ge0.
 \tag{1.3}
\]

Write (operatorname{cv}(w)) for the canonical reduction of (w), followed
by deletion of one terminal (c), if present.

Expand (1.1) at (x_0), reduce the whole product, and retain a provenance tag
on every surviving letter.  An **intact boundary** for the changing factor
(r_j) is a surviving adjacent pair

\[
 \cdots r_j\mid r_j\cdots
 \tag{1.4}
\]

whose last and first letters retain the tags of consecutive copies of that
same occurrence of (r_j^{e_j(x_0)}).  Require one such boundary for every
(j) with (delta_j\ne0), and require the selected boundary positions to be
distinct in the reduced base word.

## 2. Intact-boundary pumping lemma

**Lemma 2.1.** Under the hypotheses above, let (V_0=operatorname{cv}(W(x_0))).
For (x\in{cal O}), form (V(x)) from (V_0) by inserting exactly
(delta_j(x)) further copies of (r_j) at the selected (j)-boundary, for
every changing factor.  Then

\[
 \boxed{\operatorname{cv}(W(x))=V(x).}
 \tag{2.1}
\]

The insertions may be performed in any order.

### Proof

Because (1.4) survives the complete reduction at (x_0), the two-letter
junction from the end of (r_j) to its beginning is reduced.  This is also
the junction on both sides of a new copy inserted at (1.4).  The interior of
the new copy is reduced because (r_j) is reduced.  Thus one insertion creates
no cancellation and leaves two intact (r_j\mid r_j) boundaries in place of
one.

No letter outside the chosen boundary changes.  In particular, every chosen
boundary for another factor retains its two neighboring tagged letters.
Distinct insertions therefore commute.  Induction on
(sum_j\delta_j(x)) proves that the canonical reduction before terminal
deletion is obtained by the stated insertions.

All selected boundaries lie inside the word retained by
(operatorname{cv}).  An internal insertion changes neither the last letter
nor whether that letter is (c).  Consequently the terminal-(c) branch is
the same as at (x_0), and applying its fixed deletion gives (2.1).
\(square\)

## 3. Equality and shortlex corollaries

For one pumped template define its length by

\[
 L(x)=|V_0|+\sum_j |r_j|\delta_j(x).
 \tag{3.1}
\]

This is affine on the whole orthant.

**Corollary 3.1.** Let (V,V') satisfy Lemma 2.1 on the same orthant.

1. If (L-L') has a fixed strict sign on the orthant, that sign is the
   shortlex order of (V(x),V'(x)) for every (x).
2. If their normalized block lists agree, the words agree for every (x).
3. Suppose (L=L'), and at (x_0) the first mismatch lies in fixed blocks.
   If the two prefixes before it have identical normalized pumped block lists,
   then the prefix lengths are the same affine function and the same two fixed
   letters are the first mismatch for every (x).  Their letter order is the
   all-power shortlex order.

### Proof

Part 1 is the definition of shortlex.  Part 2 follows by expanding identical
blocks.  In part 3 the common pumped prefix expands identically by Lemma 2.1;
therefore both fixed mismatch letters move by the same affine offset and no
earlier mismatch can appear.  Their fixed order decides the comparison.
\(square\)

## 4. Concrete application obligations

For every schema/cell produced by
`.scratch/period_two_old_new_cut_covariance_checker.py`, a completed
certificate must materialize and verify:

1. every core is nonempty, reduced, and cyclically reduced;
2. every coefficient retained in a changing affine exponent is nonnegative;
3. every changing factor has a tagged intact boundary at the base point;
4. the selected boundaries are pairwise distinct;
5. the terminal-(c) branch at the base and its preservation under internal
   insertion;
6. every comparison is discharged by exactly one case of Corollary 3.1;
7. the (P)-selector cells are intersected with (h+r\ge a), and this domain
   is covered disjointly; and
8. every old row is bound to its approved raw-manifest domain and
   `current_equality`, not merely to the counts (100,113,92).

The current checker enforces items 3--4 with assertions and has the proof
shape for item 6, but it does not yet serialize all eight obligations.  Its
hard-coded zero failure counters are not substitutes for these records.

For the concrete schemas the only primitive cores are

\[
 R=\texttt{ctcTTTct},\qquad S=\texttt{cTctttcT}.
 \tag{4.1}
\]

Both are nonempty, reduced, cyclically reduced words of length eight, and all
displayed affine slopes are nonnegative.  Fixed and base schemas satisfy the
lemma vacuously.  The (b), singleton, (P), (C), and (Q) schemas are
conditional only on their base-three tagged boundary records: once those
records exist, distinct block tags prove boundary disjointness, the insertion
argument proves commutation and terminal-(c) stability, and the exact cells
(0,1,2) plus the pumped cell (ge3) cover every exponent.  No congruence
refinement is then needed.

The concrete certificate must also bind the omitted doubled slot-zero anchor
to its 21 approved provenance rows.  Its asserted evenness is presently only
a summary string.

## 5. Remaining arithmetic boundary

Once Sections 2--4 are instantiated, the all-power word comparisons are
valid.  One still has to materialize the modulo-two family values

\[
 (F,B,S,P,C,Q)=(0,0,1,0,[d=1],0).
 \tag{5.1}
\]

Only then does bilinearity give

\[
 \mathbb B(A_{n,d},b_{n,d})
 =1+[d=1]=[d>1],
 \tag{5.2}
\]

and hence diagonal covariance.  No claim about (Q(A_{n,0})), Andrews--Curtis,
or stable Andrews--Curtis is made here.
