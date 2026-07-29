# Period-Two Tree-Flow Factorization Design

## Goal

Prove the structural theorem exposed by the tracked depth-six census:

1. the subgroup $K=\langle A,B,G\rangle$ is the free group $F_3$ and its two
   module-vertex orbits are Cayley trees;
2. a finite orbit-balanced $L_0$ boundary has a unique finite forest flow, so
   its edge variables are independent of endpoint pairing and depend linearly
   on the canonical source;
3. after anchoring source atoms at $T$, every balanced two-source direction is
   a signed sum of two anchored directions;
4. all fifteen Result 157 bits are an affine quadratic function of that
   homogeneous direction; and
5. the finite summary proposed after the depth-six census is not Markov, as
   witnessed by the two depth-six near-survivors and their three left
   extensions.

The deliverable is a theorem and an exact bounded certificate.  It is not an
all-depth obstruction, does not prove that no larger finite automaton exists,
and does not settle the period-two lift, stable AC, or AC.

## Hostile-referee corrections to the initial idea

The finite-state closure suggested by the preceding handoff is false for its
natural finite interpretation.  The two projected near-survivors have the
same source-action, pairing, finite $K$-branch, and fifteen-bit state, yet
their $c,t,T$ extensions have different syndromes.  Calling that tuple a
Markov state would be a false theorem.

Affine quadraticity remains true.  It follows from class-two collection in a
fixed ordered basis, but it does not make canonical shortlex lifting
equivariant under left extension.  Exact quotient-prefix equality, especially
in $\Phi_\infty$, is the missing datum.  The negative certificate must
distinguish these statements.

The existing binomial-forest certificate also compresses several logical
steps into one rank predicate.  The new proof must state the actual
Reidemeister--Schreier argument from rank-five parity-kernel injectivity to
$K\cong F_3$, then use torsion-freeness to prove the action on
$Q/\langle c\rangle$ is free.

## Selected architecture

Create
`experiments/stable_ac/depth4_period_two_tree_flow_factorization_certificate.py`
and a focused test.  Make one surgical repair to
`depth4_period_two_source_flow_certificate.py`: normalize externally supplied
source dictionaries with `lift.add_vectors(source)` rather than
`lift.clean_vector(source)`, and expose a path/pair reconstruction helper so
alternative pairings can be certified without duplicating edge-sign logic.

The new certificate has four layers.

### 1. Free subgroup and tree-flow layer

Recompute the parity-kernel rank-five basis and complete four-sheet Stallings
cover already tracked by Tasks 1 and 2.  Record the exact implications:

- the parity kernel of $F(A,B,G)$ has rank five;
- its five images generate a free subgroup of rank five;
- the restriction is an isomorphism, hence $F(A,B,G)\to Q$ is injective;
- $K\cong F_3$ is torsion-free;
- $K\cap q\langle c\rangle q^{-1}=1$ for every module vertex;
- each $K$-orbit graph is a Cayley tree; and
- finite-support edge boundary is injective.

The executable certificate can pin all finite ingredients and representative
consequences.  The proof note supplies the general free-group and leaf-removal
arguments; no finite enumeration is presented as a proof for every vertex.

### 2. Unique linear flow and anchored atoms

For a canonical finite source $s$ with orbit-balanced $L_0s$, the exact path
construction gives one finite edge chain with the required boundary.  Any two
pairings differ by a finite forest cycle, which is zero.  Therefore the
`variables` field is pairing-independent and linear.  The `paths` metadata is
not pairing-independent and must not be stated as invariant.

Repair raw normalization before applying this theorem.  The regression

```python
{(): 1, (lift.C,): -1}
```

must normalize to the zero source, and a multiplicity collision must sum
rather than overwrite.  This does not change any existing canonical caller.

Let

```text
lambda(v) = first orbit sum of L0 e_v,
anchor = T,
H(v) = D(e_v - lambda(v)e_T).
```

Since `lambda(T)=1`, `H(v)` is defined for every source atom.  If
$e_x+\varepsilon e_y$ is balanced, then

```text
D(e_x + epsilon e_y) = H(x) + epsilon H(y).
```

Pin this on magnitude-one, magnitude-two, positive, and negative fixtures.

### 3. Affine-quadratic fifteen-bit layer

For a homogeneous direction $X$, let $S(X)$ be the fourteen projected bits
followed by $\Phi_\infty$ for `base + X`.  Define

```text
C = S(0)
U(X) = S(X) + C
B(X,Y) = S(X+Y) + S(X) + S(Y) + C.
```

Class-two collection proves $B$ is biadditive modulo two and

```text
S(X+Y) = C + U(X) + U(Y) + B(X,Y).
```

Integral coefficients require the period-four self term
$\binom n2\bmod2$; a parity-only coefficient model is insufficient.  The
certificate pins the exact near-survivor factorization and a three-direction
biadditivity fixture, plus coefficient values through one complete mod-four
period.  The proof note supplies the general polynomial-law argument.

### 4. Explicit no-Markov layer

Define the refuted summary precisely:

- unordered source action classes;
- signed $L_0$ orbit scalars;
- the multiset of paired endpoint action classes and the finite `epsilon`
  branch used by `path_between`;
- the current fourteen projected bits and $\Phi_\infty$.

The two pairs

```text
P  = e_TT   + e_TTTct
P' = e_Tctt + e_Tctct
```

have the same summary and syndrome `000000000000001`.  Their simultaneous
left extensions have the pinned distinct syndromes:

```text
c: 000100000000100 != 100100011000001
t: 000000001000000 != 100100011000100
T: 011110110101110 != 011110111101010
```

All words remain at source depth at most six.  This disproves only the stated
summary as a Markov state.  If `K-rewrite state` means the entire reduced
$A/B/G$ word it can distinguish the examples, but it is unbounded and hence
not a finite state.

## Interfaces

The new module should expose:

```python
source_scalar(vertex) -> int
anchored_direction(vertex) -> escape.ModuleVariables
add_directions(*directions) -> escape.ModuleVariables
scale_direction(direction, coefficient) -> escape.ModuleVariables
syndrome(direction) -> tuple[int, ...]  # 15 bits, Phi_infinity last
polarization(left, right) -> tuple[int, ...]
finite_pair_summary(left, right, right_coefficient) -> tuple
tree_flow_factorization_certificate() -> PeriodTwoTreeFlowFactorizationCertificate
```

The source-flow layer should expose one helper that reconstructs variables
from an explicitly supplied valid endpoint pairing, with all endpoint,
edge-sign, and zero-image assertions retained.

## Verification

Focused tests must establish:

1. raw canonical collisions sum and cancel correctly;
2. the tracked four-sheet/rank data support the explicit $K\cong F_3$ proof
   record;
3. a crossed Result 153 pairing changes paths but not variables;
4. anchored decomposition holds for representative sign and magnitude
   classes;
5. the exact near-survivor unary/bilinear factorization and biadditivity
   fixtures hold;
6. coefficient behavior retains the mod-four self term;
7. the two near-survivors have identical finite summaries;
8. their $c,t,T$ extension syndromes differ exactly as pinned; and
9. the existing subgroup/source/census tests remain green.

No depth-seven census or search is permitted.  The full period-two suite is
run once at integration with retained exit evidence, not once per task.

## Documentation boundary

Create a proof note for the tree-flow/factorization theorem and update the
handoff and direct-theory ledger.  Replace the old finite-closure target with
the proved no-Markov counterexample and the two honest remaining branches:

1. add support-order inversion data to an automaton for the fourteen finite
   bits; and
2. prove finite compression of exact-prefix equality for $\Phi_\infty$, or
   prove an explicit non-regularity obstruction.

Every note must say that neither branch is solved.
