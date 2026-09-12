# Constructive theory catalogue

This is the constructive catalogue for the three-hour investigation ending
2026-09-12 at06:28:52UTC. The final numerical answer belongs in
`u124_final_table.md`. A new result here means a proved or implemented
extension in this investigation, not a claim of priority in the literature.

Words use generators x,y; uppercase letters denote inverses. Every displayed
word equality is interpreted after free reduction. A pair has total length
L=|R|+|S|. Ordinary certificates use only relator inversion, right multiplication
by another relator, and conjugation by one signed generator. A conjugating word
is expanded into one such conjugation per letter. Cyclic reduction, rotation,
inversion and relator interchange have explicit ordinary witnesses.

The user also authorized stable AC. Stable composites below retain their exact
definitions, substitutions and invertible basis maps, and have a finite stable
AC realization on these known trivial-group inputs. They are labelled separately
from fully emitted elementary certificates. No inference from unimodular
abelianization alone supplies a stable certificate.

## 1. Residues for a general Miller–Schupp companion shape

For n>=1 and integers k,r,s, define

    R_n = X y^n x y^(-n-1),
    S_(k,r,s) = X y^(-k) X y^r x y^s.

If r=r0+n*u and s=s0+(n+1)*v, then ordinary AC moves give

    (R_n,S_(k,r,s)) ~ (R_n,S_(0,r0,s0)).

The prefix needs at most2|u|+|v|+3|k-n(u+v)| retained-donor multiplications;
the elementary conjugations and inversions cost additional moves. Thus this
infinite companion shape has at most n(n+1) representatives under these
transformations. Balanced residues give a total-length bound3n+6.

The pair trivializes if r=0 modn, or s=0 mod(n+1), or
(r,s)=(epsilon,-epsilon) modulo(n,n+1), where epsilon=+1 or-1.
The last case exposes a genuine BS(1,2) donor; it does not assume that every
BS(n,n+1) companion of stable exponent1 collapses.

For n=2 every residue pair satisfies one of those conditions. Consequently
every MS(2,w) with zero x-exponent and at most one x and one X in the freely
reduced w is ordinary-AC trivial, with arbitrary signed y-powers.

Why the proof is constructive: moving a y^n block across x, or a y^(n+1)
block across X, has an error equal to an explicitly conjugated R_n or its
inverse. Three such uses change k by one while retaining r,s. Two uses change
r by n, and one changes s by n+1. These identities hold for all signed
integer powers. Terminal residues expose a one-occurrence relator or BS(1,2),
and the compiler emits the resulting cleanup.

Real numerical example: n=2,k=1,r=s=1 gives an independently replayed
177-elementary-move trivialization, with maximum individual relator length17.
The example is a mechanism check, not a newly solved U124 row.

Scope in the actual census: the literal three-stable-letter family matches842
of1190 input rows. Its terminal residue criterion covers366; all366 were already
in the saved solved640. Among original unsolved MS cells,338 matches belong to31
retained U124 components. Their residue targets produce no length improvement
over the saved U124 starting minima. These joins use frozen member labels;
no new cell-to-U124 bridge certificate is asserted by that scope scan.
The64 selected residue targets form32 exact Aut orbits, with no newly detected
merger of the retained U124 components.

Proof and code: `ms_family_extensions.md`, `ms_family_verify.py`.
Independent verification: `ms_independent_audit.md`.
Census scope: `ms_census_scope.json`, `ms_residue_class_probe.json`.

## 2. Move a Magnus boundary inward

Choose a literal stable generator t and let z be the other generator.
Write z_i=t^i z t^-i. Collect the two relators as R=F*t and S=G, where
F and G are reduced words in the indexed letters z_i. The support is the
set of indices present; its span is largest minus smallest index.

If span(G)>span(F), a suitable shifted copy D=t^q R t^-q has its indexed
support inside the recipient interval. A lowest-index block H can be changed
to D H D^-1, or a highest-index block to D^-1 H D. Each is a legal
two-donor-use substitution. Repeat it for every run at the chosen extreme,
using the same suitable shifted donor. Each replacement introduces indices
only in the smaller interval; after every occurrence of that extreme is
removed, the selected span strictly decreases. Replacing just one run need
not decrease the span. No run exponent is required to equal1.

This controls indexed support, not ordinary word length. Expanding the indexed
letters back to x,y may produce a longer relator. If alternating this rule
with the power rule below continues to satisfy its hypotheses, the sum of
spans descends to a separately certified terminal case. If a checkpoint fails,
the compiler returns a verified finite prefix and makes no completion claim.

On the literal U124 frames, at least one boundary/power pass occurs on62 rows,
but none solves or gets shorter in ordinary total length. Euclidean relator
preparation creates many more applicable frames, with the same negative
ordinary-length result.

Proof: `astra_patterns.md`. Compiler and independent review:
`boundary_compiler.py`, `boundary_independent_audit.md`.

## 3. Extreme powers, including a nondivisible remainder

Suppose a shifted zero-stable donor can be oriented as

    D=C A E,       A=z_d^m,       B=C^-1 E^-1,       m>0,

and no other letter of D has boundary index d. The exact errors are

    A^-1 B = E D^-1 E^-1,
    A B^-1 = C^-1 D C.

These give explicit one-donor-use replacements. For a boundary run z_d^k,
put eta=sign(k) and r=k-eta*m. The freely equal factorization
z_d^k=z_d^r A^eta permits replacing it by z_d^r B^eta even when
the original literal run contains fewer than m letters.

Accept a step only when |r|<|k|. In particular, a virtual chunk with
0<|k|<m is useful exactly when2|k|>m. This strictly decreases the total
number of occurrences of the selected boundary index, so a fixed-boundary
pass terminates. A nonzero remainder need not remove the boundary; span
and expanded ordinary length need not decrease.

Actual U124 example, retaining donor YXXXyxx:

    xYYxxyyy -> xYYXyxxyy.

The selected indexed power changes2 to-1 modulo3, using five elementary
moves. Multiplicity falls2→1; ordinary recipient length grows8→9; the next
completion test still fails. Both saved occurrences are the same aca_9 state,
not two newly improved rows.

Proof, signed/cyclic cases and459 checks: `extreme_residues_report.md`.

## 4. Change both relators by a shifted row exchange

Again write R=F*t and S=G. Orient/shift S to D=t^q S^e t^-q and put
H=G_q^-1 F, where G_q is its indexed word. Three ordinary AC multiplications
with explicit unary wrappers give, for any integer k,

    (R,S) -> (H*t, F*T^(-k)(H^-1)),

where T shifts every indexed letter by one. The new zero-stable donor is
different, allowing a later rule to face a different obstruction.

For the potential Phi=span(F)+span(G), initial cancellation forces the
unique alignment of the first indexed letters. After that, only support
endpoint alignments, one possible last-letter cancellation alignment, and
the nearest nonzero shifts need consideration. At most12 candidates decide
whether this exact family admits strict Phi descent; this is not a finite
decision procedure for all AC moves.

The five accepted U124 exchanges occur on aca_31,aca_45,aca_61,aca_77 and
aca_107. Each uses11 elementary moves. Phi drops4→3 or6→5, but no ordinary
length drops, and the immediate completion retries fail.

Proof: `coupled_boundary_next.md`. Implementation and full bounded result:
`coupled_exchange_report.md` when finalized.

## 5. Derive substitutions from overlapping donor rules

Each rule L→M retains a factor identity

    L^-1 M = product c_i^-1 R^e_i c_i.

For two overlapping reductions w→u and w→v with factor ledgers A,B, followed
by u→U and v→V with ledgers C,D, the new rule has exact ledger
U^-1 V=C^-1 A^-1 B D. Orienting rules by shortlex makes reduction terminate;
the completion process itself is capped and is not asserted confluent.

This is an implementation of classical critical-pair reasoning, not a new
universal AC theorem. It exposed a generator in the planted pair
(YXYxyx,XYXyy) after56 elementary moves, followed by verified cleanup.
The same bounded mechanism produced no gain on the20-row U124 panel.

Details: `critical_pairs.md`, `critical_pairs_checks.json`.

## 6. Stable defining-word compression

Introduce a fresh z with defining relator D=z^-1 w(x,y). Compress verified
w/w^-1 blocks in both original relators. If one compressed relator contains
exactly one old generator a^epsilon, rotate and solve it for a=v in the
remaining generators. Substitution and deletion leave the exact rank2 pair

    ((z^-1 w)[a->v], compressed_companion[a->v]).

Why this is stable AC here: known group triviality supplies a finite normal
product for w in the old relators. Starting with strict stabilization z,
invert its relator and append that product to obtain z^-1 w. After isolating a and substituting it
out of the other relators, their presentation is still trivial; another
finite normal product clears the defining tail, making strict deletion legal.
The existence proof does not assume the AC conjecture. It does not bound
the cost of finding or expanding those normal products.

The root scans checked200 special-power endpoints,969 general pure-power
endpoints, and1483 literal-word endpoints, with no rank2 U124 improvement. The
literal word scan retains at most64 decompositions per subproblem and uses
defining words of length at most6; it is explicitly incomplete outside that
finite mechanism. Applying the same stable rule after ordinary theory
prefixes checked725 further endpoints on the20-row panel, again with no rank2 gain.

Proof conventions: `STABLE_CERTIFICATE_CONVENTIONS.md`.
Independent algebra/proof review: `stable_independent_audit.md`.

The known primitive-single extension replaces the literal one-occurrence test
with a rank3 primitive-word test. Apply the witnessing Whitehead maps to all
three relators, then remove the exposed basis generator and inspect the full
rank2 quotient. On the original panel excluding AK3,15 such nonliteral quotient
witnesses occur across9 of19 rows, with no rank2 endpoint length gain.
However, an audit of all522 saved macro boundaries found12 shorter rank3
intermediate tuples. Discarding these because the final rank2 endpoint grew
would misreport the user's requested best length at any rank.
The composite may temporarily need
rank4 to implement a rank3 ambient map; no internal word-length peak is claimed.
See `primitive_compression_report.md`.

There is an even simpler stable prefix: retain the entire compressed rank3
tuple without requiring an isolator. If M disjoint signed copies of a word w
are replaced across the two relators, all three new relators have total length

    L_new = L + |w| + 1 - M*(|w|-1).

The |w|+1 term is the complete defining relator z^-1*w. Each replacement
removes |w|-1 letters. The formula counts all relators and gives an exact,
cheap sufficient shortening test. It does not say the resulting search is
easier or that a trivialization has been found.

The audited one-helper scan gives84 shorter rank3 presentations on U124.
Together with the primitive intermediates, the union has85 shorter rows,
initially with aggregate length2356→2198, while the best rank2 aggregate stays2356.
Example aca_59 goes from total20 to the complete tuple

    (Zxx, YZYzyz, YYYYxzzz),

whose three lengths are3,6,8 and sum to17. All84 literal prefixes pass an
independent signed-expansion and rotation check. None of these84 tuples
admits a strict total-length Whitehead descent; that complete90-map test
cost270 individual word images per row.

Two further independently checked operations improve that union. Ordinary
substitutions on aca_24's compressed tuple reduce16→15, with a21-move
elementary suffix; the first15-letter boundary occurs at move17. Recursively
introducing a second defining generator saves one further letter on each of
aca_108,aca_109,aca_111,aca_112,aca_113,aca_114. Those six endpoints have rank4.
The resulting union remains85 rows, with aggregate2356→2191:165 letters
saved while counting every defining relator. There are no new rank2 minima.

The same length formula works at every rank: add one defining relator and
count every replaced block across every existing relator. Accepting only
strict decreases terminates because total length is a nonnegative integer.
This does not prove global optimality: the implementation retains one chosen
shortest next definition, and does not explore length-increasing detours.
See `recursive_stable_compression_independent_audit.md` and
`stable_rank3_ac_independent_audit.md` for exact source joins and certificates.

Code and audit: `stable_dictionary_compression.py`,
`stable_dictionary_independent_audit.md`, `primitive_compression_independent_audit.md`.

## 7. Subgroup completion and the limitation of a negative answer

If the exponent determinant of (R,S) is±1 and some word c satisfies
<R,S,c>=F(x,y), the previously proved cyclic-complement criterion supplies
a one-stabilization trivialization. This is a subgroup-generation condition,
not merely normal generation. The exact finite test identifies vertex pairs
in the folded Stallings graph and asks whether folding gives the full rose.

All124 starting subgroups fail that exact criterion. A capped follow-up on
951 saved new endpoints also finds no witness;123 rows leave states or graph
identifications unchecked. Only aca_117 exhausts that saved endpoint portfolio.
These negative statements are confined to those literal subgroups.

A new finite reduction handles arbitrary conjugation of one relator. For
nonempty cyclically reduced R,S whose combined support is both generators,
there exist words c,w with <R,c^-1*S*c,w>=F2 if and only if some pair of
cyclic rotations of R,S has a cyclic complement. At most |R|*|S| rotation
attachments need consideration. A witness c can be chosen with length at
most floor(|R|/2)+floor(|S|/2).

The proof tracks the two original cyclic graphs inside the bridge-and-loop
graph. A cross-component identification costs no rank; after that at most
one internal identification is available. Taking preimages commutes these
identifications, so a cyclic attachment followed by the usual complement
test suffices. The independent review checks this commutation, folded cores,
signs and the conjugator bound. See `conjugated_complement_theory.md` and
`conjugated_complement_independent_audit.md` for the precise graph proof.

The20-row development panel and the104 remaining inputs each used1000
physical vertex-pair tests per input, without repeating the panel. All124
are still unknown at that cap; no witness was found. This is a bounded
experiment with an exact finite theorem, not a completed exclusion of all
conjugators. All84 shortened dictionary tuples also fail the literal rank3
cyclic-complement criterion, with7672 total identifications and no caps.

The basic finite criterion is from Delgado–Silva,
[On the lattice of subgroups of a free group: complements and rank](https://gcc.episciences.org/6059/pdf).
Code/proof checks: `complement_audit.md`.

## 8. Two infinite exclusions that prevent repeating dead ends

For reciprocal proper BS power corridors, successful full-height transports
would force both |A|>=2^|B| and |B|>=2^|A|. These inequalities contradict
each other. This excludes that synchronized two-corridor construction for
every nonzero pair of heights; it does not exclude interleaved donor changes.

For the specified torus-companion family, projection to C2*C_(2k+1) gives
syllable runs incompatible with any ambient primitive's Christoffel pattern.
This excludes a primitive lift while that donor is retained, under the stated
parameter hypotheses. It does not establish AC nontriviality.

The complete statements, exceptional parameters and independent review are in
`coupled_power_theory.md` and `stable_independent_audit.md`.

## 9. A three-relator power-conjugacy corridor

For signed integers m,k,n, the tuple

    (z x^m y^n, Z x^-m yx, z y^k Z yx)

admits two restored-donor operations exposing

    ((x^-m z) y^k (Z x^m) y^-n, Z x^-m yx, z y^k Z yx).

The genuine free coordinate t=x^-m z then puts it into the form

    (t y^k T y^-n, T x^-2m yx, x^m y^n x^m t)

after two further ordinary donor operations. This is an exact family-level
entry into a conjugacy-of-powers relation, with no root extraction. Its
exponent determinant is k-n. Ordinary trivializations follow when n=0 and
|k|=1, when k=0 and |n|=1, or when m=0 and |k-n|=1; those subfamilies expose
a generator before any stable coordinate change is needed.

The new15-letter aca_24 stable tuple is in this family at(m,k,n)=(2,1,2).
It reaches a BS(1,2) donor, but the remaining independent generator prevents
the rank2 collapse theorem from finishing it. The resulting rank3 total19
does not beat15. All216 tested signed parameter triples pass an independent
integer identity check, and the real seed's two ordinary move segments replay.
See `stable_rank3_patterns.md` and `stable_rank3_patterns_independent_audit.md`.

The final signed extension also proves ordinary triviality when m=-1 and
|k-n|=1. First use the second relator to replace z in the first; it becomes
x*y^(n+1). Substituting x=y^(-n-1) in the other two relators gives

    (x*y^(n+1), Z*y^(-2n-1), z*y^k*Z*y^-n).

The second row now replaces z in the third, producing y^(k-n), a signed
generator. It clears both remaining tails. Every replacement uses a retained
defining relator, so this argument is ordinary AC throughout. The14 signed
fixtures n=-3,...,3 and k=n±1 have1263 explicit elementary moves, independently
replayed by three implementations to exactly(x,y,z).

This is a signed-coordinate extension of the m=0 cleanup mechanism, not a
new independent source of census coverage. The actual aca_24 parameter m=2
does not satisfy it. The proof, coordinate comparison, and complete streams
are in `rank3_corridor_final_analysis.md`,
`rank3_corridor_final_analysis_checks.json`, and
`rank3_corridor_final_independent_audit.json`.

The final analysis also makes the actual obstruction to a naive BS cleanup
explicit. After eliminating the stable letter, its proposed replacement
U=x^(-2m)*yx has exponent vector(1-2m,1). The pair(U,y) has determinant
1-2m, which is -3 at m=2, so it cannot be a free basis. Individual
primitivity of U does not repair this. A separate parameter line n=-1,k=-2
reduces to the existing Miller–Schupp residue cell(1,1); its cited terminal
criterion stops for m>=3. No unproved parameter symmetry identifies that
line with the actual aca_24 seed.

## 10. A cheap exact obstruction for a selected presentation complex

A thickenable balanced presentation of the trivial group has a known AC
trivialization theorem, but recognizing thickenability requires compatible
local rotations, not just a planar Whitehead graph. For a loopless,
3-connected planar simple support, parallel edges form contiguous reversed
blocks in every spherical embedding. The macro rotation is unique up to
global reflection. This statement works at any rank.

For one generator g, let d_g be its number of occurrences. Its positive
and negative germs each have d_g incident slots. For every cyclic phase,
count which parallel classes are paired by reversed slots, and compare
those counts with the actual occurrence-pair counts. If all d_g phases
disagree, no compatible spherical rotation exists. Surviving counts are
only necessary and must not be called a positive witness.

This rejects the16 previously unresolved planar rank3 tuples in309 phase
checks, instead of exploring their factorial rotation spaces. Five of the
six new rank4 tuples have nonplanar support; the remaining one is rejected
in20 phase checks. The newer15-letter aca_24 tuple has a literal K3,3 link.
All92 exact tuples in the combined snapshots therefore have independently
verified obstructions:75 Kuratowski subdivisions and17 rigid block-count
failures. There are145 constructed positive controls, all retained.

These are exclusions of those exact presentation complexes. They do not
exclude a different AC or stable representative becoming thickenable and do
not prove AC nontriviality. The combinatorial implementation and full proof
are in `rank3_neuwirth_extension.md`; the independent witness reconstruction
is `neuwirth_independent_audit.md`.

## 11. Project a marked free kernel to a new stable target

Let P=(R,S) present the trivial group on x,y. Choose two words C,D such that
the four words R,S,C,D generate the full free group. Define the map f from
the free group on r,s,t,u by those four images. Suppose a verified domain
basis (W1,W2,Vx,Vy) has images (1,1,x,y). Its first two basis words normally
generate the kernel of f. Define the projected pair

    Q=(W1(1,1,t,u), W2(1,1,t,u)).

Then P and Q are stably AC-equivalent. Indeed the rank4 tuple
(r,s,W1,W2) presents the trivial group, since its quotient is
F(x,y)/normal_closure(R,S). Clearing and deleting the unit rows r,s gives Q.
The verified ambient basis map sending (W1,W2,Vx,Vy) to (z1,z2,x,y), followed
by clearing and deleting z1,z2, gives P. The known-trivial-group stable
ambient lemma applies without an AC-conjecture assumption. This supplies
an exact stable equivalence, not an ordinary rank2 equivalence.

The initial example uses C=x,D=y^2 for aca_116. It produces the new pair
(yyxYxyxYx, XyXYYxxyXYXX), total21 versus starting14. It lies in a different
Aut orbit. A16-pop S20 continuation reaches18 with an independently replayed
123-elementary-move prefix, still above14 and unsolved. Displayed stable
bridges use rank4; implementing the ambient map may temporarily use rank5,
whose internal word peak is not bounded here.

There is a direct completion rule: once two different basis rows have
images x and y, fix those lifts. Remove the final image letter of any other
row by right-multiplying it by the appropriate signed lift. Its image
length drops exactly one at each Nielsen move, while the domain tuple
remains a free basis. Thus the remaining search is unnecessary. A unit
image x and a row x^p*y^epsilon*x^q, epsilon=+1 or-1, first expose y by the
same exact clearing. Applying this compiler to14 saved capped states gives
all15 full-join projections without new candidate exploration.

Changing complements or retaining different domain markings can matter;
deduplicating only image tuples is an incomplete policy for optimizing the
projected target. Choosing a complement basis of F2 itself gives back the
original problem under the natural, synchronously transported marking;
this does not classify all possible kernel markings. These limitations are explicit in
`two_complement_independent_theory.md`.

The early unit gate recognizes such lifts on each generated child and reserves
the exact remaining compiler work before stopping. On the fixed20-row panel,
15 marked projections use4224 charged image/compiler units in total; the other
five joins are proper. S20 uses the remaining10776 heap pops, making exactly
1000 combined units per searched row. These are heterogeneous work units,
not equal compute. The15 searches cost6.487106 seconds wall and give no solve
or improvement over the original saved lengths. Every ordinary suffix is
emitted:4227 elementary moves in total, separately replayed.

There is a principled complement change for two rejected rows: their second
relators are y^-4*x^n, with n=3 or7, and x is already supplied. Hence the
subgroup contains y^4. Adjoining y^3 makes y available because gcd(3,4)=1.
The same gate followed by remaining-budget S20 produces no gain: aca_115's
projected total22 returns to13, and aca_59's41 returns to20. These additional
attempts each have their own1000-unit limit and must not be combined with the
earlier attempts as a single1000-unit experiment. Negative outcomes do not
rule out other complements or domain markings. In fact these two q3 targets
are exactly ambient returns: for a second relator y^-d*x^n, the natural
q=d-1 construction sends x to x and y to x^n*Y. The inverse sends y to
Y*x^n. Applying these maps to both relators verifies the return without
search. See `two_complement_q3_report.json` and `two_complement_scope_theory.md`.

## 12. Construct a power-complement marking by Euclid, without search

Suppose the second relator is S=y^-d*x^n, where d>=2 and n is an integer.
Choose a positive integer q coprime to d. In the domain free group on
r,s,t,u, send these four generators to R,S,x,y^q. Replacing s by
A=s*t^-n gives image y^-d. The Euclidean algorithm on the two exponent
values -d and q lifts to explicit Nielsen operations on the pair (A,u),
producing a kernel word K and a lift T with images1 and y. Throughout,
the domain words and their order are retained; integer arithmetic alone
would not determine the noncommutative certificate.

Together with the fixed lift t of x, use T to clear the image of r.
This gives the marked basis required by the previous theorem and hence
an explicit stable projected pair, without a Nielsen candidate heap.
For d=2h+1 and q=2, one may take

    H=A*u^h,       T=H^-1,       K=u*H^2.

Their images are respectively y^-1,y,1. After setting r=s=1,
the projected pair, with a permissible inversion of its first relator, is

    (R(t,u^-h*t^n), u*(t^-n*u^h)^2).

The basis construction and inverse maps prove the stable bridge; replacing
all y letters by the displayed lift without this bridge would not itself
be an ordinary AC argument.

For aca_59, invert the second relator and exchange the two ambient axes.
The prepared pair is (XYYXyyxyy,YYYYYYYxxxx), with(d,n,q)=(7,4,2).
The direct unit compiler spends28 preparation/image units, then972 uncapped
S20 pops. Raw projected total60 falls to21, with a430-move ordinary suffix.
This is still longer than the original20. All eight post-search Nielsen
images have larger cyclic total (four25, four22), so the endpoint is
Aut-minimal at21 and is outside the original Aut orbit. These16 extra
word-image evaluations are recorded outside the1000-unit attempt.
The argument classifies the reached endpoint, not automatically the raw
projected pair before the ordinary suffix.

Proof and literal inverse witnesses: `euclidean_power_complement_theory.md`
and `.json`. Exact experiment and independent replay:
`euclidean_power_complement_report.json` and
`two_complement_unit_gate_independent_audit.md`.

## Length accounting

The frozen archival table totals2446. The saved best table already includes36
older reductions and totals2356. Those are distinct from this session's gains.
The audit of5374 saved certificates checks3042053 elementary steps, including
temporary donor states, and finds no overlooked strict minimum. Additional
stable states count all their current relators. The all124 table includes its
starting state for every row, so longer experiments never worsen a row's best.

Component clocks distinguish symbolic work, certificate replay, output and
cooling where measured. These methods use different algebraic charge units;
none of these totals is claimed compute-equivalent to1000 S20 heap pops.
