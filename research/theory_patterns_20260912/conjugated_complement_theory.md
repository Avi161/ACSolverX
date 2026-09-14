# Cyclic attachments for a conjugated cyclic complement

Status: proposed finite criterion, with a complete proof argument below;
independent proof challenge is still pending. No universal claim about
unimodular or trivial-group presentations is made.

Let R,S be nonempty cyclically reduced words in F(x,y), and assume their
combined alphabet support contains both x and y. Write C_R,C_S for the two
disjoint labelled cycles reading R,S, with their original starting vertices.
For a vertex u of C_R choose a path p from its start to u, and similarly
choose q from the start of C_S to a vertex v. Paths may run in either direction.

**Finite cyclic-attachment criterion.** The following are equivalent:

1. There exist arbitrary words c,w with `<R,c^-1 S c,w>=F(x,y)`.
2. For some vertices u,v, the subgroup
   `<R,(q p^-1)^-1 S(q p^-1)>` has a cyclic join complement.
3. For some cyclic rotations R',S' of R,S, `<R',S'>` has a cyclic join
   complement.

Thus one may test finitely many attachments (at most |R||S|), applying the
ordinary finite cyclic-complement criterion after each attachment. Choosing
shortest paths on the two cycles gives a successful conjugator of length at
most `floor(|R|/2)+floor(|S|/2)`, whenever any conjugator succeeds.
This bound concerns existence with an unrestricted extra word w; it is not a
claim that every conjugated subgroup has a short conjugate representative.

The exact fixed-subgroup complement test used here is
[Delgado–Silva, Lemma 5.3 and Theorem 5.4](https://gcc.episciences.org/6059/pdf).
For a folded core with more than one vertex, a single additional generator
can produce the full rose precisely when some pair of its vertices can be
identified and folded to that rose. The one-vertex cases are handled
separately. The extension from a fixed subgroup to two freely attached
cyclic components is the argument below, not a theorem attributed to that
paper.

## Necessity: a relative-rank argument

Start with the disjoint union Sigma=C_R disjoint-union C_S. Given a witness
c,w for statement 1, connect the two original starting vertices by a path
labelled c^-1, and attach at the R basepoint a loop labelled w. Call the
resulting connected graph Delta. It folds and cores to the full x/y rose.
Initially `rank(Sigma)=2` and `rank(Delta)<=3`, so the excess cycle rank

    e = rank(Delta)-rank(Sigma)

is at most one. If c is empty, one may use a two-edge connecting path labelled
`xX` with distinct endpoints before folding, so the initial old cycles remain
disjoint; its first fold gives the required cross-identification. If w is
empty, omit its loop and the initial excess is zero instead of one.

Maintain the image of Sigma as a labelled subgraph of Delta. Whenever this
image is nondeterministic, perform its folds also in Delta. Open folds
preserve both cycle ranks and closed folds lower both by one. Hence these
folds preserve e. While Sigma is separately folded on each component,
perform every available fold that does not identify two distinct vertices
of Sigma; these folds preserve the embedding of Sigma and cannot increase e.
Core trimming removes only edges outside Sigma and does not increase e.
Indeed, every old edge lies on an image of the old R or S cycle. Its label
remains the same cyclically reduced word throughout folding, so this is a
reduced closed path and none of its edges can lie in a removable hanging
tree. Full alphabet support alone would not justify that assertion without
the cyclic-reduction hypothesis.

If more old vertices must be identified, take the next fold that identifies
two distinct vertices of Sigma. At least one of the folded arcs lies outside
Sigma: otherwise its deterministic components would already admit the fold.
This is an open fold of Delta, so Delta loses one vertex and one edge and its
rank stays fixed. The image of Sigma loses one vertex and no edge at this
step. There are two possibilities:

* The two vertices lie in the same Sigma component. Its cycle rank rises by
  one, so e decreases by one.
* They lie in different Sigma components. Its component count and vertex
  count both drop by one, so its cycle rank and e stay unchanged.

The rank of a subgraph, even a disconnected subgraph, cannot exceed the rank
of the containing connected graph. Thus e is always nonnegative. There can
be at most one old-vertex identification of the first kind throughout the
process. There is exactly one component-joining identification: the two
nonempty old cycles have the same single image vertex in the final rose,
and after their images become connected they remain connected.

All additional vertex identifications forced by folds inside Sigma are free
fold consequences of these selected identifications. A fold creates no new
vertices. Therefore the final image of Sigma is the fold of the original
disjoint cycles after at most two chosen identifications: one cross-component
pair and at most one other pair. Because the combined old alphabet support
is the whole ambient alphabet, this final image is itself the full rose;
no missing generator loop has to be supplied solely by the extra w edges.

An identification selected later has original-vertex preimages. Choose them.
Identifying two specified pairs in a finite labelled graph commutes, and
folding their quotient is confluent. Hence the cross-component pair can be
performed first. After it, the remaining identification (if any) is between
vertices of a connected graph and is realized by adjoining one root-path
word. If that pair has already coalesced under folding, no additional word
is needed. This proves statement 2. The second pair is allowed to have
preimages in either or both original cycles; it is not restricted to one
cycle.

This argument is a two-component version of the old-subgraph-preserving
fold strategy in Delgado–Silva, Lemma 3.13. It does not assume that every
extra edge initially belongs to one of the old cycles. Such edges contribute
to Delta; their possible cycle rank is precisely what e bounds. The full
alphabet-support hypothesis handles the possible residual new-label loops.

## Sufficiency and explicit words

Identify u in C_R with v in C_S. The path from the original R start to the
original S start now reads `p q^-1`. Thus the based subgroup of this connected
graph is exactly

    H_uv = <R, p q^-1 S q p^-1>,

which has c=`q p^-1` in the stated convention. A complement returned by the
fixed-subgroup test is checked by folding `<R,c^-1 S c,w>` to the full rose.
This proves sufficiency with exact free words.

Alternatively, put the basepoint at the glued vertex. The two loop words
are the rotations `p^-1 R p` and `q^-1 S q`. If their cyclic complement is
w', conjugating the full tuple by p^-1 in the opposite direction fixes R
and gives the witness `(c,w)=(q p^-1,p w' p^-1)`. Shortest paths on the
cycles yield the displayed conjugator bound. Extra turns around a cycle
only change generating words within the same attached subgroup.

The condition is invariant under simultaneous conjugation of all three
generators of the subgroup. Therefore a common conjugation can first make
R cyclically reduced; the independent conjugator parameter absorbs the
normalization of S. Explicitly, if `R=alpha R0 alpha^-1` and
`S=beta S0 beta^-1`, a witness `(c0,w0)` for the cyclic cores transports to
`(c,w)=(beta c0 alpha^-1,alpha w0 alpha^-1)`. Thus the conjugator bound gains
`|alpha|+|beta|` for noncyclic input spellings. Empty words and cases missing an
ambient generator from the combined support are outside this theorem as
stated and must be treated separately rather than silently accepted by it.

## Certificate and algorithmic scope

The relative conjugation of S is an ordinary AC3 prefix, expanded letter by
letter. The word w proves an exact subgroup-generating statement only after
an independent full-rose check. On the known trivial-group inputs, using this
as a stable simplification still requires the stable-composite realization
and its requested certificate work. A positive graph result is therefore a
stable-criterion candidate, never an automatic ordinary solve.

A capped run of the attachment enumeration is not a complete negative.
Every tested fixed subgroup has its own exact or capped result, and the
budget must count all actual vertex-pair identifications across all
attachments of that input. Cyclic or automorphism canonicalization of the
two relators independently would erase the relative attachment and must not
be used for subgroup deduplication; only exact folded rooted graphs may be
reused.

## Controls and the capped twenty-row experiment

`conjugated_complement_probe.py --mode controls` checked seven finite
attachment examples, including the full basis, separate powers, full-support
nonprimitive examples, missing-support cases kept outside the theorem, and
AK(2). It also tested all 17 reduced conjugators of length at most two on six
of those controls. Every positive has an explicit conjugator/complement and
a full-rose check using both the union-find and independent partition folders.
No short-conjugator counterexample to the finite criterion was found where
the attachment test completed. These are soundness controls, not a proof of
the necessity direction. AK(2) reached its cap and has no negative conclusion.

The exact fixed twenty inputs are read from `prepared_frames_panel20.jsonl`.
Each input received one run with at most 1,000 actual vertex identifications,
shared across every relative attachment. Previously audited literal-root
graphs were reused without repeating their negative checks. The process was
serial with 0.1 seconds of cooling after each input. Exactly 20,000 new
identifications were performed, no positive was found, and all twenty inputs
remain unknown at the cap. None has a complete negative attachment result.

The detailed attempts are in `conjugated_complement_panel20.jsonl`; its JSON
summary preserves input/source hashes, exact per-input counts, completeness
flags and the empty positive list. The control records are in
`conjugated_complement_controls.json`. One control's label was corrected
afterward: it had mistakenly included “unimodular” although its determinant
is -6. Its words and all outcomes are unchanged. The exact executed source
is preserved as `conjugated_complement_probe_run_snapshot.py`, and the
metadata correction is explicitly recorded. No panel or control computation
was repeated to make that correction.
