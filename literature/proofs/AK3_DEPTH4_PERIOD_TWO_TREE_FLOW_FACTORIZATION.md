# Period-two tree flow, quadratic factorization, and the exact transition boundary

## Status

This note proves a universal structural theorem for the fixed period-two
relation-module problem and records a separate exact bounded certificate.
The universal part proves:

1. \(K=\langle A,B,G\rangle\cong F_3\), and the two \(K\)-orbits of module
   vertices are free Cayley trees;
2. every finitely supported, component-balanced \(L_0\)-boundary has one
   finite forest flow, linear in the canonical source;
3. every balanced two-source direction is a signed sum of anchored
   one-source directions;
4. the final fifteen-bit syndrome is affine quadratic, factors through
   homogeneous directions modulo two, and has biadditive alternating
   polarization; and
5. exact equality and shortlex-order inversion are the data omitted by the
   previously proposed transition summary; and
6. the subsequent exact Hessian analysis sharpens the pulled-back rank
   problem to a documented-open cross/unary boundary without deciding it.

The bounded part pins the depth-six fixtures and proves that the proposed
finite summary is not Markov.  The later Hessian boundary pins the exact
sixteen-occurrence and twelve-active-occurrence normal forms, but it does not
prove an all-depth obstruction, does not decide finite versus infinite rank
on the actual anchored \(L_0\) two-source geodesic-current language, and does
not settle the period-two lift, stable Andrews--Curtis, or Andrews--Curtis.

No depth-seven census or search is used.

## 1. Executable premises and notation

Put
\[
Q=\langle c,t\mid c^2=1\rangle=C_2*\mathbb Z
\]
and
\[
X=Q/\langle c\rangle,\qquad M=\mathbb Z[X].
\]
Module vertices are canonical right-\(\langle c\rangle\) representatives.
Write
\[
Q=F(p,q)\rtimes\langle c\rangle,\qquad p=t,\qquad q=ctc,
\]
where conjugation by \(c\) exchanges \(p\) and \(q\).

For the fixed period-two recurrence, the last three relation-module
operators are
\[
L_2=1-X_0,\qquad L_3=U^{-1}-t,\qquad L_4=t-1.
\tag{1}
\]
To avoid confusing the module vertex set \(X\) with the element \(X_0\),
use the forest basis
\[
A=t,\qquad B=X_0,\qquad G=U^{-1}t^{-1},
\tag{2}
\]
and put \(K=\langle A,B,G\rangle\le Q\).  The incidence map for (1) is the
oriented edge boundary for the \(A,B,G\)-orbit graph on \(X\), after the
fixed sign and \(t^{-1}\)-shift conventions in the \(L_3\) coordinate.

The tracked certificate supplies the following finite premises.

- The parity kernel described below has five Reidemeister--Schreier
  generators.
- Their five images in \(F(p,q)\) fold to a complete four-sheet core with
  four vertices, eight unoriented edges, sixteen directed edges, and rank
  five.
- The induced \(c\)-action on the four right \(K\)-cosets is
  \((0\ 1)(2\ 3)\).
- The source-flow implementation uses exact complete-cover rewriting for
  every displayed finite path.

These are executable premises.  The free-action, boundary-injectivity,
flow-uniqueness, and quadratic statements below are proved for arbitrary
finite support; they are not inferred from the depth-six enumeration.

## 2. The parity-kernel restriction proves \(K\cong F_3\)

Let
\[
F=\langle a,b,g\rangle
\]
and define \(\theta:F\to Q\) by
\[
\theta(a)=A,\qquad\theta(b)=B,\qquad\theta(g)=G.
\]
The \(c\)-parity of \(A,B,G\) is respectively \(0,1,1\).  Hence the
parity kernel \(P\) in \(F\) has index two.  Reidemeister--Schreier with
transversal \(\{1,b\}\) gives the free basis
\[
a,\qquad gb^{-1},\qquad bab^{-1},\qquad b^2,\qquad bg.
\tag{3}
\]
Thus \(P\) is free of rank five.

In \(H=F(p,q)\), the five reduced images of (3) are
\[
\begin{aligned}
w_1&=p,\\
w_2&=qPPqPqpQ,\\
w_3&=qPQpqPqpQ,\\
w_4&=qPQppQPq,\\
w_5&=qPQppQQp,
\end{aligned}
\tag{4}
\]
where upper-case letters denote inverses.  Their deterministic Stallings
core has four vertices and eight unoriented edges, so
\[
\operatorname{rank}\langle w_1,\ldots,w_5\rangle=8-4+1=5.
\tag{5}
\]
The restriction
\[
\theta|_P:P\longrightarrow\langle w_1,\ldots,w_5\rangle
\]
is a surjection between free groups of the same finite rank.  After choosing
a free basis of the target, it becomes a surjective endomorphism of \(F_5\).
Finite-rank free groups are Hopfian, so this restriction is an isomorphism.

If \(u\in\ker\theta\), then its image has even \(c\)-parity, so \(u\in P\).
Injectivity on \(P\) gives \(u=1\).  Therefore
\[
\boxed{K\cong F(A,B,G)\cong F_3.}
\tag{6}
\]

The same complete Stallings core is a four-sheet cover of the two-petal
rose, hence
\[
[H:\theta(P)]=4.
\]
Since \(K\) surjects onto \(Q/H\cong C_2\) and
\(K\cap H=\theta(P)\),
\[
[Q:K]=[H:K\cap H]=4.
\tag{7}
\]
This proves the index and rank claims from the recorded parity-kernel
premises; a bare rank-five predicate would not suffice.

## 3. Two free Cayley-tree components and finite boundary injectivity

The stabilizer in \(K\) of a module vertex \(q\langle c\rangle\) is
\[
K\cap q\langle c\rangle q^{-1}.
\tag{8}
\]
Every nonidentity element of the conjugate on the right has order two.
By (6), \(K\) is torsion-free, so (8) is trivial.  Thus \(K\) acts freely
on every one of its orbits in \(X\).

The complete four-sheet right-coset action has
\[
c=(0\ 1)(2\ 3).
\]
Consequently the double-coset set \(K\backslash Q/\langle c\rangle\) has
two elements.  The module-vertex incidence graph therefore has exactly two
components.  On each component, freeness of the \(K\)-action identifies the
labelled \(A,B,G\)-orbit graph with the Cayley graph of \(F(A,B,G)\).  Hence
\[
\mathcal T=\mathcal T_0\sqcup\mathcal T_1
\tag{9}
\]
is a disjoint union of two trees.

Let \(C_1^{\rm fin}(\mathcal T;\mathbb Z)\) be the finitely supported
oriented edge chains and let
\[
\partial:C_1^{\rm fin}(\mathcal T;\mathbb Z)
\longrightarrow C_0^{\rm fin}(\mathcal T;\mathbb Z)
\tag{10}
\]
be edge boundary.  If a nonzero finite chain \(z\) satisfied
\(\partial z=0\), the finite subforest spanned by the nonzero edges of
\(z\) would have a leaf.  Exactly one nonzero supported edge is incident
to that leaf, so its coefficient survives with sign in \(\partial z\), a
contradiction.  Therefore
\[
\ker\partial=0.
\tag{11}
\]
This leaf-removal proof works over \(\mathbb Z\), not merely modulo two.

## 4. Unique linear canonical forest flow

Let \(s\in M\) be finitely supported and canonical, and put \(b=L_0s\).
Under the edge-coordinate identification above, define
\[
\partial_K(d_2,d_3,d_4)=L_2d_2+L_3d_3+L_4d_4.
\]
Choosing the orientation of each \(A,B,G\)-edge to match its displayed
binomial makes \(\partial_K\) exactly the ordinary edge boundary (10).
Suppose the coefficient sum of \(b\) is zero on each component
\(\mathcal T_0,\mathcal T_1\).  In each component, split coefficients into
unit positive and negative endpoints of \(-b\), pair them arbitrarily, and
sum the corresponding oriented geodesics.  This gives a finite edge chain
\(d\) with \(\partial_Kd=-b\).

Any two endpoint pairings give chains with the same boundary.  Their
difference is a finite cycle and is zero by (11).  Hence the edge chain is
unique.  Denote the corresponding five correction variables by
\[
D(s)=(s,0,d_2,d_3,d_4),
\qquad
L_0s+L_2d_2+L_3d_3+L_4d_4=0.
\tag{12}
\]
Since \(\partial\) is linear and injective, its inverse on component-balanced
finite boundaries is linear.  Therefore
\[
D(s+s')=D(s)+D(s'),\qquad D(ns)=nD(s)
\tag{13}
\]
whenever the displayed sources are component-balanced.

Only the variables in (12) are pairing-independent.  A pairing is a
construction witness, not part of the invariant: different pairings can
and do produce different path lists while summing to the same edge chain.
The tracked crossed Result 153 fixture pins exactly this distinction.

### Canonicalization is part of the hypothesis

Raw dictionaries must be aggregated after passing keys to \(X\).  The raw
keys \(1\) and \(c\), represented by the empty word and the one-letter word
\(c\), name the same module vertex.  A dictionary comprehension can
overwrite one coefficient and is not a canonicalization map.  The repaired
source path first sums all coefficients at the canonical vertex.

The two exact regressions are
\[
\{1:1,c:-1\}\longmapsto0
\tag{14}
\]
and
\[
\{1:1,c:1,Tct:2\}\longmapsto\{1:2,Tct:2\}.
\tag{15}
\]
The theorem applies to the canonical sums on the right, not to an
uncollapsed raw-key representation.

## 5. Anchored one-source decomposition

For \(v\in X\), define
\[
\lambda(v)=
\sum_{x\in\mathcal T_0}[e_x](L_0e_v).
\tag{16}
\]
The total augmentation of \(L_0e_v\) is zero, so its two component sums are
\((\lambda(v),-\lambda(v))\).  Take the anchor
\[
a=T,\qquad\lambda(a)=1,
\tag{17}
\]
and define
\[
H(v)=D(e_v-\lambda(v)e_a).
\tag{18}
\]
The source in (18) is component-balanced, so \(H(v)\) exists uniquely by
Section 4.

If
\[
s=e_x+\epsilon e_y,\qquad\epsilon\in\{1,-1\},
\]
is component-balanced, then
\[
\lambda(x)+\epsilon\lambda(y)=0.
\]
Linearity now gives the exact anchored decomposition
\[
\boxed{D(e_x+\epsilon e_y)=H(x)+\epsilon H(y).}
\tag{19}
\]
This is an identity of all five sparse variables.  The executable fixtures
cover positive and negative signs and source scalars of magnitude one and
two:
\[
\begin{gathered}
TT+tt,\qquad TTT-cTTT,\qquad TTT+Tct,\\
TT+TTTct,\qquad Tctt+Tctct.
\end{gathered}
\tag{20}
\]

## 6. Universal affine quadraticity

Let \(N\) be the kernel of the quotient from the free group on \(c,t\) to
\(Q\).  Reidemeister--Schreier identifies \(N\) with the free group on
\[
r_v=v c^2v^{-1}\qquad(v\in X),
\tag{21}
\]
where the canonical quotient word for \(v\) is interpreted as a word in the
free group.  Then \(N_{\rm ab}\cong M\).  Work in the degree-two Magnus
quotient of \(N\).
Its linear coordinate lies in
\[
V=\mathbb Z^{(X)}
\]
and its tensor coordinate lies in \(V\otimes V\).  Multiplication,
inversion, the \(Q\)-action, and conjugation are polynomial operations of
degree at most two in these coordinates.

For a finitely supported integer vector \(f=(f_v)\), the certificate uses
the fixed shortlex section
\[
\sigma(f)=\prod_v r_v^{f_v}.
\tag{22}
\]
The degree-two coordinate of (22) is
\[
\mu(\sigma(f))
=\sum_{u<v}f_uf_v\,e_u\otimes e_v
+ \sum_v\binom{f_v}{2}e_v\otimes e_v.
\tag{23}
\]
Thus the only binomial self term is tensor-diagonal.

Let \(D\) be any finitely supported homogeneous correction direction, so
\(\sum_iL_iD_i=0\), and let \(R(D)\in[N,N]\) be the exact corrected residual
formed from the fixed base correction plus \(D\).  Every exponent in every
section (22) is affine linear in \(D\).  Applying the degree-at-most-two
operations above proves that the tensor coordinate of \(R(D)\), and hence
every linear functional of its exterior projection, is an integer-valued
affine quadratic function of \(D\).

Write the fourteen finite-action exterior-wedge bits in their tracked order
and append the full wedge-sum bit \(\Phi_\infty\).  This defines
\[
S(D)\in\mathbb F_2^{15}.
\tag{24}
\]
Put
\[
C=S(0),\qquad
U(D)=S(D)+C,
\]
and
\[
\mathcal B(D,E)=S(D+E)+S(D)+S(E)+C.
\tag{25}
\]
The vanishing of third finite differences for a quadratic law shows that
\(\mathcal B\) is biadditive over \(\mathbb F_2\), and
\[
S(D+E)=C+U(D)+U(E)+\mathcal B(D,E).
\tag{26}
\]

## 7. Tensor diagonal, period two, and alternating polarization

It remains to rule out a surviving mod-four self term.  From (23),
\[
\mu(\sigma(f+2h))-\mu(\sigma(f))
\equiv\sum_v h_v\,e_v\otimes e_v\pmod2.
\tag{27}
\]
Indeed all off-diagonal changes are even, while
\[
\binom{f_v+2h_v}{2}-\binom{f_v}{2}
=2f_vh_v+h_v(2h_v-1)\equiv h_v\pmod2.
\]
Therefore changing a correction direction by twice another direction
changes each canonical lift, modulo two and degree three, only by an element
of the tensor-diagonal subspace
\[
\Delta=\operatorname{span}_{\mathbb F_2}
\{e_v\otimes e_v:v\in X\}.
\tag{28}
\]

The corrected-residual word circuit preserves \(\Delta\), but not by
cancelling a central increment in the first four conjugation slots.  A
degree-two element central in \(N/\gamma_3N\) need not commute with a word
whose image in \(Q\) is nontrivial.

The correct argument is invariant-subspace propagation.  The \(Q\)-action
on \(V\) permutes module vertices:
\[
q e_v=e_{qv}.
\]
Consequently
\[
q(e_v\otimes e_v)=e_{qv}\otimes e_{qv},
\]
so \(\Delta\) is \(Q\)-stable.  Say that two crossed class-two coordinates
are \(\Delta\)-equivalent when they have the same quotient coordinate, the
same mod-two linear coordinate, and tensor coordinates differing by an
element of \(\Delta\).  The crossed multiplication law shows that a product
of two pairs of \(\Delta\)-equivalent coordinates is again
\(\Delta\)-equivalent: the two tensor differences are merely added after
the appropriate \(Q\)-translation.  The inversion law has the same
property.

For conjugation, suppose the payload changes by a tensor increment
\(\eta\in\Delta\), while the conjugator changes by a central tensor
increment \(\delta\in\Delta\).  Transport of \(\eta\) by the fixed quotient
of the conjugator remains in \(\Delta\).  If \(q\in Q\) is the quotient of
the conjugated payload, the extra contribution from the conjugator is
\[
\delta+q\delta.
\tag{28'}
\]
Both summands lie in \(\Delta\).  This is the point at which centrality
inside \(N/\gamma_3N\) is insufficient for cancellation but \(Q\)-stability
is sufficient for propagation.

Apply this observation successively to the exact recurrence.  Write
\(r',s',u',z'\), and \(\operatorname{target}'\) for the words formed from
\(D+2E\).  Equation (27) says that each corrected conjugator changes by
some \(\delta_i\in\Delta\).

1. In
   \(r=\operatorname{SOURCE}_A\,
   \operatorname{conj}(\operatorname{SOURCE}_B^{-1},h_0H_0)\), the fixed
   payload \(\operatorname{SOURCE}_B^{-1}\) has a generally nontrivial
   quotient.  Formula (28') gives \(r'\sim_\Delta r\).
2. In
   \(s=\operatorname{SOURCE}_B\,
   \operatorname{conj}(r^{-1},h_1H_1)\), closure under inversion first
   gives \((r')^{-1}\sim_\Delta r^{-1}\), and then the conjugation and
   product laws give \(s'\sim_\Delta s\).
3. The same argument in
   \(u=r\,\operatorname{conj}(s^{-1},h_2H_2)\) gives
   \(u'\sim_\Delta u\).
4. Applying it to
   \(z=u^{-1}\operatorname{conj}(s,h_3H_3)\) gives
   \(z'\sim_\Delta z\).
5. Finally,
   \(\operatorname{target}=\operatorname{conj}(t,h_4)\) changes by
   \(\delta_4+t\delta_4\in\Delta\), and multiplication by its inverse
   gives the same conclusion for the residual.

Thus induction through \(r,s,u,z,\operatorname{target}\), and the final
residual gives
\[
\mu(R(D+2E))-\mu(R(D))\in\Delta
\qquad\text{over }\mathbb F_2.
\tag{29}
\]

Exterior projection kills \(\Delta\), both before and after every finite
point-action pushforward.  All fifteen functionals in (24) factor through
that exterior projection.  Hence
\[
\boxed{S(D+2E)=S(D)}
\tag{30}
\]
for all finitely supported homogeneous \(D,E\).  There is no surviving
mod-four term in the final syndrome.

Combining (25) and (30),
\[
\mathcal B(D,D)=S(2D)+S(D)+S(D)+S(0)=0.
\tag{31}
\]
Thus the polarization is alternating as well as biadditive, and \(S\)
factors through the homogeneous-direction group modulo two.

The genuine sequence
\[
0,0,1,1,0
\]
for coefficients \(0,1,2,3,4\) belongs to the pre-wedge diagonal term
\(\binom n2 e_v\otimes e_v\).  It is a valid Magnus-tensor fixture, but (29)
and exterior projection prevent it from surviving in the fifteen-bit
syndrome.

In particular, the historical enumeration of
\[
4^{11}=4194304
\]
coefficient classes remains a valid obstruction replay, but it is
redundant: the final syndrome depends only on the \(2^{11}\) parity classes,
each of which the mod-four enumeration repeats \(2^{11}\) times.  Mod four
is not essential for these fifteen exterior-wedge bits.

## 8. Exact bounded certificate

The executable record is
\[
\texttt{experiments/stable\_ac/depth4\_period\_two\_tree\_flow\_factorization\_certificate.py}.
\]
Its fields have the following exact values.

| Field | Value |
|---|---|
| recorded_complete_cover | \((4,16,\mathrm{True})\) |
| recorded_parity_kernel_rank | \(5\) |
| recorded_parity_kernel_generator_count | \(5\) |
| recorded_parity_kernel_image_rank | \(5\) |
| proof_conclusion_parity_kernel_restriction_isomorphic | true |
| proof_conclusion_k_injective | true |
| proof_conclusion_k_index_in_q | \(4\) |
| proof_conclusion_k_rank | \(3\) |
| proof_conclusion_k_torsion_free | true |
| proof_conclusion_vertex_stabilizers_trivial | true |
| proof_conclusion_tree_components | \(2\) |
| proof_conclusion_tree_actions_are_cayley_trees | true |
| proof_conclusion_finite_edge_boundary_injective | true |
| proof_conclusion_unique_finite_forest_flow | true |
| proof_conclusion_flow_pairing_independent | true |
| proof_conclusion_flow_linear | true |
| proof_conclusion_syndrome_factors_through_homogeneous_directions_mod_two | true |
| proof_conclusion_polarization_is_biadditive | true |
| proof_conclusion_polarization_is_alternating | true |
| bounded_raw_collision_checks | \(2\) |
| bounded_crossed_pairing_paths_differ | true |
| bounded_crossed_pairing_variables_equal | true |
| bounded_anchor_label | \(T\) |
| bounded_anchor_scalar | \(1\) |
| bounded_anchored_decompositions | \(TT+tt,\ TTT-cTTT,\ TTT+Tct,\ TT+TTTct,\ Tctt+Tctct\) |
| bounded_quadratic_constant | 111010110101011 |
| bounded_near_survivor_unaries | 110101011011001, 101111111110111 |
| bounded_near_survivor_cross | 100000010000100 |
| bounded_biadditivity | 100000001000100 |
| bounded_fixed_zero_self_polarizations | \(4\) |
| bounded_period_two_direction | \(TT\) |
| bounded_period_two_coefficient_records | the five records in (32) |
| bounded_period_two_syndromes | the last column of (32), in order |
| bounded_depth_six_anchored_atoms | \(127\) |
| bounded_depth_six_zero_self_polarizations | \(127\) |
| bounded_tracked_homogeneous_directions | \(11\) |
| bounded_tracked_zero_self_polarizations | \(11\) |
| bounded_no_markov_summary | the source classes and scalars below (33), the six records (34), and syndrome (35) |
| bounded_no_markov_extensions | the three exact records in (36) |
| bounded_max_fixture_source_depth | \(6\) |

For the \(TT\) direction, the exact coefficient records
\((n,n\bmod2,S(nD))\) are
\[
\begin{array}{c|c|c}
n&n\bmod2&S(nD)\\ \hline
0&0&111010110101011\\
1&1&001111101110010\\
2&0&111010110101011\\
3&1&001111101110010\\
4&0&111010110101011.
\end{array}
\tag{32}
\]
The bounded checks over 127 depth-six anchored atoms and all eleven tracked
homogeneous directions support the universal proof, but do not replace it.
Every fifteen-character binary string in this note denotes the ordered
fifteen-tuple of its digits, with \(\Phi_\infty\) last.

## 9. The exact no-Markov collision

The refuted summary consists exactly of:

1. the unordered source-action classes;
2. the signed \(L_0\)-orbit scalars;
3. the multiset of paired endpoint action classes together with the finite
   \(\epsilon\)-branch used by the exact \(K\)-rewrite; and
4. the current fourteen projected bits followed by \(\Phi_\infty\).

For
\[
P=e_{TT}+e_{TTTct},
\qquad
P'=e_{Tctt}+e_{Tctct},
\tag{33}
\]
the common source-action classes are
\[
((0,2,3,1),(2,0,1,3)),
\]
the common signed orbit scalars are
\[
(-1,1),
\]
and the common six pair records are
\[
\begin{aligned}
&((0,1,2,3),(0,2,3,1),1),\\
&((0,2,3,1),(0,3,1,2),0),\\
&((0,2,3,1),(0,3,1,2),1),\\
&((2,0,1,3),(2,1,3,0),0),\\
&((2,0,1,3),(2,1,3,0),1),\\
&((2,3,0,1),(2,0,1,3),1).
\end{aligned}
\tag{34}
\]
Their common current syndrome is
\[
S(D(P))=S(D(P'))=000000000000001.
\tag{35}
\]

Simultaneous left extension separates them exactly:
\[
\begin{array}{c|c|c}
\text{extension}&S(D(gP))&S(D(gP'))\\ \hline
c&000100000000100&100100011000001\\
t&000000001000000&100100011000100\\
T&011110110101110&011110111101010.
\end{array}
\tag{36}
\]
All source words in this fixture have depth at most six.  Equations
(33)--(36) prove that the displayed summary is not a Markov state.  They do
not prove that no richer finite state exists.  The complete reduced
\(A/B/G\)-rewrite word distinguishes the examples, but it is unbounded.

## 10. Exact section cocycle under left extension

The failure in (36) comes from the non-equivariance of the canonical
shortlex section, not from a failure of affine quadraticity.

Pass to
\[
\bar V=\mathbb F_2^{(X)}
\]
and order \(X\) by the same shortlex order used in (22).  Define
\[
s(f)=\prod_{x\in X\ {\rm in\ shortlex\ order}}r_x^{f_x}.
\tag{37}
\]
Fix the quotient-word section
\[
\iota:Q\longrightarrow F(c,t)
\]
which interprets the unique reduced \(C_2*\mathbb Z\) normal form as the
same literal free word; write \(\widehat g=\iota(g)\).  This is the
canonical section used by quotient reduction, but it is not multiplicative.
For \(g\in Q\), define the one-vertex defect and full transport defect by
\[
\tau_g(x)=
\left[s(e_{gx})^{-1}\widehat g\,s(e_x)\widehat g^{-1}\right]
\in\Lambda^2\bar V
\tag{38}
\]
and
\[
\kappa_g(f)=
\left[s(gf)^{-1}\widehat g\,s(f)\widehat g^{-1}\right]
\in\Lambda^2\bar V.
\tag{39}
\]
The bracket means the degree-two exterior coordinate; both displayed
ratios have zero linear coordinate.  Put
\[
\operatorname{Inv}_g(f)=
\sum_{\substack{x<y\\gx>gy}}
f_xf_y\,e_{gx}\wedge e_{gy}.
\tag{40}
\]

Then the exact section-cocycle decomposition is
\[
\boxed{
\kappa_g(f)=\sum_x f_x\tau_g(x)+\operatorname{Inv}_g(f).
}
\tag{41}
\]
To prove it, conjugate the ordered product (37).  Each factor contributes
its central one-vertex defect (38), giving the linear sum.  The remaining
factors are still in the old \(x\)-order.  Reordering them into the new
\(gx\)-shortlex order swaps exactly the pairs in (40), and each swap
contributes the corresponding exterior commutator.  No other degree-two
term remains.

For completeness, composition must retain the multiplication defect of
\(\iota\).  Put
\[
\omega(g,h)=\widehat g\,\widehat h\,\widehat{gh}^{-1}\in N
\tag{42}
\]
and let \(\overline\omega(g,h)\in\bar V\) be its linear Magnus coordinate.
Then the exact corrected identity is
\[
\kappa_{gh}(f)=
\kappa_g(hf)+g\kappa_h(f)
+\overline\omega(g,h)\wedge(ghf).
\tag{42'}
\]
Here \(g\) on \(\Lambda^2\bar V\) is the induced label permutation.  The
last term cannot be dropped: for \(g=h=c\), the chosen lifts multiply to
\(c^2\), while \(\widehat{gh}=1\).  Formula (41), applied to each literal
multiplier \(c,t,T\), is the decomposition used below.

Thus an exact transition computation needs both linear representative
defects and shortlex inversions.

## 11. The full-wedge polarization is exact equality

Let \(b_\infty\) be the alternating bilinear form underlying
\(\Phi_\infty\).  On basis vectors,
\[
b_\infty(e_x,e_y)=
\begin{cases}
1,&x\ne y,\\
0,&x=y.
\end{cases}
\]
For arbitrary finite currents \(f,g\in\bar V\),
\[
\boxed{
b_\infty(f,g)
=\varepsilon(f)\varepsilon(g)+\langle f,g\rangle,
}
\tag{43}
\]
where
\[
\varepsilon(f)=\sum_xf_x,\qquad
\langle f,g\rangle=\sum_xf_xg_x.
\]
Indeed the left side is \(\sum_{x\ne y}f_xg_y\), which is exactly the
right side over \(\mathbb F_2\).  On augmentation-zero currents,
\[
b_\infty(f,g)=\langle f,g\rangle.
\tag{44}
\]

This equality kernel has infinite rank.  Choose pairwise distinct
\(p_i,q_i\) and one further vertex \(s\), and set
\[
f_i=e_{p_i}+e_{q_i},\qquad g_j=e_{p_j}+e_s.
\]
Then \(f_i,g_j\) have augmentation zero and
\[
b_\infty(f_i,g_j)=\delta_{ij}.
\tag{45}
\]
Therefore \(b_\infty\) cannot factor on all finite augmentation-zero
currents through a finite-dimensional linear quotient.  Nor can finite
separate summaries of \(f\) and \(g\) determine it, because (45) gives
infinitely many distinct rows.  The vertices may be chosen in fixed fibers
of any prescribed finite product of point actions and outside prescribed
finite balls.

## 12. Infinite rank of shortlex inversion

Use the quotient-letter order \(T<c<t\).  For \(i,j\ge2\), put
\[
b_i=ct^{i-1},\qquad
d_j=cT^{j-1},\qquad
a_j=td_j=tcT^{j-1}.
\tag{46}
\]
Left multiplication by \(T\) gives
\[
Tb_i=Tct^{i-1},\qquad Ta_j=d_j.
\]
A direct comparison before and after multiplication yields
\[
I_T(b_i,a_j)=
\begin{cases}
1,&i=j\ \text{or}\ i=j+1,\\
0,&\text{otherwise},
\end{cases}
\tag{47}
\]
for the scalar two-singleton inversion parity.  Every finite leading
principal matrix in (47) is bidiagonal with diagonal one, hence has full
rank over \(\mathbb F_2\).

This remains true after any prescribed finite collection of point actions.
Choose a common multiple \(L\ge2\) of the orders of the image of \(t\) and
restrict \(i,j\) to one residue class modulo \(L\).  All \(b_i\) have the
same finite-action values, all \(a_j\) have the same finite-action values,
the \(i=j+1\) band disappears, and the remaining matrix is the infinite
identity.  Discarding finitely many indices puts the vertices outside any
fixed radius.  Passing to a further infinite subsequence fixes any finite
list of bounded local types without changing the identity matrix.

Consequently no universal summary for arbitrary finite currents built from
finite-dimensional linear data, finitely many point actions, and finitely
many bounded-local additive statistics can determine both the equality and
shortlex-inversion kernels.

## 13. The precise remaining theorem boundary

Sections 11 and 12 concern arbitrary finite currents.  They do not prove
infinite rank after pulling the kernels back through the exact anchored map
\[
v\longmapsto H(v)
\]
and the fixed five-slot corrected-residual recurrence.  In particular,
equality or inversion terms from one correction slot may cancel terms from
another.  The actual anchored \(L_0\) two-source language is much smaller:
its edge currents are xors of a uniformly bounded number of geodesics in
the two \(F_3\) Cayley trees, with endpoints obtained by fixed quotient
multipliers and finite-index rewriting.

Therefore the infinite-rank results do not rule out an arbitrary finite
automaton on that restricted language.  The exact next alternative is:

1. prove that the equality and shortlex-inversion kernels pulled back to
   the anchored \(L_0\) geodesic-current image are rational finite-state
   kernels; or
2. exhibit an infinite-Hankel-rank family inside that restricted anchored
   image.

Until one side is proved, complete reduced words give an exact
pushdown/infinite-state transition procedure, but neither finite-state
closure nor finite-state impossibility is known.  This restricted-kernel
alternative, sharpened by the exact Hessian and unary recurrences below, not
a depth-seven census, is the next theorem.

## 14. Subsequent exact Hessian boundary

The follow-up proof
[`AK3_DEPTH4_PERIOD_TWO_PHI_INFINITY_HESSIAN.md`](AK3_DEPTH4_PERIOD_TWO_PHI_INFINITY_HESSIAN.md)
pulls the final full-wedge bit back through the anchored map without using a
source-depth census.  The literal AST has sixteen signed correction
occurrences with slot counts
\[
(6,4,2,2,2).
\]
After deleting only the four slot-one occurrences, which vanish on every
anchored direction, the exact normal form has twelve active occurrences with
slot counts
\[
(6,0,2,2,2),
\]
four equality kernels, six polarized inversion kernels, and 66 external
order kernels.  Their 76 normalized components reproduce the independent
crossed Hessian.

For the first explicit raw ray, the first slot-zero inversion component is
proved all-index:
\[
P_{ij}=\delta_{ij}.
\]
The complete-cover endpoint paths have exact fixed-block factorizations, and
their edge currents obey exact right-deck cocycle recurrences.  Those facts do
not prove the former companion claim.  The claim that the other 75 kernels
xor to \(\delta_{ij}\), and the resulting all-index cancellation of the full
mixed bit, is withdrawn: its attempted two-step induction omitted canonical
`c_vertex` normalization and the old--new/new--new order terms.  Universal
row-2 and row-3 primitive or companion claims are withdrawn as well.

The surviving cross obligation is exact.  For each of the 76 components,
the canonical two-step defect must vanish when both endpoints remain in one
strict region \(i<j\) or \(i>j\).  At the three \(i\)-step and three
\(j\)-step diagonal offsets, exact 76-component defect vectors must instead
be computed; constituent defects need not vanish.  The primitive boundary
defects are \((1,0,1)\) in both directions.  The recorded ten-cell component
signatures are bounded base data only.

There is no universal vanishing shortcut.  If
\(q_\infty(D)=s_\infty(D)+s_\infty(0)\), then
\[
\beta_\infty(D,E)=\delta q_\infty(D,E)
\]
is universally an alternating two-coboundary, but the anchored fixture gives
\[
\beta_\infty(H(TTT),H(cTTT))=1.
\]
Thus the mixed kernel is nonzero on the anchored image.

The complete validity-plus-syndrome rank question also retains a unary term.
The exact integral unary recurrence carries the doubled anchor, fixed-base
products, one-vertex transport defects, quotient-section defects, and tensor
diagonals through the literal AST.  Its state consists of unbounded sparse
currents and tensors.  The last unary bit matches \(\delta_{ij}\) on ten
representative cells, with signature `0000110000`, but this is bounded
evidence only.

Consequently finite rank, infinite rank, a finite quotient, and an
infinite-Hankel-rank family in the complete anchored image all remain open.
The period-two lift, stable Andrews--Curtis, and Andrews--Curtis remain open
as well.  The follow-up is an exact documented-open boundary, not a completed
rank theorem.
