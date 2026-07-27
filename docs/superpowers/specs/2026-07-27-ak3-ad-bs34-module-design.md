# AK(3) A--D \(BS(3,4)\) module design

Date: 2026-07-27

## Objective

Attack the three exact A--D projection fibers left by Result 56 using
the universal pair quotient, without bounding the relative conjugator:

\[
\mathcal G
=F(x,t,z,q)/\langle\!\langle A,D\rangle\!\rangle.
\]

For a normalized changed row

\[
P_\sigma(c)=A\,cD^\sigma c^{-1},
\]

write \(g\) for the image of c in \(\mathcal G\). The goal is to
construct a nonzero right module vector annihilated by the evaluated
Fox row for every g in the three Result 56 fibers. If the universal
construction fails, the same calculation must isolate the exact
additional group-ring condition rather than infer anything from a
finite word census.

## Universal quotient

The relation D gives

\[
t=zxz^{-1}.
\]

Put \(y=z^{-1}q\), so \(q=zy\). The relation A becomes

\[
yx^3y^{-1}=x^4.
\]

Therefore

\[
\boxed{
\mathcal G
\cong
\langle x,y\mid yx^3y^{-1}=x^4\rangle
*\langle z\rangle
=BS(3,4)*\langle z\rangle.
}
\]

This free-product/HNN normal form is the structural replacement for
bounded Whitehead enumeration.

## Exact evaluated Fox row

Over \(R=\mathbb Z[\mathcal G]\), direct differentiation gives

\[
\begin{aligned}
\nabla A={}&
\bigl(
q(1+x+x^2),
-(1+t+t^2+t^3),
0,
1-t^4
\bigr),\\
\nabla D={}&
\bigl(
t^{-1}z,
-t^{-1},
t^{-1}-1,
0
\bigr).
\end{aligned}
\]

Since A and D vanish in \(\mathcal G\), the derivatives of c cancel:

\[
J_\sigma(g)=\nabla A+\sigma g\nabla D.
\]

If \(P_\sigma(c)\) is primitive, \(J_\sigma(g)\) is right-unimodular.

## Four-state reduction

For a right R-module vector v, put

\[
S=v(1+t+t^2+t^3).
\]

The four equations \(vJ_\sigma(g)=0\) follow from

\[
\boxed{
\begin{aligned}
vt^4&=v,\\
vg&=-\sigma S,\\
vq(1+x+x^2)&=Sz.
\end{aligned}
}
\]

Indeed \(St^{-1}=S\), so the middle equation also gives
\(vg(t^{-1}-1)=0\). These three identities then annihilate the q-, z-,
t-, and x-coordinates respectively.

The main proof problem is therefore the propriety of the cyclic
right-module relations above, uniformly for g in:

\[
\sigma=+1:\ \pi(c)=qz^{-1},
\qquad
\sigma=-1:\ \pi(c)\in\{1,qz^{-1}\}.
\]

## Approaches

### 1. Four-state induced module — recommended

Realize \(v,vt,vt^2,vt^3\) as a t-orbit and map \(vg\) to its orbit
sum. Use the \(BS(3,4)*\langle z\rangle\) normal form to prove that the
third relation does not collapse v. This directly targets the complete
infinite fibers and exposes any exact stabilizer obstruction.

### 2. Finite quotient and regular module

Map \(\mathcal G\) to finite quotients and solve the three linear module
equations in the regular representation. This is useful for discovery
and independent certificates, but a finite collection cannot by itself
prove the arbitrary-g theorem.

### 3. One-dimensional characters

This recovers Results 55--56. It is intentionally not the main route:
the three fibers are precisely where the scalar character equations
fail.

## Verification

The replay will:

- verify the quotient isomorphism in both directions by substitution;
- compute the literal evaluated Fox row in the group ring;
- check the algebraic four-state reduction independently;
- test finite quotients only as discovery/certificates;
- distinguish a proved universal module from bounded experimental
  evidence.

## Boundary

A successful module obstruction proves that no arbitrary A--D product
creates a primitive changed row. It would not by itself close A--W,
W--D, two-edge traffic, AC, or stable AC. A failed universal module is
still useful only if accompanied by an exact counterexample or a
proved residual group-ring condition.
