# Period-two exact source-rewrite design

## Goal

Promote the exact complete-cover rewrite and balanced-source classifier from
research scratch into stable, independently tested certificate code.  The
immediate deliverable is a reproducible proof of the bounded depth-six
census after Result 157.  The architectural purpose is to expose the finite
state needed for a later all-depth syndrome recursion.

This does not claim a proof of Andrews--Curtis, stable Andrews--Curtis, the
period-two lift, or an all-depth source-flow obstruction.

## Considered approaches

### 1. Copy the scratch scripts verbatim

This is the fastest route to a tracked census, but it mixes subgroup
rewriting, source enumeration, edge-flow construction, finite projections,
and reporting.  A failure in one layer is hard to localize, and a later
recursion would inherit search-specific state.

### 2. Separate exact algebra, source flow, and census layers

This is the selected approach.  It introduces three small certificate
modules with explicit interfaces and independent tests.  It requires more
initial plumbing, but preserves the exact algebra while allowing the census
layer to be replaced by a recursive automaton later.

### 3. Derive the all-depth automaton directly from scratch state

This targets the deepest theorem immediately, but the current rewrite and
orbit classifier are not yet tracked or independently verified.  Building
the recursion on unpinned infrastructure would make any global claim hard
to audit.  This approach is deferred until the first two layers are stable.

## Architecture

### Exact subgroup rewrite

Create
`experiments/stable_ac/depth4_period_two_subgroup_rewrite_certificate.py`.
It owns:

- free reduction, inversion, and substitution for abstract free words;
- the normal form of $Q=F(p,q)\rtimes C_2$;
- exact multiplication and inversion in that semidirect product;
- the complete four-sheet Stallings core and its spanning-tree coordinates;
- the Nielsen inverse from core generators to the five
  Reidemeister--Schreier generators and then to the forest basis
  $(A,B,G)$;
- `rewrite_k` and `path_between` with exact round-trip assertions.

It depends only on the existing binomial-forest, degree-two escape, and
phi4 certificate modules.  It performs no source enumeration.

### Source-flow reconstruction

Create
`experiments/stable_ac/depth4_period_two_source_flow_certificate.py`.
It owns:

- canonical reduced source vertices through a requested depth;
- the six finite vertex action classes and their $L_0/L_1$ orbit
  signatures;
- orbit-balanced boundary pairing;
- exact path-flow reconstruction in components $2,3,4$;
- construction and validation of a homogeneous $L_0$ two-source direction.

Its public result for a source pair contains the source coefficients,
literal paths, sparse direction, and exact homogeneous-image assertion.  It
does not calculate obstruction syndromes.

### Depth-six census

Create
`experiments/stable_ac/depth4_period_two_depth6_l0_census_certificate.py`.
It owns:

- enumeration of the 127 depth-six source vertices;
- selection of all 4,671 orbit-balanced unordered pairs;
- projected evaluation of the fourteen finite-action Result 157 bits from
  the Schreier kernel;
- evaluation of the full wedge-sum bit only for projected survivors;
- the exact near-survivor records
  $(TT,TTTct)$ and $(Tctt,Tctct)$;
- a deterministic census hash and a zero-survivor assertion.

The census must label its scope as depth six and must not expose an
all-depth boolean.

## Data flow

For each source pair, the source-flow layer applies $L_0$, verifies the
two orbit sums vanish, pairs negative and positive boundary entries within
each orbit, requests exact forest paths from the subgroup-rewrite layer,
and converts those paths into a homogeneous module vector.  The census
adds the canonical first-layer solution, computes the nonlinear residual
and Schreier kernel, evaluates projected wedge coordinates, and constructs
the full wedge only when all projected bits vanish.

Every conversion boundary has an exact assertion: normal-form round trip,
path endpoint, homogeneous image, first-layer equation, and direct/projected
syndrome agreement on selected fixtures.

## Error handling and invariants

- `path_between` raises when endpoints are in different $K$-orbits; the
  source layer treats this as a certificate failure, not a skipped pair.
- Nielsen reduction must strictly reduce total word length at every step and
  end in a signed permutation basis.
- Every accepted core loop must return to the core base vertex.
- Balanced-pair coefficients are restricted to $\{-1,1\}$ and are checked
  against both orbit sums.
- The census aborts on any mismatch between fast projected bits and direct
  wedge evaluation for fixtures.
- No numerical or bounded-radius subgroup search is permitted.

## Verification

Tests will establish:

1. the four previously certified forest paths replay exactly;
2. every quotient word through depth six that lies in $K$ round-trips
   through `rewrite_k`;
3. the complete core is a four-sheet cover and has the expected free rank;
4. there are exactly six vertex action classes with the recorded signatures;
5. the Result 153--157 source directions reconstruct from their fixed source
   pairs;
6. the depth-six census has 127 vertices, 4,671 balanced pairs, two projected
   near-survivors, and zero fifteen-bit survivors;
7. both near-survivors have only $\Phi_\infty=1$;
8. the deterministic census hash is stable.

The existing 48-test period-two chain must remain green.  The new focused
tests and census will be independently replayed before commit and push.

## Next theorem after promotion

Once the three modules are stable, compute the transition of the source
action class, boundary pairing type, and fifteen-bit quadratic state under
left extension by $c,t,t^{-1}$.  If these data close under finitely many
states, exhaust the reachable automaton to obtain an all-depth theorem.  If
they do not close, the first missing datum identifies the precise invariant
that the recursion must retain before any depth-seven scan.
