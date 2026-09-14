# Independent review of the marked two-complement bridge

Verdict: **PASS** for the general stable-equivalence proof and the literal
`aca_116` marking. The companion JSON independently replays all15 retained
marked bases from the frozen20-row prototype, checks both inverse
compositions, and checks the exact positive kernel projections in both
markings. It pins the reviewed source report and prose hashes. No candidate
search was rerun. Ordinary AC equivalence is not asserted.

## Why the stronger stable-equivalence proof works

Let f:F(r,s,t,u)->F(a,b) have a verified basis
B=(W1,W2,V1,V2) with f(B)=(1,1,a,b). In the B coordinates, f is literally the
projection killing the first two basis letters. Therefore

    ker(f) = normal_closure(W1,W2).

For P=(f(r),f(s)) known to present the trivial group, the balanced rank-four
tuple T=(r,s,W1,W2) presents

    F4 / <<r,s,W1,W2>> = F2 / <<f(r),f(s)>> = 1.

This establishes T's triviality before using the stable ambient-change lemma.
There is no circular appeal to the AC conjecture or to Q being already solved.
The two required quotient markings are different and must not be conflated:

* Killing the original letters r,s in W1,W2 gives Q in the original t,u.
* Killing the first two **B-coordinate** letters in the inverse-basis images
  of the original r,s gives P in the marked V1,V2 coordinates.

The verified inverse map theta takes W1,W2 to literal unit basis letters.
Thus applying theta to T and clearing those two unit donors gives the literal
P, including its signs and row order. Conversely, adjoining unit r,s to Q
and reinserting the deleted letters into each projected Wi gives T. The exact
right-multiplication correction for that latter step is
pi(Wi)^-1 Wi, which lies in <<r,s>>. Unit-donor insertion also gives an explicit
finite implementation without a group word-problem oracle.

The ambient theta step has a finite stable AC realization because T is known
trivial. Its basis is supplied with a Nielsen row path, so it decomposes into
finitely many elementary ambient Nielsen changes. The accepted defining-word
lemma realizes each with one temporary helper, reused after elimination.
The four displayed generators may therefore require rank5 internally.
There is no basis for a rank4-only claim or a bound on the unexpanded
normal-product lengths.

For the exact positive record, the independent computation gives

    P = (YYYXyyX, YXXXyxx),                              length14,
    Q = (yyxYxyxYx, XyXYYxxyXYXX),                     length21,
    T = (r,s,uurtUturtUt,TuTRUUttuTRUsTT),              length28,
    theta(T) = (UrUUrTsuRuTs,UrTsTsTsutSt,r,s),         length26.

The theta(T) words use the positional coordinate alphabet r,s,t,u. Killing
its first two coordinate letters in its first two rows gives P exactly.
The two stabilized endpoint lengths are16 for P plus two units and23 for Q
plus two units. All relators are counted; strict-move intermediate peaks are
not supplied by these macro boundary lengths.

The root's separately recorded16-pop ordinary continuation lowers this Q to
length18. That does not beat P's14. Its search certificate is outside this
proof audit, and no additional candidate exploration of this frame was run.

## Deterministic unit-lift completion lemma

Suppose a retained F4 basis has two distinct rows Vx,Vy with f-images exactly
x,y. Keep these two rows fixed. If another basis row U has image
c1...cL, right-multiply U by the lifted letters cL^-1,...,c1^-1 in that order.
Each multiplication is an elementary Nielsen row operation using one of the
fixed lift rows or its inverse. At each step the image loses exactly its last
letter. Consequently the other two rows become kernel rows in exactly the
sum of their image lengths many multiplications, while the complete domain
tuple remains a free basis. Reordering gives (W1,W2,Vx,Vy).

Signed unit rows are inverted first. If one row has image X and another has
XXY or XXy, two left multiplications by the inverse X-row strip the XX prefix,
then a sign correction produces the desired units. This is deterministic
certificate compilation, not heap exploration. Its word-image work must
nevertheless be reported separately when it extends an already exhausted
prototype budget.

More generally any two rows whose image pair has a supplied free-basis
inverse can first be Nielsen-normalized within those two rows, then used as
fixed lifts. A generating-subgroup assertion alone is insufficient unless
the required basis transformation is actually provided. Unknown search
prefixes with no such verified pair remain unknown.

## Proper complement choices and redundant searches

The meaningful choice is usually the proper subgroup H=<C,D>, together with
the marked kernel construction, rather than a cosmetic change of its basis.
Precisely, let eta be a domain automorphism fixing r,s and making a Nielsen
change of t,u. Replacing f by f'=f eta and transporting the marked basis to
eta^-1(B) gives the new complements. The projected pair is then

    pi(eta^-1(Wi)) = alpha^-1(pi(Wi)),

where alpha is the induced automorphism of F(t,u). Thus this synchronized
basis change of the same complement subgroup produces only an ambient
Aut(F2) change of Q. This statement does **not** claim that arbitrary,
independently chosen kernel markings for the same subgroup are always
ordinarily AC-equivalent or Aut-equivalent.

The prototype deduplicates states by their image tuple, while their domain
markings can differ. That is valid for a bounded feasibility search, but
cannot certify an optimum projected length: pi(Wi) is not determined by the
image tuple. A future projected-length search should retain this distinction
or explicitly state its pruning. No such extra search was run here.

## A checkable shortcut that recovers the old isolator route

Suppose C=a, D=w(a,b), and one input relator has an exact freely checked
expression

    R_i = P(a,D) b^epsilon Q(a,D),  epsilon=+1 or-1.

Let r_i be its domain tag and lift b by

    Vb = (P(t,u)^-1 r_i Q(t,u)^-1)^epsilon.

It contains r_i exactly once, so replacing r_i by Vb is a free-basis change
fixing the other tag,t,u. Together with Va=t it supplies literal unit images.
Complete the kernel basis by clearing the other two rows. After killing the
tags, put h=pi(Vb). A convenient resulting projected pair is

    (u w(t,h)^-1, R_j(t,h)^-1).

This is exactly the existing stable defining-word isolator endpoint, up to
row inversion and conjugation. It is a useful deterministic compiler, but
should not be counted as new algebraic coverage when that isolator was
already screened. This equivalence concerns this specific natural marking,
not every possible marked kernel basis for the same complements.

For the current C=x,D=y^2 instance, the exact identity

    y = (R x D^-1 x D)^-1

gives V_y=U T u T R in F(r,s,t,u), with V_x=t. Taking

    W1 = u V_y^-2,
    W2 = s S(t,V_y)^-1

gives a verified marked basis. Its explicit15-operation Nielsen row path and
both inverse compositions are in the JSON. The projected pair is

    (yxYxyxYxy, XYxyxxxYXyX), total20.

This was obtained by one deterministic identity, without new complement or
projected-state enumeration. It reproduces the already studied power-isolator
route and is worse than the root's new length18 continuation. It supplies no
new minimum or solve.

For genuinely different future complement choices, the useful targets are
proper subgroups whose two relators contribute interdependent lift information
that does not reduce to this single-isolator template, or different retained
kernel markings whose projected words are structurally simpler. Short proper
power subgroups can be tested by their exact Stallings join, but unimodular
abelianization alone does not prove a full join. Choosing two complements
that already form an ambient basis, or the intentionally cancelling tag
complements excluded by the task, offers no new content under their natural
markings. No new proper-complement scan is claimed in this note.

## Independent review of deterministic completion artifacts

The subsequently frozen `two_complement_direct_completion_report.json`, SHA256
`bec4e53329a749e04739f0e22eef1639fed0e22adf615fa92c0dc374c1411107`, passes the
independent review recorded in the companion JSON. All15 exact source-prefix
links, full Nielsen paths, every compiler image state, both inverse-basis
compositions, both endpoint markings, and canonicalization conjugators/signs
were independently recomputed. All117 deterministic compiler operations and
30 projections agree with their ledgers. The225 canonicalization operations
are separately recorded. No heap, candidate-image exploration, or baseline
run was performed by this audit.

| Input | Original length | Canonical projected length | Compiler operations |
|---|---:|---:|---:|
| aca_116 |14|21|0|
| aca_1 |15|29|5|
| aca_30 |17|27|4|
| aca_55 |18|33|6|
| aca_80 |19|39|8|
| aca_82 |22|49|12|
| aca_109 |23|30|11|
| aca_101 |25|49|11|
| aca_117 |14|20|4|
| aca_9 |15|22|4|
| aca_67 |20|33|11|
| aca_86 |22|51|12|
| aca_106 |21|37|11|
| aca_54 |19|26|9|
| aca_5 |19|38|9|

The canonical projected words are all cyclically reduced and each has a
mixed-sign generator. None is a literal singleton. This is not an exclusion
of primitive relators after further AC moves. The `aca_54` projection has a
literal BS(6,7) donor; its companion's two opposite-sign stable gaps have
exponents2 and-4, failing the required7 and6 divisibilities respectively.
Thus that direct Britton reduction does not start. This does not exclude a
different donor-changing route.

There is one additional exact ordinary reduction in the new `aca_1` frame.
Its first projected relator `XXYxxyy` can be inverted/rotated to

    R = XXyxxYY,   expressing x^-2 y x^2 = y^2.

Here x^2 is a proper-power stable word, **not** a free-basis generator. The
usual rank-two BS(1,2) theorem for arbitrary companion therefore cannot be
applied automatically. Nonetheless its individual donor identities are
valid ordinary AC substitutions:

    XXYxx -> YY,
    XXyxx -> yy.

The saved companion admits these two exact pinches in sequence:

    XXXYxxyXXYxyxxYXXXyxxY
      -> XYXXYxyxxYXXXyxxY
      -> XYXXYxyxxYXy.

The complete two-relator lengths are29 ->24 ->19. The JSON contains all41
strict elementary moves, including normalization and restored-donor uses,
and an independent replay. The final pair is

    (XXyxxYY, XYXXYxyxxYXy), total19.

Its remaining opposite-sign x-blocks do not contain a complete legal x^2
pinch. This is only a literal-syntax stopping observation. The original
`aca_1` total15 is still shorter, so the new certificate changes neither the
all124 minimum nor the solved count.
