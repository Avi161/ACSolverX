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

The immediate two-stage deletion part of the remaining multi-letter
branch is closed next.

## 8. Immediate second deletion gives only an ambient-Aut endpoint

Let \(F_0\) be the old free group of finite rank \(n\), and work at a
balanced trivial-group checkpoint in

\[
F=F_0*\langle q,r\rangle.
\tag{38}
\]

Assume that the two current storage rows \(P,R'\) form a relative
primitive pair: there is an automorphism

\[
\Phi\in\operatorname{Aut}(F)
\tag{39}
\]

which fixes \(F_0\) pointwise and satisfies

\[
\Phi(q)=P,
\qquad
\Phi(r)=R'.
\tag{40}
\]

The minimal triangular storage checkpoint has this property: \(P\)
contains q exactly once and no r, while \(R'\) contains r exactly once
after the q-row has been fixed.

Use \(R'\) once as a source to form

\[
W=P\,u(R')^\eta u^{-1}
\quad\text{or}\quad
W=u(R')^\eta u^{-1}P,
\qquad
\eta\in\{+1,-1\}.
\tag{41}
\]

Now drop every unique-letter assumption and suppose only that \(W\) is
primitive in \(F\).  Primitive-delete \(W\), and let \(s\) be the image
of the surviving \(R'\)-row in

\[
H=F/\langle\!\langle W\rangle\!\rangle
\cong F_{n+1}.
\tag{42}
\]

Because the extra factor in (41) lies in the normal closure of \(R'\),
both multiplication orders give the exact kernel identity

\[
\boxed{
\langle\!\langle W,R'\rangle\!\rangle_F
=
\langle\!\langle P,R'\rangle\!\rangle_F.
}
\tag{43}
\]

Relative primitivity and (43) imply

\[
\begin{aligned}
H/\langle\!\langle s\rangle\!\rangle_H
&\cong
F/\langle\!\langle W,R'\rangle\!\rangle_F\\
&\cong
F/\langle\!\langle P,R'\rangle\!\rangle_F\\
&\cong F_0.
\end{aligned}
\tag{44}
\]

The classical one-relator freeness theorem says that a quotient of a
finite-rank free group by one nontrivial relator is free of rank one
less exactly when that relator is primitive.  Hence \(s\) is primitive
in \(H\).  An immediate second primitive deletion is therefore legal.

For completeness, this implication can also be factored through two
standard results.  Nielsen-reduce an epimorphism
\(F_{n+1}\twoheadrightarrow F_n\) to the standard projection; its
kernel is normally generated by a primitive element \(t\).  Since the
same kernel is \(\langle\!\langle s\rangle\!\rangle\), Magnus's
normal-closure theorem makes \(s\) conjugate to \(t^{\pm1}\).

Let

\[
\rho:F\longrightarrow F_0
\tag{45}
\]

kill \(q,r\) and fix \(F_0\).  The canonical relative-pair quotient is

\[
\kappa=\rho\Phi^{-1}.
\tag{46}
\]

Its kernel is the right side of (43), and \(\kappa\) restricts to the
identity on \(F_0\).  Let

\[
\theta:F\longrightarrow F_0
\tag{47}
\]

be the combined quotient map determined by the chosen \(W\)-deletion
and immediate \(s\)-deletion.  Equations (43)--(44) give

\[
\ker\theta=\ker\kappa.
\tag{48}
\]

Therefore the two induced isomorphisms
\(F/\ker\kappa\to F_0\) differ by an automorphism:

\[
\boxed{
\theta=\alpha\kappa
\quad\text{for some}\quad
\alpha\in\operatorname{Aut}(F_0).
}
\tag{49}
\]

Every restored old relator \(T\in F_0\) consequently reaches

\[
\theta(T)=\alpha(T).
\tag{50}
\]

### Theorem 8.1 (two-stage primitive cycle reduction)

Under the balanced trivial-group and relative-primitive-pair hypotheses,
every primitive multi-letter target (41), followed immediately by
deletion of its surviving source image, ends at one simultaneous
ambient automorphic image of the old relator tuple.  The stable ambient
automorphism theorem returns that endpoint to the old stable class.

This is deliberately not a claim of classical AC equivalence.  The
project's ambient-automorphism theorem is stable, and no classical
realization of the particular \(\alpha\) in (49) has been proved.
Nor does the theorem say that \((W,R')\) is a primitive pair upstairs.

## 9. Exact remaining storage frontier

The multi-letter cycle can matter only if the history uses the
intermediate rank-\((n+1)\) tuple after deleting \(W\) and before
deleting \(s\).  Concretely, it must:

1. alter another survivor using \(s\) or another post-deletion row;
2. change \(s\) before its forced primitive deletion;
3. lose the relative-primitive-pair property before forming \(W\);
4. use the changed source more than once; or
5. avoid the two-stage kernel equality (43) by deleting a different
   primitive slot.

The first post-deletion edge is narrowed further next.

## 10. Zero-bridge traffic into the surviving primitive slot closes

Normalize the intermediate tuple stably as in Theorem 8.1, so its
primitive survivor is the literal relator \(r\) and its old survivor
tuple

\[
\mathbf T=(T_1,\ldots,T_n)
\tag{51}
\]

lies in \(F_0\).  Fix one old source \(V=T_j\).  Consider one
multiplication targeting the r-slot:

\[
r\longmapsto r\,cV^\epsilon c^{-1}
\quad\text{or}\quad
r\longmapsto cV^\epsilon c^{-1}r,
\qquad
\epsilon\in\{+1,-1\}.
\tag{52}
\]

Use the free-product splitting

\[
F_0*\langle r\rangle.
\tag{53}
\]

The fixed vertex of \(\langle r\rangle\) and the fixed vertex
\(cF_0\) of the conjugated old factor are adjacent in its Bass--Serre
tree exactly when

\[
c\in\langle r\rangle F_0.
\tag{54}
\]

This is the zero-bridge case.  Write

\[
c=r^k a,
\qquad
k\in\mathbb Z,
\qquad
a\in F_0.
\tag{55}
\]

Put \(H=cV^\epsilon c^{-1}\).  The left target in (52) is conjugate to
the right target because

\[
H^{-1}(Hr)H=rH.
\tag{56}
\]

For the right target, conjugation by \(r^{-k}\) gives the exact free
group identity

\[
\begin{aligned}
r^{-k}
\bigl(r\,r^kaV^\epsilon a^{-1}r^{-k}\bigr)
r^k
&=
r\,aV^\epsilon a^{-1}.
\end{aligned}
\tag{57}
\]

The final word contains exactly one \(r\)-letter.  The stable
substitution-and-removal composite deletes it with the r-generator.
Every old survivor \(T_i\), including the source \(V\), is r-free and
therefore remains literal.  The endpoint is exactly \(\mathbf T\).

### Theorem 10.1 (zero-bridge primitive-slot traffic)

At a normalized balanced trivial-group checkpoint
\((\mathbf T,r)\), every one-edge target multiplication (52) whose
relative conjugator has zero Bass--Serre bridge is a stable self-loop
with literal endpoint \(\mathbf T\).  Its target normalization is
classical AC3; the rank-changing unique-r deletion is the stable
substitution-and-removal composite.  No primitivity assumption is
needed: (57) proves the changed target primitive.

Combined with Theorem 8.1, a post-cycle one-edge escape requires

\[
\boxed{
c\notin\langle r\rangle F_0,
}
\tag{58}
\]

so the \(\langle r\rangle\)-vertex and the conjugated old-factor vertex
have strictly positive bridge length.  The shortest apparent primitive
\(r^2V r^{-1}\) is not exceptional; it is the \(k=1,a=1\) instance of
(57).

## 11. Exact remaining storage frontier

After normalization, the first unresolved event is

\[
r\longmapsto r\,cV^\epsilon c^{-1}
\tag{59}
\]

with positive Bass--Serre bridge, followed by primitive deletion of
the changed r-slot.  All q-free or zero-bridge conjugators, all traffic
away from the primitive slot, unique-letter changed-source cycles, and
immediate second deletions are already closed.  A proof must now either:

1. show that positive-bridge words (59) are nonprimitive for the AK
   source relators;
2. classify their primitive quotient maps; or
3. use more than one post-deletion target edge.

## 12. Positive-bridge traffic into the primitive slot is impossible

For the two AK source relators

\[
A=x^3y^{-4},
\qquad
B=xyxy^{-1}x^{-1}y^{-1},
\tag{60}
\]

the first alternative in Section 11 can now be proved.  Let

\[
W=r\,cV^\epsilon c^{-1},
\qquad
V\in\{A,B\},
\qquad
\epsilon=\pm1,
\tag{61}
\]

and suppose for contradiction that \(W\) is primitive.  Then

\[
Q=(F_0*\langle r\rangle)/
\langle\!\langle W\rangle\!\rangle\cong F_2.
\tag{62}
\]

Freiheitssatz embeds the old factor as a rank-two subgroup
\(K\cong F_0\) of \(Q\).  If \(v\) is the image of \(V\), then killing
\(v\) gives the exact quotient isomorphism

\[
K/\langle\!\langle v\rangle\!\rangle_K
\cong
Q/\langle\!\langle v\rangle\!\rangle_Q
\cong
F_0/\langle\!\langle V\rangle\!\rangle.
\tag{63}
\]

For \(A\), this is the \((3,4)\)-torus-knot group.  For \(B\), the
basis

\[
a=xyx,
\qquad b=xy,
\qquad x=b^{-1}a,
\qquad y=a^{-1}b^2
\tag{64}
\]

puts \(B\) in the conjugacy class of \(a^2b^{-3}\), so (63) is the
\((2,3)\)-torus-knot group.

The Collins--Zieschang classification has a single Nielsen class of
two-generator one-relator presentations for each of these two small
torus-knot groups.  After automorphisms in the source and target, the
inclusion \(K\hookrightarrow Q\) is therefore an injective endomorphism
of \(F_2\) taking the standard torus relator
\(R=X^pY^q\) to \(R^{\pm1}\).  The word \(R\) is non-simple.  Turner's
monomorphism-test theorem makes the endomorphism an automorphism; in the
negative case apply the theorem to its square.  Hence

\[
K=Q.
\tag{65}
\]

Identify \(Q\) with \(F_0\) through this isomorphism.  The quotient map
now fixes \(F_0\) and sends \(r\) to some \(u\in F_0\).  Magnus's
normal-closure theorem makes \(W\) conjugate to
\((ru^{-1})^{\pm1}\), of cyclic free-product syllable length at most
two.  If \(c\notin\langle r\rangle F_0\), shortest double-coset normal
form instead makes (61) cyclically reduced of syllable length at least
six.  This contradiction proves

\[
\boxed{
W\text{ primitive}
\quad\Longrightarrow\quad
c\in\langle r\rangle F_0.
}
\tag{66}
\]

### Theorem 12.1 (complete one-edge primitive-slot closure)

At the normalized AK checkpoint \((\mathbf T,r)\), where the chosen old
source is \(A\) or \(B\), no one-edge multiplication into the r-slot can
escape.  A zero-bridge conjugator is the literal stable self-loop of
Theorem 10.1.  A positive-bridge conjugator produces a nonprimitive
target by (66), so the proposed primitive deletion cannot occur.

The next storage frontier must use at least two post-deletion row-changing
edges, change the source before it is used, delete another primitive slot,
or leave the normalized checkpoint.  AK(3), stable Andrews--Curtis, and
Andrews--Curtis remain open.

## 13. One old-factor source change has an exact rigidity obstruction

Result 12 extends conditionally beyond the two original sources.  Call a
non-simple word \(V\in F_0\) admissibly Nielsen-rigid if every injective
endomorphism \(\phi:F_0\to F_0\) which is unimodular on abelianization
and induces an isomorphism

\[
F_0/\langle\!\langle V\rangle\!\rangle
\xrightarrow{\ \cong\ }
F_0/\langle\!\langle\phi(V)\rangle\!\rangle
\tag{67}
\]

carries \(\phi(V)\), after a target automorphism, to a conjugate of
\(V^{\pm1}\).  The quotient proof of Section 12 then applies verbatim:
Turner makes the aligned injection onto, and positive bridge length
contradicts Magnus rigidity.  Hence

\[
V\text{ non-simple and admissibly Nielsen-rigid}
\Longrightarrow
rcV^\epsilon c^{-1}\text{ nonprimitive for positive bridge}.
\tag{68}
\]

Now make one row multiplication inside the old factor before targeting r.
Up to conjugacy and inversion, its changed source is

\[
V^A_{g,\eta}=AgB^\eta g^{-1}
\quad\text{or}\quad
V^B_{g,\eta}=BgA^\eta g^{-1},
\qquad
g\in F_0,
\quad\eta=\pm1.
\tag{69}
\]

Axis alignment reduces the minimum cyclic length over arbitrary \(g\) to
the finite cyclic-rotation table for \(A\) and \(B\).  Osborne--Zieschang
then gives

\[
\begin{array}{c|c|c}
\eta&\min_g\|V^A_{g,\eta}\|&
\text{cyclic length if primitive}\\
\hline
+1&11&9\\
-1&9&5.
\end{array}
\tag{70}
\]

The B-target versions have the same lengths.  Thus none of (69) is
primitive.  Their exponent vectors are primitive, so none is a proper
power; in rank two they are consequently non-simple.

### Theorem 13.1 (z-free changed-source reduction)

After one arbitrary old-factor source change (69), a zero-bridge
multiplication into the r-slot is still a stable self-loop.  A
positive-bridge primitive target can exist only if its changed source
fails admissible Nielsen rigidity.  Concretely, the primitive quotient
must supply a proper unimodular injection \(\phi:F_2\hookrightarrow F_2\)
which induces (67) but puts \(\phi(V)\) outside the Aut-orbit of conjugates
of \(V^{\pm1}\).

The next proof problem is therefore no longer arbitrary source
primitivity.  It is the existence or exclusion of that marked proper
self-embedding, an r-dependent first source change, or two direct source
multiplications into the r-slot.  AK(3), stable Andrews--Curtis, and
Andrews--Curtis remain open.

## 14. Two direct sources force simultaneous relative torus extensions

Consider the two-source target

\[
W=r\,cA^\epsilon c^{-1}dB^\eta d^{-1},
\qquad
\epsilon,\eta=\pm1,
\tag{71}
\]

and let \(\lambda(W)\) be its cyclic syllable length in
\(F_0*\langle r\rangle\).  If \(W\) is primitive, Freiheitssatz again
embeds \(K\cong F_0\) in \(Q\cong F_2\).  Kill the image of A.  The exact
quotient is

\[
P_A\cong
\langle G_{3,4},r\mid r d_A B_A^\eta d_A^{-1}\rangle,
\tag{72}
\]

where \(d_A\) retains every r-letter of \(d\).  Klyachko's theorem for
unimodular equations over torsion-free groups injects the coefficient
group

\[
G_{3,4}\hookrightarrow P_A.
\tag{73}
\]

This inclusion is an isomorphism on first homology, and \(B_A\) normally
generates \(P_A\).  Killing B symmetrically gives

\[
G_{2,3}\hookrightarrow
P_B\cong
\langle G_{2,3},r\mid r c_B A_B^\epsilon c_B^{-1}\rangle,
\tag{74}
\]

again homologically onto, with \(A_B\) normally generating \(P_B\).

If either coefficient inclusion is onto, the small torus-relator
classification and Turner force \(K=Q\).  Magnus rigidity then gives
\(\lambda(W)\le2\).  Therefore

\[
\boxed{
W\text{ primitive and }\lambda(W)>2
\Longrightarrow
G_{3,4}\lneq P_A
\text{ and }
G_{2,3}\lneq P_B.
}
\tag{75}
\]

### Theorem 14.1 (simultaneous-extension obstruction)

A genuine two-source primitive deletion requires both proper relative
extensions in (75) simultaneously.  Each retains the same first homology
as its coefficient group, and each is normally generated by the other AK
source.

Combining the source factors in (71) gives

\[
Z=A^\epsilon(c^{-1}d)B^\eta(c^{-1}d)^{-1}.
\tag{76}
\]

The relator killed in Q is the image of Z, whereas the relator killed in K
is obtained by first setting \(r=1\) in Z.  These marked relators need not
agree, so the one-source Turner argument does not apply without additional
alignment.

The length condition in (75) is essential.  If \(c,d\in F_0\), then
\(W=rU\) is primitive.  Even \(c=1,d=r\) cyclically reduces to a one-r
word of syllable length two.  The next theorem must exclude the
simultaneous proper extensions, align the two marked relators, or exploit
the geometry of both relative equations together.  AK(3), stable
Andrews--Curtis, and Andrews--Curtis remain open.

## 15. The simultaneous-extension obstruction is sharp

Let \(H=F(X,U)\), \(Q=F(x,y)\), and define

\[
u=yxyx^{-1}y^{-1},
\qquad
\phi(X)=x,
\qquad
\phi(U)=u.
\tag{77}
\]

This is an injective unimodular map with proper image
\(K=\langle x,u\rangle<Q\).  For every root-free \(V\in H\), Tietze
transformation gives

\[
Q/\langle\!\langle\phi(V)\rangle\!\rangle
\cong
\langle G(V),y\mid U^{-1}yXyX^{-1}y^{-1}\rangle.
\tag{78}
\]

The relative relator has y-exponent one, so Klyachko embeds \(G(V)\).
For \(V=A,B\), both embeddings are proper: finite quotients \(S_4\) and
\(S_3\) separate y from the respective coefficient subgroups.  The pair
\(\phi(A),\phi(B)\) normally generates Q, so the opposite sources normally
generate both relative quotients.

The embedding is induced by the primitive relator

\[
R=U^{-1}rXrX^{-1}r^{-1},
\tag{79}
\]

which has cyclic \(H*\langle r\rangle\)-syllable length six.  Solving it
gives \(U=rXrX^{-1}r^{-1}\), exactly (77) after renaming \(r=y\).
It is not a word of the two-source form (71): its exponent vector is
\((0,-1,1)\), while (71) has old-factor vector
\(\pm(4,-5)\) or \(\pm(2,-3)\).

### Theorem 15.1 (sharpness of Theorem 14.1)

Primitivity with cyclic syllable length greater than two, proper old-factor
embedding, both proper torus coefficient extensions, both first-homology
isomorphisms, and opposite-source normal generation can all occur
simultaneously.  None of these abstract properties can close the
two-source branch.  A proof must use the exact factorization in (71) by one
conjugate of A and one conjugate of B.

## 16. A proper stable self-embedding corridor

The sharpness example is reachable from the AK tuple.  In
\((A(X,U),B(X,U),r)\), the normal closure of the old source rows contains

\[
[X,r]U^{-1}.
\tag{80}
\]

Consequently AC2 moves targeting r change it to

\[
r[X,r]U^{-1},
\tag{81}
\]

which is conjugate to R.  Primitive substitution and U-removal sends the
surviving rows to

\[
(\phi(A),\phi(B)).
\tag{82}
\]

### Theorem 16.1 (parafree AK corridor)

The AK presentation is stably AC-equivalent to its image under the proper
injective endomorphism

\[
\phi(x)=x,
\qquad
\phi(y)=yxyx^{-1}y^{-1}.
\tag{83}
\]

Iteration gives stable equivalences to
\((\phi^n(A),\phi^n(B))\) for every \(n\ge0\), and the image subgroups form
a strictly descending chain.  This is not an ambient-automorphism
self-loop, but it does not yet trivialize AK(3).  The new live question is
whether this proper corridor supplies a shorter primitive compression or
an invariant monotone under iteration.  Stable Andrews--Curtis and
Andrews--Curtis remain open.

## 17. Arbitrary conjugating endomorphisms have stable lifts

The preceding map is part of a general family.  For any
\(g\in F(x,y)\), put

\[
\phi_g(x)=x,
\qquad
\phi_g(y)=g y g^{-1}.
\tag{84}
\]

The image vectors are the standard basis, so \(\phi_g\) is injective, and
its image normally generates \(F_2\).  For every root-free V, Klyachko
injects the induced one-relator map: the relative relator

\[
U^{-1}g(X,y)y g(X,y)^{-1}
\tag{85}
\]

has y-exponent one.

In the stabilized group, define

\[
R_g=U^{-1}g(X,r)r g(X,r)^{-1}.
\tag{86}
\]

It contains U once and is primitive.  Killing the old AK source normal
closure sends \(R_g\) to r, so \(r^{-1}R_g\) belongs to that normal
closure.  Finite AC2 traffic therefore replaces the r-row by \(R_g\),
and primitive U-deletion leaves

\[
(\phi_g(A),\phi_g(B)).
\tag{87}
\]

### Theorem 17.1 (conjugating-endomorphism corridor)

For every g,

\[
(A,B)\sim_{\mathrm{stable\ AC}}
(\phi_g(A),\phi_g(B)).
\tag{88}
\]

Whenever \(\phi_g\) is proper, (88) is a nonautomorphic stable corridor.
The case \(g=yx\) is Theorem 16.1.  The next theoretical attack can now
vary g deliberately to seek a new primitive compression or prove a
family-wide barrier, without an AC graph search.  AK(3), stable
Andrews--Curtis, and Andrews--Curtis remain open.

## 18. Internal conjugators remain trapped in every corridor

Let \(K_g=\phi_g(F_2)\).  If \(h\in K_g\), write \(h=\phi_g(k)\).  A
one-source multiplication in the image then has the form

\[
\phi_g(A)h\phi_g(B)^\eta h^{-1}
=\phi_g(AkB^\eta k^{-1}),
\tag{89}
\]

or the same formula with A and B exchanged.  The word inside \(\phi_g\)
is nonprimitive by the unbounded axis-alignment theorem, and its exponent
vector is one of \((4,-5),(2,-3),(-2,3)\).  It is therefore root-free.

Klyachko embeds its one-relator quotient into the quotient by (89).  If
(89) were primitive, the target quotient would be \(\mathbb Z\), so the
source quotient would be cyclic.  Its abelianization is \(\mathbb Z\),
and Magnus normal-closure rigidity would then force the source relator to
be primitive, a contradiction.

### Theorem 18.1 (family-wide internal-conjugator barrier)

For every g, every \(h\in K_g\), and both signs, both one-source relative
products of \(\phi_g(A)\) and \(\phi_g(B)\) are nonprimitive.  Therefore a
one-step primitive compression reached through a proper corridor must use
a conjugator outside \(K_g\).  The remaining problem lives in the
nontrivial double cosets \(K_g\backslash F_2/K_g\), or beyond one-source
traffic altogether.

## 19. The first proper corridor closes every double coset

For \(g=yx\), write \(a=\phi_g(A)\), \(b=\phi_g(B)\).  Their exact cyclic
words have lengths 11 and 18.  Direct cyclic-factor comparison gives

\[
L(a,b^{-1})=3,
\qquad
L(a,b)=4.
\tag{90}
\]

Axis alignment over every \(h\in F_2\) now yields

\[
\min_h\|a hbh^{-1}\|=23,
\qquad
\min_h\|a hb^{-1}h^{-1}\|=21.
\tag{91}
\]

The Osborne--Zieschang primitive lengths for the relevant exponent
vectors are only 9 and 5.

### Theorem 19.1 (ambient-conjugator barrier at the first proper image)

For both source orders, both signs, and every ambient conjugator h, the
one-source relative product of \(\phi_{yx}(A)\) and \(\phi_{yx}(B)\) is
nonprimitive.  Thus the first proper stable image has no one-source
primitive exit in any image-subgroup double coset.  General g and the
deeper iterates remain open.

## 20. The first image has exact external minimum 25

The folded core of \(K=\langle x,yxyx^{-1}y^{-1}\rangle\) is the barbell
with a path labelled yx between the x- and y-loops.  Its off-diagonal fiber
product is a two-edge path, so two distinct lifts have common reduced
length at most two.  Therefore, for the image sources a,b and every
\(h\notin K\),

\[
\|a hb^\eta h^{-1}\|
\ge |a|+|b|-4=25.
\tag{92}
\]

The external conjugators y for \(\eta=1\) and xxYX for \(\eta=-1\)
attain 25 and fail the core membership test.

### Theorem 20.1 (exact external-double-coset barrier)

For both source orders and both signs, the exact minimum over external
double cosets of the first proper image subgroup is 25.  The smaller
global minima 23 and 21 occur internally and are nonprimitive by Theorem
18.1.  For a general conjugating corridor, the remaining invariant is the
off-diagonal fiber-product overlap diameter of its normalized barbell
core.

## 21. A uniform barbell bound closes every conjugating corridor

Normalize \(g=x^pcy^q\), where a nonempty c begins in \(y^{\pm1}\), ends
in \(x^{\pm1}\), and has length \(n\ge2\).  The folded core of
\(K_c=\langle x,cyc^{-1}\rangle\) is the barbell with bridge c.

Two paths in an off-diagonal fiber-product component retain their order
along the bridge.  The lower path can use only the x-loop and the upper
only the y-loop, each in at most one block.  If both loops occur, their
common label lies in both \(c^{-1}x^kc\) and \(cy^\ell c^{-1}\).  The
x-block occupies at most one c-flank in the latter, proving the uniform
piece bound \(3n\).

The image-source lengths are \(2n+7\) and \(6n+6\), so every external
relative conjugator has cyclic length at least

\[
(2n+7)+(6n+6)-6n=2n+13\ge17.
\tag{93}
\]

Internal conjugators are already closed by Theorem 18.1.

### Theorem 21.1 (family-wide one-source corridor barrier)

For every conjugating endomorphism \(\phi_g\), every ambient relative
conjugator, both signs, and both source orders, one multiplication between
the two image sources is nonprimitive.  This remains true at every depth
of the descending proper corridor.  Any successful use must change both
rows before the primitive test or use a different stabilizer architecture.

## 22. Conjugating corridor maps reflect primitivity

For every word V, a primitive \(\phi_g(V)\) forces V to be root-free.
Klyachko embeds \(G(V)\) into the cyclic quotient by \(\phi_g(V)\).
Abelianization is unchanged by \(\phi_g\), so \(G(V)_{\rm ab}\cong
\mathbb Z\); hence \(G(V)\cong\mathbb Z\).  Magnus normal-closure rigidity
then makes V primitive.

### Theorem 22.1 (internal histories lift)

Every \(\phi_g\) reflects primitive elements.  Therefore every finite
AC1--AC3 history on an image pair whose conjugators remain in \(K_g\)
pulls back move-for-move to the original AK pair, and an ambient-primitive
terminal pulls back to a primitive terminal.  A genuinely new history at
any corridor depth must use an external conjugator or move the image
subgroup by an ambient automorphism.

## 23. An external second B-edge is too long

Let \(a_1=a h b^\epsilon h^{-1}\) with \(h\in K_g\), and then
\(b_1=b k a_1^\delta k^{-1}\) with \(k\notin K_g\).  In a proper
normalized corridor of bridge length n, the b-axis has length \(6n+6\),
the changed a-row has length at least 9 or 5, and the external axis overlap
is at most \(3n\).  Hence

\[
\|b_1\|\ge\|a_1\|+6.
\tag{94}
\]

The four resulting lower bounds are \(15,15,11,11\), whereas the
primitive lengths dictated by abelianization are \(11,7,7,3\).

### Theorem 23.1 (external-second-edge barrier)

An internal change of the A-image followed by an externally conjugated
change of the B-image cannot produce a primitive second row.  If the
second conjugator is internal, the history pulls back by Theorem 22.1.
Thus a genuinely new exit in this orientation must already be external
on its first edge.  The reverse B-first/A-second orientation remains open.
