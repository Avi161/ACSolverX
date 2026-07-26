# AK(3) post-primitive traffic design

Date: 2026-07-25

## Objective

Decide whether a relation-split primitive construction can escape by
performing arbitrary classical AC traffic on the surviving relator slots
after the primitive word has been manufactured but before it is deleted.

## Naturality principle

Fix a primitive slot \(W=\phi(q)\) in a balanced trivial-group
presentation and define

\[
\theta=\rho\phi^{-1},
\qquad
\rho(q)=1.
\]

Then \(\theta(W)=1\). Consider any AC1--AC3 history that never multiplies
another relator into the \(W\)-slot but may:

- multiply any other target by any other source;
- use \(W\) as a source;
- invert or conjugate the \(W\)-slot;
- invert or conjugate non-\(W\) slots;
- use arbitrary conjugators containing \(q\).

Applying \(\theta\) after every move gives:

- the same AC1, AC2, or AC3 move on quotient relators when the source is
  not \(W\);
- a no-op when the source is \(W\).

Therefore deletion after the history is classically AC-equivalent to
deletion at the original checkpoint.

## AK(3) replay

Use the source-slot checkpoint

\[
(\beta(R),W,D,q).
\]

Replay a mixed history in which:

1. the \(W\)-slot is conjugated and then inverted;
2. the \(q\)-slot is multiplied by a conjugate of \(D\);
3. the \(D\)-slot is multiplied by a conjugate of the current
   distinguished source;
4. the \(\beta(R)\)-slot is multiplied by a conjugate of the modified
   \(q\)-slot;
5. the \(q\)-slot is inverted;
6. the \(D\)-slot is conjugated by a word containing \(q\).

Map the final tuple through \(\theta\), delete the trivial \(W\)-slot,
and independently replay the descended quotient moves. The two tuples
must agree literally.

## Boundary

The theorem closes arbitrary post-manufacture AC1--AC3 traffic while the
primitive slot is not an AC1 multiplication target. It does not close a
history that changes \(W\)'s primitive conjugacy class by multiplying
another relator into it,
changes which primitive relator is deleted, or performs essential traffic
before the \(W\)-checkpoint.
