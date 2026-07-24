# The exact Neuwirth genus of the orbit-2 presentation

## Statement and conventions

Consider the exact cyclic presentation

\[
P_{\mathrm{orb2}}
  =\langle x,y\mid \mathtt{YYXXyx},\mathtt{YYYxyXX}\rangle .
\]

This note uses the occurrence dictionary, right-to-left permutation
composition, and reversed \(B\)-paired compatibility convention of
[`AK3_NEUWIRTH.md`](AK3_NEUWIRTH.md). In particular, the specified words are
not reduced or otherwise changed.

For an occurrence \(o\), write \(d_o\) and \(h_o\) for its departure and
arrival endpoints. If \(o\) is an occurrence of \(g\), put \(o^+=d_o\); if it
is an occurrence of \(g^{-1}\), put \(o^+=h_o\). In either case put

\[
o^-=B(o^+).
\]

Thus the superscripts \(+\) and \(-\) name the positive and negative ends of
the **unsigned** generator. They do not record the exponent of the letter.
For example, \(Y_{11}^+=h_{Y_{11}}\) and
\(Y_{11}^-=d_{Y_{11}}\), whereas \(y_{15}^+=d_{y_{15}}\) and
\(y_{15}^-=h_{y_{15}}\).

Number the occurrences by relator and position:

\[
\begin{aligned}
r_1&=
Y_{11}Y_{12}X_{13}X_{14}y_{15}x_{16},\\
r_2&=
Y_{21}Y_{22}Y_{23}x_{24}y_{25}X_{26}X_{27}.
\end{aligned}
\]

There are six unsigned \(x\)-occurrences and seven unsigned
\(y\)-occurrences. Hence

\[
|A|=13,\qquad |C|=4.
\]

The underlying link graph is connected, so \(L(C)=1\) for every compatible
order. The definition in `AK3_NEUWIRTH.md` therefore becomes

\[
\gamma_N(P_{\mathrm{orb2}})
  =\min_C\frac{13-4+2-|AC|}{2}
  =\min_C\frac{11-|AC|}{2}. \tag{1}
\]

We will prove:

**Theorem.**

\[
\boxed{\gamma_N(P_{\mathrm{orb2}})=1.}
\]

## The thirteen corners and the \(K_4\) support

For every cyclic corner, \(A\) pairs the arrival endpoint of its first
occurrence with the departure endpoint of its second occurrence. The complete
corner list is:

| Relator corner | \(A\)-pair |
|---|---|
| \(Y_{11}Y_{12}\) | \((Y_{11}^+\;Y_{12}^-)\) |
| \(Y_{12}X_{13}\) | \((Y_{12}^+\;X_{13}^-)\) |
| \(X_{13}X_{14}\) | \((X_{13}^+\;X_{14}^-)\) |
| \(X_{14}y_{15}\) | \((X_{14}^+\;y_{15}^+)\) |
| \(y_{15}x_{16}\) | \((y_{15}^-\;x_{16}^+)\) |
| \(x_{16}Y_{11}\) | \((x_{16}^-\;Y_{11}^-)\) |
| \(Y_{21}Y_{22}\) | \((Y_{21}^+\;Y_{22}^-)\) |
| \(Y_{22}Y_{23}\) | \((Y_{22}^+\;Y_{23}^-)\) |
| \(Y_{23}x_{24}\) | \((Y_{23}^+\;x_{24}^+)\) |
| \(x_{24}y_{25}\) | \((x_{24}^-\;y_{25}^+)\) |
| \(y_{25}X_{26}\) | \((y_{25}^-\;X_{26}^-)\) |
| \(X_{26}X_{27}\) | \((X_{26}^+\;X_{27}^-)\) |
| \(X_{27}Y_{21}\) | \((X_{27}^+\;Y_{21}^-)\) |

Grouping these \(A\)-edges by their two link vertices gives:

| Vertex pair | Parallel \(A\)-edges | Multiplicity |
|---|---|---:|
| \(y^-x^-\) | \(Y_{11}^-x_{16}^-\), \(y_{25}^-X_{26}^-\) | 2 |
| \(y^+y^-\) | \(Y_{11}^+Y_{12}^-\), \(Y_{21}^+Y_{22}^-\), \(Y_{22}^+Y_{23}^-\) | 3 |
| \(y^+x^-\) | \(Y_{12}^+X_{13}^-\), \(y_{25}^+x_{24}^-\) | 2 |
| \(x^+x^-\) | \(X_{13}^+X_{14}^-\), \(X_{26}^+X_{27}^-\) | 2 |
| \(x^+y^+\) | \(X_{14}^+y_{15}^+\), \(x_{24}^+Y_{23}^+\) | 2 |
| \(y^-x^+\) | \(y_{15}^-x_{16}^+\), \(Y_{21}^-X_{27}^+\) | 2 |

Every pair among the four vertices

\[
x^+,\quad x^-,\quad y^+,\quad y^-
\]

occurs. After parallel edges are suppressed, the support is \(K_4\).
In particular, the support is connected and planar. The obstruction below is
not nonplanarity of the abstract link graph: it is incompatibility between a
spherical rotation and the synchronized, reversed orders required at
opposite generator ends.

## A spherical rotation would force seven digons

Suppose, for contradiction, that a compatible \(C\) gives a sphere. The
associated ribbon graph then has

\[
V=|C|=4,\qquad E=|A|=13,\qquad F=2-V+E=11.
\]

It has no loop edges, so it has no monogon faces. Let \(d\) be its number of
digon faces. Every other face has length at least three, while every dart
occurs in exactly one face boundary. Therefore

\[
26=2E
  \ge 2d+3(11-d)
  =33-d,
\]

and hence

\[
d\ge7. \tag{2}
\]

On the other hand, a parallel class of \(m\) edges contributes at most
\(m-1\) digon faces. Indeed, each endpoint vertex has incident edges outside
that parallel class. Consequently, among the \(m\) cyclic gaps between
successive class halfedges, at least one contains an outside halfedge. A
digon requires an empty gap between its two class halfedges at both endpoint
vertices, with the directed orders opposite. Thus at most \(m-1\) gaps can
support digons.

There are five classes of multiplicity two and one class of multiplicity
three. Hence

\[
d\le 5(2-1)+(3-1)=7. \tag{3}
\]

Equations (2) and (3) force equality everywhere. Every doubled class must
bound one digon, and the tripled \(y^+y^-\) class must bound two. In
particular:

- the two halfedges of every doubled class are adjacent at both endpoints;
- all three halfedges of the \(y^+y^-\) class occur consecutively at both
  endpoints.

## Translating every forced adjacency through \(B\)

Let \(O_x\) and \(O_y\) denote the positive-end cyclic orders of the
occurrence labels. If two negative endpoints \(o^-\) and \(o'^-\) are
adjacent, then \(B(o^-)=o^+\) and \(B(o'^-)=o'^+\) are adjacent in the
positive order. Their direction is reversed, but undirected cyclic adjacency
is unchanged. We write \(o\sim o'\) for this adjacency.

Saturation of the five doubled bundles gives all of the following.

1. From the \(y^-x^-\) edges
   \[
   Y_{11}^-x_{16}^-,
   \qquad
   y_{25}^-X_{26}^-,
   \]
   adjacency at \(y^-\) is transported by \(B\) to
   \[
   Y_{11}\sim y_{25}\quad\text{in }O_y,
   \]
   and adjacency at \(x^-\) is transported to
   \[
   x_{16}\sim X_{26}\quad\text{in }O_x.
   \]

2. From the \(y^+x^-\) edges
   \[
   Y_{12}^+X_{13}^-,
   \qquad
   y_{25}^+x_{24}^-,
   \]
   the positive \(y\)-end gives
   \[
   Y_{12}\sim y_{25}\quad\text{in }O_y,
   \]
   while \(B(X_{13}^-)=X_{13}^+\) and
   \(B(x_{24}^-)=x_{24}^+\) give
   \[
   X_{13}\sim x_{24}\quad\text{in }O_x.
   \]

3. From the \(x^+x^-\) edges
   \[
   X_{13}^+X_{14}^-,
   \qquad
   X_{26}^+X_{27}^-,
   \]
   the positive end gives
   \[
   X_{13}\sim X_{26}\quad\text{in }O_x,
   \]
   and applying \(B\) at the negative end gives
   \[
   X_{14}\sim X_{27}\quad\text{in }O_x.
   \]

4. From the \(x^+y^+\) edges
   \[
   X_{14}^+y_{15}^+,
   \qquad
   x_{24}^+Y_{23}^+,
   \]
   both adjacencies are already at positive ends:
   \[
   X_{14}\sim x_{24}\quad\text{in }O_x,
   \qquad
   y_{15}\sim Y_{23}\quad\text{in }O_y.
   \]

5. From the \(y^-x^+\) edges
   \[
   y_{15}^-x_{16}^+,
   \qquad
   Y_{21}^-X_{27}^+,
   \]
   applying \(B\) at \(y^-\) gives
   \[
   y_{15}\sim Y_{21}\quad\text{in }O_y,
   \]
   and the positive \(x\)-end gives
   \[
   x_{16}\sim X_{27}\quad\text{in }O_x.
   \]

For completeness, the six forced \(x\)-adjacencies form the cyclic hexagon

\[
X_{13}-x_{24}-X_{14}-X_{27}-x_{16}-X_{26}-X_{13}.
\]

The contradiction, however, already occurs in \(O_y\).

The tripled \(y^+y^-\) bundle has positive-end halfedges belonging to

\[
Y_{11},\quad Y_{21},\quad Y_{22}
\]

and negative-end halfedges belonging to

\[
Y_{12},\quad Y_{22},\quad Y_{23}.
\]

Two digons in this three-edge bundle force the corresponding triples to be
consecutive blocks. Transporting the negative block through \(B\), the
positive occurrence order \(O_y\) must therefore contain both blocks

\[
\{Y_{11},Y_{21},Y_{22}\},
\qquad
\{Y_{12},Y_{22},Y_{23}\}. \tag{4}
\]

The doubled bundles already force

\[
Y_{11}\sim y_{25}\sim Y_{12},
\qquad
Y_{23}\sim y_{15}\sim Y_{21}. \tag{5}
\]

In the first block of (4), \(Y_{11}\) cannot be the middle element: one of
its two cyclic neighbours is the outside occurrence \(y_{25}\). Similarly,
\(Y_{21}\) cannot be the middle element because one of its neighbours is the
outside occurrence \(y_{15}\). Hence \(Y_{22}\) is the middle element and

\[
Y_{22}\sim Y_{11},
\qquad
Y_{22}\sim Y_{21}. \tag{6}
\]

Apply the same argument to the second block. The outside neighbours in (5)
make \(Y_{12}\) and \(Y_{23}\) the two endpoints, so

\[
Y_{22}\sim Y_{12},
\qquad
Y_{22}\sim Y_{23}. \tag{7}
\]

Equations (6) and (7) give \(Y_{22}\) four distinct cyclic neighbours:

\[
Y_{11},\quad Y_{21},\quad Y_{12},\quad Y_{23}.
\]

An element of a cyclic order has exactly two neighbours. This contradiction
proves that no synchronized compatible spherical rotation exists. By (1),

\[
\gamma_N(P_{\mathrm{orb2}})\ge1. \tag{8}
\]

## An explicit genus-one compatible rotation

Choose the positive-end occurrence orders

\[
\begin{aligned}
O_x&=(X_{13},X_{14},x_{24},x_{16},X_{26},X_{27}),\\
O_y&=(Y_{11},Y_{12},Y_{21},Y_{22},Y_{23},y_{15},y_{25}).
\end{aligned} \tag{9}
\]

Written as endpoint cycles, these are

\[
\begin{aligned}
C_x^+
  &=(X_{13}^+\;X_{14}^+\;x_{24}^+\;x_{16}^+\;X_{26}^+\;X_{27}^+),\\
C_y^+
  &=(Y_{11}^+\;Y_{12}^+\;Y_{21}^+\;Y_{22}^+\;Y_{23}^+\;y_{15}^+\;y_{25}^+).
\end{aligned}
\]

The negative cycles are obtained by reversing first and then applying \(B\)
to every endpoint. For \(x\),

\[
\begin{aligned}
&(X_{27}^+,X_{26}^+,x_{16}^+,x_{24}^+,X_{14}^+,X_{13}^+)\\
&\quad\xrightarrow{\;B\;}
(X_{27}^-,X_{26}^-,x_{16}^-,x_{24}^-,X_{14}^-,X_{13}^-),
\end{aligned}
\]

so

\[
C_x^-=
(X_{27}^-\;X_{26}^-\;x_{16}^-\;x_{24}^-\;X_{14}^-\;X_{13}^-).
\]

For \(y\),

\[
\begin{aligned}
&(y_{25}^+,y_{15}^+,Y_{23}^+,Y_{22}^+,Y_{21}^+,Y_{12}^+,Y_{11}^+)\\
&\quad\xrightarrow{\;B\;}
(y_{25}^-,y_{15}^-,Y_{23}^-,Y_{22}^-,Y_{21}^-,Y_{12}^-,Y_{11}^-),
\end{aligned}
\]

so

\[
C_y^-=
(y_{25}^-\;y_{15}^-\;Y_{23}^-\;Y_{22}^-\;Y_{21}^-\;Y_{12}^-\;Y_{11}^-).
\]

Let

\[
C=C_x^+C_x^-C_y^+C_y^-.
\]

Using the thirteen \(A\)-pairs in the corner table and tracing
\(AC(e)=A(C(e))\), the face cycles are:

\[
\begin{aligned}
&(Y_{11}^-\;X_{26}^-),\\
&(Y_{11}^+\;X_{13}^-\;X_{26}^+\;Y_{21}^-),\\
&(Y_{12}^-\;x_{16}^-\;y_{25}^+),\\
&(Y_{12}^+\;Y_{22}^-\;X_{27}^+\;X_{14}^-),\\
&(X_{13}^+\;y_{15}^+\;x_{24}^-),\\
&(X_{14}^+\;Y_{23}^+),\\
&(y_{15}^-\;Y_{22}^+\;x_{24}^+),\\
&(x_{16}^+\;X_{27}^-\;y_{25}^-),\\
&(Y_{21}^+\;Y_{23}^-).
\end{aligned} \tag{10}
\]

For example, the first cycle replays directly:

\[
\begin{aligned}
AC(Y_{11}^-)
  &=A(y_{25}^-)=X_{26}^-,\\
AC(X_{26}^-)
  &=A(x_{16}^-)=Y_{11}^-.
\end{aligned}
\]

The face lengths in the order displayed in (10) are

\[
2,\ 4,\ 3,\ 4,\ 3,\ 2,\ 3,\ 3,\ 2.
\]

They sum to \(26=2E\), and there are nine faces. Therefore

\[
\chi(\Sigma_C)=V-E+F=4-13+9=0.
\]

The support is connected and the rotation surface is orientable by
construction, so \(\Sigma_C\) is a torus. Equivalently,

\[
\frac{|A|-|C|+2-|AC|}{2}
  =\frac{13-4+2-9}{2}
  =1.
\]

Together with (8), this proves

\[
\boxed{\gamma_N(P_{\mathrm{orb2}})=1.}
\]

## AC non-invariance

The value \(\gamma_N\) is not an Andrews--Curtis invariant. A small exact
counterexample is

\[
\langle x,y\mid \mathtt{yxx},\mathtt{y}\rangle
\longmapsto
\langle x,y\mid \mathtt{yxxy},\mathtt{y}\rangle,
\]

where the displayed step is the elementary relator multiplication
\(r_1\mapsto r_1r_2\).

For the first presentation, label the occurrences

\[
y_{11}x_{12}x_{13}\mid y_{21}.
\]

The positive orders are uniquely
\((x_{12},x_{13})\) and \((y_{11},y_{21})\), up to rotating the
cycles. Direct \(AC\)-tracing gives

\[
(y_{11}^+\;y_{21}^-\;x_{12}^+\;x_{12}^-),
\qquad
(y_{11}^-\;y_{21}^+\;x_{13}^-\;x_{13}^+).
\]

Thus there are two faces and

\[
\gamma_N=\frac{4-4+2-2}{2}=0.
\]

For the second presentation, label the occurrences

\[
y_{11}x_{12}x_{13}y_{14}\mid y_{21}.
\]

The two positive \(y\)-orders, with \(y_{11}\) fixed first, are
\((y_{11},y_{14},y_{21})\) and
\((y_{11},y_{21},y_{14})\). They give respectively the single face cycles

\[
\begin{aligned}
&(y_{11}^+\;x_{13}^-\;x_{13}^+\;y_{11}^-\;y_{21}^+\;
  y_{14}^-\;x_{12}^+\;x_{12}^-\;y_{14}^+\;y_{21}^-),\\
&(y_{11}^+\;y_{21}^-\;x_{12}^+\;x_{12}^-\;y_{14}^+\;
  y_{14}^-\;y_{21}^+\;x_{13}^-\;x_{13}^+\;y_{11}^-).
\end{aligned}
\]

Hence both compatible orders have one face and

\[
\gamma_N=\frac{5-4+2-1}{2}=1.
\]

Thus the exact value must be recomputed after an AC move. In particular, the
orbit-2 calculation above is a statement about this exact word-realized
presentation, not about every AC-equivalent representative.

## Hostile self-check and scope

- The corner table contains exactly six corners from \(r_1\) and seven from
  \(r_2\), including both cyclic closing corners.
- The bundle multiplicities sum to
  \(2+3+2+2+2+2=13\).
- The simple support is \(K_4\), so it is planar; no abstract graph
  nonplanarity is used.
- The no-sphere argument uses the reversed \(B\)-paired synchronization at
  both generator ends. Dropping that condition would invalidate the forced
  adjacency argument.
- Every occurrence in the four-neighbour contradiction is distinct.
- The explicit face lengths sum to all \(26\) darts, give \(F=9\), and yield
  \(\chi=0\).
- No uniqueness claim is made for the genus-one order.

No proof gap remains in the lower or upper bound. The only scope limitation
is intentional: the theorem computes \(\gamma_N\) for the exact two cyclic
words displayed at the start, under the occurrence conventions of
`AK3_NEUWIRTH.md`.
