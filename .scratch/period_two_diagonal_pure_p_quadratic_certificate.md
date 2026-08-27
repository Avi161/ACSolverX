# Diagonal pure-\(P\) quadratic certificate

## Status

**PROVEN.** For

\[
q_i=A_{i+1,i+1}+A_{i,i},
\]

the complete new--new quadratic contribution is

\[
\boxed{Q(q_i)=1\qquad(i\geq0).}
\]

This certificate proves only that scalar theorem and its already-derived
diagonal consequences. It does not prove the free-group period-two lift,
AK(3), stable Andrews--Curtis, or Andrews--Curtis.

## Independent proof paths

The primary producer reconstructs 46 signed path contexts, collision-splices
them to 42 active coordinates, adds the twelve slot-zero tokens, and obtains
a 48-chord matching on the resulting 96-token stream. Its three positive
slot orders have sizes \(9,15,18\); all 39 adjacent comparisons are formal
all-power comparisons. The four exhaustive cells are

\[
i=0,\qquad i=1,\qquad i=2,\qquad i\geq3.
\]

In every cell the 48 prefix parities are

```text
000111010110011000111000110001000001110010100101
```

and have integer sum 21. Thus their xor is one. No expected value of
\(Q\) occurs in the producer.

The independent replay does not import either the primary quadratic checker
or the raw producer. Starting from the low-level source rows and reviewed
normalizer, it independently reconstructs:

- 46 signed contexts from 39 distinct source rows;
- 152 common-phase schemas and 608 cell templates, including the formal
  \(i\geq3\) cell and a direct \(i=4\) expansion witness;
- 44 collision fibers, of which 42 are active with profile \((9,15,18)\);
- all 96 decorated tokens and their literal AST polarities;
- the corrected 48-chord endpoint topology and all 1,128 chord-label pairs;
- the sole repeated chord label, whose two chords are nested; and
- both the 48-row prefix sweep and an explicit 4,560-pair direct kernel
  ledger at each cell base.

The prefix and direct kernel routes agree in every cell without reading the
primary scalar output. Thirteen hostile independent tests and eighteen
primary tests pass under the guarded proof runner. Primary manifest write
and byte-for-byte check also pass.

## Frozen hashes

| artifact | SHA-256 |
| --- | --- |
| primary checker | `1188ec9526f70b4cb73f252dff36e139ad4b966b69cc47afa30ec54688b8190c` |
| primary tests | `587752a614eafe1221c59b405add04de1ac3b4250eea48644496f8a44fb96c50` |
| primary manifest | `99684dd413382cff52fd596bbf4713cbe3e8398af7ca3086bf12084ad27b8b06` |
| independent replay | `753f2fca9e40d4e1a013ca3b2c454bb137ef6ff3e68ed47f7cdb005c80576c8c` |
| independent tests | `ba15767f6d607559ae6055c86729589d5934fb409069d51601c1b63f8b2243bd` |

The primary theory binding uses two exact unique intervals only: Sections
5.1--5.3 and Section 7.1 through the explicit certificate-interface end
marker. The theorem below that marker does not change either bound interval.

## Consequences

The separately proved terms are

\[
L(q_i)=0,
\qquad
\mathbb B(A_i^\Delta,q_i)=1.
\]

Therefore

\[
\boxed{
\mathscr C(A_i^\Delta,q_i)
=L(q_i)+\mathbb B(A_i^\Delta,q_i)+Q(q_i)=0.}
\]

The established row reduction gives

\[
\mathscr C(A_i^\Delta,q_i)=c_{i+1}+c_i,
\qquad
u_{ij}=c_i+[j=i].
\]

Hence all \(c_i\) are equal. The exact seed \(u_{00}=1\) gives
\(c_0=0\), so

\[
\boxed{c_i=0,\qquad u_{ij}=\delta_{ij},\qquad
\mathcal D_{ij}=0.}
\]

Consequently the complete \(i\)-edge law is

\[
\boxed{I_{ij}=[i-j=-1]+[i-j=0].}
\]

The last-coordinate first-family unary matrix is therefore an infinite
identity matrix. This proves infinite rank for that narrow unary
contribution, even after the row-only and constant rank-one terms. It does
not decide the unresolved companion cross kernels or the full Hessian rank.

## Exact boundary

All statements above live in the complete-cover/\(c^2=1\) reduction. They
neither construct a lift of the quotient witness to \(F(c,t)\) nor cancel
its nonabelian residual in \([N,N]\). A literal free-group solution or an
exact impossibility theorem remains necessary. Even a successful lift still
needs a separately proved implication to the AK(3) move/factorization
target.
