# Family completion rules for the 41 residual AC19 rows

Theory companion to [`FAMILY_DATA.md`](FAMILY_DATA.md).  Code and machine
checks: [`FAMILY_verify.py`](FAMILY_verify.py) (output
[`FAMILY_verify.json`](FAMILY_verify.json)); mining and the Magnus frame:
[`FAMILY_mine.py`](FAMILY_mine.py).

```bash
# the proofs and all 20 W-TRANSPORT certificates; no policy search is run
PYTHONPATH=. python3 research/residual_20260909/theory/FAMILY_verify.py
# adds section E: Rule TRAIL, i.e. the recorded search runs of section 6
PYTHONPATH=. python3 research/residual_20260909/theory/FAMILY_verify.py --all --matrix
```

The first command is the one that has to pass and is what the committed
`FAMILY_verify.json` records; the second re-runs the searches of §6 and §7 and
is not needed to check anything proved here.

Every certificate claimed here is built and checked twice: once by replaying
each stored state with `experiments/equivalence_classes/lib/words`
(`replay_move` for substitutions, `apply_pair` for ambient maps), and once by
decoding the mixed path with
`certificate_decoder_compact_moves.decode_elementary` and replaying the emitted
ordinary invert/swap/conjugate/multiply sequence with
`certificate_decoder.replay_elementary`, requiring the literal terminal
`['x', 'y']` — the census's own contract, the same one
`research/residual_20260909/harness.run_row` applies.

**Status of every claim in this note.**

| claim | status |
|---|---|
| Lemma W1, Theorem W2, Theorem W3, Corollary W4 (§2) | **proved**, with the algebra machine-checked on all 2,346 `R`-preserving children of the 41 roots |
| Rule W-TRANSPORT (§3) | **proved**; 20 of the 41 rows certified, each certificate decoded and independently replayed to `['x', 'y']` |
| Observation W5 (§4) | **bounded refutation** — a statement about one explicit ball (`slack = 4`, `depth = 4`), not about all `R`-preserving macros |
| Observation W6 (§4) | **proved** for the four terminal recognisers the census policy actually uses, given Theorem W2; the gate audit is §G of the verifier |
| Magnus frames, the trefoil base, the `F_5` monodromy (§5) | **proved**, with the rewriting round-trip and the two identities machine-checked |
| decidability of conjugacy in these `G` (§5.1, §5.2) | **cited**, not proved and not implemented here |
| Lemma T1, Lemma T2 (§6) | **proved** |
| every count, unit, table row and solve (§3, §6, §7 and `FAMILY_DATA.md`) | **measured**, every solve decoded and independently replayed |
| "no correlation between Magnus type and difficulty" (§5.4) | **an observation on 19 families**, not a theorem |

Nothing in this note is offered as a conjecture; where an argument stops, it is
labelled *bounded*, *cited* or *measured* rather than extended by guess.

---

## 1. Conventions

Alphabet `xXyY`, uppercase = inverse.  **Ordinary AC moves** are what
`replay_elementary` accepts: `invert(i)`, `swap`, `conjugate(i, letter)`,
`multiply(target, source)`.  The search's **Definition 2.1** packaging is

```text
r_i  <-  rot_{k1}(r_i) . rot_{k2}(r_{3-i}^{jsign})          (target, jsign, k1, k2)
```

freely and cyclically reduced and canonicalised
(`words.replay_move`).  A signed permutation of `{x, y}` and the four Nielsen
maps are **ambient transport**, not AC moves; they are carried by
`primitive_patterns.md` §2 and recorded as `{'kind': 'automorphism'}` steps.

Fix a pair `(R, W)`.  An **`R`-preserving move** (a *W-move*, in the language of
[`STALLED_BS_THEORY.md`](STALLED_BS_THEORY.md) §2) is any move that leaves `R`
unchanged as a cyclic word: inversion or conjugation of `W`, relator swap, and
`W <- g^-1 W g . h^-1 R^{±1} h`.  In the Definition 2.1 packaging these are
exactly the moves whose `target` is the companion's slot.  `G` always denotes
the one-relator group `<x, y | R>`.

---

## 2. The companion class is the exact invariant of `R`-preserving moves

**Lemma W1 (rotation is conjugation).**  For a word `u` and `0 <= k < |u|`,
`rot(u, k) = s u s^-1` where `s` is the length-`k` suffix of `u`.  Hence an
`R`-preserving Definition 2.1 move sends the companion to

```text
W'  =  rot_{k1}(W) . rot_{k2}(R^{jsign})  =  (C W C^-1) . (B R^{jsign} B^-1),
```

`C` the length-`k1` suffix of `W`, `B` the length-`k2` suffix of `R^{jsign}`.

*Proof.*  Write `u = A B` with `|B| = k`; then `rot(u, k) = B A = B (A B) B^-1`.
Apply it to `W` and to `R^{jsign}` and concatenate. ∎

*Checked* (§B of the verifier): the rotation identity on the companion side at
1,832 `(target, jsign, k1)` triples and on the donor side at every `k2` inside
them, and all 2,346 `R`-preserving children of the 41 residual roots (both
targets, both signs, every rotation pair, relator cap `root max + 4`) — the
kernel's own `replay_move` output equals `canon_pair(R, canon_rel(rot(W,k1) .
rot(R^s,k2)))` and the product factors as above, letter for letter after free
reduction.  0 failures.

**Theorem W2 (invariance).**  Let `(R, W) -> ... -> (R, W')` be any sequence of
`R`-preserving moves.  Then the images `[W']` and `[W]` in `G = <x, y | R>` are
conjugate up to inversion.

*Proof.*  By Lemma W1 one move replaces `[W]` by `C [W] C^-1` times the image of
a conjugate of `R^{±1}`, which is trivial in `G`.  Free and cyclic reduction and
`canon_rel` replace a word by a rotation — a conjugate — of it or of its
inverse.  Relator swap and inversion of `W` change the class only by inversion.
∎

**Theorem W3 (completeness, in the elementary model).**  Conversely, if `[W']`
is conjugate in `G` to `[W]^{±1}`, then `(R, W)` and `(R, W')` are joined by
ordinary AC moves none of which changes `R`.

*Proof.*  `[W'] = g^-1 [W]^{eps} g` in `G` means, in the free group,
`W' = (g^-1 W^{eps} g) . N` with `N` in the normal closure `<<R>>`, i.e.
`N = prod_i c_i^-1 R^{e_i} c_i` for finitely many `c_i`.  Realise: `invert` the
companion if `eps = -1`; `conjugate(companion, .)` letter by letter to install
`g`; then, for each `i`, conjugate by `c_i`, `multiply(companion, R-slot)` with
the sign `e_i`, conjugate back.  Each is an ordinary AC move and none touches
`R`. ∎

**Corollary W4 (the transport corollary).**  For a fixed `R`, the conjugacy
class of `[W]^{±1}` in `G` is a complete invariant of the `R`-preserving orbit
of the pair.  Two census rows of the same family whose companions have conjugate
images in `G` are therefore joined by an explicit bounded move sequence, and a
certificate for either one transports to the other.

This is the exact generalisation of `STALLED_BS_THEORY.md` Theorem 2.2 and
Theorem 3.2: there `G = BS(m, m+1)`, the conjugacy class of a cyclically
Britton-reduced companion is captured by the pair (stable length, carry-lattice
label `(m, alpha, beta)`), and Rule BS-NORMALISE is Corollary W4 made explicit
for that `G`.

---

## 3. Rule W-TRANSPORT (**proved**; certifies 20 of the 41)

*Hypotheses.*  A canonical pair `P` and a bound `(slack, depth)`.  Expand
`B_W(P)`, the set of canonical pairs reachable from `P` by at most `depth`
`R`-preserving Definition 2.1 moves keeping every relator at
`max(|r1|,|r2|) + slack` symbols.  Suppose some `Q` in `B_W(P)` is, up to one
of the eight signed permutations, a census row `S` with a stored verified
certificate whose mixed path ends at the trivial pair.

*Conclusion.*  `P` is ordinary-AC trivial, with the explicit certificate

```text
P --(the <= depth R-preserving moves, each a Definition 2.1 move)--> Q
  --(one signed permutation, recorded as an ambient transport step)--> S
  --(S's stored census certificate)--> (x, y).
```

*Proof.*  Each prefix step is a Definition 2.1 move (Lemma W1) and is emitted
with the exact `(target, jsign, k1, k2)` the kernel replays; the permutation is
transport (`primitive_patterns.md` §2, audit T2); the suffix is a verified
census certificate.  Corollary W4 is what makes such a `Q` findable at all: the
search is over one `R`-preserving class, so it never leaves the invariant. ∎

*Chaining.*  If `P`'s ball meets another residual row `P'` whose ball meets a
census row, the two prefixes concatenate (with one permutation step at the
junction).  The residual's `R`-preserving components (§4) are what this
exploits.

*Work charged.*  `depth` substitution units plus one table/relabel lookup per
generated state; the `B_W` balls of the 41 roots have 1 to 4,190 states at
`slack = 4`, `depth = 4` (median 288), each state one `relabel_key` (8 signed
permutations and a Booth least-rotation).

*Result* (`FAMILY_verify` §C, `slack = 4`, `depth = 4`).  **20 of the 41 rows
are certified**, every one decoded and independently replayed to `['x', 'y']`:

| row | `R`-preserving moves | via | source census row (route) | mixed steps | elementary moves |
|---|---:|---|---|---:|---:|
| `ac19_99` | 3 | — | `ac19_64188` (incumbent_restart) | 32 | 1,282 |
| `ac19_2696` | 1 | — | `ac19_25945` (incumbent_restart) | 41 | 2,427 |
| `ac19_6554` | 5 | `ac19_25325` | `ac19_25945` | 46 | 2,552 |
| `ac19_18413` | 5 | `ac19_25325` | `ac19_25945` | 47 | 2,561 |
| `ac19_25325` | 3 | — | `ac19_25945` | 44 | 2,473 |
| `ac19_31624` | 5 | `ac19_51124` | `ac19_36125` (plain_s20) | 25 | 1,037 |
| `ac19_40167` | 4 | — | `ac19_10229` (plain_s20) | 29 | 1,326 |
| `ac19_45056` | 4 | — | `ac19_37598` (incumbent_restart) | 44 | 2,082 |
| `ac19_51124` | 1 | — | `ac19_36125` | 20 | 800 |
| `ac19_54337` | 3 | — | `ac19_10229` | 28 | 1,280 |
| `ac19_54514` | 7 | `ac19_45056` | `ac19_37598` | 47 | 2,245 |
| `ac19_56260` | 5 | `ac19_51124` | `ac19_36125` | 25 | 915 |
| `ac19_62145` | 1 | — | `ac19_10229` | 26 | 1,163 |
| `ac19_62816` | 6 | `ac19_45056` | `ac19_37598` | 46 | 2,191 |
| `ac19_64163` | 1 | — | `ac19_20858` (incumbent_restart) | 30 | 1,910 |
| `ac19_65967` | 5 | `ac19_45056` | `ac19_37598` | 45 | 2,150 |
| `ac19_66385` | 2 | — | `ac19_10229` | 27 | 1,219 |
| `ac19_66543` | 7 | `ac19_45056` | `ac19_37598` | 47 | 2,241 |
| `ac19_69139` | 2 | — | `ac19_20858` | 31 | 1,953 |
| `ac19_70845` | 8 | `ac19_54514`, `ac19_45056` | `ac19_37598` | 49 | 2,275 |

Two remarks.  First, `ac19_99` is the class-`(7,2,5)` stalled-BS row that
`STALLED_BS_THEORY.md` §7 records as "solved, not yet a rule"; Rule W-TRANSPORT
gives it a rule-shaped certificate (3 `R`-preserving moves onto `ac19_64188`,
which by Theorem W2 must lie in the same carry class).  Second, the rule is
*only* as strong as the corpus of stored certificates it can land on: it is a
transport rule, not a completion rule in the BS-DEMOTE sense.

---

## 4. What the invariant refutes

**Observation W5 (bounded refutation).**  For the other 21 residual rows the
ball `B_W` at `slack = 4`, `depth = 4` contains **no solved census row at all**
(`FAMILY_verify` §D prints every ball size and everything each ball meets).
The residual splits into **16 `R`-preserving components** of sizes
6, 5, 4, 4, 3, 3, 3, 2, 2, 2, 2 and five singletons; eleven rows see a solved
census row directly and chaining lifts that to twenty.  `ac19_50262` is extreme:
its ball is `{itself}` — the pair admits no `R`-preserving move at all inside
`root max + 4`.

**Observation W6 (a macro of BS-DEMOTE shape cannot close this residual).**
Rule BS-DEMOTE works because its *target* — a `BS(1,2)` relator as the
companion — lies inside the companion's own `W`-class, so bounded carries
reach it and a proved gate then fires.  For the 41 residual rows:

* none of the 41 passes the two-block or the one-occurrence gate; only two have
  a consecutive-BS donor recognised at all and neither is accepted by the
  Britton preflight; exactly one (`ac19_99`) carries a BS-DEMOTE label, and it
  is class `(7,2,5)`, which `bs_demote_gate.demotable` refuses (only
  `(m, 1, m-1)` is demotable — `STALLED_BS_THEORY.md` §4).  All of this is
  §G of the verifier, run with `DONOR_NORMALIZED_BS.inspect` and
  `bs_demote_gate.recognize` on all 41 roots;
* by Theorem W2 no `R`-preserving move can change that: the class, hence the
  gate verdict, is invariant;
* and the census's own solved certificates in these families leave the class
  almost immediately — the median number of moves before `R` stops being one of
  the two relators is 1 or 2 in 16 of the 19 families
  ([`FAMILY_DATA.md`](FAMILY_DATA.md) §3).

So *within the shape "bounded `R`-preserving macro to a state a proved gate
closes", the residual is refuted*: there is no such gate to reach.  What is left
of the shape is Rule W-TRANSPORT, where the terminal is an already-certified
state rather than a gate — and that is exactly the direction §6 pushes.

---

## 5. Magnus frames of the three named family groups

For `G = <x, y | R>`, the Magnus/HNN decomposition takes as stable letter `t`
the generator whose exponent sum in `R` is **zero** (`G -> Z` kills `R` iff it
kills the other generator), and its base is generated by the conjugates
`b_i = t^i b t^-i` of the other generator `b`; the associated subgroups are
`A = <b_mu, ..., b_{nu-1}>` and `A' = <b_{mu+1}, ..., b_nu>` and `t b_i t^-1 =
b_{i+1}`.  This is the convention `STALLED_BS_THEORY.md` §1 uses for
`BS(m, m+1) = b^-1 a^m b a^-(m+1)`, where `exp_b = 0` and `b` is the stable
letter.

When neither exponent sum is zero, one ambient Nielsen shear puts one of them
at zero exactly when one exponent sum divides the other.  `FAMILY_mine.
magnus_frame` computes the shear, the transported relator `R~`, `mu`, `nu` and
the rewriting `r*`; `FAMILY_mine.magnus_word` re-expands `r*` and checks it
reproduces `R~` (13 of the 19 families admit a single-shear frame; all 13
round-trip — `FAMILY_verify` §F).

Useful reading of `r*`: if the extreme generator `b_nu` occurs exactly once it
can be Tietze-eliminated, so the base is free and `A = B`; if `b_mu` occurs
once, `A' = B`.  Both once means `A = A' = B` and `G` is a **mapping torus**
`F_n ⋊ Z`; exactly one means a **strictly ascending HNN extension** of a free
group; neither means a genuine one-relator base with proper edge groups.

### 5.1 `R = YXyXYXyxx`  (`exp = (-1, 0)`; 5 residual rows, the hardest family)

`exp_y = 0`, so **no shear is needed and `y` is the stable letter**.  Reading
`R` and recording the `x`-letters at their cumulative `y`-level with
`x_i = y^i x y^-i`:

```text
r*  =  x_{-1}^-1 x_0^-1 x_{-1}^-1 x_0^2 ,        mu = -1,  nu = 0.
```

Put `a = x_{-1}`, `b = x_0`.  The base is `B = <a, b | b^2 = a b a>` and the
associated subgroups are the **infinite cyclic** `A = <a>` and `A' = <b>`, with
`y a y^-1 = b`.  The free-basis change `c = a b` (so `a = c b^-1`) carries the
relator to `b^3 c^-2`:

> **`B` is the trefoil group `<b, c | b^3 = c^2>`** — the `(2,3)`-torus knot
> group.  (*Checked*: `canon_rel` of the substituted relator equals
> `canon_rel('yyyXX')`, `FAMILY_verify` §F.)

So `G = <B, y | y (c b^-1) y^-1 = b>`, an HNN extension of the trefoil group
with infinite cyclic edge groups.  Britton's lemma gives the normal form:
a word in `G` is reduced iff no subword `y^-1 u y` with `u in A` and no
`y u y^-1` with `u in A'` occurs, and the companion invariant of Theorem W2 is
the conjugacy class of the cyclically reduced form.  The trefoil group has
centre `<b^3>` with quotient `PSL(2, Z) = Z/2 * Z/3`, which is virtually free,
so membership in `<a>` and `<b>` and conjugacy in `B` are decidable (standard
facts about virtually-free and torus-knot groups, cited, not checked here); the
invariant of Corollary W4 is therefore computable in this family.  We did not
implement it — the bounded `B_W` balls of §3 were enough to separate the rows.

### 5.2 `R = YXYXyXXYXyX`  (`exp = (-6, -1)`; 5 residual rows)

`exp_y = -1` divides `exp_x = -6`, so the shear `y -> y x^-6` (`y -> yXXXXXX`)
puts `exp_x` at zero: `R~ = YxxxxxYXyXXYXyX` (length 15), stable letter `x`,
`y_i = x^i y x^-i`,

```text
r*  =  y_0^-1 y_5^-1 y_4 y_2^-1 y_1 ,        mu = 0,  nu = 5   (y_3 absent).
```

Both extremes occur once, so `B = <y_0..y_5 | r*>` is **free of rank 5** (
eliminate `y_0 = y_5^-1 y_4 y_2^-1 y_1`) and `A = A' = B`, since `A` recovers
`y_5 = y_4 y_2^-1 y_1 y_0^-1` and `A'` recovers `y_0`.  Hence

> **`G` is the mapping torus `F_5 ⋊_phi Z`** of the free-group automorphism
> `phi: y_1 -> y_2, y_2 -> y_3, y_3 -> y_4, y_4 -> y_5,
> y_5 -> y_5 y_3^-1 y_2 y_1^-1`.

(`phi` is an automorphism: its images contain `y_2..y_5` and hence
`y_1 = w^-1 y_5 y_3^-1 y_2` where `w = phi(y_5)`; five generators of `F_5`
generating it is an automorphism by Hopficity.)  Conjugacy in `F_n ⋊ Z` is
decidable (Bogopolski–Martino–Maslakova–Ventura), so again the invariant of
Corollary W4 is computable in principle.  Note also what the frame says about
*cheap* invariants: `G^ab = Z^2 / <(exp_x R, exp_y R)>`, and `(exp_x R, exp_y R)`
is primitive on every AC19 row, so `G^ab = Z`; the linear form killing
`(-6, -1)` is `(a, b) -> -a + 6b`, which sends `[W]` to `-det(R, W) = ±1`.  The
abelianised companion invariant is therefore *constant* on the whole family,
solved and unsolved alike, and cannot separate them.  The same computation goes
through for every family (`|det| = 1` is what forces it), which is why the data
shows exponent sums and lengths separating nothing
([`FAMILY_DATA.md`](FAMILY_DATA.md) §3).

### 5.3 `R = YYXyxYXXyx`  (`exp = (-1, -1)`; 5 residual rows)

The shear `y -> y x^-1` (`y -> yX`) puts `exp_x` at zero:
`R~ = xYxYXyxYXXy` (length 11), stable letter `x`, `y_i = x^i y x^-i`,

```text
r*  =  y_1^-1 y_2^-1 y_1 y_2^-1 y_0 ,        mu = 0,  nu = 2.
```

Only the extreme `y_0` occurs once, so the base is **free of rank 2** on
`y_1, y_2`, with `y_0 = y_2 y_1^-1 y_2 y_1`; `A' = <y_1, y_2> = B` while
`A = <y_0, y_1>` is a rank-2 — hence infinite-index — proper subgroup of `B`
(its abelianised image `<(1,0), (0,2)>` already has index 2).  Hence

> **`G` is a strictly ascending HNN extension of `F_2`**: conjugation by `x^-1`
> embeds `B` properly into itself, `x^-1 B x = A`.

Ascending HNN extensions of free groups are coherent and residually finite
(Borisov–Sapir / Feighn–Handel), and Britton's lemma again gives the normal
form; we do not claim a decision procedure for conjugacy here.

### 5.4 The rest

`FAMILY_DATA.md` §2 gives the frame of every family.  Seven are mapping tori
(`YXYXyXXYXyX`, `YXYxYXXYx`, `YXXYxxyx`, `YYXXYxYxyX`, `YXXYxYxx`,
`YYXXXyXYXyX`, `YYXYXyXXyX`), four are strictly ascending HNN extensions of a
free group (`YYXyxYXXyx`, `YXYxxYXyxYXyx`, `YYXXyxx`, `YXXyXyxx`), two have a
one-relator base with cyclic edge groups (`YXyXYXyxx`, `YXXXyxx`), and six
admit no single-shear frame (`YYXXYXYYXXX`, `YYXXYxYXX`, `YXXYxYxxx`,
`YXYxYXXYXyx`, `YYXXXXYX`, `YYXXYxYXXXYx`).  **There is no correlation between
this classification and difficulty.**  The fifteen rows the shipped cascade
still misses at 5,000 units on the bare ball spread over all four structural
classes: 2 in a no-frame family (`YYXXYxYXX`), 5 in a one-relator-base family
(`YXyXYXyxx`), 2 in strictly ascending HNN families (`YYXyxYXXyx`,
`YXYxxYXyxYXyx`) and 6 in mapping tori (`YXYxYXXYx`, `YXXYxxyx`).  Reported as
a negative result: the Magnus type of the family group predicts nothing about
whether the 1,000-unit or 5,000-unit search closes the row.

---

## 6. Rule TRAIL: the certificate corpus as a terminal (**sound, dominant**)

The backward ball `B(cap)` is exact but *length-capped*: it only contains pairs
that reach `(x, y)` without any relator exceeding `cap`.  The residual rows are
precisely the ones whose routes go uphill first (`FAMILY_DATA.md` §4).  The
published census certificates are a second, uncapped source of certified states.

**Definition.**  For a verified census certificate
`s_0 -> s_1 -> ... -> s_d = (x, y)` (mixed substitution and ambient steps, no
packed elementary tail), enter each `s_i` into a table with depth `d - i`,
successor `s_{i+1}` and the recorded move.  The **corpus** is the union over all
such certificates, minus the states the ball already holds.

**Lemma T1 (soundness).**  Every corpus entry is a state from which the stored
successor chain is a valid engine path to the trivial pair, in exactly the
schema `backward_table.tail` walks; splicing it onto a search path yields a
certificate the compact decoder accepts.

*Proof.*  A suffix of a verified certificate is a certificate: each step is
either a Definition 2.1 move or an ambient transport step, and AC-triviality is
invariant under ambient automorphisms (the decoder Nielsen-reduces the terminal
basis).  The entry format is the ball's own, so the same `tail` walk applies. ∎
*Checked* end to end: every solve reported below was decoded and independently
replayed to `['x', 'y']`.

**Lemma T2 (dominance).**  Replacing the ball `B` by `B ∪ corpus` in
`final_policy_ball` / `mid_search_ball` / `plain_search_ball` cannot lose a row
or raise its charge.  Table lookups are uncharged and never enter the heap
ordering, so the search visits the same states in the same order and can only
stop earlier. ∎

**Size.**  Over the 72,779-row census run: 70,288 certificates are usable
(2,491 are skipped — unsolved rows, or paths carrying a packed `two_block`
elementary tail); they contribute **112,261 states outside the cap-12
automorphism-closed ball**, built in about 6 s.  Their maximum relator lengths
run 9 to 131, median 15 — i.e. the corpus is exactly the uphill region the ball
cannot hold.  None of the 41 residual roots is in it (*checked*), so using it on
them is not circular.

**Honest caveat.**  The corpus contains the *root* of every solved census row,
so re-running the census with it is meaningless (0 units per row).  It is an
endgame table for *new* inputs, and the 41 residual rows are the only fair test
available here.

**Result** (all decoded and independently replayed; these runs are recorded, and
section E of the verifier reproduces them on demand with `--corpus` /
`--all --matrix` — they were not re-run for the final commit):

| configuration | @1,000 | @5,000 |
|---|---:|---:|
| shipped cascade `K3p_c12aut`, ball only | 0 / 41 | 26 / 41 |
| shipped cascade, ball + corpus | **30 / 41** | **39 / 41** |
| `ordinary_T` arm, ball only | 23 / 41 | 30 / 41 |
| `ordinary_T` arm, ball + corpus | 28 / 41 | 35 / 41 |
| `aut_edges` arm, ball + corpus | 28 / 41 | 37 / 41 |

Median charge for the 30 solved at 1,000 units is 309; ten of them cost under
30 units and the most expensive is 410.  Provenance of the hit state: 6 of the
30 land on a certificate of a row in their own family, 24 on a row from
elsewhere in the census — the corpus works as a global endgame table, **not**
because of family structure.

The two rows the corpus cascade misses at 5,000, `ac19_11753` and `ac19_38222`
(family `YYXXYxYXX`), are solved by the `ordinary_T` arm on the **bare ball** at
1,163 and 1,156 units.  Over the eight configurations measured
(`FAMILY_DATA.md` §8) **all 41 residual rows are solved and verified**.

---

## 7. The allocation result (the largest single effect measured)

At 1,000 units the shipped cascade solves 0 of the 41.  The `ordinary_T` arm —
`mid_search_ball.mixed_search(pair, 's20', w_weight=1.5, s_weight=20,
mk_weight=2, use_bs=True, general_bs=True, use_two_block=True,
probe_when='generated', use_bs_preflight=True, bs_escape_weight=4)` — on the
same table and the same 1,000 units solves **23**.  The cascade spends 250 on
the strict-donor prepass and 300 on plain `S20` and hands the routed stage 450.
This is the same failure mode `STALLED_BS_THEORY.md` §7 records for the stalled
rows ("an allowance artefact") and `NOTES.md` §3 records for the dev panel
("the frozen 250+872 prefix starves the incumbent"), now measured on the whole
residual.

---

## 8. Status by family, and what to implement

| family | rows | rule status | certified here |
|---|---|---|---|
| `YXYXyXXYXyX` | 5 | **W-TRANSPORT proved** (all five reach `ac19_37598` in 4-7 `R`-preserving moves, directly or through `ac19_45056`) | 5 |
| `YXyXYXyxx` | 5 | W-TRANSPORT proved for 2 (`51124`, `56260`); the other 3 have no solved row in `B_W` | 2 |
| `YYXyxYXXyx` | 5 | W-TRANSPORT proved for 2 (`6554`, `31624`); `17417`, `57787`, `65876` form a closed `R`-preserving component with no certified member | 2 |
| `YXYxYXXYx` | 4 | **W-TRANSPORT proved** (all four reach `ac19_10229`) | 4 |
| `YXYxxYXyxYXyx` | 3 | W-TRANSPORT proved for `18413`; `33080`, `50610` sit in a 5-row cross-family component with no certified member | 1 |
| `YYXXYxYXX` | 2 | **refuted for W-TRANSPORT** (`B_W` = 36 and 1,184 states, meeting only each other); both closed by `ordinary_T` + ball at ~1,160 units | 0 |
| `YYXXYXYYXXX`, `YYXXYxYxyX`, `YYXXyxx`, `YXXXyxx`, `YXXYxYxx`, `YXXYxYxxx`, `YXXyXyxx`, `YXYxYXXYXyx`, `YYXXXXYX`, `YYXXXyXYXyX`, `YYXXYxYXXXYx`, `YYXYXyXXyX` | 1-2 each | W-TRANSPORT proved for `99`, `2696`, `25325`, `64163`, `69139`, `70845`; refuted (bounded) for the rest | 6 |

**Superseding fact (recorded, not re-run here).**  The residual campaign has
since built the cap-14 automorphism-closed backward ball
(`tables/ball_cap14_aut.npz`, 12,803,449 states) and reports that the cascade
`K3p_c14aut` closes **all 41 rows at 1,000 units, at most 201 charged units
each, verified**.  That is the orchestrator's result, not this note's.  It
confirms the diagnosis of `FAMILY_DATA.md` §4 — the residual is an endgame-table
*reach* problem, and two more symbols of cap are enough — and it demotes items 1
and 2 below from "needed" to "useful for inputs outside whatever ball is
shipped".  Items 3 and 4 are unaffected: Rule W-TRANSPORT is a proved rule with
an invariant behind it, and Observation W6 is a statement about which macros can
ever work here.

**Implement, in order.**

1. **Reallocate for the residual.**  Route a root that survives the donor
   prepass straight to the `ordinary_T` arm with the whole remaining budget, or
   cut the plain-`S20` prefix to zero on roots the ball misses.  Zero new
   machinery, and it is worth 23 of the 41 at 1,000 units on this set.  Check
   the cost on `regression60` and the smoke panel before shipping — the
   plain-`S20` prefix is what closes 23,424 census rows cheaply, so this must be
   a *routed* change, not a global one.
2. **Rule TRAIL, if an uncapped complement is ever wanted** — build the corpus
   once from the published certificate shards (112,261 states, 6 s, a few tens
   of MB) and layer it over whatever ball is shipped, with
   `FAMILY_mine.LayeredTable`.  Lemma T2 makes it zero-loss by construction;
   measured on the cap-12 table: 0 -> 30 of the residual at 1,000 units.  The
   cap-14 ball has since made this unnecessary *for these 41 rows*; its
   remaining argument is that its states are not length-capped at all (median
   max-relator 15, tail to 131), which is where a ball of any fixed cap stops.
   If it is ever shipped, publish it as a table artefact with its own manifest
   and state the census self-reference caveat there.
3. **Ship Rule W-TRANSPORT as a bounded root macro.**  One `R`-preserving BFS
   at `slack = 4`, `depth <= 4`, testing `relabel_key` membership in a table of
   census roots; certifies 20 of the 41 with 1-8 charged moves and a proved
   invariant behind it (Theorem W2 says the search never leaves the class, so
   the ball is small — 288 states at the median).  It subsumes the class-`(7,2,5)`
   stalled-BS row `ac19_99`.
4. **Do not** widen BS-DEMOTE or any other `R`-preserving gate macro for this
   residual: Observation W6 shows there is no gate inside the class to reach.

**Open (theory, not practice).**  The `YYXXYxYXX` family (`ac19_11753`,
`ac19_38222`) is the only one with a *closed* `R`-preserving component, no census
neighbour, no single-shear Magnus frame, and no corpus contribution (all 40
solved members are ball roots, so their certificates lie entirely inside the
cap-12 ball).  Both rows are AC-trivial and are now closed cheaply by the cap-14
ball, and the `ordinary_T` arm certifies them on the cap-12 ball at ~1,160 units
— but nothing proved in this note explains them.  The right next object is their
`W`-class invariant in `G = <x, y | YYXXYxYXX>`, which needs the two-step change
of basis `sigma(R) = (-3, -4) -> (0, ±1)` — realisable as a `GL_2(Z)` matrix such
as `[[4, -3], [1, -1]]` — and therefore a much longer transported relator.  We
did not compute it; that is a conjecture-free statement of what is missing, not
a conjecture.
