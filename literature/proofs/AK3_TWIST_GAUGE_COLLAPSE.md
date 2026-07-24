# Two-sided twist gauge collapse at the AK(3) compression root

Date: 2026-07-24

Status: the all-integer signed two-parameter stable equivalence and its
Aut(\(F_2\))-orbit conclusion are **PROVEN**.  The proof is symbolic; no
bounded search is used.

## 1. Compression root

The proved hidden rank-three corridor gives

\[
 \mathrm{AK}(3)\sim_{\mathrm{st}}P_0,
\]

where

\[
 P_0=
 \left\langle x,z\ \middle|\
 A=x^3zx^{-4}z^{-1},\
 B=z^{-1}xzxz^{-1}
 \right\rangle.
\tag{1.1}
\]

Put

\[
 v=zxz^{-1}.
\]

Then

\[
 A=x^3v^{-4},\qquad B=z^{-1}xv.
\tag{1.2}
\]

Uppercase letters denote inverses in the exact word spellings below.

## 2. The two-sided signed twist family

Fix arbitrary \(p,q\in\mathbb Z\) and
\(\epsilon\in\{+1,-1\}\).  Adjoin a fresh generator \(t\) with

\[
 t=x^pv^\epsilon x^q.
\tag{2.1}
\]

This is the substitution-and-removal lemma used in reverse, not a bare
AC4 move: the new defining relator is \(t^{-1}x^pv^\epsilon x^q\).
It is legitimate because \(P_0\) is a presentation of the trivial group.

### 2.1 Positive orientation

For \(\epsilon=+1\), the defining relator is

\[
 t=x^p v x^q=x^pzxz^{-1}x^q
\]

\[
 D^+_{p,q}=t^{-1}x^pzxz^{-1}x^q.
\]

The defining relation gives

\[
 v=x^{-p}tx^{-q},
 \qquad
 v^{-1}=x^qt^{-1}x^p.
\]

Using conjugates of \((D^+_{p,q})^{\pm1}\) to replace the displayed copies in
(1.2), the two source relators become

\[
\begin{aligned}
 C^+_{p,q}
   &=x^3(x^qt^{-1}x^p)^4,\\
 I^+_{p,q}
   &=z^{-1}x^{1-p}tx^{-q}.
\end{aligned}
\tag{2.2+}
\]

The second word contains exactly one \(z^{\pm1}\), and its equation
isolates

\[
 z=x^{1-p}tx^{-q}.
\tag{2.3}
\]

Remove \(z\) and \(I^+_{p,q}\) by the substitution-and-removal lemma.  Since

\[
 z^{-1}=x^qt^{-1}x^{p-1},
\]

the defining relator descends to

\[
\begin{aligned}
 E^+_{p,q}
 &=t^{-1}x^p
   (x^{1-p}tx^{-q})x
   (x^qt^{-1}x^{p-1})x^q\\
 &=t^{-1}xtxt^{-1}x^{p+q-1}.
\end{aligned}
\tag{2.4+}
\]

Thus every pair of integers gives the exact stable corridor

\[
 P_0\sim_{\mathrm{st}}
 Q^+_{p,q}:=
 \left\langle x,t\ \middle|\
 C^+_{p,q},E^+_{p,q}
 \right\rangle.
\tag{2.5+}
\]

### 2.2 Negative orientation

For \(\epsilon=-1\), use

\[
 D^-_{p,q}=t^{-1}x^pzx^{-1}z^{-1}x^q.
\]

Now \(v^{-1}=x^{-p}tx^{-q}\), so the source relators compress to

\[
\begin{aligned}
 C^-_{p,q}
   &=x^3(x^{-p}tx^{-q})^4,\\
 I^-_{p,q}
   &=z^{-1}x^{q+1}t^{-1}x^p.
\end{aligned}
\tag{2.2-}
\]

The second equation isolates

\[
 z=x^{q+1}t^{-1}x^p.
\tag{2.3-}
\]

Substitution in \(D^-_{p,q}\) and free reduction give

\[
 E^-_{p,q}
 =t^{-1}x^{p+q+1}t^{-1}x^{-1}tx^{-1}.
\tag{2.4-}
\]

Therefore

\[
 P_0\sim_{\mathrm{st}}
 Q^-_{p,q}:=
 \left\langle x,t\ \middle|\
 C^-_{p,q},E^-_{p,q}
 \right\rangle.
\tag{2.5-}
\]

## 3. Gauge-collapse theorem

### Theorem 3.1

For every \(p,q\in\mathbb Z\) and
\(\epsilon\in\{+1,-1\}\), the presentation \(Q^\epsilon_{p,q}\) is carried
back to AK(3) by an ambient free-group automorphism, independent relator
conjugation, and, in the negative case, relator inversion.  Consequently,
the entire signed two-parameter family is a stable self-loop and has the
same complete Aut(\(F_2\))-floor as AK(3), namely \(13\).

### Proof

Relabel \(t\) as \(y\).  In the positive case let

\[
 \phi^+_{p,q}(x)=x,\qquad
 \phi^+_{p,q}(y)=x^pyx^q.
\tag{3.1}
\]

This is an automorphism: its inverse fixes \(x\) and sends
\(y\mapsto x^{-p}yx^{-q}\).

Because

\[
 \phi^+_{p,q}(y^{-1})=x^{-q}y^{-1}x^{-p},
\]

the first relator satisfies the literal identity

\[
 \phi^+_{p,q}(C^+_{p,q})
 =x^3y^{-4}.
\tag{3.2}
\]

For the second relator, put

\[
 E_0=y^{-1}xyxy^{-1}x^{-1}.
\]

Direct free reduction gives

\[
\begin{aligned}
 \phi^+_{p,q}(E^+_{p,q})
 &=x^{-q}y^{-1}xyxy^{-1}x^{q-1}\\
 &=x^{-q}E_0x^q.
\end{aligned}
\tag{3.3}
\]

The word \(E_0\) is conjugate to the second AK(3) relator \(S\), since

\[
 E_0=y^{-1}Sy.
\]

For the negative family use

\[
 \phi^-_{p,q}(x)=x,\qquad
 \phi^-_{p,q}(y)=x^py^{-1}x^q.
\tag{3.4}
\]

This is again an automorphism.  Direct free reduction gives

\[
\begin{aligned}
 \phi^-_{p,q}(C^-_{p,q})&=x^3y^{-4},\\
 \phi^-_{p,q}(E^-_{p,q})&=x^{-q}S^{-1}x^q.
\end{aligned}
\tag{3.5}
\]

Hence (3.2)--(3.5), AC2--AC3 moves, and the stable
ambient-automorphism theorem identify both \(Q^+_{p,q}\) and
\(Q^-_{p,q}\) with AK(3).

The independently complete Whitehead calculation gives Aut-floor \(13\)
for AK(3).  Since every \(Q^\epsilon_{p,q}\) lies in the same
Aut(\(F_2\))-orbit of the pair of relator conjugacy classes, its floor is
also \(13\).  \(\square\)

## 4. Consequence for proof search

The theorem removes an infinite false degree of freedom.  Once the
one-stabilization corridor has exposed

\[
 v=zxz^{-1},
\]

replacing the new generator by any element of either double coset

\[
 \langle x\rangle\,v^{\pm1}\,\langle x\rangle
\]

cannot escape the AK(3) orbit of relator conjugacy classes under this exact
compress-and-remove corridor.  The sign and two integer parameters are only
a basis gauge.

This is not a stable-AC obstruction: stabilizing words outside that double
coset pair, multiple compressed blocks, and additional relator
multiplications remain available.  In particular, the theorem does not
forbid using the same defining word and then taking extra AC moves.  It
shows only that the bare compression-and-removal family obtained by
lengthening \(v^{\pm1}\) with arbitrary left and right powers of \(x\) is
redundant, without imposing a length bound.

## 5. Independent replay

`tests/stable_ac/test_twist_gauge_collapse.py` checks, for a signed grid of
\((p,q)\)-values:

1. both literal template expansions in (2.2+) and (2.2-);
2. both unique-occurrence solutions;
3. both surviving defining relators;
4. the explicit automorphisms (3.1) and (3.4);
5. the return to both AK(3) conjugacy classes; and
6. the complete Aut representative
   `YXYxyx | YYYYxxx` of total length \(13\).

The finite replay catches transcription errors.  The theorem itself covers
both signs and all \(p,q\in\mathbb Z\) through the displayed identities.
