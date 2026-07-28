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

## 3. Scope of the one-storage theorem

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

The first and fourth items are sharpened by the next theorem.

## 4. Two storage rows and one extra multiplication are still gauge

Start from an old relator tuple

\[
(A,\mathbf B)
\tag{16}
\]

and stabilize with fresh generators \(q,r\).  Suppose restored source
moves manufacture

\[
Q=qC,
\qquad
R=rD,
\tag{17}
\]

where

\[
C,D\in
\langle\!\langle A,\mathbf B\rangle\!\rangle.
\tag{18}
\]

Let \(g\) be a word in the old generators.  Fix
\(\varepsilon\in\{+1,-1\}\) and change the \(A\)-slot to

\[
P=A(gQ^\varepsilon g^{-1}).
\tag{19}
\]

If no further move occurs, deleting \(q\) with the \(P\)-slot sends

\[
Q\longmapsto
K_\varepsilon
:=g^{-1}A^{-\varepsilon}g.
\tag{20}
\]

Indeed \(P=1\) gives \(Q^\varepsilon=g^{-1}A^{-1}g\), hence

\[
q=K_\varepsilon C^{-1}.
\tag{21}
\]

This includes the inverse-source orientation omitted from Section 1:
when \(\varepsilon=-1\), the survivor is \(g^{-1}Ag\).

Now allow exactly one additional AC multiplication before deleting
\(q\) with the changed \(P\)-slot.  Assume that the relator being
deleted still has exactly one occurrence of \(q^{\pm1}\).

### 4.1 A target other than \(P\)

Let

\[
\phi:F(\text{old generators},q,r)\longrightarrow
F(\text{old generators},r)
\tag{22}
\]

be the deletion substitution determined by (21).  Thus

\[
\phi(P)=1,
\qquad
\phi(Q)=K_\varepsilon,
\qquad
\phi(R)=R.
\tag{23}
\]

If the extra move changes a surviving relator \(T\) by multiplying it
on either side by a conjugate of another relator \(S^{\pm1}\), applying
\(\phi\) gives exactly the corresponding AC multiplication of
\(\phi(T)\) by a conjugate of \(\phi(S)^{\pm1}\).  If \(S=P\), the
factor disappears because \(\phi(P)=1\).  Therefore the whole extra
move either descends to a reversible survivor AC move or has no image.
Undo it after deletion and recover (20).

For the two storage rows, the four potentially misleading cases are
therefore only

\[
\begin{array}{c|c}
\text{extra move before deletion}
  &\text{survivors after deletion}\\ \hline
Q\mapsto QH_R &(K_\varepsilon\phi(H_R),\ R)\\
Q\mapsto H_RQ &(\phi(H_R)K_\varepsilon,\ R)\\
R\mapsto RH_Q &(K_\varepsilon,\ R\,\phi(H_Q))\\
R\mapsto H_QR &(K_\varepsilon,\ \phi(H_Q)R),
\end{array}
\tag{24}
\]

where \(H_R\) is a conjugate of \(R^{\pm1}\) and \(H_Q\) is a
conjugate of \(Q^{\pm1}\).  Every row of (24) is visibly the image of
the same survivor AC move and can be reversed.

### 4.2 The target \(P\)

It remains to multiply \(P\) on either side by a conjugate

\[
H=uS^\delta u^{-1},
\qquad \delta\in\{+1,-1\},
\tag{25}
\]

of a \(q\)-free surviving source \(S\).  Both choices make the changed
target equation equivalent to

\[
P=H^{-1}.
\tag{26}
\]

The conjugator \(u\) may itself contain \(q\).  Let \(\psi\) denote the
unique-\(q\) deletion substitution for the changed target, and put

\[
\overline H=\psi(H)
=\psi(u)S^\delta\psi(u)^{-1}.
\]

Thus \(\overline H\) remains a conjugate of the surviving source after
deletion.  Preserving the factor order gives

\[
\begin{array}{c|c}
\varepsilon
  & Q\text{ after deleting the changed target}\\ \hline
+1
  &K_+\,(g^{-1}\overline H^{-1}g)\\
-1
  &(g^{-1}\overline Hg)\,K_-.
\end{array}
\tag{27}
\]

The source \(S\) still survives.  In the first row, multiply \(Q\) on
the right by \(g^{-1}\overline Hg\); in the second, multiply it on the
left by \(g^{-1}\overline H^{-1}g\).  These are legal AC
multiplications by a conjugate of \(S^{\pm1}\), and they peel the
correction in (27), recovering \(K_\varepsilon\).

A \(Q\)-bearing source used to change \(P\) contributes a second
\(q^{\pm1}\)-occurrence, while its conjugator contributes an even
number.  Free cancellation removes occurrences in pairs.  Hence the
freely reduced changed target has an even number of q-letters and
cannot have exactly one.  It is outside the stated unique-letter
branch.

Finally,

\[
\langle\!\langle K_\varepsilon,\mathbf B\rangle\!\rangle
=
\langle\!\langle A,\mathbf B\rangle\!\rangle.
\tag{28}
\]

Consequently \(D\) is still a consequence of the recovered old tuple.
The normal-closure transvection lemma changes \(R=rD\) to \(r\), after
which \(r\) destabilizes.  Inverting and conjugating
\(K_\varepsilon\) recovers \(A\).

Hence every two-storage history of the stated form with one additional
AC multiplication is a stable self-loop.  The second storage row never
creates a lost-source effect: it remains present precisely long enough
to peel any correction that it inserts into the deleted target.

## 5. Frontier after one additional multiplication

An escape from this storage mechanism requires at least one of:

1. a dependency cycle in which the recovered-\(A\) row and the source
   needed to peel its correction are both changed or deleted;
2. a primitive eliminator with several \(q^{\pm1}\)-occurrences;
3. deletion of a slot other than the unique-\(q\) target; or
4. a stored row whose carrier is not a consequence of the ultimately
   retained tuple.

The smallest candidate storage branch therefore has two interacting
row changes, not one.  Its unique-letter part is closed next.

## 6. A changed storage source is consumed by unique-letter deletion

Work at a balanced presentation of the trivial group, so the established
substitution-and-removal composite is available.  Keep the old tuple
\((A,\mathbf B)\) and the first stored row

\[
Q=qC,
\qquad
C\in\langle\!\langle A,\mathbf B\rangle\!\rangle.
\tag{29}
\]

Let \(r\) be a second fresh generator.  At the checkpoint of interest,
let \(R'\) be any current relator in the second storage slot.  It may
have been changed by \(Q\), may contain q-letters, and need not retain
the spelling \(rD\).  Require only that the other displayed slots have
the spellings in this section.

Put

\[
P=A(gQ^\varepsilon g^{-1}),
\qquad
\varepsilon\in\{+1,-1\},
\tag{30}
\]

where \(g\) is a word in the old generators.  Use the changed second
row once as a source and replace the \(P\)-slot, on either side, by

\[
E=P\,u(R')^\eta u^{-1}
\quad\text{or}\quad
E=u(R')^\eta u^{-1}P,
\qquad
\eta\in\{+1,-1\}.
\tag{31}
\]

Assume the freely reduced word \(E\) contains exactly one
\(r^{\pm1}\)-letter.  It is then a primitive relator relative to the
other generators.  Let

\[
\psi:F(\text{old generators},q,r)
\longrightarrow F(\text{old generators},q)
\tag{32}
\]

be the substitution-and-removal homomorphism obtained by solving
\(E=1\) for \(r\).  Since \(P\) and \(Q\) are r-free,

\[
\psi(P)=P,
\qquad
\psi(Q)=Q.
\tag{33}
\]

Write \(\overline u=\psi(u)\).  Either placement in (31) gives

\[
\overline u\,\psi(R')^\eta\overline u^{-1}=P^{-1}.
\tag{34}
\]

Therefore the surviving changed storage row is forced to be

\[
\boxed{
\psi(R')
=
\overline u^{-1}P^{-\eta}\overline u.
}
\tag{35}
\]

This identity is independent of the spelling and entire prior history
of \(R'\).  It also allows \(u\) to contain r: only its deletion image
\(\overline u\) occurs in (35).

Invert the survivor when \(\eta=+1\), if necessary, and remove the
conjugator \(\overline u\).  Classical AC2--AC3 moves normalize its
slot to \(P\).  The literal \(Q\)-slot still survives, so one
matching-side multiplication gives

\[
P\,(gQ^{-\varepsilon}g^{-1})
=A.
\tag{36}
\]

The old tuple \((A,\mathbf B)\) has now been recovered.  Because \(C\)
lies in its normal closure, restored source transvections change

\[
Q=qC\longmapsto q.
\tag{37}
\]

The generator-relator pair \(q,q\) destabilizes.  Thus the whole
changed-source cycle returns to the original tuple.

### Theorem 6.1 (unique-r changed-source cycle)

At a balanced trivial-group checkpoint, every history satisfying
(29)--(31) whose final target contains exactly one
\(r^{\pm1}\)-letter is a stable self-loop.  Arbitrarily changing the
second storage row before using it as the final source does not create
an escape: deletion consumes that source and turns its surviving slot
into the target it had changed.

The replay covers both signs in (30), both signs in (31), left and
right \(Q\)-traffic into \(R'\), both placements of the final source,
and an r-dependent conjugator.

## 7. Exact remaining frontier

Results 110--111 close both the acyclic one-extra-edge layer and the
minimal changed-source cycle whenever the final deletion is a
unique-letter deletion in either fresh generator.  A storage escape
must now violate at least one of:

1. the final primitive relator has a unique \(q\)- or r-letter;
2. the changed source is used only once in the final target;
3. the literal \(Q\)-row survives long enough to peel (36);
4. the old carrier \(C\) remains a consequence of the recovered tuple;
   or
5. the relator changed by the consumed source is the relator that gets
   primitively deleted.

AK(3), stable Andrews--Curtis, and Andrews--Curtis remain open.
