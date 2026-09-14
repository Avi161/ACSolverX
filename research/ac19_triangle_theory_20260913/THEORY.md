# Rank-preserving structure of all-triangle states

Setting. A state is a tuple of cyclic words over a fixed generator set, read
modulo rotation and inversion (`search.canonical`). The only moves are ordinary
AC normal-product substitutions

    R_i  <-  rot(R_i) . rot(R_j^eps)        (i != j, eps = +-1),

which keep the rank and the declared generator set. An *all-triangle* state has
every relator of length exactly three; this is what `triangulate` produces from
a rank-two pair and is treated here as preprocessing, never as a solve. A run
exposes structure only if it reaches a relator of length two (a *bigon*) or one
(a *unit*) at unchanged rank.

Write `inv2(u, v) = (v^-1, u^-1)` for the involution induced on cyclic digrams
by inverting the word.

## Lemma 1 (parity)

The cyclically reduced length of `rot(A) . rot(B)` is congruent to `|A| + |B|`
modulo two. Free reduction and cyclic reduction each delete one inverse pair,
that is two letters, per step.

Consequences at an all-triangle state:

* triangle x triangle has length in `{0, 2, 4, 6}`: **no unit in one move**;
* quartic x triangle has length in `{1, 3, 5, 7}`: **no bigon from a quartic
  and a triangle**.

So the only one-move route to a bigon is triangle x triangle, and every route
to a unit leaves the all-triangle regime first. This is why the frozen engine's
`generate(words, relator_cap=3)` returns no children at all from a triangle
root: nothing of odd length `<= 3` is a product of two triangles.

## Lemma 2 (a shared digram is necessary for a one-move bigon)

If a single triangle x triangle substitution yields a relator of length two,
then the two relators involved share a cyclic digram modulo `inv2`.

Proof. Length six to two deletes exactly two inverse pairs. Write the chosen
rotations as `a = a1 a2 a3` and `b = b1 b2 b3`. The first deletion is at the
seam, `a3 b1`, so `b1 = a3^-1`. The second is either

* at the seam again, `a2 b2`, so `b1 b2 = (a2 a3)^-1` and `inv2(a2, a3)` is a
  digram of `b`; or
* at the cyclic wrap, `a1` against `b3`, so `b3 = a1^-1` and
  `inv2(a3, a1) = (a1^-1, a3^-1)` is a digram of `b`.

Either way a digram of `a` matches a digram of `b` under `inv2`. Since every
rotation of both relators and both signs are available, the statement is about
the relators as cyclic words. []

The converse fails exactly when the two relators coincide as canonical cyclic
words: the matched rotation then cancels completely and the product has length
zero, not two. Machine check (`verify.py::verify_theory`, independent code;
`theory.check_bigon_criterion` in the module): over 11,774 random balanced
all-triangle states of rank 2 to 4 there were **0** bigons without a shared
digram, and every one of the 1,225 states with a shared digram but no bigon had
two equal relators.

## Definition and consequence

A state is **digram-disjoint** when no two distinct relators share a cyclic
digram modulo `inv2`. By Lemma 2 a digram-disjoint all-triangle state has no
one-move bigon, and by Lemma 1 no one-move unit. Its cap-3 neighbourhood is
therefore empty and its cap-4 neighbourhood consists only of length-four
relators. A rank-preserving search from such a root cannot expose a short
relator in one step under any ordering; it must first create sharing.

## What greedy triangulation produces

`triangulate` repeatedly replaces the globally most frequent digram by a fresh
generator until every relator has length at most three. Its output falls into
two kinds, and the lemmas only speak about the first:

* **all-triangle roots** (every relator of length exactly three), and
* roots that already contain a relator of length one or two, because the
  rank-two pair had one or the compression produced one. For these the short
  relator is exposed by *preprocessing*, before any search, and Lemma 1 and
  Lemma 2 do not apply (two bigons can multiply to a bigon with no digram
  match).

Measured on 400 randomly sampled AC19 rows (`data/AC19_extended_aut_min.csv`,
seed 3; `census_digram_disjoint_s3_n400.json`): 255 roots are all-triangle and
**all 255 are digram-disjoint**; the other 145 already carry a relator of
length at most two. The most frequent digrams are exactly the shared ones, so
the greedy choice tends to consume every shared digram before it stops, but
disjointness is not forced by the stopping rule: on the frozen easy panel the
all-triangle roots of `ac19_44` and `ac19_48` do share digrams, and both expose
a bigon in one move. All four hard-panel roots are all-triangle and
digram-disjoint (`bench_cap45_p60.json`).

## Corollary 3 (minimum move counts from a digram-disjoint root at cap 4)

Let the root be a digram-disjoint all-triangle state and let every relator be
kept at length at most four.

* **No bigon in fewer than three substitutions.** After one move the state
  has exactly one quartic and otherwise the original triangles, which are still
  pairwise digram-disjoint. A bigon would need an even-length product (Lemma 1):
  quartic x triangle is odd, and triangle x triangle is blocked by Lemma 2. So
  the second move cannot produce a bigon either; at least three are needed.
* **No unit in fewer than two substitutions.** Lemma 1 forbids a unit from two
  triangles, so the first move cannot produce one.

The benchmark budgets (60 pops with beam 48 at caps 4–6) explore well beyond
depth three, so the empty hard-panel results in `RESULTS.md` are not a
depth-cutoff artefact of these bounds.

## The coupling ordering

Because sharing is necessary before any bigon and a bigon or a longer relator
is necessary before any unit, a search that wants to expose short relators at
fixed rank should climb toward sharing rather than toward short total length
(which is constant, `3r`, across every all-triangle state and `3r + 1` across
every cap-4 child, so it carries no information). `coupling_search.COUPLING`
orders states by

    (no unit, no bigon, -shared digram pairs, -shared digrams, total length, max relator length)

and is compared like for like with the incumbent `structural_score` on the same
roots, caps and budgets. Its behaviour on the frozen panels is in `RESULTS.md`.

## Scope

Both lemmas are elementary statements about free reduction of cyclic words.
They bound what one substitution can do at fixed rank; they say nothing about
longer paths, about stable moves, or about AC-triviality. A digram-disjoint
root is an obstruction to *one-step* progress only.
