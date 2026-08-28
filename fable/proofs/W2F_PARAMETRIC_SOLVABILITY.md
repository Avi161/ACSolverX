# W2f: layer-1 one-hop solvability as a function of the six-parameter normal form

Date: 2026-08-28 · Checker: `checkers/period_two_parametric_solvability.py`
(imports `period_two_normal_form.py`, `period_two_liveness_invariance.py` and
`period_two_baseline_liveness.py` unmodified; guarded foreground runs, resumable
state file).
Run records: `checkers/out/w2f_chains.json`, `w2f_sweep_k1.json`,
`w2f_report_k1.json`, `w2f_deep_k2.json`, `w2f_galts_k1.json`,
`w2f_abelian_k1.json`.

Answers the question W2e (§6) leaves open: W2d (d.1) says a uniform layer-1
argument must be quantified over the six-integer parameter family, W2e kills
the reduction to `cyc(S)`, so the map to study is

```text
(t, w)  ->  one-hop solvable mod p ?      t = (k1,p1,k2,p2,k3,p3,g),  p in {2,3,5}
```

for `w` running over the centralizer-indexed gauge windows.

---

## 0. Verdict

| question | answer |
|---|---|
| **(i)** Is layer-1 liveness generic — does every parameter tuple have a solvable window at bounded `\|k\|`? | **No.** 46 of the 67 chains at cap 15 have **zero** solvable windows over all 81 windows at `K = 1`; a 7-chain sample stays at zero over 375 windows at `K = 2`. |
| **(ii)** Is there an explicit parametric stratum dead at every tested window? | **Yes, five of them** (§4), covering 32 of the 67 chains, with **zero** windows solvable mod 3 or mod 5 — 6,156 window-decisions, no exception. |
| ...with a **proved mechanism**? | **No.** The natural finer-than-augmentation invariant (the `t`-exponent abelianization `M -> Z[x,x^-1]`) is **inert**: solvable at all 2,106 windows tested, every prime (§5). The strata are exact predicates on tested data, not theorems. |
| Does the verdict factor through a small set of parameter coordinates? | **No.** No subset of `(k1,p1,k2,p2,k3,p3,\|g\|)` of size `<= 4` determines liveness (§3.3). |
| Is one prime binding? | **Yes.** Solvable mod 5 implies solvable mod 2 and mod 3 at **every one of the 5,427 windows**; the chain-level conjunction verdict equals the mod-5 verdict at all four caps (§3.2). |

So the period-two route is not blocked by a "layer 1 is generically live" triviality
— but neither does W2f hand over a proved obstruction. What it hands over is a
sharply localised target: five parameter strata that are dead mod 3 **and** mod 5
everywhere tested, and a ruled-out candidate mechanism.

---

## 1. The index set, made concrete

`period_two_normal_form.py` (W2d c.2/c.3) generates the census exactly at caps
12–17. This checker re-runs its `pinned_step` generator **without** the
first-wins dedupe, so the parametrization multiplicity is measured, and adds two
structural checks that W2d did not make:

| fact | value | status |
|---|---|---|
| chains at caps 12 / 13 / 14 / 15 | 17 / 36 / 55 / 67 | reproduced |
| `chains(12) ⊆ chains(13) ⊆ chains(14) ⊆ chains(15)` | true | **new**, checked |
| cap-12 chain set equals the committed census file | true | **new**, checked (control) |
| every chain has **exactly one** parameter tuple `(k1,p1,k2,p2,k3,p3)` | 67/67 | **new**, checked |

The nesting is what makes the cap columns below exact rather than four separate
searches: one sweep at cap 15 supplies every smaller cap by filtering on
`max(|R|,|S|,|U|)`. The uniqueness matters for the correlation analysis — the
six integers are genuine *coordinates* on the family, not merely a surjection
onto it, so "liveness as a function of the parameters" is a well-posed question.

### 1.1 A latent defect in the W2e window machinery, found and fixed

W2e's gauge slots are built by `shortest_conjugator(base, target, radius=10)`,
a ball search. At cap 12 it always succeeds. **At cap 15 it fails for 15 of the
67 chains** — the coset's shortest element is longer than 10 — and the failure is
silent: `chain_slots` returns `None`, the chain gets zero windows, and a naive
extension of W2e's code would have recorded all 15 as `NOT_LIVE`. They are not
dead; they were never tested.

The fix is to stop searching. In a free product, `base = v rho v^-1` and
`target = v' rho' v'^-1` are conjugate iff `rho' = tau sigma` is a letter-rotation
of `rho = sigma tau`, and then

```text
h = v' * sigma^-1 * v^-1
```

conjugates one to the other — a closed form, no ball. The checker uses the ball
result when it exists (so the window family is **byte-identical to W2e's** for
every chain W2e could see) and the closed form otherwise, re-centred on the
shortest element of the coset `h<zeta>`.

**Control (runs every sweep):** wherever both are available, the closed-form `h`
must lie in `h_ball * <zeta>`. Measured across the full sweep: **agreement on
every slot checked, in every run** (`coset_agree == coset_checked`), with the
fallback used on 15 chains.

---

## 2. Method

Windows are W2e's: for each gauge slot the conjugator set is `h_base * C_Q(base)`
with `C_Q(base) = <zeta>` infinite cyclic, so a window is an integer 4-tuple
`(k0,k1,k2,k3)`, `|k_i| <= K`. Default sweep: `K = K1 = 1`, **81 windows per
chain**, one terminal conjugator `g`, no early exit — every window's verdict is
recorded for each prime separately.

Speed: the one-hop system build is memoized (operator systems depend only on
`(h2,h3,g)`, so the 9 windows sharing one reuse its columns). **Control C2**
recomputes the first four windows of every run with the unmodified reference path
`period_two_liveness_invariance._evaluate_window` and requires record-for-record
agreement — 0 disagreements in every run.

---

## 3. Results

### 3.1 The live fraction as the cap grows

67 chains, 5,427 windows, all decided.

| cap | chains | **live (mod 2,3,5)** | frac | live mod 2 | frac | live mod 3 | frac | live mod 5 | frac |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 12 | 17 | **6** | 0.353 | 12 | 0.706 | 7 | 0.412 | 6 | 0.353 |
| 13 | 36 | **16** | 0.444 | 31 | 0.861 | 17 | 0.472 | 16 | 0.444 |
| 14 | 55 | **19** | 0.345 | 40 | 0.727 | 20 | 0.364 | 19 | 0.345 |
| 15 | 67 | **21** | 0.313 | 42 | 0.627 | 22 | 0.328 | 21 | 0.313 |

**The live fraction is stable-to-falling: 0.35, 0.44, 0.35, 0.31.** It is not
rising toward 1 (which would have made per-baseline towers unable to start dead)
and it is not collapsing toward 0 (which would have suggested the live set is a
cap-12 artifact). Within caps 12–15 the honest reading is a roughly constant
one-third, with the cap-13 bump and the subsequent decline both inside the range
a 17-to-67 sample can produce. **Nonclaim:** four caps do not establish a trend;
extending to caps 16–17 (91 and 106 chains) is the direct test.

The **cap-12 live set is exactly W2b's six chains, chain for chain** — an
independent reproduction on a window family rebuilt from a different conjugator
construction (§1.1) than either W2b or W2e used.

### 3.2 Mod 5 is the binding prime

| | windows |
|---|---:|
| total | 5,427 |
| solvable mod 2 | 539 |
| solvable mod 3 | 259 |
| solvable mod 5 | 253 |
| solvable at all three (**live**) | 253 |

`live == mod 5` in total, and `live <= mod 5` holds chain by chain, so equality
forces it window by window:

> **Every window solvable mod 5 is solvable mod 2 and mod 3.** (5,427 windows,
> no exception.) At chain level the sets nest strictly:
> `live_5 = live_all ⊆ live_3 ⊆ live_2`, with 21 / 22 / 42 members at cap 15.

Practical consequence: the mod-5 solve alone decides one-hop liveness on this
family; mod 2 is far too permissive to be evidence on its own (it passes 42 of 67
chains and 539 windows). Any future note reporting a single-prime liveness number
should report **mod 5**, not mod 2, and should say which.

### 3.3 No small determining set of coordinates

A coordinate subset *determines* liveness if no value of the coordinate tuple
carries both a live and a dead chain. Searched exhaustively over all
`1 + 2 + 3 + 4`-element subsets of `(k1, p1, k2, p2, k3, p3, |g|)`:

> **No subset of size `<= 4` determines liveness.**

(Size 7 determines it trivially, since the parametrization is unique — so any
"determining set" near that size is vacuous re-indexing, and the checker flags
`vacuous: true` on any set whose value count exceeds half the family.)

So the map `t -> live?` is not a function of any four of the seven coordinates.
That is the negative half; §4 is the positive half.

### 3.4 The correlations that do exist

Single-coordinate contingency, cap 15 (`value: (chains, live)`):

```text
k1     0:(17,6)   2:(28,13)  4:(4,2)    6:(5,0)    7:(13,0)
p1     1:(28,13)  2:(17,6)   3:(3,0)    4:(2,0)    6:(17,2)
k2     0:(21,10)  2:(19,4)   3:(5,0)    4:(2,0)    6:(14,7)  7:(6,0)
p2     2:(21,9)   3:(22,5)   4:(1,0)    5:(1,0)    6:(2,0)   7:(4,0)  8:(16,7)
k3     0:(15,7)   1:(8,6)    2:(5,2)    3:(5,2)    4:(4,1)   5:(9,2)  6:(10,1)
       7:(4,0)    8:(3,0)    9:(4,0)
p3     0:(4,4)    1:(15,6)   2:(12,3)   3:(17,8)   4:(6,0)   5:(3,0)  6:(5,0)
       7:(4,0)    8:(1,0)
|g|    0:(32,15)  1:(3,0)    2:(8,0)    3:(13,6)   4:(7,0)   5:(4,0)
```

The **level-1 branch `(k1,p1)`, i.e. the value of `R`, is the strongest single
correlate**:

| `R` | `(k1,p1)` | chains | live |
|---|---|---:|---:|
| `TTctcTctc` | (2,1) | 28 | **13** |
| `TTcTTctcTcttt` | (0,2) | 17 | **6** |
| `TTTcTctcttc` | (4,6) | 4 | **2** |
| `cTcTctcTTcttc` | (7,6) | 13 | **0** |
| `TTTctttcTTTcttc` | (6,3) | 3 | **0** |
| `tcTcTTTcttc` | (6,4) | 2 | **0** |

Three of the six `R`-branches carry every live chain; the other three (18 chains)
carry none. This sharpens W2b's cap-12 observation ("the whole live set is
`k1 = 2, p1 = 1`"): at cap 15 the live set spans three branches, so `R` is not
constant on it — but the branch is still the coordinate that separates best.

The terminal conjugator is the second strongest: **every live chain has
`g ∈ {"", "TTc"}`**; the five other observed `g` values carry 22 chains and no
live one.

---

## 4. Five dead strata, exact on the tested family

Each row is an exact predicate on the parameters. "windows" is the number of
fully-decided one-hop systems inside the stratum at `K = 1`.

| stratum | predicate | chains | windows | live chains | solvable windows mod 2 | **mod 3** | **mod 5** |
|---|---|---:|---:|---:|---:|---:|---:|
| **S1** | `k1 >= 6` (equivalently `R ∈ {cTcTctcTTcttc, TTTctttcTTTcttc, tcTcTTTcttc}`) | 18 | 1,458 | 0 | 122 | **0** | **0** |
| **S2** | `g ∉ {"", "TTc"}` | 22 | 1,782 | 0 | 122 | **0** | **0** |
| **S3** | `p3 >= 4` | 19 | 1,539 | 0 | 38 | **0** | **0** |
| **S4** | `k3 >= 7` | 11 | 891 | 0 | 56 | **0** | **0** |
| **S5** | `k2 >= 7` | 6 | 486 | 0 | 0 | **0** | **0** |

`S1 ⊂ S2` (every `k1 >= 6` chain has `g ∉ {"", "TTc"}`); the others overlap
partially. **Union: 32 of 67 chains, containing no live chain.** The remaining
14 dead chains lie outside all five strata, so the strata do not exhaust
deadness — they are sufficient conditions, not a characterisation.

The mod-3/mod-5 columns are the sharp part. Inside these strata the one-hop
system is **not merely "never solvable at all three primes"** — it is unsolvable
mod 3 and unsolvable mod 5 at every single tested window, 6,156 window-decisions.
Only the permissive mod-2 test ever succeeds there, and never on more than a few
per cent of windows.

Related monotone tails (largest coordinate value carrying a live chain; every
chain strictly above it is dead):

| coordinate | max live value | chains strictly above | all dead above |
|---|---:|---:|---|
| `p3` | 3 | 19 | yes |
| `k1` | 4 | 18 | yes |
| `k3` | 6 | 11 | yes |
| `\|g\|` | 3 | 11 | yes |
| `k2` | 6 | 6 | yes |
| `total_len = \|R\|+\|S\|+\|U\|` | 38 | 7 | yes |
| `min defect terms over the chain's windows` | 23 | 23 | yes |
| `p1`, `p2`, `\|S\|`, `\|U\|`, `maxlen` | — | **0** | vacuous |

Read the last row as a warning: five of the twelve coordinates have *no* chain
above their maximal live value, so "all dead above" is empty there and carries no
information. The checker reports `chains_strictly_above` next to the flag for
exactly this reason.

### 4.1 Robustness of the strata

- **Wider windows.** Seven chains of `S2` (covering `g ∈ {c, TcTTc, cTTTc}`)
  re-run at `K = 2`, `K1 = 1`: **375 windows each, 2,625 windows, 0 solvable at
  any prime** — the same chains were already 0/81 at every prime at `K = 1`.
  Widening the gauge index five-fold on three axes changes nothing.
- **Alternative terminal conjugators.** `g` enters the operators only through
  `w = g t g^-1`, and `C_Q(t) = <t>`, so the whole coset `g<t>` gives one `w`;
  enumerating raw ball elements would return `g, gt, gT` and pretend they were
  three terminal conjugators. Deduping by `w`: **5 of those 7 chains have a
  unique `w` in `ball(6)`**, and the 2 with a second `w` stay 0/162. So inside
  the `GPAD = 5` ceiling the terminal conjugator is essentially rigid, which
  narrows W2d (d.5)'s worry — though it does not remove it, since the ceiling is
  saturated.

---

## 5. Mechanism attempt: the abelianization is inert

The obvious candidate for the "strictly finer invariant" W2d (d.3) demands is
the `t`-exponent map. `c` has `t`-exponent 0, so

```text
phi : M = Z[Q/<c>]  ->  Z[x, x^-1],      q<c>  |->  x^(t-exponent of q)
```

is well defined, and is a map of left `Z[Q]`-modules for the action of `Q`
through `Q -> Z`, `t |-> x`, `c |-> 1`. A solution `(c_v)` of the one-hop system
pushes forward to `xi_n = sum_{e(v)=n} c_v`, so

> solvable(full) **=>** solvable(collapsed),

i.e. failure of the collapsed system is a genuine obstruction — and augmentation
(W2b's only current bar) is exactly its specialisation at `x = 1`. Under `phi`
the closed forms of W2e §4.1 become Laurent polynomials, all divisible by
`(x - 1)`:

```text
L2 |-> 1 - x^(e(R)-e(U))        L3 |-> x^(-e(U)) - x        L4 |-> x - 1
L1 |-> (x^e(h2) + x^(e(h3)-e(U))) * (x^e(B) - x^e(S))
L0 |-> -(x^(-e(U)) + bridge_x * x^e(S)) * (x^e(A) - x^e(R))
```

**Measured:** on 26 chains (the whole `S2` stratum plus four controls), 2,106
windows, the collapsed system is **solvable mod 2, mod 3 and mod 5 at every
window**, with 0 violations of the predicted implication (a violation — full
solvable but collapsed unsolvable — would have been a code bug, and the checker
counts them).

> **The `t`-exponent abelianization of the one-hop system separates nothing on
> this family.** It is not merely too coarse at `x = 1` (that was already known):
> the entire Laurent-polynomial image is solvable everywhere tested.

So the strata of §4 have **no proved mechanism**, and the most natural candidate
is now ruled out at this scope. A working invariant has to be non-abelian — a
finite or infinite non-commutative quotient of `Q` acting on the coset module,
in the spirit of the elliptic obstruction's `PSU(2)` — or has to use the `p`
asymmetry that §3.2 exposes (mod 5 binding, mod 2 permissive), which no
`Z`-linear module invariant explains.

---

## 6. Controls

Every control runs on every run and each was demonstrated able to fail.

| control | guards | how it can fail | result |
|---|---|---|---|
| C1 fixed-h witness `(21, 48, 0)` | the imported lifting calculus is the codex one | forced defect mismatch ⇒ exit 2 | passes every run |
| C2 fast-path equals reference | the memoized system build is the unmodified W2e path | any record difference on the sampled windows ⇒ exit 2 | 0 disagreements, every run |
| C3 mutation flips a verdict | the pipeline can output DEAD at all | **verified by mutation**: at a live witness window, deleting one term of `L0` flips `(T,T,T) -> (F,F,F)`, and flipping one sign in `L3` flips `(T,T,T) -> (T,F,F)`. Both mutations live only inside the control function; the production path never sees them. | both flip, every run |
| C4 dynamic range | both outcomes are producible in the run | no unsolvable window, or no live verdict anywhere including C3's clean reference ⇒ exit 2 | passes |
| C5 closed-form conjugator vs ball | §1.1's fallback is the same gauge coset W2e used | any slot where the closed form leaves `h_ball * <zeta>` ⇒ exit 2 | agreement on every checked slot |
| chain-table control | cap nesting + cap-12 equals the committed census | either false ⇒ exit 2 | passes |
| witness liveness (report mode) | the sweep still finds the known-live witness | witness not live ⇒ exit 2 | passes |

An earlier iteration of C4 required a live window *in the swept slice*, which a
deliberately dead-stratum slice can never provide; it is now satisfied either by
a live window in the slice or by C3's clean (uncorrupted) reference window, which
is a real live verdict from the same code path.

Reproduce (each command is its own guarded run; the sweep is resumable — re-run
until `"remaining": 0`):

```bash
python3 scripts/run_proof_guarded.py --timeout-seconds 55 -- python3 \
  fable/proofs/checkers/period_two_parametric_solvability.py --mode chains \
  --json fable/proofs/checkers/out/w2f_chains.json

# main sweep: 67 chains x 81 windows, ~10 runs
python3 scripts/run_proof_guarded.py --timeout-seconds 55 -- python3 \
  fable/proofs/checkers/period_two_parametric_solvability.py --mode sweep --k 1 \
  --state fable/proofs/checkers/out/w2f_sweep_k1.json --budget-seconds 45

python3 scripts/run_proof_guarded.py --timeout-seconds 55 -- python3 \
  fable/proofs/checkers/period_two_parametric_solvability.py --mode report \
  --state fable/proofs/checkers/out/w2f_sweep_k1.json \
  --json fable/proofs/checkers/out/w2f_report_k1.json

# K = 2 deep probe of the g-stratum (one chain per run)
python3 scripts/run_proof_guarded.py --timeout-seconds 55 -- python3 \
  fable/proofs/checkers/period_two_parametric_solvability.py --mode sweep \
  --k 2 --k1 1 --only-g c,TcTTc,cTTTc \
  --state fable/proofs/checkers/out/w2f_deep_k2.json --budget-seconds 10

# alternative terminal conjugators (deduped by w = g t g^-1)
python3 scripts/run_proof_guarded.py --timeout-seconds 55 -- python3 \
  fable/proofs/checkers/period_two_parametric_solvability.py --mode sweep \
  --k 1 --g-alts 3 --only-g c,TcTTc,cTTTc \
  --state fable/proofs/checkers/out/w2f_galts_k1.json --budget-seconds 25

# abelianization probe
python3 scripts/run_proof_guarded.py --timeout-seconds 55 -- python3 \
  fable/proofs/checkers/period_two_parametric_solvability.py --mode sweep \
  --k 1 --abelian --only-g c,Tc,cTTc,TcTTc,cTTTc \
  --state fable/proofs/checkers/out/w2f_abelian_k1.json --budget-seconds 42
```

Exit 0 = run completed with every control green (a dead stratum is a *result*).
Exit 2 = control failure, run void.

---

## 7. Scope and nonclaims

- **`NOT_LIVE_AT_TESTED_WINDOWS` stays inconclusive at chain level.** W2b's
  doctrine is inherited unchanged. `K`, `GPAD = 5`, the cap and the `g`-radius are
  **ceilings**: every one of them can only under-report liveness. A stratum being
  "dead at all tested windows" is therefore evidence about the tested window
  family, never a proof that the stratum is dead.
- **The strata are predicates found by exhaustive search over the tested data.**
  They are exact and checkable on that data; they are not theorems, and §5 shows
  the candidate mechanism does not support them.
- **Four caps are not a trend.** The live-fraction column (0.35, 0.44, 0.35, 0.31)
  is reported as stable-to-falling; caps 16–17 are the direct test and were not
  run here.
- **One terminal conjugator per chain in the main sweep.** The `--g-alts` probe
  covers 7 chains only, and even there `ball(6)` is a ceiling.
- **The `K = 2` evidence is a 7-chain sample**, not the whole stratum.
- No claim about the free-group depth-four class, the bridge, AK(3), stable AC,
  or AC. Nothing here is a statement about lifting or trivialisation.

---

## 8. The single most decisive next question

> **Does a non-abelian quotient of `Q` kill `S2` (`g ∉ {"", "TTc"}`, 22 chains)?**

Everything points there. `S2` is the largest stratum, it contains `S1`, it is
dead mod 3 and mod 5 at every one of 1,782 windows and survives the `K = 2`
widening; its defining coordinate `g` enters the operators only through
`w = g t g^-1`, i.e. only through `L3 = U^-1 - w` and `L4 = w - 1` — the two
operators W2e proves are **untouched** by a change of `S` representative. So `S2`
is the one stratum whose defining parameter acts on a part of the system that the
known transformation law leaves fixed, and it is exactly the part an
elliptic-style representation argument attacks (`rho(w)` central would collapse
`L3, L4`). §5 rules out doing it abelian; the concrete next experiment is to
push `M = Z[Q/<c>]` through `Q -> G` for small non-abelian `G` with `c` of order 2
and test whether the defect leaves the operator image there.

---

## Summary of status

| claim | status |
|---|---|
| census caps 12–15 are nested; cap-12 set equals the committed census | **verified** (control) |
| every census chain has a unique six-parameter tuple | **verified**, 67/67 |
| W2e's `ball(10)` slot search silently fails on 15 of 67 chains at cap 15; closed-form conjugator fixes it and agrees with the ball on every slot where both exist | **verified** (control) |
| live fractions 6/17, 16/36, 19/55, 21/67 (mod 2,3,5) | **checker-verified**, 5,427 decided windows |
| W2b's six live cap-12 chains reproduced on the rebuilt window family | **verified**, chain for chain |
| every window solvable mod 5 is solvable mod 2 and mod 3; `live = live_5 ⊆ live_3 ⊆ live_2` | **verified**, all 5,427 windows |
| no subset of `(k1,p1,k2,p2,k3,p3,\|g\|)` of size `<= 4` determines liveness | **verified** (exhaustive) |
| five strata (32 chains) with zero windows solvable mod 3 or mod 5 | **verified** at `K = 1`; 7-chain sample also at `K = 2` |
| the `t`-exponent abelianization separates nothing (2,106 windows, all solvable) | **verified**; candidate mechanism **ruled out** at this scope |
| any stratum is dead at **all** windows (not just tested ones) | **not established** |
| layer-1 liveness is generic | **false** at the tested windows (46 of 67 chains have none) |
| anything about lifting, the bridge, AK(3), stable AC, or AC | **no claim** |
