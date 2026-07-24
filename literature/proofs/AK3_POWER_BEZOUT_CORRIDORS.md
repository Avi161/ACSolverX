# Power-Bézout corridors at the AK(3) compression root

Date: 2026-07-24

Status: the all-integer canonical Euclidean corridors and the even-power
recovery obstruction are **PROVEN**.  The two base Aut(\(F_2\))-floors are
independently machine-checked.  Arbitrary consequence-twisted recovery
words are not classified here.

## 1. The mechanism

At the proved AK(3) compression root, write

\[
 a=x^3,\qquad v=zxz^{-1}.
\]

The three relevant words are

\[
 A=av^{-4},\qquad B=z^{-1}xv,\qquad
 D_k=t^{-1}v^k.
\tag{1.1}
\]

Here \(D_k\) is the defining relator for a new generator \(t=v^k\).
Unlike a free-basis gauge, a power \(v^k\) can recover \(v\) only after the
power relator \(A\) is used.  The coprimality calculation behind this is

\[
 \gcd(4,k)=1.
\]

This note turns that calculation into exact AC relator operations and
classifies the rank-two endpoints of one prescribed Euclidean normal form.

## 2. Euclidean relator reduction

Assume first that \(k>0\) is odd.

### Case \(k=4r+1\)

Start with

\[
 A=av^{-4},\qquad H_0=t^{-1}v^{4r+1}.
\]

For \(0\le i<r\), multiply \(H_i\) by the cyclic rotation
\(v^{-4}a\) of \(A\), then cyclically rotate the product.  The exact
identity is

\[
\begin{aligned}
 (a^it^{-1}v^{4r+1-4i})(v^{-4}a)
 &=
 a^it^{-1}v^{4r+1-4(i+1)}a\\
 &\sim_{\mathrm{cyc}}
 a^{i+1}t^{-1}v^{4r+1-4(i+1)}.
\end{aligned}
\]

After \(r\) AC multiplications,

\[
 H_r=a^rt^{-1}v.
\tag{2.1+}
\]

This relator isolates

\[
 v=ta^{-r}=tx^{-3r}.
\tag{2.2+}
\]

### Case \(k=4r+3\)

The same \(r\) steps first give

\[
 H_r=a^rt^{-1}v^3.
\]

Now multiply \(A=av^{-4}\) by the rotation
\(v^3a^rt^{-1}\) of \(H_r\), and cyclically rotate:

\[
 (av^{-4})(v^3a^rt^{-1})
 =av^{-1}a^rt^{-1}
 \sim_{\mathrm{cyc}}
 a^rt^{-1}av^{-1}.
\]

Thus the transformed first relator is

\[
 L_r=a^rt^{-1}av^{-1},
\tag{2.1-}
\]

which isolates

\[
 v=a^rt^{-1}a=x^{3r}t^{-1}x^3.
\tag{2.2-}
\]

Every operation above is a multiplication by a conjugate of the other
relator followed by AC3 cyclic normalization.  Both relators remain
available at every step.

## 3. Removing the old generator

Use (2.2+) or (2.2-) to replace the displayed \(v\)-block in
\(B=z^{-1}xv\).  The resulting relator contains one \(z^{-1}\), so the
substitution-and-removal lemma deletes \(z\).

### The \(4r+1\) endpoint

Equation (2.2+) gives

\[
 z=xtx^{-3r}.
\]

Substitution in \(H_r\) and \(A\), followed by \(t\mapsto y\), gives

\[
\begin{aligned}
 Q^+_r=\big(&
 x^{3r}y^{-1}xyxy^{-1}x^{-1},\\
 &x^4yx^{-4}y^{-1}x^{-1}
 \big).
\end{aligned}
\tag{3.1+}
\]

The automorphism

\[
 \eta_r(x)=x,\qquad \eta_r(y)=yx^{3r}
\tag{3.2}
\]

sends \(Q^+_r\) literally to \(Q^+_0\).  The further automorphism

\[
 \rho(x)=x,\qquad \rho(y)=x^{-1}y
\]

sends the two relators of \(Q^+_0\), in order, to

\[
 z^{-1}xzxz^{-1},\qquad x^3zx^{-4}z^{-1}
\]

after the harmless relabel \(y\mapsto z\).  Thus \(Q^+_r\) is in the
compression-root orbit of relator conjugacy classes.  Its complete
Aut-floor is \(14\).

### The \(4r+3\) endpoint

Equation (2.2-) gives

\[
 z=x^{3r+1}t^{-1}x^3.
\]

Substitution in \(L_r,H_r\), followed by \(t\mapsto y\), gives

\[
\begin{aligned}
 Q^-_r=\big(&
 x^{3r}y^{-1}x^{3r+4}y^{-1}x^{-1}yx^{-(3r+1)},\\
 &x^{3r}y^{-1}x^{3r+1}y^{-1}x^3yx^{-(3r+1)}
 \big).
\end{aligned}
\tag{3.1-}
\]

The same automorphism \(\eta_r\) in (3.2) sends \(Q^-_r\) literally to

\[
 Q^-_0=
 \big(
 y^{-1}x^4y^{-1}x^{-1}yx^{-1},\
 y^{-1}xy^{-1}x^3yx^{-1}
 \big).
\tag{3.3}
\]

A complete Whitehead calculation gives

\[
 \mu(Q^-_0)=15
\]

with representative

```text
YXXYx | YYYXYxyyyX
```

This is the already observed floor-15 child of the compression wall, not a
new low-length orbit.

## 4. Negative and even powers

If \(k<0\), invert the fresh generator \(t\).  The relation
\(t=v^k\) becomes \(t^{-1}=v^{-k}\), reducing the construction to the
positive exponent \(|k|\).  Hence the canonical construction for every
nonzero odd power lands in one of the two orbits in Section 3, according as

\[
 |k|\equiv1\quad\text{or}\quad3\pmod4.
\]

Even powers cannot recover \(v\), even if arbitrary consequences of both
\(A\) and \(D_k\) are allowed before attempting the recovery.

### Proposition 4.1 (even-power abelian obstruction)

Let

\[
 G_k=
 \langle x,v,t\mid x^3v^{-4},\ t^{-1}v^k\rangle.
\]

If \(k\) is even, then

\[
 v\notin\langle x,t\rangle\le G_k.
\]

#### Proof

The abelianization of \(G_k\) is infinite cyclic and may be parametrized by

\[
 [x]=4s,\qquad [v]=3s,\qquad [t]=3ks.
\]

If \(v=U(x,t)\), and \(U\) has exponent sums \(m,n\) in \(x,t\), then

\[
 3=4m+3kn.
\tag{4.1}
\]

For even \(k\), the right side is even and the left side is odd, a
contradiction.  \(\square\)

## 5. Canonical Euclidean-corridor theorem

### Theorem 5.1

Consider the following prescribed mechanism at the AK(3) compression root:

1. adjoin \(t=v^k\);
2. apply exactly the aligned Euclidean relator products in Section 2 and
   use the resulting isolator (2.1+) or (2.1-) to recover \(v\);
3. replace the displayed \(v\) in \(B=z^{-1}xv\); and
4. remove \(z\) through the resulting unique-occurrence relator.

For every \(k\in\mathbb Z\):

- if \(k\) is even, any recovery of \(v\) from \(A,D_k\) is impossible;
- if \(k\) is odd and \(|k|\equiv1\pmod4\), the endpoint returns to the
  floor-14 compression-root orbit; and
- if \(k\) is odd and \(|k|\equiv3\pmod4\), the endpoint lies in the single
  floor-15 orbit represented by
  `YXXYx | YYYXYxyyyX`.

In particular, no endpoint of this canonical Euclidean family reaches
Aut-floor at most \(12\).

For odd \(k\), the equality \(v=U(x,t)\) in the quotient by \(A,D_k\) does
not make \(U\) a unique free word.  Multiplying the canonical \(U\) by
consequences of those relators can produce different endpoints.  For
example, when \(k=1\),

\[
 R=x^3t^{-4},\qquad R'=t^{-4}x^3
\]

are the compressed power relator and a cyclic rotation.  Besides \(U=t\),
the word

\[
 U'=tR'=t^{-3}x^3
\]

also represents \(v\).  Multiplying the compressed \(B\) by \(R'\), then
restoring \(A\) and removing \(z\), gives

```text
xxxxYYYXXXXyyyX | YxYYYxyyyX
```

of complete Aut-floor \(23\), not \(14\).  Thus the theorem does not cover
arbitrary consequence-twisted recoveries, using \(B\) in the recovery
stage, adding a non-power word in \(v,x\), or taking further AC
multiplications after the displayed endpoint.  It is a normal-form
mechanism theorem, not a stable-AC obstruction.

### Corollary 5.2 (canonical two-sided monomial corridors)

The same canonical Euclidean classification holds after replacing the
defining word \(v^k\) by

\[
 w=x^pv^kx^q
\qquad(p,q,k\in\mathbb Z).
\]

#### Proof

After adjoining \(t=w\), apply the ambient automorphism that fixes \(x,z\)
and sends

\[
 t\longmapsto x^ptx^q.
\]

It carries the defining relator

\[
 t^{-1}x^pv^kx^q
\]

to

\[
 x^{-q}t^{-1}v^kx^q,
\]

which is conjugate to \(t^{-1}v^k\).  The source relators \(A,B\) are
fixed.  Proposition 3.3 of `AK3_DUAL_SOURCE_COMPRESSION.md` realizes this
ambient automorphism stably, and AC3 removes the displayed conjugation.
Theorem 5.1 now applies.  \(\square\)

Thus the prescribed Euclidean corridors for the three-parameter family

\[
 \bigcup_{k\in\mathbb Z}
 \langle x\rangle v^k\langle x\rangle
\]

have only the two stated odd-power outcomes, while even-power recovery
remains impossible.  Consequence-twisted representatives of \(v\) remain
outside this corollary even for these same defining words.

## 6. Independent replay

`tests/stable_ac/test_power_bezout_corridors.py` checks:

1. every literal Euclidean multiplication for both odd residue classes;
2. both substitution-and-removal endpoint formulas;
3. the all-\(r\) shear identities;
4. the exact return of \(Q^+_0\) to the compression root;
5. the complete floor-14 and floor-15 Whitehead representatives;
6. the parity criterion behind (4.1);
7. removal of arbitrary two-sided \(x\)-flanks by the ambient shear; and
8. the \(k=1\) floor-23 counterexample to uniqueness of the recovery word.

The signed finite grid catches word-order and cancellation mistakes.  The
canonical theorem and the even-power obstruction cover every integer
\(k\).
