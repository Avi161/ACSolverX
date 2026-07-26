# AK(3) minimum-tail central-target design

Date: 2026-07-25

## Objective

Decide the exact Fox coset equation for the central target
\(g=c^{-1}\), the simplest residue left by the binary \(S_4\) sieve.

## HNN kernel

Use

\[
H=(LKL^{-1})K
\]

to rewrite

\[
P=\langle K,LKL^{-1}\rangle,
\qquad
J=\langle P,L\rangle=\langle K,L\rangle.
\]

The folded central-quotient core proves \(J=F(K,L)\). Thus \(J\) is an
HNN extension of \(P\), and the map

\[
z\mapsto\pi_P((1+L)z)
\]

is unsigned edge incidence on its Bass--Serre forest after quotienting
by \((K-1)R\). The leaf argument proves that its exact kernel is
\((K-1)R\).

## Second coset module

The central-target equation reduces to

\[
-(F_0+c^{-1})
\in
(d-K)R+(K-1)R
=
I_{\langle d,K\rangle}.
\]

A second folded core proves \(Q=\langle d,K\rangle\cong F_2\), with
trivial central intersection. Its coset module sends \(F_0+c^{-1}\) to
four distinct basis elements with signs \(+,+,-,-\). The vector is
nonzero, so the target is obstructed. An independent \(S_5\) quotient
reduces the same vector to the difference of two cosets distinguished
by the inverse image of a fixed point.

## Scope

- Exact Fox obstruction for \(g=c^{-1}\).
- No bounded search and no AC graph search.
- Other exact targets over the surviving binary residue remain open.
- The nonabelian kernel equation and AK(3) remain open.
