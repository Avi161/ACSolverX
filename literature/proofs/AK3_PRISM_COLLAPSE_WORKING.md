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
