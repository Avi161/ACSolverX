# AK(3) rank-three primitive-pair design

Date: 2026-07-24

Status: theorem opportunity identified; Whitehead decision not yet implemented.

## Candidate

Every certified two-stabilization template produces a balanced rank-three
presentation

\[
\langle x,z,t\mid A,B,C\rangle
\]

stably AC-equivalent to AK(3).

The candidate is:

> **Primitive-pair corridor lemma [unverified].** In at least one of the 3,016
> cyclic rank-three corridor states, two relator conjugacy classes extend to
> a free basis of \(F(x,z,t)\).

This is not a one-letter isolator test. It asks whether two relators can be
straightened simultaneously by one ambient automorphism.

## Stable implication

If two relator conjugacy classes form a primitive pair, an automorphism sends
them, up to independent conjugation and inversion, to two distinct basis
generators. Apply the stable ambient automorphism theorem, normalize those two
relators by AC1/AC3, and remove the two generator-relator pairs.

The remaining presentation has one generator and presents the trivial group,
so its relator is a power with exponent \(\pm1\). Equivalently, the original
trivial abelianization determinant forces the surviving exponent to be
\(\pm1\). The final pair removes by inverse stabilizations. AK(3) is stably
AC-trivial.

## Exact decision

Whitehead's theorem for finite tuples of cyclic words says that if a tuple is
not length-minimal in its Aut orbit, one second-kind Whitehead automorphism
strictly decreases total cyclic length.

For each of the three relator pairs in every cyclic rank-three source:

1. greedily apply a strictly length-decreasing rank-three Whitehead
   automorphism until none exists;
2. carry the composed automorphism as a witness;
3. enumerate every second-kind automorphism at the endpoint to certify local
   minimality;
4. declare the pair primitive exactly when the minimum total is two and the
   two one-letter words use distinct basis generators.

The negative certificate stores all 9,048 pair minima and binds the complete
source census. A positive stores the exact ambient automorphism and expands
the two eliminations.

## Whitehead automorphisms in rank three

Use the six signed multipliers and all subsets containing the multiplier but
not its inverse. After deduplication this gives 90 nonidentity second-kind
automorphisms. The 48 signed permutations are only needed to canonicalize a
minimal level, not to detect a descent or decide whether the minimum is two.

Cross-check the rank-two specialization against the repository's exact 12
second-kind automorphisms before trusting rank three.

## Constraints

- New files only.
- No AC graph search.
- Rebuild all 3,016 cyclic rank-three states, including immediate corridors.
- Independently replay every automorphism witness and every local-minimum
  gate.
- CPU only; `.venv/bin/python3`.
- A negative decides only this finite primitive-pair corridor lemma.
- Commit and push within twenty minutes; no PR or merge.
