# Minimum-tail repositioning defeats the evaluated first-cross barrier

Date: 2026-07-25

Status: **PROVEN**. The four previously displayed length-six non-braid
tail representatives fail the first evaluated cross equation for every
remaining conjugator. That failure is not invariant under repositioning
the tail relative to the fixed word \(p=xt\). In the dual sign row
\((+,-,-)\), an explicit repositioned non-braid killer satisfies all
three evaluated equations, has the minimum quotient-\(B\) length six,
and passes the synchronized evaluations \(z=e\) and \(z=p\).

This is not a stable AC history. Its literal \(G\)-valued bridge lift
fails the true free-kernel conjugacy test, and the test with arbitrary
kernel decorations remains open. AK(3) remains open.

## 1. Setup and the exact first-cross test

Put

\[
G=\langle x,t\mid x^3=t^4\rangle,
\qquad
c=x^3=t^4,
\qquad
p=xt,
\tag{1.1}
\]

and

\[
\Gamma=G/\langle c\rangle\cong C_3*C_4.
\tag{1.2}
\]

For a prefix-\(DB\), three-cross \(DBD\) representative, evaluation at
the proposed tail \(z=e\) gives

\[
b=e^{-1}p,
\qquad
d=t^{-1}exe^{-1},
\tag{1.3}
\]

and

\[
\begin{aligned}
K&=d\alpha b^\epsilon\alpha^{-1},\\
C&=b\beta K^\eta\beta^{-1},\\
1&=K\gamma C^\theta\gamma^{-1}.
\end{aligned}
\tag{1.4}
\]

The last equation says

\[
K=\gamma C^{-\theta}\gamma^{-1}.
\tag{1.5}
\]

Consequently the first equation has a solution \(\alpha\) exactly when

\[
\boxed{
d^{-1}K\sim_G b^\epsilon.
}
\tag{1.6}
\]

In both same-orientation rows below, the two sides of (1.6) have weight
\(-2\). The central-quotient conjugacy theorem therefore turns (1.6)
into the exact quotient test

\[
\boxed{
\pi(d^{-1}K)\sim_\Gamma\pi(b^\epsilon).
}
\tag{1.7}
\]

There is no reverse triangle inequality for translation length which
can decide (1.7) from
\(\ell_{\rm cyc}(\bar d)\) and
\(\ell_{\rm cyc}(\overline{C^{-\theta}})\) alone. Arbitrary relative
conjugation can create a long oppositely oriented axis overlap and
cascading cyclic cancellation.

## 2. The four fixed representatives really do fail

Let

\[
C_0=c^{-2}x^2t^3x^2.
\tag{2.1}
\]

The minimum-tail examples from the quotient-\(B\) theorem used

\[
\rho\in\{xt^3,xt^2\}.
\tag{2.2}
\]

For the row \((-,+,+)\), they took

\[
C=C_0,
\qquad
b=C\rho C\rho^{-1}.
\tag{2.3}
\]

For the dual row \((+,-,-)\), they took

\[
C=C_0^{-1},
\qquad
b=C\rho C\rho^{-1}.
\tag{2.4}
\]

In both rows,

\[
S=C^{-\theta}=C_0^{-1},
\qquad
K=\gamma S\gamma^{-1},
\tag{2.5}
\]

and \(\bar S\) has cyclic syllable length \(2\).

The product-of-axes classification in the Bass--Serre tree is finite
when the axes intersect. Rotate the cyclic form of \(\bar d^{-1}\),
rotate the two-syllable cyclic form of \(\bar S\), and insert one of the
six vertex twists

\[
1,\ X,\ X^2,\ T,\ T^2,\ T^3.
\tag{2.6}
\]

The \(k=1\) slice covers shared-edge configurations; nonidentity twists
cover the vertex-stabilizer configurations. Disjoint axes at distance
\(r\ge1\) give

\[
\ell_{\rm cyc}(\bar d^{-1}\gamma\bar S\gamma^{-1})
=
\ell_{\rm cyc}(\bar d)+2+2r,
\tag{2.7}
\]

which is at least \(22\) or \(26\).

The exhaustive intersecting-axis overcensuses are:

\[
\begin{array}{c|c|l}
(\epsilon,\eta,\theta)&\rho&
\text{cyclic length : overtemplate count}\\ \hline
(-,+,+)&xt^3&
12:10,\ 14:20,\ 16:26,\ 18:42,\ 20:118\\
(-,+,+)&xt^2&
14:40,\ 16:23,\ 18:35,\ 20:118\\
(+,-,-)&xt^3&
16:10,\ 18:10,\ 20:59,\ 22:35,\ 24:150\\
(+,-,-)&xt^2&
14:10,\ 16:30,\ 18:10,\ 20:23,\ 22:49,\ 24:142.
\end{array}
\tag{2.8}
\]

The first two rows contain \(18\cdot2\cdot6=216\) overtemplates each; the
last two contain \(22\cdot2\cdot6=264\). Trying every twist at every
rotation intentionally includes redundant and wrong-vertex-factor
templates, so these multiplicities are not counts of distinct geometric
configurations. The list nevertheless covers every intersecting
configuration, and every listed word is realizable. None has length
\(6\), while \(\bar b^\epsilon\) has length \(6\). Thus (1.7) fails for
every \(\gamma\) in each of these four exact representatives.

This conclusion is deliberately representative-specific. Simultaneously
conjugating \(C,\rho,\) and \(b\) does not conjugate

\[
e=pb^{-1}
\tag{2.9}
\]

because \(p\) stays fixed. Therefore it changes \(d\) in a way not
covered by (2.8).

## 3. A repositioned exact solution of all evaluated equations

Put

\[
s=xtx^{-1}
\tag{3.1}
\]

and define

\[
\begin{aligned}
C&=sC_0^{-1}s^{-1},\\
\rho&=s(xt^{-1})s^{-1},\\
\gamma&=xt^{-1}x^{-1},\\
\beta&=\rho\gamma^{-1}=x,\\
b&=C\rho C\rho^{-1},\\
e&=pb^{-1},\\
d&=t^{-1}exe^{-1},\\
K&=\gamma C\gamma^{-1},\\
\alpha&=t.
\end{aligned}
\tag{3.2}
\]

Amalgam normal-form reduction verifies the literal identities in \(G\)

\[
\boxed{
\begin{aligned}
b&=e^{-1}p,\\
K&=d\alpha b\alpha^{-1},\\
C&=b\beta K^{-1}\beta^{-1},\\
1&=K\gamma C^{-1}\gamma^{-1}.
\end{aligned}
}
\tag{3.3}
\]

These are exactly (1.4) for

\[
(\epsilon,\eta,\theta)=(+,-,-).
\tag{3.4}
\]

The weights are

\[
\boxed{
\operatorname{wt}(e)=9,
\quad
\operatorname{wt}(b)=-2,
\quad
\operatorname{wt}(C)=\operatorname{wt}(K)=-1.
}
\tag{3.5}
\]

The survivor \(C\) is a conjugate of \(C_0^{-1}\), so it is a killer.
Its projected cyclic form is

\[
T X^2
\tag{3.6}
\]

up to rotation and has length \(2\). The braid endpoint has projected
cyclic length \(6\), hence

\[
C\not\sim_GD_p^{\pm1}.
\tag{3.7}
\]

Meanwhile

\[
\operatorname{cyc}(\bar b^{-1})
=
T X T^2X^2T^3X^2
=L_1,
\tag{3.8}
\]

one of the two minimum quotient-\(B\) length-six classes.

Thus the first evaluated equation, all six-row weights, the killer
condition, and the minimum quotient-\(B\) class still do not force the
braid class.

## 4. The two evaluations can be synchronized

Let

\[
H=G*\langle z\rangle
\tag{4.1}
\]

and consider

\[
\Phi=(r_e,r_p):H\longrightarrow G\times G,
\qquad
r_a(z)=a.
\tag{4.2}
\]

Recall \(b=e^{-1}p\), and put

\[
N_b=\langle\!\langle b\rangle\!\rangle_G.
\tag{4.3}
\]

### Lemma 4.1

\[
\boxed{
\operatorname{im}\Phi
=
\{(g,gn):g\in G,\ n\in N_b\}.
}
\tag{4.4}
\]

### Proof

The image is generated by the diagonal copy of \(G\) and

\[
(e,p)=(e,e)(1,b).
\tag{4.5}
\]

Conjugating \((1,b)\) by diagonal elements gives
\((1,gbg^{-1})\), so the image contains
\((1,N_b)\). Conversely the set on the right of (4.4) is a subgroup
containing the diagonal and \((1,b)\). This proves equality.
\(\square\)

For the candidate above,

\[
\boxed{
G/N_b\cong C_2.
}
\tag{4.6}
\]

Indeed, in the central quotient the relation \(\bar b^{-1}=L_1=1\)
implies

\[
TXT^2=XTX.
\tag{4.7}
\]

With \(Y=TX\), equation (4.7) gives

\[
X=YT^2Y^{-1}.
\tag{4.8}
\]

The order of \(X\) therefore divides both \(3\) and \(2\), so \(X=1\),
and then \(T^2=1\). Thus
\((G/N_b)/\langle c\rangle\) is cyclic. Since \(c\) is central,
\(G/N_b\) itself is abelian. Its abelianization is
\(\mathbb Z/2\), because \(\operatorname{wt}(b)=-2\). This proves
(4.6), and hence

\[
N_b=\ker(\operatorname{wt}\bmod2).
\tag{4.9}
\]

For the literal evaluated bridges in (3.2),

\[
\gamma\beta=xt^{-1}.
\tag{4.10}
\]

The exact quotient-\(B\) witness is

\[
h_0=xtx^{-1},
\tag{4.11}
\]

because amalgam normal form gives

\[
\boxed{
D_ph_0D_ph_0^{-1}=b^{-1}.
}
\tag{4.12}
\]

Moreover,

\[
(\gamma\beta)^{-1}h_0=t^2x^{-1}
\tag{4.13}
\]

has weight \(2\), so it belongs to \(N_b\) by (4.9). Lemma 4.1 therefore
supplies synchronized bridge lifts. Explicitly, keep \(\gamma\) diagonal
and prescribe

\[
\beta_e=x,
\qquad
\beta_p=xt^2x^{-1}.
\tag{4.14}
\]

Then

\[
\beta_e^{-1}\beta_p=t^2x^{-1}\in N_b,
\qquad
\gamma_p\beta_p=h_0.
\tag{4.15}
\]

Thus the candidate passes not merely the separate evaluated and
quotient-\(B\) tests, but their exact two-evaluation compatibility.

## 5. The remaining equation is a free-kernel equation

Put

\[
q=ze^{-1}
\tag{5.1}
\]

and let

\[
N=\ker r_e.
\tag{5.2}
\]

Then \(N\) is free on the Schreier basis

\[
q_g=gqg^{-1},
\qquad g\in G.
\tag{5.3}
\]

For \(h\in H\), define

\[
\kappa(h)=h\,r_e(h)^{-1}\in N.
\tag{5.4}
\]

Write \({}^g n=gng^{-1}\). The split extension

\[
H=N\rtimes G
\tag{5.5}
\]

has multiplication

\[
(n,g)(m,h)=(n\,{}^gm,gh).
\tag{5.6}
\]

For the original cross relators

\[
B=z^{-1}p,
\qquad
D=t^{-1}zxz^{-1},
\tag{5.7}
\]

their kernel components are

\[
\begin{aligned}
J&=\kappa(B)=z^{-1}e=q_{e^{-1}}^{-1},\\
\Delta&=\kappa(D)=q_{t^{-1}}q_d^{-1}.
\end{aligned}
\tag{5.8}
\]

Use the canonical row-\((+,-,-)\) history

\[
\begin{aligned}
D_1&=D\,uBu^{-1},\\
B_1&=B\,vD_1^{-1}v^{-1},\\
D_2&=D_1\,wB_1^{-1}w^{-1}.
\end{aligned}
\tag{5.9}
\]

Every lift of the evaluated bridges is uniquely

\[
u=U\alpha,
\qquad
v=V\beta,
\qquad
w=W\gamma,
\qquad
U,V,W\in N.
\tag{5.10}
\]

Using the exact evaluated identities (3.3), write

\[
D_1=(n_1,K),
\qquad
B_1=(n_2,C),
\qquad
D_2=(n_3,1).
\tag{5.11}
\]

Repeated use of (5.6) gives the exact kernel equations

\[
\boxed{
\begin{aligned}
n_1={}&
\Delta\,
{}^dU\,
{}^{d\alpha}J\,
{}^K(U^{-1}),\\
n_2={}&
J\,
{}^bV\,
{}^{b\beta K^{-1}}(n_1^{-1})\,
{}^C(V^{-1}),\\
n_3={}&
n_1\,
{}^KW\,
{}^{K\gamma C^{-1}}(n_2^{-1})\,
W^{-1}.
\end{aligned}
}
\tag{5.12}
\]

The final target is a legal isolator exactly when

\[
\boxed{
n_3
\text{ is \(N\)-conjugate to }
{}^gJ=q_{ge^{-1}}^{-1}
\text{ for some }g\in G.
}
\tag{5.13}
\]

Equivalently, cyclic reduction of \(n_3\) in the free basis (5.3) must
have length \(1\) and negative sign.

The literal \(G\)-valued bridges set

\[
U=V=W=1.
\tag{5.14}
\]

For that single point, independent Schreier rewriting gives

\[
\ell_{\rm cyc,N}(n_3)=7,
\tag{5.15}
\]

equivalently free-product syllable length \(14\) in \(H\), whereas
\(J\) has kernel length \(1\). Hence the literal lift is not legal.

Equation (5.12), not (5.15), is the remaining problem. Its first exact
linearization is still nontrivial. Identify

\[
N_{\rm ab}\cong\mathbb Z[G],
\qquad
[q_g]\longmapsto g.
\tag{5.16}
\]

Put

\[
a=exe^{-1},
\qquad
r=\alpha b\alpha^{-1},
\qquad
s=\beta K^{-1}\beta^{-1},
\tag{5.17}
\]

so that

\[
d=t^{-1}a,
\qquad
K=dr,
\qquad
C=bs.
\tag{5.18}
\]

The kernel constants map to

\[
\mathbf j=-e^{-1},
\qquad
\boldsymbol\Delta=t^{-1}(1-a).
\tag{5.19}
\]

For arbitrary
\(\mathbf u,\mathbf v,\mathbf w\in\mathbb Z[G]\), abelianization of
(5.12) gives

\[
\boxed{
\begin{aligned}
\mathbf X={}&
\boldsymbol\Delta
+d(1-r)\mathbf u
+d\alpha\mathbf j,\\
\mathbf Y={}&
\mathbf j
+b(1-s)\mathbf v
-b\beta K^{-1}\mathbf X,\\
\boldsymbol\Xi={}&
\mathbf X
+(K-1)\mathbf w
-\gamma\mathbf Y.
\end{aligned}
}
\tag{5.20}
\]

A legal lift must satisfy

\[
\boxed{
\boldsymbol\Xi=-g
\quad
\text{for some }g\in G,
}
\tag{5.21}
\]

because the target is one negative Schreier basis monomial.
Here the monomial from (5.13) is initially \(-ge^{-1}\); equation
(5.21) simply reindexes \(ge^{-1}\) as \(g\), which still ranges over
all of \(G\).

Only the scalar augmentation of (5.20) is automatic:

\[
\operatorname{aug}(\boldsymbol\Xi)=-1.
\tag{5.22}
\]

Thus scalar augmentation gives no obstruction, but the full
\(\mathbb Z[G]\) Fox equation (5.20)--(5.21) remains unchecked. Mapping
it to a finite quotient \(G\to Q\) and then to a finite group algebra
\(\mathbb F_p[Q]\) gives a rigorous finite-dimensional sieve: failure
there proves nonliftability, while success is only necessary. If the full
linear equation survives, the nonabelian equation (5.12) still remains.

## 6. Scope

The result proves:

1. the four old literal minimum-tail representatives fail the first
   equation for every \(\gamma\);
2. that failure does not extend to their repositioned family;
3. a non-braid minimum-tail candidate satisfies all three evaluated
   equations and the synchronized quotient-\(B\) shadow; and
4. its general liftability is exactly the three-variable free-kernel
   equation (5.12).

It does not produce a legal stable history, an AC obstruction, or an
AC-trivialization. The exact normal forms, finite axis overcensuses,
candidate identities, synchronized bridge arithmetic, quotient-\(B\)
identity, and literal Schreier length are replayed by
`tests/stable_ac/test_prefix_db_evaluated_countermodel.py`.
The normal-closure membership used for synchronization is certified by
the proof of (4.6), not by weight arithmetic alone.

The axis-product classification used in Section 2 is the standard
product formula for hyperbolic isometries of a tree; see Proposition 4.1
of I. Kapovich, G. Levitt, P. Schupp, and V. Shpilrain,
*Translation equivalence in free groups*,
arXiv:math/0409284.

AK(3) remains open.
