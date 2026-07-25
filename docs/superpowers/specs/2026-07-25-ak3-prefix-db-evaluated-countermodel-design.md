# AK(3) prefix-DB evaluated countermodel design

Date: 2026-07-25

## Objective

Determine whether the evaluated prefix-\(DB\) equations, torus weight,
killer property, and central-quotient conjugacy criterion alone force the
remaining three-cross survivor to the AK(3) braid class.

## Canonical evaluated equation

Work in

\[
G=\langle x,t\mid x^3=t^4\rangle.
\]

For a final tail \(e\), put

\[
p=xt,\qquad b=e^{-1}p,\qquad d=t^{-1}exe^{-1}.
\]

For the \(DBD\) representative of the final-target-switch pair, evaluation
of the three cross events gives

\[
K=d\alpha b^\epsilon\alpha^{-1},\qquad
C=b\beta K^\eta\beta^{-1},\qquad
1=K\gamma C^\theta\gamma^{-1}.
\]

Here \(\alpha,\beta,\gamma\in G\) absorb evaluated bridges, multiplication
sides, and intermediate conjugations. With
\(\rho=\beta\gamma\) and \(m=\eta\theta\), the last two equations imply

\[
C=b\rho C^{-m}\rho^{-1},
\qquad
b=C\rho C^m\rho^{-1}.
\]

These identities are necessary for liftability to the original
\(H=G*\langle z\rangle\) history.

## Countermodel

Use the feasible sign row

\[
(\epsilon,\eta,\theta)=(1,1,-1).
\]

First define quotient words in
\(\Gamma=C_3*C_4=\langle X,T\mid X^3=T^4=1\rangle\):

\[
\begin{aligned}
C_0&=X^2T^3X^2,\\
\rho=\beta&=X^2,\qquad \gamma=1,\\
b_0&=X^2T^3X^2TX^2,\\
E_0&=XTXT^3XTX,\\
\alpha&=XTXT^3XT.
\end{aligned}
\]

Put \(P=XT\) and \(d_0=T^{-1}E_0XE_0^{-1}\). Direct alternating-normal-form
reduction gives

\[
E_0^{-1}P=b_0,\qquad
d_0\alpha b_0\alpha^{-1}=C_0,\qquad
C_0=b_0\beta C_0\beta^{-1}.
\]

The last cross equation is \(C_0C_0^{-1}=1\).

Lift these words to \(G\) with central powers so that

\[
\operatorname{wt}(e)=7,\qquad
\operatorname{wt}(b)=0,\qquad
\operatorname{wt}(C)=1.
\]

Projected equality plus equal weight then makes all displayed identities
exact in \(G\).

The projection of \(C\) cyclically reduces to \(XT^3\), of length \(2\).
The projection of \(D_p=t^{-1}(xt)x(xt)^{-1}\) has cyclic length \(6\).
Thus \(C\) is not conjugate to \(D_p^{\pm1}\).

Nevertheless \(C\) is a killer. Killing \(XT^3\) in \(C_3*C_4\) identifies
\(X=T\), and the orders \(3\) and \(4\) then kill both. The quotient of
\(G\) by \(C\) is consequently cyclic central, while its abelianization
is killed by \(\operatorname{wt}(C)=1\); hence it is trivial.

## Scope

This is a countermodel to the evaluated equation, not a stable-AC
counterexample and not a realized three-cross history.

An actual history additionally requires an orientation \(D_2^\delta\) of
its final target in \(H=G*\langle z\rangle\) to have cyclically reduced
syllable length \(2\) and be conjugate to \(z^{-1}e\). Evaluation only
says that target becomes trivial after \(z=e\).

For the explicit row, \(\delta=-1\). Quotienting by the original
\(B=z^{-1}p\) sends \(D_2\), up to conjugacy and inversion, to a commutator
\([D_p,h]\). A legal lift would force this commutator to be conjugate to
\(b=e^{-1}p\). In \(C_3*C_4\), \(\bar b\) has cyclic length \(4\), whereas
the complete Bass--Serre edge/vertex reduction gives commutator lengths
\(0,8,10,12\), or at least \(14\). Thus this countermodel is rigorously
nonliftable.

Whether every other liftable prefix-\(DB\) solution returns to the braid
class is the new exact frontier.

## Verification

A dependency-free replay will check:

- all three exact \(G\) identities by amalgam normal form;
- the feasible weights \(7\) and \(1\);
- cyclic lengths \(2\) and \(6\) in \(C_3*C_4\); and
- the \(216\)-case quotient-\(B\) commutator sieve.

No AC graph search is used. AK(3) remains open.
