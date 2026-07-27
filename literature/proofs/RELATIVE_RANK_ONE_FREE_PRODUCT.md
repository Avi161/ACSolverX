# Relative rank one in a free product

## Statement

Let

\[
P=A*C
\]

be a free product, let \(u\in P\), and let

\[
\Phi_u:A*\langle s\rangle\longrightarrow P
\]

be the homomorphism which is the identity on \(A\) and sends \(s\) to
\(u\).

If \(u\notin A\), its reduced free-product normal form has a unique
decomposition

\[
u=a_0wa_1,
\tag{1}
\]

where \(a_0,a_1\in A\), either of them may be the identity, and the
nonempty reduced word \(w\) begins and ends with a \(C\)-syllable.  We
call \(w\) the **\(A\)-trimmed core** of \(u\).  For \(u\in A\), define
the \(A\)-trimmed core to be \(1\).

The exact criterion is

\[
\boxed{\Phi_u\text{ is injective}
\quad\Longleftrightarrow\quad
\text{the \(A\)-trimmed core of \(u\) has infinite order}.}
\tag{2}
\]

In particular, if \(A*C\) is torsion-free, then

\[
\Phi_u\text{ is injective}\quad\Longleftrightarrow\quad u\notin A.
\tag{3}
\]

The assumption in this corollary cannot simply be omitted.  The
condition that \(u\notin A\) and \(u\) itself has infinite order is not
enough.

## 1. The two obstructions

If \(u\in A\), the source word

\[
su^{-1}
\]

is nontrivial in \(A*\langle s\rangle\) and belongs to
\(\ker\Phi_u\).

More generally, suppose \(u\notin A\) and write it as in (1).  Define

\[
\alpha_{a_0,a_1}:A*\langle s\rangle\longrightarrow
A*\langle s\rangle
\]

to be the identity on \(A\) and

\[
\alpha_{a_0,a_1}(s)=a_0sa_1.
\tag{4}
\]

This endpoint modification is a relative Nielsen automorphism.  Its
inverse fixes \(A\) and sends

\[
s\longmapsto a_0^{-1}sa_1^{-1},
\tag{5}
\]

as is checked on the free factors.  If
\(\Psi_w:A*\langle s\rangle\to P\) fixes \(A\) and sends \(s\) to
\(w\), then

\[
\Phi_u=\Psi_w\circ\alpha_{a_0,a_1}.
\tag{6}
\]

Thus \(\Phi_u\) is injective exactly when \(\Psi_w\) is injective.  If
\(w\) has finite order \(n\geq1\), then \(s^n\) is a nontrivial
element of \(\ker\Psi_w\), and

\[
\alpha_{a_0,a_1}^{-1}(s^n)
\]

is a nontrivial element of \(\ker\Phi_u\).  This also covers the
internal case if the trimmed core is defined to be \(1\).

Finite order of \(u\) is therefore an obstruction, but it is not the
whole obstruction.  For a concrete example, take

\[
A=\langle a\mid a^2=1\rangle,\qquad
C=\langle c\mid c^2=1\rangle,\qquad
u=ac.
\]

The word \(u\) has infinite order in \(C_2*C_2\): every positive power
\((ac)^n\) is already a nonempty reduced word.  It also lies outside
\(A\).  Nevertheless its \(A\)-trimmed core is \(c\), of order two,
and

\[
a u a=u^{-1}.
\]

Consequently the nontrivial reduced source word

\[
asas
\]

maps to \(auau=1\).  This disproves the tempting criterion
``\(u\notin A\) and \(u\) has infinite order'' for arbitrary free
factors.

An outside torsion element gives the simpler failure: if
\(u\notin A\) has finite order \(n\), then \(s^n\) itself is a
nontrivial kernel word.  The example above shows why one must also
inspect the trimmed core when \(u\) has infinite order.

## 2. Power-endpoint lemma

We use only the normal-form theorem for free products: a nonempty
alternating sequence of nonidentity syllables from the two factors
represents a nonidentity element.

**Lemma.** Let \(v\) be a nonempty reduced word in a free product
\(X*Y\).  Suppose that its first and last syllables lie in the same
factor and that \(v\) has infinite order.  For every
\(n\in\mathbb Z\setminus\{0\}\), the reduced normal form of \(v^n\)
is nonempty and begins and ends in that same factor.

**Proof.** We first prove the assertion for positive powers by
induction on the syllable length \(\ell(v)\), simultaneously for words
whose endpoints lie in \(X\) and words whose endpoints lie in \(Y\).

If \(\ell(v)=1\), then \(v\) is a single syllable in one factor.
Infinite order says precisely that \(v^n\neq1\) for every \(n>0\).
Hence the reduced normal form of \(v^n\) is one nonidentity syllable
in that factor.

Now let \(\ell(v)>1\).  Because the endpoint factors agree and factors
alternate, \(\ell(v)\) is odd, hence at least three.  Write the first
and last syllables as \(d\) and \(e\), in the common endpoint factor.
There are two cases.

If \(ed\neq1\), then in a product of positive copies of \(v\), each
seam reduces only by replacing the adjacent pair \(e,d\) by the single
nonidentity syllable \(ed\).  Its two neighboring syllables, when
present, lie in the other factor, so this merge creates no further
reduction.  All seams are separated by the unchanged interior of a
copy of \(v\).  Thus every \(v^n\) has a nonempty reduced form with
first syllable \(d\) and last syllable \(e\).

If \(ed=1\), then \(e=d^{-1}\), and

\[
v=d\,r\,d^{-1},
\tag{7}
\]

where \(r\) is a nonempty reduced word of length
\(\ell(v)-2\) whose first and last syllables lie in the other factor.
Conjugation preserves order, so \(r\) has infinite order.  By the
simultaneous induction hypothesis, the reduced normal form of \(r^n\)
is nonempty and begins and ends in the other factor for every \(n>0\).
Therefore

\[
v^n=d\,r^n\,d^{-1}
\tag{8}
\]

is reduced at both displayed seams and begins and ends in the original
endpoint factor.

This proves the positive-power assertion for both possible endpoint
factors.  Finally, \(v^{-1}\) has infinite order and begins and ends in
the same factor as \(v\), because inversion reverses the syllables but
does not change their factors.  Applying the positive-power assertion
to \(v^{-1}\) proves the claim for every \(n<0\).  This also shows
explicitly that no zero power is being considered: \(v^0=1\) has no
endpoints. \(\square\)

The infinite-order hypothesis is load-bearing already in the
length-one case.  A finite-order syllable has a positive power equal
to the empty word.  In the cancellation branch (7), it is exactly the
infinite order of \(v\) that guarantees the shorter conjugate \(r\)
has infinite order and permits the induction.

## 3. Sufficiency

Assume the \(A\)-trimmed core \(w\) has infinite order.  In particular,
it is nonempty and begins and ends in \(C\).  By (6), it is enough to
prove that \(\Psi_w\) is injective.

Let \(q\) be a nontrivial reduced word in
\(A*\langle s\rangle\).  If \(q\) contains no
\(\langle s\rangle\)-syllable, then \(q\) is a nonidentity element of
\(A\), and \(\Psi_w(q)=q\neq1\).

Otherwise its reduced normal form can be written

\[
q=b_0s^{n_1}b_1s^{n_2}\cdots b_{k-1}s^{n_k}b_k,
\tag{9}
\]

where \(k\geq1\), every \(n_i\) is nonzero, every internal
\(b_i\) with \(1\leq i<k\) is nonidentity, and the endpoint terms
\(b_0,b_k\) are allowed to be the identity.  Zero powers do not occur
as syllables in a reduced free-product normal form.

By the lemma, the reduced normal form of every \(w^{n_i}\), including
every negative power, is nonempty and begins and ends in \(C\).
Substitution in (9) gives

\[
\Psi_w(q)=
b_0w^{n_1}b_1w^{n_2}\cdots b_{k-1}w^{n_k}b_k.
\tag{10}
\]

At every internal seam the three adjacent blocks have factor types
\(C\mid A\mid C\), and the middle \(A\)-syllable is nontrivial.
Hence no cancellation or same-factor merge is possible there.
Likewise, a nontrivial endpoint \(b_0\) or \(b_k\) lies in \(A\) next
to a \(C\)-endpoint of a power of \(w\).  After the already-reduced
forms of the powers are inserted, (10) is therefore a nonempty
reduced free-product word.  Thus \(\Psi_w(q)\neq1\).

Every nontrivial source word has nontrivial image, so \(\Psi_w\), and
hence \(\Phi_u\), is injective.  Together with Section 1 this proves
(2).

## 4. Torsion-free specialization

If \(P=A*C\) is torsion-free, every nonidentity element of \(P\) has
infinite order.  For \(u\notin A\), the \(A\)-trimmed core is a
nonempty reduced word, hence is nonidentity and has infinite order.
The theorem gives injectivity.  For \(u\in A\), the first obstruction
in Section 1 gives noninjectivity.  This proves (3).

For the intended application, once

\[
B=BS(3,4)
\quad\text{and}\quad
G=B*\langle z\rangle
\]

have independently been proved torsion-free, the specialization says
that

\[
B*\langle s\rangle\longrightarrow G,\qquad s\longmapsto u,
\]

is injective exactly when \(u\notin B\).  The torsion-free statements
are separate inputs; no finite normal-form computation can establish
them, and they are not assumed in the general theorem above.
