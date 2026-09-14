# Coupled power corridors: exact feedback and two infinite boundaries

Date: 2026-09-12. Status: independently reviewed proof and machine identities;
see `stable_independent_audit.md`. These results do not solve a U124 row.
Sections1–5 concern ordinary donor-changing prefixes and their limitations.
Section6 additionally supplies theorem-backed stable composites, whose
elementary normal-product expansions have not been emitted.

## 1. Exact family containing the three requested roots

Use literal signed ambient letters a,t and write A=a^-1,T=t^-1. Set

    R = T a^m t a^-n,
    S = t^-(k+1) a^p t^k a^q,
    b = t^-k a t^k.

Here m,n,p,q are integers and k>=0. S is exactly T b^p a^q.
The cases below take a=X,t=y,m=3,n=2,k=2:

| row | p | q | R | S |
|---|---:|---:|---|---|
| aca_116 |1|1|YXXXyxx|YYYXyyX|
| aca_117 |1|-1|YXXXyxx|YYYXyyx|
| aca_9 |2|1|YXXXyxx|YYYXXyyX|

The source CSV orders the first two pairs as (S,R). Reordering here is just
notation; a compiler must choose the corresponding target index.

## 2. A two-use donor-changing corridor

Conjugate R by t^k, obtaining

    Rk = L^-1 H L Q,
    L=t^(k+1), H=a^m, Q=t^-k a^-n t^k.

Write M=a^p t^k a^q, so S=L^-1 M and M=L S. Then

    D = M^-1 H M Q
      = a^-q b^m a^q b^-n,
    Rk^-1 D = (Rk^-1 S^-1 Rk)(Q^-1 S Q).

This last line is a free-group identity. It is an elementary AC compiler:
retain S, append its inverse conjugated by Rk, restore S, append S conjugated
by Q, and restore S. Conjugation by a finite word expands letter by letter.
There are exactly two source multiplications. The p-block disappears by
ordinary commutation of powers of the *same* letter a before free reduction;
no quotient commutation is assumed.

`coupled_power_probe.py` checked36 signed cases with the independent integer
stack replay from `ac_words.py`. Each of the three literal roots has a40-move
prefix. The outputs changing R are

    aca_116 / aca_9: xYYXXXyyXYYxxyy,
    aca_117:         XYYXXXyyxYYxxyy.

Both are length15 before cyclic reduction, compared with the original
length7 donor. Thus this is an exact change of donor, **not length descent**.
It has no new terminal implication merely because it resembles a BS relator
in the two words (a,b): those words are conjugate, and are not a free basis.

### The immediate feedback is a self-loop

If q=1, the retained S gives a=b^-p t. Substituting this into D gives

    D -> t^-1 b^m t b^-n = t^-k R t^k.

The p-powers cancel freely. Therefore the prescribed route “make the
reciprocal power donor, then use S to recover a” returns to a conjugate of
the old donor for every p,m,n,k. Treating the new displayed BS shape as a
descent would conceal this exact self-loop. This statement classifies that
specified immediate return only, not arbitrary further AC moves.

## 3. No synchronized whole-power rectangle for reciprocal proper BS donors

Assume gcd(m,n)=gcd(r,s)=1 and |m|,|n|,|r|,|s|>=2. Consider the two donors

    t^-1 a^m t=a^n,
    a^-1 t^r a=t^s.

For nonzero integers A,B, a direct full-height corridor reducing
t^-B a^A t^B through the first relation is legal exactly when

    |m|^B divides A if B>0,
    |n|^(-B) divides A if B<0.

Indeed, at each of |B| pinches the next divisibility requirement loses one
factor of the incoming exponent and gains a coprime outgoing factor. An
induction gives the stated power. Signs of A,m,n do not change divisibility.
The analogous corridor reducing a^-A t^B a^A through the second relation
requires |r|^A dividing B or |s|^(-A) dividing B according to the sign of A.

If both corridors exist, then

    |A| >= 2^|B| > |B|,
    |B| >= 2^|A| > |A|,

a contradiction. Thus increasing A,B never produces this synchronized
rectangle. The claim permits every finite nonzero A,B and both orientations;
it is not a bounded search failure. It excludes precisely a pair of complete
single-source power transports, not arbitrary mixed-source diagrams.

The reciprocal branch p=1,q=-1 of Section1 gives
a^-1 t^(k+1) a=t^k. Hence this obstruction applies to aca_117 with
{m,n}={r,s}={2,3}. Cases with a power of absolute value1 fall outside the
theorem and include the successful BS(1,2) mechanisms.

## 4. The other branch is a torus donor, not reciprocal BS

For m,k>=1 consider

    R_m = T a^(m+1) t a^-m,
    S_k = t^-(k+1) a t^k a.

Use the actual ambient free basis (u,t), where u=a t^k and a=u t^-k.
The inverse formulas are explicit. In these coordinates S_k is conjugate to

    u^2 t^-N,   N=2k+1.

Specifically S_k=t^-(k+1) u^2 t^-k, so conjugating on the left by t^(k+1)
produces the displayed torus relator. This coordinate calculation is for
the exclusion proof; it is not emitted as a simultaneous AC move.

In the torus quotient G=<u,t | u^2=t^N>, further quotient by the central
power gives H=C2*C_N. The changed other relator is

    R_m = T (u t^-k)^m u t U (t^k U)^(m-1).

Here U=u^-1. Replacing each U by u in H gives a cyclically reduced alternating
word with exactly2m+1 u-syllables. Its cyclic sequence of intervening t
exponents modulo N is

    [-k] repeated m times,
    [1],
    [-(k+1)] repeated m-1 times,
    [-(N+1)].

No entry is zero modulo N. The last entry includes the initial T after the
cyclic cut. Forgetting it is an off-by-one error.

### Primitive-image exclusion for k>=2

The abelianization of G assigns [t]=2,[u]=N, and [R_m]=1. Suppose the
image of R_m were conjugate to the image of an ambient primitive P. Write
(e_t(P),e_u(P))=(h,j). Necessarily

    2h+Nj=1.

Thus j is odd and nonzero, h and j have opposite signs, and

    k <= |h|/|j| <= k+1.

The rank-two primitive classification says that a cyclic representative is
a signed Christoffel word. Consequently it has |j| occurrences of u, all with
one sign, separated by t-runs of lengths k or k+1, all with the other sign.
For |j|=1 one of those two lengths occurs. Projection to H causes no syllable
cancellation, because k and k+1 are strictly between0 and N. Its cyclic
t-residues therefore lie in the set {k,k+1}; the same set occurs with either
orientation because N=2k+1.

Conjugate cyclically reduced words of syllable length>=2 in a free product
have the same syllable sequence up to cyclic rotation (the factors here are
abelian cyclic groups). But R_m has the two residues1 and N-1=2k. For k>=2
neither belongs to {k,k+1}. This is a contradiction.

It follows that **for every m>=1,k>=2, retaining S_k cannot turn R_m into an
ambient primitive using any number of multiplications by conjugates of S_k,
with arbitrary conjugation/inversion of R_m**. Such operations preserve its
conjugacy class, up to inverse, in G. This is an infinite fixed-donor
exclusion, not an AC obstruction. aca_116 is m=k=2.

### Edge k=1

Now N=3 and the two residue values alone do not obstruct. The syllable count
forces |j|=2m+1. The only exponent pairs are

    (h,j)=(-3m-1,2m+1), (3m+2,-2m-1).

For the first sign, primitive t-run lengths are1 or2, with m runs of length2
and m+1 of length1. Their circular binary sequence is balanced. The R_m
sequence consists of a single block of m+1 ones and a single block of m
twos, up to a cyclic cut. For m>=2 it has length-two subwords with zero and
two twos, contradicting balance. Complementing the binary sequence treats
the other sign. Hence the same fixed-donor exclusion holds for k=1,m>=2.

The remaining m=k=1 case has matching Christoffel projection. This note
does not infer a lift merely from that match; the original donor there is
BS(2,1), so the established BS(1,2) theorem already gives ordinary AC
triviality. The m=0 or k=0 cases are outside the displayed theorem; they
have an immediate primitive/BS(1,2) simplification.

The finite checker independently verifies the coordinate equality, the
exponent formula, all cyclic normal forms and both necessary primitive
candidates for1<=m<=7 and1<=k<=6. Only(m,k)=(1,1) matches in H. These42
checks verify formulas and small edge cases; the preceding proof supplies
the unbounded statement. They are not presentation searches.

### Primitive classification source

The only external input above is the standard rank-two primitive/Christoffel
classification and its balanced run description. Primary references:
[Gilman–Keen, Enumerating Palindromes and Primitives in Rank Two Free Groups](https://arxiv.org/html/0802.2731),
especially the primitive-exponent discussion in Section5, and
[Kassel–Reutenauer, Sturmian morphisms, the braid group B4, Christoffel words
and bases of F2](https://arxiv.org/pdf/math/0507219), Section3. All torus
coordinate and relator calculations in this note are derived above and
checked in `coupled_power_checks.json`.

## 5. Scope and next constructive requirement

These calculations separate two easy-to-confuse roots: aca_117 defeats the
synchronized reciprocal power rectangle; aca_116 defeats arbitrary
primitive lifting while its torus companion is retained. aca_9 is neither
of those special branches, and no exclusion for it is claimed beyond the
explicit feedback self-loop in Section2.

A constructive continuation must change the companion after the new donor
has been installed, or use a mixed-source diagram whose corridor cannot be
split into the two prohibited full-height rectangles. It must retain an
actual source ledger. Merely adjoining b as a generator, treating(a,b) as a
free basis, or deriving a consequence and then replacing its own source by
that consequence is insufficient.

## 6. Stable-AC extension authorized later in this investigation

The user subsequently allowed stable AC. The following uses the proved
substitution-and-removal and stable ambient-automorphism lemmas in
`git show codex/proofs:literature/proofs/AK3_RANK3_COMPRESSION.md`, Sections1–3.
Its cross-reference to `literature/proofs/PROOFS.tex` is stale in the inspected
checkout; the self-contained proof below and
`STABLE_CERTIFICATE_CONVENTIONS.md` supply the needed argument. The
trivial-group hypothesis applies to the Miller–Schupp inputs. We distinguish
these **theorem-backed stable macro witnesses** from fully expanded
AC1–AC5 move ledgers. The latter were not produced in this subtask.

#### Self-contained reason defining generators are stable-AC composites here

Let a tuple of old relators present the trivial group on the old generators.
Then every finite old word w is a finite product of conjugates of signed old
relators: this is exactly the definition that their normal closure is the
whole free group. Apply AC4 to adjoin b with relator b, invert that relator,
and append the factors of such a normal-product expression for w. Each
factor is appended by temporarily conjugating/inverting its old source,
multiplying the new relator, and restoring that source. The result is
b^-1 w. Thus adding a defining generator is a finite stable-AC composite.
The normal-product expression exists because of triviality; it is not
claimed to have been constructed in these macro files.

For deletion, first use an available defining relator g^-1 v to substitute
g=v in every other relator by the ordinary source-restored substitution
identity of Section2 of the cited note. The remaining relators are now g-free.
Their presentation on the retained generators is trivial: eliminating a
unique-occurrence defining generator gives an explicit group isomorphism,
and the original group was trivial. Hence v is a finite normal product of
these remaining relators. Append its inverse normal product to g^-1 v,
leaving g^-1; invert and apply AC5. This proves the deletion composite without
assuming that arbitrary Tietze moves are themselves AC moves.

Similarly, a stable ambient-automorphism macro can be implemented by adjoining
defining generators for an explicit free-basis automorphism and eliminating
the old generators through its explicit inverse formulas. This proves finite
stable equivalence of the recorded Nielsen steps. The isolator construction
stays at rank3, and subsequent rank2 Nielsen changes use at most one temporary
generator at a time. Thus rank at most3 is guaranteed for these records.
The existence proofs do not supply a practical elementary move count or
peak word-length bound without the normal-product ledgers.

### A checkable pure-power compression family

Choose one literal generator a, a power d>=2, and one source relator. After
a cyclic cut, suppose all maximal a-runs except one have exponent divisible
by d, and the exceptional run has exponent congruent to epsilon=+1 or-1.
Introduce b=a^d. Compress the d-multiple parts of all runs. The source becomes
an explicit word I with exactly one a^epsilon. Write I=P a^epsilon Q.
Conjugate to a^epsilon QP and isolate

    a=v, with v=(QP)^-1 if epsilon=+1 and v=QP if epsilon=-1.

Here v is a word in the retained original generator and b. With D=b^-1 a^d,
the final rank-two pair is exactly

    ( b^-1 v^d, companion[a -> v] ).

Before elimination the companion may also be compressed using D. Each
chosen run identity is a^e=b^q a^r or a^r b^q, where e=dq+r. The machine
witness retains q,r and the chosen order. This is a finite, explicitly
checkable family of stable coordinate changes, not an assertion that a^d
is an ambient primitive or that a Tietze isomorphism alone is sufficient.
The accepted stable defining-generator lemma is the relevant extra theorem.

For the consecutive BS source R=T a^(m+1)t a^-m there are two especially
short isolators:

| definition | freely expanded isolator | recovered a |
|---|---|---|
| b=a^m | T a b t B | t b T B |
| b=a^(m+1) | T b t B a | b T B t |

Expanding b in either isolator freely gives R. In the second line the
hidden spelling a^-m=a^-(m+1)a is essential. The resulting donor is always
B v^d. These are actual stable equivalences under the cited lemma, even
when v is not primitive in the original basis.

For the sandwich source S=t^-(k+1)a^p t^k a^q, adjoining b=t^k gives
I=T B a^p b a^q and recovers t=B a^p b a^q. This covers the torus branch
aca_116 omitted by a literal-BS-only scan.

### A broader literal defining-word family

Let w be any nonempty free word. Find a literal compression I of one cyclic
source spelling by replacing disjoint w/w^-1 blocks with b/b^-1. Require
that I have exactly one occurrence of an old generator g and at least one
b. Independently compress any disjoint w/w^-1 blocks of the companion to
a word C. Require the exact free identities

    I[b -> w] = oriented source,
    C[b -> w] = original companion.

Introduce b=w, use its definition for these two ordinary substitutions,
isolate g=v in I, and apply substitution-and-removal. The final pair is

    ((b^-1 w)[g -> v], C[g -> v]).

This is precisely the rank-three isolator corridor theorem, applied to
arbitrary literal MS sources. It is a constructive mechanism, not a new
general theorem beyond that cited corridor lemma. Its literal implementation
does not cover all hidden-cancellation templates.

### Measured root scans

All scans read `data/ms_unsolved_reps/aca_124_best.csv`; they did not rerun
presentation searches. Strict eight-Nielsen length descent was applied only
to explicitly constructed endpoints. Failure to shorten through these maps
is not asserted to be an exhaustive automorphism-orbit classification.

| declared mechanism | matched rows | evaluated templates/endpoints | strict gains over input | wall seconds |
|---|---:|---:|---:|---:|
| the two BS power definitions, all signed literal axes/source cuts |49|see per-row counts|0|0.1034|
| generic literal pure-power residue isolators |115|969|0|0.3301|
| non-power literal defining words of length2–6 |124|1,483 distinct endpoints|0|1.5553|

The first scan also found no equal-length endpoint: every retained candidate
is longer than its input. Its best results at the requested roots are
aca_9:15→19, aca_116:14→20, and aca_117:14→20. Therefore none of this
subtask's stable witnesses improves a final best-length table, and no
trivialization is obtained.

The generic pure-power scan uses the two placements of the exceptional
single letter relative to its b-power. It does not enumerate arbitrary
split powers b^r a^epsilon b^s. It retains one locally shortest companion
run-replacement choice. The literal word scan uses all cyclic cuts, both
elimination axes, source-dependent candidate subwords, disjoint substitution
DP, and companion compression before elimination. Candidate defining words
contain both generators and are rejected if the declared primitive-reduction
filter reaches length1. Each DP subproblem retains at most64 decompositions;
each row is limited to500 distinct evaluated endpoints, and no row limit was
reached. Internal DP truncation was not separately instrumented. No negative
statement beyond these declared mechanisms follows.

Files:

- `coupled_power_stable_probe.py/.json`: the two BS power definitions.
- `coupled_power_general_compression.py/.json`: generic pure-power templates.
- `coupled_power_word_compression.py` and
  `coupled_power_word_compression_all124.json`: bounded non-power templates.

Each literal-word best witness records the original pair, defining word,
cyclic prefix/cut, compressed isolator, eliminated generator/sign, recovered
word, compressed companion, raw rank-two endpoint and Nielsen images.
Its `recorded_rank3_boundary_max_total_length` sums **all three relators**
at the saved displayed rank-three boundaries. It is not an elementary peak
length bound, and displayed rank3 is not a bound on the rank needed by a
fully expanded realization of the stable composite lemmas. Both distinctions
must survive any final report.
