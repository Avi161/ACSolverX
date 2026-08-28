# W2d (DRAFT): uniform structure of the period-two baseline family

**STATUS — DRAFT (checker-backed on its central claim).**

- **Checker-verified.** The six-parameter normal form of §(c.2) — the
  central claim — is verified by the committed checker
  `checkers/period_two_normal_form.py` at **caps 12, 13, 14, 15, 16, 17**,
  each a separate guarded run: exact set-agreement with the census
  enumeration, 0 missed and 0 spurious at every cap, with two falsifiable
  controls passing (C1 witness parametrization, C2 cap-19 non-vacuity).
- **Throwaway-script only.** Everything else — the level-by-level pinning
  tables of §(c.1), the fiber/collapse counts of §(b), the `R`-growth curve
  of §(a.3) at caps 18–21, the `U`-fiber pairwise relations of §(b.3), and
  the `R = Y·W·X` check of §(c.4) — was computed by scripts that were not
  retained. Those numbers are reproducible in principle but are **not**
  machine-verified by anything in the repo.
- **Not a proof.** The pinning lemma is an elementary consequence of the
  length identity, verified on enumerations; it has not been written out as
  a formal proof. Read it as a well-supported structural lemma.

Every claim below is about the period-two quotient `Q = <c,t | c^2> = C2 * Z`
and about the census enumeration only. **No claim** is made about the
free-group depth-four class, the bridge, AK(3), stable AC, or AC. Nothing
here proves or disproves any lifting statement; it only describes the shape
of the quotient-level solution set that a uniform argument would have to
quantify over.

## Replay

```bash
python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- \
  python3 fable/proofs/checkers/period_two_normal_form.py 12   # and 13..17
```

The checker runs the normal form as a **generator** (its own prefix/rotation
enumeration) and set-compares against the **census** side (the census
generator's own `conjugates()` enumeration). The two sides share only
primitive word arithmetic, so agreement is a cross-check rather than a
tautology. Exit is nonzero on any missed/spurious chain or control failure.

Sources read: `W2_PERIOD_TWO_BASELINE_CENSUS.md`,
`W2B_BASELINE_LIVENESS.md`, `checkers/period_two_solution_census.py`,
`checkers/period_two_census_chains.json`,
`literature/proofs/AK3_DEPTH4_PERIOD_TWO_WITNESS.md`,
`literature/proofs/AK3_DEPTH4_PERIOD_TWO_ELLIPTIC_OBSTRUCTION.md`.

Notation throughout: words over `{c, t, T}` with `c^2 = 1`, `T = t^-1`;
`|w|` is letter length; `A = TTcTTcttc` (|A| = 9), `B = TTTctctc` (|B| = 8);
`Cl(w)` is the `Q`-conjugacy class. The system is

```text
R in A·Cl(B^-1),   S in B·Cl(R^-1),   U in R·Cl(S^-1),
terminal:  exists g with  U·g t g^-1  in Cl(S).
```

---

## (a) Why `R` is rigid: a prefix-pinning theorem

### a.1 The mechanism

`R = A·X` with `X in Cl(B^-1)`. Write the conjugate in its **canonical
normal form**

```text
X = u · rho · u^-1        (reduced as written, so |X| = 8 + 2k, k = |u|),
```

where `rho` runs over the 8 letter-rotations of the cyclically reduced core
`cyc(B^-1) = cTcTcttt` (all 8 rotations have length 8; `B^-1` is already
cyclically reduced), and `u` is the unique conjugator prefix that does not
cancel into `rho`. Every conjugate of `B^-1` has exactly one such form.

Free reduction of the product `A·X` cancels the maximal common overlap
between the suffix of `A` and the prefix of `X`. That overlap length is
exactly

```text
d = |lcp(X, A^-1)|,     A^-1 = cTTcttctt   (|A^-1| = 9, so d <= 9).
```

Hence the **length identity**

```text
|R| = |A| + |X| - 2d = 9 + (8 + 2k) - 2d = 17 + 2k - 2d.        (a.1)
```

Two immediate consequences, both confirmed on the enumerations:

- **Parity.** `|R|` is always odd. Observed `R`-lengths at every cap are
  `9, 11, 13, 15, 17, 19, 21` — no even length ever occurs.
- **Minimum.** `d <= 9` forces `|R| >= 17 + 2k - 18 = 2k - 1`, and with
  `k <= 9` (since `d <= 9` and `d >= k` is needed below) the floor is
  `|R| = 9`, attained by exactly one word — the witness's
  `R_w = TTctcTctc`.

### a.2 The pinning statement

Because `X` **begins with `u`**, the requirement that `d` be large forces
`u` itself to be an initial segment of `A^-1`. Precisely, from (a.1), a cap
`|R| <= L` is the condition `d >= k - m` with

```text
m := max(0, floor((L - 17)/2)).
```

and `d >= k - m` says exactly: **`u` agrees with `A^-1` on its first `k - m`
letters**; only the last `m` letters of `u` are free.

> **Prefix-pinning (verified, not proved-by-hand here).** For every cap
> `L <= 21`, the admissible `R`-set is exactly
> ```text
> { A · u·rho·u^-1  :  rho a rotation of cTcTcttt,
>                      u[0 : k-m] = A^-1[0 : k-m],
>                      17 + 2k - 2d <= L }.
> ```

**Check.** A script enumerated the census's own `R`-set (via
`conjugates(inv(B), ...)`, the generator's routine) and the model set above,
at every cap from 11 to 21, and compared them as sets:

| cap `L` | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| census `#R` | 3 | 3 | 7 | 7 | 14 | 14 | 32 | 32 | 64 | 64 | 128 |
| model `#R` | 3 | 3 | 7 | 7 | 14 | 14 | 32 | 32 | 64 | 64 | 128 |
| sets equal | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

The `m = 0` regime (`L <= 18`) is the strong form: **`u` must be a literal
prefix of `A^-1`**, of which there are only 10. That is the whole of the
rigidity — the conjugator is confined to a 10-element set, not a ball.
Dropping the pinning hypothesis at `L = 19` (where `m = 1`) makes the model
miss 32 of the 64 true `R` values, i.e. the hypothesis is sharp and is doing
real work, not vacuously true.

### a.3 Growth: **not** linear

The number of admissible `R` by length is

| `|R|` | 9 | 11 | 13 | 15 | 17 | 19 | 21 | 23 | 25 | 27 |
|---|---|---|---|---|---|---|---|---|---|---|
| count | 1 | 2 | 4 | 7 | 18 | 32 | 64 | 128 | 213 | 385 |

so the cumulative `#R(L)` is `3, 7, 14, 32, 64, 128, …` at
`L = 11, 13, 15, 17, 19, 21`. This answers the question posed in the task:
**the `R`-count is exponential, not linear** — asymptotically it roughly
doubles per `+2` of cap, i.e. `#R(L) ~ C · 2^{L/2}`, which is the free
growth of the `m` unpinned tail letters of `u` (`|ball(m)| ~ 2^m`,
`m ~ L/2`) times the 8 rotations and the ≤10 pinned prefixes.

The three-value rigidity at cap 12 is therefore a **small-`m` phenomenon**,
not a structural finiteness: at `L <= 18` the pinning is total (`m = 0`) and
the whole `R`-family is a ≤ `10 x 8 = 80`-element table indexed by
`(prefix of A^-1, rotation of cyc(B^-1))`; past `L = 18` the tail unpins and
the family grows freely.

### a.4 The three cap-12 `R` values, in parameters

| `R` | `|R|` | `k` | `u` | `rho` | `d` |
|---|---|---|---|---|---|
| `TTctcTctc` (witness `R_w`) | 9 | 2 | `cT` | `TctttcTc` | 6 |
| `TTTcTctcttc` | 11 | 4 | `cTTc` | `ttcTcTct` | 7 |
| `tcTcTTTcttc` | 11 | 6 | `cTTctt` | `ctttcTcT` | 9 |

All three have `u = A^-1[0:k]`, as the theorem requires.

### a.5 Honest limits of (a)

- The pinning statement is **verified on enumerations at caps 11–21**, and
  its derivation from (a.1) is elementary, but it has not been written out
  as a formal proof or wired into a checker. Treat it as a
  well-supported structural lemma, not a certified theorem.
- (a) constrains `R` only. It says nothing about which `R` survive the
  later equations; the census's own numbers show `S` and `U` do the real
  filtering.

---

## (b) Fiber structure: the chain count is mostly gauge

### b.1 A conjugacy-collapse lemma (exact, from the verifier's own conditions)

The verifier `period_two_census_verify.py` states the system as

```text
(1)  cyc(R^-1 A) = cyc(B)
(2)  cyc(S^-1 B) = cyc(R)
(3)  cyc(U^-1 R) = cyc(S)
(4)  exists g:  cyc(U g t g^-1) = cyc(S)
```

Conditions **(3) and (4) mention `S` only through `cyc(S)`.** Condition (2)
does **not**: replacing `S` by `hSh^{-1}` turns `S^-1 B` into
`h S^-1 h^-1 B`, whose class generally changes. Hence:

> **Lemma (collapse).** For fixed `R`, the set of admissible `U` depends on
> `S` only through the conjugacy class `cyc(S)`. The multiplicity of `S`
> *within* one class is created entirely by equation (2) plus the length
> cap, and is invisible to everything downstream.

**Check.** Verified on the full chain populations at caps 12, 13, 14, 15:
in every case the `U`-set of each `(R,S)` pair equals the `U`-set of its
`(R, cyc S)` class — `True` at all four caps.

### b.2 Level counts

All counts below are taken over the **surviving** chains, i.e. after the
terminal filter. (`W2_PERIOD_TWO_BASELINE_CENSUS.md`'s "3 admissible `R`,
8 `(R,S)` pairs, 24 chains" are the *pre*-terminal dynamic-range numbers;
the post-terminal `(R,S)` count at cap 12 is 6.)

| cap | chains `(R,S,U)` | distinct `R` | `(R,S)` | `(R, cyc S)` | `(R, cyc S, U)` | `(cyc R, cyc S, cyc U)` |
|---:|---:|---:|---:|---:|---:|---:|
| 12 | 17 | 3 | 6 | 5 | 12 | **9** |
| 13 | 36 | 5 | 15 | 9 | 18 | **9** |
| 14 | 55 | 5 | 16 | 10 | 27 | **13** |
| 15 | 67 | 6 | 24 | 15 | 33 | **18** |

The distinct conjugacy classes appearing are remarkably few:

| cap | `#cyc(R)` | `#cyc(S)` | `#cyc(U)` |
|---:|---:|---:|---:|
| 12 | 3 | 3 | 6 |
| 13 | 3 | 3 | 6 |
| 14 | 3 | 3 | 8 |
| 15 | 4 | 5 | 9 |

`cyc(S)` takes the **same three values** `{TcTcttc, TTcTctttc, TTctttcTc}`
at caps 12, 13 **and** 14 while the raw chain count triples from 17 to 55;
and `cyc(R)` is constant at `{TTctcTctc, TTTcTctcttc, TTTcttctcTc}` over the
same range. **Most of the census's growth is conjugator/length-cap gauge,
not new invariant content.**

### b.3 The `U`-multiplicity, resolved (task item 2)

Take the witness's `R_w = TTctcTctc` and `cyc(S_w) = TcTcttc`. The
`U`-fiber has five members:

```text
TTcTcttc, TTctcTcTctct, TTcttcTc, TcTTcttcTctc, TctcTcTctc
```

Every `U` in a fiber is `U = R·v S^{-1} v^{-1}` for a conjugator `v` (this
is the `h2` freedom), and `v` matters only modulo the centralizer
`C_Q(S)` — which, `S` being hyperbolic with primitive cyclic core
`TcTcttc` (length 7, verified not a proper power), is the maximal cyclic
subgroup `v_0 <rho_0> v_0^{-1}`. So the fiber is in bijection with a set of
cosets `v·C_Q(S)`. Concretely, distinct `U` were confirmed to arise from
distinct conjugators `v` (e.g. for `S = TcTcttc`: `v = cTct, "", ctc, …`).

The three candidate explanations offered in the task were tested pairwise
on all `10` pairs from the fiber:

| relation tested | result |
|---|---|
| `U_j = U_i · z` with `z` in the centralizer of `S` (`zS = Sz`) | **false for all 10 pairs** |
| `U_i^{-1}U_j` conjugate to `S^k` for `k = ±1, ±2, ±3` | **false for all 10 pairs** |
| `U_i = R · v_i S^{-1} v_i^{-1}` for some conjugator `v_i` | **true for all 5** (by construction of the fiber) |

**Answer.** The `U`'s are *not* a centralizer orbit and *not* translates by
conjugates of `S`. They are distinct cosets of the `h2`-conjugator modulo
`C_Q(S)` — i.e. **one twisted family in the parametrization** (a single
`h2`-gauge orbit of conjugators acting on one seed `(R, cyc S)`), while
being **genuinely distinct group elements** with no pairwise translation
relation. "Scattered as elements, uniform as parameters."

### b.4 A consequence for W2b's live set — flagged, not concluded

`W2B_BASELINE_LIVENESS.md` reports six live chains, five of which are not
the witness. One of those five is

```text
(TTctcTctc, TcTcttc, TTcttcTc)
```

and `cyc(TcTcttc) = cyc(TTTcttcTctt) = TcTcttc`, so it is the **witness's
own `(R, cyc S, U)` invariant class with a different `S` representative**.
At the census's `(R,S,U)` granularity it is a distinct chain; at the
conjugacy-invariant granularity of the Lemma it is not.

**Honest caveat.** This does *not* by itself say the two are the same
layer-1 problem: the liveness checker builds its lift from the literal
words `(R,S,U)` and `W2B` explicitly documents that one-hop liveness is
gauge-representative dependent. What it does say is that the census's
essentiality criterion is **not conjugation-invariant in `S`**, so the
"six live baselines" figure counts at most **five** distinct
`(R, cyc S, U)` classes.

---

## (c) A closed-form normal form for the whole family

### c.1 The uniform pinning lemma

Every step of the recurrence has the **same shape**

```text
NEW  =  P · (a conjugate of Q^-1),
```

with `(P, Q) = (A, B)`, then `(B, R)`, then `(R, S)`. The cancellation
analysis of (a) used nothing about `A` and `B` beyond this shape. So it
applies verbatim at every level:

> **Uniform pinning (verified at caps 12–17; derivation elementary, no
> formal proof written).** Write the conjugate in canonical form
> `u·rho·u^-1` (reduced as written, `rho` a letter-rotation of
> `cyc(Q^-1)`, `k = |u|`). Then
> ```text
> |NEW| = |P| + |cyc(Q^-1)| + 2k - 2d,       d = |lcp(u rho u^-1, P^-1)|,
> ```
> and a cap `|NEW| <= L` forces `d >= k - m` with
> `m = max(0, floor((L - |P| - |cyc Q^-1|)/2))`. For `m = 0` this says
> **`u` is a literal prefix of `P^-1`**.

**Check.** For every chain in the census populations at caps 12, 13, 14,
15 (and re-derived at 16, 17), the canonical conjugator at each of the
three levels was computed and tested against the prefix condition:

| level | conjugator pinned to | cap 12 | cap 13 | cap 14 | cap 15 |
|---|---|---|---|---|---|
| 1 (`R = A·…`) | prefix of `A^-1` | 3/3 | 5/5 | 5/5 | 6/6 |
| 2 (`S = B·…`) | prefix of `B^-1` | 6/6 | 15/15 | 16/16 | 24/24 |
| 3 (`U = R·…`) | prefix of `R^-1` | 17/17 | 36/36 | 51/51 | 63/63 |

(The level-3 denominators at caps 14–15 are the instances whose canonical
form was found inside the script's `k <= 8` search window; the widened run
below parametrizes **all** of them, `unparam = 0` at every cap.)

### c.2 The normal form

> **Candidate normal form (DRAFT).** `(R, S, U)` is a census chain at cap
> `L` **iff** there are integers
> ```text
> k1 in [0, |A|],  p1 in [0, |cyc B^-1|)      (8 rotations)
> k2 in [0, |B|],  p2 in [0, |cyc R^-1|)
> k3 in [0, |R|],  p3 in [0, |cyc S^-1|)
> ```
> and a terminal conjugator `g`, such that with the **pinned** prefixes
> `u1 = A^-1[0:k1]`, `u2 = B^-1[0:k2]`, `u3 = R^-1[0:k3]` and the
> rotations `rho_i` indexed by `p_i`:
> ```text
> R = A · u1 rho1 u1^-1      (canonical: |u1 rho1 u1^-1| = |cyc B^-1| + 2k1)
> S = B · u2 rho2 u2^-1      (canonical: |·| = |cyc R^-1| + 2k2)
> U = R · u3 rho3 u3^-1      (canonical: |·| = |cyc S^-1| + 2k3)
> 0 < |R|, |S|, |U| <= L,    cyc(U g t g^-1) = cyc(S).
> ```

So the family is **six integer parameters plus one terminal conjugator** —
three prefix lengths and three rotation indices, each drawn from a range
bounded by the *lengths of the words already built*, with **no free ball
search anywhere**. That is the closed form the task asked for; it is six
parameters, not one or two.

### c.3 Hit / miss against the enumerated chains

The normal form is run as a **generator** (not a predicate) by the
committed checker `checkers/period_two_normal_form.py`: enumerate all
parameter tuples, emit the chains, compare as a set against the census
enumeration at each cap. **Every row below is a checker run**, one guarded
run per cap.

| cap | census chains | generated | hits | **missed** | **spurious** | exact? |
|---:|---:|---:|---:|---:|---:|:--:|
| 12 | 17 | 17 | 17 | **0** | **0** | ✓ |
| 13 | 36 | 36 | 36 | **0** | **0** | ✓ |
| 14 | 55 | 55 | 55 | **0** | **0** | ✓ |
| 15 | 67 | 67 | 67 | **0** | **0** | ✓ |
| 16 | 91 | 91 | 91 | **0** | **0** | ✓ |
| 17 | 106 | 106 | 106 | **0** | **0** | ✓ |

**The normal form captures every enumerated chain at every cap tested, and
produces nothing else.** Caps 16 and 17 were regenerated for this check
(`essential_chains` 91 and 106, witness re-found, elliptic-`S` hits 0 at
both — the census's own controls still pass).

**Controls (both falsifiable, both passing).**

- **C1 — witness parametrization.** The recorded tuple
  `(k1,p1,k2,p2,k3,p3,g) = (2,1,0,2,1,1,"")` must emit exactly the codex
  witness chain and satisfy the terminal condition. This pins the
  rotation-index and prefix-length conventions; it fails on a perturbed
  tuple.
- **C2 — non-vacuity at cap 19.** The checker *asserts strict pinning where
  it must fail*: at cap 19 the length identity gives `m = 1`, so the strict
  (`m = 0`) level-1 model cannot be complete. The control passes only if
  the strict model genuinely under-covers. It reports **census `R` = 64,
  strict pinning `R` = 32, missed 32**, with the strict set a proper subset
  of the census set. Without C2, "the model agrees" could merely mean the
  predicate enumerates everything.

Observed parameter ranges are small and nearly static across caps:
`k1 in 0..7`, `k2 in 0..8`, `k3 in 0..9`; and every chain is parametrized
(`unparam = 0`) at all six caps.

The cap-12 parameter table (`k1, p1, k2, p2, k3, p3, g`) — the witness is
`(2, 1, 0, 2, 1, 1, "")`:

```text
(TTctcTctc, TTTcttcTctt, TTcttcTc)      -> (2,1, 0,2, 1,1, "")   <- witness
(TTctcTctc, TTTcttcTctt, TTcTcttc)      -> (2,1, 0,2, 2,3, "")
(TTctcTctc, TTTcttcTctt, TTctcTcTctct)  -> (2,1, 0,2, 0,2, "")
(TTctcTctc, TTTcttcTctt, TcTTcttcTctc)  -> (2,1, 0,2, 6,3, "")
(TTctcTctc, TTTcttcTctt, TctcTcTctc)    -> (2,1, 0,2, 5,1, "")
(TTctcTctc, TcTcttc,     ...)           -> (2,1, 2,3, *,*, "")   [same U-fiber]
(TTctcTctc, TTcTctttc,   ...)           -> (2,1, 2,2, *,*, "")
(TTctcTctc, TTTctttcTct, TTcTTctttc)    -> (2,1, 0,3, 2,4, "")
(TTTcTctcttc, cTTcTcttctc, ...)         -> (4,6, 4,6, *,*, "")
(tcTcTTTcttc, ctcTcTctc,  ...)          -> (6,4, 3,2, *,*, "Tc")
```

Read off the structure directly: the whole witness branch is
`k1 = 2, p1 = 1` — **one** value of the level-1 parameter — and the five
"different baselines" that share `(R_w, S_w)` are simply
`k3 in {0,1,2,5,6}` at three rotation values. They are one twisted family
in the parameters, exactly as (b.3) concluded from the group theory.

### c.4 The `U`-eliminated form (task item 3)

Eliminating `U` from equations (3) and (4) gives a two-row system. From
`U = R·X^{-1}` with `X in Cl(S)` and `U = Y·W` with `Y in Cl(S)`,
`W in Cl(t^-1)`:

```text
R  in  Cl(S) · Cl(t^-1) · Cl(S).
```

This is exactly the witness document's backward form `R = Y e^{-1} X`
(eq. 1.12, `e = t`), and it is the structural sibling of the elliptic
obstruction's `A in Cl(c)Cl(B)Cl(B)` — the shape a `PSU(2)`-style
representation argument can attack.

**Check.** For all 17 cap-12 chains, explicit `Y, W, X` were extracted
(`W` from the census's own terminal `g`) and verified to satisfy
`cyc(Y) = cyc(X) = cyc(S)`, `cyc(W) = cyc(t^-1)`, and the literal word
equation `R = Y·W·X`: **17/17**.

So the system, `U` eliminated, is

```text
(i)   R in A·Cl(B^-1)                        [pinned: (a)]
(ii)  S in B·Cl(R^-1)                        [pinned: (c.1)]
(iii) R in Cl(S)·Cl(t^-1)·Cl(S)              [terminal]
```

and `U` is recovered as the product of the first two factors of (iii);
the `U`-multiplicity of a pair `(R, cyc S)` is exactly the number of
factorizations in (iii) modulo `C_Q(S)`.

### c.5 Honest limits of (c)

- **Validity range.** Exactness is checked at caps 12–17 only. The
  pinning lemma itself predicts the strict (`m = 0`) form must be relaxed
  once a cap exceeds `|P| + |cyc Q^-1|`; at level 1 that threshold is
  `9 + 8 = 17`, and section (a) confirms the strict `R`-model is exact
  through cap 18 and **misses 32 of 64** `R` values at cap 19. So the
  normal form as stated is **not claimed beyond cap 18**; the general form
  (pin all but the last `m` letters) is the extension, verified for `R`
  through cap 21 but not yet run on full chains.
- **The terminal conjugator is capped.** Observed `|g|` reaches 5, which
  is exactly the census's `GPAD` ceiling — the `g`-search is **saturated at
  its ceiling**, so chains requiring `|g| >= 6` are invisible to every
  number in this document. This is a ceiling, not a budget: it can only
  under-count.
- The pinning lemma is **verified, not proved** — no formal write-up
  exists. The committed checker verifies the *normal form it implies*
  (c.2/c.3) but does not prove the lemma; the level-by-level tables of
  (c.1) came from throwaway scripts.
- Nothing here is a statement about lifting, liveness, or AC.

---

## (d) What a uniform layer-1 argument would have to quantify over

Given (a)–(c), the shape of the required theorem is now concrete. This
section is **specification, not result** — it states the obligations, and
claims none of them are discharged.

### d.1 The index set is the parameter family, not a chain list

A uniform argument cannot be an enumeration. The raw populations grow

| cap | 12 | 13 | 14 | 15 | 16 | 17 |
|---|---|---|---|---|---|---|
| chains | 17 | 36 | 55 | 67 | 91 | 106 |
| `(cyc R, cyc S, cyc U)` triples | 9 | 9 | 13 | 18 | 28 | 31 |
| `#cyc(S)` | 3 | 3 | 3 | 5 | 8 | 11 |

with `#R` alone growing like `2^{L/2}` (a.3). Both columns are strictly
increasing with no plateau. So the argument must be quantified over the
**six integers** `(k1, p1, k2, p2, k3, p3)` of (c.2) plus `g`, with `k_i`
ranging over prefix lengths of `A^-1`, `B^-1`, `R^-1` and `p_i` over
rotation indices of the respective cores.

**What pinning buys.** This is the payoff of (c.1): the conjugators are not
free group elements ranging over a ball, they are **prefixes of words
already in the problem**. So the parameter space is a product of three
*intervals* and three *cyclic groups* — a lattice, not a tree. A uniform
argument only has to be uniform in six integers.

### d.2 The defect as a function of the parameters (qualitative only)

In the relation module `M = Z[Q/<c>]`, conjugating a row by `u` acts by
translation by the coset of `u`. Since each row is literally
`P · u rho u^-1` with `u` a prefix of `P^-1`:

- moving `k_i` translates part of the defect's support **along a fixed
  finite chain of cosets** — the prefixes of `A^-1`, `B^-1`, `R^-1` — not
  along an arbitrary walk;
- moving `p_i` cyclically permutes the core contribution;
- the number of terms grows with `|R| + |S| + |U|`, i.e. linearly in the
  `k_i`, while the five lifting operators stay 2-term differences.

So the defect is a **bounded-complexity function of the parameters**: a
fixed pattern, translated and rotated. A uniform obstruction should be an
invariant of the defect that is stable under exactly those two moves
(prefix-translation and core-rotation) and nonvanishing for all parameter
values. Stated qualitatively as requested; no defect was computed here.

### d.3 One invariant is already ruled out

`W2B_BASELINE_LIVENESS.md` reports that **all five lifting operators have
augmentation 0 by construction**, and that **0 of 17** chains died by
augmentation — every defect has coefficient sum zero. Therefore
augmentation separates no member of this family, at any parameter value.
**A uniform argument must use a strictly finer invariant** (a weighted or
valuation-type count, a mod-`p` Fox-derivative statistic, or a
representation as in the elliptic obstruction). This is a constraint read
off the existing run data, not a conjecture.

### d.4 The highest-leverage reduction, and why it is not free

By the collapse lemma (b.1), the census system sees `S` only through
`cyc(S)` from equation (3) onward. **If** layer-1 one-hop liveness were
likewise a function of `cyc(S)` only, the quantification would drop from
106 chains to 31 invariant triples at cap 17, and `#cyc(S)` (3,3,3,5,8,11)
grows far more slowly than the chain count.

But `W2B` explicitly documents that one-hop liveness **is** gauge-
representative dependent — the witness itself tests NOT-live at one
arbitrary representative — which is evidence *against* the reduction being
free. And the `S`-representative multiplicity within one class is itself
unbounded: the class `cyc(S) = TcTcttc` already contains the census words

```text
TcTcttc(7), ctcTcTctc(9), TTTcttcTctt(11), cTTcTcttctc(11),
cTctcTcTctctc(13), TTTctcTcTctcttt(15), …
```

So: **proving or refuting "layer-1 liveness depends on `S` only through
`cyc(S)`" is the single most load-bearing open question** for a uniform
argument. If true, the burden becomes the slowly-growing invariant family.
If false, the argument must additionally be uniform in the representative,
and the representative count is unbounded.

### d.5 The terminal conjugator cannot be fixed

`g` enters the lifting operators directly (`L3 = U^-1 - w`, `L4 = w - 1`
with `w` the image of `g t g^-1`). So the **operator set is itself
parameter-dependent**: a uniform argument cannot fix the operators and vary
only the defect. All present data has `|g| <= 5` purely because that is the
census's `GPAD` ceiling, and observed `|g|` *reaches* 5 — the search is
saturated at its ceiling, so the true `g`-range is unknown and a uniform
argument must quantify over all of it.

### d.6 The target theorem, and the difficulty relative to the elliptic case

The `U`-eliminated system (c.4) reduces everything to

```text
R in Cl(S) · Cl(t^-1) · Cl(S),
```

structurally identical to the elliptic obstruction's
`A in Cl(c)·Cl(B)·Cl(B)`, which was killed by a `PSU(2)` representation.
That argument worked because `rho(B) = 1` **collapsed two of the three
factors**, leaving a single conjugacy-class membership to contradict.

Here the two outer factors are `Cl(S)` with `S` *varying*. The same
technique would need a representation in which `rho(S)` is central for
**every** admissible `S` — and `#cyc(S)` is 11 by cap 17 and still growing.
That is a materially stronger demand than the elliptic case, and it is the
concrete obstacle a uniform noncancellation argument inherits from this
structure.

---

## Summary of status

| claim | status |
|---|---|
| `|R| = 17 + 2k - 2d`, `R`-lengths odd | derived, matches all enumerations |
| conjugator pinned to a prefix of `P^-1` at all 3 levels | throwaway-script verified caps 12–17; elementary derivation; **not** formally proved |
| strict pinning exact for `R` through cap 18, fails at 19 | **checker-verified** (control C2: 32 of 64 missed at cap 19) |
| `R`-count exponential (`~2^{L/2}`), not linear | throwaway-script verified caps 11–21 (3,7,14,32,64,128) |
| `U`-fiber depends on `S` only through `cyc(S)` | **proved** from the verifier's conditions; script-verified caps 12–15 |
| `U`-fiber is not a centralizer orbit, not `S`-translates | throwaway-script verified (all 10 pairs, witness fiber) |
| six-integer normal form generates the census exactly | **checker-verified**, caps 12–17: 17/36/55/67/91/106, 0 missed, 0 spurious |
| `R in Cl(S)Cl(t^-1)Cl(S)` | derived; throwaway-script verified 17/17 at cap 12 |
| one of W2b's 6 live chains is the witness's invariant class | verified; **consequence for liveness not established** |
| anything about lifting, liveness, AK(3), stable AC, or AC | **no claim** |

