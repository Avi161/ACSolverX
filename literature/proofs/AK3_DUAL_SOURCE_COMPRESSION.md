# Dual-source triangular compression

Date: 2026-07-24

Status: the dual-source triangular and primitive-pair compression theorems,
and the displayed AK(3) corridor, are **PROVEN**.  The finite-census
observations in Section 5 are **UNVERIFIED**.

## 1. Setup

Let

\[
 P=\langle x,y\mid R,S\rangle
\]

be a balanced presentation of the trivial group.  Introduce fresh
generators \(z,t\) and nonempty freely reduced words
\(w_z,w_t\in F(x,y)\), with defining relators

\[
 D_z=z^{-1}w_z,\qquad D_t=t^{-1}w_t.
\]

For \(I\in F(x,y,z,t)\), let

\[
 \operatorname{sub}_{z,t}(I;w_z,w_t)
\]

denote the freely reduced word obtained by replacing
\(z^{\pm1},t^{\pm1}\) by \(w_z^{\pm1},w_t^{\pm1}\).

If a cyclic word \(I\) contains exactly one \(g^{\pm1}\), rotate it to
\(g^\epsilon q\), where \(q\) is \(g\)-free, and put

\[
 E_g(I)=
 \begin{cases}
 q^{-1},&\epsilon=1,\\
 q,&\epsilon=-1.
 \end{cases}
\]

Thus \(I=1\) is equivalent to \(g=E_g(I)\).

## 2. Simultaneous displayed substitutions

After adjoining \(D_z,D_t\), every displayed copy of
\(w_z^{\pm1}\) in either source relator may be replaced by
\(z^{\pm1}\) using a conjugate of \(D_z^{\pm1}\).  For example,

\[
 u w_z v\longmapsto
 u w_z v\cdot v^{-1}D_z^{-1}v
 =u z v.
\]

The analogous operation uses \(D_t\).  Relator multiplication,
conjugation, and inversion are AC1--AC3 moves, and the defining relator
used in one replacement remains available for every later replacement.
The replacements may therefore be made independently in both \(R\) and
\(S\).

Consequently, if

\[
 \operatorname{sub}_{z,t}(I_R;w_z,w_t)
 \quad\text{and}\quad
 \operatorname{sub}_{z,t}(I_y;w_z,w_t)
\]

are orientations of \(R\) and \(S\), respectively, then

\[
 (R,S,D_z,D_t)
 \sim_{\mathrm{AC1-3}}
 (I_R,I_y,D_z,D_t).
\tag{2.1}
\]

The words are expanded before free reduction.  This displayed-spelling
condition permits cancellations that conceal a defining block in the
reduced source word; it does not authorize an arbitrary equality in the
presented group.

## 3. Dual-source triangular theorem

### Theorem 3.1

Assume:

1. the two expansion identities in Section 2 hold, up to free reduction,
   cyclic rotation, and inversion;
2. \(I_y\) contains exactly one occurrence of \(y^{\pm1}\); and
3. after putting \(e_y=E_y(I_y)\), the reduced word
   \[
   J_x=\overline{I_R[y\mapsto e_y]}
   \]
   contains exactly one occurrence of \(x^{\pm1}\).

Put \(e_x=E_x(J_x)\).  For \(u\in\{z,t\}\), define

\[
 U_u=
 \overline{
   D_u[y\mapsto e_y][x\mapsto e_x]
 }.
\]

The substitutions in this formula are ordered: first \(y\), then \(x\).
Then

\[
 \langle x,y\mid R,S\rangle
 \sim_{\mathrm{st}}
 \langle z,t\mid U_z,U_t\rangle.
\tag{3.1}
\]

### Proof

Adjoin \(z,t\) with defining relators \(D_z,D_t\).  These are two
applications of the substitution-and-removal lemma in reverse, hence
stable AC moves.  Apply the displayed replacements from Section 2 to
obtain (2.1).

Rotate and, if necessary, invert \(I_y\) to \(y^{-1}e_y\).  The
substitution-and-removal lemma deletes \(y\) and \(I_y\), and substitutes
\(y=e_y\) in the other three relators.  The result is

\[
 \left(
   J_x,\,
   \overline{D_z[y\mapsto e_y]},\,
   \overline{D_t[y\mapsto e_y]}
 \right)
\]

over \(F(x,z,t)\).

By hypothesis, \(J_x\) contains one \(x^{\pm1}\).  Rotate and invert it to
\(x^{-1}e_x\).  A second application of the same lemma deletes \(x\) and
\(J_x\), and substitutes \(x=e_x\) in the two surviving defining
relators.  They are exactly \(U_z,U_t\).  Every step is AC1--AC5 or a
proved substitution-and-removal composite.  \(\square\)

### Corollary 3.2

If the endpoint in (3.1) is classically AC-trivial, then the source is
stably AC-trivial.  In particular, an independently certified endpoint
with complete Aut-floor at most \(12\) settles AK(3) by the classical
length theorem and the stable ambient automorphism principle.

### Proposition 3.3 (stable ambient automorphisms in every rank)

Let

\[
 \langle a_1,\ldots,a_n\mid R_1,\ldots,R_n\rangle
\]

be a balanced presentation of the trivial group.  For every
\(\phi\in\operatorname{Aut}(F_n)\), applying \(\phi\) simultaneously to
all relators preserves the stable AC class.

#### Proof

First, a basis letter \(u\) can be exchanged for a fresh letter \(v\).
Adjoin \(v\) with defining relator \(v^{-1}u\), then apply the
substitution-and-removal lemma along the same relator to delete \(u\) and
substitute \(u=v\) everywhere.  This is an honest stable rename.

These exchanges realize the standard Nielsen generators of
\(\operatorname{Aut}(F_n)\):

- a swap of \(a_i,a_j\) uses three exchanges through one fresh letter;
- inversion of \(a_i\) uses two exchanges, the second with defining word
  equal to the inverse of the intermediate letter; and
- to realize \(a_i\mapsto a_i a_j\), adjoin \(v\) with
  \[
  v^{-1}a_i a_j^{-1},
  \]
  remove \(a_i\), which substitutes \(a_i=v a_j\), and exchange \(v\)
  back to the name \(a_i\).

Signed permutations and Nielsen transvections generate
\(\operatorname{Aut}(F_n)\).  Composing these stable exchanges realizes
\(\phi\) on the complete relator tuple.  \(\square\)

### Theorem 3.4 (primitive-pair extension)

Retain the two exact expansion identities of Section 2, but drop the
triangular unique-occurrence assumptions.  Suppose instead that the two
conjugacy classes \(([I_R],[I_y])\) form a primitive pair in
\(F(x,y,z,t)\): some \(\phi\in\operatorname{Aut}(F_4)\) sends them, after
independent conjugation and inversion, to two distinct basis letters.

Apply Proposition 3.3 to the full four-relator tuple and make those two
relators literal basis letters.  Remove their generator--relator pairs.
The two transformed defining relators descend to a balanced rank-two
presentation \(Q_\phi\), and

\[
 P\sim_{\mathrm{st}} Q_\phi.
\tag{3.2}
\]

The Aut(\(F_2\))-orbit of \(Q_\phi\) is independent of the chosen
straightening automorphism.

#### Proof

Equation (2.1) gives

\[
 (I_R,I_y,D_z,D_t)
\]

over \(F_4\).  Apply Proposition 3.3 to the full tuple, then independently
conjugate and invert the first two relators.
After a signed permutation of the basis the tuple has the form

\[
 (a,b,C(a,b,c,d),D(a,b,c,d)).
\]

The substitution-and-removal lemma applied to \(a\), then \(b\), leaves

\[
 \langle c,d\mid C(1,1,c,d),D(1,1,c,d)\rangle.
\]

This proves (3.2).  If \(\phi\) and \(\psi\) are two straightenings, then
\(\psi\phi^{-1}\) preserves the normal closure of the two removed basis
letters.  It therefore induces an automorphism of the free quotient

\[
 F_4/\langle\!\langle a,b\rangle\!\rangle\cong F_2.
\]

The two quotient relator pairs differ by that induced automorphism, up to
relator conjugation and inversion.  Hence their Aut(\(F_2\))-orbits agree.
\(\square\)

Theorem 3.1 is the constructive triangular special case of Theorem 3.4:
its two successive solutions explicitly provide a basis straightening of
the source-template pair.

## 4. Exact AK(3) corridor

Use

\[
 R=x^3y^{-4},\qquad
 S=xyxy^{-1}x^{-1}y^{-1},
\]

and choose

\[
 w_z=x^{-1},\qquad w_t=x^{-1}y.
\]

In string notation,

```text
w_z = X
w_t = Xy
I_R = TZxYYY
I_y = TZtxYX
```

The two literal expansion audits are

\[
\begin{aligned}
 \operatorname{sub}_{z,t}(I_R)
   &=y^{-1}x^3y^{-3},
 \\
 \operatorname{sub}_{z,t}(I_y)
   &\longrightarrow y^{-1}xyxy^{-1}x^{-1}.
\end{aligned}
\]

The first is a cyclic rotation of \(R\), and the second is a cyclic
rotation of \(S\).  The only \(y\)-letter in \(I_y\) is \(y^{-1}\), and
rotating it to the front gives

\[
 e_y=x^{-1}t^{-1}z^{-1}tx
 =\texttt{XTZtx}.
\]

Substitution in \(I_R\) gives

```text
TZxXTztxXTztxXTztx  ->  TZTzzztx
```

which contains exactly one \(x\).  Solving it gives

\[
 e_x=t^{-1}z^{-3}tz t
 =\texttt{TZZZtzt}.
\]

The two surviving defining relators reduce to

```text
ZTZTzzzt
TTZTzzTZtzt
```

and relabeling \(z,t\) as \(x,y\) gives the exact stable equivalence

\[
 \mathrm{AK}(3)
 \sim_{\mathrm{st}}
 \left\langle x,y\ \middle|\
 \texttt{XYXYxxxy},\
 \texttt{YYXYxxYXyxy}
 \right\rangle.
\tag{4.1}
\]

Its complete Whitehead representative is

```text
YYXXXyx | YYXXXYxyX
```

of total length \(16\).  Thus (4.1) proves a new stable corridor, but does
not reach the length-at-most-\(12\) finish line.

## 5. Bounded lead, not yet a certificate

A disposable exact word-equation pass with

- \(1\le |w_z|,|w_t|\le2\);
- freely and cyclically reduced templates of length at most six;
- both \(z,t\) present in each source-compression pair; and
- the two triangular unique-occurrence tests of Theorem 3.1

observed 25,856 triangular witnesses and minimum endpoint Aut-floor \(16\).
These counts and the minimum are **UNVERIFIED** until a separate certificate
regenerates every identity, substitution, output, and Whitehead witness.

A broader disposable pass restricted to visible contiguous source blocks
returned to floor \(13\), but every observed floor-\(13\) endpoint lay in
AK(3)'s known classical class (AK(3) or orbit-2).  That is a lead about a
return mechanism, not a closure theorem.

## 6. Scope

The theorem is not restricted by word or template length.  The observations
in Section 5 are.

The theorem does not cover cyclic dependencies between \(x\) and \(y\),
an extra AC multiplication before either removal, or arbitrary source
equalities not realized by displayed defining-block replacements.  It does
not prove stable triviality or nontriviality of AK(3).
