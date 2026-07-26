# AK(3) full q-normal-closure traffic design

Date: 2026-07-25

## Objective

Close arbitrary target traffic from the restored literal q-source,
including multipliers containing \(z\), and separately decide the four
first literal-z targets

\[
Wz^{\delta}q^{\epsilon}z^{-\delta},
\qquad
\delta,\epsilon\in\{+1,-1\}.
\]

## Source-first closure

For arbitrary

\[
v\in
\langle\!\langle q\rangle\!\rangle_{F(x,t,z,q)},
\]

the q-source normal-closure lemma produces

\[
(\beta(R),Wv,D,q).
\]

Delete the restored literal q-slot first. Killing q sends

\[
\beta(R)\mapsto R,\qquad
Wv\mapsto U,\qquad
D\mapsto D.
\]

The recovery word \(U=Rz^{-1}xt\) is primitive. Delete it next, giving

\[
\left(R,\;t^{-1}(xtR)x(xtR)^{-1}\right),
\]

which returns to the standard rank-two AK endpoint by two
\(R^{\pm1}\)-source factors. This is independent of \(v\).

## Literal-z target obstruction

Use explicit Whitehead automorphisms followed by the cut-vertex lemma.
This is a finite word certificate, not AC graph search.

First apply

\[
\alpha(x)=q^{-1}xq
\]

with \(t,z,q\) fixed. It removes the partial-q transport from \(W\).

For the \(zq^{\epsilon}z^{-1}\) pair, a second automorphism

\[
\sigma(t)=x^{-1}tx,\qquad
\sigma(z)=zx,\qquad
\sigma(q)=x^{-1}q
\]

reduces both words to length 13. Their Whitehead graphs are identical
and contain a spanning cycle on all eight signed basis vertices.

For the \(z^{-1}q^{\epsilon}z\) pair, the first reduction gives
length-14 words whose identical Whitehead graph also contains a
spanning 8-cycle.

A spanning cycle makes each graph connected with no cut vertex.
Whitehead's cut-vertex lemma therefore proves all four words
nonprimitive.

## Boundary

The stable closure requires the final q-source slot to be restored
literally and the target to have the same q-kill as \(W\). It does not
cover a changed q-source, a multiplier with nontrivial q-kill, or a
different checkpoint. Nonprimitivity is asserted only for the four
exact literal-z targets; longer traffic can change target primitivity.
