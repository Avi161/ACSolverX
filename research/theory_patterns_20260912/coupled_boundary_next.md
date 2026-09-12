# Coupled shifted row exchange: exact move and finite descent criterion

Status: proved ordinary AC move changing **both** relators, with a complete
finite recognizer for strict literal support-potential descent within the
specified family. It does not supply a new universal completion theorem.
A six-frame check on four U124 roots and the saved aca_9 residue stall found
no descent. This negative is preferable to treating integer gcd cancellation
as a free-group argument. No heap search, ambient basis map, or stabilization
is used.

## The exact coupled move

Write the current pair as R=F t,S=G using exact Magnus collection
z_i=t^i z t^-i. Thus exp_t(R)=1 and exp_t(S)=0. Let T shift indexed words
by one. Choose donor orientation e=+/-1 and an integer q; explicitly
conjugate/invert the second relator to D=t^q S^e t^-q, with indexed word G_q.
Define H=G_q^-1 F after indexed free reduction. For any integer k the pair
can be changed to

    R' = H t = D^-1 R,
    S' = F T^-k(H^-1) = R t^-k (R')^-1 t^k.

Both equalities are free-group identities. In the second one, the original
R=F t and R'=H t give

    F t t^-k t^-1 H^-1 t^k = F t^-k H^-1 t^k.

This changes the formerly obstructing zero-stable donor. It is not a
fixed-S quotient substitution: its output source is D^-1R, and its output
donor uses that changed source.

### Original-pair elementary ledger

Use AC1 inversion, AC2 right multiplication by the other current relator,
and AC3 conjugation c^-1 W c, expanded one signed generator at a time.
After the explicit orientation/preconjugation S→D:

1. Invert R, multiply it on the right by D, invert R. The first relator is
   now A=D^-1R (three elementary moves, one AC2).
2. Replace the second relator D by D A. It is exactly the original R
   (one elementary move, one AC2).
3. Temporarily invert A and conjugate it to t^-k A^-1 t^k. Multiply the
   second relator by it. Undo those conjugations and invert the source back.
   The endpoint is (A,R t^-k A^-1t^k), and A is restored.

There are exactly three AC2 multiplications and 7+2|k| elementary moves
before the donor-orientation/preconjugation overhead. Add |q| conjugations,
one inversion when e=-1, and an initial source inversion if its supplied
stable exponent is -1. No source in this ledger is assumed to remain the
original R or S after its explicitly declared change.

For software, build the entire exchange transactionally, verify its predicted
pair by a separate elementary replay, and commit only within declared work,
word, indexed-word, and certificate caps. At minimum charge all three AC2
uses, every tested orientation/shift, and every rejected candidate; report
actual elementary count separately. A cap is a software stop, not failure
of the theorem. This note does not add an uncapped production API.

## What the exchange computes algebraically

On the abelianized indexed fibre write f,g for the Laurent polynomials of F
and G_q. Then the exact free-group exchange induces

    (f,g) -> (f-g, (1-T^-k) f + T^-k g).

The corresponding 2x2 Laurent matrix has determinant1. This is an ordinary
AC-realizable coupled row exchange, but the Laurent matrix is only a shadow
of the free words: it does not prove that leading indexed runs combine as
integers. The exact words H and S' must be reduced and inspected.

## A finite, support-derived strict-descent criterion

Let Phi=span(F)+span(G), using the reduced literal indexed words, and handle
empty F or span-zero G by the already proved terminal cleanup. Require
unimodularity only for that terminal implication. The exchange itself needs
only the stated stable exponents. Independent cyclic reorientation is not
silently included in the following complete candidate prescription.

For each donor sign e:

1. The only potentially useful preconjugation is
   q=index(first(F))-index(first(G^e)), and their signs must agree. If they
   disagree, this orientation supplies no strict Phi decrease.
2. Reduce H=(T^q(G^e))^-1 F. If H is empty, R'=t is terminal. Otherwise let
   support(F)=[a,b] and support(H)=[u,v]. Test

       k in {0, u-a, v-b, index(last(H))-index(last(F)), -1, +1}.

   Deduplicate the set. If donor-changing outputs are specifically required,
   omit k=0; its endpoint merely changes R and retains D.
3. Accept only after computing the exact reduced B=F T^-k(H^-1) and checking
   span(H)+span(B)<Phi, or after an independently certified terminal match.

This has at most12 k candidates per literal oriented frame, plus normalization
and word arithmetic; these are not12 constant-time machine operations.

### Why the finite prescription is complete for strict Phi descent

If H has no cancellation across G_q^-1|F, its support contains the entire
supports of F and G_q. For k=0, B=G_q and Phi cannot decrease. For k≠0,
H ends in exactly the final letter of F; hence the seam F|T^-k(H^-1) cannot
cancel. It follows that span(H)>=span(G) and span(B)>=span(F), again ruling
out a strict decrease. Initial seam cancellation therefore is necessary,
and forces exactly the first-letter alignment in step1.

Once H is reduced and nonempty, cancellation at F|T^-k(H^-1) can occur for
only the one shift k=index(last(H))-index(last(F)); matching signs are
checked by actual reduction. This is the fourth listed candidate. At every
other shift there is no free cancellation, so B's support is exactly the
union of [a,b] and [u-k,v-k]. Its minimum possible span is attained by the
endpoint alignments k=u-a or k=v-b. If zero is excluded and both alignments
are zero, the nearest nonzero integers ±1 attain the minimum over k≠0.
Thus any strict decrease obtainable by any integer q,k and either donor sign
is witnessed by the listed finite candidates. A negative is complete for this
specific family in that literal frame, not for all coupled AC operations.

A deterministic algorithm may repeatedly accept the best strict candidate
until it reaches a separately certified terminal rule or finds none. Phi
strictly decreases, so it makes at most its initial Phi accepted exchanges.
This gives a finite general sufficient criterion, with a precise failure
checkpoint; it does not assert that all unimodular inputs pass it.

## A nonterminal infinite descent family

Put H=z_0 z_1 z_0^-1 z_1^-1, G=z_0^2 z_m^-1, F=G H, where m>=2.
The input is (F t,G), with determinant±1. Choose e=1,q=0,k=-1. The exchange
returns (H t, F T(H^-1)). Both displayed products are freely reduced at their
joining seams. Initial Phi=2m, whereas the output potential is1+m, a strict
decrease of m-1. Neither output is asserted solved. This verifies that the
strict descent family is nonempty at arbitrary support width. It does not
show a new AC reachability axiom or a classification disjoint from all older
ordinary-move search paths.

A tempting terminal specialization is

    (U T^-k(V) t, U T^-k(V) V^-1) -> (V t,U).

When U is a generator this is already an instance of the existing shifted
commutator-shell theorem after cyclic reorientation. It must not be counted
as a new independent terminal family. The value of the exchange, if any, is
its computable donor-changing nonterminal descent and possible later entry
into an existing rule.

## Checked hard examples and honest failure

`coupled_boundary_next_check.py` checks aca_1,aca_4,aca_9,aca_117, plus the
exact saved aca_9 residue stall (xYYXyxxyy,YXXXyxx) with t=y. It originally
used wider support-bounded q,k intervals, then the finite candidate prescription
above. Every displayed best output has an independently replayed strict
ordinary certificate. No strict literal Phi descent was found on these frames;
there is no new solve or ordinary-length claim. The saved stall's original
Phi is3, and even its best zero-shift exchange only ties3.

The obstruction is concrete: the scalar residue2 modulo3 can be changed to-1
in the existing rule, but that does not create the indexed prefix/seam
cancellation required for this coupled exchange to descend. Coprime boundary
coefficients do not give a legal noncommutative Euclidean algorithm. The
Laurent matrix alone cannot justify deleting intervening indexed words.

### Exact obstruction at the saved aca_9 stall

In the literal frame t=y,z=x, the saved positive-stable recipient and donor
collect as

    F = z_0 z_-2^-1 z_-1^2,
    G = z_-1^-3 z_0^2,
    R=F t, Phi=3.

The first letter of F is positive. The first letters of both G and G^-1
are negative. An index shift changes neither sign. Thus no q creates the
necessary initial seam cancellation for either donor sign. The finite
candidate proof therefore gives a complete negative for **all integers q,k**
in this exact coupled exchange family at that frame. It is stronger than
checking small shifts, while remaining explicitly weaker than an AC
obstruction or a statement about independently cyclically reoriented inputs.

The final tiny check compared19 breakpoint candidates with340 wider
support-bounded algebraic candidates on the six frames; both prescriptions
agreed on absence of strict descent, including when k=0 was excluded.
All19 breakpoint move streams and six planted family streams independently
replayed. The six planted checks use m=2,3,5 in both literal generator frames.
The recorded wall time is0.0093s. See `coupled_boundary_next_check.json`.
