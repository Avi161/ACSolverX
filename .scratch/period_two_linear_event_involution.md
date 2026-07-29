# A uniform event involution for the full unary residual

Date: 2026-07-29

## Status

There is a uniform, label-preserving, fixed-point-free involution on the
literal Schreier events of each full endpoint residual

\[
  \mathcal R(B+H(y_{ij})),\qquad i,j\geq 0,
\]

and hence on each of the three difference words in Section 4 of
`direct_unary_identity.md`.  The construction below uses all sixteen
correction occurrences and the canonical section of the merged current
\(B_s+H(y_{ij})_s\).  It does not split the actual section into a base word
followed by a direction word.

The construction has three layers.

1. Every raw transported relation-generator atom has a canonical local
   mirror matching, leaving exactly its one signed linear event.
2. Before canonical merging, the linear events of \(H(y_{ij})\) have an
   explicit path-by-path matching induced by the canonical boundary pairing
   and the unique source-tree flow.  The fixed literals and the eight base
   atoms have the finite pinned matching in Section 4.
3. Canonical merging can cancel a base atom against a flow atom, or two flow
   atoms against each other.  Alternating-path surgery through precisely
   those canceled virtual atoms transfers the two virtual matchings to the
   actual merged section.

The third layer is necessary.  A disjoint matching of the *actual* base and
actual direction survivors is false already at \(D_{00}=H(y_{00})\):

\[
 B_3(\texttt{TTct})=-1,\qquad
 D_{00,3}(\texttt{TTct})=+1,\qquad
 (B_3+D_{00,3})(\texttt{TTct})=0.                 \tag{0.1}
\]

Thus the direction atom required by the source-tree matching is not an
actual atom of the merged section.  Section 5 gives the exact two-label
obstruction and the alternating-path repair.

This proves the involution obligation (5.2) of `direct_unary_identity.md`.
It does **not** compute its heterochromatic crossing parity.  The all-index
identities for \(I_{ij}\), \(J_{ij}\), and \(u_{ij}=\delta_{ij}\) remain
open.

No index grid, census, or search is used.  Two constant-size structural
replays are recorded only to pin the fixed matching and the first source
flow.

## 1. Exact occurrence and event conventions

Let \(\mathcal O=\{1,\ldots,16\}\).  For \(o\in\mathcal O\), write
\((s_o,p_o,q_o)\) for its slot, polarity, and quotient prefix.  The exact
table is

| \(o\) | \(s_o\) | \(p_o\) | \(q_o\) |
|---:|---:|---:|---|
| 1 | 2 | + | `eps` |
| 2 | 1 | + | `tc` |
| 3 | 0 | + | `tc` |
| 4 | 0 | - | `ctcTTTcttc` |
| 5 | 1 | - | `ctcTctt` |
| 6 | 2 | - | `ctcTcTctc` |
| 7 | 0 | + | `ctcTcTctc` |
| 8 | 0 | - | `ctcTTTTcttc` |
| 9 | 3 | + | `ctcTTctt` |
| 10 | 1 | + | `ctcTctc` |
| 11 | 0 | + | `ctcTctc` |
| 12 | 0 | - | `cTTcttc` |
| 13 | 1 | - | `tt` |
| 14 | 3 | - | `t` |
| 15 | 4 | + | `t` |
| 16 | 4 | - | `eps` |

This is the literal `_residual_ast` occurrence order.  In particular, slot
one is retained even though the anchored direction has zero slot-one
current.  The occurrence operators are

\[
 O_s=\sum_{o:s_o=s}p_oq_o,                         \tag{1.1}
\]

and the certificate checks integrally that these are exactly the five
operators used by `correction_image`.

For a correction current \(C_s\), an actual atom has provenance

\[
  (o,s,v,k),\qquad
  1\leq k\leq |C_s(v)|.                            \tag{1.2}
\]

The support is in shortlex order, copies are in increasing \(k\), and a
negative occurrence reverses the complete atom list and inverts every atom.
Its linear-event label and sign are

\[
 \ell(o,v)=\operatorname{cvert}(q_ov),\qquad
 \sigma(o,v)=p_o\operatorname{sgn}C_s(v).          \tag{1.3}
\]

Formula (1.3) is a conclusion of the local raw matching below, not a
replacement of the raw word.  Chronology remains the literal order:
occurrence order, occurrence polarity, merged shortlex support, copy order,
and raw-letter order.

## 2. Local raw matching for one transported atom

Fix one of the seventeen occurrence actions \(q\), a canonical module
vertex \(v\), and a positive atom.  The approved raw bridge gives a unique
maximal-overlap branch and a word \(z=z(q,v)\) such that

\[
 \operatorname{red}(qvccv^{-1}q^{-1})
   =zccz^{-1}.                                     \tag{2.1}
\]

The terminal branch includes the proved `tau` deletion, so \(z\) does not
end in positive \(c\).  Let \(x=\operatorname{cvert}([z])\), and perform
the literal Reidemeister--Schreier scan of \(z\).  Its factorization relative
to the canonical quotient section is

\[
 z=k_z\widehat x,\qquad k_z\in K.                  \tag{2.2}
\]

If the chronological Schreier-event word of \(k_z\) is
\(a_1\cdots a_m\), then the complete event word of (2.1) is

\[
 a_1\cdots a_m\;r_x\;a_m^{-1}\cdots a_1^{-1}.     \tag{2.3}
\]

This is an equality of literal event streams: canonical \(q\) has no
Schreier event of its own, and the bridge retained every event created by
the quotient reduction of \(qv\).  Pair the event in \(a_r\) with the
mirror event in \(a_r^{-1}\).  They have the same post-`c_vertex` label and
opposite raw signs.  The only unpaired event is the central \(r_x\), whose
label is

\[
 x=\operatorname{cvert}(qv).                       \tag{2.4}
\]

For a negative atom, reverse and invert (2.3), use the same mirror pairs,
and retain the central event with sign \(-1\).  Thus every atom has a
chronology-preserving local involution on all of its noncentral events and
one survivor with exactly (1.3).  The provenance of a local raw pair is

\[
 (o,s,v,k,r)\longleftrightarrow(o,s,v,k,r^*),       \tag{2.5}
\]

where \(r,r^*\) are the two raw emitting positions belonging to the
mirrored \(a_h,a_h^{-1}\) in (2.3).  The unique central raw position is the
second positive \(c\) in the positive atom and the first negative \(c\) in
the inverse atom after the bridge's `tau` normalization.

This proves part (A): local matching preserves the actual raw chronology and
final labels while retaining exactly the translated linear event.

## 3. Explicit source-tree matching before canonical merging

Put

\[
 y=y_{ij}=p^{-1}\gamma^{\,i-j}c\gamma^{-(i+1)}t,
 \qquad S_y=e_y+2e_T.                              \tag{3.1}
\]

The exact source theorem gives `source_scalar(y)=-2` for every \(i,j\), so
the two orbit sums of \(O_0S_y\) vanish.  We now refine the source-flow
construction to event provenance.

### 3.1 Boundary tokens

For each coefficient copy \((a,k)\) of \(S_y\) and each slot-zero
occurrence \(o\), create the token

\[
 b=(S,a,k,o),\quad
 \ell(b)=\operatorname{cvert}(q_oa),\quad
 \sigma(b)=p_o.                                   \tag{3.2}
\]

There are \(6+2\cdot6=18\) tokens before collisions.  At each label, first
pair opposite-sign tokens in increasing provenance order.  These are
already label-preserving source pairs.  After deleting them, sort the
remaining negative and positive tokens in each of the two source-tree
components exactly as `paired_boundaries` does, breaking duplicate-label
ties by \((a,k,o)\), and pair the \(h\)-th negative token with the \(h\)-th
positive token.  Call such a boundary pair

\[
 b^-_r=(S,a^-,k^-,o^-),\qquad
 b^+_r=(S,a^+,k^+,o^+).                            \tag{3.3}
\]

This is an explicit provenance refinement of the certificate's canonical
boundary pairing.  Vanishing of the two orbit sums proves equality of the
two list lengths; it is not being used as an abstract same-label matching.

### 3.2 Unique tree paths and chain pairs

Let

\[
 v_{r,0}\xrightarrow{e_{r,1}}v_{r,1}
 \longrightarrow\cdots\longrightarrow
 v_{r,m_r}                                        \tag{3.4}
\]

be the unique source-tree path from
\(v_{r,0}=\ell(b^-_r)\) to \(v_{r,m_r}=\ell(b^+_r)\).  The path is the
literal `rewrite.path_between` path used by
`build_l0_direction_from_pairs`; uniqueness is the proved finite-tree-flow
theorem, not a choice made from coefficient cancellation.

For an edge \(e_{r,h}\), the exact incidence rule creates one elementary
atom

\[
 A_{r,h}=(r,h,s_{r,h},w_{r,h},\eta_{r,h})          \tag{3.5}
\]

in slot \(s_{r,h}\in\{2,3,4\}\).  Since each of \(O_2,O_3,O_4\) is a
binomial, applying the two occurrences of that slot to (3.5) creates
exactly two central survivor events.  The live incidence identities in the
raw manifest prove that their labels are precisely

\[
 \{v_{r,h-1},v_{r,h}\}.                            \tag{3.6}
\]

The event provenance is

\[
  (P,r,h,e_{r,h},o),\qquad o\in\mathcal O,\ s_o=s_{r,h}.  \tag{3.7}
\]

Trivial vertex stabilizers make the two labels in (3.6) distinct, hence
identify unambiguously which of the two occurrence events is the initial
and which is the terminal endpoint of the edge.

Match the following pairs:

\[
\begin{aligned}
 b^-_r&\longleftrightarrow(P,r,1,e_{r,1},o_{\rm initial}),\\
 (P,r,h,e_{r,h},o_{\rm terminal})
   &\longleftrightarrow
   (P,r,h+1,e_{r,h+1},o_{\rm initial})
       &&(1\leq h<m_r),\\
 (P,r,m_r,e_{r,m_r},o_{\rm terminal})
   &\longleftrightarrow b^+_r.
                                                               \tag{3.8}
\end{aligned}
\]

Every pair in (3.8) has the displayed common tree vertex as its exact final
post-`c_vertex` label.  Every boundary token and every elementary edge-event
survivor occurs once.  Together with the immediate collision pairs in
Section 3.1, (3.8) is therefore a fixed-point-free perfect matching
\(M_F\) of all *virtual* direction survivors.

The construction is uniform in \((i,j)\).  Its inputs are the raw formula
(3.1), the eighteen occurrence tokens, the canonical boundary sort, and
the unique tree path.  The approved `W:*`, `A:*`, and endpoint records in
the raw manifest are an all-index factorized enumeration of the same
currents; their `current_equality` records identify each manifest row with
the elementary atom (3.5).  No bounded path table is used as the proof.

As a structural pin only, \(y_{00}\) gives nine canonical boundary paths,
113 tree edges, 244 virtual survivor events, and 122 pairs in (3.8).  Direct
checking of every edge found its two occurrence labels equal to its two
tree endpoints.  This replay is not used for the all-index conclusion.

This proves part (B) at the correct virtual resolution: the matching is the
explicit chain matching of the unique source flow, not an arbitrary pairing
deduced from `correction_image(F)=0`.

## 4. Finite pinned matching for the fixed residual

Set all five correction currents to zero and scan the expanded literal AST.
Number expanded leaves exactly as `_expand(_residual_ast())` does, including
correction leaves in the numbering.  A raw event ID `Lh:rk` means raw
position \(k\) of expanded literal leaf \(h\).

The literal scan emits 70 events.  The following six adjacent inverse
Schreier pairs are removed by the deterministic stack matching:

| label | first | second |
|---|---|---|
| `t` | `L3:r18` | `L7:r1` |
| `ctcTTTctt` | `L9:r7` | `L11:r1` |
| `ctcTcTct` | `L14:r6` | `L17:r1` |
| `ctcTTTTctt` | `L19:r7` | `L21:r1` |
| `ctcTct` | `L24:r18` | `L28:r1` |
| `cTTctt` | `L30:r7` | `L32:r1` |

This leaves 58 fixed-literal survivors `X01` through `X58` in chronological
order.  Their raw IDs appear in the table below.  All literal-source,
quotient-section, and \(\Omega\)-events are included here: at raw-word
resolution there is no separate conceptual \(\Omega\) event to omit.

For a base event, `B:oH:bR:kK` means occurrence \(H\), zero-based
`CORRECTION` row \(R\), and coefficient copy \(K\).  Expanding the eight
base rows through all applicable occurrences gives 52 central survivors.
The following 55 pairs match all 110 base-plus-fixed survivors.  The second
and third columns are respectively the positive and negative event; the
first column is their common exact label.

| # | label | positive provenance | negative provenance |
|---:|---|---|---|
| 1 | `eps` | `B:o12:b2:k1` | `X05/L3:r15` |
| 2 | `eps` | `B:o12:b2:k2` | `X10/L8:r14` |
| 3 | `eps` | `B:o3:b0:k1` | `X11/L8:r16` |
| 4 | `eps` | `B:o3:b0:k2` | `X56/L32:r16` |
| 5 | `t` | `B:o14:b5:k1` | `X57/L32:r19` |
| 6 | `t` | `B:o14:b5:k2` | `X58/L32:r21` |
| 7 | `cT` | `B:o12:b1:k1` | `X54/L32:r10` |
| 8 | `cT` | `B:o12:b1:k2` | `X55/L32:r12` |
| 9 | `ct` | `B:o15:b7:k1` | `X12/L8:r18` |
| 10 | `Tct` | `B:o14:b6:k1` | `B:o16:b7:k1` |
| 11 | `Tct` | `X08/L8:r8` | `B:o3:b1:k1` |
| 12 | `Tct` | `X09/L8:r10` | `B:o3:b1:k2` |
| 13 | `cTT` | `X53/L32:r8` | `X50/L30:r4` |
| 14 | `Tctt` | `X06/L8:r3` | `B:o3:b2:k1` |
| 15 | `Tctt` | `X07/L8:r5` | `B:o3:b2:k2` |
| 16 | `cTct` | `X03/L3:r8` | `B:o1:b3:k1` |
| 17 | `cTct` | `X04/L3:r10` | `B:o1:b3:k2` |
| 18 | `ctcT` | `B:o11:b0:k1` | `B:o9:b6:k1` |
| 19 | `ctcT` | `B:o11:b0:k2` | `X19/L11:r15` |
| 20 | `ctcT` | `B:o4:b2:k1` | `X20/L11:r17` |
| 21 | `ctcT` | `B:o4:b2:k2` | `X43/L24:r14` |
| 22 | `ctcT` | `B:o6:b3:k1` | `X44/L24:r16` |
| 23 | `ctcT` | `B:o6:b3:k2` | `X49/L29:r15` |
| 24 | `cTTct` | `X51/L32:r4` | `B:o12:b0:k1` |
| 25 | `cTTct` | `X52/L32:r6` | `B:o12:b0:k2` |
| 26 | `cTctt` | `X01/L3:r3` | `B:o1:b4:k1` |
| 27 | `cTctt` | `X02/L3:r5` | `B:o1:b4:k2` |
| 28 | `ctcTT` | `B:o4:b1:k1` | `X17/L11:r10` |
| 29 | `ctcTT` | `B:o4:b1:k2` | `X18/L11:r12` |
| 30 | `ctcTT` | `B:o8:b2:k1` | `X35/L21:r15` |
| 31 | `ctcTT` | `B:o8:b2:k2` | `X36/L21:r17` |
| 32 | `ctcTTT` | `B:o8:b1:k1` | `X13/L9:r4` |
| 33 | `ctcTTT` | `B:o8:b1:k2` | `X33/L21:r10` |
| 34 | `ctcTTT` | `X16/L11:r8` | `X34/L21:r12` |
| 35 | `ctcTcT` | `B:o7:b0:k1` | `X23/L14:r4` |
| 36 | `ctcTcT` | `B:o7:b0:k2` | `X28/L18:r15` |
| 37 | `ctcTct` | `B:o6:b4:k1` | `X21/L11:r19` |
| 38 | `ctcTct` | `B:o6:b4:k2` | `X22/L11:r21` |
| 39 | `ctcTTTT` | `X32/L21:r8` | `X29/L19:r4` |
| 40 | `ctcTTct` | `X41/L24:r8` | `X37/L21:r19` |
| 41 | `ctcTTct` | `X42/L24:r10` | `X38/L21:r21` |
| 42 | `ctcTTTct` | `X14/L11:r4` | `B:o4:b0:k1` |
| 43 | `ctcTTTct` | `X15/L11:r6` | `B:o4:b0:k2` |
| 44 | `ctcTTctt` | `X39/L24:r3` | `B:o9:b5:k1` |
| 45 | `ctcTTctt` | `X40/L24:r5` | `B:o9:b5:k2` |
| 46 | `ctcTcTct` | `X47/L29:r8` | `B:o11:b1:k1` |
| 47 | `ctcTcTct` | `X48/L29:r10` | `B:o11:b1:k2` |
| 48 | `ctcTTTTct` | `X30/L21:r4` | `B:o8:b0:k1` |
| 49 | `ctcTTTTct` | `X31/L21:r6` | `B:o8:b0:k2` |
| 50 | `ctcTcTctt` | `X45/L29:r3` | `B:o11:b2:k1` |
| 51 | `ctcTcTctt` | `X46/L29:r5` | `B:o11:b2:k2` |
| 52 | `ctcTcTcTct` | `X26/L18:r8` | `B:o7:b1:k1` |
| 53 | `ctcTcTcTct` | `X27/L18:r10` | `B:o7:b1:k2` |
| 54 | `ctcTcTcTctt` | `X24/L18:r3` | `B:o7:b2:k1` |
| 55 | `ctcTcTcTctt` | `X25/L18:r5` | `B:o7:b2:k2` |

The canonical tab-separated payload `(label, positive, negative)` has
SHA-256

```text
04da0623e78555f7204c3a4f4e262e3bc310576d379f08f94bf6642ab5d33cac
```

Every row has equal post-`c_vertex` labels and opposite signs; every one of
the 58 literal and 52 base events occurs exactly once.  This is the requested
finite pinned event proof of

\[
 d+\operatorname{im}(B)=0,                         \tag{4.1}
\]

not merely a comparison of aggregated coefficient dictionaries.  Call this
matching \(M_0\).

## 5. Why direct base/flow separation fails

The full endpoint does not contain the disjoint union of the events matched
by \(M_0\) and \(M_F\).  It contains the canonical section of the sum.
The smallest exact collision occurs at \(D_{00}\).  The live source-tree
construction gives

\[
 D_{00,3}(\texttt{TTct})=+1,                       \tag{5.1}
\]

whereas base row `b6` is

\[
 B_3(\texttt{TTct})=-1.                            \tag{5.2}
\]

The merged coefficient is zero, so neither atom is present at occurrences
9 and 14.  Those two occurrence labels are

\[
\begin{array}{c|c|c|c}
o&p_o&q_o&\operatorname{cvert}(q_o\texttt{TTct})\\ \hline
9&+&\texttt{ctcTTctt}&\texttt{ctcT}\\
14&-&\texttt{t}&\texttt{Tct}.
\end{array}                                        \tag{5.3}
\]

Equivalently,

\[
 O_3e_{\texttt{TTct}}
   =e_{\texttt{ctcT}}-e_{\texttt{Tct}}\ne0.       \tag{5.4}
\]

Before the merge, the full virtual direction multiset has even label
multiplicity because \(\operatorname{im}(D_{00})=0\).  Removing exactly the
two events in (5.3) leaves odd multiplicity at both `ctcT` and `Tct`.
Therefore the restriction of \(M_F\) to the surviving *actual direction
events* cannot be a label-preserving perfect matching.  Parts (B) and (C)
cannot be implemented as two disjoint matchings on actual events.

This refutes that stronger interpretation of the requested decomposition;
it does not refute the full involution.

## 6. Alternating-path descent to the merged section

We now transfer \(M_0\sqcup M_F\) to the actual merged atoms.

For a fixed endpoint, expand each current coefficient into elementary
tokens:

* the eight base-row copies;
* the two slot-zero source copies in (3.1); and
* every elementary tree-edge atom (3.5), before equal module vertices are
  aggregated.

For each slot \(s\) and module vertex \(v\), sort the positive elementary
tokens and the negative elementary tokens by their displayed provenance.
Pair the first

\[
 \min(N^+_{s,v},N^-_{s,v})                         \tag{6.1}
\]

tokens.  Replicate this cancellation at every occurrence \(o\) with
\(s_o=s\).  A cancellation edge therefore joins two virtual central events
with the same occurrence and vertex:

\[
 (o,s,v,\alpha)\longleftrightarrow(o,s,v,\beta).   \tag{6.2}
\]

It is label-preserving because both labels are exactly
\(\operatorname{cvert}(q_ov)\).  Call the union of these edges \(C\).
The unmatched elementary tokens all have one sign.  Map them in provenance
order to the copies \(k=1,\ldots,|(B_s+D_s)(v)|\) of the actual canonical
section.  At a negative occurrence the complete mapped list is reversed and
inverted, exactly as the literal AST requires.  Thus the vertices not met by
\(C\) are in canonical bijection with the actual central survivor events.

Consider the graph

\[
 \mathcal G=(\mathcal V,M_0\sqcup M_F\sqcup C),     \tag{6.3}
\]

where \(\mathcal V\) consists of the 58 fixed-literal survivors and all
virtual base and direction survivors.  A canceled correction vertex has
degree two, one edge from \(M_0\sqcup M_F\) and one from \(C\).  An actual
survivor or a fixed-literal survivor has degree one.  Consequently every
component is either

1. an alternating cycle consisting entirely of canceled virtual vertices;
   or
2. an alternating path with two distinct actual endpoints.

Every edge of (6.3) preserves its exact post-`c_vertex` label.  Therefore
all vertices in a component have one label.  Discard the cycles and match
the two endpoints of every path.  This defines

\[
 \iota_{ij}^{\rm cent}                              \tag{6.4}
\]

on all actual central correction survivors and fixed-literal survivors.
It is explicit: follow the unique alternating path in the graph defined by
the pinned tables, canonical source paths, and the deterministic merge sort.
It is fixed-point-free, involutive, label-preserving, and covers every
survivor exactly once.

Finally adjoin

* the local raw mirror pairs (2.5) inside every actual correction atom; and
* the six fixed-literal stack pairs in Section 4.

The union is the required involution

\[
 \boxed{
 \iota_{ij}:\mathcal E_{ij}\longrightarrow\mathcal E_{ij},\quad
 \iota_{ij}^2=1,\quad \iota_{ij}(e)\ne e,\quad
 \ell(\iota_{ij}(e))=\ell(e).
 }                                                     \tag{6.5}
\]

For a difference word
\(\mathcal R(F^+)\mathcal R(F^-)^{-1}\), construct (6.5) separately in
the forward endpoint and in the reversed, sign-inverted endpoint.  Reversal
conjugates the endpoint involution and does not change labels.  Their
disjoint union is therefore an involution on the complete difference-word
event set.  This applies to

\[
 (F^-,F^+)=(0,D_{00}),\quad
 (D_{ij},D_{i+1,j}),\quad
 (D_{ij},D_{i,j+1}).                                \tag{6.6}
\]

## 7. Uniformity and remaining proof boundary

The matching is uniform for all \(i,j\geq0\).  Parameter dependence occurs
only in

1. the exact raw word \(y_{ij}\);
2. the canonical boundary-token labels and their source-tree paths;
3. the elementary flow atoms read from those paths; and
4. the deterministic coefficient aggregation and shortlex merge.

No branch of the matching is selected by a desired crossing value.  The
construction uses the literal sixteen-occurrence AST, exact raw event labels,
the canonical source boundary pairing, unique tree paths, the pinned fixed
matching, and deterministic alternating-path surgery.

What is now proved:

* local raw defect events pair around one translated linear survivor;
* source-flow survivors have an explicit path-chain matching;
* the 58 fixed-literal and 52 base survivors have the pinned matching above;
* the naive disjoint actual base/flow matching fails at the exact collision
  (5.1)--(5.4); and
* alternating surgery gives the full merged-section involution (6.5).

What remains open is the chronology calculation.  The involution does not
reorder any event; crossings must be read in the actual merged shortlex
chronology.  One must still evaluate

\[
 \operatorname{cr}_{\ne}(\mathcal E_{ij};\iota_{ij})
\]

and prove the two all-index edge indicators and the seed relation required
by (4.4) of `direct_unary_identity.md`.  Thus this artifact closes the
matching-existence/provenance obstruction but not the delta identity or any
Andrews--Curtis conclusion.

## Hostile rereview

**APPROVE — zero load-bearing findings.**  An independent replay reconfirmed
the 70/6/58 fixed-literal split, all 52 base events and 55 pinned pairs, the
244-event \(y_{00}\) source-flow matching, and the alternating descent to the
actual merged survivors.  The referee also checked the ambient-prefix raw
palindrome, boundary pre-cancellation, negative-occurrence chronology,
endpoint inversion, and the stated open crossing/delta boundary.
