# Depth-six balanced (L_0) census after Result 157

## Status

This is an exact bounded census, not a theorem about all homogeneous
syzygies.  It records the depth-six source search at which the tracked
fifteen-functionals check has no surviving balanced two-source
\((L_0)\) direction.  It neither searches depth seven nor proves anything
at arbitrary depth, and it does not prove stable AC.

## Census

Enumerate every reduced quotient word through length six.  There are 127
source vertices.  For each unordered pair with opposite orbit-boundary
signature, choose the coefficient in ({1,-1}) which balances both finite
orbits.  This gives 4,671 balanced source pairs.

Across the 4,671 balanced source pairs, 4,668 yield six boundary pairs, two
yield five, and one yields four.  The three exceptions are
`cTT + (-1)cTTct` and `cTT + cTcTTT`, with five boundary pairs, and
`cTcT + cTTct`, with four.  The generic complete four-sheet Stallings-cover
certificate rewrites all of their boundary pairs into exact forest paths.
The tracked
`experiments/stable_ac/depth4_period_two_subgroup_rewrite_certificate.py`
realizes the index-four subgroup \(K=\langle A,B,G\rangle\) of
\(Q=C_2*\mathbb Z\) by its four-state Reidemeister--Schreier transducer;
`experiments/stable_ac/depth4_period_two_source_flow_certificate.py`
classifies the six source-action signatures and reconstructs the five known
directions.  Their signed edge flow gives a
homogeneous vector (d) satisfying

\[
\sum_{i=0}^4L_i d_i=0.
\]

The census checker is
`experiments/stable_ac/depth4_period_two_depth6_l0_census_certificate.py`.
The tracked focused tests are
`tests/stable_ac/test_ak_depth_four_period_two_subgroup_rewrite.py`,
`tests/stable_ac/test_ak_depth_four_period_two_source_flow.py`, and
`tests/stable_ac/test_ak_depth_four_period_two_depth6_l0_census.py`.
It streams the following fourteen finite bits, in this exact order (the
order is `eleven.obstruction_bits(wedge)[1:]`):

1. Result 152 after \(\Phi_\infty\): the three-point \(\Phi_3\), remote
   four-point \(\Phi_4\), cyclic three-point, twisted three-point, and
   two-point bits;
2. Result 153: the two identity-four-cycle covectors, then the
   twisted-four-cycle covector;
3. Result 154: the second twisted-four-cycle covector;
4. Result 155: the inverse-four-cycle covector;
5. Result 156: the two five-cycle covectors; and
6. Result 157: the two double-transposition covectors.

Each serialized record uses `full_bit = 2` as a sentinel while any of those
fourteen bits is nonzero.  Only when all fourteen vanish does the checker
construct the full wedge and replace that sentinel by
\(\Phi_\infty\bmod 2\).  Thus the digest binds the finite projection and
the final gate without pretending that the sentinel is a functional.

The fourteen-bit filter leaves two near-survivors and the full gate leaves
no final survivor among all 4,671 pairs.  The deterministic record stream
has SHA-256

```text
02a688c2e0bfd1831202c6b76f8d3af9b4340c71e08d9b1e2efeea59d8301ff3
```

Fourteen projected finite-action bits leave exactly two near-survivors:

\[
e_{TT}+e_{TTTct},
\qquad
e_{Tctt}+e_{Tctct}.
\]

For both, the remaining full wedge-sum functional is

\[
\Phi_\infty=1\pmod2.
\]

Thus neither is a twelfth direction.

## Consequence and next step

Results 153--157 found new directions successively inside this same
balanced (L_0) family.  The complete depth-six failure is therefore a
meaningful change in the frontier, but it is bounded evidence only.

The focused reproducible command is:

```bash
PYTHONPYCACHEPREFIX=.scratch/pycache uv run --with numba --with numpy --with pytest python3 -m pytest -q tests/stable_ac/test_ak_depth_four_period_two_*.py
```

## Next theorem target (proposed, not proved)

The next target is closure under left extension by \(c,t,T\) of a candidate
transition state

```text
(K-coset/rewrite state, source action class, L0 pairing type,
 projected fourteen-bit class-two state, Phi_infinity gate).
```

This is not yet a proved Markov state: further prefix or order data may be
necessary.  The fourteen finite-action bits plausibly live in a finite
product of class-two Magnus states.  By contrast, \(\Phi_\infty\) is not
simply another finite point-action quotient: modulo two it is the parity of
interleavings/crossings among equal-vertex occurrence chords in the
Schreier-kernel word.  Proving finite transition data for that crossing
parity on the projected-zero source-pair language is a separate proposed
subtarget.  Only such a closure theorem, not another bounded scan, could
support an all-depth conclusion.

No claim is made for depth seven, arbitrary balanced source flows, all
depth, or stable AC.
