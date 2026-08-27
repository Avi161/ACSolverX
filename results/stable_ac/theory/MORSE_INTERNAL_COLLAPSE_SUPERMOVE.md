# Morse Internal-Collapse Supermove

Date: 2026-08-16

Status: theorem-level mechanism verified; exact `aca_115` branch replayed and
certified outside the automorphism orbit of the natural stabilization.

## The move

Let

\[
P=\langle x_1,\ldots,x_n\mid r_1,\ldots,r_n\rangle
\]

be a balanced presentation.  Form the barycentric subdivision \(K'_P\) of
its presentation 2-complex.  A certificate is an acyclic matching \(M\) on
the face poset of \(K'_P\) with exactly one critical 0-cell.

Write the unmatched 1-cells as \(a_1,\ldots,a_q\), and the unmatched
2-cells as \(e_1,\ldots,e_q\).  The exact target is

\[
P\longmapsto Q_M(P)=
\langle a_1,\ldots,a_q\mid \partial_M e_1,\ldots,\partial_M e_q\rangle .
\]

The words \(\partial_Me_j\) are not guessed.  They are computed as follows.

1. Every matched 0-cell/1-cell pair belongs to a spanning tree; its matched
   1-cell is erased from attaching words.
2. For every matched 1-cell/2-cell pair \((a,e)\), cyclically orient
   \(\partial e=u a^\epsilon v\), where this occurrence of \(a\) is unique.
   Record the gradient rewrite
   \[
   a=(u^{-1}v^{-1})^\epsilon .
   \]
3. Recursively apply these rewrites to the attaching word of every critical
   2-cell and freely reduce.

The reversed matched Hasse graph must be acyclic.  That condition makes the
recursive rewrites terminate and makes their result independent of the order
of the matched 1-cell/2-cell pairs.

Fernández's Theorems 2.8 and 2.9 prove

\[
P\sim_{Q^{**}}Q_M(P).
\]

The proof is geometric: the matching gives internal collapses of the regular
complex \(K'_P\), hence a 3-deformation to the Morse complex.  It is not a
sequence of CoV corridors.  The matching and its topological order are a
compact structural certificate; expanding the corresponding 3-deformation
can be much larger.

This constructor applies mechanically to every one of the 124 stored
presentations: each finite relator tuple has a finite subdivided face poset,
and at minimum the spanning-tree matching exists.  Not every matching is
useful and many outputs are automorphic; usefulness is decided only after the
endpoint has been constructed.  The theorem does not assume that a CoV word
or an isolating relator has already been found.

## Relation to Lemma 11

The local rewrite in the Morse constructor is analogous to the
unique-occurrence step used by Lemma 11.  If a matched triangular relator is
\(u a^\epsilon v\) with one occurrence of \(a\), its rewrite is

\[
a=(u^{-1}v^{-1})^\epsilon
\]

and it is substituted into the remaining attaching words before the pair is
deleted.  Each matched triangular 1-cell/2-cell pair is already a
unique-occurrence pair in the initial subdivided presentation.

This does **not** make the theorem a formal generalization or dominance result
over Lemma 11.  Its different source of leverage is the global barycentric
expansion plus a compatible acyclic matching: one compact matching certifies
an internal 3-deformation of the whole complex.  The `aca_115` source has no
literal defining relator in its displayed rank-two words, while the certified
subdivision matching has 27 compatible pairs and changes the whole cell
structure.  That global topological certificate—not a claim that the local
rewrite is new—is the out-of-the-box mechanism.

## Exact `aca_115` branch

The corpus state is

\[
P=\langle x,y\mid \texttt{YXYxyx},\ \texttt{YYYYxxx}\rangle .
\]

This is the canonical `aca_115` representative.  Its subdivided presentation
complex has 61 cells and 138 cover relations.  The certificate in
`morse_aca115_certificate.py` stores all 27 matching pairs.  Reversing those
27 Hasse edges gives an acyclic graph; the stored deterministic topological
order contains all 61 cells.  The critical cells have counts

\[
(c_0,c_1,c_2)=(1,3,3).
\]

Relabel the critical 1-cells

\[
\texttt{c1_0_4}\mapsto x,\qquad
\texttt{c2_x1_3}\mapsto y,\qquad
\texttt{c2_y1_1}\mapsto z.
\]

The three critical 2-cell boundaries give the exact target

\[
Q=\left\langle x,y,z\ \middle|\
\texttt{YzxxYzX},\
\texttt{YzYzY},\
\texttt{YzxYzzxYzxYzx}
\right\rangle .
\]

The exponent-sum determinant of \(Q\) is \(+1\).  No generator occurs exactly
once in any displayed target relator, so this output is not a literal
add-and-delete stabilization.

This branch is not advertised as a one-step shortening: its raw total length
is 25.  Its verified advantage is different.  The source has entered a new
rank-three automorphism orbit through a 61-cell global certificate, and after
two rank-three Whitehead changes the endpoint contains the length-three
relation `ZYY`.  A local substitution move only acts on selected literal
word occurrences; it does not enumerate these global acyclic matchings or
their gradient paths.  Whether the new short direction helps a later solver
is an empirical search question, not part of the soundness proof.

There is also a limitation that must be visible.  The second and third target
relators are individually primitive: independent rank-three Whitehead
reductions take each to a one-letter word.  If either is exposed by a Nielsen
change and then deleted, the resulting rank-two tuple has the same complete
\(\operatorname{Aut}(F_2)\) canonical form as the source.  Thus this particular
branch is a certified mechanism/orbit-escape witness, not a solution of
`aca_115`, not a total-length improvement, and not evidence that every later
primitive direction is useful.  The supermove is the raw arrow \(P\to Q\),
not the primitive deletion that follows it.

## Exact non-automorphism certificate

Because the ranks differ, comparing \(P\) directly with \(Q\) would be too
easy.  Compare instead with the natural rank-three stabilization

\[
P^+=\langle x,y,z\mid
\texttt{YXYxyx},\ \texttt{YYYYxxx},\ \texttt{z}\rangle .
\]

Its total cyclic length is 14.  Exhaustive Whitehead-graph cut evaluation
has minimum length-change 0, so its exact \(\operatorname{Aut}(F_3)\) floor is
14.

For \(Q\), apply the two verified Whitehead automorphisms

\[
\begin{array}{lll}
\phi_0:&x\mapsto z^{-1}xz,&y\mapsto yz,&z\mapsto z,\\
\phi_1:&x\mapsto xy,&y\mapsto y,&z\mapsto y^{-1}z.
\end{array}
\]

They give

\[
\begin{aligned}
Q&\xrightarrow{\phi_0}
(\texttt{YxxYX},\texttt{ZYYY},\texttt{YxYzxYxYx})\\
&\xrightarrow{\phi_1}
(\texttt{YxyxYX},\texttt{ZYY},\texttt{xYzxxx}).
\end{aligned}
\]

The last tuple has total cyclic length 15, and a separately implemented
Whitehead-graph cut enumeration again gives minimum change 0.  Hence

\[
\lambda(P^+)=14\ne15=\lambda(Q).
\]

Therefore no automorphism of \(F_3\), even after independent cyclic
conjugation/inversion and relator permutation, carries \(P^+\) to \(Q\).
This is a genuine orbit escape generated by the matching, not by a
post-generation claim that the words merely look different.

Some other matchings do return automorphic states.  That is harmless: exact
Whitehead filtering may discard them.  A useful supermove family needs one
certified escaping branch, not a majority of escaping branches.

## Bound

Let \(n\) be the generator count, \(m\) the relator count, and \(k\) the total
relator length.  Fernández Remark 2.11 gives the structural bound

\[
O(n+m)+O(k)+O(k^2)
\]

on the number of \(Q^{**}\)-transformations that construct the Morse
presentation; computing its words is \(O(k)\).  This is the useful compressed
bound attached to the matching certificate.

Fernández's convention permits a simultaneous ambient free-group
automorphism as a \(Q^{**}\) operation.  On a trusted trivial presentation,
the relators normally generate the ambient free group, so the basic
substitution principle compiles such an automorphism into project AC moves.
The elementary project-SAC count is therefore finite, but it depends on
normal-closure witnesses not supplied by the matching alone.  Two honest
forms of the stronger ceiling are:

1. with explicit normal factorizations, sum their conjugate-factor replay
   costs together with the displayed collapse ledger;
2. without those witnesses, fix a prefix-free universal machine \(U\).  Use
   the finite atomic alphabet consisting of relator inversion, an ordered
   relator product, conjugation by one declared generator or its inverse, and
   canonical stabilization/destabilization.  Presentations and the matching
   use a fixed self-delimiting serialization.  At every state the branching is
   finite.  A fixed program `search_U(P,Q)` breadth-first enumerates atomic
   move strings and halts when the freely reduced tuple equals \(Q\).  The
   theorem proves that it halts, and therefore
   \[
   d_{SAC}(P,Q)\le
   \operatorname{runtime}(\texttt{search}_U(P,Q))
   \le BB_U(|\texttt{search}_U(P,Q)|)
   \le BB_U(c_U+|\operatorname{enc}(P,Q,M)|).
   \]

   The last inequality uses the fixed search interpreter of length \(c_U\)
   followed by the self-delimiting data block \(\operatorname{enc}(P,Q,M)\).

The second is rigorous and deliberately noncomputable.  It must not be
misreported as an effective numerical estimate.

## Verification

- `experiments/stable_ac/supermoves/morse_internal_collapse.py` constructs
  the exact subdivided poset, checks the matching, and computes the endpoint.
- `experiments/stable_ac/supermoves/morse_aca115_certificate.py` stores the
  complete matching and replays the structural and Whitehead certificates.
- `tests/stable_ac/test_morse_internal_collapse.py` checks the 61 cells, 138
  covers, 27 matching pairs, critical cells, endpoint words, determinant,
  topological-order digest, Whitehead path, and both minimality cuts.

Verified command:

```text
UV_CACHE_DIR=.scratch/uv-cache uv run --offline --with pytest \
  python -m pytest tests/stable_ac/test_morse_internal_collapse.py -q
```

Result: `4 passed`.

## Sources

- Ximena Fernández, *Morse theory for group presentations*, Transactions of
  the AMS 377 (2024), Theorems 2.8--2.9, Definition 2.6, Remark 2.11.
- The author's `Finite-Topological-Spaces` reference implementation was used
  as an independent preflight: the port reproduces the stored MS(3) notebook
  matching and endpoint relators up to the recorded generator bijection and
  relator order.
