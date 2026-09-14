# Constructive residue reduction for two-stable-letter MS companions

## Result and scope

Use uppercase for inverses, and write powers with signed integer exponents.
For n>=1 and k,r,s in Z, let

    R_n = X y^n x y^(-n-1),
    S_(k,r,s) = X y^(-k) X y^r x y^s.

The pair is MS(n,w) for w=y^(-k) X y^r x y^s. The following statements use
ordinary elementary AC moves, with no stabilization or ambient automorphism.

**Residue-reduction theorem.** If r=r0+n*u and s=s0+(n+1)*v, then

    (R_n,S_(k,r,s)) ~AC (R_n,S_(0,r0,s0)).                 (1)

A constructive prefix uses at most

    2|u| + |v| + 3|k-n(u+v)|                             (2)

multiplications by conjugates of the retained R_n. Every such multiplication
is expanded below into ordinary generator conjugations, relator inversions,
and right multiplication. The count (2) excludes these unary moves.

**Terminal residue theorem.** The pair is ordinary-AC trivial if at least one
of the following conditions holds:

- r=0 modulo n;
- s=0 modulo n+1;
- for some epsilon in {+1,-1}, r=epsilon modulo n and s=-epsilon modulo n+1.

**Two-stable-letter MS(2) theorem.** Every MS(2,w) for which the freely reduced
w contains at most one x and at most one X is ordinary-AC trivial. The
hypothesis exp_x(w)=0 is the standard MS hypothesis. There is no restriction
on the number of y letters, their signs, or the total word length.

For arbitrary n, (1) reduces this entire companion shape to at most n(n+1)
AC-equivalence representatives. These representatives need not be distinct
AC classes. Failure of the sufficient terminal criterion proves no obstruction.
The same-sign residue classes include AK(n); the theorem does not solve AK(3).

## The elementary replacement ledger

For words L,M with L^-1 M=q^-1 R^epsilon q, an occurrence P L Q in a
recipient can be replaced by P M Q while retaining donor R:

1. Temporarily invert R if epsilon=-1 and conjugate it to
   Q^-1 q^-1 R^epsilon q Q.
2. Right-multiply the recipient by that temporary donor.
3. Restore the donor by reversing its temporary unary operations.

Free reduction gives P M Q exactly. Conjugation by a word is a sequence of
conjugations by its individual letters. Thus this is an ordinary elementary
AC certificate, not merely equality in a one-relator quotient.

The two power transfers required in the proof have explicit free-word errors.
For arbitrary integers a,b, let

    L = y^a x y^b,             M = y^(a-n) x y^(b+n+1).

Then

    L^-1 M = q^-1 R_n^-1 q,    q = y^(b+n+1).             (3)

For

    L = y^a X y^b,             M = y^(a-n-1) X y^(b+n),

one has

    L^-1 M = q^-1 R_n q,       q = X y^(n+b).             (4)

These identities are identities in the free group after reduction, including
negative and zero exponents. Each application therefore costs one donor
multiplication, regardless of the sizes of a,b. Moving a larger multiple of
the defining power costs a repeated sequence of these unit transfers.

## An unrestricted outer-power shift

For every n>=1 and k,r,s in Z,

    (R_n,S_(k,r,s)) ~AC (R_n,S_(k+1,r,s)).                (5)

Here is the full relation-level calculation; the displayed rearrangements
are conjugations or inversions of the recipient relator only.

Start from the second relation written as

    y^k x y^(-s) = X y^r x.

Apply (3) to its left side:

    y^(k-n) x y^(n+1-s) = X y^r x.

Rearrange, then apply (3) again:

    y^r x y^(s-n-1) = x y^(k-n) x,
    y^(r-n) x y^s = x y^(k-n) x.

Rearrange, then apply (4):

    y^(n-k) X y^(r-n) = x y^(-s) X,
    y^(-k-1) X y^r = x y^(-s) X.

The last equality is precisely x=y^(-k-1) X y^r x y^s. There are three
relation uses. Reversing this certificate decreases k by one at the same
relation-use cost. No divisibility condition on k,r,s is used in (5).

For an explicit relator-level implementation, the six intermediate recipients
are, in order,

    y^k x y^-s X y^-r x,
    y^(k-n) x y^(n+1-s) X y^-r x,
    y^r x y^(s-n-1) X y^(n-k) X,
    y^(r-n) x y^s X y^(n-k) X,
    y^(n-k) X y^(r-n) x y^s X,
    y^(-k-1) X y^r x y^s X.

Alternating transitions are unary reorientations and donor replacements;
reorient the final word to S_(k+1,r,s). The compiler records every operation
rather than treating cyclic canonicalization as a free unexplained move.

## Independent residue transfers

A unit decrease of r by n is obtained by two retained-donor uses:

    S_(k,r,s) -> S_(k,r-n,s+n+1) ~AC S_(k-n,r-n,s).       (6)

The first transition is X y^n x=y^(n+1) inside the relevant powered block.
For the second, cyclically orient the companion as

    x y^(s+n+1) X y^-k X y^(r-n).

The identity x y^(s+n+1) X = x y^s X y^n gives the claimed endpoint.
The same second transition by itself gives

    S_(k,r,s) ~AC S_(k-n,r,s-n-1).                       (7)

Both statements admit negative powers and can be reversed. Apply (6) u times
with the appropriate sign and (7) v times. The new outer parameter is
K=k-n(u+v). Apply (5) |K| times with the opposite sign to make it zero.
This proves (1) and the relation-use bound (2).

Balanced integer residues satisfy |r0|<=floor(n/2) and
|s0|<=floor((n+1)/2). Thus the resulting pair has total freely reduced
length at most 3n+6. This is a strict endpoint length reduction whenever
the actual input total length exceeds that bound. Individual intermediate
words can be longer, so this is not a monotone length-reducing algorithm.
The bound is sufficient; cancellations can improve it.

## Constructive terminal completion

If r0=0, free reduction gives S_(0,0,s0)=X y^s0. If s0=0, cyclic reduction
gives a conjugate of X y^r0. Both have one stable letter. Use that relator to
replace x by the appropriate y-power in R_n. The donor becomes y^-1; delete
all y letters from the companion and correct signs/order to finish at (x,y).
Every replacement uses the same elementary ledger.

For opposite unit residues, set r0=epsilon and s0=-epsilon. The second
relation is

    x = X y^epsilon x y^-epsilon,

or

    b^-1 a b = a^2,       a=x, b=y^-epsilon.             (8)

This is a literal BS(1,2) donor in a signed permutation of the original basis.
The retained original relator R_n has b-exponent +1 or -1. Any cyclic
companion of that stable exponent which has more than one b-letter has both
signs, hence a cyclic subword b^-1 a^j b. Repeated unit substitutions
b^-1 a^sign -> a^(2sign) b^-1 collapse that pinch, removing two stable
letters. Repeat until there is one stable letter. Its base exponent may grow,
but its stable-letter count strictly decreases at every pinch.

Orient this final companion to b a^q, substitute b=a^-q into (8), and obtain
a^-1. Delete a-letters from the companion and correct signs/order. All
intermediate relators and every generator-level move are replayed by the
attached verifier. No claim that exp_b=±1 alone suffices for BS(n,n+1) with
n>1 is used: the donor has already changed to BS(1,2) before this argument.

For n=2, choose r0=0 if r is even. Otherwise r can represent either +1 or
-1 modulo 2. Choose s0=0 when 3 divides s; choose s0=+1 or -1 otherwise,
and choose r0=-s0. Consequently every residue pair reaches a terminal case.
This supplies the two-stable-letter theorem without invoking AK(2) as a
black box.

## From an arbitrary word w with one x and one X

If w has no stable letters, x=w is already a one-stable-letter relator.
Otherwise write

    w = y^a x^epsilon y^b x^-epsilon y^c.

For epsilon=-1, the standard recipient Xw is S_(-a,b,c).
For epsilon=+1, rotate Xw starting at its final X; it becomes S_(-c,a,b).
These are explicit cyclic conjugations and cover cancellations as well: begin
with the freely reduced w, and interpret all displayed words after reduction.
Thus the theorem applies to both stable-letter orders, with arbitrary signed
outer y-powers. It is not a theorem for w containing x^2 and X^2.

## Verification and exact data scope

`ms_family_verify.py` is a standalone, search-free certificate constructor.
It emits only relator inversion, conjugation by one signed generator, and
right multiplication by the other relator. Relator interchange at the end is
expanded into those same operations. A second, separate word reducer replays
all certificates from the exact initial words.

`ms_family_checks.json` stores the tested parameters, complete elementary
move lists, exact endpoints, peaks, and input hashes. Eight planted signed
and zero-power cases independently pass both the three-use shift and the
residue reduction; their complete trivializations end exactly at (x,y).
The cases include n=1,2,3,5, both signs, negative quotient transfers and
zero exponents. These finite checks verify the implementation; equations
(3)--(7) and the stable-letter induction prove arbitrary-parameter scope.

A finite literal scan tested both relator orders, all signed generator
permutations, cyclic rotations, and inversions in the exact initial and best
U124 CSVs. Neither table has any pair with a literal consecutive-BS donor and
a one-stable-letter companion or a three-stable-letter companion of the
displayed form. The donor parameter is inferred from its exact cyclic length;
there is no parameter cutoff. Hence this result claims
no U124 solve or new census coverage. It may apply after a donor-changing
prefix, but no such prefix is supplied here. U124 denotes retained components
from a bounded AC search modulo Aut, not 124 proved distinct AC classes.

No heap search was run. The compiler is a proof artifact and is not integrated
into the frozen policy. It does not claim an optimized recognition cost or a
1,000-unit implementation bound; generator-level certificates can be much
longer than (2), and BS(1,2) powers can grow exponentially with n.

## Relationship to the existing work

The NeurIPS paper's Appendix A proves the k-shift for the special case r=s=1,
and uses it with AK(2). The extension here is that the same elementary
calculation works for arbitrary signed r,s; the independent residue transfers
then give a finite classification bound, a general sufficient congruence
criterion, and the entire two-stable-letter MS(2) class. This does not assert
bibliographic priority beyond the sources inspected.

The existing `SHORTCUT_CATALOGUE.md` supplies conditional consecutive-BS and
BS(1,2) completions, but not this two-parameter residue transfer. The
`BS23_NEW_FAMILY.md` family is a different late donor-changing splice shape;
its D_h,W_(p,h) parameters are not used here. The fixed-donor Britton
obstruction in `bs23_residual_theory.md` remains valid: normalization preserves
the three-stable-letter shape until the terminal donor change, and no
fixed-BS(n,n+1) primitive completion is asserted for a stalled companion.

Source checked: [Appendix A of the NeurIPS 2025 paper](https://proceedings.neurips.cc/paper_files/paper/2025/file/ea8c9cd935dc62e0288bbf33a15e65e9-Paper-Conference.pdf),
Theorems A.6/A.7 and Corollary A.9. The source-specific summary in the preceding
paragraph is separate from the new identities proved here.
