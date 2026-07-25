# Final-target switch duality for one-\(z\) deletion

Date: 2026-07-25

Status: **PROVEN** for arbitrary current slot words, arbitrary relative
conjugator, either multiplication side, either source orientation, and
fixed-retained-relator quotient gauges, under the stated final survivor
restoration condition. Switching which slot is targeted by the last cross
event preserves the classical endpoint class after deletion. Applied to
AK(3), the two remaining three-cross killer words \(DBB\) and \(DBD\)
are one mechanism, not two. The mechanism itself remains open.

## 1. Abstract setup

Let \(R\in F(x,t)\), put

\[
G=\langle x,t\mid R\rangle,
\qquad
H=G*\langle z\rangle,
\tag{1.1}
\]

and let \(A,B\in H\) be the quotient shadows of the two current non-\(R\)
relator slots immediately before the final cross event.

Choose

\[
u\in H,
\qquad
\theta\in\{1,-1\}.
\tag{1.2}
\]

After choosing multiplication side, the event targeting \(A\) has target
class represented by

\[
T_A=A\,uB^\theta u^{-1}.
\tag{1.3}
\]

The left-multiplication spelling

\[
uB^\theta u^{-1}A
\tag{1.4}
\]

is cyclically conjugate to (1.3), so it adds no case at the level of the
final target conjugacy class.

Suppose a final orientation and conjugation normalize this target to a
one-\(z\) isolator:

\[
I=aT_A^\delta a^{-1}=z^{-1}e,
\qquad
\delta\in\{1,-1\},
\qquad
e\in F(x,t).
\tag{1.5}
\]

## 2. The same target class comes from targeting \(B\)

Cyclically move the first factor of (1.3) to the end. The word

\[
T_B=B^\theta u^{-1}Au
\tag{2.1}
\]

is conjugate to \(T_A\). More explicitly,

\[
T_B
=
(Au)^{-1}T_A(Au).
\tag{2.2}
\]

Equation (2.1) is a legal cross event targeting the other slot:

1. orient the \(B\)-slot as \(B^\theta\);
2. use \(A\) as source with conjugator \(u^{-1}\); and
3. multiply on the right.

If \(\theta=-1\), the first step is simply whole-target inversion.
Arbitrary whole-target conjugation can be included in the final
normalization.

Because of (2.2), replace \(a\) in (1.5) by the adjusted conjugator and
obtain the same isolator from \(T_B\). If \(A,B,T_A\) denote quotient
shadows of actual \(R\)-gauged spellings, this equality initially holds in
\(H\). The fixed-relator normal-closure lemma uses the retained \(R\)-slot
to replace the alternate target by the required literal representative
before normalization. Thus the identical literal isolator \(I=z^{-1}e\),
tail \(e\), and stable deletion are available with either slot designated
as target.

## 3. The two survivors are classically equivalent

Evaluate at \(z=e\). Write

\[
A_e=A[z\mapsto e],
\qquad
B_e=B[z\mapsto e],
\qquad
u_e=u[z\mapsto e].
\tag{3.1}
\]

The isolator becomes the identity, so (1.3) gives in \(G\)

\[
[A_eu_eB_e^\theta u_e^{-1}]_G=1.
\tag{3.2}
\]

Therefore

\[
\boxed{
[A_e]_G
=
[u_eB_e^{-\theta}u_e^{-1}]_G.
}
\tag{3.3}
\]

If \(A\) is targeted and deleted, the survivor is \(B_e\). If \(B\) is
targeted through (2.1) and deleted, the survivor is \(A_e\). Equation
(3.3) says the two survivors are conjugate up to inversion in the
fixed-\(R\) quotient.

Choose a literal free-group representative \(V\) of the right side of
(3.3). Then

\[
A_e^{-1}V\in\langle\!\langle R\rangle\!\rangle.
\tag{3.4}
\]

The fixed-relator normal-closure lemma replaces \(A_e\) by \(V\) through
classical AC1--AC3 moves. AC3 removes the conjugator and AC1 removes the
sign. Hence

\[
\boxed{
(R,A_e)
\sim_{\mathrm{AC1-3}}
(R,B_e).
}
\tag{3.5}
\]

If either surviving slot undergoes later fixed-\(R\) gauges,
conjugation, or inversion, require its final quotient shadow to be restored
in the corresponding signed-conjugate orbit. The same argument applies.

The stable operation here is the substitution-and-removal composite, not
a bare AC5 deletion.

## 4. Target words pair by their last letter

Consider any fixed cross history before its final event. Theorem (3.5)
pairs the two choices for the last target without changing the classical
endpoint class. For exactly three events:

\[
\boxed{
\begin{aligned}
BBB&\longleftrightarrow BBD,\\
BDD&\longleftrightarrow BDB,\\
DBB&\longleftrightarrow DBD,\\
DDB&\longleftrightarrow DDD.
\end{aligned}
}
\tag{4.1}
\]

The letters record target slots. The prefix is unchanged; only the final
target is switched.

This explains the duplicate arithmetic and identical untwisted seam
counts found in the complete target-word classification. It is stronger
than those finite coincidences because the proof allows an arbitrary
relative conjugator at the final event.

## 5. Consequence for the three-cross frontier

The complete target-word theorem left two arbitrary bridge/twist killer
words:

\[
DBB,\qquad DBD.
\tag{5.1}
\]

Equation (4.1) identifies their endpoint classes. Therefore exactly-three
cross traffic has only one unresolved mechanism, represented by:

1. first target \(D\) using \(B^\epsilon\);
2. then target \(B\) using the modified \(D_1^\eta\); and
3. use either current slot as the final target.

If a one-\(z\) isolator occurs, the survivor lies in the same classical
endpoint class regardless of the third target choice.

This theorem does not prove that endpoint is \(D_p\), does not remove the
arbitrary bridge/twist or literal \(R\)-gauge equation in the prefix
\(DB\), and does not address restoration failure, a changed retained
relator, or a multi-\(z\) primitive eliminator.

AK(3) remains open.
