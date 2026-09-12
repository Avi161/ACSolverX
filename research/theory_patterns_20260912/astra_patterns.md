# Stable-relator boundary transport: early proved note

Status: proved ordinary-AC **donor-changing span reduction**, not a solve claim.
This note is independent of the fixed-donor overlap-completion experiment.

Use z_i=t^i z t^-i. Choose the literal ambient generators (t,z) as either
(x,y) or (y,x); no generator automorphism is being applied. Suppose the input
source R0 has exp_t(R0)=e in {+1,-1}. Put R=R0^e=F t by exact Magnus
collection. Let the other relator S have exp_t(S)=0 and indexed spelling G.
Write support(F)=[a,b], support(G)=[c,d], and require b-a<d-c.
Empty F is already a primitive terminal case; G cannot be empty for a
unimodular pair. Choose any integer q in [c+1-a,d-b] and set
D=t^q R t^-q=F_q t, where F_q shifts every index in F by q.

## Exact two-direction identities

For any indexed word H, let T(H) shift every index by +1. Direct free-group
identities (not merely quotient equalities) are

    D H D^-1 = F_q T(H) F_q^-1,
    D^-1 H D = T^-1(F_q)^-1 T^-1(H) T^-1(F_q).

For lower-boundary removal choose H=z_c^eta, eta=+/-1. Every replacement
letter lies in [c+1,d]. For upper removal choose H=z_d^eta; every replacement
letter lies in [c,d-1]. This works with arbitrary multiplicities and signs in
F and G. There is **no monic or unique-boundary occurrence requirement**.
Replace every chosen boundary occurrence using the same D. Cancellation
cannot reintroduce the eliminated boundary. The support span strictly drops.
Ordinary freely/cyclically reduced length may increase sharply.

## Restored-source elementary compiler interface

Use only ordinary AC1 inversion, AC2 right multiplication of one relator by
the other, and AC3 conjugation by one signed ambient generator. The source
R0 is restored after each multiplication. Let the current target be S=P H Q
as an exact free-word factorization, and choose s=+1 for lower transport or
s=-1 for upper transport. Desired output is S'=P D^s H D^-s Q.
Then

    S^-1 S' = (c1^-1 R0^(e*s) c1)(c2^-1 R0^(-e*s) c2),
    c1 = t^-q H Q,
    c2 = t^-q Q.

Freely reduce each c before emitting. For each (sign,c), temporarily invert
R0 if sign=-1, conjugate it to c^-1 R0^sign c, right-multiply the target,
then reverse the conjugations and restore the source sign. This emits two
source multiplications, never stabilization or a simultaneous ambient map.
Expand H and Q from the **current** indexed target, rather than using stale
free-word offsets after earlier cancellation. Formula works for any block H,
not only one letter; group maximal boundary runs z_c^k/z_d^k to use two
multiplications for the whole nonzero signed power.

## Distinction from existing rules

The existing one-sided Magnus rule retains a zero-stable-exponent donor and
uses its unique extreme letter to change the stable-exponent-one recipient.
This rule retains the stable-exponent-one relator and changes the
zero-exponent donor; it requires only a strict span inequality and no monic
condition. It is a structured composition of two ordinary conjugated
substitutions (the general commutator identity), so it is a new justified
recognition/placement rule, not a new AC move axiom. It can bypass an
obstruction tied to retaining the original BS donor by changing that donor.
No resulting solve, ordinary-length improvement, or complexity speedup is
asserted from span reduction alone.

## Early literal U124 screen

A cheap read-only scan of data/ms_unsolved_reps/aca_124_best.csv examined both
source choices and both literal stable generators; no basis enumeration and
no heap search. It found 45 oriented strict-span candidates (the sign of R0
is normalized by e above). Exact machine records and verified examples follow
in astra_boundary_checks.json. The count is oriented candidates, not 45
independent solves or even necessarily 45 distinct rows.

## Verified root evidence

The final cheap literal screen found **45 oriented candidates on42 distinct
U124 rows**. Both lower and upper passes were run and each prefix independently
replayed, giving90 verified prefixes. The standalone probe records exact
source roles, signed normalization, stable generator, q, ledgers and elementary
moves. Its observed wall time was0.0072s; it performs no heap search. Input
SHA-256:8df25b3fc585553f80886934707b147c99252dcedf4b827a9a220fe99ebb58a3.

| row | retained source | target before → after | span | ordinary length | moves |
|---|---|---|---|---|---:|
| aca_1 | YYYxyXyX | YYXXyxx → YYXYxYXyxyXyx | 2→1 | 7→13 |14|
| aca_4 | YYXXXyx | YYxyxyXyXYX → XYxyxYxyXyXYX |3→2|11→13|42|
| aca_118 | YYYYXyxx | YXXyxYx → XXYxYXyyxYx |2→1|7→11|30|

These are freely reduced literal outputs; further cyclic conjugation is a
separate AC3 step if desired. No improvement in ordinary length is claimed.

## A second proved rule: divisible extreme-power elimination

This extends the monic-boundary rule to a non-monic **single extreme run**.
It is an extension of that mechanism, not claimed to be an unrelated idea.
Let the zero-stable-exponent source S have support[a,b], and let its upper
extreme occur in exactly one literal maximal run z_b^m, m a nonzero integer. All other
letters have smaller index. Invert S if needed to make m positive, recording
that sign as e. Let recipient R=F t have support[c,d] with b-a<=d-c.
Shift by q=d-b and cut the actual donor D=t^q S^e t^-q=C A E, A=z_d^m.
Set B=C^-1 E^-1. Suppose **every maximal z_d-run in F has exponent divisible
by m**. Replace A→B and A^-1→B^-1 repeatedly in those runs. No replacement
contains z_d; a merged remaining boundary run still has exponent divisible
by m. The upper endpoint therefore disappears after finitely many uses.

The exact free-group errors for the two atomic replacements are

    A^-1 B = E D^-1 E^-1,
    A B^-1 = C^-1 D C.

For the current recipient R=U A^eta V t (eta=+1 or-1), the right-multiplier
ledger relative to the original source S is

    eta=+1: source exponent -e; conjugator t^-q E^-1 V t,
    eta=-1: source exponent +e; conjugator t^-q C V t.

Thus one source multiplication per replaced copy of A, with source restoration,
is sufficient. The lower-end version uses q=c-a and the same identities,
with all replacement indices strictly above c. This covers arbitrary words
C,E and arbitrary nonzero m; it requires neither a BS power tail nor m=1.
The m=1 case is the existing one-sided Magnus rule. The m>1 case is new to
that implemented recognizer. Failure of divisibility is not an AC obstruction.

## A proved composite termination criterion

Maintain a unimodular pair R=F t,S=G in one literal indexed frame. Then
exp_z(S)=+/-1. At any nonterminal stage apply the following deterministic
choice, with its exact source-restored elementary ledger:

1. If span(G)>span(F), use stable-relator boundary transport to shrink G.
2. If span(G)<=span(F), require a boundary of G in one literal maximal run of power m
   and every corresponding extreme run of F divisible by m; use the second
   rule to shrink F. The m=1 branch only requires a monic endpoint.

Stop with `criterion_failed` if step2's explicitly testable hypothesis fails.
The **sufficient infinite family** consists of inputs for which this hypothesis
holds whenever step2 is reached. This condition is evaluated on the exact
successive words, not inferred from exponent sums. Each nonterminal pass
strictly lowers span(F)+span(G). At most its initial value+1 whole-boundary
passes can occur. An empty F gives R=t. A span-zero G freely reduces to
z_i^exp_z(S)=z_i^+/-1, a conjugate of a generator. Either endpoint gives a
finite ordinary AC cleanup. An empty G is incompatible with unimodularity.

Thus the procedure terminates with a certificate or an explicit failed
hypothesis; under the stated checkpoint hypothesis it terminates with a
certificate. This is a sufficient constructive family, not a theorem that
all unimodular presentations satisfy those checkpoints. Its significance is
that it alternates which relator is changed, whereas either existing
fixed-donor reduction alone can stall. No total-length or polynomial-time
bound follows: indexed word lengths and expanded conjugators can grow.

## Recommended immediate experiment

Implement the first rule alone as a bounded two-direction donor-changing
prefix on the42 literal root matches, charge two relation uses per maximal
boundary run plus actual certificate cost, then test existing terminal gates
or a short explicitly budgeted continuation. Record span and ordinary length
separately. A second experiment can implement the alternating deterministic
criterion; preserve the failed checkpoint and both spans. Do not count the90
verified reductions as90 improved presentations or as any new solve.

The second-rule source-sign/target-sign ledger was additionally verified on24
expanded free-word cases (both ambient axes and m=2,3,5), saved in
`astra_power_identity_checks.json`. Cyclic orientations need a separately
recorded conjugation witness; the theorem above uses a literal maximal run.
