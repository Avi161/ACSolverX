# Conjugated consequence storage cancels under target deletion

Date: 2026-07-27

Status: **PROVEN**.

## 1. Universal cancellation theorem

Let a balanced relator tuple contain a relator \(A\), together with a
retained subtuple whose normal closure contains a word \(C\).  Stabilize
with a fresh generator \(q\) and relator \(q\).  The normal-closure
transvection lemma permits the retained sources to change this relator
to

\[
Q=qC
\tag{1}
\]

while restoring every source slot.

Fix an arbitrary word \(g\) in the old generators and replace the
\(A\)-slot by

\[
P=A(gQg^{-1})
=AgqCg^{-1}.
\tag{2}
\]

This is one AC multiplication by a conjugate of \(Q\).  The word \(P\)
contains exactly one \(q\).  Write

\[
P=LqM,
\qquad
L=Ag,
\qquad
M=Cg^{-1}.
\tag{3}
\]

The exact unique-letter solution preserves the side order:

\[
q=L^{-1}M^{-1}
=g^{-1}A^{-1}gC^{-1}.
\tag{4}
\]

Delete \(q\) and \(P\) by the substitution-and-removal lemma.  The
surviving stored-consequence relator becomes

\[
\begin{aligned}
Q[q\mapsto g^{-1}A^{-1}gC^{-1}]
&=g^{-1}A^{-1}gC^{-1}C\\
&=g^{-1}A^{-1}g.
\end{aligned}
\tag{5}
\]

Thus the endpoint differs from the original tuple only by replacing
\(A\) with a conjugate of \(A^{-1}\).  Relator inversion and conjugation
are classical Andrews--Curtis moves.  Therefore the entire stabilized
history is a self-loop.

The conclusion is independent of the length or spelling of \(C\), the
number of sources used to manufacture it, and the conjugator \(g\).
The necessary hypothesis is that those sources remain available until
\(Q=qC\) has been manufactured.  No assertion is made about histories
that alter the stored word after (1), multiply it into several targets,
or delete a different primitive word.

## 2. The braid-swapped AK(3) attempt

For AK(3), put

\[
A=x^3y^{-4},
\qquad
B=xyxy^{-1}x^{-1}y^{-1},
\qquad
\Delta=xyx,
\tag{6}
\]

and consider the swapped power word

\[
C=y^3x^{-4}.
\tag{7}
\]

The braid relator gives, modulo
\(\langle\!\langle B\rangle\!\rangle\),

\[
\Delta x\Delta^{-1}=y,
\qquad
\Delta y\Delta^{-1}=x.
\tag{8}
\]

Consequently

\[
\Delta A\Delta^{-1}
\equiv y^3x^{-4}=C
\pmod{\langle\!\langle B\rangle\!\rangle},
\tag{9}
\]

and hence

\[
C\in\langle\!\langle A,B\rangle\!\rangle.
\tag{10}
\]

It is therefore legitimate to stabilize with \(q\), use the retained
\(A,B\) slots to manufacture

\[
Q=qC,
\tag{11}
\]

and multiply the \(A\)-slot by \(yQy^{-1}\).  The resulting primitive
relator is

\[
\begin{aligned}
P
&=AyqCy^{-1}\\
&=x^3y^{-3}q\,y^3x^{-4}y^{-1}.
\end{aligned}
\tag{12}
\]

Here \(g=y\).  Equations (4)--(5) give

\[
q=y^{-1}A^{-1}yC^{-1}
\tag{13}
\]

and

\[
Q\longmapsto y^{-1}A^{-1}y.
\tag{14}
\]

Thus deletion returns the survivor pair to

\[
\bigl(B,\ y^{-1}A^{-1}y\bigr),
\tag{15}
\]

which is classically AC-equivalent to the original pair \((A,B)\).

The incorrect reverse-order substitution
\(q=M^{-1}L^{-1}\) would instead manufacture the appealing but false
survivor \(yxy^3x^{-4}\).  Equation (4) shows exactly why that endpoint
does not occur.

## 3. Scope

This theorem closes the complete mechanism

\[
q
\longrightarrow qC,
\qquad
A\longrightarrow A(gqCg^{-1}),
\qquad
\text{delete the changed \(A\)-slot}.
\]

It does not close a history in which:

1. the stored word is changed between manufacture and target
   multiplication;
2. two or more target multiplications occur before deletion;
3. the primitive relator contains several \(q^{\pm1}\)-letters;
4. the surviving \(Q\)-slot is itself changed by another retained
   source; or
5. a different relator is deleted.

AK(3), stable Andrews--Curtis, and Andrews--Curtis remain open.
