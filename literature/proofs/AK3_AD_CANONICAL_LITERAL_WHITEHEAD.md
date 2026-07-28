# Canonical A--D literals: a Whitehead cut-vertex obstruction

## Statement

Let

\[
F=F(x,t,z,q),\qquad
A=qx^3q^{-1}t^{-4},\qquad
D=t^{-1}zxz^{-1},
\]

and

\[
P_\sigma(c)=A\,cD^\sigma c^{-1},
\qquad \sigma\in\{+1,-1\}.
\tag{1}
\]

Put \(h=qz^{-1}\).  The three canonical literal representatives left
by the projection sieve,

\[
P_+(h),\qquad P_-(h),\qquad P_-(1),
\tag{2}
\]

are nonprimitive in \(F\).

The same conclusion holds for the concrete nonliteral internal lift

\[
c_0=zq^{-1}zxz^{-1}qz^{-1}
\tag{3}
\]

from the negative identity-projection fiber.  These four conclusions
do not classify arbitrary kernel insertions in the three projection
fibers.

Throughout the proof, a capital letter denotes the inverse of the
corresponding lowercase generator.

## 1. The cut-vertex criterion

For a cyclically reduced word \(w\), its Whitehead graph has the
signed basis letters as vertices and, for every cyclic subword
\(ab\), an undirected edge from \(a\) to \(b^{-1}\).

We use the classical cut-vertex lemma in the following form.  If a
cyclic word of length greater than one is primitive and its displayed
letters generate its free-factor support, then its Whitehead graph is
disconnected or has a cut vertex.  Consequently, a connected
Whitehead graph with no cut vertex obstructs primitivity.

It is enough below to draw the graph in the rank-three free factor
containing the transformed word.  Indeed, if an element of a free
factor \(H\leq F\) were primitive in \(F\), Kurosh's subgroup theorem
applied to \(H\leq\langle w\rangle*K\) would make
\(\langle w\rangle\) a free factor of \(H\).  Thus primitivity cannot
first appear after adjoining an unused free generator.

## 2. The three canonical literals

After free reduction, the three words in (2) are

\[
\begin{aligned}
P_+(h)&=\texttt{qxxxQTTTTqZTzxQ},\\
P_-(h)&=\texttt{qxxxQTTTTqXZtzQ},\\
P_-(1)&=\texttt{qxxxQTTTTzXZt}.
\end{aligned}
\tag{4}
\]

Define the following Whitehead automorphisms:

\[
\begin{array}{c|rrrr}
&x&t&z&q\\ \hline
\alpha&q^{-1}xq&t&zq&q\\
\beta&x&x^{-1}tx&x^{-1}z&x^{-1}q\\
\gamma&t^{-1}xt&t&zt&t^{-1}q.
\end{array}
\tag{5}
\]

Each row is a product of elementary Nielsen transformations.  Direct
substitution, free reduction, and cyclic conjugacy give

\[
\begin{array}{c|c|c}
\text{source}&\text{automorphism}&\text{cyclic representative}\\ \hline
P_+(h)&\alpha&
\texttt{TTTTZTzxxxx}\\
P_-(h)&\beta\alpha&
\texttt{TTTTZtzxx}\\
P_-(1)&\gamma\alpha&
\texttt{TTTzXZxxx}.
\end{array}
\tag{6}
\]

Here the rightmost map in the middle column is applied first.
Every word in the last column lies in \(F(x,t,z)\) and uses all three
generators.

For each of the first two rows, the Whitehead graph contains the
spanning cycle

\[
t-x-X-z-T-Z-t.
\tag{7}
\]

For the third row, it contains the spanning cycle

\[
t-T-Z-X-z-x-t.
\tag{8}
\]

A graph containing a cycle through all its vertices is connected and
remains connected after deleting any one vertex.  Hence each graph is
connected with no cut vertex.  The cut-vertex lemma proves that all
three words in (2) are nonprimitive.

## 3. One nonliteral kernel lift

The word (3) satisfies

\[
\rho(c_0)=zy^{-1}xyz^{-1},
\qquad
\pi(c_0)=1,
\tag{9}
\]

for the internal evaluation and projection used in the A--D sieve.
Thus it is the explicit negative identity-fiber example from the
nilpotent no-go theorem, not another literal representative.

After free reduction,

\[
P_-(c_0)
=\texttt{qxxxQTTTTzQzxZqXZtzQzXZqZ}.
\tag{10}
\]

Apply the Whitehead automorphism

\[
\theta(x)=z^{-1}xz,\qquad
\theta(t)=t,\qquad
\theta(z)=z,\qquad
\theta(q)=qz.
\tag{11}
\]

Its cyclic representative is

\[
\texttt{QQxqTxQXqttttqXXX},
\tag{12}
\]

which lies in \(F(q,t,x)\) and uses every generator of that free
factor.  Its Whitehead graph contains the spanning cycle

\[
q-t-Q-x-X-T-q.
\tag{13}
\]

The same cut-vertex argument proves that \(P_-(c_0)\) is
nonprimitive.

## 4. An unbounded kernel-insertion family

The first automorphism in (5) has the useful exact effect

\[
\alpha(A)=R:=x^3t^{-4},\qquad
\alpha(D)=D,\qquad
\alpha(h)=z^{-1}.
\tag{14}
\]

Consequently

\[
\alpha\bigl(P_\sigma(hA^n)\bigr)
=Rz^{-1}R^nD^\sigma R^{-n}z
\qquad(n\in\mathbb Z).
\tag{15}
\]

The case \(n=0\) is already covered by Section 2.  If \(n\ne0\),
the word in (15) is cyclically reduced.  Its Whitehead graph contains
the following edges for both signs of \(n\) and both values of
\(\sigma\):

\[
\{\,T\!-\!Z,\ T\!-\!t,\ T\!-\!z,\ X\!-\!Z,\
X\!-\!x,\ X\!-\!z,\ t\!-\!x,\ x\!-\!z\,\}.
\tag{16}
\]

They are read directly from the blocks
\(R,R^{-1},D,D^{-1}\) and their junctions.  Extra copies of
\(R^{\pm1}\) only repeat edges.  In particular, (16) contains the
spanning cycle

\[
t-T-Z-X-z-x-t.
\tag{17}
\]

The cut-vertex lemma therefore proves

\[
P_\sigma(hA^n)\text{ is nonprimitive}
\qquad
(n\in\mathbb Z,\ \sigma=\pm1).
\tag{18}
\]

There is a further exact gauge which costs no graph calculation.  For
arbitrary \(c\in F\) and \(r,s\in\mathbb Z\),

\[
\begin{aligned}
P_\sigma(A^r cD^s)
&=A^{r+1}cD^\sigma c^{-1}A^{-r}\\
&=A^rP_\sigma(c)A^{-r}.
\end{aligned}
\tag{19}
\]

Hence primitivity is constant on every double orbit

\[
\langle A\rangle c\langle D\rangle.
\tag{20}
\]

Combining (18)--(20) gives the unbounded family

\[
\boxed{
P_\sigma(A^rhA^nD^s)\text{ is nonprimitive}
\quad
(r,n,s\in\mathbb Z,\ \sigma=\pm1).
}
\tag{21}
\]

The same gauge propagates the conclusions for \(c=1\) and \(c=c_0\)
to their double orbits.

## 5. Scope

The first-order \(BS(3,4)\) flow module collapses on the canonical
double cosets, and every nilpotent quotient sees all A--D products as
primitive.  The present obstruction is therefore genuinely different
from both routes.  It decides the unbounded family (21), the two
additional gauge orbits based at \(1\) and \(c_0\), by a full,
untruncated Whitehead criterion.  It does not show that the spanning
cycle survives an arbitrary element of the free evaluation kernel,
so this Whitehead method alone does not close the three complete
canonical residues.  The independent finite-characteristic current in
Section 30 of AK3_AD_INTERNAL_BS34_FLOW_MODULE.md does close every lift
over their canonical internal double cosets.
