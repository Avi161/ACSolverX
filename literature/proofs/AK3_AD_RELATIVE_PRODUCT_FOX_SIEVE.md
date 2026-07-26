# Fox exponent sieve for arbitrary A--D relative products

Date: 2026-07-26

Status: **PROVEN** for every relative conjugator outside three exact
abelian exponent classes.

Put

\[
A=qx^3q^{-1}t^{-4},
\qquad
D=t^{-1}zxz^{-1}.
\tag{0.1}
\]

For \(c\in F(x,t,z,q)\) and \(\sigma=\pm1\), consider

\[
P_\sigma(c)=A\,cD^\sigma c^{-1}.
\tag{0.2}
\]

Let \(e_q(c)\) and \(e_z(c)\) be the q- and z-exponent sums of c.
Then

\[
\boxed{
\begin{aligned}
P_\sigma(c)\text{ primitive}
\quad\Longrightarrow\quad&
e_q(c)+e_z(c)=0,\\
(\sigma,e_q(c))\in&
\{(+1,1),(-1,0),(-1,1)\}.
\end{aligned}
}
\tag{0.3}
\]

There is no length or alphabet restriction on c. The three displayed
classes are failures of this Fox character slice, not claimed primitive
families.

## 1. Common-zero obstruction

Let

\[
\Lambda=\mathbb Z[X^{\pm1},T^{\pm1},Z^{\pm1},Q^{\pm1}]
\tag{1.1}
\]

and let

\[
\nabla_{\rm ab} w
=
\left(
\overline{\frac{\partial w}{\partial x}},
\overline{\frac{\partial w}{\partial t}},
\overline{\frac{\partial w}{\partial z}},
\overline{\frac{\partial w}{\partial q}}
\right)
\in\Lambda^4
\tag{1.2}
\]

be the abelianized left Fox row.

### Lemma 1.1

If w is primitive in \(F(x,t,z,q)\), then
\(\nabla_{\rm ab}w\) is unimodular over \(\Lambda\). Consequently no
homomorphism from \(\Lambda\) to a nonzero commutative ring can send all
four entries to zero while sending \(X,T,Z,Q\) to units.

#### Proof

Choose an automorphism having w as the image of one basis element. The
Fox chain rule makes its Fox Jacobian invertible over the integral group
ring, so the row belonging to w has a right Bézout identity. Abelianizing
preserves that identity. A row whose entries generate the unit ideal
cannot become the zero row in a nonzero quotient ring. \(\square\)

The use of an arbitrary nonzero commutative ring, rather than only a
field, will make the finite witness elementary.

## 2. The universal A--D character slice

Evaluate at

\[
X=T=1,
\qquad
Z=s,
\qquad
Q=r,
\tag{2.1}
\]

where r and s are units. Both factors evaluate to one:

\[
\overline A=\overline D=1.
\tag{2.2}
\]

Direct Fox differentiation gives, in the coordinate order
\((x,t,z,q)\),

\[
\nabla A=(3r,-4,0,0),
\qquad
\nabla D=(s,-1,0,0).
\tag{2.3}
\]

For any word c, put \(\lambda=\overline c(1,1,s,r)\). The product and
inverse rules give

\[
\begin{aligned}
\nabla P_\sigma(c)
={}&
\nabla A+\overline A(1-\overline D^\sigma)\nabla c
+\overline A\,\overline c\,\nabla(D^\sigma)\\
={}&
\nabla A+\sigma\lambda\nabla D\\
={}&
(3r+\sigma\lambda s,-4-\sigma\lambda,0,0).
\end{aligned}
\tag{2.4}
\]

This is the key unbounded step: the entire nonabelian Fox derivative of
c disappears because \(\overline D=1\). No bounded conjugator census is
being extrapolated.

Set

\[
r=\frac43s.
\tag{2.5}
\]

Then all four entries in (2.4) vanish exactly when

\[
\lambda=-4\sigma.
\tag{2.6}
\]

Writing

\[
k=e_q(c),
\qquad
n=e_q(c)+e_z(c),
\tag{2.7}
\]

equations (2.1), (2.5) give

\[
\lambda=r^ks^{e_z(c)}
=
\left(\frac43\right)^k s^n.
\tag{2.8}
\]

Thus the common-zero equation is

\[
\left(\frac43\right)^k s^n=-4\sigma.
\tag{2.9}
\]

## 3. Solving the character equation

If \(n\ne0\), work over an algebraic closure of \(\mathbb Q\).
The right side of

\[
s^n=(-4\sigma)(3/4)^k
\tag{3.1}
\]

is nonzero, so it has a nonzero nth root. Equations (2.5) and (3.1)
give a torus common zero. Lemma 1.1 proves \(P_\sigma(c)\)
nonprimitive.

It remains to take \(n=0\). Then (2.9) becomes

\[
(4/3)^k=-4\sigma.
\tag{3.2}
\]

For \(k\ge0\), define

\[
N_{\sigma,k}=4^k+4\sigma3^k.
\tag{3.3}
\]

For \(k=-h<0\), define

\[
N_{\sigma,-h}=3^h+4\sigma4^h.
\tag{3.4}
\]

If \(N_{\sigma,k}\) has a prime divisor \(p\ne2,3\), set

\[
s=1,\qquad r=4/3
\tag{3.5}
\]

in \(\mathbb F_p\). The variables are units and (3.3) or (3.4) is
exactly (3.2) after clearing a unit denominator. Hence (2.4) vanishes
and Lemma 1.1 again proves nonprimitivity.

The prime divisor exists except in three cases. Indeed:

- if \(k=0\), then \(N_{\sigma,0}=1+4\sigma\), giving 5 for
  \(\sigma=+1\) and \(-3\) for \(\sigma=-1\);
- if \(k=1\), then \(N_{\sigma,1}=4+12\sigma\), giving 16 for
  \(\sigma=+1\) and \(-8\) for \(\sigma=-1\);
- if \(k\ge2\), remove the factor 4. The remaining integer
  \(4^{k-1}+\sigma3^k\) is odd and congruent to 1 modulo 3. Its
  absolute value is greater than one. For the only subtle sign,
  \(4^{k-1}-3^k=1\) is ruled out directly at \(k=2,3\) and modulo 8
  for \(k\ge4\). Equality to \(-1\) is impossible modulo 4 when k is
  odd. If \(k=2m\) is even, it would give
  \[
  (3^m-2^{2m-1})(3^m+2^{2m-1})=1,
  \]
  which is impossible;
- if \(k=-h<0\), the integer \(3^h+4\sigma4^h\) is odd, not divisible
  by 3, and has absolute value greater than one.

Therefore some prime \(p\ne2,3\) divides \(N_{\sigma,k}\) except for

\[
(\sigma,k)=(+1,1),\quad(-1,0),\quad(-1,1).
\tag{3.6}
\]

This proves (0.3).

For completeness, (3.6) is also the exact failure set of this slice
over every nonzero commutative target ring. Any common zero has
\(\lambda,r,s\) units. Equation (2.6) makes 4, hence 2, a unit, and the
first-coordinate equation \(3r=4s\) then makes 3 a unit. In the three
residual cases the cleared integers are respectively \(16,-3,-8\).
Each is therefore a unit and cannot vanish in a nonzero ring.

## 4. Orientations and target direction

Any product of oriented conjugacy classes \(A^{\pm1}\) and
\(D^{\pm1}\) can be put into (0.2) by conjugating, cyclically
reordering the two factors, and, if necessary, inverting the entire
word. These operations preserve primitivity.

For example, changing the D-row gives

\[
D^\delta cA^\alpha c^{-1}
\sim
A^\alpha c^{-1}D^\delta c,
\tag{4.1}
\]

where \(\sim\) denotes conjugacy. If \(\alpha=-1\), invert and
cyclically reorder to make the A-orientation positive; this flips the
D-sign. Thus the theorem applies to either target direction after
recording the exponent sums of the normalized relative conjugator.

## 5. Consequence and boundary

Result 50 found no primitive A--D child in the signed-cyclic finite
table. Equation (0.3) now excludes arbitrary relative conjugators in
every exponent class except the three residual lines. In particular,
every conjugator with

\[
e_q(c)+e_z(c)\ne0
\tag{5.1}
\]

is ruled out at once, regardless of its length, cancellations, x/t
content, or commutator content.

The remaining A--D problem is sharply localized: decide the three
classes in (3.6) using another Fox character, a nonabelian quotient, or
an exact relative Whitehead argument. The pair-level Whitehead graph is
not by itself sufficient: carrier separability prevents a uniformly
seam-robust A--D coordinate.

Arbitrary A--W and W--D products, AK(3), AC, and stable AC remain open.

## 6. Independent replay

The verifier
`tests/stable_ac/test_ad_relative_product_fox_sieve.py`:

- differentiates the literal words A, D, and \(P_\sigma(c)\) directly
  over finite commutative quotients;
- checks (2.4) on both signs and cancellation-heavy conjugators;
- exhibits common torus zeros for nonzero-total-exponent examples;
- checks the modular witnesses through \(-24\le k\le24\);
- confirms that the exact residual set is (3.6).

The all-integer conclusion in Section 3 is the elementary parity and
modulo-three proof, not an inference from that finite replay.
