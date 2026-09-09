# Completion rules for the stalled consecutive-BS family

Companion to [`PATH_MINING.md`](PATH_MINING.md).  Everything asserted here as
*proved* also has a machine check in
[`verify_stalled_bs_examples.py`](verify_stalled_bs_examples.py); every
positive certificate quoted below was decoded with
`certificate_decoder_compact_moves.decode_elementary` and replayed with
`certificate_decoder.replay_elementary` to literal `['x','y']`.

```bash
PYTHONPATH=. python3 research/residual_20260909/theory/verify_stalled_bs_examples.py
PYTHONPATH=. python3 research/residual_20260909/theory/verify_stalled_bs_examples.py --full
```

`--full` adds the batch of §4.1: it compiles and replays Rule BS-DEMOTE for
every demotable stalled root in the census (427 rows, ~20 s).  The recogniser,
the carry lattice and the compiler live in
[`bs_normal_form.py`](bs_normal_form.py).

## 1. Conventions

Alphabet `xXyY`, uppercase = inverse; moves are the ordinary elementary AC
moves of [`primitive_patterns.md`](../../supermoves_20260908/primitive_patterns.md)
(invert a relator, multiply one relator on either side by the other, conjugate
by an arbitrary word), and the search's Definition 2.1 packaging
`r_i <- rot_{k1}(r_i) . rot_{k2}(r_{3-i}^{jsign})` from
`experiments/equivalence_classes/lib/words.replay_move`.  A signed permutation
of `{x,y}` is an ambient automorphism, not an AC move; it is carried by
`primitive_patterns.md` §2 transport and is recorded as such.

Recognition follows `bs_preflight.donor_orientations` exactly.  A donor is

```text
R = b^-1 a^m b a^-(m+1)          (length 2m+3, so m = (|R|-3)/2)
```

so in `G = <a, b | R> = BS(m, m+1)` we have `b^-1 a^m b = a^(m+1)`, and the two
**carry identities** are

```text
b    a^(k(m+1))  =  a^(km)     b          (E+)
b^-1 a^(km)      =  a^(k(m+1)) b^-1       (E-)
```

The companion `W` is described cyclically by its stable-letter signs
`d_1..d_s in {+1,-1}` (the `b^{±1}` occurrences) and by the gaps `g_1..g_s`,
where `g_i` is the `a`-exponent between stable letter `i` and stable letter
`i+1` (cyclically).  This is literally the data `bs_preflight` builds.  Write
`M(+1) = m+1` and `M(-1) = m`; the gap to the right of a stable letter of sign
`d` reduces modulo `M(d)`.

`epsilon = sum d_i` is the stable exponent; the gate requires `|epsilon| = 1`,
so `s` is odd.

Throughout, `m >= 2`.  (For `m = 1` every `(-,+)` pinch is legal because the
modulus is 1, so `bs_preflight` never rejects - see Lemma 4.1 - and there is no
stalled family.)

## 2. The stall is permanent while `R` is untouched

**Definition.** A *W-move* is any AC move that does not change `R`: conjugation
of either relator, inversion of `W`, relator swap, and
`W <- g^-1 W g . h^-1 R^{±1} h`.  The census's Definition 2.1 substitution with
target `W` is a W-move.

**Lemma 2.1 (unit carry = one AC move).**  Replacing one factor `b a^(m+1)` by
`a^m b` (or `b^-1 a^m` by `a^(m+1) b^-1`) inside `W` is exactly one Definition
2.1 substitution on `W`.

*Proof.*  Write `W = P (b a^(m+1)) Q`.  Then
`P a^m b Q = (P b a^(m+1) Q) . Q^-1 (a^-(m+1) b^-1 a^m b) Q`, and
`a^-(m+1) b^-1 a^m b` is the rotation of `R` starting at its last letter.  So
the new word is `W . Q^-1 R Q`.  Rotating `W` so that `Q` comes first,
`rot(W) = Q P b a^(m+1)`, and `rot(W) . rot(R) = Q P a^m b`, which is the
rotation of the new word by `Q`.  Cyclic reduction and canonicalisation are
what `replay_move` already does.  `(E-)` is the same computation with `R^-1`. ∎

This is verified constructively: in the 427 census certificates of §4 every
single carry was realised by a Definition 2.1 move found and checked with
`replay_move` (`bs_normal_form.find_move` / `run_plan`).

**Theorem 2.2 (stall invariance).**  Let `(R, W)` be a consecutive-BS pair with
`|epsilon| = 1` and let `s_red` be the number of stable letters in a cyclically
Britton-reduced form of `W`.  Then `s_red` is unchanged by every W-move.  In
particular, if `bs_preflight` rejects `(R, W)` with `s_red > 1`, it rejects
every pair reachable from `(R, W)` by W-moves.

*Proof.*  A W-move multiplies `W` by a conjugate of `R^{±1}`, which is trivial
in `G`, and conjugates the result; so the image of `W` in `G` changes only
within its conjugacy class.  `G` is the HNN extension of `<a> = Z` with
associated subgroups `<a^m>`, `<a^(m+1)>` and stable letter `b`.  By Britton's
lemma and the conjugacy criterion for HNN extensions, a cyclically reduced word
of stable length `>= 1` is conjugate to another one only after a cyclic
permutation and a conjugation by an element of an associated subgroup, and both
preserve the stable length; so the stable length of a cyclically reduced
representative is a conjugacy invariant.  `bs_preflight` is exactly a cyclic
Britton reduction, so it computes that invariant. ∎

**Empirical check.**  On the 584 solved stalled-root census paths there are
7,558 states at which `R0` is still the recognised donor.  `bs_preflight`
accepts at 0 of them and reports a constant `stable_letters` on each path
(section B of the verifier).

**Theorem 2.3 (no census terminal without touching `R`).**  Let `(R, W)` be
stalled with `m >= 2` and `s_red = 3`.  No pair reachable by W-moves is
accepted by any of the four terminal recognisers used by the census policy,
*except* the pairs produced by Rule BS-DEMOTE (§4).

*Proof.*  `R` itself is neither two-block (it has four cyclic blocks
`b^-1, a^m, b, a^-(m+1)`) nor one-occurrence (`m >= 1` gives `2m+1 >= 3`
`a`-letters and 2 `b`-letters), so the two-block and one-occurrence gates can
only fire through the companion.
(i) *Two-block.*  A two-block cyclic word `a^p b^q` has all its stable letters
of one sign, so `|epsilon| = s`; here `|epsilon| = 1 < 3 <= s`.
(ii) *One-occurrence.*  Every word in the coset has at least `s_red = 3`
`b`-letters, so it is not one-occurrence in `b`.  If it had one `a`-letter, two
of its three gaps would be 0; a zero gap between opposite signs cancels and
lowers `s`, contradicting Theorem 2.2, and the only same-sign junction in the
pattern `(eps, eps, -eps)` is one gap; so at least two gaps are nonzero.
(iii) *BS gate with donor `R`.*  Theorem 2.2.
(iv) *BS gate with donor `W`.*  `W` must then itself be a consecutive-BS
relator.  Its stable letter cannot be `b`: a BS relator has stable-letter
exponent 0 in its own base letter, but `b`-exponent is a homomorphism killing
`R`, hence constantly `epsilon = ±1` on the coset; and it has only two
`b`-letters, fewer than `s_red = 3`.  So `W` is `a^-1 b^(m') a b^-(m'+1)` up to
rotation/inversion/sign; that word has `2m'+1` stable letters, its `(+,-)`
junction gap is `±1` and its `(-,+)` junction gap is `∓1`, neither divisible by
`m` or `m+1` for `m >= 2`, so it is already Britton-reduced and
`2m'+1 = s_red = 3`, i.e. `m' = 1`.  The remaining freedom is `u = 0`,
`{v, w} = {+1, -1}` - the two words of Rule BS-DEMOTE. ∎

Verified over a bounded cone (`|u| <= 4`, gaps up to `3M`) for `m = 2,3,5,7` in
section C of the verifier: the only companions in the cone that are BS-shaped
or certified are those with `(u, |v|, |w|) = (0, 1, 1)`.

**Cost of ignoring this.**  On the solved paths alone the frozen policy spent
7,558 `bs_preflight` calls / 59,414 scans on states Theorem 2.2 rules out in
advance.  On the 18 unsolved stalled rows, Stage 3 received only 120 units and
spent a large part of them the same way.

## 3. Classification of the stalled `s_red = 3` family

Fix `R` and a Britton-reduced companion with `s = 3`.  The sign necklace is
`(eps, eps, -eps)`; rotate so it reads in that order and call the gaps
`(u, v, w)` (`u` at the `(eps,eps)` junction, `v` at `(eps,-eps)`, `w` at
`(-eps,eps)`).  Put `(M_v, M_w) = (m+1, m)` if `eps = +1` and `(m, m+1)` if
`eps = -1`.

**Stall criterion.**  `bs_preflight` rejects iff `v ≢ 0 (mod M_v)` and
`w ≢ 0 (mod M_w)`.  (These are exactly its two pinch tests.)

**Lemma 3.1 (carry lattice).**  The three unit carries act on `(u, v, w)` by
adding

```text
eps = +1 :  c0 = (-(m+1), 0, m)    c1 = (m, -(m+1), 0)    c2 = (0, m+1, -m)
eps = -1 :  c0 = (-m, 0, m+1)      c1 = (m+1, -m, 0)      c2 = (0, m, -(m+1))
```

and `c0 + c1 + c2 = (±1, 0, 0)`.  The lattice they generate is

```text
L = Z e_u  +  M_v Z e_v  +  M_w Z e_w .
```

*Proof.*  `c0 + c1 + c2 = (n - m, 0, 0) = (1,0,0)` for `eps=+1` (resp.
`(-1,0,0)`), so `e_u in L`; then `c0 + (m+1) e_u = (0,0,m)` and
`c2 + (0,0,m) = (0, m+1, 0)`, giving the stated inclusion; conversely each
`c_i` lies in the stated lattice.  The index is
`|det| = |M_v M_w| = m(m+1)`. ∎

**Theorem 3.2 (complete invariant).**  Two stalled `s_red = 3` pairs over the
same `R` are joined by W-moves iff their reduced gap triples agree modulo `L`,
i.e. iff `(v mod M_v, w mod M_w)` agree.  Define

```text
alpha = v mod M_v,   beta = w mod M_w,
label(R, W) = ( m, min{ (alpha', beta'), (M_v - alpha', M_w - beta') } )
```

where `(alpha', beta')` is `(alpha, beta)` if `eps = +1` and
`((-beta) mod (m+1), (-alpha) mod m)` if `eps = -1`.  Then `label` is invariant
under rotation, inversion of either relator, relator swap, all eight signed
permutations of `{x,y}`, and every W-move; and equal labels imply an explicit
AC path (a relabelling followed by at most `|c0|+|c1|+|c2|` carries) between the
two normal forms.

*Proof.*  Lemma 3.1 gives the W-move part.  Inverting `W` maps a `+1` pattern
with `(v, w)` to a `-1` pattern with `(v', w') = (-w, -v)`, which is the
`eps = -1` normalisation above.  Replacing `a` by `a^-1` fixes `R` up to
inversion and negates all gaps, giving the second candidate in the `min`.
Replacing `b` by `b^-1` maps `R` to a donor the recogniser still reads with the
same `m` and flips all signs, which composes with the previous two into the
same orbit (checked, section A: the label is constant on all eight signed
permutations for every sample).  The number of stalled classes for a given `m`
is `(M_v - 1)(M_w - 1) = m(m-1)`, halved by the `a -> a^-1` symmetry. ∎

**Corollary 3.3 (`m = 1` and `m = 2`).**  There is no stalled `s_red = 3`
class for `m = 1`, and exactly one for `m = 2`, namely `(2,1,1)`.

**Census consequence.**  The 602 stalled-BS census rows carry only 18 distinct
labels (table in `PATH_MINING.md` §5), and no label is both solved and
unsolved.  Rows sharing a label are AC-equivalent by an explicit bounded move
sequence; section F of the verifier carries out the transport for
ac19_102 / ac19_103 (class `(5,2,4)`, common normal form
`('YYxxyxxxx','YXXXXXXyxxxxx')` after the relabelling `x -> X`) and for two
class-`(2,1,1)` rows.

## 4. Rule BS-DEMOTE (proved)

**Lemma 4.1 (`m' = 1` always pinches).**  Let `(V, C)` be a consecutive-BS pair
with `V` a BS(1,2) relator and `C` any companion of stable exponent `±1`.  Then
`bs_preflight` accepts.

*Proof.*  With `m' = 1, n' = 2`, the `(-,+)` pinch test is "gap divisible by
`m' = 1`", which every integer passes.  Any cyclic sign sequence containing
both signs has a `(-,+)` adjacency, so a pinch is always available; each pinch
removes two stable letters.  The reduction therefore runs until all signs
agree, i.e. until `s = |epsilon| = 1`, which is acceptance. ∎

**Rule BS-DEMOTE.**

*Hypotheses.*  A canonical pair one of whose relators is a consecutive-BS
relator `R` of parameter `m >= 2` (recognised up to rotation, inversion,
relator swap and signed permutation by `bs_preflight.donor_orientations`); the
companion has stable exponent `±1`; its cyclic Britton reduction has
`s_red = 3`; and its label satisfies

```text
(alpha, beta) = (1, M_w - 1)   or   (M_v - 1, 1),      i.e.  label = (m, 1, m-1).
```

*Conclusion.*  The pair is ordinary-AC trivial, with a deterministic
certificate.

*Proof.*  By Lemma 3.1 the target gap triple `(0, 1, -1)` (resp. `(0, -1, 1)`)
lies in the carry orbit exactly under the stated congruences, so a finite
sequence of unit carries - each one AC move by Lemma 2.1 - turns the companion
into the word `b^(2eps) a b^(-eps) a^(-1)` (resp. `b^(2eps) a^(-1) b^(-eps) a`).
That word is a BS(1,2) relator: `b^2 a b^-1 a^-1` inverted and rotated is
`a b a^-1 b^-2`, i.e. `a b a^-1 = b^2`.  Its companion is now `R`, whose
exponent in the new stable letter `a` is `m - (m+1) = -1`, so the gate fires and
Lemma 4.1 gives acceptance.  `consecutive_bs.collapse` then produces a
substitution-only path to a pair of distinct generators. ∎

*Compiler (deterministic).*
1. `bs_preflight.donor_orientations` on both relators; take the first hit.
   Charge: 1 unit.
2. Build `(signs, gaps)` in `O(|W|)`; run `reduce_plan`, the carry version of
   `bs_preflight`'s greedy scan, emitting one unit carry per relation use.  If
   it terminates at `s = 1` the pair was never stalled (hand to
   `consecutive_bs.collapse`); if at `s != 3`, refuse.
3. Rotate to the `(eps, eps, -eps)` order, read `(u, v, w)`, and solve
   `sum c_i * c_i-vector = target - (u,v,w)` in closed form (`carry_solution`,
   `O(1)` integer arithmetic).  `None` for both targets = refuse.
4. Emit `sum |c_i|` unit carries, ordered greedily by the resulting word length
   (`transport_plan`), each one Definition 2.1 move whose `(target, jsign, k1,
   k2)` is the rotation arithmetic of Lemma 2.1.
5. Hand the resulting pair to `consecutive_bs.collapse`.

*Work charged.*
* Recognition + label: 1 gate unit + `bs_preflight`'s own `scans`, plus `O(|W|)`
  symbol work.  **A failed attempt costs nothing beyond that** - applicability
  is two residue comparisons - which is the property Theorem 2.2 says the
  current policy lacks.
* Pinch phase: one AC move per relation use; at most `sum_i |g_i| / m` for the
  census inputs (measured maximum 5).
* Transport phase: `|c0| + |c1| + |c2|` AC moves.  From the class normal form
  `(0, 1, m-1)` this is exactly `3m + 2`; from raw census companions the
  measured maximum is 40 (at `m = 2`).
* Collapse phase: `consecutive_bs.collapse` on `(V_1, R_m)` costs exactly
  `2^(m+1)` rewrites with peak relator length `2^m + 3` - **exponential in
  `m`**, because reducing `R_m` over `a b a^-1 = b^2` doubles the base exponent
  once per pinch.  For the census (`m <= 7`) that is at most 256 rewrites and
  length 131; note `consecutive_bs.collapse`'s default `intermediate_cap=256`
  must be raised (the certificates below pass `intermediate_cap=None`).

*Measured cost table* (class normal-form input `(0, 1, m-1)`):

| `m` | transport carries | collapse rewrites | collapse peak relator | total moves |
|---|---|---|---|---|
| 2 | 8 | 8 | 7 | 16 |
| 3 | 11 | 16 | 11 | 27 |
| 4 | 14 | 32 | 19 | 46 |
| 5 | 17 | 64 | 35 | 81 |
| 6 | 20 | 128 | 67 | 148 |
| 7 | 23 | 256 | 131 | 279 |
| 8 | 26 | 512 | 259 | 538 |
| 10 | 32 | 2048 | 1027 | 2080 |

### 4.1 Positive examples, all machine-replayed to `(x,y)`

| input | label | carries | collapse | elementary moves | replay |
|---|---|---|---|---|---|
| `('YYXXXXyX','YXXXXXyxxxxxx')` = census **ac19_105, unsolved by the frozen 1k policy** | `(5,1,4)` | 17 | 64 | 1,515 | `['x','y']` |
| `('YYXXyx','YXXXyxx')` = ac19_42 | `(2,1,1)` | 1 | 8 | 133 | `['x','y']` |
| `('YYXXXyxx','YXXXXyxxx')` = ac19_73 | `(3,1,2)` | 1 | 16 | 295 | `['x','y']` |
| planted `m=4`, gaps `(0,1,3)` | `(4,1,3)` | 14 | 32 | 818 | `['x','y']` |
| planted `m=6`, gaps `(0,1,5)` | `(6,1,5)` | 20 | 128 | 3,369 | `['x','y']` |
| planted `m=8`, gaps `(2,1,-1)`, `eps=-1` | `(8,1,7)` | 6 | 512 | 29,068 | `['x','y']` |

**Batch result.**  Of the 602 stalled-BS census roots, **427 satisfy the
hypotheses** (404 at `m=2`, 15 at `m=3`, 4 at `m=4`, 4 at `m=5`), including
**4 of the 18 that the frozen 1,000-unit policy failed** (class `(5,1,4)`:
ac19_105, ac19_14409, ac19_18936, ac19_37966).  All 427 were compiled and
replayed end to end to `['x','y']` (18 s of CPU for the whole batch).

### 4.2 Adversarial negatives, all refused in `O(1)` after recognition

| input | why it must be refused | reported reason |
|---|---|---|
| ac19_102 `('YYXXyx','YXXXXXXyxxxxx')` | label `(5,2,4)`: `(alpha,beta) = (4,1)`, and `(0,±1,∓1) - (0,-2,1) ∉ L` | `class_not_demotable` |
| ac19_99 `('YYXXyxx','YXXXXXXXXyxxxxxxx')` | label `(7,2,5)` | `class_not_demotable` |
| planted `m=5`, gaps `(0,2,3)` | label `(5,2,3)` | `class_not_demotable` |
| planted `m=7`, gaps `(0,3,3)` | label `(7,3,3)` | `class_not_demotable` |
| planted `m=3`, gaps `(0,4,3)` | `v = 4 ≡ 0 (mod 4)`: pinchable, not stalled | `already_pinchable` |
| `('xyxYXY','xxyy')` | no consecutive-BS relator | `not_a_consecutive_bs_pair` |

A subtler adversarial family worth stating: the rule must **not** be relaxed to
"`W` can be carried onto some BS(`m'`,`m'`+1) relator".  For `m' >= 2` and
`m >= 2` the resulting pair `(V_{m'}, R_m)` is again *stalled* - `bs_preflight`
rejects it with `2m+1` stable letters:

| `m \ m'` | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| 2 | accept | reject(5) | reject(7) | reject(9) |
| 3 | accept | reject(7) | reject(7) | reject(9) |
| 5 | accept | reject(11) | reject(11) | reject(11) |
| 7 | accept | reject(15) | reject(15) | reject(15) |

so the "demote to a smaller BS pair" idea is a genuine trap for every `m' >= 2`;
only `m' = 1` closes, and by Theorem 2.3(iv) `m' = 1` forces `s_red = 3`.

## 5. Refuted and bounded-refuted mechanisms

**5.1 The companion-driven rewrite `y^eps = A^-1 B^-1` (refuted as a descent).**
The brief suggests writing `W = A y^eps B` and substituting `y^eps` into `R` to
"kill `R`'s y-exponent".  For this family that cannot help: `R = b^-1 a^m b
a^-(m+1)` already has stable exponent 0, so there is nothing to remove, and
since `s_red = 3 > 1` every occurrence of `b^{±1}` in `W` has stable letters on
both sides, so the substitution replaces each of `R`'s two stable letters by a
word containing at least one stable letter and *increases* the stable-letter
count of `R` from 2 to at least 4.  Concretely with the normal form
`W = b^2 a^v b^-1 a^w` one gets `b = a^-w b a^-v b^-1`, and substituting both of
`R`'s stable letters gives

```text
R  ->  b a^v b^-1 a^m b a^-v b^-1 a^-(m+1)
```

- still stable exponent 0, but 4 stable letters and length `2m + 5 + 2|v|`
instead of `2m + 3` (checked for `m=5, v=2, w=3`: length 19, four stable
letters).  Iterating doubles again.  It is a valid identity, not a descent.

**5.2 "Use the second relator as a BS donor after one multiplication"
(bounded-refuted).**  If `R' = R . g^-1 W^{±1} g`, then `R'` has stable exponent
`±1`, so it is not a BS relator in the letter `b`; as a BS relator in the letter
`a` it needs `2m'+1` `b`-letters, and `R'` has at most `2 + 3 = 5` of them
before reduction, so `m' <= 2`; it also needs exactly two `a`-letters, i.e. the
cancellation of at least `2m - 1` of `R`'s `a`-letters against `W`'s.  An
exhaustive depth-1 enumeration - every W-variant with `u in {-1,0,1}` and each
gap at either of its two shortest residue representatives (12 companions per
class), and every one of the `2 |R| |W|` R-moves - finds **no** BS-shaped and
**no** certified child for any class other than `(m,1,m-1)`:

| class | R-move children enumerated | certified | BS-shaped |
|---|---|---|---|
| `(3,2,1)`, `(4,1,2)`, `(4,2,2)`, `(5,2,3)`, `(5,2,4)`, `(5,3,1)`, `(5,3,2)`, `(6,1,3)`, `(6,2,3)`, `(6,2,4)`, `(7,2,5)`, `(7,4,1)` | 1,548 - 4,556 each | 0 | 0 |
| `(2,1,1)`, `(3,1,2)`, `(4,1,3)`, `(5,1,4)` | 1,036 - 2,860 each | 75 - 141 | 75 - 141 (all through the BS-DEMOTE word) |

This is a bounded refutation, not a theorem: a wider `u` range or two
multiplications are not covered.

**5.3 Stable-letter descent (refuted).**  `s_red` cannot be lowered by W-moves
(Theorem 2.2), and the mined census paths confirm it: every one of the 584
solved stalled paths modifies `R`, and `n_sub_on_R0 in {1, 2}` for all of them.

**5.4 Two-block and one-occurrence terminals before `R` moves (refuted).**
Theorem 2.3(i)-(ii).  This matches the mining: no stalled-root path closes on a
two-block terminal, and the 364 one-occurrence closures all happen after `R`
has changed (`first_certified >= first_R_gone` in 536 / 584 rows; the other 48
are BS-DEMOTE closures).

**5.5 BS-DEMOTE for `s_red = 5` or `7` (refuted by a necklace invariant).**
Theorem 2.3(iv) forces `2m'+1 = s_red`, i.e. `m' = (s_red - 1)/2`, and by the
table in §4.2 such a pair is stalled again for `m' >= 2`.  Independently, the
sign *necklace* of the reduced companion is a W-move invariant (carries change
only gaps; cancellations only delete opposite-sign pairs), and a BS(`m'`,`m'+1`)
relator has necklace `(-^{m'}, +^{m'+1})`.  The 121 solved `s_red = 5` census
rows have necklaces `(+,+,-,+,-)` (113), `(+,-,-,+,-)` (4), `(+,-,+,+,-)` (4) -
none equal to `(-,-,+,+,+)`.  The 7 unsolved `s_red = 7`, `m = 2` rows all have
necklace `(+,+,-,+,-,+,-)`, not `(-,-,-,+,+,+,+)`.  So BS-DEMOTE provably never
applies to any of them; a different mechanism is required.  (Per the brief, no
search was run on those 7 rows.)

## 6. Rule BS-NORMALISE (proved, a preprocessing rule)

*Hypotheses.*  Any stalled consecutive-BS pair with `s_red = 3`.
*Conclusion.*  An explicit bounded AC path to the class normal form
`(R_m, b^eps a^0 b^eps a^alpha b^-eps a^beta)` with `0 < alpha < M_v`,
`0 < beta < M_w`; the companion's length is minimal in its orbit, namely
`3 + min(alpha, M_v - alpha) + min(beta, M_w - beta)`.
*Proof.*  Lemma 3.1 plus the greedy `reduce_plan`/`transport_plan` of §4.
*Work.*  `O(|W|)` recognition, `O(1)` label arithmetic, one AC move per carry.

This is the deduplication rule: it turns "solve 602 census rows" into "solve 18
classes", and it never lengthens the companion.  Verified in section F.

## 7. Status of the four residual classes

| class | census rows | status |
|---|---|---|
| `(5,1,4)` | 4, all unsolved by the 1k policy | **proved and certified** by Rule BS-DEMOTE (§4.1); 17 carries + 64 rewrites, replayed to `['x','y']` |
| `(5,2,4)` | 6, all unsolved | **solved, not yet a rule.**  `root_router(budget=1000, use_high_core_escape=True)` on ac19_102 solves it in 608 units; the decoded 1,582 elementary moves replay to `['x','y']` (verifier section G).  ac19_103 also solves under gated `mid_search` at 1,743 units.  By Theorem 3.2 the other four rows of the class transport onto the same normal form. |
| `(7,2,5)` | 1, unsolved | **solved, not yet a rule.**  `root_router(budget=1000)` on ac19_99 solves it in 896 units; 2,234 elementary moves replay to `['x','y']`. |
| `s_red = 7`, `m = 2`, necklace `(+,+,-,+,-,+,-)` | 7, unsolved | **open.**  BS-DEMOTE provably inapplicable (§5.5).  Not searched, per the brief. |

The frozen policy's failure on the first three is an allowance artefact: all 18
unsolved stalled rows were charged exactly `(prepass 8, plain_s20 872,
incumbent 120)`, so the only stage that consults the stalled-BS feature and the
BS/two-block gates never got more than 120 units, while their 584 solved
siblings needed a median of 58 and a maximum of 541.

## 8. What to implement, in order

1. **BS-DEMOTE + BS-NORMALISE as a pre-search macro.**  `O(|W|)` to decide,
   deterministic to compile, `2^(m+1) + O(m)` moves to certify.  Covers 427 /
   602 stalled census rows with no search, and 4 of the 18 current failures.
   Raise `consecutive_bs.collapse`'s `intermediate_cap` to at least `2^m + 4`
   (or pass `None`) when calling it on the demoted pair.
2. **Suppress provably doomed recognition** (Theorem 2.2).  Cache the root BS
   relator; at any descendant that still contains it as the gate donor, skip
   `bs_preflight` and skip the `4*T` re-evaluation.  Recovers 59,414 scans on
   the solved rows and most of Stage 3's 120 units on the failures.
3. **Class-keyed memoisation.**  Store one certificate per label; replay it
   through the transport of Theorem 3.2 for every other row of the class.
4. **Re-allocate the budget for stalled roots**: `plain_search_fast` has no BS
   or two-block gate, so its 872 units cannot recognise the terminal these rows
   end on.  Routing a stalled-BS root straight to Stage 3 with the full 1,000
   units already solves ac19_99 and ac19_102.
5. **Open problem for a next session**: the `s_red = 7`, `m = 2` necklace
   `(+,+,-,+,-,+,-)` class.  The right generalisation to look for is a
   `s_red -> s_red - 2` descent that *does* change `R`, since Theorem 2.2
   forbids any descent that does not.
