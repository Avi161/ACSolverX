# Direct prism-collapse route for AK3

Status: the exact construction and reference collapse are verified. The
single planned greedy attempt stops short of a point; its full trace is
retained below. No AK3 resolution is claimed. This positive-certificate
route is separate from the frozen class-two, thickening, and donor ledgers.

## Exact input complex

Use the presentation
\[
 P=\langle x,y\mid xxxYYYY,\ xyxYXY\rangle.
\]
It presents the trivial group: the braid relation makes $\Delta=xyx$
conjugate $x$ to $y$ and $y$ to $x$. Thus $x^3=y^4$ also gives
$y^3=x^4$, whence $x=x^4x^{-3}=y^3y^{-4}=y^{-1}$. The braid relation
then gives $x=y$, and $x^3=x^4$ forces both generators to be trivial.
This group calculation is not an AC move certificate.

Triangulate the rose by giving each generator a three-edge circle, with
only their base vertex shared. For a relator of length $L$, its signed
edge walk has $3L$ steps, denoted $v_0,\ldots,v_{3L}=v_0$. Give it a
separate domain circle with distinct vertices $u_0,\ldots,u_{3L-1}$ and
a separate cone vertex $a_r$. For every index $i$ modulo $3L$, insert
\[
 \{v_i,v_{i+1},u_{i+1}\},\qquad
 \{v_i,u_i,u_{i+1}\},\qquad
 \{a_r,u_i,u_{i+1}\},
\]
and all their faces.

The first two triangles triangulate the mapping cylinder of the word
map; the third cones its domain circle. The cylinder and cone together
are an attaching disk with a collar. Their outer boundary is identified
with the rose by exactly the original signed word. This is a triangulation
$K$ of the presentation polyhedron, not a replacement by a complex selected
merely for matching homology. Each rose edge has distinct endpoints, and
the separate domain vertices prevent unrelated triangles from being
identified. Its face vector is
\[
 (f_0,f_1,f_2)=(46,162,117).
\]
The count is $5+39+2$ vertices, $6+4(39)$ edges, and $3(39)$ triangles.
Contractibility follows from simple connectivity, Euler characteristic one,
and the homology/Whitehead theorem for this two-dimensional complex; Euler
characteristic alone would not suffice.

## A specific triangulated product and its reference collapse

Globally order the vertices of $K$. Encode $(v,0)$ and $(v,1)$ by $2v$
and $2v+1$. For every simplex $\sigma=\{v_0<\cdots<v_d\}$ insert the
staircase simplices
\[
 \sigma_i=\{(v_0,0),\ldots,(v_i,0),(v_i,1),\ldots,(v_d,1)\},
 \qquad 0\le i\le d,
\]
and all faces. The shared vertex order makes this triangulation agree on
common faces. The resulting $C$ triangulates $K\times I$ and has face
vector $(92,532,792,351)$.

There is a reference collapse $C\searrow K\times\{0\}$: process base
simplices by decreasing dimension, and within each simplex process the
staircases in increasing $i$. Pair $\sigma_i$ with its face obtained by
omitting $(v_i,0)$. All higher-dimensional base prisms have already been
removed; the first free face is the top simplex, and each subsequent free
face was exposed by the preceding staircase removal. Proper-face prisms
and the bottom copy remain. This gives $3f_2+2f_1+f_0=721$ pairs.
Independent replay must verify every free-face condition globally, not
merely trust this ordering recipe.

## The certificate that would resolve the stable instance

A second, verified collapse $C\searrow\{v\}$ would give
\[
 K\times\{0\}\nearrow C\searrow\{v\}
\]
through dimension at most three. The standard topological formulation of
stable AC then gives stable AC-triviality of this presentation; see
[Fagan--Qiu--Wang, Section 2](https://arxiv.org/html/2412.12293v2#S2).
This implication does not assume their fake-surface complexity bound, a
manifold thickening, or Zeeman's conjecture. The required collapse is the
new proof obligation, not an available theorem. It would establish the
stable AK3 instance, not ordinary AK3 or either general conjecture.

## Preflight and convergence rule

The implementation must independently verify the attaching words, face
closure, the induced bottom copy, and the 721-pair reference collapse.
The trivial presentation $(x,y)$ is a positive collapse control. A circle
prism and an invalid free-face pair are negative controls.

After these checks, allow one deterministic-seeded greedy collapse on the
one displayed AK3 triangulation, with a full saved trace. No subdivision
or seed sweep is part of this attempt. The independent verifier must check
that each proposed face has exactly one proper coface in the entire current
complex, that dimensions differ by one, and that success ends at exactly
one vertex. A stuck trace proves only that this chosen collapse order
stopped; it does not establish noncollapsibility, failure after subdivision,
or an AK3 obstruction. No negative residual ledger follows.

## Recorded outcome of the one planned attempt

The [constructor and recorder](../../experiments/stable_ac/ak3_prism_collapse.py)
passed the construction controls and the global reference-collapse replay
before the AK3 attempt ran. Seed $20260906$, choosing among free pairs of
maximum upper-simplex dimension first, produced exactly 610 elementary
collapses and stopped at a complex with face vector
\[
 (78,273,196).
\]
There are no remaining tetrahedra. The endpoint has Euler characteristic
one but is not a point. The [saved artifact](../../results/stable_ac/theory/ak3_prism_collapse_20260906.json)
contains every collapse pair and every maximal simplex of the endpoint;
the [independent verifier](../../tests/stable_ac/test_ak3_prism_collapse.py)
replays the trace by testing all proper cofaces in the entire current
complex, rather than relying on the recorder's coface index. It also checks
that the recorded endpoint has no further elementary free-face collapse.

Consequently this gives a certified three-deformation to the recorded
two-complex, not a stable AC trivialization. Its simplex count does not
improve on the initial triangulation, and no minimality is claimed. The
one prescribed unmodified-prism attempt is closed. A new geometric move
or a new collapse argument would be needed for further progress; no seed
sweep, subdivision sweep, or obstruction claim is authorized by this run.

## A monotone triangle fold through a tetrahedron

The next construction changes the complex; it does not rerun the prism's
collapse order. Let $L$ be a two-dimensional simplicial complex. Suppose
an edge $e=\{u,v\}$ has exactly two incident triangles
$t_1=\{u,v,c\}$ and $t_2=\{u,v,d\}$. Suppose exactly one of the two
other faces $\{u,c,d\},\{v,c,d\}$ is present. Denote the absent face by
$\mu$ and the four-vertex simplex by $\sigma=\{u,v,c,d\}$.

**Lemma (strict triangle reduction).** There is an elementary
three-deformation replacing $t_1,t_2,e$ by $\mu$, leaving every other
simplex unchanged. It removes one edge and one triangle in total.

**Proof.** The three present tetrahedral faces contain all six edges of
$\sigma$. Add the pair $(\sigma,\mu)$ by a $(3,2)$ elementary expansion.
Then collapse $\sigma$ through $t_1$, which has no other proper coface
because $L$ was two-dimensional. Finally collapse $t_2$ through $e$.
The global degree-two hypothesis guarantees that $e$ now has only the
coface $t_2$; the new face $\mu$ does not contain $e$. The net change is
exactly the one stated, with dimension never exceeding three. $\square$

The test of edge degree is against the entire complex, not just the
displayed tetrahedron. If both other faces are absent, the required
expansion is not available; if the edge has an extra incident triangle,
the final collapse is not licensed. These are explicit can-fail controls.

Starting with the saved two-complex above, the planned deterministic pass
exhausts ordinary collapses, then applies the lexicographically first
eligible triangle fold, and repeats. Ordinary collapses are ordered by
decreasing upper dimension and then lexicographically. Every completed
fold reduces the total simplex count by two, as does every ordinary
collapse, so the procedure terminates. In particular there can be at most
196 folds, the initial number of triangles. This bound is a monotonicity
proof, not an arbitrary search cap. There is no branching or seed choice.

The complete expansion/collapse trace must be independently replayed.
For an expansion, both new simplices must be absent beforehand, all
remaining proper faces must already be present, and the reverse collapse
must be legal. For a collapse, the lower face must have exactly the
specified proper coface in the entire current complex. All intermediates
must remain face closed and have dimension at most three. A point endpoint
would complete the geometric proof route; a non-point endpoint would only
close this prescribed monotone pass, not decide other three-deformations.

## Recorded monotone reduction

The single prescribed pass performed 23 triangle folds and 28 ordinary
collapses, recorded as 97 elementary operations. Its endpoint has face
vector
\[
 (66,222,157).
\]
Thus it removes 102 nonempty simplices from the saved core, preserves
Euler characteristic one, and ends at a non-point two-complex. The
[complete trace](../../results/stable_ac/theory/ak3_prism_shell_reduction_20260906.json)
retains the endpoint's maximal simplices and links its exact source
artifact. This is a strict simplification of that core, not of the original
presentation triangulation, whose total simplex count was 325.

The terminal result of this construction is a dimension-at-most-three
elementary deformation from the explicitly triangulated AK3 presentation
complex to the displayed 445-simplex two-complex. It combines the reverse
721-pair reference collapse, the previous 610 collapses, and these 97
operations. It does not trivialize the complex. The monotone pass is now
closed; changing its ordering, adding seeds, or treating its terminal
state as an obstruction is not part of the result. Further progress needs
a new geometric argument permitting moves not covered by this strict
reduction lemma.

## Certified edge contraction

Let $uv$ be an edge of a finite two-complex $L$, writing juxtaposition
for union with the named vertices. Require, for every
$\sigma$ disjoint from $u,v$ (including the empty face),
\[
 u\sigma,v\sigma\in L\quad\Longrightarrow\quad uv\sigma\in L.
\tag{EC}
\]
This is the standard link condition, not merely a common-neighbor test.
The contraction theorem is classical: see Ehrenborg--Hetyei,
[Definition 2.2 and Theorem 2.4](https://www.ms.uky.edu/~jrge/Papers/Independence.pdf).
Here is the explicit dimension bound needed for this certificate.

Put $S=\{\sigma:u,v\notin\sigma,\ v\sigma\in L\}$. For each
$\sigma\in S$ with $u\sigma$ absent, in increasing cardinality, expand
by $(uv\sigma,u\sigma)$. Condition (EC) and induction supply all other
proper faces. Next, in decreasing cardinality over all $S$, collapse
$(uv\sigma,v\sigma)$; larger cofaces have already been removed.
The final pair is $(uv,v)$. The endpoint is exactly the simplicial image
of $L$ under $v\mapsto u$. Since $|\sigma|\leq2$, no intermediate
simplex has dimension above three. This proves an explicit three-deformation,
not just preservation of homology. The vertex count drops by one and the
total nonempty face count strictly decreases.

More precisely, the three distinct faces $u,v,uv$ have the same image,
so a completed contraction loses at least two faces. This supplies the
same strict complexity decrease as the two earlier move types.

For the saved $(66,222,157)$ endpoint, permit one deterministic combined
pass: first ordinary collapses, then the preceding triangle folds, then
the lexicographically first edge satisfying (EC), always identifying its
larger vertex with its smaller vertex. Restart this priority order after
each completed move. The strict face decrease bounds the number of
completed moves, independently of runtime. In particular at most 65
contractions can occur. Record every elementary operation, not merely
the identified edges. Independently replay the full trace and verify the
terminal tests globally. A point would complete the geometric route;
otherwise close this prescribed pass without a permutation or seed sweep.

Preflight controls must include a contraction requiring an expansion,
the boundary of a triangle (common vertex but missing triangle), and the
boundary of a tetrahedron (common link edge but missing tetrahedron).
The latter catches an implementation that checks only common neighbors.

## Recorded contraction endpoint

The two preflight tests passed before the single prescribed AK3 pass.
It performed 46 contractions, three triangle folds, and three ordinary
collapses, recording 592 elementary operations in 52 completed blocks.
The [saved certificate](../../results/stable_ac/theory/ak3_prism_edge_contraction_20260906.json)
ends at a two-complex with face vector
\[
 (19,78,60),\qquad 19-78+60=1.
\]
There are 157 nonempty simplices, compared with 445 at the input and 325
in the original presentation triangulation. Thus this is also a strict
size reduction relative to that original triangulation. The certificate
stores every expansion and collapse, each block's operation interval,
and the full endpoint via its maximal simplices.

All eleven focused construction, control, and replay tests passed. The
new [independent verifier](../../tests/stable_ac/test_ak3_prism_edge_contraction.py)
reconstructs the original triangulation separately, replays all three
saved stages, checks each contraction against independently formed links
and its direct simplicial image, and confirms that no ordinary collapse,
triangle fold, or link-condition edge contraction remains at the endpoint.

The exact terminal theorem is now a three-deformation from the displayed
AK3 presentation complex to this specific 19-vertex complex. The complete
chain has 721 initial expansions, 610 prism collapses, the 97 operations
of the first reduction, and these 592 operations. It is not a deformation
to a point. No stable or ordinary AK3 claim follows merely from the
smaller face vector or Euler characteristic. The prescribed combined
monotone pass is closed; its terminal move tests do not exclude other
three-deformations. Before extending it, identify the terminal complex's
presentation and check whether the reduction simply returns to a known
AK3 representative in a smaller triangulation.

## Reading the terminal presentation

Choose the lexicographic spanning tree in the terminal one-skeleton,
adding an edge exactly when it joins two different tree components.
Its 18 edges are assigned the identity. Orient all other edges from
smaller to larger vertex and name them in lexicographic order. The
triangle $a<b<c$ gives the row $e_{ab}e_{bc}e_{ac}^{-1}$, omitting tree
edges. This yields 60 generators and 60 rows. Row identifiers retain the
sorted triangle order; no row is discarded because it is redundant or
represents the identity in the presented group.

For identification, use only the following defining-generator deletion.
If a freely reduced row is $A g^\varepsilon B$ with exactly one occurrence
of $g^{\pm1}$, rotate it to $g^\varepsilon BA$. For $\varepsilon=1$
substitute $g=(BA)^{-1}$ in every other row; for $\varepsilon=-1$
substitute $g=BA$. Delete that defining row and generator. The replacement
contains no $g$, so the inverse presentation map adjoins exactly this
definition. Keep empty rows and free-reduce only; do not silently apply
cyclic normalization. Each deletion is recorded with its pivot and
replacement for independent replay.

One deterministic pass chooses the least pair (row identifier, generator
identifier) at each step. There are at most 60 deletions. A 10,000-letter
guard is checked before constructing a substitution that could exceed it;
no order sweep or general relation search is authorized. The terminal
words identify this chosen presentation through explicit defining Tietze
moves. A group-isomorphism statement alone is not a stable-AC certificate,
and no arbitrary insertion or deletion of a consequence is permitted.

### Literal defining-row interface

Normalize a defining row by conjugation and, if necessary, inversion to
$r=gW$, where $W$ omits $g$. Write ${}^h r=hrh^{-1}$. The two identities
\[
 ({}^A r)^{-1}(AgB)=AW^{-1}B,
 \qquad
 {}^{AW}r\,(Ag^{-1}B)=AWB
\]
implement the positive and negative substitutions by left multiplication
with a conjugate of the current defining row. Conjugate and invert that
donor as necessary, multiply the recipient, then undo the donor changes.
These are restored-donor ordinary AC macros. Repetition removes $g$ from
every non-pivot row. Coordinates $g'=gW$ then make the pivot $g'$, with
all other rows unchanged, permitting destabilization.

The ambient-basis step is not being counted as an ordinary fixed-rank
relator move. A stable-AC use must retain the balanced trivial-presentation
hypothesis of the ambient-basis theorem and the geometric-to-presentation
CW dictionary. The recorded identification below does not silently
replace either gate by an abstract isomorphism of trivial groups.

## Exact return to standard AK3

The [recorded defining-generator pass](../../results/stable_ac/theory/ak3_prism_endpoint_presentation_20260906.json)
uses 58 deletions. Its remaining generator identifiers are 53 and 58;
call them $a,b$. Remaining row identifiers 57 and 59 are respectively
\[
 R=(a^2b^{-1})^3a^4,
 \qquad S=bab^{-1}ab^{-1}a.
\]
Their freely reduced lengths are 13 and 6. This is not a new unresolved
presentation: take the free basis
\[
 x=a^2b^{-1},\qquad y=a^{-1},
 \qquad a=y^{-1},\quad b=x^{-1}y^{-2}.
\]
The displayed maps compose to the identity in both directions, without
using any relator. Direct free substitution gives
\[
 R=x^3y^{-4},\qquad S=x^{-1}y^{-1}xyxy^{-1}.
\]
Conjugating the second row by $yx$ gives $xyxy^{-1}x^{-1}y^{-1}$.
Thus the extracted pair returns exactly to
\[
 \langle x,y\mid x^3y^{-4},\ xyxy^{-1}x^{-1}y^{-1}\rangle,
\]
the original AK3 presentation.

All six [focused checks](../../tests/stable_ac/test_ak3_prism_endpoint_presentation.py)
passed: small topological controls, both pivot signs and retained empty
rows, a can-fail prospective-size guard, the literal donor formulas,
independent tree construction and replay of all 58 saved deletions, and
the bidirectional basis maps with the exact final relator conjugation.

This is a literal free-basis identification followed by a relator
conjugation, not an inference from group triviality. The geometric
certificates remain valid, but their smaller triangulation has not made
the underlying presentation problem smaller. Close this geometric
corridor here: neither another reduction-order sweep nor a new family
of geometric residuals is justified by this return. The stable AK3 and
ordinary AK3 gates remain open.
