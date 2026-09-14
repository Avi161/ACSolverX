# Independent audit of the MS residue family

Status: **the stated mathematical results pass this audit for every integer
parameter in their stated domain**: n>=1 and k,r,s in Z. A missing cyclic
conjugation in the original terminal compiler was found and corrected during
the audit. The corrected constructor passes the independent checks below.
This is a mathematical review with finite implementation checks, not formal
proof-assistant verification or a claim of bibliographic priority.

Audited artifacts are `ms_family_extensions.md`, `ms_family_verify.py`, and
the eight stored certificates in `ms_family_checks.json`. Exact hashes of
these files, `ac_words.py`, and the audit script are in
`ms_independent_audit.json`. The checks fail if a source changes during a run.
Later regeneration of an author artifact requires rerunning the audit to pin
the new bytes. No frozen production files were edited.

## Finding corrected during review

The original `primitive_cleanup` counted stable letters before cyclic
reduction. Consequently `solve(2,0,1,0)`, `solve(3,0,1,0)`, and
`solve(4,-2,3,-5)` failed with `AssertionError` even though their residue
criterion is satisfied. In the first example the normalized companion is
`XXyx`; it has three stable letters as written but is conjugate to `Xy`.
The proof already made the necessary distinction between free reduction for
r0=0 and cyclic reduction for s0=0.

The corrected entry now calls `e.orient(i,core(e.pair[i])[1])` before counting.
`orient` emits ordinary generator conjugations; the correction is not an
unrecorded canonicalization. All three original failures, the signed case
`(2,0,-1,0)`, and the fully degenerate `(2,0,0,0)` pass both independent replay
implementations. No remaining correctness gap was found in the claimed domain.

## All-integer verification of the shift

Write R=`X y^n x y^(-n-1)`, S=`X y^-k X y^r x y^s`, and let T0,...,T5 be
the six successive recipients displayed in the author's shift proof. Here
conjugation by q means q^-1 W q. The following explicit witnesses remove any
dependence on an unproved relation-level rearrangement:

| Recipient change | Sign applied first | Conjugator q |
|---|---:|---|
| S to T0 | -1 | `y^-s X y^-r x` |
| T1 to T2 | -1 | `X` |
| T3 to T4 | +1 | `x y^(k-n)` |
| T5 to S_(k+1,r,s) | +1 | `x` |

The remaining three changes satisfy `U^-1 V = c^-1 R^sign c` with these
literal free-group witnesses:

| Recipient change | Donor sign | Conjugator c |
|---|---:|---|
| T0 to T1 | -1 | `y^(n+1-s) X y^-r x` |
| T2 to T3 | -1 | `y^s X y^(n-k) X` |
| T4 to T5 | +1 | `X y^r x y^s X` |

These equalities follow by concatenation and free cancellation with signed
powers. They remain valid when powers vanish or a displayed boundary cancels;
they require no divisibility condition. The audit script checks these seven
explicit identities at 300 signed parameter points independently of the
author's `witness` routine.

For a general replacement PLQ -> PMQ, the recipient difference is
`Q^-1 L^-1 M Q`. Thus if `L^-1 M=q^-1 R^sign q`, the temporary donor is
conjugated by qQ. Invert the donor when necessary, conjugate, right multiply
the recipient, and reverse the donor's unary operations. This preserves R
exactly and uses one multiplication. It is stronger than asserting equality
in the quotient by R. Applied to the table, it proves the k increase with
exactly three multiplications. Reversing the resulting ordinary certificate
gives the k decrease with the same multiplication count; its extra donor
inversions are unary moves.

The primitive transfer identities (3) and (4) also check algebraically:

* For `L=y^a x y^b`, the free reduction of `L^-1 M` is
  `y^-b X y^-n x y^(b+n+1)`, equal to the claimed conjugate of R^-1.
* For `L=y^a X y^b`, it is
  `y^-b x y^(-n-1) X y^(b+n)`, equal to the claimed conjugate of R.

There is no assumption here that a displayed `y^a` block is a positive word.
The certificate implementation works with reduced free-group words after
every operation.

## Residue bound and terminal proof

The r transfer has parameter change `(-n,-n,0)` and costs two retained-donor
multiplications. Its first application of (3) changes r to r-n and s to s+n+1;
the second transfer removes the added s power. The s transfer has change
`(-n,0,-n-1)` and costs one multiplication. Its local identity
`x y^s X -> x y^(s-n-1) X y^n` has error a conjugate of R; it is valid for
every signed s.

Therefore r=r0+n*u and s=s0+(n+1)*v give outer parameter
`K=k-n(u+v)` after the signed transfers. Removing K with the shift proves
the claimed bound `2|u|+|v|+3|K|`. Negative u,v and K use reversed
certificates, not an unjustified extension of a one-sided loop. Selecting one
residue per modulus leaves at most n(n+1) representatives. Nothing proves
their pairwise inequivalence, so this is an upper bound only.

Balanced representatives satisfy
`|r0|+|s0| <= floor(n/2)+floor((n+1)/2)=n`. Since R has length 2n+3 and
S_(0,r0,s0) has length at most 3+|r0|+|s0|, their total freely reduced length
is at most 3n+6. Zero powers and cancellations only improve this bound.
It is an endpoint bound, not a bound on intermediate lengths or on the full
number of elementary moves.

For r0=0 or s0=0, the recipient is, respectively, freely reduced or explicitly
cyclically conjugated to `X y^q`. Replacing both x letters of R by the
appropriate y powers gives y^-1; the retained primitive recipient then
finishes by deleting its y letters. The ledger certifies every substitution.

For `(r0,s0)=(epsilon,-epsilon)`, the other donor is BS(1,2) in the literal
letters a=x, b=y^-epsilon. These letters are notation for signed original
generators; the emitted moves do not apply an ambient automorphism. The
remaining R has b exponent ±1. A cyclically reduced word of that exponent
with more than one stable letter has both signs, and its cyclic stable-letter
sequence contains a negative-to-positive transition. Thus it has a pinch
`b^-1 a^j b`; j cannot be zero in a reduced word. The positive and negative
unit transfer identities replace it by `a^(2j)`, decreasing stable-letter
count by two. Repeating terminates at one stable letter regardless of growth
in the a powers. The final primitive substitution gives a^-1 and completes
the ordinary AC proof. This argument uses the coefficient-one side of
BS(1,2); it does not claim the same consequence from exponent ±1 for a
general BS(n,n+1) donor.

For n=2 the six residue pairs are all terminal: an even r gives r0=0; a
multiple-of-three s gives s0=0; otherwise choose s0=±1 and the representative
r0=-s0 of the odd r class. The proof invokes neither AK(2) nor a saved search
certificate.

The arbitrary-word reduction also survives boundaries. With exp_x(w)=0 and
at most one occurrence of each signed x letter, a freely reduced w is either
a y power or `y^a x^epsilon y^b x^-epsilon y^c`. For epsilon=-1, Xw is
S_(-a,b,c). For epsilon=+1, rotating the formal final X to the front gives
S_(-c,a,b). Conjugation of the unreduced factorization proves the same equality
after any free cancellations. The tests include both orders, zero exterior
powers, zero interior powers that cancel the stable pair, and pure y words.

## Primary-source comparison

[Appendix A of Shehper et al., NeurIPS 2025](https://proceedings.neurips.cc/paper_files/paper/2025/file/ea8c9cd935dc62e0288bbf33a15e65e9-Paper-Conference.pdf)
was checked directly. A.6 fixes r=s=1 while varying k. A.7 concerns a further
presentation of that same family. A.9 deduces its n=2 triviality using known
AK(2) triviality. A.2 already covers all MS(1,w), and A.3 covers
`w=y^-1 x y X`, which is the opposite-unit representative S_(0,-1,1) after
rotation. The new text therefore contains known subfamilies. Its specific
extension relative to this appendix is the arbitrary signed r,s shift plus
independent residue transfers and their stated consequences. This is not a
duplicate claim for the old k shift, but broader literature priority has not
been established by this audit.

## Reproducible finite checks and data scope

Run the repository virtualenv's Python on
`research/theory_patterns_20260912/check_ms_independent.py` from this worktree.
It uses its own signed-integer free-group implementation, independently
validates operation schemas, and also translates each certificate to
`ac_words.replay`. Both replayers accept only the three ordinary AC moves.
Full elementary lists for six adversarial certificates are saved in the JSON;
all other generated cases have reproducible parameter records and exact
endpoint, multiplication count, total move count, and peak relator length.

The audited snapshot passes 392 primitive free-word identity checks, 2,100
explicit shift-witness equalities, 300 shift certificates, 300 balanced
normalizations, 76 terminal certificates, six boundary certificates, 97
arbitrary-w certificates, and eight stored certificates. All 787 certificates
pass both independent replayers. The complete run used approximately 0.51
CPU seconds, with no heap search or JIT.

A separate integer-word scan rechecks both U124 input tables using both
relator orders, all eight signed generator maps, cyclic reduction, rotations,
and inversion. A three-stable-letter cyclic word with stable exponent ±1
always has the displayed companion shape after a cyclic orientation and
possibly inversion, so this scan does not rely on the author's regular
expression. It reproduces zero matches in each exact 124-row table. All input
relators were already cyclically reduced; a one-stable-letter check made
before cyclic reduction therefore caused no missed matches in these tables.
The result establishes no new census coverage and says nothing about possible
matches after donor-changing prefixes.
