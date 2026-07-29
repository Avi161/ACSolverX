# A phase obstruction to thickenability of the displayed AK(3) complex

## Theorem and scope

Let

\[
P=\langle x,y\mid \mathtt{xxxYYYY},\mathtt{xyxYXY}\rangle,
\qquad X=x^{-1},\quad Y=y^{-1},
\]

with the two relators used exactly as written: no free or cyclic reduction is
made and no occurrences are identified.

**Theorem.** The displayed AK(3) presentation complex is not thickenable.
This is not AC-invariant and proves neither an AC nor stable-AC
counterexample.

The argument is a human, non-factorial proof.  It specializes the occurrence
dictionary in [`AK3_NEUWIRTH.md`](AK3_NEUWIRTH.md) and the spherical-bundle
classification in
[`AK3_SYNCHRONIZED_PLANARITY.md`](AK3_SYNCHRONIZED_PLANARITY.md), but includes
all data and deductions needed for this exact presentation.

## Occurrences and the link multigraph

Label the signed occurrences

\[
\begin{aligned}
r_1&=p_0p_1p_2p_3p_4p_5p_6
     =x_0x_1x_2Y_3Y_4Y_5Y_6,\\
r_2&=q_0q_1q_2q_3q_4q_5
     =x'_0y'_1x'_2Y'_3X'_4Y'_5.
\end{aligned}
\]

For each occurrence \(o\), let \(d_o\) and \(h_o\) be its departure and
arrival darts and put \(B=\prod_o(d_o\ h_o)\). If \(o_i,o_{i+1}\) are
consecutive cyclic positions, the corner after \(o_i\) is the transposition
\((h_{o_i}\ d_{o_{i+1}})\) in \(A\). Write \(e_i\) for the corner after
\(p_i\) and \(f_j\) for the corner after \(q_j\), with indices cyclic in each
relator.  The dart germs are

| letter | departure | arrival |
|---|---|---|
| \(x\) | \(x^+\) | \(x^-\) |
| \(X\) | \(x^-\) | \(x^+\) |
| \(y\) | \(y^+\) | \(y^-\) |
| \(Y\) | \(y^-\) | \(y^+\) |

The thirteen labeled corners form exactly these six parallel classes:

| class | germ pair | labeled corners |
|---|---|---|
| \(U\) | \(x^+x^-\) | \(e_0(xx),e_1(xx)\) |
| \(V\) | \(y^+y^-\) | \(e_3(YY),e_4(YY),e_5(YY)\) |
| \(P\) | \(x^+y^+\) | \(e_6(Yx),f_5(Yx)\) |
| \(Q\) | \(x^+y^-\) | \(f_1(yx),f_4(XY)\) |
| \(R\) | \(x^-y^+\) | \(f_0(xy),f_3(YX)\) |
| \(S\) | \(x^-y^-\) | \(e_2(xY),f_2(xY)\) |

Thus the simple support is \(K_4\), the multiplicities are
\((2,3,2,2,2,2)\), and the degrees of
\(x^+,x^-,y^+,y^-\) are \(6,6,7,7\). In particular, the link is connected.

For a Neuwirth-compatible rotation \(C\), orientability requires

\[
C_{g^-}=B C_{g^+}^{-1}B. \tag{1}
\]

The face cycles are the cycles of \(AC\). Since there are four vertices and
thirteen edges, a spherical rotation would have

\[
4-13+|AC|=2,
\qquad\text{hence}\qquad |AC|=11. \tag{2}
\]

## The complete spherical schemes

**Parallel-\(K_4\) lemma.** A rotation system of a loopless multigraph whose
simple support is \(K_4\) is spherical if and only if:

1. each parallel class is a single interval at both endpoints;
2. contracting the six intervals gives one of the two mirror tetrahedral
   rotations of simple \(K_4\); and
3. the labeled linear order in each interval is reversed at its other
   endpoint.

**Proof.** Fix the parallel \(uv\)-arcs. The other two \(K_4\) vertices are
joined, so they lie in one component of the complement of those arcs.  Every
non-\(uv\) edge must use that same component. Consequently all nonclass
darts occupy one gap at \(u\) and one gap at \(v\), so the class is a block.
The other complementary regions are empty digons, forcing reverse endpoint
orders.  Retaining one edge from every class leaves a spherical simple
\(K_4\), whose rotation is tetrahedral and unique up to reflection.
Conversely, expand the six edges of either tetrahedral embedding into
parallel ribbons in arbitrary labeled linear orders, reversed at the far
ends.  This produces every spherical rotation.  \(\square\)

There are therefore

\[
2\prod m_{uv}!=2(2!)^5(3!)=384 \tag{3}
\]

labeled spherical rotations.  Simultaneous inversion of all four vertex
cycles is global reflection.  It preserves (1), because

\[
C_{g^-}^{-1}=B C_{g^+}B
            =B(C_{g^+}^{-1})^{-1}B.
\]

It is therefore enough to treat one mirror, containing
\((2!)^5(3!)=192\) labeled rank assignments. No permutation inside a
parallel class is quotiented out.

## Fixed slots and phases

Order the germs as \(x^+,x^-,y^+,y^-\) and fix the macro-rotation

\[
\begin{aligned}
x^+&:(x^-,y^+,y^-),&x^-&:(x^+,y^-,y^+),\\
y^+&:(x^+,x^-,y^-),&y^-&:(x^+,y^+,x^-).
\end{aligned} \tag{4}
\]

Use the first germ listed in each class above as its reference endpoint.  If
an edge in a class of size \(m\) has reference rank \(z\), its rank at the
other endpoint is \(m-1-z\). The all-different rank families are

\[
\begin{array}{c|c}
U&(u_0,u_1)=(z(e_0),z(e_1)),\quad\{u_0,u_1\}=\{0,1\}\\
V&(v_3,v_4,v_5)=(z(e_3),z(e_4),z(e_5)),\quad
   \{v_3,v_4,v_5\}=\{0,1,2\}\\
P&(p_e,p_f)=(z(e_6),z(f_5)),\quad\{p_e,p_f\}=\{0,1\}\\
Q&(q_1,q_4)=(z(f_1),z(f_4)),\quad\{q_1,q_4\}=\{0,1\}\\
R&(r_0,r_3)=(z(f_0),z(f_3)),\quad\{r_0,r_3\}=\{0,1\}\\
S&(t_e,t_f)=(z(e_2),z(f_2)),\quad\{t_e,t_f\}=\{0,1\}.
\end{array} \tag{5}
\]

Expanding (4) gives the complete slot table:

| germ | block order | slot of a rank-\(z\) dart |
|---|---|---|
| \(x^+\) | \(U,P,Q\) | \(U:z,\ P:2+z,\ Q:4+z\pmod6\) |
| \(x^-\) | \(U,S,R\) | \(U:1-z,\ S:2+z,\ R:4+z\pmod6\) |
| \(y^+\) | \(P,R,V\) | \(P:1-z,\ R:3-z,\ V:4+z\pmod7\) |
| \(y^-\) | \(Q,V,S\) | \(Q:1-z,\ V:4-z,\ S:6-z\pmod7\) |

For an occurrence \(o\), let \(o^+\) be its dart at the positive end of its
unsigned generator and let \(o^-=B(o^+)\). Equation (1) holds exactly when
there is one phase for each generator such that

\[
\operatorname{slot}(o^+)+\operatorname{slot}(o^-)+\sigma_g
\equiv0\pmod{\deg(g)} \tag{6}
\]

for every occurrence \(o\) of \(g^{\pm1}\). Indeed, reversal says the two
written slot coordinates sum to one occurrence-independent constant, and
the phase is its negative.  Conversely, (6) reconstructs the reversed
cyclic order.  Thus no cyclic alignment is lost.

## The \(x\)-phase forces every binary rank

The six \(x^{\pm1}\)-occurrences give, in order,

\[
\begin{array}{c|c}
p_0&(2+p_e)+(1-u_0)+\sigma_x\equiv0\\
p_1&u_0+(1-u_1)+\sigma_x\equiv0\\
p_2&u_1+(2+t_e)+\sigma_x\equiv0\\
q_0&(2+p_f)+(4+r_0)+\sigma_x\equiv0\\
q_2&(4+q_1)+(2+t_f)+\sigma_x\equiv0\\
q_4&(4+q_4)+(4+r_3)+\sigma_x\equiv0
\end{array}
\qquad(\bmod 6). \tag{7}
\]

The \(p_1\) equation gives \(\sigma_x=0\) when
\((u_0,u_1)=(0,1)\), but then \(p_0\) would require
\(3+p_e\equiv0\pmod6\), impossible for binary \(p_e\). Hence

\[
(u_0,u_1)=(1,0),\qquad \sigma_x=4. \tag{8}
\]

Now \(p_0\) and \(p_2\) force \(p_e=t_e=0\). The \(P\)- and \(S\)-class
all-different constraints force \(p_f=t_f=1\). Substitution in \(q_0\) and
\(q_2\) then gives \(r_0=q_1=1\), and the \(R\)- and \(Q\)-class constraints
give \(r_3=q_4=0\). The last equation is consequently
\(12\equiv0\pmod6\), so all six equations are consistent and every binary
rank is uniquely forced:

\[
\boxed{
\begin{gathered}
u_0=1, u_1=0,\quad p_e=0, p_f=1,\quad
q_1=1, q_4=0,\\
r_0=1, r_3=0,\quad t_e=0, t_f=1,\quad
\sigma_x=4.
\end{gathered}} \tag{9}
\]

No \(V\)-rank has been used.

## The incompatible \(y\)-phase

Only two occurrences are needed. At \(q_1=y\), the positive dart is on the
preceding edge \(f_0\in R\) and the negative dart is on the following edge
\(f_1\in Q\). Equation (6) becomes

\[
(3-r_0)+(1-q_1)+\sigma_y\equiv0\pmod7,
\]

so (9) forces

\[
\sigma_y\equiv5\pmod7. \tag{10}
\]

At \(q_3=Y\), the negative dart is on the preceding edge \(f_2\in S\) and
the positive dart is on the following edge \(f_3\in R\). Its equation is

\[
(6-t_f)+(3-r_3)+\sigma_y\equiv0\pmod7,
\]

which forces

\[
\sigma_y\equiv6\pmod7. \tag{11}
\]

The same phase cannot satisfy (10) and (11).  Hence the fixed tetrahedral
scheme has no compatible rotation.  The reflection argument above excludes
its mirror. The parallel-\(K_4\) lemma, the all-different ranks, and the two
phase equations represent every spherical rotation and every cyclic
alignment, so the \(192\) reflection-quotiented candidates are exhausted.
The contradiction occurs before the six possible \(V\)-orders matter:
there are zero unresolved cases.  Therefore no orientable thickening exists.

## Why a nonorientable thickening cannot escape the obstruction

The displayed balanced presentation presents the trivial group. Its
presentation complex \(K\) has \(\chi(K)=1\) and \(\pi_1(K)=1\). Hence
\(H_1(K)=0\); since \(K\) is two-dimensional, \(H_2(K)\) is free, and the
Euler characteristic forces \(H_2(K)=0\). Hurewicz and Whitehead then imply
that \(K\) is contractible.

If \(K\) embedded PL in any 3-manifold, a closed regular neighbourhood \(N\)
would deformation retract onto \(K\). Thus \(N\) would be contractible, so
its orientation character in \(H^1(N;\mathbb Z/2)\) would vanish and \(N\)
would be orientable.  That would give the orientable thickening already
excluded.  The theorem therefore rules out thickenability in arbitrary PL
3-manifolds, not only an orientable choice of ambient manifold.

## Independent computational evidence

These replays are corroboration, not premises of the proof.  The authenticated
[`ak3_neuwirth_census.json`](../../results/stable_ac/theory/ak3_neuwirth_census.json)
enumerates all \(5!6!=86{,}400\) compatible order pairs for the exact words,
finds no genus-zero order, and reports minimum Neuwirth genus two; its direct
and independent dart traces have the same digest.  Separately, the signed-rank
replay covered by
[`test_neuwirth_rank_solver.py`](../../tests/stable_ac/test_neuwirth_rank_solver.py)
returns `NOT_SPHERICAL` after exhausting its one \(K_4\) scheme, all \(42\)
phase pairs, and all \(168\) component-seed attempts. Neither result is used
in the deductions (7)--(11).
